"""Physically accepted scan-derived faucet lever, in millimetres.

X is lateral; +Y runs from the paddle tip toward the attachment; +Z faces the
customer-visible outer surface. The inner paddle plane is Z=0. This is a local
part frame, not an assembled faucet pose. evidence/datums.json maps the scans.

The primary model has parallel lateral faces and a 9 mm cylinder channel.
`build()` supplies the canonical printable and assembled lever.

The rear portion of each ledge's upper face is occluded: LEDGE_TOP is a
fit-trial parameter, not a measurement.

The printable body has no draft on either lateral face. The part lies on its
side to print, so those faces are the bed contact and the top surface and the
channel is a bridged gap; a slope on any of them does not survive.
"""

import json
import sys
from pathlib import Path

import cadquery as cq
import trimesh
from scipy.interpolate import PchipInterpolator

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_assembly
from flute_payload import cut as export_payload
from physical_acceptance import for_printed_model

# Accepted parallel side faces and cylinder channel, in millimetres.
PRINTED_OUTSIDE_WIDTH = 12.40
CHANNEL_PRINTED_WIDTH = 9.00

FLOOR_Z = 0.0
LEDGE_TOP = -5.55
LOWER_SLOT_HALF_WIDTH = 1.45
CUT_BELOW = -14.0
CUT_ABOVE = 7.0
CUT_FRONT = -3.0
CUT_REAR = 60.0
STL_TOLERANCE = 0.035
STL_ANGLE_TOLERANCE = 0.12

# Y,Z section of the outer face, sampled from the measured centre and side views.
SHOW_PROFILE = [
    (0.8, 2.95), (5.0, 2.84), (15.0, 2.74), (25.0, 2.77),
    (35.0, 2.94), (37.0, 2.97), (38.5, 4.08), (40.0, 4.43),
    (41.5, 4.05), (43.0, 3.13), (46.0, 3.00), (49.5, 3.04),
    (50.5, 3.00),
]
REAR_BOTTOM_PROFILE = [(51.0, -7.5), (50.2, -8.85), (49.3, -9.03)]
RAIL_BOTTOM_PROFILE = [
    (35.0, -5.30), (30.0, -4.86), (20.0, -3.76), (10.0, -2.56),
    (5.0, -1.88), (1.1, -0.75),
]

# The throat, from the two independently captured stop patches inward. X is the
# lateral magnitude; these carry no draft.
STOP_TAIL = [
    (3.80, 45.31), (3.50, 45.40), (3.00, 45.48),
    (2.70, 45.53), (2.50, 45.60), (2.30, 45.72), (2.20, 45.92),
]
PRINTED_STOP_PROFILE = [
    (CHANNEL_PRINTED_WIDTH / 2, 44.30), (4.20, 44.90), (4.00, 45.18),
    *STOP_TAIL,
]
POCKET_START_Y = 1.2
POCKET_FRONT_RADIUS = 0.5
POCKET_STOP_JOIN_Y = 46.1
POCKET_CEILING = [(37.0, 0.12), (39.0, 0.12), (42.0, -0.38),
                  (44.0, -0.52), (POCKET_STOP_JOIN_Y, -0.55)]
LEDGE_LIP_START = (36.70, -10.18)
LEDGE_LIP_MID = (37.7, -7.25)
LEDGE_LIP_END = (40.50, LEDGE_TOP)

# Separate lofts keep the observed upper pocket, lower slot, and sloped spout
# relief independent. Profiles are X,Y, from the centre-side start toward rear.
# The rear mouth is extended outside the solid so every relief is open.
LOWER_RELIEF = [
    (-11.5, [(LOWER_SLOT_HALF_WIDTH, POCKET_START_Y), (LOWER_SLOT_HALF_WIDTH, 47.5),
             (2.1, 48.2), (4.4, 50.2), (5.4, 52.7)]),
    (LEDGE_TOP, [(1.65, POCKET_START_Y), (1.65, 47.5),
                 (2.2, 48.2), (4.4, 50.2), (5.4, 52.7)]),
    (-0.55, [(2.20, POCKET_START_Y), (2.20, 47.5),
             (2.6, 48.25), (4.4, 50.2), (5.4, 52.7)]),
]
UPPER_RELIEF = [
    (-0.56, [(0.25, 47.22), (2.2, 48.05), (3.5, 49.0),
             (4.4, 50.2), (5.4, 52.7)]),
    (2.75, [(2.20, 42.65), (3.35, 43.1), (3.90, 44.5),
            (4.50, 48.0), (5.4, 52.7)]),
    (5.20, [(5.30, 39.1), (5.80, 40.0), (6.40, 42.0),
            (7.00, 48.0), (8.0, 52.7)]),
]


def half_outer(z):
    return PRINTED_OUTSIDE_WIDTH / 2


def half_channel(z):
    return CHANNEL_PRINTED_WIDTH / 2


def shape_preserving_curve(wire, points):
    """Cubic Hermite edges through measured stations, with no spline overshoot."""
    increasing = sorted(points)
    fn = PchipInterpolator([p[0] for p in increasing], [p[1] for p in increasing])
    slopes = fn.derivative()
    for start, end in zip(points, points[1:]):
        span = (end[0] - start[0]) / 3
        controls = [(start[0] + span, start[1] + float(slopes(start[0])) * span),
                    (end[0] - span, end[1] - float(slopes(end[0])) * span), end]
        wire = wire.bezier(controls, includeCurrent=True)
    return wire


def outer_envelope():
    """Side silhouette, extruded wide and then cut back to the side faces."""
    reach = PRINTED_OUTSIDE_WIDTH / 2
    plane = cq.Plane(origin=(-reach, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    wire = cq.Workplane(plane).moveTo(0.0, 0.8).threePointArc((0.1, 2.4), SHOW_PROFILE[0])
    wire = shape_preserving_curve(wire, SHOW_PROFILE)
    wire = (wire
            .threePointArc((52.65, 0.2), (52.0, -4.0))
            .spline(REAR_BOTTOM_PROFILE, includeCurrent=True)
            .lineTo(37.5, -10.15)
            .threePointArc((36.8, -10.05), (36.70, -9.5))
            .lineTo(36.65, -5.55))
    wire = shape_preserving_curve(wire, [(36.65, -5.55)] + RAIL_BOTTOM_PROFILE)
    wire = (wire
            .threePointArc((0.35, -0.2), (0.0, 0.8))
            .wire())
    body = wire.extrude(2 * reach)
    return body


def pocket_outline():
    """Straight 9 mm channel and the accepted cylinder pocket."""
    front, r = POCKET_START_Y, POCKET_FRONT_RADIUS
    half = CHANNEL_PRINTED_WIDTH / 2
    stop = PRINTED_STOP_PROFILE
    wire = (cq.Workplane("XY", origin=(0, 0, CUT_BELOW))
            .moveTo(-half + r, front).lineTo(half - r, front)
            .radiusArc((half, front + r), -r)
            .lineTo(*stop[0])
            .spline(stop[1:], includeCurrent=True)
            .lineTo(0.0, POCKET_STOP_JOIN_Y)
            .lineTo(-stop[-1][0], stop[-1][1])
            .spline([(-x, y) for x, y in reversed(stop[:-1])], includeCurrent=True)
            .lineTo(-half, front + r)
            .radiusArc((-half + r, front), -r).wire())
    return wire.extrude(CUT_ABOVE - CUT_BELOW)


def pocket_height():
    """The ledge lip is observed; its unseen horizontal continuation is inferred."""
    reach = PRINTED_OUTSIDE_WIDTH / 2 + 1
    plane = cq.Plane(origin=(-reach, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    wire = (cq.Workplane(plane).moveTo(CUT_FRONT, FLOOR_Z)
            .lineTo(30.0, FLOOR_Z)
            .spline(POCKET_CEILING, includeCurrent=True)
            .lineTo(POCKET_STOP_JOIN_Y, LEDGE_TOP)
            .lineTo(*LEDGE_LIP_END)
            .threePointArc(LEDGE_LIP_MID, LEDGE_LIP_START)
            .lineTo(36.0, CUT_BELOW).lineTo(CUT_FRONT, CUT_BELOW)
            .lineTo(CUT_FRONT, FLOOR_Z).wire())
    return wire.extrude(2 * reach)


def relief_wire(z, right):
    """A symmetric open-ended slot, closed outside the part for the boolean."""
    first = right[0]
    wire = cq.Workplane("XY", origin=(0, 0, z)).moveTo(-first[0], first[1]).lineTo(*first)
    # Each station has the same edge topology, so the ruled loft cannot twist.
    wire = wire.lineTo(*right[1]).spline(right[2:], includeCurrent=True)
    reach = PRINTED_OUTSIDE_WIDTH / 2 + 3
    wire = wire.lineTo(reach, CUT_REAR).lineTo(-reach, CUT_REAR)
    wire = wire.lineTo(-right[-1][0], right[-1][1])
    wire = wire.spline([(-x, y) for x, y in reversed(right[1:-1])], includeCurrent=True)
    return wire.lineTo(-first[0], first[1]).wire().val()


def relief(stations):
    return cq.Workplane("XY").add(cq.Solid.makeLoft(
        [relief_wire(z, p) for z, p in stations], ruled=True))


def build():
    body = outer_envelope()
    body = body.cut(pocket_outline().intersect(pocket_height()))
    body = body.cut(relief(LOWER_RELIEF)).cut(relief(UPPER_RELIEF)).clean()
    if not body.val().isValid() or len(body.solids().vals()) != 1:
        raise RuntimeError("Faucet lever must be one valid solid")
    return body


def print_pose(body):
    """Right side on the bed; long fibres/roads can run tip to attachment."""
    turned = body.rotate((0, 0, 0), (0, 1, 0), 90)
    return turned.translate((0, 0, PRINTED_OUTSIDE_WIDTH / 2))


def main():
    printable = build()
    step = HERE / "lever-replica.step"
    stl = HERE / "lever-replica.stl"
    export_assembly(cq.Assembly(printable, name="lever", color=cq.Color(0.91, 0.91, 0.87)), str(step))
    print_stl = HERE / "lever-replica-side-down.stl"
    cq.exporters.export(print_pose(printable), str(print_stl),
                        tolerance=STL_TOLERANCE, angularTolerance=STL_ANGLE_TOLERANCE)
    # One tessellation serves the printer and the viewer. OCCT may triangulate the
    # same analytic face differently after rotation; undo the print pose on its
    # accepted triangles instead of asking for a second local-frame tessellation.
    local_mesh = trimesh.load(print_stl, force="mesh", process=False)
    local_mesh.apply_transform([[0, 0, -1, PRINTED_OUTSIDE_WIDTH / 2],
                                [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
    local_mesh.export(stl)
    export_payload(step, stl, preserve_print_triangles=True)
    mesh = trimesh.load(stl, force="mesh")
    acceptance = for_printed_model()
    result = {"valid_brep": printable.val().isValid(), "solids": len(printable.solids().vals()),
              "volume_mm3": printable.val().Volume(),
              "mesh_bounds_mm": mesh.bounds.tolist(),
              "status": ("physical fit and functional operation confirmed by Derek"
                         if acceptance["matches_accepted_geometry"]
                         else "current geometry has no matching physical acceptance"),
              "physical_acceptance": acceptance,
              "inferred": ["ledge upper continuation", "bilateral symmetry",
                           "unobserved transitions between relief sections"],
              "printed_channel_mm": CHANNEL_PRINTED_WIDTH,
              "printed_outside_mm": PRINTED_OUTSIDE_WIDTH,
              "printed_channel_applies_to": "primary lever-replica STEP, STL, viewer payload and side-down print STL",
              "printable_volume_mm3": printable.val().Volume(),
              "widths_mm": {f"z={z}": {"channel": round(2 * half_channel(z), 3),
                                       "outside": round(2 * half_outer(z), 3),
                                       "wall": round(half_outer(z) - half_channel(z), 3)}
                            for z in (0.0, -3.25, -5.55)}}

    (HERE / "geometry-check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
