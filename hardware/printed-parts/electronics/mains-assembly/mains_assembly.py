"""Mains block assembly — the carrier with every mains body seated on it, as it
leaves the bench and goes into the machine.

`_report` proves what the module claims about itself: that no two of its solids
overlap, that every hole pattern in it stands on a boss, that every insert bore
stops short of the landing face, that every terminal faces the open side, and
that all four of its own stations are reachable with the block fully assembled.

Frame and every dimension: `_mains_interface`.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "reference" / "wago-221-413", _here.parent,
           _hw.parent / "tools"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
from docgen import substitute_md
import wago_221_413 as wago
import _mains_interface as mi
import mains_tray

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)
COLORS = {"psu": cq.Color(0.30, 0.32, 0.36),
          "relay-1": cq.Color(0.13, 0.35, 0.22),
          "ground-stack": cq.Color(0.72, 0.62, 0.30),
          "wago": cq.Color(0.85, 0.45, 0.15)}

SEATED = ("psu", "relay-1", "ground-stack")


def _seated(body):
    (cx, cy), rot, z0 = mi.seat(body)
    return (mi.seated_build(body).val()
            .rotate((0, 0, 0), (0, 0, 1), rot)
            .translate((cx, cy, z0)))


def _wagos():
    """Each lug stood on its butt end in its well, wire ports up — the quarter
    turn carries its wire-entry axis onto the module's own open direction."""
    out = []
    for cx, cy in mi.wago_places():
        out.append(wago.build().val()
                   .rotate((0, 0, 0), (1, 0, 0), 90)
                   .translate((0, wago.height / 2.0, wago.depth / 2.0))
                   .translate((cx, cy, mi.floor_t)))
    return out


def build_assembly(name="mains-assembly"):
    assy = cq.Assembly(name=name)
    assy.add(mains_tray.build_mains_tray().val(), name="tray", color=TRAY_COLOR)
    for body in SEATED:
        assy.add(_seated(body), name=body, color=COLORS[body])
    for i, w in enumerate(_wagos()):
        assy.add(w, name=f"wago{i}", color=COLORS["wago"])
    return assy


def _solids(assy):
    return [(c.name, c.obj.locate(c.loc) if hasattr(c, "loc") else c.obj)
            for c in assy.children]


def _column(x, y, r, z0, z1):
    return (cq.Workplane("XY").circle(r).extrude(z1 - z0)
            .translate((x, y, z0)).val())


def _report():
    tray = mains_tray.build_mains_tray()
    tray_solid = tray.val()
    parts = [("tray", tray_solid)]
    for body in SEATED:
        parts.append((body, _seated(body)))
    for i, w in enumerate(_wagos()):
        parts.append((f"wago{i}", w))

    print(f"   plate {mi.plate_x:.1f} × {mi.plate_y:.1f} × {mi.floor_t:g} mm, "
          f"bodies standing {mi.reach():.1f} off its open face")
    print(f"   envelope {mi.envelope()[0]:.1f} × {mi.envelope()[1]:.1f} × "
          f"{mi.envelope()[2]:.1f} mm from the landing face")

    worst = 0.0
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            v = parts[i][1].intersect(parts[j][1]).Volume()
            if v > worst:
                worst = v
            assert v < 1e-6, f"{parts[i][0]} ∩ {parts[j][0]} = {v:.4f} mm³"
    print(f"   {len(parts)} solids, no two overlapping (worst {worst:.2e} mm³)")

    # Every bolted hole stands on a boss: the ring between the insert's bore and
    # the boss wall, unbroken for the whole standoff.
    for body, holes, _dia in mi.bolted():
        for px, py in holes:
            ring = (_column(px, py, mi.boss_d / 2.0, mi.floor_t, mi.seat_z)
                    .cut(_column(px, py, mi.insert_pocket_radius,
                                 mi.floor_t - 1.0, mi.seat_z + 1.0)))
            v = ring.intersect(tray_solid).Volume()
            assert v > 0.99 * ring.Volume(), \
                f"{body} hole at ({px:.1f},{py:.1f}) stands on air"
    print(f"   {sum(len(h) for _b, h, _d in mi.bolted())} holes, each on its own boss "
          f"for the whole {mi.board_standoff:g} mm of standoff")

    # No insert bore opens on the face the plate bears on.
    landing = (cq.Workplane("XY").box(mi.plate_x, mi.plate_y, mi.insert_backing,
                                      centered=False).val())
    for _body, holes, _dia in mi.bolted():
        for px, py in holes:
            bore = _column(px, py, mi.insert_pocket_radius, 0.0, mi.insert_backing)
            v = bore.intersect(landing).intersect(tray_solid).Volume()
            want = 3.14159 * mi.insert_pocket_radius ** 2 * mi.insert_backing
            assert v > 0.9 * want, f"insert at ({px:.1f},{py:.1f}) breaks the landing face"
    print(f"   every insert bore stops {mi.insert_backing:g} mm above the landing face")

    # A station must still be reachable with the block wired: nothing of the
    # module may stand over the column its driver comes down.
    driver_r = mi.station_clearance_r() * 2.0
    for sx, sy in mi.stations():
        col = _column(sx, sy, driver_r, mi.floor_t, mi.floor_t + mi.reach())
        for name, solid in parts:
            if name == "tray":
                continue
            v = col.intersect(solid).Volume()
            assert v < 1e-6, f"station ({sx:.1f},{sy:.1f}) is under {name}"
    print(f"   {len(mi.stations())} stations, each with a clear ⌀{2 * driver_r:g} mm "
          f"column to the open face")

    assert mi.pin_clearance() > 0.0
    print(f"   the relay's pins hang {mi.pin_clearance():.1f} mm over the plate")

    # The block is wired flat: nothing is entered from an end or from behind.
    for name, _pos, axis in mi.terminals():
        assert axis[2] > 0.999, f"{name} does not look off the open face"
    print(f"   {len(mi.terminals())} terminals, every one of them looking off "
          f"the open face")

    # The hub's own floor and the plate's are one plane.
    assert mi.hub_build().val().BoundingBox().zmin == 0.0
    hub_floor = mi.hub_build().val().BoundingBox().zlen
    assert abs(mi.floor_t - mains_tray.mi.floor_t) < 1e-9
    print(f"   AC hub grown into the plate — one {mi.floor_t:g} mm floor, wells "
          f"reaching {hub_floor:.1f} mm")

    # Nothing overhangs the outline the joint wants.
    plan = (cq.Workplane("XY").box(mi.plate_x, mi.plate_y, 400.0, centered=False)
            .val())
    for name, solid in parts:
        v = solid.Volume() - solid.intersect(plan).Volume()
        assert v < 1e-6, f"{name} stands {v:.2f} mm³ outside the plate's outline"
    print("   every body inside the plate's own outline")


def _sync_readme():
    driver_d = 4.0 * mi.station_clearance_r()
    holes = sum(len(h) for _b, h, _d in mi.bolted())
    wells = mi.hub_build().val().BoundingBox().zlen
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PLATE_X": f"{mi.plate_x:.4g}",
            "PLATE_Y": f"{mi.plate_y:.4g}",
            "FLOOR_T": f"{mi.floor_t:.4g}",
            "REACH": f"{mi.reach():.4g}",
            "ENVELOPE_Z": f"{mi.envelope()[2]:.4g}",
            "PSU_LEN": f"{mi.psu_span_x:.4g}",
            "RELAY_LEN": f"{mi.relay_span_x:.4g}",
            "LEAD_GAP": f"{mi.lead_gap:.4g}",
            "SEAT_Z": f"{mi.seat_z:.4g}",
            "BOSS_D": f"{mi.boss_d:.4g}",
            "INSERT_D": f"{2 * mi.insert_pocket_radius:.4g}",
            "INSERT_DEPTH": f"{mi.insert_pocket_depth:.4g}",
            "INSERT_BACKING": f"{mi.insert_backing:.4g}",
            "PIN_CLEARANCE": f"{mi.pin_clearance():.4g}",
            "WELL_TOP": f"{wells:.4g}",
            "STATION_COUNT": f"{len(mi.stations())}",
            "STATION_INSET": f"{mi.station_inset:.4g}",
            "MARGIN": f"{mi.margin:.4g}",
            "TERMINAL_COUNT": f"{len(mi.terminals())}",
            "BOSS_COUNT": f"{holes}",
            "STANDOFF": f"{mi.board_standoff:.4g}",
            "DRIVER_D": f"{driver_d:.4g}",
        },
        expected_counts={
            "PLATE_X": 1, "PLATE_Y": 1, "FLOOR_T": 1, "REACH": 1,
            "ENVELOPE_Z": 1, "PSU_LEN": 2, "RELAY_LEN": 1, "LEAD_GAP": 1,
            "SEAT_Z": 1, "BOSS_D": 1, "INSERT_D": 1, "INSERT_DEPTH": 1,
            "INSERT_BACKING": 1, "PIN_CLEARANCE": 1, "WELL_TOP": 1,
            "STATION_COUNT": 1, "STATION_INSET": 1, "MARGIN": 1,
            "TERMINAL_COUNT": 1, "BOSS_COUNT": 1, "STANDOFF": 1,
            "DRIVER_D": 1,
        },
    )


def main():
    _report()
    _sync_readme()
    export_assembly(build_assembly(), str(_here.parent / "mains-assembly.step"))
    print("-> mains-assembly.step")


if __name__ == "__main__":
    main()
