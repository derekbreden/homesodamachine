"""The evaporator coil, wound on the carbonator, with the two tails that leave it.

`coil-mandrel` is the undersized rough-forming aid. This module defines the
finished copper after diameter, pitch and turn count are set on the vessel
fixture: one tube radius off the carbonator OD, lifted over the reed bridge
by `_ride_radius`. `wrap_length` is therefore the
copper a build CONSUMES, which is the figure `bom.md` §5 bills — longer than either of the
mandrel's two.

    winding radius   `carbonator_outer_radius + tube_radius`, the copper's centreline on the carbonator
    wraps            9.5 finished right-hand turns, opposite tangent exits
    z                `evap_tail_low_z` up to `evap_tail_high_z`, the bands the carbonator's own
                     elbows leave clear above and below it

FRAME. The finished winding uses the cold core's Z axis and opposite -Y / +Y
helix exits. The undersized mandrel is a rough-forming aid; its groove and
springback do not define the finished turn count or copper consumption.

TAIL FORM. Both helix ends lie on the port axis, at -Y / +Y. A tangent
pitch roll-off and two opposite R15 plan bends take each tail to its lane.
The inlet uses an R15 vertical dogleg; the outlet uses two R15 quarter bends
and a straight drop. Every segment is tangent to the next. The two exits
retain their shell station and their -X axes.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_cold = _hw / "printed-parts" / "cold-core"
for _p in (_hw / "scripts", _cold, _cold / "coil-mandrel",
           _cold / "reed-bridge", _here.parent):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import coil_mandrel as _mandrel                          # noqa: E402
import _copper_ports as _copper                            # noqa: E402
import reed_bridge as _bridge                            # noqa: E402
from _cold_core_interface import (                       # noqa: E402
    evap_tail_high_z,
    evap_tail_low_z,
    carbonator_outer_radius,
    carbonator_support_ring_height,
    wall_and_floor_thickness,
)
from _routing import stock_min, stock_of                 # noqa: E402
import _stated_bounds as _bounds                         # noqa: E402

TUBE_R = _mandrel.tube_radius                       # 3.175 — 1/4" ACR copper
# The copper's centreline once it is off the mandrel and onto the carbonator: its inner surface
# on the carbonator's OD.
WIND_R = carbonator_outer_radius + TUBE_R
TOTAL_WRAPS = 9.5
COPPER_STOCK = stock_of("refrigerant", 2 * TUBE_R)
COPPER_BEND = stock_min("refrigerant", 2 * TUBE_R)

# Finished helix endpoints, degrees CCW from +X in the core frame.
AZ_IN, AZ_OUT = -90.0, 90.0


def _at(azimuth_deg: float, z: float, radius: float = None) -> cq.Vector:
    r = WIND_R if radius is None else radius
    a = math.radians(azimuth_deg)
    return cq.Vector(r * math.cos(a), r * math.sin(a), z)


WIND_HEIGHT = evap_tail_high_z - evap_tail_low_z
PITCH = WIND_HEIGHT / TOTAL_WRAPS


# THE WRAP DOES NOT LIE ON THE CARBONATOR ALL THE WAY ROUND. The reed bridge stands on the register
# azimuth carrying the two carbonator reeds in pockets `reed_bridge.pocket_depth` proud of the
# wall, and the copper crossing it rides the bridge's own plateau — which is what leaves the
# glass its `copper_clearance_over_glass`. The lift, the arc it runs over and the ramps either
# side are all the BRIDGE's figures; this reads them and rides what they leave.
# HOW LONG THE COPPER TAKES TO COME UP, and it is not how long the BRIDGE takes. A rise of
# `BRIDGE_LIFT` eased over a path of `L` turns at its steepest through a radius of
# L² / (lift · π²/2), and a 1/4" ACR tube will not turn tighter than `COPPER_BEND`. So the ramp
# on and off is as long as that floor asks — longer than the bridge's own printed ramps, in
# both directions, because PETG can step where copper cannot.
BRIDGE_LIFT = _bridge.plateau_radius - carbonator_outer_radius
BRIDGE_RAMP = math.sqrt(COPPER_BEND * BRIDGE_LIFT * math.pi ** 2 / 2.0)
BRIDGE_ARC_RUNOUT = math.degrees(BRIDGE_RAMP / _bridge.plateau_radius)
# What the copper's INNER surface rides on, by azimuth off the register line. A bent tube
# BRIDGES the bridge's own arc ramps rather than following them down, so it holds the plateau
# all the way to the bridge's edge and comes back to the carbonator outside it.
RIDE_RADII = ((math.degrees(_bridge.bridge_half_angle), _bridge.plateau_radius),
              (math.degrees(_bridge.bridge_half_angle) + BRIDGE_ARC_RUNOUT, carbonator_outer_radius))
# The bridge is authored in the CARBONATOR's own frame, one floor slab and one support ring up.
_carbonator_bottom_z = wall_and_floor_thickness + carbonator_support_ring_height
BRIDGE_Z = (_bridge.bridge_z_bottom + _carbonator_bottom_z,
            _bridge.bridge_z_top + _carbonator_bottom_z)
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
    the wrap would dip inside the carbonator just off the bridge's edge. Easing the ramp is what
    keeps the drawn surface where the copper is."""
    t = max(0.0, min(1.0, t))
    return 0.5 - 0.5 * math.cos(math.pi * t)


def _ride_radius(azimuth_deg: float, z: float) -> float:
    """The copper CENTRELINE's radius at one point of the wrap.

    Off the bridge it is `WIND_R`. Over it, the tube's inner surface stands on whatever the
    bridge presents at that azimuth, and the two ends of the bridge's own axial ramp bring it
    up and down rather than stepping."""
    a = abs(((azimuth_deg - _bridge_azimuth + 180.0) % 360.0) - 180.0)
    surface = carbonator_outer_radius
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
    return WIND_R + axial * max(0.0, surface - carbonator_outer_radius)


def wrap_points() -> list:
    """The wrap's centreline, sampled — clocked so it starts on the inlet tail's own azimuth
    and lifted where the bridge carries it."""
    n = max(2, int(round(TOTAL_WRAPS * WRAP_SAMPLES_PER_TURN)))
    # A curve THROUGH sampled points runs inside the circle those points sit on, by the
    # sagitta of one step. Sampling on a circle that much larger puts the drawn surface back
    # on the carbonator instead of a hair inside it.
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

    What is taped to the carbonator sits against it, so it has to land in the copper's own gap."""
    turns = (target_z - evap_tail_low_z) / PITCH - (azimuth_deg - AZ_IN) / 360.0
    wrap_z = evap_tail_low_z + (math.floor(turns) + (azimuth_deg - AZ_IN) / 360.0) * PITCH
    return wrap_z + PITCH / 2.0


TAIL_BEND_R = 15.0


class TailForm:
    """Analytic circular bends and tangent straights, in manufacturing order."""

    def __init__(self, point, tangent):
        self.point = cq.Vector(*point)
        self.tangent = cq.Vector(*tangent).normalized()
        self.edges = []
        self.segments = []

    def bend(self, normal, degrees, label):
        normal = cq.Vector(*normal).normalized()
        angle = math.radians(degrees)
        start, tangent = self.point, self.tangent
        radius = TAIL_BEND_R
        end = (start + tangent.multiply(radius * math.sin(angle))
               + normal.multiply(radius * (1 - math.cos(angle))))
        mid = (start + tangent.multiply(radius * math.sin(angle / 2))
               + normal.multiply(radius * (1 - math.cos(angle / 2))))
        self.edges.append(cq.Edge.makeThreePointArc(start, mid, end))
        self.segments.append(dict(id=label, kind="bend", start=start.toTuple(),
                                  end=end.toTuple(), radius=radius, angle=degrees,
                                  tangent=tangent.toTuple(), normal=normal.toTuple()))
        self.point = end
        self.tangent = tangent.multiply(math.cos(angle)) + normal.multiply(math.sin(angle))

    def straight(self, length, label):
        if length <= 1e-8:
            return
        end = self.point + self.tangent.multiply(length)
        self.edges.append(cq.Edge.makeLine(self.point, end))
        self.segments.append(dict(id=label, kind="straight", start=self.point.toTuple(),
                                  end=end.toTuple(), length=length))
        self.point = end

    def wire(self):
        return cq.Wire.assembleEdges(self.edges)


def tail_form(which: str, *, working_tail=False) -> TailForm:
    """Production form from helix endpoint to the shell exit, optionally to cut end.

    B0 absorbs the helix's small pitch angle. B1/B2 are a plan S-offset;
    B3/B4 complete the vertical change. The outlet has a straight between B3
    and B4. E is the fixed exit datum, two millimetres outside the station.
    """
    sign = -1 if which == "inlet" else 1
    az = AZ_IN if which == "inlet" else AZ_OUT
    z = evap_tail_low_z if which == "inlet" else evap_tail_high_z
    start = _at(az, z)
    beta = math.atan(PITCH / (2 * math.pi * WIND_R))
    form = TailForm(start.toTuple(), (-math.cos(beta), 0, sign * math.sin(beta)))
    form.bend((-math.sin(beta), 0, -sign * math.cos(beta)), math.degrees(beta), "B0")
    (_wall_x, lane_y, cross_z), _axis = _copper.station("evap-" + which)
    offset = abs(lane_y) - WIND_R
    angle = math.acos(1 - offset / (2 * TAIL_BEND_R))
    form.bend((0, sign, 0), math.degrees(angle), "B1")
    form.bend((-math.sin(angle), -sign * math.cos(angle), 0), math.degrees(angle), "B2")
    if which == "inlet":
        drop = form.point.z - cross_z
        angle = math.acos(1 - drop / (2 * TAIL_BEND_R))
        form.bend((0, 0, -1), math.degrees(angle), "B3")
        form.bend((-math.sin(angle), 0, math.cos(angle)), math.degrees(angle), "B4")
    else:
        form.bend((0, 0, -1), 90, "B3")
        form.straight(form.point.z - (cross_z + TAIL_BEND_R), "S1")
        form.bend((-1, 0, 0), 90, "B4")
    exit_x = _wall_x - wall_and_floor_thickness
    form.straight(form.point.x - exit_x, "S2")
    if working_tail:
        form.straight(_mandrel.stub_protrusion[which], "WORKING TAIL")
    return form


def tail_points(which: str) -> list:
    """Tangent stations of the production form; not sharp polyline corners."""
    form = tail_form(which)
    return [form.segments[0]["start"], *(item["end"] for item in form.segments)]


def build_tail(which: str):
    form = tail_form(which)
    wire = form.wire()
    plane = cq.Plane(origin=wire.startPoint(), normal=wire.tangentAt(0))
    solid = cq.Workplane(plane).circle(TUBE_R).sweep(
        cq.Workplane("XY").newObject([wire]), isFrenet=True).val()
    return TAIL_BEND_R, solid


def bodies() -> dict:
    return {"evap-coil": build_wrap(),
            "evap-tail-inlet": build_tail("inlet")[1],
            "evap-tail-outlet": build_tail("outlet")[1]}


def tail_length(which: str) -> float:
    return tail_form(which).wire().Length()


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
    """What a build CUTS per carbonator — the laid wrap plus each end's own tie-in allowance.

    Struck here rather than in `coil_mandrel` because the wrap it stands on is the LAID one,
    and the reed bridge's lift is only visible from this module."""
    return wrap_length() + _mandrel.stub_total


def roll_spare_ft() -> float:
    """What one roll has left after `coil_mandrel.carbonators_per_roll` carbonators come off it."""
    return _mandrel.roll_length_ft - _mandrel.carbonators_per_roll * cut_length() / 304.8


def report() -> None:
    wrap = wrap_length()
    print("  evaporator coil")
    print(f"    stock           {COPPER_STOCK.name}, min bend {COPPER_BEND:.2f} — "
          f"{COPPER_STOCK.source}")
    print(f"    wound at        r {WIND_R:.3f} (carbonator {carbonator_outer_radius:.1f} + tube "
          f"{TUBE_R:.3f}); the mandrel winds at r {_mandrel.helix_path_radius:.3f}")
    print(f"    wraps           {TOTAL_WRAPS:.3f} at {PITCH:.4g} mm pitch, "
          f"z {evap_tail_low_z:.1f}..{evap_tail_high_z:.1f}")
    print(f"    azimuths        inlet {AZ_IN:+.2f}°, outlet {AZ_OUT:+.2f}°, "
          f"CCW delta {(AZ_OUT - AZ_IN) % 360:.2f}°")
    # Three readings of one length: what the mandrel holds, what the same wraps come to once
    # sprung onto the carbonator, and what THIS module draws with the reed bridge's lift in it.
    print(f"    wrap laid       {wrap:.0f} mm ({wrap / 304.8:.2f} ft) — mandrel "
          f"{_mandrel.mandrel_wrap_length:.0f}, sprung {_mandrel.fitted_wrap_length:.0f}, "
          f"reed bridge {bridge_lift_length():+.0f}")
    for end in ("inlet", "outlet"):
        print(f"    {end + ' stub':15} {_mandrel.stub_allowance[end]:.1f} mm allowed = "
              f"{tail_length(end):.1f} mm drawn in-shell "
              f"({_mandrel.tail_in_shell[end]:.1f} billed) + "
              f"{_mandrel.stub_protrusion[end]:.0f} protruding")
    cut = cut_length()
    print(f"    cut per carb    {cut:.1f} mm ({cut / 304.8:.3f} ft); "
          f"{_mandrel.carbonators_per_roll} per {_mandrel.roll_length_ft:.0f} ft roll leaves "
          f"{roll_spare_ft():+.3f} ft ({roll_spare_ft() * 304.8:+.0f} mm)")


if __name__ == "__main__":
    report()
