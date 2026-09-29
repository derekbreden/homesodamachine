"""Tiny SVG helper for the force-and-form schematic sketches.

Colours are CSS classes with a dark-mode override, so the files read in light
and dark viewers and in renderers without CSS variables.
"""

STYLE = """<style>
.bg{fill:#fcfcfb}
text{font-family:system-ui,-apple-system,Segoe UI,Helvetica,Arial,sans-serif;fill:#0b0b0b;font-size:12px}
.t2{fill:#52514e;font-size:11px}.h{font-size:15px;font-weight:600}.sm{font-size:10px;fill:#52514e}
.steel{fill:#c9c8c2;stroke:#52514e;stroke-width:1.2}
.dark{fill:#8f8e88;stroke:#3d3c39;stroke-width:1.2}
.bought{fill:#dcdad2;stroke:#52514e;stroke-width:1.2;stroke-dasharray:4 2}
.print{fill:#cde2fb;stroke:#2a78d6;stroke-width:1.2}
.contact{fill:#eda100;stroke:#7a5300;stroke-width:1}
.wire{stroke:#eb6834;stroke-width:4;fill:none;stroke-linecap:round}
.wirefill{fill:#eb6834;stroke:#8c3a17;stroke-width:1}
.strand{stroke:#8c3a17;stroke-width:1;fill:none}
.force{stroke:#e34948;stroke-width:2.5;fill:none}
.forcefill{fill:#e34948}
.move{stroke:#2a78d6;stroke-width:1.8;fill:none;stroke-dasharray:5 3}
.movefill{fill:#2a78d6}
.ln{stroke:#52514e;stroke-width:1.2;fill:none}
.thin{stroke:#8a8984;stroke-width:1;fill:none;stroke-dasharray:3 3}
.box{fill:none;stroke:#8a8984;stroke-width:1}
@media (prefers-color-scheme: dark){
.bg{fill:#1a1a19} text{fill:#ffffff} .t2,.sm{fill:#c3c2b7}
.steel{fill:#4a4a47;stroke:#c3c2b7}.dark{fill:#6b6a66;stroke:#d8d7d0}
.bought{fill:#33332f;stroke:#c3c2b7}.print{fill:#1c3a5e;stroke:#3987e5}
.contact{fill:#c98500;stroke:#f3c56a}.wire{stroke:#d95926}.wirefill{fill:#d95926;stroke:#f0a07e}
.strand{stroke:#f0a07e}.force{stroke:#e66767}.forcefill{fill:#e66767}
.move{stroke:#3987e5}.movefill{fill:#3987e5}.ln{stroke:#c3c2b7}.thin{stroke:#8a8984}.box{stroke:#6b6a66}}
</style>"""


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.el = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
                   f'height="{h}" role="img" aria-labelledby="t d">',
                   f'<title id="t">{title}</title>', f'<desc id="d">{desc}</desc>', STYLE,
                   '<defs>'
                   '<marker id="af" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
                   'orient="auto-start-reverse"><path class="forcefill" d="M0,0 L10,5 L0,10 z"/></marker>'
                   '<marker id="am" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
                   'orient="auto-start-reverse"><path class="movefill" d="M0,0 L10,5 L0,10 z"/></marker>'
                   '</defs>',
                   f'<rect class="bg" width="{w}" height="{h}"/>']

    def rect(self, x, y, w, h, cls="steel", rx=0):
        self.el.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>')

    def poly(self, pts, cls="steel"):
        p = " ".join(f"{a},{b}" for a, b in pts)
        self.el.append(f'<polygon class="{cls}" points="{p}"/>')

    def pline(self, pts, cls="wire"):
        p = " ".join(f"{a},{b}" for a, b in pts)
        self.el.append(f'<polyline class="{cls}" points="{p}"/>')

    def line(self, x1, y1, x2, y2, cls="ln"):
        self.el.append(f'<line class="{cls}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')

    def circle(self, x, y, r, cls="steel"):
        self.el.append(f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}"/>')

    def path(self, d, cls="ln"):
        self.el.append(f'<path class="{cls}" d="{d}"/>')

    def force(self, x1, y1, x2, y2):
        self.el.append(f'<line class="force" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#af)"/>')

    def move(self, x1, y1, x2, y2, both=False):
        st = ' marker-start="url(#am)"' if both else ""
        self.el.append(f'<line class="move" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#am)"{st}/>')

    def text(self, x, y, s, cls="", anchor="start"):
        c = f' class="{cls}"' if cls else ""
        self.el.append(f'<text{c} x="{x}" y="{y}" text-anchor="{anchor}">{s}</text>')

    def lines(self, x, y, rows, cls="", dy=15, anchor="start"):
        for i, r in enumerate(rows):
            self.text(x, y + i * dy, r, cls, anchor)

    def save(self, path):
        self.el.append("</svg>")
        with open(path, "w") as fh:
            fh.write("\n".join(self.el))
