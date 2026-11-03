"""Plain-data adapter to the machine's Rust fit, clearance and drain reader.

The physical model is immutable. Placement provides scalar construction ledgers
and explicit installed frames; Rust owns geometry import, tools and decisions.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _path(path):
    path = Path(path)
    return (ROOT / path).resolve() if not path.is_absolute() else path.resolve()


def _sha(path):
    with _path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def _binding(path):
    path = _path(path)
    return {'path': str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            'sha256': _sha(path)}


def _plain(value):
    """Only scalar ledgers cross the reader boundary; Shapes have no conversion."""
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [_plain(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f'Machine check inputs are plain scalar data, got {type(value).__name__}')


def read(request):
    """Return scorecard/drain/facts readings without constructing Python geometry.

    ``request`` has ``physical_model``, ``envelope`` (path and rigid 3×4
    transform), ``aliases`` and ``metadata``. ``mode`` selects ``all``,
    ``scorecard``, ``geometry`` or ``drain``. Geometry mode returns only the
    overlap/clearance population, before the scalar scorecard is composed.
    """
    import _rust_part
    import _assembly_model

    request = _plain(request)
    model = _path(request.get('physical_model', request.get('model')))
    request['physical_model'] = str(model)
    envelope = dict(request['envelope'])
    envelope_path = _path(envelope.get('path', envelope.get('model')))
    envelope_binding = _binding(envelope_path)
    if envelope.get('sha256') not in (None, envelope_binding['sha256']):
        raise ValueError('The exact casing model differs from its declared binding')
    envelope.update(path=str(envelope_path))
    request['envelope'] = envelope
    bindings = {'physical': _binding(model),
                'envelope': {**envelope_binding, 'transform': envelope['transform'],
                             'qualified_names': [name for name, _color in
                                                 _assembly_model.identity(envelope_path)]}}
    if request.get('wiring_model') is not None:
        request['wiring_model'] = str(_path(request['wiring_model']))
        bindings['wiring'] = _binding(request['wiring_model'])
    metadata = request.setdefault('metadata', {})
    # The source's logical inventory is ordered. JSON object-key sorting in the
    # engine protocol must not reorder newly appended connection rows.
    connections = json.loads((ROOT / 'hardware/manifold-layout/above-core.json').read_text())
    order = list(connections.get('logical_connections', {}))
    order.extend(k for k in metadata.get('native_connections', {}) if k not in order)
    metadata.setdefault('native_connection_order', order)
    metadata.setdefault('bed', [325.0, 320.0, 320.0])
    metadata.setdefault('seat_tolerance', 1.e-6)
    metadata.setdefault('tube_anchor_span', 200.0)
    metadata.setdefault('topology_path', str(ROOT / 'hardware/topology/fluid-topology.md'))
    request.setdefault('aliases', {})
    specs = request.get('route_specs', metadata.get('native_route_specs', {}))
    bindings['route_specs_sha256'] = hashlib.sha256(
        json.dumps(specs, sort_keys=True).encode()).hexdigest()
    request['input_bindings'] = bindings
    sources = ('hardware/scripts/check_asse_drain.py',
               'hardware/manifold-layout/_drain.py',
               'hardware/manifold-layout/enclosure_assembly.py',
               'hardware/manifold-layout/_lines.py',
               'hardware/manifold-layout/rear_plumbing.py',
               'hardware/manifold-layout/above-core.json',
               'hardware/reference/neofit-drain-bulkhead/neofit_drain_bulkhead.py',
               'hardware/reference/asse1022-assembly/asse1022_assembly.py',
               'hardware/printed-parts/asse-drain-adapter/asse_drain_adapter.py',
               'hardware/scripts/_assembly_model.py',
               'hardware/manifold-layout/enclosure_assembly.rs',
               'hardware/manifold-layout/machine_checks.rs',
               'hardware/manifold-layout/machine_check_drain.rs',
               'hardware/manifold-layout/machine_check_geometry.rs',
               'hardware/manifold-layout/machine_check_report.rs',
               'hardware/manifold-layout/machine_check_routes.rs',
               'hardware/manifold-layout/machine_check_rules.json',
               'hardware/scripts/_machine_checks.py')
    request['source_sha256'] = {p: _sha(ROOT / p) for p in sources}
    said = _rust_part.check('machine', 'machine-checks', {'request': request})
    # Bindings are checked after the native read, just as the existing drain
    # reader checks its immutable model inputs after its queries.
    for role, binding in bindings.items():
        if isinstance(binding, dict) and _sha(binding['path']) != binding['sha256']:
            raise ValueError(f'Fine {role} input changed during machine checks')
    return said


def check(model, *, envelope, aliases=None, metadata, drain=True):
    """Check one installed model using the construction's plain metadata."""
    return read({'physical_model': model, 'envelope': envelope,
                 'aliases': aliases or {}, 'metadata': metadata, 'drain': drain})


def drain(model, *, envelope, names=None, route_specs=None, aliases=None,
          wiring_model=None, obstacles=None, expected_envelope_bounds=None,
          physical_reading=None):
    """The existing dedicated drain question, including its exact binding."""
    if physical_reading is not None:
        if (_path(physical_reading['path']) != _path(model) or
                physical_reading['sha256'] != _sha(model)):
            raise ValueError('Physical fine summaries belong to another model')
    request = {'mode': 'drain', 'physical_model': model, 'envelope': envelope,
               'aliases': aliases or {}, 'route_specs': route_specs or {},
               'expected_envelope_bounds': expected_envelope_bounds}
    if names is not None:
        request['checked_members'] = list(names)
    if wiring_model is not None:
        request['wiring_model'] = wiring_model
    if obstacles is not None:
        request['obstacles'] = list(obstacles)
    return read(request)['drain']
