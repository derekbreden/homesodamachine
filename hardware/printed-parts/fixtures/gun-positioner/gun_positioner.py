"""Bench gun positioner: fabrication solids and catalog-envelope references.

Run with tools/cad-venv/bin/python.  No motion, printer or welder is contacted.
All dimensions are millimetres.  Blank-local XY is the drilling-template plane.
The world frame is the rotator tube axis, Z up; the reference weld point is
(-61.85, 0, 278.40). Catalog envelopes are explicitly separate from fabrication
solids. Each metal plate has a DXF and a dimensioned one-to-one SVG template.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "scripts"))
from _material_base import M_PETGF_BLACK  # noqa: E402
T = 6.35
LEAD = 2.0
RATIO = 4
LEVER = 150.0
L0 = 180.0
TRAVEL = 85.0
HARD_TRAVEL = 94.0
ANGLE = 20.0
HARD_ANGLE = 22.0
SHAFT_D = 12.0
RAIL_LENGTH = 400.0
RAIL_SEPARATION = 140.0
BLOCK_SEPARATION = 128.0
BLOCK_X = 39.0
BLOCK_Y = 41.0
BLOCK_H = 28.0
BLOCK_HOLE_X = 26.0
BLOCK_HOLE_Y = 28.0
# Mating rail's support height is a catalog-envelope parameter, not a fit claim.
RAIL_CENTER_H = 22.5
BLOCK_TOP_FROM_CENTER = 17.5
DECK = RAIL_CENTER_H + BLOCK_TOP_FROM_CENTER
KP12_H = 19.0
KP12_W = 71.0
KP12_L = 16.0
KP12_HOLES = 56.0
FORCE_END = 32.525
FORCE_SPRING_GAP = 23.0
FORCE_CAPTURE = 1.0
NUT_BODY_D = 10.2
NUT_FLANGE_D = 22.0
NUT_FLANGE_H = 3.5
NUT_LENGTH = 15.0
NUT_HOLE_PCD = 16.0
TOOL = np.array([200.0, 0.0, 47.35])
DOT = np.array([-61.85, 0.0, 278.40])
COLORS = {
    "aluminum": (0.68, 0.72, 0.75), "steel": (0.36, 0.39, 0.42),
    "brass": (0.72, 0.57, 0.23), "PET-GF": M_PETGF_BLACK.toTuple()[:3],
    "TPU": (0.20, 0.24, 0.28), "motor": (0.16, 0.18, 0.20),
    "gun-proxy": (0.79, 0.24, 0.30), "fiber-proxy": (0.36, 0.52, 0.60),
}
PARTS: dict[str, dict] = {}
# Nominal capture stacks. Final lengths use the delivered inner-race faces.
CAPTURE_STACKS={
    'yaw':[(31.35,35.15),(83.5,16),(131.85,14.65),(163.5,11.5)],
    'pitch-negative':[(0,9.5),(41.35,15.15),(73.5,25.15)],
    'pitch-positive':[(31.35,25.15),(73.5,11.5)],
    'roll':[(0,21.5),(38.5,12),(82.35,27.15),(126.5,1.15),(159.5,5.5)],
}

def capture_tube_name(length):
    return 'shaft-capture-tube-'+f'{length:.2f}'.replace('.','p')


def rotation(axis: str, angle: float) -> np.ndarray:
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


R0 = rotation("z", 105) @ rotation("y", 60)
C0 = DOT - R0 @ TOOL
STAGE_CENTER = C0 + np.array([-180.0, 0.0, 0.0])


def transform(R=None, p=(0, 0, 0)) -> cq.Location:
    R = np.eye(3) if R is None else np.asarray(R)
    return cq.Plane(origin=tuple(float(v) for v in p),
                    xDir=tuple(float(v) for v in R[:,0]),
                    normal=tuple(float(v) for v in R[:,2])).location


def cylinder(d, length):
    return cq.Workplane("XY").circle(d / 2).extrude(length)


def box(x, y, z):
    return cq.Workplane("XY").box(x, y, z, centered=(True, True, False))


def hole_grid(x, y, d=5.5, center=(0, 0)):
    return [[center[0] + a * x / 2, center[1] + b * y / 2, d]
            for a in (-1, 1) for b in (-1, 1)]


def register(name, model, *, material, kind, qty=1, size=None, holes=(),
             slots=(), notes="", print_orientation="XY, flat underside down"):
    PARTS[name] = dict(model=model, material=material, kind=kind, quantity=qty,
                       blank_mm=size, template_type=None, holes=[list(h) for h in holes],
                       slots=[list(s) for s in slots], notes=notes,
                       print_orientation=print_orientation)
    return name


def plate(name, x, y, holes=(), slots=(), *, thickness=T, qty=1, notes=""):
    model = box(x, y, thickness)
    for hx, hy, hd in holes:
        model = model.cut(cylinder(hd, thickness + 2).translate((hx, hy, -1)))
    for sx, sy, length, width, angle in slots:
        cutter = cq.Workplane("XY").center(sx, sy).slot2D(length, width, angle).extrude(thickness + 2)
        model = model.cut(cutter.translate((0, 0, -1)))
    register(name, model, material="aluminum", kind="metal", qty=qty,
             size=[x,y,thickness],holes=holes,slots=slots,notes=notes)
    PARTS[name]["template_type"]="plate"
    return name


def init_parts():
    if PARTS:
        return
    blocks = [h for a in (-1, 1) for b in (-1, 1)
              for h in hole_grid(BLOCK_HOLE_X, BLOCK_HOLE_Y,
                                 center=(a * BLOCK_SEPARATION / 2, b * RAIL_SEPARATION / 2))]
    plate("x-bed", 450, 199, hole_grid(400, 160, 6.5),
          notes="Rail bases are transfer-drilled from the received rails. Keep rail centers 140mm apart. The four 6.5mm holes attach to the common metal frame.")
    plate("x-carriage", 210, 199, blocks + hole_grid(180, 180)+[[14.175,-51,5.5],[14.175,51,5.5]])
    plate("y-bed", 450, 199, hole_grid(180, 180),
          notes="Turn this blank 90 degrees. Rail bases are transfer-drilled; holes at the center attach to the X carriage with four 40 mm long, 10 OD / 8 ID metal tube standoffs on a 180 x 180 mm pattern.")
    plate("y-carriage", 210, 199, blocks + hole_grid(180, 180)+[[14.175,-51,5.5],[14.175,51,5.5]])
    plate("z-bed", 450, 199, hole_grid(400, 160, 6.5),
          notes="Turn blank vertical. Rail bases are transfer-drilled. Back onto two continuous 4040 uprights.")
    plate("z-carriage", 210, 199, blocks + hole_grid(180, 180)+[[-14.175,-51,5.5],[-14.175,51,5.5],[-20,0,6.5],[80,0,6.5]])
    for bedname in('x-bed','y-bed','z-bed'):
        d=PARTS[bedname]
        for hx in(-171,171):
            for hy in(-10,10):
                d['model']=d['model'].cut(cylinder(6.5,T+2).translate((hx,hy,-1)))
                d['holes'].append([hx,hy,6.5])
    plate("force-gauge-backing",70,110,hole_grid(41,73,4.5),notes="Gauge is vertical in drill vise, load axis up. Included rear M4 screws only: verify socket depth and engagement before tightening.")
    for x in(-28,28):
        PARTS['force-gauge-backing']['model']=PARTS['force-gauge-backing']['model'].cut(cylinder(5.5,T+2).translate((x,48.2,-1)))
        PARTS['force-gauge-backing']['holes'].append([x,48.2,5.5])
    register('deck-metal-spacer',cylinder(10,40).cut(cylinder(8,42).translate((0,0,-1))),material='aluminum',kind='metal',qty=4,size=[10,10,40],notes='Four 10 OD / 8 ID metal tube spacers, 40 mm long, between X carriage and Y bed on180 x180 mm centers. M5x70 through-bolts; no 40 mm square spacer obscuring block screws.')
    PARTS['deck-metal-spacer']['template_type']='tube'
    register('proof-gauge-rear-spacer',cylinder(10,7).cut(cylinder(8,9).translate((0,0,-1))),material='aluminum',kind='metal',qty=4,size=[10,10,7],notes='Four 7 mm metal spacers keep the gauge rear case clear of proof quill-cap screws. Use four separately allocated M4x25 screws finished to the actual socket depth and at least 4 mm engagement; two dedicated large M4 washers per screw. The normal gauge screws are a separate set.')
    PARTS['proof-gauge-rear-spacer']['template_type']='tube'
    register('proof-bearing-riser',cylinder(10,10).cut(cylinder(8,12).translate((0,0,-1))),material='aluminum',kind='metal',qty=2,size=[10,10,10],notes='Two 10 mm metal risers lift the temporary KP001 support above the reaction plate lower edge. ID8 / OD10; M6x40 through bolts, original bearing nuts and washers reused.')
    PARTS['proof-bearing-riser']['template_type']='tube'
    plate("installed-Z-gauge-back",70,160,hole_grid(41,73,4.5),[[0,-72,12,6.5,90],[0,72,12,6.5,90]],notes="Temporary installed-load gauge mount on independently braced500 mm4040 test column. Two M6x25 slot8 screws and10 mm metal spacers clear rear M4 screw heads. Gauge axis upward under the retained Z-head foot; measured force bounds weight, cable and rail drag.")
    for x in(-28,28):
        PARTS['installed-Z-gauge-back']['model']=PARTS['installed-Z-gauge-back']['model'].cut(cylinder(5.5,T+2).translate((x,48.2,-1)))
        PARTS['installed-Z-gauge-back']['holes'].append([x,48.2,5.5])
    plate('shaft-capture-interface',100,60,[[0,0,22]]+hole_grid(26,20)+hole_grid(60,40,3.4),notes='Temporary metal interface on the hub face nearest a shaft end. The 22 mm aperture clears the complete 20 mm keeper and end-bolt head. Four M5x80 temporarily retain the actual output plate, hub and this interface; four separate M3 tie stations carry the symmetric 75 mm bridge spacers. Actual hub clamps and bearing setscrews are loose during axial proof.')
    plate('shaft-capture-bridge',100,60,[[0,0,6.5]]+hole_grid(60,40,3.4),notes='Closed coaxial force bridge beyond the complete shaft keeper. Four 75 mm metal tubes and four borrowed M3x100 ties connect the separate interface. A captured M6x16 bolt, one 1 mm washer and a 20 mm steel M6 coupling nut connect directly to the gauge load shaft. At least 6 mm measured engagement at both ends, no bottoming and no hook or cord load connection.')
    plate('capture-catch-upper',120,80,hole_grid(100,40,6.5),notes='Upper plate of a temporary independent catch. The lower plate is the borrowed drive-test-foot. Two 7.85 mm tube spacers and two borrowed M5x35 joints at the far X=-50 stations join the catch plates; nearer holes remain unused, clear of the moving interface. Vise grips only joined far-end metal and is positively bench mounted. Set 0.75 mm nominal clearance above and below the moving interface, verify no contact during proof.')
    for name,od,bore,length,qty,note in [('capture-bridge-spacer',8,6,75,4,'Four symmetric metal tubes between capture interface and closed bridge. No contact with shaft, keeper or bearing housing.'),('capture-catch-spacer',8,6,7.85,2,'Two far-end metal spacers join the independently mounted catch plates; not in the measured force path.'),('capture-gauge-guide-spacer',10,8,9.825,2,'Column-to-gauge-back guide offset. Guide screws retain laterally with sliding axial clearance and must not clamp the backing.'),('capture-bearing-riser',10,8,12.825,2,'Temporary axial-proof bearing risers place the shaft axis 78.175 mm from the column rear datum, coaxial with the positive gauge connection and manual jack.')]:
        register(name,cylinder(od,length).cut(cylinder(bore,length+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=qty,size=[od,od,length],notes=note)
        PARTS[name]['template_type']='tube'
    register('gauge-M6-coupling',cq.Workplane('XY').polygon(6,11.547).extrude(20).cut(cylinder(6,22).translate((0,0,-1))),material='steel',kind='catalog',qty=1,notes='B0DHGXW6G9 304 steel M6x1 coupling nut, 20 mm long and 10 mm across flats. Measure received gauge load-thread identity and usable thread depth. At least 6 mm engagement at each end, no bottoming, witness after adjustment. Direct positive connection transmits compression and tension; actual source is recorded in purchases.')
    plate('installed-Z-load-platen',60,40,qty=1,notes='Horizontal metal platen under the40 mm hollow Z-head upright. Gauge probe contacts only its center; independent support remains within1 mm below the load. No contact with fixed mast or actuator. Do not detach actuator until gauge and support restrain the complete carried load.')
    register('installed-Z-gauge-spacer',cylinder(10,10).cut(cylinder(8,12).translate((0,0,-1))),material='aluminum',kind='metal',qty=2,size=[10,10,10],notes='Ten millimetre metal10OD/8ID spacers offset70x160 gauge backing from4040 test column so rearM4 gauge screw heads remain clear.')
    PARTS['installed-Z-gauge-spacer']['template_type']='tube'
    plate("test-output-bridge",140,40,[[0,0,6.5]]+hole_grid(130,20),notes="Symmetric bridgeahead ofthetestrodtip. GaugeM6compressionbuttoncontactscenter; metalforkarmstouchonlyshuttle, neverfixedcage.")
    plate("test-output-arm",70,25,[[-25,0,5.5],[25,0,5.5]],qty=2,notes="Two symmetricmetaloutputforkarmsoutsidefixedcage.Boltonlytoshuttle andfrontbridge throughmetalangles; preventsloadbypass.")
    plate("drive-test-foot",120,80,hole_grid(100,40,6.5),notes="Clampmetaltestcartridgefootontodrilltable/bench.Spare200 mmtestleadpermitscoaxialgaugecontactahead ofrodtip.No drillpower; motorsonly.")
    plate("force-test-platen",120,80,[[0,0,10.5]]+hole_grid(100,30),qty=1,
          notes="Test platen reacts only on fixed cage outer ties. Gauge M6 load stud bears itscenter through a spherical suppliedbutton; pusher touches only the output shuttle. Reversible loose-link test, drill unplugged.")
    plate("torque-redirect-bracket",60,40,[[0,0,8.5],[-20,-10,6.5],[20,-10,6.5]],notes="Vise-held metal support for a608ZZ redirectwheel. M8 smoothshank axle clamps only innerrace; characterize cordloss withtwoequal200 g cups and<=5 g imbalance inbothdirections.")
    plate("yaw-head-adapter",120,120,[[-11,y,5.5] for y in(-30,0,30)],
          notes="Horizontal adapter on metalheadbeam. Two M6 T-slot holes transfer frombeamtop at100 mm spacing. Three metalangles connectyawback verticalplane to thisflatplate; rotated105 degreesaroundZ.")
    plate("z-head-diagonal",275,25,[],[[-122.5,0,10,6.5,0],[122.5,0,10,6.5,0]],
          notes="Flat metal diagonalbrace toextrusionYface. Hole span245 mm, two10 mm slots accommodate frameplacement. M6 screwsinto slot8 Tnuts; no printedbrace loadpath.")
    plate("rotator-platform", 325, 300, hole_grid(210,200,8.5),
          notes="Common metal frame top40mm; platform6.35mm; rotator foot24mm. Four through-bolts attach to the rotator's base bench holes after direct transfer. Existing six-inch tube/endcap reference seam height278.40mm.")
    plate("yaw-bearing-back", 180, 90, [[a, b, 7] for a in (-40, 40) for b in (-KP12_HOLES/2, KP12_HOLES/2)]+[[-58.85,y,5.5] for y in(-30,0,30)],
          notes="KP12 feet: drawing is a catalog envelope. Transfer the selected housing holes; the selected bolt stations are 56 mm apart; transfer actual housing holes.")
    plate("yaw-crossbar", 100, 380, [[0, 0, 12.5]] + hole_grid(26, 20) +
          [[x, y, 5.5] for x in (-30, 30) for y in (-177, 177)])
    plate("yaw-side", 100, 180, [[x, y, 5.5] for x in (-30, 30) for y in (-70, 50)], qty=2)
    plate("pitch-bearing-foot", 90, 60, [[-28, 0, 7], [28, 0, 7],[0,-20,8.5],[0,20,8.5]] + hole_grid(60, 40), qty=2,
          notes="Transfer housing bolt centers if the selected KP12 differs. The outer 60 x 40 pattern attaches metal angles. Two centerline 8.5 mm holes at Y +/-20 are used only for temporary proof-beam M8 slot8 mounts.")
    plate("pitch-side", 280, 100, [[125, 15, 12.5]] + hole_grid(26, 20, center=(125, 15)) +
          [[x, y, 5.5] for x in (-110, -10) for y in (-30, 10)], qty=2)
    plate("pitch-rear-crossbar", 190, 40, hole_grid(180, 20), qty=2)
    plate("roll-bearing-foot", 150, 120, [[x, y, 7] for x in (-45, 43) for y in (-28, 28)] +
          [[x,y,5.5] for x in(-70,30) for y in(-50,50)], notes="KP12 housings are at 90mm span. Front center is X=-122 mm; housing bolt holes transfer from parts if needed.")
    plate("roll-cradle-side", 216, 60, [[x, y, 5.5] for x in (-85, 15, 75) for y in (-20, 10)], qty=2)
    plate("roll-cradle-back", 120, 70, [[0, 0, 12.5]] + hole_grid(26, 20) + hole_grid(100, 40))
    plate("gun-jaw", 25, 130, [[0, -56, 5.5], [0, 56, 5.5],[0,-32,5.5],[0,32,5.5]], qty=4,
          notes="Two lower and two upper metal bars. Adjustable spacing along the cradle; clamp only unobstructed gun-body areas. Top bars slide on four M5x80 through-bolts.")
    plate("service-load-jaw",35,160,[[0,-56,5.5],[0,56,5.5],[10,-70.475,5.5],[10,70.475,5.5]],qty=2,
          notes="Temporary nozzle force fork jaws. Two M5x80 clamp bolts use Y +/-56; single angle bolts use local X10,Y +/-70.475. Minimum simultaneous M5 washer-center separation 17.59 mm. Working gun jaws are separate parts.")
    lever_holes = [[0, 0, 12.5]] + hole_grid(26, 20) + [[150, 0, 8.5]]
    plate("angular-lever", 190, 50,
          [[x - 75, y, d] for x, y, d in lever_holes]+hole_grid(18,18,center=(75,0)), qty=3,
          notes="Pivot datum is at X=-75mm. Output clevis datum is at X=+75mm; exactly 150mm apart.")
    plate("drive-bulkhead", 38, 60, [[0, 0, 10.5]] + hole_grid(24,44,6.5)+[[-5,13,3.4],[5,13,3.4]], qty=6,
          notes="Metal thrust stack, F8-16M on both sides. Four M6 posts are the shared metal-angle mounting fasteners; there is no overlapping M5 pattern. Plastic only locates the cover.")
    plate("linear-drive-support",150,150,hole_grid(100,70,center=(0,-25)),qty=6,notes="Universal fixed-drive floor, top26.35 mm below screw datum. XYZ floorslapunderbedand useonlythefronttwoholes;angularfloor attaches toitsmetalbulkheadlegs. Pulleyandfrontshieldslots clearrotatingparts.")
    floor=PARTS['linear-drive-support']
    for bx,by,w,h in((1.8,-55,10,60),(20,-57,4,104)):
        floor['model']=floor['model'].cut(box(w,h,T+2).translate((bx+w/2,by+h/2,-1)))
    floor['cutouts']=[[1.8,-55,10,60],[20,-57,4,104]]
    plate('motor-support-leg',100,25,[[36.35,0,5.5],[-37.3,0,5.5]],qty=12,notes="Two metal stanchions per motor. LocalX isvertical; bottomfloor=-26.35 relativetoscrew, top73.65. Upperandlower25.4 mmanglesconnectmotorplateandfloor. No floatingprintedmotorbracket.")
    plate('thrust-support-leg',42.65,38,[[9.675,0,5.5],[-14.325,0,5.5],[-9.625,12,5.5]],qty=12,notes="Two metalstanchions perbulkhead. SharedM6 mountinganglesattachbothpoststations; lowerangleattachesatfloor+6.35 mm. Lower foot datum is X41.05 mm, giving 12.89 mm minimum M5 head/washer separation. XYZ bed provides that pad; angularflooruses6.35 mmmetalpad.")
    plate('thrust-angle-pad',25.4,25.4,[[0,0,5.5]],qty=6,notes="6.35 mm metalpad undertwo thrustfootangles per angularfloor; matchesXYZ bedthickness. No printedload spacer.")
    register('kp08-fixed-riser',cylinder(10,11.35).cut(cylinder(8,13).translate((0,0,-1))),material='aluminum',kind='metal',qty=12,size=[10,10,11.35],notes='Two metal11.35 mm risers per fixedKP08 bearing; finishactualheight fromreceivedcenterheight to keep screwaxis26.35 mm abovefloor. ID8/OD10; M4 washers at least10 OD bridge the bore. M4x35 through floor.')
    register('kp08-floating-riser',cylinder(10,5).cut(cylinder(8,7).translate((0,0,-1))),material='aluminum',kind='metal',qty=6,size=[10,10,5],notes='Two metal5 mm risers perXYZ floatingKP08 bearing; finishactualheight forselectedcenterheight, noaxialnutoutsidebearing. M4x30 throughbed.')
    PARTS['kp08-fixed-riser']['template_type']='tube';PARTS['kp08-floating-riser']['template_type']='tube'
    plate("nut-face", 46, 38, [[0, 0, 10.5]] + hole_grid(34,24),
          [[8*math.cos(math.radians(a)),8*math.sin(math.radians(a)),8,4.2,a+90] for a in (0,90,180,270)],qty=12,
          notes="TR8 flange sits against this metal face; four M3x20 through-bolts with large washers and locking nuts. Tangential slots permit mountingthe singlemovingnut without forcingthe sourceflange. Four metal 30 mm spacers carry the frame load; the printed locator is 0.5 mm short at each side. There is one driving nut per axis.")
    plate("force-link-end", 110, 38, [[0,0,10.5],[-36,0,8.5],[36,0,8.5]]+hole_grid(34,24)+hole_grid(100,30), qty=12,
          notes="Two per axis. Four inner M5x90 ties join nut faces to end plates. Four outer M5x90 ties connect shoulder plates through metal spacers. Two M8x90 smooth-shank guide bolts carry four 20 mm free springs. Set preload by measured force.")
    shuttle=box(110,38,T).cut(box(50,28,T+2).translate((0,0,-1)))
    shuttle_holes=[[-36,0,12.1],[36,0,12.1]]+hole_grid(100,30,8.5)+[[x,0,5.5] for x in(-51,51)]
    for gx in(-36,36):shuttle_holes+=hole_grid(16,16,3.4,center=(gx,0))
    for hx,hy,hd in shuttle_holes:shuttle=shuttle.cut(cylinder(hd,T+2).translate((hx,hy,-1)))
    register("force-link-shuttle",shuttle,material="aluminum",kind="metal",qty=6,size=[110,38,T],holes=shuttle_holes,
             notes="Central opening 50 x 28 mm. Four M3x30 bolts clamp each pair of metal boss halves to this plate. Bronze8 ID/12 OD/10 mm bushings guide smooth M8 shanks. Outer8.5 mm holes clear stationary metal tie spacers; four5.5 mm holes attach metal output angles.")
    PARTS['force-link-shuttle']['template_type']='plate'
    PARTS['force-link-shuttle']['cutouts']=[[-25,-14,50,28]]
    shoulder=box(110,38,T).cut(box(50,28,T+2).translate((0,0,-1)))
    for gx in(-36,36):shoulder=shoulder.cut(box(26,26,T+2).translate((gx,0,-1)))
    for hx,hy,hd in hole_grid(100,30):shoulder=shoulder.cut(cylinder(hd,T+2).translate((hx,hy,-1)))
    register("force-link-shoulder",shoulder,material="aluminum",kind="metal",qty=12,size=[110,38,T],holes=hole_grid(100,30),
             notes="Fixed shoulder retains spring pressure washer at neutral. Its26 mm square windows clear 25.4 mm shuttle bosses. Inner faces are at+/-4.175 mm from shuttle center, so metal capture is+/-1.0 mm.")
    PARTS['force-link-shoulder']['template_type']='plate'
    PARTS['force-link-shoulder']['cutouts']=[[-25,-14,50,28],[-49,-13,26,26],[23,-13,26,26]]
    boss=box(25.4,25.4,7.35).cut(cylinder(8.5,10).translate((0,0,-1))).cut(cylinder(12.1,2))
    for hx,hy,hd in hole_grid(16,16,3.4):boss=boss.cut(cylinder(hd,10).translate((hx,hy,-1)))
    register("force-shuttle-boss",boss,material="aluminum",kind="metal",qty=24,size=[25.4,25.4,7.35],holes=[[0,0,8.5]]+hole_grid(16,16,3.4),
             notes="Cut from 25.4 mm square bar. Counterbore inward face12.1 mm diameter2 mm deep to clear bronze bushing projection. Pair bolts through6.35 mm shuttle with four M3x30; finished boss contact separation21.05 mm.")
    register("force-pressure-washer",cylinder(32,1.5).cut(cylinder(8.5,4).translate((0,0,-1))),material="steel",kind="catalog",qty=24,
             notes="Steel M8 fender washer OD32 mm, bore8.5 mm,1.5 mm thick. Measured OD must seat beyond each26 mm square shoulder window; OD30 mm minimum. Washer face is retained at neutral and lifts only above measured preload.")
    plate("force-output-ear",60,40,[[-20,-10,5.5],[-20,10,5.5],[20,0,8.5]],qty=12,
          notes="Two per angular or linear link. Attach to shuttle with metal angles; hinge plane is clear of both guide bolts. Output joint carries force downstream of the overload springs.")
    plate("overload-switch-tab",60,25,[[-20,0,5.5],[20,0,5.5]],qty=6,
          notes="Metal moving flag on the shuttle. Opposed NC switches trip nominally at +/-0.30 mm angular or +/-0.75 mm XYZ before +/-1.0 mm metal capture. Transfer the switch holes and adjust by measured trip force.")
    plate("friction-spring-seat",38,60,[[0,0,12.5],[-15,0,3.4],[15,0,3.4]]+hole_grid(24,44,6.5),qty=3,
          notes="Four M6x80 posts and paired jam nuts set a soft spring's preload. Two M3x50 guide pins prevent the steel washer rotating. Spring ID >=12 mm, OD <=30 mm, free length 25 mm, measured k20-40 N/mm; adjust by measured torque, not thread count.")
    plate("angular-clevis-cheek", 80, 40, [[-20, 0, 16.0], [-20, -13,3.4],[-20,13,3.4], [20, -10, 5.5], [20, 10, 5.5]], qty=12,
          notes="F688ZZ bearing body16mm/flange18mm/width5mm. Two8mm hinge stubs per joint leave the screw's central passage open. Metal cheeks and bearing flanges carry pin load; twoM3 retainers keep the bearing seated.")
    plate("trunnion-inner-ear",40,40,[[0,0,8.5],[-12,12,5.5],[12,12,5.5]],qty=12,
          notes="Bolts to metal bulkhead/nut-face angles. M8 shoulder region forms thehingestub; lockingnut clamps this ear, independently of the bearing's outerrace.")
    plate("limit-stop", 40, 30, [[-10, 0, 6.5], [10, 0, 6.5]], qty=12,
          notes="Aluminum stationary stops backed by extrusion/metal angle. They bound motion only; full travel can enter a loaded vessel.")
    plate("bench-tether-anchor", 60, 30, [[-20,0,6.5],[20,0,6.5],[0,0,6.5]], qty=2)
    plate("brake-torque-lever", 220, 30, [[0,0,10.5],[-100,0,5.5],[100,0,5.5]] +
          [[8*math.cos(math.radians(a)),8*math.sin(math.radians(a)),3.4] for a in (0,90,180,270)], qty=1,
          notes="Balanced service tool: pivot at center, load holes at +/-100 mm. Four PCD16 M3 holes attach to TR8 flange for retainer grading. Use the separate angular-load-lever at the12 mm hub. Remove before powered motion.")
    plate('angular-load-lever',220,30,[[0,0,12.5],[-100,0,5.5],[100,0,5.5]]+hole_grid(26,20),notes='Balanced100 mm load lever for the separate angular drive-lever hub. Four M5x45 bolts are reused; output hub retains the real carried mass. No small-radius M3 flange holes in this12.5 mm shaft-bore variant.')
    plate('hub-proof-lever',300,30,[[0,0,12.5],[-140,0,5.5],[140,0,5.5]]+hole_grid(26,20),notes='Balanced temporary hub proof lever, measured140 mm arm. Four M5x45 attach only the ungripped specimen hub. Complete measured torque interval30-32.5 Nm in both signs, terminal end washers removed and independent noncontact catch installed. No gauge-force assumption from motor current.')
    plate('hub-proof-load-saddle',40,50,[[0,-15.875,5.5],[0,15.875,5.5]],notes='Horizontal metal gauge contact bridge across two borrowed25.4 mm angle legs. Force axis lies at the proof lever midplane, avoiding an additional axial overhang. Two M5x20 bridge ties and one M5x25 through the lever140 mm hole; transfer the two angles from the unpowered-force-test fork.')
    # Paired metal webs support each tangent-actuator fixed clevis on its
    # parent frame. Their drilled load paths are part of the fabrication kit.
    yaw_outline=[(-50,-35),(-50,35),(0,35),(180,-120),(180,-215),(120,-215)]
    yaw_outline=[(x-65,y+90) for x,y in yaw_outline]
    yw=cq.Workplane('XY').polyline(yaw_outline).close().extrude(T)
    yh=[[150-65,-180+90,18.5],[140-65,-140+90,5.5],[160-65,-140+90,5.5],[-25-65,-20+90,5.5],[-25-65,20+90,5.5]]
    for x,y,d in yh:yw=yw.cut(cylinder(d,T+2).translate((x,y,-1)))
    register('yaw-base-web',yw,material='aluminum',kind='metal',qty=2,size=[230,250,T],holes=yh,notes="Paired stationary webs at Z162.3/235 mm. Two metal angles per web attach to the yaw-bearing back. Bearing aperture18.5 mm clears the outer clevis bearing; two M5 bolts attach each base cheek.")
    PARTS['yaw-base-web'].update(template_type='plate',outline=yaw_outline)
    pitchA=rotation('y',60)@np.array([150,0,180]);d=rotation('y',60)@np.array([0,0,-1]);lateral=np.cross(np.array([0,1,0]),d)
    ph=hole_grid(40,40,center=(-110,0))+[[pitchA[0]-110,-pitchA[2]-40,18.5]]
    for k in(-1,1):
        v=pitchA+40*d+k*10*lateral;ph.append([v[0]-110,-v[2]-40,5.5])
    plate('pitch-base-web',280,100,ph,qty=2,notes="Parallel XZ webs outside the fixed pitch clevis. Four M5x90 ties clamp both webs to the negative-Y yaw side through31.35/28.65 mm metal spacers. Two M5x20 bolts attach each base cheek.")
    ro=[[-40,-210],[180,-210],[180,-6.9],[60.5,-6.9],[60.5,-38.65],[-40,-38.65]]
    ro=[[y-70,z+108.45] for y,z in ro]
    rh=[[80,-71.55,18.5],[70,-31.55,5.5],[90,-31.55,5.5],[0,88.85,5.5],[20,88.85,5.5]]
    rw=cq.Workplane('XY').polyline(ro).close().extrude(T)
    for x,y,d in rh:rw=rw.cut(cylinder(d,T+2).translate((x,y,-1)))
    register('roll-base-web',rw,material='aluminum',kind='metal',qty=2,size=[220,203.1,T],holes=rh,notes='Paired YZ webs atX-206.70/-134 mm. UpperearsatY60.5..180 clearrollbearingfoot. Shortanchorslots letwebs passthrough sharedplate; twoangles perweb mountonanchortop. Aperture clearsclevisbearing.')
    PARTS['roll-base-web'].update(template_type='plate',outline=ro)
    plate('roll-base-anchor',160,190,[[x+185,y,5.5] for x in(-235,-135) for y in(-50,50)],notes='Sharedroll-driveanchor onpitchcrossbars; fourM5x35 bolts passthroughcrossbar,anchor,6.95 mmspacersandbearingfoot. Shortslotsclearthesupportwebeartabs; four metalangles joinwebs atopplate.')
    for bx in(-22.0,50.7):PARTS['roll-base-anchor']['model']=PARTS['roll-base-anchor']['model'].cut(box(6.95,34.5,T+2).translate((bx+6.95/2,60.5+34.5/2,-1)))
    PARTS['roll-base-anchor']['cutouts']=[[-22.0,60.5,6.95,34.5],[50.7,60.5,6.95,34.5]]
    plate('angular-output-bridge',100,60,[[-20,0,8.5]]+hole_grid(18,18,center=(-20,0))+[[20,-10,5.5],[20,10,5.5]],qty=3,notes="Bolts under angular lever at the150 mm output datum with four M5x25. Two M5x80 cross ties carry outer clevis cheeks through four23.65 mm metal spacers, keeping the screw passage open.")
    for n,l,q in(('pitch-web-left-spacer',31.35,4),('pitch-web-right-spacer',28.65,4),('angular-output-spacer',23.65,12)):
        register(n,cylinder(8,l).cut(cylinder(6,l+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=q,size=[8,8,l],notes='Metal tube spacer8 OD/6 ID; finished length is a load-path dimension. No printed substitute.')
        PARTS[n]['template_type']='tube'
    for n,l,q in(('crash-force-outer-spacer',25-12.5/4.68+1.5,16),('crash-force-center-spacer',8.35,8)):
        register(n,cylinder(8,l).cut(cylinder(6,l+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=q,size=[8,8,l],notes='8 OD/6 ID metal crash-cage tie spacer. Outer length is nominal for12.5 N per spring and must be finished from actual directional spring grading; center8.35 mm sets independent+/-1 mm capture.')
        PARTS[n]['template_type']='tube'
    # Captured axial crash pods and a transverse magnetic release cradle.
    plate("crash-pod-end",40,80,[[0,20,8.1],[0,-10,8.1]]+hole_grid(32,32,3.4,center=(0,20))+[[-12,-31,5.5],[12,-31,5.5]],qty=4,
          notes="Two integrated end/guide-support plates per 8 mm guide pod. Two ground guides separated 30 mm. Upper guide datum is local Y=20 mm; Four M3x100 tie bolts andmetalspacers retainfixedshoulders. Four4.68 N/mm springs totalinbothpods; preload setwithrealgun/cable.")
    cshoulder=box(40,40,T).cut(box(26,26,T+2).translate((0,0,-1)))
    for hx,hy,hd in hole_grid(32,32,3.4):cshoulder=cshoulder.cut(cylinder(hd,T+2).translate((hx,hy,-1)))
    register("crash-pod-shoulder",cshoulder,material="aluminum",kind="metal",qty=4,size=[40,40,T],holes=hole_grid(32,32,3.4),notes="26 mm shoulderwindow,40 mm fixedplate. Neutralshuttlecapture+/-1.0 mm; flatcam dwellafter0.25 mm axialtrip.")
    PARTS['crash-pod-shoulder'].update(template_type='plate',cutouts=[[-13,-13,26,26]])
    cshuttle=box(40,40,T)
    choles=[[0,0,12.1]]+hole_grid(16,16,3.4)+hole_grid(32,32,6)
    for hx,hy,hd in choles:cshuttle=cshuttle.cut(cylinder(hd,T+2).translate((hx,hy,-1)))
    register("crash-pod-shuttle",cshuttle,material="aluminum",kind="metal",qty=2,size=[40,40,T],holes=choles,
             notes="Bolted25.4 mm boss halves liftseatedpressurewashers. Smooth8 mm guiderod runsinbronze bushing. Twooutputcarrier holes transferonitsouteredge; no printedaxialloadpath.")
    PARTS['crash-pod-shuttle']['template_type']='plate'
    PARTS['force-shuttle-boss']['quantity']=28
    # Rails taper insidepitchframe attherear, outsidethefixedsideplates forward.
    for hand in('left','right'):
        outline=[(-95,38),(-95,63),(55,92.7),(105,92.7),(105,67.5),(65,67.5)]
        if hand=='left':outline=[(x,-y) for x,y in outline]
        cy=-65.35 if hand=="left" else 65.35
        outline=[(x,y-cy) for x,y in outline]
        rail=cq.Workplane('XY').polyline(outline).close().extrude(T)
        register(f"crash-carrier-{hand}",rail,material='aluminum',kind='metal',size=[200,60,T],
                 notes="Taperedmetal carrierabovefixedcradle atZ32.7 mm. Rearinsidepitchsideplates; forwardoutboardofgunclamp. TransferM3/M5 outputpodandrearmagneticplateangleholes.")
        PARTS[f'crash-carrier-{hand}'].update(template_type='plate',outline=outline)
    plate("crash-magnet-back",120,90,hole_grid(100,60)+[[y,z,5.5] for y,z in((-30,15),(30,15),(0,-25))],
          notes="Fixedtothreeballseats. Three countersunk steel cup magnets 25 OD x 7.7 high, M5 mounts; metalfasteners andshimmedairgapsadjustrelease. Catalogpullisnotthereleaseforce.")
    tray=box(170.459,80,T).translate((14.7705,0,0)).cut(box(55,36,T+2).translate((-36,0,-1)))
    tholes=[[x,y,5.5] for x in(25,65) for y in(-32,32)]+[[x,y,5.5] for x in(-57.759,85) for y in((-25,25) if x<0 else(-30,30))]
    for hx,hy,hd in tholes:tray=tray.cut(cylinder(hd,T+2).translate((hx,hy,-1)))
    register("gun-release-tray",tray,material='aluminum',kind='metal',size=[200,80,T],holes=tholes,
             notes="Releasedguncradle base,handleopening55x36 mmcenterX-36. LowerjawboltsatX25/65,Y+/-32; throughM5x20. Ball/magnetback andtwo shortsteelcatchtethersretainreleasedgun.")
    PARTS['gun-release-tray'].update(template_type='plate',outline=[[-70.459,-40],[100,-40],[100,40],[-70.459,40]],cutouts=[[-63.5,-18,55,36]])
    plate("gun-release-back",120,70,[[-35,26.35,5.5],[35,26.35,5.5]]+[[y,z,8.1] for y,z in((-40,-20),(40,-20),(0,25))]+[[y+dy,z,3.4] for y,z in((-40,-20),(40,-20),(0,25)) for dy in(-9,9)],
          notes="Three 8 mm hardened steel balls contacting six hardened 4 x 20 mm dowels in three registered V seats; retainingcompoundonlylocatesballs,magnetforceandmetalcontactscarryworkingload. Qualifyactualrelease20-30 Naddednozzleforceinaxial/transversedirections withrealgun,cableandgravitybaseline.")
    plate("crash-output-wall",100,70,[[x,z,3.4] for x in(-12.5,27.5) for z in(-29.35,-13.35)],qty=2,notes="Metal wall from lower guide blocks to upper axial shuttle and carrier. Block M3 holes transfer through side faces at Z+/-8 from rod, clear of the12.1 mm guide bore; M3x40 crosses25.4 mm block and6.35 mm wall.")
    plate("crash-ground-crossbar",200,40,hole_grid(160,20),qty=2,notes="Fixed metal crossbars under the cradle support integrated pod end plates; eight metal angles connect to the fixed cradle and the four end plates. Transfer holes after alignment.")
    plate("vee-seat-keeper",24,8,[[-9,0,3.4],[9,0,3.4]],qty=6,notes="One metal clamp across each paired-dowel end. Four millimetre metal stand-off pack from fixed seat plate puts keeper back face against dowel crest. Two M3x25 ties per keeper; retaining compound only locates dowels.")
    plate("nozzle-test-fork-arm",210,30,[[-45,0,5.5],[92.3,-8.3,5.5]],qty=2,notes="Temporary dry-test load fork: rigid arms outside gun at Y+/-80. Two spare jaw bars and TPU pads clamp a safe body surface, four metal angle joints. Rear angle hole is X55 at Z55.65; bridge mountsatX192.3,Z47.35 andstandsatX205. Retract wire before installing.")
    plate("nozzle-test-bridge",180,30,[[-60.95,0,5.5],[60.95,0,5.5],[0,0,6.5]],notes="Vertical bridge at X205, Z47.35. Center M6x40 grade8.8 crossdrilled3.5 mm cord studhasheadatX195 andholeatX200, lockedbytwoM6 nutsagainstbothbridgefaces. Itprojects5 mm backward to the calibrated X200 virtual endpoint after consumable wire is removed. No load on nozzle, wire guide or optics. Measure actual eye position and include alignment uncertainty.")
    register("roll-foot-metal-spacer",cylinder(8,6.95).cut(cylinder(6,10).translate((0,0,-1))),material="aluminum",kind="metal",qty=4,size=[8,8,6.95],notes="Four metal 6.95 mm spacers bridge anchor top Z-32.30 to roll bearing-foot underside Z-25.35.")
    PARTS['roll-foot-metal-spacer']['template_type']='tube'
    register("crash-striker",cylinder(25,2).cut(cylinder(6,4).translate((0,0,-1))),material="steel",kind="catalog",qty=3,notes="Three unmodified cup striker washers, carbon steel zinc M6 bore x25 OD x2 mm.")
    ballwash=cylinder(25,2).cut(cylinder(6,4).translate((0,0,-1)))
    for x in(-9,9):ballwash=ballwash.cut(cylinder(3.4,4).translate((x,0,-1)))
    register('crash-ball-backing-washer',ballwash,material='steel',kind='catalog',qty=3,notes='Three purchased25 OD /6 ID /2 mm carbon-steel washers. Drill two3.4 mm keeper holes at X+/-9,Y0. The6 mm aperture supports the hardened8 mm ball; the aluminum plate8.1 mm opening clears its nose. Use the registered purchased-washer drilling template.')
    PARTS['crash-ball-backing-washer']['drilling_faces']={'XY':[[-9,0,3.4],[9,0,3.4],[0,0,6]]}
    register("608zz-bearing",cylinder(22,7).cut(cylinder(8,9).translate((0,0,-1))),material='steel',kind='catalog',qty=3,
             notes="Twofiber swivels plusonetorque-cordredirectbearing. MetalM8 axle clampsonlyinnerrace.")
    swivel=box(40,40,10).cut(cylinder(10.5,12).translate((0,0,-1)))
    for hx,hy,hd in hole_grid(28,28,6.5):swivel=swivel.cut(cylinder(hd,12).translate((hx,hy,-1)))
    register("fiber-swivel-base",swivel,material='PET-GF',kind='print',qty=2,notes="Fixed base mounted on four 10 mm metal spacers with M6x30 slot8 fasteners. A separate M8 axle clamps only metal tubes and the 608 inner race; its head remains above the beam. Rotating saddle carries the outer race.")
    cap=cylinder(36,2).cut(cylinder(14.5,4).translate((0,0,-1)))
    for hx in(-15,15):cap=cap.cut(cylinder(3.4,4).translate((hx,0,-1)))
    register('fiber-bearing-cap',cap,material='PET-GF',kind='print',qty=3,notes='Two M3x20 through-bolts retain the 608 outer race in the rotating saddle. Center14.5 mm aperture clears fixed inner race; no screw clamping load on the inner race.')
    for name,length,bore,od,qty in(('fiber-base-metal-spacer',10,8,10,8),('fiber-axle-lower-tube',13,8.5,10,2),('fiber-axle-upper-tube',4,8.5,10,2)):
        register(name,cylinder(od,length).cut(cylinder(bore,length+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=qty,size=[od,od,length],notes='Metal tube in swivel clamp stack; fixed axle inner-race tubes never contact rotating saddle or bearing outer race. Grade free rotation with actual cable, cold and warm.')
        PARTS[name]['template_type']='tube'
    wheel=cylinder(40,10).union(cylinder(46,1)).union(cylinder(46,1).translate((0,0,9))).cut(cylinder(22.2,7.3)).cut(cylinder(10.5,12).translate((0,0,-1)))
    for hx in(-15,15):wheel=wheel.cut(cylinder(3.4,12).translate((hx,0,-1)))
    for name,length in(('redirect-lower-contact-tube',3),('redirect-upper-contact-tube',7.15)):
        register(name,cylinder(10,length).cut(cylinder(8.5,length+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=1,size=[10,10,length],notes='Metal inner-race contact tube,10 OD/8.5 ID. Redirect axle clamps bracket and inner race only; wheel and outer-race cap rotate freely.')
        PARTS[name]['template_type']='tube'
    register("torque-cord-pulley",wheel,material='PET-GF',kind='print',qty=1,notes="608 bearinginside40 mm cordwheel. Onlyunloadedservicetest; guardhangingcontainers. Characterize<=5 g imbalanceusingequal200 g cups beforeinstalledZtest.")
    register("crash-spring",cylinder(12,22).cut(cylinder(8.8,24).translate((0,0,-1))),material='steel',kind='catalog',qty=4,
             notes="B08FDWP3K6 nominal4.68 N/mm/free25 mm/OD12 mm. Directionalpreload includesgravity/cablebaseline; measuredaddednozzletrip20-30 N. Measure free and solid lengths; maximumcompression includingcapture mustremain1 mmshortofmeasuredcoilbind. Listingforce/travel conflict requiresgrading.")
    register("crash-magnet",cylinder(25,7.7).cut(cylinder(5.6,10).translate((0,0,-1))),material='steel',kind='catalog',qty=3,notes="B08LYPDYY5 steelcupmagnet25 OD/7.7 mm high,5.6 mm throughhole/10.6 mm topcountersink. M5x25 countersunkmachinebolt throughmetalplate; verifyheadflushness,actualcupbottomandshimmedpull. Contactratingisnotreleaseforce.")
    register("crash-ground-guide",cylinder(8,100),material='steel',kind='catalog',qty=4,notes="PurchasedB01NCOMFLT8x100 mmHRC60groundrod,uncut.Two perpod,30 mmverticalseparation; collarslocateonly.")
    register("crash-guide-collar",cylinder(25,8).cut(cylinder(8,10).translate((0,0,-1))),material='aluminum',kind='catalog',qty=8,notes="B0C166J3G4 splitclamp8bore/25OD/8high. Locatesrodonly; springsreactthroughfixedmetalshouldersandties.")
    block=box(25.4,25.4,15).cut(cylinder(12.1,17).translate((0,0,-1)))
    for z in(-8,8):block=block.cut(cylinder(3.4,28).rotate((0,0,0),(0,1,0),90).translate((-14,z,7.5)))
    register("crash-guide-block",block,material='aluminum',kind='metal',qty=4,size=[25.4,25.4,15],holes=[[0,0,12.1]],notes="Bronze8x12x10 mmguidebushinginside25.4 mm squaremetalblock. Two perlowerguide,40 mmcenterseparationparalleltonozzle. MounttometaloutputcarrierthroughM3/M5metalangles.")
    PARTS['crash-guide-block']['template_type']='bar'
    register("crash-vee-dowel",cylinder(4,20),material='steel',kind='catalog',qty=6,notes="B0F54FSG1Q hardened4x20 mmsteelpin.Pairsat6 mmcenterpitchformthreeVseats; noaluminumballcontact.")
    register("crash-ball",cq.Workplane('XY').sphere(4),material='steel',kind='catalog',qty=3,notes="Hardened8 mm steelball; Three V seats made frompaired4x20 mm dowels. AsteelM6-bore backingwasher supports eachball; compoundlocatesit duringdetachedhandling. Workingloadpassessteelball tosteeldowels.")
    # Seven square hubs: output yaw, paired pitch, roll, and three drive levers.
    hub = box(38.1, 38.1, 25).cut(cylinder(12.0, 27).translate((0,0,-1)))
    for x,y,d in hole_grid(26,20):
        hub = hub.cut(cylinder(d,27).translate((x,y,-1)))
    hub=hub.cut(box(1.5,16,27).translate((0,12,-1)))
    for hz in (6,19):
        hub=hub.cut(cylinder(4.2,40).rotate((0,0,0),(0,1,0),90).translate((-20,16,hz)))
    register("shaft-hub", hub, material="aluminum", kind="metal", qty=7,
             size=[38.1,38.1,25], holes=hole_grid(26,20)+[[0,0,12.0]],
             notes="12 mm 304 shaft with centered M5 end threads and no transverse hole. Ream the hub bore to 12 mm; saw the 1.5 mm slit from bore to +Y. Two 4.2 mm clamp bores run along X at Y16, Z6/19. Two grade 12.9 M4x50 bolts, four washers and two locking nuts clamp the split hub. Torque transmission requires measured proof in both signs: pitch drive and negative pitch output 30-32.5 Nm; other hubs 25.2-27.5 Nm, full uncertainty interval, no slip or permanent set. Independent metal end capture retains the shaft and hubs; bearing setscrews alone are not positive capture.")
    PARTS['shaft-hub']['template_type']='hub'
    PARTS['shaft-hub']['drilling_faces']={'YZ_clamp_bores':{'face_X_mm':-19.05,'holes_mm':[[16,6,4.2],[16,19,4.2]]},'XY_mounting':{'holes_mm':hole_grid(26,20)+[[0,0,12.0]]},'slit_mm':{'width':1.5,'X':0,'from_Y':4,'to_Y':20}}
    PARTS['force-shuttle-boss']['template_type']='bar'
    # Frame and catalog references; these are not manufacture drawings of bought parts.
    extrusion = box(40,40,1).cut(box(28,28,3).translate((0,0,-1)))
    register("4040-extrusion", extrusion, material="aluminum", kind="catalog", notes="Envelope only. Cut lengths are in the assembly receipt.")
    rail = box(RAIL_LENGTH,26,RAIL_CENTER_H-6).union(cylinder(12,RAIL_LENGTH).rotate((0,0,0),(0,1,0),90).translate((-200,0,RAIL_CENTER_H)))
    register("sbr12-rail", rail, material="steel", kind="catalog", qty=6,
             notes="CHUANGNENG SBR12-400; 400mm supported rail, transfer-drilled support holes.")
    block = box(BLOCK_X,BLOCK_Y,BLOCK_H).cut(cylinder(12.2,BLOCK_X+2).rotate((0,0,0),(0,1,0),90).translate((-BLOCK_X/2-1,0,BLOCK_H-BLOCK_TOP_FROM_CENTER)))
    for hx,hy,hd in hole_grid(26,28,4.2):
        block = block.cut(cylinder(hd,12).translate((hx,hy,BLOCK_H-10)))
    register("sbr12uu-block", block, material="aluminum", kind="catalog", qty=12,
             notes="Envelope W41/L39/F28. Four tapped M5 holes: 28mm across and26mm along. Axis-to-top17.5mm.")
    kp = box(KP12_L,KP12_W,6).union(cylinder(38,KP12_L).rotate((0,0,0),(0,1,0),90).translate((-KP12_L/2,0,KP12_H)))
    kp = kp.cut(cylinder(SHAFT_D,KP12_L+2).rotate((0,0,0),(0,1,0),90).translate((-KP12_L/2-1,0,KP12_H)))
    register("kp12-bearing", kp, material="aluminum", kind="catalog", qty=6,
             notes="XIKE KP001 catalog envelope: shaft 12 mm, foot-hole pitch 56 mm, center height 19 mm, body length 71 mm. Final source identity is in sourcing.")
    register('gimbal-shaft-stock',cylinder(12,356),material='steel',kind='catalog',qty=2,notes='304 stainless12 mm shaft stock. Finished cuts175,165,130,85 mm. Centered M5x0.8 blind end taps at both ends, usable thread10 mm,4.2 mm pilot16 mm. No transverse hole. Bored terminal hub regions require combined proof/no-set checks; no accepted capacity follows from the nominal material assumption.')
    register('tr8-screw-stock',cylinder(8,400),material='steel',kind='catalog',qty=8,notes='Purchased TR8x2 steel screws. Catalog thread envelope; thrust and single-nut fit require physical qualification.')
    register('shaft-end-retainer-washer',cylinder(20,2).cut(cylinder(6,4).translate((0,0,-1))),material='steel',kind='catalog',qty=8,notes='Uxcell B0DYK1PVYB 304 steel washer, 20 OD / 6 ID / 2 mm. Eight used from one 60-pack. The 20 mm envelope clears the four M5 hub mounting heads and washers. M5x12 plus one 0.8 mm flat washer gives 9.2 mm reach into a measured 10 mm usable M5 end thread. No trimmed-washer substitution.')
    register('shaft-end-flat-washer',cylinder(10,.8).cut(cylinder(5.5,3).translate((0,0,-1))),material='steel',kind='catalog',qty=8,notes='M5 flat washer, selected0.8 mm thickness. Actual end-bolt reach and bottom margin are measured.')
    for length,qty in Counter(l for stacks in CAPTURE_STACKS.values() for _,l in stacks).items():
        name=capture_tube_name(length)
        register(name,cylinder(20,length).cut(cylinder(12.5,length+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=qty,size=[20,20,length],notes='Metal axial-capture tube from20 OD /12 ID stock, bored12.5 mm. Face only the delivered bearing inner race or metal hub/plate, never outer race/seal. Finish actual stack for0.5 mm maximum one-side free motion; chamfer/relieve OD to the measured inner-race face. No rubbing during free rotation, cold or warm.')
        PARTS[name]['template_type']='tube'
    kp8 = box(13,55,5).union(cylinder(24,13).rotate((0,0,0),(0,1,0),90).translate((-6.5,0,15)))
    kp8 = kp8.cut(cylinder(8.2,15).rotate((0,0,0),(0,1,0),90).translate((-7.5,0,15)))
    register("kp08-bearing", kp8, material="aluminum", kind="catalog", qty=9,
             notes="Radial guide on screw crest, not an axial retainer; fixed end plus floating end for XYZ, one for each angular screw.")
    nut = cylinder(NUT_BODY_D,NUT_LENGTH).union(cylinder(22,NUT_FLANGE_H).translate((0,0,1.5))).cut(cylinder(8,NUT_LENGTH+2).translate((0,0,-1)))
    for a in (0,90,180,270):
        nut = nut.cut(cylinder(3.4,5).translate((8*math.cos(math.radians(a)),8*math.sin(math.radians(a)),-1)))
    register("tr8x2-nut", nut, material="brass", kind="catalog", qty=18,
             notes="TR8x2 single-start lead2mm. Flange hole pattern and axial length are configurable catalog interfaces.")
    register("f8-16m-thrust", cylinder(16,5).cut(cylinder(8.2,7).translate((0,0,-1))),
             material="steel", kind="catalog", qty=12, notes="Three-piece thrust bearing,8x16x5mm. Each race has its own metal seat; no printed preload path.")
    register("thrust-body-clearance-spacer",cylinder(20,10).cut(cylinder(10.5,12).translate((0,0,-1))),material="steel",kind="catalog",qty=12,
             size=None,notes="Five steel M10 flat washers per spacer stack, ID10.5/OD20/thickness2 mm, total60washers. Stack clears the10.2 mm brassbody and carries flange load to the thrustshaftwasher. Measure stacklength; adjust nutpositions before threadlocker cure.")
    register("friction-washer",cylinder(37,3).cut(cylinder(13,5).translate((0,0,-1))).cut(cylinder(3.4,4).translate((-15,0,-1))).cut(cylinder(3.4,4).translate((15,0,-1))),material="steel",kind="catalog",qty=3,
             notes="Steel M12 large washer, OD36-37 mm, ID13 mm, thickness3 mm. Drill two 3.4 mm anti-rotation holes 30 mm apart. Its dry face contacts only the rotating brass flange annulus OD22/ID13. Do not lubricate this interface.")
    register("friction-spring",cylinder(30,22.5).cut(cylinder(12.5,24.5).translate((0,0,-1))),material="steel",kind="catalog",qty=3,
             notes="Reference envelope for purchased soft axial spring, free length25 mm, ID>=12 mm, OD<=30 mm. Measured k20-40 N/mm. Actual preload and runout must satisfy per-axis breakaway window.")
    register("force-spring",cylinder(16,18.837).cut(cylinder(8.5,21).translate((0,0,-1))),material="steel",kind="catalog",qty=24,
             notes="Uxcell blue compression spring16 OD/8.5 ID/20 mm free; nominal43 N/mm from343 N at8 mm. All24 use the same source. Seated preload 100 N yaw/roll, 130 N pitch, 250 N X/Y and upward Z, 400 N downward Z. Grade both directional pairs and complete links by measured trip and peak force.")
    register("force-bushing",cylinder(12,10).cut(cylinder(8,12).translate((0,0,-1))),material="brass",kind="catalog",qty=12,
             notes="Bronze guide bushing8 ID/12 OD/10 mm length. Smooth M8 guide-bolt shanks run in these; retain bushing in the metal shuttle.")
    spacer_lengths={"nut-outer-angular":9.5122093023,"nut-outer-pitch":9.1633720930,"nut-outer-XYZ":7.7680232558,"nut-outer-Z-down":6.0238372093,"force-outer-angular":20.3372093023,"force-outer-pitch":19.9883720930,"force-outer-XYZ":18.5930232558,"force-outer-Z-down":16.8488372093,"force-center":8.35}
    for name,length in spacer_lengths.items():
        register(name+"-metal-spacer",cylinder(8,length).cut(cylinder(6,length+2).translate((0,0,-1))),material='aluminum',kind='metal',qty=(4 if name.endswith("Z-down") else 20 if name.endswith("XYZ") else 8 if name.endswith("pitch") else 16 if name.endswith("angular") else 24),size=[8,8,length],
                 notes="Metal 8 OD / 6 ID tube spacer. Set spring preload by measured rates and matched metal shims; the fixed 8.35 mm center spacer sets +/-1.0 mm capture independently of preload.")
        PARTS[name+'-metal-spacer']['template_type']='tube'
    register('guard-metal-spacer',cylinder(8,7).cut(cylinder(6,9).translate((0,0,-1))),material='aluminum',kind='metal',qty=12,size=[8,8,7],notes='Metal7 mm shield stand-off. ID6/OD8; use metal washers covering the 6 mm bore, M3x25 through2 mm shield and6.35 mm bulkhead. No clamp load through air.')
    register('V-keeper-metal-spacer',cylinder(8,4).cut(cylinder(6,6).translate((0,0,-1))),material='aluminum',kind='metal',qty=12,size=[8,8,4],notes='Metal4 mm stand-off under hardened-dowel end keeper; finishagainstactual4 mm dowel crest. Not a printedload spacer.')
    for n in('guard-metal-spacer','V-keeper-metal-spacer'):PARTS[n]['template_type']='tube'
    register('hinge-contact-tube',cylinder(10,1).cut(cylinder(8.5,3).translate((0,0,-1))),material='aluminum',kind='metal',qty=12,size=[10,10,1],notes='Inner-race contact ring,10 OD/8.5 ID/1 mm length; clears outerraceandseal. Drill10x8 stocktube to8.5 ID before cutting. No M8 washerdirectlycontactsbearingouterrace.')
    register('hinge-thread-start-spacer',cylinder(10,9.65).cut(cylinder(8.5,12).translate((0,0,-1))),material='aluminum',kind='metal',qty=12,size=[10,10,9.65],notes='Nominal 9.65 mm for the sourced 22 mm smooth shank minus 6.35 mm ear, 5 mm bearing and 1 mm contact ring. Finish to the actual thread start; nut clamps the metal stack without bottoming.')
    for n in('hinge-contact-tube','hinge-thread-start-spacer'):PARTS[n]['template_type']='tube'
    register("gt2-20t-pinion",cylinder(16,15).cut(cylinder(5,17).translate((0,0,-1))),material="aluminum",kind="catalog",qty=6,
             notes="Purchased20-tooth,2mm GT2,6mm land,5mm shaft bore.")
    register("gt2-belt",box(55,6,1.4),material="TPU",kind="catalog",qty=6,
             notes="Reference span only. Purchased closed-loop2mm GT2,6mm wide,220mm circumference. Motor centers approximately58mm, slots allow tension setting.")
    register("f688zz-bearing",cylinder(16,5).union(cylinder(18,1)).cut(cylinder(8,7).translate((0,0,-1))),material="steel",kind="catalog",qty=12,
             notes="Flanged8x16x5mm bearing, flange18mm. Inner race turns with metalhingestub; outer shell seats in metalcheek.")
    register("nut-metal-spacer",cylinder(8,30).cut(cylinder(6,32).translate((0,0,-1))),material="aluminum",kind="metal",qty=24,size=[8,8,30],
             notes="Metal spacer 30 mm long, 8 mm OD, 6 mm ID. Four per single-nut metal-face assembly. No axial preload through plastic.")
    PARTS["nut-metal-spacer"]["template_type"]="tube"
    angle=box(25.4,25.4,3.175).union(box(25.4,3.175,25.4).translate((0,-11.1125,0)))
    angle=angle.cut(cylinder(5.5,6).translate((0,0,-1))).cut(cylinder(5.5,6).rotate((0,0,0),(1,0,0),90).translate((0,-10,12.7)))
    register("metal-angle-25",angle,material="aluminum",kind="metal",qty=137,
             size=[25.4,25.4,3.175],notes="Cut 25.4 mm slices from 25.4 x 25.4 x 3.175 mm angle. Both legs drilled 5.5 mm; metal through-bolts connect plates. Not a printable bracket.")
    for suffix,hx in(('minus',7),('plus',-7)):
        name='guard-thrust-angle-'+suffix
        gm=angle.cut(cylinder(6.5,6).translate((0,0,-1))).cut(cylinder(3.4,6).translate((hx,9,-1)))
        register(name,gm,material='aluminum',kind='metal',qty=6,size=[25.4,25.4,3.175],holes=[[0,0,6.5],[hx,9,3.4]],notes='One right-side upper thrust angle per drive. Transfer the registered 3.4 mm guard passage from the bulkhead after fitting the shared 6.5 mm M6 post hole. The M3 washer is 7 mm OD and remains within the foot. This is a cut from the same small-angle stock; total137 plain plus6 of each variant remains149 slices.')
        PARTS[name]['template_type']='angle'
        PARTS[name]['drilling_faces']={'foot_XY':[[0,0,6.5],[hx,9,3.4]],'upright_XZ':[[0,12.7,5.5]]}
    stop_angle=box(50.8,40,T).translate((-25.4,0,0)).union(box(T,40,50.8).translate((-T/2,0,0)))
    stop_drilled=stop_angle
    for yy in(-10,10):stop_drilled=stop_drilled.cut(cylinder(6.5,T+2).translate((-40.7,yy,-1)))
    for zz in(25,45):stop_drilled=stop_drilled.cut(cylinder(6.5,T+2).rotate((0,0,0),(0,1,0),90).translate((-T-1,0,zz)))
    register("linear-stop-angle",stop_drilled,material="aluminum",kind="metal",qty=6,
             size=[50.8,40,T],notes="Cut40 mm slices from50.8 x50.8 x6.35 mm angle. Verticallegheight50.8 mm; stationary contact face is6.35mmplate. Foot holes areM6 atlocalX-40.7,Y+/-10; uprightM6 holesatY0,Z25/45. Foot centers arebedX+/-171,Y+/-10, clearingX-bed frameby3 mm. Backing upright sitsbehindcontactplate at+/-205.35 mm. No printed stop reaction path.")
    jack=stop_angle.cut(cylinder(6.5,9).translate((-13,0,-1)))
    for z in(15,35):jack=jack.cut(cylinder(6.5,9).rotate((0,0,0),(0,1,0),90).translate((-7.35,0,z)))
    register('installed-Z-jack-angle',jack,material='aluminum',kind='metal',qty=1,size=[50.8,40,T],notes='Seventh40 mm slice of50.8x50.8x6.35 angle. Two M6x16 slot8 mounts in vertical leg atZ15/35. Foot M6 clearance is13 mm behind the vertical face. A fully threaded M6x80 screw bears on gauge-back lower edge; hold lower working nut with10 mm wrench while feeding, then lock upper nut against angle. Advance at most1/12 turn,0.0833 mm per increment.')
    PARTS['installed-Z-jack-angle']['template_type']='angle'
    cap=box(70,50.8,T).translate((0,-25.4,0)).union(box(70,T,50.8).translate((0,-T/2,-50.8)))
    for x in(-28,28):cap=cap.cut(cylinder(5.5,T+2).rotate((0,0,0),(1,0,0),90).translate((x,1,-26.8)))
    register('proof-gauge-quill-cap',cap,material='aluminum',kind='metal',qty=1,size=[50.8,70,T],notes='One 70 mm wide slice of 50.8 x 50.8 x 6.35 mm angle. The quill presses only the horizontal metal leg, centered on the gauge axis. Two M5x25 mount the vertical leg to the gauge backplate at X +/-28, backplate Y48.2. The nearest M4/M5 washer centers are 13.897 mm apart, exceeding their 11 mm summed radii. Four 7 mm rear spacers clear screw heads from the case; finish actual M4 engagement. Drill motor unplugged throughout proof.')
    PARTS['proof-gauge-quill-cap']['template_type']='angle'
    PARTS['proof-gauge-quill-cap']['drilling_faces']={'upright_XZ':[[-28,-26.8,5.5],[28,-26.8,5.5]]}
    PARTS["metal-angle-25"]["template_type"]="angle"
    PARTS["linear-stop-angle"]["template_type"]="angle"
    PARTS["linear-stop-angle"]["drilling_faces"]={"foot_XY":[[-40.7,-10,6.5],[-40.7,10,6.5]],"upright_YZ":[[0,25,6.5],[0,45,6.5]]}
    register("nema17-motor", box(42,42,48).union(cylinder(22,2).translate((0,0,48))).union(cylinder(5,24).translate((0,0,50))),
             material="motor", kind="catalog", qty=6, notes="STEPPERONLINE17HS19-2004S1; 48mm body,31mm M3 square,5mm shaft.")
    register("steel-fastener",cylinder(5,20),material="steel",kind="catalog",notes="Reference fastener envelope; exact grade/length/washer stack in fasteners.json.")
    # Printable pulley: negative-space profile is a clearance fit, tested with the supplied sector.
    pitch_r = 80*2/(2*math.pi)
    root_r = pitch_r-0.254-0.76
    tip_r = pitch_r-0.254
    pts=[]
    for tooth in range(80):
        a=2*math.pi*tooth/80
        for da,r in ((-.031,tip_r),(-.019,tip_r),(-.013,root_r),(.013,root_r),(.019,tip_r),(.031,tip_r)):
            pts.append((r*math.cos(a+da),r*math.sin(a+da)))
    pulley = cq.Workplane("XY").polyline(pts).close().extrude(7)
    pulley = pulley.union(cylinder(tip_r*2+4,1.2).translate((0,0,-1.2))).union(cylinder(tip_r*2+4,1.2).translate((0,0,7)))
    pulley = pulley.cut(cylinder(10.5,12).translate((0,0,-2)))
    for a in (0,90,180,270):
        pulley=pulley.cut(cylinder(3.4,12).translate((8*math.cos(math.radians(a)),8*math.sin(math.radians(a)),-2)))
    register("pulley-80t", pulley, material="PET-GF", kind="print", qty=6,
             notes="GT2/2mm pitch/6mm belt,80 teeth. Four M3x20 bolt to the rotating TR8 metal flange. Nut is the hub; plastic never clamps the shaft.")
    coupon = pulley.intersect(box(60,20,12).translate((0,24,-2)))
    register("pulley-sector-coupon", coupon, material="PET-GF", kind="print", qty=1,
             notes="Print first, mesh with the purchased6mm GT2 belt. Groove tolerance is a fitting allowance, not certified belt geometry.")
    bracket = box(100,80,8)
    bracket = bracket.cut(cylinder(24,10).translate((25,0,-1)))
    for hx,hy,hd in hole_grid(31,31,3.4,center=(25,0)):
        bracket=bracket.cut(cylinder(hd,10).translate((hx,hy,-1)))
    for sx,sy in ((-35,-35),(-35,35)):
        bracket=bracket.cut(cq.Workplane("XY").center(sx,sy).slot2D(14,5.5,0).extrude(10).translate((0,0,-1)))
    register("motor-tension-plate", bracket, material="PET-GF", kind="print", qty=6,
             notes="Motor bolts fourM3x12 into its face; twoM5 through-bolts fix the slotted plate to metal angles. Slot gives8mm tension adjustment.")
    carrier = box(46,26,29).cut(cylinder(22.5,32).translate((0,0,-1)))
    for hx,hy,hd in hole_grid(34,24,8.4):
        carrier=carrier.cut(cylinder(hd,32).translate((hx,hy,-1)))
    register("paired-nut-spacer", carrier, material="PET-GF", kind="print", qty=6,
             notes="Open cavity for one metal driving nut. Four metal30mm spacers hold metal faces; the29mm printed shell locates/guards and does not carry axial preload.")
    switch = box(45,25,6)
    for hx in (-12,12):
        switch=switch.cut(cylinder(3.4,8).translate((hx,0,-1)))
    switch=switch.cut(cq.Workplane("XY").center(0,-8).slot2D(24,6.5,0).extrude(8).translate((0,0,-1)))
    register("limit-switch-bracket", switch, material="PET-GF", kind="print", qty=28,
             notes="Two M3 switch bolts; one M6 slot to metal frame. Transfer switch holes from selected body. Twelve travel plus twelve opposed overload switches. All four NC contacts per axis are in series.")
    guard=box(115,100,2)
    for x in(-5,5):guard=guard.cut(cylinder(3.4,4).translate((x,-7,-1)))
    register("belt-guard", guard, material="PET-GF", kind="print", qty=6,
             notes="Print flat, open side up. Two M3x25 bolts at localX +/-5,Y-7 pass through 7 mm metal spacers, bulkhead holes (+/-5,13) and the matched right-side thrust-angle feet. Metal grip23.525 mm leaves1.475 mm beyond the nut. Top M6 and M3 washer centers are11.402 mm apart; guard-tube/thrust radial clearance is1.928 mm. Front shield passes through its floor-clearance slot; open edges require guarded supervised commissioning.")
    register("gun-jaw-pad",box(25,34,4),material="TPU",kind="print",qty=4,
             notes="Flat TPU pad between gun body and metal bar. No trigger, vents, nozzle, guide or cable boot contact.")
    register("service-load-jaw-pad",box(35,34,4),material="TPU",kind="print",qty=2,
             notes="Temporary 35 mm wide force-fork jaw pad. Safe rigid gun-body contact only; retract wire and observe nozzle datum before loading.")
    jig=box(60,40,20).cut(cq.Workplane("XY").box(38.4,38.4,22,centered=(True,True,False)).translate((0,0,4)))
    register("hub-drilling-locator",jig,material="PET-GF",kind="print",qty=1,
             notes="Locates hub blank at drill press for marking, not a bushing. Clamp metal stock independently; do not drill while handheld.")
    saddle=box(100,50,10).union(box(12,50,25).translate((-44,0,0))).union(box(12,50,25).translate((44,0,0)))
    saddle=saddle.cut(cylinder(10.5,30).translate((0,0,-1))).cut(cylinder(22.2,7))
    for hx in(-15,15):saddle=saddle.cut(cylinder(3.4,12).translate((hx,0,-1)))
    register("fiber-saddle",saddle,material="PET-GF",kind="print",qty=2,
             notes="Broad padded support on the independent boom, with a loose fabric sling. Never tighten onto optical cable; cable arc radius350mm minimum in use.")


def _member(length,axis="z"):
    solid=box(40,40,length).cut(box(28,28,length+2).translate((0,0,-1)))
    if axis=="x": return solid.rotate((0,0,0),(0,1,0),90).translate((0,0,20))
    if axis=="y": return solid.rotate((0,0,0),(1,0,0),-90).translate((0,0,20))
    return solid


def assembly(pose=None, *, include_gun=True, include_boom=True):
    """Returns (cq.Assembly, receipt). Pose: x/y/zmm; yaw/pitch/rolldeg.

    Names are stable and individual install parts remain individual children.
    Receipt has world transforms and assembly group for every instance.
    """
    init_parts()
    pose={**dict(x=0,y=0,z=0,yaw=0,pitch=0,roll=0),**(pose or {})}
    assy=cq.Assembly(name="gun-positioner")
    receipt=[]
    def add(name,part,p=(0,0,0),R=None,group="station",model=None,notes=""):
        R=np.eye(3) if R is None else np.asarray(R)
        data=PARTS[part]
        shape=data["model"] if model is None else model
        assy.add(shape,name=name,loc=transform(R,p),color=cq.Color(*COLORS[data["material"]]))
        receipt.append(dict(name=name,part=part,group=group,kind=data["kind"],material=data["material"],
                            print_name=part if data["kind"]=="print" else None,
                            translation_mm=[float(v) for v in p],rotation_matrix=R.tolist(),notes=notes))
    # Common metal rectangle,210mmclearance from tubing fixture's left edge.
    for yy in (-270,230):
        add(f"station-long-{yy}","4040-extrusion",(-470,yy,0),group="station",model=_member(750,"x"),notes="4040cut750mm")
    for xx in (-450,260):
        add(f"station-cross-{xx}","4040-extrusion",(xx,-250,0),group="station",model=_member(460,"y"),notes="4040cut460mm")
    for xx in (-75,135):
        add(f"station-rotator-cross-{xx}","4040-extrusion",(xx,-250,0),group="station",model=_member(460,"y"),notes="4040cut460mm; directly supports rotator feet")
    for xx in (float(STAGE_CENTER[0])-200,float(STAGE_CENTER[0])+200):
        add(f"station-x-bed-cross-{xx:.3f}","4040-extrusion",(xx,-250,0),group="station",model=_member(460,"y"),notes="4040 cut460 mm; directly supports X-bed400 mm mounting stations")
    add("rotator-platform","rotator-platform",(30,0,40),group="station")
    sx,sy=float(STAGE_CENTER[0]),float(STAGE_CENTER[1])
    x0=np.array([sx,sy,40.0])
    x1=x0+np.array([pose['x'],0,T+DECK])
    y0=x1+np.array([0,0,T+40])
    y1=y0+np.array([0,pose['y'],T+DECK])
    add("x-bed","x-bed",x0,group="x")
    add("x-carriage","x-carriage",x1,group="x")
    add("y-bed","y-bed",y0,rotation("z",90),group="y")
    add("y-carriage","y-carriage",y1,rotation("z",90),group="y")
    for xx in (-90,90):
        for yy in (-90,90):
            add(f"y-bed-spacer-{xx}-{yy}","deck-metal-spacer",x1+np.array([xx,yy,T]),group="y",notes="10 OD / 8 ID tube, 40 mm long. Four M5x70 through-bolts join the 180 x 180 mm decks; block heads remain clear.")
    # Each stage is drawn from actual selected block envelope and throughbolted deck.
    for prefix,p,R,move in [("x",x0,np.eye(3),pose['x']),("y",y0,rotation("z",90),pose['y'])]:
        for side in (-1,1):
            add(f"{prefix}-rail-{side}","sbr12-rail",p+R@np.array([0,side*70,T]),R,group=prefix)
            for station in (-1,1):
                q=p+R@np.array([move+station*BLOCK_SEPARATION/2,side*70,T+DECK-BLOCK_H])
                add(f"{prefix}-block-{side}-{station}","sbr12uu-block",q,R,group=prefix)
        _linear_drive(add,p+R@np.array([-220,0,T+20]),R,prefix,move+220)

        for end in (-1,1):
            Rs=R@rotation('z',0 if end>0 else 180)
            add(f"{prefix}-stop-back-{end}","linear-stop-angle",p+R@np.array([end*(199+2*T),0,T]),Rs,group=prefix)
            add(f"{prefix}-stop-{end}","limit-stop",p+R@np.array([end*199,0,T+35]),R@rotation('y',90 if end>0 else-90),group=prefix)
            add(f"{prefix}-switch-{end}","limit-switch-bracket",p+R@np.array([end*205,45,T+DECK]),R,group=prefix)
    # Vertical rails are on the tower'sfront(X+)face; two block stations140mmapart.
    zmast=np.array([sx+pose['x'],sy+pose['y'],float(y1[2]+T)])
    for yy in (-70,70):
        add(f"z-upright-{yy}","4040-extrusion",zmast+np.array([-25,yy,0]),group="z",model=_member(600),notes="4040 cut600 mm; top thrust keeps the gravity-loaded Z screw in tension")
    # localplateXbecomesworldZ;localYworldY;normalbecomesworld-X.
    Rz=np.array([[0,0,-1],[0,1,0],[1,0,0]])
    zp=zmast+np.array([0,0,250])
    add("z-bed","z-bed",zp,Rz,group="z")
    zcar=zp+np.array([T+DECK,0,pose['z']])
    add("z-carriage","z-carriage",zcar,Rz,group="z")
    for side in (-1,1):
        add(f"z-rail-{side}","sbr12-rail",zp+np.array([T,side*70,0]),np.array([[0,0,1],[0,1,0],[-1,0,0]]),group="z")
        for station in (-1,1):
            add(f"z-block-{side}-{station}","sbr12uu-block",zp+np.array([T+DECK-BLOCK_H,side*70,pose['z']+station*BLOCK_SEPARATION/2]),np.array([[0,0,1],[0,1,0],[-1,0,0]]),group="z")
    _linear_drive(add,zp+np.array([T+20,0,220]),rotation("y",90),"z",220-pose['z'])

    for end in (-1,1):
        Rs=Rz@rotation('z',0 if end>0 else 180)
        add(f"z-stop-back-{end}","linear-stop-angle",zp+np.array([T,0,end*(199+2*T)]),Rs,group="z")
        add(f"z-stop-{end}","limit-stop",zp+np.array([T+35,0,end*199]),Rz@rotation('y',90 if end>0 else-90),group="z")
        add(f"z-switch-{end}","limit-switch-bracket",zp+np.array([T+DECK,45,end*205]),Rz,group="z")
    C=C0+np.array([pose['x'],pose['y'],pose['z']])
    # Metalcolumn,horizontalbeam,flatadapteranddiagonalbracejoinZdecktoyawbackplane.
    add("z-head-upright","4040-extrusion",(zcar[0]+20,zcar[1],C[2]-30),group="z",model=_member(225),notes="4040 cut225 mm")
    add("z-head-crossbeam","4040-extrusion",(zcar[0]+20,zcar[1],C[2]+195),group="z",model=_member(180,"x"),notes="4040cut180mm")
    fixed=rotation("z",105)
    backxy=C+fixed@np.array([-KP12_H-T,0,0])
    add("z-yaw-head-adapter","yaw-head-adapter",[backxy[0],backxy[1],C[2]+235],fixed,group="z")
    for yy in(-30,0,30):
        add(f"yaw-head-angle-{yy}","metal-angle-25",C+fixed@np.array([-KP12_H-T-11,yy,235+T]),fixed@rotation('z',90),group='yaw')
    dv=np.array([160,0,185]);dv=dv/np.linalg.norm(dv);bn=np.array([0,-1,0]);BR=np.column_stack((dv,np.cross(bn,dv),bn))
    add("z-head-diagonal","z-head-diagonal",[zcar[0]+100,zcar[1]-20,C[2]+102.5],BR,group='z')
    yawR=rotation("z",105+pose['yaw'])
    pitchR=yawR@rotation("y",60+pose['pitch'])
    rollR=pitchR@rotation("x",pose['roll'])
    def local(name,part,v,R,group,extra=None):
        add(name,part,C+R@np.array(v),R if extra is None else R@extra,group=group)
    local("yaw-bearing-back","yaw-bearing-back",[-KP12_H-T,0,195],fixed,"yaw",rotation("y",90))
    # KP12reference isshaftX,andhasbaseZ=0.
    for zz in (155,235):
        K=rotation("y",90)
        local(f"yaw-bearing-{zz}","kp12-bearing",[-KP12_H,0,zz],fixed,"yaw",K)
    add("yaw-shaft","gimbal-shaft-stock",C+fixed@np.array([0,0,80]),fixed,group="yaw",model=shaft_with_end_holes(175),notes="12 mm 304 shaft with centered tapped ends, cut 175mm")
    local("yaw-output-hub","shaft-hub",[0,0,80],yawR,"yaw")
    local("yaw-crossbar","yaw-crossbar",[0,0,105],yawR,"yaw")
    for side in (-1,1):
        local(f"yaw-side-{side}","yaw-side",[0,side*170,15],yawR,"yaw",rotation("x",90*side))
        local(f"pitch-foot-{side}","pitch-bearing-foot",[0,side*133.65,-KP12_H-T],yawR,"pitch")
        local(f"pitch-bearing-{side}","kp12-bearing",[0,side*135,-KP12_H],yawR,"pitch",rotation("z",90))
        shaft_p=[0,-200 if side<0 else 70,0]
        shaft_L=130 if side<0 else 85
        add(f"pitch-shaft-{side}","gimbal-shaft-stock",C+yawR@np.array(shaft_p),yawR,group="pitch",model=shaft_with_end_holes(shaft_L).rotate((0,0,0),(1,0,0),-90),notes=f"12 mm 304 shaft with centered tapped ends, cut {shaft_L}mm")
        local(f"pitch-output-hub-{side}","shaft-hub",[0,side*70,0],pitchR,"pitch",rotation("x",-90*side))
        local(f"pitch-side-{side}","pitch-side",[-125,side*95+(T if side>0 else 0),-15],pitchR,"pitch",rotation("x",90))
    for xx in (-235,-135):
        local(f"pitch-crossbar-{xx}","pitch-rear-crossbar",[xx,0,-45],pitchR,"pitch",rotation("z",90))
    local("roll-bearing-foot","roll-bearing-foot",[-165,0,-KP12_H-T],pitchR,"roll")
    for xx in(-235,-135):
        for yy in(-50,50):local(f"roll-foot-spacer-{xx}-{yy}","roll-foot-metal-spacer",[xx,yy,-32.30],pitchR,"roll")
    local("roll-base-anchor","roll-base-anchor",[-185,0,-38.65],pitchR,"roll")
    for xx in (-210,-122):
        local(f"roll-bearing-{xx}","kp12-bearing",[xx,0,-KP12_H],pitchR,"roll")
    add("roll-shaft","gimbal-shaft-stock",C+pitchR@np.array([-240,0,0]),pitchR,group="roll",model=shaft_with_end_holes(165).rotate((0,0,0),(0,1,0),90),notes="12 mm 304 shaft with centered tapped ends, cut 165mm")
    local("roll-output-hub","shaft-hub",[-106,0,0],rollR,"roll",rotation("y",90))
    def capture(prefix,start,length,R,parent,stackkey):
        axis=parent@R
        origin=C+parent@np.array(start)
        for i,(u,L) in enumerate(CAPTURE_STACKS[stackkey]):
            add(f'{prefix}-capture-tube-{i+1}',capture_tube_name(L),origin+axis@np.array([0,0,u]),axis,group='shaft-capture')
        for side,u in(('lower',0),('upper',length)):
            flip=np.eye(3) if side=='lower' else rotation('x',180)
            direction=1 if side=='lower' else-1
            W=axis@flip
            end=origin+axis@np.array([0,0,u])
            add(f'{prefix}-{side}-end-retainer','shaft-end-retainer-washer',end-W@np.array([0,0,2]),W,group='shaft-capture')
            add(f'{prefix}-{side}-end-flat-washer','shaft-end-flat-washer',end-W@np.array([0,0,2.8]),W,group='shaft-capture')
            add(f'{prefix}-{side}-M5-end-bolt','steel-fastener',end-W@np.array([0,0,2.8]),W,group='shaft-capture',model=_bolt(5,12),notes='M5x12; 2 mm steel retainer plus 0.8 mm flat washer gives 9.2 mm engagement in measured 10 mm usable blind thread. Do not bottom.')
    capture('yaw-shaft',[0,0,80],175,np.eye(3),yawR,'yaw')
    capture('pitch-negative-shaft',[0,-200,0],130,rotation('x',-90),yawR,'pitch-negative')
    capture('pitch-positive-shaft',[0,70,0],85,rotation('x',-90),yawR,'pitch-positive')
    capture('roll-shaft',[-240,0,0],165,rotation('y',90),pitchR,'roll')
    Ryz=np.array([[0,0,1],[1,0,0],[0,1,0]])
    local("roll-cradle-back","roll-cradle-back",[-112.35,0,0],rollR,"roll",Ryz)
    for side in (-1,1):
        local(f"roll-cradle-side-{side}","roll-cradle-side",[2,side*50,-10],rollR,"roll",rotation("x",90))
    for x in (25,65):
        local(f"gun-lower-jaw-{x}","gun-jaw",[x,0,20],rollR,"clamp")
        local(f"gun-lower-pad-{x}","gun-jaw-pad",[x,0,26.35],rollR,"clamp")
        local(f"gun-upper-pad-{x}","gun-jaw-pad",[x,0,64.35],rollR,"clamp")
        local(f"gun-upper-jaw-{x}","gun-jaw",[x,0,68.35],rollR,"clamp")

    # Two rigidly seated axial crash pods; fixed guides are independent of
    # the removable magnetic gun plate. All rods are uncut 100 mm stock.
    K=np.array([[0,0,1],[1,0,0],[0,1,0]])
    springlen=25-12.5/4.68
    shoulder_inner=T/2+FORCE_CAPTURE
    boss_end=10.525;endinner=boss_end+1.5+springlen;endouter=endinner+T
    for sign in(-1,1):
        hand='left' if sign<0 else 'right';y=sign*80
        for zz in(6.35,-23.65):
            local(f"crash-{hand}-ground-guide-{zz}","crash-ground-guide",[14,y,zz],rollR,"crash",rotation('y',90))
            for x in(65-endouter-8,65+endouter):
                local(f"crash-{hand}-collar-{zz}-{x:.3f}","crash-guide-collar",[x,y,zz],rollR,"crash",rotation('y',90))
        for direction in(-1,1):
            x=65-endouter if direction<0 else 65+endinner
            local(f"crash-{hand}-guide-support-{direction}","crash-pod-end",[x,y,-13.65],rollR,"crash",K)
            sh=65-boss_end if direction<0 else 65+4.175
            local(f"crash-{hand}-shoulder-{direction}","crash-pod-shoulder",[sh,y,6.35],rollR,"crash",K)
            bx=65-T/2 if direction<0 else 65+T/2
            local(f"crash-{hand}-boss-{direction}","force-shuttle-boss",[bx,y,6.35],rollR,"crash",K if direction>0 else K@rotation('x',180))
            wx=65-boss_end-1.5 if direction<0 else 65+boss_end
            local(f"crash-{hand}-pressure-washer-{direction}","force-pressure-washer",[wx,y,6.35],rollR,"crash",rotation('y',90))
            sx=65-endinner if direction<0 else 65+boss_end+1.5
            sm=cylinder(12,springlen).cut(cylinder(8.8,springlen+2).translate((0,0,-1)))
            add(f"crash-{hand}-spring-{direction}","crash-spring",C+rollR@np.array([sx,y,6.35]),rollR@rotation('y',90),group='crash',model=sm,notes='Nominal unloaded placement only; set directional preload with actual gun gravity and cable baseline')
        local(f"crash-{hand}-shuttle","crash-pod-shuttle",[65-T/2,y,6.35],rollR,"crash",K)
        local(f"crash-{hand}-upper-bushing","force-bushing",[60,y,6.35],rollR,"crash",rotation('y',90))
        for xx in(45,85):
            local(f"crash-{hand}-lower-guide-block-{xx}","crash-guide-block",[xx-7.5,y,-23.65],rollR,"crash",rotation('y',90))
            local(f"crash-{hand}-lower-bushing-{xx}","force-bushing",[xx-5,y,-23.65],rollR,"crash",rotation('y',90))
        # For the left wall mirror its normal and vertical coordinate.
        WR=np.array([[1,0,0],[0,0,sign],[0,-sign,0]])
        local(f"crash-{hand}-output-wall","crash-output-wall",[65,sign*92.7,-2.3],rollR,"crash",WR)
        local(f"crash-{hand}-carrier",f"crash-carrier-{hand}",[0,sign*65.35,32.7],rollR,"crash")
        for i,(hy,hz,_) in enumerate(hole_grid(32,32,3.4)):
            add(f"crash-{hand}-cage-tie-{i+1}","steel-fastener",C+rollR@np.array([65-endouter,y+hy,6.35+hz]),rollR@rotation('y',90),group='crash',model=_bolt(3,100))
            add(f"crash-{hand}-center-spacer-{i+1}","crash-force-center-spacer",C+rollR@np.array([65-shoulder_inner,y+hy,6.35+hz]),rollR@rotation('y',90),group='crash')
            for sgn in(-1,1):
                pos=65-endinner if sgn<0 else 65+boss_end
                add(f"crash-{hand}-outer-spacer-{i+1}-{sgn}","crash-force-outer-spacer",C+rollR@np.array([pos,y+hy,6.35+hz]),rollR@rotation('y',90),group='crash')
        for i,(hy,hz,_) in enumerate(hole_grid(16,16,3.4)):
            add(f"crash-{hand}-boss-tie-{i+1}","steel-fastener",C+rollR@np.array([65-boss_end,y+hy,6.35+hz]),rollR@rotation('y',90),group='crash',model=_bolt(3,30))
    for xx in(28,102):local(f"crash-fixed-crossbar-{xx}","crash-ground-crossbar",[xx,0,-60],rollR,"crash",rotation('z',90))
    # Hardened three-ball/paired-dowel seats; cup poles are spatially separate.
    front=-88.65;ballx=front+2+math.sqrt(27);back=ballx+math.sqrt(7)+2
    local("crash-magnetic-back","crash-magnet-back",[-95,0,-6.35],rollR,"crash",K)
    local("crash-released-back","gun-release-back",[back,0,-6.35],rollR,"crash",K)
    local("crash-released-tray","gun-release-tray",[0,0,13.65],rollR,"crash")
    for i,(yy,zz) in enumerate(((-40,-20),(40,-20),(0,25))):
        phi=math.atan2(zz,yy);radial=np.array([0,math.cos(phi),math.sin(phi)]);tangent=np.array([0,-math.sin(phi),math.cos(phi)])
        DR=np.column_stack((np.array([1,0,0]),tangent,-radial))
        local(f"crash-ball-{i+1}","crash-ball",[ballx,yy,zz-6.35],rollR,"crash")
        local(f"crash-ball-steel-seat-{i+1}","crash-ball-backing-washer",[ballx+math.sqrt(7),yy,zz-6.35],rollR,"crash",K)
        for dy in(-9,9):add(f'crash-ball-backing-M3-{i+1}-{dy}','steel-fastener',C+rollR@np.array([ballx+math.sqrt(7)-.5,yy+dy,zz-6.35]),rollR@K,group='crash',model=_bolt(3,20),notes='M3x20 through drilled steel washer and aluminum backplate, one flat washer and locking nut.')
        for ds in(-1,1):
            v=np.array([front+2,yy,zz-6.35])+3*ds*tangent-10*radial
            local(f"crash-V-dowel-{i+1}-{ds}","crash-vee-dowel",v,rollR,"crash",DR)
        for es in(-1,1):
            v=np.array([front+4,yy,zz-6.35])+9*es*radial
            KR=np.column_stack((tangent,radial,np.array([1,0,0])))
            local(f"crash-seat-keeper-{i+1}-{es}","vee-seat-keeper",v,rollR,"crash",KR)
    for i,(yy,zz) in enumerate(((-30,15),(30,15),(0,-25))):
        local(f"crash-cup-magnet-{i+1}","crash-magnet",[front,yy,zz-6.35],rollR,"crash",rotation('y',90))
        local(f"crash-cup-striker-{i+1}","crash-striker",[back-2,yy,zz-6.35],rollR,"crash",rotation('y',90))
        add(f"crash-cup-bolt-{i+1}","steel-fastener",C+rollR@np.array([front+7.7,yy,zz-6.35]),rollR@rotation('y',-90),group='crash',model=_bolt(5,25),notes='Reference only: actual countersunk M5x25, head flushness checked from source part')
    for channel in('hard','sense'):
        yy=-58 if channel=='hard' else 58
        local(f"crash-{channel}-axial-contact","limit-switch-bracket",[65,yy,39.05],rollR,"crash")
        local(f"crash-{channel}-plate-presence","limit-switch-bracket",[-83,yy,-6.35],rollR,"crash",K)
    for zz in(162.3,235):local(f"yaw-base-web-{zz}","yaw-base-web",[65,-90,zz],fixed,"yaw")
    PW=np.array([[1,0,0],[0,0,1],[0,-1,0]])
    for yy in(-207.70,-135):local(f"pitch-base-web-{yy}","pitch-base-web",[110,yy,-40],yawR,"pitch",PW)
    for xx in(-206.70,-134):local(f"roll-base-web-{xx}","roll-base-web",[xx,70,-108.45],pitchR,"roll",Ryz)
    for xx in(-20,20):
        for zz in(-60,-20):
            local(f"pitch-web-left-spacer-{xx}-{zz}","pitch-web-left-spacer",[xx,-201.35,zz],yawR,"pitch",rotation('x',-90))
            local(f"pitch-web-right-spacer-{xx}-{zz}","pitch-web-right-spacer",[xx,-163.65,zz],yawR,"pitch",rotation('x',-90))
    for side in(-1,1):
        for xx in(-30,30):
            local(f'yaw-side-angle-{side}-{xx}','metal-angle-25',[xx,side*150.95,105],yawR,'yaw',rotation('z',0 if side>0 else 180)@rotation('x',180))
            local(f'pitch-foot-angle-{side}-{xx}','metal-angle-25',[xx,side*150.95,-19],yawR,'pitch',rotation('z',180 if side>0 else 0))
        for bx in(-235,-135):
            for xx in(-10,10):local(f'pitch-cross-angle-{side}-{bx}-{xx}','metal-angle-25',[bx+xx,side*82.3,-38.65],pitchR,'pitch',rotation('z',180 if side>0 else 0))
        for zz in(-20,5):local(f'roll-cradle-angle-{side}-{zz}','metal-angle-25',[-106,53.175 if side>0 else -59.525,zz],rollR,'roll',rotation('y',90)@(rotation('z',180) if side<0 else np.eye(3)))
    for zz in(162.3,235):
        for yy in(-20,20):local(f'yaw-base-web-angle-{zz}-{yy}','metal-angle-25',[-25,yy,zz],fixed,'yaw',rotation('y',90))
    for xx in(-206.7,-134):
        for yy in(70,90):local(f'roll-base-web-angle-{xx}-{yy}','metal-angle-25',[xx+12.7,yy,-32.3],pitchR,'roll',rotation('z',90))
    for hand,sign in(('left',-1),('right',1)):
        for xx in(28,102):
            local(f'crash-ground-to-cradle-angle-{hand}-{xx}','metal-angle-25',[xx,sign*37.3,-53.65],rollR,'crash')
            local(f'crash-ground-to-pod-angle-{hand}-{xx}','metal-angle-25',[xx,sign*80,-53.65],rollR,'crash',rotation('y',90))
        for zz in(-15,15):local(f'crash-output-wall-angle-{hand}-{zz}','metal-angle-25',[65,sign*92.7,zz],rollR,'crash',rotation('y',90))
        for xx in(45,85):local(f'crash-carrier-angle-{hand}-{xx}','metal-angle-25',[xx,sign*80,32.7],rollR,'crash',rotation('x',180))
        local(f'crash-magnetic-carrier-angle-{hand}','metal-angle-25',[-95,sign*50,32.7],rollR,'crash',rotation('y',90))
        local(f'crash-release-back-angle-{hand}','metal-angle-25',[-70.459,sign*35,20],rollR,'crash',rotation('y',90)@(rotation('z',180) if sign<0 else np.eye(3)))
    # Tangent actuator plans. Local u,v,Nareorthonormal; positiveθlengthensscrew.
    planes=[("yaw",fixed,yawR,np.array([1,0,0]),np.array([0,1,0]),np.array([0,0,1]),np.array([0,0,205]),pose['yaw']),
            ("pitch",yawR@rotation("y",60),pitchR,np.array([1,0,0]),np.array([0,0,-1]),np.array([0,1,0]),np.array([0,-165,0]),pose['pitch']),
            ("roll",pitchR,rollR,np.array([0,1,0]),np.array([0,0,1]),np.array([1,0,0]),np.array([-164,0,0]),pose['roll'])]
    for name,parent,moving,u,v,n,offset,ang in planes:
        aa=math.radians(ang)
        A=offset+LEVER*u-L0*v
        P=offset+LEVER*math.cos(aa)*u+LEVER*math.sin(aa)*v
        d=(P-A)/np.linalg.norm(P-A)
        lateral=np.cross(n,d)
        driveR=parent@np.column_stack((d,n,lateral))
        _linear_drive(add,C+parent@A,driveR,name,float(np.linalg.norm(P-A)),angular=True,base_outer_R=parent@np.column_stack((v,n,-u)),lever_outer_R=moving@np.column_stack((v,n,-u)))
        S=moving@np.column_stack((v,n,-u))
        bridgeP=C+parent@P+S@np.array([20,0,0])-T*parent@n
        B=np.column_stack((S[:,0],S[:,2],parent@n))
        add(f"{name}-output-bridge","angular-output-bridge",bridgeP,B,group=name)
        for ns in(-1,1):
            for ls in(-1,1):
                pos=C+parent@P+S@np.array([40,-30 if ns<0 else 0,ls*10])
                add(f"{name}-output-spacer-{ns}-{ls}","angular-output-spacer",pos,S@rotation('x',-90),group=name)
        leverR=np.column_stack((u,v,n))
        local(f"{name}-lever","angular-lever",offset+75*u,moving,name,leverR)
        for end in (-1,1):
            hard_angle=end*HARD_ANGLE if name!="pitch" or end<0 else 12
            switch_angle=end*21 if name!="pitch" or end<0 else 11
            local(f"{name}-metal-stop-{end}","limit-stop",offset+145*(math.cos(math.radians(hard_angle))*u+math.sin(math.radians(hard_angle))*v),parent,name,leverR)
            local(f"{name}-switch-{end}","limit-switch-bracket",offset+140*(math.cos(math.radians(switch_angle))*u+math.sin(math.radians(switch_angle))*v)+18*n,parent,name,leverR)
        # Shafts with centered end threads use individually proof-qualified split hubs.
        hub_v=offset-25*n
        local(f"{name}-lever-hub","shaft-hub",hub_v,moving,name,leverR)
    if include_gun:
        g=box(135,34,34).translate((14.5,0,30.35))
        g=g.union(cylinder(24,18).rotate((0,0,0),(0,1,0),90).translate((82,0,47.35)))
        g=g.union(cylinder(11,46).rotate((0,0,0),(0,1,0),90).translate((100,0,47.35)))
        g=g.union(cylinder(17,31).rotate((0,0,0),(0,1,0),90).translate((146,0,47.35)))
        g=g.union(cylinder(4.4,23).rotate((0,0,0),(0,1,0),90).translate((177,0,47.35)))
        g=g.union(box(35,28,95).translate((-36,0,-64.65)))
        register("gun-envelope",g,material="gun-proxy",kind="proxy",notes="253x143x34mmX1proxy; not a scan,clampfit,heatqualification or vendorCAD.")
        local("gun-proxy","gun-envelope",[0,0,0],rollR,"gun")
        add("aim-endpoint","kp12-bearing",DOT+np.array([pose['x'],pose['y'],pose['z']]),group="gun",model=cylinder(2,1),notes="Reference endpoint,notmeasuredwireendpoint")
    if include_boom:
        # Independentfiberpostoppositeedge;two750mmmetalarmsegmentsadmitasweeping350mmradiusarc.
        add("fiber-post","4040-extrusion",(430,-230,T),group="fiber",model=_member(900),notes="4040cut900mm;independentofcameraandmotionframes")
        add("fiber-top-arm","4040-extrusion",(410,-230,860+T),group="fiber",model=_member(750,"x"),R=rotation("z",180),notes="4040 cut750 mm; arm points toward the gun, independently anchored to bench")
        for xx in(100,-250):
            add(f"fiber-swivel-base-{xx}","fiber-swivel-base",(xx,-230,910+T),group='fiber')
            for h,(hx,hy,_) in enumerate(hole_grid(28,28,6.5)):
                add(f'fiber-base-spacer-{xx}-{h}',"fiber-base-metal-spacer",(xx+hx,-230+hy,900+T),group='fiber')
                add(f'fiber-base-bolt-{xx}-{h}',"steel-fastener",(xx+hx,-230+hy,921+T),rotation('x',180),group='fiber',model=_bolt(6,30))
            add(f"fiber-swivel-bearing-{xx}","608zz-bearing",(xx,-230,922.5+T),group='fiber')
            add(f'fiber-axle-lower-tube-{xx}',"fiber-axle-lower-tube",(xx,-230,909.5+T),group='fiber')
            add(f'fiber-axle-upper-tube-{xx}',"fiber-axle-upper-tube",(xx,-230,929.5+T),group='fiber')
            add(f'fiber-axle-{xx}',"steel-fastener",(xx,-230,908+T),group='fiber',model=_bolt(8,50),notes='Head and bottom washer have0.5 mm clearance belowbase. Axle clamps metal tubes and inner race only; saddle rotates with outer race.')
            add(f'fiber-bearing-cap-{xx}',"fiber-bearing-cap",(xx,-230,920.5+T),group='fiber')
            add(f'fiber-saddle-{xx}',"fiber-saddle",(xx,-230,922.5+T),group='fiber')
            for hx in(-15,15):add(f'fiber-bearing-cap-bolt-{xx}-{hx}',"steel-fastener",(xx+hx,-230,920.5+T),group='fiber',model=_bolt(3,20))
    return assy,receipt


def _bolt(d,length):
    return cylinder(d,length).union(cq.Workplane("XY").polygon(6,1.8*d).extrude(.65*d).translate((0,0,-.65*d)))


def shaft_with_end_holes(length):
    """Concentric blind end holes; no transverse holes in the shaft."""
    s=cylinder(12,length)
    end=cylinder(5,10).union(cylinder(4.2,16))
    return s.cut(end).cut(end.rotate((0,0,0),(1,0,0),180).translate((0,0,length)))


def _linear_drive(add,p,R,prefix,nut_center,angular=False,base_outer_R=None,lever_outer_R=None,length_override=None):
    """Metal thrust, single moving nut, captured seated overload link.

    LocalX is screw length, localY clevis normal, localZ tangent-plane lateral.
    All hardware remains named and independent for the illustrated guide.
    """
    p=np.asarray(p);R=np.asarray(R)
    def item(name,part,v=(0,0,0),extra=None,model=None,notes=""):
        add(f"{prefix}-{name}",part,p+R@np.array(v),R if extra is None else R@extra,group=prefix,model=model,notes=notes)
    X=rotation("y",90)
    K=X if angular else np.array([[0,0,1],[1,0,0],[0,1,0]])
    length=length_override or (300 if angular else 400)
    item("screw","tr8-screw-stock",model=cylinder(8,length).rotate((0,0,0),(0,1,0),90).translate((-30,0,0)),notes=f"TR8x2 screw cut{length} mm, thread envelope")
    item("fixed-floor","linear-drive-support",[-20,25,-32.7])
    item("radial-bearing","kp08-bearing",[-25,0,-15])
    for yy in(-21,21):item(f"radial-riser-{yy}","kp08-fixed-riser",[-25,yy,-26.35])
    if not angular:
        for yy in(-21,21):item(f"floating-riser-{yy}","kp08-floating-riser",[360,yy,-20])
    if not angular:item("floating-bearing","kp08-bearing",[360,0,-15],notes="Axial float; no nut outside this bearing")
    item("thrust-bulkhead","drive-bulkhead",[10,0,0],X)
    for x in(5,16.35):item(f"thrust-{x}","f8-16m-thrust",[x,0,0],X)
    item("fixed-retention-nut-left","tr8x2-nut",[-10,0,0],X,notes="243 threadlocker,24 hour cure,witness line; set thrust preload before cure")
    item("fixed-retention-nut-right","tr8x2-nut",[36.35,0,0],rotation("y",-90),notes="243 locked unoccupied flange for gravity retainer")
    for x in(-5,21.35):item(f"thrust-body-spacer-{x}","thrust-body-clearance-spacer",[x,0,0],X)
    item("pulley80","pulley-80t",[-16.7,0,0],X)
    item("pinion20","gt2-20t-pinion",[-20.7,57,0],X)
    item("motor","nema17-motor",[-83.5,57,0],X)
    item("motor-tension","motor-tension-plate",[-35.5,57,25],X)
    for zz in(-25.46,25.46):item(f"belt-span-{zz}","gt2-belt",[-13.2,28.5,zz],rotation("z",90))
    item("belt-guard","belt-guard",[1,20,0],X)
    for hx in(-5,5):
        item(f'guard-spacer-{hx}','guard-metal-spacer',[3,13,-hx],X)
        item(f'guard-M3-{hx}','steel-fastener',[.5,13,-hx],X,model=_bolt(3,25),notes='M3x25 through guard2, spacer7, bulkhead6.35 and top-angle foot3.175. Two0.5 mm washers and nut4 leave1.475 mm protrusion, more than two0.5 mm threads.')
        for gx in(.5,19.525):item(f'guard-washer-{hx}-{gx}','steel-fastener',[gx,13,-hx],X,model=cylinder(7,.5).cut(cylinder(3.4,2).translate((0,0,-1))))
        item(f'guard-nut-{hx}','steel-fastener',[20.025,13,-hx],X,model=cylinder(6,4).cut(cylinder(3,6).translate((0,0,-1))))
    L=np.array([[0,1,0],[0,0,1],[1,0,0]])
    for hand,ny in(('left',25.175),('right',82.475)):
        item(f"motor-support-leg-{hand}","motor-support-leg",[-48.2,ny,23.65],L)
        upper_n=22 if hand=='left' else 92
        ur=rotation('y',-90)@(rotation('z',180) if hand=='left' else np.eye(3))
        item(f"motor-upper-angle-{hand}","metal-angle-25",[-35.5,upper_n,60],ur)
        footn=44.225 if hand=='left' else 69.775
        item(f"motor-foot-angle-{hand}","metal-angle-25",[-48.2,footn,-26.35],np.eye(3) if hand=='left' else rotation('z',180))
    for hand,ny in(('left',-31.525),('right',25.175)):
        item(f"thrust-support-leg-{hand}","thrust-support-leg",[29.05,ny,2.325],L)
        for zz in(-12,12):
            nr=rotation('y',90)@(rotation('z',180) if hand=='right' else np.eye(3))
            apart=('guard-thrust-angle-minus' if zz<0 else 'guard-thrust-angle-plus') if hand=='right' else 'metal-angle-25'
            item(f"thrust-post-angle-{hand}-{zz}",apart,[16.35,-22 if hand=='left' else 22,zz],nr,notes='Enlarge the bulkhead-leg hole to6.5 mm for the shared M6 post. Right-side feet include the3.4 mm guard passage matched to bulkhead(+/-5,13); other leg stays5.5 mm.')
        footn=-34.7 if hand=='left' else 34.7
        item(f"thrust-foot-angle-{hand}","metal-angle-25",[41.05,footn,-20],rotation('z',180) if hand=='left' else np.eye(3))
        if angular:item(f"thrust-foot-pad-{hand}","thrust-angle-pad",[37.05,footn,-26.35])
    for i,(hx,hy,_) in enumerate(hole_grid(31,31,3.4,center=(25,0))):
        item(f"motor-bolt-{i+1}","steel-fastener",[-27.5,57+hy,25-hx],rotation("y",-90),model=_bolt(3,12))
    for a in(0,90,180,270):
        yy=8*math.sin(math.radians(a));zz=-8*math.cos(math.radians(a))
        item(f"pulley-bolt-{a}","steel-fastener",[-17.9,yy,zz],X,model=_bolt(3,20))
    # Single metal drive nut eliminates forced phasing between uncertain leads.
    item("single-driving-nut","tr8x2-nut",[nut_center-16.5,0,0],X)
    item("nut-face-left","nut-face",[nut_center-21.35,0,0],K)
    item("nut-face-right","nut-face",[nut_center+15,0,0],K)
    item("nut-print-locator","paired-nut-spacer",[nut_center-14.5,0,0],K)
    # Face holes and metal tubes take axial load; print only locates the shell.
    for i,(a,b,_) in enumerate(hole_grid(34,24)):
        radial=K@np.array([a,b,0])
        item(f"nut-metal-spacer-{i+1}","nut-metal-spacer",[nut_center-15,radial[1],radial[2]],X)
    # Seated spring link: each washer stays on a fixed shoulder until preload
    # is exceeded, giving a rigid neutral joint without soft guide compliance.
    k=43.0
    preloads={sign:(130.0 if prefix=='pitch' else 100.0 if angular else 400.0 if prefix=='z' and sign>0 else 250.0) for sign in(-1,1)}
    spring_lengths={sign:20-preloads[sign]/(2*k) for sign in(-1,1)}
    shoulder_inner=T/2+FORCE_CAPTURE
    boss_end=shoulder_inner+T
    end_inners={sign:boss_end+1.5+spring_lengths[sign] for sign in(-1,1)}
    end_outers={sign:end_inners[sign]+T for sign in(-1,1)}
    end_outer=end_outers[-1]
    item("overload-shuttle","force-link-shuttle",[nut_center-T/2,0,0],K)
    for sign in(-1,1):
        plane=nut_center-end_outers[sign] if sign<0 else nut_center+end_inners[sign]
        item(f"force-end-{sign}","force-link-end",[plane,0,0],K)
        shoulder=nut_center-boss_end if sign<0 else nut_center+shoulder_inner
        item(f"force-shoulder-{sign}","force-link-shoulder",[shoulder,0,0],K)
    for gi,g in enumerate((-36,36)):
        radial=K@np.array([g,0,0]);ny,nz=radial[1],radial[2]
        item(f"force-guide-bolt-{gi+1}","steel-fastener",[nut_center-end_outer,ny,nz],X,model=_bolt(8,90),notes="Partially threaded grade8.8; smooth shank covers the entire bronze guide")
        item(f"force-guide-bushing-{gi+1}","force-bushing",[nut_center-5,ny,nz],X)
        for sign in(-1,1):
            boss_x=nut_center-T/2 if sign<0 else nut_center+T/2
            item(f"force-boss-{gi+1}-{sign}","force-shuttle-boss",[boss_x,ny,nz],K if sign>0 else K@rotation('x',180))
            washer_x=nut_center-boss_end-1.5 if sign<0 else nut_center+boss_end
            item(f"force-washer-{gi+1}-{sign}","force-pressure-washer",[washer_x,ny,nz],X)
            spring_length=spring_lengths[sign]
            spring_x=nut_center-end_inners[sign] if sign<0 else nut_center+boss_end+1.5
            spring_model=cylinder(16,spring_length).cut(cylinder(8.5,spring_length+2).translate((0,0,-1)))
            item(f"force-spring-{gi+1}-{sign}","force-spring",[spring_x,ny,nz],X,model=spring_model,notes=f"Directional pair preload {preloads[sign]} N; grade by measured trip force")
        for hi,(a,b,_) in enumerate(hole_grid(16,16,3.4)):
            v=K@np.array([g+a,b,0]);item(f"force-boss-bolt-{gi+1}-{hi+1}","steel-fastener",[nut_center-boss_end,v[1],v[2]],X,model=_bolt(3,30))
    for hi,(a,b,_) in enumerate(hole_grid(34,24)):
        v=K@np.array([a,b,0])
        item(f"nut-frame-tie-{hi+1}","steel-fastener",[nut_center-end_outer,v[1],v[2]],X,model=_bolt(5,90))
        for sign in(-1,1):
            face_spacer=end_inners[sign]-21.35
            x=nut_center-end_inners[sign] if sign<0 else nut_center+21.35
            model=cylinder(8,face_spacer).cut(cylinder(6,face_spacer+2).translate((0,0,-1)))
            item(f"nut-outer-spacer-{hi+1}-{sign}",("nut-outer-pitch-metal-spacer" if prefix=="pitch" else "nut-outer-angular-metal-spacer" if angular else "nut-outer-Z-down-metal-spacer" if prefix=="z" and sign>0 else "nut-outer-XYZ-metal-spacer"),[x,v[1],v[2]],X,model=model)
    for hi,(a,b,_) in enumerate(hole_grid(100,30)):
        v=K@np.array([a,b,0])
        item(f"force-cage-tie-{hi+1}","steel-fastener",[nut_center-end_outer,v[1],v[2]],X,model=_bolt(5,90))
        item(f"force-cage-center-spacer-{hi+1}","force-center-metal-spacer",[nut_center-shoulder_inner,v[1],v[2]],X,model=cylinder(8,2*shoulder_inner).cut(cylinder(6,2*shoulder_inner+2).translate((0,0,-1))))
        for sign in(-1,1):
            outer_spacer=end_inners[sign]-boss_end
            x=nut_center-end_inners[sign] if sign<0 else nut_center+boss_end
            model=cylinder(8,outer_spacer).cut(cylinder(6,outer_spacer+2).translate((0,0,-1)))
            item(f"force-cage-outer-spacer-{hi+1}-{sign}",("force-outer-pitch-metal-spacer" if prefix=="pitch" else "force-outer-angular-metal-spacer" if angular else "force-outer-Z-down-metal-spacer" if prefix=="z" and sign>0 else "force-outer-XYZ-metal-spacer"),[x,v[1],v[2]],X,model=model)
    for sign in(-1,1):
        item(f"overload-switch-{sign}","limit-switch-bracket",[nut_center+sign*12,0,33],K,notes="OpposedNC switches, nominal trip0.30 mm angular or0.75 mm XYZ. Flat dwell aftertrip; required overtravel0.8/0.35 mm")
    item("overload-flag","overload-switch-tab",[nut_center,0,28],K)
    if not angular:
        for sign in(-1,1):item(f"carriage-output-angle-{sign}","metal-angle-25",[nut_center+14.175,sign*51,20],rotation('z',90)@rotation('x',180),notes="Vertical leg bolts to shuttle; foot under carriage. Transfer foot hole to two governed carriage coordinates.")
    # Spring-loaded dry friction at the right flange; never shares pulley face.
    if prefix in('z','pitch','roll'):
        target={'z':.215,'pitch':.07,'roll':.03}[prefix]
        force=target/(.25*.008943915);spring_len=25-force/30
        item("friction-washer","friction-washer",[34.85,0,0],X)
        item("friction-spring","friction-spring",[37.85,0,0],X,model=cylinder(25,spring_len).cut(cylinder(13.5,spring_len+2).translate((0,0,-1))),notes="Source rate unspecified: grade actualforce/rate beforeacceptance; nominalplacementonly")
        seat=37.85+spring_len
        item("friction-preload-seat","friction-spring-seat",[seat,0,0],X)
        for hi,(a,b,_) in enumerate(hole_grid(24,44,6.5)):
            item(f"friction-preload-post-{hi+1}","steel-fastener",[10,b,-a],X,model=_bolt(6,72.5),notes="BuyM6x80 andcut underheadlength72.5 mm; twojamnuts atspringseat")
        for a in(-15,15):item(f"friction-guide-pin-{a}","steel-fastener",[seat+T,0,-a],rotation('y',-90),model=_bolt(3,50),notes="Steelwasher slides freely and maytilt; pins carryonlyanti-rotation torque")
    if angular:
        for end,x,outer in(("base",0,base_outer_R),("lever",nut_center,lever_outer_R)):
            outer=R if outer is None else np.asarray(outer)
            center=p+R@np.array([x,0,0])
            for sign in(-1,1):
                add(f"{prefix}-{end}-clevis-{sign}","angular-clevis-cheek",center+outer@np.array([20,sign*30,0]),outer@rotation('x',90),group=prefix)
                add(f"{prefix}-{end}-hinge-bearing-{sign}","f688zz-bearing",center+outer@np.array([0,sign*30,0]),outer@rotation('x',90),group=prefix)
                add(f"{prefix}-{end}-hinge-pin-{sign}","steel-fastener",center+outer@np.array([0,sign*40,0]),outer@rotation('x',90*sign),group=prefix,model=_bolt(8,50),notes='Smooth shank across bearing; finish metal inner-race spacers to thread start')
                item(f"{end}-inner-ear-{sign}","trunnion-inner-ear",[x,sign*22,0],rotation('x',90))
                for hx in(-12,12):item(f"{end}-inner-ear-angle-{sign}-{hx}","metal-angle-25",[x+hx,sign*22,12],rotation('x',90))


def fixture_assemblies():
    """Source-bound service scenes: map from stable scene name to (assembly,receipt)."""
    init_parts();result={}
    def start(name):
        a=cq.Assembly(name=name);receipt=[]
        def add(n,part,p=(0,0,0),R=None,group='fixture',model=None,notes=''):
            R=np.eye(3) if R is None else np.asarray(R);d=PARTS[part]
            a.add(d['model'] if model is None else model,name=n,loc=transform(R,p),color=cq.Color(*COLORS[d['material']]))
            receipt.append(dict(name=n,part=part,group=group,kind=d['kind'],material=d['material'],print_name=part if d['kind']=='print' else None,translation_mm=list(map(float,p)),rotation_matrix=R.tolist(),notes=notes))
        return a,receipt,add
    a,r,add=start('powered-force-fixture');D=rotation('y',-90)
    _linear_drive(add,np.zeros(3),D,'test-drive',125,angular=True,length_override=200)
    add('test-fixed-foot','drive-test-foot',(50,0,-101.35),notes='Clampfixedfoot independently from gauge vise; two metalangles transferfromverticaldrivefloor')
    K=np.array([[0,1,0],[1,0,0],[0,0,-1]])
    # Bridge top is the measured compression contact185 mm ahead ofdatum.
    add('test-output-bridge','test-output-bridge',(0,0,191.35),K)
    AR=np.array([[0,1,0],[0,0,1],[1,0,0]])
    for hand,y in(('left',-65),('right',65)):
        add(f'test-output-arm-{hand}','test-output-arm',(0,y,155),AR)
        add(f'test-fork-angle-{hand}-lower','metal-angle-25',(0,y,130),rotation('y',90))
        add(f'test-fork-angle-{hand}-upper','metal-angle-25',(0,y,180),rotation('y',90))
    add('test-gauge-backing','force-gauge-backing',(0,30,265),rotation('x',90),notes='500 N gauge mountedvertically, loadaxisdown. ActualincludedM4 rearengagementverified.')
    gm=box(64,30,130).translate((0,0,200)).union(cylinder(6,15).translate((0,0,185)))
    add('test-gauge-envelope','steel-fastener',model=gm,notes='Catalog envelope only,compressionprobe185 mm; actualgageandvisecondatum setonassembly')
    result['powered-force-fixture']=(a,r)
    a,r,add=start('nozzle-loading-fork');K=np.array([[0,0,1],[1,0,0],[0,1,0]])
    add('load-clamp-lower','service-load-jaw',(45,0,20));add('load-clamp-upper','service-load-jaw',(45,0,68.35))
    add('load-clamp-lower-pad','service-load-jaw-pad',(45,0,26.35));add('load-clamp-upper-pad','service-load-jaw-pad',(45,0,64.35))
    for sign in(-1,1):
        ar=rotation('x',90*sign)
        add(f'nozzle-fork-arm-{sign}','nozzle-test-fork-arm',(100,sign*80,55.65),ar)
        add(f'nozzle-rear-angle-{sign}','metal-angle-25',(55,sign*70.475,68.35),rotation('z',180 if sign<0 else 0)@rotation('x',180))
        add(f'nozzle-front-angle-{sign}','metal-angle-25',(205,sign*60.95,47.35),rotation('y',-90)@(rotation('z',180) if sign>0 else np.eye(3)))
    add('nozzle-fork-bridge','nozzle-test-bridge',(205,0,47.35),K)
    eye=_bolt(6,40).cut(cylinder(3.5,10).rotate((0,0,0),(1,0,0),90).translate((0,5,5)))
    add('nozzle-cord-stud','steel-fastener',(195,0,47.35),rotation('y',90),model=eye,notes='M6x40 grade8.8,3.5 mm crosshole5 mm fromunderhead; twoM6jamnuts lockbothbridgefaces. Actualholecentroidisobservedvirtualdatum.')
    result['nozzle-loading-fork']=(a,r)
    a,r,add=start('torque-redirect')
    add('redirect-metal-bracket','torque-redirect-bracket');add('redirect-bearing','608zz-bearing',(0,0,T+3));add('redirect-wheel','torque-cord-pulley',(0,0,T+3));add('redirect-outer-race-cap','fiber-bearing-cap',(0,0,T+1));add('redirect-lower-contact','redirect-lower-contact-tube',(0,0,T));add('redirect-upper-contact','redirect-upper-contact-tube',(0,0,T+10));add('redirect-smooth-axle','steel-fastener',(0,0,-1.5),model=_bolt(8,50))
    result['torque-redirect']=(a,r)
    a,r,add=start('torque-lever')
    add('balanced-torque-lever','brake-torque-lever');add('rotating-retention-nut','tr8x2-nut',(0,0,-5),notes='Temporarily replaces pulley; frictionwasher stays onoppositeflange')
    for x in(-100,100):add(f'torque-load-hole-{x}','steel-fastener',(x,0,T),model=_bolt(5,20))
    result['installed-torque-lever']=(a,r)
    a,r,add=start('installed-z-load-bound')
    add('z-test-column','4040-extrusion',model=_member(500),notes='Finished500 mm cut from existing eighth1220 mm stick. Independently brace to station using two matched40-series brackets.')
    add('z-gauge-back','installed-Z-gauge-back',(0,-30,250),rotation('x',90))
    add('z-gauge-envelope','steel-fastener',model=box(64,30,130).translate((0,-48,185)).union(cylinder(6,15).translate((0,-48,315))),notes='Reference compression-gauge envelope only; actual probe height sets column mounting position.')
    add('z-load-platen','installed-Z-load-platen',(0,-48,330))
    for z in(178,322):add(f'z-gauge-spacer-{z}','installed-Z-gauge-spacer',(0,-30,z),rotation('x',90))
    add('z-gauge-jack-angle','installed-Z-jack-angle',(0,-20,110),rotation('z',90))
    add('z-gauge-jack-screw','steel-fastener',(0,-33,90),model=_bolt(6,80),notes='Fully threaded M6x80. Lower working nut reacts only into metal angle; hand wrench supplies rotation constraint, not a load bypass. Lock upper nut after each feed.')
    result['installed-z-load-bound']=(a,r)

    a,r,add=start('hub-clamp-proof')
    # Canonical actual-seat layout for the 85 mm terminal output shaft.
    H=75.35;Q=rotation('x',-90)
    add('proof-horizontal-column','4040-extrusion',(0,-200,0),model=_member(500,'y'),notes='Reuse the 500 mm Z-test column horizontally, positively secured to the bench. No Z load-test fixture is active simultaneously.')
    add('proof-completed-shaft','gimbal-shaft-stock',(0,0,H),Q,model=shaft_with_end_holes(85),notes='Actual finished 85 mm shaft and terminal seat; remove end washers and all capture tubes during horizontal proof. Catch is independent and does not touch the specimen.')
    add('proof-specimen-hub','shaft-hub',(0,0,H),Q,notes='Specimen0..25. No vise contact. Both clamp bolts remain at the measured25 in-lb setting.')
    add('proof-companion-hub','shaft-hub',(0,26,H),Q,notes='Companion26..51: visible1 mm face gap prevents face-friction torque bypass.')
    add('proof-loaded-lever','hub-proof-lever',(0,-T,H),Q,notes='Plate-6.35..0; gauge force at measured +/-140 mm and lever midplaneY=-3.175.')
    add('proof-reaction-plate','angular-lever',(75,51,H),Q,notes='Only free plate metal X95..130 enters positively mounted vise jaws. Neither hub nor shaft is gripped by the vise.')
    add('proof-support-foot','pitch-bearing-foot',(0,66.35,40))
    add('proof-far-KP001','kp12-bearing',(0,66.35,56.35),rotation('z',90),notes='One borrowed bearing center66.35, body58.35..74.35, 1 mm clear of the reaction plate. One 10 mm metal riser under each foot; source statics are a conservative local overhang screen, not a two-bearing beam claim.')
    for x in(-28,28):add(f'proof-bearing-riser-{x}','proof-bearing-riser',(x,66.35,46.35))
    for x in(-28,28):add(f'proof-bearing-M6-{x}','steel-fastener',(x,66.35,37.35),model=_bolt(6,40),notes='Two M6x40 grade12.9 bolts through 6 mm foot, 10 mm riser and 6.35 mm plate; original bearing nuts and washers reused. Verify at least two protruding threads.')
    for y in(46.35,86.35):add(f'proof-foot-M8-{y}','steel-fastener',(0,y,47.85),rotation('x',180),model=_bolt(8,16),notes='Kit-spare M8x16/slot8 T-nut/washer; 6.35 mm plate +1.5 mm washer leaves8.15 mm reach. Verify no bottoming.')
    for hub_y in(0,26):
        for x,z,_ in hole_grid(26,20):add(f'proof-hub-M5-{hub_y}-{x}-{z}','steel-fastener',(x,hub_y-3,H-z),Q,model=_bolt(5,45),notes='Four actual M5x45 plate/hub bolts per hub, reused for service.')
        for hz in(6,19):
            add(f'proof-clamp-M4-{hub_y}-{hz}','steel-fastener',(-20.05,hub_y+hz,H-16),rotation('y',90),model=_bolt(4,50),notes='Actual M4x50 grade 12.9 clamp bolt. Clockwise 10, 20, then 25 in-lb at the head while holding the nut; never exceed the qualified setting.')
            for x in(-20.05,19.05):add(f'proof-clamp-washer-{hub_y}-{hz}-{x}','steel-fastener',(x,hub_y+hz,H-16),rotation('y',90),model=cylinder(9,1).cut(cylinder(4.5,3).translate((0,0,-1))))
            add(f'proof-clamp-nut-{hub_y}-{hz}','steel-fastener',(20.05,hub_y+hz,H-16),rotation('y',90),model=cylinder(8,5).cut(cylinder(4,7).translate((0,0,-1))))
    loadx=140;contact=H-3.175
    add('proof-load-bridge','hub-proof-load-saddle',(loadx,-T/2,H-9.525))
    add('proof-load-front-angle','metal-angle-25',(loadx,12.7,H-12.7))
    add('proof-load-back-angle','metal-angle-25',(loadx,-T-12.7,H-12.7),rotation('z',180))
    add('proof-saddle-M5-through','steel-fastener',(loadx,-10.325,H),Q,model=_bolt(5,25),notes='One M5x25 through two3.175 mm angle legs and6.35 mm lever; two0.8 mm washers and locking nut, no end-face bypass.')
    for y in(-19.05,12.7):add(f'proof-saddle-bridge-M5-{y}','steel-fastener',(loadx,y,H-2.375),rotation('x',180),model=_bolt(5,20),notes='Two M5x20 borrowed from powered-fork angle joints. Bridge-to-angle metal stack9.525 mm, washers/nut keep two threads.')
    add('proof-gauge-back','force-gauge-backing',(loadx,25.175,contact+80),rotation('x',90),notes='Rear plane22 mm behind gauge axis: case15 mm +7 mm metal spacers. Four allocated M4x25 finish to actual thread depth; no case contact with cap screws.')
    gm=box(64,30,130).translate((loadx,-T/2,contact+15)).union(cylinder(6,15).translate((loadx,-T/2,contact)))
    add('proof-gauge-envelope','steel-fastener',model=gm,notes='Gauge axis down, compression probe on the saddle at X140,Y-3.175. Rear-mounted case is loaded only through metal quill cap and its four M4 rear screws.')
    add('proof-quill-cap','proof-gauge-quill-cap',(loadx,31.525,contact+155))
    for x in(-28,28):add(f'proof-cap-M5-{x}','steel-fastener',(loadx+x,18.025,contact+128.2),Q,model=_bolt(5,25),notes='M5 heads face the case but retain at least 2.9 mm case clearance in the reference envelope; actual case and rear sockets require fit checking.')
    for x,z,_ in hole_grid(41,73,4.5):add(f'proof-gauge-rear-spacer-{x}-{z}','proof-gauge-rear-spacer',(loadx+x,contact*0+11.825,contact+80-z),Q)
    add('proof-noncontact-catch','drive-test-foot',(0,0,25),notes='Borrow metal test foot as an independent catch under shaft/hubs, and add a clear lever catch. Catch must not contact any loaded part during a reading.')
    add('proof-vise-reference','steel-fastener',model=box(60,80,30).translate((112.5,51,35)),notes='Envelope only: grip reaction plate free metal X95..130. Positively bolt purchased vise through its actual factory slots using two temporarily reused M8x75 bench anchors. Retain actual fastener grip before loading.')
    result['hub-clamp-proof']=(a,r)

    a,r,add=start('shaft-capture-proof')
    # Canonical completed 85 mm positive-pitch shaft; chosen free end is up.
    H=78.175;endz=200;axis=np.array([0,-H,endz]);S=rotation('x',180)
    U=rotation('x',90)
    def upright(n,part,p=(0,0,0),R=None,model=None,notes=''):
        p=np.array(p);R=np.eye(3) if R is None else R
        add(n,part,U@p+np.array([0,0,endz]),U@R,model=model,notes=notes)
    upright('capture-proof-column','4040-extrusion',(0,-endz,0),model=_member(500,'y'),notes='Reuse the 500 mm column vertically, braced independently with the two matched corner brackets and four M8 kit joints. Reference column front is Y=-40 mm.')
    add('capture-proof-shaft','gimbal-shaft-stock',axis,S,model=shaft_with_end_holes(85),notes='Actual completed 85 mm shaft, selected free end upward. Its real end washers and capture tubes remain installed. Hub clamps and bearing setscrews are loosened after the independent catch is secured; no gun is carried.')
    add('capture-proof-hub','shaft-hub',axis,S)
    for hz in(6,19):
        add(f'capture-clamp-M4-{hz}','steel-fastener',axis+np.array([-20.05,-16,-hz]),rotation('y',90),model=_bolt(4,50),notes='Retained clamp hardware, loose enough that it does not carry axial force during capture proof.')
        for x in(-20.05,19.05):add(f'capture-clamp-washer-{hz}-{x}','steel-fastener',axis+np.array([x,-16,-hz]),rotation('y',90),model=cylinder(9,1).cut(cylinder(4.5,3).translate((0,0,-1))))
        add(f'capture-clamp-nut-{hz}','steel-fastener',axis+np.array([20.05,-16,-hz]),rotation('y',90),model=cylinder(8,5).cut(cylinder(4,7).translate((0,0,-1))))
    add('capture-proof-output-plate','pitch-side',axis+np.array([-125,15,-25]),S,notes='Actual output plate remains connected to its real hub. The separate interface mounts on the nearer opposite face; no temporary vise pressure grips a hub or shaft.')
    upright('capture-proof-bearing-foot','pitch-bearing-foot',(0,-65,40))
    upright('capture-proof-KP001','kp12-bearing',(0,-65,59.175),rotation('z',90))
    for x in(-28,28):
        upright(f'capture-proof-riser-{x}','capture-bearing-riser',(x,-65,46.35))
        upright(f'capture-bearing-M6-{x}','steel-fastener',(x,-65,37.35),model=_bolt(6,40))
    for u in(-85,-45):upright(f'capture-foot-M8-{u}','steel-fastener',(0,u,47.85),rotation('x',180),model=_bolt(8,16))
    for i,(u,L) in enumerate(CAPTURE_STACKS['pitch-positive']):add(f'capture-proof-tube-{i+1}',capture_tube_name(L),axis+np.array([0,0,-u]),S)
    for side,u in(('near',0),('far',85)):
        W=S if side=='near' else np.eye(3);p=axis+np.array([0,0,-u])
        add(f'capture-proof-{side}-washer','shaft-end-retainer-washer',p-W@np.array([0,0,2]),W)
        add(f'capture-proof-{side}-flat','shaft-end-flat-washer',p-W@np.array([0,0,2.8]),W)
        add(f'capture-proof-{side}-M5','steel-fastener',p-W@np.array([0,0,2.8]),W,model=_bolt(5,12))
    add('capture-load-interface','shaft-capture-interface',axis)
    for x,y,_ in hole_grid(26,20):add(f'capture-interface-M5-{x}-{y}','steel-fastener',axis+np.array([x,y,-32.35]),model=_bolt(5,80),notes='Temporarily borrowed M5x80. Actual plate6.35, hub25 and interface6.35 form the metal stack. Keep all protruding ends clear of bridge, sensor and column.')
    bridgez=endz+T+75
    add('capture-closed-bridge','shaft-capture-bridge',(0,-H,bridgez))
    for x,y,_ in hole_grid(60,40,3.4):
        add(f'capture-bridge-spacer-{x}-{y}','capture-bridge-spacer',(x,-H+y,endz+T))
        add(f'capture-bridge-M3-{x}-{y}','steel-fastener',(x,-H+y,endz-.5),model=_bolt(3,100),notes='Borrow four M3x100 crash ties.75 +two6.35 plates +washers1 +nut4 =92.7 mm. Set 0.2 mm locating clearance; no capture preload. Reuse the crash tie 7 OD washers on the 3.4 mm plate holes; the 75 mm tubes remain between metal plates.')
    # M6 through-bolt and coupling give one positive interface for both signs.
    add('capture-gauge-interface-bolt','steel-fastener',(0,-H,bridgez-1),model=_bolt(6,16),notes='M6x16 plus one1 mm washer gives8.65 mm exterior thread beyond6.35 mm bridge. Hold bolt while seating steel coupling nut against the bridge; verify actual grade and grip.')
    couplingz=bridgez+T
    add('capture-gauge-coupling','gauge-M6-coupling',(0,-H,couplingz),notes='Bridge-end engagement8.65 mm nominal; gauge end7 mm reference, at least6 mm actual on each side.20 mm coupling leaves4.35 mm between ends. Verify M6x1 identity, no bottoming, alignment and witness. No hook or cord.')
    casebottom=couplingz+28
    gaugecenter=casebottom+65
    add('capture-gauge-back','installed-Z-gauge-back',(0,-49.825,gaugecenter),rotation('x',90),notes='Same70x160 backing with free guide slots. Two9.825 mm guide tubes align the case, shaft and M6 coupling coaxially. Guide screws retain laterally without clamping axial sliding or carrying proof force around the sensor.')
    add('capture-gauge-cap','proof-gauge-quill-cap',(0,-43.475,casebottom+140))
    gm=box(64,30,130).translate((0,-H,casebottom)).union(cylinder(6,15).translate((0,-H,casebottom-15)))
    add('capture-gauge-envelope','steel-fastener',model=gm,notes='500 N push/pull gauge. Compression: quill advances the body down toward bridge, jack withdrawn. Tension: quill withdrawn, manual M6 jack advances body upward away from bridge. Positive M6 coupling stays installed for both signs. Actual load-shaft length and engagement set the backing height; reference15 mm shaft has7 mm engaged.')
    for x,y,_ in hole_grid(41,73,4.5):
        add(f'capture-gauge-rear-spacer-{x}-{y}','proof-gauge-rear-spacer',(x,-56.175,gaugecenter+y),rotation('x',90))
        add(f'capture-gauge-rear-M4-{x}-{y}','steel-fastener',(x,-47.825,gaugecenter+y),rotation('x',90),model=_bolt(4,25),notes='Dedicated proof rear-screw set, finished for15.35 mm external grip and actual rear socket depth. Two12 OD washers per screw.')
    for z in(gaugecenter-72,gaugecenter+72):
        add(f'capture-gauge-guide-{z}','capture-gauge-guide-spacer',(0,-40,z),rotation('x',90))
        add(f'capture-gauge-guide-M6-{z}','steel-fastener',(0,-57.175,z),rotation('x',-90),model=_bolt(6,25),notes='M6x25 slot8 guide joint. Set measured sliding clearance under the washer and witness; never clamp the moving backing.')
    jackz=gaugecenter-140
    add('capture-manual-jack-angle','installed-Z-jack-angle',(0,-40,jackz),rotation('z',90))
    add('capture-manual-jack-screw','steel-fastener',(0,-53,gaugecenter-160),model=_bolt(6,80),notes='Fully threaded M6x80, tip under gauge-back lower edge at Y=-53. Lower working nut reacts into fixed metal foot; wrench provides rotation constraint only. Feed at most1/12 turn,0.0833 mm, to move body away from the bridge for tension. Quill remains clear.')
    # Two retained catch plates surround only the near-face interface edge.
    lower=endz-.75-T;upper=endz+T+.75
    add('capture-catch-lower','drive-test-foot',(-75,-H,lower),notes='Independent lower catch. Its right edgeX=-15 stays5 mm radially clear of20 mm keeper. Top is0.75 mm below the interface; no contact during a reading.')
    add('capture-catch-upper','capture-catch-upper',(-75,-H,upper),notes='Independent upper catch,0.75 mm above interface. Both catch plates are joined only at farX=-125 and positively held in the separately bench-anchored vise. No fixture contacts shaft, keeper, sensor or moving plate during proof.')
    for y in(-20,20):
        add(f'capture-catch-spacer-{y}','capture-catch-spacer',(-125,-H+y,endz-.75))
        add(f'capture-catch-M5-{y}','steel-fastener',(-125,-H+y,lower-.8),model=_bolt(5,35),notes='Borrow two roll-foot M5x35 joints.6.35 +7.85 +6.35 +washers1.6 +nut5 =27.15 mm;7.85 mm protrusion.')
    add('capture-vise-reference','steel-fastener',model=box(35,80,30).translate((-120,-H,lower-15)),notes='Envelope only. Grip joined catch far-end metalX=-135..-105; not the actual shaft/hub/output. Positively mount vise through factory slots with two temporarily reused M8x75 bench anchors. Set actual catch gaps so full500 N proof never touches them.')
    result['shaft-capture-proof']=(a,r)

    return result


def actuator_length(angle):
    a=math.radians(angle)
    return math.sqrt(L0*L0+2*L0*LEVER*math.sin(a)+2*LEVER*LEVER*(1-math.cos(a)))


def checks():
    # Sample every combinationat2°includinghardangles;compensationfromneutraltool.
    samples=[]
    for yaw in np.linspace(-HARD_ANGLE,HARD_ANGLE,23):
        for pitch in np.linspace(-22,12,18):
            for roll in np.linspace(-HARD_ANGLE,HARD_ANGLE,23):
                R=rotation('z',105+yaw)@rotation('y',60+pitch)@rotation('x',roll)
                samples.append(R0@TOOL-R@TOOL)
    xyz=np.array(samples)
    minimum_arm=min((actuator_length(a+.001)-actuator_length(a-.001))/math.radians(.002) for a in np.linspace(-22,22,441))
    # Beamsections:conservativehollow4040wall2mm,notasupplierstiffnessrating.
    I=(40**4-36**4)/12
    boom_length=180
    z_force=300
    E=69000
    beam_deflection=z_force*boom_length**3/(3*E*I)
    d=12
    moment=15000 # Nmm: conservative pitch shaft/hub screen; yaw/roll normal envelope10 Nm
    shear=16*moment/(math.pi*d**3)
    screw_root=5.5
    screw_I=math.pi*screw_root**4/64
    buckling=math.pi**2*200000*screw_I/400**2
    blocks_margin=200-(HARD_TRAVEL+BLOCK_SEPARATION/2+BLOCK_X/2)
    return {
        "status":"Geometry and conservative assumed-load arithmetic, not loaded accuracy, lifetime or physical acceptance.",
        "catalog_envelope_uncertainties":["Selected SBR12 base-to-deck40 mm and block28x26 M5 interface are bound to listing drawing; transfer actual railfoot holes.","Selected KP001 centerheight19 mm/71 mm body/56 mm boltcenters are catalog envelopes; verify matingparts without forcing bolts.","TR8nut flange22x3.5 mm/body10.2/length15/PCD16 mm are selectedlistinginterfaces; verify before finishing seats.","Switch roller travel and friction spring rate require physical grading."],
        "axis_names":["x","y","z","yaw","pitch","roll"],
        "linear_limits_mm":{"soft":[-85,85],"switch":[-89,89],"metal_stop":[-94,94]},
        "angular_limits_deg":{"soft":[-20,20],"soft_by_axis":{"yaw":[-20,20],"pitch":[-20,10],"roll":[-20,20]},"switch":[-21,21],"switch_by_axis":{"yaw":[-21,21],"pitch":[-21,11],"roll":[-21,21]},"metal_stop":[-22,22],"metal_stop_by_axis":{"yaw":[-22,22],"pitch":[-22,12],"roll":[-22,22]}},
        "angular_actuator":{"r_mm":LEVER,"L0_mm":L0,"soft_length_mm":[actuator_length(-20),actuator_length(20)],"hard_length_mm":[actuator_length(-22),actuator_length(22)],"minimum_effective_lever_mm":minimum_arm},
        "rail_block_end_margin_at_hard_stop_mm":blocks_margin,
        "XYZ_stop_stack_mm":{"carriage_half_length":105,"stationary_contact_face_from_bed_center":199,"metal_travel":94,"backing_leg_inner_face":205.35,"backing_leg_outer_face":211.7,"foot_bolt_local_X":[-171,171],"foot_bolt_local_Y":[-10,10],"minimum_X_frame_to_12mm_foot_washer_clearance":3,"switch_travel":89,"switch_to_metal_margin":5},
        "nominal_motion":{"lead_mm":LEAD,"ratio":RATIO,"full_step_um":LEAD/RATIO/200*1000,"sixteen_microstep_command_pulses_per_mm":RATIO*200*16/LEAD,"minimum_fullstep_tool_increment_um_at_200mm":LEAD/RATIO/200*200/LEVER*1000},
        "tool_proxy":{"v_mm":TOOL.tolist(),"reference_dot_mm":DOT.tolist(),"gimbal_center_mm":C0.tolist(),"orientation_deg":[105,60,0],"scope":"Gun proxy is unscanned; actual tool transform must be observed and calibrated. Nominal mechanical axes are Rz Ry Rx."},
        "dot_compensation_hard_angle_sample":{"poses":len(samples),"minimum_mm":xyz.min(axis=0).tolist(),"maximum_mm":xyz.max(axis=0).tolist(),"fits_soft_xyz":bool(np.abs(xyz).max()<TRAVEL),"sampling_deg":2,"scope":"Reach arithmetic; it does not establish body, camera, cable or tube clearance."},
        "load_scenario":{"assumed_maximum_Z_axial_force_N":z_force,"assumed_pitch_shaft_output_moment_Nm":15,"yaw_roll_normal_moment_Nm":10,"normal_pitch_actuator_force_N":100,"angular_force_at_minimum_effective_lever_N":moment/minimum_arm,"TR8_efficiency_assumption":.2,"screw_torque_Nm_at_300N":z_force*LEAD/1000/(2*math.pi*.2),"motor_torque_Nm_at_4to1_and_90pct_belt":z_force*LEAD/1000/(2*math.pi*.2*4*.9),"shaft_nominal_torsion_MPa":shear,"shaft_no_transverse_holes":True,"shaft_end_threads":"M5x0.8","shaft_end_section_conservative_bore_mm":5,"shaft_torsion_MPa_at_25Nm":16*25000/(math.pi*d**3),"shaft_torsion_MPa_at_32p5Nm_with_5mm_end_bore":16*32500*d/(math.pi*(d**4-5**4)),"nominal_304_yield_MPa_assumption":205,"nominal_304_shear_yield_MPa_assumption":205/math.sqrt(3),"hub_clamp_bolts_per_hub":2,"hub_high_pitch_path_proof_interval_Nm":[30,32.5],"hub_other_path_proof_interval_Nm":[25.2,27.5],"hub_capacity_scope":"No friction capacity follows from clamp bolt grade or CAD. Every hub must pass the measured two-sign proof and warm/cycled recheck before loaded use.","TR8_pinned_400mm_Euler_buckling_N":buckling,"buckling_factor_at_upward_compression_ceiling_350N":buckling/350,"conservative4040_180mm_cantilever_deflection_mm":beam_deflection,"scope":"Assumed loads and sections only. Supplier moment ratings, actual mass, cable forces, jam forces, preload, duty temperature and creep capacity are not established by this arithmetic."},
        "retention":{"metal_bounds":True,"gun_tether_required":True,"pose_retention_on_power_loss":"Spring-loaded friction washers on Z/pitch/roll. No accepted loaded result. Single243-locked nut each side:24h cure and witness marks.","breakaway_windows_Nm":{"z":[.20,.23],"pitch":[.06,.08],"roll":[.02,.04]},"loaded_tube_sweep":"Independent travel box contains vessel-collision poses. Dry commissioning removes the tube; loaded seam work is restricted to physically accepted correlated paths."},
        "force_links":{"spring_free_mm":20,"spring_nominal_k_N_per_mm":43,"spring_source":"B0B771L8G8","springs_per_axis":4,"seated_preload_N":{"yaw_roll":100,"pitch":130,"X_Y":250,"Z_up_negative_length":250,"Z_down_positive_length":400},"trip_displacement_mm":{"angular":.30,"XYZ":.75},"captured_displacement_mm":1.0,"nominal_trip_force_N":{"yaw_roll":125.8,"pitch":155.8,"X_Y_Z_up":314.5,"Z_down":464.5},"accept_trip_force_N":{"yaw_roll":[100,140],"pitch":[148,165],"X_Y_Z_up":[250,350],"Z_down":[440,500]},"powered_peak_ceiling_N":{"yaw_roll":140,"pitch":165,"X_Y_Z_up":350,"Z_down":500},"switch_required_overtravel_mm":{"angular":.8,"XYZ":.35},"switches_per_axis_loop":4,"scope":"Measure both directions and peak force with hardware loop active. Motor current is not a calibrated force limiter."},
        "manufacturing_clearances_mm":{"XYZ_cage_to_bed":1.0,"XYZ_cage_to_carriage":1.0,"XYZ_cage_to_rail_support":2.0,"spring_maximum_compression_at_capture_yaw_roll":100/(2*43)+1,"spring_maximum_compression_at_capture_pitch":130/(2*43)+1,"spring_maximum_compression_at_capture_X_Y_Z_up":250/(2*43)+1,"spring_maximum_compression_at_capture_Z_down":400/(2*43)+1},
        "drive_directions":{"x":"positiveX lengthens","y":"positiveY lengthens","z":"positiveZ shortens; fixed thrust atTOP","yaw":"positive angle lengthens","pitch":"positive angle lengthens","roll":"positive angle lengthens"},
        "work_subset_candidate":{"yaw_deg":[-5,5],"pitch_deg":[-10,10],"roll_deg":[-5,5],"endpoint_offset_each_axis_mm":[-.25,.25],"XYZ":"correlated inverse geometry keeps actual calibrated endpoint at the seam","acceptance":"Proxy clearance screening plus physical-gun/rotator/cable static sweep before motion; missing evidence limits approval."},
        "fiber":{"independent_boom":True,"minimum_active_radius_mm":350,"no_twist":True,"full_routing_sweep":"Preserve at least350 mm radius throughout the accepted working path. Boom dimensions alone do not qualify cable routing."},
    }


def _template_origin(data):
    x,y,_=data['blank_mm']
    outline=data.get('outline')
    if outline:
        cx=(min(p[0] for p in outline)+max(p[0] for p in outline))/2
        cy=(min(p[1] for p in outline)+max(p[1] for p in outline))/2
    else:cx=cy=0
    return cx-x/2,cy-y/2


def svg_template(name,data):
    x,y,t=data['blank_mm'];ox,oy=_template_origin(data);margin=20
    def at(px,py):return px-ox+margin,y-(py-oy)+margin
    e=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{x+40}mm" height="{y+60}mm" viewBox="0 0 {x+40} {y+60}">','<rect width="100%" height="100%" fill="white"/>',f'<rect x="20" y="20" width="{x}" height="{y}" fill="none" stroke="#999" stroke-width=".15"/>']
    outline=data.get('outline') or [[ox,oy],[ox+x,oy],[ox+x,oy+y],[ox,oy+y]]
    e.append('<polygon points="'+' '.join(f'{at(a,b)[0]},{at(a,b)[1]}' for a,b in outline)+'" fill="none" stroke="black" stroke-width=".25"/>')
    for hx,hy,hd in data.get('holes',[]):
        cx,cy=at(hx,hy);e.extend([f'<circle cx="{cx}" cy="{cy}" r="{hd/2}" fill="none" stroke="black" stroke-width=".2"/>',f'<path d="M{cx-2},{cy}h4 M{cx},{cy-2}v4" stroke="#b33" stroke-width=".15"/>'])
    for hx,hy,length,width,angle in data.get('slots',[]):
        cx,cy=at(hx,hy);e.append(f'<rect x="{cx-length/2}" y="{cy-width/2}" width="{length}" height="{width}" rx="{width/2}" fill="none" stroke="black" stroke-width=".2" transform="rotate({-angle},{cx},{cy})"/>')
    for bx,by,w,h in data.get('cutouts',[]):
        cx,cy=at(bx,by+h);e.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="{h}" fill="none" stroke="black" stroke-width=".25"/>')
    e.extend([f'<text x="20" y="{y+31}" font-family="sans-serif" font-size="4">{name}: {x} x {y} x {t} mm - 100% scale</text>',f'<path d="M20,{y+40}h50 M20,{y+37}v6 M70,{y+37}v6" stroke="black" stroke-width=".25"/>',f'<text x="80" y="{y+41}" font-family="sans-serif" font-size="3.5">50 mm scale check; +X right / +Y up</text>','</svg>'])
    return '\n'.join(e)


def write_dxf(path,data):
    import ezdxf
    doc=ezdxf.new('R2010');doc.units=4;m=doc.modelspace()
    x,y,_=data['blank_mm'];ox,oy=_template_origin(data)
    outline=data.get('outline') or [[ox,oy],[ox+x,oy],[ox+x,oy+y],[ox,oy+y]]
    m.add_lwpolyline(outline,close=True,dxfattribs={'layer':'CUT'})
    for hx,hy,hd in data.get('holes',[]):m.add_circle((hx,hy),hd/2,dxfattribs={'layer':'DRILL'})
    for bx,by,w,h in data.get('cutouts',[]):m.add_lwpolyline([(bx,by),(bx+w,by),(bx+w,by+h),(bx,by+h)],close=True,dxfattribs={'layer':'CUT'})
    for hx,hy,length,width,angle in data.get('slots',[]):
        a=math.radians(angle);u=np.array([math.cos(a),math.sin(a)]);v=np.array([-math.sin(a),math.cos(a)]);c=np.array([hx,hy]);left=c-u*(length-width)/2;right=c+u*(length-width)/2
        for sign in(-1,1):m.add_line(left+sign*width/2*v,right+sign*width/2*v,dxfattribs={'layer':'CUT'})
        m.add_arc(right,width/2,angle-90,angle+90,dxfattribs={'layer':'CUT'});m.add_arc(left,width/2,angle+90,angle+270,dxfattribs={'layer':'CUT'})
    doc.saveas(path)


def build():
    init_parts()
    for sub in ('stl','step','templates'):(HERE/sub).mkdir(exist_ok=True)
    allowed={n for n,d in PARTS.items() if d['kind'] in('print','metal')}
    for sub,suffix in(('step','.step'),('stl','.stl')):
        for old in(HERE/sub).glob('*'+suffix):
            if old.stem not in allowed:old.unlink()
    for old in(HERE/'step').glob('*.step.mesh'):
        if old.name.removesuffix('.step.mesh') not in allowed:old.unlink()
    template_names={n for n,d in PARTS.items() if d.get('template_type')=='plate'}|{'catalog-friction-washer','catalog-ball-backing-washer'}
    for old in(HERE/'templates').iterdir():
        if old.suffix in('.svg','.dxf') and not old.stem.startswith('stock-sheet-') and old.stem not in template_names:old.unlink()
    manifest=[]
    for name,d in PARTS.items():
        if d['kind'] not in ('print','metal'):continue
        model=d['model']
        if not model.val().isValid():raise RuntimeError(f"InvalidCAD:{name}")
        cq.exporters.export(model,str(HERE/'step'/f'{name}.step'))
        cq.exporters.export(model,str(HERE/'stl'/f'{name}.stl'),tolerance=.03,angularTolerance=.1)
        row={k:v for k,v in d.items() if k!='model'}
        row.update(name=name,step=f'step/{name}.step',stl=f'stl/{name}.stl')
        if d['kind']=='metal' and d['blank_mm'] and d.get('template_type')=='plate':
            (HERE/'templates'/f'{name}.svg').write_text(svg_template(name,d))
            write_dxf(HERE/'templates'/f'{name}.dxf',d)
            row.update(svg=f'templates/{name}.svg',dxf=f'templates/{name}.dxf')
        manifest.append(row)
    # A bought steel washer receives only guide-hole drilling, not a flat
    # aluminum fabrication substitution.
    fw={'blank_mm':[37,37,3],'outline':None,'holes':[[-15,0,3.4],[15,0,3.4]],'slots':[]}
    outer=[]
    for i in range(181):
        a=2*math.pi*i/180;outer.append([18.5*math.cos(a),18.5*math.sin(a)])
    fw['outline']=outer;fw['holes'].append([0,0,13])
    (HERE/'templates'/'catalog-friction-washer.svg').write_text(svg_template('Purchased steel washer37 OD /13 ID /3 thick',fw))
    write_dxf(HERE/'templates'/'catalog-friction-washer.dxf',fw)
    bw={'blank_mm':[25,25,2],'outline':[[12.5*math.cos(2*math.pi*i/180),12.5*math.sin(2*math.pi*i/180)] for i in range(181)],'holes':[[0,0,6],[-9,0,3.4],[9,0,3.4]],'slots':[]}
    (HERE/'templates'/'catalog-ball-backing-washer.svg').write_text(svg_template('Purchased ball backing washer25 OD /6 ID /2 thick',bw))
    write_dxf(HERE/'templates'/'catalog-ball-backing-washer.dxf',bw)
    assy,receipt=assembly()
    assy.save(str(HERE/'gun-positioner-assembly.step'))
    (HERE/'parts.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (HERE/'assembly.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (HERE/'geometry-check.json').write_text(json.dumps(checks(),indent=2)+'\n')
    hashes={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest() for folder in ('step','stl','templates') for p in sorted((HERE/folder).iterdir())}
    hashes['gun-positioner-assembly.step']=hashlib.sha256((HERE/'gun-positioner-assembly.step').read_bytes()).hexdigest()
    (HERE/'asset-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
    fixture_receipts={k:v[1] for k,v in fixture_assemblies().items()}
    (HERE/'fixture-assemblies.json').write_text(json.dumps(fixture_receipts,indent=2)+'\n')
    root=HERE.parents[3]
    source_paths=[Path(__file__),root/'tools/gun-positioner/requirements.py',root/'tools/gun-positioner/fasteners.py',root/'tools/gun-positioner/nest.py',root/'tools/gun-positioner/clearance.py',root/'tools/gun-positioner/profiles.py',root/'tools/gun-positioner/check_fabrication.py',root/'tools/gun-positioner-optics/mounts.py']
    source_hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    export_receipt={'status':'successful CAD/template export; no physical acceptance','units':'mm','sources_sha256':source_hashes,'assembly_STEP_sha256':hashes['gun-positioner-assembly.step'],'exported_fabrication_parts':len(manifest),'assembly_instances':len(receipt),'fixture_instances':{n:len(r) for n,r in fixture_receipts.items()},'asset_hash_index':'asset-hashes.json','clearance_receipt':'working-subset-clearance.json','scope':'Catalog envelopes and assumed load arithmetic are not load, fit, accuracy or lifetime acceptance.'}
    (HERE/'export-receipt.json').write_text(json.dumps(export_receipt,indent=2)+'\n')
    print(json.dumps({'parts':len(manifest),'instances':len(receipt),'geometry':checks()},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--checks',action='store_true')
    args=parser.parse_args()
    if args.checks: print(json.dumps(checks(),indent=2))
    else: build()
