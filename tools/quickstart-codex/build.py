#!/usr/bin/env python3
"""Draw the one-sheet 19 x 13 inch Codex quick start."""
from pathlib import Path
import json
import math
import shutil
import subprocess
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/quickstart-codex'
ART = DIR / 'art'
PDF = DIR / 'quick-start-codex.pdf'
W, H = 19 * 72, 13 * 72
INK = '#1a1a2e'
CORAL = '#d64050'
STONE = '#ded7cd'
MUTED = '#656473'
PALE = '#f2eee8'
for name in ['Regular', 'Semibold', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR / 'fonts' / f'Plex-{name}.ttf')))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold', italic='Regular', boldItalic='Bold')
c = canvas.Canvas(str(PDF), pagesize=(W,H), pageCompression=1)
c.setTitle('Home Soda Machine - Quick start - Codex')
c.setAuthor('Derek Bredensteiner')
c.setSubject('One 19 x 13 inch installation quick start with words')

def rect(x,y,w,h,fill,stroke=None,r=0):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke or fill))
    if r: c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else: c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))

def line(x1,y1,x2,y2,color=STONE,width=.7):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width)
    c.line(x1,H-y1,x2,H-y2)

def text(s,x,y,size=13,font='Regular',color=INK):
    c.setFillColor(HexColor(color)); c.setFont(font,size)
    c.drawString(x,H-y-size*.80,s)

def para(s,x,y,w,size=13,leading=17,color=INK,font='Regular',limit=None):
    p=Paragraph(s,ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,height=p.wrap(w,1000)
    if limit is not None and height>limit: raise ValueError(f'Text overflow: {s[:65]} {height}>{limit}')
    p.drawOn(c,x,H-y-height)
    return height

def label(s,x,y,color=MUTED,size=9):
    c.saveState()
    c.setFillColor(HexColor(color));t=c.beginText(x,H-y-size*.8)
    t.setFont('Bold',size);t.setCharSpace(1.5);t.textOut(s.upper());c.drawText(t)
    c.restoreState()

def pic(name,x,y,w,h):
    im=Image.open(ART/name)
    if im.mode=='RGBA':
        bounds=im.getchannel('A').getbbox()
        if bounds: im=im.crop(bounds)
    scale=min(w/im.width,h/im.height)
    iw,ih=im.width*scale,im.height*scale
    c.drawImage(ImageReader(im),x+(w-iw)/2,H-y-(h+ih)/2,width=iw,height=ih,mask='auto')

def arrow(x1,y1,x2,y2,color=CORAL,width=2.4,head=8):
    line(x1,y1,x2,y2,color,width)
    a=math.atan2(y2-y1,x2-x1)
    pts=[(x2,y2),(x2-head*math.cos(a-.5),y2-head*math.sin(a-.5)),(x2-head*math.cos(a+.5),y2-head*math.sin(a+.5))]
    p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:p.lineTo(x,H-y)
    p.close();c.setFillColor(HexColor(color));c.drawPath(p,fill=1,stroke=0)

def step(n,title,x,y):
    c.setFillColor(HexColor(INK));c.circle(x+14,H-y-14,14,stroke=0,fill=1)
    text(str(n),x+9.4,y+6,19,'Bold','#ffffff')
    text(title,x+40,y+2,21,'Bold')

def artfield(x,y,w=416,h=130):
    rect(x,y,w,h,PALE,r=3)

def chip(s,x,y,w,bg,fg='#ffffff'):
    rect(x,y,w,18,bg,stroke=STONE if bg=='#ffffff' else None,r=2)
    text(s,x+6,y+4,10,'Bold',fg)

# Header and the things to have ready.
rect(0,0,W,H,'#ffffff')
label('HOME SODA MACHINE',36,36,color=INK,size=11)
text('Quick start',34,58,48,'Bold')
rect(36,117,43,3,CORAL)
text('From the box to your first glass.',93,111,18)
label('BEFORE YOU START',746,39,color=CORAL)
para('<b>A prepared 1-3/8 in counter hole.</b> A cold-water supply. A grounded 120 V outlet.',746,58,582,13,17)
para('<b>A filled 5 lb CO2 cylinder</b> with the supplied regulator fitted and leak-checked. Two 14.8 fl oz bottles of SodaStream-compatible concentrate.',746,97,582,13,17)
line(36,149,1332,149,INK,1)
label('MOUNT THE FAUCET',36,162)
label('CONNECT THE COLD WATER',916,162)

# Row 1.
x,y=36,184
step(1,'Lower and seat the faucet',x,y)
artfield(x,y+39)
pic('mount-drop.png',x+8,y+42,189,122)
pic('mount-lowered-clean.png',x+217,y+42,189,122)
arrow(x+202,y+102,x+215,y+102,head=6)
para('Feed the attached tubes and cable through the hole. Lower the faucet, then <b>push it back</b> until the two black tubes rest against the back of the hole.',x,y+181,416,13.5,17.5,limit=70)

x=476
step(2,'Slide the plate. Hand-tighten.',x,y)
artfield(x,y+39)
pic('mount-under-slide-clean.png',x+6,y+50,196,107)
pic('mount-under-tighten-clean.png',x+221,y+50,189,107)
arrow(x+205,y+104,x+217,y+104,head=6)
para('From below, slide the steel plate <b>above the washer and nut.</b> Wide slot around the shank; narrow slot around the black tubes. Run the nut up by hand.',x,y+181,416,13.5,17.5,limit=70)

x=916
step(3,'Shut off the cold water',x,y)
artfield(x,y+39)
pic('modern-water-on.png',x+8,y+66,190,89)
pic('modern-water-off.png',x+220,y+66,190,89)
label('OPEN',x+14,y+48,size=8)
label('CLOSED',x+233,y+48,size=8)
arrow(x+203,y+102,x+216,y+102,head=6)
para('Follow the line to its shut-off valve and close it. Run the cold tap until flow stops to release pressure. <b>Put a towel and cup under the joint.</b>',x,y+181,416,13.5,17.5,limit=70)

line(36,440,1332,440)
label('THIS WATER PATH: A 1/4 IN PLASTIC LINE IN A PUSH FITTING',36,451,color=CORAL,size=9)
text('Braided hose instead? Use the white tee: install guide, pages 9-11.',707,449,12,'Semibold')

# Row 2.
x,y=36,478
step(4,'Press the collar. Pull the tube.',x,y)
artfield(x,y+39,h=118)
pic('modern-release-ready.png',x+8,y+67,188,72)
pic('modern-release-withdrawn.png',x+219,y+67,188,72)
arrow(x+202,y+101,x+216,y+101,head=6)
para('Hold the fitting\'s release collar in with the <b>collet press</b> from your kit. Keep it pressed while you pull the existing tube straight out.',x,y+168,416,13.5,17.5,limit=70)

x=476
step(5,'Push the supplied tee into place',x,y)
artfield(x,y+39,h=118)
pic('modern-tee-assembly-ready.png',x+8,y+53,126,94)
pic('modern-tee-line-ready.png',x+146,y+53,126,94)
pic('modern-tee-complete.png',x+282,y+53,126,94)
arrow(x+132,y+92,x+144,y+92,head=5)
arrow(x+271,y+92,x+282,y+92,head=5)
para('Push the tee\'s short tube into the fitting you opened. Push the original tube into the tee\'s open end. <b>The long white run and its filter arrive attached.</b>',x,y+168,416,13.5,17.5,limit=70)

x=916
step(6,'Match each tube to its word',x,y)
artfield(x,y+39,w=183,h=151)
pic('the-back-face.png',x+4,y+44,175,141)
rows=[('TAP','White, from the filter.','#ffffff',INK),('CO2','Red, from the cylinder.','#d7333c','#ffffff'),('SODA','Blue, from the faucet.','#1670db','#ffffff'),('FLAVOR','Both black faucet tubes.',INK,'#ffffff')]
for i,(s,t,bg,fg) in enumerate(rows):
 yy=y+40+i*30
 chip(s,x+198,yy,56,bg,fg);text(t,x+263,yy+3,10.5)
para('Either black tube fits either FLAVOR port. Click the faucet cable into the small square jack.',x+198,y+163,216,11.5,14.5,limit=44)
para('<b>Remove the shipping caps.</b> Push every tube fully home, then give it a gentle tug.',x,y+214,416,12.5,16,limit=32)

# First glass, below the installation sequence.
rect(0,752,W,148,INK)
label('THEN MAKE YOUR FIRST GLASS',36,767,color='#ffffff',size=10)
starts=[36,370,704,1038]
titles=['1  Connect the cylinder','2  Open, check, power','3  Fill each flavor','4  Let it chill. Then pour.']
bodies=[
    'Keep the cylinder upright and closed. Hand-tighten the red tube\'s brass nut onto the regulator outlet. See install guide, p. 13.',
    'Open water slowly; watch joints for a full minute. Open CO2 and check the gas connections. Then connect the cord and plug into grounded 120 V.',
    'On the enclosure display, choose <b>FILL</b>, pick a flavor and press <b>Start</b>. Invert one whole 14.8 fl oz bottle over the funnel. Let it drain. Repeat for the second flavor.',
    'Allow about an hour for the first chill. Choose a flavor on the faucet display, put a glass underneath and press the faucet lever.'
]
for xx,title,body in zip(starts,titles,bodies):
    text(title,xx,792,15,'Bold','#ffffff')
    para(body,xx,817,293,12.5,16,color='#ffffff',limit=80)

text('Leave the tubes long and coil the slack. Keep both side vents clear.',36,913,11,'Semibold')
text('19 × 13 in  ·  Print at 100%  ·  homesodamachine.com',1000,913,10,color=MUTED)

c.showPage();c.save()
output=ROOT/'output/pdf/quick-start-codex.pdf'
output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PDF,output)
preview=Path('/tmp/guide-codex-references/quick-start-codex')
preview.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1900','-singlefile','-png',str(PDF),str(preview)],check=True)
im=Image.open(preview.with_suffix('.png'));im.thumbnail((1200,1200));im.save(DIR/'quick-start-codex.cover.png')
(DIR/'quick-start-codex.pdf.json').write_text(json.dumps({'title':'Quick start · Codex','subtitle':'Illustrated installation with words - one 19 x 13 in sheet','pages':1,'cover':'quick-start-codex.cover.png','cover_size':list(im.size)},indent=2)+'\n')
print(PDF)
