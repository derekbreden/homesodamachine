"""Portable installed TPU-joint meshes in the two metal parents' native frames."""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
GROUPS = {
    "regulator": ("regulator-inlet-tpu", "regulator-inlet-band-cuff", "regulator-inlet-band-tube"),
    "check": ("check-outlet-tpu", "check-outlet-band-cuff", "check-outlet-band-tube"),
}


def interfaces():
    return json.loads((HERE / "interfaces.json").read_text())


def mesh(name, reference=False):
    with np.load(HERE / ("reference" if reference else "geometry") / (name+".npz")) as data:
        return data["v"].copy(), data["f"].copy()


def library():
    return {name: mesh(name) for names in GROUPS.values() for name in names}


def metal_library():
    return {"co2-metal-"+name: mesh(name, True) for name in ("wr1110", "gasher-co2")}


def _pose(row=None):
    row = row or {}
    return (np.array(row.get("rotation", np.eye(3)), float),
            np.array(row.get("translation_mm", row.get("translation", [0., 0., 0.])), float))


def instances(poses=None):
    """Six TPU/ring instances, placed by poses['regulator'] and poses['check']."""
    poses = poses or {}
    result = []
    for group, names in GROUPS.items():
        r, t = _pose(poses.get(group))
        for name in names:
            result.append({"name": name, "geometry": name, "rotation": r.tolist(),
                "translation": t.tolist(), "kind": "component", "context": True,
                "role": "tpu" if name.endswith("-tpu") else "clamp",
                "co2_group": group,
                "label": "Regulator inlet · threadless TPU boss cuff" if name == "regulator-inlet-tpu"
                    else "Check outlet · threadless TPU 90° cuff" if name == "check-outlet-tpu"
                    else "9 mm clamp band · metal cuff" if name.endswith("cuff")
                    else "9 mm clamp band · tube socket"})
    return result


def direct_poses(rotation=None, translation=None):
    r = np.eye(3) if rotation is None else np.array(rotation, float)
    t = np.zeros(3) if translation is None else np.array(translation, float)
    return {"regulator": {"rotation": r.tolist(), "translation_mm": t.tolist()},
            "check": {"rotation": r.tolist(), "translation_mm": (t+r@[0., 74.47, 0.]).tolist()}}


def direct_instances(rotation=None, translation=None, include_metals=False):
    poses = direct_poses(rotation, translation)
    result = instances(poses)
    if include_metals:
        for group, name in (("regulator", "wr1110"), ("check", "gasher-co2")):
            r, t = _pose(poses[group])
            result.append({"name": name, "geometry": "co2-metal-"+name,
                "rotation": r.tolist(), "translation": t.tolist(),
                "kind": "component", "role": "gas", "context": True,
                "label": "WR1105 · scanned WR1110 exterior" if name == "wr1110" else "GASHER CO2 check"})
    return result


def ports(poses=None):
    poses = poses or direct_poses()
    data = interfaces()
    result = {}
    for group, name in (("regulator", "inlet"), ("check", "outlet")):
        r, t = _pose(poses.get(group))
        port = copy.deepcopy(data[group]["tube_mouth"])
        port["point_mm"] = (r@np.array(port["point_mm"])+t).tolist()
        port["outward_axis"] = (r@np.array(port["outward_axis"])).tolist()
        port["tube_od_mm"] = 6.35
        port["tube_insertion_mm"] = 15.
        port["tube_end_at_stop_mm"] = (r@np.array(data[group]["tube_end_at_stop_mm"])+t).tolist()
        port["owner"] = GROUPS[group][0]
        result[name] = port
    return result


def direct_ports(rotation=None, translation=None):
    return ports(direct_poses(rotation, translation))


def mates(include_direct_thread=True):
    result = []
    for group, names in GROUPS.items():
        owner = "wr1110" if group == "regulator" else "gasher-co2"
        result.append({"a": owner, "b": names[0], "connection": "Threadless external metal cuff"})
        result.extend({"a": names[0], "b": n, "connection": "Closed clamp band on plain TPU seat"}
                      for n in names[1:])
    if include_direct_thread:
        result.append({"a": "wr1110", "b": "gasher-co2",
            "connection": "Direct metal1/4NPT joint", "nominal_engagement_mm": 9.18})
    return result


def world_meshes(records):
    geometries = {**library(), **metal_library()}
    return {row["name"]: (geometries[row["geometry"]][0]@np.array(row["rotation"]).T
                + row["translation"], geometries[row["geometry"]][1]) for row in records}
