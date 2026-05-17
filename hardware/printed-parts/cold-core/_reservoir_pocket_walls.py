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

w = wall_and_floor_thickness

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
    height = foam_shell_outer_height

    far_x_outer = bag_pocket_outermost_x
    far_x_inner = far_x_outer - w
    z_outer = pocket_centerward_arc_outer_radius
    z_inner = z_outer - w
    corner_inner_r = bag_pocket_corner_inner_radius
    corner_outer_r = corner_inner_r + w

    # Centerward wall geometry. The wall's cavity-side face (the side
    # facing the pocket interior, farther from the cold-core axis)
    # rides on the cylinder of radius arc_cavity_r. The wall's tank-
    # side face (the side facing the tank+coil, closer to the axis)
    # rides on the concentric cylinder one wall-thickness inboard.
    arc_cavity_r = pocket_centerward_arc_outer_radius
    arc_tank_r = arc_cavity_r - w
    arc_z = pocket_centerward_arc_transition_z

    # X positions where the middle cylindrical arc hands off to each
    # transition arc, one position per wall face.
    middle_tank_x = math.sqrt(arc_tank_r**2 - arc_z**2)
    middle_cavity_x = math.sqrt(arc_cavity_r**2 - arc_z**2)

    # Each transition arc has its center between the two endpoint
    # circles, on the bisector of the chord between the middle-arc
    # handoff and the ±Z wall. The tank-side face of the transition is
    # a circle of radius transition_tank_r; the cavity-side face is the
    # concentric circle that passes through the cavity-side handoff.
    transition_tank_r = 8.0
    chord_half_z = (z_inner - arc_z) / 2.0
    transition_center_z = (z_inner + arc_z) / 2.0
    transition_center_x = middle_tank_x + math.sqrt(transition_tank_r**2 - chord_half_z**2)
    transition_cavity_r = math.sqrt(
        (transition_center_x - middle_cavity_x) ** 2 + chord_half_z ** 2
    )
    # X at which the transition arc's tank-side face hits the ±Z wall.
    transition_tank_terminus_x = transition_center_x - math.sqrt(
        transition_tank_r**2 - (z_outer - transition_center_z) ** 2
    )

    def transition_apex(z_sign, r):
        """Apex (workplane-local x, y) of the transition arc at z_sign·Z,
        lying on the line from its center toward the cold-core axis.
        Workplane convention: local Y = −world Z."""
        return (transition_center_x - r, -(z_sign * transition_center_z))

    # Joints where the centerward wall's middle arc hands off to the
    # ±Z transition arc, per face. The two faces share the math (same
    # arc_z, different radii) — naming each joint surfaces that.
    middle_tank_handoff_plus_z = (middle_tank_x, -arc_z)
    middle_tank_handoff_minus_z = (middle_tank_x, +arc_z)
    middle_cavity_handoff_plus_z = (middle_cavity_x, -arc_z)
    middle_cavity_handoff_minus_z = (middle_cavity_x, +arc_z)

    # Where the ±Z transition arc terminates at the ±Z wall, per face.
    # Tank-side terminus is offset in X (computed); cavity-side
    # terminus sits at middle_cavity_x (the transition's cavity-face
    # circle passes through both middle-arc handoffs by construction).
    transition_tank_terminus_plus_z = (transition_tank_terminus_x, -z_outer)
    transition_tank_terminus_minus_z = (transition_tank_terminus_x, +z_outer)
    transition_cavity_terminus_plus_z = (middle_cavity_x, -z_inner)
    transition_cavity_terminus_minus_z = (middle_cavity_x, +z_inner)

    # +X far wall endpoints. The outer face spans z_inner ± corner
    # tangent; the cavity face is one wall-thickness inboard.
    far_wall_outer_plus_z = (far_x_outer, -(z_inner - corner_inner_r))
    far_wall_outer_minus_z = (far_x_outer, +(z_inner - corner_inner_r))
    far_wall_cavity_plus_z = (far_x_inner, -(z_inner - corner_inner_r))
    far_wall_cavity_minus_z = (far_x_inner, +(z_inner - corner_inner_r))

    # ±Z wall corner-arc termini on the ±Z faces. Outer- and cavity-
    # side arcs share an axis at workplane (far_x_inner - corner_inner_r,
    # ±(z_inner - corner_inner_r)) — outer at corner_outer_r, cavity at
    # corner_inner_r — so both arcs terminate at the same X.
    side_wall_outer_plus_z = (far_x_inner - corner_inner_r, -z_outer)
    side_wall_outer_minus_z = (far_x_inner - corner_inner_r, +z_outer)
    side_wall_cavity_plus_z = (far_x_inner - corner_inner_r, -z_inner)
    side_wall_cavity_minus_z = (far_x_inner - corner_inner_r, +z_inner)

    outer_perimeter = (
        cq.Workplane(xz_plane_y_up)
        # +X far wall outboard face.
        .moveTo(*far_wall_outer_plus_z)
        .lineTo(*far_wall_outer_minus_z)
        # −Z corner arc → −Z wall outboard face → centerward wall's
        # tank-side face (−Z transition + middle + +Z transition) → +Z
        # wall outboard face → +Z corner arc, closes back to start.
        .radiusArc(side_wall_outer_minus_z, -corner_outer_r)
        .lineTo(*transition_tank_terminus_minus_z)
        .threePointArc(transition_apex(-1, transition_tank_r),
                       middle_tank_handoff_minus_z)
        .threePointArc((arc_tank_r, 0),
                       middle_tank_handoff_plus_z)
        .threePointArc(transition_apex(+1, transition_tank_r),
                       transition_tank_terminus_plus_z)
        .lineTo(*side_wall_outer_plus_z)
        .radiusArc(far_wall_outer_plus_z, -corner_outer_r)
        .close()
        .extrude(height)
    )

    cavity_perimeter = (
        cq.Workplane(xz_plane_y_up)
        # +X far wall cavity face + ±Z cavity faces + filleted corners.
        .moveTo(*transition_cavity_terminus_plus_z)
        .lineTo(*side_wall_cavity_plus_z)
        .radiusArc(far_wall_cavity_plus_z, -corner_inner_r)
        .lineTo(*far_wall_cavity_minus_z)
        .radiusArc(side_wall_cavity_minus_z, -corner_inner_r)
        .lineTo(*transition_cavity_terminus_minus_z)
        # Centerward wall's cavity-side face: −Z transition, middle, +Z
        # transition. Concentric with the tank-side arcs, slightly
        # different radii.
        .threePointArc(transition_apex(-1, transition_cavity_r),
                       middle_cavity_handoff_minus_z)
        .threePointArc((arc_cavity_r, 0),
                       middle_cavity_handoff_plus_z)
        .threePointArc(transition_apex(+1, transition_cavity_r),
                       transition_cavity_terminus_plus_z)
        .close()
        .extrude(height)
    )

    plus_x_pocket = outer_perimeter.cut(cavity_perimeter)
    return plus_x_pocket.union(plus_x_pocket.mirror("YZ"))
