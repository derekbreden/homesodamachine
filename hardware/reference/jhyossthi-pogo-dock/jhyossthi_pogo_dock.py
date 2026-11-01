"""JHYOSSTHI 2-pin magnetic pogo connector — the mated pair the ASSE drip pan DOCKS on
(bom.md §3, B0CSX6ZQ1H). The FEMALE half, two flush gold pads between two magnets, is
potted in the pan's east wall and rides the pan; the MALE half, two spring pins between two
magnets, stands in the sleeve's backstop facing it. The pan's own travel mates the two and
the magnets hold the pan home, so the probe's leads never leave the pan.

External envelope only, read off the listing's drawing. Either half is one PILL: a
14.5 x 4.0 flange 3.0 deep, a 12.5 x 4.0 nose 1.0 proud of it on the mating face, and two
Ø0.7 solder tails 1.5 long off the back on the pins' own 2.5 pitch. The magnets lie flush in
the nose face on an 8.0 pitch and are that face's own metal, not drawn apart from it. The
male's pins stand 1.0 above the nose at the listing's working position.

Frame: the NOSE FACE is the XY plane at Z = 0, facing +Z, and the body hangs -Z. The pill's
long axis is X, the two pins on ±X. Origin at the nose face's centre.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATHS = {half: _here.parent / f"pogo-dock-{half}.step" for half in ("female", "male")}
PAYLOAD_PATHS = {half: step.with_name(step.name + ".mesh") for half, step in STEP_PATHS.items()}
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

# The flange — the pill's whole length and width, and its depth behind the nose.
BODY_L, BODY_W, BODY_T = 14.5, 4.0, 3.0
# The nose proud of the flange on the mating face; the step between them is the SHOULDER a
# pocket's window leaves, and the face the magnets pull the pill against.
NOSE_L, NOSE_T = 12.5, 1.0
# The two solder tails off the back, on the pins' pitch.
TAIL_D, TAIL_L = 0.7, 1.5
PIN_PITCH = 2.5
# The male's pin, and the female's pad it lands on.
PIN_D = 0.9
# The pin tip above the nose face at the listing's working position.
PIN_WORKING = 1.0
MAGNET_PITCH = 8.0


def depth():
    """Nose face to the flange's back."""
    return NOSE_T + BODY_T


def reach_back():
    """Nose face to the tails' tips — what a pocket is deep, leads not counted."""
    return depth() + TAIL_L


def nose_face():
    """The mating face's centre and its outward axis, in this frame — the station either half
    is seated on."""
    return ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0))


def main():
    for half, step in STEP_PATHS.items():
        print(f"Pogo dock {half}")
        print(f"  STEP: {step}")
        print(f"  Display payload: {PAYLOAD_PATHS[half]}")


if __name__ == "__main__":
    main()
