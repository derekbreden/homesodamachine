"""C2 tube-snap control and two smaller bores on one 3 mm comparison floor.

Run manually with tools/cad-venv/bin/python. Generates experimental parts only;
does not change production geometry or submit a printer job.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import math

import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MATRIX_REPORT=HERE/'retention-matrix-geometry.json'
MATRIX_SOURCE=HERE/'retention_matrix.py'
MATRIX=json.loads(MATRIX_REPORT.read_text())
C2=next(s for s in MATRIX['samples'] if s['label']=='C2')
ORIGINAL_REPORT=HERE/'geometry-report.json'
DIAMETER_STEP=json.loads(ORIGINAL_REPORT.read_text())['step_in_diameter_mm']
THICKNESS=C2['spring_wall_mm']
TIP=math.radians(C2['tip_angle_deg'])
TUBE_OD=MATRIX['tube_nominal_od_mm']
SPAN=MATRIX['clip_span_y_mm']
FLOOR=(60.,16.,3.)
AXIS_ABOVE_FLOOR=MATRIX['tube_axis_above_floor_mm']
RELIEF=.48
SAMPLES=((0,C2['bore_diameter_mm'],-20.),
         (1,round(C2['bore_diameter_mm']-DIAMETER_STEP,2),0.),
         (2,round(C2['bore_diameter_mm']-2*DIAMETER_STEP,2),20.))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(lo,hi):
    return cq.Solid.makeBox(*[b-a for a,b in zip(lo,hi)],cq.Vector(*lo))


def signature(shape):
    b=shape.BoundingBox()
    return dict(valid=shape.isValid(),solids=len(shape.Solids()),volume_mm3=abs(shape.Volume()),
                bounds_mm=[getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')])


def clip(diameter,x):
    ri,ro=diameter/2,diameter/2+THICKNESS
    rm,nose=ri+THICKNESS/2,THICKNESS/2
    z=FLOOR[2]+AXIS_ABOVE_FLOOR
    plane=cq.Plane(origin=(x,-SPAN/2,z),xDir=(1,0,0),normal=(0,1,0))
    def xy(r,t):return(r*math.sin(t),r*math.cos(t))
    def add(a,b):return tuple(u+v for u,v in zip(a,b))
    p0,p1,p2,p3=xy(ro,-TIP),xy(ro,TIP),xy(ri,TIP),xy(ri,-TIP)
    cp,cn=xy(rm,TIP),xy(rm,-TIP)
    qp,qn=(math.cos(TIP),-math.sin(TIP)),(math.cos(-TIP),-math.sin(-TIP))
    ring=(cq.Workplane(plane).moveTo(*p0).threePointArc((0,ro),p1)
          .threePointArc(add(cp,(nose*qp[0],nose*qp[1])),p2)
          .threePointArc((0,ri),p3)
          .threePointArc(add(cn,(-nose*qn[0],-nose*qn[1])),p0).close().extrude(SPAN).val())
    root=box((x-ro,-SPAN/2,FLOOR[2]),(x+ro,SPAN/2,z))
    bore=cq.Solid.makeCylinder(ri,SPAN+.2,cq.Vector(x,-SPAN/2-.1,z),cq.Vector(0,1,0))
    body=ring.fuse(root).cut(bore).clean()
    ray=cq.Edge.makeLine(cq.Vector(x-ro-1,0,z),cq.Vector(x+ro+1,0,z))
    section=sorted(v.Center().x-x for v in body.intersect(ray).Vertices())
    expected=(-ro,-ri,ri,ro)
    if len(section)!=4 or any(abs(a-b)>1e-5 for a,b in zip(section,expected)):
        raise ValueError('Native diameter or wing thickness differs from this sample')
    mouth=2*(rm*math.sin(TIP)-nose)
    return body,dict(centre_x_mm=x,centre_y_mm=0.,tube_axis_z_mm=z,
        bore_diameter_mm=diameter,bore_radius_mm=ri,outer_radius_mm=ro,
        spring_wall_mm=THICKNESS,tip_angle_deg=math.degrees(TIP),
        circular_wrap_deg=2*math.degrees(TIP),mouth_width_mm=mouth,
        nominal_radial_allowance_mm=(diameter-TUBE_OD)/2,
        nominal_catch_per_jaw_mm=(TUBE_OD-mouth)/2,
        native_mid_bore_section_x_mm=section,native_clip=signature(body))


def main():
    if sha(MATRIX_SOURCE)!=MATRIX['source_sha256'] or DIAMETER_STEP!=.10:
        raise ValueError('The C2 source and organizer tuning increment must remain bound')
    parts=HERE/'parts'
    parts.mkdir(parents=True,exist_ok=True)
    body=box((-FLOOR[0]/2,-FLOOR[1]/2,0),(FLOOR[0]/2,FLOOR[1]/2,FLOOR[2]))
    samples=[]
    control=None
    for steps,diameter,x in SAMPLES:
        native,reading=clip(diameter,x)
        body=body.fuse(native)
        label=f'{diameter:.2f}'
        letters=(cq.Workplane('XY',origin=(x,-6.25,FLOOR[2]-.02))
                 .text(label,2.6,RELIEF+.02,font='Arial',kind='bold',
                       halign='center',valign='center',combine=False).val())
        body=body.fuse(letters)
        samples.append(dict(label=label,steps_down=steps,
                            reference='C2' if steps==0 else f'C2 minus {steps} diameter step(s)',**reading))
        if steps==0:
            spec=importlib.util.spec_from_file_location('c2_matrix_reference',MATRIX_SOURCE)
            previous=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(previous)
            expected,_=previous.clip(THICKNESS,previous.REFERENCE_TIP+math.radians(5),x)
            missing=abs(expected.cut(native).Volume())
            extra=abs(native.cut(expected).Volume())
            if missing+extra>1e-5:
                raise ValueError('The control must preserve the physically selected C2 clip')
            control=dict(reference='C2',source=str(MATRIX_SOURCE.relative_to(ROOT)),
                         source_sha256=sha(MATRIX_SOURCE),missing_mm3=missing,extra_mm3=extra,
                         scope='Native clip geometry, including filled root and rounded noses; floor labels are diameter identities.')
    body=body.clean()
    if not body.isValid() or len(body.Solids())!=1:
        raise ValueError('The comparison floor and three clips must be one connected native solid')
    stem='tube-snap-c2-three-bores'
    stl,step=parts/f'{stem}.stl',parts/f'{stem}.step'
    cq.exporters.export(body,str(stl),tolerance=.025,angularTolerance=.10)
    cq.exporters.export(body,str(step))
    report=dict(scope='One experimental C2 control and two smaller bore diameters. No production change.',
        source=str(Path(__file__).relative_to(ROOT)),source_sha256=sha(Path(__file__)),
        reference_sample='C2',wing_thickness_mm=THICKNESS,tip_angle_deg=math.degrees(TIP),
        step_in_diameter_mm=DIAMETER_STEP,tube_nominal_od_mm=TUBE_OD,
        floor_xyz_mm=list(FLOOR),tube_axis_above_floor_mm=AXIS_ABOVE_FLOOR,
        clip_span_y_mm=SPAN,samples=samples,control=control,native=signature(body),
        files={str(p.relative_to(ROOT)):sha(p) for p in (stl,step)},
        provenance={str(p.relative_to(ROOT)):sha(p) for p in (MATRIX_SOURCE,MATRIX_REPORT,ORIGINAL_REPORT)},
        labels=dict(placement='Front band, left to right: 6.55 / 6.45 / 6.35',raised_mm=RELIEF),
        long_tube_access='One transverse row across X. Each tube axis runs along Y; a long straight tube meets only its selected clip.',
        print_pose='The complete 3 mm floor lies flat on the bed; mouths face upward.',
        physical_result_pending=True)
    (HERE/'c2-bore-geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('files','provenance')},indent=2),flush=True)


if __name__=='__main__':
    main()
