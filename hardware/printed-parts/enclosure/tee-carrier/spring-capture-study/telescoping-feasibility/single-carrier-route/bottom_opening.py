"""Bound a bottom-open guide and direct transfer of its stock to front-bottom.

This is an intentionally limited virtual change to the frozen native fixture.
No production source or print is generated. It tests access and the existing
shell's Y-slide closure, not a finished replacement guide or spring tool.
"""
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
sys.path.insert(0,str(STUDY))
from evaluate import box,ycyl,along_y,sha,bounds


def main():
    current=STUDY/"current-inputs"
    manifest=json.loads((current/"manifest.json").read_text())
    assert sha(current/"interface.json")==manifest["interface_sha256"]
    I=json.loads((current/"interface.json").read_text())["carrier_interface"]
    fixture_path=STUDY/"frozen-front-top/fixture.json"
    fixture=json.loads(fixture_path.read_text())
    wall_path=fixture_path.parent/"current-front-top.step"
    assert sha(wall_path)==fixture["step_sha256"]
    wall=cq.importers.importStep(str(wall_path)).val()
    blank_path=HERE/"continuous-reference-blank.step"
    blank=cq.importers.importStep(str(blank_path)).val()
    aft=I["aft_limit_offset_y"]
    components=[("web",I["web_x"],(I["web_fore_y"],I["web_aft_y"]),I["web_z"]),
                ("flange",(-I["flange_x"],I["flange_x"]),I["flange_y"],I["flange_z"])]
    for side in (-1,1):
        handed=lambda xs: xs if side>0 else (-xs[1],-xs[0])
        components.extend([
            (f"bar {side}",handed((I["grip_back_x"],I["grip_outer_x"])),I["guide_body_y"],I["printed_guide_body_z"]),
            (f"backing {side}",handed((I["grip_back_x"],I["grip_back_x"]+I["grip_back_t"])),I["grip_back_y"],I["printed_grip_back_z"]),
            (f"aft grip {side}",handed(I["grip_aft_x"]),I["grip_aft_y"],I["printed_guide_body_z"]),
            (f"retaining rim {side}",handed(I["grip_rim_x"]),I["grip_rim_y"],I["printed_grip_rim_z"]),
        ])
    def union(shapes):
        body=shapes[0]
        for s in shapes[1:]:body=body.fuse(s)
        return body.clean()
    component_bounds=union([box(xs,ys,zs) for _,xs,ys,zs in components])
    assert blank.cut(component_bounds).Volume()<1e-5
    x,z=(I["spring_stations"][1][k] for k in ("x","z"))
    moving_floor=I["spring_stations"][1]["bore_floor_y"]
    fixed_floor=I["fixed_seat_floor_y"]
    mouth=I["spring_bore_mouth_y"]
    radius=I["spring_bore_d"]/2
    tangent=radius/math.sqrt(2)
    u=I["grip_back_x"]-x
    passage=ycyl(2*radius,mouth-.1,moving_floor+.1).fuse(
        along_y(((-tangent,tangent),(0,radius*math.sqrt(2)),(tangent,tangent)),mouth-.1,moving_floor+.1))
    closure=along_y(((u,-radius),(0,-radius),(0,radius),(u,radius-u)),mouth,I["spring_window_y"][1]).cut(passage).clean()
    def place(shape,side):
        right=shape.translate((x,0,z))
        return right if side>0 else right.mirror("YZ")
    closed=blank.fuse(place(closure,-1)).fuse(place(closure,1)).clean()
    assert closed.isValid() and len(closed.Solids())==1
    assert closed.cut(component_bounds).Volume()<1e-5
    # End position of each closed cup is at the prescribed aft stop. A 70 mm
    # downward shift puts the entire carrier below Z160. The complete motion
    # is enclosed by the following native component prisms.
    nominal_sweep=union([box(xs,(ys[0]+aft,ys[1]+aft),(zs[0]-70,zs[1]))
                         for _,xs,ys,zs in components])
    collision=nominal_sweep.intersect(wall).clean()
    fore_shoulder_top=I["grip_rim_z"][0]-I["guide_slide_air"]
    high_region=box((-150,150),(0,240),(fore_shoulder_top+.001,360))
    assert collision.intersect(high_region).Volume()<1e-5
    cut_prisms=[box((xs[0]-.25,xs[1]+.25),(ys[0]+aft-.25,ys[1]+aft+.25),
                    (159.9,fore_shoulder_top+.001)) for _,xs,ys,zs in components]
    # Two temporary pusher envelopes accompany the springs. No assumption is
    # made that a person can comfortably maintain both compressions unaided.
    tip=fixed_floor+12.0
    spring=ycyl(6.5,tip,moving_floor+aft)
    tool=ycyl(6.3,tip-.6,tip).fuse(box((-10,0),(tip-.6,tip),(-.5,.5))).clean()
    loading_sweeps=[]
    for side in (-1,1):
        for label,body in (("held spring",place(spring,side)),("temporary pusher",place(tool,side))):
            bb=body.BoundingBox()
            sweep=box((bb.xmin,bb.xmax),(bb.ymin,bb.ymax),(bb.zmin-70,bb.zmax))
            loading_sweeps.append((side,label,sweep))
            cut_prisms.append(box((bb.xmin-.25,bb.xmax+.25),(bb.ymin-.25,bb.ymax+.25),
                                  (159.9,fore_shoulder_top+.001)))
    opening=union(cut_prisms)
    stock=wall.intersect(opening).clean()
    opened=wall.cut(opening).clean()
    report={
        "scope":"Virtual bottom-open guide and unchanged-position keeper stock against a frozen native baseline only. No production edit, complete lower shell, coupon, force or strength qualification.",
        "script_sha256":sha(__file__),"helper_sha256":sha(STUDY/"evaluate.py"),
        "front_top_sha256":sha(wall_path),"fixture_sha256":sha(fixture_path),
        "continuous_blank_sha256":sha(blank_path),"route_report_sha256":sha(HERE/"checks.json"),
        "current_input_manifest_sha256":sha(current/"manifest.json"),
        "continuous_closed_carrier":{"valid":closed.isValid(),"solids":len(closed.Solids()),
                                     "added_closure_mm3":closed.Volume()-blank.Volume(),"outside_component_envelopes_mm3":closed.cut(component_bounds).Volume()},
        "bottom_opening":{"cut_limit_z_mm":(159.9,fore_shoulder_top+.001),
                          "method":"Component XY bounding prisms plus 0.25 mm air, limited below the actual fore-shoulder top; exact full vertical bounding sweep is checked independently.",
                          "nominal_sweep_collision_mm3":collision.Volume(),"nominal_sweep_hit_bounds":bounds(collision),
                          "removed_stock_mm3":stock.Volume(),"removed_stock_bounds":bounds(stock),
                          "removed_stock_solid_count":len(stock.Solids()),
                          "opened_front_top_valid":opened.isValid(),"opened_front_top_solid_count":len(opened.Solids()),
                          "removed_upper_aft_stop_or_top_bearing_mm3":stock.intersect(box((-150,150),(0,240),(I["service_slot_z"][1],360))).Volume()},
        "entry_readings":[],"shell_closure_readings":[],
    }
    def read(group,label,body,obstacle):
        hit=body.intersect(obstacle)
        row={"label":label,"overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)}
        report[group].append(row)
        print(json.dumps(row),flush=True)
    read("entry_readings","entire closed carrier 70 mm rise, conservative continuous sweep",nominal_sweep,opened)
    for side,label,sweep in loading_sweeps:
        read("entry_readings",f"{label} {side} 70 mm rise, conservative continuous sweep",sweep,opened)
    # The existing front-top assembles by sliding +Y from the front. If all
    # removed guide stock simply becomes lower-shell stock, it stays fixed
    # while the opened top and its installed carrier take this closure motion.
    for shift in (-100.,-50.,-30.,-20.,-10.,-5.,-1.,0.):
        read("shell_closure_readings",f"carrier + top at Y shift {shift:g}: carrier / transferred keeper",
             closed.translate((0,aft+shift,0)),stock)
        read("shell_closure_readings",f"carrier + top at Y shift {shift:g}: opened top / transferred keeper",
             opened.translate((0,shift,0)),stock)
    report["all_entry_readings_clear"]=all(r["overlap_mm3"]<1e-5 for r in report["entry_readings"])
    report["all_tested_shell_closure_poses_clear"]=all(r["overlap_mm3"]<1e-5 for r in report["shell_closure_readings"])
    report["interpretation"]={
        "guidance":"The opening removes the lower fixed bearing floor, side sills/seam material and the aft portion of the fore shoulder in the carrier entry footprints. The upper aft stop and top guide remain. A connected, supported keeper must restore the lower constraints; fragmented cut stock is not a finished printable part.",
        "spring_loading":"The two closed moving cups and fixed 2 mm cups are retained. Two temporary pushers hold 12.15 mm spring lengths during the virtual lift; simultaneous hand operation, force and spring stability are unmeasured.",
        "closure":"Returning the removed stock at its original coordinates recovers the final native interfaces only. Read the closure witnesses before proposing that direct stock transfer onto front-bottom.",
        "release":"No production architecture, physical coupon or print is released; measured tee placement requires rebase.",
    }
    (HERE/"bottom-opening-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    cq.exporters.export(closed,str(HERE/"continuous-closed-cup-reference.step"))
    cq.exporters.export(stock,str(HERE/"bottom-keeper-required-stock.step"))


if __name__=="__main__":
    main()
