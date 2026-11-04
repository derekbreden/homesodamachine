"The cold core, whole — every body inside the foam and every line among them.\n\n`printed-parts/cold-core/foam-assembly` is the core as the MACHINE sees it: three casing\npieces, the outside faces the enclosure loads and stands its own bodies off. This is the core\nas the BENCH sees it, one frame further in — the carbonator that fills it, the coil wound on that,\nboth reservoirs in their pockets, the fittings made up on every port, and the lines drawn\namong all of them.\n\nFRAME: the foam shell's own. Z up, the shell floor's outer face at z = 0, the shell's open top\nat `foam_shell_outer_height`. ±Y is the carbonator's port axis and −Y the register azimuth.\n`foam_assembly.stack_floor_z` and `.cap_face_z` are the two planes the appliance reads.\n\n    tools/cad-venv/bin/python hardware/cold-core-layout/cold_core_assembly.py\n\nwrites `cold-core-assembly.step` beside this file with its `.scorecard.json`, which the 3D\nviewer's bottom bar reads at `/3d`. THE SAME CARD IS WRITTEN BESIDE `foam-assembly.step`, the\nouter model of this same core: a reader who opens either one is looking at the cold core, and\nthe cold core has one verdict.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('cold_core_assembly', action="public-names")
    try:
        return _member('cold_core_assembly', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('cold_core_assembly', action="main")
