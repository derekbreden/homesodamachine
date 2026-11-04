"""Two PETG mold bodies with flat print bases and steep corbels.

Frame: funnel brim centred in XY, cavity base at Z=0, +Z is closure lift.
The cavity prints upright; the core prints inverted on its flat dry back.
Six walls and 15% gyroid fill the solid stock. Bolt pockets have open side access.
"""

import argparse
import json
import sys
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents
            if any((p/'hardware/scripts'/name).is_file() for name in ('_rust_part.py','_cadq_export.py')))
sys.path[:0] = [str(ROOT/'hardware/printed-parts/zone-c/funnel'),
                str(ROOT/'hardware/scripts')]
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()
import funnel

from _zone_data import data as _zone, note_read


def _data(**payload):
    return _zone('funnel-mold', **payload)


globals().update(_data())


def _design(parts, m, minimum_backing, minimum_core_backing, containment):
    note_read(ROOT / 'hardware/printed-parts/zone-c/funnel/funnel.step')
    facts = {}
    for name, solid in parts.items():
        bb = solid.BoundingBox()
        facts[name] = {'size': [bb.xlen, bb.ylen, bb.zlen], 'volume': solid.Volume()}
    return _data(method='design', parts=facts, dimensions=m,
                 minimum_backing=minimum_backing, minimum_core_backing=minimum_core_backing,
                 containment=containment)


def breathers(base_width, core_back):
    return _data(method='breathers', base_width=base_width, core_back=core_back)


def load_screen(m, bottom):
    return _data(method='load_screen', dimensions=m, bottom=bottom)


def numbers():
    return _data(method='numbers')


class _PartFacts:
    def __init__(self, facts):
        self.facts = facts

    def BoundingBox(self):
        from types import SimpleNamespace
        return SimpleNamespace(**_data(method='part_facts', facts=self.facts))

    def Volume(self):
        return self.facts['volume_mm3']


def main(output):
    import _rust_part
    n = numbers()
    output.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel-mold', n, output)
    facts = {row['name']: {'bounds': [row['min'], row['max']], 'volume_mm3': row['volume']}
             for row in said['bodies'][:4]}
    facts['checks'] = said['bodies'][0]['checks']
    for name in ('cavity', 'core'):
        for suffix in ('step', 'stl', 'step.mesh', 'step.npz'):
            note_read(output / f'{name}.{suffix}')
    info = _data(method='report', facts=facts, numbers=n, output=str(output))
    (output / 'design.json').write_text(json.dumps(info, indent=2)+'\n')
    print('-> mold bodies, tooling views, fine models, print meshes and design.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'hardware/printed-parts/zone-c/funnel-mold')
    args = parser.parse_args()
    main(args.output)
