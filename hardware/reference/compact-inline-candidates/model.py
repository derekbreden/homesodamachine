"""Portable candidate meshes and their frozen socket interfaces; NumPy only."""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent


def dimensions():
    return json.loads((HERE/"dimensions.json").read_text())


def library():
    result = {}
    for name in ("candidate-regulator", "candidate-check"):
        with np.load(HERE/"geometry"/(name+".npz")) as data:
            result[name] = (data["v"].copy(), data["f"].copy())
    return result


def ports(kind="check", rotation=None, translation=None):
    r = np.eye(3) if rotation is None else np.array(rotation, float)
    t = np.zeros(3) if translation is None else np.array(translation, float)
    key = "fluidfit_hcvu_quarter" if kind in ("check", "candidate-check") else "pisco_rvfup_quarter"
    result = copy.deepcopy(dimensions()[key]["ports"])
    for row in result.values():
        row["point_mm"] = (r@np.array(row["point_mm"])+t).tolist()
        row["outward_axis"] = (r@np.array(row["outward_axis"])).tolist()
        row["tube_stop_mm"] = (r@np.array(row["tube_stop_mm"])+t).tolist()
    return result


def instance(kind="check", rotation=None, translation=None, name=None):
    check = kind in ("check", "candidate-check")
    return {"name": name or ("inline-check" if check else "inline-regulator"),
            "geometry": "candidate-check" if check else "candidate-regulator",
            "rotation": np.eye(3).tolist() if rotation is None else np.asarray(rotation).tolist(),
            "translation": [0., 0., 0.] if translation is None else list(translation),
            "kind": "component", "role": "gas", "context": True,
            "label": "Fluidfit HCVU1/4-1/4G · OEM dimensioned layout candidate" if check else
                     "PISCO RVFUP1/4-1/4-0.3 · scanned exterior"}
