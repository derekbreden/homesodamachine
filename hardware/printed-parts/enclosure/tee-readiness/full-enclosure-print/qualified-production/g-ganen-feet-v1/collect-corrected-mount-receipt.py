"""Bind the corrected pump mounting parts to the completed producer chain."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, shutil

ROOT = Path('/Users/derekbredensteiner/Developer/homesodamachine')
WORK = Path(__file__).resolve().parent
OUT = ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/qualified-production/g-ganen-feet-v1'
PHASES = ('foam_cap', 'flute_payload_cold_core', 'foam_assembly', 'cold_core_assembly',
          'enclosure_box', 'enclosure', 'tee_carrier', 'flute_payload_enclosure', 'enclosure_assembly')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def label(path):
    return str(Path(path).resolve().relative_to(ROOT))

def read(path):
    return json.loads(Path(path).read_text())

def bind(mapping, path):
    mapping[label(path)] = sha(path)

def main():
    if OUT.exists():
        raise SystemExit('Receipt is immutable; choose a fresh output directory')
    sources, artifacts, evidence, records = {}, {}, {}, []
    for name in PHASES:
        path = WORK/'generation'/(name+'.generation.json')
        row = read(path)
        assert row['raised'] is None and not row['loaded_source_drift'], name
        for rel, digest in row['loaded_source_sha256'].items():
            assert sha(ROOT/rel) == digest, ('source drift', name, rel)
            sources[rel] = digest
        records.append(path)
    scorecard = read(ROOT/'hardware/manifold-layout/enclosure-assembly.scorecard.json')
    assert scorecard['gatesPass'] is True
    assert all(row['status'] == 'pass' or row.get('active') is False for row in scorecard['checks']), 'Unresolved current assembly check'
    mount_input = ROOT/'.cache/prints/2026-09-21-g-ganen-foam-cap-lid-top-mark2-v2/inputs/print-inputs.json'
    inputs = read(mount_input)
    assert inputs['status'] == 'mesh-inputs-and-native-mouths-pass'
    for row in inputs['parts'].values():
        for path_key, hash_key in (('native_source', 'native_source_sha256'), ('stl', 'stl_sha256')):
            path = ROOT/row[path_key]
            assert sha(path) == row[hash_key], path
            bind(artifacts, path)
    for rel in (
        'hardware/printed-parts/petgf.3mf',
        'hardware/manifold-layout/enclosure-box.json',
        'hardware/manifold-layout/enclosure-assembly.step',
        'hardware/manifold-layout/enclosure-assembly.facts.json',
        'hardware/manifold-layout/enclosure-assembly.scorecard.json',
        'hardware/reference/g-ganen-pump/g-ganen-pump.step',
        'hardware/reference/g-ganen-pump/integration-envelope/g-ganen-integration-envelope.step',
        'hardware/printed-parts/cold-core/foam-assembly/foam-assembly.step',
        'hardware/cold-core-layout/cold-core-assembly.step',
    ):
        bind(artifacts, ROOT/rel)
    previous = read(WORK/'before.json')['files']
    unchanged, equivalent = {}, {}
    for rel, row in previous.items():
        if rel.endswith('.stl') and '/enclosure/' in rel:
            actual = sha(ROOT/rel)
            if actual != row['sha256']:
                assert rel.endswith('/enclosure-back-top.stl'), ('independent print mesh changed', rel)
                proof_path = ROOT/'hardware/reference/g-ganen-pump/installation/feet-correction-validation/back-top-equivalence/validation.json'
                proof = read(proof_path)
                assert proof['status'] == 'pass'
                assert proof['old_stl_sha256'] == row['sha256']
                assert proof['new_stl_sha256'] == actual
                step_rel = rel.removesuffix('.stl') + '.step'
                assert proof['new_step_sha256'] == sha(ROOT/step_rel)
                assert proof['added_mm3'] == 0 and proof['removed_mm3'] == 0
                assert proof['max_corresponding_corner_distance_mm'] < 0.0001
                equivalent[rel] = {'prior_sha256': row['sha256'], 'current_sha256': actual,
                                   'evidence': label(proof_path), 'evidence_sha256': sha(proof_path)}
            else:
                unchanged[rel] = actual
            artifacts[rel] = actual
    for job in read(ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/queue.json')['queued_jobs']:
        if job['id'].startswith('foam-cap-'):
            continue
        for part in read(ROOT/job['config'])['parts']:
            for key in ('stl', 'step'):
                bind(artifacts, ROOT/part[key])
    OUT.mkdir(parents=True)
    for path in records:
        target = OUT/'generation'/path.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(path, target)
        bind(evidence, target)
    for path in (mount_input, WORK/'installed-mount-check.json'):
        target = OUT/path.name
        shutil.copy2(path, target)
        bind(evidence, target)
    # These retain the original native checks and document only metadata changes.
    durable = ROOT/'hardware/reference/g-ganen-pump/installation/feet-correction-validation'
    assert durable.is_dir(), durable
    for path in sorted(durable.rglob('*')):
        if path.is_file() and path.suffix in ('.json', '.md', '.py', '.txt'):
            bind(evidence, path)
    for rel in (
        'hardware/reference/g-ganen-pump/common-foot/native-update.json',
        'hardware/reference/g-ganen-pump/common-foot/measurement-review.json',
        'hardware/reference/g-ganen-pump/native-validation.json',
        'hardware/reference/g-ganen-pump/integration-envelope/native-validation.json',
    ):
        bind(evidence, ROOT/rel)
    copied = OUT/'collect-corrected-mount-receipt.py'
    shutil.copy2(__file__, copied)
    bind(evidence, copied)
    receipt = {
        'schema': 1, 'status': 'current_geometry_confirmed',
        'authority': 'Coordinating task: completed corrected-foot production chain, native mounting and whole-pump/route clearance checks',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'print_released': False, 'submitted': False,
        'scope': 'Matching foam-cap-top and foam-cap-lid-top for four identical 7 mm G Ganen feet at the fully engaged rail ends. Unchanged shell/carrier print geometry retains its existing exact slice reviews; back-top numerical mesh variation has a separate native-equivalence proof.',
        'artifact_sha256': dict(sorted(artifacts.items())),
        'source_sha256': dict(sorted(sources.items())),
        'evidence_sha256': dict(sorted(evidence.items())),
        'unchanged_independent_print_mesh_sha256': unchanged,
        'native_equal_print_meshes': equivalent,
        'assembly_checks': {'total': len(scorecard['checks']),
                            'pass': sum(row['status'] == 'pass' for row in scorecard['checks']),
                            'inactive': [row['id'] for row in scorecard['checks'] if row.get('active') is False]},
        'installed_geometry': {
            'identical_foot_count': 4, 'nominal_pad_thickness_mm': 7,
            'slot_stations_along_rail_mm': [9.5, 67.5], 'fore_aft_span_mm': 58,
            'screw_offset_outward_in_slot_mm': 1.5,
            'pump_translation_delta_world_mm': [0, -1, 0],
            'travel_scope': 'Outermost positions with the entire visible 18 mm clip on the rail; not a claim about hard stops or retained partial overhang.',
        },
        'release_limits': ['This binds geometry for offline slicing. Each exact archive still needs native/support review and normal printer handoff.',
                           'Actual screw/washer fit, rubber compression and hose retention remain observations in the complete enclosure trial.'],
    }
    for mapping in (sources, artifacts, evidence):
        for rel, digest in mapping.items():
            assert sha(ROOT/rel) == digest, ('input changed during receipt', rel)
    (OUT/'current-geometry.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'path': label(OUT/'current-geometry.json'), 'sha256': sha(OUT/'current-geometry.json'),
                      'counts': {name: len(receipt[name]) for name in ('artifact_sha256','source_sha256','evidence_sha256')}}))

if __name__ == '__main__':
    main()
