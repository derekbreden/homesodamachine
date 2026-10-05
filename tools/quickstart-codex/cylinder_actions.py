#!/usr/bin/env python3
"""The cylinder connection and startup controls, in the regulator's world frame.

+Y faces the customer, +Z is up, and the cylinder stands at -X. The red tether is
pushed into the regulator's PI010822S at the factory, so the customer's one joint here is
the big nut onto the cylinder valve.
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
READY_STANDOFF = 30.0
CONNECTION_POSE = dict(cam=(.12, 1, .15), target=(-34, 0, -50), span=150,
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


def outlet_stations(stand_off):
    """The outlet push-fit and the tube leaving it, and the big nut's face."""
    x, y, mouth_z = reg.outlet()[0]
    x += stand_off
    return {
        'outlet-connector': (x, y + reg.PTC_COLLET_D / 2, (reg.OUTLET_HEX_Z + mouth_z) / 2),
        'red-tube-exit': (x, y, mouth_z),
        'cga-nut': (reg.inlet()[0][0] + stand_off, y + reg.CGA320_NUT_FLATS / 2, 0.0),
    }


def assembly(stand_off=0, pressurised=False):
    """The regulator, its factory-fitted tether and the top of the customer's cylinder."""
    return startup.assembly() if pressurised else scenes.cylinder(stand_off)


def points(stand_off, pressurised):
    def held(point):
        return (point[0] + stand_off, point[1], point[2])

    result = outlet_stations(stand_off)
    result.update({
        'upper-gauge': held(reg.outlet_dial()[0]),
        'cylinder-gauge': held(reg.tank_dial()[0]),
        'factory-screw': held(reg.adjustment()[0]),
        'cylinder-handwheel': (-115, 0, 33),
        'cylinder-valve': (-115, 12, -7.5),
    })
    if pressurised:
        result['upper-needle-tip'] = startup.points()['upper-needle-tip']
    return result


def anchor_metadata(stand_off, pressurised, pose):
    anchors = {name: dict(world=point, pixel=pixel(point, pose))
               for name, point in points(stand_off, pressurised).items()}
    for name, anchor in anchors.items():
        if name in {'cylinder-handwheel', 'cylinder-valve'}:
            anchor['source'] = 'tools/quickstart-codex/scenes.py:cylinder'
        elif name == 'upper-needle-tip':
            anchor['source'] = 'tools/quickstart-codex/startup.py:points'
        else:
            anchor['source'] = ('hardware/reference/taprite-3741-regulator/'
                                'taprite_3741_regulator.py:stations')
    nut = outlet_stations(stand_off)['cga-nut']
    seated_nut = outlet_stations(0)['cga-nut']
    return dict(
        cam=pose['cam'], target=pose['target'], span=pose['span'], size=pose['size'],
        projection='orthographic', up=(0, 0, 1), trim=False,
        pixel_origin='top-left', pixels_per_mm=pose['size'][1] / (2 * pose['span']),
        crops=(dict(overview=(173, 53, 1752, 1360),
                    upper_gauge=(533, 48, 873, 388),
                    connector_detail=(485, 950, 905, 1360)) if pressurised else
               dict(overview=(80, 0, 1600, 1500),
                    connector_detail=(420, 775, 830, 1335))),
        stand_off_mm=stand_off, outlet_psi=startup.OUTLET_PSI if pressurised else 0,
        cylinder_psi=startup.CYLINDER_PSI if pressurised else 0,
        points=anchors,
        approach=dict(axis=(-1, 0, 0), distance_mm=stand_off,
                      from_world=nut, to_world=seated_nut,
                      from_pixel=pixel(nut, pose), to_pixel=pixel(seated_nut, pose)),
        turn_axes={'cylinder-handwheel': (0, 0, 1)},
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
            'regulator': 'hardware/reference/taprite-3741-regulator/taprite_3741_regulator.py',
            'cylinder': 'tools/quickstart-codex/scenes.py:cylinder',
            'tether': 'hardware/install-guide/_install_art.py:_co2_tether',
            'startup-dials': 'tools/quickstart-codex/startup.py:assembly',
        },
        fittings=['PI010822S'],
        tether_seating='Pushed in at the factory; the drawn depth past the mouth is illustrative.',
        scenes={},
    )
    states = [('co2-ready', READY_STANDOFF, False, CONNECTION_POSE),
              ('co2-connected', 0, False, CONNECTION_POSE),
              ('startup-gas', 0, True, startup_pose())]
    for name, stand_off, pressurised, pose in states:
        if wanted and name not in wanted:
            continue
        path = OUT / f'{name}.step'
        scenes.original._export_colored(assembly(stand_off, pressurised), path, mesh=True)
        jobs.append(dict(step=str(path.relative_to(scenes.HARDWARE)),
                         out=str(ART / f'{name}.png'), cam=pose['cam'], target=pose['target'],
                         span=pose['span'], size=f"{pose['size'][0]}x{pose['size'][1]}",
                         up=(0, 0, 1), bg='#f2eee8', transparent=True, solid=True,
                         ortho=True, trim=False, ground=False, fog=False))
        metadata['scenes'][name] = anchor_metadata(stand_off, pressurised, pose)
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
