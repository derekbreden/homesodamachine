"""The evaporator coil, wound on the tank, with the two tails that leave it.

`coil-mandrel` is the tool the copper is wound ON — a cylinder undersized by `net_undersize` so
the wrap springs out and clamps the tank when it comes off. This module is the copper AFTER
that, at the radius it actually sits at: one tube radius off the tank's own OD.

    winding radius   `tank_outer_radius + tube_radius`, the copper's centreline on the tank
    wraps            `coil_mandrel.total_wraps` — 9 full plus the fraction the tails' azimuths
                     span, which is the mandrel's own figure and stays its own
    z                `evap_tail_low_z` up to `evap_tail_high_z`, the bands the vessel's own
                     elbows leave clear above and below it

FRAMES. The mandrel is authored lying down, its own Y the cylinder axis and (x, z) the radial
plane. Standing it up on the shell's Z, `x → y` and `z → −x`. `_map_azimuth` is that turn and
`COIL_CLOCK` is the roll on top of it; both leave `tail_ccw_delta` alone, so the wrap count the
mandrel struck is the wrap count drawn here.

WHERE A TAIL GOES after the wrap: radially clear of the helix, DOWN its own column, onto its
lane at the height the wall lets it cross, and out. `copper_plugs.slot_station` is where each
crosses — the inlet's on the port lane, the outlet's on the west — and both stand at
`evap_cross_z`, well under the heights their wraps leave at. Which column each one falls down
is `FALL_IN_LANE`, and the two flanks answer differently.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_cold = _hw / "printed-parts" / "cold-core"
for _p in (_hw / "scripts", _cold, _cold / "coil-mandrel", _cold / "copper-plugs", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import coil_mandrel as _mandrel                          # noqa: E402
import copper_plugs as _plugs                            # noqa: E402
from _cold_core_interface import (                       # noqa: E402
    evap_tail_high_z,
    evap_tail_low_z,
    tank_outer_radius,
    wall_and_floor_thickness,
)
from _routing import stock_min, stock_of                 # noqa: E402
import _internal_routes as _R                            # noqa: E402

TUBE_R = _mandrel.tube_radius                       # 3.175 — 1/4" ACR copper
# The copper's centreline once it is off the mandrel and onto the tank: its inner surface on
# the tank's OD.
WIND_R = tank_outer_radius + TUBE_R
TOTAL_WRAPS = _mandrel.total_wraps
PITCH = _mandrel.pitch
COPPER_STOCK = stock_of("refrigerant", 2 * TUBE_R)
COPPER_BEND = stock_min("refrigerant", 2 * TUBE_R)

# How far a tail stands off the wrap before it turns for its lane — one bend radius, the
# shortest straight a turn off the helix can be seated in.
TAIL_LEAD = COPPER_BEND


def _map_azimuth(mandrel_x: float, mandrel_z: float) -> float:
    """One of the mandrel's radial points as an azimuth in the shell's frame, degrees CCW
    off +X."""
    return math.degrees(math.atan2(mandrel_x, -mandrel_z))


# HOW THE WOUND COIL IS CLOCKED ONTO THE TANK, degrees CCW. The mandrel says where the two
# tails sit RELATIVE TO EACH OTHER — `tail_ccw_delta` is its own figure and untouched here —
# and nothing says where that pair sits relative to the shell. A helix is the same helix at
# every roll, so this is one free turn, and it is the only thing that moves both tails without
# moving anything they have to clear.
#
# THE WINDOW IS 2.5° WIDE AND THE MANDREL'S OWN AZIMUTHS SIT IN THE MIDDLE OF IT, which is why
# the turn is zero. Swept against the placed solids at 0.05° over AZ_IN ∈ [−130°, −114°]:
#
#   AZ_IN < −124.5°   the inlet tail's fall meets reservoir A's pocket, whose centreward arc
#                     stands at r 78..80 and begins at azimuth ∓125°. The fall is at r 79.4,
#                     inside that band, so it only passes where the arc is not.
#   AZ_IN > −122.0°   the same wall on reservoir B, reached by the outlet tail's step out to
#                     the west lane — `tail_ccw_delta` carries it there 247.4° round.
#
# The carbonated water's riser used to close that window from the middle; it stands one column
# clear of it now (`_cold_core_interface.cap_conduits`, carb-water-out). What is left is
# measured on every build by `bodies-clear` and `lines-apart`, not restated.
COIL_CLOCK = 0.0

AZ_IN = _map_azimuth(_mandrel.tail_inlet_x, _mandrel.tail_inlet_z) + COIL_CLOCK
AZ_OUT = _map_azimuth(_mandrel.tail_outlet_x, _mandrel.tail_outlet_z) + COIL_CLOCK


def _at(azimuth_deg: float, z: float, radius: float = None) -> cq.Vector:
    r = WIND_R if radius is None else radius
    a = math.radians(azimuth_deg)
    return cq.Vector(r * math.cos(a), r * math.sin(a), z)


WIND_HEIGHT = evap_tail_high_z - evap_tail_low_z


def helix_wire() -> cq.Wire:
    """The wrap's centreline, clocked so it starts on the inlet tail's own azimuth."""
    helix = cq.Wire.makeHelix(PITCH, WIND_HEIGHT, WIND_R)
    return (helix.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), AZ_IN)
            .translate(cq.Vector(0, 0, evap_tail_low_z)))


def build_wrap() -> cq.Solid:
    """The helix as swept copper."""
    wire = helix_wire()
    profile = cq.Workplane(cq.Plane(origin=wire.startPoint(), normal=wire.tangentAt(0)))
    return profile.circle(TUBE_R).sweep(
        cq.Workplane("XY").newObject([wire]), isFrenet=True).val()


def wrap_length() -> float:
    """The drawn wrap's developed length — the helix arc at the radius it sits at."""
    return TOTAL_WRAPS * math.hypot(2 * math.pi * WIND_R, PITCH)


def gap_z_near(azimuth_deg: float, target_z: float) -> float:
    """A Z at `azimuth_deg` midway between two wraps, as near `target_z` as the pitch allows.

    What is taped to the tank sits against it, so it has to land in the copper's own gap."""
    turns = (target_z - evap_tail_low_z) / PITCH - (azimuth_deg - AZ_IN) / 360.0
    wrap_z = evap_tail_low_z + (math.floor(turns) + (azimuth_deg - AZ_IN) / 360.0) * PITCH
    return wrap_z + PITCH / 2.0


# WHICH COLUMN EACH TAIL FALLS DOWN, and it is not the same answer on the two flanks.
#
# A lane is one bore wide, so a run standing in one at every storey between its wrap and its
# station is a wall to anything crossing there. The PORT lane HAS such a crossing — the PRV
# vent, one pitch over this very copper (`copper_plugs.columns`) — so the inlet falls at the
# standoff radius it already turned out to and joins the lane only at the height it crosses
# the wall, where it is one storey among the others.
#
# THE WEST FLANK CANNOT DO THAT. Reservoir B's pocket closes the standoff annulus on that
# side: its centreward arc stands at r 80.0 against a fall at r 79.4, and there is no room
# between the wrapped coil at 69.85 and that arc for a ⌀6.35 tube with a lead long enough to
# seat its own corner. The west lane carries no storey between the outlet's two heights, so
# the outlet falls IN the lane — the one column open to it.
FALL_IN_LANE = {"inlet": False, "outlet": True}


def tail_points(which: str) -> list:
    """One tail's centreline: off the wrap, down its own column, onto its lane at the station's
    height, and out through the wall. `FALL_IN_LANE` says which column that is."""
    if which == "inlet":
        az, z0, station = AZ_IN, evap_tail_low_z, "evap-inlet"
    else:
        az, z0, station = AZ_OUT, evap_tail_high_z, "evap-outlet"
    (wall_x, lane_y, cross_z), _axis = _plugs.slot_station(station)

    start = _at(az, z0)
    # Radially out of the wrap far enough to turn in, then down its own column, then onto the
    # lane's own y at the crossing height, then out through the wall.
    lead = _at(az, z0, WIND_R + TAIL_LEAD)
    fall_y = lane_y if FALL_IN_LANE[which] else lead.y
    return [
        (start.x, start.y, start.z),
        (lead.x, lead.y, lead.z),
        (lead.x, fall_y, z0),
        (lead.x, fall_y, cross_z),
        (lead.x, lane_y, cross_z),
        (wall_x - wall_and_floor_thickness, lane_y, cross_z),
    ]


def build_tail(which: str):
    """One tail drawn at the copper's own arc: `(bend_radius, solid)`."""
    return _R.route_bend_radius, _R.build_route(tail_points(which), COPPER_BEND, TUBE_R)


def bodies() -> dict:
    return {
        "evap-coil": build_wrap(),
        "evap-tail-inlet": _R.build_route(tail_points("inlet"), COPPER_BEND, TUBE_R),
        "evap-tail-outlet": _R.build_route(tail_points("outlet"), COPPER_BEND, TUBE_R),
    }


def tail_length(which: str) -> float:
    return _R.route_wire(tail_points(which), COPPER_BEND).Length()


def report() -> None:
    wrap = wrap_length()
    tails = tail_length("inlet") + tail_length("outlet")
    print("  evaporator coil")
    print(f"    stock           {COPPER_STOCK.name}, min bend {COPPER_BEND:.2f} — "
          f"{COPPER_STOCK.source}")
    print(f"    wound at        r {WIND_R:.3f} (tank {tank_outer_radius:.1f} + tube "
          f"{TUBE_R:.3f}); the mandrel winds at r {_mandrel.helix_path_radius:.3f}")
    print(f"    wraps           {TOTAL_WRAPS:.3f} at {PITCH:.4g} mm pitch, "
          f"z {evap_tail_low_z:.1f}..{evap_tail_high_z:.1f}")
    print(f"    azimuths        inlet {AZ_IN:+.2f}°, outlet {AZ_OUT:+.2f}°, "
          f"CCW delta {_mandrel.tail_ccw_delta:.2f}°")
    # Two readings of one length: the wrap as this module draws it on the TANK, and the figure
    # `bom.md` §5 bills, which `coil_mandrel` strikes at the MANDREL's smaller radius.
    print(f"    wrap drawn      {wrap:.0f} mm ({wrap / 304.8:.2f} ft) against "
          f"{_mandrel.wrap_length:.0f} mm ({_mandrel.wrap_length / 304.8:.2f} ft) billed "
          f"— {wrap - _mandrel.wrap_length:+.0f} mm")
    print(f"    tails drawn     {tails:.0f} mm, against the "
          f"{2 * _mandrel.stub_allowance:.0f} mm of stub the cut allows")
    cut = wrap + 2 * _mandrel.stub_allowance
    print(f"    cut per vessel  {cut / 304.8:.2f} ft against {_mandrel.cut_length / 304.8:.2f} "
          f"ft billed; 3 per 50 ft roll leaves {50 - 3 * cut / 304.8:+.2f} ft")


if __name__ == "__main__":
    report()
