"""Draws sketches/isocentric-side.svg and sketches/isocentric-plan.svg for
ideas/isocentric-couch-and-gantry.md.

Scene frame (pose.js): mm, +Z up, tube axis on Z, the dot (isocenter) at
(61.85, 0, 146.05).  In this arrangement the vertical-axis setting lives in
the couch, so the gun side is drawn at vertical 0; the couch is drawn at
phi = 0.  Gun proxy = the scene's illustrative proxy at roll 45, hole dial 30.
Mechanism sizes are rough (labelled in the idea file).  Run: python3 sketch_isocentric.py
"""
import math
import numpy as np
from geometry import pose_point, proxy_points, JOINT, GRIP_BASE, R_OUT, TUBE_H, CAP_TOP

ROLL, HOLE, VERT = 45, 30, 0
I = JOINT
BASE_Z = -206.0            # baseplate top: rotator bench (-86) minus ~120 mm couch stack
E = math.radians(HOLE)
AX = np.array([0, -math.cos(E), math.sin(E)])     # grip axis direction (B frame)
BEAR = I + 300 * AX                               # roll bearing centre
# opening pose vertical -15 set at the work (branch B-Y): tube axis moved so the dot sits 15 deg round the corner
PSI = math.radians(15)
OFF = np.array([I[0] - I[0] * math.cos(PSI), -I[0] * math.sin(PSI), 0.0])   # (2.11, -16.01, 0)


def svg_header(w, h, title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family="Helvetica, Arial, sans-serif" font-size="12">',
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
            f'<text x="12" y="20" font-size="15" font-weight="bold">{title}</text>']


def poly(pts, stroke="#222", fill="none", w=1.2, dash=None, close=False):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    tag = "polygon" if close else "polyline"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<{tag} points="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{w}"{da}/>'


def text(x, y, s, size=11, anchor="start", color="#222"):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{s}</text>'


def circle(x, y, r, stroke="#222", fill="none", w=1.2, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" stroke="{stroke}" fill="{fill}" stroke-width="{w}"{da}/>'


def hull2d(pts):
    pts = sorted(set(map(tuple, np.round(pts, 2))))
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


def gun_parts_world():
    parts = proxy_points()
    return {k: np.array([pose_point(p, ROLL, HOLE, VERT) for p in v]) for k, v in parts.items()}


def side_view():
    # screen: sx = ox + y, sy = oy - z   (looking from +X toward the tube; -Y, the gun side, on the left)
    W, H = 1080, 820
    ox, oy = 660, 560
    P = lambda p: (ox + p[1], oy - p[2])
    out = svg_header(W, H, "Isocentric couch + gantry — side view (from +X), opening pose 45/30/−15 with −15° set by the couch Y slide")
    # baseplate
    out.append(poly([P((0, -480, BASE_Z)), P((0, 360, BASE_Z))], w=3))
    out.append(text(*P((0, 60, BASE_Z - 16)), "common baseplate (the 'fixed' reference)", 11))
    # couch stack under the dot
    out.append(poly([P((0, -55, BASE_Z)), P((0, 55, BASE_Z)), P((0, 55, BASE_Z + 80)), P((0, -55, BASE_Z + 80))], close=True, fill="#eee"))
    out.append(text(*P((0, 60, BASE_Z + 45)), "optional couch rotary table (original); default is the Y slide (B-Y)", 10))
    out.append(poly([P((0, -125, BASE_Z + 80)), P((0, 185, BASE_Z + 80)), P((0, 185, BASE_Z + 92)), P((0, -125, BASE_Z + 92))], close=True))
    out.append(poly([P((0, -120 + OFF[1], BASE_Z + 92)), P((0, 180 + OFF[1], BASE_Z + 92)), P((0, 180 + OFF[1], BASE_Z + 105)), P((0, -120 + OFF[1], BASE_Z + 105))], close=True, fill="#f4f4f4"))
    out.append(text(*P((0, 190, BASE_Z + 100)), "X slide (radial, micrometer stop)", 10))
    out.append(poly([P((0, -120 + OFF[1], BASE_Z + 105)), P((0, 180 + OFF[1], BASE_Z + 105)), P((0, 180 + OFF[1], -86)), P((0, -120 + OFF[1], -86))], close=True, fill="#f4f4f4"))
    out.append(text(*P((0, 190, -90)), "Y slide = yaw knob + load/unload drawer (kinematic stop)", 10))
    # rotator base + feet + tube
    out.append(poly([P((0, -120 + OFF[1], -62)), P((0, 180 + OFF[1], -62)), P((0, 180 + OFF[1], -50)), P((0, -120 + OFF[1], -50))], close=True))
    for yy in (-110, 150):
        out.append(poly([P((0, yy + OFF[1], -86)), P((0, yy + 30 + OFF[1], -86)), P((0, yy + 30 + OFF[1], -62)), P((0, yy + OFF[1], -62))], close=True))
    out.append(text(*P((0, 190, -50)), "existing rotator (unchanged) clamped to the drawer", 10))
    out.append(poly([P((0, 97 + OFF[1], -52)), P((0, 153 + OFF[1], -52)), P((0, 153 + OFF[1], 67)), P((0, 97 + OFF[1], 67))], close=True, stroke="#888"))
    out.append(text(*P((0, 158, 60)), "NEMA 23", 9, color="#666"))
    out.append(poly([P((0, -R_OUT + OFF[1], 0)), P((0, R_OUT + OFF[1], 0)), P((0, R_OUT + OFF[1], TUBE_H)), P((0, -R_OUT + OFF[1], TUBE_H)), P((0, -R_OUT + OFF[1], 0))], w=1.6))
    out.append(poly([P((0, -61.8 + OFF[1], CAP_TOP)), P((0, 61.8 + OFF[1], CAP_TOP))], w=1, dash="4 3"))
    out.append(text(*P((0, 70, 120)), "tube (dot on the near wall,", 10))
    out.append(text(*P((0, 70, 106)), "6.35 mm below the rim)", 10))
    # vertical couch axis
    out.append(poly([P((0, 0, BASE_Z)), P((0, 0, 520))], stroke="#1b6ac9", w=1, dash="8 4"))
    out.append(text(*P((0, 6, 505)), "couch axis (phi)", 10, color="#1b6ac9"))
    # hole-axis rotary table: its axis is perpendicular to this view, through the dot; table sits behind (+X)
    out.append(circle(*P(I), 55, stroke="#1b6ac9", dash="5 3"))
    out.append(text(*P((0, 40, 215)), "hole-axis rotary table", 10, color="#1b6ac9"))
    out.append(text(*P((0, 40, 202)), "behind the tube at +X; axis ⟂ view through dot", 10, color="#1b6ac9"))
    # Z stand (behind, drawn dashed)
    out.append(poly([P((0, -30, BASE_Z)), P((0, -30, 60)), P((0, 30, 60)), P((0, 30, BASE_Z))], stroke="#999", dash="3 3"))
    out.append(text(*P((0, -300, 30)), "Z stand + bracket: behind, at +X ≈ 300 (dashed)", 10, color="#777"))
    # gantry spoke (arm plate lies at x ~ +95, parallel to this view)
    out.append(poly([P(I), P(BEAR)], stroke="#1b6ac9", w=5))
    out.append(text(*P(I + 150 * AX + np.array([0, -150, -40])), "gantry arm spoke (plate at x ≈ +95)", 10, color="#1b6ac9"))
    # grip-axis line extended
    out.append(poly([P(I - 20 * AX), P(I + 380 * AX)], stroke="#c0392b", w=1, dash="6 3"))
    out.append(text(*P(I + 385 * AX + np.array([0, -60, 8])), "grip axis = roll axis", 10, color="#c0392b"))
    # roll bearing (seen obliquely): draw as ellipse approximated by the circle projected
    n = AX; u = np.array([1.0, 0, 0]); v = np.cross(n, u)
    ring = [P(BEAR + 45 * (math.cos(t) * u + math.sin(t) * v)) for t in np.linspace(0, 2 * math.pi, 40)]
    out.append(poly(ring, stroke="#c0392b", w=2, close=True))
    out.append(text(*P(BEAR + np.array([0, -250, 95])), "roll: two hinged clamshell rings on a printed sleeve", 10, color="#c0392b"))
    out.append(text(*P(BEAR + np.array([0, -250, 82])), "(R-C; a closed bearing cannot pass the gun)", 10, color="#c0392b"))
    # gun proxy
    for name, pts in gun_parts_world().items():
        hp = hull2d([P(p) for p in pts])
        out.append(poly(hp, stroke="#333", fill="#d9d9d9" if name in ("housing", "grip") else "#bbbbbb", w=1, close=True))
    tip = pose_point([0, 0, 0], ROLL, HOLE, VERT)
    back = pose_point([0, 0, 253], ROLL, HOLE, VERT)
    bdir = (back - tip) / np.linalg.norm(back - tip)
    # standoff rail parallel to the barrel, offset
    off = np.array([0, 0, 0])
    r0 = tip + 120 * bdir + np.array([0, 18, 22]); r1 = tip + 230 * bdir + np.array([0, 18, 22])
    out.append(poly([P(r0), P(r1)], stroke="#27ae60", w=4))
    out.append(text(*P(r1 + np.array([0, 8, 10])), "standoff rail ∥ barrel (micrometer stop,", 10, color="#27ae60"))
    out.append(text(*P(r1 + np.array([0, 8, -3])), "gravity holds the carriage on the stop)", 10, color="#27ae60"))
    # beam
    out.append(poly([P(tip), P(I)], stroke="#c0392b", w=1.5))
    out.append(circle(*P(I), 3, stroke="#c0392b", fill="#c0392b"))
    out.append(text(*P(I + np.array([0, -120, -8])), "dot = isocenter", 11, color="#c0392b"))
    # umbilical: leave the grip base 30 deg off the axis, then droop to the cart
    gb = pose_point(GRIP_BASE, ROLL, HOLE, VERT)
    u1 = gb + 90 * AX
    cab = [gb, u1, u1 + np.array([0, -110, 20]), u1 + np.array([0, -220, -40]), u1 + np.array([0, -280, -180]), u1 + np.array([0, -290, -330])]
    out.append(poly([P(p) for p in cab], stroke="#8e44ad", w=3))
    out.append(text(*P(u1 + np.array([0, -300, -355])), "umbilical to cart: hung from a spring", 10, color="#8e44ad"))
    out.append(text(*P(u1 + np.array([0, -300, -368])), "balancer, ≥350 mm bend radius, clamped", 10, color="#8e44ad"))
    out.append(text(*P(u1 + np.array([0, -300, -381])), "to the roll body, not to the gun", 10, color="#8e44ad"))
    # wire: from the bearing forward along the roll body to a guide aimed at the dot, arriving along the tangent
    wg0 = I + np.array([0, -60, 40]); wg1 = I + np.array([0, -9, 5])
    wire = [BEAR + np.array([0, 15, -25]), I + 150 * AX + np.array([0, 10, -30]), wg0, wg1, I]
    out.append(poly([P(p) for p in wire], stroke="#e67e22", w=1.6))
    out.append(text(*P(wg0 + np.array([0, -330, -60])), "wire guide on the roll body, tip micrometer", 10, color="#e67e22"))
    out.append(text(*P(wg0 + np.array([0, -330, -73])), "stage; standoff changes do not move it", 10, color="#e67e22"))
    # dimension: joint height above baseplate
    out.append(poly([P((0, 250, BASE_Z)), P((0, 250, CAP_TOP))], stroke="#555", w=0.8))
    out.append(text(*P((0, 256, (BASE_Z + CAP_TOP) / 2 + 60)), f"~{CAP_TOP - BASE_Z:.0f} mm dot above baseplate", 10, color="#555"))
    out.append(text(20, H - 40, "Rough sizes: couch stack ~120 mm (4-inch rotary table 80 mm + plate + two slides). Arm spoke 300 mm to the roll bearing. Gun = the scene's illustrative proxy at roll 45°, hole 30°.", 10, color="#555"))
    out.append(text(20, H - 24, "Colours: blue = rotations about the dot; red = beam / grip axis; green = standoff; orange = wire; purple = umbilical.", 10, color="#555"))
    out.append("</svg>")
    return "\n".join(out)


def plan_view():
    W, H = 900, 820
    ox, oy = 430, 400
    P = lambda p: (ox + p[0], oy - p[1])
    out = svg_header(W, H, "Isocentric couch + gantry — plan, opening pose: −15° set by the Y slide (tube axis at +2.1, −16.0)")
    # couch sweep circle
    out.append(circle(*P(I), 260, stroke="#aaa", dash="4 4"))
    out.append(text(*P(I + np.array([-170, 200, 0])), "rotator sweep at phi = ±45° (r ≈ 260 about the dot)", 10, color="#777"))
    # rotator base (scene x in [-125,125], y in [-120,180])
    out.append(poly([P(OFF + (-125, -120, 0)), P(OFF + (125, -120, 0)), P(OFF + (125, 180, 0)), P(OFF + (-125, 180, 0))], close=True))
    out.append(text(*P(OFF + (-120, 165, 0)), "rotator base 300 × 250 (stationary part of the rotator)", 10))
    out.append(poly([P(OFF + (-28, 97, 0)), P(OFF + (28, 97, 0)), P(OFF + (28, 153, 0)), P(OFF + (-28, 153, 0))], close=True, stroke="#888"))
    out.append(text(*P(OFF + (32, 125, 0)), "motor", 9, color="#666"))
    # tube
    tube = [P(OFF + (R_OUT * math.cos(t), R_OUT * math.sin(t), 0)) for t in np.linspace(0, 2 * math.pi, 90)]
    out.append(poly(tube, w=1.6, close=True))
    out.append(circle(*P(I), 3, stroke="#c0392b", fill="#c0392b"))
    out.append(text(*P(I + np.array([-60, 12, 0])), "dot", 11, color="#c0392b"))
    # couch rotary table under the dot
    out.append(circle(*P(I), 55, stroke="#1b6ac9", dash="5 3"))
    out.append(text(*P(I + np.array([-20, 62, 0])), "optional couch table (original), centred on the dot", 10, color="#1b6ac9"))
    # hole table at +X
    out.append(poly([P((105, -55)), P((185, -55)), P((185, 55)), P((105, 55))], close=True, stroke="#1b6ac9", fill="#eaf1fb"))
    out.append(poly([P((150, 55)), P((150, 150))], stroke="#1b6ac9", w=2))
    out.append(circle(*P((150, 160)), 10, stroke="#1b6ac9"))
    out.append(text(*P((165, 165)), "handwheel (hole angle)", 10, color="#1b6ac9"))
    out.append(text(*P((190, 10)), "hole-axis table", 10, color="#1b6ac9"))
    out.append(text(*P((190, -4)), "(axis = radial X line", 10, color="#1b6ac9"))
    out.append(text(*P((190, -18)), " through the dot)", 10, color="#1b6ac9"))
    out.append(poly([P((0, 0)), P((250, 0))], stroke="#1b6ac9", dash="8 4", w=1))
    # bracket to Z stand
    out.append(poly([P((185, -20)), P((300, -20)), P((300, 20)), P((185, 20))], close=True, stroke="#999", dash="3 3"))
    out.append(poly([P((290, -30)), P((330, -30)), P((330, 30)), P((290, 30))], close=True, stroke="#555", fill="#eee"))
    out.append(text(*P((290, -45)), "Z stand (outside sweep)", 10, color="#555"))
    # arm plate at x ~ 95 running along -Y (projection of the spoke)
    out.append(poly([P((95, 0)), P((95, BEAR[1])), P((61.85, BEAR[1]))], stroke="#1b6ac9", w=4))
    out.append(text(*P((100, -150)), "gantry arm plate (x ≈ 95, outboard of gun)", 10, color="#1b6ac9"))
    # roll bearing
    out.append(poly([P((61.85 - 45, BEAR[1] - 8)), P((61.85 + 45, BEAR[1] - 8)), P((61.85 + 45, BEAR[1] + 8)), P((61.85 - 45, BEAR[1] + 8))], close=True, stroke="#c0392b", w=2))
    out.append(text(*P((61.85 - 170, BEAR[1] - 30)), "roll on the grip axis: clamshell rings on a sleeve (R-C)", 10, color="#c0392b"))
    # gun
    for name, pts in gun_parts_world().items():
        hp = hull2d([P(p) for p in pts])
        out.append(poly(hp, stroke="#333", fill="#d9d9d9" if name in ("housing", "grip") else "#bbbbbb", w=1, close=True))
    out.append(text(*P((-300, -200)), "gun (roll 45°) leans in over the tube", 10))
    # camera on rotator base, far side
    cam = np.array([-70, 90, 260]) + OFF
    out.append(poly([P(cam), P(I)], stroke="#16a085", dash="2 3"))
    out.append(poly([P(cam + np.array([-12, -8, 0])), P(cam + np.array([12, -8, 0])), P(cam + np.array([12, 8, 0])), P(cam + np.array([-12, 8, 0]))], close=True, stroke="#16a085", fill="#dff3ef"))
    out.append(text(*P(cam + np.array([-150, 20, 0])), "dot camera on the rotator base,", 10, color="#16a085"))
    out.append(text(*P(cam + np.array([-150, 7, 0])), "looks across the bore at the corner", 10, color="#16a085"))
    # Y drawer arrow and X slide arrow
    out.append(poly([P((-200, -60)), P((-200, 60))], stroke="#555", w=1.5))
    out.append(text(*P((-300, 70)), "Y slide: yaw knob + drawer", 10, color="#555"))
    out.append(poly([P((-60, -140)), P((40, -140))], stroke="#555", w=1.5))
    out.append(text(*P((-230, -132)), "X slide (dot place, radial) →", 10, color="#555"))
    # umbilical and operator
    out.append(poly([P((61.85, BEAR[1] - 20)), P((40, -380)), P((-100, -390))], stroke="#8e44ad", w=3))
    out.append(text(*P((-330, -380)), "umbilical + wire conduit → welding cart", 10, color="#8e44ad"))
    out.append(text(*P((-330, -20)), "operator side: pedal + remote", 10))
    out.append(text(*P((-330, -34)), "trigger lever on the bench", 10))
    out.append(text(20, H - 24, "+X right, +Y up. Rough positions. Yaw moves only the black items (rotator, tube, camera) by the Y slide (+ X correction); the blue/red gantry side never moves in plan.", 10, color="#555"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    d = pathlib.Path(__file__).parent / "sketches"
    (d / "isocentric-side.svg").write_text(side_view())
    (d / "isocentric-plan.svg").write_text(plan_view())
    print("wrote", d / "isocentric-side.svg", d / "isocentric-plan.svg")
