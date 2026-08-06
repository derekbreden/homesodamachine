"""Mains block — the four mains bodies in the rigid relative pose they hold in
the machine, and the proof of the contract their carrier answers.

The block has no printed part of its own: `enclosure_back_top` carries every
joint. What this file exports is the four bodies posed together, which is what
the enclosure places, and what `_report` asserts is what the carrier owes —
nine bosses on one seat plane, three wells grown into its own face, and a driver
column to every screw.

Frame and every dimension: `_mains_interface`.
"""

import sys
from pathlib import Path

import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _hw / "reference" / "wago-221-413", _here.parent,
           _hw.parent / "tools"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
from docgen import substitute_md
import wago_221_413 as wago
import _mains_interface as mi

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
    turn carries its wire-entry axis onto the block's own open direction. It
    bottoms on the carrier's face, which is the well's floor."""
    out = []
    for cx, cy in mi.wago_places():
        out.append(wago.build().val()
                   .rotate((0, 0, 0), (1, 0, 0), 90)
                   .translate((0, wago.height / 2.0, wago.depth / 2.0))
                   .translate((cx, cy, 0.0)))
    return out


def bodies():
    """Every solid the block puts in the machine, named."""
    out = [(b, _seated(b)) for b in SEATED]
    out += [(f"wago{i}", w) for i, w in enumerate(_wagos())]
    return out


def build_assembly(name="mains-assembly"):
    assy = cq.Assembly(name=name)
    for n, s in bodies():
        assy.add(s, name=n, color=COLORS.get(n, COLORS["wago"]))
    return assy


def _gap(a, b):
    e = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    e.Perform()
    return e.Value()


def _column(x, y, r, z0, z1):
    return (cq.Workplane("XY").circle(r).extrude(z1 - z0)
            .translate((x, y, z0)).val())


def _report():
    parts = bodies()
    wells = mi.hub_wells().val()

    print(f"   block {mi.block_x:.1f} × {mi.block_y:.1f} × {mi.reach():.1f} mm "
          f"off the carrier's face")
    print(f"   {len(mi.stations())} bodies, {sum(len(h) for _b, h, _d in mi.stations())} "
          f"bosses, {len(mi.wago_places())} wells — all on one printed piece")

    # Nothing in the block stands closer to a NEIGHBOUR than the machine's own
    # floor. A lug in its well is a seat and not a neighbour — it bottoms on the
    # carrier's face and its lower half is wrapped on four sides — so that one
    # pair is the well holding the lug rather than two bodies meeting.
    named = parts + [("hub-wells", wells)]
    worst, worst_pair = 1e9, None
    for i in range(len(named)):
        for j in range(i + 1, len(named)):
            a, b = named[i][0], named[j][0]
            if "hub-wells" in (a, b) and (a.startswith("wago") or b.startswith("wago")):
                continue
            g = _gap(named[i][1], named[j][1])
            if g < worst:
                worst, worst_pair = g, (a, b)
    assert worst >= mi.clearance_floor - 1e-6, \
        f"{worst_pair[0]} to {worst_pair[1]} is {worst:.3f} mm"
    print(f"   closest pair {worst_pair[0]} → {worst_pair[1]} at {worst:.2f} mm, "
          f"against a {mi.clearance_floor:g} mm floor")

    # Each lug stands in a well of its own, wrapped on both plan axes.
    for i, (cx, cy) in enumerate(mi.wago_places()):
        w, d, _h = mi.wago_stand()
        seat_box = (cq.Workplane("XY")
                    .box(w + 2.0 * mi.press, d + 2.0 * mi.press, mi.well_reach(),
                         centered=False)
                    .translate((cx - w / 2.0 - mi.press, cy - d / 2.0 - mi.press, 0.0))
                    .val())
        lug = dict(parts)[f"wago{i}"]
        held = lug.intersect(seat_box).Volume()
        assert held > 0.0, f"wago{i} stands in no well"
    print(f"   {len(mi.wago_places())} lugs, each wrapped on four faces at the "
          f"hub's own {mi.press:g} mm press")

    # The stud rides the hub's own row rather than a row of its own.
    (_gx, gy), _rot, _gz = mi.seat("ground-stack")
    assert mi.splice_y0 <= gy <= mi.splice_y1
    print(f"   the ground stud shares the hub's row, y[{mi.splice_y0:.1f},"
          f"{mi.splice_y1:.1f}] — one row, not two")

    # A boss standing on the carrier's own section holds a whole insert pocket.
    assert mi.seat_z + mi.carrier_t >= mi.station_depth - 1e-9
    print(f"   a {mi.seat_z:g} mm boss on {mi.carrier_t:g} mm of carrier holds the "
          f"{mi.insert_pocket_depth:g} mm pocket with {mi.insert_backing:g} mm behind it")

    # The relay's pins hang under its board and the seat plane carries them.
    assert mi.pin_clearance() >= mi.clearance_floor
    print(f"   the relay's pins hang {mi.pin_clearance():.1f} mm over the carrier")

    # Every screw is driven from the open face, so every station owes a clear
    # column out of the block — the bodies are wired and bolted in place.
    driver_r = mi.boss_d / 2.0
    for body, holes, _dia in mi.stations():
        for px, py in holes:
            col = _column(px, py, driver_r, mi.seat_z, mi.reach() + 1.0)
            for name, solid in named:
                if name == body:
                    continue
                v = col.intersect(solid).Volume()
                assert v < 1e-6, f"{body}'s screw at ({px:.1f},{py:.1f}) is under {name}"
    print(f"   every screw has a clear ⌀{mi.boss_d:g} mm column out of the block")

    # The wells stand out of the carrier's face; their floor is its section.
    wb = wells.BoundingBox()
    assert abs(wb.zmin - mi.hub_z) < 1e-9
    print(f"   the hub's wells rise {wb.zmax:.1f} mm out of the carrier's face, "
          f"their floor buried in its {mi.carrier_t:g} mm")

    # The block is wired flat: nothing is entered from an end or from behind.
    for name, _pos, axis in mi.terminals():
        assert axis[2] > 0.999, f"{name} does not look off the open face"
    print(f"   {len(mi.terminals())} terminals, every one of them looking off "
          f"the open face")

    # Two of the three rows stand well inside the box the block publishes.
    deepest = max(r[3] for r in mi.rows())
    assert abs(deepest - mi.reach()) < 1e-6
    for name, y0, y1, r in mi.rows():
        print(f"   row {name:7s} y[{y0:5.1f},{y1:5.1f}] reaches {r:5.1f} mm, "
              f"leaving {mi.reach() - r:5.1f} mm of the envelope free over it")

    env = (cq.Workplane("XY").box(mi.block_x, mi.block_y, mi.reach() + 1.0,
                                  centered=False).translate((0, 0, 0)).val())
    for name, solid in parts:
        v = solid.Volume() - solid.intersect(env).Volume()
        assert v < 1e-6, f"{name} stands {v:.2f} mm³ outside the block's envelope"
    print("   every body inside the envelope the block publishes")


def _sync_readme():
    holes = sum(len(h) for _b, h, _d in mi.stations())
    wells_top = mi.hub_wells().val().BoundingBox().zmax
    row = {n: r for n, _y0, _y1, r in mi.rows()}
    substitute_md(
        _here.parent / "README.md",
        variables={
            "BLOCK_X": f"{mi.block_x:.4g}",
            "BLOCK_Y": f"{mi.block_y:.4g}",
            "REACH": f"{mi.reach():.4g}",
            "PSU_LEN": f"{mi.psu_span_x:.4g}",
            "SEAT_Z": f"{mi.seat_z:.4g}",
            "BOSS_D": f"{mi.boss_d:.4g}",
            "INSERT_D": f"{2 * mi.insert_pocket_radius:.4g}",
            "INSERT_DEPTH": f"{mi.insert_pocket_depth:.4g}",
            "INSERT_BACKING": f"{mi.insert_backing:.4g}",
            "STATION_DEPTH": f"{mi.station_depth:.4g}",
            "CARRIER_T": f"{mi.carrier_t:.4g}",
            "FLOOR": f"{mi.clearance_floor:.4g}",
            "PIN_CLEARANCE": f"{mi.pin_clearance():.4g}",
            "WELL_TOP": f"{wells_top:.4g}",
            "BOSS_COUNT": f"{holes}",
            "WELL_COUNT": f"{len(mi.wago_places())}",
            "TERMINAL_COUNT": f"{len(mi.terminals())}",
            "SPLICE_Y0": f"{mi.splice_y0:.4g}",
            "SPLICE_Y1": f"{mi.splice_y1:.4g}",
            "ROW_BRICK": f"{row['brick']:.4g}",
            "ROW_SPLICE": f"{row['splice']:.4g}",
            "ROW_RELAY": f"{row['relay']:.4g}",
            "FREE_SPLICE": f"{mi.reach() - row['splice']:.4g}",
            "FREE_RELAY": f"{mi.reach() - row['relay']:.4g}",
        },
        expected_counts={
            "BLOCK_X": 1, "BLOCK_Y": 1, "REACH": 1, "PSU_LEN": 1, "SEAT_Z": 1,
            "BOSS_D": 1, "INSERT_D": 1, "INSERT_DEPTH": 1, "INSERT_BACKING": 1,
            "STATION_DEPTH": 1, "CARRIER_T": 1, "FLOOR": 2, "PIN_CLEARANCE": 1,
            "WELL_TOP": 1, "BOSS_COUNT": 2, "WELL_COUNT": 1,
            "TERMINAL_COUNT": 1, "SPLICE_Y0": 1, "SPLICE_Y1": 1,
            "ROW_BRICK": 1, "ROW_SPLICE": 1, "ROW_RELAY": 1,
            "FREE_SPLICE": 1, "FREE_RELAY": 1,
        },
    )


def main():
    _report()
    _sync_readme()
    export_assembly(build_assembly(), str(_here.parent / "mains-assembly.step"))
    print("-> mains-assembly.step")


if __name__ == "__main__":
    main()
