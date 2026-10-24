"""Split the dry electronics corner out of the study ceiling as an empty lid.

Native CAD runs manually through the shared queue. This creates a separate
arrangement study and leaves all production parts and parent studies alone.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('access_ceiling', HERE.parent / 'ceiling-fit/ceiling.py')
ceiling = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ceiling)


def rectangle(bounds, radius=0):
    shape = cq.Solid.makeBox(bounds['xmax'] - bounds['xmin'],
        bounds['ymax'] - bounds['ymin'], bounds['zmax'] - bounds['zmin'],
        cq.Vector(bounds['xmin'], bounds['ymin'], bounds['zmin']))
    return cq.Workplane(obj=shape).edges('|Z').fillet(radius).val() if radius else shape


def main():
    plan = json.loads((HERE / 'panel-plan.json').read_text())
    source = (HERE / plan['ceiling_plan']).resolve()
    original = ceiling.build(source)
    p = plan['panel']
    bounds = {key: p[key] for key in ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax')}
    radius, gap = p['corner_radius_mm'], p['edge_clearance_mm']
    panel = rectangle(bounds, radius)
    opening = {key: value + (gap if key.endswith('max') else -gap)
               for key, value in bounds.items()}
    opening.update(zmin=p['zmin'] - 1, zmax=p['zmax'] + 1)
    fixed = original.cut(rectangle(opening, radius + gap))
    seat = plan['fixed_perimeter_seat']
    outer = {key: value + (seat['root_overlap_mm'] if key.endswith('max') else -seat['root_overlap_mm'])
             for key, value in opening.items()}
    outer.update(zmin=p['zmin'] - seat['thickness_mm'], zmax=p['zmin'])
    inner = {key: value + (-seat['bearing_width_mm'] if key.endswith('max') else seat['bearing_width_mm'])
             for key, value in opening.items()}
    inner.update(zmin=outer['zmin'] - 1, zmax=outer['zmax'] + 1)
    ledge = rectangle(outer, radius + gap + seat['root_overlap_mm']).cut(rectangle(inner))
    fixed = fixed.fuse(ledge).clean()
    parts = {'access-fixed-ceiling': fixed, 'electronics-access-panel': panel}
    out = HERE / 'parts'
    out.mkdir(exist_ok=True)
    for name, shape in parts.items():
        cq.exporters.export(shape, str(out / (name + '.step')))
        vertices, faces = shape.tessellate(.1, .15)
        np.savez_compressed(out / (name + '.npz'),
            v=np.asarray([point.toTuple() for point in vertices], dtype=np.float32),
            f=np.asarray(faces, dtype=np.uint32))
    # Empty-panel motion has no attached devices, hoses or harnesses to carry.
    report = {
        'scope': plan['scope'],
        'source_plan_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'valid_single_solids': {name: shape.isValid() and len(shape.Solids()) == 1
                                for name, shape in parts.items()},
        'panel_size_mm': [p['xmax'] - p['xmin'], p['ymax'] - p['ymin'], p['zmax'] - p['zmin']],
        'closed_panel_fixed_ceiling_intersection_mm3': max(0., panel.intersect(fixed).Volume()),
        'lift_samples': [{'lift_mm': lift,
                         'fixed_ceiling_intersection_mm3': max(0., panel.translate((0, 0, lift)).intersect(fixed).Volume())}
                        for lift in (.1, 1., 3., 9., 30., plan['illustrated_lift_mm'])],
        'equipment_carried_by_panel': [],
        'retention_detail': plan['retention_detail']
    }
    (HERE / 'geometry-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
