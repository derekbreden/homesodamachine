"""
Carbonator racetrack end cap DXFs for SendCutSend.

Generates two files:
  1. Top cap blank — oversized stadium outline with 4 weld bung holes
  2. Bottom cap blank — oversized stadium outline, no holes

These are blanks for press-domed caps.  After pressing to 0.250" dome
height, the rim shrinks to slip-fit dimensions inside the rolled tube body.
Material is 0.060" 304 SS.

── Why domed caps work at 0.060" ──

A flat head resists pressure by bending (ASME UG-34):
  t = d * sqrt(C*P / S*E) = 5.470 * sqrt(0.33*70 / 20000) = 0.186"
  Requires 1/4" plate.

A domed head resists pressure by membrane stress (ASME UG-32):
  t = 0.885 * P * L / (S*E - 0.1*P)
  At t = 0.0625" (1/16"), max crown radius L = 20.17".
  Min dome height for major axis half-span a = 2.8375":
    h = L - sqrt(L^2 - a^2) = 0.201"
  Target dome height: 0.250" (25% margin).

── Blank oversize compensation ──

Doming draws material inward from the edges.  For a spherical cap of
height h over radius r, the blank radius = sqrt(r^2 + h^2).

  r = 1.930" (final slip-fit semicircle radius)
  h = 0.250" (dome height)
  r_blank = sqrt(1.930^2 + 0.250^2) = 1.946"
  delta = +0.016"

The flat length between semicircle centers is unchanged by doming.

Weld bung holes are cut at their final positions.  After doming, holes
stretch slightly larger — the 0.700" bung body drops through more easily.
The 1.000" OD flange is fillet-welded to the curved surface; minor hole
irregularity is covered by the weld seam.

── Racetrack geometry ──

The tube body is rolled from 0.048" 304 SS sheet on a slip roll (see
carbonator-body-sheet/generate_dxf.py for body blank dimensions).

Body ID (defines end cap fit):
  R=1.935", flats 1.600". Overall: 5.470" x 3.870".

End cap slip-fit (0.005" clearance/side):
  R=1.930", flats 1.600". Overall: 5.460" x 3.860".

Domed blank (oversized for draw-in):
  R=1.946", flats 1.600". Overall: 5.492" x 3.892".

Material: 304 SS, 0.060" thick.
Units: inches.  SendCutSend compensates for kerf automatically.

Weld bung: 1/4" NPT female, 304 SS, body OD 0.700", flange OD 1.000".
Hole diameter: 0.710" (body OD + 0.010" clearance).

Top cap port layout (90-deg spacing on 1.0" bolt circle):
  - 0deg (+X):   CO2 inlet (headspace)
  - 90deg (+Y):  Water inlet (atomization nozzle)
  - 180deg (-X): Carbonated water outlet (dip tube)
  - 270deg (-Y): PRV (pressure relief valve)

Assembly order:
  1. SendCutSend cuts oversized blanks with holes from 0.060" 304 SS
  2. Press-dome each blank to 0.250" crown using dishing die
  3. Roll two body half-sheets into D-halves on slip roll; butt-weld
     both flat seams together to form the closed racetrack tube
  4. Fillet-weld 4 bungs to domed top cap (flange side up / outward)
  5. Install atomization nozzle, dip tube, fittings
  6. Weld domed top cap into rolled tube body (inset slip-fit)
  7. Weld domed bottom cap into rolled tube body
  8. Install CO2 fitting and PRV from outside
  9. Passivate, hydro test
"""

import math
from pathlib import Path

import ezdxf

# ── Body interface ──
# The body ID is set by the rolled 0.048" sheet.
# See carbonator-body-sheet/generate_dxf.py for derivation.

BODY_ID_SEMI_R = 1.935     # body inner semicircle radius
BODY_ID_FLAT = 1.600       # body inner flat length

# ── End cap slip-fit dimensions (after doming) ──

CLEARANCE = 0.005          # per side
CAP_SEMICIRCLE_R = BODY_ID_SEMI_R - CLEARANCE            # 1.930"
CAP_FLAT_LEN = BODY_ID_FLAT                               # 1.600"

# ── Dome parameters ──

DOME_HEIGHT = 0.250        # dome crown height

# ── Blank oversize (pre-forming dimensions) ──

BLANK_SEMICIRCLE_R = math.sqrt(CAP_SEMICIRCLE_R**2 + DOME_HEIGHT**2)  # 1.946"
BLANK_FLAT_LEN = CAP_FLAT_LEN                           # 1.600" (unchanged)
BLANK_DELTA = BLANK_SEMICIRCLE_R - CAP_SEMICIRCLE_R     # 0.016"

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

    msp.add_arc(
        center=(half_flat, 0),
        radius=semicircle_r,
        start_angle=-90,
        end_angle=90,
    )

    msp.add_arc(
        center=(-half_flat, 0),
        radius=semicircle_r,
        start_angle=90,
        end_angle=270,
    )

    msp.add_line(
        (-half_flat, semicircle_r),
        (half_flat, semicircle_r),
    )

    msp.add_line(
        (half_flat, -semicircle_r),
        (-half_flat, -semicircle_r),
    )


def make_cap(name: str, holes: list[tuple[float, float]]) -> None:
    """Generate a DXF with oversized blank outline and optional holes."""
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 1  # inches
    msp = doc.modelspace()

    add_stadium(msp, BLANK_SEMICIRCLE_R, BLANK_FLAT_LEN)

    for cx, cy in holes:
        msp.add_circle((cx, cy), HOLE_R)

    path = OUT_DIR / f"{name}.dxf"
    doc.saveas(str(path))
    print(f"Exported: {path}  ({len(holes)} hole(s))")


# ── Compute hole positions ──

top_holes = []
for deg in PORT_ANGLES_DEG:
    rad = math.radians(deg)
    top_holes.append((BOLT_CIRCLE_R * math.cos(rad),
                       BOLT_CIRCLE_R * math.sin(rad)))

# ── Generate blanks ──

make_cap("endcap-racetrack-top", top_holes)
make_cap("endcap-racetrack-bottom-blank", [])

# ── Summary ──

print(f"\n--- Domed blank (what SendCutSend cuts) ---")
print(f"Semicircle radius: {BLANK_SEMICIRCLE_R:.4f}\"")
print(f"  (final {CAP_SEMICIRCLE_R:.3f}\" + {BLANK_DELTA:.4f}\" draw-in compensation)")
print(f"Flat length: {BLANK_FLAT_LEN:.3f}\"")
print(f"Overall: {2 * BLANK_SEMICIRCLE_R + BLANK_FLAT_LEN:.4f}\" x {2 * BLANK_SEMICIRCLE_R:.4f}\"")
print(f"After doming: {2 * CAP_SEMICIRCLE_R + CAP_FLAT_LEN:.3f}\" x {2 * CAP_SEMICIRCLE_R:.3f}\"")
print(f"Dome height: {DOME_HEIGHT:.3f}\"")
print(f"Material: 304 SS, 0.060\" thick")
print(f"Hole diameter: {HOLE_DIA}\"")
print(f"Bolt circle radius: {BOLT_CIRCLE_R}\"")
