#!/usr/bin/env python3
"""Render the cord and bottle insertion poses from the frozen installation meshes."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
SNAPSHOTS = HARDWARE / 'install-guide/out'
OUT = SNAPSHOTS / 'insertion-actions'
ART = HARDWARE / 'install-guide/art/insertion-actions'
sys.path.insert(0, str(HARDWARE / 'scripts'))
import _hsm_render
POWER_RETREAT = 25.0
BOTTLE_LIFT = 50.0
_machine_facts = json.loads((HARDWARE / 'manifold-layout/enclosure-assembly.facts.json').read_text())
_power_x, _power_z = _machine_facts['constants']['C14_STATION']
_rear_y = _machine_facts['box']['outer'][3]
POSES = {
    'power-ready': dict(cam=(-.85, 1, .25), target=(_power_x-8, _rear_y+34, _power_z-16),
                        span=64, size=(1800, 1300)),
    'fill-ready': dict(cam=(.65, -1, .5), target=(0, 140, 465),
                       span=265, size=(1600, 1500)),
}


def unit(vector):
    length = math.sqrt(sum(value * value for value in vector))
    return tuple(value / length for value in vector)


def pixel(point, pose):
    direction = unit(pose['cam'])
    right = unit((-direction[1], direction[0], 0))
    up = (direction[1] * right[2] - direction[2] * right[1],
          direction[2] * right[0] - direction[0] * right[2],
          direction[0] * right[1] - direction[1] * right[0])
    delta = tuple(value - target for value, target in zip(point, pose['target']))
    width, height = pose['size']
    scale = height / (2 * pose['span'])
    return (width / 2 + sum(value * axis for value, axis in zip(delta, right)) * scale,
            height / 2 - sum(value * axis for value, axis in zip(delta, up)) * scale)


def mesh_bounds(path):
    data = path.read_bytes()
    header_length = struct.unpack_from('<I', data)[0]
    header = json.loads(data[4:4 + header_length])
    assert header['v'] in (2, 3)
    result = {}
    for mesh in header['meshes']:
        offset, count = mesh['pos']
        points = np.frombuffer(data, dtype='<f4', count=count,
                               offset=4 + header_length + offset).reshape(-1, 3)
        result[mesh['name']] = (points.min(axis=0).tolist(), points.max(axis=0).tolist())
    return result


def anchor(point, pose):
    return dict(world=point, pixel=pixel(point, pose))


def metadata(name):
    pose = POSES[name]
    source = 'power-ready' if name == 'power-ready' else 'fill-seated'
    step = SNAPSHOTS / f'{source}.step'
    mesh = step.with_suffix('.step.mesh')
    bounds = mesh_bounds(mesh)
    if name == 'power-ready':
        plug_min, plug_max = bounds['cordset/1']
        x = (plug_min[0] + plug_max[0]) / 2
        z = (plug_min[2] + plug_max[2]) / 2
        front_y = plug_min[1] + POWER_RETREAT
        body_y = (plug_min[1] + plug_max[1]) / 2 + POWER_RETREAT
        socket_y = bounds['c14-inlet'][1][1]
        points = {
            'connector-mouth': (x, front_y, z),
            'connector-body': (x, body_y, z),
            'connector-body-top': (x, body_y, plug_max[2]),
            'connector-body-side': (plug_min[0], body_y, z),
            'socket-mouth': (x, socket_y, z),
            'arrow-start': (plug_min[0], body_y, z),
            'arrow-end': (plug_min[0], socket_y + 18, z),
        }
        action = dict(prefix='cordset', translation=(0, POWER_RETREAT, 0), expected=3)
        crop = (0, 160, 1800, 1140)
        gap = front_y - socket_y
        axis = (0, -1, 0)
    else:
        neck_min, neck_max = bounds['bottle-neck']
        body_min, body_max = bounds['bottle-body']
        x = (neck_min[0] + neck_max[0]) / 2
        y = (neck_min[1] + neck_max[1]) / 2
        radius = (body_max[0] - body_min[0]) / 2
        facing = unit((pose['cam'][0], pose['cam'][1], 0))
        surface_x, surface_y = x + radius * facing[0], y + radius * facing[1]
        mouth_z = neck_min[2] + BOTTLE_LIFT
        rim_z = bounds['funnel'][1][2]
        points = {
            'bottle-mouth': (x, y, mouth_z),
            'bottle-body': (surface_x, surface_y,
                            (body_min[2] + body_max[2]) / 2 + BOTTLE_LIFT),
            'bottle-top': (x, y, bounds['bottle-base'][1][2] + BOTTLE_LIFT),
            'funnel-mouth': (x, y, rim_z),
            'arrow-start': (surface_x, surface_y, body_max[2] + BOTTLE_LIFT - 35),
            'arrow-end': (surface_x, surface_y, body_min[2] + BOTTLE_LIFT + 24),
        }
        action = dict(prefix='bottle-', translation=(0, 0, BOTTLE_LIFT), expected=4)
        crop = (290, 190, 1550, 1500)
        gap = mouth_z - rim_z
        axis = (0, 0, -1)
    return dict(
        **pose, source_step=str(step.relative_to(ROOT)),
        source_mesh=str(mesh.relative_to(ROOT)),
        source_mesh_sha256=hashlib.sha256(mesh.read_bytes()).hexdigest(),
        projection='orthographic', up=(0, 0, 1), trim=False,
        pixel_origin='top-left', pixels_per_mm=pose['size'][1] / (2 * pose['span']),
        crop=crop, action=action, visible_axis_gap_mm=gap,
        insertion_axis=axis, points={key: anchor(value, pose) for key, value in points.items()},
    )


def moved_payload(name, entry):
    """Translate the moving meshes in a render-only copy of the frozen payload."""
    data = bytearray((ROOT / entry['source_mesh']).read_bytes())
    length = struct.unpack_from('<I', data)[0]
    header = json.loads(data[4:4 + length])
    action = entry['action']
    moved = []
    for mesh in header['meshes']:
        if mesh['name'].startswith(action['prefix']):
            offset, count = mesh['pos']
            points = np.frombuffer(data, dtype='<f4', count=count,
                                   offset=4 + length + offset).reshape(-1, 3)
            points += action['translation']
            moved.append(mesh['name'])
    if len(moved) != action['expected']:
        raise ValueError(f"Expected {action['expected']} moving meshes, found {len(moved)}")
    header.pop('src', None)
    header['cut'] = dict(source_payload_sha256=entry['source_mesh_sha256'], action=action)
    text = json.dumps(header, separators=(',', ':')).encode()
    text += b' ' * (-(len(text) + 4) % 4)
    target = OUT / f'{name}.step.mesh'
    target.write_bytes(struct.pack('<I', len(text)) + text + data[4 + length:])
    entry['render_mesh'] = str(target.relative_to(ROOT))
    entry['render_mesh_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    entry['moved_meshes'] = moved
    return target


def registration(entry, report):
    """Read the anchor pixels from the matrix the GPU picture was drawn with."""
    matrix = np.asarray(report['camera']['view_proj']).reshape(4, 4, order='F')
    width, height = entry['size']
    points = {}
    for name, anchor_entry in entry['points'].items():
        p = matrix @ [*anchor_entry['world'], 1]
        x, y = p[:2] / p[3]
        points[name] = [(x + 1) * width / 2, (1 - y) * height / 2]
    return dict(moved=entry['moved_meshes'], points=points)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenes', nargs='*', choices=list(POSES))
    parser.add_argument('--stage-only', action='store_true')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    entries = {name: metadata(name) for name in (args.scenes or POSES)}
    jobs = []
    for name, entry in entries.items():
        payload = moved_payload(name, entry)
        jobs.append(dict(
            step=str(Path(entry['source_step']).relative_to('hardware')),
            payload=str(payload),
            out=str(ART / f'{name}.png'), cam=entry['cam'], target=entry['target'],
            span=entry['span'], size='x'.join(str(n) for n in entry['size']),
            up=(0, 0, 1), bg='#f2eee8', transparent=True, solid=True,
            ortho=True, trim=False, ground=False, fog=False))
    manifest = OUT / 'scenes.json'
    manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    if not args.stage_only:
        reports = _hsm_render.render(jobs, reports=True)
        for (name, entry), report in zip(entries.items(), reports, strict=True):
            with Image.open(ART / f'{name}.png') as rendered:
                assert rendered.mode == 'RGBA'
                assert rendered.size == tuple(entry['size'])
                entry['alpha_bounds'] = rendered.getchannel('A').getbbox()
            measured_registration = registration(entry, report)
            (OUT / f'{name}.render.json').write_text(json.dumps(measured_registration, indent=2)+'\n')
            for point, anchor_entry in entry['points'].items():
                measured = measured_registration['points'][point]
                assert max(abs(a - b) for a, b in zip(measured, anchor_entry['pixel'])) < 1e-5
    (OUT / 'anchors.json').write_text(json.dumps(dict(scenes=entries), indent=2) + '\n')
    print(OUT / 'anchors.json')


if __name__ == '__main__':
    main()
