# Generates sketches/i6-sort-then-push.svg (schematic)
out = "/Users/derekbredensteiner/Developer/homesodamachine/future/jst-crimp-study/explorers/into-the-housing/sketches/i6-sort-then-push.svg"
W, H = 1000, 900
P = []
a = P.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="13">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>'
  '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="#aaa" stroke-width="2"/></pattern></defs>')
a('<text x="20" y="28" font-size="17" font-weight="bold" fill="#111">i6 — sort, then push (schematic)</text>')
a('<text x="20" y="48" fill="#444">Crimped contacts wait in ribbon order in the staging plane; a carrier lowers each 8-10 mm into its housing slot, lower layer first, centre outward;</text>')
a('<text x="20" y="66" fill="#444">a backing blade squares the row; the housing is pushed on to the first wall, then one tine finishes each contact. Numbers: calc/wave2.out.txt A-D, calc/wave3.out.txt E, H.</text>')

# ---------------- side view ----------------
S = 11.0
ox, oy = 150, 250      # Y=0 at ox, Z=0 at oy
X = lambda Y: ox + S * Y
Z = lambda z: oy - S * z
a('<text x="20" y="96" font-weight="bold" fill="#111">Side view (~11 px per mm), Y to the right, Z up</text>')
# web clamp
a(f'<rect x="{X(-10):.1f}" y="{Z(1.6):.1f}" width="{10*S:.1f}" height="{3.2*S:.1f}" fill="#8a8a8a" stroke="#222"/>')
a(f'<text x="{X(-11):.1f}" y="{Z(-2.8):.1f}" fill="#222">web clamp</text>')
a(f'<line x1="{X(-12):.1f}" y1="{Z(0):.1f}" x2="{X(-10):.1f}" y2="{Z(0):.1f}" stroke="#111" stroke-width="{1.7*S:.1f}"/>')
# root comb
a(f'<rect x="{X(3):.1f}" y="{Z(-0.85):.1f}" width="{3*S:.1f}" height="{1.2*S:.1f}" fill="#e9d8a6" stroke="#9a7d2e"/>')
a(f'<text x="{X(1):.1f}" y="{Z(2.6):.1f}" fill="#7a5c10">root comb (ribbon order)</text>')
# staged conductor
a(f'<line x1="{X(0):.1f}" y1="{Z(0):.1f}" x2="{X(27):.1f}" y2="{Z(0):.1f}" stroke="#111" stroke-width="{1.7*S:.1f}"/>')
a(f'<rect x="{X(26.5):.1f}" y="{Z(1.55):.1f}" width="{6.7*S:.1f}" height="{2.4*S:.1f}" fill="#e6c35c" stroke="#6b4f00"/>')
a(f'<text x="{X(35):.1f}" y="{Z(0.6):.1f}" fill="#222">staging plane: waiting conductors, crimped, in ribbon order</text>')
# carrier on staged contact
a(f'<rect x="{X(28):.1f}" y="{Z(3.6):.1f}" width="{3*S:.1f}" height="{1.8*S:.1f}" fill="#9fd19f" stroke="#2e7d32"/>')
a(f'<rect x="{X(28):.1f}" y="{Z(-0.9):.1f}" width="{3*S:.1f}" height="{1.2*S:.1f}" fill="#9fd19f" stroke="#2e7d32"/>')
a(f'<line x1="{X(29.5):.1f}" y1="{Z(3.6):.1f}" x2="{X(29.5):.1f}" y2="{Z(9):.1f}" stroke="#2e7d32" stroke-width="4"/>')
a(f'<text x="{X(31.5):.1f}" y="{Z(6.5):.1f}" fill="#2e7d32">carrier: fingers above and below the crimped barrels,</text>')
a(f'<text x="{X(31.5):.1f}" y="{Z(5.1):.1f}" fill="#2e7d32">a toe behind them; X-Y-Z stage, load cell in Y</text>')
a(f'<line x1="{X(26):.1f}" y1="{Z(-2):.1f}" x2="{X(26):.1f}" y2="{Z(-7.5):.1f}" stroke="#c0392b" stroke-width="2" marker-end="url(#ar)"/>')
# placed conductor
a(f'<polyline points="{X(6):.1f},{Z(0):.1f} {X(20):.1f},{Z(-9):.1f} {X(26):.1f},{Z(-9):.1f}" fill="none" stroke="#555" stroke-width="{1.7*S:.1f}" stroke-linejoin="round"/>')
a(f'<rect x="{X(25.5):.1f}" y="{Z(-7.45):.1f}" width="{6.7*S:.1f}" height="{2.4*S:.1f}" fill="#e6c35c" stroke="#6b4f00"/>')
# target comb
a(f'<rect x="{X(20):.1f}" y="{Z(-9.6):.1f}" width="{4*S:.1f}" height="{2.2*S:.1f}" fill="#cfd8e6" stroke="#1f5fa8"/>')
a(f'<text x="{X(-10):.1f}" y="{Z(-14.2):.1f}" fill="#1f5fa8">blue: target comb, 8-10 mm lower: U-slots at 2.5 mm in housing order</text>')
# backing blade
a(f'<rect x="{X(24.6):.1f}" y="{Z(-3.5):.1f}" width="{0.8*S:.1f}" height="{7.6*S:.1f}" fill="none" stroke="#c0392b" stroke-dasharray="4 3"/>')
a(f'<text x="{X(-10):.1f}" y="{Z(-15.8):.1f}" fill="#c0392b">red dashed: backing blade, drops behind every barrel after the sort and takes the push; its tines follow up to ~2 mm into the cavities</text>')
# guide comb
a(f'<path d="M{X(29):.1f},{Z(-10.7):.1f} l{3*S:.1f},0 l0,{0.6*S:.1f} l{-3*S:.1f},0 z" fill="#ddd" stroke="#555"/>')

a(f'<text x="{X(-10):.1f}" y="{Z(-17.4):.1f}" fill="#555">grey bar under the noses: sprung guide comb, pressed away as the housing arrives</text>')
a(f'<text x="{X(-10):.1f}" y="{Z(-19.0):.1f}" fill="#c0392b">after the first wall, one finishing tine pushes each contact to its own wall (contact lengths differ)</text>')
# housing and nest
a(f'<rect x="{X(35):.1f}" y="{Z(-6.95):.1f}" width="{7.75*S:.1f}" height="{4.1*S:.1f}" fill="url(#hatch)" stroke="#333"/>')
a(f'<rect x="{X(34):.1f}" y="{Z(-11.05):.1f}" width="{11*S:.1f}" height="{1.2*S:.1f}" fill="#cfd8e6" stroke="#1f5fa8"/>')
a(f'<rect x="{X(46):.1f}" y="{Z(-7.5):.1f}" width="{2.5*S:.1f}" height="{3*S:.1f}" fill="#f2d7a0" stroke="#9a7d2e"/>')
a(f'<line x1="{X(48.5):.1f}" y1="{Z(-9):.1f}" x2="{X(60):.1f}" y2="{Z(-9):.1f}" stroke="#555" stroke-width="3"/>')
a(f'<line x1="{X(40):.1f}" y1="{Z(-3.2):.1f}" x2="{X(35.5):.1f}" y2="{Z(-3.2):.1f}" stroke="#c0392b" stroke-width="2" marker-end="url(#ar)"/>')
a(f'<text x="{X(43):.1f}" y="{Z(-2.8):.1f}" fill="#222">housing nest pushes −Y onto the row</text>')
a(f'<text x="{X(44):.1f}" y="{Z(-13.6):.1f}" fill="#222">bar load cell, NEMA 17 + T8 screw</text>')

# ---------------- plan view (J7) ----------------
S2 = 13.0
px0, py0 = 180, 690    # Y=0 at px0, X=0 at py0
PX = lambda Y: px0 + S2 * Y
PY = lambda x: py0 - S2 * x
a(f'<text x="20" y="{py0-190}" font-weight="bold" fill="#111">Plan view, J7 REEDS B (~13 px per mm), after the sort and before the push</text>')
names = ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI", "x"]
pins = [1, 2, 3, 4, 7, 5, 6, 0]
n = 8
wx = [(i - (n - 1) / 2) * 1.7 for i in range(n)]
cav = lambda p: (p - 4) * 2.5
a(f'<rect x="{PX(-8):.1f}" y="{PY(wx[-1]+1.0):.1f}" width="{8*S2:.1f}" height="{(wx[-1]-wx[0]+2.0)*S2:.1f}" fill="#8a8a8a" stroke="#222"/>')
a(f'<text x="{PX(-8):.1f}" y="{PY(wx[-1]+1.4):.1f}" fill="#222">5P + 3P edge to edge</text>')
order = [0, 1, 2, 3, 5, 6, 4]
for i in [7] + order:
    if names[i] == "x":
        a(f'<line x1="{PX(0):.1f}" y1="{PY(wx[i]):.1f}" x2="{PX(4):.1f}" y2="{PY(wx[i]):.1f}" stroke="#aaa" stroke-width="{1.7*S2*0.6:.1f}"/>')
        a(f'<text x="{PX(4.5):.1f}" y="{PY(wx[i])+4:.1f}" font-size="11" fill="#777">trimmed</text>')
        continue
    up = (names[i] == "GND")
    col = "#c0392b" if up else "#666"
    if up:
        a(f'<polyline points="{PX(0):.1f},{PY(wx[i]):.1f} {PX(5):.1f},{PY(wx[i]):.1f} {PX(20):.1f},{PY(cav(pins[i])):.1f} {PX(24):.1f},{PY(cav(pins[i])):.1f}" fill="none" stroke="#fff" stroke-width="{1.7*S2*0.6+5:.1f}"/>')
    a(f'<polyline points="{PX(0):.1f},{PY(wx[i]):.1f} {PX(5):.1f},{PY(wx[i]):.1f} {PX(20):.1f},{PY(cav(pins[i])):.1f} {PX(25.5):.1f},{PY(cav(pins[i])):.1f}" fill="none" stroke="{col}" stroke-width="{1.7*S2*0.6:.1f}"/>')
    a(f'<rect x="{PX(25.5):.1f}" y="{PY(cav(pins[i]) + 0.975):.1f}" width="{6.7*S2:.1f}" height="{1.95*S2:.1f}" fill="#e6c35c" stroke="#6b4f00"/>')
    a(f'<text x="{PX(-9):.1f}" y="{PY(wx[i])+4:.1f}" font-size="11" text-anchor="end" fill="{col}">{names[i]}</text>')
# target comb, blade, housing
a(f'<rect x="{PX(20):.1f}" y="{PY(9.5):.1f}" width="{4*S2:.1f}" height="{19*S2:.1f}" fill="#cfd8e6" stroke="#1f5fa8" opacity="0.55"/>')
a(f'<line x1="{PX(25):.1f}" y1="{PY(9.8):.1f}" x2="{PX(25):.1f}" y2="{PY(-9.8):.1f}" stroke="#c0392b" stroke-width="2" stroke-dasharray="5 3"/>')
a(f'<rect x="{PX(33.5):.1f}" y="{PY(9.1):.1f}" width="{7.75*S2:.1f}" height="{18.2*S2:.1f}" fill="none" stroke="#333" stroke-dasharray="6 4"/>')
for p in range(1, 8):
    a(f'<text x="{PX(42.5):.1f}" y="{PY(cav(p))+4:.1f}" font-size="12" fill="#222">{p}</text>')
a(f'<text x="{PX(44):.1f}" y="{PY(9.6):.1f}" fill="#222">XHP-7, pins 1-7</text>')
a(f'<text x="{PX(44):.1f}" y="{PY(8.2):.1f}" fill="#555">(dashed: before the push)</text>')
a(f'<text x="{PX(-8):.1f}" y="{PY(-11.8):.1f}" fill="#c0392b">GND placed last: it rides over CLO and CHI to pin 7</text>')
a(f'<text x="{PX(-8):.1f}" y="{PY(-13.1):.1f}" fill="#555">order: RB4, CLO, RB3, CHI, RB2, RB1 (lower layer, centre outward), then GND</text>')
a(f'<text x="{PX(19):.1f}" y="{PY(10.4):.1f}" fill="#1f5fa8">target comb</text>')
a(f'<text x="20" y="{H-16}" fill="#444">Web centred on the housing. The staging plane is not shown in plan: it lies above, in ribbon order, until each contact is lowered.</text>')
a('</svg>')
open(out, "w").write("\n".join(P))
print("wrote", out)
