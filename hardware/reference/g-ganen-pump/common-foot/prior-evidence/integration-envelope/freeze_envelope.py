"""Hash the separate conservative integration envelope and its proofs."""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import sys

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
ROOT = REFERENCE.parents[2]
MANIFEST = HERE/'artifact-manifest.json'
sys.path.insert(0, str(REFERENCE))
from freeze_reference import check as check_reference


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_files():
    return {path.name: {'sha256': digest(path), 'bytes': path.stat().st_size}
            for path in sorted(HERE.iterdir()) if path.is_file() and path != MANIFEST
            and path.suffix in ('.py', '.md', '.json', '.png', '.step', '.mesh')}


def checks():
    check_reference()
    bound = json.loads((HERE/'containment.json').read_text())
    params = json.loads((HERE/'envelope-parameters.json').read_text())
    native = json.loads((HERE/'native-validation.json').read_text())
    costs = json.loads((HERE/'native-query-cost.json').read_text())
    component_cost = json.loads((HERE/'component-section-cost.json').read_text())
    for name, expected in bound['tool_sha256'].items():
        if digest(HERE/name) != expected:
            raise ValueError('Stale derivation tool: '+name)
    if bound['frozen_reference_manifest_sha256'] != digest(REFERENCE/'artifact-manifest.json'):
        raise ValueError('Frozen detailed reference changed')
    if bound['detailed_native_sha256'] != digest(REFERENCE/'g-ganen-pump.step'):
        raise ValueError('Detailed reference STEP changed')
    if params['containment_sha256'] != digest(HERE/'containment.json'):
        raise ValueError('Stale envelope parameters')
    for name, expected in native['input_sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('Stale native proof input: '+name)
    for name, expected in costs['tool_sha256'].items():
        if digest(HERE/name) != expected:
            raise ValueError('Stale benchmark tool: '+name)
    if costs['detailed_reference_costs_sha256'] != digest(REFERENCE/'native-query-cost.json'):
        raise ValueError('Benchmark detailed baseline changed')
    for name, expected in component_cost['input_sha256'].items():
        if digest(HERE/name) != expected:
            raise ValueError('Stale component-section input: '+name)
    if not component_cost['all_fragments_valid'] or not component_cost['empty_case_pass']:
        raise ValueError('Component-wise section helper is not qualified')
    if component_cost['maximum_bound_difference_mm'] > 1e-5:
        raise ValueError('Component-wise bounds differ from the standard native section')
    step = HERE/'g-ganen-integration-envelope.step'
    if native['native_sha256'] != digest(step) or costs['native_sha256'] != digest(step):
        raise ValueError('Native proof/benchmark STEP changed')
    if native['native_containment_sha256'] != digest(HERE/'containment.json'):
        raise ValueError('Native containment evidence changed')
    mesh = step.with_suffix('.step.mesh')
    if native['viewer_payload_sha256'] != digest(mesh):
        raise ValueError('Viewer payload changed')
    with mesh.open('rb') as stream:
        header = json.loads(stream.read(struct.unpack('<I', stream.read(4))[0]))
    if header.get('v') != 3 or header.get('src') != digest(step):
        raise ValueError('Viewer payload does not match native STEP')
    if not bound['native_containment_verified'] or not native['all_native_solids_valid']:
        raise ValueError('Native envelope is unqualified')
    excess = max(row['max_outward_surface_distance_mm'] for row in bound['components'])
    if excess > bound['surface_distance_bound_mm']+bound['geometry_tolerance_mm']:
        raise ValueError('Outward distance exceeds declared bound')
    return bound, native, costs, excess


def manifest():
    bound, native, costs, excess = checks()
    return {'schema': 1, 'status': 'separate_conservative_integration_envelope_frozen',
            'detailed_reference_changed': False, 'production_consumers_changed': False,
            'production_mount_and_route_qualified': False,
            'envelope_only_not_material_mass_or_strength': True,
            'frozen_detailed_manifest_sha256': digest(REFERENCE/'artifact-manifest.json'),
            'files': current_files(),
            'native_containment_verified': True, 'native_roundtrip_verified': True,
            'solids': native['solids'], 'faces': native['faces'],
            'detailed_faces': bound['source_faces'],
            'maximum_outward_distance_mm': excess,
            'geometry_tolerance_mm': bound['geometry_tolerance_mm'],
            'exact_components': [row['name'] for row in bound['components']
                                 if row['method'] == 'exact_frozen_native_copy'],
            'benchmarks': {row['operation']: row['status'] for row in costs['operations']},
            'component_section_bounds_verified': True,
            'limits': ['The outward bound is relative to the detailed native envelope; scanner absolute accuracy remains unqualified.',
                       'The four feet remain independently removable/sliding, at recorded observed poses.',
                       'Filled slots and rail-clip cavities do not qualify screw passage, clamping or replacement feet.',
                       'The measured port exterior does not qualify hose engagement or retention.',
                       'This is a conservative rigid-neighbor clearance model; a flagged contact can be checked against the detailed source.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        checks()
        saved = json.loads(MANIFEST.read_text())
        if saved['files'] != current_files():
            raise ValueError('Envelope manifest inventory or hashes changed')
        print('Detailed reference and conservative integration envelope hashes pass.')
    else:
        MANIFEST.write_text(json.dumps(manifest(), indent=2)+'\n')
        print(MANIFEST)
