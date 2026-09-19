"""The machine display plane and the tangent curves surrounding it."""

import math
import cadquery as cq

ANGLE = 30.0
FLAT = 87.0
FRONT_RADIUS = 12.0
TOP_RADIUS = 18.0
SIDE_RADIUS = 6.0
FUNNEL_SEAT = 6.0


def profile(outer):
    """YZ stations of the front round, display plane and round onto the roof."""
    yf, zt = outer[2], outer[5]
    a = math.radians(ANGLE)
    rb, rt = FRONT_RADIUS, TOP_RADIUS
    zb = zt - rb * math.cos(a) - FLAT * math.sin(a) - rt * (1.0 - math.cos(a))
    start = (yf + rb * (1.0 - math.sin(a)), zb + rb * math.cos(a))
    end = (start[0] + FLAT * math.cos(a), start[1] + FLAT * math.sin(a))
    roof = (end[0] + rt * math.sin(a), zt)
    amid = math.radians(180.0 - (90.0 - ANGLE) / 2.0)
    return {
        "foot": (yf, zb),
        "front_mid": (yf + rb + rb * math.cos(amid), zb + rb * math.sin(amid)),
        "start": start,
        "end": end,
        "top_mid": (roof[0] - rt * math.sin(a / 2.0), zt - rt + rt * math.cos(a / 2.0)),
        "roof": roof,
        "origin": (0.0, (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0),
        "normal": (0.0, -math.sin(a), math.cos(a)),
    }


def silhouette(outer, rounded_box):
    """Rounded front and side edges with the rear top edge left square."""
    p = profile(outer)
    x0, x1, y0, y1, z0, z1 = outer
    wire = (cq.Workplane("YZ", origin=(x0, 0, 0))
            .moveTo(y0, z0).lineTo(*p["foot"])
            .threePointArc(p["front_mid"], p["start"]).lineTo(*p["end"])
            .threePointArc(p["top_mid"], p["roof"])
            .lineTo(y1, z1).lineTo(y1, z0).close().val())
    envelope = cq.Solid.extrudeLinear(wire, [], cq.Vector(x1 - x0, 0, 0))
    side_edges = [edge for edge in envelope.Edges()
                  if abs(abs(edge.Center().x) - x1) < 1e-5
                  and edge.BoundingBox().zmin >= p["start"][1] - 1e-5
                  and edge.BoundingBox().ymin < y1 - 1.0]
    return envelope.fillet(SIDE_RADIUS, side_edges).intersect(rounded_box).clean()


def rounded_prism(width, depth, radius, z0, z1, cx=0.0, cy=0.0):
    wire = cq.Workplane("XY", origin=(cx, cy, z0)).rect(width, depth).val()
    wire = wire.fillet2D(radius, wire.Vertices())
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 0, z1 - z0))
