"""Build the cylindrical tank wall + four bridging walls + two
bag-pocket U-walls as one connected cross-section per ±X side."""

import math
import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    wall_and_floor_thickness,
    tank_copper_shell_radius,
    tank_copper_shell_height,
    bag_pocket_width,
    bag_pocket_depth,
    bag_pocket_corner_inner_radius,
)

tank_copper_shell_open_z = 60.0


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
        """Point on the lobe-arc / bridging circle at angle theta, in
        workplane-local coordinates."""
        cx = side * lobe_cx_abs
        cz = z_sign * lobe_cz_abs
        return (cx + R_lobe * math.cos(theta), -(cz + R_lobe * math.sin(theta)))

    def cavity_loop_midpoint(side, z_sign, theta):
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
        # apex_angle: bridging-arc circle's radius direction pointing
        # toward origin (arc apex). +X side: π; −X side: 0.
        apex_angle = math.pi if side > 0 else 0.0

        outer_solid = (
            cq.Workplane(xz_plane_y_up)
            .moveTo(side * outer_x_abs, -(inner_z_pos - R))
            .lineTo(side * outer_x_abs, +(inner_z_pos - R))
            .radiusArc((side * (inner_x_abs - R), +outer_z_pos), -side * R_pocket_outer)
            .lineTo(side * arc_outer_x_abs, +outer_z_pos)
            .threePointArc(
                outer_loop_midpoint(side, -1, apex_angle),
                (side * cyl_open_x_inner, +tank_copper_shell_open_z),
            )
            .threePointArc(
                (side * R_cyl_inner, 0),
                (side * cyl_open_x_inner, -tank_copper_shell_open_z),
            )
            .threePointArc(
                outer_loop_midpoint(side, +1, apex_angle),
                (side * arc_outer_x_abs, -outer_z_pos),
            )
            .lineTo(side * (inner_x_abs - R), -outer_z_pos)
            .radiusArc((side * outer_x_abs, -(inner_z_pos - R)), -side * R_pocket_outer)
            .close()
            .extrude(bag_pocket_height)
        )
        cavity_solid = (
            cq.Workplane(xz_plane_y_up)
            .moveTo(side * cyl_open_x_outer, -inner_z_pos)
            .lineTo(side * (inner_x_abs - R), -inner_z_pos)
            .radiusArc((side * inner_x_abs, -(inner_z_pos - R)), -side * R)
            .lineTo(side * inner_x_abs, +(inner_z_pos - R))
            .radiusArc((side * (inner_x_abs - R), +inner_z_pos), -side * R)
            .lineTo(side * cyl_open_x_outer, +inner_z_pos)
            .threePointArc(
                cavity_loop_midpoint(side, -1, apex_angle),
                (side * cyl_open_x_outer, +tank_copper_shell_open_z),
            )
            .threePointArc(
                (side * R_cyl_outer, 0),
                (side * cyl_open_x_outer, -tank_copper_shell_open_z),
            )
            .threePointArc(
                cavity_loop_midpoint(side, +1, apex_angle),
                (side * cyl_open_x_outer, -inner_z_pos),
            )
            .close()
            .extrude(bag_pocket_height)
        )
        return outer_solid.cut(cavity_solid)

    return build_side(side=+1).union(build_side(side=-1))
