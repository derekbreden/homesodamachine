"""Drop-in PET-GF funnel frame with screw seats and its drain-cradle snap socket: the frame's
datums for the hand-run tools that read them. `funnel_frame.rs`, beside this module, cuts the frame.
"""

import sys
from pathlib import Path

import elbow_cradle
import funnel

ROOT = next(p for p in Path(__file__).resolve().parents if any(
    (p / 'hardware/scripts' / helper).is_file()
    for helper in ('_rust_part.py', '_cadq_export.py')))
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
                str(ROOT / 'hardware/scripts')]

from _zone_data import data as _zone


def _data(**payload):
    return _zone('funnel-frame', **payload)


globals().update(_data())
DEFAULT_INNER = tuple(DEFAULT_INNER)
socket_flare = tuple(socket_flare)


def datums(seat=349.0):
    return tuple(_data(method='datums', seat=seat))


def roof_datums(inner=DEFAULT_INNER, centre=(0.0, center_y), seat=349.0,
                y_joint=200.0, full_front_opening=False):
    return _data(method='roof', inner=inner, centre=centre, seat=seat,
                 y_joint=y_joint, full_front_opening=full_front_opening)


def fastener_datums(inner=DEFAULT_INNER, y_joint=200.0,
                    centre=(0.0, center_y), seat=349.0):
    return tuple(_data(method='fasteners', inner=inner, y_joint=y_joint, centre=centre, seat=seat))


def drain_seat_datums(centre=(0.0, center_y), seat=349.0):
    return _data(method='drain_seat', centre=centre, seat=seat)


def body_side_half_width(inner=DEFAULT_INNER, y_joint=200.0,
                         centre=(0.0, center_y), seat=349.0):
    return _data(method='body_half', inner=inner, y_joint=y_joint, centre=centre, seat=seat)
