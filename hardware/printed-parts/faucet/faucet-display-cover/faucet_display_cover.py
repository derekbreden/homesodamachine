"""Faucet display cover plate — the printed face plate screwed down over
the faucet display, and the only thing holding it in.

THE CRADLE PARTS AT THE DEVICE'S OWN STEP. The shell stops at
`display_cover_land_n`, the step the device's board makes under its
housing; this plate is everything above it. So the seam a hand finds
around the cradle is a step the device already has, not a height chosen
for it, and the outside reads as one surface across the joint.

WHAT HOLDS IT. Two things: one M3 above the device's north edge,
threading a ruthex insert set into the shell, and the hook below. The
plate butts the shell's land the whole way round, so the screw pulls it
onto a hard stop and the device is captured with
`display_cover_over_face` of clearance rather than clamped through its
housing.

WHAT HOLDS THE SPOUT END. That screw is 50 mm up-gooseneck of it, so on
its own it leaves the bezel's grip on the device's bottom edge hanging
off a cantilever. So the plate grows a tongue there: a riser down the
notch in the shell's south wall and a toe reaching back under that
wall's overhanging top third. It goes in by sliding — the plate is set
down `display_cover_hook_travel` up-gooseneck of home, where the toe
clears the roof, and pushed toward the spout until the riser stops
against the roof's face. Then the screw, which is what keeps it there.

IT PRINTS FACE DOWN. The outer face lies on the bed and every step in
the body faces up from there. The hanging features are the annular
ledge at the counterbore and the toe's top face — the one that bears
up against the roof, which is flat because a ramp there would let the
hook cam out under the screw's own clearance.

Frame: the shell's own tip frame — s is distance up-gooseneck from the
tip end along the tip axis, n is distance from the water-tube centerline
along the tip's top normal, x is world X. `faucet_shell._cradle_prism`
builds in it, and `faucet_assembly` stands this plate on the faucet
without moving it."""

import math
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
sys.path.insert(0, str(_here.parent.parent))  # for _faucet_interface
sys.path.insert(0, str(_hw / "printed-parts" / "faucet" / "faucet-shell"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
from _faucet_interface import (
    display_corner_r,
    display_cover_wall,
    display_cover_cbore_depth,
    display_cover_lap,
    display_cover_over_face,
    display_cover_screw_len,
    display_housing_length,
    display_housing_width,
)
from docgen import substitute_md, substitute_py_comments
from faucet_shell import (
    _cradle_back_slope,
    display_cover_hook_lap,
    display_cover_hook_relief,
    display_floor_n,
    max_print_overhang_rad,
    _cradle_prism,
    _tip_frame,
    _housing_band_half_x,
    cradle_back_s,
    display_collar_half_x,
    display_cover_boss_wall,
    display_cover_cbore_dia,
    display_cover_hook_half_x,
    display_cover_hook_n0,
    display_cover_hook_n1,
    display_cover_hook_s0,
    display_cover_hook_s1,
    display_cover_hook_travel,
    display_cover_stem_s0,
    display_cover_insert_len,
    display_cover_land_n,
    display_cover_screw_s,
    display_cover_shank_dia,
    display_cover_slip,
    display_cover_top_n,
    display_cradle_clearance,
    display_face_n,
    display_s_bottom,
    display_s_top,
)


# OUTLINE — the collar's own plan, carried across the seam unchanged, and
# closed at the north by the cradle's back ramp.
plate_half_x = display_collar_half_x        # [14.36 mm](PLATE_HALF_X)
plate_s_north = cradle_back_s               # the ramp cuts back from here
plate_n_bottom = display_cover_land_n       # [17.2 mm](PLATE_N_BOTTOM) — the seam
plate_n_top = display_cover_top_n           # [24.21 mm](PLATE_N_TOP)
plate_thickness = plate_n_top - plate_n_bottom  # [7.01 mm](PLATE_THICKNESS)

# HOOK — the tongue off the plate's south end that goes under the south
# wall's overhanging top third. A riser down the shell's notch and a toe
# reaching back under the roof from it, one slip under that roof. The
# plate's own land is what sets its height; this face carries none of it.
hook_half_x = display_cover_hook_half_x   # [6.5 mm](HOOK_HALF_X)
hook_n_bottom = display_cover_hook_n0     # [13.67 mm](HOOK_N_BOTTOM)
hook_n_top = display_cover_hook_n1 - display_cover_slip  # [14.65](HOOK_N_TOP)

# SKIRT — inner faces on the cavity's own outline, so the plate comes
# down over the device's housing the way the shell came up its board.
skirt_half_x = _housing_band_half_x         # [12.5 mm](SKIRT_HALF_X)
skirt_corner_r = display_corner_r + display_cradle_clearance
bezel_n_bottom = display_face_n + display_cover_over_face  # [22.35 mm](BEZEL_N_BOTTOM)
bezel_thickness = plate_n_top - bezel_n_bottom             # [1.86 mm](BEZEL_THICKNESS)

# WINDOW — the bezel laps the device's face by display_cover_lap on every
# edge. The screen is 17.75 x 32.93 in a 24.5 x 44.5 housing, so the lap
# stops [1.375 mm](WINDOW_SIDE_MARGIN) short of the glass on the sides
# and [3.785 mm](WINDOW_END_MARGIN) short on the ends.
window_half_x = display_housing_width / 2.0 - display_cover_lap  # [10.25 mm](WINDOW_HALF_X)
window_s_south = display_s_bottom + display_cradle_clearance + display_cover_lap
window_s_north = display_s_top - display_cradle_clearance - display_cover_lap
window_corner_r = display_corner_r - display_cover_lap  # [3.75 mm](WINDOW_CORNER_R)
window_x = 2.0 * window_half_x                          # [20.5 mm](WINDOW_X)
window_s = window_s_north - window_s_south              # [40.5 mm](WINDOW_S)

# SCREW — the head sunk in a counterbore, the shank clear through, and
# the ruthex insert waiting in the shell below the land.
land_under_head = plate_thickness - display_cover_cbore_depth  # [3.81 mm](LAND_UNDER_HEAD)
thread_reach = display_cover_screw_len - land_under_head       # [4.19 mm](THREAD_REACH)
cbore_ledge = (display_cover_cbore_dia - display_cover_shank_dia) / 2.0  # [1.125 mm](CBORE_LEDGE)


def build_plate_outer() -> cq.Workplane:
    """Skirt and bezel over the seam, with the tongue and its hooks hung
    below on the two flanks, cut to the cradle's back ramp so the
    plate's north end continues the shell's slope instead of stepping
    off it."""
    body = _cradle_prism(
        plate_half_x, 0.0, plate_s_north,
        plate_n_bottom, plate_n_top,
    )
    toe = _cradle_prism(
        hook_half_x, display_cover_hook_s0, display_cover_hook_s1,
        hook_n_bottom, hook_n_top,
    )
    riser = _cradle_prism(
        hook_half_x, display_cover_stem_s0, display_cover_hook_s1,
        hook_n_bottom, plate_n_bottom,
    )
    return body.union(toe).union(riser).cut(_cradle_back_slope())


def build_plate_inner_cut() -> cq.Workplane:
    """The void the device stands in, the window over the glass, and the
    screw's two bores. The pocket starts display_cover_hook_travel south
    of the cavity's own south face: the plate is set down that far up-
    gooseneck of home, and the device has to be inside the pocket there
    as well as at home. The wall it gives up is wall the south wall's
    own thickness has more than replaced."""
    pocket = _cradle_prism(
        skirt_half_x, display_s_bottom - display_cover_hook_travel,
        display_s_top,
        hook_n_bottom - 1.0, bezel_n_bottom,
        corner_r=skirt_corner_r,
    )
    window = _cradle_prism(
        window_half_x, window_s_south, window_s_north,
        bezel_n_bottom - 1.0, plate_n_top + 1.0,
        corner_r=window_corner_r,
    )
    return pocket.union(window).union(_screw_bore())


def _screw_bore() -> cq.Workplane:
    """Shank clear through the plate, counterbore struck past the outer
    face so the head's seat breaks clean."""
    proud = 1.0
    tip_end, _, n_hat = _tip_frame()
    plane = cq.Plane(origin=tip_end, xDir=cq.Vector(1, 0, 0), normal=n_hat)

    def _bore(dia, n0, height):
        return (
            cq.Workplane(plane).workplane(offset=n0)
            .moveTo(0.0, display_cover_screw_s)
            .circle(dia / 2.0)
            .extrude(height)
        )

    shank = _bore(display_cover_shank_dia, plate_n_bottom - proud,
                  plate_thickness + 2.0 * proud)
    cbore = _bore(display_cover_cbore_dia, plate_n_top - display_cover_cbore_depth,
                  display_cover_cbore_depth + proud)
    return shank.union(cbore)


def build_display_cover() -> cq.Workplane:
    return build_plate_outer().cut(build_plate_inner_cut())


def bed_face(cover: cq.Workplane) -> tuple:
    """(count, area) of the faces lying in the plate's outer plane with
    the tip's own normal — what the plate stands on when it prints face
    down. One face, or the orientation is not what this file claims."""
    tip_end, _, n_hat = _tip_frame()
    on_plane = []
    for f in cover.val().Faces():
        c = f.Center()
        depth = (cq.Vector(c.x, c.y, c.z) - tip_end).dot(n_hat)
        if abs(depth - plate_n_top) < 1e-6 and abs(abs(f.normalAt(c).dot(n_hat)) - 1.0) < 1e-6:
            on_plane.append(f)
    return len(on_plane), sum(f.Area() for f in on_plane)


def selftest() -> int:
    cover = build_display_cover()
    fails = []
    if len(cover.val().Solids()) != 1:
        fails.append(f"the plate is {len(cover.val().Solids())} solids, not one")
    if thread_reach < display_cover_insert_len:
        fails.append(
            f"M3 x {display_cover_screw_len:g} reaches {thread_reach:.2f} past the plate,"
            f" short of the insert's {display_cover_insert_len:g}"
        )
    if window_corner_r <= 0.0:
        fails.append("the bezel's lap has eaten the window's corner radius")
    count, area = bed_face(cover)
    if count != 1:
        fails.append(f"{count} faces lie in the plate's outer plane, not one")
    for f in fails:
        print(f"FAIL {f}")
    if not fails:
        print(
            f"ok  faucet-display-cover  window {window_x:.4g} x {window_s:.4g},"
            f" bed face {area:.0f} mm\u00b2, M3 x {display_cover_screw_len:g}"
            f" biting {thread_reach:.2f}"
        )
    return 1 if fails else 0


def main():
    out_dir = _here.parent
    cover = build_display_cover()
    out = out_dir / "faucet-display-cover.step"
    export_assembly(one_body(cover, out.stem, C_FAUCET_BLACK), str(out))
    print(f"-> {out.name}")

    count, bed_area = bed_face(cover)
    print(f"  outer face {2.0 * plate_half_x:.4g} \u00d7 {plate_s_north:.4g} mm,"
          f" {plate_thickness:.4g} thick at the screw")
    print(f"  window {window_x:.4g} \u00d7 {window_s:.4g} mm, r{window_corner_r:.4g}")
    print(f"  bed face {bed_area:.0f} mm\u00b2 over {count} face(s)")
    print(f"  M3 \u00d7 {display_cover_screw_len:g} through {land_under_head:.4g} of land,"
          f" {thread_reach:.4g} into the insert")
    print(f"  volume {cover.val().Volume():.0f} mm\u00b3")

    variables = {
        "PLATE_HALF_X": f"{plate_half_x:.4g} mm",
        "PLATE_X": f"{2.0 * plate_half_x:.4g} mm",
        "PLATE_N_BOTTOM": f"{plate_n_bottom:.4g} mm",
        "PLATE_N_TOP": f"{plate_n_top:.4g} mm",
        "PLATE_THICKNESS": f"{plate_thickness:.4g} mm",
        "CRADLE_WALL_H": f"{display_cover_land_n - display_floor_n:.4g} mm",
        "FLOOR_N": f"{display_floor_n:.4g}",
        "HOOK_N0": f"{display_cover_hook_n0:.4g}",
        "HOOK_N1": f"{display_cover_hook_n1:.4g}",
        "HOOK_N_TOP": f"{hook_n_top:.4g}",
        "HOOK_RELIEF": f"{display_cover_hook_relief:.4g} mm",
        "HOOK_T": f"{hook_n_top - hook_n_bottom:.4g} mm",
        "HOOK_GAP": f"{display_cover_hook_n1 - hook_n_top:.4g} mm",
        "ROOF_T": f"{display_cover_land_n - display_cover_hook_n1:.4g} mm",
        "HOOK_LAP": f"{display_cover_hook_lap:.4g} mm",
        "HOOK_X": f"{2.0 * hook_half_x:.4g} mm",
        "HOOK_TRAVEL": f"{display_cover_hook_travel:.4g} mm",
        "S_BOTTOM": f"{display_s_bottom:.4g} mm",
        "COVER_WALL": f"{display_cover_wall:.4g} mm",
        "CHIN": f"{window_s_south:.4g} mm",
        "MAX_PRINT_OVERHANG": f"{math.degrees(max_print_overhang_rad):.0f}\u00b0",
        "SKIRT_HALF_X": f"{skirt_half_x:.4g} mm",
        "SKIRT_DEPTH": f"{bezel_n_bottom - plate_n_bottom:.4g} mm",
        "BEZEL_N_BOTTOM": f"{bezel_n_bottom:.4g} mm",
        "BEZEL_THICKNESS": f"{bezel_thickness:.4g} mm",
        "COVER_LAP": f"{display_cover_lap:.4g} mm",
        "COVER_OVER_FACE": f"{display_cover_over_face:.4g} mm",
        "WINDOW_X": f"{window_x:.4g} mm",
        "WINDOW_S": f"{window_s:.4g} mm",
        "WINDOW_CORNER_R": f"{window_corner_r:.4g} mm",
        "WINDOW_SIDE_MARGIN": f"{(window_x - 17.75) / 2.0:.4g} mm",
        "WINDOW_END_MARGIN": f"{(window_s - 32.93) / 2.0:.4g} mm",
        "SCREW_S": f"{display_cover_screw_s:.4g} mm",
        "SCREW_LEN": f"{display_cover_screw_len:g} mm",
        "CBORE_DIA": f"{display_cover_cbore_dia:.4g} mm",
        "CBORE_DEPTH": f"{display_cover_cbore_depth:.4g} mm",
        "SHANK_DIA": f"{display_cover_shank_dia:.4g} mm",
        "LAND_UNDER_HEAD": f"{land_under_head:.4g} mm",
        "THREAD_REACH": f"{thread_reach:.4g} mm",
        "CBORE_LEDGE": f"{cbore_ledge:.4g} mm",
        "BED_AREA": f"{bed_area:.0f} mm\u00b2",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")
    substitute_py_comments(Path(__file__), variables=variables)
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
