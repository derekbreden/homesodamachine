#!/usr/bin/env python3
"""The cylinder connection and startup controls, in the regulator's world frame.

+Y faces the customer, +Z is up, and the cylinder stands at -X. The PM4508F4S
flare connector and PI061008S reducer remain assembled on the red tether.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess

import cadquery as cq
from PIL import Image

import scenes
import startup


OUT = scenes.HARDWARE / 'quickstart-codex/out/cylinder-actions'
ART = scenes.HARDWARE / 'quickstart-codex/art/cylinder-actions'
READY_RETREAT = 29.0
TETHER_BEND_RADIUS = 28.0
TETHER_CORNER_DROP = 69.0
TETHER_RUN_X = 160.0
CONNECTION_POSE = dict(cam=(.12, 1, .15), target=(-34, 0, -58), span=150,
                       size=(1600, 1500))
STARTUP_EXTRA_HEIGHT = 300
reg = scenes.reg
install = scenes.install


def unit(vector):
    length = math.sqrt(sum(value * value for value in vector))
    return tuple(value / length for value in vector)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def camera_axes(cam):
    direction = unit(cam)
    right = unit(cross((0, 0, 1), direction))
    return right, cross(direction, right)


def startup_pose():
    """The startup camera's pixel registration with extra canvas below it."""
    _, up = camera_axes(startup.CAM)
    scale = startup.SIZE[1] / (2 * startup.SPAN)
    shift = STARTUP_EXTRA_HEIGHT / (2 * scale)
    height = startup.SIZE[1] + STARTUP_EXTRA_HEIGHT
    return dict(cam=startup.CAM,
                target=tuple(value - shift * axis
                             for value, axis in zip(startup.TARGET, up)),
                span=startup.SPAN * height / startup.SIZE[1],
                size=(startup.SIZE[0], height))


def pixel(point, pose):
    right, up = camera_axes(pose['cam'])
    delta = tuple(value - target for value, target in zip(point, pose['target']))
    width, height = pose['size']
    scale = height / (2 * pose['span'])
    return (width / 2 + sum(value * axis for value, axis in zip(delta, right)) * scale,
            height / 2 - sum(value * axis for value, axis in zip(delta, up)) * scale)


def adapter_stations(retreat):
    x, y, tip_z = reg.outlet()[0]
    front = tip_z + install.CO2_FLARE_HEX_LENGTH - retreat
    back = front - install.CO2_FLARE_LENGTH
    hex_back = front - install.CO2_FLARE_HEX_LENGTH
    body_middle = (back + 1.5 + hex_back) / 2
    reducer_end = back - (install.CO2_REDUCER_LENGTH - install.CO2_FLARE_INSERTION)
    return {
        'male-outlet-tip': (x, y, tip_z),
        'connector-mouth': (x, y, front),
        'connector-hex-front': (x, y + install.CO2_FLARE_HEX_FLATS / 2,
                                front - install.CO2_FLARE_HEX_LENGTH / 2),
        'connector-turn-axis': (x, y, body_middle),
        'connector-hand-turn': (x, y + install.CO2_FLARE_BODY_D / 2, body_middle),
        'connector-bottom': (x, y, back),
        'reducer-body-front': (x, y + install.CO2_REDUCER_BODY_D / 2,
                               (back + reducer_end) / 2),
        'red-tube-exit': (x, y, reducer_end),
    }


def assembly(retreat=0, pressurised=False):
    """The fitted regulator, cylinder and complete factory-assembled tether."""
    result = cq.Assembly(name='cylinder-actions')
    source = startup.assembly() if pressurised else scenes.cylinder()
    for child in source.children:
        if child.name not in {'tether-nut', 'red-tether'}:
            result.add(child)
    tip = reg.outlet()[0]
    exit_point = install._co2_tether_adapter(result, tip, retreat)
    corner_z = min(tip[2] - TETHER_CORNER_DROP - retreat,
                   exit_point[2] - TETHER_BEND_RADIUS)
    result.add(install._bend([exit_point, (tip[0], tip[1], corner_z),
                              (TETHER_RUN_X, tip[1], corner_z)],
                             radius=TETHER_BEND_RADIUS),
               name='red-tether', color=install.RED_TUBE)
    return result


def points(retreat, pressurised):
    result = adapter_stations(retreat)
    result.update({
        'upper-gauge': reg.outlet_dial()[0],
        'cylinder-gauge': reg.tank_dial()[0],
        'big-pressure-knob': reg.adjustment()[0],
        'small-gas-knob': reg.shutoff()[0],
        'cylinder-handwheel': (-115, 0, 33),
        'cylinder-valve': (-115, 12, -7.5),
    })
    if pressurised:
        result['upper-needle-tip'] = startup.points()['upper-needle-tip']
    return result


def anchor_metadata(retreat, pressurised, pose):
    anchors = {name: dict(world=point, pixel=pixel(point, pose))
               for name, point in points(retreat, pressurised).items()}
    for name, anchor in anchors.items():
        if name.startswith(('connector-', 'reducer-', 'red-tube-')):
            anchor['source'] = 'hardware/install-guide/_install_art.py:_co2_tether_adapter'
        elif name in {'cylinder-handwheel', 'cylinder-valve'}:
            anchor['source'] = 'tools/quickstart-codex/scenes.py:cylinder'
        elif name == 'upper-needle-tip':
            anchor['source'] = 'tools/quickstart-codex/startup.py:points'
        else:
            anchor['source'] = 'hardware/reference/wellbom-regulator/wellbom_regulator.py:stations'
    mouth = adapter_stations(retreat)['connector-mouth']
    seated_mouth = adapter_stations(0)['connector-mouth']
    lift_start = (mouth[0] + 26, mouth[1], mouth[2])
    lift_end = (seated_mouth[0] + 26, seated_mouth[1], seated_mouth[2])
    return dict(
        cam=pose['cam'], target=pose['target'], span=pose['span'], size=pose['size'],
        projection='orthographic', up=(0, 0, 1), trim=False,
        pixel_origin='top-left', pixels_per_mm=pose['size'][1] / (2 * pose['span']),
        crops=(dict(overview=(173, 53, 1752, 1360),
                    upper_gauge=(533, 48, 873, 388),
                    connector_detail=(485, 950, 905, 1360)) if pressurised else
               dict(overview=(80, 0, 1600, 1500),
                    connector_detail=(420, 775, 830, 1335))),
        retreat_mm=retreat, outlet_psi=startup.OUTLET_PSI if pressurised else 0,
        cylinder_psi=startup.CYLINDER_PSI if pressurised else 0,
        points=anchors,
        insertion=dict(axis=(0, 0, 1), distance_mm=retreat,
                       from_world=mouth, to_world=seated_mouth,
                       from_pixel=pixel(mouth, pose), to_pixel=pixel(seated_mouth, pose),
                       offset_arrow=dict(from_world=lift_start, to_world=lift_end,
                                         from_pixel=pixel(lift_start, pose),
                                         to_pixel=pixel(lift_end, pose))),
        turn_axes={'connector-hand-turn': (0, 0, 1),
                   'big-pressure-knob': reg.adjustment()[1],
                   'small-gas-knob': reg.shutoff()[1],
                   'cylinder-handwheel': (0, 0, 1)},
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenes', nargs='*',
                        choices=['co2-ready', 'co2-connected', 'startup-gas'])
    parser.add_argument('--stage-only', action='store_true')
    args = parser.parse_args()
    wanted = set(args.scenes)
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    jobs = []
    metadata = dict(
        geometry_sources={
            'regulator': 'hardware/reference/wellbom-regulator/wellbom_regulator.py',
            'cylinder': 'tools/quickstart-codex/scenes.py:cylinder',
            'connector': 'hardware/install-guide/_install_art.py:_co2_tether_adapter',
            'startup-dials': 'tools/quickstart-codex/startup.py:assembly',
        },
        fittings=['PM4508F4S', 'PI061008S'],
        connector_seating='Illustrative seating depth from _co2_tether_adapter.',
        scenes={},
    )
    states = [('co2-ready', READY_RETREAT, False, CONNECTION_POSE),
              ('co2-connected', 0, False, CONNECTION_POSE),
              ('startup-gas', 0, True, startup_pose())]
    for name, retreat, pressurised, pose in states:
        if wanted and name not in wanted:
            continue
        path = OUT / f'{name}.step'
        scenes.original._export_colored(assembly(retreat, pressurised), path, mesh=True)
        jobs.append(dict(step=str(path.relative_to(scenes.HARDWARE)),
                         out=str(ART / f'{name}.png'), cam=pose['cam'], target=pose['target'],
                         span=pose['span'], size=f"{pose['size'][0]}x{pose['size'][1]}",
                         up=(0, 0, 1), bg='#f2eee8', transparent=True, solid=True,
                         ortho=True, trim=False, ground=False, fog=False))
        metadata['scenes'][name] = anchor_metadata(retreat, pressurised, pose)
        if name == 'startup-gas':
            metadata['scenes'][name]['registered_source_pose'] = dict(
                cam=startup.CAM, target=startup.TARGET, span=startup.SPAN,
                size=startup.SIZE, same_pixel_coordinates=True,
                extra_canvas_below=STARTUP_EXTRA_HEIGHT)
        print(f'Staged {name}', flush=True)
    manifest = OUT / 'scenes.json'
    manifest.write_text(json.dumps(jobs, indent=2) + '\n')
    if not args.stage_only:
        subprocess.run(['node', str(scenes.original.RENDERER), '--jobs', str(manifest)],
                       cwd=scenes.ROOT, check=True)
        for name, entry in metadata['scenes'].items():
            with Image.open(ART / f'{name}.png') as rendered:
                assert rendered.size == tuple(entry['size'])
                entry['alpha_bounds'] = rendered.getchannel('A').getbbox()
    (OUT / 'anchors.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(OUT / 'anchors.json')


if __name__ == '__main__':
    main()
