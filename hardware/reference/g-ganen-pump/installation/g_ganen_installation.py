"""Installed G Ganen candidate using the purchased sliding rubber feet.

The selected slider stations are assembly choices. Observed free-foot geometry,
slot sections and planes remain in the frozen measured reference. A loaded clamp
stack and actual M3/washer fit remain physical assembly-test readings.
"""
from functools import lru_cache
from pathlib import Path
import math
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
sys.path.insert(0, str(REFERENCE/'integration-envelope'))
import g_ganen_integration as envelope
from native_queries import intersect_components, occupied_bounds

SCENE_KEY = 'g-ganen-pump'
YAW = 90.
REAR_CLEARANCE = 8.7
WASHER_OD = 9.
WASHER_T = .8
SCREW_D = 3.
SCREW_LENGTH = 20.
SELECTED_SLIDER_X = {'head_yminus': 12., 'head_yplus': 12.,
                     'rear_yminus': 50., 'rear_yplus': 50.}
# The cap's +X points toward enclosure fore. These zero-clearance stations place
# the rigid pump rear at the core rear; the shared clearance moves pump and all
# four printed mount axes fore together. pump_mount_rows checks their alignment.
CAP_MOUNT_XY = tuple((x + REAR_CLEARANCE, y) for x, y in (
    (-109.13545827612205, 40.58788185569069),
    (-109.13545827612205, -36.70985685897666),
    (-71.13545827612205, 41.32456561223638),
    (-71.13545827612205, -36.26848796999695)))

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
    for foot in envelope.mount_slots():
        observed = foot['pose_observations'][0]['local_slot_sections']
        sections = [s for s in observed['sections'] if s.get('status') == 'complete_section_observed']
        qualification = 'visible_complete_lower_sections'
        if not sections:
            sections = [min((s for s in observed['sections'] if 'center_reference_mm' in s),
                            key=lambda s: s['depth_above_local_bearing_plane_mm'])]
            qualification = 'visible_partial_mouth_only'
        center = [sum(s['center_reference_mm'][i] for s in sections)/len(sections) for i in (0, 1)]
        dx = SELECTED_SLIDER_X[foot['id']]-center[0]
        station = [center[0]+dx, center[1], 0.]
        heights = []
        for top in foot['top_plane_observations']['observations']:
            if 'top_plane_point_mm' not in top:
                continue
            pose = next(p for p in foot['pose_observations'] if p['pass'] == top['pass'])
            p = list(top['top_plane_point_mm'])
            shift = pose['native_foot_pose_translation_to_first_pass_mm']
            p = [p[i]+shift[i] for i in range(3)]
            p[0] += dx
            n = top['top_plane_normal']
            at_axis = p[2]-(n[0]*(station[0]-p[0])+n[1]*(station[1]-p[1]))/n[2]
            half_range = WASHER_OD/2*math.hypot(n[0], n[1])/abs(n[2])
            heights.append({'pass': top['pass'], 'at_screw_axis_mm': at_axis,
                            'over_washer_min_mm': at_axis-half_range,
                            'over_washer_max_mm': at_axis+half_range})
        rows.append({'id': foot['id'], 'station_mm': tuple(station),
                     'observed_slot_center_xy_mm': tuple(center),
                     'slider_translation_x_mm': dx,
                     'slot_center_basis': qualification,
                     'visible_sections': sections, 'observed_pad_top_mm': heights,
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
        key = row['id']+'_observed_rubber_slider_envelope'
        parts[key] = parts[key].translate((row['slider_translation_x_mm'], 0., 0.))
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
