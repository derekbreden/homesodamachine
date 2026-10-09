"""Sketch: arrangement B, gun carriage = XYZ stages + a hole-axis arc + a grip-axis yoke.

The arc lies in the plane x = +40 mm (outboard of the dot), centred on the
radial line through the dot, so moving along it rotates the gun about the hole
axis. The yoke carries two bearings on the grip axis (dot -> grip base line):
a ring around the cable exit and a small stub bearing ahead of the grip.
Everything but the gun proxy is this explorer's proposal.
"""
import math
from svgkit import Svg, draw_gun, draw_tube_side, draw_tube_front, R_IN

OUT = "../sketches/"
BENCH = -232.0
ARC_X = 40.0
ARC_R = 285.0
E_NOM = 31.0
GB = (-62.6, -233.5, 139.6)
STUB = (-33.1, -123.7, 73.9)
CAM = (-45.0, 70.0, 85.0)


def side():
    s = Svg(1000, 700, -260, 640, -250, 470,
            "B  gun carriage with two rotations about the dot: side view (looking from outside the tube)",
            notes=["Plan angle is not a joint: turning the gun about the vertical line through the dot is exactly a sideways (Y) move",
                   "of about R*angle (16 mm for 15 deg) because the joint is a circle. So: X, Y, Z stages + hole-axis arc + grip-axis roll.",
                   "Each axis: dual-shaft NEMA17, hand knob on the back shaft, closed-loop board that still reads the knob when the motor is off."])
    s.rect(-260, BENCH - 10, 640, BENCH, fill="#caa472", stroke="#7a5a2a")
    # rotator + tube as today
    s.rect(-180, BENCH, 120, BENCH + 36, fill="#e8d9b5", stroke="#865")
    s.rect(-178, BENCH + 36, -110, BENCH + 154, fill="#e8d9b5", stroke="#865")
    s.rect(-75, BENCH + 36, 75, BENCH + 84, fill="#efe4c8", stroke="#865")
    s.text((-70, BENCH + 60), "existing rotator (theta), on the bench as today", size=9)
    draw_tube_side(s)
    # arc: in this projection, a circle arc about the dot
    s.arc((0, 0), ARC_R - 14, 4, 60, stroke="#6a4", sw=2)
    s.arc((0, 0), ARC_R + 14, 4, 60, stroke="#6a4", sw=2)
    s.arc((0, 0), ARC_R, 4, 60, stroke="#6a4", sw=1, dash="6,4")
    s.text((ARC_R * math.cos(math.radians(62)) - 10, ARC_R * math.sin(math.radians(62)) + 12),
           "hole-axis arc, R ~285, centred on the radial line through the dot", size=10, anchor="middle", color="#361")
    # arc carriage at E_NOM
    ca = (ARC_R * math.cos(math.radians(E_NOM)), ARC_R * math.sin(math.radians(E_NOM)))
    s.poly([(ca[0] - 22, ca[1] - 20), (ca[0] + 22, ca[1] - 20), (ca[0] + 22, ca[1] + 20), (ca[0] - 22, ca[1] + 20)],
           fill="#b8d8a0", stroke="#361")
    # yoke from carriage to ring (at grip base) and stub
    gb = (-GB[1], GB[2])
    st = (-STUB[1], STUB[2])
    s.polyline([ca, (gb[0] + 15, gb[1] + 25), gb], stroke="#963", sw=4)
    s.polyline([(gb[0] + 15, gb[1] + 25), (st[0] + 10, st[1] + 45), st], stroke="#963", sw=3)
    draw_gun(s, "side")
    s.circle(gb, 16, stroke="#963", sw=3)
    s.circle(st, 6, stroke="#963", sw=3)
    s.line((0, 0), (gb[0] * 1.35, gb[1] * 1.35), stroke="#963", dash="2,3")
    s.text((gb[0] * 1.35 + 4, gb[1] * 1.35), "grip axis", size=10, color="#963")
    s.text((gb[0] + 20, gb[1] - 26), "ring bearing around the cable exit", size=10, color="#963")
    s.text((st[0] + 12, st[1] - 16), "stub bearing ahead of the grip", size=10, color="#963")
    s.dot((0, 0), 4)
    # umbilical: along -Y then down
    far = (gb[0] + 120, gb[1] + 15)
    s.line(gb, far, stroke="#222", sw=5)
    s.arc((far[0], far[1] - 380), 380, 90, 45, stroke="#222", sw=5)
    s.text((far[0] + 10, far[1] + 12), "umbilical free to roll in the ring; hanger saddle is a swivel", size=10)
    # XYZ stack and column at -Y side
    col_h = 520
    s.rect(560, BENCH, 600, BENCH + 20 + col_h, fill="#bbb", stroke="#555")
    s.rect(520, 250, 560, 390, fill="#c9d6c9", stroke="#353")
    s.text((515, 395), "Z", size=12)
    s.rect(420, 330, 520, 370, fill="#c9d6c9", stroke="#353")
    s.text((425, 375), "X (into page)", size=10)
    s.rect(300, 345, 420, 370, fill="#c9d6c9", stroke="#353")
    s.text((305, 375), "Y (tangent)", size=10)
    s.polyline([(320, 345), (320, ARC_R * math.sin(math.radians(55)) + 20), (ARC_R * math.cos(math.radians(40)) + 18, ARC_R * math.sin(math.radians(40)) + 12)],
               stroke="#555", sw=4)
    s.text((330, 300), "arc track hangs from the Y carriage", size=10)
    s.text((565, BENCH + 30 + col_h), "4040 column", size=10)
    cam = (-CAM[1], CAM[2])
    s.rect(cam[0] - 12, cam[1] - 8, cam[0] + 12, cam[1] + 8, fill="#333", stroke="#000")
    s.line(cam, (0, 0), stroke="#b00", dash="3,3")
    s.text((cam[0] - 16, cam[1] + 18), "joint camera (rides the Y carriage or stays on the frame)", size=10, anchor="start")
    s.save(OUT + "b-rcm-carriage-side.svg")


def front():
    s = Svg(820, 640, -300, 220, -250, 420,
            "B  gun carriage: front view (looking along the tangent)",
            notes=["The arc track stands in the plane x = +40 mm, outboard of the dot and clear of the tube; the yoke reaches inboard to the gun.",
                   "Rolling about the grip axis keeps the dot and the cable exit still; tilting on the arc keeps the dot still and swings the cable exit."])
    s.rect(-300, BENCH - 10, 220, BENCH, fill="#caa472", stroke="#7a5a2a")
    tube_axis = -R_IN
    s.rect(tube_axis - 125, BENCH, tube_axis + 125, BENCH + 36, fill="#e8d9b5", stroke="#865")
    draw_tube_front(s)
    s.line((tube_axis, -150), (tube_axis, 40), dash="8,4", stroke="#777")
    s.rect(ARC_X - 6, 30, ARC_X + 6, 250, fill="#b8d8a0", stroke="#361")
    s.text((ARC_X + 10, 240), "arc track (edge-on)", size=10, color="#361")
    ca_z = ARC_R * math.sin(math.radians(E_NOM))
    s.polyline([(ARC_X, ca_z), (GB[0] + 10, GB[2] + 25), (GB[0], GB[2])], stroke="#963", sw=4)
    s.polyline([(GB[0] + 10, GB[2] + 25), (STUB[0] + 25, STUB[2] + 40), (STUB[0], STUB[2])], stroke="#963", sw=3)
    draw_gun(s, "front")
    s.circle((GB[0], GB[2]), 16, stroke="#963", sw=3)
    s.circle((STUB[0], STUB[2]), 6, stroke="#963", sw=3)
    s.dot((0, 0), 4)
    s.text((6, -14), "dot", size=10, color="#b00")
    s.line((ARC_X + 30, 0), (-80, 0), stroke="#6a4", dash="6,3")
    s.text((ARC_X + 34, -4), "hole axis (through the dot)", size=10, color="#361")
    s.save(OUT + "b-rcm-carriage-front.svg")


if __name__ == "__main__":
    side()
    front()
