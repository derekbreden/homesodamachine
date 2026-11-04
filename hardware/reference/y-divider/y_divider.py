"""Y-divider — the three-port trident the manifold joins a valve pair with.

`y-divider.step` is a harvested solid: there is no builder here, and every number below was
measured off that file. `native-measurements.json` binds the native readings to that STEP by
SHA-256.
`stations_hold` compares the interface figures with those recorded readings.

Coordinate frame
----------------
- The long axis on Z. The STEM is the single port at +Z; the two OUTLETS are at −Z, offset
  ±`OUTLET_Y` either side of the axis. All three take 1/4" OD tube.
- Origin at the body centre, so the stem and the outlet faces are ±`HALF`.

The topology names its three legs (`../../topology/fluid-topology.md`); which outlet reaches
which valve is the seating's business, and the enclosure's.
"""

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()

STEP = _here.parent / "y-divider.step"

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('y_divider')
globals().update({name: _reference_values[name] for name in ('MEASUREMENTS', 'HALF', 'OUTLET_Y', 'HALF_W', 'TUBE_D', 'MEASURE_TOL')})


# --- Measured off the STEP ------------------------------------------------


def stem():
    'The single port at +Z: `(position, outward axis)`.'
    return _reference_data('y_divider', 'stem', (), {})


def outlet(sign):
    'One of the two ports at −Z, `sign` picking the +Y or −Y side.'
    return _reference_data('y_divider', 'outlet', (sign,), {})


def stations():
    'All three, under the sides they stand on.'
    return _reference_data('y_divider', 'stations', (), {})


def _collet_offsets(readings, axis, bore_r, tol=0.0001):
    return _reference_data('y_divider', '_collet_offsets', (readings, axis, bore_r, tol), {})


def stations_hold():
    "Compare the interface figures with the recorded native STEP readings.\n\n    The reaches and the radius are extents of the solid's own box. The outlet offset is not —\n    it is a bore centre inside the envelope, and it is read off the tube bores themselves."
    return _reference_data('y_divider', 'stations_hold', (), {})


# --- controls -------------------------------------------------------------

def selftest():
    stations_hold()
    return ["  the three declared stations stand on the solid they were measured off"]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("y_divider selftest OK")
    else:
        print(__doc__)
