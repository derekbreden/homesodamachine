"""Schematic sketches for ribbon-as-pallet, as the ideas finally stand.
Redraws a2, a2e, a3, a4, a5, a6 and draws a2b, a2c, a8b, a9, a10 (with a10b).
Run: python3 make_sketches_w3.py   (writes the .svg files beside this script)
Every drawing is schematic. Numbers in labels come from the idea files and their calcs.
"""
import math
from make_sketches_w2 import (Svg, SILICONE, SIL_LIGHT, COPPER, BRASS, BRASS_S, STEEL,
                              BLUE, BLUE_S, TPU)

RED = "#a33"
GREEN = "#3a7a35"


def contact_plan(s, x, y, L=62, w=14, box=24):
    """A contact seen from above, box end at y (top), barrels toward y+L."""
    s.rect(x - w / 2, y, w, box, fill=BRASS, stroke=BRASS_S)
    s.rect(x - w / 2 - 1, y + box + 6, w + 2, 12, fill="none", stroke=BRASS_S)
    s.rect(x - w / 2 - 3, y + box + 22, w + 6, L - box - 22, fill="none", stroke=BRASS_S)


# ---------------------------------------------------------------------------
def a2():
    s = Svg(1000, 660, "a2 Two pallets meet: the carrier strip is the contact pallet",
            "schematic, not to scale; strip pitch ~7.1 mm (Wurth analog; JST's figure is licence-gated)")
    s.text(20, 74, "A. Plan, after docking: every conductor already lies in its contact", weight="bold")
    s.rect(120, 150, 420, 110, fill="#eee", stroke="#555")
    s.lines(552, 158, ["strip pallet (steel): slot pins in the carrier's slots;",
                       "comb clamp bar between conductor paths;",
                       "support comb and rail carry a groove along X under the",
                       "lance line (a flat face props each contact 7.6-15.9 deg)",
                       "hardened rail flush with the contacts' floor (grey band)"], size=11)
    s.rect(120, 110, 420, 12, fill="#aab", stroke="#556")
    s.text(552, 124, "rail for the head's lower arm (Z from the strip pallet)", size=11)
    s.rect(140, 222, 380, 16, fill=BRASS, stroke=BRASS_S)
    s.line(140, 196, 520, 196, stroke=RED, dash="4 3")
    s.text(525, 238, "lance-line groove (dashed)", size=10, fill=RED)
    xs = [180 + i * 50 for i in range(7)]
    for i, x in enumerate(xs):
        s.rect(x - 7, 150, 14, 72, fill=BRASS, stroke=BRASS_S)
        s.circle(x, 230, 4, fill="#fff", stroke=BRASS_S)
        if i < 6:
            s.rect(x + 20, 226, 10, 8, fill="#555")
    for x in xs[1:6]:
        s.line(x, 180, x, 330, stroke=SILICONE, sw=9)
        s.line(x, 162, x, 184, stroke=COPPER, sw=4)
    s.rect(200, 300, 260, 80, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.lines(206, 396, ["ribbon pallet: fan block at strip pitch, flush-cut and stripped at its face;",
                       "three balls on hardened ball pairs or case-hardened rod, magnets pull it home;",
                       "if the open wings are narrower than the jacket, a finger comb presses each",
                       "conductor in at ~0.5-2 N, taken by the rail, not the tabs [calc F s4]"],
            size=11, fill=BLUE_S)
    s.rect(262, 80, 36, 60, fill="#bbb", stroke="#333")
    s.lines(552, 76, ["C-frame head (borrowed-machines b3): harvested OTP crimper and anvil,",
                      "NEMA 17 + 10:1 on a 3 mm crank, ~3.8 kN, ~1 kg; arms <= 10 mm wide"], size=11)
    s.line(262, 148, 212, 148, arrow=True)
    s.line(298, 148, 348, 148, arrow=True)
    s.text(20, 480, "B. Side: the head straddles one contact from the box end", weight="bold")
    s.rect(80, 510, 16, 90, fill="#999", stroke="#333")
    s.rect(80, 510, 160, 16, fill="#999", stroke="#333")
    s.rect(80, 584, 160, 16, fill="#999", stroke="#333")
    s.rect(200, 526, 30, 20, fill="#777", stroke="#333")
    s.rect(200, 566, 30, 18, fill="#777", stroke="#333")
    s.text(440, 538, "upper die (crimper) over the wings", size=11)
    s.lines(250, 578, ["lower die on the rail: it passes under the lance and rises behind",
                       "its tip only if the neck t >= 0.34-0.74 mm [w3 s5]; else it drops and rises"], size=11)
    s.rect(180, 548, 170, 8, fill=BRASS, stroke=BRASS_S)
    s.line(230, 542, 420, 542, stroke=SILICONE, sw=10)
    s.rect(330, 556, 60, 10, fill=BRASS, stroke=BRASS_S)
    s.text(400, 566, "carrier on slot pins", size=11)
    s.lines(40, 626, ["Then: each conductor pulled to 20 N with the shear comb's pad down on the crimped barrels "
                      "(the tab alone pitches at 2.5-4.6 N [w3 s4]);",
                      "the notched shear comb cuts every tab; lift; close to 2.5 mm; insert (a6)."], size=11)
    s.save("a2-two-pallets-meet.svg")


# ---------------------------------------------------------------------------
def a2e():
    s = Svg(1000, 720, "a2e Docked strip through a feedless applicator (a2 x borrowed-machines b1b)",
            "schematic, not to scale; strip pitch ~7.1 mm (Wurth analog); parts marked dashed are removed")
    s.text(20, 74, "A. Plan: the carriage carries the carrier segment and the docked ribbon pallet along X",
           weight="bold")
    s.rect(40, 330, 900, 12, fill=STEEL, stroke="#556")
    s.text(44, 358, "MGN12 rail + Tr8x2 NEMA 17 [Prime rows]: one X axis; load position upstream (right)",
           size=11)
    s.rect(300, 90, 220, 160, fill="#eeeeee", stroke="#555")
    s.lines(306, 106, ["OTP side-feed applicator on the VEVOR bed,", "under a 3-4 mm eccentric"], size=11)
    ax = 410
    s.rect(ax - 8, 150, 16, 40, fill="#888", stroke="#333")
    s.text(ax - 22, 144, "anvil", size=11)
    s.rect(440, 190, 70, 26, fill="none", stroke=RED, dash="4 3")
    s.rect(440, 160, 70, 26, fill="none", stroke=RED, dash="4 3")
    s.line(510, 165, 560, 100, stroke=RED, dash="2 2")
    s.lines(564, 86, ["removed (dashed): pressure plate and feed finger upstream;",
                      "shear punch at the station, its pocket now holds a pilot"], size=10, fill=RED)
    pitch = 50
    n = 5
    xs = [ax + i * pitch for i in range(0, n)]
    s.rect(xs[0] - 30, 222, xs[-1] - xs[0] + 60, 16, fill=BRASS, stroke=BRASS_S)
    for x in xs:
        s.rect(x - 7, 160, 14, 62, fill=BRASS, stroke=BRASS_S)
        s.circle(x, 230, 4, fill="#fff", stroke=BRASS_S)
    for x in (xs[0] - 25, xs[-1] + 25):
        s.rect(x - 5, 224, 10, 12, fill="#333", stroke="#111")
    s.circle(ax - 25, 230, 3, fill=RED, stroke=RED)
    s.lines(660, 256, ["grips (dark): pins in the carrier's END slots",
                       "pilot (red dot): enters the slot beside the anvil",
                       "contact before the crimpers touch; the row",
                       "floats +/-0.5 mm in X on a light spring"], size=10)
    s.rect(ax - 40, 262, 280, 58, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(ax - 36, 312, "ribbon pallet, fanned to strip pitch, on three balls", size=10, fill=BLUE_S)
    for x in xs:
        s.line(x, 172, x, 264, stroke=SILICONE, sw=9)
        s.line(x, 162, x, 180, stroke=COPPER, sw=4)
    s.rect(560, 150, 300, 90, fill="none", stroke=GREEN, dash="5 3")
    s.lines(566, 146, ["loading shelf, flush with the track; groove along X under the lance line"],
            size=10, fill=GREEN)
    s.rect(160, 150, 140, 90, fill="#fbeaea", stroke=RED, dash="4 3")
    s.lines(164, 166, ["downstream: crimped", "contacts on their", "carrier reach ~18-35 mm",
                       "past the anvil (3P-5P,", "end-slot grips);", "room unknown until scanned"],
            size=10, fill=RED)
    s.line(760, 314, 660, 314, arrow=True)
    s.text(766, 318, "index -X, one pitch per turn", size=11)

    s.text(20, 400, "B. Section at the anvil, one eccentric turn per contact", weight="bold")
    s.circle(200, 450, 20, fill="#fff", stroke="#333")
    s.circle(206, 450, 4, fill="#333")
    s.line(206, 450, 204, 540, sw=4)
    s.rect(180, 540, 50, 30, fill=STEEL, stroke="#556")
    s.lines(240, 440, ["NEMA 17 + 26.85:1 planetary [Prime], 3-4 mm eccentric:",
                       "1.0-1.7 N m, ~40-47 HX711 samples through the last 0.2 mm [P3 s5];",
                       "AS5600 on the shaft; strain gauges on the rod"], size=11)
    s.rect(185, 570, 40, 40, fill="#999", stroke="#333")
    s.text(236, 596, "crimpers (conductor, insulation) and dials", size=11)
    s.rect(120, 632, 180, 10, fill=BRASS, stroke=BRASS_S)
    s.rect(180, 642, 50, 30, fill="#888", stroke="#333")
    s.text(236, 660, "anvil (fixed): the reference for the stroke", size=11)
    s.line(60, 626, 300, 626, stroke=SILICONE, sw=10)
    s.text(40, 618, "conductor already in the barrels (docked)", size=11)
    s.lines(650, 440, ["Before each stroke:",
                       "  continuity conductor-to-carrier (far-end port)",
                       "  camera: strands in, insulation edge in the window",
                       "During: force curve, stop-before-bottom; re-touch height",
                       "After the row, back at the load position:",
                       "  slot pins drop into every slot, the shear comb's pad",
                       "  comes down on the crimped barrels, each conductor is",
                       "  pulled to 20 N; then the comb shears every tab",
                       "",
                       "Person per ribbon end: lay a strip segment, seat the",
                       "  ribbon pallet, press start (~2 min machine time per 5P)"], size=11)
    s.save("a2e-docked-strip-feedless-applicator.svg")


# ---------------------------------------------------------------------------
def a3():
    s = Svg(1000, 620, "a3 The backshell that ships: the clamp is applied once and never removed",
            "schematic, not to scale; J4 SENSORS (4P + 3P into XHP-7) shown")
    s.text(20, 74, "A. Side section of the backshell: the ribbon folds 180 deg around a bar (the IDC strain-relief fold)",
           weight="bold")
    s.rect(120, 110, 160, 90, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.circle(250, 155, 14, fill="#9db7d2", stroke=BLUE_S)
    s.path("M40,135 L250,135 A20,20 0 0 1 250,175 L120,175", stroke=SILICONE, sw=9)
    s.path("M250,141 L420,141", stroke=SILICONE, sw=9)
    s.rect(120, 100, 160, 14, fill="#9db7d2", stroke=BLUE_S)
    s.text(126, 96, "snap cover", fill=BLUE_S, size=11)
    s.line(280, 90, 280, 220, stroke=RED, dash="3 2")
    s.text(286, 216, "front face = split root = tear stop", size=11, fill=RED)
    s.text(40, 128, "loom", size=11)
    s.text(430, 145, "to fan and housing", size=11)
    s.lines(600, 110, ["a wrap multiplies the cover's hold by e^(mu pi):",
                       "4.8x at mu 0.5, 23x at mu 1.0 (2.6x at mu 0.3)",
                       "3 N on the tail resists 14-69 N of loom pull [calc X s8]",
                       "the insulation crimp on silicone slips at 0.4-9 N",
                       "(force-and-form f6): the fold is the loom's strain relief",
                       "",
                       "outer faces: the machine's datum",
                       "top: embossed name; edge: notch code = recipe"], size=11)
    s.text(20, 300, "B. Height above the board with the backshell at the split root [calc F s2]", weight="bold")
    s.rect(40, 540, 300, 14, fill="#5c8a3a", stroke="#333")
    s.text(46, 572, "main board, vertical XH wafer", size=11)
    s.rect(140, 500, 60, 40, fill="#eee", stroke="#555")
    s.text(206, 524, "XHP mated ~9.8 mm", size=11)
    s.line(170, 500, 170, 400, stroke=SILICONE, sw=9)
    s.rect(130, 370, 80, 30, fill=BLUE, stroke=BLUE_S)
    s.text(216, 390, "backshell ~12 mm", size=11)
    rows = [("fold-back parking", "8-15 mm", "30-37 mm"),
            ("housing-pitch fan only", "14-18 mm", "36-40 mm"),
            ("a1c, a2c at 5 mm, per ribbon", "17-23 mm", "39-45 mm"),
            ("a2, a2e, a10 at ~7 mm, per ribbon", "21-30 mm", "43-52 mm"),
            ("a9 at ~7.1 mm, equal-path", "22-33 mm", "44-55 mm"),
            ("a1 with the tongue, 5 mm", "30-47 mm", "52-69 mm")]
    s.text(420, 340, "parting", size=11, weight="bold")
    s.text(680, 340, "parted", size=11, weight="bold")
    s.text(780, 340, "top above board", size=11, weight="bold")
    for i, (a, b, c) in enumerate(rows):
        y = 362 + i * 20
        s.text(420, y, a, size=11)
        s.text(680, y, b, size=11)
        s.text(780, y, c, size=11)
    s.lines(420, 500, ["Arms variant: two bridge arms hook the XHP's end flanges (~0.8 mm each side);",
                       "whether they clear the wafer shroud is untested."], size=11)
    s.save("a3-backshell-that-ships.svg")


# ---------------------------------------------------------------------------
def a4():
    s = Svg(1000, 640, "a4 Spool as magazine: terminate the leading end, then feed out and cut",
            "schematic side view, not to scale")
    # spool
    s.circle(90, 200, 60, fill="#f2f2f2", stroke="#555")
    s.circle(90, 200, 22, fill="#ddd", stroke="#555")
    s.lines(30, 285, ["reel: BNTECHGO spool, or rewound once onto", "an 80 mm hub radius (procedure-is-the-machine p6);",
                      "inner end in a hub socket, or on a 6-circuit", "capsule slip ring ($9.99 [Prime]); two for a pair"],
            size=10)
    s.path("M90,140 C170,140 190,180 250,180", stroke=SILICONE, sw=6)
    # straightener
    for i, x in enumerate(range(200, 260, 15)):
        s.circle(x, 172 if i % 2 else 188, 6, fill=STEEL, stroke="#556")
    s.text(186, 160, "roller straightener", size=10)
    # belt feed
    s.rect(270, 168, 70, 10, fill="#555")
    s.rect(270, 184, 70, 10, fill="#555")
    s.text(270, 160, "belt feed + encoder", size=10)
    s.line(250, 181, 480, 181, stroke=SILICONE, sw=6)
    # clamp
    s.rect(360, 160, 90, 42, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(362, 154, "fixed clamp = the pallet", size=10, fill=BLUE_S)
    s.line(450, 140, 450, 240, stroke=RED, dash="3 2")
    s.lines(454, 252, ["clamp face = cut line", "= split root"], size=10, fill=RED)
    # covered floor
    s.rect(450, 186, 120, 6, fill="#aaa", stroke="#666")
    s.rect(450, 170, 120, 5, fill="none", stroke="#666", dash="3 2")
    s.lines(590, 182, ["<- covered floor keeps any curl", "   in plane up to the tools"], size=10)
    # stations as boxes above
    names = [("zip (a7)", 470), ("fan flat, 5 mm", 560), ("strip (a8 at the", 650), ("crimp: a1c order", 760)]
    for name, x in names:
        s.rect(x, 80, 84, 40, fill="#f6f6f6", stroke="#777")
        s.text(x + 4, 96, name, size=10)
    s.text(654, 110, "fan face)", size=10)
    s.text(764, 110, "on a short X slide", size=10)
    s.lines(470, 136, ["the stations come to the fixed end one after another;",
                       "each crimped conductor is folded back over the clamp (a1c)"], size=10)
    # insertion nest
    s.rect(870, 160, 90, 42, fill="#eee", stroke="#555")
    s.lines(872, 216, ["insertion nest:", "real XH wafer", "(a6); test through", "the reel"], size=10)
    # drop tube
    s.path("M480,190 C560,200 600,260 600,360 L600,520", stroke="#999", sw=14)
    s.path("M480,190 C560,200 600,260 600,360 L600,520", stroke=SILICONE, sw=5)
    s.lines(612, 400, ["after termination the feed pushes the loom", "length out, housing first, down a drop tube",
                       "(a 600 mm loom needs ~0.6-0.7 m); the guillotine",
                       "cuts at the clamp face: that cut frees the loom", "and squares the next end"], size=10)
    s.rect(560, 530, 90, 40, fill="#f2f2f2", stroke="#555")
    s.text(566, 554, "finished bin", size=10)
    s.lines(30, 380, ["What locates what: the clamp channel (0.2 mm under width);",
                      "tips found by touch-off through the reel; each conductor's",
                      "crimp Y from its own touch-off record (order C) or a flush",
                      "cut at the fan face (order A).",
                      "",
                      "A bad crimp costs the end's whole split (~20-35 mm of reel),",
                      "never a loom: the loom is cut last."], size=10)
    s.save("a4-spool-as-magazine.svg")


# ---------------------------------------------------------------------------
def a5():
    s = Svg(1000, 700, "a5 Part, fan and strip: three orders that keep every tip and insulation edge where the crimp needs it",
            "schematic; recession figures for the compact R 5 mm / 30 deg S groove [calc W2 s3]; other groove shapes differ")
    rows = [
        ("Order A (a1, a2, a2e, a10)", ["part to the clamp face", "fan to working pitch",
                                        "flush-cut at the fan face", "strip at the fan face"],
         "tips and edges on one line in the crimp pose; the outer conductors stay longer:\n"
         "closed to 2.5 mm they carry 0.65-2.46 mm excess, a 2-5 mm arc in the loom [calc F s5]"),
        ("Order B (a9)", ["flush-cut at the clamp face", "strip webbed (p7)", "zip from the slug's gap",
                          "equal-path fan"],
         "every conductor one length from the root; inner grooves carry humps (5P at 7.1 mm:\n"
         "5.1 mm over 21 mm) so the tips stay on a line; humps leave set, pulled straight at insertion"),
        ("Order C (a4 or a1c with a8b)", ["part", "fan", "touch off each tip", "strip each at its own tip"],
         "any fan; each conductor's position measured and used; a8b needs a snout <= 7.8 mm\n"
         "at 5 mm pitch, or the conductor lifted ~9 mm (procedure-is-the-machine p1c)"),
    ]
    y = 90
    for title, steps, note in rows:
        s.text(20, y, title, weight="bold")
        x = 20
        for i, st in enumerate(steps):
            s.rect(x, y + 10, 170, 32, fill="#f4f4f4", stroke="#777", rx=4)
            s.text(x + 6, y + 30, st, size=11)
            if i < len(steps) - 1:
                s.line(x + 170, y + 26, x + 190, y + 26, arrow=True)
            x += 190
        for j, ln in enumerate(note.split("\n")):
            s.text(20, y + 60 + j * 14, ln, size=11, fill="#444")
        y += 110
    s.text(20, 440, "Outer conductor's recession in the fan (compact S) [calc W2 s3]", weight="bold")
    tab = [("pitch", "3P", "4P", "5P"), ("2.5 mm", "0.11", "0.20", "0.31"), ("5.0 mm", "0.76", "1.20", "1.65"),
           ("7.1 mm", "1.32", "2.05", "2.77")]
    for i, r in enumerate(tab):
        for j, c in enumerate(r):
            s.text(30 + j * 80, 462 + i * 18, c, size=11, weight="bold" if i == 0 else "normal")
    s.lines(20, 552, ["A gentle S spread over the whole split gives less at 2.5 mm (5P 0.10-0.19 mm),",
                      "and about the same at 7.1 mm (2.0-3.1 mm) [P3 s1]: the groove's shape sets it."], size=11)
    s.text(520, 440, "The catalogue behind the stations", weight="bold")
    s.lines(520, 462, ["Parting: P1 floating plough (a7b); P2 fixed gang; P3 nick and wedge (a7);",
                       "  P4 interlaced toothed jaws; P5 slot punch; P6 laser slit",
                       "Fanning: F1 recipe fan block; F2 pitch changer; F3 tines that stay (a7);",
                       "  F4 form and let go; F5 equal-path grooves (order B)",
                       "Stripping: S1 crown score across the row (= p7 before the split);",
                       "  S2 V-blades per conductor; S3 ring score by turning (a8, a8b);",
                       "  S4 pinch and pull; S5 laser score; S6 hot blade; S7 strip-crimp applicator",
                       "",
                       "Nick detector for any blade or tine: isolated steel, a wire to every",
                       "conductor through the far end (a6) or the reel; a touch names it."], size=11)
    s.save("a5-part-fan-strip.svg")


# ---------------------------------------------------------------------------
def a6():
    s = Svg(1000, 720, "a6 The housing is the last comb: close, grip behind the barrels, let the fronts step, test on a real wafer",
            "schematic plan, not to scale; 5P closed from strip pitch shown in A")
    s.text(20, 74, "A. Closing a fan leaves the outer contacts ahead: a V staircase [P3 s10]", weight="bold")
    s.rect(40, 110, 120, 200, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(46, 104, "pallet", size=11, fill=BLUE_S)
    ys = [150, 175, 200, 225, 250]
    lead = [2.47, 1.22, 0.0, 1.22, 2.47]
    for y, l in zip(ys, lead):
        xf = 420 + l * 30
        s.path(f"M160,{200 + (y - 200) * 0.3:.0f} C230,{200 + (y - 200) * 0.3:.0f} 260,{y} 330,{y} L{xf - 60:.0f},{y}",
               stroke=SILICONE, sw=9)
        s.rect(xf - 60, y - 8, 60, 16, fill=BRASS, stroke=BRASS_S)
        s.text(xf + 4, y + 4, f"+{l:.2f}" if l else "0", size=10)
    s.rect(300, 135, 30, 130, fill="#9fb0c4", stroke=BLUE_S)
    s.lines(250, 290, ["2.5 mm closing block (plain grooves)", "and insertion clamp: jaws grip each",
                       "conductor 1-2 mm behind its barrel,", "then slide along to push on the",
                       "barrel's rear (Molex US 4,936,011)"], size=10)
    s.rect(560, 130, 70, 140, fill="#eee", stroke="#555")
    s.lines(636, 140, ["XHP on a real XH wafer (test board),", "nest on a load cell (HX711)"], size=10)
    s.lines(560, 300, ["Latch events: outer pair, next pair, centre (3 events for 5 contacts).",
                       "Forcing the fronts onto one line instead bows the outer",
                       "conductors 2.2-4.5 mm [P3 s10]; in order A the same excess",
                       "stays in the finished loom as a 3-5 mm arc [calc F s5].",
                       "Pull-back: release, draw back at <= 5 N per contact; the camera",
                       "looks for any contact that followed. Then pin map, shorts,",
                       "J2 cavity 3 open, through the far-end port or the reel."], size=11)
    s.text(20, 420, "B. J4 and J7: the crossing runs between the two ribbons [procedure-is-the-machine unit_inventory s1]",
           weight="bold")
    def row(y, label, cav, owners, note):
        s.text(20, y - 20, label, size=11, weight="bold")
        for i in range(7):
            x = 60 + i * 40
            fill = {"A": BRASS, "B": "#d9c7f0", "-": "#fff"}[owners[i]]
            s.rect(x, y, 34, 26, fill=fill, stroke="#555")
            s.text(x + 13, y + 17, str(i + 1), size=11)
        s.lines(360, y + 6, note, size=10)
    row(470, "J4 SENSORS, XHP-7", 7, "ABAAABB",
        ["4P (gold) by machine through a gapped closing block: cavities 1, 3, 4, 5;",
         "the 3P's GND crosses into cavity 2, so its three contacts go in by hand",
         "(or X5: one pallet with a raised crossover groove, ~39 mm split)"])
    row(560, "J7 REEDS B, XHP-7", 7, "AAAABBA",
        ["5P by machine: cavities 1-4 and 7 (its GND jumps the gap);",
         "the 3P's CLO/CHI into 5-6 by hand, under the 5P's GND.",
         "Wiring choice for Derek: GND on the 3P, the 5P's fifth trimmed -> straight"])
    s.text(20, 650, "C. Far-end port: P75-E2 conical pogo pins on the cut face, 1.3 mm cone at 1.7 mm pitch "
           "($6.49 / 100 [Prime]); or the reel's hub socket (a9)", size=11)
    s.text(20, 668, "It gives touch-off, nick detection, placement before force, and opens/shorts after insertion; "
           "it cannot grade a crimp (loom 6-34 mOhm).", size=11)
    s.save("a6-housing-as-last-comb.svg")


# ---------------------------------------------------------------------------
def a8b():
    s = Svg(1000, 520, "a8b Spindle with touch-off: one conductor at a time into a turning head",
            "schematic section, not to scale; the snout is what lets it work at 5 mm pitch")
    # bearings/spindle
    s.rect(420, 150, 220, 120, fill="#eee", stroke="#555")
    s.rect(440, 140, 30, 140, fill=STEEL, stroke="#556")
    s.rect(590, 140, 30, 140, fill=STEEL, stroke="#556")
    s.lines(430, 300, ["6700 bearings, 15 mm OD; GT2 belt from an N20 gearmotor;",
                       "a hand version turns the same head with a knob"], size=10)
    # snout
    s.rect(300, 180, 120, 60, fill="#f6f6f6", stroke="#555")
    s.lines(300, 170, ["snout <= 7.8 mm across, >= 6 mm long [P3 s8]"], size=10, fill=RED)
    s.poly([(300, 190), (320, 205), (320, 215), (300, 230)], fill="#ddd", stroke="#555")
    s.text(300, 256, "4 mm funnel", size=10)
    # blades
    s.poly([(350, 195), (380, 205), (350, 206)], fill="#556", stroke="#333")
    s.poly([(350, 225), (380, 215), (350, 214)], fill="#556", stroke="#333")
    s.lines(300, 340, ["two razor-sliver tips on flexure arms, closed together by a cone",
                       "onto stops: score radius 0.55-0.60 mm, set with a 1.1-1.2 mm gauge pin"], size=10)
    s.line(365, 240, 365, 330, stroke="#777", dash="2 2")
    # tip stop rod
    s.rect(400, 206, 300, 8, fill="#888", stroke="#333")
    s.lines(710, 206, ["isolated tip stop rod (non-rotating),", "one strip length behind the blades;", "ejects the slug"],
            size=10)
    # conductor k and neighbours
    s.line(60, 210, 330, 210, stroke=SILICONE, sw=12)
    s.line(300, 210, 330, 210, stroke=COPPER, sw=5)
    s.text(60, 200, "conductor k (from the fan block)", size=10)
    for dy in (-50, 50):
        s.line(60, 210 + dy, 260, 210 + dy, stroke=SIL_LIGHT, sw=12)
        s.text(60, 210 + dy - 10, "neighbour at 5 mm pitch", size=10)
    s.lines(40, 400, ["Cycle: touch-off (conductor k reads continuous to the stop through the far-end port),",
                      "score three turns, draw back 1.2 mm, a quarter to half turn to twist the stub,",
                      "draw off, eject. At 5 mm pitch the neighbours' jacket edges are 4.15 mm from k's axis:",
                      "without the snout their tips butt the head's face. At 2.5 mm the snout would have to be",
                      "<= 2.8 mm, so there k is lifted ~9 mm into the head instead (procedure-is-the-machine p1c)."],
            size=11)
    s.save("a8b-spindle-with-touch-off.svg")


# ---------------------------------------------------------------------------
def a2b():
    s = Svg(1000, 560, "a2b Gang stroke: the docked cassette in a stop-block die set under the idle 12-ton press",
            "schematic section across the row, not to scale; 5 stations at strip pitch")
    s.rect(80, 90, 640, 40, fill=STEEL, stroke="#556")
    s.text(86, 114, "upper shoe (pushed by the VEVOR jack), N punches with B-profiles", size=11)
    s.rect(80, 330, 640, 40, fill=STEEL, stroke="#556")
    s.text(86, 356, "lower shoe on a load cell or strain gauges; N anvils rise through windows", size=11)
    for x in (90, 690):
        s.rect(x, 130, 20, 20, fill="#555")
        s.rect(x, 310, 20, 20, fill="#555")
        s.line(x + 10, 150, x + 10, 310, stroke="#555", sw=4)
    s.lines(740, 150, ["guide posts; hardened stop", "blocks meet the upper shoe", "at the crimp height"], size=11)
    for i in range(5):
        x = 180 + i * 100
        s.rect(x - 14, 130, 28, 60, fill="#999", stroke="#333")
        s.rect(x - 14, 260, 28, 70, fill="#888", stroke="#333")
        s.rect(x - 16, 236, 32, 16, fill=BRASS, stroke=BRASS_S)
        s.circle(x, 224, 9, fill=SILICONE, stroke=SILICONE)
    s.rect(140, 252, 480, 8, fill="#cfd6dd", stroke="#556")
    s.lines(740, 250, ["strip pallet: windows for the", "anvils; a lance relief in each anvil"], size=10)
    s.rect(640, 190, 40, 140, fill="#666", stroke="#333")
    s.text(620, 186, "stop block", size=10)
    s.lines(40, 410, ["Force for the stroke: 2.4-7.8 kN (3 contacts), 4.0-12.9 kN (5), 7-23 kN (J1's 9), against ~118 kN.",
                      "A missing conductor drops the summed force 12-20 %, a missing contact 20 %; one strand of 60 is invisible.",
                      "Continuity to the carrier before the stroke names the station; the camera frame of the docked row too.",
                      "Dies: N harvested pairs (each with its own side adjustment and height shim), one wire-EDM plate pair,",
                      "or two strokes with simpler single-arch plates (conductor barrels, then insulation barrels).",
                      "At 7.1 mm pitch a one-piece crimper plate leaves 5.1-5.6 mm webs between profiles (force-and-form f7).",
                      "Target height scales with channel width: a 1.5 mm-channel height copied to a 1.6 mm channel over-compacts."],
            size=11)
    s.save("a2b-gang-press-stop-die.svg")


# ---------------------------------------------------------------------------
def a2c():
    s = Svg(1000, 600, "a2c Loose-contact cassette: kit contacts in keyed printed nests",
            "schematic, not to scale")
    s.text(20, 74, "A. One pocket, from above and in section", weight="bold")
    s.rect(80, 100, 60, 44, fill="#eee", stroke="#555")
    s.rect(84, 104, 52, 36, fill=BRASS, stroke=BRASS_S)
    s.rect(92, 144, 36, 110, fill="#f8f8f8", stroke="#999", dash="3 2")
    s.rect(78, 144, 64, 6, fill="#555")
    s.lines(160, 110, ["box pocket ~2.0 x 2.45 mm, box floor on the pocket floor",
                       "rear shoulder (dark) behind the box: the pull reaction",
                       "open cradle under the barrels (or a steel anvil insert)",
                       "lance relief on ONE side: a reversed contact does not drop in"], size=11)
    s.rect(560, 110, 120, 40, fill="#eee", stroke="#555")
    s.rect(580, 150, 20, 12, fill="#eee", stroke="#555")
    s.text(610, 160, "lance relief", size=10)
    s.text(20, 290, "B. The nest bar at a free pitch; each pocket set back by its conductor's fan recession",
           weight="bold")
    offs = [0.0, 0.77, 1.65]
    xs = [120, 220, 320, 420, 520]
    yb = 330
    setback = [1.65, 0.77, 0.0, 0.77, 1.65]
    for x, sb in zip(xs, setback):
        y = yb + sb * 12
        s.rect(x - 16, y, 32, 60, fill=BRASS, stroke=BRASS_S)
        s.line(x, y + 60, x, 470, stroke=SILICONE, sw=9)
        s.text(x - 12, y - 6, f"{sb:.2f}", size=10)
    s.rect(80, 470, 480, 30, fill=BLUE, stroke=BLUE_S)
    s.text(86, 490, "ribbon pallet, stripped webbed before the split (procedure-is-the-machine p7), fanned to 5 mm",
           size=10, fill=BLUE_S)
    s.lines(600, 330, ["5P at 5 mm: pockets set back 0, 0.77, 1.65 mm from",
                       "the centre out [P3 s1], printed from the same",
                       "groove geometry as the fan block, so a strip made",
                       "before the split docks without an equal-path fan.",
                       "",
                       "Loading: tweezers; a stapler-style stick; shaking",
                       "on a coin motor [Prime]; or strip cut one at a time.",
                       "",
                       "At 3.4 mm (change-the-question c1): odd conductors",
                       "dock with no fan; each pocket becomes a steel anvil",
                       "slide lifted into a fixed punch.",
                       "",
                       "With a10's tack: close each insulation barrel",
                       "loosely in the bar, lift, crimp each in the SN-2549."],
            size=11)
    s.save("a2c-loose-contact-cassette.svg")


# ---------------------------------------------------------------------------
def a9():
    s = Svg(1000, 780, "a9 The reel end docks: terminate at the reel clamp, dock on reel strip, crimp through a feedless applicator, cut last",
            "schematic plan, not to scale; a combination with procedure-is-the-machine p6, p7 and p3; 4P reel shown")
    s.text(20, 74, "A. Plan of the bench: the clamp rides one X axis past four lanes", weight="bold")
    # X rail
    s.rect(110, 330, 860, 10, fill=STEEL, stroke="#556")
    s.text(200, 322, "X carriage: MGN12 rail, NEMA 17 on Tr8x2 [Prime rows]", size=10)
    # lanes
    lanes = [(170, "draw + cut"), (300, "insert + test"), (470, "anvil"), (650, "dock")]
    for x, name in lanes:
        s.line(x, 344, x, 362, stroke="#555")
        s.text(x - 30, 376, name, size=10, weight="bold")
    # clamp carriage at the dock lane
    cx = 650
    s.rect(cx - 50, 270, 100, 56, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(cx + 56, 300, "channel clamp + fan block", size=10, fill=BLUE_S)
    s.line(cx - 70, 270, cx + 70, 270, stroke=RED, dash="3 2")
    s.text(cx + 74, 274, "clamp face = cut line = split root", size=10, fill=RED)
    # ribbon from reel below
    s.path(f"M{cx},326 L{cx},420", stroke=SILICONE, sw=12)
    s.text(cx + 10, 410, "from the reel (belt feed + encoder)", size=10)
    s.circle(cx - 150, 450, 34, fill="#f2f2f2", stroke="#555")
    s.circle(cx - 150, 450, 14, fill="#ddd", stroke="#555")
    s.path(f"M{cx - 116},450 C{cx - 60},450 {cx},440 {cx},420", stroke=SILICONE, sw=6, dash="4 3")
    s.lines(cx - 330, 420, ["4P reel, 80 mm hub radius;", "hub socket + flying lead;", "no slip ring: the reel",
                            "stands still while it works"], size=10)
    # carrier track along X through the anvil, contacts first, conductors drawn over them
    pitch = 44
    xs = [cx - 1.5 * pitch + i * pitch for i in range(4)]
    s.rect(380, 196, 560, 8, fill=BRASS, stroke=BRASS_S)
    s.text(730, 226, "SXH strip on a fixed track from +X;", size=10)
    s.text(730, 240, "sprocket feeder (borrowed-machines b2)", size=10)
    for k in range(-5, 8):
        x = cx - 1.5 * pitch + k * pitch
        if 380 < x < 940:
            s.rect(x - 7, 136, 14, 60, fill=BRASS, stroke=BRASS_S)
    for i, x in enumerate(xs):
        x0 = cx - 18 + i * 12
        s.path(f"M{x0:.0f},270 C{x0:.0f},240 {x:.0f},235 {x:.0f},205 L{x:.0f},176", stroke=SILICONE, sw=8)
        s.line(x, 176, x, 150, stroke=COPPER, sw=3)
    # applicator at the anvil lane
    s.rect(420, 112, 100, 76, fill="none", stroke="#555", dash="5 3")
    s.lines(380, 90, ["OTP applicator, feed and shear punch removed; 3-4 mm eccentric,",
                      "NEMA 17 + 26.85:1 [Prime]; pilot enters the carrier slot"], size=10)
    s.line(590, 300, 470, 300, arrow=True)
    s.text(350, 290, "docked row indexes -X, one pitch per turn", size=10)
    # insertion lane
    s.rect(270, 150, 60, 50, fill="#eee", stroke="#555")
    s.lines(250, 120, ["XHP on a B4B-XH wafer", "on a load cell"], size=10)
    # draw lane: puller rail along +Y
    s.line(170, 320, 170, 96, stroke="#999", sw=4)
    s.lines(40, 110, ["puller: belt carriage", "along +Y; grips the", "ribbon behind the", "housing (fold on a bar);",
                      "razor cuts at the", "clamp face"], size=10)
    s.text(20, 520, "B. Side view of the equal-path fan (4P to 7.1 mm): the inner grooves carry humps", weight="bold")
    s.path("M60,620 L400,620", stroke=SIL_LIGHT, sw=8)
    s.path("M60,620 C140,620 150,570 230,570 C310,570 320,620 400,620", stroke=SILICONE, sw=8)
    s.text(60, 645, "outer groove (flat, grey) and inner groove (humped), same path length", size=10)
    s.lines(430, 560, ["inner pair: hump 3.3 mm over the fan's 16.7 mm, bend R ~4.3 mm;",
                       "5P centre: 5.1 mm over 21.4 mm, R ~4.5 [P3 s1]. Every tip recedes",
                       "the same 2.05 mm (4P) or 2.77 mm (5P), so the strip line made before",
                       "the split stays straight. The humps take a set (the strands yield",
                       "below R 39-78 mm); the insertion clamp pulls them straight at",
                       "0.06-0.23 N [calc F s5], and the loom leaves with every conductor",
                       "one length from the root."], size=11)
    s.text(20, 680, "C. One end, in order", weight="bold")
    s.lines(20, 700, ["1 feed out to a grounded tip stop (touch-off through the hub socket); 2 strip webbed: two razors on steel "
                      "stops, slide the slug off (p7);",
                      "3 zip from the slug's gaps back to 1 mm short of the clamp face (a7's tines); 4 equal-path fan; "
                      "5 dock; continuity to the carrier;",
                      "6 crimp, one per turn; 7 back at the dock: pad or neck blades, 20 N pull each, shear comb; "
                      "8 insert; 9 test on the wafer through the hub;",
                      "10 draw the loom's length and cut at the clamp face, which leaves the next end square."],
            size=10)
    s.save("a9-reel-end-docks.svg")


# ---------------------------------------------------------------------------
def a10():
    s = Svg(1000, 780, "a10 Dock, tack, cut: then each contact crimped alone in a keyed steel nest",
            "schematic, not to scale; a combination with force-and-form f9, f3, f6 and f4, and change-the-question c1b's tack")
    s.text(20, 74, "A. Side section at the strip pallet, one contact of the docked row", weight="bold")
    # pallet plate with slot pins (drops for the shear)
    s.rect(150, 214, 150, 14, fill="#cfd6dd", stroke="#556")
    s.lines(60, 244, ["carrier plate on slot pins", "(drops for the shear)"], size=10)
    # carrier
    s.rect(220, 206, 80, 8, fill=BRASS, stroke=BRASS_S)
    # rail under insulation barrel
    s.rect(302, 206, 58, 40, fill="#9aa4ae", stroke="#556")
    s.lines(302, 262, ["hardened rail under the", "insulation barrels only;", "its rear edge = shear edge"], size=10)
    # contact
    s.path("M302,206 L302,176 M340,206 L340,176", stroke=BRASS_S, sw=3)
    s.rect(302, 202, 38, 4, fill=BRASS, stroke=BRASS_S)
    s.path("M350,206 L350,186 M378,206 L378,186", stroke=BRASS_S, sw=3)
    s.rect(350, 202, 28, 4, fill=BRASS, stroke=BRASS_S)
    s.rect(390, 164, 64, 42, fill=BRASS, stroke=BRASS_S)
    s.line(420, 206, 408, 222, stroke=BRASS_S, sw=3)
    s.text(430, 236, "lance hangs free (a flat shelf would prop it 7.6-15.9 deg)", size=10)
    # conductor
    s.line(60, 190, 340, 190, stroke=SILICONE, sw=12)
    s.line(340, 192, 384, 192, stroke=COPPER, sw=5)
    s.rect(40, 170, 90, 40, fill=BLUE, stroke=BLUE_S)
    s.text(40, 164, "ribbon pallet (fan block face)", size=10, fill=BLUE_S)
    # tack comb
    s.poly([(296, 110), (346, 110), (346, 160), (336, 172), (306, 172), (296, 160)], fill="#8894a0", stroke="#333")
    s.line(321, 96, 321, 108, arrow=True)
    s.lines(480, 110, ["1 dock: every conductor drops into every open contact; continuity to the carrier",
                       "2 tack: a notched steel comb closes every insulation barrel loosely in one stroke",
                       "   to a hard stop (165-660 N for a 5P [w3 s3]); conductor barrels stay open",
                       "3 cut: the comb stays down as the pad; the carrier plate drops past the rail's",
                       "   edge and shears every tab (250-800 N for a 5P)",
                       "4 lift: every contact now hangs from its own conductor, one strip pitch apart"],
            size=10)
    s.text(20, 330, "B. The heavy station: one tacked contact at a time", weight="bold")
    s.path("M80,370 L80,590 L360,590 L360,550 L140,550 L140,410 L360,410 L360,370 Z", fill=STEEL, stroke="#556")
    s.text(90, 386, "steel C (f4), throat toward the wire", size=10)
    s.rect(240, 430, 30, 50, fill="#999", stroke="#333")
    s.rect(274, 440, 14, 40, fill="#bbb", stroke="#333")
    s.lines(380, 420, ["conductor crimper on f3's knee (NEMA 17 on Tr8x2, 60-160 N push), to a geometric bottom;",
                       "f6's insulation blade beside it on its own drive; 0.001 mm indicator across the dies"],
            size=10)
    s.rect(230, 510, 70, 40, fill="#777", stroke="#333")
    s.lines(380, 500, ["keyed nest on a button load cell: box slot with lead-in chamfers, lance relief,",
                       "front stop; the contact goes in vertically, then +Y to the stop"], size=10)
    s.rect(236, 484, 60, 12, fill=BRASS, stroke=BRASS_S)
    s.line(160, 490, 236, 490, stroke=SILICONE, sw=8)
    s.lines(380, 550, ["neighbours hang one strip pitch away: jaws <= 10.8-11.4 mm wide where they pass [w3 s3];",
                       "the far-end port reads which conductor touches the grounded nest (identity before force);",
                       "pull: a 0.3 mm blade on the box's rear face, a jaw on the jacket, ~20 N"], size=10)
    s.text(20, 640, "C. a10b, no motor: the same docked, tacked, sheared row, crimped by hand", weight="bold")
    s.lines(20, 660, ["The tack holds each contact on its jacket at its docked depth and roll: the locator the SN-2549 lacks.",
                      "The person seats one tacked contact in the SN-2549's XH nest, squeezes to the ratchet's release,",
                      "and moves to the next. Tack comb and shear on POWERTEC toggle clamps ($18.25 for two [Prime]).",
                      "Kit contacts on hand can take the strip's place in a2c's keyed nest bar."], size=11)
    s.save("a10-dock-tack-then-nest.svg")


if __name__ == "__main__":
    for f in (a2, a2e, a3, a4, a5, a6, a8b, a2b, a2c, a9, a10):
        f()
    print("written")
