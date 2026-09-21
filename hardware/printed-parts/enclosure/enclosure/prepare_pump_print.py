"""Prepare the scan-corrected cartridge and cap for a Mark2 dry-fit print.

Requires the dedicated cartridge generation/native-fit manifest to be current.
This produces a native slice and support reading; it never connects to a printer.
"""
import argparse
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
PROFILE = ROOT / 'hardware/printed-parts/petgf.3mf'
JOB_NAME = 'pump-cartridge-scan-corrected-black-z004-mark2-v1'
JOB = ROOT / '.cache/prints' / ('2026-09-20-' + JOB_NAME)
GEOMETRY = HERE / 'pump-cartridge-generation.json'
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet'))
import refresh_print_project as project_tools


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-slice', action='store_true',
                        help='Review an existing native slice only if its input digest is identical')
    args = parser.parse_args()
    geometry_sha = sha(GEOMETRY)
    rebuild = json.loads(GEOMETRY.read_text())
    assert rebuild['status'] == 'current_cartridge_only_native_checks_passed'
    assert rebuild['native']['checks_pass']
    assert not rebuild['assembly_current'] and not rebuild['production_enclosure_released']
    for group in ('source_sha256', 'input_sha256', 'artifact_sha256'):
        for relative, expected in rebuild[group].items():
            assert sha(ROOT / relative) == expected, f'Cartridge generation input/output changed: {relative}'
    parts = tuple((f'enclosure-{name}', HERE / f'enclosure-{name}.stl', angle)
                  for name, angle in (('pump-cartridge', 0.0), ('pump-cap', 180.0)))
    for _name, path, _angle in parts:
        for artifact in (path, path.with_suffix('.step')):
            relative = str(artifact.relative_to(ROOT))
            assert sha(artifact) == rebuild['artifact_sha256'][relative], relative

    JOB.mkdir(parents=True, exist_ok=True)
    staged = JOB / (JOB_NAME + '-input.3mf')
    old_input_sha = sha(staged) if staged.is_file() else None
    report = project_tools.refresh(
        PROFILE, staged, parts=parts, offsets=((0.0, 50.0), (0.0, -50.0)),
        title='Scan-corrected pump cartridge and cap, black PET-GF, Mark2', z_trim=0.04)
    with zipfile.ZipFile(staged) as z:
        members = {name: z.read(name) for name in z.namelist()}
    settings = json.loads(members[project_tools.SETTINGS_MEMBER])
    settings['extruder_ams_count'] = ['1#0|4#0', '1#0|4#0']
    members[project_tools.SETTINGS_MEMBER] = (json.dumps(settings, indent=2) + '\n').encode()
    project_tools.archive_write(staged, members)
    report['project_sha256'] = sha(staged)
    report['settings_sha256'] = hashlib.sha256(members[project_tools.SETTINGS_MEMBER]).hexdigest()
    staged.with_suffix('.print.json').write_text(json.dumps(report, indent=2) + '\n')
    ready = JOB / 'ready'
    ready.mkdir(exist_ok=True)
    output_name = JOB_NAME + '.gcode.3mf'
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
               '--slice', '0', '--arrange', '0', '--orient', '0',
               '--outputdir', str(ready), '--export-3mf', output_name, str(staged)]
    (JOB / 'slice-command.json').write_text(json.dumps(command, indent=2) + '\n')
    archive = ready / output_name
    if args.reuse_slice:
        assert old_input_sha == sha(staged), 'The existing slice input changed'
        assert archive.is_file()
        saved = json.loads((JOB / 'slice-input.json').read_text())
        assert saved == {'input_sha256': sha(staged), 'archive_sha256': sha(archive)}
    else:
        with (ready / 'bambu-cli.log').open('w') as log:
            run = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT,
                                 env={**os.environ, 'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1'})
        if run.returncode:
            raise RuntimeError(f'Native slice failed: {ready / "bambu-cli.log"}')
        (JOB / 'slice-input.json').write_text(json.dumps(
            {'input_sha256': sha(staged), 'archive_sha256': sha(archive)}, indent=2) + '\n')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        effective = json.loads(z.read(project_tools.SETTINGS_MEMBER))
        gcode = z.read('Metadata/plate_1.gcode')
        assert z.read('Metadata/plate_1.gcode.md5').decode().strip().lower() == hashlib.md5(gcode).hexdigest()
    (ready / 'plate_1.gcode').write_bytes(gcode)
    trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gcode, re.M)]
    assert trims == [0.0, 0.02], trims
    with zipfile.ZipFile(PROFILE) as z:
        base = json.loads(z.read(project_tools.SETTINGS_MEMBER))
    preserved = (
        'layer_height', 'initial_layer_print_height', 'wall_loops', 'sparse_infill_density',
        'sparse_infill_pattern', 'filament_flow_ratio', 'nozzle_diameter', 'filament_colour',
        'enable_support', 'support_type', 'support_top_z_distance', 'support_interface_top_layers',
        'support_interface_spacing', 'support_interface_pattern', 'support_object_xy_distance',
        'curr_bed_type', 'enable_arc_fitting', 'filament_nozzle_map', 'filament_map',
    )
    for key in preserved:
        assert effective[key] == base[key], (key, base[key], effective[key])
    intentional = {key: [base.get(key), settings.get(key)]
                   for key in set(base) | set(settings) if base.get(key) != settings.get(key)}
    assert set(intentional) == {'machine_start_gcode', 'printer_settings_id', 'extruder_ams_count'}
    normalizations = {key: [settings.get(key), effective.get(key)]
                      for key in set(settings) | set(effective)
                      if settings.get(key) != effective.get(key)}
    allowed = {'filament_prime_volume': [['30'], ['45']],
               'filament_map_2': [None, ['1']]}
    assert all(key in allowed and value == allowed[key]
               for key, value in normalizations.items()), normalizations
    result = json.loads((ready / 'result.json').read_text())
    assert result['return_code'] == 0
    plate, = result['sliced_plates']
    assert not plate['warning_message'] and len(plate['objects']) == 2
    assert plate['triangle_count'] == sum(row['triangles'] for row in report['parts'])
    support = project_tools.slice_review(staged, report, ready)
    assert sha(GEOMETRY) == geometry_sha
    for group in ('source_sha256', 'input_sha256', 'artifact_sha256'):
        for relative, expected in rebuild[group].items():
            assert sha(ROOT / relative) == expected, f'Cartridge changed during slicing: {relative}'
    record = {
        'status': 'native_slice_complete_toolpath_and_support_access_review_pending',
        'submitted': False, 'printer': 'Mark2',
        'purpose': 'Bench-fit the two corrected Kamoer wells and cap rails. Final four-tube operation requires the qualified collet/carrier assembly.',
        'assembly_current': False,
        'production_enclosure_released': False,
        'physical_filament': 'Black PET-GF, left external spool 254, PET-CF metadata',
        'requested_z_trim_mm': 0.04, 'actual_z_trim_commands_mm': trims,
        'source_profile': str(PROFILE.relative_to(ROOT)), 'source_profile_sha256': sha(PROFILE),
        'source_parts': report['parts'],
        'geometry_manifest': str(GEOMETRY.relative_to(ROOT)),
        'geometry_manifest_sha256': geometry_sha,
        'cartridge_source_sha256': rebuild['source_sha256'],
        'cartridge_input_sha256': rebuild['input_sha256'],
        'cartridge_artifact_sha256': rebuild['artifact_sha256'],
        'print_preparation_source_sha256': sha(Path(__file__)),
        'unqualified_tee_datums': rebuild['native']['unqualified_tee_datums'],
        'staged_input': str(staged.relative_to(ROOT)), 'staged_input_sha256': sha(staged),
        'native_archive': str(archive.relative_to(ROOT)), 'native_archive_sha256': sha(archive),
        'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
        'process': {key: effective[key] for key in preserved},
        'intentional_settings_changed': sorted(intentional),
        'native_normalizations': normalizations,
        'layers': int(re.search(rb'^; total layer number: (\d+)', gcode, re.M).group(1)),
        'estimated_seconds': plate['total_predication'],
        'estimated_filament_g': sum(row['total_used_g'] for row in plate['filaments']),
        'slicer_warning': plate['warning_message'], 'toolpath_fit': support['fit'],
        'support_audit': str(staged.with_suffix('.support-audit.json').relative_to(ROOT)),
        'support_audit_sha256': sha(staged.with_suffix('.support-audit.json')),
        'live_printer_mapping_and_empty_plate_still_required': True,
        'physical_fit_tested': False,
    }
    (HERE / 'pump-print-readiness.json').write_text(json.dumps(record, indent=2) + '\n')
    (JOB / 'readiness.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ('status', 'native_archive', 'layers',
                                                 'estimated_seconds', 'estimated_filament_g')}, indent=2))


if __name__ == '__main__':
    main()
