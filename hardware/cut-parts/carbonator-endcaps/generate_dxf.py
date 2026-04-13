"""
Carbonator end cap DXFs for SendCutSend.

Generates three disc variants:
  1. Top cap — 3 holes for 1/4" NPT weld bungs (CO2 in, water in, PRV)
  2. Bottom cap — 1 centered hole for 1/4" NPT weld bung (carbonated water out)
  3. Blank — no holes (spare / weld practice)

Material: 304 stainless steel, 0.250" (1/4") thick
Disc diameter: 4.860" (fits inside 5.000" OD x 0.065" wall tube, ID = 4.870")
Hole diameter: 0.710" (for weld bung body OD 0.700" + 0.010" clearance)

Units: inches (SendCutSend accepts inches or mm; we use inches throughout).
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Weld bung: 1/4" NPT female, 304 SS, stepped body OD 0.700", flange OD 1.000"
The body drops through the hole; the flange sits on the disc surface and is fillet-welded.

Top cap port layout (120° spacing on 1.0" bolt circle radius):
  - Position 1 (0°):   CO2 inlet
  - Position 2 (120°): Water inlet (atomization nozzle threads in from inside)
  - Position 3 (240°): PRV (pressure relief valve)

The 1.0" bolt circle keeps all flanges (1.0" OD) clear of each other
(center-to-center = 1.732", minus 1.0" = 0.732" gap) and clear of the disc
edge (disc radius 2.430" - bolt radius 1.0" - flange radius 0.5" = 0.930").
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
PORT_ANGLES_DEG = [0, 120, 240]  # top cap hole positions

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


# ── Top cap: 3 holes at 120° on bolt circle ──

top_holes = []
for deg in PORT_ANGLES_DEG:
    rad = math.radians(deg)
    top_holes.append((BOLT_CIRCLE_R * math.cos(rad),
                       BOLT_CIRCLE_R * math.sin(rad)))

make_disc("endcap-top-3hole", top_holes)

# ── Bottom cap: 1 centered hole ──

make_disc("endcap-bottom-1hole", [(0.0, 0.0)])

# ── Blank disc: no holes ──

make_disc("endcap-blank", [])

print(f"\nDisc diameter: {DISC_DIA}\"")
print(f"Hole diameter: {HOLE_DIA}\"")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")
print(f"Fits tube: 5.000\" OD x 0.065\" wall (ID = 4.870\")")
