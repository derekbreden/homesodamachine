"""Sketch: idea E, Derek's table opening as a motorised, observed station.
Builds on workspace-as-structure's table-opening gantry and drop-in collar (their
dimensions: opening D150-160, Y rails either side of the opening, X beam at y ~ -190 under the
gun body, four-post shelf with belt-linked Tr8x2 screws, side loading by ~70 mm drop).
Gun = scene proxy at the opening pose (dial values). Rim flush with the table top.
"""
import math
from svgkit import Svg, draw_gun, R_IN

OUT = "../sketches/"
TOP = 6.35          # table top relative to the dot (rim flush)
COLLAR = TOP + 12.7
TA = -R_IN          # tube axis x relative to the dot
GB = (-62.6, -233.5, 139.6)


def plan():
    s = Svg(900, 760, -1000, 420, -700, 820,
            "E  table-opening station: plan (bench long axis along Y; operator at the front, -X)",
            notes=["Gantry after workspace-as-structure: Y rails either side of the opening, X beam at y ~ -190 under the gun body, on a drop-in collar.",
                   "Added here: stylus at the dot's angle (+X gap), joint camera on the collar (+Y, inboard), two PTZ cameras (front across the bore; +Y end),",
                   "fiducial tags on the collar so every PTZ frame is registered to the collar; cable clamped to the X carriage, then a >=350 mm saddle at the -Y end."])
    s.rect(-300, -690, 400, 810, fill="#e8d2a8", stroke="#a07a40")          # bench top (depth along X)
    s.text((-290, 790), "bench top (wood); front edge at -X", size=10)
    s.rect(TA - 250, -460, TA + 250, 260, fill="#dfe3e8", stroke="#556")      # collar
    s.text((TA - 245, 245), "drop-in collar (workspace-as-structure)", size=10)
    s.circle((TA, 0), 80, fill="#fff", stroke="#333", sw=1.5)
    s.circle((TA, 0), 63.5, stroke="#555", sw=2)
    s.text((TA - 30, -95), "opening D160", size=9)
    for xr in (TA - 205, TA + 205):
        s.rect(xr - 6, -440, xr + 6, 240, fill="#9aa", stroke="#344")
    s.text((TA + 212, 200), "Y rail", size=10)
    s.rect(TA - 215, -200, TA + 215, -180, fill="#8a9", stroke="#243")
    s.text((TA - 245, -250), "X beam (gantry), rides the Y rails", size=10)
    s.rect(-120, -215, -40, -165, fill="#b8d8a0", stroke="#361")
    s.text((-35, -250), "X carriage + roll/tilt head", size=9)
    draw_gun(s, "plan")
    s.dot((0, 0), 4)
    # stylus at +X in the gap
    s.circle((6, 0), 3, fill="#fff", stroke="#000")
    s.line((9, 0), (60, 0), stroke="#333", sw=2)
    s.rect(60, -12, 120, 12, fill="#c9d6c9", stroke="#353")
    s.text((125, -4), "stylus + scale", size=10)
    # cameras
    for (cx, cy, lab) in ((-45, 70, "joint camera"), (-800, 0, "PTZ 1 (front, high, over the operator)"), (-230, 700, "PTZ 2 (+Y end, high)")):
        s.rect(cx - 14, cy - 10, cx + 14, cy + 10, fill="#333", stroke="#000")
        s.line((cx, cy), (0, 0), stroke="#b00", dash="3,4")
        s.text((cx + 18, cy + 4), lab, size=10)
    for (fx, fy) in ((TA - 130, 120), (TA + 110, 120), (TA - 130, -130), (TA + 120, -120)):
        s.rect(fx - 12, fy - 12, fx + 12, fy + 12, fill="#000", stroke="#000")
    s.text((TA - 140, 150), "tags", size=9)
    # cable
    clamp = (GB[0], -320)
    s.line((GB[0], GB[1]), clamp, stroke="#222", sw=5)
    s.line(clamp, (GB[0], -680), stroke="#222", sw=5)
    s.rect(GB[0] - 10, -330, GB[0] + 10, -310, fill="#f2c26b", stroke="#963")
    s.text((GB[0] + 14, -330), "cable clamp on the X carriage", size=9)
    s.text((GB[0] + 14, -660), "to the -Y bench end: R>=350 saddle, then the cart", size=9)
    s.line((-420, 0), (-320, 0), stroke="#333", sw=1, arrow=True)
    s.text((-560, 40), "operator (box opens toward -X)", size=10)
    s.save(OUT + "e-table-station-plan.svg")


def side():
    s = Svg(1000, 640, -300, 700, -360, 300,
            "E  table-opening station: section along the tangent (looking from +X; gun toward the right)",
            notes=["Above the collar: Y rails, X beam and carriage (gun side: X, Y, roll, tilt). Below: four posts, a shelf on four belt-linked Tr8x2 screws, one motor (work side: Z).",
                   "WELD height is set per tube from the work (camera triangulation or a centre plunger); LOAD drops the shelf ~70 mm so the tube slides out the front.",
                   "Stylus reaches down the gap between tube OD and the opening, touching the OD at the dot's angle 9 mm below the joint; it lifts clear before LOAD."])
    s.rect(-300, TOP - 30, -80, TOP, fill="#e8d2a8", stroke="#a07a40")
    s.rect(80, TOP - 30, 700, TOP, fill="#e8d2a8", stroke="#a07a40")
    s.rect(-260, TOP, -80, COLLAR, fill="#dfe3e8", stroke="#556")
    s.rect(80, TOP, 460, COLLAR, fill="#dfe3e8", stroke="#556")
    s.text((90, TOP - 20), "bench top", size=9)
    s.text((300, COLLAR + 4), "collar", size=9)
    s.rect(-240, COLLAR, 420, COLLAR + 12, fill="#9aa", stroke="#344")
    s.text((330, COLLAR + 22), "Y rail (+X side shown)", size=9)
    s.rect(180, COLLAR + 12, 200, COLLAR + 32, fill="#8a9", stroke="#243")
    s.text((205, COLLAR + 30), "X beam", size=9)
    s.rect(170, COLLAR + 32, 260, COLLAR + 52, fill="#b8d8a0", stroke="#361")
    # simple tilt arc on the carriage (hole axis through the dot) and yoke
    s.arc((0, 0), 200, 12, 55, stroke="#6a4", sw=4)
    s.polyline([(215, COLLAR + 52), (200 * math.cos(math.radians(25)), 200 * math.sin(math.radians(25)))], stroke="#6a4", sw=3)
    s.text((150, 190), "tilt arc about the hole axis", size=9, color="#361")
    draw_gun(s, "side")
    s.dot((0, 0), 4)
    # tube + rotator on shelf
    s.rect(-63.5, TOP - 152.4, 63.5, TOP, fill="#eee", stroke="#555")
    s.line((-63.5, 0), (63.5, 0), dash="4,3", stroke="#555")
    base = -208.05
    s.rect(-180, base - 24, 120, base + 12, fill="#e8d9b5", stroke="#865")
    s.rect(-178, base + 12, -110, base + 130, fill="#e8d9b5", stroke="#865")
    s.rect(-200, base - 36, 200, base - 24, fill="#c9c9c9", stroke="#444")
    s.text((-195, base - 50), "shelf (WELD height)", size=9)
    for yp in (-185, 185):
        s.rect(yp - 6, base - 36, yp + 6, TOP, fill="#aaa", stroke="#444")
    s.rect(-200, base - 106, 200, base - 94, fill="none", stroke="#888", dash="5,4")
    s.text((-195, base - 120), "shelf at LOAD (-70 mm): tube slides out toward -X", size=9, color="#666")
    s.rect(220, base - 60, 262, base - 18, fill="#555", stroke="#000")
    s.text((266, base - 40), "Z motor + belt to 4 screws", size=9)
    # stylus
    s.circle((0, -9), 3, fill="#fff", stroke="#000")
    s.polyline([(0, -9), (6, -9), (6, COLLAR + 8)], stroke="#333", sw=2)
    s.text((12, -20), "stylus (in the gap, +X side)", size=9)
    # cameras
    s.rect(-70 - 12, 85 - 8, -70 + 12, 85 + 8, fill="#333", stroke="#000")
    s.line((-70, 85), (0, 0), stroke="#b00", dash="3,3")
    s.text((-260, 100), "joint camera (+Y, inboard)", size=9)
    # cable
    gb = (-GB[1], GB[2])
    s.line(gb, (330, 150), stroke="#222", sw=5)
    s.arc((650, 150 - 350), 350, 90, 60, stroke="#222", sw=5)
    s.line((330, 150), (650, 150), stroke="#222", sw=5)
    s.text((340, 165), "cable clamped on the carriage, then along the bench", size=9)
    s.save(OUT + "e-table-station-side.svg")


if __name__ == "__main__":
    plan()
    side()
