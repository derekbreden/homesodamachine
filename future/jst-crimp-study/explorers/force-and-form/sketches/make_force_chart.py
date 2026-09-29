"""Force versus punch height chart for the XH crimp model family.

Writes force-stroke.svg next to this file. Data: ../calc/stroke_model.py
(table view: ../calc/stroke_model.out.txt section 1). Palette: categorical
slots 1-4 of the dataviz reference palette, validated light and dark
(relief rule: every line is direct-labelled).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "calc"))
from stroke_model import total_force  # noqa: E402

SERIES = [("low", "low: 0.75 kN peak"), ("central", "central: 1.6 kN"),
          ("high", "high: 2.3 kN"), ("steep", "steep: 2.3 kN, late rise")]

W, H = 800, 430
PANELS = [  # x0, x1 (px), s_left, s_right (mm), title
    (70, 420, 1.6, 0.0, "Whole forming stroke"),
    (470, 720, 0.25, 0.0, "Last 0.25 mm (zoom)"),
]
Y0, Y1 = 330, 70          # px for 0 N and F_MAX
F_MAX = 2500.0


def ypx(f):
    return Y0 - (Y0 - Y1) * f / F_MAX


def xpx(panel, s):
    x0, x1, sl, sr, _ = panel
    return x0 + (x1 - x0) * (sl - s) / (sl - sr)


out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'width="{W}" height="{H}" role="img" aria-labelledby="t d">')
out.append('<title id="t">XH crimp: force versus punch height above bottom of stroke</title>')
out.append('<desc id="d">Model family from calc/stroke_model.py. Force stays in the tens to a few '
           'hundred newtons while the wings curl, and climbs to 0.75-2.4 kN only in the last '
           '0.1-0.2 mm before the bottom of the stroke.</desc>')
out.append("""<style>
.bg{fill:#fcfcfb}.band{fill:#f0efec}
text{font-family:system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#52514e;font-size:11px}
.h{fill:#0b0b0b;font-size:13px;font-weight:600}
.lab{font-size:11px;fill:#0b0b0b}
.grid{stroke:#e4e3df;stroke-width:1}
.axis{stroke:#52514e;stroke-width:1}
.ln{fill:none;stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.s1{stroke:#2a78d6}.s2{stroke:#eb6834}.s3{stroke:#1baf7a}.s4{stroke:#eda100}
@media (prefers-color-scheme: dark){
.bg{fill:#1a1a19}.band{fill:#262624}text{fill:#c3c2b7}.h,.lab{fill:#ffffff}
.grid{stroke:#383835}.axis{stroke:#c3c2b7}
.s1{stroke:#3987e5}.s2{stroke:#d95926}.s3{stroke:#199e70}.s4{stroke:#c98500}}
</style>""")
out.append(f'<g><rect class="bg" width="{W}" height="{H}"/>')
out.append('<text class="h" x="70" y="24">XH crimp, modelled: where along the stroke the force is needed</text>')
out.append('<text x="70" y="42">Estimate family, not measurement (calc/stroke_model.py). Punch moves left to right; '
           '0 = bottom of stroke.</text>')

for pi_, panel in enumerate(PANELS):
    x0, x1, sl, sr, title = panel
    # compaction band
    xb = xpx(panel, 0.2) if sl > 0.2 else x0
    out.append(f'<rect x="{xb:.1f}" y="{Y1}" width="{x1-xb:.1f}" height="{Y0-Y1}" class="band"/>')
    out.append(f'<text class="h" x="{x0}" y="{Y1-12}">{title}</text>')
    for f in range(0, 2501, 500):
        y = ypx(f)
        out.append(f'<line class="grid" x1="{x0}" x2="{x1}" y1="{y:.1f}" y2="{y:.1f}"/>')
        if pi_ == 0:
            out.append(f'<text x="{x0-8}" y="{y+4:.1f}" text-anchor="end">{f:,}</text>')
    ticks = [1.6, 1.2, 0.8, 0.4, 0.2, 0.0] if sl > 1 else [0.25, 0.2, 0.15, 0.1, 0.05, 0.0]
    for s in ticks:
        x = xpx(panel, s)
        out.append(f'<line class="axis" x1="{x:.1f}" x2="{x:.1f}" y1="{Y0}" y2="{Y0+4}"/>')
        out.append(f'<text x="{x:.1f}" y="{Y0+17}" text-anchor="middle">{s:g}</text>')
    out.append(f'<line class="axis" x1="{x0}" x2="{x1}" y1="{Y0}" y2="{Y0}"/>')
    out.append(f'<text x="{(x0+x1)/2:.1f}" y="{Y0+34}" text-anchor="middle">punch height above bottom of stroke (mm)</text>')
    for k, (case, _) in enumerate(SERIES):
        pts = []
        s = sl
        step = (sl - sr) / 300
        while s >= sr - 1e-9:
            pts.append(f"{xpx(panel, max(s,0)):.1f},{ypx(total_force(max(s, 0.0), case)):.1f}")
            s -= step
        out.append(f'<polyline class="ln s{k+1}" points="{" ".join(pts)}">'
                   f'<title>{SERIES[k][1]}</title></polyline>')
    if pi_ == 0:
        out.append(f'<text x="{x0+8}" y="{ypx(420):.1f}">wings enter and curl:</text>')
        out.append(f'<text x="{x0+8}" y="{ypx(420)+14:.1f}">tens to a few hundred N</text>')
        out.append(f'<text x="{xb-4:.1f}" y="{Y1+14}" text-anchor="end">compaction zone,</text>')
        out.append(f'<text x="{xb-4:.1f}" y="{Y1+28}" text-anchor="end">last ~0.2 mm</text>')
    out.append(f'<text x="{x0}" y="{Y1-28 if False else Y1-12}" />')

# direct labels on the zoom panel, at s = 0 end, spread vertically
p = PANELS[1]
ends = []
for k, (case, lab) in enumerate(SERIES):
    ends.append([ypx(total_force(0.0, case)), k, lab])
ends.sort()
last = -99
for e in ends:
    if e[0] - last < 14:
        e[0] = last + 14
    last = e[0]
for y, k, lab in ends:
    out.append(f'<text class="lab" x="{p[1]+6}" y="{y+4:.1f}">{lab.split(":")[0]}</text>')

# legend row
lx = 70
for k, (case, lab) in enumerate(SERIES):
    out.append(f'<line x1="{lx}" x2="{lx+18}" y1="{H-18}" y2="{H-18}" class="s{k+1}" stroke-width="3"/>')
    out.append(f'<text class="lab" x="{lx+24}" y="{H-14}">{lab}</text>')
    lx += 24 + 7.0 * len(lab) + 22
out.append('<text x="70" y="{0}" font-size="10">Table view: calc/stroke_model.out.txt, section 1.</text>'.format(H - 34))
out.append('</g></svg>')

with open(os.path.join(HERE, "force-stroke.svg"), "w") as fh:
    fh.write("\n".join(out))
print("wrote force-stroke.svg")
