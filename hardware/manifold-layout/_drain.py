"""Direct TPU ASSE sleeve and the white 4 mm return in one vertical plane.

The 4 mm LLDPE follows two tangent reverse-curvature R25 arcs, starting
downward and finishing aft on the OVER bulkhead's axis. The short straight
lead keeps the first bend outside the sleeve's tube socket.
"""
import math
from pathlib import Path
import sys

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "printed-parts/asse-drain-adapter"))
import asse_drain_adapter as adapter

ADAPTER_NAMES = ("asse-drain-adapter",)
OD = 4.0
ID = 2.5
MIN_R = 25.0
STRAIGHT_EXIT = 3.0


def route(vent_tip, drain_mouth):
    """Exact outside centreline, plus the 14 mm engaged sleeve-end segment."""
    source = cq.Vector(*adapter.tube_mouth(vent_tip))
    target = cq.Vector(*drain_mouth)
    if abs(target.x - source.x) > 1e-5:
        raise ValueError("The ASSE vent and OVER bulkhead must share their X column")
    start = source - cq.Vector(0, 0, STRAIGHT_EXIT)
    radius = MIN_R
    rise = target.z - start.z
    theta = math.acos((1 - rise / radius) / 2)
    aft_reach = radius * (1 + 2 * math.sin(theta))
    end = cq.Vector(start.x, start.y + aft_reach, target.z)
    if target.y <= end.y:
        raise ValueError("The OVER return needs a straight lead after its R25 bends")
    first_angle = math.pi / 2 + theta
    first_end = cq.Vector(start.x, start.y + radius * (1 + math.sin(theta)),
                          start.z - radius * math.cos(theta))
    first_mid = cq.Vector(start.x, start.y + radius * (1 - math.cos(first_angle / 2)),
                          start.z - radius * math.sin(first_angle / 2))
    second_mid = first_end + cq.Vector(
        0, radius * (math.sin(theta) - math.sin(theta / 2)),
        radius * (math.cos(theta / 2) - math.cos(theta)))
    inserted_end = source + cq.Vector(0, 0, adapter.TUBE_DEPTH)
    edges = [cq.Edge.makeLine(inserted_end, start),
             cq.Edge.makeThreePointArc(start, first_mid, first_end),
             cq.Edge.makeThreePointArc(first_end, second_mid, end),
             cq.Edge.makeLine(end, target)]
    return source, cq.Wire.assembleEdges(edges), {
        "outside_length_mm": STRAIGHT_EXIT + radius * (math.pi / 2 + 2 * theta)
                             + target.y - end.y,
        "sleeve_insertion_mm": adapter.TUBE_DEPTH,
        "initial_straight_mm": STRAIGHT_EXIT,
        "bulkhead_straight_mm": target.y - end.y,
        "bend_radii_mm": [radius, radius],
        "bend_angles_deg": [math.degrees(first_angle), math.degrees(theta)],
        "scope": "Nominal centreline. Tube cut length adds the marked bulkhead insertion.",
    }


def bodies(vent_tip, drain_mouth):
    source, wire, _ = route(vent_tip, drain_mouth)
    tube = (cq.Workplane(cq.Plane(origin=source + cq.Vector(0, 0, adapter.TUBE_DEPTH),
                                 xDir=(1, 0, 0), normal=(0, 0, -1)))
            .circle(OD / 2).circle(ID / 2).sweep(wire, transition="round").val())
    return {"asse-drain-adapter": adapter.placed(vent_tip), "tube-drain-vent": tube}
