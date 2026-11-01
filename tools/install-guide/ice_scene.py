#!/usr/bin/env python3
"""Model and render ice in the owner guides' frozen first-pour scene."""
from pathlib import Path
import argparse
import json
import math
import sys

import cadquery as cq
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
OUT = HARDWARE / 'install-guide/out/ice'
SOURCE = HARDWARE / 'install-guide/out/pour-legibility/pour-running.step'
sys.path.insert(0, str(HARDWARE / 'scripts'))
from _cadq_export import _per_solid_color
import _hsm_render
import _mesh_payload
from flute_payload import read_payload

GLASS_CENTER = (0, -133.99672200476698)
CAMERA = (1, -1.8, .67)


def scene():
    meshes = read_payload(SOURCE.with_suffix('.step.mesh'))
    if not meshes:
        raise ValueError(f'No frozen first-pour payload at {SOURCE}')
    result = cq.Assembly(name='first-pour-with-ice')
    length = math.hypot(*CAMERA[:2])
    front = (CAMERA[0] / length, CAMERA[1] / length)
    right = (-front[1], front[0])
    cubes = [
        (-14, -8, 78, (21, 21, 23), (11, -8, 18)),
        (15, -10, 79, (21, 21, 22), (-9, 12, -19)),
        (0, 15, 76, (22, 21, 24), (8, -9, 34)),
    ]
    layers = [
        (14.8, 10.3, -12, (18.8, 19.0, 16.8)),
        (33.4, 10.8, 14, (20.0, 19.7, 17.2)),
        (51.9, 11.1, -5, (20.4, 20.1, 17.0)),
    ]
    turns = [(-2, 2, -2), (2, -1, 2), (-1, -2, -3), (1, 2, 3)]
    alignment = math.degrees(math.atan2(right[1], right[0]))
    for z, spread, yaw, size in layers:
        angle = math.radians(yaw)
        for (u, v), (rx, ry, rz) in zip(
                [(-spread, -spread), (spread, -spread),
                 (spread, spread), (-spread, spread)], turns):
            u, v = (u*math.cos(angle)-v*math.sin(angle),
                    u*math.sin(angle)+v*math.cos(angle))
            cubes.append((u, v, z, size, (rx, ry, alignment-yaw+rz)))
    for i, (u, v, z, size, angles) in enumerate(cubes, 1):
        cube = cq.Workplane('XY').box(*size).edges().fillet(2.1)
        for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), angles):
            cube = cube.rotate((0, 0, 0), axis, angle)
        x = GLASS_CENTER[0] + right[0]*u + front[0]*v
        y = GLASS_CENTER[1] + right[1]*u + front[1]*v
        cube = cube.translate((x, y, z))
        result.add(cube, name=f'ice-{i}', color=cq.Color(.83, .92, .97))
    ice = _mesh_payload.from_assembly(_per_solid_color(result))
    light = np.asarray((-.25, -.65, 1.))
    light /= np.linalg.norm(light)

    def linear(hex_color):
        rgb = np.asarray([int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)])
        return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055)**2.4)

    dark, pale = linear('7594a8'), linear('f0f9ff')
    for mesh in ice:
        normals = np.asarray(mesh['nrm']).reshape(-1, 3)
        t = np.clip(.25 + .8 * (normals @ light), 0, 1)[:, None]
        mesh['col'] = ((1-t)*dark + t*pale).ravel().tolist()
    drink = next((m for m in meshes if m['name'] == 'drink'), None)
    if drink is None:
        raise ValueError('The frozen first-pour scene has no cola')
    back = dict(drink, name='cola-depth')
    normals = np.asarray(drink['nrm']).reshape(-1, 3)
    indices = np.asarray(drink['idx']).reshape(-1, 3)
    keep = normals[indices, 2].sum(axis=1) < 1.5
    drink['idx'] = indices[keep].ravel().tolist()
    faces, offset = [], 0
    for lo, hi in zip(drink['fac'][::2], drink['fac'][1::2]):
        count = int(keep[lo:hi+1].sum())
        if count:
            faces.extend((offset, offset+count-1))
            offset += count
    drink['fac'] = faces
    target = OUT / 'pour-with-ice.step.mesh'
    _mesh_payload.write([*meshes, *ice, back], target)
    return target


def materials(style, opacity):
    return [
        dict(names=['cola-depth'], color='#351a0f', unlit=True, side='back'),
        dict(names=['glass'], color='#d6e8ec', opacity=.045, roughness=.15,
             metalness=.05, depth_write=False, side='double', order=10),
        dict(names=['glass-rim', 'glass-base'], color='#edf2f3', unlit=True, side='front'),
        dict(names=['drink'], color='#351a0f', unlit=True, opacity=opacity,
             depth_write=opacity == 1, side='front', order=2),
        dict(names=['drink-top'], color='#6f422b', unlit=True, opacity=opacity,
             depth_write=opacity == 1, side='front', order=3),
        dict(names=['ice-*'], color='#ffffff', unlit=True, tone_mapped=False,
             vertex_colors=True, opacity=.78 if style == 'clear' else 1,
             depth_write=True, side='front', order=1),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style', choices=['frosted', 'clear'], default='clear')
    parser.add_argument('--cola-opacity', type=float, default=.82)
    parser.add_argument('--compare', action='store_true')
    args = parser.parse_args()
    if not 0 < args.cola_opacity <= 1:
        parser.error('--cola-opacity must be between 0 and 1')
    OUT.mkdir(parents=True, exist_ok=True)
    payload = scene()
    entries = []
    for opacity in ([.70, .82] if args.compare else [args.cola_opacity]):
        directory = OUT / f'cola-{round(opacity*100)}'
        directory.mkdir(exist_ok=True)
        job = dict(payload=str(payload), out=str(directory / 'pour-base.png'),
                   materials=materials(args.style, opacity),
                   hide=['countertop', 'glass-edge-*', 'glass-highlight-*',
                         'glass-rim-edge', 'glass-base-edge'],
                   cam=CAMERA, target=(0, -78, 119), span=140,
                   size='1600x1500', up=(0, 0, 1), bg='#ffffff', transparent=True,
                   solid=True, ortho=True, trim=False, ground=False, fog=False)
        entries.append(job)
    jobs = OUT / 'jobs.json'
    jobs.write_text(json.dumps(entries, indent=2)+'\n')
    _hsm_render.render(entries)
    for job in entries:
        print(job['out'])


if __name__ == '__main__':
    main()
