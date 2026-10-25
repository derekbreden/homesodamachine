"""Manual sampled slide query for the wall-carried back-top over the core.

Run after an appliance export, through the CAD queue. This reader is not called
by a generator, build, commit hook or publisher. It writes no production geometry.
"""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'hardware/scripts'),
               str(ROOT / 'hardware/manifold-layout'),
               str(ROOT / 'hardware/assembly/scenes')]
from _cadq_export import import_assembly, import_step
import _scenes
import above_core
from review import bounds, manifold


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT / 'hardware/manifold-layout/enclosure-assembly.step'
    facts_path = source.with_suffix('.facts.json')
    shell_path = ROOT / 'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step'
    placed = {name: row[0] for name, row in import_assembly(source).items()}
    names = {}
    for name in placed:
        tail = name.rsplit('/', 1)[-1]
        if tail in names:
            raise ValueError(f'Duplicate component tail: {tail}')
        names[tail] = name
    # The separate piece may contain newer local stock than the appliance. Bind
    # that substitution explicitly, without moving any component or datum.
    shell_name = names['enclosure-back-top']
    exported_shell = placed[shell_name]
    placed[shell_name] = import_step(shell_path).val()
    shell_delta = placed[shell_name].Volume() - exported_shell.Volume()
    inventory = cq.Assembly(name='exported-inventory')
    for tail, name in names.items():
        inventory.add(placed[name], name=tail)
    inventory.wiring_body_names = frozenset(
        n for n in names if n.startswith(('wire-', 'terminal-', 'jacket-')))
    ownership = _scenes.holders(inventory)
    handoffs = frozenset(('tube-drain-vent', *_scenes.BACK_TOP_HANDOFF_TUBES))
    selected = _scenes.back_top_carried_names()
    if selected - names.keys():
        raise ValueError(f'Missing carried components: {sorted(selected - names.keys())}')
    bodies = frozenset(n for n in _scenes.held_by(
        'enclosure-back-top', ownership, stop=('funnel-frame', 'funnel', 'funnel-cover'))
        if not n.startswith('tube-') and n not in handoffs)
    carried = set(bodies) | set(selected)

    carried -= handoffs
    lid_override = None
    if '--lid-world' in sys.argv:
        lid_override = Path(sys.argv[sys.argv.index('--lid-world') + 1]).resolve()
        placed[names['foam-cap-lid-top']] = cq.Shape.importBrep(str(lid_override))
    upper = cq.Solid.makeBox(400, 800, 200, cq.Vector(-200, 0, 253.3))
    moving = {shell_name + ' above Z253.3': placed[shell_name].intersect(upper)}
    for tail in sorted(carried - {'enclosure-back-top'}):
        name = names.get(tail)
        if name and not tail.endswith('-screw') and bounds(placed[name])[1][2] > 253.3:
            moving[name] = placed[name]
    core_equipment = set(above_core.core_equipment_names())
    stationary = {name: shape for name, shape in placed.items()
                  if ('cold-core/' in name or name.rsplit('/', 1)[-1] in core_equipment)
                  and bounds(shape)[1][2] > 253.3
                  and name not in moving}
    stage_pump = '--stage-pump-joint' in sys.argv
    if stage_pump:
        # A separate handling scenario, not a change to final geometry or its
        # permanent mounting parent. The pump-side elbow is already on the pump.
        moving.pop(names['lower-pump-elbow'], None)
        stationary[names['lower-pump-elbow']] = placed[names['lower-pump-elbow']]
    foam_name = names['soda-continuous-insulation']
    moving.pop(foam_name, None)
    offsets = np.array([(0., y, 0.) for y in
                        (0., .25, .5, 1., 2., 5., 10., 20., 30., 50., 75.,
                         100., 132., 150., 200., 250., 300.)])
    mesh_cache = {}

    def meshed(name, shape):
        if name not in mesh_cache:
            print('Meshing', name, flush=True)
            mesh_cache[name] = manifold(shape)
        return mesh_cache[name]

    readings = []
    positives = []
    soft = []
    for name, shape in moving.items():
        low, high = bounds(shape)
        for other, obstacle in stationary.items():
            a, b = bounds(obstacle)
            active = [i for i, offset in enumerate(offsets)
                      if np.all(high + offset >= a) and np.all(b >= low + offset)]
            if not active:
                continue
            left, right = meshed(name, shape), meshed(other, obstacle)
            amounts = [(i, float((left.translate(offsets[i]) ^ right).volume()))
                       for i in active]
            peak, amount = max(amounts, key=lambda row: row[1])
            row = {'moving': name, 'stationary': other,
                   'sample_count': len(active), 'maximum_mesh_common_mm3': amount,
                   'peak_offset_mm': offsets[peak].tolist()}
            if amount > .1:
                moved = shape.translate(tuple(offsets[peak]))
                common = moved.intersect(obstacle, tol=1e-6)
                exact = 0. if common.isNull() else abs(common.Volume())
                row['native_common_at_peak_mm3'] = exact
                row['native_common_bounds_mm'] = (
                    [*bounds(common)[0].tolist(), *bounds(common)[1].tolist()]
                    if exact > 1e-6 else None)
                row['positive_samples'] = [
                    {'offset_mm': offsets[i].tolist(), 'mesh_common_mm3': v}
                    for i, v in amounts if v > .1]
                if 'soda-continuous-insulation' in name:
                    soft.append(row)
                elif exact > .1:
                    positives.append(row)
                print(json.dumps(row), flush=True)
            readings.append(row)
    sources = [Path(__file__), HERE / 'review.py', source, shell_path,
               Path(_scenes.__file__), Path(above_core.__file__),
               ROOT / 'hardware/manifold-layout/above-core.json',
               ROOT / 'hardware/manifold-layout/_scorecard.py']
    if lid_override is not None:
        sources.append(lid_override)
    result = {
        'schema': 1, 'units': 'mm', 'frame': 'Production enclosure XYZ; Z up',
        'scope': 'Sampled pure-Y travel of the selected back-top upper stock and '
                 'carried equipment over the populated cold core. The latest separate '
                 'back-top and any explicitly named world-lid fixture replace their appliance copies at unchanged datums.',
        'method': 'Native bodies tessellated at 0.02 mm / 0.08 rad, float32 manifold '
                  'intersections at the listed offsets. Each mesh-positive peak is '
                  'read again with a native solid intersection. A clear sample set '
                  'is not a continuous-path proof.',
        'mesh_reporting_threshold_mm3': .1,
        'no_rigid_counterexample_at_tested_offsets': not positives,
        'offsets_mm': offsets.tolist(),
        'moving_components': sorted(moving),
        'stationary_components': sorted(stationary),
        'omitted_cross_parent_handoffs': sorted(handoffs),
        'pump_joint_staged_at_core': stage_pump,
        'unqueried_soft_component': foam_name,
        'same_datum_back_top_volume_delta_mm3': shell_delta,
        'same_datum_core_lid_override': str(lid_override.relative_to(ROOT)) if lid_override else None,
        'rigid_native_counterexamples': positives,
        'soft_foam_proxy_contacts': soft,
        'soft_foam_scope': 'Not queried as a rigid sliding member. The occupied proxy is an estimated compressed shape; its handling is unqualified.',
        'pair_readings': readings,
        'limits': [
            'The original lower rails, floor and shell seam motions retain their separate records.',
            'Funnel, frame, drain group and closure screws are removed.',
            'The continuous inlet stays one physical tube through a plain guide. Its '
            'cross-parent span is not included as an undeformable moving member.',
            'Pump, gas, drain and electrical handoffs need separate final-connection handling.',
            'The occupied foam is a soft display estimate. Its contacts are reported '
            'separately and establish no compression force, strain or clearance.',
            'No hand access, insertion force, printed fit, stiffness, retention, sealing '
            'or lifetime qualification is inferred.',
        ],
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
    }
    output = HERE / ('wall-closing-staged-review.json' if stage_pump else 'wall-closing-review.json')
    output.write_text(json.dumps(result, indent=2) + '\n')
    print('REPORT', output, flush=True)
    print('RIGID COUNTEREXAMPLES', len(positives), flush=True)


if __name__ == '__main__':
    main()
