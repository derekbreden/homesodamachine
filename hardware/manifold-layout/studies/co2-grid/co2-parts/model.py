"""Portable frozen CO2 part meshes and nominal connection datums.

All parts use their metal parent's native +Y flow frame. The regulator's
female inlet face is Y0; the check's center is Y0. No production CAD imports.
"""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
PARTS = ("wr1110", "gasher-co2", "co2-adapter-regulator-in",
         "co2-adapter-regulator-out", "co2-adapter-check-in", "co2-adapter-check-out")
GROUPS = {
    "regulator": ("wr1110", "co2-adapter-regulator-in", "co2-adapter-regulator-out"),
    "check": ("gasher-co2", "co2-adapter-check-in", "co2-adapter-check-out"),
}


def _read(name):
    return json.loads((HERE / name).read_text())


def evidence():
    return _read("source-evidence.json")


def dimensions():
    return _read("adapter-dimensions.json")


def part_mesh(name):
    with np.load(HERE / "geometry" / (name + ".npz")) as data:
        return data["v"].copy(), data["f"].copy()


def library():
    return {"co2-parts-" + n: part_mesh(n) for n in PARTS}


def _port(point, axis, kind="tube_socket", tube_od=6.35):
    result = {"point_mm": list(point), "outward_axis": list(axis), "kind": kind}
    if tube_od is not None:
        result["tube_od_mm"] = tube_od
    if kind == "tube_socket":
        result.update(tube_insertion_mm=15.7,
            tube_insertion_basis="Manufacturer dimension with collet released; selected layout depth")
    return result


def interfaces():
    return {
        "regulator": {
            "flow_axis": [0., 1., 0.],
            "tube_inlet": _port([0., -13.7, 0.], [0., -1., 0.]),
            "tube_outlet": _port([0., 86.47, 0.], [0., 1., 0.]),
            "metal_inlet": _port([0., 0., 0.], [0., -1., 0.], "female_1/4_NPT", None),
            "metal_outlet": _port([0., 63.65, 0.], [0., 1., 0.], "male_1/4_NPT", None),
            "outlet_thread_shoulder_y_mm": 54.47,
            "outlet_exposed_thread_projection_mm": 9.18,
            "barrel": {"point_mm": [0., 32.35, 0.], "axis": [0., 1., 0.],
                       "diameter_mm": 18.87, "length_mm": 35.4},
            "selected_male_inlet_engagement_mm": 14.3,
            "selected_female_outlet_engagement_mm": 9.18,
            "tube_mouth_span_mm": 100.17,
        },
        "check": {
            "flow_axis": [0., 1., 0.],
            "tube_inlet": _port([0., -33.7, 0.], [0., -1., 0.]),
            "tube_outlet": _port([0., 41., 0.], [0., 1., 0.]),
            "metal_inlet": _port([0., -20., 0.], [0., -1., 0.], "female_1/4_NPT", None),
            "metal_outlet": _port([0., 20., 0.], [0., 1., 0.], "male_1/4_NPT", None),
            "outlet_thread_shoulder_y_mm": 9.,
            "outlet_exposed_thread_projection_mm": 11.,
            "round_inlet_boss": {"point_mm": [0., -14.5, 0.], "axis": [0., 1., 0.],
                                 "diameter_mm": 15.5, "length_mm": 11.},
            "selected_male_inlet_engagement_mm": 14.3,
            "selected_female_outlet_engagement_mm": 11.,
            "tube_mouth_span_mm": 74.7,
        },
        "cap_handoff": copy.deepcopy(evidence()["cap_handoff"]),
        "connection_assumptions": {
            "metal_threads": "1/4NPT female inlet and male outlet on regulator and check; no need for a push-connect transition between compatible threaded ports.",
            "male_inlet_makeup": "Full14.3mm published thread projection is the selected layout engagement. With11mm engagement the inlet mouth stands3.3mm farther out.",
            "female_outlet_makeup": "9.18mm on regulator, bounded by scanned exposed stub;11mm on Gasher, from nominal reference.",
            "internal_geometry": "External occupancy models; simple bores/thread cylinders do not establish sealing or actual internal flow.",
        },
    }


def _pose(rotation=None, translation=None):
    return (np.eye(3) if rotation is None else np.asarray(rotation, float),
            np.zeros(3) if translation is None else np.asarray(translation, float))


def transform_port(port, rotation=None, translation=None):
    r, t = _pose(rotation, translation)
    out = copy.deepcopy(port)
    out["point_mm"] = (r @ np.array(port["point_mm"]) + t).tolist()
    out["outward_axis"] = (r @ np.array(port["outward_axis"])).tolist()
    return out


def ports(group="regulator", rotation=None, translation=None):
    return {n: transform_port(p, rotation, translation)
            for n, p in interfaces()[group].items()
            if isinstance(p, dict) and "outward_axis" in p}


def instances(poses):
    """All six parts, with each three-part group moved by poses[group].

    Poses contain rotation plus translation_mm (or translation). Geometry IDs
    come from library(). No tube links are supplied by this hardware module.
    """
    result = []
    for group, names in GROUPS.items():
        pose = poses[group]
        r, t = _pose(pose.get("rotation"), pose.get("translation_mm", pose.get("translation")))
        for name in names:
            result.append({"name": name, "geometry": "co2-parts-" + name,
                "rotation": r.tolist(), "translation": t.tolist(),
                "kind": "component", "role": "gas", "context": True,
                "label": "WR1105 regulator · scanned WR1110 exterior" if name == "wr1110"
                    else "GASHER CO2 check" if name == "gasher-co2" else
                    "John Guest PI010822S · published envelope" if name.endswith("-in") else
                    "John Guest PI450822S · published envelope",
                "co2_group": group})
    return result


def direct_joint(engagement_mm=9.18):
    """The check female inlet seats directly on the regulator male outlet.

    Engagement9.18mm is the exposed scanned regulator stub, putting the check
    face at the regulator hex shoulder. This is a compact nominal make-up.
    """
    return {"rotation": np.eye(3).tolist(),
            "translation_mm": [0., 83.65-engagement_mm, 0.],
            "nominal_engagement_mm": engagement_mm,
            "regulator_male_tip_y_mm": 63.65,
            "check_female_face_y_mm": 63.65-engagement_mm,
            "interface": "WR1105 male1/4NPT directly into GASHER female1/4NPT",
            "scope": "Compatible nominal thread types; make-up reach is an explicit estimate, not a measured or sealing-qualified joint"}


def direct_instances(rotation=None, translation=None, engagement_mm=9.18, inlet_engagement_mm=14.3):
    """Four-part compact series: inletJG + regulator + check + outletJG."""
    r, t = _pose(rotation, translation)
    joint = direct_joint(engagement_mm)
    check_t = r @ np.array(joint["translation_mm"]) + t
    records = instances({"regulator": {"rotation": r, "translation_mm": t},
                         "check": {"rotation": r, "translation_mm": check_t}})
    result = [m for m in records if m["name"] not in
              ("co2-adapter-regulator-out", "co2-adapter-check-in")]
    for row in result:
        if row["name"] == "co2-adapter-regulator-in":
            row["translation"] = (np.array(row["translation"]) +
                r @ np.array([0., inlet_engagement_mm-14.3, 0.])).tolist()
            row["nominal_thread_engagement_mm"] = inlet_engagement_mm
    return result


def direct_ports(rotation=None, translation=None, engagement_mm=9.18, inlet_engagement_mm=14.3):
    r, t = _pose(rotation, translation)
    check_t = r @ np.array(direct_joint(engagement_mm)["translation_mm"]) + t
    inlet = ports("regulator", r, t)["tube_inlet"]
    inlet["point_mm"] = (np.array(inlet["point_mm"]) +
        r @ np.array([0., inlet_engagement_mm-14.3, 0.])).tolist()
    return {"inlet": inlet,
            "outlet": ports("check", r, check_t)["tube_outlet"]}


def mates(direct=True):
    pairs = [("wr1110", "co2-adapter-regulator-in"),
             ("gasher-co2", "co2-adapter-check-out")]
    pairs += [("wr1110", "gasher-co2")] if direct else [
        ("wr1110", "co2-adapter-regulator-out"),
        ("gasher-co2", "co2-adapter-check-in")]
    return [{"a": a, "b": b, "connection": "Nominal made-up1/4NPT thread joint"}
            for a, b in pairs]


def cap_handoff():
    return copy.deepcopy(evidence()["cap_handoff"])


def world_meshes(records):
    lib = library()
    result = {}
    for row in records:
        v, f = lib[row["geometry"]]
        result[row["name"]] = (v @ np.asarray(row["rotation"]).T + row["translation"], f)
    return result
