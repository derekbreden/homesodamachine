"""Draws sketches/knob-wired-suspension.svg: the one-wire-per-parameter layout
found by diagonal_wires.py, on the scene's proxy gun at the opening pose.
Wires are drawn 260 mm out from their attachment toward their anchors.
"""
import json, math, pathlib
import numpy as np
import diagonal_wires as W
from geometry import R_OUT, R_IN, TUBE_H, CAP_TOP, GRIP_BASE
from sketch_isocentric import svg_header, poly, text, circle, hull2d
from geometry import proxy_points

cfg = json.loads(pathlib.Path(__file__).with_name("diagonal_wires_layout.json").read_text())
wires = W.layout(cfg["q"])
pre = [(np.array(s), np.array(d), f) for s, d, f in cfg["pre"]]
COL = {"W_x": "#777", "W_y": "#777", "W_z": "#777", "W_hole": "#1b6ac9", "W_vert": "#27ae60", "W_grip": "#c0392b"}
LAB = {"W_x": "W_x (triad)", "W_y": "W_y (triad)", "W_z": "W_z (triad)", "W_hole": "W_hole = hole knob",
       "W_vert": "W_vert = vertical knob", "W_grip": "W_grip = roll knob"}


def panel(out, P, title, x0, y0):
    out.append(text(x0, y0, title, 12, color="#333"))
    for pts in [np.array([W.gp(p) for p in v]) for v in proxy_points().values()]:
        hp = hull2d([P(p) for p in pts])
        out.append(poly(hp, stroke="#444", fill="#e3e3e3", w=1, close=True))
    # outrigger: from the barrel near the nozzle to the triad and grip attachments
    root = W.gp([0, 0, 40])
    for nm, a, u, L in wires:
        if nm in ("W_x", "W_y", "W_z", "W_grip"):
            out.append(poly([P(root), P(a)], stroke="#b07d2b", w=4))
    # base loop
    out.append(circle(*P(W.GB), 9, stroke="#1b6ac9", w=2.5))
    for nm, a, u, L in wires:
        out.append(poly([P(a), P(a + 200 * u)], stroke=COL[nm], w=2.2 if nm.startswith("W_h") or nm in ("W_vert", "W_grip") else 1.4,
                        dash=None if nm in ("W_hole", "W_vert", "W_grip") else "6 3"))
        out.append(circle(*P(a), 3, stroke=COL[nm], fill=COL[nm]))
        e = P(a + 206 * u)
        out.append(text(e[0] + 3, e[1], LAB[nm], 10, color=COL[nm]))
    for site, d, f in pre:
        out.append(poly([P(site), P(site + 180 * d)], stroke="#8e44ad", w=1.4, dash="2 3"))
        e = P(site + 188 * d)
        out.append(text(e[0] + 3, e[1] + 10, f"preload ~{f:.0f} N (misses the tube)", 10, color="#8e44ad"))
    # umbilical leaving the butt
    u1 = W.GB + 60 * W.g_ax
    out.append(poly([P(W.GB), P(u1), P(u1 + np.array([0, -120, -10])), P(u1 + np.array([0, -220, -120]))], stroke="#6c3483", w=4))
    out.append(circle(*P(W.D), 3.5, stroke="#c0392b", fill="#c0392b"))


def main():
    Wd, Hd = 1300, 760
    out = svg_header(Wd, Hd, "Knob-wired suspension — each rotation wire sets one of Derek's angles; the grey triad meets at the dot")
    # side view from +X: screen x = y, screen y = -z
    ox, oy, s = 430, 540, 0.78
    P = lambda p: (ox + s * p[1], oy - s * p[2])
    out.append(poly([P((0, -R_OUT, 0)), P((0, R_OUT, 0)), P((0, R_OUT, TUBE_H)), P((0, -R_OUT, TUBE_H)), P((0, -R_OUT, 0))], w=1.4))
    out.append(poly([P((0, -R_IN, CAP_TOP)), P((0, R_IN, CAP_TOP))], w=0.8, dash="3 3"))
    panel(out, P, "Side view from +X (the tangent plane); −Y (arriving side, gun) to the left", 20, 45)
    # plan: screen x = x, screen y = -y
    ox2, oy2, s2 = 960, 330, 0.72
    Q = lambda p: (ox2 + s2 * p[0], oy2 - s2 * p[1])
    out.append(poly([Q((R_OUT * math.cos(t), R_OUT * math.sin(t), 0)) for t in np.linspace(0, 2 * math.pi, 90)], w=1.4, close=True))
    panel(out, Q, "Plan (+X right, +Y up)", 830, 45)
    notes = [
        "Grey dashed (W_x, W_y, W_z): lines through the dot — a virtual ball joint there (carry-and-locate's triad). Set once, then left alone: they make the dot the pivot.",
        "Blue W_hole: from the grip-base loop, in the vertical plane of the grip axis -> changes only the hole angle.   Green W_vert: from the same loop, along the hole-axis",
        "direction (in the plane of grip and hole axes) -> changes only the vertical-axis angle.   Red W_grip: from the outrigger, in the vertical radial plane through the dot -> only roll.",
        "Brown: printed outrigger from the nozzle end of the shell over the rim.  Purple: preloads (Derek's bungees) keep every wire taut; they set no position.",
        "Dot place (X, Z) is moved at the work (couch slides) so that no wire length has to change for it.  Layout from diagonal_wires.py; anchors ~400 mm out.",
    ]
    for i, n in enumerate(notes):
        out.append(text(20, Hd - 92 + 15 * i, n, 10, color="#444"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    p = pathlib.Path(__file__).parent / "sketches" / "knob-wired-suspension.svg"
    p.write_text(main())
    print("wrote", p)
