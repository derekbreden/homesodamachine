"""The evaporator coil, wound on the tank, with the two tails that leave it.

`coil-mandrel` is the tool the copper is wound ON — a cylinder undersized by `net_undersize` so
the wrap springs out and clamps the tank when it comes off. This module is the copper AFTER
that: at the radius it actually sits at, one tube radius off the tank's own OD, and lifted
again wherever the reed bridge carries it (`_ride_radius`). `wrap_length` is therefore the
copper a build CONSUMES, which is the figure `bom.md` §5 bills — longer than either of the
mandrel's two.

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
for _p in (_hw / "scripts", _cold, _cold / "coil-mandrel", _cold / "copper-plugs",
           _cold / "reed-bridge", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import coil_mandrel as _mandrel                          # noqa: E402
import copper_plugs as _plugs                            # noqa: E402
import reed_bridge as _bridge                            # noqa: E402
from _cold_core_interface import (                       # noqa: E402
    evap_tail_high_z,
    evap_tail_low_z,
    tank_outer_radius,
    tank_support_ring_height,
    wall_and_floor_thickness,
)
from _routing import stock_min, stock_of                 # noqa: E402
import _internal_routes as _R                            # noqa: E402
import _stated_bounds as _bounds                         # noqa: E402

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


# THE WRAP DOES NOT LIE ON THE TANK ALL THE WAY ROUND. The reed bridge stands on the register
# azimuth carrying the two carbonator reeds in pockets `reed_bridge.pocket_depth` proud of the
# wall, and the copper crossing it rides the bridge's own plateau — which is what leaves the
# glass its `copper_clearance_over_glass`. The lift, the arc it runs over and the ramps either
# side are all the BRIDGE's figures; this reads them and rides what they leave.
# HOW LONG THE COPPER TAKES TO COME UP, and it is not how long the BRIDGE takes. A rise of
# `BRIDGE_LIFT` eased over a path of `L` turns at its steepest through a radius of
# L² / (lift · π²/2), and a 1/4" ACR tube will not turn tighter than `COPPER_BEND`. So the ramp
# on and off is as long as that floor asks — longer than the bridge's own printed ramps, in
# both directions, because PETG can step where copper cannot.
BRIDGE_LIFT = _bridge.plateau_radius - tank_outer_radius
BRIDGE_RAMP = math.sqrt(COPPER_BEND * BRIDGE_LIFT * math.pi ** 2 / 2.0)
BRIDGE_ARC_RUNOUT = math.degrees(BRIDGE_RAMP / _bridge.plateau_radius)
# What the copper's INNER surface rides on, by azimuth off the register line. A bent tube
# BRIDGES the bridge's own arc ramps rather than following them down, so it holds the plateau
# all the way to the bridge's edge and comes back to the tank outside it.
RIDE_RADII = ((math.degrees(_bridge.bridge_half_angle), _bridge.plateau_radius),
              (math.degrees(_bridge.bridge_half_angle) + BRIDGE_ARC_RUNOUT, tank_outer_radius))
# The bridge is authored in the TANK's own frame, one floor slab and one support ring up.
_tank_bottom_z = wall_and_floor_thickness + tank_support_ring_height
BRIDGE_Z = (_bridge.bridge_z_bottom + _tank_bottom_z,
            _bridge.bridge_z_top + _tank_bottom_z)
BRIDGE_AXIAL_RAMP = max(_bridge.axial_ramp_length, BRIDGE_RAMP)
# How finely the wrap is sampled. Enough that the ramps read as ramps and the sampled circle
# carries the tube's own surface (`wrap_points` swells for the rest), and no finer: every body
# in the pack is met with this one, and a spline with a thousand poles is felt on every build.
WRAP_SAMPLES_PER_TURN = 96
# The bridge stands on the register azimuth, which is the shell's +X.
_bridge_azimuth = 0.0


def _ease(t: float) -> float:
    """A 0→1 ramp with no corner at either end.

    A tube does not turn a corner, and a curve drawn THROUGH points that do overshoots at one:
    the wrap would dip inside the tank just off the bridge's edge. Easing the ramp is what
    keeps the drawn surface where the copper is."""
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def _ride_radius(azimuth_deg: float, z: float) -> float:
    """The copper CENTRELINE's radius at one point of the wrap.

    Off the bridge it is `WIND_R`. Over it, the tube's inner surface stands on whatever the
    bridge presents at that azimuth, and the two ends of the bridge's own axial ramp bring it
    up and down rather than stepping."""
    a = abs(((azimuth_deg - _bridge_azimuth + 180.0) % 360.0) - 180.0)
    surface = tank_outer_radius
    for i, (edge, radius) in enumerate(RIDE_RADII):
        if a <= edge:
            if i == 0:
                surface = radius
            else:
                lo_edge, lo_r = RIDE_RADII[i - 1]
                surface = lo_r + (radius - lo_r) * _ease((a - lo_edge) / (edge - lo_edge))
            break
    z0, z1 = BRIDGE_Z
    axial = _ease(min((z - (z0 - BRIDGE_AXIAL_RAMP)) / BRIDGE_AXIAL_RAMP,
                      ((z1 + BRIDGE_AXIAL_RAMP) - z) / BRIDGE_AXIAL_RAMP))
    return WIND_R + axial * max(0.0, surface - tank_outer_radius)


def wrap_points() -> list:
    """The wrap's centreline, sampled — clocked so it starts on the inlet tail's own azimuth
    and lifted where the bridge carries it."""
    n = max(2, int(round(TOTAL_WRAPS * WRAP_SAMPLES_PER_TURN)))
    # A curve THROUGH sampled points runs inside the circle those points sit on, by the
    # sagitta of one step. Sampling on a circle that much larger puts the drawn surface back
    # on the tank instead of a hair inside it.
    swell = 1.0 / math.cos(math.pi * TOTAL_WRAPS / n)
    pts = []
    for i in range(n + 1):
        turn = TOTAL_WRAPS * i / n
        az = AZ_IN + 360.0 * turn
        z = evap_tail_low_z + PITCH * turn
        pts.append(_at(az, z, _ride_radius(az, z) * swell))
    return pts


def helix_wire() -> cq.Wire:
    """The wrap's centreline as one wire — the NOMINAL circle, clocked so it starts on the
    inlet tail's own azimuth.

    THE DRAWN BODY IS THE CIRCLE, NOT THE LAID PATH. The lift over the reed bridge is real and
    `wrap_length` bills it, but a body swept along a spline that rises and falls ten times costs
    ~50 s in every boolean it meets, and this one is met by every body in the pack — an hour a
    build, on a 3 mm excursion over 0.7 % of the wrap. So the SOLID is the exact helix and
    `cold_core_assembly.RIDES_ON` is where the three bodies that lift are named."""
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
    """What a build CUTS for the wrap — the laid path, bridge lift and all.

    `wrap_points` is the centreline the copper actually takes, so this is longer than the
    drawn body's own circle by whatever riding the bridge costs. `bom.md` §5 bills this."""
    pts = wrap_points()
    return sum((pts[i + 1] - pts[i]).Length for i in range(len(pts) - 1))


def bridge_lift_length() -> float:
    """How much of `wrap_length` the bridge alone adds."""
    return wrap_length() - TOTAL_WRAPS * math.hypot(2 * math.pi * WIND_R, PITCH)


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


# WHAT THE CUT ALLOWS, AGAINST WHAT THE TAILS ACTUALLY TAKE. A tie-in allowance is that end's
# in-shell run plus what protrudes past the plug for the braze, and `coil_mandrel` writes the
# in-shell half down as a constant because this module imports THAT one and not the reverse.
# Here is where the two can be read together: a tail re-routed longer than its written figure
# is copper the cut never allowed for, and the stub pays for it out of the protrusion the
# brazier needs. The bound says so on the card rather than raising — `_stated_bounds` says why.
STUB_TAIL_TOL = 1.0

_tails_billed = _bounds.bound(
    "stub-tails-billed",
    "Each coil tail's in-shell run is the one its stub allowance bills",
    f"within {STUB_TAIL_TOL:.1f} mm of `coil_mandrel.tail_in_shell`")
for _end, _billed in _mandrel.tail_in_shell.items():
    _drawn = tail_length(_end)
    _tails_billed(
        abs(_drawn - _billed) <= STUB_TAIL_TOL,
        f"{_end} tail draws {_drawn:.1f} mm against the {_billed:.1f} mm "
        f"`coil_mandrel.tail_in_shell` bills — {_drawn - _billed:+.1f} mm out of the "
        f"{_mandrel.stub_protrusion[_end]:.0f} mm that end has to protrude with")


def cut_length() -> float:
    """What a build CUTS per vessel — the laid wrap plus each end's own tie-in allowance.

    Struck here rather than in `coil_mandrel` because the wrap it stands on is the LAID one,
    and the reed bridge's lift is only visible from this module."""
    return wrap_length() + _mandrel.stub_total


def roll_spare_ft() -> float:
    """What one roll has left after `coil_mandrel.vessels_per_roll` vessels come off it."""
    return _mandrel.roll_length_ft - _mandrel.vessels_per_roll * cut_length() / 304.8


def report() -> None:
    wrap = wrap_length()
    print("  evaporator coil")
    print(f"    stock           {COPPER_STOCK.name}, min bend {COPPER_BEND:.2f} — "
          f"{COPPER_STOCK.source}")
    print(f"    wound at        r {WIND_R:.3f} (tank {tank_outer_radius:.1f} + tube "
          f"{TUBE_R:.3f}); the mandrel winds at r {_mandrel.helix_path_radius:.3f}")
    print(f"    wraps           {TOTAL_WRAPS:.3f} at {PITCH:.4g} mm pitch, "
          f"z {evap_tail_low_z:.1f}..{evap_tail_high_z:.1f}")
    print(f"    azimuths        inlet {AZ_IN:+.2f}°, outlet {AZ_OUT:+.2f}°, "
          f"CCW delta {_mandrel.tail_ccw_delta:.2f}°")
    # Three readings of one length: what the mandrel holds, what the same wraps come to once
    # sprung onto the tank, and what THIS module draws with the reed bridge's lift in it.
    print(f"    wrap laid       {wrap:.0f} mm ({wrap / 304.8:.2f} ft) — mandrel "
          f"{_mandrel.mandrel_wrap_length:.0f}, sprung {_mandrel.fitted_wrap_length:.0f}, "
          f"reed bridge {bridge_lift_length():+.0f}")
    for end in ("inlet", "outlet"):
        print(f"    {end + ' stub':15} {_mandrel.stub_allowance[end]:.1f} mm allowed = "
              f"{tail_length(end):.1f} mm drawn in-shell "
              f"({_mandrel.tail_in_shell[end]:.1f} billed) + "
              f"{_mandrel.stub_protrusion[end]:.0f} protruding")
    cut = cut_length()
    print(f"    cut per vessel  {cut:.1f} mm ({cut / 304.8:.3f} ft); "
          f"{_mandrel.vessels_per_roll} per {_mandrel.roll_length_ft:.0f} ft roll leaves "
          f"{roll_spare_ft():+.3f} ft ({roll_spare_ft() * 304.8:+.0f} mm)")


if __name__ == "__main__":
    report()
