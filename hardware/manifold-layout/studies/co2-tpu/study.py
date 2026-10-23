"""Selected enclosure arrangement with threadless TPU gas joints.

The water group retains its fitting axes and original aft-facing valve heads.
The regular rear grid, cold-core gas handoff and low forward PCB remain explicit.
Run --check manually to query the selected installed meshes; no checks run on edits.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


parent = module("co2_grid_parent", HERE.parent / "co2-grid/study.py")
tpu = module("co2_tpu_joints", HERE / "tpu-joints/model.py")
base = parent.base
I = np.eye(3)
FORE = np.array([0., -7., 0.])
PCB_SHIFT = np.zeros(3)
GAS_R = np.diag([-1., -1., 1.])
GAS_INLET = parent.GAS_INLET.copy()
GAS_T = GAS_INLET - GAS_R @ np.array([0., -18.5, 0.])
OLD_GAS = {"wr1110", "gasher-co2", "co2-adapter-regulator-in",
           "co2-adapter-check-out", "co2-inlet-link", "co2-turn", "co2-core-drop"}


def source_scene(geometries):
    return parent.parent.pose(geometries)


def gas_ports():
    return tpu.direct_ports(GAS_R, GAS_T)


def drop_points():
    mouth = np.array(gas_ports()["outlet"]["point_mm"])
    cap = np.array(parent.gas.cap_handoff()["point_mm"])
    start, end = mouth - [0., 0., 10.], cap + [0., 0., 10.]
    t = np.linspace(0., 1., 33)
    curve = start + t[:, None] * (end - start)
    curve[:, 1] = start[1] + (t*t*(3.-2.*t)) * (end[1] - start[1])
    return np.vstack([mouth + [0., 0., 15.], mouth, start,
                      curve[1:-1], end, cap, cap - [0., 0., 12.]])


def library():
    result = parent.library()
    result.update(tpu.library())
    result.update(tpu.metal_library())
    for path in sorted((HERE / "parts").glob("*.npz")):
        with np.load(path) as data:
            result[path.stem] = data["v"], data["f"]
    source = source_scene(result)
    inlet = np.array(source["layout"]["asse_inlet_mouth_world_mm"]) + FORE
    result["tpu-water-link"] = parent.tube(
        [inlet - [0., 15., 0.], [parent.COLS[0], 446.51 + 12.7, parent.ROWS[0]]],
        3.175, 2.12,
    )
    result["tpu-inlet-link"] = parent.tube(
        [GAS_INLET + [0., 12.7, 0.], GAS_INLET - [0., 15., 0.]], 3.175, 2.12
    )
    result["tpu-core-drop"] = parent.tube(drop_points(), 3.175, 2.12)
    return result


def pose(geometries):
    scene = parent.pose(geometries)
    source = source_scene(geometries)
    originals = {m["name"]: m for m in source["instances"]}
    header = {m["name"] for m in source["instances"] if not m.get("context")}
    scene["instances"] = [m for m in scene["instances"] if m["name"] not in OLD_GAS]
    for m in scene["instances"]:
        name = m["name"]
        if name in header:
            original = originals[name]
            m.update(rotation=copy.deepcopy(original["rotation"]),
                     translation=(np.array(original["translation"]) + FORE).tolist())
            if name in ("vk", "va"):
                m["label"] = name.upper().replace("V", "V-") + " · original aft-facing head"
        if name == "pcba" or m.get("connection_owner") == "pcba":
            m["translation"] = (np.array(m["translation"]) + PCB_SHIFT).tolist()
        if name == "water-in":
            m.update(geometry="tpu-water-link", translation=[0., 0., 0.], rotation=I.tolist())
    # Restore source header mate datums with the same rigid translation.
    source_mates = {frozenset((m["a"], m["b"])): m for m in source["mates"]}
    for mate in scene["mates"]:
        pair = frozenset((mate["a"], mate["b"]))
        if mate["a"] in header and mate["b"] in header and pair in source_mates:
            original = source_mates[pair]
            if "point" in original:
                mate["point"] = (np.array(original["point"]) + FORE).tolist()
    scene["instances"].extend(tpu.direct_instances(GAS_R, GAS_T, include_metals=True))
    scene["instances"].extend([
        base.instance("co2-inlet-link", "tpu-inlet-link", role="gas", kind="tube", context=True,
                      label="CO₂ · concealed inlet tube between touching mouths"),
        base.instance("co2-core-drop", "tpu-core-drop", role="gas", kind="tube", context=True,
                      label="CO₂ · unresolved drop intersects V-K", route_status="unresolved"),
    ])
    scene["mates"].extend(tpu.mates())
    scene["mates"].extend([
        {"a": "co2-inlet-link", "b": "co2-inlet", "insertion_mm": 12.7},
        {"a": "co2-inlet-link", "b": "regulator-inlet-tpu", "insertion_mm": 15.0},
        {"a": "co2-core-drop", "b": "check-outlet-tpu", "insertion_mm": 15.0},
    ])
    names = {m["name"] for m in scene["instances"]}
    scene["mates"] = [m for m in scene["mates"] if m["a"] in names and m["b"] in names]
    inlet = np.array(source["layout"]["asse_inlet_mouth_world_mm"]) + FORE
    for mate in scene["mates"]:
        if {mate["a"], mate["b"]} == {"water-in", "asse-inlet-tpu"}:
            mate["point"] = inlet.tolist()
    labels = {"ASSE 1022", "Pump", "V-K", "Regulator", "V-A",
              "ASSE inlet → back wall", "To flavor manifold", "To carbonator"}
    header_pins = {p["text"]: p for p in source["pins"] if p["text"] in labels}
    for pin in scene["pins"]:
        if pin["text"] in header_pins:
            pin["at"] = (np.array(header_pins[pin["text"]]["at"]) + FORE).tolist()
        if pin["text"].startswith("PCB"):
            pin["at"] = (np.array(pin["at"]) + PCB_SHIFT).tolist()
        if pin["text"] == "CO₂ regulator + check":
            pin["text"] = "CO₂ · direct metal pair + TPU ends"
    scene["arrows"] = copy.deepcopy(source["arrows"])
    for arrow in scene["arrows"]:
        arrow["at"] = (np.array(arrow["at"]) + FORE).tolist()
    scene.update(id="co2-tpu", title="TPU gas joints · original valve heads")
    for key in ("va_inlet_world_mm", "va_outlet_world_mm", "flavor_mouth_world_mm",
                "asse_inlet_mouth_world_mm"):
        scene["layout"][key] = (np.array(source["layout"][key]) + FORE).tolist()
    scene["layout"].update(
        water_header_translation_from_pcb_low_fore_mm=FORE.tolist(),
        water_header_poses="Rigid group7mm fore; original valve head rotations and all fitting axes retained",
        va_head_direction=[0, 1, 0], vk_head_direction=[0, 1, 0],
        valve_clocking="Original aft-facing heads",
        pcb_inboard_translation_mm=PCB_SHIFT.tolist(),
        pcb_footprint_mm={"xmin": -72., "xmax": 0.800018310546875,
                          "ymin": 182., "ymax": 272.81605529785156},
        pcb_lead_dressing="PCB-low-fore local plug and lead models",
        co2_flow="Rear bulkhead → threadless TPU inlet cuff → WR regulator → directly threaded Gasher check → TPU90°outlet cuff → continuous tube to core",
        co2_datums={"inlet_mouth_mm": GAS_INLET.tolist(),
                    "outlet_mouth_mm": gas_ports()["outlet"]["point_mm"],
                    "core_guide_mm": parent.gas.cap_handoff()["point_mm"]},
        co2_route_status="Unresolved: the proposed drop to the fixed core guide intersects V-K",
        co2_clamps="Four9mm closed bands on the two metal cuffs and two tube sockets",
        context_scope="Selected water and CO2 assemblies, dry electronics with local leads, funnel/frame and native walls/roof; WAGOs deferred, V-B and reservoir routes set aside",
    )
    scene["layout"].pop("co2_inlet_thread_engagement_mm", None)
    return scene


def check(scene, geometries):
    import fcl
    meshes = base.world_meshes(scene, geometries)
    objects, bounds = {}, {}
    for name, (v, f) in meshes.items():
        model = fcl.BVHModel()
        model.beginModel(len(v), len(f))
        model.addSubModel(v, f.astype(np.int32))
        model.endModel()
        objects[name] = fcl.CollisionObject(model)
        bounds[name] = v.min(0), v.max(0)
    mates = {frozenset((m["a"], m["b"])) for m in scene["mates"]}
    for side in ("inlet", "outlet"):
        for band in ("barb", "tube"):
            mates.add(frozenset((f"pump-{side}-{band}-band", f"pump-{side}-tpu")))
    hits, names = [], list(meshes)
    for i, a in enumerate(names):
        lo, hi = bounds[a]
        for b in names[i+1:]:
            if frozenset((a, b)) in mates:
                continue
            low, high = bounds[b]
            if np.any(np.minimum(hi, high) - np.maximum(lo, low) < .001):
                continue
            if fcl.collide(objects[a], objects[b], fcl.CollisionRequest(), fcl.CollisionResult()):
                hits.append([a, b])
    def gap(a, b):
        return float(fcl.distance(objects[a], objects[b], fcl.DistanceRequest(), fcl.DistanceResult()))
    pairs = [("co2-core-drop", "vk"), ("co2-core-drop", "pump"),
             ("check-outlet-tpu", "vk"), ("pump", "pcba"),
             ("va-outlet-elbow", "pcba"), ("reg", "funnel"),
             ("reg", "ceiling"), ("asse", "ceiling"),
             ("regulator-inlet-band-cuff", "ceiling"),
             ("bulkhead-flavor-a-departure", "pump")]
    return {"scope": "All selected installed bodies, TPU joints and bands, tubes, local wires, bare nuts and native wall/roof context; intended mates excluded",
            "unrelated_interferences": hits,
            "selected_gaps_mm": {a + "_to_" + b: gap(a, b) for a, b in pairs},
            "minimum_ceiling_stock_mm": 3., "gas_pocket_stock_mm": 6.,
            "rear_fitting_mounting_stock_mm": 6.,
            "limits": "TPU metal cuffs, clamp occupancy and local tube dressing are estimates. Full onward soda/vent/flavor and complete wire routes are outside this selected arrangement."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = library()
    scene = pose(geometries)
    if args.check:
        scene["metrics"] = check(scene, geometries)
    (HERE / "study.json").write_text(json.dumps(scene, indent=2) + "\n")
    (HERE / "interfaces.json").write_text(json.dumps({
        "units": "mm", "grid": parent.grid(),
        "water_group_translation_mm": FORE.tolist(),
        "pcb_translation_from_pcb_low_fore_mm": PCB_SHIFT.tolist(),
        "J7_lead_geometry": "connection-J7-wire-edge",
        "gas_rotation": GAS_R.tolist(), "gas_regulator_translation_mm": GAS_T.tolist(),
        "gas": gas_ports(), "core_handoff": parent.gas.cap_handoff(),
        "gas_drop_status": "Unresolved: proposed centreline intersects V-K",
        "gas_drop_centerline_mm": drop_points().tolist(),
        "direct_metal_joint": tpu.interfaces()["direct_metal_joint"],
        "joint_geometry_source": "tpu-joints/interfaces.json",
    }, indent=2) + "\n")
    used = {m["geometry"] for m in scene["instances"]}
    packed = {n: base.pack(*geometries[n], 12000 if n.startswith("connection-")
                           else 8000 if n.endswith("-tpu") else 5200 if n == "pump" else 3600)
              for n in sorted(used)}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    space = parent.parent.parent.parent.water.SPACE
    (out / "viewer-data.json").write_text(json.dumps(
        {"space": space, "geometries": packed, "variants": [scene]}, separators=(",", ":")
    ))
    print(json.dumps(scene.get("metrics", {}), indent=2))


if __name__ == "__main__":
    main()
