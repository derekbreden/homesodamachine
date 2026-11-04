'Finished drilled water-inlet jet cap, on one ANSI A landscape sheet.\n\nThe nominal disc and through passage come from _water_inlet_jet, the same\nparameters used by the installed model. This drawing owns finished-component\ntolerances, centering, face condition and burr limits. The cap-to-elbow joint,\ninstalled port fit and post-weld acceptance belong to assembly/water-inlet-jet.md.\n\nRun with tools/cad-venv/bin/python. No CAD geometry or welding settings change.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('water_inlet_jet_cap_drawing', action="public-names")
    try:
        return _member('water_inlet_jet_cap_drawing', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('water_inlet_jet_cap_drawing', action="main")
