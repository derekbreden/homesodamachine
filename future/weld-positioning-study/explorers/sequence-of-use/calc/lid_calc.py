"""Pose: scene hole DIAL 30 (true opening pose) since the wave-3 fix. Park angle 88 deg (CG passes
over the hinge at ~71.5 deg at dial 30; it was ~58 deg at dial 65). Seats drawn where who-moves-what
moved them (behind the station: pair at x=170, y=+-110; rear ball at x=300; latch at the rear).
Lid (hinged carrier) numbers for one chosen hinge, plus a side-view SVG built from the proxy.

Chosen hinge: axis parallel to the tangent (Y), 200 mm from the tube axis on the weld-station
(+X) side, 60 mm above the rim (298 mm above the bench on current feet). From lid_swing2.py:
collision-free for the proxy, lift-clear at ~20 deg, column clear to rim+320 at ~72 deg.
Assumed masses [Agent estimates, not measured]: gun 1.0 kg at housing centre; shell+stage 0.4 kg
at the same point; lid frame 0.8 kg at its own centroid (taken half way hinge->gun).
"""
import math
from proxy import *

H = (200.0, 0.0, RIM + 60.0)
U = (0.0, 1.0, 0.0)
pts = {
    'wire tip / dot': (0, 0, -CL), 'nozzle tip': (0, 0, 0), 'lens ring': (0, 0, 100),
    'housing centre (CG proxy)': (0, 0, 185.5), 'housing back': (0, 0, 253), 'grip base (cable exit)': GB,
}
def at(p, deg):
    return rot_about_axis(pose(p), H, U, math.radians(deg))
print('hinge (tube frame)', H, ' above bench', round(H[2] - BENCH_Z, 1))
for deg in (0, 20.5, 45, 72.5, 88):
    print(f'-- lid angle {deg} deg')
    for k, p in pts.items():
        q = at(p, deg)
        print(f'   {k:28s} x={q[0]:7.1f} y={q[1]:7.1f} z_bench={q[2]-BENCH_Z:7.1f} r_axis={math.hypot(q[0], q[1]):6.1f}')
cg = pose((0, 0, 185.5))
v = (cg[0] - H[0], cg[2] - H[2])
over = math.degrees(math.atan2(-v[0], v[1])) if v[1] > 0 else None
print('CG rel hinge (x,z)', [round(t, 1) for t in v])
# angle at which CG passes vertically over the hinge (x rel -> 0) for sign +1 rotation about +Y
for d10 in range(0, 1800):
    d = d10 / 10
    q = at((0, 0, 185.5), d)
    if q[0] - H[0] >= 0:
        print('CG passes over hinge at', d, 'deg'); break
m_gun, m_shell, m_lid = 1.0, 0.4, 0.8
lever_gun = H[0] - cg[0]
lid_c = ((H[0] + cg[0]) / 2)
M = 9.81 * ((m_gun + m_shell) * lever_gun + m_lid * (H[0] - lid_c)) / 1000
print(f'closing moment at 0 deg about hinge: {M:.2f} N*m (masses assumed)')
# grip base travel
g0 = at(GB, 0); g1 = at(GB, 88)
print('grip base moves', round(math.dist(g0, g1), 1), 'mm between closed and 88 deg; radius from hinge axis',
      round(math.hypot(g0[0] - H[0], g0[2] - H[2]), 1))

# ---------- SVG side view (looking from -Y toward +Y; X right, Z up; bench coords) ----------
S = 1.0
W, HGT = 860, 720
X0, Z0 = 300, 680
def sv(x, zb):
    return (X0 + x * S, Z0 - zb * S)
def hull(ps):
    ps = sorted(set(ps))
    if len(ps) < 3: return ps
    def cr(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in ps:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(ps):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]
def gun_svg(deg, style):
    out = []
    def P(local):
        q = at(local, deg); return sv(q[0], q[2] - BENCH_Z)
    # housing hull
    corners = [P((x, y, z)) for x in (-17, 17) for y in (-17, 17) for z in (118, 253)]
    hp = hull([(round(a, 1), round(b, 1)) for a, b in corners])
    out.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in hp)}" {style}/>')
    # grip hull
    g = []
    for t in (0, 1):
        c = [0, -25 + t * (-86), 172 + t * 60]
        for dx in (-15, 15):
            for dz in (-14, 14):
                g.append(P((c[0] + dx, c[1], c[2] + dz)))
    gp = hull([(round(a, 1), round(b, 1)) for a, b in g])
    out.append(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in gp)}" {style}/>')
    a, b = P((0, 0, 0)), P((0, 0, 118))
    out.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#555" stroke-width="12" stroke-linecap="round" opacity="0.55"/>')
    w0, w1 = P((0, 0, -CL)), P((0, -24.7, 87.1))
    out.append(f'<line x1="{w0[0]:.1f}" y1="{w0[1]:.1f}" x2="{w1[0]:.1f}" y2="{w1[1]:.1f}" stroke="#b36b00" stroke-width="1.6"/>')
    return '\n'.join(out), P
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
       '<rect width="100%" height="100%" fill="#fbfbf8"/>',
       '<text x="12" y="20" font-size="14" font-weight="bold">Lid carrier (idea A) — side view along the tangent, closed and parked</text>',
       '<text x="12" y="36">Proxy at Derek\'s opening pose (grip 45°, hole DIAL 30, vertical −15°); body lies toward −Y (foreshortened here). 1 px = 1 mm.</text>']
# bench
bx0, by = sv(-300, 0)
svg.append(f'<line x1="10" y1="{by}" x2="{W-10}" y2="{by}" stroke="#333" stroke-width="2"/><text x="14" y="{by+14}">bench</text>')
# rotator: feet 24, base 12 (assume centred on tube axis), table+nest simplified to rim seat at tube z=0
fx, fy = sv(-150, 36); svg.append(f'<rect x="{fx}" y="{fy}" width="300" height="12" fill="#d9d4c7" stroke="#777"/>')
for x in (-140, 120):
    a, b = sv(x, 24); svg.append(f'<rect x="{a}" y="{b}" width="20" height="24" fill="#d9d4c7" stroke="#777"/>')
a, b = sv(-75, -BENCH_Z); svg.append(f'<rect x="{a}" y="{b}" width="150" height="{-BENCH_Z-36:.1f}" fill="#ece8dc" stroke="#999" stroke-dasharray="3 2"/>')
svg.append(f'<text x="{sv(-150,40)[0]}" y="{sv(-150,40)[1]-40}">rotator (turntable, nest; motor tower not drawn)</text>')
# tube walls and plate (section)
for sgn in (-1, 1):
    a, b = sv(sgn * R_IN if sgn > 0 else -R_OUT, RIM - BENCH_Z)
    svg.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{WALL:.2f}" height="{RIM:.1f}" fill="#8aa" stroke="#577"/>')
a, b = sv(-R_IN, CAP_TOP - BENCH_Z); svg.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{2*R_IN:.1f}" height="{RECESS:.2f}" fill="#9bb" stroke="#577"/>')
svg.append(f'<text x="{sv(-60, CAP_TOP-BENCH_Z-20)[0]}" y="{sv(-60, CAP_TOP-BENCH_Z-20)[1]}">end plate, 6.35 below rim</text>')
# column that must be clear for loading
a, b = sv(-95, RIM + 320 - BENCH_Z)
svg.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="190" height="320" fill="none" stroke="#2a7" stroke-dasharray="6 4"/>')
svg.append(f'<text x="{a+4:.1f}" y="{b+14:.1f}" fill="#2a7">loading column r&lt;95 to rim+320</text>')
# hinge
hx, hy = sv(H[0], H[2] - BENCH_Z)
svg.append(f'<circle cx="{hx}" cy="{hy}" r="7" fill="#fff" stroke="#000" stroke-width="2"/><text x="{hx+10}" y="{hy+4}">hinge ∥ tangent (Y)</text>')
svg.append(f'<text x="{hx+10}" y="{hy+18}">200 from axis, 298 above bench</text>')
# hinge post
svg.append(f'<rect x="{hx-10}" y="{hy}" width="20" height="{by-hy}" fill="#ccc" stroke="#777"/>')
svg.append(f'<text x="{hx+14}" y="{by-30}">post on common subplate</text>')
# gun closed
g_closed, P0f = gun_svg(0, 'fill="#c9d6ee" stroke="#335" stroke-width="1"')
svg.append(g_closed)
# lid arm closed: hinge -> housing centre
c0 = P0f((0, 0, 185.5))
svg.append(f'<line x1="{hx}" y1="{hy}" x2="{c0[0]:.1f}" y2="{c0[1]:.1f}" stroke="#335" stroke-width="5" opacity="0.6"/>')
# gun parked 88
g_park, P1f = gun_svg(88, 'fill="none" stroke="#335" stroke-dasharray="4 3"')
svg.append(g_park)
c1 = P1f((0, 0, 185.5))
svg.append(f'<line x1="{hx}" y1="{hy}" x2="{c1[0]:.1f}" y2="{c1[1]:.1f}" stroke="#335" stroke-width="5" opacity="0.25"/>')
svg.append(f'<text x="{c1[0]+60:.1f}" y="{c1[1]+40:.1f}">parked at 88° (dashed):</text><text x="{c1[0]+60:.1f}" y="{c1[1]+54:.1f}">CG past the hinge; lid rests open</text>')
# wire tip path
path = [P0f((0, 0, -CL))]
for d in range(1, 89, 2):
    q = at((0, 0, -CL), d); path.append(sv(q[0], q[2] - BENCH_Z))
svg.append('<polyline points="' + ' '.join(f'{a:.1f},{b:.1f}' for a, b in path) + '" fill="none" stroke="#b36b00" stroke-dasharray="2 2"/>')
t0 = P0f((0, 0, -CL))
svg.append(f'<text x="{t0[0]+8:.1f}" y="{t0[1]+22:.1f}" fill="#b36b00">wire tip leaves the corner up and inward</text>')
# kinematic seat symbols (schematic positions)
for (x, z, lab) in ((170, RIM + 70, 'vee pair ±Y (x 170)'), (300, RIM + 70, 'rear vee + latch')):
    a, b = sv(x, z - BENCH_Z)
    svg.append(f'<polygon points="{a-9},{b-8} {a+9},{b-8} {a},{b+3}" fill="#e7c" stroke="#704"/><circle cx="{a}" cy="{b-11}" r="5" fill="#666"/>')
    svg.append(f'<text x="{a-60 if x < 200 else a+12}" y="{b+(34 if x < 200 else 18)}" fill="#704">{lab}</text>')
svg.append(f'<text x="12" y="{HGT-12}">Closed: three balls in vees behind the station + latch (CG lies outside the triangle, so the latch is load-bearing); hinge pins in tight slots.</text>')
svg.append('</svg>')
open('../sketches/lid-side-view.svg', 'w').write('\n'.join(svg))
print('wrote sketches/lid-side-view.svg')
