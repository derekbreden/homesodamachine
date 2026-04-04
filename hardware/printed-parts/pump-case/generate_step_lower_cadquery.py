"""Generate the pump-case lower part STEP file.

The lower part sits below the main pump case skirt.  The mating surface
is stepped: the wide (+Z) half mates at the original level, the narrow
(-Z) half extends 19mm further into what was the main part's skirt.

  Cap end (Y=0):  solid 3mm cap, then uniform 62×62 shell
  Middle:         45° ramp — wider half expands from 62→76, narrow stays 62
  Wide mating:    split footprint 76/62 (wide half mates with main part here)
  Step extension: narrow (-Z) half continues 19mm, replicating main part skirt
  Narrow mating:  3mm cap at far end (narrow half mates with main part here)

Layout (cap end to narrow mating end):
  11.5mm  uniform straight  (62×62)
   7.0mm  ramp at 45°       (wider half: 31→38 he, 7mm/side)
   4.5mm  footprint straight (76/62 split)
  ── wide half ends here, narrow half continues ──
  19.0mm  step extension    (narrow half of main part's skirt)
  ─────
  42.0mm  total (narrow half)  /  23.0mm (wide half)
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
# Seam plane at X + Z = -PROFILE_CENTER = -35 (matches main part)
uniform_tz_plus  = -PROFILE_CENTER + UNIFORM_HE + 0.01   # -3.99 (near-degenerate)
uniform_tz_minus = -PROFILE_CENTER + UNIFORM_HE - 0.01   # -4.01

footprint_tz_plus  = -PROFILE_CENTER + FOOTPRINT_WIDE_HE    # 3
footprint_tz_minus = -PROFILE_CENTER + FOOTPRINT_NARROW_HE  # -4

# ── Inner profile dimensions ──
seam_z_shift = WALL_THICKNESS * (math.sqrt(2) - 1)

INNER_CORNER_R = CORNER_R - WALL_THICKNESS              # 3

inner_uniform_he = UNIFORM_HE - WALL_THICKNESS           # 28
inner_footprint_wide_he = FOOTPRINT_WIDE_HE - WALL_THICKNESS   # 35
inner_footprint_narrow_he = FOOTPRINT_NARROW_HE - WALL_THICKNESS  # 28

# Inner transition Z (shifted for 3mm perpendicular wall thickness)
inner_uniform_tz_plus  = uniform_tz_plus + seam_z_shift
inner_uniform_tz_minus = uniform_tz_minus + seam_z_shift
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

# ── Step extension: narrow (-Z) half of main part's skirt ──
# Extends 19mm past Y=-TOTAL_HEIGHT (the mating surface) to create a
# stepped mating surface.  The extension replicates the main part's
# narrow-half skirt geometry.  Dimensions must match generate_step_cadquery.py.
STEP_HEIGHT = 19.0

MAIN_BASE_HE = 35.0
MAIN_WIDE_FLARE = 3.0
MAIN_NARROW_TAPER = 4.0
MAIN_WIDE_HE = MAIN_BASE_HE + MAIN_WIDE_FLARE          # 38
MAIN_NARROW_HE = MAIN_BASE_HE - MAIN_NARROW_TAPER       # 31
MAIN_MID_NARROW_HE = MAIN_BASE_HE - MAIN_WIDE_FLARE     # 32

# Main part transition Z values (seam plane: X + Z = -35)
main_tz_sym = (0.01, -0.01)
main_tz_mid = (MAIN_WIDE_FLARE, -MAIN_WIDE_FLARE)        # (3, -3)
main_tz_end = (MAIN_WIDE_FLARE, -MAIN_NARROW_TAPER)      # (3, -4)

# Main part inner dimensions
main_inner_r = CORNER_R - WALL_THICKNESS                   # 3
main_inner_base_he = MAIN_BASE_HE - WALL_THICKNESS         # 32
main_inner_wide_he = MAIN_WIDE_HE - WALL_THICKNESS         # 35
main_inner_narrow_he = MAIN_NARROW_HE - WALL_THICKNESS     # 28
main_inner_mid_narrow_he = MAIN_MID_NARROW_HE - WALL_THICKNESS  # 29

main_seam_shift = WALL_THICKNESS * (math.sqrt(2) - 1)
main_itz_sym = (0.01, -0.01)
main_itz_mid = (main_tz_mid[0] + main_seam_shift, main_tz_mid[1] + main_seam_shift)
main_itz_end = (main_tz_end[0] + main_seam_shift, main_tz_end[1] + main_seam_shift)

# Main part's 5 skirt profiles (top to bottom: levels 0–4)
main_outer = [
    split_skirt_profile(MAIN_BASE_HE, CORNER_R, MAIN_BASE_HE, CORNER_R,
                        *main_tz_sym),
    split_skirt_profile(MAIN_BASE_HE, CORNER_R, MAIN_BASE_HE, CORNER_R,
                        *main_tz_sym),
    split_skirt_profile(MAIN_WIDE_HE, CORNER_R, MAIN_MID_NARROW_HE, CORNER_R,
                        *main_tz_mid),
    split_skirt_profile(MAIN_WIDE_HE, CORNER_R, MAIN_NARROW_HE, CORNER_R,
                        *main_tz_end),
    split_skirt_profile(MAIN_WIDE_HE, CORNER_R, MAIN_NARROW_HE, CORNER_R,
                        *main_tz_end),
]

main_inner = [
    split_skirt_profile(main_inner_base_he, main_inner_r,
                        main_inner_base_he, main_inner_r,
                        *main_itz_sym),
    split_skirt_profile(main_inner_base_he, main_inner_r,
                        main_inner_base_he, main_inner_r,
                        *main_itz_sym),
    split_skirt_profile(main_inner_wide_he, main_inner_r,
                        main_inner_mid_narrow_he, main_inner_r,
                        *main_itz_mid),
    split_skirt_profile(main_inner_wide_he, main_inner_r,
                        main_inner_narrow_he, main_inner_r,
                        *main_itz_end),
    split_skirt_profile(main_inner_wide_he, main_inner_r,
                        main_inner_narrow_he, main_inner_r,
                        *main_itz_end),
]


def narrow_half_polygon(full_profile, n=ARC_SEGMENTS):
    """Extract the narrow (-Z) half from a split_skirt_profile result."""
    return list(full_profile[2 * n: 4 * n + 4])


# Extension profiles: main part bottom→top (levels 4,3,2,1,0)
# maps to lower part Y=-23 → Y=-42
ext_outer_profiles = [narrow_half_polygon(main_outer[i]) for i in [4, 3, 2, 1, 0]]
ext_inner_profiles = [narrow_half_polygon(main_inner[i]) for i in [4, 3, 2, 1, 0]]

# Y steps from Y=-23 downward (main part steps in reverse order)
main_narrow_straight = FOOTPRINT_STRAIGHT_HEIGHT - (MAIN_NARROW_TAPER - MAIN_WIDE_FLARE)
ext_y_steps = [
    main_narrow_straight,                         # 3.5
    MAIN_NARROW_TAPER - MAIN_WIDE_FLARE,          # 1
    MAIN_WIDE_FLARE,                              # 3
    STEP_HEIGHT - main_narrow_straight             # 11.5
    - (MAIN_NARROW_TAPER - MAIN_WIDE_FLARE)
    - MAIN_WIDE_FLARE,
]

# Build extension outer loft (Y=-23 → Y=-42)
ext_outer_solid = (
    cq.Workplane("XZ")
    .workplane(offset=TOTAL_HEIGHT)
    .center(PROFILE_CENTER, PROFILE_CENTER)
)
ext_outer_solid = ext_outer_solid.polyline(ext_outer_profiles[0]).close()
for step, profile in zip(ext_y_steps, ext_outer_profiles[1:]):
    ext_outer_solid = ext_outer_solid.workplane(offset=step).polyline(profile).close()
ext_outer_solid = ext_outer_solid.loft(ruled=True)

# Build extension inner loft (Y=-23 → Y=-42, overcut at far end)
ext_inner_solid = (
    cq.Workplane("XZ")
    .workplane(offset=TOTAL_HEIGHT)
    .center(PROFILE_CENTER, PROFILE_CENTER)
)
ext_inner_solid = ext_inner_solid.polyline(ext_inner_profiles[0]).close()
for i, (step, profile) in enumerate(zip(ext_y_steps, ext_inner_profiles[1:])):
    extra = OVERCUT if i == len(ext_y_steps) - 1 else 0
    ext_inner_solid = ext_inner_solid.workplane(offset=step + extra).polyline(profile).close()
ext_inner_solid = ext_inner_solid.loft(ruled=True)

extension = ext_outer_solid.cut(ext_inner_solid)

# Cap at the far end of the extension (3mm solid slab ending at Y=-42)
ext_cap = (
    cq.Workplane("XZ")
    .workplane(offset=TOTAL_HEIGHT + STEP_HEIGHT - CAP_THICKNESS)
    .center(PROFILE_CENTER, PROFILE_CENTER)
    .polyline(ext_outer_profiles[-1]).close()
    .extrude(CAP_THICKNESS)
)
extension = extension.union(ext_cap)

solid = solid.union(extension)

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
