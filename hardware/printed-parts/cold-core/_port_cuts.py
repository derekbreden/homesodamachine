"Openings through the foam shell — the PRV vent's port through the +Y flank and the front\nwall's two copper feed-throughs — and the two lines that cross the carbonator support ring.\n\nEVERY FLUID LINE LEAVES BY THE TOP, and no line crosses a bag pocket's wall: both reservoirs\nare filled and drawn through their own caps. The two lines that run under the carbonator —\nthe CO2 in and the carbonated water out — cross the support ring at its own slots, on the\ncolumns `co2_lane_x` and `water_outlet_climb_x`, and the assertions here are what hold each\ncrossing inside one slot.\n\nOnly the two copper feed-throughs open on the shell's −X FACE. The two reed cables take the\nreed channels' own cavities, open to the cap (`_reed_channels`), and they are the whole\nof what crosses that wall besides the copper: it is mated face to face with the refrigeration\nbase, and the copper meets that base's own entries.\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('_port_cuts', action="public-names")
    try:
        return _member('_port_cuts', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_port_cuts', action="main")
