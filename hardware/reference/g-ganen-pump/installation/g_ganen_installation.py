"""Installed G Ganen with four identical purchased sliding rubber feet.

The shared foot has a nominal 7 mm pad. Its rail clips reach the fore/aft rail
ends with their full axial span engaged. Scan poses and raw slot observations
remain separate from the installed mounting stations.
"""
from functools import lru_cache
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
sys.path.insert(0, str(REFERENCE/'integration-envelope'))
import g_ganen_integration as envelope
from native_queries import intersect_components, occupied_bounds
sys.path.insert(0, str(REFERENCE/'common-foot'))
import g_ganen_foot as stock_foot

SCENE_KEY = 'g-ganen-pump'
YAW = 90.
REAR_CLEARANCE = 9.7
WASHER_OD = 9.
WASHER_T = .8
SCREW_D = 3.
SCREW_LENGTH = 20.
SCREW_BORE_MIN_DEPTH = 8.5
SCREW_SLOT_OFFSET_OUTWARD = 1.5
# The visible rail ends and the shared foot's complete engagement span define
# the installed fore/aft extremes. Positive reference X points aft.
RAIL_X = (0.5, 76.5)
CLIP_X = stock_foot.rail_engagement_interval()
SELECTED_SLIDER_X = {
    name: RAIL_X[0] - CLIP_X[0] if name.startswith('head_') else RAIL_X[1] - CLIP_X[1]
    for name in ('rear_yminus', 'rear_yplus', 'head_yminus', 'head_yplus')}
SLOT_Y = stock_foot.SLOT_Y
# Reference origin in the installed cap frame, with the rear-clearance shift.
CAP_PUMP_ORIGIN = (-59.13545827612205 + REAR_CLEARANCE, 2.07113514496717)
CAP_MOUNT_XY = tuple((CAP_PUMP_ORIGIN[0] - x,
                      CAP_PUMP_ORIGIN[1] - (-1 if 'yminus' in name else 1)
                      * (SLOT_Y + SCREW_SLOT_OFFSET_OUTWARD))
                     for name, x in SELECTED_SLIDER_X.items())

parameters = envelope.parameters
port = envelope.port
suction = envelope.suction
discharge = envelope.discharge
port_profile = envelope.port_profile
sliding_rails = envelope.sliding_rails
mount_seat_z = envelope.mount_seat_z


@lru_cache(maxsize=1)
def mount_stations():
    rows = []
    for observed in envelope.mount_slots():
        name = observed['id']
        side = -1 if 'yminus' in name else 1
        x = SELECTED_SLIDER_X[name]
        interval = CLIP_X if side > 0 else (-CLIP_X[1], -CLIP_X[0])
        rows.append({
            'id': name,
            'station_mm': (x, side*(SLOT_Y + SCREW_SLOT_OFFSET_OUTWARD), 0.),
            'slot_center_mm': (x, side*SLOT_Y, 0.),
            'screw_offset_outward_mm': SCREW_SLOT_OFFSET_OUTWARD,
            'shape_basis': 'shared_purchased_rubber_foot',
            'pad_thickness_mm': stock_foot.PAD_THICKNESS,
            'rail_engagement_x_mm': (x+interval[0], x+interval[1]),
            'station_basis': 'outermost_complete_visible_rail_engagement',
            'observed_pad_top_mm': [{
                'pass': 'Derek_direct_measurement_approximately_7_mm',
                'at_screw_axis_mm': stock_foot.PAD_THICKNESS,
                'over_washer_min_mm': stock_foot.PAD_THICKNESS,
                'over_washer_max_mm': stock_foot.PAD_THICKNESS}],
            'through_slot_physically_qualified': False,
            'washer_physically_qualified': False})
    return tuple(rows)


def mount_holes():
    """Selected candidate screw axes; these do not declare a fixed purchased pattern."""
    return tuple(row['station_mm'][:2] for row in mount_stations())


def bearing_datum():
    return (0., 0., 0.), (0., 0., 1.)


def placed_bearing_z(carry):
    return carry(bearing_datum())[0][2]


def bearing_z_from_frame(frame):
    """Bearing Z from a placed port frame in this yaw-only installation."""
    return frame.at('suction')[2]-suction()[0][2]


def observed_pad_upper_z():
    return max(top['over_washer_max_mm'] for foot in mount_stations()
               for top in foot['observed_pad_top_mm'])


def observed_pad_lower_z():
    return min(top['over_washer_min_mm'] for foot in mount_stations()
               for top in foot['observed_pad_top_mm'])


def build_parts():
    parts = envelope.build_parts()
    for row in mount_stations():
        name = row['id']
        x, y, _ = row['slot_center_mm']
        parts[name+'_observed_rubber_slider_envelope'] = stock_foot.placed_foot(
            x, -1 if 'yminus' in name else 1, abs(y))
    return parts


def rigid_shape():
    return cq.Compound.makeCompound([shape for name, shape in build_parts().items()
                                     if 'rubber_slider' not in name])


def feet_shapes(carry=None):
    parts = {name: shape for name, shape in build_parts().items() if 'rubber_slider' in name}
    if carry is not None:
        parts = {name: shape.moved(carry.where) for name, shape in parts.items()}
    return parts


def cap_bearing_contact_parts(carry, cap_plane_z):
    """Placed rigid pump plus four exact free-rubber masks below its cap plane.

    These masks classify only the observed unloaded foot envelope where it bears
    on the flat lid. They are not material/compression models. A collision checker
    must still test the rigid pump against the cap and retain every overlap not
    inside these masks; the complete pump remains in all other neighbor checks.
    """
    point, axis = carry(bearing_datum())
    if abs(point[2] - cap_plane_z) > 1e-6:
        raise ValueError('G Ganen bearing datum is not on the independent cap plane')
    if max(abs(a - b) for a, b in zip(axis, (0., 0., 1.))) > 1e-7:
        raise ValueError('G Ganen bearing masks require the installed upright Z axis')
    parts = build_parts()
    expected = {name + '_observed_rubber_slider_envelope' for name in SELECTED_SLIDER_X}
    foot_names = {name for name in parts if 'rubber_slider' in name}
    if foot_names != expected or len(expected) != 4:
        raise ValueError('G Ganen bearing masks require exactly the four named stock feet')
    rigid = cq.Compound.makeCompound([
        shape.moved(carry.where) for name, shape in parts.items() if name not in foot_names])
    masks = {}
    for name in sorted(expected):
        foot = parts[name].moved(carry.where)
        b = foot.BoundingBox()
        if b.zmin >= cap_plane_z:
            masks[name] = cq.Compound.makeCompound([])
            continue
        # No extension above the independently located lid plane. The small
        # sideways/bottom extension belongs to the cutter, not the returned mask.
        eps = 1e-5
        slab = cq.Solid.makeBox(b.xlen + 2*eps, b.ylen + 2*eps,
                                cap_plane_z - b.zmin + eps,
                                cq.Vector(b.xmin-eps, b.ymin-eps, b.zmin-eps))
        masks[name] = foot.intersect(slab)
    return rigid, masks


def build():
    return cq.Compound.makeCompound(list(build_parts().values()))


def discharge_shape(carry=None):
    parts = envelope.build_parts()
    shape = cq.Compound.makeCompound([parts['port_yplus_barb_envelope'], parts['port_yplus_root_envelope']])
    return shape if carry is None else shape.moved(carry.where)


def profiled_barb_length(port_name):
    key = {'suction': 'port_yminus', 'discharge': 'port_yplus'}.get(port_name, port_name)
    return port_profile(key)['profiled_exterior_length_mm']
