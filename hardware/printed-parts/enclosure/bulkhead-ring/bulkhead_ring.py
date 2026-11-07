"""Rear-port identification figures: the word each of the +Y wall of back-top's six stations
carries, the lettering those words are set in, and the label envelope the wall's port pockets
are read from.

Nothing here builds a part. `rear_identification` cuts the six installed tiles and `tube_collar`
the collars that name the same lines, and both take each station's word, the key its two filaments
are read under and the lettering from here, so a word changed for a port is changed on the wall
and on the tube by one edit.

    STATIONS, FLUIDS    each station's word, and the key shared-data's `color.chips` names its
                        chip and word filaments under
    WORD_*              the face, em, recess depth, raise and measured widths of the lettering
    RING_W, THICK, RISE, od, bottom, rise
                        the label envelope `enclosure_assembly` reads for the wall's port
                        pockets, the bosses behind them and the clamp stack
    split               a two-colour label STEP back apart, as `(tile, word)`

Coordinate frame — THE FITTING'S:
  Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
  Origin = the label's INBOARD face, the one that lands on the wall. A label spans y = 0 to its
      own thickness, and its word fills a recess in the outboard face and stands proud of it.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT and a word reads along −X.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'bulkhead_ring'

def __getattr__(name):
    if name == "__all__":
        return _compiled('bulkhead_ring', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('bulkhead_ring', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('bulkhead_ring', action="main")
