"""Generate the borrowed-ecosystems sketches (SVG) from the scene's gun proxy.

python3 make_sketches.py  -> writes *.svg beside this file.
Gun, wire and cable come from geometry.py at the scene's opening pose
(grip 45, hole dial 30, vertical -15; the hole dial offset of 35 deg is applied
in geometry.pose_point); every support element is schematic.
"""
import os
import numpy as np
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = (45, 30, -15)
CG = to_bench(G.pose_point(G.CG_LOCAL, *POSE))
GB = to_bench(G.pose_point(G.GRIP_BASE, *POSE))
GAX = (GB - DOT) / np.linalg.norm(GB - DOT)
DZ = DOT[2]


def base_xz(s, bench_u=(-380, 420), rotator=True, bench_z=0):
    s.line2((bench_u[0], bench_z), (bench_u[1], bench_z), stroke="#6b4f2a", w=3)
    if rotator:
        draw_rotator_xz(s)
    draw_tube_xz(s)


def label_dot(s, u, v, text="dot (inside corner)", du=12, dv=-18):
    s.line2((u, v), (u + du, v + dv), stroke="#d62828", w=0.8)
    s.text2(u + du + 2, v + dv - 2, text, size=10, color="#d62828")


# =============================================================================
# A0 -- the original: a gas-spring monitor arm holds the gun shell directly
# =============================================================================
def a0():
    s = Svg(760, 720, 'xz', 0.95, (400, 690), "Section along the tangent (x radial, z up)")
    base_xz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=180)
    label_dot(s, DOT[0], DOT[2])
    # arm projected: clamp post at bench back edge (x=-300 in projection), shoulder, elbow, head
    clamp = (-300, 0); post_top = (-300, 120); elbow = (-260, 380); head = (-110, 470)
    s.rect2(-315, -30, -285, 0, stroke="#333", fill="#555")
    s.line2(clamp, post_top, stroke="#333", w=6)
    s.line2(post_top, elbow, stroke="#555", w=7)
    s.line2(elbow, head, stroke="#555", w=7)
    for (u, v), t in ((post_top, "J1 swivel (friction)"), (elbow, "J2/J3 gas-spring lift + swivel"), (head, "J4 tilt/swivel/rotate (friction)")):
        s.circle2((u, v), 7, stroke="#111", fill="#fff", w=1.5)
        s.text2(u - 70 if u < -200 else u + 10, v + 12, t, size=10)
    # VESA plate -> printed adapter -> shell lug near CG
    s.line2(head, (CG[0] - 10, CG[2] + 40), stroke="#2a6f97", w=4)
    s.text2(-100, 500, "VESA plate -> printed adapter -> shell", size=10, color="#2a6f97")
    s.text2(-360, 650, "Gas spring ~ constant force: vertical rate ~0, held by friction band", size=11, color="#b5451b")
    s.text2(-360, 632, "Swivels: fingertip force moves them; lock screws only add friction", size=11, color="#b5451b")
    s.text2(-360, 614, "Result: 'floats' in all 6 DOF -- a carrier, not a locator", size=11, color="#b5451b", weight="bold")

    p = Svg(560, 720, 'xy', 0.95, (300, 300), "Plan (x radial, y tangent)")
    draw_tube_xy(p)
    p.rect2(-150, -125, 150, 125, stroke="#999", dash="4,3")
    p.text2(-148, -140, "rotator base 300 x 250 (placement schematic)", size=10, color="#777")
    draw_gun(p, POSE, shell=True)
    cp = draw_cable(p, POSE, tail=0)
    clampP = (-200, -380); elbowP = (-300, -250); headP = (-110, -170)
    p.rect2(-230, -395, -170, -365, stroke="#333", fill="#555")
    p.line2(clampP, elbowP, stroke="#555", w=7)
    p.line2(elbowP, headP, stroke="#555", w=7)
    p.line2(headP, (CG[0], CG[1]), stroke="#2a6f97", w=4)
    for q in (clampP, elbowP, headP):
        p.circle2(q, 7, stroke="#111", fill="#fff", w=1.5)
    p.text2(-285, -410, "bench-edge clamp", size=10)
    # free motions
    p.raw('')
    p.text2(40, -300, "umbilical leaves toward -Y at ~30 deg,", size=10, color="#555")
    p.text2(40, -315, "apex ~450 mm above the bench", size=10, color="#555")
    for ang in (0.6, 2.2):
        pass
    p.text2(-280, 330, "Every swivel axis is vertical: a sideways push", size=11, color="#b5451b")
    p.text2(-280, 314, "(umbilical, wire conduit, hand) swings the head", size=11, color="#b5451b")
    p.text2(-280, 298, "about J1/J3 until joint friction balances it.", size=11, color="#b5451b")
    compose([(s, 10, 40), (p, 780, 40)], os.path.join(HERE, "a0-arm-holds-the-gun.svg"),
            title="A0  Original: gas-spring monitor arm holding the fitted shell (kept as proposed)",
            notes=["Gun, wire (brown), beam (red dashes) and umbilical at the scene's opening pose (grip 45, hole 30, vertical -15). Gun proxy 253 x 143 x 34 mm from the manual; arm geometry schematic.",
                   "Use it for: weight relief and parking while Derek still aims by hand (zero-gravity tool-arm role). As a locator it drifts: see ideas/a-monitor-arm-roles.md."])


# =============================================================================
# A1 -- the arm carries, the tube locates (rider below the rim, revised wave 2)
# =============================================================================
def a1():
    s = Svg(760, 700, 'xz', 1.0, (400, 660), "Section at y = 0 (x radial, z up); rider stations rotated into view")
    base_xz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=150)
    label_dot(s, DOT[0], DOT[2], du=-150, dv=-40)
    R = RIM_Z
    # OD straddle wheel (axle vertical), 25 mm below the dot
    s.rect2(63.5, DZ - 27, 76.5, DZ - 23, stroke="#111", fill="#444")
    s.text2(84, DZ - 22, "OD wheels at -30 and +30 deg, 25 mm below the dot (radial)", size=10)
    s.rect2(63.5, DZ - 62, 76.5, DZ - 58, stroke="#111", fill="#444")
    s.text2(84, DZ - 58, "roll wheel on the OD at 0 deg, 60 mm below the dot", size=10)
    # rim height wheel (rotated into view), axle radial
    s.rect2(60.5, R, 64.9, R + 13, stroke="#111", fill="#777")
    s.text2(84, R + 8, "height: V-wheels on the rim at -60 and +60 deg", size=10)
    # rider yoke outboard, below the rim, with arm over the rim for the height wheel
    s.poly2([(78, DZ - 70), (100, DZ - 70), (100, R + 24), (58, R + 24), (58, R + 14), (80, R + 14), (80, DZ - 70)],
            stroke="#2a6f97", fill="#2a6f97", op=0.25, w=1.6)
    s.text2(106, DZ - 90, "rider yoke (printed, metal axle posts)", size=10, color="#2a6f97")
    # bracket rider -> fine XYZ -> shell at the drawer/housing front
    s.line2((95, R + 24), (95, 300), stroke="#2a6f97", w=5)
    s.rect2(78, 300, 112, 324, stroke="#2a6f97", fill="#fff", w=1.5)
    s.text2(116, 312, "fine XYZ (set by dot, locked)", size=10, color="#2a6f97")
    s.line2((80, 318), (20, 330), stroke="#2a6f97", w=5)
    s.text2(116, 298, "bracket rises at theta = -75 deg, outside the wire", size=10, color="#2a6f97")
    # hook at CG
    top = (CG[0], 610)
    s.spring2(top, (CG[0], CG[2] + 55), n=10, amp=6)
    s.line2((CG[0], CG[2] + 55), (CG[0], CG[2] + 8), stroke="#b5451b", w=1.5)
    s.rect2(CG[0] - 25, 610, CG[0] + 25, 622, stroke="#333", fill="#777")
    s.text2(CG[0] + 30, 622, "monitor-arm head or balancer (coarse height)", size=10)
    s.text2(CG[0] + 12, 560, "soft spring 0.3-0.5 N/mm on a line", size=10, color="#b5451b")
    s.text2(CG[0] + 12, 547, "through the CG: carries, cannot locate", size=10, color="#b5451b")
    s.circle2((CG[0], CG[2]), 4, stroke="#111", fill="#ffd166")
    s.text2(CG[0] - 80, CG[2] + 4, "CG proxy", size=10)
    s.text2(-390, -22, "Precision loop: dot - nozzle - shell - screws - rider - wheels - tube. Bench, arm and table are outside it.", size=11, weight="bold")

    p = Svg(640, 700, 'xy', 1.25, (360, 260), "Plan: wheels below the rim straddle the dot; height wheels at +/-60 deg")
    draw_tube_xy(p)
    draw_gun(p, POSE, shell=True)
    draw_cable(p, POSE, tail=0)
    ang = np.radians(np.linspace(150, 110, 12))
    p.poly2([(95 * np.cos(a), 95 * np.sin(a)) for a in ang], stroke="#333", w=1.4, closed=False)
    p.line2((95 * np.cos(ang[-2]), 95 * np.sin(ang[-2])), (95 * np.cos(ang[-1]), 95 * np.sin(ang[-1])), stroke="#333", w=1.4, arrow=True)
    p.text2(-120, 104, "tube turns CCW; -Y is the arriving side", size=10)
    for th in (-30, 30):
        t = np.radians(th)
        p.circle2((70 * np.cos(t), 70 * np.sin(t)), 6.5, stroke="#111", fill="#444")
    p.text2(80, 40, "OD wheel +30 (departing, 25 mm below the weld)", size=10)
    p.text2(80, -44, "OD wheel -30", size=10)
    p.circle2((70, 0), 6.5, stroke="#111", fill="#888")
    for th in (-60, 60):
        t = np.radians(th)
        c = np.array((62.7 * np.cos(t), 62.7 * np.sin(t)))
        tang = np.array([-np.sin(t), np.cos(t)])
        p.line2(tuple(c - tang * 6.5), tuple(c + tang * 6.5), stroke="#777", w=5)
    p.text2(36, 70, "rim V-wheel +60", size=10)
    p.text2(40, -66, "rim V-wheel -60", size=10)
    arc = [(r * np.cos(np.radians(q)), r * np.sin(np.radians(q))) for r in (66,) for q in np.linspace(-66, 66, 20)]
    arc2 = [(r * np.cos(np.radians(q)), r * np.sin(np.radians(q))) for r in (100,) for q in np.linspace(66, -66, 20)]
    p.poly2(arc + arc2, stroke="#2a6f97", fill="#2a6f97", op=0.15, w=1.5)
    # bracket at -75 deg up to the shell
    t = np.radians(-75)
    p.circle2((95 * np.cos(t), 95 * np.sin(t)), 5, stroke="#2a6f97", fill="#2a6f97")
    p.line2((95 * np.cos(t), 95 * np.sin(t)), (5, -66), stroke="#2a6f97", w=4)
    # tether
    post = (170, 170)
    p.line2((95, 40), post, stroke="#b5451b", w=1.5, dash="5,3")
    p.rect2(post[0] - 8, post[1] - 8, post[0] + 8, post[1] + 8, stroke="#333", fill="#777")
    p.text2(post[0] - 10, post[1] + 14, "tether + magnetic breakaway (NC switch in pedal line)", size=10, color="#b5451b", anchor="end")
    # arm to the CG hook
    p.line2((-230, -330), (-250, -150), stroke="#555", w=6)
    p.line2((-250, -150), (CG[0], CG[1]), stroke="#555", w=6)
    p.circle2((CG[0], CG[1]), 5, stroke="#111", fill="#ffd166")
    p.text2(-270, -345, "arm clamp (or balancers overhead)", size=10)
    p.text2(-270, 150, "Wire (brown) crosses the arriving-side rim between", size=10, color="#8a5a00")
    p.text2(-270, 138, "-15 and -30 deg, only 4 mm from where a rim wheel", size=10, color="#8a5a00")
    p.text2(-270, 126, "at -30 would sit: the wave-1 rim stations moved.", size=10, color="#8a5a00")
    compose([(s, 10, 40), (p, 780, 40)], os.path.join(HERE, "a1-arm-carries-tube-locates.svg"),
            title="A1 (revised)  The arm carries, the tube locates: rider straddles the dot below the rim; weight hung at the CG",
            notes=["Radial: OD wheels at +/-30 deg, 25 mm below the dot (worst 0.017 mm at 0.25 TIR; ovality leaks 0.5x). Height: rim V-wheels at +/-60 deg (0.075 mm at 0.30 TIR) or left to the carrier.",
                   "Wave-1 version (rim V-wheels ahead at -30/-60) collides with the wire at the corrected pose and extrapolates ovality 1.8x; kept in the idea file as the original."])


# =============================================================================
# B -- nodal head: rotations about axes through the dot, work moves in X/Y
# =============================================================================
def b():
    OFF = 110
    s = Svg(820, 700, 'xz', 1.0, (420, 580), "Section at y = 0 (x radial, z up); z from the cross-slide top")
    s.line2((-400, -OFF), (420, -OFF), stroke="#6b4f2a", w=3)
    s.rect2(-240, -OFF, 240, 0, stroke="#555", fill="#c9c9c9", w=1.2)
    s.text2(-235, -OFF + 40, "cast-iron compound cross-slide (X radial 210 mm, Y 110 mm travel)", size=10)
    s.text2(-235, -OFF + 26, "carries the rotator: the corner is moved to the fixed pivot", size=10)
    draw_rotator_xz(s)
    draw_tube_xz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=120)
    s.line2((-120, DZ), (300, DZ), stroke="#1b7f3b", w=1.2, dash="10,3,2,3")
    s.text2(-118, DZ - 14, "hole axis (radial, through dot)", size=10, color="#1b7f3b")
    s.line(DOT, DOT + GAX * 360, stroke="#7b2cbf", w=1.2, dash="10,3,2,3")
    s.rect2(300, -OFF, 330, 560, stroke="#333", fill="#8d99ae")
    s.text2(250, 575, "column", size=10)
    s.rect2(270, 180, 300, 300, stroke="#333", fill="#adb5bd")
    s.text2(336, 250, "Z carriage", size=10)
    s.rect2(135, 210, 270, 277, stroke="#333", fill="#dee2e6")
    s.rect2(95, DZ - 36, 135, DZ + 36, stroke="#111", fill="#6c757d")
    s.text2(140, DZ - 50, "rotator on the hole axis (dial in degrees)", size=10)
    # hole arm plate seen edge-on at x ~ 88-94, rising to ~400, then bracket inboard at the grip end
    s.rect2(86, DZ - 10, 94, 400, stroke="#1b7f3b", fill="#1b7f3b", op=0.7)
    s.line2((90, 395), (-5, 385), stroke="#1b7f3b", w=6)
    s.text2(100, 420, "hole arm: plate 30 mm outside the OD, runs back along -Y", size=10, color="#1b7f3b")
    s.text2(100, 406, "at the grip axis' 30 deg, then steps inboard to the roll", size=10, color="#1b7f3b")
    c = DOT + GAX * 305
    ang = np.radians(np.linspace(-60, 200, 30))
    s.poly2([(c[0] + 45 * np.cos(a), c[2] + 25 * np.sin(a)) for a in ang], stroke="#7b2cbf", w=4, closed=False)
    s.text2(-380, 470, "grip-roll element on the grip axis behind the butt", size=10, color="#7b2cbf")
    s.text2(-380, 456, "(open arc / clamp / wedges: branches B0-B3)", size=10, color="#7b2cbf")
    label_dot(s, DOT[0], DOT[2], du=-150, dv=-50)

    p = Svg(640, 700, 'xy', 0.9, (330, 360), "Plan")
    p.rect2(-240, -85, 240, 85, stroke="#555", fill="#c9c9c9", w=1.2, op=0.6)
    p.rect2(-150, -125, 150, 125, stroke="#999", dash="4,3")
    draw_tube_xy(p)
    draw_gun(p, POSE, shell=True)
    draw_cable(p, POSE, tail=0)
    p.line2((-40, 0), (300, 0), stroke="#1b7f3b", w=1.2, dash="10,3,2,3")
    p.rect2(95, -35, 135, 35, stroke="#111", fill="#6c757d")
    p.rect2(135, -20, 300, 20, stroke="#333", fill="#dee2e6")
    p.rect2(300, -15, 330, 15, stroke="#333", fill="#8d99ae")
    p.poly2([(90, 0), (90, -262), (-5, -262)], stroke="#1b7f3b", w=6, closed=False)
    p.text2(100, -200, "hole arm", size=10, color="#1b7f3b")
    R = 253
    ang = np.radians(np.linspace(-35, 35, 30))
    p.poly2([(DOT[0] + R * np.cos(a), R * np.sin(a)) for a in ang], stroke="#333", w=8, closed=False)
    p.text2(130, 190, "column foot on an arc about the dot's vertical", size=10)
    p.text2(-300, 330, "gun and cables stay still while X/Y move the tube", size=10)
    compose([(s, 10, 40), (p, 840, 40)], os.path.join(HERE, "b-nodal-head.svg"),
            title="B  Nodal head: camera/machinist rotators arranged so both rolls pivot on the dot; the work moves in X/Y",
            notes=["Both rolls turn about lines through the dot, so changing either angle leaves the dot in place; X/Y at the work and Z at the column put the dot on the corner.",
                   "Gravity torque about the hole axis at the opening pose: 1.35-2.7 N*m for 1-2 kg gun + shell (corrected wave 2); the rotator must hold it or be counterweighted."])


# =============================================================================
# C -- engraver gantry on legs over the rotator
# =============================================================================
def c():
    s = Svg(900, 640, 'yz', 0.85, (560, 600), "Elevation from outside the dot (y tangent right, z up)")
    s.line2((-640, 0), (400, 0), stroke="#6b4f2a", w=3)
    s.rect2(-125, 0, 125, 86, stroke="#777", fill="#efe9d8", dash="4,3")
    draw_tube_yz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=300)
    ZR = 500
    for yl in (-400, 300):
        s.rect2(yl - 10, 0, yl + 10, ZR, stroke="#333", fill="#adb5bd")
    s.rect2(-410, ZR, 310, ZR + 20, stroke="#333", fill="#8d99ae")
    s.text2(-400, ZR + 32, "engraver frame raised on 2040 legs (Y rails at x = +/-330)", size=10)
    yb = -135
    s.rect2(yb - 20, ZR + 20, yb + 20, ZR + 60, stroke="#333", fill="#6c757d")
    s.text2(yb + 26, ZR + 52, "X beam (end-on) + carriage", size=10)
    s.rect2(yb - 18, 440, yb + 18, ZR + 20, stroke="#333", fill="#dee2e6")
    s.text2(yb + 24, 460, "Z module holds the shell by the housing top", size=10)
    s.rect2(160, 400, 190, 420, stroke="#333", fill="#222")
    s.line2((160, 410), (5, DZ + 5), stroke="#999", w=1, dash="4,4")
    s.text2(110, 385, "USB camera on the frame watches the dot", size=10)
    s.text2(-630, 250, "umbilical passes under the rear rail", size=10)
    s.text2(-630, 236, "(apex ~450 mm), saddle on a rear leg", size=10)

    p = Svg(600, 700, 'xy', 0.75, (300, 330), "Plan")
    p.rect2(-340, -400, 340, 300, stroke="#333", w=1.5)
    for sx in (-1, 1):
        p.rect2(sx * 330 - 10, -400, sx * 330 + 10, 300, stroke="#333", fill="#8d99ae")
        for sy in (-400, 300):
            p.rect2(sx * 330 - 12, sy - 12, sx * 330 + 12, sy + 12, stroke="#111", fill="#495057")
    p.rect2(-340, -155, 340, -115, stroke="#333", fill="#6c757d", op=0.8)
    p.text2(-335, -100, "X beam (moves in Y)", size=10)
    p.rect2(-150, -125, 150, 125, stroke="#999", dash="4,3")
    draw_tube_xy(p)
    draw_gun(p, POSE, shell=True)
    draw_cable(p, POSE, tail=0)
    p.rect2(-85, -155, -45, -115, stroke="#111", fill="none", w=2)
    compose([(s, 10, 40), (p, 920, 40)], os.path.join(HERE, "c-engraver-gantry.svg"),
            title="C  Engraver gantry: a diode-laser engraver's XY frame on legs, carrying the gun shell on a Z module",
            notes=["Angles live in the printed shell (fixed cassette) or in two small roll stages under the Z module; the gantry supplies X/Y/Z for dry-run search and repeat.",
                   "Branch C-T (Derek's table hole): the same frame flat on the tabletop over a hole, rotator on a shelf below, rim near countertop height."])


# =============================================================================
# A2 -- the arm carries into a kinematic dock (toolchanger)
# =============================================================================
def a2():
    s = Svg(900, 560, 'xz', 1.0, (470, 520), "Section at y = 0: the shell docks on a bench-fixed kinematic receiver")
    base_xz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=100)
    label_dot(s, DOT[0], DOT[2], du=20, dv=-40)
    s.rect2(-300, 0, -270, 440, stroke="#333", fill="#8d99ae")
    s.text2(-420, 450, "bench post (or the B head)", size=10)
    s.rect2(-270, 380, -170, 405, stroke="#333", fill="#dee2e6")
    s.text2(-270, 364, "fine XYZ stage", size=10)
    s.rect2(-180, 405, -100, 420, stroke="#111", fill="#495057")
    for u in (-170, -140, -110):
        s.circle2((u, 426), 6, stroke="#111", fill="#e9ecef")
    s.rect2(-180, 432, -100, 444, stroke="#2a6f97", fill="#2a6f97", op=0.4)
    s.line2((-100, 438), (-55, 410), stroke="#2a6f97", w=5)
    s.text2(-290, 470, "3 balls in 3 V-grooves + magnet/latch (3D-printer toolchanger dock)", size=10)
    s.spring2((CG[0], 540), (CG[0], CG[2] + 40), n=8, amp=6)
    s.text2(CG[0] + 12, 530, "arm / balancer floats the weight and parks the gun", size=10)
    compose([(s, 10, 40)], os.path.join(HERE, "a2-arm-into-dock.svg"),
            title="A2  The arm carries, a dock locates: toolchanger-style kinematic coupling on a bench reference",
            notes=["The dock repeats the shell's pose each time it is set down; the arm only moves weight. Take it off to tack or hand-weld, put it back to the same pose."])


if __name__ == "__main__":
    a0(); a1(); a2(); b(); c()
    print("written:", [f for f in os.listdir(HERE) if f.endswith('.svg')])
