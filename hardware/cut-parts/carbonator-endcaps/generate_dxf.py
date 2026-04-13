"""
Carbonator end cap DXFs for SendCutSend.

Generates two disc variants:
  1. Top cap — 3 tapped 1/4" NPT holes + 1 weld bung hole
  2. Bottom cap — blank, no holes

Material: 304 stainless steel, 0.250" (1/4") thick
Disc diameter: 4.860" (fits inside 5.000" OD x 0.065" wall tube, ID = 4.870")

Three holes are 0.4375" (7/16") pilot for 1/4" NPT tapping by SendCutSend.
One hole is 0.710" for a 1/4" NPT weld bung (body OD 0.700" + 0.010"
clearance) — the dip tube port needs a smooth bore for the tube to pass
through into the vessel interior.

Units: inches.
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Top cap port layout (90° spacing on 1.0" bolt circle radius):
  - Position 1 (0°):   CO2 inlet — tapped 1/4" NPT
  - Position 2 (90°):  Water inlet (atomization nozzle) — tapped 1/4" NPT
  - Position 3 (180°): Carbonated water outlet (dip tube) — weld bung
  - Position 4 (270°): PRV (pressure relief valve) — tapped 1/4" NPT

Assembly order:
  1. Weld the bung into the dip tube port (position 3)
  2. Install atomization nozzle into tapped hole (position 2) from outside
  3. Install dip tube compression fitting + tube through the bung
  4. Weld top cap into tube
  5. Weld bottom cap into tube
  6. Install CO2 fitting and PRV from outside
  7. Passivate, hydro test
"""

import math
from pathlib import Path

import ezdxf

# ── Dimensions (inches) ──

DISC_DIA = 4.860
DISC_R = DISC_DIA / 2

TAP_DRILL_DIA = 0.4375   # 7/16" pilot for 1/4" NPT tap
TAP_DRILL_R = TAP_DRILL_DIA / 2

BUNG_HOLE_DIA = 0.710    # weld bung body OD 0.700" + 0.010" clearance
BUNG_HOLE_R = BUNG_HOLE_DIA / 2

BOLT_CIRCLE_R = 1.000

# (angle, hole_type): "tap" = 7/16" pilot, "bung" = 0.710" clearance
PORTS = [
    (0,   "tap"),    # CO2 inlet
    (90,  "tap"),    # Water inlet / atomizer
    (180, "bung"),   # Carbonated water outlet / dip tube
    (270, "tap"),    # PRV
]

OUT_DIR = Path(__file__).resolve().parent


def make_disc(name: str, holes: list[tuple[float, float, float]]) -> None:
    """Create a DXF with the disc outline and optional holes.

    Args:
        name: filename stem (without .dxf)
        holes: list of (x, y, radius) tuples
    """
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), DISC_R)

    for cx, cy, r in holes:
        msp.add_circle((cx, cy), r)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(holes)} hole(s))")


# ── Top cap ──

top_holes = []
for deg, hole_type in PORTS:
    rad = math.radians(deg)
    cx = BOLT_CIRCLE_R * math.cos(rad)
    cy = BOLT_CIRCLE_R * math.sin(rad)
    r = BUNG_HOLE_R if hole_type == "bung" else TAP_DRILL_R
    top_holes.append((cx, cy, r))

make_disc("endcap-top", top_holes)

# ── Bottom cap: blank ──

make_disc("endcap-bottom-blank", [])

print(f"\nDisc diameter: {DISC_DIA}\"")
print(f"Tap drill holes (x3): {TAP_DRILL_DIA}\" (7/16\", pilot for 1/4\" NPT)")
print(f"Bung hole (x1): {BUNG_HOLE_DIA}\" (for weld bung body)")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")
print(f"Fits tube: 5.000\" OD x 0.065\" wall (ID = 4.870\")")
