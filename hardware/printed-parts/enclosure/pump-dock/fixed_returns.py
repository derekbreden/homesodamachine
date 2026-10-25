"""Station datums for the four pump tees, the tee wall's fore band and the fittings and tubes
that join them.

Coordinates are enclosure millimetres: +Y points inward and +Z points up. Each pump port
feeds one purchased PP0208E tee, its branch toward the pump and its run upright. The fore
valve stands over the run on one short straight tube. The lower return reaches the rear valve's
bottom port: a trimmed NeoFit stem elbow in the tee's lower collet, one straight tube, and a
second stem elbow in the valve.

THE FORE BAND'S AFT FACE IS THE BORE FACE. Each tee's branch bore opens on it, and the tee
stands with its fixed branch barrel just aft of it. The branch collet stands extended in its
recess ahead of that face and grips the pump tube like any push-fit; the tube is pushed home
once, at the factory, to the tee's stop.

This module holds geometry data only; the dock's solids and the manifold read the same
figures.
"""

import math
import sys
from pathlib import Path

_hw = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
for _p in (_hw / "reference" / "tee-connector", _hw / "reference" / "neofit-stem-elbow",
           _hw / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import tee_connector as tee  # noqa: E402
import neofit_stem_elbow as elbow  # noqa: E402


TUBE_OD = tee.TUBE_D
TUBE_ID = 4.30
# The tee wall's fore band, from the bay face to the bore face.
PLATE_T = 3.175 + tee.BRANCH_COLLET_TRAVEL
# The tee's run axis aft of the bore face: its fixed branch barrel stands
# `BORE_FACE_TO_AXIS - tee.BRANCH_FIXED_END` aft of that face, the stop it lands on pushed fore.
BORE_FACE_TO_AXIS = tee.BRANCH_PRESSED_REACH
RUN_FACE = tee.RUN_HALF                          # each run collet face from the tee's centre
TIP_DEPTH = tee.INSERTION                        # a bottomed tube's tip past the bore face
# The pump tube's tip, aft of the fore band's bay face, with the cradle home.
TIP_FROM_FORE = PLATE_T + TIP_DEPTH
# Seat depths: a stem or tube bottomed in a run collet standing extended, and the valve's
# layout estimate. Actual fully seated marks govern factory cuts.
RUN_INSERTION = tee.RUN_INSERTION_EXTENDED
VALVE_INSERTION_NOMINAL = 12.0
# A stem elbow's axes cross this far under the face its shoulder stands on.
ELBOW_DROP = elbow.HUB_BACK_REACH


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


def plate_aft_y(fore_y):
    """The bore face: the fore band's aft face."""
    return fore_y + PLATE_T


def tee_axis_y(fore_y):
    """The tee's run axis in Y."""
    return plate_aft_y(fore_y) + BORE_FACE_TO_AXIS


def fore_valve_axis_y(fore_y):
    """The fore valve's port axis in Y: over its tee's run axis."""
    return tee_axis_y(fore_y)


def tip_y(fore_y):
    """The pump tube's seated tip: bottomed at the tee's stop."""
    return fore_y + TIP_FROM_FORE


def tee_ports(fore_y, x, z):
    """The tee's centre and its three collet faces, as point and outward axis."""
    y = tee_axis_y(fore_y)
    return {"centre": (x, y, z),
            "branch": {"point": (x, plate_aft_y(fore_y), z), "axis": (0.0, -1.0, 0.0)},
            "upper": {"point": (x, y, z + RUN_FACE), "axis": (0.0, 0.0, 1.0)},
            "lower": {"point": (x, y, z - RUN_FACE), "axis": (0.0, 0.0, -1.0)}}


def elbow_return(start, end):
    """The lower return from the tee's downward lower collet at `start` to the rear valve's
    downward bottom collet at `end`: a stem elbow in each, one straight tube between them.

    The tee's elbow is cut to the run collet's seat depth, so its shoulder stands on the collet
    face and its axes cross `ELBOW_DROP` under it. The valve's elbow keeps enough stem below its
    collet to cross at that same height, so the two sockets face each other on one straight
    line and the tube between them runs level. Each `elbows` row is the elbow's crossing, the
    way its socket opens, its stem's length past the shoulder and how much of that stands
    outside the collet."""
    (x0, y0, z0), (x1, y1, z1) = start, end
    z = z0 - ELBOW_DROP
    showing = z1 - ELBOW_DROP - z
    spare = elbow.STEM_LENGTH - VALVE_INSERTION_NOMINAL
    if not -1e-9 <= showing <= spare + 1e-9:
        raise ValueError(
            f"the valve's collet stands {z1 - z0:+g} mm off the tee's, so its elbow would show "
            f"{showing:g} mm of stem below it, outside the 0 to {spare:g} mm its stem has")
    span = math.hypot(x1 - x0, y1 - y0)
    exposed = span - 2.0 * elbow.SOCKET_MOUTH_REACH
    if exposed <= 0.0:
        raise ValueError(f"the ports stand {span:g} mm apart, closer than two elbows' sockets")
    u = _unit((x1 - x0, y1 - y0, 0.0))
    back = (-u[0], -u[1], 0.0)
    mouth = (x0 + u[0] * elbow.SOCKET_MOUTH_REACH, y0 + u[1] * elbow.SOCKET_MOUTH_REACH, z)
    return {"elbows": ({"crossing": (x0, y0, z), "socket": u,
                        "stem": RUN_INSERTION, "showing": 0.0},
                       {"crossing": (x1, y1, z), "socket": back,
                        "stem": VALVE_INSERTION_NOMINAL + showing, "showing": showing}),
            "tube": (_line(mouth, u, exposed),),
            "exposed_mm": exposed,
            "cut_mm": exposed + 2.0 * elbow.SOCKET_INSERTION,
            "floor_z": z - elbow.COLLAR_OD / 2.0}


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
    """One pump port's tee, its fore valve's tube and its lower return to the rear valve."""
    ports = tee_ports(fore_y, x, z)
    upper = s_bend(ports["upper"]["point"], tuple(upper_port["point"]))
    lower = elbow_return(ports["lower"]["point"], tuple(return_port["point"]))
    return {"tee": ports, "upper_target": dict(upper_port), "return_target": dict(return_port),
            "upper_tube": upper, "return": lower,
            "upper_exposed_mm": sum(s["length_mm"] for s in upper)}


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
