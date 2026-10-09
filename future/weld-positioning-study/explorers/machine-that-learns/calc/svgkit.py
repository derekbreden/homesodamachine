"""Tiny SVG helper: projects the scene's gun proxy and the tube into simple views.

Coordinates are mm relative to the laser dot (scene frame: +Z up, dot on the
+X side of the tube, tangent along +/-Y). The gun silhouette is the scene's
illustrative proxy (253 x 143 x 34 envelope), not a scan.
"""
import math
from pose_points import pose_point, R_IN

TUBE_R_OUT = 63.5
TUBE_LEN = 152.4
RECESS = 6.35
DOT_ABOVE_BASE_BOTTOM = 214.4 - RECESS   # rotator base bottom -> dot
DOT_ABOVE_BENCH = 232.0


def box_corners(center, half, axis_u, axis_v, axis_w):
    pts = []
    for su in (-1, 1):
        for sv in (-1, 1):
            for sw in (-1, 1):
                pts.append(tuple(center[i] + su * half[0] * axis_u[i] + sv * half[1] * axis_v[i] + sw * half[2] * axis_w[i]
                                 for i in range(3)))
    return pts


def unit(v):
    n = math.sqrt(sum(a * a for a in v))
    return tuple(a / n for a in v)


def gun_parts_local():
    """Lists of local points per part (scene gun proxy in main.js)."""
    parts = {}
    # barrel as rings of points
    barrel = []
    for z0, z1, r in ((0, 23, 2.2), (23, 54, 8.5), (54, 100, 5.5), (100, 118, 12)):
        for z in (z0, z1):
            for k in range(12):
                a = 2 * math.pi * k / 12
                barrel.append((r * math.cos(a), r * math.sin(a), z))
    parts["barrel"] = barrel
    parts["body"] = box_corners((0, 0, 185.5), (17, 17, 67.5), (1, 0, 0), (0, 1, 0), (0, 0, 1))
    gs, ge = (0, -25, 172), (0, -111, 232)
    d = unit(tuple(b - a for a, b in zip(gs, ge)))
    c = tuple((a + b) / 2 for a, b in zip(gs, ge))
    length = math.dist(gs, ge) + 16
    perp = (0, -d[2], d[1])
    parts["grip"] = box_corners(c, (15, length / 2, 14), (1, 0, 0), d, perp)
    return parts


def project(p, view):
    """view: 'side' looks from +X toward -X (horizontal = -Y to the left? we use +Y right),
    'front' looks from -Y toward +Y (horizontal = X), 'plan' looks down (X right, Y up)."""
    x, y, z = p
    if view == "side":
        return (-y, z)       # tangent: -Y (gun side) to the right
    if view == "front":
        return (x, z)
    if view == "plan":
        return (x, y)
    raise ValueError(view)


def hull(points):
    pts = sorted(set((round(a, 3), round(b, 3)) for a, b in points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
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


def gun_polys(view, pose=(45, 30, -15), transform=None):
    polys = []
    for name, pts in gun_parts_local().items():
        world = [pose_point(p, *pose) for p in pts]
        world = [(w[0] - R_IN, w[1], w[2] - (6 * 25.4 - RECESS)) for w in world]   # relative to dot
        if transform:
            world = [transform(w) for w in world]
        polys.append((name, hull([project(w, view) for w in world])))
    return polys


def gun_point(local, view, pose=(45, 30, -15), transform=None):
    w = pose_point(local, *pose)
    w = (w[0] - R_IN, w[1], w[2] - (6 * 25.4 - RECESS))
    if transform:
        w = transform(w)
    return project(w, view)


class Svg:
    def __init__(self, width, height, xmin, xmax, ymin, ymax, title="", notes=None, top=34):
        self.top = top
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.s = min(width / (xmax - xmin), height / (ymax - ymin))
        self.w = width
        self.plot_h = (ymax - ymin) * self.s
        notes = notes or []
        self.h = int(self.top + self.plot_h + 16 + 15 * len(notes))
        self.items = []
        if title:
            self.items.append(f'<text x="10" y="22" font-size="15" font-weight="bold">{title}</text>')
        for i, ln in enumerate(notes):
            ln = ln.replace("&", "&amp;").replace("<", "&lt;")
            self.items.append(f'<text x="10" y="{self.top + self.plot_h + 20 + 15*i:.0f}" font-size="12" fill="#111">{ln}</text>')

    def tx(self, p):
        return ((p[0] - self.xmin) * self.s, self.top + self.plot_h - (p[1] - self.ymin) * self.s)

    def poly(self, pts, fill="#ddd", stroke="#333", sw=1, dash=None, opacity=1.0):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.tx(p) for p in pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<polygon points="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def line(self, a, b, stroke="#333", sw=1, dash=None, arrow=False):
        (x1, y1), (x2, y2) = self.tx(a), self.tx(b)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        mk = ' marker-end="url(#arr)"' if arrow else ""
        self.items.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}{mk}/>')

    def polyline(self, pts, stroke="#333", sw=1, dash=None, fill="none"):
        d = " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.tx(p) for p in pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<polyline points="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def rect(self, x0, y0, x1, y1, **kw):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)

    def circle(self, c, r, fill="none", stroke="#333", sw=1, dash=None):
        x, y = self.tx(c)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*self.s:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def dot(self, c, r_px=3, fill="#d00"):
        x, y = self.tx(c)
        self.items.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r_px}" fill="{fill}"/>')

    def text(self, p, s, size=11, anchor="start", color="#111", dx=0, dy=0):
        x, y = self.tx(p)
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.items.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{s}</text>')

    def arc(self, c, r, a0, a1, stroke="#333", sw=1, dash=None, n=40):
        pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
        self.polyline(pts, stroke=stroke, sw=sw, dash=dash)

    def raw_text_block(self, x_px, y_px, lines, size=11):
        for i, ln in enumerate(lines):
            ln = ln.replace("&", "&amp;").replace("<", "&lt;")
            self.items.append(f'<text x="{x_px}" y="{y_px + i*(size+3)}" font-size="{size}" fill="#111">{ln}</text>')

    def save(self, path):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="Helvetica, Arial, sans-serif">'
                '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
                '<path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>'
                f'<rect width="{self.w}" height="{self.h}" fill="#fff"/>')
        with open(path, "w") as f:
            f.write(head + "".join(self.items) + "</svg>\n")


def draw_gun(svg, view, pose=(45, 30, -15), transform=None, fill="#9bb7d4", opacity=0.9):
    for name, pts in gun_polys(view, pose, transform):
        svg.poly(pts, fill=fill if name != "grip" else "#7f9fc4", stroke="#234", sw=1, opacity=opacity)


def draw_tube_side(svg, x0=0.0):
    """Side view (looking along X): tube is a rectangle, y from -63.5..63.5 -> horizontal -y."""
    top = RECESS
    bottom = RECESS - TUBE_LEN
    svg.rect(-TUBE_R_OUT, bottom, TUBE_R_OUT, top, fill="#eee", stroke="#555")
    svg.line((-TUBE_R_OUT, 0), (TUBE_R_OUT, 0), stroke="#555", dash="4,3")


def draw_tube_front(svg):
    """Front view (looking along Y): wall at x in [0, 1.65] (dot side) and [-125.35, -123.7]."""
    top = RECESS
    bottom = RECESS - TUBE_LEN
    wall = 1.65
    for x0 in (0.0, -2 * R_IN - wall):
        svg.rect(x0, bottom, x0 + wall, top, fill="#bbb", stroke="#555", sw=0.8)
    svg.rect(-2 * R_IN + 0.25, -6.35, -0.25, 0, fill="#ccc", stroke="#555", sw=0.8)   # cap
