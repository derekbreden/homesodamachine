"""Wave 3: mirrored for table ccw (the scene's wire approaches from -Y, so the arriving side is -Y);
pose at hole DIAL 30. Schematic of idea C (rim-riding saddle). Plan view to scale (2 px/mm) for the tube and roller
angles; saddle outline and section are schematic."""
import math
from proxy import R_IN, R_OUT, pose, CL
S = 1.6
W, H = 980, 780
cx, cy = 260, 250
def P(x, y): return (cx + S * x, cy - S * y)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Rim-riding saddle (idea C) — plan from above (left, to scale) and radial section (right, schematic)</text>',
     '<text x="12" y="36">Contacts on the ARRIVING (cold) side. At the true pose the wire comes from −Y, so the table turns ccw and the contacts sit on −Y, under the wire and barrel.</text>']
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_OUT}" fill="#dfe9e9" stroke="#577"/>')
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_IN}" fill="#cfdede" stroke="#577"/>')
o.append(f'<text x="{cx-40}" y="{cy+6}">end plate face</text>')
d = P(R_IN, 0); o.append(f'<circle cx="{d[0]}" cy="{d[1]}" r="4" fill="#d00"/><text x="{d[0]+8}" y="{d[1]+14}" fill="#d00">dot (+X)</text>')
# rotation arrow (cw from above): arc from theta=120 to 70 at r=40
arc = [P(40 * math.cos(math.radians(t)), 40 * math.sin(math.radians(t))) for t in range(-150, -60, 5)]
o.append('<polyline points="%s" fill="none" stroke="#333" stroke-width="1.5" marker-end="url(#a)"/>' % ' '.join(f'{a:.1f},{b:.1f}' for a, b in arc))
o.append(f'<text x="{P(-35,-52)[0]}" y="{P(-35,-52)[1]}">table turns ccw</text>')
# gun plan projection (proxy): nozzle->lens->housing->grip base
pts = [pose(p) for p in ((0, 0, 0), (0, 0, 118), (0, 0, 253))]
o.append('<polyline points="%s" fill="none" stroke="#335" stroke-width="10" opacity="0.35" stroke-linecap="round"/>' % ' '.join(f'{P(q[0], q[1])[0]:.1f},{P(q[0], q[1])[1]:.1f}' for q in pts))
g = pose((0, -118, 237)); gs = pose((0, -25, 172))
o.append(f'<line x1="{P(gs[0],gs[1])[0]:.1f}" y1="{P(gs[0],gs[1])[1]:.1f}" x2="{P(g[0],g[1])[0]:.1f}" y2="{P(g[0],g[1])[1]:.1f}" stroke="#335" stroke-width="14" opacity="0.25" stroke-linecap="round"/>')
o.append(f'<text x="{P(g[0],g[1])[0]+10:.1f}" y="{P(g[0],g[1])[1]:.1f}">grip / cable exit (proxy pose)</text>')
# CG marker
cgq = pose((0, 0, 185.5)); cgp = P(cgq[0], cgq[1])
o.append(f'<circle cx="{cgp[0]:.1f}" cy="{cgp[1]:.1f}" r="6" fill="none" stroke="#000"/><line x1="{cgp[0]-8:.1f}" y1="{cgp[1]:.1f}" x2="{cgp[0]+8:.1f}" y2="{cgp[1]:.1f}" stroke="#000"/><text x="{cgp[0]+10:.1f}" y="{cgp[1]+4:.1f}">gun CG (proxy)</text>')
# rollers
def roller_rim(th, lab):
    x, y = (R_IN + R_OUT) / 2 * math.cos(math.radians(th)), (R_IN + R_OUT) / 2 * math.sin(math.radians(th))
    a, b = P(x, y)
    o.append(f'<g transform="translate({a:.1f},{b:.1f}) rotate({-th:.1f})"><rect x="-11" y="-3.5" width="22" height="7" fill="#e7c" stroke="#704"/></g>')
    o.append(f'<text x="{a+8:.1f}" y="{b-8:.1f}" fill="#704">{lab}</text>')
def roller_od(th, r, lab, dash=False):
    rr = R_OUT + r
    a, b = P(rr * math.cos(math.radians(th)), rr * math.sin(math.radians(th)))
    o.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{S*r:.1f}" fill="none" stroke="#704" {"stroke-dasharray=\"3 2\"" if dash else ""}/>')
    o.append(f'<text x="{a+S*r+3:.1f}" y="{b+4:.1f}" fill="#704">{lab}</text>')
roller_rim(-22, 'R1'); roller_rim(-52, 'R2')
roller_od(-22, 11, 'O1'); roller_od(-52, 11, 'O2'); roller_od(-37, 11, 'O3 (lower)', True)
# saddle outline (schematic arc band outside the tube)
band = [P(r * math.cos(math.radians(t)), r * math.sin(math.radians(t))) for r, rng in ((100, range(-10, -64, -3)), (78, range(-63, -9, 3))) for t in rng]
o.append('<polygon points="%s" fill="#f3e7c9" fill-opacity="0.5" stroke="#a70" stroke-dasharray="5 3"/>' % ' '.join(f'{a:.1f},{b:.1f}' for a, b in band))
a, b = P(95, -40); o.append(f'<text x="{a:.1f}" y="{b:.1f}" fill="#a70">saddle (printed), bridges the rim below rim+35</text>')
# tether tangential at theta 60
t0 = P(100 * math.cos(math.radians(-60)), 100 * math.sin(math.radians(-60)))
t1 = P(100 * math.cos(math.radians(60)) - 60 * math.sin(math.radians(60)) * -1, 100 * math.sin(math.radians(60)) + 60 * math.cos(math.radians(60)) * -1)
t1 = P(100 * math.cos(math.radians(-60)) + 75, 100 * math.sin(math.radians(-60)) - 45)
o.append(f'<line x1="{t0[0]:.1f}" y1="{t0[1]:.1f}" x2="{t1[0]:.1f}" y2="{t1[1]:.1f}" stroke="#333" stroke-width="2"/><circle cx="{t1[0]:.1f}" cy="{t1[1]:.1f}" r="4" fill="#fff" stroke="#333"/>')
o.append(f'<text x="{t1[0]-60:.1f}" y="{t1[1]+20:.1f}">tether to frame: takes roller drag only</text>')
# preload arrow radial inward at theta 37
pa = P(135 * math.cos(math.radians(-30)), 135 * math.sin(math.radians(-30))); pb = P(108 * math.cos(math.radians(-30)), 108 * math.sin(math.radians(-30)))
o.append(f'<line x1="{pa[0]:.1f}" y1="{pa[1]:.1f}" x2="{pb[0]:.1f}" y2="{pb[1]:.1f}" stroke="#2a7" stroke-width="2.5" marker-end="url(#a)"/><text x="{pa[0]+10:.1f}" y="{pa[1]+14:.1f}" fill="#2a7">radial preload</text>')
o.append(f'<text x="12" y="{H-50}">Five contacts: R1,R2 on the rim top (height, tilt about radius); O1,O2 on the OD near the rim (radius, yaw); O3 lower on the OD (tilt about the tangent).</text>')
o.append(f'<text x="12" y="{H-34}">Sixth freedom (along the circumference) held by the tether. Weight carried by a balancer; net load chosen to keep all five contacts loaded.</text>')
o.append(f'<text x="12" y="{H-18}">Angles to scale: R/O at −22° and −52°. The wire crosses over the OD near −54° at ~rim+49 and the barrel near −81° at ~rim+76 (proxy, dial 30).</text>')
# section (schematic), right side
sx, sy = 640, 150
o.append(f'<text x="{sx}" y="{sy-58}" font-weight="bold">Radial section through O3 (schematic, ~3 px/mm)</text>')
k = 3
wall_x = sx + 120
o.append(f'<rect x="{wall_x}" y="{sy+40}" width="{1.65*k:.1f}" height="{120*k/1.5:.1f}" fill="#8aa" stroke="#577"/>')
o.append(f'<rect x="{wall_x-150}" y="{sy+40+6.35*k:.1f}" width="150" height="{6.35*k:.1f}" fill="#9bb" stroke="#577"/>')
o.append(f'<text x="{wall_x-146}" y="{sy+40+6.35*k+14:.1f}">end plate (inside)</text>')
o.append(f'<text x="{wall_x+10}" y="{sy+36}">rim</text>')
# rim roller on top
o.append(f'<circle cx="{wall_x+2.5}" cy="{sy+40-11*k/2:.1f}" r="{11*k/2:.1f}" fill="none" stroke="#704"/><text x="{wall_x-60}" y="{sy+20}" fill="#704">R (rim top)</text>')
# OD rollers O (upper) and O3 (lower)
for dz, lab in ((6, 'O1/O2 (upper OD)'), (30, 'O3 (lower OD)')):
    o.append(f'<circle cx="{wall_x+1.65*k+11*k:.1f}" cy="{sy+40+dz*k:.1f}" r="{11*k:.1f}" fill="none" stroke="#704"/><text x="{wall_x+1.65*k+22*k+4:.1f}" y="{sy+44+dz*k:.1f}" fill="#704">{lab}</text>')
# saddle C
o.append(f'<path d="M{wall_x-20},{sy+5} L{wall_x+95},{sy+5} L{wall_x+95},{sy+40+44*k}" fill="none" stroke="#a70" stroke-width="4" opacity="0.6"/>')
o.append(f'<text x="{wall_x+100}" y="{sy+10}" fill="#a70">saddle body</text>')
o.append(f'<line x1="{wall_x+170}" y1="{sy+120}" x2="{wall_x+105}" y2="{sy+120}" stroke="#2a7" stroke-width="2.5" marker-end="url(#a)"/><text x="{wall_x+120}" y="{sy+112}" fill="#2a7">inward</text>')
o.append(f'<line x1="{wall_x+2}" y1="{sy-40}" x2="{wall_x+2}" y2="{sy-6}" stroke="#2a7" stroke-width="2.5" marker-end="url(#a)"/><text x="{wall_x+8}" y="{sy-28}" fill="#2a7">down (net of balancer)</text>')
o.append(f'<text x="{sx-40}" y="{sy+300}">At dial 65 the CG sat over the tube centre and lifted O3. At the true pose</text>')
o.append(f'<text x="{sx-40}" y="{sy+314}">(dial 30) it sits at (−30, −108), beyond R2 and outboard: a balancer</text>')
o.append(f'<text x="{sx-40}" y="{sy+328}">hooked at the CG carries it; a small preload goes between R1 and R2.</text>')
o.append('</svg>')
open('../sketches/rim-saddle.svg', 'w').write('\n'.join(o))
print('ok')
