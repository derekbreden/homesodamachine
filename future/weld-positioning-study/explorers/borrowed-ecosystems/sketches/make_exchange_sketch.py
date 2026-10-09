"""Wave-2 exchange sketch: one-knob-one-parameter's isocentric gantry with its two
gun-side rotations realised as gravity-preloaded 'sine arms' on bought
metrology (gauge-block stack for the hole angle, micrometer under a lever for
roll) and the roll carried in a pair of hinged clamshell rings around a printed
sleeve on the grip axis. Drawn at the corrected opening pose (grip 45, hole
dial 30, vertical -15). Supports are schematic.

python3 make_exchange_sketch.py -> x-okop-gravity-sine-arms.svg
"""
import os
import numpy as np
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = (45, 30, -15)
GB = to_bench(G.pose_point(G.GRIP_BASE, *POSE))
GAX = (GB - DOT) / np.linalg.norm(GB - DOT)
DZ = DOT[2]


def along(t):
    return DOT + GAX * t


def main():
    # ---------------- side view from +X (y tangent right, z up) -------------
    s = Svg(900, 640, 'yz', 1.05, (620, 570), "Seen from +X: the hole axis points at you through the dot")
    s.line2((-560, 0), (260, 0), stroke="#6b4f2a", w=3)
    s.text2(-555, 8, "baseplate (couch stack below the rotator not drawn)", size=10, color="#6b4f2a")
    draw_tube_yz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=180)
    # hole pivot (bearing pair on the X line, ~40 mm outboard of the dot)
    s.circle2((0, DZ), 14, stroke="#1b7f3b", fill="#fff", w=2)
    s.circle2((0, DZ), 3, stroke="#1b7f3b", fill="#1b7f3b")
    s.text2(20, DZ - 26, "hole pivot: bearing pair on the X line through the dot,", size=10, color="#1b7f3b")
    s.text2(20, DZ - 39, "40 mm outboard (in front of the tube in this view)", size=10, color="#1b7f3b")
    # spoke plate in the plane x = dot + 40, following the grip axis' YZ projection
    d = np.array([GAX[1], GAX[2]]) / np.hypot(GAX[1], GAX[2])
    p0 = np.array([0, DZ])
    tip = p0 + d * 360
    s.line2(tuple(p0), tuple(tip), stroke="#1b7f3b", w=8)
    s.text2(tip[0] - 20, tip[1] + 34, "spoke (turns about the hole axis)", size=10, color="#1b7f3b")
    # sine ball at L = 200 on the spoke, gauge stack under it
    L = 200.0
    ball = p0 + d * L
    s.circle2(tuple(ball), 5, stroke="#111", fill="#adb5bd")
    ref_z = 240.0
    s.rect2(ball[0] - 60, ref_z - 12, ball[0] + 40, ref_z, stroke="#333", fill="#8d99ae")
    s.text2(ball[0] - 250, ref_z - 26, "anvil on the Z-carriage bracket (same body as the pivot)", size=10)
    h = ball[1] - 5 - ref_z
    n = 4
    ys = np.linspace(ref_z, ball[1] - 5, n + 1)
    for i in range(n):
        s.rect2(ball[0] - 12, ys[i], ball[0] + 12, ys[i + 1], stroke="#333", fill="#e9ecef" if i % 2 else "#ced4da")
    s.text2(ball[0] + 20, (ref_z + ball[1]) / 2 + 10, f"gauge-block stack h = {h:.1f} mm", size=10, weight="bold")
    s.text2(ball[0] + 20, (ref_z + ball[1]) / 2 - 4, "sets the hole angle: sin(e - e0) = (h - h0)/L, L = 200 mm", size=10)
    s.text2(ball[0] + 20, (ref_z + ball[1]) / 2 - 18, "gun weight presses the ball down with 8-19 N (1-2 kg)", size=10, color="#b5451b")
    s.line2((ball[0] - 20, ball[1] + 40), (ball[0] - 20, ball[1] + 12), stroke="#b5451b", w=1.5, arrow=True)
    # sleeve on the grip axis, two hinged rings
    a, b = along(295), along(430)
    s.line((a[0] + 0, a[1], a[2]), (b[0], b[1], b[2]), stroke="#7b2cbf", w=26)
    s.line((a[0], a[1], a[2]), (b[0], b[1], b[2]), stroke="#e0c3fc", w=22)
    for t in (315, 410):
        c = along(t)
        nrm = np.array([0, -d[1], d[0]])
        s.line2((c[1] - 20 * nrm[1] / 1, c[2] - 20 * nrm[2]), (c[1] + 20 * nrm[1], c[2] + 20 * nrm[2]), stroke="#111", w=7)
    c = along(360)
    s.text2(c[1] - 240, c[2] + 70, "printed sleeve (halves) on the grip axis behind the butt;", size=10, color="#7b2cbf")
    s.text2(c[1] - 240, c[2] + 57, "two hinged clamshell rings 95 mm apart (lens collar /", size=10, color="#7b2cbf")
    s.text2(c[1] - 240, c[2] + 44, "tube-ring class): they close around it, nothing threads", size=10, color="#7b2cbf")
    # ring bracket from spoke tip inboard (drawn as short link)
    s.line2(tuple(tip), (along(410)[1], along(410)[2] - 16), stroke="#1b7f3b", w=5)
    s.line2(tuple(p0 + d * 300), (along(315)[1], along(315)[2] - 16), stroke="#1b7f3b", w=5)
    s.text2(-540, -14, "Knob kinds (one-knob-one-parameter's vocabulary): gauge stack and micrometer are knobs; the rings' three screws are calibration screws;", size=10)
    s.text2(-540, -27, "lifting the spoke off the stack (a lever) is a motion to a stop that returns to the same stack.", size=10)

    # ---------------- end view along the grip axis (schematic) ---------------
    e = Svg(420, 640, 'xy', 1.6, (190, 330), "Looking along the grip axis at the rear ring (schematic)")
    e.circle2((0, 0), 42, stroke="#7b2cbf", fill="#e0c3fc", w=2)
    e.circle2((0, 0), 12, stroke="#555", fill="#555")
    e.text2(-30, -2, "umbilical", size=9, color="#fff")
    e.circle2((0, 0), 52, stroke="#111", w=6)
    e.circle2((0, 52), 5, stroke="#111", fill="#fff", w=2)
    e.text2(8, 64, "hinge", size=10)
    e.rect2(-8, -64, 8, -52, stroke="#111", fill="#6c757d")
    e.text2(12, -66, "clamp knob (lock)", size=10)
    for ang in (90, 210, 330):
        t = np.radians(ang)
        e.line2((52 * np.cos(t), 52 * np.sin(t)), (44 * np.cos(t), 44 * np.sin(t)), stroke="#b5451b", w=3)
    e.text2(-100, 88, "3 PTFE-tipped screws per ring:", size=10, color="#b5451b")
    e.text2(-100, 76, "calibration (sleeve axis onto grip axis)", size=10, color="#b5451b")
    # roll lever and micrometer
    e.line2((30, -30), (105, -30), stroke="#7b2cbf", w=6)
    e.circle2((105, -30), 4, stroke="#111", fill="#adb5bd")
    e.rect2(98, -80, 112, -38, stroke="#111", fill="#dee2e6")
    e.rect2(95, -100, 115, -80, stroke="#111", fill="#adb5bd")
    e.text2(10, -115, "micrometer under a 100 mm lever:", size=10, weight="bold")
    e.text2(10, -128, "roll knob, 0.01 mm = 0.006 deg", size=10)
    e.text2(10, -141, "gravity roll torque 0.3-0.9 N*m -> 3-9 N on the tip", size=10, color="#b5451b")
    ang = np.radians(np.linspace(200, 250, 10))
    e.poly2([(70 * np.cos(t), 70 * np.sin(t)) for t in ang], stroke="#b5451b", w=1.5, closed=False)
    e.line2((70 * np.cos(ang[-2]), 70 * np.sin(ang[-2])), (70 * np.cos(ang[-1]), 70 * np.sin(ang[-1])), stroke="#b5451b", w=1.5, arrow=True)
    e.text2(-160, -95, "one-signed for roll > ~10 deg", size=10, color="#b5451b")
    compose([(s, 10, 40), (e, 920, 40)], os.path.join(HERE, "x-okop-gravity-sine-arms.svg"),
            title="Exchange branch for one-knob-one-parameter: both gun-side rotations as gravity-preloaded sine arms on bought metrology",
            notes=["Corrected opening pose (grip 45, hole dial 30, vertical -15). Gravity torque about the hole axis is 1.4-3.1 N*m and about the grip axis 0.3-0.9 N*m for 1-2 kg over the working range, one sign each.",
                   "Parts: WEN 81-pc gauge blocks ($105), micrometer head ($16, partner's sourcing), hinged lens-collar/tube-ring clamshells or printed equivalents, deep-groove pivot bearings, printed sleeve and spoke."])


if __name__ == "__main__":
    main()
