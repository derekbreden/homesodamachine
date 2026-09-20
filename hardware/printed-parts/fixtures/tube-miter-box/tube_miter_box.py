"""Tube miter box: the bench block that holds 1/4" and 3/8" OD LLDPE tube round and guides a
razor blade square across it.

Two open troughs run along Y, one per tube size: a half-round floor at the tube's radius plus
a running fit, under vertical walls the same width apart, open at the top face so a tube lies
in from above at any point along its length. One slot crosses both troughs in the XZ plane. A
0.009" single-edge razor blade drops into it from the top face; the slot's walls to either side
of each trough hold the blade in one plane while the trough holds the tube round under it, and
the spine landing on the top face ends the stroke with the edge below the trough floor. A
0.025" utility blade fits the same slot and ends on the slot floor.

The slot stands nearer one end face. The short side carries the offcut; the long side aligns
the tube that is kept.

Frame: X along the blade, Y along the tube, +Z up. The bottom face is Z = 0 and is the print
bed. Every face is vertical, upward or a valley; the print needs no support.

Run with tools/cad-venv/bin/python. No argument exports the print; `selftest` checks geometry
without writing files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _cadq_export import export_assembly, note_write  # noqa: E402
from _material_base import M_PETGF_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402
from fits import running  # noqa: E402


INCH = 25.4

TUBE_OD_1_4 = INCH / 4
TUBE_OD_3_8 = INCH * 3 / 8

# Single-edge razor blade, 1.5 x 0.75 x 0.009 in; the folded back runs along its top edge
# and is what a thumb pushes on.
RAZOR_BLADE_L = 1.5 * INCH
RAZOR_BLADE_H = 0.75 * INCH
RAZOR_BLADE_T = 0.009 * INCH
RAZOR_SPINE_H = 5.0
RAZOR_REACH = RAZOR_BLADE_H - RAZOR_SPINE_H

UTILITY_BLADE_T = 0.025 * INCH

SLOT_W = 0.8
SLOT_L = 40.0
SLOT_DEPTH = 15.0
END_WALL = 5.0
FLOOR_UNDER_SLOT = 3.0
OFFCUT_SIDE = 5.0
KEEP_SIDE = 19.0
TROUGH_FLOOR_ABOVE_SLOT_FLOOR = 2.5
TROUGH_PITCH = 20.0
MIN_WALL = 3.0
MIN_WALL_ABOVE_TUBE = 2.0
MIN_RAZOR_PAST_FLOOR = 1.0
MIN_BLADE_END_PLAY = 0.5
MIN_GUIDE_L = 20.0

BLOCK_X = SLOT_L + 2 * END_WALL
BLOCK_Y = OFFCUT_SIDE + SLOT_W + KEEP_SIDE
BLOCK_Z = FLOOR_UNDER_SLOT + SLOT_DEPTH

slot_y0 = OFFCUT_SIDE
slot_y1 = OFFCUT_SIDE + SLOT_W
slot_floor_z = FLOOR_UNDER_SLOT
trough_floor_z = slot_floor_z + TROUGH_FLOOR_ABOVE_SLOT_FLOOR
razor_edge_z = BLOCK_Z - RAZOR_REACH

TROUGHS = {
    "1/4": (-TROUGH_PITCH / 2, TUBE_OD_1_4),
    "3/8": (TROUGH_PITCH / 2, TUBE_OD_3_8),
}

MESH_TOLERANCE = 0.02
MESH_ANGLE = 0.15


def trough_r(tube_od):
    return tube_od / 2 + running


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane(obj=cq.Solid.makeBox(
        x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0)
    ))


def _along_y(radius, x, z, y0, y1):
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        radius, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0)
    ))


def _trough(x, tube_od):
    r = trough_r(tube_od)
    axis_z = trough_floor_z + r
    floor = _along_y(r, x, axis_z, -1.0, BLOCK_Y + 1.0)
    walls = _box(x - r, x + r, -1.0, BLOCK_Y + 1.0, axis_z, BLOCK_Z + 1.0)
    return floor.union(walls)


def _slot():
    return _box(-SLOT_L / 2, SLOT_L / 2, slot_y0, slot_y1, slot_floor_z, BLOCK_Z + 1.0)


def build():
    block = _box(-BLOCK_X / 2, BLOCK_X / 2, 0.0, BLOCK_Y, 0.0, BLOCK_Z)
    for x, tube_od in TROUGHS.values():
        block = block.cut(_trough(x, tube_od))
    return block.cut(_slot())


def _tube(x, tube_od):
    return _along_y(tube_od / 2, x, trough_floor_z + tube_od / 2, 0.0, BLOCK_Y)


def _razor_at_stroke_end():
    y = (slot_y0 + slot_y1) / 2
    return _box(-RAZOR_BLADE_L / 2, RAZOR_BLADE_L / 2,
                y - RAZOR_BLADE_T / 2, y + RAZOR_BLADE_T / 2,
                razor_edge_z, BLOCK_Z)


def _volume(shape):
    return sum(s.Volume() for s in shape.solids().vals())


def _single_valid(name, shape):
    solids = shape.solids().vals()
    if len(solids) != 1 or not solids[0].isValid() or solids[0].Volume() <= 0:
        raise ValueError(f"{name}: expected one valid, positive-volume solid")
    return solids[0]


def selftest():
    block = build()
    _single_valid("tube miter box", block)

    troughs = {}
    for name, (x, tube_od) in TROUGHS.items():
        r = trough_r(tube_od)
        if _volume(block.intersect(_tube(x, tube_od))) > 1e-6:
            raise ValueError(f"{name}: the tube meets its trough")
        wall_above_tube = BLOCK_Z - (trough_floor_z + tube_od)
        if wall_above_tube < MIN_WALL_ABOVE_TUBE:
            raise ValueError(f"{name}: too little wall above the tube to guide the blade")
        cap = _box(x - r, x + r, 0.0, BLOCK_Y, BLOCK_Z - 0.5, BLOCK_Z)
        if _volume(block.intersect(cap)) > 1e-6:
            raise ValueError(f"{name}: the trough is closed at the top face")
        troughs[name] = {"trough_w_mm": 2 * r, "wall_above_tube_mm": wall_above_tube}

    r_1_4 = trough_r(TUBE_OD_1_4)
    r_3_8 = trough_r(TUBE_OD_3_8)
    wall_between = TROUGH_PITCH - r_1_4 - r_3_8
    wall_outside = min(BLOCK_X / 2 - TROUGH_PITCH / 2 - r_1_4,
                       BLOCK_X / 2 - TROUGH_PITCH / 2 - r_3_8)
    if min(wall_between, wall_outside, END_WALL, FLOOR_UNDER_SLOT, OFFCUT_SIDE) < MIN_WALL:
        raise ValueError("a wall is thinner than the minimum")

    razor = _razor_at_stroke_end()
    if _volume(block.intersect(razor)) > 1e-6:
        raise ValueError("the razor at the end of its stroke meets the block")
    razor_past_floor = trough_floor_z - razor_edge_z
    if razor_past_floor < MIN_RAZOR_PAST_FLOOR:
        raise ValueError("the razor's edge stops short of the tube's floor")
    if razor_edge_z <= slot_floor_z:
        raise ValueError("the razor's edge reaches the slot floor before its spine lands")
    if UTILITY_BLADE_T > SLOT_W - 0.1:
        raise ValueError("a utility blade does not fit the slot")
    blade_end_play = (SLOT_L - RAZOR_BLADE_L) / 2
    if blade_end_play < MIN_BLADE_END_PLAY:
        raise ValueError("the razor blade does not drop into the slot")
    guide_l = SLOT_L - 2 * r_1_4 - 2 * r_3_8
    if guide_l < MIN_GUIDE_L:
        raise ValueError("too little slot wall beside the troughs to hold the blade square")

    bb = block.val().BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise ValueError("print does not sit on Z=0")
    if any(abs(a - b) > 1e-6 for a, b in zip((bb.xlen, bb.ylen, bb.zlen), (BLOCK_X, BLOCK_Y, BLOCK_Z))):
        raise ValueError("unexpected print envelope")

    print(json.dumps({
        "status": "CAD checks passed; the printed slot and a cut are untested",
        "troughs": troughs,
        "razor_past_trough_floor_mm": razor_past_floor,
        "razor_above_slot_floor_mm": razor_edge_z - slot_floor_z,
        "slot_guide_l_mm": guide_l,
        "blade_end_play_mm": blade_end_play,
    }, indent=2))
    return block


def _export_print(part):
    stem = "tube-miter-box"
    stl = _here.parent / f"{stem}.stl"
    step = _here.parent / f"{stem}.step"
    # A sibling slicer mesh keeps this bench fixture out of viewer payloads.
    cq.exporters.export(part, str(stl), tolerance=MESH_TOLERANCE, angularTolerance=MESH_ANGLE)
    note_write(stl)
    export_assembly(one_body(part, stem, M_PETGF_BLACK), str(step))
    print(f"-> {step.name}, {stl.name}: {_volume(part) / 1000:.2f} cm³")


def main():
    block = selftest()
    _export_print(block)
    substitute_md(_here.parent / "README.md", variables={
        "TMB_BLOCK": f"{BLOCK_X:g} × {BLOCK_Y:g} × {BLOCK_Z:g} mm",
        "TMB_TROUGH_1_4": f"{2 * trough_r(TUBE_OD_1_4):.2f} mm",
        "TMB_TROUGH_3_8": f"{2 * trough_r(TUBE_OD_3_8):.2f} mm",
        "TMB_RUNNING": f"{running:g} mm",
        "TMB_TROUGH_PITCH": f"{TROUGH_PITCH:g} mm",
        "TMB_SLOT_W": f"{SLOT_W:g} mm",
        "TMB_SLOT_L": f"{SLOT_L:g} mm",
        "TMB_OFFCUT_SIDE": f"{OFFCUT_SIDE:g} mm",
        "TMB_KEEP_SIDE": f"{KEEP_SIDE:g} mm",
        "TMB_RAZOR_PAST_FLOOR": f"{trough_floor_z - razor_edge_z:.2f} mm",
        "TMB_TROUGH_FLOOR_ABOVE_SLOT_FLOOR": f"{TROUGH_FLOOR_ABOVE_SLOT_FLOOR:g} mm",
        "TMB_WALL_ABOVE_3_8": f"{BLOCK_Z - (trough_floor_z + TUBE_OD_3_8):.2f} mm",
    })


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    elif sys.argv[1:]:
        sys.exit("usage: tube_miter_box.py [selftest]")
    else:
        main()
