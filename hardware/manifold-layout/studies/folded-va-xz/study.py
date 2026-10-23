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


def pose(kind, geometries, check=False):
    scene = lower.spaced_regulator()
    scene.update(id=kind, title="Tighter fold" if kind == "tight" else "Raised outlet")
    outlet = np.array(next(j["point"] for j in scene["mates"] if {j["a"], j["b"]} == {"reg", "va"}))
    shoulder = -base.ED["stem_shoulder"][0][0]
    socket = base.ED["socket"][0][1]
    if kind == "tight":
        corner = outlet + [shoulder, 0, 0]
        inlet = corner - [0, 0, socket]
        rotation = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        male_host, female_host = "reg", "va"
    else:
        corner = outlet + [socket, 0, 0]
        inlet = corner - [0, 0, shoulder]
        rotation = np.array([[0, -1, 0], [0, 0, -1], [1, 0, 0]])
        male_host, female_host = "va", "reg"
    bottom = inlet - [0, 0, VALVE_LENGTH]
    scene["instances"] = [m for m in scene["instances"] if m["name"] not in base.HANDOFFS]
    for m in scene["instances"]:
        if m["name"] == "va":
            m.update(geometry="vk", rotation=np.eye(3).tolist(), translation=(inlet - VK_TOP).tolist(),
                     label="V-A · vertical ports, inlet above outlet, head −Y like V-K")
    scene["instances"].append(base.instance("reg-va-elbow", "stem-elbow-trimmed", corner, rotation,
        role="stem", kind="elbow", label="Regulator–V-A · one flush stem elbow · stem into " + male_host.upper()))
    names = {m["name"] for m in scene["instances"]}
    scene["mates"] = [j for j in scene["mates"] if j["a"] in names and j["b"] in names
                      and {j["a"], j["b"]} != {"reg", "va"}]
    for host, male in ((male_host, True), (female_host, False)):
        scene["mates"].append({"a": host, "b": "reg-va-elbow",
            "point": (outlet if host == "reg" else inlet).tolist(), "exposed_tube_mm": 0,
            "connection": "trimmed male stem into socket" if male else "female mouths meet on concealed tube",
            **({"insertion_mm": 12.7, "shoulder_gap_mm": 0} if male else {"concealed_tube_length_mm": 29.591}),
            "host_insertion_basis": "12.7 mm layout estimate; flush shoulders fix exterior pose"})
    local = base.world_meshes(scene, geometries)
    points = np.vstack([v for v, f in local.values()])
    lo, hi = points.min(0), points.max(0)
    width, height = float(hi[0] - lo[0]), float(hi[2] - lo[2])
    shift = np.array([-(lo[0] + hi[0]) / 2, 0, SPACE["world_core_plain_top_z_mm"] - lo[2]])
    metrics = {"local_bounds_mm": [lo.tolist(), hi.tolist()], "width_x_mm": width, "height_z_mm": height,
               "ideal_width_x_mm": SPACE["ideal_inner_x_span_mm"], "ideal_height_z_mm": SPACE["headroom_mm"],
               "centered_side_gap_mm": (SPACE["ideal_inner_x_span_mm"] - width) / 2,
               "ceiling_intrusion_mm": height - SPACE["headroom_mm"],
               "va_outlet_above_core_mm": float(bottom[2] - lo[2]),
               "group_translation_for_xz_comparison_mm": shift.tolist(),
               "placed_bounds_mm": [(lo + shift).tolist(), (hi + shift).tolist()],
               "highest_body": "asse", "lower_height_datum": "pump scanned foot plane"}
    metrics["body_ceiling_intrusions_mm"] = {
        n: float(v[:, 2].max() + shift[2] - SPACE["ideal_roof_underside_z_mm"])
        for n, (v, f) in local.items()
        if v[:, 2].max() + shift[2] > SPACE["ideal_roof_underside_z_mm"]}
    if check:
        metrics["unrelated_body_interferences"] = base.interference(scene, geometries)
        metrics["va_to_regulator_surface_gap_mm"] = lower.surface_distance(local["va"], local["reg"])
        metrics["va_to_pump_surface_gap_mm"] = lower.surface_distance(local["va"], local["pump"])
    scene["layout"].update(va_head_direction=[0, -1, 0], va_ports_axis=[0, 0, 1],
        va_inlet_local_mm=inlet.tolist(), va_outlet_local_mm=bottom.tolist(), reg_outlet_local_mm=outlet.tolist(),
        reg_va_elbow_male_host=male_host, reg_va_exposed_tube_mm=0,
        va_inlet_world_mm=(inlet + shift).tolist(), va_outlet_world_mm=(bottom + shift).tolist(),
        comparison_y_placement="unconstrained; no Y fit claim")
    for m in scene["instances"]:
        m["translation"] = (np.array(m["translation"]) + shift).tolist()
    for j in scene["mates"]:
        j["point"] = (np.array(j["point"]) + shift).tolist()
    placed = base.world_meshes(scene, geometries)
    scene["pins"] = []
    for name, text in (("asse", "ASSE 1022"), ("pump", "Pump"), ("vk", "V-K"),
                       ("reg", "Regulator"), ("va", "V-A")):
        v = placed[name][0]
        scene["pins"].append({"text": text, "at": ((v.min(0) + v.max(0)) / 2).tolist()})
    scene["arrows"] = []
    scene["metrics"] = metrics
    return scene


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = lower.library()
    scenes = [pose(k, geometries, args.check) for k in ("tight", "raised")]
    report = {"scope": SPACE["scope"], "units": "mm", "ideal_space": SPACE,
              "envelope": "Hardware, adapters and local joints up to external connection ports; arbitrary handoff stubs omitted",
              "placement": "Each variant centered in X; scanned pump foot plane on plain core cap; no mounting or assembly allowance",
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
