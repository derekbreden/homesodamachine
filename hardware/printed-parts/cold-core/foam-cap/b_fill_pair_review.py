"""Manual local B-fill fitting, cover and installed-neighbor reading.

This question-specific reader is not part of the generator or recurring checks.
It builds current cup/lid stock and reads explicitly supplied saved native
neighbor fixtures. Canonical artifact binding is a separate optional readback.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(parent for parent in HERE.parents if (parent/'hardware/scripts').is_dir())
sys.path[:0] = [str(ROOT/'hardware'/path) for path in (
    'scripts', 'manifold-layout', 'printed-parts/cold-core',
    'printed-parts/cold-core/foam-cap', 'printed-parts/cadlib')]
import cadquery as cq
import above_core as layout
import above_core_parts as parts
import above_core_routes as routes
import _above_core_mounts as mounts
import _cold_core_interface as core
import foam_cap


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def bounds(shape):
    box = shape.BoundingBox()
    return [getattr(box, axis) for axis in ('xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax')]


def signature(shape):
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
            'faces': len(shape.Faces()), 'volume_mm3': volume(shape),
            'bounds_mm': bounds(shape)}


def nearby(first, second, allowance=0.):
    a, b = bounds(first), bounds(second)
    return all(a[i+3]+allowance >= b[i] and b[i+3]+allowance >= a[i] for i in range(3))


def contact(first, second):
    common = first.intersect(second, tol=1.e-7)
    result = {'overlap_mm3': volume(common), 'air_mm': first.distance(second)}
    if result['overlap_mm3'] > 1.e-6:
        result['bounds_mm'] = bounds(common)
    return result


def box(a, b):
    return cq.Solid.makeBox(*(y-x for x, y in zip(a, b)), cq.Vector(*a))


def refine_service_scope(record, hardware_index, cache):
    """Compare only the four recorded access contacts, without a layout replay."""
    targets = json.loads(hardware_index.read_text())['parts']
    folder = hardware_index.parent/'targets'
    region = box((-105., 220., 250.), (-10., 305., 310.))
    old_tube = cq.Shape.importBrep(str(folder/targets['tube-fluid-24'])).intersect(region)
    new_tube = cq.Shape.importBrep(str(cache/'tube-fluid-24-tail.brep'))
    comparisons = []
    for name in ('access-terminal-J5-withdrawal', 'access-terminal-J6-withdrawal',
                 'access-terminal-J13-withdrawal'):
        witness = cq.Shape.importBrep(str(folder/targets[name]))
        comparisons.append({'witness': name,
                            'prior_fluid24': contact(old_tube, witness),
                            'selected_fluid24': contact(new_tube, witness)})
    upper = cq.Shape.importBrep(str(cache/'reservoir-b-fill-upper.brep'))
    old_upper = cq.Shape.importBrep(str(folder/targets['reservoir-b-fill-upper']))
    mouth = cq.Shape.importBrep(str(folder/targets['access-J10-mouth-V12']))
    drivers = {name: contact(upper, cq.Shape.importBrep(str(folder/targets[name])))
               for name in ('access-J10-V12', 'access-J10-GND')}
    record['service_comparison'] = {
        'scope': 'Only the three saved vertical withdrawal witnesses versus the same old/new fluid24 tail region, plus the J10 entry witness and two actual screw tools. Connector handling, flexible tube displacement and force are not qualified.',
        'fluid24_region_world_mm': bounds(region),
        'vertical_withdrawal_comparisons': comparisons,
        'J10_entry': {'prior_upper_fitting': contact(old_upper, mouth),
                      'selected_upper_fitting': contact(upper, mouth),
                      'selected_upper_vs_vertical_screw_tools': drivers},
        'assembly_order': 'Terminate both J10 power leads on the loose PCB, then fasten the PCB to the core and land the free ends at the core WAGOs. The captured B-fill upper fitting is already inside the closed cap. This does not qualify installed wire insertion/withdrawal service; field retermination may require unbolting/staging the PCB and flexible leads.',
        'connector_service': 'Disconnect and stage the flexible B-fill tube for the recorded vertical J5/J6/J13 service approaches. No handling path or force is established by the witness intersection alone.',
        'reader_sha256': sha(Path(__file__)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hardware-index', type=Path,
                        default=ROOT/'tmp/dry-sidewall-wiring/native-targets.json')
    parser.add_argument('--wire-index', type=Path,
                        default=ROOT/'tmp/dry-sidewall-wiring/current-wiring-index.json')
    parser.add_argument('--wire-overlay', type=Path,
                        default=ROOT/'tmp/ground-j2-wire-delta/final-seven-index.json')
    parser.add_argument('--direct-j13', type=Path,
                        default=ROOT/'tmp/b-fill-selected-native/direct-j13/index.json')
    parser.add_argument('--ports', type=Path, default=ROOT/'tmp/above-core-route-fixture.json')
    parser.add_argument('--cache', type=Path, default=ROOT/'tmp/b-fill-selected-native')
    parser.add_argument('--cached-stock', action='store_true',
                        help='Read the saved source-built world cup/lid from --cache.')
    parser.add_argument('--access-only', action='store_true',
                        help='Append only the finite prior/selected service comparison.')
    parser.add_argument('--output', type=Path, default=HERE/'b-fill-pair-review.json')
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    if args.access_only:
        record = json.loads(args.output.read_text())
        refine_service_scope(record, args.hardware_index, args.cache)
        args.output.write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps(record['service_comparison'], indent=2), flush=True)
        return
    height = core.foam_cap_height-core.head_pad_height
    frame = layout.frame_location(layout.cap_lid_pose())
    if args.cached_stock:
        cup = cq.Shape.importBrep(str(args.cache/'cup-world.brep'))
        lid = cq.Shape.importBrep(str(args.cache/'lid-world.brep'))
    else:
        cup = foam_cap.build_foam_cap().val().translate((0., 0., -height)).moved(frame)
        lid = foam_cap.build_top_lid().val().moved(frame)
        cup.exportBrep(str(args.cache/'cup-world.brep'))
        lid.exportBrep(str(args.cache/'lid-world.brep'))
    data = mounts.reservoir_b_fill_link()
    features = mounts.reservoir_b_fill_features(height)
    fittings = mounts.reservoir_b_fill_parts()
    link_spec = {'od_mm': 6.35, 'id_mm': 4.24,
                 'points_mm': data['exposed_route_world_mm'],
                 'segments': [{'kind': 'bezier',
                               'control_points_mm': data['exposed_route_world_mm']}]}
    link = parts.route_shape(link_spec)
    ports = json.loads(args.ports.read_text())['ports']
    ports['foam-assembly.reservoir-b-fill'] = [data['upper_mouth_world_mm'], [0., 0., 1.], 6.35]
    external_spec = routes.route_specifications(lambda name, port: ports[name+'.'+port])['fluid-24']
    external = parts.route_shape(external_spec)
    # Only the final rounding, crossrun and vertical entry change. The front
    # valve and earlier west run keep their existing finite receiving record.
    external_tail = external.intersect(box((-105., 220., 250.), (-10., 305., 310.)))
    old_cup = cq.importers.importStep(str(HERE/'foam-cap-top.step')).val()
    old_cup = old_cup.translate((0., 0., -height)).moved(frame)
    old_lid = cq.importers.importStep(str(HERE/'foam-cap-lid-top.step')).val().moved(frame)
    # STEP reimport/Boolean residuals elsewhere are outside this fitting
    # question. Crop only the named old/new pocket area before comparing
    # printed additions with installed neighbors.
    pocket_region = box((-65., 215., 233.), (-15., 306., 256.))
    additions = {'cup-added-stock': cup.cut(old_cup).intersect(pocket_region),
                 'lid-added-stock': lid.cut(old_lid).intersect(pocket_region)}
    subjects = {**fittings, 'reservoir-b-fill-link': link,
                'tube-fluid-24-tail': external_tail, **additions}
    print('Current source cup/lid and four fluid subjects built', flush=True)
    record = {
        'scope': 'Selected +15X upper B-fill guide and scoped2.4mm cover. Lower reservoir bore/stem tip, V-A tube, PCB and other installed rigid poses remain fixed. Only the two fittings, direct internal link, changed fluid24 tail and added cup/lid stock are checked against local saved native neighbors. This is CAD layout/capture evidence, not physical load, pressure, tolerance, foam sealing or installation qualification.',
        'source_sha256': {str(path.relative_to(ROOT)): sha(path) for path in (
            Path(__file__), Path(mounts.__file__), Path(layout.__file__), Path(parts.__file__),
            Path(routes.__file__), ROOT/'hardware/manifold-layout/above-core.json',
            HERE/'foam_cap.py', HERE.parent/'_foam_cap.py')},
        'link': data,
        'cup': signature(cup), 'lid': signature(lid),
        'stock_input': {'basis': ('Saved source-built world stock from the preceding '
                                 'same-geometry run' if args.cached_stock else 'Fresh source build'),
                        'cup_brep_sha256': sha(args.cache/'cup-world.brep'),
                        'lid_brep_sha256': sha(args.cache/'lid-world.brep'),
                        'named_pocket_delta_region_mm': bounds(pocket_region)},
        'fittings': {name: signature(shape) for name, shape in fittings.items()},
        'exposed_link': {'specification': link_spec, 'signature': signature(link),
                         'drawn_length_mm': parts.route_wire(link_spec).Length(),
                         'receiving_depth_scope': 'Observed socket faces define exposed tube only. The JG receiving depth is unmeasured; use actual receiving marks for the physical cut.'},
        'external_fluid24': {'specification': external_spec,
                            'drawn_length_mm': parts.route_wire(external_spec).Length(),
                            'changed_scope_bounds_mm': bounds(external_tail)},
        'printed_contacts': {}, 'native_neighbors': [], 'intersections': [],
        'qualification_limits': [
            'The upper2.4mm cover is a dry fitting restraint beneath the PCB, not an enclosure ceiling or a fluid-pressure wall.',
            'Upward capture transfers through the broad cover into the pocket walls/lid; no pull-force or lifetime capacity is established.',
            'The original2mm cup floor remains around the lower reservoir stem. Mask the dry fitting pockets/link during the clamped foam pour; dry mating faces are not foam or vapor seals.',
            'The lid retains its flat underside-down print frame and saved Tree(auto)/Default support decisions. Geometric access does not qualify support removal or physical print thickness.',
            'Saved native lead bodies and approach witnesses retain their explicitly named source scope. No whole-appliance replay or flexible handling claim is inferred.'],
    }
    for name, shape in {**fittings, 'reservoir-b-fill-link': link, 'tube-fluid-24-tail': external_tail}.items():
        record['printed_contacts'][name] = {'cup': contact(shape, cup), 'lid': contact(shape, lid)}
    pcb = layout.place(parts.native_reference('pcba'), 'pcba')
    record['PCB'] = {'cup': contact(cup, pcb), 'lid': contact(lid, pcb),
                     'upper_fitting': contact(fittings['reservoir-b-fill-upper'], pcb)}
    upper_air = features['upper_horizontal_air'].BoundingBox()
    upper_top = features['upper_cover_top_z_mm']
    cover_probe = box((upper_air.xmin, upper_air.ymin, upper_air.zmax),
                      (upper_air.xmax, upper_air.ymax, upper_top))
    upper_frame = data['parts']['reservoir-b-fill-upper']['frame']
    outlet_probe = cq.Solid.makeCylinder(8.35, 60., cq.Vector(
        *upper_frame['translation_mm'][:2], 220.))
    cover_probe = cover_probe.cut(outlet_probe)
    lower_air = features['lower_air'].BoundingBox()
    lower_probe = box((lower_air.xmin, lower_air.ymin, lower_air.zmax),
                      (lower_air.xmax, lower_air.ymax, data['roof_top_z_mm']))
    floor_top = layout.cap_lid_pose()['translation_mm'][2]-height+core.cap_shell_clearance+2.
    floor_band = box((-100., 180., floor_top-2.), (100., 467., floor_top-1.e-6))
    record['stock'] = {
        'upper_cover_thickness_mm': data['upper_cover_thickness_mm'],
        'upper_cover_top_world_z_mm': upper_top,
        'upper_cover_missing_mm3': volume(cover_probe.cut(lid)),
        'lower_cover_thickness_mm': data['roof_top_z_mm']-lower_air.zmax,
        'lower_cover_missing_mm3': volume(lower_probe.cut(lid)),
        'original_floor_removed_mm3': volume(old_cup.cut(cup).intersect(floor_band)),
    }
    record['upward_capture'] = {str(dz): contact(
        fittings['reservoir-b-fill-upper'].translate((0., 0., dz)), lid)
        for dz in (0., .15, .2)}
    targets = json.loads(args.hardware_index.read_text())
    paths = {name: args.hardware_index.parent/'targets'/path
             for name, path in targets['parts'].items()}
    wire_index = json.loads(args.wire_index.read_text())
    paths.update({name: Path(path) for name, path in wire_index['parts'].items()})
    overlay = json.loads(args.wire_overlay.read_text())
    paths.update({name: ROOT/row['path'] for name, row in overlay['bodies'].items()})
    direct = json.loads(args.direct_j13.read_text())
    paths.update({name: ROOT/row['path'] for name, row in direct['bodies'].items()})
    wiring_manifest = ROOT/'hardware/wiring/enclosure-wiring.json'
    active_wires = {'wire-'+row['id'] for row in json.loads(wiring_manifest.read_text())['routes']}
    paths = {name: path for name, path in paths.items()
             if not name.startswith('wire-') or name in active_wires}
    # Current route and ground fixtures replace only their named old leaves.
    paths['tube-fluid-14'] = ROOT/'tmp/reservoir-a-free-final/fluid-14.brep'
    paths['tube-fluid-16'] = ROOT/'tmp/reservoir-a-free-final/fluid-16.brep'
    paths['ground-stack'] = ROOT/'tmp/reservoir-a-ground-native/ground-stack.brep'
    obsolete = {'foam-cap-lid-top', 'foam-cap-top', 'reservoir-b-fill-lower',
                'reservoir-b-fill-upper', 'tube-fluid-24', 'pump-contact-female',
                'pump-contact-male', 'nominal-strip-va-east-turn'}
    record['fixture_inputs_sha256'] = {str(path.relative_to(ROOT)): sha(path) for path in (
        args.hardware_index, args.wire_index, args.wire_overlay, args.direct_j13,
        wiring_manifest, args.ports,
        HERE/'foam-cap-top.step', HERE/'foam-cap-lid-top.step')}
    record['targets_considered'] = len(paths)-len(obsolete.intersection(paths))
    for name, path in paths.items():
        if name in obsolete or 'pogo' in name:
            continue
        other = cq.Shape.importBrep(str(path))
        possible = [(subject, shape) for subject, shape in subjects.items() if nearby(shape, other)]
        if not possible:
            continue
        for subject, shape in possible:
            reading = {'subject': subject, 'target': name, 'target_sha256': sha(path),
                       **contact(shape, other)}
            record['native_neighbors'].append(reading)
            if reading['overlap_mm3'] > .001:
                record['intersections'].append(reading)
        print('Local target '+name, flush=True)
    for name, shape in {**subjects, 'cup-world': cup, 'lid-world': lid,
                        'tube-fluid-24': external}.items():
        shape.exportBrep(str(args.cache/(name+'.brep')))
    (args.cache/'fluid-24-specification.json').write_text(json.dumps(external_spec, indent=2)+'\n')
    record['native_candidate_count'] = len(record['native_neighbors'])
    record['access_witness_contacts'] = [row for row in record['intersections']
                                       if row['target'].startswith('access-')]
    record['physical_intersections'] = [row for row in record['intersections']
                                        if not row['target'].startswith('access-')]
    record['physical_layout_native_passed'] = (not record['physical_intersections']
        and record['cup']['valid'] and record['lid']['valid']
        and record['cup']['solids'] == record['lid']['solids'] == 1
        and record['stock']['upper_cover_missing_mm3'] < .001
        and record['stock']['lower_cover_missing_mm3'] < .001
        and record['PCB']['cup']['overlap_mm3'] < .001
        and record['PCB']['lid']['overlap_mm3'] < .001)
    record['source_native_passed'] = (record['physical_layout_native_passed']
                                      and not record['access_witness_contacts'])
    refine_service_scope(record, args.hardware_index, args.cache)
    args.output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'source_native_passed': record['source_native_passed'],
                     'stock': record['stock'], 'PCB': record['PCB'],
                     'intersections': record['intersections'],
                     'candidate_count': record['native_candidate_count']}, indent=2), flush=True)


if __name__ == '__main__':
    main()
