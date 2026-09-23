"""The machine display plane and the tangent curves surrounding it."""

import math
import cadquery as cq
import _enclosure_interface as dims

ANGLE = 30.0
FLAT = 87.0
FRONT_RADIUS = dims.show_corner_r
TOP_RADIUS = 3.0 * dims.show_edge_r
SIDE_RADIUS = dims.show_edge_r
FUNNEL_SEAT = 6.0
# The top curve's last 0.48 mm under the roof — its last two 0.24 mm layers, printed up +Z —
# rises at the plane's own ANGLE instead of rolling level, so each of those layers steps back
# the plane's 0.42 mm rather than the curve's 1.5 and 1.0 mm, and none stands vertical.
TOP_PULL = 0.48


def profile(outer):
    """YZ stations of the front round, display plane and round onto the roof."""
    yf, zt = outer[2], outer[5]
    a = math.radians(ANGLE)
    rb, rt = FRONT_RADIUS, TOP_RADIUS
    zb = zt - rb * math.cos(a) - FLAT * math.sin(a) - rt * (1.0 - math.cos(a))
    start = (yf + rb * (1.0 - math.sin(a)), zb + rb * math.cos(a))
    end = (start[0] + FLAT * math.cos(a), start[1] + FLAT * math.sin(a))
    centre = (end[0] + rt * math.sin(a), zt - rt)
    b = math.acos(1.0 - TOP_PULL / rt)
    pull = (centre[0] - rt * math.sin(b), zt - TOP_PULL)
    top = (a + b) / 2.0
    amid = math.radians(180.0 - (90.0 - ANGLE) / 2.0)
    return {
        "foot": (yf, zb),
        "front_mid": (yf + rb + rb * math.cos(amid), zb + rb * math.sin(amid)),
        "start": start,
        "end": end,
        "top_mid": (centre[0] - rt * math.sin(top), centre[1] + rt * math.cos(top)),
        "pull": pull,
        "roof": (pull[0] + TOP_PULL / math.tan(a), zt),
        "origin": (0.0, (start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0),
        "normal": (0.0, -math.sin(a), math.cos(a)),
    }


def silhouette(outer, rounded_box, vertical_radius):
    """Rounded front and side edges with the rear top edge left square."""
    p = profile(outer)
    x0, x1, y0, y1, z0, z1 = outer
    wire = (cq.Workplane("YZ", origin=(x0, 0, 0))
            .moveTo(y0, z0).lineTo(*p["foot"])
            .threePointArc(p["front_mid"], p["start"]).lineTo(*p["end"])
            .threePointArc(p["top_mid"], p["pull"]).lineTo(*p["roof"])
            .lineTo(y1, z1).lineTo(y1, z0).close().val())
    envelope = cq.Solid.extrudeLinear(wire, [], cq.Vector(x1 - x0, 0, 0))
    # The front standing rounds participate in the side blend. Its rolling radius
    # follows their intersection with the front curve, joining all three surfaces
    # tangentially. The rear standing corners are applied after this blend, keeping
    # the rear top edge square.
    fore_end = y0 + vertical_radius
    rear_fill = (cq.Workplane("XY")
                 .box(x1 - x0, y1 - fore_end, z1 - z0)
                 .translate(((x0 + x1) / 2.0, (fore_end + y1) / 2.0,
                             (z0 + z1) / 2.0)).val())
    body = envelope.intersect(rounded_box.fuse(rear_fill)).clean()
    side_edges = [edge for edge in body.Edges()
                  if (edge.BoundingBox().xmin >= x1 - vertical_radius - 1e-5
                      or edge.BoundingBox().xmax <= x0 + vertical_radius + 1e-5)
                  and edge.BoundingBox().zmin >= p["foot"][1] - 1e-5
                  and edge.BoundingBox().ymin < y1 - 1.0]
    return body.fillet(SIDE_RADIUS, side_edges).intersect(rounded_box).clean()


def rounded_prism(width, depth, radius, z0, z1, cx=0.0, cy=0.0):
    wire = cq.Workplane("XY", origin=(cx, cy, z0)).rect(width, depth).val()
    wire = wire.fillet2D(radius, wire.Vertices())
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 0, z1 - z0))
