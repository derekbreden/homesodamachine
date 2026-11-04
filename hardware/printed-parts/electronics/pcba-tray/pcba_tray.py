"""PCBA tray — the main board's bench mount, off the +X wall of back-top.

Carries the JLCPCB-assembled main board ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx),
[85 × 72.8 mm](PCBA_SIZE) as fabbed): four M3 heat-set standoff bosses under the board's
four electrically isolated plated mounting holes (MH1–MH4, 3.2 mm hole /
4.0 mm pad, a 78.0 × 66.3 mm rectangle) — M3 SHCS down through the board into
ruthex inserts, the board's bottom face seating on the boss tops. A single
convex-outline floor, no walls, heat-set bosses;
built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.
The 5 mm standoff clears the board's THT tails (XH wafers, the J10 screw
block, U10, BT1, J14's shield legs).

The populated-board model carries those tails 2 mm below the PCB underside.
That underside remains the Z = 0 mounting datum; the tail envelope is what
keeps either a bench-tray floor or the appliance wall out from under it.

Local frame: the main board's own pcb frame (pcbX / pcbY exactly as in `pcba.tsx` —
outline x[−68, 17], y[−36.3, 36.5]), Z up, floor underside at Z = 0, so the
boss centres below are the MH1–MH4 coordinates verbatim. Connector openings
face the board edges: USB-C (J14) flush on the west edge, the J10 12 V screw
throats east — the tray leaves both edges open.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_py_comments
from module_tray import Mount

from _rust_data import request as _request

_GLB = _hw / 'pcb' / 'pcba' / 'out' / 'pcba.glb'


def _data(**payload):
    import _rust_part
    if payload.get('method') in ('boxes', 'stock'):
        _rust_part._READ_TARGETS.add(_GLB.resolve().relative_to(_rust_part.ROOT.resolve()).as_posix())
    return _request('part-data', 'part-data', {'part': 'pcba-tray', 'glb': str(_GLB), **payload})


_state = _data()
globals().update(_state['values'])
_outline_x, _outline_y, _centre = tuple(_outline_x), tuple(_outline_y), tuple(_centre)
_holes_pcb = tuple(tuple(p) for p in _holes_pcb)
_hole_joints = tuple((pin, tuple(p), dia) for pin, p, dia in _hole_joints)


def _glb_component_boxes():
    """Fab-model component bounds in PCB coordinates, read by Rust."""
    return [tuple(box) for box in _data(method='boxes')]


def component_stock():
    """The board's above-face and pin-tail stock from the Rust GLB reader."""
    above, below = _data(method='stock')
    return ([tuple(tuple(p) for p in row) for row in above],
            [tuple(tuple(p) for p in row) for row in below])


def _build_board():
    """The main board as a simplified populated model: the fabbed
    outline slab + one box per component at the axis-aligned bounding box of
    its actual 3D model in `hardware/pcb/pcba/out/pcba.glb` (the full mesh
    detail stays in the glb; this carries every body's true footprint and
    height). The glb board slab itself is skipped — the outline slab with its
    MH1–MH4 holes stands in for it.

    A through-hole component's glb box spans both sides of the board. Its body
    is kept above the top face and its wall-facing projection is kept separately
    as the 2 mm pin-tail envelope. Imported lead lengths vary by model, so that
    projection is capped at the assembly clearance this board states rather than
    letting one decorative component model move the PCB mounting datum. Round each
    mounting hole the boxes give way to the board's own joints (`_hole_joints`):
    component AABBs are conservative rectangles drawn from top-side bodies, and
    within `_hole_reach` of a hole the underside carries nothing else."""
    import cadquery as cq
    slab = cq.Workplane("XY").box(
        _outline_x[1] - _outline_x[0], _outline_y[1] - _outline_y[0], _thickness,
        centered=(True, True, False))
    for hx, hy in _holes_pcb:
        slab = slab.cut(
            cq.Workplane("XY").cylinder(_thickness + 1, 3.2 / 2.0, centered=(True, True, False))
            .translate((hx - _centre[0], hy - _centre[1], -0.5)))
    above, below = component_stock()
    for origin, size in above:
        slab = slab.union(cq.Workplane("XY").box(*size, centered=(False, False, False))
                          .translate(origin))
    tails = None
    for origin, size in below:
        tail = (cq.Workplane("XY").box(*size, centered=(False, False, False))
                .translate(origin))
        tails = tail if tails is None else tails.union(tail)
    if tails is not None:
        for hx, hy in _holes_pcb:
            tails = tails.cut(
                cq.Workplane("XY")
                .box(2.0 * _hole_reach, 2.0 * _hole_reach, pin_drop + 1.0,
                     centered=(True, True, False))
                .translate((hx - _centre[0], hy - _centre[1], -pin_drop - 0.5)))
        for _pin, (px, py), dia in _hole_joints:
            tails = tails.union(
                cq.Workplane("XY").cylinder(pin_drop, dia / 2.0, centered=(True, True, False))
                .translate((px - _centre[0], py - _centre[1], -pin_drop)))
        slab = slab.union(tails)
    return slab


board = SimpleNamespace(**_state['board'], build=_build_board)
board.holes = tuple(tuple(p) for p in board.holes)
board.joints = tuple(tuple(p) for p in board.joints)

MOUNTS = [Mount(board, _centre, 0.0)]


# --- The board's own stations -----------------------------------------------
# Two frames. `pcba.tsx` writes every pad and connector in the PCB FRAME; the board is DRAWN
# about its own outline centre, which is the datum its mount pattern and its box share. They
# differ by `_centre`, and `port` applies it — so a caller names a connector out of
# `pcba.tsx` verbatim.

def port(px, py) -> tuple:
    """A connector's station on the board's top mating face."""
    return tuple(tuple(p) for p in _data(method='port', px=px, py=py))


def stations_hold():
    """Hold the mating plane to the board this module draws.

    `port` measures `_thickness` up from zero, so zero remains the PCB underside. The populated
    model deliberately continues `pin_drop` below it: that floor is the tail-clearance plane a
    wall or tray may approach, while every mounting hole remains on Z = 0."""
    floor = _build_board().val().BoundingBox().zmin
    if abs(floor + pin_drop) > 1e-9:
        raise ValueError(
            f"the board's tail envelope ends at z = {floor:.4f}, not {-pin_drop:g}; "
            "the placed solid no longer gives the mounting plane its stated below-board air.")


def main():
    substitute_py_comments(_here, variables=_data()['variables'])
    print(f'-> {_here.name}')


if __name__ == "__main__":
    main()
