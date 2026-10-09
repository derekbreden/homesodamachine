"""Plain SVG sketches for the workspace-as-structure explorer.

The gun silhouette is projected from the scene proxy (geom.py, opening pose
grip 45 / hole dial 30 / vertical -15). Everything else is a rough layout,
drawn to scale in millimetres; dimensions labelled "~" are proposals.

Frame: tube centre at plan origin, +X toward the far (back) side where the
dot is, tangent along Y, Z = 0 at the tube rim (= table surface in the
table-opening arrangements).
"""
import math
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import geom  # noqa: E402

POSE = (45, 30, -15)
RIM_Z = geom.RIM
R_IN = geom.R_IN
R_OD = geom.TUBE_OD / 2


# ---------------------------------------------------------------- geometry
def hull(points):
    pts = sorted(set((round(p[0], 3), round(p[1], 3)) for p in points))
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


def cyl_points(z0, z1, r, n=16):
    out = []
    for z in (z0, z1):
        for k in range(n):
            a = 2 * math.pi * k / n
            out.append(np.array([r * math.cos(a), r * math.sin(a), z]))
    return out


GUN_PARTS = {
    "nozzle": cyl_points(0, 54, 8.5),
    "tube": cyl_points(54, 100, 5.5),
    "lens": cyl_points(100, 118, 12),
    "housing": geom.box_corners((0, 0, 185.5), (34, 34, 135)),
    "grip": geom.grip_corners(),
}


def gun_world(pose=POSE, shift=(0, 0, 0)):
    roll, dial, vert = pose
    hp = dial - geom.HOLE_OFFSET
    parts = {}
    for k, pts in GUN_PARTS.items():
        w = [geom.pose_point(p, roll, hp, vert) for p in pts]
        parts[k] = [np.array([q[0], q[1], q[2] - RIM_Z]) + np.array(shift) for q in w]
    gb = geom.pose_point(geom.GRIP_BASE, roll, hp, vert)
    gb = np.array([gb[0], gb[1], gb[2] - RIM_Z]) + np.array(shift)
    dot = np.array([geom.JOINT[0], geom.JOINT[1], geom.JOINT[2] - RIM_Z]) + np.array(shift)
    return parts, gb, dot


# ---------------------------------------------------------------- svg
class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.items = []

    def add(self, s):
        self.items.append(s)

    def line(self, a, b, stroke="#222", width=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def poly(self, pts, fill="none", stroke="#222", width=1.2, dash=None, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)
        self.add(f'<polygon points="{s}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def path(self, d, stroke="#222", width=1.2, fill="none", dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" fill="{fill}"{dd}/>')

    def rect(self, x, y, w, h, fill="none", stroke="#222", width=1.2, dash=None, opacity=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def circle(self, c, r, fill="none", stroke="#222", width=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def text(self, p, s, size=11, anchor="start", color="#111", weight="normal"):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.add(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-family="Helvetica, Arial, sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{weight}">{s}</text>')

    def arrow(self, a, b, stroke="#222", width=1.2, head=7):
        self.line(a, b, stroke, width)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        for s in (+1, -1):
            q = (b[0] - head * math.cos(ang + s * 0.45), b[1] - head * math.sin(ang + s * 0.45))
            self.line(b, q, stroke, width)

    def save(self, name):
        body = "\n".join(self.items)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
               f'viewBox="0 0 {self.w} {self.h}">\n<rect width="100%" height="100%" fill="#ffffff"/>\n{body}\n</svg>\n')
        with open(os.path.join(HERE, name), "w") as f:
            f.write(svg)


class View:
    """Maps model (u, v) mm to svg px. u right, v up."""
    def __init__(self, svg, origin_px, scale, flip_u=False):
        self.s, self.o, self.k, self.fu = svg, origin_px, scale, flip_u

    def p(self, u, v):
        uu = -u if self.fu else u
        return (self.o[0] + uu * self.k, self.o[1] - v * self.k)

    def ps(self, pts):
        return [self.p(*q) for q in pts]


def draw_gun(view, parts, proj, fill="#f3d9a8", stroke="#7a4b00", label=True):
    order = ["grip", "housing", "lens", "tube", "nozzle"]
    for k in order:
        h = hull([proj(q) for q in parts[k]])
        view.s.poly(view.ps(h), fill=fill, stroke=stroke, width=1.0, opacity=0.9)


def plan_proj(q):
    return (q[0], q[1])


# ------------------------------------------------------------------ helpers
def title(s, text, sub=None):
    s.text((20, 28), text, size=16, weight="bold")
    if sub:
        s.text((20, 46), sub, size=11, color="#444")


def draw_cable(view, gb, direction, proj, length=260, bend=380, color="#1b5e20"):
    a = proj(gb)
    d = np.array(direction) / np.linalg.norm(direction)
    b = proj(gb + d * length)
    view.s.line(view.p(*a), view.p(*b), stroke=color, width=3)
    return b


# =================================================================== sketch 1
def sketch_table_opening():
    s = Svg(1200, 1010)
    title(s, "Table opening + countertop gantry (Derek's branch, developed)",
          "Gun proxy from the orientation scene at its opening pose (grip 45, hole 30, vertical -15). mm, to scale; '~' = proposal.")
    parts, gb, dot = gun_world()
    d = (gb - dot) / np.linalg.norm(gb - dot)
    k = 0.62
    # ---- plan: u = -Y (gun extends right), v = +X (far side up)
    v = View(s, (60 + 300 * k, 95 + 335 * k), k)
    def P(x, y):
        return v.p(-y, x)
    s.text((60, 80), "PLAN (from above).  Operator at the bottom (front edge); dot on the far (+X) wall.", size=11, weight="bold")
    s.poly([P(x, y) for x, y in [(-300, 300), (335, 300), (335, -800), (-300, -800)]], fill="#efe7da", stroke="#9b8563", width=1)
    s.text(P(-285, 290), "72 x 25 in bench top: 30 mm rubberwood on the VEVOR steel frame", size=10, color="#6b5a3a")
    s.circle(P(0, 0), 80 * k, fill="#ffffff", stroke="#9b8563", width=1.2)
    s.circle(P(0, 0), R_OD * k, stroke="#333", width=1.5)
    s.circle(P(0, 0), R_IN * k, stroke="#333", width=0.8, dash="3,2")
    s.text(P(-92, 0), "Ø160 opening", size=9, anchor="middle", color="#6b5a3a")
    box = [(-160, 185), (160, 185), (160, -185), (-160, -185)]
    s.poly([P(x, y) for x, y in box], stroke="#555", dash="6,4", width=1)
    for x, y in box:
        s.circle(P(x, y), 6, fill="#888", stroke="#333")
    s.text(P(175, 180), "4 posts / Tr8x2 screws under the top (dashed = below)", size=9, color="#444")
    s.text(P(-178, 0), "open face of the box: tube leaves toward the operator", size=9, anchor="middle", color="#444")
    for xr in (-205, 205):
        s.line(P(xr, -70), P(xr, -480), stroke="#1f4e9c", width=4)
    s.text(P(215, -280), "Y rail (MGN12) on the top", size=9, color="#1f4e9c")
    s.text(P(-222, -280), "Y rail", size=9, color="#1f4e9c")
    yb = -190
    s.line(P(-225, yb), P(225, yb), stroke="#1f4e9c", width=7)
    s.text(P(240, yb + 60), "gantry beam along X", size=9, color="#1f4e9c")
    s.poly([P(x, y) for x, y in [(-55, -150), (15, -150), (15, -235), (-55, -235)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.text(P(-75, -150), "carriage + pose saddle under the gun body", size=9, color="#1f4e9c")
    draw_gun(v, parts, lambda q: (-q[1], q[0]))
    s.circle(P(dot[0], dot[1]), 3.5, fill="#d00000", stroke="#d00000")
    s.text(P(dot[0] + 12, dot[1] + 6), "laser dot", size=10, color="#d00000")
    s.circle(P(gb[0], gb[1]), 3.5, fill="#1b5e20", stroke="#1b5e20")
    c1 = gb + d * 260
    s.line(P(gb[0], gb[1]), P(c1[0], c1[1]), stroke="#1b5e20", width=3)
    s.path(f"M {P(c1[0], c1[1])[0]:.1f} {P(c1[0], c1[1])[1]:.1f} Q {P(c1[0] - 20, -720)[0]:.1f} {P(c1[0] - 20, -720)[1]:.1f} {P(-60, -800)[0]:.1f} {P(-60, -800)[1]:.1f}",
           stroke="#1b5e20", width=3)
    s.text(P(-150, -520), "umbilical + wire conduit leave along the grip axis", size=9, color="#1b5e20")
    s.text(P(-168, -520), "(tangent, 30° up), >= 350 mm bend, off the bench end", size=9, color="#1b5e20")
    s.text(P(-230, -690), "to the welding cart at the bench end", size=10, color="#1b5e20")
    s.text(P(-330, -100), "OPERATOR", size=11, anchor="middle", weight="bold", color="#444")
    s.arrow(P(-250, 250), P(-180, 250), stroke="#666")
    s.text(P(-175, 245), "+X", size=10, color="#666")
    s.arrow(P(-250, 250), P(-250, 180), stroke="#666")
    s.text(P(-262, 175), "-Y", size=10, color="#666")

    # ---- elevation: operator's view toward +X; u = -Y, v = Z
    e = View(s, (60 + 300 * k, 560 + 300 * k), k)
    def E(y, z):
        return e.p(-y, z)
    s.text((60, 545), "ELEVATION (operator's view, looking toward +X).  Z = 0 at the rim = table surface.", size=11, weight="bold")
    s.poly([E(y, z) for y, z in [(300, 0), (80, 0), (80, -30), (300, -30)]], fill="#e2d4bc", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(-80, 0), (-800, 0), (-800, -30), (-80, -30)]], fill="#e2d4bc", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(R_OD, 0), (-R_OD, 0), (-R_OD, -152.4), (R_OD, -152.4)]], stroke="#333", width=1.5)
    s.poly([E(y, z) for y, z in [(R_IN, -6.35), (-R_IN, -6.35), (-R_IN, -12.7), (R_IN, -12.7)]], fill="#bbbbbb", stroke="#333")
    s.text(E(0, -80), "tube", size=10, anchor="middle")
    s.poly([E(y, z) for y, z in [(75, -152.4), (-75, -152.4), (-75, -190), (75, -190)]], fill="#dddddd", stroke="#555")
    s.poly([E(y, z) for y, z in [(125, -202.4), (-125, -202.4), (-125, -214.4), (125, -214.4)]], fill="#cfcfcf", stroke="#555")
    for y in (-110, 110):
        s.poly([E(yy, zz) for yy, zz in [(y - 12, -214.4), (y + 12, -214.4), (y + 12, -238.4), (y - 12, -238.4)]], fill="#cfcfcf", stroke="#555")
    s.text(E(290, -175), "rotator as built", size=9)
    s.poly([E(y, z) for y, z in [(185, -238.4), (-185, -238.4), (-185, -250.4), (185, -250.4)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.text(E(290, -265), "shelf; hole under the Ø90 purge passage", size=9, color="#1f4e9c")
    for y in (-185, 185):
        s.line(E(y, -30), E(y, -330), stroke="#444", width=3)
    s.text(E(-200, -320), "posts / screws, belt-synced", size=9, color="#444")
    s.arrow(E(-240, -245), E(-240, -175), stroke="#1f4e9c")
    s.arrow(E(-240, -175), E(-240, -245), stroke="#1f4e9c")
    s.text(E(-250, -205), "Z: standoff trim, and ~70 mm drop to unload", size=9, color="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-150, 0), (-235, 0), (-235, 22), (-150, 22)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-170, 22), (-210, 22), (-210, 62), (-170, 62)]], fill="#9fb6e0", stroke="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-160, 62), (-220, 62), (-205, 95), (-175, 95)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.text(E(-245, 30), "Y rail, X beam, carriage, pose saddle", size=9, color="#1f4e9c")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(dot[1], dot[2]), 3.5, fill="#d00000", stroke="#d00000")
    s.text(E(dot[1] + 10, dot[2] - 22), "dot, 6.35 below the rim", size=9, color="#d00000", anchor="end")
    s.circle(E(gb[1], gb[2]), 3.5, fill="#1b5e20", stroke="#1b5e20")
    c1 = gb + d * 260
    s.line(E(gb[1], gb[2]), E(c1[1], c1[2]), stroke="#1b5e20", width=3)
    s.path(f"M {E(c1[1], c1[2])[0]:.1f} {E(c1[1], c1[2])[1]:.1f} Q {E(-760, 330)[0]:.1f} {E(-760, 330)[1]:.1f} {E(-800, 60)[0]:.1f} {E(-800, 60)[1]:.1f}", stroke="#1b5e20", width=3)
    s.text(E(c1[1] - 10, c1[2] + 14), "umbilical + wire", size=9, color="#1b5e20")
    s.text(E(-260, 250), "grip base ~133 above the top, ~233 along -Y", size=9, color="#1b5e20")
    # notes
    x0 = 790
    notes = [
        "What each motion does at the dot (tangent pose):",
        "  X (gantry carriage)  across the seam, wall <-> cap",
        "  Y (gantry on rails)  along the tangent: = a vertical-",
        "                         axis turn of 0.93 deg/mm; radial",
        "                         error only dy^2/2R",
        "  Z (shelf)            height / standoff; in this pose",
        "                         moves the dot ~0.64 across and",
        "                         ~0.75 along the seam per mm",
        "",
        "Loads:",
        "  gun -> saddle -> carriage -> beam -> Y rails -> top",
        "  tube -> rotator -> shelf -> 4 posts -> top",
        "  the loop closes through the wood top",
        "  (drop-in-collar.svg repairs this)",
        "",
        "Tube change without touching the gun:",
        "  crank the shelf down ~70 mm, lift the tube",
        "  off the nest, slide it out of the open face;",
        "  reverse; crank back to the recorded number.",
        "",
        "Top-load alternative: slide the gantry -Y",
        "  150+ mm (the insensitive axis) to a stop.",
    ]
    for i, t in enumerate(notes):
        s.text((x0, 110 + 17 * i), t, size=11, weight="bold" if t.endswith(":") and not t.startswith(" ") else "normal")
    s.save("table-opening-gantry.svg")


# =================================================================== sketch 2
def sketch_collar():
    s = Svg(1000, 620)
    title(s, "Drop-in collar: close the gun-to-joint loop in one frame, not in the bench top",
          "Section through the opening, looking toward +X. The bench top only carries the collar's weight.")
    e = View(s, (560, 250), 0.9)
    def E(y, z):
        return e.p(-y, z)
    parts, gb, dot = gun_world()
    # bench top
    s.poly([E(y, z) for y, z in [(420, 0), (130, 0), (130, -30), (420, -30)]], fill="#efe7da", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(-130, 0), (-520, 0), (-520, -30), (-130, -30)]], fill="#efe7da", stroke="#9b8563")
    s.text(E(380, -50), "bench top (wood)", size=10, color="#6b5a3a")
    # collar frame: flange plate on top of bench, 12 mm; ring walls down
    red = "#b00020"
    s.poly([E(y, z) for y, z in [(200, 12), (-400, 12), (-400, 0), (-80, 0), (-80, -12), (80, -12), (80, 0), (200, 0)]],
           fill="#f6c7cf", stroke=red, width=1.5)
    s.text(E(-395, 40), "collar plate (MIC-6 1/2 in or steel 3/8 in, laser-cut opening and holes)", size=10, color=red, anchor="end")
    for y in (-120, 120):
        s.poly([E(yy, z) for yy, z in [(y - 10, 0), (y + 10, 0), (y + 10, -300), (y - 10, -300)]], fill="#f6c7cf", stroke=red, width=1.5)
    s.text(E(130, -290), "posts hang from the collar, not the wood", size=10, color=red)
    # three pads under flange sitting on wood
    for y in (170, -250, -380):
        s.poly([E(yy, z) for yy, z in [(y - 12, 0), (y + 12, 0), (y + 12, -4), (y - 12, -4)]], fill="#333", stroke="#333")
    s.text(E(-240, -20), "3 pads on the wood (kinematic rest; wood only supports)", size=9, color="#333")
    # tube + rotator + shelf
    s.poly([E(y, z) for y, z in [(R_OD, 0), (-R_OD, 0), (-R_OD, -152.4), (R_OD, -152.4)]], stroke="#333", width=1.5)
    s.poly([E(y, z) for y, z in [(R_IN, -6.35), (-R_IN, -6.35), (-R_IN, -12.7), (R_IN, -12.7)]], fill="#bbb", stroke="#333")
    s.poly([E(y, z) for y, z in [(75, -152.4), (-75, -152.4), (-75, -214.4), (75, -214.4)]], fill="#ddd", stroke="#555")
    s.poly([E(y, z) for y, z in [(110, -214.4), (-110, -214.4), (-110, -238.4), (110, -238.4)]], fill="#ddd", stroke="#555")
    s.poly([E(y, z) for y, z in [(130, -238.4), (-130, -238.4), (-130, -250.4), (130, -250.4)]], fill="#f6c7cf", stroke=red, width=1.5)
    s.text(E(0, -270), "shelf (Z on 4 synced screws)", size=10, anchor="middle", color=red)
    # gun on rails on collar plate
    s.poly([E(y, z) for y, z in [(-150, 12), (-240, 12), (-240, 34), (-150, 34)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-165, 34), (-225, 34), (-210, 80), (-180, 80)]], fill="#c9d7f0", stroke="#1f4e9c")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(dot[1], dot[2]), 3.5, fill="#d00000", stroke="#d00000")
    # loop path
    loop = [(dot[1], dot[2]), (-40, 60), (-195, 60), (-195, 6), (-120, 6), (-120, -244), (0, -244), (0, -160), (40, -20), (dot[1], dot[2])]
    s.path("M " + " L ".join(f"{E(y, z)[0]:.1f} {E(y, z)[1]:.1f}" for y, z in loop), stroke=red, width=2.2, dash="7,4")
    s.text(E(-10, -130), "structural loop", size=11, color=red, weight="bold")
    # mag base
    s.poly([E(y, z) for y, z in [(110, 12), (160, 12), (160, 52), (110, 52)]], fill="#888", stroke="#333")
    s.line(E(135, 52), E(80, 90), stroke="#333", width=2)
    s.line(E(80, 90), E(55, 2), stroke="#333", width=2)
    s.text(E(165, 60), "indicator base on the collar: reads the bore lip in the gun's frame", size=9, anchor="end")
    s.text((40, 590), "A lean or bump on the bench tilts the collar as one body: gun and joint move together. The wood top can creep or swell without entering the loop.", size=11)
    s.save("drop-in-collar.svg")


# =================================================================== sketch 3
def sketch_sled():
    s = Svg(1180, 700)
    title(s, "Countertop sled: the plane carries Z and the two tilts; the gun slides in X / Y",
          "Three ball feet on a flat reference plate at rim height; a fence sets X and heading; a stop or micrometer sets Y.")
    parts, gb, dot = gun_world()
    # plan
    v = View(s, (300, 300), 0.8)
    def P(x, y):
        return v.p(-y, x)
    s.text((40, 72), "PLAN", size=11, weight="bold")
    plate = [(-150, 110), (150, 110), (150, -330), (-150, -330)]
    s.poly([P(x, y) for x, y in plate], fill="#e8eef4", stroke="#4a6378")
    s.circle(P(0, 0), 78 * 0.8, fill="#ffffff", stroke="#4a6378")
    s.text(P(-140, 100), "reference plate with tube opening (MIC-6 / granite / steel)", size=9, color="#4a6378")
    s.circle(P(0, 0), R_OD * 0.8, stroke="#333", width=1.4)
    draw_gun(v, parts, lambda q: (-q[1], q[0]))
    feet = [(40, -95), (-80, -250), (40, -260)]
    for x, y in feet:
        s.circle(P(x, y), 6, fill="#222", stroke="#222")
    s.poly([P(x, y) for x, y in feet], stroke="#222", dash="4,3", width=1)
    s.text(P(48, -92), "F1", size=10)
    s.text(P(-88, -262), "F3", size=10)
    s.text(P(48, -266), "F2", size=10)
    # fence along Y at x = 95
    s.line(P(-112, -90), P(-112, -320), stroke="#8a2be2", width=5)
    s.text(P(-128, -300), "fence on the operator side: two micrometers set X and heading", size=9, color="#8a2be2")
    s.circle(P(-102, -120), 4, fill="#8a2be2", stroke="#8a2be2")
    s.circle(P(-102, -280), 4, fill="#8a2be2", stroke="#8a2be2")
    s.arrow(P(60, -345), P(60, -300), stroke="#8a2be2")
    s.text(P(75, -350), "Y stop / micrometer", size=9, color="#8a2be2")
    s.arrow(P(-20, -200), P(-70, -240), stroke="#b35900")
    s.text(P(-10, -175), "preload spring (toward fence + stop)", size=9, color="#b35900")
    s.circle(P(dot[0], dot[1]), 3.5, fill="#d00000", stroke="#d00000")
    s.circle(P(gb[0], gb[1]), 3.5, fill="#1b5e20", stroke="#1b5e20")
    d = (gb - dot) / np.linalg.norm(gb - dot)
    c1 = gb + d * 120
    s.line(P(gb[0], gb[1]), P(c1[0], c1[1]), stroke="#1b5e20", width=3)
    s.rect(*P(c1[0] + 15, c1[1] + 10), 20, 26, fill="#1b5e20")
    s.text(P(c1[0] + 40, c1[1] - 40), "cable anchor on plate, slack loop to sled", size=9, color="#1b5e20")
    s.text(P(-170, 0), "OPERATOR", size=11, anchor="middle", weight="bold", color="#444")
    # elevation
    e = View(s, (760, 420), 0.8)
    def E(y, z):
        return e.p(-y, z)
    s.text((620, 72), "ELEVATION (looking toward +X)", size=11, weight="bold")
    s.poly([E(y, z) for y, z in [(110, 0), (78, 0), (78, -25), (110, -25)]], fill="#e8eef4", stroke="#4a6378")
    s.poly([E(y, z) for y, z in [(-78, 0), (-330, 0), (-330, -25), (-78, -25)]], fill="#e8eef4", stroke="#4a6378")
    s.poly([E(y, z) for y, z in [(R_OD, 0), (-R_OD, 0), (-R_OD, -152.4), (R_OD, -152.4)]], stroke="#333", width=1.4)
    s.poly([E(y, z) for y, z in [(R_IN, -6.35), (-R_IN, -6.35), (-R_IN, -12.7), (R_IN, -12.7)]], fill="#bbb", stroke="#333")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    # sled shell outline around housing/grip + legs
    shell_pts = []
    for k2 in ("housing", "grip", "lens"):
        shell_pts += [(-q[1], q[2]) for q in parts[k2]]
    sh = hull(shell_pts)
    cx = sum(p[0] for p in sh) / len(sh); cz = sum(p[1] for p in sh) / len(sh)
    grown = [(cx + (p[0] - cx) * 1.12, cz + (p[1] - cz) * 1.12) for p in sh]
    s.poly(e.ps(grown), stroke="#555", width=1.2, dash="5,3")
    s.text(e.p(cx + 40, cz + 115), "printed shell (dashed)", size=9, color="#555")
    for (x, y) in feet:
        top_z = 95 if y > -150 else 125
        s.line(E(y, 0), E(y, top_z), stroke="#222", width=4)
        s.circle(E(y, 4), 5, fill="#222", stroke="#222")
    s.text(E(-95, -45), "ball feet on plate (Z + 2 tilts from 3 screw heights)", size=9)
    s.circle(E(dot[1], dot[2]), 3.5, fill="#d00000", stroke="#d00000")
    s.circle(E(gb[1], gb[2]), 3.5, fill="#1b5e20", stroke="#1b5e20")
    c1 = gb + d * 140
    s.line(E(gb[1], gb[2]), E(c1[1], c1[2]), stroke="#1b5e20", width=3)
    s.path(f"M {E(c1[1], c1[2])[0]:.1f} {E(c1[1], c1[2])[1]:.1f} Q {E(-470, 330)[0]:.1f} {E(-470, 330)[1]:.1f} {E(-440, 30)[0]:.1f} {E(-440, 30)[1]:.1f}", stroke="#1b5e20", width=3)
    s.rect(*E(-430, 30), 16, 22, fill="#1b5e20")
    s.text(E(-445, 45), "anchor", size=9, color="#1b5e20")
    # lift-off hinge
    s.arrow(E(-120, 260), E(-60, 300), stroke="#b35900")
    s.text(E(-40, 300), "lift-off: tip about the rear feet (F2-F3 line) and set back down", size=9, color="#b35900")
    s.text((620, 640), "Optional pusher gantry: grips the sled through a vertical pin in a bushing, so it sets X / Y", size=10)
    s.text((620, 656), "but carries no weight or moment. Plane = weight, height, tilt.  Gantry = in-plane position only.", size=10)
    s.save("countertop-sled.svg")


# =================================================================== sketch 4
def sketch_moving_shelf():
    s = Svg(1180, 660)
    title(s, "Gun as structure, work moves: fixed pose saddle on a bridge, XY + Z under the rotator",
          "Left: elevation. Right: why a tangent (Y) slide of the work is a turn about the vertical axis through the dot.")
    parts, gb, dot = gun_world()
    e = View(s, (380, 300), 0.62)
    def E(y, z):
        return e.p(-y, z)
    s.poly([E(y, z) for y, z in [(330, 0), (100, 0), (100, -30), (330, -30)]], fill="#efe7da", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(-100, 0), (-520, 0), (-520, -30), (-100, -30)]], fill="#efe7da", stroke="#9b8563")
    s.text(E(320, -45), "top with Ø200 opening (travel room)", size=9, color="#6b5a3a")
    # bridge
    s.poly([E(y, z) for y, z in [(-140, 0), (-150, 0), (-150, 100), (-140, 100)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-150, 100), (-300, 100), (-300, 115), (-150, 115)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.poly([E(y, z) for y, z in [(-300, 0), (-310, 0), (-310, 115), (-300, 115)]], fill="#c9d7f0", stroke="#1f4e9c")
    s.text(E(-320, 130), "rigid bridge + pose saddle bolted to the collar / top: gun never moves", size=9, color="#1f4e9c")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(dot[1], dot[2]), 3.5, fill="#d00000", stroke="#d00000")
    s.circle(E(gb[1], gb[2]), 3.5, fill="#1b5e20", stroke="#1b5e20")
    d = (gb - dot) / np.linalg.norm(gb - dot)
    c1 = gb + d * 120
    s.line(E(gb[1], gb[2]), E(c1[1], c1[2]), stroke="#1b5e20", width=3)
    s.rect(*E(c1[1] + 5, c1[2] + 12), 18, 24, fill="#1b5e20")
    s.text(E(c1[1] - 25, c1[2] + 8), "cables clamped to structure", size=9, color="#1b5e20")
    # tube / rotator
    s.poly([E(y, z) for y, z in [(R_OD, 0), (-R_OD, 0), (-R_OD, -152.4), (R_OD, -152.4)]], stroke="#333", width=1.4)
    s.poly([E(y, z) for y, z in [(R_IN, -6.35), (-R_IN, -6.35), (-R_IN, -12.7), (R_IN, -12.7)]], fill="#bbb", stroke="#333")
    s.poly([E(y, z) for y, z in [(75, -152.4), (-75, -152.4), (-75, -214.4), (75, -214.4)]], fill="#ddd", stroke="#555")
    s.poly([E(y, z) for y, z in [(125, -214.4), (-125, -214.4), (-125, -238.4), (125, -238.4)]], fill="#ddd", stroke="#555")
    # cross slide
    s.poly([E(y, z) for y, z in [(225, -238.4), (-225, -238.4), (-225, -268), (225, -268)]], fill="#b7c9a8", stroke="#3d5a2a")
    s.poly([E(y, z) for y, z in [(150, -268), (-150, -268), (-150, -310), (150, -310)]], fill="#b7c9a8", stroke="#3d5a2a")
    s.text(E(235, -262), "compound cross-slide (X across seam, Y along tangent)", size=9, color="#3d5a2a", anchor="end")
    s.poly([E(y, z) for y, z in [(160, -310), (-160, -310), (-160, -330), (160, -330)]], fill="#c9d7f0", stroke="#1f4e9c")
    for y in (-160, 160):
        s.line(E(y, -30), E(y, -380), stroke="#444", width=3)
    s.text(E(170, -350), "Z: 4-post shelf (or lab jack)", size=9, color="#1f4e9c", anchor="end")
    # right: Y = vertical rotation diagram (tube frame, plan, far side up)
    v = View(s, (900, 380), 1.6)
    def P(x, y):
        return v.p(-y, x)
    s.circle(P(0, 0), R_IN * 1.6, stroke="#333", width=1.2)
    s.circle(P(0, 0), 2, fill="#333")
    s.line(P(R_IN, 0), P(R_IN, -95), stroke="#d00000", width=2)
    s.circle(P(R_IN, 0), 3, fill="#d00000", stroke="#d00000")
    dy = 20.0
    phi = math.atan2(dy, R_IN)
    # the same gun line after the work moves -dy along Y: in the tube frame the gun sits dy toward +Y
    px, py = R_IN * math.cos(phi), R_IN * math.sin(phi)
    s.line(P(px, py), P(px, py - 95), stroke="#d00000", width=2, dash="6,3")
    s.circle(P(px, py), 3, fill="#1f4e9c", stroke="#1f4e9c")
    tx, ty = math.sin(phi), -math.cos(phi)
    s.line(P(px, py), P(px + 95 * tx, py + 95 * ty), stroke="#1f4e9c", width=1.5)
    s.text((760, 150), "solid red: gun line, set tangent at the dot", size=10, color="#d00000")
    s.text((760, 166), "dashed red: the same gun line after the work slides dy along Y", size=10, color="#d00000")
    s.text((760, 182), "   (plus dx = dy^2/2R so the dot lands on the corner again)", size=10, color="#d00000")
    s.text((760, 198), "blue: local tangent at the new contact point", size=10, color="#1f4e9c")
    s.text(P(-R_IN - 18, 0), "angle between gun line and local tangent = atan(dy/R) = 0.93 deg per mm", size=10, anchor="middle")
    s.text(P(-R_IN - 32, 0), "radial correction dy^2/2R: 1 mm -> 0.008 mm, 10 mm -> 0.8 mm", size=10, anchor="middle")
    s.text(P(-R_IN - 46, 0), "(drawn for dy = 20 mm, 18 deg; R = 61.85 mm bore radius)", size=9, anchor="middle", color="#444")
    s.save("fixed-gun-moving-shelf.svg")


# =================================================================== sketch 5
def sketch_lid():
    s = Svg(900, 520)
    title(s, "Lidded mouth (seed): a stationary lid over the turning tube carries the ports",
          "Gun port, camera port, argon / extraction port. The lid hangs from the collar with a 2-5 mm gap above the rim.")
    parts, gb, dot = gun_world()
    e = View(s, (470, 230), 0.9)
    def E(y, z):
        return e.p(-y, z)
    s.poly([E(y, z) for y, z in [(R_OD, 0), (-R_OD, 0), (-R_OD, -152.4), (R_OD, -152.4)]], stroke="#333", width=1.4)
    s.poly([E(y, z) for y, z in [(R_IN, -6.35), (-R_IN, -6.35), (-R_IN, -12.7), (R_IN, -12.7)]], fill="#bbb", stroke="#333")
    s.poly([E(y, z) for y, z in [(95, 4), (-95, 4), (-95, 12), (95, 12)]], fill="#f6c7cf", stroke="#b00020", width=1.5)
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(dot[1], dot[2]), 3.5, fill="#d00000", stroke="#d00000")
    s.poly([E(y, z) for y, z in [(60, 12), (35, 12), (35, 60), (60, 60)]], fill="#ddd", stroke="#333")
    s.text(E(62, 70), "camera port", size=9)
    s.text(E(96, 20), "lid (stationary)", size=10, color="#b00020")
    s.text(E(-100, -30), "gun port: slot in the lid the nozzle passes through;", size=9)
    s.text(E(-100, -44), "a port ring can locate the nose (pool-cue bridge)", size=9)
    s.text((40, 490), "Contains most back-reflection above the mouth, gives a fixed camera and gas geometry, and gives a place to locate the nose.", size=10)
    s.save("lidded-mouth.svg")


if __name__ == "__main__":
    sketch_table_opening()
    sketch_collar()
    sketch_sled()
    sketch_moving_shelf()
    sketch_lid()
    print("written")
