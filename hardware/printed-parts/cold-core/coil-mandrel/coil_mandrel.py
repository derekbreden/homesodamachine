'\nCoil winding mandrel.\n\nHollow PETG cylinder for hand-winding 1/4" OD copper around the 5"\nround 316L carbonator. [5 mm](WALL) solid PETG wall, with a shallow\nhelical guide groove [1 mm](GROOVE_DEPTH) deep that cradles the copper.\n\nThe undersized groove is a rough-forming aid. Feed material from the long\nends while setting the finished diameter, pitch and turn count on the vessel\nfixture. EVAP-01 and cold-core-layout/_coil.py define the production coil,\nincluding its opposite tangent exits and complete R15 tail forms.\n\nThe Rust cold-core scalar recipe derives the winding dimensions and stub\nallowances. This interface supplies them to the part program and Python readers;\n`coil_mandrel.rs` cuts the STEP, payload and STL on the kernel.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('coil_mandrel', action="public-names")
    try:
        return _member('coil_mandrel', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('coil_mandrel', action="main")
