"""Draw the drilling/cutting bench book by hand. No appliance/CAD build.

Pictures are vector schematics; dimensions and fitting checks govern. Source
hashes record this authored edition. Re-run only when reviewing this document.
"""
from __future__ import annotations

import ast
import json
import math
import operator
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/assembly-guides"))
from common import *

PDF = ROOT / "output/pdf/drill-and-cut-guide.pdf"
GUIDE = ROOT / "hardware/drill-and-cut-guide"
SITE = "https://github.com/derekbreden/homesodamachine/blob/main/"
DOCS = "https://homesodamachine.com/docs/"
PRESS_MANUAL = "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/4208T.manual.20220914.pdf?v=1664398265"
SAW_MANUAL = "https://cdn.shopify.com/s/files/1/0012/0350/3168/files/BA4555.manual.20211206.pdf?v=1649272733"
SOURCES = [
    "hardware/assembly/pressure-vessel.md",
    "hardware/cut-parts/carbonation/endcaps-circular/endcap_circular_dxf.py",
    "hardware/printed-parts/cold-core/_float_interface.py",
    "hardware/assembly/handwork.md",
    "hardware/assembly/water-inlet-jet.md",
    "hardware/printed-parts/fixtures/water-inlet-jet/README.md",
    "hardware/printed-parts/fixtures/weld-rotator/README.md",
    "hardware/assembly/refrigerant-loop.md",
    "hardware/assembly/internal-plumbing.md",
    "hardware/assembly/cold-core.md",
    "hardware/assembly/faucet-and-umbilical.md",
    "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md",
    "hardware/assembly/enclosure-mechanical.md",
    "hardware/assembly/finish-pack-ship.md",
    "hardware/assembly/cable-assemblies.md",
    "hardware/wiring/ac-wiring-schedule.md",
    "hardware/ledger/tools.md",
    "hardware/topology/fluid-topology.md",
    "hardware/mechanical-qualification/README.md",
    "hardware/printed-parts/fixtures/tube-miter-box/README.md",
]


def marked_number(path, token):
    match = re.search(r"\[([\d.]+)(?:[^\]]*)\]\(" + re.escape(token) + r"\)",
                      (ROOT / path).read_text())
    if not match:
        raise ValueError(f"Review changed source figure {path}: {token}")
    return float(match.group(1))


def constants(path, wanted, external=None):
    """Arithmetic dependency closure only; never import a geometry module."""
    tree = ast.parse((ROOT / path).read_text())
    expressions = {t.id: s.value for s in tree.body if isinstance(s, ast.Assign)
                   for t in s.targets if isinstance(t, ast.Name)}
    values = dict(external or {})
    ops = {ast.Add: operator.add, ast.Sub: operator.sub,
           ast.Mult: operator.mul, ast.Div: operator.truediv}
    def evaluate(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.Name):
            return get(n.id)
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            return ops[type(n.op)](evaluate(n.left), evaluate(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -evaluate(n.operand)
        raise ValueError(f"Review numeric source: {path}: {ast.dump(n)}")
    def get(name):
        if name not in values:
            values[name] = evaluate(expressions[name])
        return values[name]
    return {name: get(name) for name in wanted}


F = constants(SOURCES[2], ["rod_axis_from_inner_wall"])
D = constants(SOURCES[1], ["disc_diameter", "disc_thickness", "hole_spacing",
                           "register_radius", "register_drill_diameter", "register_depth"], F)
if not math.isclose(D["register_drill_diameter"], 9/64):
    raise ValueError("Review the named register drill and cross-section.")
if not math.isclose(D["register_depth"], .1) or not math.isclose(D["disc_thickness"], .25):
    raise ValueError("Review register depth and intact plate thickness.")
ROD = marked_number(SOURCES[3], "ROD_LEN")
RESERVOIR_ROD = marked_number(SOURCES[3], "RESERVOIR_ROD_LEN")
FU = {name: marked_number("hardware/assembly/faucet-and-umbilical.md", name)
      for name in ["BLUE_CUT", "FLAVOR_CUT", "SODA_FAUCET_CUT", "WHITE_A_CUT", "WHITE_B_CUT",
                   "BLACK_A_CUT", "BLACK_B_CUT", "FOAM_LENGTH", "FOAM_BARE_TOP", "COLLAR_SLEEVE_TAIL"]}
N = 28


def callout(c, title, body, y=680, fill=ICE):
    box(c, 32, y, 548, 65, fill, radius=7)
    text(c, title, 46, y+18, 11, "PlexBold", BLUE if fill == ICE else ORANGE)
    paragraph(c, body, 46, y+25, 520, 10.6, 13.2, max_height=34)


def steps(c, items, y=516):
    for n, item in enumerate(items, 1):
        box(c, 33, y, 21, 21, BLUE, radius=5)
        text(c, str(n), 43.5, y+15, 11.5, "PlexBold", PAPER, "center")
        height = paragraph(c, item, 65, y+1, 508, 11.3, 14.2)
        y += max(height, 21) + 10
    if y > 674:
        raise ValueError(f"Action text crosses gate: y={y}")


def draw_page(c, n, title, subtitle, artist, caption, items, check_title, check,
              source, link=None):
    begin_page(c)
    header(c, n, title, subtitle, N, "DRILL & CUT")
    panel(c, 32, 167, 548, 305)
    with Art(c, 48, 182) as a:
        artist(a)
    paragraph(c, caption, 36, 480, 535, 10.4, 12.6, MUTED, 28)
    steps(c, items)
    callout(c, check_title, check)
    footer(c, n, source, link or SITE+source.split(" | ")[0])
    end_page(c)


def hatch(a, x, y, w, h, step=10):
    for offset in range(-int(h), int(w)+int(h), step):
        x1, y1 = max(0, offset), max(0, -offset)
        x2, y2 = min(w, offset+h), min(h, w-offset)
        if x2 >= x1 and y2 >= y1:
            a.line(x+x1, y+y1, x+x2, y+y2, RULE, .7)


def disc(a, x, y, r=100, face=True, active_register=False):
    a.ellipse(x-r, y-r, r*2, r*2, STEEL)
    if not face:
        return
    for hx in [-D["hole_spacing"]/2, D["hole_spacing"]/2]:
        px = x + hx/(D["disc_diameter"]/2)*r
        a.ellipse(px-8, y-8, 16, 16, PAPER)
    ry = y + D["register_radius"]/(D["disc_diameter"]/2)*r
    a.ellipse(x-4, ry-4, 8, 8, ORANGE if active_register else PAPER,
              ORANGE if active_register else INK)


def bit(a, x, y, length=90, width=18, fill=ORANGE, cone=True):
    a.rect(x-width/2, y, width, length-(8 if cone else 0), fill)
    for yy in range(int(y+6), int(y+length-9), 11):
        a.line(x-width/2+2, yy, x+width/2-2, yy+7, PAPER, .9)
    if cone:
        a.shape([(x-width/2,y+length-8),(x,y+length),(x+width/2,y+length-8)],fill)


def clamp(a, x, y, width=42, height=76, horizontal=False):
    """C frame with visible screw/pad; schematic, no catalogue envelope."""
    if horizontal:
        a.shape([(x,y),(x+width,y),(x+width,y+height),(x,y+height)], None, BLUE, 6, False)
        a.line(x+width/2,y+height,x+width/2,y+height-20,INK,3)
        a.rect(x+width/2-10,y+height-27,20,7,BLUE)
        a.line(x+width/2-12,y+height+6,x+width/2+12,y+height+6,INK,2)
    else:
        a.shape([(x+width,y),(x,y),(x,y+height),(x+width,y+height)], None, BLUE, 6, False)
        a.line(x+width-4,y+height-6,x+width-4,y+height-24,INK,3)
        a.rect(x+width-14,y+height-31,20,7,BLUE)
        a.line(x+width-15,y+height+4,x+width+7,y+height+4,INK,2)


def rod(a, x, y, length=260, diameter=15, fill=STEEL):
    a.rect(x, y, length, diameter, fill)
    a.ellipse(x-3, y, 6, diameter, fill)
    a.ellipse(x+length-3, y, 6, diameter, fill)


def tube(a, x, y, length=230, d=35, fill=COPPER):
    a.rect(x,y,length,d,fill)
    a.ellipse(x-5,y,10,d,fill)
    a.ellipse(x+length-5,y,10,d,fill)
    a.ellipse(x+length-3,y+6,6,d-12,PAPER,INK,.9)


def blade(a, x, y, length=180):
    a.rect(x-6,y,12,length,STEEL)
    for yy in range(int(y+2),int(y+length),7):
        a.shape([(x+6,yy),(x+10,yy+3),(x+6,yy+5)],ORANGE,ORANGE,.6)


def ruler(a, x, y, length=240):
    a.rect(x,y,length,18,ICE,BLUE)
    for xx in range(0,length+1,10):
        a.line(x+xx,y,x+xx,y+(10 if xx%50==0 else 5),BLUE,.8)


def cover_art(a):
    disc(a, 136, 113, 100, active_register=True)
    a.label("ENDCAPS",136,239,11,BLUE,align="center")
    bit(a,279,13,105,22)
    a.arrow(279,130,279,161)
    for i,l in enumerate([170,220,220]):
        rod(a,282,171+i*32,l,12,ORANGE if i==0 else STEEL)
    a.label("RODS / STOCK",385,283,11,BLUE,align="center")
    tube(a,296,58,168,27,COPPER)
    a.line(368,36,368,104,ORANGE,2)
    a.label("SQUARE CUTS",378,125,11,BLUE,align="center")


def chamfer_art(a):
    disc(a,133,131,101)
    a.ellipse(91,116,31,31,ORANGE,ORANGE)
    a.ellipse(98,123,17,17,PAPER)
    a.label("BOTH FACES",133,252,11,BLUE,align="center")
    a.arrow(238,136,274,136)
    a.rect(300,156,180,58,STEEL)
    hatch(a,300,156,180,58)
    a.shape([(371,156),(382,166),(398,166),(409,156),(409,214),(371,214)],PAPER)
    a.shape([(341,54),(439,54),(390,132)],ORANGE)
    a.line(370,88,410,88,PAPER,1)
    a.arrow(390,134,390,148)
    a.label("82°",457,93,15,ORANGE)
    a.label('5/8" or 3/4" body',390,36,12,BLUE,align="center")
    a.label("CLEAR THE RECAST LIP",390,252,11,BLUE,align="center")


def tap_art(a):
    a.rect(70,219,379,20,ICE,BLUE)
    a.ellipse(133,174,256,72,STEEL)
    a.ellipse(237,194,22,9,PAPER)
    bit(a,248,130,77,23)
    a.rect(240,50,16,40,BLUE)
    for yy in range(60,91,5):
        a.line(242,yy,254,yy+3,PAPER,.8)
    a.line(248,90,248,130,BLUE,3)
    a.rect(148,118,200,12,INK)
    a.ellipse(239,109,18,29,STEEL)
    a.arrow(308,80,349,101,ORANGE)
    a.arrow(188,166,147,144,ORANGE)
    a.label("HAND DRIVE",358,108,12,ORANGE)
    a.label("SPRING GUIDE",266,63,11,BLUE)
    a.label("outside face",91,184,11)
    a.label("SPINDLE OFF",83,42,15,BLUE)
    a.label('1/4"-18 NPT',247,265,14,BLUE,align="center")


def register_art(a):
    x,y,r=142,131,113
    disc(a,x,y,r,active_register=True)
    a.line(x-r-5,y,x+r+5,y,BLUE,.8,[4,3])
    a.line(x,y-r-7,x,y+r+9,BLUE,.8,[4,3])
    ry=y+D["register_radius"]/(D["disc_diameter"]/2)*r
    a.dim(x+37,y,x+37,ry)
    a.label(f'{D["register_radius"]:.4f}"',x+47,y+49,12,BLUE)
    a.label("-Y",x-17,y+r+23,11,BLUE)
    a.label("INSIDE FACE UP",x,11,12,BLUE,align="center")
    a.label("center",x+7,y-8,10)
    a.arrow(267,198,311,153)
    a.rect(340,122,125,69,STEEL)
    hatch(a,340,122,125,69)
    a.shape([(385,122),(385,144),(404,155),(423,144),(423,122)],PAPER)
    a.dim(481,122,481,155)
    a.label('0.100"',480,109,11,BLUE,align="right")
    a.dim(481,155,481,191)
    a.label('0.150" remains',403,221,12,BLUE,align="center")
    a.label("9/64-inch blind pocket",400,85,12,ORANGE,align="center")
    a.label("not a through hole",400,251,11,ORANGE,align="center")


def stop_art(a):
    for xx in [0,173,347]:
        a.rect(xx+4,15,162,243,PAPER,RULE)
    a.label("1  TOUCH",17,38,11,BLUE)
    a.rect(21,199,124,26,STEEL)
    bit(a,82,94,105,15)
    a.label("tip at surface",84,246,10,align="center")
    a.label("2  LOCK STOP",185,38,11,BLUE)
    a.rect(190,199,122,26,STEEL)
    a.rect(245,61,15,124,STEEL)
    a.line(246,68,258,68,BLUE,3)
    a.line(246,105,258,105,ORANGE,4)
    a.dim(281,68,281,105)
    a.label('0.100"',294,87,10,BLUE)
    a.label("prove on scrap",257,245,10,align="center")
    a.label("3  CUT TO TIP",359,38,11,BLUE)
    a.rect(368,156,122,67,STEEL)
    a.shape([(406,156),(406,177),(429,190),(452,177),(452,156)],PAPER)
    bit(a,429,85,105,46)
    a.line(369,156,491,156,BLUE,.8,[3,2])
    a.dim(476,156,476,190)
    a.label("the cone counts",429,246,10,align="center")


def edge_art(a):
    a.label("INSIDE / REGISTER FACE",254,30,12,BLUE,align="center")
    a.shape([(96,109),(124,78),(430,78),(458,109),(458,165),(96,165)],STEEL)
    hatch(a,125,80,305,82)
    a.shape([(96,109),(124,78),(147,78),(96,132)],ORANGE,ORANGE)
    a.shape([(430,78),(458,109),(458,132),(407,78)],ORANGE,ORANGE)
    a.arrow(90,54,109,91)
    a.label("lead-in chamfer",33,43,11,ORANGE)
    a.label("OUTSIDE / WELD FACE",254,228,12,BLUE,align="center")
    a.line(96,165,458,165,INK,3)
    a.arrow(62,207,96,165,ORANGE)
    a.arrow(489,207,458,165,ORANGE)
    a.label("burr only",35,245,11,ORANGE)
    a.label("keep this corner",361,265,11,ORANGE)
    a.dim(480,78,480,165)
    a.label('1/4"',500,124,10,BLUE)


def tube_end_art(a):
    a.ellipse(53,91,211,78,STEEL)
    a.rect(53,125,211,90,STEEL)
    a.ellipse(53,72,211,78,STEEL)
    a.ellipse(70,86,177,52,PAPER)
    a.line(83,108,99,99,ORANGE,4)
    a.shape([(20,36),(44,25),(105,99),(89,111)],INK)
    a.arrow(291,119,327,119)
    a.rect(355,82,34,121,STEEL)
    hatch(a,355,82,34,121)
    a.shape([(355,82),(363,78),(367,88)],ORANGE,ORANGE)
    a.arrow(414,55,363,80,ORANGE)
    a.label("remove rolled burr",339,32,11,ORANGE)
    a.dim(355,227,389,227)
    a.label('0.065" wall',373,250,11,BLUE,align="center")
    a.label("ID + OD / BOTH ENDS",160,265,12,BLUE,align="center")
    a.label("light edge break",414,180,11,BLUE)


def rods_art(a):
    data=[(ROD,"CARBONATOR",ORANGE),(RESERVOIR_ROD,"RESERVOIR A",STEEL),
          (RESERVOIR_ROD,"RESERVOIR B",STEEL)]
    for i,(length,label,fill) in enumerate(data):
        yy=58+i*72
        a.label(label,0,yy-17,11,BLUE)
        scaled=length*1.7
        rod(a,153,yy,scaled,12,fill)
        a.dim(153,yy+31,153+scaled,yy+31)
        a.label(f'{length:g} mm',153+scaled/2,yy+47,12,BLUE,align="center")
    a.label('All three: 1/8-inch 316L rod',254,273,12,align="center")


def rod_fit_art(a):
    for xx,title,good in [(36,"SEATS",True),(291,"TOO LONG",False)]:
        a.label(title,xx+92,30,12,BLUE if good else ORANGE,align="center")
        a.rect(xx+15,59 if good else 38,151,28,STEEL)
        a.rect(xx+15,222,151,28,STEEL)
        a.shape([(xx+75,222),(xx+75,231),(xx+90,240),(xx+105,231),(xx+105,222)],PAPER)
        top=87 if good else 66
        a.shape([(xx+75,top),(xx+75,top-9),(xx+90,top-21),
                 (xx+105,top-9),(xx+105,top)],PAPER)
        rod_top=81 if good else 52
        a.rect(xx+80,rod_top,20,234-rod_top,ORANGE)
        a.line(xx+0,59,xx+184,59,BLUE,.8,[3,2])
        if good:
            a.arrow(xx+138,117,xx+99,87,BLUE)
            a.label("tip enters",xx+124,141,10,BLUE)
            a.label("clearance",xx+114,155,10,BLUE)
        else:
            a.dim(xx+178,38,xx+178,59,ORANGE)
            a.label("plate held",xx+119,129,10,ORANGE)
            a.label("above seat",xx+119,145,10,ORANGE)
        a.label("flat rod ends",xx+90,273,10,align="center")


def jet_fit_art(a):
    a.rect(38,148,80,78,STEEL)
    a.rect(70,87,137,73,STEEL)
    a.ellipse(40,207,76,30,STEEL)
    a.ellipse(156,66,60,27,STEEL)
    a.ellipse(147,26,78,31,ORANGE)
    a.ellipse(178,36,17,10,PAPER)
    a.arrow(186,57,186,66)
    a.label("actual elbow land",33,259,11,BLUE)
    a.line(85,243,187,93,BLUE,.9)
    a.rect(304,84,178,58,STEEL)
    a.rect(365,84,56,58,PAPER)
    a.ellipse(347,181,94,32,ORANGE)
    a.dim(347,231,441,231)
    a.label("measure welded OD",393,257,11,BLUE,align="center")
    a.label("actual tapped opening",396,61,11,BLUE,align="center")
    a.arrow(393,174,393,149)
    a.label("loose plate",304,163,10)


def blank_art(a):
    ruler(a,31,32,420)
    rod(a,35,132,402,35,STEEL)
    a.rect(190,184,130,52,ICE,BLUE)
    a.rect(190,102,130,31,ICE,BLUE)
    blade(a,113,71,153)
    a.dim(34,242,110,242)
    a.label("50-60 mm",72,267,12,BLUE,align="center")
    a.arrow(113,232,87,247,ORANGE)
    a.label("handling",20,94,11,ORANGE)
    a.label("blank",20,109,11,ORANGE)
    a.label("long stock in vise",308,270,11,BLUE,align="center")
    a.label("square end",138,93,10)


def fixture_art(a):
    a.label("2 horizontal jaw clamps",20,26,11,BLUE)
    a.label("TOP VIEW",481,26,11,BLUE,align="right")
    a.rect(70,57,370,190,STEEL)
    a.rect(162,76,186,74,STEEL)
    a.rect(162,154,186,74,ORANGE)
    a.ellipse(242,137,30,30,STEEL)
    a.label("rod",257,132,9,BLUE,align="center")
    a.label("fixed jaw",257,105,11,align="center")
    a.label("loose jaw",257,199,11,align="center")
    a.shape([(205,69),(145,69),(145,245),(205,245)],None,BLUE,6,False)
    a.shape([(309,69),(369,69),(369,245),(309,245)],None,BLUE,6,False)
    for xx in [190,320]:
        a.line(xx,245,xx,236,INK,3)
        a.rect(xx-10,228,20,8,BLUE)
        a.line(xx-12,251,xx+12,251,INK,2)
    a.arrow(117,36,190,65,BLUE)
    for xx in [106,406]:
        a.ellipse(xx-10,143,20,20,BLUE,BLUE)
        a.line(xx-4,153,xx+4,153,PAPER,1)
        a.line(xx,149,xx,157,PAPER,1)
    a.arrow(69,273,106,166,BLUE)
    a.arrow(445,273,406,166,BLUE)
    a.label("2 vertical clamps / flange pads",257,278,11,BLUE,align="center")


def jet_drill_art(a):
    a.rect(192,94,124,170,STEEL)
    hatch(a,192,94,124,170)
    a.shape([(236,94),(236,146),(254,157),(272,146),(272,94)],PAPER)
    bit(a,254,25,132,36)
    a.line(152,94,345,94,BLUE,.9,[4,3])
    a.line(152,129,345,129,ORANGE,1.5,[4,3])
    a.dim(355,94,355,157)
    a.label("3-4 mm to tip",370,116,11,BLUE)
    a.label("hole continues",370,148,10,BLUE)
    a.label("past cap back",370,161,10,BLUE)
    a.label("2 mm slice",18,131,12,ORANGE)
    a.arrow(103,132,184,132,ORANGE)
    a.label('1/16-inch stub cobalt',251,12,12,BLUE,align="center")
    a.label("1100 rpm",24,235,14,BLUE)
    a.label("trial start",24,254,11,BLUE)
    a.label("retract for chips + fluid",359,239,10,BLUE)
    a.arrow(272,52,272,30,BLUE)


def slice_art(a):
    rod(a,72,106,331,49,STEEL)
    a.rect(99,82,213,24,ICE,BLUE)
    a.rect(99,155,213,60,ICE,BLUE)
    a.rect(354,127,49,7,PAPER)
    a.ellipse(401,127,4,7,PAPER)
    blade(a,374,21,195)
    a.dim(384,77,403,77)
    a.label("2 mm ±0.2",433,53,12,BLUE,align="center")
    a.label("nominal slice",433,69,10,BLUE,align="center")
    a.arrow(408,160,435,222,ORANGE)
    a.rect(371,245,127,17,ICE,BLUE)
    a.label("free cutoff / tray",432,280,11,ORANGE,align="center")
    a.label("retained rod in vise",160,258,11,BLUE,align="center")
    a.label("low speed / 24 TPI",16,30,12,BLUE)


def jet_clean_art(a):
    for xx,label in [(74,"DRILLED FACE"),(300,"SAWN FACE")]:
        a.ellipse(xx,43,130,130,STEEL)
        a.ellipse(xx+52,95,26,26,PAPER)
        a.label(label,xx+65,205,11,BLUE,align="center")
    a.shape([(208,50),(223,38),(267,108),(246,120)],ORANGE)
    a.arrow(250,120,150,108,ORANGE)
    a.label("light hand turn",232,233,11,ORANGE,align="center")
    a.line(245,246,245,270,BLUE,1)
    a.label("wash / rinse / dry",252,282,12,BLUE,align="center")
    a.label("keep the 1/16-inch passage",252,14,12,BLUE,align="center")


def coupon_art(a):
    a.rect(158,106,184,76,STEEL)
    a.rect(158,177,74,77,STEEL)
    a.ellipse(302,72,65,37,ORANGE)
    a.ellipse(329,81,12,14,PAPER)
    a.line(336,27,336,256,BLUE,2,[5,4])
    a.label("SECTION 1",335,17,12,BLUE,align="center")
    a.label("through jet axis",410,245,11,BLUE,align="center")
    a.arrow(439,222,340,163,BLUE)
    a.ellipse(27,75,75,75,STEEL)
    a.ellipse(57,105,15,15,PAPER)
    a.line(36,138,94,83,ORANGE,2,[4,3])
    a.label("SECTION 2",66,174,12,ORANGE,align="center")
    a.label("another azimuth",67,190,10,ORANGE,align="center")
    a.label("retain both sections + settings",250,280,12,BLUE,align="center")


def copper_shoe_art(a):
    a.shape([(63,95),(366,95),(395,75),(91,75)],COPPER)
    a.rect(63,95,303,94,COPPER)
    a.shape([(366,95),(395,75),(395,169),(366,189)],"#AA6228")
    blade(a,281,40,193)
    a.dim(294,227,366,227)
    a.label("25 mm slice",330,252,12,BLUE,align="center")
    a.dim(420,75,420,169)
    a.label("50 mm",435,125,12,BLUE)
    a.label("1/4-inch edge on table",187,280,11,BLUE,align="center")
    a.label("factory broad face",116,32,12,BLUE)
    a.arrow(189,40,188,134,BLUE)
    a.label("125 FPM / 24 TPI",361,29,12,BLUE,align="center")


def metal_tube_art(a):
    tube(a,38,119,211,41,COPPER)
    a.ellipse(107,87,77,105,None,INK,5)
    a.ellipse(150,118,21,21,ORANGE)
    a.arrow(187,98,200,131,ORANGE)
    a.label("COPPER: wheel cutter",152,42,12,BLUE,align="center")
    a.label("advance lightly",158,225,11,BLUE,align="center")
    a.ellipse(354,86,116,116,STEEL)
    a.ellipse(373,105,78,78,PAPER)
    a.line(368,144,377,153,ORANGE,5)
    a.arrow(311,209,369,147,ORANGE)
    a.label("ID + OD burrs out",408,235,12,BLUE,align="center")
    a.label("metal + particles out",252,281,12,BLUE,align="center")
    a.label("protect the round bore",408,63,11,BLUE,align="center")


def lldpe_art(a):
    tube(a,37,123,411,26,BLUE)
    a.shape([(145,70),(210,86),(274,17),(290,29),(225,104),(210,185),(194,179),(207,107)],INK)
    a.ellipse(201,90,20,20,STEEL)
    a.shape([(231,109),(231,166),(244,140)],ORANGE)
    a.arrow(254,81,254,116,ORANGE)
    a.label("square across the tube",324,73,12,BLUE,align="center")
    a.ellipse(303,205,73,43,BLUE)
    a.ellipse(314,214,51,26,PAPER)
    a.label("round / clean / square",339,271,12,BLUE,align="center")
    a.label("Mudder cutter",104,236,12,BLUE,align="center")
    a.label("check blade is sharp",95,258,10,MUTED,align="center")


def faucet_schedule_art(a):
    a.label("BOTH FINISHES",0,14,11,BLUE)
    rows=[("blue / 1/4-inch",FU["BLUE_CUT"],BLUE),
          ("soda faucet / 3/8-inch",FU["SODA_FAUCET_CUT"],MUTED)]
    for i,(lab,length,fill) in enumerate(rows):
        yy=34+i*43
        a.label(lab,0,yy+11,11)
        a.line(190,yy+4,445,yy+4,fill,9)
        a.label(f'{length:g} mm',506,yy+11,12,BLUE,align="right")
    a.label("BLACK FAUCET",0,135,11,BLUE)
    a.line(190,148,445,148,INK,9)
    a.label("2 flavor tubes",0,155,11)
    a.label(f'2 × {FU["FLAVOR_CUT"]:g}',506,155,12,BLUE,align="right")
    a.label("WHITE FAUCET / FLAVOR",0,203,11,BLUE)
    for yy,flav,w,b in [(224,"A",FU["WHITE_A_CUT"],FU["BLACK_A_CUT"]),
                         (265,"B",FU["WHITE_B_CUT"],FU["BLACK_B_CUT"] )]:
        a.label(flav,0,yy+2,12,BLUE)
        a.line(27,yy-6,140,yy-6,STEEL,10)
        a.line(163,yy-6,324,yy-6,INK,10)
        a.rect(141,yy-14,21,16,STEEL)
        a.label(f'{w:g} white + {b:g} black',504,yy+1,11,BLUE,align="right")


def outlets_art(a):
    a.shape([(78,68),(441,68),(441,167),(78,167)],STEEL)
    for xx,fill in [(190,BLUE),(279,INK),(359,INK)]:
        a.rect(xx-15,12,30,175,fill)
        a.rect(xx-7,12,14,175,PAPER)
        a.line(xx-17,168,xx+17,168,ORANGE,3)
    a.line(50,168,476,168,BLUE,1.1,[5,4])
    a.label("printed tip's outlet face",263,227,13,BLUE,align="center")
    a.arrow(284,212,284,178,BLUE)
    a.label("trim each tube flush here",263,263,13,ORANGE,align="center")
    a.label("soda tube",190,2,10,BLUE,align="center")
    a.label("flavor A",279,2,10,ORANGE,align="center")
    a.label("flavor B",359,2,10,ORANGE,align="center")


def internal_art(a):
    for i,(col,lab,ids) in enumerate([(PAPER,"TAP WATER","water / fluid-1, -2, -3"),
                                     (BLUE,"SODA WATER","carb-1 / carb-2"),
                                     ("#D63A3A","CO2","co2-0 / -1 / -2"),
                                     (INK,"FLAVOR","remaining fluid IDs")]):
        yy=19+i*44
        a.line(11,yy+4,109,yy+4,col,10)
        if col==PAPER:
            a.line(11,yy-1,109,yy-1,INK,.7)
            a.line(11,yy+9,109,yy+9,INK,.7)
        a.label(lab,132,yy+8,11,BLUE)
        a.label(ids,263,yy+8,10)
    a.rect(45,217,111,32,STEEL)
    a.rect(354,217,111,32,STEEL)
    a.rect(134,224,245,17,INK)
    a.dim(135,206,156,206)
    a.dim(354,206,379,206)
    a.dim(156,265,354,265)
    a.label("exposed route + BOTH insertions",251,286,11,BLUE,align="center")


def pvc_art(a):
    a.rect(53,97,79,51,STEEL)
    for xx in [112,124,136]:
        a.shape([(xx,107),(xx+13,97),(xx+13,148),(xx,138)],STEEL)
    a.rect(360,97,82,51,STEEL)
    for xx in [330,343,356]:
        a.shape([(xx,97),(xx+13,107),(xx+13,138),(xx,148)],STEEL)
    a.shape([(123,101),(330,101),(349,108),(349,137),(330,144),(123,144)],ICE,BLUE)
    for xx in range(132,337,16):
        a.line(xx,103,xx+15,141,BLUE,.5)
        a.line(xx,141,xx+15,103,BLUE,.5)
    for xx in [152,318]:
        a.rect(xx-7,94,14,57,STEEL)
        a.rect(xx-9,80,18,14,INK)
    a.dim(123,204,348,204)
    a.label("cut blank includes both barb grips",237,230,12,BLUE,align="center")
    a.label("SAE #6 clamp",251,48,12,BLUE,align="center")
    a.arrow(234,59,158,89,BLUE)
    a.arrow(270,59,321,89,BLUE)
    a.label("water-6 / water-7: 3/8-inch ID reinforced PVC",251,278,11,BLUE,align="center")


def soft_art(a):
    tube(a,30,68,200,37,BLUE)
    a.rect(87,48,87,77,STEEL)
    a.line(98,55,164,119,INK,.8)
    a.line(98,119,164,55,INK,.8)
    a.line(91,53,91,122,ORANGE,2)
    a.label("foam butts / no gaps",131,162,11,BLUE,align="center")
    tube(a,290,70,190,31,STEEL)
    for xx in range(291,475,14):
        a.line(xx,71,xx+19,100,INK,.8)
        a.line(xx,100,xx+19,71,INK,.8)
    a.arrow(356,39,383,39,ORANGE)
    a.arrow(433,39,404,39,ORANGE)
    a.label("braid expands / shortens",389,163,11,BLUE,align="center")
    a.rect(196,226,106,17,INK)
    a.shape([(300,217),(348,217),(348,242),(300,242)],STEEL)
    a.line(351,213,351,247,ORANGE,2)
    a.label("zip ties flush",261,278,12,BLUE,align="center")
    a.label("measure on the real bundle",253,197,12,ORANGE,align="center")


def ribbon_art(a):
    a.rect(48,40,105,192,INK)
    for xx in [48,69,90,111,132,153]:
        a.line(xx,41,xx,230,RULE,.7)
    a.rect(155,40,80,192,INK)
    for xx in [155,175,195,215,235]:
        a.line(xx,41,xx,230,RULE,.7)
    a.line(31,201,257,201,ORANGE,2)
    a.label("pair / same longest leg",141,268,12,BLUE,align="center")
    a.label("5P + 4P shown",141,19,11,BLUE,align="center")
    a.rect(325,39,26,109,INK)
    a.shape([(325,149),(303,186),(288,239),(313,239),(348,149)],INK)
    a.shape([(335,149),(383,169),(424,222),(446,222),(356,145)],INK)
    a.line(284,226,318,226,ORANGE,2)
    a.line(421,209,451,209,ORANGE,2)
    a.label("peel / trim branches",391,270,12,BLUE,align="center")
    a.label("no nicks in insulation",391,281,10,ORANGE,align="center")


def wire_stub_art(a):
    for xx in [0,175,350]:
        a.rect(xx+2,22,160,228,PAPER,RULE)
    a.label("1  FREEZE",15,47,11,BLUE)
    a.shape([(18,77),(38,65),(96,140),(79,153)],STEEL)
    a.line(92,145,122,181,ORANGE,3)
    a.rect(25,184,125,18,STEEL)
    a.label("no wire advance",84,230,10,ORANGE,align="center")
    a.label("2  SNIP",188,47,11,BLUE)
    a.rect(191,184,126,18,STEEL)
    a.line(265,145,294,181,ORANGE,3)
    a.shape([(195,96),(207,88),(285,162),(276,177)],INK)
    a.shape([(208,74),(220,81),(271,177),(259,176)],INK)
    a.label("between nozzle + bead",256,231,9.5,align="center")
    a.label("3  DRESS",362,47,11,BLUE)
    a.rect(367,184,125,18,STEEL)
    a.ellipse(409,118,50,50,INK)
    for theta in range(0,360,30):
        rad=math.radians(theta)
        a.line(434,143,434+24*math.cos(rad),143+24*math.sin(rad),ORANGE,1)
    a.line(434,81,434,120,STEEL,8)
    a.label("stub to bead only",430,231,10,ORANGE,align="center")
    a.label("stainless-only wheel",431,273,10,BLUE,align="center")


def cover(c):
    begin_page(c)
    header(c,1,"Drill & cut","A bench book for the pressure vessel, inlet jet, rods, tubing and harness stock.",N,"DRILL & CUT")
    panel(c,32,152,548,331)
    with Art(c,48,176) as a:
        cover_art(a)
    text(c,"A clean edge. A square cut. A part that fits.",33,521,18,"PlexBold")
    paragraph(c,"Work one operation at a time. Coral shows the cutting action or the fresh edge; blue shows a gauge, clamp or measurement. Pictures explain the setup. Their size is not a cutting template.",33,541,538,13,17,max_height=68)
    callout(c,"BEFORE THE BATCH", "Prove the setup and the first fit. A trial dimension or generated route is identified at the operation that uses it.")
    footer(c,1,"Home Soda Machine | shop guide | 8.5 × 11 inches",SITE+"hardware/assembly/handwork.md")
    end_page(c)


def contents(c):
    begin_page(c)
    header(c,2,"Choose the operation","Read the setup picture, make the cut, then check the part before the next operation.",N,"DRILL & CUT")
    rows=[("03-08","End plates + vessel tube","Chamfer, NPT, blind registers, edge preparation"),
          ("09-10","Three float rods","Blank lengths, square ends and register fit"),
          ("11-17","Water-inlet jet","Fit, handling blank, clamping, drill, slice, section"),
          ("18-19","Copper + metal tubing","Rotator shoe, clean tube and purge-link cuts"),
          ("20-25","Fluid tubing + coverings","Square cuts, faucet, internal routes, PVC, braid"),
          ("26-27","Wire + weld cleanup","Ribbon stock, branches and attached filler wire"),
          ("28","Keep the source at hand","Current procedures and companion guides")]
    yy=165
    for pages,title,desc in rows:
        box(c,32,yy,548,63,ICE if int(pages[:2])%2 else "#F2F4F7",radius=7)
        text(c,pages,46,yy+22,15,"PlexBold",BLUE)
        text(c,title,113,yy+22,15,"PlexBold")
        paragraph(c,desc,113,yy+31,447,10.7,13,MUTED,max_height=26)
        yy+=71
    callout(c,"AT A POWERED CUT", "Read the WEN manual. Clamp work and vise to the table, remove the chuck key, use eye/hearing protection, keep hair/clothing clear and wear no gloves at a running press or saw.")
    footer(c,2,"WEN 4208T manual pp. 6-7; BA4555 manual pp. 6-7",PRESS_MANUAL)
    end_page(c)


def sources_page(c):
    begin_page(c)
    header(c,28,"Keep the source at hand","The current procedures own the dimensions and qualification records. The pictures give the working order.",N,"DRILL & CUT")
    sources=[("End plates / vessel / rods", "hardware/assembly/pressure-vessel.md", "03-10 / 27"),
             ("Jet fit, drilling, cutting and coupon", "hardware/assembly/water-inlet-jet.md", "11-17 / 19"),
             ("Jet split-jaw fixture", "hardware/printed-parts/fixtures/water-inlet-jet/README.md", "13-14"),
             ("Rotator contact shoe", "hardware/printed-parts/fixtures/weld-rotator/README.md", "18"),
             ("Faucet / umbilical cut schedule", "hardware/assembly/faucet-and-umbilical.md", "21-22 / 25"),
             ("Internal fluid routes + fit limits", "hardware/assembly/internal-plumbing.md", "23-24"),
             ("Harness stock + branch schedule", "hardware/assembly/cable-assemblies.md", "26"),
             ("Current wiring run table", "hardware/wiring/ac-wiring-schedule.md", "26")]
    y=168
    for title,path,pages in sources:
        text(c,title,34,y,13,"PlexSemi",BLUE)
        text(c,pages,579,y,10,"PlexSemi",MUTED,"right")
        paragraph(c,path,34,y+8,519,9.8,12,MUTED,max_height=27)
        c.linkURL(SITE+path,(32,H-y-34,580,H-y+13),relative=1)
        y+=54
    text(c,"Companion books",33,615,15,"PlexBold")
    for n,(title,path) in enumerate([
        ("Refrigeration: coil, donor opening, capillary and line work", "hardware/refrigeration-guide/refrigeration-guide.pdf"),
        ("Molds: pouring, cure and trimming foam / silicone", "hardware/mold-guide/mold-guide.pdf"),
        ("Weld rotator: fixture assembly and commissioning", "hardware/weld-rotator-guide/weld-rotator-guide.pdf")]):
        yy=637+n*24
        text(c,title,35,yy,10.8,"PlexSemi",BLUE)
        c.linkURL(DOCS+path.removeprefix("hardware/"),(33,H-yy-5,579,H-yy+13),relative=1)
    paragraph(c,"Print on Letter, one-up, 100% / no scaling. The body is already 98% centered; the broad edge bands are drawn separately for the calibrated Epson borderless output.",33,708,544,10.3,13,MUTED,max_height=30)
    footer(c,28,"Manual document | source hashes: drill-and-cut-guide.sources.json",SITE+"hardware/drill-and-cut-guide/README.md")
    end_page(c)


def build():
    PDF.parent.mkdir(parents=True,exist_ok=True)
    c = canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle("Home Soda Machine - Drill & Cut")
    c.setAuthor("Home Soda Machine")
    cover(c)
    contents(c)
    draw_page(c,3,"Chamfer the port holes","Clear the laser-cut lip before the taper tap touches either plate.",chamfer_art,
              "Four port holes per carbonator. Break the lip on both faces of every 7/16-inch pilot.",
              ["Clamp the plate and backer securely. Fit the JNB Pro 82° countersink with the press unplugged; use its <b>5/8-inch or 3/4-inch body</b>.",
               "Apply Tap Magic EP-Xtra. Run slowly and touch in lightly; crowding the five-flute cutter makes it chatter.",
               "Turn the plate over and clear the other face. Remove chips with the spindle stopped, then inspect all four hole edges."],
              "CHECK THE LIP", "The recast lip is gone and the tap has a clean square start. This step does not enlarge the pilot to make a fitting pass.",
              "hardware/assembly/pressure-vessel.md | step 1")
    draw_page(c,4,"Hand-tap from outside","The drill press holds the spring guide square. Your tap wrench supplies the drive.",tap_art,
              "1/4-inch-18 NPT. Two holes in each plate, entered from that plate's outside face.",
              ["Mark the outside face and secure the disc. With the spindle <b>off</b>, align the Brown & Sharpe spring guide with the tap axis.",
               "Lubricate the LingGan M35 taper tap with Tap Magic. Turn the wrench by hand; clear chips and re-lubricate as cutting requires.",
               "Check with the actual elbow. Target <b>4.5 turns of engagement</b>, snug-firm with <b>2-3 threads showing</b>; verify the final clock on a trial before the batch."],
              "FIRST FIT BEFORE FORTY PORTS", "The production tapping fixture and repeatable engagement still need a recorded trial. Tap depth is decided by the fitting check, not a turns-only shortcut.",
              "hardware/assembly/pressure-vessel.md | step 1")
    draw_page(c,5,"Locate the blind register","Both identical plates get the same pocket in their inside face.",register_art,
              f'The center is (0, -{D["register_radius"]:.4f} in), {D["register_radius"]*25.4:.3f} mm from the disc center, perpendicular to the two-port axis.',
              ["Put the <b>inside face up</b>. Find the disc center and the axis through the two port centers; lay out the perpendicular -Y axis.",
               f'Mark the register center <b>{D["register_radius"]:.4f} inches / {D["register_radius"]*25.4:.3f} mm</b> from the disc center, clear of both ports.',
               "Align the stopped <b>9/64-inch M35, 135° split-point</b> drill to the mark, then clamp the disc and backer. Recheck the tip after tightening."],
              "SAME POCKET, TWO JOBS", "The bottom pocket seats the rod for its tack; the top pocket captures its tip. The pocket is blind because the end plate is the pressure boundary.",
              "hardware/assembly/pressure-vessel.md | step 1")
    draw_page(c,6,"Prove the depth stop","0.100 inch means the drill-point tip, including the cone at the bottom.",stop_art,
              'A 0.100-inch tip depth in a 0.250-inch plate leaves 0.150 inch intact.',
              ["With the press stopped, touch the drill point to the inside surface. Set and lock the stop for <b>0.100 inch of tip travel</b>.",
               "Prove the depth on a scrap disc before a real end plate. Use the slowest WEN setting, <b>about 740 rpm</b>, with Tap Magic.",
               "Drill each clamped plate to the proved stop, clearing chips and renewing fluid. Remove the burr without increasing the pocket depth."],
              "KEEP THE BACK FACE INTACT", "Stop if the setup moves or the depth is uncertain. A through-hole rejects this pressure-boundary plate; it is not a weld repair step.",
              "hardware/assembly/pressure-vessel.md | step 1")
    draw_page(c,7,"Two faces, two edges","The plate needs a lead-in inside and a sharp fillet root outside.",edge_art,
              "Section through the perimeter. Coral highlights the inside lead-in; the outside corner remains crisp.",
              ["Keep track of the register face. Run the Noga NG8150 around the <b>inside-face OD edge</b> to make the insertion lead-in.",
               "On the <b>outside-face OD edge</b>, remove the burr only. Keep the corner where the outer face meets the tube bore crisp.",
               "Inspect and clean both edges. Keep stainless-only abrasives separate from anything used on carbon steel."],
              "PRESERVE THE WELD ROOT", "A broad outside chamfer opens the gap the laser must bridge. Coarse grinding can round this corner even when the plate still looks tidy.",
              "hardware/assembly/pressure-vessel.md | steps 1, 3")
    draw_page(c,8,"Deburr the vessel tube","Prepare both loose tube ends while you can turn the tube freely.",tube_end_art,
              'The vessel is 5-inch OD × 0.065-inch wall × 6-inch cut length. The closure fillet sits 1/4 inch below the cut rim.',
              ["Check the received cut ends. Use the Noga to remove rolled saw burrs from <b>ID and OD at both ends</b>; keep the edge break light.",
               "Check that the plate slips into the bore and seats at its 1/4-inch recess. A rim burr must not catch and hold it above the seat.",
               "Clean the tube's bore band below each end and the plate's outside face. Keep the actual rim and end-cap seat square for the rotator checks."],
              "SQUARENESS IS A FIT CHECK", "The rotator's radial and face runout gates still apply. If a received end needs squaring, support the tube and check the corrected length and seat before welding.",
              "hardware/assembly/pressure-vessel.md | step 3")
    draw_page(c,9,"Cut the three float rods","One carbonator blank and one rod for each flavor reservoir.",rods_art,
              'Square-cut and deburr 1/8-inch 316L stock. The carbonator value is a starting blank; the reservoir value already includes end clearance.',
              ["Mark one <b>carbonator blank</b> and two <b>reservoir rods</b> to the lengths above. Identify each before the cut.",
               "Set a square cut at the BA4555. Secure the retained rod in the vise with support that prevents rocking; keep the cutoff free of the blade and stop.",
               "Cut, deburr both flat ends and measure each rod. The vessel rod is hand-fitted at the next step; keep the two reservoir rods paired with their bodies and caps."],
              "NO CAP HELD OPEN", "Rod capture locates a cap; it never supplies its closing stop. Check both end registers and the seated cap rather than accepting the cut length alone.",
              "hardware/assembly/handwork.md | float rods")
    draw_page(c,10,"Hand-fit the carbonator rod","Conical pocket bottoms make the actual seat-to-seat span shorter than the tip-depth arithmetic.",rod_fit_art,
              f'The {ROD:g} mm blank is hand-fitted to the actual two plates before the bottom tack.',
              ["Seat the flat-ended rod in the bottom pocket. Check the real upper plate at its specified <b>1/4-inch recess</b> before committing the tack.",
               "Shorten and deburr the rod as needed so its tip enters the top pocket while the plate reaches its full seat. Leave clearance at the top.",
               "Repeat the seating check with the actual float and parts. The reservoir rods are captured by printed bosses and are <b>not welded</b>."],
              "A POCKET DOES NOT SET THE RECESS", "Positive tip engagement and a fully seated plate must both be present. Open the top pocket to 5/32 inch only if actual binding calls for it; keep it blind.",
              "hardware/assembly/pressure-vessel.md | steps 2, 5")
    draw_page(c,11,"Measure before making jets","The nominal 9.5 mm × 2 mm cap is a fabrication-trial candidate.",jet_fit_art,
              "Use the actual rod, elbow and a loose tapped plate. CAD elbow dimensions do not establish this fit.",
              ["Measure rod OD, elbow tip OD, bore and flat annular land. Check that the cap covers the bore and seats flat with a root that can be fused.",
               "Measure the tapped plate's clear opening and the finished welded OD. Check made-up elbow depth, clock and headspace projection.",
               "Record the accepted fit before cutting a batch. A cap that will not clear the plate returns to design; it does not justify a deeper tap."],
              "TRIAL / UNQUALIFIED", "The cap fit, drilled/cut repeatability and weld root have no accepted measurements recorded. Use a spare elbow and retain the trial records.",
              "hardware/assembly/water-inlet-jet.md | measured fit")
    draw_page(c,12,"Cut a handling blank","Keep the full 400 mm jet rod off the upright drill-press setup.",blank_art,
              "A 50-60 mm handling blank gives the two-piece fixture a manageable first setup.",
              ["Mark <b>50-60 mm</b> on the nominal 9.5 mm 316 rod. Set the BA4555 cut square and clamp the long retained stock in its vise.",
               "Use the 24 TPI M42 blade trial at low speed. Support the short blank's landing and keep the cutoff free to fall.",
               "Deburr both ends flat. Clear chips from the fixture floor before the blank goes into the drill jaws."],
              "KEEP ENOUGH ROD TO GRIP", "Retire this handling blank before it falls below 40 mm, or earlier if chuck clearance requires it. Keep the short remainder as coupon stock.",
              "hardware/assembly/water-inlet-jet.md | step 1")
    draw_page(c,13,"Clamp the jet blank","Two clamps close the split jaws; two more secure the base and backer to the table.",fixture_art,
              "Top schematic. The rod seats on a solid floor. Check real clamp frames and the stopped quill through the full drilling stroke.",
              ["Seat the flat blank on the solid floor. Tighten the two <b>horizontal jaw clamps</b> evenly until it cannot turn, rock or lift; the jaw split stays visible.",
               "Align the stopped drill after tightening the jaws, then secure the two <b>vertical table clamps</b> against a solid table edge, trapping the base and backer.",
               "Turn the chuck by hand and lower the stopped quill through the intended stroke. Prove grip and clearance on scrap before caps."],
              "PRINTED GRIP NEEDS A TRIAL", "The jaw fixture is CAD-checked, physically untested. Stop at stock or fixture motion, jaw opening, rubbing or drill wander; do not solve poor grip with drilling force.",
              "hardware/printed-parts/fixtures/water-inlet-jet/README.md")
    draw_page(c,14,"Drill the jet first","The cap stays on its handling blank until its short axial passage is drilled.",jet_drill_art,
              "The drill's full-diameter hole must continue past the proposed 2 mm slice. Do not drill the whole handling blank.",
              ["Align the <b>1/16-inch stub cobalt drill</b> to the rod axis. Verify concentric chuck grip and all four clamps before powering the press.",
               "Begin at the WEN's <b>1100 rpm trial setting</b> with Tap Magic. Feed to make chips; retract to clear them and renew fluid.",
               "Drill about <b>3-4 mm deep</b>. Stop for squealing, heat, stalled cutting or wandering; correct the setup before continuing."],
              "A STARTING SETTING", "1100 rpm is not an accepted production recipe. Record the setting and the cut that actually work with this stock, drill and clamping setup.",
              "hardware/assembly/water-inlet-jet.md | step 1")
    draw_page(c,15,"Saw the 2 mm cap slice","Take the drilled blank out of the printed jaws and hold the retained rod in the saw vise.",slice_art,
              "Put the drilled end on the cutoff side. Do not trap a thin slice between the moving blade and a stop.",
              ["Set a square cut with the <b>24 TPI M42 blade at low speed</b>. Set the nominal slice to <b>2 mm ±0.2 mm</b>; account for the stop's blade reference and kerf.",
               "Clamp the retained rod securely. Let the cap slice fall clear into a tray; do not hold the 2 mm slice by hand.",
               "Measure thickness and squareness. Reject a wedge or damaged slice. Clean and reseat the remaining blank, then realign it for the next drilled hole."],
              "NO FILLER HIDES A BAD SLICE", "The cap must sit flat on the elbow. A wedge-shaped cut opens a weld gap and changes the passage length; it is rejected at this cutting step.",
              "hardware/assembly/water-inlet-jet.md | step 1")
    draw_page(c,16,"Clean both jet faces","Both ends of the bore are accessible now, before welding.",jet_clean_art,
              "Inspect under magnification. A small edge burr is removed by hand, with the passage kept consistent.",
              ["Inspect the drilled and sawn faces. Remove loose saw/drill burrs with a <b>light hand turn</b> of a larger owned drill if needed.",
               "Keep the 1/16-inch passage and exit edge intact. Do not power-countersink this thin cap or turn a burr cleanup into a larger jet.",
               "Wash away cutting fluid and loose particles, rinse and dry. Check that the cap sits on the measured elbow land without rocking."],
              "LOOK THROUGH, THEN FIT", "Reject a visibly distorted or obstructed hole. A post-weld drill-through repair changes this geometry and requires its own recorded acceptance.",
              "hardware/assembly/water-inlet-jet.md | step 1")
    draw_page(c,17,"Section the welded trial","An outside bead cannot show whether the bore-side root fused.",coupon_art,
              "One cut passes through the jet axis. A second azimuth samples a tack or restart region.",
              ["Secure the spare elbow body in the bandsaw vise. Section the trial cap/elbow <b>through the jet axis</b>, retaining the cut pieces.",
               "Make the second section at a different azimuth. Dress the cut faces on a flat support using owned fine abrasive stock, then inspect and photograph under magnification.",
               "Keep sections with the fit and weld settings record. Reject a bore-connected unfused interface, cracking, root scale or distorted passage."],
              "SECTION READABILITY IS REQUIRED", "A root that cannot be read remains unresolved. Sectioning samples the joint; appearance, pressure retention or a good jet stream do not prove full root fusion.",
              "hardware/assembly/water-inlet-jet.md | step 3")
    draw_page(c,18,"Cut the rotator contact shoe","One crosscut from the acquired nominal 1/4 × 2 inch C110 bar.",copper_shoe_art,
              "Stand the stock's 2-inch mill width vertically. The factory broad face contacts the tube; no copper hole or thread is made.",
              ["Put the <b>1/4-inch edge on the BA4555 table</b>, broad face vertical. Clamp the retained bar and mark one <b>25 mm slice</b>.",
               "Use the installed <b>24 TPI M42 blade at 125 FPM</b> with light downfeed, letting the gullets clear. Keep the cutoff free.",
               "Deburr the fresh cut without rounding the factory contact face. Stand the 50 mm stock width vertically in the ground-shoe shelf."],
              "THE MILL FACE IS THE CONTACT", "The shoe is nominally 6 × 25 × 50 mm. The saw cut seats on its printed shelf; it is not the sliding electrical contact surface.",
              "hardware/printed-parts/fixtures/weld-rotator/README.md")
    draw_page(c,19,"Keep metal tube cuts clean","Square ends and clear bores matter on copper refrigerant lines and the stainless purge links.",metal_tube_art,
              "Copper: RIDGID Model 150 wheel cutter. Stainless purge links: cut to the actual bench arrangement, then deburr and clean.",
              ["Measure the needed run and fitting engagements before cutting. Follow the <b>refrigeration guide</b> for coil stock, donor opening and capillary cuts.",
               "Cut copper square with light cutter advances; remove ID/OD burrs and every particle without gouging or narrowing the bore. Protect open ends from debris.",
               "For the jet purge fixture, cut two clean <b>1/4-inch OD stainless links</b> to suit the bench. Close the cylinder and depressurize before cutting the 6 mm regulated hose square."],
              "CHARGED LINES HAVE THEIR OWN PROCEDURE", "Use the refrigeration book before opening a donor. Capillary tubing takes its dedicated cutter. Fit stainless compression links to their maker's assembly instructions.",
              "hardware/assembly/water-inlet-jet.md | step 2",DOCS+"refrigeration-guide/refrigeration-guide.pdf")
    draw_page(c,20,"Square-cut the plastic tube","One clean cutting plane, with the bore round and the sealing surface undamaged.",lldpe_art,
              "Mudder cutter for 1/4-inch and 3/8-inch OD LLDPE. The printed razor miter box is a separate, untested tool trial.",
              ["Check the blade. Measure and mark the cut; place the tube square in the Mudder cutter without squeezing it out of round.",
               "Make a clean cut across the tube. Inspect the end for angle, deformation and burrs; recut a damaged end before it reaches a fitting.",
               "Allow the real fitting's full insertion at each end, mark engagement, push fully home and tug-test. Keep the smooth outside sealing surface free of scores."],
              "END CONDITION BEFORE LENGTH", "A nominally correct length with a slanted, oval or scored end is not ready for a push-fit joint. Use the received fitting's insertion requirement.",
              "hardware/assembly/internal-plumbing.md | tubing cuts")
    draw_page(c,21,"Cut the faucet tube set","Choose Black or White before pulling the flavor tubes from their reels.",faucet_schedule_art,
              "Lengths in mm. White faucet flavor runs join white upper tubes to black lower tubes using the staggered PP0408W unions.",
              ["Cut the <b>blue 1/4-inch umbilical</b> and the finish's <b>3/8-inch soda faucet tube</b> to the common lengths shown.",
               "For Black, cut two full black flavor tubes. For White, cut the separate A/B white and black pairs shown; keep the two union stations identified.",
               "Square-cut every end. Route to the actual faucet and inspect the tails before the outlet trim; the blue tube begins at the Westbrass's lower compression port."],
              "REACH IS PART OF THE CUT", "These factory cuts include installation reach allowance. Do not substitute the shorter nominal installed lengths or equalize White faucet A/B pieces.",
              "hardware/assembly/faucet-and-umbilical.md | step 1")
    draw_page(c,22,"Trim the three outlets flush","The printed tip supports the tubes. The tubes remain the fluid passages.",outlets_art,
              "Section schematic: one soda outlet and two flavor outlets share the printed tip's dispense-face plane.",
              ["Route the 3/8-inch soda tube and both flavor tubes through their actual faucet channels. Fit the tip and verify that all three tubes pass freely.",
               "Use a clean square cut to trim <b>each outlet flush with the printed tip</b>. Keep the blade away from the display, ribbon and printed sealing/support faces.",
               "Inspect each outlet for an open round bore and a clean end. Check that the tubes and ribbon clear the seated display underside."],
              "TRIM AT THE OUTLET PLANE", "The factory tail allowance is retained. This is the three outlet-end trim; the lower bare tails still need their full installed reach and square push-fit ends.",
              "hardware/printed-parts/faucet/faucet-shell/ASSEMBLY.md")
    draw_page(c,23,"Cut internal tubes by route","A developed exposed path is not a blank length until both engagements are included.",internal_art,
              "Use the current fluid topology and internal-plumbing procedure. Identify each segment before installation.",
              ["Pull from the carrying fluid's reel: <b>white tap water, blue soda water, red CO2, black flavor</b>. Fluid-1, -2 and -3 are white; tag all fluid IDs.",
               "Cut established runs from their reported cut length. Bench-fit the four moving bowed tee links and the warm CO2 routes where fitting reaches and travel remain unqualified.",
               "Include both received-fitting insertions even at zero exposed span. Keep the PRV vent mouth flush with the shell flank, its relief chase clear, and every finished end square."],
              "NO FORCED ROUTE", "Keep stock bend radii and collet axes. Resolve the documented fluid-2 clearance before assembly; a shorter cut is not a clearance repair. Tug-test each seated end.",
              "hardware/assembly/internal-plumbing.md | all tube routes")
    draw_page(c,24,"Fit the PVC hose blanks","The pump hoses need their exposed turn plus the grip over both actual barbs.",pvc_art,
              "Water-6 discharge and water-7 suction are reinforced 3/8-inch ID PVC, each with two SAE #6 clamps.",
              ["Measure the received pump and adapter barb engagements. Add them to the actual exposed route; the generated ~49 mm / ~48 mm paths are <b>not complete hose cuts</b>.",
               "Cut square, slide on both clamps, then seat the hose on both barbs. Preserve at least the documented <b>15.9 mm bend radius</b> and check an open bore.",
               "Cut the separate clear-PVC ASSE vent stub to its placed overhang so it drips bare to the pan. Cut the LLDPE funnel drain stub to <b>25.79 mm</b>."],
              "FIT EACH HOSE FAMILY", "Pump hose is reinforced PVC; ASSE vent is a separate 1/4-inch-ID clear PVC stub. The vent remains open to atmosphere and is not connected to a drain.",
              "hardware/assembly/internal-plumbing.md | step 2")
    draw_page(c,25,"Cut coverings on the bundle","Foam butts tightly. Expanded braid takes up length, so measure it fitted.",soft_art,
              "The standard umbilical uses five foam/braid segments; internal soda risers use one continuous insulation piece per actual run.",
              ["For the umbilical, fit the blue tube's foam over the prescribed <b>1338 mm</b> coverage with the <b>127 mm top</b> and <b>75 mm tail</b> left bare. Butt segments without gaps.",
               "Measure each braid segment expanded over the actual tube/ribbon/foam pack before cutting; the top segment extends past its foam over the union stations.",
               "Cut internal carb-1/carb-2 insulation to their complete runs before the collets close. Finish harness braid ends with heat-shrink, and flush-cut all zip-tie tails."],
              "TRIM FOAM AFTER CURE IN THE MOLD GUIDE", "Molded foam flash and silicone trimming belong with their cured parts. Keep knives off tubes, gasket seats and printed bearing faces when cutting any covering.",
              "hardware/assembly/faucet-and-umbilical.md | step 3")
    draw_page(c,26,"Cut the harness stock","Make the loom blank to its longest leg, then peel and trim the shorter branches.",ribbon_art,
              "Use the current cable-assembly and wiring run tables. A ribbon pair is two ribbons, laid edge-to-edge, cut to the same blank length.",
              ["Choose the wafer's specified <b>22 AWG 3P/4P/5P ribbon pair</b>. Measure the longest leg plus the actual service loop, then cut both ribbons together.",
               "Peel branch conductors without nicking insulation; trim the shorter legs to their endpoints. The 3P/5P web tear behavior still needs the stated stock check.",
               "Use <b>16 AWG bulk</b> for the specified mains/trunk runs, <b>18 AWG SJOOW</b> for the compressor lead, and <b>28 AWG 4P</b> for the umbilical. Strip to the received terminal's barrel length."],
              "LABEL THE LOOM BEFORE TERMINATION", "DC-5 fixed half is 350 mm 22 AWG 4P; cartridge leads are four ~100 mm pieces. Keep the current donor's unverified external connector decision out of a speculative final cut.",
              "hardware/assembly/cable-assemblies.md | cut and strip")
    draw_page(c,27,"Snip the attached filler wire","At the end of a bead, keep the gun where it stopped while the wire is detached.",wire_stub_art,
              "One hand holds the stopped gun; the other brings the diagonal-cutter tips between wire nozzle and bead.",
              ["End the weld and hold the head at its stopping position. <b>Do not feed extra wire</b> from the feeder before detaching it.",
               "Put the Knipex 70 11 110 tips between the nozzle and bead and snip the attached wire. Remove the freed head without lasering the stub off.",
               "With the work supported and weld operation stopped, dress the stub with a stainless-only <b>1/4-inch-shank flap wheel in the drill</b>, down to the bead and no further."],
              "PRESERVE THE CRATER FOR INSPECTION", "The end-of-bead crater can contain a crack. Grinding into the bead can smear it shut before dye penetrant; do not grind a crater away to make the weld look finished.",
              "hardware/assembly/pressure-vessel.md | step 3")
    sources_page(c)
    c.save()
    canonical=publish(PDF,GUIDE,"Drill & cut bench guide",
                      "28 illustrated Letter pages: endcaps, rods, inlet jet, metal and fluid tubing, coverings and harness stock.",
                      N,SOURCES,extra={"external_sources":{"WEN 4208T":PRESS_MANUAL,"WEN BA4555":SAW_MANUAL},
                                      "external_checked":"2026-10-04",
                                      "numeric_inputs":{"endcap":D,"carbonator_rod_blank_mm":ROD,
                                                        "reservoir_rod_mm":RESERVOIR_ROD,"faucet_cuts_mm":FU}})
    print(canonical.relative_to(ROOT))
    print(f"{N} pages / Letter / vector art / manual build")


if __name__ == "__main__":
    build()
