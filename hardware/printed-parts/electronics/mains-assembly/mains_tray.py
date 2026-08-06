"""Mains carrier — the one printed part of the mains block.

A rectangular plate that lands on four bosses of whatever wall carries it, and
that carries, on its open face, every mains body in the appliance: a heat-set
boss under each hole of the Mean Well brick and the Teyleten relay, the AC hub's
three Wago wells rising straight out of the plate, and one stud boss for the
chassis-ground lug fan.

The plate is a rectangle. It lands flat on its carrier, and its four stations
stand in the margin band at its corners.

Frame and every dimension: `_mains_interface`.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import _mains_interface as mi


def _plate():
    return cq.Workplane("XY").box(mi.plate_x, mi.plate_y, mi.floor_t,
                                  centered=False)


def _insert_boss(px, py):
    """One heat-set boss: a column off the plate's open face, bored from its top
    for a ruthex M3 short. The bore stops `insert_backing` above the landing
    face, so no station opens on the plane the plate bears on."""
    boss = (cq.Workplane("XY")
            .cylinder(mi.board_standoff, mi.boss_d / 2.0, centered=(True, True, False))
            .translate((px, py, mi.floor_t)))
    bore = (cq.Workplane("XY")
            .cylinder(mi.insert_pocket_depth, mi.insert_pocket_radius,
                      centered=(True, True, False))
            .translate((px, py, mi.seat_z - mi.insert_pocket_depth)))
    return boss.cut(bore)


def _station_holes(part):
    """The four clearance holes the module's own screws pass through."""
    for sx, sy in mi.stations():
        part = part.cut(cq.Workplane("XY")
                        .cylinder(mi.floor_t + 2.0, mi.station_clearance_r(),
                                  centered=(True, True, False))
                        .translate((sx, sy, -1.0)))
    return part


def build_mains_tray():
    tray = _plate()
    for _body, holes, _dia in mi.bolted():
        for px, py in holes:
            tray = tray.union(_insert_boss(px, py))
    # The hub's own floor is this plate's floor — same plane, same thickness — so
    # the part goes on at the carrier's own z = 0 and its wells stand out of the
    # plate.
    hub_x, hub_y = mi.hub_corner
    tray = tray.union(mi.hub_build().translate((hub_x, hub_y, 0.0)))
    return _station_holes(tray)


def main():
    tray = build_mains_tray()
    bb = tray.val().BoundingBox()
    print(f"   mains tray {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm — "
          f"{sum(len(h) for _b, h, _d in mi.bolted())} heat-set bosses on one "
          f"{mi.floor_t:g} mm plate, {len(mi.stations())} stations to its carrier")
    export_step(tray, str(_here.parent / "mains-tray.step"))
    print("-> mains-tray.step")


if __name__ == "__main__":
    main()
