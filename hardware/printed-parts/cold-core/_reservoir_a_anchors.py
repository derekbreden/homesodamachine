"""Reservoir A's fore snap receiver and aft tied seats, in appliance millimetres.

The fore integral C2 pair shares `_reservoir_a_c2`. The aft seat's west
stock ramps from the lid face under V-K's outlet elbow. Its tie witnesses
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
         "tube_centers_world_mm": [[86.5, 304., 259.5], [94., 304., 259.5]],
         "curved_seats": True,
         "seat_top_z_mm": 256.95,
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
    fore = result["stations"][0]
    fore.update(snap.specification())
    result["stations"][1]["closure"] = "tie"
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
            result[station['id']].update(
                nominal_tube_centers_world_mm=station['tube_centers_world_mm'],
                tube_centers_world_mm=[p for p, _axis in held],
                tube_axes_world=[axis for _p, axis in held])
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


def _box(bounds):
    import cadquery as cq
    lo, hi = bounds
    return cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))


def cuts():
    """Apply after the seats join the lid, opening the slot through lid stock."""
    spec = specification()
    result = {}
    for name, row in datums().items():
        if row["closure"] == "direct-snap":
            continue
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
        if row["closure"] == "direct-snap":
            result[name] = snap.base()
            continue
        body = _box(row["stock_bounds_mm"])
        if "west_ramp_xz_mm" in row:
            body = body.cut(_west_ramp_cutter(row, spec))
        if row.get('curved_seats'):
            import above_core_parts as parts
            import above_core_routes as routes
            paths = routes.reservoir_a_route_specs()
            for identifier in row['routes_west_to_east']:
                wire = parts.route_wire(paths[identifier])
                edge = wire.Edges()[0]
                bore = (cq.Workplane(cq.Plane(origin=edge.startPoint(), normal=edge.tangentAt(0.)))
                        .circle(spec['seat_radius_mm'])
                        .sweep(wire, isFrenet=False, transition='round').val())
                body = body.cut(bore)
        else:
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
        if row["closure"] != "tie":
            continue
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
