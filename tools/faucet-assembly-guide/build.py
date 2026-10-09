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
SEALS = "hardware/printed-parts/faucet/asse-vent-seals/README.md"
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
    FU, SHELL, SEALS,
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
    "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json",
    "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
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


def donor_art(a):
    for j,(title,x) in enumerate([("1  DONOR UP",14),("2  LEVER DOWN",185),("3  SLIDE FORWARD",357)]):
        a.rect(x,16,157,253,PAPER,RULE)
        a.label(title,x+78,39,10,BLUE,align="center")
        a.shape([(x+28,213),(x+31,126),(x+126,126),(x+134,213)],STEEL)
        a.rect(x+59,147,41,58,BRASS)
        a.rect(x+76,205,9,46,BRASS)
        a.ellipse(x+80,152,33,24,BRASS)
        a.label("soda tube absent",x+78,65,10,MUTED,align="center")
        if j==0:
            a.arrow(x+79,254,x+79,222)
            a.label("from below",x+79,111,10,BLUE,align="center")
        elif j==1:
            a.shape([(x+92,104),(x+115,104),(x+101,142),(x+39,148),(x+37,137),(x+83,124)],ORANGE)
            a.arrow(x+106,78,x+106,94)
            a.label("aft of working pose",x+78,234,9.5,MUTED,align="center")
        else:
            a.shape([(x+74,159),(x+98,159),(x+88,182),(x+15,185),(x+15,174),(x+66,170)],ORANGE)
            a.arrow(x+129,104,x+63,104)
            a.label("front / handle end",x+78,234,9.5,MUTED,align="center")


def thimble_art(a):
    a.label("SECTION THROUGH TOP PORT",153,23,11,BLUE,align="center")
    a.rect(86,120,133,139,BRASS)
    a.rect(113,120,79,112,PAPER)
    a.shape([(118,124),(118,215),(187,215),(187,124)],None,ORANGE,8,False)
    a.rect(118,215,69,12,ORANGE)
    a.rect(141,215,22,12,PAPER,PAPER)
    a.rect(126,45,52,140,STEEL)
    a.rect(139,45,26,140,PAPER,PAPER)
    a.arrow(152,187,152,210)
    a.label("3/8-inch soda tube",154,41,12,BLUE,align="center")
    a.label("fresh TPU thimble",275,157,13,ORANGE)
    a.line(271,165,187,182,ORANGE,1.5)
    a.label("CAP DOWN",276,193,16,ORANGE)
    a.label("tube bottoms here",275,230,12,BLUE)
    a.line(270,224,180,215,BLUE,1.5)
    a.arrow(152,281,152,234,BLUE)
    a.label("water from valve",152,291,11,BLUE,align="center")


def bung(a,x,y,upstream=True):
    a.ellipse(x,y,102,102,ORANGE)
    a.ellipse(x+5,y+5,92,92,STEEL)
    # S, two flavors and four separate insulated-wire holes.
    a.ellipse(x+36,y+55,30,30,PAPER)
    for xx in [21,62]:
        a.ellipse(x+xx,y+32,20,20,PAPER)
    if upstream:
        a.ellipse(x+43,y+27,16,16,PAPER)
    for xx in [25,41,57,73]:
        a.ellipse(x+xx-3,y+17,6,6,PAPER)


def thread_art(a):
    a.label("FREE DRINK / DISPLAY ENDS",13,22,11,BLUE)
    for i,ink in enumerate([INK,INK,BLUE]):
        a.line(22,104+i*39,477,104+i*39,ink,7 if i<2 else 11)
    for i in range(4):
        a.line(22,52+i*10,477,52+i*10,WIRE,2)
        a.label(f"C{i+1}",486,55+i*10,8.5,INK)
    a.line(465,52,474,52,PAPER,.9)
    for x,label,drain in [(169,"1  UPSTREAM",True),(332,"2  DISTAL",False)]:
        bung(a,x,86,drain)
        a.label(label,x+51,226,12,BLUE,align="center")
        a.arrow(x+51,242,x+51,259,ORANGE)
        a.label("flange toward open joint",x+51,276,9,MUTED,align="center")
    a.arrow(103,221,139,221)
    a.label("thread in this order",82,247,10,BLUE,align="center")
    a.label("D is separate",447,261,11,MUTED,align="center")
    a.line(407,238,487,238,MUTED,5)
    a.line(407,238,487,238,PAPER,3)


def seal_section(a,upstream=False):
    # Unwrapped axial section, explicitly labeled; the insertion path inset is curved.
    a.label("AXIAL SECTION / FLOW LEFT TO RIGHT",10,17,11,BLUE)
    a.rect(24,97,401,25,STEEL)
    a.rect(24,210,401,25,STEEL)
    for x in [152,352]:
        a.rect(x,116,20,97,"#D0D7E1")
        a.rect(x+3,121,14,89,PAPER,PAPER)
    # Depict the local tube/wire pack as continuous runs, not sealed fluid mixing.
    for y,ink,w in [(142,BLUE,3),(158,INK,6),(181,INK,6),(199,BLUE,9)]:
        a.line(28,y,462,y,ink,w)
    x=154 if upstream else 354
    a.rect(x,123,17,86,ORANGE)
    for y in [142,158,181,199]:
        a.line(x-2,y,x+19,y,PAPER,2)
    if upstream:
        a.line(29,171,211,171,MUTED,7)
        a.line(29,171,211,171,PAPER,4)
        a.ellipse(207,167,8,8,PAPER)
        a.arrow(210,174,235,195,BLUE,1.5)
        a.label("D ends inside cavity",254,74,12,BLUE,align="center")
        a.line(253,81,211,168,BLUE,1)
    else:
        a.line(29,253,101,253,MUTED,7)
        a.line(29,253,101,253,PAPER,4)
        a.label("D stays outside",103,257,11,BLUE)
        a.rect(92,133,230,11,BLUE,BLUE)
        a.rect(92,211,230,10,BLUE,BLUE)
        a.arrow(288,83,345,83,ORANGE)
        a.label("perimeter tool",198,72,12,BLUE,align="center")
    a.rect(221,210,87,25,PAPER,PAPER)
    a.arrow(263,207,263,253,BLUE)
    a.label("separate bottom opening",283,281,11,BLUE,align="center")
    a.label("upstream gland",161,54,10,MUTED,align="center")
    a.label("distal gland",362,54,10,MUTED,align="center")


def distal_art(a):
    seal_section(a)
    # Curved pusher motion is a separate, recognizable inset.
    a.label("ROTATE THE TOOL",441,22,10,BLUE,align="center")
    a.shape([(426,34),(445,28),(460,35),(470,52),(473,73)],None,BLUE,9,False)
    a.arrow(473,74,470,95,BLUE)


def drain_art(a):
    a.label("SET D WHILE THE BUNG IS OUT",14,24,11,BLUE)
    a.rect(44,92,22,108,ORANGE)
    a.rect(36,89,8,114,ORANGE)
    a.line(14,155,215,155,MUTED,13)
    a.line(14,155,215,155,PAPER,8)
    a.ellipse(211,150,8,10,PAPER)
    a.line(36,73,36,219,BLUE,.8,[3,2])
    a.line(215,130,215,219,BLUE,.8,[3,2])
    a.dim(36,219,215,219)
    a.label("8.0 ± 0.2 mm",128,242,16,BLUE,align="center")
    a.label("flange FRONT face",18,59,11,ORANGE)
    a.label("square open end",143,112,11,BLUE)
    a.label("toward body / cavity",130,273,10,MUTED,align="center")
    a.arrow(259,147,283,147)
    a.shape([(333,204),(324,154),(334,106),(365,65),(411,46)],None,STEEL,47,False)
    a.shape([(332,203),(324,154),(334,106),(365,65),(411,46)],None,PAPER,29,False)
    a.line(358,81,383,108,ORANGE,8)
    a.shape([(310,211),(300,165),(310,116),(335,83)],None,BLUE,8,False)
    a.arrow(335,82,351,66,BLUE)
    a.label("advance D + bung",384,242,12,BLUE,align="center")
    a.label("together around the arc",384,261,10,MUTED,align="center")


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
    a.label("AFTER BOTH BUNGS ARE SEATED",14,20,11,BLUE)
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
    a.label("WHITE FAUCET ONLY",102,21,11,BLUE,align="center")
    for x,y,name in [(43,79,"A"),(128,45,"B")]:
        a.line(x,38,x,y,MUTED,9)
        a.line(x,38,x,y,PAPER,6)
        a.rect(x-15,y,30,48,STEEL)
        a.line(x,y+48,x,248,INK,9)
        a.label(name,x,y+28,14,BLUE,align="center")
    a.label("white above / black below",102,274,10,MUTED,align="center")
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
    for x,y,diam,ink in [(205,64,31,INK),(213,105,31,INK),(58,128,20,PAPER)]:
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
                      ("Parts and tube cuts",4,402),("Build the shell and vent chamber",5,434),
                      ("Fit display, mount hardware and supply",12,466),
                      ("Plug, sleeve, final inspection and packing",15,498)]:
        text(c,title,244,y,11.3,"PlexSemi")
        text(c,str(n),563,y,12,"PlexBold",BLUE,"right")
        c.linkRect("",f"page{n}",(242,H-y-8,570,H-y+17),relative=1,thickness=0)
    paragraph(c,"Follow pages 4-17 in order for a complete build. Use pages 2-3 when you only need the wiring. The matching Sculpted or Industrial base, cover, plate and gasket surround the shared tip and display.",34,548,542,12,15,max_height=65)
    paragraph(c,"Coral identifies the part being added; blue identifies a tool, datum, wire path or check. Pictures are schematics unless identified as a CAD overview. Stated dimensions govern. The rear-board picture keeps the actual pad order.",34,623,542,11.3,14.2,max_height=55)
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
        ("Vent seals: threading, curved pusher and drain setting",SITE+SEALS),
        ("Waveshare: actual rear layout and interface labels",VENDOR),
        ("Waveshare: P1 numbers and power/UART schematic",SCHEMATIC),
        ("Faucet firmware: GPIO43 TX, GPIO44 RX, 921600 baud",SITE+"firmware/src_faucet/base_link.cpp"),
        ("Main board: J3 physical pin numbers and nets",SITE+"hardware/pcb/pcba/parts.tsx"),
        ("SIG-6: the inboard loom and rear jack",SITE+"hardware/assembly/wiring.md"),
        ("RiteAV: CAT3 USOC punchdown jack, mpn46181",JACK),
        ("Leviton: numbered 6-contact USOC terminal colors",USOC),
    ]
    for i,(title,url) in enumerate(refs):
        yy=177+i*31
        text(c,title,35,yy,11.3,"PlexSemi",BLUE)
        text(c,"OPEN SOURCE",575,yy+14,8,"PlexSemi",MUTED,"right")
        box(c,33,yy+21,545,.7,RULE)
        c.linkURL(url,(32,H-yy-23,579,H-yy+12),relative=1)
    text(c,"Physical evidence has a specific scope",34,508,17,"PlexBold")
    paragraph(c,"The recorded display cover has accepted PET-GF give, spring, fit and retention; the recorded lever has accepted fit and operation. These results belong to their identified physical articles. Retention force, cycle life, the current complete vent assembly's containment and maximum clampable countertop thickness remain separate qualifications.",34,523,542,11.3,14.2,max_height=83)
    for title,path,yy in [
        ("Display cover acceptance","hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json",621),
        ("Lever acceptance","hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",645),
        ("Vent-cavity qualification","hardware/printed-parts/faucet/vent-qualification/README.md",669),
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
         "Use page 2 for the pad map. In a complete build, do this after the wires pass through both seated vent bungs (pages 8-10).",
         solder_art,"Detail section through one P1 pad. Make the electrical joints in the dry display pocket.",
         ["Keep C1-C4 identified from the white C1 edge mark shown on page 2. With J3 and USB unplugged, strip only the dry PCB ends. Solder C1/VBUS, C2/GND, C3/TXD and C4/RXD at the page-2 pads; inspect for bridges.",
          "Leave free wire length for the page-12 slide and lowering motion. Route the leads in the open space below the PCB, clear of feet, components, lips and the USB socket.",
          "After the page-15 terminations, check the specified connections with J3 unplugged: pin 3/V5 to VBUS, 4/GND to GND, 2/IO35 to TXD and 1/IO33 to RXD. Confirm no adjacent-wire or power-to-ground short."],
         "After the unpowered checks, power through J3. The screen should boot and receive the main board's selected flavor. A bright-screen tap changes the selection and the main board ticks; a dim-screen first tap only wakes it.","firmware/src_faucet/README.md")
    # Page 4 is a cut table rather than a generic parts picture.
    start(c,4,"Lay out the matching kit","Choose the style and finish before cutting. Mark one black ribbon edge white at both free ends as C1; count C1-C4 from it. Leave both ends unterminated.")
    paragraph(c,"<b>Rigid parts:</b> matching base, display cover and above-counter plate; shared shell tip; printed lever. <b>Soft parts:</b> matching countertop gasket, fresh TPU thimble and two vent bungs. <b>Hardware:</b> bare Westbrass, Waveshare 1.47 display, 3 short M3 inserts, 3 M3 × 8 screws, captive donor washer/nut, loose stainless under-counter plate.",34,161,542,11.3,14.2,max_height=74)
    text(c,"Factory tube cuts / mm",34,251,19,"PlexBold")
    cutrows=[
        ("Blue supply, 1/4-inch OD",figure("BLUE_CUT"),figure("BLUE_CUT")),
        ("Soda tube, 3/8-inch OD",figure("SODA_FAUCET_CUT"),figure("SODA_FAUCET_CUT")),
        ("White OVER, 4 mm OD",figure("DRAIN_CUT"),figure("DRAIN_CUT")),
        ("Flavor A / B, black 1/4-inch OD",figure("FLAVOR_CUT")+" / "+figure("FLAVOR_CUT"),figure("BLACK_A_CUT")+" / "+figure("BLACK_B_CUT")),
        ("Flavor A / B, white 1/4-inch OD","-",figure("WHITE_A_CUT")+" / "+figure("WHITE_B_CUT")),
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
    paragraph(c,"The 3/8-inch soda tube matches the faucet finish. Both flavor runs are black throughout a Black faucet. A White faucet has white upper runs and black lower runs joined by two PP0408W unions. The OVER is one continuous 1872 mm run.",34,579,542,11.3,14.2,max_height=58)
    note(c,"TOOLS AND CONSUMABLES","Tube cutter, 2.5 mm hex key, M3 heat-set tip/iron, fine soldering tip, solder, multimeter, magnifier, modular crimper and 3-prong 6P4C plug. Use the vent perimeter pusher, foam and PET braid already specified for this bench.")
    footer(c,4,FU+" | matching style parts",SITE+FU)
    end_page(c)
    page(c,5,"Clean and fit the base inserts","Keep the shell base, tip and above-counter plate separate for access.",prep_art,
         "Underside view at left; one insert/pilot section at right. The other two inserts use the same approach.",
         ["Remove supports and stringing from the donor cavity, tube passages, pedestal sockets and insert pilots. Dry-fit the matching printed pieces.",
          "Heat-set the three ruthex RX-M3Sx4.0 short inserts into the base's bottom-facing Ø4 mm pilots. Keep each insert square; the specified insert-mouth datum is Z = 3.2 mm.",
          "Let the inserts cool undisturbed. Hand-start the M3 screws, then remove them; the plate is fitted after the tubes and shell joint."],
         "The pedestals enter their sockets freely, the mating surfaces close, and each cooled insert accepts its screw without forcing or turning in the print.",SHELL)
    page(c,6,"Seat the donor, then the lever","The soda tube stays out during the complete aft/down/forward lever motion.",donor_art,
         "Side-view sequence. Front is the projecting handle end; the donor enters through the open foot.",
         ["Remove and retain the donor's own lever. With the base plate separate and soda tube absent, seat the bare donor from below, valve interface facing the front opening.",
          "Hold the printed lever aft of its working position. Lower it onto the valve, then slide it forward around the metal cylinder until its light snap seats.",
          "Move the handle through its actual travel. Check the rear arm's rising clearance before fitting the soda tube or closing the base."],
         "The lever seats and operates on the real donor without catching the shell. Keep the soda tube out if the lever needs to be removed or repositioned.",SHELL)
    page(c,7,"Seat the thimble and soda tube","A fresh TPU thimble seals the 3/8-inch tube in the donor's top water port.",thimble_art,
         "Section view. The annular cap has a center flow hole; the tube's square end seats on its upper face.",
         ["Place the fresh TPU 90A thimble cap-down in the donor's top port. The open end faces up toward the soda tube.",
          "Feed the finish-matched 330 mm soda tube through the lower neck. Push its square-cut end down through the thimble until it bottoms on the cap.",
          "Keep that seating while routing the tube toward the shared tip. The installed tube blocks the printed lever's aft disengagement path."],
         "The tube reaches its positive bottom seat, the lever still travels fully and the tube remains seated while the upper bundle is handled.","hardware/printed-parts/faucet/tpu-o-ring/README.md")
    page(c,8,"Pre-thread the vent bungs","The display wires must be individually insulated through both seals before they are soldered.",thread_art,
         "Threading order, not an installed chamber section. Both bung flanges face back toward the open shell joint.",
         ["Keep the display ends unterminated. Peel the ribbon web into four continuously insulated conductors only through the local spread; preserve wire order and reject any nicked jacket.",
          "Wet the bores with clean water. From the free S, F1, F2 and wire ends, thread the upstream bung first, then the distal bung. Leave the upstream D hole empty.",
          "Park the upstream bung clear of the pusher's full stroke. Feed the three beverage ends and four wires through the tip's dry outlet guides, leaving D outside the tip."],
         "Four intact wire jackets and all three drink tubes pass through each bung. No stripped wire, solder joint, adhesive or slit is inside the seals.",SEALS)
    page(c,9,"Seat the distal bung first","D stays outside while the slotted perimeter pusher passes through the empty upstream gland.",distal_art,
         "The large section is unwrapped for visibility. The inset shows the actual curved insertion direction.",
         ["Fit the pusher around the continuous bundle through its 19 mm side slot. Its leading annulus bears on the distal bung's perimeter.",
          "Rotate the curved tool about the gooseneck arc center. Advance the distal bung through the empty upstream gland until its body meets the distal backstop and its flange enters the retaining groove.",
          "Withdraw the tool along that same curve until it clears the socket, then lift it off through the open side. Leave the upstream bung parked outside."],
         "The complete distal flange is captured, its body is seated at the backstop, and the continuous tubes and insulated wires remain in their assigned bores.",SEALS)
    page(c,10,"Set D and seat the upstream bung","The drain ends inside the wet chamber. It does not continue to the drink face.",drain_art,
         "Measure from the flange front face contacted by the tool, toward the bung body and cavity, to D's square cut.",
         ["With the upstream bung outside the tip, feed D through its own hole. Set the square-cut end to 8.0 ± 0.2 mm from the flange's front face toward the body/cavity.",
          "Refit the perimeter pusher and rotate D plus the upstream bung into the gland together. Its flange seats in the groove against the body-seat shoulder; the upstream body has no terminal backstop.",
          "Remove the pusher by the same curved withdrawal and side exit. Confirm D opens into the cavity and the separate bottom discharge opening is completely clear."],
         "Both flanges are captured; every intended tube/wire bore is occupied. D's open end projects into the cavity, while the three drink tubes continue through the distal seal into their dry channels.",SEALS)
    page(c,11,"Close the neck and base","Route the continuous bundle before rotating the dry curved lap closed.",closure_art,
         "Neck joining at left; base screws aligned with their underside holes at right. Schematics, not screw-station dimensions.",
         ["Rotate the tip socket over the base plug about the arc center until the seam seats. Preserve the soda tube's donor-port seat and keep the chamber's bottom opening clear.",
          "Pass F1/D/F2 and the flat ribbon through the plate's rear passage, and the bare shank through its center. Keep the ribbon flat behind the bundle. Seat all three pedestals.",
          "Install three M3 × 8 screws from below with a 2.5 mm hex key, progressively and evenly. Square-trim only the three beverage outlets flush with their symmetric drink face."],
         "The plate and curved seam close evenly. Lever travel and both flavor paths remain free. D ends inside the chamber and its separate bottom opening remains bare. Now connect/check the display using pages 2-3.",SHELL)
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
          "Leave the under-counter steel plate off. The next page connects the blue tube below the hardware, making this washer and nut permanently captive."],
         "The gasket lies flat and covers the base screw heads. The washer/nut are on the shank above the supply joint. The 38 mm routing envelope does not establish maximum clampable countertop thickness.",FU)
    page(c,14,"Join White runs and the blue supply","A Black faucet has continuous flavor tubes. Both finishes use the same donor supply connection.",supply_art,
         "White flavor unions at left, B above A. Blue supply connection at right, shown before tightening.",
         ["On a White faucet, push each white upper flavor run and matching black lower run into its PP0408W union to the 16 mm stops. Keep B's union one 30 mm union length above A's, at the factory stations.",
          "Keep F1/D/F2 and ribbon straight through the countertop routing zone. Below that zone, preserve the specified R30 flavor/ribbon returns and R25 drain returns around the unions.",
          "Put one Siptenk brass stiffener fully inside the blue 1/4-inch tube end. Insert the stiffened end into the donor's lower compression port and tighten its factory ferrule/nut hand-snug plus 1/4 turn."],
         "Both White-faucet unions bottom and pass a tug check. The blue tube is connected below the captive hardware. The separate 3/8-inch soda tube remains in the donor's top port.",FU)
    plug_page(c)
    page(c,16,"Insulate and sleeve the bundle","Lay the completed signal cable beside all four tubes before sliding on any braid segment.",sleeve_art,
         "Bundle section at left; two fitted sleeve segments at right. D gathers opposite the cold foam from the flavors.",
         ["Fit foam only to the blue cold tube, one segment at a time, butting the segment above it. The standard run uses five pieces covering 1322 mm; leave 143 mm bare at the top and 75 mm at the wall tail.",
          "Gather the flavor pair beside the foam and D on its opposite side, with SIG-6 inside the braid. Slide one fitted PET-braid segment over the pack for each foam segment.",
          "Fit before cutting: braid shortens when expanded. The top braid extends 126 mm above the foam to cover both unions on a White faucet, or that same length of the continuous Black-faucet runs."],
         "Foam joints and braid joints butt without gaps; no braid segment excludes the display cable or D. All four tails remain bare, square and accessible beyond the final sleeve.",FU)
    page(c,17,"Identify, inspect and bag","The customer receives the completed faucet, gasket, captive mount hardware, tubes and signal plug.",final_art,
         "Four identified bare wall tails. One stainless under-counter plate ships loose beside the complete faucet/umbilical.",
         ["Thread the matching collars onto the wall tails: blue SODA, two black FLAVOR and white 4 mm OVER. Run each collar up the bare tail below the braid with its word visible.",
          "Inspect the complete unit: seams/lips seated; full lever motion; three beverage ends flush; D and bottom port clear; unpinched cable; page-2 continuity and page-3 powered flavor response.",
          "Coil the umbilical to an 8-12 inch loop diameter, bag it with the loose steel plate, then seal and label with the build number and FAUCET-UMBILICAL-SUBASSEMBLY."],
         "The blue supply is permanently attached below the captive washer/nut. The gasket is already fitted. The loose steel plate is in the bag. Acceptance of vent containment and mounting range follows the linked physical qualification, not this visual inspection.",FU)
    sources_page(c)
    c.save()
    publish(PDF,GUIDE,"Faucet assembly guide",
            "Shop guide - faucet, rear display wiring and umbilical; 18 illustrated Letter pages",
            N,SOURCES,extra={
                "artwork":"original vector schematics; rear pad order from Waveshare; existing CAD overview on page 1",
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
