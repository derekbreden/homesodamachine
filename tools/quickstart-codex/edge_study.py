#!/usr/bin/env python3
"""Compose page-space silhouette treatments for the quick-start artwork."""
from pathlib import Path
import html
import json
import math
import shutil
import subprocess
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/quickstart-codex'
ART = DIR / 'art/edge-study'
OUT = DIR / 'out/edge-study'
W, H = 1368, 936
EXTRA_DEFS = []


def render_subjects():
    source_path = ROOT / 'tools/render/render-step-posed.js'
    source = source_path.read_text()
    source = source.replace('from "./browser.js"', f'from {(source_path.parent / "browser.js").as_uri()!r}')
    source = source.replace('from "../../web/server.js"', f'from {(ROOT / "web/server.js").as_uri()!r}')
    source = source.replace('import sharp from "sharp";', f'import {{ createRequire }} from "module"; const sharp = createRequire({str(source_path)!r})("sharp");')
    source = source.replace('const REPO_ROOT = path.resolve(__dirname, "..", "..");', f'const REPO_ROOT = {str(ROOT)!r};')
    source = source.replace('const opts = defaults();\n  if (entry.cam', 'const opts = defaults();\n  opts.studyMode = entry.studyMode;\n  if (entry.cam')
    source = source.replace('renderer.render(scene, cam);', '''
    currentGroup.traverse((part) => {
      if (!part.isMesh) return;
      if (o.studyMode === "glass-mask") {
        part.visible = part.name === "glass";
        part.material = new THREE.MeshBasicMaterial({color: "#ffffff", side: THREE.DoubleSide});
        return;
      }
      if (part.name === "countertop" || part.name.startsWith("glass-edge-") ||
          part.name.startsWith("glass-highlight-") || part.name === "glass-rim-edge" ||
          part.name === "glass-base-edge") {
        part.visible = false;
      } else if (part.name === "glass") {
        part.material = new THREE.MeshPhysicalMaterial({
          color: "#d6e8ec", opacity: 0.045, transparent: true,
          roughness: 0.15, metalness: 0.05, depthWrite: false, side: THREE.DoubleSide,
        });
        part.renderOrder = 10;
      } else if (part.name === "glass-rim" || part.name === "glass-base") {
        part.material = new THREE.MeshBasicMaterial({color: "#edf2f3"});
      } else if (part.name === "drink") {
        part.material = new THREE.MeshBasicMaterial({color: "#351a0f"});
      } else if (part.name === "drink-top") {
        part.material = new THREE.MeshBasicMaterial({color: "#6f422b"});
      }
    });
    renderer.render(scene, cam);''')
    renderer = OUT / 'render-subjects.mjs'
    renderer.write_text(source)
    jobs = []
    for mode in ('base', 'glass-mask'):
        jobs.append(dict(
            step='quickstart-codex/out/pour-legibility/pour-running.step',
            out=str(ART / f'pour-{mode}.png'), studyMode=mode,
            cam=[1, -1.8, .67], target=[0, -78, 119], span=140,
            size='1600x1500', up=[0, 0, 1], bg='#ffffff', transparent=True,
            solid=True, ortho=True, trim=False, ground=False, fog=False,
        ))
    manifest = OUT / 'subjects.json'
    manifest.write_text(json.dumps(jobs, indent=2))
    subprocess.run(['node', str(renderer), '--jobs', str(manifest)], cwd=ROOT, check=True)


def text(s, x, y, size=13, weight=400, color='#202337', tracking=0):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" letter-spacing="{tracking}">{html.escape(s)}</text>'


def rule(x1, y1, x2, y2, color='#d9dcdf'):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width=".6"/>'


def image_tag(path, box):
    x, y, w, h = box
    return f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{path.relative_to(DIR).as_posix()}"/>'


def fit(path, x, y, w, h, crop=None):
    im = Image.open(path)
    a, b, c, d = crop or im.getchannel('A').getbbox()
    scale = min(w / (c-a), h / (d-b))
    ox, oy = x + (w-(c-a)*scale)/2-a*scale, y + (h-(d-b)*scale)/2-b*scale
    return (ox, oy, im.width*scale, im.height*scale)


def glass_lip(box):
    direction = (1, -1.8, .67)
    def unit(v):
        length = math.sqrt(sum(a*a for a in v))
        return [a / length for a in v]
    def cross(a, b):
        return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
    direction = unit(direction)
    right = unit(cross((0, 0, 1), direction))
    up = cross(direction, right)
    points = []
    x, y, w, h = box
    for i in range(129):
        angle = i * 2 * math.pi / 128
        delta = (37*math.cos(angle), -133.99672200476698+37*math.sin(angle)+78, 104-119)
        px = 800 + sum(a*b for a, b in zip(delta, right))*1500/280
        py = 750 - sum(a*b for a, b in zip(delta, up))*1500/280
        points.append((x+px*w/1600, y+py*h/1500))
    return 'M'+'L'.join(f'{px:.3f} {py:.3f}' for px, py in points)+'Z'


def filters():
    return '''
    <filter id="ink" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feComponentTransfer in="SourceAlpha"><feFuncA type="linear" slope="40"/></feComponentTransfer>
      <feMorphology operator="dilate" radius=".6" result="outside"/>
      <feComponentTransfer in="SourceAlpha" result="solid"><feFuncA type="linear" slope="40"/></feComponentTransfer>
      <feComposite in="outside" in2="solid" operator="out" result="edge"/>
      <feFlood flood-color="#75828a"/><feComposite in2="edge" operator="in"/>
    </filter>
    <filter id="selective" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feComponentTransfer in="SourceAlpha" result="solid"><feFuncA type="linear" slope="40"/></feComponentTransfer>
      <feMorphology operator="dilate" radius=".6" result="outside"/>
      <feComposite in="outside" in2="solid" operator="out" result="edge"/>
      <feColorMatrix in="SourceGraphic" type="luminanceToAlpha"/>
      <feComponentTransfer><feFuncA type="linear" slope="2" intercept="-.65"/></feComponentTransfer>
      <feMorphology operator="dilate" radius="1.2"/>
      <feComposite in2="edge" operator="in" result="paleEdge"/>
      <feFlood flood-color="#75828a"/><feComposite in2="paleEdge" operator="in"/>
    </filter>
    <filter id="soft" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feComponentTransfer in="SourceAlpha" result="solid"><feFuncA type="linear" slope="40"/></feComponentTransfer>
      <feGaussianBlur stdDeviation="1.05"/>
      <feComposite in2="solid" operator="out" result="softAlpha"/>
      <feFlood flood-color="#34434c" flood-opacity=".23"/><feComposite in2="softAlpha" operator="in"/>
    </filter>
    <filter id="shadowOnly" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
      <feComponentTransfer in="SourceAlpha" result="solid"><feFuncA type="linear" slope="40"/></feComponentTransfer>
      <feGaussianBlur stdDeviation="1.35"/><feOffset dx=".8" dy="1.35"/>
      <feComposite in2="solid" operator="out" result="shadowAlpha"/>
      <feFlood flood-color="#34434c" flood-opacity=".36"/><feComposite in2="shadowAlpha" operator="in"/>
    </filter>
    '''


def subject(path, box, treatment, glass=False, clip=None):
    raw = image_tag(path, box)
    silhouette = raw
    if glass:
        silhouette += image_tag(ART / 'pour-glass-mask.png', box)
    pieces = []
    if treatment in ('shadow', 'hybrid'):
        pieces.append(f'<g filter="url(#{"shadowOnly" if treatment == "shadow" else "soft"})">{silhouette}</g>')
    if treatment in ('outline', 'hybrid'):
        pieces.append(f'<g filter="url(#{"ink" if treatment == "outline" else "selective"})">{silhouette}</g>')
    pieces.append(raw)
    if glass and treatment in ('outline', 'hybrid'):
        pieces.append(f'<path d="{glass_lip(box)}" fill="none" stroke="#75828a" stroke-width=".6"/>')
    content = ''.join(pieces)
    if not glass:
        x, y, w, h = box
        fade = f'fade{len(EXTRA_DEFS)}'
        EXTRA_DEFS.append(f'''
        <linearGradient id="{fade}-x"><stop offset="0" stop-color="black"/><stop offset=".035" stop-color="white"/>
          <stop offset=".965" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient>
        <linearGradient id="{fade}-y" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white"/>
          <stop offset=".95" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient>
        <mask id="{fade}-mx" maskUnits="userSpaceOnUse" x="{x}" y="{y-8}" width="{w}" height="{h+16}">
          <rect x="{x}" y="{y-8}" width="{w}" height="{h+16}" fill="url(#{fade}-x)"/></mask>
        <mask id="{fade}-my" maskUnits="userSpaceOnUse" x="{x-8}" y="{y}" width="{w+16}" height="{h}">
          <rect x="{x-8}" y="{y}" width="{w+16}" height="{h}" fill="url(#{fade}-y)"/></mask>
        ''')
        content = f'<g mask="url(#{fade}-mx)"><g mask="url(#{fade}-my)">{content}</g></g>'
    return f'<g clip-path="url(#{clip})">{content}</g>' if clip else content


def page():
    EXTRA_DEFS.clear()
    elements = [f'<rect width="{W}" height="{H}" fill="#fff"/>']
    elements += [
        text('HOME SODA MACHINE / VISUAL STUDY', 36, 34, 9, 600, '#5f6872', 1.5),
        text('Let the objects sit on the paper.', 36, 80, 32, 600),
        text('The same scenes, the same size, on white. Only their projected edges change.', 36, 107, 14, 400, '#5f6872'),
        rule(36, 126, 1332, 126),
    ]
    choices = [
        ('A', 'No treatment', 'The white-paper reference.', 'none'),
        ('B', 'Fine contour', 'A quiet, continuous silhouette.', 'outline'),
        ('C', 'Close shadow', 'A soft edge, slightly offset.', 'shadow'),
        ('D', 'Selective contour', 'Pale edges defined; dark parts quieter.', 'hybrid'),
    ]
    cols = [36, 367, 698, 1029]
    defs = [filters()]
    tubing = DIR / 'art/release-with-press.png'
    glass = ART / 'pour-base.png'
    for x, (letter, title, description, treatment) in zip(cols, choices):
        elements.extend([
            text(letter, x, 167, 12, 600, '#d64050'),
            text(title, x+24, 167, 19, 600),
            text(description, x, 191, 11.5, 400, '#5f6872'),
        ])
        elements.append(text('WHITE TUBE + RELEASE TOOL', x, 232, 8.5, 600, '#6d7580', 1.2))
        bounds = (x+9, 252, 281, 140)
        elements.append(subject(tubing, fit(tubing, *bounds), treatment))
        elements.append(text('GLASS + COLA', x, 439, 8.5, 600, '#6d7580', 1.2))
        elements.append(subject(glass, fit(glass, x+14, 454, 272, 264), treatment, glass=True))
        elements.append(rule(x, 740, x+299, 740))
        elements.append(text('SMALLER ON THE GUIDE', x, 763, 8.5, 600, '#6d7580', 1.2))
        elements.append(subject(tubing, fit(tubing, x+8, 784, 120, 60), treatment))
        elements.append(subject(glass, fit(glass, x+179, 773, 81, 101), treatment, glass=True))
    elements.extend([
        rule(36, 897, 1332, 897),
        text('Edges and softness are measured on this page, after projection. The glass rim is also drawn on the page.', 36, 918, 10.5, 400, '#5f6872'),
    ])
    font = 'fonts/Plex-Regular.ttf'
    semibold = 'fonts/Plex-Semibold.ttf'
    return f'''<!doctype html><html><head><meta charset="utf-8"><title>Objects on white paper</title>
    <style>
    @font-face{{font-family:Plex;src:url('{font}');font-weight:400}}
    @font-face{{font-family:Plex;src:url('{semibold}');font-weight:600}}
    *{{box-sizing:border-box}}html,body{{margin:0;width:100%;height:100%;background:white}}
    svg{{display:block;width:100vw;height:100vh;font-family:Plex,sans-serif}}
    </style></head><body><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">
    <defs>{''.join(defs+EXTRA_DEFS)}</defs>{''.join(elements)}</svg></body></html>'''


def build():
    html_path = DIR / 'edge-study.html'
    html_path.write_text('\n'.join(line.rstrip() for line in page().splitlines())+'\n')
    subprocess.run(['node', 'tools/render/render-card.js', str(html_path), str(OUT / 'edge-study.png'),
                    '--size', '5700x3900', '--dpr', '1', '--pdf', '19x13in'], cwd=ROOT, check=True)
    pdf = DIR / 'edge-study.pdf'
    shutil.copyfile(OUT / 'edge-study.pdf', pdf)
    shutil.copyfile(pdf, ROOT / 'output/pdf/quick-start-edge-study.pdf')
    subprocess.run(['pdftoppm', '-scale-to', '1900', '-singlefile', '-png', str(pdf), str(OUT / 'edge-study-review')], check=True)
    cover = Image.open(OUT / 'edge-study-review.png')
    cover.resize((1200, 821), Image.Resampling.LANCZOS).save(DIR / 'edge-study.cover.png')
    (DIR / 'edge-study.pdf.json').write_text(json.dumps({
        'title': 'Quick start - objects on white paper',
        'subtitle': 'Four page-space edge treatments: reference, contour, shadow, and selective contour with a soft halo',
        'pages': 1, 'cover': 'edge-study.cover.png', 'cover_size': [1200, 821],
    }, indent=2)+'\n')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    if '--render-subjects' in sys.argv:
        render_subjects()
    build()
