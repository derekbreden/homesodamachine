"""
Carbonator body press dies: two-piece die set for press-forming a flat
0.048" 304 SS sheet blank into one half (a "D-half") of the racetrack-
cross-section tube body.  Two D-halves are butt-welded along both flat
edges to close the full racetrack.  Order qty 2 of this die set to make
one vessel (one die set yields one D-half per stroke; two D-halves per
vessel — a second set lets both halves be formed in parallel if desired,
otherwise a single set can cycle twice).

Female die (bottom): concave U-shaped cavity in a block.  Extruded along
the tube axis (Y).  The blank lies flat on the top face ("die land"),
then the male punch drives it straight down into the cavity.

Male die (top): convex U-shaped punch protruding from the bottom face.
The flat flange around the punch acts as a blank holder, pinning the
blank edges against the female's top face so the sheet cannot wrinkle
or lift as it wraps around the punch.

D-half cross-section (the target formed shape, inside surface):
  Two vertical tangent walls, 0.800" tall, at X = ±1.935
  Semicircle at the bottom, R = 1.935", center at (0, -0.800)
  Apex of semicircle at Z = -(0.800 + 1.935) = -2.735"
  Developed blank length: 0.800 + π*(1.935 + 0.048/2) + 0.800 = 7.754"

The OUTSIDE of the sheet rides against the female cavity: all female
radii are 0.048" larger than the male so the gap at full stroke equals
sheet thickness.

Axis convention (pressing orientation):
  X = across the press bed, weld-line direction
  Y = along the tube axis (6.000" long)
  Z = vertical, press direction (Z=0 is the female die's top / die land,
      Z<0 is inside the cavity, Z>0 is where the male die sits)

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import math
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Sheet stock ──

SHEET_T = 0.048 * IN  # 304 SS annealed blank thickness

# ── D-half cross-section geometry (inside surface of the formed sheet) ──

INSIDE_R = 1.935 * IN              # inside semicircle radius (tube ID at curved end)
TANGENT_LEN = 0.800 * IN           # tangent-wall height per side
TUBE_AXIS_LEN = 6.000 * IN         # length along Y

# Outside surface radii (what the female cavity sees)
OUTSIDE_R = INSIDE_R + SHEET_T     # 1.983"

# ── Springback compensation ──
#
# 304 SS at R/t ≈ 40 typically springs back 3–8% on tight wraps.  Batch-to-
# batch yield variation (σ_y 205–290 MPa within the annealed spec range)
# is the dominant source of spread.  v1 runs with zero compensation: form
# a part, measure it against the R=1.930" end-cap slip fit, then bump this
# number and reprint if the walls open up or the radius is loose.
#
# Non-zero values shrink both die radii by the same fractional amount so
# the punch-to-cavity gap stays equal to SHEET_T at every point on the D.
# The over-formed part then springs back toward the nominal target.
#
# Typical first-revision value after measuring: 0.03–0.05 (3–5%).

SPRINGBACK_COMP = 0.0              # fractional over-bend (0.0 = no compensation)

INSIDE_R_DIE = INSIDE_R * (1.0 - SPRINGBACK_COMP)
OUTSIDE_R_DIE = INSIDE_R_DIE + SHEET_T

# Developed flat blank length (for cross-reference with the DXF generator)
BLANK_DEVELOPED = (
    TANGENT_LEN
    + math.pi * (INSIDE_R + SHEET_T / 2)
    + TANGENT_LEN
)  # ≈ 7.754"

# ── Die geometry ──

WALL = 0.500 * IN                  # wall around cavity perimeter (heavier than dishing)
FLOOR = 0.500 * IN                 # floor below cavity (female)
BACKING = 0.500 * IN               # backing plate above flange (male)

# Female cavity descent (top-of-land at Z=0 down to apex)
FEMALE_CAVITY_DEPTH = TANGENT_LEN + OUTSIDE_R_DIE  # ≈ 0.800 + 1.983 = 2.783"
# Male punch descent (flange at Z=0 down to apex)
MALE_PUNCH_DEPTH = TANGENT_LEN + INSIDE_R_DIE      # ≈ 0.800 + 1.935 = 2.735"

# Outer footprint (cavity + WALL on each X side, TUBE_AXIS_LEN + WALL on each Y side)
OUTER_X = 2 * OUTSIDE_R_DIE + 2 * WALL             # ≈ 2*1.983 + 2*0.500 = 4.966"
OUTER_Y = TUBE_AXIS_LEN + 2 * WALL                 # 6.000 + 1.000 = 7.000"

# Block heights
FEMALE_Z = FEMALE_CAVITY_DEPTH + FLOOR             # 2.783 + 0.500 = 3.283"
MALE_Z = MALE_PUNCH_DEPTH + BACKING                # 2.735 + 0.500 = 3.235"

# ── Registration dowel pins ──

DOWEL_DIA = 0.250 * IN
DOWEL_DEPTH = 0.375 * IN
# Pins on the tube-axis centerline (X=0), flanking the cavity in Y,
# centered in the 0.500" wall that caps each Y end.
DOWEL_OFFSET_Y = TUBE_AXIS_LEN / 2 + WALL / 2      # 3.000 + 0.250 = 3.250"


def make_d_half_wire(inside_r: float, tangent_len: float) -> cq.Workplane:
    """Draw a closed D cross-section wire on the XZ plane.

    The D opens upward (toward +Z).  The two tangent walls run from
    (±inside_r, 0) down to (±inside_r, -tangent_len), then a semicircle
    from (+inside_r, -tangent_len) through the apex (0, -(tangent_len +
    inside_r)) back to (-inside_r, -tangent_len).  The top (Z=0) is
    closed with a straight segment so the resulting wire is a closed
    planar face that can be extruded along Y.
    """
    apex_z = -(tangent_len + inside_r)
    return (
        cq.Workplane("XZ")
        .moveTo(-inside_r, 0)
        .lineTo(-inside_r, -tangent_len)
        .threePointArc(
            (0, apex_z),
            (inside_r, -tangent_len),
        )
        .lineTo(inside_r, 0)
        .close()
    )


def make_female_die() -> cq.Workplane:
    """Female die (bottom): concave D cavity in a rectangular block.

    Block bottom face at Z = -FEMALE_Z, top face ("die land") at Z = 0.
    Cavity is the D cross-section (OUTSIDE_R, TANGENT_LEN) extruded
    along Y for TUBE_AXIS_LEN, centered in the block.
    """

    # ── Outer block: rectangle extruded downward ──
    block = (
        cq.Workplane("XY")
        .rect(OUTER_X, OUTER_Y)
        .extrude(-FEMALE_Z)
    )

    # ── Cavity: D-shape on XZ, extruded along Y ──
    # The wire lives on XZ at Y=0; extrude symmetrically ±TUBE_AXIS_LEN/2.
    d_wire = make_d_half_wire(OUTSIDE_R_DIE, TANGENT_LEN)
    cavity = d_wire.extrude(TUBE_AXIS_LEN / 2, both=True)

    result = block.cut(cavity)

    # ── Dowel pin holes on top face (Z=0), drilling downward ──
    for y_sign in (+1, -1):
        pin = (
            cq.Workplane("XY")
            .transformed(offset=(0, y_sign * DOWEL_OFFSET_Y, 0))
            .circle(DOWEL_DIA / 2)
            .extrude(-DOWEL_DEPTH)
        )
        result = result.cut(pin)

    return result


def make_male_die() -> cq.Workplane:
    """Male die (top): convex D punch below a rectangular flange block.

    The flange sits at Z in [0, BACKING], the punch protrudes downward
    from the flange to Z = -MALE_PUNCH_DEPTH.  When the male die is set
    on top of the female die, their parting planes (Z=0) coincide and
    the punch drops into the cavity with a uniform SHEET_T gap.
    """

    # ── Flange + backing block: rectangle from Z=0 upward ──
    block = (
        cq.Workplane("XY")
        .rect(OUTER_X, OUTER_Y)
        .extrude(BACKING)
    )

    # ── Punch: D cross-section (INSIDE_R_DIE, TANGENT_LEN) extruded along Y ──
    d_wire = make_d_half_wire(INSIDE_R_DIE, TANGENT_LEN)
    punch = d_wire.extrude(TUBE_AXIS_LEN / 2, both=True)

    result = block.union(punch)

    # ── Dowel pin holes on bottom face (Z=0), drilling upward ──
    for y_sign in (+1, -1):
        pin = (
            cq.Workplane("XY")
            .transformed(offset=(0, y_sign * DOWEL_OFFSET_Y, 0))
            .circle(DOWEL_DIA / 2)
            .extrude(DOWEL_DEPTH)
        )
        result = result.cut(pin)

    return result


# ═══════════════════════════════════════════════════════
# BUILD
# ═══════════════════════════════════════════════════════

female = make_female_die()
male = make_male_die()


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

# Constraint thresholds
H2C_X, H2C_Y, H2C_Z = 300.0, 320.0, 325.0   # Bambu H2C usable build volume (mm)
PRESS_THROAT = 250.0                         # max footprint dim, mm (H-frame clearance)
MASS_LIMIT = 1500.0                          # g per half

all_pass = True

for name, part in [("Female die (bottom)", female), ("Male die (top)", male)]:
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
    print(f"  X range: [{bb.xmin:.1f}, {bb.xmax:.1f}]  (across press bed / weld line)")
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

female_path = out_dir / "body-press-die-female.step"
cq.exporters.export(female, str(female_path))
print(f"\nExported: {female_path}")

male_path = out_dir / "body-press-die-male.step"
cq.exporters.export(male, str(male_path))
print(f"Exported: {male_path}")

# ── Summary ──

print(f"\n--- Body press die dimensions ---")
print(f"Sheet thickness:       {SHEET_T / IN:.3f}\"")
print(f"Springback comp:       {SPRINGBACK_COMP:.3f}  ({SPRINGBACK_COMP*100:.1f}% over-bend)")
print(f"Target inside  semi-R: {INSIDE_R / IN:.3f}\"  (formed part after springback)")
print(f"Target outside semi-R: {OUTSIDE_R / IN:.3f}\"")
print(f"Die inside  semi-R (male):   {INSIDE_R_DIE / IN:.3f}\"")
print(f"Die outside semi-R (female): {OUTSIDE_R_DIE / IN:.3f}\"")
print(f"Tangent-wall length:   {TANGENT_LEN / IN:.3f}\" per side")
print(f"Tube axis length:      {TUBE_AXIS_LEN / IN:.3f}\"")
print(f"Developed blank length: {BLANK_DEVELOPED / IN:.3f}\"")
print(f"Wall:                  {WALL / IN:.3f}\"")
print(f"Floor (female):        {FLOOR / IN:.3f}\"")
print(f"Backing (male):        {BACKING / IN:.3f}\"")
print(f"Outer footprint:       {OUTER_X / IN:.3f}\" x {OUTER_Y / IN:.3f}\"")
print(f"Female block Z:        {FEMALE_Z / IN:.3f}\"  (cavity {FEMALE_CAVITY_DEPTH/IN:.3f}\" + floor)")
print(f"Male block Z:          {MALE_Z / IN:.3f}\"  (punch {MALE_PUNCH_DEPTH/IN:.3f}\" + backing)")
print(f"Radial gap at stroke:  {(OUTSIDE_R_DIE - INSIDE_R_DIE) / IN:.3f}\"  (= sheet thickness)")
