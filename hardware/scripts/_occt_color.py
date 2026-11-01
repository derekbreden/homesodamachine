"""OCCT's arithmetic on a colour, bit for bit, without OCCT.

`cq.Color` wraps a `Quantity_ColorRGBA`, which keeps a colour as float32 LINEAR RGB and a
float32 alpha. Three sRGB numbers reach it through the sRGB curve in double, rounded to float32
(`Quantity_Color(r, g, b, Quantity_TOC_sRGB)`); a hex colour's bytes through the same curve in
float32, with the C library's `powf` (`Quantity_ColorRGBA::ColorFromHex`). `toTuple` reads sRGB
back off the float32 values through the inverse curve in double, whose multiply and subtract
OCCT's build fuses into one rounding. This module repeats each step, so a colour made while
CadQuery is deferred (`_rust_part.start`) answers as OCCT would, and
`hardware/scripts/test_rust_part.py` holds the two to the same bits.
"""
from __future__ import annotations

import functools
import math
import re
import struct

_HEX = re.compile(r"#([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})")


def rgba(args: tuple, kwargs: dict):
    """The linear RGB and alpha OCCT keeps for `cq.Color(*args, **kwargs)`, or None where only
    OCCT can say: no arguments, a colour's name, or a number outside 0 to 1, which it refuses."""
    if len(args) == 1 and isinstance(args[0], str):
        hexed = _HEX.fullmatch(args[0])
        if hexed is None:
            return None
        # Each byte over 255, then the curve, in float32; the alpha stays the default one.
        return (*(_curve32(_f32(_f32(int(b, 16)) / _f32(255.0))) for b in hexed.groups()), 1.0)
    if len(args) == 3:
        alpha = kwargs.get("a") or 1.0          # `cq.Color` sets an `a=` only when it is truthy
    elif len(args) in (4, 5):
        alpha = args[3]
    else:
        return None
    if not all(0.0 <= c <= 1.0 for c in (*args[:3], alpha)):
        return None
    # The curve in double, kept in float32. A fifth argument, false, says the three are linear.
    srgb_in = len(args) < 5 or args[4]
    return (*(_f32(_curve(c) if srgb_in else c) for c in args[:3]), _f32(alpha))


def srgb(rgb) -> tuple:
    """sRGB off float32 linear RGB, as `Quantity_Color::Values(Quantity_TOC_sRGB)` reads it."""
    return tuple(_inverse(_f32(c)) for c in rgb)


def _f32(x: float) -> float:
    return struct.unpack("f", struct.pack("f", x))[0]


def _curve(c: float) -> float:
    """sRGB to linear, in double (`Quantity_Color::Convert_sRGB_To_LinearRGB`)."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _curve32(v: float) -> float:
    """sRGB to linear, in float32: the same curve's single-precision overload. A float32 sum or
    quotient taken in double and rounded once is the float32 one."""
    if v <= _f32(0.04045):
        return _f32(v / _f32(12.92))
    return _f32(_powf()(_f32(_f32(v + _f32(0.055)) / _f32(1.055)), _f32(2.4)))


def _inverse(v: float) -> float:
    """Linear to sRGB, in double (`Quantity_Color::Convert_LinearRGB_To_sRGB`), its multiply and
    subtract one fused operation."""
    if v <= 0.0031308:
        return v * 12.92
    return math.fma(v ** (1.0 / 2.4), 1.055, -0.055)


@functools.cache
def _powf():
    import ctypes
    powf = ctypes.CDLL(None).powf
    powf.restype, powf.argtypes = ctypes.c_float, (ctypes.c_float, ctypes.c_float)
    return powf
