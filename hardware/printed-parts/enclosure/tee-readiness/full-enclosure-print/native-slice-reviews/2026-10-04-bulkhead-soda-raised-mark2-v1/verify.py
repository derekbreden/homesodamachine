"""Verify the SODA ring's native slice: letters, layers, tools, trim and right-nozzle correction."""
import hashlib
import json
import re
import shutil
import sys
import zipfile

import prepare as prep

sys.path[:0] = [str(prep.ROOT/'hardware/scripts'), str(prep.ROOT/'hardware/printed-parts/enclosure/nameplate'),
                str(prep.ROOT/'hardware/printed-parts/calibration/dual-nozzle-registration')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from verify_correction import verify as verify_registration

LETTER_TOOL, BODY_TOOL = 0, 1


def main():
    job = prep.JOB
    sha = prep.sha
    prepared = json.loads((job/'preparation.json').read_text())
    staged = job/(prep.STEM+'-input.3mf')
    native = job/'ready'/(prep.STEM+'.gcode.3mf')
    assert sha(staged) == prepared['project_sha256']
    for p, digest in prepared['settings_and_script_sha256'].items():
        assert sha(prep.ROOT/p) == digest, p
    for label, part in prepared['geometry_snapshot']['parts'].items():
        assert sha(prep.GEOMETRY/f'soda-{label}.stl') == part['stl_sha256'], label
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings = json.loads(z.read('Metadata/project_settings.config'))
        gc = z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        slice_info = z.read('Metadata/slice_info.config').decode()
        (job/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    for k, v in {'enable_support': '0', 'initial_layer_print_height': '0.2', 'layer_height': '0.24',
                 'filament_nozzle_map': ['0', '1'], 'filament_map': ['1', '2'], 'nozzle_diameter': ['0.4', '0.4'],
                 'filament_colour': prep.COLOURS, 'filament_type': ['PET-CF', 'PET-CF'],
                 'curr_bed_type': 'Textured PEI Plate',
                 'wall_sequence': 'inner wall/outer wall', 'is_infill_first': '0', 'infill_wall_overlap': '15%'}.items():
        assert settings[k] == v, (k, settings[k])
    filaments = re.findall(r'<filament id="(\d)"[^>]*type="([^"]+)" color="(#[0-9A-F]{6})"', slice_info)
    assert filaments == [('1', 'PET-CF', '#FFFFFF'), ('2', 'PET-CF', '#46A8F9')], filaments
    trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gc, re.M)]
    assert trims == [0., .02], trims
    path = job/'ready/plate_1.gcode'
    path.write_bytes(gc)
    roads = list(segments(path))
    assert {r['object'] for r in roads} == {2901}
    assert not any(r['feature'].startswith('Support') for r in roads)
    assert prepared['calibration_applied'] and prepared['right_nozzle_correction_mm'] == {'X': -.5, 'Y': .7}
    assert settings['extruder_offset'] == prepared['native_extruder_offset'] == ['0x0', '0.5x-0.7']
    nominal = job/'uncorrected/ready'/(prep.STEM+'-uncorrected.gcode.3mf')
    registration = verify_registration(nominal, native, prepared['right_nozzle_correction_mm'])
    registration['physical_alignment'] = ('Right-nozzle correction measured with the registration coupon and accepted on '
                                          'the nameplate and the TAP/FLAVOR rings; this ring awaits its own finish check.')
    (job/'registration-verification.json').write_text(json.dumps(registration, indent=2)+'\n')
    layers = wall_layers(native, 2901)
    assert layers[0] == (.2, .2) and layers[-3:] == [(2., .12), (2.24, .24), (2.48, .24)], layers
    model = [r for r in roads if r['feature'] != 'Prime tower']
    assert {r['tool'] for r in model if r['layer'] <= 1.} == {BODY_TOOL}
    assert {r['tool'] for r in model} == {LETTER_TOOL, BODY_TOOL}
    readings = []
    for height in (2.24, 2.48):
        raised = [r for r in model if r['layer'] == height]
        assert len(raised) > 20 and {r['tool'] for r in raised} == {LETTER_TOOL}
        readings.append({'print_z_mm': height, 'letter_nozzle': 'left', 'extrusion_paths': len(raised)})
    result = json.loads((job/'ready/result.json').read_text())
    assert result['return_code'] == 0
    sliced, = result['sliced_plates']
    assert not sliced['warning_message']
    send = job/'send'
    send.mkdir(exist_ok=True)
    copy = send/native.name
    if not copy.exists():
        shutil.copy2(native, copy)
    assert sha(copy) == sha(native)
    report = {'pass': True, 'native_archive': str(native.relative_to(prep.ROOT)), 'native_archive_sha256': sha(native),
              'gcode_sha256': hashlib.sha256(gc).hexdigest(), 'staged_input_sha256': sha(staged),
              'geometry_snapshot_head': prepared['geometry_snapshot']['head'],
              'filaments': {'1': 'white PET-GF, left nozzle, external 254: lettering',
                            '2': 'blue PET-GF, right nozzle, external 255: body'},
              'support_paths': 0, 'layers': {'first': layers[0], 'last_three': layers[-3:]},
              'raised_letter_checks': readings, 'emitted_z_trim_mm': trims,
              'estimated_seconds': sliced['total_predication'],
              'estimated_grams_saved_profile_density': sum(f['total_used_g'] for f in sliced['filaments']),
              'submitted': False, 'calibration_applied': True,
              'right_nozzle_correction_mm': prepared['right_nozzle_correction_mm'],
              'maximum_normalized_registration_path_error_mm': registration['maximum_normalized_path_error_mm'],
              'send_copy': str(copy.relative_to(prep.ROOT))}
    (job/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ('pass', 'support_paths', 'estimated_seconds',
                                             'estimated_grams_saved_profile_density', 'layers',
                                             'maximum_normalized_registration_path_error_mm')}, indent=1))


if __name__ == '__main__':
    main()
