#!/usr/bin/env python3
"""Render concentrate bottles, the closed funnel and a framed Fill screen from the current appliance."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import shutil
import sys

import cadquery as cq
import cairosvg
import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
DIR = HARDWARE / 'install-guide'
OUT = DIR / 'out/fill-redesign'
SOURCE = HARDWARE / 'manifold-layout/enclosure-assembly.step'
FACTS = SOURCE.with_suffix('.facts.json')
sys.path.insert(0, str(HARDWARE / 'scripts'))
sys.path.insert(0, str(HARDWARE / 'printed-parts/enclosure/enclosure'))
import _hsm_render
import _mesh_payload
from flute_payload import read_payload
import _swept_top
import _enclosure_interface

ASSEMBLY_FACTS = json.loads(FACTS.read_text())
FUNNEL_BOUNDS = ASSEMBLY_FACTS['bodies']['funnel']
# Poured from the front, base toward the cabinet door and tipped TIP degrees past level, which
# empties it: the mouth over the centre of the funnel's, the bottle's lowest point CLEARANCE mm
# over the brim.
TIP = 20
CLEARANCE = 3
AXIS = (0, -math.cos(math.radians(TIP)), math.sin(math.radians(TIP)))  # mouth to base
CAMERA = (1, -.5, .45)
TARGET = (0, 150, 380)
SPAN = 230
SWING_R, SWING_FROM = 225, 0
DISPLAY_PROFILE = _swept_top.profile(ASSEMBLY_FACTS['box']['outer'])
SCREEN = dict(width=103.5, height=62.1, angle_deg=_swept_top.ANGLE,
              origin=[p - n * (_enclosure_interface.display_bezel_depth - 1 - .05)
                      for p, n in zip(DISPLAY_PROFILE['origin'], DISPLAY_PROFILE['normal'])])
EXTERIOR = {'funnel', 'funnel-cover', 'funnel-frame', 'nameplate', 'nameplate-ink',
            'enclosure-front-top', 'enclosure-front-bottom', 'enclosure-back-top',
            'enclosure-back-bottom'}


def visible(name):
    return name.split('/')[0] in EXTERIOR or 'display' in name


def bottle():
    """The bottle as it pours, and the centre of its mouth.

    Built mouth down at the origin, then tipped about the mouth toward the cabinet door. The
    concentrate keeps its volume and settles level.
    """
    outer = (cq.Workplane('XZ').moveTo(0, 0).lineTo(13.5, 0)
             .lineTo(13.5, 23).threePointArc((14.3, 29), (18, 34))
             .lineTo(29, 52).threePointArc((31.8, 58), (32, 66))
             .lineTo(32.5, 190).threePointArc((31.9, 198), (27.5, 202))
             .lineTo(0, 202).close().revolve())
    inside = (cq.Workplane('XZ').moveTo(0, -1).lineTo(11.5, -1)
              .lineTo(11.5, 24).lineTo(16.4, 34).lineTo(28, 53)
              .threePointArc((30.7, 60), (31, 66)).lineTo(31.5, 190)
              .threePointArc((30.9, 196), (26, 198)).lineTo(0, 198)
              .close().revolve())
    recess = (cq.Workplane('XZ').moveTo(0, 200).lineTo(16, 200)
              .threePointArc((21, 201), (25, 203)).lineTo(25, 206)
              .lineTo(0, 206).close().revolve())
    shell = outer.cut(inside).cut(recess)
    volume = (inside.intersect(cq.Workplane('XY').box(80, 80, 186, centered=(True, True, False)))
              .val().Volume())
    grip = cq.Workplane('XY').workplane(offset=2).circle(15.2).circle(13.4).extrude(17)
    parts = [(shell, 'bottle-pet', cq.Color(.85, .89, .9)),
             (grip, 'bottle-collar', cq.Color(.065, .065, .065))]
    for i in range(36):
        rib = (cq.Workplane('XY').box(1.1, .8, 14)
               .translate((15.25, 0, 10.5)).rotate((0, 0, 0), (0, 0, 1), i*10))
        parts.append((rib, f'bottle-grip-{i}', cq.Color(.08, .08, .08)))
    for z, radius, height in [(0, 14.5, 1.6), (20.5, 15.4, 1.8), (24, 14.6, 1.2)]:
        ring = cq.Workplane('XY').workplane(offset=z).circle(radius).circle(11.5).extrude(height)
        parts.append((ring, f'bottle-ring-{z}', cq.Color(.81, .85, .86)))

    def tipped(shape):
        return shape.rotate((0, 0, 0), (1, 0, 0), 90 - TIP)

    parts = [(tipped(shape), name, color) for shape, name, color in parts]
    inside = tipped(inside)
    bounds = inside.val().BoundingBox()

    def settled(level):
        return inside.intersect(cq.Workplane('XY', origin=(0, 0, bounds.zmin - 1))
                                .box(400, 400, level - bounds.zmin + 1,
                                     centered=(True, True, False)))

    low, high = bounds.zmin, bounds.zmax
    for _ in range(20):
        level = (low + high) / 2
        low, high = (level, high) if settled(level).val().Volume() < volume else (low, level)
    parts.insert(1, (settled(low), 'bottle-concentrate', cq.Color(.22, .09, .035)))
    lowest = min(shape.val().BoundingBox().zmin for shape, _, _ in parts)
    mouth = (*ASSEMBLY_FACTS['box']['funnel'], FUNNEL_BOUNDS[5] + CLEARANCE - lowest)
    a = cq.Assembly(name='concentrate-bottle')
    for shape, name, color in parts:
        a.add(shape.translate(mouth), name=name, color=color)
    return a, mouth


def scene():
    props, mouth = bottle()
    current = read_payload(SOURCE.with_suffix('.step.mesh'))
    if not current:
        raise ValueError(f'No appliance payload at {SOURCE}')
    meshes = [m for m in current if visible(m['name'])]
    enclosure = next(m for m in meshes if m['name'] == 'enclosure-back-top')
    cover = next(m for m in meshes if m['name'] == 'display-cover')
    cover['color'] = enclosure['color']
    meshes.extend(_mesh_payload.from_assembly(props))

    def surface(name, positions, normals, uv, indices):
        return dict(name=name, color=[1., 1., 1.], pos=np.asarray(positions).ravel().tolist(),
                    nrm=np.asarray(normals).ravel().tolist(), uv=np.asarray(uv).ravel().tolist(),
                    idx=indices, fac=[0, len(indices)//3-1])

    def transformed(points, angle, origin):
        c, s = math.cos(angle), math.sin(angle)
        matrix = np.asarray(((1, 0, 0), (0, c, -s), (0, s, c)))
        return np.asarray(points) @ matrix.T + origin

    w, h = SCREEN['width']/2, SCREEN['height']/2
    angle = math.radians(SCREEN['angle_deg'])
    positions = transformed([(-w, -h, 0), (w, -h, 0), (-w, h, 0), (w, h, 0)],
                            angle, SCREEN['origin'])
    normal = transformed([(0, 0, 1)], angle, (0, 0, 0))[0]
    meshes.append(surface('guide-fill-screen', positions, [normal]*4,
                          [(0, 0), (1, 0), (0, 1), (1, 1)], [0, 1, 2, 1, 3, 2]))

    tilt = math.radians(90-TIP)
    angle = math.atan2(CAMERA[1]*math.cos(tilt)+CAMERA[2]*math.sin(tilt), CAMERA[0])
    count = 160
    positions, normals, uv, indices = [], [], [], []
    for j in range(2):
        z, radius = 72+j*106, 32.25+j*.43
        for i in range(count+1):
            u = i/count
            theta = angle+2*math.pi*(u-.5)
            positions.append((radius*math.cos(theta), radius*math.sin(theta), z))
            normals.append((math.cos(theta), math.sin(theta), 0))
            uv.append((1-u, 1-j))
    for i in range(count):
        indices.extend((i, i+1, count+1+i, i+1, count+2+i, count+1+i))
    positions = transformed(positions, tilt, mouth)
    normals = transformed(normals, tilt, (0, 0, 0))
    meshes.append(surface('bottle-label', positions, normals, uv, indices))
    path = OUT / 'fill.step.mesh'
    _mesh_payload.write(meshes, path)
    return path, mouth


def label(kind):
    font = TTFont(DIR / 'fonts/Plex-Bold.ttf')
    glyphs = font.getGlyphSet()
    mapping = font.getBestCmap()

    def text(value, y, size, color='#101828'):
        advances = [font['hmtx'][mapping[ord(c)]][0] for c in value]
        scale = size / font['head'].unitsPerEm
        pieces = []
        x = -sum(advances)/2
        for char, advance in zip(value, advances):
            pen = SVGPathPen(glyphs); glyphs[mapping[ord(char)]].draw(pen)
            pieces.append(f'<path transform="translate({x} 0)" d="{pen.getCommands()}"/>')
            x += advance
        return f'<g fill="{color}" transform="translate(600 {y}) scale({scale} {-scale})">'+''.join(pieces)+'</g>'

    if kind == 'pepsi':
        pieces = ['<rect width="1200" height="560" fill="#0755d6"/>',
                  '<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="2" fill="#fff" opacity=".12"/></pattern><clipPath id="globe"><circle cx="600" cy="306" r="177"/></clipPath></defs>',
                  '<rect width="1200" height="560" fill="url(#dots)"/>',
                  '<ellipse cx="600" cy="0" rx="214" ry="120" fill="#fff"/>',
                  text('sodastream', 48, 35, '#13386e'), text('drink mix', 85, 24, '#13386e'),
                  '<circle cx="600" cy="306" r="188" fill="#fff"/><circle cx="600" cy="306" r="181" fill="#141414"/>',
                  '<g clip-path="url(#globe)"><rect x="414" y="120" width="372" height="372" fill="#043dbd"/><path d="M414 265 L414 120 H786 V265 Q610 223 414 265" fill="#f32139"/><path d="M414 265 Q610 223 786 265 V355 Q610 393 414 355 Z" fill="#fff"/></g>',
                  text('PEPSI', 338, 80, '#080808'), text('440 mL', 532, 29, '#fff')]
    else:
        pieces = ['<rect width="1200" height="560" fill="#f2f0e5"/>',
                  '<rect y="18" width="1200" height="54" fill="#173581"/>',
                  text('DRINK MIX', 59, 29, '#fff'),
                  '<path d="M0 118 H1200 M0 462 H1200" stroke="#c8c8bf" stroke-width="3"/>',
                  text('COLA', 303, 112, '#153383'),
                  text('CONCENTRATE', 365, 40, '#153383'),
                  text('SodaStream-compatible', 429, 26, '#505661'),
                  text('440 mL', 522, 31, '#153383')]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560">'+''.join(pieces)+'</svg>'
    (OUT/f'label-{kind}.svg').write_text(svg)
    target = OUT / f'label-{kind}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target))
    return str(target)


def materials(label):
    return [
        dict(names=['guide-fill-screen'], texture=str(DIR/'assets/fill-screen.png'),
             unlit=True, tone_mapped=False, side='front'),
        dict(names=['bottle-pet'], color='#dce9ee', opacity=.065, depth_write=False,
             roughness=.18, metalness=.02, clearcoat=.5, clearcoat_roughness=.18,
             side='front', order=5),
        dict(names=['bottle-concentrate'], color='#361b0d', roughness=.62, metalness=0,
             side='front'),
        dict(names=['bottle-ring-*'], color='#9daeb4', opacity=.63, roughness=.18,
             metalness=.08, depth_write=False, side='front', order=6),
        dict(names=['bottle-grip-*', 'bottle-collar'], color='#17191a', roughness=.42,
             metalness=0, side='front'),
        dict(names=['display/2'], color='#11151a', unlit=True, side='front'),
        dict(names=['bottle-label'], texture=label, roughness=.62, metalness=.015,
             side='front'),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', choices=['neutral', 'pepsi'], default='neutral')
    parser.add_argument('--compare', action='store_true')
    parser.add_argument('--scale', type=float, default=1,
                        help='render scale with the same camera and scene coordinates')
    parser.add_argument('--publish', action='store_true',
                        help='copy registered reference artwork or print artwork to the install guide')
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    payload, mouth = scene()
    jobs = []
    for kind in (['neutral', 'pepsi'] if args.compare else [args.label]):
        jobs.append(dict(payload=str(payload), out=str(OUT/f'fill-{kind}.png'),
                         materials=materials(label(kind)), hide=['funnel-cover'],
                         cam=CAMERA, target=TARGET, span=SPAN, size='1600x1500',
                         up=(0, 0, 1), bg='#ffffff', transparent=True, solid=True,
                         ortho=True, trim=False, ground=False, fog=False))
        jobs.append(dict(jobs[-1], out=str(OUT/f'bottle-{kind}.png'),
                         only=['bottle-*'], context='hide',
                         target=[m + 102 * a for m, a in zip(mouth, AXIS)], span=114,
                         size='1350x900', trim=True))
    jobs.append(dict(jobs[0], out=str(OUT/'fill-screen-framed.png'),
                     only=['display', 'display-cover', 'display-gasket', 'guide-fill-screen'],
                     context='hide',
                     cam=DISPLAY_PROFILE['normal'], target=SCREEN['origin'], span=46,
                     size='1800x1020', trim=True))
    jobs.append(dict(jobs[0], out=str(OUT/'fill-closed.png'), hide=['bottle-*']))
    if args.scale <= 0:
        parser.error('--scale must be positive')
    for job in jobs:
        job['size'] = 'x'.join(str(round(int(value) * args.scale))
                               for value in job['size'].split('x'))
    manifest = OUT/'jobs.json'; manifest.write_text(json.dumps(jobs, indent=2)+'\n')
    _hsm_render.render(jobs)
    if args.publish:
        publish(args, mouth)
    for job in jobs:
        print(job['out'])


def publish(args, mouth):
    fill = OUT / f'fill-{args.label}.png'
    frame = OUT / 'fill-screen-framed.png'
    closed = OUT / 'fill-closed.png'
    if args.scale == 1:
        targets = [(fill, DIR / 'assets/reference/fill-ready.png'),
                   (frame, DIR / 'assets/reference/fill-screen-framed.png'),
                   (closed, DIR / 'assets/reference/fill-closed.png')]
        for source, target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        # The motion cue: the base's swing round the mouth as it tips, just beyond the base.
        swing = [[mouth[0], mouth[1] - SWING_R * math.cos(math.radians(angle)),
                  mouth[2] + SWING_R * math.sin(math.radians(angle))]
                 for angle in range(SWING_FROM, TIP + 1, 2)]
        inputs = dict(
            sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (SOURCE, SOURCE.with_suffix('.step.mesh'), FACTS,
                               Path(_swept_top.__file__).resolve(),
                               Path(_enclosure_interface.__file__).resolve(),
                               Path(__file__), Path(_hsm_render.__file__).resolve(),
                               Path(_mesh_payload.__file__).resolve(),
                               ROOT/'web/public/finishes.json',
                               *sorted((ROOT/'tools/hsm/render').rglob('*.rs')),
                               *sorted((ROOT/'tools/hsm/render').rglob('*.wgsl')))},
            funnel_bounds=FUNNEL_BOUNDS, bottle_mouth=mouth, bottle_tip=TIP, screen=SCREEN,
            pose=dict(cam=CAMERA, target=TARGET, span=SPAN, size=(1600, 1500)),
            arrow=swing,
            artwork={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for _, p in targets},
        )
        (DIR / 'assets/fill-scene-inputs.json').write_text(json.dumps(inputs, indent=2) + '\n')
    else:
        install = HARDWARE / 'install-guide/assets'
        resolution_file = install / 'print-resolution.json'
        resolutions = json.loads(resolution_file.read_text())
        for source, name, reference in [
            (fill, 'steps/fill-ready.png', DIR / 'assets/reference/fill-ready.png'),
            (frame, 'fill-screen-framed.png', DIR / 'assets/reference/fill-screen-framed.png'),
            (closed, 'steps/fill-closed.png', DIR / 'assets/reference/fill-closed.png'),
        ]:
            target = install / name
            shutil.copy2(source, target)
            reference_size = Image.open(reference).size
            render_size = Image.open(target).size
            resolutions['assets'][name] = dict(
                reference_size=reference_size, render_size=render_size,
                scale=[a / b for a, b in zip(render_size, reference_size)],
                coordinate_reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest(),
                render_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
            )
        resolution_file.write_text(json.dumps(resolutions, indent=2) + '\n')


if __name__ == '__main__':
    main()
