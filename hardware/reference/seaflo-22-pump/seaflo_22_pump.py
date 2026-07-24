"""SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand diaphragm pump (B0166UBJX4)
— the appliance's `seaflo-pump`, transferring tap water against CO2
back-pressure into the carbonator. 3/8" hose-barb inlet + outlet on the head
(hardware/assembly/internal-plumbing.md).

External envelope: a motor can, a pump head carrying the two barb ports and the
pressure switch, on a mounting base whose four feet splay wider than the body.
The internal diaphragm mechanism is not modeled.

The two 3/8" barbs leave the head's two opposite side faces (±Y), each pointing
straight out along its own ±Y axis — perpendicular to the motor axis, near the
-X end and at head mid-height. The pressure switch occupies the head's -X end
face, opposite the motor. (The casting marks the ports IN and OUT; this model
puts IN/suction on -Y and OUT/discharge on +Y — a mirror pair across the motor
axis, so the two sides are geometrically interchangeable.)

Frame: +X = motor axis (head at -X), base underside at Z = 0, centered on Y.
The barbs leave the head's ±Y side faces; the -X end face carries the switch.

Run:
    tools/cad-venv/bin/python hardware/reference/seaflo-22-pump/seaflo_22_pump.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

BASE_L, BASE_W, BASE_T = 178.0, 98.0, 5.0     # mounting base (feet splay to BASE_W)
MOTOR_D, MOTOR_L = 56.0, 92.0                  # motor can
HEAD_L, HEAD_W, HEAD_H = 66.0, 80.0, 56.0      # pump head block (carries ports)
SWITCH_PROJ, SWITCH_W, SWITCH_H = 18.0, 40.0, 36.0  # pressure switch, on the -X end face
PORT_D, PORT_L = 13.0, 16.0                    # 3/8" hose-barb inlet + outlet
FOOT_R = 6.0                                   # base corner radius


HEAD_FACE_X = -BASE_L / 2.0 + 6.0              # the head's -X end face (carries the switch)
PORT_X = HEAD_FACE_X + 20.0                    # barb centerline, ~20 mm inboard of the -X end
PORT_Z = BASE_T + HEAD_H / 2.0                 # both barbs at the head's mid-height
PORT_FACE_Y = HEAD_W / 2.0                     # the ±Y side faces the barbs leave from
PORT_TIP_Y = PORT_FACE_Y + PORT_L              # the barb tips, where the hose slips on


def suction():
    """The 3/8" hose-barb the supply line slips over: (position, outward axis).
    On the head's -Y side face, pointing straight out along -Y. The casting
    marks IN and OUT; IN/suction is modeled on -Y."""
    return (PORT_X, -PORT_TIP_Y, PORT_Z), (0.0, -1.0, 0.0)


def discharge():
    """The 3/8" hose-barb feeding the carbonator: (position, outward axis) —
    the suction's mirror across the motor axis, on the +Y side face, pointing
    straight out along +Y."""
    return (PORT_X, PORT_TIP_Y, PORT_Z), (0.0, 1.0, 0.0)


def build():
    """Motor can + head + pressure switch on a wide base; the two 3/8" barbs
    leave the head's ±Y side faces; base underside at Z = 0, motor axis along +X."""
    base = (
        cq.Workplane("XY")
        .box(BASE_L, BASE_W, BASE_T, centered=(True, True, False))
        .edges("|Z").fillet(FOOT_R)
    )
    motor_cx = BASE_L / 2.0 - MOTOR_L / 2.0 - 8.0     # motor toward +X
    motor = cq.Solid.makeCylinder(
        MOTOR_D / 2.0, MOTOR_L,
        cq.Vector(motor_cx - MOTOR_L / 2.0, 0, BASE_T + MOTOR_D / 2.0),
        cq.Vector(1, 0, 0),
    )
    head_x0 = HEAD_FACE_X
    head = (
        cq.Workplane("XY")
        .box(HEAD_L, HEAD_W, HEAD_H, centered=(False, True, False))
        .translate((head_x0, 0, BASE_T))
    )
    # Pressure switch protruding from the head's -X end face, opposite the motor.
    switch = (
        cq.Workplane("XY")
        .box(SWITCH_PROJ, SWITCH_W, SWITCH_H, centered=(False, True, True))
        .translate((head_x0 - SWITCH_PROJ, 0, PORT_Z))
    )
    part = base.union(head).union(switch).union(motor)
    # Two 3/8" hose-barb ports on the head's ±Y side faces, each pointing straight out.
    for sy in (-1, 1):
        barb = cq.Solid.makeCylinder(
            PORT_D / 2.0, PORT_L,
            cq.Vector(PORT_X, sy * PORT_FACE_Y, PORT_Z),
            cq.Vector(0, sy, 0),
        )
        part = part.union(barb)
    return part


def main():
    part = build()
    bb = part.val().BoundingBox() if hasattr(part, "val") else part.BoundingBox()
    print("SEAFLO 22-Series diaphragm pump")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  base {BASE_L}×{BASE_W}, motor Ø{MOTOR_D}×{MOTOR_L}, head {HEAD_L}×{HEAD_W}×{HEAD_H}")
    for label, (pos, axis) in (("suction  ", suction()), ("discharge", discharge())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "seaflo-22-pump.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
