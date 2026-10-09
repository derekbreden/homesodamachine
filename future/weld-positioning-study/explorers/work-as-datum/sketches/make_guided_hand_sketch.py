"""Wave-4 sketch: the hand stays the actuator; a dot-centred cup on the endcap gives the dot.

Elevation seen from +X (the dot's side), +Y right. Tube, plate, ports: repo dimensions.
Gun: scene proxy at the opening pose (pose_geometry.py). Cup, hanger, fork: schematic.
Run: python3 make_guided_hand_sketch.py
"""
import itertools
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pose_geometry import pose_point, GRIP_BASE  # noqa: E402
from make_sketches import STYLE, P, R_IN, R_OUT, RIM, PLATE_R, PORT  # noqa: E402
from make_exchange_sketch import hull  # noqa: E402

POSE = (45, 30, -15)
s = 1.75
OX, OY = 490, 540
Y = lambda y: OX + s * y
Z = lambda z: OY - s * z
g = lambda p: np.array(pose_point(p, *POSE))
yz = lambda p: (Y(g(p)[1]), Z(g(p)[2]))


def main():
    o = []
    o.append('<text class="t" x="20" y="24">H1. Guided hand: the work holds the dot, a fork holds two angles, the hand holds roll, preload and trigger</text>')
    o.append('<text class="s" x="20" y="40">Seen from +X, +Y right. Tube, plate, ports: repo; gun: scene proxy at the opening pose; cup, hanger, fork: schematic.</text>')
    # tube, plate, seat
    for sgn in (-1, 1):
        y0, y1 = sorted((sgn * R_IN, sgn * R_OUT))
        o.append(f'<rect class="metal" x="{Y(y0):.1f}" y="{Z(RIM):.1f}" width="{s*(y1-y0):.1f}" height="{s*(RIM+40):.1f}"/>')
    o.append(f'<rect class="plate" x="{Y(-PLATE_R):.1f}" y="{Z(0):.1f}" width="{s*2*PLATE_R:.1f}" height="{s*RIM:.1f}"/>')
    for py in (-PORT, PORT):
        o.append(f'<rect class="buy" x="{Y(py-6.85):.1f}" y="{Z(14):.1f}" width="{s*13.7:.1f}" height="{s*14:.1f}"/>')
    o.append(f'<rect class="print" x="{Y(-28):.1f}" y="{Z(14):.1f}" width="{s*56:.1f}" height="{s*5:.1f}"/>')
    o.append(f'<rect class="print" x="{Y(-45):.1f}" y="{Z(30):.1f}" width="{s*90:.1f}" height="{s*8:.1f}"/>')
    for wy in (0, -38):
        o.append(f'<circle class="buy" cx="{Y(wy):.1f}" cy="{Z(6.5):.1f}" r="{s*6.5:.1f}"/>')
    # gun
    noz, bb = yz((0, 0, 0)), yz((0, 0, 150))
    o.append(f'<line x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}" stroke="#1f4e9a" stroke-width="{s*20:.1f}" stroke-opacity="0.18"/>')
    o.append(f'<line class="gun" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}"/>')
    body = hull([yz((a, b, c)) for a, b, c in itertools.product((-17, 17), (-17, 17), (118, 253))])
    o.append(f'<polygon class="gun" points="{P(body)}" fill="#1f4e9a" fill-opacity="0.08"/>')
    o.append(f'<polyline class="gun" points="{P([yz((0, -25, 172)), yz(GRIP_BASE)])}" stroke-width="7" stroke-opacity="0.5"/>')
    dot3 = g((0, 0, -16))
    dot = (Y(dot3[1]), Z(dot3[2]))
    o.append(f'<line class="beam" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{dot[0]:.1f}" y2="{dot[1]:.1f}"/>')
    o.append(f'<circle cx="{dot[0]:.1f}" cy="{dot[1]:.1f}" r="3" fill="#d22"/>')
    # cup: three balls on the shell at 41 mm up the barrel, 57 mm circle; pads toward the dot
    bar = g((0, 0, 1)) - g((0, 0, 0))
    bar /= np.linalg.norm(bar)
    gdn = np.array([0, 0, -1.0])
    e1 = gdn - np.dot(gdn, bar) * bar
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(bar, e1)
    Rs, al = 50.0, math.radians(35)
    for k in range(3):
        th = math.radians(60 + 120 * k)
        c = dot3 + Rs * math.cos(al) * bar + Rs * math.sin(al) * (math.cos(th) * e1 + math.sin(th) * e2)
        pad = dot3 + (Rs - 6) * (c - dot3) / np.linalg.norm(c - dot3)
        o.append(f'<line class="dim" x1="{Y(c[1]):.1f}" y1="{Z(c[2]):.1f}" x2="{dot[0]:.1f}" y2="{dot[1]:.1f}"/>')
        o.append(f'<circle class="metal" cx="{Y(c[1]):.1f}" cy="{Z(c[2]):.1f}" r="{s*4:.1f}"/>')
        o.append(f'<circle cx="{Y(pad[1]):.1f}" cy="{Z(pad[2]):.1f}" r="{s*3:.1f}" fill="#2f6b3a"/>')
        o.append(f'<line x1="{Y(pad[1]):.1f}" y1="{Z(pad[2]):.1f}" x2="{Y(-10):.1f}" y2="{Z(38):.1f}" stroke="#8a6d1f" stroke-width="3" stroke-opacity="0.7"/>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150):.1f}">cup on the work: three shell balls rest on</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+12:.1f}" class="s">pads of a sphere R 50 centred on the dot (normals, dashed,</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+23:.1f}" class="s">all pass through the dot): the dot is fixed, every rotation</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+34:.1f}" class="s">about it is free. Pads on stalks from the plate hanger.</text>')
    o.append(f'<text x="{Y(-40):.1f}" y="{Z(-30):.1f}">plate hanger (port seat, pin, three wheels, clamp) — as in D1</text>')
    # tail fork: round vertical bore at the grip base, on a room post
    gb = g(GRIP_BASE)
    ty, tz = Y(gb[1]), Z(gb[2])
    o.append(f'<circle cx="{ty:.1f}" cy="{tz:.1f}" r="6" fill="#7a3fa0"/>')
    o.append(f'<rect x="{ty-12:.1f}" y="{tz-18:.1f}" width="24" height="36" fill="none" stroke="#555" stroke-width="2"/>')
    o.append(f'<rect class="room" x="{ty-6:.1f}" y="{tz+18:.1f}" width="12" height="{Z(-40)-tz-18:.1f}"/>')
    o.append(f'<text x="20" y="{tz-90:.1f}">tail fork (room): grip-base ball</text>')
    o.append(f'<text x="20" y="{tz-78:.1f}" class="s">in a round vertical bore — sets hole and</text>')
    o.append(f'<text x="20" y="{tz-67:.1f}" class="s">plan angle (0.21°/mm); dot unaffected</text>')
    # hand at the grip
    gm = yz((0, -80, 215))
    o.append(f'<ellipse cx="{gm[0]:.1f}" cy="{gm[1]:.1f}" rx="26" ry="16" fill="#f1c9a5" fill-opacity="0.6" stroke="#a0683d"/>')
    o.append(f'<text x="{gm[0]-10:.1f}" y="{gm[1]-26:.1f}">hand: grip + trigger;</text>')
    o.append(f'<text x="{gm[0]-10:.1f}" y="{gm[1]-14:.1f}" class="s">holds roll about the grip axis, presses 7–15 N into the cup</text>')
    # grip axis
    o.append(f'<line x1="{dot[0]:.1f}" y1="{dot[1]:.1f}" x2="{ty:.1f}" y2="{tz:.1f}" stroke="#c05a00" stroke-dasharray="8 4"/>')
    o.append(f'<text x="{Y(-150):.1f}" y="{Z(40):.1f}" fill="#c05a00" class="s">grip axis (dot → cable exit): the one freedom left to the hand</text>')
    # IMU and seat light
    hb = yz((17, 17, 200))
    o.append(f'<rect x="{hb[0]-7:.1f}" y="{hb[1]-7:.1f}" width="14" height="10" fill="#333"/>')
    o.append(f'<text x="{hb[0]+10:.1f}" y="{hb[1]:.1f}" class="s">IMU logs roll; LED: all three balls seated</text>')
    # table
    ty0 = 640
    rows = [("dot: 3 translations", "work (plate face + port-pair centre)", "cup centred on the dot"),
            ("hole angle + plan angle", "room (or rotator frame)", "tail ball in a round bore"),
            ("roll about the grip axis", "the hand", "pointer / IMU; beam turns 0.42° per 1° of roll"),
            ("weight", "cup (nose share) + balancer", "the hand carries none of it"),
            ("travel along the seam", "the rotator", "pedal"),
            ("trigger", "the hand", "squeeze is internal to the hand")]
    o.append(f'<text class="t" x="20" y="{ty0}">What each part sets</text>')
    for i, (a, b, c) in enumerate(rows):
        yy = ty0 + 18 + i * 15
        o.append(f'<text x="30" y="{yy}" class="s">{a}</text><text x="230" y="{yy}" class="s">{b}</text><text x="470" y="{yy}" class="s">{c}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{ty0+115}" viewBox="0 0 900 {ty0+115}">\n'
           f'<rect width="900" height="{ty0+115}" fill="#fcfcfa"/>\n{STYLE}\n' + "\n".join(o) + "\n</svg>\n")
    with open(os.path.join(HERE, "guided-hand.svg"), "w") as f:
        f.write(svg)
    print("wrote guided-hand.svg")


if __name__ == "__main__":
    main()
