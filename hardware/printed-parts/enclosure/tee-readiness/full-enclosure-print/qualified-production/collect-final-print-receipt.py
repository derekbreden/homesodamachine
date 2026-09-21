#!/usr/bin/env python3
"""Collect an exact, fresh enclosure print input receipt after the coordinated chain.

Read-only except for a NEW output directory. No CAD imports, generators, slicer,
printer calls, historical source-equivalence exceptions, or support approvals.
A receipt is written only after every required check passes. On failure the new
output directory contains receipt-audit.json, never current-geometry.json.

A fresh verify_current_front_top.py report can supply both native carrier equality
and the canonical 2 mm pusher route. Alternatively supply two bounded reports:
 --carrier-equality: status=pass, claims.canonical_carriers_equal_motion_gate=true;
 --pusher-check: status=pass, claims.canonical_2mm_pusher_motion_clear=true.
Each bounded report must contain nonempty checks (all pass=true), input_sha256 and
source_sha256 maps, zero failures/drift, and exact required current inputs. These
are geometry proofs, not a permission to reuse any old native support reading.
"""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import zipfile

ROOT_DEFAULT = Path('/Users/derekbredensteiner/Developer/homesodamachine')
WORK_DEFAULT = Path('/tmp/scanner-review/integration-correction')
PROFILE = 'hardware/printed-parts/petgf.3mf'
PROFILE_SHA = '3864deceaa295d0fffded05e445b77ee926e2706d8765fdc8bbf81a23fe98697'
BOX = 'hardware/manifold-layout/enclosure-box.json'
ASSEMBLY = 'hardware/manifold-layout/enclosure-assembly'
ENC = 'hardware/printed-parts/enclosure/enclosure'
CARRIER = 'hardware/printed-parts/enclosure/tee-carrier'
PUSHER = 'hardware/printed-parts/fixtures/carrier-spring-pusher'
FOAM = 'hardware/printed-parts/cold-core/foam-cap'
MOUNT_NATIVE = (FOAM + '/foam-cap-top.step', FOAM + '/foam-cap-top.stl',
                FOAM + '/foam-cap-top.step.mesh', FOAM + '/foam-cap-lid-top.step',
                FOAM + '/foam-cap-lid-top.step.mesh')
LID_MESH = '.cache/prints/2026-09-21-g-ganen-foam-cap-lid-top-h2c-v2/inputs/foam-cap-lid-top.stl'
PRODUCERS = (
    'hardware/manifold-layout/enclosure_box.py',
    ENC + '/enclosure.py',
    CARRIER + '/tee_carrier.py',
    'hardware/scripts/flute_payload_enclosure.py',
    'hardware/manifold-layout/enclosure_assembly.py',
)
SHELL_BASES = tuple(f'{ENC}/enclosure-{name}' for name in
                   ('front-top', 'front-bottom', 'back-top', 'back-bottom'))
CARRIER_BASES = tuple(f'{CARRIER}/enclosure-tee-carrier-{side}' for side in ('left', 'right'))
PUSHER_BASE = PUSHER + '/carrier-spring-pusher'
PART_BASES = (*SHELL_BASES, *CARRIER_BASES, PUSHER_BASE)
PART_ARTIFACTS = tuple(base + ext for base in PART_BASES for ext in ('.step', '.stl', '.step.mesh'))
CARRIER_INPUTS = {BOX, *(base + ext for base in CARRIER_BASES for ext in ('.step', '.stl'))}
PUSHER_INPUTS = CARRIER_INPUTS | {SHELL_BASES[0] + '.step', PUSHER_BASE + '.step', PUSHER_BASE + '.stl'}
CARRIER_SOURCES = {CARRIER + '/tee_carrier.py', CARRIER + '/_simple_carrier.py',
                   'hardware/manifold-layout/enclosure_assembly.py'}
PUSHER_SOURCES = CARRIER_SOURCES | {ENC + '/enclosure.py', CARRIER + '/_carrier_motion.py',
                                   PUSHER + '/carrier_spring_pusher.py'}
SHA_RE = re.compile(r'^[0-9a-f]{64}$')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def gate_errors(card):
    errors = []
    if card.get('gatesPass') is not True:
        errors.append('assembly scorecard gatesPass is not true')
    rows = card.get('checks')
    if not isinstance(rows, list) or not rows:
        return errors + ['assembly scorecard contains no checks']
    gates = [r for r in rows if r.get('kind') == 'gate' and r.get('active', True)]
    if not gates:
        errors.append('assembly scorecard has no active gates')
    for row in gates:
        if row.get('status') != 'pass':
            errors.append(f"active gate {row.get('id')} is {row.get('status')}: {row.get('value')}")
    motion = [r for r in rows if r.get('id') == 'tee-carrier-motion']
    if len(motion) != 1 or motion[0].get('status') != 'pass' or not motion[0].get('active', True):
        errors.append('current tee-carrier-motion gate is absent, inactive or not passing')
    return errors


class Audit:
    def __init__(self, root):
        self.root = root.resolve()
        self.issues = []
        self.seen = {}
        self.artifacts = {}
        self.sources = {}
        self.evidence = {}
        self.inputs = {}
        self.traced_read_names = set()
        self.details = {}

    def path(self, name):
        p = Path(name)
        return (self.root / p).resolve() if not p.is_absolute() else p.resolve()

    def label(self, path):
        p = self.path(path)
        return str(p.relative_to(self.root)) if p.is_relative_to(self.root) else str(p)

    def error(self, message):
        self.issues.append(str(message))

    def hash(self, path):
        p = self.path(path)
        try:
            before = p.stat()
            value = digest(p)
            after = p.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ValueError('file changed while hashing')
            name = self.label(p)
            if name in self.seen and self.seen[name] != value:
                raise ValueError('file changed during collection')
            self.seen[name] = value
            return value
        except (OSError, ValueError) as e:
            self.error(f'{self.label(p)}: {e}')
            return None

    def remember(self, path, group):
        value = self.hash(path)
        if value:
            group[self.label(path)] = value
        return value

    def load(self, path, group=None):
        if not self.remember(path, self.evidence if group is None else group):
            return None
        try:
            return json.loads(self.path(path).read_text())
        except (OSError, ValueError) as e:
            self.error(f'{self.label(path)}: invalid JSON: {e}')
            return None

    def map_matches(self, mapping, scope, *, group=None, required=()):
        if not isinstance(mapping, dict) or not mapping:
            self.error(f'{scope}: missing nonempty hash map')
            return
        normalized = {}
        for name, expected in mapping.items():
            key = self.label(name)
            normalized[key] = expected
            if not isinstance(expected, str) or not SHA_RE.fullmatch(expected):
                self.error(f'{scope}: invalid SHA256 for {name}')
                continue
            actual = self.hash(name)
            if actual != expected:
                self.error(f'{scope}: {name} changed (expected {expected}, actual {actual})')
            elif group is not None:
                group[key] = actual
        for name in required:
            if self.label(name) not in normalized:
                self.error(f'{scope}: does not bind required {name}')

    def verify_proof(self, path, *, role, full=False):
        doc = self.load(path)
        if not isinstance(doc, dict):
            return
        expected_inputs = PUSHER_INPUTS if role == 'pusher' or full else CARRIER_INPUTS
        expected_sources = PUSHER_SOURCES if role == 'pusher' or full else CARRIER_SOURCES
        self.map_matches(doc.get('input_sha256'), f'{role} proof inputs', group=self.evidence,
                         required=expected_inputs)
        self.map_matches(doc.get('source_sha256'), f'{role} proof sources', group=self.sources,
                         required=expected_sources)
        for key in ('failures', 'source_drift', 'loaded_source_drift'):
            if doc.get(key):
                self.error(f'{role} proof has {key}: {doc[key]}')
        checks = doc.get('checks')
        if not isinstance(checks, list) or not checks or any(r.get('pass') is not True for r in checks):
            self.error(f'{role} proof has missing or nonpassing native checks')
        if full:
            if doc.get('status') != 'current_front_top_native_pass' or doc.get('all_native_checks_pass') is not True:
                self.error('fresh full front-top proof has no current native pass')
            pusher = doc.get('canonical_pusher', {})
            if abs(pusher.get('thickness_mm', -1) - 2.0) > 1e-9:
                self.error('fresh front-top proof does not qualify the canonical 2 mm pusher')
        else:
            claim = 'canonical_2mm_pusher_motion_clear' if role == 'pusher' else 'canonical_carriers_equal_motion_gate'
            if doc.get('status') != 'pass' or doc.get('claims', {}).get(claim) is not True:
                self.error(f'{role} proof does not establish {claim}')
        self.details.setdefault('mechanism_evidence', []).append({
            'role': 'carrier equality and canonical 2 mm pusher route' if full else role,
            'path': self.label(path), 'sha256': self.hash(path), 'status': doc.get('status'),
            'check_count': len(checks) if isinstance(checks, list) else 0,
        })


def inspect_profile(a):
    actual = a.remember(PROFILE, a.artifacts)
    if actual != PROFILE_SHA:
        a.error('saved PET-GF profile differs from the selected exact profile')
        return
    with zipfile.ZipFile(a.path(PROFILE)) as z:
        if z.testzip() is not None:
            a.error('saved PET-GF project has a damaged member')
        settings = json.loads(z.read('Metadata/project_settings.config'))
    expected = {'brim_type': 'auto_brim', 'filament_nozzle_map': ['0'],
                'filament_colour': ['#000000'], 'nozzle_diameter': ['0.4', '0.4'],
                'print_sequence': 'by layer', 'layer_height': '0.24',
                'initial_layer_print_height': '0.2', 'curr_bed_type': 'Textured PEI Plate'}
    for key, value in expected.items():
        if settings.get(key) != value:
            a.error(f'saved profile {key} is not {value!r}')
    if settings.get('extruder_printable_area', [None])[0] != '0x0,325x0,325x320,0x320':
        a.error('saved left nozzle does not name the selected 325 x 320 mm area')
    a.details['profile'] = {'path': PROFILE, 'sha256': actual, 'settings': expected,
        'left_nozzle_area_mm': [[0, 0], [325, 320]], 'model_border_mm': 15,
        'requested_trim_mm': {'H2C': 0.18, 'Mark2': 0.04},
        'effective_textured_trim_mm': {'H2C': 0.16, 'Mark2': 0.02},
        'native_support_and_auto_brim_paths_reviewed': False}


def inspect_published_payload(a, proof_path, generated_sha):
    """Qualify the explicit publication stage after the native production chain.

    The site's publisher replaces six fixed viewer surfaces in the same frame
    and carries two moving carrier surfaces onto their native assembled poses.
    This is not a replacement for any native or printed-mesh input: the
    before/after verifier proves that exact transform.
    """
    doc = a.load(proof_path)
    if not isinstance(doc, dict):
        return
    checks = doc.get('checks')
    if (doc.get('status') != 'pass' or doc.get('failures') or not checks
            or any(row.get('pass') is not True for row in checks)):
        a.error('published viewer payload has no passing exact transformation proof')
    if doc.get('before_sha256') != generated_sha:
        a.error('published viewer proof does not start at this completed generator output')
    before = doc.get('before_payload')
    if not before or a.remember(before, a.evidence) != generated_sha:
        a.error('published viewer proof lacks the exact retained generator payload')
    payload = ASSEMBLY + '.step.mesh'
    if a.path(doc.get('after_payload', '')) != a.path(payload):
        a.error('published viewer proof does not name the canonical assembly payload')
    if a.hash(payload) != doc.get('after_sha256'):
        a.error('published viewer proof differs from the current published payload')
    if a.hash(ASSEMBLY + '.step') != doc.get('source_step_sha256'):
        a.error('published viewer proof differs from the current native assembly')
    a.map_matches(doc.get('source_sha256'), 'published viewer verifier sources', group=a.sources,
                  required=('hardware/scripts/flute_payload.py', 'hardware/scripts/_mesh_payload.py'))
    a.map_matches(doc.get('input_sha256'), 'published viewer canonical surfaces', group=a.artifacts,
                  required=(ASSEMBLY + '.step', *(base + ext for base in (*SHELL_BASES, *CARRIER_BASES)
                                                 for ext in ('.step', '.stl', '.step.mesh'))))
    pointers = json.loads(a.path('hardware/cad-artifacts.json').read_text()).get('solids', {})
    for name in (payload, ASSEMBLY + '.step'):
        if pointers.get(name) != a.hash(name):
            a.error('published pointer does not name the current artifact: ' + name)
    a.details['publication_stage'] = {'proof': a.label(proof_path),
        'proof_sha256': a.hash(proof_path), 'generator_payload_sha256': generated_sha,
        'published_payload_sha256': doc.get('after_sha256'),
        'transformation': 'Six canonical fixed surfaces and two carriers at their facts-bound assembled poses; all other entries unchanged.',
        'physical_print_inputs_changed': False}


def inspect_chain(a, work, published_payload_check=None):
    chain_path = work / 'final-chain.json'
    chain = a.load(chain_path)
    if not isinstance(chain, list) or [r.get('producer') for r in chain] != list(PRODUCERS):
        a.error('final-chain.json does not contain exactly the five completed production phases')
        return False
    if any(row.get('exit_code') != 0 for row in chain):
        a.error('one or more final production phases did not exit 0')
        return False
    a.remember(work / 'run-final-chain.py', a.evidence)
    a.remember(work / 'trace-production.py', a.evidence)
    latest_outputs, producer_rows, trace_inputs = {}, [], set()
    for row in chain:
        producer = row['producer']; stem = Path(producer).stem
        record_path = work / 'generation' / (stem + '.generation.json')
        trace_path = work / 'generation' / (stem + '.input-trace.json')
        record, trace = a.load(record_path), a.load(trace_path)
        a.remember(row['log'], a.evidence)
        if not isinstance(record, dict) or not isinstance(trace, dict):
            continue
        a.traced_read_names.update(trace.get('reads', []))
        if record.get('producer') != producer or record.get('raised') is not None or trace.get('raised') is not None:
            a.error(f'{producer}: mismatched or failed producer trace')
        if record.get('loaded_source_drift'):
            a.error(f"{producer}: loaded-source drift {record['loaded_source_drift']}")
        a.map_matches(record.get('loaded_source_sha256'), producer + ' loaded sources', group=a.sources,
                      required=(producer,))
        outputs = record.get('output_sha256')
        if not isinstance(outputs, dict) or not outputs:
            a.error(f'{producer}: output hashes missing')
            outputs = {}
        # A later chain member intentionally replaces a payload made by an earlier member.
        # Validate its FINAL producing occurrence, without accepting stale intermediate bytes.
        for name, value in outputs.items():
            latest_outputs[name] = (value, producer)
        trace_inputs.update(name for name in trace.get('reads', [])
                            if name.startswith(('hardware/', 'tools/'))
                            and not name.startswith(('tools/cad-venv/', 'tools/cad-venv-site/'))
                            and a.path(name).is_file())
        producer_rows.append({'producer': producer, 'generation_receipt': a.label(record_path),
            'generation_receipt_sha256': a.hash(record_path), 'input_trace': a.label(trace_path),
            'input_trace_sha256': a.hash(trace_path), 'rewritten_sources': record.get('rewritten_sources', [])})
    for name, (expected, producer) in latest_outputs.items():
        if name == ASSEMBLY + '.step.mesh' and published_payload_check is not None:
            inspect_published_payload(a, published_payload_check, expected)
        else:
            a.map_matches({name: expected}, producer + ' final output')
    required_chain_outputs = (BOX, *(p for p in PART_ARTIFACTS if not p.startswith(PUSHER + '/')),
                              ASSEMBLY + '.step', ASSEMBLY + '.step.mesh',
                              ASSEMBLY + '.scorecard.json', ASSEMBLY + '.facts.json')
    for name in required_chain_outputs:
        if name not in latest_outputs:
            a.error(f'no completed chain producer owns required output {name}')
    # Snapshot current on-disk reads. The runner records read paths, not load-time
    # byte hashes for non-Python inputs; name that limit instead of inventing one.
    for name in sorted(trace_inputs):
        value = a.remember(name, a.inputs)
        if value:
            target = a.sources if name.endswith('.py') else a.artifacts if name.endswith(('.step', '.stl', '.step.mesh')) else a.evidence
            target[a.label(name)] = value
    a.details['producers'] = producer_rows
    a.details['trace_input_scope'] = ('Current bytes of repository files named by completed raw read traces. '
        'Python bytes additionally match producer loaded-source receipts. Chain-written inputs match '
        'their final producer receipts. The trace runner does not record load-time byte hashes for other inputs.')
    return True


def inspect_facts(a):
    # Pure reader modules. Neither imports or constructs CadQuery geometry here.
    facts_source = 'hardware/scripts/_facts.py'
    realized_source = 'hardware/scripts/_realized.py'
    a.remember(facts_source, a.sources); a.remember(realized_source, a.sources)
    a.remember('tools/bazel/graph.json', a.evidence)
    spec = importlib.util.spec_from_file_location('_receipt_facts', a.path(facts_source))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    facts = module.read()
    result = {'card': facts.agrees_with_card(), 'step': facts.agrees_with_step(),
              'sources': facts.agrees_with_sources(), 'source_count': len(module.sources()),
              'stale': facts.stale()}
    if any(result[key] is not True for key in ('card', 'step', 'sources')) or result['stale']:
        a.error(f'facts do not bind the current card, assembly STEP and source tree: {result}')
    absent = []
    for name in module.sources():
        if not a.path(name).is_file():
            # The graph's directory expansion includes historical study names
            # which are absent. _facts' own digest records absence as an empty
            # contribution; do not invent a file digest or a print dependency.
            if name in a.traced_read_names or name in PART_ARTIFACTS:
                a.error('required facts input is absent: ' + name)
            absent.append(name)
        else:
            a.remember(name, a.sources if name.endswith('.py') else a.evidence)
    result['absent_declared_names'] = absent
    result['absence_scope'] = 'Names absent in the facts graph and current checkout; no print artifact or successful current read is qualified by absence.'
    a.details['facts_current'] = result


def inspect_pusher_export(a):
    path = PUSHER + '/geometry-check.json'
    doc = a.load(path)
    if not isinstance(doc, dict):
        return
    a.map_matches(doc.get('source_sha256'), 'pusher producer sources', group=a.sources,
                  required=(PUSHER + '/carrier_spring_pusher.py',))
    a.map_matches(doc.get('artifacts'), 'pusher producer outputs', group=a.artifacts,
                  required=(PUSHER_BASE + ext for ext in ('.step', '.stl', '.step.mesh')))
    if not (doc.get('native_valid') is True and doc.get('native_solids') == 1
            and doc.get('mesh_watertight') is True and doc.get('mesh_bodies') == 1
            and doc.get('constant_thickness_mm') == 2.0):
        a.error('pusher export does not establish one closed 2 mm tool')


def inspect_mount_inputs(a, manifest):
    """Bind canonical mount inputs; a separately checked new lid mesh is optional.

    Without the mesh manifest the receipt cannot stage the lid: its exact mesh
    is absent from artifact_sha256. This does not delay the five shell/carrier
    plates. No previously cached STEP or mesh is an implicit substitute.
    """
    for name in MOUNT_NATIVE:
        a.remember(name, a.artifacts)
    a.details['pump_mount_inputs'] = {'canonical_inputs': list(MOUNT_NATIVE),
        'lid_mesh_included': False, 'lid_print_staging_qualified': False,
        'required_lid_mesh': LID_MESH}
    if manifest is None:
        a.details['pump_mount_inputs']['pending'] = 'Fresh native triangulation and its exact mesh provenance manifest are required before lid staging.'
        return
    doc = a.load(manifest)
    if not isinstance(doc, dict):
        return
    a.map_matches(doc.get('source_sha256'), 'mount native inputs', group=a.artifacts,
                  required=(FOAM + '/foam-cap-top.step', FOAM + '/foam-cap-top.stl',
                            FOAM + '/foam-cap-lid-top.step'))
    a.map_matches(doc.get('tool_sha256'), 'mount tessellation tools', group=a.sources,
                  required=('hardware/printed-parts/cadlib/print_mesh.py',))
    a.map_matches(doc.get('producer_loaded_source_sha256'), 'mount producer loaded sources',
                  group=a.sources, required=('hardware/printed-parts/cold-core/_cold_core_interface.py',
                                            'hardware/printed-parts/cold-core/_foam_cap.py'))
    a.map_matches({doc.get('producer_receipt', ''): doc.get('producer_receipt_sha256')},
                  'mount producer receipt', group=a.evidence)
    if doc.get('status') != 'mesh-inputs-and-native-mouths-pass':
        a.error('fresh mount mesh/native-mouth manifest has no pass')
    rows = doc.get('parts', {})
    for stem, mesh in (('foam-cap-top', FOAM + '/foam-cap-top.stl'),
                       ('foam-cap-lid-top', LID_MESH)):
        row = rows.get(stem, {})
        step = FOAM + '/' + stem + '.step'
        if a.path(row.get('native_source', '')) != a.path(step):
            a.error(f'{stem}: manifest does not use the current canonical STEP')
        a.map_matches({step: row.get('native_source_sha256'), mesh: row.get('stl_sha256')},
                      stem + ' exact input pair', group=a.artifacts)
        if a.path(row.get('stl', '')) != a.path(mesh):
            a.error(f'{stem}: mesh path is not the assigned fresh print input')
        if not (row.get('watertight') is True and row.get('winding_consistent') is True
                and row.get('connected_bodies') == 1 and row.get('non_manifold_edges') == 0):
            a.error(f'{stem}: no one-closed-mesh qualification')
        if row.get('print_orientation', {}).get('native_up') != [0, 0, 1]:
            a.error(f'{stem}: fresh native +Z orientation declaration is missing')
    mouths = doc.get('native_support_mouths')
    if not isinstance(mouths, list) or not mouths or any(r.get('passed') is not True for r in mouths):
        a.error('mount native support mouths are missing or not passing')
    a.details['pump_mount_inputs'].update(lid_mesh_included=True,
        lid_print_staging_qualified=not a.issues, manifest=a.label(manifest),
        manifest_sha256=a.hash(manifest), native_support_mouths=mouths,
        actual_slice_support_paths_reviewed=False)


def inspect_functional_regions(a, path):
    doc = a.load(path)
    if not isinstance(doc, dict):
        return
    if doc.get('status') != 'current_native_regions_declared' or not doc.get('authority'):
        a.error('functional-region declaration lacks current explicit authority')
    a.map_matches(doc.get('source_sha256'), 'functional-region source', group=a.sources,
                  required=(CARRIER + '/tee_carrier.py', CARRIER + '/_simple_carrier.py'))
    a.map_matches(doc.get('input_sha256'), 'functional-region native/mesh inputs', group=a.artifacts,
                  required=(CARRIER_BASES[1] + '.step', CARRIER_BASES[1] + '.stl'))
    a.map_matches(doc.get('evidence_sha256'), 'functional-region native proof', group=a.evidence)
    for name in doc.get('evidence_sha256', {}):
        proof = a.load(name)
        if not isinstance(proof, dict):
            continue
        if proof.get('status') != 'pass' or not proof.get('checks') or any(r.get('pass') is not True for r in proof['checks']):
            a.error('functional-region native containment proof is absent or not passing')
        a.map_matches(proof.get('source_sha256'), 'functional-region proof sources', group=a.sources)
        a.map_matches(proof.get('input_sha256'), 'functional-region proof inputs', group=a.artifacts)
    regions = [r for r in doc.get('regions', []) if r.get('id') == 'carrier-retaining-wall']
    if len(regions) != 1:
        a.error('functional declaration must contain exactly one complete retaining-wall region')
    else:
        row = regions[0]
        a.map_matches({CARRIER_BASES[1] + '.step': row.get('source_step_sha256'),
                       CARRIER_BASES[1] + '.stl': row.get('source_stl_sha256')},
                      'declared retaining-wall exact input pair', group=a.artifacts)
    a.details['functional_regions'] = {'path': a.label(path), 'sha256': a.hash(path),
                                      'native_slice_toolpaths_reviewed': False}


def collect(args):
    root, work = args.root.resolve(), args.work.resolve()
    out = args.output_dir.resolve()
    if out.exists():
        raise ValueError('Output directory must be new; existing receipts are immutable: ' + str(out))
    a = Audit(root)
    a.remember(Path(__file__), a.evidence)
    complete = inspect_chain(a, work, args.published_payload_check)
    inspect_profile(a)
    for name in (*PART_ARTIFACTS, BOX, ASSEMBLY + '.step', ASSEMBLY + '.step.mesh'):
        a.remember(name, a.artifacts)
    card = a.load(ASSEMBLY + '.scorecard.json')
    a.load(ASSEMBLY + '.facts.json')
    if isinstance(card, dict):
        a.issues.extend(gate_errors(card))
        a.details['current_gates'] = card
    if complete:
        try:
            inspect_facts(a)
        except Exception as exc:
            a.error('facts-current reader failed: ' + repr(exc))
    inspect_pusher_export(a)
    inspect_mount_inputs(a, args.mount_mesh_manifest)
    if args.functional_regions:
        inspect_functional_regions(a, args.functional_regions)
    tree = ast.parse(a.path(ENC + '/enclosure.py').read_bytes())
    counts = [n.value.value for n in tree.body if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == 'flute_count' for t in n.targets)
              and isinstance(n.value, ast.Constant)]
    if counts != [262]:
        a.error(f'current frozen flute_count is {counts}, expected [262]')
    if args.front_top_check:
        a.verify_proof(args.front_top_check, role='pusher', full=True)
    else:
        if args.carrier_equality:
            a.verify_proof(args.carrier_equality, role='carrier')
        else:
            a.error('need a fresh native equality proof: canonical carrier exports versus full-gate CarrierSpec')
        if args.pusher_check:
            a.verify_proof(args.pusher_check, role='pusher')
        else:
            a.error('need a fresh canonical 2 mm pusher route proof; full assembly still uses a 0.6 mm witness')
    # A single beginning/end pair detects changes while the collector was reading.
    for name, expected in tuple(a.seen.items()):
        actual = a.hash(name)
        if actual != expected:
            a.error('input changed before receipt freeze: ' + name)
    for name in a.details.get('facts_current', {}).get('absent_declared_names', []):
        if a.path(name).exists():
            a.error('declared absent name appeared before receipt freeze: ' + name)
    status = 'current_geometry_confirmed' if not a.issues else 'geometry_receipt_incomplete'
    receipt = {'schema': 1, 'status': status, 'authority': args.authority,
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'print_released': False, 'submitted': False,
        'scope': 'Four complete enclosure shell quadrants, both production carrier halves, one canonical spring pusher; canonical G Ganen mount inputs with lid mesh inclusion stated separately.',
        'artifact_sha256': dict(sorted(a.artifacts.items())),
        'source_sha256': dict(sorted(a.sources.items())),
        'evidence_sha256': dict(sorted(a.evidence.items())),
        'input_sha256': dict(sorted(a.inputs.items())),
        'collector_sha256': digest(Path(__file__)), 'checks': a.details,
        'unresolved': a.issues,
        'release_limits': ['Offline staging input receipt only; exact native slicing and support-removal review remain required.',
            'No historic support approval or source-equivalence adapter is carried forward.',
            'Physical spring feel, retention, stiffness and cleanup effort remain complete-enclosure trial observations.'],
        'physical_trial_is_preprint_gate': False,
    }
    out.mkdir(parents=True)
    audit_path = out / 'receipt-audit.json'
    audit_path.write_text(json.dumps(receipt, indent=2) + '\n')
    if not a.issues:
        (out / 'current-geometry.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'status': status, 'audit': str(audit_path),
        'receipt': str(out / 'current-geometry.json') if not a.issues else None,
        'blocking_items': a.issues, 'counts': {k: len(receipt[k]) for k in
            ('artifact_sha256', 'source_sha256', 'evidence_sha256')}}, indent=2))
    return 0 if not a.issues else 2


def selftest():
    motion = {'id': 'tee-carrier-motion', 'kind': 'gate', 'active': True, 'status': 'pass'}
    assert not gate_errors({'gatesPass': True, 'checks': [motion]})
    assert gate_errors({'gatesPass': False, 'checks': [motion]})
    assert gate_errors({'gatesPass': True, 'checks': [{**motion, 'status': 'fail'}]})
    assert gate_errors({'gatesPass': True, 'checks': [{**motion, 'active': False}]})
    assert not gate_errors({'gatesPass': True, 'checks': [motion,
        {'id': 'unmeasured-physical-trial', 'kind': 'gate', 'active': False, 'status': 'warn'}]})
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder); p = root / 'native.step'; p.write_text('current bytes')
        a = Audit(root); a.map_matches({'native.step': digest(p)}, 'fresh input', required=('native.step',))
        assert not a.issues
        old = digest(p); p.write_text('changed bytes')
        a.map_matches({'native.step': old}, 'stale input')
        assert a.issues
        a = Audit(root); a.map_matches({'native.step': digest(p)}, 'missing paired STL', required=('native.stl',))
        assert a.issues
        a = Audit(root); a.map_matches({}, 'absent provenance')
        assert a.issues
    print('PASS synthetic checks: failing/inactive gates, stale bytes, missing paired inputs and empty provenance rejected; inactive physical trial allowed')
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--root', type=Path, default=ROOT_DEFAULT)
    p.add_argument('--work', type=Path, default=WORK_DEFAULT)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--authority', help='Coordinating-task handoff for the completed exact production inputs')
    p.add_argument('--front-top-check', type=Path, help='Fresh verify_current_front_top.py report; covers both bounded proofs')
    p.add_argument('--carrier-equality', type=Path)
    p.add_argument('--pusher-check', type=Path)
    p.add_argument('--mount-mesh-manifest', type=Path,
                   help='Fresh G mount native/mesh manifest; without it the lid mesh is not qualified for staging')
    p.add_argument('--functional-regions', type=Path,
                   help='Fresh complete right-carrier wall declaration and exact native/mesh stock evidence')
    p.add_argument('--published-payload-check', type=Path,
                   help='Exact pre/post publisher proof when normal publication replaces the assembly viewer surfaces')
    p.add_argument('--selftest', action='store_true')
    args = p.parse_args()
    if args.selftest:
        return selftest()
    if not args.output_dir or not args.authority:
        p.error('--output-dir and --authority are required; launch only after the completed output handoff')
    if args.front_top_check and (args.carrier_equality or args.pusher_check):
        p.error('choose the current full native proof OR the two bounded proofs')
    return collect(args)


if __name__ == '__main__':
    raise SystemExit(main())
