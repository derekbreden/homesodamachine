"""Small native feasibility probe for complementary integral arc guards.

This checks the guards against each other and identifies required relief in
the current carrier. It does not perform that relief or qualify coil behavior.
"""
import json
import math
from pathlib import Path

import cadquery as cq

from evaluate import HERE, sha, ycyl, bounds

R0, WALL = 6.57/2, 1.30
R1 = R0+WALL
ARC = 110.0
FIXED_LENGTH = MOVING_LENGTH = 13.50
HELD_LENGTH = 9.61


def polar(radius,angle):
    a=math.radians(angle)
    return radius*math.cos(a),radius*math.sin(a)


def sector(a0,a1,y0,y1):
    plane=cq.Plane(origin=(0,y0,0),xDir=(1,0,0),normal=(0,-1,0))
    body=(cq.Workplane(plane).moveTo(0,0).lineTo(*polar(R1,a0))
          .threePointArc(polar(R1,(a0+a1)/2),polar(R1,a1)).close()
          .extrude(y0-y1).val())
    return body.cut(ycyl(2*R0,y0-.1,y1+.1)).clean()


def main():
    current=HERE/"current-inputs"
    manifest=json.loads((current/"manifest.json").read_text())
    assert sha(current/"interface.json")==manifest["interface_sha256"]
    I=json.loads((current/"interface.json").read_text())["carrier_interface"]
    meta_path=HERE/"frozen-front-top/fixture.json"
    meta=json.loads(meta_path.read_text())
    wall_path=meta_path.parent/"current-front-top.step"
    assert sha(wall_path)==meta["step_sha256"]
    wall=cq.importers.importStep(str(wall_path)).val()
    fixed=sector(180-ARC/2,180+ARC/2,0,FIXED_LENGTH)
    moving=sector(-ARC/2,ARC/2,19.5-MOVING_LENGTH,19.6)
    x,z=(I["spring_stations"][1][k] for k in ("x","z"))
    floor=I["fixed_seat_floor_y"]

    def place(shape,side):
        right=shape.translate((x,floor,z))
        return right if side>0 else right.mirror("YZ")

    native={}
    for side,name in ((-1,"left"),(1,"right")):
        row=manifest["bodies"]["carrier-"+name]
        assert sha(current/row["path"])==row["sha256"]
        native[side]=cq.importers.importStep(str(current/row["path"])).val()
    pair=[]
    for dx in (3.25,2.5,1.5,.5,0.0):
        posed=moving.translate((-dx,4.65,0))
        pair.append({"inset_mm":dx,"guard_overlap_mm3":fixed.intersect(posed).Volume(),
                     "guard_distance_mm":fixed.distance(posed)})
    native_rows=[]
    for side in (-1,1):
        for state,dy,dx in (("release",0,0),("connected",2.15,0),("aft_stop",4.65,0),
                            ("inset_assembly",4.65,-side*3.25)):
            carrier=native[side].translate((dx,dy,0))
            fix=place(fixed,side)
            mov=place(moving,side).translate((dx,dy,0))
            hit=fix.intersect(carrier)
            native_rows.append({"side":side,"state":state,
                                "fixed_guard_vs_unmodified_carrier_mm3":hit.Volume(),
                                "required_carrier_relief_bounds":bounds(hit),
                                "moving_guard_vs_current_front_top_mm3":mov.intersect(wall).Volume()})
    held=ycyl(6.5,24.15-HELD_LENGTH,24.15).translate((-3.25,0,0))
    fixed_max_x=-R0*math.cos(math.radians(ARC/2))
    moving_min_x=-3.25+R0*math.cos(math.radians(ARC/2))
    throat=2*R0*math.cos(math.radians(ARC/2))
    record={"scope":"Guard-pair and frozen native interference feasibility only; required carrier relief, supports and complete assembly are not implemented or qualified. New tee branch measurements require placement rebase.",
            "script_sha256":sha(__file__),"front_top_sha256":sha(wall_path),
            "helper_sha256":sha(HERE/"evaluate.py"),"fixture_sha256":sha(meta_path),
            "current_input_manifest_sha256":sha(current/"manifest.json"),
            "parameters_mm":{"id":2*R0,"wall":WALL,"od":2*R1,"fixed_projection":FIXED_LENGTH,
                             "moving_projection_from_its_floor":MOVING_LENGTH,"held_spring_length":HELD_LENGTH},
            "arc_degrees_each":ARC,"guard_pair_at_assembly":pair,
            "continuous_lateral_separation_proof":{"fixed_guard_x_max":fixed_max_x,
                                                   "moving_guard_x_min_at_maximum_inset":moving_min_x,
                                                   "minimum_x_gap_mm":moving_min_x-fixed_max_x,
                                                   "scope":"All intermediate parallel X offsets from 0 to 3.25 mm; projected X intervals do not meet."},
            "axial_overlap_mm":{"release":7.5,"connected":5.35,"aft_stop":2.85},
            "spring_loading":{"held_length_mm":HELD_LENGTH,"front_end_above_fixed_floor_at_assembly_mm":24.15-HELD_LENGTH,
                              "front_end_past_fixed_guard_tip_mm":24.15-HELD_LENGTH-FIXED_LENGTH,
                              "held_spring_vs_fixed_guard_overlap_mm3":fixed.intersect(held).Volume(),
                              "reported_compressed_length_mm":7.0,"length_above_reported_compressed_mm":HELD_LENGTH-7,
                              "19mm_fixed_guard_available_spring_length_at_assembly_mm":24.15-19.0,
                              "tool":"An inboard-withdrawing flat blade could act through the retained loading window aft of the fixed-guard tip. Its full native exit route with the required relief is pending."},
            "rigid_od_escape_bound":{"inner_chord_across_each_angular_gap_mm":throat,
                                      "rigid_test_cylinder_diameter_mm":6.0,
                                      "gap_is_narrower_than_rigid_od":throat<6,
                                      "scope":"Only undeformed Ø6 geometry inside the zone where both arcs overlap. Individual coil-wire flexibility, ovalization and end-region escape are not modeled."},
            "current_native_interferences":native_rows,
            "conclusion":"Short complementary arcs can clear each other and a precompressed spring during the existing lateral seating. They require local carrier clearance relief and a clear pusher exit. The pair offers a geometric lateral bound only in its overlap; end-region enclosure, structure and real spring behavior remain unqualified. No coupon is released."}
    (HERE/"arc-guard-checks.json").write_text(json.dumps(record,indent=2)+"\n")
    cq.exporters.export(cq.Compound.makeCompound([fixed,moving.translate((0,4.65,0))]),str(HERE/"arc-pair-at-aft-stop.step"))
    print(json.dumps(record,indent=2),flush=True)


if __name__=="__main__":
    main()
