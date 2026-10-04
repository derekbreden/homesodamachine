#!/usr/bin/env python3
"""Hand-authored Letter refrigeration guide. Never an appliance build target."""
from __future__ import annotations
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/assembly-guides"))
from common import *

PDF = ROOT / "output/pdf/refrigeration-guide.pdf"
GUIDE = ROOT / "hardware/refrigeration-guide"
SOURCES = [
    "hardware/assembly/cold-core.md",
    "hardware/assembly/cold-core.figures.json",
    "hardware/assembly/handwork.md",
    "hardware/refrigeration-guide/README.md",
    "hardware/assembly/refrigerant-loop.md",
    "hardware/assembly/refrigerant-loop.figures.json",
    "hardware/reference/ice-maker/README.md",
    "hardware/reference/compressor/README.md",
    "hardware/reference/condenser-block/README.md",
    "hardware/assembly/enclosure-mechanical.md",
    "hardware/ledger/bom.md",
    "hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py",
    "hardware/printed-parts/cold-core/copper-plugs/README.md",
    "hardware/printed-parts/refrigeration/fuse-clamp/README.md",
    "hardware/assembly/firmware-and-commissioning.md",
    "firmware/src_appliance/README.md",
    "firmware/lib/machine_policy/cold_policy.h",
    "hardware/assembly/acceptance-and-burn-in.md",
    "hardware/mechanical-qualification/README.md",
    "hardware/concerns.md",
    "business/regulatory.md",
    "tools/refrigeration-guide/build.py",
    "tools/assembly-guides/common.py",
]

MANUFACTURERS = {
    "secop_service": "https://www.secop.com/sustainability/natural-refrigerants/compressor-service",
    "secop_repair": "https://www.secop.com/fileadmin/user_upload/technical-literature/guidelines/repair_of_hermetic_refrigeration_systems_05-2018_desg620a202.pdf",
    "supco_access": "https://supco.com/web/supco_live/products/BPV31.html",
    "uniweld_purge": "https://www.uniweld.com/product/rhp-special-purpose-series/",
    "orion_pump": "https://orionmotortech.com/cdn/shop/files/new_VPH-BN0A-O1_VPH-BN0A-O2.pdf?v=10939169087783086859",
    "epa_handling": "https://www.epa.gov/section608/stationary-refrigeration-prohibition-venting-refrigerants",
    "harris_filler": "https://ch-delivery.lincolnelectric.com/api/public/content/7cdc09a3e3364eca8d9ecb0145977257?v=7aae3e72",
}


def verify_manual_numbers():
    """A deliberate rebuild catches numeric drift without evaluating CAD.

    This check belongs to this manual document command only. A change to source
    figures never launches a render or rewrites the guide in the appliance build.
    """
    expected = {
        "cold-core.figures.json": {
            "CUT_FT":"15.92 ft", "SPRUNG_LEN":"4.06 m", "STUB_INLET":"335.5 mm",
            "STUB_OUTLET":"429.6 mm", "MANDREL_OD":"123 mm", "TANK_OD":"127 mm",
            "TOTAL_WRAPS":"9.687", "PITCH":"12.33 mm", "WIND_LENGTH":"119.4 mm",
            "PROT_INLET":"200 mm", "PROT_OUTLET":"175 mm",
        },
        "refrigerant-loop.figures.json": {
            "UNIT_A_CHARGE":"15 g", "UNIT_B_CHARGE":"23 g", "VACUUM_TARGET":"500 microns",
            "VACUUM_HOLD":"15 min", "RECHARGE_TOL":"±1 g", "PETG_TG":"~80 °C",
        },
    }
    for name, required in expected.items():
        data = json.loads((ROOT/"hardware/assembly"/name).read_text())
        flat = {key:value for group in data.values() for key,value in group.items()}
        for key,value in required.items():
            if flat.get(key)!=value:
                raise ValueError(f"Review the manual guide before rebuilding: {name}:{key} is {flat.get(key)!r}, expected {value!r}")
    policy=(ROOT/"firmware/lib/machine_policy/cold_policy.h").read_text()
    firmware={"kTankTargetC":2,"kHysteresisC":2,"kFreezeCutoffC":-8,
              "kFreezeRecoverC":-5,"kMinOffMs":180000,"kMinOnMs":60000,"kReadingStaleMs":30000}
    for name,value in firmware.items():
        found=re.search(r"constexpr\s+(?:float|uint32_t)\s+"+name+r"\s*=\s*(-?[\d.]+)f?\s*;",policy)
        if not found or float(found.group(1))!=value:
            raise ValueError(f"Review the manual guide before rebuilding: cold policy {name}")
    return {"selected_document_figures":expected,"firmware_literals":firmware}


def rounded(a, x, y, w, h, fill=ICE, stroke=RULE, radius=8):
    c = a.c
    c.setFillColor(color(fill))
    c.setStrokeColor(color(stroke))
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def path(a, points, stroke=COPPER, width=5, dash=None):
    for p, q in zip(points, points[1:]):
        a.line(*p, *q, stroke, width, dash)


def cross(a, x, y, r=8, fill=ORANGE):
    a.line(x-r, y-r, x+r, y+r, fill, 3)
    a.line(x-r, y+r, x+r, y-r, fill, 3)


def tick(a, x, y, fill=BLUE):
    path(a, [(x-7, y), (x-1, y+6), (x+10, y-9)], fill, 2.5)


def tank(a, x, y, w=126, h=200, foil=True, coil=True, current=False):
    fill = "#F4F6FA" if foil else STEEL
    a.rect(x, y+12, w, h-24, fill, INK)
    a.ellipse(x, y, w, 24, fill, INK)
    a.ellipse(x, y+h-24, w, 24, fill, INK)
    if foil:
        for dx in [17, 36, 55, 74, 93, 112]:
            if dx < w-5:
                a.line(x+dx, y+19, x+dx-7, y+h-21, RULE, .8)
    if coil:
        for i in range(8):
            cy = y+34+i*(h-67)/7
            a.shape([(x-4,cy+1), (x+20,cy+14,x+w-20,cy+14,x+w+4,cy-1)],
                    None, ORANGE if current else COPPER, 6, False)
    return x+w/2, y+h/2


def compressor(a, x, y, w=102, h=106, scale=1, cover=True):
    a.rect(x-9, y+h-8, w+18, 16, STEEL, INK)
    a.ellipse(x, y, w, h, INK, INK)
    a.ellipse(x+6, y+5, w-12, h-12, "#33384D", INK)
    if cover:
        a.rect(x+w*.27, y+h*.59, w*.5, h*.32, "#0F1526", INK)
    for dx in [-3, w-3]:
        a.ellipse(x+dx, y+h-4, 7, 5, PAPER, INK)


def condenser(a, x, y, w=100, h=124, current=False):
    a.rect(x, y, w, h, STEEL, INK)
    for dx in range(8, int(w), 7):
        a.line(x+dx, y+5, x+dx, y+h-5, MUTED, .8)
    a.ellipse(x+w*.2, y+h*.29, w*.6, w*.6, INK, INK)
    for angle in [0, 120, 240]:
        xx=x+w*.5; yy=y+h*.29+w*.3
        rad=math.radians(angle)
        a.shape([(xx,yy), (xx+math.cos(rad)*23, yy+math.sin(rad)*23),
                 (xx+math.cos(rad+.6)*19, yy+math.sin(rad+.6)*19)],
                STEEL, None)
    a.ellipse(x+w*.44, y+h*.29+w*.24, w*.12, w*.12, ORANGE if current else STEEL, None)


def drier(a, x, y, w=84, h=24, highlight=False):
    rounded(a,x,y,w,h,ORANGE if highlight else COPPER,INK,h/2)
    a.line(x-14,y+h/2,x,y+h/2,COPPER,4)
    a.line(x+w,y+h/2,x+w+14,y+h/2,COPPER,2)


def circuit(a, variant="new"):
    compressor(a, 36, 133, 100, 110)
    condenser(a, 220, 45, 95, 105)
    drier(a, 371, 57, 96, 24, variant=="new")
    if variant=="new":
        tank(a,368,144,110,130,coil=True)
    else:
        a.rect(365,152,124,34,STEEL,INK)
        for xx in range(375,480,17):
            a.shape([(xx,186),(xx+8,186),(xx+8,230),(xx,230)],STEEL,INK)
    path(a,[(136,162),(179,162),(179,81),(220,81)],COPPER,5)
    path(a,[(315,69),(371,69)],COPPER,5)
    path(a,[(467,69),(493,69),(493,266),(478,266)],COPPER,2)
    a.arrow(172,117,172,88)
    a.arrow(327,59,352,59)
    a.arrow(501,112,501,139)
    path(a,[(368,159),(345,159),(345,257),(136,257),(136,220)],COPPER,5)
    a.arrow(238,267,208,267)
    a.label("COMPRESSOR",28,127,10)
    a.label("CONDENSER + FAN",212,34,10)
    a.label("DRIER",396,44,10)
    a.label("CAPILLARY",450,107,10,align="right")
    a.label("SUCTION RETURN",155,293,10)
    if variant=="new":
        a.label("WOUND EVAPORATOR",349,132,10)
    else:
        a.label("FINGER PLATE",365,144,10)
        path(a,[(166,162),(166,114),(366,114),(366,152)],ORANGE,3)
        rounded(a,252,99,45,30,"#FBEAE2",ORANGE)
        a.label("BYPASS",274,118,8,ORANGE,align="center")
        cross(a,271,113,16)
    path(a,[(46,202),(17,202),(17,239)],COPPER,4)
    a.label("PROCESS",10,260,9)
    a.label("ACCESS",10,272,9)


def fig_cover(a):
    circuit(a)


def fig_labels(a):
    rounded(a,20,28,227,208,PAPER,INK)
    a.label("APPLIANCE RATING LABEL",34,54,11)
    for i,(k,v) in enumerate([("MODEL","Read exact model"),("REFRIGERANT","R600a"),("CHARGE","Copy actual grams"),("VOLTAGE / Hz","Copy actual supply")]):
        y=86+i*36
        a.label(k,35,y,8,MUTED)
        a.label(v,35,y+17,13,BLUE if i in [1,2] else INK)
    rounded(a,286,48,210,156,ICE,RULE)
    a.label("REFERENCE BASELINES",300,72,10,BLUE)
    a.label("Unit A / HZB-12/Q",300,103,12)
    a.label("15 g",471,103,15,ORANGE,align="right")
    a.label("Unit B / EFIC117-SS",300,140,12)
    a.label("23 g",471,140,15,ORANGE,align="right")
    a.label("The donor's label governs.",300,184,11)
    a.line(302,227,480,227,COPPER,7)
    a.label("Cast-stamps 48.5-2 / 45",302,251,11,MUTED)
    a.label("are not charge masses.",302,268,11,MUTED)
    a.arrow(254,137,278,137)


def fig_salvage(a):
    circuit(a,"donor")
    a.label("KEEP THE BONDED PAIR",157,185,10,BLUE)
    path(a,[(184,197),(310,197)],BLUE,1)
    a.label("Capillary + suction heat exchanger",151,210,9,BLUE)
    cross(a,423,202,30)


def fig_lengths(a):
    rounded(a,20,19,476,110,ICE,RULE)
    a.line(50,74,464,74,COPPER,9)
    a.line(79,49,79,94,BLUE,1)
    a.line(377,49,377,94,BLUE,1)
    a.dim(50,44,79,44)
    a.dim(79,44,377,44)
    a.dim(377,44,464,44)
    a.label("335.5 mm",26,116,11,ORANGE)
    a.label("Inlet allowance",25,153,11)
    a.label("4.06 m fitted wrap",213,115,13,BLUE,align="center")
    a.label("429.6 mm",474,116,11,ORANGE,align="right")
    a.label("Outlet allowance",487,153,11,align="right")
    a.label("Total cut / about 4.85 m (15.92 ft)",254,184,15,align="center")
    for x,lab,inside,out in [(28,"INLET",135.5,200),(290,"OUTLET",254.6,175)]:
        a.line(x,240,x+190,240,COPPER,8)
        a.rect(x+83,223,13,35,ORANGE,INK)
        a.label(f"{lab} / plug face is the datum",x,213,10)
        a.label(f"{inside:g} mm in shell",x,277,10,BLUE)
        a.label(f"{out:g} mm outside",x+190,277,10,BLUE,align="right")
    a.label("length picture is schematic",500,299,8,MUTED,align="right")


def fig_wind(a):
    for x,n,title in [(0,1,"REGISTER THE FIRST TAIL"),(177,2,"FOLLOW THE GROOVE"),(354,3,"SLIDE OFF AXIALLY")]:
        rounded(a,x+2,18,163,270,PAPER,RULE)
        a.label(str(n),x+14,41,17,BLUE)
        a.label(title,x+12,66,8)
        xx=x+38; yy=90
        a.rect(xx,yy+9,95,150,ICE,BLUE)
        a.ellipse(xx,yy,95,18,ICE,BLUE)
        a.ellipse(xx,yy+141,95,18,ICE,BLUE)
        for i in range(9):
            a.shape([(xx-4,yy+24+i*13),(xx+20,yy+36+i*13,xx+72,yy+36+i*13,xx+99,yy+19+i*13)],None,COPPER,4,False)
        path(a,[(xx-4,yy+134),(xx-20,yy+134),(xx-20,yy+157)],ORANGE,4)
        path(a,[(xx+99,yy+24),(xx+117,yy+24),(xx+117,yy+103)],COPPER,4)
        if n==2:
            a.arrow(xx+108,yy+130,xx+108,yy+34)
            a.label("9.687 wraps",x+12,266,12,BLUE)
        elif n==3:
            a.arrow(xx+47,yy+77,xx+47,yy+10)
            a.label("Keep each tail",x+12,257,10)
            a.label("in its own lane.",x+12,273,10)
        else:
            a.label("123 mm mandrel",x+12,266,11,BLUE)


def fig_wall(a):
    tank(a,147,28,150,239,foil=False,coil=False)
    a.rect(161,59,19,103,ORANGE,INK)
    for yy in [88,132]:
        a.rect(166,yy,8,21,PAPER,INK)
        a.line(170,yy+21,170,yy+33,INK,1)
    a.rect(249,234,12,13,BLUE,INK)
    path(a,[(255,247),(255,275),(347,275)],BLUE,1.7)
    a.line(264,240,322,220,BLUE,1)
    a.label("DS18B20 / 0x28",325,220,13,BLUE)
    a.label("Bare wall below the wind",325,240,10)
    a.line(161,111,94,111,ORANGE,1)
    a.label("Reed bridge",8,84,12,ORANGE)
    a.label("Calibrated with the",8,101,10)
    a.label("finished float first",8,119,10)
    a.label("ROD-REGISTER AZIMUTH",148,16,10,MUTED)
    a.shape([(379,46),(478,31),(492,163),(385,179)],STEEL,INK)
    for y in range(67,156,24):
        a.line(383,y,484,y-10,RULE,1)
    a.arrow(343,143,308,143)
    a.label("3M 425 foil",395,192,12)


def fig_transfer(a):
    tank(a,47,35,139,224,foil=True,coil=True,current=True)
    path(a,[(49,224),(22,224),(22,177)],COPPER,6)
    path(a,[(185,70),(208,70),(208,176)],COPPER,6)
    a.arrow(214,55,214,113)
    a.label("127 mm carbonator",23,289,11,BLUE)
    rounded(a,271,30,230,242,ICE,RULE)
    a.label("SUCTION-END PROBE",286,55,11,BLUE)
    a.line(302,126,477,126,COPPER,18)
    a.rect(365,109,17,13,BLUE,INK)
    path(a,[(371,109),(371,77),(449,77)],BLUE,2)
    a.shape([(338,105),(409,105),(414,145),(333,145)],"#C5CED9",INK)
    a.label("DS18S20 / 0x10",286,177,14,BLUE)
    a.label("Flat on copper at the",286,205,12)
    a.label("high / outlet end",286,224,12)
    a.label("Secure before foam hides it.",286,251,10)


def fig_tails(a):
    a.rect(63,25,242,240,STEEL,INK)
    tank(a,104,48,139,180,coil=True)
    path(a,[(104,195),(87,195),(87,231),(33,231)],ORANGE,6)
    path(a,[(243,82),(276,82),(276,159),(400,159)],COPPER,6)
    a.rect(59,214,15,37,ORANGE,INK)
    a.rect(298,139,15,37,ORANGE,INK)
    a.dim(26,260,63,260)
    a.label("INLET / lower wrap",8,280,10,ORANGE)
    a.label("200 mm from plug",8,298,10,BLUE)
    a.line(398,181,484,181,BLUE,1)
    a.label("OUTLET / upper wrap",338,204,10,COPPER)
    a.label("175 mm from plug",338,223,10,BLUE)
    a.label("One tail per lane",334,74,12)
    a.label("Port lane / inlet",334,96,11,ORANGE)
    a.label("West lane / outlet",334,119,11,COPPER)
    a.line(334,48,450,48,BLUE,1)
    a.label("Measure on the real routed part",92,13,10,BLUE)


def fig_support(a):
    rounded(a,23,229,474,32,STEEL,INK)
    compressor(a,54,94,108,129)
    condenser(a,214,76,92,135)
    tank(a,363,49,117,166,coil=True)
    for x in [337,363]:
        a.rect(x,209,28,19,BLUE,INK)
    path(a,[(156,178),(199,178),(199,205),(363,205)],COPPER,4)
    a.arrow(161,49,99,92)
    a.label("Keep the donor upright",28,39,12)
    a.label("Hold every body",311,15,12,BLUE)
    a.label("before a fastener comes out",286,33,10)
    a.line(354,32,375,52,BLUE,1)
    a.line(118,196,118,279,ORANGE,1)
    a.label("Retain terminal / PTC cover",28,294,11,ORANGE)
    a.label("Lines carry refrigerant, not the assembly's weight.",253,276,12,align="center")


def fig_bench(a):
    a.rect(15,37,492,183,ICE,RULE)
    for x in [34,68,102]:
        a.arrow(x,44,x,94,BLUE)
    a.label("VENTILATED WORKSPACE",139,56,11,BLUE)
    a.label("Ignition control + gas monitoring",139,78,11)
    compressor(a,56,111,80,91)
    rounded(a,176,115,138,81,PAPER,INK)
    a.label("HC-SUITABLE",245,142,11,BLUE,align="center")
    a.label("SERVICE RIG",245,161,11,BLUE,align="center")
    path(a,[(50,162),(25,162),(25,202),(176,202),(176,164)],BLUE,2)
    path(a,[(314,155),(469,155),(469,17)],BLUE,2)
    a.arrow(469,80,469,29)
    a.label("Safe discharge",331,104,11,BLUE)
    a.label("location outdoors",331,123,11,BLUE)
    rounded(a,24,242,219,56,PAPER,RULE)
    a.label("Equipment approval",38,264,12)
    a.label("Exact model + R600a use",38,285,10,MUTED)
    rounded(a,277,242,219,56,PAPER,RULE)
    a.label("Written service setup",291,264,12)
    a.label("Removal / purge / leak / charge",291,285,10,MUTED)


def fig_remove(a):
    compressor(a,36,65,138,156)
    path(a,[(39,115),(15,115),(15,150)],COPPER,8)
    rounded(a,0,146,52,33,ORANGE,INK)
    a.label("TEMP.",24,167,8,PAPER,align="center")
    path(a,[(27,179),(27,243),(273,243),(273,159)],BLUE,3)
    rounded(a,222,93,148,93,ICE,INK)
    a.label("CONTROLLED",296,124,13,BLUE,align="center")
    a.label("HC HANDLING",296,143,13,BLUE,align="center")
    a.label("Approved method",296,166,10,align="center")
    path(a,[(370,139),(466,139),(466,56)],BLUE,3)
    a.arrow(466,95,466,56)
    a.label("Safe destination",403,35,11,BLUE,align="center")
    a.label("Process tube",4,56,11)
    a.label("not suction / discharge",4,35,10,MUTED)
    a.label("No flame at this stage",269,279,14,ORANGE,align="center")
    cross(a,477,268,10)


def fig_cuts(a):
    condenser(a,39,28,80,97)
    drier(a,179,36,95,25)
    path(a,[(119,49),(179,49)],COPPER,4)
    path(a,[(274,49),(329,49),(329,213),(397,213)],COPPER,2)
    path(a,[(36,250),(315,250),(315,147),(397,147)],COPPER,6)
    path(a,[(329,66),(339,78),(329,90),(339,102),(329,114)],COPPER,2)
    a.rect(397,126,101,119,STEEL,INK)
    a.label("DISCARD",447,175,12,ORANGE,align="center")
    a.label("FACTORY",447,193,10,align="center")
    a.label("EVAPORATOR",447,210,10,align="center")
    cross(a,359,147,8)
    cross(a,369,213,8)
    a.label("Suction cut",233,126,11,ORANGE)
    a.label("Capillary cut",222,281,11,ORANGE)
    a.line(274,270,369,220,ORANGE,1)
    a.label("Keep this length and bonded pair",82,176,11,BLUE)
    a.line(280,184,316,200,BLUE,1)
    a.label("Remove hot-gas bypass",34,290,10)
    a.label("and qualify the branch closure.",34,307,10)
    a.label("Trace your donor; cut labels are functional.",40,12,10,MUTED)


def fig_purge(a):
    rounded(a,15,26,94,157,ICE,BLUE)
    a.label("DRY",62,91,16,BLUE,align="center")
    a.label("N2",62,115,22,BLUE,align="center")
    a.rect(46,8,30,18,STEEL,INK)
    rounded(a,137,48,112,75,PAPER,INK)
    a.label("REGULATE",193,74,10,align="center")
    a.label("+ METER FLOW",193,96,10,BLUE,align="center")
    path(a,[(109,94),(137,94)],BLUE,3)
    path(a,[(249,86),(289,86),(289,54),(466,54)],BLUE,3)
    path(a,[(249,86),(289,86),(289,140),(466,140)],BLUE,3)
    a.arrow(415,54,486,54)
    a.arrow(415,140,486,140)
    a.label("High branch",313,39,11)
    a.label("Low branch",313,124,11)
    a.label("OPEN OUTLETS",380,183,10,BLUE)
    a.label("Check each path",137,155,11,BLUE)
    drier(a,31,244,136,27,True)
    a.label("NEW, SEALED DRIER",24,224,11,ORANGE)
    a.arrow(184,257,217,257)
    a.label("Keep capillary length /",245,252,11)
    a.label("specify its new connection",245,271,11)
    a.label("RHP400's pressure dial is not a purge flowmeter.",262,306,10,MUTED,align="center")


def fig_suction(a):
    a.line(22,115,183,115,COPPER,18)
    a.line(338,115,495,115,COPPER,18)
    a.rect(218,99,83,32,ORANGE,INK)
    a.line(218,107,301,107,"#F3B18E",1)
    a.arrow(181,161,228,161)
    a.arrow(336,161,290,161)
    a.label("Coil outlet",19,83,13)
    a.label("1/4 in OD",19,184,12,BLUE)
    a.label("Suction return",385,83,13)
    a.label("1/4 in OD",389,184,12,BLUE)
    a.label("ACR slip coupling",260,58,14,ORANGE,align="center")
    a.label("Clean sockets / full intended engagement / no stress",260,229,12,align="center")
    rounded(a,38,252,440,45,ICE,RULE)
    a.label("Copper to copper + verified BCuP-5 = dry joint",258,279,12,BLUE,align="center")


def fig_swage(a):
    for x,n,title in [(0,1,"TRY ON MATCHING SCRAP"),(177,2,"FORM THE COPPER"),(354,3,"PROVE THE JOINT")]:
        rounded(a,x+2,20,163,262,PAPER,RULE)
        a.label(str(n),x+14,42,17,BLUE)
        a.label(title,x+12,67,8)
        if n==1:
            a.rect(x+14,118,86,25,COPPER,INK)
            a.line(x+89,130,x+145,130,INK,3)
            a.arrow(x+133,157,x+96,157)
            a.label("Mark insertion",x+12,220,10)
            a.label("Keep bore open",x+12,242,10,BLUE)
        elif n==2:
            a.shape([(x+14,118),(x+58,118),(x+97,128),(x+135,128),(x+135,132),(x+97,132),(x+58,143),(x+14,143)],COPPER,INK)
            a.line(x+131,130,x+150,130,INK,3)
            a.rect(x+62,95,52,13,STEEL,INK)
            a.rect(x+62,151,52,13,STEEL,INK)
            a.arrow(x+88,86,x+88,110)
            a.arrow(x+88,180,x+88,149)
            a.label("Smooth jaws",x+12,220,10)
            a.label("Progressive rotation",x+12,242,10)
        else:
            a.rect(x+15,106,71,56,ICE,BLUE)
            a.label("FLOW",x+50,128,10,BLUE,align="center")
            a.label("+ LEAK",x+50,146,10,BLUE,align="center")
            a.line(x+86,133,x+142,133,COPPER,5)
            tick(a,x+115,182)
            a.label("Bore + insertion +",x+12,220,10)
            a.label("braze + tightness",x+12,242,10)
    a.label("~0.031 in bore is a donor estimate; measure your capillary.",260,305,10,MUTED,align="center")


def fig_braze(a):
    a.rect(8,53,134,222,STEEL,INK)
    a.rect(130,145,17,64,ORANGE,INK)
    a.line(148,177,481,177,COPPER,15)
    a.shape([(151,147),(188,147),(196,154),(201,185),(191,205),(151,206)],ICE,BLUE)
    a.label("Heat sink",8,25,12,BLUE)
    a.line(71,31,167,148,BLUE,1)
    a.rect(270,167,66,20,ORANGE,INK)
    a.line(126,155,126,118,BLUE,2)
    rounded(a,104,83,80,33,ICE,BLUE)
    a.label("T PLUG",144,104,10,BLUE,align="center")
    a.shape([(355,95),(425,52),(442,73),(372,112)],INK,INK)
    a.shape([(355,98),(350,116),(344,126),(326,148),(342,114)],ORANGE,None)
    a.line(313,137,297,176,COPPER,2)
    a.arrow(393,211,480,211,BLUE)
    a.label("Flame / hot gas away from core",258,241,11,ORANGE)
    a.label("Open nitrogen outlet",319,271,11,BLUE)
    a.dim(147,224,271,224)
    a.label("Actual reach governs the sample",164,296,10,MUTED)


def fig_pressure(a):
    rounded(a,19,24,89,164,ICE,BLUE)
    a.label("DRY N2",63,113,18,BLUE,align="center")
    a.ellipse(136,48,50,50,PAPER,INK)
    a.line(161,73,174,62,BLUE,2)
    path(a,[(108,137),(161,137),(161,98),(220,98),(220,224),(454,224),(454,137)],BLUE,3)
    compressor(a,229,42,89,108)
    tank(a,382,33,105,145,coil=True)
    path(a,[(318,109),(343,109),(343,168),(382,168)],COPPER,4)
    for x,y in [(339,166),(450,223),(217,117)]:
        a.ellipse(x-10,y-10,20,20,None,ORANGE,1.5)
    rounded(a,26,251,471,49,PAPER,RULE)
    a.label("TEST PRESSURE + TIME + DECAY LIMIT",262,271,11,BLUE,align="center")
    a.label("Specified from the weakest rated circuit component",262,289,10,align="center")
    a.label("No pressure figure is inferred from the water-side hydro-test.",260,318,10,MUTED,align="center")


def fig_vacuum(a):
    compressor(a,30,62,113,138)
    rounded(a,181,60,95,78,ICE,BLUE)
    a.label("SYSTEM",228,82,10,BLUE,align="center")
    a.label("MICRONS",228,99,10,BLUE,align="center")
    a.label("500",228,125,23,BLUE,align="center")
    path(a,[(38,163),(14,163),(14,229),(315,229),(315,142),(392,142)],BLUE,3)
    path(a,[(229,138),(229,229)],BLUE,3)
    a.rect(291,219,18,20,ORANGE,INK)
    a.label("ISOLATE HERE",288,270,10,ORANGE,align="center")
    a.line(291,261,298,242,ORANGE,1)
    rounded(a,392,111,102,81,STEEL,INK)
    a.rect(420,99,45,12,INK,INK)
    a.label("HC PUMP",443,154,11,BLUE,align="center")
    a.arrow(446,100,446,46,BLUE)
    a.label("Exhaust outdoors",388,29,11,BLUE)
    a.label("Gauge stays with the system",138,293,13,BLUE)
    a.label("after the pump is isolated.",138,311,11)


def fig_charge(a):
    rounded(a,21,197,183,58,ICE,INK)
    a.rect(32,235,61,15,PAPER,INK)
    a.label("0.1 g",62,247,10,BLUE,align="center")
    rounded(a,67,46,103,150,STEEL,INK)
    a.rect(99,28,38,18,ORANGE,INK)
    a.label("R600a",118,114,20,BLUE,align="center")
    a.label("GRADE",118,139,11,align="center")
    path(a,[(137,34),(208,34),(208,163),(325,163)],BLUE,3)
    compressor(a,347,90,114,136)
    path(a,[(325,163),(347,163)],BLUE,3)
    a.label("Can + valve on scale",17,282,12)
    a.label("Hose support independent",213,69,11,BLUE)
    a.line(230,74,208,132,BLUE,1)
    rounded(a,246,233,254,63,PAPER,RULE)
    a.label("NET TO CIRCUIT",262,253,11,ORANGE)
    a.label("Can loss - retained / returned mass",262,277,11)
    a.label("Target comes from the qualified build recipe.",255,316,11,BLUE,align="center")


def fig_close(a):
    compressor(a,26,63,127,146)
    path(a,[(30,115),(4,115),(4,168)],COPPER,8)
    rounded(a,0,148,41,34,ORANGE,INK)
    cross(a,21,165,24)
    a.label("TEMPORARY",8,257,11,ORANGE)
    a.label("Piercing access",8,278,11)
    a.arrow(170,146,215,146)
    compressor(a,271,63,127,146)
    path(a,[(279,114),(236,114),(236,162)],COPPER,8)
    a.rect(221,153,30,18,BLUE,INK)
    a.label("FINAL",320,256,11,BLUE,align="center")
    a.label("Qualified closure / service fitting",320,277,11,align="center")
    tick(a,234,197)
    a.line(437,221,238,171,BLUE,1.5)
    rounded(a,425,212,72,36,ICE,BLUE)
    a.label("LEAK",460,235,10,BLUE,align="center")
    a.label("No torch on a charged circuit",253,26,14,ORANGE,align="center")


def fig_sensor(a):
    a.rect(25,222,464,21,STEEL,INK)
    a.rect(25,62,21,160,STEEL,INK)
    for xx in [72,160]:
        a.rect(xx,173,18,50,ICE,INK)
        a.rect(xx+5,173,6,45,INK,INK)
    a.rect(82,88,83,78,ORANGE,INK)
    a.ellipse(57,106,31,44,STEEL,INK)
    for yy in range(113,145,5):
        a.line(61,yy,83,yy,MUTED,.7)
    for xx in [165,172,179,186]:
        a.line(xx,119,xx+16,119,INK,1.5)
    a.arrow(129,23,129,70,BLUE)
    a.arrow(124,178,124,210,BLUE)
    a.label("Mesh faces WEST",206,74,13,BLUE)
    a.label("into the wall's well",206,95,11)
    a.label("Header faces EAST",206,146,13)
    a.label("into the open bay",206,167,11)
    a.line(199,157,187,129,INK,1)
    a.label("Install before the compressor blocks access.",42,280,13)
    a.label("Card is on edge; lower until it lands on its shoulder.",42,306,11)


def fig_mount(a):
    compressor(a,58,37,139,149)
    a.arrow(124,9,124,28,BLUE)
    a.label("Covered power end faces front",217,27,12,BLUE)
    a.rect(27,257,206,23,STEEL,INK)
    for x in [61,176]:
        a.rect(x,219,19,38,ICE,INK)
        a.ellipse(x-7,218,33,20,INK,INK)
        a.arrow(x+10,193,x+10,209,BLUE)
    rounded(a,275,48,230,222,PAPER,RULE)
    a.label("EACH OF FOUR MOUNTS",291,71,10,BLUE)
    a.rect(370,84,31,15,ORANGE,INK)
    a.rect(381,99,10,28,ORANGE,INK)
    a.ellipse(345,137,81,13,STEEL,INK)
    a.arrow(385,117,385,131,BLUE)
    a.rect(371,189,27,57,ICE,INK)
    a.ellipse(351,178,67,25,INK,INK)
    a.rect(379,190,11,32,COPPER,INK)
    a.label("M5 x 10 screw",294,106,10,ORANGE)
    a.label("OD25 washer",294,163,10)
    a.label("Post / insert",410,218,9,BLUE)
    a.label("Rubber stays the isolator",286,285,11)
    a.label("Stop at the washer's post landing.",34,309,12,BLUE)


def fig_condenser(a):
    a.rect(399,51,15,220,STEEL,INK)
    for yy in [67,230]:
        a.rect(312,yy,87,14,ICE,BLUE)
        a.rect(295,yy,18,32,ICE,BLUE)
    condenser(a,59,56,126,189)
    a.arrow(195,134,266,134,BLUE)
    a.label("Slide FORE into rails",32,26,12,BLUE)
    a.label("Aft fingers enter recess",251,25,11)
    for xx,yy in [(346,36),(346,174)]:
        a.rect(xx,yy,18,11,ORANGE,INK)
        a.line(xx+9,yy+11,xx+9,yy+32,ORANGE,5)
        a.arrow(xx+9,yy+38,xx+9,yy+56,BLUE)
    a.label("2 x M3 x 8",422,108,12,ORANGE)
    a.label("Vertical axes",422,129,10)
    a.label("Lower screw:",422,166,10)
    a.label("approach aft",422,182,10)
    a.arrow(419,218,382,218,BLUE)
    a.arrow(6,142,49,142,BLUE)
    a.arrow(187,275,283,275,BLUE)
    a.label("Keep fan and grille air paths clear",258,303,12,BLUE,align="center")


def fig_fuse(a):
    a.rect(152,54,203,141,INK,INK)
    a.rect(150,240,207,23,STEEL,INK)
    a.label("RETAINED DONOR COVER",147,30,12)
    a.line(128,201,342,201,BLUE,1)
    a.label("Gap belongs to compressor",293,287,11,BLUE,align="center")
    a.shape([(57,107),(108,107),(108,199),(166,199),(166,216),(96,216),(86,147),(57,147)],ORANGE,INK)
    a.shape([(108,216),(164,216),(164,235),(104,235)],ORANGE,INK)
    a.ellipse(91,119,13,38,STEEL,INK)
    a.line(96,116,96,74,INK,2)
    a.line(96,160,96,204,INK,2)
    a.arrow(34,169,73,169,BLUE)
    a.label("Slide clamp onto",358,106,11,ORANGE)
    a.label("the cover / plate gap",358,127,11,ORANGE)
    a.label("Case against insulated",358,173,11)
    a.label("outside cover flank",358,194,11)
    a.label("77 C one-shot cutoff",32,52,11,BLUE)
    a.label("Case is live: both contact faces remain insulating.",255,310,12,ORANGE,align="center")


def fig_start(a):
    rounded(a,20,30,224,194,INK,INK)
    a.label("thermal",36,58,13,PAPER)
    a.label("0x28  DS18B20  TANK",36,86,11,"#94BFFF")
    a.label("0x10  DS18S20  COIL",36,109,11,"#94BFFF")
    a.label("status",36,144,13,PAPER)
    a.label("Probe health / gas clear",36,171,11,PAPER)
    a.label("Relay + fan + off timer",36,194,11,PAPER)
    compressor(a,318,74,138,145)
    a.arrow(268,94,299,94,BLUE)
    rounded(a,289,235,214,60,ICE,RULE)
    a.label("RECORD ACTUAL CURRENT",304,256,10,BLUE)
    a.label("Compare with donor nameplate",304,279,11)
    a.label("Brief empty-core smoke test",22,262,13)
    a.label("30-60 s under a commissioned control",22,285,10)
    a.label("Observe / stop / honor restart guard",22,306,10,ORANGE)


def fig_thermal(a):
    rounded(a,23,24,248,212,ICE,RULE)
    a.line(55,190,251,190,INK,1)
    a.line(55,51,55,190,INK,1)
    a.line(55,80,251,80,BLUE,1,[4,4])
    a.line(55,126,251,126,BLUE,1,[4,4])
    path(a,[(56,53),(94,126),(129,80),(165,126),(201,80),(245,126)],ORANGE,3)
    a.label("4 C / ON",73,70,11,BLUE)
    a.label("2 C / OFF",73,151,11,BLUE)
    a.label("Carbonator wall",35,220,12)
    rounded(a,295,24,204,212,PAPER,RULE)
    a.label("COIL FREEZE GUARD",308,49,11,BLUE)
    a.label("-8 C / trip",308,85,16,ORANGE)
    a.label("-5 C / recover",308,119,16,BLUE)
    a.label("3 min minimum off",308,164,12)
    a.label("60 s minimum on",308,188,12)
    a.label("Stale probe / 30 s",308,213,12)
    a.label("Record the actual water-load test",32,267,15)
    a.label("Ambient / fill / charge / temperatures / cycles / current",32,296,11,MUTED)


def fig_return(a):
    stages=[("POWER OFF","Isolate + identify",BLUE),("REMOVE CHARGE","Controlled HC route",ORANGE),
            ("CLEAR / REPAIR","Nitrogen + new drier",BLUE),("TEST + EVACUATE","Pressure + microns",BLUE),
            ("METER + CLOSE","Qualified target",BLUE)]
    for i,(title,sub,col) in enumerate(stages):
        y=13+i*56
        rounded(a,68,y,390,44,PAPER,RULE)
        a.label(str(i+1),87,y+27,17,col)
        a.label(title,119,y+18,11,col)
        a.label(sub,119,y+35,10)
        if i<4:
            a.arrow(262,y+47,262,y+55,BLUE,1.5,4)
    a.label("A charged or leaking circuit never goes directly to heat.",263,313,11,ORANGE,align="center")


def fig_record(a):
    rounded(a,29,14,458,279,PAPER,INK)
    a.label("PER-UNIT REFRIGERATION RECORD",47,40,13,BLUE)
    lines=[("Donor / label / actual topology","Pages 2-3"),
           ("Coil / probes / routed protrusions","Pages 4-8"),
           ("HC setup / drier / qualified joints","Pages 10-17"),
           ("Micron trace / charge / final closure","Pages 18-20"),
           ("Mount / airflow / controls / load test","Pages 21-26")]
    for i,(lab,pg) in enumerate(lines):
        y=78+i*39
        a.rect(47,y-10,12,12,PAPER,BLUE)
        a.label(lab,72,y,10)
        a.label(pg,72,y+16,9,MUTED)
        a.line(333,y+12,468,y+12,RULE,1)
    a.label("Name / serial / date / measurements / scope",47,282,10,MUTED)


PAGES = [
    ("Build the cold loop", "Wind the evaporator, transfer the donor circuit, and prove the installed refrigeration assembly.", fig_cover,
     [ ("Follow the physical sequence", "Coil work: pages 4-8. Donor prep and circuit service: 2-3 and 9-20. Mounting and commissioning: 21-28."),
       ("Read the pictures", "Coral marks the current work. Copper is refrigerant tube. Blue marks a tool, gauge or movement. Pictures are schematic; printed dimensions govern."),
       ("Keep the scope honest", "Dry coil and mount work have bench steps. Opening or heating R600a requires the qualified service setup described at the actual operation.") ],
     "CHECK", "A cured cold core alone does not qualify a refrigerant circuit or a finished charge.",
     "cold-core.md / refrigerant-loop.md / enclosure-mechanical.md", None),

    ("Read the donor's label", "Identify the exact appliance and compressor before choosing the service route or supplying power.", fig_labels,
     [("Photograph the real labels", "Record appliance model, refrigerant, factory charge, compressor voltage, frequency and current ratings. Keep each donor's data with its parts."),
      ("Verify R600a", "Use the actual label. A different refrigerant changes handling and circuit suitability. The referenced 15 g and 23 g values are donor baselines."),
      ("Mark the assembly", "Tag Unit A or Unit B and its compressor. Do not infer charge from the cast-stamps or borrow Unit A's electrical lead colors for Unit B.")],
     "DONE WHEN", "The labels and supply ratings are recorded; the finished-machine charge remains separate.",
     "reference/ice-maker/README.md / refrigerant-loop.md §1", None),

    ("Trace what stays", "Walk every tube while the donor is still intact. Mark the cuts and closure plan before dismantling.", fig_salvage,
     [("Keep the useful assembly", "Compressor, condenser/fan, original terminal cover, grommets and the bonded capillary/suction pair stay together."),
      ("Remove the ice-making path", "The finger plate and hot-gas bypass serve ice harvest. Their removal must leave a continuous normal circuit with no bypass or open tee."),
      ("Plan the drier replacement", "The loop-opening session consumes a compatible new drier. Record its capillary connection and preserve metering length or specify a recalculation.")],
     "HOLD", "Unit A's topology is recorded. Trace Unit B at teardown; its exact branch closure is open.",
     "reference/ice-maker/README.md / refrigerant-loop.md §3", MANUFACTURERS["secop_repair"]),

    ("Reserve both coil tails", "Cut the dry coil stock with a tubing cutter, with enough copper for the wrap and each separate routed tail.", fig_lengths,
     [("Use the specified stock", 'GOORY ACR copper, 1/4 in OD x 0.031 in wall. Keep its bore clean and capped. Do not saw refrigerant tubing.'),
      ("Mark the wrap and tails", "Current nominal stock is about 4.85 m total: 4.06 m fitted wrap plus 335.5 mm inlet and 429.6 mm outlet allowances."),
      ("Keep the allowances intact", "Each allowance includes the in-shell route and protrusion. The longer outlet route still leaves the shorter outside working length.")],
     "CHECK", "The two tails are labeled and the ends are round, square, burr-free and protected from dirt.",
     "coil-mandrel/coil_mandrel.py / cold-core.md §1 / handwork.md", None),

    ("Wind the copper coil", "Use the printed mandrel groove to place a single layer of tubing without flattening the bore.", fig_wind,
     [("Start on the correct tail", "Reserve the inlet allowance, register the first wrap in the groove, and keep the tail on its assigned side."),
      ("Follow the helix", "Wind 9.687 wraps at 12.33 mm pitch over 119.4 mm. The mandrel is 123 mm OD. Keep steady contact without crushing or kinking the tube."),
      ("Remove without bending a tail", "Slide the coil axially off the mandrel. Inspect every turn and both exits; a flattened or sharply creased tube is not usable.")],
     "DONE WHEN", "The free coil holds one layer and the inlet/outlet tails leave on opposite assigned lanes.",
     "coil-mandrel/coil_mandrel.py / cold-core.md §1", None),

    ("Dress the bare wall", "Install and prove everything that needs direct steel contact before foil, coil or foam covers it.", fig_wall,
     [("Bond the wall probe", "Tape the DS18B20, family 0x28, flat against bare carbonator steel in the band below the wind. Insulate its leads and route them upward."),
      ("Set the reed bridge", "Use the rod-register azimuth. Calibrate the finished float and both directional liquid crossings before fixing the final bridge position."),
      ("Apply the foil skin", "Apply continuous 3M 425 foil between steel and coil. Preserve the proven sensor positions, lead insulation and the bridge's crossing envelope.")],
     "DONE WHEN", "Probe and reed checks are recorded while every contact point is still reachable.",
     "cold-core.md §1 / magnetic-float/all-aero/installation.md", None),

    ("Transfer and bond the coil", "Slip the wound coil over the foil-dressed 127 mm carbonator, then place the freeze-protect probe.", fig_transfer,
     [("Slide the coil into place", "The wound coil is undersize to hold against the tank. Ease it on without kinking a tail, dislodging a reed or abrading insulated leads."),
      ("Add the coil probe", "Tape the DS18S20, family 0x10, flat against suction-end copper at the high/outlet end. The wall probe stays on steel below the wind."),
      ("Secure and prove", "Bond the thermal contact with foil. Prove both probe families and lead continuity before the mold guide's pre-pour check hides the surfaces.")],
     "CHECK", "Two different probe families: 0x28 on steel; 0x10 on copper. Neither probe floats in foam.",
     "cold-core.md §1 / firmware-and-commissioning.md §6", None),

    ("Route the two exits", "Lower the dressed carbonator into the open shell with one refrigerant tail in each assigned lane.", fig_tails,
     [("Clock by the tails", "The lower/inlet tail takes the port lane. The upper/outlet tail takes the west lane. Avoid torsion where either tail leaves the wrap."),
      ("Measure from each plug face", "Leave 200 mm inlet and 175 mm outlet outside the plug. Measure the physical routed assembly; do not cut away the in-shell part of an allowance."),
      ("Handoff to the mold guide", "The copper plugs close their elongated wall slots, with sensor leads protected. Follow the mold guide for pre-pour inspection and cured closure.")],
     "DONE WHEN", "Both protrusions are recorded and the cured core can be supported with no load on the tube exits.",
     "cold-core.md §§1,5 / coil_mandrel.py / copper-plugs/README.md", None),

    ("Support before teardown", "Remove only the donor casing and supports that prevent access, while keeping the sealed circuit undamaged.", fig_support,
     [("Unplug and identify the leads", "Keep mains isolated. Photograph the factory-external compressor and fan connections. Retain the terminal/PTC cover and its original retention."),
      ("Support each body", "Keep the compressor upright. Support the condenser, fan and evaporator before undoing their fasteners. Copper tubing must not hold their weight."),
      ("Preserve the useful details", "Retain grommets and mounting hardware for inspection. Protect condenser fins, the bonded capillary pair and the process stub. Keep Unit B lead identity open until recorded.")],
     "CHECK", "A missing, cracked, altered or loose terminal cover fails the assembly before power is applied.",
     "reference/ice-maker/README.md / reference/compressor/README.md", None),

    ("Make the HC bench ready", "Complete the service setup before piercing, cutting, pressure testing, evacuation or charging.", fig_bench,
     [("Assign the service work", "A technician trained for R600a chooses the handling route and approves the exact equipment, hoses, connections, ventilation and ignition control."),
      ("Stage the complete session", "Have the replacement drier, joint arrangement, final process closure, dry-nitrogen controls, leak-test method, micron gauge and charge procedure ready."),
      ("Verify the real equipment", "An ultimate vacuum figure and a 1/4 in SAE fitting do not establish hydrocarbon suitability. The owned Orion gear has no recorded exact-model HC approval.")],
     "HOLD", "Opening waits for this setup. The technician's approved method supplies the missing circuit limits.",
     "refrigerant-loop.md / Secop HC service / Orion compatible-use manual", MANUFACTURERS["secop_service"]),

    ("Remove the donor charge", "Use the factory process tube as controlled service access under the approved hydrocarbon-handling method.", fig_remove,
     [("Fit temporary access correctly", "A BPV31 may be fitted if its adapter and instructions match the real tube. Connect the handling rig before piercing or opening."),
      ("Use the approved destination", "The technician records donor end-use, handling route and discharge/collection arrangement. Keep ignition sources outside the defined service area."),
      ("Prove the clearing condition", "Depressurize under the service method. Residual fuel can leave compressor oil; gauge zero and absence of smell alone do not authorize a cut or flame.")],
     "CHECK", "EPA's exemption depends on end use. The donor's status does not authorize venting a rebuilt unit.",
     "refrigerant-loop.md §2 / EPA Section 608 / Supco BPV31", MANUFACTURERS["epa_handling"]),

    ("Cut at the evaporator", "Remove the ice-making evaporator while preserving the donor's metering restriction and bonded heat exchanger.", fig_cuts,
     [("Mark the two functional cuts", "Suction side: near the discarded evaporator outlet. Capillary side: at its evaporator-inlet end. Trace the actual donor before cutting."),
      ("Use the dedicated cutters", "Tubing cutter for normal copper; Mastercool capillary cutter for the hair-bore tube. Clean the outside first and keep every burr or grit particle out."),
      ("Close the bypass correctly", "Remove the harvest solenoid/branch under the donor-specific closure plan. Keep the capillary helix and bonded suction pair without shortening or pulling them apart.")],
     "HOLD", "No improvised tee cap or guessed metering length: qualify the traced branch closure and capillary plan.",
     "refrigerant-loop.md §3 / ice-maker/README.md / Secop repair §§2.1-2.2", MANUFACTURERS["secop_repair"]),

    ("Clear, then replace the drier", "Use the technician's dry-nitrogen sequence to clear each circuit branch and protect every braze internally.", fig_purge,
     [("Clear high and low paths", "Verify the actual gas path and open outlet for each branch. A pressure dial does not prove protective flow through the capillary or compressor."),
      ("Fit a fresh compatible drier", "Cut the used drier out without heating it. Keep the selected replacement sealed until assembly; specify its connection to the retained capillary."),
      ("Protect the open loop", "Continue approved dry protective flow through a joint while brazing. Close and protect any interrupted work against moisture. Keep an unobstructed outlet.")],
     "HOLD", "Nitrogen pressure/flow and drier compatibility are specified by the service plan, not the picture.",
     "refrigerant-loop.md §3 / Secop repair / Uniweld RHP400 specifications", MANUFACTURERS["uniweld_purge"]),

    ("Fit the suction coupling", "Join the upper coil outlet to the retained factory suction line with an ACR-grade 1/4 in slip coupling.", fig_suction,
     [("Prepare the dry fit", "Clean both tube ODs and fitting sockets. Preserve a clean bore. Confirm the coupling takes the actual tube sizes and intended engagement."),
      ("Align without spring load", "Support the core and donor assembly at their installed relationship. Each tube enters straight; the joint must not pull the plug or hang a component."),
      ("Stage for brazing", "For verified copper-to-copper joints, BCuP-5 is self-fluxing. Keep flux out of the sealed loop. Use the qualified purge and plug-protection sequence on page 16.")],
     "DONE WHEN", "The intended engagement is visible/marked, the joint is unstressed and the bore stays clean.",
     "refrigerant-loop.md §5 / Harris Stay-Silv 15 technical sheet", MANUFACTURERS["harris_filler"]),

    ("Prove the capillary joint", "The proposed pinch-swage reduces the coil-inlet tube around the donor capillary. Qualify a sample before the core.", fig_swage,
     [("Measure and try the real pair", "The cited ~0.031 in capillary bore is an estimate. Use matching stock. Establish insertion, forming and braze details on a representative sample."),
      ("Form without closing the bore", "The proposed tool is smooth parallel-jaw Knipex pliers. Progressive rotation collapses the larger tube; the 60-degree suggestion is a trial, not an accepted recipe."),
      ("Record what the sample proves", "Prove the capillary remains open, the required insertion is retained, the braze is sound and the joint meets the specified leak test. Apply only the accepted sequence to the core.")],
     "HOLD", "The metering-joint qualification is open. A closed-looking swage does not prove a working capillary.",
     "refrigerant-loop.md §6 / ice-maker/README.md", None),

    ("Protect the plug, then braze", "Use the qualified heat sink, flame shield and temperature limit at both installed-core joints.", fig_braze,
     [("Qualify the thermal stack", "Use the same copper reach, PETG plug and foam as the installed joint. Measure plug-interface temperature through heating and cooling; justify its allowed limit."),
      ("Make the controlled braze", "With residual-fuel clearing complete and protective nitrogen flowing, use the accepted joint sequence. Direct flame and hot gas away from the core."),
      ("Stop and inspect", "Stop at the qualified temperature/time limit or a failing heat-sink contact. Let the joint cool, then inspect the plug and foam boundary before the second braze.")],
     "HOLD", "A wet rag's boiling-point behavior is above nominal PETG Tg (~80 C). It does not qualify this stack.",
     "refrigerant-loop.md §4 / copper-plugs/README.md / Secop HC service", MANUFACTURERS["secop_service"]),

    ("Test the closed circuit", "Pressure leak-test after all joints are complete and cool, before evacuation and the first R600a charge.", fig_pressure,
     [("Use the written test limits", "Dry nitrogen, regulated and pressure-protected. The technician specifies pressure, time, temperature correction and decay acceptance from the weakest rated component."),
      ("Inspect every new connection", "Include both coil joins, replacement drier joins, hot-gas branch closure and the planned final service/process connection. Use the qualified leak-test method."),
      ("Record and depressurize", "Log the gauges, starting/ending pressure, elapsed time and all inspected sites. Release test gas under the service method before connecting the vacuum rig.")],
     "HOLD", "Circuit pressure-test limits are open. The stainless water-vessel hydro-test does not supply them.",
     "refrigerant-loop.md §7 / Secop repair §3.4", MANUFACTURERS["secop_repair"]),

    ("Measure the vacuum", "Read absolute pressure at the circuit with suitable HC evacuation equipment; keep that gauge on the isolated system.", fig_vacuum,
     [("Place the system gauge", "An absolute micron gauge reads the circuit, not the isolated pump. Keep the compressor off and route pump exhaust to the approved outdoor location."),
      ("Reach the project target", "The current target is 500 microns or less, with at least 15 minutes while pumping. Record the actual pressure trace; a compound manifold dial cannot prove it."),
      ("Isolate and observe", "Isolate the pump and record the next 15 minutes at the system gauge. Diagnose a rapid rise. Some rebound is possible; use the technician's written decay limit.")],
     "HOLD", "The isolated-pressure acceptance and exact equipment approval must be settled before charging.",
     "refrigerant-loop.md §7 / Secop repair §§2.8-2.9", MANUFACTURERS["secop_repair"]),

    ("Meter the qualified charge", "Use the finished-machine charge recipe and account for the refrigerant that remains outside the circuit.", fig_charge,
     [("Start from an accepted target", "The redesigned evaporator has no qualified charge mass yet. Neither the donor's 15/23 g nor an automatic volume overage is the final recipe."),
      ("Keep the scale honest", "The owned scale resolves 0.1 g. Check its response with a known mass; support hoses independently so their pull cannot change the reading."),
      ("Record net delivery", "Follow the technician's refrigerant state/orientation and valve sequence. Record start/end mass, hose inventory and net to circuit. The project metering target is +/-1 g.")],
     "HOLD", "Charging waits for the calibrated target, refrigerant grade and a repeatable net-delivery method.",
     "refrigerant-loop.md §8 / Secop repair §3.1", MANUFACTURERS["secop_repair"]),

    ("Finish the process access", "Leave a qualified permanent closure or service fitting, then check it after the charging connection is removed.", fig_close,
     [("Use the specified closure", "The technician's plan establishes the final fitting/closure and when it is made. A charged circuit must not go directly to a torch."),
      ("Remove temporary piercing access", "Supco's FAQ warns solderless piercing valves can leak over time and says they should not remain after repair. Do not leave the BPV31 as the lifetime service point."),
      ("Check the final state", "After disconnection, test the final closure, caps/threads and every joint with the qualified R600a leak method. Record detector identity and proof check.")],
     "DONE WHEN", "The final closure is recorded and leak-tested; no temporary saddle is counted as the permanent seal.",
     "refrigerant-loop.md §§8-9 / Supco BPV31 FAQ", MANUFACTURERS["supco_access"]),

    ("Place the gas sensor first", "Install the MQ-6 in the open floor strip before the compressor makes the slot hard to reach.", fig_sensor,
     [("Orient the card on edge", "The card runs along the west (-X) flank. Mesh faces west into the wall well; its header faces east into the bay."),
      ("Lower into the grooves", "Drop the card straight between the two printed posts until it lands on their shoulder. Route its loom without lifting the card or blocking the low floor zone."),
      ("Check installed response later", "A located sensor is not a commissioned interlock. Prove module polarity, clean-air behavior and actual compressor shutdown under the approved test method.")],
     "CHECK", "The gas module is reachable, correctly oriented and retained; its threshold/shutdown evidence remains open.",
     "enclosure-mechanical.md §3 / concerns.md / refrigerant-loop.md", None),

    ("Lower the compressor", "Mount the connected refrigeration assembly without transferring its weight into the copper lines.", fig_mount,
     [("Face the power end forward", "Keep the original covered terminal/PTC assembly intact. Support the cold core and condenser while lowering the plate straight onto all four floor posts."),
      ("Use the four intended stacks", "M5 x 10 SHCS with OD25 fender washers, into RX-M5x9.5 inserts. The posts rise through the rubber grommets; keep the grommets seated."),
      ("Stop at the post crown", "The washer is intended to land on the post after nominal 0.4 mm flange squeeze. Check the real bearing path and isolation; there is no accepted torque or load-life result.")],
     "DONE WHEN", "All four stacks land without crushing rubber, hanging on tubework or forcing an insert.",
     "enclosure-mechanical.md §3 / BOM §13 / mechanical-qualification/README.md", None),

    ("Seat the condenser and fan", "Use the printed rails and aft fingers to carry the condenser block above the slab.", fig_condenser,
     [("Enter the aft recess", "Feed the aft end onto the mounting fingers, then slide fore until the front flanges enter the rail grooves and the face meets their shoulder."),
      ("Close the two mounts", "Drive the two M3 x 8 screws down through the donor's aft flange holes into the fingers' inserts. Approach the lower screw from aft with the bay still open."),
      ("Keep the air path open", "Confirm the native fan's installed flow direction, clear fins and cross-cabinet inlet/exhaust grilles. Inspect every attached line for stress or rubbing.")],
     "CHECK", "The block is supported by its mounts, the fan turns freely and airflow is confirmed on the real donor.",
     "enclosure-mechanical.md §3 / condenser-block/README.md", None),

    ("Seat the thermal cutoff", "The 77 C one-shot fuse reads through contact with the outside flank of the retained donor power cover.", fig_fuse,
     [("Keep the live case insulated", "The cover and printed clamp are the insulating contact surfaces. Keep bare case/leads clear of the compressor can and plate; wiring follows the AC schedule."),
      ("Place the case and clamp", "Seat the fuse along its channel against the cover flank. Slide the clamp's leaves into the cover-to-plate gap so the clamp rides with the compressor."),
      ("Inspect the actual fit", "The fuse must contact the cover without damage or a loose air gap. Nominal CAD diameter does not prove contact across case/print tolerance; preserve required straight lead length.")],
     "HOLD", "Installed retention, contact and insulation need bench evidence before the cutoff is credited as protection.",
     "refrigeration/fuse-clamp/README.md / sf76e-thermal-fuse / concerns.md", None),

    ("Prove the first start", "Finish electrical commissioning and leak checks before a brief compressor smoke test.", fig_start,
     [("Read real probes", "Use thermal and status on the shipping firmware. Require family 0x28 on the tank and 0x10 on the coil; de-energized ambient checks are within +/-2 C."),
      ("Prove the control path", "Use a commissioned bench control, with gas interlock and condenser fan working. Honor the 3-minute firmware off guard and any longer donor restart requirement."),
      ("Observe and stop", "For the empty-core smoke test, 30-60 s is the procedure's brief window. Record actual nameplate-compatible current and falling coil temperature; stop for hum, overload or a leak.")],
     "CHECK", "This proves switching and probe location only. It does not establish water-load performance or lifetime.",
     "firmware-and-commissioning.md §§6,8 / src_appliance/README.md", None),

    ("Prove the loaded cold loop", "Commission refrigeration with the documented water load and verify the actual control limits.", fig_thermal,
     [("Confirm current firmware values", "Tank: on at 4 C, off at 2 C. Coil: trip at -8 C, recover at -5 C. Minimum off 3 min, on 60 s; stale probe after 30 s parks cooling."),
      ("Run the specified loaded test", "Record water fill, ambient, actual charge, starting temperatures, pull-down, outlet-water temperature, coil trend, current and cycle timing."),
      ("Keep acceptance distinct", "The acceptance document's 8-hour window and 10-70% duty band are proposed defaults. Missing loaded measurements and a qualified charge block production acceptance.")],
     "DONE WHEN", "The logged control behavior and load result meet a committed test specification, with no leak alarm.",
     "cold_policy.h / firmware-and-commissioning.md §9 / acceptance-and-burn-in.md", None),

    ("Repair through the full sequence", "A leak or abnormal operation returns to diagnosis and controlled service, not direct reheating.", fig_return,
     [("Stop and identify the fault", "Isolate power, keep the area ventilated and use the approved leak/diagnostic method. A gas alarm, repeated freeze trip or overload is not a tune-by-guessing cue."),
      ("Remove charge under the right route", "The completed dispenser's end-use basis and HC equipment govern removal. Do not borrow the donor's venting exemption."),
      ("Repeat the relevant proof", "After opening: replace drier, clear/purge, repair, test, evacuate, meter charge and finish access. Record the cause and repeat the affected installed/load checks.")],
     "CHECK", "Any route that skips charge removal or residual-fuel clearing before heat fails this sequence.",
     "refrigerant-loop.md §§2-9 / EPA Section 608 / Secop HC service", MANUFACTURERS["secop_service"]),

    ("Keep the unit's evidence", "The guide supplies order and pictures; the per-unit record establishes which work and measurements were completed.", fig_record,
     [("Keep the measured result", "Attach donor labels, coil/probe checks, service setup, joint qualifications, leak record, vacuum trace, net charge, final closure and installed control/load results."),
      ("Use the written sources", "The footer names the responsible procedure or part reference. Click a source footer for an external service source where supplied; the README indexes local documents."),
      ("Keep this guide manual", "Rebuild it deliberately when its operation changes. The PDFs and source receipt are committed artifacts; the appliance build does not redraw them.")],
     "HOLD", "Open service limits, joints, charge and commissioning claims are visible at their operation, not signed off by this book.",
     "refrigeration-guide/README.md / mechanical-qualification/README.md", None),
]


def draw_page(c, n, page):
    title, sub, figure, actions, kind, gate, source, link = page
    begin_page(c)
    header(c, n, title, sub, len(PAGES), "REFRIGERATION")
    panel(c,32,140,548,340)
    with Art(c,46,148) as a:
        figure(a)
    y=498
    for i,(label,copy) in enumerate(actions):
        badge(c,i+1,32,y,label,size=13)
        h=paragraph(c,copy,63,y+25,510,size=11.25,leading=13.5,max_height=41)
        y += 63
    if y>694:
        raise ValueError(f"Actions spill on page {n}")
    box(c,32,699,548,41,"#FBEDE5" if kind=="HOLD" else ICE,radius=5)
    text(c,kind,43,714,8.5,"PlexBold",ORANGE if kind=="HOLD" else BLUE)
    paragraph(c,gate,43,719,522,size=9.7,leading=11.2,max_height=22)
    if link is None:
        local_sources = {
            1:"hardware/assembly/refrigerant-loop.md",
            2:"hardware/reference/ice-maker/README.md",
            4:"hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py",
            5:"hardware/printed-parts/cold-core/coil-mandrel/coil_mandrel.py",
            6:"hardware/assembly/cold-core.md",7:"hardware/assembly/cold-core.md",
            8:"hardware/assembly/cold-core.md",9:"hardware/reference/ice-maker/README.md",
            15:"hardware/assembly/refrigerant-loop.md",
            21:"hardware/assembly/enclosure-mechanical.md",
            22:"hardware/assembly/enclosure-mechanical.md",
            23:"hardware/assembly/enclosure-mechanical.md",
            24:"hardware/printed-parts/refrigeration/fuse-clamp/README.md",
            25:"hardware/assembly/firmware-and-commissioning.md",
            26:"firmware/lib/machine_policy/cold_policy.h",
            28:"hardware/refrigeration-guide/README.md",
        }
        link="https://github.com/derekbreden/homesodamachine/blob/main/"+local_sources[n]
    footer(c,n,source,link)
    end_page(c)


def build():
    numbers=verify_manual_numbers()
    PDF.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(PDF),pagesize=(W,H),pageCompression=1,invariant=1)
    c.setTitle("Home Soda Machine - Refrigeration bench guide")
    c.setAuthor("Home Soda Machine")
    c.setSubject("Manual illustrated Letter instructions, service hold points and measured evidence")
    for n,page in enumerate(PAGES,1):
        draw_page(c,n,page)
    c.save()
    publish(PDF,GUIDE,"Refrigeration bench guide",
            f"Coil, donor circuit, HC service, mounts and commissioning - {len(PAGES)} illustrated Letter pages",
            len(PAGES),SOURCES,extra={
                "manufacturer_sources":MANUFACTURERS,
                "manufacturer_sources_checked":"2026-10-04",
                "manual_number_review":numbers,
                "qualification_scope":"Manual sequence and source review; no installed HC service, charge, joint, thermal or load qualification claimed",
                "page_inventory":[{"page":n,"operation":page[0]} for n,page in enumerate(PAGES,1)],
            })
    print(f"{PDF} ({len(PAGES)} Letter pages)")


if __name__=="__main__":
    build()
