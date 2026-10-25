"""Integral paired seats for Reservoir A's continuous fill and draw tubes.

All public coordinates are appliance-world millimetres. The selected stations
are recorded in ``studies/funnel-gate/reservoir-a-anchors.json``; production
geometry is independent of that study. The slot ceiling is derived from the
seat bottom and the ordinary 3 mm wall. Nominal tie witnesses describe routing,
not purchased tie dimensions, threading, retention or physical acceptance.
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
    "root_z_mm": 248.6,
    "seat_top_z_mm": 258.,
    "seat_radius_mm": 3.325,
    "seat_floor_stock_mm": 3.,
    "station_length_mm": 10.,
    "stock_west_of_first_tube_mm": 3.7,
    "stock_east_of_last_tube_mm": 3.7,
    "tie_slot_width_y_mm": 3.2,
    "tie_slot_bottom_z_mm": 251.6,
    "tie_slot_floor_stock_mm": 3.,
    "tie_access_outer_offset_mm": 6.,
    "tie_access_inner_offset_mm": 2.75,
    "tie_witness_width_mm": 2.5,
    "tie_witness_thickness_mm": .8,
    "tie_witness_outer_bend_radius_mm": 3.75,
    "tie_witness_bottom_center_z_mm": 252.4,
    "stations": [
        {"id": "a-pair-fore-anchor", "label": "Reservoir A fore paired anchor",
         "tube_centers_world_mm": [[50.5, 205., 259.5], [58., 205., 259.5]],
         "routes_west_to_east": ["fluid-16", "fluid-14"]},
        {"id": "a-pair-aft-anchor", "label": "Reservoir A aft paired anchor",
         "tube_centers_world_mm": [[86.5, 304., 259.5], [94., 304., 259.5]],
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
        outer = spec["tie_access_outer_offset_mm"]
        inner = spec["tie_access_inner_offset_mm"]
        result[station["id"]] = {
            **station,
            "stock_bounds_mm": [
                [x0-spec["stock_west_of_first_tube_mm"], y-half, spec["root_z_mm"]],
                [x1+spec["stock_east_of_last_tube_mm"], y+half, spec["seat_top_z_mm"]],
            ],
            "tie_slot_bounds_mm": [
                [x0-outer-.1, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                [x1+outer+.1, y+slot_half, spec["tie_slot_top_z_mm"]],
            ],
            "access_bounds_mm": [
                [[x0-outer-.1, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x0-inner, y+slot_half, spec["seat_top_z_mm"]+.1]],
                [[x1+inner, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x1+outer+.1, y+slot_half, spec["seat_top_z_mm"]+.1]],
            ],
        }
    return result


def _box(bounds):
    import cadquery as cq
    lo, hi = bounds
    return cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))


def cuts():
    """Apply after the seats join the lid, opening the slot through lid stock."""
    return {name: _box(row["tie_slot_bounds_mm"]).fuse(
                *(_box(bounds) for bounds in row["access_bounds_mm"])).clean()
            for name, row in datums().items()}


def supports():
    """Native open paired seats, including their local slot and mouth cuts."""
    import cadquery as cq
    spec = specification()
    passages = cuts()
    result = {}
    for name, row in datums().items():
        body = _box(row["stock_bounds_mm"])
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
    """Nominal 2.5 x 0.8 mm strips and west-side heads; no physical-fit claim."""
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
        head = _box([[x-7.25, y-1.9, z-.5], [x-3.55, y+1.9, z+2.9]])
        result[name+"-tie"] = strip.fuse(head).clean()
    return result
