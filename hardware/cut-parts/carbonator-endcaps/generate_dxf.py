"""
Carbonator end cap DXFs for SendCutSend.

Generates two disc variants:
  1. Top cap — 4 holes for 1/4" NPT weld bungs
     (CO2 in, water in, carbonated water out via dip tube, PRV)
  2. Bottom cap — blank, no holes

Material: 304 stainless steel, 0.250" (1/4") thick
Disc diameter: 4.860" (fits inside 5.000" OD x 0.065" wall tube, ID = 4.870")
Hole diameter: 0.710" (for weld bung body OD 0.700" + 0.010" clearance)

Units: inches (SendCutSend accepts inches or mm; we use inches throughout).
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Weld bung: 1/4" NPT female, 304 SS, stepped body OD 0.700", flange OD 1.000"
The body drops through the hole; the flange sits on the disc surface and is fillet-welded.

Top cap port layout (90° spacing on 1.0" bolt circle radius):
  - Position 1 (0°):   CO2 inlet (headspace)
  - Position 2 (90°):  Water inlet (atomization nozzle threads in from inside)
  - Position 3 (180°): Carbonated water outlet (dip tube to near bottom)
  - Position 4 (270°): PRV (pressure relief valve)

Clearance check at 90° spacing on 1.0" bolt circle:
  - Center-to-center between adjacent holes: 2 * 1.0 * sin(45°) = 1.414"
  - Minus two flange radii (0.5" + 0.5"): 0.414" gap between flanges — clears
  - Flange edge to disc edge: 2.430" - 1.0" - 0.5" = 0.930" — clears
"""

import math
from pathlib import Path

import ezdxf

# ── Dimensions (inches) ──

DISC_DIA = 4.860       # disc outer diameter
DISC_R = DISC_DIA / 2  # 2.430"

HOLE_DIA = 0.710       # weld bung through-hole
HOLE_R = HOLE_DIA / 2  # 0.355"

BOLT_CIRCLE_R = 1.000  # radial distance from disc center to hole centers
PORT_ANGLES_DEG = [0, 90, 180, 270]  # top cap hole positions

OUT_DIR = Path(__file__).resolve().parent


def make_disc(name: str, holes: list[tuple[float, float]]) -> None:
    """Create a DXF with the disc outline and optional holes.

    Args:
        name: filename stem (without .dxf)
        holes: list of (x, y) hole center positions
    """
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    # Outer profile
    msp.add_circle((0, 0), DISC_R)

    # Holes
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

make_disc("endcap-top-4hole", top_holes)

# ── Bottom cap: blank ──

make_disc("endcap-bottom-blank", [])

print(f"\nDisc diameter: {DISC_DIA}\"")
print(f"Hole diameter: {HOLE_DIA}\"")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")
print(f"Fits tube: 5.000\" OD x 0.065\" wall (ID = 4.870\")")
