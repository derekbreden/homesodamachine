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


def _roof_fill(outer):
    """A side-edge fill whose leading end follows the curved display top.

    Each section keeps the display's R6 side offset. An ellipse tangent to that
    display plane joins it to the shared print-down roof chamfer. The fill's
    inner surface overlaps the retained round, rather than ending on an exposed
    horizontal underside.
    """
    from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
    from overhang_round import transition, OUTWARD_PER_HEIGHT

    p = profile(outer)
    radius, rt = SIDE_RADIUS, TOP_RADIUS
    angle = math.radians(ANGLE)
    sa, ca = math.sin(angle), math.cos(angle)
    cy, cz = p["roof"][0], outer[5] - rt
    aft = cy + 2.0 * radius
    height, foot = transition(radius)
    tangent_depth = foot - OUTWARD_PER_HEIGHT * height
    depths = {radius * (1.0 - math.sin(math.radians(a)))
              for a in range(0, 91, 2)}
    depths = {d for d in depths if d >= tangent_depth}
    depths.update((tangent_depth, foot, radius))

    fills = []
    for edge, inward in ((outer[0], 1), (outer[1], -1)):
        loft = BRepOffsetAPI_ThruSections(True, True, 1e-6)
        # The wires already have corresponding edges. Automatic realignment can
        # shift their joins as the top arc changes from a circle to an ellipse.
        loft.CheckCompatibility(False)
        for depth in sorted(depths):
            side = radius - math.sqrt(max(0.0, radius**2 - (radius - depth)**2))
            roof = min(side, max(0.0, (foot - depth) / OUTWARD_PER_HEIGHT))
            # Keep the loft's display edge inside the exact retained side roll.
            # Its lower skin also overlaps that roll, so the union has no fins.
            side += .01
            k, b = rt - side, rt - roof
            a = math.sqrt((k*k - b*b * ca*ca) / (sa*sa))
            top_tangent = (cy - a*a * sa / k, cz + b*b * ca / k)
            theta = math.degrees(math.atan2(a * sa, b * ca))
            start = (p["end"][0] + sa * side - ca,
                     p["end"][1] - ca * side - sa)
            inner_r = rt - side - .25
            inner_end = (cy - inner_r * sa, cz + inner_r * ca)
            inner_mid = (cy - inner_r * math.sin(angle / 2.0),
                         cz + inner_r * math.cos(angle / 2.0))
            inner_start = (inner_end[0] - ca, inner_end[1] - sa)
            upper_roof, lower_roof = (cy, cz + b), (cy, cz + inner_r)
            upper_aft, lower_aft = (aft, cz + b), (aft, cz + inner_r)
            x = edge + inward * depth

            def v(point):
                return cq.Vector(x, *point)

            wire = cq.Wire.assembleEdges([
                cq.Edge.makeLine(v(start), v(top_tangent)),
                cq.Edge.makeEllipse(b, a, (x, cy, cz), (1, 0, 0),
                                    (0, 0, 1), 0, theta),
                cq.Edge.makeLine(v(upper_roof), v(upper_aft)),
                cq.Edge.makeLine(v(upper_aft), v(lower_aft)),
                cq.Edge.makeLine(v(lower_aft), v(lower_roof)),
                cq.Edge.makeThreePointArc(v(lower_roof), v(inner_mid), v(inner_end)),
                cq.Edge.makeLine(v(inner_end), v(inner_start)),
                cq.Edge.makeLine(v(inner_start), v(start)),
            ])
            loft.AddWire(wire.wrapped)
        loft.Build()
        fills.append(cq.Solid(loft.Shape()))
    return cq.Compound.makeCompound(fills)


def silhouette(outer, rounded_box, vertical_radius):
    """Rounded front and side edges with the rear top edge left square."""
    p = profile(outer)
    x0, x1, y0, y1, z0, z1 = outer
    wire = (cq.Workplane("YZ", origin=(x0, 0, 0))
            .moveTo(y0, z0).lineTo(*p["foot"])
            .threePointArc(p["front_mid"], p["start"]).lineTo(*p["end"])
            .threePointArc(p["top_mid"], p["roof"])
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
    rounded = body.fillet(SIDE_RADIUS, side_edges).intersect(rounded_box).clean()
    # Back-top beds on the exterior roof. Its straight side-edge chamfer stays
    # exact aft of the top curve. The leading fill follows that curve, preserving
    # the display side roll and the common silhouette at the shell seam.
    from overhang_round import rectangular_edge_fill
    aft_cap = rectangular_edge_fill(x0, x1, p["roof"][0], y1, z1, SIDE_RADIUS)
    aft_cap = aft_cap.intersect(rounded_box)
    fore_cap = _roof_fill(outer).intersect(body).intersect(rounded_box)
    # Fuse each fill into the connected body. Joining the disconnected cap
    # compounds first can discard a side's stock in the exact boolean.
    result = rounded.fuse(aft_cap).clean().fuse(fore_cap).clean()
    undersides = [face for face in result.Faces()
                  if face.geomType() == "PLANE"
                  and face.normalAt().z < -1.0 + 1e-6
                  and face.Center().z > p["foot"][1] + 1e-5]
    assert not undersides, "the swept roof has an exposed flat underside"
    return result


def rounded_prism(width, depth, radius, z0, z1, cx=0.0, cy=0.0):
    wire = cq.Workplane("XY", origin=(cx, cy, z0)).rect(width, depth).val()
    wire = wire.fillet2D(radius, wire.Vertices())
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 0, z1 - z0))
