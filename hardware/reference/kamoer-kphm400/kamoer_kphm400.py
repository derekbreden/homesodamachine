"""The purchased pump's simplified reference and compatibility routing datums.

The exterior belongs to frozen-asset.json. scan_model.rs constructs smooth
primitive solids from measured principal dimensions and connection stations.
The compatibility directory names the pump family; scan-evidence.json identifies
the scanned unit. Holder-derived dimensions remain compatibility datums for
current consumers and do not construct or constrain the visible exterior.
"""
from pathlib import Path
import sys

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'kamoer-kphm400.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'kamoer-kphm400.step.mesh'
FINE_PAYLOAD_PATH = PAYLOAD_PATH
ASSET_MANIFEST_PATH = _REFERENCE_DIR / 'frozen-asset.json'


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")


if __name__ == '__main__':
    main()
    raise SystemExit(0)


_hw = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
sys.path[:0] = [str(_hw / 'scripts'), str(_hw / 'printed-parts/cadlib'),
               str(_hw / 'printed-parts/enclosure/pump-tray')]
import pump_case as pc

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('kamoer_kphm400', inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})
globals().update({name: _reference_values[name] for name in ('cx', 'cy', 'rear_axis_y_shift', 'rear_axis_y', 'base_plane_z', 'octagon_top_z', 'outlet_above_skirt_bottom', 'arch_plane_z', 'y_face', 'tube_casing_w', 'shaft_w', 'outlet_span_x', 'barb_pitch', 'outlet_open_span_x', 'arch_xs', 'skirt_depth', 'head_front_below_skirt', 'skirt_support_air', 'skirt_y', 'skirt_y_max', 'skirt_y_plus_air', 'skirt_upper_band', 'skirt_body_y', 'skirt_support_xy_air', 'skirt_support_y_minus', 'skirt_support_y_plus', 'skirt_body_y_max', 'skirt_body_y_min', 'head_w', 'head_depth', 'motor_dia', 'motor_reach', 'pump_len', 'body_y_face', 'bracket_w', 'bracket_t', 'bracket_z', 'outlet_relief', 'outlet_relief_top_z', 'outlet_relief_run', 'head_front_z', 'motor_end_z')})


def barb(i: int):
    "The routed outlet station in the compatibility frame."
    return _reference_data('kamoer_kphm400', 'barb', (i,), {}, inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})


def barbs():
    "Both, in `arch_xs` order — west to east across the head's own face."
    return _reference_data('kamoer_kphm400', 'barbs', (), {}, inputs={'pc': {name: getattr(pc, name) for name in ('bore_bottom_z', 'center_x', 'center_y', 'pos_y_face_y', 'skirt_bottom_z')}})
