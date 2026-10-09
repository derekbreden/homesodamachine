"""Draws sketches/recipe-cartridge-pose.svg: the recipe cartridge at the scene's
opening pose (45 / 30 / -15).  Three balls on the shell (under the barrel near the
body front, at the grip base, under the housing back) sit in the pose block's
upper vees; the block's three lower balls sit in dowel-pin vees on a stand plate
outboard on the -Y side, clear of the tube.  Block shape = hull of the six seats
(schematic).  Rough sizes.
"""
import math
import numpy as np
from geometry import pose_point, proxy_points, JOINT, R_OUT, TUBE_H, CAP_TOP
from sketch_isocentric import svg_header, poly, text, circle, hull2d

POSE = (45, 30, -15)
SHELL_BALLS_LOCAL = [(0, -30, 120), (0, -118, 237), (0, -17, 250)]
STAND = [np.array(v, float) for v in ((110, -150, 200), (40, -230, 200), (140, -250, 200))]


def main():
    shell = [pose_point(p, *POSE) for p in SHELL_BALLS_LOCAL]
    gun = {k: np.array([pose_point(p, *POSE) for p in v]) for k, v in proxy_points().items()}
    W, H = 1180, 640
    out = svg_header(W, H, "Recipe cartridge at the opening pose 45/30/−15 — pose block between a stand and the shell (schematic)")
    for title, ox, oy, proj, x0 in (("Side view from +X (−Y left)", 380, 470, lambda p: (p[1], p[2]), 20),
                                     ("Plan (+X right, +Y up)", 900, 250, lambda p: (p[0], p[1]), 640)):
        P = lambda p, proj=proj, ox=ox, oy=oy: (ox + proj(p)[0], oy - proj(p)[1])
        out.append(text(x0, 50, title, 12, color="#333"))
        if title.startswith("Side"):
            out.append(poly([P((0, -R_OUT, 0)), P((0, R_OUT, 0)), P((0, R_OUT, TUBE_H)), P((0, -R_OUT, TUBE_H)), P((0, -R_OUT, 0))], w=1.4))
            out.append(poly([P((0, -61.8, CAP_TOP)), P((0, 61.8, CAP_TOP))], w=0.8, dash="3 3"))
            for sp in STAND:
                out.append(poly([P(sp), P((sp[0], sp[1], -60))], stroke="#999", w=1, dash="3 3"))
            out.append(text(*P((0, -300, -40)), "stand post(s) to the baseplate", 10, color="#777"))
        else:
            out.append(poly([P((R_OUT * math.cos(t), R_OUT * math.sin(t), 0)) for t in np.linspace(0, 2 * math.pi, 90)], w=1.4, close=True))
        # block
        hp = hull2d([P(p) for p in shell + STAND])
        out.append(poly(hp, stroke="#e67e22", fill="#fbeee6", w=1.5, close=True))
        for name, pts in gun.items():
            h = hull2d([P(p) for p in pts])
            out.append(poly(h, stroke="#333", fill="#dddddd", w=1, close=True))
        for b in shell:
            out.append(circle(*P(b), 5, stroke="#222", fill="#555"))
        for sp in STAND:
            out.append(circle(*P(sp), 5, stroke="#222", fill="#999"))
        out.append(circle(*P(JOINT), 3.5, stroke="#c0392b", fill="#c0392b"))
    out.append(text(20, H - 60, "Orange: the printed pose block (one per recipe; generated from the pose math). Dark balls: three 1/4 in G25 balls on the shell, seated in the block's",
                    10, color="#444"))
    out.append(text(20, H - 45, "upper vees. Grey: the block's lower balls in dowel-pin vees on the stand plate, outboard on −Y, clear of the tube. Dot place (X, Z) and yaw are",
                    10, color="#444"))
    out.append(text(20, H - 30, "set at the work (couch slides) with the dot camera; branch S puts hardened angle blocks under a hinged plate whose hinge pivots on the dot.",
                    10, color="#444"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).parent / "sketches" / "recipe-cartridge-pose.svg"
    p.write_text(main())
    print("wrote", p)
