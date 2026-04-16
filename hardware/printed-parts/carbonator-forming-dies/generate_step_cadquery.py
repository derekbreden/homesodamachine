"""
Carbonator tube forming dies: clamshell die set for pressing 5" round
304 SS tube into a stadium/racetrack cross-section.

Both halves are external — no mandrel enters the tube.  Each half is a
half-pipe channel that the tube lays in lengthwise.  The racetrack is the
CROSS-SECTION of the channel, extruded along the tube axis.

Female die (bottom): half-pipe trough (bottom half of racetrack),
tube lays in it horizontally.  Sits on the press platen.

Male die (top): half-pipe trough inverted (top half of racetrack),
closes down over the tube.  Flat top for the press ram.

Variable wall thickness:
  - Semicircle end walls: 0.500" (resists lateral forming force, bending loads)
  - Floor / ceiling: 0.250" (pure compression against platen / ram)
  - Outer profile follows the stadium shape (no rectangular corners)

The outer shell is a stadium offset 0.500" from the inner cavity, then
clipped in Z to give 0.250" floor/ceiling.  This smoothly transitions
from 0.500" at the semicircle tips to 0.250" at the floor.

Axis convention:
  X = tube axis (die length, 6.250")
  Y = racetrack major axis (horizontal, 5.675" wide)
  Z = racetrack minor axis (vertical, 3.875" tall, press direction)

Springback-compensated dimensions (midpoints of README ranges):
  Minor axis (height): 3.875"
  Major axis (width):  5.675"
  Semicircle radius:   1.875"
  Flat side length:    5.675 - 2 * 1.875 = 1.925"

Tube: 5.000" OD, 0.065" wall, 6.000" long.
Die length (extrusion along X): 6.250".

Units: inches throughout, converted to mm for CadQuery at export.

Run with: tools/cad-venv/bin/python generate_step_cadquery.py
"""

from pathlib import Path
import cadquery as cq

# ── Conversion ──

IN = 25.4  # mm per inch

# ── Tube stock ──

TUBE_OD = 5.000 * IN
TUBE_WALL = 0.065 * IN
TUBE_LEN = 6.000 * IN

# ── Springback-compensated die cavity (racetrack = tube OD after forming) ──

COMP_MINOR = 3.875 * IN        # overall height of racetrack cross-section
COMP_MAJOR = 5.675 * IN        # overall width
COMP_SEMI_R = 1.875 * IN       # semicircle end radius
COMP_FLAT = COMP_MAJOR - 2 * COMP_SEMI_R  # flat side length: 1.925"

# ── Die geometry ──

DIE_LEN = 6.250 * IN           # extrusion length along tube axis (X)
SIDE_WALL = 0.500 * IN         # semicircle end walls (bending loads)
FLOOR_WALL = 0.250 * IN        # floor / ceiling (compression only)
TROUGH_DEPTH = COMP_MINOR / 2  # half the minor axis = 1.9375"

# Outer stadium: uniform SIDE_WALL offset from inner cavity
OUTER_MAJOR = COMP_MAJOR + 2 * SIDE_WALL   # 6.675"
OUTER_MINOR = COMP_MINOR + 2 * SIDE_WALL   # 4.875"

# Block Z height per half: trough depth + floor
BLOCK_Z = TROUGH_DEPTH + FLOOR_WALL        # 2.1875"

# ── Registration dowel pins ──

DOWEL_DIA = 0.250 * IN
DOWEL_DEPTH = 0.375 * IN
# Pins at the Y extremes, centered in the 0.500" side wall at the parting line
DOWEL_OFFSET_Y = COMP_MAJOR / 2 + SIDE_WALL / 2

# ── Entry chamfer ──

ENTRY_CHAMFER = 0.125 * IN


def make_half_stadium_channel(is_bottom: bool) -> cq.Workplane:
    """Create a die half with a half-pipe racetrack channel.

    The channel runs along X (tube axis).  The racetrack cross-section
    is in the YZ plane.  The outer shell follows the stadium profile
    (no rectangular corners), clipped in Z for thinner floor/ceiling.

    For is_bottom=True: block below parting line (Z=0), trough opens up.
    For is_bottom=False: block above parting line (Z=0), trough opens down.
    """

    # ── Outer stadium shell (full height, both halves) ──
    outer_full = (
        cq.Workplane("YZ")
        .slot2D(OUTER_MAJOR, OUTER_MINOR)
        .extrude(DIE_LEN / 2, both=True)
    )

    # ── Clip to correct Z range (one half + floor thickness) ──
    if is_bottom:
        clip_box = (
            cq.Workplane("XY")
            .box(DIE_LEN + 1, OUTER_MAJOR + 1, BLOCK_Z,
                 centered=(True, True, False))
            .translate((0, 0, -BLOCK_Z))
        )
    else:
        clip_box = (
            cq.Workplane("XY")
            .box(DIE_LEN + 1, OUTER_MAJOR + 1, BLOCK_Z,
                 centered=(True, True, False))
        )

    block = outer_full.intersect(clip_box)

    # ── Cut inner trough (half of the racetrack cavity) ──
    inner_cavity = (
        cq.Workplane("YZ")
        .slot2D(COMP_MAJOR, COMP_MINOR)
        .extrude(DIE_LEN / 2, both=True)
    )

    result = block.cut(inner_cavity)

    # ── Entry chamfers at each X end ──
    chamfer_cavity = (
        cq.Workplane("YZ")
        .slot2D(COMP_MAJOR + 2 * ENTRY_CHAMFER, COMP_MINOR + 2 * ENTRY_CHAMFER)
        .extrude(DIE_LEN / 2, both=True)
    )
    for x_sign in [+1, -1]:
        x_pos = x_sign * (DIE_LEN / 2 - ENTRY_CHAMFER / 2)
        slab = (
            cq.Workplane("XY")
            .box(ENTRY_CHAMFER, OUTER_MAJOR + 1, OUTER_MINOR + 1,
                 centered=(True, True, True))
            .translate((x_pos, 0, 0))
        )
        chamfer_region = chamfer_cavity.intersect(slab)
        result = result.cut(chamfer_region)

    # ── Dowel pin holes on the parting face (Z=0) ──
    for y_sign in [+1, -1]:
        if is_bottom:
            pin = (
                cq.Workplane("XY")
                .transformed(offset=(0, y_sign * DOWEL_OFFSET_Y, 0))
                .circle(DOWEL_DIA / 2)
                .extrude(-DOWEL_DEPTH)
            )
        else:
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

female = make_half_stadium_channel(is_bottom=True)
male = make_half_stadium_channel(is_bottom=False)


# ═══════════════════════════════════════════════════════
# DIAGNOSTICS
# ═══════════════════════════════════════════════════════

for name, part in [("Female die (bottom)", female), ("Male die (top)", male)]:
    bb = part.val().BoundingBox()
    dx = bb.xmax - bb.xmin
    dy = bb.ymax - bb.ymin
    dz = bb.zmax - bb.zmin

    # Volume in cm³ → grams (PA6-CF density ~1.24 g/cm³)
    vol_mm3 = part.val().Volume()
    vol_cm3 = vol_mm3 / 1000.0
    mass_g = vol_cm3 * 1.24

    print(f"\n{name}:")
    print(f"  Bounding box: {dx:.1f} x {dy:.1f} x {dz:.1f} mm")
    print(f"               ({dx / IN:.3f} x {dy / IN:.3f} x {dz / IN:.3f} in)")
    print(f"  Volume: {vol_cm3:.1f} cm³")
    print(f"  Estimated mass (PA6-CF): {mass_g:.0f} g")
    print(f"  X range: [{bb.xmin:.1f}, {bb.xmax:.1f}]  (tube axis)")
    print(f"  Y range: [{bb.ymin:.1f}, {bb.ymax:.1f}]  (major axis)")
    print(f"  Z range: [{bb.zmin:.1f}, {bb.zmax:.1f}]  (minor axis / press)")


# ═══════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════

out_dir = Path(__file__).resolve().parent

female_path = out_dir / "forming-die-female.step"
cq.exporters.export(female, str(female_path))
print(f"\nExported: {female_path}")

male_path = out_dir / "forming-die-male.step"
cq.exporters.export(male, str(male_path))
print(f"Exported: {male_path}")

# ── Summary ──

print(f"\n--- Clamshell die dimensions (compensated for springback) ---")
print(f"Channel cross-section (racetrack): {COMP_MAJOR / IN:.3f}\" wide x {COMP_MINOR / IN:.3f}\" tall")
print(f"  Semicircle R:    {COMP_SEMI_R / IN:.3f}\"")
print(f"  Flat length:     {COMP_FLAT / IN:.3f}\"")
print(f"Die length (X):    {DIE_LEN / IN:.3f}\"  (tube lays along this axis)")
print(f"Trough depth:      {TROUGH_DEPTH / IN:.3f}\" (per half)")
print(f"Wall — semicircle: {SIDE_WALL / IN:.3f}\"  (bending loads)")
print(f"Wall — floor/ceil: {FLOOR_WALL / IN:.3f}\"  (compression only)")
