"""Reusable nine-and-a-half-millimetre split seats with blind M3 retention.

Local X is the direction into the fixed print, local Y follows the tube,
and local Z selects the side on which the two removable-key screws sit.
The three-millimetre key opens the bearing. A negative split datum can
require axial threading while the purchased tube's end remains free.
"""
import math,cadquery as cq

def box(x0,y0,z0,x1,y1,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def split_seat(centre, *, normal=(1,0,0), axis=(0,1,0),
               diameter=6.35, length=9.5, slip=.15,
               split=-1.075, root=7.175, screw_side=1, screw_pitch=None,
               key_thickness=3., screw_radial_offset=5.5,
               screw_axial_stations=None):
    """Return fixed bearing, removable key, both screws, and exact pilots.

    ``split`` and ``root`` are local X datums relative to the tube centre.
    Their separation must be at least8.25mm: a5.25mm blind insert cavity
    followed by3mm of closed print stock. The fixed bearing is joined to
    the declared parent print before its pilot cutters are re-applied.
    """
    if root-split<8.25-1e-8:
        raise ValueError('Blind M3 seat needs5.25mm pilot plus3mm closed stock')
    if length<9.5-1e-8:
        raise ValueError('Tube bearing section must be at least9.5mm')
    if key_thickness<3-1e-8:raise ValueError('Removable key requires at least3mm stock')
    if screw_radial_offset<5.-1e-8:raise ValueError('A4mm pilot requires at least3mm radial tube-bore stock')
    r=diameter/2+slip;outer=r+3.;half=length/2
    bore=cq.Solid.makeCylinder(r,length+2,cq.Vector(0,-half-1,0),cq.Vector(0,1,0))
    ring=cq.Solid.makeCylinder(outer,length,cq.Vector(0,-half,0),cq.Vector(0,1,0)).cut(bore)
    fixed=ring.intersect(box(split,-half,-outer,root,half,outer))
    key=ring.intersect(box(-outer,-half,-outer,split,half,outer))
    pitch=half+3.75 if screw_pitch is None else screw_pitch
    if pitch<3.5:raise ValueError('Two4mm insert cavities need at least3mm inter-hole stock')
    axial=[-pitch,pitch]if screw_axial_stations is None else list(screw_axial_stations)
    if len(axial)!=2 or axial[1]-axial[0]<7.-1e-8:
        raise ValueError('Two4mm insert cavities need at least3mm inter-hole stock')
    bossz=screw_side*(r+screw_radial_offset)
    # A continuous3mm axial bridge links each8mm ear to the9.5mm bearing.
    zlo,zhi=sorted((screw_side*r,screw_side*(r+3.)))
    ylo=min(-half,min(axial)-4.);yhi=max(half,max(axial)+4.)
    fixed=fixed.fuse(box(split,ylo,zlo,root,yhi,zhi))
    key=key.fuse(box(split-key_thickness,ylo,zlo,split,yhi,zhi))
    screws=[];pilots=[];holes=[]
    for y in axial:
        fixed=fixed.fuse(box(split,y-4,bossz-4,root,y+4,bossz+4))
        key=key.fuse(box(split-key_thickness,y-4,bossz-4,split,y+4,bossz+4))
        pilot=cq.Solid.makeCylinder(2.,5.25,cq.Vector(split,y,bossz),cq.Vector(1,0,0))
        hole=cq.Solid.makeCylinder(1.6,key_thickness+.01,cq.Vector(split-key_thickness,y,bossz),cq.Vector(1,0,0))
        fixed=fixed.cut(pilot);key=key.cut(hole)
        shaft=cq.Solid.makeCylinder(1.5,8.,cq.Vector(split-key_thickness,y,bossz),cq.Vector(1,0,0))
        head=cq.Solid.makeCylinder(2.75,3.,cq.Vector(split-key_thickness-3,y,bossz),cq.Vector(1,0,0))
        screws.append(shaft.fuse(head));pilots.append(pilot);holes.append(hole)
    fixed=fixed.cut(bore).clean();key=key.cut(bore).clean()
    n=cq.Vector(*normal).normalized();u=cq.Vector(*axis).normalized()
    if abs(n.dot(u))>1e-8:raise ValueError('Seat normal must be perpendicular to its tube axis')
    v=n.cross(u).normalized();p=cq.Vector(*centre)
    location=cq.Location(cq.Plane(origin=p,xDir=n,normal=v))
    world=lambda s:s.moved(location)
    result={'fixed':world(fixed),'key':world(key),
            'screws':[world(q)for q in screws],
            'pilots':[world(q)for q in pilots],
            'key_holes':[world(q)for q in holes],
            'properties':{'bearing_length_mm':length,'bore_radius_mm':r,
                          'radial_stock_mm':3.,'key_thickness_mm':key_thickness,
                          'blind_pilot_depth_mm':5.25,'closed_pilot_stock_mm':root-split-5.25,
                          'screw_spec':'2×M3×8 socket heads',
                          'threaded_engagement_mm':8-key_thickness,
                          'insert_length_mm':4.,'pilot_tip_reserve_mm':5.25-8+key_thickness,
                          'centre_mm':list(centre),'normal':list(normal),'tube_axis':list(axis),
                          'split_local_mm':split,'root_local_mm':root,
                          'screw_side':screw_side,'screw_half_pitch_mm':pitch,
                          'screw_axial_stations_mm':axial,
                          'screw_radial_offset_mm':screw_radial_offset,
                          'screw_boss_local_mm':bossz,
                          'lateral_mouth_mm':2*math.sqrt(r*r-split*split),
                          'rigid_lateral_release':2*math.sqrt(r*r-split*split)>=diameter,
                          'assembly':'Thread while the tube end is free if the exact split mouth is narrower than the tube.'}}
    for label in ['fixed','key']:
        if not result[label].isValid()or len(result[label].Solids())!=1:
            raise ValueError(label+' is not one valid solid')
    return result
