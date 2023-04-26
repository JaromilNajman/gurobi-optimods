"""
Module for loading datasets for use in optimods examples, in the same vein
as sklearn.datasets.
"""

import pathlib

import pandas as pd

DATA_FILE_DIR = pathlib.Path(__file__).parent / "data"


class AttrDict(dict):
    """Even simpler version of sklearn's Bunch"""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)


def load_workforce():
    return AttrDict(
        availability=pd.read_csv(
            DATA_FILE_DIR / "workforce/availability.csv", parse_dates=["Shift"]
        ),
        pay_rates=pd.read_csv(DATA_FILE_DIR / "workforce/pay_rates.csv"),
        shift_requirements=pd.read_csv(
            DATA_FILE_DIR / "workforce/shift_requirements.csv", parse_dates=["Shift"]
        ),
    )


def load_diet():
    return AttrDict(
        categories=pd.read_csv(DATA_FILE_DIR / "diet-categories.csv"),
        foods=pd.read_csv(DATA_FILE_DIR / "diet-foods.csv"),
        nutrition_values=pd.read_csv(DATA_FILE_DIR / "diet-values.csv"),
    )


def load_opfsettings():
    conf = str(DATA_FILE_DIR) + "/opf/opfsettings.txt"
    return conf


def load_caseopf(number):
    case = str(DATA_FILE_DIR) + "/opf/case" + number + ".m"
    return case


def load_coordsfilepath(filename):
    file = str(DATA_FILE_DIR) + "/opf/" + filename
    return file


def load_caseopfmat(number):
    case = str(DATA_FILE_DIR) + "/opf/case" + number + ".mat"
    return case


def load_caseNYopf():  # real world data case
    case = str(DATA_FILE_DIR) + "/opf/caseNY.m"
    casemat = str(DATA_FILE_DIR) + "/opf/caseNY.mat"
    return case, casemat


def load_opfgraphicssettings():
    conf = str(DATA_FILE_DIR) + "/opf/graphicssettings.txt"
    return conf


def load_opfdictcase():
    casefile_dict = {
        "baseMVA": 100.0,
        "bus": {
            1: {
                "bus_i": 1,
                "type": 3,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            2: {
                "bus_i": 2,
                "type": 2,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            3: {
                "bus_i": 3,
                "type": 2,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            4: {
                "bus_i": 4,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            5: {
                "bus_i": 5,
                "type": 1,
                "Pd": 90.0,
                "Qd": 30.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            6: {
                "bus_i": 6,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            7: {
                "bus_i": 7,
                "type": 1,
                "Pd": 100.0,
                "Qd": 35.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            8: {
                "bus_i": 8,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            9: {
                "bus_i": 9,
                "type": 1,
                "Pd": 125.0,
                "Qd": 50.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0,
                "Va": 1.0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
        },
        "gen": {
            1: {
                "bus": 1,
                "Pg": 0.0,
                "Qg": 0.0,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 250.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
            2: {
                "bus": 2,
                "Pg": 163.0,
                "Qg": 0.0,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 300.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
            3: {
                "bus": 3,
                "Pg": 85.0,
                "Qg": 0.0,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 270.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
        },
        "branch": {
            1: {
                "fbus": 1,
                "tbus": 4,
                "r": 0.0,
                "x": 0.0576,
                "b": 0.0,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            2: {
                "fbus": 4,
                "tbus": 5,
                "r": 0.017,
                "x": 0.092,
                "b": 0.158,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            3: {
                "fbus": 5,
                "tbus": 6,
                "r": 0.039,
                "x": 0.17,
                "b": 0.358,
                "rateA": 150.0,
                "rateB": 150.0,
                "rateC": 150.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            4: {
                "fbus": 3,
                "tbus": 6,
                "r": 0.0,
                "x": 0.0586,
                "b": 0.0,
                "rateA": 300.0,
                "rateB": 300.0,
                "rateC": 300.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            5: {
                "fbus": 6,
                "tbus": 7,
                "r": 0.0119,
                "x": 0.1008,
                "b": 0.209,
                "rateA": 150.0,
                "rateB": 150.0,
                "rateC": 150.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            6: {
                "fbus": 7,
                "tbus": 8,
                "r": 0.0085,
                "x": 0.072,
                "b": 0.149,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            7: {
                "fbus": 8,
                "tbus": 2,
                "r": 0.0,
                "x": 0.0625,
                "b": 0.0,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            8: {
                "fbus": 8,
                "tbus": 9,
                "r": 0.032,
                "x": 0.161,
                "b": 0.306,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
            9: {
                "fbus": 9,
                "tbus": 4,
                "r": 0.01,
                "x": 0.085,
                "b": 0.176,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
            },
        },
        "gencost": {
            1: {
                "costtype": 2,
                "startup": 1500,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.11, 5, 150],
            },
            2: {
                "costtype": 2,
                "startup": 2000,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.085, 1.2, 600],
            },
            3: {
                "costtype": 2,
                "startup": 3000,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.1225, 1, 335],
            },
        },
    }
    return casefile_dict


def load_case9solution():
    solution = {
        "baseMVA": 100.0,
        "bus": {
            1: {
                "bus_i": 1,
                "type": 3,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0999999995979244,
                "Va": 0,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            2: {
                "bus_i": 2,
                "type": 2,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0973546244747725,
                "Va": 0.02133231397117487,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            3: {
                "bus_i": 3,
                "type": 2,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0866203031590291,
                "Va": -0.10332700657567774,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            4: {
                "bus_i": 4,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.094221515099568,
                "Va": -0.04298613445945756,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            5: {
                "bus_i": 5,
                "type": 1,
                "Pd": 90.0,
                "Qd": 30.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0844484942625547,
                "Va": -0.06949870314439885,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            6: {
                "bus_i": 6,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0999999999782026,
                "Va": -0.14951980703585152,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            7: {
                "bus_i": 7,
                "type": 1,
                "Pd": 100.0,
                "Qd": 35.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0894894840534413,
                "Va": 0.1276213999659528,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            8: {
                "bus_i": 8,
                "type": 1,
                "Pd": 0.0,
                "Qd": 0.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.099999999978765,
                "Va": 0.0909362321027965,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
            9: {
                "bus_i": 9,
                "type": 1,
                "Pd": 125.0,
                "Qd": 50.0,
                "Gs": 0.0,
                "Bs": 0.0,
                "area": 0.0,
                "Vm": 1.0717554471070498,
                "Va": -0.005421158945950168,
                "baseKV": 345.0,
                "zone": 1.0,
                "Vmax": 1.1,
                "Vmin": 0.9,
            },
        },
        "gen": {
            1: {
                "bus": 1,
                "Pg": 89.79870779007074,
                "Qg": 12.965647168632897,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 250.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
            2: {
                "bus": 2,
                "Pg": 134.32060071336346,
                "Qg": 0.031844157165189804,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 300.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
            3: {
                "bus": 3,
                "Pg": 94.18738039126077,
                "Qg": -22.634206967384564,
                "Qmax": 300.0,
                "Qmin": -300.0,
                "Vg": 1,
                "mBase": 100,
                "status": 1,
                "Pmax": 270.0,
                "Pmin": 10.0,
                "Pc1": 0,
                "Pc2": 0,
                "Qc1min": 0,
                "Qc1max": 0,
                "Qc2min": 0,
                "Qc2max": 0,
                "ramp_agc": 0,
                "ramp_10": 0,
                "ramp_30": 0,
                "ramp_q": 0,
                "apf": 0,
            },
        },
        "branch": {
            1: {
                "fbus": 1,
                "tbus": 4,
                "r": 0.0,
                "x": 0.0576,
                "b": 0.0,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": 0.8979870779007074,
                "Pt": -0.8979870779007074,
                "Qf": 0.12965647168632896,
                "Qt": -0.09046983054698969,
                "switching": 1,
            },
            2: {
                "fbus": 4,
                "tbus": 5,
                "r": 0.017,
                "x": 0.092,
                "b": 0.158,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": 0.35221229765343953,
                "Pt": -0.350406909599984,
                "Qf": -0.03890066477405548,
                "Qt": -0.13882359148222675,
                "switching": 1,
            },
            3: {
                "fbus": 5,
                "tbus": 6,
                "r": 0.039,
                "x": 0.17,
                "b": 0.358,
                "rateA": 150.0,
                "rateB": 150.0,
                "rateC": 150.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": -0.549593090400016,
                "Pt": 0.5596906046691518,
                "Qf": -0.16117640851777346,
                "Qt": -0.2219078937558932,
                "switching": 1,
            },
            4: {
                "fbus": 3,
                "tbus": 6,
                "r": 0.0,
                "x": 0.0586,
                "b": 0.0,
                "rateA": 300.0,
                "rateB": 300.0,
                "rateC": 300.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": 0.9418738039126078,
                "Pt": -0.9418738039126078,
                "Qf": -0.22634206967384563,
                "Qt": 0.27291248177027905,
                "switching": 1,
            },
            5: {
                "fbus": 6,
                "tbus": 7,
                "r": 0.0119,
                "x": 0.1008,
                "b": 0.209,
                "rateA": 150.0,
                "rateB": 150.0,
                "rateC": 150.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": 0.3821831992434558,
                "Pt": -0.38069073022082184,
                "Qf": -0.05100458801438591,
                "Qt": -0.18683849803362798,
                "switching": 1,
            },
            6: {
                "fbus": 7,
                "tbus": 8,
                "r": 0.0085,
                "x": 0.072,
                "b": 0.149,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": -0.6193092697791784,
                "Pt": 0.6220958149510928,
                "Qf": -0.16316150196637214,
                "Qt": 0.008189622198387835,
                "switching": 1,
            },
            7: {
                "fbus": 8,
                "tbus": 2,
                "r": 0.0,
                "x": 0.0625,
                "b": 0.0,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": -1.3432060071336347,
                "Pt": 1.3432060071336347,
                "Qf": 0.09332369112548133,
                "Qt": 0.00031844157165189806,
                "switching": 1,
            },
            8: {
                "fbus": 8,
                "tbus": 9,
                "r": 0.032,
                "x": 0.161,
                "b": 0.306,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": 0.7211101921825418,
                "Pt": -0.7071732226728661,
                "Qf": -0.10151331332386916,
                "Qt": -0.1892412487991822,
                "switching": 1,
            },
            9: {
                "fbus": 9,
                "tbus": 4,
                "r": 0.01,
                "x": 0.085,
                "b": 0.176,
                "rateA": 250.0,
                "rateB": 250.0,
                "rateC": 250.0,
                "ratio": 1.0,
                "angle": 0.0,
                "status": 1,
                "angmin": -360.0,
                "angmax": 360.0,
                "Pf": -0.5428267773271339,
                "Pt": 0.5457747802472681,
                "Qf": -0.3107587512008182,
                "Qt": 0.12937049532104491,
                "switching": 1,
            },
        },
        "gencost": {
            1: {
                "costtype": 2,
                "startup": 1500,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.11, 5.0, 150.0],
            },
            2: {
                "costtype": 2,
                "startup": 2000,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.085, 1.2, 600.0],
            },
            3: {
                "costtype": 2,
                "startup": 3000,
                "shutdown": 0,
                "n": 3,
                "costvector": [0.1225, 1.0, 335.0],
            },
        },
        "et": 0.9751458168029785,
        "success": 1,
        "f": 5296.686204000454,
    }

    return solution
