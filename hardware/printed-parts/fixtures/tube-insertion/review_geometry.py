"""Manual review of the tube-insertion fixture's requested fit and full travel.

Run when answering this fixture's geometry question. This does not join a
build, watcher, hook or print-launch path, and supplies no physical load rating.
"""

import hashlib
import importlib.util
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "tube_insertion.py"
spec = importlib.util.spec_from_file_location("tube_insertion_review", SOURCE)
jig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jig)


def bounds(shape):
    b = shape.val().BoundingBox()
    return ((b.xmin, b.xmax), (b.ymin, b.ymax), (b.zmin, b.zmax))


def overlap_bounds(a, b):
    return all(min(hi_a, hi_b) - max(lo_a, lo_b) > 1e-6
               for (lo_a, hi_a), (lo_b, hi_b) in zip(a, b))


def main():
    parts = jig.build_parts()
    printed = jig.build_parts(print_frame=True)
    base = parts["base"]
    donor = jig.donor_shape()
    tube0 = jig.tube_shape(length=330.0)
    sleeve0 = jig.sleeve_on_tube_shape()
    pivot = {
        "pivot-bolt": jig.bolt_shape(jig.PRESS_PIVOT_X, jig.PRESS_PIVOT_Y, jig.PIVOT_COUNTERBORE_H),
        "pivot-washer": jig.washer_shape(jig.PRESS_PIVOT_X, jig.PRESS_PIVOT_Y,
                                          jig.PRESS_LEVER_Z0 + jig.PRESS_LEVER_H + 0.2),
    }
    wz = jig.PRESS_LEVER_Z0 + jig.PRESS_LEVER_H + 0.2
    for i in range(2):
        pivot[f"pivot-nut-{i + 1}"] = jig.square_nut_shape(jig.PRESS_PIVOT_X, jig.PRESS_PIVOT_Y,
                                                          wz + 1.5 + i * 4)
    static = {"base": base, "touch-flo-donor": donor, **pivot}
    moving0 = {
        "ram": parts["ram"].translate((jig.RAM_FINAL_X, jig.TUBE_Y, jig.RAM_BOTTOM_Z)),
        "lower-jaw": parts["lower-jaw"].translate((jig.CLAMP_FINAL_X, jig.TUBE_Y, jig.TUBE_Z)),
        "upper-jaw": parts["upper-jaw"].translate((jig.CLAMP_FINAL_X, jig.TUBE_Y, jig.TUBE_Z)),
        "lower-liner": parts["liner"].translate((jig.CLAMP_FINAL_X + jig.LINER_X0,
                                                  jig.TUBE_Y, jig.TUBE_Z - jig.LINER_H)),
        "upper-liner": parts["liner"].mirror("XY").translate((jig.CLAMP_FINAL_X + jig.LINER_X0,
                                                                jig.TUBE_Y, jig.TUBE_Z + jig.LINER_H)),
        "lldpe-tube": tube0,
        "sealing-thimble": sleeve0,
    }
    for side, label in ((-1, "front"), (1, "rear")):
        x, y = jig.CLAMP_FINAL_X + jig.CLAMP_BOLT_X, jig.TUBE_Y + side * jig.CLAMP_BOLT_Y
        wz = jig.TUBE_Z + jig.JAW_HALF_H
        moving0[f"clamp-{label}-bolt"] = jig.bolt_shape(x, y, jig.TUBE_Z - jig.JAW_HALF_H)
        moving0[f"clamp-{label}-washer"] = jig.washer_shape(x, y, wz)
        moving0[f"clamp-{label}-nut"] = jig.square_nut_shape(x, y, wz + 1.5)
    intentional = {
        frozenset(("lldpe-tube", "lower-liner")): "Designed 0.1375 mm radial TPU grip interference",
        frozenset(("lldpe-tube", "upper-liner")): "Designed 0.1375 mm radial TPU grip interference",
        frozenset(("touch-flo-donor", "sealing-thimble")): "Nominal expanded TPU overlaps the port before elastic compression; no deformation solution",
    }
    failure = []
    checked = 0
    shape_pairs = 0
    strokes = [i / 2 for i in range(41)]
    for stroke in strokes:
        placed = dict(static)
        placed.update({name: shape.translate((stroke, 0, 0)) for name, shape in moving0.items()})
        placed["press-lever"] = parts["press-lever"].rotate(
            (0, 0, 0), (0, 0, 1), jig.press_angle(stroke)).translate(
                (jig.PRESS_PIVOT_X, jig.PRESS_PIVOT_Y, jig.PRESS_LEVER_Z0))
        boxes = {name: bounds(shape) for name, shape in placed.items()}
        for a, b in itertools.combinations(placed, 2):
            shape_pairs += 1
            if frozenset((a, b)) in intentional or not overlap_bounds(boxes[a], boxes[b]):
                continue
            checked += 1
            volume = placed[a].intersect(placed[b]).val().Volume()
            if volume > 1e-5:
                failure.append({"stroke_mm": stroke, "parts": [a, b], "overlap_mm3": volume})
    part_results = []
    for name, shape in printed.items():
        part_results.append({"part": name, "valid_brep": shape.val().isValid(),
                             "solid_count": len(shape.solids().vals()), "bbox": jig._bbox(shape),
                             "volume_mm3": shape.val().Volume()})
    report = {
        "schema": 1,
        "scope": "Manual dimensional and B-rep fit review of the requested tube-insertion tool",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "reference_source_sha256": {
            str(p.relative_to(jig.REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (jig.DONOR_SOURCE, jig.SLEEVE_SOURCE)},
        "parts": part_results,
        "travel_review": {
            "stroke_range_mm": [0, jig.PRESS_TRAVEL], "increment_mm": 0.5,
            "states": len(strokes), "pairwise_bounds_reviews": shape_pairs,
            "brep_intersection_queries": checked, "unintended_intersections": failure,
            "tube_length_mm": 330.0,
            "included": "All rigid parts, donor, 330 mm tube, liners, thimble, three screws, four nuts and three washers",
            "intentional_interference": [{"parts": sorted(pair), "reason": reason}
                                           for pair, reason in intentional.items()],
        },
        "location_and_grip": {
            "tube_axis_yz_mm": [jig.TUBE_Y, jig.TUBE_Z],
            "donor_round_base_tangent_floor_z_mm": jig.TUBE_Z - jig.DONOR_BODY_OD / 2,
            "donor_flat_clocking_pad_z_mm": jig.CLOCKING_PAD_Z1,
            "lower_jaw_supported_shelf_z_mm": jig.TUBE_Z - jig.JAW_HALF_H,
            "guide_bearing_span_mm": jig.RAM_FOOT_LENGTH,
            "guide_lateral_gap_each_mm": jig.RAIL_LATERAL_GAP,
            "grip_bore_mm": jig.GRIP_BORE_D, "tube_od_mm": jig.TUBE_OD,
            "nominal_diameter_reduction_percent": (1 - jig.GRIP_BORE_D / jig.TUBE_OD) * 100,
            "liner_grip_length_mm": jig.LINER_LENGTH,
            "jaw_pocket_front_end_wall_mm": jig.LINER_X0 - jig.JAW_LINER_AXIAL_CLEARANCE / 2,
            "jaw_pocket_rear_end_wall_mm": jig.JAW_LENGTH - jig.LINER_X0 - jig.LINER_LENGTH - jig.JAW_LINER_AXIAL_CLEARANCE / 2,
            "jaw_pocket_backing_mm": jig.JAW_BACK_H,
            "liner_minimum_backing_mm": jig.LINER_H - jig.GRIP_BORE_D / 2,
            "liner_end_contact_area_mm2": jig.LINER_WIDTH * jig.LINER_H - 0.5 * 3.141592653589793 * (jig.GRIP_BORE_D / 2) ** 2,
            "liner_print_pose": "Tube axis vertical; thick premolded half-round block, no bending or wrapping",
            "clamp_front_final_x_mm": jig.CLAMP_FINAL_X,
            "arch_axial_clearance_mm": jig.CLAMP_FINAL_X - jig.DONOR_ARCH_X,
            "bare_tube_to_rigid_jaw_radial_clearance_mm": (jig.JAW_TUBE_CLEARANCE_D - jig.TUBE_OD) / 2,
            "tube_to_ram_open_slot_each_side_mm": jig.RAM_GROOVE_HALF - jig.TUBE_OD / 2,
            "bolt_head_to_stop_vertical_clearance_mm": jig.TUBE_Z - jig.JAW_HALF_H - jig.M5_HEAD_H - jig.STOP_Z1,
            "jaw_bottom_to_guide_top_clearance_mm": jig.TUBE_Z - jig.JAW_HALF_H - jig.BASE_H - jig.RAIL_HEIGHT,
        },
        "setup": {
            "bore_depth": "Measure actual annular floor depth D in the bare donor with the existing caliper; source records at least 20 mm",
            "lip_witness_from_tube_end_mm": "D - 2.1",
            "jaw_front_witness_from_tube_end_mm": "D + 16.9",
            "initial_manual_engagement_for_depth_over_20_mm": "D - 20, with the T handle, before the collar fits the ram at the rear start stop",
            "stop_scope": "Geometric overtravel limit; sleeve cap compression, grip, full seating and leak tightness require physical assembly observations",
        },
        "evidence_limits": [
            "Print and physical grip unqualified; no load capacity or lifetime is established",
            "The accepted faucet lever has no measured assembled rigid pose; its down unpressed rest position is the user's operating authority",
            "The fixture leaves the original front side open and locates only the donor's metal base and lower column; it does not model a fabricated faucet-lever pose",
            "B-rep travel samples do not establish fit after printing or continuous contact mechanics",
            "The sleeve is fitted to the tube first, with tube end on sleeve cap; the sleeved tube enters the bare donor",
        ],
    }
    out = HERE / "geometry-review.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(out), "states": len(strokes), "intersections": checked,
                      "failures": failure,
                      "parts": [{"part": item["part"], "valid": item["valid_brep"], "solids": item["solid_count"]}
                                for item in part_results]}, indent=2))


if __name__ == "__main__":
    main()
