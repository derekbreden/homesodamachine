"""Frozen local connection assets for the wet/dry arrangement study.

No production reference, wiring generator or CAD dependency is imported. Meshes
and datum points use the associated frozen component's source-world frame.
Pass that component's arrangement rotation/translation to resolve them.
"""
from pathlib import Path
import copy
import json

import numpy as np

HERE = Path(__file__).resolve().parent
PREFIX = "connection-"


def _read(name):
    return json.loads((HERE / name).read_text())


def _poses(layout_instances):
    if isinstance(layout_instances, dict) and "instances" in layout_instances:
        layout_instances = layout_instances["instances"]
    if isinstance(layout_instances, list):
        layout_instances = {m["name"]: m for m in layout_instances}
    result = {}
    for name, m in layout_instances.items():
        t = m.get("translation", m.get("translation_mm", [0., 0., 0.]))
        result[name] = np.array(m.get("rotation", np.eye(3)), float), np.array(t, float)
    return result


def library():
    """Return source-frame meshes keyed by each instance's ``geometry`` field."""
    result = {}
    for p in sorted((HERE / "geometry").glob("*.npz")):
        with np.load(p) as d:
            result[PREFIX + p.stem] = d["v"], d["f"]
    return result


def instances(layout_instances, *, probes=False, optional_j8=False, owners=None):
    """Return 30 installed instances; access probes and unused J8 are opt-in.

    ``layout_instances`` may be the layout's instance list, its whole JSON
    object, or a name-to-pose mapping using translation/translation_mm.
    """
    selection = _read("selection.json")
    rows = copy.deepcopy(selection["physical"])
    if probes:
        rows.extend(copy.deepcopy(selection["probes"]))
    if optional_j8:
        rows.extend([
            {"name": "optional-terminal-J8", "owner": "pcba", "geometry": "J8-plug",
             "kind": "component", "role": "clearance", "label": "J8 · unused expansion mating envelope"},
            {"name": "optional-local-lead-J8", "owner": "pcba", "geometry": "J8-wire-edge",
             "kind": "tube", "role": "clearance", "label": "J8 · unused expansion lead envelope"},
        ])
    poses = _poses(layout_instances)
    result = []
    for row in rows:
        owner = row.pop("owner")
        if owners is not None and owner not in owners:
            continue
        if owner not in poses:
            raise KeyError(f"Connection owner {owner!r} has no layout pose")
        r, t = poses[owner]
        row.update(geometry=PREFIX + row["geometry"], rotation=r.tolist(),
                   translation=t.tolist(), context=True, connection_owner=owner)
        result.append(row)
    return result


def world_datums(layout_instances):
    """Resolve every JST cavity, J10 role, and physical PSU/relay pole.

    ``logical`` is an update map compatible with the study's existing terminal
    records: point/outward describe conductor entry, while screw_head_mm and
    screw_axis describe tool approach. Unused poles/cavities remain explicit.
    """
    data, selection = _read("interfaces.json"), _read("selection.json")
    poses = _poses(layout_instances)
    def carried(datum, owner):
        r, t = poses[owner]
        return {"point_mm": (r @ datum["point_mm"] + t).tolist(),
                "axis": (r @ datum["axis"]).tolist()}
    result = {"headers": {}, "J10": {}, "power": {}, "logical": {}}
    for name, h in data["headers"].items():
        populated = set(h["wire_path_points_edge_mm"]) if h["installed_harness"] else set()
        rows = []
        for pin in h["wire_exits"]:
            d = {**pin, **carried(pin, "pcba"), "installed_wire": pin["id"] in populated}
            rows.append(d)
            result["logical"][pin["id"]] = {
                "id": pin["id"], "part": "pcba", "point": d["point_mm"],
                "outward": d["axis"], "kind": "JST-XH", "status": "nominal",
                "pin": str(pin["pin"]), "installed_wire": d["installed_wire"],
                "basis": "Frozen fabricated pin map and official JST nominal mated height; header normal verified in imported component models",
            }
        result["headers"][name] = {"housing": h["housing"], "pins": rows,
                                   "installed_harness": h["installed_harness"],
                                   "unused_basis": h["unused_basis"]}
    for name, entry in data["J10"]["pins"].items():
        mouth, screw = carried(entry["wire_mouth"], "pcba"), carried(entry["screw_head"], "pcba")
        result["J10"][name] = {"wire_mouth": mouth, "screw_head": screw}
        result["logical"][name] = {
            "id": name, "part": "pcba", "point": mouth["point_mm"], "outward": mouth["axis"],
            "kind": "screw", "status": "nominal", "installed_wire": True,
            "screw_head_mm": screw["point_mm"], "screw_axis": screw["axis"],
            "basis": data["J10"]["source"],
        }
    for owner, group in data["power"].items():
        result["power"][owner] = {}
        for label, entry in group["terminals"].items():
            mouth, screw = carried(entry["wire_mouth"], owner), carried(entry["screw_head"], owner)
            result["power"][owner][label] = {"wire_mouth": mouth, "screw_head": screw,
                                            "basis": group["basis"]}
            logical = next((n for n, pole in selection["power_logical_poles"].items() if pole == label), None) if owner == "psu" else owner + "." + label
            if logical:
                result["logical"][logical] = {
                    "id": logical, "part": owner, "physical_pole": label,
                    "point": mouth["point_mm"], "outward": mouth["axis"],
                    "screw_head_mm": screw["point_mm"], "screw_axis": screw["axis"],
                    "kind": "screw", "status": "nominal", "installed_wire": label != "NC",
                    "basis": group["basis"],
                }
    result["scope"] = selection["scope"]
    result["service"] = selection["service"]
    return result


def mates():
    """Declare intended housing/header and wire/terminal contact pairs."""
    result = []
    for row in _read("selection.json")["physical"]:
        name, owner = row["name"], row["owner"]
        if name.startswith("terminal-"):
            result.append({"a": name, "b": owner, "connection": "Mated XH housing in its PCB header"})
        elif name.startswith("local-lead-J") and "." not in name:
            result.append({"a": name, "b": "terminal-" + name[len("local-lead-"):],
                           "connection": "Populated conductors leave their crimp housing"})
        else:
            result.append({"a": name, "b": owner, "connection": "Side-entry conductor at its terminal mouth"})
    return result


def frozen_checks():
    """Read the selected manual audit; this does not execute a check or gate."""
    return _read("selected-audit.json")
