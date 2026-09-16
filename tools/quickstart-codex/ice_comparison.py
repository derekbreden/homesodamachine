#!/usr/bin/env python3
"""Compose cola opacity samples at detail and quick-start illustration sizes."""
from pathlib import Path
import shutil
import subprocess
import sys

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

from contours import Contours, PAD

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/quickstart-codex'
OUT = DIR / 'out/ice'
PDF = OUT / 'cola-opacity.pdf'
W, H = 792, 612
for name in ['Regular', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR/'fonts'/f'Plex-{name}.ttf')))
c = canvas.Canvas(str(PDF), pagesize=(W, H), invariant=1)
c.setTitle('Ice in cola - opacity comparison')
c.setAuthor('Derek Bredensteiner')
contours = Contours('#46515b')


def text(s, x, y, size=11, font='Regular', color='#202337'):
    c.setFillColor(HexColor(color)); c.setFont(font, size)
    c.drawString(x, H-y-size*.8, s)


def picture(source, x, y, w, h, bounds):
    a, b, cc, d = bounds
    scale = min(w/(cc-a), h/(d-b))
    iw, ih = (cc-a)*scale, (d-b)*scale
    target, (pw, ph) = contours.picture(source, bounds, iw, ih)
    if target.exists():
        c.drawImage(str(target), x+(w-iw)/2-PAD, H-y-(h+ih)/2-PAD,
                    width=pw, height=ph, mask='auto')


text('Ice in the first glass', 30, 27, 27, 'Bold', '#10319C')
text('Front cola opacity varies; the depth stays dark brown.', 30, 64, 12)
for i, (opacity, title) in enumerate([(100, 'Opaque'), (92, '92% opacity'),
                                     (82, '82% opacity'), (70, '70% opacity')]):
    x = 30+i*188
    source = OUT/f'cola-{opacity}/pour-base.png'
    shutil.copy2(DIR/'art/edge-study/pour-glass-mask.png', source.parent/'pour-glass-mask.png')
    text(title, x, 105, 15, 'Bold', '#1749D1')
    picture(source, x, 134, 166, 238, (439, 820, 858, 1495))
    text('QUICK START SIZE', x, 399, 8.5, 'Bold', '#606A78')
    picture(source, x-5, 422, 176, 149, (150, 95, 1475, 1495))
text('Larger glass detail above; the current 19 x 13 inch sheet scale below.',
     30, 588, 10, color='#606A78')
c.showPage(); c.save()
if contours.pending:
    contours.render()
    subprocess.run([sys.executable, str(Path(__file__).resolve())], cwd=ROOT, check=True)
    sys.exit(0)
subprocess.run(['pdftoppm', '-scale-to', '1800', '-singlefile', '-png',
                str(PDF), str(OUT/'cola-opacity')], check=True)
print(PDF)
