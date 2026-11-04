"""Python import adapters for the enclosure's Rust scalar and leaf recipes."""
from functools import cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'printed-parts' / 'cadlib')]

from _rust_data import request


def read(op, **values):
    return request('enclosure-data', 'enclosure-data', {'op': op, **values})


@cache
def dimensions():
    import _rust_part
    _rust_part.start()
    import fits
    import port_chip
    return read('defaults', slip=fits.slip, supported_surface=fits.supported_surface,
                port_width=port_chip.WIDTH, port_corner=port_chip.LOWER_CORNER_RADIUS)
