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


# Tank copper shell. 7 mm radial clearance between the tank and the
# inner shell face fits 1/4" ACR copper coil + thermal tape + slack.
tank_outer_radius = 63.5
coil_radial_clearance = 7.0
tank_copper_shell_radius = tank_outer_radius + coil_radial_clearance + wall_and_floor_thickness

tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = tank_height + below_tank_elbows_height + above_tank_elbows_height + 1.0

tank_support_ring_height = 30.0

# Bag pocket. Width tracks tank_copper_shell_radius so the Z interior
# cavity matches the cylinder's Z extent. Depth sized so each reservoir
# holds ≥1 L of usable fluid (~23.6 mL per mm of X interior; baseline
# 33 mm cleared 791.6 mL; 42 mm clears ~1004 mL).
bag_pocket_width = tank_copper_shell_radius * 2
bag_pocket_depth = 42 + 2 * wall_and_floor_thickness
bag_pocket_far_inner_x = tank_copper_shell_radius + bag_pocket_depth - 2 * wall_and_floor_thickness
bag_pocket_z_inner_max = bag_pocket_width / 2 - wall_and_floor_thickness
bag_pocket_floor_top_y = wall_and_floor_thickness
bag_pocket_walls_top_y = tank_copper_shell_height

reservoir_clearance = 0.5
reservoir_floor_thickness = 4.0
bulkhead_pocket_diameter = 23.0

reservoir_bulkhead_port_y = (
    bag_pocket_floor_top_y
    + reservoir_clearance
    + reservoir_floor_thickness
    + bulkhead_pocket_diameter / 2
)
reservoir_bulkhead_port_x = (bag_pocket_far_inner_x + tank_copper_shell_radius) / 2

# Outer footprint shared by the outer shell, the foam cap, and the
# foam cap lid (must be coplanar at the corners so the pin bosses
# line up).
outer_shell_foam_gap = 16.0
bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)


foam_cap_interior_height = outer_shell_foam_gap
foam_cap_height = foam_cap_interior_height + wall_and_floor_thickness

foam_cap_lid_pour_radius = 5.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0

# Cap-to-outer-shell joinery: ruthex M3 heat-set inserts + M3 SHCS,
# 6 attachment points per face × 2 faces = 12 inserts / 12 screws.
# Gasket compresses between each cap's mating edge and the outer shell
# (foam-cap-gasket.step). See bom.md for hardware SKUs.
screw_clearance_radius = 1.95   # ⌀3.9 clearance for M3 SHCS shank
insert_pocket_radius   = 2.0    # ⌀4.0 for ruthex M3 short heat-set
insert_pocket_depth    = 8.0    # 4 mm insert engagement + 4 mm relief
screw_boss_size        = 8.0    # 8 × 8 mm square pillar at each attachment

# Mid-long-side bosses offset in X to clear the copper/water-outlet
# slot at x=0; opposite signs at ±Z preserve 180° rotational symmetry
# around the Y axis (balanced gasket compression).
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
    cavity-loop polyline, then unioned. The cylinder is cut at
    z = ±tank_copper_shell_open_z, leaving two crescents disjoint in
    cross-section — each crescent + its two bridging walls + its
    bag-pocket walls are one connected component."""
    bag_pocket_height = tank_copper_shell_height
    half_width = bag_pocket_width / 2

    outer_x_abs = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
    inner_x_abs = outer_x_abs - wall_and_floor_thickness
    inner_z_pos = half_width - wall_and_floor_thickness
    outer_z_pos = half_width
    R           = bag_pocket_corner_inner_radius
    R_pocket_outer = R + wall_and_floor_thickness

    R_cyl_outer = tank_copper_shell_radius
    R_cyl_inner = tank_copper_shell_radius - wall_and_floor_thickness
    cyl_open_x_inner = math.sqrt(R_cyl_inner ** 2 - tank_copper_shell_open_z ** 2)
    cyl_open_x_outer = math.sqrt(R_cyl_outer ** 2 - tank_copper_shell_open_z ** 2)

    # Bridging-wall arcs. The tank-facing R=8 arc is the same circle as
    # the centerward lobe arc, so they combine into one continuous arc
    # on the outer loop. The reservoir-facing arc is the concentric one
    # wall-thickness inboard radially; its endpoint at z = ±open_z hits
    # x = cyl_open_x_outer so the cylinder wall band meets it flush.
    R_lobe         = 8.0
    half_chord     = (inner_z_pos - tank_copper_shell_open_z) / 2.0
    d_lobe         = math.sqrt(R_lobe ** 2 - half_chord ** 2)
    lobe_cx_abs    = cyl_open_x_inner + d_lobe
    lobe_cz_abs    = (inner_z_pos + tank_copper_shell_open_z) / 2.0
    arc_outer_dx   = math.sqrt(R_lobe ** 2 - (outer_z_pos - lobe_cz_abs) ** 2)
    arc_outer_x_abs = lobe_cx_abs - arc_outer_dx
    d_bridging_inner = abs(cyl_open_x_outer - lobe_cx_abs)
    R_bridging_inner = math.sqrt(d_bridging_inner ** 2 + half_chord ** 2)

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
    the +Z wall (outer face at z ≈ R + 18). With the tank cylinder
    open at ±Z and the support ±Z walls gapped at x=0 (both folded
    into `build_tank_and_bag_pocket_walls`), the slot pierces only
    this one wall.

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

# Horizontal cable channel cavity sits on the foam-shell floor
# (bottom y = wall_and_floor_thickness) — no unsupported envelope
# floor mid-air. The +Z cable hole shares cable_y_center, so the
# cable runs straight from channel to hole with no y-bend.
cable_y_half_h = 4.0
cable_y_center = wall_and_floor_thickness + cable_y_half_h

# X depth of the cable channel cavity, also the rise of the 45°
# printability slope on the cavity ceiling (slope runs over this same
# x distance, then continues wall_and_floor_thickness further through
# the bag-pocket wall).
cable_channel_x_depth = 5.0

# Vertical reed channel position in Z, matching the reservoir's
# STRUT_POSITION_Z so reeds sit opposite the float-on-strut across
# the bag-pocket wall.
reed_z_center = -45.0
reed_z_half_w = 4.0

# +Z extent of the horizontal cable channel — reaches the +Z
# bag-pocket inner face.
cable_z_max = 70.5

# X depth of the vertical reed channel cavity.
reed_x_depth = 6.0


def build_reed_channels(side):
    """Reed-and-cable channel system for one ±X reservoir, returned as
    a single solid (new wall material) to union with the foam shell.

    Two segments, both with back face on the bag-pocket far ±X wall,
    extruding outward into the outer-foam zone:

    - Vertical reed channel at z = reed_z_center, open at the top so
      the pre-soldered reed column can be dropped in before the foam
      cap is installed.
    - Horizontal cable channel running in +Z from the vertical channel
      to the +Z bag-pocket inner face. Cavity sits on the foam-shell
      floor; ceiling slopes 45° over the straight section for
      printability (no bridging). Cable exits at z = cable_z_max
      through wall openings cut by `cut_reed_channel_openings`, then
      out the +Z cable hole at the same y = cable_y_center so no
      y-bend is required.

    `side` = ±1 mirrors x across the y-z plane."""
    s = side
    W = wall_and_floor_thickness

    bag_x = s * bag_pocket_outermost_x  # outer face of bag-pocket far ±X wall

    def make_box(x_a, x_b, y_min, y_max, z_a, z_b):
        x_min, x_max = min(x_a, x_b), max(x_a, x_b)
        z_min, z_max = min(z_a, z_b), max(z_a, z_b)
        return (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=y_min)
            .moveTo((x_min + x_max) / 2, -(z_min + z_max) / 2)
            .rect(x_max - x_min, z_max - z_min)
            .extrude(y_max - y_min)
        )

    # Vertical reed channel envelope + cavity
    vert_envelope = make_box(
        bag_x, bag_x + s * (reed_x_depth + W),
        cable_y_center - cable_y_half_h - W, tank_copper_shell_height,
        reed_z_center - reed_z_half_w - W, reed_z_center + reed_z_half_w + W,
    )
    vert_cavity = make_box(
        bag_x, bag_x + s * reed_x_depth,
        cable_y_center - cable_y_half_h, tank_copper_shell_height,
        reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w,
    )

    # Horizontal cable channel envelope + cavity. The (+X, +Z) corner
    # of each — the corner opposite the bag pocket at the +Z end of
    # the channel — is rounded with R = bag_pocket_corner_inner_radius.
    # At this corner the cable bends from going +Z (along the channel)
    # to going -X (out into the bag-pocket interior via the wall
    # opening cut by `cut_reed_channel_openings`); the rounded corner
    # gives the cable's outer fiber a smooth bend path along an arc
    # parallel to the bag-pocket inner corner arc the channel joins.
    #
    # Built as polylines (cross-section in the xz plane, extruded in
    # +Y across the channel y range) rather than `make_box(...).fillet()`
    # because R is larger than cable_channel_x_depth — the cavity's +Z face is
    # too narrow for a tangent fillet, so the arc is tangent only to
    # the channel-outer face and meets the channel-inner face partway
    # up along the -X side. The envelope's +Z face IS wide enough for
    # a true tangent fillet (cable_channel_x_depth + W > R), so its arc is
    # tangent to both faces.
    R = bag_pocket_corner_inner_radius

    horiz_envelope = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_y_center - cable_y_half_h - W)
        .moveTo(bag_x, -(reed_z_center - reed_z_half_w - W))                # (-X, -Z) corner
        .lineTo(bag_x + s * (cable_channel_x_depth + W), -(reed_z_center - reed_z_half_w - W))  # +X face start
        .lineTo(bag_x + s * (cable_channel_x_depth + W), -(cable_z_max + W - R))    # +X face to arc tangent
        .radiusArc(
            (bag_x + s * (cable_channel_x_depth + W - R), -(cable_z_max + W)),
            s * R,
        )                                                                     # quarter-circle to +Z tangent
        .lineTo(bag_x, -(cable_z_max + W))                                   # +Z face to (-X, +Z) corner
        .close()                                                              # -X face back to start
        .extrude(2 * (cable_y_half_h + W))
    )

    # Where the cavity arc crosses the channel-inner face (x = bag_x):
    # solve (R - cable_channel_x_depth)² + (z - center_z)² = R² for z, where
    # center_z = cable_z_max - R.
    cavity_arc_z_at_inner_x = (cable_z_max - R) + math.sqrt(R**2 - (R - cable_channel_x_depth)**2)
    horiz_cavity = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=cable_y_center - cable_y_half_h)
        .moveTo(bag_x, -(reed_z_center - reed_z_half_w))                    # (-X, -Z) corner
        .lineTo(bag_x + s * cable_channel_x_depth, -(reed_z_center - reed_z_half_w))  # +X face start
        .lineTo(bag_x + s * cable_channel_x_depth, -(cable_z_max - R))              # +X face to arc tangent
        .radiusArc(
            (bag_x, -cavity_arc_z_at_inner_x),
            s * R,
        )                                                                     # arc to -X face crossing
        .close()                                                              # -X face back to start
        .extrude(2 * cable_y_half_h)
    )

    # Sloped ceiling on the horizontal cable channel (straight section
    # only, z ≤ cable_z_max − R). Triangular wedge added to both
    # envelope and cavity, rising 1:1 (45°) over cable_channel_x_depth
    # from the channel-outer face to the bag-pocket-wall side. Self-
    # supporting in Y-up print; no internal support material needed.
    # The +Z corner area keeps its current flat ceiling (TODO: address
    # the resulting step at z = cable_z_max − R in a later iteration).
    slope_z_min_env = reed_z_center - reed_z_half_w - W
    slope_z_min_cav = reed_z_center - reed_z_half_w
    slope_z_max     = cable_z_max - R
    env_wedge_y_low  = cable_y_center + cable_y_half_h + W
    env_wedge_y_high = env_wedge_y_low + cable_channel_x_depth
    cav_wedge_y_low  = cable_y_center + cable_y_half_h
    cav_wedge_y_high = cav_wedge_y_low + cable_channel_x_depth
    env_wedge = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=slope_z_min_env)
        .moveTo(bag_x, env_wedge_y_low)
        .lineTo(bag_x + s * cable_channel_x_depth, env_wedge_y_low)
        .lineTo(bag_x, env_wedge_y_high)
        .close()
        .extrude(slope_z_max - slope_z_min_env)
    )
    cav_wedge = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=slope_z_min_cav)
        .moveTo(bag_x, cav_wedge_y_low)
        .lineTo(bag_x + s * cable_channel_x_depth, cav_wedge_y_low)
        .lineTo(bag_x, cav_wedge_y_high)
        .close()
        .extrude(slope_z_max - slope_z_min_cav)
    )
    horiz_envelope = horiz_envelope.union(env_wedge)
    horiz_cavity = horiz_cavity.union(cav_wedge)

    # Corner wedge — extends the channel envelope around the bag-pocket
    # wall's +Z outer corner arc so the channel-outer face meets the
    # wall continuously (no foam-pour gap behind the corner). Cut back
    # in the cable's y range by cut_reed_channel_openings.
    R_outer_corner = bag_pocket_corner_inner_radius + W
    corner_arc_endpoint_x = s * (
        bag_pocket_outermost_x - W - bag_pocket_corner_inner_radius
    )
    z_outer = bag_pocket_width / 2
    z_corner_start = z_outer - W - bag_pocket_corner_inner_radius
    y_min_env = cable_y_center - cable_y_half_h - W
    y_max_env = cable_y_center + cable_y_half_h + W
    corner_wedge = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=y_min_env)
        .moveTo(bag_x, -z_corner_start)
        .radiusArc((corner_arc_endpoint_x, -z_outer), s * R_outer_corner)
        .lineTo(bag_x, -z_outer)
        .close()
        .extrude(y_max_env - y_min_env)
    )

    return (
        vert_envelope.union(horiz_envelope).union(corner_wedge)
        .cut(vert_cavity).cut(horiz_cavity)
    )


def cut_reed_channel_openings(foam_shell):
    """Cut the bag-pocket far ±X wall in the reed-and-cable channel
    footprint, so each channel is open to the bag pocket interior on
    its back face. Two payoffs:

    - Shortens the magnet-to-reed magnetic path (removes the 2 mm
      bag-pocket wall PETG between the magnet inside the reservoir
      and the reed sensors in the foam-zone channel).
    - Makes the channels accessible / inspectable from the bag-pocket
      side.

    Foam-pour safety is unaffected: the cut is on the bag-pocket-inner
    side; foam lives only in the foam zone outboard of the channel."""
    W = wall_and_floor_thickness

    def make_box(x_a, x_b, y_min, y_max, z_a, z_b):
        x_min, x_max = min(x_a, x_b), max(x_a, x_b)
        z_min, z_max = min(z_a, z_b), max(z_a, z_b)
        return (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=y_min)
            .moveTo((x_min + x_max) / 2, -(z_min + z_max) / 2)
            .rect(x_max - x_min, z_max - z_min)
            .extrude(y_max - y_min)
        )

    for s in (+1, -1):
        # Bag-pocket far ±X wall: 2 mm-thick band at x ∈ [outer−W, outer]
        # in the straight section, curving inward along the +Z corner
        # arc up to its terminus at x = ±(outer − W − R).
        wall_x_outer   = s * bag_pocket_outermost_x
        wall_x_inner   = s * (bag_pocket_outermost_x - W)
        corner_x_inner = s * (bag_pocket_outermost_x - W - bag_pocket_corner_inner_radius)

        # Vertical opening: through the wall in the reed channel's
        # footprint (full height).
        vert_opening = make_box(
            wall_x_inner, wall_x_outer,
            cable_y_center - cable_y_half_h, tank_copper_shell_height,
            reed_z_center - reed_z_half_w, reed_z_center + reed_z_half_w,
        )
        foam_shell = foam_shell.cut(vert_opening)

        # Horizontal opening: through the wall (and the corner-arc band
        # material) in the cable channel's y footprint, reaching to
        # z = ±cable_z_max.
        horiz_opening = make_box(
            corner_x_inner, wall_x_outer,
            cable_y_center - cable_y_half_h, cable_y_center + cable_y_half_h,
            reed_z_center - reed_z_half_w, cable_z_max,
        )
        foam_shell = foam_shell.cut(horiz_opening)

        # Slope wall cut: extends the cavity ceiling's 45° slope
        # through the bag-pocket wall — removes the trapezoidal slice
        # of wall material under the slope's continuation. Straight
        # section only (z ≤ cable_z_max − R).
        slope_y_low      = cable_y_center + cable_y_half_h
        slope_y_at_outer = slope_y_low + cable_channel_x_depth
        slope_y_at_inner = slope_y_at_outer + W
        slope_z_min      = reed_z_center - reed_z_half_w
        slope_z_max      = cable_z_max - bag_pocket_corner_inner_radius
        slope_wall_cut = (
            cq.Workplane(xy_plane_z_up)
            .workplane(offset=slope_z_min)
            .moveTo(wall_x_inner, slope_y_low)
            .lineTo(wall_x_outer, slope_y_low)
            .lineTo(wall_x_outer, slope_y_at_outer)
            .lineTo(wall_x_inner, slope_y_at_inner)
            .close()
            .extrude(slope_z_max - slope_z_min)
        )
        foam_shell = foam_shell.cut(slope_wall_cut)

    return foam_shell


cable_hole_offset_from_bulkhead_hole_x = 8.0  # ±X offset of cable hole from bulkhead hole, away from the cold-core centerline. The two ⌀6.5 holes are also separated by 12 mm in y (cable hole at `cable_y_center` = 6, bulkhead at `reservoir_bulkhead_port_y` = 18), so center-to-center distance is ~14 mm — plenty of PETG between them.


def cut_reed_cable_holes(foam_shell):
    """Cut the cable holes — one per reservoir side — through both the
    +Z bag-pocket wall and the +Z outer shell wall, in +Z direction,
    using the same `build_a_hole_punch` pattern as the existing
    bulkhead-tube pass-throughs. The cable hole sits at the same z as
    its side's bulkhead hole, offset in X by `cable_hole_offset_from_
    bulkhead_hole_x` away from the bulkhead hole (toward the +X far
    wall for the +X reservoir, toward the −X far wall for the −X
    reservoir), and at y = `cable_y_center` (= 6, matching the channel
    cavity center) so the cable runs straight from the channel through
    the bag-pocket interior and out the hole — no bend.

    Cable's path: reed column → vertical channel → horizontal channel
    → bag-pocket-wall opening (cut by `cut_reed_channel_openings`,
    making the channels open to the bag-pocket interior) → bag-pocket
    interior, traversing in −X by ~13 mm through the body's dry-side
    empty space (open at z ≥ panel_z_max due to the reservoir body's
    slab cut) → cable hole, in +Z direction → out the front face of
    the cold core, parallel to and ±8 mm offset from (and 12 mm below)
    the bulkhead-tube exit."""
    for s in (+1, -1):
        hole_origin = (
            s * (reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x),
            cable_y_center,
            bag_pocket_width / 2 - 10,
        )
        foam_shell = foam_shell.cut(build_a_hole_punch(origin=hole_origin))
    return foam_shell


def build_full_shell():
    """Assemble the foam shell and cut all its port holes."""
    foam_shell = (
        build_tank_and_bag_pocket_walls()
        .union(build_tank_support_ring())
        .union(build_outer_shell())
        .union(build_reed_channels(side=+1))
        .union(build_reed_channels(side=-1))
    )
    foam_shell = cut_circular_port_holes(foam_shell)
    foam_shell = cut_co2_inlet(foam_shell)
    foam_shell = cut_slot_for_copper_and_water_inlet(foam_shell)
    foam_shell = cut_reed_channel_openings(foam_shell)
    foam_shell = cut_reed_cable_holes(foam_shell)
    return foam_shell


