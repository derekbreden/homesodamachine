"""Wave 2 sketches: the paddle compass (work-as-datum's compass with one foot on
the room plane) and the axis-column clearance at the true opening pose.

Scene proxy gun at grip 45 / hole dial 30 / vertical -15 (parameter -5).
Plan origin at the tube axis; Z = 0 at the plate's outer face (the dot).
"""
import math
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import geom  # noqa: E402
from make_sketches import Svg, View, hull, GUN_PARTS, draw_gun, title  # noqa: E402

R_IN, R_OD = geom.R_IN, geom.TUBE_OD / 2
RECESS = 6.35


def gun_plate_frame(pose=(45, 30, -15)):
    roll, dial, vert = pose
    hp = dial - geom.HOLE_OFFSET
    parts = {}
    for k, pts in GUN_PARTS.items():
        parts[k] = [geom.pose_point(p, roll, hp, vert) - np.array([0, 0, geom.CAP_TOP]) for p in pts]
    gb = geom.pose_point(geom.GRIP_BASE, roll, hp, vert) - np.array([0, 0, geom.CAP_TOP])
    return parts, gb


def paddle():
    s = Svg(1200, 900)
    title(s, "Paddle compass: two rollers on the plate, one foot on the room plane",
          "work-as-datum's endcap compass with its support triangle stretched onto the counter. True scene opening pose (hole dial 30). mm, to scale.")
    parts, gb = gun_plate_frame()
    red, blue, green, purple = "#d00000", "#1f4e9c", "#1b5e20", "#8a2be2"
    P1, P2, P3 = (36, 0), (-40, 0), (-70, -250)
    # ---------------- plan: u = -Y (gun side to the right), v = +X (dot up)
    k = 1.25
    v = View(s, (120 + 90 * k, 110 + 110 * k), k)
    def P(x, y):
        return v.p(-y, x)
    s.text((60, 80), "PLAN", size=12, weight="bold")
    # counter plane with opening
    s.poly([P(x, y) for x, y in [(-150, 110), (110, 110), (110, -330), (-150, -330)]], fill="#efe7da", stroke="#9b8563")
    s.circle(P(0, 0), 80 * k, fill="#ffffff", stroke="#9b8563")
    s.text(P(-140, 100), "room plane at rim height (collar plate / counter / rotator deck)", size=10, color="#6b5a3a")
    s.circle(P(0, 0), R_OD * k, stroke="#333", width=1.5)
    s.circle(P(0, 0), R_IN * k, stroke="#333", width=0.8, dash="3,2")
    # ports + nipples + seat bar (turns with plate)
    for px in (-19.05, 19.05):
        s.circle(P(px, 0), 5.56 * k, stroke="#555")
        s.poly([P(px + 8.2 * math.cos(math.radians(a)), 8.2 * math.sin(math.radians(a))) for a in range(0, 360, 60)], stroke="#555")
    s.poly([P(x, y) for x, y in [(-30, 7), (30, 7), (30, -7), (-30, -7)]], stroke="#555", dash="4,2")
    s.text(P(-8, 175), "seat bar on two 316 nipples (turns with the plate)", size=9, color="#555")
    # paddle outline (stationary)
    outline = [(18, 12), (44, 8), (44, -8), (18, -10), (-8, -22), (-40, -58), (-52, -150), (-58, -262),
               (-84, -262), (-84, -238), (-78, -150), (-68, -60), (-50, -8), (-50, 8), (-20, 16)]
    s.poly([P(x, y) for x, y in outline], fill="#c9d7f0", stroke=blue, width=1.4, opacity=0.8)
    s.text(P(-95, -150), "paddle (printed/aluminium), stationary in the room", size=10, color=blue)
    s.circle(P(0, 0), 7 * k, fill="#ffffff", stroke=blue, width=1.4)
    s.text(P(8, 175), "hub: spherical bearing on the centre pin (stationary)", size=9, color=blue)
    for (x, y), name in ((P1, "P1"), (P2, "P2")):
        s.rect(*P(x + 6.5, y + 2.5), 5 * k, 13 * k, fill=red, stroke=red)
        s.text(P(x - 4, y + 22), name, size=11, color=red, weight="bold")
    s.line(P(-60, 0), P(75, 0), stroke=red, width=1, dash="6,3")
    s.text(P(74, 175), "P1-P2 line = the dot's radius (red dashes)", size=9, color=red)
    s.circle(P(P3[0], P3[1]), 6, fill=purple, stroke=purple)
    s.text(P(P3[0] - 14, P3[1] + 6), "P3 ball foot on room plane", size=10, color=purple)
    s.line(P(-100, -205), P(-100, -300), stroke=purple, width=5)
    s.text(P(-110, -262), "fence (azimuth)", size=9, color=purple)
    draw_gun(v, parts, lambda q: (-q[1], q[0]))
    s.circle(P(R_IN, 0), 3.5, fill=red, stroke=red)
    s.text(P(R_IN + 8, 6), "dot", size=10, color=red)
    s.circle(P(gb[0], gb[1]), 3.5, fill=green, stroke=green)
    s.rect(*P(-20, -305), 16, 16, fill=green)
    s.text(P(-5, -300), "cable anchor on the room plane", size=9, color=green)
    s.line(P(gb[0], gb[1]), P(-12, -300), stroke=green, width=3)

    # ---------------- elevation: looking toward +X; u = -Y, v = Z (plate face = 0)
    e = View(s, (720 + 60 * 0.95, 560), 0.95)
    def E(y, z):
        return e.p(-y, z)
    s.text((660, 80), "ELEVATION (looking toward +X)", size=12, weight="bold")
    # tube section
    s.poly([E(y, z) for y, z in [(R_OD, RECESS), (-R_OD, RECESS), (-R_OD, -140), (R_OD, -140)]], stroke="#333", width=1.4)
    s.poly([E(y, z) for y, z in [(R_IN, 0), (-R_IN, 0), (-R_IN, -6.35), (R_IN, -6.35)]], fill="#bbb", stroke="#333")
    # room plane at rim height beyond the opening
    s.poly([E(y, z) for y, z in [(-80, RECESS), (-330, RECESS), (-330, RECESS - 14), (-80, RECESS - 14)]], fill="#efe7da", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(80, RECESS), (140, RECESS), (140, RECESS - 14), (80, RECESS - 14)]], fill="#efe7da", stroke="#9b8563")
    # seat bar / nipples / pin
    s.poly([E(y, z) for y, z in [(8, 0), (-8, 0), (-8, 16), (8, 16)]], stroke="#555")
    s.poly([E(y, z) for y, z in [(3, 16), (-3, 16), (-3, 52), (3, 52)]], fill="#999", stroke="#333")
    # hub + spring
    s.poly([E(y, z) for y, z in [(9, 26), (-9, 26), (-9, 38), (9, 38)]], fill="#c9d7f0", stroke=blue)
    for i in range(5):
        s.line(E(-6, 39 + 2.4 * i), E(6, 40.2 + 2.4 * i), stroke="#333", width=1)
    s.text(E(-12, 58), "hold-down spring + thrust washer: clamps paddle to plate,", size=9, color="#333")
    s.text(E(-12, 50), "no net force on the tube", size=9, color="#333")
    # paddle arm from hub to P3, rising over the rim
    arm = [(-8, 26), (-58, 26), (-70, 22), (-240, 22), (-262, 22), (-262, 14), (-240, 14), (-70, 14), (-58, 18), (-8, 18)]
    s.poly([E(y, z) for y, z in arm], fill="#c9d7f0", stroke=blue, width=1.4)
    # rollers P1 (hidden behind hub along X, shown as circle at y=0) P2 same y; draw at y=0 offset for clarity
    s.circle(E(0, 6.5), 6.5 * 0.95, fill=red, stroke=red)
    s.text(E(14, 2), "P1, P2 rollers on the plate face (both on y = 0)", size=9, color=red, anchor="end")
    s.circle(E(-250, RECESS + 6), 6, fill=purple, stroke=purple)
    s.text(E(-250, RECESS - 26), "P3 on the room plane", size=9, color=purple, anchor="middle")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(0, 0), 3.5, fill=red, stroke=red)
    # shell legs from arm to gun
    for y, ztop in ((-90, 95), (-200, 120)):
        s.line(E(y, 26), E(y, ztop), stroke=blue, width=4)
    s.text(E(-150, 180), "gun in its shell / pose block on the paddle", size=9, color=blue, anchor="middle")
    s.circle(E(gb[1], gb[2]), 3.5, fill=green, stroke=green)
    s.line(E(gb[1], gb[2]), E(-300, 60), stroke=green, width=3)
    s.rect(*E(-296, 64), 14, 14, fill=green)

    notes = [
        "Contacts (6):  centre pin -> x, y of the hub   (work: plate centre)",
        "               P1, P2 rollers -> z at two points on the dot's radius   (work: plate face)",
        "               P3 foot -> z far out under the grip   (room plane)",
        "               fence at P3 -> azimuth   (room; the freedom that doesn't matter)",
        "The dot lies on the P1-P2 line, so the one rotation the room sets (about that line) does not move it.",
        "Dot height = 1.34 x P1 - 0.34 x P2.  Tube length now turns the gun 0.23 deg per mm about the dot's",
        "radius instead of moving the dot ~1 mm per mm; a per-tube shelf trim removes even that.",
        "Weight, trigger and cable loads land mostly on P3 and the room; the support triangle's inradius",
        "is ~33 mm and a 10 N upward cable pull at the grip is held by the weight alone (A2: 0.09-0.35 N m).",
    ]
    for i, t in enumerate(notes):
        s.text((60, 770 + 15 * i), t, size=11)
    s.save("paddle-compass.svg")


if __name__ == "__main__":
    paddle()
    print("written")


# =================================================================== wave 3: cart station
def cart_station():
    import cable_path as cp
    s = Svg(1240, 1060)
    title(s, "Cart station: the welding cart carries the whole cable system and the weld module",
          "Weldpro 3-tier cart (40.5 x 18.2 x 30.7 in, trays 20.9 x 13 in) [listing]. Tray heights, unit placement and cylinder size are assumptions. mm, to scale.")
    parts, gb = gun_plate_frame()
    TRAY = 740.0
    FEET = TRAY + 12.0           # rotator feet on the module plate
    DOTZ = FEET + 238.4 - 6.35   # dot above floor
    U0 = 150.0                   # tube axis from the cart's front end
    red, blue, green, gray, brown = "#d00000", "#1f4e9c", "#1b5e20", "#555", "#9b8563"
    # ---- side elevation: u along cart length (front at left), v = height above floor
    k = 0.52
    e = View(s, (70, 80 + 1450 * k), k)
    def E(u, z):
        return e.p(u, z)
    s.text((60, 72), "SIDE ELEVATION from the operator's side (front of cart at left)", size=12, weight="bold")
    s.line(E(-60, 0), E(1300, 0), stroke="#999", width=1)
    # cart frame + trays
    for z, u0, u1, lab in ((130, 60, 900, "bottom tray (33.1 x 13.8 in)"), (TRAY, 0, 531, "upper tray (20.9 x 13 in)")):
        s.poly([E(u, zz) for u, zz in [(u0, z), (u1, z), (u1, z - 12), (u0, z - 12)]], fill="#ccc", stroke=gray)
        s.text(E(u0 + 5, z - 30), lab, size=9, color=gray)
    s.poly([E(u, zz) for u, zz in [(0, 480), (531, 480), (531, 468), (0, 468)]], stroke=gray, dash="4,3")
    s.text(E(360, 495), "middle tray removed", size=9, color=gray)
    for u in (0, 531, 1029):
        s.line(E(u, 60), E(u, TRAY), stroke=gray, width=3)
    for u in (40, 980):
        s.circle(E(u, 50), 50 * k, stroke=gray, width=2)
    # cylinder at rear
    s.poly([E(u, z) for u, z in [(700, 80), (880, 80), (880, 1250), (840, 1330), (740, 1330), (700, 1250)]], fill="#eef3e8", stroke="#6a8a4a")
    s.text(E(705, 1200), "argon cylinder (height depends on size)", size=9, color="#6a8a4a")
    # X1 Pro on bottom tray, feeder on middle tray
    s.poly([E(u, z) for u, z in [(80, 130), (550, 130), (550, 465), (80, 465)]], fill="#e9e1f5", stroke="#6a4c93")
    s.text(E(100, 300), "X1 Pro unit 470 x 205 x 335, 21 kg (bottom tray)", size=9, color="#6a4c93")
    s.text(E(100, 270), "up to 2.5 kW dissipated: bottom tray, exhaust aimed away", size=9, color="#6a4c93")
    s.poly([E(u, z) for u, z in [(330, FEET), (510, FEET), (510, FEET + 200), (330, FEET + 200)]], fill="#f1ecf8", stroke="#6a4c93")
    s.text(E(335, FEET + 180), "wire feeder on the", size=9, color="#6a4c93")
    s.text(E(335, FEET + 160), "module, under the tail", size=9, color="#6a4c93")
    # module plate + rotator + tube
    s.poly([E(u, z) for u, z in [(20, TRAY + 3), (520, TRAY + 3), (520, FEET), (20, FEET)]], fill="#f6c7cf", stroke="#b00020")
    s.text(E(20, TRAY - 55), "weld module plate on 3 hard feet (the loop lives here)", size=9, color="#b00020")
    s.poly([E(u, z) for u, z in [(U0 - 150, FEET + 24), (U0 + 150, FEET + 24), (U0 + 150, FEET + 36), (U0 - 150, FEET + 36)]], fill="#ddd", stroke=gray)
    s.poly([E(u, z) for u, z in [(U0 - 75, FEET + 36), (U0 + 75, FEET + 36), (U0 + 75, FEET + 86), (U0 - 75, FEET + 86)]], fill="#ddd", stroke=gray)
    s.poly([E(u, z) for u, z in [(U0 - 63.5, DOTZ - 146), (U0 + 63.5, DOTZ - 146), (U0 + 63.5, DOTZ + 6.35), (U0 - 63.5, DOTZ + 6.35)]], stroke="#333", width=1.4)
    # purge hose from cylinder up through trays
    s.path(f"M {E(760, 1100)[0]:.1f} {E(760, 1100)[1]:.1f} C {E(640, 900)[0]:.1f} {E(640, 900)[1]:.1f} {E(U0 + 20, 600)[0]:.1f} {E(U0 + 20, 600)[1]:.1f} {E(U0, FEET)[0]:.1f} {E(U0, FEET)[1]:.1f}",
           stroke="#6a8a4a", width=1.5, dash="5,3")
    s.text(E(U0 + 25, 640), "purge up through a tray hole into the Ø90 passage", size=9, color="#6a8a4a")
    # gun: tube-frame y (-) maps to +u; z above plate + DOTZ
    def G(q):
        return (U0 - q[1], q[2] + DOTZ)
    for kpart in ["grip", "housing", "lens", "tube", "nozzle"]:
        h = hull([G(q) for q in parts[kpart]])
        s.poly(e.ps(h), fill="#f3d9a8", stroke="#7a4b00", width=1.0, opacity=0.9)
    dotu, dotz = U0, DOTZ
    s.circle(E(dotu, dotz), 3, fill=red, stroke=red)
    # cable: exit -> lead -> arc R 375 -> vertical drop
    p = cp.path(45, 30, -15, 375.0)
    gbu, gbz = U0 - p["gb"][1], DOTZ + p["gb"][2]
    stu, stz = U0 - p["start"][1], DOTZ + p["start"][2]
    s.circle(E(gbu, gbz), 3.5, fill=green, stroke=green)
    s.line(E(gbu, gbz), E(stu, stz), stroke=green, width=3)
    # arc in the projected plane (heading -105 deg: projected length factor cos(15))
    el = math.radians(p["elev"])
    Rp = 375.0
    cu = stu - Rp * math.sin(el) * 0.966
    cz = stz - Rp * math.cos(el)
    pts = []
    for i in range(41):
        a = el + (-math.pi / 2 - el) * i / 40
        pts.append(E(cu + Rp * 0.966 * (math.sin(el) - math.sin(el) + math.sin(el) - math.sin(a) + math.sin(a)) , 0))
    # simpler: parametric circle in (u, z): tangent direction (cos a, sin a); centre below-left
    pts = []
    cu = stu + (-Rp * math.sin(el)) * 0.966 * 0 + 0
    for i in range(41):
        a = el - (el + math.pi / 2) * i / 40
        du = Rp * (math.sin(el) - math.sin(a)) * -1
        dz = Rp * (math.cos(a) - math.cos(el))
        pts.append(E(stu + 0.966 * Rp * (math.sin(a + 0) * 0 + (math.sin(el) - math.sin(a)) * -1 * -1), stz + dz))
    s.path("M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts), stroke=green, width=3)
    endu = stu + 0.966 * Rp * (math.sin(el) + 1)
    endz = stz + Rp * (math.cos(-math.pi / 2) - math.cos(el))
    s.line(E(endu, endz), E(endu, 560), stroke=green, width=3)
    s.text(E(endu - 330, endz + 120), "fixed-shape umbilical + wire conduit: one bend, R 375,", size=9, color=green)
    s.text(E(endu - 330, endz + 95), "on a printed saddle carried by a mast at the rear", size=9, color=green)
    # mast + saddle
    s.line(E(endu + 25, 700), E(endu + 25, stz + 260), stroke=blue, width=5)
    s.text(E(endu + 35, stz + 250), "mast", size=9, color=blue)
    # stored excess: S on the cart side (dashed)
    s.path(f"M {E(endu, 560)[0]:.1f} {E(endu, 560)[1]:.1f} C {E(endu, 180)[0]:.1f} {E(endu, 180)[1]:.1f} {E(endu - 700, 180)[0]:.1f} {E(endu - 700, 180)[1]:.1f} {E(endu - 700, 480)[0]:.1f} {E(endu - 700, 480)[1]:.1f}",
           stroke=green, width=2, dash="6,4")
    s.text(E(endu - 690, 105), "excess ~3 m stored on the cart side panel as an S of R >= 350 turns (no net twist), then to the unit", size=9, color=green)
    s.text(E(dotu - 10, dotz + 40), "dot ~1.0 m above floor", size=9, color=red, anchor="end")
    s.text(E(gbu + 120, gbz + 230), f"cable apex ~{DOTZ + p['apex']:.0f} mm above floor", size=9, color=green)
    # ---- plan
    k2 = 0.42
    v = View(s, (760, 150 + 240 * k2), k2)
    def P(u, w):
        return v.p(u, w)
    s.text((740, 72), "PLAN (operator at the bottom)", size=12, weight="bold")
    s.poly([P(u, w) for u, w in [(0, 231), (1029, 231), (1029, -231), (0, -231)]], fill="#f4f4f4", stroke=gray)
    s.poly([P(u, w) for u, w in [(0, 165), (531, 165), (531, -165), (0, -165)]], fill="#e4e4e4", stroke=gray)
    s.circle(P(790, 0), 90 * k2, fill="#eef3e8", stroke="#6a8a4a")
    s.circle(P(U0, 0), 63.5 * k2, stroke="#333")
    s.poly([P(u, w) for u, w in [(20, 150), (520, 150), (520, -150), (20, -150)]], stroke="#b00020", dash="5,3")
    for kpart in ["grip", "housing", "lens", "tube", "nozzle"]:
        h = hull([(U0 - q[1], q[0]) for q in parts[kpart]])
        s.poly(v.ps(h), fill="#f3d9a8", stroke="#7a4b00", width=1.0, opacity=0.9)
    s.circle(P(U0, R_IN), 3, fill=red, stroke=red)
    dxy = p["drop_xy"]
    s.line(P(U0 - p["gb"][1], p["gb"][0] + R_IN), P(U0 - dxy[1], dxy[0]), stroke=green, width=3)
    s.circle(P(U0 - dxy[1], dxy[0]), 4, fill=green, stroke=green)
    s.text(P(560, -210), "drop point ~840-910 mm from the dot", size=9, color=green)
    s.text(P(0, -280), "OPERATOR (long side)", size=11, weight="bold", color="#444")
    notes = [
        "Loop: gun support + rotator on the module plate only; the cart's trays and casters carry, never locate.",
        "Cable: unit -> S store -> mast saddle -> one R 375 bend -> clamp on the module -> grip. Same shape every tube.",
        "Feeder on the module plate under the gun tail: conduit short and in a fixed shape; purge and gun gas from the cart own cylinder.",
        "Loading from above: gun parks by a hinge through its cable exit (the cable only bends in its own plane).",
        "Rolls to the window fan or a laser-safe corner; the whole station moves as one piece.",
    ]
    import textwrap
    y = 380
    for t in notes:
        for j, line in enumerate(textwrap.wrap(t, 78)):
            s.text((740 + (12 if j else 0), y), line, size=10)
            y += 15
        y += 4
    s.save("cart-station.svg")


if __name__ == "__main__":
    cart_station()
    print("cart written")


# =================================================================== wave 4: split-mount station
def split_mount():
    s = Svg(1240, 960)
    title(s, "Split-mount station: the plate places the dot, the collar tilts the gun about it",
          "Carrier rollers on a line through the dot (30 deg off the radius), hub pin on the plate centre, P3 on a motorised pad on the collar. True opening pose. mm, to scale.")
    parts, gb = gun_plate_frame()
    red, blue, green, purple, orange = "#d00000", "#1f4e9c", "#1b5e20", "#8a2be2", "#b35900"
    psi = math.radians(30)
    L = (-math.cos(psi), math.sin(psi))
    dot = (R_IN, 0.0)
    P1 = (dot[0] + 34 * L[0], 34 * L[1])
    P2 = (dot[0] + 90 * L[0], 90 * L[1])
    P3 = (-70.0, -250.0)
    k = 1.2
    v = View(s, (120 + 110 * k, 110 + 120 * k), k)
    def P(x, y):
        return v.p(-y, x)
    s.text((60, 80), "PLAN", size=12, weight="bold")
    s.poly([P(x, y) for x, y in [(-170, 120), (110, 120), (110, -330), (-170, -330)]], fill="#efe7da", stroke="#9b8563")
    s.circle(P(0, 0), 80 * k, fill="#ffffff", stroke="#9b8563")
    s.text(P(-160, 110), "collar plate at rim height (table opening)", size=10, color="#6b5a3a")
    s.circle(P(0, 0), R_OD * k, stroke="#333", width=1.5)
    s.circle(P(0, 0), R_IN * k, stroke="#333", width=0.8, dash="3,2")
    s.circle(P(0, 0), 27.3 * k, stroke="#888", dash="2,2")
    
    # line through dot
    s.line(P(dot[0] + 5 * -L[0], 5 * -L[1]), P(dot[0] + 120 * L[0], 120 * L[1]), stroke=red, width=1, dash="6,3")
    s.text(P(100, 112), "red dashes: tilt line through the dot, 30 deg off the radius", size=9, color=red)
    # carrier outline (rollers + gun mount), paddle outline (hub -> P3)
    carrier = [(P1[0] + 8, P1[1] - 12), (P2[0] - 8, P2[1] + 12), (P2[0] - 20, P2[1] - 6), (-30, -40), (-40, -120), (-10, -120), (20, -30)]
    s.poly([P(x, y) for x, y in carrier], fill="#fde2c4", stroke=orange, width=1.3, opacity=0.8)
    s.text(P(-128, 112), "orange: carrier (rollers + roll yoke + gun) on X/Y slides", size=9, color=orange)
    paddle = [(-12, 12), (12, 12), (12, -10), (-40, -150), (-58, -262), (-84, -262), (-84, -238), (-66, -150), (-14, -12)]
    s.poly([P(x, y) for x, y in paddle], fill="#c9d7f0", stroke=blue, width=1.3, opacity=0.8)
    s.text(P(-110, -150), "paddle: hub -> P3; carries the X/Y slides", size=9, color=blue)
    s.circle(P(0, 0), 7 * k, fill="#ffffff", stroke=blue, width=1.4)
    for p, n in ((P1, "P1"), (P2, "P2")):
        s.circle(P(*p), 6.5 * k, fill=red, stroke=red)
        s.text(P(p[0] + 10, p[1] + 10), n, size=11, color=red, weight="bold")
    s.circle(P(*P3), 7, fill=purple, stroke=purple)
    s.text(P(P3[0] - 16, P3[1] + 10), "P3 on a motorised lift (hole tilt)", size=10, color=purple)
    s.line(P(-100, -205), P(-100, -300), stroke=purple, width=5)
    s.text(P(-112, -300), "fence (azimuth)", size=9, color=purple)
    draw_gun(v, parts, lambda q: (-q[1], q[0]))
    s.circle(P(*dot), 3.5, fill=red, stroke=red)
    s.circle(P(gb[0], gb[1]), 3.5, fill=green, stroke=green)
    s.line(P(gb[0], gb[1]), P(-12, -300), stroke=green, width=3)
    # joint camera on +Y
    s.rect(*P(20, 100), 18, 14, fill="#555")
    s.text(P(28, 104), "joint camera (+Y)", size=9, color="#333")
    # ---------------- elevation along the tilt line's normal is complex; show YZ view
    e = View(s, (760, 560), 0.95)
    def E(y, z):
        return e.p(-y, z)
    s.text((660, 80), "ELEVATION (looking toward +X)", size=12, weight="bold")
    RECESS_ = 6.35
    s.poly([E(y, z) for y, z in [(R_OD, RECESS_), (-R_OD, RECESS_), (-R_OD, -140), (R_OD, -140)]], stroke="#333", width=1.4)
    s.poly([E(y, z) for y, z in [(R_IN, 0), (-R_IN, 0), (-R_IN, -6.35), (R_IN, -6.35)]], fill="#bbb", stroke="#333")
    s.poly([E(y, z) for y, z in [(-80, RECESS_), (-330, RECESS_), (-330, RECESS_ - 14), (-80, RECESS_ - 14)]], fill="#efe7da", stroke="#9b8563")
    s.poly([E(y, z) for y, z in [(80, RECESS_), (140, RECESS_), (140, RECESS_ - 14), (80, RECESS_ - 14)]], fill="#efe7da", stroke="#9b8563")
    # hub + magnet hold-down
    s.poly([E(y, z) for y, z in [(8, 0), (-8, 0), (-8, 14), (8, 14)]], stroke="#555")
    s.poly([E(y, z) for y, z in [(10, 18), (-10, 18), (-10, 34), (10, 34)]], fill="#c9d7f0", stroke=blue)
    s.text(E(-12, 50), "hub: pin in a spherical bearing; RC62 magnets pull on a 430 disc on the seat", size=9)
    s.text(E(-12, 40), "(hold-down internal to the plate: no net force on the tube)", size=9)
    arm = [(-10, 30), (-58, 30), (-70, 24), (-262, 24), (-262, 16), (-70, 16), (-58, 22), (-10, 22)]
    s.poly([E(y, z) for y, z in arm], fill="#c9d7f0", stroke=blue, width=1.3)
    for p in (P1, P2):
        s.circle(E(p[1], 6.5), 6.5 * 0.95, fill=red, stroke=red)
    s.text(E(P2[1] + 10, -18), "P1, P2 rollers on the plate face", size=9, color=red, anchor="end")
    # P3 lift
    s.poly([E(y, z) for y, z in [(-240, RECESS_), (-262, RECESS_), (-262, RECESS_ - 60), (-240, RECESS_ - 60)]], fill="#e9e1f5", stroke=purple)
    s.circle(E(-250, 20), 6, fill=purple, stroke=purple)
    s.text(E(-251, -70), "P3 lift: NEMA 17 + T8 under the collar, ~5 mm per degree", size=9, color=purple, anchor="middle")
    draw_gun(e, parts, lambda q: (-q[1], q[2]))
    s.circle(E(0, 0), 3.5, fill=red, stroke=red)
    for y, ztop in ((-90, 95), (-200, 120)):
        s.line(E(y, 30), E(y, ztop), stroke=orange, width=4)
    s.rect(*E(-120, 205), 22, 14, fill="#333")
    s.text(E(-150, 215), "inclinometer on the shell", size=9)
    s.circle(E(gb[1], gb[2]), 3.5, fill=green, stroke=green)
    s.line(E(gb[1], gb[2]), E(-300, 60), stroke=green, width=3)
    notes = [
        "Who sets what:  plate centre (pin) -> dot x, y;  plate face (P1, P2 on a line through the dot) -> dot height, tilt across that line;",
        "  collar (P3 lift) -> rotation about the line through the dot (exact: the dot is on it);  collar fence -> azimuth (doesn't matter).",
        "Motors: P3 lift (tilt), roll yoke (grip axis), X and Y micro-slides on the paddle (wall/cap offset, plan-angle trim), shelf Z (LOAD/WELD).",
        "Feedback: inclinometer for both rotations (gravity is square to the tube), slide counts for X/Y, joint camera for the dot.",
        "Tube length, runout and face tilt never reach the dot: the gun rides the plate.  The shelf only has to bring the plate into range.",
    ]
    for i, t in enumerate(notes):
        s.text((60, 850 + 16 * i), t, size=10)
    s.save("split-mount-station.svg")


if __name__ == "__main__":
    split_mount()
    print("split written")
