"""Manual native old/new stock comparison appended to the original path reading."""
from pathlib import Path
import argparse
import json

import review as r


def read_native(path):
    identity = r.sha(path)
    shape = r.import_step(path).val()
    if r.sha(path) != identity:
        raise RuntimeError(f'Native part changed during its read: {path}')
    return shape, dict(path=r.path_label(path), sha256=identity)


def delta(old, new):
    return new.cut(old), old.cut(new)


def common_volume(shape, region):
    return r.volume(shape.intersect(region)) if shape.Solids() else 0.


def solid_bounds(shape):
    return r.shape_bounds(shape) if shape.Solids() else None


def retainer_reading(reading, old_path, new_path):
    old, old_id = read_native(old_path)
    new, new_id = read_native(new_path)
    expected = reading['sources']['hardware/printed-parts/enclosure/enclosure/enclosure-pump-retainer.step']
    if old_id['sha256'] != expected:
        raise RuntimeError('Retainer baseline differs from the original path-query input')
    added, removed = delta(old, new)
    land = reading['datums']['flange_z'] - r.enc._tray.skirt_depth
    under = r.enc._ybox(-150., 150., 0., 120., 100., land)
    below_change = common_volume(added, under) + common_volume(removed, under)
    columns = []
    radius = max(r.enc.head_cbore_dia / 2., r.enc.screw_clear_dia / 2.) + r.enc.wall
    d = reading['datums']
    for station in reading['fasteners']:
        guard = r.cq.Solid.makeCylinder(radius, d['retainer_top_z'] - d['bottom_z'] + 2.,
            r.cq.Vector(station['x'], station['y'], d['bottom_z'] - 1.))
        columns.append(dict(x=station['x'], y=station['y'], radius_mm=radius,
            changed_volume_mm3=common_volume(added, guard) + common_volume(removed, guard)))
    result = dict(part='enclosure-pump-retainer', original_native=old_id,
        refined_native=new_id, valid=new.isValid(), solids=len(new.Solids()),
        added_volume_mm3=r.volume(added), removed_volume_mm3=r.volume(removed),
        removed_bounds_mm=r.shape_bounds(removed), protected_land_z_mm=land,
        changed_volume_below_land_mm3=below_change, screw_column_guards=columns,
        original_path_scope='The refined retainer is a native subset of the original. '
            'All material below the skirt land and around the three screw columns agrees. '
            'Previously proved paths against the original retainer remain conservative.')
    if (not result['valid'] or result['solids'] != 1 or result['added_volume_mm3'] > r.VOLUME_FLOOR
            or below_change > r.VOLUME_FLOOR
            or any(row['changed_volume_mm3'] > r.VOLUME_FLOOR for row in columns)):
        raise RuntimeError(f'Retainer refinement needs further review: {result}')
    return result


def front_reading(reading, old_path, new_path, retainer_path):
    old, old_id = read_native(old_path)
    new, new_id = read_native(new_path)
    expected = reading['sources']['hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step']
    if old_id['sha256'] != expected:
        raise RuntimeError('Front-top baseline differs from the original path-query input')
    retainer, retainer_id = read_native(retainer_path)
    added, removed = delta(old, new)
    hardware, cache = r.native_hardware(r.ROOT / 'hardware/manifold-layout/enclosure-assembly.step',
        reading['native_hardware_cache']['assembly_sha256'])
    box, _ = r._box_spec.read(r.enc.Box, r.enc.Bound,
                             (r.enc.Pack, r.enc.PortField, r.enc.Nameplate))
    d = reading['datums']
    pump_names = [f'pump-{pump}-{part}' for pump in ('a', 'b')
                  for part in ('head', 'boss', 'motor')]
    stub_ids = [cid for cid, _a, _b, how in r.manifold.SEGMENTS if how in r.manifold.BARB_OF]
    unit = {'enclosure-pump-retainer': retainer,
            **{name: hardware[name] for name in pump_names},
            **{f'tube-fluid-{cid}': hardware[f'tube-fluid-{cid}'] for cid in stub_ids}}
    casings = {f'declared-casing-x{x:g}': r.cq.Solid.makeCylinder(
        r.enc._tray.fitting_w / 2., 4.305,
        r.cq.Vector(x, d['head_y'] + 27., z), r.cq.Vector(0., 1., 0.))
        for x, z in box.pack.collet_plate['holes']}
    fixed = {'added-front-top-stock': added}
    loading = r.translation('Added front stock vs complete motor-first unit', unit, fixed, (0., 0., -130.))
    casing_path = r.translation('Added front stock vs declared casing loading', casings, fixed, (0., 0., -130.))
    group_names = {'tee-' + name.lower() for name in r.manifold.PUMP_JUNCTIONS}
    group_names.update(f'{part}-v-{valve}' for part in ('valve', 'coil') for valve in ('e', 'f', 'h', 'i'))
    group_names.update(f'tube-fluid-{cid}' for cid, _a, _b, how in r.manifold.SEGMENTS if how.startswith('fore-'))
    groups = {name: hardware[name] for name in group_names}
    fore_path = r.translation('Added front stock vs full prepared fore groups', groups, fixed,
        (0., reading['tee_group_approaches']['conservative_test_travel_mm'], 0.))
    lower = {name: hardware[name] for name in ('enclosure-front-bottom', 'compressor',
             'condenser+fan', 'fuse-clamp', 'mq6-sensor')}
    travel = reading['changed_mount_chassis_slide']['total_travel_mm']
    closure = r.translation('Added front stock rides aft over lower assembly', fixed, lower, (0., -travel, 0.))
    takeup = [dict(rise_z_mm=rise, contacts=r.contacts(
        {name: shape.translate((0., 0., rise)) for name, shape in unit.items()}, fixed))
        for rise in (0., .4)]
    neighbors = r.contacts(fixed, {name: hardware[name] for name in ('display', 'funnel-frame')})
    drivers = []
    for station in reading['fasteners']:
        tool = r.cq.Solid.makeCylinder(1.75, 70.,
            r.cq.Vector(station['x'], station['y'], station['head_seat_z'] - 70.))
        drivers.append(dict(x=station['x'], y=station['y'],
                            contacts=r.contacts({'driver-shaft': tool}, fixed)))
    guard_z = max(f['pilot_end_z'] for f in reading['fasteners'])
    guard_z = max(guard_z, d['flange_z'] + r.enc._tray.boss_depth + .4)
    bearing_guard = r.enc._ybox(-150., 150., 0., 230., 100., guard_z)
    protected_change = common_volume(added, bearing_guard) + common_volume(removed, bearing_guard)
    result = dict(part='enclosure-front-top', original_native=old_id, refined_native=new_id,
        moving_retainer=retainer_id, hardware_cache=cache, valid=new.isValid(), solids=len(new.Solids()),
        added_volume_mm3=r.volume(added), removed_volume_mm3=r.volume(removed),
        added_bounds_mm=solid_bounds(added), removed_bounds_mm=solid_bounds(removed),
        bearing_and_screw_guard_top_z_mm=guard_z, changed_volume_in_bearing_and_screw_guard_mm3=protected_change,
        added_stock_pump_loading=loading, added_stock_casing_loading=casing_path,
        added_stock_fore_groups=fore_path, added_stock_chassis_slide=closure,
        added_stock_takeup=takeup, added_stock_display_and_funnel_contacts=neighbors,
        added_stock_driver_columns=drivers, current_wiring_passages=r.mount.wiring_passages(r.enc, box),
        scope='Original complete path receipts remain bound to their actual old native parts. '
            'Removed stock cannot introduce a rigid collision. Added stock is tested here '
            'against the complete rigid loading unit, fore groups and applicable installed neighbors. '
            'Wire/Faston fit retains its separate native wiring review and physical limits.')
    paths = (loading, casing_path, fore_path, closure)
    if (not result['valid'] or result['solids'] != 1 or protected_change > r.VOLUME_FLOOR
            or any(path['status'] != 'clear_continuous_native_distance_intervals' for path in paths)
            or any(row['contacts'] for row in takeup + drivers) or neighbors):
        raise RuntimeError(f'Front-top refinement needs further review: {result}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reading', type=Path, default=r.HERE / 'native-review.json')
    parser.add_argument('--old-directory', type=Path, default=Path('/tmp/pump-mount-before-lint-fix'))
    parser.add_argument('--stage', choices=('retainer', 'front-top', 'all'), default='all')
    args = parser.parse_args()
    reading_sha = r.sha(args.reading)
    reading = json.loads(args.reading.read_text())
    results = []
    if args.stage in ('retainer', 'all'):
        results.append(retainer_reading(reading,
            args.old_directory / 'enclosure-pump-retainer.step', r.ENC / 'enclosure-pump-retainer.step'))
    if args.stage in ('front-top', 'all'):
        results.append(front_reading(reading,
            args.old_directory / 'enclosure-front-top.step', r.ENC / 'enclosure-front-top.step',
            r.ENC / 'enclosure-pump-retainer.step'))
    reading.setdefault('printed_stock_refinements', []).append(dict(
        verification_source_sha256=r.sha(Path(__file__).resolve()),
        prior_reading_sha256=reading_sha, status='native_refinement_clear', parts=results))
    temporary = args.reading.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(reading, indent=2) + '\n')
    temporary.replace(args.reading)
    print(args.reading, flush=True)


if __name__ == '__main__':
    main()
