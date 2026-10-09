"""Draws sketches/flexure-trim-head.svg (schematic, rough sizes).

Left: the radial vertical section at the station with the work tilted to
tau* = 32.5 deg about the seam tangent (who-moves-what's cradle): the tube's
corner, the dot, the vertical escape rail and its hard stop, and the flexure
trim head on the carriage (A: across-the-corner parallelogram; W: remote-centre
pivot whose two leaves aim at the seam tangent through the dot; S: standoff
parallelogram along the beam, drawn foreshortened).
Right: one stage in detail: parallelogram, 5:1 flexure lever, micrometer, steel spring.
"""
import math
import numpy as np
from sketch_isocentric import svg_header, poly, text, circle, hull2d
from geometry import pose_point, proxy_points, JOINT

TAU = math.radians(32.5)


def main():
    W, H = 1200, 720
    out = svg_header(W, H, "Flexure trim head — printed fine knobs with no backlash, stick-slip or lock shift (schematic)")
    # ---------------- left panel: section through the station (room XZ plane, dot at origin), scale 2.2
    ox, oy, s = 330, 520, 1.5
    P = lambda x, z: (ox + s * x, oy - s * z)
    rot = lambda x, z: (x * math.cos(TAU) + z * math.sin(TAU), -x * math.sin(TAU) + z * math.cos(TAU))
    # tube-frame outlines relative to the dot: wall (x=0 inner, x=1.65 outer) from z=-60 to rim at +6.35, cap z=0 inward to x=-80
    wall_in = [rot(0, z) for z in (-60, 6.35)]
    wall_out = [rot(1.65, z) for z in (-60, 6.35)]
    cap_top = [rot(x, 0) for x in (-90, 0)]
    cap_bot = [rot(x, -6.35) for x in (-90, 0)]
    for seg in (wall_in, wall_out, cap_top, cap_bot):
        out.append(poly([P(*seg[0]), P(*seg[1])], w=1.8))
    out.append(poly([P(*rot(0, 6.35)), P(*rot(1.65, 6.35))], w=1.8))
    # the gun proxy at the opening pose 45/30/-15, tilted with the work by tau* (everything rides the cradle)
    for pts in proxy_points().values():
        rel = [pose_point(q, 45, 30, -15) - JOINT for q in pts]
        xz = [rot(v[0], v[2]) for v in rel]
        out.append(poly(hull2d([P(*q) for q in xz]), stroke="#666", fill="#e8e8e8", w=0.8, close=True))
    out.append(circle(*P(0, 0), 4, stroke="#c0392b", fill="#c0392b"))
    out.append(text(*P(-78, -12), "dot; the seam tangent is ⟂ to this view", 10, color="#c0392b"))
    out.append(text(*P(-95, -40), "tube wall and end plate,", 10))
    out.append(text(*P(-95, -47), "tilted τ* = 32.5° (fillet ~flat)", 10))
    # escape rail (vertical) on the station side
    out.append(poly([P(70, -20), P(70, 150)], stroke="#555", w=5))
    out.append(text(*P(74, 146), "escape rail (vertical at τ*)", 10, color="#555"))
    out.append(poly([P(64, -12), P(76, -12)], stroke="#555", w=3))
    out.append(text(*P(78, -14), "hard stop: ball in vee, gravity-seated (motion to a stop)", 10, color="#555"))
    # carriage
    out.append(poly([P(60, -8), P(80, -8), P(80, 40), P(60, 40)], close=True, stroke="#555", fill="#eee"))
    # A stage: parallelogram moving horizontally (across the corner)
    ax0, az0 = 30, 20
    out.append(poly([P(ax0, az0 - 12), P(ax0 + 28, az0 - 12), P(ax0 + 28, az0 + 12), P(ax0, az0 + 12)], close=True, stroke="#27ae60", fill="#eaf7ef"))
    for xx in (ax0 + 4, ax0 + 24):
        out.append(poly([P(xx, az0 - 12), P(xx, az0 + 12)], stroke="#27ae60", w=1))
    out.append(poly([P(ax0 - 6, az0), P(ax0 + 34, az0)], stroke="#27ae60", w=1, dash="3 2"))
    out.append(text(*P(ax0 - 2, az0 + 20), "A: across the corner", 10, color="#27ae60"))
    out.append(text(*P(ax0 - 2, az0 + 14), "parallelogram, ±1.5 mm", 10, color="#27ae60"))
    # W stage: remote-centre pivot, two leaves aimed at the dot from ~80 mm
    for ang in (38, 62):
        a = math.radians(ang)
        n = (math.cos(a), math.sin(a))
        p1 = (80 * n[0], 80 * n[1]); p2 = (130 * n[0], 130 * n[1])
        out.append(poly([P(*p1), P(*p2)], stroke="#1b6ac9", w=3))
        out.append(poly([P(0, 0), P(*p1)], stroke="#1b6ac9", w=0.8, dash="4 3"))
    out.append(text(*P(34, 110), "W: remote-centre pivot — two spring-steel", 10, color="#1b6ac9"))
    out.append(text(*P(34, 104), "leaves whose lines meet at the seam tangent", 10, color="#1b6ac9"))
    out.append(text(*P(34, 98), "through the dot (D ≈ 80 mm): work angle", 10, color="#1b6ac9"))
    # S stage along the beam (beam lies in the vertical tangent plane -> appears vertical here)
    out.append(poly([P(10, 140), P(10, 200)], stroke="#8e44ad", w=4))
    out.append(text(*P(-80, 205), "S: standoff parallelogram along the beam", 10, color="#8e44ad"))
    out.append(text(*P(-80, 199), "(beam lies in the view's normal plane, drawn foreshortened)", 10, color="#8e44ad"))
    out.append(poly([P(0, 0), P(10, 140)], stroke="#c0392b", w=1.2, dash="6 3"))
    out.append(text(*P(-80, 160), "recipe block + shell above (coarse hole/roll)", 10))
    out.append(text(20, 40, "Section at the station, room frame, work and gun (proxy, opening pose 45/30/−15) tilted to τ* (who-moves-what T-b1). ×1.5, rough.", 11, color="#555"))

    # ---------------- right panel: stage detail
    bx, by = 760, 470
    Q = lambda x, y: (bx + x, by - y)
    out.append(text(740, 110, "One stage, in detail", 12, color="#333"))
    out.append(poly([Q(0, 0), Q(360, 0)], w=3))
    # parallelogram: fixed base, two vertical leaves, moving platform
    out.append(poly([Q(40, 0), Q(40, 12), Q(200, 12), Q(200, 0)], close=True, fill="#ddd"))
    for xx in (60, 180):
        out.append(poly([Q(xx, 12), Q(xx, 132)], stroke="#1b6ac9", w=2))
    out.append(poly([Q(40, 132), Q(200, 132), Q(200, 160), Q(40, 160)], close=True, fill="#eaf1fb", stroke="#1b6ac9"))
    out.append(text(*Q(52, 175), "moving platform (to the next stage)", 10, color="#1b6ac9"))
    out.append(text(*Q(66, 80), "spring-steel leaves 0.25 × 20 × 40,", 10, color="#1b6ac9"))
    out.append(text(*Q(66, 68), "clamped in PET-GF blocks", 10, color="#1b6ac9"))
    # lever with notch hinge, micrometer at the long end, spring preload
    out.append(poly([Q(200, 146), Q(230, 146)], w=2))          # push rod platform -> lever short arm
    out.append(poly([Q(230, 30), Q(250, 30), Q(250, 250), Q(230, 250)], close=True, fill="#fbeee6", stroke="#e67e22"))
    out.append(circle(*Q(240, 120), 5, stroke="#e67e22", fill="#e67e22"))
    out.append(text(*Q(258, 118), "notch hinge (printed)", 10, color="#e67e22"))
    out.append(text(*Q(258, 144), "short arm 26 mm", 10, color="#e67e22"))
    out.append(text(*Q(258, 250), "long arm 130 mm → 5:1", 10, color="#e67e22"))
    out.append(poly([Q(250, 245), Q(330, 245)], stroke="#333", w=6))
    out.append(text(*Q(270, 262), "micrometer head (0.01 mm)", 10))
    out.append(text(*Q(270, 232), "→ 2 µm per division at the stage", 10))
    out.append(poly([Q(20, 146), Q(40, 146)], stroke="#8e44ad", w=2, dash="2 2"))
    out.append(text(*Q(-60, 120), "steel spring: keeps platform,", 10, color="#8e44ad"))
    out.append(text(*Q(-60, 108), "lever and spindle in contact", 10, color="#8e44ad"))
    notes = [
        "Rules: flexures guide, steel springs preload, steel micrometers set, the carrier (not the flexures) takes the gun's weight where it can;",
        "leaves run along the gun's weight at the working tilt; the dry run happens at thermal steady state just before the weld.",
        "Ranges (1095 shim leaves): parallelogram ±4 mm at L 40; remote-centre pivot ±3.4° (L 40) to ±13° (L 80) at D 70. Drift of the remote centre:",
        "≤ 24–42 µm at ±1°, 96–170 µm at ±2° (D 70). All estimates, flexures.py.",
    ]
    for i, n in enumerate(notes):
        out.append(text(20, H - 70 + 15 * i, n, 10, color="#444"))
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    import pathlib
    p = pathlib.Path(__file__).parent / "sketches" / "flexure-trim-head.svg"
    p.write_text(main())
    print("wrote", p)
