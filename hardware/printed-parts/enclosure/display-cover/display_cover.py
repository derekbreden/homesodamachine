"""Display cover plate — the printed border that fills the display inset in the enclosure's
45° facet, laps the Waveshare 4.3B's glass on all four sides, and closes that face flat.

The inset, its sunk land, the bezel counterbore and the two heat-set bores are cut by
`enclosure._display_cuts`. This is the part that drops into them, and every figure here is off
those same names.

TWO SECTIONS, AND THE GLASS DECIDES WHICH. Over the glass the plate is
`display_cover_thickness` and cannot be anything else: what stands in the step there is the
display gasket, and under that the cover glass. Everywhere else — the whole lateral land the
inset reaches out to for the screws — it is `display_cover_seat`, a screw seat's own section,
and the land is sunk to meet it. So THERE IS NO PAD: what used to stand off the plate's back as
two circles is now the back itself, over all the ground the glass is not under, and the plate
is two and a half times its old section across the widest part of its span.

IT PRINTS FACE DOWN. The top face has to come out flat and lie in the 45° plane, and a face
printed against the bed is flat because the bed is. That orientation is also what makes the two
sections free: build upward from the top face and every step in the back is an UP-facing one —
the lap stops at its own depth and the seat carries on, with nothing hanging anywhere. What is
left over the bed is the annular ledge at each counterbore, `(cbore_dia - screw_clear_dia) / 2`
wide, which is a millimetre and a tenth.

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
from _materials import M_PETGF_BLACK, one_body
# The bound this file states about its own show face, recorded at import for the machine's card.
import _stated_bounds as _bounds
from docgen import substitute_md, substitute_py_comments
from _enclosure_interface import (
    display_bezel_depth,
    display_bezel_slope,
    display_bezel_x,
    display_corner_r,
    display_cover_cbore_depth,
    display_cover_seat,
    display_cover_seat_recess,
    display_cover_slip,
    display_cover_thickness,
    display_inset_depth,
    display_inset_lap,
    display_inset_slope,
    display_inset_x,
    display_screw_x,
    flute_depth,
    flute_full_depth_height,
    flute_reach,
    head_cbore_dia,
    heatset_depth,
    mount_bore_relief,
    screw_clear_dia,
)


# THE PLATE IS THE INSET, LESS THE SLIP IT DROPS IN ON. Corner radius comes off by the same
# slip, so the plate's round and the inset's stay concentric and the fit is the one figure all
# the way round the outline.
cover_x = display_inset_x - 2.0 * display_cover_slip          # [153.2 mm](COVER_X)
cover_slope = display_inset_slope - 2.0 * display_cover_slip  # [82.7 mm](COVER_SLOPE)
cover_corner_r = display_corner_r - display_cover_slip        # [2.35 mm](COVER_CORNER_R)

# The top face IS the 45° plane and the body hangs below it. The LAP is `display_cover_thickness`
# down, which is the inset's own depth; the SEAT is `display_cover_seat` down, and it is the
# plate's back everywhere the glass is not beneath it.
plate_z_top = 0.0
lap_z_bottom = plate_z_top - display_cover_thickness
seat_z_bottom = plate_z_top - display_cover_seat

# WHERE THE TWO MEET IS THE BEZEL'S OUTLINE, one slip out. Inside it the plate is over the glass
# and has to stay thin; outside it the plate is over the inset's land and may be anything. The
# deeper section's inner wall stands one `display_cover_slip` outside the bezel's own outline, so
# it drops past that counterbore's wall on the same figure the plate's edge takes at the outline.
seat_inner_x = display_bezel_x + 2.0 * display_cover_slip          # [113.8 mm](SEAT_INNER_X)
seat_inner_slope = display_bezel_slope + 2.0 * display_cover_slip  # [77.3 mm](SEAT_INNER_SLOPE)
seat_inner_corner_r = display_corner_r + display_cover_slip        # [2.65 mm](SEAT_INNER_R)

# THE WINDOW IS THE GLASS, LESS THE LAP. `display_inset_lap` is what the border stands over the
# glass on every side, so the opening is that lap taken off the glass twice over and the border
# is [5.85 mm](BORDER_SLOPE) up the slope. Laterally the inset reaches far past the glass for the
# two screws to stand in, so the same window leaves [22.85 mm](BORDER_X) of border either side.
# The opening's corners are the glass's own radius — the lap is constant round the corner only
# if the two outlines share it.
window_x = display_bezel_x - 2.0 * display_inset_lap          # [107.5 mm](WINDOW_X)
window_slope = display_bezel_slope - 2.0 * display_inset_lap  # [71 mm](WINDOW_SLOPE)
window_corner_r = display_corner_r
border_x = (cover_x - window_x) / 2.0
border_slope = (cover_slope - window_slope) / 2.0

# WHAT THE DEEPER SECTION IS WORTH, per side: the band of border it thickens. Laterally the inset
# reaches [19.7 mm](SEAT_BAND_X) past the glass for the screws to stand in, and all of it carries
# the seat; up the slope the land is only [2.7 mm](SEAT_BAND_SLOPE), because there the border is
# nearly all lap. What stays thin is the ring inside it — [3.15 mm](LAP_BAND) from the window out,
# which covers the gasket's own footprint and one slip more.
seat_band_x = (cover_x - seat_inner_x) / 2.0
seat_band_slope = (cover_slope - seat_inner_slope) / 2.0
lap_band = (seat_inner_x - window_x) / 2.0
# What the deeper section is worth in stiffness, which is the reason to want it: a plate's
# bending stiffness goes as the cube of its section, so this is [17.6×](SEAT_STIFFNESS) times.
seat_stiffness = (display_cover_seat / display_cover_thickness) ** 3

# THE PLATE IS A REVEAL IN THE FACET AND NOT A FLUTED FACE, and three separate things say so.
#
# ITS SHOW FACE LIES IN THE 45° PLANE. The box's field is struck along a plan and runs vertically
# (`enclosure.flute_rails`), so the facet carries no run at all — it is the material's own
# answer, along with the top rails and the pockets round the drop cutouts
# (`cadlib/flute_skin.py`). A plate let into that plane reads with the facet or against it.
#
# AND THE BAND IT DOES STAND ON IS SHORT. The plate's own edge is `display_cover_seat` on the
# run, well under the `flute_full_depth_height` it takes before one station stands `flute_rise`
# clear of both faces — the whole band would be ramp, and `flute_reach` says what would land
# there instead.
#
# AND TWO OF ITS FACES WOULD OWE THIS AT ANY HEIGHT. The border's underside over the glass is
# the display gasket's own land (`glass_face_depth`), and a groove across a sealing land is a
# path for what the gasket is there to keep out; the window it laps is the screen a customer
# reads through.
_bounds.state(
    "display-cover-reveal", "The display cover is a reveal in the facet, not a fluted face",
    f"under {flute_full_depth_height:g} mm on the run",
    flute_reach(display_cover_seat) < flute_depth,
    f"the plate stands {display_cover_seat:g} mm on the run, at or over the "
    f"{flute_full_depth_height:g} mm at which the field reaches its full {flute_depth:g} mm — "
    f"so a groove would land {flute_reach(display_cover_seat):.3f} mm here and the facet it "
    f"lies in still carries no run")

# THE LAP BEARS ON THE GLASS THROUGH THE GASKET. The plate's underside is one
# `display_inset_depth` below the 45° face and the glass's own front face is
# `display_bezel_depth` less its 1 mm of cover glass below it, so the border stands
# [1 mm](GLASS_LAP_SEAT) off the glass all the way round. `display_gasket`'s TPU ring is that
# step — its section IS this figure rather than a thickness chosen beside it — so what the
# two screws pull down on is the display, not the plate alone.
glass_face_depth = display_bezel_depth - 1.0
glass_lap_seat = glass_face_depth - display_inset_depth

# THE HEAD LANDS UNDER THE 45° FACE AND THE PLANE CLOSES OVER IT. Same flat-bottomed
# ⌀`head_cbore_dia` seat the foam cap's lids take, sunk `display_cover_seat_recess` under the
# face — [3.2 mm](COVER_CBORE_DEPTH) of the seat's [5.2 mm](COVER_SEAT), which leaves the land under
# the head at the lap's own [2 mm](COVER_LAND) section. That is what sets the seat: a screw seat is
# its counterbore and the lap under it, and the plate carries exactly that.
cbore_dia = head_cbore_dia
cbore_depth = display_cover_cbore_depth
land_under_head = display_cover_seat - cbore_depth             # [2 mm](COVER_LAND)
# The ledge the counterbore's floor leaves round the shank. Printed face down it is the one thing
# on the plate that hangs, and it hangs this far.
cbore_ledge = (cbore_dia - screw_clear_dia) / 2.0              # [1.125 mm](CBORE_LEDGE)

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


def _screw_bore(center_x) -> cq.Workplane:
    """One screw's whole passage through a pad: the shank clearance the length of the section,
    and over it the flat-bottomed head seat struck down from the TOP face. The head bears on the
    counterbore's floor, which is the land the pad exists to leave under it."""
    proud = 1.0  # struck past the top face so the seat breaks clean
    shank = (
        cq.Workplane("XY").workplane(offset=seat_z_bottom)
        .center(center_x, 0.0)
        .circle(screw_clear_dia / 2.0)
        .extrude(display_cover_seat)
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
    """The lap's own section over the whole outline, and under it the seat — the same outline
    with the bezel's taken out of it.

    A RING, NOT TWO PADS. The old part stood two ⌀12 circles off an otherwise flat back and had
    to rest on them; this stands the whole border down to the seat and keeps the plate thin only
    where the glass is under it."""
    lap = _rounded_prism(cover_x, cover_slope, cover_corner_r, lap_z_bottom, plate_z_top)
    seat = _rounded_prism(cover_x, cover_slope, cover_corner_r, seat_z_bottom, lap_z_bottom)
    well = _rounded_prism(seat_inner_x, seat_inner_slope, seat_inner_corner_r,
                          seat_z_bottom - 1.0, lap_z_bottom + 1.0)
    return lap.union(seat.cut(well))


def build_cover_inner_cut() -> cq.Workplane:
    """The window the screen shows through, and the two screw passages."""
    proud = 1.0  # struck past both faces so every cut breaks clean
    cut = _rounded_prism(window_x, window_slope, window_corner_r,
                         seat_z_bottom - proud, plate_z_top + proud)
    for sx in (-1.0, +1.0):
        cut = cut.union(_screw_bore(sx * display_screw_x))
    return cut


def build_display_cover() -> cq.Workplane:
    return build_cover_outer().cut(build_cover_inner_cut())


def glass_shadow() -> float:
    """How much plate stands below the lap's own underside inside the GLASS's outline.

    THIS IS THE ONE PLACE THE PLATE MAY NOT THICKEN. What is under it there is the gasket and
    then the cover glass, and a plate that reaches into that step is a plate bearing on glass.
    It has to be zero, and this measures the built solid rather than arguing from the figures."""
    probe = _rounded_prism(display_bezel_x, display_bezel_slope, display_corner_r,
                           seat_z_bottom - 1.0, lap_z_bottom - 1e-6).val()
    got = build_display_cover().val().intersect(probe)
    return got.Volume() if got is not None else 0.0


def bed_face() -> tuple:
    """What the plate lays on the bed, off the built solid: `(faces, area)`.

    It prints face down, so the bed takes the TOP face — one plane, the outline less the window
    and the two counterbores, and the face that has to come out flat and lie in the 45° plane."""
    body = build_display_cover().val()
    faces = [f for f in body.Faces()
             if abs(f.Center().z - plate_z_top) < 1e-6
             and abs(abs(f.normalAt().z) - 1.0) < 1e-6]
    return (len(faces), sum(f.Area() for f in faces))


def selftest() -> int:
    """The plate against the glass it may not touch, the screw against the seat that holds it,
    and the back against the bed it prints on."""
    fails = []
    shadow = glass_shadow()
    if shadow > 1e-6:
        fails.append(f"the plate stands {shadow:.3f} mm3 below its lap inside the glass's own "
                     f"outline, and what is in that step is the gasket")
    if abs(land_under_head - display_cover_thickness) > 1e-9:
        fails.append(f"the land under a head is {land_under_head:g} and the lap it should be "
                     f"the section of is {display_cover_thickness:g}")
    if abs((cbore_depth + land_under_head) - display_cover_seat) > 1e-9:
        fails.append(f"a {cbore_depth:g} counterbore over {land_under_head:g} of land is not the "
                     f"{display_cover_seat:g} seat the plate carries")
    if screw_len > screw_reach + 1e-9:
        fails.append(f"an M3x{screw_len:g} runs {screw_len:g} under its head and the station "
                     f"gives it {screw_reach:.2f}")
    if thread_engaged < heatset_depth - 1e-9:
        fails.append(f"the screw takes {thread_engaged:.2f} of a {heatset_depth:g} insert")
    for band, name in ((seat_band_x, "laterally"), (seat_band_slope, "up the slope")):
        if band <= 0.0:
            fails.append(f"the seat leaves no band {name} — the glass reaches the plate's edge")
    if seat_band_x < cbore_dia:
        fails.append(f"the seat's lateral band is {seat_band_x:.2f} and a head's counterbore is "
                     f"{cbore_dia:g} across — the seat cannot hold it")
    # THE BACK IS ONE PLANE EITHER SIDE OF THE STEP, and the bed takes the top face whole.
    faces, area = bed_face()
    if faces != 1:
        fails.append(f"the face on the bed is {faces} face(s) and the plate has one top")
    body = build_display_cover().val()
    low = body.BoundingBox().zmin
    if abs(low - seat_z_bottom) > 1e-6:
        fails.append(f"the plate reaches {low:.3f} and its seat is {seat_z_bottom:g} — something "
                     f"stands off the back")
    for f in fails:
        print(f"FAIL {f}")
    if not fails:
        print(f"ok  display-cover  {cover_x:g} x {cover_slope:g}, {display_cover_thickness:g} "
              f"over the glass and {display_cover_seat:g} on the land "
              f"({seat_band_x:.1f} of band each side), {area:.0f} mm2 on the bed, "
              f"0 mm3 in the gasket's step")
    return 1 if fails else 0


def main():
    cover = build_display_cover()

    out = _here.parent / "display-cover.step"
    export_assembly(one_body(cover, "display-cover", M_PETGF_BLACK), str(out))
    print(f"-> {out.name}")

    bb = cover.val().BoundingBox()
    faces, bed_area = bed_face()
    print("Display cover plate")
    print(f"  {cover_x:g} x {cover_slope:g} outer, r{cover_corner_r:g} corners, "
          f"{display_cover_thickness:g} over the glass and {display_cover_seat:g} on the land")
    print(f"  seat band {seat_band_x:g} laterally / {seat_band_slope:g} up the slope, "
          f"lap {lap_band:g} — {bed_area:.0f} mm2 of top face on the bed, printed face down")
    print(f"  {seat_stiffness:.1f}x the bending stiffness across the land, "
          f"{glass_shadow():.0f} mm3 standing in the gasket's step")
    print(f"  {window_x:g} x {window_slope:g} window, r{window_corner_r:g} corners — "
          f"{border_x:g} border laterally, {border_slope:g} up the slope")
    print(f"  {cbore_dia:g} flat counterbore {cbore_depth:g} deep over a "
          f"{screw_clear_dia:g} shank, {land_under_head:g} of land under the head; "
          f"M3x{screw_len:g} DIN 912 into a ruthex M3 short, {thread_engaged:g} engaged")
    print(f"  {glass_lap_seat:g} of air under the lap, glass face {glass_face_depth:g} below the "
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
        "COVER_SEAT": f"{display_cover_seat:.4g} mm",
        "SEAT_INNER_X": f"{seat_inner_x:.4g} mm",
        "SEAT_INNER_SLOPE": f"{seat_inner_slope:.4g} mm",
        "SEAT_INNER_R": f"{seat_inner_corner_r:.4g} mm",
        "SEAT_BAND_X": f"{seat_band_x:.4g} mm",
        "SEAT_BAND_SLOPE": f"{seat_band_slope:.4g} mm",
        "LAP_BAND": f"{lap_band:.4g} mm",
        "CBORE_LEDGE": f"{cbore_ledge:.4g} mm",
        "SEAT_STIFFNESS": f"{seat_stiffness:.1f}\u00d7",
        "BED_AREA": f"{bed_face()[1]:.0f} mm\u00b2",
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
        "GLASS_LAP_SEAT": f"{glass_lap_seat:.4g} mm",
    }

    substitute_md(_here.parent / "README.md", variables=variables)
    print("-> README.md")

    substitute_py_comments(Path(__file__), variables=variables)
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    main()
