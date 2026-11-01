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
port_face = 30.5
port_dia = 18.3                 # largest fixed collar diameter
port_neck_radius = 7.95
port_neck_end = 19.6
port_collar_end = 26.8
port_collar_radii = (8.95, 9.15)
port_collet_radius = 5.0
port_mouth_radius = 3.25
port_mouth_depth = 6.0          # visible mouth only; no internal insertion stop
body_dia = 35.0                 # outer cover flange
body_len = 28.3                 # overall depth, including screw heads
body_center_x = 0.0
body_center_z = 8.9
label_y = 18.7
underside_y = -9.4
boss_x = 12.5
boss_z = 14.0
boss_radius = 3.45
boss_y_range = (0.0, 17.2)
screw_head_radius = 2.65
screw_head_y_range = (17.2, 18.9)
wire_root = (0.0, 14.8, 26.5)
wire_root_width = 6.0
wire_root_depth = 3.0
wire_boss_dia = wire_root_width # compatibility: the lead root is a slot
wire_boss_len = 1.5


def inlet():
    return (-port_face, 0.0, 0.0), (-1.0, 0.0, 0.0)


def outlet():
    return (port_face, 0.0, 0.0), (1.0, 0.0, 0.0)


def wire_exit():
    return wire_root, (0.0, 0.0, 1.0)


def mounting_profile(sign):
    """Fixed port exterior from the housing outward: (start, end, r0, r1).

    Distances are measured outward from the origin along sign*X. The separate
    collet starts at port_collar_end and is outside these bearing sections.
    """
    return ((15.5, port_neck_end, port_neck_radius, port_neck_radius),
            (port_neck_end, port_collar_end, *port_collar_radii))


def main():
    print("digiten-flow-sensor")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
