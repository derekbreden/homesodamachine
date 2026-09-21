"""Rigid one-piece carrier route barriers against the frozen front-top.

The reference blank is reconstructed from matching native halves by replacing
the joint-only centre strip with the uninterrupted web and shelf described by
_carrier_blank. No production module is imported and no model is adopted.
"""
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
sys.path.insert(0, str(STUDY))
from evaluate import box, sha, bounds


def main():
    current = STUDY / "current-inputs"
    manifest = json.loads((current / "manifest.json").read_text())
    assert sha(current / "interface.json") == manifest["interface_sha256"]
    I = json.loads((current / "interface.json").read_text())["carrier_interface"]
    fixture_path = STUDY / "frozen-front-top/fixture.json"
    fixture = json.loads(fixture_path.read_text())
    wall_path = fixture_path.parent / "current-front-top.step"
    assert sha(wall_path) == fixture["step_sha256"]
    wall = cq.importers.importStep(str(wall_path)).val()
    halves=[]
    for name in ("left","right"):
        row=manifest["bodies"]["carrier-"+name]
        path=current/row["path"]
        assert sha(path)==row["sha256"]
        halves.append(cq.importers.importStep(str(path)).val())
    # The joint strip is inside the nearest tie cut and tee trough. Its only
    # original blank surfaces are the uninterrupted web and top shelf.
    xa,xb=I["joint_tongue_x"]
    nearest_tie=min(abs(v)-I["tie_slot_x"]/2 for r in I["tie_sites"] for v in r["slot_xs"])
    nearest_trough=min(abs(v)-I["station_trough_r"] for v in I["tee_xs"])
    assert max(abs(xa),abs(xb)) < min(nearest_tie,nearest_trough)
    strip=box((xa,xb),(0,200),(150,250))
    web=box((xa,xb),(I["web_fore_y"],I["web_aft_y"]),I["web_z"])
    flange=box((xa,xb),I["flange_y"],I["flange_z"])
    blank=halves[0].cut(strip).fuse(halves[1].cut(strip)).fuse(web).fuse(flange).clean()
    assert blank.isValid() and len(blank.Solids())==1
    outside_change=blank.cut(strip).cut(halves[0].fuse(halves[1])).Volume()
    assert outside_change<1e-5
    report={
        "scope":"Frozen provisional tee datum, front-bottom absent, bare carrier without springs/tees/valves. Axis-aligned route probes identify actual barriers; they do not exhaust all possible six-axis rigid motions or qualify a redesigned guide.",
        "script_sha256":sha(__file__),"helper_sha256":sha(STUDY/"evaluate.py"),
        "front_top_sha256":sha(wall_path),"fixture_sha256":sha(fixture_path),
        "current_input_manifest_sha256":sha(current/"manifest.json"),
        "blank":{"reconstruction":"Replace joint-only centre strip with _carrier_blank's uninterrupted web and shelf; preserve frozen native geometry outside that strip.",
                 "centre_strip_x":(xa,xb),"nearest_tie_cut_x_abs_mm":nearest_tie,
                 "nearest_trough_x_abs_mm":nearest_trough,"valid":blank.isValid(),
                 "solids":len(blank.Solids()),"volume_mm3":blank.Volume(),"bounds":bounds(blank),
                 "added_outside_joint_strip_mm3":outside_change},
        "native_poses":[],"diagnostic_bottom_clearance":{},
    }
    seam=160.0
    seam_rim=174.8
    def read(label,dy,dz):
        posed=blank.translate((0,dy,dz))
        hit=posed.intersect(wall)
        volume=hit.Volume()
        row={"label":label,"offset_y_mm":dy,"offset_z_mm":dz,
             "overlap_mm3":volume,"hit_bounds":bounds(hit),
             "hit_at_seam_storey_mm3":hit.intersect(box((-150,150),(0,240),(seam,seam_rim))).Volume() if volume>1e-8 else 0.0,
             "hit_above_seam_storey_mm3":hit.intersect(box((-150,150),(0,240),(seam_rim,360))).Volume() if volume>1e-8 else 0.0}
        report["native_poses"].append(row)
        print(json.dumps(row),flush=True)
    aft=I["aft_limit_offset_y"]
    for name,dy in (("release",0),("connected",I["connected_offset_y"]),("aft stop",aft)):
        read(name,dy,0)
    for dz in (-.24,-.25,-.30,-.5,-1,-5,-10,-14.8,-20,-30,-50,-68,-70,-80):
        read("straight underside entry at aft stop",aft,dz)
    for dy in (4.9,5.5,10,20,I["half_entry_staging_y"]):
        read("centred rear approach at installed height",dy,0)
    for dy,dz in ((aft,70),(I["half_entry_staging_y"],70),
                  (I["half_entry_staging_y"],-1),(I["half_entry_staging_y"],-30),
                  (I["half_entry_staging_y"],-68),(I["half_entry_staging_y"],-70)):
        read("alternate staging pose",dy,dz)
    # Conservative assembly aperture needed for a straight rise at the aft
    # stop: component prisms enclose each native feature's complete vertical
    # sweep. Their overlap is an upper bound, not the smallest possible cut.
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
    cuts=[]
    per_component=[]
    for name,xs,ys,zs in components:
        cutter=box((xs[0]-.25,xs[1]+.25),(ys[0]+aft-.25,ys[1]+aft+.25),(seam-.1,zs[1]+.25))
        cuts.append(cutter)
        hit=cutter.intersect(wall)
        per_component.append({"component":name,"overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    clearance=cuts[0]
    for cutter in cuts[1:]:clearance=clearance.fuse(cutter)
    clearance=clearance.clean()
    interference=clearance.intersect(wall).clean()
    report["diagnostic_bottom_clearance"]={
        "method":"Union of native component bounding prisms from Z160 to each component's upper plane at the aft stop, with 0.25 mm XY/top air. Conservative upper bound only; not a proposed production cut.",
        "components":per_component,"total_affected_native_mm3":interference.Volume(),
        "affected_bounds":bounds(interference),
        "seam_storey_affected_mm3":interference.intersect(box((-150,150),(0,240),(seam,seam_rim))).Volume(),
        "above_seam_affected_mm3":interference.intersect(box((-150,150),(0,240),(seam_rim,360))).Volume(),
    }
    (HERE/"checks.json").write_text(json.dumps(report,indent=2)+"\n")
    for name,body in (("continuous-reference-blank",blank),("underside-barrier-at-minus-1mm",blank.translate((0,aft,-1)).intersect(wall)),
                       ("conservative-bottom-opening-stock",interference)):
        cq.exporters.export(body,str(HERE/(name+".step")))


if __name__=="__main__":
    main()
