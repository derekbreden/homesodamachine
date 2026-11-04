"""PP0208E measured clearance reference, run on ±Z and branch on +Y.

Fixed roots/collars use the unscaled scan envelope; run and branch faces and
their distinct operating strokes use Derek's calipers. Terminal-ring detail
remains explicitly unqualified. This is an external clearance reference,
not a detailed internal fitting or manufacturing tolerance specification.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))

STEP = _here.parent / "tee-connector.step"

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('tee_connector')
globals().update({name: _reference_values[name] for name in ('BRANCH_MEASUREMENTS', '_branch', 'TUBE_D', 'RUN_SPAN', 'RUN_SPAN_PRESSED', 'RUN_HALF', 'RUN_COLLET_TRAVEL', 'FIRST_RESISTANCE', 'GRIP_DEPTH', 'INSERTION', 'RUN_INSERTION_EXTENDED', 'COLLAR_NOMINAL_D', 'COLLAR_ENVELOPE_D', 'BARREL_R', 'HALF_W', 'ARM_R', 'RUN_ROOT_BAND', 'BRANCH_ROOT_BAND', 'RUN_COLLAR_BAND', 'BRANCH_COLLAR_BAND', 'ARM_ROOT', 'CAP_NEAR', 'CAP_FAR', 'BARREL_NEAR', 'RUN_ENVELOPE_SHOULDER', 'BRANCH_ENVELOPE_SHOULDER', 'BRANCH_WIDTH_EXTENDED', 'BRANCH_WIDTH_PRESSED', 'BRANCH_REACH', 'BRANCH_PRESSED_REACH', 'BRANCH_COLLET_TRAVEL', 'BRANCH_INSERTION_EXTENDED', 'FIXED_NOSE_R', 'RUN_COLLAR_END', 'BRANCH_COLLAR_END', 'RUN_FIXED_END', 'BRANCH_FIXED_END', 'COLLET_NOSE_R', 'BARREL_FAR', 'COLLET_PROUD', 'UNQUALIFIED_DATUMS', 'MEASURE_TOL', 'CARRIER_AFT_COLLET_GAP', 'CARRIER_STROKE', 'CARRIER_MAX_STROKE', 'CARRIER_RELEASE_OFFSET', 'CARRIER_SQUEEZE_OFFSET', 'CARRIER_CONNECTED_OFFSET', 'CARRIER_PARK_OFFSET', 'CARRIER_STATES')})


# Calipered operating dimensions. Insertion is from the PRESSED sleeve face.

# Fitted collar midpoints are Ø16.224..16.330; the outer draft reaches the
# rounded Ø16.5 sample envelope. Printed passages add their own running air.
# These conservative envelope transitions precede the observed shoulders.
# The fit bands above are interior measurement patches, NOT shoulder edges.

# The caliper's back jaw meets the NOMINAL fixed collar, not the conservative
# clearance envelope. The resulting faces are nominal axis stations; the raw
# outside-to-outside readings remain the primary measurements.
if abs(BRANCH_COLLET_TRAVEL - _branch["branch_collet_travel_mm"]) > 1e-9:
    raise ValueError("branch stroke differs from its raw overall-width readings")

# Fixed reduced barrels precede the small moving terminal rings. These are
# conservative clearance bounds around the observed scan surfaces, not exact
# molded shoulder or moving-ring seam measurements. Run and branch have
# distinct fixed profiles. No part of either fixed barrel moves on release.

if not BRANCH_COLLET_TRAVEL <= CARRIER_STROKE <= CARRIER_MAX_STROKE:
    raise ValueError("carrier stroke must release the sleeve within 2.5 mm")


def carrier_collet_depression(offset: float):
    'Sleeve movement while its nose bears against the fixed release plate.'
    return _reference_data('tee_connector', 'carrier_collet_depression', (offset,), {})


def run(sign):
    return _reference_data('tee_connector', 'run', (sign,), {})


def run_barrel(sign):
    return _reference_data('tee_connector', 'run_barrel', (sign,), {})


def branch():
    return _reference_data('tee_connector', 'branch', (), {})


def branch_collar():
    return _reference_data('tee_connector', 'branch_collar', (), {})


def stations():
    return _reference_data('tee_connector', 'stations', (), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'tee-connector.step'
PAYLOAD_PATH = _FROZEN_DIR / 'tee-connector.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('tee-connector frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
