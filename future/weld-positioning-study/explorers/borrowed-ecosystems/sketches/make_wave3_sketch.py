"""Wave-3 sketch: E, the film-grip carrier (iso-elastic stabilizer arm on a
C-stand, gimbal at the gun's CG, umbilical saddle on the same stand), with the
gun located by the tube rider (A1-S / A1-G). Corrected opening pose. Stand,
arm and saddle positions are schematic; bench height assumed 900 mm.

python3 make_wave3_sketch.py -> e-film-grip-carrier.svg
"""
import os
import numpy as np
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = (45, 30, -15)
CG = to_bench(G.pose_point(G.CG_LOCAL, *POSE))
BENCH_H = 900.0
STAND = np.array([-60.0, -720.0])      # stand riser position in plan (bench coords, off the bench end)
SOCKET_Z = 420.0                       # arm socket height above the bench top
SADDLE = np.array([-40.0, -470.0, 470.0])


def main():
    # ---------------- elevation from +X -------------------------------------
    s = Svg(980, 800, 'yz', 0.48, (720, 345), "Elevation from +X (y along the tangent, z up; floor 900 mm below the bench top)")
    s.line2((-1200, 0), (320, 0), stroke="#6b4f2a", w=3)
    s.rect2(-560, -BENCH_H, 300, 0, stroke="#b08968", w=1, dash="6,4")
    s.text2(-550, -40, "bench (VEVOR, height adjustable)", size=10, color="#6b4f2a")
    s.line2((-1400, -BENCH_H), (330, -BENCH_H), stroke="#555", w=2)
    s.text2(-1400, -BENCH_H + 12, "floor", size=10, color="#555")
    s.rect2(-125, 0, 125, 86, stroke="#777", fill="#efe9d8", dash="4,3")
    draw_tube_yz(s)
    draw_gun(s, POSE, shell=True)
    # rider (schematic block on the tube's +X side, seen through)
    s.rect2(-45, DOT[2] - 70, 45, DOT[2] + 12, stroke="#2a6f97", fill="#2a6f97", op=0.25, w=1.5)
    s.text2(60, DOT[2] - 60, "rider on the tube (A1-S wheels + A1-G goniometer):", size=10, color="#2a6f97")
    s.text2(60, DOT[2] - 90, "locates 5 DOF; carries only preload", size=10, color="#2a6f97")
    # C-stand: turtle base on the floor, riser up to socket height
    sy = STAND[1]
    s.line2((sy, -BENCH_H), (sy, SOCKET_Z + 60), stroke="#495057", w=7)
    for dy in (-220, 160):
        s.line2((sy, -BENCH_H + 120), (sy + dy, -BENCH_H), stroke="#495057", w=5)
    s.text2(sy - 330, -BENCH_H + 150, "stainless C-stand (turtle base + sandbag)", size=10)
    # arm socket and iso-elastic arm (two parallelogram sections)
    s.rect2(sy - 14, SOCKET_Z - 20, sy + 14, SOCKET_Z + 20, stroke="#111", fill="#6c757d")
    e1 = np.array([sy + 260, SOCKET_Z + 40])
    gim = np.array([CG[1], CG[2]])
    for a, b in (((sy, SOCKET_Z), tuple(e1)), (tuple(e1), (gim[0], gim[1] + 70))):
        a = np.array(a); b = np.array(b)
        s.line2(tuple(a + [0, 10]), tuple(b + [0, 10]), stroke="#b5451b", w=4)
        s.line2(tuple(a - [0, 10]), tuple(b - [0, 10]), stroke="#b5451b", w=4)
    s.circle2(tuple(e1), 8, stroke="#111", fill="#fff", w=2)
    s.text2(sy + 120, SOCKET_Z + 205, "iso-elastic stabilizer arm (Steadicam / zero-G tool-arm principle):", size=10, color="#b5451b")
    s.text2(sy + 120, SOCKET_Z + 182, "near-constant lift over its travel, bearing hinges on vertical axes", size=10, color="#b5451b")
    s.line2((gim[0], gim[1] + 70), tuple(gim), stroke="#b5451b", w=3)
    s.circle2(tuple(gim), 9, stroke="#b5451b", fill="#ffd166", w=2)
    s.text2(gim[0] + 14, gim[1] + 18, "3-axis gimbal at the gun's CG (16 mm arm post)", size=10, color="#b5451b")
    s.text2(gim[0] + 14, gim[1] - 14, "wave 5: carry pins lock both tilt axes off the tube (E-s)", size=10, color="#7b2cbf")
    s.text2(60, DOT[2] - 120, "wave 5: LAND / WELD cam stops on a barrel-line slide (E-z)", size=10, color="#7b2cbf")
    # boom arm with umbilical saddle
    s.line2((sy, SOCKET_Z + 60), (SADDLE[1] + 60, SADDLE[2] + 30), stroke="#495057", w=4)
    s.circle2((sy, SOCKET_Z + 60), 7, stroke="#111", fill="#adb5bd")
    ang = np.radians(np.linspace(20, 160, 20))
    s.poly2([(SADDLE[1] + 90 * np.cos(a), SADDLE[2] - 90 + 90 * np.sin(a)) for a in ang], stroke="#555", w=5, closed=False)
    s.text2(SADDLE[1] - 700, SADDLE[2] + 150, "umbilical + conduit saddle (R>=350 arc) on the stand's boom", size=10)
    s.text2(SADDLE[1] - 700, SADDLE[2] + 125, "via a grip head; moves with the stand when it parks", size=10)
    # umbilical from the gun to the saddle and down to the cart
    p = cable_path(POSE, R=350, tail=0)
    s.poly(p[:10] + [np.array([SADDLE[0], SADDLE[1] + 60, SADDLE[2] - 10])], stroke="#555", w=3, closed=False)
    s.poly2([(SADDLE[1] - 60, SADDLE[2] - 40), (SADDLE[1] - 180, SADDLE[2] - 200), (SADDLE[1] - 230, -BENCH_H + 80)], stroke="#555", w=3, closed=False)
    s.text2(SADDLE[1] - 420, -300, "to laser unit / wire feeder on the cart", size=10, color="#555")
    # parking cup on the stand
    s.rect2(sy + 30, SOCKET_Z - 160, sy + 90, SOCKET_Z - 140, stroke="#111", fill="#dee2e6")
    s.text2(sy + 96, SOCKET_Z - 156, "docking cup: parks the gimbal", size=10)

    # ---------------- plan ---------------------------------------------------
    p2 = Svg(620, 800, 'xy', 0.5, (380, 190), "Plan")
    p2.rect2(-380, -560, 380, 300, stroke="#b08968", w=1, dash="6,4")
    p2.text2(-370, 285, "bench top (schematic)", size=10, color="#6b4f2a")
    p2.rect2(-150, -125, 150, 125, stroke="#999", dash="4,3")
    draw_tube_xy(p2)
    draw_gun(p2, POSE, shell=True)
    sx, sy = STAND
    for ang in (90, 210, 330):
        t = np.radians(ang)
        p2.line2((sx, sy), (sx + 220 * np.cos(t), sy + 220 * np.sin(t)), stroke="#495057", w=5)
    p2.circle2((sx, sy), 14, stroke="#111", fill="#6c757d")
    e1p = np.array([sx + 250, sy + 330])
    p2.line2((sx, sy), tuple(e1p), stroke="#b5451b", w=6)
    p2.line2(tuple(e1p), (CG[0], CG[1]), stroke="#b5451b", w=6)
    p2.circle2(tuple(e1p), 9, stroke="#111", fill="#fff", w=2)
    p2.circle2((CG[0], CG[1]), 9, stroke="#b5451b", fill="#ffd166", w=2)
    # parked position
    park = np.array([sx - 330, sy + 200])
    e1k = np.array([sx - 260, sy - 120])
    p2.line2((sx, sy), tuple(e1k), stroke="#b5451b", w=3, dash="6,4")
    p2.line2(tuple(e1k), tuple(park), stroke="#b5451b", w=3, dash="6,4")
    p2.circle2(tuple(park), 9, stroke="#b5451b", fill="none", w=2)
    p2.text2(park[0] - 40, park[1] + 20, "parked in the docking cup", size=10, color="#b5451b")
    p2.circle2((SADDLE[0], SADDLE[1]), 10, stroke="#555", fill="#ced4da")
    p2.text2(SADDLE[0] + 16, SADDLE[1], "saddle", size=10)
    p2.text2(sx + 20, sy - 30, "C-stand off the bench end", size=10)
    p2.text2(-370, -800, "The stand, arm and saddle locate nothing: floor reference and", size=10)
    p2.text2(-370, -830, "flex do not enter the dot. The tube rider locates.", size=10)
    compose([(s, 10, 40), (p2, 1000, 40)], os.path.join(HERE, "e-film-grip-carrier.svg"),
            title="E  Film-grip carrier: iso-elastic stabilizer arm on a C-stand, gimbal at the CG, umbilical saddle on the same stand",
            notes=["Carries: arm spring (2-5 kg window, tension knob) through a 3-axis gimbal at the CG, so no moment reaches the gun. Locates: the tube rider. Parks: swing into the docking cup, or roll the stand away with the saddle.",
                   "Corrected opening pose (grip 45, hole dial 30, vertical -15). Bench height 900 mm assumed; stand, arm geometry and saddle placement schematic."])


if __name__ == "__main__":
    main()
