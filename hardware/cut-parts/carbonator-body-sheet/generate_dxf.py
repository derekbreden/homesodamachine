"""
Carbonator body sheet DXF for SendCutSend.

Generates one file: a rectangular blank that gets rolled on a slip roll
into the racetrack tube body.  One longitudinal butt weld closes it.

── Dimension chain ──

The end caps define the tube ID.  Working backward:

  End cap semicircle R:  1.930"  (from endcap DXF generator)
  Slip-fit clearance:    0.005"  per side
  Body ID semicircle R:  1.930 + 0.005 = 1.935"
  Body ID flat length:   1.600"

  Sheet thickness:       0.048"  (SendCutSend 304 SS stock)

  Body OD semicircle R:  1.935 + 0.048 = 1.983"
  Body OD flat length:   1.600"
  External overall:      5.566" x 3.966"

── Blank length (neutral axis) ──

During bending, the neutral axis sits at the midplane of the sheet
(R/t ≈ 40, well into the regime where neutral axis ≈ 0.5t).

  Neutral axis R:  1.935 + 0.024 = 1.959"

  Two semicircles at neutral axis:  2 * pi * 1.959 = 12.310"
  Two flat sections:                2 * 1.600       =  3.200"
  Total blank length:                                 15.510"

  Blank height (tube length):  6.000"

The blank is a 15.510" x 6.000" rectangle.

── Rolling sequence ──

The sheet has four zones along its length:
  1. Flat section 1:  0.000" to 1.600"   (stays flat)
  2. Semicircle 1:    1.600" to 7.755"   (roll to R=1.959" at neutral axis)
  3. Flat section 2:  7.755" to 9.355"   (stays flat)
  4. Semicircle 2:    9.355" to 15.510"  (roll to R=1.959" at neutral axis)

The seam (butt weld) falls at the junction of flat 1 and semicircle 2,
i.e. one of the flat sides.  Straight-line weld, easy access.

── Hoop stress check ──

  sigma = P * OD / (2 * t)
        = 70 * 5.566 / (2 * 0.048)
        = 4,058 PSI

  Allowable (304 SS):  20,000 PSI
  Safety factor:       4.9x

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

# ── Blank dimensions ──

SEMICIRCLE_ARC_LEN = math.pi * NEUTRAL_AXIS_R    # one semicircle at neutral axis
BLANK_LENGTH = 2 * SEMICIRCLE_ARC_LEN + 2 * BODY_ID_FLAT  # 15.510"
BLANK_HEIGHT = 6.000                               # tube length

OUT_DIR = Path(__file__).resolve().parent


def generate_blank() -> None:
    """Generate a rectangular blank DXF."""
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    # Rectangle centered at origin
    hw = BLANK_LENGTH / 2
    hh = BLANK_HEIGHT / 2

    msp.add_line((-hw, -hh), (hw, -hh))
    msp.add_line((hw, -hh), (hw, hh))
    msp.add_line((hw, hh), (-hw, hh))
    msp.add_line((-hw, hh), (-hw, -hh))

    path = OUT_DIR / "carbonator-body-blank.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}")


generate_blank()

# ── Summary ──

print(f"\n--- Body blank ---")
print(f"Blank: {BLANK_LENGTH:.3f}\" x {BLANK_HEIGHT:.3f}\"")
print(f"Material: 304 SS, {SHEET_T}\" thick")

print(f"\n--- Dimension chain ---")
print(f"End cap semicircle R:    {CAP_SEMICIRCLE_R:.3f}\"")
print(f"Slip-fit clearance:      {CLEARANCE:.3f}\"/side")
print(f"Body ID semicircle R:    {BODY_ID_SEMI_R:.3f}\"")
print(f"Body ID flat length:     {BODY_ID_FLAT:.3f}\"")
print(f"Sheet thickness:         {SHEET_T:.3f}\"")
print(f"Body OD semicircle R:    {BODY_OD_SEMI_R:.3f}\"")
print(f"Neutral axis R:          {NEUTRAL_AXIS_R:.3f}\"")

print(f"\n--- Blank length breakdown ---")
print(f"Semicircle arc (x2):     {2 * SEMICIRCLE_ARC_LEN:.3f}\"")
print(f"Flat sections (x2):      {2 * BODY_ID_FLAT:.3f}\"")
print(f"Total:                   {BLANK_LENGTH:.3f}\"")

print(f"\n--- Rolling zones (along blank length) ---")
z1_end = BODY_ID_FLAT
z2_end = z1_end + SEMICIRCLE_ARC_LEN
z3_end = z2_end + BODY_ID_FLAT
z4_end = z3_end + SEMICIRCLE_ARC_LEN
print(f"Flat 1:       0.000\" to {z1_end:.3f}\"")
print(f"Semicircle 1: {z1_end:.3f}\" to {z2_end:.3f}\"")
print(f"Flat 2:       {z2_end:.3f}\" to {z3_end:.3f}\"")
print(f"Semicircle 2: {z3_end:.3f}\" to {z4_end:.3f}\"")

print(f"\n--- Hoop stress ---")
sigma = 70 * (2 * BODY_OD_SEMI_R + BODY_OD_FLAT) / (2 * SHEET_T)
print(f"sigma = {sigma:.0f} PSI  (allowable 20,000 PSI, SF = {20000/sigma:.1f}x)")

print(f"\n--- External racetrack (after rolling) ---")
print(f"OD overall: {2 * BODY_OD_SEMI_R + BODY_OD_FLAT:.3f}\" x {2 * BODY_OD_SEMI_R:.3f}\"")
print(f"Circumference at OD: {2 * math.pi * BODY_OD_SEMI_R + 2 * BODY_OD_FLAT:.3f}\"")
