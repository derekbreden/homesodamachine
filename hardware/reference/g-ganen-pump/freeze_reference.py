"""Bind the standalone native reference to its measured inputs and checks.

This does not change production consumers, run the shared graph, or publish.
The native exporter must have completed before freezing. --check verifies the
retained evidence, report dependencies, native STEP and viewer payload hashes.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
MANIFEST = HERE/'artifact-manifest.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_files():
    paths = list(HERE.iterdir()) + list((HERE/'common-foot').rglob('*'))
    return {str(path.relative_to(HERE)): {'sha256': digest(path), 'bytes': path.stat().st_size}
            for path in sorted(set(paths)) if path.is_file() and path != MANIFEST
            and path.suffix in ('.py', '.md', '.json', '.png', '.step', '.mesh', '.txt')}


def unchanged_registration_algorithm(filename, expected):
    if filename != 'register_scan.py':
        return False
    proof = json.loads((HERE/'common-foot/cli-dispatch-equivalence.json').read_text())
    before = (HERE/proof['before_source']).read_bytes()
    after = (HERE/filename).read_bytes()
    old_line, new_line = proof['before_line'].encode(), proof['after_line'].encode()
    return (proof['status'] == 'pass' and expected == proof['before_sha256']
            and hashlib.sha256(before).hexdigest() == expected
            and hashlib.sha256(after).hexdigest() == proof['after_sha256']
            and before.count(old_line) == 1 and before.replace(old_line, new_line) == after)


def report_dependencies():
    checked = 0
    for name in ('scan-measurements.json', 'pass-02-registration.json', 'pass-03-registration.json',
                 'registered-measurements.json', 'casing-sections.json', 'interface-measurements.json',
                 'reference-parameters.json', 'native-validation.json'):
        report = json.loads((HERE/name).read_text())
        for group in ('input_sha256', 'tool_sha256', 'diagnostic_sha256', 'verified_parameter_input_digests'):
            for filename, expected in report.get(group, {}).items():
                if digest(HERE/filename) != expected and not unchanged_registration_algorithm(filename, expected):
                    raise ValueError(f'Stale {name} dependency: {filename}')
                checked += 1
    return checked


def manifest():
    verified_count = report_dependencies()
    validation = json.loads((HERE/'native-validation.json').read_text())
    if validation['reference_parameters_sha256'] != digest(HERE/'reference-parameters.json'):
        raise ValueError('Native validation is not bound to current parameters')
    if not validation['all_native_solids_valid'] or validation['production_mount_and_route_qualified']:
        raise ValueError('Unexpected qualification state')
    first = json.loads((HERE/'scan-measurements.json').read_text())
    measured = json.loads((HERE/'registered-measurements.json').read_text())
    for index, item in enumerate(measured['passes'], 1):
        retained = json.loads((HERE/f'pass-0{index}-reference-transform.json').read_text())
        if not np.allclose(item['native_to_reference'], retained, atol=1e-10):
            raise ValueError('Retained inspection transform is stale')
    for filename in ('pass-02-registration.json', 'pass-03-registration.json'):
        row = json.loads((HERE/filename).read_text())
        if not np.allclose(row['fixed_native_to_shared'], first['native_to_reference'], atol=1e-10):
            raise ValueError('Registration no longer uses the measured first-pass datum')
    native = HERE/'g-ganen-pump.step'
    mesh = HERE/'g-ganen-pump.step.mesh'
    if not native.is_file() or not mesh.is_file():
        raise ValueError('Export the native STEP and viewer payload before freezing')
    # Read the public payload header directly. Importing either exporter module
    # takes the shared build lock even for a read-only check.
    with mesh.open('rb') as stream:
        header_length = struct.unpack('<I', stream.read(4))[0]
        header = json.loads(stream.read(header_length))
    if header.get('v') != 3 or header.get('src') != digest(native):
        raise ValueError('Viewer payload is not bound to the current STEP bytes')
    imported = cq.importers.importStep(str(native)).val()
    solids = imported.Solids()
    if len(solids) != len(validation['native_solids']) or not all(shape.isValid() for shape in solids):
        raise ValueError('Exported native solid validity/count differs from validation')
    bounds = np.array([row['bounds_mm'] for row in validation['native_solids']])
    expected = np.array([bounds[:, 0].min(0), bounds[:, 1].max(0)])
    b = imported.BoundingBox()
    actual = np.array([[b.xmin, b.ymin, b.zmin], [b.xmax, b.ymax, b.zmax]])
    if not np.allclose(expected, actual, atol=1e-5):
        raise ValueError('Exported native bounds differ from validated solids')
    files = current_files()
    evidence = json.loads((HERE/'scan-evidence.json').read_text())
    return {'schema': 1, 'part': 'G Ganen B07F35PTFR diaphragm-pump external reference',
            'status': 'standalone_native_reference_frozen_with_explicit_interface_limits',
            'native_reference_valid': True, 'production_consumers_changed': False,
            'production_mount_and_route_qualified': False,
            'envelope_only_not_material_mass_or_strength': True,
            'files': files, 'report_dependency_hashes_verified': verified_count,
            'native_reimport': {'valid_solids': len(solids), 'bounds_mm': actual.tolist(),
                               'matches_validated_bounds': True, 'viewer_payload_matches_step': True},
            'native_sources': [{'path': row['fused_path'], 'sha256': row['fused_sha256'], 'points': row['points']}
                               for row in evidence['captures']],
            'source_scale_factor': 1.0,
            'remaining_physical_fit': ['Actual M3 screw passage through all four rubber slots.',
                                       'Selected washer flat seating and upstand clearance.',
                                       'Loaded rubber clamp stack, chosen slider positions and production mount/tube/wire integration.'],
            'limits': ['The identical nominal 7 mm feet describe visible purchased-part geometry; hidden clip retention and rubber compression are not qualified.',
                       'Rail face extent is observed; hidden clip geometry and hard travel limits are unqualified.',
                       'Lead transition regions are retained, while flexible wire routes and any distinct rigid strain-relief boundary remain unqualified.',
                       'Native scan residuals do not establish absolute scanner or sprayed-part dimensional tolerance.']}


def check():
    saved = json.loads(MANIFEST.read_text())
    report_dependencies()
    if set(current_files()) != set(saved['files']):
        raise ValueError('Reference manifest inventory is stale')
    for filename, expected in saved['files'].items():
        path = HERE/filename
        if expected != {'sha256': digest(path), 'bytes': path.stat().st_size}:
            raise ValueError('Reference artifact changed: '+filename)
    # Identical native bytes reuse the recorded successful native reimport.
    # Hash checking does not repeat a costly import/geometry query unnecessarily.
    if not saved['native_reimport']['matches_validated_bounds']:
        raise ValueError('Native reimport was not qualified')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        check()
        print('Reference hashes pass; identical STEP bytes retain the recorded native reimport proof.')
    else:
        current = manifest()
        MANIFEST.write_text(json.dumps(current, indent=2)+'\n')
        print(MANIFEST)
