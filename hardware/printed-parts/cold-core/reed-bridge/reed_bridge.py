"Carbonator reed bridge — printed PETG interposer holding the two\nexternal level reeds against the carbonator wall on the register azimuth,\nstanding the evaporator coil off the glass where a wrap crosses it.\n\nThe RC62 is an axially-magnetised neodymium ring: radially outside it, on\nits mid-plane, the field is purely axial, so both reeds stand with their\nglass vertical. reed_glass_length of vertical glass spans one wrap or two\nat the wind's inter_wrap_clear.\n\nThe plateau stands pocket_depth off the steel; each reed lies in a pocket\ncut clear through to the wall, so its glass rests on bare 316L. Ramps on\nall four sides are what each wrap rides over as the coil is dragged down\nthe carbonator. Copper hoop tension clamps the bridge to the wall; the foam\npour sets it.\n\nThe setting gauge hangs on the tube's bottom rim and its top face is\nbridge_z_bottom.\n\nFrame: +Z is the carbonator axis, Z=0 at the tube's bottom rim — the face\nthat seats on the carbonator support ring. +X is the register azimuth, the line\nthe wall-preloaded donut rides. The part is symmetric about the XZ plane\napart from the lead groove.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('reed_bridge', action="public-names")
    try:
        return _member('reed_bridge', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('reed_bridge', action="main")
