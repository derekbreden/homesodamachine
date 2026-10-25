"""Manual Reservoir A paired-anchor stock and local-contact reading.

Run through tmp/takeover/cadq. With --apply-delta, the exported input lid is
the actual baseline to which only the two production seats and passages are
applied. Without it, read back the populated production lid. No generator,
hook, recurring check or machine-wide clearance review invokes this script.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
HW = ROOT/'hardware'
sys.path[:0] = [str(HW/path) for path in (
    'printed-parts/cold-core', 'printed-parts/cadlib', 'scripts', 'manifold-layout')]
import _reservoir_a_anchors as anchors
import above_core as layout
import above_core_parts as parts
import above_core_routes as routes
import above_core_wiring as wiring

TOL_MM3 = .001


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def bounds(shape):
    b = shape.BoundingBox()
    return [getattr(b, key) for key in ('xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax')]


def signature(shape):
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
            'faces': len(shape.Faces()), 'volume_mm3': volume(shape),
            'center_mm': list(shape.Center().toTuple()), 'bounds_mm': bounds(shape)}


def nearby(first, second):
    a, b = bounds(first), bounds(second)
    return all(a[i+3] >= b[i] and b[i+3] >= a[i] for i in range(3))


def contact(first, second):
    common = first.intersect(second, tol=1.e-7)
    v = volume(common)
    return {'overlap_mm3': v, 'bounds_mm': bounds(common) if v > TOL_MM3 else None,
            'passed': v < TOL_MM3}


def box(x0, y0, z0, x1, y1, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def printed_stock(path, spec, datums):
    """Finite vertical web/floor readings from the actual printed STL."""
    import numpy as np
    import trimesh
    mesh = trimesh.load_mesh(str(path))
    frame = layout.cap_lid_pose()
    matrix = np.eye(4)
    matrix[:3, :3] = frame['rotation']
    matrix[:3, 3] = frame['translation_mm']
    mesh.apply_transform(matrix)
    result = {'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
        'surface_basis': 'foam_cap.main writes both lids through '
                         '_show_skin.piece_mesh(), the plain source tessellation; '
                         'only the cup branch calls write_bed_file()/fluted(). '
                         'These finite anchor webs/floors do not meet a fluted field.',
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            HERE/'foam_cap.py', HERE.parent/'_show_skin.py')},
        'coordinate_tolerance_mm': 1.e-5, 'readings': []}
    for name, row in datums.items():
        for feature, zmid, minimum in (
            ('seat web', (spec['tie_slot_top_z_mm'] + row['tube_centers_world_mm'][0][2]
                          - spec['seat_radius_mm'])/2, 3.),
            ('slot floor', (spec['root_z_mm']+spec['tie_slot_bottom_z_mm'])/2, 3.)):
            # The seat-web mouth planes meet the outer tube axes. Read just
            # inside the closed web rather than exactly on those open edges.
            inward = (.1, -.1) if feature == 'seat web' else (0., 0.)
            origins = np.array([[p[0]+dx, p[1]+dy, zmid]
                                for p, dx in zip(row['tube_centers_world_mm'], inward)
                                for dy in (-1.2, 0., 1.2)])
            sides = []
            for direction in (1., -1.):
                locations, rays, _ = mesh.ray.intersects_location(
                    origins, np.tile([0., 0., direction], (len(origins), 1)),
                    multiple_hits=True)
                sides.append([min((abs(point[2]-origin[2]) for point, ray in zip(locations, rays)
                                   if ray == i), default=None)
                              for i, origin in enumerate(origins)])
            thickness = [up+down if up is not None and down is not None else None
                         for up, down in zip(*sides)]
            result['readings'].append({'station': name, 'feature': feature,
                'axes_world_mm': origins.tolist(), 'thicknesses_mm': thickness,
                'minimum_required_mm': minimum,
                'passed': all(t is not None and t >= minimum-1.e-5 for t in thickness)})
    result['passed'] = all(row['passed'] for row in result['readings'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lid', type=Path, default=HERE/'foam-cap-lid-top.step')
    parser.add_argument('--apply-delta', action='store_true')
    parser.add_argument('--bind-only', action='store_true',
                        help='Rebind existing seat/tie contacts to the actual lid stock and STL.')
    parser.add_argument('--wire-index', type=Path)
    parser.add_argument('--exclude-wire', action='append', default=[])
    parser.add_argument('--neighbor-index', type=Path)
    parser.add_argument('--neighbor-dir', type=Path)
    parser.add_argument('--neighbor-tubes-only', action='store_true',
                        help='Append only the unchanged cached tube-neighbor contacts.')
    parser.add_argument('--cache', type=Path, default=ROOT/'tmp/reservoir-a-anchor-native')
    parser.add_argument('--output', type=Path, default=HERE/'reservoir-a-anchor-review.json')
    args = parser.parse_args()
    args.lid = args.lid.resolve()
    args.output = args.output.resolve()
    if args.wire_index:
        args.wire_index = args.wire_index.resolve()
    if args.neighbor_tubes_only:
        record = json.loads(args.output.read_text())
        if record['source_sha256'][str(Path(anchors.__file__).relative_to(ROOT))] != sha(Path(anchors.__file__)):
            raise ValueError('Anchor source differs from the saved stock reading.')
        index_path = args.neighbor_index.resolve()
        directory = args.neighbor_dir.resolve()
        index = json.loads(index_path.read_text())
        selected = {**anchors.supports(), **anchors.tie_witnesses()}
        result = {'scope': 'Only the new seats/nominal ties versus cached unchanged tube '
                           'neighbors; selected A14/A16 retain their separate route review.',
                  'index': str(index_path.relative_to(ROOT)), 'index_sha256': sha(index_path),
                  'reader_sha256': sha(Path(__file__)), 'tube_sha256': {}, 'contacts': []}
        for name, relative in index['parts'].items():
            if not name.startswith('tube-') or name in ('tube-fluid-14', 'tube-fluid-16'):
                continue
            path = directory/relative
            other = cq.Shape.importBrep(str(path))
            result['tube_sha256'][name] = sha(path)
            for subject, shape in selected.items():
                if nearby(shape, other):
                    result['contacts'].append({'subject': subject, 'target': name,
                                               **contact(shape, other)})
        result['passed'] = all(row['passed'] for row in result['contacts'])
        record['unchanged_tube_neighbors'] = result
        record['passed'] = (record['stock_passed'] and result['passed']
                            and all(row['passed'] for row in record['contacts']))
        args.output.write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps({'tube_count': len(result['tube_sha256']),
            'candidate_count': len(result['contacts']), 'passed': result['passed'],
            'contacts': [row for row in result['contacts'] if not row['passed']]}), flush=True)
        return
    prior = json.loads(args.output.read_text()) if args.bind_only else None
    args.cache.mkdir(parents=True, exist_ok=True)
    spec, datums = anchors.specification(), anchors.datums()
    seats, cuts, ties = anchors.supports(), anchors.cuts(), anchors.tie_witnesses()
    lid = cq.importers.importStep(str(args.lid)).val().moved(
        layout.frame_location(layout.cap_lid_pose()))
    baseline = signature(lid)
    input_seat_missing = {name: volume(shape.cut(lid)) for name, shape in seats.items()}
    input_passage_stock = {name: volume(lid.intersect(shape)) for name, shape in cuts.items()}
    if all(v<TOL_MM3 for v in (*input_seat_missing.values(), *input_passage_stock.values())):
        args.apply_delta = False
    if args.apply_delta:
        for shape in seats.values():
            lid = lid.fuse(shape)
        for shape in cuts.values():
            lid = lid.cut(shape)
        lid = lid.clean()
    fixtures = {**seats, **ties, 'lid-world': lid}
    index = {'scope': 'World native seat/tie witnesses and actual-lid fixture; ties nominal.',
             'parts': {}, 'source_sha256': {str(Path(anchors.__file__).relative_to(ROOT)):
                                          sha(Path(anchors.__file__))}}
    for name, shape in fixtures.items():
        path = args.cache/(name+'.brep')
        shape.exportBrep(str(path))
        index['parts'][name] = {'path': str(path.resolve()), 'sha256': sha(path),
                                'signature': signature(shape)}
    (args.cache/'index.json').write_text(json.dumps(index, indent=2)+'\n')
    print('World fixture ready: '+str(args.cache/'index.json'), flush=True)

    record = {
        'scope': 'Two selected paired seats and lid passages, actual exported lid stock, '
                 'the two source-native continuous A tubes, selected above-core purchased '
                 'bodies and explicitly supplied cached electrical bodies. No other lid '
                 'feature is requalified. Nominal ties do not establish threading, '
                 'purchased fit, retention or load capacity.',
        'lid_input': {'path': str(args.lid.relative_to(ROOT)), 'sha256': sha(args.lid),
                      'mode': 'actual exported baseline plus only the named anchor delta'
                              if args.apply_delta else 'actual exported populated lid',
                      'baseline_signature': baseline},
        'actual_input_seat_presence': {'missing_mm3': input_seat_missing,
                                      'passage_stock_mm3': input_passage_stock,
                                      'delta_applied': args.apply_delta},
        'source_sha256': {str(path.relative_to(ROOT)): sha(path) for path in (
            Path(__file__), Path(anchors.__file__), HERE/'foam_cap.py',
            Path(routes.__file__), Path(parts.__file__), Path(wiring.__file__),
            HW/'manifold-layout/above-core.json',
            HW/'manifold-layout/reservoir-a-routes.json')},
        'specification': spec, 'datums': datums, 'lid_signature': signature(lid),
        'seats': {}, 'nominal_ties': {}, 'contacts': [], 'stock_checks': [],
        'volume_tolerance_mm3': TOL_MM3,
        'b_fill_scope': 'Unchanged; neither fittings nor their passage/roof are authored here.',
    }
    if prior is not None:
        old_source = prior['source_sha256'][str(Path(anchors.__file__).relative_to(ROOT))]
        if old_source != sha(Path(anchors.__file__)):
            raise ValueError('Anchor source changed; saved contact reading cannot be reused.')
        record['contacts'] = [row for row in prior['contacts'] if row['target'] != 'actual lid']
        record['electrical_cache'] = prior.get('electrical_cache')
        record['retained_contact_scope'] = {
            'record_sha256': sha(args.output),
            'basis': 'Identical paired-seat and nominal-tie source; only actual exported '
                     'lid stock and printed web/floor measurements are refreshed. '
                     'Saved equipment/tube/electrical readings are retained at their original scope.',
            'original_lid_input': prior['lid_input'],
            'original_source_sha256': prior['source_sha256'],
        }
    lid_east = 90.2
    lid_bottom = layout.cap_lid_pose()['translation_mm'][2]
    for name, row in datums.items():
        shape = seats[name]
        first, last = row['tube_centers_world_mm']
        x0, x1 = first[0], last[0]
        y, z = first[1:]
        h = spec['tie_slot_width_y_mm']/2
        seat_bottom = z-spec['seat_radius_mm']
        inner = spec['tie_access_inner_offset_mm']
        witness = box(x0-inner, y-h, spec['tie_slot_top_z_mm'],
                      x1+inner, y+h, seat_bottom)
        missing = volume(witness.cut(lid))
        record['stock_checks'].append({'check': name+' / complete seat floor',
            'thickness_mm': seat_bottom-spec['tie_slot_top_z_mm'],
            'missing_mm3': missing, 'passed': missing<TOL_MM3})
        floor = box(x0-2.75, y-h, lid_bottom, min(x1+2.75, lid_east),
                    y+h, spec['tie_slot_bottom_z_mm'])
        missing = volume(floor.cut(lid))
        record['stock_checks'].append({'check': name+' / slot floor within lid edge',
            'thickness_mm': spec['tie_slot_bottom_z_mm']-lid_bottom,
            'east_edge_world_x_mm': lid_east, 'missing_mm3': missing,
            'passed': missing<TOL_MM3})
        floor = box(x0-2.75, y-h, spec['root_z_mm'], x1+2.75,
                    y+h, spec['tie_slot_bottom_z_mm'])
        missing = volume(floor.cut(lid))
        record['stock_checks'].append({'check': name+' / complete slot floor including overhang',
            'thickness_mm': spec['tie_slot_bottom_z_mm']-spec['root_z_mm'],
            'missing_mm3': missing, 'passed': missing<TOL_MM3})
        lo, hi = row['stock_bounds_mm']
        for side, ya, yb in (('fore', lo[1], y-h), ('aft', y+h, hi[1])):
            root = box(lo[0], ya, spec['root_z_mm'], min(hi[0], lid_east),
                       yb, spec['lid_face_z_mm'])
            missing = volume(root.cut(lid))
            record['stock_checks'].append({'check': name+' / '+side+' lid root',
                'thickness_mm': spec['lid_face_z_mm']-spec['root_z_mm'],
                'missing_mm3': missing, 'passed': missing<TOL_MM3})
        record['seats'][name] = {**signature(shape),
            'missing_from_lid_mm3': volume(shape.cut(lid))}
        points = anchors.tie_profile(row)
        length = sum(math.dist(a, b) for a, b in zip(points, points[1:]+points[:1]))
        tie = ties[name+'-tie']
        record['nominal_ties'][name+'-tie'] = {**signature(tie),
            'closed_piecewise_linear_centerline_length_mm': length,
            'physical_threading_retention_and_load_qualified': False}
        record['contacts'].append({'subject': name+'-tie', 'target': 'actual lid',
                                    **contact(tie, lid)})

    if args.bind_only:
        record['printed_stock'] = printed_stock(args.lid.with_suffix('.stl'), spec, datums)
        finish(record, args.output, lid)
        return
    selected = routes.reservoir_a_route_specs()
    tube_shapes = {name: parts.route_shape(data) for name, data in selected.items()}
    (args.cache/'route-specs.json').write_text(json.dumps(selected, indent=2)+'\n')
    bodies = {name: row[0] for name, row in parts.components().items()}
    bodies.update({name: row[0] for name, row in wiring.components().items()})
    targets = {**bodies, **tube_shapes}
    for subject, shape in {**seats, **ties}.items():
        for target, other in targets.items():
            if nearby(shape, other):
                record['contacts'].append({'subject': subject, 'target': target,
                                            **contact(shape, other)})
    if args.wire_index:
        cache = json.loads(args.wire_index.read_text())
        record['electrical_cache'] = {'path': str(args.wire_index.relative_to(ROOT)),
            'sha256': sha(args.wire_index), 'excluded': args.exclude_wire,
            'body_count': 0, 'candidate_pairs': 0, 'body_sha256': {}}
        for name, item in cache['parts'].items():
            if name in args.exclude_wire or name.removeprefix('wire-') in args.exclude_wire:
                continue
            path = Path(item['path'] if isinstance(item, dict) else item)
            if not path.is_absolute():
                path = args.wire_index.parent/path
            other = cq.Shape.importBrep(str(path))
            record['electrical_cache']['body_count'] += 1
            record['electrical_cache']['body_sha256'][name] = sha(path)
            for subject, shape in {**seats, **ties}.items():
                if nearby(shape, other):
                    record['electrical_cache']['candidate_pairs'] += 1
                    record['contacts'].append({'subject': subject, 'target': name,
                                                **contact(shape, other)})
    if args.lid.with_suffix('.stl').exists():
        record['printed_stock'] = printed_stock(args.lid.with_suffix('.stl'), spec, datums)
    finish(record, args.output, lid)


def finish(record, output, lid):
    record['stock_passed'] = (lid.isValid() and len(lid.Solids())==1
        and all(row['passed'] for row in record['stock_checks'])
        and all(row['valid'] and row['solids']==1 and row['missing_from_lid_mm3']<TOL_MM3
                for row in record['seats'].values())
        and record.get('printed_stock', {}).get('passed', True))
    record['passed'] = (lid.isValid() and len(lid.Solids())==1
        and all(row['passed'] for row in record['stock_checks']+record['contacts'])
        and all(row['valid'] and row['solids']==1 and row['missing_from_lid_mm3']<TOL_MM3
                for row in record['seats'].values())
        and record.get('printed_stock', {}).get('passed', True))
    output.write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({'passed': record['passed'], 'lid': record['lid_signature'],
        'failed_stock': [r for r in record['stock_checks'] if not r['passed']],
        'contacts': [r for r in record['contacts'] if not r['passed']]}), flush=True)


if __name__ == '__main__':
    main()
