"""Wave-5 sketch: work-hung suspension D4 — the nose loop replaced by a cup centred on the dot,
with sprung outer pads closing the preload inside the cup; base loop and third ring on lines from a
post on the rotator frame; a balancer carries. Derived from make_guided_hand_sketch.py.

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
s = 1.6
OX, OY = 620, 540
Y = lambda y: OX + s * y
Z = lambda z: OY - s * z
g = lambda p: np.array(pose_point(p, *POSE))
yz = lambda p: (Y(g(p)[1]), Z(g(p)[2]))


def main():
    o = []
    o.append('<text class="t" x="20" y="24">D4. Work-hung suspension with a dot-centred cup: the work holds the dot, room lines hold the angles, a float carries</text>')
    o.append('<text class="s" x="20" y="40">Seen from +X, +Y right. Tube, plate, ports: repo; gun: scene proxy at the opening pose; cup, hanger, lines: schematic.</text>')
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
        outer = dot3 + (Rs + 6) * (c - dot3) / np.linalg.norm(c - dot3)
        o.append(f'<rect x="{Y(outer[1])-4:.1f}" y="{Z(outer[2])-4:.1f}" width="8" height="8" fill="#c05a00"/>')
        o.append(f'<line x1="{Y(pad[1]):.1f}" y1="{Z(pad[2]):.1f}" x2="{Y(-10):.1f}" y2="{Z(38):.1f}" stroke="#8a6d1f" stroke-width="3" stroke-opacity="0.7"/>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150):.1f}">cup on the work: each shell ball is held between</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+12:.1f}" class="s">an inner pad (green) and a sprung outer pad (orange), both on</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+23:.1f}" class="s">spheres centred on the dot: ~25 N preload closes inside the cup;</text>')
    o.append(f'<text x="{Y(30):.1f}" y="{Z(150)+34:.1f}" class="s">the dot is fixed, rotations about it free (friction 0.15–0.5 N·m).</text>')
    o.append(f'<text x="{Y(-40):.1f}" y="{Z(-30):.1f}">plate hanger (port seat, pin, three wheels, clamp) — as in D1</text>')
    # room lines from a post on the rotator frame; balancer; third ring
    gb = g(GRIP_BASE)
    ax_ = (gb - dot3) / np.linalg.norm(gb - dot3)
    base = gb + 40 * ax_
    by_, bz_ = Y(base[1]), Z(base[2])
    o.append(f'<circle cx="{by_:.1f}" cy="{bz_:.1f}" r="10" fill="none" stroke="#8a6d1f" stroke-width="3.5"/>')
    postx = Y(-300)
    o.append(f'<rect class="room" x="{postx-6:.1f}" y="{Z(260):.1f}" width="12" height="{Z(-40)-Z(260):.1f}"/>')
    o.append(f'<line x1="{postx:.1f}" y1="{Z(250):.1f}" x2="{by_:.1f}" y2="{bz_-10:.1f}" stroke="#444" stroke-width="1.4"/>')
    o.append(f'<path d="M{by_:.1f},{bz_+10:.1f} l6,8 l-12,8 l12,8 l-12,8 l6,8" fill="none" stroke="#7a3fa0"/>')
    o.append(f'<line x1="{by_:.1f}" y1="{bz_+50:.1f}" x2="{postx:.1f}" y2="{Z(60):.1f}" stroke="#7a3fa0"/>')
    o.append(f'<circle cx="{by_-22:.1f}" cy="{bz_:.1f}" r="5" fill="#fff" stroke="#444"/><circle cx="{by_-22:.1f}" cy="{bz_:.1f}" r="1.5" fill="#444"/>')
    o.append(f'<text x="20" y="{Z(250)-60:.1f}">base loop: Z line + its own bungee, X line (⊙) + bungee,</text>')
    o.append(f'<text x="20" y="{Z(250)-48:.1f}" class="s">all anchored on a post from the rotator frame (not the ceiling);</text>')
    o.append(f'<text x="20" y="{Z(250)-37:.1f}" class="s">they set pitch and yaw about the dot and no longer move it</text>')
    tr = yz((0, 17, 245))
    o.append(f'<circle cx="{tr[0]:.1f}" cy="{tr[1]:.1f}" r="8" fill="none" stroke="#8a6d1f" stroke-width="3"/>')
    o.append(f'<line x1="{tr[0]:.1f}" y1="{tr[1]-8:.1f}" x2="{postx:.1f}" y2="{Z(262):.1f}" stroke="#444" stroke-width="1.2"/>')
    o.append(f'<text x="{tr[0]+12:.1f}" y="{tr[1]-10:.1f}" class="s">third ring: roll (line + bungee)</text>')
    cg = yz((0, -30, 200))
    o.append(f'<line x1="{cg[0]:.1f}" y1="{cg[1]:.1f}" x2="{cg[0]:.1f}" y2="60" stroke="#444" stroke-dasharray="2 2"/>')
    o.append(f'<rect class="room" x="{cg[0]-14:.1f}" y="48" width="28" height="12"/>')
    o.append(f'<text x="{cg[0]+18:.1f}" y="74" class="s">spring balancer: carries the weight (float)</text>')
    o.append(f'<path class="cable" d="M{Y(gb[1]):.1f},{Z(gb[2]):.1f} C{Y(-330):.1f},{Z(gb[2]+30):.1f} {Y(-360):.1f},{Z(80):.1f} {Y(-380):.1f},{Z(-30):.1f}"/>')
    # table
    ty0 = 640
    rows = [("dot: 3 translations", "work (plate face + port-pair centre)", "cup centred on the dot, preload internal"),
            ("pitch + yaw about the dot", "rotator frame post", "base Z and X lines, each with its own bungee"),
            ("roll", "rotator frame post", "third-ring line + bungee"),
            ("weight", "room", "spring balancer; the plate carries ~nothing"),
            ("umbilical + conduit", "room", "saddle behind the base loop"),
            ("trigger", "inside the shell", "presser (Bowden or solenoid)")]
    o.append(f'<text class="t" x="20" y="{ty0}">What each part sets (D4)</text>')
    for i, (a, b, c) in enumerate(rows):
        yy = ty0 + 18 + i * 15
        o.append(f'<text x="30" y="{yy}" class="s">{a}</text><text x="230" y="{yy}" class="s">{b}</text><text x="470" y="{yy}" class="s">{c}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="980" height="{ty0+115}" viewBox="0 0 980 {ty0+115}">\n'
           f'<rect width="980" height="{ty0+115}" fill="#fcfcfa"/>\n{STYLE}\n' + "\n".join(o) + "\n</svg>\n")
    with open(os.path.join(HERE, "work-hung-suspension-D4.svg"), "w") as f:
        f.write(svg)
    print("wrote work-hung-suspension-D4.svg")


if __name__ == "__main__":
    main()
