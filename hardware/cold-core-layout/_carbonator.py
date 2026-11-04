'The carbonator, in the foam shell\'s own frame.\n\nA 5" OD × 0.065" wall 316 tube with a 1/4"-thick circular plate recessed into each end and\nfillet-welded there, the 1/8" 316L float rod welded between the plates\' blind registers, a\nTAISHER street elbow made up on each of the top plate\'s two tapped 1/4" NPT ports, and a neoFit\nAME4-N2-E push-fit male elbow on each of the bottom plate\'s two.\n\n  Z         the shell\'s own. The tube\'s bottom sits one floor slab and one support ring up\n            (`carbonator_bottom_z`); every figure below is struck off that.\n  ±Y        the port axis. All four ports stand `carbonator_port_offset` off the carbonator\'s axis\n            on it, two under the carbonator and two over it.\n  −Y        the register azimuth — the rod, and the reed bridge on the outside of the wall.\n\nEach plate is set one plate thickness in from its tube end, and that recess is where the\nclosure fillet is laid (`assembly/pressure-vessel.md`). So the interior runs\n`interior_floor_z` to `interior_ceiling_z` in the tube\'s own frame and the carbonator\'s outside is\nthe tube, end to end.\n\nTHE ELBOWS ARE PLACED BY THE STOREYS, NOT BY THEIR OWN REACH. `front_face_port_z` and\n`top_band_z` are where the shell\'s lines cross those bands, and an elbow\'s corner is what has\nto arrive there. `BOTTOM_AXIS_OFFSET` and `ELBOW_AXIS_OFFSET` are those standoffs struck off\nthe shell, and `report` holds each against the same distance read off its catalog part.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_carbonator', action="public-names")
    try:
        return _member('_carbonator', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_carbonator', action="main")
