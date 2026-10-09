"""Pose: scene hole DIAL 30 (wave-3 fix). Pads moved to 45/150/255 deg, frame rim+15 (head_w3.py);
the wave-2 layout (180/60/-60 at rim+40) hits the barrel at the true pose. Exchange sketches (wave 2): the stand-hung plate head for a still gun, and the trolley-parked
carrier. Plan panel of sketch 1 is to scale from the proxy; sections and sketch 2 are schematic."""
import math
from proxy import *

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;')
# ---------------- sketch 1 ----------------
S = 2.2
W, H = 1100, 640
cx, cy = 330, 330
def P(x, y): return (cx + S * x, cy - S * y)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Still gun, moving work — hanging the plate from P (repair for phases 3–6)</text>',
     '<text x="12" y="36">Left: plan from above, to scale (proxy gun, opening pose). Right: section through the port line, schematic. Stationary parts green; parts turning with the tube brown.</text>']
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_OUT}" fill="#e6eeee" stroke="#577"/><circle cx="{cx}" cy="{cy}" r="{S*R_IN}" fill="#d8e4e4" stroke="#577"/>')
for sgn in (1, -1):
    a, b = P(0, sgn * 19.05); o.append(f'<circle cx="{a}" cy="{b}" r="{S*5.56:.1f}" fill="#fff" stroke="#840"/>')
    o.append(f'<circle cx="{a}" cy="{b}" r="{S*3:.1f}" fill="#b86" stroke="#840"/>')
o.append(f'<text x="{P(4,26)[0]}" y="{P(4,26)[1]}" fill="#840">port plug + collar (turns)</text>')
d = P(R_IN, 0); o.append(f'<circle cx="{d[0]}" cy="{d[1]}" r="4" fill="#d00"/><text x="{d[0]+8}" y="{d[1]+16}" fill="#d00">P (dot)</text>')
g = [pose(p) for p in ((0, 0, 0), (0, 0, 118), (0, 0, 253))]
o.append('<polyline points="%s" fill="none" stroke="#335" stroke-width="16" opacity="0.25" stroke-linecap="round"/>' % ' '.join(f'{P(q[0], q[1])[0]:.1f},{P(q[0], q[1])[1]:.1f}' for q in g))
gb, gs = pose(GB), pose((0, -25, 172))
o.append(f'<line x1="{P(gs[0],gs[1])[0]:.1f}" y1="{P(gs[0],gs[1])[1]:.1f}" x2="{P(gb[0],gb[1])[0]:.1f}" y2="{P(gb[0],gb[1])[1]:.1f}" stroke="#335" stroke-width="20" opacity="0.18" stroke-linecap="round"/>')
o.append(f'<text x="{P(25,-120)[0]}" y="{P(25,-120)[1]}" fill="#335">gun (proxy plan)</text>')
# fork across ports (turns)
a, b = P(0, 19.05); c2, d2 = P(0, -19.05)
o.append(f'<line x1="{a}" y1="{b}" x2="{c2}" y2="{d2}" stroke="#840" stroke-width="5"/>')
o.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#fff" stroke="#2a6" stroke-width="2"/>')
# stationary head: 3 pads at r=40
for ang in (45, 150, 255):
    x, y = 40 * math.cos(math.radians(ang)), 40 * math.sin(math.radians(ang))
    a, b = P(x, y)
    o.append(f'<line x1="{cx}" y1="{cy}" x2="{a:.1f}" y2="{b:.1f}" stroke="#2a6" stroke-width="4" opacity="0.8"/>')
    o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{S*8:.1f}" fill="#bfe3c8" stroke="#2a6"/>')
o.append(f'<text x="{P(-120,95)[0]}" y="{P(-120,95)[1]}" fill="#2a6">3 ball-transfer pads, r = 40 mm, at 45°/150°/255° (stationary)</text>')
o.append(f'<text x="{P(-120,87)[0]}" y="{P(-120,87)[1]}" fill="#2a6">define the plate face plane at P height</text>')
# arm to stand toward -X
a, b = P(-140, 0)
o.append(f'<line x1="{cx}" y1="{cy}" x2="{a}" y2="{b}" stroke="#2a6" stroke-width="7" opacity="0.7"/>')
o.append(f'<rect x="{a-14}" y="{b-14}" width="28" height="28" fill="#cfe9d6" stroke="#2a6"/><text x="{a-20}" y="{b+30}" fill="#2a6">arm to the gun stand</text>')
# rim flag at -X
a, b = P(-R_OUT - 2, -12); o.append(f'<rect x="{a-6}" y="{b-5}" width="14" height="10" fill="#2a6"/><text x="{a-60}" y="{b+22}" fill="#2a6">rim flag at P + 6.35</text>')
# drawer direction
a, b = P(90, -95); a2, b2 = P(150, -95)
o.append(f'<line x1="{a}" y1="{b}" x2="{a2}" y2="{b2}" stroke="#a50" stroke-width="2.5" marker-end="url(#a)"/><text x="{a-10}" y="{b+18}" fill="#a50">drawer out: +X only, after a 10 mm drop</text>')
o.append(f'<text x="{a-10}" y="{b+32}" fill="#a50">(or any direction after 14 mm wire retract)</text>')
o.append(f'<text x="{P(-110,-130)[0]}" y="{P(-110,-130)[1]}">Closest head-to-gun centre-line distance 38.8 mm (barrel), frame at rim+15. Old 180/±60° layout: 6 mm (hits the barrel).</text>')
# section panel (schematic, 3 px/mm)
k = 3.0
sx, sy = 640, 250   # sy = P height
o.append(f'<text x="{sx}" y="90" font-weight="bold">Section through the port line (schematic)</text>')
# tube walls at +/- R
def X(x): return sx + 170 + k * x * 0.9
o.append(f'<rect x="{X(-R_OUT)}" y="{sy - k*6.35}" width="{k*1.65}" height="210" fill="#8aa" stroke="#577"/>')
o.append(f'<rect x="{X(R_IN)}" y="{sy - k*6.35}" width="{k*1.65}" height="210" fill="#8aa" stroke="#577"/>')
o.append(f'<rect x="{X(-R_IN)}" y="{sy}" width="{X(R_IN)-X(-R_IN)}" height="{k*6.35}" fill="#b89" fill-opacity="0.5" stroke="#840"/>')
o.append(f'<text x="{X(-40)}" y="{sy + k*6.35 + 14}" fill="#840">end plate (turns with tube)</text>')
o.append(f'<line x1="{sx-10}" y1="{sy}" x2="{X(R_OUT)+60}" y2="{sy}" stroke="#d00" stroke-dasharray="4 3"/><text x="{X(R_OUT)+10}" y="{sy-4}" fill="#d00">P height</text>')
o.append(f'<line x1="{sx-10}" y1="{sy-k*6.35}" x2="{X(R_OUT)+60}" y2="{sy-k*6.35}" stroke="#2a6" stroke-dasharray="4 3"/><text x="{X(R_OUT)+10}" y="{sy-k*6.35-4}" fill="#2a6">rim = P + 6.35 (rim flag)</text>')
# plugs + collars
for sgn in (1, -1):
    x = X(sgn * 19.05)
    o.append(f'<rect x="{x-8}" y="{sy-18}" width="16" height="{18+k*3}" fill="#b86" stroke="#840"/>')
    o.append(f'<rect x="{x-11}" y="{sy-30}" width="22" height="7" fill="#b86" stroke="#840"/>')
# fork on spindle (turns)
o.append(f'<rect x="{X(-25)}" y="{sy-40}" width="{X(25)-X(-25)}" height="9" fill="none" stroke="#840" stroke-width="2"/>')
o.append(f'<line x1="{X(0)}" y1="{sy-40}" x2="{X(0)}" y2="{sy-110}" stroke="#840" stroke-width="4"/>')
o.append(f'<text x="{X(-25)-10}" y="{sy-46}" fill="#840">keyhole fork on collars</text>')
# spindle housing (stationary) + spring
o.append(f'<rect x="{X(0)-12}" y="{sy-130}" width="24" height="30" fill="#cfe9d6" stroke="#2a6"/>')
o.append(f'<text x="{X(0)+16}" y="{sy-118}" fill="#2a6">bearing housing (stationary); spring pulls</text><text x="{X(0)+16}" y="{sy-104}" fill="#2a6">spindle UP: plate held against pads</text>')
# pads (stationary) pressing on plate face at r=40 (one shown each side, schematic)
for sgn in (1, -1):
    x = X(sgn * 40)
    o.append(f'<line x1="{x}" y1="{sy-130}" x2="{x}" y2="{sy-10}" stroke="#2a6" stroke-width="3"/>')
    o.append(f'<circle cx="{x}" cy="{sy-6}" r="6" fill="#bfe3c8" stroke="#2a6"/>')
o.append(f'<line x1="{X(-40)}" y1="{sy-130}" x2="{X(40)}" y2="{sy-130}" stroke="#2a6" stroke-width="3"/>')
o.append(f'<line x1="{X(-40)}" y1="{sy-130}" x2="{sx-20}" y2="{sy-130}" stroke="#2a6" stroke-width="5"/><text x="{sx-10}" y="{sy-136}" fill="#2a6">arm (to stand, over the −X rim)</text>')
o.append(f'<text x="{X(40)+10}" y="{sy-14}" fill="#2a6">pad</text>')
o.append(f'<text x="{sx-20}" y="{sy+120}">Holds: plate Z and tilt (pads, from the stand = from P).</text>')
o.append(f'<text x="{sx-20}" y="{sy+136}">Leaves free: radial (the bore centres the plate) and spin (bearing).</text>')
o.append(f'<text x="{sx-20}" y="{sy+152}">Corner height at the station = P for any tube length; the work Z</text>')
o.append(f'<text x="{sx-20}" y="{sy+168}">only sets the lip (rim flag). Engaged phases 3–5; lifted 2 mm for the weld.</text>')
o.append('</svg>')
open('../sketches/x2-plate-hung-from-P.svg', 'w').write('\n'.join(o))

# ---------------- sketch 2 ----------------
W, H = 1000, 680
K = 0.42
def B(x, z): return (260 + K * x, 610 - K * z)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Carrier + seat, parked on a trolley (branch of who-moves-what D1/D2; schematic, 0.42 px/mm)</text>',
     '<text x="12" y="36">Side view. One overhead rail; the trolley carries both balancers and the umbilical saddle, so the gun-to-saddle umbilical keeps one shape at the station and at park.</text>']
bx0, by0 = B(-600, 0); bx1, _ = B(1500, 0)
o.append(f'<line x1="{bx0}" y1="{by0}" x2="{bx1}" y2="{by0}" stroke="#333" stroke-width="2"/><text x="{bx0+4}" y="{by0+14}">bench</text>')
# rotator base + tube
a, b = B(-150, 36); a2, b2 = B(150, 24)
o.append(f'<rect x="{a}" y="{b}" width="{a2-a}" height="{b2-b}" fill="#ddd" stroke="#888"/>')
a, b = B(-63.5, 238.4); a2, b2 = B(63.5, 86)
o.append(f'<rect x="{a}" y="{b}" width="{a2-a}" height="{b2-b}" fill="#dfeaea" stroke="#577"/><text x="{a}" y="{b2+14}">tube on rotator</text>')
# seat post at -Y side drawn at x=-230
pa, pb = B(-230, 420); pa2, pb2 = B(-218, 36)
o.append(f'<rect x="{pa}" y="{pb}" width="{pa2-pa}" height="{pb2-pb}" fill="#cfe9d6" stroke="#2a6"/>')
o.append(f'<polygon points="{pa-10},{pb} {pa+30},{pb} {pa+26},{pb-7} {pa-6},{pb-7}" fill="#e7c" stroke="#704"/><text x="{pa-150}" y="{pb-14}" fill="#704">seat (3 vees) on post from rotator base</text>')
RZ = 1250
ra, rb = B(-350, RZ); rc, rd = B(1100, RZ)
o.append(f'<rect x="{ra}" y="{rb-8}" width="{rc-ra}" height="8" fill="#aaa" stroke="#666"/><text x="{rc-230}" y="{rb-14}">rail, ~1.25 m above bench (estimate)</text>')
def carrier(x0, ghost):
    st = ' opacity="0.35"' if ghost else ''
    out = []
    t0, t1 = B(x0 - 120, RZ), B(x0 + 260, RZ)
    out.append(f'<rect x="{t0[0]}" y="{t0[1]}" width="{t1[0]-t0[0]}" height="10" fill="#cfe9d6" stroke="#2a6"{st}/>')
    nz, gbz = (x0 + 30, 250), (x0 - 20, 490)     # nozzle, grip base (schematic side positions)
    ringA, ringB = (x0 + 20, 330), (x0 - 40, 540)
    g0, g1 = B(*nz), B(x0 - 30, 480)
    out.append(f'<line x1="{g0[0]}" y1="{g0[1]}" x2="{g1[0]}" y2="{g1[1]}" stroke="#335" stroke-width="16" stroke-opacity="0.3" stroke-linecap="round"{st}/>')
    for (rx, rz), lab in ((ringA, 'ring A'), (ringB, 'ring B + roll lock')):
        bb = B(rx, RZ - 60); r = B(rx, rz)
        out.append(f'<rect x="{bb[0]-10}" y="{bb[1]-6}" width="20" height="30" fill="#ddd" stroke="#666"{st}/>')
        out.append(f'<line x1="{bb[0]}" y1="{bb[1]+24}" x2="{r[0]}" y2="{r[1]}" stroke="#666" stroke-dasharray="3 2"{st}/>')
        out.append(f'<circle cx="{r[0]}" cy="{r[1]}" r="7" fill="none" stroke="#2a6" stroke-width="2"{st}/>')
        if not ghost: out.append(f'<text x="{r[0]+10}" y="{r[1]+4}" fill="#2a6">{lab} (balancer)</text>')
    # umbilical: from grip base up to saddle on trolley at x0+200, z=1150, then down to cart at x0+700
    gb = B(x0 - 30, 480); sd = B(x0 + 200, 1160); sd2 = B(x0 + 260, 1150); cart = B(x0 + 750, 300)
    out.append(f'<path d="M{gb[0]},{gb[1]} C{B(x0-40, 900)[0]},{B(x0-40,900)[1]} {B(x0+60,1170)[0]},{B(x0+60,1170)[1]} {sd[0]},{sd[1]}" fill="none" stroke="#b33" stroke-width="3"{st}/>')
    out.append(f'<path d="M{sd[0]},{sd[1]} C{B(x0+500,1120)[0]},{B(x0+500,1120)[1]} {B(x0+720,800)[0]},{B(x0+720,800)[1]} {cart[0]},{cart[1]}" fill="none" stroke="#b33" stroke-width="3"{st}/>')
    out.append(f'<rect x="{sd[0]-8}" y="{sd[1]-4}" width="{sd2[0]-sd[0]+16}" height="8" fill="#e8b0b0" stroke="#b33"{st}/>')
    return '\n'.join(out)
o.append(carrier(0, False))
o.append(carrier(420, True))
lx, ly = B(210, 1200); o.append(f'<text x="{lx}" y="{ly}" fill="#b33">umbilical saddle on the trolley (R ≥ 350)</text>')
a1, b1 = B(60, 700); a2, b2 = B(400, 700)
o.append(f'<line x1="{a1}" y1="{b1}" x2="{a2}" y2="{b2}" stroke="#333" stroke-width="2" marker-end="url(#a)"/><text x="{a1}" y="{b1-8}">park: lift ~30 mm, roll ~420 mm</text>')
px, py = B(430, 200); o.append(f'<text x="{px}" y="{py}">parked (faded): lines stay vertical,</text><text x="{px}" y="{py+14}">no pendulum pull back over the tube;</text><text x="{px}" y="{py+28}">tube column open for loading</text>')
o.append(f'<text x="12" y="{H-30}">Without the trolley: a 15–20 N gun on 0.8–1.2 m lines pulled 300 mm aside is pulled back with 4–8 N and must be hooked; two separate anchors also yaw it.</text>')
o.append(f'<text x="12" y="{H-14}">Roll on the rings is not free in practice: the proxy CG sits 85 mm off the grip axis (0.58–1.01 N·m for 0.8–1.4 kg at the true pose). Ring B carries a roll lock.</text>')
o.append('</svg>')
open('../sketches/x2-trolley-parked-carrier.svg', 'w').write('\n'.join(o))
print('ok')
