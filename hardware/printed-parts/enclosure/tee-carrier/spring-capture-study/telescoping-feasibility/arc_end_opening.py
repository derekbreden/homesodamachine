"""Bound the short arc pair's open end regions in the frozen native fixture.

A swept rigid ball is an access probe, not a model of a spring coil. A clear
lane disproves whole-length enclosure by the arc pair; it does not predict
that the real spring will enter the lane or leave its end seats.
"""
import json
import math

import cadquery as cq

from evaluate import HERE, sha, bounds
from arc_guard_probe import sector, FIXED_LENGTH, MOVING_LENGTH


def main():
    current = HERE / "current-inputs"
    manifest = json.loads((current / "manifest.json").read_text())
    assert sha(current / "interface.json") == manifest["interface_sha256"]
    I = json.loads((current / "interface.json").read_text())["carrier_interface"]
    meta_path = HERE / "frozen-front-top/fixture.json"
    meta = json.loads(meta_path.read_text())
    wall_path = meta_path.parent / "current-front-top.step"
    assert sha(wall_path) == meta["step_sha256"]
    wall = cq.importers.importStep(str(wall_path)).val()
    X, Z = (I["spring_stations"][1][k] for k in ("x", "z"))
    floor = I["fixed_seat_floor_y"]
    separation = I["spring_stations"][1]["bore_floor_y"] - floor
    aft = I["aft_limit_offset_y"]
    end_window = I["spring_window_y"][1] - floor + aft
    y = (FIXED_LENGTH + end_window) / 2
    travel = 10.0
    radius = 3.0
    capsule = cq.Solid.makeCylinder(radius, travel, cq.Vector(0,y,0), cq.Vector(-1,0,0))
    capsule = capsule.fuse(cq.Solid.makeSphere(radius,cq.Vector(0,y,0),angleDegrees1=-90,angleDegrees2=90))
    capsule = capsule.fuse(cq.Solid.makeSphere(radius,cq.Vector(-travel,y,0),angleDegrees1=-90,angleDegrees2=90)).clean()
    expected_volume = math.pi*radius**2*travel + 4*math.pi*radius**3/3
    assert capsule.isValid() and abs(capsule.Volume()-expected_volume) < 1e-6
    fixed_arc = sector(125,235,0,FIXED_LENGTH)
    moving_arc = sector(-55,55,separation-MOVING_LENGTH+aft,separation+aft+.1)

    def place(shape, side):
        body = shape.translate((X,floor,Z))
        return body if side > 0 else body.mirror("YZ")

    rows = []
    for side,name in ((-1,"left"),(1,"right")):
        row = manifest["bodies"]["carrier-"+name]
        path = current / row["path"]
        assert sha(path) == row["sha256"]
        carrier = cq.importers.importStep(str(path)).val().translate((0,aft,0))
        probe = place(capsule,side)
        for label,obstacle in (("frozen front-top",wall),("original moving carrier",carrier),
                               ("fixed arc",place(fixed_arc,side)),("moving arc",place(moving_arc,side))):
            hit = probe.intersect(obstacle)
            rows.append({"side":side,"obstacle":label,"overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    states = []
    for name,dy in (("release",0),("connected",2.15),("aft_stop",aft)):
        states.append({"state":name,
                       "fixed_end_single_arc_axial_region_mm":separation+dy-MOVING_LENGTH-I["fixed_seat_depth"],
                       "moving_end_single_arc_axial_region_mm":I["spring_window_y"][1]-floor+dy-FIXED_LENGTH})
    report = {
        "scope":"Short complementary arc pair with the existing cups and loading window, on the frozen tee datum only. No relief, deeper cup, physical coupon or production source is released.",
        "script_sha256":sha(__file__),"arc_helper_sha256":sha(HERE/"arc_guard_probe.py"),
        "front_top_sha256":sha(wall_path),"fixture_sha256":sha(meta_path),
        "current_input_manifest_sha256":sha(current/"manifest.json"),
        "end_region_readings":states,
        "probe":{"rigid_ball_diameter_mm":2*radius,"inboard_sweep_mm":travel,
                 "center_y_above_fixed_floor_mm":y,"state":"aft_stop",
                 "native_volume_mm3":capsule.Volume(),"analytic_swept_ball_volume_mm3":expected_volume,
                 "distance_from_ball_to_fixed_arc_tip_mm":y-radius-FIXED_LENGTH,
                 "distance_from_ball_to_end_of_loading_window_mm":end_window-y-radius},
        "native_readings":rows,
        "entire_probe_lane_clear":all(r["overlap_mm3"] < 1e-5 for r in rows),
        "qualification":"The swept local rigid-OD probe identifies an open inboard lane near the moving spring end. It is not the entire spring, a prediction of coil deformation, or proof that either real spring end unseats. The arc pair does not enclose the entire spring length.",
    }
    (HERE/"arc-end-opening-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__ == "__main__":
    main()
