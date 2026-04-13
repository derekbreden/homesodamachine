"""
Carbonator end cap DXFs for SendCutSend.

Generates two disc variants:
  1. Top cap — 4 tapped 1/4" NPT holes
     (CO2 in, water in, carbonated water out via dip tube, PRV)
  2. Bottom cap — blank, no holes

Material: 304 stainless steel, 0.250" (1/4") thick
Disc diameter: 4.860" (fits inside 5.000" OD x 0.065" wall tube, ID = 4.870")

Holes are 0.4375" (7/16") pilot for 1/4" NPT tapping by SendCutSend.
SendCutSend taps after cutting — select "1/4 NPT" tapping on each hole
when configuring the order. They handle the tap drill sizing; the DXF
provides the pilot hole at the standard 7/16" tap drill diameter.

Units: inches.
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Top cap port layout (90° spacing on 1.0" bolt circle radius):
  - Position 1 (0°):   CO2 inlet (headspace)
  - Position 2 (90°):  Water inlet (atomization nozzle threads in from inside)
  - Position 3 (180°): Carbonated water outlet (dip tube to near bottom)
  - Position 4 (270°): PRV (pressure relief valve)

Assembly note: the atomization nozzle and dip tube compression fitting
must be installed BEFORE welding the top cap into the tube, since they
need inside access. CO2 fitting and PRV install after welding.
"""

import math
from pathlib import Path

import ezdxf

# ── Dimensions (inches) ──

DISC_DIA = 4.860       # disc outer diameter
DISC_R = DISC_DIA / 2  # 2.430"

TAP_DRILL_DIA = 0.4375  # 7/16" pilot for 1/4" NPT tap
TAP_DRILL_R = TAP_DRILL_DIA / 2

BOLT_CIRCLE_R = 1.000
PORT_ANGLES_DEG = [0, 90, 180, 270]

OUT_DIR = Path(__file__).resolve().parent


def make_disc(name: str, holes: list[tuple[float, float]]) -> None:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), DISC_R)

    for cx, cy in holes:
        msp.add_circle((cx, cy), TAP_DRILL_R)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(holes)} hole(s))")


# ── Top cap: 4 holes at 90° on bolt circle ──

top_holes = []
for deg in PORT_ANGLES_DEG:
    rad = math.radians(deg)
    top_holes.append((BOLT_CIRCLE_R * math.cos(rad),
                       BOLT_CIRCLE_R * math.sin(rad)))

make_disc("endcap-top-4hole", top_holes)

# ── Bottom cap: blank ──

make_disc("endcap-bottom-blank", [])

print(f"\nDisc diameter: {DISC_DIA}\"")
print(f"Tap drill diameter: {TAP_DRILL_DIA}\" (7/16\", pilot for 1/4\" NPT)")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")
print(f"Fits tube: 5.000\" OD x 0.065\" wall (ID = 4.870\")")
