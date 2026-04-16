"""
Carbonator end cap dishing dies: two-piece die set for press-doming a flat
0.060" 304 SS racetrack blank into a shallow spherical dome.

Female die (bottom): concave spherical cavity inside a racetrack rim.
The blank sits on the rim and is pressed into the dish.

Male die (top): convex spherical dome protruding from the bottom face.
The flat surround acts as a blank holder.  Flat top for the press ram.

Dome geometry:
  Sphere radius R = (a² + h²) / (2h) = 15.03" where a = 2.730", h = 0.250"
  Female cavity: R_female = 15.03"
  Male punch:   R_male   = 15.03 - 0.060 = 14.97" (gap = sheet thickness)
  Dome height at center: 0.250"

Rim (final cap dimensions):
  Racetrack: semicircle R = 1.930", flat length = 1.600"
  Overall: 5.460" x 3.860"

Axis convention:
  X = racetrack major axis (wide, 5.460")
  Y = racetrack minor axis (narrow, 3.860")
  Z = press direction / dome depth

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Sheet stock ──

SHEET_T = 0.060 * IN  # 304 SS blank thickness

# ── Dome geometry ──

DOME_HEIGHT = 0.250 * IN           # dome depth at center
R_FEMALE = 15.03 * IN              # sphere radius for female cavity
R_MALE = (15.03 - 0.060) * IN     # sphere radius for male punch (14.97")

# ── Racetrack rim (final cap dimensions) ──

SEMI_R = 1.930 * IN               # semicircle end radius
FLAT_LEN = 1.600 * IN             # flat straight section length
RACETRACK_X = 2 * SEMI_R + FLAT_LEN   # overall X = 5.460"
RACETRACK_Y = 2 * SEMI_R              # overall Y = 3.860"

# ── Die geometry ──

WALL = 0.375 * IN                 # wall around rim
FLOOR = 0.250 * IN                # floor under female cavity
BACKING = 0.375 * IN              # male die backing plate

# Outer footprint (racetrack + wall on each side)
OUTER_X = RACETRACK_X + 2 * WALL  # 6.210"
OUTER_Y = RACETRACK_Y + 2 * WALL  # 4.610"
OUTER_SEMI_R = SEMI_R + WALL      # 2.305"

# Block heights
FEMALE_Z = DOME_HEIGHT + FLOOR    # 0.500"
MALE_Z = DOME_HEIGHT + BACKING    # 0.625"

# ── Registration dowel pins ──

DOWEL_DIA = 0.250 * IN
DOWEL_DEPTH = 0.375 * IN
# Pins flanking the racetrack in Y, centered in the wall
DOWEL_OFFSET_Y = RACETRACK_Y / 2 + WALL / 2


def make_stadium_wire(semi_r, flat_len, workplane="XY"):
    """Create a racetrack/stadium wire on the given workplane.

    The stadium is centered at origin with the major axis along X.
    Two semicircles of radius semi_r connected by straight segments
    of length flat_len.
    """
    half_flat = flat_len / 2
    # slot2D makes a stadium: length along X, width along Y
    overall_x = 2 * semi_r + flat_len
    overall_y = 2 * semi_r
    return (
        cq.Workplane(workplane)
        .slot2D(overall_x, overall_y)
    )


def make_female_die() -> cq.Workplane:
    """Female die (bottom): concave spherical cavity in a racetrack-rimmed block.

    Block sits with its bottom face at Z = -FEMALE_Z, top (rim) face at Z = 0.
    The sphere center is at Z = R_FEMALE - DOME_HEIGHT (above the rim),
    so the cavity floor is at Z = -DOME_HEIGHT.
    """

    # ── Outer block: stadium profile extruded downward ──
    block = (
        cq.Workplane("XY")
        .slot2D(OUTER_X, OUTER_Y)
        .extrude(-FEMALE_Z)
    )

    # ── Sphere to subtract (concave cavity) ──
    # Sphere center is at Z = R_FEMALE - DOME_HEIGHT above the rim (Z=0).
    # The lowest point of the sphere is at Z = (R_FEMALE - DOME_HEIGHT) - R_FEMALE = -DOME_HEIGHT.
    sphere_center_z = R_FEMALE - DOME_HEIGHT

    sphere = cq.Workplane("XY").sphere(R_FEMALE).translate((0, 0, sphere_center_z))

    # ── Clip sphere to racetrack footprint (only cut inside the rim) ──
    # Create a tall racetrack prism to intersect with the sphere
    clip_prism = (
        cq.Workplane("XY")
        .slot2D(RACETRACK_X, RACETRACK_Y)
        .extrude(-FEMALE_Z)
    )

    cavity_tool = sphere.intersect(clip_prism)

    result = block.cut(cavity_tool)

    # ── Dowel pin holes on top face (Z = 0), drilling downward ──
    for y_sign in [+1, -1]:
        pin = (
            cq.Workplane("XY")
            .transformed(offset=(0, y_sign * DOWEL_OFFSET_Y, 0))
            .circle(DOWEL_DIA / 2)
            .extrude(-DOWEL_DEPTH)
        )
        result = result.cut(pin)

    return result


def make_male_die() -> cq.Workplane:
    """Male die (top): convex dome protruding from bottom face, flat top for ram.

    Block sits with its bottom face (dome side) at Z = 0, top face at Z = MALE_Z.
    The dome protrudes 0.250" below the surround, so the dome apex is at Z = 0
    and the flat surround is at Z = DOME_HEIGHT.  The backing plate runs from
    Z = DOME_HEIGHT to Z = MALE_Z.

    Actually, let's orient so the bottom of the dome is at Z=0 and everything
    goes up:
    - Dome apex: Z = 0
    - Flat surround: Z = DOME_HEIGHT (0.250")
    - Top of backing: Z = MALE_Z (0.625")
    """

    # ── Outer block: stadium profile from Z = DOME_HEIGHT to Z = MALE_Z ──
    # This is the backing plate + surround (no dome region yet)
    block = (
        cq.Workplane("XY")
        .workplane(offset=DOME_HEIGHT)
        .slot2D(OUTER_X, OUTER_Y)
        .extrude(BACKING)
    )

    # ── Dome: sphere intersected with racetrack footprint ──
    # Sphere center at Z = DOME_HEIGHT + R_MALE - DOME_HEIGHT = R_MALE ... wait.
    # The dome protrudes downward from the surround at Z = DOME_HEIGHT.
    # The dome apex is at Z = 0.  The sphere's lowest point should be at Z = 0.
    # So sphere center is at Z = 0 + R_MALE = R_MALE.
    # At the rim edge (racetrack boundary), the sphere surface should be at Z = DOME_HEIGHT.
    # Check: at the major axis extreme, r = 2.730", z = R_MALE - sqrt(R_MALE^2 - r^2)
    # This should equal DOME_HEIGHT. (It will be very close since R_MALE ≈ R_FEMALE.)

    sphere_center_z = R_MALE  # sphere lowest point at Z = 0

    sphere = cq.Workplane("XY").sphere(R_MALE).translate((0, 0, sphere_center_z))

    # Clip to racetrack footprint, from Z = 0 to Z = DOME_HEIGHT
    clip_prism = (
        cq.Workplane("XY")
        .slot2D(RACETRACK_X, RACETRACK_Y)
        .extrude(DOME_HEIGHT)
    )

    dome = sphere.intersect(clip_prism)

    result = block.union(dome)

    # ── Dowel pin holes on bottom face ──
    # The surround is at Z = DOME_HEIGHT.  Dowel holes drill upward from Z = DOME_HEIGHT.
    for y_sign in [+1, -1]:
        pin = (
            cq.Workplane("XY")
            .workplane(offset=DOME_HEIGHT)
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

for name, part in [("Female die (bottom)", female), ("Male die (top)", male)]:
    bb = part.val().BoundingBox()
    dx = bb.xmax - bb.xmin
    dy = bb.ymax - bb.ymin
    dz = bb.zmax - bb.zmin

    vol_mm3 = part.val().Volume()
    vol_cm3 = vol_mm3 / 1000.0
    mass_g = vol_cm3 * 1.24

    print(f"\n{name}:")
    print(f"  Bounding box: {dx:.1f} x {dy:.1f} x {dz:.1f} mm")
    print(f"               ({dx / IN:.3f} x {dy / IN:.3f} x {dz / IN:.3f} in)")
    print(f"  Volume: {vol_cm3:.1f} cm³")
    print(f"  Estimated mass (PA6-CF): {mass_g:.0f} g")
    print(f"  X range: [{bb.xmin:.1f}, {bb.xmax:.1f}]  (major axis)")
    print(f"  Y range: [{bb.ymin:.1f}, {bb.ymax:.1f}]  (minor axis)")
    print(f"  Z range: [{bb.zmin:.1f}, {bb.zmax:.1f}]  (press direction)")


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

female_path = out_dir / "dishing-die-female.step"
cq.exporters.export(female, str(female_path))
print(f"\nExported: {female_path}")

male_path = out_dir / "dishing-die-male.step"
cq.exporters.export(male, str(male_path))
print(f"Exported: {male_path}")

# ── Summary ──

print(f"\n--- Dishing die dimensions ---")
print(f"Racetrack rim: {RACETRACK_X / IN:.3f}\" x {RACETRACK_Y / IN:.3f}\"")
print(f"  Semicircle R:  {SEMI_R / IN:.3f}\"")
print(f"  Flat length:   {FLAT_LEN / IN:.3f}\"")
print(f"Dome height:     {DOME_HEIGHT / IN:.3f}\"")
print(f"Sphere R female: {R_FEMALE / IN:.3f}\"")
print(f"Sphere R male:   {R_MALE / IN:.3f}\"")
print(f"Wall:            {WALL / IN:.3f}\"")
print(f"Female block Z:  {FEMALE_Z / IN:.3f}\"  (cavity + floor)")
print(f"Male block Z:    {MALE_Z / IN:.3f}\"  (dome + backing)")
