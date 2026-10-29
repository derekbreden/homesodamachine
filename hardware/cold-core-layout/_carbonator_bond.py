"""Carbonator earth ring screwed radially into the existing upper tube rim.

All points use the cold core's native shell frame. The M3 tapped hole is in
the open 6.35 mm rim above the recessed closure plate. The ring, tooth washer
and screw head remain outside the tube; there is no internal nut. Datums do
not import CAD so installed wiring shares the steel contact and barrel exit.
"""

from __future__ import annotations

import math


# The radial attachment faces the shared west cap passage (native X23.2/Y48).
RIM_AZIMUTH_XY = (23.2, 48.0)
TUBE_OUTER_RADIUS = 63.5
TUBE_WALL = .065 * 25.4
RIM_HEIGHT = .25 * 25.4
HOLE_HEIGHT = 3.5                      # above the top plate's outside face
TAP_DRILL_DIAMETER = 2.5
THREAD_DIAMETER = 3.0
THREAD_PITCH = .5

SCREW_LENGTH = 4.0                    # finished under-head length
SCREW_DIAMETER = THREAD_DIAMETER
SCREW_HEAD_DIAMETER = 5.5
SCREW_HEAD_HEIGHT = 3.0
RING_TONGUE_THICKNESS = .8
RING_EYE_DIAMETER = 8.0
RING_BARREL_DIAMETER = 4.2
RING_BARREL_LENGTH = 6.0
WASHER_DIAMETER = 6.0
WASHER_BORE = 3.2
WASHER_THICKNESS = .4
WASHER_PART = "M3 DIN 6797 A external-tooth lockwasher, A2 stainless"
WASHER_SOURCE = (
    "https://damesa.com/en/products/fasteners/washers/"
    "din-6797-external-tooth-lock-washer-form-a")


def datums(top_plate_outer_z: float) -> dict:
    """Tapped rim contact and upward ring barrel, without importing CAD.

    The nominal site is used where the finished bore and screw-tip envelope
    are wholly above the actual closure-weld toe. The closure weld is not cut
    to fit this attachment; its size remains specified by the weld procedure.
    """
    scale = math.hypot(*RIM_AZIMUTH_XY)
    ux, uy = (v / scale for v in RIM_AZIMUTH_XY)
    outward = (ux, uy, 0.)
    z = top_plate_outer_z + HOLE_HEIGHT

    def radial(radius, height=z):
        return (ux * radius, uy * radius, height)

    head_radius = TUBE_OUTER_RADIUS + RING_TONGUE_THICKNESS + WASHER_THICKNESS
    tip_radius = head_radius - SCREW_LENGTH
    return {
        "body": "carbonator-tube",
        "base_center_mm": radial(TUBE_OUTER_RADIUS, top_plate_outer_z),
        "hole_center_mm": radial(TUBE_OUTER_RADIUS - TUBE_WALL / 2),
        "hole_axis": (-ux, -uy, 0.),
        "tap_drill_diameter_mm": TAP_DRILL_DIAMETER,
        "thread": "M3 x 0.5 through",
        "thread_diameter_mm": THREAD_DIAMETER,
        "thread_pitch_mm": THREAD_PITCH,
        "thread_engagement_mm": TUBE_WALL,
        "nominal_engaged_threads": TUBE_WALL / THREAD_PITCH,
        "rim_top_z_mm": top_plate_outer_z + RIM_HEIGHT,
        "hole_height_above_plate_mm": HOLE_HEIGHT,
        "hole_height_below_rim_mm": RIM_HEIGHT - HOLE_HEIGHT,
        "contact_point_mm": radial(TUBE_OUTER_RADIUS),
        "contact_outward": outward,
        "wire_exit_mm": radial(TUBE_OUTER_RADIUS + RING_BARREL_DIAMETER / 2, z + 9.),
        "wire_outward": (0., 0., 1.),
        "screw_axis": (-ux, -uy, 0.),
        "screw_underhead_mm": radial(head_radius),
        "screw_length_mm": SCREW_LENGTH,
        "screw_tip_mm": radial(tip_radius),
        "screw_projection_inside_tube_mm": TUBE_OUTER_RADIUS - TUBE_WALL - tip_radius,
        "screw_source": "304 stainless M3x12 stock shortened and end-finished to M3x4",
        "ring_tongue_thickness_mm": RING_TONGUE_THICKNESS,
        "ring_eye_diameter_mm": RING_EYE_DIAMETER,
        "ring_barrel_diameter_mm": RING_BARREL_DIAMETER,
        "ring_barrel_length_mm": RING_BARREL_LENGTH,
        "lockwasher_part": WASHER_PART,
        "lockwasher_source": WASHER_SOURCE,
        "hardware_bodies": ("carbonator-earth-screw", "carbonator-earth-lockwasher"),
        "clamp_order_from_head": (
            "M3x4 stainless screw", WASHER_PART, "M3 closed ring tongue",
            "bare upper tube rim tapped M3x0.5"),
    }


def cut_tube(tube, top_plate_outer_z: float):
    """Cut the radial tapped-hole envelope from the existing native tube.

    Threads are omitted: the display bore is the M3 major-diameter envelope.
    Fabrication uses the 2.5 mm tap drill and M3 x 0.5 through thread above.
    The cutter crosses only this wall, ending inside the open upper recess.
    """
    import cadquery as cq

    d = datums(top_plate_outer_z)
    outward = cq.Vector(*d["contact_outward"])
    start = cq.Vector(*d["contact_point_mm"]) + outward
    bore = cq.Solid.makeCylinder(
        THREAD_DIAMETER / 2, TUBE_WALL + 2, start, -outward)
    return tube.cut(bore)


def build_hardware(top_plate_outer_z: float) -> dict:
    """Exterior M3x4 screw and tooth washer; wiring supplies the closed ring.

    Threads, socket recess and individual washer teeth are omitted from the
    display envelopes. The short screw clears the unpressurized recess;
    there is no fastener head or nut beside the closure fillet.
    """
    import cadquery as cq

    d = datums(top_plate_outer_z)
    underhead = cq.Vector(*d["screw_underhead_mm"])
    axis = cq.Vector(*d["screw_axis"])
    shank = cq.Solid.makeCylinder(SCREW_DIAMETER / 2, SCREW_LENGTH, underhead, axis)
    head = cq.Solid.makeCylinder(
        SCREW_HEAD_DIAMETER / 2, SCREW_HEAD_HEIGHT, underhead, -axis)
    screw = head.fuse(shank)

    washer = cq.Solid.makeCylinder(
        WASHER_DIAMETER / 2, WASHER_THICKNESS, underhead, axis)
    bore = cq.Solid.makeCylinder(
        WASHER_BORE / 2, WASHER_THICKNESS + 2, underhead - axis, axis)
    washer = washer.cut(bore)
    return {"carbonator-earth-screw": screw, "carbonator-earth-lockwasher": washer}
