"""DERPIPE 5/16" push-to-connect × 1/4" NPT male straight fitting — the
appliance's `co2-inlet` on the front panel. The NPT stub threads through the
front-wall hole and carries the CO2 chain inboard (→ GASHER → WR1110); the PTC
collet stands proud outboard where the customer's 5/16" CO2 tube pushes in.

External envelope only — a PTC collet body, a 9/16" wrench hex, and a
plain-cylinder NPT shank. AirTAC NPC5/16-1/4 class reference: 1.06" overall,
1/4" NPT.

Frame: +Y = flow axis (matches the enclosure placement); the PTC collet is at
the -Y end (outboard), the NPT shank at +Y (inboard, through the wall).
Centered on X/Z, +Z up.

Run:
    tools/cad-venv/bin/python hardware/reference/derpipe-co2-inlet/derpipe_co2_inlet.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

STEP = _here.parent / "derpipe-co2-inlet.step"

COLLET_D = 16.0             # 5/16" PTC collet body OD
COLLET_LENGTH = 12.0        # push-in cartridge + release collar
HEX_ACROSS_CORNERS = 16.5   # 9/16" hex (14.29 across flats)
HEX_LENGTH = 5.0            # wrench flat thickness
SHANK_D = 13.7             # 1/4" NPT major Ø (simplified, no helix)
SHANK_LENGTH = 10.0        # NPT engagement, through the wall inboard
BODY_LENGTH = COLLET_LENGTH + HEX_LENGTH + SHANK_LENGTH   # collet face to stub tip
PROUD_LENGTH = COLLET_LENGTH + HEX_LENGTH   # what has to stand OUTSIDE a wall: the push-in
                                            # cartridge and the flats a wrench takes


def collet():
    """The 5/16" push-in mouth, outboard: `(position, outward axis)`. It is the frame's own
    origin — the tube goes in here."""
    return ((0.0, 0.0, 0.0), (0.0, -1.0, 0.0))


def stub_tip():
    """The far end of the NPT shank, inboard: `(position, outward axis)`. This is the shoulder
    a female socket makes up against, so whatever threads onto this fitting stands here."""
    return ((0.0, BODY_LENGTH, 0.0), (0.0, 1.0, 0.0))


def stations() -> dict:
    """Both ends, under the sides of the wall they stand on."""
    return {"collet": collet(), "stub-tip": stub_tip()}


def stations_hold():
    """Hold both ends to `derpipe-co2-inlet.step` — the file the enclosure seats, while it
    takes these stations out of this module's live figures.

    The fitting is a straight run on one axis, so its two stations ARE the ends of that
    solid's box, and whatever is made up onto the stub tip stands on this reading."""
    bb = cq.importers.importStep(str(STEP)).val().BoundingBox()
    for name, (pos, _axis), actual in (("collet", collet(), bb.ymin),
                                       ("stub-tip", stub_tip(), bb.ymax)):
        if abs(pos[1] - actual) > 1e-6:
            raise ValueError(
                f"derpipe {name} stands at y = {pos[1]:g} and {STEP.name} ends at "
                f"{actual:.4f} — {abs(pos[1] - actual):.4f} mm apart. The pack seats that file "
                f"and reads this station, so anything made up on it closes on nothing.")


def build():
    """PTC collet (-Y, outboard) → hex → NPT shank (+Y, inboard). Built along
    +Z low-to-high = outboard-to-inboard, then reoriented +Z -> +Y."""
    collet = cq.Workplane("XY").circle(COLLET_D / 2.0).extrude(COLLET_LENGTH)
    hex_sec = (
        cq.Workplane("XY")
        .workplane(offset=COLLET_LENGTH)
        .polygon(6, HEX_ACROSS_CORNERS)
        .extrude(HEX_LENGTH)
    )
    shank = (
        cq.Workplane("XY")
        .workplane(offset=COLLET_LENGTH + HEX_LENGTH)
        .circle(SHANK_D / 2.0)
        .extrude(SHANK_LENGTH)
    )
    part = collet.union(hex_sec).union(shank)
    return part.rotate((0, 0, 0), (1, 0, 0), -90.0)


def main():
    part = build()
    bb = part.val().BoundingBox()
    total = COLLET_LENGTH + HEX_LENGTH + SHANK_LENGTH
    print("DERPIPE 5/16\" PTC × 1/4\" NPT CO2 inlet")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Collet Ø{COLLET_D} × {COLLET_LENGTH:g}; hex {HEX_ACROSS_CORNERS} corners × "
          f"{HEX_LENGTH:g}; NPT Ø{SHANK_D} × {SHANK_LENGTH:g}; total {total:g} mm")
    out = _here.parent / "derpipe-co2-inlet.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
