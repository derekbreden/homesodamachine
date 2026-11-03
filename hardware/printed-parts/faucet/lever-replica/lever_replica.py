"""Scan-derived faucet lever, in millimetres.

X is lateral; +Y runs from the paddle tip toward the attachment; +Z faces the
customer-visible outer surface. The inner paddle plane is Z=0. This is a local
part frame, not an assembled faucet pose. evidence/datums.json maps the scans.

The primary model has parallel lateral faces and a 9 mm cylinder channel.
`numbers()` supplies the kernel stations; `build()` retains the native body
for section-art readers.

The rear portion of each ledge's upper face is occluded: LEDGE_TOP is a
fit-trial parameter, not a measurement.

The printable body has no draft on either lateral face. The part lies on its
side to print, so those faces are the bed contact and the top surface and the
channel is a bridged gap; a slope on any of them does not survive.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
sys.path.insert(0, str(HARDWARE / "scripts"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
import trimesh
from scipy.interpolate import PchipInterpolator
from flute_payload import cut as export_payload

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


def numbers():
    """Measured stations and matching PCHIP slopes in the lever's authored frame."""
    from _materials import linear

    def pchip_stations(points):
        increasing = sorted(points)
        fn = PchipInterpolator([p[0] for p in increasing], [p[1] for p in increasing])
        slope = fn.derivative()
        return [[x, y, float(slope(x))] for x, y in points]

    return {
        "name": "lever-replica", "color": list(linear(cq.Color(0.91, 0.91, 0.87))),
        "outside_width": PRINTED_OUTSIDE_WIDTH, "channel_width": CHANNEL_PRINTED_WIDTH,
        "floor_z": FLOOR_Z, "ledge_top": LEDGE_TOP,
        "cut_below": CUT_BELOW, "cut_above": CUT_ABOVE,
        "cut_front": CUT_FRONT, "cut_rear": CUT_REAR,
        "outer_start": [0.0, 0.8], "tip_arc": [[0.1, 2.4], SHOW_PROFILE[0]],
        "show_pchip": pchip_stations(SHOW_PROFILE),
        "rear_arc": [[52.65, 0.2], [52.0, -4.0]],
        "rear_bottom": REAR_BOTTOM_PROFILE,
        "outer_corner": [[37.5, -10.15], [36.8, -10.05], [36.70, -9.5]],
        "rail_start": [36.65, -5.55],
        "rail_pchip": pchip_stations([(36.65, -5.55)] + RAIL_BOTTOM_PROFILE),
        "tip_return_mid": [0.35, -0.2],
        "pocket_start": POCKET_START_Y, "pocket_front_radius": POCKET_FRONT_RADIUS,
        "pocket_stop_join": POCKET_STOP_JOIN_Y, "stop_profile": PRINTED_STOP_PROFILE,
        "pocket_floor_end": [30.0, FLOOR_Z], "pocket_ceiling": POCKET_CEILING,
        "ledge_lip": [LEDGE_LIP_START, LEDGE_LIP_MID, LEDGE_LIP_END],
        "pocket_lower_corner": [36.0, CUT_BELOW],
        "lower_relief": [{"z": z, "right": points} for z, points in LOWER_RELIEF],
        "upper_relief": [{"z": z, "right": points} for z, points in UPPER_RELIEF],
    }


FRAME_DATA = HERE / "lever-replica.frame.json"


def write_frame_data(step):
    """The authored STEP's exact native bounds for its assembly seating datum."""
    from _cadq_export import _atomic_write, import_step

    step = Path(step)
    bounds = import_step(step).val().BoundingBox()
    record = {
        "source": {"path": step.relative_to(HARDWARE.parent).as_posix(),
                   "sha256": hashlib.sha256(step.read_bytes()).hexdigest()},
        "query": "import_step().val().BoundingBox()",
        "bounds_mm": [[bounds.xmin, bounds.ymin, bounds.zmin],
                      [bounds.xmax, bounds.ymax, bounds.zmax]],
    }
    text = json.dumps(record, indent=2, sort_keys=True) + "\n"
    _atomic_write(FRAME_DATA, lambda path: Path(path).write_text(text))
    return record


def main():
    import _rust_part

    _rust_part.cut("faucet", "lever-replica", numbers(), HERE)
    step = HERE / "lever-replica.step"
    stl = HERE / "lever-replica.stl"
    print_stl = HERE / "lever-replica-side-down.stl"
    # The viewer and printer use the same emitted triangles in their own frames.
    local_mesh = trimesh.load(print_stl, force="mesh", process=False)
    local_mesh.apply_transform([[0, 0, -1, PRINTED_OUTSIDE_WIDTH / 2],
                                [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]])
    local_mesh.export(stl)
    export_payload(step, stl, preserve_print_triangles=True)

if __name__ == "__main__":
    main()
