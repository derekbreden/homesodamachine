"""Annular ring sitting at the bottom of the foam-shell's central
zone, holding the tank up by its outer rim. The ring's outer face is
coincident with the reservoir pockets' centerward wall on its tank-
side face."""

import cadquery as cq

from _cold_core_interface import (
    xy_plane_z_up,
    wall_and_floor_thickness,
    pocket_centerward_arc_outer_radius,
    tank_support_ring_height,
    support_ring_radial_width,
)


slot_count = 4
slot_angular_width = 30.0
# Radial overrun on each side so the slot cuts past the ring faces and
# doesn't leave a thin shell at r_inner / r_outer from numerical noise.
slot_radial_margin = 1.0


def revolve_rect(r_range, y_range, angle=360):
    """Revolve a rectangular (r, y) profile around the Y axis by `angle`
    degrees. The profile lives on the XY plane with its first coordinate
    interpreted as radius; revolve's default axis is +Y, sweeping from
    the +X axis."""
    r_min, r_max = min(r_range), max(r_range)
    y_min, y_max = min(y_range), max(y_range)
    return (
        cq.Workplane(xy_plane_z_up)
        .moveTo(r_min, y_min)
        .lineTo(r_max, y_min)
        .lineTo(r_max, y_max)
        .lineTo(r_min, y_max)
        .close()
        .revolve(angle)
    )


def build_tank_support_ring():
    """Built as a full revolve of a rectangular (r, y) profile around
    the Y axis; equal-spaced angular slots are cut as partial revolves
    of the same profile (with a radial margin), so every slot boundary
    stays on the same cylinder as the ring faces — no chord-vs-arc
    slivers."""
    r_outer = pocket_centerward_arc_outer_radius - wall_and_floor_thickness
    r_inner = r_outer - support_ring_radial_width
    y_bottom = wall_and_floor_thickness
    y_top = y_bottom + tank_support_ring_height

    ring_r_range = (r_inner, r_outer)
    ring_y_range = (y_bottom, y_top)
    slot_r_range = (r_inner - slot_radial_margin, r_outer + slot_radial_margin)

    ring = revolve_rect(ring_r_range, ring_y_range)
    slot_spacing_angle = 360 / slot_count
    slot_template = revolve_rect(slot_r_range, ring_y_range, slot_angular_width)
    for i in range(slot_count):
        slot_center_angle = slot_spacing_angle * (i + 0.5)
        slot_start_angle = slot_center_angle - slot_angular_width / 2
        slot = slot_template.rotate((0, 0, 0), (0, 1, 0), slot_start_angle)
        ring = ring.cut(slot)
    return ring
