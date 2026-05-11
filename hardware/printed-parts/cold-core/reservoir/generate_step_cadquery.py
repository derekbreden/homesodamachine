import math
import sys
from pathlib import Path
import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step

# ═══════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
# Same coordinate convention as ../foam-bag-shell/: +Y vertical, +X is
# the bag-pocket axis (two cavities sit on opposite sides), +Z is
# perpendicular to it.
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))


def _wp_at(x, y, z):
    """A Workplane parallel to the xz plane at world point (x, y, z), normal
    +Y. Use this instead of ``cq.Workplane(xz_plane_y_up).workplane(origin=(x, y, z))``
    — the latter silently drops the Y component (which is along the
    plane's normal, not the in-plane direction), leaving every
    extrusion stuck at world Y=0."""
    return cq.Workplane(
        cq.Plane(origin=(x, y, z), xDir=(1, 0, 0), normal=(0, 1, 0))
    )
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cavity envelope (mirrors as-built foam-bag-shell inner-face values)
# -------------------------------------------------------
#
# These constants describe the bag-pocket cavity into which this
# reservoir fits. They mirror — but do not import from — the analogous
# constants in ../foam-bag-shell/generate_step_cadquery.py. The
# reservoir is a separate part with its own life cycle; treating the
# foam-bag-shell envelope as a stable interface keeps the two parts
# from leaking implementation details across each other.
#
# Bag-pocket inner faces (the surfaces the reservoir must clear):
#   - Far (away from tank): x = ±104.5 mm (sign flips with reservoir side)
#   - +Z / −Z side: z = ±70.5 mm
#   - Floor top: y = 1.0 mm
#   - Top of bag-pocket walls: y = 212.4 mm
#   - Centerward (toward tank): cylindrical surface, radius 71.5 mm,
#     vertical axis on +Y through origin — this is the tank_copper_shell
#     outer surface, which the reservoir's centerward face follows.
#
bag_pocket_far_inner_x = 104.5
bag_pocket_z_inner_max = 70.5
bag_pocket_floor_top_y = 1.0
bag_pocket_walls_top_y = 212.4
tank_copper_shell_outer_radius = 71.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Reservoir geometry
# -------------------------------------------------------
#
# The body is an OPEN-TOP `[` cup: floor + four walls (far, +Z, −Z,
# centerward concave-curve) of uniform 4 mm PETG. The top is closed by
# a separately-printed cap clamped down through a TPU gasket with six
# M3 screws into heat-set inserts.
#
# All six surfaces of the assembled stack (floor + 4 walls + cap) are
# 4 mm thick where the body provides them; the cap adds another base
# plate + perimeter wall on top. FDM can't reliably bridge a 140 × 90 mm
# horizontal span at 4 mm thickness with no internal supports — hence
# the open-top + separate-cap split.
#
reservoir_wall_thickness = 4.0
#
# Clearance between reservoir outer surfaces and bag-pocket inner
# faces on every face. Slack for sliding the printed reservoir into
# the cavity from above + FDM tolerance on both prints.
reservoir_clearance = 0.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Sharp-corner fillets (where the centerward curve meets the ±Z walls)
# -------------------------------------------------------
#
# At z = ±70 mm the outer centerward curve (radius 72 mm) meets the
# outer ±Z walls. Interior angle of the body's exterior at that point
# is only ~13° — a pointy tab that's structurally useless, won't FDM
# cleanly, and looks like a defect. Filleted off externally.
#
# At z = ±66 mm the inner centerward curve (radius 76 mm) meets the
# inner ±Z walls (cavity boundary). Interior angle of the cavity at
# that point is ~30° — a sharp corner inside the syrup volume that
# would trap residual liquid through clean cycles and concentrate
# stress in the wall. Filleted off internally.
#
# Same fillet radius on both for visual consistency. 5 mm is large
# relative to the wall thickness but small relative to the wall arc
# lengths (~140 mm far wall, ~190 mm centerward curve).
#
outer_corner_fillet_radius = 5.0
inner_corner_fillet_radius = 5.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cap geometry
# -------------------------------------------------------
#
# Base plate (top, the flat surface) + perimeter wall (bottom, the
# "lip" hanging down around the gasket joint). The base plate hosts
# the counterbored screw heads on its flat top face; the perimeter
# wall provides depth for the screw shaft to pass through to the
# gasket + body insert below.
#
cap_base_thickness = 3.0
cap_wall_height = 5.0
cap_wall_width = 6.0
#
# Screw recess geometry. M3 SHCS head OD ~5.5 mm; ø6 counterbore is
# the standard fit. Counterbore depth 3 mm = cap_base_thickness, so
# the counterbore recesses the screw head through the full base
# plate; the remaining 5 mm of clearance hole through the perimeter
# wall carries the shaft to the gasket + body insert below.
cap_counterbore_diameter = 6.0
cap_counterbore_depth = 3.0
cap_clearance_hole_diameter = 3.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Heat-set insert + screw spec
# -------------------------------------------------------
#
# M3 ruthex-style brass heat-set inserts (same as foam-bag-shell cap-
# stack joinery). Insert OD 4 mm × length 4 mm; pocket is 4 mm bore
# × 7 mm deep (4 mm insert + 3 mm relief). Screws: BNUOK M3 × 12 mm
# DIN 912 SHCS, black oxide 12.9 alloy (Amazon B0DJQGVK8S), same
# brand/finish as the M3 × 25 used on the foam-bag-shell cap stack
# but the right length for the reservoir's thinner cap-stack geometry
# (under-head stack is 7 mm cap-plus-gasket vs ~19 mm there). With
# M3 × 12, the shaft seats 4 mm into the insert, runs another 1 mm
# into the pocket relief, and leaves 2 mm of slack between the shaft
# tip and the pocket floor.
#
insert_pocket_radius = 2.0
insert_pocket_depth = 7.0
#
# Boss radii — chosen so each hole has a 2 mm PETG annulus around it:
#   Body pocket ø4 + 2 mm PETG → body boss ø8 (radius 4)
#   Cap counterbore ø6 + 2 mm PETG → cap boss ø10 (radius 5)
#
body_boss_radius = insert_pocket_radius + 2.0                          # 4
cap_boss_radius = cap_counterbore_diameter / 2.0 + 2.0                 # 5
#
# Body boss vertical layout (extruding downward from the wall top):
#   top 7 mm:  pocket (ø4 hole for heat-set insert + screw shaft)
#   below:     solid ø8 cylinder. Built extra-long (extending below
#              the intended boss-bottom y) and then cut with a flat
#              45° plane through the wall at that boss-bottom y, so
#              the wall side of the cylinder stays straight (and gets
#              fused into the wall) and the cavity side of the
#              cylinder gets sliced off at 45° — an FDM-printable
#              overhang anchored on the wall.
#
# Bosses 1/2/3/6 sit 1 mm inside the cavity from the wall's inner
# face (so the cap counterbore keeps a strict 2 mm of PETG to the
# outer face). The 45° cut starts at the wall inner face / corner
# at y = boss_bottom_y, NOT at the boss center, so the kept material
# on the wall side reaches all the way down to that y. Bosses 4/5
# (curve × ±Z corner, at outer-fillet center) sit inside the post-
# fillet wall material and don't get a cut — the body-boss loop
# skips them.
boss_height = 13.0                                                     # 7 mm pocket + 6 mm of solid+cut
_cyl_extra_below_bottom = 5.0                                          # extra cylinder length to be sliced off by the cut
#
# Insert / screw positions, derived from the wall geometry so the cap
# counterbore at each position has 2 mm of PETG to the nearest outer
# face of the cap base plate.
#
# Outer envelope (body and cap share this footprint):
_outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance        # 104
_outer_z_max = bag_pocket_z_inner_max - reservoir_clearance            # 70
_outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance  # 72
#
# 5 mm = counterbore radius (3) + PETG margin (2) — the inset from
# every outer face the counterbore center must keep.
_screw_setback = cap_counterbore_diameter / 2.0 + 2.0                  # 5
#
# Positions 1/2 — inset 5 mm from outer +X face × outer ±Z face.
_corner_xz_x = _outer_far_x_abs - _screw_setback                       # 99
_corner_xz_z = _outer_z_max - _screw_setback                           # 65
#
# Position 3 — inset 5 mm from outer +X face, z = 0.
_far_mid_x = _outer_far_x_abs - _screw_setback                         # 99
#
# Position 6 — 5 mm outward from outer curve (radially), z = 0.
_curve_apex_x = _outer_centerward_radius + _screw_setback              # 77
#
# Positions 4/5 — corner of outer curve × outer ±Z face. The corner
# is filleted at outer_corner_fillet_radius (= 5 mm). The fillet
# center is the unique point that is 5 mm from BOTH the outer +Z
# face and the outer curve, measured along the shortest path; the
# counterbore at this point has exactly 2 mm of PETG to the outer
# curve and 2 mm to the +Z face. The ø8 body boss disk fits entirely
# inside the fillet arc (radius 5), so at these positions the boss
# is a no-op subset of the post-fillet wall material — no cavity
# bump, no chamfer needed (the body-boss loop below skips the chamfer
# for these two positions explicitly, for code-reading clarity).
_corner_curve_z = _outer_z_max - outer_corner_fillet_radius             # 65
_corner_curve_R = _outer_centerward_radius + outer_corner_fillet_radius  # 77
_corner_curve_x = math.sqrt(_corner_curve_R**2 - _corner_curve_z**2)    # ~41.28
#
# (for the side=+1 reservoir; sign flips for −1)
INSERT_POSITIONS_FOR_SIDE_PLUS_1 = [
    (_corner_xz_x, _corner_xz_z),         # 1: +X × +Z outer corner
    (_corner_xz_x, -_corner_xz_z),        # 2: +X × −Z outer corner
    (_far_mid_x, 0.0),                    # 3: +X face midpoint
    (_corner_curve_x, _corner_curve_z),   # 4: curve × +Z outer corner (at outer fillet center)
    (_corner_curve_x, -_corner_curve_z),  # 5: curve × −Z outer corner (at outer fillet center)
    (_curve_apex_x, 0.0),                 # 6: curve apex
]
#
# For each body boss that needs the 45° flat cut at its bottom (i.e.,
# the four bosses whose disks extend into the cavity, not the two
# curve-corner bosses which sit inside the post-fillet wall), record
# the wall pivot point (the (x, z) on the wall's inner face from which
# the cut plane originates) and the unit direction in XZ from the boss
# center toward that pivot. The cut plane passes through (pivot_x,
# boss_bottom_y, pivot_z) and is tilted at 45° from horizontal, rising
# away from the wall — keep above, cut below.
#
# Values stored for side=+1; the x component is multiplied by `side`
# in the body-boss loop to mirror across x=0 for side=−1.
_FAR_WALL_INNER_X = _outer_far_x_abs - reservoir_wall_thickness        # 100
_PLUS_Z_WALL_INNER_Z = _outer_z_max - reservoir_wall_thickness         # 66
_CURVE_INNER_X_AT_Z0 = _outer_centerward_radius + reservoir_wall_thickness  # 76
_INV_SQRT2 = 1.0 / math.sqrt(2.0)
BODY_BOSS_CUT_INFO_FOR_SIDE_PLUS_1 = {
    # (boss_x, boss_z) → (pivot_x, pivot_z, wall_dir_x, wall_dir_z)
    #   wall_dir is a UNIT vector in XZ pointing from the boss center toward the wall pivot
    (_corner_xz_x, _corner_xz_z):
        (_FAR_WALL_INNER_X, _PLUS_Z_WALL_INNER_Z, _INV_SQRT2, _INV_SQRT2),    # 1
    (_corner_xz_x, -_corner_xz_z):
        (_FAR_WALL_INNER_X, -_PLUS_Z_WALL_INNER_Z, _INV_SQRT2, -_INV_SQRT2),  # 2
    (_far_mid_x, 0.0):
        (_FAR_WALL_INNER_X, 0.0, 1.0, 0.0),                                   # 3
    (_curve_apex_x, 0.0):
        (_CURVE_INNER_X_AT_Z0, 0.0, -1.0, 0.0),                               # 6
    # 4 and 5 deliberately absent — those bosses sit inside the
    # post-fillet wall material, no cavity overhang to slice.
}
#
# -------------------------------------------------------


# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


def _build_outer_envelope(side, outer_far_x_abs, outer_z_max, outer_centerward_radius, floor_y, height):
    """`[`-shape solid: rectangle on three sides + concave cylindrical
    cutout on the centerward side. Used for both reservoir-body and
    cap footprints."""
    rect = (
        _wp_at(side * outer_far_x_abs / 2, floor_y, 0)
        .rect(outer_far_x_abs, 2 * outer_z_max)
        .extrude(height)
    )
    cyl = (
        _wp_at(0, floor_y, 0)
        .circle(outer_centerward_radius)
        .extrude(height)
    )
    return rect.cut(cyl)


def build_reservoir_body(side=1):
    """
    Open-top `[`-shaped PETG body with 4 mm walls + 4 mm floor, sized
    to fit one side of the bag-pocket cavity with `reservoir_clearance`
    mm of slack on every outer face.

    Six insert bosses (one per `INSERT_POSITIONS_FOR_SIDE_PLUS_1`) are
    unioned at the top of the perimeter, each with an ø4 × 5 mm-deep
    heat-set-insert pocket drilled into the top face. The bosses
    locally thicken the wall to ø8 mm wide so the insert has 2 mm of
    PETG around it on all sides.

    side=+1 builds the +X reservoir; side=−1 builds the −X (mirrored
    across x = 0).
    """
    # Outer envelope dimensions.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_floor_bottom_y = bag_pocket_floor_top_y + reservoir_clearance
    outer_top_y = bag_pocket_walls_top_y - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance
    outer_height = outer_top_y - outer_floor_bottom_y

    # Inner cavity dimensions. No ceiling — cavity extends all the way
    # to outer_top_y; the cap closes the top with a gasket between.
    W = reservoir_wall_thickness
    inner_far_x_abs = outer_far_x_abs - W
    inner_z_max = outer_z_max - W
    inner_floor_top_y = outer_floor_bottom_y + W
    inner_top_y = outer_top_y  # <- no ceiling
    inner_centerward_radius = outer_centerward_radius + W
    inner_height = inner_top_y - inner_floor_top_y

    outer_envelope = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        outer_floor_bottom_y, outer_height,
    )
    inner_cavity = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        inner_floor_top_y, inner_height,
    )

    body = outer_envelope.cut(inner_cavity)

    # Fillet the four sharp corners where the centerward concave curve
    # meets the ±Z walls — applied to the bare wall geometry BEFORE
    # unioning the insert bosses, because two of the inner corners
    # coincide with boss positions (37.68, ±66) and unioning a cylinder
    # there would replace the sharp edge with a curved boss-to-wall
    # transition that the fillet operation can't pick up.
    #
    # Exterior corners (outer perimeter, ~13° interior angle) are pointy
    # tabs. Interior corners (cavity boundary, ~30° interior angle) are
    # sharp inside the syrup volume. Both get rounded with the same
    # radius for visual consistency.
    outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_z_max**2)
    inner_corner_x = math.sqrt(inner_centerward_radius**2 - inner_z_max**2)
    y_mid_body = (outer_floor_bottom_y + outer_top_y) / 2

    for sharp_z in (outer_z_max, -outer_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_body, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    for sharp_z in (inner_z_max, -inner_z_max):
        body = (
            body
            .edges(cq.NearestToPointSelector(
                (side * inner_corner_x, y_mid_body, sharp_z),
            ))
            .fillet(inner_corner_fillet_radius)
        )

    # Insert bosses at the top perimeter (unioned AFTER the fillets so
    # the bosses sit on top of the now-rounded corners cleanly).
    boss_bottom_y = outer_top_y - boss_height
    pocket_bottom_y = outer_top_y - insert_pocket_depth

    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        cut_info = BODY_BOSS_CUT_INFO_FOR_SIDE_PLUS_1.get((px, pz))

        # Build the boss cylinder. If this boss needs a 45° cut,
        # extend the cylinder _cyl_extra_below_bottom past the
        # intended boss bottom so the cut has material to slice
        # off; otherwise build it straight from the intended bottom.
        if cut_info is None:
            cyl_bottom_y = boss_bottom_y
        else:
            cyl_bottom_y = boss_bottom_y - _cyl_extra_below_bottom
        boss = (
            _wp_at(px_signed, cyl_bottom_y, pz)
            .circle(body_boss_radius)
            .extrude(outer_top_y - cyl_bottom_y)
        )

        if cut_info is not None:
            pivot_x, pivot_z, dir_x, dir_z = cut_info
            pivot_x_signed = pivot_x * side
            dir_x_signed = dir_x * side
            # Cut plane: passes through (pivot_x_signed, boss_bottom_y, pivot_z),
            # tilted 45° from horizontal with the high side toward the
            # wall (along (dir_x_signed, dir_z) in XZ). Plane normal
            # = (wall_dir_x, 1, wall_dir_z), magnitude sqrt(2), 45° from
            # vertical when wall_dir is unit in XZ. xDir is perpendicular
            # to normal in the XZ plane (so the workplane's Z axis is
            # the cut plane's "horizontal" axis).
            cut_plane = cq.Plane(
                origin=(pivot_x_signed, boss_bottom_y, pivot_z),
                xDir=(-dir_z, 0, dir_x_signed),
                normal=(dir_x_signed, 1, dir_z),
            )
            # Half-space below the cut plane (toward cavity-and-down)
            # is the volume to remove. Extrude a large rect on the plane
            # in the -normal direction.
            cut_tool = (
                cq.Workplane(cut_plane)
                .rect(500, 500)
                .extrude(-500)
            )
            boss = boss.cut(cut_tool)

        body = body.union(boss)

        pocket = (
            _wp_at(px_signed, pocket_bottom_y, pz)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth + 0.1)  # +0.1 to break the top surface cleanly
        )
        body = body.cut(pocket)

    return body


def build_reservoir_cap(side=1):
    """
    PETG cap that sits on top of the reservoir body through a 2 mm TPU
    gasket.

    Orientation: the cap is a flat lid with a downward-hanging rim.
    The flat top face (the 3 mm base plate) is what the user sees
    from above, and is the surface the counterbored screw heads sit
    flush in. The 5 mm-tall × 6 mm-wide perimeter wall ("lip") hangs
    DOWN from the base plate around the gasket joint.

    In cap-local coordinates:
      - y = 0 .. 5  : perimeter wall (the downward-hanging rim)
      - y = 5 .. 8  : base plate (the flat top, full `[` footprint)
      - y = 8       : top face of the cap (the surface the screw
                      heads recess into; faces up / toward the user)

    To visualize the assembled stack, translate the cap up by
    (reservoir wall top y + gasket thickness) ≈ 213.9 mm. The
    perimeter-wall bottom face (cap y=0) lands at body y=213.9, the
    cap's top face (cap y=8) at body y=221.9.

    Six counterbored M3 holes pass through the cap at the same XZ
    positions as the body's insert bosses. ø6 × 3 mm counterbore on
    the top face recesses the M3 SHCS head flush in the base plate;
    ø3.5 clearance hole continues through the rest of the cap.
    Six cap-side bosses mirror the body bosses inside the perimeter
    wall, providing additional PETG around the clearance hole and a
    matching cross-section for the gasket compression at each screw.
    """
    # Same outer footprint as the reservoir body.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance

    # Perimeter wall inner footprint (offset inward by cap_wall_width).
    inner_far_x_abs = outer_far_x_abs - cap_wall_width
    inner_z_max = outer_z_max - cap_wall_width
    inner_centerward_radius = outer_centerward_radius + cap_wall_width

    # Perimeter wall (outer − inner footprint, 5 mm tall) at the BOTTOM
    # of the cap, y = [0, 5]. The "lip" that hangs down around the gasket.
    perimeter_outer = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        0.0, cap_wall_height,
    )
    perimeter_inner = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        0.0, cap_wall_height,
    )
    perimeter_wall = perimeter_outer.cut(perimeter_inner)

    # Base plate (full footprint, 3 mm thick) at the TOP of the cap,
    # y = [5, 8]. The flat surface the user sees from above; hosts the
    # counterbores for the screw heads.
    base = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        cap_wall_height, cap_base_thickness,
    )

    cap = base.union(perimeter_wall)

    cap_total_height = cap_base_thickness + cap_wall_height

    # Fillet the two exterior sharp corners (same outer footprint as
    # the body, so same sharp tabs). Done BEFORE the bosses are
    # unioned because the corner bosses (4/5) sit exactly at the
    # outer-fillet center, where the boss disk's outer edge IS the
    # fillet arc — unioning them first leaves no sharp corner edge
    # for the fillet selector to find, and CadQuery silently produces
    # malformed geometry (a leftover triangular tab where the corner
    # tip should have been rounded off). Filleting first, then
    # unioning the boss, leaves the fillet correct; the corner
    # bosses become a no-op there (the perimeter wall already covers
    # the boss-disk footprint inside the fillet arc), and the bosses
    # at the other four positions union normally.
    outer_corner_x = math.sqrt(outer_centerward_radius**2 - outer_z_max**2)
    y_mid_cap = cap_total_height / 2

    for sharp_z in (outer_z_max, -outer_z_max):
        cap = (
            cap
            .edges(cq.NearestToPointSelector(
                (side * outer_corner_x, y_mid_cap, sharp_z),
            ))
            .fillet(outer_corner_fillet_radius)
        )

    # Cap-side bosses at each insert position, mirroring the body
    # bosses. They sit inside the perimeter wall at y = [0, 5],
    # locally thickening the wall inward and providing extra PETG
    # around the clearance hole. Matching cross-sections on body and
    # cap also give the gasket a consistent bearing surface at each
    # screw position.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        boss = (
            _wp_at(px_signed, 0.0, pz)
            .circle(cap_boss_radius)
            .extrude(cap_wall_height)
        )
        cap = cap.union(boss)

    # Counterbored screw holes. The counterbore recesses the M3 SHCS
    # head 3 mm into the base plate (y = [5, 8.1], opening at the cap's
    # top face); the ø3.5 clearance hole continues through the rest of
    # the cap so the screw shaft can pass through the perimeter wall,
    # gasket, and into the body's insert pocket below.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        clearance = (
            _wp_at(px_signed, -0.1, pz)
            .circle(cap_clearance_hole_diameter / 2)
            .extrude(cap_total_height + 0.2)
        )
        cap = cap.cut(clearance)

        counterbore = (
            _wp_at(
                px_signed, cap_total_height - cap_counterbore_depth, pz,
            )
            .circle(cap_counterbore_diameter / 2)
            .extrude(cap_counterbore_depth + 0.1)
        )
        cap = cap.cut(counterbore)

    return cap


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    body = build_reservoir_body(side=1)
    cap = build_reservoir_cap(side=1)

    here = Path(__file__).resolve().parent
    export_step(body, str(here / "reservoir.step"))
    export_step(cap, str(here / "reservoir-cap.step"))
    print(f"-> reservoir.step")
    print(f"-> reservoir-cap.step")


if __name__ == "__main__":
    main()
