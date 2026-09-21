"""Local deeper-cup geometry and loading checks at measured tee datums.

The fixed cup is an integral enclosure feature, not a third carrier part.
Matching full-wall and placed-neighbor checks remain separate.
"""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,box,bounds,sha

HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,*_=build()
    x,z=I["spring_stations"][1]["x"],I["spring_stations"][1]["z"]
    floor=I["fixed_seat_floor_y"]
    mouth=I["spring_bore_mouth_y"]
    moving_floor=I["spring_stations"][1]["bore_floor_y"]
    bore=I["spring_bore_d"]
    depth=8.0
    od=bore+4.0
    def ycyl(d,y0,y1):
        return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
    fixed=ycyl(od,floor-3,floor+depth).cut(ycyl(bore,floor,floor+depth+.1)).clean()
    extension=ycyl(od,floor+I["fixed_seat_depth"]-.1,floor+depth).cut(
        ycyl(bore,floor+I["fixed_seat_depth"]-.2,floor+depth+.1)).clean()
    aft=I["aft_limit_offset_y"]
    report={"scope":"Local current-datum two-cup geometry only. Complete wall/guide and placed-neighbor checks are in wall-checks.json and neighbor-checks.json. Fixed extension merges into enclosure; no additional retained part.",
        "input_manifest_sha256":sha(HERE/"inputs/manifest.json"),
        "generator_sha256":sha(HERE/"build_concept.py"),"script_sha256":sha(__file__),
        "dimensions_mm":{"fixed_cup_depth":depth,"fixed_cup_id":bore,"fixed_cup_od":od,
                         "fixed_cup_wall":2,"moving_cup_depth":I["spring_bore_depth"],
                         "free_spring":27,"spring_od":6,"reported_solid_spring":7},
        "working":[],"loading":[],"assembly":[],
        "physical_required":["Load and release actual delivered spring with the temporary flat pusher.",
            "At each stop and during unequal-hand operation, try deliberate sideways coil bowing and observe both ends.",
            "Full-enclosure carrier bending and guide retention under realistic service force.",
            "No spring-force, wire-diameter, ID or fatigue assumptions are supplied."]}
    for label,dy in (("release",0),("connected",I["connected_offset_y"]),("aft_limit",aft)):
        moving=R.translate((0,dy,0))
        spring=ycyl(6.5,floor,moving_floor+dy)
        gap=mouth+dy-(floor+depth)
        cz=(floor+depth+mouth+dy)/2
        ball=cq.Solid.makeSphere(3,cq.Vector(x,cz,z),angleDegrees1=-90,angleDegrees2=90)
        # A capsule encloses the full lateral ball translation; this is a
        # blocking witness, not a claim about a deformable helical spring.
        cap=ball.fuse(ball.translate((-10,0,0))).fuse(
            cq.Solid.makeCylinder(3,10,cq.Vector(x-10,cz,z),cq.Vector(1,0,0))).clean()
        hit=cap.intersect(fixed.fuse(moving))
        report["working"].append({"state":label,"offset_y":dy,
            "spring_length_mm":moving_floor+dy-floor,"uncovered_middle_mm":gap,
            "gap_less_than_spring_od_mm":6-gap,
            "fixed_vs_moving_mm3":fixed.intersect(moving).Volume(),
            "spring_envelope_vs_fixed_mm3":spring.intersect(fixed).Volume(),
            "spring_envelope_vs_moving_mm3":spring.intersect(moving).Volume(),
            "rigid_d6_ball_straight_lateral_escape_witness_overlap_mm3":hit.Volume()})
    for inset in (I["half_entry_shoulder_inset_x"],2.5,1.5,.5,0):
        posed=R.translate((-inset,aft,0))
        hit=posed.intersect(fixed)
        report["assembly"].append({"right_inset_x_mm":inset,"offset_y_mm":aft,
                                     "fixed_cup_overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    # Whole fixed-cup outside envelope in the moving frame for every point
    # of the final straight lateral motion. Zero is a conservative proof.
    r=od/2
    fixed_sweep=box((x-r,x+r+I["half_entry_shoulder_inset_x"]),
                    (floor-3-aft,floor+depth-aft),(z-r,z+r))
    report["continuous_final_seating_outside_envelope_overlap_mm3"]=fixed_sweep.intersect(R).Volume()
    held=12.15
    tip=moving_floor+aft-held
    disc=ycyl(6.3,tip-.6,tip)
    tool=disc.fuse(box((x-10,x),(tip-.6,tip),(z-.5,z+.5))).clean()
    moving=R.translate((0,aft,0))
    withdraw=x-max(M["spec"]["tee_xs"])
    b=tool.BoundingBox()
    lane=box((b.xmin-withdraw,b.xmax),(b.ymin,b.ymax),(b.zmin,b.zmax))
    for name,item in (("held spring",ycyl(6.5,tip,moving_floor+aft)),
                      ("pusher",tool),("pusher full inboard withdrawal",lane)):
        report["loading"].append({"item":name,"fixed_overlap_mm3":item.intersect(fixed).Volume(),
                                  "moving_overlap_mm3":item.intersect(moving).Volume()})
    report["loading_parameters_mm"]={"held_spring_length":held,"pusher_tip_d":6.3,
        "pusher_tip_t":.6,"handle_inboard_length":10,"handle_height":1,
        "pusher_fore_y":tip-.6,"fixed_tip_y":floor+depth,
        "pusher_to_fixed_tip_air":tip-.6-(floor+depth),"inboard_withdrawal":withdraw}
    report["interpretation"]="The 4.75 mm maximum mouth gap is narrower than the Ø6 rigid envelope, and both end bores are closed. A helical spring can deform: these native readings do not establish essentially impossible real misalignment. The complete enclosure assembly print supplies the actual spring retention and feel observations."
    for name,body in (("fixed-cup-integral-extension",extension),("fixed-cup-local-section",fixed)):
        cq.exporters.export(body,str(HERE/(name+".step")))
    (HERE/"spring-capture-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2),flush=True)


if __name__=="__main__":main()
