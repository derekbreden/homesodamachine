"""Check measured spring consumers without rebuilding the full appliance.

Rebuild both native carrier halves and compare with the published STEP. Optional
pre-edit interface and artifact hashes additionally prove this bounded change
preserves all printed geometry and interface coordinates.
"""

from pathlib import Path
import argparse
import hashlib
import json
import sys

import cadquery as cq

import tee_carrier as carrier
import tee_carrier_spring as spring

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
ROOT = HW.parent
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'manifold-layout'),
               str(HW / 'assembly' / 'scenes')]
import _box_spec
import _facts
import _scorecard
import _scenes
import enclosure_assembly as assembly


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measure(baseline=None):
    spec = carrier.DEFAULT_SPEC
    interface = carrier.interface(spec)
    offsets = {'release': spec.release_offset_y, 'connected': spec.connected_offset_y,
               'aft_limit': spec.aft_limit_offset_y}
    bearing = {state: round(spec.spring_bore_floor_y + offset - spec.fixed_seat_floor_y, 6)
               for state, offset in offsets.items()}
    data = spring.fit_facts(bearing, bore_diameter=spec.spring_bore_d,
                            loading_length=spec.spring_load_length,
                            required_radial_air=spec.slide_air)
    failures = []
    # Use the actual facts and producer/consumer handoff serializers, then read
    # through the fact accessor used by document drivers. None must remain unknown.
    for name, plain in (('facts', _facts._plain(data)),
                        ('box_spec', _box_spec._plain(data))):
        decoded = json.loads(json.dumps(plain, allow_nan=False))
        if name == 'box_spec':
            decoded = _box_spec._tupled(decoded, {})
        view = _facts.Facts({'box': {'tee_carrier': decoded}}, {}).box.tee_carrier
        if (any(value is not None for value in view['spring_pair_forces_n'].values())
                or view['spring_rate_n_per_mm'] is not None
                or view['spring_wire_diameter'] is not None
                or view['spring_inside_diameter'] is not None
                or view['spring_representation']['material_volume_mm3'] is not None
                or view['spring_representation']['mass_g'] is not None):
            failures.append(f'{name} gives an unmeasured spring property a numerical value')
    rejected = []
    for label, kwargs in (
            ('at compressed upper estimate', {'bearing_lengths': {'probe': 7.0}}),
            ('below compressed upper estimate', {'bearing_lengths': {'probe': 6.9}}),
            ('no compression at free length', {'bearing_lengths': {'probe': 27.0}}),
            ('too little running air', {'bore_diameter': 6.49}),
            ('loading at compressed upper estimate', {'loading_length': 7.0}),
            ('nonfinite length', {'bearing_lengths': {'probe': float('nan')}})):
        params = dict(bearing_lengths=bearing, bore_diameter=spec.spring_bore_d,
                      loading_length=spec.spring_load_length, required_radial_air=spec.slide_air)
        params.update(kwargs)
        try:
            spring.fit_facts(**params)
        except ValueError:
            rejected.append(label)
        else:
            failures.append(f'accepted {label}')
    shapes, files = [], {}
    for side, name in ((-1, 'left'), (1, 'right')):
        part = HERE / f'enclosure-tee-carrier-{name}.step'
        published = cq.importers.importStep(str(part)).val()
        built = carrier.build_half(spec, side).val()
        added, removed = built.cut(published).Volume(), published.cut(built).Volume()
        if max(added, removed) > 1e-5:
            failures.append(f'{name} differs from the published native carrier')
        shapes.append({'side': name, 'source_added_mm3': added, 'source_removed_mm3': removed})
        for suffix in ('.step', '.stl', '.step.mesh'):
            file = part.with_suffix(suffix)
            files[file.name] = sha(file)
    envelope_checks = []
    for state, length in bearing.items():
        unit = cq.Assembly(name=f'measured-springs-{state}')
        assembly.add_carrier_spring_envelopes(unit, {**interface, **data}, state=state)
        for node, station in zip(unit.children, interface['spring_stations']):
            body = node.obj
            bb = body.BoundingBox()
            wanted = (station['x'] - 3.0, station['x'] + 3.0,
                      station['seat_floor_y'], station['seat_floor_y'] + length,
                      station['z'] - 3.0, station['z'] + 3.0)
            got = (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)
            if max(abs(a - b) for a, b in zip(wanted, got)) > 1e-6:
                failures.append(f'{node.name}/{state} has the wrong measured envelope')
            if node.metadata != spring.ENVELOPE_METADATA or '-envelope-' not in node.name:
                failures.append(f'{node.name} is not explicitly clearance-only')
            if node.name not in _scenes.BEARS_ON:
                failures.append(f'{node.name} is missing its service scene holder')
            mounts = [row for row in _scorecard.MOUNTS if row[0] == node.name]
            if len(mounts) != 1:
                failures.append(f'{node.name} is missing its unique mechanical mount')
            envelope_checks.append({'body': node.name, 'state': state,
                                    'bounds_mm': got, 'representation': node.metadata})
            assembly.SEATS.pop(node.name, None)
    preserved = None
    if baseline is not None:
        before = json.loads(baseline.read_text())
        current = json.loads(json.dumps(interface))
        changed = sorted(key for key in before['interface'].keys() | current.keys()
                         if before['interface'].get(key) != current.get(key))
        moved_files = sorted(name for name, digest in before['files'].items()
                             if files.get(name) != digest)
        preserved = {'baseline_sha256': sha(baseline), 'changed_interface_fields': changed,
                     'changed_artifact_bytes': moved_files}
        if changed or moved_files:
            failures.append('printed interface or native/mesh artifact bytes changed')
    return {'scope': 'Measured spring consumer and printed-geometry invariance only; '
                     'no whole-appliance regeneration or spring-retention qualification.',
            'status': 'pass' if not failures else 'fail', 'failures': failures,
            'measured_sample_fit': data, 'rejected_invalid_fits': rejected,
            'nullable_serializers_checked': ['facts JSON and accessor', 'box_spec JSON and accessor'],
            'native_carrier_comparison': shapes, 'published_artifact_sha256': files,
            'pre_edit_invariance': preserved, 'envelopes': envelope_checks,
            'source_sha256': {str(path.relative_to(ROOT)): sha(path) for path in
                              (Path(carrier.__file__), Path(spring.__file__),
                               spring.MEASUREMENT_FILE, Path(assembly.__file__))},
            'assembly_facts_status': 'Retained baseline; full assembly rebuild intentionally pending.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'measured-spring-check.json')
    args = parser.parse_args()
    result = measure(args.baseline)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(f"Measured spring consumer: {result['status']}; "
          f"{len(result['rejected_invalid_fits'])} invalid fits rejected; "
          f"{len(result['envelopes'])} installed envelopes checked")
    for row in result['native_carrier_comparison']:
        print(f"{row['side']}: added {row['source_added_mm3']:.9f} / "
              f"removed {row['source_removed_mm3']:.9f} mm³")
    for failure in result['failures']:
        print(f'FAIL: {failure}')
    return bool(result['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
