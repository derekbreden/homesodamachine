"""Bare installed G Ganen; the complete rubber feet/legs slide off its rails.

Production placement belongs to above-core.json. The nominal stock-foot
observations below describe the removable purchased sliders only; the installed
bare casing rests on the plain lid and its motor sits in the integral half
pipe. A removable upper half pipe snaps into the lid seat.
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


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('g_ganen_installation')
globals().update({name: _reference_values[name] for name in ('SCENE_KEY', 'YAW', 'REAR_CLEARANCE', 'WASHER_OD', 'WASHER_T', 'SCREW_D', 'SCREW_LENGTH', 'SCREW_BORE_MIN_DEPTH', 'SCREW_SLOT_OFFSET_OUTWARD', 'RAIL_X', 'CLIP_X', 'SELECTED_SLIDER_X', 'SLOT_Y', 'CAP_PUMP_ORIGIN', 'CAP_MOUNT_XY')})

# The visible rail ends and the shared foot's complete engagement span define
# the installed fore/aft extremes. Positive reference X points aft.
# Reference origin in the installed cap frame, with the rear-clearance shift.

parameters = envelope.parameters
port = envelope.port
suction = envelope.suction
discharge = envelope.discharge
port_profile = envelope.port_profile
sliding_rails = envelope.sliding_rails


def mount_seat_z():
    "Molded cable cover's low point, in the purchased frame."
    return _reference_data('g_ganen_installation', 'mount_seat_z', (), {})


@lru_cache(maxsize=1)
def mount_stations():
    return _reference_data('g_ganen_installation', 'mount_stations', (), {})


def mount_holes():
    'No foot screws belong to the bare installed pump.'
    return _reference_data('g_ganen_installation', 'mount_holes', (), {})


def bearing_datum():
    return _reference_data('g_ganen_installation', 'bearing_datum', (), {})


def placed_bearing_z(carry):
    return carry(bearing_datum())[0][2]


def bearing_z_from_frame(frame):
    return _reference_data('g_ganen_installation', 'bearing_z_from_frame', (frame.at('suction')[2],), {})


def observed_pad_upper_z():
    return _reference_data('g_ganen_installation', 'observed_pad_upper_z', (), {})


def observed_pad_lower_z():
    return _reference_data('g_ganen_installation', 'observed_pad_lower_z', (), {})


def build_parts():
    """Installed rigid casing, motor, ports and fixed rails, without sliders."""
    return {name: shape for name, shape in envelope.build_parts().items()
            if 'rubber_slider' not in name}


def rigid_shape():
    return cq.Compound.makeCompound([shape for name, shape in build_parts().items()
                                     if 'rubber_slider' not in name])


def feet_shapes(carry=None):
    parts = {name: shape for name, shape in build_parts().items() if 'rubber_slider' in name}
    if carry is not None:
        parts = {name: shape.moved(carry.where) for name, shape in parts.items()}
    return parts


def cap_bearing_contact_parts(carry, cap_plane_z):
    """Bare pump and no rubber contact masks."""
    return rigid_shape().moved(carry.where), {}


def build():
    return cq.Compound.makeCompound(list(build_parts().values()))


def discharge_shape(carry=None):
    parts = envelope.build_parts()
    shape = cq.Compound.makeCompound([parts['port_yplus_barb_envelope'], parts['port_yplus_root_envelope']])
    return shape if carry is None else shape.moved(carry.where)


def profiled_barb_length(port_name):
    return _reference_data('g_ganen_installation', 'profiled_barb_length', (port_name,), {})
