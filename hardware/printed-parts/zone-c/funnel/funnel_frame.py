"""Drop-in PET-GF funnel frame with screw seats and its drain-cradle snap socket.

Construction uses machine coordinates. The exported removable frame is translated
onto its flat underside, with the funnel's plan center at the origin.
"""

import argparse
import sys
from pathlib import Path

import elbow_cradle
import funnel

ROOT = next(p for p in Path(__file__).resolve().parents if any(
    (p / 'hardware/scripts' / helper).is_file()
    for helper in ('_rust_part.py', '_cadq_export.py')))
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
                str(ROOT / 'hardware/scripts')]

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()


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


def numbers(inner=DEFAULT_INNER, y_joint=200.0, centre=(0.0, center_y), seat=349.0):
    return _data(method='numbers', inner=inner, y_joint=y_joint, centre=centre, seat=seat)


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel-frame', numbers(), out)
    print(f'-> funnel-frame STEP, STL and payload; {said["bodies"][0]["volume"]:.1f} mm3; '
          f'floor Z {datums()[0]:g}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    main(options.output)
