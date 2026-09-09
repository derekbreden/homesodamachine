"""The weld-rotator build guide's pictures, one per step of the build.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/weld-rotator-guide/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
and it keeps no `note_read` / `note_write` bookkeeping.

Each picture holds one step's subject: the parts that step touches, staged where that step
leaves them, framed on what the reader's hands are on.

THREE APPEARANCES THE FIXTURE DOES NOT HAVE. Coral is the part or fastener the step adds; brass
is a heat-set insert; blue is a gauge, a block or a probe. Everything already standing keeps the
stock's own colour. Page 3 of the guide declares the same three to the reader.

AND A FASTENER STANDS OFF ITS OWN HOLE, along the axis it goes in on, by `POISE`.

Screws, inserts, feeler blades, blocks and the indicator are proxies built here to catalogue
head and length. Nothing here is a dimension.

    tools/cad-venv/bin/python tools/weld-rotator-guide/rotator_art.py            # every picture
    tools/cad-venv/bin/python tools/weld-rotator-guide/rotator_art.py hero feet  # named ones
    tools/cad-venv/bin/python tools/weld-rotator-guide/rotator_art.py --list
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Set before `_cadq_export` is imported: it takes the build lock at import time, and a hand-run
# picture pass must neither supersede a running generator nor be superseded by one.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq  # noqa: E402
from PIL import Image  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
FIXTURE = HARDWARE / "printed-parts" / "fixtures" / "weld-rotator"
GUIDE = HARDWARE / "weld-rotator-guide"
ART = GUIDE / "art"
OUT = GUIDE / "out"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"

sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(FIXTURE))

from _material_base import (  # noqa: E402
    M_ALUMINIUM,
    M_COPPER,
    M_PETGF_BLACK,
    M_STAINLESS,
    M_TPU_BLACK,
    step_safe,
)
from _cadq_export import _per_solid_color  # noqa: E402

import weld_rotator as wr  # noqa: E402
import _rotator_interface as interface  # noqa: E402


M_BRASS = cq.Color(0.78, 0.60, 0.22)
M_ACCENT = cq.Color(0.84, 0.25, 0.31)
M_GAUGE = cq.Color(0.30, 0.52, 0.84)
M_PP_BALL = cq.Color(0.90, 0.90, 0.92)

#: How far a poised fastener stands off its own hole, everywhere.
POISE = 16.0


# ---------------------------------------------------------------------------
# Proxies

def _shcs(x, y, z_seat, length, *, d=3.0, head_d=5.5, head_h=3.0, down=True, poise=POISE):
    """A socket-head cap screw poised over the seat at (x, y, `z_seat`).

    `z_seat` is the face the head lands on; `down` drives it into the part below. The screw sits
    `poise` along its withdrawal direction.
    """
    sign = -1.0 if down else 1.0
    z = z_seat - sign * poise
    head = cq.Workplane("XY", origin=(x, y, z)).circle(head_d / 2.0).extrude(-sign * head_h)
    shank = cq.Workplane("XY", origin=(x, y, z)).circle(d / 2.0).extrude(sign * length)
    return head.union(shank)


def _csk(x, y, z_seat, length, *, d=5.0, head_d=9.8, head_h=2.8, down=True, poise=POISE):
    """A DIN 7991 90-degree countersunk screw, poised the same way."""
    sign = -1.0 if down else 1.0
    z = z_seat - sign * poise
    head = (
        cq.Workplane("XY", origin=(x, y, z))
        .circle(head_d / 2.0)
        .workplane(offset=sign * head_h)
        .circle(d / 2.0)
        .loft()
    )
    shank = (
        cq.Workplane("XY", origin=(x, y, z + sign * head_h))
        .circle(d / 2.0)
        .extrude(sign * (length - head_h))
    )
    return head.union(shank)


def _insert(x, y, z_face, depth, *, d=4.6, down=True, poise=POISE):
    """A heat-set insert poised off the bore it seats in at `z_face`.

    `down` presses it into an up-facing bore, so it stands above the face; otherwise it enters
    an underside bore and stands below it.
    """
    z0 = z_face + poise if down else z_face - poise - depth
    return cq.Workplane("XY", origin=(x, y, z0)).circle(d / 2.0).extrude(depth)


def _insert_along_y(x, y_face, z, depth, *, sign, d=4.6, poise=POISE):
    """An insert or screw driven inward along Y from an outside wall at `y_face`."""
    y0 = y_face + sign * poise
    return (
        cq.Workplane("XY", origin=(x, y0, z))
        .circle(d / 2.0)
        .extrude(depth)
        .rotate((x, y0, z), (x + 1.0, y0, z), sign * 90.0)
    )


def _radial_insert(angle, radius_outer, depth, z, *, d=4.6, poise=POISE):
    """An insert poised outside a collar's face at `angle`, pointing at the axis."""
    return (
        cq.Workplane("XY")
        .circle(d / 2.0)
        .extrude(depth)
        .rotate((0, 0, 0), (0, 1, 0), 90.0)
        .translate((radius_outer - depth + poise, 0.0, z))
        .rotate((0, 0, 0), (0, 0, 1), angle)
    )


def _radial_screw(angle, tip_radius, length, z, *, d=3.0, head_d=5.5, head_h=3.0, poise=POISE):
    """An M3 adjuster lying along `angle`, poised with its tip `poise` off `tip_radius`."""
    r0 = tip_radius + poise
    shank = (
        cq.Workplane("XY").circle(d / 2.0).extrude(length)
        .rotate((0, 0, 0), (0, 1, 0), 90.0).translate((r0, 0.0, z))
    )
    head = (
        cq.Workplane("XY").circle(head_d / 2.0).extrude(head_h)
        .rotate((0, 0, 0), (0, 1, 0), 90.0).translate((r0 + length, 0.0, z))
    )
    return shank.union(head).rotate((0, 0, 0), (0, 0, 1), angle)


def _cyl(x, y, z0, height, diameter):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(diameter / 2.0).extrude(height)


def _box(x, y, z0, sx, sy, sz):
    return cq.Workplane("XY", origin=(x, y, z0)).box(sx, sy, sz, centered=(True, True, False))


def _union(shapes):
    out = None
    for shape in shapes:
        out = shape if out is None else out.union(shape)
    return out


def _flip(shape):
    """Turn a part over the way a hand turns it: 180 degrees about X."""
    return shape.rotate((0, 0, 0), (1, 0, 0), 180.0)


# ---------------------------------------------------------------------------
# Stations, read out of the fixture's own module so a moved hole moves the picture.

def _polar(radius, angle):
    return wr._polar(radius, angle)


def foot_screw_stations():
    return [(fx + dx, fy)
            for fx, fy in wr.BASE_FOOT_CENTERS
            for dx in (-wr.BASE_FOOT_SCREW_X, wr.BASE_FOOT_SCREW_X)]


def race_ring_stations():
    return [_polar(wr.RACE_RING_SCREW_R, a) for a in wr.RACE_RING_SCREW_ANGLES]


def spool_stations():
    return [_polar(wr.SPOOL_SCREW_R, a) for a in wr.SPOOL_SCREW_ANGLES]


def nest_retainer_stations():
    return [_polar(wr.NEST_SCREW_R, a) for a in wr.NEST_RETAINER_ANGLES]


def tower_rail_stations():
    return [(x, sign * wr.TOWER_RAIL_INSERT_Y)
            for x in wr.TOWER_RAIL_INSERT_X for sign in (-1.0, 1.0)]


def carriage_clamp_stations():
    return [(wr.MOTOR_CENTER_NOMINAL + dx, sign)
            for dx in (-wr.MOTOR_CLAMP_SCREW_X, wr.MOTOR_CLAMP_SCREW_X)
            for sign in (-1.0, 1.0)]


# ---------------------------------------------------------------------------
# Assembly helpers

def _add(assembly, shape, name, color):
    if shape is not None:
        assembly.add(shape, name=name, color=step_safe(color))


def _scene(name):
    return cq.Assembly(name=f"{name}-scene")


def _feet(a, color=M_PETGF_BLACK):
    for index, (x, y) in enumerate(wr.BASE_FOOT_CENTERS):
        _add(a, wr.build_base_foot().translate((x, y, -wr.BASE_FOOT_H)), f"foot-{index+1}", color)


def _bearing(a, cage_color=M_PETGF_BLACK):
    _add(a, wr.build_cage(), "cage", cage_color)
    _add(a, wr.build_balls_proxy(), "balls", M_PP_BALL)


def _rotor(a, table=M_PETGF_BLACK, ring=M_PETGF_BLACK, spool=M_PETGF_BLACK):
    _add(a, wr.build_turntable(), "turntable", table)
    _add(a, wr.build_race_ring(), "race-ring", ring)
    _add(a, wr.build_spool(), "spool", spool)


def _drive(a, carriage=M_PETGF_BLACK, motor=M_STAINLESS, pulley=M_ALUMINIUM, belt=M_TPU_BLACK):
    _add(a, wr.build_motor_tower(), "motor-tower", M_PETGF_BLACK)
    _add(a, wr.build_motor_carriage(), "carriage", carriage)
    pad_y = interface.MOTOR_FRAME / 2.0 + wr.MOTOR_CLAMP_PAD_Y / 2.0
    _add(a, wr.build_motor_clamp_pad().translate(
        (wr.MOTOR_CENTER_NOMINAL, -pad_y, wr.MOTOR_FACE_Z + 2.0)), "pad-neg", M_PETGF_BLACK)
    _add(a, wr.build_motor_clamp_pad().rotate((0, 0, 0), (0, 0, 1), 180.0).translate(
        (wr.MOTOR_CENTER_NOMINAL, pad_y, wr.MOTOR_FACE_Z + 2.0)), "pad-pos", M_PETGF_BLACK)
    _add(a, wr.build_motor_proxy(), "motor", motor)
    _add(a, wr.build_motor_pulley_proxy(), "motor-pulley", pulley)
    _add(a, wr.build_belt_proxy(), "belt", belt)


def _ground(a, tower=M_PETGF_BLACK, arm=M_PETGF_BLACK, shoe=M_COPPER):
    _add(a, wr.build_ground_tower(), "ground-tower", tower)
    _add(a, wr.build_ground_arm(), "ground-arm", arm)
    _add(a, wr.build_ground_shoe_proxy(), "ground-shoe", shoe)


def _nest(a, color=M_PETGF_BLACK):
    _add(a, wr.build_nest().translate((0.0, 0.0, wr.NEST_SEAT_Z)), "nest", color)


def _whole(a, *, tube=False, tube_color=M_STAINLESS):
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _rotor(a)
    _drive(a)
    _ground(a)
    _nest(a)
    if tube:
        _add(a, wr.build_tube_proxy(), "tube", tube_color)
    return a


# ---------------------------------------------------------------------------
# Scenes

class Scene:
    def __init__(self, build, *, cam, target=None, span=None, size="2200x2200",
                 up=(0, 0, 1), ortho=True, zoom=None):
        self.build, self.cam, self.target = build, cam, target
        self.span, self.size, self.up, self.ortho, self.zoom = span, size, up, ortho, zoom


# --- the whole machine ------------------------------------------------------

def s_hero():
    return _whole(_scene("hero"), tube=True)


def s_hero_bare():
    return _whole(_scene("hero-bare"))


def s_operator():
    return _whole(_scene("operator"), tube=True)


def s_exploded():
    a = _scene("exploded")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, wr.build_cage().translate((0, 0, 45)), "cage", M_PETGF_BLACK)
    _add(a, wr.build_balls_proxy().translate((0, 0, 45)), "balls", M_PP_BALL)
    _add(a, wr.build_race_ring().translate((0, 0, 95)), "race-ring", M_PETGF_BLACK)
    _add(a, wr.build_turntable().translate((0, 0, 140)), "turntable", M_PETGF_BLACK)
    _add(a, wr.build_spool().translate((0, 0, 215)), "spool", M_PETGF_BLACK)
    _add(a, wr.build_nest().translate((0.0, 0.0, wr.NEST_SEAT_Z + 205)), "nest", M_PETGF_BLACK)
    _add(a, wr.build_motor_tower().translate((150, 0, 0)), "motor-tower", M_PETGF_BLACK)
    _add(a, wr.build_motor_carriage().translate((150, 0, 130)), "carriage", M_PETGF_BLACK)
    pad_y = interface.MOTOR_FRAME / 2.0 + wr.MOTOR_CLAMP_PAD_Y / 2.0
    _add(a, wr.build_motor_clamp_pad().translate(
        (wr.MOTOR_CENTER_NOMINAL + 150, -pad_y - 45, wr.MOTOR_FACE_Z + 130)),
        "pad-neg", M_PETGF_BLACK)
    _add(a, wr.build_motor_clamp_pad().rotate((0, 0, 0), (0, 0, 1), 180.0).translate(
        (wr.MOTOR_CENTER_NOMINAL + 150, pad_y + 45, wr.MOTOR_FACE_Z + 130)),
        "pad-pos", M_PETGF_BLACK)
    _add(a, wr.build_ground_tower().translate((-30, -130, 0)), "ground-tower", M_PETGF_BLACK)
    _add(a, wr.build_ground_arm().translate((-30, -130, 85)), "ground-arm", M_PETGF_BLACK)
    _add(a, wr.build_ground_shoe_proxy().translate((-30, -130, 150)), "shoe", M_COPPER)
    _add(a, wr.build_pulley_coupon().translate((-170, 90, 0)), "coupon", M_PETGF_BLACK)
    return a


# --- printing ---------------------------------------------------------------

def _on_bed(shape):
    """A part dropped so its lowest point sits on Z=0 — the plate, as it is sliced."""
    bb = shape.val().BoundingBox()
    return shape.translate((0, 0, -bb.zmin))


def s_coupon():
    a = _scene("coupon")
    _add(a, _on_bed(wr.build_pulley_coupon()), "coupon", M_ACCENT)
    return a


def s_plate_base():
    a = _scene("plate-base")
    _add(a, _on_bed(wr.build_base()), "base", M_PETGF_BLACK)
    return a


def s_plate_turntable():
    a = _scene("plate-turntable")
    _add(a, _on_bed(wr.build_turntable()), "turntable", M_PETGF_BLACK)
    return a


def s_plate_small():
    """Every remaining printed part, each lying on the face it prints on."""
    a = _scene("plate-small")
    _add(a, _on_bed(wr.build_race_ring()).translate((0, 0, 0)), "race-ring", M_PETGF_BLACK)
    _add(a, _on_bed(_flip(wr.build_spool())).translate((230, 0, 0)), "spool", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_nest()).translate((0, 230, 0)), "nest", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_cage()).translate((230, 230, 0)), "cage", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_motor_tower().translate((-140, 0, 0))).translate((-190, 0, 0)),
         "motor-tower", M_PETGF_BLACK)
    _add(a, _on_bed(_flip(wr.build_motor_carriage().translate((-125, 0, 0))))
         .translate((-190, 150, 0)), "carriage", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_motor_clamp_pad().rotate((0, 0, 0), (1, 0, 0), 90.0))
         .translate((-190, 250, 0)), "pad-a", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_motor_clamp_pad().rotate((0, 0, 0), (1, 0, 0), 90.0))
         .translate((-140, 250, 0)), "pad-b", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_ground_tower().translate((99.5, 50.0, 0)))
         .translate((-40, -180, 0)), "ground-tower", M_PETGF_BLACK)
    _add(a, _on_bed(wr.build_ground_arm().rotate((0, 0, 0), (1, 0, 0), 90.0)
                    .translate((99.5, 0.0, 0.0))).translate((90, -180, 0)),
         "ground-arm", M_PETGF_BLACK)
    for index in range(4):
        _add(a, _on_bed(wr.build_base_foot()).translate((-190 + index * 55, -260, 0)),
             f"foot-{index+1}", M_PETGF_BLACK)
    return a


# --- heat-set inserts -------------------------------------------------------

def s_inserts_base():
    a = _scene("inserts-base")
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, _union([_insert(x, y, wr.BASE_Z, wr.M5_INSERT_DEPTH, d=7.0)
                    for x, y in tuple(wr.TOWER_MOUNT_POINTS) + tuple(wr.GROUND_BASE_POINTS)]),
         "m5-inserts", M_BRASS)
    return a


def s_inserts_base_tower():
    a = s_inserts_base()
    a.name = "inserts-base-tower-scene"
    return a


def s_inserts_table_under():
    """The turntable turned over: six M3 inserts down into its flat underside."""
    a = _scene("inserts-table-under")
    _add(a, _flip(wr.build_turntable()), "turntable", M_PETGF_BLACK)
    pins = [_insert(x, y, wr.PLATTER_Z0, wr.RACE_RING_INSERT_DEPTH, down=False)
            for x, y in race_ring_stations()]
    pins += [_insert(x, y, wr.PLATTER_Z0, wr.SPOOL_INSERT_DEPTH, down=False)
             for x, y in spool_stations()]
    _add(a, _flip(_union(pins)), "underside-inserts", M_BRASS)
    return a


def s_inserts_table_nest():
    """The turntable upright: three M3 inserts down into the nest register face."""
    a = _scene("inserts-table-nest")
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _add(a, _union([_insert(x, y, wr.NEST_SEAT_Z, wr.NEST_INSERT_DEPTH)
                    for x, y in nest_retainer_stations()]), "nest-inserts", M_BRASS)
    return a


def s_inserts_nest():
    a = _scene("inserts-nest")
    _add(a, wr.build_nest(), "nest", M_PETGF_BLACK)
    _add(a, _union([_radial_insert(angle, wr.OUTER_COLLAR_OD / 2.0,
                                   wr.TUBE_ADJUSTER_INSERT_DEPTH, wr.TUBE_ADJUSTER_Z)
                    for angle in wr.TUBE_ADJUSTER_ANGLES]), "adjuster-inserts", M_BRASS)
    return a


def s_inserts_tower():
    a = _scene("inserts-tower")
    _add(a, wr.build_motor_tower(), "motor-tower", M_PETGF_BLACK)
    _add(a, _union([_insert(x, y, wr.TOWER_Z1, wr.TOWER_RAIL_INSERT_DEPTH)
                    for x, y in tower_rail_stations()]), "rail-inserts", M_BRASS)
    return a


def s_inserts_carriage():
    """The carriage's four side-wall inserts, pressed inward from outside."""
    a = _scene("inserts-carriage")
    _add(a, wr.build_motor_carriage(), "carriage", M_PETGF_BLACK)
    pins = [_insert_along_y(x, sign * wr.CARRIAGE_WALL_Y1, wr.MOTOR_CLAMP_SCREW_Z,
                            wr.MOTOR_CLAMP_INSERT_DEPTH, sign=sign)
            for x, sign in carriage_clamp_stations()]
    _add(a, _union(pins), "clamp-inserts", M_BRASS)
    return a


def s_inserts_ground():
    """The ground tower's two top inserts, which the flexure arm bolts to."""
    a = _scene("inserts-ground")
    _add(a, wr.build_ground_tower(), "ground-tower", M_PETGF_BLACK)
    _add(a, _union([_insert(x, y, wr.GROUND_TOP_Z, wr.GROUND_ARM_INSERT_DEPTH, poise=11.0)
                    for x, y in wr.GROUND_ARM_POINTS]), "arm-inserts", M_BRASS)
    return a


def s_inserts_foot():
    a = _scene("inserts-foot")
    foot = wr.build_base_foot()
    _add(a, foot, "foot", M_PETGF_BLACK)
    _add(a, _union([_insert(x, 0.0, wr.BASE_FOOT_H, wr.BASE_FOOT_INSERT_DEPTH)
                    for x in (-wr.BASE_FOOT_SCREW_X, wr.BASE_FOOT_SCREW_X)]),
         "foot-inserts", M_BRASS)
    return a


# --- the stationary structure ----------------------------------------------

def s_feet():
    """The four feet on the bench, the base lifted off them, eight M3 x 25 above its top face.

    The screws are flush in the base's TOP face and thread down into the feet, so the base is
    never turned over for this: the feet go under it and the driver works from above.
    """
    a = _scene("feet")
    _add(a, wr.build_base().translate((0, 0, 62)), "base", M_PETGF_BLACK)
    for index, (x, y) in enumerate(wr.BASE_FOOT_CENTERS):
        _add(a, wr.build_base_foot().translate((x, y, -wr.BASE_FOOT_H)),
             f"foot-{index+1}", M_ACCENT)
    _add(a, _union([_shcs(x, y, wr.BASE_Z + 62, wr.BASE_FOOT_SCREW_LENGTH, poise=24.0)
                    for x, y in foot_screw_stations()]), "m3x25", M_STAINLESS)
    return a


def s_service():
    """Two 25.4 mm probes standing where the welded lower plate's ports will be."""
    a = _scene("service")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _rotor(a)
    _nest(a)
    _add(a, _union([_cyl(*_polar(30.0, angle), -wr.BASE_FOOT_H - 55.0,
                         wr.BASE_FOOT_H + 55.0 + wr.PLATTER_Z1, 25.4)
                    for angle in (30.0, 210.0)]), "25.4mm-probe", M_GAUGE)
    return a


def s_race_ring():
    """The turntable turned over, race ring going on groove-down."""
    a = _scene("race-ring")
    _add(a, _flip(wr.build_turntable()), "turntable", M_PETGF_BLACK)
    _add(a, _flip(wr.build_race_ring().translate((0, 0, -22))), "race-ring", M_ACCENT)
    _add(a, _flip(_union([_shcs(x, y, wr.RACE_RING_Z0 - 22, wr.RACE_RING_SCREW_LENGTH,
                                down=False, poise=26.0)
                          for x, y in race_ring_stations()])), "m3x8", M_STAINLESS)
    return a


def s_balls():
    """Cage in the base's lower race, thirty-six sorted balls in its pockets."""
    a = _scene("balls")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, wr.build_cage(), "cage", M_ACCENT)
    _add(a, wr.build_balls_proxy(), "balls", M_PP_BALL)
    return a


def s_turntable_on():
    """The rotor lowered onto the loaded race."""
    a = _scene("turntable-on")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _add(a, wr.build_turntable().translate((0, 0, 60)), "turntable", M_ACCENT)
    _add(a, wr.build_race_ring().translate((0, 0, 60)), "race-ring", M_ACCENT)
    return a


def s_spool():
    """The spool entering from below and three M3 x 25 drawing it up into the platter."""
    a = _scene("spool")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _add(a, wr.build_race_ring(), "race-ring", M_PETGF_BLACK)
    _add(a, wr.build_spool().translate((0, 0, -34)), "spool", M_ACCENT)
    _add(a, _union([_shcs(x, y, wr.SPOOL_FLANGE_Z0 - 34, wr.SPOOL_SCREW_LENGTH,
                          down=False, poise=26.0)
                    for x, y in spool_stations()]), "m3x25", M_STAINLESS)
    return a


def s_tower():
    """The motor tower on its four M5 stations, driven down the access holes."""
    a = _scene("tower")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _rotor(a)
    _add(a, wr.build_motor_tower().translate((0, 0, 30)), "motor-tower", M_ACCENT)
    _add(a, _union([_shcs(x, y, wr.TOWER_FOOT_Z1 + 30, 10.0, d=5.0, head_d=8.5, head_h=5.0,
                          poise=26.0)
                    for x, y in wr.TOWER_MOUNT_POINTS]), "m5x10", M_STAINLESS)
    return a


# --- the drive --------------------------------------------------------------

def s_pulley_gauge():
    """The 20T pulley gauged 0.25 mm off the motor's own face pilot."""
    a = _scene("pulley-gauge")
    _add(a, wr.build_motor_proxy(), "motor", M_STAINLESS)
    _add(a, wr.build_motor_pulley_proxy(), "pulley", M_ACCENT)
    _add(a, _box(wr.MOTOR_CENTER_NOMINAL, -50.0, wr.MOTOR_PULLEY_Z1,
                 16.0, 76.0, wr.MOTOR_PULLEY_PILOT_GAP), "0.25mm-feeler", M_GAUGE)
    return a


def s_motor_on_carriage():
    """The carriage skin-up on two blocks, the motor lowered face-down onto its pilot."""
    a = _scene("motor-on-carriage")
    _add(a, _flip(wr.build_motor_carriage()), "carriage", M_PETGF_BLACK)
    _add(a, _flip(wr.build_motor_proxy().translate((0, 0, 46))), "motor", M_ACCENT)
    _add(a, _flip(wr.build_motor_pulley_proxy().translate((0, 0, 46))), "pulley", M_ALUMINIUM)
    _add(a, _flip(_union([_csk(wr.MOTOR_MOUNT_X, sign * wr.MOTOR_MOUNT_Y, wr.CARRIAGE_ARM_Z0,
                               20.0, down=False, poise=30.0)
                          for sign in (-1.0, 1.0)])), "m5x20-csk", M_STAINLESS)
    for sign in (-1.0, 1.0):
        _add(a, _flip(_box(wr.MOTOR_CENTER_NOMINAL, sign * 64.0,
                           wr.CARRIAGE_ARM_Z0 - 25.0, 64.0, 26.0, 25.0)),
             f"block-{'p' if sign > 0 else 'n'}", M_GAUGE)
    return a


def s_motor_pads():
    """The two clamp pads and their four M3 x 8, on the assembled motor and carriage."""
    a = _scene("motor-pads")
    _add(a, wr.build_motor_carriage(), "carriage", M_PETGF_BLACK)
    _add(a, wr.build_motor_proxy(), "motor", M_STAINLESS)
    pad_y = interface.MOTOR_FRAME / 2.0 + wr.MOTOR_CLAMP_PAD_Y / 2.0
    _add(a, wr.build_motor_clamp_pad().translate(
        (wr.MOTOR_CENTER_NOMINAL, -pad_y - 22.0, wr.MOTOR_FACE_Z + 2.0)), "pad-neg", M_ACCENT)
    _add(a, wr.build_motor_clamp_pad().rotate((0, 0, 0), (0, 0, 1), 180.0).translate(
        (wr.MOTOR_CENTER_NOMINAL, pad_y + 22.0, wr.MOTOR_FACE_Z + 2.0)), "pad-pos", M_ACCENT)
    pins = [_insert_along_y(x, sign * (wr.CARRIAGE_WALL_Y1 + 22.0), wr.MOTOR_CLAMP_SCREW_Z,
                            8.0, sign=sign, d=3.0, poise=10.0)
            for x, sign in carriage_clamp_stations()]
    _add(a, _union(pins), "m3x8", M_STAINLESS)
    return a


def s_carriage_on():
    """Carriage and motor going down onto the rails, the belt already round both pulleys."""
    a = _scene("carriage-on")
    _feet(a)
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _bearing(a)
    _rotor(a)
    _add(a, wr.build_motor_tower(), "motor-tower", M_PETGF_BLACK)
    _add(a, wr.build_motor_carriage().translate((0, 0, 45)), "carriage", M_ACCENT)
    _add(a, wr.build_motor_proxy().translate((0, 0, 45)), "motor", M_STAINLESS)
    _add(a, wr.build_motor_pulley_proxy().translate((0, 0, 45)), "pulley", M_ALUMINIUM)
    _add(a, wr.build_belt_proxy(), "belt", M_TPU_BLACK)
    _add(a, _union([_shcs(x, y, wr.MOTOR_FACE_Z + 45, 10.0, poise=22.0)
                    for x, y in tower_rail_stations()]), "m3x10", M_STAINLESS)
    return a


def s_belt():
    """From directly above: the two spans, where the 90-degree twist is judged."""
    a = _scene("belt")
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _add(a, wr.build_motor_tower(), "motor-tower", M_PETGF_BLACK)
    _add(a, wr.build_motor_carriage(), "carriage", M_PETGF_BLACK)
    _add(a, wr.build_motor_pulley_proxy(), "pulley", M_ALUMINIUM)
    _add(a, wr.build_belt_proxy(), "belt", M_ACCENT)
    return a


# --- nest and contact -------------------------------------------------------

def s_nest_on():
    """The nest onto its register, three retainers down the access wells."""
    a = _scene("nest-on")
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _add(a, wr.build_race_ring(), "race-ring", M_PETGF_BLACK)
    _add(a, wr.build_nest().translate((0.0, 0.0, wr.NEST_SEAT_Z + 40.0)), "nest", M_ACCENT)
    _add(a, _union([_shcs(x, y, wr.NEST_SEAT_Z + wr.NEST_BASE_H + 40.0,
                          wr.NEST_RETAINER_SCREW_LENGTH, poise=22.0)
                    for x, y in nest_retainer_stations()]), "m3x10", M_STAINLESS)
    return a


def s_adjusters():
    """The three M3 x 25 tube adjusters, backed fully clear of the guide bore."""
    a = _scene("adjusters")
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _nest(a)
    _add(a, _union([_radial_screw(angle, wr.OUTER_COLLAR_OD / 2.0 - 4.0, 25.0,
                                  wr.NEST_SEAT_Z + wr.TUBE_ADJUSTER_Z, poise=10.0)
                    for angle in wr.TUBE_ADJUSTER_ANGLES]), "m3x25", M_ACCENT)
    return a


def s_ground():
    """Ground tower, flexure arm and the crosscut C110 shoe, loaded by the tube."""
    a = _scene("ground")
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _add(a, wr.build_race_ring(), "race-ring", M_PETGF_BLACK)
    _nest(a)
    _add(a, wr.build_tube_proxy(), "tube", M_STAINLESS)
    _add(a, wr.build_ground_tower(), "ground-tower", M_PETGF_BLACK)
    _add(a, wr.build_ground_arm(), "ground-arm", M_PETGF_BLACK)
    _add(a, wr.build_ground_shoe_proxy(), "ground-shoe", M_ACCENT)
    return a


def s_ground_arm_on():
    """The ground tower on its two M5 stations, the flexure arm poised over its two M3."""
    a = _scene("ground-arm-on")
    _add(a, wr.build_base(), "base", M_PETGF_BLACK)
    _add(a, wr.build_ground_tower(), "ground-tower", M_ACCENT)
    _add(a, wr.build_ground_arm().translate((0, 0, 40)), "ground-arm", M_ACCENT)
    _add(a, _union([_shcs(x, y, wr.GROUND_TOP_Z + 40, 12.0, poise=15.0)
                    for x, y in wr.GROUND_ARM_POINTS]), "m3x12", M_STAINLESS)
    _add(a, _union([_shcs(x, y, wr.TOWER_FOOT_Z1, 10.0, d=5.0, head_d=8.5, head_h=5.0,
                          poise=20.0)
                    for x, y in wr.GROUND_BASE_POINTS]), "m5x10", M_STAINLESS)
    return a


def s_shoe():
    """The shoe alone in its fork: one factory face at the tube, the cut edge on the shelf."""
    a = _scene("shoe")
    _add(a, wr.build_ground_tower(), "ground-tower", M_PETGF_BLACK)
    _add(a, wr.build_ground_arm(), "ground-arm", M_PETGF_BLACK)
    _add(a, wr.build_ground_shoe_proxy().translate((0, 0, 20)), "ground-shoe", M_ACCENT)
    return a


# --- the tube ---------------------------------------------------------------

def s_indicate():
    """The tube in the nest with the indicator standing on the motor's lamination face."""
    a = _whole(_scene("indicate"), tube=True, tube_color=M_ACCENT)
    mx = wr.MOTOR_CENTER_NOMINAL
    stand = _union([
        _box(mx, 0.0, wr.MOTOR_FACE_Z + 42.0, 54.0, 54.0, 62.0),
        _cyl(mx, 0.0, wr.MOTOR_FACE_Z + 104.0, 96.0, 13.0),
        (cq.Workplane("XY", origin=(mx, 0.0, wr.MOTOR_FACE_Z + 188.0))
         .box(mx + 74.0, 13.0, 13.0, centered=(False, True, False))
         .translate((-(mx + 74.0), 0.0, 0.0))),
        _cyl(interface.TUBE_OD / 2.0 + 6.0, 0.0, wr.MOTOR_FACE_Z + 178.0, 14.0, 9.0),
    ])
    _add(a, stand, "indicator", M_GAUGE)
    return a


def s_tube_in():
    """The tube dropping into the nest — the ID pilot and the OD guide it lands on."""
    a = _scene("tube-in")
    _add(a, wr.build_turntable(), "turntable", M_PETGF_BLACK)
    _nest(a)
    _add(a, wr.build_tube_proxy().translate((0, 0, 90)), "tube", M_ACCENT)
    return a


def s_elevation():
    """Straight on: where the tube's working rim stands over the highest printed part."""
    return _whole(_scene("elevation"), tube=True)


SCENES = {
    "hero": Scene(s_hero, cam=(1.0, -1.1, 0.62), size="2400x2400"),
    "hero-bare": Scene(s_hero_bare, cam=(1.0, -1.05, 0.55), size="2400x2000"),
    "operator": Scene(s_operator, cam=(-0.62, -1.0, 0.34), size="2200x2400"),
    "exploded": Scene(s_exploded, cam=(1.0, -1.0, 0.40), size="2400x2600"),

    "coupon": Scene(s_coupon, cam=(0.7, -1.0, 0.75), size="1800x1200"),
    "plate-base": Scene(s_plate_base, cam=(0.5, -0.8, 0.9), size="2200x1600"),
    "plate-turntable": Scene(s_plate_turntable, cam=(0.5, -0.8, 0.85), size="2000x1600"),
    "plate-small": Scene(s_plate_small, cam=(0.25, -0.5, 1.0), size="2400x2200"),

    "inserts-base": Scene(s_inserts_base, cam=(0.55, -0.85, 0.80), size="2400x1700"),
    "inserts-base-tower": Scene(s_inserts_base_tower, cam=(0.7, -0.9, 0.75),
                                target=(140.0, 0.0, 14.0), span=62.0, size="1800x1500"),
    "inserts-table-under": Scene(s_inserts_table_under, cam=(0.5, -0.8, 0.85), size="2000x1600"),
    "inserts-table-nest": Scene(s_inserts_table_nest, cam=(0.55, -0.85, 0.8), size="2000x1600"),
    "inserts-nest": Scene(s_inserts_nest, cam=(-0.55, -0.85, 0.34),
                          target=(-58.0, 0.0, 13.0), span=42.0, size="1800x1400"),
    "inserts-tower": Scene(s_inserts_tower, cam=(0.8, -0.9, 0.7), size="1800x1400"),
    "inserts-carriage": Scene(s_inserts_carriage, cam=(0.75, -0.9, 0.55), size="1900x1400"),
    "inserts-ground": Scene(s_inserts_ground, cam=(-0.8, -0.9, 0.55),
                            target=(-104.0, -50.0, 64.0), span=44.0, size="1700x1500"),
    "inserts-foot": Scene(s_inserts_foot, cam=(0.6, -0.9, 0.75), size="1500x1200"),

    "feet": Scene(s_feet, cam=(0.65, -0.9, 0.75), size="2400x1700"),
    "service": Scene(s_service, cam=(0.85, -1.0, 0.24), size="2200x1800"),
    "race-ring": Scene(s_race_ring, cam=(0.55, -0.9, 0.75), size="2000x1700"),
    "balls": Scene(s_balls, cam=(0.4, -0.65, 1.05), size="2200x1700"),
    "turntable-on": Scene(s_turntable_on, cam=(0.75, -1.0, 0.45), size="2200x2000"),
    "spool": Scene(s_spool, cam=(0.85, -1.0, -0.42), size="2200x1800"),
    "tower": Scene(s_tower, cam=(-0.30, -0.95, 0.52), target=(144.0, 0.0, 42.0),
                   span=86.0, size="2000x1800"),

    "pulley-gauge": Scene(s_pulley_gauge, cam=(0.85, -1.0, 0.40), size="1800x1700"),
    "motor-on-carriage": Scene(s_motor_on_carriage, cam=(0.85, -1.0, 0.5), size="2000x1700"),
    "motor-pads": Scene(s_motor_pads, cam=(0.8, -1.0, 0.5), size="1900x1500"),
    "carriage-on": Scene(s_carriage_on, cam=(0.9, -0.85, 0.5), target=(110.0, 0.0, 60.0),
                         span=132.0, size="2000x1900"),
    "belt": Scene(s_belt, cam=(0.22, -1.0, 0.30), target=(72.0, 0.0, 42.0), span=86.0,
                  size="2200x1600"),

    "nest-on": Scene(s_nest_on, cam=(0.65, -0.95, 0.62), size="2000x1700"),
    "adjusters": Scene(s_adjusters, cam=(0.5, -0.85, 0.55), size="2000x1500"),
    "ground": Scene(s_ground, cam=(-0.55, -1.0, 0.30), size="2000x2000"),
    "ground-arm-on": Scene(s_ground_arm_on, cam=(-0.62, -1.0, 0.42),
                           target=(-100.0, -44.0, 78.0), span=88.0, size="1900x1800"),
    "shoe": Scene(s_shoe, cam=(0.55, -1.0, 0.34), target=(-72.0, -4.0, 102.0), span=58.0,
                  size="1700x1700"),

    "tube-in": Scene(s_tube_in, cam=(0.6, -1.0, 0.42), size="1900x2100"),
    "indicate": Scene(s_indicate, cam=(0.9, -1.0, 0.30), size="2200x2400"),
    "elevation": Scene(s_elevation, cam=(1.0, -0.06, 0.10), size="1900x2400"),
}


# ---------------------------------------------------------------------------

def _clear_background(path: Path) -> None:
    """Flood the connected white field to transparent; enclosed whites survive."""
    magick = shutil.which("magick") or shutil.which("convert")
    if not magick:
        raise RuntimeError("ImageMagick is required to clear picture backgrounds")
    primitive = "alpha" if Path(magick).name == "magick" else "matte"
    subprocess.run(
        [magick, str(path), "-bordercolor", "white", "-border", "1",
         "-alpha", "set", "-channel", "RGBA", "-fuzz", "3%",
         "-fill", "none", "-draw", f"{primitive} 0,0 floodfill",
         "-shave", "1x1", "-trim", "+repage", str(path)],
        check=True,
    )
    with Image.open(path) as image:
        image.convert("RGBA").save(path, format="PNG", compress_level=9, optimize=False)


def render(names: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rotator-art-", dir=OUT) as directory:
        work = Path(directory)
        jobs = []
        for name in names:
            scene = SCENES[name]
            step = work / f"{name}.step"
            _per_solid_color(scene.build()).export(str(step))
            job = {
                "step": str(step.relative_to(HARDWARE)),
                "out": str(ART / f"{name}.png"),
                "cam": list(scene.cam),
                "up": list(scene.up),
                "size": scene.size,
                "bg": "#ffffff",
                "trim": True,
                "solid": True,
                "ortho": scene.ortho,
                # No contact shadow and no distance fade: these land on paper.
                "ground": False,
                "fog": False,
            }
            if scene.target is not None:
                job["target"] = list(scene.target)
            if scene.span is not None:
                job["span"] = scene.span
            if scene.zoom is not None:
                job["zoom"] = scene.zoom
            jobs.append(job)
            print(f"  staged {name}")
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
        for job in jobs:
            out = Path(job["out"])
            _clear_background(out)
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
