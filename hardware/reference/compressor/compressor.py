"""Compressor — the refrigeration loop's cold end driver, as a donor primitive.

Hermetic reciprocating compressor harvested from the Antarctic Star HZB-12/Q donor
(NingBo Anuodan / HuaJun HD48Y11A, 110-120 V 60 Hz, ~90-120 W class) — the teardown
is `../ice-maker/README.md`. There is no vendor solid and no scan: the part was
calipered, and what the pack takes of it is its ENVELOPE and its bolt pattern, which
is what this module draws.

Coordinate frame
----------------
- Z = 0 is the MOUNTING PLANE, the plate's underside. The plate stands the shell
  up, and the shell's own carries the crown to
 .
- The PLATE is centered on the origin, so its four Ø holes stand symmetric
  about it on a x rectangle, each inset
  from both edges it sits in from. A floor that carries this pattern
  carries it about its own center.
- The SHELL is centered on X and offset on Y, so the plate reaches
  past it at -Y and at +Y.
- The POWER BOX stands in that long reach, hanging off the shell with air under it:
  across, deep — the reach exactly — and tall,
  its underside at, its aft face on the shell's own tangent plane at
  y =. **-Y is the power end.** It is narrower than the plate,
  which reaches past each of its flanks — so a body pressed on a
  flank stands over the can's own metal, and `power_face()` is the +X one.

The suction, discharge and process stubs are not modeled. All three are STATIONS instead —
`stations()` for the two that are in the loop, `process_tube()` for the one that is not —
so a line brazed into one and a valve clamped on one both answer to the can. The box
carries the compressor's terminal block and clip-on
PTC start relay under the donor's own moulded cover, so it is the one feature that tells the
two ends apart: the bolt pattern is symmetric about the origin, the box is not.

The shell is WIDER THAN ITS OWN PLATE — across against the plate's
 — so the widest thing on the part is its belly, overhanging
 each side and starting up. A floor sees
 x; a wall beside it sees, and sees it
one plate-thickness off the deck.

Run:
    tools/cad-venv/bin/python hardware/reference/compressor/compressor.py
    tools/cad-venv/bin/python hardware/reference/compressor/compressor.py selftest


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'compressor.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'compressor.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'compressor.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

# --- Calipered off the donor ----------------------------------------------

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('compressor')
globals().update({name: _reference_values[name] for name in ('BASE_X', 'BASE_Y', 'BASE_Z', 'SHELL_X', 'SHELL_Y', 'SHELL_Z', 'SHELL_OFFSET_Y', 'MOUNT_D', 'MOUNT_INSET', 'POWER_X', 'POWER_Y', 'POWER_Z', 'POWER_GAP', 'OVERALL_H', 'MOUNT_PITCH_X', 'MOUNT_PITCH_Y', 'SHELL_OVERHANG_X', 'PLATE_REACH_LONG', 'PLATE_REACH_SHORT', 'MOUNT_LIGAMENT', 'SHELL_TANGENT_Y', 'POWER_Y0', 'POWER_Z0', 'POWER_Z1', 'POWER_FLANK_REACH', 'DISCHARGE_Z', 'SUCTION_Z', 'PROCESS_Z', 'PROCESS_CLAMP', 'PROCESS_OVER_SUCTION')})






# --- What those give ------------------------------------------------------
# The plate a hole leaves between itself and the edge it is inset from.
# The shell's own -Y extreme, which the box's aft face stands on. The ellipse reaches it at
# one point, x = 0, so the two bodies meet along a line rather than over a face.
# What the plate still reaches past either FLANK of the box. The box is narrower than the
# plate it stands on, so a body laid on a flank stands over the can's own plate — where the
# -Y face has nothing past it at all, that being the plate's own edge (`power_face`).
# Where the two loop stubs leave the shell, up its standing height. Both are on a tangent
# line; only the height along it is free, and these are the heights the donor brazes at.
# THE THIRD STUB, the one that is not in the loop: the process tube, a short copper stub
# pinched and brazed shut at the factory (`../ice-maker/README.md` "Process tube"). It
# leaves the -X tangent, the same flank the suction does, standing above it — so the saddle
# and the suction leg share one lane down the machine's west side, and the valve is reached
# from beside the can rather than over it. Like the other two it is a STATION and not a solid.
# How far out along that stub the saddle bands. The stub is ~50 long and its tip stays
# pinched, so the clamp goes on the middle of it.
# What the stub stands above the suction's own, the other station on this tangent.


def mount_pattern():
    'The four hole centers on the mounting plane — the corners of a\n    x rectangle, symmetric about the origin.'
    return _reference_data('compressor', 'mount_pattern', (), {})


def power_face():
    "The +X FLANK of the POWER BOX, as `(centre, outward axis)` in this frame.\n\n    The box is the donor's own moulded cover over the terminal block and the PTC start\n    relay, and every face of it is that same moulding — so a case pressed on this one is\n    pressed on the cover as surely as on the box's front.\n\n    WHAT THIS FLANK HAS THAT THE FRONT DOES NOT is that nothing standing proud of it costs\n    the machine any DEPTH. The box's -Y face is the deepest plane on the whole donor —\n    `POWER_Y0` is the plate's own edge — so a body laid there is the frontmost thing in the\n    cabinet and the appliance's front wall stands off IT. Laid on the flank instead, the same\n    body stands over the plate's own mm of reach at +X, in air the\n    can already owns, and the front plane answers to the box.\n\n    The gap the clamp's leaves press runs the box's whole footprint, so it is reached from\n    this face as readily as from the front — and the shell is not a fence here at all, since\n    the box's aft plane IS the shell's own tangent and this face's whole width stands forward\n    of it."
    return _reference_data('compressor', 'power_face', (), {})


def process_tube():
    "Where the piercing valve bands the PROCESS TUBE, as `(the point on the stub's own\n    axis, the stub's outward direction)` in this frame.\n\n    The stub leaves the -X tangent, `PROCESS_Z` up — the same flank the suction leaves by,\n    above it, so the saddle bands the copper in the lane that leg\n    already runs in and both are reached from the machine's west side.\n\n    The point is on the STUB: `PROCESS_CLAMP` out along the tube, where the clamp grips."
    return _reference_data('compressor', 'process_tube', (), {})


def stations():
    "The two ends of the sealed loop this body carries, in its own frame.\n\n    An ELLIPSE HAS NO FLAT FACE. This shell touches a neighbour's plane along ONE LINE — the\n    tangent at its own extreme — so both picks stand on a tangent and nowhere else, where a\n    box would let a station stand anywhere on a wall. Both stand at `SHELL_OFFSET_Y`, because\n    that is where the two X extremes fall: discharge on the +X tangent, suction on the -X one,\n    the two of them on opposite flanks of the same can. A neighbour mated to this body meets it\n    there, which is what the two of them read as one point."
    return _reference_data('compressor', 'stations', (), {})


def stations_hold():
    "Hold both picks inside the shell's standing height."
    return _reference_data('compressor', 'stations_hold', (), {})


def build():
    """The three bodies as the pack carries them: the plate on the mounting plane with its
    four holes through it, the oblong shell standing on the plate's crown offset on Y, and
    the power box filling the plate's long reach at -Y."""
    import cadquery as cq
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
    "Hold the box to the reach it fills: end to end on Y, standing clear of the plate with\n    air under it, and off the mounts below its footprint.\n\n    It hangs on the SHELL, not on the plate — `POWER_GAP` of air under it — so a driver still\n    reaches the plate beneath, and its aft face closes on the shell's own tangent."
    return _reference_data('compressor', 'power_hold', (), {})


def mounts_hold():
    'All four holes stand inside the plate they are cut in, and clear of the shell — a\n    hole the belly covers is a hole no bolt reaches.'
    return _reference_data('compressor', 'mounts_hold', (), {})


# --- controls -------------------------------------------------------------

def _docvars():
    "Every figure this part's prose quotes, from the constant that owns it."
    return _reference_data('compressor', '_docvars', (), {})


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
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        for line in selftest():
            print(line)
        print("compressor selftest OK")
    else:
        main()


def __getattr__(name):
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'C_COMP', 'one_body'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
