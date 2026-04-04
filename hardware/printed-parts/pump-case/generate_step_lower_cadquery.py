"""Generate the pump-case lower part STEP file.

The lower part mates to the bottom of the main pump case skirt.
At the top it matches the split skirt profile (wider half 76mm, narrower half 62mm).
It tapers linearly to a uniform 62×62 rounded rectangle at the bottom.
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

# ── Top profile (matches skirt bottom of full part) ──
top_wide_he     = FOOTPRINT / 2 + WIDE_FLARE         # 38
top_wide_r      = CORNER_R + WIDE_FLARE               # 9
top_narrow_he   = FOOTPRINT / 2 - NARROW_TAPER        # 31
top_narrow_r    = max(0, CORNER_R - NARROW_TAPER)      # 2
top_tz_plus     = WIDE_FLARE                           # +3
top_tz_minus    = -NARROW_TAPER                        # -4

# ── Bottom profile (uniform 62×62) ──
bot_he    = top_narrow_he                              # 31
bot_r     = top_narrow_r                               # 2
bot_tz_plus  =  0.01
bot_tz_minus = -0.01

# ── Inner profile dimensions ──
seam_z_shift = WALL * (math.sqrt(2) - 1)

itop_wide_he    = top_wide_he - WALL                   # 35
itop_wide_r     = top_wide_r - WALL                    # 6
itop_narrow_he  = top_narrow_he - WALL                 # 28
itop_narrow_r   = max(0, top_narrow_r - WALL)          # 0
itop_tz_plus    = top_tz_plus + seam_z_shift
itop_tz_minus   = top_tz_minus + seam_z_shift

ibot_he   = bot_he - WALL                             # 28
ibot_r    = max(0, bot_r - WALL)                       # 0
ibot_tz_plus  =  0.01
ibot_tz_minus = -0.01


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


# ── Build outer and inner lofts ──
# Y=0 is the top (mates with upper part), extends to Y=-23 at bottom.
# XZ workplane normal is -Y, so workplane offsets go in -Y.

top_outer = split_skirt_profile(top_wide_he, top_wide_r,
                                top_narrow_he, top_narrow_r,
                                top_tz_plus, top_tz_minus)
bot_outer = split_skirt_profile(bot_he, bot_r, bot_he, bot_r,
                                bot_tz_plus, bot_tz_minus)

top_inner = split_skirt_profile(itop_wide_he, itop_wide_r,
                                itop_narrow_he, itop_narrow_r,
                                itop_tz_plus, itop_tz_minus)
bot_inner = split_skirt_profile(ibot_he, ibot_r, ibot_he, ibot_r,
                                ibot_tz_plus, ibot_tz_minus)

outer_solid = (
    cq.Workplane("XZ").workplane(offset=0).center(CENTER, CENTER)
    .polyline(top_outer).close()
    .workplane(offset=HEIGHT)
    .polyline(bot_outer).close()
    .loft(ruled=True)
)

inner_solid = (
    cq.Workplane("XZ").workplane(offset=0).center(CENTER, CENTER)
    .polyline(top_inner).close()
    .workplane(offset=HEIGHT + OVERCUT)
    .polyline(bot_inner).close()
    .loft(ruled=True)
)

solid = outer_solid.cut(inner_solid)

# ── Arch notches at the mating edge (Y=0, +Z face of wider half) ──
z_face_outer = CENTER + top_wide_he   # 73
arch_hole_xs = [
    CORNER_R + ARCH_RADIUS - 4,                   # 6.5
    FOOTPRINT - CORNER_R - ARCH_RADIUS + 4,       # 63.5
]

for ax in arch_hole_xs:
    arch_cutter = (
        cq.Workplane("XY")
        .workplane(offset=z_face_outer + OVERCUT)
        .center(ax, 0)
        .circle(ARCH_RADIUS)
        .extrude(-(WALL + 3 + OVERCUT))
    )
    solid = solid.cut(arch_cutter)

# ── Export ──
OUTPUT = Path(__file__).resolve().parent / "pump-case-lower-cadquery.step"
cq.exporters.export(solid, str(OUTPUT))
print(f"Exported → {OUTPUT}")
