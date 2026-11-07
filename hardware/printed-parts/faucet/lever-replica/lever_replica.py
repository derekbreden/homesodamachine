"""Scan-derived faucet lever, in millimetres.

X is lateral; +Y runs from the paddle tip toward the attachment; +Z faces the
customer-visible outer surface. The inner paddle plane is Z=0. This is a local
part frame, not an assembled faucet pose. evidence/datums.json maps the scans.

The primary model has parallel lateral faces and a 9 mm cylinder channel.
`lever_replica.rs` cuts the part from its numbers (`numbers.rs`); `build()` draws
the native body for the section-art readers that still take it from Python.

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
import cadquery as cq
import trimesh

from _rust_data import request


def _data():
    return request("faucet-data", "faucet-data", {"op": "lever"})


globals().update(_data()["datums"])
for _profile in ("SHOW_PROFILE", "REAR_BOTTOM_PROFILE", "RAIL_BOTTOM_PROFILE", "STOP_TAIL",
                 "PRINTED_STOP_PROFILE", "POCKET_CEILING"):
    globals()[_profile] = [tuple(row) for row in globals()[_profile]]
for _point in ("LEDGE_LIP_START", "LEDGE_LIP_MID", "LEDGE_LIP_END"):
    globals()[_point] = tuple(globals()[_point])
LOWER_RELIEF = [(z, [tuple(p) for p in points]) for z, points in LOWER_RELIEF]
UPPER_RELIEF = [(z, [tuple(p) for p in points]) for z, points in UPPER_RELIEF]


def half_outer(z):
    return _data()["half_outer"]


def half_channel(z):
    return _data()["half_channel"]


def shape_preserving_curve(wire, points):
    """Cubic Hermite edges through measured stations, with no spline overshoot."""
    stations = request("faucet-data", "faucet-data", {"op": "pchip", "points": points})
    for start, end in zip(stations, stations[1:]):
        span = (end[0] - start[0]) / 3
        controls = [(start[0] + span, start[1] + start[2] * span),
                    (end[0] - span, end[1] - end[2] * span), tuple(end[:2])]
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
