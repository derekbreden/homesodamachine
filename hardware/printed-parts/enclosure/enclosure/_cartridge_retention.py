"""One paused-in RC62 pair on the four tube axes, magnetized along insertion.

K&J RC62: 19.05 mm OD, 9.525 mm ID, 3.175 mm thick, axial N42,
±0.1 mm dimensional tolerance and 80 C continuous service rating:
https://www.kjmagnetics.com/rc62-neodymium-ring-magnet

The 1.2 mm mating-face cover is a local magnetic barrier, carried round its
entire perimeter by the ordinary 3 mm stock. Keeping this specific cover thin
limits the pair's separation; it is not an ordinary enclosure-wall section.
Retention force and heat exposure in the PET-GF print remain physical checks.
"""

import cadquery as cq

OD = 19.05
ID = 9.525
THICKNESS = 3.175
TOLERANCE = 0.1
FIT_COUPON = "C3"
RADIAL_AIR = 0.0
AXIAL_AIR = 0.0
FACE_COVER = 1.2
BACKING = 3.0
ROOF_AIR = 0.48
MAX_SERVICE_C = 80.0


def station(holes):
    """Centre between all four tubes, at their common Z axis."""
    xs, zs = zip(*holes)
    if len(holes) != 4 or max(zs) - min(zs) > 1e-6:
        raise ValueError("RC62 retention requires the four tubes on one horizontal row")
    return (min(xs) + max(xs)) / 2.0, sum(zs) / len(zs)


def dimensions(xz, face_y, into):
    x, z = xz
    radius = OD / 2.0 + RADIAL_AIR
    depth = THICKNESS + AXIAL_AIR
    ys = sorted((face_y + into * FACE_COVER,
                 face_y + into * (FACE_COVER + depth)))
    return {"axis_xz_mm": [x, z], "magnet_axis": [0, 1, 0],
            "mating_face_y_mm": face_y, "into": into,
            "pocket_y_mm": ys, "pocket_radius_mm": radius,
            "arc_center_z_mm": z + RADIAL_AIR,
            "seat_floor_z_mm": z - OD / 2.0,
            "roof_z_mm": z + OD / 2.0 + ROOF_AIR,
            "face_cover_mm": FACE_COVER, "backing_minimum_mm": BACKING,
            "width_mm": 2 * radius, "depth_mm": depth,
            "fit_coupon": FIT_COUPON,
            "maximum_od_x_interference_mm": max(0.0, OD + TOLERANCE - 2 * radius),
            "maximum_thickness_y_interference_mm": max(0.0, THICKNESS + TOLERANCE - depth),
            "nominal_roof_clearance_mm": ROOF_AIR,
            "minimum_roof_clearance_at_maximum_od_mm": ROOF_AIR - TOLERANCE}


def pocket(xz, face_y, into):
    """Round lower seat with a full-width upper mouth, capped after insertion.

    Both owning parts print in +Z. A closed circular or annular pocket would
    narrow above its equator before an upright ring could enter. This D-shaped
    cavity keeps the selected C3 width up to the flat roof. A maximum-size ring
    has intentional lateral interference; the roof air is independent of that
    hand-fit choice. There is no post through the ring's centre.
    """
    d = dimensions(xz, face_y, into)
    x, _z = xz
    y0, y1 = d["pocket_y_mm"]
    arc_z = d["arc_center_z_mm"]
    r = d["pocket_radius_mm"]
    circle = cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(x, y0, arc_z), cq.Vector(0, 1, 0))
    mouth = cq.Solid.makeBox(2 * r, y1 - y0, d["roof_z_mm"] - arc_z,
                            cq.Vector(x - r, y0, arc_z))
    return circle.fuse(mouth).clean()


def magnet(xz, face_y, into):
    """Nominal seated ring bearing on the cover toward its attracting mate."""
    x, z = xz
    y0, y1 = sorted((face_y + into * FACE_COVER,
                     face_y + into * (FACE_COVER + THICKNESS)))
    outer = cq.Solid.makeCylinder(OD / 2, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
    inner = cq.Solid.makeCylinder(ID / 2, y1 - y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))
    return outer.cut(inner)
