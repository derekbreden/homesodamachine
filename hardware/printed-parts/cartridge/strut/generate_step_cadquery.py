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


# --- Original: 2mm taper (5→6), grooves at 5.6 ---
# Y=0..2: taper 5→6 | Y=2..6: groove 5.6 | Y=6..143: body 6 |
# Y=143..148: groove 5.6 | Y=148..150: taper 6→5
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.6, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.6, 6.0)
s = cut_taper(s, 0, 2.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 148.0, 5.0, 6.0)
export(s, "strut")

# --- Short taper: 1mm taper (5→6), 1mm flat gap before groove ---
# Y=0..1: taper 5→6 | Y=1..2: flat 6 | Y=2..6: groove 5.6 | Y=6..143: body 6 |
# Y=143..148: groove 5.6 | Y=148..149: flat 6 | Y=149..150: taper 6→5
s = make_bar(6.0)
s = cut_groove(s, 2.0, 4.0, 5.6, 6.0)
s = cut_groove(s, 143.0, 5.0, 5.6, 6.0)
s = cut_taper(s, 0, 1.0, 5.0, 6.0)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.0)
export(s, "strut-short-taper")

# --- Oversize bump: 6.2 entry/retention bumps, 5.8 grooves, ramp to 6.0 body ---
# Y=0..1: taper 5→6.2 | Y=1..2: flat 6.2 | Y=2..6: groove 5.8 |
# Y=6..8: bump 6.2 | Y=8..10: ramp 6.2→6.0 | Y=10..139: body 6.0 |
# Y=139..141: ramp 6.0→6.2 | Y=141..143: bump 6.2 | Y=143..148: groove 5.8 |
# Y=148..149: flat 6.2 | Y=149..150: taper 6.2→5
s = make_bar(6.2)
s = cut_groove(s, 10.0, 129.0, 6.0, 6.2)
s = cut_groove(s, 2.0, 4.0, 5.8, 6.2)
s = cut_groove(s, 143.0, 5.0, 5.8, 6.2)
s = cut_taper(s, 0, 1.0, 5.0, 6.2)
s = cut_taper(s, 150.0, 149.0, 5.0, 6.2)
s = cut_taper(s, 10.0, 8.0, 6.0, 6.2)
s = cut_taper(s, 139.0, 141.0, 6.0, 6.2)
export(s, "strut-oversize-bump")

# --- Split-tip cantilever: + slot creates 4 flexible fingers, aggressive bumps ---
# Bumps on BOTH sides of groove act as barbs: tapered lead-in, 90° retention cliff.
# Very hard insertion, near-permanent once seated.
#
# Y=0..1: taper 5→6.5 | Y=1..2: bump 6.5 | Y=2..6: groove 5.6 |
# Y=6..7: bump 6.5 | Y=7..142: body 6.0 | Y=142..143: bump 6.5 |
# Y=143..148: groove 5.6 | Y=148..149: bump 6.5 | Y=149..150: taper 6.5→5
# + slot: 1mm wide, 15mm deep from each tip
BUMP = 6.5
SPLIT_GROOVE = 5.6
SLOT_W = 1.0
SLOT_DEPTH = 15.0

s = make_bar(BUMP)
s = cut_groove(s, 7.0, 135.0, 6.0, BUMP)           # body
s = cut_groove(s, 2.0, 4.0, SPLIT_GROOVE, BUMP)     # lever groove
s = cut_groove(s, 143.0, 5.0, SPLIT_GROOVE, BUMP)   # release groove
s = cut_taper(s, 0, 1.0, 5.0, BUMP)                 # lever taper
s = cut_taper(s, 150.0, 149.0, 5.0, BUMP)           # release taper

# + slots from each tip
slot_half = SLOT_W / 2
cross_half = BUMP / 2 + oc
for y_start, length in [(-oc, SLOT_DEPTH + oc), (STRUT_L - SLOT_DEPTH, SLOT_DEPTH + oc)]:
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-slot_half, y_start, -cross_half))
        .box(SLOT_W, length, 2 * cross_half, centered=False))
    s = s.cut(cq.Workplane("XY")
        .transformed(offset=cq.Vector(-cross_half, y_start, -slot_half))
        .box(2 * cross_half, length, SLOT_W, centered=False))

export(s, "strut-split-tip")
