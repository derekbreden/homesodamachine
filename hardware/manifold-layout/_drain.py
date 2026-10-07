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
PVC_BEND_R = 25.0
ADAPTER_AXIS_X = -56.0
PVC_DROP = 13.0
PVC_FORWARD_LEAD = 75.0
WHITE_REAR_LEAD = 75.0

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

def bodies(vent_tip, drain_mouth):
    """Return bodies from the hose's free end and the bulkhead's inboard mouth."""
    x, y, z = vent_tip
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
    # Clock the black assembly from down/front to front/up. The clear hose
    # reaches this station with two tangent bends, clear of the flavor-B lane.
    dx = ADAPTER_AXIS_X - x
    lo, hi = 0.0, math.pi / 2
    for _ in range(60):
        alpha = (lo + hi) / 2
        if PVC_BEND_R * (math.sin(alpha) + 1 - math.cos(alpha)) < dx:
            lo = alpha
        else:
            hi = alpha
    alpha = (lo + hi) / 2
    unit = cq.Vector(math.sin(alpha), -math.cos(alpha), 0)
    vent = cq.Vector(x, y, z)
    p0 = vent + cq.Vector(0, 0, -PVC_DROP)
    p1 = p0 + unit.multiply(PVC_BEND_R) + cq.Vector(0, 0, -PVC_BEND_R)
    m1 = p0 + unit.multiply(PVC_BEND_R * (1 - math.sqrt(.5))) + cq.Vector(0, 0, -PVC_BEND_R * math.sqrt(.5))
    center = p1 - cq.Vector(PVC_BEND_R * math.cos(alpha), PVC_BEND_R * math.sin(alpha), 0)
    p2 = center + cq.Vector(PVC_BEND_R, 0, 0)
    m2 = center + cq.Vector(PVC_BEND_R * math.cos(alpha / 2), PVC_BEND_R * math.sin(alpha / 2), 0)
    root = p2 + cq.Vector(0, -BARB_LENGTH - PVC_FORWARD_LEAD, 0)
    hose_path = cq.Wire.assembleEdges([
        cq.Edge.makeLine(vent, p0),
        cq.Edge.makeThreePointArc(p0, m1, p1),
        cq.Edge.makeThreePointArc(p1, m2, p2), cq.Edge.makeLine(p2, root)])
    hose_profile = cq.Plane(origin=vent, xDir=(1, 0, 0), normal=(0, 0, -1))
    hose = cq.Workplane(hose_profile).circle(PVC_OD / 2).circle(PVC_ID / 2).sweep(hose_path, transition="round").val()
    def clock(shape):
        return shape.translate((-x, -y, -z)).rotate((0, 0, 0), (1, 0, 0), -90).translate(root)
    barb, elbow, reducer = (clock(s) for s in (barb, elbow, reducer))
    source = root + cq.Vector(0, elbow_z - z, y - reducer_y)
    # Rise above the regulator, return downward, then approach the wall on
    # its own row. Every white-tube arc is at least R25.
    apex1 = source + cq.Vector(0, MIN_R, MIN_R)
    mid1 = source + cq.Vector(0, MIN_R * (1 - math.sqrt(.5)), MIN_R * math.sqrt(.5))
    apex2 = apex1 + cq.Vector(0, WHITE_REAR_LEAD, 0)
    end_u = apex2 + cq.Vector(0, MIN_R, -MIN_R)
    mid2 = apex2 + cq.Vector(0, MIN_R * math.sqrt(.5), -MIN_R * (1 - math.sqrt(.5)))
    end_q = end_u + cq.Vector(0, MIN_R, -MIN_R)
    mid_q = end_u + cq.Vector(0, MIN_R * (1 - math.sqrt(.5)), -MIN_R * math.sqrt(.5))
    edges = [cq.Edge.makeThreePointArc(source, mid1, apex1), cq.Edge.makeLine(apex1, apex2),
             cq.Edge.makeThreePointArc(apex2, mid2, end_u), cq.Edge.makeThreePointArc(end_u, mid_q, end_q)]
    def s_bend(start, side, displacement):
        if abs(displacement) < 1e-8:
            return start
        sign = math.copysign(1, displacement)
        angle = math.acos(1 - abs(displacement) / (2 * MIN_R))
        run = 2 * MIN_R * math.sin(angle)
        end = start + cq.Vector(0, run, 0) + side.multiply(displacement)
        halfway = start + cq.Vector(0, MIN_R * math.sin(angle), 0) + side.multiply(displacement / 2)
        first_mid = start + cq.Vector(0, MIN_R * math.sin(angle / 2), 0) + side.multiply(sign * MIN_R * (1 - math.cos(angle / 2)))
        second_mid = end - cq.Vector(0, MIN_R * math.sin(angle / 2), 0) - side.multiply(sign * MIN_R * (1 - math.cos(angle / 2)))
        edges.extend([cq.Edge.makeThreePointArc(start, first_mid, halfway), cq.Edge.makeThreePointArc(halfway, second_mid, end)])
        return end
    offset = cq.Vector(drain_mouth[0] - end_q.x, 0, drain_mouth[2] - end_q.z)
    if offset.Length > 1e-8:
        end_q = s_bend(end_q, offset.normalized(), offset.Length)
    target = cq.Vector(*drain_mouth)
    if target.y < end_q.y:
        raise ValueError("Drain return requires more rearward room")
    edges.append(cq.Edge.makeLine(end_q, target))
    path = cq.Wire.assembleEdges(edges)
    profile = cq.Plane(origin=source, xDir=(1, 0, 0), normal=(0, 0, 1))
    tube = cq.Workplane(profile).circle(OD / 2).circle(ID / 2).sweep(path, transition="round").val()
    return dict(zip(ADAPTER_NAMES, (barb, elbow, reducer))) | {"hose-drain-vent": hose, "tube-drain-vent": tube}
