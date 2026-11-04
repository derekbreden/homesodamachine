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

Run with tools/cad-venv/bin/python. No argument exports the print.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _repo / "tools"):
    sys.path.insert(0, str(_path))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

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

SLOT_W = 0.8
SLOT_L = 40.0
SLOT_DEPTH = 15.0
END_WALL = 5.0
FLOOR_UNDER_SLOT = 3.0
OFFCUT_SIDE = 5.0
KEEP_SIDE = 19.0
TROUGH_FLOOR_ABOVE_SLOT_FLOOR = 2.5
TROUGH_PITCH = 20.0

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


def numbers():
    """Current block, tube troughs and blade path, in the print frame."""
    from _material_base import M_PETGF_BLACK
    from _materials import linear
    y = (slot_y0 + slot_y1) / 2
    return {
        "block": [BLOCK_X, BLOCK_Y, BLOCK_Z],
        "trough_floor": trough_floor_z,
        "troughs": [value for x, od in TROUGHS.values()
                    for value in (x, trough_r(od), od)],
        "slot_y": [slot_y0, slot_y1], "slot_length": SLOT_L,
        "slot_floor": slot_floor_z,
        "razor_bounds": [-RAZOR_BLADE_L/2, RAZOR_BLADE_L/2,
                         y-RAZOR_BLADE_T/2, y+RAZOR_BLADE_T/2,
                         razor_edge_z, BLOCK_Z],
        "color": list(linear(M_PETGF_BLACK)),
    }


def _document():
    from docgen import substitute_md
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


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "tube-miter-box", numbers(), out)
    _document()
    print(f"-> tube-miter-box STEP, STL and fine model; {said['bodies'][0]['volume'] / 1000:.2f} cm3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
