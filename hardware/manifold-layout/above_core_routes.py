"""Complete warm-side tube continuations at the native component ports.

``continuations(placed, carries)`` returns additional component rows and route
specifications consumed by the enclosure assembly. ``unresolved`` names any
interface that has no buildable route. Native lines, circular arcs and explicit
Bezier spans retain their named minima; 4 mm LLDPE retains R25.
"""

from pathlib import Path

import above_core as layout
from _layout_data import data as _data, read_json as _read_json

unresolved = []


def _add(a, b):
    return tuple(_data('add', a=a, b=b))


def _sub(a, b):
    return tuple(_data('sub', a=a, b=b))


def _mul(a, n):
    return tuple(_data('mul', a=a, scale=n))


def _dot(a, b):
    return _data('dot', a=a, b=b)


def _norm(a):
    return _data('norm', a=a)


def _unit(a):
    return tuple(_data('unit', a=a))


def _cross(a, b):
    return tuple(_data('cross', a=a, b=b))


def _line(a, b):
    return _data('line', a=a, b=b)


def _bezier(control):
    return _data('bezier', control=control)


def _ease_lane(start, end):
    return _data('ease-lane', start=start, end=end)


def _arc(start, tangent, axis, angle, radius):
    segment, end = _data('arc', start=start, tangent=tangent, axis=axis, angle=angle, radius=radius)
    return segment, tuple(end)


def _rounded(points, radius):
    return _data('rounded', points=points, radius=radius)


def _lane_transition(start, displacement, radius):
    segments, end = _data('lane-transition', start=start, displacement=displacement, radius=radius)
    return segments, tuple(end)


def _points(segments):
    return _data('points', segments=segments)


def reservoir_a_route_specs():
    data = _read_json(Path(__file__).with_name('reservoir-a-routes.json'))
    return dict(_data('reservoir-routes', data=data, order=list(data['paths'])))


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


def route_specifications(station, *, plumbing=None):
    """Rust tube recipes from the caller's raw world-port station resolver."""
    unresolved.clear()
    if plumbing is None:
        import rear_plumbing as plumbing
    spec = layout.specification()
    stations = {f'{name}.{port}': station(name, port)
                for name, port in _data('route-stations', operation='route-specifications', spec=spec)}
    result = _data('route-specifications', spec=spec, stations=stations,
                   continuations=list(plumbing.continuations(station).items()),
                   flavors=list(plumbing.flavor_routes(station).items()),
                   reservoir=list(reservoir_a_route_specs().items()))
    unresolved.extend(result['unresolved'])
    return dict(result['routes'])
