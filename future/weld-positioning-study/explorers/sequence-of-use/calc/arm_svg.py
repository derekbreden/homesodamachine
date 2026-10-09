"""Monitor-arm session sketch (wave 3). Plan: tube and proxy gun at the TRUE opening pose (hole dial 30)
to scale; arm, dock, cradle and umbilical support positions are proposals, drawn to the same scale.
Right panel: the shell interface (bail at the CG, ball plate, latch, trigger presser), schematic."""
import math
from proxy import *
S = 0.9
W, H = 1180, 960
cx, cy = 420, 430
def P(x, y): return (cx + S * x, cy - S * y)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="#333"/></marker></defs>',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">Monitor arm through a session: the arm carries, a cradle parks, a dock locates (plan, 0.9 px/mm)</text>',
     '<text x="12" y="36">Tube and proxy gun to scale at Derek\'s opening pose (grip 45, hole dial 30, vertical −15). Arm, dock, cradle and umbilical support are proposals. Updated wave 5: saddle at the natural apex, operator on −X.</text>']
# bench outline
a, b = P(-420, 380); a2, b2 = P(520, -360)
o.append(f'<rect x="{a}" y="{b}" width="{a2-a}" height="{b2-b}" fill="none" stroke="#bbb" stroke-dasharray="6 4"/><text x="{a+6}" y="{b2-6}" fill="#999">bench front edge</text>')
# rotator base outline (assumed centred)
a, b = P(-150, 125); o.append(f'<rect x="{a}" y="{b}" width="{300*S}" height="{250*S}" fill="#eee" stroke="#aaa"/><text x="{a+4}" y="{b+12}" fill="#888">rotator base 300 × 250 (assumed centred)</text>')
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_OUT}" fill="#dfeaea" stroke="#577"/><circle cx="{cx}" cy="{cy}" r="{S*95}" fill="none" stroke="#2a7" stroke-dasharray="5 4"/>')
a, b = P(-60, 98); o.append(f'<text x="{a}" y="{b}" fill="#2a7">loading column r 95</text>')
d = P(R_IN, 0); o.append(f'<circle cx="{d[0]}" cy="{d[1]}" r="4" fill="#d00"/><text x="{d[0]+6}" y="{d[1]-6}" fill="#d00">dot</text>')
# gun plan (docked)
def gun(style, deg=0):
    pts = [pose(p) for p in ((0, 0, 0), (0, 0, 118), (0, 0, 253))]
    out = ['<polyline points="%s" fill="none" stroke="#335" stroke-width="14" %s stroke-linecap="round"/>' % (' '.join(f'{P(q[0], q[1])[0]:.1f},{P(q[0], q[1])[1]:.1f}' for q in pts), style)]
    gs, gb = pose((0, -25, 172)), pose(GB)
    out.append(f'<line x1="{P(gs[0],gs[1])[0]:.1f}" y1="{P(gs[0],gs[1])[1]:.1f}" x2="{P(gb[0],gb[1])[0]:.1f}" y2="{P(gb[0],gb[1])[1]:.1f}" stroke="#335" stroke-width="18" {style} stroke-linecap="round"/>')
    return '\n'.join(out)
o.append(gun('stroke-opacity="0.35"'))
cg = pose((0, 0, 185.5)); c = P(cg[0], cg[1])
o.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="6" fill="#fff" stroke="#000"/><text x="{c[0]-150:.1f}" y="{c[1]-8:.1f}">bail hook above CG (−30, −108)</text>')
gb = pose(GB); g = P(gb[0], gb[1]); o.append(f'<text x="{g[0]+14:.1f}" y="{g[1]+4:.1f}">grip base / cable exit (−1, −234)</text>')
# dock post (vees) under the body, forward of the grip
dp = P(-45, -165)
o.append(f'<rect x="{dp[0]-16}" y="{dp[1]-16}" width="32" height="32" fill="#cfe9d6" stroke="#2a6"/>')
for ang in (90, 210, 330):
    bx, by = -45 + 55 * math.cos(math.radians(ang)), -165 + 55 * math.sin(math.radians(ang))
    q = P(bx, by); o.append(f'<polygon points="{q[0]-6},{q[1]-5} {q[0]+6},{q[1]-5} {q[0]},{q[1]+5}" fill="#e7c" stroke="#704"/>')
o.append(f'<text x="{dp[0]-210}" y="{dp[1]+34}" fill="#2a6">DOCK: three vees on a post from the subplate,</text><text x="{dp[0]-210}" y="{dp[1]+48}" fill="#2a6">~80 mm above the rim; latch; rim flag; Bowden lever</text>')
# arm base and links (docked and parked)
base = (40, 360)
elbow_d = (-180, 170)
head_d = (cg[0], cg[1] + 0)
park = (330, 250)
elbow_p = (250, 380)
def link(p1, p2, st):
    a, b = P(*p1); c2, d2 = P(*p2)
    return f'<line x1="{a:.1f}" y1="{b:.1f}" x2="{c2:.1f}" y2="{d2:.1f}" stroke="#555" stroke-width="9" stroke-linecap="round" {st}/>'
o.append(link(base, elbow_d, 'stroke-opacity="0.8"')); o.append(link(elbow_d, head_d, 'stroke-opacity="0.8"'))
o.append(link(base, elbow_p, 'stroke-opacity="0.25"')); o.append(link(elbow_p, park, 'stroke-opacity="0.25"'))
b0 = P(*base); o.append(f'<rect x="{b0[0]-12}" y="{b0[1]-12}" width="24" height="24" fill="#999" stroke="#555"/><text x="{b0[0]+16}" y="{b0[1]-6}">arm clamp (back edge)</text>')
for p_ in (elbow_d, elbow_p):
    q = P(*p_); o.append(f'<circle cx="{q[0]:.1f}" cy="{q[1]:.1f}" r="6" fill="#fff" stroke="#555"/>')
lp = P(-175, 190); o.append(f'<text x="{lp[0]-110:.1f}" y="{lp[1]-8:.1f}">gas-spring arm, docked (links ~200 above rim)</text>')
# park cradle
pk = P(*park); o.append(f'<rect x="{pk[0]-26}" y="{pk[1]-18}" width="52" height="36" rx="6" fill="#f3e7c9" stroke="#a70"/>')
o.append(f'<text x="{pk[0]+32}" y="{pk[1]-4}" fill="#a70">PARK CRADLE: nozzle cap,</text><text x="{pk[0]+32}" y="{pk[1]+10}" fill="#a70">stickout gauge, positive stop</text>')
# umbilical support (fixed) and loop
us = P(-90, -470)
o.append(f'<circle cx="{us[0]}" cy="{us[1]}" r="9" fill="#e8b0b0" stroke="#b33"/><text x="{us[0]+14}" y="{us[1]+4}" fill="#b33">umbilical saddle at the cable\'s natural apex</text><text x="{us[0]+14}" y="{us[1]+18}" fill="#b33">(~420–450 above bench, on a stand past the bench edge;</text><text x="{us[0]+14}" y="{us[1]+32}" fill="#b33">wave-3 drawing had the stale dial-65 figure of 680)</text>')
o.append(f'<path d="M{g[0]:.1f},{g[1]:.1f} Q{P(-30,-420)[0]:.1f},{P(-30,-420)[1]:.1f} {us[0]},{us[1]}" fill="none" stroke="#b33" stroke-width="3"/>')
o.append(f'<path d="M{us[0]},{us[1]} Q{P(-300,-560)[0]:.1f},{P(-300,-560)[1]:.1f} {P(-440,-420)[0]:.1f},{P(-440,-420)[1]:.1f}" fill="none" stroke="#b33" stroke-width="3" stroke-dasharray="6 3"/>')
o.append(f'<text x="{P(-460,-400)[0]:.1f}" y="{P(-460,-400)[1]:.1f}" fill="#b33">to cart</text>')
# tube exit
te1, te2 = P(-70, 0), P(-280, 0)
o.append(f'<line x1="{te1[0]}" y1="{te1[1]}" x2="{te2[0]}" y2="{te2[1]}" stroke="#2a7" stroke-width="2.5" marker-end="url(#a)"/><text x="{te2[0]}" y="{te2[1]-8}" fill="#2a7">tube out (gun parked)</text>')
# operator
op = P(-420, -120); o.append(f'<text x="{op[0]-20}" y="{op[1]}" font-weight="bold">operator (−X side:</text><text x="{op[0]-20}" y="{op[1]+14}" font-weight="bold">the cable owns −Y)</text>')
# ---------- right panel: shell interface ----------
rx, ry = 800, 90
o.append(f'<text x="{rx}" y="{ry}" font-weight="bold">Shell interface (schematic side view)</text>')
o.append(f'<line x1="{rx+120}" y1="{ry+20}" x2="{rx+120}" y2="{ry+70}" stroke="#555" stroke-width="4"/><text x="{rx+128}" y="{ry+40}">arm head: short drop rod</text>')
o.append(f'<path d="M{rx+110},{ry+70} q10,14 20,0" fill="none" stroke="#333" stroke-width="3"/><text x="{rx+136}" y="{ry+82}">swivel hook</text>')
o.append(f'<path d="M{rx+60},{ry+150} L{rx+60},{ry+95} L{rx+180},{ry+95} L{rx+180},{ry+150}" fill="none" stroke="#2a6" stroke-width="3"/><text x="{rx+190}" y="{ry+106}" fill="#2a6">bail; pins on a trim slide (d = τ/W),</text><text x="{rx+190}" y="{ry+120}" fill="#2a6">grease drag; carry pins lock it</text>')
o.append(f'<rect x="{rx+30}" y="{ry+140}" width="180" height="46" rx="10" fill="#c9d6ee" stroke="#335"/><text x="{rx+70}" y="{ry+168}">shell + gun (CG ⊕)</text>')
o.append(f'<circle cx="{rx+120}" cy="{ry+150}" r="5" fill="#fff" stroke="#000"/>')
o.append(f'<line x1="{rx+60}" y1="{ry+150}" x2="{rx+180}" y2="{ry+150}" stroke="#2a6" stroke-dasharray="3 2"/>')
for bx in (rx + 70, rx + 120, rx + 170):
    o.append(f'<circle cx="{bx}" cy="{ry+194}" r="6" fill="#666"/>')
o.append(f'<rect x="{rx+50}" y="{ry+200}" width="140" height="10" fill="#e7c" stroke="#704"/><text x="{rx+200}" y="{ry+208}" fill="#704">vees (dock)</text>')
o.append(f'<line x1="{rx+120}" y1="{ry+210}" x2="{rx+120}" y2="{ry+290}" stroke="#2a6" stroke-width="10"/><text x="{rx+132}" y="{ry+260}" fill="#2a6">dock post</text>')
o.append(f'<path d="M{rx+20},{ry+170} l-30,40 l20,0" fill="none" stroke="#704" stroke-width="3"/><text x="{rx-60}" y="{ry+232}" fill="#704">cam latch pulls</text><text x="{rx-60}" y="{ry+246}" fill="#704">plate down (~60 N)</text>')
o.append(f'<line x1="{rx+215}" y1="{ry+175}" x2="{rx+300}" y2="{ry+250}" stroke="#555" stroke-width="2"/><text x="{rx+230}" y="{ry+270}">Bowden to trigger presser</text><text x="{rx+230}" y="{ry+284}">(lever on the dock post; main)</text>')
o.append(f'<text x="{rx-10}" y="{ry+330}">Hook at the CG passes only a vertical force:</text>')
o.append(f'<text x="{rx-10}" y="{ry+344}">the arm floats the gun (hand mode), and its</text>')
o.append(f'<text x="{rx-10}" y="{ry+358}">friction joints cannot push the docked shell.</text>')
o.append(f'<text x="{rx-10}" y="{ry+386}" font-weight="bold">States</text>')
for i, t in enumerate(['PARK: in the cradle; arm holds nothing precisely', 'HAND: lifted out; weightless; hand aims and tacks',
                       'DOCK: balls in vees, latched; arm only floats', 'Every change: snip first; stickout at the cradle']):
    o.append(f'<text x="{rx-10}" y="{ry+402+i*15}">{t}</text>')
o.append(f'<text x="12" y="{H-14}">Branch M2 (not drawn): a pole-mount arm high overhead carries a spring balancer whose line holds the bail — Derek\'s "hook on a wire" with its anchor on his monitor arm.</text>')
o.append('</svg>')
open('../sketches/w3-monitor-arm-session.svg', 'w').write('\n'.join(o))
print('ok')
