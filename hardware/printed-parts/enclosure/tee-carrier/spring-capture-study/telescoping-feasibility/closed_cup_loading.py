"""Assembly-access probe for two integral cups without an internal spring guide.

A temporary flat-ended pusher is a geometric access envelope, not a qualified
tool or a promise about manual compression, friction, buckling or spring force.
"""
import argparse
import json
import math
from pathlib import Path

import cadquery as cq

from evaluate import (HERE, STUDY, INPUTS, BASELINE, box, ycyl, along_y, sha, bounds)


def main(current=False):
    if current:
        root=next(p for p in HERE.parents if (p/".git").exists())
        fixture_path=HERE/"frozen-front-top/fixture.json"
        fixture=json.loads(fixture_path.read_text())
        wall_path=fixture_path.parent/"current-front-top.step"
        assert sha(wall_path)==fixture["step_sha256"]
        current_inputs=HERE/"current-inputs"
        manifest=json.loads((current_inputs/"manifest.json").read_text())
        assert sha(current_inputs/"interface.json")==manifest["interface_sha256"]
        I=json.loads((current_inputs/"interface.json").read_text())["carrier_interface"]
        S={**BASELINE["spec"],"entry_staging_y":I["half_entry_staging_y"]}
        paths={"front_top":wall_path}
        for name in ("left","right"):
            row=manifest["bodies"]["carrier-"+name]
            paths[name]=current_inputs/row["path"]
            assert sha(paths[name])==row["sha256"]
        provenance={"fixture_path":str(fixture_path.relative_to(root)),
                    "fixture_sha256":sha(fixture_path),"front_top_sha256":sha(wall_path),
                    "current_input_manifest_sha256":sha(current_inputs/"manifest.json")}
        prefix="current-"
    else:
        manifest=json.loads((STUDY/"input-manifest.json").read_text())
        for row in manifest.values():
            assert sha(STUDY/row["frozen_path"])==row["source_sha256"]
        I,S=BASELINE["interface"],BASELINE["spec"]
        paths={name:INPUTS/f"{name}.step" for name in ("front_top","left","right")}
        provenance={"input_manifest_sha256":sha(STUDY/"input-manifest.json")}
        prefix=""
    X,Z=(I["spring_stations"][1][k] for k in ("x","z"))
    FLOOR=I["fixed_seat_floor_y"]
    MOVING_FLOOR=I["spring_stations"][1]["bore_floor_y"]
    MOUTH=I["spring_bore_mouth_y"]

    def place(shape,side):
        right=shape.translate((X,0,Z))
        return right if side>0 else right.mirror("YZ")

    def window_fill():
        r=I["spring_bore_d"]/2
        u=I["grip_back_x"]-X
        return along_y(((u,-r),(0,-r),(0,r),(u,r-u)),MOUTH,I["spring_window_y"][1])

    native={name:cq.importers.importStep(str(path)).val() for name,path in paths.items()}
    radius=I["spring_bore_d"]/2
    tangent=radius/math.sqrt(2)
    passage=ycyl(2*radius,MOUTH-.1,MOVING_FLOOR+.1).fuse(
        along_y(((-tangent,tangent),(0,radius*math.sqrt(2)),(tangent,tangent)),
                MOUTH-.1,MOVING_FLOOR+.1)).clean()
    fill=window_fill().cut(passage).clean()
    halves={side:native["right" if side>0 else "left"].fuse(place(fill,side)).clean()
            for side in (-1,1)}
    aft=I["aft_limit_offset_y"]
    shoulder=I["half_entry_shoulder_inset_x"]
    staged=S["entry_staging_y"]
    rows=[]
    # Several axial holding positions distinguish a blocked probe from a
    # supposed impossibility. The spring is always represented only by OD.
    for tip_above_floor in (3.0,5.0,8.0,12.0):
        tip=FLOOR+tip_above_floor
        moving_end=MOVING_FLOOR+aft
        length=moving_end-tip
        spring=ycyl(6.5,tip,moving_end)  # Ø6 spring plus 0.25 mm radial air
        disc=ycyl(6.3,tip-.6,tip)
        handle=box((-10,0),(tip-.6,tip),(-.5,.5))
        tool=disc.fuse(handle).clean()
        # Straight forward motion while inset: the cylinder's swept volume is
        # exact; the tool uses a conservative rectangular swept envelope.
        b=tool.BoundingBox()
        forward_tool=box((b.xmin,b.xmax),(b.ymin,b.ymax+staged-aft),(b.zmin,b.zmax))
        forward_spring=ycyl(6.5,tip,moving_end+staged-aft)
        for side in (-1,1):
            row={"side":side,"tip_above_fixed_floor_mm":tip_above_floor,
                 "held_spring_length_mm":length,"compression_from_free_mm":27-length,
                 "readings":[]}
            def read(label,shape,blocker):
                overlap=shape.intersect(blocker)
                row["readings"].append({"label":label,"overlap_mm3":overlap.Volume(),
                                        "hit_bounds":bounds(overlap)})
            # The held spring and pusher accompany the half during the
            # existing rear-entry, lowering and shoulder-approach segments.
            inset=-side*I["half_entry_shift_x"]
            shoulder_x=-side*shoulder
            rear_offset=native["front_top"].BoundingBox().ymax-I["grip_rim_y"][0]+.25
            poses=((inset,rear_offset,70),(inset,staged,70),
                   (inset,staged,0),(shoulder_x,staged,0),(shoulder_x,aft,0))
            labels=("rear entry above well","lowering behind fixed body", "approach wall shoulder", "fore slide while inset")
            for item_name,item in (("held spring",spring),("pusher",tool)):
                bb=place(item,side).translate((0,-aft,0)).BoundingBox()
                for label,start,end_pose in zip(labels,poses,poses[1:]):
                    ranges=[(getattr(bb,a+"min")+min(v,w),getattr(bb,a+"max")+max(v,w))
                            for a,v,w in zip("xyz",start,end_pose)]
                    sweep=box(*ranges)
                    read(item_name+" complete "+label+" bounding sweep",sweep,native["front_top"])
                    if side>0:
                        read(item_name+" "+label+" versus parked left half",sweep,halves[-1].translate((0,aft,0)))
            read("held spring forward sweep while inset",place(forward_spring,side).translate((-side*shoulder,0,0)),native["front_top"])
            read("pusher forward bounding sweep while inset",place(forward_tool,side).translate((-side*shoulder,0,0)),native["front_top"])
            for dx in (shoulder,2.5,1.5,.5,0.0):
                shift=(-side*dx,0,0)
                read(f"spring during outward seating at inset {dx:g}",place(spring,side).translate(shift),native["front_top"])
                read(f"pusher during outward seating at inset {dx:g}",place(tool,side).translate(shift),native["front_top"])
            carrier=halves[side].translate((0,aft,0))
            read("held spring within closed moving cup",place(spring,side),carrier)
            read("pusher versus closed moving carrier",place(tool,side),carrier)
            # Pusher leaves toward the open inboard well after the half seats.
            # An enclosing prism proves a clear lane if its overlap is zero.
            withdraw=X-max(S["tee_xs"])
            withdrawal=box((b.xmin-withdraw,b.xmax),(b.ymin,b.ymax),(b.zmin,b.zmax))
            read("inboard pusher withdrawal bounding sweep",place(withdrawal,side),native["front_top"])
            read("inboard pusher withdrawal versus carrier",place(withdrawal,side),carrier)
            # Lift out through the same outer-well approach used by spring
            # loading, then leave through the loose front-top's open rear.
            lift=box((b.xmin-withdraw,b.xmax-withdraw),(b.ymin,b.ymax),
                     (b.zmin,b.zmax+70))
            read("pusher lift through outer well",place(lift,side),native["front_top"])
            read("pusher lift versus installed half",place(lift,side),carrier)
            wall_rear=native["front_top"].BoundingBox().ymax
            rear=box((b.xmin-withdraw,b.xmax-withdraw),(b.ymin,wall_rear+1),
                     (b.zmin+70,b.zmax+70))
            read("pusher exit through open rear",place(rear,side),native["front_top"])
            # This is a straight envelope only. The real spring is not assumed
            # to obey it automatically when the pusher is released.
            expansion=place(ycyl(6.5,FLOOR,moving_end),side)
            read("coaxial spring expansion envelope versus fixed cup",expansion,native["front_top"])
            read("coaxial spring expansion envelope versus moving cup",expansion,carrier)
            row["all_tested_geometry_clear"]=max(r["overlap_mm3"] for r in row["readings"])<1e-5
            rows.append(row)
    # Operating enclosure has two bearing cups but an uncovered middle span.
    states=[]
    for label,dy in (("release",0.0),("connected",2.15),("aft_limit",4.65)):
        gap=MOUTH+dy-I["fixed_seat_mouth_y"]
        states.append({"state":label,"spring_length_mm":MOVING_FLOOR+dy-FLOOR,
                       "moving_cup_depth_mm":I["spring_bore_depth"],
                       "fixed_cup_depth_mm":I["fixed_seat_depth"],
                       "unconfined_span_between_cup_mouths_mm":gap})
    scope=("Frozen fresh front-top native fixture with corrected Kamoer/tee baseline and provisional 20.07 mm tee branch datum; the new tee measurement, selected G Ganen and complete production enclosure require rebase."
           if current else "Matched archived native fixture; current production enclosure remains unqualified.")
    report={"scope":scope+" Valves are absent for carrier installation. Actual spring deformation/force is not qualified.",
            "script_sha256":sha(__file__),"helper_sha256":sha(HERE/"evaluate.py"),**provenance,
            "moving_cup":"Existing Ø6.57 teardrop bore, original floor and full inboard window permanently filled.",
            "temporary_pusher":{"flat_tip_diameter_mm":6.3,"tip_thickness_mm":.6,
                                 "inboard_handle_length_mm":10,"handle_height_mm":1.0,
                                 "role":"Temporary loading-access envelope, no retained plug and no spring-ID engagement.",
                                 "qualification":"Tool stiffness, hand access/comfort and applied force unmeasured."},
            "loading_rows":rows,"working_states":states,
            "tool_disc_above_tee_trough_top_mm":Z-6.3/2-I["station_trough_top_z"],
            "spring_clearance_envelope_above_tee_trough_top_mm":Z-6.5/2-I["station_trough_top_z"],
            "qualification":{"native_access":"Read individual swept-envelope results; clearance does not assert low manual compression effort.",
                             "end_retention":"The closed moving bore and fixed 2 mm cup retain end positions under an assumed coaxial spring. No intermediate lateral guide spans the open 6.4–11.05 mm gap.",
                             "physical_required":"Actual loading/release with the delivered spring, full-stroke and unequal-hand cycling, end seating and lateral bowing observation. Spring rate, force, wire and ID are not invented.",
                             "production":"Full production assembly, actual loading/retention observations and print/support qualification still required."}}
    report["clear_loading_cases"]=[{"side":r["side"],"held_spring_length_mm":r["held_spring_length_mm"],
                                     "compression_from_free_mm":r["compression_from_free_mm"]}
                                    for r in rows if r["all_tested_geometry_clear"]]
    (HERE/(prefix+"closed-cup-checks.json")).write_text(json.dumps(report,indent=2)+"\n")
    clip=box((X-10,X+11),(FLOOR-3,MOVING_FLOOR+8),(Z-10,Z+11))
    for name,shape in (("closed-cup-fixed-native-coupon",native["front_top"].intersect(clip)),
                       ("closed-cup-moving-native-coupon",halves[1].intersect(clip))):
        cq.exporters.export(shape,str(HERE/(prefix+name+".step")))
    print(json.dumps({"cases":[{k:v for k,v in row.items() if k!='readings'} for row in rows],
                      "working_states":states},indent=2),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--current",action="store_true",help="Use the frozen carrier and archived fresh front-top fixture; not a claim of production currentness")
    args=parser.parse_args()
    main(args.current)
