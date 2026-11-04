"""Carbonator earth ring screwed radially into the existing upper tube rim.

All points use the cold core's native shell frame. The M3 tapped hole is in
the open 6.35 mm rim above the recessed closure plate. The ring, tooth washer
and screw head remain outside the tube; there is no internal nut. Datums do
not import CAD so installed wiring shares the steel contact and barrel exit.
"""

from __future__ import annotations

from _cold_core_data import read as _read


globals().update(_read("bond-constants"))
RIM_AZIMUTH_XY = tuple(RIM_AZIMUTH_XY)


def datums(top_plate_outer_z: float) -> dict:
    """Tapped rim contact and upward ring barrel from the Rust scalar recipe."""
    result = _read("bond", top_plate_outer_z=top_plate_outer_z)
    return {name: tuple(value) if isinstance(value, list) else value
            for name, value in result.items()}


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
