"""One-off design review; nothing in the machine build invokes this file.

Read the exported machine, try two explicitly provisional socket placements,
and evaluate a compact bundle transition. No production geometry is changed.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "hardware").is_dir())
sys.path[:0] = [str(BASE), str(ROOT / "hardware/scripts")]
import umbilical as u
from _cadq_export import import_assembly

FOAM_R = 12.7
FAN_LENGTH = 65.0
PACK_X = 5.5
PACK_Z = math.sqrt((FOAM_R + 6.35 / 2) ** 2 - PACK_X ** 2)
SODA_X, SODA_Z, _ = u.PORTS["soda"]
PACK = {
    "soda": (SODA_X, SODA_Z),
    "flavor-a": (SODA_X - PACK_X, SODA_Z + PACK_Z),
    "flavor-b": (SODA_X + PACK_X, SODA_Z + PACK_Z),
    "drain": (SODA_X, SODA_Z + FOAM_R + 2.0),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transition(name, t):
    x, z, _ = u.PORTS[name]
    px, pz = PACK[name]
    s = 10 * t ** 3 - 15 * t ** 4 + 6 * t ** 5
    return (x + (px - x) * s, -u.PLUG_L - FAN_LENGTH * t,
            z + (pz - z) * s)


def bundle_review():
    old_d = math.hypot(2 * u.H, 2 * u.H) + FOAM_R + 6.35 / 2
    c = ((FOAM_R + 6.35 / 2) ** 2 - (FOAM_R - 6.35 / 2) ** 2) / (
        2 * (PACK_Z + FOAM_R - 6.35 / 2))
    radius = FOAM_R + c
    curves = {}
    for name in PACK:
        x, z, od = u.PORTS[name]
        px, pz = PACK[name]
        delta = math.hypot(px - x, pz - z)
        ks = []
        for i in range(2001):
            t = i / 2000
            ds = 30 * t ** 2 - 60 * t ** 3 + 30 * t ** 4
            dds = 60 * t - 180 * t ** 2 + 120 * t ** 3
            ks.append(FAN_LENGTH * delta * abs(dds) /
                      (FAN_LENGTH ** 2 + delta ** 2 * ds ** 2) ** 1.5)
        curves[name] = {"offset_mm": delta,
                        "minimum_centerline_radius_mm": 1 / max(ks) if max(ks) else None,
                        "manufacturer_minimum_radius_mm": 25.0 if od < 5 else 25.4}
    circles = {n: (*PACK[n], 12.7 if n == "soda" else u.PORTS[n][2] / 2)
               for n in PACK}
    bounds = {n: math.hypot(x - SODA_X, z - SODA_Z - c) + r
              for n, (x, z, r) in circles.items()}
    return {
        "counter_hole_mm": u.COUNTER_HOLE,
        "straight_foam_at_plug_pair_diameter_lower_bound_mm": old_d,
        "proposed_pack_axes_xz_mm": PACK,
        "bare_pack_enclosing_diameter_mm": 2 * max(bounds.values()),
        "braid_and_cable_radial_allowance_mm": 1.3,
        "proposed_outer_envelope_mm": 2 * (max(bounds.values()) + 1.3),
        "nominal_radial_hole_margin_mm": u.COUNTER_HOLE / 2 - max(bounds.values()) - 1.3,
        "fan_length_mm": FAN_LENGTH,
        "foam_start_behind_plug_face_mm": u.PLUG_L + FAN_LENGTH,
        "curves": curves,
        "scope": "Uncompressed nominal geometric candidate. The founder reports the purchased foam is quite compressible and intends compression in the boot. Neither compressed shape nor passage is predicted here. Direct packing with deliberate compression is the first tactile candidate; the fan is an alternative. This is not a finished strain-relief design.",
    }


def bounds(s):
    b = s.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def overlapping(a, b):
    return all(min(a[i + 3], b[i + 3]) - max(a[i], b[i]) > 1e-5 for i in range(3))


def retainer_review():
    r, f = u.BODY_R - .5, u.BODY_F - .5
    _, _, xf = u.profile_corners(r, f)
    radius = max(r, math.hypot(xf, f)) + .001
    stock = u.profile(r, f, u.REAR, u.REAR + u.RETAINER_T)
    circle = u.cyl(2 * radius, u.REAR, u.REAR + u.RETAINER_T)
    return {"round_blank_diameter_mm": 2 * radius,
            "original_blank_width_height_mm": [2 * r, 2 * f],
            "width_height_increase_mm": [2 * radius - 2 * r, 2 * radius - 2 * f],
            "original_outer_outline_edges": len(u.profile_wire(r, f, u.REAR).Edges()),
            "round_outer_outline_edges": 1,
            "existing_blank_stock_removed_mm3": stock.cut(circle).Volume(),
            "scope": "Simpler perimeter candidate preserving all original blank stock. No functional retainer is replaced, and surrounding clearance remains a separate design question."}


def placement_review():
    step = ROOT / "hardware/manifold-layout/enclosure-assembly.step"
    facts_path = step.with_suffix(".facts.json")
    facts = json.loads(facts_path.read_text())
    native = import_assembly(step)
    rear_face = max(facts["bodies"]["bulkhead-ring-water"][4],
                    facts["bodies"]["bulkhead-ring-carb"][4])
    x = sum((facts["bodies"][n][0] + facts["bodies"][n][3]) / 2
            for n in ("bulkhead-flavor-a", "bulkhead-flavor-b")) / 2
    mid_z = sum((facts["bodies"][n][2] + facts["bodies"][n][5]) / 2
                for n in ("bulkhead-flavor-a", "bulkhead-carb")) / 2
    # Components replaced by a consolidated connection, rather than obstacles.
    removed = ("bulkhead-carb", "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-drain",
               "bulkhead-ring-carb", "bulkhead-ring-flavor-a", "bulkhead-ring-flavor-b",
               "bulkhead-ring-drain", "keystone-jack", "data-ring")
    assembly = u.socket().fuse(u.retainer()).clean()
    placements = []
    for name, z in (("existing_connection_field_center", mid_z),
                    ("raised_in_same_connection_lane", 326.5)):
        loc = u.cq.Location(u.cq.Vector(x, rear_face + u.FACE, z),
                            u.cq.Vector(0, 0, 1), 180)
        placed = assembly.moved(loc)
        pb = bounds(placed)
        collisions = []
        for n, (s, _color) in native.items():
            if n.startswith("enclosure-") or any(n == r or n.startswith(r + "-") for r in removed):
                continue
            if not overlapping(pb, bounds(s)):
                continue
            v = placed.intersect(s).Volume()
            if v > .01:
                collisions.append({"body": n, "intersection_mm3": round(v, 3)})
        placements.append({"name": name, "wall_center_xz_mm": [x, z],
                           "world_bounds_mm": pb, "native_intersections": collisions})
    return {
        "step": str(step.relative_to(ROOT)), "step_sha256": sha(step),
        "facts_sha256": sha(facts_path), "placements": placements,
        "scope": "Two trial locations, not an exhaustive placement search. Existing rear wall and enclosure supports are excluded because their openings would be redesigned. Replaced umbilical fittings and signal jack are excluded. Intersections are real native solid intersections; changing routes may resolve tube collisions. This does not authorize or implement any enclosure change.",
    }


def main():
    print("Reading native machine and testing two locations", flush=True)
    r = {"reviewed_local_date": "2026-10-09", "umbilical_source_sha256": sha(BASE / "umbilical.py"),
         "reviewer_sha256": sha(Path(__file__)), "bundle": bundle_review(),
         "retainer": retainer_review(), "machine": placement_review(),
         "magnet_rail": {"rail_height_mm": u.RAIL_H,
                         "nominal_groove_height_mm": 1.6002,
                         "drawing_groove_tolerance_mm": .010 * 25.4,
                         "minimum_groove_height_mm": (.063 - .010) * 25.4,
                         "minimum_groove_minus_rail_mm": (.063 - .010) * 25.4 - u.RAIL_H,
                         "scope": "Supplier drawing tolerance, excluding print error and groove-position tolerance. A nominal 1.5 mm rail does not fit every permitted groove."}}
    (HERE / "geometry-review.json").write_text(json.dumps(r, indent=2) + "\n")
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
