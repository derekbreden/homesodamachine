"""Draws sketches/c-arm-side.svg for ideas/c-arm-on-the-gun.md.

Same scene frame and gun proxy as sketch_isocentric.py.  Here the rotator is
not rotated: it sits on an X/Z trim + Y drawer only, so its bench is ~60 mm
higher than the bare rotator's.  The whole orientation stack hangs from an
overhead yaw bearing on the dot's vertical.  Sizes are rough.
"""
import math
import numpy as np
from geometry import pose_point, JOINT, GRIP_BASE, R_OUT, TUBE_H, CAP_TOP
from sketch_isocentric import svg_header, poly, text, circle, hull2d, gun_parts_world

I = JOINT
BASE_Z = -86.0 - 60.0     # trim stack ~60 mm (X slide, Y drawer, Z wedge/screws)
R_ARC = 300.0
E = math.radians(30)
AX = np.array([0, -math.cos(E), math.sin(E)])


YAW = math.radians(-15)          # the opening pose's vertical-axis angle, applied by the yaw table
RZ = np.array([[math.cos(YAW), -math.sin(YAW), 0], [math.sin(YAW), math.cos(YAW), 0], [0, 0, 1]])
AX = RZ @ AX


def yawed(p):
    p = np.asarray(p, float)
    return I + RZ @ (p - I)


def arc_pt(e_deg, r=R_ARC):
    e = math.radians(e_deg)
    return yawed(I + r * np.array([0, -math.cos(e), math.sin(e)]))


def side():
    W, H = 1000, 1000
    ox, oy = 600, 760
    P = lambda p: (ox + p[1], oy - p[2])
    out = svg_header(W, H, "C-arm on the gun (original) — side view from +X at the opening pose 45/30/−15 (yaw table turned −15°)")
    out.append(poly([P((0, -420, BASE_Z)), P((0, 330, BASE_Z))], w=3))
    # goalpost
    for yy in (-400, 260):
        out.append(poly([P((0, yy, BASE_Z)), P((0, yy, 640)), P((0, yy + 40, 640)), P((0, yy + 40, BASE_Z))], close=True, fill="#eee"))
    out.append(poly([P((0, -400, 640)), P((0, 300, 640)), P((0, 300, 680)), P((0, -400, 680))], close=True, fill="#eee"))
    out.append(text(*P((0, -390, 695)), "goalpost frame (4040 extrusion or welded steel box), straddles the rotator", 10))
    # yaw table upside down under the crossbeam, centred on the dot's vertical
    out.append(poly([P((0, -55, 560)), P((0, 55, 560)), P((0, 55, 640)), P((0, -55, 640))], close=True, stroke="#1b6ac9", fill="#eaf1fb"))
    out.append(text(*P((0, 62, 600)), "yaw (vertical-axis) rotary table, hung table-down", 10, color="#1b6ac9"))
    out.append(poly([P((0, 0, 700)), P((0, 0, BASE_Z))], stroke="#1b6ac9", w=1, dash="8 4"))
    # yaw frame: from table down to arc top, plus a strut to arc bottom
    top = arc_pt(78); bot = arc_pt(8)
    out.append(poly([P((0, 0, 560)), P((0, 0, 520)), P(top)], stroke="#1b6ac9", w=5))
    out.append(poly([P(yawed((I[0], -30, 540))), P(yawed((I[0], -330, 470))), P(bot)], stroke="#1b6ac9", w=3))
    out.append(text(*P((0, -330, 485)), "yaw frame + strut (swings about the dot's vertical)", 10, color="#1b6ac9"))
    # the C-arc (in the plane x = dot.x + 50)
    arc = [P(arc_pt(e)) for e in np.linspace(8, 78, 60)]
    out.append(poly(arc, stroke="#1b6ac9", w=7))
    out.append(text(*P(arc_pt(55) + np.array([0, -330, 60])), "C-arc, R 300 about the dot (plane x = dot + 50):", 10, color="#1b6ac9"))
    out.append(text(*P(arc_pt(55) + np.array([0, -330, 47])), "carriage position = hole angle, read on the arc", 10, color="#1b6ac9"))
    # graduations every 5 deg
    for e in range(10, 80, 5):
        a = arc_pt(e, R_ARC + 6); b = arc_pt(e, R_ARC + (16 if e % 10 == 0 else 11))
        out.append(poly([P(a), P(b)], stroke="#1b6ac9", w=1))
    # carriage + roll bearing at e = 30
    c = arc_pt(30)
    out.append(circle(*P(c), 16, stroke="#c0392b", w=2.5))
    out.append(text(*P(c + np.array([0, -330, -60])), "carriage carries the roll bearing on the grip axis", 10, color="#c0392b"))
    out.append(poly([P(I - 15 * AX), P(I + 360 * AX)], stroke="#c0392b", w=1, dash="6 3"))
    # gun
    from geometry import proxy_points
    for name, pts in {k: np.array([pose_point(p, 45, 30, -15) for p in v]) for k, v in proxy_points().items()}.items():
        hp = hull2d([P(p) for p in pts])
        out.append(poly(hp, stroke="#333", fill="#d9d9d9" if name in ("housing", "grip") else "#bbbbbb", w=1, close=True))
    tip = pose_point([0, 0, 0], 45, 30, -15)
    out.append(poly([P(tip), P(I)], stroke="#c0392b", w=1.5))
    out.append(circle(*P(I), 3, stroke="#c0392b", fill="#c0392b"))
    # tube + trim stack + rotator
    out.append(poly([P((0, -R_OUT, 0)), P((0, R_OUT, 0)), P((0, R_OUT, TUBE_H)), P((0, -R_OUT, TUBE_H)), P((0, -R_OUT, 0))], w=1.6))
    out.append(poly([P((0, -61.8, CAP_TOP)), P((0, 61.8, CAP_TOP))], w=1, dash="4 3"))
    out.append(poly([P((0, -120, -62)), P((0, 180, -62)), P((0, 180, -50)), P((0, -120, -50))], close=True))
    out.append(poly([P((0, -130, BASE_Z)), P((0, 190, BASE_Z)), P((0, 190, -86)), P((0, -130, -86))], close=True, fill="#f4f4f4"))
    out.append(text(*P((0, 60, BASE_Z + 20)), "X/Z trim + Y drawer (no rotation) under the rotator", 10))
    # umbilical up to a balancer on the crossbeam
    gb = pose_point(GRIP_BASE, 45, 30, -15)
    cab = [gb, gb + 80 * AX, gb + 80 * AX + np.array([0, -60, 80]), np.array([0, -250, 640])]
    out.append(poly([P(p) for p in cab], stroke="#8e44ad", w=3))
    out.append(text(*P((0, -250, 620)), "umbilical hung from a balancer on the crossbeam", 10, color="#8e44ad"))
    out.append(text(20, H - 40, "Sizes rough. Arc drawn from 8° to 78° grip-axis elevation, turned −15° with the yaw frame. Branch C-0 deletes the yaw table and sets −15° by the work's Y slide.", 10, color="#555"))
    out.append(text(20, H - 24, "What moves for each knob: yaw table → frame + arc + gun about the dot's vertical; arc carriage → roll bearing + gun about the X line through the dot; roll → gun about the grip axis.", 10, color="#555"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    d = pathlib.Path(__file__).parent / "sketches"
    (d / "c-arm-side.svg").write_text(side())
    print("wrote", d / "c-arm-side.svg")
