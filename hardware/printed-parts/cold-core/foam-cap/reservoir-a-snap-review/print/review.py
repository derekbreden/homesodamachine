"""Manual emitted-path reading for the fore paired snap's two offline jobs.

This reads existing projects and slices. It does not slice, import CAD, launch a
printer or join a build/check path. Analysis boxes below sample emitted beads;
they are not additional modifiers in the print project.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import sys
import zipfile

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
PREP = ROOT / 'hardware/printed-parts/enclosure/trial-preparation'
COLD = ROOT / 'hardware/printed-parts/cold-core'
sys.path[:0] = [str(PREP), str(COLD)]
import _reservoir_a_snap as snap

loader = importlib.util.spec_from_file_location('fore_snap_native_print_reader', PREP / 'review.py')
reader = importlib.util.module_from_spec(loader)
loader.loader.exec_module(reader)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def identity(path):
    path = Path(path).resolve()
    return dict(path=str(path.relative_to(ROOT)), sha256=sha(path))


def read_job(directory):
    preparation = json.loads((directory / 'preparation.json').read_text())
    review = json.loads((directory / 'review.json').read_text())
    audit = json.loads((directory / 'support-audit-1901.json').read_text())
    project = ROOT / preparation['project']
    archive = ROOT / preparation['archive']
    with zipfile.ZipFile(archive) as source:
        settings = json.loads(source.read('Metadata/project_settings.config'))
    part = preparation['objects'][0]
    files = [directory / 'preparation.json', directory / 'review.json',
             directory / 'support-audit-1901.json', project, archive,
             ROOT / part['stl'], (ROOT / part['stl']).with_suffix('.step')]
    current = (sha(ROOT / part['stl']) == part['stl_sha256']
               and sha((ROOT / part['stl']).with_suffix('.step')) == part['step_sha256']
               and sha(project) == preparation['project_sha256']
               and sha(archive) == preparation['archive_sha256'] == review['archive_sha256'])
    result = dict(piece=preparation['piece'], files=[identity(path) for path in files],
                  current_native_and_archive_identity=current, existing_review_pass=review['pass'],
                  printer=preparation['printer'], nozzle=preparation['nozzle'],
                  material=preparation['material'], pose=part['pose'],
                  pose_rotation=part['pose_rotation'], source_center_mm=part['source_center_mm'],
                  plate_bounds_mm=part['plate_bounds_mm'],
                  minimum_full_bead_margin_mm=review['minimum_bed_margin_mm'],
                  support_summary=audit['summary'],
                  model_and_support_estimate_seconds=preparation['estimated_seconds'],
                  process={key: settings.get(key) for key in
                           ('wall_loops', 'wall_generator', 'sparse_infill_density',
                            'sparse_infill_pattern', 'enable_support', 'support_type',
                            'support_style', 'layer_height', 'initial_layer_print_height')},
                  existing_checks=review['checks'])
    return preparation, review, audit, archive, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cap', type=Path, required=True)
    parser.add_argument('--lid', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=HERE / 'review.json')
    args = parser.parse_args()
    cap, _cap_review, _cap_audit, cap_archive, cap_result = read_job(args.cap.resolve())
    lid, lid_review, lid_audit, _lid_archive, lid_result = read_job(args.lid.resolve())
    spec = snap.specification()
    part = cap['objects'][0]
    wo, wi = spec['wing_outer_x_mm'], spec['wing_inner_x_mm']
    hook, bottom, lip = spec['hook_inner_x_mm'], spec['hook_bottom_z_mm'], spec['hook_top_z_mm']
    root, roof = spec['spring_root_z_mm'], spec['outer_arch_rise_mm']
    half = spec['cap_length_mm']/2
    boxes = [('Whole cap', [-wo, -half, bottom], [wo, half, root+roof]),
             ('West spring leaf', [-wo, -half, lip+.4], [-wi, half, root-.4]),
             ('East spring leaf', [wi, -half, lip+.4], [wo, half, root-.4]),
             ('West integral hook', [-wo, -half, bottom+.05], [-hook, half, lip-.05]),
             ('East integral hook', [hook, -half, bottom+.05], [wo, half, lip-.05]),
             ('Fixed cap roof', [-wo, -half, root], [wo, half, root+roof])]
    analysis = copy.deepcopy(cap)
    selected = analysis['objects'][0]
    selected['modifiers'] = []
    for name, low, high in boxes:
        points = np.array(list(itertools.product(*zip(low, high))))
        placed = ((points-part['source_center_mm']) @ np.array(part['build_rotation']).T
                  + part['translation_mm'])
        selected['modifiers'].append(dict(name=name,
            plate_bounds_mm=[placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]))
    coverage = reader.dense_regions(args.cap.resolve(), analysis, cap_archive)
    cap_result['sampled_model_bead_coverage'] = coverage
    cap_result['coverage_scope'] = ('Three emitted layers along the six-millimetre extrusion, '
        'using the existing native reader. Each named section must have at least 90% '
        'model-bead area coverage. This is a deposition reading, not strength qualification.')

    current_regions = COLD / 'foam-cap/fore-snap-print-regions.json'
    frozen_regions = args.lid.resolve() / 'region-input-at-preparation.json'
    current, frozen = (json.loads(path.read_text()) for path in (current_regions, frozen_regions))
    same_region = (current['pieces'] == frozen['pieces']
                   and current['native_artifact_sha256'] == frozen['native_artifact_sha256']
                   and sha(frozen_regions) == lid['objects'][0]['regions']['record_sha256'])
    lid_result['region_inputs'] = dict(current=identity(current_regions),
        frozen_at_preparation=identity(frozen_regions), same_modifier_and_native_geometry=same_region)
    lid_result['receiver_root_deposition'] = lid_review['solid_host_deposition']
    source = current['pieces']['foam-cap-lid-top'][0]['applied_source_bounds_mm']
    local = [source[i] for i in (0, 2, 4, 1, 3, 5)]
    def intersects(bounds):
        return all(min(bounds[i+3], local[i+3])-max(bounds[i], local[i]) > 1e-6
                   for i in range(3))
    nearby = [row for row in lid_audit['interfaces'] if intersects(row['bbox_cad_xyz_mm'])]
    lid_result['receiver_support_interfaces'] = nearby
    lid_result['catch_underside_strategy'] = (
        'Keep the lid-up pose and Tree(auto)/Default support decisions. The emitted interface '
        'boxes do not meet the fore receiver/root region. The short fixed ledges print with '
        'the model, and the cap retains its 0.40 mm catch-underside allowance. The receiver '
        'is open at the top and both flanks for inspection and cleanup before tube/cap assembly. '
        'No manual support override or claim about printed surface finish is added.')
    cap_settings = cap_result['process']
    checks = dict(
        cap_current_identity=cap_result['current_native_and_archive_identity'],
        lid_current_identity=lid_result['current_native_and_archive_identity'],
        existing_cap_review=cap_result['existing_review_pass'],
        existing_lid_review=lid_result['existing_review_pass'],
        cap_three_loops_and_solid_recipe=(cap_settings['wall_loops'] == '3'
            and cap_settings['wall_generator'] == 'classic'
            and cap_settings['sparse_infill_density'] == '100%'
            and cap_settings['sparse_infill_pattern'] == 'zig-zag'),
        cap_section_in_bed_plane=np.allclose(np.array(part['pose_rotation']) @ [0., 1., 0.],
                                            [0., 0., 1.]),
        cap_no_support=cap_result['support_summary']['support_bodies'] == 0,
        cap_emitted_solid_sections=all(row['minimum_coverage'] is not None
            and len(row['samples']) == 3 and row['minimum_coverage'] >= .9 for row in coverage),
        lid_unchanged_native_and_region=same_region,
        lid_dense_receiver_root=bool(lid_result['receiver_root_deposition'])
            and all(row['minimum_coverage'] is not None and row['minimum_coverage'] >= .9
                    for row in lid_result['receiver_root_deposition']),
        no_fore_receiver_support_interface=not nearby)
    result = dict(scope='Current offline manufacturing inputs and emitted paths for one '
                  'fore paired snap cap and its integral lid receiver. No printer launch, '
                  'physical fit, release, retention, load or lifetime acceptance.',
                  source_files=[identity(Path(__file__)), identity(PREP / 'review.py'),
                                identity(PREP / 'prepare.py'), identity(Path(snap.__file__))],
                  cap=cap_result, lid=lid_result, checks=checks, status='pass' if all(checks.values()) else 'fail')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(status=result['status'], checks=checks,
        cap_minimum_bead_coverage=min(row['minimum_coverage'] or 0. for row in coverage),
        receiver_support_interfaces=len(nearby), output=str(args.out)), indent=2))
    return 0 if result['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
