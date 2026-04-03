from pathlib import Path

import cadquery as cq

STRUT_L = 150.0
STRUT_Z = 6.0   # constant Z height (flat faces for printing, no features)
oc = 0.1
OUT_DIR = Path(__file__).parent


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


# --- Original: 2mm taper (5→6), grooves at 5.6 ---
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.6, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.6, 6.0)
s = cut_taper(s, 0, 2.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 148.0, 5.0, 6.0)
export(s, "strut")

# --- Short taper: 1mm taper (5→6), 1mm flat, grooves at 5.6 ---
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.6, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.6, 6.0)
s = cut_taper(s, 0, 1.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.0)
export(s, "strut-short-taper")

# --- Oversize bump: 6.2 entry/bumps in X, 5.8 grooves, ramp to 6.0 body ---
s = make_bar(6.2)
s = cut_groove(s, 10.0, 129.0, 6.0, 6.2)
s = cut_groove(s, 2.0, 4.0, 5.8, 6.2)
s = cut_groove(s, 143.0, 5.0, 5.8, 6.2)
s = cut_taper(s, 0, 1.0, 5.0, 6.2)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.2)
s = cut_taper(s, 10.0, 8.0, 6.0, 6.2)
s = cut_taper(s, 139.0, 141.0, 6.0, 6.2)
export(s, "strut-oversize-bump")

# --- Split-tip cantilever: single slot creates 2 fingers flexing in X ---
# Bumps on both sides of groove, 90° retention cliffs.
BUMP = 6.5
SPLIT_GROOVE = 5.6
SLOT_W = 1.0
SLOT_DEPTH = 15.0

s = make_bar(BUMP)
s = cut_groove(s, 7.0, 135.0, 6.0, BUMP)
s = cut_groove(s, 2.0, 4.0, SPLIT_GROOVE, BUMP)
s = cut_groove(s, 143.0, 5.0, SPLIT_GROOVE, BUMP)
s = cut_taper(s, 0, 1.0, 5.0, BUMP)
s = cut_taper(s, 150.0, 149.0, 5.0, BUMP)

# Single slot along X center, full Z height — creates left/right fingers
slot_half_x = SLOT_W / 2
z_cut = STRUT_Z / 2 + oc
for y_start, length in [(-oc, SLOT_DEPTH + oc), (STRUT_L - SLOT_DEPTH, SLOT_DEPTH + oc)]:
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-slot_half_x, y_start, -z_cut))
        .box(SLOT_W, length, 2 * z_cut, centered=False))

export(s, "strut-split-tip")
