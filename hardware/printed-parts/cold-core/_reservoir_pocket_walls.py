"""Build the two reservoir pockets — one on each ±X side — as
four-walled enclosures whose centerward wall is curved to clear the
tank+coil envelope. The +X pocket is traced explicitly; the −X pocket
is its mirror across the YZ plane."""

import math
import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_up,
    flip_z,
    wall_and_floor_thickness,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_outermost_x,
)

w = wall_and_floor_thickness

# Z at which the centerward wall hands off from its middle segment
# (the cylindrical arc that wraps the tank+coil envelope) to the
# transition arcs that swing the wall out to the pocket's ±Z walls.
pocket_centerward_arc_transition_z = 60.0


def build_reservoir_pocket_walls():
    """Two reservoir pockets, mirrored across YZ. Built per side as an
    outer-perimeter polyline minus a cavity-perimeter polyline rather
    than a single multi-loop sketch because CadQuery's pending-wire
    heuristic mis-classifies two non-nested outer wires in the same
    workplane as nested ones."""
    height = foam_shell_outer_height

    far_x_outer = bag_pocket_outermost_x
    far_x_inner = far_x_outer - w
    z_outer = pocket_centerward_arc_outer_radius
    z_inner = z_outer - w
    corner_inner_r = bag_pocket_corner_inner_radius
    corner_outer_r = corner_inner_r + w

    # Centerward wall: cavity-side face on the cylinder of radius
    # arc_cavity_r (farther from cold-core axis), tank-side face on the
    # concentric cylinder one wall-thickness inboard.
    arc_cavity_r = pocket_centerward_arc_outer_radius
    arc_tank_r = arc_cavity_r - w
    arc_z = pocket_centerward_arc_transition_z

    middle_tank_x = math.sqrt(arc_tank_r**2 - arc_z**2)
    middle_cavity_x = math.sqrt(arc_cavity_r**2 - arc_z**2)

    # Transition arc: center between the two endpoint circles, on the
    # bisector of the chord between middle-arc handoff and ±Z wall.
    # Tank-side face has radius transition_tank_r; cavity-side face is
    # the concentric circle through the cavity-side handoff.
    transition_tank_r = 8.0
    chord_half_z = (z_inner - arc_z) / 2.0
    transition_center_z = (z_inner + arc_z) / 2.0
    transition_center_x = middle_tank_x + math.sqrt(transition_tank_r**2 - chord_half_z**2)
    transition_cavity_r = math.sqrt(
        (transition_center_x - middle_cavity_x)**2 + chord_half_z**2
    )
    transition_tank_terminus_x = transition_center_x - math.sqrt(
        transition_tank_r**2 - (z_outer - transition_center_z)**2
    )

    def transition_apex(z_sign, r):
        """Apex of the transition arc at z_sign·Z, on the line from its
        center toward the cold-core axis."""
        return (transition_center_x - r, z_sign * transition_center_z)

    # Centerward-wall joints, world coords.
    middle_tank_handoff_plus_z = (middle_tank_x, arc_z)
    middle_tank_handoff_minus_z = (middle_tank_x, -arc_z)
    middle_cavity_handoff_plus_z = (middle_cavity_x, arc_z)
    middle_cavity_handoff_minus_z = (middle_cavity_x, -arc_z)

    # Cavity-side transition terminus sits at middle_cavity_x because
    # the transition's cavity-face circle passes through both middle-
    # arc handoffs by construction.
    transition_tank_terminus_plus_z = (transition_tank_terminus_x, z_outer)
    transition_tank_terminus_minus_z = (transition_tank_terminus_x, -z_outer)
    transition_cavity_terminus_plus_z = (middle_cavity_x, z_inner)
    transition_cavity_terminus_minus_z = (middle_cavity_x, -z_inner)

    # +X far wall: outer face at far_x_outer, cavity face at far_x_inner,
    # both spanning ±(z_inner - corner_inner_r) where corner arcs begin.
    far_wall_outer_plus_z = (far_x_outer, z_inner - corner_inner_r)
    far_wall_outer_minus_z = (far_x_outer, -(z_inner - corner_inner_r))
    far_wall_cavity_plus_z = (far_x_inner, z_inner - corner_inner_r)
    far_wall_cavity_minus_z = (far_x_inner, -(z_inner - corner_inner_r))

    # ±Z wall corner-arc termini. Outer- and cavity-side arcs share an
    # axis at (far_x_inner - corner_inner_r, ±(z_inner - corner_inner_r))
    # — outer at corner_outer_r, cavity at corner_inner_r — so both
    # terminate at the same X.
    side_wall_outer_plus_z = (far_x_inner - corner_inner_r, z_outer)
    side_wall_outer_minus_z = (far_x_inner - corner_inner_r, -z_outer)
    side_wall_cavity_plus_z = (far_x_inner - corner_inner_r, z_inner)
    side_wall_cavity_minus_z = (far_x_inner - corner_inner_r, -z_inner)

    outer_perimeter = (
        cq.Workplane(xz_plane_y_up)
        .moveTo(*flip_z(far_wall_outer_plus_z))
        .lineTo(*flip_z(far_wall_outer_minus_z))
        .radiusArc(flip_z(side_wall_outer_minus_z), -corner_outer_r)
        .lineTo(*flip_z(transition_tank_terminus_minus_z))
        .threePointArc(flip_z(transition_apex(-1, transition_tank_r)), flip_z(middle_tank_handoff_minus_z))
        .threePointArc(flip_z((arc_tank_r, 0)), flip_z(middle_tank_handoff_plus_z))
        .threePointArc(flip_z(transition_apex(+1, transition_tank_r)), flip_z(transition_tank_terminus_plus_z))
        .lineTo(*flip_z(side_wall_outer_plus_z))
        .radiusArc(flip_z(far_wall_outer_plus_z), -corner_outer_r)
        .close()
        .extrude(height)
    )

    cavity_perimeter = (
        cq.Workplane(xz_plane_y_up)
        .moveTo(*flip_z(transition_cavity_terminus_plus_z))
        .lineTo(*flip_z(side_wall_cavity_plus_z))
        .radiusArc(flip_z(far_wall_cavity_plus_z), -corner_inner_r)
        .lineTo(*flip_z(far_wall_cavity_minus_z))
        .radiusArc(flip_z(side_wall_cavity_minus_z), -corner_inner_r)
        .lineTo(*flip_z(transition_cavity_terminus_minus_z))
        .threePointArc(flip_z(transition_apex(-1, transition_cavity_r)), flip_z(middle_cavity_handoff_minus_z))
        .threePointArc(flip_z((arc_cavity_r, 0)), flip_z(middle_cavity_handoff_plus_z))
        .threePointArc(flip_z(transition_apex(+1, transition_cavity_r)), flip_z(transition_cavity_terminus_plus_z))
        .close()
        .extrude(height)
    )

    plus_x_pocket = outer_perimeter.cut(cavity_perimeter)
    return plus_x_pocket.union(plus_x_pocket.mirror("YZ"))
