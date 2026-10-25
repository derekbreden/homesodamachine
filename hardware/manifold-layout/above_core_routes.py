"""Complete warm-side tube continuations at the native component ports.

``continuations(placed, carries)`` returns additional component rows and route
specifications consumed by the enclosure assembly. ``unresolved`` names any
interface that has no buildable route. Native lines, circular arcs and explicit
Bezier spans retain their named minima; 4 mm LLDPE retains R25.
"""

import json
import math
from pathlib import Path

import above_core as layout

unresolved = []


def _add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def _sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def _mul(a, n):
    return tuple(x*n for x in a)


def _dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def _norm(a):
    return math.sqrt(_dot(a, a))


def _unit(a):
    return _mul(a, 1/_norm(a))


def _cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _line(a, b):
    return {'kind': 'line', 'points_mm': [list(a), list(b)]}


def _bezier(control):
    return {'kind': 'bezier', 'control_points_mm': [list(p) for p in control]}


def _arc(start, tangent, axis, angle, radius):
    """Circular bend from a tangent; right-handed axis and angle in radians."""
    normal = _cross(axis, tangent)
    center = _add(start, _mul(normal, radius))
    radial = _sub(start, center)
    def at(t):
        return _add(center, _add(_mul(radial, math.cos(t)),
                                _mul(_cross(axis, radial), math.sin(t))))
    end = at(angle)
    segment = {'kind': 'arc', 'points_mm': [list(start), list(at(angle/2)), list(end)],
               'radius_mm': radius, 'center_mm': center,
               'axis': axis, 'angle_rad': angle}
    return segment, end


def _rounded(points, radius):
    """One constant-radius fillet at each real corner, without tightening."""
    clean = []
    for point in points:
        point = tuple(float(v) for v in point)
        if not clean or math.dist(clean[-1], point) > 1e-7:
            clean.append(point)
    while len(clean) > 2:
        remove = [index for index in range(1, len(clean)-1)
                  if _dot(_unit(_sub(clean[index], clean[index-1])),
                          _unit(_sub(clean[index+1], clean[index]))) > 1-1e-8]
        if not remove:
            break
        clean = [p for index, p in enumerate(clean) if index not in remove]
    bends = {}
    for index in range(1, len(clean)-1):
        incoming = _unit(_sub(clean[index], clean[index-1]))
        outgoing = _unit(_sub(clean[index+1], clean[index]))
        angle = math.acos(max(-1., min(1., _dot(incoming, outgoing))))
        reach = radius * math.tan(angle/2)
        bends[index] = incoming, outgoing, angle, reach
    for index in range(len(clean)-1):
        used = bends.get(index, (0, 0, 0, 0))[3] + bends.get(index+1, (0, 0, 0, 0))[3]
        if used > math.dist(clean[index], clean[index+1]) + 1e-5:
            raise ValueError(f'R{radius:g} needs {used:.3f} mm on leg {index}; '
                             f'only {math.dist(clean[index], clean[index+1]):.3f} mm available')
    segments, cursor = [], clean[0]
    for index, (incoming, outgoing, angle, reach) in bends.items():
        before = _sub(clean[index], _mul(incoming, reach))
        if math.dist(cursor, before) > 1e-7:
            segments.append(_line(cursor, before))
        segment, cursor = _arc(before, incoming, _unit(_cross(incoming, outgoing)), angle, radius)
        segments.append(segment)
    if math.dist(cursor, clean[-1]) > 1e-7:
        segments.append(_line(cursor, clean[-1]))
    return segments


def _points(segments):
    result = []
    for segment in segments:
        if segment['kind'] == 'line':
            sampled = segment['points_mm']
        elif segment['kind'] == 'bezier':
            controls = segment['control_points_mm']
            sampled = []
            for i in range(65):
                t = i/64
                weights = ((1-t)**3, 3*(1-t)**2*t, 3*(1-t)*t*t, t**3)
                sampled.append([sum(w*p[k] for w, p in zip(weights, controls)) for k in range(3)])
        else:
            center, axis = segment['center_mm'], segment['axis']
            radial = _sub(segment['points_mm'][0], center)
            sampled = [_add(center, _add(_mul(radial, math.cos(segment['angle_rad']*i/24)),
                                         _mul(_cross(axis, radial), math.sin(segment['angle_rad']*i/24))))
                       for i in range(25)]
        for point in sampled:
            if not result or math.dist(result[-1], point) > 1e-6:
                result.append(list(point))
    return result


def reservoir_a_route_specs():
    """Selected paired-anchor paths, in the existing logical route directions."""
    data = json.loads(Path(__file__).with_name('reservoir-a-routes.json').read_text())
    specifications = {}
    for identifier, row in data['paths'].items():
        segments = []
        for segment in row['segments']:
            if segment['kind'] == 'line':
                segments.append(_line(*segment['points_mm']))
                continue
            center = segment['center_mm']
            radial = _sub(segment['start_mm'], center)
            tangent = _unit(_cross(segment['axis'], radial))
            native, _ = _arc(segment['start_mm'], tangent, segment['axis'],
                             segment['angle_rad'], segment['radius_mm'])
            native['points_mm'][0] = segment['start_mm']
            native['points_mm'][-1] = segment['end_mm']
            segments.append(native)
        if row['reverse']:
            segments.reverse()
            for segment in segments:
                segment['points_mm'].reverse()
                if segment['kind'] == 'arc':
                    segment['axis'] = _mul(segment['axis'], -1.)
        points = _points(segments)
        specifications[identifier] = {
            'points_mm': points, 'centerline_mm': points, 'segments': segments,
            'od_mm': data['tube_od_mm'], 'id_mm': data['tube_id_mm'],
            'radius_mm': data['minimum_radius_mm'],
            'minimum_radius_mm': data['minimum_radius_mm'], 'spool': data['spool'],
            'from': row['frm'], 'frm': row['frm'], 'to': row['to'],
            'owners': list(dict.fromkeys((row['frm'].partition('.')[0],
                                         row['to'].partition('.')[0]))),
            'status': 'selected_native_layout',
            'note': ('Reservoir A continuous tube retained by the fore and aft '
                     'paired lid anchors; the plain guide adds no joint or cut'),
        }
    return specifications


def _station(carries, name, port):
    import above_core_parts as parts
    selected = parts.port_stations(name)
    if selected and port in selected:
        point, axis, diameter = selected[port]
    elif name == 'digiten-flow':
        point, axis, diameter = ((-30.5 if port == 'inlet' else 30.5), 0., 0.), (
            (-1. if port == 'inlet' else 1.), 0., 0.), 6.35
    elif name == 'foam-assembly':
        if port == 'reservoir-b-fill' and 'reservoir_b_fill_link' in layout.specification():
            mount = parts._module('above_core_route_mounts', 'printed-parts/cold-core/_above_core_mounts.py')
            return tuple(mount.reservoir_b_fill_link()['upper_mouth_world_mm']), (0., 0., 1.), 6.35
        import enclosure_assembly as assembly
        point, axis = assembly.cap_conduit(port)
        diameter = 6.35
    elif name in ('soda-stem-elbow', 'carbonator-fold', 'soda-outlet-return-stem'):
        point, axis, diameter = (0., 19.05, 0.), (0., 1., 0.), 6.35
    else:
        import _lines
        station, diameter = _lines.STATIONS[name][port]
        point, axis = station()
    world, direction = carries[name]((point, axis))
    return tuple(world), tuple(direction), diameter


def continuations(placed, carries):
    """Return ``(extra_components, logical_route_specs)`` at actual ports.

    ``placed`` contains native shapes by production name and ``carries`` maps
    those names to native port carries. The added meter row uses that same
    tuple format. Route specifications include spool, logical endpoints,
    owners, exact native segments and sampled points for reporting.
    """
    import above_core_parts as parts
    core = parts.core_components()
    extra = {name: row for name, row in core.items() if name not in carries}
    carries = {**{name: row[2] for name, row in core.items()}, **carries}
    return extra, route_specifications(lambda name, port: _station(carries, name, port))


def core_route_specs():
    """Standalone-core warm-side tube rows; its soda tube ends at a plain guide."""
    return {}


def route_specifications(station):
    """Explicit lines and arcs from a caller's native world-port resolver."""
    unresolved.clear()
    import soda_inlet
    specifications = {'soda-core-rise': soda_inlet.tube_spec()}

    def route(identifier, source, destination, points, *, radius=14., spool='black',
              od=6.35, inside=4.24, source_depth=12.7, destination_depth=12.7,
              suffix=None, note=''):
        a, ua, _ = station(*source)
        b, ub, _ = station(*destination)
        outside = [a, *points, b] if suffix is None else [a, *points]
        full = [_sub(a, _mul(ua, source_depth)), *outside]
        if suffix is None:
            full.append(_sub(b, _mul(ub, destination_depth)))
        try:
            segments = _rounded(full, radius)
            if suffix is not None:
                segments.extend(suffix)
                segments.append(_line(b, _sub(b, _mul(ub, destination_depth))))
            sampled = _points(segments)
            bent = any(segment['kind'] != 'line' for segment in segments)
            specifications[identifier] = {
                'points_mm': sampled, 'centerline_mm': sampled,
                'segments': segments, 'od_mm': od, 'id_mm': inside,
                'radius_mm': radius if bent else None, 'minimum_radius_mm': radius if bent else None,
                'spool': spool, 'from': '.'.join(source), 'frm': '.'.join(source),
                'to': '.'.join(destination),
                'owners': list(dict.fromkeys((source[0], destination[0]))),
                'status': 'selected_native_layout', 'note': note,
            }
        except ValueError as failure:
            unresolved.append({'id': identifier, 'reason': str(failure)})

    # The downward fold feeds a plain guide directly below its socket. This
    # guide is a boundary in one continuous tube, with no receiving fitting.
    route('water-5', ('carbonator-fold', 'socket'), ('foam-assembly', 'water-in'), [],
          source_depth=16.891, destination_depth=0., spool='white',
          note='neoFit ACHV44-E discharge check folds down into the passive aft water-in guide')
    route('soda-meter-bulkhead', ('digiten-flow', 'outlet'), ('soda-outlet-return-stem', 'socket'), [],
          spool='blue', source_depth=15.7, destination_depth=16.891,
          note='Concealed 32.591 mm tube joins the coincident meter and rear-stem collet faces')

    # Both dispense lines retain R25 and their three-dimensional rear returns.
    # Their west overpasses clear V-A below the rear frame receiver, outside
    # the removable frame's lower body and the connector service paths.
    flavor_a = station('bulkhead-flavor-a', 'tube-in')[0]
    r = 25.
    diagonal = math.sqrt(.5)
    start_a = (flavor_a[0], flavor_a[1]-r, flavor_a[2]+r)
    arc_a, end_a = _arc(start_a, (0., 0., -1.), (1., 0., 0.), math.pi/2, r)
    hairpin_height = 337.75
    hairpin_start = (start_a[0]-r, start_a[1], hairpin_height)
    hairpin, hairpin_end = _arc(hairpin_start, (1., 0., 0.), (0., 1., 0.), math.pi/2, r)
    route('fluid-18', ('valve-v-g', 'outlet'), ('bulkhead-flavor-a', 'tube-in'),
          [(73.82, 166.24, 292.), (35., 135., 289.), (-68., 135., 289.),
           (-94., 205., 281.5), (-94., 245., 281.5), (-94., 245., 331.5),
           (-94., 300., 331.5), (-40., 340., 331.5),
           (-40., 380., hairpin_height), (-40., start_a[1], hairpin_height), hairpin_start],
          radius=r, spool='flavor-black-4mm', od=4., inside=2.5, source_depth=10.,
          destination_depth=10., suffix=[hairpin, _line(hairpin_end, start_a), arc_a])

    flavor_b = station('bulkhead-flavor-b', 'tube-in')[0]
    # R25 and the port fix the drop's Y from its X. Moving the drop east takes it aft, off
    # the meter collar's tie pad and toward the PISCO regulator; X64.35 splits the room.
    b_drop_x = 64.35
    b_heading = math.pi/4-math.asin(((flavor_b[0]-b_drop_x)/r-1)/math.sqrt(2))
    b_east, b_aft = math.cos(b_heading), math.sin(b_heading)
    b_drop_y = flavor_b[1]-r*(b_east+b_aft)
    start_b = (b_drop_x, b_drop_y, flavor_b[2]+r)
    b_lower, b_lower_end = _arc(start_b, (0., 0., -1.), (b_aft, -b_east, 0.), math.pi/2, r)
    arc_b, _ = _arc(b_lower_end, (b_east, b_aft, 0.), (0., 0., 1.), math.pi/2-b_heading, r)
    b_curve_start = (b_drop_x-r, b_drop_y, 343.)
    b_upper, b_upper_end = _arc(b_curve_start, (1., 0., 0.), (0., 1., 0.), math.pi/2, r)
    route('fluid-28', ('valve-v-j', 'outlet'), ('bulkhead-flavor-b', 'tube-in'),
          [(-73.82, 166.24, 283.), (-94., 210., 276.), (-94., 260., 276.),
           (-94., 260., 326.), (-94., 310., 326.), (-59., 330., 343.),
           (-59., 380., 343.), (-59., b_drop_y, 343.), b_curve_start],
          radius=r, spool='flavor-black-4mm', od=4., inside=2.5,
          source_depth=10., destination_depth=10.,
          suffix=[b_upper, _line(b_upper_end, start_b), b_lower, arc_b])

    # Vent travels above the dry electronics and drops aft of the motor.
    vent = station('bulkhead-drain', 'inboard')[0]
    vent_start = (vent[0]-r*diagonal, vent[1]-r, vent[2]+r*diagonal)
    vent_arc, _ = _arc(vent_start, (diagonal, 0., -diagonal),
                           (diagonal, 0., diagonal), math.pi/2, r)
    vent_turn_start = (vent_start[0]-r*diagonal, vent_start[1], vent[2]+r)
    vent_turn, vent_turn_end = _arc(vent_turn_start, (1., 0., 0.), (0., 1., 0.), math.pi/4, r)
    # The foreward S leaves the sleeve on-axis; the long west leg is separated
    # from both dispense lines by its X/Z lanes.
    route('drain-vent', ('asse-drain-adapter', 'tube'), ('bulkhead-drain', 'inboard'),
          [(-35., 355.3849605281867, 342.), (-35., 410., 342.),
           (-15., vent_start[1], vent_turn_start[2]), vent_turn_start],
          radius=r, spool='drain-white', od=4., inside=2.5,
          source_depth=14., destination_depth=10., suffix=[vent_turn, vent_arc])

    specifications.update(reservoir_a_route_specs())
    # B-fill's JG mouth is above the lid; its lower stem/link belong to the
    # core builder. The selected Reservoir A paths leave both B routes intact.
    b_draw = station('foam-assembly', 'reservoir-b')[0]
    b_draw_target = station('valve-v-h', 'inlet')[0]
    b_draw_z = 295.7
    b_draw_down_start = (b_draw_target[0]+14., b_draw_target[1], b_draw_target[2]+14.)
    b_draw_rise_angle = math.acos(1-(b_draw_down_start[2]-b_draw_z)/(2*14.))
    b_draw_rise_start = (b_draw_down_start[0]+28.*math.sin(b_draw_rise_angle), b_draw_target[1], b_draw_z)
    b_draw_rise_first, b_draw_rise_mid = _arc(b_draw_rise_start, (-1., 0., 0.), (0., 1., 0.),
                                                       b_draw_rise_angle, 14.)
    b_draw_rise_second, _ = _arc(b_draw_rise_mid, (-math.cos(b_draw_rise_angle), 0., math.sin(b_draw_rise_angle)),
                                              (0., -1., 0.), b_draw_rise_angle, 14.)
    b_draw_down, _ = _arc(b_draw_down_start, (-1., 0., 0.), (0., -1., 0.), math.pi/2, 14.)
    route('fluid-26', ('foam-assembly', 'reservoir-b'), ('valve-v-h', 'inlet'),
          [(b_draw[0], b_draw[1], b_draw_z), (b_draw_target[0], 214., b_draw_z),
           (b_draw_target[0], 138., b_draw_z), (11.3, 138., b_draw_z),
           (11.3, b_draw_target[1], b_draw_z), b_draw_rise_start],
          source_depth=0.,
          suffix=[b_draw_rise_first, b_draw_rise_second, b_draw_down],
          note='B draw completes its westward offset aft of the drain cradle, then enters V-H from the fore corridor')
    b_fill = station('foam-assembly', 'reservoir-b-fill')[0]
    route('fluid-24', ('valve-v-i', 'outlet'), ('foam-assembly', 'reservoir-b-fill'),
          [(-82.1, 108.04, 296.175), (-82.1, 180., 296.175),
           (-82.1, 245., 296.175), (b_fill[0], b_fill[1], 296.175)], destination_depth=0.)
    return specifications
