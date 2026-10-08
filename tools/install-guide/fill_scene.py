#!/usr/bin/env python3
"""Render concentrate bottles and a framed Fill screen from the current appliance."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys

import cadquery as cq
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
DIR = HARDWARE / 'install-guide'
OUT = DIR / 'out/fill-redesign'
SOURCE = HARDWARE / 'manifold-layout/enclosure-assembly.step'
FACTS = SOURCE.with_suffix('.facts.json')
RENDERER = ROOT / 'tools/render/render-step-posed.js'
sys.path.insert(0, str(HARDWARE / 'scripts'))
sys.path.insert(0, str(HARDWARE / 'printed-parts/enclosure/enclosure'))
from _cadq_export import _per_solid_color
import _mesh_payload
from flute_payload import read_payload
import _swept_top
import _enclosure_interface

ASSEMBLY_FACTS = json.loads(FACTS.read_text())
FUNNEL_BOUNDS = ASSEMBLY_FACTS['bodies']['funnel']
# This approach pose keeps the bottle mouth 34 mm above the funnel brim.
MOUTH = ((FUNNEL_BOUNDS[0] + FUNNEL_BOUNDS[3]) / 2,
         (FUNNEL_BOUNDS[1] + FUNNEL_BOUNDS[4]) / 2, FUNNEL_BOUNDS[5] + 34)
CAMERA = (.65, -1, .5)
DISPLAY_PROFILE = _swept_top.profile(ASSEMBLY_FACTS['box']['outer'])
SCREEN = dict(width=103.5, height=62.1, angle_deg=_swept_top.ANGLE,
              origin=[p - n * (_enclosure_interface.display_bezel_depth - 1 - .05)
                      for p, n in zip(DISPLAY_PROFILE['origin'], DISPLAY_PROFILE['normal'])])
EXTERIOR = {'funnel', 'funnel-frame', 'nameplate', 'nameplate-ink', 'enclosure-front-top',
            'enclosure-front-bottom', 'enclosure-back-top', 'enclosure-back-bottom'}


def visible(name):
    return name.split('/')[0] in EXTERIOR or 'display' in name


def bottle():
    a = cq.Assembly(name='concentrate-bottle')
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
    liquid = inside.intersect(cq.Workplane('XY').box(80, 80, 186,
                                                   centered=(True, True, False)))
    grip = cq.Workplane('XY').workplane(offset=2).circle(15.2).circle(13.4).extrude(17)
    a.add(shell.translate(MOUTH), name='bottle-pet', color=cq.Color(.85, .89, .9))
    a.add(liquid.translate(MOUTH), name='bottle-concentrate', color=cq.Color(.22, .09, .035))
    a.add(grip.translate(MOUTH), name='bottle-collar', color=cq.Color(.065, .065, .065))
    for i in range(36):
        rib = (cq.Workplane('XY').box(1.1, .8, 14)
               .translate((15.25, 0, 10.5)).rotate((0, 0, 0), (0, 0, 1), i*10))
        a.add(rib.translate(MOUTH), name=f'bottle-grip-{i}', color=cq.Color(.08, .08, .08))
    for z, radius, height in [(0, 14.5, 1.6), (20.5, 15.4, 1.8), (24, 14.6, 1.2)]:
        ring = cq.Workplane('XY').workplane(offset=z).circle(radius).circle(11.5).extrude(height)
        a.add(ring.translate(MOUTH), name=f'bottle-ring-{z}', color=cq.Color(.81, .85, .86))
    return a


def scene():
    original = cq.Assembly.load(str(SOURCE))
    props = bottle()
    a = cq.Assembly(name='fill-with-concentrate')
    for child in original.children:
        if visible(child.name):
            a.add(child)
    for child in props.children:
        a.add(child)
    path = OUT / 'fill.step'
    _per_solid_color(a).export(str(path))
    current = read_payload(SOURCE.with_suffix('.step.mesh'))
    assert current
    meshes = [m for m in current if visible(m['name'])]
    meshes.extend(_mesh_payload.from_assembly(props))
    _mesh_payload.write(meshes, path.with_suffix('.step.mesh'), src=_mesh_payload.source_digest(path))
    return path


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
    return 'data:image/svg+xml;base64,'+base64.b64encode(svg.encode()).decode()


def renderer():
    source = RENDERER.read_text()

    def replace(old, new):
        nonlocal source
        assert source.count(old) == 1, old
        source = source.replace(old, new)

    replace('from "./browser.js"', f'from {(RENDERER.parent/"browser.js").as_uri()!r}')
    replace('from "../../web/server.js"', f'from {(ROOT/"web/server.js").as_uri()!r}')
    replace('import sharp from "sharp";', f'import {{ createRequire }} from "module"; const sharp = createRequire({str(RENDERER)!r})("sharp");')
    replace('const REPO_ROOT = path.resolve(__dirname, "..", "..");', f'const REPO_ROOT = {str(ROOT)!r};')
    replace('const opts = defaults();\n  if (entry.cam', 'const opts = defaults();\n  opts.labelUrl = entry.labelUrl;\n  opts.fillScreen = entry.fillScreen;\n  opts.view = entry.view;\n  opts.mouth = entry.mouth;\n  opts.screen = entry.screen;\n  if (entry.cam')
    replace('if (page && pageSize === want) {', 'if (false) {')
    replace('renderer.render(scene, cam);', (Path(__file__).with_name('fill_materials.js')).read_text()+'\nrenderer.render(scene, cam);')
    path = OUT/'render-fill.mjs'; path.write_text(source)
    return path


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
    step = scene()
    screen = 'data:image/png;base64,'+base64.b64encode((DIR/'assets/fill-screen.png').read_bytes()).decode()
    jobs = []
    for kind in (['neutral', 'pepsi'] if args.compare else [args.label]):
        jobs.append(dict(step=str(step.relative_to(HARDWARE)), out=str(OUT/f'fill-{kind}.png'),
                         labelUrl=label(kind), fillScreen=screen, view='fill', mouth=MOUTH, screen=SCREEN,
                         cam=CAMERA, target=(0, 140, 465), span=265, size='1600x1500',
                         up=(0, 0, 1), bg='#ffffff', transparent=True, solid=True,
                         ortho=True, trim=False, ground=False, fog=False))
        jobs.append(dict(jobs[-1], out=str(OUT/f'bottle-{kind}.png'), view='bottle',
                         target=(MOUTH[0], MOUTH[1], MOUTH[2] + 102), span=114, size='900x1350', trim=True))
    jobs.append(dict(jobs[0], out=str(OUT/'fill-screen-framed.png'), view='frame',
                     cam=DISPLAY_PROFILE['normal'], target=SCREEN['origin'], span=46,
                     size='1800x1020', trim=True))
    if args.scale <= 0:
        parser.error('--scale must be positive')
    for job in jobs:
        job['size'] = 'x'.join(str(round(int(value) * args.scale))
                               for value in job['size'].split('x'))
    manifest = OUT/'jobs.json'; manifest.write_text(json.dumps(jobs, indent=2)+'\n')
    subprocess.run(['node', str(renderer()), '--jobs', str(manifest)], cwd=ROOT, check=True)
    if args.publish:
        publish(args)
    for job in jobs:
        print(job['out'])


def publish(args):
    fill = OUT / f'fill-{args.label}.png'
    frame = OUT / 'fill-screen-framed.png'
    if args.scale == 1:
        targets = [(fill, DIR / 'assets/reference/fill-ready.png'),
                   (frame, DIR / 'assets/reference/fill-screen-framed.png')]
        for source, target in targets:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        right = (1 / math.hypot(1, CAMERA[0]), CAMERA[0] / math.hypot(1, CAMERA[0]))
        side = [MOUTH[0] + 42.5 * right[0], MOUTH[1] + 42.5 * right[1]]
        inputs = dict(
            sources={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (SOURCE, SOURCE.with_suffix('.step.mesh'), FACTS,
                               Path(_swept_top.__file__).resolve(),
                               Path(_enclosure_interface.__file__).resolve(),
                               Path(__file__), Path(__file__).with_name('fill_materials.js'))},
            funnel_bounds=FUNNEL_BOUNDS, bottle_mouth=MOUTH, screen=SCREEN,
            pose=dict(cam=CAMERA, target=(0, 140, 465), span=265, size=(1600, 1500)),
            arrow=dict(start=[*side, MOUTH[2] + 175], end=[*side, MOUTH[2] + 5]),
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
