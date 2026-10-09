"""Sketch for ideas/tilt-cradle-escape-rail.md: the whole station on an isocentric
cradle tilted tau about the station's tangent line through the dot. Left: view along
the tangent (XZ plane, from -Y). Right: view from +X (YZ plane) - the gun lies nearly
flat in this plane at tau* = 32.5 deg. Room frame: origin at the dot, +Z up.
Gun = capsule proxy; cradle, rail, column, plate head are schematic.
Run: tools/cad-venv/bin/python tilt_sketch.py
"""
import math
import numpy as np
import sketches as S
from geometry import world, CAPSULES, FEATURES, R_IN, R_OUT, RIM, CAP_TOP, FIBER_DIR_LOCAL
from tilt_calcs import Ry, RECIPE, DOT

TAU = 32.5
R = Ry(TAU)


def room(p_tube):
    return R @ (np.asarray(p_tube, float) - DOT)


def main():
    S.SCALE = 1.0
    W, H = 1500, 860
    s = S.Svg(W, H, "Tilt cradle + escape rail: the whole station tilted 32.5 deg about the station tangent (schematic)")
    # ---- left panel: XZ (view along -Y... looking toward +Y: right = +X)
    oxL, oyL = 560, 500

    def PL(q):
        return (oxL + q[0], oyL - q[2])
    bench_z = -330
    s.line(PL((-380, 0, bench_z)), PL((300, 0, bench_z)), S.INK, 2)
    s.text(PL((-375, 0, bench_z - 16)), "bench", S.NOTE, 10)
    # trunnion posts (at y = +/-175, drawn at x = 0)
    s.line(PL((0, 0, bench_z)), PL((0, 0, 0)), "#999", 12, op=0.5)
    s.circle(PL((0, 0, 0)), 9, color=S.INK, fill="#fff", w=2)
    s.text(PL((12, 0, -18)), "trunnion axis = station tangent", S.INK, 10)
    s.text(PL((12, 0, -32)), "through the dot (posts at y = +/-190)", S.INK, 10)
    # tube outline (section through the axis in the XZ plane)
    for sx in (-1, 1):
        a = room((sx * R_OUT, 0, 0)); b = room((sx * R_OUT, 0, RIM))
        a2 = room((sx * R_IN, 0, 0)); b2 = room((sx * R_IN, 0, RIM))
        s.poly([PL(a), PL(b), PL(b2), PL(a2)], color=S.WORK, fill=S.WORK, op=0.5)
    pl = [room((-R_IN, 0, CAP_TOP - 6.35)), room((R_IN, 0, CAP_TOP - 6.35)), room((R_IN, 0, CAP_TOP)), room((-R_IN, 0, CAP_TOP))]
    s.poly([PL(q) for q in pl], color=S.WORK, fill=S.WORK, op=0.25)
    # rotator + cradle floor (tube frame boxes)
    sup = RIM - 238.4
    rot = [room((x, 0, z)) for x, z in ((-150, sup), (150, sup), (150, sup + 86), (-150, sup + 86))]
    s.poly([PL(q) for q in rot], color=S.WORK, w=1, dash="3,2")
    s.text(PL(room((-150, 0, sup + 95)) + np.array([-90, 0, 0])), "rotator on 3 Z screws", S.WORK, 10)
    floor = [room((x, 0, z)) for x, z in ((-215, sup - 14), (230, sup - 14), (230, sup), (-215, sup))]
    s.poly([PL(q) for q in floor], color=S.MECH, fill=S.MECH, op=0.3)
    s.text(PL(room((-215, 0, sup - 40))), "cradle floor (tilts with everything on it)", S.MECH, 10)
    # column = upper extension of the -Y cradle side plate (y = -175), on the station side of the gun's plane;
    # rail on its -X face runs along the corner's escape direction, which is vertical at tau*
    s.poly([PL((62, 0, -30)), PL((84, 0, -30)), PL((84, 0, 330)), PL((62, 0, 330))], color=S.MECH, fill=S.MECH, op=0.35)
    s.text(PL((90, 0, 320)), "column = upper extension of the -Y cradle", S.MECH, 10)
    s.text(PL((90, 0, 306)), "side plate; rail on its face along the", S.MECH, 10)
    s.text(PL((90, 0, 292)), "escape direction (vertical at tau*)", S.MECH, 10)
    side = [room((x, -175, z)) for x, z in ((-215, sup - 14), (230, sup - 14))]
    s.line(PL((0, 0, 0)), PL(side[1]), S.MECH, 2, dash="5,4")
    s.line(PL((0, 0, 0)), PL(side[0]), S.MECH, 2, dash="5,4")
    s.line(PL((0, 0, 0)), PL((73, 0, -30)), S.MECH, 2, dash="5,4")
    # carriage arm and the vertical mounting plate, edge-on
    plate_x = 28
    s.line(PL((plate_x + 8, 0, 175)), PL((62, 0, 175)), "#335", 5, op=0.6)
    s.poly([PL((plate_x, 0, 95)), PL((plate_x + 8, 0, 95)), PL((plate_x + 8, 0, 265)), PL((plate_x, 0, 265))], color="#8d6e00", fill="#ffd54f", op=0.9)
    s.text(PL((plate_x - 250, 0, 250)), "vertical plate + recipe block (gun flat on it)", "#8d6e00", 10)
    s.arrow(PL((100, 0, 150)), PL((100, 0, 215)), S.MECH)
    s.text(PL((106, 0, 180)), "lift-off along the rail", S.MECH, 10)
    # gun capsules (room)
    for name, (a, b, rad) in CAPSULES.items():
        pa = room(world(a, RECIPE)); pb = room(world(b, RECIPE))
        s.line(PL(pa), PL(pb), S.GUN, 2 * rad, op=0.3, cap="round")
    s.circle(PL((0, 0, 0)), 4, color="#d00", fill="#d00")
    # bisector and beam arrows at the dot
    bis = room(DOT + 40 * np.array([-0.7071, 0, 0.7071]))
    s.arrow(PL((0, 0, 0)), PL(bis), "#d00")
    s.text(PL(bis + np.array([-80, 0, 8])), "fillet bisector: 12.5 deg from vertical", "#d00", 10)
    # plate head from P on the cradle (their idea, pads re-clocked)
    ph0 = room((-61.85 - 120, 0, RIM + 40)); ph1 = room((0, 0, RIM + 40)); ph2 = room((0, 0, CAP_TOP + 2))
    s.line(PL(ph0), PL(ph1), "#7b1fa2", 4, op=0.7); s.line(PL(ph1), PL(ph2), "#7b1fa2", 3, op=0.7)
    s.text(PL(ph0 + np.array([-40, 0, 14])), "plate head from P (on the cradle)", "#7b1fa2", 10)
    # tilt lock quadrant
    s.arc(PL((0, 0, 0)), 230, 200, 250, color=S.MECH, w=4)
    s.text(PL((-300, 0, -210)), "quadrant + pin: 0 ... 35 deg", S.MECH, 10)
    # ---- right panel: YZ from +X (right = +Y)
    oxR, oyR = 1220, 500

    def PR(q):
        return (oxR + q[1], oyR - q[2])
    s.line(PR((0, -330, bench_z)), PR((0, 220, bench_z)), S.INK, 2)
    # tube rim ellipse and plate
    rim_pts = [PR(room((R_IN * math.cos(t), R_IN * math.sin(t), RIM))) for t in np.linspace(0, 2 * math.pi, 90)]
    s.poly(rim_pts, color=S.WORK, w=1.2)
    s.text(PR(room((0, R_IN, RIM)) + np.array([0, 10, 10])), "rim (tilted)", S.WORK, 10)
    for name, (a, b, rad) in CAPSULES.items():
        pa = room(world(a, RECIPE)); pb = room(world(b, RECIPE))
        s.line(PR(pa), PR(pb), S.GUN, 2 * rad, op=0.35, cap="round")
    s.circle(PR((0, 0, 0)), 4, color="#d00", fill="#d00")
    s.text(PR((0, 8, -14)), "dot", "#d00", 10)
    s.poly([PR((0, -40, 95)), PR((0, -260, 95)), PR((0, -260, 265)), PR((0, -40, 265))], color="#8d6e00", fill="#ffd54f", op=0.25)
    s.line(PR((0, -150, bench_z)), PR((0, -150, 330)), S.MECH, 6, op=0.3, dash="6,4")
    s.text(PR((0, -320, 300)), "plate (behind the gun), rail/column (dashed)", "#8d6e00", 10)
    gb = room(world(FEATURES['grip_base_QBH'], RECIPE))
    fdir = R @ (world((FEATURES['grip_base_QBH'][0] + 100 * FIBER_DIR_LOCAL[1], FEATURES['grip_base_QBH'][1] + 100 * FIBER_DIR_LOCAL[2]), RECIPE) - world(FEATURES['grip_base_QBH'], RECIPE)) / 100
    pts = [gb + t * fdir for t in np.linspace(0, 90, 6)]
    end = pts[-1]
    for t in np.linspace(0, 1, 12)[1:]:
        pts.append(end * (1 - t) ** 2 + (end + 200 * fdir) * 2 * t * (1 - t) + np.array([0, -330, 440]) * t * t)
    s.poly([PR(q) for q in pts], color=S.CABLE, w=3, closed=False)
    s.text(PR((0, -330, 460)), "umbilical leaves along -Y, in the gun's plane", S.CABLE, 10)
    # notes
    notes = ["Who moves what",
             " spin: rotator (tilted, on the cradle)",
             " tilt tau: cradle about the station tangent",
             "   through the dot - a PROCESS knob",
             "   (gravity only; tau = 0 is today)",
             " lift-off, loading: the gun slides up a rail",
             "   fixed to the work along the corner's",
             "   escape direction; clears for 32/32",
             "   feasible recipes; vertical at tau*",
             " tube length: 3 Z screws, corner back",
             "   onto the trunnion axis",
             " roll, hole: recipe block; yaw: Y slide",
             "At tau* = 32.5 deg (recipe 45/30/-15):",
             " fillet bisector 12.5 deg from vertical",
             " beam in the vertical tangent plane",
             " gun's side 11 deg from that plane",
             " fiber leaves horizontally along -Y"]
    for i, l in enumerate(notes):
        s.text((20, 40 + 15 * i), l, S.INK if i == 0 else S.NOTE, 11, bold=(i == 0))
    s.save("s6-tilt-cradle-escape-rail.svg")


if __name__ == "__main__":
    main()
    print("wrote sketches/s6-tilt-cradle-escape-rail.svg")
