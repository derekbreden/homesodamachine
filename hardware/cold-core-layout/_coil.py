"""The evaporator coil, wound on the carbonator, with the two tails that leave it.

`coil-mandrel` is the undersized rough-forming aid. This module defines the
finished copper after diameter, pitch and turn count are set on the vessel
fixture: one tube radius off the carbonator OD, lifted over the reed bridge
by `_ride_radius`. `wrap_length` is the copper in that finished winding,
which is the figure `bom.md` §5 bills. The mandrel's groove has its own
turn count and length.

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

import coil_mandrel as _mandrel
import _copper_ports as _copper
import reed_bridge as _bridge
from _cold_core_interface import (
    evap_tail_high_z, evap_tail_low_z, carbonator_outer_radius,
    carbonator_support_ring_height, wall_and_floor_thickness,
    carbonator_sensor_azimuth,
)
from _routing import stock_min, stock_of
import _stated_bounds as _bounds
from _cold_core_data import read as _read

# The Rust recipe derives the wrap, bridge lift, R15 bends and copper ledger.
# These inputs are the external dimensions authored by their component providers.
_spec = {
    'evap_tail_high_z': evap_tail_high_z, 'evap_tail_low_z': evap_tail_low_z,
    'carbonator_outer_radius': carbonator_outer_radius,
    'carbonator_support_ring_height': carbonator_support_ring_height,
    'wall_and_floor_thickness': wall_and_floor_thickness,
    'carbonator_sensor_azimuth': carbonator_sensor_azimuth,
    'copper_bend': stock_min('refrigerant', _copper.copper_outer_diameter),
    'plateau_radius': _bridge.plateau_radius,
    'bridge_half_angle': _bridge.bridge_half_angle,
    'bridge_z_bottom': _bridge.bridge_z_bottom, 'bridge_z_top': _bridge.bridge_z_top,
    'axial_ramp_length': _bridge.axial_ramp_length,
    'front_wall_x': _copper.front_wall_x, 'port_lane_mid_y': _copper.port_lane_mid_y,
    'west_lane_mid_y': _copper.west_lane_mid_y, 'evap_cross_z': _copper.evap_cross_z,
}


def _recipe(action, **inputs):
    return _read('coil', action=action, spec=_spec, **inputs)


globals().update(_recipe('constants'))
RIDE_RADII = tuple(tuple(row) for row in RIDE_RADII)
BRIDGE_Z = tuple(BRIDGE_Z)
COPPER_STOCK = stock_of('refrigerant', _copper.copper_outer_diameter)


def _at_xyz(azimuth_deg, z, radius=None):
    return tuple(_recipe('at', azimuth_deg=azimuth_deg, z=z, radius=radius))


def _at(azimuth_deg, z, radius=None):
    return cq.Vector(*_at_xyz(azimuth_deg, z, radius))


def _ease(t):
    return _recipe('ease', t=t)


def _ride_radius(azimuth_deg, z):
    return _recipe('ride-radius', azimuth_deg=azimuth_deg, z=z)


def wrap_points_xyz():
    """The laid wrap's scalar sampled centreline, including bridge lift."""
    return [tuple(point) for point in _recipe('wrap-points')]


def wrap_points():
    return [cq.Vector(*point) for point in wrap_points_xyz()]


def wrap_length():
    return _recipe('wrap-length')


def bridge_lift_length():
    return _recipe('bridge-lift-length')


def gap_z_near(azimuth_deg, target_z):
    return _recipe('gap-z-near', azimuth_deg=azimuth_deg, target_z=target_z)


def _segments(rows):
    return [{key: tuple(value) if isinstance(value, list) else value
             for key, value in row.items()} for row in rows]


def tail_layout(which, *, working_tail=False):
    """Rust's source-frame tangent stations and analytic bends."""
    return _segments(_recipe('tail-layout', which=which, working_tail=working_tail))


def tail_layout_length(which):
    return _recipe('tail-length', which=which)


def tail_points(which):
    return [tuple(point) for point in _recipe('tail-points', which=which)]


def tail_length(which):
    return _recipe('tail-length', which=which)


def cut_length():
    return _recipe('cut-length')


def roll_spare_ft():
    return _recipe('roll-spare-ft')


class TailForm:
    """Native edge adapter for the Rust manufacturing stations."""

    def __init__(self, which, *, working_tail=False):
        data = _recipe('tail-edges', which=which, working_tail=working_tail)
        self.point = cq.Vector(*data['point'])
        self.tangent = cq.Vector(*data['tangent'])
        self.edges = []
        self.segments = []
        for row in _segments(data['segments']):
            start, end = cq.Vector(*row['start']), cq.Vector(*row['end'])
            if row['kind'] == 'bend':
                self.edges.append(cq.Edge.makeThreePointArc(start, cq.Vector(*row.pop('mid')), end))
            else:
                self.edges.append(cq.Edge.makeLine(start, end))
            self.segments.append(row)

    def wire(self):
        return cq.Wire.assembleEdges(self.edges)


def tail_form(which, *, working_tail=False):
    return TailForm(which, working_tail=working_tail)


def helix_wire():
    """Native drawing adapter for the nominal-circle helix."""
    helix = cq.Wire.makeHelix(PITCH, WIND_HEIGHT, WIND_R)
    return (helix.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), AZ_IN)
            .translate(cq.Vector(0, 0, evap_tail_low_z)))


def build_wrap():
    wire = helix_wire()
    profile = cq.Workplane(cq.Plane(origin=wire.startPoint(), normal=wire.tangentAt(0)))
    return profile.circle(TUBE_R).sweep(
        cq.Workplane('XY').newObject([wire]), isFrenet=True).val()


def build_tail(which):
    wire = tail_form(which).wire()
    plane = cq.Plane(origin=wire.startPoint(), normal=wire.tangentAt(0))
    solid = cq.Workplane(plane).circle(TUBE_R).sweep(
        cq.Workplane('XY').newObject([wire]), isFrenet=True).val()
    return TAIL_BEND_R, solid


def bodies():
    return {'evap-coil': build_wrap(),
            'evap-tail-inlet': build_tail('inlet')[1],
            'evap-tail-outlet': build_tail('outlet')[1]}


_ledger = _recipe('tail-ledger')
_tails_billed = _bounds.bound('stub-tails-billed', _ledger['label'], _ledger['target'])
for _row in _ledger['rows']:
    _tails_billed(_row['holds'], _row['detail'])


def report(*, laid_length=None, tail_lengths=None):
    print(_recipe('report', laid_length=laid_length, tail_lengths=tail_lengths,
                  stock_name=COPPER_STOCK.name, stock_source=COPPER_STOCK.source), end='')


if __name__ == '__main__':
    report()
