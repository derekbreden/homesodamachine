"""Project-neutral material appearances and the one-body STEP wrapper.

This is the bottom of the material import graph.  A generator for an independent
tool or cut part may import these stable stock appearances without inheriting an
appliance assembly, an enclosure dimension, or the complete finish catalogue.
Keep project geometry and measured, product-specific palettes out of this file.
"""

import cadquery as cq


# Polymaker Fiberon PET-GF15 black, the stock every surface a customer sees
# prints in (`ledger/bom.md` §7).  This triple is reasoned rather than measured:
# glass fill stands a shade over the PETG it closes on.  STEP carries colour but
# not the roughness which most visibly separates the two stocks.
M_PETGF_BLACK = cq.Color(0.20, 0.20, 0.21)

# Bambu TPU 90A black, the one spool every soft seal on this machine prints off
# (`ledger/bom.md` §8).
M_TPU_BLACK = cq.Color(0.15, 0.15, 0.15)

# Stock metal appearances used across projects.  The copper triple is the same
# one `_routing.SPOOLS["copper"]` states in 0–255 units for the GOORY ACR coil
# and its two tails.
M_STAINLESS = cq.Color(0.72, 0.73, 0.76)
M_ALUMINIUM = cq.Color(0.80, 0.81, 0.83)
M_COPPER = cq.Color(184 / 255.0, 115 / 255.0, 51 / 255.0)


#: The lightest a colour can be and still reach a STEP. OCCT treats pure white
#: as the default and writes no `COLOUR_RGB` for it, so a requested white body
#: otherwise arrives carrying no colour at all.
_WHITEST = 254.0 / 255.0


def step_safe(color) -> cq.Color:
    """`color`, held below the pure white that OCCT does not write to STEP."""
    r, g, b, a = color.toTuple()
    if min(r, g, b) >= _WHITEST:
        return cq.Color(_WHITEST, _WHITEST, _WHITEST, a)
    return color


def one_body(shape, name, color) -> cq.Assembly:
    """`shape` as a one-body assembly with `color` baked into its STEP.

    The shape rides the assembly root so `_cadq_export._per_solid_color` can
    preserve its name and colour, including when the shape contains more than
    one solid.
    """
    return cq.Assembly(shape, name=name, color=step_safe(color))
