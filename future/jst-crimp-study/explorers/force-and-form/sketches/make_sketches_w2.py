"""Wave-2 schematic sketches for force-and-form: f4b, f5b, f6, f7, f8. Not to scale.

Run: python3 make_sketches_w2.py  (writes the SVGs beside this file)
"""
import os
from svgkit import Svg

HERE = os.path.dirname(os.path.abspath(__file__))
LEGEND = [("steel", "steel (force path, dies)"), ("print", "printed"),
          ("bought", "bought motion / sensing"), ("contact", "XH contact")]


def legend(s, x, y):
    for i, (cls, lab) in enumerate(LEGEND):
        s.rect(x + i * 175, y - 10, 14, 12, cls)
        s.text(x + i * 175 + 20, y, lab, "sm")
    s.line(x + 4 * 175, y - 4, x + 4 * 175 + 22, y - 4, "wire")
    s.text(x + 4 * 175 + 28, y, "conductor", "sm")


def contact_side(s, x, y, sc=1.0, box_left=True):
    """XH contact seen from the side, floor at y, front (box) at x if box_left.
    Lengths ~ box 2.0, transition 0.6, cond barrel 1.4, window 0.6, ins barrel 1.2 (x ~ 30 px/mm * sc)."""
    k = 30 * sc
    d = 1 if box_left else -1
    xs = x
    # box
    s.rect(min(xs, xs + d * 2.0 * k), y - 2.3 * k, 2.0 * k, 2.3 * k, "contact")
    # lance
    lx = xs + d * 2.44 * k
    s.pline([(xs + d * 1.9 * k, y), (lx, y + 0.7 * k)], "ln")
    # conductor barrel wings
    cx0 = xs + d * 2.6 * k
    s.rect(min(cx0, cx0 + d * 1.4 * k), y - 1.55 * k, 1.4 * k, 1.55 * k, "contact")
    ix0 = xs + d * 4.6 * k
    s.rect(min(ix0, ix0 + d * 1.2 * k), y - 2.9 * k, 1.2 * k, 2.9 * k, "contact")
    s.rect(min(xs, xs + d * 5.8 * k), y, 5.8 * k, 0.2 * k, "contact")


# ---------------------------------------------------------------- f4b
def f4b():
    s = Svg(880, 560, "f4 head leaving toward the box, schematic",
            "Side section of the travelling crimp head: steel C with its spine ahead of the box and "
            "its mouth toward the comb; knee-driven crimper above, anvil on a dropping wedge below.")
    s.text(20, 28, "f4  The head goes to the wire, and leaves toward the box", "h")
    s.text(20, 46, "schematic side section along the conductor, not to scale", "t2")
    s.rect(20, 60, 840, 330, "box")
    # comb and ribbon
    s.rect(40, 230, 110, 40, "print", 4)
    s.text(44, 290, "comb grips the jacket", "sm")
    s.text(44, 303, "4-5 mm behind the tip", "sm")
    s.line(40, 250, 330, 250, "wire")
    for dy in (-3, 0, 3):
        s.line(330, 250 + dy, 395, 250 + dy, "strand")
    # contact on the wire (box to the right)
    k = 22
    x0 = 300
    s.rect(x0 + 0, 250 - 2.9 * k + 20, 1.2 * k, 2.9 * k - 20, "contact")      # ins barrel
    s.rect(x0 + 44, 250 - 1.55 * k + 8, 1.4 * k, 1.55 * k - 8, "contact")     # cond barrel
    s.rect(x0 + 90, 250 - 2.3 * k + 6, 2.0 * k, 2.3 * k, "contact")           # box
    s.line(x0 + 92, 256, x0 + 84, 272, "ln")                                  # lance
    s.text(x0 + 84, 290, "lance", "sm")
    # head C: spine at right, jaws reaching left
    s.rect(560, 90, 60, 280, "steel")                                         # spine
    s.rect(270, 90, 290, 40, "steel")                                         # upper jaw
    s.rect(270, 330, 290, 40, "steel")                                        # lower jaw
    s.text(566, 385, "spine", "sm")
    s.rect(640, 150, 90, 60, "bought", 3)
    s.lines(645, 170, ["NEMA 17", "lead screw"], "sm", 12)
    s.pline([(640, 180), (560, 180)], "ln")
    # knee
    s.pline([(470, 130), (440, 160), (410, 130)], "ln")
    s.circle(440, 160, 4, "dark")
    s.text(476, 150, "knee", "sm")
    s.rect(405, 160, 70, 40, "steel")                                         # crimper holder
    s.rect(395, 200, 80, 18, "dark")                                          # crimper
    s.text(420, 196, "crimper", "sm")
    # anvil on wedge
    s.rect(300, 276, 190, 18, "dark")
    s.text(310, 290, "anvil (relief behind the lance)", "sm")
    s.poly([(300, 294), (500, 294), (500, 318), (300, 306)], "steel")
    s.rect(505, 300, 40, 22, "bought", 3)
    s.text(505, 338, "wedge servo", "sm")
    s.move(470, 300, 470, 326)
    s.text(440, 345, "drops 1.5 mm", "sm")
    # moves
    s.move(640, 132, 760, 132)
    s.lines(636, 94, ["leave: crimper up 5 mm, anvil down", "1.5 mm, head moves toward the box"], "sm", 12)
    s.move(380, 70, 300, 70)
    s.text(385, 74, "thread: head moves toward the comb; the barrel's flared rear is the funnel", "sm")
    s.lines(30, 410, ["1 Pick: box first into the mouth at the dispenser; anvil up, crimper to capture; the dispenser's drop-shear cuts the tab outside the mouth.",
                      "2 Find the tip (camera).  3 Thread: the head slides the captured contact onto the still conductor.  4 Crimp: knee straight.",
                      "5 Leave: down is closed (crimper), sideways is closed (neighbours at 5 mm), back along the wire is closed (anything behind the barrel);",
                      "  forward is open: box and lance (2.8-3.25 mm) pass a 6.5 mm gap."], "t2", 16)
    legend(s, 30, 500)
    s.text(30, 530, "The force closes inside the C; the gantry that carries the head only positions it.", "t2")
    s.save(os.path.join(HERE, "f4b-head-exit.svg"))


# ---------------------------------------------------------------- f5b
def f5b():
    s = Svg(880, 580, "f5b half-row cassette at 5.0 mm, schematic",
            "Top view of the lower shoe with five keyed pockets at 5.0 mm, a gate, a housing nest at the "
            "front edge, and the odd plane of a split ribbon spread from 3.4 to 5.0 mm by a comb.")
    s.text(20, 28, "f5b  Half-row cassette: crimp every other cavity at 5.0 mm, then push the row in", "h")
    s.text(20, 46, "schematic top view of the lower shoe, not to scale", "t2")
    s.rect(20, 60, 560, 380, "box")
    # ribbon
    s.rect(40, 210, 70, 80, "print", 3)
    s.text(40, 305, "web clamp", "sm")
    ys_r = [226, 243, 260, 277]
    for y in ys_r:
        s.line(110, y, 150, y, "wire")
    # odd plane spreads 3.4 -> 5.0 (drawn 2 of 4 for a T4 row pair plus a third)
    ys_st = [180, 230, 280, 330, 380]
    for i, y in enumerate([ys_r[0], ys_r[2]]):
        s.pline([(150, y), (230, ys_st[i + 1] - 0), (330, ys_st[i + 1])], "wire")
    s.text(40, 196, "odd plane: 3.4 -> 5.0 mm", "sm")
    s.text(40, 330, "even plane folded back below", "sm")
    s.rect(230, 170, 30, 220, "print", 3)
    s.text(206, 405, "V-tooth comb", "sm")
    # lower shoe with pockets
    s.rect(330, 160, 150, 240, "steel")
    for i, y in enumerate(ys_st):
        s.rect(338, y - 6, 34, 12, "dark")               # anvil
        s.rect(372, y - 7, 60, 14, "bg")                 # pocket
        s.rect(380, y - 6, 48, 12, "contact") if i in (1, 2) else None
    s.text(330, 150, "anvils (one ground block)", "sm")
    s.text(372, 420, "keyed pockets, lance relief", "sm")
    s.rect(434, 162, 8, 236, "bought", 1)
    s.text(446, 176, "gate", "sm")
    # housing nest
    s.rect(480, 200, 60, 150, "print", 3)
    s.rect(486, 210, 44, 130, "steel")
    for j in range(7):
        s.rect(488, 214 + j * 18, 12, 10, "bg")
    s.text(484, 368, "XHP in nest", "sm")
    s.move(460, 430, 500, 430)
    s.text(380, 452, "pusher drives the half-row into alternate cavities", "sm")
    # right: section
    X = 600
    s.text(X, 76, "Section across the stations", "t2")
    s.rect(X, 86, 260, 300, "box")
    s.rect(X + 20, 110, 220, 40, "steel")
    s.text(X + 26, 104, "upper shoe", "sm")
    s.rect(X + 30, 150, 200, 30, "dark")
    s.text(X + 34, 170, "one EDM crimper plate, 5 profiles", "sm")
    for i in range(5):
        s.rect(X + 40 + i * 40, 176, 14, 8, "bg")
    s.rect(X + 20, 260, 220, 50, "steel")
    s.text(X + 26, 330, "lower shoe, anvil block", "sm")
    s.rect(X + 22, 190, 16, 70, "steel")
    s.rect(X + 222, 190, 16, 70, "steel")
    s.text(X + 40, 250, "stop blocks set height", "sm")
    s.force(X + 130, 92, X + 130, 108)
    s.lines(X + 10, 352, ["webs between channels:", "5.0 - 2.0 = 3.0 mm", "(separate crimpers: 0.6-1.5)"], "sm", 12)
    s.lines(30, 470, ["Rows per unit: T4 2+2 (x5), J1 5+4, J2 2+3, J4 4+3, J6 3+2, J7 4+3 -> 20 strokes, 53 crimps; 68 % in rows of three or fewer.",
                      "Force at the stop: row of 2 1.6-4.9 kN, row of 3 2.3-7.3 kN (1 t arbor press); rows of 4-5 need the central estimate or the shop press."], "t2", 16)
    legend(s, 30, 530)
    s.text(30, 560, "f5 (cassette, stops, any press) x change-the-question c1 (planes, half-rows at twice the pitch, two pushes).", "t2")
    s.save(os.path.join(HERE, "f5b-half-row-cassette.svg"))


# ---------------------------------------------------------------- f6
def f6():
    s = Svg(880, 600, "f6 two blades two drives, schematic",
            "Conductor crimper on the knee and a separate insulation crimper with its own small drive, "
            "with force curves for each blade and the insulation-height window between cut and cavity.")
    s.text(20, 28, "f6  Two blades, two drives: the copper to its stop, the jacket to its own height", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    # left: front view along the wire, blades side by side (seen from the side of the press)
    s.rect(20, 60, 400, 330, "box")
    s.text(30, 78, "Side view along the wire: two blades in one slot", "t2")
    s.rect(80, 90, 80, 30, "steel")
    s.text(86, 108, "knee", "sm")
    s.rect(95, 120, 50, 110, "steel")
    s.text(40, 180, "conductor", "sm")
    s.text(40, 193, "crimper", "sm")
    s.rect(145, 140, 40, 110, "steel")
    s.text(190, 180, "insulation crimper", "sm")
    s.text(190, 193, "slides on the conductor", "sm")
    s.text(190, 206, "blade's face", "sm")
    s.rect(260, 110, 90, 40, "bought", 3)
    s.lines(266, 126, ["NEMA 17 + lever", "up to 150 N, load cell"], "sm", 12)
    s.pline([(260, 135), (185, 145)], "ln")
    s.rect(210, 225, 40, 20, "steel")
    s.text(254, 240, "motor-set wedge = insulation height", "sm")
    # contact below
    s.rect(95, 262, 50, 18, "contact")
    s.rect(145, 250, 40, 30, "contact")
    s.line(40, 272, 300, 272, "wire")
    s.rect(95, 282, 50, 28, "dark")
    s.rect(145, 282, 40, 28, "dark")
    s.text(96, 325, "anvils", "sm")
    s.lines(30, 350, ["Order: capture both; thread; conductor crimp (knee);",
                      "then insulation blade alone; silhouette; tab cut;",
                      "a track section drops ~3 mm; bend DOWN and look."], "sm", 13)
    # right top: force curves
    X = 440
    s.rect(X, 60, 420, 190, "box")
    s.text(X + 10, 78, "What each blade's load cell sees (shape only)", "t2")
    s.line(X + 40, 230, X + 400, 230, "ln")
    s.line(X + 40, 230, X + 40, 90, "ln")
    s.text(X + 400, 245, "stroke", "sm", "end")
    s.pline([(X + 40, 228), (X + 150, 215), (X + 250, 205), (X + 300, 190), (X + 330, 140), (X + 345, 95)], "force")
    s.text(X + 200, 104, "conductor: kN at its bottom", "sm")
    s.pline([(X + 40, 229), (X + 120, 222), (X + 220, 220), (X + 280, 214), (X + 300, 211)], "move")
    s.pline([(X + 300, 211), (X + 310, 170)], "force")
    s.lines(X + 60, 150, ["insulation (own load cell):", "wings, tens of N; silicone slope,", "1-13 N; tips on copper:", "20-500x steeper"], "sm", 12)
    # right bottom: window
    s.rect(X, 262, 420, 128, "box")
    s.text(X + 10, 280, "Insulation crimp height window on 1.7 mm silicone [estimate]", "t2")
    x0, x1 = X + 40, X + 400
    s.line(x0, 330, x1, 330, "ln")
    for i, h in enumerate([1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]):
        xx = x0 + i * (x1 - x0) / 8
        s.line(xx, 326, xx, 334, "ln")
        s.text(xx, 348, f"{h:.1f}", "sm", "middle")
    s.rect(x0, 300, 3 * (x1 - x0) / 8, 22, "force")
    s.text(x0 + 4, 296, "tips cut the jacket", "sm")
    s.rect(x0 + 3 * (x1 - x0) / 8, 300, 2 * (x1 - x0) / 8, 22, "print")
    s.text(x0 + 3 * (x1 - x0) / 8 + 4, 296, "window", "sm")
    s.rect(x0 + 7 * (x1 - x0) / 8, 300, 1 * (x1 - x0) / 8, 22, "bought")
    s.text(x0 + 7 * (x1 - x0) / 8 - 20, 296, "over 2.4 envelope", "sm")
    s.text(x0 + (x1 - x0) / 8, 368, "1.80 = clone spec (PVC-class wire)", "sm")
    s.text(x0 + 4, 382, "height in mm, at 1.8-1.9 mm wide; bounds modelled, not measured", "sm")
    s.lines(30, 420, ["On this wire the insulation crimp is not a pull-out grip (strands slip in the jacket at 0.4-9 N).",
                      "Silicone pushes back 1-13 N against 30-130 N of wing forming, so the jacket must be set by position, not force.",
                      "Checks: silhouette height and width; bend 60-90 deg DOWN over a 2 mm (diameter) pin, so the wing tips on top are on the",
                      "outside (strain 0.46; a cut gapes 0.23-0.56 mm), and look for tin on black; jacket tug with the camera on the insulation",
                      "edge. Continuity cannot see a cut at the insulation barrel. Bending up would close the cut while the camera looks."], "t2", 16)
    legend(s, 30, 530)
    s.text(30, 560, "Blades: an OTP knife set already has separate conductor and insulation crimpers, or EDM (f7).", "t2")
    s.save(os.path.join(HERE, "f6-two-blades.svg"))


# ---------------------------------------------------------------- f7
def f7():
    s = Svg(880, 560, "f7 die cartridges from four steel sources, schematic",
            "One small press with a pocket; four interchangeable die cartridges whose dies come from "
            "SN jaws, an OTP knife set, EDM plates and ground stock.")
    s.text(20, 28, "f7  Where the steel comes from: die cartridges, closed by any press", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    # press
    s.rect(30, 70, 200, 300, "box")
    s.rect(50, 90, 160, 30, "steel")
    s.rect(60, 120, 20, 200, "steel")
    s.rect(110, 120, 40, 50, "bought", 3)
    s.text(96, 186, "pusher +", "sm")
    s.text(96, 198, "disc springs", "sm")
    s.force(130, 172, 130, 214)
    s.rect(90, 300, 100, 30, "steel")
    s.text(92, 346, "bed pocket, two dowels", "sm")
    s.rect(100, 220, 80, 80, "steel", 3)
    s.text(108, 262, "cartridge", "sm")
    s.lines(40, 390, ["any pusher: f3's knee, a 1 t arbor", "press, the shop press, an eccentric"], "sm", 12)
    # four cartridges
    names = [("SN jaws", ["$9.99, days", "today's profile", "height: jaws, if they bottom", "insulation step fixed", "one nest per cartridge"]),
             ("OTP knife set", ["~$30-100, weeks [est.]", "industrial XH profile", "separate CH / IH blades", "narrow: heads, gangs", "some vendor's contact"]),
             ("EDM plates", ["~$50-200, weeks [est.]", "any profile you draw", "gang plates, 2.9 mm", "narrow dies, overlap", "first drawing is a guess"]),
             ("Ground stock", ["anvil = stock on edge", "width +/-0.013 mm", "lap the top, harden O1", "laser-cut plates for", "holders, stops (+/-0.13)"])]
    for i, (n, rows) in enumerate(names):
        x = 250 + i * 155
        s.rect(x, 70, 145, 300, "box")
        s.text(x + 8, 90, n, "h")
        s.rect(x + 20, 105, 105, 16, "steel")
        s.rect(x + 25, 121, 8, 70, "steel")
        s.rect(x + 112, 121, 8, 70, "steel")
        s.rect(x + 55, 121, 35, 28, "dark")
        s.rect(x + 55, 160, 35, 22, "dark")
        s.rect(x + 20, 191, 105, 16, "steel")
        s.lines(x + 8, 232, rows, "sm", 14)
    s.lines(30, 430, ["Every cartridge: base and top on two ground pins, return spring, its own stop block, same outer shape and button.",
                      "Stop in the cartridge, spring in the pusher. A 0.001 mm indicator across the plates reads re-touch height.",
                      "A single die's channel may be +/-0.05 mm if its width is measured and its height set for that width (W x H is the",
                      "compaction); a gang plate's stations must match to ~0.01; an anvil ~+/-0.02 (ground stock); holders and stops",
                      "~+/-0.15 (laser cutting). Printed parts never make a die face."], "t2", 16)
    legend(s, 30, 546)
    s.save(os.path.join(HERE, "f7-die-cartridges.svg"))


# ---------------------------------------------------------------- f8
def f8():
    s = Svg(880, 640, "f8 narrow press at the housing mouth, schematic",
            "Side section: the contact's box sits in its housing cavity, the barrels stand out over an "
            "anvil with a lance relief; a narrow crimper in a steel C bottoms on shoulders below the floor. "
            "Inset: end view of the 2.9 mm crimper between neighbour wires at 2.5 mm pitch.")
    s.text(20, 28, "f8  A narrow press at the housing's mouth (into-the-housing i2 x force-and-form f3/f4)", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    s.rect(20, 60, 500, 400, "box")
    s.text(30, 78, "Side section along the wire", "t2")
    # housing
    s.rect(40, 180, 130, 110, "print", 2)
    s.rect(40, 214, 130, 40, "bg")
    s.text(44, 306, "XHP nest: fixed in Y,", "sm")
    s.text(44, 319, "floats in X and Z", "sm")
    s.rect(120, 216, 50, 36, "contact")                      # box in cavity
    s.text(90, 205, "box 1.4-2.4 mm in", "sm")
    s.rect(170, 238, 8, 14, "contact")                       # transition
    s.pline([(166, 252), (180, 266)], "ln")
    s.text(128, 350 - 60, "", "sm")
    s.rect(186, 228, 36, 24, "contact")                      # cond barrel
    s.rect(236, 212, 30, 40, "contact")                      # ins barrel
    s.line(200, 240, 480, 240, "wire")
    # anvil block with shoulders
    s.rect(190, 252, 90, 50, "steel")
    s.rect(182, 262, 8, 40, "bg")
    s.text(196, 316, "anvil: front stops behind the lance;", "sm")
    s.text(196, 329, "shoulders below the floor", "sm")
    s.text(150, 278, "lance", "sm", "end")
    s.move(290, 262, 290, 292)
    s.text(296, 284, "anvil drops 1.5 mm", "sm")
    # crimper
    s.rect(186, 130, 36, 90, "dark")
    s.rect(236, 140, 30, 64, "dark")
    s.text(60, 124, "narrow stepped crimper", "sm")
    s.pline([(170, 121), (186, 130)], "ln")
    # C
    s.rect(330, 90, 170, 26, "steel")
    s.rect(474, 90, 26, 260, "steel")
    s.rect(330, 324, 170, 26, "steel")
    s.pline([(330, 103), (222, 103), (222, 130)], "ln")
    s.text(360, 140, "knee in a steel C (f4)", "sm")
    s.force(290, 106, 290, 128)
    # saddle
    s.path("M 330 240 Q 400 200 470 240", "wire")
    s.text(380, 196, "saddle hump stores ~5 mm", "sm")
    s.lines(30, 350, ["Crimp 0.2-0.3 mm from the PA6 face; the die never touches it.",
                      "Then cut the tab, drop the anvil, push the contact home (blade),",
                      "5 N pull-back, step 2.5 mm (5.0 past J2's empty cavity 3).",
                      "A comb 3-5 mm behind the rear face centres the seated wires."], "sm", 13)
    # inset end view
    X = 540
    s.rect(X, 60, 320, 400, "box")
    s.text(X + 10, 78, "End view at the crimp (scale ~40 px/mm)", "t2")
    cx, fy = X + 160, 330
    k = 40
    for dx in (-2.5, 2.5):
        s.circle(cx + dx * k, fy - 1.05 * k, 0.85 * k, "wirefill")
    s.text(cx - 2.5 * k, fy - 2.3 * k, "neighbour", "sm", "middle")
    s.text(cx + 2.5 * k, fy - 2.3 * k, "neighbour", "sm", "middle")
    s.rect(cx - 1.45 * k, fy - 3.4 * k, 2.9 * k, 2.55 * k, "dark")          # crimper body and roof
    s.rect(cx - 1.45 * k, fy - 0.85 * k, 0.7 * k, 1.05 * k, "dark")          # left wall down to shoulder
    s.rect(cx + 0.75 * k, fy - 0.85 * k, 0.7 * k, 1.05 * k, "dark")          # right wall
    s.rect(cx - 0.75 * k, fy - 0.85 * k, 1.5 * k, 0.85 * k, "contact")       # crimp
    s.rect(cx - 0.75 * k, fy, 1.5 * k, 0.2 * k, "steel")                     # anvil top
    s.rect(cx - 1.9 * k, fy + 0.2 * k, 3.8 * k, 1.2 * k, "steel")            # anvil block with shoulders
    s.text(cx + 2.0 * k, fy + 0.8 * k, "shoulders", "sm")
    s.line(X + 20, fy, X + 300, fy, "thin")
    s.text(X + 22, fy - 4, "floor", "sm")
    s.lines(X + 12, fy + 64, ["2.9 mm crimper: 1.5 channel + 2 x 0.7 walls;", "3.30 mm free at the neighbours' equator,",
                              "0.00 to +0.08 mm a side net of the wires' play;", "walls land on anvil-block shoulders below",
                              "the floor, where there are 5 mm of room."], "sm", 12)
    s.lines(30, 488, ["Decisive unknown: the transition t from box rear to conductor barrel front. With t >= ~0.8 mm an anvil can stop behind the lance",
                      "and still carry the barrel; below ~0.7 mm the entry must fold the lance first. One side-on photo of a kit contact settles it."], "t2", 16)
    legend(s, 30, 560)
    s.text(30, 590, "Walls of 0.3-0.4 mm crack at 2,200-9,450 MPa; 0.7-0.85 mm walls run 490-1,740 MPa (k = 0.3-0.5).", "t2")
    s.save(os.path.join(HERE, "f8-housing-mouth.svg"))


if __name__ == "__main__":
    # f5b is drawn as it now stands by make_sketches_w3.py
    f4b()
    f6()
    f7()
    f8()
