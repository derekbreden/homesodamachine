"""Two reservoir pockets, one on each ±X side, as four-walled
enclosures whose centerward wall is curved to clear the carbonator+coil
envelope. The −X pocket mirrors the +X pocket across YZ."""

import math
import cadquery as cq

from world_workplane import WorldWorkplane, WorldProfile, xy_plane_z_up
from _cold_core_interface import (
    wall_thickness,
    pocket_centerward_arc_outer_radius,
    foam_shell_outer_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_y_inner_max,
    bag_pocket_far_inner_x,
)

w = wall_thickness

# Y at which the centerward wall hands off from its middle segment
# (the cylindrical arc that wraps the carbonator+coil envelope) to the
# transition arcs that swing the wall out to the pocket's ±Y walls.
pocket_centerward_arc_transition_y = 60.0

# Transition arc: the short curve between the middle (carbonator-wrapping)
# arc and the pocket's ±Y wall. Carbonator-side face radius.

# Centerward-wall arc geometry, at the transition corner where the
# centerward wall meets a ±Y wall. The +Y side is described; the −Y side
# mirrors in y.
arc_cavity_r = pocket_centerward_arc_outer_radius
arc_outer_r = arc_cavity_r - w
# ±Y wall position — the reservoir's own half-width, NOT the arc radius, so the
# centerward wall can move out (bigger foam blanket) without splaying the pocket.
y_inner = bag_pocket_y_inner_max
middle_outer_x = math.sqrt(arc_outer_r**2 - pocket_centerward_arc_transition_y**2)
middle_cavity_x = math.sqrt(arc_cavity_r**2 - pocket_centerward_arc_transition_y**2)
_chord_half_y = (y_inner - pocket_centerward_arc_transition_y) / 2.0
# Mating-profile datum, independent of the stock outside the cavity.
transition_center_x = 56.655020677894306
transition_center_y = (y_inner + pocket_centerward_arc_transition_y) / 2.0
transition_cavity_r = math.sqrt((transition_center_x - middle_cavity_x)**2 + _chord_half_y**2)
transition_outer_r = transition_cavity_r + w


def build_plus_x_cavity(height=None):
    """The +X reservoir pocket's cavity solid. The −X pocket mirrors
    across YZ."""
    if height is None:
        height = foam_shell_outer_height
    far_x_inner = bag_pocket_far_inner_x
    corner_inner_r = bag_pocket_corner_inner_radius
    arc_y = pocket_centerward_arc_transition_y

    def transition_apex(y_sign):
        return (transition_center_x - transition_cavity_r, y_sign * transition_center_y)

    cavity_profile = (
        WorldProfile()
        .moveTo((middle_cavity_x, y_inner))
        .lineTo((far_x_inner - corner_inner_r, y_inner))
        .radiusArc((far_x_inner, y_inner - corner_inner_r), corner_inner_r)
        .lineTo((far_x_inner, -(y_inner - corner_inner_r)))
        .radiusArc((far_x_inner - corner_inner_r, -y_inner), corner_inner_r)
        .lineTo((middle_cavity_x, -y_inner))
        .threePointArc(transition_apex(-1), (middle_cavity_x, -arc_y))
        .threePointArc((arc_cavity_r, 0), (middle_cavity_x, arc_y))
        .threePointArc(transition_apex(+1), (middle_cavity_x, y_inner))
    )
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=0)
        .profile(cavity_profile).wire()
        .extrude(height)
    )


def build_reservoir_pocket_walls():
    """Fixed mating cavities, offset into the foam by the standing-wall stock."""
    height = foam_shell_outer_height
    cavity = build_plus_x_cavity(height).unwrap()
    wire = cavity.faces('<Z').wires().val()
    outer_wire = wire.offset2D(w, kind='arc')[0]
    outer = cq.Workplane('XY').add(outer_wire).toPending().extrude(height)
    plus_x_pocket = outer.cut(cavity)
    return plus_x_pocket.union(plus_x_pocket.mirror('YZ'))
