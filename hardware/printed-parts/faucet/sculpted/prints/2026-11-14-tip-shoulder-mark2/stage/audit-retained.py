"""Verify unchanged base and hardware roads and the revised cover's native roads."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

PARTS = {1901: 'base', 1903: 'display_cover', 1904: 'mounting_plate', 1905: 'lever'}
START = '; MACHINE_START_GCODE_END'
END = '; MACHINE_END_GCODE_START'
SCOPE = '; start printing object, unique label id: '
STOP = '; stop printing object, unique label id: '
RINGS = '; HSM_PHASE: mounting plate counterbore supports'
WORDS = re.compile(r'([XYZEFIJKPS])\s*(-?(?:\d+(?:\.\d*)?|\.\d+))')
MOTION = ('G0', 'G1', 'G2', 'G3')


def deposition(path):
    hashes = {obj: sha256() for obj in PARTS}
    counts = dict.fromkeys(PARTS, 0)
    xyz = (290., -.5, 6.2)
    feed, fan, accel = 0., 0., 10000.
    object_id = None
    ring = False
    with path.open() as tape:
        if not any(line.startswith(START) for line in tape):
            raise ValueError(f'Missing model body in {path}')
        for line in tape:
            if line.startswith(END):
                break
            if line.startswith('; HSM_PHASE: '):
                ring = line.startswith(RINGS)
            if line.startswith(SCOPE):
                object_id = int(line[len(SCOPE):])
            elif line.startswith(STOP):
                object_id = None
            action = line.split(' ', 1)[0].strip()
            if action not in (*MOTION, 'M106', 'M204'):
                continue
            args = {key: float(value) for key, value in WORDS.findall(line.split(';', 1)[0])}
            if action == 'M106' and args.get('P', 1) == 1:
                fan = args['S']
            elif action == 'M204' and 'S' in args:
                accel = args['S']
            elif action in MOTION:
                before = xyz
                xyz = tuple(args.get(axis, value) for axis, value in zip('XYZ', xyz))
                feed = args.get('F', feed)
                e = args.get('E', 0.)
                arc = action in ('G2', 'G3')
                if not ring and object_id in PARTS and e > 0 and (before[:2] != xyz[:2] or arc):
                    center = tuple(args.get(axis, 0.) for axis in 'IJK') if arc else ()
                    row = (*before, *xyz, *center, e, feed, fan, accel)
                    hashes[object_id].update((action+','+','.join(f'{v:.5f}' for v in row)+'\n').encode())
                    counts[object_id] += 1
        else:
            raise ValueError(f'Missing machine end in {path}')
    return {obj: {'ordered_road_sha256': hashes[obj].hexdigest(), 'road_count': counts[obj]} for obj in PARTS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference', type=Path)
    parser.add_argument('revised_native', type=Path)
    parser.add_argument('merged', type=Path)
    args = parser.parse_args()
    old = deposition(args.reference)
    new = deposition(args.revised_native)
    actual = deposition(args.merged)
    expected = {obj: (new if obj == 1903 else old)[obj] for obj in PARTS}
    if not all(expected[obj] == actual[obj] and actual[obj]['road_count'] for obj in PARTS):
        raise ValueError((expected, actual))
    print(json.dumps({
        'input_tapes_sha256': {name: sha256(path.read_bytes()).hexdigest() for name, path in vars(args).items()},
        'signature_fields': ['command', 'start_xyz', 'end_xyz', 'arc_center_offset_ijk',
                             'extrusion_length', 'feed', 'fan_pwm', 'acceleration'],
        'retained_ordered_deposition': {
            PARTS[obj]: {**actual[obj], 'source': 'revised_native' if obj == 1903 else 'reference'} for obj in PARTS
        },
    }, indent=2))


if __name__ == '__main__':
    main()
