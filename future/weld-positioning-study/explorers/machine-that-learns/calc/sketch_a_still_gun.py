"""Sketch: arrangement A, the gun bolted still and the tube doing the moving.

Gun silhouette = scene proxy at the opening pose (45, 30, -15). Stage heights,
bridge position and camera position are this explorer's proposals.
"""
from svgkit import Svg, draw_gun, draw_tube_side, draw_tube_front, R_IN

OUT = "../sketches/"
DOT_Z_ABOVE_BENCH = 400.0          # proposal: stage stack raises the dot from 232 to ~400 mm
BENCH = -DOT_Z_ABOVE_BENCH
BASE_BOTTOM = -208.05              # rotator base bottom (repo: rim 214.4 above base bottom)
FEET = BASE_BOTTOM - 24.0
ADAPTER = FEET - 10.0
XSTAGE_BOT = ADAPTER - 65.0        # assumed height of an SFU1605 double-rail stage
ZBED_BOT = XSTAGE_BOT - 15.0
FRAME_TOP = BENCH + 20.0
CROSSBAR_Z = 270.0
CAM = (-45.0, 70.0, 85.0)
GRIP_BASE = (-62.6, -233.5, 139.6)


def label(s, p, txt, to=None, size=10, color="#111", anchor="start"):
    if to:
        s.line(p, to, stroke="#888", sw=0.7)
    s.text(p, txt, size=size, color=color, anchor=anchor, dy=-2)


def side():
    s = Svg(1000, 760, -300, 560, -420, 330,
            "A  still gun, moving tube: side view (looking at the dot from outside the tube; tangent runs left-right)",
            notes=["Fixed to the frame: gun (kinematic seat on a printed pose block), joint camera, umbilical saddle.",
                   "Moving: the tube, by X (radial, first new motor), Z (bed) and theta (existing rotator). Gun = scene proxy at 45/30/-15.",
                   "Dot ~400 mm above the bench here (proposal): 232 mm today plus ~170 mm of stage stack."])
    s.rect(-300, BENCH - 10, 560, BENCH, fill="#caa472", stroke="#7a5a2a")
    s.rect(-250, BENCH, 380, FRAME_TOP, fill="#bbb", stroke="#555")
    label(s, (400, FRAME_TOP + 30), "2040 frame: one datum for", (360, FRAME_TOP + 10))
    s.text((400, FRAME_TOP + 16), "tube stack and gun bridge", size=10, dy=-2)
    for yh in (-150, 110):
        s.rect(yh - 4, FRAME_TOP, yh + 4, ZBED_BOT, fill="#999", stroke="#444")
    s.rect(-200, ZBED_BOT, 150, XSTAGE_BOT, fill="#d9d9d9", stroke="#444")
    s.line((175, ZBED_BOT - 25), (175, ZBED_BOT + 25), arrow=True)
    s.text((181, ZBED_BOT - 5), "Z", size=12)
    label(s, (400, ZBED_BOT - 5), "Z bed on 3 belt-linked T8 screws", (150, ZBED_BOT + 7))
    s.rect(-135, XSTAGE_BOT, 135, ADAPTER, fill="#c9d6c9", stroke="#353")
    s.circle((150, (XSTAGE_BOT + ADAPTER) / 2), 7)
    s.dot((150, (XSTAGE_BOT + ADAPTER) / 2), 2, "#333")
    s.text((160, (XSTAGE_BOT + ADAPTER) / 2 + 12), "X", size=12)
    label(s, (400, XSTAGE_BOT + 40), "X stage, SFU1605 (radial, into page)", (135, XSTAGE_BOT + 40))
    s.rect(-185, ADAPTER, 125, FEET, fill="#e6e6e6", stroke="#555")
    for yh in (-175, -110, 60, 115):
        s.rect(yh, FEET, yh + 10, BASE_BOTTOM, fill="#aaa", stroke="#555", sw=0.6)
    s.rect(-180, BASE_BOTTOM, 120, BASE_BOTTOM + 12, fill="#e8d9b5", stroke="#865")
    s.rect(-178, BASE_BOTTOM + 12, -110, BASE_BOTTOM + 130, fill="#e8d9b5", stroke="#865")
    s.text((-176, BASE_BOTTOM + 118), "motor", size=9)
    s.text((-176, BASE_BOTTOM + 107), "tower", size=9)
    s.rect(96, BASE_BOTTOM + 12, 118, BASE_BOTTOM + 91, fill="#e8d9b5", stroke="#865")
    s.rect(-75, BASE_BOTTOM + 12, 75, BASE_BOTTOM + 60, fill="#efe4c8", stroke="#865")
    label(s, (400, BASE_BOTTOM + 30), "existing rotator, unchanged (theta)", (120, BASE_BOTTOM + 30))
    label(s, (400, BASE_BOTTOM + 90), "ground shoe tower", (118, BASE_BOTTOM + 85))
    draw_tube_side(s)
    label(s, (400, -60), "tube + recessed endcap", (63.5, -60))
    for yh in (-210, 330):
        s.rect(yh - 20, FRAME_TOP, yh + 20, CROSSBAR_Z + 20, fill="#ccc", stroke="#555")
    s.rect(-230, CROSSBAR_Z, 350, CROSSBAR_Z + 40, fill="#bbb", stroke="#555")
    s.text((-220, CROSSBAR_Z + 26), "gun bridge: 4040 portal on the same frame", size=10)
    s.poly([(95, CROSSBAR_Z), (111, CROSSBAR_Z), (108, 175), (98, 175)], fill="#f2c26b", stroke="#963")
    label(s, (400, 240), "printed pose block (one per nominal pose)", (111, 240))
    label(s, (400, 190), "kinematic seat on the shell (3 balls / 3 grooves)", (110, 175))
    draw_gun(s, "side")
    s.dot((0, 0), 4)
    s.text((6, -14), "dot", size=10, color="#b00")
    gb = (-GRIP_BASE[1], GRIP_BASE[2])
    far = (gb[0] + 110, gb[1] + 14)
    s.line(gb, far, stroke="#222", sw=5)
    s.arc((far[0], far[1] - 350), 350, 90, 30, stroke="#222", sw=5)
    s.rect(far[0] - 6, far[1] - 10, far[0] + 6, far[1] + 10, fill="#f2c26b", stroke="#963")
    label(s, (400, 130), "swivel saddle: umbilical + conduit, R >= 350 mm", (far[0], far[1]))
    s.polyline([(77.5, 85.6), (150, 110), gb], stroke="#c60", sw=2)
    label(s, (400, 60), "wire conduit to bracket under barrel", (150, 105), color="#a40")
    cam = (-CAM[1], CAM[2])
    s.rect(cam[0] - 12, cam[1] - 8, cam[0] + 12, cam[1] + 8, fill="#333", stroke="#000")
    s.line(cam, (0, 0), stroke="#b00", dash="3,3")
    s.line(cam, (-CAM[1], CROSSBAR_Z), stroke="#555", sw=2)
    s.text((cam[0] - 16, cam[1] + 18), "joint camera", size=10, anchor="end")
    s.save(OUT + "a-still-gun-side.svg")


def front():
    s = Svg(900, 720, -360, 330, -420, 330,
            "A  still gun, moving tube: front view (looking along the tangent; gun comes toward you)",
            notes=["Tube change: Z down ~10 mm, X toward -X ~100 mm (the +X wall passes ~5 mm under the nozzle tip),",
                   "lift the tube out by hand, drop the next one in, return; the camera re-finds the corner before anything else.",
                   "Bridge posts stand in front of and behind this view (dashed)."])
    s.rect(-360, BENCH - 10, 330, BENCH, fill="#caa472", stroke="#7a5a2a")
    s.rect(-320, BENCH, 190, FRAME_TOP, fill="#bbb", stroke="#555")
    s.rect(-250, ZBED_BOT, 120, XSTAGE_BOT, fill="#d9d9d9", stroke="#444")
    s.rect(-240, XSTAGE_BOT, 110, ADAPTER, fill="#c9d6c9", stroke="#353")
    s.line((-60, XSTAGE_BOT + 30), (30, XSTAGE_BOT + 30), arrow=True)
    s.line((-60, XSTAGE_BOT + 30), (-150, XSTAGE_BOT + 30), arrow=True)
    s.text((-60, XSTAGE_BOT + 38), "X", size=12, anchor="middle")
    tube_axis = -R_IN
    s.rect(tube_axis - 125, ADAPTER, tube_axis + 125, FEET, fill="#e6e6e6", stroke="#555")
    s.rect(tube_axis - 125, BASE_BOTTOM, tube_axis + 125, BASE_BOTTOM + 12, fill="#e8d9b5", stroke="#865")
    s.rect(tube_axis - 70, BASE_BOTTOM + 12, tube_axis + 70, BASE_BOTTOM + 60, fill="#efe4c8", stroke="#865")
    draw_tube_front(s)
    s.line((tube_axis, -170), (tube_axis, 60), dash="8,4", stroke="#777")
    s.text((tube_axis + 4, 45), "tube axis", size=9)
    s.rect(-60, FRAME_TOP, -20, CROSSBAR_Z + 40, fill="none", stroke="#777", dash="5,4")
    s.rect(-60, CROSSBAR_Z, -20, CROSSBAR_Z + 40, fill="#999", stroke="#555")
    s.poly([(-45, CROSSBAR_Z), (-35, CROSSBAR_Z), (-62, 175), (-75, 175)], fill="#f2c26b", stroke="#963")
    draw_gun(s, "front")
    s.dot((0, 0), 4)
    label(s, (60, -40), "dot at the inside corner", (2, -2), color="#b00")
    s.rect(CAM[0] - 10, CAM[2] - 8, CAM[0] + 10, CAM[2] + 8, fill="#333", stroke="#000")
    s.line((CAM[0], CAM[2]), (0, 0), stroke="#b00", dash="3,3")
    label(s, (60, 110), "joint camera (on the +Y side, beyond the gun)", (CAM[0] + 10, CAM[2]))
    label(s, (60, BASE_BOTTOM + 40), "existing rotator", (tube_axis + 125, BASE_BOTTOM + 12))
    label(s, (60, XSTAGE_BOT + 50), "X stage (radial)", (110, XSTAGE_BOT + 40))
    label(s, (60, ZBED_BOT + 30), "Z bed", (120, ZBED_BOT + 8))
    s.save(OUT + "a-still-gun-front.svg")


if __name__ == "__main__":
    side()
    front()
