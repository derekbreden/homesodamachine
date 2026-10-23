"""Place the dry-side electronics and bare rear fittings around the water header.

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


def library():
    import trimesh
    result = parent.library()
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
    scene["metrics"] = measure(scene, geometries, args.check)
    report = {"scope": "Selected-component wet/dry arrangement in the current-size enclosure",
        "units": "mm", "layout": scene["layout"], "metrics": scene["metrics"],
        "instances": scene["instances"], "mates": scene["mates"]}
    (HERE / "study.json").write_text(json.dumps(report, indent=2) + "\n")
    used = {m["geometry"] for m in scene["instances"]}
    packed = {n: base.pack(*geometries[n], 5200 if n == "pump" else 3600) for n in sorted(used)}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"space": parent.water.SPACE,
        "geometries": packed, "variants": [scene]}, separators=(",", ":")))
    print(json.dumps(scene["metrics"], indent=2))


if __name__ == "__main__":
    main()
