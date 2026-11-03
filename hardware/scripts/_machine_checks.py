"""Plain-data adapter to the machine's Rust fit, clearance and drain reader.

The physical model is immutable. Placement provides scalar construction ledgers
and explicit installed frames; Rust owns geometry import, tools and decisions.
"""
from __future__ import annotations

import ast
from contextlib import redirect_stdout
import hashlib
import importlib
import io
import json
from pathlib import Path
import sys

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


def _source_statements(path, names, bounds=()):
    """The source's existing scalar declarations, without its native assembly imports."""
    source = ast.parse(path.read_text(), filename=str(path))
    selected = []
    for node in source.body:
        target = node.targets[0].id if (isinstance(node, ast.Assign) and
            isinstance(node.targets[0], ast.Name)) else getattr(node, 'name', None)
        if target in names:
            selected.append(node)
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            call = node.value
            if call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value in bounds:
                selected.append(node)
        elif isinstance(node, ast.For) and '_port_stack' in ast.unparse(node):
            selected.append(node)
    return compile(ast.Module(body=selected, type_ignores=[]), str(path), 'exec')


def _construction_metadata(request):
    """Carry the source's existing final assembly questions to its Rust readers.

    Import-time scalar claims no longer arrive incidentally through native CAD
    imports. The enclosure question graph constructs the handhold tools in Rust;
    the slope question uses the same immutable final physical members as the
    other machine checks.
    """
    metadata = request['metadata']
    if not metadata.get('box'):
        return
    hardware = ROOT / 'hardware'
    paths = (hardware / 'manifold-layout', hardware / 'cold-core-layout',
             hardware / 'printed-parts/enclosure/enclosure',
             hardware / 'printed-parts/refrigeration/fuse-clamp',
             hardware / 'printed-parts/enclosure/bulkhead-ring',
             hardware / 'reference/jg-bulkhead-union',
             hardware / 'reference/neofit-drain-bulkhead', hardware / 'reference/neofit-bulkhead')
    for path in paths:
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))
    import _enclosure_datums
    shell = _enclosure_datums.load()
    import _coil  # its tail ledger uses only the numeric _TailLayout
    import fuse_clamp  # its donor ledger is entirely scalar
    import _stated_bounds
    import _box_spec
    import above_core
    import fits
    import _rust_enclosure_checks as enclosure_checks
    import _assembly_model
    types = {kind.__name__: kind for kind in (shell.Pack, shell.PortField, shell.Nameplate)}
    document = metadata['box']
    box = shell.Box(*(_box_spec._tupled(document['box'][field], types)
                      for field in shell.Box._fields))
    source = hardware / 'manifold-layout/enclosure_assembly.py'
    scope = {'_enc': shell, '_stated': _stated_bounds, '_above': above_core, 'fits': fits,
             '_jg': importlib.import_module('jg_bulkhead_union'),
             '_ring': importlib.import_module('bulkhead_ring'),
             '_drain_bulkhead': importlib.import_module('neofit_drain_bulkhead'),
             '_neofit': importlib.import_module('neofit_bulkhead')}
    exec(_source_statements(source, {'Y_WALL_FITTINGS', 'PORT_BOSS_PROUD',
        'port_clamp_stack', '_port_stack', 'WEDGE_CLEAR', 'KEPT_WEDGES',
        'authored_anchor_corbels', '_PLAN_INSET'}, {'port-pocket-floor'}), scope)
    wanted = {'fuse-clamp-donor', 'stub-tails-billed', 'port-pocket-floor', 'port-clamp-stack'}
    rows = [{**bound._asdict(), 'kind': 'gate'} for bound in _stated_bounds.records()
            if bound.id in wanted]

    frame = metadata['frames']['funnel-drain-union']
    stem_top = frame['ports']['stub']['pos'][2]
    funnel = shell._funnel
    elbow = importlib.import_module('neofit_stem_elbow')
    land_top = shell.funnel_seat_z(box.outer) + funnel.spout_land_z
    floor = shell._funnel_frame_part.datums(shell.funnel_seat_z(box.outer))[0]
    bend_z = frame['transform'][2][3]
    body_air = floor - bend_z - elbow.COLLAR_OD / 2.
    drain = next((row for row in metadata['runs']
                  if row['id'] == 'above-core-drain-vb-east-link'), None)
    rows.append(dict(id='funnel-drain-attachment',
        label='The removable funnel seals on the retained elbow stem', kind='goal',
        ok=abs(stem_top - land_top) < 1.e-3 and body_air > 0 and drain is not None,
        value=f'Uncut ATEU44W tip Z{stem_top:.3f}; {funnel.sealing_land:.3f} mm engagement; '
              f'socket body {body_air:.3f} mm below the frame; fluid-4 ' +
              (f"{drain['length']:.1f} mm to V-B" if drain is not None else 'not drawn'),
        target='a fixed elbow stem through the frame connected to V-B',
        detail=["The cradle's snap and the plug's push-on seal on the stem are not physically "
                'qualified; `zone-c/funnel/cradle-trial` tests the snap.']))

    indices = {}
    for i, (name, _color) in enumerate(_assembly_model.identity(request['physical_model'])):
        logical = name.rsplit('/', 1)[0] if name.rsplit('/', 1)[-1].isdigit() else name
        indices.setdefault(logical, []).append(i)

    def handhold(graph):
        pieces = {name: graph.model(dict(model=request['physical_model'],
                  indices=indices['enclosure-' + name]))
                  for name in ('front-bottom', 'back-bottom')}
        original = shell.record_bound
        shell.record_bound = lambda row: row
        try:
            with enclosure_checks._numeric(shell, graph, box):
                return shell._handhold_bound(pieces, box)
        finally:
            shell.record_bound = original

    graph = enclosure_checks._Questions()
    with redirect_stdout(io.StringIO()):
        handhold(graph)
    measured = enclosure_checks._measure(graph)
    row = handhold(enclosure_checks._Questions(measured))
    rows.append({**row._asdict(), 'kind': 'gate'})
    replace = {row['id'] for row in rows}
    metadata['bounds'] = [row for row in metadata.get('bounds', ()) if row['id'] not in replace] + rows
    metadata['wedge_question'] = dict(clearance=scope['WEDGE_CLEAR'], inset=scope['_PLAN_INSET'],
        print_up=shell.PIECE_PRINT_UP,
        kept=[*scope['KEPT_WEDGES'], *scope['authored_anchor_corbels'](metadata.get('tube_anchors', ()))],
        piece_paths={name: 'hardware/printed-parts/enclosure/enclosure/enclosure-' + name + '.step'
                     for name in shell.PIECE_PRINT_UP})


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
    if request.get('mode', 'all') not in ('drain', 'geometry', 'clearance'):
        _construction_metadata(request)
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
               'hardware/manifold-layout/machine_check_bounds.rs',
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
