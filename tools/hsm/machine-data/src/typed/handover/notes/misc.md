# misc agent notes

Modules: _facts, check_asse_drain, _tube_export, above_core_parts, above_core_wiring.
Stopped at the coordinator's wind-down (2026-11-04 ~21:50). ws/misc (workspace build, snapshots,
probe clones, compare outputs) is deleted; the probe that verified the non-genrule functions is
kept below.

## Module status

Builds compared: md-1 (19:28, four modules typed, _facts not yet) and md-3 (final source; opt-level 0).
Genrule compares ran with every worker pinned from bin-all, the generated build first in the same
call (or the saved base-trees); the probe ran once per build in a clone of a staged step and
compared canonical results entry by entry.

- **_facts: TYPED = true, complete.** md-3 matched the generated build on fluid-topology-sync
  (678 files, 0 differ), enclosure-mechanical-sync (671/0) and enclosure-dimensions (665/0); those
  run read, _request, _read_graph, _source_names and sources. The probe (md-3, 139 entries, 0
  differ, same stdout/stderr) matched the rest: consts, sources, source_digest, _source_names,
  _source_digest, _request (and None), _plain (15 cases), _box_plain (and stale), _BB, _Row, _Frame,
  _disagrees, the Facts properties and methods, stale, selftest, main, write, read of a missing
  file. Not run anywhere: _tube_handoff (nothing in the repo calls it).
- **above_core_parts: TYPED = true, complete.** foam-cap matched (md-1 against the saved base
  tree: 386 files, 0 differ; it runs _module). The md-3 edits touch only route_specs and the
  layout-data error text. The md-3 probe matched every other function: consts, refs, _frame,
  _compose, _snapshot, route_port_frame, _grid, _grid_module, core_components, _offset, _link,
  port_stations, _line, _bezier, _crowned_beziers, _sample_bezier, route_specs.
- **_tube_export: TYPED = true, complete.** No genrule runs it. The probe matched unit (3 cases)
  and _resolve_end (anchor, nearest, station, socket, keywords, missing) on md-3 (light pass, and
  29 of 29 entries of the CAD pass). Not run anywhere: route_metadata; its only caller is
  _facts._tube_handoff, which nothing calls.
- **check_asse_drain: TYPED = false; code complete, not fully verified.** No genrule runs it. The
  md-3 probe matched consts, sha (and missing), _path, _base, _overlap, _binding, _names,
  _torus_records, _rows (5 cases) and main's input checks (stale facts, scene binding, wiring
  manifest, no cold-core bodies, missing facts file). Left: compare `write` and the rest of `main`
  (input digests, placement bounds, output file) with the generated build. That needs a real
  installed fine model, scene and wiring manifest (the enclosure-assembly outputs), or a stub
  `_machine_checks.drain`. Then set TYPED = true.
- **above_core_wiring: TYPED = false; code complete, not fully verified.** foam-cap matched on md-1
  (placements, put; the file is unchanged since), and the md-3 probe matched consts, placements,
  frame, owner (and missing) and carry. Left: compare _box, _union, _well, _features,
  cap_features, shell_features, driver_columns and components. The probe's `cad` pass below does
  it in a clone of steps/enclosure-assembly: `run.py <steps/enclosure-assembly> base=<generated
  build> misc=<typed build> -- cad`. The generated build's pass recorded 131 entries (it then stops
  at `F.read()`, because that step has no enclosure-assembly.facts.json; the same for any build);
  the typed pass waited in admission and was stopped. Then set TYPED = true and compare
  enclosure-assembly, enclosure-box, enclosure and foam-cap.
- Not compared on md-3, stopped by the wind-down: install-envelope-sync, faucet-and-umbilical-sync,
  internal-plumbing-sync, valve-tray, pump-tray, bom-masses (_facts read, _request, _read_graph,
  _source_names, sources), rear-equipment-caps and enclosure (above_core_parts _module, _frame,
  _compose), foam-cap, enclosure-box, enclosure-assembly. Each runs only functions the compares and
  probe above matched.

## Comparing
- An opt-0 workspace build differs from the opt-3 generated build at arc samples (sin and cos merge
  into __sincos_stret at opt >= 1); none of these five modules calls sin or cos. Compare an opt-0
  build against bin-base0/machine-data.
- The saved base-trees predate compare.py's <ENGINE-TMP>: enclosure-box's
  tmp/machine-layout/pack/equipment/machine-equipment.json names the engine's pid-named scratch
  path, so it differs against base-trees/enclosure-box.json on every run. The saved enclosure run
  stopped at an error (enclosure-checks, nameplate-stock). Compare both with the generated build
  first in the same call.

## Shared files
- py::bind's error text differs from the generated bind (a list of unexpected keywords; too many
  positionals checked first). Error paths only.
- rt.layout_data does not give the generated error text `ValueError: layout-data: <error>`;
  above_core_parts wraps it locally (`layout_data`). If rt.layout_data adopts that text, drop the wrap.
- py::dict_of reads mappings only; `dict(pairs)` needs its own conversion (above_core_parts
  `dict_from`).
- The check_asse_drain surface's `_rust_exports` lists `pair`, which the generated namespace does
  not define (the CONNECTED comprehension binds it in a child env).

## Findings
- _facts: `_request` goes through `_rust_data.request` as generated (read() hands the documents to the
  Python Facts object, so a Python dict is the cheaper carrier). The graph reads behind sources(),
  source_digest(), _source_names, _source_digest are answered in process: `crate::answer` (read_json,
  optional) and `crate::source_names` — the same functions the worker runs — so the 1.5 MB graph no
  longer crosses into Python and back twice per call.
- _facts: methods of Facts call the module's own typed functions directly where the generated code went
  through the instance (self.bb, out.add, self.agrees_with_*). Error text in those paths would lose
  Python's KeyError quoting; no genrule reaches them.
- above_core_wiring: every replaceable name (layout, _box, cq, SIZES, WALL, FIT, rotations, carry,
  shell_features) is read from the namespace at use.
- above_core_parts: `_data` ops answered in process (rt.layout_data); stem_elbow_names and
  reservoir_gate_elbow_hosts called through the typed above_core_bom API.
- check_asse_drain: centerline_radii/_names/_torus_records reached through the namespace (native installs).
- _facts `_request`: hand-bound like the generated bind (op first, then excess positionals).

## Appendix: the probe

`run.py` (beside `probe.py`): runs probe.py under harness.py once per build, each in a fresh
`cp -c -R` clone of a staged step, removes the clone, and lists the entries that differ from the
first label's (or from a saved `<label>.json` with `--against=<label>`).

```python
"""Run probe.py once per machine-data binary, each in a fresh clone of a staged step, and diff.

usage: run.py <pristine step dir> <label=program> [<label=program> ...] [-- probe args]
Leaves <label>.json, <label>.out and <label>.err beside this file and prints the keys whose
entries differ from the first label's.
"""
import json, os, subprocess, sys, time
from pathlib import Path

REPO = '/Users/derekbredensteiner/Developer/homesodamachine'
R = Path(REPO) / '.cache/runs/machine-typed-202611041700'
HERE = Path(__file__).resolve().parent
py = f'{REPO}/tools/cad-venv/bin/python'
argv = sys.argv[1:]
extra = argv[argv.index('--') + 1:] if '--' in argv else []
argv = argv[:argv.index('--')] if '--' in argv else argv
pristine, variants = Path(argv[0]), [a.split('=', 1) for a in argv[1:]]
results = {}
against = None
if variants and variants[0][0] == '--against':
    against = variants.pop(0)[1]
    results[against] = json.loads((HERE / f'{against}.json').read_text())
for label, program in variants:
    work = HERE / f'work-{label}'
    fix = work / 'probe-fixture'
    if work.exists():
        subprocess.run(['rm', '-rf', str(work)], check=True)
    subprocess.run(['cp', '-c', '-R', str(pristine), str(work)], check=True)
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe', 'HSM_WORKSPACE': REPO,
           'PYTHONHASHSEED': '0'}
    t = time.perf_counter()
    try:
        with open(HERE / f'{label}.out', 'w') as out, open(HERE / f'{label}.err', 'w') as err:
            r = subprocess.run([py, str(R / 'harness.py'), str(R / 'bin-all'), program, str(HERE / 'probe.py'),
                                str(HERE / f'{label}.json'), str(fix), *extra], cwd=work, env=env, stdout=out,
                               stderr=err)
        print(label, 'exit', r.returncode, 'wall', round(time.perf_counter() - t, 1), flush=True)
    finally:
        subprocess.run(['rm', '-rf', str(work)], check=True)
    results[label] = json.loads((HERE / f'{label}.json').read_text())
first = against or variants[0][0]
for label, _ in (variants if against else variants[1:]):
    keys = sorted(set(results[first]) | set(results[label]))
    differ = [k for k in keys if results[first].get(k) != results[label].get(k)]
    print(label, 'entries', len(results[label]), 'of', len(results[first]), 'differ', len(differ), differ[:40])
    for name in ('out', 'err'):
        a, b = ['\n'.join(l for l in (HERE / f'{x}.{name}').read_text().splitlines() if not l.startswith('[run]'))
                for x in (first, label)]
        print(label, name, 'same' if a.replace(f'work-{first}', '<W>')
              == b.replace(f'work-{label}', '<W>') else 'DIFFERENT')
```

```python
"""Call the misc modules' functions that no genrule reaches, and write what each returned.

usage (cwd = a clone of a staged step, under harness.py): probe.py <out.json> <fixture dir> [cad]
Each entry is the canonical form of the value, or the exception's type and text. With `cad`,
the CadQuery-backed functions of above_core_wiring run too and their shapes are measured.
"""
import collections
import json
import sys
import types
from pathlib import Path, PurePath

work = Path.cwd()
for folder in ('hardware/manifold-layout', 'hardware/scripts'):
    sys.path.insert(0, str(work / folder))
out_path, fix = Path(sys.argv[1]), Path(sys.argv[2])
cad = 'cad' in sys.argv[3:]
fix.mkdir(parents=True, exist_ok=True)
OUT = {}


def clean(text):
    return text.replace(str(work), '<WORK>').replace(str(fix), '<FIX>')


def canon(v, depth=0):
    if depth > 12:
        return '<deep>'
    if v is None or isinstance(v, (bool, int, str)):
        return clean(v) if isinstance(v, str) else v
    if isinstance(v, float):
        return 'f:' + repr(v)
    if isinstance(v, PurePath):
        return 'Path:' + clean(str(v))
    if isinstance(v, bytes):
        return 'bytes:' + v.hex()
    if isinstance(v, tuple) and hasattr(v, '_fields'):
        return {'namedtuple': type(v).__name__, 'fields': [[f, canon(getattr(v, f), depth + 1)] for f in v._fields]}
    if isinstance(v, dict):
        return {'type': type(v).__name__, 'items': [[canon(k, depth + 1), canon(x, depth + 1)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [canon(x, depth + 1) for x in v]}
    if isinstance(v, (set, frozenset)):
        return {'type': type(v).__name__, 'items': sorted(json.dumps(canon(x, depth + 1), sort_keys=True) for x in v)}
    if isinstance(v, types.ModuleType):
        return 'module:' + v.__name__
    name = type(v).__name__
    if name == '_BB':
        return {'BB': [canon(getattr(v, k)) for k in ('xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax')], 'repr': repr(v)}
    if name == '_Frame':
        return {'Frame': canon(v.ports, depth + 1)}
    if hasattr(v, 'tolist'):
        return {'array': name, 'value': canon(v.tolist(), depth + 1)}
    if hasattr(v, 'toTuple'):
        return {'obj': name, 'tuple': canon(v.toTuple(), depth + 1)}
    if hasattr(v, 'BoundingBox') and hasattr(v, 'Volume'):
        b = v.BoundingBox()
        return {'shape': name, 'volume': round(v.Volume(), 6), 'faces': len(v.Faces()),
                'bbox': [round(x, 6) for x in (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)]}
    if callable(v):
        return 'callable:' + name
    attrs = {}
    for k in getattr(type(v), '__slots__', None) or sorted(getattr(v, '__dict__', {})):
        try:
            attrs[k] = canon(getattr(v, k), depth + 1)
        except Exception as exc:
            attrs[k] = 'err:' + type(exc).__name__
    return {'obj': name, 'attrs': attrs}


def rec(key, fn):
    try:
        row = {'ok': canon(fn())}
    except SystemExit as exc:
        row = {'exit': canon(exc.code)}
    except BaseException as exc:
        row = {'err': type(exc).__name__, 'msg': clean(str(exc))}
    OUT[key] = row
    sys.stdout.flush()
    sys.stderr.flush()


def save():
    out_path.write_text(json.dumps(OUT, indent=1) + '\n')


try:
    import numpy as np
    import _realized

    # --- _tube_export ---------------------------------------------------------------------
    import _tube_export as T
    rec('tube.consts', lambda: [T.ROOT, T.HW, T._p])
    rec('tube.unit', lambda: [T.unit((0, 0, 0), (3, 4, 0)), T.unit([1, 2, 3], [1, 2, 4.5]),
                              T.unit((0.1, 0.2, 0.3), (1, 1, 1)), T.unit(a=(0, 0, 0), b=(0, 0, -2))])
    rec('tube.unit.zero', lambda: T.unit((1, 1, 1), (1, 1, 1)))
    rec('tube.unit.short', lambda: T.unit((1, 1), (1, 2)))
    import _routing as R
    box = types.SimpleNamespace(xmin=-1., xmax=11., ymin=-1., ymax=1., zmin=-1., zmax=1.)
    R._frames['probe-frame'] = R.Frame('probe-frame', {'a': ((0., 0., 0.), (1., 0., 0.), 6.35),
                                                       'b': ((10., 0., 0.), (-1., 0., 0.), 4.)}, box)

    class FakeAssembly:
        carries = {'valve-v-a': lambda station: (tuple(station[0]), tuple(station[1]))}

    rec('tube._resolve_end.anchor', lambda: T._resolve_end(None, 'probe-frame.b', (0, 0, 0), (1, 0, 0), 6.35))
    rec('tube._resolve_end.nearest', lambda: [T._resolve_end(None, 'probe-frame', (9., 0., 0.), (1, 0, 0), 6.35),
                                              T._resolve_end(None, 'probe-frame', [1, 0.5, 0], (1, 0, 0), 6.35),
                                              T._resolve_end(None, 'probe-frame', (5, 0, 0), (1, 0, 0), 6.35)])
    rec('tube._resolve_end.station', lambda: T._resolve_end(FakeAssembly(), 'valve-v-a.inlet', (0, 0, 0), (1, 0, 0), 6.35))
    rec('tube._resolve_end.socket', lambda: T._resolve_end(None, 'loose-body', [1, 2, 3], [0, 0, 1], 4.0))
    rec('tube._resolve_end.kw', lambda: T._resolve_end(a=None, name='loose-body', at_pt=(1, 2, 3), tangent=(0, 0, 1), diam=4))
    rec('tube._resolve_end.missing', lambda: T._resolve_end(FakeAssembly(), 'no-body.port', (0, 0, 0), (1, 0, 0), 6.35))

    # --- check_asse_drain -----------------------------------------------------------------
    import check_asse_drain as C
    rec('cad.consts', lambda: [C.ROOT, C.OUTPUT, C.NAMES, C.CONNECTED, C.pair])
    some = work / 'hardware/manifold-layout/above-core.json'
    rec('cad.sha', lambda: [C.sha(some), C.sha(str(some))])
    rec('cad.sha.missing', lambda: C.sha(work / 'nope'))
    rec('cad._path', lambda: [C._path('hardware/manifold-layout/above-core.json'), C._path(str(some)),
                              C._path('hardware/../hardware/scripts'), C._path(Path('hardware'))])
    rec('cad._base', lambda: [C._base('cold-core/12'), C._base('a/b'), C._base('x/1/2'), C._base('plain'),
                              C._base('y/12a')])
    rec('cad._overlap', lambda: [C._overlap((0, 0, 0, 1, 1, 1), (2, 0, 0, 3, 1, 1)),
                                 C._overlap((0, 0, 0, 1, 1, 1), (2.5, 0, 0, 3, 1, 1)),
                                 C._overlap([0, 0, 0, 1, 1, 1], [0.5, 0.5, 0.5, 2, 2, 2]),
                                 C._overlap((0, 0, 0, 1, 1, 1), (0, 0, -3, 1, 1, -2.5))])

    def npz(path, **members):
        np.savez(path, **{k: np.frombuffer(json.dumps(v).encode(), dtype=np.uint8) for k, v in members.items()})
        return path

    names = ['cold-core/reservoir/1', 'tube-drain-vent', 'asse-drain-adapter']
    records = [[{'kind': 'PLANE'}, {'kind': 'TORUS', 'r': 1.5}], [{'kind': 'TORUS'}, 'x'], []]
    model = npz(fix / 'agg.step.npz', names=names, records=records)
    rec('cad._binding', lambda: [C._binding('hardware/manifold-layout/above-core.json'), C._binding(model)])
    rec('cad._names', lambda: C._names(model))
    rec('cad._torus_records', lambda: C._torus_records(model, [(0, 'cold-core/reservoir/1'), (1, 'tube-drain-vent')]))
    good = {'path': str(model), 'sha256': C.sha(model), 'bodies': [{'name': n, 'v': i} for i, n in enumerate(names)]}
    rec('cad._rows', lambda: C._rows(model, (), good))
    rec('cad._rows.kw', lambda: C._rows(model, component_names=('a',), reading=good))
    rec('cad._rows.other', lambda: C._rows(model, (), {**good, 'sha256': '0'}))
    rec('cad._rows.names', lambda: C._rows(model, (), {**good, 'bodies': good['bodies'][:2]}))
    rec('cad._rows.relative', lambda: C._rows(str(model), (), {**good, 'path': str(model)}))

    # main() up to the drain question, over fixture files
    (fix / 'agg.step').write_text('fixture step\n')
    (fix / 'card.json').write_text('{"checks": []}\n')
    wiring = fix / 'wiring.step.npz'
    wiring.write_bytes(b'fixture wiring')
    envelope = fix / 'envelope.json'
    envelope.write_text(json.dumps({'path': str(some), 'transform': [1, 0, 0]}))
    facts = {'card': _realized.code_digest(fix / 'card.json'), 'step': _realized.code_digest(fix / 'agg.step'),
             'bodies': {'foam-assembly': [0, 0, 0, 1, 1, 1]}, 'native_runs': [{'id': 'r1', 'x': 1}]}
    (fix / 'facts.json').write_text(json.dumps(facts))
    (fix / 'stale-facts.json').write_text(json.dumps({**facts, 'card': 'x'}))
    (fix / 'wiring.json').write_text(json.dumps({'physical_fine_model_sha256': C.sha(model),
                                                 'wiring_fine_model_sha256': 'mismatch'}))
    npz(fix / 'scene.npz', document={'drain': {'fine_inputs': {'physical': {'sha256': 'other'}}}})
    base = ['--aggregate', str(fix / 'agg.step'), '--scorecard', str(fix / 'card.json'),
            '--manifest', str(fix / 'wiring.json'), '--output', str(fix / 'drain.json')]
    rec('cad.main.stale', lambda: C.main([*base, '--facts', str(fix / 'stale-facts.json')]))
    rec('cad.main.scene', lambda: C.main([*base, '--facts', str(fix / 'facts.json'), '--scene', str(fix / 'scene.npz')]))
    rec('cad.main.wiring', lambda: C.main([*base, '--facts', str(fix / 'facts.json'), '--envelope-frame', str(envelope)]))
    nocore = fix / 'nocore'
    nocore.mkdir(exist_ok=True)
    (nocore / 'agg.step').write_text('fixture step\n')
    npz(nocore / 'agg.step.npz', names=names[1:], records=records[1:])
    rec('cad.main.nocore', lambda: C.main(['--aggregate', str(nocore / 'agg.step'), '--facts', str(fix / 'facts.json'),
                                           '--scorecard', str(fix / 'card.json')]))
    rec('cad.main.missing', lambda: C.main(['--facts', str(fix / 'absent.json')]))
    save()

    # --- above_core_wiring ----------------------------------------------------------------
    import above_core_wiring as W
    rec('w.consts', lambda: [W.SIZES, W.WALL, W.FIT, W.IDENTITY, W.PORTS_WEST, W.PORTS_FORE, W.UPRIGHT_PORTS_FORE,
                             W.WALL_BACK_FORE, W.WALL_BACK_AFT, W.EAST_FLANK, W.REFERENCES, W.HERE, W.HW, W.C_AC_HUB])
    rec('w.placements', W.placements)
    rec('w.frame', lambda: [W.frame('wago-h'), W.frame('nope')])
    rec('w.owner', lambda: [W.owner(n) for n in W.placements()])
    rec('w.owner.missing', lambda: W.owner('nope'))
    for n in ('wago-v12', 'wago-mana', 'wago-h'):
        rec(f'w.carry.{n}', lambda n=n: W.carry(n)(((1., 2., 3.), (0., 0., 1.))))
        rec(f'w.carry.where.{n}', lambda n=n: W.carry(n).where)
    if cad:
        rec('w._box', lambda: W._box(0, 1, -2, 2, 0.5, 3))
        rec('w._union.empty', lambda: W._union([]))
        rec('w._union', lambda: W._union([W._box(0, 1, 0, 1, 0, 1), W._box(0.5, 2, 0, 1, 0, 1)]))
        for n in W.placements():
            rec(f'w._well.{n}', lambda n=n: W._well(n))
        for parent in ('back-top', 'front-top', 'cold-core', 'nowhere'):
            rec(f'w._features.{parent}', lambda parent=parent: W._features(parent))
        rec('w.cap_features', W.cap_features)
        rec('w.shell_features', lambda: W.shell_features('back-top'))
        rec('w.driver_columns', W.driver_columns)
        rec('w.components', lambda: {k: (v[0], v[1], v[2].where) for k, v in W.components().items()})
    save()

    # --- above_core_parts -----------------------------------------------------------------
    import above_core_parts as P
    rec('p.consts', lambda: [P.IDENTITY, P.ORIGIN, P.REFERENCES, P.HERE, P.HW, P.ROOT])
    rec('p.refs', lambda: [P.check_reference(), P.tee_reference(), P.stem_elbow_reference(),
                           P.check_reference() is P.check_reference()])
    rec('p._frame', lambda: [P._frame(), P._frame(((1, 0, 0), (0, 1, 0), (0, 0, 1)), (1, 2, 3)),
                             P._frame(translation=(4, 5, 6))])
    rec('p._compose', lambda: P._compose(P._frame(translation=(1, 2, 3)),
                                         P._frame(((0, -1, 0), (1, 0, 0), (0, 0, 1)), (4, 5, 6))))
    rec('p._snapshot', lambda: [P._snapshot('reg'), P._snapshot('reg', P._frame(((0, 0, 1), (0, 1, 0), (-1, 0, 0)), (1, 0, 0)))])
    rec('p._snapshot.missing', lambda: P._snapshot('valve-v-b'))
    for n in ('suction-reducer', 'flow-regulator', 'valve-v-a', 'asse1022-assembly', 'nope'):
        rec(f'p.route_port_frame.{n}', lambda n=n: P.route_port_frame(n))
    rec('p._grid', P._grid)
    rec('p._grid_module', lambda: [P._grid_module({'native_kind': k}) for k in ('gas', 'quarter', 'four')])
    rec('p.core_components', P.core_components)
    rec('p._offset', lambda: [P._offset((0, 0, 0), (1, 0, 0)), P._offset((1, 2, 3), (0, 0, 1), 2.5),
                              P._offset(point=(1, 2, 3), vector=(0, 1, 0), length=-1)])
    rec('p._link', lambda: P._link((0, 0, 0), (1, 0, 0), 1., (10, 0, 0), (-1, 0, 0), 2.))
    import above_core_bom
    extra = [*list(above_core_bom.stem_elbow_names())[:2], *list(above_core_bom.reservoir_gate_elbow_hosts())[:2]]
    for n in ('valve-v-a', 'valve-v-b', 'vk-solenoid', 'asse1022-assembly', 'water-split', 'flow-regulator',
              'gas-regulator', 'gas-check', 'discharge-chain', 'asse-inlet-tpu', 'asse-outlet-tpu',
              'asse-drain-adapter', 'suction-reducer', 'nope', *extra):
        rec(f'p.port_stations.{n}', lambda n=n: P.port_stations(n))
    rec('p._line', lambda: P._line((0, 0, 0), (1, 2, 3)))
    rec('p._bezier', lambda: P._bezier([(0, 0, 0), (1, 1, 0), (2, 0, 0)]))
    cubic = [(0, 0, 0), (1, 1, 0), (2, 1, 0.5), (3, 0, 0)]
    rec('p._crowned_beziers', lambda: [P._crowned_beziers(cubic, 0.5), P._crowned_beziers(cubic, 0.5, 4),
                                       P._crowned_beziers(control=cubic, crown=-1., intervals=3)])
    rec('p._crowned_beziers.bad', lambda: P._crowned_beziers([(0, 0, 0), (1, 1, 0), (2, 0, 0)], 0.5))
    rec('p._sample_bezier', lambda: [P._sample_bezier(cubic, 5), P._sample_bezier(cubic)])
    rec('p._sample_bezier.bad', lambda: P._sample_bezier([(0, 0, 0), (1, 1, 0), (2, 0, 0)], 5))
    rec('p.route_specs', P.route_specs)
    save()

    # --- _facts ---------------------------------------------------------------------------
    import _facts as F
    rec('facts.consts', lambda: [F.ARTIFACT, F.SCORECARD, F.STEP, F.SCHEMA, F.GRAPH, F.GENERATOR, F.DECLARED_GAPS,
                                 F.DECLARED_RUN_NEIGHBOURS, F.CARD_PORT_BODIES, F._BOX_FACT_ORDER,
                                 F._BOX_FACT_EXCLUDED, F._HERE, F._HW, F._ROOT, F._p])
    rec('facts.sources', F.sources)
    rec('facts.source_digest', F.source_digest)
    graph = F._read_graph()
    rec('facts._source_names', lambda: F._source_names(graph))
    rec('facts._source_digest', lambda: [F._source_digest(graph), F._source_digest({})])
    rec('facts._request', lambda: [F._request('read_json', path=str(F.SCORECARD))['checks'][:2],
                                   F._request(op='read_json', path=str(fix / 'absent.json'), optional=True)])
    rec('facts._request.none', lambda: F._request())
    NT = collections.namedtuple('NT', 'a b')

    class Vec:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class Weird:
        pass

    plain_cases = [None, True, 3, 2.5, 'x', NT(1, (2, 3)), {1: 'a', 'b': [1, 2]}, [1, (2,)], (1, 2), {3},
                   frozenset({4}), Vec(1, 2.5, 3), NT(Vec(1, 2, 3), {'k': NT(1, 2)}), Weird(), [Weird()]]
    for i, v in enumerate(plain_cases):
        rec(f'facts._plain.{i}', lambda v=v: F._plain(v))
    order = F._BOX_FACT_ORDER
    PackNT = collections.namedtuple('PackNT', order[:12])
    BoxNT = collections.namedtuple('BoxNT', [*order[12:], 'pack', 'placed', 'keystone'])
    kinds = [1.5, (1, 2), {'k': (1.0, 2)}, None, 'text', [Vec(1, 2, 3)], NT(1, 2), {3: 4}, True, frozenset({'a'})]
    pack = PackNT(*[kinds[i % len(kinds)] for i in range(12)])
    box = BoxNT(*[kinds[(i + 3) % len(kinds)] for i in range(len(order) - 12)], pack, 'solids', (0, 0, 1))
    rec('facts._box_plain', lambda: F._box_plain(box))
    StaleNT = collections.namedtuple('StaleNT', [*order[12:-1], 'bogus', 'pack'])
    stale_box = StaleNT(*range(len(order) - 12), pack)
    rec('facts._box_plain.stale', lambda: F._box_plain(stale_box))
    bb = F._BB(1, 2.5, 3, 4, 5, 6.25)
    rec('facts._BB', lambda: [bb, bb.xlen, bb.ylen, bb.zlen, repr(bb), F._BB(xmin=0, ymin=0, zmin=0, xmax=1, ymax=1, zmax=1)])
    rec('facts._BB.add', lambda: [bb.add(F._BB(0, 3, 2, 5, 4, 7)), F._BB(1, 1, 1, 2, 2, 2).add(F._BB(1.0, 0, 1, 2.0, 3, 2))])
    row = F._Row({'a': 1})
    rec('facts._Row', lambda: [row.a, row, isinstance(row, dict)])
    rec('facts._Row.missing', lambda: row.zz)
    rec('facts._Frame', lambda: F._Frame({'p': {'pos': [1, 2, 3], 'axis': (0, 0, 1), 'diam': 6.35}}))
    rec('facts._disagrees', lambda: [F._disagrees('x.json', 'taken beside', None, 'abc'),
                                     F._disagrees('x.json', 'measured off', 'def', None)])
    f = F.read()
    for name in ('box', 'pack', 'wall_ports', 'pieces', 'valve_trays', 'valve_tray_stations', 'pump_trays', 'gaps',
                 'faces', 'card_ports', 'carried_points', 'card_digest', 'constants', 'hopper_hole',
                 'manifold_bodies', 'mouths', 'bodies', 'runs'):
        rec(f'facts.Facts.{name}', lambda name=name: getattr(f, name))
    bodies = list(f.bodies)
    rec('facts.Facts.bb', lambda: [f.bb(b) for b in bodies[:5]])
    rec('facts.Facts.bb.missing', lambda: f.bb('no-such-body'))
    rec('facts.Facts.group', lambda: [f.group(lambda n: n.startswith('valve')), f.group(lambda n: True)])
    rec('facts.Facts.group.none', lambda: f.group(lambda n: False))
    rec('facts.Facts.near.missing', lambda: f.near('no-run'))
    rec('facts.Facts.check', lambda: [f.check('clearance-floor'), f.check(cid='clearance-floor')])
    rec('facts.Facts.check.missing', lambda: f.check('no-check'))
    rec('facts.Facts.agrees', lambda: [f.agrees_with_card(), f.agrees_with_step(), f.agrees_with_sources()])
    rec('facts.Facts.stale', f.stale)
    moved = F.Facts({**f._f, 'sources': '0' * 32, 'card': None, 'step': 'x'}, f._c)
    rec('facts.Facts.stale.moved', lambda: [moved.agrees_with_card(), moved.agrees_with_step(),
                                            moved.agrees_with_sources(), moved.stale()])
    rec('facts.selftest', F.selftest)
    rec('facts.main', lambda: F.main([]))
    rec('facts.main.selftest', lambda: F.main(['selftest']))
    rec('facts.main.write', lambda: F.main(['--write']))
    rec('facts.write', lambda: [F.write({'b': 1, 'a': [1.5, None, 'é']}), F.ARTIFACT.read_text()])
    rec('facts.read.missing', lambda: (F.ARTIFACT.unlink(), F.read())[1])
finally:
    save()
```
