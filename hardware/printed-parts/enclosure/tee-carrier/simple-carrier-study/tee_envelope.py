"""Verified conservative tee cylinders, with exact rectilinear swept unions."""
import cadquery as cq
from build_concept import box


def cylinder(axis,center,span,r=8.25):
    p=list(center)
    p[axis]=span[0]
    direction=[0,0,0];direction[axis]=1
    return cq.Solid.makeCylinder(r,span[1]-span[0],cq.Vector(*p),cq.Vector(*direction))


def dimensions(shape):
    b=shape.BoundingBox()
    return (b.xmin+b.xmax)/2,b.ymax-8.25,(b.zmin+b.zmax)/2,(b.zmin,b.zmax),(b.ymin,b.ymax-8.25)


def envelope(shape):
    x,y,z,zspan,yspan=dimensions(shape)
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


def sweep(shape,start,end):
    # Sweep the stationary obstacle through the opposite carrier translation.
    x,y,z,zspan,yspan=dimensions(shape)
    center=(x-start[0],y-start[1],z-start[2])
    delta=tuple(a-b for a,b in zip(start,end))
    return sweep_cylinder(2,center,(zspan[0]-start[2],zspan[1]-start[2]),delta).fuse(
        sweep_cylinder(1,center,(yspan[0]-start[1],yspan[1]-start[1]),delta)).clean()
