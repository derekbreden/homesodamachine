"""Wave-3 sketch: Derek's suspension with the tip loop hung from the endcap.

Elevation seen from +X (the dot's side), +Y to the right. Tube, lip, plate, ports:
repo dimensions. Gun: scene proxy at grip 45 / hole dial 30 / vertical -15
(pose_geometry.py, dial offset applied). Hub, loops, wires: schematic.
Run: python3 make_suspension_sketch.py
"""
import itertools
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from pose_geometry import pose_point, GRIP_BASE  # noqa: E402
from make_sketches import STYLE, P, R_IN, R_OUT, RIM, PLATE_R, PORT  # noqa: E402
from make_exchange_sketch import hull  # noqa: E402

POSE = (45, 30, -15)
s = 1.1
OX, OY = 400, 560
Y = lambda y: OX + s * y
Z = lambda z: OY - s * z
g = lambda p: pose_point(p, *POSE)
yz = lambda p: (Y(g(p)[1]), Z(g(p)[2]))


def main():
    o = []
    o.append('<text class="t" x="20" y="24">D1. Work-hung suspension: Derek\'s tip loop hangs from the endcap, the rest from the room</text>')
    o.append('<text class="s" x="20" y="40">Seen from +X (the dot\'s side), +Y right. Tube, plate, ports: repo; gun: scene proxy at the opening pose; hub, loops, lines: schematic.</text>')
    # overhead bar
    zb = 330
    o.append(f'<rect class="room" x="{Y(-330):.1f}" y="{Z(zb)-10:.1f}" width="{s*420:.1f}" height="10"/>')
    o.append(f'<text x="{Y(-325):.1f}" y="{Z(zb)-14:.1f}" class="s">room: overhead bar (continues up to ~950 mm above the bench) — carries, never locates the dot</text>')
    # tube
    for sgn in (-1, 1):
        y0, y1 = sorted((sgn * R_IN, sgn * R_OUT))
        o.append(f'<rect class="metal" x="{Y(y0):.1f}" y="{Z(RIM):.1f}" width="{s*(y1-y0):.1f}" height="{s*(RIM+40):.1f}"/>')
    o.append(f'<rect class="plate" x="{Y(-PLATE_R):.1f}" y="{Z(0):.1f}" width="{s*2*PLATE_R:.1f}" height="{s*RIM:.1f}"/>')
    for py in (-PORT, PORT):
        o.append(f'<rect class="buy" x="{Y(py-6.85):.1f}" y="{Z(14):.1f}" width="{s*13.7:.1f}" height="{s*14:.1f}"/>')
    o.append(f'<rect class="print" x="{Y(-28):.1f}" y="{Z(14):.1f}" width="{s*56:.1f}" height="{s*5:.1f}"/>')
    # hub: pin, spherical bearing block, wheels
    o.append(f'<rect class="metal" x="{Y(-3):.1f}" y="{Z(30):.1f}" width="{s*6:.1f}" height="{s*16:.1f}"/>')
    o.append(f'<rect class="print" x="{Y(-45):.1f}" y="{Z(30):.1f}" width="{s*90:.1f}" height="{s*8:.1f}"/>')
    for wy, lab in ((0, "P1, P2 (behind each other, on the dot's radius)"), (-38, "P4")):
        o.append(f'<circle class="buy" cx="{Y(wy):.1f}" cy="{Z(6.5):.1f}" r="{s*6.5:.1f}"/>')
        o.append(f'<line x1="{Y(wy):.1f}" y1="{Z(13):.1f}" x2="{Y(wy):.1f}" y2="{Z(22):.1f}" stroke="#8a6d1f" stroke-width="3"/>')
    o.append(f'<path d="M{Y(-2):.1f},{Z(34)} l{s*4:.1f},-3 l-{s*4:.1f},-3 l{s*4:.1f},-3" fill="none" stroke="#555"/>')
    o.append(f'<text x="{Y(70):.1f}" y="{Z(-12):.1f}">plate hanger: port seat + centre pin (x, y),</text>')
    o.append(f'<text x="{Y(70):.1f}" y="{Z(-12)+12:.1f}" class="s">three stainless wheels on the plate face (height, both tilts),</text>')
    o.append(f'<text x="{Y(70):.1f}" y="{Z(-12)+23:.1f}" class="s">pin spring clamps hub to plate (~25 N, internal)</text>')
    # tether for hub azimuth
    o.append(f'<line x1="{Y(45):.1f}" y1="{Z(34):.1f}" x2="{Y(190):.1f}" y2="{Z(34):.1f}" stroke="#444" stroke-width="1.2"/>')
    o.append(f'<rect class="room" x="{Y(190):.1f}" y="{Z(60):.1f}" width="10" height="{s*60:.1f}"/>')
    o.append(f'<text x="{Y(95):.1f}" y="{Z(40):.1f}" class="s">azimuth tether (line + bungee)</text>')
    # nose loop stalk
    nose = g((0, 0, 30))
    ny, nz = Y(nose[1]), Z(nose[2])
    o.append(f'<polyline points="{P([(Y(-10), Z(38)), (Y(-18), Z(38)), (ny, nz+s*15)])}" fill="none" stroke="#8a6d1f" stroke-width="5"/>')
    # gun body
    noz, bb = yz((0, 0, 0)), yz((0, 0, 150))
    o.append(f'<line x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}" stroke="#1f4e9a" stroke-width="{s*20:.1f}" stroke-opacity="0.18"/>')
    o.append(f'<line class="gun" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{bb[0]:.1f}" y2="{bb[1]:.1f}"/>')
    body = hull([yz((a, b, c)) for a, b, c in itertools.product((-17, 17), (-17, 17), (118, 253))])
    o.append(f'<polygon class="gun" points="{P(body)}" fill="#1f4e9a" fill-opacity="0.08"/>')
    o.append(f'<polyline class="gun" points="{P([yz((0, -25, 172)), yz(GRIP_BASE)])}" stroke-width="6" stroke-opacity="0.5"/>')
    dot = yz((0, 0, -16))
    o.append(f'<line class="beam" x1="{noz[0]:.1f}" y1="{noz[1]:.1f}" x2="{dot[0]:.1f}" y2="{dot[1]:.1f}"/>')
    o.append(f'<circle cx="{dot[0]:.1f}" cy="{dot[1]:.1f}" r="3" fill="#d22"/>')
    o.append(f'<text x="{dot[0]+6:.1f}" y="{dot[1]+14:.1f}" fill="#d22" class="s">dot</text>')
    # nose loop (ring around shell nose collar)
    o.append(f'<ellipse cx="{ny:.1f}" cy="{nz:.1f}" rx="{s*16:.1f}" ry="{s*11:.1f}" transform="rotate(-38 {ny:.1f} {nz:.1f})" fill="none" stroke="#8a6d1f" stroke-width="3.5"/>')
    o.append(f'<text x="{Y(-190):.1f}" y="{Z(60):.1f}">nose loop on the work</text>')
    o.append(f'<text x="{Y(-190):.1f}" y="{Z(60)+12:.1f}" class="s">openable, V-bottom, grooved shell collar</text>')
    o.append(f'<text x="{Y(-190):.1f}" y="{Z(60)+23:.1f}" class="s">46 mm from the dot; carries 49–61 %</text>')
    o.append(f'<line class="dim" x1="{Y(-95):.1f}" y1="{Z(58):.1f}" x2="{ny-12:.1f}" y2="{nz:.1f}"/>')
    # park line from bar to nose (slack)
    o.append(f'<line x1="{ny:.1f}" y1="{nz-s*14:.1f}" x2="{ny+20:.1f}" y2="{Z(zb):.1f}" stroke="#777" stroke-dasharray="6 4"/>')
    o.append(f'<text x="{ny+26:.1f}" y="{Z(250):.1f}" class="s">Derek\'s tip wire, kept as the</text>')
    o.append(f'<text x="{ny+26:.1f}" y="{Z(250)+11:.1f}" class="s">park / lift line: slack while welding</text>')
    # base loop at grip butt
    gb = g(GRIP_BASE)
    axis = [gb[i] - g((0, 0, -16))[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in axis))
    base = [gb[i] + 40 * axis[i] / L for i in range(3)]
    by_, bz_ = Y(base[1]), Z(base[2])
    o.append(f'<circle cx="{by_:.1f}" cy="{bz_:.1f}" r="12" fill="none" stroke="#8a6d1f" stroke-width="3.5"/>')
    o.append(f'<line x1="{by_:.1f}" y1="{bz_-12:.1f}" x2="{by_:.1f}" y2="{Z(zb):.1f}" stroke="#444" stroke-width="1.4"/>')
    o.append(f'<rect x="{by_-6:.1f}" y="{Z(260):.1f}" width="12" height="16" fill="#fff" stroke="#444"/>')
    o.append(f'<text x="{by_+10:.1f}" y="{Z(262):.1f}" class="s">ratchet: per-tube pitch trim</text>')
    o.append(f'<circle cx="{by_-24:.1f}" cy="{bz_+4:.1f}" r="5" fill="#fff" stroke="#444"/>')
    o.append(f'<circle cx="{by_-24:.1f}" cy="{bz_+4:.1f}" r="1.5" fill="#444"/>')
    for i, (txt, cls) in enumerate((("base loop (room): Derek's wire in Z;", ""),
                                     ("X held by a line (out of page, ⊙) with his", "s"),
                                     ("bungee as its preload; bungees alone would", "s"),
                                     ("let 1 N move the dot 1–1.7 mm", "s"))):
        c = f' class="{cls}"' if cls else ''
        o.append(f'<text x="20" y="{Z(420)+12*i:.1f}"{c}>{txt}</text>')
    # third ring at housing back top
    tr = yz((0, 17, 245))
    o.append(f'<circle cx="{tr[0]:.1f}" cy="{tr[1]:.1f}" r="9" fill="none" stroke="#8a6d1f" stroke-width="3"/>')
    o.append(f'<line x1="{tr[0]:.1f}" y1="{tr[1]-9:.1f}" x2="{tr[0]:.1f}" y2="{Z(zb):.1f}" stroke="#444" stroke-width="1.4"/>')
    o.append(f'<text x="{tr[0]+12:.1f}" y="{tr[1]-14:.1f}" class="s">third ring (room): roll about the nose–base line</text>')
    # cable saddle
    o.append(f'<path class="cable" d="M{Y(gb[1]):.1f},{Z(gb[2]):.1f} C{Y(-330):.1f},{Z(gb[2]+10):.1f} {Y(-360):.1f},{Z(60):.1f} {Y(-370):.1f},{Z(-30):.1f}"/>')
    o.append(f'<text x="30" y="{Z(40):.1f}" fill="#7a3fa0" class="s">umbilical + conduit</text>')
    o.append(f'<text x="30" y="{Z(40)+11:.1f}" fill="#7a3fa0" class="s">on a room saddle, R ≥ 350</text>')

    # inset: nose loop contact
    ix, iy = 690, 250
    o.append(f'<rect x="{ix-110}" y="{iy-95}" width="220" height="215" fill="#fff" stroke="#999"/>')
    o.append(f'<text x="{ix-102}" y="{iy-78}" class="s">nose loop, in its own plane (⟂ barrel)</text>')
    o.append(f'<circle cx="{ix}" cy="{iy}" r="34" fill="#f3e3b5" stroke="#8a6d1f"/>')
    o.append(f'<circle cx="{ix}" cy="{iy}" r="12" fill="#d9dde3" stroke="#333"/>')
    o.append(f'<circle cx="{ix+14}" cy="{iy+20}" r="3" fill="#666"/>')
    o.append(f'<text x="{ix-28}" y="{iy+4}" class="s">barrel</text>')
    o.append(f'<text x="{ix+19}" y="{iy+33}" class="s">wire guide</text>')
    vy = iy + 34 * math.sqrt(2)
    o.append(f'<polyline points="{ix-60},{iy+8} {ix},{vy:.1f} {ix+60},{iy+8}" fill="none" stroke="#2f6b3a" stroke-width="4"/>')
    o.append(f'<path d="M{ix-60},{iy+8} A62,62 0 0 1 {ix+60},{iy+8}" fill="none" stroke="#2f6b3a" stroke-width="2" stroke-dasharray="5 3"/>')
    o.append(f'<circle cx="{ix+60}" cy="{iy+8}" r="4" fill="#2f6b3a"/>')
    o.append(f'<text x="{ix-102}" y="{iy+80}" class="s">V flanks: 2 in-plane translations, seated by</text>')
    o.append(f'<text x="{ix-102}" y="{iy+91}" class="s">4.9–7 N of the nose share; groove on the</text>')
    o.append(f'<text x="{ix-102}" y="{iy+102}" class="s">knife-edge ring: axial. Upper half (dashed) is</text>')
    o.append(f'<text x="{ix-102}" y="{iy+113}" class="s">clearance + latch pin: captive, not clamped.</text>')
    o.append(f'<line x1="{ix}" y1="{iy-40}" x2="{ix}" y2="{iy-10}" class="arrow"/>')

    # what is fixed to what
    ty = 640
    rows = [("nose: height, radius, along-barrel (3)", "plate (face + port-pair centre)", "V-loop on a stalk from the plate hanger"),
            ("pitch + yaw about the nose (2)", "room", "base loop: Z wire (ratchet) + X line/bungee"),
            ("roll about the nose–base line (1)", "room", "third ring's Z wire"),
            ("hub azimuth (harmless)", "room", "tether line + bungee, one-sided vs stuck-wire drag"),
            ("weight: nose share 49–61 % / rest", "plate / room", "the plate sees ~10 N at r 48: ~0.4 N·m"),
            ("umbilical + conduit", "room", "saddle behind the base loop")]
    o.append(f'<text class="t" x="20" y="{ty}">What "fixed" is fixed to</text>')
    for i, (a, b, c) in enumerate(rows):
        yy = ty + 18 + i * 15
        o.append(f'<text x="30" y="{yy}" class="s">{a}</text><text x="290" y="{yy}" class="s">{b}</text><text x="490" y="{yy}" class="s">{c}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{ty+120}" viewBox="0 0 900 {ty+120}">\n'
           f'<rect width="900" height="{ty+120}" fill="#fcfcfa"/>\n{STYLE}\n' + "\n".join(o) + "\n</svg>\n")
    with open(os.path.join(HERE, "work-hung-suspension.svg"), "w") as f:
        f.write(svg)
    print("wrote work-hung-suspension.svg")


if __name__ == "__main__":
    main()
