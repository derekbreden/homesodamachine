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
- The PLATE is centered on the origin, so its four holes stand symmetric about it on
  an [81](MOUNT_PITCH_X) x [145](MOUNT_PITCH_Y) rectangle. A floor that carries this
  pattern carries it about its own center.
- The SHELL is centered on X and offset [10](SHELL_OFFSET_Y) on Y, so the plate reaches
  [27.5](PLATE_REACH_LONG) past it at -Y and [7.5](PLATE_REACH_SHORT) at +Y.
- The POWER BOX stands in that long reach, on the plate's crown: [45](POWER_X) across,
  [27.5](POWER_Y) deep — the reach exactly — and [45](POWER_Z) tall, its aft face on the
  shell's own tangent plane at y = [-52.5](SHELL_TANGENT_Y). **-Y is the power end.**

The suction, discharge and process stubs are not modeled. The box carries the compressor's
power components under their own shroud, so it is the one feature that tells the two ends
apart: the bolt pattern is symmetric about the origin, the box is not.

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
from _cadq_export import export_step  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402

# --- Calipered off the donor ----------------------------------------------
BASE_X = 96.0          # the stamped mounting plate, across the machine
BASE_Y = 160.0         #   and along it — the plate is the longer body of the two
BASE_Z = 15.0          # what the plate stands the shell off the mounting plane

SHELL_X = 110.0        # the shell's minor axis
SHELL_Y = 125.0        #   and its major — a cylinder pressed slightly oblong
SHELL_Z = 120.0        # plate crown to shell crown

SHELL_OFFSET_Y = 10.0  # the shell stands off the plate's own center by this much

MOUNT_D = 14.0         # the four holes through the plate
MOUNT_INSET = 7.5      #   center to plate edge, the same figure on both axes

POWER_X = 45.0         # the power components' box, across the machine
POWER_Y = 27.5         #   along it — the plate's long reach, exactly
POWER_Z = 45.0         # standing on the plate's crown

# --- What those give ------------------------------------------------------
OVERALL_H = BASE_Z + SHELL_Z                       # [135](OVERALL_H), crown off the deck
MOUNT_PITCH_X = BASE_X - 2.0 * MOUNT_INSET         # [81](MOUNT_PITCH_X), center to center
MOUNT_PITCH_Y = BASE_Y - 2.0 * MOUNT_INSET         # [145](MOUNT_PITCH_Y)
SHELL_OVERHANG_X = (SHELL_X - BASE_X) / 2.0        # [7](SHELL_OVERHANG_X) each side
PLATE_REACH_LONG = (BASE_Y - SHELL_Y) / 2.0 + SHELL_OFFSET_Y    # [27.5](PLATE_REACH_LONG) at -Y
PLATE_REACH_SHORT = (BASE_Y - SHELL_Y) / 2.0 - SHELL_OFFSET_Y   # [7.5](PLATE_REACH_SHORT) at +Y
# The plate a hole leaves between itself and the edge it is inset from. Ø[14](MOUNT_D)
# inset [7.5](MOUNT_INSET) stands very nearly tangent to both edges it sits in from.
MOUNT_LIGAMENT = MOUNT_INSET - MOUNT_D / 2.0  # [0.5](MOUNT_LIGAMENT)
# What a cylinder on the larger axis would fill that this shell does not.
CYL_EXCESS_PCT = (SHELL_Y / SHELL_X - 1.0) * 100.0
# The shell's own -Y extreme, which the box's aft face stands on. The ellipse reaches it at
# one point, x = 0, so the two bodies meet along a line rather than over a face.
SHELL_TANGENT_Y = SHELL_OFFSET_Y - SHELL_Y / 2.0   # [-52.5](SHELL_TANGENT_Y)
POWER_Y0 = -BASE_Y / 2.0                           # the plate's own -Y edge
POWER_Z1 = BASE_Z + POWER_Z                        # [60](POWER_Z1), the box's crown


def mount_pattern():
    """The four hole centers on the mounting plane — the corners of a
    [81](MOUNT_PITCH_X) x [145](MOUNT_PITCH_Y) rectangle, symmetric about the origin."""
    return [(sx * MOUNT_PITCH_X / 2.0, sy * MOUNT_PITCH_Y / 2.0)
            for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


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
        cq.Workplane("XY", origin=(0.0, POWER_Y0 + POWER_Y / 2.0, BASE_Z))
        .rect(POWER_X, POWER_Y)
        .extrude(POWER_Z)
    )
    part = part.union(shell).union(power)
    for x, y in mount_pattern():
        part = part.cut(cq.Solid.makeCylinder(
            MOUNT_D / 2.0, BASE_Z, cq.Vector(x, y, 0.0), cq.Vector(0, 0, 1)))
    return part.val()


# --- Holds ----------------------------------------------------------------
# The envelope is two stated bodies and four stated holes. Each hold reads one of those
# statements back off the solid.

def envelope_hold():
    """The six faces the machine has to clear: the plate's own Y, the SHELL's X, and the
    mounting plane to the crown."""
    bb = build().BoundingBox()
    for ax, got, want in (("x", bb.xmax - bb.xmin, SHELL_X),
                          ("y", bb.ymax - bb.ymin, BASE_Y),
                          ("z", bb.zmax - bb.zmin, OVERALL_H)):
        if abs(got - want) > 1e-6:
            raise ValueError(
                f"compressor measures {got:g} across {ax} and the bodies it is built from "
                f"give {want:g} — the envelope this module draws is no longer the envelope "
                f"it declares.")
    if abs(bb.zmin) > 1e-6:
        raise ValueError(
            f"compressor's underside stands at z = {bb.zmin:g} — Z = 0 is the mounting "
            f"plane, and the plate has come off the deck it is bolted to.")


def shell_hold():
    """The shell is an ELLIPSE, not a cylinder on its larger axis — a round one fills the
    same bounding box and [14](CYL_EXCESS_PCT)% more of it."""
    got = build().Volume()
    want = (BASE_X * BASE_Y * BASE_Z
            - 4.0 * math.pi * (MOUNT_D / 2.0) ** 2 * BASE_Z
            + math.pi * (SHELL_X / 2.0) * (SHELL_Y / 2.0) * SHELL_Z
            + POWER_X * POWER_Y * POWER_Z)
    if abs(got - want) > 1e-6 * want:
        raise ValueError(
            f"compressor fills {got:.0f} mm³ against the {want:.0f} its plate, its shell, "
            f"its box and its four holes come to — the shell has stopped being the pressed "
            f"oblong the donor is, a hole has found a body it does not pass through, or the "
            f"box has run into the shell instead of standing on its tangent.")


def power_hold():
    """Hold the box to the plate it stands on: filling the long reach end to end, inside the
    plate's own X, standing on the crown, and clear of the two mounts under its footprint."""
    if abs(POWER_Y0 + POWER_Y - SHELL_TANGENT_Y) > 1e-9:
        raise ValueError(
            f"the box runs y {POWER_Y0:g}..{POWER_Y0 + POWER_Y:g} and the plate's long reach "
            f"ends at the shell's tangent y = {SHELL_TANGENT_Y:g} — the box no longer fills "
            f"the reach the shell's own offset opened for it.")
    if POWER_X / 2.0 > BASE_X / 2.0:
        raise ValueError(
            f"the box is {POWER_X:g} across against the plate's {BASE_X:g} — it hangs off the "
            f"footprint it stands on.")
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
             "POWER_X", "POWER_Y", "POWER_Z", "POWER_Z1", "SHELL_TANGENT_Y")
    variables = {name: f"{globals()[name]:g}" for name in plain}
    variables["CYL_EXCESS_PCT"] = f"{CYL_EXCESS_PCT:.0f}"
    return variables


def selftest():
    envelope_hold()
    shell_hold()
    power_hold()
    mounts_hold()
    return [
        f"  envelope stands {SHELL_X:g} x {BASE_Y:g} x {OVERALL_H:g} off the mounting plane",
        f"  shell is the pressed oblong, {SHELL_X:g} x {SHELL_Y:g}, not a cylinder",
        f"  the box fills the long reach, y {POWER_Y0:g}..{SHELL_TANGENT_Y:g}, "
        f"crown at {POWER_Z1:g}",
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
    export_step(part, str(out))
    print(f"-> {out.name}")

    variables = _docvars()
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "BASE_X": 2, "BASE_Y": 1, "BASE_Z": 2,
            "SHELL_X": 2, "SHELL_Z": 1, "SHELL_OFFSET_Y": 1,
            "MOUNT_D": 1, "MOUNT_INSET": 1,
            "OVERALL_H": 2, "MOUNT_PITCH_X": 3, "MOUNT_PITCH_Y": 3,
            "SHELL_OVERHANG_X": 2,
            "PLATE_REACH_LONG": 2, "PLATE_REACH_SHORT": 2,
            "MOUNT_LIGAMENT": 1, "CYL_EXCESS_PCT": 1,
            "POWER_X": 1, "POWER_Y": 1, "POWER_Z": 1, "POWER_Z1": 1,
            "SHELL_TANGENT_Y": 2,
        },
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={
            "BASE_X": 2, "BASE_Y": 2, "BASE_Z": 2,
            "SHELL_X": 4, "SHELL_Y": 2, "SHELL_Z": 1, "SHELL_OFFSET_Y": 1,
            "MOUNT_D": 1, "MOUNT_INSET": 1,
            "OVERALL_H": 1, "MOUNT_PITCH_X": 1, "MOUNT_PITCH_Y": 1,
            "SHELL_OVERHANG_X": 1,
            "PLATE_REACH_LONG": 1, "PLATE_REACH_SHORT": 1,
            "MOUNT_LIGAMENT": 1, "CYL_EXCESS_PCT": 1,
            "POWER_X": 1, "POWER_Y": 2, "POWER_Z": 1, "POWER_Z1": 1,
            "SHELL_TANGENT_Y": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("compressor selftest OK")
    else:
        main()
