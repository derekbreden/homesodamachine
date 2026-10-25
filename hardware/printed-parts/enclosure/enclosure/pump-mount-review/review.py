"""Manual native assembly reading for the integral pump mount.

Run explicitly after exporting the enclosure and appliance. This file is not called
by a build, hook or scorecard. Native minimum-distance intervals bound complete
translations; a zero gap stops that bound instead of being stepped over.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import os
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
ENC = HERE.parent
for directory in (ROOT / 'hardware/scripts', ROOT / 'hardware/manifold-layout', ENC):
    sys.path.insert(0, str(directory))

# This reader exports no CAD and must not serialize unrelated generators.
os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
import _box_spec
from _cadq_export import import_assembly, import_step
import _fixed_pump_mount as mount
import enclosure as enc
import manifold_layout as manifold

DISTANCE_MARGIN = 1e-5
VOLUME_FLOOR = 1e-6


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_label(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def shape_bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def compound(bodies):
    return cq.Compound.makeCompound(list(bodies.values()))


def native_hardware(path, source_sha):
    """Cache only the named native inputs, retaining their original assembly hash."""
    cache = ROOT / '.cache/pump-mount-review' / source_sha
    index_path = cache / 'index.json'
    if index_path.exists():
        index = json.loads(index_path.read_text())
        bodies = {}
        for name, row in index['bodies'].items():
            native = cache / row['file']
            if sha(native) != row['sha256']:
                raise RuntimeError(f'Native cache changed: {native}')
            bodies[name] = cq.Shape.importBrep(str(native))
        print(f'Read {len(bodies)} cached native bodies from {source_sha}', flush=True)
        return bodies, dict(assembly_sha256=source_sha, index_sha256=sha(index_path),
                            cache_directory=str(cache.relative_to(ROOT)), **index)
    print(f'Reading native hardware from {path}', flush=True)
    native = {name: shape for name, (shape, _colour) in import_assembly(path).items()}
    if sha(path) != source_sha:
        raise RuntimeError(f'{path} changed during its native read')
    stubs = {cid for cid, _a, _b, how in manifold.SEGMENTS if how in manifold.BARB_OF
             or how.startswith('fore-')}
    wanted = {f'pump-{pump}-{part}' for pump in ('a', 'b')
              for part in ('head', 'boss', 'motor')}
    wanted.update(f'{part}-v-{valve}' for valve in ('e', 'f', 'h', 'i')
                  for part in ('valve', 'coil'))
    wanted.update('tee-' + tee.lower() for tee in manifold.PUMP_JUNCTIONS)
    wanted.update(f'tube-fluid-{cid}' for cid in stubs)
    wanted.update(('display', 'funnel-frame', 'enclosure-front-bottom', 'compressor',
                   'condenser+fan', 'fuse-clamp', 'mq6-sensor'))
    bodies = {name: native[name] for name in sorted(wanted)}
    cache.mkdir(parents=True, exist_ok=True)
    index = dict(original_assembly=path_label(path), bodies={})
    for name, shape in bodies.items():
        target = cache / (name + '.brep')
        shape.exportBrep(str(target))
        index['bodies'][name] = dict(file=target.name, sha256=sha(target),
            bounds_world_mm=shape_bounds(shape), volume_mm3=volume(shape))
    index_path.write_text(json.dumps(index, indent=2) + '\n')
    print(f'Cached {len(bodies)} named native bodies before querying', flush=True)
    return bodies, dict(assembly_sha256=source_sha, index_sha256=sha(index_path),
                        cache_directory=str(cache.relative_to(ROOT)), **index)


def box_gap(a, b):
    return math.sqrt(sum(max(0., a[i] - b[i + 1], b[i] - a[i + 1]) ** 2
                         for i in (0, 2, 4)))


def contacts(moving, fixed):
    found = []
    for name, shape in moving.items():
        bounds = shape_bounds(shape)
        for other_name, other in fixed.items():
            if box_gap(bounds, shape_bounds(other)) > DISTANCE_MARGIN:
                continue
            common = shape.intersect(other)
            shared = volume(common)
            if shared > VOLUME_FLOOR:
                found.append(dict(moving=name, fixed=other_name,
                                  overlap_mm3=shared,
                                  bounds_world_mm=shape_bounds(common)))
    return found


def translation(label, moving, fixed, start, spatial_margin=None):
    """Cover a translation with native gap-bounded intervals, ending at installed pose.

    A rigid translation shorter than the current solid-to-solid distance cannot
    contact the other solid anywhere in that interval. The margin retreats from
    the kernel reading. No minimum stride bridges a zero gap or unresolved contact.
    """
    start = tuple(float(v) for v in start)
    length = math.sqrt(sum(v * v for v in start))
    moving_shape = compound(moving)
    domain = None
    if spatial_margin is not None:
        b = shape_bounds(moving_shape)
        swept = [b[i] + min(0., start[i // 2]) if i % 2 == 0
                 else b[i] + max(0., start[i // 2]) for i in range(6)]
        expanded = [value + (-spatial_margin if i % 2 == 0 else spatial_margin)
                    for i, value in enumerate(swept)]
        region = cq.Solid.makeBox(*(expanded[i + 1] - expanded[i] for i in (0, 2, 4)),
                                 cq.Vector(*(expanded[i] for i in (0, 2, 4))))
        active = {}
        for name, shape in fixed.items():
            if box_gap(expanded, shape_bounds(shape)) > 0.:
                continue
            pieces = shape.intersect(region).Solids()
            if pieces:
                active[name] = cq.Compound.makeCompound(pieces)
        fixed_query = active
        domain = dict(swept_bounds_mm=swept, expanded_query_bounds_mm=expanded,
                      outside_domain_clearance_lower_bound_mm=spatial_margin,
                      queried_fixed_bodies=list(active))
    else:
        fixed_query = fixed
    fixed_shape = compound(fixed_query)
    print(f'{label}: native interval reading starts', flush=True)
    travelled = 0.
    intervals = []
    started = time.monotonic()
    for _iteration in range(3000):
        fraction = travelled / length if length else 1.
        offset = tuple(v * (1. - fraction) for v in start)
        placed = moving_shape.translate(offset)
        native_gap = placed.distance(fixed_shape) if fixed_query else None
        gap = (min(native_gap, spatial_margin) if native_gap is not None else spatial_margin
               ) if spatial_margin is not None else native_gap
        remaining = length - travelled
        row = dict(travelled_mm=travelled, remaining_mm=remaining,
                   offset_mm=offset, native_gap_mm=native_gap, proved_gap_bound_mm=gap)
        intervals.append(row)
        if _iteration < 3 or _iteration % 100 == 0:
            print(f'  {label}: remaining {remaining:.6g}, gap bound {gap:.6g}', flush=True)
        if remaining <= 1e-9:
            status = 'clear_continuous_native_distance_intervals'
            break
        if gap <= 2. * DISTANCE_MARGIN:
            status = 'unresolved_zero_or_terminal_gap'
            break
        step = min(remaining, .9 * (gap - DISTANCE_MARGIN))
        row['proved_next_interval_mm'] = step
        travelled += step
    else:
        status = 'interval_limit_reached'
    stopped = {name: shape.translate(offset) for name, shape in moving.items()}
    stopped_contacts = contacts(stopped, fixed)
    final_contacts = contacts(moving, fixed)
    closest_pairs = []
    if status != 'clear_continuous_native_distance_intervals':
        for name, shape in stopped.items():
            bounds = shape_bounds(shape)
            for other_name, other in fixed.items():
                if box_gap(bounds, shape_bounds(other)) > .01:
                    continue
                pair_gap = shape.distance(other)
                if pair_gap < .01:
                    closest_pairs.append(dict(moving=name, fixed=other_name,
                                               native_gap_mm=pair_gap))
    if stopped_contacts or final_contacts:
        status = 'native_interference'
    result = dict(label=label, status=status, start_offset_mm=start,
                  distance_margin_mm=DISTANCE_MARGIN,
                  proved_travel_mm=travelled, total_travel_mm=length,
                  unproved_final_mm=max(0., length - travelled),
                  minimum_read_gap_mm=min(row['proved_gap_bound_mm'] for row in intervals),
                  interval_count=len(intervals), intervals=intervals,
                  stopped_contacts=stopped_contacts, final_contacts=final_contacts,
                  closest_pairs_at_stop=closest_pairs,
                  moving_bodies=list(moving), fixed_bodies=list(fixed),
                  spatial_query_domain=domain,
                  elapsed_seconds=time.monotonic() - started)
    print(f"{label}: {status}; {len(intervals)} intervals; "
          f"{result['unproved_final_mm']:.6g} mm unproved", flush=True)
    return result


def fore_group_motion(front, assembly, loading_unit, box):
    """Straight prepared-group approach, with explicit post mates separated.

    The four round posts nominally touch their sockets. Their full axial swept
    cylinders are queried natively. All other valve material, including the port
    barrel below the bearing plane, remains in the complete-front-top distance query.
    """
    ids = {how: cid for cid, _a, _b, how in manifold.SEGMENTS if how in manifold.BARB_OF}
    valves, port_bellies, tee_links, post_sweeps, rows = {}, {}, {}, {}, []
    post_source = enc._valve_tray._valve
    required_travel = enc._dock.tee.BRANCH_INSERTION_EXTENDED
    travel = max(required_travel, enc._dock.tee.RUN_INSERTION_EXTENDED)
    bearing_plane = None
    for _station, tee, x, _z in enc._dock.stations(box.pack.collet_plate):
        valve = manifold.PUMP_VALVES[tee][0].lower()
        body_name, coil_name = 'valve-' + valve, 'coil-' + valve
        body = assembly[body_name]
        b = shape_bounds(body)
        plane = b[2] + post_source.bearing_z_range[0]
        if bearing_plane is not None and abs(bearing_plane - plane) > DISTANCE_MARGIN:
            raise ValueError('Fore valves do not share one mounting plane')
        bearing_plane = plane
        centre_z = (b[4] + b[5]) / 2.
        pins = []
        for sx in (-1., 1.):
            for sz in (-1., 1.):
                px = x + sx * post_source.corner_inset_x
                pz = centre_z + sz * post_source.corner_inset_y
                pins.append(cq.Solid.makeCylinder(post_source.corner_boss_radius,
                    plane - b[2], cq.Vector(px, b[2], pz), cq.Vector(0., 1., 0.)))
                post_sweeps[f'{body_name}-post-{sx:g}-{sz:g}'] = cq.Solid.makeCylinder(
                    post_source.corner_boss_radius, plane - b[2] + travel,
                    cq.Vector(px, b[2], pz), cq.Vector(0., 1., 0.))
        pin_mask = cq.Compound.makeCompound(pins)
        free = body.cut(pin_mask)
        omitted = body.cut(free)
        unexpected = volume(omitted.cut(pin_mask))
        if unexpected > VOLUME_FLOOR:
            raise ValueError(f'{body_name}: {unexpected:g} mm3 outside declared post mates')
        above = cq.Solid.makeBox(500., 500., 500., cq.Vector(-250., plane, 0.))
        valves[body_name + '-above-bearing'] = cq.Compound.makeCompound(
            free.intersect(above).Solids())
        port_bellies[body_name + '-port-belly'] = cq.Compound.makeCompound(
            free.cut(above).Solids())
        valves[coil_name] = assembly[coil_name]
        upper_id = next(cid for cid, _a, _b, how in manifold.SEGMENTS
                        if how == 'fore-' + tee.lower())
        tee_links['tee-' + tee.lower()] = assembly['tee-' + tee.lower()]
        tee_links[f'tube-fluid-{upper_id}'] = assembly[f'tube-fluid-{upper_id}']
        rows.append(dict(tee=tee, valve=body_name, x=x, bearing_plane_y_mm=plane,
                         post_leading_y_mm=b[2], post_length_mm=plane - b[2],
                         unexpected_omitted_material_mm3=unexpected,
                         expected_mating_tube=f'tube-fluid-{ids[tee]}'))
    fixed_other = {name: shape for name, shape in loading_unit.items()
                   if not name.startswith('tube-fluid-')}
    aft_region = cq.Solid.makeBox(500., 500., 500., cq.Vector(-250., bearing_plane, 0.))
    aft_front = cq.Compound.makeCompound(front.intersect(aft_region).Solids())
    valve_paths = []
    belly_paths = []
    for row in rows:
        names = (row['valve'] + '-above-bearing', row['valve'].replace('valve-', 'coil-'))
        valve_paths.append(translation(row['valve'] + ': axial body and coil approach',
            {name: valves[name] for name in names},
            {'front-top-aft-of-bearing': aft_front, **fixed_other},
            (0., travel, 0.), spatial_margin=2.))
        belly_name = row['valve'] + '-port-belly'
        belly_paths.append(translation(row['valve'] + ': axial port-belly approach',
            {belly_name: port_bellies[belly_name]},
            {'enclosure-front-top': front, **fixed_other},
            (0., travel, 0.), spatial_margin=2.))
    tee_path = translation('Four prepared tees and upper links: axial approach', tee_links,
        {'enclosure-front-top': front, **fixed_other}, (0., travel, 0.))
    pin_contacts = contacts(post_sweeps, {'enclosure-front-top': front})
    full_groups = {**tee_links,
        **{name: assembly[name] for row in rows
           for name in (row['valve'], row['valve'].replace('valve-', 'coil-'))}}
    final_contacts = contacts(full_groups, {'enclosure-front-top': front, **fixed_other})
    group_x = []
    for row in rows:
        tee = row['tee']
        names = ['tee-' + tee.lower(), row['valve'],
                 row['valve'].replace('valve-', 'coil-')]
        upper_id = next(cid for cid, _a, _b, how in manifold.SEGMENTS
                        if how == 'fore-' + tee.lower())
        names.append(f'tube-fluid-{upper_id}')
        bounds = shape_bounds(compound({name: assembly[name] for name in names}))
        group_x.append(dict(tee=tee, x_min_mm=bounds[0], x_max_mm=bounds[1]))
    group_x.sort(key=lambda row: row['x_min_mm'])
    group_gaps = [dict(left=a['tee'], right=b['tee'], gap_mm=b['x_min_mm']-a['x_max_mm'])
                  for a, b in zip(group_x, group_x[1:])]
    if any(row['gap_mm'] <= 0. for row in group_gaps):
        raise ValueError('Prepared group transverse envelopes are not separated')
    other_stub_gaps = []
    for row in group_x:
        for name, stub in loading_unit.items():
            if not name.startswith('tube-fluid-') or name == next(
                    r['expected_mating_tube'] for r in rows if r['tee'] == row['tee']):
                continue
            b = shape_bounds(stub)
            gap = max(row['x_min_mm'] - b[1], b[0] - row['x_max_mm'])
            if gap <= 0.:
                raise ValueError('Prepared group and non-mating stub X envelopes overlap')
            other_stub_gaps.append(dict(tee=row['tee'], non_mating_stub=name, gap_mm=gap))
    return dict(required_branch_engagement_mm=required_travel,
        conservative_test_travel_mm=travel, fore_groups=rows,
        bearing_plane_y_mm=bearing_plane,
        intended_post_socket_contact='Four Ø6.9 native post sweeps per valve. '
            'Only the four post cylinders below the bearing plane are removed '
            'from the separate body-distance query. Body material at or aft of '
            'the bearing plane is queried against all fixed solids aft of that '
            'plane. It is separated from all fore-side stock for positive approach '
            'offset and can meet its bearing faces only at the terminal plane. '
            'The remaining native port belly below that plane is queried against '
            'the complete quadrant.',
        body_and_coil_translations=valve_paths, tee_and_link_translation=tee_path,
        port_belly_translations=belly_paths,
        complete_post_sweep_contacts=pin_contacts, final_native_contacts=final_contacts,
        group_x_envelopes=group_x, transverse_group_gaps=group_gaps,
        non_mating_stub_transverse_gaps=other_stub_gaps,
        sequential_group_scope='The groups have disjoint transverse X envelopes, '
            'so their relative Y offsets cannot create an inter-group collision. '
            'Fit all four groups before the rear valve row.',
        rear_row_installed_during_approach=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assembly', type=Path,
                        default=ROOT / 'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--out', type=Path, default=HERE / 'native-review.json')
    parser.add_argument('--query', choices=('all', 'front-plumbing', 'static'), default='all')
    parser.add_argument('--hardware-cache-sha256',
                        help='Read a retained native subset from this original aggregate hash')
    parser.add_argument('--candidate-wago', action='store_true',
                        help='Reconstruct only the canonical manifold-WAGO tower for a prospective local query')
    args = parser.parse_args()
    box, _ = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate))
    datums, fasteners = mount.datums(enc, box), mount.fasteners(enc, box)
    front_path = ENC / 'enclosure-front-top.step'
    retainer_path = ENC / 'enclosure-pump-retainer.step'
    sources = [Path(__file__).resolve(), front_path, retainer_path,
               ROOT / 'hardware/manifold-layout/enclosure-box.json',
               ENC / 'enclosure.py', ENC / '_fixed_pump_mount.py',
               ENC / '_above_core_shell.py', ROOT / 'hardware/manifold-layout/above_core_wiring.py',
               ROOT / 'hardware/reference/kamoer-kphm400/kamoer_kphm400.py',
               ROOT / 'hardware/printed-parts/enclosure/pump-tray/pump_tray.py']
    if args.hardware_cache_sha256:
        index = ROOT / '.cache/pump-mount-review' / args.hardware_cache_sha256 / 'index.json'
        if not index.exists():
            raise RuntimeError('The explicitly requested native subset is not retained')
        sources.append(index)
    else:
        sources.append(args.assembly)
    input_hashes = {path_label(path): sha(path) for path in sources}
    front = import_step(front_path).val()
    retainer = import_step(retainer_path).val()
    assembly, hardware_cache = native_hardware(args.assembly,
        args.hardware_cache_sha256 or input_hashes[path_label(args.assembly)])
    for native in (front_path, retainer_path) + (() if args.hardware_cache_sha256 else (args.assembly,)):
        if sha(native) != input_hashes[path_label(native)]:
            raise RuntimeError(f'{native} changed during its native read')
    prospective = None
    if args.candidate_wago:
        import above_core_wiring as electrical
        import _above_core_shell as shell_hosts
        features = electrical.shell_features('front-top')
        tower = shell_hosts.stacked_well_towers(features['add'], box.inner)
        # The region contains the two named WAGO wells, their one full-width
        # tower and ordinary flat flank. It lies ahead of the Y-seam furniture.
        region = cq.Solid.makeBox(12.45, 31.05, 79.65,
                                  cq.Vector(95.05, 157.95, 215.4))
        flank = cq.Solid.makeBox(9., 31.05, 79.65,
                                 cq.Vector(98.5, 157.95, 215.4))
        front = front.cut(region).fuse(flank, tower).cut(features['cut']).clean()
        prospective = dict(method='Native seed quadrant with the named WAGO tower and '
            'ordinary flank region reconstructed from canonical source; this is a '
            'prospective assembly query, not the exported production quadrant.',
            wago_poses={name: electrical.placements()[name]
                        for name in ('wago-mana', 'wago-manb')},
            region_bounds_mm=shape_bounds(region), source_seed=input_hashes[str(front_path.relative_to(ROOT))])
    pump_names = [f'pump-{p}-{part}' for p in ('a', 'b')
                  for part in ('head', 'boss', 'motor')]
    stub_ids = {how: cid for cid, _start, _end, how in manifold.SEGMENTS
                if how in manifold.BARB_OF}
    stub_names = [f'tube-fluid-{cid}' for cid in stub_ids.values()]
    pumps = {name: assembly[name] for name in pump_names}
    stubs = {name: assembly[name] for name in stub_names}
    loading_unit = {'enclosure-pump-retainer': retainer, **pumps, **stubs}
    partial = dict(sources=input_hashes, native_hardware_cache=hardware_cache,
                   status='manual_reading_in_progress', requested_query=args.query)

    def checkpoint(key, value):
        partial[key] = value
        args.out.with_suffix('.progress.json').write_text(json.dumps(partial, indent=2) + '\n')

    path = (translation('Prepared pumps and retainer enter from below', loading_unit,
                        {'enclosure-front-top': front}, (0., 0., -130.))
            if args.query == 'all' else None)
    checkpoint('pump_loading', path)

    # A declared casing probe supplements the coarse pump-head B-rep. Its diameter
    # is the reference's molded-casing width; its short Y span is a local envelope,
    # not an independently scanned complete casing model.
    casings = {}
    for x, z in box.pack.collet_plate['holes']:
        casings[f'declared-casing-x{x:g}'] = cq.Solid.makeCylinder(
            enc._tray.fitting_w / 2., 4.305,
            cq.Vector(x, datums['head_y'] + 27., z), cq.Vector(0., 1., 0.))
    casing_loading = (translation('Declared casing envelopes enter from below', casings,
                                  {'enclosure-front-top': front}, (0., 0., -130.))
                      if args.query == 'all' else None)
    checkpoint('declared_casing_loading', casing_loading)

    # The loose quadrant leaves a straight tool column below each screw head.
    driver_rows = []
    for station in (fasteners if args.query == 'all' else ()):
        tool = cq.Solid.makeCylinder(1.75, 70.,
            cq.Vector(station['x'], station['y'], station['head_seat_z'] - 70.),
            cq.Vector(0., 0., 1.))
        driver_rows.append(dict(station=station, shaft_diameter_mm=3.5,
            reach_mm=70., contacts=contacts({'driver-shaft': tool},
                {'enclosure-front-top': front, **loading_unit, **casings})))

    tee_paths = (fore_group_motion(front, assembly, loading_unit, box)
                 if args.query != 'static' else None)
    checkpoint('tee_group_approaches', tee_paths)

    # This query covers the changed mount during chassis closure. The shell rail
    # profiles and the existing manifold returns retain their separate records.
    lower = {name: assembly[name] for name in ('enclosure-front-bottom', 'compressor',
             'condenser+fan', 'fuse-clamp', 'mq6-sensor') if name in assembly}
    travel = enc._z_rail_travel(box.inner, box.y_joint, 'front',
                               box.pack.collet_plate, box.pack.vent_chase)
    chassis_path = (translation('Installed pump mount rides aft over the lower assembly',
                                {**loading_unit, **casings}, lower, (0., -travel, 0.))
                    if args.query == 'all' else None)
    neighbors = {name: assembly[name] for name in ('display', 'funnel-frame')
                 if name in assembly}
    neighbor_contacts = contacts({'enclosure-front-top': front,
                                  'enclosure-pump-retainer': retainer}, neighbors)

    takeup = []
    for rise in (0., enc.fits.clearance(supported=True)):
        takeup.append(dict(rise_z_mm=rise, contacts=contacts(
            {name: shape.translate((0., 0., rise)) for name, shape in loading_unit.items()},
            {'enclosure-front-top': front}),
            screw_pilot_tip_reserve_mm=min(f['pilot_end_z'] - f['screw_tip_z'] - rise
                                          for f in fasteners),
            tube_axis_z_mm=[z + rise for _x, z in box.pack.collet_plate['holes']]))
    results = dict(
        scope='Explicit manual native geometry reading. Continuous translations are proved '
              'only for the recorded positive-gap intervals; an unresolved zero gap stops '
              'the bound. Connector boots, hands, flexible wire/tube handling, printed fit, '
              'screw preload, operating retention and lifetime are not qualified.',
        sources=input_hashes, requested_query=args.query,
        native_hardware_cache=hardware_cache,
        prospective_wago_geometry=prospective,
        datums=datums, fasteners=fasteners, wiring_passages=mount.wiring_passages(enc, box),
        printed_parts={name: dict(valid=shape.isValid(), solids=len(shape.Solids()),
                                 volume_mm3=volume(shape), bounds_mm=shape_bounds(shape))
                       for name, shape in (('enclosure-front-top', front),
                                           ('enclosure-pump-retainer', retainer))},
        pump_loading=path, declared_casing_loading=casing_loading,
        casing_probe_scope='Reference Ø12.75 mm cylindrical casing envelope, '
                           'Y=head centre+27 to +31.305. Not a complete scanned casing.',
        underside_driver_columns=driver_rows, tee_group_approaches=tee_paths,
        axial_face_allowance_static=takeup,
        changed_mount_chassis_slide=chassis_path,
        display_and_funnel_static_contacts=neighbor_contacts,
        lower_well_scope='Existing fitted lower well and skirt land retained. '
                         'The earlier firm-holding/no-play report applies to its '
                         'identified cradle and cap, not this revised two-face capture.')
    args.out.write_text(json.dumps(results, indent=2) + '\n')
    print(args.out, flush=True)


if __name__ == '__main__':
    main()
