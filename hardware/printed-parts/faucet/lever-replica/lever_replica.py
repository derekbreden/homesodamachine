"""Scan-derived comparison faucet lever, in millimetres.

X is lateral; +Y runs from the paddle tip toward the attachment; +Z faces the
customer-visible outer surface. The inner paddle plane is Z=0. This is a local
part frame, not an assembled faucet pose. evidence/datums.json maps the scans.

The side faces and the channel walls are both drafted, so a width here is only
meaningful with the height it was read at, and the channel converges into the
rear stops over its last four millimetres. Those are what the transverse metal
cylinder runs along.

The rear portion of each ledge's upper face is occluded: LEDGE_TOP is a
fit-trial parameter, not a measurement.
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

# Both side faces and both channel walls are drafted. Each figure is a least
# squares line through 0.5 mm Z bins of the scan's pooled left and right
# surfaces over the straight run, y 6 to 37 — the channel to 0.024 mm, the
# outside to 0.031 mm. Half-width grows with Z: the part is widest at the show
# face and narrowest down at the ledge.
CHANNEL_HALF_AT_Z0 = 4.4297
CHANNEL_DRAFT = 0.02672        # mm of half-width per mm of Z; 1.53 deg per side
OUTER_HALF_AT_Z0 = 6.3827
OUTER_DRAFT = 0.01932          # 1.11 deg per side
# The wall between them runs 1.95 mm at Z=0 and 1.99 mm at the ledge. That is a
# consequence of the two drafts, not a figure imposed on them.

# The 2026-09-20 black PET-GF print measured 8.4 mm across a modelled 8.60 mm
# channel. The printable body carries that difference so the printed part lands
# on the donor's width; the STEP, the payload and the assembly pose carry the
# donor itself. Zero it once a print measures at the donor's width.
CHANNEL_PRINT_ALLOWANCE = 0.20

OUTSIDE_REACH = 20.0           # clears the part, for construction solids
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

# The channel's straight run ends near y = 40 and converges into the stops.
# These are the scan's own half-widths at the cylinder's seat height, given as
# an offset from the straight wall; they replace a drawn continuation. The
# convergence is read at one height and applied at every height — the scan
# shows it is stronger low in the channel than high.
CHANNEL_CONVERGENCE = [
    (40.25, +0.000), (40.75, -0.012), (41.25, -0.042), (41.75, -0.067),
    (42.25, -0.092), (42.75, -0.124), (43.25, -0.166), (43.75, -0.204),
    (44.25, -0.259), (44.75, -0.312),
]
# The throat, from the two independently captured stop patches inward. X is the
# lateral magnitude; these carry no draft.
STOP_TAIL = [
    (3.80, 45.31), (3.50, 45.40), (3.00, 45.48),
    (2.70, 45.53), (2.50, 45.60), (2.30, 45.72), (2.20, 45.92),
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
    """Outside half-width at a height, along the drafted side face."""
    return OUTER_HALF_AT_Z0 + OUTER_DRAFT * z


def half_channel(z, allowance=0.0):
    """Channel half-width at a height, along the drafted inner wall."""
    return CHANNEL_HALF_AT_Z0 + CHANNEL_DRAFT * z + allowance / 2


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


def side_face(sign):
    """One drafted side face, as the solid outside it."""
    z_low, z_high = CUT_BELOW - 2, CUT_ABOVE + 2
    plane = cq.Plane(origin=(0, CUT_REAR + 5, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    outside = sign * (OUTSIDE_REACH + 5)   # past the silhouette, so no coincident face
    return (cq.Workplane(plane)
            .polyline([(sign * half_outer(z_low), z_low),
                       (sign * half_outer(z_high), z_high),
                       (outside, z_high), (outside, z_low)])
            .close()
            .extrude(CUT_REAR + 5 - (CUT_FRONT - 5)))


def outer_envelope():
    """Side silhouette, extruded wide and then cut back to the drafted sides."""
    plane = cq.Plane(origin=(-OUTSIDE_REACH, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
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
    body = wire.extrude(2 * OUTSIDE_REACH)
    return body.cut(side_face(+1)).cut(side_face(-1))


def pocket_footprint(z, allowance):
    """Channel footprint at one height: drafted walls into the measured stops."""
    half = half_channel(z, allowance)
    r = POCKET_FRONT_RADIUS
    front = POCKET_START_Y
    wall = [(half + delta, y) for y, delta in CHANNEL_CONVERGENCE]
    return (cq.Workplane("XY", origin=(0, 0, z))
            .moveTo(-half + r, front).lineTo(half - r, front)
            .radiusArc((half, front + r), -r)
            .polyline(wall, includeCurrent=True)
            .spline(STOP_TAIL, includeCurrent=True)
            .lineTo(0.0, POCKET_STOP_JOIN_Y)
            .lineTo(-STOP_TAIL[-1][0], STOP_TAIL[-1][1])
            .spline([(-x, y) for x, y in reversed(STOP_TAIL[:-1])], includeCurrent=True)
            .polyline([(-(half + delta), y) for y, delta in reversed(CHANNEL_CONVERGENCE)],
                      includeCurrent=True)
            .lineTo(-half, front + r)
            .radiusArc((-half + r, front), -r).wire().val())


def pocket_outline(allowance):
    """The channel, lofted between its lowest and highest footprints.

    Half-width is linear in Z, so a ruled loft reproduces the drafted walls
    exactly; the stop throat is the same curve at both ends and stays upright.
    """
    return cq.Workplane("XY").add(cq.Solid.makeLoft(
        [pocket_footprint(CUT_BELOW, allowance),
         pocket_footprint(CUT_ABOVE, allowance)], ruled=True))


def pocket_height():
    """The ledge lip is observed; its unseen horizontal continuation is inferred."""
    plane = cq.Plane(origin=(-OUTSIDE_REACH, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    wire = (cq.Workplane(plane).moveTo(CUT_FRONT, FLOOR_Z)
            .lineTo(30.0, FLOOR_Z)
            .spline(POCKET_CEILING, includeCurrent=True)
            .lineTo(POCKET_STOP_JOIN_Y, LEDGE_TOP)
            .lineTo(*LEDGE_LIP_END)
            .threePointArc(LEDGE_LIP_MID, LEDGE_LIP_START)
            .lineTo(36.0, CUT_BELOW).lineTo(CUT_FRONT, CUT_BELOW)
            .lineTo(CUT_FRONT, FLOOR_Z).wire())
    return wire.extrude(2 * OUTSIDE_REACH)


def relief_wire(z, right):
    """A symmetric open-ended slot, closed outside the part for the boolean."""
    first = right[0]
    wire = cq.Workplane("XY", origin=(0, 0, z)).moveTo(-first[0], first[1]).lineTo(*first)
    # Each station has the same edge topology, so the ruled loft cannot twist.
    wire = wire.lineTo(*right[1]).spline(right[2:], includeCurrent=True)
    wire = wire.lineTo(OUTSIDE_REACH, CUT_REAR).lineTo(-OUTSIDE_REACH, CUT_REAR)
    wire = wire.lineTo(-right[-1][0], right[-1][1])
    wire = wire.spline([(-x, y) for x, y in reversed(right[1:-1])], includeCurrent=True)
    return wire.lineTo(-first[0], first[1]).wire().val()


def relief(stations):
    return cq.Workplane("XY").add(cq.Solid.makeLoft([relief_wire(z, p) for z, p in stations], ruled=True))


def build(channel_allowance=0.0):
    body = outer_envelope()
    body = body.cut(pocket_outline(channel_allowance).intersect(pocket_height()))
    body = body.cut(relief(LOWER_RELIEF)).cut(relief(UPPER_RELIEF)).clean()
    if not body.val().isValid() or len(body.solids().vals()) != 1:
        raise RuntimeError("Comparison lever must be one valid solid")
    return body


def print_pose(body):
    """Right side on the bed; long fibres/roads can run tip to attachment."""
    turned = body.rotate((0, 0, 0), (0, 1, 0), 90)
    return turned.translate((0, 0, -turned.val().BoundingBox().zmin))


def main():
    body = build()
    printable = build(CHANNEL_PRINT_ALLOWANCE)
    step = HERE / "lever-replica.step"
    stl = HERE / "lever-replica.stl"
    export_assembly(cq.Assembly(body, name="lever-replica", color=cq.Color(0.91, 0.91, 0.87)), str(step))
    cq.exporters.export(body, str(stl), tolerance=STL_TOLERANCE, angularTolerance=STL_ANGLE_TOLERANCE)
    export_payload(step, stl, preserve_print_triangles=True)
    cq.exporters.export(print_pose(printable), str(HERE / "lever-replica-side-down.stl"),
                        tolerance=STL_TOLERANCE, angularTolerance=STL_ANGLE_TOLERANCE)
    printed = trimesh.load(stl, force="mesh")
    result = {"valid_brep": body.val().isValid(), "solids": len(body.solids().vals()),
              "volume_mm3": body.val().Volume(),
              "mesh_bounds_mm": printed.bounds.tolist(),
              "status": "comparison prototype; physical attachment and travel unvalidated",
              "inferred": ["ledge upper continuation", "bilateral symmetry",
                           "channel convergence read at one height, applied at all",
                           "unobserved transitions between relief sections"],
              "channel_print_allowance_mm": CHANNEL_PRINT_ALLOWANCE,
              "allowance_applies_to": "lever-replica-side-down.stl only; the STEP, the "
                                      "payload and the assembly pose are the donor",
              "printable_volume_mm3": printable.val().Volume(),
              "widths_mm": {f"z={z}": {"channel": round(2 * half_channel(z), 3),
                                       "outside": round(2 * half_outer(z), 3),
                                       "wall": round(half_outer(z) - half_channel(z), 3)}
                            for z in (0.0, -3.25, -5.55)}}
    (HERE / "geometry-check.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
