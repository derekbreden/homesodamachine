"""Scan-fitted neoFit ABU44M-E 4 mm bulkhead union, HSM-000061.

Native +Y points outboard. The origin is the fixed flange's panel-seating
face; the nut retains its captured free position. build() supplies the bare
fitting, and build_assembly() includes the separate captured nut. Hidden
threads use a crest envelope; bore and mouth closures are display geometry.

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations
from pathlib import Path
import sys


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == 'hardware')
sys.path.insert(0, str(_hw/'scripts'))

STEP = _here.with_name('neofit-drain-bulkhead.step')
# Frozen measurements keep consumers of this fitting independent of scan files.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('neofit_drain_bulkhead')
globals().update({name: _reference_values[name] for name in ('PARAMETER_SNAPSHOT_SHA256', 'PARAMETERS', 'TUBE_OD', 'THREAD_D', 'THREAD_PITCH', 'PANEL_THREAD', 'NUT_LEN', 'TUBE_STOP_DEPTH', 'OVERALL', 'FLANGE_AF', 'NUT_AF', 'FLANGE_D', 'NUT_D', 'near_ring_face_y', 'far_ring_face_y', 'far_body_face_y', 'PROUD_LENGTH')})




def panel_hole_d(clearance):
    return _reference_data('neofit_drain_bulkhead', 'panel_hole_d', (clearance,), {})


def panel_footprint():
    return _reference_data('neofit_drain_bulkhead', 'panel_footprint', (), {})


def flange_footprint():
    return _reference_data('neofit_drain_bulkhead', 'flange_footprint', (), {})


def port(side):
    return _reference_data('neofit_drain_bulkhead', 'port', (side,), {})


def radius_at(profile, x):
    return _reference_data('neofit_drain_bulkhead', 'radius_at', (profile, x), {})


def profile_between(profile, lo, hi):
    return _reference_data('neofit_drain_bulkhead', 'profile_between', (profile, lo, hi), {})


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'neofit-drain-bulkhead.step'
PAYLOAD_PATH = _FROZEN_DIR / 'neofit-drain-bulkhead.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('neofit-drain-bulkhead frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
