"""Manual native mounting-stock and display-pocket reading for passage refinements."""
from pathlib import Path
import argparse
import json

import refine_review as refinement
import review as r


def protected_change(added, removed, name, bounds):
    region = r.enc._ybox(*bounds)
    result = dict(name=name, bounds_mm=bounds)
    for label, shape in (('added', added), ('removed', removed)):
        gap = r.box_gap(r.shape_bounds(shape), bounds) if shape.Solids() else None
        shared = 0. if gap is None or gap > 0. else refinement.common_volume(shape, region)
        result[label + '_bounds_separation_mm'] = gap
        result[label + '_volume_mm3'] = shared
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline', type=Path)
    parser.add_argument('--regions', type=Path,
                        default=r.ENC / 'heat-set-review/print-regions.json')
    parser.add_argument('--reading', type=Path, default=r.HERE / 'native-review.json')
    parser.add_argument('--cleanouts', action='store_true',
                        help='also read the two below-glass-seat support cleanouts')
    parser.add_argument('--joint-review', type=Path,
                        help='identified current M5 review for intentional Y-seam host changes')
    parser.add_argument('--joint-band-y', type=float, nargs=2, default=(197., 217.8),
                        metavar=('MIN', 'MAX'),
                        help='declared Y extent of the identified joint revision')
    args = parser.parse_args()
    prior_sha = r.sha(args.reading)
    reading = json.loads(args.reading.read_text())
    old, old_id = refinement.read_native(args.baseline)
    if not any(part['refined_native']['sha256'] == old_id['sha256']
               for entry in reading['printed_stock_refinements'] for part in entry['parts']):
        raise RuntimeError('Baseline has no recorded native refinement')
    new, new_id = refinement.read_native(r.ENC / 'enclosure-front-top.step')
    added, removed = refinement.delta(old, new)
    joint_reference = None
    if args.joint_review is not None:
        joint_sha = r.sha(args.joint_review)
        joint = json.loads(args.joint_review.read_text())
        expected = joint['input_sha256'][r.path_label(r.ENC / 'enclosure-front-top.step')]
        if expected != new_id['sha256'] or r.sha(args.joint_review) != joint_sha:
            raise RuntimeError('Current native part is not the identified M5 review input')
        band_y0, band_y1 = args.joint_band_y
        if band_y1 <= band_y0:
            raise RuntimeError('The declared joint Y band must have positive width')
        band = r.enc._ybox(-200.,200.,band_y0-.001,band_y1+.001,-100.,400.)
        outside = sum(r.volume(shape.cut(band)) for shape in (added, removed)
                      if shape.Solids())
        joint_reference = dict(path=r.path_label(args.joint_review),sha256=joint_sha,
                              identified_native_sha256=expected,
                              joint_y_band_mm=[band_y0, band_y1],
                              changed_volume_outside_joint_band_mm3=outside)
        if outside > r.VOLUME_FLOOR:
            raise RuntimeError(f'Joint changes leave their declared band: {joint_reference}')
    regions_sha = r.sha(args.regions)
    regions = json.loads(args.regions.read_text())['pieces']['front-top']
    if r.sha(args.regions) != regions_sha:
        raise RuntimeError('Modifier specification changed during its read')
    modifiers = [protected_change(added, removed, row['name'], row['machine_bounds_mm'])
                 for row in regions]
    for row in modifiers:
        row['scope'] = ('identified_current_M5_joint_review'
                        if joint_reference is not None and row['name'].startswith('Y seam knuckle')
                        else 'native_material_unchanged')
    box, _ = r._box_spec.read(r.enc.Box, r.enc.Bound,
                             (r.enc.Pack, r.enc.PortField, r.enc.Nameplate))
    valve_guards = []
    for plane, sign, seats in box.pack.valve_trays:
        mid = (min(z for _x, z in seats) + max(z for _x, z in seats)) / 2.
        face = plane - sign * r.enc._valve_tray.SEAT
        near, far = sorted((face, face - sign * r.enc._valve_tray.THICK))
        half = r.enc._valve_tray.height(seats) / 2.
        bounds = [box.outer[0], box.outer[1], near, far, mid-half, mid+half]
        valve_guards.append(protected_change(added, removed,
            f'Complete valve tray, post-socket and bearing envelope at Y{plane:g}', bounds))
    guard_z = max(f['pilot_end_z'] for f in r.mount.fasteners(r.enc, box))
    guard_z = max(guard_z, r.mount.datums(r.enc, box)['flange_z'] + r.enc._tray.boss_depth + .4)
    pump_guard = protected_change(added, removed, 'Fixed pump bearing and screw stock',
                                 [-150., 150., 0., r.enc.housing_back_y(box.outer), 100., guard_z])
    canonical = r.enc._display_cuts(box.outer, extend_wing_exits=False)
    pocket_overlap = refinement.common_volume(new, canonical)
    place = r.cq.Location(r.enc.display_plane(box.outer))
    inverse = r.mount.inverse_cuts(r.enc, box)
    cross = r.mount.wire_cuts(r.enc, box)[2]
    wing_gaps = [dict(side=side, inverse_distance_mm=min(exit.distance(cut) for cut in inverse),
                     cross_distance_mm=exit.distance(cross))
                 for side, local in zip(('left', 'right'), r.enc._display_wings.support_exits(12.))
                 for exit in (local.moved(place),)]
    cleanout_reading = None
    if args.cleanouts:
        wings = r.enc._display_wings
        reach = wings.COVER_X/2. + wings.WING_REACH + wings.TIP_AIR
        roof = wings.GLASS_SEAT-r.enc.wall
        floor = wings.BACK+wings.WING_THICK+wings.BEARING_AIR-12.
        upper_guard = r.enc._ybox(-reach-1.,reach+1.,-wings.COVER_Y/2.-1.,
            wings.COVER_Y/2.+1.,roof,1.).moved(place)
        glass_guard = r.enc._ybox(-r.enc.display_bezel_cut_x/2.,r.enc.display_bezel_cut_x/2.,
            -r.enc.display_bezel_cut_slope/2.,r.enc.display_bezel_cut_slope/2.,
            roof,wings.GLASS_SEAT).moved(place)
        exterior = r.cq.Compound.makeCompound(r.enc._rounded_outer(box.outer).Faces())
        branches = []
        for side, channel, pcb_x in zip(('left','right'), r.mount.display_cleanouts(r.enc,box),
                (r.enc.display_body_offset_x-r.enc.display_pcb_x/2.,
                 r.enc.display_body_offset_x+r.enc.display_pcb_x/2.)):
            y0 = r.enc.display_body_offset_slope-r.enc.display_pcb_slope/2.
            y1 = r.enc.display_body_offset_slope+r.enc.display_pcb_slope/2.
            aperture = r.enc._ybox(pcb_x-.1,pcb_x+.1,y0,y1,floor,roof).moved(place)
            branches.append(dict(side=side, bounds_world_mm=r.shape_bounds(channel),
                native_material_in_channel_mm3=refinement.common_volume(new,channel),
                native_material_in_pcb_aperture_mm3=refinement.common_volume(new,aperture),
                distance_from_pump_inverse_mm=min(channel.distance(cut) for cut in inverse),
                distance_from_outer_silhouette_mm=channel.distance(exterior)))
        cleanout_reading = dict(normal_floor_mm=floor, normal_roof_mm=roof,
            nominal_clear_normal_height_mm=roof-floor,
            nominal_pcb_opening_span_mm=r.enc.display_pcb_slope,
            retained_glass_backing_normal_mm=wings.GLASS_SEAT-roof,
            changed_volume_in_three_mm_glass_backing_mm3=(
                refinement.common_volume(added,glass_guard)+refinement.common_volume(removed,glass_guard)),
            changed_volume_above_cleanout_roof_mm3=(
                refinement.common_volume(added,upper_guard)+refinement.common_volume(removed,upper_guard)),
            branches=branches)
    result = dict(part='enclosure-front-top', predecessor_native=old_id, refined_native=new_id,
        valid=new.isValid(), solids=len(new.Solids()),
        geometry_sources={r.path_label(path): r.sha(path) for path in (
            Path(r.enc.__file__).resolve(), Path(r.mount.__file__).resolve(),
            Path(r.enc._display_wings.__file__).resolve(),
            r.ROOT / 'hardware/manifold-layout/enclosure-box.json')},
        added_volume_mm3=r.volume(added), removed_volume_mm3=r.volume(removed),
        added_bounds_mm=refinement.solid_bounds(added),
        removed_bounds_mm=refinement.solid_bounds(removed),
        modifier_specification=dict(actual_input_path=str(args.regions.resolve()), sha256=regions_sha),
        intentional_joint_reference=joint_reference,
        protected_modifier_boxes=modifiers, protected_valve_mounting_envelopes=valve_guards,
        protected_pump_stock=pump_guard,
        canonical_display_pocket_overlap_mm3=pocket_overlap,
        canonical_twelve_mm_wing_exit_separation=wing_gaps,
        display_support_cleanouts=cleanout_reading,
        scope='Native added and removed material are compared with the exact predecessor. '
            f'All {len(modifiers)} modifier boxes are identified; Y-seam changes, when present, '
            'retain their separate exact-input M5 review. The other modifier boxes, both complete '
            'valve tray/post/bearing envelopes, and the pump bearing/screw region retain their '
            'native material. The unchanged '
            'canonical display pocket and 12 mm exits stay clear. Continuous added-stock paths '
            'are recorded separately by verify_successor.py. Support extraction, wire/Faston '
            'fit and physical pump retention retain their separate evidence and limits.')
    guards = [row for row in modifiers if row['scope']=='native_material_unchanged'] + valve_guards + [pump_guard]
    if (not result['valid'] or result['solids'] != 1 or pocket_overlap > r.VOLUME_FLOOR
            or any(row[key] > r.VOLUME_FLOOR for row in guards
                   for key in ('added_volume_mm3', 'removed_volume_mm3'))
            or any(row['inverse_distance_mm'] < 17.22 for row in wing_gaps)
            or (cleanout_reading is not None and (
                (joint_reference is None and r.volume(added) > r.VOLUME_FLOOR)
                or cleanout_reading['changed_volume_in_three_mm_glass_backing_mm3'] > r.VOLUME_FLOOR
                or cleanout_reading['changed_volume_above_cleanout_roof_mm3'] > r.VOLUME_FLOOR
                or any(row[key] > r.VOLUME_FLOOR for row in cleanout_reading['branches']
                    for key in ('native_material_in_channel_mm3','native_material_in_pcb_aperture_mm3'))))):
        raise RuntimeError(f'Passage refinement changes protected stock or fit: {result}')
    reading.setdefault('passage_stock_refinements', []).append(dict(
        verification_source_sha256=r.sha(Path(__file__).resolve()),
        comparison_source_sha256=r.sha(Path(refinement.__file__).resolve()),
        prior_reading_sha256=prior_sha, status='native_passage_stock_clear', result=result))
    temporary = args.reading.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(reading, indent=2) + '\n')
    temporary.replace(args.reading)
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
