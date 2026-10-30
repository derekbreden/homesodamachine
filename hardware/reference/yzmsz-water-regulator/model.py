"""Frozen scan-fitted YZMSZ fixed 0.3 MPa regulator exterior; NumPy only."""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
NAME = "yzmsz-water-regulator"


def dimensions():
    return json.loads((HERE/"dimensions.json").read_text())


def library():
    with np.load(HERE/"geometry"/(NAME+".npz")) as data:
        return {NAME: (data["v"].copy(), data["f"].copy())}


def instances(rotation=None, translation=None):
    return [{"name": NAME, "geometry": NAME,
             "rotation": np.eye(3).tolist() if rotation is None else np.array(rotation).tolist(),
             "translation": [0.0, 0.0, 0.0] if translation is None else list(translation),
             "kind": "component", "role": "regulator", "context": True,
             "label": "YZMSZ 0.3 MPa water regulator · scanned exterior"}]


def ports(rotation=None, translation=None):
    r = np.eye(3) if rotation is None else np.array(rotation, float)
    t = np.zeros(3) if translation is None else np.array(translation, float)
    result = copy.deepcopy(dimensions()["tube_ports"])
    for row in result.values():
        row["point_mm"] = (r@np.array(row["point_mm"])+t).tolist()
        row["outward_axis"] = (r@np.array(row["outward_axis"])).tolist()
    return result


def mates():
    return []
