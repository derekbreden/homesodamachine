"""Fold V-A like V-K; compare the connected group with plain 9 mm X/Z bounds.

Mesh-only arrangement study. Production parts, mounts and placements are not
modified. Run --check to ask about unrelated-body intersections and body gaps.
"""
from pathlib import Path
import argparse
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("lowered_vk", HERE.parent / "lowered-vk/study.py")
lower = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lower)
base = lower.base
SPACE = json.loads((HERE / "ideal-space.json").read_text())
# The benchmark V-K top mouth is the datum for its scanned valve geometry.
VK_TOP = np.array([-4.916132605004726, 0, 78])
VALVE_LENGTH = 59.5
TO_ENCLOSURE = np.diag([-1, -1, 1])


def library():
    import trimesh
    result = lower.library()
    # A direction stub terminates at the cap face. The complete parent stub is
    # retained separately for the foot/path clearance question.
    parent = lower.spaced_regulator()
    meshes = base.world_meshes(parent, result)
    depth = float(meshes["check-carbonator"][0][:, 2].max() - meshes["pump"][0][:, 2].min())
    v, f = result["check-carbonator"]
    v = v.copy()
    top = v[:, 2].max()
    v[:, 2] = top + (v[:, 2] - top) * depth / np.ptp(v[:, 2])
    result["carbonator-to-cap"] = (v, f)
    tube = trimesh.creation.annulus(r_min=2.12, r_max=3.175, height=36.891, sections=32)
    rotation = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
    result["flavor-handoff"] = (tube.vertices @ rotation.T + [0, 1.5545, 0], tube.faces)
    return result


def pose(geometries, check=False):
    scene = lower.spaced_regulator()
    scene.update(id="raised", title="V-A raised · back wall identified")
    outlet = np.array(next(j["point"] for j in scene["mates"] if {j["a"], j["b"]} == {"reg", "va"}))
    shoulder = -base.ED["stem_shoulder"][0][0]
    socket = base.ED["socket"][0][1]
    corner = outlet + [socket, 0, 0]
    inlet = corner - [0, 0, shoulder]
    rotation = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
    male_host, female_host = "va", "reg"
    bottom = inlet - [0, 0, VALVE_LENGTH]
    scene["instances"] = [m for m in scene["instances"] if m["name"] not in base.HANDOFFS - {"check-carbonator", "water-in"}]
    for m in scene["instances"]:
        if m["name"] == "pump-sliding-foot":
            m["translation"] = (np.array(m["translation"]) + [0, -30, 0]).tolist()
            m["label"] = "Discharge-side rear rubber slider · reference position on its rail"
        if m["name"] == "check-carbonator":
            m.update(geometry="carbonator-to-cap", label="To carbonator · direction stub to cap face")
        if m["name"] == "water-in":
            m.update(role="carbonator", label="Water supply · ASSE inlet points aft to +Y back wall")
        if m["name"] == "va":
            m.update(geometry="vk", rotation=np.eye(3).tolist(), translation=(inlet - VK_TOP).tolist(),
                     label="V-A · vertical ports, inlet above outlet, head aft like V-K")
    scene["instances"].append(base.instance("reg-va-elbow", "stem-elbow-trimmed", corner, rotation,
        role="stem", kind="elbow", label="Regulator–V-A · one flush stem elbow · stem into " + male_host.upper()))
    outlet_corner = bottom - [0, 0, shoulder]
    flavor_mouth = outlet_corner + [0, socket, 0]
    scene["instances"].extend([
        base.instance("va-outlet-elbow", "stem-elbow-trimmed", outlet_corner,
            np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]]), role="stem", kind="elbow",
            label="V-A outlet elbow · forward toward flavor manifold, clear above cap"),
        base.instance("va-flavor", "flavor-handoff", flavor_mouth, role="flavor", kind="tube",
            label="To flavor manifold · forward −Y · direction stub"),
    ])
    names = {m["name"] for m in scene["instances"]}
    scene["mates"] = [j for j in scene["mates"] if j["a"] in names and j["b"] in names
                      and {j["a"], j["b"]} != {"reg", "va"}]
    for host, male in ((male_host, True), (female_host, False)):
        scene["mates"].append({"a": host, "b": "reg-va-elbow",
            "point": (outlet if host == "reg" else inlet).tolist(), "exposed_tube_mm": 0,
            "connection": "trimmed male stem into socket" if male else "female mouths meet on concealed tube",
            **({"insertion_mm": 12.7, "shoulder_gap_mm": 0} if male else {"concealed_tube_length_mm": 29.591}),
            "host_insertion_basis": "12.7 mm layout estimate; flush shoulders fix exterior pose"})
    scene["mates"].extend([
        {"a": "va", "b": "va-outlet-elbow", "point": bottom.tolist(),
         "connection": "trimmed male stem into valve outlet", "insertion_mm": 12.7,
         "shoulder_gap_mm": 0, "exposed_tube_mm": 0},
        {"a": "va-outlet-elbow", "b": "va-flavor", "point": flavor_mouth.tolist(),
         "connection": "tube in NeoFit socket", "insertion_mm": 16.891},
    ])
    local = base.world_meshes(scene, geometries)
    points = np.vstack([v for n, (v, f) in local.items() if n not in base.HANDOFFS])
    lo, hi = points.min(0), points.max(0)
    width, height = float(hi[0] - lo[0]), float(hi[2] - lo[2])
    oriented = points @ TO_ENCLOSURE.T
    rlo, rhi = oriented.min(0), oriented.max(0)
    shift = np.array([-(rlo[0] + rhi[0]) / 2,
                      SPACE["back_wall_reference_inner_y_mm"] - 10 - rhi[1],
                      SPACE["world_core_plain_top_z_mm"] - rlo[2]])
    def world(p):
        return (TO_ENCLOSURE @ p + shift).tolist()
    metrics = {"local_bounds_mm": [lo.tolist(), hi.tolist()], "width_x_mm": width, "height_z_mm": height,
               "ideal_width_x_mm": SPACE["ideal_inner_x_span_mm"], "ideal_height_z_mm": SPACE["headroom_mm"],
               "centered_side_gap_mm": (SPACE["ideal_inner_x_span_mm"] - width) / 2,
               "ceiling_intrusion_mm": height - SPACE["headroom_mm"],
               "va_outlet_above_core_mm": float(bottom[2] - lo[2]),
               "local_to_enclosure_rotation": TO_ENCLOSURE.tolist(),
               "local_to_enclosure_translation_mm": shift.tolist(),
               "placed_bounds_mm": [(rlo + shift).tolist(), (rhi + shift).tolist()],
               "va_outlet_elbow_above_core_mm": float(local["va-outlet-elbow"][0][:, 2].min() - lo[2]),
               "highest_body": "asse", "lower_height_datum": "pump scanned foot plane"}
    metrics["body_ceiling_intrusions_mm"] = {
        n: float(v[:, 2].max() + shift[2] - SPACE["ideal_roof_underside_z_mm"])
        for n, (v, f) in local.items()
        if v[:, 2].max() + shift[2] > SPACE["ideal_roof_underside_z_mm"]}
    if check:
        metrics["unrelated_body_interferences"] = base.interference(scene, geometries)
        metrics["va_to_regulator_surface_gap_mm"] = lower.surface_distance(local["va"], local["reg"])
        metrics["va_to_pump_surface_gap_mm"] = lower.surface_distance(local["va"], local["pump"])
        metrics["foot_to_carbonator_elbow_gap_mm"] = lower.surface_distance(local["pump-sliding-foot"], local["carbonator-fold"])
        # Ask about the full 24 mm continuation as well as the visible short
        # stub. The restored foot and this path also have disjoint Y bounds.
        parent = lower.spaced_regulator()
        full_stub = base.world_meshes(parent, geometries)["check-carbonator"]
        metrics["foot_to_carbonator_24mm_path_gap_mm"] = lower.surface_distance(local["pump-sliding-foot"], full_stub)
    scene["layout"] = dict(parent_local_layout=scene["layout"],
        va_head_direction=[0, 1, 0], vk_head_direction=[0, 1, 0], va_ports_axis=[0, 0, 1],
        va_inlet_local_mm=inlet.tolist(), va_outlet_local_mm=bottom.tolist(), reg_outlet_local_mm=outlet.tolist(),
        reg_va_elbow_male_host=male_host, reg_va_exposed_tube_mm=0,
        va_inlet_world_mm=world(inlet), va_outlet_world_mm=world(bottom), flavor_mouth_world_mm=world(flavor_mouth),
        flavor_handoff_direction_world=[0, -1, 0], asse_inlet_direction_world=[0, 1, 0],
        sliding_foot_translation_from_benchmark_mm=[0, -30, 0],
        comparison_y_placement="Rear wall gives orientation; illustrative 10 mm rear-body gap; no complete Y fit claim")
    for m in scene["instances"]:
        m["translation"] = world(m["translation"])
        m["rotation"] = (TO_ENCLOSURE @ m["rotation"]).tolist()
        if m["name"] == "vk":
            m["label"] = "V-K · vertical ports, head aft like V-A"
        if m["name"] == "pump":
            m["label"] = "G Ganen pump · discharge −X, motor toward back wall +Y"
    for j in scene["mates"]:
        j["point"] = world(j["point"])
    placed = base.world_meshes(scene, geometries)
    scene["pins"] = []
    for name, text in (("asse", "ASSE 1022"), ("pump", "Pump"), ("vk", "V-K"),
                       ("reg", "Regulator"), ("va", "V-A")):
        v = placed[name][0]
        scene["pins"].append({"text": text, "at": ((v.min(0) + v.max(0)) / 2).tolist()})
    inlet_mesh = placed["asse-inlet-tpu"][0]
    inlet_mouth = [(inlet_mesh[:, 0].min() + inlet_mesh[:, 0].max()) / 2,
                   inlet_mesh[:, 1].max(), (inlet_mesh[:, 2].min() + inlet_mesh[:, 2].max()) / 2]
    scene["layout"]["asse_inlet_mouth_world_mm"] = inlet_mouth
    scene["pins"].extend([
        {"text": "ASSE inlet → back wall", "short": "Inlet → back", "at": (np.array(inlet_mouth) + [0, 20, 0]).tolist()},
        {"text": "To flavor manifold", "short": "Flavor", "at": world(flavor_mouth + [0, 20, 0])},
        {"text": "To carbonator", "short": "Carbonator", "at": placed["check-carbonator"][0].mean(0).tolist()},
    ])
    scene["arrows"] = [{"at": inlet_mouth, "dir": [0, 1, 0], "role": "carbonator", "length": 28},
                       {"at": world(flavor_mouth + [0, 20, 0]), "dir": [0, -1, 0], "role": "flavor", "length": 10}]
    for key in ("tee_center_mm", "asse_translation_mm", "flavor_translation_mm"):
        scene.pop(key, None)
    scene["metrics"] = metrics
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = library()
    scenes = [pose(geometries, args.check)]
    report = {"scope": SPACE["scope"], "units": "mm", "ideal_space": SPACE,
              "envelope": "Hardware, adapters and local joints, including V-A outlet elbow; external handoff stubs excluded",
              "placement": "Whole group registered to enclosure with ASSE inlet +Y; centered in X, pump foot plane on plain cap; rear wall for orientation only",
              "variants": {s["id"]: {k: s[k] for k in ("title", "layout", "metrics", "mates", "instances")} for s in scenes}}
    (HERE / "study.json").write_text(json.dumps(report, indent=2) + "\n")
    used = {m["geometry"] for s in scenes for m in s["instances"]}
    packed = {n: base.pack(*geometries[n], 5200 if n == "pump" else 3600) for n in sorted(used)}
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"space": SPACE, "geometries": packed, "variants": scenes}, separators=(",", ":")))
    print(json.dumps({s["id"]: s["metrics"] for s in scenes}, indent=2))


if __name__ == "__main__":
    main()
