"""Place connected dry-side electronics and rear fittings around the water header.

This is an isolated arrangement study, not a production-pack migration.
Run --check manually to ask about the selected meshes and fitting departures.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ceiling_fit", HERE.parent / "ceiling-fit/study.py")
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
base = parent.base
spec = importlib.util.spec_from_file_location("wet_dry_connections", HERE / "connections/model.py")
connections = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connections)
spec = importlib.util.spec_from_file_location("wet_dry_forward", HERE / "forward-context/study.py")
forward = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forward)


def library():
    import trimesh
    result = parent.library()
    result.update(connections.library())
    result.update(forward.library())
    for path in sorted((HERE / "parts").glob("*.npz")):
        with np.load(path) as data:
            result[path.stem] = (data["v"], data["f"])
    context = json.loads((HERE / "layout.json").read_text())
    inlet = np.array([37.2499988712316, 414.38496052818664, 334.3760478805363])
    length = context["water_inboard_mouth_mm"][1] - inlet[1]
    rotation = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    tube = trimesh.creation.annulus(r_min=2.12, r_max=3.175, height=length+15+12.7, sections=32)
    result["straight-water-link"] = (tube.vertices @ rotation.T + [0, (length+12.7-15)/2, 0], tube.faces)
    for port in context["wet_ports"]:
        if port["name"] == "bulkhead-water":
            continue
        radius = port["tube_od_mm"] / 2
        tube = trimesh.creation.annulus(r_min=radius*.66, r_max=radius, height=30, sections=24)
        result[port["name"] + "-departure"] = (tube.vertices @ rotation.T + [0, -5, 0], tube.faces)
    return result


def pose(geometries):
    scene = parent.clocked(geometries)
    scene.update(id="wet-dry", title="Dry electronics wall · grouped wet rear connections")
    context = json.loads((HERE / "layout.json").read_text())
    old = json.loads((parent.HERE / "context.json").read_text())
    retained = {"funnel", "funnel-frame", "bulkhead-nut"}
    scene["instances"].extend(copy.deepcopy([m for m in old["instances"] if m["name"] in retained]))
    scene["mates"].extend(copy.deepcopy(old["mates"]))
    scene["instances"].extend(copy.deepcopy(context["instances"]))
    scene["instances"].extend(connections.instances(context["instances"]))
    scene["mates"].extend(connections.mates())
    scene["mates"].extend(copy.deepcopy(context.get("mates", [])))
    scene["pins"].extend(copy.deepcopy(context.get("pins", [])))
    for port in context["wet_ports"]:
        if port["name"] == "bulkhead-water":
            continue
        name = port["name"] + "-departure"
        scene["instances"].append(base.instance(name, name, port["inboard_mouth_mm"],
            role="wet", kind="tube", context=True,
            label=port["label"] + " · 20 mm inward departure, not a complete route"))
        scene["mates"].append({"a": name, "b": port["name"],
            "connection": "Initial tube departure; 10 mm illustrative insertion"})
    inlet = scene["layout"]["asse_inlet_mouth_world_mm"]
    for instance in scene["instances"]:
        if instance["name"] == "water-in":
            instance.update(geometry="straight-water-link", rotation=np.eye(3).tolist(),
                translation=inlet, label="Water bulkhead to ASSE · straight inlet tube")
    scene["mates"].extend([
        {"a": "water-in", "b": "asse-inlet-tpu", "point": inlet, "insertion_mm": 15.0},
        {"a": "water-in", "b": "bulkhead-water", "point": context["water_inboard_mouth_mm"],
         "insertion_mm": 12.7, "insertion_basis": "layout estimate"},
    ])
    for name in ("left-wall", "right-wall", "back-wall", "ceiling"):
        scene["instances"].append(base.instance(name, name, role="structure", kind="component",
            context=True, label=context["structure_labels"][name]))
    scene["layout"].update(context["description"])
    return scene


def connection_fit(scene, geometries):
    """Ask about installed plugs/leads against this exact native context once."""
    import fcl
    meshes = base.world_meshes(scene, geometries)
    forward_meshes = base.world_meshes({"instances": forward.obstacles()}, geometries)
    meshes.update(forward_meshes)
    objects = {}
    bounds = {}
    for name, (v, f) in meshes.items():
        model = fcl.BVHModel()
        model.beginModel(len(v), len(f))
        model.addSubModel(v, f.astype(np.int32))
        model.endModel()
        objects[name] = fcl.CollisionObject(model)
        bounds[name] = v.min(0), v.max(0)
    mates = {frozenset((m["a"], m["b"])) for m in scene["mates"]}
    rows = [m for m in scene["instances"] if "connection_owner" in m]
    checked, issues, forward_issues = set(), [], []
    for row in rows:
        name = row["name"]
        for other in meshes:
            pair = frozenset((name, other))
            if name == other or pair in checked or pair in mates:
                continue
            checked.add(pair)
            lo, hi = bounds[name]
            low, high = bounds[other]
            if np.any(np.minimum(hi, high) - np.maximum(lo, low) < .001):
                continue
            if fcl.collide(objects[name], objects[other], fcl.CollisionRequest(), fcl.CollisionResult()):
                issues.append([name, other])
    # The retained wet neighbors are context, not another production-pack audit.
    for name in ("pcba", "psu", "relay-1", "relay-2", "c14-inlet", "keystone-jack"):
        lo, hi = bounds[name]
        for other in forward_meshes:
            low, high = bounds[other]
            if np.any(np.minimum(hi, high) - np.maximum(lo, low) < .001):
                continue
            if fcl.collide(objects[name], objects[other], fcl.CollisionRequest(), fcl.CollisionResult()):
                forward_issues.append([name, other])
    leads = np.vstack([meshes[m["name"]][0] for m in rows
                       if m["name"].startswith("local-lead-J")])
    return {"scope": "Installed mating housings and local lead meshes against selected bodies, tubes, clamps and rebuilt wall/roof solids; intended contacts excluded",
            "installed_connection_meshes": len(rows), "interferences": issues,
            "changed_electronics_to_retained_forward_context": forward_issues,
            "pcb_lead_top_z_mm": float(leads[:, 2].max()),
            "pcb_lead_to_ordinary_ceiling_mm": float(346 - leads[:, 2].max()),
            "pcb_lead_to_left_wall_mm": float(leads[:, 0].min() + 98.5),
            "access_audit": "connections/selected-audit.json",
            "service": connections.world_datums(scene["instances"])["service"]}


def measure(scene, geometries, check=False):
    meshes = base.world_meshes(scene, geometries)
    context = json.loads((HERE / "layout.json").read_text())
    result = {
        "electronics_wall": "-X", "wet_connections_rear_half": "+X",
        "bulkhead_count": 6, "printed_label_collars_included": False,
        "water_header_poses": "ceiling-fit, unchanged",
        "ceiling_retained_stock_mm": 3.0,
        "component_bounds_mm": {n: [v.min(0).tolist(), v.max(0).tolist()]
            for n, (v, f) in meshes.items() if n in context["report_components"]},
    }
    if check:
        result["unrelated_body_interferences"] = base.interference(scene, geometries)
        result["installed_connections"] = connection_fit(scene, geometries)
        result["selected_gaps_mm"] = {
            a + "_to_" + b: parent.lower.surface_distance(meshes[a], meshes[b])
            for a, b in context["measure_pairs"]
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = library()
    scene = pose(geometries)
    context = json.loads((HERE / "layout.json").read_text())
    datums = connections.world_datums(context["instances"])
    (HERE / "connections/world-datums.json").write_text(json.dumps(datums, indent=2) + "\n")
    scene["metrics"] = measure(scene, geometries, args.check)
    report = {"scope": "Selected-component wet/dry arrangement in the current-size enclosure",
        "units": "mm", "layout": scene["layout"], "metrics": scene["metrics"],
        "instances": scene["instances"], "mates": scene["mates"]}
    (HERE / "study.json").write_text(json.dumps(report, indent=2) + "\n")
    # Access probes are visible on request; they are not installed components.
    viewer = copy.deepcopy(scene)
    viewer["instances"].extend([m for m in connections.instances(context["instances"], probes=True)
                                if m["kind"] == "probe"])
    for m in forward.obstacles():
        viewer["instances"].append({**m, "forward_context": True})
    for height in ("low", "high"):
        viewer["instances"].append({**forward.ghost(height), "role": "ghost", "ghost_height": height})
    used = {m["geometry"] for m in viewer["instances"]}
    packed = {n: base.pack(*geometries[n], 12000 if n.startswith("connection-")
                          else 5200 if n == "pump" else 3600) for n in sorted(used)}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"space": parent.water.SPACE,
        "geometries": packed, "variants": [viewer]}, separators=(",", ":")))
    print(json.dumps(scene["metrics"], indent=2))


if __name__ == "__main__":
    main()
