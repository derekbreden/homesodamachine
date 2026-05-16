"""Build the two reservoir pockets — one on each ±X side — as
four-walled enclosures whose centerward wall is curved to clear the
tank+coil envelope. The +X pocket is traced explicitly; the −X pocket
is its mirror across the YZ plane."""

import math
import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    wall_and_floor_thickness,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_outermost_x,
)

# Z at which the centerward wall hands off from its middle segment
# (the cylindrical arc that wraps the tank+coil envelope) to the
# transition arcs that swing the wall out to the pocket's ±Z walls.
pocket_centerward_arc_transition_z = 60.0


def build_reservoir_pocket_walls():
    """Two reservoir pockets, mirrored across YZ. Each pocket has four
    walls: a far ±X wall, ±Z walls, and a curved centerward wall. The
    centerward wall is the only curved one — its outer face traces
    three arc segments (middle + two transitions) that together swing
    around the tank+coil envelope and join smoothly to the ±Z walls.

    Built per side as an outer-perimeter polyline extruded, with a
    cavity-perimeter polyline extruded and cut from it. Done as
    outer-extrude minus cavity-extrude rather than a single multi-loop
    sketch because CadQuery's pending-wire heuristic mis-classifies
    two non-nested outer wires in the same workplane as nested ones."""
    W = wall_and_floor_thickness
    height = foam_shell_outer_height

    far_x_outer = bag_pocket_outermost_x
    far_x_inner = far_x_outer - W
    z_outer = pocket_centerward_arc_outer_radius
    z_inner = z_outer - W
    corner_inner_R = bag_pocket_corner_inner_radius
    corner_outer_R = corner_inner_R + W

    # Centerward wall geometry. The wall's cavity-side face (the side
    # facing the pocket interior, farther from the cold-core axis)
    # rides on the cylinder of radius arc_cavity_R. The wall's tank-
    # side face (the side facing the tank+coil, closer to the axis)
    # rides on the concentric cylinder one wall-thickness inboard.
    arc_cavity_R = pocket_centerward_arc_outer_radius
    arc_tank_R   = arc_cavity_R - W
    arc_z        = pocket_centerward_arc_transition_z

    # X positions where the middle cylindrical arc hands off to each
    # transition arc, one position per wall face.
    middle_tank_x   = math.sqrt(arc_tank_R**2 - arc_z**2)
    middle_cavity_x = math.sqrt(arc_cavity_R**2 - arc_z**2)

    # Each transition arc has its center between the two endpoint
    # circles, on the bisector of the chord between (middle_tank_x,
    # arc_z) and (transition_x, z_inner). The tank-side face of the
    # transition is a circle of radius transition_tank_R; the cavity-
    # side face is the concentric circle that passes through
    # (middle_cavity_x, arc_z).
    transition_tank_R   = 8.0
    chord_half_z        = (z_inner - arc_z) / 2.0
    transition_center_z = (z_inner + arc_z) / 2.0
    transition_center_x = middle_tank_x + math.sqrt(transition_tank_R**2 - chord_half_z**2)
    transition_cavity_R = math.sqrt(
        (transition_center_x - middle_cavity_x) ** 2 + chord_half_z ** 2
    )
    # X at which the transition arc's tank-side face hits the ±Z wall.
    transition_x = transition_center_x - math.sqrt(
        transition_tank_R**2 - (z_outer - transition_center_z) ** 2
    )

    def transition_apex(z_sign, R):
        """Apex (workplane-local x, y) of the transition arc at z_sign·Z,
        lying on the line from its center toward the cold-core axis.
        Workplane convention: local Y = −world Z."""
        return (transition_center_x - R, -(z_sign * transition_center_z))

    outer_perimeter = (
        cq.Workplane(xz_plane_y_up)
        # +X far wall outboard face.
        .moveTo(far_x_outer, -(z_inner - corner_inner_R))
        .lineTo(far_x_outer, +(z_inner - corner_inner_R))
        # −Z far-corner outboard arc.
        .radiusArc((far_x_inner - corner_inner_R, +z_outer), -corner_outer_R)
        # −Z wall outboard face.
        .lineTo(transition_x, +z_outer)
        # −Z transition arc, middle arc, +Z transition arc — the three
        # segments of the centerward wall's tank-side face.
        .threePointArc(transition_apex(-1, transition_tank_R),
                       (middle_tank_x, +arc_z))
        .threePointArc((arc_tank_R, 0),
                       (middle_tank_x, -arc_z))
        .threePointArc(transition_apex(+1, transition_tank_R),
                       (transition_x, -z_outer))
        # +Z wall outboard face.
        .lineTo(far_x_inner - corner_inner_R, -z_outer)
        # +Z far-corner outboard arc, closes back to start.
        .radiusArc((far_x_outer, -(z_inner - corner_inner_R)), -corner_outer_R)
        .close()
        .extrude(height)
    )

    cavity_perimeter = (
        cq.Workplane(xz_plane_y_up)
        # +X far wall cavity face + ±Z cavity faces + filleted corners.
        .moveTo(middle_cavity_x, -z_inner)
        .lineTo(far_x_inner - corner_inner_R, -z_inner)
        .radiusArc((far_x_inner, -(z_inner - corner_inner_R)), -corner_inner_R)
        .lineTo(far_x_inner, +(z_inner - corner_inner_R))
        .radiusArc((far_x_inner - corner_inner_R, +z_inner), -corner_inner_R)
        .lineTo(middle_cavity_x, +z_inner)
        # Centerward wall's cavity-side face: −Z transition, middle, +Z
        # transition. Concentric with the tank-side arcs, slightly
        # different radii.
        .threePointArc(transition_apex(-1, transition_cavity_R),
                       (middle_cavity_x, +arc_z))
        .threePointArc((arc_cavity_R, 0),
                       (middle_cavity_x, -arc_z))
        .threePointArc(transition_apex(+1, transition_cavity_R),
                       (middle_cavity_x, -z_inner))
        .close()
        .extrude(height)
    )

    plus_x_pocket = outer_perimeter.cut(cavity_perimeter)
    return plus_x_pocket.union(plus_x_pocket.mirror("YZ"))
