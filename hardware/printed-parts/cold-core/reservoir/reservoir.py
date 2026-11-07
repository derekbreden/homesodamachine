'Reservoir — open-top `[`-shaped PETG cup that stands on the floor of each\nbag pocket of the foam shell, closed by a separately-printed cap clamped\nthrough a TPU gasket. Mirrored ±X. Carries the level-sensing rod, and its\ncap carries flush TPU tube grips and a separate bidirectional air tube.\n\nSame coordinate convention as ../foam-shell/: +Z vertical, +X is\nthe bag-pocket axis (two cavities sit on opposite sides), +Y is\nperpendicular to it.'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('reservoir', action="public-names")
    try:
        return _member('reservoir', name)
    except ValueError as error:
        raise AttributeError(name) from error
