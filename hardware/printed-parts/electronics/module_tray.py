"""Shared engine for flat-board electronics trays (the pcba tray, the Lite
logic tray).

Tight flush packing, a single convex-outline floor, no walls, heat-set M3 boss
mounting. A board reference exposes ``length`` (X), ``width`` (Y), ``holes``
[(dx,dy), ...] and ``build()``; a ``Mount`` places it at centre ``c`` rotated
``rot`` degrees about Z. Boards with holes stand on heat-set bosses; boards with
no holes (tiny adhesive parts) rest on the floor."""

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

floor_t = 3.0           # base-plate thickness
margin = 8.0            # part-to-plate-edge margin
board_standoff = 5.0    # boss height — stands every board off so its pins clear


def _rot(dx, dy, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return (dx * c - dy * s, dx * s + dy * c)


def _rect_corners(cx, cy, xdim, ydim, deg):
    """Four corners of an xdim×ydim footprint centred at (cx,cy), rotated deg."""
    out = []
    for hx, hy in ((-xdim / 2, -ydim / 2), (xdim / 2, -ydim / 2),
                   (xdim / 2, ydim / 2), (-xdim / 2, ydim / 2)):
        rx, ry = _rot(hx, hy, deg)
        out.append((cx + rx, cy + ry))
    return out


def _convex_hull(points):
    """2-D convex hull (monotone chain), CCW, no collinear points."""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _boss_spec(hole_dia):
    """(boss outer dia, heat-set bore dia, bore depth) sized to the board's hole:
    M2 for ~2 mm board holes, M3 otherwise."""
    if hole_dia <= 2.6:
        return 5.5, 3.2, 4.0      # M2 ruthex insert
    return 7.0, 4.0, 5.5          # M3 ruthex insert


def _insert_boss(px, py, boss_d, bore_d, depth):
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
    out = []
    for dx, dy in m.ref.holes:
        rx, ry = _rot(dx, dy, m.rot)
        out.append((m.c[0] + rx, m.c[1] + ry))
    return out


def build_module_tray(mounts):
    """Single convex-outline floor under every board footprint — grown where a
    mounting hole sits nearer a board edge than its boss radius, so every boss
    lands fully on the floor — plus a heat-set standoff boss (M2 or M3, sized
    per board) at each mounting hole. No walls."""
    pts = []
    for m in mounts:
        pts += _rect_corners(m.c[0], m.c[1], m.ref.length, m.ref.width, m.rot)
        r = _boss_spec(getattr(m.ref, "hole_dia", 3.2))[0] / 2.0
        for px, py in _posts(m):
            pts += [(px - r, py - r), (px + r, py - r), (px + r, py + r), (px - r, py + r)]
    tray = cq.Workplane("XY").polyline(_convex_hull(pts)).close().extrude(floor_t)
    for m in mounts:
        boss_d, bore_d, depth = _boss_spec(getattr(m.ref, "hole_dia", 3.2))
        for px, py in _posts(m):
            tray = tray.union(_insert_boss(px, py, boss_d, bore_d, depth))
    return tray


TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)
_COLORS = {
    "pcba": cq.Color(0.13, 0.35, 0.22),
}


def build_module_assembly(mounts, name):
    assy = cq.Assembly(name=name)
    assy.add(build_module_tray(mounts).val(), name="tray", color=TRAY_COLOR)
    for i, m in enumerate(mounts):
        # Every board seats at the standoff height; hole-less boards (tiny
        # adhesive parts) ride at the same level, tucked against a neighbour.
        s = (m.ref.build().val().rotate((0, 0, 0), (0, 0, 1), m.rot)
             .translate((m.c[0], m.c[1], floor_t + board_standoff)))
        assy.add(s, name="%s%d" % (m.ref.name, i),
                 color=_COLORS.get(m.ref.name, cq.Color(0.5, 0.5, 0.5)))
    return assy
