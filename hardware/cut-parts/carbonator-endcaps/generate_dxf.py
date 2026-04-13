"""
Carbonator end cap DXFs for SendCutSend.

Generates two disc variants:
  1. Top cap — 4 holes for 1/4" NPT weld bungs
     (CO2 in, water in, carbonated water out via dip tube, PRV)
  2. Bottom cap — blank, no holes

Material: 304 stainless steel, 0.250" (1/4") thick
Disc diameter: 4.860" (fits inside 5.000" OD x 0.065" wall tube, ID = 4.870")
Hole diameter: 0.710" (for weld bung body OD 0.700" + 0.010" clearance)

Units: inches.
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Weld bung: 1/4" NPT female, 304 SS, stepped body OD 0.700", flange OD 1.000"
The body drops through the hole; the flange sits on the disc surface and
is fillet-welded with the laser welder.

Top cap port layout (90° spacing on 1.0" bolt circle radius):
  - Position 1 (0°):   CO2 inlet (headspace)
  - Position 2 (90°):  Water inlet (atomization nozzle threads in from inside)
  - Position 3 (180°): Carbonated water outlet (dip tube to near bottom)
  - Position 4 (270°): PRV (pressure relief valve)

Assembly order:
  1. Fillet-weld all 4 bungs to the top disc (flange side up / outward)
  2. Install atomization nozzle from outside (threads through to inside)
  3. Install dip tube compression fitting + tube through the bung bore
  4. Weld top cap into tube
  5. Weld bottom cap into tube
  6. Install CO2 fitting and PRV from outside
  7. Passivate, hydro test
"""

import math
from pathlib import Path

import ezdxf

# ── Dimensions (inches) ──

DISC_DIA = 4.860       # disc outer diameter
DISC_R = DISC_DIA / 2  # 2.430"

HOLE_DIA = 0.710       # weld bung body OD 0.700" + 0.010" clearance
HOLE_R = HOLE_DIA / 2  # 0.355"

BOLT_CIRCLE_R = 1.000
PORT_ANGLES_DEG = [0, 90, 180, 270]

OUT_DIR = Path(__file__).resolve().parent


def make_disc(name: str, holes: list[tuple[float, float]]) -> None:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    msp.add_circle((0, 0), DISC_R)

    for cx, cy in holes:
        msp.add_circle((cx, cy), HOLE_R)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(holes)} hole(s))")


# ── Top cap: 4 holes at 90° on bolt circle ──

top_holes = []
for deg in PORT_ANGLES_DEG:
    rad = math.radians(deg)
    top_holes.append((BOLT_CIRCLE_R * math.cos(rad),
                       BOLT_CIRCLE_R * math.sin(rad)))

make_disc("endcap-top", top_holes)

# ── Bottom cap: blank ──

make_disc("endcap-bottom-blank", [])

print(f"\nDisc diameter: {DISC_DIA}\"")
print(f"Hole diameter: {HOLE_DIA}\" (for weld bung body)")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")
print(f"Fits tube: 5.000\" OD x 0.065\" wall (ID = 4.870\")")
