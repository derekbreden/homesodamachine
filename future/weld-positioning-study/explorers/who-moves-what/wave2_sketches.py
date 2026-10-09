"""Wave 2 branch sketch for sequence-of-use's lid carrier: seat behind the station,
recipe stack on the lid, per-tube height taken by the work. Side view from -Y
(X right, Z up), matching their lid-side-view.svg. Gun = my capsule proxy.
Run: tools/cad-venv/bin/python wave2_sketches.py
"""
import math
import numpy as np
import sketches as S
from geometry import world, CAPSULES, FEATURES, R_IN, R_OUT, RIM, CAP_TOP, BENCH

HINGE = np.array([200.0, 0.0, RIM + 60.0])


def rot_y(p, ang_deg):
    a = math.radians(ang_deg)
    v = np.asarray(p) - HINGE
    c, s = math.cos(a), math.sin(a)
    # rotation about +Y through the hinge (positive lifts a point on the -X side)
    return HINGE + np.array([v[0] * c + v[2] * s, v[1], -v[0] * s + v[2] * c])


def draw():
    S.SCALE = 1.0
    W, H = 1520, 760
    s = S.Svg(W, H, "Wave 2 - lid carrier, re-allocated (side view from -Y; X right; hole dial 30)")
    ox, oy = 380, 720

    def P(p):
        return (ox + p[0], oy - (p[2] - BENCH))

    s.line((20, oy), (820, oy), S.INK, 2)
    s.text((24, oy + 16), "bench / common subplate", S.NOTE, 10)
    # rotator on three belt-linked screws (per-tube Z)
    sup = RIM - 238.4
    s.poly([P((-150, 0, sup + 24)), P((150, 0, sup + 24)), P((150, 0, sup + 36)), P((-150, 0, sup + 36))], color=S.WORK, fill=S.WORK, op=0.15)
    for fx in (-130, 130):
        s.line(P((fx, 0, BENCH)), P((fx, 0, sup + 24)), S.MECH, 4)
        s.circle(P((fx, 0, BENCH + 10)), 7, color=S.MECH, fill="#fff", w=1.5)
    s.line(P((-130, 0, BENCH + 10)), P((130, 0, BENCH + 10)), S.MECH, 1.2, dash="4,3")
    s.text(P((-300, 0, BENCH + 40)), "3 fine screws, ball/cone-vee-flat,", S.MECH, 10)
    s.text(P((-300, 0, BENCH + 27)), "one GT2 loop: one knob = pure Z", S.MECH, 10)
    s.text(P((-300, 0, BENCH + 14)), "(per tube, set in phase 2)", S.MECH, 10)
    s.poly([P((-75, 0, sup + 36)), P((75, 0, sup + 36)), P((75, 0, sup + 86)), P((-75, 0, sup + 86))], color=S.WORK, w=0.8, dash="3,2")
    # tube and plate (section)
    for x0 in (-R_OUT, R_IN):
        s.poly([P((x0, 0, RIM - 152.4)), P((x0 + (R_OUT - R_IN), 0, RIM - 152.4)), P((x0 + (R_OUT - R_IN), 0, RIM)), P((x0, 0, RIM))], color=S.WORK, fill=S.WORK, op=0.5)
    s.poly([P((-R_IN, 0, CAP_TOP - 6.35)), P((R_IN, 0, CAP_TOP - 6.35)), P((R_IN, 0, CAP_TOP)), P((-R_IN, 0, CAP_TOP))], color=S.WORK, fill=S.WORK, op=0.25)
    # H2 stationary swivel hanger (their kit K1) from -X, now unobstructed
    s.line(P((-330, 0, RIM + 50)), P((0, 0, RIM + 50)), "#7b1fa2", 5, op=0.7)
    s.line(P((0, 0, RIM + 50)), P((0, 0, CAP_TOP + 2)), "#7b1fa2", 3, op=0.7)
    s.line(P((-330, 0, BENCH)), P((-330, 0, RIM + 50)), "#7b1fa2", 5, op=0.4)
    s.text(P((-330, 0, RIM + 62)), "their H2 swivel hanger (-X side now free of lid structure)", "#7b1fa2", 10)
    # hinge post and hinge
    s.line(P((200, 0, BENCH)), P((200, 0, RIM + 60)), "#999", 14, op=0.6)
    s.circle(P(HINGE), 7, color=S.INK, fill="#fff", w=2)
    s.text((P(HINGE)[0] - 60, P(HINGE)[1] - 40), "hinge || Y (theirs: x 200, rim+60), pins in slots", S.INK, 10)
    s.line(P((300, 0, RIM + 55)), P((200, 0, RIM + 20)), "#999", 4, op=0.6)
    # closed gun
    pose = (45, 30, -15)
    S.gun_2d(s, lambda q: P(q), pose, op=0.35)
    # parked gun at 80 deg
    for name, (a, b, rad) in CAPSULES.items():
        pa = rot_y(world(a, pose), 80)
        pb = rot_y(world(b, pose), 80)
        s.line(P(pa), P(pb), S.GUN, 2 * rad, op=0.10, cap="round")
    s.text(P(rot_y(world((0, 247), pose), 80) + np.array([10, 0, 30])), "parked at 80 deg (their over-centre)", S.GUN, 10)
    dot = world(FEATURES['dot'], pose)
    s.circle(P(dot), 4, color="#d00", fill="#d00")
    # lid frame: cantilever from hinge to the recipe stack near body back, tail to rear ball
    bb = world(FEATURES['body_back'], pose)
    stack = np.array([bb[0] + 40, 0, bb[2] - 60])
    s.line(P(HINGE), P(stack), "#335", 6, op=0.6)
    s.line(P(HINGE), P((300, 0, RIM + 76)), "#335", 6, op=0.6)
    s.line(P(np.array([170, 0, RIM + 95])), P((170, 0, RIM + 76)), "#335", 5, op=0.6)
    s.text(P((60, 0, RIM + 110)), "lid arm to front pair", "#335", 10)
    # recipe stack boxes
    labels = ["X slide (radial, per recipe)", "Y slide = yaw, 1.08 mm/deg", "recipe block (roll, hole)"]
    for i, lab in enumerate(labels):
        c = stack + np.array([-i * 18, 0, -i * 18])
        s.poly([P(c + np.array([-14, 0, -8])), P(c + np.array([14, 0, -8])), P(c + np.array([14, 0, 8])), P(c + np.array([-14, 0, 8]))], color="#8d6e00", fill="#ffd54f", op=0.9)
    s.text(P(stack + np.array([25, 0, 30])), "stack on the lid, outermost first:", "#8d6e00", 10)
    for i, lab in enumerate(labels):
        s.text(P(stack + np.array([25, 0, 16 - 13 * i])), f"{i+1}. {lab}", "#8d6e00", 10)
    # seat behind the station
    for bx, lab in ((170, "front pair y=+/-110, outside base"), (300, "rear ball (tail)")):
        p = np.array([bx, 0, RIM + 70])
        a = P(p)
        s.poly([(a[0] - 11, a[1] - 6), (a[0], a[1] + 5), (a[0] + 11, a[1] - 6), (a[0] + 11, a[1] + 10), (a[0] - 11, a[1] + 10)], color="#704", fill="#e7c")
        s.circle((a[0], a[1] - 3), 5, color=S.INK, fill="#666")
        s.line((a[0], a[1] + 10), P((bx, 0, BENCH)) if bx < 200 else P((bx, 0, RIM + 55)), "#999", 4, op=0.6)
        s.text((a[0] - 30, a[1] + 22), lab, "#704", 10)
    s.arrow(P((300, 0, RIM + 40)), P((300, 0, RIM + 62)), "#704")
    s.text(P((310, 0, RIM + 36)), "latch at the rear ball: >= 40 N", "#704", 10)
    # notes / phase allocation
    notes = ["Who owns each freedom, by phase",
             "",
             "load, indicate, plate, invert:",
             "  hinge (lid parked); per-tube Z set",
             "  on the work's 3 screws in phase 2",
             "tacks: lid seated + H2 (or hand)",
             "dry run, weld, stuck wire:",
             "  seat + latch (location), rotator (spin)",
             "  X, yaw (Y slide), recipe block: locked",
             "gun away: hinge",
             "",
             "Per recipe: block, X, Y(yaw) on the lid",
             "Per tube:   work Z (rim back to nominal)",
             "Per snip:   stickout (their K3)",
             "",
             "Checked with their proxy + hinge at the",
             "true opening pose (hole dial 30):",
             " every feasible recipe pose escapes",
             "   (grip 30-60, hole dial 15-45, yaw",
             "   -30..+5 by rotation); yaw by Y slide",
             "   escapes -25..+5, near miss at -30",
             " tube +/-3.2 mm escapes if Z is taken",
             "   by the work or the lid; untaken +3.2",
             "   puts the wire into the plate",
             "",
             "Seat behind the station, all posts on",
             "the subplate outside the rotator base:",
             "front pair x=170, rear ball x=300.",
             "CG at (-30, -108) is 200 mm outside",
             "the front pair: latch at the rear ball",
             ">= 33 N, + 7 N for a 5 N cable tug",
             "(lid+gun 2.2 kg, their estimate);",
             "their 60 N latch gives ~1.5x."]
    for i, l in enumerate(notes):
        s.text((1250, 50 + 16 * i), l, S.INK if i == 0 else S.NOTE, 11, bold=(i == 0))
    s.save("w2-lid-reallocated.svg")


if __name__ == "__main__":
    draw()
    print("wrote sketches/w2-lid-reallocated.svg")
