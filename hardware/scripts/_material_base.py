"""Project-neutral material appearances and the one-body STEP wrapper.

This is the bottom of the material import graph.  A generator for an independent
tool or cut part may import these stable stock appearances without inheriting an
appliance assembly, an enclosure dimension, or the complete finish catalogue.
Keep project geometry and measured, product-specific palettes out of this file.
"""
from __future__ import annotations

# Polymaker Fiberon PET-GF15 black, the stock every surface a customer sees
# prints in (`ledger/bom.md` §7). This is the shared sRGB appearance in the
# install guide's source artwork (`install-guide/assets/fill-scene-inputs.json`).
# STEP carries color; the finish catalog carries roughness.
_STOCK_RGB = {
    "M_PETGF_BLACK": (0.20, 0.20, 0.21),

    # Bambu TPU 90A black, the one spool every soft seal on this machine prints off
    # (`ledger/bom.md` §8).
    "M_TPU_BLACK": (0.15, 0.15, 0.15),

    # Stock metal appearances used across projects.  The copper triple is the same
    # one `_routing.SPOOLS["copper"]` states in 0–255 units for the GOORY ACR coil
    # and its two tails.
    "M_STAINLESS": (0.72, 0.73, 0.76),
    "M_ALUMINIUM": (0.80, 0.81, 0.83),
    "M_COPPER": (184 / 255.0, 115 / 255.0, 51 / 255.0),
    # Zinc-plated and baked carbon/music wire.  The Lee carrier spring is the first consumer, but
    # the appearance is stock-finish neutral and belongs below the appliance palette.
    "M_ZINC_PLATED_STEEL": (0.73, 0.75, 0.76),
}

__all__ = ["annotations", "cq", *_STOCK_RGB, "step_safe", "one_body", "stock_srgb"]


def __getattr__(name):
    if name == "cq":
        import cadquery
        globals()[name] = cadquery
        return cadquery
    if name in _STOCK_RGB:
        import cadquery as cq
        color = cq.Color(*_STOCK_RGB[name])
        globals()[name] = color
        return color
    raise AttributeError(name)


def __dir__():
    return sorted(set(globals()) | set(_STOCK_RGB) | {"cq"})


def stock_srgb(name):
    """A stock's sRGB triple, exactly as its native colour's ``toTuple`` reads it."""
    from _occt_color import rgba, srgb
    return srgb(rgba(_STOCK_RGB[name], {})[:3])


#: The lightest a colour can be and still reach a STEP. OCCT treats pure white
#: as the default and writes no `COLOUR_RGB` for it, so a requested white body
#: otherwise arrives carrying no colour at all.
_WHITEST = 254.0 / 255.0


def step_safe(color) -> cq.Color:
    """`color`, held below the pure white that OCCT does not write to STEP."""
    import cadquery as cq
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
    import cadquery as cq
    return cq.Assembly(shape, name=name, color=step_safe(color))
