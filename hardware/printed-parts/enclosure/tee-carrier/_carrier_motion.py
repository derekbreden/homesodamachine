"""Native continuous straight-motion and snap-wall clearance witnesses."""
import cadquery as cq
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec
from _simple_carrier import box,bounds



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



def cylinder(axis,center,span,r=8.25):
    p=list(center)
    p[axis]=span[0]
    direction=[0,0,0];direction[axis]=1
    return cq.Solid.makeCylinder(r,span[1]-span[0],cq.Vector(*p),cq.Vector(*direction))


def tee_dimensions(shape):
    b=shape.BoundingBox()
    return (b.xmin+b.xmax)/2,b.ymax-8.25,(b.zmin+b.zmax)/2,(b.zmin,b.zmax),(b.ymin,b.ymax-8.25)


def tee_envelope(shape):
    x,y,z,zspan,yspan=tee_dimensions(shape)
    return cylinder(2,(x,y,z),zspan).fuse(cylinder(1,(x,y,z),yspan)).clean()


def sweep_cylinder(axis,center,span,delta,r=8.25):
    active=[i for i,v in enumerate(delta) if abs(v)>1e-8]
    assert len(active)==1,delta
    motion=active[0]
    if motion==axis:
        return cylinder(axis,center,(span[0]+min(0,delta[axis]),span[1]+max(0,delta[axis])),r)
    a=cylinder(axis,center,span,r)
    bounds=[]
    for k in range(3):
        if k==axis:bounds.append(span)
        elif k==motion:bounds.append((center[k]+min(0,delta[k]),center[k]+max(0,delta[k])))
        else:bounds.append((center[k]-r,center[k]+r))
    return a.fuse(a.translate(delta)).fuse(box(*bounds)).clean()


def tee_sweep(shape,start,end):
    # Sweep the stationary obstacle through the opposite carrier translation.
    x,y,z,zspan,yspan=tee_dimensions(shape)
    center=(x-start[0],y-start[1],z-start[2])
    delta=tuple(a-b for a,b in zip(start,end))
    return sweep_cylinder(2,center,(zspan[0]-start[2],zspan[1]-start[2]),delta).fuse(
        sweep_cylinder(1,center,(yspan[0]-start[1],yspan[1]-start[1]),delta)).clean()


def joint_checks(spec,parts):
    """Continuous structural placement and geometric elastic-wall witness."""
    aft=spec.aft_limit_offset_y;stage=spec.entry_staging_y
    shift=spec.entry_shift_x;inset=spec.entry_shoulder_inset_x
    left=parts['left'].translate((0,aft,0));right=parts['right_structural']
    wall,lip=parts['retention_wall'],parts['retention_lip']
    poses=[(-shift,210,70),(-shift,stage,70),(-shift,stage,0),(-inset,stage,0),(-inset,aft,0),(0,aft,0)]
    sweeps=[swept_overlap(right,a,b,left) for a,b in zip(poses,poses[1:])]
    flex=loft_wall(wall,lip)
    elastic=[]
    for dx in (inset,2.5,1.5,.5,.25):
        elastic.append({'inset_x_mm':dx,'deflection_y_mm':2.3,
                        'overlap_mm3':right.fuse(flex).translate((-dx,aft,0)).intersect(left).Volume()})
    for amount in (2.3,1.5,.5,0):
        nose=loft_wall(wall,lip,amount) if amount else wall.fuse(lip)
        elastic.append({'inset_x_mm':.25,'deflection_y_mm':amount,
                        'overlap_mm3':nose.translate((-.25,aft,0)).intersect(left).Volume()})
    return {'rigid_sweeps':sweeps,'elastic_wall':elastic,
            'clear':all(r['initial_overlap_mm3']<1e-5 and r['max_prism_overlap_mm3']<1e-5 for r in sweeps)
                    and all(r['overlap_mm3']<1e-5 for r in elastic),
            'elastic_scope':'Geometric 2.3 mm free-tip displacement, fixed root; no force, strain or fatigue qualification.'}


def loading_checks(spec,parts,wall,tees):
    """Carrier with preloaded springs, followed by pusher removal, in the loose wall."""
    rows=[];aft=spec.aft_limit_offset_y;stage=spec.entry_staging_y
    containment=[{'tee':name,'outside_mm3':s.cut(tee_envelope(s)).Volume()} for name,s in tees]
    if any(r['outside_mm3']>1e-5 for r in containment):
        raise ValueError('Native tee exceeds its declared swept-cylinder envelope')
    def record(label,s,start,end,obstacle):
        rows.append({'check':label,**swept_overlap(s,start,end,obstacle)})
    def ycyl(x,d,y0,y1):
        return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(x,y0,spec.spring_z),cq.Vector(0,1,0))
    for side,key in ((-1,'left'),(1,'right_structural')):
        body=parts[key];shift=-side*spec.entry_shift_x;inset=-side*spec.entry_shoulder_inset_x
        poses=[(shift,210,spec.entry_lift_z),(shift,stage,spec.entry_lift_z),
               (shift,stage,0),(inset,stage,0),(inset,aft,0),(0,aft,0)]
        tip=spec.spring_bore_floor_y-spec.spring_load_length;x=spec.spring_x;z=spec.spring_z
        tool=ycyl(x,6.3,tip-.6,tip).fuse(box((x-10,x),(tip-.6,tip),(z-.5,z+.5)))
        held=ycyl(x,6.5,tip,spec.spring_bore_floor_y).fuse(tool)
        if side<0:tool=tool.mirror('YZ');held=held.mirror('YZ')
        for start,end in zip(poses,poses[1:]):
            record(f'half {side:+} structural wall route',body,start,end,wall)
            record(f'half {side:+} held spring and pusher',held,start,end,wall)
            for name,tee in tees:
                swept=tee_sweep(tee,start,end);v=body.intersect(swept).Volume()
                rows.append({'check':f'half {side:+} seated {name} envelope','start':start,'end':end,
                             'initial_overlap_mm3':0,'max_prism_overlap_mm3':v,'nonzero':[]})
        withdraw=spec.spring_x-max(spec.tee_xs)
        path=[(0,aft,0),(-side*withdraw,aft,0),(-side*withdraw,aft,spec.entry_lift_z)]
        blockers=wall.fuse(body.translate((0,aft,0)))
        for start,end in zip(path,path[1:]):record(f'half {side:+} pusher removal',tool,start,end,blockers)
    elastic=parts['retention_wall'].fuse(parts['retention_lip'])
    shift=spec.entry_shift_x;inset=spec.entry_shoulder_inset_x
    poses=[(-shift,210,70),(-shift,stage,70),(-shift,stage,0),(-inset,stage,0),(-inset,aft,0),(0,aft,0)]
    for start,end in zip(poses,poses[1:]):record('nominal retaining-wall route',elastic,start,end,wall)
    b=elastic.BoundingBox()
    full=box((b.xmin-inset,b.xmax),(b.ymin+aft,b.ymax+aft+4.3),(b.zmin,b.zmax))
    volume=full.intersect(wall).Volume()
    rows.append({'check':'final retaining-wall deflection envelope','initial_overlap_mm3':0,
                 'max_prism_overlap_mm3':volume,'nonzero':[]})
    air=spec.spring_z-3.25-max(s.BoundingBox().zmax for _,s in tees)
    return {'rows':rows,'tee_envelope_containment':containment,
            'spring_tool_to_tee_vertical_air_mm':air,
            'clear':air>0 and all(r['initial_overlap_mm3']<1e-5 and r['max_prism_overlap_mm3']<1e-5 for r in rows),
            'scope':'Native rigid motions and closed-cup preload geometry. Springs deform and printed fit/force remain full-enclosure trial observations.'}
