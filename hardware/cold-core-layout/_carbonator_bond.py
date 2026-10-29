"""Carbonator's welded earth tab and its dedicated M3 clamp.

All points use the cold core's native shell frame. The base lands on the top
plate's outside face; neither the tab hole nor its fastener enters that plate.
Datums are available without importing CAD so the installed wiring can share
the exact steel contact and conductor exit.
"""

from __future__ import annotations

import math


TAB_XY = (23.2, 40.0)
TAB_WIDTH = 12.0
TAB_HEIGHT = 13.0
TAB_THICKNESS = 1.5
TAB_TOP_RADIUS = 2.0
HOLE_DIAMETER = 3.6
HOLE_HEIGHT = 8.0

SCREW_LENGTH = 12.0
SCREW_DIAMETER = 3.0
SCREW_HEAD_DIAMETER = 5.5
SCREW_HEAD_HEIGHT = 3.0
RING_TONGUE_THICKNESS = .8
RING_EYE_DIAMETER = 8.0
RING_BARREL_DIAMETER = 4.2
RING_BARREL_LENGTH = 6.0
NUT_HEIGHT = 3.3
NUT_WIDTH_ACROSS_FLATS = 5.5
NUT_WASHER_DIAMETER = 6.5
NUT_WASHER_THICKNESS = .5
NUT_PART = "McMaster 90923A216"


def datums(top_plate_outer_z: float) -> dict:
    """Tab contact, clamp order and conductor exit in the core's own frame.

    The ring tongue bears directly on the tab's +Y face. Its barrel points
    upward toward the existing sensor/earth passage; no cap mount is needed.
    """
    x, y = TAB_XY
    z = top_plate_outer_z + HOLE_HEIGHT
    contact_y = y + TAB_THICKNESS / 2
    head_bearing_y = contact_y + RING_TONGUE_THICKNESS
    nut_end_y = y - TAB_THICKNESS / 2 - NUT_HEIGHT
    return {
        "body": "carbonator-earth-tab",
        "base_center_mm": (x, y, top_plate_outer_z),
        "hole_center_mm": (x, y, z),
        "contact_point_mm": (x, contact_y, z),
        "contact_outward": (0., 1., 0.),
        "wire_exit_mm": (x, contact_y + RING_BARREL_DIAMETER / 2, z + 9.),
        "wire_outward": (0., 0., 1.),
        "screw_axis": (0., -1., 0.),
        "screw_underhead_mm": (x, head_bearing_y, z),
        "screw_length_mm": SCREW_LENGTH,
        "screw_tip_y_mm": head_bearing_y - SCREW_LENGTH,
        "nut_outer_face_y_mm": nut_end_y,
        "thread_beyond_nut_mm": nut_end_y - (head_bearing_y - SCREW_LENGTH),
        "ring_tongue_thickness_mm": RING_TONGUE_THICKNESS,
        "ring_eye_diameter_mm": RING_EYE_DIAMETER,
        "ring_barrel_diameter_mm": RING_BARREL_DIAMETER,
        "ring_barrel_length_mm": RING_BARREL_LENGTH,
        "hardware_bodies": ("carbonator-earth-screw", "carbonator-earth-locknut"),
        "clamp_order_from_head": ("M3x12 stainless screw", "M3 ring tongue", "bare welded tab",
                                   "captive external-tooth locknut 90923A216"),
    }


def build_tab(top_plate_outer_z: float):
    """One 304 stainless tab, rounded at the two upper corners and drilled."""
    import cadquery as cq

    x, y = TAB_XY
    tab = cq.Solid.makeBox(
        TAB_WIDTH, TAB_THICKNESS, TAB_HEIGHT,
        cq.Vector(x - TAB_WIDTH / 2, y - TAB_THICKNESS / 2, top_plate_outer_z))
    top_edges = [e for e in tab.Edges()
                 if abs(e.Length() - TAB_THICKNESS) < 1e-7
                 and abs(e.Center().z - top_plate_outer_z - TAB_HEIGHT) < 1e-7]
    tab = tab.fillet(TAB_TOP_RADIUS, top_edges)
    bore = cq.Solid.makeCylinder(
        HOLE_DIAMETER / 2, TAB_THICKNESS + 2,
        cq.Vector(x, y - TAB_THICKNESS / 2 - 1, top_plate_outer_z + HOLE_HEIGHT),
        cq.Vector(0, 1, 0))
    return tab.cut(bore)


def build_hardware(top_plate_outer_z: float) -> dict:
    """Dedicated stainless screw and captive-tooth nut.

    Threads, socket recess and individual lockwasher teeth are omitted from the
    display envelopes. The installed-wiring producer supplies the ring terminal.
    """
    import cadquery as cq

    d = datums(top_plate_outer_z)
    x, yh, z = d["screw_underhead_mm"]
    axis = cq.Vector(0, -1, 0)
    shank = cq.Solid.makeCylinder(SCREW_DIAMETER / 2, SCREW_LENGTH,
                                 cq.Vector(x, yh, z), axis)
    head = cq.Solid.makeCylinder(SCREW_HEAD_DIAMETER / 2, SCREW_HEAD_HEIGHT,
                                cq.Vector(x, yh, z), -axis)
    screw = head.fuse(shank)

    def washer(diameter, thickness, y):
        outer = cq.Solid.makeCylinder(diameter / 2, thickness, cq.Vector(x, y, z), axis)
        bore = cq.Solid.makeCylinder(3.2 / 2, thickness + 2,
                                    cq.Vector(x, y + 1, z), axis)
        return outer.cut(bore)

    nut_y = TAB_XY[1] - TAB_THICKNESS / 2
    tooth = washer(NUT_WASHER_DIAMETER, NUT_WASHER_THICKNESS, nut_y)
    plane = cq.Plane(origin=(x, nut_y - NUT_WASHER_THICKNESS, z),
                     xDir=(1, 0, 0), normal=(0, -1, 0))
    hexagon = cq.Workplane(plane).polygon(
        6, NUT_WIDTH_ACROSS_FLATS / math.cos(math.pi / 6)).extrude(
            NUT_HEIGHT - NUT_WASHER_THICKNESS).val()
    nut_bore = cq.Solid.makeCylinder(SCREW_DIAMETER / 2, NUT_HEIGHT + 2,
                                    cq.Vector(x, nut_y + 1, z), axis)
    nut = tooth.fuse(hexagon).cut(nut_bore)
    return {"carbonator-earth-screw": screw, "carbonator-earth-locknut": nut}
