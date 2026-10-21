"""Draw the faucet shop book and its rear-display wiring plate by hand.

This is a manual document tool. It has no CAD imports or build-system target.
The PDF and SVG share one wiring illustration; the source receipt records the
procedures and firmware reviewed for this edition.
"""
from __future__ import annotations

import html
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/assembly-guides"))
from common import *

GUIDE = ROOT / "hardware/faucet-assembly-guide"
PDF = ROOT / "output/pdf/faucet-assembly-guide.pdf"
SITE = "https://github.com/derekbreden/homesodamachine/blob/main/"
DOCS = "https://homesodamachine.com/read/"
VENDOR = "https://docs.waveshare.com/ESP32-S3-Touch-LCD-1.47"
SCHEMATIC = "https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-1.47/ESP32-S3-Touch-LCD-1.47-Schematic.pdf"
INTERFACE = "https://docs.waveshare.com/assets/images/ESP32-S3-Touch-LCD-1.47-details-inter-f60fcf8e6f1405b29f83509d1d1246e7.webp"
JACK = "https://www.riteav.com/products/riteav-rj11-phone-black-punchdown-type-keystone-jack-10-pack"
USOC = "https://leviton.com/content/dam/leviton/network-solutions/product_documents/instruction_sheet/Leviton-IST-41106-41108-Voice-Grade-Jacks.pdf"
MODULAR_VIEW = "https://www.apo.nmsu.edu/mainpage/sdss/rj11basics/"
FU = "hardware/assembly/faucet-and-umbilical.md"
SHELL = "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md"
OBSERVATIONS = "hardware/printed-parts/faucet/lever-replica/assembly-observations.json"
INSERTION = "hardware/printed-parts/fixtures/tube-insertion/README.md"
INSERTION_PDF = "https://homesodamachine.com/read/tube-insertion-guide/tube-insertion-guide.pdf"
N = 18
GREEN = "#217E57"
BRASS = "#C89542"
PAD = "#EBC77D"
PCB = "#30353D"
WIRE = "#272A30"
# Assembly assignment: C1 is the deliberately indexed edge of the black 28 AWG
# ribbon. RJ11 numbers retain all six positions; only 2-5 carry contacts.
# J3 physical numbers include the 180-degree wafer rotation in parts.tsx.
SIG6 = [
    {"wire":"C1", "pad":"VBUS", "P1":1, "RJ11":2, "IDC":"white/orange", "J3_pin":3, "J3":"V5", "function":"+5 V input"},
    {"wire":"C2", "pad":"GND", "P1":3, "RJ11":3, "IDC":"blue", "J3_pin":4, "J3":"GND", "function":"0 V return"},
    {"wire":"C3", "pad":"TXD", "P1":5, "GPIO":43, "RJ11":4, "IDC":"white/blue", "J3_pin":2, "J3":"IO35 RX", "function":"GPIO43, display TX"},
    {"wire":"C4", "pad":"RXD", "P1":7, "GPIO":44, "RJ11":5, "IDC":"orange", "J3_pin":1, "J3":"IO33 TX", "function":"GPIO44, display RX"},
]
SOURCES = [
    FU, SHELL, OBSERVATIONS,
    "hardware/printed-parts/faucet/faucet-shell/faucet_shell.py",
    "hardware/faucet-layout/faucet_assembly.py",
    "hardware/reference/touch-flo-faucet/display-reference/README.md",
    "hardware/wiring/ac-wiring-schedule.md",
    "hardware/assembly/wiring.md",
    "hardware/assembly/cable-assemblies.md",
    "hardware/pcb/pcba/pcba.tsx",
    "hardware/pcb/pcba/parts.tsx",
    "firmware/src_faucet/base_link.cpp",
    "firmware/src_faucet/README.md",
    "firmware/src_appliance/pins.h",
    "hardware/printed-parts/faucet/README.md",
    "hardware/printed-parts/faucet/tpu-o-ring/README.md",
    "hardware/printed-parts/faucet/tpu-o-ring/print-log.md",
    "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json",
    "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
    "tools/faucet-assembly-guide/faucet_art.py",
    "hardware/faucet-assembly-guide/art/accepted-lever.png",
    "hardware/faucet-assembly-guide/art/sleeve-on-tube.png",
    "hardware/faucet-assembly-guide/art/sleeved-tube-to-donor.png",
    "hardware/faucet-assembly-guide/art/shell-base-section.png",
    "hardware/faucet-assembly-guide/art/shared-tip-section.png",
    "hardware/printed-parts/faucet/vent-qualification/README.md",
    "hardware/mechanical-qualification/README.md",
    "hardware/install-guide/assets/reference/drain-mount-drop.png",
]


def figure(token):
    match = re.search(r"\[([\d.]+)(?:[^\]]*)\]\(" + re.escape(token) + r"\)",
                      (ROOT / FU).read_text())
    if not match:
        raise ValueError(f"Review faucet procedure figure: {token}")
    return match.group(1)


class SvgArt:
    """The same top-left drawing primitives as the PDF illustration."""

    def __init__(self):
        self.parts = []

    def shape(self, points, fill=None, stroke=INK, width=1.5, close=True):
        coords = " ".join(f"{x:g},{y:g}" for x, y in points)
        tag = "polygon" if close else "polyline"
        self.parts.append(f'<{tag} points="{coords}" fill="{fill or "none"}" '
                          f'stroke="{stroke or "none"}" stroke-width="{width:g}"/>')

    def line(self, x1, y1, x2, y2, fill=INK, width=1.4, dash=None):
        d = f' stroke-dasharray="{" ".join(map(str, dash))}"' if dash else ""
        self.parts.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
                          f'stroke="{fill}" stroke-width="{width:g}"{d}/>')

    def rect(self, x, y, width, height, fill=STEEL, stroke=INK):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" '
                          f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="1.5"/>')

    def ellipse(self, x, y, width, height, fill=STEEL, stroke=INK, lw=1.5):
        self.parts.append(f'<ellipse cx="{x + width/2:g}" cy="{y + height/2:g}" '
                          f'rx="{width/2:g}" ry="{height/2:g}" fill="{fill or "none"}" '
                          f'stroke="{stroke or "none"}" stroke-width="{lw:g}"/>')

    def label(self, value, x, y, size=10, fill=INK, font="PlexSemi", align="left"):
        anchor = {"left": "start", "center": "middle", "right": "end"}[align]
        weight = "400" if font == "Plex" else "700" if font == "PlexBold" else "600"
        self.parts.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" '
                          f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">'
                          f'{html.escape(value)}</text>')

    def arrow(self, x1, y1, x2, y2, fill=BLUE, width=2, head=6):
        self.line(x1, y1, x2, y2, fill, width)
        angle = math.atan2(y2-y1, x2-x1)
        self.shape([(x2, y2),
                    (x2-head*math.cos(angle-.5), y2-head*math.sin(angle-.5)),
                    (x2-head*math.cos(angle+.5), y2-head*math.sin(angle+.5))], fill, None)


def board(a, x, y, scale=1, connected=False):
    """Rear component view, USB-C at top. P1 odds left, evens right."""
    def rect(xx, yy, w, h, fill=STEEL, stroke=INK):
        a.rect(x+xx*scale, y+yy*scale, w*scale, h*scale, fill, stroke)
    def ellipse(xx, yy, w, h, fill=STEEL, stroke=INK, lw=1.5):
        a.ellipse(x+xx*scale, y+yy*scale, w*scale, h*scale, fill, stroke, lw*scale)
    def label(value, xx, yy, size=9, fill=PAPER, align="left"):
        a.label(value, x+xx*scale, y+yy*scale, size*scale, fill, align=align)
    # Rounded housing outline, then the PCB and its four brass mounting feet.
    a.shape([(x+16*scale,y),(x+124*scale,y),(x+140*scale,y+18*scale),
             (x+140*scale,y+250*scale),(x+124*scale,y+268*scale),
             (x+16*scale,y+268*scale),(x,y+250*scale),(x,y+18*scale)], PCB, PCB)
    for xx, yy in [(13,12),(112,12),(13,238),(112,238)]:
        ellipse(xx,yy,15,15,BRASS,BRASS)
        ellipse(xx+4,yy+4,7,7,PCB,PCB)
    rect(45,-4,50,48,STEEL,"#A5ADB6")
    rect(50,1,40,29,"#F0F1F3","#A5ADB6")
    rect(53,33,34,6,PCB,PCB)
    label("USB-C",70,22,9,INK,"center")
    rect(8,31,15,23,STEEL)
    rect(117,31,15,23,STEEL)
    rect(44,68,52,38,STEEL,"#A5ADB6")
    label("microSD",70,90,8,INK,"center")
    rect(41,119,40,24,INK,INK)
    rect(36,158,68,55,INK,INK)
    label("ESP32-S3",70,181,9,PAPER,"center")
    label("R8",70,196,10,PAPER,"center")
    rect(57,218,28,8,STEEL,STEEL)
    rect(45,248,50,11,STEEL,STEEL)
    for xx in [43,94]:
        for yy in [112,126,140,153,213,230]:
            rect(xx,yy,5,7,STEEL,STEEL)
    left_names = ["VBUS","GND","TXD","RXD","RST","1","2","3","4","5","6"]
    right_names = ["VBAT","GND","GND","3V3","SCL","SDA","11","10","9","8","7"]
    for i in range(11):
        yy=76+i*14.6
        for xx,names in [(19,left_names),(121,right_names)]:
            active = connected and xx == 19 and i < 4
            ellipse(xx-4,yy-4,8,8,PAD if active else "#59606B",PAD if active else "#BEC4CC",1)
            ellipse(xx-2,yy-2,4,4,PCB,PCB,.5)
            if xx == 19:
                label(names[i],27,yy+2.4,4.8,"#DCE2EB")
            else:
                label(names[i],113,yy+2.4,4.8,"#DCE2EB","right")


def installed_orientation_art(a, y=0):
    """Side section: USB at the outlet, opposite end up the gooseneck."""
    a.rect(8,y,504,100,ICE,RULE)
    a.label("INSTALLED: USB-C TOWARD THE DISPENSE FACE",20,y+18,11,BLUE,font="PlexBold")
    # Level tip at left; the neck curls beneath the display toward the stem.
    # Both outlines follow the same circular bend, with a square section cut.
    angles = [i*.7/14 for i in range(15)]
    outer = [(240+114*math.sin(t),y+168-114*math.cos(t)) for t in angles]
    inner = [(240+96*math.sin(t),y+168-96*math.cos(t)) for t in reversed(angles)]
    a.shape([(180,y+54),*outer,*inner,(180,y+72)],STEEL)
    a.line(180,y+54,180,y+72,BLUE,3)
    # Glass, PCB and USB socket all have their outlet end at left.
    a.rect(186,y+33,90,4,"#B7DAF1",BLUE)
    a.rect(186,y+37,90,12,PCB,PCB)
    a.rect(178,y+41,14,8,BRASS,INK)
    a.line(179,y+44,185,y+44,INK,2)
    a.label("display",234,y+29,9,MUTED,align="center")
    a.label("USB-C",24,y+45,12,ORANGE,font="PlexBold")
    a.arrow(112,y+43,177,y+45,ORANGE,1.8,5)
    a.label("dispense face",24,y+73,11,BLUE)
    a.arrow(135,y+68,177,y+65,BLUE,1.5,5)
    a.label("gooseneck",378,y+58,12,BLUE)
    a.label("toward faucet base",378,y+76,9,MUTED,font="Plex")
    a.arrow(370,y+62,309,y+84,BLUE,1.5,5)
    a.label("Side section; tip shown level",24,y+94,8.5,MUTED,font="Plex")


def wiring_art(a):
    a.label("REAR / COMPONENT SIDE",14,24,12,BLUE)
    a.label("Glass faces away from you",14,43,11,MUTED,font="Plex")
    board(a,345,20,.8,True)
    for i,row in enumerate(SIG6):
        y=73+i*43
        a.label(f'{row["wire"]}  {row["pad"]}',14,y,17,INK,font="PlexBold")
        a.label(f'P1-{row["P1"]}  ·  {row["function"]}',14,y+16,10.7,MUTED,font="Plex")
        # Actual four black conductors, splayed only at the dry PCB end.
        xx=267+i*16
        yy=129+i*15
        pady=80.8+i*11.68
        a.shape([(xx,230),(xx,yy),(360.2,pady)],None,WIRE,4,False)
        a.ellipse(357.2,pady-3,6,6,PAD,WIRE,1)
        a.label(row["wire"],xx,248,10,INK,align="center")
    a.line(267,211,267,225,PAPER,2)
    a.label("All four wires are BLACK",14,235,11,INK)
    a.label("Add a white C1 mark at both ends",14,252,10.2,BLUE)
    a.arrow(226,246,263,222,BLUE,1.2,4)
    a.label("USB-C AT TOP",411,252,10.5,BLUE,align="center")
    installed_orientation_art(a,266)


def write_wiring_svg():
    a=SvgArt()
    wiring_art(a)
    (GUIDE / "display-wiring.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="750" viewBox="0 0 520 375" '
        'role="img" aria-labelledby="title desc">\n'
        '<title id="title">Faucet display wiring, rear view with USB-C at top</title>\n'
        '<desc id="desc">Waveshare ESP32-S3-Touch-LCD-1.47. The top four left pads are '
        'VBUS, GND, TXD, RXD: P1 pins 1, 3, 5, 7. All four ribbon wires are black. '
        'Add a white mark to edge C1 at both ends; count C1-C4 across the ribbon from that edge. '
        'C1 VBUS goes through RJ11 pin 2 to J3 pin 3 V5; C2 GND through RJ11 pin 3 to J3 pin 4 GND; '
        'C3 TXD through RJ11 pin 4 to J3 pin 2 IO35 RX; C4 RXD through RJ11 pin 5 to J3 pin 1 IO33 TX. '
        'Signal levels are 3.3 V TTL; power is 5 V. This is a rear view, not mirrored. '
        'In the installed faucet, USB-C points toward the dispense face; the opposite end '
        'points up the gooseneck. The inset shows this in a side section.</desc>\n'
        '<rect width="520" height="375" fill="#FFFFFF"/>\n'
        '<g font-family="IBM Plex Sans, Arial, sans-serif" stroke-linejoin="round" stroke-linecap="round">\n'
        + "\n".join(a.parts) + '\n</g>\n</svg>\n')


def note(c, title, body, y=680):
    box(c,32,y,548,65,ICE,radius=7)
    text(c,title,46,y+18,11,"PlexBold",BLUE)
    paragraph(c,body,46,y+25,518,10.6,13.2,max_height=40)


def steps(c, items, y=515):
    for i,item in enumerate(items,1):
        box(c,33,y,21,21,BLUE,radius=5)
        text(c,str(i),43.5,y+15,11.5,"PlexBold",PAPER,"center")
        height=paragraph(c,item,65,y+1,508,11.3,14.2)
        y+=max(height,21)+10
    if y>674:
        raise ValueError(f"Action band too tall: {y}")


def start(c,n,title,lede):
    begin_page(c)
    c.bookmarkPage(f"page{n}")
    c.addOutlineEntry(f"{n:02d}  {title.replace(chr(10),' ')}",f"page{n}",0)
    header(c,n,title,lede,N,"FAUCET ASSEMBLY")


def page(c,n,title,lede,artist,caption,items,check,source=FU):
    start(c,n,title,lede)
    panel(c,32,161,548,314)
    with Art(c,48,174) as a:
        artist(a)
    paragraph(c,caption,35,483,541,10.4,12.6,MUTED,max_height=28)
    steps(c,items)
    note(c,"CHECK BEFORE CONTINUING",check)
    footer(c,n,source,SITE+source)
    end_page(c)


def path(a,points,fill=INK,width=8):
    a.shape(points,None,fill,width,False)


def screw(a,x,y,fill=ORANGE):
    a.rect(x-8,y,16,11,fill)
    a.rect(x-3,y+11,6,27,fill)
    for yy in range(int(y+14),int(y+36),4):
        a.line(x-3,yy,x+3,yy+2,PAPER,.6)


def insert(a,x,y):
    a.rect(x-10,y,20,24,BRASS)
    for yy in range(int(y+4),int(y+24),5):
        a.line(x-9,yy,x+9,yy-3,INK,.7)
    a.ellipse(x-10,y-4,20,8,BRASS)
    a.ellipse(x-5,y-2,10,4,PCB)


def bundle(a,x,y,length=220,drain=True):
    for i,ink in enumerate([INK,"#B4BFCC",INK,BLUE]):
        a.line(x+i*17,y,x+i*17,y+length,ink,9 if i<3 else 7)
    if drain:
        a.line(x+23,y,x+23,y+length,"#FFFFFF",4)
        a.line(x+21,y,x+21,y+length,MUTED,.7)
        a.line(x+25,y,x+25,y+length,MUTED,.7)


def prep_art(a):
    a.label("SHELL FOOT / UNDERSIDE",126,20,11,BLUE,align="center")
    a.ellipse(26,49,202,173,STEEL)
    a.ellipse(86,109,78,60,PAPER)
    pilots=[(59,117),(196,117),(128,197)]
    for x,y in pilots:
        a.ellipse(x-9,y-9,18,18,PAPER)
    insert(a,196,72)
    a.arrow(196,99,196,107)
    a.label("3 × short M3 inserts",126,255,13,BLUE,align="center")
    a.arrow(251,132,280,132)
    a.rect(305,141,180,83,STEEL)
    a.shape([(376,141),(376,175),(416,175),(416,141)],PAPER)
    insert(a,396,149)
    a.rect(386,48,20,54,BLUE)
    a.shape([(387,102),(405,102),(402,147),(390,147)],STEEL)
    a.arrow(430,90,430,142)
    a.label("square to the pilot",396,251,12,BLUE,align="center")


def cad_image(a, name, x, y, width, height):
    a.c.saveState()
    a.c.scale(1, -1)
    a.c.drawImage(str(GUIDE / "art" / (name + ".png")), x, -y-height,
                  width=width, height=height, preserveAspectRatio=True,
                  anchor="c", mask="auto")
    a.c.restoreState()


def donor_art(a):
    a.label("ACCEPTED PRINTED LEVER",111,23,11,BLUE,align="center")
    cad_image(a,"accepted-lever",6,41,207,225)
    a.label("Attachment channel / underside",112,285,9.5,MUTED,align="center")
    for j,(title,y) in enumerate([("1  LOWER WHILE AFT",35),("2  SLIDE FORWARD",120),("3  DOWN AT REST",205)]):
        a.label(title,237,y,11,BLUE)
        a.rect(374,y+20,74,45,STEEL)
        a.ellipse(390,y+20,25,12,BRASS)
        if j==0:
            a.shape([(311,y+3),(432,y+3),(432,y+13),(314,y+13)],ORANGE)
            a.arrow(414,y-2,414,y+18,BLUE,1.5,4)
        else:
            a.shape([(273,y+27),(413,y+27),(413,y+36),(273,y+36)],ORANGE)
            if j==1:
                a.arrow(450,y+9,358,y+9,BLUE,1.5,4)
            else:
                a.label("unpressed",460,y+51,10,MUTED,align="center")
    a.label("BARE DONOR OUTSIDE SHELL",367,290,10.5,BLUE,align="center")


def thimble_art(a):
    a.label("FIT OUTSIDE THE DONOR",121,23,11,BLUE,align="center")
    cad_image(a,"sleeve-on-tube",18,44,196,226)
    a.arrow(228,86,228,175,BLUE,1.5,5)
    a.label("open mouth",271,65,11,BLUE)
    a.rect(318,93,71,140,STEEL)
    a.rect(338,93,31,140,PAPER,PAPER)
    a.shape([(310,155),(310,239),(397,239),(397,155)],None,ORANGE,8,False)
    a.rect(310,233,87,12,ORANGE)
    a.rect(338,233,31,12,PAPER,PAPER)
    a.arrow(300,78,310,153,BLUE,1.2,4)
    a.line(301,155,310,155,BLUE,1.5)
    a.label("even wall",418,159,10.5,BLUE)
    a.line(399,181,416,166,BLUE,1.2)
    a.label("tube end on cap",352,270,12,BLUE,align="center")
    a.arrow(352,259,352,235,BLUE,1.4,4)
    a.label("CAP FIRST INTO METAL NEXT",352,290,10,ORANGE,align="center")


def sleeve_insert_art(a):
    a.label("SLEEVE + TUBE MOVE TOGETHER",123,23,10.5,BLUE,align="center")
    cad_image(a,"sleeved-tube-to-donor",13,35,220,258)
    a.arrow(240,77,240,149,BLUE,1.8,5)
    a.rect(372,155,72,75,STEEL)
    a.rect(400,93,17,88,INK)
    a.shape([(398,130),(398,168),(420,168),(420,130)],None,ORANGE,4,False)
    a.line(289,153,399,153,ORANGE,9)
    a.rect(400,230,13,43,STEEL)
    a.label("lever attached",363,49,13,BLUE,align="center")
    a.label("DOWN AT REST",363,74,14,BLUE,align="center")
    a.label("not pressed",298,177,11,MUTED)
    a.arrow(451,101,451,138,BLUE,1.6,5)
    a.label("bare metal port",359,291,11,BLUE,align="center")


def shell_insertion_art(a):
    a.label("CURRENT BASE / SECTION",111,23,11,BLUE,align="center")
    cad_image(a,"shell-base-section",4,37,217,250)
    a.arrow(224,272,224,216,BLUE,1.6,5)
    for j,(title,y) in enumerate([("1  FLIP THE LEVER UP",41),("2  INSERT FROM FOOT",130),("3  SNAP TO REST",219)]):
        a.label(title,251,y,10.7,BLUE)
        if j<2:
            a.shape([(353,y+25),(353,y+67),(451,y+67),(451,y+25)],None,INK,4,False)
            a.rect(383,y+42,43,43,STEEL)
            a.line(383,y+48,332,y+2,ORANGE,8)
            if j==1:
                a.arrow(441,y+85,441,y+49,BLUE,1.5,4)
                a.arrow(320,y+19,344,y+19,BLUE,1.5,4)
        else:
            a.rect(353,y+21,98,50,INK)
            a.rect(383,y+25,43,40,STEEL)
            a.line(282,y+28,385,y+28,ORANGE,8)
            a.label("unpressed",297,y+62,10,MUTED)


def route_tip_art(a):
    a.label("CURRENT SHARED TIP / SECTION",126,23,10.5,BLUE,align="center")
    cad_image(a,"shared-tip-section",2,39,234,215)
    a.label("Smooth common passage",125,280,11,BLUE,align="center")
    a.rect(280,113,220,80,STEEL)
    a.rect(282,133,218,39,PAPER,PAPER)
    for y,ink in [(140,INK),(151,BLUE),(163,INK)]:
        a.line(260,y,500,y,ink,5)
    a.line(260,123,468,123,WIRE,4)
    a.line(260,178,445,178,MUTED,4)
    a.line(459,180,459,192,BLUE,5)
    a.label("3 drink ends flush",407,68,12,BLUE,align="center")
    a.arrow(498,81,498,130,BLUE,1.4,4)
    a.label("D ends inside",324,225,11,BLUE,align="center")
    a.arrow(350,209,442,179,BLUE,1.4,4)
    a.label("Ø4 fault-drip hole",410,267,11,BLUE,align="center")
    a.arrow(428,250,459,193,BLUE,1.4,4)
    a.line(407,238,487,238,PAPER,3)


def closure_art(a):
    a.shape([(49,201),(50,139),(70,84),(114,48),(167,38)],None,STEEL,39,False)
    a.shape([(178,41),(222,56),(248,88)],None,ORANGE,39,False)
    a.arrow(184,10,216,24,BLUE)
    a.label("curved lap",145,128,12,BLUE,align="center")
    a.label("rotate until seam seats",143,249,11,BLUE,align="center")
    a.ellipse(329,98,146,51,STEEL)
    a.ellipse(345,111,22,13,PAPER)
    a.ellipse(438,111,22,13,PAPER)
    a.ellipse(390,130,22,11,PAPER)
    for x,y in [(356,173),(449,173),(401,211)]:
        screw(a,x,y)
        a.arrow(x,y-9,x,y-29,BLUE)
    a.label("3 × M3 × 8 mm",402,75,14,BLUE,align="center")
    a.label("2.5 mm hex key / from below",399,276,11,BLUE,align="center")


def solder_art(a):
    a.label("AFTER LEADS PASS THROUGH THE NECK",14,20,11,BLUE)
    a.rect(163,115,119,20,STEEL)
    a.ellipse(194,118,16,14,BRASS)
    a.line(20,211,170,211,WIRE,5)
    a.line(170,211,202,131,WIRE,5)
    a.line(199,137,202,131,COPPER,3)
    a.shape([(362,57),(422,82),(397,123),(337,91)],BLUE)
    a.shape([(337,91),(354,113),(211,126),(205,118)],STEEL)
    a.arrow(312,156,226,137,ORANGE)
    a.label("fine iron tip",390,150,11,BLUE,align="center")
    a.label("insulation close to pad",115,251,12,BLUE,align="center")
    a.label("solder at dry PCB only",376,251,12,ORANGE,align="center")


def display_art(a):
    installed_orientation_art(a)
    for i,(x,label) in enumerate([(12,"1  DISPLAY INTO COVER"),(185,"2  SLIDE FROM OUTLET"),(359,"3  LOWER TO SEAT")]):
        a.rect(x,114,155,179,PAPER,RULE)
        a.label(label,x+77,135,8.8,BLUE,align="center")
        a.shape([(x+28,240),(x+130,240),(x+130,261),(x+28,261)],STEEL)
        for xx in [x+39,x+112]:
            a.rect(xx,229,9,11,STEEL)
        if i==0:
            a.shape([(x+39,170),(x+39,153),(x+116,153),(x+116,170)],None,ORANGE,9,False)
            a.rect(x+42,194,71,16,PCB)
            a.rect(x+34,198,12,8,BRASS,INK)
            a.arrow(x+76,185,x+76,173,BLUE)
            a.arrow(x+45,170,x+28,170,BLUE,1.5)
            a.arrow(x+110,170,x+130,170,BLUE,1.5)
            a.label("spread plastic wings",x+77,281,9,MUTED,align="center")
        else:
            yy=169 if i==1 else 208
            a.rect(x+35,yy,91,17,PCB)
            a.rect(x+27,yy+4,12,8,BRASS,INK)
            a.shape([(x+28,yy+34),(x+28,yy-4),(x+134,yy-4),(x+134,yy+34)],None,ORANGE,7,False)
            for xx in [x+39,x+112]:
                a.rect(xx,yy+17,9,10,BRASS)
            if i==1:
                a.arrow(x+12,yy-25,x+106,yy-25,BLUE)
                a.dim(x+147,yy+27,x+147,240)
                a.label("9.5 mm lift",x+77,281,11,BLUE,align="center")
            else:
                a.arrow(x+77,161,x+77,199,BLUE)
                a.line(x+28,240,x+41,240,BLUE,3)
                a.line(x+121,240,x+134,240,BLUE,3)
                a.label("feet + both lips seated",x+77,281,9,MUTED,align="center")


def mount_art(a):
    a.label("FACTORY ORDER / SHANK BELOW",145,22,11,BLUE,align="center")
    a.rect(68,49,164,39,STEEL)
    a.rect(130,86,38,160,BRASS)
    for yy in range(98,246,10):
        a.line(132,yy,166,yy+5,INK,.7)
    a.ellipse(63,125,174,26,ORANGE)
    a.ellipse(126,131,47,13,PAPER)
    a.ellipse(109,191,80,16,STEEL)
    a.ellipse(133,194,32,9,PAPER)
    a.shape([(112,237),(128,227),(172,227),(189,237),(172,254),(129,254)],STEEL)
    a.arrow(51,151,51,93,BLUE)
    a.arrow(261,245,261,151,BLUE)
    a.label("1  gasket",293,142,14,ORANGE)
    a.label("2  retained washer",293,199,14,BLUE)
    a.label("3  retained nut",293,246,14,BLUE)
    a.label("blue tube still OFF",144,281,13,BLUE,align="center")


def supply_art(a):
    a.label("CONTINUOUS BLACK FLAVORS",102,21,10.5,BLUE,align="center")
    for x,name in [(58,"A"),(145,"B")]:
        a.line(x,45,x,248,INK,6)
        a.label(name,x,151,13,BLUE,align="center")
    a.label("4 mm OD / both finishes",102,274,10,MUTED,align="center")
    a.label("BLUE SUPPLY / BOTH FINISHES",371,21,11,BLUE,align="center")
    a.rect(343,40,58,51,BRASS)
    a.rect(350,104,44,18,BRASS)
    a.shape([(346,149),(353,138),(393,138),(400,149),(393,164),(353,164)],BRASS)
    a.rect(365,218,16,39,BLUE)
    a.rect(369,190,8,54,BRASS)
    a.arrow(373,181,373,171,BLUE)
    a.arrow(373,128,373,95,BLUE)
    a.label("stiffener inside tube",372,279,12,BLUE,align="center")
    a.label("factory ferrule + nut",458,134,10,MUTED,align="center")


def plug_art(a):
    a.label("PLUG / GOLD CONTACTS FACE YOU",5,18,10.2,BLUE)
    a.label("Nose up · cable down · latch behind",5,36,9.8,MUTED,font="Plex")
    a.rect(31,65,141,143,STEEL)
    a.rect(42,87,119,112,PAPER)
    # Latch is on the far side, dashed through the transparent body.
    a.shape([(82,173),(82,211),(121,211),(121,173)],None,MUTED,1,False)
    a.label("PIN",11,81,8,BLUE)
    for pin in range(1,7):
        xx=53+(pin-1)*18
        a.label(str(pin),xx,81,12,BLUE,align="center")
        a.rect(xx-4,94,8,25,BRASS if 2<=pin<=5 else STEEL,
               INK if 2<=pin<=5 else RULE)
    for i,row in enumerate(SIG6):
        xx=71+i*18
        a.line(xx,119,xx,252,WIRE,8)
        a.label(row["wire"],xx,271,10.5,INK,align="center")
    a.line(71,226,71,244,PAPER,2.5)
    a.line(60,166,136,166,ORANGE,10)
    a.arrow(186,166,145,166,ORANGE,1.4,4)
    a.label("grip",190,160,9.5,ORANGE)
    a.label("jacket",190,175,9.5,ORANGE)
    a.label("C1 = white edge mark",102,293,10.5,BLUE,align="center")
    a.label("1 and 6: empty positions",102,311,10,MUTED,align="center")

    a.label("JACK / PUNCHDOWN SIDE UP",243,18,10.2,BLUE)
    a.label("Plug opening toward bottom of picture",243,36,9.8,MUTED,font="Plex")
    # RiteAV CAT3 USOC block: rows 3/4 at rear, 2/5 middle, 1/6
    # nearest the port. Numbers are contacts, not ribbon conductor numbers.
    a.rect(296,62,156,178,PCB)
    a.rect(319,63,111,145,STEEL)
    slots=[(3,328,85,"blue","C2 / GND",False),
           (2,328,130,"orange","C1 / V5",True),
           (1,328,175,"green","open",True),
           (4,421,85,"blue","C3 / IO35",True),
           (5,421,130,"orange","C4 / IO33",False),
           (6,421,175,"green","open",False)]
    shades={"blue":"#1777BE","orange":"#E49127","green":"#258D62"}
    for pin,xx,yy,shade,label,striped in slots:
        left=xx==328
        # These colored dots reproduce the jack's printed USOC legend.
        chipx=300 if left else 441
        a.ellipse(chipx-7,yy+8,14,14,PAPER if striped else shades[shade],shades[shade],1.5)
        if striped:
            a.line(chipx-4,yy+19,chipx+4,yy+11,shades[shade],2)
        a.rect(xx-10,yy-12,20,24,PAPER)
        a.label(str(pin),xx,yy+4,12,INK,align="center")
        if pin not in [1,6]:
            outer=268 if left else 477
            inner=xx-13 if left else xx+13
            a.line(outer,yy,inner,yy,WIRE,4)
            a.label(label,278 if left else 465,yy-15,10,INK,
                    align="right" if left else "left")
        else:
            a.label(label,278 if left else 465,yy+4,9.5,MUTED,
                    align="right" if left else "left")
    a.rect(303,208,142,42,PCB)
    a.rect(329,219,90,21,"#11151B")
    a.rect(360,231,28,13,"#11151B","#11151B")
    a.label("FRONT / PLUG OPENING",374,270,10.5,BLUE,align="center")
    a.label("Colors are labels on the jack.",374,293,10.2,MUTED,align="center")
    a.label("The connected wires are BLACK.",374,311,10.2,INK,align="center")


def sig6_table(c, y):
    columns=[(37,"WIRE"),(92,"DISPLAY PAD"),(230,"RJ11 PIN"),
             (300,"JACK IDC LABEL"),(451,"J3 PIN / NET")]
    for x,label in columns:
        text(c,label,x,y,9.1,"PlexBold",BLUE)
    for i,row in enumerate(SIG6):
        yy=y+22+i*27
        box(c,32,yy-18,548,25,ICE if i%2==0 else PAPER)
        values=[row["wire"],f'{row["pad"]} / P1-{row["P1"]}',
                str(row["RJ11"]),row["IDC"],f'{row["J3_pin"]} / {row["J3"]}']
        for (x,_),value in zip(columns,values):
            text(c,value,x,yy,10.6,"PlexSemi")


def plug_page(c):
    start(c,15,"Wire the RJ11 plug and jack",
          "Use the same C1-C4 identities as page 2. Plug pins 2-5 carry the four wires; positions 1 and 6 stay empty.")
    panel(c,32,148,548,329)
    with Art(c,44,155) as a:
        plug_art(a)
    sig6_table(c,493)
    paragraph(c,"At the plug, C1-C4 run left to right in the view above. At the jack, punch J3 pin 3/V5 into slot 2, pin 4/GND into slot 3, pin 2/IO35 into slot 4 and pin 1/IO33 into slot 5.",35,616,538,11,14,max_height=42)
    note(c,"MAKE THESE TERMINATIONS WITH J3 AND USB UNPLUGGED",
         "Crimp a 3-prong 6P4C plug on the 28 AWG ribbon. Shim the final 15 mm so the bar grips the jacket. Punch the 22 AWG J3 leads into the numbered slots without stripping their insulation; trim outward and refit the dust cover.")
    footer(c,15,"RiteAV CAT3 USOC jack | Leviton 6-contact USOC labels | main-board J3",JACK)
    end_page(c)


def write_connector_svg():
    a=SvgArt()
    plug_art(a)
    (GUIDE / "sig6-connector-wiring.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="650" viewBox="0 0 520 325" '
        'role="img" aria-labelledby="title desc">\n'
        '<title id="title">SIG-6 RJ11 plug and RiteAV punchdown jack wiring</title>\n'
        '<desc id="desc">Plug gold contacts toward viewer, nose up, cable down, latch behind. '
        'C1-C4 occupy pins 2-5 left to right. All wires are black; C1 has an added white edge mark. '
        'Jack punchdown side up, front opening toward bottom: rear row 3 and 4, middle 2 and 5, '
        'front 1 and 6 unused. J3 pin 3 V5 goes to jack 2 white/orange; J3 pin 4 GND to jack 3 blue; '
        'J3 pin 2 IO35 RX to jack 4 white/blue; J3 pin 1 IO33 TX to jack 5 orange. '
        'Colored symbols reproduce labels on the jack, not wire insulation.</desc>\n'
        '<rect width="520" height="325" fill="#FFFFFF"/>\n'
        '<g font-family="IBM Plex Sans, Arial, sans-serif" stroke-linejoin="round" stroke-linecap="round">\n'
        + "\n".join(a.parts) + '\n</g>\n</svg>\n')


def sleeve_art(a):
    a.label("FOAM ON BLUE ONLY",132,20,11,BLUE,align="center")
    a.ellipse(49,50,163,163,STEEL)
    a.ellipse(64,65,133,133,"#BCC3CE")
    a.ellipse(108,110,45,45,BLUE)
    a.ellipse(119,121,23,23,PAPER)
    for x,y,diam,ink in [(205,72,20,INK),(211,105,20,INK),(58,128,20,PAPER)]:
        a.ellipse(x,y,diam,diam,ink)
        a.ellipse(x+diam*.27,y+diam*.27,diam*.46,diam*.46,PAPER)
    a.rect(204,158,8,44,BLUE)
    a.ellipse(31,31,227,198,None,ORANGE,3)
    a.label("common PET braid",134,252,12,ORANGE,align="center")
    a.label("D opposite the flavors",134,274,10,MUTED,align="center")
    for i in range(2):
        y=44+i*92
        a.rect(332,y,127,89,"#D8DCE4")
        for yy in range(y+6,y+82,12):
            a.line(332,yy,459,yy+10,ORANGE,1)
            a.line(332,yy+10,459,yy,ORANGE,1)
    a.line(335,136,457,136,BLUE,3)
    a.label("butt adjoining segments",398,252,12,BLUE,align="center")
    a.label("fit braid before cutting",398,274,10,MUTED,align="center")


def final_art(a):
    a.label("IDENTIFIED WALL TAILS",14,20,11,BLUE)
    for i,(name,ink) in enumerate([("SODA",BLUE),("FLAVOR",INK),("FLAVOR",INK),("OVER",MUTED)]):
        x=43+i*104
        a.line(x,42,x,214,ink,9 if i<3 else 6)
        a.rect(x-31,109,62,73,ink)
        a.label(name,x,150,10,PAPER,align="center")
        a.line(x-12,214,x+12,214,ORANGE,2)
    a.label("bare, square ends below collars",230,241,12,BLUE,align="center")
    a.ellipse(430,72,65,68,STEEL)
    a.ellipse(452,92,18,24,PAPER)
    a.rect(430,101,31,17,PAPER,PAPER)
    a.label("loose steel plate",462,177,10,BLUE,align="center")
    a.label("goes in the bag",462,195,10,MUTED,align="center")


def cover(c):
    start(c,1,"Faucet assembly","An illustrated bench guide for the faucet, display and permanently attached umbilical.")
    c.drawImage(str(ROOT/SOURCES[-1]),43,H-168-324,width=178,height=324,
                preserveAspectRatio=True,anchor="c",mask="auto")
    text(c,"LOOKING FOR THE DISPLAY PINS?",244,193,10.5,"PlexBold",BLUE)
    text(c,"Start on page 2.",244,225,25,"PlexBold")
    paragraph(c,"A labeled rear view, with USB-C at the top, shows the four pads and their main-board destinations. Page 3 shows the joint and the connection checks.",245,243,318,12,15,max_height=80)
    for title,n,y in [("Rear display wiring",2,338),("Connect and check the display",3,370),
                      ("Parts and tube cuts",4,402),("Lever, sleeved tube and shell",5,434),
                      ("Fit display, mount hardware and supply",12,466),
                      ("Plug, sleeve, final inspection and packing",15,498)]:
        text(c,title,244,y,11.3,"PlexSemi")
        text(c,str(n),563,y,12,"PlexBold",BLUE,"right")
        c.linkRect("",f"page{n}",(242,H-y-8,570,H-y+17),relative=1,thickness=0)
    paragraph(c,"Follow pages 4-17 in order for a complete build. Use pages 2-3 when you only need the wiring. The matching Sculpted or Industrial base, cover, plate and gasket surround the shared tip and display.",34,548,542,12,15,max_height=65)
    paragraph(c,"Coral identifies the part being added; blue identifies a tool, datum, wire path or check. CAD sections show the actual accepted lever and current printed parts. Motion and wiring diagrams are labeled schematics. Stated dimensions govern. The rear-board picture keeps the actual pad order.",34,623,542,11.3,14.2,max_height=55)
    note(c,"LETTER SHOP BOOK","18 pages, one-up, color, 100% / no scaling. The instructional layer is already centered at 98%. Source links and physical evidence scope are on page 18.")
    footer(c,1,"CAD overview: installation guide | manual shop document",SITE+"hardware/faucet-assembly-guide/README.md")
    end_page(c)


def wiring_page(c):
    start(c,2,"The display wiring","Waveshare ESP32-S3-Touch-LCD-1.47. Hold the loose module with its back toward you and USB-C up.")
    panel(c,32,151,548,378)
    with Art(c,44,157) as a:
        wiring_art(a)
    sig6_table(c,542)
    paragraph(c,"Count C1-C4 across the black ribbon from the edge you mark. Page 15 shows plug orientation and the exact jack slots. Jack colors above name its printed labels.",35,653,537,10.5,12.5,max_height=25)
    note(c,"POWER AND SERIAL ARE DIFFERENT","VBUS takes 5 V. TX/RX are 3.3 V TTL at 921600 baud, 8N1. Leave VBAT, 3V3, RST and all other GPIO pads open. Disconnect J3 and USB while making the joints.")
    footer(c,2,"Waveshare P1 schematic + rear layout | faucet base_link.cpp | appliance pins.h",SCHEMATIC)
    end_page(c)


def sources_page(c):
    start(c,18,"Sources and fit scope","The guide adds the order and pictures. These procedures, manufacturer documents and physical records own the requirements.")
    refs=[
        ("Faucet and umbilical: cuts, mount stack, braid and packing",SITE+FU),
        ("Shell assembly: donor, lever, thimble and display seating",SITE+SHELL),
        ("Observed lever/sleeve order and shell-guided motion",SITE+OBSERVATIONS),
        ("Tube insertion jig: T handle and bench press",INSERTION_PDF),
        ("Waveshare: actual rear layout and interface labels",VENDOR),
        ("Waveshare: P1 numbers and power/UART schematic",SCHEMATIC),
        ("Faucet firmware: GPIO43 TX, GPIO44 RX, 921600 baud",SITE+"firmware/src_faucet/base_link.cpp"),
        ("Main board: J3 physical pin numbers and nets",SITE+"hardware/pcb/pcba/parts.tsx"),
        ("SIG-6: the inboard loom and rear jack",SITE+"hardware/assembly/wiring.md"),
        ("RiteAV: CAT3 USOC punchdown jack, mpn46181",JACK),
        ("Leviton: numbered 6-contact USOC terminal colors",USOC),
    ]
    for i,(title,url) in enumerate(refs):
        yy=177+i*29
        text(c,title,35,yy,10.8,"PlexSemi",BLUE)
        text(c,"OPEN SOURCE",575,yy+14,8,"PlexSemi",MUTED,"right")
        box(c,33,yy+21,545,.7,RULE)
        c.linkURL(url,(32,H-yy-23,579,H-yy+12),relative=1)
    text(c,"Physical evidence has a specific scope",34,508,17,"PlexBold")
    paragraph(c,"The recorded display cover has accepted PET-GF give, spring, fit and retention; the recorded lever has accepted fit and operation. These results belong to their identified physical articles. Retention force, cycle life, physical fault-drip behavior and maximum clampable countertop thickness remain separate qualifications.",34,523,542,11.3,14.2,max_height=83)
    for title,path,yy in [
        ("Display cover acceptance","hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json",621),
        ("Lever acceptance","hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",645),
        ("Fault-drip qualification","hardware/printed-parts/faucet/vent-qualification/README.md",669),
    ]:
        text(c,title,35,yy,11,"PlexSemi",BLUE)
        c.linkURL(SITE+path,(32,H-yy-6,580,H-yy+14),relative=1)
    paragraph(c,"Manufacturer layout and schematic reviewed 2026-10-08. The source-hash receipt is committed beside the delivery copy. Rebuild by hand when deliberately reviewing this guide; no machine build regenerates it.",34,698,542,10.3,13,max_height=42)
    footer(c,18,"Manual source receipt: output/pdf/faucet-assembly-guide.sources.json",SITE+"hardware/faucet-assembly-guide/README.md")
    end_page(c)


def build():
    GUIDE.mkdir(parents=True,exist_ok=True)
    PDF.parent.mkdir(parents=True,exist_ok=True)
    write_wiring_svg()
    write_connector_svg()
    c=canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle("Home Soda Machine - Faucet assembly")
    c.setAuthor("Home Soda Machine")
    cover(c)
    wiring_page(c)
    page(c,3,"Connect and check the display",
         "Use page 2 for the pad map. In a complete build, do this after the insulated leads pass through the neck and tip (pages 9-11).",
         solder_art,"Detail section through one P1 pad. Make the electrical joints in the dry display pocket.",
         ["Keep C1-C4 identified from the white C1 edge mark shown on page 2. With J3 and USB unplugged, strip only the dry PCB ends. Solder C1/VBUS, C2/GND, C3/TXD and C4/RXD at the page-2 pads; inspect for bridges.",
          "Leave free wire length for the page-12 slide and lowering motion. Route the leads in the open space below the PCB, clear of feet, components, lips and the USB socket.",
          "After the page-15 terminations, check the specified connections with J3 unplugged: pin 3/V5 to VBUS, 4/GND to GND, 2/IO35 to TXD and 1/IO33 to RXD. Confirm no adjacent-wire or power-to-ground short."],
         "After the unpowered checks, power through J3. The screen should boot and receive the main board's selected flavor. A bright-screen tap changes the selection and the main board ticks; a dim-screen first tap only wakes it.","firmware/src_faucet/README.md")
    # Page 4 is a cut table rather than a generic parts picture.
    start(c,4,"Lay out the matching kit","Choose the style and finish before cutting. Mark one black ribbon edge white at both free ends as C1; count C1-C4 from it. Leave both ends unterminated.")
    paragraph(c,"<b>Rigid parts:</b> matching base, display cover and above-counter plate; shared shell tip; printed lever; umbilical organizer. <b>Soft parts:</b> matching countertop gasket and fresh TPU 85A thimble. <b>Hardware:</b> bare Westbrass, Waveshare 1.47 display, 3 short M3 inserts, 3 M3 × 8 screws, captive donor washer/nut, loose stainless under-counter plate.",34,161,542,11.3,14.2,max_height=74)
    text(c,"Factory tube cuts / mm",34,251,19,"PlexBold")
    cutrows=[
        ("Blue supply, 1/4-inch OD",figure("BLUE_CUT"),figure("BLUE_CUT")),
        ("Soda tube, 3/8-inch OD",figure("SODA_FAUCET_CUT"),figure("SODA_FAUCET_CUT")),
        ("White OVER, 4 mm OD",figure("DRAIN_CUT"),figure("DRAIN_CUT")),
        ("Flavor A / B, black 4 mm OD",figure("FLAVOR_CUT")+" / "+figure("FLAVOR_CUT"),figure("FLAVOR_CUT")+" / "+figure("FLAVOR_CUT")),
    ]
    for x,label in [(38,"TUBE"),(365,"BLACK FAUCET"),(478,"WHITE FAUCET")]:
        text(c,label,x,280,9,"PlexBold",BLUE)
    for i,row in enumerate(cutrows):
        yy=307+i*34
        box(c,32,yy-21,548,32,ICE if i%2==0 else PAPER)
        for x,value in zip([38,365,478],row):
            text(c,value,x,yy,10.4,"PlexSemi")
    with Art(c,54,470) as a:
        a.line(4,31,426,31,BLUE,11)
        for x in range(4,427,14):
            a.line(x,50,x,61 if x%28==4 else 56,MUTED,.8)
        a.rect(319,2,10,40,ORANGE)
        a.arrow(324,-6,324,0,ORANGE)
        a.label("one square cut",238,9,12,BLUE)
        a.label("keep supplied reach",4,96,13,BLUE)
    paragraph(c,"The 3/8-inch soda tube matches the faucet finish. Both flavor runs are continuous black 4 mm tubing, on either faucet finish. Keep their centerline bends at or above R25. The OVER is one continuous "+figure("DRAIN_CUT")+" mm run.",34,579,542,11.3,14.2,max_height=58)
    note(c,"TOOLS AND CONSUMABLES","Tube cutter, 2.5 mm hex key, M3 heat-set tip/iron, fine soldering tip, solder, multimeter, magnifier, modular crimper and 3-prong 6P4C plug. Use the tube insertion jig, foam and PET braid specified for this bench. The linked jig guide gives its assembly and use.")
    footer(c,4,FU+" | matching style parts",SITE+FU)
    end_page(c)
    page(c,5,"Clean and fit the base inserts","Keep the shell base, tip and above-counter plate separate for access.",prep_art,
         "Underside view at left; one insert/pilot section at right. The other two inserts use the same approach.",
         ["Remove supports and stringing from the donor cavity, tube passages, pedestal sockets and insert pilots. Dry-fit the matching printed pieces.",
          "Heat-set the three ruthex RX-M3Sx4.0 short inserts into the base's bottom-facing Ø4 mm pilots. Keep each insert square; the specified insert-mouth datum is Z = 3.2 mm.",
          "Let the inserts cool undisturbed. Hand-start the M3 screws, then remove them; the plate is fitted after the tubes and shell joint."],
         "The pedestals enter their sockets freely, the mating surfaces close, and each cooled insert accepts its screw without forcing or turning in the print.",SHELL)
    page(c,6,"Attach the faucet lever first","Keep the Touch-Flo outside the shell and the soda tube out during attachment.",donor_art,
         "Accepted lever CAD at left; observed aft/down/forward motion at right is schematic.",
         ["Remove and retain the donor's own lever. Keep the bare metal donor outside the shell, with its top water port empty.",
          "Hold the printed faucet lever aft of its working position. Lower it onto the valve, then slide it forward around the metal cylinder until its light snap seats.",
          "Leave the attached lever down at its unpressed rest position. Fit the tube next; pressing with the tube absent can dislodge the lever aft."],
         "The printed lever is attached before tube insertion and before shell insertion. Its light snap holds it during handling. Keep it down at rest for the next two pages.",OBSERVATIONS)
    page(c,7,"Fit the sleeve onto the tube","Stretch and slide the fresh TPU 85A sleeve evenly onto the tube outside the Touch-Flo.",thimble_art,
         "Current thimble CAD section at left; fully fitted tube/cap section at right is schematic.",
         ["Hold the finish-matched 330 mm soda tube with the insertion jig's tube grip. Keep its square-cut sealing end clean, accessible and undamaged.",
          "Start the fresh TPU sleeve's open mouth around the tube end. Work around the whole circumference, stretching and sliding it evenly rather than advancing one side far ahead.",
          "Continue until the square tube end bottoms on the cap. Straighten the sleeve wall and rim; the cap's center flow hole stays open. Keep the donor port empty."],
         "The cap is fully against the square tube end, with a straight sleeve wall and even rim. The sleeve is fitted before either part enters the donor.","hardware/printed-parts/faucet/tpu-o-ring/README.md")
    page(c,8,"Insert the sleeved tube","The faucet lever stays attached and down at unpressed rest. The Touch-Flo is bare metal.",sleeve_insert_art,
         "CAD section shows cap-first port alignment; the attached lever's rest position is schematic.",
         ["Support the bare donor in the insertion jig, clear of its attached faucet lever and threaded shank. The empty top port faces the sleeved tube.",
          "Align tube and port. Push the tube and sleeve into the metal together, cap first, using the T handle or press in the separate jig guide.",
          "Release the grip and lift the donor out. Preserve the tube's seated position; the installed tube blocks the faucet lever's aft disengagement path."],
         "The sleeve remains straight on the tube through insertion and the cap stays against the tube end. The faucet lever remains down at unpressed rest. The shell is fitted next.",INSERTION)
    page(c,9,"Insert the donor into the shell","Flip the attached faucet lever up for this insertion, with the sleeved soda tube already seated.",shell_insertion_art,
         "Sculpted base CAD section at left; observed shell-guided lever motion at right is schematic.",
         ["Keep the base plate and tip separate. Flip the attached faucet lever up. Feed the soda tube through the lower neck while preserving its donor-port seat.",
          "Insert the donor through the open shell foot, with the handle toward the front opening. The shell pushes the lever forward as the donor advances.",
          "Fully seat the donor. The shell prevents the lever reaching the flipped-up position; let it snap down to unpressed rest. Keep tube and lever seated while routing."],
         "The donor is fully seated, the lever has snapped down to unpressed rest, and the shell prevents the flipped-up assembly position. The soda tube remains seated.",SHELL)
    page(c,10,"Route the shared tip","Keep the drink paths inside their LLDPE tubes and the display leads continuously insulated.",route_tip_art,
         "Current shared tip CAD section at left; passage and end positions at right are schematic.",
         ["Feed S, F1, F2 and the flat insulated SIG-6 ribbon through the tip's smooth shared passage. Keep C1-C4 identified and the display ends unterminated.",
          "Feed the separate white 4 mm D between the flavors. Set its square end at the terminal datum, leaving the 3 mm mouth clearance empty and its bore unobstructed.",
          "Keep the round Ø4 mm underside fault-drip hole clear into the common passage. Position the three beverage ends at their outlets; final flush trimming follows closure."],
         "All drink tubes and insulated leads pass freely. D ends inside with its mouth clear; the separate bottom hole is open. The continuous ribbon stays flat through the curved joint.",SHELL)
    page(c,11,"Close the neck and base","Route the continuous bundle before rotating the dry curved lap closed.",closure_art,
         "Neck joining at left; base screws aligned with their underside holes at right. Schematics, not screw-station dimensions.",
         ["Rotate the tip plug into the base socket about the arc center until the seam seats. Preserve the soda tube's donor-port seat and keep the tip's bottom opening clear.",
          "Pass F1/D/F2 and the flat ribbon through the plate's rear passage, and the bare shank through its center. Keep the ribbon flat behind the bundle. Seat all three pedestals.",
          "Install three M3 × 8 screws from below with a 2.5 mm hex key, progressively and evenly. Square-trim only the three beverage outlets flush with their symmetric drink face."],
         "The plate and curved seam close evenly. Lever travel and both flavor paths remain free. D ends inside the common passage and its separate bottom opening remains bare. Now connect/check the display using pages 2-3.",SHELL)
    page(c,12,"Fit the display and cover","USB-C faces the dispense face; the opposite end points up the gooseneck. Complete the page-3 joints/check first.",display_art,
         "Side sections show the USB-C end at the outlet. Two of four feet are visible; the 9.5 mm lift is normal to the glass.",
         ["Keep USB-C toward the dispense face. Route the leads freely below the PCB toward its southwest corner as viewed from the glass. Spread the wings and load the display through the cover's open underside.",
          "Hold the pair 9.5 mm above the final seat, normal to the glass. Slide it along the tip from the outlet end until the four metal feet align with their supports; feed the ribbon as it moves.",
          "Lower the pair normal to the glass until both broad lips seat in the side grooves. Check all four feet, the glass/bezel clearance and the real tube/wire/component clearances."],
         "Both retaining lips and four feet are seated, the seam closes and touch pressure leaves the display seated. No wire is pinched or pulling a solder pad. The display has no mounting screw or insert.",SHELL)
    page(c,13,"Fit gasket, washer and captive nut","The mount hardware must be on the bare shank before the blue supply is permanently connected.",mount_art,
         "Exploded order from the shell foot downward. The steel under-counter plate stays loose for the install bag.",
         ["Pass both flavor tails, D and the unterminated wall end of the ribbon through the gasket's matching passage. Pass the bare shank through its center and slide the gasket flat against the printed plate.",
          "Slide the retained donor washer onto the shank, then thread on the retained donor nut loosely. Keep the gap above them for the countertop and laterally inserted steel plate.",
          "Leave the steel plate off. Thread the organizer onto unjoined flavors, D, flat ribbon and bare blue tube before the supply joint and plug. Keep it below the washer/nut workspace."],
         "The gasket lies flat and covers the base screw heads. The washer/nut are on the shank above the supply joint. The 38 mm routing envelope does not establish maximum clampable countertop thickness.",FU)
    page(c,14,"Route flavors and connect blue supply","Both finishes use continuous black 4 mm flavor tubes and the same donor supply connection.",supply_art,
         "Continuous black flavor tubes at left. Blue supply connection at right, shown before tightening.",
         ["Keep each black 4 mm flavor tube uncut from its tip to appliance tail. Pass both through the 4.40 mm organizer bores; OVER uses the third 4.40 mm bore, and blue uses 6.65 mm.",
          "Keep F1/D/F2 and ribbon straight through the countertop routing zone. Below that zone, preserve the specified R30 flavor/ribbon returns and R25 drain returns below the organizer.",
          "Put one Siptenk brass stiffener fully inside the blue 1/4-inch tube end. Insert the stiffened end into the donor's lower compression port and tighten its factory ferrule/nut hand-snug plus 1/4 turn."],
         "Both continuous flavor tubes route freely. The blue tube is connected below the captive hardware. The separate 3/8-inch soda tube remains in the donor's top port.",FU)
    plug_page(c)
    page(c,16,"Insulate and sleeve the bundle","Lay the completed signal cable beside all four tubes before sliding on any braid segment.",sleeve_art,
         "Bundle section at left; two fitted sleeve segments at right. D gathers opposite the cold foam from the flavors.",
         ["Fit foam only to the blue cold tube, one segment at a time, butting the segment above it. The standard run uses five pieces covering "+figure("FOAM_LENGTH")+" mm; leave "+figure("FOAM_BARE_TOP")+" mm bare at the top and 75 mm at the wall tail.",
          "Gather the flavor pair beside the foam and D on its opposite side, with SIG-6 inside the braid. Slide one fitted PET-braid segment over the pack for each foam segment.",
          "Fit before cutting: braid shortens when expanded. The top braid extends "+figure("SLEEVE_ABOVE_FOAM")+" mm above the foam to the organizer, covering the continuous tubes and flat cable."],
         "Foam joints and braid joints butt without gaps; no braid segment excludes the display cable or D. All four tails remain bare, square and accessible beyond the final sleeve.",FU)
    page(c,17,"Identify, inspect and bag","The customer receives the completed faucet, gasket, captive mount hardware, tubes and signal plug.",final_art,
         "Four identified bare wall tails. One stainless under-counter plate ships loose beside the complete faucet/umbilical.",
         ["Thread the matching collars onto the wall tails: blue SODA, two black FLAVOR and white 4 mm OVER. Run each collar up the bare tail below the braid with its word visible.",
          "Inspect the complete unit: seams/lips seated; full lever motion; three beverage ends flush; D and bottom port clear; unpinched cable; page-2 continuity and page-3 powered flavor response.",
          "Coil the umbilical to an 8-12 inch loop diameter, bag it with the loose steel plate, then seal and label with the build number and FAUCET-UMBILICAL-SUBASSEMBLY."],
         "The blue supply is permanently attached below the captive washer/nut. The gasket is already fitted. The loose steel plate is in the bag. Qualification of physical fault discharge and mounting range follows the linked physical qualification, not this visual inspection.",FU)
    sources_page(c)
    c.save()
    publish(PDF,GUIDE,"Faucet assembly guide",
            "Shop guide - faucet, rear display wiring and umbilical; 18 illustrated Letter pages",
            N,SOURCES,extra={
                "artwork":"current component CAD sections and labeled motion/wiring schematics; rear pad order from Waveshare; existing CAD overview on page 1",
                "display":{"model":"ESP32-S3-Touch-LCD-1.47", "view":"rear PCB, USB-C at top",
                           "installed_orientation":"USB-C toward dispense face; opposite end up the gooseneck",
                           "left_top_four":SIG6,
                           "wire_stock":"28 AWG all-black 4P ribbon outboard; 22 AWG all-black inboard",
                           "C1_index":"builder adds white mark to one ribbon edge at both free ends",
                           "RJ11_plug_view":"gold contacts toward viewer, nose up, cable down, latch behind",
                           "jack_view":"punchdown side up, front opening down; rear 3/4, middle 2/5, front 1/6 unused",
                           "power_volts":5,"logic_volts":3.3,"baud":921600},
                "manufacturer_references":{"reviewed":"2026-10-08", "docs":VENDOR,
                                           "schematic":SCHEMATIC,"rear_layout":INTERFACE,
                                           "jack":JACK,"six_contact_USOC":USOC,"jack_contact_view":MODULAR_VIEW},
            })
    print(f"Wrote {PDF.relative_to(ROOT)} ({N} pages), display-wiring.svg and sig6-connector-wiring.svg")


if __name__ == "__main__":
    build()
