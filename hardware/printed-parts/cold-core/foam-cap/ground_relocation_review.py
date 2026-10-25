"""Manual local reading of the deferred core-lid ground landing.

Run through tmp/takeover/cadq after the lid export. Only the moved bond stack,
its printed boss and one nominal M3 driver column are subjects. Existing
paired-anchor stock readings are retained at their original artifact scope.
No build, hook or recurring check invokes this reader.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
HW = ROOT/'hardware'
sys.path[:0] = [str(HW/p) for p in (
    'manifold-layout', 'scripts', 'printed-parts/cold-core', 'printed-parts/cadlib')]
import above_core as layout
import above_core_wiring as wiring
import _reservoir_a_anchors as anchors
import fits
from reservoir_a_anchor_review import bounds, signature, volume, nearby, contact

OUT = ROOT/'tmp/reservoir-a-ground-native'
REPORT = HERE/'ground-relocation-review.json'
ATTACHED = {'wire-AC6-PE', 'wire-PE-bus', 'wire-PE-carbonator', 'wire-J2-COM'}
LOOSE = {'va-east-turn', 'tube-above-core-va-fore-feed',
         'tube-above-core-va-under-head', 'lower-pump-elbow'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_j13_bounds(manifest, subjects):
    result = {}
    for row in manifest['routes']:
        if not row['id'].startswith('J13-'):
            continue
        radius = manifest['stock'][row['stock']]['od_mm']/2
        segment_boxes = []
        for segment in row['segments']:
            if segment['kind'] == 'line':
                points = [segment['start_mm'], segment['end_mm']]
                pad = radius
            elif segment['kind'] == 'arc':
                # Every point on a circle is within two radii of its start.
                points = [segment['start_mm']]
                pad = radius+2*segment['radius_mm']
            else:
                raise ValueError('Unsupported J13 source segment: '+segment['kind'])
            segment_boxes.append([min(p[i] for p in points)-pad for i in range(3)]
                                 +[max(p[i] for p in points)+pad for i in range(3)])
        overlaps = []
        for name, subject in subjects.items():
            b = bounds(subject)
            overlaps.extend({'subject': name, 'segment': i} for i, a in enumerate(segment_boxes)
                            if all(a[k+3]>=b[k] and b[k+3]>=a[k] for k in range(3)))
        result[row['id']] = {'source_sha256': hashlib.sha256(
            json.dumps(row['segments'], sort_keys=True).encode()).hexdigest(),
            'segment_bounds_mm': segment_boxes, 'overlapping_bounds': overlaps,
            'passed': not overlaps}
    return result


def closing_axis_bound(stack, boss):
    facts_path = HW/'manifold-layout/enclosure-assembly.facts.json'
    stage_path = HW/'mechanical-qualification/enclosure-above-core/wall-closing-staged-review.json'
    shell_path = HW/'printed-parts/enclosure/enclosure/enclosure-back-top.step'
    facts, stage = json.loads(facts_path.read_text()), json.loads(stage_path.read_text())
    retained = {}
    for name in stage['moving_components']:
        tail = name.rsplit('/', 1)[-1]
        if tail in LOOSE or tail == 'enclosure-back-top above Z253.3':
            continue
        retained[tail] = facts['bodies'][tail]
    first = min(retained, key=lambda name: retained[name][1])
    shell = cq.importers.importStep(str(shell_path)).val()
    a, b = bounds(stack), bounds(boss)
    stationary = [min(a[i], b[i]) for i in range(3)]+[max(a[i], b[i]) for i in range(3, 6)]
    # A +Y translation preserves X/Z. Only stock inside this conservative
    # X/Z prism can meet the raised ground hardware at any closing offset.
    eps = 1.e-5
    prism = cq.Solid.makeBox(stationary[3]-stationary[0]+2*eps, 800.,
        stationary[5]-stationary[2]+2*eps,
        cq.Vector(stationary[0]-eps, 0., stationary[2]-eps))
    relevant = shell.intersect(prism)
    relevant_bounds = bounds(relevant) if volume(relevant)>.001 else None
    min_y = min(retained[first][1], relevant_bounds[1] if relevant_bounds else math.inf)
    return {
        'scope': 'Only the ground relocation delta after the named low V-A chain and '
                 'pump-side elbow are loose. Retained stock/bodies translate only +Y; '
                 'one conservative X/Z stock prism replaces a sampled-motion replay.',
        'reader_sha256': sha(Path(__file__)), 'loose_names': sorted(LOOSE),
        'retained_body_bounds_mm': retained, 'facts_sha256': sha(facts_path),
        'motion_scope_sha256': sha(stage_path), 'actual_back_top_sha256': sha(shell_path),
        'full_actual_back_top_bounds_mm': bounds(shell),
        'raised_ground_bounds_mm': stationary,
        'native_stock_in_ground_XZ_prism_bounds_mm': relevant_bounds,
        'stationary_raised_ground_ymax_mm': stationary[4],
        'retained_ymin_mm': min_y, 'positive_y_separation_mm': min_y-stationary[4],
        'retired_pilot_fill_ymax_mm': 197.,
        'full_shell_to_retired_pilot_fill_y_gap_mm': bounds(shell)[1]-197.,
        'passed': min_y>stationary[4] and bounds(shell)[1]>197.,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    landing = wiring.placements()['ground-stack']['translation_mm']
    x, y, z = landing
    plan = wiring.ground_fastener_datums()
    stack = wiring.components()['ground-stack'][0]
    boss = cq.Solid.makeCylinder(plan['boss_diameter_mm']/2, z-253.4,
                                cq.Vector(x, y, 253.4))
    pilot = cq.Solid.makeCylinder(plan['pilot_diameter_mm']/2,
                                 plan['pilot_depth_mm']+1,
                                 cq.Vector(x, y, plan['pilot_bottom_z_mm']))
    boss = boss.cut(pilot)
    # The existing M3 nominal tool section is the 2.5 mm hex with fits.slip.
    head_top = z+plan['clamped_thickness_mm']+3.
    tool = cq.Solid.makeCylinder(2.5/math.sqrt(3.)+fits.slip, 355.-head_top,
                                cq.Vector(x, y, head_top))
    subjects = {'ground-stack': stack, 'ground-boss': boss, 'ground-tool': tool}
    lid_path = HERE/'foam-cap-lid-top.step'
    lid = cq.importers.importStep(str(lid_path)).val().moved(
        layout.frame_location(layout.cap_lid_pose()))
    fixture = {**subjects, 'ground-pilot': pilot, 'lid-world': lid}
    index = {'parts': {}}
    for name, shape in fixture.items():
        path = OUT/(name+'.brep')
        shape.exportBrep(str(path))
        index['parts'][name] = {'path': str(path.resolve()), 'sha256': sha(path),
                                'signature': signature(shape)}
    (OUT/'index.json').write_text(json.dumps(index, indent=2)+'\n')
    print('Ground fixture ready: '+str(OUT/'index.json'), flush=True)
    if '--closing-only' in sys.argv:
        report = json.loads(REPORT.read_text())
        report['closing_axis_separation'] = closing_axis_bound(stack, boss)
        report['passed'] = (all(row['passed'] for row in report['stock']+report['contacts']+report['approaches'])
            and all(row['passed'] for row in report['electrical']['source_current_J13_hulls'].values())
            and report['closing_axis_separation']['passed'])
        REPORT.write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report['closing_axis_separation']), flush=True)
        return

    report = {'scope': 'Only the selected ground landing, unchanged nominal bond hardware, '
        'printed boss/pilot and one nominal 2.5 mm M3 driver approach. Local nonattached '
        'neighbors use the named cached geometry. Attached ground leads and J2-COM are '
        'separate electrical work. No hand access, bond resistance, retention or load qualification.',
        'landing_world_mm': landing, 'fastener_plan': plan,
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), Path(wiring.__file__), Path(anchors.__file__), Path(fits.__file__))},
        'actual_lid': {'path': str(lid_path.relative_to(ROOT)), 'sha256': sha(lid_path),
                      'signature': signature(lid)},
        'subjects': {name: signature(shape) for name, shape in subjects.items()},
        'stock': [], 'contacts': [], 'approaches': [], 'read_cache_sha256': {},
        'assembly_stage': 'Install/tighten the ground clamp through the open funnel aperture '
                          'with the removable funnel/frame absent; hand reach is unqualified.',
        'tool': {'across_flats_mm': 2.5, 'radial_air_mm': fits.slip,
                 'start_world_z_mm': head_top, 'end_world_z_mm': 355.},
    }
    for name, witness in (
        ('complete 3 mm annular insert wall', boss),
        ('complete blind floor below pilot', cq.Solid.makeCylinder(
            5., plan['pilot_bottom_z_mm']-248., cq.Vector(x, y, 248.))),
    ):
        missing = volume(witness.cut(lid))
        report['stock'].append({'feature': name, 'missing_mm3': missing, 'passed': missing<.001})
    for name in ('ground-stack', 'ground-tool'):
        report['contacts'].append({'subject': name, 'target': 'actual lid',
                                    **contact(subjects[name], lid)})

    target_dir = ROOT/'tmp/dry-sidewall-wiring/targets'
    target_index_path = target_dir.parent/'native-targets.json'
    targets = json.loads(target_index_path.read_text())
    selected = {**anchors.supports(), **anchors.tie_witnesses()}
    for row in anchors.datums().values():
        for route, (xx, yy, zz) in zip(row['routes_west_to_east'], row['tube_centers_world_mm']):
            selected[route+'/'+row['id']+'/fixed-seat-segment'] = cq.Solid.makeCylinder(
                6.35/2, 10., cq.Vector(xx, yy-5., zz), cq.Vector(0, 1, 0))
    for name, relative in targets['parts'].items():
        if name in ('ground-stack', 'foam-cap-lid-top', 'funnel-frame', 'funnel-drain-stub',
                    'funnel-drain-union', 'elbow-cradle', 'tube-fluid-14', 'tube-fluid-16'):
            continue
        path = target_dir/relative
        other = cq.Shape.importBrep(str(path))
        selected[name] = other
        report['read_cache_sha256'][name] = sha(path)
    shell_path = HW/'printed-parts/enclosure/enclosure/enclosure-back-top.step'
    selected['enclosure-back-top'] = cq.importers.importStep(str(shell_path)).val()
    report['actual_back_top_sha256'] = sha(shell_path)
    for name, other in selected.items():
        if name.startswith('terminal-pogo-'):
            continue
        for subject, shape in subjects.items():
            if name.startswith('access-') and subject == 'ground-tool':
                continue
            if nearby(shape, other):
                row = {'subject': subject, 'target': name, **contact(shape, other)}
                report['approaches' if name.startswith('access-') else 'contacts'].append(row)

    wire_path = ROOT/'tmp/dry-sidewall-wiring/current-wiring-index.json'
    cache = json.loads(wire_path.read_text())
    manifest_path = HW/'wiring/enclosure-wiring.json'
    manifest = json.loads(manifest_path.read_text())
    current_names = {'wire-'+row['id'] for row in manifest['routes']} | set(manifest['terminations'])
    j13 = {'wire-'+row['id'] for row in manifest['routes'] if row['id'].startswith('J13-')}
    report['electrical'] = {'cache_sha256': sha(wire_path),
        'manifest_sha256': sha(manifest_path), 'excluded_attached_or_redressed': sorted(ATTACHED),
        'retired_cache_bodies_omitted': sorted(set(cache['parts'])-current_names),
        'source_current_J13_hulls': current_j13_bounds(manifest, subjects), 'body_sha256': {}}
    for name, relative in cache['parts'].items():
        if name not in current_names or name in ATTACHED or name in j13:
            continue
        path = Path(relative)
        other = cq.Shape.importBrep(str(path))
        report['electrical']['body_sha256'][name] = sha(path)
        for subject, shape in subjects.items():
            if nearby(shape, other):
                report['contacts'].append({'subject': subject, 'target': name,
                                            **contact(shape, other)})

    report['closing_axis_separation'] = closing_axis_bound(stack, boss)
    report['paired_anchor_stock_reuse'] = {
        'receipt': str((HERE/'reservoir-a-anchor-review.json').relative_to(ROOT)),
        'source_sha256': sha(Path(anchors.__file__)),
        'basis': 'The old/new ground-boss discs and pilot footprints are disjoint from '
                 'the finite anchor web/root/floor witnesses. Those native/STL readings '
                 'retain their original artifact hashes; no anchor stock reading is repeated.'}
    report['passed'] = (all(row['passed'] for row in report['stock']+report['contacts']+report['approaches'])
        and all(row['passed'] for row in report['electrical']['source_current_J13_hulls'].values())
        and report['closing_axis_separation']['passed'])
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'passed': report['passed'],
        'contacts': [r for r in report['contacts']+report['approaches'] if not r['passed']],
        'stock': report['stock'],
        'closing_gap_mm': report['closing_axis_separation']['positive_y_separation_mm']}), flush=True)


if __name__ == '__main__':
    main()
