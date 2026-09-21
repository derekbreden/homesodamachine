"""Integral external spring-sleeve study against the matched archived fixture.

No production source is imported or modified. These are native geometry and
assembly-path checks, not a production release or force/stiffness qualification.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
INPUTS = STUDY / "inputs"
BASELINE = json.loads((INPUTS / "carrier-interface-baseline.json").read_text())
I = BASELINE["interface"]
S = BASELINE["spec"]
CURRENT = json.loads((STUDY / "current-interface-reference.json").read_text())["carrier_interface"]
X, Z = I["spring_stations"][1]["x"], I["spring_stations"][1]["z"]
FLOOR = I["fixed_seat_floor_y"]
MOVING_FLOOR = I["spring_stations"][1]["bore_floor_y"]
MOUTH = I["spring_bore_mouth_y"]
BORE_DEPTH = I["spring_bore_depth"]
SPRING_OD, SPRING_FREE = 6.0, 27.0
SLEEVE_ID, SLEEVE_WALL, PROJECTION = 6.57, 1.30, 19.0
SLEEVE_OD = SLEEVE_ID + 2 * SLEEVE_WALL
MOVING_ID = SLEEVE_OD + 0.50
RADIAL_AIR = (MOVING_ID - SLEEVE_OD) / 2
TOL = 1e-5


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def box(xs, ys, zs):
    return cq.Solid.makeBox(xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0],
                            cq.Vector(xs[0], ys[0], zs[0]))


def ycyl(diameter, y0, y1):
    return cq.Solid.makeCylinder(diameter/2, y1-y0,
                                cq.Vector(0, y0, 0), cq.Vector(0, 1, 0))


def along_y(points, y0, y1):
    plane = cq.Plane(origin=(0, y0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    return cq.Workplane(plane).polyline(points).close().extrude(y0-y1).val()


def place(shape, side):
    right = shape.translate((X, 0, Z))
    return right if side > 0 else right.mirror("YZ")


def window_fill():
    # Fill the complete existing lateral loading cut. The larger circular
    # receiver is then cut through both the original bar and this added stock.
    r = I["spring_bore_d"] / 2
    u = S["grip_back_x"] - X
    return along_y(((u, -r), (0, -r), (0, r), (u, r-u)),
                   MOUTH, I["spring_window_y"][1])


def bounds(shape):
    if not shape.Solids() or shape.Volume() < TOL:
        return None
    b = shape.BoundingBox()
    return {axis: [getattr(b, axis+"min"), getattr(b, axis+"max")]
            for axis in "xyz"}


def main():
    manifest = json.loads((STUDY / "input-manifest.json").read_text())
    for name, row in manifest.items():
        assert sha(STUDY / row["frozen_path"]) == row["source_sha256"], name
    native = {name: cq.importers.importStep(str(INPUTS / f"{name}.step")).val()
              for name in ("front_top", "cartridge", "cap", "left", "right")}
    sleeve = ycyl(SLEEVE_OD, FLOOR-.10, FLOOR+PROJECTION).cut(
        ycyl(SLEEVE_ID, FLOOR-.11, FLOOR+PROJECTION+.01)).clean()
    sleeves = {side: place(sleeve, side) for side in (-1, 1)}
    receiver_cut = ycyl(MOVING_ID, MOUTH-.10, MOVING_FLOOR)
    rim_relief = ycyl(MOVING_ID, I["grip_rim_y"][0]-.10, MOUTH+.01)
    moving, naive = {}, {}
    for side in (-1, 1):
        original = native["right" if side > 0 else "left"]
        naive[side] = original.fuse(place(window_fill(), side)).cut(
            place(receiver_cut, side)).clean()
        moving[side] = naive[side].cut(place(rim_relief, side)).clean()
    fixed = native["front_top"].fuse(*sleeves.values()).clean()
    results = {
        "scope": "Matched archived fixture only. Current front-top is stale; this is not a complete current assembly verification.",
        "input_sha256": {name: row["source_sha256"] for name, row in manifest.items()},
        "script_sha256": sha(__file__),
        "dimensions_mm": {
            "spring_od": SPRING_OD, "spring_free": SPRING_FREE,
            "fixed_sleeve_id": SLEEVE_ID, "fixed_sleeve_od": SLEEVE_OD,
            "fixed_sleeve_wall": SLEEVE_WALL, "fixed_sleeve_projection": PROJECTION,
            "moving_bore_id": MOVING_ID, "moving_bore_depth": BORE_DEPTH,
            "sleeve_to_moving_bore_radial_air": RADIAL_AIR,
            "spring_to_fixed_sleeve_radial_air": (SLEEVE_ID-SPRING_OD)/2,
            "spring_to_moving_bore_radial_air": (MOVING_ID-SPRING_OD)/2,
        },
        "archived_stations": {"x": X, "z": Z, "fixed_floor_y": FLOOR,
                              "moving_floor_y": MOVING_FLOOR, "moving_mouth_y": MOUTH},
        "current_reference_stations": {
            "x": CURRENT["spring_stations"][1]["x"],
            "z": CURRENT["spring_stations"][1]["z"],
            "fixed_floor_y": CURRENT["fixed_seat_floor_y"],
            "moving_floor_y": CURRENT["spring_stations"][1]["bore_floor_y"],
            "moving_mouth_y": CURRENT["spring_bore_mouth_y"],
        },
        "validity": {}, "working": [], "assembly": [], "local_stock": {},
        "rim_relief": {
            "reason": "The outboard retaining rim extends 6.15 mm fore of the bore mouth and intersects the external sleeve unless relieved.",
            "bore_diameter_mm": MOVING_ID,
            "y_band": [I["grip_rim_y"][0]-.10, MOUTH+.01],
            "minimum_remaining_radial_outer_rim_stock_mm": I["grip_rim_x"][1]-(X+MOVING_ID/2),
        },
    }
    for name, body in [("fixed", fixed), *((f"moving_{side}", s) for side, s in moving.items())]:
        results["validity"][name] = {"valid": body.isValid(), "solids": len(body.Solids())}

    for label, dy in (("release", 0.0), ("connected", 2.15), ("aft_limit", 4.65)):
        length = MOVING_FLOOR + dy - FLOOR
        axial = {"state": label, "dy": dy, "spring_length": length,
                 "sleeve_overlap_in_moving_bore": FLOOR+PROJECTION-(MOUTH+dy),
                 "sleeve_tip_to_floor": length-PROJECTION,
                 "spring_compression_from_free": SPRING_FREE-length}
        for side in (-1, 1):
            body = moving[side].translate((0, dy, 0))
            spring = place(ycyl(SPRING_OD, FLOOR, MOVING_FLOOR+dy), side)
            row = {**axial, "side": side}
            row["without_rim_relief_fixed_overlap_mm3"] = naive[side].translate((0,dy,0)).intersect(fixed).Volume()
            for name, obstacle in (("fixed", fixed), ("cartridge", native["cartridge"]),
                                   ("cap", native["cap"])):
                row[name+"_overlap_mm3"] = body.intersect(obstacle).Volume()
            row["spring_vs_fixed_overlap_mm3"] = spring.intersect(fixed).Volume()
            row["spring_vs_moving_overlap_mm3"] = spring.intersect(body).Volume()
            results["working"].append(row)

    for side in (-1, 1):
        body = moving[side]
        old = native["right" if side > 0 else "left"]
        # Verify that the web, flange/lap and material behind the spring floor
        # are not removed by the bore change. This does not predict stiffness.
        aft = box((-150, 150), (MOVING_FLOOR+.001, 180), (100, 260))
        changed_aft = old.intersect(aft).cut(body).Volume()
        web = box((-94, 94), (I["web_fore_y"], I["web_aft_y"]), I["web_z"])
        # The last 1.1 mm of enlarged bore reaches the web plane at the bar root.
        # Report any actual cut there instead of declaring unchanged web stock.
        removed_web = old.intersect(web).cut(body).Volume()
        results["local_stock"][str(side)] = {
            "minimum_inboard_bar_wall_mm": X-MOVING_ID/2-S["grip_back_x"],
            "floor_to_bar_aft_mm": I["guide_body_y"][1]-MOVING_FLOOR,
            "removed_behind_spring_floor_mm3": changed_aft,
            "removed_inside_web_envelope_mm3": removed_web,
            "added_to_carrier_mm3": body.cut(old).Volume(),
            "removed_from_carrier_mm3": old.cut(body).Volume(),
            "additional_rim_relief_mm3": naive[side].cut(body).Volume(),
        }

    # Follow the production inside-out sequence at the actual aft hard stop.
    # The half moves fore while inset by 3.25 mm, then moves laterally outward.
    aft_limit = I["aft_limit_offset_y"]
    inset = I["half_entry_shoulder_inset_x"]
    for side in (-1, 1):
        for dx_abs in (inset, 2.5, 1.5, .5, RADIAL_AIR, 0.0):
            pose = (-side*dx_abs, aft_limit, 0.0)
            body = moving[side].translate(pose)
            hit = body.intersect(sleeves[side])
            wall_hit = body.intersect(native["front_top"])
            results["assembly"].append({
                "path": "existing final outward seating", "side": side,
                "pose": pose, "axis_offset_mm": dx_abs,
                "sleeve_overlap_mm3": hit.Volume(), "sleeve_hit_bounds": bounds(hit),
                "original_wall_overlap_mm3": wall_hit.Volume(),
            })
        # Clearing the closed bore mouth is a necessary lower bound. The rim
        # projects still further forward. Test this already-excessive staging
        # offset against the real wall before claiming an assembly route.
        earlier_y = FLOOR + PROJECTION - MOUTH + .25
        pose = (0.0, earlier_y, 0.0)
        body = moving[side].translate(pose)
        hit = body.intersect(native["front_top"])
        results["assembly"].append({
            "path": "outward seating with bore mouth behind sleeve tip", "side": side,
            "pose": pose, "required_offset_y_mm": earlier_y,
            "extra_over_aft_stop_mm": earlier_y-aft_limit,
            "original_wall_overlap_mm3": hit.Volume(), "wall_hit_bounds": bounds(hit),
            "sleeve_overlap_mm3": body.intersect(sleeves[side]).Volume(),
        })
        # The fixed sleeve's new material must not narrow cartridge insertion.
        added = sleeves[side].cut(native["front_top"])
        b = native["cartridge"].BoundingBox()
        # This bounding prism encloses the entire 100 mm straight upward lift.
        sweep = box((b.xmin, b.xmax), (b.ymin, b.ymax), (b.zmin, b.zmax+100))
        results["assembly"].append({
            "path": "cartridge vertical bounding envelope", "side": side,
            "added_sleeve_overlap_mm3": added.intersect(sweep).Volume(),
            "added_sleeve_to_cartridge_mm": added.distance(native["cartridge"]),
            "added_sleeve_to_cap_mm": added.distance(native["cap"]),
        })

    results["assembly_math"] = {
        "inset_for_wall_shoulder_mm": inset,
        "maximum_parallel_axis_offset_while_overlapped_mm": RADIAL_AIR,
        "overlap_at_aft_stop_mm": FLOOR+PROJECTION-(MOUTH+aft_limit),
        "dy_for_disengagement_mm": FLOOR+PROJECTION-MOUTH,
        "dy_for_disengagement_with_axial_air_mm": FLOOR+PROJECTION-MOUTH+.25,
        "dy_for_entire_fore_rim_past_sleeve_tip_with_air_mm": FLOOR+PROJECTION-I["grip_rim_y"][0]+.25,
        "maximum_parallel_sleeve_length_for_existing_lateral_entry_mm": MOUTH+aft_limit-FLOOR,
        "minimum_sleeve_length_for_positive_operating_overlap_mm": MOUTH+aft_limit-FLOOR,
        "interpretation": "The same aft-stop pose is used for operation and lateral installation. A rigid sleeve cannot have positive overlap there and also clear a closed receiver for the 3.25 mm lateral entry. Additional assembly travel or a changed guide/stop/receiver is required.",
    }
    results["spring_end_alignment"] = {
        "largest_open_length_past_sleeve_tip_mm": MOVING_FLOOR+aft_limit-(FLOOR+PROJECTION),
        "moving_bore_radial_air_to_spring_mm": (MOVING_ID-SPRING_OD)/2,
        "interpretation": "Full external enclosure prevents escape but does not positively center the moving spring end in a 9.67 mm bore. A separate integral narrow end cup would reduce this freedom and consume sleeve tip clearance; it has not been qualified here.",
    }
    results["conclusion"] = "After relief of the retaining rim, the working telescope clears the archived native fixture, but the integral closed receiver blocks the established inside-out carrier assembly. The existing guide and aft stop prevent the axial disengagement needed to seat the half outward. No production change or print release."
    (HERE / "checks.json").write_text(json.dumps(results, indent=2)+"\n")
    # Local native coupons show the actual bore/wall intersections and the
    # troublesome final inside-out position without creating production files.
    clip = box((X-10, X+11), (FLOOR-3, MOVING_FLOOR+8), (Z-10, Z+11))
    for name, shape in (("fixed-sleeve-coupon", fixed.intersect(clip)),
                        ("moving-closed-bore-coupon", moving[1].intersect(clip)),
                        ("assembly-clash", moving[1].translate((-inset, aft_limit, 0)).intersect(sleeves[1]))):
        cq.exporters.export(shape, str(HERE / (name+".step")))
    print(json.dumps({"validity":results["validity"],"working":results["working"],
                      "assembly":results["assembly"],"local_stock":results["local_stock"],
                      "conclusion":results["conclusion"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
