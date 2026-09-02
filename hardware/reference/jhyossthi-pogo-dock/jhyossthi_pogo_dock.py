"""JHYOSSTHI 2-pin magnetic pogo connector — the mated pair the ASSE drip pan DOCKS on
(bom.md §3, B0CSX6ZQ1H). The FEMALE half, two flush gold pads between two magnets, is
potted in the pan's east wall and rides the pan; the MALE half, two spring pins between two
magnets, stands in the sleeve's backstop facing it. The pan's own travel mates the two and
the magnets hold the pan home, so the probe's leads never leave the pan.

External envelope only, read off the listing's drawing. Either half is one PILL: a
14.5 x 4.0 flange 3.0 deep, a 12.5 x 4.0 nose 1.0 proud of it on the mating face, and two
Ø0.7 solder tails 1.5 long off the back on the pins' own 2.5 pitch. The magnets lie flush in
the nose face on an 8.0 pitch and are that face's own metal, not drawn apart from it. The
male's pins stand 1.0 above the nose at the listing's working position; a caller mating the
pair across a gap it knows asks `build_male` for that reach instead.

Frame: the NOSE FACE is the XY plane at Z = 0, facing +Z, and the body hangs -Z. The pill's
long axis is X, the two pins on ±X. Origin at the nose face's centre.

Run:
    tools/cad-venv/bin/python hardware/reference/jhyossthi-pogo-dock/jhyossthi_pogo_dock.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_assembly
from _materials import C_DOCK, one_body

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


def pill(length, width, z0, z1):
    """A stadium `length` x `width` in the XY plane, standing from `z0` to `z1`."""
    return (cq.Workplane("XY", origin=(0.0, 0.0, z0))
            .slot2D(length, width).extrude(z1 - z0))


def _half():
    body = pill(NOSE_L, BODY_W, -NOSE_T, 0.0).union(pill(BODY_L, BODY_W, -depth(), -NOSE_T))
    for sx in (-1.0, 1.0):
        tail = (cq.Workplane("XY", origin=(sx * PIN_PITCH / 2.0, 0.0, -reach_back()))
                .circle(TAIL_D / 2.0).extrude(TAIL_L))
        body = body.union(tail)
    return body


def build_female():
    """The pad half: the pill, its two pads flush in the nose face."""
    return _half()


def build_male(pin_reach=PIN_WORKING):
    """The pin half: the pill with its two pins standing `pin_reach` above the nose face, each
    a Ø`PIN_D` post under a hemispherical tip."""
    body = _half()
    r = PIN_D / 2.0
    for sx in (-1.0, 1.0):
        x = sx * PIN_PITCH / 2.0
        post_h = max(pin_reach - r, 0.0)
        if post_h > 1e-6:
            body = body.union(cq.Workplane("XY", origin=(x, 0.0, 0.0)).circle(r).extrude(post_h))
        body = body.union(cq.Workplane("XY").sphere(r).translate((x, 0.0, post_h)))
    return body


def main():
    print("JHYOSSTHI 2-pin magnetic pogo dock")
    for name, part in (("pogo-dock-female", build_female()), ("pogo-dock-male", build_male())):
        bb = part.val().BoundingBox()
        print(f"  {name}: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
              f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
        out = _here.parent / f"{name}.step"
        export_assembly(one_body(part, name, C_DOCK), str(out))
        print(f"-> {out.name}")
    print(f"  pill {BODY_L:g} x {BODY_W:g}, nose {NOSE_L:g} x {BODY_W:g} x {NOSE_T:g} proud, "
          f"{depth():g} deep to the flange's back, {reach_back():g} to the tails' tips; "
          f"pins on {PIN_PITCH:g}, magnets on {MAGNET_PITCH:g}")


if __name__ == "__main__":
    main()
