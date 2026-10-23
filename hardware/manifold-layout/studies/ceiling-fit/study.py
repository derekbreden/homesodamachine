"""Lower the square water header and place a few simple enclosure neighbours.

This is a reproducible implementation study, separate from the production pack.
The ceiling is a native solid with underside recesses and at least 3 mm stock.
Run --check to ask about the selected body, ceiling and path clearances.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import math

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("folded_water", HERE.parent / "folded-va-xz/study.py")
water = importlib.util.module_from_spec(spec)
spec.loader.exec_module(water)
base, lower = water.base, water.lower
ANGLE = 27.5
CAP = water.SPACE["world_core_plain_top_z_mm"]
FIXED = {"pump", "pump-sliding-foot", "pump-outlet-tpu", "pump-outlet-barb-band",
         "pump-outlet-tube-band", "check", "carbonator-fold", "check-carbonator"}
INLET = {"pump-inlet-tpu", "pump-inlet-barb-band", "pump-inlet-tube-band"}


def library():
    import trimesh
    result = water.library()
    for path in sorted((HERE / "parts").glob("*.npz")):
        with np.load(path) as data:
            result[path.stem] = (data["v"], data["f"])
    inlet = np.array([37.2499988712316, 414.38496052818664, 334.3760478805363])
    length = 446.51 - inlet[1]
    tube = trimesh.creation.annulus(r_min=2.12, r_max=3.175, height=length + 15 + 12.7, sections=32)
    rotation = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    result["straight-water-link"] = (tube.vertices @ rotation.T + [0, (length + 12.7 - 15) / 2, 0], tube.faces)
    return result


def clocked(geometries, angle=ANGLE):
    scene = water.pose(geometries)
    scene.update(id="ceiling-fit", title="Square header · 3 mm ceiling pockets")
    frame = np.array(scene["metrics"]["local_to_enclosure_rotation"])
    origin = np.array(scene["metrics"]["local_to_enclosure_translation_mm"])
    theta = math.radians(angle)
    q = np.array([0, math.cos(theta), -math.sin(theta)])
    q0 = np.array([0, math.cos(math.radians(25)), -math.sin(math.radians(25))])
    reach = 18.5 + base.ED["socket"][0][1]
    delta_local = reach * (q - q0)
    delta = frame @ delta_local
    for m in scene["instances"]:
        name = m["name"]
        if name in FIXED:
            continue
        if name in INLET:
            m["rotation"] = (frame @ lower.rx(-math.pi / 2 - theta)).tolist()
            if name == "pump-inlet-tpu":
                m["label"] = f"Existing pump TPU elbow · clocked {angle:g}° below horizontal"
        elif name == "lower-pump-elbow":
            x = np.array([1, 0, 0])
            rotation = np.column_stack((x, -q, np.cross(x, -q)))
            corner = np.array([-4.916132605004726, 0, 0]) + reach * q
            m["translation"] = (frame @ corner + origin).tolist()
            m["rotation"] = (frame @ rotation).tolist()
        else:
            m["translation"] = (np.array(m["translation"]) + delta).tolist()
    for j in scene["mates"]:
        if {j["a"], j["b"]} == {"pump-inlet-tpu", "lower-pump-elbow"}:
            movement = frame @ (18.5 * (q - q0))
        elif j["a"] not in FIXED and j["b"] not in FIXED:
            movement = delta
        else:
            continue
        j["point"] = (np.array(j["point"]) + movement).tolist()
    for p in scene["pins"]:
        if p["text"] not in {"Pump", "To carbonator"}:
            p["at"] = (np.array(p["at"]) + delta).tolist()
    for a in scene["arrows"]:
        a["at"] = (np.array(a["at"]) + delta).tolist()
    for k, v in scene["layout"].items():
        if k.endswith("_world_mm"):
            scene["layout"][k] = (np.array(v) + delta).tolist()
    scene["layout"].update(pump_joint_angle_degrees=angle, rigid_header_translation_mm=delta.tolist(),
        rigid_header_lowering_mm=-float(delta[2]), rigid_header_rotations_unchanged=True)
    scene.pop("metrics")
    return scene


def high_surface_points(vertices, faces, z):
    """Include edge crossings so a tall triangle cannot hide a wide footprint."""
    triangles = vertices[faces]
    points = [vertices[vertices[:, 2] >= z]]
    for a, b in ((0, 1), (1, 2), (2, 0)):
        p, q = triangles[:, a], triangles[:, b]
        crosses = ((p[:, 2] < z) & (q[:, 2] > z)) | ((p[:, 2] > z) & (q[:, 2] < z))
        p, q = p[crosses], q[crosses]
        fraction = (z - p[:, 2]) / (q[:, 2] - p[:, 2])
        points.append(p + fraction[:, None] * (q - p))
    return np.vstack(points)


def ceiling_plan(scene, geometries):
    meshes = base.world_meshes(scene, geometries)
    pockets = []
    for name, group in (("asse", ("asse", "asse-inlet-tpu", "asse-outlet-tpu")),
                        ("regulator", ("reg",))):
        points = np.vstack([high_surface_points(*meshes[n], 345.0) for n in group])
        lo = np.floor(points.min(0) - 1)
        hi = np.ceil(points.max(0) + 1)
        highest = max(float(meshes[n][0][:, 2].max()) for n in group)
        pockets.append({"name": name, "xmin": float(lo[0]), "xmax": float(hi[0]),
                        "ymin": float(lo[1]), "ymax": float(hi[1]), "zmax": 352.0,
                        "bodies": list(group), "highest_body_z_mm": highest,
                        "minimum_roof_gap_mm": float(352 - highest)})
    return {"slab": {"xmin": -107.5, "xmax": 107.5, "ymin": 244.0, "ymax": 471.3,
                     "zmin": 346.0, "zmax": 355.0},
            "pockets": pockets, "minimum_stock_mm": 3.0}


def add_context(scene, geometries):
    path = HERE / "context.json"
    if not path.exists():
        return
    data = json.loads(path.read_text())
    scene["instances"].extend(copy.deepcopy(data["instances"]))
    scene["pins"].extend(copy.deepcopy(data.get("pins", [])))
    scene["mates"].extend(copy.deepcopy(data.get("mates", [])))
    inlet = scene["layout"]["asse_inlet_mouth_world_mm"]
    for m in scene["instances"]:
        if m["name"] == "water-in":
            m.update(geometry="straight-water-link", rotation=np.eye(3).tolist(), translation=inlet,
                     label="Water bulkhead to ASSE · straight tube · 32.125 mm visible")
    scene["mates"].extend([
        {"a": "water-in", "b": "asse-inlet-tpu", "point": inlet, "insertion_mm": 15.0},
        {"a": "water-in", "b": "bulkhead-water", "point": [inlet[0], 446.51, inlet[2]],
         "insertion_mm": 12.7, "insertion_basis": "layout estimate"},
    ])
    scene["layout"].update(visible_water_link_mm=446.51-inlet[1], pcb_bottom_clearance_mm=3.0)
    for name in ("right-wall", "back-wall", "left-wall"):
        if name in geometries:
            scene["instances"].append(base.instance(name, name, context=True, kind="component", role="structure",
                label={"right-wall": "9 mm wall · four PCB standoffs at existing mounting holes",
                       "back-wall": "9 mm back wall · bored for water bulkhead", "left-wall": "9 mm sidewall"}[name]))
    scene["mates"].extend([
        {"a": "pcba", "b": "right-wall", "connection": "Four existing M3 holes seat on straight standoff faces"},
        {"a": "bulkhead-water", "b": "back-wall", "connection": "Barrel through 17.44 mm hole; outboard flange seats on wall"},
        {"a": "bulkhead-nut", "b": "back-wall", "connection": "Estimated nut seats on inner wall"},
        {"a": "right-wall", "b": "back-wall", "connection": "Plain wall solids meet on their corner face"},
        {"a": "left-wall", "b": "back-wall", "connection": "Plain wall solids meet on their corner face"},
    ])


def measure(scene, geometries, plan, check=False):
    meshes = base.world_meshes(scene, geometries)
    header = [v for n, (v, f) in meshes.items() if n not in base.HANDOFFS
              and not next(m for m in scene["instances"] if m["name"] == n).get("context")]
    points = np.vstack(header)
    low, high = points.min(0), points.max(0)
    result = {"pump_joint_angle_degrees": ANGLE, "header_lowering_mm": scene["layout"]["rigid_header_lowering_mm"],
        "hardware_bounds_mm": [low.tolist(), high.tolist()], "hardware_width_mm": float(high[0] - low[0]),
        "highest_body_z_mm": float(high[2]), "ceiling_outer_z_mm": 355.0, "pocket_roof_z_mm": 352.0,
        "ceiling_stock_mm": 3.0, "highest_body_to_pocket_roof_gap_mm": float(352 - high[2]),
        "lowest_pump_elbow_above_core_mm": float(meshes["lower-pump-elbow"][0][:, 2].min() - CAP),
        "lowest_pump_elbow_point_mm": meshes["lower-pump-elbow"][0][np.argmin(meshes["lower-pump-elbow"][0][:, 2])].tolist(),
        "va_outlet_elbow_above_core_mm": float(meshes["va-outlet-elbow"][0][:, 2].min() - CAP),
        "pocket_roof_count": len(plan["pockets"])}
    if check:
        result["unrelated_body_interferences"] = base.interference(scene, geometries)
        result["body_gaps_mm"] = {n + "_to_pump": lower.surface_distance(meshes[n], meshes["pump"])
                                  for n in ("asse", "reg", "vk", "va")}
        result["foot_to_carbonator_elbow_mm"] = lower.surface_distance(meshes["pump-sliding-foot"], meshes["carbonator-fold"])
        if "pcba" in meshes:
            result["pcb_to_pump_mm"] = lower.surface_distance(meshes["pcba"], meshes["pump"])
            result["pcb_to_vk_mm"] = lower.surface_distance(meshes["pcba"], meshes["vk"])
            result["pcb_tail_to_wall_mm"] = 98.5 - float(meshes["pcba"][0][:, 0].max())
            v, f = meshes["pcba"]
            tail_faces = f[np.any(v[f, 0] > 90.26, axis=1)]
            result["pcb_tails_to_wall_and_posts_mm"] = lower.surface_distance((v, tail_faces), meshes["right-wall"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="Write the native ceiling plan before exporting its solid")
    args = parser.parse_args()
    geometries = library()
    scene = clocked(geometries)
    plan = ceiling_plan(scene, geometries)
    (HERE / "ceiling-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    if args.plan_only:
        print(json.dumps(plan, indent=2))
        return
    add_context(scene, geometries)
    if "ceiling" in geometries:
        scene["instances"].append(base.instance("ceiling", "ceiling", role="structure", kind="component",
            context=True, label="9 mm ceiling · two rectangular recesses retain 3 mm stock"))
    scene["metrics"] = measure(scene, geometries, plan, args.check)
    report = {"scope": "Current-size enclosure packing study; current plain cold-core cap, 9 mm walls and native recessed ceiling",
              "units": "mm", "layout": scene["layout"], "metrics": scene["metrics"],
              "instances": scene["instances"], "mates": scene["mates"], "ceiling_plan": plan}
    (HERE / "study.json").write_text(json.dumps(report, indent=2) + "\n")
    used = {m["geometry"] for m in scene["instances"]}
    packed = {n: base.pack(*geometries[n], 5200 if n == "pump" else 3600) for n in sorted(used)}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"space": water.SPACE, "ceiling_plan": plan,
        "geometries": packed, "variants": [scene]}, separators=(",", ":")))
    print(json.dumps(scene["metrics"], indent=2))


if __name__ == "__main__":
    main()
