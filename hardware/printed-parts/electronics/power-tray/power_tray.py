"""Power tray — the AC + PSU block of the Zone-B electronics shelf.

Mounts the Mean Well IRM-90-12ST PSU, relay #1, and the three Wago 221-413 AC
distribution connectors (H / N / G), plus a ground-bus tie point. Retention is
**press fit** throughout, matching the valve trays and the enclosure:

- PSU and Wagos drop into press-fit pockets (walls one ``press`` clearance
  off the body).
- The relay board presses onto four posts that enter its mounting holes — the
  reverse of the valve's posts-into-tray-sockets, since here the part has the
  holes. The posts stand the board off so its underside pins clear the floor.

GFCI is tabled; the C14 inlet lives on the back panel; the ground bus is the
bolted ring-terminal stack on the heat-set ground boss. Local frame: X right,
Y deep, Z up; origin at the floor's bottom-left corner, Z = 0 the floor
underside, floor top at ``floor_t``.
"""

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
wall_t = 3.0           # pocket / perimeter wall thickness
press = 0.15           # per-side press-fit clearance (validated on the valve trays)
margin = 8.0           # part-to-plate-edge margin
perim_h = 6.0          # perimeter stiffening lip

psu_pocket_h = 12.0    # PSU pocket wall height (captures the base, leaves the body proud)
psu_notch_w = 34.0     # wire/terminal notch in each PSU end wall

wago_pocket_h = wago.height          # 8.4, capture the body; levers clear above
relay_standoff = 4.0                 # board underside above the floor (pins drop ~2)
relay_peg_d = 3.1                    # post peg into the board's 3.2 hole (press)
relay_peg_h = 3.0

gnd_boss_d = 8.0
gnd_boss_h = 8.0          # boss top at floor_t + gnd_boss_h = 11
gnd_insert_d = 4.0       # ruthex M3 heat-set insert OD — boss bore for melt-in
gnd_insert_depth = 6.0   # blind bore; insert length 5.7 + clearance

# --- Layout (corner-origin frame) -----------------------------------------
# PSU footprint at the left; terminals on its two short (±Y) ends.
psu_cx = margin + psu.width / 2.0
psu_cy = margin + psu.length / 2.0
# Relay long-axis along Y, just right of the PSU.
relay_cx = margin + psu.width + 6.0 + relay.width / 2.0
relay_cy = margin + relay.length / 2.0
# Three Wagos in a column on the far right.
wago_gap = 5.0
wago_cx = relay_cx + relay.width / 2.0 + 6.0 + wago.width / 2.0
wago_cys = [margin + wago.depth / 2.0 + i * (wago.depth + wago_gap) for i in range(3)]
# Ground-bus boss above the relay.
gnd_cx = relay_cx
gnd_cy = relay_cy + relay.length / 2.0 + 18.0

plate_w = wago_cx + wago.width / 2.0 + margin
plate_d = psu_cy + psu.length / 2.0 + margin

# Relay mounting-hole pattern in the tray frame (length now along Y).
relay_posts = [
    (relay_cx + sx * relay.hole_dy, relay_cy + sy * relay.hole_dx)
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]


def _box(w, d, h, cx, cy, z0):
    return cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).translate((cx, cy, z0))


def _pocket(cx, cy, ix, iy, h):
    """Four press-fit walls around an ix × iy cavity, rising ``h`` off the floor."""
    outer = _box(ix + 2 * wall_t, iy + 2 * wall_t, h, cx, cy, floor_t)
    inner = _box(ix, iy, h + 2, cx, cy, floor_t - 1)
    return outer.cut(inner)


def build_power_tray():
    tray = _box(plate_w, plate_d, floor_t, plate_w / 2.0, plate_d / 2.0, 0.0)

    # Perimeter stiffening lip.
    perim = _box(plate_w, plate_d, perim_h, plate_w / 2.0, plate_d / 2.0, floor_t).cut(
        _box(plate_w - 2 * wall_t, plate_d - 2 * wall_t, perim_h + 2, plate_w / 2.0, plate_d / 2.0, floor_t - 1)
    )
    tray = tray.union(perim)

    # PSU pocket with a wire notch through each ±Y end wall.
    psu_pkt = _pocket(psu_cx, psu_cy, psu.width + 2 * press, psu.length + 2 * press, psu_pocket_h)
    for sy in (-1.0, 1.0):
        psu_pkt = psu_pkt.cut(
            _box(psu_notch_w, 2 * wall_t + 2, psu_pocket_h + 2,
                 psu_cx, psu_cy + sy * (psu.length / 2.0 + press + wall_t / 2.0), floor_t - 1)
        )
    tray = tray.union(psu_pkt)

    # Three Wago pockets, each open on the −Y (wire-entry) face.
    for cy in wago_cys:
        pkt = _pocket(wago_cx, cy, wago.width + 2 * press, wago.depth + 2 * press, wago_pocket_h)
        pkt = pkt.cut(
            _box(wago.width, 2 * wall_t + 2, wago_pocket_h + 2,
                 wago_cx, cy - (wago.depth / 2.0 + press + wall_t / 2.0), floor_t - 1)
        )
        tray = tray.union(pkt)

    # Relay press-fit posts (shoulder stands the board off; peg enters the hole).
    for px, py in relay_posts:
        post = (
            cq.Workplane("XY").cylinder(relay_standoff, 3.0, centered=(True, True, False))
            .translate((px, py, floor_t))
        )
        peg = (
            cq.Workplane("XY").cylinder(relay_peg_h, relay_peg_d / 2.0, centered=(True, True, False))
            .translate((px, py, floor_t + relay_standoff))
        )
        tray = tray.union(post).union(peg)

    # Ground-bus tie-point boss — a heat-set M3 insert takes the ground-stud
    # SHCS. The "bus" is the bolted ring-terminal stack the screw clamps onto
    # this boss (hardware/reference/ground-ring-stack/): the lugs are
    # equipotential to each other, so the dielectric boss only provides the
    # clamp reaction and the earthed thread.
    boss_top = floor_t + gnd_boss_h
    boss = (
        cq.Workplane("XY").cylinder(gnd_boss_h, gnd_boss_d / 2.0, centered=(True, True, False))
        .translate((gnd_cx, gnd_cy, floor_t))
    )
    boss = boss.cut(  # blind bore from the top for the heat-set insert melt-in
        cq.Workplane("XY").cylinder(gnd_insert_depth + 2, gnd_insert_d / 2.0, centered=(True, True, False))
        .translate((gnd_cx, gnd_cy, boss_top - gnd_insert_depth))
    )
    tray = tray.union(boss)
    return tray


def main():
    export_step(build_power_tray(), str(_here.parent / "power-tray.step"))
    print("-> power-tray.step")


if __name__ == "__main__":
    main()
