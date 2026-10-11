"""The Pour: individually printed studies assembled as an exposed descending stream.

Run manually with HSM_NO_BUILD_LOCK=1. Every STL uses its own manufacturing
frame; assembly placements are storage/display poses, not slicer rotations.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(ROOT / "hardware/scripts"),
                str(ROOT / "hardware/printed-parts/cadlib"),
                str(ROOT / "hardware/printed-parts/enclosure/enclosure")]
from _cadq_export import export_assembly
from _material_base import M_PETGF_BLACK, one_body
from _grip_interface import GripInterface
from print_mesh import write_print_stl

PARTS = HERE / "parts"
NECK_SOURCE = ROOT / "hardware/printed-parts/faucet/finish-coupons/scarf-swatches-v1/faucet-neck-swatch.step"
NECK_SOURCE_STL = NECK_SOURCE.with_suffix(".stl")
NECK_IDS = ("N08", "N12", "N24", "NR00", "NR05", "NR15", "NS00", "NS10", "NS20")
SLIDER_GAPS = (0.05, 0.15, 0.25, 0.35, 0.45)
BASE_T = 6.2
DOCK_DIAMETER = 6.0
DOCK_AIR_DIAMETRAL = 0.3
DOCK_HEIGHT = 2.0
VERSION = "POUR V2"
MASTER_DATE = "2026-10-11"
SLIDER_X = (-68, -34, 0, 34, 68)
Q_CENTERS = (-49, 0, 49)
Q_Y = 64.0
SOURCE_ORIGIN = (0, -1, 66.45)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def rounded(width, depth, height, *, z=0.0, radius=2.0):
    return (cq.Workplane("XY").workplane(offset=z).rect(width, depth)
            .extrude(height).edges("|Z").fillet(radius).val())


def letters(value, size, height, z, *, x=0.0, y=0.0):
    return (cq.Workplane("XY").workplane(offset=z).text(value, size, height,
            font="Arial", kind="bold", halign="center", valign="center", combine=False)
            .val().translate((x, y, 0)))


def mark(shape, value, x, y, z, *, size=4.0, inset=False):
    text = letters(value, size, .49 if not inset else .50,
                   z-.01 if not inset else z-.48, x=x, y=y)
    return (shape.cut(text) if inset else shape.fuse(text)).clean()


def label_window(value, size, x, y, surface_z):
    """Exact glyph footprint, separate from the backing face's deposition."""
    shape = letters(value, size, .48, surface_z, x=x, y=y)
    b = shape.BoundingBox()
    return dict(text=value, font="Arial", font_kind="bold", font_size_mm=size,
                nominal_raise_mm=.48, surface_z_mm=surface_z,
                bounds_mm=[[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]])


def peg(x, y, z):
    return cq.Solid.makeCylinder(DOCK_DIAMETER/2, DOCK_HEIGHT+.1,
                                cq.Vector(x, y, z-.1))


def socket(shape, x, y):
    return shape.cut(cq.Solid.makeCylinder((DOCK_DIAMETER+DOCK_AIR_DIAMETRAL)/2,
                     DOCK_HEIGHT+.35, cq.Vector(x, y, -.1))).clean()


def capture_inputs():
    """Capture once; later runs read only this object's compressed snapshots."""
    folder = HERE / "inputs"
    folder.mkdir(parents=True, exist_ok=True)
    for source in (NECK_SOURCE, NECK_SOURCE_STL):
        target = folder / (source.name + ".gz")
        if not target.exists():
            target.write_bytes(gzip.compress(source.read_bytes(), mtime=0))
    step_bytes = gzip.decompress((folder / "faucet-neck-swatch.step.gz").read_bytes())
    stl_bytes = gzip.decompress((folder / "faucet-neck-swatch.stl.gz").read_bytes())
    return step_bytes, stl_bytes, {
        "source_step": str(NECK_SOURCE.relative_to(ROOT)),
        "source_step_sha256": hashlib.sha256(step_bytes).hexdigest(),
        "source_stl": str(NECK_SOURCE_STL.relative_to(ROOT)),
        "source_stl_sha256": hashlib.sha256(stl_bytes).hexdigest(),
        "snapshot_step": "inputs/faucet-neck-swatch.step.gz",
        "snapshot_stl": "inputs/faucet-neck-swatch.stl.gz",
        "source_pose": "Frozen production -15 degree X pose; no additional rotation",
        "geometry_change": "Rigid XY recentering only; every source STL triangle retained",
    }


def neck_geometry():
    step_bytes, stl_bytes, provenance = capture_inputs()
    with tempfile.TemporaryDirectory(prefix="the-pour-neck-") as temp:
        step_path = Path(temp) / "neck.step"
        stl_path = Path(temp) / "neck.stl"
        step_path.write_bytes(step_bytes)
        stl_path.write_bytes(stl_bytes)
        shape = cq.importers.importStep(str(step_path)).val()
        mesh = trimesh.load_mesh(stl_path, process=False)
    b = shape.BoundingBox()
    offset = np.array([-(b.xmin+b.xmax)/2, -(b.ymin+b.ymax)/2, 0.0])
    shape = shape.translate(tuple(offset))
    mesh.vertices += offset
    provenance["recenter_translation_mm"] = offset.tolist()
    return shape, mesh, provenance


def rotation_matrix(rotation=(0, 0, 0), placement=(0, 0, 0)):
    result = np.eye(4)
    for axis, angle in enumerate(rotation):
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        r = (np.array([[1,0,0],[0,c,-s],[0,s,c]]),
             np.array([[c,0,s],[0,1,0],[-s,0,c]]),
             np.array([[c,-s,0],[s,c,0],[0,0,1]]))[axis]
        result[:3,:3] = r @ result[:3,:3]
    result[:3,3] = placement
    return result


def pose(shape, placement=(0,0,0), rotation=(0,0,0)):
    for axis, angle in zip(((1,0,0),(0,1,0),(0,0,1)), rotation):
        if angle:
            shape = shape.rotate((0,0,0), axis, angle)
    return shape.translate(placement)


def transform_shape(shape, matrix):
    from source_features import transform_shape as rigid_transform
    return rigid_transform(shape, matrix)


def euler_xyz(matrix):
    r = np.asarray(matrix)[:3,:3]
    y = math.asin(max(-1., min(1., -r[2,0])))
    if abs(math.cos(y)) > 1e-8:
        x, z = math.atan2(r[2,1],r[2,2]), math.atan2(r[1,0],r[0,0])
    else:
        x, z = math.atan2(-r[1,2],r[1,1]), 0.
    return [math.degrees(v) for v in (x,y,z)]


def bounds(shape):
    b = shape.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]


def inner_section(shape, z, air=.15):
    wires = cq.Workplane(obj=shape).section(z).val().Wires()
    # A complete planar section contains one outside and one or more passages.
    wires = sorted(wires, key=lambda w: cq.Face.makeFromWires(w).Area(), reverse=True)
    if len(wires) < 2:
        raise ValueError(f"No source passage at Z{z}")
    wire = wires[1]
    original_area = cq.Face.makeFromWires(wire).Area()
    candidates = wire.offset2D(air) + wire.offset2D(-air)
    inside = [w for w in candidates if cq.Face.makeFromWires(w).Area() < original_area]
    return max(inside, key=lambda w: cq.Face.makeFromWires(w).Area())


def ribbon(points, width=7., thickness=4.):
    wires=[]
    for i,(x,y,z) in enumerate(points):
        a,b=points[max(0,i-1)],points[min(len(points)-1,i+1)]
        dx,dy=b[0]-a[0],b[1]-a[1]
        length=math.hypot(dx,dy)
        if length < .001:
            dx,dy,length=1.,0.,1.
        nx,ny=-dy/length,dx/length
        v=[cq.Vector(x+side*nx*width/2,y+side*ny*width/2,z+up*thickness/2)
           for side,up in ((-1,-1),(1,-1),(1,1),(-1,1))]
        wires.append(cq.Wire.makePolygon(v+[v[0]]))
    return cq.Solid.makeLoft(wires, ruled=False)


def stations():
    return [(52*math.cos(math.radians(135+45*j)),
             52*math.sin(math.radians(135+45*j)),29+9.5*j) for j in range(9)]


def root_apron():
    wall = box(-56.8,-16.8,43,50.,BASE_T,24)
    # Production field profile: 4 mm half-ellipse, depth 1.2, pitch 5.1221.
    # Fade is 5 mm at each end; 5.8 mm intact backing remains at full depth.
    zs=[BASE_T+v for v in (0,1.25,2.5,3.75,5)] + [19.,20.25,21.5,22.75,24.]
    for x in (-52.6,-47.4779,-42.3558,-37.2337,-32.1116,-26.9895,-21.8674):
        wires=[]
        for z in zs:
            t=min(1.,(z-BASE_T)/5.,(24-z)/5.)
            fraction=t*t*(3-2*t)
            d=max(.0001,1.2*fraction)
            pts=[(x-2,51.0),(x+2,51.0)]
            pts.extend((x+2*math.cos(a),50.0-d*math.sin(a))
                       for a in np.linspace(0,math.pi,17))
            vectors=[cq.Vector(xx,yy,z) for xx,yy in pts]
            wires.append(cq.Wire.makePolygon(vectors+[vectors[0]]))
        wall=wall.cut(cq.Solid.makeLoft(wires,ruled=True))
    for x in (-51,-23):
        wall=wall.fuse(box(x-3,x+3,43.6,46.6,3.45,BASE_T+.1))
    return wall.clean()


def helix_body():
    points=[(70*math.cos(math.radians(135+360*j/64)),
             70*math.sin(math.radians(135+360*j/64)),20+76*j/64) for j in range(65)]
    body=ribbon(points)
    for j,point in enumerate(stations()):
        pod=rounded(12.5,14.5,8,z=-11,radius=1)
        pod=pod.cut(box(-3.25,3.25,-4.25,4.25,-5.75,-2.9))
        pod=pod.fuse(box(5,21.5,-3.5,3.5,-11,-7))
        body=body.fuse(pose(pod,point,(-25,0,135+45*j)))
    body=body.fuse(root_apron())
    # Open interior top socket on the source R6 buttress. The bearing lands
    # and exterior expanding and inward rounds remain exposed.
    top=BASE_T+21.054223
    landing=box(56.6,67.4,18,32,top,top+3)
    landing=landing.fuse(box(59,65,21,29,top-2.75,top+.1))
    brace=ribbon([(62,25,top+2),(49,51,34),(-22,51,34),(-36.76955,36.76955,18.5)])
    body=body.fuse(landing).fuse(brace)
    # Three compact source-angle fin seats share the interior structural root.
    for x in (-13,0,13):
        landing=rounded(12,24,3,z=26.5,radius=1.5).translate((x,31,0))
        for y in (24,36):
            landing=landing.fuse(peg(x,y,29.5))
        body=body.fuse(landing)
    body=body.fuse(box(-19,19,20,23,26.5,29.5))
    body=body.fuse(ribbon([(-36.77,36.77,18.5),(-22,21.5,26),(-17,21.5,27.5)]))
    # The intact grip receiver is an exposed side column. A top-only storage
    # cup accepts its solid upper footer, away from the actual wing slots.
    cup=box(-84.65,-74.85,-9.15,12.15,100.95,107.2)
    cup=cup.cut(box(-84.75,-77.85,-6.15,9.15,100.9,104.5))
    body=body.fuse(cup).fuse(ribbon([(-79.75,1.5,106),(-67,38,101),(-49.497475,49.497475,96)]))
    # Apply moving seats after all structural fusions, so the ribbon cannot
    # refill a socket or creep into a source specimen's cut-plane envelope.
    body=body.cut(box(-84.75,-77.85,-6.15,9.15,100.9,104.5))
    for j,point in enumerate(stations()):
        cavity=box(-3.25,3.25,-4.25,4.25,-5.75,-2.9)
        clear=box(-14.1,14.1,-28,18,-3,25)
        body=body.cut(pose(cavity,point,(-25,0,135+45*j)))
        body=body.cut(pose(clear,point,(-25,0,135+45*j)))
    return body.clean()


def source_host_foot(host):
    from mount_geometry import source_host_foot as safe_foot
    return safe_foot(host, origin=SOURCE_ORIGIN)


def pip_shutter(center, gap):
    # Closed eye starts on the bed; only the upper retaining contact is swept.
    roof=6.44+gap
    top=roof+2.40
    eye=box(center-3,center+3,Q_Y-5.15,Q_Y+5.15,0,top)
    eye=eye.cut(box(center-3.1,center+3.1,Q_Y-2.15,Q_Y+2.15,2.60,roof))
    eye=cq.Workplane(obj=eye).faces("<Z").edges().chamfer(.30).val()
    flag=rounded(13,14.15,1.6,z=top,radius=.6).translate((center,Q_Y-1.925,0))
    eye=eye.fuse(flag)
    eye=mark(eye,f".{round(gap*100):02d}",center,Q_Y-5.6,top+1.6,size=4.)
    return eye.clean(), top+1.6


def basin_body(host):
    body=rounded(174,144,BASE_T,radius=12)
    for center in Q_CENTERS:
        body=body.cut(box(center-16.35,center+16.35,Q_Y-5.5,Q_Y+5.5,-.1,BASE_T+.1))
        # Widen just the bed mouth: both first-layer gap edges recede .30 mm.
        wires=[]
        for z,w,d in ((-.1,33.3,11.6),(.30,32.7,11.0)):
            wires.append(cq.Workplane("XY").workplane(offset=z).rect(w,d).val().translate((center,Q_Y,0)))
        body=body.cut(cq.Solid.makeLoft(wires,ruled=True))
        for side in (-1,1):
            a,b=sorted((center+side*19.5,center+side*22.5))
            body=body.fuse(box(a,b,Q_Y-6,Q_Y+6,BASE_T-.1,11.2))
        body=body.fuse(box(center-19.6,center+19.6,Q_Y-1.8,Q_Y+1.8,4.04,6.44))
        # Smooth covered/revealed datum: record initial release here by hand.
        body=body.cut(box(center-6.5,center+6.5,55,58.3,BASE_T-.12,BASE_T+.1))
    for x in SLIDER_X:
        for dx in (-10,10):
            body=body.fuse(peg(x+dx,-40,BASE_T))
    for x,y in ((-30.5,1),(0,37.5),(31,1)):
        for dx in (-9,9):
            body=body.fuse(peg(x+dx,y+9.5,BASE_T))
    for x in (-51,-23):
        body=body.cut(box(x-3.15,x+3.15,43.45,46.75,3.2,BASE_T+.1))
    for y in (7,43):
        body=body.fuse(peg(65,y,BASE_T))
    body=body.fuse(box(-78,-75,-4,4,BASE_T-.1,12.2))
    body=body.fuse(box(-80,-77.9,-2,2,7.7,10.7))
    body=body.fuse(source_host_foot(host))
    # Accessible smooth identity/date/material patch and adjacent raking-light
    # datum, with no recipes or implementation details on the show surfaces.
    body=mark(body,"BATCH / DATE",-64,16,BASE_T,size=4.)
    body=mark(body,"THE POUR",0,-68,BASE_T,size=4.3)
    body=mark(body,"X / SIDE",-59,-68,BASE_T,size=4.)
    body=mark(body,".25 MOVE",57,-68,BASE_T,size=4.)
    body=mark(body,"Z TOP",-64,51,BASE_T,size=4.)
    body=mark(body,"Y .35/SIDE",33,51,BASE_T,size=4.)
    for x,d in ((-78,4.4),(78,6.65)):
        body=body.cut(cq.Solid.makeCylinder(d/2,BASE_T+1,cq.Vector(x,40,-.1)))
        body=mark(body,f"{d:.2f}",x,46,BASE_T,size=4.)
    # Version identity is an underside recess, above the nominal bed plane.
    body=body.cut(letters(VERSION,4.0,.49,-.01,x=0,y=-22).mirror("YZ"))
    body=body.cut(letters("MASTER "+MASTER_DATE,4.0,.49,-.01,x=0,y=-27).mirror("YZ"))
    return body.clean()


def slide_receiver(gap):
    body=rounded(30.8,42,10.06,radius=2)
    body=body.cut(box(-9-gap,9+gap,-22,22,3,7.06))
    body=body.cut(box(-12.4,12.4,-22,22,3,5.38))
    body=body.cut(box(-12.45,12.45,-14,14,7.06,10.2))
    for x in (-10,10):
        body=socket(body,x,0)
    if abs(gap-.25)<1e-8:
        # Two tiny rear-cut-edge saddles park the complete relaxed cover. All
        # storage additions lie outside the open functional sliding channel.
        for side in (-1,1):
            x=side*13.6
            body=body.fuse(box(x-1,x+1,6.6,9.2,10.05,10.5))
            a,b=sorted((side*15.05,side*18.05))
            body=body.fuse(box(a,b,6,9.2,10.05,12.9))
            a,b=sorted((side*12.8,side*18.05))
            body=body.fuse(box(a,b,4,7,10.05,12.9))
    body=mark(body,f"{gap:.2f}",0,17.8,10.06,size=4.)
    return body.clean()


def slide_tongue(gap):
    body = rounded(18, 29, 3.36, radius=.6)
    for side in (-1, 1):
        body = body.fuse(rounded(3.4, 23, 1.68, radius=.6).translate((side*9.7, 0, 0)))
    tab = rounded(26, 6, 4.2, radius=2).translate((0, -16.5, 0))
    body = body.fuse(tab)
    body = mark(body, f"{gap:.2f}", 0, -16.5, 4.2, size=4.0)
    return body.clean()


def roof_sample(identifier):
    # The open front and sides leave the cantilever's entire underside and
    # automatically generated support tree accessible for removal.
    body = rounded(30, 9, 3, radius=1).translate((0, 9.5, 0))
    body = body.fuse(box(-15, 15, 9, 13, 2.9, 20))
    body = body.fuse(box(-15, 15, -12, 13, 17, 20))
    # Same label pad and footprint on all three specimens.
    body = body.fuse(rounded(24, 7, 3, z=20, radius=1).translate((0, 9.5, 0)))
    body = mark(body, identifier, 0, 9.5, 23, size=4.0)
    for x in (-9, 9):
        body = socket(body, x, 9.5)
    return body.clean()


def transverse_round():
    # Orthogonal R6 convex show shoulder in XZ, extrusion along Y. It is a
    # true manufacturing azimuth comparison with the blade's YZ R6 shoulder.
    return (cq.Workplane("XZ", origin=(-6, -13, 3))
            .moveTo(0, 0).lineTo(12, 0).lineTo(12, 6)
            .threePointArc((6+6/math.sqrt(2), 6+6/math.sqrt(2)), (6, 12))
            .lineTo(0, 12).close().extrude(7).val())


def curve_blade(identifier):
    y, z = -17.0, 4.0
    points = [(y, z)]
    facets = []
    for angle in range(0, 91, 15):
        yy, zz = y+6*math.cos(math.radians(angle)), z+6*math.sin(math.radians(angle))
        facets.append((angle, (y+yy)/2, (z+zz)/2))
        y, z = yy, zz
        points.append((y, z))
    q = math.sqrt(2)
    profile = cq.Workplane("YZ", origin=(-4, 0, 0)).polyline(points).lineTo(y, 80)
    profile = profile.threePointArc((y-6+6/q, 80+6/q), (y-6, 86)).lineTo(-9, 86)
    profile = profile.threePointArc((-9-6/q, 80+6/q), (-15, 80)).lineTo(-12, 80)
    profile = profile.threePointArc((-9-3/q, 80+3/q), (-9, 83)).lineTo(y-9, 83)
    profile = profile.threePointArc((y-9+6/q, 77+6/q), (y-3, 77))
    profile = profile.lineTo(y-3, z+3)
    for yy, zz in reversed(points[:-1]):
        profile = profile.lineTo(yy-3, zz+3)
    profile = profile.lineTo(-20, 2).lineTo(-17, 2).close()
    body = profile.extrude(8).val()
    foot = rounded(12, 24, 3, radius=1.5).translate((0,-10,0))
    body = body.fuse(foot).fuse(transverse_round())
    for yy in (-15, -3):
        body = socket(body, 0, yy)
    id_text=(cq.Workplane("YZ",origin=(-4.49,0,0)).text(identifier,4.,.49,
             font="Arial",kind="bold",combine=False).val()
             .rotate((0,0,0),(1,0,0),90).translate((0,7.2826,50)))
    body=body.fuse(id_text)
    ib=id_text.BoundingBox()
    body = mark(body, "X", -3, -17, 15, size=4.0)
    # Values are angles of the outside ramp surface above the bed, measured
    # in the YZ manufacturing plane. Markings are on the side, off that face.
    side_labels = []
    for angle, yy, zz in facets:
        radians = math.radians(angle)
        # Follow the facet tangent. The complete glyph remains inside the
        # ramp's side stock, clear of the outside comparison surface. The
        # first facet lies behind the transverse shoulder, so its numeral
        # belongs on that shoulder's actual outboard side face.
        face_x = 6.0 if angle == 0 else 4.0
        cy, cz = yy-1.5*math.sin(radians), zz+1.5*math.cos(radians)
        text = (cq.Workplane("YZ", origin=(face_x-.01, 0, 0))
                .text(str(angle), 3.6, .49, font="Arial", kind="bold", combine=False).val()
                .rotate((0, 0, 0), (1, 0, 0), angle).translate((0, cy, cz)))
        body = body.fuse(text)
        b = text.BoundingBox()
        side_labels.append(dict(text=str(angle), font="Arial", font_kind="bold",
                                font_size_mm=3.6, nominal_raise_mm=.48,
                                surface_x_mm=face_x, view_axis="x",
                                bounds_mm=[[face_x, b.ymin, b.zmin],
                                           [face_x+.48, b.ymax, b.zmax]]))
    windows = [dict(text=identifier,font="Arial",font_kind="bold",font_size_mm=4.,
                    nominal_raise_mm=.48,surface_x_mm=-4.,view_axis="x",
                    outward_sign=-1,bounds_mm=[[-4.48,ib.ymin,ib.zmin],[-4.,ib.ymax,ib.zmax]]),
               label_window("X", 4.0, -3, -17, 15)] + side_labels
    facet_rows = [{"angle_above_bed_degrees": a,
                   "midpoint_print_yz_mm": [yy, zz]} for a, yy, zz in facets]
    return body.clean(), facet_rows, windows


def grip_interface():
    # Full production span. The original interface's cover/slot construction
    # is reused with explicit local dimensions; no enclosure rebuild occurs.
    grip = GripInterface.__new__(GripInterface)
    grip.shell = SimpleNamespace(handhold_length=80.0, handhold_wall=3.0)
    for name, value in dict(BODY_AIR=.15, LENGTH=79.7, WIDTH=11.558203932499373,
                            THICK=3.36, WING_THICK=1.68, WING_REACH=2.4,
                            WING_SPAN=5.0, WING_END_R=.6, CORNER_R=.6,
                            TOUCH_R=.6, WING_END_AIR=.15, BEARING_AIR=.45,
                            BACK_AIR=.25, ENTRY_WIDTH=1.1, ENTRY_DEPTH=.4).items():
        setattr(grip, name, value)
    return grip


def grip_receiver(grip):
    # A complete pair of 3mm end walls, with the accepted open rear slot exit
    # and full 12mm structural roof stock. Rear web makes it one rigid part.
    body = box(-45, 45, 6.0, 9.0, 0, 14.38)
    for side in (-1, 1):
        a, b = sorted((side*40, side*43))
        body = body.fuse(box(a, b, -6.1, 9, 0, 14.38))
    # Endwall receiver rests on a bridge with a quarter-millimetre supported
    # back datum; the complete strip is installed with its finger face up.
    for x in (-46, 46):
        body = body.fuse(box(x-3, x+3, -6, 9, 0, 3.5))
    body=body.cut(box(-47.65,-44.35,-2.15,2.15,-.1,2.3))
    for slot in grip.receiver_slots():
        body = body.cut(slot.translate((0, 0, .25)))
    return body.clean()


def neck_shoe(identifier, neck):
    """Cut-face foot and existing-passage locator; no outside cage."""
    face=max((f for f in neck.Faces() if f.BoundingBox().zlen<1e-5 and
              abs(f.Center().z)<1e-5),key=lambda f:f.Area())
    body=cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),cq.Vector(0,0,-3))
    body=body.fuse(box(-11,11,-2,2,-3,0))
    locator=cq.Solid.makeLoft([inner_section(neck,z) for z in (0,.9,1.8)])
    body=body.fuse(locator)
    body=body.fuse(box(-2,2,-2,2,-.1,19.3))
    body=body.fuse(box(-3.2,3.2,-2.5,2.5,19.2,20.4))
    body=body.fuse(box(-6,6,-21,-15,-3,-1))
    body=body.fuse(rounded(16,6,3,z=-3,radius=1).translate((0,-23,0)))
    body=body.fuse(box(-3,3,-4,4,-5.5,-2.9))
    return mark(body,identifier,0,-23,0,size=4.).clean()


def neck_keeper(identifier):
    # Open +Y T-slot accepts the foot head. Gravity slides the keeper toward
    # +Y against its closed -Y stop; uphill -Y extraction opens it. Roof .30.
    body=rounded(27.4,9,4.2,z=18.3,radius=.6)
    body=body.cut(box(-2.15,2.15,-2.65,4.6,18.29,19.35))
    body=body.cut(box(-3.35,3.35,-2.65,4.6,19.05,20.7))
    return mark(body,identifier,0,0,22.5,size=4.).clean()


def r6_docked(feature):
    body=feature.shape
    for y in (-18,18):
        body=socket(body,0,y)
    top=body.BoundingBox().zmax
    # Open top at every manufacturing layer; no new docking ceiling.
    body=body.cut(box(-6.15,.15,-4.15,4.15,top-3,top+.1))
    return body.clean()


def pip_probes(identifier, center, gap):
    def region(x0,x1,y0,y1,z0,z1):
        return [[center+x0,Q_Y+y0,z0],[center+x1,Q_Y+y1,z1]]
    top=dict(name="Z TOP retaining rail",fixed_body_id="P",moving_body_id=identifier,
        fixed_surface="top",moving_surface="bottom",
        fixed_contact_bounds_mm=region(-2.8,2.8,-1.5,1.5,4.04,6.44),
        moving_contact_bounds_mm=region(-2.8,2.8,-1.5,1.5,6.44+gap,8.84+gap),
        support_gap_bounds_mm=region(-2.8,2.8,-1.5,1.5,6.44,6.44+gap),
        nominal_fixed_surface_z_mm=6.44,nominal_moving_surface_z_mm=6.44+gap,
        requested_gap_mm=gap)
    lower=dict(name="Fixed lower rail gap",fixed_body_id="P",moving_body_id=identifier,
        fixed_surface="bottom",moving_surface="top",
        fixed_contact_bounds_mm=region(-2.8,2.8,-1.5,1.5,4.04,6.44),
        moving_contact_bounds_mm=region(-2.8,2.8,-1.5,1.5,0,2.60),
        support_gap_bounds_mm=region(-2.8,2.8,-1.5,1.5,2.60,4.04),
        nominal_fixed_surface_z_mm=4.04,nominal_moving_surface_z_mm=2.60,
        requested_gap_mm=1.44)
    rail=[]
    for side in (1,-1):
        rail.append(dict(name=("+Y" if side>0 else "-Y")+" running air per side",
            fixed_body_id="P",moving_body_id=identifier,
            line_xy_mm=[[center,Q_Y],[center,Q_Y+side*6]],print_z_mm=[4.2,6.2],
            fixed_interval_mm=[1.2,1.8],moving_interval_mm=[2.15,3.0],requested_gap_mm=.35))
        rail.append(dict(name=("+Y" if side>0 else "-Y")+" first-layer mouth/foot air",
            fixed_body_id="P",moving_body_id=identifier,
            line_xy_mm=[[center,Q_Y],[center,Q_Y+side*7]],print_z_mm=[.19,.21],
            fixed_interval_mm=[5.5,6.5],moving_interval_mm=[4.1,5.2],requested_gap_mm=.70,
            nominal_cad_midplane_z_mm=.10))
    return dict(native_release_probes=[top,lower],native_gap_probes=rail,
        native_body_window=dict(bounds_mm=region(-1.5,1.5,-1.5,1.5,0,2.60)))


def collision_review(placed):
    """One manual rigid CAD overlap review of this composition's parked pose."""
    rows=[]
    candidates=0
    for i,(aid,a) in enumerate(placed):
        ab=a.BoundingBox()
        for bid,b in placed[i+1:]:
            bb=b.BoundingBox()
            if any(hi <= lo+1e-5 for hi,lo in (
                (min(ab.xmax,bb.xmax),max(ab.xmin,bb.xmin)),
                (min(ab.ymax,bb.ymax),max(ab.ymin,bb.ymin)),
                (min(ab.zmax,bb.zmax),max(ab.zmin,bb.zmin)))):
                continue
            candidates+=1
            volume=a.intersect(b).Volume()
            if volume>.001:
                rows.append(dict(parts=[aid,bid],rigid_overlap_mm3=volume))
    return dict(scope="Nominal parked-pose solid intersections; face bearing is allowed. No elastic seating, printed tolerance, load or lifetime prediction.",
                pairs_considered=len(placed)*(len(placed)-1)//2,
                broad_phase_candidates=candidates,positive_overlaps=rows)


def main():
    import source_features as sf
    from viewer_payload import write_reference_payloads
    PARTS.mkdir(parents=True,exist_ok=True)
    neck,neck_mesh,provenance=neck_geometry()
    source_host=sf.rigid_groove_host(crop_end_s_mm=55)
    source_cover=sf.industrial_cover()
    source_r6=sf.expanding_r6_surface()
    assembly=cq.Assembly(name="The Pour")
    rows=[]
    placed=[]
    leaf_shapes={}
    leaf_meshes={}
    written=set()

    def emit(identifier,name,shape,group="kit",*,placement=(0,0,0),rotation=(0,0,0),
             matrix=None,mesh=None,shared_frame=False,**details):
        if not shape.isValid() or len(shape.Solids())!=1:
            raise ValueError(f"{identifier}: expected one valid printable solid")
        display=rotation_matrix(rotation,placement) if matrix is None else np.asarray(matrix)
        low=shape.BoundingBox().zmin
        shift=0. if shared_frame or abs(low)<1e-5 else -low
        if shared_frame and low < -1e-5:
            raise ValueError(f"{identifier}: shared manufacturing body below bed")
        if shift:
            shape=shape.translate((0,0,shift))
            if mesh is not None:
                mesh=mesh.copy();mesh.vertices += (0,0,shift)
            adjust=np.eye(4);adjust[2,3]=-shift
            display=display@adjust
            for window in details.get("label_windows",[]):
                window["bounds_mm"][0][2]+=shift;window["bounds_mm"][1][2]+=shift
                if "surface_z_mm" in window:
                    window["surface_z_mm"]+=shift
        b=shape.BoundingBox()
        stem=identifier.lower()+"-"+name.lower().replace(" ","-")
        step,stl=PARTS/(stem+".step"),PARTS/(stem+".stl")
        export_assembly(one_body(cq.Workplane(obj=shape),f"{identifier} {name}",M_PETGF_BLACK),str(step))
        if mesh is None:
            mesh=write_print_stl(shape,stl)
        else:
            mesh.export(stl)
        checked=trimesh.load_mesh(stl,process=True)
        if not checked.is_watertight or len(checked.split())!=1 or checked.volume<=0:
            raise ValueError(f"{identifier}: expected one positive watertight STL body")
        posed=transform_shape(shape,display)
        assembly.add(posed,name=f"{identifier} {name}",color=M_PETGF_BLACK)
        placed.append((identifier,posed))
        leaf_shapes[identifier]=shape;leaf_meshes[identifier]=mesh
        written.update((step,stl,Path(str(step)+".mesh")))
        row=dict(id=identifier,name=f"{identifier} {name}",kind=details.pop("kind","kit"),
            stl=str(stl.relative_to(ROOT)),step=str(step.relative_to(ROOT)),
            stl_relative=str(stl.relative_to(HERE)),step_relative=str(step.relative_to(HERE)),
            group=group,print_group=group,rotation_x_degrees=0,
            print_bounds_mm=bounds(shape),stl_sha256=sha(stl),step_sha256=sha(step),
            assembly=dict(rotation_xyz_degrees=euler_xyz(display),translation_mm=display[:3,3].tolist()),
            geometry_check=dict(one_valid_solid=True,one_watertight_mesh_body=True,
                                triangle_count=len(checked.faces)),**details)
        rows.append(row)
        print(identifier,len(checked.faces),flush=True)
        return row

    pip=dict(id="PIP-BASE",frame="shared-manufacturing")
    p_labels=[label_window(t,size,x,y,BASE_T) for t,size,x,y in (
        ("BATCH / DATE",4.,-64,16),("THE POUR",4.3,0,-68),
        ("X / SIDE",4.,-59,-68),(".25 MOVE",4.,57,-68),
        ("Z TOP",4.,-64,51),("Y .35/SIDE",4.,33,51),
        ("4.40",4.,-78,46),("6.65",4.,78,46))]
    emit("P","basin and captive rails",basin_body(source_host),kind="carrier",shared_frame=True,
        print_assembly=pip,print_recipe=dict(initial_layer_height_mm=.20,layer_height_mm=.24,supports_enabled=False,
            wall_probes=[dict(name="rear locator continuous +Y land",line_xy_mm=[[0,10],[0,7]],
                             print_z_mm=[6.21,13.50],expected_wall_roads=2)]),
        label_windows=p_labels,bore_diameters_mm=[4.40,6.65],bores_print_xy_mm=[[-78,40],[78,40]],
        writable_batch_flat_mm=[[-77,20,BASE_T],[-51,39,BASE_T]],
        smooth_comparison_datum_mm=[[-80,34,BASE_T],[-59,39,BASE_T]],
        datum_scope="Smooth neighboring edge of the writable flat; clear prior ink before raking-light comparison",
        native_body_window=dict(bounds_mm=[[-8,-63,0],[8,-58,BASE_T]]),
        master_identity=dict(version=VERSION,date=MASTER_DATE,placement="Underside recessed .48 mm; mirrored for reading from below"),
        recessed_label_windows=[dict(text=t,font="Arial",font_kind="bold",font_size_mm=4.,
            view_axis="-z",surface_z_mm=0,nominal_recess_mm=.48,
            bounds_mm=bounds(letters(t,4.,.48,0,x=0,y=y).mirror("YZ")))
            for t,y in ((VERSION,-22),("MASTER "+MASTER_DATE,-27))],
        source_host_mount=dict(face="Native rear cut S55",bearing_thickness_mm=5.25,
            passage_locator_height_mm=1.8,minimum_locator_air_mm=.2015646773,
            locator_air_scope="Measured minimum in exact source passage; not uniform per-face air",scope="Reference-only rear-face adapter, not a snap stiffness specimen"))
    for center,gap in zip(Q_CENTERS,(.24,.48,.72)):
        identifier=f"Q{round(gap*100):02d}"
        shutter,label_z=pip_shutter(center,gap)
        emit(identifier,"captive ripple shutter",shutter,kind="pip_shutter",shared_frame=True,
            print_assembly=pip,top_release_gap_mm=gap,lower_release_gap_mm=1.44,
            y_running_air_per_side_mm=.35,first_layer_chamfer_mm=.30,travel_x_mm=26,
            bed_region_midplane_z_mm=.10,bed_region_y_air_per_side_mm=.70,
            print_recipe=dict(initial_layer_height_mm=.20,layer_height_mm=.24,supports_enabled=False),
            label_windows=[label_window(f".{round(gap*100):02d}",4.,center,Q_Y-5.6,label_z)],
            comparison="Z TOP only: bed-start eye around bridge rail; Y running air .35 per face. Solid skins differ from sparse supports.",
            initial_state_options=["Free off bed","Gently freed at intended handle","Fused"],
            **pip_probes(identifier,center,gap))
    emit("H","fluted helix and keyed fin docks",helix_body(),kind="helix_structure",
         print_recipe=dict(initial_layer_height_mm=.20,layer_height_mm=.24,supports_enabled=True),
         foot_key_air_per_side_mm=.25,static_key_air_per_side_mm=.15,
         flute_profile=dict(width_mm=4.,depth_mm=1.2,pitch_mm=5.1221,fade_each_end_mm=5.,minimum_backing_mm=5.8),
         removal="Lift vertically4mm from P root keys, R6 interior top socket and GR upper footer after unloading source samples",
         grip_column_dock="Upper cup open world -X; roof, Y side walls and inner backing remain. G/GR slide out together before N12 removal.")

    for x,gap,travel in zip(SLIDER_X,SLIDER_GAPS,(-12,-10,-8,-10,-12)):
        identifier=f"S{round(gap*100):02d}"
        emit(identifier+"R","sliding receiver",slide_receiver(gap),placement=(x,-40,BASE_T),
            kind="slider_receiver",body_side_air_each_mm=gap,floor_air_mm=.25,
            roof_air_above_wing_mm=.45,wing_tip_air_each_mm=1.,storage_seat_air_per_side_mm=.15,
            label_windows=[label_window(f"{gap:.2f}",4.,0,17.8,10.06)],
            comparison="Open synthetic flat-wing lane; X gap is per face, not diametral",
            source_cover_parking="Rear cut-edge saddles outside the functional channel" if identifier=="S25" else None)
        emit(identifier,"sliding tongue",slide_tongue(gap),placement=(x,-40+travel,BASE_T+3.25),
            kind="slider",body_side_air_each_mm=gap,body_width_mm=18,body_thickness_mm=3.36,
            wing_projection_mm=2.4,wing_thickness_mm=1.68,
            label_windows=[label_window(f"{gap:.2f}",4.,0,-16.5,4.2)],
            comparison="All five functional tongue geometries identical; only printed value differs")
    for x,y,identifier,gap in ((-30.5,1,"R30",.30),(0,37.5,"R45",.45),(31,1,"R60",.60)):
        emit(identifier,"support ceiling",roof_sample(identifier),f"support-{round(gap*100):03d}",
            placement=(x,y,BASE_T),kind="support",support_top_z_distance_mm=gap,
            support_ceiling_z_mm=17,ceiling_xy_bounds_mm=[[-15,-12],[15,9]],
            label_windows=[label_window(identifier,4.,0,9.5,23)],
            comparison="Identical 3 mm cantilever ceiling with three open removal directions")
    for x,identifier,height in ((-13,"A08",.08),(0,"A12",.12),(13,"A24",.24)):
        blade,facets,labels=curve_blade(identifier)
        emit(identifier,"angle and curve blade",blade,f"finish-{round(height*100):03d}",
            placement=(x,21,29.5),rotation=(0,0,180),kind="angle_blade",requested_layer_height_mm=height,
            angle_facets=facets,curve_radius_mm=6,nominal_curve_wall_mm=3,
            label_windows=labels,surface_azimuths=["YZ blade","XZ transverse shoulder"],
            comparison="Angles above manufacturing bed; display rotation does not change print azimuth",
            geometry_adaptation="Short storage heel, .15 per-side sockets and straight top bridge shortened6mm; active ramps/orthogonal R6 rounds retained")
    for j,(identifier,point) in enumerate(zip(NECK_IDS,stations())):
        rotation=(-25,0,135+45*j)
        emit(identifier+"D","neck cut-face foot",neck_shoe(identifier,neck),placement=point,rotation=rotation,
            kind="neck_shoe",neck_id=identifier,passage_locator_air_per_side_mm=.15,
            moving_key_mm=[6,8,2.5],moving_key_air_per_side_mm=.25,moving_key_floor_air_mm=.25,
            label_windows=[label_window(identifier,4.,0,-23,0)],
            comparison="Cut-face bearing and inset existing-passage locator, no exterior cage",
            whole_unit_removal=dict(local_normal_lift_mm=3.,radial_direction="Local +X away from the centre",
                radial_clearance_path_mm=50.,
                exception=("Slide G/GR together world -X10mm and set aside before radial withdrawal" if identifier=="N12" else
                           "After radial10mm, raise world +Z3mm before continuing to radial50mm" if identifier=="NS20" else None),
                scope="Sampled nominal rigid storage path; unprinted, no continuous sweep or friction qualification"))
        emit(identifier+"K","neck T-slot keeper",neck_keeper(identifier),placement=point,rotation=rotation,
            kind="neck_keeper",neck_id=identifier,cut_top_air_mm=.10,t_slot_air_per_side_mm=.15,
            t_slot_roof_air_mm=.30,print_recipe=dict(supports_enabled=False),label_windows=[label_window(identifier,4.,0,0,22.5)],
            removal="Slide keeper toward local negative Y7.2mm off its +Y opening; withdraw neck along its +15-degree Y/Z source axis",
            retention="Captures cut-face normal; closed -Y stop, open +Y slot; keeper removes -Y. Gravity seats the stop; not qualified for inversion")
        details=dict(kind="neck",source=provenance,
            withdrawal_axis_print_xyz=[0,math.sin(math.radians(15)),math.cos(math.radians(15))],
            withdrawal_path="Keeper off; translate manufacturing +Y by tan15 times +Z; sampled rigid CAD, unprinted",
            comparison="Unscaled source faucet neck; short section thermal conditions differ")
        if identifier in ("N08","N12","N24"):
            height=int(identifier[1:])/100;group=f"finish-{round(height*100):03d}"
            details.update(requested_layer_height_mm=height,seam_method="regular",seam_gap_percent=15)
        else:
            group="seam";details.update(requested_layer_height_mm=.12,
                seam_method="regular" if identifier.startswith("NR") else "scarf",
                seam_gap_percent=int(identifier[-2:]) if identifier.startswith("NR") else 15)
            if identifier.startswith("NS"):
                details["scarf_gap_percent"]=int(identifier[-2:])
        emit(identifier,"faucet neck",neck,group,placement=point,rotation=rotation,
             mesh=neck_mesh.copy(),**details)
    grip=grip_interface()
    emit("GR","grip receiver bridge",grip_receiver(grip),placement=(-78,0,55.2),rotation=(0,-90,0),
         kind="grip_receiver",source_path="hardware/printed-parts/enclosure/enclosure/_grip_interface.py",
         endwall_mm=3,roof_stock_mm=12,retaining_air_mm=.45,supported_back_air_mm=.25,
         geometry_adaptation="Solid storage footers; lower static key socket. Full production wing slots and span retained.",
         complete_module_removal="Slide G/GR together world -X10mm clear of the horizontal lower key and open upper H cup; set aside. Hand-support H while its left bearing is absent.")
    emit("G","complete grip insert",grip.cover(),"finish-008",placement=(-78.25,0,55.2),rotation=(0,-90,0),
         kind="grip",source_path="hardware/printed-parts/enclosure/enclosure/_grip_interface.py",
         overall_length_mm=84.5,body_length_mm=79.7,body_width_mm=grip.WIDTH,body_thickness_mm=3.36,
         comparison="Complete production broad strip and coplanar wings; side-mounted reference receiver",
         assembly_axes=dict(length="World +Z",fingerface="World -X",width="World +Y"),
         removal="Bow centre outboard toward world -X; disengage an upper/lower wing along world +/-Z")
    r6_shape=r6_docked(source_r6)
    emit("R6","expanding round structural buttress",r6_shape,"r6",placement=(65,25,BASE_T),kind="source_round",
         source=source_r6.metadata,print_recipe=source_r6.metadata["print_recipe"],
         geometry_adaptation="Two underside static storage sockets and open interior top key seat; source exterior intact")
    display=rotation_matrix((-90,0,180),SOURCE_ORIGIN)
    emit("FH","complete rigid groove host",source_host.shape,"host",kind="source_snap_host",
         matrix=display@np.array(source_host.metadata["print_to_native_matrix"]),
         source=source_host.metadata,print_recipe=source_host.metadata["print_recipe"],
         geometry_adaptation="Source crop unchanged; removable rear-face adapter and existing-passage locator are in P")
    lift=np.eye(4);lift[2,3]=9.5
    emit("FC","complete relaxed Industrial cover",source_cover.shape,"cover",kind="source_snap_cover",
         matrix=display@lift@np.array(source_cover.metadata["print_to_native_matrix"]),mesh=source_cover.mesh.copy(),
         source=source_cover.metadata,print_recipe=source_cover.metadata["print_recipe"],
         source_open_lift_n_mm=9.5,parking="Whole relaxed cover bears on two rear cut-edge saddles on S25R; open loading pose",
         source_snap_scope="Elastic wings must spread to engage. Open rigid pose is not a seated state.")

    group_dir=HERE/"print-assemblies";group_dir.mkdir(exist_ok=True)
    group_step=group_dir/"pip-base.step";group_stl=group_dir/"pip-base.stl"
    group_members=("P","Q24","Q48","Q72")
    print_assembly=cq.Assembly(name="PIP-BASE")
    for identifier in group_members:
        print_assembly.add(leaf_shapes[identifier],name=identifier,color=M_PETGF_BLACK)
    export_assembly(print_assembly,str(group_step))
    combined=trimesh.util.concatenate([leaf_meshes[k] for k in group_members])
    combined.export(group_stl)
    group_record=dict(id="PIP-BASE",stl=str(group_stl.relative_to(ROOT)),step=str(group_step.relative_to(ROOT)),
        stl_sha256=sha(group_stl),step_sha256=sha(group_step),frame="Shared manufacturing XYZ; all four members start on bed",
        members=[dict(id=k,transform_mm=np.eye(4).tolist()) for k in group_members],
        geometry_check=dict(watertight_mesh_bodies=len(trimesh.load_mesh(group_stl,process=True).split()),
                            triangle_count=len(combined.faces)))
    assembly_path=HERE/"the-pour.step"
    export_assembly(assembly,str(assembly_path))
    b=assembly.toCompound().BoundingBox()
    collision=collision_review(placed)
    by_id=dict(placed)
    travel=[]
    for identifier in ("Q24","Q48","Q72"):
        for dx in (-13,-6.5,6.5,13):
            moved=by_id[identifier].translate((dx,0,0))
            overlaps=[]
            mb=moved.BoundingBox()
            for other,shape in placed:
                if other==identifier:
                    continue
                sb=shape.BoundingBox()
                if (mb.xmax<=sb.xmin+1e-5 or sb.xmax<=mb.xmin+1e-5 or
                    mb.ymax<=sb.ymin+1e-5 or sb.ymax<=mb.ymin+1e-5 or
                    mb.zmax<=sb.zmin+1e-5 or sb.zmax<=mb.zmin+1e-5):
                    continue
                volume=moved.intersect(shape).Volume()
                if volume>.001:
                    overlaps.append(dict(part=other,overlap_mm3=volume))
            travel.append(dict(id=identifier,translation_x_mm=dx,positive_overlaps=overlaps))
    withdrawal=[]
    foot=neck_shoe("N08",neck)
    for dz in (0,.25,.75,1.5,3,6,12,20,26):
        dy=math.tan(math.radians(15))*dz
        withdrawal.append(dict(translation_print_xyz_mm=[0,dy,dz],
                               rigid_overlap_mm3=neck.translate((0,dy,dz)).intersect(foot).Volume()))
    collision.update(pip_travel=dict(scope="Sampled rigid parked mechanism positions; strand sag, release force and wear unmeasured",
                                     positions=travel),
        neck_withdrawal=dict(scope="One identical source-neck/foot geometry; keeper removed. Sampled nominal rigid positions, unprinted; pure +Z is not the removal axis.",
                             axis_print_xyz=[0,math.sin(math.radians(15)),math.cos(math.radians(15))],positions=withdrawal),
        cover_parking=dict(closest_distance_mm=by_id["FC"].distance(by_id["S25R"]),
                           bearing="Two rear-cut-edge pads; source cover unchanged and openN+9.5"),
        intentional_contacts=["H root rests on P with .15 per-face keys and .25 floor air",
                              "H bears on R6 open top and GR upper-footer cup",
                              "D cut-face ring rests on H pod; .25 per-face moving key",
                              "FC rear cut edges bear on S25R corner pads in open source pose"],
        removal_sequence=["For N12, slide complete G/GR column world -X10mm and set aside; hand-support H while its left bearing is absent",
                          "Lift whole labeled D/N/K unit3mm along its local cut normal, then withdraw radially local +X toward50mm",
                          "For NS20, pause at radial10mm, raise world +Z3mm, then continue to radial50mm",
                          "Slide K uphill local -Y7.2mm through its +Y opening",
                          "Withdraw N along manufacturing +15-degree Y/Z source axis",
                          "H lifts vertically4mm from P/R6/GR after removal of displayed source samples"])
    (HERE/"assembly-review.json").write_text(json.dumps(collision,indent=2)+"\n")
    report=dict(schema=2,title="The Pour",version=VERSION,master_date=MASTER_DATE,
        status="Prepared printable reference; physical results unrecorded",generator="reference.py",assembly="the-pour.step",
        source_inputs=provenance,source_features_inputs="inputs/source-features/sources.json",
        printable=rows,parts=rows,print_assemblies=[group_record],
        overall_bounds_mm=[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
        overall_dimensions_mm=[b.xlen,b.ylen,b.zlen],
        frame="Manufacturing XY bed and Z up. PIP assembly retains shared XYZ; other leaves bed-normalized independently.",
        slider_gap_convention="Per-face X body air; floor .25 and wing roof .45 held fixed",
        pip_gap_convention="Z TOP .24/.48/.72 over bed-start eyes; lower gap1.44 fixed, Y running air .35 each face, X travel26",
        docking_convention="Static storage seats .15 per face; removable neck foot moving key .25 per face",
        source_neck_families=[list(NECK_IDS[i:i+3]) for i in (0,3,6)],
        source_snap_scope="Complete relaxed cover shown at native N+9.5; positive rigid preload at seated source datum is not removed",
        storage="Upright desk reference. Captured necks lift out on local tilted keys; keepers and source cover park by gravity; not qualified for inversion.",
        physical_assembly="Unprinted; tactile release, supports, nominal docks, elastic assembly, load and lifetime are unqualified",
        assembly_review="assembly-review.json")
    for name in ("manifest.json","geometry.json"):
        (HERE/name).write_text(json.dumps(report,indent=2)+"\n")
    write_reference_payloads(report)
    # Discard obsolete generated accessory paths; the kit uses the manifest.
    obsolete=[]
    for path in PARTS.iterdir():
        if path not in written and (path.suffix in (".step",".stl") or path.name.endswith(".step.mesh")):
            obsolete.append(path.name);path.unlink()
    print(json.dumps(dict(assembly=str(assembly_path),parts=len(rows),dimensions_mm=report["overall_dimensions_mm"],
                         overlaps=collision["positive_overlaps"],obsolete_paths=obsolete)),flush=True)


if __name__=="__main__":
    main()
