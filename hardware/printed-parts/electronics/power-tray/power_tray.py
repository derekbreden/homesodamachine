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

GFCI is tabled; the C14 inlet lives on the back panel. Local frame: X right,
Y deep, Z up; origin at the floor's bottom-left corner, Z = 0 the floor
underside, floor top at ``floor_t``.
"""

import math
import sys
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

gnd_boss_d = 8.0
gnd_boss_h = 8.0       # boss top at floor_t + gnd_boss_h = 11
gnd_insert_depth = 6.0  # blind bore for the ground-stud insert

# --- Layout (corner-origin frame) -----------------------------------------
# PSU footprint at the left; terminals on its two short (±Y) ends.
psu_cx = margin + psu.width / 2.0
psu_cy = margin + psu.length / 2.0
psu_posts = [
    (psu_cx + sx * psu.hole_dx, psu_cy + sy * psu.hole_dy)
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]

# Relay long-axis along Y, just right of the PSU.
relay_cx = margin + psu.width + 6.0 + relay.width / 2.0
relay_cy = margin + relay.length / 2.0
# Mounting-hole pattern in the tray frame (relay length now along Y).
relay_posts = [
    (relay_cx + sx * relay.hole_dy, relay_cy + sy * relay.hole_dx)
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]

# Three Wagos in a column on the far right, butt-bottom Y of each angled slot.
wago_cx = relay_cx + relay.width / 2.0 + 6.0 + wago.width / 2.0
wago_butt_ys = [margin + 4.0, margin + 27.6, margin + 51.2]

# Ground-bus boss above the relay.
gnd_cx = relay_cx
gnd_cy = relay_cy + relay.length / 2.0 + 18.0

plate_w = wago_cx + wago.width / 2.0 + margin
plate_d = psu_cy + psu.length / 2.0 + margin


def _box(w, d, h, cx, cy, z0):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((cx, cy, z0))


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


def _build_floor():
    """A single solid floor: the convex outline of every object's footprint pad,
    extruded at plate thickness. One connected piece, no thin trusses."""
    s = math.sin(math.radians(wago_tilt))
    c = math.cos(math.radians(wago_tilt))
    wy0 = -wago.height * s        # tilted-Wago XY projection: butt-top corner
    wy1 = wago.depth * c          #                            wire-bottom corner
    rects = [
        (psu_cx, psu_cy, psu.width, psu.length),           # PSU body + ledges
        (relay_cx, relay_cy, relay.width, relay.length),   # relay PCB
        (gnd_cx, gnd_cy, 18.0, 18.0),                      # ground ring-stack fan
    ]
    for by in wago_butt_ys:
        rects.append((wago_cx, by + (wy0 + wy1) / 2.0, wago.width, wy1 - wy0))
    pts = []
    for cx, cy, w, d in rects:
        pts += [(cx - w / 2.0, cy - d / 2.0), (cx + w / 2.0, cy - d / 2.0),
                (cx + w / 2.0, cy + d / 2.0), (cx - w / 2.0, cy + d / 2.0)]
    return cq.Workplane("XY").polyline(_convex_hull(pts)).close().extrude(floor_t)


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


def build_power_tray():
    tray = _build_floor()

    # PSU: four low heat-set mounting bosses (sits ~flush, no clearance standoff).
    for px, py in psu_posts:
        tray = tray.union(_insert_boss(px, py, psu_boss_d, psu_boss_h, insert_depth))

    # Relay #1: four heat-set standoff bosses (stand the board off for its pins).
    for px, py in relay_posts:
        tray = tray.union(_insert_boss(px, py, relay_boss_d, relay_standoff, insert_depth))

    # Three angled Wago slots.
    for by in wago_butt_ys:
        tray = tray.union(_wago_slot(wago_cx, by))

    # Ground-bus tie-point boss — heat-set insert for the ground-stud SHCS; the
    # "bus" is the bolted ring-terminal stack the screw clamps onto this boss
    # (hardware/reference/ground-ring-stack/).
    tray = tray.union(_insert_boss(gnd_cx, gnd_cy, gnd_boss_d, gnd_boss_h, gnd_insert_depth))
    return tray


def main():
    export_step(build_power_tray(), str(_here.parent / "power-tray.step"))
    print("-> power-tray.step")


if __name__ == "__main__":
    main()
