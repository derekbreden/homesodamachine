#!/usr/bin/env python3
"""Draw the one-sheet 19 x 13 inch Home Soda Machine quick start."""
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
PALE = '#e5e1da'
for name in ['Regular', 'Semibold', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR / 'fonts' / f'Plex-{name}.ttf')))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold', italic='Regular', boldItalic='Bold')
c = canvas.Canvas(str(PDF), pagesize=(W,H), pageCompression=1)
c.setTitle('Home Soda Machine - Quick start')
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
    c.setFillColor(HexColor(INK));c.circle(x+12,H-y-12,12,stroke=0,fill=1)
    text(str(n),x+7.7,y+5,17,'Bold','#ffffff')
    text(title,x+35,y+1,20,'Bold')

def artfield(x,y,w=416,h=130):
    rect(x,y,w,h,PALE,r=3)

def chip(s,x,y,w,bg,fg='#ffffff'):
    rect(x,y,w,18,bg,stroke=STONE if bg=='#ffffff' else None,r=2)
    text(s,x+6,y+4,10,'Bold',fg)

def phase(s,y):
    label(s,36,y,color=CORAL,size=9)
    line(172,y+4,1332,y+4,STONE,.8)

def leader(s,x,y,point,side='right'):
    text(s,x,y,10,'Semibold')
    width=pdfmetrics.stringWidth(s,'Semibold',10)
    start=(x+width+5,y+5) if side=='right' else (x-5,y+5)
    line(*start,*point,INK,.7)
    c.setFillColor(HexColor(INK));c.circle(point[0],H-point[1],1.6,fill=1,stroke=0)

# The kitchen is prepared before any connection is opened.
rect(0,0,W,H,'#ffffff')
label('HOME SODA MACHINE',36,20,color=INK,size=9)
text('Quick start',34,38,34,'Bold')
text('From the box to your first glass.',274,47,17)
label('HAVE READY',800,16,color=CORAL,size=9)
para('A <b>1-3/8 in counter hole</b>, cold water and grounded <b>120 V.</b> A filled <b>5 lb CO2 cylinder</b> with the supplied regulator fitted and leak-checked. Two <b>14.8 fl oz</b> bottles of SodaStream-compatible concentrate.',800,33,532,12,15,limit=60)
text('Place the appliance: 1-5/8 in clear at each side, 2-3/8 in behind, and room above to invert a bottle into the funnel.',36,96,12,'Semibold')
phase('INSTALL',121)
text('Cylinder closed. Power unplugged.',1066,110,11.5,'Semibold',MUTED)

# Faucet: one above-counter view, then a larger view of the retained stack.
x,y=36,143
step(1,'Mount the faucet',x,y)
artfield(x,177,w=416,h=131)
p=pic('mount-drop.png',x+1,183,100,118,crop=(9,33,763,1331))
arrow(*p(190,660),*p(190,963),head=6)
text('Lower',x+6,218,9.5,'Semibold')
p=pic('mount-under-slide-clean.png',x+111,180,293,112,crop=(325,178,1120,610))
arrow(*p(318,470),*p(600,435),head=7)
leader('Plate above washer + nut',x+170,293,p(730,440),side='left')
para('Feed the attached tubes and cable through the hole. Lower the faucet, then <b>push it back</b> until the black tubes meet the back of the hole.',x,319,416,12.5,16,limit=64)
para('From below, slide the steel plate <b>above the retained washer and nut.</b> Wide slot around the shank; narrow slot around the black tubes. <b>Hand-tighten the nut.</b>',x,376,416,12.5,16,limit=64)

# The kitchen choice precedes opening any joint.
x=476
step(2,'Add the cold-water tee',x,y)
para('<b>1/4 in plastic tube?</b> Use the black tee below.<br/><b>Braided hose?</b> Follow install guide pp. 9-11, then return at <b>Step 3.</b>',x,177,416,11.8,14.5,limit=43.5)
c.linkURL('https://homesodamachine.com/docs/install-guide/install-guide.pdf#page=9',(x,H-220,x+416,H-177),relative=0)
artfield(x,229,w=122,h=58)
p=pic('modern-water-off.png',x+3,232,116,51,crop=(170,190,1100,635))
para('<b>Close the cold supply.</b> Run the cold tap until it stops. Put a cup and towel under the fitting.',x+136,230,280,12.1,15,limit=60)
artfield(x,300,w=122,h=61)
p=pic('release-with-press.png',x+3,304,116,53,crop=(0,0,1840,1040))
arrow(*p(1316.97,779.94),*p(1042.29,700.52),head=5)
arrow(*p(1305.98,317.07),*p(1723.50,437.79),head=5)
para('<b>Hold the release ring in</b> with the collet press. Keep it pressed while pulling the existing tube out.',x+136,300,280,12.1,15,limit=60)
artfield(x,374,w=122,h=62)
p=pic('modern-tee-assembly-ready.png',x+3,377,116,54,crop=(200,130,1860,670))
arrow(*p(1110,170),*p(810,170),head=5)
para('<b>Push the tee\'s short tube into that fitting.</b> Reconnect the original tube to the tee\'s open end. The white filtered run is already attached.',x+136,373,280,12.1,15,limit=75)

# A front view gives the ports and the small jack their own readable shapes.
x=916
step(3,'Match the rear connections',x,y)
para('<b>Remove the CO2 and TAP caps.</b> Open ports shown below.',x,177,416,12.1,16,limit=32)
artfield(x,202,w=224,h=166)
p=pic('the-back-face.png',x+4,205,216,159,crop=(565,40,1565,855))
rows=[('CO2','Red / cylinder','#d7333c','#ffffff'),('SODA','Blue / faucet','#1670db','#ffffff'),('TAP','White / filter','#ffffff',INK),('FLAVOR','Black / either port',INK,'#ffffff')]
for i,(s,t,bg,fg) in enumerate(rows):
    yy=204+i*29
    chip(s,x+236,yy,59,bg,fg);text(t,x+302,yy+4,10.5)
text('Faucet cable',x+236,326,11.5,'Bold')
para('Click into the square jack.',x+236,344,180,11.5,14,limit=28)
jack=p(1075,465)
route=[jack,(x+229,jack[1]),(x+229,337),(x+234,337)]
for color,width in [('#ffffff',2.6),(INK,.8)]:
    for start,end in zip(route,route[1:]):line(*start,*end,color,width)
c.setFillColor(HexColor('#ffffff'));c.circle(jack[0],H-jack[1],2.8,fill=1,stroke=0)
c.setFillColor(HexColor(CORAL));c.circle(jack[0],H-jack[1],1.7,fill=1,stroke=0)
para('<b>Push every tube fully home</b> (a little over 1/2 in), then tug gently. Either black tube fits either FLAVOR port.',x,380,416,12.4,16,limit=48)
text('Lay the filter flat. Keep long tubes in easy, coiled curves.',x,432,11.5,'Semibold')

# Startup receives three pictures, in the same order as the actions.
c.saveState();c.translate(0,10)
phase('TURN IT ON',463)
x,y=36,484
step(4,'Connect the cylinder',x,y)
artfield(x,519,w=416,h=113)
pic('co2-ready.png',x+2,522,167,108,crop=(80,0,1600,1500))
p=pic('co2-ready.png',x+177,522,117,108,crop=(380,675,840,1260))
arrow(*p(460,1100),*p(460,869),head=6)
turn([p(587,1115),p(420,980),p(853,970),p(700,1106)],head=6)
para('<b>Valve closed.<br/>Cylinder upright.</b>',x+302,533,108,11.4,15,limit=60)
para('<b>Hand-tighten</b> the red tube\'s brass nut onto the regulator\'s bottom outlet. Keep the fitted regulator on the cylinder.',x,644,416,12.6,16,limit=64)

x=476
step(5,'Water, then gas, then power',x,y)
starts=[476,770,1064]
for xx,title in zip(starts,['1  WATER','2  GAS','3  POWER']):
    label(title,xx,522,color=INK,size=10)
    artfield(xx,542,w=268,h=90)
x=starts[0]
pic('modern-water-on.png',x+5,549,258,73,crop=(170,190,1100,635))
para('Open the cold supply <b>slowly.</b> Watch every water joint for a <b>full minute.</b>',x,644,268,12.4,16,limit=64)
x=starts[1]
gas_pose=((.08,1,.12),(-35,0,-4.5),103.5,(1800,1200))
p=pic('startup-gas.png',x+4,544,147,86,crop=(173,53,1752,1200))
pic('startup-gas.png',x+208,547,45,45,crop=(533,48,873,388))
text('Upper',x+157,554,10,'Semibold')
text('gauge',x+157,567,10,'Semibold')
leader('Big knob',x+157,598,projected(p,(0,45,0),*gas_pose),side='left')
leader('Small knob',x+157,617,projected(p,(0,27,-47),*gas_pose),side='left')
para('Open the cylinder and <b>small knob.</b> Use the <b>big knob</b> to set the upper needle in <b>green.</b> Check the brass nut and red CO2 port for leaks <b>before power.</b>',x,644,268,12.4,16,limit=64)
x=starts[2]
p=pic('power-ready.png',x+5,545,258,84,crop=(0,160,1800,1140))
power_pose=((-0.85,1,.25),(58.9,501,320.2105808375568),64,(1800,1300))
arrow(*projected(p,(66.9,525,336.21),*power_pose),*projected(p,(66.9,478,336.21),*power_pose),head=7)
para('Seat the cord in the <b>top-left rear socket.</b> Plug into grounded 120 V. <b>It chimes.</b>',x,644,268,12.4,16,limit=64)
text('Leak or continuing hiss? Close water and cylinder; get help.',36,690,11.3,'Semibold')
c.restoreState()

# One fill scene and one larger finished-glass scene carry the result.
c.saveState();c.translate(0,43)
phase('YOUR FIRST GLASS',748)
x,y=36,771
step(6,'Fill both flavors',x,y)
para('On the enclosure display, choose <b>FILL</b> and select a flavor.',x,813,292,12.6,16,limit=48)
para('Invert one whole <b>14.8 fl oz bottle</b> into the funnel. Then press <b>START FILL.</b>',x,855,292,12.6,16,limit=64)
para('<b>Wait for Filled.</b> Repeat for the second flavor.',x,918,292,12.6,16,limit=32)
artfield(348,804,w=290,h=160)
p=pic('fill-seated.png',355,810,277,148,crop=(290,290,1550,1500))
fill_pose=((.65,-1,.5),(0,140,465),265)
arrow(*projected(p,(60,156.5,469),*fill_pose),*projected(p,(60,156.5,364),*fill_pose),head=6)

x=696
step(7,'Chill. Choose. Pour.',x,y)
rect(x,810,296,24,INK,r=3)
text('FIRST CHILL: ABOUT 1 HOUR',x+9,817,12,'Bold','#ffffff')
para('<b>Choose:</b> tap the faucet display to select a flavor. A dim screen takes one tap to wake.',x,848,296,12.6,16,limit=64)
para('<b>Pour:</b> place a glass under the faucet and press the lever. Release it to stop.',x,901,296,12.6,16,limit=48)
artfield(1005,804,w=327,h=160)
q=pic('pour-running.png',1010,808,317,152,crop=(150,95,1475,1495))
pour_pose=((1,-1.8,.67),(0,-78,119),140)
tap=projected(q,(0,-131.55,217.61),*pour_pose)
arrow(tap[0]-28,tap[1]+6,tap[0]-1,tap[1]+1,head=6)
press=projected(q,(0,-38,39),*pour_pose)
arrow(press[0]+21,press[1]-25,press[0]+1,press[1]-1,head=6)
c.restoreState()

c.showPage();c.save()
output=ROOT/'output/pdf/quick-start-codex.pdf'
output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(PDF,output)
preview=Path('/tmp/guide-codex-references/quick-start-codex')
preview.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['pdftoppm','-scale-to','1900','-singlefile','-png',str(PDF),str(preview)],check=True)
im=Image.open(preview.with_suffix('.png'));im.thumbnail((1200,1200));im.save(DIR/'quick-start-codex.cover.png')
(DIR/'quick-start-codex.pdf.json').write_text(json.dumps({'title':'Home Soda Machine quick start','subtitle':'Owner quick start - installation through your first glass - one 19 x 13 in sheet','pages':1,'cover':'quick-start-codex.cover.png','cover_size':list(im.size)},indent=2)+'\n')
print(PDF)
