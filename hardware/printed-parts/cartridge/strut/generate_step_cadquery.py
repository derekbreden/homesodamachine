from pathlib import Path

import cadquery as cq

STRUT_L = 150.0
STRUT_Z = 6.0   # constant Z height (flat faces for printing, no features)
oc = 0.1
OUT_DIR = Path(__file__).parent

# Widths (X axis, Z is always STRUT_Z)
TIP_WIDTH = 5.0
BUMP_WIDTH = 6.7
BODY_WIDTH = 6.0

# Lengths (Y axis)
LEAD_IN_LENGTH = 1.0
BUMP_LENGTH = 1.0
LEVER_SEAT_LENGTH = 4.0    # matches lever plate thickness
RELEASE_SEAT_LENGTH = 5.0  # matches release plate thickness

# Slot
SLOT_WIDTH = 0.6
SLOT_DEPTH_ADD = 8.0  # extra slot depth beyond the body-side bump

# Lever end Y positions (from Y=0 inward)
LEVER_LEAD_IN_END = LEAD_IN_LENGTH                                  # 1.0
LEVER_TIP_BUMP_END = LEVER_LEAD_IN_END + BUMP_LENGTH                # 2.0
LEVER_SEAT_END = LEVER_TIP_BUMP_END + LEVER_SEAT_LENGTH             # 6.0
LEVER_BODY_BUMP_END = LEVER_SEAT_END + BUMP_LENGTH                  # 7.0

# Release end Y positions (from Y=150 inward)
RELEASE_LEAD_IN_START = STRUT_L - LEAD_IN_LENGTH                    # 149.0
RELEASE_TIP_BUMP_START = RELEASE_LEAD_IN_START - BUMP_LENGTH        # 148.0
RELEASE_SEAT_START = RELEASE_TIP_BUMP_START - RELEASE_SEAT_LENGTH   # 143.0
RELEASE_BODY_BUMP_START = RELEASE_SEAT_START - BUMP_LENGTH          # 142.0

BODY_LENGTH = RELEASE_BODY_BUMP_START - LEVER_BODY_BUMP_END         # 135.0


def make_bar(x_width):
    """Bar centered at XZ origin. Variable width in X, constant STRUT_Z in Z."""
    return (cq.Workplane("XY")
        .transformed(offset=cq.Vector(-x_width / 2, 0, -STRUT_Z / 2))
        .box(x_width, STRUT_L, STRUT_Z, centered=False))


def cut_groove(solid, y0, length, zone_width, bar_width):
    """Cut ±X faces only to reduce X width from bar_width to zone_width."""
    if zone_width >= bar_width:
        return solid
    inset = (bar_width - zone_width) / 2
    half_x = bar_width / 2
    half_z = STRUT_Z / 2
    for x0, w in [(-half_x - oc, inset + oc), (half_x - inset, inset + oc)]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x0, y0, -half_z - oc))
            .box(w, length, STRUT_Z + 2 * oc, centered=False))
    return solid


def cut_taper(solid, y_narrow, y_wide, narrow_width, wide_width):
    """Cut taper wedges on ±X faces only."""
    narrow_half = narrow_width / 2
    wide_half = wide_width / 2
    half_z = STRUT_Z / 2
    y_n_oc = y_narrow - oc if y_narrow < y_wide else y_narrow + oc
    for sign in [-1, 1]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -half_z - oc))
            .moveTo(sign * (wide_half + oc), y_n_oc)
            .lineTo(sign * narrow_half, y_n_oc)
            .lineTo(sign * (wide_half + oc), y_wide)
            .close()
            .extrude(STRUT_Z + 2 * oc))
    return solid


def export(solid, name):
    path = OUT_DIR / f"{name}-cadquery.step"
    cq.exporters.export(solid, str(path))
    print(f"Exported {path}")


# Build: start from BUMP_WIDTH bar, cut everything else down
s = make_bar(BUMP_WIDTH)

# Body
s = cut_groove(s, LEVER_BODY_BUMP_END, BODY_LENGTH, BODY_WIDTH, BUMP_WIDTH)

# Lever end: seat + lead-in
s = cut_groove(s, LEVER_TIP_BUMP_END, LEVER_SEAT_LENGTH, BODY_WIDTH, BUMP_WIDTH)
s = cut_taper(s, 0, LEVER_LEAD_IN_END, TIP_WIDTH, BUMP_WIDTH)

# Release end: seat + lead-in
s = cut_groove(s, RELEASE_SEAT_START, RELEASE_SEAT_LENGTH, BODY_WIDTH, BUMP_WIDTH)
s = cut_taper(s, STRUT_L, RELEASE_LEAD_IN_START, TIP_WIDTH, BUMP_WIDTH)

# Lever slot
lever_slot_depth = LEAD_IN_LENGTH + BUMP_LENGTH + LEVER_SEAT_LENGTH + BUMP_LENGTH + SLOT_DEPTH_ADD
slot_half_x = SLOT_WIDTH / 2
z_cut = STRUT_Z / 2 + oc
s = s.cut(cq.Workplane("XY")
    .transformed(offset=cq.Vector(-slot_half_x, -oc, -z_cut))
    .box(SLOT_WIDTH, lever_slot_depth + oc, 2 * z_cut, centered=False))

# Release slot
release_slot_depth = LEAD_IN_LENGTH + BUMP_LENGTH + RELEASE_SEAT_LENGTH + BUMP_LENGTH + SLOT_DEPTH_ADD
s = s.cut(cq.Workplane("XY")
    .transformed(offset=cq.Vector(-slot_half_x, STRUT_L - release_slot_depth, -z_cut))
    .box(SLOT_WIDTH, release_slot_depth + oc, 2 * z_cut, centered=False))

export(s, "strut")
