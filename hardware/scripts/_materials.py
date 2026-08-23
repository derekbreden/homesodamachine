"""What each material on this machine looks like with the lights on.

A body is coloured by what it is MADE OF, and every part of one material takes one constant here.
Both ends read these: the assembly that places a body, and the generator that cuts the body's own
STEP — so the same part is the same colour in the picture of the machine and in the picture of
itself.

EVERY PICTURE IN THIS REPO IS A PICTURE OF THE THING, not a diagram of it. A colour here is what
the part is, and nothing else may set one: not telling a piece from its neighbour, not seeing
through a wall, not holding a contrast ratio against the viewer's ground. Those are the viewer's
jobs and it has them — x-ray ghosts the whole model and draws every solid's feature edges
(web/public/js/viewer/xray.js), the component picker highlights the one you point at, and the
scorecard's rows select a body by name. A colour spent on any of that is a colour that lies
about the material, and the lie survives into every render the tree ships.

TRANSLUCENCY IS A MATERIAL PROPERTY TOO. The alpha on a constant here is carried because the
stock is see-through — the reservoirs' PETG Translucent Clear, the sparge stub's silicone, the
vent telltale's clear PVC, the reed's glass ampoule — and for no other reason.

A COLOUR IS THREE COMPONENTS by the time it is drawn: `_mesh_payload` hands over the RGB a STEP
carries and occt-import-js reads back the same three.
"""

import sys
from pathlib import Path

import cadquery as cq

# `chip_color`, for `M_PETG_BLACK` below — the same anchor `_routing` uses to reach it.
_yw = Path(__file__).resolve().parents[1] / "printed-parts" / "enclosure" / "y-wall-of-back-top"
if str(_yw) not in sys.path:
    sys.path.insert(0, str(_yw))
import _y_wall_dimensions as _rear                     # noqa: E402

# --- the plastics ------------------------------------------------------------
M_JG_BLACK_PP = cq.Color(0.12, 0.12, 0.14)     # John Guest's black polypropylene PTC range
# The white range beside it. A John Guest part number ending W IS the white one, and three of
# them are on this machine: the PP0408W union, the PP061208W reducer stem and the PP451223W
# female adapter (`reference/jg-*`). The Basics MTB-0606WP barb tee is the same white PP.
M_JG_WHITE_PP = cq.Color(0.90, 0.90, 0.87)
# The grey acetal the potable PTC bodies are moulded in — McMaster 51055K3's bulkhead union and
# the PI4512F6S flare swivel inside `reference/flare38-14ptc`.
M_JG_GREY_ACETAL = cq.Color(0.55, 0.56, 0.57)
M_NEOFIT_ACETAL = cq.Color(0.14, 0.14, 0.15)   # neoFit's black acetal bulkhead bodies
# The one filament every black print on this machine comes off — the box, the pan, the clamp,
# the cold core's five foam bodies and the plugs and shroud among them — MEASURED rather than
# named: `_y_wall_dimensions.chip_filaments` holds the swatch the flavour chips are cut to.
M_PETG_BLACK = cq.Color(*(c / 255.0 for c in _rear.chip_color("flavor")))
# Bambu PETG Translucent Clear, the stock the four syrup-wetted reservoir parts print in
# (`ledger/bom.md` §7) — SO THE CUSTOMER READS FILL STATE THROUGH THE WALL, which is the whole
# reason a clear spool is bought. Neutral rather than blue: PETG's own clear pulls faintly warm.
M_PETG_TRANSLUCENT = cq.Color(0.88, 0.88, 0.85, 0.35)
# Bambu TPU 90A black, the one spool every soft seal on this machine prints off (`ledger/bom.md`
# §8) — the display ring, the above-counter gasket and the faucet's o-ring.
M_TPU_BLACK = cq.Color(0.15, 0.15, 0.15)
# Platinum-cure silicone at BBDINO's carbon-black pigment, ≤2% by weight (`ledger/bom.md` §8).
M_SILICONE_BLACK = cq.Color(0.08, 0.08, 0.08)
# Unpigmented food-grade silicone, which is milky rather than clear — the sparge stub inside the
# vessel and the uxcell flat washer under each reservoir bulkhead (`ledger/bom.md` §2, §8).
M_SILICONE_CLEAR = cq.Color(0.92, 0.92, 0.90, 0.60)
# Sealproof clear PVC, the vent telltale stub over the ASSE 1022's barb.
M_PVC_CLEAR = cq.Color(0.85, 0.90, 0.92, 0.45)
# LVDALAB's PTFE membrane, in each reservoir cap's vent pocket — an opaque sintered white.
M_PTFE_WHITE = cq.Color(0.93, 0.93, 0.92)
# A moulded epoxy package, which is the black both 1-wire probes arrive in: the TO-92 body of
# the DS18B20 carbonator probe and the DS18S20 coil probe (`ledger/bom.md` §5).
M_EPOXY_BLACK = cq.Color(0.10, 0.10, 0.10)
# The Gebildet reed's 14 mm glass ampoule (`ledger/bom.md` §12) — soda-lime, and see-through
# because a reed switch is see-through.
M_GLASS = cq.Color(0.86, 0.90, 0.88, 0.35)
# CARGEN closed-cell nitrile pipe insulation, the sleeve over the carbonated-water riser
# (`ledger/bom.md` §11) — a rubber black, which reads flatter than any print on this machine.
M_NITRILE_BLACK = cq.Color(0.11, 0.11, 0.11)
# Alex Tech's black PET expandable braid over the harnesses and the umbilical (`ledger/bom.md`
# §11). An OPEN weave, so what it covers is meant to read through it.
M_PET_BRAID = cq.Color(0.10, 0.10, 0.11, 0.55)

# --- the metals --------------------------------------------------------------
M_STAINLESS = cq.Color(0.72, 0.73, 0.76)
# Sintered 316 SS — the FERRODAY sparge stone. The same alloy as the barb it hangs off, and a
# powder-formed surface, so it reads matte where the bar stock reads bright.
M_SINTERED_SS = cq.Color(0.58, 0.59, 0.61)
M_ALUMINIUM = cq.Color(0.80, 0.81, 0.83)
# The Multiplex 19-0897's hex barrel (`reference/multiplex-asse1022`).
M_BRASS = cq.Color(0.71, 0.56, 0.33)
# The SF76E's tin-plated case, which its listing states as metal.
M_TINNED_STEEL = cq.Color(0.78, 0.79, 0.80)
# The GASHER check valve's nickel-plated copper body — a plated white metal, warmer than steel
# and a shade down from it.
M_NICKEL_PLATE = cq.Color(0.76, 0.75, 0.71)
# The GOORY ACR coil and its two tails. THE SAME VALUE THE REFRIGERANT RUNS ARE DRAWN IN —
# `_routing.SPOOLS["copper"]` states this triple in 0–255, and a coil and the tube brazed to it
# are one stock. It is restated here rather than imported because THIS MODULE IS AT THE BOTTOM
# OF THE IMPORT GRAPH: every generator in the tree reads it, and `_routing` reads figures no
# reference part declares, so an edge from here to there is an edge from everything to there.
# The triple is written in the spool's own 0–255 units so the two read as the one value.
M_COPPER = cq.Color(184 / 255.0, 115 / 255.0, 51 / 255.0)

# --- the cold core's own bodies, by what each one is --------------------------
# `cold-core-layout/cold_core_assembly` places these and the generators below cut them, so the
# two read the same constant.
#
# THE STACK IS OPAQUE BECAUSE THE STACK IS OPAQUE. Nine printed bodies close this box — the
# shell, the four foam caps and lids, the two copper-line plugs, the PRV shroud and the reed
# bridge — and every one of them comes off the black spool `ledger/bom.md` §7 bills. What is
# potted inside them is read through x-ray, which is the viewer's default and ghosts the whole
# model at once; a cap drawn see-through is a cap nobody prints.
C_PLUG = M_PETG_BLACK
C_FOAM_SHELL = M_PETG_BLACK
C_CAP_TOP = M_PETG_BLACK
C_CAP_LID_TOP = M_PETG_BLACK
C_CAP_BOTTOM = M_PETG_BLACK
C_CAP_LID_BOTTOM = M_PETG_BLACK
C_SHROUD = M_PETG_BLACK
# The two syrup vessels and their caps, in the ONE stock on this machine that is bought clear —
# `ledger/bom.md` §7, "so the customer reads fill state through the wall".
C_RESERVOIR = M_PETG_TRANSLUCENT
C_RES_CAP = M_PETG_TRANSLUCENT
C_SILICONE = M_SILICONE_CLEAR
# The Gebildet reed bodies standing against the vessel and in each reservoir's channel.
C_REED = M_GLASS

# --- the enclosure's own bodies -----------------------------------------------
# THE BOX'S PIECES ARE ONE COLOUR BECAUSE THEY ARE ONE FILAMENT. `printed-parts/enclosure/
# enclosure` cuts them and `enclosure_assembly` stands them, off this dict — whose keys are also
# the roll of the pieces the box has, which is what `enclosure.build_pieces` walks. Shading one
# piece off its neighbour would draw a box nobody prints, and against the box's own intent:
# `enclosure.flute-hides-seam` strikes the flute field so the Y seam falls in a groove's own
# shadow. WHAT TELLS A PIECE FROM ITS NEIGHBOUR IN THE VIEWER is x-ray's feature edges and the
# component picker, neither of which needs the paint to lie.
WALL_COLORS = {name: M_PETG_BLACK
               for name in ("front-bottom", "front-top", "back-bottom", "back-top",
                            "pump-cartridge", "pump-cap")}
# The collet plate — the one piece of this box that is steel, waterjet from 1/8" 304.
C_STEEL_PLATE = cq.Color(0.72, 0.73, 0.75)
C_PCBA = cq.Color(0.11, 0.11, 0.12)

# --- the bought-in bodies, by what each one is --------------------------------
# `enclosure_assembly` stands these and each reference generator cuts its own STEP, off these.
C_COMP = cq.Color(0.18, 0.18, 0.19)          # a hermetic compressor's painted-steel can
C_COND = cq.Color(0.76, 0.77, 0.78)
C_SEAFLO = cq.Color(0.89, 0.35, 0.13)        # the pump's orange housing
# The Waveshare ESP32-S3-Touch-LCD-4.3B, whose two faces are two materials: the module's own
# solder mask, SAMPLED off the vendor's board photo (waveshare.com, `esp32-s3-touch-lcd-4.3b-3`)
# rather than named, and the cover glass over the panel the customer looks at.
C_DISPLAY = cq.Color(0.094, 0.306, 0.525)
C_DISPLAY_GLASS = cq.Color(0.12, 0.13, 0.16)
C_PSU = cq.Color(0.20, 0.20, 0.24)
C_RELAY = cq.Color(0.16, 0.42, 0.22)         # the relay board's green solder mask
C_AC_HUB = cq.Color(0.90, 0.55, 0.20)        # Wago's orange levers
C_GND = cq.Color(0.75, 0.13, 0.13)
C_PLATE = cq.Color(0.63, 0.42, 0.24)
C_MQ6 = cq.Color(0.25, 0.40, 0.70)           # the module's own blue board, under a steel can
C_C14 = cq.Color(0.18, 0.18, 0.20)
C_DIGITEN = cq.Color(0.92, 0.92, 0.94)
# The Beduan solenoid's moulded white body — the eleven valves' one shared shell — and the
# lacquered coil pack stacked on top of it, which is its own body and its own material.
C_VALVE = cq.Color(0.93, 0.93, 0.91)
C_COIL = cq.Color(0.20, 0.20, 0.23)
# The Kamoer KPHM400's three, READ OFF THE PUMP ON THE BENCH rather than named — the photo set
# at `off-the-shelf-parts/kamoer-kphm400/raw-images/` is what says which is which: a black
# moulded head, a WHITE moulded rotor housing under it (the bracket the mounting holes go
# through), and a bare steel motor can behind that.
C_PUMP_HEAD = cq.Color(0.16, 0.16, 0.18)
C_PUMP_BOSS = cq.Color(0.90, 0.90, 0.88)
C_PUMP_MOTOR = cq.Color(0.74, 0.76, 0.80)

# --- the faucet's own bodies ---------------------------------------------------
# `faucet-layout/faucet_assembly` stands these and the touch-flo generators cut them.
# Polymaker Fiberon PET-CF17, the faucet's own stock (`ledger/bom.md` §7) — the faucet shell's
# three pieces and the above-counter plate. Carbon fill takes the gloss off, so it stands a shade lighter than
# the PETG black the box is printed in and reads matte beside the donor's matte-black metal.
C_PETCF_BLACK = cq.Color(0.19, 0.19, 0.20)
# The Westbrass A2031-NL-62 / R2031-NL-62 donor body inside that shell, which the BOM buys in
# MATTE BLACK (`reference/touch-flo-faucet/README.md`, `faucet-shell/ASSEMBLY.md`) — a
# finished metal, so it stands a shade under the print that wraps it rather than over it.
M_DONOR_BLACK = cq.Color(0.13, 0.13, 0.14)


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
