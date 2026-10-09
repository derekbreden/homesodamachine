"""Generate the who-moves-what sketches from the pose.js port in geometry.py.

The gun outline is the capsule proxy (drawing-scaled estimate). Mechanism parts
(stand, arc, seat, stages) are schematic and labelled as such in the SVGs.
Run: tools/cad-venv/bin/python sketches.py   (writes sketches/*.svg)
"""
import os
import numpy as np
from geometry import pose_point, world, FEATURES, CAPSULES, R_IN, R_OUT, BENCH, RIM, CAP_TOP, FIBER_DIR_LOCAL

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "sketches")
os.makedirs(OUT, exist_ok=True)

INK = "#222"
GUN = "#3a6ea5"
WORK = "#8a5a2b"
MECH = "#2e7d32"
CABLE = "#b23b3b"
NOTE = "#555"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.items = [f'<rect width="{w}" height="{h}" fill="#fcfcf8"/>',
                      f'<text x="12" y="22" font-size="15" font-weight="bold" fill="{INK}">{title}</text>']

    def line(self, a, b, color=INK, w=1.2, dash=None, op=1.0, cap="butt"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{color}" stroke-width="{w:.1f}" stroke-opacity="{op}" stroke-linecap="{cap}"{d}/>')

    def poly(self, pts, color=INK, fill="none", w=1.2, op=1.0, dash=None, closed=True):
        tag = "polygon" if closed else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.items.append(f'<{tag} points="{p}" stroke="{color}" fill="{fill}" stroke-width="{w}" fill-opacity="{op}"{d}/>')

    def circle(self, c, r, color=INK, fill="none", w=1.2, dash=None, op=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.items.append(f'<circle cx="{c[0]:.1f}" cy="{c[1]:.1f}" r="{r:.1f}" stroke="{color}" fill="{fill}" stroke-width="{w}" fill-opacity="{op}"{d}/>')

    def arc(self, c, r, a0, a1, color=INK, w=1.2, dash=None):
        pts = [(c[0] + r * np.cos(np.radians(a)), c[1] - r * np.sin(np.radians(a))) for a in np.linspace(a0, a1, 60)]
        self.poly(pts, color=color, w=w, dash=dash, closed=False)

    def text(self, p, s, color=NOTE, size=11, anchor="start", bold=False):
        b = ' font-weight="bold"' if bold else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.items.append(f'<text x="{p[0]:.1f}" y="{p[1]:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}"{b}>{s}</text>')

    def arrow(self, a, b, color=INK, w=1.4):
        self.line(a, b, color, w)
        v = np.array(b, float) - np.array(a, float)
        n = v / (np.linalg.norm(v) + 1e-9)
        p = np.array([-n[1], n[0]])
        tip = np.array(b, float)
        self.poly([tip, tip - 8 * n + 4 * p, tip - 8 * n - 4 * p], color=color, fill=color, op=1.0)

    def save(self, name):
        body = "\n".join(self.items)
        with open(os.path.join(OUT, name), "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" font-family="Helvetica, Arial, sans-serif">\n{body}\n</svg>\n')


def gun_2d(svg, proj, pose, op=0.35, color=GUN, lift=0.0, shift=(0, 0)):
    for name, (a, b, rad) in CAPSULES.items():
        pa = world(a, pose) + np.array([shift[0], shift[1], lift])
        pb = world(b, pose) + np.array([shift[0], shift[1], lift])
        svg.line(proj(pa), proj(pb), color=color, w=2 * rad * SCALE, op=op, cap="round")


SCALE = 1.0

# ---------------------------------------------------------------- S1 plan: yaw by moving the work
def s1():
    global SCALE
    SCALE = 1.8
    W, H = 820, 600
    s = Svg(W, H, "S1 - Plan: sliding the work along the tangent turns the relative yaw (tube symmetry)")
    ox, oy = 230, 250

    def P(p):
        return (ox + SCALE * p[0], oy - SCALE * p[1])

    station = np.array([R_IN, 0.0])
    for phi, col, lab in ((0, WORK, "work at phi = 0: gun tangent (relative yaw 0)"), (15, "#c77d2e", "work moved 16.0 mm along -Y and 2.1 mm toward +X: relative yaw -15")):
        p = np.radians(phi)
        c = station - R_IN * np.array([np.cos(p), np.sin(p)])
        s.circle(P(c), R_IN * SCALE, color=col, w=1.3, dash=None if phi == 0 else "6,4")
        s.circle(P(c), R_OUT * SCALE, color=col, w=0.8, dash=None if phi == 0 else "6,4")
        s.circle(P(c), 2.5, color=col, fill=col)
        tdir = np.array([-np.sin(p), np.cos(p)])
        s.line(P(station - 70 * tdir), P(station + 70 * tdir), color=col, w=1, dash="3,3")
    s.text(P((-60, 72)), "tube at phi = 0", WORK)
    s.text(P((-66, -80)), "tube shifted (phi = 15 deg)", "#c77d2e")
    gun_2d(s, lambda q: P(q[:2]), (45, 30, 0), op=0.30)
    s.circle(P(station), 4, color="#d00", fill="#d00")
    s.text((P(station)[0] - 60, P(station)[1] - 150), "station point P (dot)", "#d00", 11)
    s.text((P(station)[0] - 60, P(station)[1] - 136), "fixed in the room", "#d00", 11)
    s.line((P(station)[0] - 10, P(station)[1] - 132), P(station), "#d00", 0.8)
    s.text(P((-120, -150)), "gun (grip 45, hole dial 30) - orientation fixed in the room", GUN)
    s.arrow(P((0, 0)), P((2.1, -16.0)), color="#c77d2e")
    x0 = 440
    lines = ["Rotation about the tube axis changes nothing (the joint",
             "is a circle on that axis). So moving the WORK along",
             "the tangent by r*sin(phi) and toward the station by",
             "r*(1-cos(phi)) keeps the seam through P and turns the",
             "local tangent by phi under a gun that never turns.",
             "",
             "  1.08 mm of slide per degree of yaw (r = 61.85 mm)",
             "  +/-15 deg  = +/-16.0 mm slide, 2.1 mm correction",
             "  +/-30 deg  = +/-30.9 mm slide, 8.3 mm correction",
             "",
             "Consequences:",
             " - any X/Y carrier (gantry, compound table) already",
             "   owns the vertical-axis rotation; no yaw bearing",
             " - a 1 mm Y error IS a 0.93 deg yaw error; Y is not",
             "   'free' just because the tube spins",
             " - yaw is gravity-neutral, so the work can take it",
             "   without changing the downhand puddle"]
    for i, l in enumerate(lines):
        s.text((x0, 70 + 17 * i), l, INK if i < 5 else NOTE, 11.5)
    s.text((12, H - 12), "Plan view, +X right, +Y up. Gun = capsule proxy from the manual drawing (estimate). Tube circles: ID/OD from the repo.", NOTE, 10)
    s.save("s1-plan-yaw-by-work-slide.svg")


# ---------------------------------------------------------------- side-view helpers (viewer at +X: right = +Y, up = Z)
def side_proj(ox, oy, lift):
    def P(p):
        return (ox + SCALE * p[1], oy - SCALE * (p[2] - BENCH + lift))
    return P


def draw_tube_side(s, P, shift_y=0.0, lift=0.0, label=True):
    z0 = BENCH - lift  # unused; heights are relative to bench in P
    zb = 0.0 + 86.0      # tube bottom above the rotator's own bench plane
    # tube outline (section through the axis, seen from +X)
    y0, y1 = shift_y - R_OUT, shift_y + R_OUT
    zt = RIM
    zbot = RIM - 152.4
    s.poly([P((0, y0, zbot)), P((0, y1, zbot)), P((0, y1, zt)), P((0, y0, zt))], color=WORK, w=1.2)
    s.poly([P((0, shift_y - R_IN, CAP_TOP - 6.35)), P((0, shift_y + R_IN, CAP_TOP - 6.35)), P((0, shift_y + R_IN, CAP_TOP)), P((0, shift_y - R_IN, CAP_TOP))], color=WORK, fill=WORK, op=0.25)
    if label:
        s.text(P((0, y1 + 6, zt - 20)), "tube + recessed plate", WORK, 10)


def draw_rotator_side(s, P, shift_y=0.0):
    # base bottom 24 above its support, 12 thick; tube bottom 86 above support (repo: rim 238.4 above support)
    sup = RIM - 238.4
    s.poly([P((0, shift_y - 150, sup + 24)), P((0, shift_y + 150, sup + 24)), P((0, shift_y + 150, sup + 36)), P((0, shift_y - 150, sup + 36))], color=WORK, fill=WORK, op=0.15)
    for fy in (-135, 115):
        s.poly([P((0, shift_y + fy, sup)), P((0, shift_y + fy + 20, sup)), P((0, shift_y + fy + 20, sup + 24)), P((0, shift_y + fy, sup + 24))], color=WORK, fill=WORK, op=0.15)
    s.poly([P((0, shift_y - 75, sup + 36)), P((0, shift_y + 75, sup + 36)), P((0, shift_y + 75, sup + 86)), P((0, shift_y - 75, sup + 86))], color=WORK, w=0.8, dash="3,2")
    s.text(P((0, shift_y + 80, sup + 60)), "rotator (turntable, nest; motor/ground towers not drawn)", WORK, 9)


def umbilical(s, P, pose, lift, length=420, to=None):
    gb = world(FEATURES['grip_base_QBH'], pose) + np.array([0, 0, lift])
    tip = world((FEATURES['grip_base_QBH'][0] + 100 * FIBER_DIR_LOCAL[1], FEATURES['grip_base_QBH'][1] + 100 * FIBER_DIR_LOCAL[2]), pose) + np.array([0, 0, lift])
    d = (tip - gb) / 100
    pts = [gb + t * d for t in np.linspace(0, 120, 8)]
    if to is not None:
        a = pts[-1]
        for t in np.linspace(0, 1, 16)[1:]:
            q = a * (1 - t) ** 2 + (a + 250 * d) * 2 * t * (1 - t) + to * t * t
            pts.append(q)
    s.poly([P(q) for q in pts], color=CABLE, w=3, closed=False)
    return gb


# ---------------------------------------------------------------- S2 still gun, moving work
def s2():
    global SCALE
    SCALE = 0.95
    W, H = 1380, 780
    s = Svg(W, H, "S2 - Still gun, moving work (side view from +X; opening pose, hole dial 30)")
    lift = 150.0  # compound table + drawer under the rotator (estimate)
    ox, oy = 640, 740
    P = side_proj(ox, oy, lift)
    pose = (45, 30, 0)
    shift_y = -16.0
    # bench
    s.line((20, oy), (980, oy), INK, 2)
    s.text((24, oy + 16), "bench top (VEVOR height can drop to keep the joint where it was)", NOTE, 10)
    # compound table + drawer
    sup = RIM - 238.4
    s.poly([P((0, -230, sup - lift)), P((0, 230, sup - lift)), P((0, 230, sup - lift + 110)), P((0, -230, sup - lift + 110))], color=MECH, fill=MECH, op=0.12)
    s.text(P((0, -225, sup - lift + 60)), "cross-slide table (X 210 / Y 110 mm travel): radial X and yaw-by-Y, set per tube", MECH, 10)
    s.poly([P((0, -200 + shift_y, sup - lift + 110)), P((0, 200 + shift_y, sup - lift + 110)), P((0, 200 + shift_y, sup - lift + 140)), P((0, -200 + shift_y, sup - lift + 140))], color=MECH, fill=MECH, op=0.25)
    s.text(P((0, -195, sup - lift + 126)), "drawer on rails with a hard stop (loading, out along X)", MECH, 10)
    s.text(P((0, 160, sup - lift + 145)), "3 fine screws: Z + small tilt", MECH, 10)
    draw_rotator_side(s, P, shift_y)
    draw_tube_side(s, P, shift_y)
    gun_2d(s, P, pose, op=0.35)
    dot = world(FEATURES['dot'], pose)
    s.circle(P(dot), 4, color="#d00", fill="#d00")
    s.text((P(dot)[0] + 8, P(dot)[1] + 4), "P: dot = fixed station point", "#d00", 10)
    # stand column and bracket to the shell near the body back / grip
    colY = -400
    bb = world(FEATURES['body_back'], pose)
    gb = world(FEATURES['grip_base_QBH'], pose)
    s.poly([P((0, colY - 20, BENCH - lift)), P((0, colY + 20, BENCH - lift)), P((0, colY + 20, BENCH + 560)), P((0, colY - 20, BENCH + 560))], color=MECH, fill=MECH, op=0.18)
    s.text(P((0, colY - 18, BENCH + 570)), "stand (bench-fixed), set back in x", MECH, 10)
    s.text(P((0, colY - 18, BENCH + 556)), "so the fiber leaving along -Y misses it", MECH, 10)
    att = (bb + gb) / 2
    s.line(P((0, colY + 20, att[2] + 40)), P(att), MECH, 7, op=0.6)
    s.poly([P(att + np.array([0, -18, -18])), P(att + np.array([0, 18, -18])), P(att + np.array([0, 18, 18])), P(att + np.array([0, -18, 18]))], color=MECH, fill="#ffd54f", op=0.9)
    s.text(P(att + np.array([0, 30, 30])), "printed recipe block (roll, hole tilt)", "#8d6e00", 10)
    s.text(P(att + np.array([0, 30, 16])), "between bracket and scan-fit shell", "#8d6e00", 10)
    # camera
    cam = np.array([0, 190, BENCH + 520])
    s.poly([P(cam + np.array([0, -15, -10])), P(cam + np.array([0, 15, -10])), P(cam + np.array([0, 15, 10])), P(cam + np.array([0, -15, 10]))], color=INK, fill="#999", op=0.8)
    s.line(P(cam), P(dot), NOTE, 0.8, dash="4,3")
    s.text(P(cam + np.array([0, -60, 24])), "camera on the stand: the dot never moves in its image", NOTE, 10)
    # umbilical + wire to overhead anchor
    anchor = np.array([0, -560, BENCH + 560])
    umbilical(s, P, pose, 0, to=anchor)
    s.text(P(anchor + np.array([0, -60, 20])), "umbilical + wire conduit: static route to the cart", CABLE, 10)
    # notes
    notes = ["Who moves what",
             " gun: nothing after setup",
             "   roll, hole tilt = recipe block, per session",
             " work: X radial (cross-slide)",
             "   Y = yaw, 1.08 mm per degree (S1)",
             "   Z + trim tilt (3 screws under base)",
             "   spin (existing rotator)",
             "   lift-off: a >=10 mm drop (the wire",
             "   tip sits in the corner below the rim)",
             "   loading: drop, out toward +X, back",
             " cables: never move -> constant force",
             "   -> constant, calibratable sag",
             "",
             "Heights: joint rises ~150 mm on the",
             "stages (estimate). Gun at grip 45 /",
             "hole dial 30; tube shifted -16 mm",
             "for relative yaw -15."]
    for i, l in enumerate(notes):
        s.text((1000, 60 + 17 * i), l, INK if i == 0 else NOTE, 11, bold=(i == 0))
    s.save("s2-still-gun-moving-work.svg")


# ---------------------------------------------------------------- S3 protractor and stub
def s3():
    global SCALE
    SCALE = 1.0
    W, H = 1180, 740
    s = Svg(W, H, "S3 - Protractor + stub (side view from +X, gun room-yaw 0, grip 45; hole dials 0 / 30 / 60)")
    ox, oy = 470, 720
    P = side_proj(ox, oy, 0)
    s.line((20, oy), (800, oy), INK, 2)
    draw_tube_side(s, P, 0, label=False)
    draw_rotator_side(s, P, 0)
    dot = world(FEATURES['dot'], (45, 0, 0))
    STUB = 345.0
    Rarc = STUB
    c2 = P(dot)
    s.arc(c2, Rarc * SCALE, 112, 185, color=MECH, w=9)
    s.arc(c2, Rarc * SCALE, 112, 185, color="#fcfcf8", w=5)
    s.text((c2[0] - 440, c2[1] + 40), "arc plate, R = dot-to-stub (~345 mm, estimate),", MECH, 10)
    s.text((c2[0] - 440, c2[1] + 54), "centred on P; its low end reaches dot height", MECH, 10)
    for h, op in ((0, 0.18), (30, 0.4), (60, 0.18)):
        pose = (45, h, 0)
        gun_2d(s, P, pose, op=op)
        gb = world(FEATURES['grip_base_QBH'], pose)
        g = (gb - dot) / np.linalg.norm(gb - dot)
        stub = dot + STUB * g
        s.line(P(dot), P(stub), NOTE, 0.8, dash="5,4")
        s.line(P(gb), P(stub), MECH, 5, op=0.8)
        s.circle(P(stub), 9, color=MECH, fill="#fff", w=2)
        s.text((P(stub)[0] + 12, P(stub)[1] - 4), f"dial {h}", MECH, 10)
    s.circle(P(dot), 4, color="#d00", fill="#d00")
    s.text((P(dot)[0] + 8, P(dot)[1] + 14), "P: dot = arc centre = on the stub axis", "#d00", 10)
    notes = ["What each joint does",
             " carriage along the arc:",
             "   hole-axis tilt (about the X line",
             "   through P)",
             " stub bearing, axis = grip axis",
             "   (dashed), pointing at P: roll",
             " neither moves the dot: both axes",
             "   pass through P by construction",
             " yaw: work slides along Y (S1), or",
             "   the whole arc rides a gantry Y",
             " X, Z: the work, or the arc's base",
             "",
             "Loads: gun weight to a balancer on",
             "the shell near its centre of mass;",
             "stub + arc only locate. Cable forces",
             "enter at the stub, next to the QBH.",
             "",
             "At room yaw 0 the QBH stays 279.2 mm",
             "from P in this plane for every hole",
             "tilt (pose.js), so the arc is exact.",
             "The QBH sits at (dial) degrees above",
             "the -Y horizontal: dial 30 -> 30 deg.",
             "Ghosts: dials 0 and 60."]
    for i, l in enumerate(notes):
        s.text((810, 60 + 17 * i), l, INK if i == 0 else NOTE, 11, bold=(i == 0))
    s.save("s3-protractor-and-stub.svg")


# ---------------------------------------------------------------- S4 rim rider radial section
def s4():
    global SCALE
    SCALE = 5.0
    W, H = 1120, 600
    s = Svg(W, H, "S4 - Rim rider, radial section at the station (schematic)")
    ox, oy = 180, 540

    def P(x, z):  # x radial (mm from tube axis), z above bench
        return (ox + SCALE * (x - 20), oy - SCALE * (z - 180))
    zdot = 232.05
    # plate and wall
    s.poly([P(20, zdot - 6.35), P(R_IN, zdot - 6.35), P(R_IN, zdot), P(20, zdot)], color=WORK, fill=WORK, op=0.25)
    s.poly([P(R_IN, 190), P(R_OUT, 190), P(R_OUT, 238.4), P(R_IN, 238.4)], color=WORK, fill=WORK, op=0.45)
    s.text(P(22, zdot - 3.5), "end plate 6.35 (recessed 6.35)", WORK, 11)
    s.text(P(R_OUT + 1, 200), "tube wall 1.65", WORK, 11)
    s.circle(P(R_IN, zdot), 5, color="#d00", fill="#d00")
    s.text(P(R_IN - 20, zdot + 2.5), "dot / corner", "#d00", 11)
    # skid on plate face (drawn projected; really ~20 deg upstream)
    sk = (47.0, zdot + 7.9)
    s.circle(P(*sk), 7.9 * SCALE, color=MECH, w=2)
    s.text(P(21, zdot - 10), "Z skid, one of a tripod:", MECH, 11)
    s.text(P(21, zdot - 12.5), "5/8 in ball transfer, r ~47 mm,", MECH, 10)
    s.text(P(21, zdot - 15), "inboard of tacks, outside ports,", MECH, 10)
    s.text(P(21, zdot - 17.5), "upstream on cold plate", MECH, 10)
    # OD roller
    rr = 8.0
    s.circle(P(R_OUT + rr, 218), rr * SCALE, color=MECH, w=2)
    s.text(P(R_OUT + 2 * rr + 2, 219), "X rollers (pair) on tube OD, below the plate", MECH, 11)
    s.text(P(R_OUT + 2 * rr + 2, 216.5), "(wall-thickness transfer; ~20 deg upstream)", MECH, 10)
    # carriage frame
    s.poly([P(47, zdot + 15.8), P(47, 250), P(R_OUT + rr, 250), P(R_OUT + rr, 226)], color=MECH, w=4, closed=False)
    s.text(P(40, 258), "carriage straddles the lip;", MECH, 11)
    s.text(P(40, 255.5), "carries shell + recipe block", MECH, 11)
    # float
    s.text(P(84, 250), "hangs free from a balancer; located only by its contacts:", MECH, 11)
    s.text(P(84, 247.5), "tripod on plate face (Z + 2 tilts), 2 OD rollers (X + yaw),", MECH, 11)
    s.text(P(84, 245), "soft tether (travel around the tube, the harmless freedom)", MECH, 11)
    s.text(P(84, 233), "preload: net weight (tripod), radial spring (rollers)", MECH, 11)
    # gun nozzle hint
    s.line(P(R_IN - 3, zdot + 13), P(R_IN - 8, zdot + 27), GUN, 11 * 5 / 5, op=0.35, cap="round")
    s.text(P(R_IN - 7, zdot + 29), "nozzle (proxy, at P)", GUN, 11)
    notes = ["Runout reaching the dot through each contact (from geometry.py):",
             " one contact 20 deg upstream: 0.35 x eccentricity + 0.68 x ovality",
             " a pair straddling +/-20 deg, averaged: 0.06 x eccentricity + 0.23 x ovality",
             " (the downstream contact then rides freshly welded plate, hot)"]
    for i, l in enumerate(notes):
        s.text((330, 500 + 16 * i), l, INK if i == 0 else NOTE, 11, bold=(i == 0))
    s.save("s4-rim-rider-section.svg")


# ---------------------------------------------------------------- S5 carrier and seat
def s5():
    global SCALE
    SCALE = 0.95
    W, H = 1180, 760
    s = Svg(W, H, "S5 - Carrier + seat (side view from +X; opening pose, hole dial 30)")
    ox, oy = 560, 740
    P = side_proj(ox, oy, 0)
    s.line((20, oy), (800, oy), INK, 2)
    draw_rotator_side(s, P, 0)
    draw_tube_side(s, P, 0)
    pose = (45, 30, 0)
    gun_2d(s, P, pose, op=0.35)
    dot = world(FEATURES['dot'], pose)
    s.circle(P(dot), 4, color="#d00", fill="#d00")
    # seat post on rotator base at -Y side
    sup = RIM - 238.4
    postY = -140
    top = BENCH + 290
    s.poly([P((0, postY - 12, sup + 36)), P((0, postY + 12, sup + 36)), P((0, postY + 12, top)), P((0, postY - 12, top))], color=MECH, fill=MECH, op=0.25)
    s.text(P((0, postY - 170, sup + 120)), "seat post on the rotator base", MECH, 10)
    s.text(P((0, postY - 170, sup + 106)), "(same datum as the nest)", MECH, 10)
    bb = world(FEATURES['body_back'], pose)
    lf = world(FEATURES['light_switch'], pose)
    seat = np.array([0, postY + 20, top + 10])
    s.poly([P(seat + np.array([0, -40, -8])), P(seat + np.array([0, 40, -8])), P(seat + np.array([0, 40, 4])), P(seat + np.array([0, -40, 4]))], color=MECH, fill="#ffd54f", op=0.9)
    for dy in (-30, 0, 30):
        s.circle(P(seat + np.array([0, dy, 8])), 5, color=INK, fill="#bbb")
    s.line(P(seat + np.array([0, 0, 12])), P(lf), MECH, 5, op=0.6)
    s.text(P(seat + np.array([0, -330, -30])), "3 balls on the shell / 3 V's on the seat,", "#8d6e00", 10)
    s.text(P(seat + np.array([0, -330, -44])), "magnet or toggle preload; recipe block below", "#8d6e00", 10)
    # carriers: two balancers on rings on the grip axis (Derek's suspension read as a hinge)
    gb = world(FEATURES['grip_base_QBH'], pose)
    g = (gb - dot) / np.linalg.norm(gb - dot)
    ringA = dot + 100 * g
    ringB = dot + 330 * g
    for r, lab in ((ringA, "ring A (front)"), (ringB, "ring B (behind butt)")):
        s.circle(P(r), 13, color=MECH, w=2.5)
        hook = np.array([0, r[1], BENCH + 700])
        s.line(P(r + np.array([0, 0, 13])), P(hook), NOTE, 1, dash="5,3")
        s.poly([P(hook + np.array([0, -14, 0])), P(hook + np.array([0, 14, 0])), P(hook + np.array([0, 14, 30])), P(hook + np.array([0, -14, 30]))], color=INK, fill="#ddd")
        s.text(P(hook + np.array([0, 18, 12])), "balancer", NOTE, 10)
        s.text((P(r)[0] + 16, P(r)[1] + 4), lab, MECH, 10)
    s.line(P(dot), P(ringB), NOTE, 0.8, dash="5,4")
    s.text(P(dot + 180 * g + np.array([0, 25, 0])), "grip axis", NOTE, 10)
    umbilical(s, P, pose, 0, to=np.array([0, -520, BENCH + 640]))
    notes = ["Who moves what",
             " weight: carrier (monitor-arm gas",
             "   spring, or two balancers)",
             " gross motion, lift-off, swing-away",
             "   for loading: carrier, by hand",
             " location during the weld: the seat",
             "   (kinematic, preloaded)",
             " recipe angles: printed block or",
             "   adjusters under the seat",
             " spin: rotator; yaw: seat along Y",
             "",
             "Drawn: branch D2 - Derek's two rings,",
             "centred on the grip axis, hang from",
             "balancers; roll is then a hinge while",
             "hanging; lock one ring to hold it.",
             "Seat post and rings are schematic."]
    for i, l in enumerate(notes):
        s.text((810, 60 + 17 * i), l, INK if i == 0 else NOTE, 11, bold=(i == 0))
    s.save("s5-carrier-and-seat.svg")


if __name__ == "__main__":
    s1(); s2(); s3(); s4(); s5()
    print("wrote", sorted(os.listdir(OUT)))
