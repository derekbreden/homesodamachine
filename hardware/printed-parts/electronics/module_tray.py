"""Shared engine for flat-board electronics trays (the pcba tray, the Lite
logic tray).

Tight flush packing, a single convex-outline floor, no walls, heat-set M3 boss
mounting. A board reference exposes ``length`` (X), ``width`` (Y), ``holes``
[(dx,dy), ...] and ``build()``; a ``Mount`` places it at centre ``c`` rotated
``rot`` degrees about Z. Boards with holes stand on heat-set bosses; boards with
no holes (tiny adhesive parts) rest on the floor.

The numbers import alone: CadQuery and the materials load when a builder runs."""

import sys
from dataclasses import dataclass
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'module-tray', **payload})


globals().update(_data())


def _rot(dx, dy, deg):
    return tuple(_data(method='rot', dx=dx, dy=dy, degrees=deg))


def _rect_corners(cx, cy, xdim, ydim, deg):
    return [tuple(p) for p in _data(method='corners', center=[cx, cy], width=xdim,
                                   depth=ydim, degrees=deg)]


def _convex_hull(points):
    return [tuple(p) for p in _data(method='hull', points=points)]


def _boss_spec(hole_dia):
    return tuple(_data(method='boss', hole_dia=hole_dia))


def _insert_boss(px, py, boss_d, bore_d, depth):
    import cadquery as cq
    top = floor_t + board_standoff
    boss = (cq.Workplane("XY").cylinder(board_standoff, boss_d / 2.0, centered=(True, True, False))
            .translate((px, py, floor_t)))
    bore = (cq.Workplane("XY").cylinder(depth + 1, bore_d / 2.0, centered=(True, True, False))
            .translate((px, py, top - depth)))
    return boss.cut(bore)


@dataclass(frozen=True)
class Mount:
    ref: object          # a board reference module (.length, .width, .holes, .hole_dia, .build(), .name)
    c: tuple             # centre (x, y) in the tray frame
    rot: float = 0.0     # rotation about Z, degrees


def _posts(m):
    return [tuple(p) for p in _data(method='posts', center=m.c,
                                   rotation=m.rot, holes=m.ref.holes)]


def build_module_tray(mounts):
    """Single convex-outline floor under every board footprint — grown where a
    mounting hole sits nearer a board edge than its boss radius, so every boss
    lands fully on the floor — plus a heat-set standoff boss (M2 or M3, sized
    per board) at each mounting hole. No walls."""
    import cadquery as cq
    pts = []
    for m in mounts:
        pts += _rect_corners(m.c[0], m.c[1], m.ref.length, m.ref.width, m.rot)
        r = _boss_spec(getattr(m.ref, "hole_dia", 3.2))[0] / 2.0
        for px, py in _posts(m):
            pts += [(px - r, py - r), (px + r, py - r), (px + r, py + r), (px - r, py + r)]
    hull = _convex_hull(pts)
    tray = cq.Workplane("XY").polyline(hull + hull[:1]).wire().extrude(floor_t)
    for m in mounts:
        boss_d, bore_d, depth = _boss_spec(getattr(m.ref, "hole_dia", 3.2))
        for px, py in _posts(m):
            tray = tray.union(_insert_boss(px, py, boss_d, bore_d, depth))
    return tray


def build_module_assembly(mounts, name):
    import cadquery as cq
    from _materials import C_PCBA, M_PETG_BLACK
    # The tray prints off the same black spool every other printed body on this machine does
    # (`pcba-tray/README.md`).
    tray_color = M_PETG_BLACK
    colors = {
        # Black mask, white silk — what `pcb/pcba/order.md` places the board at.
        "pcba": C_PCBA,
    }
    assy = cq.Assembly(name=name)
    assy.add(build_module_tray(mounts).val(), name="tray", color=tray_color)
    for i, m in enumerate(mounts):
        # Every board seats at the standoff height; hole-less boards (tiny
        # adhesive parts) ride at the same level, tucked against a neighbour.
        s = (m.ref.build().val().rotate((0, 0, 0), (0, 0, 1), m.rot)
             .translate((m.c[0], m.c[1], floor_t + board_standoff)))
        assy.add(s, name="%s%d" % (m.ref.name, i),
                 color=colors.get(m.ref.name, C_PCBA))
    return assy
