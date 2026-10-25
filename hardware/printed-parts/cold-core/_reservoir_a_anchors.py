"""Integral paired seats for Reservoir A's continuous fill and draw tubes.

All public coordinates are appliance-world millimetres. The selected stations
are recorded in ``studies/funnel-gate/reservoir-a-anchors.json``; production
geometry is independent of that study. The slot ceiling is derived from the
seat bottom and the ordinary 3 mm wall. The aft seat's west stock ramps from
the lid face up to the seat top, under V-K's outlet elbow. Nominal tie
witnesses describe routing, not purchased tie dimensions, threading, retention
or physical acceptance.
"""
from copy import deepcopy
import math


_SPECIFICATION = {
    "units": "mm",
    "assembly_owner": "back-bottom",
    "mounting_parent": "cold-core top lid",
    "tube_od_mm": 6.35,
    "tube_axis_world": [0., 1., 0.],
    "lid_face_z_mm": 253.4,
    "root_z_mm": 248.,
    "seat_top_z_mm": 257.,
    "seat_radius_mm": 3.325,
    "seat_floor_stock_mm": 3.,
    "station_length_mm": 10.,
    "stock_west_of_first_tube_mm": 6.325,
    "stock_east_of_last_tube_mm": 6.325,
    "tie_slot_width_y_mm": 3.2,
    "tie_slot_bottom_z_mm": 251.6,
    "tie_slot_floor_stock_mm": 3.,
    "tie_access_inner_offset_mm": 0.,
    "tie_witness_width_mm": 2.5,
    "tie_witness_thickness_mm": .8,
    "tie_witness_outer_bend_radius_mm": 3.75,
    "tie_witness_bottom_center_z_mm": 252.4,
    "stations": [
        {"id": "a-pair-fore-anchor", "label": "Reservoir A fore paired anchor",
         "tube_centers_world_mm": [[50.5, 205., 259.5], [58., 205., 259.5]],
         "tie_head_side": "east",
         "routes_west_to_east": ["fluid-16", "fluid-14"]},
        {"id": "a-pair-aft-anchor", "label": "Reservoir A aft paired anchor",
         "tube_centers_world_mm": [[86.5, 304., 259.5], [94., 304., 259.5]],
         "open_quarter_side": "east",
         "base_east_of_last_tube_mm": 3.7,
         # The west stock leaves the lid face at its ordinary root edge and
         # meets the seat top this far west of the first tube, 1.3 mm short of
         # the groove lip. V-K's outlet elbow hub stands over the ramp.
         "west_ramp_top_west_of_first_tube_mm": 3.5,
         "routes_west_to_east": ["fluid-16", "fluid-14"]},
    ],
}


def specification():
    """Selected production dimensions, including the derived slot ceiling."""
    result = deepcopy(_SPECIFICATION)
    result["tie_slot_top_z_mm"] = min(
        point[2] for row in result["stations"]
        for point in row["tube_centers_world_mm"]
    ) - result["seat_radius_mm"] - result["seat_floor_stock_mm"]
    result["tie_access_outer_offset_mm"] = max(
        result["stock_west_of_first_tube_mm"], result["stock_east_of_last_tube_mm"])
    return result


def datums():
    """World-frame stock, seat axes and through-slot/threading-mouth bounds."""
    spec = specification()
    result = {}
    for station in spec["stations"]:
        first, last = station["tube_centers_world_mm"]
        x0, x1 = first[0], last[0]
        y = first[1]
        half = spec["station_length_mm"] / 2
        slot_half = spec["tie_slot_width_y_mm"] / 2
        inner = spec["tie_access_inner_offset_mm"]
        east = station.get("base_east_of_last_tube_mm", spec["stock_east_of_last_tube_mm"])
        west_edge = x0-spec["stock_west_of_first_tube_mm"]
        east_edge = x1+east
        result[station["id"]] = {
            **station,
            "stock_bounds_mm": [
                [west_edge, y-half, spec["root_z_mm"]],
                [east_edge, y+half, spec["seat_top_z_mm"]],
            ],
            "tie_slot_bounds_mm": [
                [west_edge, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                [east_edge, y+slot_half, spec["tie_slot_top_z_mm"]],
            ],
            "access_bounds_mm": [
                [[west_edge, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x0-inner, y+slot_half, spec["seat_top_z_mm"]+.1]],
                [[x1+inner, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [east_edge, y+slot_half, spec["seat_top_z_mm"]+.1]],
            ],
        }
        if station.get("open_quarter_side") == "east":
            result[station["id"]]["open_quarter_bounds_mm"] = [
                [x1, y-half, spec["tie_slot_top_z_mm"]],
                [x1+east+.1, y+half, spec["seat_top_z_mm"]+.1],
            ]
        if "west_ramp_top_west_of_first_tube_mm" in station:
            # X/Z ends of the west ramp: the root edge on the lid face, then
            # the seat top's west edge. The ramp spans the station's length.
            result[station["id"]]["west_ramp_xz_mm"] = [
                [west_edge, spec["lid_face_z_mm"]],
                [x0-station["west_ramp_top_west_of_first_tube_mm"], spec["seat_top_z_mm"]],
            ]
    return result


def _box(bounds):
    import cadquery as cq
    lo, hi = bounds
    return cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))


def cuts():
    """Apply after the seats join the lid, opening the slot through lid stock."""
    result = {}
    for name, row in datums().items():
        openings = [_box(bounds) for bounds in row["access_bounds_mm"]]
        if "open_quarter_bounds_mm" in row:
            openings.append(_box(row["open_quarter_bounds_mm"]))
        result[name] = _box(row["tie_slot_bounds_mm"]).fuse(*openings).clean()
    return result


def _west_ramp_cutter(row, spec):
    """Everything above the west ramp's line, over the station's length."""
    import cadquery as cq
    (xa, za), (xb, zb) = row["west_ramp_xz_mm"]
    slope = (zb-za)/(xb-xa)
    y = row["tube_centers_world_mm"][0][1]
    half = spec["station_length_mm"]/2+.1
    ceiling = zb+slope
    outline = [(xa-1., za-slope), (xb+1., ceiling), (xa-1., ceiling)]
    wire = cq.Wire.makePolygon(
        [cq.Vector(x, y-half, z) for x, z in outline], close=True)
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, 2*half, 0))


def supports():
    """Native open paired seats, including their local slot and mouth cuts."""
    import cadquery as cq
    spec = specification()
    passages = cuts()
    result = {}
    for name, row in datums().items():
        body = _box(row["stock_bounds_mm"])
        if "west_ramp_xz_mm" in row:
            body = body.cut(_west_ramp_cutter(row, spec))
        for x, y, z in row["tube_centers_world_mm"]:
            bore = cq.Solid.makeCylinder(
                spec["seat_radius_mm"], spec["station_length_mm"]+.2,
                cq.Vector(x, y-spec["station_length_mm"]/2-.1, z), cq.Vector(0, 1, 0))
            body = body.cut(bore)
        result[name] = body.cut(passages[name]).clean()
    return result


def tie_profile(row):
    """Closed nominal X/Z tie centreline, without an untrimmed loose tail."""
    spec = specification()
    first, last = row["tube_centers_world_mm"]
    x0, x1, z = first[0], last[0], first[2]
    radius = spec["tie_witness_outer_bend_radius_mm"]
    bottom = spec["tie_witness_bottom_center_z_mm"]
    turn = 1.5
    points = []

    def arc(x, zz, r, start, end):
        for i in range(13):
            angle = start+(end-start)*i/12
            points.append((x+r*math.cos(angle), zz+r*math.sin(angle)))

    arc(x0, z, radius, math.pi, math.pi/2)
    arc(x1, z, radius, math.pi/2, 0)
    arc(x1+radius-turn, bottom+turn, turn, 0, -math.pi/2)
    arc(x0-radius+turn, bottom+turn, turn, -math.pi/2, -math.pi)
    return points


def tie_witnesses():
    """Nominal 2.5 x 0.8 mm strips and dressed heads; no physical-fit claim."""
    import cadquery as cq
    from shapely.geometry import Polygon
    spec = specification()
    result = {}
    for name, row in datums().items():
        line = Polygon(tie_profile(row))
        outer = line.buffer(spec["tie_witness_thickness_mm"]/2, join_style=2)
        inner = line.buffer(-spec["tie_witness_thickness_mm"]/2, join_style=2)
        x, y, z = row["tube_centers_world_mm"][0]
        width = spec["tie_witness_width_mm"]

        def wire(points):
            return cq.Wire.makePolygon(
                [cq.Vector(a, y+width/2, b) for a, b in list(points)[:-1]], close=True)

        strip = cq.Solid.extrudeLinear(wire(outer.exterior.coords),
                                      [wire(inner.exterior.coords)], cq.Vector(0, -width, 0))
        if row.get("tie_head_side", "west") == "east":
            x = row["tube_centers_world_mm"][-1][0]
            head = _box([[x+3.55, y-1.9, z-.5], [x+7.25, y+1.9, z+2.9]])
        else:
            head = _box([[x-7.25, y-1.9, z-.5], [x-3.55, y+1.9, z+2.9]])
        result[name+"-tie"] = strip.fuse(head).clean()
    return result
