"""Annular ring sitting at the bottom of the foam-shell's central
zone, holding the tank up by its outer rim. The ring's outer face is
coincident with the reservoir pockets' centerward wall on its tank-
side face."""

import cadquery as cq

from _cold_core_interface import (
    wall_and_floor_thickness,
    pocket_centerward_arc_outer_radius,
    tank_support_ring_height,
)


def build_tank_support_ring():
    """Built as a full revolve of a rectangular (R, y) profile around
    the Y axis; four 30°-wide angular slots at the diagonals are cut
    as 30° revolves of the same profile (with a radial margin), so
    every slot boundary stays on the same cylinder as the ring faces
    — no chord-vs-arc slivers."""
    R_outer = pocket_centerward_arc_outer_radius - wall_and_floor_thickness
    R_inner = R_outer - 9
    y_bottom = wall_and_floor_thickness
    y_top = y_bottom + tank_support_ring_height

    ring_profile = (
        cq.Workplane("XY")
        .moveTo(R_inner, y_bottom)
        .lineTo(R_outer, y_bottom)
        .lineTo(R_outer, y_top)
        .lineTo(R_inner, y_top)
        .close()
    )
    ring = ring_profile.revolve()

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
