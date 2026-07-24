"""SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand diaphragm pump (B0166UBJX4)
— the appliance's `seaflo-pump`, transferring tap water against CO2
back-pressure into the carbonator. 3/8" hose-barb inlet + outlet on the head
(hardware/assembly/internal-plumbing.md).

External envelope: a motor can, a pump head carrying the two barb ports and the
pressure switch, on a mounting base whose four feet splay wider than the body.
The internal diaphragm mechanism is not modeled.

Frame: +X = motor axis (head at -X, carrying the ports), base underside at
Z = 0, centered on Y.

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
SWITCH_L, SWITCH_W, SWITCH_H = 42.0, 34.0, 13.0  # pressure switch on the head top
PORT_D, PORT_L = 13.0, 16.0                    # 3/8" hose-barb inlet + outlet
FOOT_R = 6.0                                   # base corner radius


HEAD_FACE_X = -BASE_L / 2.0 + 6.0              # the head's -X face, where the barbs leave
PORT_TIP_X = HEAD_FACE_X - PORT_L              # the barb tips
PORT_Y = HEAD_W / 4.0                          # the two ports' offset either side of the axis
PORT_Z = BASE_T + HEAD_H / 2.0                 # both ports at the head's mid-height


def suction():
    """The 3/8" hose-barb the supply line slips over: (position, outward axis).
    The casting marks IN and OUT; the two barbs are the same fitting on the same
    face, so which one this is falls out of how the pump is turned in its bay."""
    return (PORT_TIP_X, -PORT_Y, PORT_Z), (-1.0, 0.0, 0.0)


def discharge():
    """The 3/8" hose-barb feeding the carbonator: (position, outward axis) —
    the suction's twin, the other side of the head's axis."""
    return (PORT_TIP_X, PORT_Y, PORT_Z), (-1.0, 0.0, 0.0)


def build():
    """Motor can + head + pressure switch on a wide base, ports on the head's
    -X face; base underside at Z = 0, motor axis along +X."""
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
    switch = (
        cq.Workplane("XY")
        .box(SWITCH_L, SWITCH_W, SWITCH_H, centered=(False, True, False))
        .translate((head_x0 + 10.0, 0, BASE_T + HEAD_H))
    )
    part = base.union(head).union(switch).union(motor)
    # Two 3/8" hose-barb ports on the head's -X face, side by side in Y.
    for sy in (-1, 1):
        barb = cq.Solid.makeCylinder(
            PORT_D / 2.0, PORT_L,
            cq.Vector(head_x0, sy * PORT_Y, PORT_Z),
            cq.Vector(-1, 0, 0),
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
