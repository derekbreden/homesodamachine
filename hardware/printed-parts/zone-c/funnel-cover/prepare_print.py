"""Prepare an unsent native H2C PETG cover slice and retain its review receipt."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/funnel-mold-print/profiles.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/faucet'), str(ROOT / 'tools/funnel-mold-print')]
import refresh_print_project as writer
from profiles import system_preset
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/nameplate'))
from verify_mark2_print import segments
from shapely.geometry import LineString
from shapely.ops import unary_union

PROFILE = ROOT / 'hardware/printed-parts/petgf.3mf'
PRESETS = Path('/Applications/BambuStudio.app/Contents/Resources/profiles/BBL')
JOB = ROOT / '.cache/prints/funnel-cover-petg-native'


def main():
    JOB.mkdir(parents=True, exist_ok=True)
    project = HERE / 'funnel-cover-petg.3mf'
    report = writer.refresh(PROFILE, project,
                            parts=(('funnel-cover', HERE / 'funnel-cover-print.stl', 0.0),),
                            offsets=((0.0, 0.0),), title='Funnel cover - black PETG - unsent',
                            z_trim=0.18, plate_border=15.0)
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    preset_files = {}
    filament, _origins, ids = system_preset(PRESETS, 'filament', 'Bambu PETG Basic @BBL H2C', preset_files)
    settings.update(filament)
    settings.update(wall_loops='3', sparse_infill_density='100%',
                    sparse_infill_pattern='zig-zag', enable_support='0',
                    brim_type='no_brim', brim_width='0', layer_height='0.24',
                    initial_layer_print_height='0.2', enable_prime_tower='0',
                    filament_colour=['#000000'], filament_type=['PETG'],
                    filament_settings_id=['Bambu PETG Basic @BBL H2C'],
                    filament_ids=[ids['filament_id']], filament_nozzle_map=['0'],
                    filament_map=['1'], filament_map_2=['1'], filament_map_mode='Manual',
                    support_filament='1', support_interface_filament='1',
                    extruder_ams_count=['1#0|4#0', '1#0|4#0'], flush_into_support='0')
    # The material selector inherits the PETG preset rather than the exterior's spool.
    settings['inherits_group'][1] = 'Bambu PETG Basic @BBL H2C'
    overrides = {'wall_loops', 'sparse_infill_density', 'sparse_infill_pattern',
                 'enable_support', 'brim_type', 'brim_width', 'layer_height',
                 'initial_layer_print_height', 'enable_prime_tower'}
    settings['different_settings_to_system'][0] = ';'.join(sorted(
        set(settings['different_settings_to_system'][0].split(';')) | overrides))
    settings['print_settings_id'] = 'Funnel cover - solid PETG - 0.24 mm'
    members[writer.SETTINGS_MEMBER] = json.dumps(settings, indent=2).encode()
    writer.archive_write(project, members)
    command = ['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio',
               '--slice', '0', '--arrange', '0', '--orient', '0',
               '--outputdir', str(JOB), '--export-3mf', 'funnel-cover.gcode.3mf', str(project)]
    with (JOB / 'bambu-cli.log').open('w') as log:
        rc = subprocess.run(command, cwd=JOB, stdout=log, stderr=subprocess.STDOUT).returncode
    assert rc == 0, (rc, str(JOB / 'bambu-cli.log'))
    native = JOB / 'funnel-cover.gcode.3mf'
    with zipfile.ZipFile(native) as archive:
        assert archive.testzip() is None
        emitted = archive.read('Metadata/plate_1.gcode')
        assert hashlib.md5(emitted).hexdigest() == archive.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB / 'plate_1.gcode').write_bytes(emitted)
        effective = json.loads(archive.read(writer.SETTINGS_MEMBER))
        preview = archive.read('Metadata/plate_1.png')
    assert b'; FEATURE: Support' not in emitted
    roads = list(segments(JOB / 'plate_1.gcode'))
    assert {road['object'] for road in roads} == {1901}
    assert {road['tool'] for road in roads} == {0}
    assert not any(road['feature'].startswith('Support') for road in roads)
    layers = sorted({road['layer'] for road in roads})
    assert layers[:2] == [0.2, 0.44], layers[:2]
    footprints = [unary_union([LineString((road['a'], road['b'])).buffer(road['width'] / 2)
                               for road in roads if road['layer'] == layer]) for layer in layers[:2]]
    overlap = footprints[0].intersection(footprints[1]).area / footprints[1].area
    assert overlap > 0.95, overlap
    for key, value in {'wall_loops':'3', 'sparse_infill_density':'100%',
                       'enable_support':'0', 'filament_type':['PETG'],
                       'filament_nozzle_map':['0'], 'layer_height':'0.24',
                       'initial_layer_print_height':'0.2'}.items():
        assert effective[key] == value, (key, effective[key])
    result = json.loads((JOB / 'result.json').read_text())
    assert result['return_code'] == 0
    sliced, = result['sliced_plates']
    assert not sliced['warning_message'], sliced['warning_message']
    sources = [Path(__file__), HERE / 'funnel-cover-print.stl', HERE / 'funnel-cover-print.step', PROFILE]
    # Retain the final, material-correct project receipt beside the project.
    report.update(project_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),
                  source_mesh_sha256=hashlib.sha256((HERE / 'funnel-cover-print.stl').read_bytes()).hexdigest(),
                  material='Bambu PETG Basic Black', wall_loops=3, sparse_infill_percent=100,
                  filament_preset_sha256=preset_files)
    (HERE / 'funnel-cover-petg.print.json').write_text(json.dumps(report, indent=2) + '\n')
    report.update(project_sha256=hashlib.sha256(project.read_bytes()).hexdigest(),
                  source_sha256={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
                  stock_filament_preset_sha256=preset_files, native_archive=str(native.relative_to(ROOT)),
                  native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),
                  gcode_sha256=hashlib.sha256(emitted).hexdigest(), settings_verified=True,
                  process={'first_layer_mm':0.20, 'layer_mm':0.24, 'walls':3,
                           'infill_percent':100, 'supports':False, 'material':'Bambu PETG Basic Black'},
                  support_paths=0, estimated_seconds=sliced['total_predication'],
                  estimated_grams=sum(f['total_used_g'] for f in sliced['filaments']),
                  first_two_layer_heights_mm=layers[:2],
                  first_to_second_bead_footprint_overlap_fraction=overlap,
                  model_layers=len(layers), model_tools=[0],
                  submitted=False, physical_retention_and_drip_exclusion='Unqualified')
    (HERE / 'native-slice-review.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'native-slice-preview.png').write_bytes(preview)
    print(f'Native cover slice: no supports, solid PETG, {report["estimated_seconds"]} s; unsent.')


if __name__ == '__main__':
    main()
