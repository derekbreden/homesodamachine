"""Tiny SVG writer for schematic sketches (borrowed-machines explorer)."""

FONT = "Helvetica,Arial,sans-serif"
INK = "#222"
MUTED = "#666"
STEEL = "#9aa5ad"
BRONZE = "#c9a45c"
COPPER = "#c87533"
SILICONE = "#3a3a3a"
PRINTED = "#8fb8de"
BOUGHT = "#d9d9d9"
ACCENT = "#d62828"
GREEN = "#2a9d4b"
PAPER = "#fcfcf8"


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Sketch:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.items = []
        self.items.append(f'<rect width="100%" height="100%" fill="{PAPER}"/>')
        self.text(14, 28, title, size=18, weight="bold")

    # primitives -------------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.2, dash=None, rx=0, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.2, dash=None, arrow=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow in ("end", "both"):
            m += ' marker-end="url(#arr)"'
        if arrow in ("start", "both"):
            m += ' marker-start="url(#arrs)"'
        self.items.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}/>')

    def poly(self, pts, fill="none", stroke=INK, sw=1.2, closed=True, dash=None, opacity=1.0):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<{tag} points="{p}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
                          f'stroke-width="{sw}"{d}/>')

    def path(self, d, fill="none", stroke=INK, sw=1.2, dash=None, arrow=None, opacity=1.0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow in ("end", "both"):
            m += ' marker-end="url(#arr)"'
        if arrow in ("start", "both"):
            m += ' marker-start="url(#arrs)"'
        self.items.append(f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
                          f'stroke-width="{sw}"{da}{m}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=1.2, dash=None, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
                          f'fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, t, size=12, weight="normal", fill=INK, anchor="start", italic=False):
        st = ' font-style="italic"' if italic else ""
        self.items.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
                          f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{st}>{esc(t)}</text>')

    def lines(self, x, y, rows, size=12, gap=None, **kw):
        gap = gap or size * 1.3
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, size=size, **kw)

    def label(self, x, y, tx, ty, t, size=11, anchor="start"):
        """leader line from (x,y) on the part to text at (tx,ty)"""
        self.line(x, y, tx, ty - 4 if ty > y else ty + 2, stroke=MUTED, sw=0.8)
        self.circle(x, y, 1.8, fill=MUTED, stroke=MUTED)
        self.text(tx, ty, t, size=size, anchor=anchor)

    def panel(self, x, y, w, h, title):
        self.rect(x, y, w, h, stroke="#bbb", sw=1)
        self.text(x + 8, y + 18, title, size=13, weight="bold", fill="#333")

    def legend(self, x, y):
        rows = [(PRINTED, "printed"), (BOUGHT, "bought / borrowed"), (STEEL, "steel"),
                (SILICONE, "ribbon / conductor"), (COPPER, "stripped strands"), (BRONZE, "XH contact")]
        for i, (c, t) in enumerate(rows):
            self.rect(x + i * 150, y - 10, 14, 12, fill=c, stroke=INK, sw=0.8)
            self.text(x + i * 150 + 20, y, t, size=11)

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">\n'
                '<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                '<path d="M0,0 L10,4 L0,8 z" fill="#333"/></marker>'
                '<marker id="arrs" markerWidth="10" markerHeight="8" refX="1" refY="4" orient="auto">'
                '<path d="M10,0 L0,4 L10,8 z" fill="#333"/></marker></defs>\n')
        with open(path, "w") as f:
            f.write(head + "\n".join(self.items) + "\n</svg>\n")
