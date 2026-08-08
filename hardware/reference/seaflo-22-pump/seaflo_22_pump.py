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

THE CAN'S AXIS IS THE BODY'S DATUM. The motor is bolted to the head on that line,
the bracket is built to the barrel it holds, and every station on the head is
placed about it. The can's top, the head block's top and the pressure switch's
top all come out on one plane at `CROWN_Z`, and what hangs below the head at the
port end is a 30 mm boss — the lowest casting on the body, with the head block's
own underside standing clear above it.

That crown stands 67 over the foot underside, 5 under the drawing's labeled 72 —
the same gap the length carries.

Dimensions come from SEAFLO's dimensioned drawing for the 22 Series (Marine & RV
catalog p.15, and the same drawing as an image on the Amazon listing). Labeled
values — 187 long, 72 tall, 80 across the barb tips, Ø10.4 barbs — are taken as
given. Everything else is scaled off that drawing's linework at its own 57 mm
hole pitch, which leaves the part 178.5 mm long against the labeled 187; the
model carries that 8.5 mm in the pressure-switch block, the least-constrained
feature.

THE FOOT PAD IS THE ONE FEATURE MEASURED OFF THE PART. It is what the machine
bolts, so its four bores and their pattern are calipered rather than read — Ø6.0
on 59 x 79, each centre 10 off both edges it stands near, which puts the pad at
79 x 99 against the drawing's 98 across the feet.

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
OVERALL_H = 72.0         # 2.83in, foot underside to the top; `CROWN_Z` is what the
                         #   linework builds, and stands 5 under it
PORT_SPAN = 80.0         # 3.15in, across the two barb tips
PORT_D = 10.4            # 0.41in Ø10.40, the 3/8" hose barb

# THE MOUNTING PATTERN IS OFF THE PART, not off the drawing — calipers on the pad the holes are
# cut in, which is stiff rubber and reads a little over the drawing's Ø5.00 on 57 x 79.
HOLE_D = 6.0             # Ø6.00, one hole in each corner of the foot pad
HOLE_PITCH = (59.0, 79.0)  # centre to centre, along the motor axis then across it
HOLE_INSET = 10.0        # each centre off BOTH pad edges it stands near
# So the pad is the pattern and its inset all round, and every one of its four edges is one
# `HOLE_INSET` outboard of the two holes on it.
FOOT_L = HOLE_PITCH[0] + 2.0 * HOLE_INSET   # 79, along the motor axis
FOOT_SPAN = HOLE_PITCH[1] + 2.0 * HOLE_INSET  # 99, across the mounting feet (labeled 98)

# Scaled off the same drawing's linework.
HEAD_W = 54.0            # the block the ports are on
FLANGE_W = 70.0          # the head's wide band where it meets the motor
MOTOR_D = 54.0           # motor can
SWITCH_W = 44.0          # pressure switch
BOSS_W = 30.0            # the boss under the head's port end

# The motor axis: the head's mid-height, the line the bracket's cradle is struck on, and the
# datum every station below is placed about.
MOTOR_Z = 40.0
CROWN_Z = MOTOR_Z + MOTOR_D / 2.0    # 67.0 — the can's crown, the highest the casting reaches
HEAD_Z0, HEAD_Z1 = 11.0, CROWN_Z  # the head block, its top on that same crown
BOSS_Z0 = 8.0                    # the boss under it, the body's lowest casting
PORT_Z = 48.0                    # both barbs, above head mid-height
SWITCH_Z0, SWITCH_Z1 = 32.0, CROWN_Z
FOOT_T, CRADLE_Z1 = 8.0, 15.0    # foot pad thickness; the cradle up to the can

# Stations along the motor axis, motor rear at +OVERALL_L/2.
X_MOTOR_REAR = OVERALL_L / 2.0             # +93.5, the can's rear cap
X_SWITCH_FACE = -OVERALL_L / 2.0           # -93.5
X_HEAD_JOINT = 3.1                         # where the can meets the head flange
X_FLANGE_END = -17.9                       # flange band -> narrow port block
X_HEAD_END = -49.8                         # port block -> pressure switch
FOOT_MID_X = 45.2                          # the bracket's own centre on the motor axis
FOOT_X = (FOOT_MID_X - FOOT_L / 2.0,       # the bracket's foot footprint
          FOOT_MID_X + FOOT_L / 2.0)
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


def mount_holes():
    """The four Ø`HOLE_D` bores through the foot pad, as `(x, y)` in the pump's own frame —
    one in each corner, `HOLE_INSET` off both pad edges it stands near.

    A screw through one of these is the only thing on this pump that fastens it to anything:
    the barbs are moulded, the cradle is a saddle, and the pad is what the machine bolts."""
    return tuple((FOOT_MID_X + sx * HOLE_PITCH[0] / 2.0, sy * HOLE_PITCH[1] / 2.0)
                 for sx in (-1, 1) for sy in (-1, 1))


def mount_seat_z():
    """The plane the pad bears on — its own underside, and the pump's Z datum."""
    return 0.0


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
    head's top and the switch's top all land on `CROWN_Z`."""
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
    # The four mounting bores, sunk through the pad they are cut in. Nothing else stands over
    # them: the cradle is `MOTOR_D + 2` wide and they lie outboard of it.
    for hx, hy in mount_holes():
        part = part.cut(cq.Solid.makeCylinder(
            HOLE_D / 2.0, FOOT_T, cq.Vector(hx, hy, 0.0), cq.Vector(0, 0, 1)))
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
    print(f"  overall {OVERALL_L}L x {FOOT_SPAN}W(feet) x {CROWN_Z}H "
          f"(labeled {OVERALL_H}), "
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
