"""Draws sketches/c-g2-vertical-angle.svg for the wave-2 exchange on
borrowed-ecosystems' C (engraver gantry).  A gantry only translates the gun.
Translating it so the dot travels along the corner circle (a G2/G3 arc about
the tube axis) changes the gun's approach relative to the local tangent by the
arc angle, and the dot never leaves the corner.  A straight tangent move does
the same only approximately (the dot drifts off the corner by s^2/2R).
"""
import math
import numpy as np
from geometry import pose_point, proxy_points, JOINT, R_IN, R_OUT
from sketch_isocentric import svg_header, poly, text, circle, hull2d

POSE = (45, 30, 0)          # gun frame at vertical 0; the gantry supplies the plan angle


def gun_plan(offset):
    parts = proxy_points()
    return [np.array([pose_point(p, *POSE) for p in v]) + offset for v in parts.values()]


def main():
    W, H = 980, 700
    ox, oy, s = 300, 230, 1.6
    P = lambda p: (ox + s * p[0], oy - s * p[1])
    out = svg_header(W, H, "Engraver gantry: the vertical-axis angle as a G2 arc about the tube axis (plan)")
    out.append(poly([P((R_OUT * math.cos(t), R_OUT * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 120)], w=1.6, close=True))
    out.append(poly([P((R_IN * math.cos(t), R_IN * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 120)], w=0.8, dash="3 3", close=True))
    out.append(circle(*P((0, 0)), 2, fill="#222"))
    out.append(text(*P((4, -10)), "tube axis = G2 centre (I, J)", 10))
    for psi, col in ((0, "#999"), (15, "#1b6ac9")):
        d = np.array([R_IN * math.cos(math.radians(psi)), R_IN * math.sin(math.radians(psi)), JOINT[2]])
        off = d - JOINT
        for pts in gun_plan(off):
            hp = hull2d([P(p) for p in pts])
            out.append(poly(hp, stroke=col, fill="none", w=1.2, close=True))
        out.append(circle(*P(d), 3.5, stroke="#c0392b", fill="#c0392b"))
        t = np.array([-math.sin(math.radians(psi)), math.cos(math.radians(psi))])
        out.append(poly([P(d[:2] - 70 * t), P(d[:2] + 40 * t)], stroke="#c0392b", dash="5 3"))
    arc = [P((R_IN * math.cos(a), R_IN * math.sin(a))) for a in np.radians(np.linspace(0, 15, 20))]
    out.append(poly(arc, stroke="#1b6ac9", w=3))
    out.append(text(*P((R_IN + 6, 12)), "dot path: G2 about the tube axis, R 61.85", 10, color="#1b6ac9"))
    out.append(text(*P((130, 60)), "grey: gun at ψ = 0 (tangent approach, vertical 0)", 10, color="#777"))
    out.append(text(*P((130, 48)), "blue: same gun, translated only, dot moved 15° round the corner:", 10, color="#1b6ac9"))
    out.append(text(*P((130, 36)), "relative to that point's tangent (red dashes) it now approaches at vertical −15°", 10, color="#1b6ac9"))
    rows = ["straight tangent move instead (same approach change):",
            "   5°: 5.4 mm along Y leaves the dot 0.23 mm off the corner",
            "  10°: 10.7 mm → 0.93 mm off;  15°: 16.0 mm → 2.04 mm off",
            "The G2 arc leaves it exactly on the corner: one parameter, one command."]
    for i, r in enumerate(rows):
        out.append(text(520, 330 + 15 * i, r, 11, color="#333"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).parent / "sketches" / "c-g2-vertical-angle.svg"
    p.write_text(main())
    print("wrote", p)
