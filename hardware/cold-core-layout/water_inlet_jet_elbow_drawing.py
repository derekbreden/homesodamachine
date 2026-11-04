'Water-inlet jet elbow assembly: purchased fitting plus welded drilled cap.\n\nThe exterior envelope and local tip section use the same parametric reference\nfitting as the cold core. It is a layout stand-in, not measured vendor detail. The drawing\nidentifies the purchased item and controls assembly alignment and acceptance;\ncap dimensions belong to JET-CAP-01. Grey bands show the required fusion path,\nnot a predicted or dimensioned weld profile. Measured fit and weld qualification\nremain explicit release items under assembly/water-inlet-jet.md.\n\nRun with tools/cad-venv/bin/python. No machine geometry or weld recipe changes.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('water_inlet_jet_elbow_drawing', action="public-names")
    try:
        return _member('water_inlet_jet_elbow_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('water_inlet_jet_elbow_drawing', action="main")
