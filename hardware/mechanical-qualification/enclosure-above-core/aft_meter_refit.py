"""Manually read the changed aft meter carrier against named native fixtures.

The target index records the appliance snapshot and maps names to native BREP
files. The owning back-top is excluded. This local reader is called by no build,
hook or publisher. It establishes nominal stock and clearance, not printed
strength, tie threading, retention or lifetime. Run through the CAD queue.
"""

import argparse
import json
from pathlib import Path

from wall_meter import ROOT, HERE, cq, meter, mounts, sha, bounds, contacts, stock_probes, tie_slot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--targets', type=Path)
    parser.add_argument('--bind-back-top', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'aft-meter-refit-review.json')
    args = parser.parse_args()
    support = meter.meter_supports()[1]
    data = meter.meter_support_datums()[1]
    if args.bind_back_top:
        from _cadq_export import import_step

        path = args.bind_back_top.resolve()
        stock = import_step(path).val()
        a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
        slot = tie_slot(data)
        x, y, z = data['centre_world_mm']
        bore = cq.Solid.makeCylinder(data['seat_radius_mm'], data['width_mm'],
            cq.Vector(x, data['stock_min_world_mm'][1], z), cq.Vector(0, 1, 0))
        report = json.loads(args.output.read_text())
        report['actual_back_top_binding'] = {
            'path': str(path.relative_to(ROOT)), 'sha256': sha(path),
            'valid': stock.isValid(), 'solids': len(stock.Solids()),
            'source_support_missing_mm3': support.cut(stock).Volume(),
            'tie_slot_stock_mm3': slot.intersect(stock).Volume(),
            'seat_bore_stock_mm3': bore.intersect(stock).Volume(),
            **{key: shape.cut(stock).Volume() for key, shape in stock_probes(data).items()}}
    else:
        if not args.targets:
            parser.error('--targets or --bind-back-top is required')
        index_path = args.targets.resolve()
        index = json.loads(index_path.read_text())
        files = {name: (Path(path) if Path(path).is_absolute() else ROOT / path)
                 for name, path in index['parts'].items()}
        targets = {name: cq.Shape.importBrep(str(path)) for name, path in files.items()}
        strip = mounts.nominal_tie_strips()['meter-aft']
        tie = meter.meter_tie_routes()['meter-aft']
        report = {
            'scope': __doc__.strip(), 'assembly_sha256': index['assembly_sha256'],
            'target_scope': index['scope'], 'target_index_sha256': sha(index_path),
            'target_sha256': {name: sha(path) for name, path in files.items()},
            'datums': data, 'support_valid': support.isValid(),
            'support_solids': len(support.Solids()), 'support_bounds_mm': bounds(support),
            'support': contacts(support, targets), 'strip': contacts(strip, targets),
            'strip_own_support_mm3': strip.intersect(support).Volume(),
            'regulator_air_mm': support.distance(targets['gas-regulator']),
            'check_air_mm': support.distance(targets['gas-check']),
            'tie': tie, 'tie_remainder_mm': tie['stock_length_mm']-tie['length_mm'],
            'stock': {key: shape.cut(support).Volume()
                      for key, shape in stock_probes(data).items()}}
    report['source_sha256'] = {
        str(path.relative_to(ROOT)): sha(path) for path in (
            Path(__file__), HERE / 'wall_meter.py', Path(meter.__file__))}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(args.output, flush=True)


if __name__ == '__main__':
    main()
