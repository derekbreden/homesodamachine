"""Compressor — the refrigeration loop's cold end driver, as a donor primitive.

Hermetic reciprocating compressor harvested from the Antarctic Star HZB-12/Q donor
(NingBo Anuodan / HuaJun HD48Y11A, 110-120 V 60 Hz, ~90-120 W class) — the teardown
is `../ice-maker/README.md`. There is no vendor solid and no scan: the part was
calipered, and what the pack takes of it is its ENVELOPE and its bolt pattern, which
is what this module draws.

Coordinate frame
----------------
- Z = 0 is the MOUNTING PLANE, the plate's underside. The plate stands the shell
  [15](BASE_Z) up, and the shell's own [120](SHELL_Z) carries the crown to
  [135](OVERALL_H).
- The PLATE is centered on the origin, so its four Ø[14](MOUNT_D) holes stand symmetric
  about it on a [67](MOUNT_PITCH_X) x [131](MOUNT_PITCH_Y) rectangle, each inset
  [14.5](MOUNT_INSET) from both edges it sits in from. A floor that carries this pattern
  carries it about its own center.
- The SHELL is centered on X and offset [10](SHELL_OFFSET_Y) on Y, so the plate reaches
  [27.5](PLATE_REACH_LONG) past it at -Y and [7.5](PLATE_REACH_SHORT) at +Y.
- The POWER BOX stands in that long reach, hanging off the shell with air under it:
  [45](POWER_X) across, [27.5](POWER_Y) deep — the reach exactly — and [45](POWER_Z) tall,
  its underside at [30](POWER_Z0), its aft face on the shell's own tangent plane at
  y = [-52.5](SHELL_TANGENT_Y). **-Y is the power end.** It is narrower than the plate,
  which reaches [25.5](POWER_FLANK_REACH) past each of its flanks — so a body pressed on a
  flank stands over the can's own metal, and `power_face()` is the +X one.

The suction, discharge and process stubs are not modeled. All three are STATIONS instead —
`stations()` for the two that are in the loop, `process_tube()` for the one that is not —
so a line brazed into one and a valve clamped on one both answer to the can. The box
carries the compressor's terminal block and clip-on
PTC start relay under the donor's own moulded cover, so it is the one feature that tells the
two ends apart: the bolt pattern is symmetric about the origin, the box is not.

The shell is WIDER THAN ITS OWN PLATE — [110](SHELL_X) across against the plate's
[96](BASE_X) — so the widest thing on the part is its belly, overhanging
[7](SHELL_OVERHANG_X) each side and starting [15](BASE_Z) up. A floor sees
[96](BASE_X) x [160](BASE_Y); a wall beside it sees [110](SHELL_X), and sees it
one plate-thickness off the deck.

Run:
    tools/cad-venv/bin/python hardware/reference/compressor/compressor.py
    tools/cad-venv/bin/python hardware/reference/compressor/compressor.py selftest
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from _cadq_export import export_assembly
from _materials import C_COMP, one_body  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402

# --- Calipered off the donor ----------------------------------------------
BASE_X = 96.0          # the stamped base plate, across the machine
BASE_Y = 160.0         #   and along it — the plate is the longer body of the two
BASE_Z = 15.0          # what the plate stands the shell off the mounting plane

SHELL_X = 110.0        # the shell's minor axis
SHELL_Y = 125.0        #   and its major — a cylinder pressed slightly oblong
SHELL_Z = 120.0        # plate crown to shell crown

SHELL_OFFSET_Y = 10.0  # the shell stands off the plate's own center by this much

MOUNT_D = 14.0         # the four holes through the plate
MOUNT_INSET = 14.5     #   center to plate edge, the same figure on both axes

POWER_X = 45.0         # the power components' box, across the machine
POWER_Y = 27.5         #   along it — the plate's long reach, exactly
POWER_Z = 45.0         # its own standing height
POWER_GAP = 15.0       # and the air under it — the box hangs off the shell, not the plate

# --- What those give ------------------------------------------------------
OVERALL_H = BASE_Z + SHELL_Z                       # [135](OVERALL_H), crown off the deck
MOUNT_PITCH_X = BASE_X - 2.0 * MOUNT_INSET         # [67](MOUNT_PITCH_X), center to center
MOUNT_PITCH_Y = BASE_Y - 2.0 * MOUNT_INSET         # [131](MOUNT_PITCH_Y)
SHELL_OVERHANG_X = (SHELL_X - BASE_X) / 2.0        # [7](SHELL_OVERHANG_X) each side
PLATE_REACH_LONG = (BASE_Y - SHELL_Y) / 2.0 + SHELL_OFFSET_Y    # [27.5](PLATE_REACH_LONG) at -Y
PLATE_REACH_SHORT = (BASE_Y - SHELL_Y) / 2.0 - SHELL_OFFSET_Y   # [7.5](PLATE_REACH_SHORT) at +Y
# The plate a hole leaves between itself and the edge it is inset from.
MOUNT_LIGAMENT = MOUNT_INSET - MOUNT_D / 2.0  # [7.5](MOUNT_LIGAMENT)
# The shell's own -Y extreme, which the box's aft face stands on. The ellipse reaches it at
# one point, x = 0, so the two bodies meet along a line rather than over a face.
SHELL_TANGENT_Y = SHELL_OFFSET_Y - SHELL_Y / 2.0   # [-52.5](SHELL_TANGENT_Y)
POWER_Y0 = -BASE_Y / 2.0                           # the plate's own -Y edge
POWER_Z0 = BASE_Z + POWER_GAP                      # [30](POWER_Z0), the box's underside
POWER_Z1 = POWER_Z0 + POWER_Z                      # [75](POWER_Z1), the box's crown
# What the plate still reaches past either FLANK of the box. The box is narrower than the
# plate it stands on, so a body laid on a flank stands over the can's own plate — where the
# -Y face has nothing past it at all, that being the plate's own edge (`power_face`).
POWER_FLANK_REACH = BASE_X / 2.0 - POWER_X / 2.0    # [25.5](POWER_FLANK_REACH) each side
# Where the two loop stubs leave the shell, up its standing height. Both are on a tangent
# line; only the height along it is free, and these are the heights the donor brazes at.
DISCHARGE_Z = 75.0
SUCTION_Z = 60.0
# THE THIRD STUB, the one that is not in the loop: the process tube, a short copper stub
# pinched and brazed shut at the factory (`../ice-maker/README.md` "Process tube"). It
# leaves the -X tangent, the same flank the suction does, standing above it — so the saddle
# and the suction leg share one lane down the machine's west side, and the valve is reached
# from beside the can rather than over it. Like the other two it is a STATION and not a solid.
PROCESS_Z = 100.0
# How far out along that stub the saddle bands. The stub is ~50 long and its tip stays
# pinched, so the clamp goes on the middle of it.
PROCESS_CLAMP = 20.0
# What the stub stands above the suction's own, the other station on this tangent.
PROCESS_OVER_SUCTION = PROCESS_Z - SUCTION_Z   # [40](PROCESS_OVER_SUCTION)


def mount_pattern():
    """The four hole centers on the mounting plane — the corners of a
    [67](MOUNT_PITCH_X) x [131](MOUNT_PITCH_Y) rectangle, symmetric about the origin."""
    return [(sx * MOUNT_PITCH_X / 2.0, sy * MOUNT_PITCH_Y / 2.0)
            for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def power_face():
    """The +X FLANK of the POWER BOX, as `(centre, outward axis)` in this frame.

    The box is the donor's own moulded cover over the terminal block and the PTC start
    relay, and every face of it is that same moulding — so a case pressed on this one is
    pressed on the cover as surely as on the box's front.

    WHAT THIS FLANK HAS THAT THE FRONT DOES NOT is that nothing standing proud of it costs
    the machine any DEPTH. The box's -Y face is the deepest plane on the whole donor —
    `POWER_Y0` is the plate's own edge — so a body laid there is the frontmost thing in the
    cabinet and the appliance's front wall stands off IT. Laid on the flank instead, the same
    body stands over the plate's own [25.5](POWER_FLANK_REACH) mm of reach at +X, in air the
    can already owns, and the front plane answers to the box.

    The gap the clamp's leaves press runs the box's whole footprint, so it is reached from
    this face as readily as from the front — and the shell is not a fence here at all, since
    the box's aft plane IS the shell's own tangent and this face's whole width stands forward
    of it."""
    return ((POWER_X / 2.0, POWER_Y0 + POWER_Y / 2.0, (POWER_Z0 + POWER_Z1) / 2.0),
            (1.0, 0.0, 0.0))


def process_tube():
    """Where the piercing valve bands the PROCESS TUBE, as `(the point on the stub's own
    axis, the stub's outward direction)` in this frame.

    The stub leaves the -X tangent, `PROCESS_Z` up — the same flank the suction leaves by,
    [40](PROCESS_OVER_SUCTION) above it, so the saddle bands the copper in the lane that leg
    already runs in and both are reached from the machine's west side.

    The point is on the STUB: `PROCESS_CLAMP` out along the tube, where the clamp grips."""
    return ((-SHELL_X / 2.0 - PROCESS_CLAMP, SHELL_OFFSET_Y, PROCESS_Z), (-1.0, 0.0, 0.0))


def stations() -> dict:
    """The two ends of the sealed loop this body carries, in its own frame.

    An ELLIPSE HAS NO FLAT FACE. This shell touches a neighbour's plane along ONE LINE — the
    tangent at its own extreme — so both picks stand on a tangent and nowhere else, where a
    box would let a station stand anywhere on a wall. Both stand at `SHELL_OFFSET_Y`, because
    that is where the two X extremes fall: discharge on the +X tangent, suction on the -X one,
    the two of them on opposite flanks of the same can. A neighbour mated to this body meets it
    there, which is what the two of them read as one point."""
    return {
        "refrig-discharge": ((SHELL_X / 2.0, SHELL_OFFSET_Y, DISCHARGE_Z), (1.0, 0.0, 0.0)),
        "refrig-suction":   ((-SHELL_X / 2.0, SHELL_OFFSET_Y, SUCTION_Z), (-1.0, 0.0, 0.0)),
    }


def stations_hold():
    """Hold both picks inside the shell's standing height."""
    for name, (pos, _axis) in stations().items():
        if not (BASE_Z <= pos[2] <= OVERALL_H):
            raise ValueError(
                f"compressor {name} stands at z = {pos[2]:g}, outside the shell's own "
                f"{BASE_Z:g}..{OVERALL_H:g} — the stub has left the can it is brazed into.")


def build():
    """The three bodies as the pack carries them: the plate on the mounting plane with its
    four holes through it, the oblong shell standing on the plate's crown offset on Y, and
    the power box filling the plate's long reach at -Y."""
    part = cq.Workplane("XY").box(BASE_X, BASE_Y, BASE_Z, centered=(True, True, False))
    shell = (
        cq.Workplane("XY", origin=(0.0, SHELL_OFFSET_Y, BASE_Z))
        .ellipse(SHELL_X / 2.0, SHELL_Y / 2.0)
        .extrude(SHELL_Z)
    )
    power = (
        cq.Workplane("XY", origin=(0.0, POWER_Y0 + POWER_Y / 2.0, POWER_Z0))
        .rect(POWER_X, POWER_Y)
        .extrude(POWER_Z)
    )
    part = part.union(shell).union(power)
    for x, y in mount_pattern():
        part = part.cut(cq.Solid.makeCylinder(
            MOUNT_D / 2.0, BASE_Z, cq.Vector(x, y, 0.0), cq.Vector(0, 0, 1)))
    return part.val()


# --- Holds ----------------------------------------------------------------

def power_hold():
    """Hold the box to the reach it fills: end to end on Y, standing clear of the plate with
    air under it, and off the mounts below its footprint.

    It hangs on the SHELL, not on the plate — `POWER_GAP` of air under it — so a driver still
    reaches the plate beneath, and its aft face closes on the shell's own tangent."""
    if abs(POWER_Y0 + POWER_Y - SHELL_TANGENT_Y) > 1e-9:
        raise ValueError(
            f"the box runs y {POWER_Y0:g}..{POWER_Y0 + POWER_Y:g} and the plate's long reach "
            f"ends at the shell's tangent y = {SHELL_TANGENT_Y:g} — the box no longer fills "
            f"the reach the shell's own offset opened for it.")
    if POWER_Z0 <= BASE_Z + 1e-9:
        raise ValueError(
            f"the box's underside stands at z {POWER_Z0:g} against the plate's crown at "
            f"{BASE_Z:g} — it is sitting on the plate rather than hanging off the shell.")
    for x, y in mount_pattern():
        if abs(x) < POWER_X / 2.0 + MOUNT_D / 2.0 and POWER_Y0 <= y <= POWER_Y0 + POWER_Y:
            raise ValueError(
                f"the mount at ({x:g}, {y:g}) stands under the box — a Ø{MOUNT_D:g} hole "
                f"{abs(x) - POWER_X / 2.0:g} outboard of a box face is not a hole a driver "
                f"reaches.")


def mounts_hold():
    """All four holes stand inside the plate they are cut in, and clear of the shell — a
    hole the belly covers is a hole no bolt reaches."""
    if MOUNT_LIGAMENT < 0.0:
        raise ValueError(
            f"a Ø{MOUNT_D:g} hole inset {MOUNT_INSET:g} breaks out of the plate's own "
            f"edge by {-MOUNT_LIGAMENT:g} — that is an open slot, and the donor's plate "
            f"is bolted through closed holes.")
    for x, y in mount_pattern():
        if abs(x) >= SHELL_X / 2.0:
            continue                       # outboard of the belly on X, nothing above it
        half = (SHELL_Y / 2.0) * math.sqrt(1.0 - (x / (SHELL_X / 2.0)) ** 2)
        if abs(y - SHELL_OFFSET_Y) < half:
            raise ValueError(
                f"the mount at ({x:g}, {y:g}) stands under the shell's own belly — the "
                f"shell reaches {SHELL_OFFSET_Y - half:g}..{SHELL_OFFSET_Y + half:g} on Y "
                f"at that X, and a bolt cannot be driven through it.")


# --- controls -------------------------------------------------------------

def _docvars():
    """Every figure this part's prose quotes, from the constant that owns it."""
    plain = ("BASE_X", "BASE_Y", "BASE_Z", "SHELL_X", "SHELL_Y", "SHELL_Z",
             "SHELL_OFFSET_Y", "MOUNT_D", "MOUNT_INSET", "OVERALL_H",
             "MOUNT_PITCH_X", "MOUNT_PITCH_Y", "SHELL_OVERHANG_X",
             "PLATE_REACH_LONG", "PLATE_REACH_SHORT", "MOUNT_LIGAMENT",
             "POWER_X", "POWER_Y", "POWER_Z", "POWER_Z0", "POWER_Z1", "SHELL_TANGENT_Y",
             "POWER_FLANK_REACH",
             "PROCESS_Z", "PROCESS_CLAMP", "PROCESS_OVER_SUCTION")
    return {name: f"{globals()[name]:g}" for name in plain}


def selftest():
    power_hold()
    mounts_hold()
    stations_hold()
    (fx, _fy, fz), _fa = power_face()
    (px, _py, pz), _pa = process_tube()
    return [
        f"  power face centred at ({fx:g}, {fz:g}) on the box's own +X flank, "
        f"{POWER_FLANK_REACH:g} of plate past it",
        f"  both loop stubs stand on a shell tangent — discharge +X at z {DISCHARGE_Z:g}, "
        f"suction -X at z {SUCTION_Z:g}",
        f"  the process stub leaves -X at z {pz:g}, {PROCESS_OVER_SUCTION:g} over the "
        f"suction's own station, and the saddle bands it at x {px:g}",
        f"  envelope stands {SHELL_X:g} x {BASE_Y:g} x {OVERALL_H:g} off the mounting plane",
        f"  shell is the pressed oblong, {SHELL_X:g} x {SHELL_Y:g}, not a cylinder",
        f"  the box fills the long reach, y {POWER_Y0:g}..{SHELL_TANGENT_Y:g}, "
        f"z {POWER_Z0:g}..{POWER_Z1:g} with {POWER_GAP:g} of air under it",
        f"  four mounts clear the belly and the box, {MOUNT_LIGAMENT:g} of plate outboard "
        f"of each",
    ]


def main():
    part = build()
    bb = part.BoundingBox()
    print("compressor — HuaJun HD48Y11A, harvested (Antarctic Star HZB-12/Q)")
    print(f"  X[{bb.xmin:.1f}, {bb.xmax:.1f}]  Y[{bb.ymin:.1f}, {bb.ymax:.1f}]"
          f"  Z[{bb.zmin:.1f}, {bb.zmax:.1f}]")
    print(f"  plate  {BASE_X:g} x {BASE_Y:g} x {BASE_Z:g}, centered on the origin")
    print(f"  shell  {SHELL_X:g} x {SHELL_Y:g} ellipse x {SHELL_Z:g}, "
          f"offset {SHELL_OFFSET_Y:g} on Y")
    print(f"  power  {POWER_X:g} x {POWER_Y:g} x {POWER_Z:g}, y[{POWER_Y0:g}, "
          f"{SHELL_TANGENT_Y:g}] z[{BASE_Z:g}, {POWER_Z1:g}] — the -Y end")
    print(f"  belly overhangs the plate {SHELL_OVERHANG_X:g} each side, from {BASE_Z:g} up")
    print(f"  plate reaches {PLATE_REACH_LONG:g} past the shell at -Y, "
          f"{PLATE_REACH_SHORT:g} at +Y")
    print(f"  4x Ø{MOUNT_D:g} on {MOUNT_PITCH_X:g} x {MOUNT_PITCH_Y:g}, "
          f"{MOUNT_LIGAMENT:g} of plate outboard of each")

    out = _here.parent / "compressor.step"
    export_assembly(one_body(part, "compressor", C_COMP), str(out))
    print(f"-> {out.name}")

    variables = _docvars()
    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("compressor selftest OK")
    else:
        main()
