"""The install guide's own pictures: one frame composed for each page that asks for an action.

The Quick Start's frames are composed for its six actions. This module composes a frame per
guide page instead, off the same solids and through the same posed renderer, so the two
documents still cannot drift.

Presentation cuts, the kind `_cad_art` makes and for the same reasons:

- the cabinet, the countertop slab, the CO2 cylinder and its regulator, the filter cartridge,
  the concentrate bottle and the cord housing have no source CAD. Each is a plain block or
  cylinder drawn to its catalogue size, and none is a dimensional authority;
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

import cadquery as cq  # noqa: E402

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HARDWARE.parent
ART = HERE / "art"
OUT = HERE / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "quickstart"))

from _cadq_export import import_step, note_read, note_write  # noqa: E402
import _cad_art  # noqa: E402

RENDERER = _cad_art.RENDERER
MACHINE_STEP = _cad_art.MACHINE_STEP
MACHINE_MESH = _cad_art.MACHINE_MESH
COLLET_PRESS = HARDWARE / "printed-parts" / "collet-press" / "collet-press.step"


# The appliance's own frame, read off `enclosure-assembly.step` and its facts: X across the
# front, Y from the front face back, Z up from the cabinet floor.
BOX_X0, BOX_X1 = -113.5, 107.5
BOX_Y0, BOX_Y1 = 5.0, 462.0
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
# the one the machine needs every hour it runs and the one this tree has never put a number on, so
# the pad here states a gap without claiming a figure.
CLEAR_BEHIND, CLEAR_SIDE = 60.0, 60.0
CYLINDER_LANE = 133.0

# Catalogue sizes for the things with no CAD.
CYLINDER_D, CYLINDER_H = 178.0, 508.0
FILTER_D, FILTER_L = 64.0, 305.0
BOTTLE_D, BOTTLE_H = 72.0, 190.0
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


def _add(assembly, shape, name, color):
    if shape is not None:
        assembly.add(shape, name=name, color=color)


def _machine(assembly):
    assembly.add(import_step(str(MACHINE_STEP)), name="appliance")


def _floor(x0, y0, sx, sy):
    return _box(x0, y0, -24.0, sx, sy, 18.0)


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
    _add(a, _cyl(cx, BOX_Y0 + 150.0, -6.0, CYLINDER_D, CYLINDER_H), "co2-cylinder", STEEL)
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
    for name in ("flavor_tube_pos_x", "flavor_tube_neg_x", "soda_umbilical_tube"):
        child = parts.get(name)
        if child is not None:
            _add(a, _cad_art._clip_z(child.obj, -70.0, 40.0).translate((0, 0, lift)),
                 name, BLACK_PART)
    shank = parts.get("westbrass")
    if shank is not None:
        _add(a, _cad_art._clip_z(shank.obj, -70.0, 40.0).translate((0, 0, lift)), "shank", STEEL)
    return a


def s_filter_in_cabinet():
    """The cartridge lying flat, the white run easing into both ends with no tight bend."""
    a = cq.Assembly(name="filter-scene")
    z = FILTER_D / 2.0
    _add(a, _cyl(-FILTER_L / 2.0, 110.0, z, FILTER_D, FILTER_L, axis="X"),
         "cartridge", CORAL)
    _add(a, _run([(-FILTER_L / 2.0, 110.0, z), (-300.0, 110.0, z), (-300.0, -40.0, z)]),
         "white-run-in", BLACK_PART)
    _add(a, _run([(FILTER_L / 2.0, 110.0, z), (300.0, 110.0, z), (300.0, -40.0, z)]),
         "white-run-out", BLACK_PART)
    return a


def s_power_socket():
    """The recessed inlet at the left of the back face, with the cord housing sat down in it."""
    a = cq.Assembly(name="power-socket-scene")
    _machine(a)
    _add(a, _box(-108.0, PORT_FACE_Y - 2.0, 300.0, 26.0, 34.0, 22.0), "cord-housing", CORAL)
    _add(a, _run([(-95.0, PORT_FACE_Y + 32.0, 311.0), (-95.0, PORT_FACE_Y + 120.0, 311.0)], 8.0),
         "cord", BLACK_PART)
    return a


def s_collet_press():
    """The little printed tool: what takes any 1/4 inch push fitting in this system apart."""
    a = cq.Assembly(name="collet-press-scene")
    a.add(import_step(str(COLLET_PRESS)), name="collet-press", color=CORAL)
    return a


SCENES = {
    "cabinet-plan": (s_cabinet_plan, dict(cam=(0.16, -0.40, 1.0), size="2000x2000")),
    "opening": (s_opening, dict(cam=(0.42, -0.80, 0.95), target=(0.0, 0.0, 24.0),
                                span=120.0, size="1900x1600")),
    "filter-in-cabinet": (s_filter_in_cabinet, dict(cam=(0.32, -1.0, 0.52),
                                                size="2200x1200")),
    "power-socket": (s_power_socket, dict(cam=(0.55, 1.0, 0.30),
                                          target=(-92.0, 486.0, 314.0), span=95.0,
                                          size="1900x1500")),
    "collet-press": (s_collet_press, dict(cam=(0.6, -1.0, 0.75), size="1700x1100")),
}


def render(names: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    note_read(RENDERER)
    note_read(MACHINE_STEP)
    note_read(MACHINE_MESH)
    note_read(COLLET_PRESS)
    with tempfile.TemporaryDirectory(prefix="install-art-", dir=OUT) as directory:
        work = Path(directory)
        jobs = []
        for name in names:
            build, pose = SCENES[name]
            step = work / f"{name}.step"
            _cad_art._export_colored(build(), step)
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
