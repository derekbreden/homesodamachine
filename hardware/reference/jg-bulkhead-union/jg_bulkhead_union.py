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

PORT_D = TUBE_OD = 6.35
THREAD_D = 16.7
MOUNTING_HOLE_D = 17.0
TUBE_STOP_DEPTH = PORT_DEPTH = 15.7
OVERALL = 37.55273081350097
near_ring_face_y = PROUD_LENGTH = 11.521369623928024
far_ring_face_y = -26.031361189572948
BODY_D = FLANGE_D = 23.34348
RING_D = 10.9
FLANGE_AF = 18.83501909374671
NUT_AF = 20.001471308895436
NUT_D = 22.50104
NUT_LEN = 5.939959183240793
CAPTURED_NUT_GAP = 5.691909221634731
PANEL_THREAD = 13.5


def panel_hole_d(clearance):
    """The manufacturer's round mounting-hole diameter plus the panel's slip."""
    return MOUNTING_HOLE_D + clearance


def panel_footprint():
    diameter = max(FLANGE_D, NUT_D)
    return diameter, diameter


def flange_footprint():
    return FLANGE_D


def port(side):
    return ((0., near_ring_face_y if side > 0 else far_ring_face_y, 0.),
            (0., 1. if side > 0 else -1., 0.))


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
