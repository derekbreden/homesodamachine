#!/usr/bin/env python3
"""Build the two coaxial joints, scan-envelope cradle and fit coupons.

All printable solids are exported in their specified print orientation.
Assembly STEP and display meshes retain rotator coordinates. No source files
outside this package are changed. Run with tools/cad-venv/bin/python.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import math
import sys
import zipfile

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import MultiPoint
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'hardware/scripts'))
import flute_payload
import _mesh_payload

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
D = json.loads((HERE / 'design.json').read_text())
OUT = HERE / 'parts'
PARTS = []
HARDWARE = []

def box(x, y, z, at=(0, 0, 0)):
    return cq.Workplane('XY').box(x, y, z, centered=(True, True, False)).translate(at)

def cyl(d, h, at=(0, 0, 0)):
    return cq.Workplane('XY').circle(d / 2).extrude(h).translate(at)

def ring(od, id_, h, z=0):
    return cyl(od, h, (0, 0, z)).cut(cyl(id_, h + 2, (0, 0, z - 1)))

def pcd(r, n, phase=0):
    return [(r * math.cos(math.radians(phase + i * 360 / n)),
             r * math.sin(math.radians(phase + i * 360 / n))) for i in range(n)]

def holes(shape, pts, d, z, height):
    for x, y in pts:
        shape = shape.cut(cyl(d, height, (x, y, z)))
    return shape

def nut(shape, x, y, z, af, depth):
    cut = cq.Workplane('XY').polygon(6, af / math.cos(math.pi / 6)).extrude(depth).translate((x, y, z))
    return shape.cut(cut)

def ax(shape):
    """Local Z axis to world X axis; local X to -world Z."""
    return shape.rotate((0, 0, 0), (0, 1, 0), 90)

def add(name, shape, group='fixed', at=(0, 0, 0), orientation=None, material='PET-CF17', qty=1):
    print('part',name,flush=True)
    shape = shape.val() if isinstance(shape, cq.Workplane) else shape
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError(f'{name}: expected one valid solid, got {len(shape.Solids())}')
    world = shape if orientation is None else orientation(cq.Workplane(obj=shape)).val()
    world = world.translate(cq.Vector(*at))
    PARTS.append(dict(name=name, solid=shape, world=world, group=group, material=material, quantity=qty))
    return world

def hw(name, shape, group='fixed', at=(0, 0, 0), orientation=None):
    solid = shape.val() if isinstance(shape, cq.Workplane) else shape
    world = solid if orientation is None else orientation(cq.Workplane(obj=solid)).val()
    HARDWARE.append(dict(name=name, world=world.translate(cq.Vector(*at)), group=group))

def adapter():
    # Flush M4 heads; separate captured M3 nuts couple the supported journal.
    a = ring(48,14.4,7.7).union(ring(44,14.4,.3,7.7))
    a = holes(a, pcd(15, 6, D['output_phase_deg']), 4.4, -1, 10)
    a = holes(a, pcd(15, 6, D['output_phase_deg']), 9.4, 4, 5)
    for x, y in pcd(12, 6, 45):
        a = holes(a, [(x, y)], 3.4, -1, 10)
        a = nut(a, x, y, 5.5, 5.6, 3)
    for angle in range(45,405,60):
        key=box(6,5,6.1,(20,0,2)).rotate((0,0,0),(0,0,1),angle)
        a=a.cut(key)
    return a

def journal():
    j = cyl(D['journal_diameter'], D['journal_length'])
    j = j.union(cyl(44, D['neck_length'], (0, 0, D['journal_length'])))
    flange_z = D['journal_length'] + D['neck_length']
    j = j.union(cyl(76, 6, (0, 0, flange_z)))
    j = j.cut(cyl(8.0, flange_z + 8, (0, 0, -1)))
    for x, y in pcd(12, 6, 45):
        j = holes(j, [(x, y)], 3.4, -1, flange_z + 8)
        j = holes(j, [(x, y)], 9.4, 7, flange_z + 1)
    for angle in range(45,405,60):
        key=box(6,5.05,6,(20,0,-6)).rotate((0,0,0),(0,0,1),angle)
        j=j.union(key)
    j=holes(j,pcd(15,6,D['output_phase_deg']),7.6,-.1,1.3)
    for x, y in pcd(29, 6, 30):
        j = holes(j, [(x, y)], 5.4, flange_z - 1, 8)
        j = nut(j, x, y, flange_z - .1, 8.2, 4.2)
    return j

def bearing_housing(z):
    # The outer-race shoulder is separate from the rotating inner-race pad.
    s = box(86, 86, 4, (0, 0, z - 4)).cut(cyl(48.4, 6, (0, 0, z - 5)))
    s = s.union(ring(76, D['bearing_bore'], 22, z))
    for x, y in pcd(33, 4, 45):
        s = holes(s, [(x, y)], 4.4, z + 7, 16)
        s = nut(s, x, y, z + 9, 7.2, 3.3)
        angle=math.degrees(math.atan2(y,x))
        window=box(16,8,3.3,(38,0,z+9)).rotate((0,0,0),(0,0,1),angle)
        s=s.cut(window)
    return s

def bearing_cap():
    return holes(ring(76, 48.4, 2), pcd(33, 4, 45), 4.4, -1, 4)

def motor_case_mount(z):
    s = box(94, 94, 8, (0, 0, z))
    s = s.cut(cyl(60.4, 10, (0, 0, z - 1)))
    return holes(s, pcd(35, 4, 45), 5.8, z - 1, 10)

def bridge():
    b = box(302, 90, 18, (30, 0, 0))
    # Real stationary-base holes at Y=-107; overhanging bridge behind rotor.
    anchor_y=-107-D['yaw_xy'][1]
    for x in (-102, 162):
        b = b.union(box(30,26,18,(x,anchor_y,0)))
        b = b.union(ring(9.7, 8.5, 10, -10).translate((x, anchor_y, 0)))
        b = holes(b, [(x, anchor_y)], 8.5, -11, 31)
        for y in (-34, -44):
            b = holes(b, [(x, y)], 5.4, -1, 21)
    for x, y in [(D['yaw_xy'][0] + a, b) for a in (-42, 42) for b in (-35, 35)]:
        b = holes(b, [(x, y)], 5.4, -1, 21)
        b = nut(b, x, y, -.1, 8.2, 4.3)
    return b

def toe():
    s = box(40, 20, 36)
    for y in (-5, 5):
        s = holes(s, [(0, y)], 5.4, 22, 15)
        s = nut(s, 0, y, 25.5, 8.2, 4.3)
        # Nut loading window through the side; does not cut the compression foot.
        s = s.cut(box(12, 16, 4.3, (0, y - 9, 25.5)))
    return s

def pedestal():
    base = box(100, 88, 8)
    base = holes(base, [(x, y) for x in (-42, 42) for y in (-35, 35)], 5.4, -1, 10)
    base = holes(base, [(x, y) for x in (-42, 42) for y in (-35, 35)], 10.6, 5, 5)
    case_z = D['yaw_input_z'] + 4.4 - 30
    s = base.union(motor_case_mount(case_z))
    for x in (-34, 34):
        for y in (-34, 34):
            s = s.union(box(14, 14, case_z, (x, y, 7)))
    s=s.cut(box(61.2,61.2,4.4,(0,0,case_z-4.4)))
    # Leave motor/cable clearance through the base.
    s = s.cut(box(44, 44, 12, (0, 0, -1)))
    for x in (-34, 34):
        for y in (-34, 34):
            s = holes(s, [(x, y)], 5.4, case_z - 1, 10)
            s = nut(s, x, y, case_z, 8.2, 4.2)
    return s

def yaw_cartridge():
    bottom = D['yaw_input_z'] + 12.4
    seat = D['yaw_input_z'] + D['reducer_length'] + 8
    s = bearing_housing(seat - bottom)
    for x in (-34, 34):
        for y in (-34, 34):
            leg = box(14, 14, seat - bottom - 4, (x, y, 0))
            s = s.union(leg)
            s = holes(s, [(x, y)], 5.4, -1, 8)
            s = holes(s, [(x, y)], 10.6, 6, 12)
    ear=box(52,42,8,(0,-50,seat-bottom+10))
    s=s.union(ear)
    for x in(-14,14):
        s=holes(s,[(x,-65)],4.4,seat-bottom+9,10)
        s=nut(s,x,-65,seat-bottom+10,7.2,3.3)
    return s

def fork():
    seat_z = D['yaw_input_z'] + D['reducer_length'] + 8
    deck_z = seat_z + D['journal_length'] + D['neck_length'] + 6
    pivot = D['pivot_z']
    deck = box(236, 118, 12, (-30, 0, deck_z - pivot))
    case_input = D['pitch_output_x'] - D['reducer_length']
    case_mount = case_input + 4.4
    seat = D['pitch_output_x'] + 8
    f = deck.union(ax(motor_case_mount(0)).translate((case_mount, 0, 0)))
    bh = ax(bearing_housing(0)).translate((seat, 0, 0))
    f = f.union(bh)
    for y in (-34, 34):
        for z in (-34, 34):
            f = f.union(box(seat - 4 - (case_mount + 8), 14, 14,
                            ((seat - 4 + case_mount + 8)/2, y, z - 7)))
    # Opposite support, with two axially captured 6001 bearings.
    right = ax(ring(44, 12.4, 29)).translate((50, 0, 0))
    right = right.cut(ax(cyl(24,5.01)).translate((49.99,0,0)))
    for x in (55, 71):
        right = right.cut(ax(cyl(D['opposite_bearing_bore'], 8.1)).translate((x, 0, 0)))
    f = f.union(right)
    # Solid webs tie the opposite cartridge down to the deck.
    for y in (-20, 20):
        f = f.union(box(29, 12, 28, (64.5, y, deck_z - pivot + 6)))
    # Clearance through deck for reducer and motor; case support is the 94mm plate.
    f = f.cut(ax(cyl(60.4, D['reducer_length']+1)).translate((case_input - .5, 0, 0)))
    f=f.cut(ax(box(61.2,61.2,4.4)).translate((case_input,0,0)))
    f = f.cut(box(52, 44, 60, (case_input - 26, 0, -22)))
    f = holes(f, pcd(29, 6, 30), 5.4, deck_z - pivot - 1, 15)
    f = holes(f, pcd(29, 6, 30), 10.6, deck_z - pivot + 9, 4)
    # Yaw parking datum and cam on a rear deck extension.
    f=f.union(box(18,35,12,(0,-72,deck_z-pivot)))
    f = holes(f, [(0, -70)], 6.4, deck_z - pivot - 1, 16)
    f = nut(f,0,-70,deck_z-pivot-.1,10.2,5.3)
    f = holes(f,[(0,-77.5)],3.05,deck_z-pivot-1,16)
    f=f.union(box(5,14,3.2,(0,-88,deck_z-pivot-3)))
    # Mount holes for travel/stop accessories, on the accessible rear edge.
    for x in (-20, 20):
        f = holes(f, [(x, -49)], 4.4, deck_z - pivot - 1, 15)
        f = nut(f, x, -49, deck_z - pivot - .1, 7.2, 3.3)
    # Pitch stop is attached to the driven cheek. No shaft-clamp friction
    # participates in the positive stop's load path.
    f=f.union(box(12,42,64,(-61,-50,-32)))
    f=f.cut(box(14,12,18,(-61,-70,-9)))
    for zz in(-14,14):
        f=f.cut(ax(cyl(4.4,13,(-zz,-65,0))).translate((-67,0,0)))
        pocket=cq.Workplane('XY').polygon(6,7.2/math.cos(math.pi/6)).extrude(3.3).translate((-zz,-65,0))
        f=f.cut(ax(pocket).translate((-64,0,0)))
        f=f.cut(box(3.3,12,8,(-62.35,-68,zz-4)))
    # Bearing outer retainers on the right.
    for yy, zz in pcd(18, 4, 45):
        f = f.cut(ax(cyl(3.4, 12, (yy, zz, 0))).translate((72, 0, 0)))
        f = f.cut(ax(cq.Workplane('XY').polygon(6, 5.6/math.cos(math.pi/6)).extrude(2.6)
                       .translate((yy, zz, 0))).translate((72, 0, 0)))
        angle=math.degrees(math.atan2(zz,yy))
        window=box(10,6.2,2.6,(22,0,72)).rotate((0,0,0),(0,0,1),angle)
        f=f.cut(ax(window))
    # Cut AFTER all webs/deck unions: no deck material may fill a bearing seat.
    for diameter,x,h in [(48.8,D['pitch_output_x']-.2,8.4),(48.4,seat-4.01,4.02),
                         (D['bearing_bore'],seat-.01,22.02),(76.4,seat+22,3.2),(76.6,seat+25.1,6.4),
                         (12.4,49.99,29.02),(24,49.99,5.02),
                         (D['opposite_bearing_bore'],54.99,8.12),
                         (18.4,63,8),(D['opposite_bearing_bore'],70.99,8.12),
                         (44.4,79,4.3),(18.4,83.2,17),(28.8,31.9,15.3)]:
        f=f.cut(ax(cyl(diameter,h)).translate((x,0,0)))
    # Rear clearance for the driven cheek and its stop arm. Retain the
    # front crossmember so the deck, reducer support and idler form one frame.
    f=f.cut(box(14.8,110,35,(-35,-15,-35)))
    f=f.cut(box(10.8,80,28,(37,0,-28)))
    return f

def gun_transform(shape):
    # X->barrel direction, Y->-worldX, Z->housing up. Orthogonal proper rotation.
    return shape.rotate((0,0,0),(1,0,0),D['gun_roll_deg']).rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(1,0,0),-D['barrel_down_deg']).rotate((0,0,0),(0,0,1),D['barrel_azimuth_deg'])

def gun_origin_relative():
    angle=math.radians(D['barrel_down_deg']); az=math.radians(D['barrel_azimuth_deg'])
    direction=np.array([-math.cos(angle)*math.sin(az),math.cos(angle)*math.cos(az),-math.sin(angle)])
    lateral=np.array([-math.cos(az),-math.sin(az),0.])
    return np.array([0.,D['working_lever_mm'],0.])-(121+D['nozzle_gap'])*direction+D['gun_lateral_mm']*lateral


def contacts():
    # Deterministic conservative envelope from pinned reconstructed housing,
    # with only the head region in each 16mm clamping band.
    surf = np.load(ROOT / 'hardware/reference/xlaserlab-sup29f-xh/source/reconstructed-surfaces.npz')
    v = surf['housing__v']
    profiles = []
    for x in D['cradle_bands_x']:
        points = v[(abs(v[:, 0] - x) <= 8.1) & (v[:, 2] > -24), 1:]
        profile = MultiPoint(points).convex_hull.buffer(D['contact_clearance'] + D['liner_thickness'],
                                                      quad_segs=3).simplify(.12)
        profiles.append((x, profile))
    return profiles

def profile_solid(poly, x, length):
    # Workplane YZ's normal is +X; its coordinates are Y,Z.
    pts = list(poly.exterior.coords)[:-1]
    return cq.Workplane('YZ').polyline(pts).close().extrude(length).translate((x, 0, 0))

def cradle_parts():
    profiles = contacts()
    cradle = box(141, 10, 12, (-70.5, -25, -30)).union(box(141, 10, 12, (-70.5, 25, -30)))
    for i, (x, profile) in enumerate(profiles):
        lower = box(16, 62, 30, (x, 0, -30)).cut(profile_solid(profile, x - 8.1, 16.2))
        cradle = cradle.union(lower)
        upper = box(16, 62, 27.4, (0, 0, .6)).cut(profile_solid(profile, -8.1, 16.2))
        for y in (-25, 25):
            cradle = holes(cradle, [(x, y)], 4.4, -32, 36)
            cradle = nut(cradle, x, y, -15, 7.2, 3.3)
            cradle = cradle.cut(box(8,14,3.3,(x, y + (7 if y>0 else -7),-15)))
            # Upper band uses M4x20 with deep head wells, ends above grip space.
            upper = holes(upper, [(0, y)], 4.4, -1, 31)
            upper = holes(upper, [(0, y)], 9.4, 4, 26)
        # Saved at local origin for easy print placement; world transform below.
        world = gun_transform(upper.translate((x, 0, 0))).translate(tuple(gun_origin_relative()))
        add(f'gun-retainer-{i+1}', upper, 'pitch', orientation=lambda s,w=world: cq.Workplane(obj=w.val()))
        # Two thin liners at each clamping station, scan-envelope offset shapes.
        inner = profile.buffer(-D['liner_thickness'])
        sleeve = profile_solid(profile, -8, 16).cut(profile_solid(inner, -8.1, 16.2))
        for side, clip in [('lower', box(20,70,40,(0,0,-40))), ('upper', box(20,70,40))]:
            liner = sleeve.intersect(clip)
            world_l = gun_transform(liner.translate((x,0,0))).translate(tuple(gun_origin_relative()))
            add(f'liner-{i+1}-{side}', liner, 'pitch', material='TPU', orientation=lambda s,w=world_l: cq.Workplane(obj=w.val()))
    # Front shoulder stop bears on the lower housing face, clear of the feed guide.
    for side in(-1,1):
        cradle=cradle.union(box(6,18,6,(3,side*21,-24)))
        cradle=cradle.union(box(3,6,14,(1.7,side*15,-22)))
    # Cradle screws into cheeks, below gun/liner contact region.
    for x, _ in profiles:
        for y in (-25, 25):
            cradle = holes(cradle, [(x + 12, y)], 4.4, -32, 17)
            cradle = nut(cradle, x + 12, y, -22, 7.2, 4.1)
    add('lower-cradle', cradle, 'pitch', orientation=lambda s: gun_transform(s).translate(tuple(gun_origin_relative())))
    return profiles

def cheek(side, profiles):
    centers = []
    angle = math.radians(D['barrel_down_deg'])
    origin = gun_origin_relative()
    for x, _ in profiles:
        centers.append([origin[1] + x*math.cos(angle)-26*math.sin(angle),
                        origin[2]-x*math.sin(angle)-26*math.cos(angle)])
    contour = MultiPoint([[0,-24],[34,0],[-34,0]] +
                        [[y+dy,z+dz] for y,z in centers for dy,dz in [(-17,-16),(17,-16),(17,16),(-17,16)]]).convex_hull
    # Local plate plane YZ, normal X. Spindle drives left; shaft clamps right.
    s = profile_solid(contour, 0, 10)
    if side == 'left':
        s=s.union(box(14,70,48,(7,-35,-24)))
        s=s.union(box(14,16.2,18,(7,-78,-9)))
        s=s.union(box(3.1,14,5,(-1.15,-88,-2.5)))
        s=s.cut(ax(cyl(6.4,17,(0,-70,0))).translate((-1,0,0)))
        pocket=cq.Workplane('XY').polygon(6,10.2/math.cos(math.pi/6)).extrude(5.3).translate((0,-70,0))
        s=s.cut(ax(pocket).translate((-.1,0,0)))
        s=s.cut(ax(cyl(3.05,17,(0,-77.5,0))).translate((-1,0,0)))
        # The frame tie retains its 64 mm width; relieve only the added
        # four-millimetre stop-arm thickness at that bolted interface.
        s=s.cut(box(4.2,40.2,18.2,(12.1,0,-9.1)))
        s = s.cut(ax(cyl(14.4,12)).translate((-1,0,0)))
        for a,b in pcd(29,6,30):
            # Same orientation as axle adapter: local X->-Z, local Y->Y.
            yy,zz=b,-a
            s = s.cut(ax(cyl(5.4,12,(a,b,0))).translate((-1,0,0)))
            s = s.cut(ax(cyl(10.6,2,(a,b,0))).translate((9,0,0)))
    else:
        hub = ax(cyl(28,15)).translate((0,0,0))
        s = s.union(hub).cut(ax(cyl(D['shaft_bore'],26)).translate((-1,0,0)))
        s = s.cut(box(16,1.2,20,(8,0,-20)))
        # Across the split hub, M4x20 clamp with captured nut.
        screw = cyl(4.4,30).rotate((0,0,0),(1,0,0),90).translate((8,15,-8))
        s = s.cut(screw)
        pocket = cq.Workplane('XY').polygon(6,7.2/math.cos(math.pi/6)).extrude(3.4)
        s = s.cut(pocket.rotate((0,0,0),(1,0,0),90).translate((8,-9,-8)))
    for yy in(-14,14):
        s=s.cut(ax(cyl(4.4,22,(0,yy,0))).translate((-1,0,0)))
        s=s.cut(ax(cyl(9.4,6,(0,yy,0))).translate((-1 if side=='left' else 5,0,0)))
    # Two 8mm pads below the rails, bolts parallel to gun's housing-up axis.
    for i,(x,_) in enumerate(profiles):
        local_y = 25 if side=='left' else -25
        rail_mount = gun_transform(box(18,16,8,(x+12,local_y,-38))).translate(tuple(origin))
        x_offset = -42 if side=='left' else 32
        rail_mount = rail_mount.translate((-x_offset,0,0))
        s = s.union(rail_mount)
        cut = gun_transform(cyl(4.4,30,(x+12,local_y,-40))).translate(tuple(origin)).translate((-x_offset,0,0))
        s = s.cut(cut)
    return s

def bottom_tie():
    s=box(64,40,18,(0,0,-9))
    for yy in(-14,14):
        s=s.cut(ax(cyl(4.4,66,(0,yy,0))).translate((-33,0,0)))
        for xx in(-26,22.7):
            n=cq.Workplane('XY').polygon(6,7.2/math.cos(math.pi/6)).extrude(3.3).translate((0,yy,0))
            s=s.cut(ax(n).translate((xx,0,0)))
            s=s.cut(box(3.3,10,11,(xx+1.65,yy,-1)))
    return s

def stop_sector():
    # R70 M6 follower. The printed slot sets nominal +/-1.5 degrees.
    width = 6.0 + 2*D['stop_radius']*math.sin(math.radians(D['hard_stop_deg']))
    s = box(46,20,12,(0,-70,0))
    s = s.cut(box(width,7.0,14,(0,-70,-1)))
    s = holes(s,[(0,-77.5)],3.05,-1,15)
    for x in (-14,14):
        s = holes(s,[(x,-65)],4.4,-1,15)
        s = holes(s,[(x,-65)],9.4,5,9)
    for x in(-18,18):
        s=holes(s,[(x,-76)],3.4,-1,15)
        s=nut(s,x,-76,-.1,5.6,2.6)
    return s

def switch_holder():
    # Face-clamped KW12 body slides 16mm along its length to align the roller.
    base=box(26,18,4)
    base=base.cut(cq.Workplane('XY').slot2D(15,3.4).extrude(6).translate((0,4,-1)))
    clip=box(13,12,40,(0,-11,3))
    clip=clip.cut(box(8,7.2,36,(0,-11,5)))
    clip=clip.cut(box(10,14,32,(6,-11,7)))
    base=base.union(clip)
    screw=cyl(3.4,14).rotate((0,0,0),(1,0,0),90).translate((0,-4,23))
    pocket=cq.Workplane('XY').polygon(6,5.6/math.cos(math.pi/6)).extrude(2.6)
    base=base.cut(screw).cut(pocket.rotate((0,0,0),(1,0,0),-90).translate((0,-17,23)))
    return base

def cable_saddle():
    s=box(60,34,10).union(box(60,10,35,(0,-12,8)))
    # Broad smooth bend support, held with the acquired 8-inch nylon ties.
    s=s.cut(cyl(40,64).rotate((0,0,0),(0,1,0),90).translate((-32,5,32)))
    for x in(-22,22):
        s=s.cut(box(6,25,4,(x,0,5)))
    s=holes(s,[(-20,0),(20,0)],5.4,-1,12)
    return s

def bench_post(height):
    s=box(90,80,10).union(box(40,40,height,(0,0,9)))
    s=s.cut(box(22,22,height+2,(0,0,10)))
    s=s.union(box(72,60,10,(0,0,height)))
    s=holes(s,[(-20,0),(20,0)],5.4,height-15,28)
    for x in(-20,20):
        s=nut(s,x,0,height-.1,8.2,4.1)
        s=s.cut(box(20,10,4.1,(x+(8 if x>0 else -8),0,height-.1)))
    s=holes(s,[(-20,0),(20,0)],5.4,-1,12)
    return s

def electronics_case():
    s = box(124,90,34).cut(box(118,84,34,(0,0,3)))
    # Manufacturer board outline 85x56, holes 58x49; M3 screws/nut pockets.
    for x in (-39,19):
        for y in (-24.5,24.5):
            s = s.union(cyl(9,5,(x,y,3)))
            s = holes(s,[(x,y)],3.4,-1,11)
            s = nut(s,x,y,.5,5.6,2.6)
    s = s.cut(box(90,8,12,(0,-44,8))) # Endstop harness window
    s = s.cut(box(90,8,14,(0,44,8))) # Motor/endstop harnesses
    s = s.cut(box(8,18,14,(60,20,8)))
    s = s.cut(box(8,18,14,(60,-15,8))) # 24V power harness
    for x in (-55,55):
        for y in (-37,37):
            s=s.union(cyl(9,31,(x,y,3)))
            s=holes(s,[(x,y)],3.4,20,18)
            s=nut(s,x,y,26,5.6,2.6)
    return s

def camera_frame():
    return box(270,170,10,(0,40,0)).cut(box(234,134,12,(0,40,-1)))

def camera_stage():
    beta=D['camera_view_down_deg'];front_y=-118.;lens_height=136.
    rx=lambda s:s.rotate((0,0,0),(1,0,0),beta)
    b=math.radians(beta)
    # The manufacturer requires a level base. Only the PTZ head and macro
    # cassette tilt; 29 degrees stays inside the documented -30 degree limit.
    origin=np.array([D['aim'][0],(D['camera_lens_distance_mm']-front_y)*math.cos(b),
                     D['aim'][2]+(D['camera_lens_distance_mm']-front_y)*math.sin(b)-lens_height])
    stage_at=(origin[0],origin[1],-24.)
    base=camera_frame()
    points=[(x,y)for x in(-118,118)for y in(-30,102)]
    for x,y in points:
        base=base.union(ring(20,14,141,9).translate((x,y,0)))
    # Top frame does not cover the two rear posts: use their actual centers.
    for x,y in points:
        base=base.union(box(28,28,10,(x,y,150)))
        base=holes(base,[(x,y)],5.4,146,18)
        base=nut(base,x,y,151,8.2,4.2)
        base=base.cut(box(22,10,4.2,(x+(8 if x>0 else -8),y,151)))
    add('camera-riser-base',base,'camera',at=stage_at,material='PETG')
    relative_height=origin[2]-(stage_at[2]+160)
    upper=camera_frame()
    for x,y in points:upper=upper.union(box(28,28,10,(x,y,0)))
    for x,y in points:
        col=ring(20,14,relative_height-9,9).translate((x,y,0))
        upper=upper.union(col)
        upper=holes(upper,[(x,y)],5.4,-1,14)
    platform=box(270,184,6,(0,20,0)).union(box(108,60,6,(0,-100,0)))
    for x in(-130,130):
        for y in(-50,50):platform=platform.cut(box(6,20,10,(x,y,-1)))
    lens_at=np.array([0.,-100*math.cos(b),lens_height-100*math.sin(b)])
    foot_y=-110.
    platform=holes(platform,[(-48,foot_y),(48,foot_y)],5.4,-1,10)
    upper=upper.union(platform.translate((0,0,relative_height)))
    add('camera-riser-top',upper,'camera',at=(origin[0],origin[1],stage_at[2]+160),material='PETG')
    lens_map=lambda s:rx(s.rotate((0,0,0),(1,0,0),90)).translate(tuple(lens_at))
    upright=box(108,30,8,(0,foot_y,6))
    for x in(-48,48):
        upright=upright.union(lens_map(box(12,120,12,(x,0,17.8))))
        upright=upright.union(box(12,30,58.5,(x,foot_y,6)))
        slot=cq.Workplane('XY').slot2D(98,5.4,90).extrude(90).translate((x,0,16.7))
        upright=upright.cut(lens_map(slot))
    upright=holes(upright,[(-48,foot_y),(48,foot_y)],5.4,5,12)
    add('camera-lens-upright',upright,'camera',at=tuple(origin),material='PETG')
    cassette=box(108,86,17.7).cut(cyl(53.4,20,(0,0,2))).cut(cyl(43.6,21,(0,0,-1)))
    cassette=holes(cassette,[(x,z)for x in(-48,48)for z in(-30,30)],5.4,-1,21)
    cassette=holes(cassette,[(x,z)for x in(-48,48)for z in(-30,30)],10.6,-.1,7.8)
    retainer=holes(box(76,76,2.4).cut(cyl(49.4,5,(0,0,-1))),[(x,z)for x in(-32,32)for z in(-32,32)],3.4,-1,6)
    for x,z in [(x,z)for x in(-32,32)for z in(-32,32)]:
        cassette=holes(cassette,[(x,z)],3.4,-1,22);cassette=nut(cassette,x,z,-.1,5.6,2.8)
    to_lens=lambda s:rx(s.rotate((0,0,0),(1,0,0),90)).translate(tuple(lens_at))
    add('camera-lens-cassette',cassette,'camera',at=tuple(origin),orientation=to_lens,material='PETG')
    add('camera-lens-retainer',retainer,'camera',at=tuple(origin),orientation=lambda s:to_lens(s.translate((0,0,17.7))),material='PETG')
    add('camera-lens-front-pad',ring(53.2,49.5,.2),'camera',at=tuple(origin),orientation=lambda s:to_lens(s.translate((0,0,17.5))),material='TPU')
    for h in(.4,):
        shim=ring(53.2,49.5,h).cut(box(15,18,2,(0,27,-1)))
        add(f'camera-lens-shim-{h:.1f}',shim,'coupon',material='TPU')
    # Camera is an external envelope. Tray ties grip the base; no PTZ housing
    # fit or unmeasured mounting thread is required by this mechanism.
    body=box(253.5,144,40,(0,0,6)).union(box(80,120,100,(0,0,45)))
    head=rx(cyl(80,116).rotate((0,0,0),(1,0,0),90).translate((0,58,0))).translate((0,0,136))
    body=body.union(head)
    hw('camera-envelope',body,'camera',at=tuple(origin))
    lens=ring(43,32,3,-1).union(ring(49,32,12.5,2)).union(ring(53,32,3,14.5))
    hw('raynox-dcr250',lens,'camera',at=tuple(origin),orientation=to_lens)

def build():
    YX,YY = D['yaw_xy']; PZ=D['pivot_z']; YOUT=D['yaw_input_z']+D['reducer_length']
    YSEAT=YOUT+8; POUT=D['pitch_output_x']; PSEAT=POUT+8
    add('bridge',bridge(),at=(0,YY,12))
    for i,x in enumerate((-102,162)):
        add(f'bench-toe-{i+1}',toe(),at=(x,YY-39,-24))
    add('motor-pedestal',pedestal(),at=(YX,YY,30))
    add('yaw-bearing-cartridge',yaw_cartridge(),at=(YX,YY,D['yaw_input_z']+12.4))
    add('yaw-output-adapter',adapter(),'yaw',at=(YX,YY,YOUT))
    add('yaw-journal',journal(),'yaw',at=(YX,YY,YSEAT))
    add('yaw-bearing-cap',bearing_cap(),at=(YX,YY,YSEAT+22))
    add('fork',fork(),'yaw',at=(YX,YY,PZ))
    add('pitch-output-adapter',adapter(),'pitch',at=(YX+POUT,YY,PZ),orientation=ax)
    add('pitch-journal',journal(),'pitch',at=(YX+PSEAT,YY,PZ),orientation=ax)
    add('pitch-bearing-cap',bearing_cap(),'yaw',at=(YX+PSEAT+22,YY,PZ),orientation=ax)
    for joint,at,ori,group in [('yaw',(YX,YY,YSEAT+7),None,'fixed'),('pitch',(YX+PSEAT+7,YY,PZ),ax,'yaw')]:
        add(f'{joint}-outer-spacer',ring(51.9,48.4,7),group,at=at,orientation=ori)
        add(f'{joint}-inner-spacer',ring(44,40.2,7), 'yaw' if joint=='yaw' else 'pitch',at=at,orientation=ori)
        for index,offset in enumerate((0,14)):
            loc=(YX,YY,YSEAT+offset) if joint=='yaw' else (YX+PSEAT+offset,YY,PZ)
            hw(f'{joint}-6808-{index+1}',ring(52,40,7),group,at=loc,orientation=ori)
    profiles=cradle_parts()
    # Cradle parts currently in pivot-local coordinates; place their world origin.
    for p in PARTS:
        if p['name'].startswith(('gun-retainer','liner-','lower-cradle')):
            p['world']=p['world'].translate(cq.Vector(YX,YY,PZ))
    add('left-cheek',cheek('left',profiles),'pitch',at=(YX-42,YY,PZ))
    add('right-cheek',cheek('right',profiles),'pitch',at=(YX+32,YY,PZ))
    add('bottom-frame-tie',bottom_tie(),'pitch',at=(YX,YY,PZ))
    # Positive outer race retainer and inner spacers at the opposite axle.
    cap=holes(ring(44,24,4),pcd(18,4,45),3.4,-1,7)
    add('opposite-bearing-cap',cap,'yaw',at=(YX+79.1,YY,PZ),orientation=ax)
    for i,x in enumerate((55,71)):
        hw(f'opposite-6001-{i+1}',ring(28,12,8),'yaw',at=(YX+x,YY,PZ),orientation=ax)
    for name,x,h in [('axle-collet-spacer',47,8),('opposite-inner-spacer',63,8),('axle-front-stop-spacer',79,21),('axle-middle-spacer',100,12),('axle-end-spacer',112,18)]:
        add(name,ring(18,12.2,h),'pitch',at=(YX+x,YY,PZ),orientation=ax)
    add('axle-keeper',holes(cyl(20,3),[(0,0)],6.5,-1,5),'pitch',at=(YX+130,YY,PZ),orientation=ax)
    hw('opposite-axle',cyl(12,100),'pitch',at=(YX+30,YY,PZ),orientation=ax)
    for joint,at,ori,group in [('yaw',(YX,YY,YSEAT+D['journal_length']+D['neck_length']-11),None,'fixed'),('pitch',(YX-85,YY,PZ),ax,'yaw')]:
        for sign in(-1,1):
            add(f'{joint}-limit-holder-{sign}',switch_holder() if sign>0 else switch_holder().mirror('YZ'),group,at=tuple(np.array(at)+np.array([sign*18,-80,0]) if ori is None else np.array(at)+np.array([-4,-80,sign*18])),orientation=ori)
            if joint=='pitch':
                spacer=holes(box(26,14,30,(0,2,0)),[(0,4)],3.4,-1,32)
                add(f'pitch-switch-standoff-{sign}',spacer,'yaw',at=(YX-85,YY-80,PZ+sign*18),orientation=ax)
    add('umbilical-post-base',bench_post(180),at=(YX,YY-273,-24))
    add('umbilical-post-top',bench_post(190),at=(YX,YY-273,166))
    add('umbilical-saddle',cable_saddle(),at=(YX,YY-273,366))
    # Symbolic purchased reducers: drawing-constrained external envelopes.
    for name,at,ori,group in [('yaw',(YX,YY,D['yaw_input_z']),None,'fixed'),
                              ('pitch',(YX+POUT-D['reducer_length'],YY,PZ),ax,'yaw')]:
        gear=cyl(59,58.6).union(box(60,60,4.4)).union(cyl(55.8,4.5,(0,0,58.6)))
        gear=holes(gear,pcd(35,4,45),5.5,-1,7)
        hw(f'{name}-reducer',gear,group,at=at,orientation=ori)
        motor=box(42.3,42.3,48,(0,0,-48)).union(cyl(22,2)).union(cyl(5,24))
        hw(f'{name}-motor',motor,group,at=at,orientation=ori)
    # Positive stops act directly on the driven fork and left cheek.
    # Stops are separate accessories so their clearance follows the built datum.
    add('yaw-stop-sector',stop_sector(),at=(YX,YY,YSEAT+D['journal_length']+D['neck_length']+6-13))
    hw('yaw-stop-follower',cyl(6,25),'yaw',at=(YX,YY-70,YSEAT+D['journal_length']+D['neck_length']+6+12+.8-25))
    hw('pitch-stop-follower',cyl(6,35),'pitch',at=(YX-62.2,YY-70,PZ),orientation=ax)
    add('pitch-stop-sector',stop_sector(),'yaw',at=(YX-55,YY,PZ),orientation=ax)
    case=electronics_case()
    add('controller-case',case,at=(-180,YY-100,-24),material='PETG')
    lid=box(124,90,3)
    lid=holes(lid,[(x,y)for x in(-55,55)for y in(-37,37)],3.4,-1,5)
    lid=lid.cut(cyl(22.5,5,(-35,0,-1)))
    lid=lid.cut(cyl(36,5,(23,0,-1)))
    lid=holes(lid,[(23+x,y)for x in(-16,16)for y in(-16,16)],3.4,-1,5)
    add('controller-lid',lid,at=(-180,YY-100,10),material='PETG')
    fan=ring(38,6,2)
    for y in (-10,0,10):
        fan=fan.union(box(40,2.4,2,(0,y,0)))
    fan=holes(fan,[(x,y)for x in(-16,16)for y in(-16,16)],3.4,-1,5)
    add('fan-guard',fan,at=(-157,YY-100,33),material='PETG')
    camera_stage()
    # Vertical bearing fit coupons, with readable engraved dimension labels.
    for size in (39.98,40.04,40.06):
        s=cyl(size,7).union(box(48,8,2,(0,-19,0)))
        s=s.cut(cq.Workplane('XY').text(f'{size:.2f}',4,1).translate((0,-19,1.2)))
        add(f'journal-fit-{size:.2f}',s,'coupon')
    for size in (52.00,52.03,52.08):
        s=ring(64,size,7).union(box(50,8,2,(0,-27,0)))
        s=s.cut(cq.Workplane('XY').text(f'{size:.2f}',4,1).translate((0,-27,1.2)))
        add(f'housing-fit-{size:.2f}',s,'coupon')

def mesh(s):
    v,f=s.tessellate(.12,.15)
    m=trimesh.Trimesh(vertices=[p.toTuple() for p in v],faces=f,process=True)
    m.fix_normals()
    return m

def exports():
    OUT.mkdir(exist_ok=True)
    expected_names={p['name'] for p in PARTS}
    for old in OUT.iterdir():
        if old.suffix in ('.stl','.step') and old.stem not in expected_names:old.unlink()
    assy=cq.Assembly(name='PGFUN_two_axis_positioner')
    records=[]; display=[]; qa={}
    for p in PARTS:
        name=p['name']; solid=p['solid']; world=p['world']
        # Plates are flat on their largest face; bearing journals retain Z axes.
        printed=solid
        if name in ('bridge','yaw-journal','pitch-journal','yaw-bearing-cartridge'):
            printed=solid.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
        elif name=='camera-riser-top':
            printed=solid.rotate(cq.Vector(0,0,0),cq.Vector(1,0,0),180)
        elif name in ('left-cheek','right-cheek','fork','camera-lens-upright') or name.startswith('liner-'):
            printed=solid.rotate(cq.Vector(0,0,0),cq.Vector(0,1,0),-90)
        bounds=printed.BoundingBox()
        printed=printed.translate(cq.Vector(-bounds.xmin,-bounds.ymin,-bounds.zmin))
        cq.exporters.export(printed,str(OUT/f'{name}.stl'),tolerance=.025,angularTolerance=.12)
        # Individual STEP, printable STL and viewer payload share the bed frame.
        piece=cq.Assembly(printed,name=name,color=cq.Color(.18,.28,.31))
        piece.export(str(OUT/f'{name}.step'))
        flute_payload.cut(OUT/f'{name}.step',OUT/f'{name}.stl',verbose=False,
                          preserve_print_triangles=True)
        m=trimesh.load(OUT/f'{name}.stl',force='mesh')
        if not m.is_watertight or not m.is_volume:
            raise ValueError(f'{name}: STL is not a closed positive volume')
        dimensions=m.extents.round(3).tolist()
        if any(a>b for a,b in zip(dimensions,(325,320,320))):
            raise ValueError(f'{name}: exceeds H2C build volume')
        records.append(dict(name=name,material=p['material'],quantity=p['quantity'],
            volume_cm3=round(solid.Volume()/1000,3),solid_mass_g=round(solid.Volume()/1000*(1.22 if p['material']=='TPU' else 1.34 if p['material']=='PET-CF17' else 1.27),2),
            print_bounds_mm=dimensions,support_required=name in ('fork','left-cheek','right-cheek',
                'motor-pedestal','yaw-bearing-cartridge','yaw-journal','pitch-journal',
                'camera-riser-base','camera-riser-top','camera-lens-upright',
                'umbilical-post-base','umbilical-post-top','umbilical-saddle')or name.startswith('gun-retainer-'),
            watertight=True,sha256=hashlib.sha256((OUT/f'{name}.stl').read_bytes()).hexdigest()))
        if p['group']!='coupon':
            assy.add(world,name=name,color=cq.Color(.18,.28,.31))
            dm=mesh(world)
            qa[name+'__v']=dm.vertices;qa[name+'__f']=dm.faces
            display.append(dict(name=name,group=p['group'],category='liner' if p['material']=='TPU' else 'print',v=dm.vertices.round(2).flatten().tolist(),f=dm.faces.flatten().tolist()))
    for p in HARDWARE:
        assy.add(p['world'],name=p['name'],color=cq.Color(.48,.5,.52))
        dm=mesh(p['world'])
        qa[p['name']+'__v']=dm.vertices;qa[p['name']+'__f']=dm.faces
        display.append(dict(name=p['name'],group=p['group'],category='motor' if 'motor' in p['name'] else 'metal',v=dm.vertices.round(2).flatten().tolist(),f=dm.faces.flatten().tolist()))
    assy.export(str(HERE/'assembly.step'))
    payload=[]
    for p in PARTS+HARDWARE:
        if p.get('group')=='coupon':continue
        pm=mesh(p['world']);pos,nrm,idx,fac=flute_payload.creased(pm)
        payload.append(dict(name=p['name'],color=[.18,.28,.31] if 'material' in p else [.48,.5,.52],
                            pos=pos.ravel().tolist(),nrm=nrm.ravel().tolist(),idx=idx.ravel().tolist(),fac=fac.tolist()))
    _mesh_payload.write(payload,str(HERE/'assembly.step.mesh'),
                        src=_mesh_payload.source_digest(HERE/'assembly.step'),cut={'dev':0,'bound':0})
    np.savez_compressed(HERE/'assembly-meshes.npz',**qa)
    (HERE/'print-manifest.json').write_text(json.dumps(dict(design=D,parts=records),indent=2)+'\n')
    (HERE/'display-meshes.json').write_text(json.dumps(display,separators=(',',':')))
    # Canonical mechanical/firmware binding contains only motion-relevant geometry.
    motion=dict(D)
    sources=[HERE/'build.py',ROOT/'hardware/reference/xlaserlab-sup29f-xh/source/reconstructed-surfaces.npz',
             ROOT/'hardware/reference/xlaserlab-sup29f-xh/xlaserlab_sup29f_xh.py',
             ROOT/'hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py',
             ROOT/'hardware/printed-parts/fixtures/weld-rotator/_rotator_interface.py']
    motion['mechanical_sources']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    encoded=json.dumps(motion,sort_keys=True,separators=(',',':')).encode()
    (HERE/'motion-geometry.json').write_text(json.dumps(dict(motion=motion,sha256=hashlib.sha256(encoded).hexdigest()),indent=2)+'\n')
    with zipfile.ZipFile(HERE/'print-pack.zip','w',compression=zipfile.ZIP_DEFLATED) as pack:
        for p in OUT.glob('*.stl'): pack.write(p,p.name)
        pack.write(HERE/'design.json','design.json')
        pack.write(HERE/'print-manifest.json','print-manifest.json')
    print(json.dumps(dict(print_parts=len(records),solid_grams=round(sum(p['solid_mass_g']for p in records),1),assembly=str(HERE/'assembly.step'))))

if __name__=='__main__':
    build(); exports()
