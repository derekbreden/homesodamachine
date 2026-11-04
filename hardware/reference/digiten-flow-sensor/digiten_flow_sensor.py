"""Measured external reference for the DIGITEN inline flow sensor.

Millimetres. X is the port axis, Y points toward the label, Z toward the
pigtail. The origin is midway between the two collet faces on the port axis.
The round housing axis is offset toward +Z. Hidden turbine, seals, electronics,
threads and the flexible lead are not reconstructed.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""
from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "digiten-flow-sensor.step"
PAYLOAD_PATH = _here.parent / "digiten-flow-sensor.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

# External dimensions fitted to MINI 2 observations; see scan-evidence.json.
# Interface stations are on the collet faces, not at the offset housing centre.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('digiten_flow_sensor')
globals().update({name: _reference_values[name] for name in ('port_face', 'port_dia', 'port_neck_radius', 'port_neck_end', 'port_collar_end', 'port_collar_radii', 'port_collet_radius', 'port_mouth_radius', 'port_mouth_depth', 'body_dia', 'body_len', 'body_center_x', 'body_center_z', 'label_y', 'underside_y', 'housing_profile', 'boss_x', 'boss_z', 'boss_radius', 'boss_y_range', 'screw_head_radius', 'screw_head_y_range', 'wire_root', 'wire_root_width', 'wire_root_depth', 'wire_boss_dia', 'wire_boss_len')})

# Axial Y/radius profile of the fixed housing, excluding its four bosses.


def inlet():
    return _reference_data('digiten_flow_sensor', 'inlet', (), {})


def outlet():
    return _reference_data('digiten_flow_sensor', 'outlet', (), {})


def wire_exit():
    return _reference_data('digiten_flow_sensor', 'wire_exit', (), {})


def mounting_profile(sign):
    'Fixed port exterior from the housing outward: (start, end, r0, r1).\n\n    Distances are measured outward from the origin along sign*X. The separate\n    collet starts at port_collar_end and is outside these bearing sections.\n    '
    return _reference_data('digiten_flow_sensor', 'mounting_profile', (sign,), {})


def main():
    print("digiten-flow-sensor")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
