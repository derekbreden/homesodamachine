"""Wave-2 exchange sketch: two work-referenced repairs inside workspace-as-structure's
table-opening arrangement. Elevation seen from +X (the dot's side), +Y to the right,
so the gun (which climbs toward -Y at the scene's opening pose) is on the left and
the free +Y side is on the right.

Tube, lip, plate, ports: repo dimensions. Gun: scene proxy at grip 45 / hole dial 30 /
vertical -15 (pose_geometry.py, dial offset corrected). Collar, shelf, gantry: after
workspace-as-structure's build, schematic. Run: python3 make_exchange_sketch.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pose_geometry import pose_point, GRIP_BASE  # noqa: E402
from make_sketches import STYLE, P, R_IN, R_OUT, RIM, PLATE_R, PORT  # noqa: E402

POSE = (45, 30, -15)
s = 1.2


def gun(o, Y, Z):
    g = lambda p: pose_point(p, *POSE)
    yz = lambda p: (Y(g(p)[1]), Z(g(p)[2]))
    noz, bb = yz((0, 0, 0)), yz((0, 0, 150))
    o.append(f'<line x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}" stroke="#1f4e9a" stroke-width="{s*20:.1f}" stroke-opacity="0.18"/>')
    o.append(f'<line class="gun" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}"/>')
    import itertools
    corners = [yz((a, b, c)) for a, b, c in itertools.product((-17, 17), (-17, 17), (118, 253))]
    body = hull(corners)
    o.append(f'<polygon class="gun" points="{P(body)}" fill="#1f4e9a" fill-opacity="0.08"/>')
    grip = [yz((0, -25, 172)), yz(GRIP_BASE)]
    o.append(f'<polyline class="gun" points="{P(grip)}" stroke-width="6" stroke-opacity="0.5"/>')
    gb = yz(GRIP_BASE)
    o.append(f'<circle cx="{gb[0]:.1f}" cy="{gb[1]:.1f}" r="4" fill="#7a3fa0"/>')
    dot = yz((0, 0, -16))
    o.append(f'<line class="beam" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{dot[0]:.1f}" y2="{dot[1]:.1f}"/>')
    o.append(f'<circle cx="{dot[0]:.1f}" cy="{dot[1]:.1f}" r="3" fill="#d22"/>')
    wb = yz((0, -20, 110))
    o.append(f'<line class="wire" x1="{wb[0]:.1f}" y1="{wb[1]:.1f}" x2="{dot[0]:.1f}" y2="{dot[1]:.1f}"/>')
    return gb, noz, dot


def hull(pts):
    pts = sorted(set((round(x, 2), round(y, 2)) for x, y in pts))
    def cross(o_, a, b):
        return (a[0] - o_[0]) * (b[1] - o_[1]) - (a[1] - o_[1]) * (b[0] - o_[0])
    lower, upper = [], []
    for p_ in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p_) <= 0:
            lower.pop()
        lower.append(p_)
    for p_ in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p_) <= 0:
            upper.pop()
        upper.append(p_)
    return lower[:-1] + upper[:-1]


def tube_top(o, Y, Z, zbot):
    for sgn in (-1, 1):
        y0, y1 = sorted((sgn * R_IN, sgn * R_OUT))
        o.append(f'<rect class="metal" x="{Y(y0):.1f}" y="{Z(RIM):.1f}" width="{s*(y1-y0):.1f}" height="{s*(RIM-zbot):.1f}"/>')
    o.append(f'<rect class="plate" x="{Y(-PLATE_R):.1f}" y="{Z(0):.1f}" width="{s*2*PLATE_R:.1f}" height="{s*RIM:.1f}"/>')
    for py in (-PORT, PORT):
        o.append(f'<rect class="buy" x="{Y(py-6.85):.1f}" y="{Z(25):.1f}" width="{s*13.7:.1f}" height="{s*25:.1f}"/>')
    o.append(f'<rect class="print" x="{Y(-30):.1f}" y="{Z(24):.1f}" width="{s*60:.1f}" height="{s*7:.1f}"/>')


def collar(o, Y, Z, open_r=80):
    top = RIM
    for y0, y1 in ((-270, -open_r), (open_r, 215)):
        o.append(f'<rect class="metal" x="{Y(y0):.1f}" y="{Z(top):.1f}" width="{s*(y1-y0):.1f}" height="{s*12.7:.1f}"/>')
    for y0, y1 in ((-270, -100), (100, 215)):
        o.append(f'<rect x="{Y(y0):.1f}" y="{Z(top-12.7):.1f}" width="{s*(y1-y0):.1f}" height="{s*30:.1f}" fill="#e8d7b8" stroke="#9a7b45"/>')


def panel_a(o):
    ox, oy = 340, 320
    Y = lambda y: ox + s * y
    Z = lambda z: oy - s * z
    o.append('<text class="t" x="20" y="24">W1. Collar-hung centre inside the table-opening gantry (seen from +X; +Y right)</text>')
    o.append('<text class="s" x="20" y="40">The shelf is cranked up until the plate\'s own centre meets a plunger hung from the collar. Tube, plate, ports: repo; gun: scene proxy; the rest schematic.</text>')
    collar(o, Y, Z)
    zb = RIM - 152.4
    tube_top(o, Y, Z, zb)
    # nest, rotator, shelf, posts
    o.append(f'<rect class="print" x="{Y(-75):.1f}" y="{Z(zb):.1f}" width="{s*150:.1f}" height="{s*14:.1f}"/>')
    base_bot = RIM - 214.4
    o.append(f'<rect class="print" x="{Y(-150):.1f}" y="{Z(zb-14):.1f}" width="{s*300:.1f}" height="{s*(zb-14-base_bot):.1f}"/>')
    o.append(f'<text x="{Y(-145):.1f}" y="{Z(zb-14)+14:.1f}" class="s">rotator (turns only; carries)</text>')
    o.append(f'<rect class="metal" x="{Y(-185):.1f}" y="{Z(base_bot):.1f}" width="{s*370:.1f}" height="{s*12:.1f}"/>')
    for py in (-180, 172):
        o.append(f'<rect class="metal" x="{Y(py):.1f}" y="{Z(RIM-12.7):.1f}" width="{s*8:.1f}" height="{s*(RIM-12.7-base_bot):.1f}"/>')
    o.append(f'<text x="{Y(100):.1f}" y="{Z(base_bot)+22:.1f}" class="s">four-post shelf (theirs): crank up to "plunger at 0", lock</text>')
    # plunger + arm on the +Y side
    o.append(f'<circle class="metal" cx="{Y(0):.1f}" cy="{Z(24+6.35):.1f}" r="{s*6.35:.1f}"/>')
    o.append(f'<rect class="metal" x="{Y(-6):.1f}" y="{Z(100):.1f}" width="{s*12:.1f}" height="{s*64:.1f}"/>')
    o.append(f'<rect class="buy" x="{Y(-14):.1f}" y="{Z(72):.1f}" width="{s*28:.1f}" height="{s*24:.1f}"/>')
    o.append(f'<path d="M{Y(-9):.1f},{Z(48)} l{s*18:.1f},-4 l-{s*18:.1f},-4 l{s*18:.1f},-4 l-{s*18:.1f},-4" fill="none" stroke="#555"/>')
    arm = [(Y(14), Z(60)), (Y(115), Z(60)), (Y(115), Z(RIM))]
    o.append(f'<polyline points="{P(arm)}" fill="none" stroke="#555" stroke-width="{s*16:.1f}" stroke-opacity="0.7"/>')
    o.append(f'<rect x="{Y(-10):.1f}" y="{Z(112):.1f}" width="{s*20:.1f}" height="{s*12:.1f}" fill="#fff" stroke="#333"/>')
    o.append(f'<text x="{Y(16):.1f}" y="{Z(112)+2:.1f}" class="s">scale / dial: plate-centre height vs collar</text>')
    o.append(f'<text x="{Y(40):.1f}" y="{Z(84):.1f}">spring plunger (LM12 + Ø12 shaft), ball tip</text>')
    o.append(f'<text x="{Y(40):.1f}" y="{Z(84)+12:.1f}" class="s">in a 90° countersink at the port-pair midpoint:</text>')
    o.append(f'<text x="{Y(40):.1f}" y="{Z(84)+23:.1f}" class="s">plate centre forced onto the plunger axis; 30–50 N hold-down</text>')
    o.append(f'<text x="{Y(125):.1f}" y="{Z(20):.1f}" class="s">arm on the free +Y side</text>')
    o.append(f'<text x="{Y(125):.1f}" y="{Z(20)+11:.1f}" class="s">(tip deflection ~0.01 mm, constant)</text>')
    gb, noz, dot = gun(o, Y, Z)
    # their gantry + saddle under the gun
    o.append(f'<rect class="print" x="{Y(-215):.1f}" y="{Z(110):.1f}" width="{s*55:.1f}" height="{s*(110-RIM):.1f}" fill-opacity="0.6"/>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(118):.1f}" class="s">gantry + pose saddle (theirs)</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-30):.1f}" class="s">collar at rim height (theirs)</text>')
    o.append(f'<text x="{dot[0]+8:.1f}" y="{dot[1]+30:.1f}" fill="#d22" class="s">dot (on the near wall)</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-60):.1f}" class="s">316 hex nipples + seat bar on the plate</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-60)+11:.1f}" class="s">(18.6 mm above the rim: clears the 40 mm gap</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-60)+22:.1f}" class="s">when the shelf drops 70 mm for side loading)</text>')


def panel_b(o):
    ox, oy = 340, 900
    Y = lambda y: ox + s * y
    Z = lambda z: oy - s * z
    o.append(f'<text class="t" x="20" y="{oy-265}">L1. Work-borne lid, parked by the collar (same view)</text>')
    o.append(f'<text class="s" x="20" y="{oy-249}">The lid rides the plate and carries the gun\'s nose ring, a camera and a gas port; the gun\'s tail rests on the workspace.</text>')
    collar(o, Y, Z)
    tube_top(o, Y, Z, -45)
    # centre pin + lid
    lid0, lid1 = RIM + 3, RIM + 6
    o.append(f'<rect class="metal" x="{Y(-4):.1f}" y="{Z(lid0):.1f}" width="{s*8:.1f}" height="{s*(lid0-24):.1f}"/>')
    o.append(f'<rect x="{Y(-100):.1f}" y="{Z(lid1):.1f}" width="{s*200:.1f}" height="{s*3:.1f}" fill="#c9ced6" stroke="#333"/>')
    o.append(f'<rect x="{Y(-100):.1f}" y="{Z(lid1+2):.1f}" width="{s*14:.1f}" height="{s*5:.1f}" fill="#c9ced6" stroke="#333"/>')
    o.append(f'<rect x="{Y(86):.1f}" y="{Z(lid1+2):.1f}" width="{s*14:.1f}" height="{s*5:.1f}" fill="#c9ced6" stroke="#333"/>')
    for by in (30.6, 6.9, -39.4):
        o.append(f'<line x1="{Y(by):.1f}" y1="{Z(lid0):.1f}" x2="{Y(by):.1f}" y2="{Z(8):.1f}" stroke="#2f6b3a" stroke-width="{s*10:.1f}" stroke-opacity="0.5"/>')
        o.append(f'<circle class="metal" cx="{Y(by):.1f}" cy="{Z(4):.1f}" r="{s*4:.1f}"/>')
    # azimuth pin into collar slot at +Y
    o.append(f'<rect x="{Y(92):.1f}" y="{Z(lid1+14):.1f}" width="{s*4:.1f}" height="{s*20:.1f}" fill="#555"/>')
    o.append(f'<text x="{Y(105):.1f}" y="{Z(lid1+40):.1f}" class="s">lugs 5 mm above the collar;</text>')
    o.append(f'<text x="{Y(105):.1f}" y="{Z(lid1+40)+11:.1f}" class="s">tall pin in a collar slot = azimuth;</text>')
    o.append(f'<text x="{Y(105):.1f}" y="{Z(lid1+40)+22:.1f}" class="s">shelf drop > 5 mm parks the lid</text>')
    o.append(f'<text x="{Y(105):.1f}" y="{Z(lid1+40)+33:.1f}" class="s">on the collar; raising lifts it off</text>')
    # camera and gas on the +Y side
    o.append(f'<rect class="metal" x="{Y(55):.1f}" y="{Z(70):.1f}" width="{s*6:.1f}" height="{s*(70-lid1):.1f}"/>')
    o.append(f'<rect x="{Y(50):.1f}" y="{Z(82):.1f}" width="{s*20:.1f}" height="{s*14:.1f}" fill="#555"/>')
    o.append(f'<text x="{Y(75):.1f}" y="{Z(80):.1f}" class="s">camera on the lid:</text>')
    o.append(f'<text x="{Y(75):.1f}" y="{Z(80)+11:.1f}" class="s">dot in plate coordinates</text>')
    o.append(f'<rect class="buy" x="{Y(22):.1f}" y="{Z(lid1+12):.1f}" width="{s*10:.1f}" height="{s*12:.1f}"/>')
    o.append(f'<text x="{Y(20):.1f}" y="{Z(lid1+30):.1f}" class="s">gas port</text>')
    gb, noz, dot = gun(o, Y, Z)
    ring = pose_point((0, 0, 10), *POSE)
    ry, rz = Y(ring[1]), Z(ring[2])
    o.append(f'<ellipse cx="{ry:.1f}" cy="{rz:.1f}" rx="{s*14:.1f}" ry="{s*5:.1f}" fill="none" stroke="#8a6d1f" stroke-width="3"/>')
    o.append(f'<line x1="{ry:.1f}" y1="{rz+6:.1f}" x2="{ry:.1f}" y2="{Z(lid1):.1f}" stroke="#8a6d1f" stroke-width="4"/>')
    o.append(f'<text x="{Y(-150):.1f}" y="{Z(40):.1f}">nose ring on the lid, 26 mm from the dot</text>')
    o.append(f'<line class="dim" x1="{Y(-60):.1f}" y1="{Z(38):.1f}" x2="{ry-10:.1f}" y2="{rz:.1f}"/>')
    tail = pose_point((0, -80, 215), *POSE)
    ty, tz = Y(tail[1]), Z(tail[2])
    o.append(f'<polyline points="{P([(ty-14, tz+8), (ty, tz+2), (ty+14, tz+8)])}" fill="none" stroke="#8a6d1f" stroke-width="4"/>')
    o.append(f'<rect class="print" x="{ty-8:.1f}" y="{tz+8:.1f}" width="16" height="{Z(RIM)-tz-8:.1f}" fill-opacity="0.6"/>')
    o.append(f'<text x="{Y(-265):.1f}" y="{tz-30:.1f}">tail cradle on the workspace</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{tz-18:.1f}" class="s">carries weight + trigger reaction; 220 mm from the ring:</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{tz-7:.1f}" class="s">work motion d reaches the dot as ~0.12 d</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-28):.1f}" class="s">lid: 3 mm sheet, 3 mm above the rim because it rides the plate;</text>')
    o.append(f'<text x="{Y(-265):.1f}" y="{Z(-28)+11:.1f}" class="s">notch at the weld azimuth (-35° to +10°, r > 42) for nozzle, beam, wire</text>')


def main():
    o = []
    panel_a(o)
    panel_b(o)
    body = "\n".join(o)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="960" viewBox="0 0 720 960">\n'
           f'<rect width="720" height="960" fill="#fcfcfa"/>\n{STYLE}\n{body}\n</svg>\n')
    with open(os.path.join(HERE, "xw-collar-centre-and-lid.svg"), "w") as f:
        f.write(svg)
    print("wrote xw-collar-centre-and-lid.svg")


if __name__ == "__main__":
    main()
