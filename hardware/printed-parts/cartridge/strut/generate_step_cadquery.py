from pathlib import Path

import cadquery as cq

STRUT_L = 150.0
oc = 0.1
OUT_DIR = Path(__file__).parent


def make_bar(size):
    half = size / 2
    return (cq.Workplane("XY")
        .transformed(offset=cq.Vector(-half, 0, -half))
        .box(size, STRUT_L, size, centered=False))


def cut_groove(solid, y0, length, zone_size, bar_size):
    """Cut all 4 faces to reduce cross-section from bar_size to zone_size."""
    if zone_size >= bar_size:
        return solid
    inset = (bar_size - zone_size) / 2
    half = bar_size / 2
    for x0, w in [(-half - oc, inset + oc), (half - inset, inset + oc)]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(x0, y0, -half - oc))
            .box(w, length, bar_size + 2 * oc, centered=False))
    for z0, h in [(-half - oc, inset + oc), (half - inset, inset + oc)]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(-half - oc, y0, z0))
            .box(bar_size + 2 * oc, length, h, centered=False))
    return solid


def cut_taper(solid, y_narrow, y_wide, narrow_size, wide_size):
    """Cut taper wedges on all 4 faces. wide_size should equal the bar size."""
    narrow_half = narrow_size / 2
    wide_half = wide_size / 2
    y_n_oc = y_narrow - oc if y_narrow < y_wide else y_narrow + oc
    # ±X faces (XY plane, extruded in Z)
    for sign in [-1, 1]:
        solid = solid.cut(
            cq.Workplane("XY")
            .transformed(offset=cq.Vector(0, 0, -wide_half - oc))
            .moveTo(sign * (wide_half + oc), y_n_oc)
            .lineTo(sign * narrow_half, y_n_oc)
            .lineTo(sign * (wide_half + oc), y_wide)
            .close()
            .extrude(wide_size + 2 * oc))
    # ±Z faces (YZ plane, extruded in X)
    for sign in [-1, 1]:
        solid = solid.cut(
            cq.Workplane("YZ")
            .transformed(offset=cq.Vector(0, 0, -wide_half - oc))
            .moveTo(y_n_oc, sign * (wide_half + oc))
            .lineTo(y_n_oc, sign * narrow_half)
            .lineTo(y_wide, sign * (wide_half + oc))
            .close()
            .extrude(wide_size + 2 * oc))
    return solid


def export(solid, name):
    path = OUT_DIR / f"{name}-cadquery.step"
    cq.exporters.export(solid, str(path))
    print(f"Exported {path}")


# --- Original: 2mm taper (5→6), grooves at 5.75 ---
# Y=0..2: taper 5→6 | Y=2..6: groove 5.75 | Y=6..143: body 6 |
# Y=143..148: groove 5.75 | Y=148..150: taper 6→5
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.75, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.75, 6.0)
s = cut_taper(s, 0, 2.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 148.0, 5.0, 6.0)
export(s, "strut")

# --- Short taper: 1mm taper (5→6), 1mm flat gap before groove ---
# Y=0..1: taper 5→6 | Y=1..2: flat 6 | Y=2..6: groove 5.75 | Y=6..143: body 6 |
# Y=143..148: groove 5.75 | Y=148..149: flat 6 | Y=149..150: taper 6→5
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.75, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.75, 6.0)
s = cut_taper(s, 0, 1.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.0)
export(s, "strut-short-taper")

# --- Oversize bump: 6.1 entry/retention bumps, 5.9 grooves, ramp to 6.0 body ---
# Y=0..1: taper 5→6.1 | Y=1..2: flat 6.1 | Y=2..6: groove 5.9 |
# Y=6..8: bump 6.1 | Y=8..10: ramp 6.1→6.0 | Y=10..139: body 6.0 |
# Y=139..141: ramp 6.0→6.1 | Y=141..143: bump 6.1 | Y=143..148: groove 5.9 |
# Y=148..149: flat 6.1 | Y=149..150: taper 6.1→5
s = make_bar(6.1)
s = cut_groove(s, 10.0, 129.0, 6.0, 6.1)
s = cut_groove(s, 2.0, 4.0, 5.9, 6.1)
s = cut_groove(s, 143.0, 5.0, 5.9, 6.1)
s = cut_taper(s, 0, 1.0, 5.0, 6.1)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.1)
s = cut_taper(s, 10.0, 8.0, 6.0, 6.1)
s = cut_taper(s, 139.0, 141.0, 6.0, 6.1)
export(s, "strut-oversize-bump")
