"""Shared engine for flat-board electronics trays (controller, driver).

Same idioms as the power tray: tight flush packing, a single convex-outline
floor, no walls, heat-set M3 boss mounting. A board reference exposes ``length``
(X), ``width`` (Y), ``holes`` [(dx,dy), ...] and ``build()``; a ``Mount`` places
it at centre ``c`` rotated ``rot`` degrees about Z. Boards with holes stand on
heat-set bosses; boards with no holes (tiny adhesive parts) rest on the floor.

Geometry helpers and the floor/boss conventions are reused from
[`power_tray`](power-tray/power_tray.py)."""

import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics" / "power-tray"))
sys.path.insert(0, str(_hw / "scripts"))
import power_tray as pt
from power_tray import _rot, _rect_corners, _convex_hull, _insert_boss

floor_t = pt.floor_t
insert_depth = pt.insert_depth
margin = pt.margin
board_standoff = 5.0    # boss height — stands every board off so its pins clear
board_boss_d = 7.0      # heat-set boss diameter


@dataclass(frozen=True)
class Mount:
    ref: object          # a board reference module (.length, .width, .holes, .build(), .name)
    c: tuple             # centre (x, y) in the tray frame
    rot: float = 0.0     # rotation about Z, degrees


def _posts(m):
    out = []
    for dx, dy in m.ref.holes:
        rx, ry = _rot(dx, dy, m.rot)
        out.append((m.c[0] + rx, m.c[1] + ry))
    return out


def build_module_tray(mounts):
    """Single convex-outline floor under every board footprint, plus a heat-set
    standoff boss at each mounting hole. No walls."""
    pts = []
    for m in mounts:
        pts += _rect_corners(m.c[0], m.c[1], m.ref.length, m.ref.width, m.rot)
    tray = cq.Workplane("XY").polyline(_convex_hull(pts)).close().extrude(floor_t)
    for m in mounts:
        for px, py in _posts(m):
            tray = tray.union(_insert_boss(px, py, board_boss_d, board_standoff, insert_depth))
    return tray


TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)
_COLORS = {
    "esp32": cq.Color(0.20, 0.45, 0.75),
    "mcp": cq.Color(0.25, 0.55, 0.40),
    "ds3231": cq.Color(0.55, 0.30, 0.55),
    "rs485": cq.Color(0.75, 0.55, 0.20),
    "uln": cq.Color(0.25, 0.55, 0.40),
    "l298n": cq.Color(0.65, 0.22, 0.22),
    "relay": cq.Color(0.20, 0.45, 0.75),
    "dcdist": cq.Color(0.45, 0.45, 0.50),
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
