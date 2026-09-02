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
from OCP.Quantity import Quantity_TypeOfColor

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
# The black PETG spool, and what still comes off it: the drip pan, the fuse clamp, the two
# copper-line plugs, the PRV shroud, the reed bridge, and the black rings, collars and
# nameplate stock. MEASURED rather than named — `_y_wall_dimensions.chip_filaments` holds the
# swatch the flavour chips are cut to.
M_PETG_BLACK = cq.Color(*(c / 255.0 for c in _rear.chip_color("flavor")))
# Polymaker Fiberon PET-GF15 black, the stock every surface a customer sees prints in
# (`ledger/bom.md` §7): the four quadrants, the lower pump cradle and its top clamp, the ceiling
# panel, the display cover plate, the faucet shell's two pieces and the above-counter plate.
# The cold core's five foam bodies come off the same stock — the shell and its four caps and
# lids — so the two biggest plates in the build run one spool.
#
# THIS TRIPLE IS NOT MEASURED, and it is the only black here that is not. `M_PETG_BLACK` above
# is a swatch off a named spool; this was reasoned — glass fill standing it a shade over the
# PETG it closes on. No swatch of PET-GF15 has been sampled, and `chip_filaments` is the
# mechanism that would hold one.
#
# WHAT SEPARATES THE TWO STOCKS IS GLOSS, NOT COLOUR, so a better triple would not close the
# gap on its own. `cadlib/flute-evidence/02` has both in one exposure: across the seam, where
# the light grazes, PETG throws a warm specular bloom and PET-GF holds neutral, and PET-GF
# reads 0.59× the PETG beside it; on the fluted panels below, same frame and same light, it
# reads 1.10×. One ratio cannot be both, because what swings is the specular lobe. A material's
# roughness is the channel that carries that, and there is nowhere to put it: a STEP colour is
# RGBA, and `web/public/js/viewer/step.js` gives every body one hardcoded `roughness: 0.6`.
M_PETGF_BLACK = cq.Color(0.20, 0.20, 0.21)
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
# Sintered 304 SS — the FERRODAY sparge stone, which its listing states as 304 throughout. A
# powder-formed surface, so it reads matte where the bar stock it hangs off reads bright.
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
# bridge — and every one of them is black, off one of the two spools `ledger/bom.md` §7 bills.
# What is potted inside them is read through x-ray, which is the viewer's default and ghosts
# the whole model at once; a cap drawn see-through is a cap nobody prints.
#
# THE FIVE FOAM BODIES ARE PET-GF AND THE FOUR SMALL ONES ARE PETG, which is a real difference
# in the hand and a hairline one in the eye: glass fill stands PET-GF a shade above the PETG it
# stacks against. §7 is where a body's stock is stated; these two constants are what that stock
# looks like.
C_PLUG = M_PETG_BLACK
C_FOAM_SHELL = M_PETGF_BLACK
C_CAP_TOP = M_PETGF_BLACK
C_CAP_LID_TOP = M_PETGF_BLACK
C_CAP_BOTTOM = M_PETGF_BLACK
C_CAP_LID_BOTTOM = M_PETGF_BLACK
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
WALL_COLORS = {name: M_PETGF_BLACK
               for name in ("front-bottom", "front-top", "back-bottom", "back-top",
                            "pump-cartridge", "pump-cap")}
# The collet plate — the one piece of this box that is steel, laser-cut from 1/8" 316.
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
# The JHYOSSTHI pogo dock's black moulded pill, either half; its gold pins and pads and the
# flush magnets are that face's own metal and are not drawn apart from it.
C_DOCK = cq.Color(0.09, 0.09, 0.10)
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
# `faucet-layout/faucet_assembly` stands these and the touch-flo generators cut them. The shell's
# two pieces and the above-counter plate come off `M_PETGF_BLACK`, the same spool the box's
# exterior does, so the two stand in one colour across the countertop between them.
C_FAUCET_BLACK = M_PETGF_BLACK
# The Westbrass A2031-NL-62 / R2031-NL-62 donor body inside that shell, which the BOM buys in
# MATTE BLACK (`reference/touch-flo-faucet/README.md`, `faucet-shell/ASSEMBLY.md`) — a
# finished metal, so it stands a shade under the print that wraps it rather than over it.
M_DONOR_BLACK = cq.Color(0.13, 0.13, 0.14)


# --- how each material takes the light -----------------------------------------
#
# A COLOUR IS HALF OF WHAT A MATERIAL LOOKS LIKE, and on this machine it is the quieter half.
# `cadlib/flute-evidence/02` holds both print stocks in ONE exposure: across the seam, where the
# light grazes, PETG throws a warm specular bloom — rgb(173,165,142), not a black at all — while
# PET-GF beside it holds rgb(96,98,98) neutral, 0.59x the PETG. On the fluted panels below, same
# frame and same light, the same PET-GF reads 1.10x the same PETG. ONE RATIO CANNOT BE BOTH. What
# swings between those two readings is the specular lobe and not the pigment, which is why no
# triple read off that frame could have settled it and why the evidence README forbids reading
# one. The channel that carries it is ROUGHNESS.
#
# ROUGHNESS IS A MATERIAL PROPERTY EXACTLY AS COLOUR IS: 0 is a mirror, 1 is fully diffuse, and
# `metalness` says whether the specular takes the surface's own colour (metal) or the light's
# (everything else). A glass-filled print scatters where an unfilled one reflects; a sintered
# stone reads matte where the bar stock it hangs off reads bright; a lacquered coil pack is
# glossy where the moulded body under it is not. Those are the same kind of fact as "the reservoir
# is see-through", and they are stated here for the same reason.
#
# THE FIGURES ARE ESTIMATES, and unlike the colours none of them is a measurement. They are read
# off what each constant's own comment already says the surface is — matte, moulded, plated,
# powder-formed, lacquered, an open weave — and a part whose comment says nothing about its
# surface takes the value its class of thing takes. A gloss meter would replace the lot.
#
# EVERY COLOUR CONSTANT ABOVE MUST APPEAR EXACTLY ONCE BELOW. `_finish_table()` raises if one
# does not, so a material cannot enter this module and silently inherit somebody else's finish —
# which is the failure this whole block exists to end, the viewer having drawn all 44 of them at
# one hardcoded 0.6.
_METAL, _DIELECTRIC = 1.0, 0.0
FINISHES = [
    # the plastics
    (M_JG_BLACK_PP,      0.45, _DIELECTRIC),   # moulded polypropylene
    (M_JG_WHITE_PP,      0.45, _DIELECTRIC),
    (M_JG_GREY_ACETAL,   0.35, _DIELECTRIC),   # acetal is slick in the hand
    (M_NEOFIT_ACETAL,    0.35, _DIELECTRIC),
    (M_PETG_BLACK,       0.45, _DIELECTRIC),   # the flank that blooms bronze in flute-evidence/02
    (M_PETGF_BLACK,      0.85, _DIELECTRIC),   # glass fill scatters; it holds neutral in that frame
    (M_PETG_TRANSLUCENT, 0.40, _DIELECTRIC),   # the black stock's own gloss, on a clear spool
    (M_TPU_BLACK,        0.70, _DIELECTRIC),
    (M_SILICONE_BLACK,   0.60, _DIELECTRIC),
    (M_SILICONE_CLEAR,   0.55, _DIELECTRIC),
    (M_PVC_CLEAR,        0.25, _DIELECTRIC),   # extruded clear tube
    (M_PTFE_WHITE,       0.90, _DIELECTRIC),   # "an opaque sintered white"
    (M_EPOXY_BLACK,      0.45, _DIELECTRIC),   # a moulded TO-92 package
    (M_GLASS,            0.05, _DIELECTRIC),
    (M_NITRILE_BLACK,    0.95, _DIELECTRIC),   # "reads flatter than any print on this machine"
    (M_PET_BRAID,        0.80, _DIELECTRIC),   # "an OPEN weave"
    # the metals, whose specular takes their own colour
    (M_STAINLESS,        0.35, _METAL),
    (M_SINTERED_SS,      0.85, _METAL),        # "powder-formed ... matte where the bar stock reads bright"
    (M_ALUMINIUM,        0.30, _METAL),
    (M_BRASS,            0.30, _METAL),
    (M_TINNED_STEEL,     0.40, _METAL),        # "the SF76E's tin-plated case"
    (M_NICKEL_PLATE,     0.25, _METAL),        # "a plated white metal"
    (M_COPPER,           0.30, _METAL),
    # the box's own steel, and the boards
    (C_STEEL_PLATE,      0.40, _METAL),        # 1/8" 316, laser-cut
    (C_PCBA,             0.50, _DIELECTRIC),   # solder mask
    # the bought-in bodies
    (C_COMP,             0.50, _DIELECTRIC),   # a PAINTED steel can — the paint is what you see
    (C_COND,             0.45, _METAL),        # bare tube and fin stack
    (C_SEAFLO,           0.50, _DIELECTRIC),
    (C_DISPLAY,          0.50, _DIELECTRIC),   # solder mask
    (C_DISPLAY_GLASS,    0.08, _DIELECTRIC),   # "the cover glass over the panel"
    (C_PSU,              0.45, _METAL),
    (C_RELAY,            0.50, _DIELECTRIC),   # "the relay board's green solder mask"
    (C_AC_HUB,           0.50, _DIELECTRIC),   # "Wago's orange levers"
    (C_GND,              0.50, _DIELECTRIC),
    (C_PLATE,            0.40, 0.9),           # bare interdigitated copper on a board: mostly metal
    (C_MQ6,              0.50, _DIELECTRIC),   # "the module's own blue board"
    (C_C14,              0.45, _DIELECTRIC),
    (C_DIGITEN,          0.50, _DIELECTRIC),
    (C_DOCK,             0.45, _DIELECTRIC),   # "the dock's black moulded pill"
    (C_VALVE,            0.50, _DIELECTRIC),   # "the Beduan solenoid's moulded white body"
    (C_COIL,             0.30, _DIELECTRIC),   # "the LACQUERED coil pack", and lacquer is glossy
    (C_PUMP_HEAD,        0.45, _DIELECTRIC),   # "a black moulded head"
    (C_PUMP_BOSS,        0.45, _DIELECTRIC),   # "a WHITE moulded rotor housing"
    (C_PUMP_MOTOR,       0.40, _METAL),        # "a bare steel motor can"
    (M_DONOR_BLACK,      0.70, _DIELECTRIC),   # matte black on a finished metal: the coating is what shows
    # THE WAYFINDING PALETTE, which is stock and not decoration. `_y_wall_dimensions` holds the
    # four spools a bulkhead ring and its tube collar are cut from and the two a word is
    # lettered in, and every one of them is Bambu PETG Basic — the black among them IS
    # `M_PETG_BLACK` above, which is why it is not repeated here. `enclosure_assembly` paints
    # these bodies straight off `chip_color`/`word_color` rather than off a constant in this
    # module, so without these rows the rings, the collars and the nameplate's lettering are
    # the one part of the machine with no finish to find.
    # WALKED, NOT LISTED, so a sixth chip or a third lettering colour cannot arrive without one.
    *[(cq.Color(*(c / 255.0 for c in rgb)), 0.45, _DIELECTRIC)
      for rgb in dict.fromkeys([_rear.chip_color(f) for f in _rear.chip_filaments]
                               + [_rear.word_color(f) for f in _rear.chip_word_colors])],
]


def linear(color) -> tuple:
    """The exact three doubles a `.step.mesh` carries for this colour.

    A COLOUR IS WRITTEN TWICE IN TWO SPACES. The STEP takes it in sRGB — `COLOUR_RGB` holds
    0.2 for a 0.2 constant — and `_mesh_payload._mesh` takes it in LINEAR, off this same call,
    where 0.2 is 0.0331. The viewer meets the linear one, so the linear one is what a finish
    has to be found by. Reading it here through OCCT rather than converting by hand is what
    makes the two bit-identical instead of merely close."""
    return tuple(color.wrapped.GetRGB().Values(Quantity_TypeOfColor.Quantity_TOC_RGB))


def finish_rows() -> list:
    """`[{"rgb": [linear r, g, b], "roughness": f, "metalness": f}]`, one per material here.

    NO KEY AND NO ROUNDING, for two reasons that both bite in the dark. A LINEAR palette is
    crowded at the black end — `M_EPOXY_BLACK` and `M_NITRILE_BLACK` are 0.0100 and 0.0116,
    which is one unit apart at 0-255 and would collapse to one material — so a quantized key
    cannot carry this palette at all. And where a key lands on a rounding boundary the two ends
    disagree by construction: Python's `round` is half-to-even and JavaScript's `Math.round` is
    half-up, over a 0.1-spaced palette that produces such values readily. Handing over the
    doubles themselves and letting the reader match on DISTANCE has no boundary to sit on: the
    payload route hits at distance 0, and the occt-parse fallback, whose arithmetic is its own,
    snaps to the nearest.

    Raises rather than returning a table with a hole in it — see the two guards below."""
    rows, seen = [], {}
    for color, rough, metal in FINISHES:
        # A WHITE IS TWO COLOURS BY THE TIME IT IS DRAWN. `step_safe` holds anything at or over
        # `_WHITEST` down a part in 255 so OCCT writes a `COLOUR_RGB` for it at all, and the
        # generators that cut a body's own STEP go through it — while the assemblies that place
        # that body paint it off the raw constant. Both reach a renderer, so both are named.
        for rgb in dict.fromkeys((linear(color), linear(step_safe(color)))):
            # ONE ROW PER COLOUR. A stock can be named twice over — the flavour chip's filament
            # IS `M_PETG_BLACK`, and a white reached through `step_safe` is the white it was —
            # and naming it twice is agreement, not conflict. It is a second ROW at one colour
            # that would be the defect, because a reader matching on distance would find both.
            if rgb in seen:
                seen[rgb].add((rough, metal))
                continue
            seen[rgb] = {(rough, metal)}
            rows.append({"rgb": list(rgb), "roughness": rough, "metalness": metal})
    for rgb, got in seen.items():
        if len(got) > 1:
            raise ValueError(
                f"_materials: linear {rgb} is given {len(got)} finishes {sorted(got)}. Two "
                f"substances at one colour cannot both be drawn — give one of them its own.")
    named = {n: v for n, v in globals().items()
             if isinstance(v, cq.Color) and (n.startswith("M_") or n.startswith("C_"))}
    missing = sorted(n for n, v in named.items() if linear(v) not in seen)
    if missing:
        raise ValueError(
            f"_materials: {', '.join(missing)} name a colour with no finish. Add each to "
            f"FINISHES — a material cannot be drawn without saying how it takes the light.")
    return rows


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
