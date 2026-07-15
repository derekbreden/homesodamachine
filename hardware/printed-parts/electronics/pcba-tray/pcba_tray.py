"""PCBA tray — the controller-board mount of the Zone-B electronics shelf.

Carries the JLCPCB-assembled controller PCBA ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx),
85.05 × 72.85 mm as fabbed): four M3 heat-set standoff bosses under the board's
four electrically isolated plated mounting holes (MH1–MH4, 3.2 mm hole /
4.0 mm pad, a 78.0 × 66.3 mm rectangle) — M3 SHCS down through the board into
ruthex inserts, the board's bottom face seating on the boss tops. Same idioms
as the power tray: a single convex-outline floor, no walls, heat-set bosses;
built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.
The 5 mm standoff clears the board's THT tails (XH wafers, the J10 screw
block, U10, BT1, J14's shield legs).

Local frame: the PCBA's own pcb frame (pcbX / pcbY exactly as in `pcba.tsx` —
outline x[−68, 17], y[−36.3, 36.5]), Z up, floor underside at Z = 0, so the
boss centres below are the MH1–MH4 coordinates verbatim. Connector openings
face the board edges: USB-C (J14) flush on the west edge, the J10 12 V screw
throats east — the tray leaves both edges open.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step
import module_tray as mt
from module_tray import Mount

# Board datum — pcba.tsx <board outline> + the MH1–MH4 <platedhole>s.
_outline_x = (-68.0, 17.0)
_outline_y = (-36.3, 36.5)
_holes_pcb = ((-64.5, 33.0), (13.5, 33.0), (13.5, -33.3), (-64.5, -33.3))
_centre = (sum(_outline_x) / 2.0, sum(_outline_y) / 2.0)
_thickness = 1.6


def _build_board():
    """Bare-outline stand-in for the assembly view (the true 3D is
    hardware/pcb/pcba/out/pcba.glb)."""
    slab = cq.Workplane("XY").box(
        _outline_x[1] - _outline_x[0], _outline_y[1] - _outline_y[0], _thickness,
        centered=(True, True, False))
    for hx, hy in _holes_pcb:
        slab = slab.cut(
            cq.Workplane("XY").cylinder(_thickness + 1, 3.2 / 2.0, centered=(True, True, False))
            .translate((hx - _centre[0], hy - _centre[1], -0.5)))
    return slab


board = SimpleNamespace(
    name="pcba",
    length=_outline_x[1] - _outline_x[0],
    width=_outline_y[1] - _outline_y[0],
    holes=tuple((hx - _centre[0], hy - _centre[1]) for hx, hy in _holes_pcb),
    hole_dia=3.2,
    build=_build_board,
)

MOUNTS = [Mount(board, _centre, 0.0)]


def build_pcba_tray():
    return mt.build_module_tray(MOUNTS)


def main():
    tray = build_pcba_tray()
    export_step(tray, str(_here.parent / "pcba-tray.step"))
    print("-> pcba-tray.step (%.1f cm3)" % (tray.val().Volume() / 1000.0))


if __name__ == "__main__":
    main()
