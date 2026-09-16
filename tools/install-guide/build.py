#!/usr/bin/env python3
"""Compose the 24-page owner install guide from committed print artwork."""
from pathlib import Path
import io
import json
import math
import subprocess
import sys
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader
from contours import Contours, PAD
from press import TRIM_W, TRIM_H, BLEED, write_editions, make_order_bundle

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/install-guide'
ART = DIR / 'assets'
OUT = DIR / 'out'
PDF = DIR / 'install-guide.pdf'
W, H = 396, 612
M, CW = 32, 332
SX, SY = TRIM_W/W, TRIM_H/H
BX, BY = BLEED/SX, BLEED/SY
PRESS_DIR = DIR / 'press'
BLUE, NAVY, ICE, ORANGE = '#1749D1', '#10319C', '#DCE6FF', '#FF9152'
INK, MUTED, RULE, CORAL = '#202337', '#606A78', '#DCE2EB', '#D64050'
for name in ['Regular','Semibold','Bold']:
    pdfmetrics.registerFont(TTFont(name,str(DIR/'fonts'/f'Plex-{name}.ttf')))
pdfmetrics.registerFontFamily('Regular',normal='Regular',bold='Bold',italic='Regular',boldItalic='Bold')
contours = Contours('#46515b')
buffer = io.BytesIO()
c = canvas.Canvas(buffer,pagesize=(TRIM_W+2*BLEED,TRIM_H+2*BLEED),pageCompression=1,invariant=1,initialFontName='Regular')
c.setTitle('Home Soda Machine - Install guide')
c.setAuthor('Derek Bredensteiner')
c.setSubject('Seven steps from installation through the first glass. 24 Comic Book pages.')
page_no = 0
checks=[]
image_checks=[]
resolution_file=ART/'print-resolution.json'
resolutions=json.loads(resolution_file.read_text())['assets'] if resolution_file.exists() else {}

def begin_page():
    c.translate(BLEED,BLEED)
    c.scale(SX,SY)

def ground(color):
    rect(-BX,-BY,W+2*BX,H+2*BY,color)

def image_reader(source,background='#FFFFFF'):
    image=Image.open(source).convert('RGBA') if isinstance(source,(str,Path)) else source.convert('RGBA')
    flat=Image.new('RGB',image.size,background)
    flat.paste(image,mask=image.getchannel('A'))
    return ImageReader(flat)

def rect(x,y,w,h,fill,stroke=None,r=0):
    c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill));c.setLineWidth(.6)
    if r:c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
    else:c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))

def line(x1,y1,x2,y2,color=RULE,width=.7):
    c.setStrokeColor(HexColor(color));c.setLineWidth(width);c.line(x1,H-y1,x2,H-y2)

def text(s,x,y,size=11,font='Regular',color=INK):
    c.setFillColor(HexColor(color));c.setFont(font,size);c.drawString(x,H-y-size*.8,s)
    width=pdfmetrics.stringWidth(s,font,size)
    if x<0 or x+width>W+.1:raise ValueError(f'Page {page_no} text outside page: {s}')

def para(s,x,y,w=CW,size=11,leading=15,color=INK,font='Regular',limit=None):
    p=Paragraph(s,ParagraphStyle('body',fontName=font,fontSize=size,leading=leading,textColor=HexColor(color)))
    _,h=p.wrap(w,1000)
    if limit is not None and h>limit+.1:raise ValueError(f'Page {page_no}: {s[:70]} {h}>{limit}')
    if y+h>560:raise ValueError(f'Page {page_no} footer collision: {s[:70]} bottom {y+h}')
    p.drawOn(c,x,H-y-h);checks.append({'page':page_no,'text':s,'box':[x,y,w,h]})
    return h

def label(s,x,y,color=BLUE,size=8):
    c.saveState();t=c.beginText(x,H-y-size*.8);t.setFont('Bold',size);t.setFillColor(HexColor(color));t.setCharSpace(1.15);t.textOut(s.upper());c.drawText(t);c.restoreState()

def badge(n,x,y,r=12):
    c.setFillColor(HexColor(BLUE));c.circle(x+r,H-y-r,r,stroke=0,fill=1)
    text(str(n),x+r-pdfmetrics.stringWidth(str(n),'Bold',r*1.2)/2,y+r*.46,r*1.2,'Bold','#FFFFFF')

def header(title,phase='BEFORE YOU START',step=None,sub=None):
    global page_no
    page_no+=1
    begin_page()
    ground('#FFFFFF')
    rect(-BX,-BY,W+2*BX,7+BY,BLUE)
    label(phase,M,30)
    if step is not None:
        badge(step,340,30,12)
    for i,t in enumerate(title.split('\n')):
        size=min(27,27*CW/pdfmetrics.stringWidth(t,'Bold',27))
        text(t,M,55+i*30,size,'Bold',NAVY)
    yy=55+len(title.split('\n'))*30+9
    if sub:para(sub,M,yy,CW,size=11,leading=15,limit=60)
    c.bookmarkPage(f'page-{page_no}')
    c.addOutlineEntry(f'{page_no}. {title.replace(chr(10)," ")}',f'page-{page_no}',0,False)

def end():
    line(M,566,W-M,566)
    text('HOME SODA MACHINE',M,574,7.4,'Bold',NAVY)
    text('Install guide',173,574,7.4,'Regular',MUTED)
    text(str(page_no),W-M-pdfmetrics.stringWidth(str(page_no),'Semibold',8),573,8,'Semibold',NAVY)
    c.showPage()

def pic(name,x,y,w,h,crop=None,outline=True,fade_crops=True):
    source=ART/name
    im=Image.open(source)
    resolution=resolutions.get(name,{})
    if resolution and list(im.size)!=resolution['render_size']:
        raise ValueError(f'{name}: dimensions disagree with print-resolution.json')
    rx,ry=resolution.get('scale',[1,1])
    if crop:crop=tuple(value*factor for value,factor in zip(crop,(rx,ry,rx,ry)))
    bounds=crop or (im.getchannel('A').getbbox() if im.mode=='RGBA' else None) or (0,0,im.width,im.height)
    a,b,cc,d=bounds;scale=min(w/(cc-a),h/(d-b));iw,ih=(cc-a)*scale,(d-b)*scale
    ppi=(72/(scale*SX),72/(scale*SY))
    if min(ppi)<300:
        raise ValueError(f'Page {page_no}, {name}: native artwork is only {min(ppi):.1f} PPI')
    image_checks.append({'page':page_no,'source':name,'native_pixels':list(im.size),'ppi':list(ppi)})
    ox,oy=x+(w-iw)/2,y+(h-ih)/2
    if outline:
        target,(pw,ph)=contours.picture(source,bounds,iw,ih,fade_crops=fade_crops)
        if target.exists():c.drawImage(image_reader(target),ox-PAD,H-oy-ih-PAD,width=pw,height=ph)
    else:
        image=im.crop(bounds)
        c.drawImage(image_reader(image),ox,H-oy-ih,width=iw,height=ih)
    return lambda px,py:(ox+(px*rx-a)*scale,oy+(py*ry-b)*scale)

def caption(s,y,x=M,w=CW):return para(s,x,y,w,9,12,MUTED,limit=36)

def note(title,s,y,kind='blue'):
    h=Paragraph(s,ParagraphStyle('measure',fontName='Regular',fontSize=10.5,leading=14)).wrap(CW-24,1000)[1]+42
    if y+h>560:raise ValueError(f'Page {page_no} note overflow {title} {y+h}')
    rect(M,y,CW,h,ICE if kind=='blue' else '#FFF0E6',r=6)
    label(title,M+12,y+12,color=NAVY if kind=='blue' else '#8B381B',size=7.5)
    para(s,M+12,y+29,CW-24,10.5,14,limit=h-34)
    return h

def item(n,title,s,y):
    text(n,M,y,13,'Bold',BLUE)
    text(title,M+24,y,12,'Bold',NAVY)
    return para(s,M+24,y+20,CW-24,11,15)+24

def arrowhead(tip,tangent,head):
    length=math.hypot(*tangent);ux,uy=(v/length for v in tangent)
    back=head*math.cos(.5);half=head*math.sin(.5);neck=(tip[0]-back*ux,tip[1]-back*uy)
    p=c.beginPath();p.moveTo(tip[0],H-tip[1]);p.lineTo(neck[0]-half*uy,H-neck[1]-half*ux);p.lineTo(neck[0]+half*uy,H-neck[1]+half*ux);p.close()
    return neck,p

def draw_arrow(shaft,head,width=2.5):
    c.saveState();c.setLineCap(1);c.setLineJoin(1)
    c.setStrokeColor(white);c.setFillColor(white);c.setLineWidth(width+2.2);c.drawPath(shaft,fill=0,stroke=1)
    c.setLineWidth(2.2);c.drawPath(head,fill=1,stroke=1)
    c.setStrokeColor(HexColor(CORAL));c.setFillColor(HexColor(CORAL));c.setLineWidth(width);c.drawPath(shaft,fill=0,stroke=1);c.drawPath(head,fill=1,stroke=0);c.restoreState()

def arrow(x1,y1,x2,y2,head=8):
    neck,tip=arrowhead((x2,y2),(x2-x1,y2-y1),head)
    shaft=c.beginPath();shaft.moveTo(x1,H-y1);shaft.lineTo(neck[0],H-neck[1]);draw_arrow(shaft,tip)

def turn(points,head=7):
    a,b,d,e=points;neck,tip=arrowhead(e,(e[0]-d[0],e[1]-d[1]),head)
    def lerp(p,q,t):return tuple(x+(y-x)*t for x,y in zip(p,q))
    def split(t):
        ab=lerp(a,b,t);bd=lerp(b,d,t);de=lerp(d,e,t);left=lerp(ab,bd,t);right=lerp(bd,de,t)
        return ab,left,lerp(left,right,t)
    back=head*math.cos(.5);lo,hi=0.,1.
    for _ in range(32):
        mid=(lo+hi)/2;point=split(mid)[2]
        if math.dist(point,e)>back:lo=mid
        else:hi=mid
    ab,left,point=split((lo+hi)/2)
    shaft=c.beginPath();shaft.moveTo(a[0],H-a[1]);shaft.curveTo(ab[0],H-ab[1],left[0],H-left[1],point[0],H-point[1]);shaft.lineTo(neck[0],H-neck[1]);draw_arrow(shaft,tip)

def leader(s,x,y,point,side='right'):
    text(s,x,y,9.5,'Semibold',INK)
    w=pdfmetrics.stringWidth(s,'Semibold',9.5)
    start=(x+w+5,y+4) if side=='right' else (x-5,y+4)
    for col,lw in [('#FFFFFF',2.6),(INK,.7)]:line(*start,*point,col,lw)
    c.setFillColor(HexColor(CORAL));c.setStrokeColor(white);c.setLineWidth(.7);c.circle(point[0],H-point[1],2.2,fill=1,stroke=1)

def projected(mapper,point,cam,target,span,size=(1600,1500)):
    def unit(v):
        length=math.sqrt(sum(t*t for t in v));return tuple(t/length for t in v)
    def cross(a,b):return(a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    direction=unit(cam);right=unit(cross((0,0,1),direction));up=cross(direction,right);delta=tuple(p-t for p,t in zip(point,target));scale=size[1]/(2*span)
    return mapper(size[0]/2+sum(a*b for a,b in zip(delta,right))*scale,size[1]/2-sum(a*b for a,b in zip(delta,up))*scale)

# 1
def front_cover():
    begin_page()
    ground(BLUE)
    c.drawImage(image_reader(ART/'brand/mark-1024.png',BLUE),M-17,H-175,width=160,height=160)
    label('HOME SODA MACHINE',M,191,'#FFFFFF',10)
    text('Install',M,236,54,'Bold','#FFFFFF');text('guide',M,293,54,'Bold','#FFFFFF')
    rect(M,365,56,5,ORANGE)
    para('From the box<br/>to your first glass.',M,395,CW,22,28,'#FFFFFF',limit=70)
    text('SEVEN STEPS. EVERY CONNECTION.',M,519,9,'Semibold',ICE)
    text('homesodamachine.com',M,558,10,'Regular','#FFFFFF')
page_no=1
front_cover()
c.bookmarkPage('page-1');c.addOutlineEntry('1. Install guide','page-1',0,False);c.showPage()

# 2
header('Your route to soda',sub='Use this booklet on its own, or beside the quick start. The same seven steps appear in both.')
route=[('INSTALL',[(1,'Mount the faucet','5-6',5),(2,'Add the cold-water tee','7-11',7),(3,'Match the rear connections','12-13',12)]),('TURN IT ON',[(4,'Prepare the cylinder','14-15',14),(5,'Water, then gas, then power','16-18',16)]),('YOUR FIRST GLASS',[(6,'Fill both flavors','19-20',19),(7,'Chill. Choose. Pour.','21',21)])]
y=150
for phase,rows in route:
    label(phase,M,y);y+=24
    for n,title,pages,target in rows:
        badge(n,M,y-2,9);text(title,M+27,y+1,10.7,'Semibold',NAVY)
        text(pages,335-pdfmetrics.stringWidth(pages,'Regular',10),y+1,10,'Regular',MUTED)
        c.linkRect('',f'page-{target}',(M,H-y-23,W-M,H-y+5),relative=1,thickness=0);y+=31
    y+=13
note('BEFORE THE FIRST CONNECTION','Check the kit and the space on pages 3-4. Keep the cylinder valve closed and the power cord unplugged while you install.',459)
end()

# 3
header('Have everything ready',sub='Unpack the appliance, faucet bag and install kit before opening a water connection.')
label('IN THE BOX',M,146)
rows=[('Faucet assembly','Faucet, three attached tubes and display cable; steel under-counter plate.'),('Water connections','Black tee with short jumper, long white run and inline filter; a separate white tee for a braided hose.'),('Gas connections','Two-gauge regulator and red tether with two gray fittings already assembled.'),('Tools and cord','Collet press and grounded power cord. Keep the bagged cold kit for later.')]
y=166
for title,s in rows:
    text(title,M,y,11,'Bold',NAVY);hh=para(s,M,y+16,CW,10.5,14,limit=42);y+=hh+29
line(M,y-4,W-M,y-4)
label('YOU SUPPLY',M,y+10)
para('A filled <b>5 lb CO2 cylinder</b>, two <b>14.8 fl oz (440 mL)</b> bottles of SodaStream-compatible concentrate, an <b>adjustable wrench</b> for the regulator nut, and a cup and towel.',M,y+29,CW,11,15,limit=75)
para('The braided-hose path also needs a second wrench to hold the shutoff steady. A prepared counter hole, cold water and grounded 120 V complete the setup.',M,y+104,CW,10.5,14,limit=56)
end()

# 4
header('Make room',sub='Prepare the opening and cabinet before lowering the faucet.')
pic('opening.png',M,145,134,121)
text('1-3/8 in hole',187,157,19,'Bold',NAVY)
para('One opening through the counter.<br/>Counter thickness: <b>3/4 to 1-1/2 in.</b>',187,188,177,10.5,14,limit=56)
caption('Have a countertop fabricator prepare a stone counter.',275)
line(M,304,W-M,304)
text('Space around the appliance',M,314,16,'Bold',NAVY)
text('8-1/2 in wide, 18-1/4 in deep, 14-1/4 in tall.',M,338,10,'Regular',INK)
# A plan-view diagram uses page dimensions for the clearance labels.
rect(57,359,125,159,ICE,r=4);rect(73,382,93,136,'#E8EBF0',stroke=INK,r=3)
rect(79,461,81,50,'#D8DCE3',stroke=MUTED,r=2)
text('TOP VIEW',89,410,8,'Semibold',MUTED)
text('Front',106,526,8.5,'Regular',MUTED)
line(166,369,213,369,NAVY,.6);text('2-3/8 in behind',221,364,10,'Semibold',NAVY)
line(178,431,213,431,NAVY,.6);text('1-5/8 in each side',221,426,10,'Semibold',NAVY)
para('Above: room to invert a bottle into the funnel.',221,451,143,10,13,limit=52)
para('Cylinder: its own space beside the appliance, about 5-1/4 in across and 18 in tall, plus the regulator.',221,497,143,9,11,limit=60)
caption('Keep side air paths open.',548,w=165)
end()

# 5
header('Lower. Then push back.', 'INSTALL / MOUNT THE FAUCET',1, 'The faucet, its tubes and cable arrive joined together. Keep the assembly intact.')
p=pic('steps/mount-drop.png',74,149,244,263,crop=(9,33,763,1331))
arrow(*p(190,660),*p(190,963),head=10)
arrow(*p(382,866),*p(585,928),head=9)
leader('Lower',M,257,p(190,800))
leader('Push back',261,333,p(530,912),side='left')
item('1','Feed the tails through', 'Pass all three attached tubes and the display cable through the prepared hole. Lower the faucet onto the counter.',428)
para('<b>Push the faucet away from you</b> until the two black tubes beneath it meet the back edge of the hole. Hold that position for the plate.',M+24,501,CW-24,11,15,limit=45)
end()

# 6
header('Slide the plate.\nTighten the nut.', 'INSTALL / MOUNT THE FAUCET',1)
p=pic('steps/mount-under-slide-clean.png',M,149,CW,148,crop=(205,275,960,575))
arrow(*p(295,405),*p(720,345),head=9)
point=p(869,344)
leader('Plate above washer + nut',M+15,309,point)
para('From below, hold the steel plate against the counter, <b>above the washer and nut already on the shank.</b> Slide the wide slot around the shank and the narrow slot around the black tubes.',M,340,CW,11,15,limit=75)
p=pic('steps/mount-under-tighten-clean.png',M,428,135,112,crop=(670,260,900,503))
turn([p(739,375),p(718,348),p(843,340),p(829,374)],head=9)
para('<b>Hand-tighten the nut.</b><br/>The plate stays flat against the underside of the counter and the faucet stays seated above.',190,433,174,11,15,limit=90)
end()

# 7
header('Which water connection?', 'INSTALL / ADD THE COLD-WATER TEE',2, 'Look at the cold supply under your sink. Use the tee that matches that connection.')
pic('kitchen-push.png',M,156,130,105)
text('1/4 in plastic tube',184,157,13,'Bold',NAVY)
para('A small plastic tube in a push fitting, like a filter or refrigerator line. Use the <b>black tee</b>.',184,181,180,10.5,14,limit=56)
text('Continue on page 8',184,246,10.5,'Bold',BLUE)
line(M,287,W-M,287)
pic('kitchen-hose.png',M,303,130,114)
text('Braided hose',184,308,13,'Bold',NAVY)
para('A braided supply hose threaded onto a <b>3/8 in shutoff</b>. Use the <b>white tee</b>.',184,333,180,10.5,14,limit=56)
text('Continue on pages 9-11',184,396,10.5,'Bold',BLUE)
note('ONE TEE FOR YOUR KITCHEN','The long white filtered run arrives attached to the black tee. Page 11 shows how to move it to the white tee for the braided-hose path.',451)
end()

# 8
header('Connect the plastic tube', 'INSTALL / ADD THE COLD-WATER TEE',2)
pic('steps/modern-water-off.png',M,116,110,61,crop=(170,190,1100,635))
para('<b>Close the cold-water shutoff.</b> Run the tap or dispenser on that line until flow stops. Put a cup and towel beneath the fitting.',162,111,202,10.5,14,limit=70)
p=pic('steps/release-with-press.png',M,204,134,88,crop=(0,0,1840,1040))
arrow(*p(1316.97,779.94),*p(1042.29,700.52),head=6)
arrow(*p(1510,554),*p(1780,632),head=6)
para('<b>Hold the release ring in</b> with the collet press. With your other hand, pull the original white tube out.',184,204,180,10.5,14,limit=70)
p=pic('steps/modern-tee-assembly-ready.png',M,320,134,60,crop=(200,130,1860,670))
arrow(*p(1110,170),*p(810,170),head=6)
para('<b>Push the short jumper</b> on the supplied black tee into the fitting you just opened.',184,316,180,10.5,14,limit=70)
pic('steps/modern-tee-complete.png',M,411,134,60,crop=(200,130,1860,670))
para('<b>Reconnect the original tube</b> to the tee\'s open end. Push both joints fully home; tug gently to check.',184,405,180,10.5,14,limit=70)
note('NEXT: REAR CONNECTIONS / PAGE 12','Keep the water shutoff closed. The white run already includes its filter; its free end goes to the appliance.',489)
end()

# 9
header('The braided-hose path', 'INSTALL / ADD THE COLD-WATER TEE',2, 'These three pages show the white tee connection. After it is in place, continue at Step 3 on page 12.')
pic('two-tees.png',M,159,CW,91)
caption('Black tee: plastic tube. White tee with lever: braided hose.',266)
item('1','Find the cold-water shutoff','Trace the kitchen faucet\'s cold hose down to its valve. The supplied white tee fits a 3/8 in outlet.',315)
item('2','Close it and relieve the pressure','Close the valve, then open the kitchen faucet on cold. Wait for the flow to stop. Set a cup and towel under the connection.',391)
note('CHECK BEFORE LOOSENING','If water keeps flowing, leave the hose connected; the shutoff needs repair. This tee fits a 3/8 in outlet. Do not force it onto another size.',473,'orange')
end()

# 10
header('Lift the hose clear', 'INSTALL / BRAIDED-HOSE CONNECTION',2)
pic('hose-attached.png',M,115,155,228,crop=(270,0,820,940))
pic('hose-removed.png',209,115,155,228,crop=(270,0,820,940))
caption('Valve closed',355,x=M,w=155)
caption('Hose nut lifted clear',355,x=208,w=156)
item('3','Hold the shutoff steady','Use one wrench on the valve body while the other loosens the braided hose\'s nut. Keep the valve from twisting on its pipe.',402)
para('Finish unscrewing the nut by hand, then lift the hose away. Catch the water left in the hose.',M+24,485,CW-24,11,15,limit=45)
end()

# 11
header('Fit the white tee', 'INSTALL / BRAIDED-HOSE CONNECTION',2)
pic('tee-after.png',M,117,153,190)
para('<b>4 / Tee onto valve</b><br/>Start the tee\'s lower nut by hand on the shutoff outlet.',205,120,159,10.5,14,limit=70)
para('<b>5 / Hose onto tee</b><br/>Reconnect the braided hose to the top. Hold the tee steady and nip both joints up with the wrench: snug, then a little more.',205,203,159,10.5,14,limit=112)
line(M,331,W-M,331)
text('6 / Move the white filtered run',M,347,12,'Bold',NAVY)
para('Use the collet press to release the long white run from the black tee\'s branch. Keep the filter and collar on the run. The black tee and its short jumper are not used on this path.',M,371,CW,11,15,limit=75)
para('Push the white run fully into the white tee\'s side port, then tug gently. Leave the tee\'s small lever open so water can reach the appliance later.',M,444,CW,11,15,limit=60)
text('Keep the main shutoff closed. Go to page 12.',M,527,10.5,'Bold',BLUE)
end()

# 12
header('Match the rear connections', 'INSTALL / MATCH THE REAR CONNECTIONS',3)
para('<b>Pull off the CO2 and TAP shipping caps.</b> They fit over the outside of the fittings. Leave the fittings mounted in the appliance.',M,106,CW,11,15,limit=60)
p=pic('steps/the-back-face.png',M+13,171,306,214,crop=(565,40,1565,855))
jack=p(1075,465)
leader('Faucet cable clicks here',95,398,jack)
rows=[('CO2','Red tube from the cylinder','#D7333C','#FFFFFF'),('SODA','Blue tube from the faucet','#1670DB','#FFFFFF'),('TAP','White run from the filter','#FFFFFF',INK),('FLAVOR','Two black tubes; either black port',INK,'#FFFFFF')]
for i,(name,desc,bg,fg) in enumerate(rows):
    yy=435+i*28;rect(M,yy,66,19,bg,stroke=RULE if bg=='#FFFFFF' else None,r=2);text(name,M+7,yy+5,9,'Bold',fg);text(desc,110,yy+4,10,'Regular',INK)
end()

# 13
header('Push home. Then tug.', 'INSTALL / MATCH THE REAR CONNECTIONS',3, 'Every tube needs to reach the fitting\'s internal stop, then stay put when you pull gently.')
pic('steps/connect-rear-open.png',M,151,CW,153,crop=(195,160,1350,880))
para('Push each tube straight in until it bottoms, <b>a little over 1/2 in.</b> A fitting can grip a tube before it reaches the seal, so push to its internal stop. <b>Tug gently</b> to check it holds.',M,318,CW,11,15,limit=75)
line(M,398,W-M,398)
pic('filter-in-cabinet.png',M,416,140,83)
text('Lay the filter flat',193,412,13,'Bold',NAVY)
para('Keep its factory connections together. Route the white tube and faucet tails in loose curves, clear of things that slide in and out.',193,438,171,10.5,14,limit=84)
caption('Keep the extra length coiled. A tight bend can pinch a tube closed.',534)
end()

# 14
header('Attach the regulator', 'TURN IT ON / PREPARE THE CYLINDER',4, 'Stand the filled 5 lb cylinder upright beside the appliance. Keep its valve closed.')
p=pic('steps/co2-ready.png',M,150,CW,230,crop=(80,0,1600,1500))
caption('The regulator\'s large nut meets the cylinder outlet.',389)
item('1','One washer, lying flat','Place one supplied nylon washer flat inside the large nut. Start the nut squarely on the cylinder outlet by hand. Keep the spare washer in your kit.',429)
para('<b>Nip it up with the adjustable wrench.</b> Extra force can damage the washer. Keep the cylinder valve easy to reach.',M+24,510,CW-24,11,15,limit=45)
end()

# 15
header('Connect the red tether', 'TURN IT ON / PREPARE THE CYLINDER',4)
p=pic('steps/co2-connected.png',M,117,159,220,crop=(420,775,830,1335))
leader('Gray connector',209,158,p(637,943),side='left')
para('Screw the gray connector onto the regulator\'s bottom outlet <b>by hand until it stops.</b>',209,197,155,11,15,limit=75)
para('Its rubber washer makes the seal. Keep both gray fittings assembled.',209,281,155,10.5,14,limit=56)
line(M,369,W-M,369)
item('2','Check the other end','The red tube belongs in the appliance\'s red CO2 port. Push it fully home and tug gently.',390)
note('KEEP THE CYLINDER CLOSED','Finish all connections before opening water or gas. The next three pages take you through water, gas and power in that order.',481)
end()

# 16
header('First, open the water', 'TURN IT ON / WATER, GAS, POWER',5)
label('1 / WATER',M,107)
pic('steps/modern-water-on.png',M,142,CW,125,crop=(170,190,1100,635))
caption('Plastic-tube shutoff shown open, handle in line with the tube.',281)
item('1','Open the shutoff slowly','On the braided-hose path, also check that the white tee\'s small side-port lever is open.',331)
item('2','Watch for a full minute','Inspect the tee, both filter ends and the appliance TAP connection. Keep the power cord unplugged while you check.',415)
note('IF YOU SEE WATER','Close the water shutoff. Resolve the leak before opening the cylinder or connecting power. Page 23 has the first checks.',489,'orange')
end()

# 17
header('Then, open the gas', 'TURN IT ON / WATER, GAS, POWER',5)
label('2 / GAS',M,107)
gas_pose=((.08,1,.12),(-34.7549267293,3.0634158833,-30.1918478747),129.375,(1800,1500))
p=pic('steps/startup-gas.png',M,141,210,158,crop=(173,53,1752,1360))
leader('Cylinder valve',245,153,projected(p,(-115,0,33),*gas_pose),side='left')
leader('Big knob',245,207,projected(p,(0,45,0),*gas_pose),side='left')
leader('Small knob',245,264,projected(p,(0,27,-47),*gas_pose),side='left')
pic('steps/startup-gas.png',278,320,71,71,crop=(533,48,873,388))
para('Open the <b>cylinder valve</b>, then the regulator\'s <b>small knob</b>. Turn the <b>big knob</b> until the <b>upper gauge needle sits in the green band.</b>',M,325,221,11,15,limit=75)
para('Listen at the large nut, gray connector and red CO2 port. A continuing hiss means a leak. Soapy water at a joint can reveal it as growing bubbles.',M,421,CW,11,15,limit=60)
note('CHECK BEFORE POWER','If gas continues to escape, close the cylinder valve. Page 23 has the connection checks. Retest before connecting power.',489,'orange')
end()

# 18
header('Finally, connect power', 'TURN IT ON / WATER, GAS, POWER',5)
label('3 / POWER',M,107)
p=pic('steps/power-ready.png',M,143,CW,176,crop=(0,160,1800,1140))
arrow(*p(490.44,603.57),*p(1061.06,477.95),head=10)
item('1','Seat the appliance end','Push the cord straight into the top-left socket on the back of the appliance.',343)
item('2','Plug into grounded 120 V','The appliance chimes and its enclosure display starts. Follow the display if it reports an issue.',423)
note('POWER REQUIREMENTS','120 V, 60 Hz; 5 A, 600 W. Use the supplied grounded cord. The socket\'s 250 V marking describes the connector; the appliance uses 120 V.',475)
end()

# 19
header('Choose the flavor to fill', 'YOUR FIRST GLASS / FILL BOTH FLAVORS',6, 'Use the enclosure display under the counter. The left rail chooses which reservoir you are filling.')
# The frozen interface illustration is authored beside the scene snapshots.
if (ART/'fill-screen-framed.png').exists():pic('fill-screen-framed.png',M,159,CW,199,fade_crops=False)
else:
    raise FileNotFoundError(ART/'fill-screen-framed.png')
caption('Flavor 1 is selected. Fill and Start filling are separate controls.',373)
item('1','Choose a flavor','Tap its image on the left. The large portrait shows your selected flavor.',414)
item('2','Open Fill','Tap Fill across the top. Leave the Start filling button alone until the concentrate is in place on the next page.',488)
end()

# 20
header('Bottle first. Then start.', 'YOUR FIRST GLASS / FILL BOTH FLAVORS',6)
p=pic('steps/fill-ready.png',M,118,171,235,crop=(295,330,1555,1450))
arrow(*p(947.15,473.85),*p(947.15,943.67),head=8)
para('<b>3 / Add concentrate</b><br/>Invert one whole <b>14.8 fl oz (440 mL)</b> bottle into the top funnel.',223,142,141,11,15,limit=120)
para('<b>4 / Start filling</b><br/>Tap <b>Start filling</b>. Let the appliance draw the concentrate into the selected reservoir.',223,266,141,11,15,limit=105)
line(M,387,W-M,387)
item('5','Wait for Filled','When the display says Filled, that bottle is in the reservoir. Remove the empty bottle.',406)
item('6','Repeat for the second flavor','Select the other image on the left, open Fill, put its bottle in the funnel, then tap Start filling.',485)
end()

# 21
header('Chill. Choose. Pour.', 'YOUR FIRST GLASS',7)
rect(M,105,CW,38,BLUE,r=5);text('FIRST CHILL: ABOUT 1 HOUR',M+15,118,14,'Bold','#FFFFFF')
p=pic('steps/pour-base.png',91,161,244,247,crop=(150,95,1475,1495))
pose=((1,-1.8,.67),(0,-78,119),140)
tap=projected(p,(0,-131.55,217.61),*pose)
leader('Tap screen',M,199,tap)
press=projected(p,(0,-38,39),*pose)
arrow(press[0],press[1]-23,press[0],press[1]-2,head=7)
leader('Press down',287,355,(press[0]+6,press[1]-12),side='left')
item('1','Choose at the faucet','Tap the faucet display to select a flavor. If the screen is dim, the first tap wakes it.',430)
item('2','Fill your glass with ice','Put it below the faucet and press the lever down to pour over the ice. Release the lever to stop.',505)
end()

# 22
header('Keep it ready', 'AFTER INSTALLATION')
text('Top up a flavor',M,111,13,'Bold',NAVY)
para('Use the same Fill sequence on pages 19-20. If the display says <b>Full</b>, the reservoir is full and some concentrate remains in the funnel. Stop adding concentrate.',M,135,CW,11,15,limit=75)
line(M,210,W-M,210)
pic('collet-press.png',M,228,80,75)
text('Rinse the funnel',135,231,13,'Bold',NAVY)
para('Rinse it weekly and after a flavor change. The silicone funnel is dishwasher safe.',135,255,229,10.5,14,limit=56)
para('When empty, release the funnel\'s drain connection with the collet press. Lift the funnel with its short drain stub and clamp attached. Refit it and push the connection fully home.',M,328,CW,11,15,limit=75)
line(M,406,W-M,406)
text('Filter and cylinder',M,423,13,'Bold',NAVY)
para('Replace the water filter once a year. Release pressure in the white water line as described on page 23 before opening its connections. Keep the spare nylon cylinder washer with the install kit for the next cylinder refill.',M,449,CW,11,15,limit=75)
caption('Keep the collet press. The bagged cold kit is for shortening and insulating the faucet run after installation is complete.',532)
end()

# 23
header('Check the leaking connection', 'FIRST CHECKS')
para('<b>Close the water shutoff and cylinder valve.</b> Unplug the appliance. Leave pressurized connections assembled.',M,105,CW,10.8,14.5,limit=43.5)
line(M,158,W-M,158)
text('Water at a push fitting',M,175,13,'Bold',NAVY)
y=para('<b>Tee, filter or white TAP tube:</b> run the tap or dispenser fed by that same cold-water line until flow stops. Keep the white tee\'s side lever open, if used.<br/><b>Blue SODA tube:</b> put a jug under the soda faucet and press its lever until water and hissing stop.',M,199,CW,10.8,14.5,limit=101.5)
y=199+y+10
y+=para('After pressure is released, hold the fitting\'s release ring in with the collet press and pull the tube out. Check for dirt or damage. Push an undamaged tube fully to the internal stop, then tug gently.',M,y,CW,10.8,14.5,limit=72.5)
line(M,y+12,W-M,y+12)
y+=29
text('Gas at a connection',M,y,13,'Bold',NAVY)
y+=24
y+=para('Growing bubbles in soapy water show the leaking joint. The cylinder nut seals on one flat nylon washer; the gray connector seals on rubber. A crooked washer needs reseating; replace a damaged seal. See page 14.',M,y,CW,10.8,14.5,limit=72.5)
y+=10
y+=para('<b>Keep gas fittings assembled until the regulator and red tether are depressurized.</b> Do not loosen a fitting to let pressure out.',M,y,CW,10.8,14.5,limit=43.5)
line(M,y+12,W-M,y+12)
y+=29
para('<b>After repair:</b> repeat the water and gas checks on pages 16-17. Connect power only when water joints stay dry and gas joints show no growing bubbles.',M,y,CW,10.8,14.5,limit=58)
end()

# 24
def back_cover():
    begin_page()
    ground(BLUE)
    c.drawImage(image_reader(ART/'brand/mark-1024.png',BLUE),M-10,H-139,width=120,height=120)
    label('HOME SODA MACHINE',M,164,'#FFFFFF',9)
    text('On tap.',M,212,45,'Bold','#FFFFFF')
    rect(M,282,49,4,ORANGE)
    para('Keep this guide<br/>with your install kit.',M,315,CW,21,27,'#FFFFFF',limit=60)
    para('<b>No pour:</b> check the water shutoff and the tee lever. <b>No power:</b> check the cord and outlet, then read any display message. <b>Warm pour:</b> allow about an hour for the first chill.',M,408,CW,10.5,14,ICE,limit=56)
    para('<b>Sealed cooling circuit</b><br/>R-600a (isobutane), flammable refrigerant.<br/>Under 1.5 oz (40 g). Do not open, puncture or heat.',M,472,CW,9,12,ICE,limit=48)
    text('homesodamachine.com',M,533,16,'Semibold','#FFFFFF')
    text('Guides: homesodamachine.com/drawings',M,563,9,'Regular',ICE)
    c.linkURL('https://homesodamachine.com',(M,H-550,W-M,H-530),relative=1)
    c.linkURL('https://homesodamachine.com/drawings',(M,H-577,W-M,H-560),relative=1)
page_no+=1
back_cover()
c.bookmarkPage('page-24');c.addOutlineEntry('24. Keep your guide','page-24',0,False)
c.showPage()
c.save()
assert page_no==24
if contours.pending:
    contours.render()
    subprocess.run([sys.executable,str(Path(__file__).resolve())]+sys.argv[1:],cwd=ROOT,check=True)
    sys.exit(0)
write_editions(buffer.getvalue(),PDF,PRESS_DIR,ROOT/'output/pdf',OUT)
subprocess.run(['pdftoppm','-f','1','-l','1','-scale-to','1200','-singlefile','-png',str(PDF),str(OUT/'cover')],check=True)
im=Image.open(OUT/'cover.png');im.thumbnail((800,1200));im.save(DIR/'install-guide.cover.png')
(DIR/'install-guide.pdf.json').write_text(json.dumps({'title':'Home Soda Machine install guide','subtitle':'Owner install guide - seven steps in detail - 24 pages, 6.625 x 10.25 in','pages':24,'cover':'install-guide.cover.png','cover_size':list(im.size)},indent=2)+'\n')
(OUT/'layout-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
(OUT/'image-checks.json').write_text(json.dumps(image_checks,indent=2)+'\n')
print(f'{PDF}: {page_no} pages, {PDF.stat().st_size//1024} KB')
subprocess.run([sys.executable,str(Path(__file__).with_name('preflight.py'))],cwd=ROOT,check=True)
make_order_bundle(PRESS_DIR,ROOT/'output/pdf')
