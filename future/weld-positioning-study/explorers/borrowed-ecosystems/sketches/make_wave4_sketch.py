"""Wave-4 sketch: F, the hand-steered isocentre. Corrected opening pose.
Supports schematic. python3 make_wave4_sketch.py -> f-hand-steered-isocentre.svg
"""
import os
import numpy as np
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
POSE = (45, 30, -15)
GB = to_bench(G.pose_point(G.GRIP_BASE, *POSE))
GAX = (GB - DOT) / np.linalg.norm(GB - DOT)
CG = to_bench(G.pose_point(G.CG_LOCAL, *POSE))
DZ = DOT[2]


def along(t):
    return DOT + GAX * t


def main():
    s = Svg(1000, 720, 'yz', 1.05, (640, 620), "Seen from +X: the hole hinge's axis points at you through the dot")
    s.line2((-600, 0), (330, 0), stroke="#6b4f2a", w=3)
    s.text2(-590, 10, "work side below: X micrometer, Y read as the yaw knob, Z per tube (one-knob / who-moves-what)", size=10, color="#6b4f2a")
    draw_tube_yz(s)
    draw_gun(s, POSE, shell=True)
    draw_cable(s, POSE, tail=150)
    piv = np.array([0.0, DZ])
    # disc rotor on the hinge (face-on), caliper at the top
    s.circle2(tuple(piv), 80, stroke="#6c757d", w=3)
    s.circle2(tuple(piv), 14, stroke="#1b7f3b", fill="#fff", w=2)
    s.circle2(tuple(piv), 3, stroke="#1b7f3b", fill="#1b7f3b")
    s.rect2(-18, DZ + 70, 18, DZ + 96, stroke="#111", fill="#495057")
    s.text2(22, DZ + 92, "bicycle cable disc brake on a 160 mm rotor = the hinge lock", size=10)
    s.text2(22, DZ - 30, "hole hinge: preloaded bearing pair on the X line", size=10, color="#1b7f3b")
    s.text2(22, DZ - 43, "through the dot, 40 mm outboard (in front here)", size=10, color="#1b7f3b")
    # spoke along the grip-axis projection
    d = np.array([GAX[1], GAX[2]]) / np.hypot(GAX[1], GAX[2])
    tip = piv + d * 350
    s.line2(tuple(piv), tuple(tip), stroke="#1b7f3b", w=8)
    # zero-length spring: attach on the pivot->CG line, anchor above the pivot, pulley
    cgv = np.array([CG[1], CG[2]]) - piv
    cgu = cgv / np.linalg.norm(cgv)
    att = piv + cgu * 150
    anc = piv + np.array([0, 150])
    s.line2(tuple(piv), tuple(att), stroke="#1b7f3b", w=4, dash="6,3")
    s.circle2(tuple(att), 4, stroke="#111", fill="#fff")
    s.circle2(tuple(anc), 7, stroke="#111", fill="#dee2e6")
    s.line2(tuple(att), tuple(anc), stroke="#b5451b", w=1.5)
    s.spring2(tuple(anc), tuple(anc + np.array([120, 60])), n=8, amp=5)
    s.circle2(tuple(anc + np.array([120, 60])), 3, stroke="#111", fill="#111")
    s.text2(60, DZ + 205, "counterbalance: spring behind a pulley = zero-length spring", size=10, color="#b5451b")
    s.text2(60, DZ + 192, "tau = k a b sin(theta) matches m g r sin(theta) at every hole angle;", size=10, color="#b5451b")
    s.text2(60, DZ + 179, "anchor height b is the trim knob (a video fluid head's counterbalance)", size=10, color="#b5451b")
    s.circle2((CG[1], CG[2]), 4, stroke="#111", fill="#ffd166")
    # tiller from the spoke, up and back, away from the dot
    t0 = piv + d * 220
    handle = t0 + np.array([-40, 160])
    s.line2(tuple(t0), tuple(handle), stroke="#333", w=6)
    s.rect2(handle[0] - 30, handle[1] - 8, handle[0] + 30, handle[1] + 8, stroke="#111", fill="#adb5bd")
    s.text2(handle[0] - 150, handle[1] + 40, "tiller: hand steers the hole angle here, 250+ mm from the dot;", size=10)
    s.text2(handle[0] - 150, handle[1] + 27, "brake lever (lock) and trigger lever (Bowden to the shell) on it", size=10)
    # roll sleeve and rings
    a, b = along(295), along(430)
    s.line((a[0], a[1], a[2]), (b[0], b[1], b[2]), stroke="#7b2cbf", w=22)
    s.line((a[0], a[1], a[2]), (b[0], b[1], b[2]), stroke="#e0c3fc", w=18)
    for t in (315, 410):
        c = along(t)
        nrm = np.array([-d[1], d[0]])
        s.line2((c[1] - 18 * nrm[0], c[2] - 18 * nrm[1]), (c[1] + 18 * nrm[0], c[2] + 18 * nrm[1]), stroke="#111", w=6)
    c = along(370)
    s.line2((c[1], c[2]), (c[1] - 20, c[2] + 110), stroke="#7b2cbf", w=4)
    s.text2(-590, 520, "roll: who-moves-what's stub shaft on the grip axis (or hinged rings); its own small", size=10, color="#7b2cbf")
    s.text2(-590, 507, "zero-length spring (0.9 sin(roll) N*m), drag, tiller, lock", size=10, color="#7b2cbf")
    # camera on +Y
    s.rect2(200, 330, 232, 352, stroke="#333", fill="#222")
    s.line2((200, 340), (4, DZ + 3), stroke="#999", w=1, dash="4,4")
    s.text2(150, 366, "dot camera (+Y side): live dot vs corner", size=10)
    s.rect2(200, 40, 280, 90, stroke="#333", fill="#f1f3f5")
    s.text2(206, 76, "hole 30.4", size=10, weight="bold")
    s.text2(206, 61, "roll 45.1", size=10, weight="bold")
    s.text2(206, 46, "dot +0.02", size=10, weight="bold")
    s.text2(196, 100, "readout (encoders + camera)", size=9)
    # grease damper note
    s.text2(22, DZ - 70, "drag: damping-grease film in the hinge housing (~1 N*m*s/rad)", size=10, color="#1b7f3b")

    # --------- principle panel -----------------------------------------------
    p = Svg(330, 720, 'xy', 1.0, (120, 420), "Zero-length spring balance (principle)")
    p.circle2((0, 0), 5, stroke="#111", fill="#111")
    p.text2(-60, -20, "pivot", size=10)
    th = np.radians(40)
    arm = np.array([np.sin(th), np.cos(th)]) * 170
    p.line2((0, 0), tuple(arm), stroke="#1b7f3b", w=5)
    p.circle2(tuple(arm), 9, stroke="#111", fill="#ffd166")
    p.text2(arm[0] + 12, arm[1], "CG (m)", size=10)
    p.line2(tuple(arm), (arm[0], arm[1] - 60), stroke="#333", w=1.5, arrow=True)
    p.text2(arm[0] + 6, arm[1] - 50, "m g", size=10)
    at = arm * 0.55
    p.circle2(tuple(at), 4, stroke="#111", fill="#fff")
    an = np.array([0, 110])
    p.circle2(tuple(an), 6, stroke="#111", fill="#dee2e6")
    p.line2(tuple(at), tuple(an), stroke="#b5451b", w=2)
    p.text2(-100, 150, "anchor b above the pivot", size=10)
    p.text2(at[0] + 8, at[1] - 10, "attach a along the CG line", size=10)
    p.text2(-110, -80, "gravity: m g r sin(theta)", size=10)
    p.text2(-110, -96, "spring (zero free length):", size=10)
    p.text2(-110, -110, "k a b sin(theta)", size=10)
    p.text2(-110, -126, "equal for all theta if k a b = m g r", size=10, weight="bold")
    p.text2(-110, -150, "The same law holds for roll about the", size=10)
    p.text2(-110, -164, "grip axis (0.90 sin(roll) N*m, 1.5 kg).", size=10)
    p.text2(-110, -188, "Anglepoise lamps and video fluid heads", size=10)
    p.text2(-110, -202, "use it; drag makes the hand smooth.", size=10)
    compose([(s, 10, 40), (p, 1020, 40)], os.path.join(HERE, "f-hand-steered-isocentre.svg"),
            title="F  Hand-steered isocentre: balanced, damped, lockable hinges about the dot, steered by hand while the camera watches",
            notes=["Combines one-knob-one-parameter's isocentric gantry (rotations about the dot, walk test), sequence-of-use's HAND state (the hand as actuator), machine-that-learns' dot camera, and the film/lamp counterbalance.",
                   "Corrected opening pose. Rotor, spring, tiller and camera placement schematic; gun mass 1.5 kg assumed for the spring numbers."])


if __name__ == "__main__":
    main()
