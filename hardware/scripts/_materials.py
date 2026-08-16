"""What each material on this machine looks like with the lights on.

A body is coloured by what it is MADE OF, and every part of one material takes one constant here.
Both ends read these: the assembly that places a body, and the generator that cuts the body's own
STEP — so the same part is the same colour in the picture of the machine and in the picture of
itself.

A COLOUR IS THREE COMPONENTS by the time it is drawn: `_mesh_payload` hands over the RGB a STEP
carries and occt-import-js reads back the same three. The pack is read through X-RAY, a mode the
viewer enters over the whole model (web/public/js/viewer/xray.js).
"""

import sys
from pathlib import Path

import cadquery as cq

# `chip_color`, for `M_PETG_BLACK` below — the same anchor `_routing` uses to reach it.
_bp = Path(__file__).resolve().parents[1] / "printed-parts" / "enclosure" / "back-panel"
if str(_bp) not in sys.path:
    sys.path.insert(0, str(_bp))
import _back_panel_dimensions as _rear                 # noqa: E402

M_JG_BLACK_PP = cq.Color(0.12, 0.12, 0.14)     # John Guest's black polypropylene PTC range
M_NEOFIT_ACETAL = cq.Color(0.14, 0.14, 0.15)   # neoFit's black acetal bulkhead bodies
M_STAINLESS = cq.Color(0.72, 0.73, 0.76)
M_ALUMINIUM = cq.Color(0.80, 0.81, 0.83)
# The Multiplex 19-0897's hex barrel (`reference/multiplex-asse1022`).
M_BRASS = cq.Color(0.71, 0.56, 0.33)
# The SF76E's tin-plated case, which its listing states as metal.
M_TINNED_STEEL = cq.Color(0.78, 0.79, 0.80)
# The one filament every black print on this machine comes off — the box, the pan, the clamp and
# the cold core — MEASURED rather than named: `_back_panel_dimensions.chip_filaments` holds the
# swatch the flavour chips are cut to.
M_PETG_BLACK = cq.Color(*(c / 255.0 for c in _rear.chip_color("flavor")))
# Platinum-cure silicone at BBDINO's carbon-black pigment, ≤2% by weight (`ledger/bom.md` §8).
M_SILICONE_BLACK = cq.Color(0.08, 0.08, 0.08)

# --- the cold core's own bodies, by what each one is --------------------------
# `cold-core-layout/cold_core_assembly` places these and the generators below cut them, so the
# two read the same constant.
C_PLUG = cq.Color(0.35, 0.40, 0.48)
C_SHROUD = cq.Color(0.30, 0.34, 0.40)
C_REED = cq.Color(0.95, 0.55, 0.85)


def one_body(shape, name, color) -> cq.Assembly:
    """`shape` as a one-body assembly, so `export_assembly` bakes `color` into its STEP.

    `cq.exporters.export` writes geometry and no colour, and a STEP carrying none is drawn at
    `DEFAULT_FRONT` in web/public/js/viewer/step.js. A part whose own picture is a card of its
    own comes through here instead.

    The shape rides the assembly's ROOT rather than a child under it: a child may not take its
    parent's name, and `_cadq_export._per_solid_color` reads a root's own `obj` and `color` —
    splitting to `<name>/1…n` itself where the body is more than one solid."""
    return cq.Assembly(shape, name=name, color=color)
