"""Prepare and slice the isolated joint coupon for Mark2; no printer connection."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware').is_dir() and (p / 'tools').is_dir())
JOB_NAME = 'carrier-joint-coupon-black-z004-mark2-v1'
JOB = ROOT / '.cache' / 'prints' / ('2026-09-20-' + JOB_NAME)
PROFILE = ROOT / 'hardware/printed-parts/petgf.3mf'
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/faucet'))
import refresh_print_project as project_tools


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    checks = json.loads((HERE / 'checks.json').read_text())
    assert checks['status'] == 'coupon_geometry_pass' and not checks['errors']
    assert checks['generator_sha256'] == sha(HERE / 'joint_coupon.py')
    parts = tuple((f'joint-coupon-{name}', HERE / f'coupon-only-{name}.stl', 0.0)
                  for name in ('left', 'right', 'keeper'))
    for name, path, _angle in parts:
        assert checks['printed_meshes'][name.rsplit('-', 1)[1]]['sha256'] == sha(path)
    JOB.mkdir(parents=True, exist_ok=True)
    staged = JOB / (JOB_NAME + '-input.3mf')
    report = project_tools.refresh(
        PROFILE, staged, parts=parts, offsets=((-55.0, 0.0), (0.0, 0.0), (48.0, 0.0)),
        title='Carrier joint coupon black PET-GF Mark2 v1', z_trim=0.04)
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
    with (ready / 'bambu-cli.log').open('w') as log:
        sliced = subprocess.run(command, cwd=ready, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, 'OMP_NUM_THREADS': '1',
                                     'OPENBLAS_NUM_THREADS': '1'})
    if sliced.returncode:
        raise RuntimeError(f'Native slice failed: {ready / "bambu-cli.log"}')
    archive = ready / output_name
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        effective = json.loads(z.read(project_tools.SETTINGS_MEMBER))
        gcode = z.read('Metadata/plate_1.gcode')
        if 'Metadata/plate_1.gcode.md5' in z.namelist():
            assert z.read('Metadata/plate_1.gcode.md5').decode().strip().lower() == hashlib.md5(gcode).hexdigest()
    (ready / 'plate_1.gcode').write_bytes(gcode)
    trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gcode, re.M)]
    assert trims == [0.0, 0.02], trims
    with zipfile.ZipFile(PROFILE) as z:
        base = json.loads(z.read(project_tools.SETTINGS_MEMBER))
    preserved = [
        'layer_height', 'initial_layer_print_height', 'wall_loops', 'sparse_infill_density',
        'sparse_infill_pattern', 'filament_flow_ratio', 'nozzle_diameter', 'filament_colour',
        'enable_support', 'support_type', 'support_top_z_distance', 'support_interface_top_layers',
        'support_interface_spacing', 'support_interface_pattern', 'support_object_xy_distance',
        'curr_bed_type', 'enable_arc_fitting', 'filament_nozzle_map', 'filament_map',
    ]
    for key in preserved:
        assert effective[key] == base[key], (key, base[key], effective[key])
    intentional = {key: [base.get(key), settings.get(key)]
                   for key in set(base) | set(settings) if base.get(key) != settings.get(key)}
    assert set(intentional) == {'machine_start_gcode', 'printer_settings_id', 'extruder_ams_count'}
    result = json.loads((ready / 'result.json').read_text())
    assert result['return_code'] == 0
    plate, = result['sliced_plates']
    assert plate['warning_message'] == ''
    assert len(plate['objects']) == 3 and plate['obj_cached_cnt'] == 0
    assert plate['triangle_count'] == sum(row['triangles'] for row in report['parts'])
    support = project_tools.slice_review(staged, report, ready)
    record = {
        'status': 'native_slice_complete_toolpath_review_pending',
        'production_carrier_ready': False, 'coupon_only': True, 'submitted': False,
        'printer': 'Mark2', 'physical_filament': 'Black Polymaker PET-GF',
        'filament_metadata': effective['filament_type'],
        'requested_z_trim_mm': 0.04, 'actual_z_trim_commands_mm': trims,
        'source_profile': str(PROFILE.relative_to(ROOT)), 'source_profile_sha256': sha(PROFILE),
        'source_parts': report['parts'], 'geometry_checks_sha256': sha(HERE / 'checks.json'),
        'staged_input': str(staged.relative_to(ROOT)), 'staged_input_sha256': sha(staged),
        'native_archive': str(archive.relative_to(ROOT)), 'native_archive_sha256': sha(archive),
        'gcode_sha256': hashlib.sha256(gcode).hexdigest(),
        'process': {key: effective[key] for key in preserved},
        'intentional_settings_changed': sorted(intentional),
        'native_normalizations': {key: [settings.get(key), effective.get(key)]
                                  for key in set(settings) | set(effective)
                                  if settings.get(key) != effective.get(key)},
        'layers': int(re.search(rb'^; total layer number: (\d+)', gcode, re.M).group(1)),
        'estimated_seconds': plate['total_predication'],
        'estimated_filament_g': sum(row['total_used_g'] for row in plate['filaments']),
        'slicer_warning': plate['warning_message'], 'toolpath_fit': support['fit'],
        'support_audit': str(staged.with_suffix('.support-audit.json').relative_to(ROOT)),
        'support_audit_sha256': sha(staged.with_suffix('.support-audit.json')),
        'live_printer_mapping_and_empty_plate_still_required': True,
    }
    (HERE / 'print-readiness.json').write_text(json.dumps(record, indent=2) + '\n')
    (JOB / 'readiness.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({key: record[key] for key in ('status', 'native_archive', 'layers',
                                                 'estimated_seconds', 'estimated_filament_g')}, indent=2))


if __name__ == '__main__':
    main()
