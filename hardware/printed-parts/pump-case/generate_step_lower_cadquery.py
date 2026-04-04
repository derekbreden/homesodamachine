"""Generate the pump-case lower part STEP file.

The lower part sits below the main pump case skirt.
  Top (Y=0):   uniform 62×62 rounded rect
  Middle:      45° ramp — wider half expands from 62→76, narrow half stays 62
  Bottom:      split profile 76 wide / 62 narrow

Layout (top to bottom):
  11.5mm  top straight   (62×62)
   7.0mm  ramp at 45°    (wider half: 31→38 he, 7mm/side)
   4.5mm  bottom straight (76/62 split)
  ─────
  23.0mm  total
"""

from pathlib import Path
import math

import cadquery as cq

# ── Dimensions ──
FOOTPRINT = 70.0
CORNER_R = 6.0
WALL = 3.0
WIDE_FLARE = 3.0         # per side: 70 → 76
NARROW_TAPER = 4.0        # per side: 70 → 62
HEIGHT = 23.0
ARC_SEGMENTS = 8
OVERCUT = 0.1
ARCH_RADIUS = 4.5

CENTER = FOOTPRINT / 2    # 35

# ── Profile dimensions ──

# Uniform 62×62 (top and top-of-ramp)
uni_he = FOOTPRINT / 2 - NARROW_TAPER                # 31
uni_r  = CORNER_R                                     # 6mm corner radius on all profiles

# Split 76/62 (bottom-of-ramp and bottom)
split_wide_he   = FOOTPRINT / 2 + WIDE_FLARE         # 38
split_wide_r    = CORNER_R                            # 6mm corner radius on all profiles
split_narrow_he = uni_he                              # 31
split_narrow_r  = CORNER_R                            # 6mm corner radius on all profiles

# Transition Z values — seam plane stays at X + Z = -uni_he = -31
# Uniform profile: both halves at he=31, transition at ~0
uni_tz_plus  =  0.01
uni_tz_minus = -0.01

# Split profile: wide_he=38 → tz_plus = 38 - 31 = 7;  narrow_he=31 → tz_minus = 0
split_tz_plus  = split_wide_he - uni_he               # 7
split_tz_minus = 0.01                                  # ~0 (avoid degenerate edge)

# ── Inner profile dimensions ──
seam_z_shift = WALL * (math.sqrt(2) - 1)

# Inner uniform
iuni_he = uni_he - WALL                               # 28
iuni_r  = uni_r - WALL                                 # 3

# Inner split
isplit_wide_he   = split_wide_he - WALL               # 35
isplit_wide_r    = split_wide_r - WALL                 # 3
isplit_narrow_he = split_narrow_he - WALL              # 28
isplit_narrow_r  = split_narrow_r - WALL               # 3

# Inner transition Z (shifted for 3mm perpendicular wall thickness)
iuni_tz_plus  =  0.01
iuni_tz_minus = -0.01
isplit_tz_plus  = split_tz_plus + seam_z_shift
isplit_tz_minus = split_tz_minus + seam_z_shift

# ── Section heights ──
RAMP_HEIGHT = split_wide_he - uni_he                  # 7mm (45° = 1:1)
BOTTOM_STRAIGHT = 4.5                                  # matches main part
TOP_STRAIGHT = HEIGHT - RAMP_HEIGHT - BOTTOM_STRAIGHT  # 11.5


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
    split_skirt_profile(uni_he, uni_r, uni_he, uni_r,
                        uni_tz_plus, uni_tz_minus),
    # Level 1: Y=-11.5, end of top straight — still 62×62
    split_skirt_profile(uni_he, uni_r, uni_he, uni_r,
                        uni_tz_plus, uni_tz_minus),
    # Level 2: Y=-18.5, end of ramp — split 76/62
    split_skirt_profile(split_wide_he, split_wide_r,
                        split_narrow_he, split_narrow_r,
                        split_tz_plus, split_tz_minus),
    # Level 3: Y=-23, bottom — split 76/62
    split_skirt_profile(split_wide_he, split_wide_r,
                        split_narrow_he, split_narrow_r,
                        split_tz_plus, split_tz_minus),
]

# ── Inner profiles at 4 Y-levels ──
inner_profiles = [
    split_skirt_profile(iuni_he, iuni_r, iuni_he, iuni_r,
                        iuni_tz_plus, iuni_tz_minus),
    split_skirt_profile(iuni_he, iuni_r, iuni_he, iuni_r,
                        iuni_tz_plus, iuni_tz_minus),
    split_skirt_profile(isplit_wide_he, isplit_wide_r,
                        isplit_narrow_he, isplit_narrow_r,
                        isplit_tz_plus, isplit_tz_minus),
    split_skirt_profile(isplit_wide_he, isplit_wide_r,
                        isplit_narrow_he, isplit_narrow_r,
                        isplit_tz_plus, isplit_tz_minus),
]

# Incremental Y offsets between levels
y_steps = [TOP_STRAIGHT, RAMP_HEIGHT, BOTTOM_STRAIGHT]

# ── Build outer loft ──
outer_solid = cq.Workplane("XZ").workplane(offset=0).center(CENTER, CENTER)
outer_solid = outer_solid.polyline(outer_profiles[0]).close()
for step, profile in zip(y_steps, outer_profiles[1:]):
    outer_solid = outer_solid.workplane(offset=step).polyline(profile).close()
outer_solid = outer_solid.loft(ruled=True)

# ── Build inner loft ──
inner_solid = cq.Workplane("XZ").workplane(offset=0).center(CENTER, CENTER)
inner_solid = inner_solid.polyline(inner_profiles[0]).close()
for i, (step, profile) in enumerate(zip(y_steps, inner_profiles[1:])):
    extra = OVERCUT if i == len(y_steps) - 1 else 0
    inner_solid = inner_solid.workplane(offset=step + extra).polyline(profile).close()
inner_solid = inner_solid.loft(ruled=True)

solid = outer_solid.cut(inner_solid)

# ── Cap: solid 3mm slab on top (Y=0 to Y=+3) ──
CAP_THICKNESS = 3.0
cap = (
    cq.Workplane("XZ").workplane(offset=0).center(CENTER, CENTER)
    .polyline(outer_profiles[0]).close()
    .extrude(CAP_THICKNESS)
)
solid = solid.union(cap)

# ── Arch notches at the bottom rim (+Z face of wider half) ──
z_face_outer = CENTER + split_wide_he   # 73
arch_hole_xs = [
    CORNER_R + ARCH_RADIUS - 4,                   # 6.5
    FOOTPRINT - CORNER_R - ARCH_RADIUS + 4,       # 63.5
]

bottom_y = -HEIGHT  # Y=-23
for ax in arch_hole_xs:
    arch_cutter = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + OVERCUT)
        .center(ax, bottom_y)
        .circle(ARCH_RADIUS)
        .extrude(-(WALL + 3 + OVERCUT))
    )
    solid = solid.cut(arch_cutter)

# ── Export ──
OUTPUT = Path(__file__).resolve().parent / "pump-case-lower-cadquery.step"
cq.exporters.export(solid, str(OUTPUT))
print(f"Exported → {OUTPUT}")
