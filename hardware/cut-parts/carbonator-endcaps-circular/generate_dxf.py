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
in hardware/cut-parts/carbonator-milled-dome-cap[-min]/ so the plumbing
layout is identical regardless of which cap style is used.

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

from pathlib import Path

import ezdxf

# ── Dimensions (inches) ──

DISC_DIA = 4.860
DISC_R = DISC_DIA / 2

HOLE_DIA = 0.438          # 7/16" tap drill for 1/4"-18 NPT
HOLE_R = HOLE_DIA / 2

HOLE_POSITIONS = [
    (-0.750, 0.0),
    (+0.750, 0.0),
]

OUT_DIR = Path(__file__).resolve().parent


def make_disc(name: str) -> None:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), DISC_R)
    for cx, cy in HOLE_POSITIONS:
        msp.add_circle((cx, cy), HOLE_R)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(HOLE_POSITIONS)} holes)")


# Single disc design; both end caps of a vessel are identical.
make_disc("endcap-circular-2hole")

print(f"\nDisc diameter:   {DISC_DIA}\"  (fits 5.000\" OD x 0.065\" wall tube, ID 4.870\")")
print(f"Disc thickness:  0.250\"")
print(f"Hole diameter:   {HOLE_DIA}\"  (7/16\" tap drill for 1/4\"-18 NPT)")
print(f"Hole spacing:    1.500\" center-to-center along one axis")
print(f"Material:        316 SS, laser-cut")
print(f"Per vessel:      2 identical discs, each tapped 2x 1/4\"-18 NPT")
