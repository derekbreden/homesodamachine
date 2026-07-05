"""Annular ring sitting at the bottom of the foam-shell's central
zone, holding the tank up by its outer rim. The ring's outer face sits
on the tank+coil envelope — inboard of the reservoir pockets' centerward
wall, which stands off from it by the cylinder's foam blanket."""

import cadquery as cq

from _cold_core_interface import (
    xz_plane_y_down,
    wall_and_floor_thickness,
    tank_coil_envelope_radius,
    tank_support_ring_height,
    support_ring_radial_width,
)


slot_count = 4
slot_angular_width = 30.0
# Slot overruns each ring face radially.
slot_radial_margin = 1.0


def revolve_rect(r_range, z_range, angle=360):
    """Rectangular (r, z) profile on the XZ plane (first coord is radius),
    revolved `angle` degrees about +Z from the +X axis."""
    r_min, r_max = min(r_range), max(r_range)
    z_min, z_max = min(z_range), max(z_range)
    return (
        cq.Workplane(xz_plane_y_down)
        .moveTo(r_min, z_min)
        .lineTo(r_max, z_min)
        .lineTo(r_max, z_max)
        .lineTo(r_min, z_max)
        .close()
        .revolve(angle)
    )


def build_tank_support_ring():
    """Annular ring with equal-spaced angular slots cut through it; slot
    boundaries lie on the same cylinders as the ring faces."""
    r_outer = tank_coil_envelope_radius
    r_inner = r_outer - support_ring_radial_width
    z_bottom = wall_and_floor_thickness
    z_top = z_bottom + tank_support_ring_height

    ring_r_range = (r_inner, r_outer)
    ring_z_range = (z_bottom, z_top)
    slot_r_range = (r_inner - slot_radial_margin, r_outer + slot_radial_margin)

    ring = revolve_rect(ring_r_range, ring_z_range)
    slot_spacing_angle = 360 / slot_count
    slot_template = revolve_rect(slot_r_range, ring_z_range, slot_angular_width)
    for i in range(slot_count):
        slot_center_angle = slot_spacing_angle * (i + 0.5)
        slot_start_angle = slot_center_angle - slot_angular_width / 2
        slot = slot_template.rotate((0, 0, 0), (0, 0, 1), slot_start_angle)
        ring = ring.cut(slot)
    return ring
