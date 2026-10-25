"""Manually read the two source-built meter brackets and complete nominal ties.

The explicit target index binds native purchased, tube, electrical and access
witness BREPs to one recorded scope. It may contain cached prior artifacts;
its own scope must identify changed equipment or wiring separately. This
local reading does not build an appliance or qualify physical tying, printed
strength, insertion force, hand access or lifetime. Run through the CAD queue.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'hardware/manifold-layout'),
               str(ROOT / 'hardware/scripts'),
               str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
               str(ROOT / 'hardware/printed-parts/cold-core')]

import cadquery as cq
import _back_top_meter as meter
import _above_core_mounts as mounts


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    box = shape.BoundingBox()
    return [[box.xmin, box.ymin, box.zmin],
            [box.xmax, box.ymax, box.zmax]]


def nearby(first, second):
    a, b = bounds(first), bounds(second)
    return all(a[1][i] >= b[0][i] and b[1][i] >= a[0][i]
               for i in range(3))


def contacts(shape, targets):
    rows = []
    candidates = 0
    for name, other in targets.items():
        if not nearby(shape, other):
            continue
        candidates += 1
        common = shape.intersect(other)
        if common.Volume() > 1.e-6:
            rows.append({'name': name, 'volume_mm3': common.Volume(),
                         'bounds_mm': bounds(common)})
    return {'candidate_count': candidates, 'contacts': rows}


def stock_probes(data):
    """Complete quarter bearing, slot surround and wall landing witnesses."""
    x, y, z = data['centre_world_mm']
    radius, wall = data['seat_radius_mm'], data['wall_mm']
    half = data['width_mm'] / 2.
    low = data['seat_bottom_world_z_mm']
    outer = cq.Solid.makeCylinder(radius + wall, 2. * half,
                                  cq.Vector(x, y - half, z), cq.Vector(0, 1, 0))
    quarter = outer.intersect(cq.Solid.makeBox(
        radius + wall, 2. * half, radius + wall, cq.Vector(x, y - half, low)))
    bore = cq.Solid.makeCylinder(radius, 2. * half + .2,
                                 cq.Vector(x, y - half - .1, z), cq.Vector(0, 1, 0))
    a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
    bottom = data['beam_bottom_world_z_mm']
    surround = cq.Solid.makeBox(b[0] - a[0] + 6., b[1] - a[1] + 6., 3.,
                                cq.Vector(a[0] - 3., a[1] - 3., bottom))
    slot = cq.Solid.makeBox(b[0] - a[0], b[1] - a[1], 3.2,
                            cq.Vector(a[0], a[1], bottom - .1))
    root_x = data['wall_root_x_mm']
    landing = cq.Solid.makeBox(.01, data['beam_width_mm'], 3., cq.Vector(
        root_x - .01, data['wall_lane_world_y_mm'] - data['beam_width_mm'] / 2.,
        bottom))
    return {'full_3mm_quarter_missing_mm3': quarter.cut(bore),
            'full_3mm_slot_surround_missing_mm3': surround.cut(slot),
            'wall_landing_missing_mm3': landing}


def neck_clearance(data):
    """The two removed fore shoulder wedges, with no other shell allowance."""
    points = data['beam_plan_world_xy_mm']
    if not points:
        return cq.Compound.makeCompound([])
    x0, x1 = min(p[0] for p in points), max(p[0] for p in points)
    y0, y1 = min(p[1] for p in points), max(p[1] for p in points)
    bottom = data['beam_bottom_world_z_mm']
    rectangle = cq.Solid.makeBox(x1 - x0, y1 - y0, 3., cq.Vector(x0, y0, bottom))
    neck = (cq.Workplane('XY').polyline(points).close().extrude(3.).val()
            .translate((0., 0., bottom)))
    return rectangle.cut(neck)


def bind_back_top(path, output):
    """Append only actual printed-stock readings to the original local proof."""
    from _cadq_export import import_step

    report = json.loads(output.read_text())
    stock = import_step(path).val()
    rows = {}
    for number, data in enumerate(meter.meter_support_datums()):
        name = 'meter-' + ('fore' if number == 0 else 'aft')
        support = meter.meter_supports()[number]
        x, y, z = data['centre_world_mm']
        half = data['width_mm'] / 2.
        a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
        bottom = data['beam_bottom_world_z_mm']
        slot = cq.Solid.makeBox(b[0] - a[0], b[1] - a[1], 3.,
                                cq.Vector(a[0], a[1], bottom))
        bore = cq.Solid.makeCylinder(data['seat_radius_mm'], 2. * half,
                                     cq.Vector(x, y - half, z), cq.Vector(0, 1, 0))
        original = report['rows'][name]['datums']
        rows[name] = {
            'same_recorded_datums': json.loads(json.dumps(data)) == original,
            'source_support_missing_mm3': support.cut(stock).Volume(),
            'actual_tie_slot_stock_mm3': slot.intersect(stock).Volume(),
            'actual_seat_bore_stock_mm3': bore.intersect(stock).Volume(),
            'neck_relief_stock_mm3': neck_clearance(data).intersect(stock).Volume(),
            **{key: probe.cut(stock).Volume()
               for key, probe in stock_probes(data).items()}}
    binding = {
        'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
        'current_applicability': True,
        'stock_valid': stock.isValid(), 'stock_solids': len(stock.Solids()),
        'source_sha256': {
            str(Path(meter.__file__).relative_to(ROOT)): sha(Path(meter.__file__)),
            str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
        'rows': rows,
        'scope': ('Imported back-top versus the two unchanged source bracket solids, '
                  'complete quarter/slot stock, open slots and bore air. The original '
                  '172-target cached-neighbor/strip reading is preserved and is not replayed. '
                  'No installed-wire, whole-group motion or physical qualification is added.')}
    binding['passed_actual_stock'] = (
        binding['stock_valid'] and binding['stock_solids'] == 1
        and all(row['same_recorded_datums'] and all(
            value <= 1.e-6 for key, value in row.items()
            if key.endswith('_mm3')) for row in rows.values()))
    report['actual_back_top_binding'] = binding
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('Actual meter bracket stock:', json.dumps(binding), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--targets', type=Path,
                        help='JSON with scope and parts mapping names to native BREP paths')
    parser.add_argument('--bind-back-top', type=Path,
                        help='Append only imported-shell stock to the existing receipt')
    parser.add_argument('--output', type=Path, default=HERE / 'wall-meter-review.json')
    parser.add_argument('--brep-output', type=Path)
    args = parser.parse_args()
    if args.bind_back_top:
        return bind_back_top(args.bind_back_top.resolve(), args.output)
    if not args.targets:
        parser.error('--targets is required for the local cached-neighbor reading')
    index_path = args.targets.resolve()
    index = json.loads(index_path.read_text())
    files = {name: (Path(path) if Path(path).is_absolute() else ROOT / path)
             for name, path in index['parts'].items()}
    targets = {name: cq.Shape.importBrep(str(path)) for name, path in files.items()}
    supports = meter.meter_supports()
    strips = {name: shape for name, shape in mounts.nominal_tie_strips().items()
              if name.startswith('meter-')}
    routes = meter.meter_tie_routes()
    rows = {}
    for number, data in enumerate(meter.meter_support_datums()):
        name = 'meter-' + ('fore' if number == 0 else 'aft')
        support, strip = supports[number], strips[name]
        row = {'datums': data, 'support_valid': support.isValid(),
               'support_solids': len(support.Solids()),
               'support_faces': len(support.Faces()),
               'support_volume_mm3': support.Volume(),
               'support': contacts(support, targets),
               'strip': contacts(strip, targets),
               'strip_own_support_mm3': strip.intersect(support).Volume(),
               'strip_solids_valid': all(s.isValid() for s in strip.Solids()),
               'tie_length_mm': routes[name]['length_mm'],
               'tie_stock_mm': routes[name]['stock_length_mm'],
               'tie_remainder_mm': routes[name]['stock_length_mm'] - routes[name]['length_mm']}
        row.update({key: probe.cut(support).Volume()
                    for key, probe in stock_probes(data).items()})
        rows[name] = row
        if args.brep_output:
            args.brep_output.mkdir(parents=True, exist_ok=True)
            support.exportBrep(str(args.brep_output / (name + '-support.brep')))
            strip.exportBrep(str(args.brep_output / (name + '-tie.brep')))
    rows['between_supports_mm3'] = supports[0].intersect(supports[1]).Volume()
    rows['cross_tie_support_mm3'] = {
        name: strip.intersect(supports[1 if name == 'meter-fore' else 0]).Volume()
        for name, strip in strips.items()}
    report = {'scope': __doc__.strip(), 'target_scope': index['scope'],
              'target_index_sha256': sha(index_path),
              'target_sha256': {name: sha(path) for name, path in files.items()},
              'source_sha256': {
                  str(Path(meter.__file__).relative_to(ROOT)): sha(Path(meter.__file__)),
                  str(Path(__file__).relative_to(ROOT)): sha(Path(__file__))},
              'rows': rows}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('Meter rows:', json.dumps(rows), flush=True)


if __name__ == '__main__':
    main()
