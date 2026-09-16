#!/usr/bin/env python3
"""Compose bottle options and the framed enclosure display at reading size."""
from pathlib import Path
import subprocess
import sys

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from contours import Contours, PAD

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT/'hardware/quickstart-codex'
OUT = DIR/'out/fill-redesign'
PDF = OUT/'step6-options.pdf'
W, H = 792, 612
for name in ['Regular', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR/'fonts'/f'Plex-{name}.ttf')))
c = canvas.Canvas(str(PDF), pagesize=(W,H), invariant=1)
c.setTitle('Step 6 - concentrate and enclosure display')
c.setAuthor('Derek Bredensteiner')
contours = Contours('#46515b')


def text(value, x, y, size=11, font='Regular', color='#202337'):
    c.setFillColor(HexColor(color)); c.setFont(font, size)
    c.drawString(x, H-y-size*.8, value)


def picture(source, x, y, w, h, bounds=None, fade_crops=True):
    if bounds is None:
        with Image.open(source) as im:
            bounds = (0, 0, im.width, im.height)
    a, b, cc, d = bounds
    scale = min(w/(cc-a), h/(d-b))
    iw, ih = (cc-a)*scale, (d-b)*scale
    target, (pw,ph) = contours.picture(source, bounds, iw, ih, fade_crops=fade_crops)
    if target.exists():
        c.drawImage(str(target), x+(w-iw)/2-PAD, H-y-(h+ih)/2-PAD,
                    width=pw, height=ph, mask='auto')


text('Step 6: concentrate and display', 30, 27, 27, 'Bold', '#10319C')
text('A shaped PET bottle, dark concentrate and a label wrapped around the body.', 30, 65, 12)
for x, kind, title in [(90, 'neutral', 'Simple concentrate label'), (460, 'pepsi', 'Pepsi-style label')]:
    text(title, x, 104, 15, 'Bold', '#1749D1')
    picture(OUT/f'bottle-{kind}.png', x+38, 134, 142, 225)
text('FRAMED ENCLOSURE DISPLAY', 30, 404, 9, 'Bold', '#606A78')
picture(OUT/'fill-screen-framed.png', 30, 432, 240, 130, fade_crops=False)
for x, kind, title in [(352, 'neutral', 'SIMPLE LABEL'), (577, 'pepsi', 'PEPSI-STYLE LABEL')]:
    text(title, x, 404, 9, 'Bold', '#606A78')
    picture(OUT/f'fill-{kind}.png', x, 432, 131, 117, (295,330,1555,1450))
text('Lower row: the proposed quick start illustration sizes.', 30, 587, 10, color='#606A78')
c.showPage(); c.save()
if contours.pending:
    contours.render()
    subprocess.run([sys.executable,str(Path(__file__).resolve())],cwd=ROOT,check=True)
    sys.exit(0)
subprocess.run(['pdftoppm','-scale-to','1800','-singlefile','-png',str(PDF),str(OUT/'step6-options')],check=True)
print(PDF)
