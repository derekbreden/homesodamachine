'Three-piece cold-core casing in its native assembly frame.\n\nThe fixed shell floor is Z0. The bottom cap stands on Z−20 and the uniform top\nlid presents its equipment face at Z233.4. The taller shell rim seats the lid\nwith its dry-face allowance. Vessel, reservoir, coil and port datums are fixed\nindependently of the casing rim. The separate B-fill bend holder belongs to the\npopulated cold-core assembly, not this casing-only assembly.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('foam_assembly', action="public-names")
    try:
        return _member('foam_assembly', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('foam_assembly', action="main")
