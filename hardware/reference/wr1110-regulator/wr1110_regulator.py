"""Scan-derived external form of the received WR1110 fixed inline regulator.

Two MINI 2 passes establish the smooth barrel, unequal wrench sections, shoulders
and outlet stub at native millimetre scale. See README.md and scan-measurements.json.
The thread crests use a smooth envelope; visible mouths are shallow display bores.
Internal pressure-control geometry and made-up NPT engagement are unmeasured.

Frame: inlet face at the origin, flow along +Y, barrel centred on X/Z.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "wr1110-regulator.step"

# Rounded modelling dimensions from the coated, unit-scale exterior scan.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('wr1110_regulator')
globals().update({name: _reference_values[name] for name in ('BODY_D', 'BODY_START', 'BODY_END', 'BODY_LENGTH', 'INLET_HEX_AF', 'INLET_HEX_D', 'OUTLET_HEX_AF', 'OUTLET_HEX_D', 'OUTLET_HEX_CLOCK', 'TOTAL_LENGTH', 'STUB_LENGTH', 'STUB_D', 'OVERALL_LENGTH', 'INLET_PROFILE', 'OUTLET_PROFILE', 'STUB_PROFILE')})


# (Y station, radius). Short straight segments represent the turned end rounds.


def inlet():
    'The upstream hex\'s outer face — the mouth of the 1/4" NPT female socket,\n    taking a PI010822S male connector: (position, outward axis). The body is\n    built from the origin along the flow axis, so the inlet face is at y = 0 and\n    the outlet hex face at y = TOTAL_LENGTH, not either side of the origin.'
    return _reference_data('wr1110_regulator', 'inlet', (), {})


def outlet():
    'The measured far end of the outlet stub: position and outward axis.'
    return _reference_data('wr1110_regulator', 'outlet', (), {})


def barrel():
    'The measured circular mounting band: `(midpoint station, radius, length)`.\n\n    The enclosure locates its cradle on this band independently of wrench clock.\n    '
    return _reference_data('wr1110_regulator', 'barrel', (), {})


def stations():
    'Both sockets, in the order the gas meets them.'
    return _reference_data('wr1110_regulator', 'stations', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'wr1110-regulator.step'
PAYLOAD_PATH = _FROZEN_DIR / 'wr1110-regulator.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def __getattr__(name):
    if name != 'import_step':
        raise AttributeError(name)
    from _cadq_export import import_step
    globals()[name] = import_step
    return import_step


def main():
    print('wr1110-regulator frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
