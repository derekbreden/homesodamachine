"""
Carbonator body squash dies: two-piece die set for crushing a round 304 SS
tube (5.000" OD x 0.065" wall x 6.000" long) into the racetrack cross-
section carbonator body, in a single closing stroke on a 12-ton H-frame
press.  Alternate fabrication path to the D-half press dies — this one
produces a seamless body (no butt welds) at the cost of needing tube
stock and an internal-support strategy (sand-pack primary).

Upper die (press ram side): rectangular block with the upper half of the
racetrack OD cavity cut into its lower (parting) face.  The cavity is
extruded along the tube axis (Y).

Lower die (press bed side): rectangular block with the lower half of the
racetrack OD cavity cut into its upper (parting) face.  Mirror image of
the upper.

When the press closes, the two parting faces meet at Z=0 and the two
cavity halves form a closed racetrack-OD bore around the tube.  The tube
starts round (5.000" OD) and is flattened until it matches the cavity.

Racetrack OD cross-section (XZ plane, tube extrudes along Y):
  Two semicircles of R = 2.000", centers at (X=+/-0.800, Z=0)
  Two flat tangent walls at Z = +/-2.000", X in [-0.800, +0.800]
  Overall: 5.600" (X) x 4.000" (Z)

Racetrack ID (after forming, for reference — not cut into this die):
  Semicircle R = 1.935"  (= 2.000 - 0.065 wall)
  Flat length = 1.600"  (same as OD flat length; wall is constant)
  Overall ID: 5.470" x 3.870"

Axis convention (pressing orientation):
  X = across the press bed, long axis of the racetrack
  Y = along the tube axis (6.000" long)
  Z = vertical, press direction (ram is +Z, bed is -Z, parting plane Z=0)

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Tube stock (starting material) ──
#
# Commercial-grade 304 SS round tube.  0.065" is the smallest standard
# catalog wall on 5" OD; the earlier 0.048" wall plan does not apply to
# tube stock.  McMaster 89955K85 or equivalent.

TUBE_OD_START = 5.000 * IN         # pre-forming tube OD (round)
TUBE_WALL = 0.065 * IN             # tube wall thickness
TUBE_ID_START = TUBE_OD_START - 2 * TUBE_WALL   # pre-forming tube ID = 4.870"
TUBE_AXIS_LEN = 6.000 * IN         # length along Y

# ── Racetrack OD cross-section (final formed shape — cavity profile) ──
#
# OD semicircle R is set by body ID + one wall: end-cap slip-fit ID at the
# curved end is R = 1.935" (unchanged from the D-half plan), so OD radius
# R = 1.935 + 0.065 = 2.000".  Flat length is unchanged at 1.600".

OD_SEMI_R = 2.000 * IN             # racetrack OD semicircle radius
OD_FLAT_LEN = 1.600 * IN           # racetrack OD flat-wall length (X direction)

# Derived racetrack OD bounding box
RACETRACK_OD_X = OD_FLAT_LEN + 2 * OD_SEMI_R   # 1.600 + 4.000 = 5.600"
RACETRACK_OD_Z = 2 * OD_SEMI_R                 # 4.000"

# Hoop stress at 70 PSI design pressure (for reference / traceability)
# σ = P * D / (2 * t) = 70 * 5.600 / (2 * 0.065) ≈ 3,015 PSI → 6.6x SF
# on 20,000 PSI allowable for 304 SS.

# ── Springback compensation ──
#
# On a tube-squash the minor-axis flats want to re-bulge outward after
# the press opens (elastic recovery of the freshly-bent flat walls), and
# the major-axis semicircles want to relax slightly larger.  Simplest
# correction: shrink the cavity Z depth — pull the upper and lower flats
# closer together — so the part springs back to the nominal 4.000" minor
# axis.  The X dimension is governed by the semicircle diameter, which is
# mechanically pinned by the tube's circumference, so we leave X alone.
#
# v1 runs with zero compensation: squash a tube, measure it against the
# R=1.930" end-cap slip-fit gauge (or just caliper the minor axis), then
# bump this number and reprint if the flats bulge open.
#
# Typical first-revision value after measuring: 0.02–0.04 (2–4%).

SPRINGBACK_COMP = 0.0              # fractional over-squash of cavity Z depth

# Effective cavity half-depth in Z (parting plane at Z=0 to far flat at Z=±half)
CAVITY_HALF_Z = OD_SEMI_R * (1.0 - SPRINGBACK_COMP)

# ── Die geometry ──

WALL = 0.500 * IN                  # wall around cavity perimeter (match body-press-dies)
FLOOR = 0.500 * IN                 # backing above/below cavity

# Outer footprint (cavity + WALL on each X side, TUBE_AXIS_LEN + WALL on each Y side)
OUTER_X = RACETRACK_OD_X + 2 * WALL            # 5.600 + 1.000 = 6.600"
OUTER_Y = TUBE_AXIS_LEN + 2 * WALL             # 6.000 + 1.000 = 7.000"

# Block height per half: cavity-half depth + floor
BLOCK_Z = CAVITY_HALF_Z + FLOOR                # 2.000 + 0.500 = 2.500"

# ── Registration dowel pins ──

DOWEL_DIA = 0.250 * IN
DOWEL_DEPTH = 0.375 * IN
# Pins on the long-axis centerline (X=0), flanking the cavity in Y,
# centered in the 0.500" wall that caps each Y end.
DOWEL_OFFSET_Y = TUBE_AXIS_LEN / 2 + WALL / 2  # 3.000 + 0.250 = 3.250"


def make_half_cavity_wire(semi_r: float, flat_len: float, half_z: float,
                           upper: bool) -> cq.Workplane:
    """Build the half-racetrack cavity cross-section as a closed wire.

    Uses two genuine quarter-arc segments (via threePointArc) plus two
    straight segments to trace the closed half-profile on XZ.

    Path (upper half, Z >= 0):
      (x_far_left, 0)
        -> quarter arc through apex (x_left_c, +half_z)   [radius semi_r]
      (x_left_c, +half_z)
        -> straight flat to (x_right_c, +half_z)
      (x_right_c, +half_z)
        -> quarter arc through (x_far_right, 0)           [radius semi_r]
      (x_far_right, 0)
        -> straight back along parting plane to (x_far_left, 0)
        (implicit .close())

    For the lower half (Z <= 0), mirror Z.
    """
    sign = +1 if upper else -1
    x_left_c = -flat_len / 2
    x_right_c = +flat_len / 2
    x_far_left = x_left_c - semi_r
    x_far_right = x_right_c + semi_r
    z_flat = sign * half_z
    # Quarter-arc midpoints: at 45° between the parting-plane endpoint
    # and the flat-tangent endpoint, relative to each semicircle center.
    # For the left semicircle at (x_left_c, 0) the quarter arc goes from
    # (x_far_left, 0) to (x_left_c, z_flat), passing through the point
    # at 135° (upper) or 225° (lower) — i.e. (x_left_c - semi_r*cos45,
    # sign*semi_r*sin45).
    cos45 = math.sqrt(2) / 2
    mid_left = (x_left_c - semi_r * cos45, sign * semi_r * cos45)
    mid_right = (x_right_c + semi_r * cos45, sign * semi_r * cos45)

    return (
        cq.Workplane("XZ")
        .moveTo(x_far_left, 0)
        .threePointArc(mid_left, (x_left_c, z_flat))
        .lineTo(x_right_c, z_flat)
        .threePointArc(mid_right, (x_far_right, 0))
        .close()
    )


def make_die_half(upper: bool) -> cq.Workplane:
    """Build one die half (upper or lower).

    Rectangular block OUTER_X x OUTER_Y x BLOCK_Z.  For the upper die
    the parting face is at Z=0 and the block extends to Z=+BLOCK_Z; the
    cavity (upper half of racetrack OD) is cut downward from the parting
    face into the block.  For the lower die it's mirrored: parting face
    at Z=0, block from Z=0 down to Z=-BLOCK_Z, cavity cut upward into it.

    Dowel pin holes drill into the parting face so the two halves
    register when clamped together.
    """
    sign = +1 if upper else -1

    # ── Outer block ──
    block = (
        cq.Workplane("XY")
        .rect(OUTER_X, OUTER_Y)
        .extrude(sign * BLOCK_Z)
    )

    # ── Cavity: half-racetrack on XZ, extruded along Y ──
    cavity_wire = make_half_cavity_wire(
        OD_SEMI_R, OD_FLAT_LEN, CAVITY_HALF_Z, upper=upper,
    )
    cavity = cavity_wire.extrude(TUBE_AXIS_LEN / 2, both=True)

    result = block.cut(cavity)

    # ── Dowel pin holes on parting face (Z=0), drilling into the block ──
    for y_sign in (+1, -1):
        pin = (
            cq.Workplane("XY")
            .transformed(offset=(0, y_sign * DOWEL_OFFSET_Y, 0))
            .circle(DOWEL_DIA / 2)
            .extrude(sign * DOWEL_DEPTH)
        )
        result = result.cut(pin)

    return result


# ═══════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════

upper = make_die_half(upper=True)
lower = make_die_half(upper=False)


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

# Constraint thresholds
H2C_X, H2C_Y, H2C_Z = 300.0, 320.0, 325.0   # Bambu H2C usable build volume (mm)
PRESS_THROAT = 250.0                         # max footprint dim, mm (H-frame clearance)
MASS_LIMIT = 1500.0                          # g per half

all_pass = True

for name, part in [("Upper die (ram side)", upper), ("Lower die (bed side)", lower)]:
    bb = part.val().BoundingBox()
    dx = bb.xmax - bb.xmin
    dy = bb.ymax - bb.ymin
    dz = bb.zmax - bb.zmin

    vol_mm3 = part.val().Volume()
    vol_cm3 = vol_mm3 / 1000.0
    mass_g = vol_cm3 * 1.24  # PA6-CF density 1.24 g/cm³

    fits_printer = dx <= H2C_X and dy <= H2C_Y and dz <= H2C_Z
    fits_press = max(dx, dy, dz) <= PRESS_THROAT
    mass_ok = mass_g <= MASS_LIMIT

    print(f"\n{name}:")
    print(f"  Bounding box: {dx:.1f} x {dy:.1f} x {dz:.1f} mm")
    print(f"               ({dx / IN:.3f} x {dy / IN:.3f} x {dz / IN:.3f} in)")
    print(f"  Volume: {vol_cm3:.1f} cm³")
    print(f"  Estimated mass (PA6-CF): {mass_g:.0f} g")
    print(f"  X range: [{bb.xmin:.1f}, {bb.xmax:.1f}]  (racetrack long axis)")
    print(f"  Y range: [{bb.ymin:.1f}, {bb.ymax:.1f}]  (tube axis)")
    print(f"  Z range: [{bb.zmin:.1f}, {bb.zmax:.1f}]  (press direction)")
    print(f"  Check - fits H2C (300 x 320 x 325 mm): "
          f"{'PASS' if fits_printer else 'FAIL'}")
    print(f"  Check - max footprint <= {PRESS_THROAT:.0f} mm (press throat): "
          f"{'PASS' if fits_press else 'FAIL'}")
    print(f"  Check - mass <= {MASS_LIMIT:.0f} g: "
          f"{'PASS' if mass_ok else 'FAIL'}")

    all_pass = all_pass and fits_printer and fits_press and mass_ok

print(f"\nOverall: {'ALL CHECKS PASS' if all_pass else 'ONE OR MORE CHECKS FAILED'}")


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

upper_path = out_dir / "body-squash-die-upper.step"
cq.exporters.export(upper, str(upper_path))
print(f"\nExported: {upper_path}")

lower_path = out_dir / "body-squash-die-lower.step"
cq.exporters.export(lower, str(lower_path))
print(f"Exported: {lower_path}")

# ── Summary ──

print(f"\n--- Body squash die dimensions ---")
print(f"Tube stock:            {TUBE_OD_START / IN:.3f}\" OD x "
      f"{TUBE_WALL / IN:.3f}\" wall x {TUBE_AXIS_LEN / IN:.3f}\" long")
print(f"Tube ID (pre-forming): {TUBE_ID_START / IN:.3f}\"")
print(f"Springback comp:       {SPRINGBACK_COMP:.3f}  "
      f"({SPRINGBACK_COMP*100:.1f}% cavity-depth over-squash)")
print(f"Target OD semi-R:      {OD_SEMI_R / IN:.3f}\"  (formed part after springback)")
print(f"Target OD flat length: {OD_FLAT_LEN / IN:.3f}\"")
print(f"Racetrack OD box:      {RACETRACK_OD_X / IN:.3f}\" x {RACETRACK_OD_Z / IN:.3f}\"")
print(f"Cavity half-depth (Z): {CAVITY_HALF_Z / IN:.3f}\"  (per die half)")
print(f"Tube axis length (Y):  {TUBE_AXIS_LEN / IN:.3f}\"")
print(f"Wall:                  {WALL / IN:.3f}\"")
print(f"Floor:                 {FLOOR / IN:.3f}\"")
print(f"Outer footprint:       {OUTER_X / IN:.3f}\" x {OUTER_Y / IN:.3f}\"")
print(f"Block Z (per half):    {BLOCK_Z / IN:.3f}\"  "
      f"(cavity {CAVITY_HALF_Z/IN:.3f}\" + floor {FLOOR/IN:.3f}\")")
print(f"Closed stack height:   {2 * BLOCK_Z / IN:.3f}\"  (upper + lower at Z=0)")
