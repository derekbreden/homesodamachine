"""Clamped wire-spline readings from the shared Rust composer."""
from ._wiring_data import read as _read


def measure(segment):
    return _read("spline_measure", segment)
