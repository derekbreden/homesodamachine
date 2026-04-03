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


# --- Split-tip: 0.6mm slot, 6.7 bumps, 5.6 grooves, 0.4mm groove clearance ---
BUMP = 6.7
GROOVE = 5.6
SLOT_W = 0.6
SLOT_DEPTH = 15.0
LEVER_GROOVE_L = 4.4    # 4mm plate + 0.4mm clearance
RELEASE_GROOVE_L = 5.4  # 5mm plate + 0.4mm clearance

# Y layout lever: 0..1 taper | 1..2 bump | 2..6.4 groove | 6.4..7.4 bump | 7.4.. body
# Y layout release: ..141.6 body | 141.6..142.6 bump | 142.6..148 groove | 148..149 bump | 149..150 taper
LEVER_GROOVE_END = 2.0 + LEVER_GROOVE_L        # 6.4
LEVER_BUMP_END = LEVER_GROOVE_END + 1.0         # 7.4
RELEASE_BUMP_START = STRUT_L - 1.0 - RELEASE_GROOVE_L - 1.0 - 1.0  # 141.6
RELEASE_GROOVE_START = RELEASE_BUMP_START + 1.0  # 142.6

s = make_bar(BUMP)
s = cut_groove(s, LEVER_BUMP_END, RELEASE_BUMP_START - LEVER_BUMP_END, 6.0, BUMP)
s = cut_groove(s, 2.0, LEVER_GROOVE_L, GROOVE, BUMP)
s = cut_groove(s, RELEASE_GROOVE_START, RELEASE_GROOVE_L, GROOVE, BUMP)
s = cut_taper(s, 0, 1.0, 5.0, BUMP)
s = cut_taper(s, 150.0, 149.0, 5.0, BUMP)

slot_half_x = SLOT_W / 2
z_cut = STRUT_Z / 2 + oc
for y_start, length in [(-oc, SLOT_DEPTH + oc), (STRUT_L - SLOT_DEPTH, SLOT_DEPTH + oc)]:
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-slot_half_x, y_start, -z_cut))
        .box(SLOT_W, length, 2 * z_cut, centered=False))

export(s, "strut")
