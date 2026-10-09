"""Sketch: idea F, the wire path as the organising element (side view along the radial line,
tangent left-right, gun toward the right). Gun and wire direction = scene proxy at the
opening pose; feeder, straightener, trough and cameras are proposals, positions schematic."""
import math
from svgkit import Svg, draw_gun, draw_tube_side

OUT = "../sketches/"
GUIDE_BACK = (75.8, 64.9)      # side-view (-y, z) of the scene's wire-guide back
W = (0.715, 0.612)             # wire direction in side view (dot -> guide), from calc/wire_path.py


def side():
    s = Svg(1000, 600, -220, 760, -170, 330,
            "F  the wire path as the spine: fixed feeder, one-bend conduit in a trough, wire camera, finger on the jog button",
            notes=["Every sensor here is optical or mechanical with respect to the welder. Nothing connects to the clip lead, ground terminal,",
                   "feeder connector, feeder buttons' contacts, RS232/DB25, or the wire's electrical path. The finger presses the feeder's own button.",
                   "Touch-off: the stage (not the feeder) closes on the cap at 0.1-0.5 mm/s; the wire camera sees 1 px of stick-out bend (~0.13 N) and stops."])
    s.rect(-220, -170, 760, -160, fill="#caa472", stroke="#7a5a2a")
    draw_tube_side(s)
    draw_gun(s, "side")
    s.dot((0, 0), 4)
    s.text((-40, -16), "dot", size=10, color="#b00")
    # wire: stick-out from the dot back to the guide, then conduit
    s.line((0, 0), GUIDE_BACK, stroke="#c60", sw=2)
    p1 = (GUIDE_BACK[0] + 110 * W[0] / math.hypot(*W), GUIDE_BACK[1] + 110 * W[1] / math.hypot(*W))
    s.line(GUIDE_BACK, p1, stroke="#c60", sw=5)
    # one bend to horizontal, R ~150 (schematic)
    s.arc((p1[0] + 95, p1[1] - 112), 147, 130, 90, stroke="#c60", sw=5)
    bend_end = (p1[0] + 95, p1[1] - 112 + 147)
    s.line(bend_end, (560, bend_end[1]), stroke="#c60", sw=5)
    s.rect(160, bend_end[1] - 14, 560, bend_end[1] - 8, fill="#f2c26b", stroke="#963")
    s.text((250, bend_end[1] - 28), "printed trough: conduit held along its whole length (one ~50 deg bend)", size=9)
    s.rect(560, bend_end[1] - 12, 620, bend_end[1] + 12, fill="#ccd", stroke="#335")
    s.text((545, bend_end[1] + 22), "straightener rollers", size=9)
    s.rect(620, bend_end[1] - 70, 740, bend_end[1] + 50, fill="#ddd", stroke="#333")
    s.circle((690, bend_end[1] - 10), 45, stroke="#555")
    s.text((740, bend_end[1] - 84), "wire feeder (fixed, on the module)", size=9, anchor="end")
    s.rect(700, bend_end[1] + 50, 720, bend_end[1] + 70, fill="#963", stroke="#000")
    s.text((695, bend_end[1] + 62), "servo finger on the Feed / Retract buttons", size=9, anchor="end")
    # wire camera near the bracket
    s.rect(28, 30, 52, 44, fill="#333", stroke="#000")
    s.line((40, 30), (4, 3), stroke="#b00", dash="2,2")
    s.text((-120, 60), "wire camera (5.5 mm endoscope) on the shell", size=9)
    s.line((-2, 54), (28, 38), stroke="#888", sw=0.7)
    # joint camera
    s.rect(-82, 77, -58, 93, fill="#333", stroke="#000")
    s.line((-70, 85), (0, 0), stroke="#b00", dash="3,3")
    s.text((-210, 100), "joint camera (+Y, inboard)", size=9)
    # welder boundary
    s.rect(420, -150, 740, -60, fill="none", stroke="#c00", dash="6,4", sw=1.5)
    s.text((428, -75), "welder's own circuits - nothing connects:", size=10, color="#a00")
    s.text((428, -92), "clip lead + ground terminal, gun-to-work contact,", size=9, color="#a00")
    s.text((428, -107), "feeder 6-pin connector, RS232 / DB25, key switch", size=9, color="#a00")
    s.text((428, -125), "(the camera may read the unit's screen/LEDs)", size=9, color="#a00")
    s.text((70, 18), "stick-out (camera-gauged)", size=9, color="#a40")
    s.save(OUT + "f-wire-path-side.svg")


if __name__ == "__main__":
    side()
