"""SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand diaphragm pump (B0166UBJX4,
model SFDP1-013-100-22) — the appliance's `seaflo-pump`, transferring tap water
against CO2 back-pressure into the carbonator. 3/8" hose-barb inlet + outlet on
the head (hardware/assembly/internal-plumbing.md).

External envelope: a motor can bolted straight onto the pump head, the head
carrying the two barb ports and the pressure switch, on a mounting bracket whose
four rubber feet splay wider than any of it. The internal diaphragm mechanism is
not modeled.

The head is a narrow block — 54 mm across — and the two 3/8" barbs are short
stubs off its ±Y side faces, 13 mm each, which is what carries the pump out to
its 80 mm published width across the ports. Nearer the motor the head widens to
a 70 mm flange band. The ports sit above head mid-height and toward the switch
end. The pressure switch occupies the upper part of the head's -X end face,
opposite the motor. (The casting marks the ports IN and OUT; this model puts
IN/suction on -Y and OUT/discharge on +Y — a mirror pair across the motor axis,
so the two sides are geometrically interchangeable.)

THE PUMP'S 72 mm IS THE CAN'S OWN CROWN. The motor axis is on the head's
mid-height and the can is Ø54, so the can's top, the head block's top and the
pressure switch's top all come out on that one plane — the published overall
height is three surfaces and not a boss. What hangs below the head at the port
end is a 30 mm boss, the lowest casting on the body, and the head block's own
underside stands clear above it.

Dimensions come from SEAFLO's dimensioned drawing for the 22 Series (Marine & RV
catalog p.15, and the same drawing as an image on the Amazon listing). Labeled
values — 187 long, 72 tall, 80 across the barb tips, 98 across the feet, Ø10.4
barbs, Ø5.0 mounting holes on a 57 x 79 pattern — are taken as given. Everything
else is scaled off that drawing's linework at its 57 mm hole pitch, which leaves
the part 178.5 mm long against the labeled 187; the model carries that 8.5 mm in
the pressure-switch block, the least-constrained feature.

Frame: +X = motor axis (head at -X), foot underside at Z = 0, centered on Y.
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

# Labeled on the SEAFLO 22-Series drawing.
OVERALL_L = 187.0        # 7.35in, motor rear to switch face
OVERALL_H = 72.0         # 2.83in, foot underside to the head's top boss
PORT_SPAN = 80.0         # 3.15in, across the two barb tips
FOOT_SPAN = 98.0         # 3.86in, across the mounting feet
PORT_D = 10.4            # 0.41in Ø10.40, the 3/8" hose barb
HOLE_D = 5.0             # 0.20in Ø5.00 mounting holes,
HOLE_PITCH = (57.0, 79.0)  #   on a 57 x 79 pattern (not cut in this envelope)

# Scaled off the same drawing's linework.
HEAD_W = 54.0            # the block the ports are on
FLANGE_W = 70.0          # the head's wide band where it meets the motor
MOTOR_D = 54.0           # motor can
SWITCH_W = 44.0          # pressure switch
BOSS_W = 30.0            # the boss under the head's port end

HEAD_Z0, HEAD_Z1 = 16.0, 72.0    # the head block, its top on the pump's crown
BOSS_Z0 = 13.0                   # the boss under it, the body's lowest casting
MOTOR_Z = 45.0                   # motor axis, on the head's mid-height
PORT_Z = 53.0                    # both barbs, above head mid-height
SWITCH_Z0, SWITCH_Z1 = 37.0, 72.0
FOOT_T, CRADLE_Z1 = 8.0, 15.0    # foot pad thickness; the cradle up to the can

# Stations along the motor axis, motor rear at +OVERALL_L/2.
X_MOTOR_REAR = OVERALL_L / 2.0             # +93.5, the can's rear cap
X_SWITCH_FACE = -OVERALL_L / 2.0           # -93.5
X_HEAD_JOINT = 3.1                         # where the can meets the head flange
X_FLANGE_END = -17.9                       # flange band -> narrow port block
X_HEAD_END = -49.8                         # port block -> pressure switch
FOOT_X = (7.2, 83.2)                       # the bracket's foot footprint
PORT_X = -36.6                             # barb centerline

PORT_FACE_Y = HEAD_W / 2.0                 # the ±Y side faces the barbs leave
PORT_L = PORT_SPAN / 2.0 - PORT_FACE_Y     # 13.0 mm of barb, each side
PORT_TIP_Y = PORT_SPAN / 2.0               # the barb tips, where the hose slips on


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


def _box(x0, x1, w, z0, z1):
    """A body given its X span, its full Y width about the axis, and its Z span."""
    return (
        cq.Workplane("XY")
        .box(x1 - x0, w, z1 - z0, centered=(False, True, False))
        .translate((x0, 0, z0))
    )


def build():
    """Motor can bolted to the head, the head carrying the two 3/8" barbs on its
    ±Y side faces and the pressure switch on its -X end, all on the mounting
    bracket; foot underside at Z = 0, motor axis along +X. The can's crown, the
    head's top and the switch's top all land on `OVERALL_H`."""
    # Mounting bracket: the four splayed feet as one pad, and the cradle that
    # carries them up to the motor can.
    feet = (
        cq.Workplane("XY")
        .box(FOOT_X[1] - FOOT_X[0], FOOT_SPAN, FOOT_T, centered=(False, True, False))
        .edges("|Z").fillet(6.0)
        .translate((FOOT_X[0], 0, 0))
    )
    cradle = _box(FOOT_X[0], FOOT_X[1], MOTOR_D + 2.0, FOOT_T, CRADLE_Z1)
    # Motor can, running into the head flange so the two are one body.
    motor = cq.Solid.makeCylinder(
        MOTOR_D / 2.0, X_MOTOR_REAR - (X_HEAD_JOINT - 9.0),
        cq.Vector(X_HEAD_JOINT - 9.0, 0, MOTOR_Z),
        cq.Vector(1, 0, 0),
    )
    flange = _box(X_FLANGE_END, X_HEAD_JOINT, FLANGE_W, HEAD_Z0, HEAD_Z1)
    head = _box(X_HEAD_END, X_FLANGE_END, HEAD_W, HEAD_Z0, HEAD_Z1)
    boss = _box(PORT_X - BOSS_W / 2.0, PORT_X + BOSS_W / 2.0,
                BOSS_W, BOSS_Z0, HEAD_Z0)
    switch = _box(X_SWITCH_FACE, X_HEAD_END, SWITCH_W, SWITCH_Z0, SWITCH_Z1)

    part = feet.union(cradle).union(motor).union(flange).union(head)
    part = part.union(boss).union(switch)
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
    print("SEAFLO 22-Series diaphragm pump (SFDP1-013-100-22)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  overall {OVERALL_L}L x {FOOT_SPAN}W(feet) x {OVERALL_H}H, "
          f"{PORT_SPAN} across the barb tips")
    print(f"  motor Ø{MOTOR_D}, head {HEAD_W} wide ({FLANGE_W} at the flange), "
          f"barbs Ø{PORT_D} x {PORT_L}")
    for label, (pos, axis) in (("suction  ", suction()), ("discharge", discharge())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "seaflo-22-pump.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
