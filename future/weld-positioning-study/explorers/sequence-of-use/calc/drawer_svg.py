"""Side-view sketch for idea B (gun fixed; rotator on a drawer with end ramps into kinematic seats)."""
import math
from proxy import *
from lid_calc import hull  # reuse hull (lid_calc prints on import; harmless)
W, HGT = 900, 720
X0, Z0 = 330, 660
def sv(x, zb): return (X0 + x, Z0 - zb)
DROP, RAMP, TRAVEL = 20.0, 60.0, 260.0
def gun(style):
    o = []
    def P(l):
        q = pose(l); return sv(q[0], q[2] - BENCH_Z)
    c = [P((x, y, z)) for x in (-17, 17) for y in (-17, 17) for z in (118, 253)]
    o.append('<polygon points="%s" %s/>' % (' '.join(f'{a:.1f},{b:.1f}' for a, b in hull([(round(a,1), round(b,1)) for a, b in c])), style))
    g = []
    for t in (0, 1):
        cc = [0, -25 - 86 * t, 172 + 60 * t]
        for dx in (-15, 15):
            for dz in (-14, 14): g.append(P((cc[0] + dx, cc[1], cc[2] + dz)))
    o.append('<polygon points="%s" %s/>' % (' '.join(f'{a:.1f},{b:.1f}' for a, b in hull([(round(a,1), round(b,1)) for a, b in g])), style))
    a, b = P((0, 0, 0)), P((0, 0, 118))
    o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#555" stroke-width="12" stroke-linecap="round" opacity="0.55"/>')
    w0, w1 = P((0, 0, -CL)), P((0, -24.7, 87.1))
    o.append(f'<line x1="{w0[0]:.1f}" y1="{w0[1]:.1f}" x2="{w1[0]:.1f}" y2="{w1[1]:.1f}" stroke="#b36b00" stroke-width="1.6"/>')
    return '\n'.join(o), P
def tube(cx, dz, style, fill):
    o = []
    for sgn in (-1, 1):
        x = cx + (R_IN if sgn > 0 else -R_OUT)
        a, b = sv(x, RIM - BENCH_Z - dz)
        o.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{WALL:.2f}" height="{RIM:.1f}" fill="{fill}" {style}/>')
    a, b = sv(cx - R_IN, CAP_TOP - BENCH_Z - dz)
    o.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="{2*R_IN:.1f}" height="{RECESS:.2f}" fill="{fill}" {style}/>')
    a, b = sv(cx - 150, 36 - dz + 18)
    o.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="300" height="12" fill="none" {style}/>')
    a, b = sv(cx - 75, -BENCH_Z - dz + 18)
    o.append(f'<rect x="{a:.1f}" y="{b:.1f}" width="150" height="{-BENCH_Z-36:.1f}" fill="none" {style}/>')
    return '\n'.join(o)
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{HGT}" viewBox="0 0 {W} {HGT}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Gun stays, work travels (idea B) — side view along the tangent</text>',
     '<text x="12" y="36">Gun fixed to a portal for the whole session. Rotator rides a carriage 20 mm low, then climbs end ramps into three ball-in-vee seats.</text>',
     '<text x="12" y="50">Approach must be along −X (from the weld-station side, within ~±20°): only then is the wire tip inside the bore before the rim arrives. 1 px = 1 mm.</text>']
by = Z0
s.append(f'<line x1="10" y1="{by}" x2="{W-10}" y2="{by}" stroke="#333" stroke-width="2"/><text x="14" y="{by+14}">bench / subplate</text>')
# base plate with tracks
a, b = sv(-200, 18); s.append(f'<rect x="{a}" y="{b}" width="{TRAVEL+420}" height="18" fill="#e3e0d6" stroke="#888"/>')
# ramp profile (for one ball track), drawn at ball height
pts = [(-170 + TRAVEL + 40, 18), (-170 + RAMP, 18), (-170, 18 + DROP)]
# carriage positions
s.append(tube(TRAVEL, DROP, 'stroke="#577" stroke-dasharray="4 3"', '#dfeaea'))
s.append(tube(0, 0, 'stroke="#577"', '#8aa'))
g, P = gun('fill="#c9d6ee" stroke="#335"')
s.append(g)
# portal
hx0, hy0 = sv(-230, 0); hx1, _ = sv(-230, 0)
top = sv(0, 540)[1]
s.append(f'<rect x="{hx0}" y="{top}" width="20" height="{by-top}" fill="#ccc" stroke="#777"/>')
a, b = sv(-230, 540); s.append(f'<rect x="{a}" y="{b}" width="260" height="16" fill="#ccc" stroke="#777"/>')
c = P((0, 0, 185.5))
s.append(f'<line x1="{c[0]:.1f}" y1="{c[1]:.1f}" x2="{c[0]:.1f}" y2="{b+16}" stroke="#335" stroke-width="5" opacity="0.6"/>')
s.append(f'<text x="{a+4}" y="{b-6}">fixed portal on the same subplate (fine-aim stage + shell hang from it)</text>')
# ramp detail inset
ix, iy = 560, 130
s.append(f'<rect x="{ix-10}" y="{iy-40}" width="330" height="150" fill="#fff" stroke="#aaa"/>')
s.append(f'<text x="{ix}" y="{iy-24}" font-weight="bold">one ball track, 2:1 vertical exaggeration</text>')
s.append(f'<polyline points="{ix},{iy+80} {ix+180},{iy+80} {ix+240},{iy+80-2*DROP} {ix+262},{iy+80-2*DROP} {ix+270},{iy+80-2*DROP+8} {ix+278},{iy+80-2*DROP} {ix+300},{iy+80-2*DROP}" fill="none" stroke="#333" stroke-width="2"/>')
s.append(f'<circle cx="{ix+120}" cy="{iy+72}" r="8" fill="#666"/><circle cx="{ix+270}" cy="{iy+80-2*DROP-4}" r="8" fill="#666"/>')
s.append(f'<text x="{ix}" y="{iy+100}">travel (low, 20 mm below weld height)</text>')
s.append(f'<text x="{ix+170}" y="{iy+60}">60 mm ramp</text><text x="{ix+230}" y="{iy+14}">vee seat</text>')
s.append(f'<text x="{ix}" y="{iy+116}">push ≈ m·g·20/60 ≈ 20–25 N for ~6 kg (estimate) + friction</text>')
# arrow
a, b = sv(TRAVEL - 60, 300); a2, _ = sv(80, 300)
s.append(f'<line x1="{a}" y1="{b}" x2="{a2}" y2="{b}" stroke="#2a7" stroke-width="2" marker-end="url(#ar)"/><text x="{a2+10}" y="{b-6}" fill="#2a7">push in; last 60 mm rises 20 mm</text>')
s.insert(1, '<defs><marker id="ar" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#2a7"/></marker></defs>')
a, b = sv(TRAVEL - 60, 250)
s.append(f'<text x="{a-40}" y="{b}" fill="#577">LOAD position (dashed): full access to nest, plate, indicator, float</text>')
s.append(f'<text x="12" y="{HGT-12}">Moves with the carriage: rotator, motor + driver cable, copper shoe + work lead, purge hose (2nd closure). Never moves: gun, umbilical, wire conduit, camera.</text>')
s.append('</svg>')
open('../sketches/drawer-lift.svg', 'w').write('\n'.join(s))
print('ok')
