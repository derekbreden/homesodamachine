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
# Heat-set insert + screw spec
# -------------------------------------------------------
#
# M3 ruthex-style brass heat-set inserts (same as foam-bag-shell cap-
# stack joinery). Insert OD 4 mm × length 4 mm; pocket is 4 mm bore
# × 5 mm deep (4 mm insert + 1 mm relief). Screws: M3 SHCS, black
# 12.9 alloy preferred. Length needed for the cap stack is
# ~11–13 mm minimum (see comments in build_reservoir_cap); M3x12 or
# M3x16 are the natural choices. The B0DJQGF665 M3x25 used on the
# foam_cap stack is longer than necessary here; the boss is sized to
# tolerate it anyway.
#
insert_pocket_radius = 2.0
insert_pocket_depth = 5.0
#
# Six insert positions (for the side=+1 reservoir; sign flips for −1):
#   4 corners of the `[` + 2 mid-long-edges (the far-wall midpoint and
#   the centerward-curve apex). Distance check: every position is
#   within the reservoir wall material with at least 2 mm of PETG
#   around the ø4 mm insert.
#
#   1. (100, +66)   far wall × +Z wall, inner corner
#   2. (100, −66)   far wall × −Z wall, inner corner
#   3. (100,   0)   far wall, midpoint
#   4. (45,  +66)   inner curve × +Z wall, in the wedge of body material
#                   filled in by the inner-corner concave fillet. The
#                   fillet added body material to round out the cavity's
#                   sharp 30° corner; the wedge ends up substantially
#                   thicker than the 4 mm walls elsewhere, so the ø8 boss
#                   fits entirely inside it (verified by probing the
#                   post-fillet solid: full disk at center (45, 66)
#                   sits inside the body cross-section).
#   5. (45,  −66)   inner curve × −Z wall (mirror)
#   6. (76,    0)   centerward curve apex, midpoint
#
INSERT_POSITIONS_FOR_SIDE_PLUS_1 = [
    (100.0, 66.0),
    (100.0, -66.0),
    (100.0, 0.0),
    (45.0, 66.0),
    (45.0, -66.0),
    (76.0, 0.0),
]
#
# Boss geometry: vertical cylindrical thickening of the wall at each
# insert position. ø8 mm gives 2 mm of PETG around the ø4 mm insert
# pocket. Boss extends 20 mm downward from the wall top, which is
# enough to host the screw shaft tip for any reasonable M3 length and
# to keep the boss/wall transition above mid-cavity.
#
boss_radius = 4.0
boss_height = 20.0
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
# Base plate + raised perimeter wall (the "stub of wall" that recesses
# the screw heads). The 6 mm-wide perimeter wall hosts the M3 screws
# fully recessed via counterbores; the central base plate seals the
# rest of the reservoir top through the gasket below.
#
cap_base_thickness = 3.0
cap_wall_height = 5.0
cap_wall_width = 6.0
#
# Screw recess geometry. M3 SHCS head OD ~5.5 mm; ø6 counterbore is
# the standard fit. Counterbore depth 3 mm leaves 5 mm of cap material
# below it (base_thickness + wall_height − counterbore_depth), more
# than enough for the screw shaft to traverse through clearance.
cap_counterbore_diameter = 6.0
cap_counterbore_depth = 3.0
cap_clearance_hole_diameter = 3.5
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
        boss = (
            _wp_at(px_signed, boss_bottom_y, pz)
            .circle(boss_radius)
            .extrude(boss_height)
        )
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
    gasket. Two-piece geometry: a 3 mm base plate covering the full
    `[`-shaped footprint, plus a 5 mm-tall × 6 mm-wide raised perimeter
    wall around the outside (the "stub of wall" that recesses the M3
    cap-screw heads).

    Six counterbored screw holes pass through the cap at the same
    perimeter positions as the body's insert bosses. ø6 × 3 mm
    counterbore on top recesses the M3 SHCS head fully; ø3.5 clearance
    hole through the remaining 5 mm of cap thickness lets the screw
    shaft pass through to the gasket + insert below.

    Cap output is positioned at y = 0 (its own coordinate origin). To
    visualize the assembled stack, translate the cap up by
    (reservoir wall top y + gasket thickness) ≈ 213.9 mm.
    """
    # Same outer footprint as the reservoir body.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance

    # Perimeter wall inner footprint (offset inward by cap_wall_width).
    inner_far_x_abs = outer_far_x_abs - cap_wall_width
    inner_z_max = outer_z_max - cap_wall_width
    inner_centerward_radius = outer_centerward_radius + cap_wall_width

    # Base plate (full footprint, 3 mm thick) at y = [0, 3].
    base = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        0.0, cap_base_thickness,
    )

    # Perimeter wall (outer footprint − inner footprint, 5 mm tall)
    # sitting on top of the base plate at y = [3, 8].
    perimeter_outer = _build_outer_envelope(
        side, outer_far_x_abs, outer_z_max, outer_centerward_radius,
        cap_base_thickness, cap_wall_height,
    )
    perimeter_inner = _build_outer_envelope(
        side, inner_far_x_abs, inner_z_max, inner_centerward_radius,
        cap_base_thickness, cap_wall_height,
    )
    perimeter_wall = perimeter_outer.cut(perimeter_inner)

    cap = base.union(perimeter_wall)

    cap_total_height = cap_base_thickness + cap_wall_height

    # Cap-side bosses at each insert position, mirroring the body bosses.
    # Without these, the ø6 counterbore (= cap_wall_width) extends past
    # the perimeter wall's inner edge at the mid-edge positions, leaving
    # the counterbore open into the cap's central opening on the inside —
    # the screw head wouldn't be fully recessed. Each boss is a ø8
    # cylindrical thickening that sits on top of the base plate and runs
    # the full height of the perimeter wall, providing the same 1 mm of
    # PETG on either side of the counterbore that the corner positions
    # naturally have from the L-shaped wall.
    for (px, pz) in INSERT_POSITIONS_FOR_SIDE_PLUS_1:
        px_signed = px * side
        boss = (
            _wp_at(px_signed, cap_base_thickness, pz)
            .circle(boss_radius)
            .extrude(cap_wall_height)
        )
        cap = cap.union(boss)

    # Fillet the two exterior sharp corners (same outer footprint as
    # the body, so same sharp tabs). Done before drilling so the
    # counterbore-edge geometry doesn't confuse the edge selector.
    # Inner perimeter-wall corners are not user-visible and left alone.
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

    # Counterbored screw holes at each insert position. ø3.5 clearance
    # passes through the full cap thickness; ø6 × 3 mm counterbore at
    # the top recesses the M3 SHCS head fully below the cap's top face.
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
