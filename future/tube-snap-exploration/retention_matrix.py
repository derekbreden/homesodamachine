"""Nine retention trials on three movable strips; all bores are R3.275 mm.

Rows A/B/C vary leaf thickness. Columns 1/2/3 vary each leaf's circular
wrap angle. A1 repeats the smallest-bore clip geometry from the first trial.
Each strip has only one transverse row, allowing a long tube along Y.
Run manually; this generator neither changes production nor submits a print.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BORE_RADIUS = 3.275
TUBE_OD = 6.35
FLOOR = (60.,16.,3.)
AXIS_ABOVE_FLOOR = 4.5
SPAN = 8.
REFERENCE_THICKNESS = 1.44
REFERENCE_CATCH = .45
REFERENCE_MID_RADIUS = BORE_RADIUS+REFERENCE_THICKNESS/2
REFERENCE_TIP = math.pi-math.asin(
    (TUBE_OD/2-REFERENCE_CATCH+REFERENCE_THICKNESS/2)/REFERENCE_MID_RADIUS)
ROWS = (("A",1.44),("B",1.92),("C",2.40))
COLUMNS = ((1,0.,-20.),(2,5.,0.),(3,10.,20.))
RELIEF = .48


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(lo,hi):
    return cq.Solid.makeBox(*[b-a for a,b in zip(lo,hi)],cq.Vector(*lo))


def signature(shape):
    b=shape.BoundingBox()
    return dict(valid=shape.isValid(),solids=len(shape.Solids()),volume_mm3=abs(shape.Volume()),
                bounds_mm=[getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')])


def clip(thickness,tip,x):
    ri,ro=BORE_RADIUS,BORE_RADIUS+thickness
    rm,nose=BORE_RADIUS+thickness/2,thickness/2
    z=FLOOR[2]+AXIS_ABOVE_FLOOR
    plane=cq.Plane(origin=(x,-SPAN/2,z),xDir=(1,0,0),normal=(0,1,0))
    def xy(r,t):return(r*math.sin(t),r*math.cos(t))
    def add(a,b):return tuple(u+v for u,v in zip(a,b))
    p0,p1,p2,p3=xy(ro,-tip),xy(ro,tip),xy(ri,tip),xy(ri,-tip)
    cp,cn=xy(rm,tip),xy(rm,-tip)
    qp,qn=(math.cos(tip),-math.sin(tip)),(math.cos(-tip),-math.sin(-tip))
    c=(cq.Workplane(plane).moveTo(*p0).threePointArc((0,ro),p1)
       .threePointArc(add(cp,(nose*qp[0],nose*qp[1])),p2)
       .threePointArc((0,ri),p3)
       .threePointArc(add(cn,(-nose*qn[0],-nose*qn[1])),p0).close().extrude(SPAN).val())
    root=box((x-ro,-SPAN/2,FLOOR[2]),(x+ro,SPAN/2,z))
    bore=cq.Solid.makeCylinder(ri,SPAN+.2,cq.Vector(x,-SPAN/2-.1,z),cq.Vector(0,1,0))
    body=c.fuse(root).cut(bore).clean()
    ray=cq.Edge.makeLine(cq.Vector(x-ro-1,0,z),cq.Vector(x+ro+1,0,z))
    measured=sorted(v.Center().x-x for v in body.intersect(ray).Vertices())
    if len(measured)!=4 or any(abs(a-b)>1e-5 for a,b in zip(measured,[-ro,-ri,ri,ro])):
        raise ValueError("Native bore section differs from the fixed radius")
    mouth=2*(rm*math.sin(tip)-nose)
    return body,dict(centre_x_mm=x,centre_y_mm=0.,tube_axis_z_mm=z,
                     bore_diameter_mm=2*ri,bore_radius_mm=ri,outer_radius_mm=ro,
                     spring_wall_mm=thickness,tip_angle_deg=math.degrees(tip),
                     circular_wrap_deg=2*math.degrees(tip),mouth_width_mm=mouth,
                     nominal_catch_per_jaw_mm=(TUBE_OD-mouth)/2,
                     native_mid_bore_section_x_mm=measured,
                     native_clip=signature(body))


def control_comparison(control):
    source=HERE/"tube_snap_trial.py"
    spec=importlib.util.spec_from_file_location("tube_snap_original_trial",source)
    original=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(original)
    expected,_=original.snap(6.55,-20.)
    missing=abs(expected.cut(control).Volume())
    extra=abs(control.cut(expected).Volume())
    if missing+extra>1e-5:
        raise ValueError("A1 must preserve the tested smallest-bore clip")
    return dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),
                missing_mm3=missing,extra_mm3=extra,
                scope="A1 clip geometry only; new strip floor and raised identity labels are different.")


def main():
    parts=HERE/"parts"
    parts.mkdir(parents=True,exist_ok=True)
    rows,samples,files=[],[],{}
    control=None
    for row,thickness in ROWS:
        body=box((-FLOOR[0]/2,-FLOOR[1]/2,0),(FLOOR[0]/2,FLOOR[1]/2,FLOOR[2]))
        for column,extra,x in COLUMNS:
            label=f"{row}{column}"
            native,reading=clip(thickness,REFERENCE_TIP+math.radians(extra),x)
            body=body.fuse(native)
            # Raised identification leaves the full 3 mm structural floor intact.
            letters=(cq.Workplane("XY",origin=(x,-6.25,FLOOR[2]-.02))
                     .text(label,2.6,RELIEF+.02,font="Arial",kind="bold",
                           halign="center",valign="center",combine=False).val())
            body=body.fuse(letters)
            samples.append(dict(label=label,row=row,column=column,
                                extra_wrap_per_wing_deg=extra,**reading))
            if label=="A1":control=control_comparison(native)
        body=body.clean()
        if not body.isValid() or len(body.Solids())!=1:
            raise ValueError(f"Strip {row} must be one connected native solid")
        stem=f"tube-snap-row-{row.lower()}-print"
        stl,step=parts/f"{stem}.stl",parts/f"{stem}.step"
        cq.exporters.export(body,str(stl),tolerance=.025,angularTolerance=.10)
        cq.exporters.export(body,str(step))
        files.update({str(p.relative_to(ROOT)):sha(p) for p in (stl,step)})
        rows.append(dict(row=row,spring_wall_mm=thickness,
                         source_stl=str(stl.relative_to(ROOT)),
                         source_step=str(step.relative_to(ROOT)),
                         floor_xyz_mm=list(FLOOR),native=signature(body)))
    report=dict(scope="Two-axis physical retention experiment on three movable strips; no production change.",
                source=str(Path(__file__).relative_to(ROOT)),source_sha256=sha(Path(__file__)),
                bore_radius_mm=BORE_RADIUS,bore_diameter_mm=2*BORE_RADIUS,
                tube_nominal_od_mm=TUBE_OD,reference_tip_angle_deg=math.degrees(REFERENCE_TIP),
                row_axis="Wing thickness: A=1.44, B=1.92, C=2.40 mm",
                column_axis="Additional circular wrap per wing: 1=0, 2=5, 3=10 degrees",
                rows=rows,samples=samples,files=files,control=control,
                tube_axis_above_floor_mm=AXIS_ABOVE_FLOOR,clip_span_y_mm=SPAN,
                labels=dict(placement="Front band of each strip",raised_mm=RELIEF,
                            purpose="Permanent test identity after separating and moving the three strips"),
                long_tube_access="Each strip has just one row of clips across X. Separate the strips before testing; a straight tube along Y then meets only the selected clip.",
                print_pose="Three 3 mm floors flat on the bed, mouths upward; same layer direction as the first trial.",
                design_basis="Hold the bore and tube-axis height fixed. The outer radius and rounded-nose radius follow wall thickness; circular end angle sets the wrap axis. Mouth width is a measured consequence of both axes, not a separately tuned parameter.",
                physical_result_pending=True)
    (HERE/"retention-matrix-geometry.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"rows":rows,"samples":[{k:s[k] for k in ('label','bore_radius_mm','spring_wall_mm','tip_angle_deg','mouth_width_mm')}for s in samples],"control":control},indent=2),flush=True)


if __name__=="__main__":
    main()
