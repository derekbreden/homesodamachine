"""Generate the pump-case lower part STEP file.

The lower part sits below the main pump case skirt.  Both parts share
the identical split 76/62 footprint at their bottoms — that is the
mating interface.

  Top (Y=0):   solid 3mm cap, then uniform 62×62 shell
  Middle:      45° ramp — wider half expands from 62→76, narrow half stays 62
  Bottom:      split footprint 76 wide / 62 narrow (mates with main part)

Layout (top to bottom):
  11.5mm  uniform straight  (62×62)
   7.0mm  ramp at 45°       (wider half: 31→38 he, 7mm/side)
   4.5mm  footprint straight (76/62 split)
  ─────
  23.0mm  total
"""

from pathlib import Path
import math

import cadquery as cq

# ── Dimensions ──
CORNER_R = 6.0
WALL_THICKNESS = 3.0
TOTAL_HEIGHT = 23.0
ARC_SEGMENTS = 8
OVERCUT = 0.1
ARCH_RADIUS = 4.5

# The bottom footprint matches the main part's split skirt bottom.
# Wider half (+Z) is 76mm, narrower half (-Z) is 62mm.
FOOTPRINT_WIDE_HE = 38.0     # half of 76mm
FOOTPRINT_NARROW_HE = 31.0   # half of 62mm

# The uniform top profile matches the narrow half (both halves are 62mm)
UNIFORM_HE = FOOTPRINT_NARROW_HE  # 31

# Profile center — aligns with the main part's 70×70 footprint center
PROFILE_CENTER = 35.0

# ── Transition Z values ──
# Seam plane stays at X + Z = -UNIFORM_HE = -31
# Uniform profile: both halves at he=31, transition at ~0
uniform_tz_plus  =  0.01
uniform_tz_minus = -0.01

# Footprint profile: wide_he=38 → tz = 38-31 = 7;  narrow_he=31 → tz ≈ 0
footprint_tz_plus  = FOOTPRINT_WIDE_HE - UNIFORM_HE    # 7
footprint_tz_minus = 0.01                                # ~0 (avoid degenerate edge)

# ── Inner profile dimensions ──
seam_z_shift = WALL_THICKNESS * (math.sqrt(2) - 1)

INNER_CORNER_R = CORNER_R - WALL_THICKNESS              # 3

inner_uniform_he = UNIFORM_HE - WALL_THICKNESS           # 28
inner_footprint_wide_he = FOOTPRINT_WIDE_HE - WALL_THICKNESS   # 35
inner_footprint_narrow_he = FOOTPRINT_NARROW_HE - WALL_THICKNESS  # 28

# Inner transition Z (shifted for 3mm perpendicular wall thickness)
inner_uniform_tz_plus  =  0.01
inner_uniform_tz_minus = -0.01
inner_footprint_tz_plus  = footprint_tz_plus + seam_z_shift
inner_footprint_tz_minus = footprint_tz_minus + seam_z_shift

# ── Section heights ──
RAMP_HEIGHT = FOOTPRINT_WIDE_HE - UNIFORM_HE             # 7mm (45° = 1:1)
FOOTPRINT_STRAIGHT_HEIGHT = 4.5                           # matches main part
UNIFORM_STRAIGHT_HEIGHT = TOTAL_HEIGHT - RAMP_HEIGHT - FOOTPRINT_STRAIGHT_HEIGHT  # 11.5


def split_skirt_profile(wide_he, wide_r, narrow_he, narrow_r,
                        transition_z_plus=None, transition_z_minus=None,
                        n=ARC_SEGMENTS):
    """Asymmetric profile: wider rounded rect on +Z half, narrower on -Z half,
    with diagonal transitions on the left and right sides."""
    wide_r = max(wide_r, 0.01)
    narrow_r = max(narrow_r, 0.01)
    wide_cc = wide_he - wide_r
    narrow_cc = narrow_he - narrow_r

    if transition_z_plus is None:
        transition_z_plus = max((wide_he - narrow_he) / 2, 0.01)
    if transition_z_minus is None:
        transition_z_minus = -transition_z_plus

    pts = []

    # +Z half arcs (wide)
    for i in range(n):
        a = math.radians(90 * i / n)
        pts.append((wide_cc + wide_r * math.cos(a),
                     wide_cc + wide_r * math.sin(a)))
    for i in range(n):
        a = math.radians(90 + 90 * i / n)
        pts.append((-wide_cc + wide_r * math.cos(a),
                     wide_cc + wide_r * math.sin(a)))

    # Left transition
    pts.append((-wide_he, transition_z_plus))
    pts.append((-narrow_he, transition_z_minus))

    # -Z half arcs (narrow)
    for i in range(n):
        a = math.radians(180 + 90 * i / n)
        pts.append((-narrow_cc + narrow_r * math.cos(a),
                     -narrow_cc + narrow_r * math.sin(a)))
    for i in range(n):
        a = math.radians(270 + 90 * i / n)
        pts.append((narrow_cc + narrow_r * math.cos(a),
                     -narrow_cc + narrow_r * math.sin(a)))

    # Right transition
    pts.append((narrow_he, transition_z_minus))
    pts.append((wide_he, transition_z_plus))

    return pts


# ── Outer profiles at 4 Y-levels ──
outer_profiles = [
    # Level 0: Y=0, top — uniform 62×62
    split_skirt_profile(UNIFORM_HE, CORNER_R, UNIFORM_HE, CORNER_R,
                        uniform_tz_plus, uniform_tz_minus),
    # Level 1: end of uniform straight — still 62×62
    split_skirt_profile(UNIFORM_HE, CORNER_R, UNIFORM_HE, CORNER_R,
                        uniform_tz_plus, uniform_tz_minus),
    # Level 2: end of ramp — split 76/62 footprint
    split_skirt_profile(FOOTPRINT_WIDE_HE, CORNER_R,
                        FOOTPRINT_NARROW_HE, CORNER_R,
                        footprint_tz_plus, footprint_tz_minus),
    # Level 3: bottom — split 76/62 footprint
    split_skirt_profile(FOOTPRINT_WIDE_HE, CORNER_R,
                        FOOTPRINT_NARROW_HE, CORNER_R,
                        footprint_tz_plus, footprint_tz_minus),
]

# ── Inner profiles at 4 Y-levels ──
inner_profiles = [
    split_skirt_profile(inner_uniform_he, INNER_CORNER_R,
                        inner_uniform_he, INNER_CORNER_R,
                        inner_uniform_tz_plus, inner_uniform_tz_minus),
    split_skirt_profile(inner_uniform_he, INNER_CORNER_R,
                        inner_uniform_he, INNER_CORNER_R,
                        inner_uniform_tz_plus, inner_uniform_tz_minus),
    split_skirt_profile(inner_footprint_wide_he, INNER_CORNER_R,
                        inner_footprint_narrow_he, INNER_CORNER_R,
                        inner_footprint_tz_plus, inner_footprint_tz_minus),
    split_skirt_profile(inner_footprint_wide_he, INNER_CORNER_R,
                        inner_footprint_narrow_he, INNER_CORNER_R,
                        inner_footprint_tz_plus, inner_footprint_tz_minus),
]

# Incremental Y offsets between levels
y_steps = [UNIFORM_STRAIGHT_HEIGHT, RAMP_HEIGHT, FOOTPRINT_STRAIGHT_HEIGHT]

# ── Build outer loft ──
outer_solid = cq.Workplane("XZ").workplane(offset=0).center(PROFILE_CENTER, PROFILE_CENTER)
outer_solid = outer_solid.polyline(outer_profiles[0]).close()
for step, profile in zip(y_steps, outer_profiles[1:]):
    outer_solid = outer_solid.workplane(offset=step).polyline(profile).close()
outer_solid = outer_solid.loft(ruled=True)

# ── Build inner loft ──
inner_solid = cq.Workplane("XZ").workplane(offset=0).center(PROFILE_CENTER, PROFILE_CENTER)
inner_solid = inner_solid.polyline(inner_profiles[0]).close()
for i, (step, profile) in enumerate(zip(y_steps, inner_profiles[1:])):
    extra = OVERCUT if i == len(y_steps) - 1 else 0
    inner_solid = inner_solid.workplane(offset=step + extra).polyline(profile).close()
inner_solid = inner_solid.loft(ruled=True)

solid = outer_solid.cut(inner_solid)

# ── Cap: solid 3mm slab on top (Y=0 to Y=+3) ──
CAP_THICKNESS = 3.0
cap = (
    cq.Workplane("XZ").workplane(offset=0).center(PROFILE_CENTER, PROFILE_CENTER)
    .polyline(outer_profiles[0]).close()
    .extrude(CAP_THICKNESS)
)
solid = solid.union(cap)

# ── Arch notches at the bottom rim (+Z face of wider half) ──
z_face_outer = PROFILE_CENTER + FOOTPRINT_WIDE_HE   # 73
arch_hole_xs = [
    CORNER_R + ARCH_RADIUS - 4,                       # 6.5
    2 * PROFILE_CENTER - CORNER_R - ARCH_RADIUS + 4,  # 63.5
]

bottom_y = -TOTAL_HEIGHT  # Y=-23
for ax in arch_hole_xs:
    arch_cutter = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + OVERCUT)
        .center(ax, bottom_y)
        .circle(ARCH_RADIUS)
        .extrude(-(WALL_THICKNESS + 3 + OVERCUT))
    )
    solid = solid.cut(arch_cutter)

# ── Export ──
OUTPUT = Path(__file__).resolve().parent / "pump-case-lower-cadquery.step"
cq.exporters.export(solid, str(OUTPUT))
print(f"Exported → {OUTPUT}")
