"""Native continuous straight-motion and snap-wall clearance witnesses."""
import json
from pathlib import Path
import cadquery as cq
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from build_concept import build,box,bounds,sha

HERE=Path(__file__).resolve().parent


def disjoint(a,b):
    return any(getattr(a,k+"max") < getattr(b,k+"min")+1e-7 or
               getattr(b,k+"max") < getattr(a,k+"min")+1e-7 for k in "xyz")


def swept_overlap(s,start,end,obstacle):
    """Sweep all boundary faces plus starting interior along one translation.

    Planar faces use exact native prisms, with their inner holes preserved.
    Curved faces use enclosing swept boxes: zero is conservative, a positive
    curved-face reading is inconclusive rather than a proven interference.
    """
    vec=cq.Vector(*(b-a for a,b in zip(start,end)))
    posed=s.translate(start)
    obb=obstacle.BoundingBox()
    rows=[]
    initial=posed.intersect(obstacle).Volume()
    for idx,f in enumerate(posed.Faces()):
        b=f.BoundingBox()
        spans=[(getattr(b,k+"min")+min(0,v),getattr(b,k+"max")+max(0,v))
               for k,v in zip("xyz",vec.toTuple())]
        if any(q-p<1e-8 for p,q in spans):
            continue
        envelope=box(*spans)
        if disjoint(envelope.BoundingBox(),obb):
            continue
        planar=f.geomType()=="PLANE"
        if planar and abs(f.normalAt().dot(vec))<1e-8:
            continue
        # Sweep the original trimmed face directly: reconstructing its wires
        # can reject valid native seams or change the face's inner boundaries.
        prism=cq.Shape.cast(BRepPrimAPI_MakePrism(
            f.wrapped,gp_Vec(*vec.toTuple()),True).Shape()) if planar else envelope
        kind="exact planar prism" if planar else "curved-face enclosing box"
        if not prism.isValid():
            prism=envelope
            kind="invalid-face-prism enclosing box"
        hit=prism.intersect(obstacle)
        rows.append({"face":idx,"kind":kind,
                     "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    return {"start":start,"end":end,"initial_overlap_mm3":initial,
            "tested_face_prisms":len(rows),"max_prism_overlap_mm3":max([0]+[r["overlap_mm3"] for r in rows]),
            "nonzero":[r for r in rows if r["overlap_mm3"]>1e-5]}


def loft_wall(wall,lip,tip=2.3):
    wb=wall.BoundingBox()
    lb=lip.BoundingBox()
    length=wb.xlen
    def shift(x):
        s=(wb.xmax-x)/length
        return tip*(3*s*s-s*s*s)/2
    def rect(x,y0,y1,z0,z1):
        plane=cq.Plane(origin=(x,0,0),xDir=(0,1,0),normal=(1,0,0))
        return cq.Workplane(plane).center((y0+y1)/2+shift(x),(z0+z1)/2)\
            .rect(y1-y0,z1-z0).val()
    xs=sorted(set([wb.xmin,lb.xmax]+[wb.xmin+length*i/10 for i in range(11)]))
    flex=cq.Solid.makeLoft([rect(x,wb.ymin,wb.ymax,wb.zmin,wb.zmax) for x in xs],False)
    nose=cq.Solid.makeLoft([rect(lb.xmin+(lb.xmax-lb.xmin)*i/6,
                                 lb.ymin,lb.ymax+.03,lb.zmin,lb.zmax) for i in range(7)],False)
    return flex.fuse(nose).clean()


def main():
    M,I,plain,blank,L,R,Rrigid,wall,lip,*_=build()
    aft=I["aft_limit_offset_y"]
    left=L.translate((0,aft,0))
    shift=I["half_entry_shift_x"]
    shoulder=I["half_entry_shoulder_inset_x"]
    stage=I["half_entry_staging_y"]
    poses=[(-shift,210,70),(-shift,stage,70),(-shift,stage,0),
           (-shoulder,stage,0),(-shoulder,aft,0),(0,aft,0)]
    report={"scope":"Two-half relative assembly only; whole-wall/neighbor checks are separate.",
            "generator_sha256":sha(HERE/"build_concept.py"),"script_sha256":sha(__file__),
            "continuous_rigid_sweeps":[],"elastic_wall_clearance":[]}
    for start,end in zip(poses,poses[1:]):
        row=swept_overlap(Rrigid,start,end,left)
        report["continuous_rigid_sweeps"].append(row)
        print(json.dumps(row),flush=True)
    flex=loft_wall(wall,lip)
    flexed=Rrigid.fuse(flex).clean()
    report["deflected_wall_model"]={"tip_y_mm":2.3,"root_shift_mm":0,
        "shape_law":"Cubic cantilever displacement interpolation; geometric clearance witness, not a material simulation.",
        "valid":flexed.isValid(),"solids":len(flexed.Solids()),"free_tip_length_x_mm":wall.BoundingBox().xlen}
    assert flexed.isValid() and len(flexed.Solids())==1
    for inset in (3.25,2.5,1.5,.5,.25):
        hit=flexed.translate((-inset,aft,0)).intersect(left)
        report["elastic_wall_clearance"].append({"inset_x_mm":inset,"tip_deflection_y_mm":2.3,
                                                "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    for amount in (2.3,1.5,.5,0):
        nose=loft_wall(wall,lip,amount) if amount else wall.fuse(lip)
        hit=nose.translate((-.25,aft,0)).intersect(left)
        report["elastic_wall_clearance"].append({"inset_x_mm":.25,"tip_deflection_y_mm":amount,
                                                "overlap_mm3":hit.Volume(),"hit_bounds":bounds(hit)})
    cq.exporters.export(flexed,str(HERE/"right-deflected-clearance-witness.step"))
    report["all_reported_native_readings_clear"]=all(r["max_prism_overlap_mm3"]<1e-5 and r["initial_overlap_mm3"]<1e-5
        for r in report["continuous_rigid_sweeps"]) and all(r["overlap_mm3"]<1e-5 for r in report["elastic_wall_clearance"])
    (HERE/"joint-motion-checks.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report["deflected_wall_model"]),flush=True)


if __name__=="__main__":main()
