"""Writes the wave-1 schematic sketches for the work-as-datum explorer.

Plain lines and labels; tube, lip, plate and port dimensions are the repo's,
the gun outline is the orientation scene's proxy at its opening pose
(pose_geometry.py), and every mechanism part is schematic.

Run:  python3 make_sketches.py
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pose_geometry import pose_point, GRIP_BASE  # noqa: E402

IN = 25.4
R_IN = 5 * IN / 2 - 0.065 * IN
R_OUT = 5 * IN / 2
RIM = 0.25 * IN
PLATE_R = 4.86 * IN / 2
PORT = 0.75 * IN
PORT_R = 0.438 * IN / 2
POSE = (45, 30, -15)

STYLE = """<style>
 text{font-family:Helvetica,Arial,sans-serif;font-size:11px;fill:#222}
 .t{font-size:13px;font-weight:bold}
 .s{font-size:9.5px;fill:#555}
 .metal{fill:#d9dde3;stroke:#333;stroke-width:1}
 .plate{fill:#b9c2cc;stroke:#333;stroke-width:1}
 .print{fill:#f3e3b5;stroke:#8a6d1f;stroke-width:1}
 .buy{fill:#cfe8d4;stroke:#2f6b3a;stroke-width:1}
 .gun{fill:none;stroke:#1f4e9a;stroke-width:1.6}
 .shell{fill:none;stroke:#1f4e9a;stroke-width:1;stroke-dasharray:5 3}
 .beam{stroke:#d22;stroke-width:1.6}
 .wire{stroke:#666;stroke-width:1.2}
 .cable{fill:none;stroke:#7a3fa0;stroke-width:2.2}
 .rope{stroke:#444;stroke-width:1;stroke-dasharray:2 2}
 .dim{stroke:#999;stroke-width:0.8;stroke-dasharray:3 3;fill:none}
 .arrow{stroke:#c05a00;stroke-width:1.4;fill:none;marker-end:url(#ah)}
 .room{fill:#eee;stroke:#777;stroke-width:1}
</style>
<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
<path d="M0,0 L8,4 L0,8 z" fill="#c05a00"/></marker></defs>"""


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">\n<rect width="{w}" height="{h}" fill="#fcfcfa"/>\n'
            f'{STYLE}\n{body}\n</svg>\n')


def P(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def gp(p):
    return pose_point(p, *POSE)


# ---------------------------------------------------------------- compass
def compass():
    o = []
    # ---- elevation (section in the XZ plane through the dot) ----
    ox, oy, s = 250, 520, 1.35
    X = lambda x: ox + s * x
    Z = lambda z: oy - s * z
    o.append(f'<text class="t" x="20" y="24">A. Endcap compass — elevation, section through the dot (XZ plane)</text>')
    o.append(f'<text class="s" x="20" y="40">tube, lip, plate, ports: repo dimensions. Gun: scene proxy at grip 45 / hole 30 / vertical -15. Mechanism parts schematic.</text>')
    # rotator base hint
    o.append(f'<rect class="room" x="{X(-150):.1f}" y="{Z(-60):.1f}" width="{s*300:.1f}" height="14"/>')
    o.append(f'<text class="s" x="{X(-148):.1f}" y="{Z(-60)+11:.1f}">rotator turntable/base (below, not to scale) — tube turns here</text>')
    # tube walls
    for sgn in (-1, 1):
        x0, x1 = sorted((sgn * R_IN, sgn * R_OUT))
        o.append(f'<rect class="metal" x="{X(x0):.1f}" y="{Z(RIM):.1f}" width="{s*(x1-x0):.1f}" height="{s*(RIM+50):.1f}"/>')
    # plate with port holes
    o.append(f'<rect class="plate" x="{X(-PLATE_R):.1f}" y="{Z(0):.1f}" width="{s*2*PLATE_R:.1f}" height="{s*RIM:.1f}"/>')
    for px in (-PORT, PORT):
        o.append(f'<rect x="{X(px-PORT_R):.1f}" y="{Z(0):.1f}" width="{s*2*PORT_R:.1f}" height="{s*RIM:.1f}" fill="#fcfcfa" stroke="#333" stroke-width="0.8"/>')
        # hex nipple: hex 0..7, pin 7..25
        o.append(f'<rect class="buy" x="{X(px-8.2):.1f}" y="{Z(7):.1f}" width="{s*16.4:.1f}" height="{s*7:.1f}"/>')
        o.append(f'<rect class="buy" x="{X(px-6.85):.1f}" y="{Z(26):.1f}" width="{s*13.7:.1f}" height="{s*19:.1f}"/>')
        o.append(f'<rect x="{X(px-4.5):.1f}" y="{Z(26):.1f}" width="{s*9:.1f}" height="{s*26:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="2 2"/>')
    # seat bar 17..24
    o.append(f'<rect class="print" x="{X(-30):.1f}" y="{Z(24):.1f}" width="{s*60:.1f}" height="{s*7:.1f}"/>')
    # centre pin 24..44
    o.append(f'<rect class="metal" x="{X(-4):.1f}" y="{Z(44):.1f}" width="{s*8:.1f}" height="{s*20:.1f}"/>')
    # frame ring 32..44 with bushing
    o.append(f'<rect class="print" x="{X(-46):.1f}" y="{Z(46):.1f}" width="{s*92:.1f}" height="{s*12:.1f}"/>')
    o.append(f'<rect class="buy" x="{X(-7):.1f}" y="{Z(47):.1f}" width="{s*14:.1f}" height="{s*14:.1f}"/>')
    # ball transfer at 180 deg (x=-35) in section, others ghosted
    o.append(f'<rect class="buy" x="{X(-47.4):.1f}" y="{Z(34):.1f}" width="{s*16:.1f}" height="{s*26:.1f}"/>')
    o.append(f'<circle class="metal" cx="{X(-39.4):.1f}" cy="{Z(8):.1f}" r="{s*8:.1f}"/>')
    o.append(f'<rect x="{X(17.7):.1f}" y="{Z(34):.1f}" width="{s*16:.1f}" height="{s*26:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="3 2"/>')
    # gun (projected on XZ)
    pts = {k: gp(v) for k, v in {
        'noz': (0, 0, 0), 'b60': (0, 0, 60), 'b120': (0, 0, 120),
        'bft': (17, 0, 150), 'bfb': (-17, 0, 150), 'bbt': (17, 0, 237), 'bbb': (-17, 0, 237),
        'bbot': (0, -45, 237), 'grip': GRIP_BASE, 'wb': (0, -20, 110), 'dot': (0, 0, -16)}.items()}
    xz = lambda k: (X(pts[k][0]), Z(pts[k][2]))
    # barrel as thick line of ~24 mm
    nx, nz = pts['noz'][0], pts['noz'][2]
    bx, bz = gp((0, 0, 150))[0], gp((0, 0, 150))[2]
    o.append(f'<line x1="{X(nx):.1f}" y1="{Z(nz):.1f}" x2="{X(bx):.1f}" y2="{Z(bz):.1f}" stroke="#1f4e9a" stroke-width="{s*20:.1f}" stroke-opacity="0.18"/>')
    o.append(f'<line class="gun" x1="{X(nx):.1f}" y1="{Z(nz):.1f}" x2="{X(bx):.1f}" y2="{Z(bz):.1f}"/>')
    body = [xz('bft'), xz('bbt'), xz('bbb'), xz('bfb')]
    o.append(f'<polygon class="gun" points="{P(body)}" fill="#1f4e9a" fill-opacity="0.08"/>')
    o.append(f'<polyline class="gun" points="{P([xz("bbot"), xz("grip")])}"/>')
    o.append(f'<circle cx="{xz("grip")[0]:.1f}" cy="{xz("grip")[1]:.1f}" r="4" fill="#7a3fa0"/>')
    o.append(f'<text x="20" y="{xz("bbb")[1]-30:.1f}">gun (projected on XZ);</text>')
    o.append(f'<text x="20" y="{xz("bbb")[1]-17:.1f}" class="s">its body climbs away toward -Y (see plan)</text>')
    o.append(f'<text x="{xz("grip")[0]+10:.1f}" y="{xz("grip")[1]+18:.1f}">grip base / cable exit (toward -Y)</text>')
    # shell (dashed) around barrel + body
    o.append(f'<polygon class="shell" points="{P([(X(nx)+10, Z(nz)-18), xz("bft"), xz("bbt"), xz("bbb"), (X(bx)-22, Z(bz)+10), (X(nx)-8, Z(nz)-26)])}"/>')
    o.append(f'<text x="{X(nx)+14:.1f}" y="{Z(nz)-44:.1f}" fill="#1f4e9a">printed shell</text>')
    # beam + wire
    o.append(f'<line class="beam" x1="{X(nx):.1f}" y1="{Z(nz):.1f}" x2="{X(R_IN):.1f}" y2="{Z(0):.1f}"/>')
    o.append(f'<line class="wire" x1="{xz("wb")[0]:.1f}" y1="{xz("wb")[1]:.1f}" x2="{X(R_IN):.1f}" y2="{Z(0):.1f}"/>')
    o.append(f'<circle cx="{X(R_IN):.1f}" cy="{Z(0):.1f}" r="3" fill="#d22"/>')
    o.append(f'<text x="{X(R_IN)+8:.1f}" y="{Z(0)+16:.1f}" fill="#d22">dot in the corner (r 61.85, 6.35 below rim)</text>')
    o.append(f'<text x="{xz("wb")[0]+6:.1f}" y="{xz("wb")[1]+14:.1f}" class="s">wire bracket</text>')
    # compass leg from ring to shell belly
    leg = [(X(34), Z(46)), (X(40), Z(62)), (X(44), Z(70))]
    o.append(f'<polyline points="{P(leg)}" fill="none" stroke="#8a6d1f" stroke-width="7" stroke-linecap="round"/>')
    o.append(f'<text x="{X(64):.1f}" y="{Z(70):.1f}">compass leg / pose block</text>')
    o.append(f'<text x="{X(64):.1f}" y="{Z(70)+12:.1f}" class="s">(radial + height fine screws;</text>')
    o.append(f'<text x="{X(64):.1f}" y="{Z(70)+23:.1f}" class="s">angles by printed block or arcs about the dot)</text>')
    # fork arm to post
    o.append(f'<polyline points="{P([(X(-46), Z(40)), (X(-118), Z(40)), (X(-118), Z(24))])}" fill="none" stroke="#8a6d1f" stroke-width="5"/>')
    o.append(f'<rect class="room" x="{X(-126):.1f}" y="{Z(30):.1f}" width="{s*16:.1f}" height="{s*90:.1f}"/>')
    o.append(f'<rect x="{X(-120):.1f}" y="{Z(30):.1f}" width="{s*4:.1f}" height="{s*22:.1f}" fill="#fcfcfa" stroke="#777"/>')
    o.append(f'<text x="{X(-178):.1f}" y="{Z(66):.1f}">fork arm: pin in a</text>')
    o.append(f'<text x="{X(-178):.1f}" y="{Z(66)+12:.1f}">vertical slot on a post</text>')
    o.append(f'<text x="{X(-178):.1f}" y="{Z(66)+24:.1f}">from the rotator base</text>')
    o.append(f'<text x="{X(-178):.1f}" y="{Z(66)+36:.1f}" class="s">(azimuth only)</text>')
    # camera on ring far side
    cx, cz = -40, 70
    o.append(f'<rect x="{X(cx)-9:.1f}" y="{Z(cz)-7:.1f}" width="18" height="14" fill="#555"/>')
    o.append(f'<line x1="{X(cx):.1f}" y1="{Z(cz):.1f}" x2="{X(R_IN):.1f}" y2="{Z(0):.1f}" class="dim"/>')
    o.append(f'<line x1="{X(cx):.1f}" y1="{Z(cz)+7:.1f}" x2="{X(-40):.1f}" y2="{Z(46):.1f}" stroke="#555" stroke-width="3"/>')
    o.append(f'<text x="{X(-110):.1f}" y="{Z(96):.1f}">camera on the ring,</text>')
    o.append(f'<text x="{X(-110):.1f}" y="{Z(96)+12:.1f}">sees dot vs corner</text>')
    # balancer
    o.append(f'<rect class="room" x="{X(-10):.1f}" y="{Z(330):.1f}" width="{s*30:.1f}" height="22"/>')
    o.append(f'<text x="{X(-14):.1f}" y="{Z(330)+10:.1f}" text-anchor="end">spring balancer (room)</text>')
    o.append(f'<text x="{X(-14):.1f}" y="{Z(330)+22:.1f}" text-anchor="end" class="s">carries all but 10–20 N</text>')
    o.append(f'<line class="rope" x1="{X(5):.1f}" y1="{Z(330)+22:.1f}" x2="{X(5):.1f}" y2="{Z(250):.1f}"/>')
    # cable loop to strain relief
    gx, gy = xz('grip')
    o.append(f'<path class="cable" d="M{gx:.1f},{gy:.1f} C{gx+120:.1f},{gy+10:.1f} {gx+150:.1f},{Z(322):.1f} {X(190):.1f},{Z(322):.1f}"/>')
    o.append(f'<rect class="room" x="{X(190):.1f}" y="{Z(330):.1f}" width="{s*40:.1f}" height="22"/>')
    o.append(f'<text x="{X(190)+60:.1f}" y="{Z(330)+10:.1f}">strain relief to the room</text>')
    o.append(f'<text x="{X(190)+60:.1f}" y="{Z(330)+22:.1f}" class="s">soft loop, R ≥ 350 mm while emitting</text>')
    o.append(f'<text x="{X(190)+60:.1f}" y="{Z(330)+34:.1f}" fill="#7a3fa0">umbilical + wire conduit</text>')
    # labels on hub
    o.append(f'<text x="{X(-150):.1f}" y="{Z(-18):.1f}">plate outer face = fillet base (height, tilt datum)</text>')
    o.append(f'<line class="dim" x1="{X(-55):.1f}" y1="{Z(-14):.1f}" x2="{X(-35):.1f}" y2="{Z(0):.1f}"/>')
    o.append(f'<text x="{X(-10):.1f}" y="{Z(-26):.1f}" fill="#2f6b3a">316 hex nipples in the tapped ports (hollow: purge vents)</text>')
    o.append(f'<line class="dim" x1="{X(17):.1f}" y1="{Z(-18):.1f}" x2="{X(19):.1f}" y2="{Z(3):.1f}"/>')
    o.append(f'<text x="{X(-150):.1f}" y="{Z(-36):.1f}">seat bar turns with the plate; centre pin at the port-pair midpoint; frame ring on a bushing;</text>')
    o.append(f'<text x="{X(-150):.1f}" y="{Z(-36)+13:.1f}">three stainless ball transfers roll on the plate face at r 40 (one in section, one ghosted)</text>')
    o.append(f'<text x="{X(-150):.1f}" y="{Z(RIM)+4:.1f}" class="s">rim</text>')

    # ---- plan ----
    px0, py0, q = 790, 330, 1.45
    PX = lambda x: px0 + q * x
    PY = lambda y: py0 - q * y
    o.append(f'<text class="t" x="{PX(-100):.1f}" y="{PY(135):.1f}">Plan (looking down), same instant</text>')
    o.append(f'<circle cx="{PX(0)}" cy="{PY(0)}" r="{q*R_OUT:.1f}" fill="none" stroke="#333"/>')
    o.append(f'<circle cx="{PX(0)}" cy="{PY(0)}" r="{q*R_IN:.1f}" fill="#b9c2cc" fill-opacity="0.35" stroke="#333"/>')
    for x in (-PORT, PORT):
        o.append(f'<circle class="buy" cx="{PX(x):.1f}" cy="{PY(0):.1f}" r="{q*8.2:.1f}"/>')
        o.append(f'<circle cx="{PX(x):.1f}" cy="{PY(0):.1f}" r="{q*4.5:.1f}" fill="#fcfcfa" stroke="#2f6b3a"/>')
    o.append(f'<rect class="print" x="{PX(-30):.1f}" y="{PY(7):.1f}" width="{q*60:.1f}" height="{q*14:.1f}" fill-opacity="0.8"/>')
    a1, a2 = math.radians(-5), math.radians(-75)
    p1 = (PX(46 * math.cos(a1)), PY(46 * math.sin(a1)))
    p2 = (PX(46 * math.cos(a2)), PY(46 * math.sin(a2)))
    o.append(f'<path d="M{p1[0]:.1f},{p1[1]:.1f} A{q*46:.1f},{q*46:.1f} 0 1 0 {p2[0]:.1f},{p2[1]:.1f}" fill="none" stroke="#8a6d1f" stroke-width="5" stroke-opacity="0.6"/>')
    leg0 = (PX(46 * math.cos(math.radians(-80))), PY(46 * math.sin(math.radians(-80))))
    o.append(f'<line x1="{leg0[0]:.1f}" y1="{leg0[1]:.1f}" x2="{PX(27):.1f}" y2="{PY(-41):.1f}" stroke="#8a6d1f" stroke-width="5"/>')
    o.append(f'<text x="{PX(-100):.1f}" y="{PY(-95):.1f}" class="s">C-ring open over the barrel\'s descent (-5° to -75°);</text>')
    o.append(f'<text x="{PX(-100):.1f}" y="{PY(-95)+11:.1f}" class="s">compass leg from its end up to the shell</text>')
    for a in (50, 170, 280):
        bx, by = 40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a))
        o.append(f'<circle class="buy" cx="{PX(bx):.1f}" cy="{PY(by):.1f}" r="{q*8:.1f}"/>')
    tri = [(40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a))) for a in (50, 170, 280)]
    o.append(f'<polygon points="{P([(PX(x), PY(y)) for x, y in tri])}" fill="none" stroke="#2f6b3a" stroke-dasharray="2 2"/>')
    o.append(f'<circle cx="{PX(0)}" cy="{PY(0)}" r="3" fill="#333"/>')
    # dot, tangent
    o.append(f'<circle cx="{PX(R_IN):.1f}" cy="{PY(0):.1f}" r="3.5" fill="#d22"/>')
    o.append(f'<line class="dim" x1="{PX(R_IN):.1f}" y1="{PY(-90):.1f}" x2="{PX(R_IN):.1f}" y2="{PY(60):.1f}"/>')
    o.append(f'<text x="{PX(R_IN)+6:.1f}" y="{PY(60):.1f}" class="s">tangent (±Y)</text>')
    # gun footprint
    pl = lambda k: (PX(pts[k][0]), PY(pts[k][1]))
    o.append(f'<polyline class="gun" points="{P([pl("noz"), pl("b60"), pl("b120")])}"/>')
    o.append(f'<polygon class="gun" points="{P([pl("bft"), pl("bbt"), pl("bbb"), pl("bfb")])}" fill="#1f4e9a" fill-opacity="0.08"/>')
    o.append(f'<polyline class="gun" points="{P([pl("bbot"), pl("grip")])}"/>')
    o.append(f'<circle cx="{pl("grip")[0]:.1f}" cy="{pl("grip")[1]:.1f}" r="4" fill="#7a3fa0"/>')
    o.append(f'<text x="{pl("grip")[0]+8:.1f}" y="{pl("grip")[1]+4:.1f}">grip base</text>')
    o.append(f'<line class="wire" x1="{pl("wb")[0]:.1f}" y1="{pl("wb")[1]:.1f}" x2="{PX(R_IN):.1f}" y2="{PY(0):.1f}"/>')
    # fork arm and slot
    o.append(f'<line x1="{PX(-46):.1f}" y1="{PY(0):.1f}" x2="{PX(-118):.1f}" y2="{PY(0):.1f}" stroke="#8a6d1f" stroke-width="5"/>')
    o.append(f'<rect class="room" x="{PX(-130):.1f}" y="{PY(8):.1f}" width="{q*24:.1f}" height="{q*16:.1f}"/>')
    o.append(f'<rect x="{PX(-126):.1f}" y="{PY(2.5):.1f}" width="{q*16:.1f}" height="{q*5:.1f}" fill="#fcfcfa" stroke="#777"/>')
    o.append(f'<text x="{PX(-135):.1f}" y="{PY(-16):.1f}" class="s">fork slot: long radially,</text>')
    o.append(f'<text x="{PX(-135):.1f}" y="{PY(-16)+11:.1f}" class="s">narrow tangentially</text>')
    # rotation arrow
    o.append(f'<path class="arrow" d="M{PX(52):.1f},{PY(-52):.1f} A{q*74:.1f},{q*74:.1f} 0 0 1 {PX(74):.1f},{PY(-4):.1f}"/>')
    o.append(f'<text x="{PX(78):.1f}" y="{PY(-40):.1f}" fill="#c05a00">plate + seat turn;</text>')
    o.append(f'<text x="{PX(78):.1f}" y="{PY(-40)+12:.1f}" fill="#c05a00">frame stays</text>')
    o.append(f'<text x="{PX(-100):.1f}" y="{PY(-78):.1f}" class="s">balls at 50°, 170°, 280° from the dot, r 40:</text>')
    o.append(f'<text x="{PX(-100):.1f}" y="{PY(-78)+11:.1f}" class="s">residual load must fall inside the triangle</text>')

    # ---- what is fixed to what ----
    y = 690
    rows = [
        ("height + tilt (3)", "plate outer face", "3 stainless ball transfers rolling"),
        ("radial x, y (2)", "plate centre = port-pair midpoint", "hex nipples → seat bar → pin → bushing"),
        ("azimuth (1)", "rotator base (loosely)", "fork pin in slot — the freedom that does not matter"),
        ("weight", "room", "spring balancer; 10–20 N left on the balls"),
        ("cable / wire / trigger forces", "room, or closed inside the shell", "strain relief + soft loop; Bowden or solenoid trigger"),
    ]
    o.append(f'<text class="t" x="20" y="{y}">What "fixed" is fixed to</text>')
    for i, (a, b, c) in enumerate(rows):
        yy = y + 18 + i * 16
        o.append(f'<text x="30" y="{yy}">{a}</text><text x="230" y="{yy}">{b}</text><text x="470" y="{yy}">{c}</text>')
    return svg(1040, 790, "\n".join(o))


# ---------------------------------------------------------- between centres
def centres():
    o = []
    ox, oy, s = 330, 450, 0.85
    X = lambda x: ox + s * x
    Z = lambda z: oy - s * z
    o.append('<text class="t" x="20" y="24">B. Between centres — elevation (XZ section through the dot), schematic</text>')
    o.append('<text class="s" x="20" y="40">rotator and mast on one sub-plate; tailstock live centre forces the plate centre onto a fixed line; gun rigid on the mast.</text>')
    bench = -232.0
    sub = bench + 12
    # bench + sub-plate
    o.append(f'<rect class="room" x="{X(-230):.1f}" y="{Z(bench):.1f}" width="{s*480:.1f}" height="16"/>')
    o.append(f'<text x="{X(-228):.1f}" y="{Z(bench)+12:.1f}" class="s">bench (only holds the sub-plate up)</text>')
    o.append(f'<rect class="metal" x="{X(-200):.1f}" y="{Z(sub):.1f}" width="{s*400:.1f}" height="{s*12:.1f}"/>')
    o.append(f'<text x="{X(160):.1f}" y="{Z(sub)+2:.1f}">steel / aluminium sub-plate (the datum)</text>')
    # rotator schematic
    base_top = sub + 36
    o.append(f'<rect class="print" x="{X(-150):.1f}" y="{Z(base_top):.1f}" width="{s*300:.1f}" height="{s*36:.1f}"/>')
    o.append(f'<text x="{X(-146):.1f}" y="{Z(base_top)+16:.1f}" class="s">rotator base (PET-GF, bolted through its 4 clamp holes), ball race, turntable</text>')
    nest_top = -152.4 + 6.35
    o.append(f'<rect class="print" x="{X(-75):.1f}" y="{Z(nest_top):.1f}" width="{s*150:.1f}" height="{s*(nest_top-base_top):.1f}"/>')
    o.append(f'<text x="{X(-70):.1f}" y="{Z(nest_top)+14:.1f}" class="s">nest (lower centre: ID pilot + OD guide)</text>')
    for sgn in (-1, 1):
        x0, x1 = sorted((sgn * R_IN, sgn * R_OUT))
        o.append(f'<rect class="metal" x="{X(x0):.1f}" y="{Z(RIM):.1f}" width="{s*(x1-x0):.1f}" height="{s*(RIM-nest_top):.1f}"/>')
    o.append(f'<rect class="plate" x="{X(-PLATE_R):.1f}" y="{Z(0):.1f}" width="{s*2*PLATE_R:.1f}" height="{s*RIM:.1f}"/>')
    for px in (-PORT, PORT):
        o.append(f'<rect class="buy" x="{X(px-6.85):.1f}" y="{Z(25):.1f}" width="{s*13.7:.1f}" height="{s*25:.1f}"/>')
    o.append(f'<rect class="print" x="{X(-30):.1f}" y="{Z(24):.1f}" width="{s*60:.1f}" height="{s*7:.1f}"/>')
    # live centre point down, quill
    o.append(f'<polygon class="buy" points="{P([(X(0), Z(24)), (X(-8), Z(38)), (X(-20), Z(40)), (X(-20), Z(75)), (X(20), Z(75)), (X(20), Z(40)), (X(8), Z(38))])}"/>')
    o.append(f'<rect class="metal" x="{X(-8):.1f}" y="{Z(125):.1f}" width="{s*16:.1f}" height="{s*50:.1f}"/>')
    o.append(f'<text x="{X(-120):.1f}" y="{Z(56):.1f}">live centre (MT2)</text>')
    o.append(f'<text x="{X(-120):.1f}" y="{Z(56)+12:.1f}" class="s">spring quill, 30–50 N down</text>')
    # C-arm from mast
    mx = -175
    o.append(f'<rect class="metal" x="{X(mx-15):.1f}" y="{Z(430):.1f}" width="{s*30:.1f}" height="{s*(430-sub):.1f}"/>')
    o.append(f'<text x="{X(mx-40):.1f}" y="{Z(440):.1f}">mast (steel or 4040)</text>')
    carm = [(X(mx + 15), Z(150)), (X(-60), Z(150)), (X(-60), Z(125)), (X(-8), Z(125))]
    o.append(f'<polyline points="{P(carm)}" fill="none" stroke="#555" stroke-width="7"/>')
    o.append(f'<text x="20" y="{Z(175):.1f}">tailstock C-arm</text>')
    o.append(f'<text x="20" y="{Z(175)+12:.1f}" class="s">enters over the far rim; rises</text>')
    o.append(f'<text x="20" y="{Z(175)+23:.1f}" class="s">on the side away from the grip</text>')
    o.append(f'<line class="dim" x1="{X(0):.1f}" y1="{Z(nest_top-8):.1f}" x2="{X(0):.1f}" y2="{Z(135):.1f}"/>')
    o.append(f'<text x="{X(4):.1f}" y="{Z(-100):.1f}" class="s">spin axis = line from nest centre to live-centre point</text>')
    # gun on Z slide from mast
    pts = {k: gp(v) for k, v in {'noz': (0, 0, 0), 'b150': (0, 0, 150), 'bft': (17, 0, 150),
                                   'bfb': (-17, 0, 150), 'bbt': (17, 0, 237), 'bbb': (-17, 0, 237),
                                   'bbot': (0, -45, 237), 'grip': GRIP_BASE}.items()}
    xz = lambda k: (X(pts[k][0]), Z(pts[k][2]))
    o.append(f'<line class="gun" x1="{xz("noz")[0]:.1f}" y1="{xz("noz")[1]:.1f}" x2="{xz("b150")[0]:.1f}" y2="{xz("b150")[1]:.1f}" stroke-width="3"/>')
    o.append(f'<polygon class="gun" points="{P([xz("bft"), xz("bbt"), xz("bbb"), xz("bfb")])}" fill="#1f4e9a" fill-opacity="0.08"/>')
    o.append(f'<polyline class="gun" points="{P([xz("bbot"), xz("grip")])}"/>')
    o.append(f'<line class="beam" x1="{xz("noz")[0]:.1f}" y1="{xz("noz")[1]:.1f}" x2="{X(R_IN):.1f}" y2="{Z(0):.1f}"/>')
    o.append(f'<circle cx="{X(R_IN):.1f}" cy="{Z(0):.1f}" r="3" fill="#d22"/>')
    # Z slide on mast + arm over to shell top
    o.append(f'<rect class="buy" x="{X(mx+15):.1f}" y="{Z(400):.1f}" width="{s*12:.1f}" height="{s*120:.1f}"/>')
    o.append(f'<text x="{X(mx+30):.1f}" y="{Z(405):.1f}">Z-slide (MGN12): B1 locked to the quill reading,</text>')
    o.append(f'<text x="{X(mx+30):.1f}" y="{Z(405)+12:.1f}" class="s">B2 free on a two-ball rocker riding the plate face</text>')
    arm = [(X(mx + 27), Z(330)), (X(-20), Z(330)), (X(0), Z(262))]
    o.append(f'<polyline points="{P(arm)}" fill="none" stroke="#8a6d1f" stroke-width="7"/>')
    o.append(f'<text x="{X(-10):.1f}" y="{Z(340):.1f}">rigid arm + pose adjustments to the shell</text>')
    # cable strain relief on mast top
    gx, gy = xz('grip')
    o.append(f'<path class="cable" d="M{gx:.1f},{gy:.1f} C{gx+60:.1f},{gy-80:.1f} {X(-60):.1f},{Z(470):.1f} {X(mx):.1f},{Z(432):.1f}"/>')
    o.append(f'<text x="{X(150):.1f}" y="{Z(440):.1f}" fill="#7a3fa0">cables relieved to the mast top —</text>')
    o.append(f'<text x="{X(150):.1f}" y="{Z(440)+13:.1f}" fill="#7a3fa0">the gun never moves in a session</text>')
    # B2 rocker ghost
    o.append(f'<rect x="{X(25):.1f}" y="{Z(22):.1f}" width="{s*26:.1f}" height="{s*8:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="3 2"/>')
    o.append(f'<text x="{X(70):.1f}" y="{Z(-40):.1f}" class="s">B2 rocker: two balls on the plate face at r 42, ±35° off the dot (ghosted)</text>')
    o.append(f'<text x="{X(R_IN)+8:.1f}" y="{Z(0)+14:.1f}" fill="#d22">dot</text>')
    return svg(900, 700, "\n".join(o))


# ---------------------------------------------------------- collar
def collar():
    o = []
    ox, oy, s = -30, 332, 4.5
    X = lambda x: ox + s * x
    Z = lambda z: oy - s * z
    o.append('<text class="t" x="20" y="24">C. Riding the tube — C0 rollers on the lip; C1 collar track (elevation near the weld azimuth, schematic)</text>')
    # wall at +X
    o.append(f'<rect class="metal" x="{X(R_IN):.1f}" y="{Z(RIM):.1f}" width="{s*(R_OUT-R_IN):.1f}" height="{s*(RIM+45):.1f}"/>')
    o.append(f'<rect class="plate" x="{X(20):.1f}" y="{Z(0):.1f}" width="{s*(PLATE_R-20):.1f}" height="{s*RIM:.1f}"/>')
    o.append(f'<circle cx="{X(R_IN):.1f}" cy="{Z(0):.1f}" r="3" fill="#d22"/>')
    o.append(f'<text x="{X(R_IN)-10:.1f}" y="{Z(0)-6:.1f}" fill="#d22" text-anchor="end">corner (fillet) — dot</text>')
    o.append(f'<text x="{X(24):.1f}" y="{Z(-3.2)+4:.1f}" class="s">end plate (recessed 6.35)</text>')
    # C0 rollers (ghost, arriving side ~25 deg ahead, drawn in the same section for clarity)
    o.append(f'<circle cx="{X((R_IN+R_OUT)/2):.1f}" cy="{Z(RIM+3):.1f}" r="{s*3:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="2 2"/>')
    o.append(f'<circle cx="{X(R_IN-3):.1f}" cy="{Z(RIM-1.2):.1f}" r="{s*3:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="2 2"/>')
    o.append(f'<circle cx="{X(R_OUT+3):.1f}" cy="{Z(RIM-1.2):.1f}" r="{s*3:.1f}" fill="none" stroke="#2f6b3a" stroke-dasharray="2 2"/>')
    o.append(f'<text x="{X(R_OUT+45):.1f}" y="{Z(RIM+8):.1f}" fill="#2f6b3a">C0 (dashed): rim roller + lip pinch pair</text>')
    o.append(f'<text x="{X(R_OUT+45):.1f}" y="{Z(RIM+8)+12:.1f}" class="s">25° ahead of the puddle, top 2 mm of the lip;</text>')
    o.append(f'<text x="{X(R_OUT+45):.1f}" y="{Z(RIM+8)+24:.1f}" class="s">the lip moves ~30 µm per N if pushed, so pinch, do not push</text>')
    # C1 collar below plate
    ztop, zbot = -12, -30
    o.append(f'<rect class="metal" x="{X(R_OUT):.1f}" y="{Z(ztop):.1f}" width="{s*22:.1f}" height="{s*(ztop-zbot):.1f}" fill="#e7d9c4"/>')
    o.append(f'<rect x="{X(R_OUT)-1:.1f}" y="{Z(ztop+2):.1f}" width="3" height="{s*(ztop-zbot+4):.1f}" fill="#555"/>')
    o.append(f'<text x="{X(R_OUT+45):.1f}" y="{Z(ztop)+10:.1f}">C1 collar (two halves + 5 in exhaust band clamp)</text>')
    o.append(f'<text x="{X(R_OUT+45):.1f}" y="{Z(ztop)+22:.1f}" class="s">turns with the tube; top face + outer cylinder = running track</text>')
    # carriage rollers on collar
    o.append(f'<circle class="buy" cx="{X(R_OUT+14):.1f}" cy="{Z(ztop+4):.1f}" r="{s*4:.1f}"/>')
    o.append(f'<circle class="buy" cx="{X(R_OUT+26):.1f}" cy="{Z((ztop+zbot)/2):.1f}" r="{s*4:.1f}"/>')
    carriage = [(X(R_OUT + 14), Z(ztop + 8)), (X(R_OUT + 14), Z(40)), (X(R_IN - 5), Z(55))]
    o.append(f'<polyline points="{P(carriage)}" fill="none" stroke="#8a6d1f" stroke-width="6"/>')
    o.append(f'<polyline points="{P([(X(R_OUT+26), Z((ztop+zbot)/2)), (X(R_OUT+36), Z((ztop+zbot)/2)), (X(R_OUT+36), Z(40)), (X(R_OUT+14), Z(40))])}" fill="none" stroke="#8a6d1f" stroke-width="4"/>')
    o.append(f'<text x="{X(R_OUT+40):.1f}" y="{Z(46):.1f}">carriage (azimuth held; up and over the lip to the shell)</text>')
    # nozzle + beam
    noz = gp((0, 0, 0))
    o.append(f'<line class="beam" x1="{X(noz[0]):.1f}" y1="{Z(noz[2]):.1f}" x2="{X(R_IN):.1f}" y2="{Z(0):.1f}"/>')
    o.append(f'<circle cx="{X(noz[0]):.1f}" cy="{Z(noz[2]):.1f}" r="{s*5:.1f}" fill="none" stroke="#1f4e9a"/>')
    o.append(f'<text x="{X(noz[0])-120:.1f}" y="{Z(noz[2])-8:.1f}" fill="#1f4e9a">nozzle (opening pose)</text>')
    o.append(f'<text x="20" y="560" class="s">Collar 12–30 mm below the fillet: heat decides the material (printed doubtful, aluminium likely).</text>')
    o.append(f'<text x="20" y="573" class="s">Height registration at install from the rim (fingers, removed before welding) or from the plate face (gauge through the interior).</text>')
    return svg(900, 600, "\n".join(o))


if __name__ == "__main__":
    for name, fn in (("endcap-compass.svg", compass), ("between-centres.svg", centres),
                     ("lip-collar-track.svg", collar)):
        with open(os.path.join(HERE, name), "w") as f:
            f.write(fn())
        print("wrote", name)
