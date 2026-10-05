#!/usr/bin/env python3
"""Editable SUP29F-XH exterior in mm, fitted to the MINI 2 capture and photos.

X points toward the nozzle, Y is transverse, Z is up. The front housing face
intersects the barrel axis at the origin; reflection is across Y=0.
"""
from pathlib import Path
import math
import sys
import json
import argparse
import numpy as np
import cadquery as cq
import trimesh
from mesh_tools import checked_stl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from _cadq_export import export_assembly
from _material_base import M_ALUMINIUM, M_COPPER, M_TPU_BLACK

HEAD_LENGTH = 134.4
HEAD_WIDTH = 33.9
HEAD_HEIGHT = 36.7
HEAD_Z = -1.15
GRIP_WIDTH = 38.0
GRIP_THICKNESS = 34.0
GRIP_LENGTH = 83.0
GRIP_ORIGIN = np.array([-64.86, 0., -20.])
GRIP_ANGLE = math.radians(29.91)
GRIP_AXIS = np.array([-math.sin(GRIP_ANGLE), 0., -math.cos(GRIP_ANGLE)])
GRIP_ACROSS = np.array([math.cos(GRIP_ANGLE), 0., -math.sin(GRIP_ANGLE)])
STEM_D = 12.0743
SLEEVE_D = 17.8993
SLEEVE_END = 96.0
NOZZLE_LENGTH = 25.0
NOZZLE_BASE_D = 14.6
NOZZLE_MOUTH_D = 8.4
BOOT_CUFF_LENGTH = 31.0
BOOT_LENGTH = 80.0
WIRE_AXIS = np.array([.792, 0., .6105])
WIRE_AXIS /= np.linalg.norm(WIRE_AXIS)
WIRE_ORIGIN = np.array([68.3, 0., -34.8])
BRASS = cq.Color(.71, .56, .33)


def grip_point(t, across=0.0, y=0.0):
    return tuple(GRIP_ORIGIN + GRIP_AXIS*t + GRIP_ACROSS*across + np.array([0., y, 0.]))


def revolve_x(profile):
    """Closed outer radius profile, with flat axial caps."""
    points = [(0., profile[0][0]), *((r, x) for x, r in profile),
              (0., profile[-1][0])]
    return (cq.Workplane('XZ').polyline(points).close()
            .revolve(360, (0, 0), (0, 1))
            .rotate((0, 0, 0), (0, 1, 0), 90))


def cylinder_x(x0, x1, r):
    return revolve_x([(x0, r), (x1, r)])


def place_axis(shape, origin, axis):
    """Place a +X axial solid at an arbitrary direction."""
    axis = np.array(axis, dtype=float)
    axis /= np.linalg.norm(axis)
    rot_axis = np.cross([1., 0., 0.], axis)
    angle = math.degrees(math.acos(np.clip(axis[0], -1, 1)))
    if np.linalg.norm(rot_axis) > 1e-8:
        shape = shape.rotate((0, 0, 0), tuple(rot_axis), angle)
    elif axis[0] < 0:
        shape = shape.rotate((0, 0, 0), (0, 1, 0), 180)
    return shape.translate(tuple(origin))


def rounded_bar(width, thickness, length, radius, origin, axis):
    part = (cq.Workplane('XY').rect(width, thickness).extrude(length)
            .edges('|Z').fillet(radius))
    # The cross section is symmetric; a rotation through Y puts its long axis
    # down the grip while reversing the across direction harmlessly.
    if np.allclose(axis, GRIP_AXIS):
        return part.rotate((0, 0, 0), (0, 1, 0), -180+math.degrees(GRIP_ANGLE)).translate(tuple(origin))
    raise ValueError('Unsupported rounded-bar axis')


def housing():
    head = (cq.Workplane('XY').box(HEAD_LENGTH, HEAD_WIDTH, HEAD_HEIGHT)
            .edges('|X').fillet(4.5).translate((-HEAD_LENGTH/2, 0., HEAD_Z)))
    grip = rounded_bar(GRIP_WIDTH, GRIP_THICKNESS, GRIP_LENGTH+20, 4.5,
                       GRIP_ORIGIN-GRIP_AXIS*20, GRIP_AXIS)
    body = head.union(grip)
    # Side reliefs are display geometry. The scanned mesh retains their actual
    # relief, lettering, fastener recesses and the transition around the grip.
    panels = [[(-84, 10.2), (-41, 10.2), (-40, -7.5), (-76, -7.5)],
              [(-37, 10.2), (-8, 10.2), (-8, -7.5), (-27, -7.5)]]
    for side in (-1, 1):
        for outline in panels:
            cut = (cq.Workplane('XZ').polyline(outline).close()
                   .extrude(side*.40).translate((0., side*16.95, 0.)))
            body = body.cut(cut)
    for y in (-8.0, 8.0):
        stem = cq.Workplane('XY').center(-15.5, y).circle(2.55).extrude(4.0).translate((0, 0, 17.2))
        knob = cq.Workplane('XY').center(-15.5, y).circle(5.0).extrude(3.8).translate((0, 0, 21.2))
        body = body.union(stem).union(knob)
    return body


def barrel_parts():
    neck = revolve_x([(-.3, 11.9), (1.2, 11.9), (1.2, 10.6),
                      (4.5, 10.6), (5.8, 12.9), (7., 13.3),
                      (17., 13.3), (17.8, 12.6)])
    # The observed knurled ring has approximately 0.75 mm pitch. Grooves here
    # provide its outer clearance shape without a threaded mating claim.
    for i in range(96):
        a=2*math.pi*i/96
        cutter=cq.Solid.makeCylinder(.25, 10.2, cq.Vector(6.9, 13.40*math.cos(a), 13.40*math.sin(a)), cq.Vector(1, 0, 0))
        neck=neck.cut(cutter)
    shoulder = (cq.Workplane('YZ').polygon(6, 16/math.cos(math.pi/6))
                .extrude(5.0).translate((17.0, 0, 0)))
    stem = cylinder_x(21.0, 61.8, STEM_D/2)
    sleeve = revolve_x([(61.8, STEM_D/2), (62.4, 6.3), (63.7, 8.15),
                        (65.3, SLEEVE_D/2), (SLEEVE_END, SLEEVE_D/2)])
    return {'barrel-neck-and-ring': neck, 'barrel-hex': shoulder,
            'barrel-stem': stem, 'barrel-sleeve': sleeve}


def nozzle():
    end = SLEEVE_END + NOZZLE_LENGTH
    part = revolve_x([(SLEEVE_END-.4, 8.95), (SLEEVE_END+2., 8.95),
                      (SLEEVE_END+2., NOZZLE_BASE_D/2),
                      (end-1.2, NOZZLE_MOUTH_D/2), (end, NOZZLE_MOUTH_D/2)])
    # The visible mouth is open. Its shallow depth and internal taper are
    # estimates and do not describe the internal optical or gas passage.
    mouth = revolve_x([(end-3.5, 2.8), (end+.2, 3.2)])
    return part.cut(mouth)


def capsule_xz(p1, p2, radius, thickness):
    d=np.array(p2)-np.array(p1);length=np.linalg.norm(d)
    center=(np.array(p1)+np.array(p2))/2
    angle=math.degrees(math.atan2(d[1],d[0]))
    return (cq.Workplane('XZ').slot2D(length+2*radius, 2*radius, angle)
            .extrude(thickness/2,both=True).translate((center[0], 0, center[1])))


def feeder_bracket():
    short=capsule_xz((.5,-28.9),(30.5,-28.9),4.65,18.5)
    long=capsule_xz((30.5,-27.5),(58.,-26.5),5.3,15.)
    elbow=capsule_xz((58.,-26.5),(68.3,-34.8),5.0,15.)
    attachment=(cq.Workplane('XY').box(6.5,18.5,11.5).translate((-3.,0,-22.4)))
    bracket=short.union(long).union(elbow).union(attachment)
    # Through openings are measured from the scan/profile and checked in the
    # photographs. They must stay open in the fit reference.
    opening1=(cq.Workplane('XY').box(19.,10.,30.).translate((15.8,0,-29.1)))
    opening2=(cq.Workplane('XY').box(21.,8.,30.).translate((44.7,0,-28.6)))
    bracket=bracket.cut(opening1).cut(opening2)
    for x,z,r in [(.5,-28.9,4.45),(30.5,-28.9,4.5)]:
        boss=(cq.Workplane('XZ').center(x,z).circle(r).extrude(10.4,both=True))
        bracket=bracket.union(boss)
    return bracket


def hex_axial(t0,t1,af):
    return (cq.Workplane('YZ').polygon(6, af/math.cos(math.pi/6))
            .extrude(t1-t0).translate((t0,0,0)))


def feeder_parts():
    parts={'wire-feed-bracket':feeder_bracket()}
    axial={'wire-feed-front-nut':hex_axial(3.9,10.2,16.0),
           'wire-feed-rear-nut':hex_axial(-10.7,-4.0,16.0),
           'wire-feed-coupler':hex_axial(-30.,-10.0,12.4),
           'wire-feed-guide-nut':hex_axial(-39.,-29.7,11.8),
           'wire-feed-thread-envelope':cylinder_x(9.6,32.0,4.95),
           'wire-feed-shank':cylinder_x(-12.,10.5,5.2),
           'wire-feed-guide':cylinder_x(-137.,-38.,3.95)}
    # The photographed mouth is reflected with the requested symmetric exterior.
    for side in (-1, 1):
        axial['wire-feed-coupler']=axial['wire-feed-coupler'].cut(
            cq.Solid.makeCylinder(1.5,3.0,cq.Vector(-19,side*6.5,0),cq.Vector(0,-side,0)))
    for name,part in axial.items():
        parts[name]=place_axis(part,WIRE_ORIGIN,WIRE_AXIS)
    return parts


def trigger():
    # Unscanned front face: photo-derived fixed clearance envelope in the
    # released position. The paddle runs along the front of the grip.
    plane=cq.Plane(origin=grip_point(23,18.8),xDir=tuple(GRIP_AXIS),normal=tuple(GRIP_ACROSS))
    paddle=cq.Workplane(plane).slot2D(38.,10.).extrude(4.3)
    button=(cq.Workplane(cq.Plane(origin=grip_point(32,23.1),xDir=tuple(GRIP_AXIS),normal=tuple(GRIP_ACROSS)))
            .circle(3.8).extrude(2.1))
    return paddle.union(button)


def boot():
    # Loft stations use the grip-sized section specified by the operator,
    # the slight cuff expansion and the shoulder visible in the photographs.
    g=GRIP_LENGTH
    cuff=g+BOOT_CUFF_LENGTH
    end=g+BOOT_LENGTH
    stations=[(g-.4,38.0,34.,6.0), (g+2.,40.5,35.8,7.0),
              (cuff-6.,40.5,35.8,7.0), (cuff,38.0,34.8,7.0),
              (cuff+4.,29.0,28.5,7.0), (end-15.,29.,28.5,7.0),
              (end-11.,32.0,29.0,8.0), (end-6.,32.,29.,8.0),
              (end,28.,27.,7.0)]
    wires=[]
    for t,w,h,r in stations:
        plane=cq.Plane(origin=grip_point(t),xDir=tuple(GRIP_ACROSS),normal=tuple(GRIP_AXIS))
        wire=cq.Workplane(plane).rect(w,h).val()
        wire=wire.fillet2D(r,wire.Vertices())
        wires.append(wire)
    return cq.Workplane('XY').add(cq.Solid.makeLoft(wires,ruled=True))


def build_parts():
    return {'housing':housing(),**barrel_parts(),'copper-nozzle':nozzle(),
            **feeder_parts(),'trigger-clearance':trigger(),'umbilical-boot':boot()}


def to_mesh(shape,deflection=.075):
    v,f=shape.val().tessellate(deflection,.12)
    m=trimesh.Trimesh(np.array([p.toTuple() for p in v]),np.array(f),process=True)
    m.fix_normals(multibody=True)
    return m


def build():
    """Compound with named exterior components; internal mechanisms are omitted."""
    parts=build_parts()
    return cq.Workplane('XY').add(cq.Compound.makeCompound([p.val() for p in parts.values()]))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'output/xlaserlab-sup29f-xh')
    args=parser.parse_args()
    output=args.output.resolve();output.mkdir(parents=True,exist_ok=True)
    parts=build_parts()
    assembly=cq.Assembly(name='xlaserlab-sup29f-xh')
    meshes={}
    for name,p in parts.items():
        if not p.val().isValid():
            raise ValueError(f'Invalid BREP: {name}')
        color = M_COPPER if 'copper' in name else M_TPU_BLACK if 'boot' in name else BRASS if any(x in name for x in ('front-nut','rear-nut','coupler','thread','shank')) else M_ALUMINIUM
        assembly.add(p,name=name,color=color)
        m=to_mesh(p)
        if not m.is_watertight or not m.is_winding_consistent:
            raise ValueError(f'Invalid mesh: {name}')
        meshes[name]=m
    export_assembly(assembly,str(output/'xlaserlab-sup29f-xh.step'))
    merged=trimesh.boolean.union(list(meshes.values()),engine='manifold')
    if not merged.is_watertight or len(merged.split())!=1:
        raise ValueError('CAD exterior must be one watertight connected volume')
    merged = checked_stl(merged, output/'xlaserlab-sup29f-xh-cad.stl')
    np.savez_compressed(output/'cad-meshes.npz',
                        **{name+'__v':m.vertices for name,m in meshes.items()},
                        **{name+'__f':m.faces for name,m in meshes.items()})
    (output/'cad-check.json').write_text(json.dumps({
        'units':'mm','symmetry_plane':'Y=0','valid_brep':True,
        'components':{name:{'triangles':len(m.faces),'watertight':bool(m.is_watertight),
                            'volume_mm3':float(m.volume),'bounds_mm':m.bounds.tolist()}
                      for name,m in meshes.items()},
        'scope':'Exterior geometry for mount layout; scan and photo estimates are identified in measurements.json.'},indent=2)+'\n')
    print('Exported',len(parts),'valid exterior components to',output)


if __name__=='__main__':
    main()
