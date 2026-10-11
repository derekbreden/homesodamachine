"""The Pour: individually printed studies assembled around a rising cascade.

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
NECK_IDS = ("N08", "NR00", "NR05", "NR15", "N12", "NS00", "NS10", "NS20", "N24")
SLIDER_GAPS = (0.15, 0.25, 0.35, 0.45)
BASE_T = 6.6
DOCK_DIAMETER = 6.0
DOCK_AIR_DIAMETRAL = 0.8
DOCK_HEIGHT = 3.0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def rounded(width, depth, height, *, z=0.0, radius=2.0):
    return (cq.Workplane("XY").workplane(offset=z).rect(width, depth)
            .extrude(height).edges("|Z").fillet(radius).val())


def letters(value, size, height, z, *, x=0.0, y=0.0):
    return (cq.Workplane("XY").workplane(offset=z).text(value, size, height,
            font="Arial", halign="center", valign="center", combine=False)
            .val().translate((x, y, 0)))


def mark(shape, value, x, y, z, *, size=3.0, inset=False):
    text = letters(value, size, .49 if not inset else .50,
                   z-.01 if not inset else z-.48, x=x, y=y)
    return (shape.cut(text) if inset else shape.fuse(text)).clean()


def peg(x, y, z):
    return cq.Solid.makeCylinder(DOCK_DIAMETER/2, DOCK_HEIGHT+.1,
                                cq.Vector(x, y, z-.1))


def socket(shape, x, y):
    return shape.cut(cq.Solid.makeCylinder((DOCK_DIAMETER+DOCK_AIR_DIAMETRAL)/2,
                     DOCK_HEIGHT+.6, cq.Vector(x, y, -.1))).clean()


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


def cascade_body():
    """Two open structural stairways park the unchanged cut neck specimens."""
    body = rounded(180, 148, BASE_T, radius=18)
    stair_outer = [(-21.5, BASE_T), (72.5, BASE_T), (72.5, 98), (29.5, 98),
                   (29.5, 68), (12.5, 68), (12.5, 38), (-4.5, 38), (-4.5, 8), (-21.5, 8)]
    stair_inner = [(2.5, 13.6), (65.5, 13.6), (65.5, 91), (36.5, 91),
                   (36.5, 61), (19.5, 61), (19.5, 31), (2.5, 31)]
    for x in (-65, 65):
        outboard_sign = -1 if x < 0 else 1
        # The structural web is outboard of every shoe and specimen; a later
        # stair cannot intrude into the neighboring lower specimen's space.
        web_x = outboard_sign*86.3
        web = (cq.Workplane("YZ", origin=(web_x-3, 0, 0))
               .polyline(stair_outer).close().extrude(6).val())
        opening = (cq.Workplane("YZ", origin=(web_x-3.1, 0, 0))
                   .polyline(stair_inner).close().extrude(6.2).val())
        body = body.fuse(web.cut(opening))
        for y, height in zip((0, 17, 34, 51), (8, 38, 68, 98)):
            shelf = rounded(42, 43, 3, z=height-3, radius=2).translate((x+outboard_sign*2, y, 0))
            # The cradle bears only on the existing flat cut bottom and keeps
            # over 0.5 mm nominal air at the manufacturing-frame bounds.
            for side in (-1, 1):
                shelf = shelf.fuse(box(x+side*18.8-.7, x+side*18.8+.7,
                                      y-15.0, y+15.0, height-.1, height+1.8))
            shelf = shelf.fuse(box(x-18.1, x+18.1, y+21.0, y+22.0,
                                  height-.1, height+1.8))
            body = body.fuse(shelf)
    # The centre-front neck has a fully supported cut-face shelf.
    body = body.fuse(box(-3, 3, -21, -15, BASE_T-.1, 44))
    body = body.fuse(rounded(38, 43, 3, z=41, radius=2).translate((0, -11, 0)))
    for side in (-1, 1):
        body = body.fuse(box(side*18.8-.7, side*18.8+.7, -26, 4, 43.9, 45.8))
    # Dock pegs are storage fits with generous separate allowance.
    for x in (-66, -22, 22, 66):
        for dx in (-10, 10):
            body = body.fuse(peg(x+dx, -45, BASE_T))
    for x in (-30.5, 0, 30.5):
        for dx in (-9, 9):
            body = body.fuse(peg(x+dx, 7, BASE_T))
    for x in (-16, 0, 16):
        for y in (21, 47):
            body = body.fuse(peg(x, y, BASE_T))
    # Rigid grip receiver bridge: two plain columns, no shortened flexure.
    for x in (-46, 46):
        body = body.fuse(box(x-3, x+3, -51, -39, BASE_T-.1, 27))
        body = body.fuse(peg(x, -45, 27))
    for x, diameter in ((-44, 4.40), (0, 6.65)):
        body = body.cut(cq.Solid.makeCylinder(diameter/2, BASE_T+1,
                                             cq.Vector(x, -64, -.5)))
        body = mark(body, f"{diameter:.2f}", x, -71, BASE_T, size=2.6, inset=x<0)
    signal = cq.Workplane("XY", origin=(44, -64, -.5)).slot2D(5.4, 1.8).extrude(BASE_T+1).val()
    body = body.cut(signal)
    body = mark(body, "SIG", 44, -71, BASE_T, size=2.6)
    body = mark(body, "THE POUR", 0, 70, BASE_T, size=4.3)
    body = mark(body, "X", 78, -2, BASE_T, size=4.0)
    body = mark(body, "Y", 0, 64, BASE_T, size=4.0, inset=True)
    return body.clean()


def slide_receiver(gap):
    body = rounded(34, 46, 14, radius=2)
    # 0.25 mm floor allowance and 0.45 mm above each seated wing are fixed;
    # only the vertical body side clearance is varied in this family.
    body = body.cut(box(-9-gap, 9+gap, -24, 24, 3, 7.06))
    body = body.cut(box(-12.4, 12.4, -24, 24, 3, 5.38))
    for x in (-10, 10):
        body = socket(body, x, 0)
    body = mark(body, f"{gap:.2f}", 0, 15.7, 14, size=3.5)
    return body.clean()


def slide_tongue(gap):
    body = rounded(18, 29, 3.36, radius=.6)
    for side in (-1, 1):
        body = body.fuse(rounded(3.4, 23, 1.68, radius=.6).translate((side*9.7, 0, 0)))
    tab = rounded(26, 6, 4.2, radius=2).translate((0, -16.5, 0))
    body = body.fuse(tab)
    body = mark(body, f"{gap:.2f}", 0, -16.5, 4.2, size=3.2)
    return body.clean()


def roof_sample(identifier):
    # The open front and sides leave the cantilever's entire underside and
    # automatically generated support tree accessible for removal.
    body = rounded(30, 9, 3, radius=1).translate((0, 9.5, 0))
    body = body.fuse(box(-15, 15, 9, 13, 2.9, 20))
    body = body.fuse(box(-15, 15, -12, 13, 17, 20))
    # Same label pad and footprint on all three specimens.
    body = body.fuse(rounded(24, 7, 3, z=20, radius=1).translate((0, 9.5, 0)))
    body = mark(body, identifier, 0, 9.5, 23, size=3.0)
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
    profile = profile.threePointArc((y-6+6/q, 80+6/q), (y-6, 86)).lineTo(-15, 86)
    profile = profile.threePointArc((-15-6/q, 80+6/q), (-21, 80)).lineTo(-18, 80)
    profile = profile.threePointArc((-15-3/q, 80+3/q), (-15, 83)).lineTo(y-9, 83)
    profile = profile.threePointArc((y-9+6/q, 77+6/q), (y-3, 77))
    profile = profile.lineTo(y-3, z+3)
    for yy, zz in reversed(points[:-1]):
        profile = profile.lineTo(yy-3, zz+3)
    profile = profile.lineTo(-20, 2).lineTo(-17, 2).close()
    body = profile.extrude(8).val()
    foot = rounded(12, 44, 3, radius=1.5)
    body = body.fuse(foot).fuse(transverse_round())
    for yy in (-13, 13):
        body = socket(body, 0, yy)
    body = mark(body, identifier, 0, 18.3, 3, size=3.0)
    body = mark(body, "X", -3, -17, 15, size=2.6)
    # Values are angles of the outside ramp surface above the bed, measured
    # in the YZ manufacturing plane. Markings are on the side, off that face.
    for angle, yy, zz in facets:
        text = (cq.Workplane("YZ", origin=(3.99, yy-1.2, zz+1.2))
                .text(str(angle), 2.1, .35, font="Arial", combine=False).val())
        body = body.fuse(text)
    return body.clean(), [{"angle_above_bed_degrees": a,
                           "midpoint_print_yz_mm": [yy, zz]} for a, yy, zz in facets]


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
        body = socket(body, x, 0)
    for slot in grip.receiver_slots():
        body = body.cut(slot.translate((0, 0, .25)))
    return body.clean()


def neck_shoe(identifier):
    """A removable storage frame; source surfaces are untouched and visible."""
    body = rounded(36, 41, 4, radius=2)
    for side in (-1, 1):
        a, b = sorted((side*15, side*18))
        body = body.fuse(box(a, b, -12, 12, 3.9, 26.73))
        # Keeper wing slot opens front/back so it slides out along print Y.
        xa, xb = sorted((side*14.9, side*18.1))
        body = body.cut(box(xa, xb, -12.1, 9.1, 22.35, 24.73))
        # Small sloping mouth clears the wing during insertion.
        body = body.cut(box(xa, xb, -12.1, -8, 24.72, 25.13))
    body = body.fuse(box(-14.9, 14.9, 17.1, 19.1, 3.9, 6.4))
    body = mark(body, identifier, 0, -18, 4, size=3.2)
    return body.clean()


def neck_keeper(identifier):
    body = rounded(29.7, 8, 2.4, radius=.6)
    for side in (-1, 1):
        body = body.fuse(rounded(3.4, 5, 1.68, radius=.6).translate((side*15.55, 0, 0)))
    body = mark(body, identifier, 0, 0, 2.4, size=3.2)
    return body.clean()


def main():
    PARTS.mkdir(parents=True, exist_ok=True)
    neck, neck_mesh, provenance = neck_geometry()
    assembly = cq.Assembly(name="The Pour")
    rows = []
    placed_solids = []

    def emit(identifier, name, shape, group="kit", *, placement=(0, 0, 0),
             rotation=(0, 0, 0), mesh=None, **details):
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError(f"{identifier}: expected one valid printable solid")
        bounds = shape.BoundingBox()
        if abs(bounds.zmin) > .00001:
            raise ValueError(f"{identifier}: exported print frame is not on bed: {bounds.zmin}")
        stem = identifier.lower() + "-" + name.lower().replace(" ", "-")
        step, stl = PARTS/(stem+".step"), PARTS/(stem+".stl")
        export_assembly(one_body(cq.Workplane(obj=shape), f"{identifier} {name}", M_PETGF_BLACK), str(step))
        if mesh is None:
            mesh = write_print_stl(shape, stl)
        else:
            mesh.export(stl)
        check_mesh = trimesh.load_mesh(stl, process=True)
        if not check_mesh.is_watertight or len(check_mesh.split()) != 1 or check_mesh.volume <= 0:
            raise ValueError(f"{identifier}: expected one positive watertight STL body")
        posed = shape
        for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), rotation):
            if angle:
                posed = posed.rotate((0, 0, 0), axis, angle)
        posed = posed.translate(placement)
        assembly.add(posed, name=f"{identifier} {name}", color=M_PETGF_BLACK)
        placed_solids.append(posed)
        row = dict(id=identifier, name=f"{identifier} {name}", kind=details.pop("kind", "kit"),
                   stl=str(stl.relative_to(ROOT)), step=str(step.relative_to(ROOT)),
                   stl_relative=str(stl.relative_to(HERE)), step_relative=str(step.relative_to(HERE)),
                   group=group, print_group=group, rotation_x_degrees=0,
                   print_bounds_mm=[[bounds.xmin, bounds.ymin, bounds.zmin],
                                    [bounds.xmax, bounds.ymax, bounds.zmax]],
                   stl_sha256=sha(stl), step_sha256=sha(step),
                   assembly=dict(rotation_xyz_degrees=list(rotation), translation_mm=list(placement)),
                   nominal_storage_dock_diametral_air_mm=DOCK_AIR_DIAMETRAL,
                   geometry_check=dict(one_valid_solid=True, one_watertight_mesh_body=True,
                                       triangle_count=len(check_mesh.faces)), **details)
        rows.append(row)
        # Independent print families are reviewable as soon as their stable
        # component rows exist; the final write supplies complete assembly data.
        partial = dict(schema=1, title="The Pour", assembly="the-pour.step",
                       source_inputs=provenance, printable=rows, parts=rows,
                       preparation_status="Component generation in progress")
        for metadata in ("manifest.json", "geometry.json"):
            (HERE/metadata).write_text(json.dumps(partial, indent=2)+"\n")
        print(identifier, len(check_mesh.faces), flush=True)

    body = cascade_body()
    neck_positions = [(-65, 0, 8), (-65, 17, 38), (-65, 34, 68), (-65, 51, 98),
                      (0, -11, 44), (65, 51, 98), (65, 34, 68), (65, 17, 38), (65, 0, 8)]
    for identifier, (x, y, z) in zip(NECK_IDS, neck_positions):
        body = mark(body, identifier, x, y-20.1, z, size=2.4, inset=True)
    emit("P", "cascade carrier", body, kind="carrier",
         bore_diameters_mm=[4.40, 6.65], ribbon_slot_mm=[5.4, 1.8],
         bores_print_xy_mm=[[-44, -64], [0, -64]], ribbon_slot_print_xy_mm=[44, -64],
         marking_raise_mm=.48, marking_recess_mm=.48,
         storage="Upright gravity saddles; samples are captured in removable labeled shoes")

    for x, gap in zip((-66, -22, 22, 66), SLIDER_GAPS):
        identifier = f"S{round(gap*100):02d}"
        emit(identifier+"R", "sliding receiver", slide_receiver(gap), placement=(x, -45, BASE_T),
             kind="slider_receiver", body_side_air_each_mm=gap, floor_air_mm=.25,
             roof_air_above_wing_mm=.45, wing_tip_air_each_mm=1.0,
             comparison="Synthetic short flat-wing sliding fit; X gap is per side")
        emit(identifier, "sliding tongue", slide_tongue(gap), placement=(x, -55, BASE_T+3.25),
             kind="slider", body_side_air_each_mm=gap, body_width_mm=18,
             body_thickness_mm=3.36, wing_projection_mm=2.4, wing_thickness_mm=1.68,
             comparison="Same tongue shape in all four lanes; label alone differs")

    for x, identifier, gap in ((-30.5, "R30", .30), (0, "R45", .45), (30.5, "R60", .60)):
        emit(identifier, "support ceiling", roof_sample(identifier), f"support-{round(gap*100):03d}",
             placement=(x, -2.5, BASE_T), kind="support", support_top_z_distance_mm=gap,
             support_ceiling_z_mm=17, ceiling_xy_bounds_mm=[[-15, -12], [15, 9]],
             comparison="Identical 3mm cantilever ceilings with open removal access")

    for x, identifier, height in ((-16, "A08", .08), (0, "A12", .12), (16, "A24", .24)):
        blade, facets = curve_blade(identifier)
        emit(identifier, "angle and curve blade", blade, f"finish-{round(height*100):03d}",
             placement=(x, 34, BASE_T), kind="angle_blade", requested_layer_height_mm=height,
             angle_facets=facets, curve_radius_mm=6, nominal_curve_wall_mm=3,
             surface_azimuths=["YZ blade", "XZ transverse shoulder"],
             comparison="Facets 0..90 degrees above bed; actual orthogonal print surfaces")

    for identifier, shoe_placement in zip(NECK_IDS, neck_positions):
        placement = (shoe_placement[0], shoe_placement[1], shoe_placement[2]+4)
        emit(identifier+"D", "neck storage shoe", neck_shoe(identifier), placement=shoe_placement,
             kind="neck_shoe", neck_id=identifier, source_neck_bed_above_shoe_mm=4,
             keeper_slot_floor_z_mm=22.35, keeper_slot_roof_z_mm=24.73,
             comparison="Labeled storage accessory; touches cut end faces only")
        emit(identifier+"K", "neck keeper bar", neck_keeper(identifier),
             placement=(shoe_placement[0], shoe_placement[1], shoe_placement[2]+22.6),
             kind="neck_keeper", neck_id=identifier, cut_top_air_mm=.4,
             comparison="Sliding bar captures specimen at its cut top; remove to inspect")
        details = dict(kind="neck", source=provenance,
                       comparison="Unscaled source faucet neck; short-section thermal conditions differ")
        if identifier in ("N08", "N12", "N24"):
            height = int(identifier[1:])/100
            group = f"finish-{round(height*100):03d}"
            details["requested_layer_height_mm"] = height
            details["seam_method"] = "regular"
            details["seam_gap_percent"] = 15
        else:
            group = "seam"
            details["requested_layer_height_mm"] = .12
            details["seam_method"] = "regular" if identifier.startswith("NR") else "scarf"
            details["seam_gap_percent"] = int(identifier[-2:]) if identifier.startswith("NR") else 15
            if identifier.startswith("NS"):
                details["scarf_gap_percent"] = int(identifier[-2:])
        emit(identifier, "faucet neck", neck, group, placement=placement,
             mesh=neck_mesh.copy(), **details)

    grip = grip_interface()
    emit("GR", "grip receiver bridge", grip_receiver(grip), placement=(0, -45, 27),
         kind="grip_receiver", source_path="hardware/printed-parts/enclosure/enclosure/_grip_interface.py",
         endwall_mm=3, roof_stock_mm=12, retaining_air_mm=.45, supported_back_air_mm=.25)
    emit("G", "complete grip insert", grip.cover(), "finish-008", placement=(0, -45, 27.25),
         kind="grip", source_path="hardware/printed-parts/enclosure/enclosure/_grip_interface.py",
         overall_length_mm=84.5, body_length_mm=79.7, body_width_mm=grip.WIDTH,
         body_thickness_mm=3.36, comparison="Complete production broad strip and both wings")
    assembly_path = HERE / "the-pour.step"
    export_assembly(assembly, str(assembly_path))
    compound = cq.Compound.makeCompound(placed_solids)
    b = compound.BoundingBox()
    report = dict(schema=1, title="The Pour", status="Prepared printable reference; physical results unrecorded",
                  generator="reference.py", assembly="the-pour.step", source_inputs=provenance,
                  printable=rows, parts=rows,
                  overall_bounds_mm=[[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]],
                  overall_dimensions_mm=[b.xlen, b.ylen, b.zlen],
                  frame="All individual meshes: millimetres, XY bed, Z up, lowest material at Z0",
                  slider_gap_convention="Per-side X body air; floor .25 and wing roof .45 held fixed",
                  physical_assembly="Unprinted; nominal docking fits and tactile behavior are unqualified")
    for name in ("manifest.json", "geometry.json"):
        (HERE/name).write_text(json.dumps(report, indent=2)+"\n")
    from viewer_payload import write_reference_payloads
    write_reference_payloads(report)
    print(json.dumps({"assembly": str(assembly_path), "parts": len(rows),
                      "dimensions_mm": report["overall_dimensions_mm"]}), flush=True)


if __name__ == "__main__":
    main()
