"""Collet press — one-piece hand tool for releasing a 1/4-inch John Guest
push-to-connect collet.

Print orientation is the modelling orientation: the handle lies flat on Z=0
and the forked head rises from it at 45 degrees.  The head is one unstepped
slab.  Its U-slot passes the tube while the surrounding face bears on the
release sleeve.

Run:
    tools/cad-venv/bin/python \
        hardware/printed-parts/collet-press/collet_press.py
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path


_here = Path(__file__).resolve().parent
_hardware = next(p for p in _here.parents if p.name == "hardware")
_repo = _hardware.parent
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hardware / "reference" / "jg-pp0408w"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import jg_pp0408w as jg  # noqa: E402


# --- working fit -----------------------------------------------------------

# A close slip over nominal 1/4-inch tube.  It remains narrower than the
# measured collet bore, so each jaw arm spans the sleeve's complete radial wall.
JAW_GAP = 6.55
JAW_RADIUS = JAW_GAP / 2.0
JAW_ROOT_U = 0.0
# With the tube seated in the semicircular root, the straight inner edges run
# through the collet's forward OD tangent.  Every part of the annular release
# face reachable by the two arms is therefore under straight material before
# their rounded noses turn away.
STRAIGHT_TIP_U = jg.COLLET_D / 2.0
JAW_DEPTH = STRAIGHT_TIP_U - (JAW_ROOT_U - JAW_RADIUS)
STRAIGHT_OVERRUN = STRAIGHT_TIP_U - jg.PORT_D / 2.0


# --- printable body --------------------------------------------------------

HEAD_ANGLE = 45.0
HEAD_THICKNESS = 6.00       # 25 layers at 0.24 mm; 50 at 0.12 mm
HEAD_WIDTH = 20.0
ARM_WIDTH = (HEAD_WIDTH - JAW_GAP) / 2.0
TIP_RADIUS = 2.0
HEAD_BACK_LAND = ARM_WIDTH
HEAD_BACK_U = JAW_ROOT_U - JAW_RADIUS - HEAD_BACK_LAND
# The two rounded noses carry on by exactly their fillet radius after the
# straight lands reach the collet's outer edge.
HEAD_FRONT_U = STRAIGHT_TIP_U + TIP_RADIUS
HEAD_LENGTH = HEAD_FRONT_U - HEAD_BACK_U
HEAD_CENTER_U = (HEAD_BACK_U + HEAD_FRONT_U) / 2.0

# Length of the handle's bottom bed edge before its front rises at 45°.
HANDLE_LENGTH = 88.0
HANDLE_WIDTH = HEAD_WIDTH
HANDLE_THICKNESS = HEAD_THICKNESS
HANDLE_CORNER_RADIUS = TIP_RADIUS
# Enough overlap for a broad fused root, while the head's underside clears the
# tube slot before that slot begins.
ROOT_BURY = HEAD_THICKNESS * math.cos(math.radians(HEAD_ANGLE))
HEAD_REAR_LOWER_Z = HANDLE_THICKNESS - ROOT_BURY
HEAD_Z_SHIFT = (
    HEAD_REAR_LOWER_Z
    - HEAD_BACK_U * math.sin(math.radians(HEAD_ANGLE))
)


def _head_underside_x(z: float) -> float:
    """World X of the head's lower face at world height ``z``."""
    return (z - HEAD_Z_SHIFT) / math.tan(math.radians(HEAD_ANGLE))


HANDLE_FRONT_BED_X = _head_underside_x(0.0)
HANDLE_FRONT_TOP_X = _head_underside_x(HANDLE_THICKNESS)
HANDLE_REAR_X = HANDLE_FRONT_BED_X - HANDLE_LENGTH


def numbers():
    """The original handle, U-profile and print-pose dimensions."""
    from _materials import M_PETGF_BLACK, linear
    z0, z1 = -1.0, HANDLE_THICKNESS + 1.0
    return {
        "head_back": HEAD_BACK_U, "head_front": HEAD_FRONT_U,
        "head_width": HEAD_WIDTH, "head_thickness": HEAD_THICKNESS,
        "head_angle": HEAD_ANGLE, "head_z_shift": HEAD_Z_SHIFT,
        "jaw_gap": JAW_GAP, "jaw_root": JAW_ROOT_U, "tip_radius": TIP_RADIUS,
        "handle_x": [HANDLE_REAR_X, HANDLE_FRONT_TOP_X + 2.0],
        "handle_width": HANDLE_WIDTH, "handle_thickness": HANDLE_THICKNESS,
        "handle_corner_radius": HANDLE_CORNER_RADIUS,
        "handle_clip": [HANDLE_REAR_X - 2.0, z0, _head_underside_x(z0), z0,
                        _head_underside_x(z1), z1, HANDLE_REAR_X - 2.0, z1],
        "tube_diameter": jg.PORT_D, "collet_bore": jg.COLLET_BORE,
        "color": list(linear(M_PETGF_BLACK)),
    }


def _document(bb, volume):
    from docgen import substitute_md
    variables = {
        "TUBE_D": f"{jg.PORT_D:.2f} mm",
        "JAW_GAP": f"{JAW_GAP:.2f} mm",
        "JAW_DEPTH": f"{JAW_DEPTH:.2f} mm",
        "STRAIGHT_OVERRUN": f"{STRAIGHT_OVERRUN:.2f} mm",
        "ARM_W": f"{ARM_WIDTH:.3f} mm",
        "TIP_R": f"{TIP_RADIUS:.1f} mm",
        "HEAD_BACK_LAND": f"{HEAD_BACK_LAND:.3f} mm",
        "ROOT_BURY": f"{ROOT_BURY:.2f} mm",
        "TUBE_CLEARANCE": f"{JAW_GAP - jg.PORT_D:.2f} mm",
        "COLLET_D": f"{jg.COLLET_D:.2f} mm",
        "COLLET_BORE": f"{jg.COLLET_BORE:.2f} mm",
        "COLLET_WALL": f"{jg.COLLET_WALL:.2f} mm",
        "JAW_COVER": f"{(jg.COLLET_D - JAW_GAP) / 2.0:.2f} mm per side",
        "COLLET_TRAVEL": f"{jg.COLLET_TRAVEL:.3f} mm",
        "HEAD_ANGLE": f"{HEAD_ANGLE:.0f}°",
        "HEAD_T": f"{HEAD_THICKNESS:.2f} mm",
        "HEAD_W": f"{HEAD_WIDTH:.0f} mm",
        "HANDLE_L": f"{HANDLE_LENGTH:.0f} mm",
        "HANDLE_W": f"{HANDLE_WIDTH:.0f} mm",
        "HANDLE_T": f"{HANDLE_THICKNESS:.2f} mm",
        "TOOL_X": f"{bb.xlen:.1f} mm",
        "TOOL_Y": f"{bb.ylen:.1f} mm",
        "TOOL_Z": f"{bb.zlen:.1f} mm",
        "TOOL_VOLUME": f"{volume / 1000.0:.1f} cm³",
    }
    substitute_md(_here / "README.md", variables=variables)
    print("-> README.md")


def main(output=None):
    import _rust_part
    from types import SimpleNamespace
    out = Path(output) if output is not None else _here
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut("tooling", "collet-press", numbers(), out)
    body = said["bodies"][0]
    span = [high - low for high, low in zip(body["max"], body["min"])]
    _document(SimpleNamespace(xlen=span[0], ylen=span[1], zlen=span[2]), body["volume"])
    print(f"-> collet-press STEP, STL, fine model and payload; {body['volume'] / 1000:.2f} cm3")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
