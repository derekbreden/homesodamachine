"""Manual 40-specimen Mark2 bridge/ramp comparison. Does not send a print."""
from pathlib import Path
import importlib.util
import json
import random

HERE = Path(__file__).resolve().parent
source = HERE.parent/'bonding-and-fins-v4/prepare.py'
loader = importlib.util.spec_from_file_location('v4_geometry', source)
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)
STEM = '2026-10-14-v6-finish-matrix-petgf-left04-z004-mark2'


def main():
    v4.FIN_ROOF = v4.FIRST + 78*v4.LAYER  # 18.92; all ramps finish first.
    pools = {key: [] for key in ('C', 'F', 'Y', 'R')}
    conditions = []
    for fan in (70, 100):
        for flow in (100, 125):
            for speed in (15, 25):
                index = len(conditions)+1
                conditions.append({'condition': index, 'flow_percent': flow,
                                   'fan_percent': fan, 'first_bridge_speed_mm_s': speed})
                for prefix in ('C', 'F', 'Y'):
                    name = f'{prefix}{index:02d}'
                    if prefix == 'C':
                        shape, detail = v4.control(name, v4.FIN_ROOF, 5*v4.LAYER)
                    else:
                        shape, detail = v4.fin(name, two=True, rotate=prefix == 'Y')
                    detail.update(condition=index, thick_bridges=False,
                                  bridge_extrusion_multiplier=flow/100,
                                  first_bridge_speed_mm_s=speed, fan_percent=fan)
                    pools[prefix].append((name, shape, detail))
    for angle in (35, 37.5, 40, 42.5):
        for fan in (70, 100):
            for reverse in (False, True):
                name = f'R{len(pools["R"])+1:02d}'
                shape, detail = v4.ramp(name, angle)
                if reverse:
                    shape = shape.rotate((0,0,0), (0,0,1), 180)
                detail.update(fan_percent=fan, reversed=reverse,
                              rotation_degrees=180 if reverse else 0)
                pools['R'].append((name, shape, detail))

    # Balance wide fins and narrow controls/ramps in each row. Spread settings
    # across the center of the bed instead of assigning fan levels to regions.
    rng = random.Random(20261014)
    for items in pools.values():
        rng.shuffle(items)
    allocation = [dict(C=2,F=1,Y=1,R=3), dict(C=2,F=1,Y=1,R=3),
                  dict(C=1,F=2,Y=1,R=3), dict(C=1,F=2,Y=1,R=3),
                  dict(C=1,F=1,Y=2,R=2), dict(C=1,F=1,Y=2,R=2)]
    rows = []
    for counts in allocation:
        items = [pools[key].pop() for key, count in counts.items() for _ in range(count)]
        rng.shuffle(items)
        height = max(shape.val().BoundingBox().ylen for _,shape,_ in items)
        rows.append((height, items))
    row_gap = 2.5
    cursor = 160-(sum(height for height,_ in rows)+row_gap*(len(rows)-1))/2
    groups = []
    for height, items in rows:
        groups.append((cursor+height/2, items))
        cursor += height+row_gap
    v4.write_plate('Mark2', groups, destination=HERE, stem=STEM, spacing_mm=3.5)
    (HERE/'conditions.json').write_text(json.dumps({'bridge_conditions':conditions,
        'C':'permanent posts, X bridge', 'F':'opposing removable fins, X bridge',
        'Y':'opposing removable fins, Y bridge', 'R':'full 14 mm ramp; see manifest for angle, fan and direction',
        'within_row_gap_mm':3.5, 'between_row_gap_mm':row_gap,
        'placement_seed':20261014}, indent=2)+'\n')


if __name__ == '__main__':
    main()
