from pathlib import Path

import cadquery as cq

STRUT_L = 150.0
STRUT_Z = 6.0   # constant Z height (flat faces for printing, no features)
oc = 0.1
OUT_DIR = Path(__file__).parent

# Base form
TIP_WIDTH = 5.0
BUMP_WIDTH = 7.0
BODY_WIDTH = 6.0
LEAD_IN_LENGTH = 2.0
BUMP_LENGTH = 2.0
LEVER_SEAT_LENGTH = 4.0    # matches lever plate thickness
RELEASE_SEAT_LENGTH = 5.0  # matches release plate thickness
SLOT_WIDTH = 1.0
SLOT_DEPTH_ADD = 8.0


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


def build_strut(name, bump_width=BUMP_WIDTH, slot_width=SLOT_WIDTH, slot_depth_add=SLOT_DEPTH_ADD):
    lever_lead_in_end = LEAD_IN_LENGTH
    lever_tip_bump_end = lever_lead_in_end + BUMP_LENGTH
    lever_seat_end = lever_tip_bump_end + LEVER_SEAT_LENGTH
    lever_body_bump_end = lever_seat_end + BUMP_LENGTH

    release_lead_in_start = STRUT_L - LEAD_IN_LENGTH
    release_tip_bump_start = release_lead_in_start - BUMP_LENGTH
    release_seat_start = release_tip_bump_start - RELEASE_SEAT_LENGTH
    release_body_bump_start = release_seat_start - BUMP_LENGTH

    body_length = release_body_bump_start - lever_body_bump_end

    s = make_bar(bump_width)

    # Body
    s = cut_groove(s, lever_body_bump_end, body_length, BODY_WIDTH, bump_width)

    # Lever end: seat + lead-in
    s = cut_groove(s, lever_tip_bump_end, LEVER_SEAT_LENGTH, BODY_WIDTH, bump_width)
    s = cut_taper(s, 0, lever_lead_in_end, TIP_WIDTH, bump_width)

    # Release end: seat + lead-in
    s = cut_groove(s, release_seat_start, RELEASE_SEAT_LENGTH, BODY_WIDTH, bump_width)
    s = cut_taper(s, STRUT_L, release_lead_in_start, TIP_WIDTH, bump_width)

    # Lever slot
    lever_slot_depth = LEAD_IN_LENGTH + BUMP_LENGTH + LEVER_SEAT_LENGTH + slot_depth_add
    slot_half_x = slot_width / 2
    z_cut = STRUT_Z / 2 + oc
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-slot_half_x, -oc, -z_cut))
        .box(slot_width, lever_slot_depth + oc, 2 * z_cut, centered=False))

    # Release slot
    release_slot_depth = LEAD_IN_LENGTH + BUMP_LENGTH + RELEASE_SEAT_LENGTH + slot_depth_add
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-slot_half_x, STRUT_L - release_slot_depth, -z_cut))
        .box(slot_width, release_slot_depth + oc, 2 * z_cut, centered=False))

    path = OUT_DIR / f"{name}-cadquery.step"
    cq.exporters.export(s, str(path))
    print(f"Exported {path}")


build_strut("strut")
build_strut("strut-a", bump_width=7.5)
build_strut("strut-b", bump_width=7.5, slot_width=1.4)
build_strut("strut-c", slot_depth_add=0)
build_strut("strut-d", slot_depth_add=5)
