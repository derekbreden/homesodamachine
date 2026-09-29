"""Schematic sketches for the force-and-form ideas f1-f5. Not to scale.

Run: python3 make_sketches.py  (writes f1-...svg to f5-...svg beside this file)
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


# ---------------------------------------------------------------- f1
def f1():
    s = Svg(880, 590, "f1 motorised ratchet crimper, schematic",
            "A stock ratchet crimper lies flat in a printed cradle; a linear actuator with a load "
            "cell closes its handle; the conductor hangs down through a funnel into the XH nest.")
    s.text(20, 28, "f1  The hand tool is the press: a ratchet crimper closed by a slow actuator", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    # --- left panel: top view
    s.text(30, 76, "Top view (tool lies flat on a steel plate)", "t2")
    s.rect(30, 86, 420, 330, "box")
    s.rect(60, 180, 90, 90, "steel", 8)                       # head
    s.rect(62, 218, 86, 14, "dark")                           # jaw line
    s.rect(96, 219, 10, 12, "contact")                        # XH nest
    s.text(60, 172, "jaws (EDM-cut, SN-2549)", "sm")
    s.poly([(150, 250), (420, 318), (420, 336), (150, 268)], "steel")   # fixed handle
    s.poly([(150, 196), (410, 150), (410, 168), (150, 214)], "steel")   # moving handle
    s.rect(250, 262, 150, 90, "print", 6)                      # cradle
    s.text(260, 370, "printed cradle clamps", "sm")
    s.text(260, 383, "the fixed handle", "sm")
    s.rect(370, 96, 44, 36, "bought", 3)                      # actuator body
    s.rect(386, 132, 12, 10, "dark")                          # load cell
    s.line(392, 142, 392, 158, "ln")
    s.force(392, 146, 392, 162)
    s.lines(236, 100, ["linear actuator", "(12 V, 500-1500 N) or", "NEMA 17 lead screw"], "sm", 12)
    s.text(300, 142, "load cell", "sm")
    s.move(430, 180, 430, 300)
    s.lines(434, 200, ["handle", "closes"], "sm", 12)
    s.lines(40, 300, ["The tool's own toggle and", "ratchet make the force; the",
                      "jaws bottom, so crimp height", "is the tool's."], "sm", 13)
    # --- right panel: section through the nest
    X = 670
    s.text(480, 76, "Section through the XH nest (wire vertical)", "t2")
    s.rect(480, 86, 380, 330, "box")
    s.rect(X - 50, 100, 100, 26, "bought", 3)
    s.text(X, 117, "ribbon clamp", "sm", "middle")
    s.text(X + 56, 106, "X/Z carriage", "sm")
    s.move(X + 60, 118, X + 110, 118, both=True)
    s.move(X - 62, 98, X - 62, 138, both=True)
    s.line(X, 126, X, 262, "wire")
    for dx in (-30, -15, 15, 30):
        s.pline([(X + dx * 0.3, 126), (X + dx * 0.4, 150), (X + dx * 2.6, 205)], "wire")
    s.rect(X - 50, 150, 100, 10, "print", 3)
    s.text(X + 56, 159, "fork fans the others aside", "sm")
    s.poly([(X - 26, 222), (X + 26, 222), (X + 8, 250), (X - 8, 250)], "print")
    s.text(X + 32, 238, "printed funnel", "sm")
    s.lines(488, 222, ["tip depth = carriage Z,", "zeroed on the tip by the", "camera before each thread"], "sm", 11)
    s.rect(484, 252, X - 8 - 484, 44, "steel")
    s.rect(X + 8, 252, 856 - X - 8, 44, "steel")
    s.force(840, 274, X + 16, 274)
    s.text(490, 290, "fixed jaw", "sm")
    s.text(850, 290, "moving jaw", "sm", "end")
    s.rect(X - 6, 256, 12, 36, "contact")
    s.rect(X - 7, 292, 14, 30, "contact")
    s.rect(X - 60, 296, 120, 10, "print", 2)
    s.rect(X - 8, 296, 16, 10, "bg")
    s.lines(488, 324, ["keyed flap (printed): the box", "drops through a slot notched",
                       "for the lance; the shoulder", "sets the axial position"], "sm", 12)
    s.lines(X + 20, 330, ["contact stands box-down,", "barrels up, open side", "facing the moving jaw"], "sm", 12)
    s.lines(30, 444, ["Per crimp: 1 contact dropped into the flap (person or chute)   2 actuator to the first ratchet click: wings captured",
                      "3 carriage lowers the conductor through the funnel   4 actuator completes; ratchet releases   5 carriage lifts it out",
                      "Logged every crimp: actuator force vs travel (the crimp curve seen through the tool's linkage)."], "t2", 16)
    legend(s, 30, 516)
    s.lines(30, 546, ["Hands back: loading one contact per crimp (or a chute), stripping, insertion.",
                      "Branch f1b puts JST WC-110 (flap locator and wire stop built in) in the same cradle."], "t2", 15)
    s.save(os.path.join(HERE, "f1-motorised-ratchet.svg"))


# ---------------------------------------------------------------- f2
def f2():
    s = Svg(880, 560, "f2 slow crank press for a mini-applicator, schematic",
            "A steel C-frame press with a stepper and worm gearbox turning an eccentric crank; "
            "the ram drives a bought side-feed applicator; a ribbon carriage lays each conductor "
            "into the waiting contact.")
    s.text(20, 28, "f2  Build the press, buy the applicator: a crank press turning at ~2 rpm", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    s.text(30, 76, "Front view", "t2")
    s.text(300, 56, "steel C-frame (k ~ tens to hundreds of kN/mm)", "sm")
    s.rect(470, 62, 36, 390)          # column
    s.rect(200, 62, 306, 32)          # top arm
    s.rect(110, 450, 430, 26)         # base
    s.rect(262, 94, 26, 12, "steel")  # bearing block
    s.rect(330, 104, 116, 40, "bought", 3)
    s.lines(336, 120, ["NEMA 23 + 30:1 worm", "(self-locking, 20 N*m)"], "sm", 12)
    s.line(297, 120, 330, 120, "ln")
    s.circle(275, 124, 22, "steel")
    s.circle(275, 124, 3, "dark")
    s.circle(288, 138, 4, "dark")
    s.line(288, 138, 275, 176, "ln")
    s.line(289, 139, 276, 177, "ln")
    s.text(200, 118, "eccentric", "sm")
    s.circle(236, 146, 5, "bought")
    s.text(160, 150, "angle sensor", "sm")
    s.rect(236, 176, 14, 52, "steel")
    s.rect(300, 176, 14, 52, "steel")
    s.rect(254, 176, 42, 48, "steel")
    s.text(320, 196, "ram in guide", "sm")
    s.rect(262, 224, 26, 8, "dark")
    s.text(320, 230, "T-slot grips the shank collar", "sm")
    s.force(275, 160, 275, 174)
    s.rect(266, 232, 18, 34, "steel")
    s.rect(190, 262, 170, 150, "steel", 4)
    s.text(196, 280, "OTP side-feed applicator", "sm")
    s.text(196, 292, "(bought)", "sm")
    s.rect(262, 294, 26, 16, "dark")
    s.rect(266, 320, 18, 18, "dark")
    s.rect(258, 311, 34, 9, "contact")
    s.lines(196, 362, ["feed finger, anvil, crimpers,", "tab cut-off, crimp-height dial",
                       "(JST MKS-L: 0.05 mm per step)"], "sm", 12)
    s.rect(220, 412, 110, 12, "bought", 2)
    s.text(336, 422, "button load cell", "sm")
    s.rect(190, 424, 170, 26, "steel")
    s.circle(80, 300, 44, "bought")
    s.text(80, 356, "SXH strip reel", "sm", "middle")
    for i in range(6):
        s.rect(128 + i * 22, 311, 12, 9, "contact")
    s.line(124, 320, 258, 320, "ln")
    # inset: side view at the anvil
    s.text(560, 76, "Side view at the anvil (wire axis in the page)", "t2")
    s.rect(560, 86, 300, 330, "box")
    s.rect(640, 150, 60, 50, "steel")
    s.text(706, 172, "crimpers (ram up)", "sm")
    s.rect(640, 256, 60, 40, "steel")
    s.text(600, 280, "anvil", "sm")
    s.rect(630, 236, 18, 20, "contact")
    s.path("M648,236 L648,256 L696,256 L696,236", "ln")
    s.poly([(648, 238), (648, 256), (696, 256), (696, 238), (693, 238), (693, 252), (651, 252), (651, 238)], "contact")
    s.line(662, 246, 694, 246, "strand")
    s.line(694, 246, 790, 246, "wire")
    s.rect(736, 232, 10, 28, "print", 2)
    s.text(700, 222, "fork holds one conductor", "sm")
    for dy in (-60, -44):
        s.pline([(800, 240), (790, 230), (770, 246 + dy)], "wire")
    s.rect(790, 228, 50, 38, "bought", 3)
    s.text(850, 284, "ribbon carriage X/Y/Z", "sm", "end")
    s.move(830, 318, 710, 318)
    s.lines(575, 350, ["the conductor is laid in from above-rear", "while the ram is up; pre-feed means",
                       "the next contact is already on the anvil.", "The applicator's wire-hold spring and",
                       "stripper hold it as the crimpers descend."], "sm", 13)
    s.lines(30, 500, ["Per crimp: carriage lays conductor i into the waiting contact -> one crank revolution (crimp, cut-off, feed next)",
                      "-> carriage lifts and indexes. Logged: force (load cell) vs ram height (crank angle). BDC: 1 deg off = 3-4 um."], "t2", 15)
    legend(s, 30, 546)
    s.save(os.path.join(HERE, "f2-crank-applicator-press.svg"))


# ---------------------------------------------------------------- f3
def f3():
    s = Svg(880, 540, "f3 knee micro-press, schematic",
            "A palm-sized steel die set on two guide pins, closed by a toggle whose straight "
            "position is bottom of stroke, pushed by a small stepper lead screw; a load cell under "
            "the anvil and a 0.001 mm indicator across the dies measure every crimp.")
    s.text(20, 28, "f3  Knee micro-press: the die is the locator, the gauge is the micrometer", "h")
    s.text(20, 46, "schematic, not to scale; side view, wire axis left-right", "t2")
    s.rect(106, 80, 298, 26)
    s.text(410, 97, "bridge", "sm")
    s.rect(120, 106, 12, 222)
    s.rect(378, 106, 12, 222)
    s.rect(106, 176, 298, 28)
    s.lines(410, 188, ["punch holder on guide", "pins and bushings"], "sm", 12)
    for (x1, y1, x2, y2) in ((250, 106, 268, 141), (268, 141, 250, 176)):
        s.line(x1, y1, x2, y2, "ln")
        s.line(x1 + 2, y1, x2 + 2, y2, "ln")
    for (x, y) in ((250, 106), (268, 141), (250, 176)):
        s.circle(x, y, 5, "dark")
    s.lines(150, 136, ["knee (toggle)", "straight = BDC"], "sm", 12)
    s.rect(448, 124, 56, 34, "bought", 3)
    s.text(448, 118, "NEMA 17 lead screw (or servo)", "sm")
    s.line(448, 141, 272, 141, "ln")
    s.force(360, 148, 292, 148)
    s.text(300, 166, "60-160 N", "sm")
    s.rect(236, 204, 28, 32, "steel")
    s.text(186, 224, "crimpers", "sm")
    s.rect(236, 276, 28, 24, "steel")
    s.text(200, 294, "anvil", "sm")
    s.poly([(236, 300), (300, 300), (300, 308), (236, 314)], "steel")
    s.text(306, 306, "wedge = crimp-height dial", "sm")
    s.rect(230, 314, 46, 12, "bought", 2)
    s.text(306, 324, "load cell under the anvil", "sm")
    s.rect(212, 262, 20, 14, "contact")
    s.rect(232, 266, 40, 10, "contact")
    s.rect(150, 236, 16, 90, "bought", 2)
    s.line(158, 236, 158, 204, "ln")
    s.lines(26, 250, ["0.001 mm", "indicator,", "holder to", "base, beside", "the dies"], "sm", 12)
    s.rect(90, 326, 330, 46)
    s.rect(272, 278, 36, 8, "print", 1)
    s.text(90, 390, "behind the dies: side-feed strip track (printed), steel pilot pin, tab shear", "sm")
    s.line(272, 270, 560, 270, "wire")
    s.line(250, 270, 272, 270, "strand")
    for dy in (-34, -18, 18, 34):
        s.pline([(600, 270 + dy * 0.2), (580, 270 + dy * 0.3), (556, 270 + dy)], "wire")
    s.rect(560, 248, 70, 44, "bought", 3)
    s.text(560, 242, "ribbon carriage", "sm")
    s.move(556, 310, 470, 310)
    s.text(470, 326, "threads axially after capture", "sm")
    s.rect(520, 190, 34, 22, "bought", 3)
    s.lines(560, 198, ["camera: rear view", "into the barrel"], "sm", 12)
    s.line(520, 208, 290, 266, "thin")
    s.lines(30, 422, ["1 strip advances; pilot pin fixes the contact   2 knee to capture height (wings in the punch), pause   3 shear the tab",
                      "4 camera: barrel open and square?   5 carriage threads the conductor to depth; camera: strands inside?",
                      "6 straighten the knee; log force vs indicator gap   7 back off, re-touch at 10 N: crimp height",
                      "8 carriage pulls to a proof load against a fork behind the barrel   9 open, lift out"], "t2", 16)
    legend(s, 30, 520)
    s.save(os.path.join(HERE, "f3-knee-micropress.svg"))


# ---------------------------------------------------------------- f4
def f4():
    s = Svg(880, 580, "f4 crimp head goes to the wire, schematic",
            "The ribbon end lies still in a printed comb board; a light steel C-frame crimp head on "
            "an XYZ gantry picks a contact from a strip, threads it onto each stripped conductor "
            "and crimps with the force closed inside the head.")
    s.text(20, 28, "f4  The head goes to the wire: the ribbon never moves", "h")
    s.text(20, 46, "schematic, not to scale; top view", "t2")
    # board
    s.rect(40, 110, 300, 290, "print", 6)
    s.text(50, 128, "ribbon board (printed): clamp + comb", "sm")
    s.rect(40, 210, 120, 80, "bought")
    s.pline([(40, 250), (160, 250)], "thin")
    s.text(50, 305, "ribbon clamped", "sm")
    ys = [190, 220, 250, 280, 310]
    for y in ys:
        s.pline([(160, 250 + (y - 250) * 0.2), (230, y), (330, y)], "wire")
        s.line(330, y, 350, y, "strand")
    s.rect(300, 170, 18, 160, "print")
    s.text(262, 350, "comb slots at a", "sm")
    s.text(262, 362, "spread pitch (~5 mm)", "sm")
    # contact dispenser
    s.rect(470, 80, 300, 26, "print", 3)
    for i in range(8):
        s.rect(480 + i * 34, 86, 14, 14, "contact")
    s.text(470, 74, "contact strip in a printed track; fixed tab shear at the end", "sm")
    # gantry rails
    s.line(360, 140, 840, 140, "thin")
    s.text(700, 134, "gantry rail (X; Y and Z ride on it)", "sm")
    # head at conductor 3
    s.rect(352, 236, 96, 28, "steel", 4)
    s.rect(346, 244, 10, 12, "contact")
    s.text(360, 230, "C-frame head", "sm")
    s.move(620, 110, 470, 230)
    s.lines(560, 190, ["1 pick: nest under lead contact,", "close to capture, pull through shear"], "sm", 12)
    s.move(470, 262, 452, 262)
    s.lines(470, 290, ["2 approach along the conductor axis:", "the conductor threads into the barrel",
                       "3 crimp: force stays inside the head", "4 open, back off, next conductor"], "sm", 13)
    # inset: head side view
    s.text(560, 360, "Head, side view", "t2")
    s.rect(560, 370, 290, 120, "box")
    s.poly([(610, 380), (800, 380), (800, 480), (610, 480), (610, 462), (780, 462), (780, 398), (610, 398)], "steel")
    s.rect(610, 398, 16, 22, "steel")
    s.rect(610, 440, 16, 22, "steel")
    s.rect(606, 426, 24, 8, "contact")
    s.line(570, 430, 606, 430, "wire")
    s.circle(700, 410, 4, "dark")
    s.circle(712, 425, 4, "dark")
    s.line(626, 410, 700, 410, "ln")
    s.line(700, 410, 712, 425, "ln")
    s.rect(730, 402, 44, 26, "bought", 3)
    s.lines(560, 506, ["knee + NEMA 17 inside the C; load cell under the anvil;", "the C closes the crimp force on itself"], "sm", 12)
    s.lines(40, 430, ["Hands back: laying the split, stripped ribbon into the comb;",
                      "insertion (the same gantry could carry an insertion nose).",
                      "Gantry sees positioning loads only (a few N)."], "t2", 15)
    legend(s, 40, 565)
    s.save(os.path.join(HERE, "f4-head-to-wire.svg"))


# ---------------------------------------------------------------- f5
def f5():
    s = Svg(900, 560, "f5 die cassette in the shop press, schematic",
            "A steel die cassette with one station per conductor, spring-open on two guide posts "
            "with stop blocks; loaded and inspected under a camera, then pushed to its stops by "
            "the idle 12-ton shop press.")
    s.text(20, 28, "f5  Die cassette: load and look at leisure, then one push per ribbon end", "h")
    s.text(20, 46, "schematic, not to scale; front view (wire axis into the page)", "t2")

    def cassette(x0, y0, closed):
        gap = 0 if closed else 26
        s.rect(x0, y0 + 110, 300, 30)                 # lower shoe
        s.rect(x0 + 10, y0 + 20, 14, 120)             # posts
        s.rect(x0 + 276, y0 + 20, 14, 120)
        s.rect(x0, y0 + 40 - gap, 300, 30)            # upper shoe
        s.rect(x0 + 34, y0 + 90, 18, 20, "dark")      # stop blocks
        s.rect(x0 + 248, y0 + 90, 18, 20, "dark")
        for i in range(5):
            cx = x0 + 80 + i * 36
            s.rect(cx - 7, y0 + 96, 14, 14, "steel")              # anvil
            s.rect(cx - 8, y0 + 70 - gap, 16, 14, "steel")         # crimper
            if closed:
                s.rect(cx - 6, y0 + 86, 12, 10, "contact")
                s.circle(cx, y0 + 91, 3, "wirefill")
            else:
                s.path(f"M{cx-9},{y0+80} L{cx-7},{y0+96} L{cx+7},{y0+96} L{cx+9},{y0+80}", "ln")
                s.poly([(cx - 9, y0 + 80), (cx - 7, y0 + 96), (cx + 7, y0 + 96), (cx + 9, y0 + 80),
                        (cx + 6, y0 + 80), (cx + 5, y0 + 93), (cx - 5, y0 + 93), (cx - 6, y0 + 80)], "contact")
                s.circle(cx, y0 + 89, 3.5, "wirefill")
        if not closed:
            for xs in (x0 + 17, x0 + 283):
                s.path(f"M{xs-6},{y0+72} l12,6 l-12,6 l12,6 l-12,6", "ln")
    # loading station
    s.text(40, 80, "Loading station (bench, camera above)", "t2")
    s.rect(160, 92, 40, 26, "bought", 3)
    s.text(206, 106, "ELP camera: every conductor in its U?", "sm")
    s.line(180, 118, 180, 150, "thin")
    cassette(40, 120, closed=False)
    s.lines(40, 290, ["strip segment of N contacts on steel pilot pins", "(station pitch = the strip's pitch)",
                      "ribbon fanned into a printed comb, then flush-cut",
                      "and stripped at the comb face (edges on one line)",
                      "each anvil insulated: the far end names its conductor",
                      "springs hold the upper shoe open"], "sm", 13)
    # press
    s.text(470, 80, "In the idle 12-ton shop press", "t2")
    s.rect(470, 90, 26, 330)
    s.rect(824, 90, 26, 330)
    s.rect(470, 90, 380, 24)
    s.rect(470, 396, 380, 24)
    s.rect(630, 114, 60, 70, "bought", 3)
    s.text(696, 150, "bottle-jack ram", "sm")
    s.force(660, 186, 660, 200)
    cassette(510, 180, closed=True)
    s.rect(560, 322, 200, 12, "bought", 2)
    s.rect(540, 334, 240, 62, "steel")
    s.lines(548, 356, ["press bed plates; the 5 t load cell above", "(or the jack's gauge) reads summed force"], "sm", 12)
    s.lines(504, 130, ["pump until the shoes", "meet the stop blocks:", "the stops set crimp", "height; the press", "only pushes"], "sm", 12)
    s.lines(40, 450, ["One stroke crimps a whole ribbon end (3-5 conductors, 5-12 kN; the press has ~118 kN).",
                      "A floating shear under the carrier cuts the tabs in the same stroke (or a second); each conductor proof-pulled at the comb face.",
                      "Hands back: loading strip and ribbon into the cassette, pumping (or a motorised screw), insertion."], "t2", 15)
    legend(s, 40, 540)
    s.save(os.path.join(HERE, "f5-cassette-gang.svg"))


if __name__ == "__main__":
    # f1, f3 and f4 are drawn as they now stand by make_sketches_w3.py
    for f in (f2, f5):
        f()
    print("wrote f2 and f5 sketches")
