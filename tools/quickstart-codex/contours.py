"""Fixed-width page silhouettes for the quick-start illustrations."""
from pathlib import Path
import hashlib
import json
import math
import subprocess

from PIL import Image

from edge_study import glass_lip

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'hardware/quickstart-codex/art'
OUT = ROOT / 'hardware/quickstart-codex/out/contours'
PAD = 3
PPI = 432


class Contours:
    def __init__(self, color, width=.6):
        self.color = color
        self.width = width
        self.pending = []
        OUT.mkdir(parents=True, exist_ok=True)

    def picture(self, source, bounds, iw, ih):
        a, b, c, d = bounds
        scale = iw / (c-a)
        source_size = Image.open(source).size
        x, y = PAD-a*scale, PAD-b*scale
        w, h = source_size[0]*scale, source_size[1]*scale
        pw, ph = iw+2*PAD, ih+2*PAD
        pixels = (math.ceil(pw*PPI/72), math.ceil(ph*PPI/72))
        raw = f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{source.as_uri()}"/>'
        silhouette = raw
        lip = ''
        if source.name == 'pour-base.png':
            mask = source.parent / 'pour-glass-mask.png'
            silhouette += f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{mask.as_uri()}"/>'
            lip = f'<path d="{glass_lip((x,y,w,h))}" fill="none" stroke="{self.color}" stroke-width="{self.width}"/>'

        im = Image.open(source).convert('RGBA')
        alpha = im.getchannel('A')
        actual = (max(0,a), max(0,b), min(im.width,c), min(im.height,d))
        aa, bb, cc, dd = actual
        edge_bands = [(aa,bb,aa+1,dd), (cc-1,bb,cc,dd), (aa,bb,cc,bb+1), (aa,dd-1,cc,dd)]
        cut = [max(alpha.crop(band).getdata(),default=0)>100 for band in edge_bands]
        fx, fy = min(3.2,iw*.035)/iw, min(3.2,ih*.05)/ih
        stops_x = [(0,'black' if cut[0] else 'white'),(fx,'white'),(1-fx,'white'),(1,'black' if cut[1] else 'white')]
        stops_y = [(0,'black' if cut[2] else 'white'),(fy,'white'),(1-fy,'white'),(1,'black' if cut[3] else 'white')]
        mx0, mx1 = (PAD if cut[0] else 0), (PAD+iw if cut[1] else pw)
        my0, my1 = (PAD if cut[2] else 0), (PAD+ih if cut[3] else ph)
        def stops(values):
            return ''.join(f'<stop offset="{offset}" stop-color="{color}"/>' for offset,color in values)
        body = f'''<!doctype html><html><head><style>html,body{{margin:0;width:100%;height:100%;background:transparent}}svg{{display:block;width:100vw;height:100vh}}</style></head><body>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {pw} {ph}"><defs>
        <filter id="contour" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
          <feComponentTransfer in="SourceAlpha" result="solid"><feFuncA type="linear" slope="40"/></feComponentTransfer>
          <feMorphology operator="dilate" radius="{self.width}" result="outside"/>
          <feComposite in="outside" in2="solid" operator="out" result="edge"/>
          <feFlood flood-color="{self.color}"/><feComposite in2="edge" operator="in"/>
        </filter>
        <linearGradient id="fade-x">{stops(stops_x)}</linearGradient>
        <linearGradient id="fade-y" x1="0" y1="0" x2="0" y2="1">{stops(stops_y)}</linearGradient>
        <mask id="mx" maskUnits="userSpaceOnUse" x="0" y="0" width="{pw}" height="{ph}">
          <rect x="{mx0}" y="0" width="{mx1-mx0}" height="{ph}" fill="url(#fade-x)"/>
        </mask>
        <mask id="my" maskUnits="userSpaceOnUse" x="0" y="0" width="{pw}" height="{ph}">
          <rect x="0" y="{my0}" width="{pw}" height="{my1-my0}" fill="url(#fade-y)"/>
        </mask>
        </defs><g mask="url(#mx)"><g mask="url(#my)"><g filter="url(#contour)">{silhouette}</g>{raw}{lip}</g></g>
        </svg></body></html>'''
        digest = hashlib.sha256((body+hashlib.sha256(source.read_bytes()).hexdigest()).encode()).hexdigest()[:20]
        target = OUT / f'{digest}.png'
        if not target.exists():
            page = OUT / f'{digest}.html'
            page.write_text('\n'.join(line.rstrip() for line in body.splitlines())+'\n')
            self.pending.append({'html':str(page), 'out':str(target), 'size':pixels})
        return target, (pw,ph)

    def render(self):
        manifest = OUT / f'jobs-{self.color[1:]}.json'
        manifest.write_text(json.dumps(self.pending,indent=2)+'\n')
        subprocess.run(['node',str(Path(__file__).with_name('render-contours.mjs')),str(manifest)],cwd=ROOT,check=True)
