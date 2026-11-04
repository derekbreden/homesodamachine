"""A VALVE TRAY IS A PLATE OF VALVE SEATS, and it is a wall of the enclosure.

One `valve_seat` per valve — four blind sockets a corner post presses into — SUNK into a flat
plate that runs from side wall to side wall of `enclosure-front-top`. The plate is one socket
and one wall thick, so it is the boss: nothing stands off it, the valve lands on its face, and
the only thing it opens for is each valve's own port, on a channel out both ends. It is
that piece's own material, fused in the way the ASSE anchor, the flow-meter anchors and every
tube rib are: `enclosure._valve_trays` stands one per deck, off the stations
`enclosure_assembly.valve_tray_stations` reads off the placed valves. NO TRAY SHIPS AS A PART,
nothing bolts a valve to one and nothing is bonded — the posts in their sockets are the whole of
the retention, the same bargain the cold core's cap lid strikes under its three valves
(`_cold_core_interface.cap_cradles`).

    ACROSS  wall to wall. The plate is the piece, so it takes no slip and ends on the two
            interior faces
    ALONG   the seats' own reach off their valves' centres, and one `MARGIN` past that. The
            plate ends where the last boss does; the valves' collets and the tube butted into
            them hang past it

This module states the tray's own figures and draws one in its own frame; `enclosure` turns it
onto a deck and fuses it. The frame is `valve_seat`'s carried onto a plate:
  Z = out of the valve-side face, the direction a valve's own +Z runs. `z = 0` IS THAT FACE, so
      the plate spans z = −`THICK` to 0 and every seat is sunk from zero. That face is the plane
      the valve's own round body boss lands on, so a valve stands ON the plate and not on four
      boss tops — `SEAT` is negative here, and that is the whole of the difference.
  X = across the plate. Y = along it. Origin is the plate's centre in both.

The rectangular socket pattern follows the valve: X across the plate and the port axis on Y.

In the piece's own print orientation the plate stands vertical, wall to wall, and NOTHING
stands off it: the port channel is a notch that runs up the plate's own section, while
`enclosure._valve_socket_cutters` carries each horizontal socket's complete round post room into
a tangent teardrop roof. There is no unsupported crown and no support in the thirty-two sockets
to pick out — which is what the thickness and roof buy, a boss on a standing plate being a
cylinder cantilevered into air.

Run:
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/valve-tray/valve_tray.py selftest
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'valve_tray'

def __getattr__(name):
    if name == "__all__":
        return _compiled('valve_tray', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('valve_tray', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('valve_tray', action="main")
