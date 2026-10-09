"""Sketch for ideas/gravity-in-the-gun-plane.md: view from +X of the tilted station at
tau* = 32.5 deg (room frame, origin at the dot). The gun lies flat in this plane.
Gun = capsule proxy; cup, hanger, wire, fork, rings, anchor are schematic.
Run: tools/cad-venv/bin/python gravity_plane_sketch.py
"""
import math
import numpy as np
import sketches as S
from geometry import world, CAPSULES, FEATURES, R_IN, RIM, CAP_TOP
from tilt_calcs import Ry, RECIPE, DOT

R = Ry(32.5)


def room(p):
    return R @ (np.asarray(p, float) - DOT)


def main():
    S.SCALE = 1.0
    W, H = 1400, 820
    s = S.Svg(W, H, "Gravity in the gun's plane: tilted 32.5 deg, nose in the work's cup, one hanging wire (view from +X, schematic)")
    ox, oy = 640, 700

    def P(q):
        return (ox + S.SCALE * q[1], oy - S.SCALE * q[2])
    # tilted rim and plate edge
    rim = [P(room((R_IN * math.cos(t), R_IN * math.sin(t), RIM))) for t in np.linspace(0, 2 * math.pi, 90)]
    s.poly(rim, color=S.WORK, w=1.2)
    s.text(P(room((0, R_IN, RIM))) + np.array([-40, 60]), "tilted rim (station = low point)", S.WORK, 10)
    # gun
    for name, (a, b, rad) in CAPSULES.items():
        s.line(P(room(world(a, RECIPE))), P(room(world(b, RECIPE))), S.GUN, 2 * rad * S.SCALE, op=0.32, cap="round")
    s.circle(P((0, 0, 0)), 4, color="#d00", fill="#d00")
    # cup centred on the dot around the nose (46 mm up the barrel), on the plate hanger
    nose = room(world((0.0, 30.0), RECIPE))
    s.arc(P((0, 0, 0)), 46 * S.SCALE, 60, 125, color="#7b1fa2", w=5)
    s.text((P(nose)[0] + 90, P(nose)[1] + 20), "sprung cup, pads on a sphere centred on the dot", "#7b1fa2", 10)
    s.text((P(nose)[0] + 90, P(nose)[1] + 34), "(work-as-datum H1-p / carry-and-locate E-RA), on the", "#7b1fa2", 10)
    s.text((P(nose)[0] + 90, P(nose)[1] + 48), "plate hanger riding the plate: the dot follows the work", "#7b1fa2", 10)
    # base loop + rings on the grip axis
    gb = room(world(FEATURES['grip_base_QBH'], RECIPE))
    g = gb / np.linalg.norm(gb)
    s.circle(P(gb), 11 * S.SCALE, color=S.MECH, w=3)
    ringA = 100 * g
    s.circle(P(ringA), 9 * S.SCALE, color=S.MECH, w=2, dash="4,3")
    s.line(P((0, 0, 0)), P(gb + 40 * g), S.NOTE, 1, dash="5,4")
    s.text(P(gb + np.array([0, -150, -30])), "Derek's base loop on the grip axis (roll journal)", S.MECH, 10)
    s.text(P(ringA + np.array([0, -230, -10])), "ring A (roll journal, friction lock)", S.MECH, 10)
    # hole wire straight up to a lead-screw anchor
    top = gb + np.array([0, 0, 380])
    s.line(P(gb), P(top), S.INK, 1.6)
    s.poly([P(top + np.array([0, -18, 0])), P(top + np.array([0, 18, 0])), P(top + np.array([0, 18, 26])), P(top + np.array([0, -18, 26]))], color=S.INK, fill="#ddd")
    s.text(P(top + np.array([0, 24, 18])), "hole knob: Tr8x2 lead-screw anchor (one-knob's W_hole)", S.INK, 10)
    s.text(P(top + np.array([0, 24, 4])), "vertical wire, tensioned by gravity alone", S.INK, 10)
    # ballast hanging from the loop
    bal = gb + np.array([0, 0, -70])
    s.line(P(gb), P(bal), S.INK, 1)
    s.poly([P(bal + np.array([0, -12, 0])), P(bal + np.array([0, 12, 0])), P(bal + np.array([0, 12, -28])), P(bal + np.array([0, -12, -28]))], color=S.INK, fill="#777")
    s.text(P(bal + np.array([0, 16, -18])), "1 kg ballast: wire preload only", S.INK, 10)
    # yaw fork: vertical slot (seen face-on as a vertical bar just beside the loop)
    s.poly([P(gb + np.array([0, 16, -45])), P(gb + np.array([0, 24, -45])), P(gb + np.array([0, 24, 60])), P(gb + np.array([0, 16, 60]))], color="#8d6e00", fill="#ffd54f", op=0.8)
    s.text(P(gb + np.array([0, 28, 50])), "yaw fork: vertical slot, X constraint", "#8d6e00", 10)
    # umbilical leaving vertically from the loop's clamp
    pts = [gb + np.array([0, -6, 0]) + np.array([0, -60 * math.sin(t), 300 * (1 - math.cos(t))]) for t in np.linspace(0, math.pi / 2, 12)]
    s.poly([P(q) for q in pts], color=S.CABLE, w=3, closed=False)
    s.text(P(pts[-1] + np.array([0, -200, -60])), "umbilical free loop leaves the clamp", S.CABLE, 10)
    s.text(P(pts[-1] + np.array([0, -200, -74])), "vertically (acts like +/- ballast)", S.CABLE, 10)
    # escape arrow
    s.arrow(P((0, 30, 60)), P((0, 30, 130)), "#d00")
    s.text(P((0, 36, 100)), "lift = escape direction (vertical here):", "#d00", 10)
    s.text(P((0, 36, 86)), "cup lets go, wire slackens, pin rides up the slot", "#d00", 10)
    notes = ["At tau* (1.5 kg proxy gun):",
             " gravity torque: hole 1.30 N*m, grip 0.13 N*m (0.77 upright),",
             "   vertical 0 (always); grip torque crosses zero near tau 38 deg",
             " wire at the grip base: 6.8 N from gravity; 16.6 N with 1 kg",
             "   ballast (11.6 N if the cable pulls up 5 N); cup ~8 N up",
             " each support is one knob (one-knob's plane rule):",
             "   wire meets the grip axis and is parallel to the vertical",
             "   fork line meets the grip axis and is parallel to the hole axis",
             "   rings concentric with the grip axis"]
    for i, l in enumerate(notes):
        s.text((900, 60 + 16 * i), l, S.INK if i == 0 else S.NOTE, 11, bold=(i == 0))
    s.save("s7-gravity-in-the-gun-plane.svg")


if __name__ == "__main__":
    main()
    print("wrote sketches/s7-gravity-in-the-gun-plane.svg")
