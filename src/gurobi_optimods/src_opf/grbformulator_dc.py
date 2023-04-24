import math
import time
import logging
import numpy as np
import gurobipy as gp
from gurobipy import GRB

from .utils import break_exit
from .grbfile import grbreadvoltsfile
from .grbformulator_ac import computebalbounds


def lpformulator_dc_body(alldata, model):
    """
    Adds variables and constraints for DC formulation to a given Gurobi model

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    # Create model variables
    lpformulator_dc_create_vars(alldata, model)
    # Create model constraints
    lpformulator_dc_create_constraints(alldata, model)

    alldata["model"] = model


def lpformulator_dc_create_vars(alldata, model):
    """
    Creates and adds variables for DC formulation to a given Gurobi model

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    logger.info("Creating variables.")

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
    Pvar_f = {}  # DC, so f-flow = - t-flow
    twinPvar_f = {}  # auxiliary variable in case branch-switching is being used
    GenPvar = {}  # DC, generator real power injections variables

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

    alldata["LP"][
        "thetavar"
    ] = thetavar  # for DC this is the voltage angle - voltage magnitude is always 1 for DC
    alldata["LP"]["Pinjvar"] = Pinjvar
    alldata["LP"]["GenPvar"] = GenPvar  # DC, generator real power injections variables

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

    alldata["LP"][
        "Pvar_f"
    ] = Pvar_f  # DC branch real power injected into "from" end of branch
    # DC branch real power injected into "to" end of branch is the same as Pvar_f
    alldata["LP"]["twinPvar_f"] = twinPvar_f

    zvar = {}
    if alldata["branchswitching_mip"]:
        logger.info("Adding branch switching variables.")
        for j in range(1, 1 + numbranches):
            branch = branches[j]
            f = branch.f
            t = branch.t
            zvar[branch] = model.addVar(
                obj=0.0,
                vtype=GRB.BINARY,
                name="z_%d_%d_%d" % (j, f, t),
            )
            branch.switchvarind = varcount
            varcount += 1
    alldata["MIP"]["zvar"] = zvar

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
    """
    Creates and adds constraints for DC formulation to a given Gurobi model

    Parameters
    ----------
    alldata : dictionary
        Main dictionary holding all necessary data
    model : gurobipy.Model
        Gurobi model to be constructed
    """

    logger = logging.getLogger("OpfLogger")
    numbuses = alldata["numbuses"]
    buses = alldata["buses"]
    numbranches = alldata["numbranches"]
    branches = alldata["branches"]
    gens = alldata["gens"]
    IDtoCountmap = alldata["IDtoCountmap"]

    thetavar = alldata["LP"]["thetavar"]
    Pvar_f = alldata["LP"]["Pvar_f"]
    twinPvar_f = alldata["LP"]["twinPvar_f"]
    zvar = alldata["MIP"]["zvar"]
    Pinjvar = alldata["LP"]["Pinjvar"]
    GenPvar = alldata["LP"]["GenPvar"]
    lincostvar = alldata["LP"]["lincostvar"]

    logger.info("Creating constraints.")
    logger.info("  Adding cost definition.")

    coeff = [gen.costvector[gen.costdegree - 1] for gen in gens.values()]
    variables = [GenPvar[gen] for gen in gens.values()]
    expr = gp.LinExpr(coeff, variables)
    model.addConstr(expr == lincostvar, name="lincostdef")

    numquadgens = 0
    for gen in gens.values():
        if gen.costdegree >= 2 and gen.costvector[0] > 0 and gen.status:
            numquadgens += 1

    logger.info(
        "    Number of generators with quadratic cost coefficient: %d." % numquadgens
    )

    if numquadgens > 0:
        if alldata["usequadcostvar"]:
            quadcostvar = alldata["LP"]["quadcostvar"]
            logger.info("    Adding quadcost definition constraint.")
            qcost = gp.QuadExpr()
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    qcost.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.addConstr(qcost <= quadcostvar, name="qcostdef")
        else:
            logger.info("    Adding quad cost to objective.")
            model.update()  # Necessary to flush changes in the objective function
            oldobj = model.getObjective()
            newobj = gp.QuadExpr(oldobj)
            for gen in gens.values():
                if gen.costdegree == 2 and gen.costvector[0] != 0:
                    newobj.add(gen.costvector[0] * GenPvar[gen] * GenPvar[gen])

            model.setObjective(newobj, GRB.MINIMIZE)

    # Active PF defs
    logger.info("  Adding active power flow definitions.")
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

    logger.info("    %d active power flow definitions added." % count)

    # Balance constraints
    logger.info(
        "  Adding constraints stating bus injection = total outgoing power flow."
    )
    count = 0
    balancecons = {}
    for j in range(1, 1 + numbuses):
        bus = buses[j]
        expr = gp.LinExpr()
        for branchid in bus.frombranchids.values():
            expr.add(Pvar_f[branches[branchid]])

        for branchid in bus.tobranchids.values():
            expr.add(-Pvar_f[branches[branchid]])
        # Create dictionary accessed by bus holding these constraints to access their duals afterwards
        balancecons[bus] = model.addConstr(
            expr == Pinjvar[bus], name="PBaldef%d_%d" % (j, bus.nodeID)
        )

        count += 1
    alldata["LP"]["balancecons"] = balancecons
    logger.info("    %d constraints added." % count)

    # Injection defs
    logger.info("  Adding injection definition constraints.")
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

    logger.info("    %d injection definition constraints added." % count)

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