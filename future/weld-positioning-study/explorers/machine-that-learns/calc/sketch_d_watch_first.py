"""Sketch: D, watch-first. The gun hangs on a magnet-preloaded kinematic seat under a
small bridge, with two hand-wheel stages (counters + AS5600) between bridge and
pose block. Rotator on the bench exactly as today. No new motors.
"""
from svgkit import Svg, draw_gun, draw_tube_side

OUT = "../sketches/"
BENCH = -232.0
CAM = (-45.0, 70.0, 85.0)
GB = (-62.6, -233.5, 139.6)
BAR = 330.0


def side():
    s = Svg(1000, 660, -300, 600, -250, 420,
            "D  watch-first: gun hangs on a kinematic seat; the station only measures and shows",
            notes=["Carries the gun: bridge -> hand-wheel Z -> hand-wheel X -> printed pose block -> kinematic seat (3 balls, 3 grooves, pot-magnet preload) -> shell.",
                   "The hand no longer holds the pose; it only seats the gun (magnet snap), dials X/Z to what the screen shows, and fires (trigger or Bowden pedal).",
                   "Rotator on the bench as today: pedal turns the table; the camera logs every revolution. Every part is reused when motors arrive (A or B)."])
    s.rect(-300, BENCH - 10, 600, BENCH, fill="#caa472", stroke="#7a5a2a")
    s.rect(-180, BENCH, 120, BENCH + 36, fill="#e8d9b5", stroke="#865")
    s.rect(-178, BENCH + 36, -110, BENCH + 154, fill="#e8d9b5", stroke="#865")
    s.rect(96, BENCH + 36, 118, BENCH + 115, fill="#e8d9b5", stroke="#865")
    s.rect(-75, BENCH + 36, 75, BENCH + 84, fill="#efe4c8", stroke="#865")
    s.text((-70, BENCH + 60), "existing rotator, unchanged, clamped to the bench", size=9)
    draw_tube_side(s)
    for yh in (-230, 330):
        s.rect(yh - 15, BENCH, yh + 15, BAR + 25, fill="#ccc", stroke="#555")
    s.rect(-245, BAR, 345, BAR + 25, fill="#bbb", stroke="#555")
    s.text((-240, BAR + 33), "small 2040 bridge, feet clamped through the same bench (or to the rotator base)", size=10)
    # hand-wheel stages
    s.rect(80, 240, 125, BAR, fill="#c9d6c9", stroke="#353")
    s.circle((102, 330 + 45), 12)
    s.text((130, 300), "Z hand wheel + counter (vertical SFU1605)", size=10)
    s.rect(60, 215, 150, 240, fill="#c9d6c9", stroke="#353")
    s.text((155, 222), "X hand wheel + counter (radial, into page)", size=10)
    s.poly([(95, 215), (111, 215), (108, 175), (98, 175)], fill="#f2c26b", stroke="#963")
    s.text((115, 190), "pose block + seat (pot magnet preload)", size=10)
    draw_gun(s, "side")
    s.dot((0, 0), 4)
    s.text((6, -14), "dot", size=10, color="#b00")
    gb = (-GB[1], GB[2])
    far = (gb[0] + 110, gb[1] + 14)
    s.line(gb, far, stroke="#222", sw=5)
    s.arc((far[0], far[1] - 350), 350, 90, 35, stroke="#222", sw=5)
    s.text((far[0] + 8, far[1] + 14), "umbilical to a saddle on the post", size=10)
    cam = (-CAM[1], CAM[2])
    s.rect(cam[0] - 12, cam[1] - 8, cam[0] + 12, cam[1] + 8, fill="#333", stroke="#000")
    s.line(cam, (0, 0), stroke="#b00", dash="3,3")
    s.line(cam, (-CAM[1], BAR), stroke="#555", sw=2)
    s.text((cam[0] - 16, cam[1] + 18), "joint camera", size=10, anchor="end")
    # HUD
    s.rect(-290, 120, -170, 200, fill="#223", stroke="#000")
    s.text((-285, 185), "screen:", size=10, color="#fff")
    s.text((-285, 170), "dot->corner +0.08", size=10, color="#fff")
    s.text((-285, 155), "wall/cap 38/62", size=10, color="#fff")
    s.text((-285, 140), "standoff -0.1", size=10, color="#fff")
    s.text((-285, 125), "theta 212.4 deg", size=10, color="#fff")
    s.save(OUT + "d-watch-first-side.svg")


if __name__ == "__main__":
    side()
