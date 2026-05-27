"""Enclosure + cold-core assembly geometry for the engineering drawings.

Builds a plain rectangular appliance box (no knobs, buttons, doors, or
nameplate — this view is about internal layout, not external skin) with
the cold-core foam shell nested inside it. Returned as a single
cq.Compound so the CadQuery SVG exporter (which HLRs a Shape /
Compound — an Assembly fails its multimethod dispatch) can render the
whole thing in one projection: the box outer edges as solid lines and
the foam shell's outline visible through the walls as dashed hidden
lines.

Coordinate convention (matches _appliance_model.py):
- +X is the appliance's width axis. x=0 LEFT, x=APPLIANCE_W RIGHT.
- +Y is the appliance's depth axis. y=0 FRONT, y=APPLIANCE_D BACK.
- +Z is the appliance's height axis. z=0 BOTTOM, z=H TOP.
- The box origin is at the front-bottom-left corner.

Cold-core placement:
The foam shell is built in its own world frame centered on the X and Y
axes (X = [-141.5, +141.5], Y = [-90.5, +90.5]) with its floor at Z=0.
The appliance W (283 mm) exactly matches the foam shell's X length, so
the cold core fits side-to-side with ~0 mm gap — the appliance width
was derived from the foam-shell footprint. The appliance depth
(331 mm = foam-shell depth 181 + CONDENSER_DEPTH 150) places the cold
core flush against the back; the front 150 mm reserves space for the
condenser/Zone D. The cold core sits on the floor (Z=0)."""

from pathlib import Path
import sys

import cadquery as cq

_HERE = Path(__file__).resolve().parent
_ENCLOSURE = _HERE.parents[1]
_PRINTED_PARTS = _ENCLOSURE.parent

# Path additions match the existing cold-core engineering-drawings model
# and _appliance_model.py — so build_full_shell() and the enclosure
# dimension constants both resolve.
sys.path.insert(0, str(_PRINTED_PARTS / "cadlib"))
sys.path.insert(0, str(_PRINTED_PARTS / "cold-core"))
sys.path.insert(0, str(_ENCLOSURE))

from _foam_shell import build_full_shell
from _enclosure_dimensions import APPLIANCE_W, APPLIANCE_D
from _cold_core_interface import (
    outer_shell_x_length,
    outer_shell_y_length,
)


# Outer enclosure height. Same value as _appliance_model.py's H — keep
# them in sync if either side moves. (Not imported because that module
# carries cosmetic feature solids we explicitly DO NOT want here.)
H = 280.0


# Cold-core placement inside the appliance frame.
#
# Native foam-shell frame centers X and Y at 0, with floor at Z=0:
#   X: -outer_shell_x_length/2 .. +outer_shell_x_length/2
#   Y: -outer_shell_y_length/2 .. +outer_shell_y_length/2
#   Z: 0 .. foam_shell_outer_height
#
# To land it in the appliance frame (origin at front-bottom-left):
# - Center it across the appliance width (foam X length == APPLIANCE_W,
#   so this comes out flush with both side walls).
# - Push it to the BACK so its +Y face hugs the back wall (Y = APPLIANCE_D),
#   leaving the front depth for Zone D / condenser.
# - Sit it on the floor (Z stays at 0).
COLD_CORE_X_OFFSET = APPLIANCE_W / 2
COLD_CORE_Y_OFFSET = APPLIANCE_D - outer_shell_y_length / 2
COLD_CORE_Z_OFFSET = 0.0


def build_enclosure_box() -> cq.Workplane:
    """Plain solid box representing the appliance outer envelope.

    Solid (not shelled) on purpose: in CadQuery's default HLR, the
    box's outer edges render as solid lines and the cold core nested
    inside it shows through the walls as dashed hidden lines — exactly
    the engineering-drawing look we want."""
    return cq.Workplane("XY").box(APPLIANCE_W, APPLIANCE_D, H, centered=False)


def build_enclosure_assembly() -> cq.Compound:
    """Outer appliance box + cold-core foam shell positioned inside,
    flattened to a single cq.Compound for cq.exporters.export."""
    shapes = []

    shapes.append(build_enclosure_box().val())

    foam_shell = build_full_shell().val()
    foam_shell = foam_shell.translate(
        (COLD_CORE_X_OFFSET, COLD_CORE_Y_OFFSET, COLD_CORE_Z_OFFSET)
    )
    shapes.append(foam_shell)

    return cq.Compound.makeCompound(shapes)
