#!/usr/bin/env python3
"""Draw the one-sheet 19 x 13 inch Home Soda Machine quick start."""
from pathlib import Path
import argparse
import io
import json
import math
import shutil
import subprocess
import sys
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from contours import Contours, PAD

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/quickstart-codex'
ART = DIR / 'art'
parser = argparse.ArgumentParser()
parser.add_argument('--contour', default='#46515b')
parser.add_argument('--output', type=Path, default=DIR / 'quick-start-codex.pdf')
args = parser.parse_args()
PDF = args.output.resolve()
contours = Contours(args.contour)
W, H = 19 * 72, 13 * 72
BLUE, NAVY, ICE, ORANGE = '#1749D1', '#10319C', '#DCE6FF', '#FF9152'
INK = '#202337'
CORAL = '#d64050'
RULE = '#DCE2EB'
MUTED = '#606A78'
for name in ['Regular', 'Semibold', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR / 'fonts' / f'Plex-{name}.ttf')))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold', italic='Regular', boldItalic='Bold')
pdf_buffer = io.BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=(W,H), pageCompression=1, invariant=1)
c.setTitle('Home Soda Machine - Quick start')
c.setAuthor('Derek Bredensteiner')
c.setSubject('One 19 x 13 inch installation quick start with words')
checks = []

def rect(x,y,w,h,fill,stroke=None,r=0):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke or fill))
    if r: c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else: c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))

def line(x1,y1,x2,y2,color=RULE,width=.7):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width)
    c.line(x1,H-y1,x2,H-y2)

def text(s,x,y,size=13,font='Regular',color=INK):
    width = pdfmetrics.stringWidth(s,font,size)
    if x < 0 or x+width > W or y < 0 or y+size > H-30:
        raise ValueError(f'Text outside print area: {s}')
    c.setFillColor(HexColor(color)); c.setFont(font,size)
    c.drawString(x,H-y-size*.80,s)
    checks.append({'text':s,'box':[x,y,width,size]})

def para(s,x,y,w,size=13,leading=17,color=INK,font='Regular',limit=None):
    p=Paragraph(s,ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,height=p.wrap(w,1000)
    if limit is not None and height>limit+.1: raise ValueError(f'Text overflow: {s[:65]} {height}>{limit}')
    if x < 0 or x+w > W or y < 0 or y+height > H-30:
        raise ValueError(f'Paragraph outside print area: {s[:65]}')
    p.drawOn(c,x,H-y-height)
    checks.append({'text':s,'box':[x,y,w,height]})
    return height

def label(s,x,y,color=BLUE,size=9):
    c.saveState()
    c.setFillColor(HexColor(color));t=c.beginText(x,H-y-size*.8)
    t.setFont('Bold',size);t.setCharSpace(1.5);t.textOut(s.upper());c.drawText(t)
    c.restoreState()

def pic(name,x,y,w,h,crop=None,outline=True,fade_crops=True):
    source = ART/name
    im=Image.open(source)
    bounds=crop or (im.getchannel('A').getbbox() if im.mode=='RGBA' else None) or (0,0,im.width,im.height)
    bw,bh=bounds[2]-bounds[0],bounds[3]-bounds[1]
    scale=min(w/bw,h/bh)
    iw,ih=bw*scale,bh*scale
    ox,oy=x+(w-iw)/2,y+(h-ih)/2
    if outline:
        contoured, (pw,ph) = contours.picture(source,bounds,iw,ih,fade_crops=fade_crops)
        if contoured.exists():
            c.drawImage(str(contoured),ox-PAD,H-oy-ih-PAD,width=pw,height=ph,mask='auto')
    else:
        c.drawImage(ImageReader(im.crop(bounds)),ox,H-oy-ih,width=iw,height=ih,mask='auto')
    return lambda px,py: (ox+(px-bounds[0])*scale,oy+(py-bounds[1])*scale)

def projected(mapper,point,cam,target,span,size=(1600,1500)):
    """Put an action arrow on the same world point the CAD camera drew."""
    def unit(v):
        length=math.sqrt(sum(t*t for t in v));return tuple(t/length for t in v)
    def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    direction=unit(cam);right=unit(cross((0,0,1),direction));up=cross(direction,right)
    delta=tuple(p-t for p,t in zip(point,target));scale=size[1]/(2*span)
    return mapper(size[0]/2+sum(a*b for a,b in zip(delta,right))*scale,
                  size[1]/2-sum(a*b for a,b in zip(delta,up))*scale)

def arrowhead(tip,tangent,head):
    length=math.hypot(*tangent)
    ux,uy=(v/length for v in tangent)
    back=head*math.cos(.5);half=head*math.sin(.5)
    neck=(tip[0]-back*ux,tip[1]-back*uy)
    p=c.beginPath();p.moveTo(tip[0],H-tip[1])
    p.lineTo(neck[0]-half*uy,H-neck[1]-half*ux)
    p.lineTo(neck[0]+half*uy,H-neck[1]+half*ux)
    p.close()
    return neck,p

def draw_arrow(shaft,head,color=CORAL,width=2.4,outline=1.1):
    """Outline the complete silhouette in page points, after scene projection."""
    c.saveState();c.setLineCap(1);c.setLineJoin(1)
    # Both white shapes precede both coral shapes, so their shared seam stays filled.
    c.setStrokeColor(white);c.setFillColor(white)
    c.setLineWidth(width+2*outline);c.drawPath(shaft,fill=0,stroke=1)
    c.setLineWidth(2*outline);c.drawPath(head,fill=1,stroke=1)
    c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color))
    c.setLineWidth(width);c.drawPath(shaft,fill=0,stroke=1)
    c.drawPath(head,fill=1,stroke=0)
    c.restoreState()

def arrow(x1,y1,x2,y2,color=CORAL,width=2.4,head=8):
    neck,tip=arrowhead((x2,y2),(x2-x1,y2-y1),head)
    shaft=c.beginPath();shaft.moveTo(x1,H-y1);shaft.lineTo(neck[0],H-neck[1])
    draw_arrow(shaft,tip,color,width)

def turn(points,head=7):
    a,b,d,e=points
    neck,tip=arrowhead(e,(e[0]-d[0],e[1]-d[1]),head)
    def lerp(p,q,t):return tuple(x+(y-x)*t for x,y in zip(p,q))
    def split(t):
        ab=lerp(a,b,t);bd=lerp(b,d,t);de=lerp(d,e,t)
        left=lerp(ab,bd,t);right=lerp(bd,de,t)
        return ab,left,lerp(left,right,t)
    # End the curved shaft at the head's base, leaving the point to the triangle.
    back=head*math.cos(.5);lo,hi=0.0,1.0
    for _ in range(32):
        mid=(lo+hi)/2;end=split(mid)[2]
        if math.dist(end,e)>back:lo=mid
        else:hi=mid
    ab,left,end=split((lo+hi)/2)
    shaft=c.beginPath();shaft.moveTo(a[0],H-a[1])
    shaft.curveTo(ab[0],H-ab[1],left[0],H-left[1],end[0],H-end[1])
    shaft.lineTo(neck[0],H-neck[1])
    draw_arrow(shaft,tip)

def step(n,title,x,y):
    c.setFillColor(HexColor(BLUE));c.circle(x+12,H-y-12,12,stroke=0,fill=1)
    text(str(n),x+7.7,y+5,17,'Bold','#ffffff')
    text(title,x+35,y+1,20,'Bold',NAVY)

def chip(s,x,y,w,bg,fg='#ffffff'):
    rect(x,y,w,18,bg,stroke=RULE if bg=='#ffffff' else None,r=2)
    text(s,x+6,y+4,10,'Bold',fg)

def phase(s,y):
    rect(36,y,4,10,ORANGE)
    label(s,49,y+1,color=BLUE,size=9)
    line(209,y+5,1332,y+5,RULE,.8)

def leader(s,x,y,point,side='right'):
    text(s,x,y,10,'Semibold')
    width=pdfmetrics.stringWidth(s,'Semibold',10)
    start=(x+width+5,y+5) if side=='right' else (x-5,y+5)
    line(*start,*point,INK,.7)
    c.setFillColor(HexColor(INK));c.circle(point[0],H-point[1],1.6,fill=1,stroke=0)

def tap_cue(s,x,y,point):
    text(s,x,y,9.5,'Semibold')
    width=pdfmetrics.stringWidth(s,'Semibold',9.5)
    line(x+width+4,y+4,point[0]-4,point[1],INK,.65)
    c.setFillColor(HexColor(CORAL));c.setStrokeColor(white);c.setLineWidth(1)
    c.circle(point[0],H-point[1],2.5,fill=1,stroke=1)
    for dx,dy in [(-4,-4),(0,-5),(4,-4)]:
        line(point[0]+dx,point[1]+dy,point[0]+dx*1.5,point[1]+dy*1.5,CORAL,.85)

# The kitchen is prepared before any connection is opened.
rect(0,0,W,H,'#ffffff')
rect(0,0,W,102,BLUE)
c.drawImage(str(ART/'brand/mark-1024.png'),24,H-96,width=92,height=92,mask='auto')
label('HOME SODA MACHINE',127,25,color='#FFFFFF',size=9)
text('Quick start',125,45,42,'Bold','#FFFFFF')
para('From the box<br/>to your first glass.',422,32,310,19,24,'#FFFFFF',limit=48)
rect(422,88,43,4,ORANGE)
label('HAVE READY',797,24,color=ICE,size=9)
para('A <b>1-3/8 in counter hole</b>, cold water and grounded <b>120 V.</b> A filled <b>5 lb CO2 cylinder</b> and an adjustable wrench for the regulator\'s nut. Two <b>14.8 fl oz</b> bottles of SodaStream-compatible concentrate.',797,42,535,12,15,'#FFFFFF',limit=45)
rect(0,102,W,39,ICE)
label('MAKE ROOM',36,117,color=NAVY,size=8)
text('1-5/8 in clear at each side, 2-3/8 in behind, and room above to invert a bottle into the funnel.',161,115,12,'Semibold',NAVY)
phase('INSTALL',158)
text('Cylinder closed. Power unplugged.',1066,148,11.5,'Semibold',MUTED)

# Faucet: lower and seat the base, insert the plate, then turn only the nut.
x,y=36,181
step(1,'Mount the faucet',x,y)
p=pic('mount-drop.png',x+1,215,100,110,crop=(9,33,763,1331))
arrow(*p(190,660),*p(190,963),head=6)
text('1 Lower',x+2,248,9.5,'Semibold')
arrow(*p(382,866),*p(585,928),head=6)
text('2 Back',x+75,282,9.5,'Semibold')
p=pic('mount-under-slide-clean.png',x+118,218,194,88,crop=(205,275,960,575))
arrow(*p(295,405),*p(720,345),head=7)
plate_gap=p(869,344)
for row,caption in enumerate(['Plate above','washer + nut']):
    caption_width=pdfmetrics.stringWidth(caption,'Semibold',10)
    text(caption,x+272-caption_width,316+row*12,10,'Semibold')
for color,width in [('#ffffff',2.2),(INK,.7)]:
    line(x+278,325,x+291,325,color,width)
    line(x+291,325,*plate_gap,color,width)
c.setFillColor(HexColor(INK));c.setStrokeColor(white);c.setLineWidth(.65)
c.circle(plate_gap[0],H-plate_gap[1],1.8,fill=1,stroke=1)
p=pic('mount-under-tighten-clean.png',x+324,227,90,83,crop=(670,260,900,503))
turn([p(739,375),p(718,348),p(843,340),p(829,374)],head=5)
text('Turn nut',x+339,211,9.5,'Semibold')
para('Feed the attached tubes and cable through the hole. Lower the faucet, then <b>push it back</b> until the black tubes meet the back of the hole.',x,350,416,12.5,16,limit=48)
para('From below, slide the steel plate <b>above the retained washer and nut.</b> Wide slot around the shank; narrow slot around the black tubes and cable. <b>Hand-tighten the nut.</b>',x,403,416,12.5,16,limit=48)

# The kitchen choice precedes opening any joint.
x=476
step(2,'Add the cold-water tee',x,y)
rect(x,214,416,49,ICE,r=5)
para('<b>1/4 in plastic tube?</b> Use the black tee below.<br/><b>Braided hose?</b> See install guide pp. 9-11,<br/>then return at <b>Step 3.</b>',x+10,220,396,11.5,13.5,NAVY,limit=40.5)
c.linkURL('https://homesodamachine.com/docs/install-guide/install-guide.pdf#page=9',(x,H-263,x+416,H-214),relative=0)
p=pic('modern-water-off.png',x+3,279,116,51,crop=(170,190,1100,635))
text('Closed',x+49,330,8.5,'Semibold',MUTED)
para('<b>Close the cold-water shutoff.</b> Run the tap or dispenser on that line until flow stops. Put a cup and towel under the fitting.',x+136,275,280,12.1,15,limit=60)
p=pic('release-with-press.png',x+3,341,116,53,crop=(0,0,1840,1040))
arrow(*p(1316.97,779.94),*p(1042.29,700.52),head=5)
arrow(*p(1510,554),*p(1780,632),head=5)
para('<b>Push the collet press against the release ring and hold.</b> With your other hand, <b>pull the white tube out.</b>',x+136,339,280,12.1,15,limit=60)
p=pic('modern-tee-assembly-ready.png',x+3,405,116,45,crop=(200,130,1860,670))
arrow(*p(1110,170),*p(810,170),head=5)
para('<b>Push the tee\'s short tube into that fitting.</b> Reconnect the original tube to the open end. Leave the filtered run attached.',x+136,403,280,12.1,15,limit=45)

# A front view gives the ports and the small jack their own readable shapes.
x=916
step(3,'Match the rear connections',x,y)
para('<b>Pull the CO2 and TAP shipping caps off the soda machine.</b>',x,215,416,12.1,16,limit=16)
text('Caps fit over the outside of the fittings. Leave the fittings in place.',x,233,10,'Regular',MUTED)
p=pic('the-back-face.png',x+4,249,216,145,crop=(565,40,1565,855))
rows=[('CO2','Red / cylinder','#d7333c','#ffffff'),('SODA','Blue / faucet','#1670db','#ffffff'),('TAP','White / filter','#ffffff',INK),('FLAVOR','Black / either port','#1a1a2e','#ffffff')]
for i,(s,t,bg,fg) in enumerate(rows):
    yy=250+i*27
    chip(s,x+236,yy,59,bg,fg);text(t,x+302,yy+4,10.5)
text('Faucet cable',x+236,358,11.5,'Bold',NAVY)
para('Click into the square jack.',x+236,376,180,11.5,14,limit=28)
jack=p(1075,465)
route=[jack,(x+229,jack[1]),(x+229,369),(x+234,369)]
for color,width in [('#ffffff',2.6),(INK,.8)]:
    for start,end in zip(route,route[1:]):line(*start,*end,color,width)
c.setFillColor(HexColor('#ffffff'));c.circle(jack[0],H-jack[1],2.8,fill=1,stroke=0)
c.setFillColor(HexColor(CORAL));c.circle(jack[0],H-jack[1],1.7,fill=1,stroke=0)
para('<b>Push every tube fully home</b> (a little over 1/2 in), then tug gently. Either black tube fits either FLAVOR port.',x,409,416,12.4,16,limit=32)
text('Lay the filter flat. Keep long tubes in easy, coiled curves.',x,448,11.5,'Semibold')

# Startup receives three pictures, in the same order as the actions.
phase('TURN IT ON',480)
x,y=36,502
step(4,'Prepare the cylinder',x,y)
pic('cylinder-actions/co2-connected.png',x+2,540,167,90,crop=(80,0,1600,1500))
p=pic('cylinder-actions/co2-connected.png',x+177,540,117,90,crop=(420,775,830,1335))
para('<b>Valve closed.<br/>Cylinder upright.</b>',x+302,547,108,11.4,15,limit=30)
leader('Gray connector',x+302,599,p(637,943),side='left')
para('<b>Washer in the big nut; start by hand, nip up with the wrench.</b> Gray connector onto the bottom outlet hand-tight, both fittings left assembled.',x,642,416,12.6,16,limit=32)

x=476
step(5,'Water, then gas, then power',x,y)
starts=[476,770,1064]
for xx,title in zip(starts,['1  WATER','2  GAS','3  POWER']):
    label(title,xx,540,color=BLUE,size=10)
x=starts[0]
pic('modern-water-on.png',x+5,562,258,62,crop=(170,190,1100,635))
text('Open',x+113,627,8.5,'Semibold',MUTED)
para('Open the water shutoff <b>slowly.</b> Watch every water joint for a <b>full minute.</b>',x,646,268,12.4,16,limit=48)
x=starts[1]
gas_pose=((.08,1,.12),(-34.7549267293,3.0634158833,-30.1918478747),129.375,(1800,1500))
p=pic('cylinder-actions/startup-gas.png',x+4,557,139,80,crop=(173,53,1752,1360))
pic('cylinder-actions/startup-gas.png',x+216,561,45,45,crop=(533,48,873,388))
text('Upper',x+218,612,9.5,'Semibold')
text('gauge',x+218,624,9.5,'Semibold')
leader('Cylinder valve',x+143,563,projected(p,(-115,0,33),*gas_pose),side='left')
leader('Big knob',x+143,600,projected(p,(0,45,0),*gas_pose),side='left')
leader('Small knob',x+143,625,projected(p,(0,27,-47),*gas_pose),side='left')
para('Open the <b>cylinder valve</b> and <b>small knob.</b> Use the <b>big knob</b> to set the upper needle in <b>green.</b> Listen at the nut, gray connector and red CO2 port <b>before power:</b> a hiss is a leak.',x,646,268,12.4,16,limit=64)
x=starts[2]
p=pic('insertion-actions/power-ready.png',x+5,558,258,78,crop=(0,160,1800,1140))
arrow(*p(490.44,603.57),*p(1061.06,477.95),head=7)
para('Seat the cord in the <b>top-left rear socket.</b> Plug into grounded 120 V. <b>It chimes.</b>',x,646,268,12.4,16,limit=48)
rect(36,688,416,26,'#FFF0E6',r=5)
text('Leak or hiss? Close water and cylinder. See guide, p. 23.',46,697,11.3,'Semibold','#8B381B')
c.linkURL('https://homesodamachine.com/docs/install-guide/install-guide.pdf#page=23',(36,H-714,452,H-688),relative=0)

# The display, bottle and faucet show the controls and the first glass.
phase('YOUR FIRST GLASS',734)
x,y=36,757
step(6,'Fill both flavors',x,y)
para('On the machine display, <b>tap a flavor on the left</b>, then open <b>Fill.</b>',x,793,270,12,15,limit=30)
para('Invert one whole <b>14.8 fl oz bottle</b> into the funnel. Tap <b>Start filling.</b>',x,831,270,12,15,limit=30)
para('<b>Wait for Filled.</b> Repeat for the other flavor.',x,870,270,12,15,limit=30)
pic('fill-screen-framed.png',309,773,240,130,fade_crops=False)
p=pic('insertion-actions/fill-ready.png',555,787,131,117,crop=(295,330,1555,1450))
arrow(*p(947.15,473.85),*p(947.15,943.67),head=6)

x=716
step(7,'Chill. Choose. Pour.',x,y)
rect(x,791,280,26,BLUE,r=5)
text('FIRST CHILL: ABOUT 1 HOUR',x+10,799,12,'Bold','#ffffff')
text('Fill your glass with ice.',x,823,13,'Bold',NAVY)
para('<b>Choose:</b> tap the faucet display for a flavor. Tap once to wake a dim screen.',x,841,280,12,15,limit=30)
para('<b>Pour:</b> put it under the faucet. Press the lever; release to stop.',x,876,280,12,15,limit=30)
q=pic('edge-study/pour-base.png',1010,755,317,149,crop=(150,40,1475,1500))
pour_pose=((1,-1.8,.67),(0,-78,119),140)
tap=projected(q,(0,-134.243,211.599),*pour_pose)
tap_cue('Tap screen',tap[0]-80,tap[1]-4,tap)
press=projected(q,(0,-38,39),*pour_pose)
arrow(press[0],press[1]-17,press[0],press[1]-1,head=5)
leader('Press down',press[0]+58,press[1]-14,(press[0]+6,press[1]-10),side='left')

c.showPage();c.save()
if contours.pending:
    contours.render()
    subprocess.run([sys.executable,*sys.argv],cwd=ROOT,check=True)
    sys.exit(0)
PDF.parent.mkdir(parents=True,exist_ok=True)
PDF.write_bytes(pdf_buffer.getvalue())
if PDF == DIR/'quick-start-codex.pdf':
    output=ROOT/'output/pdf/quick-start-codex.pdf'
    output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PDF,output)
preview=DIR/'out/contours'/f'guide-{args.contour[1:]}'
preview.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1900','-singlefile','-png',str(PDF),str(preview)],check=True)
im=Image.open(preview.with_suffix('.png'));im.thumbnail((1200,1200));im.save(PDF.with_suffix('.cover.png'))
if PDF == DIR/'quick-start-codex.pdf':
    (DIR/'quick-start-codex.pdf.json').write_text(json.dumps({'title':'Home Soda Machine quick start','subtitle':'Owner quick start - installation through your first glass - one 19 x 13 in sheet','pages':1,'cover':'quick-start-codex.cover.png','cover_size':list(im.size)},indent=2)+'\n')
(DIR/'out/layout-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(PDF)
