"""Frozen EcoReg candidate geometry and nominal interfaces; NumPy only."""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
PARTS = ("ecoreg-body", "ecoreg-inlet-adapter", "ecoreg-outlet-adapter")


def dimensions():
    return json.loads((HERE/"dimensions.json").read_text())


def library():
    result = {}
    for name in (*PARTS, "ecoreg-with-adapters"):
        with np.load(HERE/"geometry"/(name+".npz")) as data:
            result[name] = data["v"].copy(), data["f"].copy()
    return result


def instances(rotation=None, translation=None, with_adapters=True):
    r = np.eye(3).tolist() if rotation is None else np.array(rotation).tolist()
    t = [0., 0., 0.] if translation is None else list(translation)
    return [{"name": name, "geometry": name, "rotation": r, "translation": t,
        "kind": "component", "role": "regulator" if name == "ecoreg-body" else "fitting",
        "context": True, "label": "EcoReg239KS1245 · research candidate" if name == "ecoreg-body"
        else "JG PP010822E · nominal water adapter"} for name in (PARTS if with_adapters else PARTS[:1])]


def ports(rotation=None, translation=None, with_adapters=True):
    r = np.eye(3) if rotation is None else np.array(rotation, float)
    t = np.zeros(3) if translation is None else np.array(translation, float)
    result = copy.deepcopy(dimensions()["tube_ports" if with_adapters else "body_ports"])
    for row in result.values():
        row["point_mm"] = (r@np.array(row["point_mm"])+t).tolist()
        row["outward_axis"] = (r@np.array(row["outward_axis"])).tolist()
        if with_adapters:
            row.update(tube_od_mm=6.35, insertion_estimate_mm=12.7)
    return result


def mates():
    return [{"a": "ecoreg-body", "b": n, "connection": "Nominal made-up1/4NPT joint",
             "engagement_estimate_mm": 11.} for n in PARTS[1:]]
