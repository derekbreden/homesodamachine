"""Draws sketches/a1g-isocentric-rider.svg for the wave-2 exchange on
borrowed-ecosystems' A1 (rim rider).  Branch A1-G: on the rider, an XYZ
micrometer stage carries both the wire-guide mount and a small arc centred on
the seam tangent through the dot; the shell hangs on the arc's carriage; the
weight is carried by the arm/balancer through a soft hook at the CG.

Gun = the scene's proxy at the real opening pose (roll 45, dial 30, vertical -15).
Rider stations from borrowed-ecosystems A1 (theta -30, -60 on the rim, OD wheel
at -45).  Arc: plane y = -40, radius 70, 0-60 deg.  Rough, schematic sizes.
"""
import math
import numpy as np
from geometry import pose_point, JOINT, R_IN, R_OUT, TUBE_H, CAP_TOP, GRIP_BASE
from sketch_isocentric import svg_header, poly, text, circle, hull2d
from geometry import proxy_points

POSE = (45, 30, -15)
Y0, RA = -40.0, 70.0
I = JOINT


def gun_parts():
    return {k: np.array([pose_point(p, *POSE) for p in v]) for k, v in proxy_points().items()}


def main():
    W, H = 1180, 700
    out = svg_header(W, H, "A1-G — isocentric rider (branch of borrowed-ecosystems A1): section along the tangent, and plan")
    # ---------------- left panel: section in the XZ plane (looking along +Y from the arriving side)
    ox, oy, s = 330, 470, 2.2
    P = lambda p: (ox + s * (p[0] - I[0]), oy - s * (p[2] - I[2]))
    # tube wall (bore/OD) at y = -40 is at x ~47..49 ; draw the wall at the dot's section (y=0) for clarity
    out.append(poly([P((R_IN, 0, 60)), P((R_IN, 0, TUBE_H)), P((R_OUT, 0, TUBE_H)), P((R_OUT, 0, 60))], w=1.6))
    out.append(poly([P((R_IN - 120, 0, CAP_TOP)), P((R_IN, 0, CAP_TOP))], w=1.6))
    out.append(poly([P((R_IN - 120, 0, CAP_TOP - 6.35)), P((R_IN, 0, CAP_TOP - 6.35))], w=0.8, dash="3 3"))
    out.append(text(*P((R_IN - 118, 0, CAP_TOP - 12)), "end plate (6.35)", 10))
    out.append(text(*P((R_OUT + 3, 0, 75)), "tube wall", 10))
    out.append(circle(*P(I), 3.5, stroke="#c0392b", fill="#c0392b"))
    out.append(text(*P((I[0] - 115, 0, I[2] - 22)), "dot (seam tangent ⟂ to this view)", 10, color="#c0392b"))
    # arc
    arc = [P((R_IN + RA * math.cos(a), Y0, CAP_TOP + RA * math.sin(a))) for a in np.radians(np.arange(-5, 66, 2))]
    out.append(poly(arc, stroke="#1b6ac9", w=6))
    for a in range(0, 61, 10):
        p0 = (R_IN + (RA + 5) * math.cos(math.radians(a)), Y0, CAP_TOP + (RA + 5) * math.sin(math.radians(a)))
        p1 = (R_IN + (RA + 11) * math.cos(math.radians(a)), Y0, CAP_TOP + (RA + 11) * math.sin(math.radians(a)))
        out.append(poly([P(p0), P(p1)], stroke="#1b6ac9"))
    out.append(text(*P((R_IN + RA + 14, 0, CAP_TOP + 50)), "work-angle arc, R 70 about the", 10, color="#1b6ac9"))
    out.append(text(*P((R_IN + RA + 14, 0, CAP_TOP + 43)), "seam tangent through the dot", 10, color="#1b6ac9"))
    out.append(text(*P((R_IN + RA + 14, 0, CAP_TOP + 36)), "(printed arc + micrometer tangent screw)", 10, color="#1b6ac9"))
    # carriage at 35 deg and bracket to the barrel
    ca = math.radians(35)
    car = np.array([R_IN + RA * math.cos(ca), Y0, CAP_TOP + RA * math.sin(ca)])
    out.append(circle(*P(car), 9, stroke="#1b6ac9", fill="#eaf1fb", w=2))
    barrel_y = pose_point([0, 0, 0], *POSE) + 58 * (pose_point([0, 0, 100], *POSE) - pose_point([0, 0, 0], *POSE)) / 100
    out.append(poly([P(car), P((car[0] - 20, Y0, car[2] + 20)), P(barrel_y)], stroke="#1b6ac9", w=3))
    out.append(text(*P((car[0] - 60, 0, car[2] + 34)), "carriage → shell bracket", 10, color="#1b6ac9"))
    # gun proxy projected
    for name, pts in gun_parts().items():
        hp = hull2d([P(p) for p in pts if p[2] < I[2] + 120])
        if len(hp) >= 3:
            out.append(poly(hp, stroke="#333", fill="#dddddd", w=1, close=True))
    tip = pose_point([0, 0, 0], *POSE)
    out.append(poly([P(tip), P(I)], stroke="#c0392b", w=1.5))
    # rider saddle outboard: XYZ stage block and V-wheel
    vw = np.array([R_OUT * math.cos(math.radians(-30)), R_OUT * math.sin(math.radians(-30)), TUBE_H])
    out.append(circle(*P((R_OUT - 1, 0, TUBE_H + 4)), 6.5, stroke="#555", w=1.5))
    out.append(text(*P((R_OUT - 95, 0, TUBE_H + 20)), "V-wheels on the rim edge →", 10, color="#555"))
    out.append(circle(*P((R_OUT + 6.5, 0, TUBE_H - 45)), 11, stroke="#555", w=1.5))
    out.append(text(*P((R_OUT + 20, 0, TUBE_H - 48)), "OD wheel", 10, color="#555"))
    out.append(poly([P((R_OUT + 12, 0, TUBE_H - 20)), P((R_OUT + 12, 0, TUBE_H + 10)), P((R_OUT + 70, 0, TUBE_H + 10)), P((R_OUT + 70, 0, TUBE_H - 20))], close=True, stroke="#555", fill="#f2f2f2"))
    out.append(text(*P((R_OUT + 14, 0, TUBE_H - 30)), "rider saddle", 10, color="#555"))
    out.append(poly([P((R_OUT + 72, 0, TUBE_H - 20)), P((R_OUT + 72, 0, TUBE_H + 20)), P((R_OUT + 112, 0, TUBE_H + 20)), P((R_OUT + 112, 0, TUBE_H - 20))], close=True, stroke="#27ae60", fill="#eaf7ef"))
    out.append(text(*P((R_OUT + 74, 0, TUBE_H - 30)), "XYZ micrometer stage", 10, color="#27ae60"))
    out.append(text(*P((R_OUT + 74, 0, TUBE_H - 37)), "(dot place: moves arc, gun", 10, color="#27ae60"))
    out.append(text(*P((R_OUT + 74, 0, TUBE_H - 44)), " and wire guide together)", 10, color="#27ae60"))
    # wire guide mount on the XYZ carriage, arriving from -Y (shown end-on-ish)
    wg = np.array([I[0] - 10, 0, I[2] + 22])
    out.append(poly([P((R_OUT + 80, 0, TUBE_H + 20)), P((R_OUT + 20, 0, TUBE_H + 40)), P(wg)], stroke="#e67e22", w=2))
    out.append(poly([P(wg), P(I)], stroke="#e67e22", w=1.2))
    out.append(text(*P((R_OUT + 22, 0, TUBE_H + 48)), "wire guide on the XYZ carriage, not on the gun", 10, color="#e67e22"))
    out.append(text(20, 40, "Section: looking along the seam tangent from the arriving side (−Y). Scale ×2.2.", 11, color="#555"))

    # ---------------- right panel: plan
    ox2, oy2, s2 = 900, 300, 1.25
    Q = lambda p: (ox2 + s2 * p[0], oy2 - s2 * p[1])
    out.append(poly([Q((R_OUT * math.cos(t), R_OUT * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 90)], w=1.6, close=True))
    out.append(circle(*Q(I), 3, stroke="#c0392b", fill="#c0392b"))
    for ang in (-30, -60):
        p = (R_OUT * math.cos(math.radians(ang)), R_OUT * math.sin(math.radians(ang)))
        out.append(circle(*Q(p), 5, stroke="#555", w=1.5))
    out.append(text(*Q((75, -80)), "V-wheels at −30°, −60°", 10, color="#555"))
    out.append(poly([Q((R_IN + RA * math.cos(a), Y0)) for a in np.radians((0, 60))], stroke="#1b6ac9", w=6))
    out.append(text(*Q((96, -52)), "arc (plane y = −40)", 10, color="#1b6ac9"))
    for name, pts in gun_parts().items():
        hp = hull2d([Q(p) for p in pts])
        out.append(poly(hp, stroke="#333", fill="#dddddd", w=1, close=True))
    cg = pose_point([0, -20, 190], *POSE)
    out.append(circle(*Q(cg), 6, stroke="#8e44ad", w=2))
    out.append(text(*Q((cg[0] - 150, cg[1] - 12)), "soft hook at the CG → arm / balancer", 10, color="#8e44ad"))
    out.append(text(*Q((cg[0] - 150, cg[1] - 24)), "(weight only; the rider sees none of it)", 10, color="#8e44ad"))
    gb = pose_point(GRIP_BASE, *POSE)
    out.append(circle(*Q(gb), 4, stroke="#c0392b"))
    out.append(text(*Q((gb[0] + 8, gb[1])), "grip base (dial 30)", 10, color="#c0392b"))
    out.append(poly([Q((30, -150)), Q((150, -150))], stroke="#555", dash="4 3"))
    out.append(text(*Q((40, -162)), "tangential tether + breakaway (A1)", 10, color="#555"))
    out.append(text(640, 40, "Plan: gun at the scene's real opening pose (roll 45, dial 30, vertical −15).", 11, color="#555"))
    out.append(text(20, H - 44, "Knobs: XYZ = dot place (beam and wire move together); arc = work angle about the dot (gun only; wire stays); printed wedges = coarse hole/roll/vertical (gun only);", 10, color="#555"))
    out.append(text(20, H - 28, "wire micrometers = wire tip vs dot. Loads through the arc and stage are the rider preload and disturbances only, so printed arcs and optics stages are adequate there.", 10, color="#555"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).parent / "sketches" / "a1g-isocentric-rider.svg"
    p.write_text(main())
    print("wrote", p)
