"""Verify the raised lettering and filament assignments in all three native slices."""
import hashlib
import json
import re
import sys
import zipfile
import prepare_print as prep

sys.path[:0] = [str(prep.ROOT/'hardware/scripts'), str(prep.HERE.parents[1]/'nameplate')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers


def main():
    job = prep.JOB
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    prepared = json.loads((job/'preparation.json').read_text())
    staged = next(job.glob('*-input.3mf'))
    native = next((job/'ready').glob('*.gcode.3mf'))
    assert sha(staged) == prepared['project_sha256']
    for p, digest in prepared['source_geometry_and_settings_sha256'].items():
        assert sha(prep.ROOT/p) == digest, p
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings = json.loads(z.read('Metadata/project_settings.config'))
        gc = z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (job/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    for k, v in {'enable_support':'0', 'initial_layer_print_height':'0.2', 'layer_height':'0.24',
                 'filament_nozzle_map':['0','1'], 'nozzle_diameter':['0.4','0.4'],
                 'wall_sequence':'inner wall/outer wall', 'is_infill_first':'0', 'infill_wall_overlap':'15%'}.items():
        assert settings[k] == v, (k, settings[k])
    trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gc, re.M)]
    assert trims == [0., .02]
    path = job/'ready/plate_1.gcode'
    path.write_bytes(gc)
    roads = list(segments(path))
    assert {r['object'] for r in roads} == {2901, 2902, 2903}
    assert not any(r['feature'].startswith('Support') for r in roads)
    readings = []
    for oid, station, letter_tool in ((2901, 'water', 0), (2902, 'flavor-a', 1), (2903, 'flavor-b', 1)):
        layers = wall_layers(native, oid)
        assert layers[0] == (.2, .2) and layers[-3:] == [(2., .12), (2.24, .24), (2.48, .24)]
        for height in (2.24, 2.48):
            raised = [r for r in roads if r['object'] == oid and r['layer'] == height and r['feature'] != 'Prime tower']
            assert len(raised) > 20 and {r['tool'] for r in raised} == {letter_tool}
            readings.append({'station':station, 'print_z_mm':height, 'letter_nozzle':letter_tool, 'extrusion_paths':len(raised)})
    result = json.loads((job/'ready/result.json').read_text())
    assert result['return_code'] == 0
    sliced, = result['sliced_plates']
    assert not sliced['warning_message']
    report = {'pass':True, 'native_archive':str(native.relative_to(prep.ROOT)), 'native_archive_sha256':sha(native),
              'gcode_sha256':hashlib.sha256(gc).hexdigest(), 'source_hashes_current':True,
              'support_paths':0, 'raised_letter_checks':readings, 'emitted_z_trim_mm':trims,
              'estimated_seconds':sliced['total_predication'],
              'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
              'submitted':False, 'calibration_applied':False, 'hold':prepared['hold']}
    (job/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('pass', 'support_paths', 'estimated_seconds')}))


if __name__ == '__main__':
    main()
