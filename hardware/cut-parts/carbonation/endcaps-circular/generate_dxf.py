"""
Carbonator end-cap DXFs for SendCutSend — circular vessel, 2 ports per cap.

Two identical discs per vessel.  Each disc has 2x tap-drill holes for
1/4"-18 NPT.  Tapping is done post-laser (SendCutSend does not offer
NPT tapping — user taps by hand, or sends the cut discs to a shop that
taps NPT).  2 ports/cap * 2 caps = 4 ports/vessel — same port count as
the original 4-hole-top design, just split across both end caps.

── Why 2 ports per cap (instead of 4-on-top + 0-on-bottom) ──

The earlier revision concentrated all 4 NPT ports on the top disc and
left the bottom disc blank.  With the vessel mounted vertically and both
end caps reachable, splitting the ports 2+2 lets plumbing approach from
both ends of the vessel — shorter runs, less crowding on one face, and
the two caps become identical parts (qty N from SendCutSend = N/2
vessels, and there's no "top vs. bottom" orientation error possible).

── Dimensions ──

  Disc diameter:       4.860"    (= tube ID 4.870" − 0.010" slip-fit)
  Disc thickness:      0.250"    (1/4" 316 SS, SendCutSend laser-cut)
  Hole diameter:       0.438"    (7/16" — tap drill for 1/4"-18 NPT)
  Hole spacing:        1.500"    (center-to-center along one axis)
  Hole positions:      (-0.750, 0) and (+0.750, 0)

The 1.500" center-to-center spacing matches the CNC dome-cap variants
preserved at the archive-plan-b git tag so the plumbing layout is
identical regardless of which cap style is used.

── Tapping notes ──

1/4"-18 NPT has a full-thread taper of ~0.390".  Tapping a 0.250"-thick
plate gives ~5–6 engaged threads instead of the standard 7, which still
seals reliably with thread sealant on a 100 PSI service vessel.  If
more engagement is wanted, weld on a 1/4" NPT bung over each hole
(historical plan — see git commit 08bdc4b for the 0.710" bung-hole
variant).

── Material ──

  316 stainless steel, 0.250" thick, laser-cut.

SendCutSend compensates for kerf automatically — draw nominal dims.
Units: inches.  DXF $INSUNITS = 1 (inches).
"""

import sys
from pathlib import Path

import ezdxf

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_py_comments

# Dimensions in inches; DXF $INSUNITS = 1 (inches).

# [4.86 in](DISC_D) — tube ID 4.870" − 0.010" slip-fit.
disc_diameter = 4.860
# [2.43 in](DISC_R) — disc_diameter / 2.
disc_radius = disc_diameter / 2
# [0.25 in](DISC_THK) — 1/4" 316 SS, SendCutSend laser-cut.
disc_thickness = 0.250

# [0.438 in](HOLE_D) — 7/16" tap drill for 1/4"-18 NPT.
hole_diameter = 0.438
# [0.219 in](HOLE_R) — hole_diameter / 2.
hole_radius = hole_diameter / 2

# [1.5 in](HOLE_SPACING) center-to-center along one axis — matches the
# CNC dome-cap variants preserved at git tag archive-plan-b so plumbing
# layout is identical across cap styles.
hole_spacing = 1.500
hole_positions = [
    (-hole_spacing / 2, 0.0),
    (+hole_spacing / 2, 0.0),
]

out_dir = Path(__file__).resolve().parent
out_name = "endcap-circular-2hole"


def make_disc() -> Path:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), disc_radius)
    for hole_center in hole_positions:
        msp.add_circle(hole_center, hole_radius)

    path = out_dir / f"{out_name}.dxf"
    doc.saveas(str(path))
    return path


def main() -> None:
    path = make_disc()
    print(f"Exported: {path}  ({len(hole_positions)} holes)")
    print(f"  Disc diameter:   {disc_diameter}\"  (fits 5.000\" OD x 0.065\" wall tube, ID 4.870\")")
    print(f"  Disc thickness:  {disc_thickness}\"")
    print(f"  Hole diameter:   {hole_diameter}\"  (7/16\" tap drill for 1/4\"-18 NPT)")
    print(f"  Hole spacing:    {hole_spacing:g}\" center-to-center along one axis")
    print(f"  Material:        316 SS, laser-cut")
    print(f"  Per vessel:      2 identical discs, each tapped 2x 1/4\"-18 NPT")

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # dynamic-comment marker follows.
    variables = {
        "DISC_D": f"{disc_diameter:g} in",
        "DISC_R": f"{disc_radius:g} in",
        "DISC_THK": f"{disc_thickness:g} in",
        "HOLE_D": f"{hole_diameter:g} in",
        "HOLE_R": f"{hole_radius:g} in",
        "HOLE_SPACING": f"{hole_spacing:g} in",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "DISC_D": 1,
            "DISC_R": 1,
            "DISC_THK": 1,
            "HOLE_D": 1,
            "HOLE_R": 1,
            "HOLE_SPACING": 1,
        },
    )


if __name__ == "__main__":
    main()
