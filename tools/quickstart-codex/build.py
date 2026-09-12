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

def pic(name,x,y,w,h,crop=None):
    im=Image.open(ART/name)
    bounds=crop or (im.getchannel('A').getbbox() if im.mode=='RGBA' else None) or (0,0,im.width,im.height)
    im=im.crop(bounds)
    scale=min(w/im.width,h/im.height)
    iw,ih=im.width*scale,im.height*scale
    ox,oy=x+(w-iw)/2,y+(h-ih)/2
    c.drawImage(ImageReader(im),ox,H-oy-ih,width=iw,height=ih,mask='auto')
    return lambda px,py: (ox+(px-bounds[0])*scale,oy+(py-bounds[1])*scale)

def arrow(x1,y1,x2,y2,color=CORAL,width=2.4,head=8):
    line(x1,y1,x2,y2,PALE,width+3)
    line(x1,y1,x2,y2,color,width)
    a=math.atan2(y2-y1,x2-x1)
    pts=[(x2,y2),(x2-head*math.cos(a-.5),y2-head*math.sin(a-.5)),(x2-head*math.cos(a+.5),y2-head*math.sin(a+.5))]
    p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:p.lineTo(x,H-y)
    p.close();c.setFillColor(HexColor(color));c.drawPath(p,fill=1,stroke=0)

def turn(points,head=7):
    a,b,d,e=points
    p=c.beginPath();p.moveTo(a[0],H-a[1]);p.curveTo(b[0],H-b[1],d[0],H-d[1],e[0],H-e[1])
    c.setStrokeColor(HexColor(PALE));c.setLineWidth(5.4);c.drawPath(p)
    c.setStrokeColor(HexColor(CORAL));c.setLineWidth(2.4);c.drawPath(p)
    vx,vy=e[0]-d[0],e[1]-d[1];length=math.hypot(vx,vy)
    arrow(e[0]-2*vx/length,e[1]-2*vy/length,*e,head=head)

def step(n,title,x,y):
    c.setFillColor(HexColor(INK));c.circle(x+14,H-y-14,14,stroke=0,fill=1)
    text(str(n),x+9.4,y+6,19,'Bold','#ffffff')
    text(title,x+40,y+2,21,'Bold')

def artfield(x,y,w=416,h=130):
    rect(x,y,w,h,PALE,r=3)

def chip(s,x,y,w,bg,fg='#ffffff'):
    rect(x,y,w,18,bg,stroke=STONE if bg=='#ffffff' else None,r=2)
    text(s,x+6,y+4,10,'Bold',fg)

# Prepare the kitchen.
rect(0,0,W,H,'#ffffff')
label('HOME SODA MACHINE',36,30,color=INK,size=10)
text('Quick start',34,49,43,'Bold')
rect(302,59,3,24,CORAL)
text('From the box to your first glass.',322,62,19)
label('HAVE READY',800,29,color=CORAL,size=9)
para('A <b>1-3/8 in counter hole</b>, cold water and a grounded <b>120 V</b> outlet. A filled <b>5 lb CO2 cylinder</b> with the supplied regulator fitted and leak-checked. Two <b>14.8 fl oz</b> bottles of SodaStream-compatible concentrate.',800,47,532,12.5,16,limit=64)
line(36,111,1332,111,INK,1)
label('INSTALL',36,122,color=CORAL,size=9)
text('Keep the cylinder closed and the power unplugged while making the connections.',773,121,11,'Semibold',MUTED)

# The faucet and its retained hardware.
x,y=36,145
step(1,'Mount the faucet',x,y)
artfield(x,y+37,h=120)
p=pic('mount-drop.png',x+4,y+40,133,114,crop=(9,33,763,1331))
arrow(*p(190,660),*p(190,963),head=7)
label('LOWER',x+5,y+50,size=7)
p=pic('mount-under-slide-clean.png',x+144,y+49,127,83)
arrow(*p(318,470),*p(600,435),head=7)
q=pic('mount-under-tighten-clean.png',x+281,y+49,127,83)
turn([q(640,386),q(570,218),q(970,204),q(959,361)],head=6)
label('SLIDE PLATE',x+149,y+138,size=7)
label('HAND-TIGHTEN',x+290,y+138,size=7)
para('Feed the attached tubes and cable through the hole. Lower the faucet, then <b>push it back</b> until the black tubes rest against the back of the hole.',x,y+170,416,12.8,16.5,limit=66)
para('From below, slide the steel plate <b>above the retained washer and nut.</b> Wide slot around the shank; narrow slot around the black tubes. Tighten the nut by hand.',x,y+226,416,12.8,16.5,limit=66)

# Each water action keeps its own close-up and words.
x=476
step(2,'Add the cold-water tee',x,y)
artfield(x,y+38,w=138,h=69)
p=pic('modern-water-on.png',x+3,y+43,132,58,crop=(170,190,1100,635))
turn([p(475,300),p(450,160),p(860,175),p(837,336)],head=6)
para('<b>Close the cold supply.</b> Run the cold tap until flow stops to release pressure. Put a cup and towel under the fitting.',x+153,y+39,263,12.2,15.5,limit=78)
artfield(x,y+117,w=138,h=69)
p=pic('modern-release-ready.png',x+3,y+126,132,52)
arrow(*p(1400,378),*p(1070,336),head=6)
arrow(*p(1275,730),*p(1700,785),head=6)
para('<b>Release the existing tube.</b> Hold the fitting\'s release ring in with the collet press. Keep it pressed while pulling the tube out.',x+153,y+118,263,12.2,15.5,limit=78)
artfield(x,y+197,w=138,h=87)
p=pic('modern-tee-line-ready.png',x+3,y+202,132,76,crop=(0,161,2000,1032))
arrow(*p(1910,490),*p(1570,479),head=6)
para('<b>Insert the supplied tee.</b> Push its short tube into the fitting you opened. Reconnect the original tube to the tee\'s open end. The white filtered run arrives attached.',x+153,y+198,263,12.2,15.5,limit=93)

# The rear face and the names the owner matches.
x=916
step(3,'Match the connections',x,y)
artfield(x,y+38,w=180,h=157)
pic('connect-rear-open.png',x+3,y+42,174,148)
rows=[('TAP','White, from the filter.','#ffffff',INK),('CO2','Red, from the cylinder.','#d7333c','#ffffff'),('SODA','Blue, from the faucet.','#1670db','#ffffff'),('FLAVOR','Two black faucet tubes.',INK,'#ffffff')]
for i,(s,t,bg,fg) in enumerate(rows):
    yy=y+41+i*29
    chip(s,x+193,yy,56,bg,fg);text(t,x+259,yy+3,11)
para('<b>Faucet cable:</b> click its plug into the small square jack.',x+193,y+166,223,11.5,14.5,limit=43.5)
para('<b>Remove the shipping caps.</b> Push every tube fully home, then tug gently. Either black tube fits either FLAVOR port.',x,y+209,416,12.8,16.5,limit=66)
para('Lay the filter flat. Leave the tubes long, with easy curves and the slack coiled.',x,y+265,416,12.5,16,limit=32)

# The kitchen fork stays next to the water connection.
line(36,449,1332,449)
text('Braided cold-water hose instead? Use the white tee: install guide, pages 9-11.',36,459,11.5,'Semibold')
text('Leave 1-5/8 in at both sides and 2-3/8 in behind the appliance.',968,459,10.5,'Semibold',MUTED)
c.linkURL('https://homesodamachine.com/docs/install-guide/install-guide.pdf#page=9',(36,H-475,700,H-457),relative=0)

# The first-glass sequence has four full illustrated steps.
rect(0,488,W,418,INK)
label('THEN MAKE YOUR FIRST GLASS',36,504,color='#ffffff',size=11)
text('Water, gas and power first. Then fill, chill and pour.',914,504,12,'Semibold','#ffffff')
starts=[36,366,696,1026]
for n,title,xx in zip([4,5,6,7],['Connect the cylinder','Water, gas, then power','Fill both flavors','Chill. Choose. Pour.'],starts):
    c.setFillColor(HexColor(CORAL));c.circle(xx+12,H-542,12,stroke=0,fill=1)
    text(str(n),xx+7.7,534,17,'Bold','#ffffff')
    text(title,xx+35,533,19.5,'Bold','#ffffff')
    artfield(xx,567,w=306,h=161)

# Art arrives as committed snapshots. The existing views make the first layout visible
# while the new CAD scenes are being drawn in the same manual authoring session.
def available(preferred,fallback):
    return preferred if (ART/preferred).exists() else fallback

x=36
pic(available('co2-ready.png','regulator.png'),x+6,571,294,151)
text('Keep the cylinder upright, with its valve closed.',x,742,12.6,'Bold','#ffffff')
para('Hand-tighten the red tube\'s brass nut onto the regulator\'s bottom outlet. Keep the fitted regulator on the cylinder. If it has not been fitted and leak-checked, the refill shop can do that.',x,767,306,12.8,16.5,color='#ffffff',limit=115.5)

x=366
pic(available('power-ready.png','the-socket.png'),x+6,571,294,151)
para('<b>Water:</b> open the shut-off slowly. Watch every water joint for a full minute.<br/><b>Gas:</b> open the cylinder and regulator outlet. Check the red line\'s connections; set the upper gauge in its green band.<br/><b>Power:</b> seat the cord in the top-left rear socket, then plug into grounded 120 V.',x,742,306,12.5,16.4,color='#ffffff',limit=147.6)

x=696
pic(available('fill-seated.png','bottle-in-funnel.png'),x+6,571,294,151)
para('On the enclosure display, choose <b>FILL</b>, pick a flavor and press <b>Start.</b>',x,742,306,13,17,color='#ffffff',limit=51)
para('Invert one whole <b>14.8 fl oz bottle</b> over the funnel. Let it drain; the appliance stops the fill itself. Repeat for the second flavor.',x,800,306,13,17,color='#ffffff',limit=85)

x=1026
pic(available('pour-running.png','faucet-side-pressed.png'),x+6,571,294,151)
text('Allow about an hour for the first chill.',x,742,13.2,'Bold','#ffffff')
para('<b>Choose:</b> tap the faucet display to select a flavor. A dim screen takes one tap to wake.',x,771,306,13,17,color='#ffffff',limit=68)
para('<b>Pour:</b> place a glass underneath and press the faucet lever. Release it to stop.',x,830,306,13,17,color='#ffffff',limit=51)

text('Home Soda Machine  /  Quick start',36,916,9.5,color=MUTED)
text('19 × 13 in  ·  Print at 100%  ·  homesodamachine.com',1000,916,9.5,color=MUTED)
c.showPage();c.save()
output=ROOT/'output/pdf/quick-start-codex.pdf'
output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PDF,output)
preview=Path('/tmp/guide-codex-references/quick-start-codex')
preview.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1900','-singlefile','-png',str(PDF),str(preview)],check=True)
im=Image.open(preview.with_suffix('.png'));im.thumbnail((1200,1200));im.save(DIR/'quick-start-codex.cover.png')
(DIR/'quick-start-codex.pdf.json').write_text(json.dumps({'title':'Quick start · Codex','subtitle':'Installation, cylinder, power, fill and first pour - one 19 x 13 in sheet','pages':1,'cover':'quick-start-codex.cover.png','cover_size':list(im.size)},indent=2)+'\n')
print(PDF)
