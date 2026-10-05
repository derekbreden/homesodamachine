"""Hand-authored Letter guide for the silicone funnel and three cold-core pours.

Run by hand. No CAD import, scene render, metadata sync or appliance-build target.
The drawings teach handling and order; named dimensions govern the operation.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/assembly-guides"))
from common import *

PDF = ROOT / "output/pdf/mold-guide.pdf"
GUIDE = ROOT / "hardware/mold-guide"
TOTAL = 22
TEAL = "#C9EEEE"
GOLD = "#EEDDB2"
FOAM = "#FFE2CC"
SKIN = "#F1D5B6"

SOURCES = [
    "hardware/printed-parts/zone-c/funnel-mold/README.md",
    "hardware/printed-parts/zone-c/funnel-mold/silicone.md",
    "hardware/printed-parts/zone-c/funnel-mold/design.json",
    "hardware/printed-parts/zone-c/funnel-mold/rod-check.json",
    "hardware/printed-parts/zone-c/funnel-mold/print-log.md",
    "hardware/printed-parts/zone-c/funnel/wall-review.json",
    "hardware/assembly/cold-core.md",
    "hardware/printed-parts/cold-core/foam-shell/README.md",
    "hardware/printed-parts/cold-core/copper-plugs/README.md",
    "hardware/mechanical-qualification/core-and-faucet-heatsets.json",
    "hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md",
    "hardware/printed-parts/zone-c/funnel-mold/containment-review.json",
]
F = json.loads((ROOT / SOURCES[2]).read_text())
if not math.isclose(F["finish_allowance_mm"], .30):
    raise ValueError("Review changed shell finishing allowance")
for value, expected in [(F["rod"]["diameter_mm"], 6.0),
                        (F["rod"]["length_mm"], 25.0),
                        (F["rod_support"]["guide_diameter_mm"], 6.4),
                        (F["rod_socket"]["diameter_mm"], 6.4),
                        (F["rod_socket"]["depth_mm"], 1.5)]:
    if not math.isclose(value, expected):
        raise ValueError("Review changed straight-rod dimensions before rebuilding")
if not F["rod_support"]["guide_open"]:
    raise ValueError("The rod guide must open into the dry back")
VOLUME = F["volume_ml"]["funnel"]
MASS = VOLUME * 1.13  # Planning estimate from the project silicone material record.
MANUFACTURERS = {
    "BBDINO 40A": "https://bbdino.com/products/bbdino-40a-clear-silicone-mold-making-trial-kit-gp-platinum-cure-high-hardness",
    "Ease Release 200": "https://www.smooth-on.com/products/ease-release-200/",
    "Sealers and release": "https://www.smooth-on.com/page/sealers-releases/",
    "Degassing example": "https://www.smooth-on.com/tutorials/making-piece-cut-block-mold/vacuum-de-gassing/",
    "FSD pour foam": "https://fiberglasssupplydepot.com/Expandable-Polyurethane-Pour-Foam-2lb.html",
    "FSD foam SDS": "https://fiberglasssupplydepot.com/pour-foam-sds",
}


def start(c, n, title, subtitle, group):
    begin_page(c)
    header(c, n, title, subtitle, TOTAL, f"MOLD OPERATIONS / {group}")


def finish(c, n, source, local):
    footer(c, n, source, "https://github.com/derekbreden/homesodamachine/blob/main/hardware/" + local)
    end_page(c)


def actions(c, rows, y=506):
    y = min(y, 506)
    for i, (heading, copy) in enumerate(rows, 1):
        badge(c, i, 34, y, heading, size=13)
        paragraph(c, copy, 65, y + 26, 493, 11.2, 13.6, max_height=28)
        y += 59
    return y


def gate(c, heading, copy, y=682, tone=ORANGE):
    box(c, 32, y, 547, 61, ICE if tone == BLUE else "#FFF0E7", radius=7)
    box(c, 32, y, 5, 61, tone)
    text(c, heading.upper(), 45, y + 17, 10.4, "PlexBold", tone)
    paragraph(c, copy, 45, y + 25, 518, 10.6, 12.6, max_height=34)


def figure(c, callback, y=155, height=330):
    drawing_height = height
    height = min(height, 334)
    scale = (height - 28) / (drawing_height - 28)
    panel(c, 32, y, 547, height)
    with Art(c, 48 + 512 * (1-scale) / 2, y + 14, scale=scale) as a:
        callback(a)


def step_label(a, n, caption, x, y, width=140):
    a.rect(x, y, 20, 20, BLUE, None)
    a.label(str(n), x + 10, y + 14, 11, PAPER, "PlexBold", "center")
    a.label(caption, x + 28, y + 14, 10, INK)


def cup(a, x, y, width=70, height=90, level=.35, fill=ORANGE, label=None):
    a.shape([(x, y), (x + width, y), (x + width - 8, y + height),
             (x + 8, y + height)], PAPER)
    if level:
        dy = height * (1 - level)
        side = 8 * (1 - level)
        a.shape([(x + side, y + dy), (x + width - side, y + dy),
                 (x + width - 8, y + height), (x + 8, y + height)], fill, None)
    a.line(x, y, x + width, y)
    for dy in range(18, int(height), 18):
        a.line(x + width - 10, y + dy, x + width - 3, y + dy, MUTED, .6)
    if label:
        a.label(label, x + width / 2, y + height + 20, 10, INK, align="center")


def bottle(a, x, y, label, fill=STEEL):
    a.rect(x + 10, y, 35, 12, INK, None)
    a.shape([(x + 10, y + 12), (x + 45, y + 12), (x + 45, y + 22),
             (x + 55, y + 33), (x + 55, y + 101), (x, y + 101),
             (x, y + 33), (x + 10, y + 22)], fill)
    a.rect(x + 7, y + 46, 41, 33, PAPER, None)
    a.label(label, x + 27.5, y + 68, 16, INK, "PlexBold", "center")


def shell(a, x, y, width=190, depth=110, core=False, color_=None):
    """Oblique half-mold schematic with forming face up."""
    color_ = color_ or (GOLD if core else TEAL)
    dx = 32
    a.shape([(x, y), (x + width, y), (x + width + dx, y + depth),
             (x + dx, y + depth)], color_)
    a.shape([(x + dx, y + depth), (x + width + dx, y + depth),
             (x + width + dx, y + depth + 10), (x + dx, y + depth + 10)], color_)
    if core:
        a.shape([(x + 37, y + 30), (x + width - 24, y + 30),
                 (x + width - 3, y + depth - 22), (x + 56, y + depth - 22)], GOLD)
        a.line(x + 37, y + 30, x + 40, y + 16, INK)
    else:
        a.shape([(x + 32, y + 19), (x + width - 26, y + 19),
                 (x + width - 4, y + depth - 20), (x + 54, y + depth - 20)], PAPER)
        a.shape([(x + 50, y + 33), (x + width - 40, y + 33),
                 (x + width - 21, y + depth - 32), (x + 67, y + depth - 32)], TEAL)
        a.rect(x + width/2-5, y + depth-43, 32, 18, PAPER)
    for px, py in [(x+18,y+9),(x+width/2,y+9),(x+width-13,y+9),
                   (x+width+13,y+depth/2),(x+width+18,y+depth-5),
                   (x+width/2+29,y+depth-5),(x+42,y+depth-5),(x+19,y+depth/2)]:
        a.ellipse(px-3,py-2,6,4,PAPER)


def steel_rod(a, x, y, height=160, fill=STEEL):
    """Stock straight steel rod, shown at its actual diameter/length ratio."""
    scale = height / F["rod"]["length_mm"]
    diameter = F["rod"]["diameter_mm"] * scale
    a.rect(x-diameter/2, y, diameter, height, fill)
    return scale


def mold_section(a, x=15, y=110, width=465, include_core=True, liquid=False,
                 include_pin=True):
    """Reviewed section proportions: 6 mm silicone, about 5 mm PETG backing.

    Coordinates are a hand-authored section in millimetres, not CAD imports.
    The block and neck are thicker than the ramp; the steel rod stays inside
    the bowl height. The 0.20 mm radial guide clearance is omitted at this scale.
    """
    s = width/211
    nc = 1.85
    def point(px, py):
        return x+(px+105.5)*s, y+py*s
    def shape(points, fill, stroke=INK):
        a.shape([point(px, py) for px, py in points], fill, stroke)
    # The cavity's forming surface follows the finished brim/collar/ramp/block.
    cavity_inner = [(-89.5, 0), (-89.5, 6), (-82.5, 6), (-82.5, 23.486),
                    (-81.5, 29.5), (nc-18, 42), (nc-18, 48.95),
                    (nc-3.2, 48.95), (nc-3.2, 50.45),
                    (nc+3.2, 50.45), (nc+3.2, 48.95),
                    (nc+18, 48.95), (nc+18, 42), (81.5, 29.5),
                    (82.5, 23.486), (82.5, 6), (89.5, 6), (89.5, 0)]
    cavity_outer = [(105.5, 0), (105.5, 5), (94.5, 5), (94.5, 11),
                    (87.5, 11), (87.5, 23.486), (86.5, 34.5),
                    (nc+23, 47), (nc+23, 55.45),
                    (nc-23, 55.45), (nc-23, 47), (-86.5, 34.5),
                    (-87.5, 23.486), (-87.5, 11), (-94.5, 11),
                    (-94.5, 5), (-105.5, 5), (-105.5, 0)]
    shape([(-105.5, 0), *cavity_inner, *cavity_outer], TEAL)
    # This pale band is the casting space; coral is liquid silicone on pour pages.
    shape(cavity_inner, ORANGE if liquid else ICE, None)
    if include_core:
        # The core forming face is six millimetres inboard of the collar wall.
        wet = [(-89.5, -.3), (-76.5, -.3), (-76.5, 23.486),
               (nc-3.0, 37.685179), (nc+3.0, 37.685179),
               (76.5, 23.486), (76.5, -.3), (89.5, -.3)]
        shape([(-105.5, -5), (105.5, -5), (105.5, 0),
               (89.5, 0), *reversed(wet), (-89.5, 0), (-105.5, 0)], GOLD)
        dry = [(-71.5, -5), (71.5, -5), (71.5, 17.486),
               (nc+3.0, 31.685179), (nc-3.0, 31.685179), (-71.5, 17.486)]
        shape(dry, PAPER, None)
        # Straight open guide: the stock rod is accessible from the dry back.
        bx, by = point(nc-8.2, 29.685179)
        a.rect(bx, by, 16.4*s, 7.7*s, GOLD)
        shape([(nc-3.2, 29.685179), (nc+3.2, 29.685179),
               (nc+3.2, 37.685179), (nc-3.2, 37.685179)],
              ORANGE if liquid else PAPER)
    if include_pin:
        px, py = point(nc, 25.45)
        steel_rod(a, px, py, 25*s, STEEL)
    return {"point": point, "scale": s}


def cap_section(a, x=20, y=150, width=455, top=True, foam=False):
    a.rect(x,y+89,width,27,STEEL)
    a.rect(x+12,y+73,width-24,13,PAPER)
    a.rect(x+12,y+11,16,62,PAPER)
    a.rect(x+width-28,y+11,16,62,PAPER)
    if foam:
        a.rect(x+28,y+11,width-56,62,FOAM,None)
    a.rect(x+12,y-2,width-24,13,ORANGE)
    for sx in [x+19,x+width-20]:
        a.rect(sx-5,y+94,10,16,COPPER)
        a.rect(sx-2,y+9,4,96,INK,None)
        a.rect(sx-6,y-1,12,10,INK,None)
    # Open conduit and pour + vents.
    if top:
        a.rect(x+176,y-3,18,90,PAPER)
        for bx in [x+161,x+194]:
            a.rect(bx,y+11,15,62,PAPER)
    a.rect(x+300,y-3,30,14,PAPER)
    a.rect(x+90,y-3,9,14,PAPER)
    a.rect(x+width-56,y-3,9,14,PAPER)
    if not top:
        a.rect(x+12,y+11,16,13,ORANGE)
        a.rect(x+width-28,y+11,16,13,ORANGE)


def core_plan(a, x=26, y=55, width=460, height=230, foam=False):
    a.rect(x,y,width,height,STEEL)
    a.rect(x+10,y+10,width-20,height-20,FOAM if foam else PAPER)
    # Two schematic reservoir pockets; carbonator center.
    a.shape([(x+19,y+32),(x+133,y+32),(x+116,y+64),
             (x+103,y+116),(x+116,y+168),(x+133,y+height-32),
             (x+19,y+height-32)],PAPER)
    a.shape([(x+width-19,y+32),(x+width-133,y+32),(x+width-116,y+64),
             (x+width-103,y+116),(x+width-116,y+168),
             (x+width-133,y+height-32),(x+width-19,y+height-32)],PAPER)
    a.ellipse(x+width/2-84,y+height/2-84,168,168,PAPER)
    a.ellipse(x+width/2-91,y+height/2-91,182,182,None,COPPER,3)
    a.rect(x+5,y+84,8,63,BLUE,None)
    a.rect(x+width-13,y+84,8,63,BLUE,None)
    a.label("RESERVOIR A",x+70,y+116,9,INK,align="center")
    a.label("RESERVOIR B",x+width-70,y+116,9,INK,align="center")
    a.label("SEALED",x+width/2,y+108,10,INK,align="center")
    a.label("CARBONATOR",x+width/2,y+126,10,INK,align="center")


def pages(c):
    n=1
    start(c,n,"Make the soft parts", "Silicone funnel + two foam caps + one body pour. A picture for each bench move.", "START HERE")
    def cover(a):
        shell(a,15,37,190,98)
        shell(a,279,37,185,98,core=True)
        a.arrow(222,80,268,80,ORANGE)
        a.label("FUNNEL",263,18,16,BLUE,"PlexBold","center")
        a.label("cavity + core + steel rod",263,172,11,align="center")
        a.rect(239,247,222,31,FOAM)
        a.rect(239,292,222,31,FOAM)
        a.rect(48,232,146,94,STEEL)
        a.label("BODY",121,283,12,INK,"PlexBold","center")
        a.label("TOP CAP",350,268,11,INK,"PlexBold","center")
        a.label("BOTTOM CAP",350,313,11,INK,"PlexBold","center")
        a.label("THREE COLD-CORE POURS",263,220,14,BLUE,"PlexBold","center")
    figure(c,cover,height=367)
    actions(c,[("Funnel: pages 2-16", "Finish the printed tooling, prove the material stack, cast, open and inspect the removable funnel."),
               ("Cold core: pages 17-22", "Prepare both cap pours and the body pour. Record the batch recipe before combining the foam liquids.")],y=540)
    gate(c,"Use this at the bench", "Coral marks the current move. Blue marks gauges, air paths and surfaces to keep clear. Pictures are schematic; named dimensions govern.",tone=BLUE)
    finish(c,n,"Scope: funnel-mold/README.md; cold-core.md steps 3, 5-7", "mold-guide/README.md")

    n=2
    start(c,n,"Stage the casting bench", "Lay out the whole job before silicone A meets silicone B.", "FUNNEL")
    def bench(a):
        shell(a,10,20,153,78)
        shell(a,288,20,153,78,True)
        a.label("cavity",105,132,11,align="center")
        a.label("core",380,132,11,align="center")
        steel_rod(a,245,20,100,ORANGE)
        a.label("steel rod",245,140,11,align="center")
        bottle(a,15,180,"A",TEAL)
        bottle(a,90,180,"B",GOLD)
        cup(a,186,195,64,83,.25,label="mix cup")
        a.rect(213,164,7,48,STEEL)
        a.rect(287,239,93,35,STEEL)
        a.rect(305,248,56,17,PAPER)
        a.label("0.0 g",333,261,11,BLUE,align="center")
        a.label("scale",333,300,11,align="center")
        a.rect(421,204,63,77,PAPER)
        a.rect(437,180,32,24,STEEL)
        a.label("ER200",451,247,10,BLUE,align="center")
        a.label("release",452,300,11,align="center")
    figure(c,bench)
    actions(c,[("Tooling + closure", "Cavity, core, stock steel rod, eight M4 x 20 bolts, 9 mm OD washers and nuts; a sharp blade for cured flash."),
               ("Liquids + handling", "BBDINO 40A A/B, compatible black pigment, scale, cups, sticks, release, catch tray, vacuum chamber and pump."),
               ("Dry, ventilated work", "Read the container instructions. Wear eye protection and appropriate gloves; keep release spray away from ignition sources.")])
    gate(c,"Ready", "Room, materials and tooling are at the recorded batch temperature. The open mold and catch tray fit through the actual chamber opening.",tone=BLUE)
    finish(c,n,"Tooling: funnel-mold/README.md. Release: Smooth-On ER200 instructions.", "printed-parts/zone-c/funnel-mold/README.md")

    n=3
    start(c,n,"Finish the forming faces", "The coating allowance belongs to the forming surfaces. The parting lands remain bare.", "FUNNEL")
    def finish_faces(a):
        shell(a,50,78,340,161)
        a.shape([(a_,b_) for a_,b_ in [(84,96),(364,96),(389,215),(104,215)]],ORANGE)
        a.rect(52,77,337,14,BLUE,None)
        a.shape([(55,90),(75,90),(97,231),(78,231)],BLUE,None)
        a.shape([(370,90),(390,90),(415,231),(395,231)],BLUE,None)
        a.rect(81,229,335,14,BLUE,None)
        a.label("SAND + SEAL + RELEASE",246,162,14,PAPER,"PlexBold","center")
        a.label("forming faces: 0.30 mm net reserve",246,184,11,PAPER,align="center")
        a.arrow(33,24,74,78,BLUE)
        a.label("mask bare lands",26,17,11,BLUE)
        a.arrow(455,47,404,133,BLUE)
        a.label("mask holes",481,38,11,BLUE,align="right")
        a.label("also mask: locators, rod guides and axial stops",258,289,11,BLUE,align="center")
    figure(c,finish_faces)
    actions(c,[("Remove every support", "Clear the dry backs, neck and rod guides. Remove loose plastic and smooth the forming slopes before applying the finish."),
               ("Measure a witness", "Use the actual PETG, sanding and finish stack on a sample. Measure net growth; the shell reserve is 0.30 mm normal to the face."),
               ("Mask closure datums", "Keep lands, pegs/holes, bolt bores, rod guides and end stops bare. Coated lands change closure height.")])
    gate(c,"Before continuing", "The finish is dry and coherent, and the coated halves still close on the bare lands. Coating compatibility and closure need a physical check.")
    finish(c,n,"Funnel-mold/README.md: forming surfaces and fit; print-log.md", "printed-parts/zone-c/funnel-mold/README.md")

    n=4
    start(c,n,"Prepare the steel rod", "One stock 6 mm x 25 mm rod forms the entire straight outlet bore.", "FUNNEL")
    def tool_profile(a):
        steel_rod(a,184,22,264,STEEL)
        a.dim(117,22,117,286)
        a.label("25 mm",74,143,12,BLUE,align="center")
        a.dim(152.3,305,215.7,305)
        a.label("6 mm diameter",184,330,11,BLUE,align="center")
        a.label("304 STAINLESS STEEL",303,95,13,BLUE,"PlexBold")
        a.label("smooth stock cylinder",303,125,11,INK)
        a.label("clean + light release film",303,151,11,INK)
        a.label("ends stay outside the cast",303,177,11,INK)
    figure(c,tool_profile,height=359)
    actions(c,[("Select the stock rod", "Use the specified smooth 6 mm x 25 mm stainless dowel. Its factory end chamfers stay outside the silicone forming span."),
               ("Clean the cylinder", "Remove oil and debris, then dry. Keep the cylindrical surface smooth and free of dents or raised burrs."),
               ("Apply release", "Apply the same light release film used on the mold. Keep the rod and both printed guides clean for a loose drop-in fit.")],y=530)
    gate(c,"Ready", "The straight rod slides through the open core guide and rests on the cavity's lower floor. Its upper end stays visible.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md: stock rod and open guide", "printed-parts/zone-c/funnel-mold/README.md")

    n=5
    start(c,n,"Prove the material stack", "A small same-stack witness protects the first full casting.", "FUNNEL")
    def witness(a):
        for i,(label,caption) in enumerate([("PETG", "shell + steel rod"),("FINISH", "sealer + release"),("PIGMENT", "actual concentration")]):
            x=18+i*172
            a.rect(x,80,144,79,STEEL)
            a.rect(x+9,96,126,10,BLUE,None)
            a.rect(x+9,107,126,25,ORANGE,None)
            a.label(label,x+72,52,14,BLUE,"PlexBold","center")
            a.label(caption,x+72,188,10,INK,align="center")
            a.arrow(x+154,225,x+128,140,ORANGE)
        a.label("actual 40A silicone + actual pigment on each actual contact stack",262,258,11,INK,align="center")
        a.label("cure, then peel and inspect the contact face",262,283,12,BLUE,"PlexSemi","center")
    figure(c,witness)
    actions(c,[("Make the witness representative", "Use the actual shell PETG and finish, steel rod, release and silicone batch. Include the planned pigment concentration."),
               ("Keep the stack clean", "Use clean cups, tools and contact surfaces. Test the exact finishing products and pigment that will touch this platinum-cure silicone."),
               ("Inspect after cure", "The rubber must cure at the contact face and release without tack, tearing or coating transfer. Record that result before the full cast.")])
    gate(c,"Hold if gummy", "A firm outer surface can hide inhibited rubber at the tool. Cure/release compatibility has no accepted full-tool record yet.")
    finish(c,n,"Funnel-mold/README.md; Smooth-On sealer/release reference", "printed-parts/zone-c/funnel-mold/README.md")

    n=6
    start(c,n,"Drop in the steel rod", "The open core guide leads the rod into the cavity's lower floor seat.", "FUNNEL")
    def seat(a):
        view = mold_section(a,y=95)
        p = view["point"]
        a.label("SECTION / straight stock rod",263,21,12,BLUE,"PlexSemi","center")
        a.label("open 6.4 mm guide",43,55,11,BLUE)
        a.line(158,59,*p(1.85,29.685179),BLUE,.8)
        a.label("6 x 25 mm steel rod",330,142,11,BLUE)
        a.line(323,143,*p(4.85,40),BLUE,.8)
        a.label("lower seat / 1.5 mm deep",323,244,10.5,BLUE,align="right")
        a.line(270,231,*p(5.05,50.45),BLUE,.8)
        a.label("6 mm silicone space",27,280,11,BLUE)
        a.line(109,261,*p(-40,37),BLUE,.8)
        a.label("PETG ramp backing: 5 mm minimum",300,280,10.5,INK,align="center")
        a.label("core brim pocket backing: 4.7 mm",300,299,10,INK,align="center")
        a.label("open guide allows air and small silicone overflow",263,329,10,MUTED,align="center")
    figure(c,seat,height=354)
    actions(c,[("Close the empty mold", "Seat the locators and bare flange lands. The core guide must align with the cavity's lower seat."),
               ("Drop the rod through the guide", "Lower the stock rod from the open dry back. It rests on the lower floor, 1.5 mm below the block-bottom face."),
               ("Check free movement", "Lift the rod and let it settle again without pressing. The upper end projects about 4.2 mm above the guide.")],y=530)
    gate(c,"Ready", "The mold closes on its bare lands independently of rod length. Clear support residue if the rod catches.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md: straight rod and open guide", "printed-parts/zone-c/funnel-mold/README.md")

    n=7
    start(c,n,"Dry-close the mold", "Bring the bare parting lands together before adding liquid.", "FUNNEL")
    def close(a):
        a.rect(76,46,355,210,TEAL)
        a.rect(90,60,327,182,GOLD)
        points=[(99,68),(407,231),(407,68),(99,231),(253,68),(253,231),(99,149),(407,149)]
        for i,(x,y) in enumerate(points,1):
            a.ellipse(x-11,y-11,22,22,ORANGE,INK)
            a.label(str(i),x,y+4,10,PAPER,"PlexBold","center")
        a.rect(123,98,260,106,GOLD)
        a.label("8 x M4 x 20",252,144,17,INK,"PlexBold","center")
        a.label("9 mm OD washers + nuts",252,166,11,INK,align="center")
        a.label("opposite stations / small increments",252,291,12,BLUE,"PlexSemi","center")
        a.label("bolt order schematic; actual asymmetric locators set orientation",252,315,9.5,MUTED,align="center")
    figure(c,close,height=348)
    actions(c,[("Locate without force", "The asymmetric short pegs establish drain orientation. One mating hole is slotted to accommodate spacing error."),
               ("Close opposite stations", "Use eight bolts, washers and nuts or small clamps on the flat flange backs. Tighten incrementally until bare lands meet."),
               ("Backlight the seam", "Check closure with the steel rod resting on the lower floor. Reopen for release and filling after this dry fit succeeds.")],y=522)
    gate(c,"Check", "The bare flange lands meet, the rod rests on its lower floor, and the open upper guide leaves its end accessible.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md: closure; print-log.md: physical evidence scope", "printed-parts/zone-c/funnel-mold/README.md")

    n=8
    start(c,n,"Apply a light release film", "A thin, dry, continuous film reaches the small wet features too.", "FUNNEL")
    def release(a):
        shell(a,160,125,270,133)
        a.rect(38,96,54,109,STEEL)
        a.rect(45,82,40,16,ORANGE)
        a.rect(69,79,18,8,INK,None)
        for yy in [127,147,170]:
            a.line(87,88,194,yy,BLUE,.7,dash=[2,5])
        a.dim(86,58,195,58)
        a.label("6-8 in",143,42,14,BLUE,"PlexBold","center")
        a.label("15-20 cm",143,75,10,BLUE,align="center")
        a.label("mist / brush detail / mist / dry",284,302,13,BLUE,"PlexSemi","center")
    figure(c,release)
    actions(c,[("Clean and shake", "Use a suitable cleaner for the proven finish stack. Shake Ease Release 200 well; spray with ventilation and eye/skin protection."),
               ("Mist from 6-8 inches", "Apply lightly, brush over fine details and add a second light mist. Coat the steel rod lightly; keep the guide and fill/vent holes open."),
               ("Let it dry", "Recheck bare closure datums, rod guides and port openings. Apply a light fresh release film before each cast.")])
    gate(c,"Release check", "The same-stack witness must already have passed. Spray application does not establish compatibility, cleanability or finished food-contact acceptance.")
    finish(c,n,"Smooth-On Ease Release 200 instructions + sealer/release reference", "mold-guide/README.md#manufacturer-sources")

    n=9
    start(c,n,"Measure, color and mix", "BBDINO 40A uses equal A and B. Choose one measurement basis for the whole batch.", "FUNNEL")
    def measure(a):
        bottle(a,23,48,"A",TEAL)
        bottle(a,403,48,"B",GOLD)
        cup(a,149,101,94,117,.4,TEAL,"M / 2")
        cup(a,284,101,94,117,.4,GOLD,"M / 2")
        a.label("1 A : 1 B",263,55,25,BLUE,"PlexBold","center")
        a.label("BY WEIGHT OR BY VOLUME",263,80,11,BLUE,align="center")
        a.line(75,181,136,181,ORANGE,2)
        a.arrow(463,181,390,181,ORANGE)
        a.label(f"{VOLUME:.1f} mL nominal casting",263,275,17,INK,"PlexBold","center")
        a.label(f"about {MASS:.0f} g rubber + ports and mixing allowance",263,301,11,INK,align="center")
    figure(c,measure)
    actions(c,[("Set a batch quantity", f"Nominal geometry is {VOLUME:.1f} mL. The ~1.13 g/mL material estimate gives ~{MASS:.0f} g in the casting; allow extra for fill ports and mixing loss."),
               ("Weigh the pigment", "Use the actual BBDINO platinum-compatible black. Project limit: at most 2% by weight. Include it in the same-stack cure/release witness."),
               ("Mix the measured components", "Scrape the cup wall and bottom until uniform. Start the working-time clock when A and B meet; no unmixed streaks remain.")])
    gate(c,"Batch clock", "Maker working time: 30 min at 23 C. Record room and liquid temperature; warmer conditions shorten the window. Follow the supplied batch instructions.",tone=BLUE)
    finish(c,n,"Funnel silicone.md; design.json; BBDINO 40A manufacturer product page", "printed-parts/zone-c/funnel-mold/silicone.md")

    n=10
    start(c,n,"Degas the mixed silicone", "This 40A grade requires degassing. Give the rising foam room above the liquid.", "FUNNEL")
    def degas(a):
        for i,(caption,level) in enumerate([("rise",.7),("collapse",.28),("vent slowly",.25)]):
            x=17+i*173
            a.rect(x,52,147,174,STEEL)
            a.rect(x+8,63,131,152,PAPER)
            a.rect(x-3,45,153,10,BLUE)
            cup(a,x+34,97,78,105,level,ORANGE)
            if i==0:
                for px,py in [(x+57,136),(x+80,138),(x+73,112),(x+105,155),(x+65,156)]:
                    a.ellipse(px,py,7,7,PAPER,ORANGE,.6)
            if i==2:
                a.arrow(x+74,8,x+74,43,BLUE)
            else:
                a.arrow(x+75,41,x+75,13,BLUE)
            a.label(caption,x+73,256,13,BLUE,"PlexSemi","center")
        a.label("headroom above actual batch / catch tray below",263,292,11,INK,align="center")
    figure(c,degas)
    actions(c,[("Choose an ample cup", "Mixed silicone rises during evacuation. Use a larger container or split the batch if the available cup cannot contain the froth."),
               ("Evacuate under control", "Degas in a separate container with expansion space. Observe the rise and collapse; control the valve to prevent overflow."),
               ("Vent and pour while fluid", "Vent slowly, remove the cup and continue the casting sequence within the measured working-time window.")])
    gate(c,"Use the actual equipment instructions", "The guide supplies no universal vacuum setpoint or timer. Follow the chamber/pump and silicone batch instructions; watch the material.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md; BBDINO 40A; Smooth-On degassing example", "printed-parts/zone-c/funnel-mold/README.md")

    n=11
    start(c,n,"Fill, lower, then top up", "Set the rod in the lower seat, fill the open cavity, then lower the core slowly over it.", "FUNNEL")
    def casting(a):
        step_label(a,1,"Rod seated / fill cavity",18,4)
        mold_section(a,x=14,y=66,width=220,include_core=False,liquid=True)
        cup(a,57,32,49,37,.3,ORANGE)
        a.arrow(81,69,81,88,ORANGE)
        step_label(a,2,"Lower the core slowly",287,4)
        mold_section(a,x=289,y=111,width=220,liquid=True)
        a.arrow(352,58,352,98,ORANGE)
        a.arrow(445,58,445,98,ORANGE)
        a.label("small guide overflow trims after cure",263,208,10.5,INK,align="center")
        a.rect(133,272,256,27,GOLD)
        a.ellipse(262,277,19,13,ORANGE)
        for px in [163,206,329,359,374]:
            a.ellipse(px,282,7,7,ICE,BLUE)
            a.arrow(px+3,273,px+3,248,BLUE,1.2,4)
        a.arrow(272,247,272,271,ORANGE)
        a.label("3  Top up: 11 mm fill / 5 x 4 mm vents open",265,324,12,BLUE,"PlexSemi","center")
    figure(c,casting,height=355)
    actions(c,[("Seat the rod, then fill", "Set the steel rod on the lower seat floor. Fill around the rod and drain block while the degassed silicone still flows."),
               ("Seat the core evenly", "Lower slowly over the rod. Let air escape through the open rod guide; close the bare flange lands without force."),
               ("Top up through the fill hole", "Use the 11 mm fill opening. The five 4 mm vents remain clear for air; catch overflow and keep the dry backs open.")],y=527)
    gate(c,"Check", "The parting lands remain closed, the rod stays seated, and liquid reaches the block and continuous 6 mm ramp space. No pressure injection.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md: cast and open, steps 2-3", "printed-parts/zone-c/funnel-mold/README.md")

    n=12
    start(c,n,"Cycle the filled mold gently", "If using a filled-mold vacuum cycle, the whole tool shares the chamber pressure.", "FUNNEL")
    def mold_vacuum(a):
        a.rect(25,31,473,241,STEEL)
        a.rect(37,43,449,216,PAPER)
        a.rect(20,19,483,19,BLUE)
        a.rect(56,239,410,9,INK,None)
        a.rect(60,211,405,28,ICE)
        mold_section(a,x=67,y=132,width=393,liquid=True)
        for px in [96,435]:
            a.arrow(px,129,px,98,BLUE)
        a.arrow(218,119,218,80,BLUE)
        a.arrow(313,118,336,80,BLUE)
        a.arrow(86,194,51,209,BLUE)
        a.label("fill + vents + both dry backs open",268,299,12,BLUE,"PlexSemi","center")
        a.label("catch tray / overflow clear of pressure paths",268,321,10,INK,align="center")
    figure(c,mold_vacuum,height=350)
    actions(c,[("Keep openings connected", "Place the complete mold inside the chamber. Fill, vents and dry backs must communicate with chamber air; overflow cannot seal them."),
               ("Evacuate and vent slowly", "Perform any cycle while silicone is fluid. Observe tool/overflow behavior, vent gently, then recheck and top up the fill level."),
               ("Return to ambient for cure", "Keep the flanges held together through room-temperature cure. The tooling is not rated for a sealed atmosphere differential.")],y=526)
    gate(c,"Keep pressure paths open", "Fill, vents, dry backs and the rod guide share the chamber pressure. Stop on seam opening, distortion or a blocked air path.")
    finish(c,n,"Funnel-mold/README.md: load and vacuum; cast and open step 4", "printed-parts/zone-c/funnel-mold/README.md")

    n=13
    start(c,n,"Hold the flanges through cure", "Leave the tool undisturbed at ambient pressure while the silicone develops its cure.", "FUNNEL")
    def cure(a):
        mold_section(a,x=99,y=120,width=333,liquid=True)
        for xx in [111,420]:
            a.rect(xx,109,5,24,INK,None)
            a.rect(xx-4,106,13,7,ORANGE)
        a.ellipse(8,8,98,98,ICE,BLUE)
        a.line(57,57,57,29,BLUE,3)
        a.line(57,57,80,66,BLUE,3)
        a.label("23 C",463,70,16,BLUE,"PlexBold","center")
        a.label("reference",463,89,10,BLUE,align="center")
        a.label("5 h project demold hold",268,245,19,BLUE,"PlexBold","center")
        a.label("24 h project full-use hold",268,278,15,INK,"PlexSemi","center")
        a.label("also inspect a same-batch witness",268,311,12,INK,align="center")
    figure(c,cure,height=345)
    actions(c,[("Log time and temperature", "Record A/B mixing start, pour finish, room/liquid temperature and batch identity. Warmer and cooler shops change the cure window."),
               ("Use the conservative project hold", "Project material record uses 5 h before demold at 23 C and 24 h before full use. Check the supplied batch insert and cured witness."),
               ("Keep the tool assembled", "Maintain ambient pressure and closed flanges. Leave the casting and steel rod seated until their contact surfaces have cured.")],y=524)
    gate(c,"Cure is not food-contact release", "The manufacturer's direct page lists 3 h; the project holds 5 h conservatively. No qualified post-cure bake schedule is established.")
    finish(c,n,"Funnel silicone.md; BBDINO direct page checked 04 Oct 2026", "printed-parts/zone-c/funnel-mold/silicone.md")

    n=14
    start(c,n,"Open in small movements", "Free the core first; keep the casting and steel rod together while peeling from the cavity.", "FUNNEL")
    def open_mold(a):
        mold_section(a,x=25,y=152,width=455,liquid=True)
        a.arrow(117,141,117,97,ORANGE)
        a.arrow(396,141,396,97,ORANGE)
        a.label("lift core straight off the steel rod",256,65,14,ORANGE,"PlexSemi","center")
        a.line(40,150,23,136,BLUE,3)
        a.line(468,150,488,136,BLUE,3)
        a.label("alternate opposite notches",256,320,12,BLUE,"PlexSemi","center")
        a.label("peel accessible brim to admit air",256,341,11,INK,align="center")
    figure(c,open_mold,height=360)
    actions(c,[("Clear the opening points", "Trim overflow at port mouths and remove the flange bolts or clamps. Keep the casting supported while freeing the core."),
               ("Alternate opening points", "Use a blunt tool at opposing edge notches, moving a little at a time. Peel accessible silicone brim to let air enter."),
               ("Lift, then peel", "Lift the core straight off the rod. Peel the casting and rod together from the cavity; support the drain block.")],y=532)
    gate(c,"Stop on sticking", "Peel the accessible brim to admit air; keep opening movements small. Support the drain block without levering on the rod.")
    finish(c,n,"Funnel-mold/README.md: cast and open step 5", "printed-parts/zone-c/funnel-mold/README.md")

    n=15
    start(c,n,"Pull the rod and trim flash", "Support the silicone block while sliding the straight steel rod out.", "FUNNEL")
    def collar(a):
        for i,cx in enumerate([93,268]):
            a.rect(cx-62,129,124,84,ORANGE)
            if i == 0:
                steel_rod(a,cx,45,154,STEEL)
                a.arrow(cx+61,147,cx+61,57,BLUE,2.5,8)
            else:
                a.rect(cx-20,213,40,17,ORANGE)
                a.line(cx-69,213,cx+69,213,BLUE,1.2,dash=[4,3])
                a.shape([(cx-89,226),(cx-44,216),(cx-68,240)],STEEL)
            a.label("1  Slide rod out" if i == 0 else "2  Trim flush",cx,22,11,BLUE,"PlexSemi","center")
        a.rect(390,129,104,84,ORANGE)
        a.rect(430,127,24,88,PAPER)
        a.label("STRAIGHT",442,256,12,BLUE,"PlexBold","center")
        a.label("6 mm bore",442,278,11,BLUE,align="center")
    figure(c,collar,height=352)
    actions(c,[("Withdraw the straight rod", "Support the block and slide the released steel rod out along its axis. Peel the silicone from it if needed."),
               ("Trim the accessible collars", "Cut lower-seat flash flush with the block bottom and guide overflow flush with the bowl throat. Trim port and vent flash."),
               ("Keep the bore intact", "Leave the cylindrical 6 mm wall smooth. Clean the rod and guide openings before the next casting.")],y=528)
    gate(c,"Ready", "The straight outlet is open end to end, its edge is clean, and the flat bearing face is intact.",tone=BLUE)
    finish(c,n,"Funnel-mold/README.md: opening, rod withdrawal and flash trim", "printed-parts/zone-c/funnel-mold/README.md")

    n=16
    start(c,n,"Inspect and clean the funnel", "A complete casting has a continuous ramp, an open straight bore and an intact bearing face.", "FUNNEL")
    def funnel_check(a):
        a.shape([(56,64),(453,64),(437,85),(426,122),(274,208),
                 (259,218),(245,208),(77,122),(65,85)],FOAM)
        a.shape([(65,65),(440,65),(424,87),(401,115),(274,172),
                 (247,181),(96,111),(74,87)],PAPER)
        a.rect(229,207,63,76,ORANGE)
        a.ellipse(250,213,21,56,PAPER,BLUE)
        a.line(299,259,393,266,BLUE,.9)
        a.label("straight bore",397,270,11,BLUE)
        a.line(195,171,88,215,BLUE,.9)
        a.label("ramp + brim",22,228,11,BLUE)
        a.line(258,285,258,316,BLUE,.9)
        a.label("flat bearing face",258,339,11,BLUE,align="center")
    figure(c,funnel_check,height=355)
    actions(c,[("Inspect every wetted surface", "Look for pinholes, bubbles, tack, tears and coating transfer. Inspect the straight bore and both trimmed outlet ends."),
               ("Clean with the qualified process", "Release traces and residue must be removed. The finished silicone, black pigment and post-process need the wetted-surface qualification."),
               ("Check its actual installation", "The block bears on the cradle's hook tops. Its 6 mm bore grips the 6.35 mm LLDPE drain stub. Check seating, lift-out and leaks.")],y=528)
    gate(c,"Hold from food service", "No qualified bake schedule or finished-mixture food-contact result is recorded. A cured, attractive part alone does not close that gate.")
    finish(c,n,"Funnel silicone.md; funnel-mold/README.md; wetted-surface-test.md", "printed-parts/zone-c/funnel-mold/silicone.md")

    n=17
    start(c,n,"Prepare the three foam pours", "Two cap cavities and one body cavity use the acquired FSD 2 lb closed-cell PU foam.", "COLD CORE")
    def foam_recipe(a):
        bottle(a,27,45,"A",TEAL)
        bottle(a,113,45,"B",GOLD)
        a.arrow(190,99,251,99,ORANGE)
        a.rect(275,33,222,264,PAPER)
        a.label("BATCH RECIPE",291,59,16,BLUE,"PlexBold")
        for yy,label in [(87,"ratio + measurement basis"),(121,"liquid / room temperature"),
                         (155,"mix + working window"),(189,"A/B quantity for each shot"),
                         (223,"release / cure / trim time")]:
            a.label(label,291,yy,10,INK)
            a.line(291,yy+14,478,yy+14,RULE,1)
        a.label("TOP / BOTTOM / BODY",265,330,13,BLUE,"PlexSemi","center")
    figure(c,foam_recipe,height=355)
    actions(c,[("Confirm the actual batch", "Use FSD B08R7TX8QJ and its container instructions/SDS. The official page says equal parts; ratio basis and process window need the batch record."),
               ("Record each shot", "Top and bottom caps differ. Set the measured A/B quantities, expansion allowance, mixing/working time and cure/trim hold before combining."),
               ("Stage a dry, ventilated bench", "Use dry cups/tools, protective gloves and chemical eye protection. Keep moisture out of the liquids and vapors away from the operator.")],y=527)
    gate(c,"Hold mixing and pouring", "The repository has no calibrated cap/body shot recipe or verified batch timing. Geometry and nominal density do not supply liquid dose or cure time.")
    finish(c,n,"Cold-core.md open items; FSD official foam page + SDS checked 04 Oct 2026", "mold-guide/README.md#foam-recipe-gate")

    n=18
    start(c,n,"Clamp each cap mouth-up", "Use the shell's top face as the pour fixture for both cap stacks, one after the other.", "COLD CORE")
    def cap_clamp(a):
        cap_section(a,y=119,top=False)
        a.label("lid / pads into BOTTOM cup",44,74,11,ORANGE)
        a.line(99,78,53,126,ORANGE,.8)
        a.label("cap floor",109,256,11,INK)
        a.line(178,251,153,199,INK,.8)
        a.label("shell top face + inserts",276,277,11,BLUE)
        a.line(369,261,370,227,BLUE,.8)
        a.label("10 x M3 x 25 through lid + cap",263,25,14,BLUE,"PlexSemi","center")
        a.label("TOP: flat lid underside / 4 deck inserts first",263,306,11,BLUE,align="center")
        a.label("BOTTOM: counterbore pads face into the cup",263,326,11,INK,align="center")
    figure(c,cap_clamp,height=350)
    actions(c,[("Label TOP and BOTTOM", "The top cap carries conduits and four deck-mount columns. Press the four full-length RX-M3x5.7 inserts into those columns before pouring."),
               ("Use installed shell threads", "Ten full-length M3 inserts in the shell's top face supply the pour-clamp threads. Lid and cap have clearance holes."),
               ("Build the correct stack", "Cap floor down on the shell. Bottom lid pads enter the cup; top lid underside is flat. Close with ten M3 x 25 screws.")],y=526)
    gate(c,"Check", "The lid is held by the complete screw pattern, not its own threads. All top-cap conduits and both vent paths remain open.",tone=BLUE)
    finish(c,n,"Cold-core.md step 3; foam-shell/README.md cap stack; heat-set geometry record", "assembly/cold-core.md")

    n=19
    start(c,n,"Pour the two cap cavities", "With the recorded foam recipe ready, liquid enters the lid and air leaves through both vents.", "COLD CORE")
    def cap_pour(a):
        cap_section(a,y=149,foam=True)
        a.arrow(335,107,335,164,ORANGE,3,8)
        a.arrow(116,165,116,101,BLUE,2,7)
        a.arrow(424,165,424,101,BLUE,2,7)
        a.label("20 mm pour",331,80,13,ORANGE,align="center")
        a.label("6 mm vents x 2",119,52,12,BLUE)
        a.label("TOP 12.6 mm / BOTTOM 16 mm pour depth",262,298,13,BLUE,"PlexSemi","center")
        a.label("top-cap section / one stack at a time",262,324,11,INK,align="center")
    figure(c,cap_pour,height=350)
    actions(c,[("Mix the recorded shot", "Use the batch recipe's measurement basis, A/B quantities, temperature and working window. Have the clamped cap ready before mixing."),
               ("Pour into the 20 mm hole", "Keep the two 6 mm vents clear while foam expands. The lid stays clamped; do not cover the vent paths to force fill."),
               ("Cure, trim, unbolt, repeat", "After the recorded cure/trim hold, trim pour/vent overflow to the plate. Remove ten screws and repeat for the other labeled cap.")],y=526)
    gate(c,"Preserve the top features", "Trim flush without cutting a valve cradle, conduit, anchor or deck-mount feature. No numeric shot size or cure timer is implied by this page.")
    finish(c,n,"Cold-core.md step 3; foam-shell/README.md cap pour", "assembly/cold-core.md")

    n=20
    start(c,n,"Close the slots; protect access", "Everything foam will bury is installed, routed and proved before the body pour.", "COLD CORE")
    def plug_section(a):
        # Plug section at the wall, cavity on the right.
        a.rect(188,47,35,249,STEEL)
        a.rect(222,65,10,207,ORANGE)
        a.rect(172,49,50,13,ORANGE)
        a.rect(172,276,50,13,ORANGE)
        a.label("outside",111,38,12,BLUE,align="center")
        a.label("foam cavity",331,38,12,BLUE,align="center")
        a.label("continuous inner lip",315,104,12,ORANGE)
        a.line(292,100,232,100,ORANGE,.9)
        a.label("short outer tabs",20,128,11,ORANGE)
        a.line(141,124,176,59,ORANGE,.9)
        a.ellipse(175,241,68,38,COPPER,INK)
        a.arrow(254,12,254,47,ORANGE)
        a.label("slide down from above",262,320,13,BLUE,"PlexSemi","center")
        a.label("lower arch over copper / plug top flush with shell",262,343,11,INK,align="center")
    figure(c,plug_section,height=365)
    actions(c,[("Prove the buried work", "Carbonator and inlet jet qualified; coil/probes/reeds and fitted fluid lines checked. Tug-test inaccessible push fittings before encapsulating."),
               ("Seat both copper plugs", "Continuous lip faces the foam cavity. Shell wall lies between that lip and the short outside tabs. Lower arch seats over the copper."),
               ("Keep service paths open", "Protect reservoir vent/fill openings, top conduits, relief outlet and both reed channels. Reed columns are installed after body foam cure.")],y=534)
    gate(c,"Probe and access check", "Both probes and lead entries need foam coverage without a trapped void. Do not bury an unproved sensor, line, relief path or fitting.")
    finish(c,n,"Cold-core.md steps 1, 5-6; copper-plugs/README.md", "assembly/cold-core.md")

    n=21
    start(c,n,"Pour through the open top", "The body foam fills around the sealed carbonator and reservoirs; its connected zone reaches the coil.", "COLD CORE")
    def body_pour(a):
        core_plan(a,y=64,foam=True)
        for p in [(206,56,169,81),(302,56,338,81),(173,207,158,171),(351,155,365,186)]:
            a.arrow(*p,ORANGE,3,8)
        a.label("OPEN +Z TOP / no cap during the pour",263,31,14,BLUE,"PlexSemi","center")
        a.line(50,194,14,312,BLUE,.9)
        a.label("reed channel",8,330,10,BLUE)
        a.line(480,194,503,312,BLUE,.9)
        a.label("reed channel",507,330,10,BLUE,align="right")
        a.label("blue channels stay empty",264,330,11,BLUE,align="center")
        a.label("CORAL = foam zone / sealed vessel interiors take no foam",263,350,10,MUTED,align="center")
    figure(c,body_pour,height=370)
    actions(c,[("Mix the recorded body shot", "Use the batch record's quantities, temperature and mix/working window. The top remains open; cap stacks are already poured separately."),
               ("Pour directly into the body", "One pour fills the connected outer gap and space around the carbonator/coil, through the open paths at the reservoir-pocket ends."),
               ("Watch fill and squeeze-out", "Preserve empty reservoir/reed cavities and open tube paths. Foam may emerge at tube exits; leave trimming until the recorded cure hold.")],y=537)
    gate(c,"Do not assume hidden wet-out", "Probe voids and trapped gaps around the embedded coil are insulation defects. A risen top surface does not prove the hidden zone is full.")
    finish(c,n,"Cold-core.md step 6; foam-shell/README.md body pour paths", "printed-parts/cold-core/foam-shell/README.md")

    n=22
    start(c,n,"Trim and close the cold core", "All three pours are cured before the gaskets and caps complete the insulated stack.", "COLD CORE")
    def cold_close(a):
        a.rect(158,161,211,137,STEEL)
        a.rect(146,122,235,28,FOAM)
        a.rect(149,149,229,8,BLUE,None)
        a.rect(149,308,229,8,BLUE,None)
        a.rect(146,321,235,28,FOAM)
        for xx in [175,210,285,328]:
            a.rect(xx,82,8,28,ORANGE)
            a.rect(xx-3,78,14,7,ORANGE)
            a.arrow(xx+4,112,xx+4,127,ORANGE)
        a.label("10 M3 x 25",429,211,10,BLUE,align="center")
        a.label("per end",429,230,10,BLUE,align="center")
        a.arrow(391,123,391,160,ORANGE)
        a.arrow(391,320,391,297,ORANGE)
        a.label("TOP / installed rotation 180 deg",266,60,13,BLUE,"PlexSemi","center")
        a.label("gasket",78,154,11,BLUE)
        a.line(120,151,148,151,BLUE,.8)
        a.label("gasket",78,314,11,BLUE)
        a.line(120,310,148,310,BLUE,.8)
        a.label("BOTTOM / mouth down",266,376,13,BLUE,"PlexSemi","center")
    figure(c,cold_close,height=400)
    actions(c,[("Trim only cured overflow", "Use the qualified trim method. Protect tubes/leads, plug webs, cradles and insert hosts; clear all conduits, vents and reed channels."),
               ("Install reeds, gaskets and caps", "Drop reservoir reed columns in, route their cables out the top, and lay both TPU gaskets. Top cap rotates 180 deg; bottom mouth faces down."),
               ("Close and inspect", "Ten M3 x 25 screws per end. Identify top orientation by deck/cradle features. Check open paths, gasket seating and recessed screw heads.")],y=561)
    gate(c,"Finished", "Both caps and body cured; exposed foam flush; probes protected; channels and relief path open. Buried-fill quality needs its own process evidence.",y=686,tone=BLUE)
    finish(c,n,"Cold-core.md output condition + step 7; foam-shell/README.md", "assembly/cold-core.md")


def main():
    PDF.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(PDF), pagesize=(W,H), pageCompression=1, invariant=1)
    c.setTitle("Mold operations - Home Soda Machine")
    c.setAuthor("Home Soda Machine")
    pages(c)
    c.save()
    from pypdf import PdfReader
    r=PdfReader(PDF)
    assert len(r.pages)==TOTAL
    for p in r.pages:
        assert tuple(float(v) for v in p.mediabox)==(0.,0.,W,H)
    publish(PDF, GUIDE, "Mold operations", "Shop guide - silicone funnel and three cold-core foam pours, 22 pages, 8.5 x 11 in", TOTAL, SOURCES,
            {"manufacturer_sources":MANUFACTURERS,"source_review_date":"2026-10-05", "recipe_limits": [
                "Foam shot quantities, ratio measurement basis, processing temperature and mix/cure times must be supplied by the actual batch recipe before any pour.",
                "Project silicone hold is 5h demold/24h full use at23C; the direct manufacturer page states3h. No qualified post-cure bake or finished food-contact release is recorded.",
                "Current molding operations exclude the unbuilt silicone reservoir alternative and printed ASA Aero floats.",
            ]})
    print(f"{PDF.relative_to(ROOT)}: {TOTAL} Letter pages")


if __name__=="__main__":
    main()
