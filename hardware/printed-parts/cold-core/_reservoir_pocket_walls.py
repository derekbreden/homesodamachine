"""Build the two reservoir pockets — one on each ±X side — as
four-walled enclosures whose centerward wall is curved to clear the
tank+coil envelope. The +X pocket is traced explicitly; the −X pocket
is its mirror across the YZ plane."""

import math

from world_workplane import WorldWorkplane, WorldProfile, xy_plane_z_up
from _cold_core_interface import (
    wall_and_floor_thickness,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_outermost_x,
)

w = wall_and_floor_thickness

# Y at which the centerward wall hands off from its middle segment
# (the cylindrical arc that wraps the tank+coil envelope) to the
# transition arcs that swing the wall out to the pocket's ±Y walls.
pocket_centerward_arc_transition_y = 60.0

# Transition arc: the short curve between the middle (tank-wrapping)
# arc and the pocket's ±Y wall. Tank-side face radius.
transition_tank_r = 8.0

# Centerward-wall arc geometry, at module level so sibling parts (the
# reservoir corner supports) can seat features against the transition corner
# where the centerward wall meets a ±Y wall. The +Y side is described; the
# −Y side mirrors in y.
arc_cavity_r = pocket_centerward_arc_outer_radius
arc_tank_r = arc_cavity_r - w
y_inner = arc_cavity_r - w
middle_tank_x = math.sqrt(arc_tank_r**2 - pocket_centerward_arc_transition_y**2)
middle_cavity_x = math.sqrt(arc_cavity_r**2 - pocket_centerward_arc_transition_y**2)
_chord_half_y = (y_inner - pocket_centerward_arc_transition_y) / 2.0
transition_center_x = middle_tank_x + math.sqrt(transition_tank_r**2 - _chord_half_y**2)
transition_center_y = (y_inner + pocket_centerward_arc_transition_y) / 2.0
transition_cavity_r = math.sqrt((transition_center_x - middle_cavity_x)**2 + _chord_half_y**2)
# Cavity-side vertex where the centerward wall meets a ±Y wall (+Y; −Y
# mirrors). The corner the centerward supports nest into.
centerward_corner_x = middle_cavity_x
centerward_corner_y = y_inner


def build_reservoir_pocket_walls():
    """Two reservoir pockets, mirrored across YZ. Built per side as an
    outer-perimeter polyline minus a cavity-perimeter polyline rather
    than a single multi-loop sketch because CadQuery's pending-wire
    heuristic mis-classifies two non-nested outer wires in the same
    workplane as nested ones."""
    height = foam_shell_outer_height

    far_x_outer = bag_pocket_outermost_x
    far_x_inner = far_x_outer - w
    y_outer = pocket_centerward_arc_outer_radius
    corner_inner_r = bag_pocket_corner_inner_radius
    corner_outer_r = corner_inner_r + w
    arc_y = pocket_centerward_arc_transition_y

    # Centerward-wall arc geometry (arc_cavity_r, arc_tank_r, middle_*_x,
    # transition_center_*, transition_cavity_r, y_inner) is module-level.
    transition_tank_terminus_x = transition_center_x - math.sqrt(
        transition_tank_r**2 - (y_outer - transition_center_y)**2
    )

    def transition_apex(y_sign, r):
        """Apex of the transition arc at y_sign·Y, on the line from its
        center toward the cold-core axis."""
        return (transition_center_x - r, y_sign * transition_center_y)

    # Centerward-wall joints. Apexes are where each middle-arc reaches
    # its max +X excursion (at y=0).
    middle_tank_apex = (arc_tank_r, 0)
    middle_cavity_apex = (arc_cavity_r, 0)
    middle_tank_handoff_plus_y = (middle_tank_x, arc_y)
    middle_tank_handoff_minus_y = (middle_tank_x, -arc_y)
    middle_cavity_handoff_plus_y = (middle_cavity_x, arc_y)
    middle_cavity_handoff_minus_y = (middle_cavity_x, -arc_y)

    # Cavity-side transition terminus sits at middle_cavity_x because
    # the transition's cavity-face circle passes through both middle-
    # arc handoffs by construction.
    transition_tank_terminus_plus_y = (transition_tank_terminus_x, y_outer)
    transition_tank_terminus_minus_y = (transition_tank_terminus_x, -y_outer)
    transition_cavity_terminus_plus_y = (middle_cavity_x, y_inner)
    transition_cavity_terminus_minus_y = (middle_cavity_x, -y_inner)

    # +X far wall: outer face at far_x_outer, cavity face at far_x_inner,
    # both spanning ±(y_inner - corner_inner_r) where corner arcs begin.
    far_wall_outer_plus_y = (far_x_outer, y_inner - corner_inner_r)
    far_wall_outer_minus_y = (far_x_outer, -(y_inner - corner_inner_r))
    far_wall_cavity_plus_y = (far_x_inner, y_inner - corner_inner_r)
    far_wall_cavity_minus_y = (far_x_inner, -(y_inner - corner_inner_r))

    # ±Y wall corner-arc termini. Outer- and cavity-side arcs share an
    # axis at (far_x_inner - corner_inner_r, ±(y_inner - corner_inner_r))
    # — outer at corner_outer_r, cavity at corner_inner_r — so both
    # terminate at the same X.
    side_wall_outer_plus_y = (far_x_inner - corner_inner_r, y_outer)
    side_wall_outer_minus_y = (far_x_inner - corner_inner_r, -y_outer)
    side_wall_cavity_plus_y = (far_x_inner - corner_inner_r, y_inner)
    side_wall_cavity_minus_y = (far_x_inner - corner_inner_r, -y_inner)

    outer_profile = (
        WorldProfile()
        .moveTo(far_wall_outer_plus_y)
        .lineTo(far_wall_outer_minus_y)
        .radiusArc(side_wall_outer_minus_y, corner_outer_r)
        .lineTo(transition_tank_terminus_minus_y)
        .threePointArc(transition_apex(-1, transition_tank_r), middle_tank_handoff_minus_y)
        .threePointArc(middle_tank_apex, middle_tank_handoff_plus_y)
        .threePointArc(transition_apex(+1, transition_tank_r), transition_tank_terminus_plus_y)
        .lineTo(side_wall_outer_plus_y)
        .radiusArc(far_wall_outer_plus_y, corner_outer_r)
    )
    outer_perimeter = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .profile(outer_profile).close()
        .extrude(height)
    )

    cavity_profile = (
        WorldProfile()
        .moveTo(transition_cavity_terminus_plus_y)
        .lineTo(side_wall_cavity_plus_y)
        .radiusArc(far_wall_cavity_plus_y, corner_inner_r)
        .lineTo(far_wall_cavity_minus_y)
        .radiusArc(side_wall_cavity_minus_y, corner_inner_r)
        .lineTo(transition_cavity_terminus_minus_y)
        .threePointArc(transition_apex(-1, transition_cavity_r), middle_cavity_handoff_minus_y)
        .threePointArc(middle_cavity_apex, middle_cavity_handoff_plus_y)
        .threePointArc(transition_apex(+1, transition_cavity_r), transition_cavity_terminus_plus_y)
    )
    cavity_perimeter = (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .profile(cavity_profile).close()
        .extrude(height)
    )

    plus_x_pocket = outer_perimeter.cut(cavity_perimeter)
    return plus_x_pocket.union(plus_x_pocket.mirror("YZ")).unwrap()
