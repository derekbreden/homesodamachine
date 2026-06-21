"""Power tray — the AC + PSU block of the Zone-B electronics shelf.

Mounts the Mean Well IRM-90-12ST PSU, relay #1, and the three Wago 221-413 AC
distribution connectors (H / N / G), plus a ground-bus tie point.

- **PSU and relay #1** screw down into **heat-set M3 insert bosses** (ruthex),
  the same insert + SHCS idiom as every module on the shelf. The PSU sits on
  four low bosses (just tall enough to seat an insert — no clearance standoff);
  the relay sits on four taller standoff bosses so its underside pins clear the
  floor.
- **The three Wagos** drop butt-end-first into **angled slots**: each lug tilts
  45° up toward its wire end, and the blank butt end press-fits into a slot that
  wraps it on five faces (both X, both Z, and the −Y end), open toward the wire
  end so the lug sticks halfway out for wiring.
- **Ground bus** — a heat-set boss for the ground-stud SHCS; the bus is the
  bolted ring-terminal stack (hardware/reference/ground-ring-stack/).

The components pack **flush** (no inter-part gaps), and the floor is the single
convex outline of every footprint. The build is parameterised by a ``Layout``
(component centres + Z rotations), so the sibling ``narrow-power-tray`` reuses
``build_tray`` with the PSU turned 90°. GFCI is tabled; the C14 inlet lives on
the back panel. Local frame: X right, Y deep, Z up; origin at the floor's
bottom-left corner, Z = 0 the floor underside, floor top at ``floor_t``.
"""

import math
import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "meanwell-irm90",
    _hw / "reference" / "wago-221-413",
    _hw / "reference" / "teyleten-relay",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import meanwell_irm90 as psu
import wago_221_413 as wago
import teyleten_relay as relay

# --- Tray parameters ------------------------------------------------------
floor_t = 3.0          # base-plate thickness
wall_t = 3.0           # slot wall thickness
press = 0.15           # per-side press-fit clearance (validated on the valve trays)
margin = 8.0           # part-to-plate-edge margin

# Heat-set mounting — ruthex M3 insert melted into a printed boss, M3 SHCS
# through the part into the insert. Replaces the press-fit pockets and pegs.
insert_d = 4.0         # melt-in bore diameter for the M3 insert
insert_depth = 5.5     # blind bore depth in the PSU / relay bosses

psu_boss_d = 8.0       # PSU mounting boss (low — seats the insert, not a standoff)
psu_boss_h = 4.0
relay_boss_d = 7.0     # relay standoff boss
relay_standoff = 4.0   # board underside above the floor so its ~2 mm pins clear

wago_tilt = 45.0                 # each lug angles up toward its wire end
wago_engage = wago.depth / 2.0   # butt half buried in the slot; wire half sticks out
wago_ped = 30.0                  # slot pedestal depth (local frame; trimmed at the plate)
wago_slot_half = wago.width / 2.0 + wall_t + press   # slot half-width in X
wago_pitch = 23.6                # Y spacing of the slots in a column

gnd_boss_d = 8.0
gnd_boss_h = 8.0       # boss top at floor_t + gnd_boss_h = 11
gnd_insert_depth = 6.0  # blind bore for the ground-stud insert
gnd_foot = 18.0        # ground ring-stack fan footprint (square)


@dataclass(frozen=True)
class Layout:
    """Placement of the four mounted things in the tray frame. ``*_rot`` is the
    part's rotation about Z in degrees; ``wago_places`` is one (cx, butt_y) per
    angled Wago slot."""
    psu_c: tuple
    psu_rot: float
    relay_c: tuple
    relay_rot: float
    wago_places: tuple
    gnd_c: tuple


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


def _hole_posts(cx, cy, dx, dy, deg):
    """The 4 mounting-hole positions (±dx, ±dy about the part centre), rotated."""
    out = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            rx, ry = _rot(sx * dx, sy * dy, deg)
            out.append((cx + rx, cy + ry))
    return out


def _abox(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from corner (x0,y0,z0) to (x1,y1,z1)."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _insert_boss(px, py, d, h, depth):
    """A cylindrical boss rising ``h`` off the floor with a blind heat-set bore
    opening at its top."""
    top = floor_t + h
    boss = (
        cq.Workplane("XY").cylinder(h, d / 2.0, centered=(True, True, False))
        .translate((px, py, floor_t))
    )
    bore = (
        cq.Workplane("XY").cylinder(depth + 1, insert_d / 2.0, centered=(True, True, False))
        .translate((px, py, top - depth))
    )
    return boss.cut(bore)


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


def _wago_slot(cx, by):
    """Angled butt-end slot for one Wago. Built in a local frame (butt-bottom
    centre at the origin, wire end +Y, body up +Z), then tilted up and seated.

    The slot wraps the butt half on five faces — both X, both Z, and the −Y end
    — and is open toward +Y where the wire half sticks out. A pedestal carries it
    down to the plate."""
    e = wall_t + press
    hw = wago.width / 2.0
    tower = _abox(-(hw + e), (hw + e), -e, wago_engage, -wago_ped, wago.height + e)
    cav = _abox(-(hw + press), (hw + press), -press, wago_engage + 40.0, -press, wago.height + press)
    slot = tower.cut(cav)
    slot = slot.rotate((0, 0, 0), (1, 0, 0), wago_tilt).translate((cx, by, floor_t))
    slot = slot.cut(_abox(cx - 60.0, cx + 60.0, by - 80.0, by + 80.0, -100.0, 0.0))  # trim below the plate
    return slot


def _build_floor(L):
    """A single solid floor: the convex outline of every object's footprint,
    extruded at plate thickness. The Wago footprints use the full slot extent so
    the floor underlies each angled slot with nothing cantilevered off an edge."""
    pts = []
    pts += _rect_corners(L.psu_c[0], L.psu_c[1], psu.width, psu.length, L.psu_rot)
    pts += _rect_corners(L.relay_c[0], L.relay_c[1], relay.length, relay.width, L.relay_rot)
    pts += _rect_corners(L.gnd_c[0], L.gnd_c[1], gnd_foot, gnd_foot, 0.0)
    for cx, by in L.wago_places:
        bb = _wago_slot(cx, by).val().BoundingBox()
        pts += [(bb.xmin, bb.ymin), (bb.xmax, bb.ymin),
                (bb.xmax, bb.ymax), (bb.xmin, bb.ymax)]
    return cq.Workplane("XY").polyline(_convex_hull(pts)).close().extrude(floor_t)


def build_tray(L):
    """Build the tray for a given Layout."""
    tray = _build_floor(L)
    for px, py in _hole_posts(L.psu_c[0], L.psu_c[1], psu.hole_dx, psu.hole_dy, L.psu_rot):
        tray = tray.union(_insert_boss(px, py, psu_boss_d, psu_boss_h, insert_depth))
    for px, py in _hole_posts(L.relay_c[0], L.relay_c[1], relay.hole_dx, relay.hole_dy, L.relay_rot):
        tray = tray.union(_insert_boss(px, py, relay_boss_d, relay_standoff, insert_depth))
    for cx, by in L.wago_places:
        tray = tray.union(_wago_slot(cx, by))
    tray = tray.union(_insert_boss(L.gnd_c[0], L.gnd_c[1], gnd_boss_d, gnd_boss_h, gnd_insert_depth))
    return tray


# --- Wide layout (default) ------------------------------------------------
# PSU at the lower-left; relay flush to its right; Wago column flush past the
# relay; ground boss flush above the relay. Everything packs edge-to-edge.
_psu_c = (margin + psu.width / 2.0, margin + psu.length / 2.0)
_relay_cx = margin + psu.width + relay.width / 2.0
_relay_cy = margin + relay.length / 2.0
_wago_cx = _relay_cx + relay.width / 2.0 + wago_slot_half
WIDE = Layout(
    psu_c=_psu_c, psu_rot=0.0,
    relay_c=(_relay_cx, _relay_cy), relay_rot=90.0,
    wago_places=tuple((_wago_cx, margin + 8.454 + i * wago_pitch) for i in range(3)),
    gnd_c=(_relay_cx + 6.5, _relay_cy + relay.length / 2.0 + 12.0),  # open space above the cluster
)


def build_power_tray():
    return build_tray(WIDE)


def main():
    export_step(build_power_tray(), str(_here.parent / "power-tray.step"))
    print("-> power-tray.step")


if __name__ == "__main__":
    main()
