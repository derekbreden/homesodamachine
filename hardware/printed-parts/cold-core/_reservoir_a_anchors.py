"""Reservoir A's fore snap receiver and aft tied seats, in appliance millimetres.

The fore integral C2 pair shares `_reservoir_a_c2`. The aft open seats
share one filled stepped-height saddle within the casing footprint. Its tie witnesses
describe routing, not purchased dimensions or physical acceptance.
"""
from copy import deepcopy
import math

import _reservoir_a_c2 as snap


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
         "routes_west_to_east": ["fluid-16", "fluid-14"]},
        {"id": "a-pair-aft-anchor", "label": "Reservoir A aft paired anchor",
         "world_y_mm": 390.5,
         "station_length_mm": 9.2,
         "curved_seats": True,
         "seat_lip_below_axis_mm": 1.2,
         "routes_west_to_east": ["fluid-16", "fluid-14"]},
    ],
}


def specification():
    """Selected production dimensions, including the derived slot ceiling."""
    result = deepcopy(_SPECIFICATION)
    fore = result["stations"][0]
    fore.update(snap.specification())
    aft = result["stations"][1]
    aft["closure"] = "tie"
    aft["tube_centers_world_mm"] = [
        _route_station(route, aft['world_y_mm'])[0]
        for route in aft['routes_west_to_east']]
    result["tie_slot_top_z_mm"] = min(
        point[2] for row in result["stations"] if row["closure"] == "tie"
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
        half = station.get("station_length_mm", spec["station_length_mm"]) / 2
        if station["closure"] == "direct-snap":
            result[station["id"]] = {
                **station,
                "stock_bounds_mm": station["body_bounds_mm"],
                "tube_axes_world": [station['tube_axis_world']]*2,
            }
            continue
        top = station.get("seat_top_z_mm", spec["seat_top_z_mm"])
        slot_half = spec["tie_slot_width_y_mm"] / 2
        inner = spec["tie_access_inner_offset_mm"]
        east = station.get("base_east_of_last_tube_mm", spec["stock_east_of_last_tube_mm"])
        west_edge = x0-spec["stock_west_of_first_tube_mm"]
        east_edge = x1+east
        result[station["id"]] = {
            **station,
            "stock_bounds_mm": [
                [west_edge, y-half, spec["root_z_mm"]],
                [east_edge, y+half, top],
            ],
            "tie_slot_bounds_mm": [
                [west_edge, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                [east_edge, y+slot_half, spec["tie_slot_top_z_mm"]],
            ],
            "access_bounds_mm": [
                [[west_edge, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [x0-inner, y+slot_half, top+.1]],
                [[x1+inner, y-slot_half, spec["tie_slot_bottom_z_mm"]],
                 [east_edge, y+slot_half, top+.1]],
            ],
        }
        if station.get("open_quarter_side") == "east":
            result[station["id"]]["open_quarter_bounds_mm"] = [
                [x1, y-half, spec["tie_slot_top_z_mm"]],
                [x1+east+.1, y+half, top+.1],
            ]
        if "west_ramp_top_west_of_first_tube_mm" in station:
            # X/Z ends of the west ramp: the root edge on the lid face, then
            # the seat top's west edge. The ramp spans the station's length.
            result[station["id"]]["west_ramp_xz_mm"] = [
                [west_edge, spec["lid_face_z_mm"]],
                [x0-station["west_ramp_top_west_of_first_tube_mm"], top],
            ]
        if station.get('curved_seats'):
            held = [_route_station(route, y) for route in station['routes_west_to_east']]
            row = result[station['id']]
            row.update(
                nominal_tube_centers_world_mm=station['tube_centers_world_mm'],
                tube_centers_world_mm=[p for p, _axis in held],
                tube_axes_world=[axis for _p, axis in held])
            lanes = [[_route_station(route, y-half+i*2*half/64) for i in range(65)]
                     for route in station['routes_west_to_east']]
            edges = [(min(p[0]-spec['seat_radius_mm']/abs(u[1]) for p,u in lane),
                      max(p[0]+spec['seat_radius_mm']/abs(u[1]) for p,u in lane))
                     for lane in lanes]
            tops = [min(p[2] for p,_u in lane)-station['seat_lip_below_axis_mm']
                    for lane in lanes]
            west_edge, east_edge = edges[0][0]-3., edges[-1][1]+3.
            row['stock_bounds_mm'] = [[west_edge,y-half,spec['root_z_mm']],
                                      [east_edge,y+half,max(tops)]]
            # Cross both curved clearance bores with a broad roof transition.
            # Ending the ramp at their swept extremes leaves vanishing tips.
            reach = spec['seat_floor_stock_mm']
            row['seat_roof_xz_mm'] = [(west_edge,tops[0]),(edges[0][1]-reach,tops[0]),
                                      (edges[-1][0]+reach,tops[-1]),(east_edge,tops[-1])]
            row['tie_slot_bounds_mm'][0][0] = west_edge
            row['tie_slot_bounds_mm'][1][0] = east_edge
            for mouth, xa, xb in zip(row['access_bounds_mm'],
                                      (west_edge,x1),(x0,east_edge)):
                mouth[0][0], mouth[1][0], mouth[1][2] = xa, xb, max(tops)+.1
    return result


def _route_station(identifier, y):
    """Exact line/arc centre and tangent at a restraint's world Y plane."""
    import above_core_routes as routes
    for segment in routes.reservoir_a_route_specs()[identifier]['segments']:
        first, last = segment['points_mm'][0], segment['points_mm'][-1]
        if not min(first[1], last[1])-1.e-8 <= y <= max(first[1], last[1])+1.e-8:
            continue
        if segment['kind'] == 'line':
            if abs(last[1]-first[1]) < 1.e-9:
                continue
            t = (y-first[1])/(last[1]-first[1])
            return routes._add(first, routes._mul(routes._sub(last, first), t)), routes._unit(routes._sub(last, first))
        center, axis = segment['center_mm'], segment['axis']
        radial = routes._sub(first, center)
        sideways = routes._cross(axis, radial)
        def point(angle):
            return routes._add(center, routes._add(routes._mul(radial, math.cos(angle)),
                                                  routes._mul(sideways, math.sin(angle))))
        lo, hi = 0., segment['angle_rad']
        increasing = last[1] > first[1]
        for _ in range(48):
            mid = (lo+hi)/2
            if (point(mid)[1] < y) == increasing:
                lo = mid
            else:
                hi = mid
        station = point((lo+hi)/2)
        return station, routes._unit(routes._cross(axis, routes._sub(station, center)))
    raise ValueError(f'{identifier} has no restraint crossing at Y{y:g}')


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

    tangent = math.atan2(last[2]-first[2],x1-x0)+math.pi/2
    arc(x0, z, radius, math.pi, tangent)
    arc(x1, last[2], radius, tangent, 0)
    arc(x1+radius-turn, bottom+turn, turn, 0, -math.pi/2)
    arc(x0-radius+turn, bottom+turn, turn, -math.pi/2, -math.pi)
    return points
