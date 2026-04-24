"""
Carbonator body half-sheet DXF for SendCutSend.

Generates one file: a rectangular half-blank.  Two of these are rolled
into D-halves on a slip roll, then butt-welded together along both
flat sides to form the racetrack tube body.

── Why two halves instead of one ──

A slip roll can only produce open shells.  Once a rolled sheet wraps
far enough that it approaches a closed loop, it cannot slide off the
rollers axially — the captive end supports block it.  Splitting the
racetrack into two symmetric D-halves gives two open 180° shells,
each with a short flat tangent on either end, that roll and release
cleanly.

Two butt welds (one on each flat side) instead of one.  Material
total and rolled geometry are unchanged.

── Dimension chain ──

End caps define the tube ID.  Working backward:

  End cap semicircle R:  1.930"  (from endcap DXF generator)
  Slip-fit clearance:    0.005"  per side
  Body ID semicircle R:  1.930 + 0.005 = 1.935"
  Body ID flat length:   1.600"

  Sheet thickness:       0.048"  (SendCutSend 304 SS stock)

  Body OD semicircle R:  1.935 + 0.048 = 1.983"
  Body OD flat length:   1.600"
  External overall:      5.566" x 3.966"

── Half-blank length (neutral axis) ──

During bending, the neutral axis sits at the midplane of the sheet
(R/t ≈ 40, well into the regime where neutral axis ≈ 0.5t).

  Neutral axis R:  1.935 + 0.024 = 1.959"

  Each half:  one semicircle + two half-flats
    Semicircle arc at neutral axis:  pi * 1.959 = 6.154"
    Two half-flats (0.800" each):    2 * 0.800  = 1.600"
    Half-blank length:                            7.754"

  Half-blank height (tube length):  6.000"

Full racetrack perimeter:  2 * 7.754" = 15.509"  (unchanged from
the single-seam plan).  Order quantity 2 from SendCutSend.

── Rolling sequence (per half) ──

Each 7.754" x 6.000" half has three zones along its length:
  1. Flat tangent:  0.000" to 0.800"   (stays flat — butts to neighbor half)
  2. Semicircle:    0.800" to 6.954"   (roll to R=1.959" at neutral axis)
  3. Flat tangent:  6.954" to 7.754"   (stays flat — butts to neighbor half)

The 0.800" flat tangents also absorb the leading/trailing flat
that slip rolls inherently leave due to roller geometry (the sheet
can't fully curve until past the top roller pinch point).

Roll each half, then butt-weld the two halves together along both
flat sides.  The seams are straight-line, easy access, and land on
the flats where there's no residual bend stress.

── Hoop stress check ──

  sigma = P * OD / (2 * t)
        = 70 * 5.566 / (2 * 0.048)
        = 4,058 PSI

  Allowable (304 SS):  20,000 PSI
  Safety factor:       4.9x

Two weld seams don't change this — hoop stress runs through the
welds as continuous membrane.  Full-penetration butt welds on
passivated 304 SS are stronger than the parent material.

── Material ──

304 stainless steel, 0.048" thick.
Units: inches.
SendCutSend compensates for kerf automatically — draw nominal dimensions.
"""

import math
from pathlib import Path

import ezdxf

# ── End cap interface (from endcap DXF generator) ──

CAP_SEMICIRCLE_R = 1.930      # end cap slip-fit semicircle radius
CLEARANCE = 0.005             # per side

# ── Body dimensions ──

SHEET_T = 0.048               # sheet thickness (SendCutSend 304 SS stock)

BODY_ID_SEMI_R = CAP_SEMICIRCLE_R + CLEARANCE   # 1.935"
BODY_ID_FLAT = 1.600                              # flat length (same as end cap)

BODY_OD_SEMI_R = BODY_ID_SEMI_R + SHEET_T        # 1.983"
BODY_OD_FLAT = BODY_ID_FLAT                       # 1.600"

# ── Neutral axis (for blank length calculation) ──

NEUTRAL_AXIS_R = BODY_ID_SEMI_R + SHEET_T / 2    # 1.959"

# ── Half-blank dimensions ──

SEMICIRCLE_ARC_LEN = math.pi * NEUTRAL_AXIS_R     # one semicircle at neutral axis
HALF_FLAT = BODY_ID_FLAT / 2                      # 0.800"
HALF_BLANK_LENGTH = SEMICIRCLE_ARC_LEN + 2 * HALF_FLAT  # 7.754"
BLANK_HEIGHT = 6.000                               # tube length

OUT_DIR = Path(__file__).resolve().parent


def generate_half_blank() -> None:
    """Generate a rectangular half-blank DXF.  Order quantity 2."""
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    # Rectangle centered at origin
    hw = HALF_BLANK_LENGTH / 2
    hh = BLANK_HEIGHT / 2

    msp.add_line((-hw, -hh), (hw, -hh))
    msp.add_line((hw, -hh), (hw, hh))
    msp.add_line((hw, hh), (-hw, hh))
    msp.add_line((-hw, hh), (-hw, -hh))

    path = OUT_DIR / "carbonator-body-half-blank.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}")


generate_half_blank()

# ── Summary ──

print(f"\n--- Half-blank (order quantity 2) ---")
print(f"Half-blank: {HALF_BLANK_LENGTH:.3f}\" x {BLANK_HEIGHT:.3f}\"")
print(f"Material: 304 SS, {SHEET_T}\" thick")

print(f"\n--- Dimension chain ---")
print(f"End cap semicircle R:    {CAP_SEMICIRCLE_R:.3f}\"")
print(f"Slip-fit clearance:      {CLEARANCE:.3f}\"/side")
print(f"Body ID semicircle R:    {BODY_ID_SEMI_R:.3f}\"")
print(f"Body ID flat length:     {BODY_ID_FLAT:.3f}\"")
print(f"Sheet thickness:         {SHEET_T:.3f}\"")
print(f"Body OD semicircle R:    {BODY_OD_SEMI_R:.3f}\"")
print(f"Neutral axis R:          {NEUTRAL_AXIS_R:.3f}\"")

print(f"\n--- Half-blank length breakdown ---")
print(f"Semicircle arc:          {SEMICIRCLE_ARC_LEN:.3f}\"")
print(f"Half-flats (x2):         {2 * HALF_FLAT:.3f}\"")
print(f"Per half:                {HALF_BLANK_LENGTH:.3f}\"")
print(f"Full perimeter (x2):     {2 * HALF_BLANK_LENGTH:.3f}\"")

print(f"\n--- Rolling zones (per half, along length) ---")
z1_end = HALF_FLAT
z2_end = z1_end + SEMICIRCLE_ARC_LEN
z3_end = z2_end + HALF_FLAT
print(f"Flat tangent: 0.000\" to {z1_end:.3f}\"")
print(f"Semicircle:   {z1_end:.3f}\" to {z2_end:.3f}\"")
print(f"Flat tangent: {z2_end:.3f}\" to {z3_end:.3f}\"")

print(f"\n--- Hoop stress ---")
sigma = 70 * (2 * BODY_OD_SEMI_R + BODY_OD_FLAT) / (2 * SHEET_T)
print(f"sigma = {sigma:.0f} PSI  (allowable 20,000 PSI, SF = {20000/sigma:.1f}x)")

print(f"\n--- External racetrack (after rolling + welding both seams) ---")
print(f"OD overall: {2 * BODY_OD_SEMI_R + BODY_OD_FLAT:.3f}\" x {2 * BODY_OD_SEMI_R:.3f}\"")
print(f"Circumference at OD: {2 * math.pi * BODY_OD_SEMI_R + 2 * BODY_OD_FLAT:.3f}\"")
