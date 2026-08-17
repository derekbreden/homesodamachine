"""Display cover plate — the printed border that fills the display inset in the enclosure's
45° facet, laps the Waveshare 4.3B's glass on all four sides, and closes that face flat.

The inset, the bezel counterbore, the two pad pockets and the two heat-set bores are cut by
`enclosure._display_cuts`. This is the part that drops into them, and every figure here is off
those same names.

Frame: `enclosure.display_plane`'s own — +X the box's lateral axis, +Y up the 45° slope, +Z out
of the face at the user, origin on the glass's centre IN THE 45° PLANE. The plate's TOP face
lies on Z = 0 and the whole body hangs below it, so every Z here is a depth below that face and
reads against the depths the facet is cut to. `enclosure_assembly.build_display_cover` turns
this frame onto the facet and moves it by nothing else.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
from _cadq_export import export_assembly
from _materials import C_COVER, one_body
from docgen import substitute_md, substitute_py_comments
from enclosure import (
    display_bezel_depth,
    display_bezel_slope,
    display_bezel_x,
    display_corner_r,
    display_cover_cbore_depth,
    display_cover_seat_recess,
    display_cover_slip,
    display_cover_thickness,
    display_inset_depth,
    display_inset_lap,
    display_inset_slope,
    display_inset_x,
    display_screw_pad_depth,
    display_screw_pad_dia,
    display_screw_x,
    head_cbore_dia,
    heatset_depth,
    mount_bore_relief,
    screw_clear_dia,
)


# THE PLATE IS THE INSET, LESS THE SLIP IT DROPS IN ON. Corner radius comes off by the same
# slip, so the plate's round and the inset's stay concentric and the fit is the one figure all
# the way round the outline.
cover_x = display_inset_x - 2.0 * display_cover_slip          # [152.9 mm](COVER_X)
cover_slope = display_inset_slope - 2.0 * display_cover_slip  # [82.4 mm](COVER_SLOPE)
cover_corner_r = display_corner_r - display_cover_slip        # [2.2 mm](COVER_CORNER_R)

# The top face IS the 45° plane; the plate hangs `display_cover_thickness` below it, which is
# the inset's own depth, and each pad hangs `display_screw_pad_depth` below that.
plate_z_top = 0.0
plate_z_bottom = plate_z_top - display_cover_thickness
pad_z_bottom = plate_z_bottom - display_screw_pad_depth
# What the counterbore stands in — the plate's whole section under a screw, which is [5.2 mm](PAD_SEAT)
# where the bare border is [2 mm](COVER_T).
pad_seat_depth = display_cover_thickness + display_screw_pad_depth

# THE WINDOW IS THE GLASS, LESS THE LAP. `display_inset_lap` is what the border stands over the
# glass on every side, so the opening is that lap taken off the glass twice over and the border
# is [5.7 mm](BORDER_SLOPE) up the slope. Laterally the inset reaches far past the glass for the
# two screws to stand in, so the same window leaves [22.7 mm](BORDER_X) of border either side.
# The opening's corners are the glass's own radius — the lap is constant round the corner only
# if the two outlines share it.
window_x = display_bezel_x - 2.0 * display_inset_lap          # [107.5 mm](WINDOW_X)
window_slope = display_bezel_slope - 2.0 * display_inset_lap  # [71 mm](WINDOW_SLOPE)
window_corner_r = display_corner_r
border_x = (cover_x - window_x) / 2.0
border_slope = (cover_slope - window_slope) / 2.0

# THE LAP STANDS OVER THE GLASS AND NOT ON IT. The plate's underside is one `display_inset_depth`
# below the 45° face and the glass's own front face is `display_bezel_depth` less its 1 mm of
# cover glass below it, so [1 mm](GLASS_LAP_AIR) of air runs under the border all the way round.
glass_face_depth = display_bezel_depth - 1.0
glass_lap_air = glass_face_depth - display_inset_depth

# THE HEAD LANDS UNDER THE 45° FACE AND THE PLANE CLOSES OVER IT. Same flat-bottomed
# ⌀`head_cbore_dia` seat the foam cap's lids take, sunk `display_cover_seat_recess` under the
# face — [3.2 mm](COVER_CBORE_DEPTH) of the pad's [5.2 mm](PAD_SEAT), which leaves the land under the
# head at the bare border's own [2 mm](COVER_LAND) section.
cbore_dia = head_cbore_dia
cbore_depth = display_cover_cbore_depth
land_under_head = pad_seat_depth - cbore_depth                 # [2 mm](COVER_LAND)

# WHAT THE SCREW HAS TO STAND IN, under the head: the land, then the bore the box cuts past it —
# the ruthex M3 short's own thread and the relief under it, so a tip that runs past the insert
# finds air rather than a floor.
screw_reach = land_under_head + heatset_depth + mount_bore_relief   # [8.25 mm](COVER_SCREW_REACH)
# DIN 912 states a length UNDER the head, the head standing proud of it — so this is the M3×8
# the machine already buys, the longest stock length inside that reach.
screw_len = 8.0                                                # [8 mm](COVER_SCREW_LEN)
thread_engaged = min(screw_len - land_under_head, heatset_depth)  # [5.25 mm](THREAD_ENGAGED)


def _rounded_prism(x, slope, corner_r, z_bottom, z_top) -> cq.Workplane:
    """Rounded-corner rectangular prism on the frame's origin, over a Z range."""
    return (
        cq.Workplane("XY").workplane(offset=z_bottom)
        .rect(x, slope)
        .extrude(z_top - z_bottom)
        .edges("|Z").fillet(corner_r)
    )


def _screw_pad(center_x) -> cq.Workplane:
    """One pad, standing off the plate's underside into its pocket in the inset floor."""
    return (
        cq.Workplane("XY").workplane(offset=pad_z_bottom)
        .center(center_x, 0.0)
        .circle(display_screw_pad_dia / 2.0)
        .extrude(display_screw_pad_depth)
    )


def _screw_bore(center_x) -> cq.Workplane:
    """One screw's whole passage through a pad: the shank clearance the length of the section,
    and over it the flat-bottomed head seat struck down from the TOP face. The head bears on the
    counterbore's floor, which is the land the pad exists to leave under it."""
    proud = 1.0  # struck past the top face so the seat breaks clean
    shank = (
        cq.Workplane("XY").workplane(offset=pad_z_bottom)
        .center(center_x, 0.0)
        .circle(screw_clear_dia / 2.0)
        .extrude(pad_seat_depth)
        .val()
    )
    cbore = (
        cq.Workplane("XY").workplane(offset=plate_z_top - cbore_depth)
        .center(center_x, 0.0)
        .circle(cbore_dia / 2.0)
        .extrude(cbore_depth + proud)
        .val()
    )
    return cq.Workplane(obj=shank.fuse(cbore))


def build_cover_outer() -> cq.Workplane:
    """The border slab with a pad under each screw."""
    plate = _rounded_prism(cover_x, cover_slope, cover_corner_r, plate_z_bottom, plate_z_top)
    for sx in (-1.0, +1.0):
        plate = plate.union(_screw_pad(sx * display_screw_x))
    return plate


def build_cover_inner_cut() -> cq.Workplane:
    """The window the screen shows through, and the two screw passages."""
    proud = 1.0  # struck past both faces so every cut breaks clean
    cut = _rounded_prism(window_x, window_slope, window_corner_r,
                         pad_z_bottom - proud, plate_z_top + proud)
    for sx in (-1.0, +1.0):
        cut = cut.union(_screw_bore(sx * display_screw_x))
    return cut


def build_display_cover() -> cq.Workplane:
    return build_cover_outer().cut(build_cover_inner_cut())


def main():
    cover = build_display_cover()

    out = _here.parent / "display-cover.step"
    export_assembly(one_body(cover, "display-cover", C_COVER), str(out))
    print(f"-> {out.name}")

    bb = cover.val().BoundingBox()
    print("Display cover plate")
    print(f"  {cover_x:g} x {cover_slope:g} outer, r{cover_corner_r:g} corners, "
          f"{display_cover_thickness:g} thick, {pad_seat_depth:g} under each screw")
    print(f"  {window_x:g} x {window_slope:g} window, r{window_corner_r:g} corners — "
          f"{border_x:g} border laterally, {border_slope:g} up the slope")
    print(f"  {cbore_dia:g} flat counterbore {cbore_depth:g} deep over a "
          f"{screw_clear_dia:g} shank, {land_under_head:g} of land under the head; "
          f"M3x{screw_len:g} DIN 912 into a ruthex M3 short, {thread_engaged:g} engaged")
    print(f"  {glass_lap_air:g} of air under the lap, glass face {glass_face_depth:g} below the "
          f"45° plane and the plate's underside {display_inset_depth:g}")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")

    variables = {
        "COVER_X": f"{cover_x:.4g} mm",
        "COVER_SLOPE": f"{cover_slope:.4g} mm",
        "COVER_CORNER_R": f"{cover_corner_r:.4g} mm",
        "COVER_T": f"{display_cover_thickness:.4g} mm",
        "COVER_SLIP": f"{display_cover_slip:.4g} mm",
        "WINDOW_X": f"{window_x:.4g} mm",
        "WINDOW_SLOPE": f"{window_slope:.4g} mm",
        "WINDOW_CORNER_R": f"{window_corner_r:.4g} mm",
        "BORDER_X": f"{border_x:.4g} mm",
        "BORDER_SLOPE": f"{border_slope:.4g} mm",
        "INSET_LAP": f"{display_inset_lap:.4g} mm",
        "COVER_PAD_D": f"{display_screw_pad_dia:.4g} mm",
        "COVER_PAD_DEPTH": f"{display_screw_pad_depth:.4g} mm",
        "PAD_SEAT": f"{pad_seat_depth:.4g} mm",
        "PAD_X": f"{display_screw_x:.4g} mm",
        "SHANK_D": f"{screw_clear_dia:.4g} mm",
        "CBORE_D": f"{cbore_dia:.4g} mm",
        "COVER_CBORE_DEPTH": f"{cbore_depth:.4g} mm",
        "SEAT_RECESS": f"{display_cover_seat_recess:.4g} mm",
        "COVER_LAND": f"{land_under_head:.4g} mm",
        "COVER_SCREW_LEN": f"{screw_len:.4g} mm",
        "COVER_SCREW_REACH": f"{screw_reach:.4g} mm",
        "THREAD_ENGAGED": f"{thread_engaged:.4g} mm",
        "HEATSET_DEPTH": f"{heatset_depth:.4g} mm",
        "GLASS_FACE_DEPTH": f"{glass_face_depth:.4g} mm",
        "GLASS_LAP_AIR": f"{glass_lap_air:.4g} mm",
    }

    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")

    substitute_py_comments(Path(__file__), variables=variables)
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
