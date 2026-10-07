"""The ASSE vent's black neoFit adapters and continuous white 4 mm return.

ATBC44-E (1/4-inch hose barb / stem), AEU44-E elbow, ARD4M4-E reducer.
Manufacturer envelopes, in millimetres, from the FWS dimensional sheets:
https://assets.freshwatersystems.com/image/upload/lzis3sgj4zd7j4k9ptf4.pdf
https://assets.freshwatersystems.com/image/upload/xerc4zwgwguls1fvyxde.pdf
https://assets.freshwatersystems.com/image/upload/ogt8i8sqv3vd0r25jd0r.pdf
The stem seating allowance is 15 mm; verify the marked insertion on the supplied fittings.
"""
import math
import cadquery as cq

PVC_OD = 9.525
PVC_ID = 6.35
BARB_GAP = 0.2019808375568
WHITE_REAR_LEAD = 20.8496
WHITE_LATERAL_FRACTION = 0.665
WHITE_VERTICAL_LEAD = 13.0

ADAPTER_NAMES = ("drain-barb-adapter", "drain-elbow", "drain-stem-reducer")
OD = 4.0
ID = 2.5
MIN_R = 25.0
STEM_INSERTION = 15.0
BARB_LENGTH = .709 * 25.4
BARB_OVERALL = 1.535 * 25.4
ELBOW_D = .610 * 25.4
ELBOW_BODY_D = .665 * 25.4
ELBOW_REACH = 1.134 * 25.4 - ELBOW_D / 2
REDUCER_D = .520 * 25.4
REDUCER_OVERALL = 1.445 * 25.4
REDUCER_BODY = .579 * 25.4

def _adapters(root):
    """The seated black barb, elbow and reducer, with the white-tube mouth."""
    x, y, z = root.toTuple()
    def cylinder(d, point, axis, length):
        return cq.Solid.makeCylinder(d / 2, length, cq.Vector(*point), cq.Vector(*axis))
    stem_length = .709 * 25.4
    barb = (cylinder(.270 * 25.4, (x, y, z), (0, 0, 1), BARB_LENGTH)
            .fuse(cylinder(.465 * 25.4, (x, y, z - 2.97), (0, 0, 1), 2.97))
            .fuse(cylinder(6.35, (x, y, z - 2.97 - stem_length), (0, 0, 1), stem_length))
            .cut(cylinder(ID, (x, y, z - BARB_OVERALL), (0, 0, 1), 2 * BARB_OVERALL)))
    elbow_face_z = z - 2.97 - stem_length + STEM_INSERTION
    elbow_z = elbow_face_z - ELBOW_REACH
    elbow_face_y = y - ELBOW_REACH
    elbow = (cylinder(ELBOW_BODY_D, (x, y, elbow_z), (0, 0, 1), ELBOW_REACH)
             .fuse(cylinder(ELBOW_BODY_D, (x, elbow_face_y, elbow_z), (0, 1, 0), ELBOW_REACH))
             .fuse(cq.Workplane("XY").sphere(ELBOW_BODY_D / 2).val().translate((x, y, elbow_z)))
             .cut(cylinder(6.35, (x, y, elbow_z - 3.175), (0, 0, 1), ELBOW_REACH + 3.175))
             .cut(cylinder(6.35, (x, elbow_face_y, elbow_z), (0, 1, 0), ELBOW_REACH + 3.175)).clean())
    reducer_y = elbow_face_y - REDUCER_OVERALL + STEM_INSERTION
    reducer = (cylinder(REDUCER_D, (x, reducer_y, elbow_z), (0, 1, 0), REDUCER_BODY)
               .fuse(cylinder(6.35, (x, reducer_y + REDUCER_BODY, elbow_z),
                              (0, 1, 0), REDUCER_OVERALL - REDUCER_BODY))
               .cut(cylinder(ID, (x, reducer_y, elbow_z), (0, 1, 0), REDUCER_OVERALL)))
    return barb, elbow, reducer, cq.Vector(x, reducer_y, elbow_z)


def bodies(vent_tip, drain_mouth):
    """A straight clear hose and tangent R25 white return to the DRAIN bulkhead."""
    vent = cq.Vector(*vent_tip)
    target = cq.Vector(*drain_mouth)
    root = vent - cq.Vector(0, 0, BARB_LENGTH + BARB_GAP)
    hose = (cq.Workplane(cq.Plane(origin=vent, xDir=(1, 0, 0), normal=(0, 0, -1)))
            .circle(PVC_OD / 2).circle(PVC_ID / 2)
            .sweep(cq.Edge.makeLine(vent, root)).val())
    barb, elbow, reducer, source = _adapters(root)
    radius = MIN_R
    q = math.sqrt(.5)
    forward = cq.Vector(0, -1, 0)
    side = cq.Vector(WHITE_LATERAL_FRACTION, 0,
                     math.sqrt(1 - WHITE_LATERAL_FRACTION ** 2))
    p1 = source + forward.multiply(radius) + side.multiply(radius)
    m1 = source + forward.multiply(radius * q) + side.multiply(radius * (1 - q))
    theta = math.acos(side.z)
    inward = (cq.Vector(0, 0, 1) - side.multiply(side.z)).normalized()
    p2 = p1 + side.multiply(radius * math.sin(theta)) + inward.multiply(radius * (1 - math.cos(theta)))
    m2 = p1 + side.multiply(radius * math.sin(theta / 2)) + inward.multiply(radius * (1 - math.cos(theta / 2)))
    p3 = cq.Vector(p2.x, p2.y, root.z + WHITE_VERTICAL_LEAD)
    if p3.z <= p2.z:
        raise ValueError("Drain return requires a straight vertical lead")
    p4 = p3 + cq.Vector(0, radius, radius)
    m4 = p3 + cq.Vector(0, radius * (1 - q), radius * q)
    p5 = p4 + cq.Vector(0, WHITE_REAR_LEAD, 0)
    edges = [cq.Edge.makeThreePointArc(source, m1, p1),
             cq.Edge.makeThreePointArc(p1, m2, p2), cq.Edge.makeLine(p2, p3),
             cq.Edge.makeThreePointArc(p3, m4, p4), cq.Edge.makeLine(p4, p5)]
    offset = cq.Vector(target.x - p5.x, 0, target.z - p5.z)
    theta = math.acos(1 - offset.Length / (2 * radius))
    side = offset.normalized()
    run = 2 * radius * math.sin(theta)
    end = p5 + cq.Vector(0, run, 0) + offset
    half = p5 + cq.Vector(0, radius * math.sin(theta), 0) + offset.multiply(.5)
    first_mid = p5 + cq.Vector(0, radius * math.sin(theta / 2), 0) + side.multiply(radius * (1 - math.cos(theta / 2)))
    second_mid = end - cq.Vector(0, radius * math.sin(theta / 2), 0) - side.multiply(radius * (1 - math.cos(theta / 2)))
    if target.y <= end.y:
        raise ValueError("Drain return requires a straight rearward lead")
    edges.extend([cq.Edge.makeThreePointArc(p5, first_mid, half),
                  cq.Edge.makeThreePointArc(half, second_mid, end), cq.Edge.makeLine(end, target)])
    tube = (cq.Workplane(cq.Plane(origin=source, xDir=(0, 0, 1), normal=forward))
            .circle(OD / 2).circle(ID / 2)
            .sweep(cq.Wire.assembleEdges(edges), transition="round").val())
    return dict(zip(ADAPTER_NAMES, (barb, elbow, reducer))) | {"hose-drain-vent": hose, "tube-drain-vent": tube}
