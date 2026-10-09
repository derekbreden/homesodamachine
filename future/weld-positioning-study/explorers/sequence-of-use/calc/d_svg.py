"""Idea D at the true opening pose (hole dial 30): original rim gauge vs branch D-r/D-m foot.
Plan to scale (tube, proxy gun); gauge, foot, holder and stack schematic in placement."""
import math
from proxy import *
S = 1.6
W, H = 1200, 740
cx, cy = 440, 300
def P(x, y): return (cx + S * x, cy - S * y)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif" font-size="11">',
     '<rect width="100%" height="100%" fill="#fbfbf8"/>',
     '<text x="12" y="20" font-size="14" font-weight="bold">D — gauge-set, lock-held: original rim gauge and the rate-split branch (D-r / D-m), plan at the true opening pose</text>',
     '<text x="12" y="36">Tube and proxy gun to scale (grip 45, hole dial 30, vertical −15); gauge, foot pads, holder and stack placements are proposals.</text>']
o.append(f'<circle cx="{cx}" cy="{cy}" r="{S*R_OUT}" fill="#dfeaea" stroke="#577"/><circle cx="{cx}" cy="{cy}" r="{S*R_IN}" fill="#d3e2e2" stroke="#577"/>')
d = P(R_IN, 0); o.append(f'<circle cx="{d[0]}" cy="{d[1]}" r="4" fill="#d00"/><text x="{d[0]+6}" y="{d[1]+16}" fill="#d00">dot</text>')
pts = [pose(p) for p in ((0, 0, 0), (0, 0, 118), (0, 0, 253))]
o.append('<polyline points="%s" fill="none" stroke="#335" stroke-width="16" stroke-opacity="0.3" stroke-linecap="round"/>' % ' '.join(f'{P(q[0], q[1])[0]:.1f},{P(q[0], q[1])[1]:.1f}' for q in pts))
gs, gb = pose((0, -25, 172)), pose(GB)
o.append(f'<line x1="{P(gs[0],gs[1])[0]:.1f}" y1="{P(gs[0],gs[1])[1]:.1f}" x2="{P(gb[0],gb[1])[0]:.1f}" y2="{P(gb[0],gb[1])[1]:.1f}" stroke="#335" stroke-width="20" stroke-opacity="0.2" stroke-linecap="round"/>')
wt, wg = pose((0, 0, -CL)), pose((0, -24.7, 87.1))
o.append(f'<line x1="{P(wt[0],wt[1])[0]:.1f}" y1="{P(wt[0],wt[1])[1]:.1f}" x2="{P(wg[0],wg[1])[0]:.1f}" y2="{P(wg[0],wg[1])[1]:.1f}" stroke="#b36b00" stroke-width="2"/>')
o.append(f'<text x="{P(wg[0],wg[1])[0]-60:.1f}" y="{P(wg[0],wg[1])[1]+14:.1f}" fill="#b36b00">wire from −Y</text>')
# original rim gauge: arc segment on the rim from -35 to +35 deg, split on +Y side
arc = [P((R_OUT + 6) * math.cos(math.radians(t)), (R_OUT + 6) * math.sin(math.radians(t))) for t in range(-35, 31, 3)]
o.append('<polyline points="%s" fill="none" stroke="#a70" stroke-width="10" stroke-opacity="0.45"/>' % ' '.join(f'{a:.1f},{b:.1f}' for a, b in arc))
o.append(f'<text x="{P(80,-40)[0]:.1f}" y="{P(80,-40)[1]:.1f}" fill="#a70">D original: printed rim gauge (split, slides out</text><text x="{P(80,-48)[0]:.1f}" y="{P(80,-48)[1]+4:.1f}" fill="#a70">on +Y past the wire) receives the shell; kept as a pose CHECK</text>')
# D-r foot pads on +Y side, 8 mm along the seam
th = math.degrees(8 / R_IN)
zp = P(50 * math.cos(math.radians(th)), 50 * math.sin(math.radians(th)))
xp = P((R_IN - 1) * math.cos(math.radians(th + 3)), (R_IN - 1) * math.sin(math.radians(th + 3)))
o.append(f'<rect x="{zp[0]-5}" y="{zp[1]-5}" width="10" height="10" fill="#2a6"/><circle cx="{xp[0]:.1f}" cy="{xp[1]:.1f}" r="5" fill="#2a6"/>')
o.append(f'<text x="{P(-40,40)[0]:.1f}" y="{P(-40,40)[1]:.1f}" fill="#2a6">D-r foot (on the shell, 3 mm cam slide): Z pad on the</text>')
o.append(f'<text x="{P(-40,32)[0]:.1f}" y="{P(-40,32)[1]+4:.1f}" fill="#2a6">plate face r≈50, X pad on the bore; +Y side, 8 mm along</text>')
o.append(f'<text x="{P(-40,24)[0]:.1f}" y="{P(-40,24)[1]+8:.1f}" fill="#2a6">the seam (free side at this pose)</text>')
# tacks at +-22.5 when gauging
for t in (22.5, -22.5, 67.5, -67.5, 112.5, -112.5, 157.5, -157.5):
    a = P(R_IN * math.cos(math.radians(t)), R_IN * math.sin(math.radians(t)))
    o.append(f'<circle cx="{a[0]:.1f}" cy="{a[1]:.1f}" r="3" fill="#555"/>')
o.append(f'<text x="{P(-60,-75)[0]:.1f}" y="{P(-60,-75)[1]:.1f}" fill="#555">tacks (grey) while gauging: table indexed 22.5°, so the foot lands between tacks</text>')
# holder and stack
hb = P(-200, -120); sh = P(-40, -110)
o.append(f'<line x1="{hb[0]}" y1="{hb[1]}" x2="{sh[0]}" y2="{sh[1]}" stroke="#555" stroke-width="7" stroke-opacity="0.7"/>')
o.append(f'<rect x="{hb[0]-12}" y="{hb[1]-12}" width="24" height="24" fill="#999"/><text x="{hb[0]-80}" y="{hb[1]+30}">holder base (lockable arm, D original;</text><text x="{hb[0]-80}" y="{hb[1]+44}">in D-r the lead-screw slides hold)</text>')
o.append(f'<rect x="{sh[0]-26}" y="{sh[1]-12}" width="52" height="24" fill="#f3e7c9" stroke="#a70"/><text x="{sh[0]-110}" y="{sh[1]-18}" fill="#a70">stack: X slide, Y slide (yaw), recipe block</text>')
# right column text
rx = 790
lines = [('D original (wave 1)', True), ('one printed gauge on the rim sets all six freedoms per tube;', False), ('a single-lock holder holds; gauge removed before the weld.', False), ('Breaks: lock shift strains the gauge; the gauge must split', False), ('to pass the wire.', False), ('', False),
         ('D-r (who-moves-what, wave 2)', True), ('split by rate: angles in a printed block (per recipe),', False), ('yaw/radial on lead-screw slides (per recipe; stopping', False), ('turning is locking), height per tube by the work,', False), ('set with the retractable foot.', False), ('', False),
         ('D-m (who-moves-what)', True), ('a dial on the Z pad read at the eight between-tack angles:', False), ('the tube\'s runout map; set height to the mean.', False), ('', False),
         ('Sequence (sequence-of-use)', True), ('index 22.5° → touch → read / set → retract → back to tack 1.', False), ('With the stand-hung plate head the foot only measures.', False)]
y = 70
for t, b in lines:
    o.append(f'<text x="{rx}" y="{y}" {"font-weight=\"bold\"" if b else ""}>{t}</text>'); y += 16
o.append('</svg>')
open('../sketches/d-gauge-foot.svg', 'w').write('\n'.join(o))
print('ok')
