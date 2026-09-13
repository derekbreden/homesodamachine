"""The install guide's own pictures: one frame composed for each page that asks for an action.

The Quick Start's frames are composed for its six actions. This module composes a frame per
guide page instead, off the same solids and through the same posed renderer, so the two
documents still cannot drift.

Presentation cuts, the kind `_cad_art` makes and for the same reasons:

- the cabinet, the countertop slab, the CO2 cylinder and its regulator, the filter cartridge and
  the customer's power cord have no source CAD. Each is drawn to its catalogue size — the cord to
  the inlet it mates with — and none is a dimensional authority;
- a clearance is a coral pad lying on the cabinet floor where the air has to be, so it states a
  footprint without standing in front of the appliance;
- coral marks the one thing the reader's hands are on, which is what it already means in the
  guide's type.

    tools/cad-venv/bin/python hardware/install-guide/_install_art.py
    tools/cad-venv/bin/python hardware/install-guide/_install_art.py --list
    tools/cad-venv/bin/python hardware/install-guide/_install_art.py opening cabinet-plan
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import math

import cadquery as cq  # noqa: E402

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HARDWARE.parent
ART = HERE / "art"
OUT = HERE / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "quickstart"))
sys.path.insert(0, str(HARDWARE / "printed-parts" / "cadlib"))
sys.path.insert(0, str(HARDWARE / "reference" / "iec-c14-inlet"))

from _cadq_export import import_step, note_read, note_write  # noqa: E402
from world_workplane import xz_plane_y_up  # noqa: E402
import iec_c14_inlet as _c14  # noqa: E402
import _cad_art  # noqa: E402

RENDERER = _cad_art.RENDERER
MACHINE_STEP = _cad_art.MACHINE_STEP
MACHINE_MESH = _cad_art.MACHINE_MESH
MACHINE_FACTS = _cad_art.MACHINE_FACTS
COLLET_PRESS = HARDWARE / "printed-parts" / "collet-press" / "collet-press.step"
REGULATOR_DIR = HARDWARE / "reference" / "wellbom-regulator"
PLUMBING_DIR = HARDWARE / "quickstart" / "plumbing"
MODERN_DIR = PLUMBING_DIR / "modern"
C14_SOURCE = Path(_c14.__file__).resolve()


# The appliance's own frame, read off `enclosure-assembly.step` and its facts: X across the
# front, Y from the front face back, Z up from the cabinet floor.
BOX_X0, BOX_X1 = -113.5, 107.5
BOX_Y0, BOX_Y1 = 5.0, 467.0
BOX_Z0, BOX_Z1 = -6.0, 361.0
BOX_MID_X = (BOX_X0 + BOX_X1) / 2.0

#: `enclosure-assembly.facts.json` — the funnel mouth in the top face, and the rear wall the
#: umbilical ports stand on.
HOPPER_X0, HOPPER_X1, HOPPER_Y0, HOPPER_Y1 = -79.5, 79.5, 77.0, 236.0
HOPPER_MID = ((HOPPER_X0 + HOPPER_X1) / 2.0, (HOPPER_Y0 + HOPPER_Y1) / 2.0)
PORT_FACE_Y = 476.5
PORT_Z_UPPER, PORT_Z_LOWER = 336.2, 273.8
PORT_X_WEST, PORT_X_EAST = -78.1, -37.8

# The clearances page 7 asks the reader to leave. There is no pad in front: the pump cartridge's
# own draw is a service motion, and the umbilical's 300 mm service loop is what answers it — the
# appliance comes out to the cabinet face on the day it is wanted rather than standing off the
# doors for the years it is not (`marketing/install-envelope.md`). Behind is 60 mm because the lead
# turns 90° at R12 off a collet standing 9.5 mm proud, and that one is permanent. The side gap is
# the one the machine needs every hour it runs; 40 mm is derived in `marketing/install-envelope.md`
# so its intake and its exhaust are not the same air.
CLEAR_BEHIND, CLEAR_SIDE = 60.0, 40.0
CYLINDER_LANE = 133.0

# Catalogue sizes for the things with no CAD.
CYLINDER_D, CYLINDER_H = 133.0, 457.0
FILTER_D, FILTER_L = 63.0, 311.0
BOTTLE_D, BOTTLE_H = 72.0, 190.0
BOTTLE_NECK_D, BOTTLE_NECK_H = 27.0, 34.0
TUBE_D = 6.35

STONE = cq.Color(0.55, 0.55, 0.58, 1.0)
CABINET = cq.Color(0.74, 0.70, 0.64, 1.0)
CORAL = cq.Color(0.84, 0.25, 0.31, 1.0)
STEEL = cq.Color(0.78, 0.79, 0.82, 1.0)
BRASS = cq.Color(0.72, 0.58, 0.28, 1.0)
WHITE_TUBE = cq.Color(0.90, 0.90, 0.93, 1.0)
RED_TUBE = cq.Color(0.78, 0.20, 0.20, 1.0)
BLUE_TUBE = cq.Color(0.16, 0.40, 0.75, 1.0)
BLACK_PART = cq.Color(0.10, 0.10, 0.12, 1.0)
CONCENTRATE = cq.Color(0.30, 0.10, 0.13, 1.0)
BOTTLE_PET = cq.Color(0.86, 0.87, 0.90, 1.0)
FILTER_BODY = cq.Color(0.905, 0.915, 0.94, 1.0)
FILTER_CAP = cq.Color(0.42, 0.45, 0.49, 1.0)
PRINTED = cq.Color(0.26, 0.27, 0.30, 1.0)
CYLINDER = cq.Color(0.40, 0.42, 0.47, 1.0)
ACETAL_GRAY = cq.Color(0.43, 0.44, 0.43, 1.0)


def _box(x0, y0, z0, sx, sy, sz):
    return cq.Workplane("XY", origin=(x0, y0, z0)).box(sx, sy, sz, centered=(False, False, False))


def _cyl(x, y, z, d, length, axis="Z"):
    """A cylinder of `length` from (x, y, z) along `axis`."""
    base = cq.Workplane("XY", origin=(x, y, z)).circle(d / 2.0).extrude(length)
    if axis == "Z":
        return base
    if axis == "Y":
        return base.rotate((x, y, z), (x + 1.0, y, z), -90.0)
    return base.rotate((x, y, z), (x, y + 1.0, z), 90.0)


def _run(points, diameter=TUBE_D):
    """A tube along axis-aligned segments, with a ball at each turn."""
    solid = None
    for a, b in zip(points, points[1:]):
        deltas = [b[i] - a[i] for i in range(3)]
        moving = [i for i, d in enumerate(deltas) if abs(d) > 1e-6]
        if not moving:
            continue
        if len(moving) != 1:
            raise ValueError(f"{a} -> {b} is not axis-aligned")
        axis = "XYZ"[moving[0]]
        length = deltas[moving[0]]
        start = list(a)
        if length < 0:
            start[moving[0]] += length
        seg = _cyl(start[0], start[1], start[2], diameter, abs(length), axis=axis)
        solid = seg if solid is None else solid.union(seg)
    for point in points[1:-1]:
        ball = cq.Workplane("XY", origin=point).sphere(diameter / 2.0)
        solid = ball if solid is None else solid.union(ball)
    return solid


def _bend(points, diameter=TUBE_D, radius=55.0, steps=20):
    """A tube along axis-aligned segments whose corners are swept, not broken.

    Each turn is a quarter arc of `radius` tangent to both legs, in whatever plane
    the two legs span, sampled into stubs with a ball at each joint. `_run` puts
    one ball at the corner itself, which is the kink the filter page tells you not
    to make. The pieces overlap in a compound rather than a boolean union: same
    colour, one read, no solid modelling for a shape that is only looked at.
    """
    samples = [list(points[0])]
    for i, corner in enumerate(points[1:-1], start=1):
        u = _unit([corner[k] - points[i - 1][k] for k in range(3)])
        v = _unit([points[i + 1][k] - corner[k] for k in range(3)])
        if abs(sum(a * b for a, b in zip(u, v))) > 1e-6:
            raise ValueError("a bend turns a square corner")
        centre = [corner[k] - u[k] * radius + v[k] * radius for k in range(3)]
        # From the centre the entry lies at -v*R and the exit at +u*R, so the arc
        # between them is centre + R*(-v cos t + u sin t) over a quarter turn.
        for step in range(steps + 1):
            t = math.pi / 2.0 * step / steps
            samples.append([centre[k] + radius * (-v[k] * math.cos(t) + u[k] * math.sin(t))
                            for k in range(3)])
    samples.append(list(points[-1]))

    pieces = []
    for a, b in zip(samples, samples[1:]):
        span = cq.Vector(b[0] - a[0], b[1] - a[1], b[2] - a[2])
        if span.Length < 1e-9:
            continue
        pieces.append(cq.Solid.makeCylinder(
            diameter / 2.0, span.Length, cq.Vector(*a), span.normalized()))
    for point in samples[1:-1]:
        pieces.append(cq.Solid.makeSphere(
            diameter / 2.0, cq.Vector(*point), angleDegrees1=-90.0))
    return cq.Compound.makeCompound(pieces)


def _unit(vec):
    mag = math.sqrt(sum(c * c for c in vec))
    return [c / mag for c in vec]





def _add(assembly, shape, name, color):
    if shape is not None:
        assembly.add(shape, name=name, color=color)


def _machine(assembly):
    """The whole appliance with the colours its own STEP carries."""
    for child in cq.Assembly.load(str(MACHINE_STEP)).children:
        assembly.add(child)
    return assembly


def _hex(x, y, z, across_flats, length, axis="Z"):
    """A hexagonal prism of `across_flats`, from (x, y, z) along `axis`."""
    r = across_flats / math.sqrt(3.0)
    pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
           for a in range(0, 360, 60)]
    base = cq.Workplane("XY", origin=(x, y, z)).polyline(pts).close().extrude(length)
    if axis == "Z":
        return base
    if axis == "Y":
        return base.rotate((x, y, z), (x + 1.0, y, z), -90.0)
    return base.rotate((x, y, z), (x, y + 1.0, z), 90.0)


def _floor(x0, y0, sx, sy):
    return _box(x0, y0, -24.0, sx, sy, 18.0)


# --- the back face ----------------------------------------------------------
#
# The children of `enclosure-assembly.step` a customer standing behind the machine can see. Each
# carries its own colour out of the STEP: the shell dark, the four bulkhead rings in the fluids'
# colours, the nameplate's ink white.
REAR_CHILDREN = frozenset({
    "c14-inlet",
    "keystone-jack",
    "co2-inlet",
    "bulkhead-water",
    "bulkhead-carb",
    "bulkhead-flavor-a",
    "bulkhead-flavor-b",
    "funnel",
    "nameplate",
    "nameplate-ink",
    "enclosure-back-bottom",
    "enclosure-back-top",
})
REAR_RING_PREFIX = "bulkhead-ring-"

#: `enclosure-assembly.facts.json`. The show face is the wall's +Y plane and the inlet stands on
#: the top port row's own storey, so the cord goes in level with the tubes.
_FACTS = json.loads(MACHINE_FACTS.read_text())
REAR_FACE_Y = _FACTS["box"]["outer"][3]
C14_STATION = tuple(_FACTS["constants"]["C14_STATION"])

# The mating half of `reference/iec-c14-inlet`: the customer's own cord, which has no source CAD.
# Its socket is that inlet's shroud plus a slip; wall, body, boot and cable are the catalogue
# sizes of a moulded 18 AWG cordset.
C13_SLIP = 0.35
C13_WALL = 3.5
C13_BODY_LEN = 31.0
C13_BOOT_LEN = 30.0
C13_BOOT_D = (14.5, 9.0)
C13_CABLE_D = 7.8
CORDSET = cq.Color(0.035, 0.038, 0.043, 1.0)


def _rear_face(assembly):
    """Add the machine's rear-visible children, colours and all."""
    for child in cq.Assembly.load(str(MACHINE_STEP)).children:
        if child.name in REAR_CHILDREN or child.name.startswith(REAR_RING_PREFIX):
            assembly.add(child)
    return assembly


def _prism(w, h, r, length):
    """A rounded rectangular prism on the show face's own plane, running `length` in +Y."""
    return (cq.Workplane(xz_plane_y_up)
            .rect(w, h).extrude(length).edges("|Y").fillet(r))


def _cable(points, diameter, tangents):
    """A round cord swept along a spline through `points`."""
    vectors = [cq.Vector(*point) for point in points]
    path = cq.Edge.makeSpline(vectors, tangents=[cq.Vector(*t) for t in tangents], scale=False)
    profile = cq.Wire.makeCircle(diameter / 2.0, vectors[0], cq.Vector(*tangents[0]))
    return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=False)


def _c13_cordset(gap):
    """The cord end on the inlet's mating axis, `gap` millimetres out from the show face.

    The socket the shroud enters, the moulding round it, the strain relief and the cord. Its
    three contact slots stand where the inlet's own blades do.
    """
    x, z = C14_STATION
    y0 = REAR_FACE_Y + gap
    socket_w = _c14.SHROUD_W + 2.0 * C13_SLIP
    socket_h = _c14.SHROUD_H + 2.0 * C13_SLIP
    socket_depth = _c14.SHROUD_PROUD + 0.8

    body = _prism(socket_w + 2.0 * C13_WALL, socket_h + 2.0 * C13_WALL, 3.0, C13_BODY_LEN)
    body = body.faces(">Y").chamfer(1.2)
    body = body.cut(_prism(socket_w, socket_h, _c14.SHROUD_FILLET + C13_SLIP, socket_depth))
    for blade in _c14.build_blades().val().Solids():
        bb = blade.BoundingBox()
        body = body.cut(_box(bb.xmin - 0.3, socket_depth, bb.zmin - 0.3,
                             bb.xlen + 0.6, C13_BODY_LEN, bb.zlen + 0.6))
    boot = (cq.Workplane(xz_plane_y_up).workplane(offset=C13_BODY_LEN)
            .circle(C13_BOOT_D[0] / 2.0)
            .workplane(offset=C13_BOOT_LEN).circle(C13_BOOT_D[1] / 2.0).loft())

    tail = C13_BODY_LEN + C13_BOOT_LEN
    cord = _cable(
        ((0.0, tail, 0.0), (0.0, tail + 26.0, 0.0),
         (7.0, tail + 48.0, -58.0), (11.0, tail + 55.0, -175.0)),
        C13_CABLE_D,
        ((0.0, 1.0, 0.0), (0.0, 0.0, -1.0)),
    )
    parts = [body.val(), boot.val(), cord]
    return cq.Compound.makeCompound(parts).translate((x, y0, z))


# --- scenes -----------------------------------------------------------------

def s_cabinet_plan():
    """The slot the appliance stands in, with the clearances lying on the cabinet floor."""
    a = cq.Assembly(name="cabinet-plan-scene")
    _machine(a)
    x0 = BOX_X0 - CLEAR_SIDE - CYLINDER_LANE - 30.0
    x1 = BOX_X1 + CLEAR_SIDE + 30.0
    _add(a, _floor(x0, BOX_Y0 - 40.0, x1 - x0,
                   BOX_Y1 - BOX_Y0 + CLEAR_BEHIND + 80.0),
         "cabinet-floor", CABINET)
    pads = (
        ("behind", BOX_X0, BOX_Y1, BOX_X1 - BOX_X0, CLEAR_BEHIND),
        ("side-west", BOX_X0 - CLEAR_SIDE, BOX_Y0, CLEAR_SIDE, BOX_Y1 - BOX_Y0),
        ("side-east", BOX_X1, BOX_Y0, CLEAR_SIDE, BOX_Y1 - BOX_Y0),
    )
    for name, px, py, sx, sy in pads:
        _add(a, _box(px, py, -6.0, sx, sy, 10.0), f"clear-{name}", CORAL)
    cx = BOX_X0 - CLEAR_SIDE - CYLINDER_LANE / 2.0
    _add(a, _cyl(cx, BOX_Y0 + 150.0, -6.0, CYLINDER_D, CYLINDER_H), "co2-cylinder", CYLINDER)
    return a


def s_opening():
    """The one cut, from above: a 1-3/8 inch circle, with what it has to accept over it."""
    fa = _cad_art._load_faucet_module()
    parts = _cad_art._children_by_name(fa.build_assembly())
    a = cq.Assembly(name="opening-scene")
    slab = (
        cq.Workplane("XY")
        .workplane(offset=fa.countertop_bottom_z)
        .box(320.0, 210.0, fa.countertop_thickness, centered=(True, True, False))
        .cut(
            cq.Workplane("XY")
            .workplane(offset=fa.countertop_bottom_z - 1.0)
            .center(0.0, fa.countertop_hole_center_y)
            .circle(fa.hole_radius)
            .extrude(fa.countertop_thickness + 2.0)
        )
    )
    _add(a, slab, "countertop", STONE)
    lift = 128.0
    for name, colour in (("flavor_tube_pos_x", BLACK_PART),
                         ("flavor_tube_neg_x", BLACK_PART),
                         ("soda_umbilical_tube", BLUE_TUBE)):
        child = parts.get(name)
        if child is not None:
            _add(a, _cad_art._clip_z(child.obj, -70.0, 40.0).translate((0, 0, lift)),
                 name, colour)
    shank = parts.get("westbrass")
    if shank is not None:
        _add(a, _cad_art._clip_z(shank.obj, -70.0, 40.0).translate((0, 0, lift)), "shank", STEEL)
    return a


def s_filter_in_cabinet():
    """The cartridge lying flat, the white run easing into both ends with no tight bend."""
    a = cq.Assembly(name="filter-scene")
    z = FILTER_D / 2.0
    half, cap = FILTER_L / 2.0, 26.0
    _add(a, _cyl(-half + cap, 110.0, z, FILTER_D, FILTER_L - 2 * cap, axis="X"),
         "cartridge", FILTER_BODY)
    for side in (-1.0, 1.0):
        end = half - cap if side > 0 else -half
        _add(a, _cyl(end, 110.0, z, FILTER_D * 0.62, cap, axis="X"),
             f"quick-connect-{'out' if side > 0 else 'in'}", FILTER_CAP)
    _add(a, _bend([(-half, 110.0, z), (-330.0, 110.0, z), (-330.0, -40.0, z)]),
         "white-run-in", WHITE_TUBE)
    _add(a, _bend([(half, 110.0, z), (330.0, 110.0, z), (330.0, -40.0, z)]),
         "white-run-out", WHITE_TUBE)
    return a


def s_collet_press():
    """The little printed tool: what takes any 1/4 inch push fitting in this system apart."""
    a = cq.Assembly(name="collet-press-scene")
    a.add(import_step(str(COLLET_PRESS)), name="collet-press", color=PRINTED)
    return a


def s_the_back_face():
    """The face with nothing in it: seven stations to count, in two rows and four columns."""
    return _rear_face(cq.Assembly(name="the-back-face-scene"))


def s_the_socket():
    """The top row's left-hand end with the cord home in it and its tail falling away.

    Home is the show face. The wall's opening is cut to the shroud alone and the shroud stands
    0.75 mm out of it, so the cordset's moulding comes to rest on the wall itself.
    """
    a = _rear_face(cq.Assembly(name="the-socket-scene"))
    a.add(_c13_cordset(0.5), name="c13-cordset", color=CORDSET)
    return a


#: Scenes standing on the machine's printed bodies. `enclosure-assembly.step` is a smooth prism
#: and the flutes live in the payload beside it, so these carry that skin across.
FLUTED = frozenset({"the-back-face", "the-socket", "nameplate"})

def s_two_tees():
    """The kit's two tees at one scale. Everything else in the box is unmistakable;
    these two are a black fitting and a white one, and page 9 decides between them."""
    a = cq.Assembly(name="two-tees")
    black = _load(HARDWARE / "reference" / "jg-pp0208e-tee", "jg_pp0208e_tee")
    _add(a, black.build_jg_pp0208e_tee().translate((30.0, 0.0, 0.0)),
         "black-tee", BLACK_PART)
    plumbing = _load(PLUMBING_DIR, "plumbing_scenes")
    white = cq.Assembly(name="white-tee")
    # Its own builder stands it on z=0; both tees sit on one centreline here.
    plumbing._add_tee(white, origin=(-12.0, 0.0, -30.8), open_ports=True)
    for child in white.children:
        a.add(child)
    return a


def s_nameplate():
    """The plate the back cover sends the reader to, with the serial and its link on it."""
    a = cq.Assembly(name="nameplate-scene")
    _rear_face(a)
    return a


#: The plate's stand-off along the slide, from its seat. Both of its channels open on +X (the cut
#: part turns its DXF a quarter about Z on the way into this frame), so it comes in from -X; at
#: this stand-off its mouths sit a finger's width short of the shank and the flavor pair.
PLATE_STANDOFF_X = -44.0
#: The washer and nut the faucet ships with, as the quick start draws them: on the last thread at
#: the bottom of the shank, under the gap the plate slides through.
WASHER_T, NUT_H = 1.5, 5.0
NUT_STEEL = cq.Color(0.43, 0.45, 0.48, 1.0)
#: The plate as the quick start draws it, a step lighter than the washer it will meet.
PLATE_STEEL = cq.Color(0.91, 0.92, 0.94, 1.0)
#: One of the flavor pair a shade lighter, so the two stay countable where their silhouettes meet.
BLACK_PART_LIT = cq.Color(0.20, 0.205, 0.215, 1.0)


def s_plate_sideways():
    """The under-counter plate coming in from the side, which is the only way it goes on.

    Seen from under the counter on the plate's own side, so both mouths and all three lines
    are in the open. The plate stands off at -X with both mouths toward the shank and the
    flavor pair, the washer and nut hang at the bottom of the shank below the gap it slides
    through, and the seat itself is the quick start's frame.
    """
    fa = _cad_art._load_faucet_module()
    parts = _cad_art._children_by_name(fa.build_assembly())
    a = cq.Assembly(name="plate-scene")
    # A slab long on the slide axis and narrow across it, with stone beyond the plate's far rim.
    slab = (
        cq.Workplane("XY")
        .workplane(offset=fa.countertop_bottom_z)
        .center(-8.0, 0.0)
        .box(142.0, 68.0, fa.countertop_thickness, centered=(True, True, False))
        .cut(
            cq.Workplane("XY")
            .workplane(offset=fa.countertop_bottom_z - 1.0)
            .center(0.0, fa.countertop_hole_center_y)
            .circle(fa.hole_radius)
            .extrude(fa.countertop_thickness + 2.0)
        )
    )
    _add(a, slab, "countertop", STONE)
    for name, colour in (("westbrass", STEEL),
                         ("flavor_tube_pos_x", BLACK_PART),
                         ("flavor_tube_neg_x", BLACK_PART_LIT),
                         ("soda_umbilical_tube", BLUE_TUBE)):
        child = parts.get(name)
        if child is not None:
            _add(a, _cad_art._clip_z(child.obj, -88.0, -30.0), name, colour)
    washer_top = -fa.shank_length + NUT_H + WASHER_T
    _add(a, (cq.Workplane("XY").workplane(offset=washer_top - WASHER_T)
             .circle(12.0).circle(6.1).extrude(WASHER_T)), "retained-washer", STEEL)
    _add(a, (cq.Workplane("XY").workplane(offset=washer_top - WASHER_T - NUT_H)
             .polygon(6, 22.0).circle(6.1).extrude(NUT_H)), "retained-nut", NUT_STEEL)
    plate = parts.get("under_counter_plate")
    if plate is not None:
        _add(a, plate.obj.translate((PLATE_STANDOFF_X, 0.0, 0.0)), "under-counter-plate", PLATE_STEEL)
    return a


def s_bottle_in_funnel():
    """The one action after the last push: a 440 mL bottle upended over the funnel."""
    a = cq.Assembly(name="bottle-scene")
    _machine(a)
    mouth_x = (HOPPER_X0 + HOPPER_X1) / 2.0
    mouth_y = (HOPPER_Y0 + HOPPER_Y1) / 2.0
    top = 355.0
    # Neck down in the funnel's throat, shoulder just clear of the mouth, body above it.
    neck_z = top - 16.0
    _add(a, _cyl(mouth_x, mouth_y, neck_z, BOTTLE_NECK_D, BOTTLE_NECK_H),
         "bottle-neck", BOTTLE_PET)
    shoulder = neck_z + BOTTLE_NECK_H
    _add(a, cq.Workplane("XY", origin=(mouth_x, mouth_y, shoulder))
         .circle(BOTTLE_NECK_D / 2.0).workplane(offset=26.0).circle(BOTTLE_D / 2.0).loft(),
         "bottle-shoulder", BOTTLE_PET)
    _add(a, _cyl(mouth_x, mouth_y, shoulder + 26.0, BOTTLE_D, BOTTLE_H),
         "bottle-body", CONCENTRATE)
    _add(a, _cyl(mouth_x, mouth_y, shoulder + 26.0 + BOTTLE_H, BOTTLE_D * 0.62, 4.0),
         "bottle-base", BOTTLE_PET)
    return a


def s_stop_open():
    """The cold shut-off as it stands, lever in line with the outlet."""
    return _plumbing("plumbing-valve-on")


def s_stop_closed():
    """The same valve, a quarter turn: lever across the outlet."""
    return _plumbing("plumbing-valve-off")


def s_tee_before():
    """The hose off the stop, and the tee subassembly waiting to go between them."""
    return _plumbing("plumbing-pre-tee")


def s_tee_after():
    """The tee in, the hose back on top of it, the appliance's run in its branch."""
    return _plumbing("plumbing-tee-installed")


# John Guest's PM4508F4S and PI061008S drawings, page 2 of each (mm):
# https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Female%20Adaptor%20(FFL%20Thread)%20Data%20Sheet.pdf
# https://www.johnguest.com/sites/jg/files/2022-03/JG%20Air%20Reducer%20(Imperial)%20Data%20Sheet.pdf
# Lengths and insertion depths are with the collets in release position.
CO2_FLARE_LENGTH = 33.8
CO2_FLARE_BODY_D = 19.8
CO2_FLARE_HEX_FLATS, CO2_FLARE_HEX_D, CO2_FLARE_HEX_LENGTH = 15.9, 17.5, 10.0
CO2_FLARE_INSERTION = 16.5
CO2_REDUCER_LENGTH, CO2_REDUCER_BODY_D = 37.4, 15.0
CO2_REDUCER_STEM_LENGTH, CO2_REDUCER_STEM_D = 19.1, 7.94


def _co2_tether_adapter(assembly, tip, gap=0.0):
    """The acetal female flare connector and inserted stem reducer; return the tube exit.

    Published outer bounds; the moulded transitions and collet lips are schematic. The flare
    tip lies at the back of the connector's hex in the seated picture: an illustrative pose,
    since the regulator-side seating depth is unmeasured. `gap` is retreat from that pose.
    """
    x, y, z = tip
    front = z + CO2_FLARE_HEX_LENGTH - gap
    back = front - CO2_FLARE_LENGTH
    hex_back = front - CO2_FLARE_HEX_LENGTH
    lip_length = 1.5
    hexagon = _hex(x, y, hex_back, CO2_FLARE_HEX_FLATS, CO2_FLARE_HEX_LENGTH).intersect(
        _cyl(x, y, hex_back, CO2_FLARE_HEX_D, CO2_FLARE_HEX_LENGTH))
    connector = _cyl(x, y, back + lip_length, CO2_FLARE_BODY_D,
                     hex_back - back - lip_length).union(hexagon)
    connector = connector.cut(_cyl(x, y, hex_back, 25.4 * 7.0 / 16.0, CO2_FLARE_HEX_LENGTH))
    _add(assembly, connector, "tether-flare-connector", ACETAL_GRAY)

    # Collet lips occupy the ends of the published envelopes.
    _add(assembly, _cyl(x, y, back, CO2_FLARE_BODY_D * 0.8, lip_length),
         "tether-flare-collet", BLACK_PART)
    stem_end = back - (CO2_REDUCER_STEM_LENGTH - CO2_FLARE_INSERTION)
    _add(assembly, _cyl(x, y, stem_end, CO2_REDUCER_STEM_D, back - stem_end),
         "tether-reducer-stem", ACETAL_GRAY)
    exit_z = back - (CO2_REDUCER_LENGTH - CO2_FLARE_INSERTION)
    _add(assembly, _cyl(x, y, exit_z + lip_length, CO2_REDUCER_BODY_D,
                        stem_end - exit_z - lip_length),
         "tether-stem-reducer", ACETAL_GRAY)
    _add(assembly, _cyl(x, y, exit_z, CO2_REDUCER_BODY_D * 0.8, lip_length),
         "tether-reducer-collet", BLACK_PART)
    return x, y, exit_z


def s_regulator():
    """The two dials, pressure knob and acetal connector pair on the outlet flare."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wellbom_regulator", REGULATOR_DIR / "wellbom_regulator.py")
    reg = importlib.util.module_from_spec(spec)
    note_read(REGULATOR_DIR / "wellbom_regulator.py")
    spec.loader.exec_module(reg)

    a = reg.build_assembly()
    tip, _ = reg.outlet()
    _, _, top = _co2_tether_adapter(a, tip)
    # The tether leaves sideways rather than hanging: the page's picture has to be wider
    # than it is tall or the two dials print too small to read.
    _add(a, _bend([(tip[0], tip[1], top), (tip[0], tip[1], top - 46.0),
                   (tip[0] + 120.0, tip[1], top - 46.0)], radius=22.0),
         "red-tether", RED_TUBE)
    return a


def _load(directory, stem):
    import importlib.util
    path = directory / f"{stem}.py"
    note_read(path)
    spec = importlib.util.spec_from_file_location(stem, path)
    module = importlib.util.module_from_spec(spec)
    # A dataclass defined in the module resolves its annotations through
    # sys.modules[__module__], so the entry has to exist before it executes.
    sys.modules[stem] = module
    sys.path.insert(0, str(directory))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(directory))
    return module


def s_kitchen_push():
    """The newer cold side: a 1/4-inch line on a push fitting, nothing to turn."""
    return _load(MODERN_DIR, "render_modern_tee").build_water_on()


def _plumbing(name):
    """One of the sheet's four under-sink scenes, without its wall plane.

    Every picture in this guide floats on the card's field; the escutcheon and the copper
    stub already say the stop comes out of a wall.
    """
    scene = _load(PLUMBING_DIR, "plumbing_scenes").build_scenes()[name]
    kept = cq.Assembly(name=name)
    for child in scene.children:
        if child.name != "finished-wall":
            kept.add(child)
    return kept


def s_kitchen_hose():
    """The older cold side: a braided hose on a shut-off valve, no 1/4-inch line anywhere.

    The sheet's own wall plane comes out: every picture in this guide floats on the card's
    field, and the escutcheon and copper stub already say the stop comes out of a wall.
    """
    return _plumbing("plumbing-valve-on")


SCENES = {
    "cabinet-plan": (s_cabinet_plan, dict(cam=(0.0, 0.0, 1.0), up=(0, 1, 0),
                                      size="1700x2000")),
    "opening": (s_opening, dict(cam=(0.42, -0.80, 0.95), target=(0.0, 0.0, 24.0),
                                span=120.0, size="1900x1600")),
    "filter-in-cabinet": (s_filter_in_cabinet, dict(cam=(0.32, -1.0, 0.52),
                                                size="2200x1200")),
    # One span and one frame for both, and no trim, so the two halves of the fork are
    # at the same scale in the same box: the comparison is the whole picture.
    "two-tees": (s_two_tees, dict(cam=(0.25, 1.0, 0.32), size="1600x900")),
    "nameplate": (s_nameplate, dict(cam=(-0.14, 1.0, 0.10),
                   target=(38.16, 467.0, 262.9), span=132.0, size="1600x1100")),
    "plate-sideways": (s_plate_sideways, dict(cam=(-0.85, -1.0, -0.85),
                        target=(-16.0, 0.0, -43.0), span=88.0, size="1700x950")),
    # One camera per pair, and no trim, so before and after are the same frame.
    "stop-open": (s_stop_open, dict(cam=(1.05, 1.70, 0.62), target=(-6.0, 44.0, 96.0), span=86.0, size="1250x1150", trim=False)),
    "stop-closed": (s_stop_closed, dict(cam=(1.05, 1.70, 0.62), target=(-6.0, 44.0, 96.0), span=86.0, size="1250x1150", trim=False)),
    "tee-before": (s_tee_before, dict(cam=(1.05, 1.70, 0.62), target=(-6.0, 44.0, 112.0), span=132.0, size="1250x1150", trim=False)),
    "tee-after": (s_tee_after, dict(cam=(1.05, 1.70, 0.62), target=(-6.0, 44.0, 112.0), span=132.0, size="1250x1150", trim=False)),
    "bottle-in-funnel": (s_bottle_in_funnel, dict(cam=(0.55, -1.0, 0.62),
                          target=(0.0, 150.0, 405.0), span=395.0, size="1500x1180")),
    "kitchen-push": (s_kitchen_push, dict(cam=(1.05, -1.72, 0.72), target=(-46.0, 8.0, 100.0),
                                          span=88.0, size="1500x980", trim=False)),
    "kitchen-hose": (s_kitchen_hose, dict(cam=(1.05, 1.70, 0.62), target=(10.0, 53.0, 150.0),
                                          span=88.0, size="1500x980", trim=False)),
    "regulator": (s_regulator, dict(cam=(0.10, 1.0, 0.16), size="1700x1500")),
    "collet-press": (s_collet_press, dict(cam=(-0.5, -0.9, 0.85), size="1700x1100")),
    # On the wall's own column, tilted down. Screen up is world up, so every row is level. The
    # frame holds both port rows, the inlet, the jack, the nameplate, and a sliver of the top
    # face over the wall's top edge.
    "the-back-face": (s_the_back_face, dict(cam=(0.0, 1.0, 0.16),
                                            target=(-3.0, REAR_FACE_Y, 292.0),
                                            span=70.5, size="2200x1540")),
    # Off the column, on the top row: the four collets, the inlet with the cord home in it, and
    # the tail leaving past the machine's +X corner.
    "the-socket": (s_the_socket, dict(cam=(-0.26, 1.0, 0.16),
                                      target=(5.0, REAR_FACE_Y, 334.1),
                                      span=31.7, size="2200x668")),
}


def _graft_flutes(step: Path) -> None:
    """Put the machine's printed skin on the bodies this scene borrowed from it.

    The flutes live in `enclosure-assembly.step.mesh` and not in the solid beside it. Every body
    built in this file keeps the surface its own solid tessellates to.
    """
    import flute_payload

    source = flute_payload.read_payload(MACHINE_MESH) or []
    landed = flute_payload.graft(Path(str(step) + ".mesh"),
                                 {entry["name"]: entry for entry in source})
    if landed < 3:
        raise RuntimeError(f"{step.name}: {landed} appliance meshes landed, not the rear bodies")


def render(names: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    note_read(RENDERER)
    note_read(MACHINE_STEP)
    note_read(MACHINE_MESH)
    note_read(MACHINE_FACTS)
    note_read(COLLET_PRESS)
    note_read(C14_SOURCE)
    with tempfile.TemporaryDirectory(prefix="install-art-", dir=OUT) as directory:
        work = Path(directory)
        jobs = []
        for name in names:
            build, pose = SCENES[name]
            step = work / f"{name}.step"
            fluted = name in FLUTED
            _cad_art._export_colored(build(), step, mesh=fluted)
            if fluted:
                _graft_flutes(step)
            jobs.append({
                "step": str(step.relative_to(HARDWARE)),
                "out": str(ART / f"{name}.png"),
                "up": (0, 0, 1),
                "bg": "#ffffff",
                "trim": True,
                "solid": True,
                "ortho": True,
                "ground": False,
                "fog": False,
                **pose,
            })
            print(f"  staged {name}")
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
        for job in jobs:
            out = Path(job["out"])
            _cad_art._clear_connected_background(out)
            note_write(out)
            print(f"  -> art/{out.name} ({out.stat().st_size // 1024} KB)")


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for name in SCENES:
            print(name)
        return 0
    wanted = [a for a in argv if not a.startswith("-")] or list(SCENES)
    unknown = [n for n in wanted if n not in SCENES]
    if unknown:
        print(f"unknown scene(s): {', '.join(unknown)}", file=sys.stderr)
        return 1
    render(wanted)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
