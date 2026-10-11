"""Manual, question-specific geometry review; no load qualification or build gate."""
import hashlib
import importlib.util
import itertools
import json
import math
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


def assembly_shapes(stroke):
    assembly = jig.build_assembly(stroke=stroke)
    return {name: node.obj for name, node in assembly.objects.items()
            if node.obj is not None and hasattr(node.obj, "val")}


def main():
    printed = jig.build_parts(print_frame=True)
    part_results = [{"part": name, "valid_brep": shape.val().isValid(),
                     "solid_count": len(shape.solids().vals()), "bbox": jig._bbox(shape),
                     "volume_mm3": shape.val().Volume()}
                    for name, shape in printed.items()]
    intentional = {
        frozenset(("lldpe-tube", "lower-liner")): "Designed 0.1375 mm radial TPU grip interference",
        frozenset(("lldpe-tube", "upper-liner")): "Designed 0.1375 mm radial TPU grip interference",
        frozenset(("touch-flo-donor", "tpu-sealing-thimble")): "Expanded TPU overlaps nominal port before elastic compression; no deformation solution",
    }
    failure = []
    checked = 0
    shape_pairs = 0
    strokes = [i / 2 for i in range(41)]
    initial = assembly_shapes(0)
    def stationary(name):
        return name in ("base", "touch-flo-donor") or any(name.endswith(s) for s in (
            "/fixed-pad-envelope", "/fixed-jaw-schematic", "/rail-schematic"))
    for stroke in strokes:
        placed = {name: shape if stationary(name) else shape.translate((stroke, 0, 0))
                  for name, shape in initial.items()}
        boxes = {name: bounds(shape) for name, shape in placed.items()}
        for a, b in itertools.combinations(placed, 2):
            shape_pairs += 1
            # Factory schematic components meet each other by illustration,
            # and are not an exact CAD model of the manufacturer's assembly.
            if "/" in a and "/" in b and a.split("/")[0] == b.split("/")[0]:
                continue
            if frozenset((a, b)) in intentional or not overlap_bounds(boxes[a], boxes[b]):
                continue
            checked += 1
            volume = placed[a].intersect(placed[b]).val().Volume()
            if volume > 1e-5:
                failure.append({"stroke_mm": stroke, "parts": [a, b], "overlap_mm3": volume})
    base = jig.build_base()
    lower = jig.build_lower_jaw().translate((jig.CLAMP_FINAL_X, jig.TUBE_Y, jig.TUBE_Z))
    upper = jig.build_upper_jaw().translate((jig.CLAMP_FINAL_X, jig.TUBE_Y, jig.TUBE_Z))
    jaw = lower.union(upper)
    bearing = []
    for station in jig.clamp_stations():
        for role, solid, x, inward in (("fixed", base, jig.THRUST_WALL_X0, 1),
                                        ("moving", jaw, jig.CLAMP_BACK_X, -1)):
            y = station[f"{role}_center_mm"][1]
            slab = jig.cylinder_x(min(x, x + inward * 0.1), max(x, x + inward * 0.1),
                                  y, jig.TUBE_Z, jig.FACTORY_PAD_ENVELOPE_D / 2)
            missing = slab.cut(solid).val().Volume()
            bearing.append({"station": station["name"], "role": role,
                            "contact_center_mm": [x, y, jig.TUBE_Z],
                            "pad_envelope_diameter_mm": jig.FACTORY_PAD_ENVELOPE_D,
                            "missing_backing_mm3_in_0p1mm_slab": missing})
    gap = jig.RAIL_LATERAL_GAP
    span = jig.CARRIER_LENGTH
    lip_play = lambda stroke: gap * (1 + 2 * (jig.CARRIER_FINAL_X + stroke - jig.DONOR_PORT_X) / span)
    report = {
        "schema": 2,
        "scope": "Manual dimensional and B-rep fit review of twin screw-clamp fixture; schematic factory envelopes are not measured manufacturer CAD",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "reference_source_sha256": {str(p.relative_to(jig.REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                                    for p in (jig.DONOR_SOURCE, jig.SLEEVE_SOURCE)},
        "parts": part_results,
        "travel_review": {"stroke_range_mm": [0, jig.PRESS_TRAVEL], "increment_mm": 0.5,
                          "states": len(strokes), "pairwise_bounds_reviews": shape_pairs,
                          "brep_intersection_queries": checked, "unintended_intersections": failure,
                          "tube_length_mm": 330.0,
                          "included": "All printed rigid parts, reference donor, full tube, liners, thimble, four screws, four nuts, two washers, and schematic factory clamps",
                          "intentional_interference": [{"parts": sorted(p), "reason": r} for p, r in intentional.items()]},
        "factory_bearing_review": bearing,
        "location_and_grip": {
            "tube_axis_yz_mm": [jig.TUBE_Y, jig.TUBE_Z],
            "donor_round_base_tangent_floor_z_mm": jig.TUBE_Z - jig.DONOR_BODY_OD / 2,
            "donor_flat_clocking_pad_z_mm": jig.CLOCKING_PAD_Z1,
            "lower_jaw_shelf_z_mm": jig.TUBE_Z - jig.JAW_HALF_H,
            "guide_bearing_span_mm": span,
            "guide_lateral_gap_each_mm": gap,
            "carrier_foot_final_x_range_mm": [jig.CARRIER_FINAL_X, jig.CARRIER_FINAL_X + span],
            "carrier_foot_initial_x_range_mm": [jig.CARRIER_FINAL_X + jig.PRESS_TRAVEL,
                                                jig.CARRIER_FINAL_X + span + jig.PRESS_TRAVEL],
            "nominal_guide_only_lip_play_final_mm": lip_play(0),
            "nominal_guide_only_lip_play_initial_mm": lip_play(jig.PRESS_TRAVEL),
            "guide_play_scope": "Geometric free play with lower jaw metal-coupled without slip; not an interfering sleeve's measured working alignment allowance",
            "grip_bore_mm": jig.GRIP_BORE_D,
            "tube_od_mm": jig.TUBE_OD,
            "liner_grip_length_mm": jig.LINER_LENGTH,
            "jaw_pocket_front_end_wall_mm": jig.LINER_X0 - jig.JAW_LINER_AXIAL_CLEARANCE / 2,
            "jaw_pocket_rear_end_wall_mm": jig.JAW_LENGTH - jig.LINER_X0 - jig.LINER_LENGTH - jig.JAW_LINER_AXIAL_CLEARANCE / 2,
            "jaw_pocket_backing_mm": jig.JAW_BACK_H,
            "liner_minimum_backing_mm": jig.LINER_H - jig.GRIP_BORE_D / 2,
            "liner_end_contact_area_mm2": jig.LINER_WIDTH * jig.LINER_H - 0.5 * math.pi * (jig.GRIP_BORE_D / 2) ** 2,
            "carrier_countersink_retained_shelf_mm": jig.CARRIER_SHELF_H - jig.M5_CS_HEAD_H,
            "carrier_nut_floor_mm": jig.COUPLING_NUT_Z0 + jig.JAW_HALF_H,
            "carrier_screw_tip_z_mm": jig.CARRIER_BOTTOM_Z + jig.M5_CS_HEAD_RECESS + 20,
            "carrier_screw_tip_relief_mm": jig.TUBE_Z - (jig.CARRIER_BOTTOM_Z + jig.M5_CS_HEAD_RECESS + 20),
            "carrier_countersink_radial_stock_mm": jig.COUPLING_TOE_R - jig.M5_CS_HEAD_D / 2,
            "carrier_nut_z_range_mm": [jig.TUBE_Z + jig.COUPLING_NUT_Z0, jig.TUBE_Z + jig.COUPLING_NUT_Z0 + 4],
            "liner_print_pose": "Tube axis vertical; thick preformed half-round block; no bending or wrapping",
            "clamp_front_final_x_mm": jig.CLAMP_FINAL_X,
            "arch_axial_clearance_mm": jig.CLAMP_FINAL_X - jig.DONOR_ARCH_X,
            "factory_pad_to_shank_slot_near_clearance_mm": jig.SCREW_OFFSET_Y - jig.TUBE_Y - jig.SHANK_SLOT_D / 2 - jig.FACTORY_PAD_ENVELOPE_D / 2,
        },
        "setup": {
            "bore_depth": "Measure actual bare donor annular floor depth D with existing caliper; source records at least 20 mm",
            "lip_witness_from_tube_end_mm": "D - 2.1",
            "jaw_front_witness_from_tube_end_mm": "D + 16.9",
            "initial_manual_engagement_for_depth_over_20_mm": "D - 20 with T handle before carrier reaches rear stop",
            "stop_scope": "Geometric overtravel limit; no force holding, seating or leak-tightness rating",
            "factory_clamp_check": "On ordinary unloaded setup, both actual pads remain fully backed at stations and each spindle covers the full20mm stroke without manual sliding-jaw repositioning",
            "lever_check": "Attached faucet lever stays down at unpressed rest, untouched through the full ordinary unloaded movement; no measured rigid pose is inferred",
        },
        "evidence_limits": [
            "Insertion force, as-printed strength, grip, sliding fit and lifetime are unmeasured",
            "PET-GF15 manufacturer mechanical coupons were annealed120C16h; no published number is an as-printed allowable",
            "Manufacturer600lb clamp force does not rate the printed fixture, donor, tube or grip",
            "No assembled faucet lever pose is invented; a low narrow forward shelf and rearward full-width guides preserve front access",
            "Factory pads, rail, spindle and handles use schematic envelopes, requiring ordinary actual-tool setup",
            "The sleeve is fitted to tube first, with tube end on cap; the sleeved tube enters the bare donor",
        ],
    }
    out = HERE / "geometry-review.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(out), "states": len(strokes), "queries": checked,
                      "failures": failure, "bearing": bearing,
                      "parts": [{"part": p["part"], "valid": p["valid_brep"], "solids": p["solid_count"]} for p in part_results]}, indent=2))


if __name__ == "__main__":
    main()
