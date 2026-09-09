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
FILTER_BODY = cq.Color(0.905, 0.915, 0.94, 1.0)
FILTER_CAP = cq.Color(0.42, 0.45, 0.49, 1.0)
PRINTED = cq.Color(0.26, 0.27, 0.30, 1.0)
CYLINDER = cq.Color(0.40, 0.42, 0.47, 1.0)


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
FLUTED = frozenset({"the-back-face", "the-socket"})

def s_regulator():
    """The regulator the guide names three things on: which dial is which, the knob that
    sets the pressure, and the brass nut on the flare below it."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "wellbom_regulator", REGULATOR_DIR / "wellbom_regulator.py")
    reg = importlib.util.module_from_spec(spec)
    note_read(REGULATOR_DIR / "wellbom_regulator.py")
    spec.loader.exec_module(reg)

    a = reg.build_assembly()
    tip, _ = reg.outlet()
    # The MI4508F4SLF's swivel nut, and the red tether leaving it for the appliance.
    nut_len = 14.0
    _add(a, _hex(tip[0], tip[1], tip[2] - nut_len, reg.OUTLET_HEX_FLATS, nut_len),
         "tether-swivel-nut", BRASS)
    top = tip[2] - nut_len
    # The tether leaves sideways rather than hanging: the page's picture has to be wider
    # than it is tall or the two dials print too small to read.
    _add(a, _bend([(tip[0], tip[1], top), (tip[0], tip[1], top - 46.0),
                   (tip[0] + 120.0, tip[1], top - 46.0)], radius=22.0),
         "red-tether", RED_TUBE)
    return a


SCENES = {
    "cabinet-plan": (s_cabinet_plan, dict(cam=(0.0, 0.0, 1.0), up=(0, 1, 0),
                                      size="1700x2000")),
    "opening": (s_opening, dict(cam=(0.42, -0.80, 0.95), target=(0.0, 0.0, 24.0),
                                span=120.0, size="1900x1600")),
    "filter-in-cabinet": (s_filter_in_cabinet, dict(cam=(0.32, -1.0, 0.52),
                                                size="2200x1200")),
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
