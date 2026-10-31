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


def _ease_lane(start, end):
    """A gradual change between parallel +Y tube lanes, flat at both ends."""
    step = (end[1] - start[1]) / 5.
    return _bezier([start,
        (start[0], start[1] + step, start[2]),
        (start[0], start[1] + 2*step, start[2]),
        (end[0], start[1] + 3*step, end[2]),
        (end[0], start[1] + 4*step, end[2]), end])


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


def _lane_transition(start, displacement, radius):
    """Two opposite circular bends between parallel +Y lanes in an X/Z plane."""
    distance = _norm(displacement)
    direction = _mul(displacement, 1. / distance)
    angle = math.acos(1. - distance / (2. * radius))
    axis = _cross((0., 1., 0.), direction)
    first, point = _arc(start, (0., 1., 0.), axis, angle, radius)
    tangent = _add(_mul((0., 1., 0.), math.cos(angle)),
                   _mul(direction, math.sin(angle)))
    second, point = _arc(point, tangent, _mul(axis, -1.), angle, radius)
    return [first, second], point


def _points(segments):
    result = []
    for segment in segments:
        if segment['kind'] == 'line':
            sampled = segment['points_mm']
        elif segment['kind'] == 'bezier':
            controls = segment['control_points_mm']
            degree = len(controls) - 1
            sampled = []
            for i in range(65):
                t = i/64
                weights = [math.comb(degree, k)*(1-t)**(degree-k)*t**k
                           for k in range(degree+1)]
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
        import enclosure_assembly as assembly
        point, axis = assembly.cap_conduit(port)
        diameter = 6.35
    elif name in ('soda-stem-elbow', 'carbonator-fold', 'soda-outlet-return-stem'):
        (point, axis), diameter = parts.stem_elbow_reference().socket(), 6.35
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
              suffix=None, prefix=None, native_segments=None, note=''):
        a, ua, _ = station(*source)
        b, ub, _ = station(*destination)
        outside = [a, *points, b] if suffix is None else [a, *points]
        # Butted sockets whose release faces overlap leave the tube straight
        # between the two receiving depths.
        if not points and suffix is None and prefix is None and _dot(_sub(b, a), ua) < 0.:
            outside = []
        full = ([_sub(a, _mul(ua, source_depth)), *outside] if prefix is None else
                [prefix[-1]['points_mm'][-1], *points, *([b] if suffix is None else [])])
        if suffix is None:
            full.append(_sub(b, _mul(ub, destination_depth)))
        try:
            if native_segments is not None:
                segments = native_segments
            else:
                segments = [*(prefix or []), *_rounded(full, radius)]
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

    import rear_plumbing
    specifications.update(rear_plumbing.continuations(station))
    specifications.update(rear_plumbing.flavor_routes(station))

    specifications.update(reservoir_a_route_specs())
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
    b_fill = layout.specification()['reservoir_b_fill_external']
    route('fluid-24', ('reservoir-b-fill-turn', 'socket'), ('foam-assembly', 'reservoir-b-fill'),
          [], native_segments=b_fill['segments'], radius=b_fill['minimum_radius_mm'],
          source_depth=b_fill['source_depth_mm'], destination_depth=0.,
          note='B fill follows two exposed circular arcs to the fore cap entry')
    return specifications
