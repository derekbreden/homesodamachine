"""Manual native rear-breakout subset and existing mounting-stock comparison."""
from pathlib import Path
import argparse
import json

import refine_review as refinement
import review as r


def protected_reading(removed, name, bounds):
    region = r.enc._ybox(*bounds)
    gap = r.box_gap(r.shape_bounds(removed), bounds)
    common = 0. if gap > 0. else refinement.common_volume(removed, region)
    return dict(name=name, bounds_mm=bounds, removed_bounds_separation_mm=gap,
                changed_volume_mm3=common)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--reading', type=Path, default=r.HERE / 'native-review.json')
    args = parser.parse_args()
    prior_sha = r.sha(args.reading)
    reading = json.loads(args.reading.read_text())
    old, old_id = refinement.read_native(args.baseline)
    matches = [entry for entry in reading['printed_stock_refinements']
               if any(part['part'] == 'enclosure-front-top' and
                      part['refined_native']['sha256'] == old_id['sha256']
                      for part in entry['parts'])]
    if not matches:
        raise RuntimeError('Baseline is not a recorded front-top refinement')
    new, new_id = refinement.read_native(r.ENC / 'enclosure-front-top.step')
    added, removed = refinement.delta(old, new)
    regions_path = r.ENC / 'heat-set-review/print-regions.json'
    regions_sha = r.sha(regions_path)
    regions = json.loads(regions_path.read_text())['pieces']['front-top']
    if r.sha(regions_path) != regions_sha:
        raise RuntimeError('Modifier specification changed during read')
    modifiers = [protected_reading(removed, row['name'], row['machine_bounds_mm'])
                 for row in regions]
    box, _ = r._box_spec.read(r.enc.Box, r.enc.Bound,
                             (r.enc.Pack, r.enc.PortField, r.enc.Nameplate))
    tray_guards = []
    for plane, sign, seats in box.pack.valve_trays:
        mid = (min(z for _x, z in seats) + max(z for _x, z in seats)) / 2.
        face = plane - sign * r.enc._valve_tray.SEAT
        near, far = sorted((face, face - sign * r.enc._valve_tray.THICK))
        half = r.enc._valve_tray.height(seats) / 2.
        bounds = [box.outer[0], box.outer[1], near, far, mid - half, mid + half]
        tray_guards.append(protected_reading(removed,
            f'Complete valve tray, post-socket and bearing envelope at Y{plane:g}', bounds))
    guard_z = max(part['bearing_and_screw_guard_top_z_mm'] for entry in matches
                  for part in entry['parts'] if part['part'] == 'enclosure-front-top')
    pump_guard = protected_reading(removed, 'Fixed pump bearing and screw stock',
                                  [-150., 150., 0., 230., 100., guard_z])
    result = dict(part='enclosure-front-top', original_native=old_id, refined_native=new_id,
        valid=new.isValid(), solids=len(new.Solids()), added_volume_mm3=r.volume(added),
        removed_volume_mm3=r.volume(removed), removed_bounds_mm=refinement.solid_bounds(removed),
        modifier_specification=dict(path=r.path_label(regions_path), sha256=regions_sha),
        protected_modifier_boxes=modifiers, protected_valve_mounting_envelopes=tray_guards,
        protected_pump_stock=pump_guard,
        bearing_and_screw_guard_top_z_mm=guard_z,
        changed_volume_in_bearing_and_screw_guard_mm3=pump_guard['changed_volume_mm3'],
        scope='The current part is a native material subset of its recorded predecessor. '
            'Prior rigid collision bounds remain conservative. All nine actual front-top '
            'infill modifier boxes and both complete valve tray/post/bearing envelopes are '
            'checked separately. Valves use press-in posts; the six nonpump modifier boxes '
            'cover seam and funnel hosts. No physical retention or lifetime claim is made.')
    guards = modifiers + tray_guards + [pump_guard]
    if (not result['valid'] or result['solids'] != 1 or result['added_volume_mm3'] > r.VOLUME_FLOOR
            or any(row['changed_volume_mm3'] > r.VOLUME_FLOOR for row in guards)):
        raise RuntimeError(f'Rear-breakout refinement changes protected stock: {result}')
    for entry in matches:
        entry['role'] = 'predecessor_rigid_stock_refinement'
    reading['printed_stock_refinements'].append(dict(role='rear_breakout_removal_successor',
        verification_source_sha256=r.sha(Path(__file__).resolve()),
        comparison_source_sha256=r.sha(Path(refinement.__file__).resolve()),
        prior_reading_sha256=prior_sha, status='native_refinement_clear', parts=[result]))
    temporary = args.reading.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(reading, indent=2) + '\n')
    temporary.replace(args.reading)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
