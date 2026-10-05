#!/usr/bin/env python3
"""Compose the 32-interior-page, 9 x 7 inch owner install guide."""
from pathlib import Path
import io
import json
import math
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.utils import ImageReader

from contours import Contours, PAD
from press import BLEED, TRIM_W, TRIM_H, write_editions, make_order_bundle

ROOT = Path(__file__).resolve().parents[2]
DIR = ROOT / 'hardware/install-guide'
ART = DIR / 'assets'
OUT = DIR / 'out/landscape'
PDF = DIR / 'install-guide.pdf'
PRESS_DIR = DIR / 'press'
W, H = TRIM_W, TRIM_H
M, CW = 44, W - 88
RIGHT, RW = 350, W - M - 350
BLUE, NAVY, ICE, ORANGE = '#1749D1', '#10319C', '#DCE6FF', '#FF9152'
INK, MUTED, RULE, CORAL = '#202337', '#606A78', '#DCE2EB', '#D64050'
for name in ['Regular', 'Semibold', 'Bold']:
    pdfmetrics.registerFont(TTFont(name, str(DIR/'fonts'/f'Plex-{name}.ttf')))
pdfmetrics.registerFontFamily('Regular', normal='Regular', bold='Bold',
                             italic='Regular', boldItalic='Bold')
contours = Contours('#46515b', width=.72)
buffer = io.BytesIO()
c = canvas.Canvas(buffer, pagesize=(W+2*BLEED, H+2*BLEED),
                  pageCompression=1, invariant=1, initialFontName='Regular')
c.setTitle('Home Soda Machine - Install guide')
c.setAuthor('Derek Bredensteiner')
c.setSubject('Seven steps to the first glass. 32 interior pages. 9 x 7 inch landscape.')
page_no = 0
checks, image_checks, titles = [], [], []
resolutions = json.loads((ART/'print-resolution.json').read_text())['assets']
FILL = json.loads((ART/'fill-scene-inputs.json').read_text())
FILL_POSE = tuple(FILL['pose'][key] for key in ('cam', 'target', 'span'))


def begin_page():
    c.translate(BLEED, BLEED)


def rect(x, y, w, h, fill, stroke=None, r=0):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke or fill))
    c.setLineWidth(.7)
    if r:
        c.roundRect(x, H-y-h, w, h, r, fill=1, stroke=bool(stroke))
    else:
        c.rect(x, H-y-h, w, h, fill=1, stroke=bool(stroke))


def ground(color):
    rect(-BLEED, -BLEED, W+2*BLEED, H+2*BLEED, color)


def line(x1, y1, x2, y2, color=RULE, width=.8):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width)
    c.line(x1, H-y1, x2, H-y2)


def text(s, x, y, size=13, font='Regular', color=INK):
    width = pdfmetrics.stringWidth(s, font, size)
    if x < 36 or x+width > W-36 or y < 36 or y+size > H-36:
        raise ValueError(f'Page {page_no}: text outside safety margin: {s!r}')
    c.setFillColor(HexColor(color))
    c.setFont(font, size)
    c.drawString(x, H-y-size*.8, s)


def para(s, x, y, w=CW, size=13, leading=18, color=INK,
         font='Regular', limit=None, alignment=0):
    p = Paragraph(s, ParagraphStyle('body', fontName=font, fontSize=size,
                                    leading=leading, textColor=HexColor(color),
                                    alignment=alignment))
    _, h = p.wrap(w, 1000)
    if limit is not None and h > limit+.1:
        raise ValueError(f'Page {page_no}: paragraph {h}>{limit}: {s[:80]}')
    if x < 36 or x+w > W-36 or y < 36 or y+h > 441:
        raise ValueError(f'Page {page_no}: paragraph overflow {y+h}: {s[:80]}')
    p.drawOn(c, x, H-y-h)
    checks.append(dict(page=page_no, text=s, box=[x, y, w, h]))
    return h


def label(s, x, y, color=BLUE, size=9):
    c.saveState()
    t = c.beginText(x, H-y-size*.8)
    t.setFont('Bold', size)
    t.setFillColor(HexColor(color))
    t.setCharSpace(1)
    t.textOut(s.upper())
    c.drawText(t)
    c.restoreState()


def badge(n, x, y, r=14):
    c.setFillColor(HexColor(BLUE))
    c.circle(x+r, H-y-r, r, stroke=0, fill=1)
    text(str(n), x+r-pdfmetrics.stringWidth(str(n), 'Bold', 16)/2,
         y+6, 16, 'Bold', '#FFFFFF')


def header(title, phase='BEFORE YOU START', step=None, sub=None):
    global page_no
    page_no += 1
    begin_page()
    ground('#FFFFFF')
    rect(-BLEED, -BLEED, W+2*BLEED, 7+BLEED, BLUE)
    label(phase, M, 40)
    width = CW-44 if step else CW
    size = min(28, 28*width/pdfmetrics.stringWidth(title, 'Bold', 28))
    text(title, M, 64, size, 'Bold', NAVY)
    if step is not None:
        badge(step, W-M-28, 61)
    if sub:
        para(sub, M, 103, CW, 12, 16, MUTED, limit=32)
    c.bookmarkPage(f'page-{page_no}')
    c.addOutlineEntry(f'{page_no-1}. {title}', f'page-{page_no}', 0, False)
    titles.append(title)


def end():
    line(M, 449, W-M, 449)
    text('HOME SODA MACHINE', M, 459, 8, 'Bold', NAVY)
    text('Install guide', 275, 459, 8, 'Regular', MUTED)
    number = str(page_no-1)
    text(number, W-M-pdfmetrics.stringWidth(number, 'Semibold', 9),
         458, 9, 'Semibold', NAVY)
    c.showPage()


def image_reader(source, background='#FFFFFF'):
    im = Image.open(source).convert('RGBA') if isinstance(source, (str, Path)) else source.convert('RGBA')
    flat = Image.new('RGB', im.size, background)
    flat.paste(im, mask=im.getchannel('A'))
    return ImageReader(flat)


def pic(name, x, y, w, h, crop=None, outline=True, fade_crops=True):
    source = ART/name
    im = Image.open(source)
    resolution = resolutions.get(name, {})
    if resolution and list(im.size) != resolution['render_size']:
        raise ValueError(f'{name}: dimensions disagree with print-resolution.json')
    rx, ry = resolution.get('scale', [1, 1])
    if crop:
        crop = tuple(value*factor for value, factor in zip(crop, (rx, ry, rx, ry)))
    bounds = crop or (im.getchannel('A').getbbox() if im.mode == 'RGBA' else None) or (0, 0, im.width, im.height)
    a, b, cc, d = bounds
    scale = min(w/(cc-a), h/(d-b), 72/300)
    iw, ih = (cc-a)*scale, (d-b)*scale
    ox, oy = x+(w-iw)/2, y+(h-ih)/2
    ppi = 72/scale
    image_checks.append(dict(page=page_no, source=name, native_pixels=list(im.size),
                             ppi=ppi, box=[ox, oy, iw, ih]))
    if outline:
        target, (pw, ph) = contours.picture(source, bounds, iw, ih, fade_crops=fade_crops)
        if target.exists():
            c.drawImage(image_reader(target), ox-PAD, H-oy-ih-PAD, width=pw, height=ph)
    else:
        c.drawImage(image_reader(im.crop(bounds)), ox, H-oy-ih, width=iw, height=ih)
    return lambda px, py: (ox+(px*rx-a)*scale, oy+(py*ry-b)*scale)


def caption(s, y, x=M, w=264):
    return para(s, x, y, w, 10, 14, MUTED, limit=42)


def kit_picture(name, x, y, w, h):
    svg = ET.parse(ART/'kit'/f'{name}.svg').getroot()
    paths = [[(command, float(px), float(py)) for command, px, py in
              re.findall(r'([ML])([-+\d.eE]+),([-+\d.eE]+)', node.attrib['d'])]
             for node in svg.iter('{http://www.w3.org/2000/svg}path')]
    points = [point for path in paths for point in path]
    left, right = min(p[1] for p in points), max(p[1] for p in points)
    top, bottom = min(p[2] for p in points), max(p[2] for p in points)
    scale = min(w/(right-left), h/(bottom-top))
    ox, oy = x+(w-(right-left)*scale)/2, y+h-(bottom-top)*scale
    c.saveState()
    c.setLineWidth(.68)
    c.setStrokeColor(HexColor('#46515b'))
    c.setLineCap(1)
    c.setLineJoin(1)
    for points in paths:
        path = c.beginPath()
        for command, px, py in points:
            point = ox+(px-left)*scale, H-oy-(py-top)*scale
            (path.moveTo if command == 'M' else path.lineTo)(*point)
        c.drawPath(path, stroke=1, fill=0)
    c.restoreState()


def note(title, s, y, x=M, w=CW, kind='blue'):
    h = Paragraph(s, ParagraphStyle('measure', fontName='Regular', fontSize=12,
                                   leading=17)).wrap(w-28, 1000)[1]+44
    if y+h > 439:
        raise ValueError(f'Page {page_no}: note overflow {title}: {y+h}')
    rect(x, y, w, h, ICE if kind == 'blue' else '#FFF0E6', r=6)
    label(title, x+14, y+13, NAVY if kind == 'blue' else '#8B381B', 8)
    para(s, x+14, y+32, w-28, 12, 17, limit=h-32)
    return h


def item(n, title, s, y, x=RIGHT, w=RW, size=13):
    label(n, x, y)
    text(title, x, y+22, 16, 'Bold', NAVY)
    return 51+para(s, x, y+51, w, size, 18)


def arrow(x1, y1, x2, y2, head=9):
    length = math.hypot(x2-x1, y2-y1)
    ux, uy = (x2-x1)/length, (y2-y1)/length
    bx, by = x2-head*ux, y2-head*uy
    shaft = c.beginPath()
    shaft.moveTo(x1, H-y1)
    shaft.lineTo(bx, H-by)
    tip = c.beginPath()
    tip.moveTo(x2, H-y2)
    tip.lineTo(bx-head*.45*uy, H-by-head*.45*ux)
    tip.lineTo(bx+head*.45*uy, H-by+head*.45*ux)
    tip.close()
    c.saveState()
    c.setLineCap(1)
    for color, width in [(white, 4.8), (HexColor(CORAL), 2.7)]:
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(width)
        c.drawPath(shaft, stroke=1)
        c.drawPath(tip, fill=1, stroke=1 if color == white else 0)
    c.restoreState()


def leader(s, x, y, point, side='right'):
    text(s, x, y, 10, 'Semibold', INK)
    width = pdfmetrics.stringWidth(s, 'Semibold', 10)
    start = (x+width+6, y+4) if side == 'right' else (x-6, y+4)
    for color, stroke in [('#FFFFFF', 3), (INK, .8)]:
        line(*start, *point, color, stroke)
    c.setFillColor(HexColor(CORAL))
    c.setStrokeColor(white)
    c.setLineWidth(.8)
    c.circle(point[0], H-point[1], 2.5, fill=1, stroke=1)


def projected(mapper, point, cam, target, span, size=(1600, 1500)):
    def unit(v):
        length = math.sqrt(sum(t*t for t in v))
        return tuple(t/length for t in v)
    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
    direction = unit(cam)
    right = unit(cross((0, 0, 1), direction))
    up = cross(direction, right)
    delta = tuple(p-t for p, t in zip(point, target))
    scale = size[1]/(2*span)
    return mapper(size[0]/2+sum(a*b for a, b in zip(delta, right))*scale,
                  size[1]/2-sum(a*b for a, b in zip(delta, up))*scale)


def front_cover():
    global page_no
    page_no = 1
    begin_page()
    ground(BLUE)
    label('HOME SODA MACHINE', 52, 51, '#FFFFFF', 11)
    text('Install', 52, 145, 60, 'Bold', '#FFFFFF')
    text('guide', 52, 211, 60, 'Bold', '#FFFFFF')
    c.drawImage(image_reader(ART/'brand/mark-1024.png', BLUE), 373, H-295,
                width=222, height=222)
    rect(52, 311, 64, 5, ORANGE)
    para('From the box<br/>to your first glass.', 52, 345, 328, 23, 30,
         '#FFFFFF', limit=60)
    text('SEVEN STEPS. EVERY CONNECTION.', 52, 445, 9, 'Semibold', ICE)
    text('homesodamachine.com', 425, 445, 10, 'Regular', '#FFFFFF')
    c.bookmarkPage('page-1')
    c.addOutlineEntry('Cover', 'page-1', 0, False)
    c.showPage()


front_cover()

# Interior 1
header('Your first glass starts here', sub='Keep this booklet beside you while you install. Follow the seven steps in order.')
pic('steps/pour-base.png', M, 145, 260, 271, crop=(150, 40, 1475, 1500))
text('Make the connections.', RIGHT, 158, 18, 'Bold', NAVY)
para('Start with the faucet and cold-water supply. Match each tube to its color on the back of the machine.', RIGHT, 190, RW)
text('Fill both flavors.', RIGHT, 271, 18, 'Bold', NAVY)
para('Use one concentrate bottle for each reservoir. The display walks you through Fill.', RIGHT, 304, RW)
para('<b>Then chill, choose and pour.</b><br/>The first chill takes about an hour. Fill your glass with ice before pouring.', RIGHT, 373, RW, 12, 17, limit=68)
end()

# Interior 2
header('Your route to soda', sub='Follow the seven steps in order. Page numbers below refer to this booklet.')
route = [(1, 'Mount the faucet', '5-8', 5),
         (2, 'Add the cold-water tee', '9-16', 9),
         (3, 'Match the rear connections', '17-18', 17),
         (4, 'Prepare the cylinder', '19-21', 19),
         (5, 'Water, then gas, then power', '22-24', 22),
         (6, 'Fill both flavors', '25-27', 25),
         (7, 'Chill. Choose. Pour.', '28-29', 28)]
for i, (number, title, pages, target) in enumerate(route):
    y = 145+i*36
    badge(number, M, y, 11)
    text(title, M+35, y+3, 13, 'Semibold', NAVY)
    text(pages, 327-pdfmetrics.stringWidth(pages, 'Regular', 11), y+4, 11, 'Regular', MUTED)
    c.linkRect('', f'page-{target+1}', (M, H-y-25, 333, H-y+2), relative=1, thickness=0)
note('BEFORE THE FIRST CONNECTION', 'Check the kit and space on pages 3-4. Keep the cylinder closed and the power cord unplugged while you install.', 149, RIGHT, RW)
note('KEEP THIS GUIDE', 'Care is on page 30. Connection checks are on pages 31-32.', 334, RIGHT, RW)
end()

# Interior 3
header('Have everything ready', sub='Unpack the kit. Have your own supplies ready before opening a water connection.')
label('IN THE BOX', M, 134)
kit = [('machine', 'Soda machine'),
       ('faucet-and-plate', 'Faucet +<br/>mounting plate'),
       ('filtered-line', 'Filtered water line'),
       ('water-tees', 'Both water tees'),
       ('regulator-and-tether', 'Regulator + CO2 tether<br/>+ nylon washer'),
       ('collet-press', 'Collet press'),
       ('power-cord', 'Power cord'),
       ('install-guide', 'Install guide'),
       ('cold-kit', 'Cold kit')]
for i, (art, title) in enumerate(kit):
    x, y = M+(i%3)*136, 149+(i//3)*99
    title_height = 25 if '<br/>' in title else 12.5
    caption_height = title_height + (13 if art == 'cold-kit' else 0)
    caption_y = y+90-7-caption_height
    rect(x, y, 128, 90, '#FFFFFF', RULE, r=4)
    kit_picture(art, x+8, y+5, 112, caption_y-y-10)
    para(title, x+8, caption_y, 112, 10.5, 12.5, INK, 'Semibold',
         limit=title_height, alignment=1)
    if art == 'cold-kit':
        para('Keep bagged for later.', x+8, caption_y+title_height+1,
             112, 9, 12, MUTED, alignment=1)
rect(459, 144, 145, 295, '#F2F5FB', r=6)
label('YOU SUPPLY', 473, 159, NAVY, 8)
supplies = ['Filled 5 lb CO2 cylinder<br/>(CGA-320)',
            'Concentrate for both flavors<br/>(SodaStream compatible)', 'Adjustable wrench',
            'Second wrench for a braided hose', 'Towel',
            'Prepared counter opening', 'Grounded 120 V outlet']
y = 181
for entry in supplies:
    rect(473, y+2, 8, 8, '#FFFFFF', MUTED, 1)
    h = para(entry, 488, y, 103, 10, 13, limit=52)
    y += h+11
end()

# Interior 4
header('Make room under the counter', sub='Leave the cylinder valve, water shutoff and power plug easy to reach.')
rect(65, 152, 237, 224, ICE, r=6)
rect(97, 179, 172, 194, '#E8EBF0', INK, 4)
rect(110, 292, 146, 68, '#D8DCE3', MUTED, 3)
text('TOP VIEW', 150, 229, 11, 'Semibold', MUTED)
text('Front', 165, 391, 11, 'Regular', MUTED)
text('Machine envelope', RIGHT, 152, 17, 'Bold', NAVY)
para('<b>8-1/2 in wide</b><br/><b>18-3/8 in deep</b><br/><b>14-3/8 in tall, with cover</b>', RIGHT, 187, RW, 13, 20)
para('Leave <b>2-3/8 in behind</b> and <b>1-5/8 in on each side.</b> Keep the side air paths open.', RIGHT, 268, RW)
para('Above: room to invert a bottle into the funnel.<br/><br/>Beside it: space for the cylinder, about 5-1/4 in across and 18 in tall, plus its regulator.', RIGHT, 338, RW, 12, 17, limit=102)
end()

# Interior 5
header('Prepare the counter opening', 'INSTALL / MOUNT THE FAUCET', 1)
pic('opening.png', M, 151, 264, 220)
text('One 1-3/8 in opening', RIGHT, 158, 18, 'Bold', NAVY)
para('Use one opening through the counter for the faucet, tubes and cable.<br/><br/>Counter thickness:<br/><b>3/4 to 1-1/2 in.</b>', RIGHT, 194, RW, 13, 19, limit=133)
note('STONE COUNTER', 'Use a spare 1-3/8 in sink or counter hole, or a 1-3/8 in diamond core bit kept wet.', 351, RIGHT, RW)
caption('Prepare the opening before lowering the faucet.', 390)
end()

# Interior 6
header('Lower. Then push back.', 'INSTALL / MOUNT THE FAUCET', 1)
p = pic('steps/mount-drop.png', M, 125, 274, 294, crop=(9, 33, 763, 1331))
arrow(*p(190, 660), *p(190, 963), head=11)
arrow(*p(382, 866), *p(585, 928), head=10)
item('1 / LOWER', 'Feed the tails through', 'Pass all three attached tubes and the display cable through the opening. Lower the faucet onto the counter.', 151)
item('2 / POSITION', 'Push the faucet back', 'Push it away from you until the two black tubes beneath it meet the back edge of the hole. Hold that position for the plate.', 299)
end()

# Interior 7
header('Slide the plate into place', 'INSTALL / MOUNT THE FAUCET', 1)
p = pic('steps/mount-under-slide-clean.png', M, 167, 278, 177, crop=(205, 275, 960, 575))
arrow(*p(295, 405), *p(720, 345), head=10)
caption('The plate sits above the washer and nut.', 365)
item('3 / FROM BELOW', 'Hold the plate flat', 'Hold the steel plate against the underside of the counter, above the washer and nut already on the shank.', 153)
para('Slide its <b>wide slot around the shank</b> and its <b>narrow slot around the black tubes and cable.</b>', RIGHT, 318, RW, 13, 19, limit=95)
end()

# Interior 8
header('Tighten the faucet nut', 'INSTALL / MOUNT THE FAUCET', 1)
pic('steps/mount-under-tighten-clean.png', M, 156, 270, 228, crop=(670, 260, 900, 503))
item('4 / SECURE', 'Hand-tighten the nut', 'Keep the plate flat against the underside of the counter. The faucet stays seated above.', 158)
note('CHECK THE POSITION', 'The faucet stays pushed back, with the black tubes against the back edge of the hole.', 323, RIGHT, RW)
end()

# Interior 9
header('Which water connection?', 'INSTALL / ADD THE COLD-WATER TEE', 2,
       'Look at the cold supply under your sink. Use the tee that matches it.')
pic('kitchen-push.png', M, 145, 225, 121)
text('1/4 in plastic tube', M, 286, 18, 'Bold', NAVY)
para('A small tube in a push fitting, like a filter or refrigerator line. Use the <b>black tee</b>.', M, 321, 258)
text('Continue on pages 10-12', M, 403, 12, 'Bold', BLUE)
pic('kitchen-hose.png', RIGHT, 145, RW, 121)
text('Braided hose', RIGHT, 286, 18, 'Bold', NAVY)
para('A braided supply hose threaded onto a <b>3/8 in shutoff</b>. Use the <b>white tee</b>.', RIGHT, 321, RW)
text('Continue on pages 13-16', RIGHT, 403, 12, 'Bold', BLUE)
end()

# Interior 10
header('Close the cold-water shutoff', 'INSTALL / PLASTIC-TUBE CONNECTION', 2)
pic('steps/modern-water-off.png', M, 167, 278, 169, crop=(170, 190, 1100, 635))
caption('Keep the shutoff closed while making connections.', 368)
item('1 / WATER OFF', 'Wait for flow to stop', 'Close the cold-water shutoff. Run the tap or dispenser on that line until flow stops.', 156)
para('Put a towel beneath the fitting to catch the water left in the tube.', RIGHT, 318, RW)
end()

# Interior 11
header('Release the original tube', 'INSTALL / PLASTIC-TUBE CONNECTION', 2)
p = pic('steps/release-with-press.png', M, 173, 278, 173, crop=(0, 0, 1840, 1040))
arrow(*p(1316.97, 779.94), *p(1042.29, 700.52), head=8)
arrow(*p(1510, 554), *p(1780, 632), head=8)
item('2 / RELEASE', 'Hold the ring in', 'Use the collet press to hold the fitting\'s release ring in. With your other hand, pull the original white tube out.', 153)
note('KEEP THE TOOL', 'The collet press also releases the machine\'s push-connect tubes when their pressure has been relieved.', 321, RIGHT, RW)
end()

# Interior 12
header('Fit the black tee', 'INSTALL / PLASTIC-TUBE CONNECTION', 2)
p = pic('steps/modern-tee-assembly-ready.png', M, 145, 278, 90, crop=(200, 130, 1860, 670))
arrow(*p(1110, 170), *p(810, 170), head=9)
pic('steps/modern-tee-complete.png', M, 286, 278, 90, crop=(200, 130, 1860, 670))
item('3 / JUMPER', 'Push it fully home', 'Push the short jumper on the supplied black tee into the fitting you opened.', 137)
item('4 / ORIGINAL TUBE', 'Reconnect. Then tug.', 'Push the original tube into the tee\'s open end. Tug both joints gently to check they hold.', 281)
caption('Keep the filtered white run attached. Go to page 17.', 403, w=CW)
end()

# Interior 13
header('Prepare the braided-hose connection', 'INSTALL / BRAIDED-HOSE CONNECTION', 2)
pic('two-tees.png', M, 162, 274, 121)
caption('The white tee has a side-port lever.', 315)
item('1 / FIND COLD', 'Trace the hose to its valve', 'The white tee fits a 3/8 in outlet. Close that valve, then open the kitchen faucet on cold. Wait for flow to stop.', 145)
note('BEFORE LOOSENING', 'If water keeps flowing, leave the hose connected; the shutoff needs repair. Put a towel below the connection.', 321, RIGHT, RW, 'orange')
end()

# Interior 14
header('Lift the braided hose clear', 'INSTALL / BRAIDED-HOSE CONNECTION', 2)
pic('hose-attached.png', M, 135, 130, 215, crop=(270, 0, 820, 940))
pic('hose-removed.png', 192, 135, 130, 215, crop=(270, 0, 820, 940))
caption('Valve closed', 369, w=130)
caption('Hose lifted clear', 369, x=192, w=130)
item('2 / TWO WRENCHES', 'Hold the valve steady', 'Use one wrench on the valve body while the other loosens the hose nut. Keep the valve from twisting on its pipe.', 153)
para('Finish unscrewing the nut by hand. Lift the hose away and catch the water left in it.', RIGHT, 319, RW)
end()

# Interior 15
header('Fit the white tee', 'INSTALL / BRAIDED-HOSE CONNECTION', 2)
pic('tee-after.png', M, 137, 264, 269)
item('3 / TEE ONTO VALVE', 'Start the lower nut by hand', 'Thread the tee\'s lower nut onto the shutoff outlet. Keep the valve body steady.', 144)
item('4 / HOSE ONTO TEE', 'Reconnect the braided hose', 'Start the hose nut on the tee\'s top by hand. Hold the tee steady and nip both joints up: snug, then a little more.', 291)
end()

# Interior 16
header('Move the white filtered run', 'INSTALL / BRAIDED-HOSE CONNECTION', 2)
pic('filter-in-cabinet.png', M, 164, 274, 179)
caption('Keep the filter and its tube collar on the run.', 371)
item('5 / MOVE THE RUN', 'Release it from the black tee', 'Use the collet press on the black tee\'s branch. Its short jumper and the black tee are not used on this path.', 146)
para('Push the filtered white run fully into the white tee\'s side port, then tug gently. Leave the small side-port lever open.', RIGHT, 294, RW)
text('Keep the main shutoff closed.', RIGHT, 396, 12, 'Bold', BLUE)
end()

# Interior 17
header('Match the rear connections', 'INSTALL / MATCH THE REAR CONNECTIONS', 3)
p = pic('steps/the-back-face.png', M, 148, 282, 253, crop=(565, 40, 1565, 855))
leader('Faucet cable', M, 414, p(1075, 465))
para('Pull off the <b>CO2 and TAP shipping caps.</b> They cover the fittings; leave the fittings mounted.', RIGHT, 136, RW, 12, 17, limit=68)
rows = [('CO2', 'Red tube from the cylinder', '#D7333C', '#FFFFFF'),
        ('SODA', 'Blue tube from the faucet', '#1670DB', '#FFFFFF'),
        ('TAP', 'White run from the filter', '#FFFFFF', INK),
        ('FLAVOR', 'Two black tubes; either port', INK, '#FFFFFF')]
for i, (name, desc, bg, fg) in enumerate(rows):
    y = 231+i*49
    rect(RIGHT, y, 71, 23, bg, RULE if bg == '#FFFFFF' else None, 3)
    text(name, RIGHT+8, y+6, 10, 'Bold', fg)
    text(desc, RIGHT, y+29, 11.5, 'Regular', INK)
end()

# Interior 18
header('Push home. Then tug.', 'INSTALL / MATCH THE REAR CONNECTIONS', 3)
pic('steps/connect-rear-open.png', M, 155, 283, 183, crop=(195, 160, 1350, 880))
caption('Push straight into the fitting, all the way to its stop.', 362)
item('CHECK EVERY TUBE', 'A little over 1/2 in', 'A fitting can grip a tube before it reaches the seal. Push each tube to its internal stop, then tug gently.', 144)
para('<b>Click the faucet cable into its jack.</b><br/><br/>Lay the filter flat. Keep its factory connections together and route the tails in loose curves, clear of things that slide in and out.', RIGHT, 303, RW, 12, 17, limit=136)
end()

# Interior 19
header('Prepare the CO2 cylinder', 'TURN IT ON / PREPARE THE CYLINDER', 4)
pic('steps/co2-ready.png', M, 135, 278, 279, crop=(0, 0, 1560, 1500))
item('1 / CYLINDER', 'Stand it upright', 'Use a filled 5 lb cylinder with a CGA-320 connection. Stand it beside the machine with its valve closed.', 146)
note('PRESSURE IS ALREADY SET', 'The supplied regulator is set at the factory. Leave its adjusting screw and locknut alone.', 315, RIGHT, RW)
end()

# Interior 20
header('Attach the supplied regulator', 'TURN IT ON / PREPARE THE CYLINDER', 4)
pic('steps/co2-ready.png', M, 137, 278, 266, crop=(0, 0, 1560, 1500))
item('2 / CGA-320 NUT', 'One washer, lying flat', 'Place one supplied nylon washer flat inside the large nut. Start the nut squarely on the closed cylinder outlet by hand.', 146)
para('Snug it with the wrench. Extra force can damage the washer.', RIGHT, 282, RW, 12, 17, limit=51)
note('REGULATOR + TETHER', 'The outlet adapter and red tether arrive fitted to the regulator. Keep them assembled.', 341, RIGHT, RW)
end()

# Interior 21
header('Connect the red tether', 'TURN IT ON / PREPARE THE CYLINDER', 4)
p = pic('steps/connect-rear-open.png', M, 156, 278, 230, crop=(195, 160, 1350, 880))
arrow(*p(730, 438), *p(386, 378), head=10)
caption('Keep the regulator end of the tether assembled.', 402)
item('3 / CO2 PORT', 'Red tube to red fitting', 'Push the free end of the red tether into the machine\'s red CO2 port. Push fully home, then tug gently.', 153)
note('KEEP THE CYLINDER CLOSED', 'Finish all connections before opening water or gas. The next pages take you through water, gas and power in that order.', 319, RIGHT, RW)
end()

# Interior 22
header('First, open the water', 'TURN IT ON / WATER, GAS, POWER', 5)
pic('steps/modern-water-on.png', M, 158, 278, 176, crop=(170, 190, 1100, 635))
caption('Plastic-tube valve: its open handle follows the tube.', 365)
item('1 / WATER', 'Open the shutoff slowly', 'On the braided-hose path, check that the white tee\'s small side-port lever is open too.', 141)
para('<b>Watch for a full minute.</b><br/>Inspect the tee, filter ends and TAP connection. Keep power unplugged.', RIGHT, 267, RW, 12, 17)
note('IF YOU SEE WATER', 'Close the shutoff. Resolve the leak before opening gas or connecting power. See page 31.', 342, RIGHT, RW, 'orange')
end()

# Interior 23
header('Then, open the gas', 'TURN IT ON / WATER, GAS, POWER', 5)
pic('steps/startup-gas.png', M, 138, 278, 269)
item('2 / GAS', 'Open the valve slowly', 'Pressure is factory set. Leave the screw alone; the upper gauge settles near 75 PSI.', 144, size=12)
para('Listen at the cylinder nut, outlet and red CO2 port. A continuing hiss means a leak. Soapy water shows it as growing bubbles.', RIGHT, 251, RW, 12, 17, limit=102)
note('BEFORE POWER', 'If gas continues to escape, close the cylinder. Check page 32 and retest.', 342, RIGHT, RW, 'orange')
end()

# Interior 24
header('Finally, connect power', 'TURN IT ON / WATER, GAS, POWER', 5)
p = pic('steps/power-ready.png', M, 164, 278, 194, crop=(0, 160, 1800, 1140))
arrow(*p(491.16, 602.56), *p(1089.73, 470.79), head=10)
item('3 / POWER', 'Connect the supplied cord', 'Push it straight into the top-left socket on the back of the machine. Plug into a grounded 120 V outlet.', 144)
para('The machine chimes and its display starts. Follow the display if it reports an issue.', RIGHT, 296, RW)
caption('120 V, 60 Hz; 5 A, 600 W. The inlet\'s 250 V marking describes the connector.', 396, w=CW)
end()

# Interior 25
header('Choose the flavor to fill', 'YOUR FIRST GLASS / FILL BOTH FLAVORS', 6)
pic('fill-screen-framed.png', M, 160, 278, 207, fade_crops=False)
caption('Flavor 1 is selected. Fill and Start filling are separate controls.', 389)
item('1 / CHOOSE', 'Tap a flavor on the left', 'The large portrait shows the reservoir you selected.', 149)
item('2 / OPEN FILL', 'Tap Fill across the top', 'Leave Start filling alone until the concentrate is in place on the next page.', 283)
end()

# Interior 26
header('Bottle first. Then start.', 'YOUR FIRST GLASS / FILL BOTH FLAVORS', 6)
p = pic('steps/fill-ready.png', M, 133, 278, 279, crop=(295, 330, 1555, 1450))
arrow(*projected(p, FILL['arrow']['start'], *FILL_POSE),
      *projected(p, FILL['arrow']['end'], *FILL_POSE), head=10)
item('3 / ADD CONCENTRATE', 'Lift off the funnel cover', 'Wipe off water and debris. Lift by the front edge, then invert one whole 14.8 fl oz (440 mL) bottle into the funnel.', 146)
item('4 / START', 'Tap Start filling', 'Let the machine draw the concentrate into the selected reservoir.', 309)
end()

# Interior 27
header('Wait for Filled. Then repeat.', 'YOUR FIRST GLASS / FILL BOTH FLAVORS', 6)
pic('steps/fill-ready.png', M, 130, 278, 282, crop=(295, 330, 1555, 1450))
item('5 / FILLED', 'Remove the empty bottle', 'When the display says Filled, the bottle is in the reservoir. Press the cover down until it rests evenly on the brim.', 145)
item('6 / OTHER FLAVOR', 'Repeat the same sequence', 'Select the other image, open Fill, lift off the cover, put its bottle in the funnel, then tap Start filling.', 295)
end()

# Interior 28
header('Allow the first chill', 'YOUR FIRST GLASS', 7)
pic('steps/pour-base.png', M, 132, 278, 286, crop=(150, 40, 1475, 1500))
label('FIRST CHILL', RIGHT, 152)
text('About 1 hour', RIGHT, 185, 28, 'Bold', NAVY)
para('Let the machine chill before your first pour.', RIGHT, 242, RW, 15, 21)
note('READY FOR YOUR GLASS', 'Keep the water and cylinder supplies open. Choose your flavor at the faucet when you are ready to pour.', 330, RIGHT, RW)
end()

# Interior 29
header('Choose. Ice. Pour.', 'YOUR FIRST GLASS', 7)
p = pic('steps/pour-base.png', M, 131, 278, 283, crop=(150, 40, 1475, 1500))
pose = ((1, -1.8, .67), (0, -78, 119), 140)
tap = projected(p, (0, -134.243, 211.599), *pose)
leader('Tap screen', M, 157, tap)
press = projected(p, (0, -38, 39), *pose)
arrow(press[0], press[1]-26, press[0], press[1]-2, head=9)
item('1 / CHOOSE', 'Tap the faucet display', 'Select a flavor. If the display is dim, the first tap wakes it.', 143)
item('2 / POUR', 'Fill your glass with ice', 'Put it under the faucet and press the lever down. Release the lever to stop.', 284)
end()

# Interior 30
header('Keep it ready', 'AFTER INSTALLATION')
text('Top up a flavor', M, 148, 17, 'Bold', NAVY)
para('Use the Fill sequence on pages 25-27. If the display says <b>Full</b>, concentrate remains in the funnel. Stop adding, remove the bottle and replace the cover.', M, 180, 263, 12, 17, limit=102)
text('Rinse the funnel', M, 296, 17, 'Bold', NAVY)
para('Rinse weekly and after changing flavors. Wash the removable silicone funnel and both faces of its cover by hand.', M, 328, 263, 12, 17, limit=102)
text('Lift out. Press back in.', RIGHT, 148, 17, 'Bold', NAVY)
para('Wipe the cover and lift it by its front edge. When the funnel is empty, lift it straight out. Its plug slides off the drain tube; the tube stays in the machine.', RIGHT, 180, RW, 12, 17, limit=102)
para('To refit, align the plug in its socket and press down until the brim seats. Press the cover evenly onto the brim.', RIGHT, 296, RW, 12, 17, limit=85)
caption('Filter: replace yearly; relieve the white line\'s pressure as on page 31 first. Cylinder: refill when its left gauge reaches the red band. Keep the spare nylon washer for the refill.', 402, w=CW)
end()

# Interior 31
header('Check a leaking water connection', 'FIRST CHECKS')
note('FIRST, CLOSE THE SUPPLIES', 'Close the water shutoff and cylinder valve. Unplug the machine. Leave pressurized connections assembled.', 139)
text('White TAP line', M, 260, 17, 'Bold', NAVY)
para('Run the tap or dispenser on that same cold-water line until flow stops. Keep the white tee\'s side lever open, if used.', M, 292, 263, 12, 17, limit=85)
text('Blue SODA line', M, 365, 17, 'Bold', NAVY)
para('Press the soda lever over a jug until water and hissing stop.', M, 397, 263, 12, 17, limit=34)
text('After pressure is released', RIGHT, 260, 17, 'Bold', NAVY)
para('Hold the release ring in with the collet press. Pull out the tube and check for dirt or damage. Push an undamaged tube fully to its internal stop, then tug gently.', RIGHT, 292, RW, 12, 17, limit=119)
end()

# Interior 32
header('Gas and first-pour checks', 'FIRST CHECKS')
text('Gas at a connection', M, 145, 17, 'Bold', NAVY)
para('Close the cylinder valve. Growing bubbles in soapy water locate a leaking joint.', M, 180, 263, 12, 16, limit=48)
para('<b>Leave the regulator and red tether assembled until depressurized.</b> Do not loosen a fitting to let pressure out.', M, 244, 263, 12, 16, limit=64)
para('Then check the nut\'s flat nylon washer and fully seat both red-tube ends. See pages 20-21.', M, 322, 263, 12, 16, limit=64)
para('After repair, repeat the water and gas checks on pages 22-23 before connecting power.', M, 393, 263, 12, 16, limit=48)
for y, title, s in [(145, 'No pour', 'Check the water shutoff and the white tee\'s side-port lever.'),
                    (242, 'No power', 'Check the cord and outlet, then read any display message.'),
                    (339, 'Warm pour', 'Allow about an hour for the first chill.')]:
    text(title, RIGHT, y, 17, 'Bold', NAVY)
    para(s, RIGHT, y+32, RW, 12, 17, limit=51)
end()


def back_cover():
    global page_no
    page_no += 1
    begin_page()
    ground(BLUE)
    label('HOME SODA MACHINE', 52, 51, '#FFFFFF', 11)
    c.drawImage(image_reader(ART/'brand/mark-1024.png', BLUE), 44, H-280,
                width=216, height=216)
    text('On tap.', 313, 136, 51, 'Bold', '#FFFFFF')
    rect(315, 212, 57, 5, ORANGE)
    para('Keep this guide<br/>with your install kit.', 315, 251, 277, 23, 30,
         '#FFFFFF', limit=60)
    para('<b>Sealed cooling circuit</b><br/>R-600a (isobutane), flammable refrigerant.<br/>Under 1.5 oz (40 g). Do not open, puncture or heat.',
         52, 357, 540, 10.5, 15, ICE, limit=60)
    text('homesodamachine.com', 52, 438, 15, 'Semibold', '#FFFFFF')
    text('Guides: /drawings', 455, 442, 10, 'Regular', ICE)
    c.linkURL('https://homesodamachine.com', (52, H-459, 301, H-435), relative=1)
    c.linkURL('https://homesodamachine.com/drawings', (450, H-458, 600, H-435), relative=1)
    c.bookmarkPage(f'page-{page_no}')
    c.addOutlineEntry('Back cover', f'page-{page_no}', 0, False)
    c.showPage()


back_cover()
c.save()
assert page_no == 34
if contours.pending:
    contours.render()
    subprocess.run([sys.executable, str(Path(__file__).resolve())], cwd=ROOT, check=True)
    sys.exit(0)
OUT.mkdir(parents=True, exist_ok=True)
write_editions(buffer.getvalue(), PDF, PRESS_DIR, ROOT/'output/pdf', OUT)
subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-scale-to', '1200',
                '-singlefile', '-png', str(PDF), str(OUT/'cover')], check=True)
im = Image.open(OUT/'cover.png')
im.thumbnail((1200, 1200))
im.save(DIR/'install-guide.cover.png')
(DIR/'install-guide.pdf.json').write_text(json.dumps(dict(
    title='Home Soda Machine install guide',
    subtitle='Owner install guide - seven steps in detail - 32 interior pages, 9 x 7 in landscape',
    pages=34, interior_pages=32, cover='install-guide.cover.png', cover_size=list(im.size)
), indent=2)+'\n')
(OUT/'layout-checks.json').write_text(json.dumps(checks, indent=2)+'\n')
(OUT/'image-checks.json').write_text(json.dumps(image_checks, indent=2)+'\n')
(OUT/'page-plan.json').write_text(json.dumps(dict(interior_pages=32, titles=titles), indent=2)+'\n')
print(f'{PDF}: 32 interior pages + covers, {PDF.stat().st_size//1024} KB')
make_order_bundle(PRESS_DIR, ROOT/'output/pdf')
