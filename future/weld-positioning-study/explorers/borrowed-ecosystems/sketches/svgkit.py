"""Tiny SVG helper plus the gun proxy drawn from geometry.py (the scene's pose).

Views (bench coordinates, mm; bench top z = 0, tube axis at x = y = 0,
dot at x = +61.85 on the rim side):
  'xz'  section looking along the tangent (+Y into the page): radial x right, z up
  'yz'  elevation looking from outside at the dot (from +X): tangent y right, z up
  'xy'  plan from above: x right, y up
The gun proxy (253 x 143 x 34 mm envelope, parts placed from the manual drawing)
is illustrative, as in the orientation scene.
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import geometry as G

B = G.BENCH_OFFSET  # tube-frame z -> bench z


def to_bench(p):
    return np.array([p[0], p[1], p[2] + B])


DOT = to_bench(G.JOINT)
RIM_Z = G.TUBE_H + B
TUBE_BOTTOM_Z = B


def hull2d(pts):
    pts = sorted(set(map(tuple, np.round(pts, 3))))
    if len(pts) < 3:
        return pts
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


class Svg:
    def __init__(self, w, h, view, scale, origin, title=""):
        self.w, self.h, self.view, self.s = w, h, view, scale
        self.ox, self.oy = origin
        self.items = []
        self.title = title

    def proj(self, p):
        x, y, z = p
        if self.view == 'xz':
            u, v = x, z
        elif self.view == 'yz':
            u, v = y, z
        else:
            u, v = x, y
        return (self.ox + self.s * u, self.oy - self.s * v)

    def pt(self, u, v):
        """2D view coordinates (mm) to px."""
        return (self.ox + self.s * u, self.oy - self.s * v)

    def raw(self, s):
        self.items.append(s)

    def poly(self, pts3, stroke="#222", fill="none", w=1.2, dash=None, closed=True, op=1.0):
        pp = [self.proj(p) for p in pts3]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pp)
        tag = "polygon" if closed else "polyline"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<{tag} points="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{w}" fill-opacity="{op}"{da}/>')

    def poly2(self, pts2, stroke="#222", fill="none", w=1.2, dash=None, closed=True, op=1.0):
        pp = [self.pt(u, v) for u, v in pts2]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pp)
        tag = "polygon" if closed else "polyline"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<{tag} points="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{w}" fill-opacity="{op}"{da}/>')

    def line(self, a, b, stroke="#222", w=1.2, dash=None, arrow=False):
        (x1, y1), (x2, y2) = self.proj(a), self.proj(b)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = ' marker-end="url(#arr)"' if arrow else ""
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{da}{mk}/>')

    def line2(self, a, b, stroke="#222", w=1.2, dash=None, arrow=False, arrow2=False):
        (x1, y1), (x2, y2) = self.pt(*a), self.pt(*b)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = ' marker-end="url(#arr)"' if arrow else ""
        mk2 = ' marker-start="url(#arrs)"' if arrow2 else ""
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{da}{mk}{mk2}/>')

    def circle2(self, c, r, stroke="#222", fill="none", w=1.2, dash=None):
        x, y = self.pt(*c)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{self.s*r:.1f}" stroke="{stroke}" fill="{fill}" stroke-width="{w}"{da}/>')

    def rect2(self, u0, v0, u1, v1, stroke="#222", fill="none", w=1.2, dash=None, op=1.0):
        self.poly2([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], stroke, fill, w, dash, True, op)

    def text2(self, u, v, s, size=12, color="#111", anchor="start", weight="normal"):
        x, y = self.pt(u, v)
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>')

    def textpx(self, x, y, s, size=12, color="#111", anchor="start", weight="normal"):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.raw(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{s}</text>')

    def spring2(self, a, b, n=8, amp=5, stroke="#b5451b", w=1.4):
        a, b = np.array(a, float), np.array(b, float)
        d = b - a
        L = np.linalg.norm(d)
        t = d / L
        nrm = np.array([-t[1], t[0]])
        pts = [a, a + t * L * 0.15]
        for i in range(n):
            f = 0.15 + 0.7 * (i + 0.5) / n
            pts.append(a + t * L * f + nrm * amp * (1 if i % 2 == 0 else -1))
        pts += [a + t * L * 0.85, b]
        self.poly2([tuple(p) for p in pts], stroke=stroke, w=w, closed=False)

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                '<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#333"/></marker>'
                '<marker id="arrs" markerWidth="10" markerHeight="8" refX="1" refY="4" orient="auto"><path d="M10,0 L0,4 L10,8 z" fill="#333"/></marker></defs>'
                f'<rect width="100%" height="100%" fill="#fcfcf8"/>')
        body = "\n".join(self.items)
        tt = ""
        if self.title:
            tt = f'<text x="14" y="24" font-family="Helvetica,Arial,sans-serif" font-size="16" font-weight="bold" fill="#111">{self.title}</text>'
        with open(path, "w") as f:
            f.write(head + tt + body + "</svg>")


# ---- gun proxy -------------------------------------------------------------
def _cyl(z0, z1, r0, r1, n=10):
    pts = []
    for z, r in ((z0, r0), (z1, r1)):
        for k in range(n):
            a = 2 * np.pi * k / n
            pts.append([r * np.cos(a), r * np.sin(a), z])
    return pts


def _box(x0, x1, y0, y1, z0, z1):
    return [[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def _grip_outline():
    a, b = np.array([-25.0, 172.0]), np.array([-111.0, 232.0])
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([d[1], -d[0]])
    a, b = a - 8 * d, b + 8 * d
    return [tuple(q) for q in (a + 14 * n, a - 14 * n, b + 14 * n, b - 14 * n)]


GUN_PARTS = {   # the scene's main.js proxy
    "nozzle": _cyl(0, 23, 2.2, 2.2),
    "graduated tube": _cyl(23, 54, 8.5, 8.5),
    "tube": _cyl(54, 100, 5.5, 5.5),
    "lens drawer": _cyl(100, 118, 12, 12),
    "body": _box(-17, 17, -17, 17, 118, 253),
    "grip": [[x, y, z] for x in (-15, 15) for (y, z) in _grip_outline()],
}


def gun_parts_world(pose):
    out = {}
    for k, pts in GUN_PARTS.items():
        out[k] = [to_bench(G.pose_point(p, *pose)) for p in pts]
    return out


def draw_gun(svg, pose, stroke="#333", fill="#d9d9d9", label=True, shell=False):
    parts = gun_parts_world(pose)
    for k, pts in parts.items():
        pp = [svg.proj(p) for p in pts]
        h = hull2d(pp)
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in h)
        svg.raw(f'<polygon points="{d}" stroke="{stroke}" fill="{fill}" stroke-width="1" fill-opacity="0.85"/>')
    if shell:
        # shell: hull of body+grip+sleeve+drawer, drawn as a translucent outline
        allp = []
        for k in ("tube", "lens drawer", "body", "grip"):
            allp += [svg.proj(p) for p in parts[k]]
        h = hull2d(allp)
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in h)
        svg.raw(f'<polygon points="{d}" stroke="#2a6f97" fill="#2a6f97" stroke-width="1.6" fill-opacity="0.12" stroke-dasharray="5,3"/>')
    # wire: guide back -> tip (dot)
    gb = to_bench(G.pose_point([0, -24.7, 87.1], *pose))
    svg.line(gb, DOT, stroke="#8a5a00", w=1.4)
    # beam: nozzle -> dot
    nz = to_bench(G.pose_point([0, 0, 0], *pose))
    svg.line(nz, DOT, stroke="#d62828", w=1.0, dash="3,2")
    return parts


def cable_path(pose, R=350.0, tail=250.0, n=40):
    """Scene-style cable: leaves the butt along the grip rake, is on the grip
    axis 70 mm out (main.js), then bends down at R (emitting minimum)."""
    base = to_bench(G.pose_point(G.GRIP_BASE, *pose))
    dot = DOT
    ax = (base - dot) / np.linalg.norm(base - dot)
    rk = to_bench(G.pose_point(G.GRIP_BASE + G.GRIP_RAKE * 100, *pose)) - base
    rk /= np.linalg.norm(rk)
    end = base + 70 * ax
    c1, c2 = base + 24 * rk, end - 25 * ax
    pts = [(1-t)**3*base + 3*(1-t)**2*t*c1 + 3*(1-t)*t**2*c2 + t**3*end for t in np.linspace(0, 1, 10)]
    d = ax
    down = np.array([0, 0, -1.0])
    nrm = down - np.dot(down, d) * d
    nrm /= np.linalg.norm(nrm)
    phimax = np.arcsin(d[2]) + np.pi / 2
    pts += [end + R * (np.sin(f) * d + (1 - np.cos(f)) * nrm) for f in np.linspace(0, phimax, n)]
    pts.append(pts[-1] + np.array([0, 0, -tail]))
    return pts


def draw_cable(svg, pose, R=350.0, tail=250.0, stroke="#555"):
    pts = cable_path(pose, R, tail)
    svg.poly(pts, stroke=stroke, w=3.0, closed=False)
    return pts


def draw_tube_xz(svg, closure_plate=True):
    ri, ro = G.R_IN, G.R_OUT
    zb, zr = TUBE_BOTTOM_Z, RIM_Z
    for sgn in (1, -1):
        svg.poly2([(sgn * ri, zb), (sgn * ro, zb), (sgn * ro, zr), (sgn * ri, zr)], stroke="#444", fill="#9aa5ad", w=1)
    if closure_plate:
        svg.rect2(-61.72, DOT[2] - 6.35, 61.72, DOT[2], stroke="#444", fill="#b8c2c8", w=1)
    svg.circle2((DOT[0], DOT[2]), 2.2, stroke="#d62828", fill="#d62828")


def draw_tube_yz(svg):
    zb, zr = TUBE_BOTTOM_Z, RIM_Z
    svg.rect2(-G.R_OUT, zb, G.R_OUT, zr, stroke="#444", fill="#9aa5ad", w=1, op=0.5)
    svg.circle2((0, DOT[2]), 2.2, stroke="#d62828", fill="#d62828")


def draw_tube_xy(svg):
    svg.circle2((0, 0), G.R_OUT, stroke="#444", w=1.2)
    svg.circle2((0, 0), G.R_IN, stroke="#444", w=0.8)
    for s in (1, -1):
        svg.circle2((0, s * 19.05), 5.56, stroke="#777", w=0.8)
    svg.circle2((DOT[0], DOT[1]), 2.2, stroke="#d62828", fill="#d62828")


def draw_rotator_xz(svg):
    # schematic only: feet, base, turntable/nest block
    svg.rect2(-150, 24, 150, 36, stroke="#777", fill="#e8e2d0", w=1)
    for u in (-140, 130):
        svg.rect2(u, 0, u + 10, 24, stroke="#777", fill="#e8e2d0", w=1)
    svg.rect2(-90, 36, 90, TUBE_BOTTOM_Z, stroke="#777", fill="#efe9d8", w=1, dash="4,3")
    svg.text2(-148, 44, "existing rotator (schematic)", size=10, color="#777")


def draw_bench(svg, u0, u1):
    svg.line2((u0, 0), (u1, 0), stroke="#6b4f2a", w=3)


def compose(panels, path, title="", notes=(), w=None, h=None, pad=10):
    """Place several Svg panels side by side (list of (svg, x, y)) in one file."""
    if w is None:
        w = max(x + s.w for s, x, y in panels) + pad
    if h is None:
        h = max(y + s.h for s, x, y in panels) + pad + 18 * len(notes)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
           '<defs><marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 z" fill="#333"/></marker>'
           '<marker id="arrs" markerWidth="10" markerHeight="8" refX="1" refY="4" orient="auto"><path d="M10,0 L0,4 L10,8 z" fill="#333"/></marker></defs>',
           '<rect width="100%" height="100%" fill="#fcfcf8"/>']
    if title:
        out.append(f'<text x="14" y="26" font-family="Helvetica,Arial,sans-serif" font-size="18" font-weight="bold" fill="#111">{title}</text>')
    for s, x, y in panels:
        out.append(f'<g transform="translate({x},{y})">')
        out.append(f'<rect x="0" y="0" width="{s.w}" height="{s.h}" fill="none" stroke="#ccc"/>')
        if s.title:
            out.append(f'<text x="8" y="18" font-family="Helvetica,Arial,sans-serif" font-size="13" font-weight="bold" fill="#333">{s.title}</text>')
        out.extend(s.items)
        out.append('</g>')
    y0 = max(y + s.h for s, x, y in panels) + 20
    for i, n in enumerate(notes):
        n = n.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        out.append(f'<text x="14" y="{y0 + 18*i}" font-family="Helvetica,Arial,sans-serif" font-size="12" fill="#333">{n}</text>')
    out.append('</svg>')
    with open(path, 'w') as f:
        f.write("\n".join(out))
