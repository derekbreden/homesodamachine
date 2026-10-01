"""Read full-thickness wall ends and the bottom enclosure's mating geometry."""
import argparse
import json

import prepare_geometry as p


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--baseline-dir",type=p.Path)
    args=parser.parse_args()
    e=p.e
    box,_,_=p._declared_box(p._box_spec,e)
    pieces={n:p.cq.importers.importStep(str(p.ENC/f"enclosure-{n}.step"))
            for n in ("front-bottom","back-bottom")}
    shapes={n:s.val() for n,s in pieces.items()}
    bed,roof,_=e._handhold_levels(box.inner)
    ends={n:e._handhold_backing_end(box.y_joint,n) for n in ("front","back")}
    rows=[]

    def check(name,ok,**data):
        row={"check":name,"pass":bool(ok),**data}
        rows.append(row)
        print(name,ok,data,flush=True)

    check("Both bottom halves are valid connected solids",
          all(s.isValid() and len(s.Solids())==1 for s in shapes.values()))
    overlap=shapes["front-bottom"].intersect(shapes["back-bottom"]).Volume()
    check("Assembled bottom halves do not overlap",overlap<.001,overlap_mm3=overlap)
    for side in (-1,1):
        x_ext=side*e.appliance_width/2
        _seat,_tip,_heat,cap=e._boss_x(x_ext,-side)
        xa,xb=sorted((cap,cap+side*e.handhold_wall))
        for name,y in ends.items():
            shape=shapes[f"{name}-bottom"]
            y0,y1=(y-.5,y) if name=="front" else (y,y+.5)
            stock=e._ybox(xa,xb,y0,y1,bed,roof)
            missing=stock.cut(shape).Volume()
            face_window=e._ybox(xa,xb,y-.001,y+.001,bed,roof)
            faces=[]
            for face in shape.Faces():
                if face.geomType()!="PLANE":continue
                b=face.BoundingBox()
                if (abs(b.ymin-y)<1e-6 and abs(b.ymax-y)<1e-6
                    and b.xmax>xa and b.xmin<xb and b.zmax>bed and b.zmin<roof):
                    faces.append(face.intersect(face_window).Area())
            area=e.handhold_wall*(roof-bed)
            check(f"{name} wall {side:+d} ends at the full 3 mm section",
                  missing<.001 and abs(sum(faces)-area)<.001,
                  end_y_mm=y,missing_stock_mm3=missing,end_face_areas_mm2=faces)
        air=e._ybox(xa,xb,ends["front"],ends["back"],bed,roof)
        contested=sum(s.intersect(air).Volume() for s in shapes.values())
        check(f"Wall {side:+d} has an open running gap",contested<.001,
              gap_mm=ends["back"]-ends["front"],blocked_mm3=contested)
    for bound in (e._handhold_bound(pieces,box),e._lower_y_seam_bound(pieces,box)):
        check(bound.label,bound.ok,reading=bound._asdict())
    if args.baseline_dir:
        allowed=p.cq.Compound.makeCompound([e._ybox(x0,x1,208,214,bed,roof)
            for x0,x1 in ((90.5,93.5),(-93.5,-90.5))])
        for name,shape in shapes.items():
            original=args.baseline_dir/f"original-{name}.step"
            old=p.cq.importers.importStep(str(original)).val()
            added=shape.cut(old)
            removed=old.cut(shape)
            outside=sum(s.cut(allowed).Volume() for s in (added,removed) if s.Solids())
            check(f"{name} changes only the handhold wall joint",outside<.001,
                  change_outside_joint_mm3=outside,baseline_sha256=p.sha(original))
    report={"status":"pass" if all(r["pass"] for r in rows) else "fail",
            "checks":rows,"artifacts_sha256":{f"enclosure-{n}.step":p.sha(p.ENC/f"enclosure-{n}.step")
                for n in shapes},"scope":"Geometric wall stock, seam fit and retained lifting structure; no physical load test."}
    (p.HERE/"geometry-check.json").write_text(json.dumps(report,indent=2)+"\n")
    if report["status"]!="pass":raise SystemExit(1)


if __name__=="__main__":main()
