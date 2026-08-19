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
# Translucent, so the vessel and the lines standing inside the stack read through the cap that
# closes them and the shell that holds them.
C_FOAM_SHELL = cq.Color(0.62, 0.78, 0.95, 0.25)
C_CAP_TOP = cq.Color(0.90, 0.66, 0.32, 0.55)          # amber
C_CAP_LID_TOP = cq.Color(0.97, 0.85, 0.55, 0.55)      # pale amber
C_CAP_BOTTOM = cq.Color(0.45, 0.70, 0.45, 0.55)       # green
C_CAP_LID_BOTTOM = cq.Color(0.66, 0.86, 0.62, 0.55)   # pale green
C_RESERVOIR = cq.Color(0.85, 0.88, 0.92, 0.35)
C_RES_CAP = cq.Color(0.70, 0.74, 0.80, 0.55)
# The platinum-cure silicone the gaskets and the dry seal are cast in.
C_SILICONE = cq.Color(0.92, 0.92, 0.90, 0.60)
C_SHROUD = cq.Color(0.30, 0.34, 0.40)

# --- the enclosure's own bodies -----------------------------------------------
# The four printed walls, in the one black filament, a shade apart so a seam between two of
# them reads. `printed-parts/enclosure/enclosure` cuts them and `enclosure_assembly` stands
# them, off these.
WALL_COLORS = {"front-bottom": cq.Color(0.15, 0.15, 0.16),
               "front-top": cq.Color(0.19, 0.19, 0.21),
               "back-bottom": cq.Color(0.13, 0.13, 0.14),
               "back-top": cq.Color(0.17, 0.17, 0.18),
               "pump-cartridge": cq.Color(0.22, 0.21, 0.24)}
# The collet plate — the one piece of this box that is steel, waterjet from 1/8" 304.
C_STEEL_PLATE = cq.Color(0.72, 0.73, 0.75)
C_COVER = cq.Color(0.14, 0.14, 0.15)
C_DGASKET = cq.Color(0.24, 0.22, 0.26)
C_PCBA = cq.Color(0.11, 0.11, 0.12)

# --- the bought-in bodies, by what each one is --------------------------------
# `enclosure_assembly` stands these and each reference generator cuts its own STEP, off these.
C_COMP = cq.Color(0.18, 0.18, 0.19)          # a hermetic compressor's painted-steel can
C_COND = cq.Color(0.76, 0.77, 0.78)
C_SEAFLO = cq.Color(0.89, 0.35, 0.13)        # the pump's orange housing
C_PP0408W = cq.Color(0.93, 0.93, 0.90)       # John Guest's white acetal stem elbow
C_DISPLAY = cq.Color(0.16, 0.17, 0.20)
C_PSU = cq.Color(0.20, 0.20, 0.24)
C_RELAY = cq.Color(0.16, 0.42, 0.22)         # the relay board's green solder mask
C_AC_HUB = cq.Color(0.90, 0.55, 0.20)        # Wago's orange levers
C_GND = cq.Color(0.75, 0.13, 0.13)
C_PLATE = cq.Color(0.63, 0.42, 0.24)
C_MQ6 = cq.Color(0.25, 0.40, 0.70)           # the module's own blue board, under a steel can
C_C14 = cq.Color(0.18, 0.18, 0.20)
C_DIGITEN = cq.Color(0.92, 0.92, 0.94)

# --- the faucet's own bodies ---------------------------------------------------
# `faucet-layout/faucet_assembly` stands these and the touch-flo generators cut them.
# Polymaker Fiberon PET-CF17, the faucet stack's own stock (`ledger/bom.md` §7) — the shell's three
# pieces and the mounting plate. Carbon fill takes the gloss off, so it stands a shade lighter than
# the PETG black the box is printed in and reads matte beside the donor's matte-black metal.
C_PETCF_BLACK = cq.Color(0.19, 0.19, 0.20)
C_TPU_BLACK = cq.Color(0.15, 0.15, 0.15)     # TPU 90A black, the gasket and the o-ring
C_VALVE = cq.Color(0.93, 0.93, 0.91)         # the touch-flo valve body's own white acetal
C_REED = cq.Color(0.95, 0.55, 0.85)


#: The lightest a colour can be and still reach a STEP. OCCT treats pure white as the default
#: and writes no `COLOUR_RGB` for it, so a body asked to be white arrives carrying no colour at
#: all and `web/public/js/viewer/step.js` draws it at `DEFAULT_FRONT` — a blue-grey. One part in
#: 255 under white is the nearest thing that survives the round trip.
_WHITEST = 254.0 / 255.0


def step_safe(color) -> cq.Color:
    """`color`, held below the white a STEP cannot carry.

    Every white on this machine is a wayfinding white — the water chip, its word — so the one
    that comes back has to be white to a reader and not the viewer's default."""
    r, g, b, a = color.toTuple()
    if min(r, g, b) >= _WHITEST:
        return cq.Color(_WHITEST, _WHITEST, _WHITEST, a)
    return color


def one_body(shape, name, color) -> cq.Assembly:
    """`shape` as a one-body assembly, so `export_assembly` bakes `color` into its STEP.

    `cq.exporters.export` writes geometry and no colour, and a STEP carrying none is drawn at
    `DEFAULT_FRONT` in web/public/js/viewer/step.js. A part whose own picture is a card of its
    own comes through here instead.

    The shape rides the assembly's ROOT rather than a child under it: a child may not take its
    parent's name, and `_cadq_export._per_solid_color` reads a root's own `obj` and `color` —
    splitting to `<name>/1…n` itself where the body is more than one solid."""
    return cq.Assembly(shape, name=name, color=step_safe(color))
