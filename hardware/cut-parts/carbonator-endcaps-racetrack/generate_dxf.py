"""
Carbonator racetrack end cap DXFs for SendCutSend.

Generates three files:
  1. Top cap — stadium/racetrack outline with 4 weld bung holes
  2. Bottom cap — stadium/racetrack outline, no holes
  3. Die profile — the external racetrack cross-section (tube OD shape)
     used as the cavity reference for 3D-printed forming dies

The racetrack geometry preserves the circumference of the original 5" round
tube (15.71") so a hydraulic press can deform round tube stock into this
shape without stretching or compressing the material.

Racetrack (external, tube OD):
  Two semicircles of radius 2.000" connected by two flat sides of 1.600".
  Overall: 5.600" wide x 4.000" tall.
  Circumference: pi * 4.000 + 2 * 1.600 = 15.766" (vs. 15.708" for 5" circle).

Racetrack (internal, tube ID):
  Wall thickness 0.065".  Uniform inward offset.
  Semicircle radius: 2.000 - 0.065 = 1.935"
  Flat length: 1.600" (unchanged by wall offset)
  Overall: 5.470" wide x 3.870" tall.

End cap (inset slip-fit):
  0.005" clearance per side (0.010" total on diameter), same as circular caps.
  Semicircle radius: 1.935 - 0.005 = 1.930"
  Flat length: 1.600" (unchanged — clearance is radial, not axial along flats)
  Overall: 5.460" wide x 3.860" tall.

Material: 304 stainless steel, 0.250" (1/4") thick.
  UG-34 check: longest span 5.470", t_min = 0.186". 1/4" gives 34% margin.

Hole diameter: 0.710" (for weld bung body OD 0.700" + 0.010" clearance)

Units: inches.
SendCutSend compensates for kerf automatically — draw nominal dimensions.

Weld bung: 1/4" NPT female, 304 SS, stepped body OD 0.700", flange OD 1.000"
The body drops through the hole; the flange sits on the disc surface and
is fillet-welded with the laser welder.

Top cap port layout (90-degree spacing on 1.0" bolt circle radius, same as circular):
  - Position 1 (0deg, +X):   CO2 inlet (headspace)
  - Position 2 (90deg, +Y):  Water inlet (atomization nozzle)
  - Position 3 (180deg, -X): Carbonated water outlet (dip tube)
  - Position 4 (270deg, -Y): PRV (pressure relief valve)

All four holes sit well within the cap boundary.  At 1.0" bolt circle + 0.355"
hole radius = 1.355" from center, vs. 1.930" minimum radius of the cap profile.

Assembly order (same as circular):
  1. Fillet-weld all 4 bungs to top cap (flange side up / outward)
  2. Install atomization nozzle from outside
  3. Install dip tube compression fitting + tube through bung bore
  4. Press round tube into racetrack using die set
  5. Weld top cap into formed tube (inset slip-fit)
  6. Weld bottom cap into formed tube
  7. Install CO2 fitting and PRV from outside
  8. Passivate, hydro test
"""

import math
from pathlib import Path

import ezdxf

# ── External racetrack (tube OD) ──

EXT_SEMICIRCLE_R = 2.000   # radius of each semicircle end
EXT_FLAT_LEN = 1.600       # length of each straight side
WALL_THICKNESS = 0.065     # tube wall

# ── Internal racetrack (tube ID) ──

INT_SEMICIRCLE_R = EXT_SEMICIRCLE_R - WALL_THICKNESS   # 1.935"
INT_FLAT_LEN = EXT_FLAT_LEN                            # 1.600"

# ── End cap (slip-fit inside tube) ──

CLEARANCE = 0.005          # per side
CAP_SEMICIRCLE_R = INT_SEMICIRCLE_R - CLEARANCE         # 1.930"
CAP_FLAT_LEN = INT_FLAT_LEN                             # 1.600"

# ── Weld bung holes ──

HOLE_DIA = 0.710
HOLE_R = HOLE_DIA / 2      # 0.355"
BOLT_CIRCLE_R = 1.000
PORT_ANGLES_DEG = [0, 90, 180, 270]

OUT_DIR = Path(__file__).resolve().parent


def add_stadium(msp, semicircle_r: float, flat_len: float) -> None:
    """Draw a stadium (racetrack) outline centered at the origin.

    Long axis along X.  Two semicircles at x = +/- flat_len/2,
    connected by two horizontal lines at y = +/- semicircle_r.
    """
    half_flat = flat_len / 2

    # Right semicircle: center (+half_flat, 0), from -90 to +90
    msp.add_arc(
        center=(half_flat, 0),
        radius=semicircle_r,
        start_angle=-90,
        end_angle=90,
    )

    # Left semicircle: center (-half_flat, 0), from +90 to +270
    msp.add_arc(
        center=(-half_flat, 0),
        radius=semicircle_r,
        start_angle=90,
        end_angle=270,
    )

    # Top flat: from left semicircle top to right semicircle top
    msp.add_line(
        (-half_flat, semicircle_r),
        (half_flat, semicircle_r),
    )

    # Bottom flat: from right semicircle bottom to left semicircle bottom
    msp.add_line(
        (half_flat, -semicircle_r),
        (-half_flat, -semicircle_r),
    )


def make_cap(name: str, holes: list[tuple[float, float]]) -> None:
    """Generate a DXF with stadium outline and optional holes."""
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    add_stadium(msp, CAP_SEMICIRCLE_R, CAP_FLAT_LEN)

    for cx, cy in holes:
        msp.add_circle((cx, cy), HOLE_R)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(holes)} hole(s))")


def make_die_profile() -> None:
    """Generate a DXF of the external racetrack cross-section.

    This is the shape of the tube OD after pressing — use it as the
    cavity profile for the 3D-printed forming dies.
    """
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1
    msp = doc.modelspace()

    add_stadium(msp, EXT_SEMICIRCLE_R, EXT_FLAT_LEN)

    path = OUT_DIR / "die-profile-racetrack.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  (die cavity reference)")


# ── Top cap: 4 holes at 90-degree intervals on bolt circle ──

top_holes = []
for deg in PORT_ANGLES_DEG:
    rad = math.radians(deg)
    top_holes.append((BOLT_CIRCLE_R * math.cos(rad),
                       BOLT_CIRCLE_R * math.sin(rad)))

make_cap("endcap-racetrack-top", top_holes)

# ── Bottom cap: blank ──

make_cap("endcap-racetrack-bottom-blank", [])

# ── Die profile ──

make_die_profile()

# ── Summary ──

print(f"\n--- End cap dimensions ---")
print(f"Semicircle radius: {CAP_SEMICIRCLE_R:.3f}\"")
print(f"Flat length: {CAP_FLAT_LEN:.3f}\"")
print(f"Overall: {2 * CAP_SEMICIRCLE_R + CAP_FLAT_LEN:.3f}\" x {2 * CAP_SEMICIRCLE_R:.3f}\"")
print(f"Hole diameter: {HOLE_DIA}\" (for weld bung body)")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
print(f"Material: 304 SS, 0.250\" thick")

print(f"\n--- External racetrack (die profile) ---")
print(f"Semicircle radius: {EXT_SEMICIRCLE_R:.3f}\"")
print(f"Flat length: {EXT_FLAT_LEN:.3f}\"")
print(f"Overall: {2 * EXT_SEMICIRCLE_R + EXT_FLAT_LEN:.3f}\" x {2 * EXT_SEMICIRCLE_R:.3f}\"")
print(f"Circumference: {math.pi * 2 * EXT_SEMICIRCLE_R + 2 * EXT_FLAT_LEN:.3f}\"")
print(f"(Original 5\" circle: {math.pi * 5:.3f}\")")

print(f"\n--- Internal racetrack (tube ID) ---")
print(f"Semicircle radius: {INT_SEMICIRCLE_R:.3f}\"")
print(f"Overall: {2 * INT_SEMICIRCLE_R + INT_FLAT_LEN:.3f}\" x {2 * INT_SEMICIRCLE_R:.3f}\"")
