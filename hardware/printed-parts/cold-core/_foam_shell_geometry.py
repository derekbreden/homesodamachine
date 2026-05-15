"""Shared geometry for the foam shell and the foam-cap stack. Imported
by the two sibling generators (foam-shell/, foam-cap/), each of which
writes the STEPs for its own folder. Constants and build functions live
here so both generators produce a coherent set of mating parts."""

import math
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
xy_plane_z_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
# All structural walls and floors are 2 mm PETG.
wall_and_floor_thickness = 2.0
hole_shift_from_edge = 15.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank copper shell
# -------------------------------------------------------
#
# Outer radius of the tank-copper-shell cylinder.
#   = tank_outer_radius (63.5) + coil_radial_clearance (7) + wall (2) = 72.5
# The 7 mm radial clearance between the tank (R=63.5) and the inner shell
# face accommodates 1/4" ACR copper coil + thermal tape + assembly slack.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
tank_copper_shell_radius = tank_outer_radius + coil_radial_clearance + wall_and_floor_thickness
#
# Outer height of the tank-copper-shell cylinder.
#   = tank_height (152.4) + 30 below tank + 30 above tank + 1 mm floor allowance
# The floor lives at y=0..wall, so the cylinder's interior cavity (above
# the floor) is height − wall = 211.4 mm, providing the 30 mm of slack
# above/below the tank's elbows.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = tank_height + below_tank_elbows_height + above_tank_elbows_height + 1.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank support ring
# -------------------------------------------------------
#
tank_support_ring_height = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Bag pocket
# -------------------------------------------------------
#
# bag_pocket_width tracks tank_copper_shell_radius so the bag-pocket Z
# interior cavity (= width − 2 × wall = 141 mm) matches the cylinder's
# Z extent.  bag_pocket_depth gives an X interior cavity of 42 mm
# (= depth − 2 × wall) — sized so each reservoir holds ≥ 1 L of
# usable fluid (cavity volume after subtracting strut + wedge + panel
# housing + dry-section vent + bulkhead-body displacement).  Each
# additional mm of X interior adds ~23.6 mL of usable fluid; the
# baseline 33 mm interior cleared 791.6 mL, so 42 mm clears ~1004 mL
# per reservoir.  Outer-shell X width grows by 2 × 9 = 18 mm to match
# (both reservoirs deepen on their ±X sides), 251 mm → 269 mm.
bag_pocket_width = tank_copper_shell_radius * 2
bag_pocket_depth = 42 + 2 * wall_and_floor_thickness
#
# Derived bag-pocket inner-face coordinates, exposed for downstream
# parts (e.g. the printed reservoirs) that must clear the same cavity.
# Keeping these here means the reservoir cannot drift out of sync with
# wall_and_floor_thickness or any of the inputs above.
#   bag_pocket_far_inner_x:  +X face of the bag pocket interior
#   bag_pocket_z_inner_max:  ±Z face of the bag pocket interior
#   bag_pocket_floor_top_y:  top of the bag-pocket floor (= floor thickness)
#   bag_pocket_walls_top_y:  top of the bag-pocket walls (= shell height)
# At 2 mm wall: 105.5 / 70.5 / 2.0 / 213.4.
bag_pocket_far_inner_x = (
    tank_copper_shell_radius + bag_pocket_depth - 2 * wall_and_floor_thickness
)
bag_pocket_z_inner_max = bag_pocket_width / 2 - wall_and_floor_thickness
bag_pocket_floor_top_y = wall_and_floor_thickness
bag_pocket_walls_top_y = tank_copper_shell_height
#
# Reservoir interface constants. These describe properties of the
# printed reservoir that fits inside the bag pocket, but they live
# here (instead of in reservoir/generate_step_cadquery.py) because
# the foam shell's bulkhead-pass-through hole has to line up with
# the reservoir's outlet bulkhead — so a value used by both files
# belongs in the shared module. The reservoir imports these.
#   reservoir_clearance:        gap between reservoir outer faces and bag-pocket inner faces
#   reservoir_floor_thickness:  PETG thickness of the reservoir's outer floor (= reservoir wall thickness)
#   bulkhead_pocket_diameter:   ø of the JG bulkhead's flange chamber (= 22.9 mm flange + 0.1 mm clearance)
reservoir_clearance = 0.5
reservoir_floor_thickness = 4.0
bulkhead_pocket_diameter = 23.0
#
# Y of the reservoir's outlet-bulkhead axis, AND of the matching
# pass-through hole in the foam shell's bag-pocket wall (cut in
# `cut_circular_port_holes` below). Derived parametrically
# so the two values cannot drift on future wall-thickness changes:
#   outer_floor_bottom_y of the reservoir = bag_pocket_floor_top_y + reservoir_clearance
#   + reservoir_floor_thickness puts the inner floor top at the chamber's lower extent
#   + bulkhead_pocket_diameter / 2 raises that to the chamber's centerline (= bulkhead axis)
# At the current 2 mm shell wall: 2.0 + 0.5 + 4.0 + 11.5 = 18.0, which
# leaves the chamber's curved bottom at y = 18 − 11.5 = 6.5 — exactly
# on top of the reservoir's 4 mm outer floor (bottom y = 2.5, top y = 6.5),
# so 4 mm of PETG sits below the flange chamber as a fluid barrier.
reservoir_bulkhead_port_y = (
    bag_pocket_floor_top_y
    + reservoir_clearance
    + reservoir_floor_thickness
    + bulkhead_pocket_diameter / 2
)
#
# |X| of the reservoir's outlet-bulkhead axis, AND of the matching
# pass-through hole in the foam shell's bag-pocket +Z wall (cut in
# `cut_circular_port_holes` below). Sign flips with the reservoir
# side. Derived from the reservoir-side geometry: the foam-shell +Z
# wall has plenty of X range to accept the ⌀6.5 pass-through at
# almost any |X|, but the reservoir's bulkhead pocket has to fit
# inside the body's two interior X walls.
#
# Those two walls are:
#   - the +X far inner face (flat, at bag_pocket_far_inner_x
#     − reservoir_clearance − reservoir_floor_thickness)
#   - the concave-arc inner cavity wall on the tank-facing side,
#     whose deepest reach into the cavity is at z = 0, at
#     x = tank_copper_shell_radius + reservoir_clearance
#         + reservoir_floor_thickness
# Center between these two — even though the bulkhead pocket lives
# at z ≈ 30 where the arc has receded outward (toward the tank), use
# the arc's peak (z = 0) as the conservative inner-X bound. That way
# the centering is independent of the pocket's actual −Z reach and
# we get equal clearance to the two walls at the binding (z = 0)
# section, which is the part that would collide first if the pocket
# ever grew longer.
_reservoir_far_inner_x   = bag_pocket_far_inner_x - reservoir_clearance - reservoir_floor_thickness
_reservoir_arch_peak_x   = tank_copper_shell_radius + reservoir_clearance + reservoir_floor_thickness
reservoir_bulkhead_port_x = (_reservoir_arch_peak_x + _reservoir_far_inner_x) / 2
#
# -------------------------------------------------------


# -------------------------------------------------------
# Outer shell
# -------------------------------------------------------
#
outer_shell_foam_gap = 16.0
#
# Outer footprint, shared by the outer shell, the foam cap, and the
# foam cap lid (they must remain coplanar at the corners so the pin
# bosses line up).
bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap (top/bottom 16 mm foam pour tray, printed twice)
# -------------------------------------------------------
#
# Foam cap interior cavity height (= foam thickness in the cap), matched
# to outer_shell_foam_gap so the foam budget at the top/bottom faces of
# the assembly equals the foam budget on the long sides — 16 mm of foam
# everywhere around the tank.
foam_cap_interior_height = 16.0
# Foam cap outer height = interior cavity + floor. With
# wall_and_floor_thickness = 2 mm, outer height = 18 mm.
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap lid (sits atop a cap during foam pour, printed twice)
# -------------------------------------------------------
#
foam_cap_lid_pour_radius = 5.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cap-to-outer-shell screw + heat-set joinery
# -------------------------------------------------------
#
# Inserts: ruthex M3 short brass heat-set (Amazon B09ZHSGHXD,
# 100-pc bag ~$0.11/insert) — reused from the touch-flo-shell order;
# same insert spec works here. Press into the top and bottom faces
# of the outer_shell at 6 attachment points per face, 12 inserts
# per outer_shell.
#
# Screws: BNUOK M3 × 25 mm DIN 912 socket head cap, 12.9 alloy steel,
# black oxide finish (Amazon B0DJQGF665, 60-pc bag $8.57 delivered =
# $0.14/screw, sold by BNUOK Fasterner). Head Ø 5.5 × 3.0 mm tall,
# 2.5 mm hex socket (DIN 912 standard). Thread up from below the
# bottom cap and down from above the top cap + lid into the inserts.
# 12 screws per built unit. Black oxide on alloy steel is adequate
# corrosion protection for this dry foam-filled enclosed interior.
#
# Gasket: 2 mm-thick TPU 90A perimeter ring (foam-cap-gasket.step)
# matching the foam_cap footprint, with screw holes at the same
# 6 positions, compressed between each cap's mating edge and the
# outer_shell's mating face. Printed twice — one per cap.
#
# Replaces the earlier friction-fit dowel-pin design, which clamped
# nothing and left the cap-shell seam open to humid kitchen air —
# the condensation/frost concern.
#
# Standard SHCS chosen instead of the McMaster ULH used in touch-
# flo-mounting-plate: there's no flush-mount constraint here (the
# heads protrude on the appliance top and bottom faces; under-
# counter install hides both), and standard DIN 912 SHCS is roughly
# an order of magnitude cheaper Prime-shippable than McMaster ULH.
#
# Stack-up under the head, top cap (mm), with 2 mm walls/floors and
# 16 mm interior foam:
#   lid (2) + cap floor (2) + cap interior void / boss height (16)
#   + cap mating edge (2) + gasket (2)         = 24 mm
# Plus 4 mm engagement into the insert = 28 mm. The M3 × 25 is too
# short now; a longer M3 (≥ 30 mm) is needed at next BOM update.
#
# Insert pocket: Ø 4.0 mm × 8 mm deep (4 mm insert engagement +
# 4 mm relief so the M3 × 25 screw tip has 2 mm of clearance into
# the relief and doesn't bottom out).
#
screw_clearance_radius = 1.95   # = Ø 3.9, matches touch-flo screw clearance
insert_pocket_radius   = 2.0    # = Ø 4.0, recommended for ruthex M3 short
insert_pocket_depth    = 8.0    # 4 mm insert + 4 mm relief
screw_boss_size        = 8.0    # 8 × 8 mm square pillar at each attachment
#
# Six attachment-point (x, z) positions: 4 corners (inherited from
# the earlier pin layout) + 2 mid-long-side points near the ±Z walls.
# The mid-long-side adds halve the longest unsupported gasket span
# between adjacent screws from ~245 mm (corner-to-corner along the long
# axis) to ~120 mm.
#
# The two mid-long-side points are offset in X by ±mid_screw_x_offset
# (opposite signs at +Z vs −Z) so they clear the copper-line and water-
# outlet column that runs up the centerline at x=0. The 8×8 boss
# centered at x=0 would overlap that column; ±15 mm pushes the boss
# edge ~7.75 mm clear of the widest cut (the ⌀6.5 copper slit). Opposite
# signs at +Z and −Z preserve 180° rotational symmetry around the Y
# axis, which keeps the gasket compression balanced and avoids
# crowding both middle bosses onto one side of the foam-cap.
mid_screw_x_offset = 15.0
foam_cap_attachment_xz_positions = (
    [(x_sign * (outer_shell_x_length / 2 - screw_boss_size / 2),
      z_sign * (outer_shell_z_length / 2 - screw_boss_size / 2))
     for x_sign in (1, -1) for z_sign in (1, -1)]
    + [(z_sign * mid_screw_x_offset,
        z_sign * (outer_shell_z_length / 2 - screw_boss_size / 2))
       for z_sign in (1, -1)]
)
#
# Gasket: TPU 90A, rectangular perimeter ring matching the outer-
# shell footprint, 2 mm thick, 5 mm wide (1 mm aligned with the cap
# and shell wall edges that compress it, plus 4 mm extending inward
# over the cavity opening for print stability and material continuity).
# Six screw holes at the same foam_cap_attachment_xz_positions.
gasket_thickness   = 2.0
gasket_strip_width = 5.0
#
# -------------------------------------------------------
#
# -------------------------------------------------------


tank_copper_shell_open_z = 60.0
#
#
def build_tank_support_ring():
    """Annular ring inside the tank-copper-shell, holding the tank up
    by its outer rim.  Built as a revolve of a rectangular (R, y)
    profile around the Y axis; four 30°-wide angular slots at the
    diagonals (45°/135°/225°/315°) are cut as 30° revolves of the same
    profile (with a small radial margin), so every slot boundary is
    an arc on the same cylinder as the ring's inner and outer faces —
    no chord-vs-arc slivers left behind.
    """
    R_outer = tank_copper_shell_radius - wall_and_floor_thickness  # 70.5
    R_inner = R_outer - 9                                          # 61.5
    y_bottom = wall_and_floor_thickness                             # 2
    y_top = y_bottom + tank_support_ring_height                    # 32

    ring_profile = (
        cq.Workplane("XY")
        .moveTo(R_inner, y_bottom)
        .lineTo(R_outer, y_bottom)
        .lineTo(R_outer, y_top)
        .lineTo(R_inner, y_top)
        .close()
    )
    ring = ring_profile.revolve()

    # Four 30°-wide slots at the diagonals, leaving four 60° support
    # segments aligned with the cardinal axes.
    slot_radial_margin = 1.0
    slot_angular_width = 30
    def build_slot():
        return (
            cq.Workplane("XY")
            .moveTo(R_inner - slot_radial_margin, y_bottom)
            .lineTo(R_outer + slot_radial_margin, y_bottom)
            .lineTo(R_outer + slot_radial_margin, y_top)
            .lineTo(R_inner - slot_radial_margin, y_top)
            .close()
            .revolve(slot_angular_width)
        )
    for i in range(4):
        slot_center_angle = 45 + 90 * i
        slot_start_angle = slot_center_angle - slot_angular_width / 2
        slot = build_slot().rotate((0, 0, 0), (0, 1, 0), slot_start_angle)
        ring = ring.cut(slot)
    return ring

# Inner radius of the bag pocket's two far-side corners (where the
# far wall meets the +Z and −Z walls). Matches the reservoir's outer
# +X × ±Z fillet so the printed reservoir slides into a snugly-mated
# pocket. The reservoir's outer fillet is radius 6 mm with its center
# at (±98, ±64); maintaining the existing 0.5 mm reservoir_clearance
# uniformly around that arc puts the foam-shell pocket's inner-corner
# arc at radius 6.5 mm with the same center, so the inner-face
# tangents (x = ±104.5 along the far wall, z = ±70.5 along the ±Z
# walls) line up exactly with the surrounding flat-wall inner faces.
bag_pocket_corner_inner_radius = 6.5


def build_tank_and_bag_pocket_walls():
    """Cylindrical tank wall + four bridging walls + two bag-pocket
    U-walls (+X and −X), built per side as outer-loop polyline minus
    cavity-loop polyline, then unioned.

    The cylinder is cut at z = ±tank_copper_shell_open_z, leaving two
    crescents disjoint in cross-section — each crescent + its two
    bridging walls + its bag-pocket walls are one connected component.

    Outer loop (each side, +X polarity): bag-pocket outer far face
    (x=±107.5 from z=−64 to z=+64) + ±outer corner arcs R=8.5 +
    outer ±Z faces (z=±72.5) extended centerward to where the lobe
    arc breaks the z=±outer_z_pos line + a single R=8 arc that runs
    continuously from (arc_outer_x, ±outer_z) through the bridging
    apex (±35.06, ±65.25) down to (cyl_open_x_inner, ±60) — the lobe
    arc and the bridging tank-facing arc are co-circular and combine
    into one arc — then the cylinder R=70.5 inner face wraps the
    ±X apex, then mirrored on the other ±Z half to close.

    Cavity loop (each side): bag-pocket inner faces (z=±70.5, x=±105.5)
    + inner corner arcs R=6.5 + bridging walls' reservoir-facing
    R=R_bridging_inner (5.76) arcs + cylinder R=72.5 outer face around
    the ±X apex.
    """
    bag_pocket_height = tank_copper_shell_height
    half_width = bag_pocket_width / 2

    # Far-corner (bag-pocket) geometry.
    outer_x_abs = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness  # 107.5
    inner_x_abs = outer_x_abs - wall_and_floor_thickness                                   # 105.5
    inner_z_pos = half_width - wall_and_floor_thickness                                    # 70.5
    outer_z_pos = half_width                                                                # 72.5
    R           = bag_pocket_corner_inner_radius                                            # 6.5
    R_pocket_outer = R + wall_and_floor_thickness                                           # 8.5

    # Cylinder geometry (the cylinder's wall is the annulus
    # R−t ≤ r ≤ R, clipped to |z| ≤ tank_copper_shell_open_z).
    R_cyl_outer = tank_copper_shell_radius                                                  # 72.5
    R_cyl_inner = tank_copper_shell_radius - wall_and_floor_thickness                       # 70.5
    cyl_open_x_inner = math.sqrt(R_cyl_inner ** 2 - tank_copper_shell_open_z ** 2)          # 37.02
    cyl_open_x_outer = math.sqrt(R_cyl_outer ** 2 - tank_copper_shell_open_z ** 2)          # 40.69

    # Bridging-wall arc geometry. R=8 arc (tank-facing) is the same
    # circle as the centerward lobe arc that extends the wall up to
    # z = ±outer_z_pos. R=R_bridging_inner (reservoir-facing) is the
    # concentric arc one wall-thickness inboard radially; its endpoint
    # at z = ±tank_copper_shell_open_z hits x = cyl_open_x_outer so
    # the cylinder wall band meets the bridging wall flush at z = ±60.
    R_lobe         = 8.0
    half_chord     = (inner_z_pos - tank_copper_shell_open_z) / 2.0                         # 5.25
    d_lobe         = math.sqrt(R_lobe ** 2 - half_chord ** 2)                                # 6.04
    lobe_cx_abs    = cyl_open_x_inner + d_lobe                                               # 43.06
    lobe_cz_abs    = (inner_z_pos + tank_copper_shell_open_z) / 2.0                          # 65.25
    arc_outer_dx   = math.sqrt(R_lobe ** 2 - (outer_z_pos - lobe_cz_abs) ** 2)               # 3.38
    arc_outer_x_abs = lobe_cx_abs - arc_outer_dx                                             # 39.68
    d_bridging_inner = abs(cyl_open_x_outer - lobe_cx_abs)                                   # 2.37
    R_bridging_inner = math.sqrt(d_bridging_inner ** 2 + half_chord ** 2)                    # 5.76

    def outer_loop_midpoint(side, z_sign, theta):
        """A point on the R=8 lobe-arc/bridging circle at angle theta
        (radians) from the center (side·43.06, z_sign·65.25), returned
        in workplane (local) coordinates."""
        cx = side * lobe_cx_abs
        cz = z_sign * lobe_cz_abs
        return (cx + R_lobe * math.cos(theta), -(cz + R_lobe * math.sin(theta)))

    def cavity_loop_midpoint(side, z_sign, theta):
        """Same, on the R=R_bridging_inner circle."""
        cx = side * lobe_cx_abs
        cz = z_sign * lobe_cz_abs
        return (cx + R_bridging_inner * math.cos(theta),
                -(cz + R_bridging_inner * math.sin(theta)))

    def build_side(side):
        """Build one ±X side as an outer-loop polyline (extruded) with
        the cavity-loop polyline cut out of it. Done as outer-extrude
        minus cavity-extrude rather than a single multi-loop sketch
        because CadQuery's pending-wire heuristic mis-classifies two
        non-nested outer wires in the same workplane as nested ones."""
        # apex_angle: angle (in radians) on the bridging-arc circle
        # pointing back at origin. On +X side the circle's center is at
        # (+43.06, ±65.25), so the radius pointing toward origin (the
        # arc apex) is at angle π. On −X side, mirrored to 0.
        apex_angle = math.pi if side > 0 else 0.0

        outer_solid = (
            cq.Workplane(xz_plane_y_up)
            # bag-pocket outer +X face start at +Z outer corner tangent
            .moveTo(side * outer_x_abs, -(inner_z_pos - R))
            # outer +X face down to −Z outer corner tangent
            .lineTo(side * outer_x_abs, +(inner_z_pos - R))
            # outer +X−Z corner arc
            .radiusArc((side * (inner_x_abs - R), +outer_z_pos), -side * R_pocket_outer)
            # outer −Z face west to where the lobe arc breaks z=−72.5
            .lineTo(side * arc_outer_x_abs, +outer_z_pos)
            # combined lobe arc + −Z bridging tank-facing arc on R=8,
            # from (arc_outer_x, ±outer_z) all the way through the apex
            # down to (cyl_open_x_inner, ±tank_copper_shell_open_z) —
            # one continuous arc on the bridging-arc circle.
            .threePointArc(
                outer_loop_midpoint(side, -1, apex_angle),
                (side * cyl_open_x_inner, +tank_copper_shell_open_z),
            )
            # cylinder R−t inner face around the ±X apex
            .threePointArc(
                (side * R_cyl_inner, 0),
                (side * cyl_open_x_inner, -tank_copper_shell_open_z),
            )
            # combined +Z bridging tank-facing arc + +Z lobe arc on R=8
            .threePointArc(
                outer_loop_midpoint(side, +1, apex_angle),
                (side * arc_outer_x_abs, -outer_z_pos),
            )
            # outer +Z face east to start of outer +X+Z corner arc
            .lineTo(side * (inner_x_abs - R), -outer_z_pos)
            # outer +X+Z corner arc — closes the outer loop
            .radiusArc((side * outer_x_abs, -(inner_z_pos - R)), -side * R_pocket_outer)
            .close()
            .extrude(bag_pocket_height)
        )
        cavity_solid = (
            cq.Workplane(xz_plane_y_up)
            # bag-pocket inner +Z face start at the bridging inner-face
            # endpoint (= cyl_open_x_outer at z = ±inner_z_pos)
            .moveTo(side * cyl_open_x_outer, -inner_z_pos)
            # inner +Z face east to start of inner +X+Z corner arc
            .lineTo(side * (inner_x_abs - R), -inner_z_pos)
            # inner +X+Z corner arc
            .radiusArc((side * inner_x_abs, -(inner_z_pos - R)), -side * R)
            # inner +X face south to start of inner +X−Z corner arc
            .lineTo(side * inner_x_abs, +(inner_z_pos - R))
            # inner +X−Z corner arc
            .radiusArc((side * (inner_x_abs - R), +inner_z_pos), -side * R)
            # inner −Z face west back to the bridging inner-face endpoint
            .lineTo(side * cyl_open_x_outer, +inner_z_pos)
            # −Z bridging reservoir-facing inner arc (R=R_bridging_inner),
            # back down to z = +tank_copper_shell_open_z
            .threePointArc(
                cavity_loop_midpoint(side, -1, apex_angle),
                (side * cyl_open_x_outer, +tank_copper_shell_open_z),
            )
            # cylinder R outer face around the ±X apex
            .threePointArc(
                (side * R_cyl_outer, 0),
                (side * cyl_open_x_outer, -tank_copper_shell_open_z),
            )
            # +Z bridging reservoir-facing inner arc back up to z = −inner_z_pos
            # — closes the cavity loop
            .threePointArc(
                cavity_loop_midpoint(side, +1, apex_angle),
                (side * cyl_open_x_outer, -inner_z_pos),
            )
            .close()
            .extrude(bag_pocket_height)
        )
        return outer_solid.cut(cavity_solid)

    return build_side(side=+1).union(build_side(side=-1))

def build_outer_shell():
    """Outer rectangular cup (floor + four perimeter walls) with the
    6 corner/mid-side bosses and their heat-set insert pockets."""
    shell = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    # pushPoints uses workplane-local coords; on xz_plane_y_up, local Y
    # = -world Z, so flip the z component of each (x, z) world position.
    boss_points = [(x, -z) for (x, z) in foam_cap_attachment_xz_positions]
    # Six full-height bosses.
    bosses = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(tank_copper_shell_height)
    )
    # Heat-set insert pockets — one set drilled DOWN from the top face
    # (accepting the top-cap screw threading down from above) and one
    # set drilled UP from the bottom face (accepting the bottom-cap
    # screw threading up from below).
    top_pockets = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=tank_copper_shell_height - insert_pocket_depth)
        .pushPoints(boss_points)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    bottom_pockets = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(insert_pocket_radius)
        .extrude(insert_pocket_depth)
    )
    return shell.union(bosses).cut(top_pockets).cut(bottom_pockets)

def build_foam_cap():
    cap = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    # Same workplane-local coord flip as in build_outer_shell.
    boss_points = [(x, -z) for (x, z) in foam_cap_attachment_xz_positions]
    bosses = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(foam_cap_height)
    )
    # Screw clearance holes through the full boss height — the screws
    # pass from the cap floor (top in service) all the way to the cap's
    # mating edge (bottom in service).
    clearances = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(foam_cap_height)
    )
    cap = cap.union(bosses).cut(clearances)
    # Consolidate the multi-cut Compound into a single Solid for clean
    # STEP export.
    return cap.union(cap)

def build_foam_cap_lid():
    lid = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(wall_and_floor_thickness)
    )

    pour_x = outer_shell_x_length / 2 - foam_cap_lid_hole_inset
    vent_x = -(outer_shell_x_length / 2 - foam_cap_lid_hole_inset)
    vent_z = outer_shell_z_length / 2 - foam_cap_lid_hole_inset

    pour_hole = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(pour_x, 0, 0))
        .circle(foam_cap_lid_pour_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_a = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_b = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, -vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )

    lid = lid.cut(pour_hole).cut(vent_hole_a).cut(vent_hole_b)

    # Six screw-clearance holes, one per attachment position.
    boss_points = [(x, -z) for (x, z) in foam_cap_attachment_xz_positions]
    clearances = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    return lid.cut(clearances)

def build_foam_cap_gasket():
    """TPU 90A gasket between foam_cap mating edge and outer_shell
    mating face.

    Flat 2D shape, gasket_thickness mm tall throughout. The shape is
    a rectangular perimeter ring matching the outer_shell footprint,
    PLUS a screw_boss_size × screw_boss_size pad at each of the 6
    screw positions matching the matching boss footprints on the cap
    and shell.

    Perimeter ring: gasket_strip_width (5 mm) wide. 1 mm of the
    width is aligned with the cap and shell wall edges that compress
    it (where the seal happens along the wall sections); the
    remaining 4 mm extends inward over the cavity opening for print
    stability and material continuity.

    Screw-position pads: 8 × 8 mm squares centered on each
    foam_cap_attachment_xz_position. Each screw hole sits at the
    center of its pad with 4 mm of TPU material on all sides — same
    buffer as the 8 × 8 boss footprint above and below the gasket —
    so the screw clamp force compresses the full boss footprint
    uniformly. A uniform-width ring without these pads would leave
    the corner-boss screw holes asymmetrically supported (1 mm of
    TPU on the cavity-facing side, 4 mm on the outer-facing side),
    which would compress unevenly and seal poorly at the corners.

    Printed twice: one gasket sits between the top cap and the
    outer_shell top edge, one between the bottom cap and the
    outer_shell bottom edge.
    """
    outer = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(gasket_thickness)
    )
    inner = (
        cq.Workplane(xz_plane_y_up)
        .rect(
            outer_shell_x_length - 2 * gasket_strip_width,
            outer_shell_z_length - 2 * gasket_strip_width,
        )
        .extrude(gasket_thickness)
    )
    gasket = outer.cut(inner)

    # 8 × 8 mm pads at each screw position, matching the cap and
    # outer_shell boss footprints. At corner screws, each pad extends
    # 3 mm inward beyond the perimeter ring on both axes; at mid-
    # long-side screws, 3 mm inward on the wall-perpendicular axis.
    # Holes are cut AFTER the pads are unioned in, so each hole sits
    # at the center of an 8 × 8 mm pad surrounded by 4 mm of TPU.
    boss_points = [(x, -z) for (x, z) in foam_cap_attachment_xz_positions]
    pads = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .rect(screw_boss_size, screw_boss_size)
        .extrude(gasket_thickness)
    )
    holes = (
        cq.Workplane(xz_plane_y_up)
        .pushPoints(boss_points)
        .circle(screw_clearance_radius)
        .extrude(gasket_thickness)
    )
    return gasket.union(pads).cut(holes)

def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    # Default height (40 mm) is intentionally larger than every call
    # site's exact wall-reach distance.  Don't reduce it to the
    # per-hole exact reach — looks like an obvious refactor, but the
    # co2_inlet's hole is tangent to the support ring's inner curved
    # cylinder (r = 61.5).  At the hole's outer radius |x| = 3.25 the
    # ring extends to z ≈ -61.41, so an exact-reach height of 9 mm
    # (ending at z = -61.5) leaves a ~1.86 mm³ sliver of ring material
    # in the tube's actual path.  The 40 mm overshoot reliably clears
    # that.  (Flat-wall holes — water_outlet, reservoir bulkheads —
    # do tolerate exact-reach face coincidence, but mixing exact-reach
    # for some and overshoot for others adds nothing here; the 40 mm
    # extrude just cuts air past the wall in those cases.)
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )

def build_a_slot_punch(
    origin=(0, 0, 0),
    slot_length=1.0,
    slot_diameter=6.5,
    slot_punch_height=40,
):
    """Y-elongated, Z-extruded rounded slot (circle-rect-circle), centered
    at `origin`. The slot's long axis runs along world Y (angle=90 on a
    workplane whose own X axis = world X), short axis along world X. The
    rounded ends each contribute slot_diameter/2 of additional Y reach
    beyond `slot_length` — so the through-wall opening at the top end
    extends slot_diameter/2 above origin_y + slot_length/2."""
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .slot2D(slot_length, slot_diameter, angle=90)
        .extrude(slot_punch_height)
    )

# All circular port holes through the foam shell: Z-axis ⌀6.5 × 40 mm
# cylindrical cuts, starting at the given z and extending in +Z.
#   - water_outlet:            outer +Z wall
#   - reservoir_bulkhead_±X:   bag-pocket +Z wall (and outer +Z wall;
#     the bulkhead body sits in the bag-pocket wall, the dry-side tube
#     exits through the outer wall along the same axis)
#
# The CO2 inlet through the −Z support arch is cut separately by
# `cut_co2_inlet()` — its bore is ⌀16 (vs ⌀6.5 here) to house an
# in-cavity 90° push-to-connect elbow, so it doesn't fit this list's
# default radius.
CIRCULAR_PORT_HOLES = [
    # (x, y, z)
    (0,                          hole_shift_from_edge + wall_and_floor_thickness,    tank_copper_shell_radius - 20),
    (+reservoir_bulkhead_port_x, reservoir_bulkhead_port_y,                          bag_pocket_width / 2 - 10),
    (-reservoir_bulkhead_port_x, reservoir_bulkhead_port_y,                          bag_pocket_width / 2 - 10),
]

def cut_circular_port_holes(foam_shell):
    for (x, y, z) in CIRCULAR_PORT_HOLES:
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=(x, y, z)))
    return foam_shell

def cut_co2_inlet(foam_shell):
    """CO2 inlet through the −Z support arch: a Z-axis "doorway" cut
    that combines a ⌀16 round bore (upper half) with a rectangular slot
    clamped to the support arch's bottom face. The composite cut looks
    like a classic doorway / tombstone profile when viewed from outside
    the −Z support arch at z=−70.5:

      - rounded top: upper half of the Ø16 circle, y=17..25, x=±8
      - rectangular body: 16 mm wide in X × (slot_y_top − slot_y_bottom)
        tall in Y, from y=slot_y_bottom=wall_and_floor_thickness (the
        floor's top face / arch's bottom face) up to y=slot_y_top=17
        (the bore's Y center)

    Both halves are extruded 40 mm in +Z, so the cut pierces the full
    Z thickness of the arch material (z=−70.5..−61.5 ≈ 9 mm of solid
    PETG) and continues into the cavity beyond.

    The CO2 line drops vertically through the foam-cap top and then
    makes a 90° turn inside the cylinder cavity at a John Guest PP0308E
    push-to-connect elbow (~⌀15 mm body, ~20 mm legs). The elbow's
    horizontal leg seats in the Ø16 round pocket, which is sized to
    clear the elbow body (vs the ⌀6.5 of the other circular port holes,
    which are sized for 1/4" OD tubing).

    Assembly rationale (step 2/2): the elbow has perpendicular legs
    that snag at the round bore's opening if you try to insert it along
    the bore axis, and the back wall (z<−70.5) is solid, so there is
    no through-axis insertion path either. The rectangular slot extends
    the bore downward to the support arch's bottom face — its bottom
    is flush with the floor's top face at y=wall_and_floor_thickness
    and does NOT cut through the foam-shell floor below it. The slot
    only provides angled-insertion clearance from above: the elbow is
    lowered through the open +Y top of the foam shell with one leg
    tilted into the doorway opening on the arch's bottom face, then
    rotated/translated into the round pocket. Once seated, it stays."""
    co2_inlet_z_start = -(tank_copper_shell_radius - wall_and_floor_thickness)
    co2_inlet_y_center = hole_shift_from_edge + wall_and_floor_thickness
    bore_radius = 8.0  # ⌀16, sized to clear the ~⌀15 mm PP0308E elbow body.
    # Round bore — upper half of the doorway profile.
    round_bore = build_a_hole_punch(
        origin=(0, co2_inlet_y_center, co2_inlet_z_start),
        hole_punch_radius=bore_radius,
    )
    # Rectangular slot — body of the doorway, extending from the bore's
    # Y center (= top of the slot) down to the support arch's bottom
    # face at y=wall_and_floor_thickness (= top face of the foam-shell
    # floor). The floor below stays intact. Width in X matches the
    # bore's diameter so the slot sides line up tangent with the bore's
    # vertical extents and the round/rect join is clean.
    slot_width = 2 * bore_radius  # 16 mm — matches the bore's diameter.
    slot_y_top = co2_inlet_y_center  # 17 — bore's Y center, the round/rect join.
    slot_y_bottom = wall_and_floor_thickness  # 2 — flush with floor's top face / arch's bottom face.
    slot_height_y = slot_y_top - slot_y_bottom
    slot_y_center = (slot_y_top + slot_y_bottom) / 2.0
    slot_extrude_z = 40              # matches the round bore's Z extrusion.
    slot_punch = (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(0, slot_y_center, co2_inlet_z_start), offset=co2_inlet_z_start)
        .rect(slot_width, slot_height_y)
        .extrude(slot_extrude_z)
    )
    return foam_shell.cut(round_bore).cut(slot_punch)

def build_a_y_axis_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    """Y-axis ⌀ × height cylindrical cut, centered in (X, Z) at `origin`'s
    X/Z and starting at `origin`'s Y, extruded in +Y. Mirror of
    `build_a_hole_punch` but along the Y axis instead of the Z axis."""
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=origin, offset=origin[1])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )

def cut_slot_for_copper_and_water_inlet(foam_shell):
    """Single Y-elongated slot through the outer_shell +Z wall, shared by
    the two copper plugs (low and high) and the water-inlet plug. X width
    is 6.5 mm (rounded slot ends), matching the ⌀6.5 of the original
    single-port holes; Y span runs from a few mm below the lowest copper
    plug (y≈46) up past the wall's top edge so plugs can be slid down
    into the slot from above. Z-extruded 40 mm starting from z = R − 20
    (matching the existing hole_punch convention), enough to fully pierce
    the +Z wall (outer face at z ≈ R + 18). With the cylinder wall now
    open at ±Z and the bag_pocket_support_shell ±Z walls gapped at x=0,
    the slot pierces only this one wall.

    `slot_y_top` is pushed `slot_diameter/2` past `tank_copper_shell_
    height` so the slot2D's rounded top tapers above the wall — the
    straight (full-width) portion of the slot reaches exactly the
    wall's top edge, so the wall is fully open at the top with no
    sliver remaining."""
    slot_diameter = 6.5
    slot_y_bottom = 42.0
    slot_y_top    = tank_copper_shell_height + slot_diameter / 2
    slot_length   = slot_y_top - slot_y_bottom
    slot_y_center = (slot_y_top + slot_y_bottom) / 2.0
    slot_z_offset = tank_copper_shell_radius - 20
    slot_x_offset = 0
    slot_punch = build_a_slot_punch(
        origin=(slot_x_offset, slot_y_center, slot_z_offset),
        slot_length=slot_length,
        slot_diameter=slot_diameter,
    )
    return foam_shell.cut(slot_punch)

# ═══════════════════════════════════════════════════════
# TOP-LEVEL ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_full_shell():
    """Assemble the foam shell and cut all its port holes."""
    foam_shell = (
        build_tank_and_bag_pocket_walls()
        .union(build_tank_support_ring())
        .union(build_outer_shell())
    )
    foam_shell = cut_circular_port_holes(foam_shell)
    foam_shell = cut_co2_inlet(foam_shell)
    foam_shell = cut_slot_for_copper_and_water_inlet(foam_shell)
    return foam_shell


