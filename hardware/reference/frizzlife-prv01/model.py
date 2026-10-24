"""Frozen Frizzlife PRV01 geometry and nominal interfaces; NumPy only."""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
PARTS = ("frizzlife-body", "frizzlife-inlet-collet", "frizzlife-outlet-collet",
         "frizzlife-inlet-clip", "frizzlife-outlet-clip")


def dimensions():
    return json.loads((HERE/"dimensions.json").read_text())


def library():
    result = {}
    for name in (*PARTS, "frizzlife-prv01"):
        with np.load(HERE/"geometry"/(name+".npz")) as data:
            result[name] = data["v"].copy(), data["f"].copy()
    return result


def instances(rotation=None, translation=None):
    r = np.eye(3).tolist() if rotation is None else np.array(rotation).tolist()
    t = [0., 0., 0.] if translation is None else list(translation)
    return [{"name": name, "geometry": name, "rotation": r, "translation": t,
             "kind": "component", "role": "regulator" if name == PARTS[0] else "fitting",
             "context": True, "label": "Frizzlife PRV01 · native 1/4 push-connect" if name == PARTS[0]
             else "Frizzlife PRV01 · release collet" if "collet" in name else "Frizzlife PRV01 · lock clip"}
            for name in PARTS]


def ports(rotation=None, translation=None):
    r = np.eye(3) if rotation is None else np.array(rotation, float)
    t = np.zeros(3) if translation is None else np.array(translation, float)
    result = copy.deepcopy(dimensions()["tube_ports"])
    for row in result.values():
        row["point_mm"] = (r@np.array(row["point_mm"])+t).tolist()
        row["outward_axis"] = (r@np.array(row["outward_axis"])).tolist()
    return result


def mates():
    return [{"a": PARTS[0], "b": name, "connection": "Native socket release hardware"}
            for name in PARTS[1:]]
