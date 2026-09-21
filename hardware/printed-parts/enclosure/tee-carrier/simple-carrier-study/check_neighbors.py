"""Concept against frozen current-datum native placed manifold neighbors."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,sha,box,bounds
from check_joint_motion import disjoint,swept_overlap,loft_wall
from tee_envelope import envelope,sweep

HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,Rrigid,wall,lip,*_=build()
    folder=HERE/"inputs/placed-neighbors"
    manifest=json.loads((folder/"manifest.json").read_text())
    neighbors={}
    for name,row in manifest["bodies"].items():
        p=folder/row["brep"]
        assert sha(p)==row["sha256"]
        neighbors[name]=cq.Shape.importBrep(str(p))
    report={"scope":"Frozen measured-tee native pack. Connected-state comparisons use its actual placed tubes. At other stops the four attached tee bodies move with the carrier; tube readings retain the connected tube path only, not a simulated flexible tube shape. Carrier installation uses the loose front-top with valves absent, and checks the four seated tees. Matching native wall readings are in wall-checks.json.",
        "generator_sha256":sha(HERE/"build_concept.py"),"script_sha256":sha(__file__),
        "neighbor_manifest_sha256":sha(folder/"manifest.json"),
        "tee_envelope_script_sha256":sha(HERE/"tee_envelope.py"),
        "operating":[],"tee_assembly_sweeps":[],"flex_wall_envelope":[]}
    for label,dy in (("release",0),("connected",I["connected_offset_y"]),("aft_limit",I["aft_limit_offset_y"])):
        for side,s in (("left",L),("right",R)):
            posed=s.translate((0,dy,0))
            for name,n in neighbors.items():
                obs=n.translate((0,dy-I["connected_offset_y"],0)) if name.startswith("tee-") else n
                if disjoint(posed.BoundingBox(),obs.BoundingBox()):
                    continue
                hit=posed.intersect(obs)
                report["operating"].append({"state":label,"side":side,"neighbor":name,
                    "overlap_mm3":hit.Volume(),
                    "hit_bounds":bounds(hit)})
            print(json.dumps({"state":label,"side":side,"readings":len(report["operating"]),
                "nonzero":[r for r in report["operating"] if r["overlap_mm3"]>1e-5]}),flush=True)
    # The complete outside box of every deformed wall position is a
    # conservative occupied region for static neighbor clearance.
    b=wall.fuse(lip).BoundingBox()
    flex_box=box((b.xmin,b.xmax),(b.ymin,b.ymax+2.3),(b.zmin,b.zmax))
    for dy in (0,I["connected_offset_y"],I["aft_limit_offset_y"]):
        posed=flex_box.translate((0,dy,0))
        for name,n in neighbors.items():
            if disjoint(posed.BoundingBox(),n.BoundingBox()):continue
            hit=posed.intersect(n)
            report["flex_wall_envelope"].append({"offset_y_mm":dy,"neighbor":name,
                                                "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    # Production carrier-installation source explicitly seats the tees at
    # release, not at the connected native-pack Y station. The extended branch
    # ring is remote from the carrier and is left as a conservative envelope.
    tees={n:s.translate((0,-I["connected_offset_y"],0))
          for n,s in neighbors.items() if n.startswith("tee-")}
    report["tee_envelope_containment"]={n:s.cut(envelope(s)).Volume() for n,s in tees.items()}
    assert all(v<1e-5 for v in report["tee_envelope_containment"].values())
    report["sweep_method"]="Each full native tee is first proved inside a union of two radius-8.25 mm cylinders. Exact cylinder/box unions cover every point of each straight carrier motion. Positive envelope overlaps are conservative; zeros prove clearance."
    # Record the actual production-reference barrier separately from the
    # corrected study so the enclosing-cylinder test cannot obscure it.
    original=cq.importers.importStep(str(HERE/"inputs/screwed-baseline-left.step")).val()
    outer=tees["tee-y-g"]
    report["outer_tee_entry_corner"]=[]
    for x in (3.25,2.5,1.5,0):
        for label,s in (("screwed_reference",original),("study",L)):
            hit=s.translate((x,I["aft_limit_offset_y"],0)).intersect(outer)
            report["outer_tee_entry_corner"].append({"part":label,"left_inset_x_mm":x,
                "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    report["installation_tee_pose"]={"state":"release","translation_from_native_pack_y_mm":-I["connected_offset_y"],
        "authority":"hardware/manifold-layout/enclosure_assembly.py _carrier_front_top_motion_bound seats installation tees at spec.release_offset_y; branch sleeve envelope is unpressed and remote from the carrier."}
    aft=I["aft_limit_offset_y"];stage=I["half_entry_staging_y"]
    for side,s in ((-1,L),(1,Rrigid)):
        shift=-side*I["half_entry_shift_x"]; shoulder=-side*I["half_entry_shoulder_inset_x"]
        poses=[(shift,210,70),(shift,stage,70),(shift,stage,0),
               (shoulder,stage,0),(shoulder,aft,0),(0,aft,0)]
        for start,end in zip(poses,poses[1:]):
            for name,tee in tees.items():
                swept=sweep(tee,start,end)
                hit=s.intersect(swept)
                row={"side":side,"tee":name,"start":start,"end":end,
                     "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)}
                report["tee_assembly_sweeps"].append(row)
                print(json.dumps(row),flush=True)
            (HERE/"neighbor-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    report["all_reported_native_readings_clear"]=all(r["overlap_mm3"]<1e-5 for r in report["operating"]+report["flex_wall_envelope"]) and all(
        r["overlap_mm3"]<1e-5 for r in report["tee_assembly_sweeps"])
    report["nonzero_operating"]=[r for r in report["operating"] if r["overlap_mm3"]>1e-5]
    (HERE/"neighbor-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"clear":report["all_reported_native_readings_clear"],"nonzero":report["nonzero_operating"]},indent=2),flush=True)


if __name__=="__main__":main()
