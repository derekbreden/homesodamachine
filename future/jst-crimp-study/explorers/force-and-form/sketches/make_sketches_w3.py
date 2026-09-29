"""Schematic sketches for force-and-form as the ideas stand: f1, f3, f4 (top view), f5b,
f9b and f2c. Not to scale.

Run: python3 make_sketches_w3.py  (writes the SVGs beside this file)
f2, f5 come from make_sketches.py; f4b, f6, f7, f8 from make_sketches_w2.py.
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
    s = Svg(880, 640, "f1 motorised ratchet crimper, schematic",
            "A stock ratchet crimper lies flat in a printed cradle; a linear actuator with a load cell "
            "closes its handle. A swinging keyed flap loads a contact outside the jaws and lifts it into "
            "the nest; the jaws close short of the first ratchet tooth; the camera measures the tip; the "
            "carriage lowers the conductor; after the crimp a neck blade reacts a 20 N pull.")
    s.text(20, 28, "f1  The hand tool is the press: a ratchet crimper closed by a slow actuator", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    # --- left panel: top view
    s.text(30, 76, "Top view (tool lies flat on a steel plate)", "t2")
    s.rect(30, 86, 420, 330, "box")
    s.rect(60, 180, 90, 90, "steel", 8)
    s.rect(62, 218, 86, 14, "dark")
    s.rect(96, 219, 10, 12, "contact")
    s.text(60, 172, "SN-2549 jaws (XH nest)", "sm")
    s.poly([(150, 250), (420, 318), (420, 336), (150, 268)], "steel")
    s.poly([(150, 196), (410, 150), (410, 168), (150, 214)], "steel")
    s.rect(250, 262, 150, 90, "print", 6)
    s.text(260, 370, "printed cradle clamps", "sm")
    s.text(260, 383, "the fixed handle", "sm")
    s.rect(370, 96, 44, 36, "bought", 3)
    s.rect(386, 132, 12, 10, "dark")
    s.line(392, 142, 392, 158, "ln")
    s.force(392, 146, 392, 162)
    s.lines(222, 100, ["linear actuator (Justech 1,500 N,", "PA-01-POT ~750 N) or", "NEMA 17 Tr8x2 pusher"], "sm", 12)
    s.text(300, 142, "S-beam load cell", "sm")
    s.move(430, 180, 430, 300)
    s.lines(434, 200, ["handle", "closes"], "sm", 12)
    # swinging flap in top view
    s.circle(60, 300, 5, "dark")
    s.rect(60, 296, 50, 8, "print", 2)
    s.path("M 110 300 Q 110 255 101 238", "move")
    s.lines(40, 322, ["swinging flap, hinged outside", "the tool: loads a contact out",
                      "here, swings under the nest,", "lifts it in from below"], "sm", 12)
    s.lines(40, 390, ["The tool's toggle and ratchet make the force;",
                      "crimp height is the tool's."], "sm", 12)
    # --- right panel: section through the nest
    X = 670
    s.text(480, 76, "Section through the XH nest (wire vertical)", "t2")
    s.rect(480, 86, 380, 330, "box")
    s.rect(X - 50, 96, 100, 24, "bought", 3)
    s.text(X, 112, "ribbon clamp", "sm", "middle")
    s.text(X + 56, 102, "X/Z carriage", "sm")
    s.move(X + 60, 114, X + 108, 114, both=True)
    s.line(X, 120, X, 262, "wire")
    for dx in (12, 24, 36, 48):
        s.pline([(X + dx * 0.25, 120), (X + dx * 0.35, 146), (X + dx * 2.2 + 20, 186)], "wire")
    s.rect(X + 6, 144, 70, 10, "print", 3)
    s.lines(X + 80, 146, ["fork: every other", "conductor bent to", "one side (a set)"], "sm", 11)
    # camera and backlight at the tip
    s.rect(500, 190, 34, 22, "bought", 3)
    s.rect(X + 34, 192, 8, 34, "bought", 1)
    s.line(534, 201, X + 34, 206, "thin")
    s.lines(488, 170, ["camera + light pad:", "bare length before threading"], "sm", 11)
    s.poly([(X - 22, 226), (X + 22, 226), (X + 7, 250), (X - 7, 250)], "print")
    s.text(X - 26, 244, "funnel", "sm", "end")
    # jaws, held short of the first tooth
    s.rect(484, 252, X - 12 - 484, 44, "steel")
    s.rect(X + 12, 252, 856 - X - 12, 44, "steel")
    s.force(840, 274, X + 20, 274)
    s.text(490, 290, "fixed jaw", "sm")
    s.text(850, 290, "moving jaw", "sm", "end")
    s.lines(730, 240, ["held just short of", "the first tooth"], "sm", 11)
    # contact box-down, barrels in the nest
    s.rect(X - 6, 256, 12, 36, "contact")
    s.rect(X - 7, 296, 14, 26, "contact")
    # neck blade
    s.rect(X + 10, 293, 40, 4, "dark")
    s.rect(X + 50, 286, 24, 18, "bought", 2)
    s.lines(X + 60, 344, ["neck blade: in only after", "the crimp, for the 20 N pull"], "sm", 11)
    # flap under
    s.rect(X - 50, 322, 100, 10, "print", 2)
    s.rect(X - 8, 322, 16, 10, "bg")
    s.circle(X - 56, 327, 4, "dark")
    s.lines(488, 350, ["swinging flap: keyed slot (box + lance notch),", "steel floor sets the axial position"], "sm", 12)
    s.lines(488, 392, ["contact box-down, barrels up in the nest"], "sm", 12)
    s.lines(30, 444, ["1 flap takes a contact outside the jaws (magazine, strip shear or tacked), swings in, lifts it into the nest",
                      "2 jaws close to just short of the first ratchet tooth: located, not pinched, ratchet not yet engaged",
                      "3 camera measures the hanging tip's bare length   4 carriage lowers the conductor to the Z that puts the insulation edge mid-window",
                      "5 actuator completes the stroke; the ratchet releases at full closure; force vs travel logged",
                      "6 jaws open, neck blade drops onto the box's rear face, carriage pulls ~20 N   7 blade out, flap out, lift"], "t2", 16)
    legend(s, 30, 548)
    s.lines(30, 578, ["Hands back: magazine or strip loading, a split and stripped ribbon end, insertion. The neighbours leave with",
                      "one uniform set at the fork line (26-46 deg by split length). Branch f1b puts JST's WC-110 in the same cradle."], "t2", 15)
    s.save(os.path.join(HERE, "f1-motorised-ratchet.svg"))


# ---------------------------------------------------------------- f3
def f3():
    s = Svg(880, 600, "f3 knee micro-press, schematic",
            "A palm-sized steel die set on two guide pins, closed by a toggle whose straight position is "
            "bottom of stroke; a flush pilot pin locates the strip from below; the carriage threads the "
            "conductor to a camera-set depth; a neck blade reacts the proof pull after the crimp.")
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
    s.lines(150, 136, ["knee (toggle)", "straight = bottom"], "sm", 12)
    s.rect(448, 124, 56, 34, "bought", 3)
    s.text(448, 118, "NEMA 17 Tr8x2 (or servo, or a hand lever)", "sm")
    s.line(448, 141, 272, 141, "ln")
    s.force(360, 148, 292, 148)
    s.text(300, 166, "60-160 N", "sm")
    s.rect(236, 204, 28, 32, "steel")
    s.text(186, 224, "crimpers", "sm")
    s.rect(236, 276, 28, 24, "steel")
    s.text(196, 294, "anvil", "sm")
    s.poly([(236, 300), (300, 300), (300, 308), (236, 314)], "steel")
    s.text(306, 306, "wedge = crimp-height dial", "sm")
    s.rect(230, 314, 46, 12, "bought", 2)
    s.text(306, 324, "load cell under the anvil", "sm")
    # contact: box left, barrels over the anvil
    s.rect(204, 258, 20, 18, "contact")
    s.rect(236, 266, 40, 10, "contact")
    # neck blade above the neck
    s.rect(226, 236, 5, 26, "dark")
    s.lines(20, 214, ["neck blade: drops", "after the crimp"], "sm", 11)
    s.pline([(112, 222), (224, 248)], "thin")
    s.rect(150, 236, 16, 90, "bought", 2)
    s.line(158, 236, 158, 204, "ln")
    s.lines(26, 300, ["0.001 mm", "indicator", "across the", "dies"], "sm", 12)
    s.rect(90, 326, 330, 46)
    # strip carrier behind the dies, flush pin from below
    s.rect(276, 276, 40, 4, "contact")
    s.rect(300, 280, 6, 30, "steel")
    s.lines(440, 352, ["flush pilot pin rises from below", "into the lead contact's pilot hole"], "sm", 11)
    s.pline([(438, 350), (306, 304)], "thin")
    s.text(90, 390, "behind the dies: side-feed strip track, tapered pins in the neighbours' holes, floating drop-shear", "sm")
    s.line(276, 270, 560, 270, "wire")
    s.line(250, 270, 276, 270, "strand")
    for dy in (-34, -18, 18, 34):
        s.pline([(600, 270 + dy * 0.2), (580, 270 + dy * 0.3), (556, 270 + dy)], "wire")
    s.rect(560, 248, 70, 44, "bought", 3)
    s.text(560, 242, "ribbon carriage (web clamp = depth datum)", "sm")
    s.move(556, 312, 470, 312)
    s.text(470, 328, "threads axially after capture, tab in tension", "sm")
    s.rect(520, 190, 34, 22, "bought", 3)
    s.lines(560, 198, ["camera: into the barrel,", "and the tip's bare length"], "sm", 12)
    s.line(520, 208, 290, 266, "thin")
    s.lines(30, 422, ["1 strip advances; tapered pins bring it within 0.1-0.2 mm; flush pin from below locates the lead contact (+/-0.01-0.03)",
                      "2 knee to capture height, pause   3 camera: barrel open and square; tip's bare length   4 carriage threads to the depth that puts",
                      "   the insulation edge mid-window; the far end reads which conductor touches the grounded anvil",
                      "5 knee to straight; log force vs indicator gap   6 back off, re-touch at 10 N: crimp height   7 drop-shear the tab",
                      "8 neck blade drops onto the box's rear face; carriage pulls ~20 N against the web clamp   9 stripper plate, open, lift out"], "t2", 16)
    legend(s, 30, 530)
    s.text(30, 560, "Dies: SN jaws, knife set, EDM or ground stock (f7). Branches: f3b (curl, then finish), f6 (second blade and drive).", "t2")
    s.save(os.path.join(HERE, "f3-knee-micropress.svg"))


# ---------------------------------------------------------------- f4
def f4():
    s = Svg(880, 600, "f4 crimp head goes to the wire, schematic top view",
            "The ribbon end lies still in a printed comb board after a split into planes; a steel C-frame "
            "crimp head on a gantry picks a contact box-first from a strip dispenser whose drop-shear cuts "
            "the tab, probes the tip, threads the contact onto the still conductor, crimps, and leaves toward "
            "the box.")
    s.text(20, 28, "f4  The head goes to the wire: the ribbon never moves", "h")
    s.text(20, 46, "schematic, not to scale; top view (side section of the head: f4b)", "t2")
    s.rect(40, 110, 300, 290, "print", 6)
    s.text(50, 128, "ribbon board (printed): clamp + comb", "sm")
    s.rect(40, 210, 110, 80, "bought")
    s.text(48, 305, "web clamp = split root", "sm")
    ys = [175, 225, 275, 325]
    for y in ys:
        s.pline([(150, 250 + (y - 250) * 0.15), (230, y), (330, y)], "wire")
        s.line(330, y, 350, y, "strand")
    s.rect(290, 160, 18, 180, "print")
    s.lines(170, 356, ["plane A in a 5 mm comb, stripped", "after the spread; plane B", "folded back under the clamp"], "sm", 12)
    # dispenser
    s.rect(470, 76, 300, 26, "print", 3)
    for i in range(8):
        s.rect(480 + i * 34, 82, 14, 14, "contact")
    s.text(470, 70, "strip dispenser: flush pilot pin, servo drop-shear outside the head's mouth", "sm")
    s.line(360, 140, 840, 140, "thin")
    s.text(640, 134, "gantry (printer-class or 3018)", "sm")
    # head at conductor 3, spine to the right (ahead of the box), mouth toward the comb
    s.rect(356, 262, 80, 26, "steel", 4)
    s.rect(436, 250, 16, 50, "steel", 2)
    s.rect(348, 269, 14, 12, "contact")
    s.text(360, 256, "head: mouth toward the comb", "sm")
    s.text(440, 314, "spine", "sm")
    s.move(620, 106, 470, 240)
    s.lines(560, 180, ["1 pick box-first into the mouth;", "anvil up, capture, tab sheared outside"], "sm", 12)
    s.move(470, 300, 452, 300)
    s.lines(470, 318, ["2 camera + tip probe (captured barrel's rim touches the tip;",
                       "   the far end reads it): X, Z, Y and identity",
                       "3 slide the contact onto the still conductor, camera-set depth",
                       "4 knee to straight; force closes inside the head",
                       "5 open 5 mm, drop the anvil 1.5 mm, leave toward the box"], "sm", 13)
    s.move(460, 275, 520, 275)
    s.lines(40, 428, ["Then: lift crimped plane A out of the comb and park it at the split root; crimp plane B in the same comb;",
                      "unpark both into a 2.5 mm comb (the half-rows interleave exactly) and move a housing onto the whole row.",
                      "Or no planes at all: f10 keeps the ribbon flat at 2.5 mm, lifts one conductor 3.5 mm, and the same C crimps at a fixed station.",
                      "Hands back: splitting, laying the comb board (J4/J7 crossings on raised routes), strip loading, the housing move.",
                      "Gantry sees positioning loads only (a few N)."], "t2", 16)
    legend(s, 40, 565)
    s.save(os.path.join(HERE, "f4-head-to-wire.svg"))


# ---------------------------------------------------------------- f5b
def f5b():
    s = Svg(880, 640, "f5b half-row cassette, schematic",
            "Top view of the lower shoe: loose contacts in five keyed pockets at 5.0 mm; plane A of a split "
            "ribbon captured by a grooved fan block from the root and stripped after the spread; each anvil "
            "insulated for an identity check. Below: crimp A, park it, crimp B, merge both at 2.5 mm, move the "
            "housing onto the whole row.")
    s.text(20, 28, "f5b  Half-row cassette: crimp every other cavity at 5.0 mm, merge at 2.5 mm, insert once", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    s.rect(20, 60, 560, 330, "box")
    s.text(30, 78, "Lower shoe, top view, loading plane A", "t2")
    s.rect(40, 190, 70, 90, "print", 3)
    s.lines(40, 296, ["ribbon pallet on balls;", "clamp face = split root"], "sm", 12)
    ys_r = [214, 231, 248, 265]
    ys_st = [150, 200, 250, 300, 350]
    for i, y in enumerate([ys_r[0], ys_r[2]]):
        s.pline([(110, y), (170, y), (300, ys_st[i + 1] + 0), (340, ys_st[i + 1])], "wire")
    s.poly([(170, 200), (300, 170), (300, 330), (170, 290)], "print")
    s.lines(40, 340, ["grooved fan block: grooves start at", "3.4 mm at the root, open to 5.0;", "strip after the spread, at its face"], "sm", 12)
    s.rect(340, 130, 150, 240, "steel")
    for i, y in enumerate(ys_st):
        s.rect(348, y - 6, 34, 12, "dark")
        s.rect(382, y - 7, 60, 14, "bg")
        if i in (1, 2):
            s.rect(390, y - 6, 48, 12, "contact")
        s.line(365, y + 6, 365, y + 16, "thin")
    s.text(340, 122, "anvils (insulated, wired: identity)", "sm")
    s.text(384, 386, "keyed pockets, open on top", "sm")
    # right: section
    X = 600
    s.text(X, 76, "Section across the stations", "t2")
    s.rect(X, 86, 260, 304, "box")
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
    s.lines(X + 10, 350, ["webs between channels:", "5.0 - 2.0 = 3.0 mm", "(separate crimpers: 0.6-1.5)"], "sm", 12)
    # bottom: sequence
    s.text(30, 416, "Sequence (end view of the contacts, one ribbon end)", "t2")
    y0 = 470
    steps = [("1 crimp plane A", "A"), ("2 lift A out, park it", "park"), ("3 reload, crimp plane B", "B"),
             ("4 merge at 2.5 mm", "merge"), ("5 move the housing on", "house")]
    for j, (lab, kind) in enumerate(steps):
        x = 40 + j * 164
        s.text(x, y0 - 30, lab, "sm")
        if kind in ("A", "B"):
            for k in range(3):
                s.rect(x + k * 40, y0 - 10, 18, 22, "contact" if kind == "A" or True else "contact")
            s.rect(x - 6, y0 + 14, 120, 8, "steel")
        if kind == "park":
            s.path(f"M {x} {y0 + 10} Q {x + 60} {y0 - 30} {x + 110} {y0 + 10}", "wire")
            s.text(x, y0 + 30, "folded back at the root", "sm")
        if kind == "merge":
            for k in range(5):
                s.rect(x + k * 22, y0 - 10, 16, 22, "contact")
            s.rect(x - 6, y0 + 14, 120, 8, "print")
            s.text(x, y0 + 36, "printed 2.5 mm comb", "sm")
        if kind == "house":
            s.rect(x - 8, y0 - 16, 124, 34, "print", 3)
            for k in range(5):
                s.rect(x + k * 22, y0 - 10, 16, 22, "contact")
            s.text(x - 8, y0 + 32, "housing slides on along", "sm")
            s.text(x - 8, y0 + 44, "the wire; one D for all", "sm")
    s.lines(30, 530, ["Why not push each half-row in turn: every conductor has the same length from the web, so a second push needs 6-9 mm of stored feed.",
                      "Rows per unit: T4 2+2 (x5), J1 5+4, J2 2+3, J4 4+3, J6 3+2, J7 4+3 -> 20 strokes; row of 2 1.6-4.9 kN, row of 3 2.3-7.3 kN (1 t arbor press)."], "t2", 16)
    legend(s, 30, 590)
    s.text(30, 620, "f5 (cassette, stops, any press) x change-the-question c1 (planes) x ribbon-as-pallet K4 / into-the-housing i3 (merge, one housing move).", "t2")
    s.save(os.path.join(HERE, "f5b-half-row-cassette.svg"))


# ---------------------------------------------------------------- f9b
def f9b():
    s = Svg(880, 640, "f9b tack on the strip, schematic",
            "Left: a strip segment on slot pins with a hardened rail under the insulation barrels; the "
            "ribbon pallet docks on balls so every conductor drops into its contact; a tack comb closes the "
            "insulation barrels loosely and a shear under the carrier cuts the tabs. Right: the heavy "
            "station, a fixed steel C with a keyed nest on a narrow post; a stage lowers each tacked contact "
            "into the nest.")
    s.text(20, 28, "f9b  Tack on the strip: dock, tack, cut the tabs, then crimp one at a time in a keyed nest", "h")
    s.text(20, 46, "schematic, not to scale", "t2")
    # left panel: side section at one contact of the docked row
    s.rect(20, 60, 420, 360, "box")
    s.text(30, 78, "Tack-and-shear block, side section at one contact", "t2")
    # strip pallet plate
    s.rect(40, 300, 380, 30, "steel")
    s.text(46, 344, "strip pallet (steel plate, slot pins in the carrier)", "sm")
    # carrier and tab (right side), contact to the left
    s.rect(290, 284, 110, 6, "contact")
    s.text(318, 278, "carrier on slot pins", "sm")
    s.rect(268, 286, 22, 4, "contact")
    # rail under insulation barrel with shear edge
    s.rect(236, 290, 32, 10, "dark")
    s.lines(40, 364, ["rail under the insulation barrels only (3 x 3 HSS);", "its rear edge is the shear edge"], "sm", 12)
    s.line(250, 354, 252, 300, "thin")
    # contact: insulation barrel over rail, conductor barrel and box overhang
    s.rect(236, 262, 32, 24, "contact")
    s.rect(190, 272, 34, 14, "contact")
    s.rect(140, 262, 44, 24, "contact")
    s.pline([(178, 286), (170, 300)], "ln")
    s.text(120, 312, "lance hangs free", "sm")
    s.line(190, 276, 236, 276, "strand")
    s.line(236, 272, 300, 272, "wire")
    s.pline([(300, 272), (330, 240), (420, 240)], "wire")
    # ribbon pallet
    s.rect(330, 206, 90, 30, "print", 3)
    s.lines(334, 198, ["ribbon pallet (fan block)"], "sm", 12)
    s.circle(360, 244, 5, "dark")
    s.circle(400, 244, 5, "dark")
    s.text(344, 260, "balls in V-grooves", "sm")
    # tack comb
    s.rect(234, 150, 36, 104, "steel")
    s.lines(40, 150, ["tack comb: loose insulation profile", "per contact, to a steel stop;",
                      "stays down as the pad while", "the shear cuts"], "sm", 12)
    s.force(252, 120, 252, 146)
    s.text(262, 134, "toggle lever", "sm")
    # shear under carrier
    s.rect(276, 300, 30, 26, "bought", 2)
    s.force(292, 336, 292, 318)
    s.lines(40, 396, ["shear drives the carrier down past the rail edge: each tab 53-104 N; the contact",
                      "sees at most the tab's plastic moment, held by the comb at its stop (2-8 N)"], "sm", 12)
    # right panel: heavy station
    X = 460
    s.rect(X, 60, 400, 360, "box")
    s.text(X + 10, 78, "Heavy station, side section (throat toward the wire)", "t2")
    s.rect(X + 300, 100, 30, 260, "steel")
    s.rect(X + 150, 100, 150, 24, "steel")
    s.rect(X + 150, 336, 150, 24, "steel")
    s.text(X + 300, 94, "spine", "sm")
    s.pline([(X + 260, 124), (X + 244, 150), (X + 228, 124)], "ln")
    s.circle(X + 244, 150, 4, "dark")
    s.text(X + 256, 150, "knee", "sm")
    s.rect(X + 200, 150, 40, 70, "dark")
    s.rect(X + 160, 160, 38, 60, "dark")
    s.lines(X + 12, 100, ["conductor crimper (knee);", "insulation blade on its", "own drive and wedge (f6)"], "sm", 12)
    # nest post
    s.rect(X + 186, 262, 90, 74, "steel")
    s.rect(X + 230, 244, 44, 18, "bg")
    s.rect(X + 234, 244, 36, 18, "contact")
    s.rect(X + 202, 250, 26, 12, "contact")
    s.rect(X + 162, 240, 36, 22, "contact")
    s.line(X + 202, 254, X + 230, 254, "strand")
    s.line(X + 60, 250, X + 202, 250, "wire")
    s.rect(X + 228, 226, 4, 22, "dark")
    s.lines(X + 12, 156, ["neck blade: after the crimp,", "for the 20 N pull"], "sm", 12)
    s.pline([(X + 150, 162), (X + 228, 230)], "thin")
    s.lines(X + 150, 378, ["keyed nest on a narrow post: box slot, front", "stop, lance relief; load cell under the anvils"], "sm", 12)
    # stage and pallet
    s.rect(X + 20, 234, 40, 30, "print", 3)
    s.text(X + 12, 284, "ribbon pallet on an XYZ stage", "sm")
    s.move(X + 110, 206, X + 110, 240)
    s.text(X + 40, 200, "lowered straight down", "sm")
    s.lines(X + 12, 310, ["neighbours hang one strip", "pitch (~7 mm) away,", "beside the post"], "sm", 12)
    s.lines(30, 450, ["1 lay N + 2 contacts of strip on the slot pins   2 dock the ribbon pallet: every conductor drops into its open contact;",
                      "   the far end reads each conductor to the grounded carrier   3 tack lever to its stop   4 shear lever   5 lift: contacts hang by their tacks",
                      "6 at the heavy station: into the nest vertically (tack loaded across the jacket), capture, look, identity (only k reads)",
                      "7 knee to straight, re-touch height   8 insulation blade to this wire's window   9 neck blade, pull 20 N against the web clamp",
                      "10 bend down over the anvil's radiused rear edge, look   11 eject, index one strip pitch.   ~14 calls per unit."], "t2", 16)
    legend(s, 30, 560)
    s.text(30, 590, "ribbon-as-pallet a2 (docking on strip) x change-the-question c1b (tack) x force-and-form f3/f6 (knee, second blade) and f9.", "t2")
    s.save(os.path.join(HERE, "f9b-tack-on-the-strip.svg"))


# ---------------------------------------------------------------- f2c
def f2c():
    s = Svg(880, 560, "f2c T4 ends from the spool, schematic",
            "A 4P spool on a slip ring feeds a web clamp on the carriage; two blades strip the whole end; "
            "the applicator in the slow crank press crimps one conductor per turn; the carriage places each "
            "crimped contact into one hinged pallet at 2.5 mm in cavity order; one push inserts all four; a "
            "wafer tests; a puller and guillotine free the end into a bin and square the next.")
    s.text(20, 28, "f2c  The applicator station makes whole T4 ends from the spool", "h")
    s.text(20, 46, "schematic plan view, not to scale", "t2")
    # spool
    s.circle(80, 200, 50, "print")
    s.circle(80, 200, 12, "bought")
    s.lines(40, 272, ["4P spool, inner end", "on a slip ring (p6)"], "sm", 12)
    s.pline([(130, 200), (200, 200)], "wire")
    s.rect(200, 186, 40, 28, "bought", 3)
    s.text(196, 180, "puller", "sm")
    s.pline([(240, 200), (300, 200)], "wire")
    s.rect(300, 180, 14, 40, "steel")
    s.text(284, 174, "guillotine", "sm")
    s.pline([(314, 200), (380, 200)], "wire")
    # carriage with web clamp and hinged pallet
    s.rect(380, 170, 120, 60, "bought", 4)
    s.text(384, 164, "carriage: web clamp", "sm")
    for dy in (-12, -4, 4, 12):
        s.line(500, 200 + dy, 560, 200 + dy * 2.2, "wire")
    s.rect(510, 250, 70, 20, "print", 2)
    for k in range(4):
        s.rect(514 + k * 16, 253, 10, 14, "contact")
    s.lines(470, 290, ["one pallet at 2.5 mm, on the carriage,", "hinged to swing clear; filled in cavity order"], "sm", 12)
    s.rect(590, 244, 40, 32, "print", 2)
    s.text(588, 238, "XHP-4 nest", "sm")
    s.move(584, 260, 596, 260)
    # strip blades
    s.rect(560, 150, 10, 30, "steel")
    s.rect(560, 220, 10, 30, "steel")
    s.lines(520, 130, ["p7: two blades strip the", "whole webbed end at once"], "sm", 12)
    # applicator in crank press
    s.rect(680, 110, 170, 150, "steel")
    s.rect(700, 130, 130, 80, "dark")
    s.text(706, 150, "OTP applicator", "sm")
    s.text(706, 166, "(grounded: identity", "sm")
    s.text(706, 180, "before each stroke)", "sm")
    s.circle(765, 236, 12, "bought")
    s.lines(690, 280, ["slow crank press (f2):", "NEMA 23 + 30:1 worm"], "sm", 12)
    s.rect(640, 60, 180, 30, "contact")
    s.text(644, 80, "strip reel feeds the applicator", "sm")
    s.move(600, 200, 676, 200)
    s.text(596, 188, "fork presents one", "sm")
    s.lines(30, 340, ["Per end: feed; strip the whole end; split to the clamp face; for each conductor: present at its measured depth, one crank turn",
                      "(crimp, tab cut, next contact fed), lift, set into its pocket in cavity order; then one push inserts all four with the web following:",
                      "every contact latches at the same distance from the web, so no conductor needs stored feed; wafer test; puller draws",
                      "400 or 700 mm; the guillotine frees the end into the bin and squares the next. ~4-5 min per end; a 15.2 m spool is 21-38 ends."], "t2", 16)
    legend(s, 30, 440)
    s.lines(30, 474, ["f2 (applicator in a slow crank press) x change-the-question c1 (pallet, push, wafer test) and c5 (ends as stock, cut last)",
                      "x procedure-is-the-machine p7 (whole-end strip) and p6 (reel as the far end, puller). Hands back: threading a spool,",
                      "housings, a contact reel, emptying the bin; at unit build, cutting stock ends to length and the far end."], "t2", 15)
    s.save(os.path.join(HERE, "f2c-t4-ends-from-the-spool.svg"))


if __name__ == "__main__":
    for f in (f1, f3, f4, f5b, f9b, f2c):
        f()
    print("wrote f1, f3, f4, f5b, f9b, f2c")
