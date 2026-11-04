"""Scan-fitted John Guest PP1208E 1/4-inch bulkhead union, HSM-000059.

+Y points outboard; Y0 is the fixed flange's panel-seating face. The frozen
reference contains the fitting and its separate nut at the captured position.
The manual Rust generator reads reference-parameters.json; assembly consumers
use these frozen datums and the declared model, without opening the scan archive.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
STEP_PATH = HERE / 'jg-bulkhead-union.step'
PAYLOAD_PATH = HERE / 'jg-bulkhead-union.step.mesh'
ASSET_MANIFEST_PATH = HERE / 'frozen-asset.json'


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('jg_bulkhead_union')
globals().update({name: _reference_values[name] for name in ('PORT_D', 'TUBE_OD', 'THREAD_D', 'MOUNTING_HOLE_D', 'TUBE_STOP_DEPTH', 'PORT_DEPTH', 'OVERALL', 'near_ring_face_y', 'PROUD_LENGTH', 'far_ring_face_y', 'BODY_D', 'FLANGE_D', 'RING_D', 'FLANGE_AF', 'NUT_AF', 'NUT_D', 'NUT_LEN', 'CAPTURED_NUT_GAP', 'PANEL_THREAD')})



def panel_hole_d(clearance):
    "The manufacturer's round mounting-hole diameter plus the panel's slip."
    return _reference_data('jg_bulkhead_union', 'panel_hole_d', (clearance,), {})


def panel_footprint():
    return _reference_data('jg_bulkhead_union', 'panel_footprint', (), {})


def flange_footprint():
    return _reference_data('jg_bulkhead_union', 'flange_footprint', (), {})


def port(side):
    return _reference_data('jg_bulkhead_union', 'port', (side,), {})


def main():
    import json
    sys.path.insert(0, str(HERE.parents[1] / 'scripts'))
    import _rust_part
    _rust_part.start()
    from _materials import M_JG_BLACK_PP, linear
    parameters = json.loads((HERE / 'reference-parameters.json').read_text())
    _rust_part.cut('tooling', 'jg-bulkhead-reference',
                   {**parameters, 'color': linear(M_JG_BLACK_PP)}, HERE)


if __name__ == '__main__':
    main()
