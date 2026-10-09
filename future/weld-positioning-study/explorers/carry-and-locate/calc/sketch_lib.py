"""Tiny SVG sketcher: the station drawn in three orthographic views from 3D points.

World frame = scene frame (+Z up, tube axis at the origin, dot on +X, tangent +/-Y),
but heights are drawn ABOVE THE BENCH (scene z + BENCH_Z) so the bench line is z=0.
Gun geometry is the scene's schematic proxy at a chosen pose (pose.py).
Views: plan (X right, Y up), elevation from +X (Y right, Z up), elevation from -Y (X right, Z up).
"""
import numpy as np
from html import escape
from pose import pose_point, rot_matrix, LOCAL, BENCH_Z, TUBE_OD, R_IN, TUBE_H, RECESS

S = 0.5  # px per mm


def bench(p):
    p = np.asarray(p, float)
    return np.array([p[0], p[1], p[2] + BENCH_Z])


class View:
    def __init__(self, name, ox, oy, axes, xr, zr, title):
        self.name, self.ox, self.oy, self.axes = name, ox, oy, axes
        self.xr, self.zr, self.title = xr, zr, title
        self.w = (xr[1] - xr[0]) * S
        self.h = (zr[1] - zr[0]) * S

    def xy(self, P):
        P = np.asarray(P, float)
        u = P[self.axes[0]]
        v = P[self.axes[1]]
        return (self.ox + (u - self.xr[0]) * S, self.oy + (self.zr[1] - v) * S)


class Sketch:
    def __init__(self, title, width=1180, height=860):
        self.title = title
        self.W, self.H = width, height
        self.items = []
        # views in bench coordinates
        self.views = [
            View("plan", 20, 60, (0, 1), (-340, 340), (-760, 280), "PLAN (looking down; +X = radial outward at the dot, +Y = tangent)"),
            View("elevY", 440, 60, (1, 2), (-760, 300), (0, 1000), "ELEVATION from +X (tangent Y to the right)"),
            View("elevX", 860, 60, (0, 2), (-300, 330), (0, 1000), "ELEVATION from -Y (radial X to the right)"),
        ]
        # fit: shrink views to share the canvas
        self.views[0].oy = 60
        self.views[1].ox = 20 + self.views[0].w + 30
        self.views[2].ox = self.views[1].ox + self.views[1].w + 30
        self.W = int(self.views[2].ox + self.views[2].w + 20)
        self.H = int(max(v.oy + v.h for v in self.views) + 170)

    # ---- primitives in 3D (bench coords) ----
    def line(self, a, b, color="#333", w=1.2, dash=None, views=None):
        self.items.append(("line", np.asarray(a, float), np.asarray(b, float), color, w, dash, views))

    def poly(self, pts, color="#333", w=1.2, dash=None, views=None, fill="none"):
        self.items.append(("poly", [np.asarray(p, float) for p in pts], color, w, dash, views, fill))

    def dot(self, p, color="#c00", r=3.5, views=None):
        self.items.append(("dot", np.asarray(p, float), color, r, views))

    def label(self, p, text, color="#111", dx=5, dy=-4, size=10.5, views=None, anchor="start"):
        self.items.append(("label", np.asarray(p, float), text, color, dx, dy, size, views, anchor))

    def arrow(self, a, b, color="#333", w=1.2, views=None):
        self.items.append(("arrow", np.asarray(a, float), np.asarray(b, float), color, w, views))

    def circle_h(self, center, r, color="#333", w=1.2, dash=None, n=72, views=None):
        """horizontal circle (constant z)"""
        c = np.asarray(center, float)
        pts = [c + r * np.array([np.cos(t), np.sin(t), 0]) for t in np.linspace(0, 2 * np.pi, n)]
        self.poly(pts, color, w, dash, views)

    def box(self, corners_local, R, origin, color="#333", w=1.2, fill="none", views=None):
        """8 corners -> draw all 12 edges"""
        pts = [origin + R @ c for c in corners_local]
        edges = [(0, 1), (1, 3), (3, 2), (2, 0), (4, 5), (5, 7), (7, 6), (6, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        for i, j in edges:
            self.line(pts[i], pts[j], color, w, None, views)

    # ---- the station ----
    def station(self, pose=(45, 30, -15), rotator=True, gun=True, cable=True):
        # bench line
        for v in self.views[1:]:
            pass
        self.line([-320, 0, 0], [330, 0, 0], "#888", 1, "2,3", views=("elevX",))
        self.line([0, -380, 0], [0, 280, 0], "#888", 1, "2,3", views=("elevY",))
        # rotator base (footprint 300 x 250; its orientation vs the station is free - drawn with motor at -X)
        bx0, bx1, by0, by1 = -180, 120, -125, 125
        self.poly([[bx0, by0, 36], [bx1, by0, 36], [bx1, by1, 36], [bx0, by1, 36], [bx0, by0, 36]], "#999", 1)
        for (x0, x1) in ((bx0, bx1),):
            self.poly([[x0, by0, 24], [x1, by0, 24], [x1, by0, 36], [x0, by0, 36], [x0, by0, 24]], "#999", 1, views=("elevX",))
            self.poly([[bx0, by0, 24], [bx0, by1, 24], [bx0, by1, 36], [bx0, by0, 36], [bx0, by0, 24]], "#999", 1, views=("elevY",))
        # motor tower (drawn at -X 125) and ground tower
        m = [-125, 0]
        self.poly([[m[0]-29, -29, 36], [m[0]+29, -29, 36], [m[0]+29, 29, 36], [m[0]-29, 29, 36], [m[0]-29, -29, 36]], "#aaa", 1, views=("plan",))
        self.poly([[m[0]-29, 0, 36], [m[0]+29, 0, 36], [m[0]+29, 0, 140], [m[0]-29, 0, 140], [m[0]-29, 0, 36]], "#aaa", 1, views=("elevX",))
        self.label([m[0], 0, 140], "motor tower", "#888", -20, -4, 9, views=("elevX", "plan"))
        # turntable + nest region
        self.circle_h([0, 0, 60], 82.5, "#bbb", 0.8, "3,3", views=("plan",))
        # tube: OD circle, bore circle, walls in elevation
        z0, z1 = BENCH_Z, BENCH_Z + TUBE_H
        zc = BENCH_Z + TUBE_H - RECESS
        self.circle_h([0, 0, z1], TUBE_OD / 2, "#1a4f8a", 1.6, views=("plan",))
        self.circle_h([0, 0, z1], R_IN, "#1a4f8a", 0.8, views=("plan",))
        for vname, ax in (("elevX", 0), ("elevY", 1)):
            for s in (-1, 1):
                a = [0, 0, z0]; b = [0, 0, z1]
                a[ax] = s * TUBE_OD / 2; b[ax] = s * TUBE_OD / 2
                self.line(a, b, "#1a4f8a", 1.6, views=(vname,))
                a2 = list(a); b2 = list(b); a2[ax] = s * R_IN; b2[ax] = s * R_IN
                self.line(a2, b2, "#1a4f8a", 0.6, views=(vname,))
            # cap
            c0 = [0, 0, zc]; c1 = [0, 0, zc]; c0[ax] = -R_IN; c1[ax] = R_IN
            self.line(c0, c1, "#1a4f8a", 2.2, views=(vname,))
            c0 = [0, 0, zc - 6.35]; c1 = [0, 0, zc - 6.35]; c0[ax] = -R_IN; c1[ax] = R_IN
            self.line(c0, c1, "#1a4f8a", 0.6, views=(vname,))
        self.label([0, 0, z0 + 20], "tube 5 in", "#1a4f8a", -22, 0, 9, views=("elevX", "elevY"))
        if gun:
            self.gun(pose, cable)

    def gun(self, pose=(45, 30, -15), cable=True, color="#444"):
        self.pose = pose
        R = rot_matrix(*pose)
        o = bench(pose_point(np.zeros(3), *pose))
        P = {k: bench(pose_point(v, *pose)) for k, v in LOCAL.items()}
        self.P = P
        # barrel sections
        self.line(P["nozzle_tip"], P["nozzle_back"], "#b36b00", 3.0)
        self.line(P["nozzle_back"], P["grad_tube_back"], color, 6.0)
        self.line(P["grad_tube_back"], P["barrel_back"], color, 4.0)
        self.line(P["barrel_back"], P["lens_back"], color, 8.0)
        # housing box 34 x 34 x 135 centred at z 185.5; local x = width, y = height
        hc = []
        for zz in (118, 253):
            for yy in (-17, 17):
                for xx in (-17, 17):
                    hc.append(np.array([xx, yy, zz]))
        # reorder to match box() edge convention: index bits (x,y) inner, z outer
        hc = [np.array([xx, yy, zz]) for zz in (118, 253) for yy in (-17, 17) for xx in (-17, 17)]
        self.box(hc, R, o, color, 1.4)
        # grip as a box between grip_start and grip_end, 30 wide, 28 deep
        gs, ge = LOCAL["grip_start"], LOCAL["grip_end"]
        d = (ge - gs) / np.linalg.norm(ge - gs)
        n = np.array([0, d[2], -d[1]])  # perpendicular in local YZ
        gc = []
        for t in (gs - 8 * d, ge + 8 * d):
            for k in (-14, 14):
                for xx in (-15, 15):
                    gc.append(t + k * n + np.array([xx, 0, 0]))
        self.box(gc, R, o, color, 1.1)
        # laser: nozzle tip to dot
        self.line(P["nozzle_tip"], P["dot"], "#d00", 1.2, "4,2")
        self.dot(P["dot"], "#d00", 3.5)
        # wire guide + wire: from wire brace down to dot (straight guide proxy)
        self.line(P["wire_brace"], P["dot"], "#0a7", 1.3)
        if cable:
            self.umbilical()

    def umbilical(self, saddle_center=None, radius=380, color="#6a3d9a"):
        """Umbilical leaves the grip butt along the grip direction, rises, arcs over a large saddle, falls to the cart."""
        pose = self.pose
        gs, ge = LOCAL["grip_start"], LOCAL["grip_end"]
        exit_local = LOCAL["grip_base"]
        d_local = (ge - gs) / np.linalg.norm(ge - gs)
        e = bench(pose_point(exit_local, *pose))
        e2 = bench(pose_point(exit_local + 120 * d_local, *pose))
        dirv = (e2 - e) / np.linalg.norm(e2 - e)
        # arc in the vertical plane containing the exit direction's horizontal part
        hdir = np.array([dirv[0], dirv[1], 0.0]); hdir /= np.linalg.norm(hdir)
        # control points: exit, along the exit direction, over a large saddle, down toward the cart
        top = e + 330 * hdir + np.array([0, 0, 330])
        ctrl = [e, e + 110 * dirv, e + 250 * hdir + np.array([0, 0, 290]), top,
                e + 420 * hdir + np.array([0, 0, 260]), e + 520 * hdir + np.array([0, 0, 40]),
                e + 560 * hdir + np.array([0, 0, -300]), e + 580 * hdir + np.array([0, 0, -e[2] + 60])]
        pts = []
        cp = [ctrl[0]] + ctrl + [ctrl[-1]]
        for i in range(1, len(cp) - 2):
            p0, p1, p2, p3 = cp[i - 1], cp[i], cp[i + 1], cp[i + 2]
            for t in np.linspace(0, 1, 12, endpoint=False):
                pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
        pts.append(ctrl[-1])
        self.poly(pts, color, 3.0)
        self.umb_pts = pts
        self.umb_top = top
        self.label(top, "umbilical over a large saddle (R >= 350 mm while emitting)", color, -120, -10, 9.5)
        # wire conduit beside it (offset 20 mm sideways)
        side = np.cross(hdir, [0, 0, 1])
        self.poly([p + 18 * side for p in pts[:-1]] + [pts[-1] + 18 * side + np.array([0, 0, 0])], "#0a7", 1.1, "5,3")

    # ---- output ----
    def _vis(self, views, v):
        return views is None or v.name in views

    def svg(self, notes=()):
        out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H + 16*len(notes)}" '
               f'viewBox="0 0 {self.W} {self.H + 16*len(notes)}" font-family="Helvetica, Arial, sans-serif">',
               f'<rect width="100%" height="100%" fill="#fbfbf8"/>',
               '<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
               '<path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>',
               f'<text x="20" y="28" font-size="17" font-weight="bold" fill="#111">{self.title}</text>']
        for v in self.views:
            out.append(f'<rect x="{v.ox:.1f}" y="{v.oy:.1f}" width="{v.w:.1f}" height="{v.h:.1f}" fill="none" stroke="#ddd"/>')
            out.append(f'<text x="{v.ox+4:.1f}" y="{v.oy-6:.1f}" font-size="10" fill="#666">{v.title}</text>')
            out.append(f'<clipPath id="c{v.name}"><rect x="{v.ox:.1f}" y="{v.oy:.1f}" width="{v.w:.1f}" height="{v.h:.1f}"/></clipPath>')
            out.append(f'<g clip-path="url(#c{v.name})">')
            for it in self.items:
                kind = it[0]
                if kind == "line":
                    _, a, b, col, w, dash, views = it
                    if not self._vis(views, v):
                        continue
                    (x1, y1), (x2, y2) = v.xy(a), v.xy(b)
                    da = f' stroke-dasharray="{dash}"' if dash else ""
                    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"{da} stroke-linecap="round"/>')
                elif kind == "poly":
                    _, pts, col, w, dash, views, fill = it
                    if not self._vis(views, v):
                        continue
                    s = " ".join(f"{x:.1f},{y:.1f}" for x, y in (v.xy(p) for p in pts))
                    da = f' stroke-dasharray="{dash}"' if dash else ""
                    out.append(f'<polyline points="{s}" fill="{fill}" stroke="{col}" stroke-width="{w}"{da} stroke-linejoin="round"/>')
                elif kind == "dot":
                    _, p, col, r, views = it
                    if not self._vis(views, v):
                        continue
                    x, y = v.xy(p)
                    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}"/>')
                elif kind == "arrow":
                    _, a, b, col, w, views = it
                    if not self._vis(views, v):
                        continue
                    (x1, y1), (x2, y2) = v.xy(a), v.xy(b)
                    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" marker-end="url(#ah)"/>')
            out.append('</g>')
            for it in self.items:
                if it[0] == "label":
                    _, p, text, col, dx, dy, size, views, anchor = it
                    if not self._vis(views, v):
                        continue
                    x, y = v.xy(p)
                    if not (v.ox - 5 <= x <= v.ox + v.w + 5 and v.oy - 5 <= y <= v.oy + v.h + 5):
                        continue
                    out.append(f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" font-size="{size}" fill="{col}" text-anchor="{anchor}">{escape(text)}</text>')
        y = self.H - 150
        for n in notes:
            out.append(f'<text x="20" y="{y:.0f}" font-size="11.5" fill="#222">{escape(n)}</text>')
            y += 16
        out.append('</svg>')
        return "\n".join(out)
