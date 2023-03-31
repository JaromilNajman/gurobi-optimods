import math
import time
import logging
import numpy as np
import gurobipy as gp
from gurobipy import GRB

from .myutils import break_exit
from .grbfile import grbreadvoltsfile
from .grbgraphical import grbgraphical
from .grbformulator_ac import computebalbounds


def lpformulator_dc(alldata):
    """Formulate DCOPF model and solve it"""

    logging.info("\nDC formulation.")

    starttime = time.time()

    sol_count = 0
    solution = None
    objval = None
    # Create model
    with gp.Env() as env, gp.Model("dc_formulation_model", env=env) as model:
        # Add model variables and constraints
        lpformulator_dc_body(alldata, model)

        if alldata["strictcheckvoltagesolution"]:
            # check input solution against formulation
            spitoutvector = True
            # TODO-Dan Why do you need the feascode? It's not used anywhere and the function does not even return anything
            feascode = lpformulator_dc_strictchecker(
                alldata, model, spitoutvector
            )  # uncomment this for check

        sol_count = lpformulator_dc_opt(alldata, model)

        endtime = time.time()
        logging.info(
            "Overall time taken (model construction + optimization): %f s."
            % (endtime - starttime)
        )
        logging.info("Solution count: %d." % (sol_count))

        if sol_count > 0:
            lpformulator_dc_examine_solution(alldata, model)
            objval = model.ObjVal
            solution = {}
            for v in model.getVars():
                if math.fabs(v.x) > 1e-09:
                    logging.info(v.varname + " = " + str(v.x))
                    solution[v.VarName] = v.X
                else:
                    solution[v.VarName] = 0

    return solution, objval
    """
    buses        = alldata['buses']
    branches     = alldata['branches']
    gens         = alldata['gens']
    IDtoCountmap = alldata['IDtoCountmap']
    """


def lpformulator_dc_body(alldata, model):
    """Helper function for adding variables and constraints to the model"""

    # Create model variables
    lpformulator_dc_create_vars(alldata, model)
    # Create model constraints
    lpformulator_dc_create_constraints(alldata, model)

    model.update()  # Update to get correct model stats
    logging.info(
        "Constructed DCOPF model with %d variables and %d constraints.\n"
        % (model.NumVars, model.NumConstrs)
    )

    if alldata["lpfilename"] != None:
        model.write(
            alldata["lpfilename"]
        )  # FIXME remove.  Jarek: I am using this for debugging, for now
        logging.info("Wrote LP to " + alldata["lpfilename"])

    alldata["model"] = model


def lpformulator_dc_create_vars(alldata, model):
    """Create model variables for DCOPF"""

    logging.info("Creating variables.")

    fixtolerance = 1e-05
    if alldata["fixtolerance"] > 0:
        fixtolerance = alldata["fixtolerance"]

    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    IDtoCountmap = alldata["IDtoCountmap"]
    gens = alldata["gens"]

    varcount = 0
    thetavar = {}
    Pinjvar = {}
    Pvar_f = {}  # DC, so f-flow = t-flow
    twinPvar_f = {}  # auxiliary variable in case branch-switching is being used
    GenPvar = {}

    for j in range(1, numbuses + 1):
        bus = buses[j]
        ubound = 2 * math.pi
        lbound = -ubound

        if bus.inputvoltage:
            candidatelbound = bus.inputA_rad - fixtolerance
            candidateubound = bus.inputA_rad + fixtolerance
            lbound = max(lbound, candidatelbound)
            ubound = min(ubound, candidateubound)

        thetavar[bus] = model.addVar(
            obj=0.0, lb=lbound, ub=ubound, name="theta_" + str(bus.nodeID)
        )
        bus.thetavarind = varcount
        varcount += 1

        Plbound = Qlbound = -GRB.INFINITY
        Pubound = Qubound = GRB.INFINITY
        Pubound, Plbound, Qubound, Qlbound = computebalbounds(alldata, bus)

        Pinjvar[bus] = model.addVar(
            obj=0.0, lb=Plbound, ub=Pubound, name="IP_%d" % bus.nodeID
        )
        bus.Pinjvarind = varcount
        # comment: Pinjvar is the variable modeling total active power injected by bus j into the branches incident with j
        varcount += 1

        # Next, generator variables
        for genid in bus.genidsbycount:
            gen = gens[genid]
            lower = gen.Pmin * gen.status
            upper = gen.Pmax * gen.status
            # if bus.nodetype == 3:
            #  upper = GRB.INFINITY
            #  lower = -GRB.INFINITY  #ignoring slack bus
            GenPvar[gen] = model.addVar(
                obj=0.0, lb=lower, ub=upper, name="GP_%d_%d" % (gen.count, gen.nodeID)
            )
            gen.Pvarind = varcount
            varcount += 1

    alldata["LP"]["thetavar"] = thetavar
    alldata["LP"]["Pinjvar"] = Pinjvar
    alldata["LP"]["GenPvar"] = GenPvar

    # Branch related variables
    branches = alldata["branches"]
    numbranches = alldata["numbranches"]

    for j in range(1, 1 + numbranches):
        branch = branches[j]
        f = branch.f
        t = branch.t
        count_of_f = IDtoCountmap[f]
        count_of_t = IDtoCountmap[t]
        busf = buses[count_of_f]
        bust = buses[count_of_t]
        if branch.constrainedflow:
            ubound = branch.limit
        else:
            ubound = alldata["sumPd"]  # DC
        lbound = -ubound

        Pvar_f[branch] = model.addVar(
            obj=0.0,
            lb=lbound,
            ub=ubound,
            name="P_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
        )
        branch.Pftvarind = varcount
        varcount += 1

        if alldata["branchswitching_mip"]:
            twinPvar_f[branch] = model.addVar(
                obj=0.0,
                lb=lbound,
                ub=ubound,
                name="twinP_%d_%d_%d" % (j, busf.nodeID, bust.nodeID),
            )
            branch.twinPftvarind = varcount
            varcount += 1

    alldata["LP"]["Pvar_f"] = Pvar_f
    alldata["LP"]["twinPvar_f"] = twinPvar_f

    zvar = {}
    if alldata["branchswitching_mip"]:
        logging.info("Adding branch switching variables.")
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            lbound = 0
            ubound = 1
            zvar[branch] = model.addVar(
                lb=lbound,
                ub=ubound,
                obj=0.0,
                vtype=GRB.INTEGER,
                name="z_%d_%d_%d" % (j, f, t),
            )
            branch.switchvarind = varcount
            varcount += 1
    alldata["LP"]["zvar"] = zvar

    lincostvar = model.addVar(
        obj=1.0, lb=-GRB.INFINITY, ub=GRB.INFINITY, name="lincost"
    )
    alldata["LP"]["lincostvar"] = lincostvar
    alldata["LP"]["lincostvarind"] = varcount
    varcount += 1

    if alldata["usequadcostvar"]:
        quadcostvar = model.addVar(obj=1.0, lb=0, ub=GRB.INFINITY, name="quadcost")
        alldata["LP"]["quadcostvar"] = quadcostvar
        alldata["LP"]["quadcostvarind"] = varcount
        varcount += 1

    constobjval = 0
    for gen in gens.values():
        if gen.status > 0:
            constobjval += gen.costvector[gen.costdegree]

    constvar = model.addVar(obj=constobjval, lb=1.0, ub=1.0, name="constant")
    alldata["LP"]["constvar"] = constvar
    varcount += 1


def lpformulator_dc_create_constraints(alldata, model):
    """ "Create constraint for DCOPF"""

    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    numbranches = alldata["numbranches"]
    branches = alldata["branches"]
    gens = alldata["gens"]
    IDtoCountmap = alldata["IDtoCountmap"]

    thetavar = alldata["LP"]["thetavar"]
    Pvar_f = alldata["LP"]["Pvar_f"]
    twinPvar_f = alldata["LP"]["twinPvar_f"]
    zvar = alldata["LP"]["zvar"]
    Pinjvar = alldata["LP"]["Pinjvar"]
    GenPvar = alldata["LP"]["GenPvar"]
    lincostvar = alldata["LP"]["lincostvar"]

    logging.info("Creating constraints.")
    logging.info("  Adding cost definition.")

    coeff = [gen.costvector[gen.costdegree - 1] for gen in gens.values()]
    variables = [GenPvar[gen] for gen in gens.values()]
    expr = gp.LinExpr(coeff, variables)
    model.addConstr(expr == lincostvar, name="lincostdef")

    numquadgens = 0
    for gen in gens.values():
        if gen.costdegree >= 2 and gen.costvector[0] > 0 and gen.status:
            numquadgens += 1

    logging.info(
        "    Number of generators with quadratic cost coefficient: %d." % numquadgens
    )

    if numquadgens > 0:
        if alldata["usequadcostvar"]:
            quadcostvar = alldata["LP"]["quadcostvar"]
            logging.info("    Adding quadcost definition constraint.")
            qcost = gp.QuadExpr()
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    qcost.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.addConstr(qcost <= quadcostvar, name="qcostdef")
        else:
            logging.info("    Adding quad cost to objective.")
            model.update()  # Necessary to flush changes in the objective function
            oldobj = model.getObjective()
            newobj = gp.QuadExpr(oldobj)
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    newobj.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.setObjective(newobj, GRB.MINIMIZE)

    # Active PF defs
    logging.info("  Adding active power flow definitions.")
    count = 0
    for j in range(1, 1 + numbranches):
        branch = branches[j]
        f = branch.f
        t = branch.t
        count_of_f = IDtoCountmap[f]
        count_of_t = IDtoCountmap[t]
        busf = buses[count_of_f]
        bust = buses[count_of_t]
        branch.Pfcname = "Pdef_%d_%d_%d" % (j, f, t)
        if branch.status:
            # Pf = (thetaf - thetat)/(x*ratio)
            coeff = 1 / (branch.x * branch.ratio)
            exp = Pvar_f[branch]
            if alldata["branchswitching_mip"]:
                exp += twinPvar_f[branch]
            # angle_exp = coeff*thetavar[busf] - coeff*thetavar[bust] - coeff*branch.angle_rad
            branch.Pdeffconstr = model.addConstr(
                exp
                == coeff * thetavar[busf]
                - coeff * thetavar[bust]
                - coeff * branch.angle_rad,
                name=branch.Pfcname,
            )
            count += 1

            if alldata["branchswitching_mip"]:
                if branch.constrainedflow:
                    coeff = branch.limit
                else:
                    coeff = alldata["sumPd"]  # DC

                model.addConstr(
                    Pvar_f[branch] <= coeff * zvar[branch],
                    name="upmip_%d_%d_%d" % (j, f, t),
                )
                model.addConstr(
                    Pvar_f[branch] >= -coeff * zvar[branch],
                    name="dnmip_%d_%d_%d" % (j, f, t),
                )
                model.addConstr(
                    twinPvar_f[branch] <= coeff * (1 - zvar[branch]),
                    name="upmip_twin_%d_%d_%d" % (j, f, t),
                )
                model.addConstr(
                    twinPvar_f[branch] >= -coeff * (1 - zvar[branch]),
                    name="dnmip_twin_%d_%d_%d" % (j, f, t),
                )
        else:
            branch.Pdeffconstr = model.addConstr(
                Pvar_f[branch] == 0, name=branch.Pfcname
            )

    logging.info("    %d active power flow definitions added." % count)

    # Balance constraints
    logging.info(
        "  Adding constraints stating bus injection = total outgoing power flow."
    )
    count = 0
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        expr = gp.LinExpr()
        for branchid in bus.frombranchids.values():
            expr.add(Pvar_f[branches[branchid]])

        for branchid in bus.tobranchids.values():
            expr.add(-Pvar_f[branches[branchid]])

        model.addConstr(expr == Pinjvar[bus], name="PBaldef%d_%d" % (j, bus.nodeID))

        count += 1
    logging.info("    %d constraints added." % count)

    # Injection defs
    logging.info("  Adding injection definition constraints.")
    count = 0
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        expr = gp.LinExpr()

        if len(bus.genidsbycount) > 0:
            for genid in bus.genidsbycount:
                gen = gens[genid]
                expr.add(GenPvar[gen])

        model.addConstr(Pinjvar[bus] == expr - bus.Pd, name="Bus_PInj_%d" % j)
        count += 1

    logging.info("    %d injection definition constraints added." % count)

    if alldata["branchswitching_mip"]:
        boundzs = True
        if boundzs:
            exp = gp.LinExpr()
            delta = numbranches
            N = numbranches - delta  # <<<<<<---- here is the heuristic lower bound
            for j in range(1, 1 + numbranches):
                branch = branches[j]
                exp += zvar[branch]
            model.addConstr(exp >= N, name="sumzbd")


def lpformulator_dc_opt(alldata, model):
    """Optimizes constructed DCOPF model"""

    numbranches = alldata["numbranches"]
    branches = alldata["branches"]

    logging.disable(logging.INFO)
    model.params.LogFile = alldata["logfile"]

    # Specific settings for better convergence
    model.Params.MIPGap = 1.0e-4
    model.Params.OptimalityTol = 1.0e-4
    model.Params.FeasibilityTol = 1.0e-6

    feastol = model.Params.FeasibilityTol
    opttol = model.Params.OptimalityTol
    mipgap = model.Params.MIPGap

    model.Params.SolutionLimit = 20  # TODO-Dan Why do we need a solution limit for DC?

    if alldata["branchswitching_mip"]:
        logging.critical("Using mip start with all branches kept on.")
        # mip start
        zvar = alldata["LP"]["zvar"]
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            zvar[branch].Start = 1.0

        zholder = np.zeros(numbranches)
        alldata["MIP"]["zholder"] = zholder
        alldata["MIP"]["solutionfound"] = False
        alldata["MIP"]["bestsolval"] = 1e50
        alldata["MIP"]["solcount"] = 0
        gholder = np.zeros(alldata["numgens"])
        alldata["MIP"]["gholder"] = gholder

        # Optimize
        model._vars = model.getVars()
        model._data = alldata
        model.optimize(
            plot_new_solution_callback
        )  # TODO-Dan We only use graphviz for DCOPF. Why is that? The dographics setting does nothing for AC or IV.
    else:
        model.optimize()

    logging.disable(logging.NOTSET)

    # Check model status and re-optimize or try computing an IIS if necessary
    if model.status == GRB.INF_OR_UNBD:
        logging.info("\nModel Status: infeasible or unbounded.")
        logging.info("Re-optimizing with DualReductions turned off.\n")
        logging.disable(logging.INFO)
        model.Params.DualReductions = 0
        model.optimize()
        logging.disable(logging.NOTSET)

    if model.status == GRB.INFEASIBLE:
        logging.info("\nModel Status: infeasible.")
        logging.info("Computing IIS...\n")
        logging.disable(logging.INFO)
        model.computeIIS()
        logging.disable(logging.NOTSET)
        logging.info("\nIIS computed, writing IIS to file dcopfmodel.ilp.\n")
        model.write("acopfmodel.ilp")

    elif model.status == GRB.UNBOUNDED:
        logging.info("\nModel Status: unbounded.\n")

    elif model.status == GRB.INTERRUPTED:
        logging.info("\nModel Status: interrupted.\n")

    elif model.status == GRB.OPTIMAL:
        logging.info("\nModel Status: optimal.\n")

    # Only print objective value and solution quality if at least
    # one feasible point is available
    if model.SolCount > 0:
        logging.info("Objective value = %g." % model.objVal)
        logging.disable(logging.INFO)
        model.printQuality()
        logging.disable(logging.NOTSET)

    return model.SolCount


def lpformulator_dc_examine_solution(alldata, model):
    """TODO-Dan Add description"""

    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    branches = alldata["branches"]
    numbranches = alldata["numbranches"]
    branches = alldata["branches"]
    gens = alldata["gens"]
    IDtoCountmap = alldata["IDtoCountmap"]
    if alldata["branchswitching_mip"]:
        zholder = alldata["MIP"]["zholder"]
        gholder = alldata["MIP"]["gholder"]

    thetavar = alldata["LP"]["thetavar"]
    Pvar_f = alldata["LP"]["Pvar_f"]
    twinPvar_f = alldata["LP"]["twinPvar_f"]
    zvar = alldata["LP"]["zvar"]
    Pinjvar = alldata["LP"]["Pinjvar"]
    GenPvar = alldata["LP"]["GenPvar"]
    lincostvar = alldata["LP"]["lincostvar"]

    loud = False
    numzeros = 0

    """
    for j1 in range(1, 1 + alldata['numgens']):
        gen = alldata['gens'][j1]
        print('gen',gen.count)
        break_exit('printed')  #functionality to be added
    """

    for j in range(1, 1 + numbranches):
        branch = branches[j]
        f = branch.f
        t = branch.t
        count_of_f = IDtoCountmap[f]
        count_of_t = IDtoCountmap[t]
        busf = buses[count_of_f]
        bust = buses[count_of_t]

        if alldata["branchswitching_mip"]:
            zholder[j - 1] = zvar[branch].x
            if zvar[branch].x < 0.5:  # turned off
                numzeros += 1
                if loud:
                    logging.info("branch %d (%d, %d) switched off." % (j, f, t))

    logging.info("Done examining solution.\n")
    """
    if alldata['dographics']:
        grbgraphical(alldata, 'branchswitching')
    """


def plot_new_solution_callback(model, where):
    """Callback to plot new feasible solutions as they are found"""
    if where == GRB.Callback.MIPSOL:
        x = model.cbGetSolution(model._vars)
        objval = model.cbGet(GRB.Callback.MIPSOL_OBJ)
        logging.info("Found new solution of value %.3e." % objval)

        numbuses = model._data["numbuses"]
        buses = model._data["buses"]
        numbranches = model._data["numbranches"]
        branches = model._data["branches"]
        gens = model._data["gens"]
        IDtoCountmap = model._data["IDtoCountmap"]

        thetavar = model._data["LP"]["thetavar"]
        Pvar_f = model._data["LP"]["Pvar_f"]
        twinPvar_f = model._data["LP"]["twinPvar_f"]

        zholder = model._data["MIP"]["zholder"]
        gholder = model._data["MIP"]["gholder"]

        numzeros = 0
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            zholder[j - 1] = x[branch.switchvarind]
            if x[branch.switchvarind] < 0.5:
                numzeros += 1

        for j1 in range(1, 1 + model._data["numgens"]):
            gen = model._data["gens"][j1]
            gholder[j1 - 1] = (
                model._data["baseMVA"] * x[gen.Pvarind]
            )  # print('gen',gen.count,x[gen.Pvarind])
            # break_exit('printed')  #functionality to be added # TODO-Dan What functionality is that?

        model._data["MIP"]["solutionfound"] = True
        difftol = 1e-6
        if model._data["dographics"]:
            if objval < model._data["MIP"]["bestsolval"] - difftol:
                model._data["MIP"]["solcount"] += 1
                textlist = []
                textlist.append("SOLUTION " + str(model._data["MIP"]["solcount"]))
                textlist.append("OBJ: %10.2f" % (objval))
                textlist.append("Lines off: %d" % (numzeros))
                grbgraphical(model._data, "branchswitching", textlist)
            else:
                logging.info(
                    "Skipping graphical display due to insufficient improvement."
                )

        model._data["MIP"]["bestsolval"] = objval