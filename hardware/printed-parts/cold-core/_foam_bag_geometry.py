"""Shared geometry for the foam shell and the foam-cap stack. Imported
by the two sibling generators (foam-shell/, foam-cap/), each of which
writes the STEPs for its own folder. Constants and build functions live
here so both generators produce a coherent set of mating parts. (File
and function names still carry the "foam_bag" prefix from when
reservoirs were flexible bags — left as-is to avoid a sweeping rename;
only the visible part name has moved to "foam-shell".)"""

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
# All structural walls and floors are 1 mm thick. Earlier 1 mm prints of
# the full-size shell deformed mid-print; we initially attributed that to
# inadequate wall thickness and bumped to 2 mm. The 2 mm version printed
# cleanly with the chamber-exhaust fix in place, which suggested the
# original failures were chamber heat soak, not wall strength — so we're
# back at 1 mm to confirm. Outer dimensions of every component are
# refactored below so that wall-thickness growth is *added* to the outer
# envelope rather than absorbed from inner buffers, foam gaps, bag
# pocket cavities, etc.
wall_and_floor_thickness = 1.0
# Reference wall thickness used in the original 1 mm design. Outer-
# dimension formulas use (wall_and_floor_thickness - reference_wall_thickness)
# as a compensation term, so 1 mm walls reproduce the original geometry
# exactly and 2 mm walls grow each affected outer dimension by 1 mm.
reference_wall_thickness = 1.0
wall_thickness_compensation = wall_and_floor_thickness - reference_wall_thickness
hole_shift_from_edge = 15.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank copper shell
# -------------------------------------------------------
#
# Tank copper shell radius. The +compensation term keeps the inner face
# of the shell wall (where the copper coil sits) at radius 69.5 regardless
# of wall thickness, preserving the 6 mm coil buffer.
tank_outer_radius = 63.5
# Bumped from 7 to 8 mm so the actual radial clearance between the tank
# (R=63.5) and the inner shell face is 7 mm (with 2 mm walls), enough
# for 1/4" ACR copper coil + thermal tape + assembly slack.
copper_coil_buffer_radius = 8.0
tank_copper_shell_radius = tank_outer_radius + copper_coil_buffer_radius + wall_thickness_compensation
#
# Tank copper shell height. The +compensation term keeps the interior
# Y cavity at the original 211.4 mm regardless of floor thickness.
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = (
    tank_height + below_tank_elbows_height + above_tank_elbows_height
    + wall_thickness_compensation
)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank support wedge
# -------------------------------------------------------
#
tank_support_wedge_height = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Bag pocket
# -------------------------------------------------------
#
# bag_pocket_width tracks tank_copper_shell_radius automatically, so the
# bag-pocket Z interior cavity (= width − 2 × wall) stays at 139 mm. The
# bag_pocket_depth gets +2*compensation so the X interior cavity stays
# at 33 mm regardless of wall thickness.
bag_pocket_width = tank_copper_shell_radius * 2
bag_pocket_depth = 35 + 2 * wall_thickness_compensation
#
# -------------------------------------------------------


# -------------------------------------------------------
# Outer shell
# -------------------------------------------------------
#
outer_shell_foam_gap = 16.0
# Outer wall is the same 2 mm as the rest of the assembly now. Kept as
# its own constant in case the inner/outer split is ever needed again.
outer_shell_wall_thickness = wall_and_floor_thickness
#
# Outer footprint shared by the outer shell, the foam cap, and the foam
# cap lid. Defined at module level so changing outer_shell_wall_thickness
# updates all three together (they must remain coplanar at the corners
# so the pin bosses line up).
bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + outer_shell_wall_thickness)
outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + outer_shell_wall_thickness)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap (top/bottom 16 mm foam pour tray, printed twice)
# -------------------------------------------------------
#
# Foam cap outer height. The +compensation term keeps the cap's interior
# Y cavity (= foam thickness in the cap) at 15 mm regardless of floor
# thickness.
foam_cap_height = 16.0 + wall_thickness_compensation
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
# the condensation/frost concern documented in
# reservoir/README.md.
#
# Standard SHCS chosen instead of the McMaster ULH used in touch-
# flo-mounting-plate: there's no flush-mount constraint here (the
# heads protrude on the appliance top and bottom faces; under-
# counter install hides both), and standard DIN 912 SHCS is roughly
# an order of magnitude cheaper Prime-shippable than McMaster ULH.
#
# Stack-up under the head, top cap (mm):
#   lid (1) + cap floor (1) + cap interior void / boss height (14)
#   + cap mating edge (1) + gasket (2)         = 19 mm
# Plus 4 mm engagement into the insert = 23 mm. M3 × 25 rounds up
# with 2 mm slack into the pocket relief below the insert.
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
def build_tank_copper_shell():

    shell = (
        cq.Workplane(xz_plane_y_up)
        .circle(tank_copper_shell_radius)
        .extrude(tank_copper_shell_height)
    )
    shell = shell.faces(">Y").shell(-wall_and_floor_thickness)
    # Cut the cylindrical wall off above z = +tank_copper_shell_open_z
    # and below z = −tank_copper_shell_open_z, so the wall no longer
    # wraps all the way around at +Z and −Z.
    cut_plus_z = (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(0, 0,  tank_copper_shell_open_z), offset= tank_copper_shell_open_z)
        .rect(500, 500)
        .extrude(500)
    )
    cut_minus_z = (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=(0, 0, -tank_copper_shell_open_z), offset=-tank_copper_shell_open_z)
        .rect(500, 500)
        .extrude(-500)
    )
    shell = shell.cut(cut_plus_z).cut(cut_minus_z)

    # Close each of the four open ends with a curved wall that is
    # convex toward the tank/copper cavity (origin side) and concave
    # toward the flavor-reservoir bag-pocket side.  Each wall connects
    # the cylinder's open end at (x_sign · cylinder_open_x,  z_sign ·
    # tank_copper_shell_open_z) to the bag_pocket_support_shell ±Z
    # wall's inner face at (x_sign · cylinder_open_x,  z_sign · (R −
    # wall_and_floor_thickness)).
    #
    # The wall's tank-facing face is an arc of radius
    # tank_copper_open_end_wall_arc_radius (default 6.5 mm) bulging
    # toward the origin; its reservoir-facing face is a concentric arc
    # of radius (arc_radius − wall_and_floor_thickness) so the wall is
    # `wall_and_floor_thickness` thick along the radial direction
    # (slightly thicker in pure-X measure at the chord ends — the
    # outer arc and inner arc meet the z = z_near and z = z_far lines
    # at different x).
    tank_copper_open_end_wall_arc_radius = 6.5
    # The cylinder's wall occupies the radial band R ∈ [R−t, R] (inner
    # face to outer face).  At z = ±tank_copper_shell_open_z, that band
    # projects to x ∈ [cyl_open_x_inner, cyl_open_x_outer] in absolute
    # value, so we anchor the wall's tank-facing arc at the cylinder's
    # inner face and its reservoir-facing arc at the cylinder's outer
    # face.  The wall's chord-end x range then lines up exactly with
    # the cylinder's wall band and the two pieces share a 2-D face at
    # z = ±60 (not just a 1-D edge), so OCCT's boolean union merges
    # them into a single solid without any z-overlap fudge.
    cyl_open_x_outer = math.sqrt(
        tank_copper_shell_radius ** 2 - tank_copper_shell_open_z ** 2
    )
    cyl_open_x_inner = math.sqrt(
        (tank_copper_shell_radius - wall_and_floor_thickness) ** 2
        - tank_copper_shell_open_z ** 2
    )
    z_meet_wall = tank_copper_shell_radius - wall_and_floor_thickness
    R_outer = tank_copper_open_end_wall_arc_radius
    for x_sign in (1, -1):
        for z_sign in (1, -1):
            outer_anchor_x = x_sign * cyl_open_x_inner   # ±37.02
            inner_anchor_x = x_sign * cyl_open_x_outer   # ±38.89
            z_near = z_sign * tank_copper_shell_open_z   # ±60
            z_far  = z_sign * z_meet_wall                # ±70.5
            z_mid  = (z_near + z_far) / 2.0
            half_chord = abs(z_far - z_near) / 2.0
            # Outer (tank-facing) arc center sits on the chord's
            # perpendicular bisector, offset toward +X (for +X walls)
            # so the arc bulges toward origin.
            d_outer = math.sqrt(R_outer ** 2 - half_chord ** 2)
            center_x = outer_anchor_x + x_sign * d_outer
            # Inner (reservoir-facing) arc shares that center; its
            # radius is set by the cylinder's wall thickness (its
            # endpoint at z_near/z_far must hit inner_anchor_x).
            d_inner = abs(inner_anchor_x - center_x)
            R_inner = math.sqrt(d_inner ** 2 + half_chord ** 2)
            outer_apex_x = center_x - x_sign * R_outer
            inner_apex_x = center_x - x_sign * R_inner
            profile = (
                cq.Workplane(xz_plane_y_up)
                .moveTo(outer_anchor_x, -z_near)
                .threePointArc((outer_apex_x, -z_mid), (outer_anchor_x, -z_far))
                .lineTo       (inner_anchor_x, -z_far)
                .threePointArc((inner_apex_x, -z_mid), (inner_anchor_x, -z_near))
                .close()
                .extrude(tank_copper_shell_height)
            )
            shell = shell.union(profile)

    return shell

def build_bag_pocket_support_shell():
    """
    Floor + +Z wall + −Z wall. No +X / −X walls.

    The omitted ±X walls would be coincident with the bag pockets'
    centerward walls (also omitted, in build_a_bag_pocket_shell) and
    would have air on both sides — bag cavity inside, corner-pocket
    air outside — so they aren't earning their 1 mm of PETG.

    The +Z and −Z walls *are* doing real work: they separate corner-
    pocket air (between this shell's interior and the round cup's
    outside) from outer-pour foam (outside this shell at +Z and −Z).
    Without them, foam would invade the corner pocket and reach the
    bag through the open centerward face.
    """
    side_length = 2 * tank_copper_shell_radius

    floor = (
        cq.Workplane(xz_plane_y_up)
        .rect(side_length, side_length)
        .extrude(wall_and_floor_thickness)
    )

    # The ±Z walls now have a central gap in X — the strip directly
    # above (and below) the cylinder's open ends.  Width of the gap
    # at the wall's inner face matches the cylinder's inner-cavity
    # opening at the cut plane (2 · sqrt((R−t)² − tank_copper_shell_open_z²)),
    # leaving two outboard segments that still attach to the curved
    # lobe walls' tops on the ±X sides.  At each of the four gap corners
    # an additional curved sliver is cut so the wall's inner edge
    # follows the lobe walls' outer (tank-facing) arc through the
    # wall's z range, blending with the curve instead of meeting it
    # at a sharp right angle.
    cyl_open_x_inner = math.sqrt(
        (tank_copper_shell_radius - wall_and_floor_thickness) ** 2
        - tank_copper_shell_open_z ** 2
    )
    segment_length = side_length / 2 - cyl_open_x_inner
    segment_center_x = cyl_open_x_inner + segment_length / 2

    def build_z_wall_segment(z_sign, x_sign):
        z_pos = z_sign * (side_length / 2 - wall_and_floor_thickness / 2)
        return (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(x_sign * segment_center_x, 0, z_pos))
            .rect(segment_length, wall_and_floor_thickness)
            .extrude(tank_copper_shell_height)
        )

    # Lobe-arc geometry (mirrors build_tank_copper_shell's tank_copper_
    # open_end_wall_arc_radius and derived values — kept local instead
    # of imported so this helper has no cross-function dependency).
    R_lobe_arc = 6.5
    z_meet_wall = tank_copper_shell_radius - wall_and_floor_thickness    # 70.5
    half_chord  = (z_meet_wall - tank_copper_shell_open_z) / 2.0          # 5.25
    d_lobe_arc  = math.sqrt(R_lobe_arc ** 2 - half_chord ** 2)            # 3.83
    lobe_arc_center_x = cyl_open_x_inner + d_lobe_arc                     # 40.85
    lobe_arc_center_z = (z_meet_wall + tank_copper_shell_open_z) / 2.0    # 65.25
    wall_outer_z = tank_copper_shell_radius                                # 71.5

    def build_corner_blend_cut(z_sign, x_sign):
        inner_x = x_sign * cyl_open_x_inner
        z_inner = z_sign * z_meet_wall
        z_outer = z_sign * wall_outer_z
        cx = x_sign * lobe_arc_center_x
        cz = z_sign * lobe_arc_center_z
        dz = z_outer - cz
        arc_outer_x = cx - x_sign * math.sqrt(R_lobe_arc ** 2 - dz ** 2)
        a1 = math.atan2(z_inner - cz, inner_x       - cx)
        a2 = math.atan2(z_outer - cz, arc_outer_x  - cx)
        a_mid = (a1 + a2) / 2.0
        arc_mid_x = cx + R_lobe_arc * math.cos(a_mid)
        arc_mid_z = cz + R_lobe_arc * math.sin(a_mid)
        return (
            cq.Workplane(xz_plane_y_up)
            .moveTo(inner_x,      -z_inner)
            .lineTo(inner_x,      -z_outer)
            .lineTo(arc_outer_x,  -z_outer)
            .threePointArc((arc_mid_x, -arc_mid_z), (inner_x, -z_inner))
            .close()
            .extrude(tank_copper_shell_height)
        )

    shell = (
        floor
        .union(build_z_wall_segment(z_sign= 1, x_sign= 1))
        .union(build_z_wall_segment(z_sign= 1, x_sign=-1))
        .union(build_z_wall_segment(z_sign=-1, x_sign= 1))
        .union(build_z_wall_segment(z_sign=-1, x_sign=-1))
    )
    for z_sign in (1, -1):
        for x_sign in (1, -1):
            shell = shell.cut(build_corner_blend_cut(z_sign, x_sign))
    return shell

def build_tank_support_wedge():
    support_wedge_outer_radius = tank_copper_shell_radius - wall_and_floor_thickness
    support_wedge_ring_width = 9
    support_wedge_inner_radius = support_wedge_outer_radius - support_wedge_ring_width
    support_wedge_bottom_y = wall_and_floor_thickness
    filled_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_outer_radius)
        .extrude(tank_support_wedge_height)
    )
    cut_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_inner_radius)
        .extrude(tank_support_wedge_height)
    )
    ring = filled_cylinder.cut(cut_cylinder)
    # Recover ~3% thermal loss from removing the cone: 4 angular slots cut
    # through the ring at 45°/135°/225°/315°, 30° wide each. Leaves four
    # 60° support segments aligned with the cardinal axes.
    slot_radial_margin = 1.0
    slot_inner_radius = support_wedge_inner_radius - slot_radial_margin
    slot_outer_radius = support_wedge_outer_radius + slot_radial_margin
    slot_half_width = math.radians(15)
    for i in range(4):
        center_angle = math.radians(45 + 90 * i)
        a1 = center_angle - slot_half_width
        a2 = center_angle + slot_half_width
        p1 = (slot_inner_radius * math.cos(a1), slot_inner_radius * math.sin(a1))
        p2 = (slot_outer_radius * math.cos(a1), slot_outer_radius * math.sin(a1))
        p3 = (slot_outer_radius * math.cos(a2), slot_outer_radius * math.sin(a2))
        p4 = (slot_inner_radius * math.cos(a2), slot_inner_radius * math.sin(a2))
        slot = (
            cq.Workplane(xz_plane_y_up)
            .workplane(offset=support_wedge_bottom_y)
            .moveTo(*p1).lineTo(*p2).lineTo(*p3).lineTo(*p4).close()
            .extrude(tank_support_wedge_height)
        )
        ring = ring.cut(slot)
    return ring

def build_a_bag_pocket_shell(side=1):
    """
    Floor + far wall + +Z wall + −Z wall. No centerward (toward-tank)
    wall.

    The omitted centerward wall would be coincident with the
    bag_pocket_support_shell's matching ±X wall (also omitted) and
    would have air on both sides — bag cavity inside, corner-pocket
    air outside — so it isn't earning its 1 mm of PETG. Result: the
    bag cavity opens along its centerward face into the support
    shell's interior, becoming one continuous air volume.

    side=+1 builds the +X bag pocket; side=−1 builds the −X side
    (everything mirrored).
    """
    bag_pocket_height = tank_copper_shell_height
    bag_pocket_x_center = (
        tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    ) * side
    half_depth = bag_pocket_depth / 2
    half_width = bag_pocket_width / 2

    floor = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(bag_pocket_x_center, 0, 0))
        .rect(bag_pocket_depth, bag_pocket_width)
        .extrude(wall_and_floor_thickness)
    )

    # Far wall: at the +X face of the +X bag pocket (or the −X face of
    # the −X bag pocket). Sits 1 mm inside the pocket's outer extent
    # along the radial-out direction.
    far_wall = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(
            bag_pocket_x_center + side * (half_depth - wall_and_floor_thickness / 2),
            0,
            0,
        ))
        .rect(wall_and_floor_thickness, bag_pocket_width)
        .extrude(bag_pocket_height)
    )

    def build_z_wall(z_sign):
        z_pos = z_sign * (half_width - wall_and_floor_thickness / 2)
        return (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(bag_pocket_x_center, 0, z_pos))
            .rect(bag_pocket_depth, wall_and_floor_thickness)
            .extrude(bag_pocket_height)
        )

    return (
        floor
        .union(far_wall)
        .union(build_z_wall(z_sign=1))
        .union(build_z_wall(z_sign=-1))
    )

def punch_a_bag_pocket_shell_hole(foam_bag_shell, side=1):

    # Bag pocket offset
    bag_pocket_x_offset = tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    bag_pocket_x_offset *= side

    # Hole offset
    hole_z_offset = bag_pocket_width / 2 - 10
    hole_x_offset = bag_pocket_x_offset
    # y must match the reservoir's bulkhead port_position_y so the dry-side
    # tube exits straight without bending. The reservoir bumps port_position_y
    # to 17 to keep 4 mm of PETG under the bulkhead's flange chamber; this
    # hole follows. The CO2 and water inlets (which use hole_shift_from_edge
    # directly) are not affected.
    hole_y_offset = 17

    # Hole
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))

    return foam_bag_shell.cut(hole_punch)

def build_outer_shell():
    shell = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-outer_shell_wall_thickness)
    )
    for (boss_x, boss_z) in foam_cap_attachment_xz_positions:
        boss = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(boss_x, 0, boss_z), offset=0)
            .rect(screw_boss_size, screw_boss_size)
            .extrude(tank_copper_shell_height)
        )
        shell = shell.union(boss)
        # Heat-set insert pockets, one drilled DOWN from the top face
        # and one drilled UP from the bottom face. Top pocket accepts
        # the top-cap screw threading down from above; bottom pocket
        # accepts the bottom-cap screw threading up from below.
        top_pocket = (
            cq.Workplane(xz_plane_y_up)
            .workplane(
                origin=(boss_x, tank_copper_shell_height - insert_pocket_depth, boss_z),
                offset=tank_copper_shell_height - insert_pocket_depth,
            )
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth)
        )
        bottom_pocket = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(boss_x, 0, boss_z), offset=0)
            .circle(insert_pocket_radius)
            .extrude(insert_pocket_depth)
        )
        shell = shell.cut(top_pocket).cut(bottom_pocket)
    return shell

def build_foam_cap():
    cap = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    for (boss_x, boss_z) in foam_cap_attachment_xz_positions:
        boss = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(boss_x, 0, boss_z), offset=0)
            .rect(screw_boss_size, screw_boss_size)
            .extrude(foam_cap_height)
        )
        cap = cap.union(boss)
        # Screw clearance hole through the full boss height, so the
        # screw can pass from the cap floor (top in service) all the
        # way to the cap's mating edge (bottom in service).
        clearance = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(boss_x, 0, boss_z), offset=0)
            .circle(screw_clearance_radius)
            .extrude(foam_cap_height)
        )
        cap = cap.cut(clearance)
    return cap

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

    for (boss_x, boss_z) in foam_cap_attachment_xz_positions:
        clearance = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(boss_x, 0, boss_z), offset=0)
            .circle(screw_clearance_radius)
            .extrude(wall_and_floor_thickness * 3)
        )
        lid = lid.cut(clearance)

    return lid

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

    # Add 8 × 8 mm pads at each screw position, matching the cap and
    # outer_shell boss footprints. At corner screws, the pad extends
    # 3 mm inward beyond the perimeter ring on both axes; at mid-
    # long-side screws, 3 mm inward on the wall-perpendicular axis.
    for (pad_x, pad_z) in foam_cap_attachment_xz_positions:
        pad = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(pad_x, 0, pad_z), offset=0)
            .rect(screw_boss_size, screw_boss_size)
            .extrude(gasket_thickness)
        )
        gasket = gasket.union(pad)

    # Cut screw holes AFTER unioning the pads, so each hole sits at
    # the center of an 8 × 8 mm pad surrounded by 4 mm of TPU.
    for (hole_x, hole_z) in foam_cap_attachment_xz_positions:
        hole = (
            cq.Workplane(xz_plane_y_up)
            .workplane(origin=(hole_x, 0, hole_z), offset=0)
            .circle(screw_clearance_radius)
            .extrude(gasket_thickness)
        )
        gasket = gasket.cut(hole)

    return gasket

def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
    hole_punch_height=40,
):
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )

def cut_hole_for_co2_inlet(foam_bag_shell):
    hole_z_offset = (tank_copper_shell_radius + 20) * -1
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_hole_for_water_outlet(foam_bag_shell):
    hole_z_offset = tank_copper_shell_radius - 20
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

# ═══════════════════════════════════════════════════════
# TOP-LEVEL ASSEMBLY
# ═══════════════════════════════════════════════════════

def build_full_shell():
    """Assemble the foam shell and cut its three port holes."""
    tank_copper_shell = build_tank_copper_shell()
    tank_support_wedge = build_tank_support_wedge()
    bag_pocket_support_shell = build_bag_pocket_support_shell()
    bag_pocket_shell = build_a_bag_pocket_shell()
    bag_pocket_shell_2 = build_a_bag_pocket_shell(side=-1)
    outer_shell = build_outer_shell()
    foam_bag_shell = (
        tank_copper_shell
        .union(tank_support_wedge)
        .union(bag_pocket_support_shell)
        .union(bag_pocket_shell)
        .union(bag_pocket_shell_2)
        .union(outer_shell)
    )
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell)
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell, side=-1)
    foam_bag_shell = cut_hole_for_co2_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_outlet(foam_bag_shell)
    return foam_bag_shell


def build_foam_cap_solid():
    """build_foam_cap() returns a shell; unioning with itself converts
    it into a solid (a CadQuery quirk we'd otherwise have to remember
    at every call site)."""
    cap = build_foam_cap()
    return cap.union(cap)
