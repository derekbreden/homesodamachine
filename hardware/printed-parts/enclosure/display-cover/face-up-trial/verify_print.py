"""Check the cover's bed-connected wings and the receiver's native tree support."""
import hashlib
import json
import re
import sys
import zipfile
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
import prepare_print as prep

sys.path[:0] = [str(prep.ROOT/'hardware/scripts'), str(prep.HERE.parents[1]/'nameplate')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from enclosure_support_audit import audit


def main():
    job = prep.JOB
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    prepared = json.loads((job/'preparation.json').read_text())
    staged, native = next(job.glob('*-input.3mf')), next((job/'ready').glob('*.gcode.3mf'))
    assert sha(staged) == prepared['project_sha256']
    for p, digest in prepared['source_geometry_and_settings_sha256'].items():
        assert sha(prep.ROOT/p) == digest, p
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings = json.loads(z.read('Metadata/project_settings.config'))
        gc = z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (job/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    with zipfile.ZipFile(prep.ROOT/'hardware/printed-parts/petgf.3mf') as z:
        shared = json.loads(z.read('Metadata/project_settings.config'))
    support_keys = [k for k in shared if k.startswith(('support_', 'tree_support_')) or k in ('enable_support', 'independent_support_layer_height')]
    diff = {k:{'profile':shared[k], 'job':settings[k]} for k in support_keys if settings[k] != shared[k]}
    assert set(diff) == {'support_filament', 'support_interface_filament'}
    for k, v in {'initial_layer_print_height':'0.2', 'layer_height':'0.24', 'filament_nozzle_map':['0'],
                 'filament_colour':['#000000'], 'nozzle_diameter':['0.4','0.4'], 'support_type':'tree(auto)',
                 'wall_sequence':'inner wall/outer wall', 'is_infill_first':'0', 'infill_wall_overlap':'15%'}.items():
        assert settings[k] == v, (k, settings[k])
    trims = [float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)', gc, re.M)]
    assert trims == [0., .16]
    path = job/'ready/plate_1.gcode'
    path.write_bytes(gc)
    roads = list(segments(path))
    assert {r['object'] for r in roads} == {1901, 1902} and {r['tool'] for r in roads} == {0}
    cover = [r for r in roads if r['object'] == 1901]
    assert not any(r['feature'].startswith('Support') for r in cover)
    layers = wall_layers(native, 1901)
    assert layers[:2] == [(.2, .2), (.48, .28)] and layers[-1] == (3.84, .24)
    assert (1.44, .24) in layers and (1.68, .24) in layers
    wing_checks = []
    for height in (.2, .48, 1.44, 1.68):
        shape = unary_union([LineString((r['a'], r['b'])).buffer(r['width']/2) for r in cover if r['layer'] == height])
        span = prep.trial.cover.cover_x/2+prep.trial.WING_REACH/2
        covered = [shape.covers(Point(x, 230)) for x in (162.5-span, 162.5+span)]
        assert covered == ([True, True] if height <= 1.44 else [False, False]), (height, covered)
        wing_checks.append({'z_mm':height, 'both_wing_midpoints_covered':covered})
    receiver_layers = wall_layers(native, 1902)
    assert receiver_layers[0] == (.2, .2) and all(abs(h-.24) < 1e-5 for z, h in receiver_layers[1:])
    print('Toolpath and profile checks passed; reading tree connectivity.', flush=True)
    support = audit(path, 'display-face-up-receiver', profile=staged, include_unlabelled_support=True)
    support['physical_removal_tested'] = False
    support['removal_access'] = 'Remove trees through the open front and rear before installing glass or cover. The straight wing pockets open inward into the empty display mouth; their 2.64 mm opening has no cover hook obstructing the removal lane.'
    (job/'support-audit.json').write_text(json.dumps(support, indent=2)+'\n')
    result = json.loads((job/'ready/result.json').read_text())
    assert result['return_code'] == 0
    sliced, = result['sliced_plates']
    assert not sliced['warning_message']
    report = {'pass':True, 'native_archive':str(native.relative_to(prep.ROOT)), 'native_archive_sha256':sha(native),
              'gcode_sha256':hashlib.sha256(gc).hexdigest(), 'source_hashes_current':True,
              'cover_support_paths':0, 'cover_layers':layers, 'wing_checks':wing_checks,
              'receiver_layers':len(receiver_layers), 'receiver_support_profile_differences':diff,
              'support_summary':support['summary'], 'emitted_z_trim_mm':trims,
              'estimated_seconds':sliced['total_predication'],
              'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
              'submitted':False, 'physical_fit_and_support_removal':'Pending physical trial.'}
    (job/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('pass', 'cover_support_paths', 'estimated_seconds')}))


if __name__ == '__main__':
    main()
