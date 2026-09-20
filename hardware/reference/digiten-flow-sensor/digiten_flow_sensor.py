"""Measured external reference for the DIGITEN inline flow sensor.

Millimetres. X is the port axis, Y points toward the label, Z toward the
pigtail. The origin is midway between the two collet faces on the port axis.
The round housing axis is offset toward +Z. Hidden turbine, seals, electronics,
threads and the flexible lead are not reconstructed.
"""
import sys
import math
import json
import hashlib
from pathlib import Path
import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hardware / 'scripts'))
sys.path.insert(0, str(_hardware.parent / 'tools'))
from _cadq_export import export_assembly
from docgen import substitute_md
from _materials import C_DIGITEN, C_DIGITEN_CLIP, M_MOULDED_BLACK, M_ZINC_PLATED_STEEL

# External dimensions fitted to MINI 2 observations; see scan-evidence.json.
# Interface stations are on the collet faces, not at the offset housing centre.
port_face = 30.5
port_dia = 18.3                 # largest fixed collar diameter
port_neck_radius = 7.95
port_neck_end = 19.6
port_collar_end = 26.8
port_collar_radii = (8.95, 9.15)
port_collet_radius = 5.0
port_mouth_radius = 3.25
port_mouth_depth = 6.0          # visible mouth only; no internal insertion stop
body_dia = 35.0                 # outer cover flange
body_len = 28.3                 # overall depth, including screw heads
body_center_x = 0.0
body_center_z = 8.9
label_y = 18.7
underside_y = -9.4
boss_x = 12.5
boss_z = 14.0
boss_radius = 3.45
boss_y_range = (0.0, 17.2)
screw_head_radius = 2.65
screw_head_y_range = (17.2, 18.9)
wire_root = (0.0, 14.8, 26.5)
wire_root_width = 6.0
wire_root_depth = 3.0
wire_boss_dia = wire_root_width # compatibility: the lead root is a slot
wire_boss_len = 1.5


def inlet():
    return (-port_face, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    return (port_face, 0.0, 0.0), (1.0, 0.0, 0.0)


def wire_exit():
    return wire_root, (0.0, 0.0, 1.0)


def mounting_profile(sign):
    """Fixed port exterior from the housing outward: (start, end, r0, r1).

    Distances are measured outward from the origin along sign*X. The separate
    collet starts at port_collar_end and is outside these bearing sections.
    """
    return ((15.5, port_neck_end, port_neck_radius, port_neck_radius),
            (port_neck_end, port_collar_end, *port_collar_radii))


def _cylinder_y(r, y0, y1, x=body_center_x, z=body_center_z):
    return cq.Solid.makeCylinder(r, y1-y0, cq.Vector(x,y0,z), cq.Vector(0,1,0))


def _cone_y(r0, r1, y0, y1):
    return cq.Solid.makeCone(r0,r1,y1-y0,cq.Vector(body_center_x,y0,body_center_z),cq.Vector(0,1,0))


def _bosses(y0, y1, r=boss_radius):
    return [_cylinder_y(r,y0,y1,body_center_x+sx*boss_x,body_center_z+sz*boss_z)
            for sx in (-1,1) for sz in (-1,1)]


def _union(parts):
    shape=parts[0]
    for part in parts[1:]:
        shape=shape.fuse(part)
    return shape.clean()


def build_body_disk():
    """Lower moulding, drafted rotor housing, cover flange and screw posts."""
    main=_union([_cone_y(15.1,15.45,-8.1,7.3),
                 _cone_y(13.9,15.1,underside_y,-8.1),
                 _cylinder_y(17.5,7.3,10.6),
                 *_bosses(boss_y_range[0],10.6)])
    # Six open recesses leave the observed centre, rim and radial bearing ribs.
    recess=_cylinder_y(12.7,underside_y-.1,-8.45)
    core=_cylinder_y(2.9,underside_y-.2,-7.9)
    ribs=[]
    for angle in range(0,180,60):
        rib=cq.Workplane('XY').box(26,1.7,1.7).val()
        # Initial long axis X; box depth is Y and thickness Z.
        rib=rib.rotate((0,0,0),(0,1,0),angle).translate((body_center_x,-8.65,body_center_z))
        ribs.append(rib)
    recess=recess.cut(_union([core,*ribs]))
    return main.cut(recess).clean()


def build_port(sign):
    axis=cq.Vector(sign,0,0)
    def cylinder(r,a,b):
        return cq.Solid.makeCylinder(r,b-a,cq.Vector(sign*a,0,0),axis)
    collar=cq.Solid.makeCone(*port_collar_radii,port_collar_end-port_neck_end,
                            cq.Vector(sign*port_neck_end,0,0),axis)
    root=cq.Solid.makeCone(5.2,6.25,1.5,cq.Vector(sign*10.5,0,0),axis)
    shoulder=cq.Solid.makeCone(6.25,port_neck_radius,2.0,cq.Vector(sign*13.5,0,0),axis)
    outer=_union([root,cylinder(6.25,12.0,13.5),shoulder,
                  cylinder(port_neck_radius,15.5,port_neck_end),collar,
                  cylinder(port_collet_radius,port_collar_end,port_face)])
    mouth=cylinder(port_mouth_radius,port_face-port_mouth_depth,port_face+.1)
    return outer.cut(mouth).clean()


def build_lock_clip(sign):
    """One observed locking-clip position per end, from underside passes 04/05."""
    centre=165.0 if sign<0 else 195.0
    a0,a1=map(math.radians,(centre-23,centre+23))
    am=(a0+a1)/2
    def point(r,a):return (r*math.cos(a),r*math.sin(a))
    ear=(cq.Workplane('YZ').workplane(offset=sign*27.0)
         .moveTo(*point(6.65,a0)).threePointArc(point(6.65,am),point(6.65,a1))
         .lineTo(*point(4.9,a1)).threePointArc(point(4.9,am),point(4.9,a0))
         .close().extrude(sign*3.1).val())
    ring=cq.Solid.makeCylinder(5.65,1.8,cq.Vector(sign*27.0,0,0),cq.Vector(sign,0,0))
    bore=cq.Solid.makeCylinder(4.9,2.0,cq.Vector(sign*26.9,0,0),cq.Vector(sign,0,0))
    return ring.cut(bore).fuse(ear).clean()


def build_band():
    return _union([_cylinder_y(17.45,10.6,14.8),*_bosses(10.6,14.8)])


def build_cover():
    return _union([_cylinder_y(17.5,14.8,17.2),
                   _cone_y(17.5,13.2,17.2,label_y),
                   *_bosses(14.8,17.2)])


def build_wire_boss():
    return cq.Workplane('XY').box(wire_root_width,wire_root_depth,wire_boss_len).val().translate(
        (wire_root[0],wire_root[1],wire_root[2]-wire_boss_len/2))


def build_screws():
    return cq.Compound.makeCompound(_bosses(*screw_head_y_range,r=screw_head_radius))


_PARTS=[('lower-housing',build_body_disk,C_DIGITEN),
        ('inlet',lambda:build_port(-1),C_DIGITEN),
        ('outlet',lambda:build_port(1),C_DIGITEN),
        ('sensor-band',build_band,M_MOULDED_BLACK),
        ('inlet-lock-clip',lambda:build_lock_clip(-1),C_DIGITEN_CLIP),
        ('outlet-lock-clip',lambda:build_lock_clip(1),C_DIGITEN_CLIP),
        ('label-cover',build_cover,C_DIGITEN),
        ('wire-root',build_wire_boss,M_MOULDED_BLACK),
        ('screw-heads',build_screws,M_ZINC_PLATED_STEEL)]


def build_assembly():
    result=cq.Assembly(name='digiten-flow-sensor')
    for name,builder,color in _PARTS:
        result.add(builder(),name=name,color=color)
    return result


def build_scene():
    return cq.Compound.makeCompound([builder() for _,builder,_ in _PARTS])


def main():
    shape=build_scene()
    solids=shape.Solids()
    invalid=[i for i,solid in enumerate(solids)
             if not solid.isValid() or solid.Volume()<=0]
    if not solids or invalid or not shape.isValid():
        raise ValueError(f'Invalid DIGITEN reference solid(s): {invalid}')
    export_assembly(build_assembly(),str(_here.parent/'digiten-flow-sensor.step'))
    bb=shape.BoundingBox()
    report={'executed_producer_sha256':hashlib.sha256(_here.read_bytes()).hexdigest(),
            'hash_scope':'Executed producer bytes; Bazel normalizes Python source before execution. The scan comparison separately hashes the full repository source.',
            'valid_solids':len(solids),'faces':sum(len(s.Faces()) for s in solids),
            'bounds_mm':{'x':[bb.xmin,bb.xmax],'y':[bb.ymin,bb.ymax],'z':[bb.zmin,bb.zmax]},
            'port_faces_x_mm':[-port_face,port_face],
            'fixed_collar_extent_abs_x_mm':[port_neck_end,port_collar_end],
            'fixed_collar_radii_mm':list(port_collar_radii),
            'body_center_z_mm':body_center_z,'wire_root_mm':list(wire_root)}
    (_here.parent/'model-check.json').write_text(json.dumps(report,indent=2)+'\n')
    substitute_md(_here.parent/'README.md',variables={
        'FLOW_BODY_DIA':f'{body_dia:g}','BODY_LEN':f'{body_len:g}',
        'FLOW_PORT_DIA':f'{port_dia:g}','PORT_FACE':f'{port_face:g}',
        'PORT_SPAN':f'{2*port_face:g}','BODY_OFFSET':f'{body_center_z:g}',
        'COLLAR_START':f'{port_neck_end:g}','COLLAR_END':f'{port_collar_end:g}',
        'COLLAR_LEN':f'{port_collar_end-port_neck_end:g}',
        'NECK_DIA':f'{2*port_neck_radius:g}','COLLET_LEN':f'{port_face-port_collar_end:g}',
        'WIRE_ROOT_WIDTH':f'{wire_root_width:g}','WIRE_ROOT_DEPTH':f'{wire_root_depth:g}',
        'WIRE_BOSS_LEN':f'{wire_boss_len:g}'})
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
