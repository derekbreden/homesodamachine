"""What stands inside the vessel and inside each pocket: the sparge stack, both floor
bulkheads, the level-sensing columns, and the two 1-wire probes.

Every station here is read off the part that owns it. The reservoir rod is at `reservoir.py`'s
own `rod_position_x` / `rod_position_y`; the reed column stands in the channel
`_reed_channels` carves; the carbonator's two reeds sit at the heights `reed_bridge` cuts its
pockets at; the sparge hangs off the bottom plate's lane-side port.

THE ONE SET OF STATIONS THIS FILE STRIKES ITSELF is where each reservoir's four reeds sit
along its column. `level-sensing.md` states the float's useful travel and the pitch that
spans it — the soldering is what fixes them on the real column — so `reservoir_reed_z` lays
four at that pitch, centred in that travel, and `report` prints what it laid.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_cold = _hw / "printed-parts" / "cold-core"
for _p in (_hw / "scripts", _cold, _cold / "reservoir", _cold / "reed-bridge", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _fittings as F                                    # noqa: E402
import _vessel as _V                                     # noqa: E402
import _coil as _C                                       # noqa: E402
import reservoir as _res                                 # noqa: E402
import reed_bridge as _bridge                            # noqa: E402
import _internal_routes as _R                            # noqa: E402
from _cold_core_interface import (                       # noqa: E402
    bag_pocket_outermost_x,
    bulkhead_elbow_bottom_z,
    bulkhead_elbow_exit_z,
    reed_x_depth,
    reservoir_bulkhead_port_x,
    tank_outer_radius,
)
from _reed_channels import reed_y_center, reeds_per_reservoir   # noqa: E402

_ref = _hw / "reference" / "jg-pp010822e"
sys.path.insert(0, str(_ref))
import jg_pp010822e as _ptc                              # noqa: E402


# --- the three collets made up on vessel elbows ------------------------------
#
# `bom.md` §3, §4 and §9 each carry a PP010822E that lands on one of the vessel's own elbows.
# The shank threads the elbow's socket and the collet stands outside it, so a line that used to
# start at the elbow's mouth starts at the collet's.
PTC_STANDOFF = _ptc.COLLET_LENGTH + _ptc.HEX_LENGTH
PTC_PORTS = ("co2-in", "carb-water-out", "water-in")


def collet_on(mouth):
    """One PP010822E made up on a mouth: `(solid, the mouth it now presents)`."""
    out = cq.Vector(*mouth.axis).normalized()
    origin = cq.Vector(*mouth.pos) + out.multiply(PTC_STANDOFF)
    solid = F.stand_x_along(cq.importers.importStep(str(_ref / "jg-pp010822e.step")).val(),
                            at=origin, axis=-out)
    return solid, F.Mouth(tuple(origin), tuple(out), _ptc.TUBE_D)


def vessel_collets() -> dict:
    """Each vessel port's collet, name → `(solid, mouth)`."""
    vm = _V.mouths()
    return {name: collet_on(vm[name]) for name in PTC_PORTS}

# --- the sparge stack, inside the vessel over the bottom plate ---------------
#
# The barb threads the bottom plate's lane-side port from the INSIDE and faces up the column.
# The stone sits on the vessel's own axis a `STONE_STANDOFF` off the plate, and the silicone
# stub arcs over from the barb to its stem — so the gas enters under the whole column and rises
# the length of it, at every level the float reads.
SILICONE_R = 0.5 * 6.35        # 1/4" ID silicone, drawn at the bore it carries
SILICONE_BEND = 3.0 * SILICONE_R
STONE_STANDOFF = 2.0
# The stone is a ⌀2" disc and the port it feeds stands `vessel_port_offset` off the axis, so a
# stone centred on the axis reaches the barb. It sits across the axis from the port instead,
# far enough that its rim clears the barb's own hex.
STONE_Y = 18.0


def _sparge_stem_top() -> float:
    return _V.interior_z[0] + STONE_STANDOFF + F.STONE_H + F.STONE_STEM_LEN


def sparge_stub_points() -> list:
    """The silicone's centreline: up out of the barb, over the plate, down onto the stem."""
    y = _V.PORTS["co2-in"]["y"]
    barb_tip_z = _V.interior_z[0] + F.BARB_HEX_H + F.BARB_LEN
    crest = max(barb_tip_z, _sparge_stem_top()) + SILICONE_BEND
    return [(0.0, y, barb_tip_z),
            (0.0, y, crest),
            (0.0, STONE_Y, crest),
            (0.0, STONE_Y, _sparge_stem_top())]


def sparge_stack() -> dict:
    """Barb, silicone stub and stone, standing on the bottom plate's inner face."""
    y = _V.PORTS["co2-in"]["y"]
    barb, _mouth = F.hose_barb(at=(0.0, y, _V.interior_z[0]), axis=(0.0, 0.0, 1.0))
    stub = _R.build_route(sparge_stub_points(), SILICONE_BEND, SILICONE_R)
    stone = F.sparge_stone(at=(0.0, STONE_Y, _sparge_stem_top()), axis=(0.0, 0.0, -1.0))
    return {"sparge-barb": barb, "sparge-silicone-stub": stub, "sparge-stone": stone}


def sparge_top_z() -> float:
    """The stone's own crown — what the liquid line has to stand over."""
    return _V.interior_z[0] + STONE_STANDOFF + F.STONE_H


def sparge_stub_length() -> float:
    return _R.route_wire(sparge_stub_points(), SILICONE_BEND).Length()


# --- both reservoirs' floor bulkheads ----------------------------------------
#
# The PureSec barrel rises through the trough floor on the bulkhead axis and its integral
# elbow turns the syrup line onto the run `_internal_routes` draws out of the pocket, so the
# collet is clocked by that line the same way the vessel's sockets are.
BULKHEAD_LINES = {"reservoir-a": "reservoir-a", "reservoir-b": "reservoir-b"}
# The elbow's own half-height, read off the band `_cold_core_interface` gives it: the
# lateral port's centre at `bulkhead_elbow_exit_z` over the lowest hardware at
# `bulkhead_elbow_bottom_z`, which is what leaves the pocket floor its clearance.
BULKHEAD_COLLET_R = bulkhead_elbow_exit_z - bulkhead_elbow_bottom_z


def _bulkhead_out(line: str) -> tuple:
    pts = _R.routes[line]
    return tuple(cq.Vector(*pts[1]).sub(cq.Vector(*pts[0])).normalized().toTuple())


def _bulkhead_corner(line: str) -> tuple:
    x = reservoir_bulkhead_port_x if line == "reservoir-a" else -reservoir_bulkhead_port_x
    return (x, 0.0, bulkhead_elbow_exit_z)


def trough_floor_z(reservoir_solid, x: float) -> float:
    """The top of one pocket's trough floor on the bulkhead's own axis.

    The floor is bored ⌀16 for the barrel, so a probe on the axis passes clear; this samples a
    ring just outside that bore and takes the highest floor material under the wet V."""
    bb = reservoir_solid.BoundingBox()
    ring = (cq.Solid.makeCylinder(F.PURESEC_NUT_AF / 2, (bb.zmax - bb.zmin) / 3.0,
                                  cq.Vector(x, 0.0, bb.zmin), cq.Vector(0, 0, 1))
            .cut(cq.Solid.makeCylinder(F.PURESEC_BARREL_R, (bb.zmax - bb.zmin) / 3.0 + 2,
                                       cq.Vector(x, 0.0, bb.zmin - 1), cq.Vector(0, 0, 1))))
    hit = reservoir_solid.intersect(ring)
    return hit.BoundingBox().zmax if hit.Volume() > 1e-9 else bb.zmin


def reservoir_bulkheads(reservoirs: dict = None) -> dict:
    """Each pocket's floor bulkhead, name → `(solid, mouth)`.

    The barrel carries the trough floor it passes and the washer squeezed on top of it, so the
    nut lands on the wet side of both."""
    out = {}
    for name, line in BULKHEAD_LINES.items():
        corner = _bulkhead_corner(line)
        body = (reservoirs or {}).get(name)
        barrel = None
        if body is not None:
            # The nut lands on the wet side of the seal, so the barrel carries the
            # floor it passes AND the washer squeezed on top of it.
            barrel = max(F.PURESEC_BARREL_LEN,
                         trough_floor_z(body, corner[0]) - corner[2] + F.WASHER_T)
        out[name] = F.puresec_elbow(corner=corner, up=(0, 0, 1), out=_bulkhead_out(line),
                                    barrel_len=barrel, collet_r=BULKHEAD_COLLET_R)
    return out


# --- level sensing -----------------------------------------------------------
#
# The carbonator's float rides `_vessel`'s welded rod; each reservoir's rides the rod standing
# in its own printed boss. Every reed is vertical: a donut on a rod couples axially, and the
# glass sits in a pocket cut on that axis.
RES_ROD_X = _res.rod_position_x
RES_ROD_Y = _res.rod_position_y
RES_ROD_LEN = _res.reservoir_rod_len


def rod_seat_z(reservoir_solid, x: float) -> float:
    """Where one reservoir's rod bottoms — the blind bore's floor in its anchor boss.

    `reservoir.py` strikes the boss off a sloping wet floor, so the seat follows that slope.
    Probing the part on the rod's own axis is what reads it, and a boss that moves carries its
    rod with it."""
    bb = reservoir_solid.BoundingBox()
    probe = cq.Solid.makeCylinder(
        _V.ROD_D / 2, (bb.zmin + bb.zmax) / 2.0 - bb.zmin + 1,
        cq.Vector(x, RES_ROD_Y, bb.zmin - 1), cq.Vector(0, 0, 1))
    hit = reservoir_solid.intersect(probe)
    return hit.BoundingBox().zmax if hit.Volume() > 1e-9 else bb.zmin

# The reed column's own x — the middle of the channel `_reed_channels` carves outward from the
# pocket's far ±X wall.
REED_COLUMN_X = bag_pocket_outermost_x + reed_x_depth / 2.0
# `level-sensing.md`: the float's useful travel on the rod, floor-side above the wet slope to
# just under the cap, and the pitch four reeds span it at.
FLOAT_TRAVEL_Z = (40.0, 210.0)
RESERVOIR_REED_PITCH = 45.0


def reservoir_reed_z() -> tuple:
    """The four stations along one reservoir's column, centred in the float's travel."""
    span = (reeds_per_reservoir - 1) * RESERVOIR_REED_PITCH
    mid = sum(FLOAT_TRAVEL_Z) / 2.0
    return tuple(mid - span / 2.0 + i * RESERVOIR_REED_PITCH
                 for i in range(reeds_per_reservoir))


def carbonator_reed_z() -> tuple:
    """The bridge's own two pockets, carried into the shell's frame."""
    return (_bridge.reed_low_z + _V.tank_bottom_z, _bridge.reed_high_z + _V.tank_bottom_z)


def carbonator_reed_x() -> float:
    """The reeds sit against bare 316L on the register azimuth, so their glass stands one
    radius out from the tank wall inside the bridge that holds them."""
    return tank_outer_radius + F.REED_GLASS_R


# --- where a float rides -----------------------------------------------------
#
# EVERY REED IN THIS MACHINE READS THROUGH A WALL, and magnetic coupling falls off fast across
# one. So a float is not placed on its rod's axis — it is placed against the wall its own reed
# column stands behind, and the rod is parked OUTBOARD of where a concentric float would touch
# so the wall has to push back. `endcap_circular_dxf.magnet_wall_bias` is that overhang on the
# carbonator and `reservoir.rod_position_x` is it on a pocket; `reed_bridge.donut_wall_bias`
# reads the same figure off the plate.
#
# What lets a rod be parked past the wall is that the float is a LOOSE capsule: the donor's
# ⌀9.75 bore over a ⌀3.175 rod gives `FLOAT_SLOP` of radial freedom, and the park spends it.
# `float_standoff` is what is left — the most the magnet can retreat from the wall anywhere in
# the travel, and the figure the reed has to read at.
FLOAT_SLOP = (F.FLOAT_BORE - _V.ROD_D) / 2.0
# `reservoir/level-sensing.md`, measured on the bench against both walls: the reed trips
# reliably with the magnet within ~2 mm of its wall and gives nothing by ~3 mm off.
MAGNET_WALL_REACH = 2.0


def float_ride(park: float, wall: float) -> tuple:
    """One float on a rod parked `park` from the wall's own origin, riding a wall at `wall`.

    Returns `(centre, standoff)`: how far off that origin the capsule's axis actually lies, and
    the most its magnet can stand off the wall. A negative standoff is a capsule that cannot
    get onto the rod inside the wall at all."""
    touching = wall - F.FLOAT_OD / 2.0
    return min(park + FLOAT_SLOP, touching), touching - (park - FLOAT_SLOP)


def reservoir_wall_x(reservoir_solid, side: int) -> float:
    """The |x| of the far wall one pocket's float rides, probed outward on the rod's own line.

    The reed column stands outside this wall (`REED_COLUMN_X`), so it is the wall the magnet
    has to be against. Reading it off the part is what keeps a wall that moves carrying its
    float with it. Both pockets are the same part mirrored, so the probe walks `side`."""
    step = 0.05
    bb = reservoir_solid.BoundingBox()
    far = bb.xmax if side > 0 else bb.xmin
    reach = RES_ROD_X
    while reach < abs(far) + step:
        x = side * reach
        bar = cq.Solid.makeBox(step, 1.0, 1.0,
                               cq.Vector(min(x, x + side * step), RES_ROD_Y - 0.5,
                                         sum(FLOAT_TRAVEL_Z) / 2.0 - 0.5))
        if reservoir_solid.intersect(bar).Volume() > 1e-9:
            return reach
        reach += step
    return abs(far)


def float_seats(reservoirs: dict = None) -> dict:
    """Every float, and the wall it lies against: name → `(park, wall, centre, standoff)`.

    One row per float, in the frame its own wall's origin is on — the tank's axis for the
    carbonator, the pocket's own centre plane for a reservoir. `cold_core_assembly` grades
    these; `report` prints them."""
    out = {}
    park, wall = _V.ROD_X, _V.TUBE_ID / 2.0
    centre, standoff = float_ride(park, wall)
    out["float-carb"] = (park, wall, centre, standoff)
    for name, side in (("a", +1), ("b", -1)):
        body = (reservoirs or {}).get(f"reservoir-{name}")
        if body is None:
            continue
        wall = reservoir_wall_x(body, side)
        centre, standoff = float_ride(RES_ROD_X, wall)
        out[f"float-{name}"] = (RES_ROD_X, wall, centre, standoff)
    return out


def level_bodies(reservoirs: dict = None) -> dict:
    out = {}
    seats = float_seats(reservoirs)
    # The carbonator: one float on the welded rod, lying against the tube's bore on the
    # register azimuth, resting at the high threshold.
    out["float-carb"] = F.float_capsule(
        centre=(seats["float-carb"][2], 0.0, _bridge.high_level_z + _V.tank_bottom_z))
    for i, z in enumerate(carbonator_reed_z(), start=1):
        out[f"reed-carb-{i}"] = F.reed(centre=(carbonator_reed_x(), 0.0, z))

    # Each reservoir: its rod, its float, and four reeds in the shell's own channel.
    for name, side in (("a", +1), ("b", -1)):
        body = (reservoirs or {}).get(f"reservoir-{name}")
        z0 = rod_seat_z(body, side * RES_ROD_X) if body is not None else 0.0
        out[f"float-rod-{name}"] = cq.Solid.makeCylinder(
            _V.ROD_D / 2, RES_ROD_LEN,
            cq.Vector(side * RES_ROD_X, RES_ROD_Y, z0), cq.Vector(0, 0, 1))
        seat = seats.get(f"float-{name}")
        out[f"float-{name}"] = F.float_capsule(
            centre=(side * (seat[2] if seat else RES_ROD_X), RES_ROD_Y,
                    sum(FLOAT_TRAVEL_Z) / 2.0))
        for i, z in enumerate(reservoir_reed_z(), start=1):
            out[f"reed-{name}-{i}"] = F.reed(
                centre=(side * REED_COLUMN_X, reed_y_center, z))
    return out


def seals(reservoirs: dict = None) -> dict:
    """Each pocket's wet-side face seal, and the membrane in each cap's vent pocket."""
    out = {}
    for name, side in (("a", +1), ("b", -1)):
        body = (reservoirs or {}).get(f"reservoir-{name}")
        x = side * reservoir_bulkhead_port_x
        floor = trough_floor_z(body, x) if body is not None else bulkhead_elbow_exit_z
        out[f"bulkhead-seal-{name}"] = F.silicone_washer(centre=(x, 0.0, floor))
        out[f"vent-membrane-{name}"] = F.membrane(
            centre=(side * _res.vent_position_x, _res.vent_position_y,
                    _cap_z() + _res.vent_pocket_bottom_z))
    return out


def _cap_z() -> float:
    """Where a reservoir cap's own zero sits in the shell's frame."""
    return _R.reservoir_cap_top_z - _res.cap_total_height


# --- the two 1-wire probes ---------------------------------------------------
#
# `bom.md` §5. The tank probe (family 0x28) is foil-taped to the vessel OD; the coil probe
# (0x10) tucks under the tape at the wrap's suction end, which is the outlet tail's own.
# A TO-92 is a rounded square, so what stands it off the wall it is taped to is its half
# DIAGONAL rather than half its width.
PROBE_STANDOFF = F.TO92_W * 0.71


def probes() -> dict:
    tank_z = _C.gap_z_near(180.0, (_V.interior_z[0] + _V.interior_z[1]) / 2.0)
    tank_at = (-(tank_outer_radius + PROBE_STANDOFF), 0.0, tank_z)
    # One wrap back from the outlet tail, in the gap between two wraps and against the tank —
    # which is where the tape that holds it can reach it.
    coil_at = _C._at(_C.AZ_OUT, _C.gap_z_near(_C.AZ_OUT, _C.evap_tail_high_z - _C.PITCH),
                     tank_outer_radius + PROBE_STANDOFF).toTuple()
    return {"probe-tank-ds18b20": F.to92(centre=tank_at, axis=(0, 0, 1)),
            "probe-coil-ds18s20": F.to92(centre=coil_at, axis=(0, 0, 1))}


def bodies(reservoirs: dict = None) -> dict:
    out = {}
    out.update(sparge_stack())
    for name, (solid, _m) in vessel_collets().items():
        out[f"collet-{name}"] = solid
    for name, (solid, _m) in reservoir_bulkheads(reservoirs).items():
        out[f"bulkhead-{name}"] = solid
    out.update(level_bodies(reservoirs))
    out.update(seals(reservoirs))
    out.update(probes())
    return out


def mouths() -> dict:
    return {name: mouth for name, (_s, mouth) in reservoir_bulkheads().items()}


def report(reservoirs: dict = None) -> None:
    hi = _bridge.high_level_z + _V.tank_bottom_z
    lo = _bridge.low_level_z + _V.tank_bottom_z
    print("  internals")
    print(f"    sparge          barb on the bottom plate at y {_V.PORTS['co2-in']['y']:+.2f}; "
          f"stone crown z {sparge_top_z():.1f}, under the low line {lo:.1f} "
          f"and the high {hi:.1f}")
    print(f"    silicone stub   {sparge_stub_length():.1f} mm drawn against the "
          f"~{3 * 25.4:.0f} mm bom.md §2 bills")
    for name, m in sorted(mouths().items()):
        print(f"    {name:15} mouth ({m.pos[0]:+.1f}, {m.pos[1]:+.1f}, {m.pos[2]:.1f})")
    print(f"    carb reeds      z {', '.join(f'{z:.1f}' for z in carbonator_reed_z())} "
          f"at x {carbonator_reed_x():.2f}")
    print(f"    res reeds       z {', '.join(f'{z:.1f}' for z in reservoir_reed_z())} "
          f"at x ±{REED_COLUMN_X:.1f}, y {reed_y_center:.1f}, "
          f"{RESERVOIR_REED_PITCH:.0f} mm pitch in a "
          f"{FLOAT_TRAVEL_Z[0]:.0f}..{FLOAT_TRAVEL_Z[1]:.0f} travel")
    seats = ""
    if reservoirs:
        seats = ", seated at z " + ", ".join(
            f"{rod_seat_z(reservoirs[f'reservoir-{n}'], s * RES_ROD_X):.1f}"
            for n, s in (("a", 1), ("b", -1)) if f"reservoir-{n}" in reservoirs)
    print(f"    res rods        ⌀{_V.ROD_D:.3f} × {RES_ROD_LEN:.1f} at x ±{RES_ROD_X:.0f}, "
          f"y {RES_ROD_Y:.1f}{seats}")
    print(f"    float slop      ⌀{F.FLOAT_BORE:.2f} bore on a ⌀{_V.ROD_D:.3f} rod — "
          f"{FLOAT_SLOP:.3f} mm of radial freedom, against the {MAGNET_WALL_REACH:.1f} mm "
          f"the reed reads at")
    for name, (park, wall, centre, standoff) in sorted(float_seats(reservoirs).items()):
        print(f"    {name:15} rod parked {park:.3f}, wall {wall:.3f}, capsule lies at "
              f"{centre:.3f} — magnet stands off {standoff:+.3f} mm")


if __name__ == "__main__":
    report()
