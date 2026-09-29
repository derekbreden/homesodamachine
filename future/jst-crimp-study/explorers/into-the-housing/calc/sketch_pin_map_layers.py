# Generates sketches/pin-map-layers.svg (schematic, from calc/wave2.py geometry)
out = "/Users/derekbredensteiner/Developer/homesodamachine/future/jst-crimp-study/explorers/into-the-housing/sketches/pin-map-layers.svg"
S = 18.0   # px per mm across
V = 9.0    # px per mm along the split
W, H = 1000, 720
parts = []
a = parts.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="13">')
a(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
a('<text x="20" y="28" font-size="17" font-weight="bold" fill="#111">Pin maps as layers: J4 and J7 each carry one group over the rest (schematic)</text>')
a('<text x="20" y="48" fill="#444">Plan view of the split, web (top) to housing rear face (bottom). Web at 1.7 mm per conductor, cavities at 2.5 mm, web centred on the housing.</text>')
a('<text x="20" y="66" fill="#444">Grey: lower layer, laid in order, no crossings. Red: upper layer, laid last, lying over the grey where they cross. calc/wave2.out.txt sections A-C.</text>')

def panel(ox, title, sub, names, pins, ncav, upper, trimmed_idx=None):
    L = 30.0  # mm split drawn
    y0 = 175
    y1 = y0 + L * V
    n = len(names)
    cx0 = ox
    a(f'<text x="{ox-200}" y="{y0-88}" font-weight="bold" fill="#111">{title}</text>')
    a(f'<text x="{ox-200}" y="{y0-72}" fill="#444">{sub}</text>')
    # web block
    wx = [(i - (n - 1) / 2) * 1.7 for i in range(n)]
    a(f'<rect x="{cx0 + wx[0]*S - 0.85*S - 4:.1f}" y="{y0-14}" width="{(wx[-1]-wx[0]+1.7)*S + 8:.1f}" height="14" fill="#333" rx="3"/>')
    # cavities
    cav_x = [(p - 1 - (ncav - 1) / 2) * 2.5 for p in range(1, ncav + 1)]
    for p, x in enumerate(cav_x, start=1):
        a(f'<rect x="{cx0 + x*S - 0.975*S:.1f}" y="{y1+4}" width="{1.95*S:.1f}" height="26" fill="#f4f1ea" stroke="#555"/>')
        a(f'<text x="{cx0 + x*S:.1f}" y="{y1+22}" text-anchor="middle" font-size="12" fill="#222">{p}</text>')
    a(f'<text x="{cx0 + cav_x[-1]*S + 30:.1f}" y="{y1+22}" fill="#555">cavities</text>')
    # lines: lower first, then upper
    order = [i for i in range(n) if i not in upper] + [i for i in range(n) if i in upper]
    for i in order:
        if i == trimmed_idx:
            x = cx0 + wx[i] * S
            a(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + 6*V:.1f}" stroke="#aaa" stroke-width="{1.7*S*0.5:.1f}" stroke-linecap="butt"/>')
            a(f'<text x="{x+14:.1f}" y="{y0 + 6*V + 4:.1f}" font-size="11" fill="#777">trimmed</text>')
            continue
        p = pins[i]
        xa = cx0 + wx[i] * S
        xb = cx0 + cav_x[p - 1] * S
        col = "#c0392b" if i in upper else "#666"
        # casing to show over/under
        if i in upper:
            a(f'<line x1="{xa:.1f}" y1="{y0}" x2="{xb:.1f}" y2="{y1:.1f}" stroke="#ffffff" stroke-width="13"/>')
        a(f'<line x1="{xa:.1f}" y1="{y0}" x2="{xb:.1f}" y2="{y1:.1f}" stroke="{col}" stroke-width="9"/>')
    for i in range(n):
        x = cx0 + wx[i] * S
        col = "#c0392b" if i in upper else "#222"
        lab = names[i]
        a(f'<text x="{x:.1f}" y="{y0-20}" font-size="11" fill="{col}" text-anchor="start" transform="rotate(-55 {x:.1f} {y0-20})">{lab}</text>')

panel(300, "J4 SENSORS: 2 layers, 5 crossings",
      "4P laid V5, IO25, 3V3, IO26 (pairs adjacent); 3P GND, IO27, IO23",
      ["V5", "IO25", "3V3", "IO26", "GND", "IO27", "IO23"], [3, 4, 1, 5, 2, 6, 7], 7, upper={2, 4})
panel(760, "J7 REEDS B: 2 layers, 2 crossings",
      "5P RB1-RB4, GND; 3P CLO, CHI, third trimmed",
      ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI", "x"], [1, 2, 3, 4, 7, 5, 6, 0], 7, upper={4}, trimmed_idx=7)

y = 535
lines = [
 "Every other loom is one layer: J1 (5P + 4P), J2 (3P + 3P, cavity 3 an empty slot), J3, J5, J6, J9, J11, J13.",
 "J4 with change-the-question's 4P order (3V3, IO26, V5, IO25) is 3 layers, also 5 crossings. With the 1-wire pair split",
 "around the flow pair (3V3, V5, IO25, IO26) it is 3 crossings and 2 layers, GND alone on top.",
 "In both looms the upper layer lands at an END of the housing, beside the lower layer, never in a gap inside it.",
 "Placing: lower layer first, from the housing centre outward, with waiting conductors held 5-8 mm above placed ones.",
 "J7 becomes one layer if GND rides the 3P with CLO and CHI and the 5P's fifth is trimmed (procedure-is-the-machine).",
 "The J4 order shown (V5, IO25, 3V3, IO26 | GND, IO27, IO23) is also a least-crossing order for half-row machines (2 off-parity, 2 crossings).",
 "A board revision to J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23 and J7 = RB1-RB4, GND, CLO, CHI makes both one layer (Derek's choice).",
]
for k, t in enumerate(lines):
    a(f'<text x="20" y="{y + 20*k}" fill="#333">{t}</text>')
a('</svg>')
open(out, "w").write("\n".join(parts))
print("wrote", out)
