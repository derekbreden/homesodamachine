"""Station datums for the four pump tees, the collet plate and the tubes that join them.

Coordinates are enclosure millimetres: +Y points inward and +Z points up. Each pump port
feeds one purchased PP0208E tee, its branch toward the pump and its run upright. The fore
valve stands over the run on one short tube; the rear valve's bottom port takes one R14
hairpin from the run's lower port.

THE PLATE'S AFT FACE IS THE RELEASE FACE. In service each tee stands at `connected`: its
branch collet extended, its nose on that face, and the pump tube bottomed at the tee's stop.
Pulling the cartridge drags the tee forward the collet's 1.5 mm stroke while the plate holds
the collet in, and at `released` the collet is pressed home and the tube draws out. The fore
valve's axis stands over the connected run axis, so its tube stands straight in service and
bends the whole stroke at release.

This module holds geometry data only; the dock's solids and the manifold read the same
figures.
"""

import math
import sys
from pathlib import Path

_hw = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
for _p in (_hw / "reference" / "tee-connector", _hw / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import tee_connector as tee  # noqa: E402
import _routing  # noqa: E402


TUBE_OD = tee.TUBE_D
TUBE_ID = 4.30
# The collet plate: Derek's 1/8 in plate, printed into front-top.
PLATE_T = 3.175
BRANCH_FACE = tee.BRANCH_REACH                   # extended collet face from the run axis
BRANCH_FACE_PRESSED = tee.BRANCH_PRESSED_REACH   # pressed collet face from the run axis
TRAVEL = tee.BRANCH_COLLET_TRAVEL                # the tee's whole travel: one collet stroke
RUN_FACE = tee.RUN_HALF                          # each run collet face from the tee's centre
TIP_DEPTH = tee.BRANCH_INSERTION_EXTENDED        # a bottomed tube past the extended face
# The pump tube's tip, aft of the plate's fore face, with the cartridge seated.
TIP_FROM_FORE = PLATE_T + TIP_DEPTH
# The 1/4 in LLDPE stock's bend radius (bench test on the spool) and the straight tube each
# collet keeps before a bend starts.
HAIRPIN_R = _routing.stock_of("fluid", TUBE_OD).min_bend
HAIRPIN_LEAD = 0.5
# Cut-length allowances: a tube bottomed in a run collet standing extended, and the valve's
# layout estimate. Actual fully seated marks govern factory cuts.
RUN_INSERTION = tee.RUN_INSERTION_EXTENDED
VALVE_INSERTION_NOMINAL = 12.0
STATES = ("connected", "released")


def _add(a, b):
    return tuple(a[i] + b[i] for i in range(3))


def _scale(a, k):
    return tuple(v * k for v in a)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return _scale(v, 1.0 / n)


def _line(start, direction, length):
    return {"kind": "line", "start_mm": tuple(start),
            "end_mm": _add(start, _scale(direction, length)),
            "start_tangent": tuple(direction), "end_tangent": tuple(direction),
            "length_mm": float(length)}


def _quarter(start, d_in, d_out, r):
    """A 90-degree turn of radius `r` from heading `d_in` onto `d_out`."""
    centre = _add(start, _scale(d_out, r))
    end = _add(centre, _scale(d_in, r))
    mid = _add(centre, _scale(_add(d_in, _scale(d_out, -1.0)), r / math.sqrt(2.0)))
    return {"kind": "arc", "start_mm": tuple(start), "midpoint_mm": mid, "end_mm": end,
            "radius_mm": float(r), "sweep_degrees": 90.0,
            "start_tangent": tuple(d_in), "end_tangent": tuple(d_out),
            "length_mm": r * math.pi / 2.0}


def plate_aft_y(fore_y):
    """The release face: the collet plate's aft face."""
    return fore_y + PLATE_T


def tee_axis_y(fore_y, state="connected"):
    """The tee's run axis in Y: its extended collet on the release face at `connected`, its
    pressed collet on that face one stroke further fore at `released`."""
    if state not in STATES:
        raise ValueError(f"a tee stands {' or '.join(STATES)}, not {state!r}")
    y = plate_aft_y(fore_y) + BRANCH_FACE
    return y - TRAVEL if state == "released" else y


def fore_valve_axis_y(fore_y):
    """The fore valve's port axis in Y: over its tee's connected run axis."""
    return tee_axis_y(fore_y)


def tip_y(fore_y):
    """The pump tube's seated tip: bottomed at the stop of a tee standing at connected."""
    return fore_y + TIP_FROM_FORE


def tee_ports(fore_y, x, z, state="connected"):
    """The tee's centre and its three collet faces, as point and outward axis."""
    y = tee_axis_y(fore_y, state)
    return {"centre": (x, y, z),
            "branch": {"point": (x, plate_aft_y(fore_y), z), "axis": (0.0, -1.0, 0.0)},
            "upper": {"point": (x, y, z + RUN_FACE), "axis": (0.0, 0.0, 1.0)},
            "lower": {"point": (x, y, z - RUN_FACE), "axis": (0.0, 0.0, -1.0)}}


def hairpin(start, end, r=HAIRPIN_R, lead=HAIRPIN_LEAD):
    """One tube from a downward collet at `start` to another at `end`: down, an `r` turn
    toward the other port, a straight, an `r` turn up and a straight up into it.

    The lower of the two ports keeps `lead` of straight tube before its turn begins, so the
    run's lowest surface stands `lead + r + TUBE_OD/2` under that port."""
    (x0, y0, z0), (x1, y1, z1) = start, end
    span = math.hypot(x1 - x0, y1 - y0)
    straight = span - 2.0 * r
    if straight < 0.0:
        raise ValueError(f"the ports stand {span:g} mm apart, closer than a hairpin of R{r:g}")
    across = _unit((x1 - x0, y1 - y0, 0.0))
    down, up = (0.0, 0.0, -1.0), (0.0, 0.0, 1.0)
    floor = min(z0, z1) - lead - r
    path = [_line(start, down, z0 - (floor + r))]
    path.append(_quarter(path[-1]["end_mm"], down, across, r))
    path.append(_line(path[-1]["end_mm"], across, straight))
    path.append(_quarter(path[-1]["end_mm"], across, up, r))
    path.append(_line(path[-1]["end_mm"], up, z1 - (floor + r)))
    return tuple(s for s in path if s["length_mm"] > 1e-9)


def s_bend(start, end):
    """A tube from an upward collet at `start` into a downward one at `end`, both axes
    upright: two equal arcs when the axes are offset, one straight when they are not."""
    (x0, y0, z0), (x1, y1, z1) = start, end
    length = z1 - z0
    offset = math.hypot(x1 - x0, y1 - y0)
    up = (0.0, 0.0, 1.0)
    if offset < 1e-9:
        return (_line(start, up, length),)
    side = _unit((x1 - x0, y1 - y0, 0.0))
    theta = 2.0 * math.atan2(offset, length)
    r = length / (2.0 * math.sin(theta))
    centre = _add(start, _scale(side, r))

    def at(phi):
        return _add(centre, _add(_scale(side, -r * math.cos(phi)), _scale(up, r * math.sin(phi))))

    mid = at(theta)
    turn = _add(_scale(side, math.sin(theta)), _scale(up, math.cos(theta)))
    first = {"kind": "arc", "start_mm": tuple(start), "midpoint_mm": at(theta / 2.0),
             "end_mm": mid, "radius_mm": r, "sweep_degrees": math.degrees(theta),
             "start_tangent": up, "end_tangent": turn, "length_mm": r * theta}
    mirror = lambda p: tuple(2.0 * mid[i] - p[i] for i in range(3))  # noqa: E731
    second = {"kind": "arc", "start_mm": mid, "midpoint_mm": mirror(at(theta / 2.0)),
              "end_mm": tuple(end), "radius_mm": r, "sweep_degrees": math.degrees(theta),
              "start_tangent": turn, "end_tangent": up, "length_mm": r * theta}
    return first, second


def station(fore_y, x, z, upper_port, return_port):
    """One pump port's tee, its fore valve's tube and its hairpin to the rear valve."""
    ports = tee_ports(fore_y, x, z)
    upper_start = ports["upper"]["point"]
    lower_start = ports["lower"]["point"]
    upper = s_bend(upper_start, tuple(upper_port["point"]))
    lower = hairpin(lower_start, tuple(return_port["point"]))
    return {"tee": ports, "released": tee_ports(fore_y, x, z, "released"),
            "upper_target": dict(upper_port), "return_target": dict(return_port),
            "upper_tube": upper, "hairpin": lower,
            "upper_exposed_mm": sum(s["length_mm"] for s in upper),
            "hairpin_exposed_mm": sum(s["length_mm"] for s in lower),
            "hairpin_floor_z": min(lower_start[2], return_port["point"][2])
                               - HAIRPIN_LEAD - HAIRPIN_R - TUBE_OD / 2.0}


def layouts(plate):
    return {str(x): station(plate["fore_y"], x, z, plate["upper_ports"][str(x)],
                            plate["return_ports"][str(x)])
            for x, z in plate["holes"]}


def sweep(diameter, segments):
    """A round tube of `diameter` swept along the centreline `segments`."""
    import cadquery as cq
    edges = []
    for s in segments:
        a, b = cq.Vector(*s["start_mm"]), cq.Vector(*s["end_mm"])
        edges.append(cq.Edge.makeThreePointArc(a, cq.Vector(*s["midpoint_mm"]), b)
                     if s["kind"] == "arc" else cq.Edge.makeLine(a, b))
    first = segments[0]
    profile = cq.Wire.makeCircle(diameter / 2.0, cq.Vector(*first["start_mm"]),
                                 cq.Vector(*first["start_tangent"]))
    return cq.Solid.sweep(profile, [], cq.Wire.assembleEdges(edges), makeSolid=True,
                          isFrenet=True)


def tube(segments):
    """The tube itself: its outside swept, its bore swept out."""
    return sweep(TUBE_OD, segments).cut(sweep(TUBE_ID, segments)).clean()
