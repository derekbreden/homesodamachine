"""Final-pass sketches for machine-that-sees-and-learns.

Run: python3 make_sketches_final.py   (writes the w3-*.svg files beside this script)

w3-v8-shadow-test.svg uses cited dimensions (captions say which). The others are
schematic: proportions chosen to be read, not measured.
"""
import math
from make_sketches import SVG, header, INK, GREY, LIGHT, DARK, VIEW, FORCE, GOOD, BAD

STEEL = "#afb8c1"
TIN = "#c9d1d9"
JACKET = "#24292f"
AMBER = "#9a6700"
MCU = "#8250df"
PERSON = "#bf3989"


# ------------------------------------------------------------------ v8 / v9 shadow test
def shadow_test():
    s = SVG(1000, 680, "shadow test in the open conductor barrel")
    header(s, "The shadow test: a bundle held by its jacket hovers off the floor; a strand on the floor casts no displaced shadow",
           "Left: end view looking along the wire at mid conductor barrel, 1 mm = 110 px, from cited dimensions. Right: side view, schematic.")
    k = 110.0
    cx, fy = 330, 540                     # barrel centre; y of the anvil top (contact's underside)
    def X(mm): return cx + mm * k
    def Y(mm): return fy - mm * k
    t = 0.20                              # stock [xh-facts s1]
    half_out = 1.79 / 2                   # open width 1.68-1.90 [xh-facts s1], mean
    h_wing = 1.55                         # wing tips 1.50-1.60 [xh-facts s1]
    s.rect(X(-2.0), Y(0), 4.0 * k, 0.5 * k, fill="#24292f")
    s.text(X(0), Y(0) + 34, "anvil (blackened)", size=11, anchor="middle", fill="#ffffff")
    s.rect(X(-half_out), Y(t), 2 * half_out * k, t * k, fill=TIN)
    s.rect(X(-half_out), Y(h_wing), t * k, (h_wing - t) * k, fill=TIN)
    s.rect(X(half_out - t), Y(h_wing), t * k, (h_wing - t) * k, fill=TIN)
    s.text(X(half_out) + 10, Y(h_wing) + 10, "wing tips 1.50-1.60 mm up", size=10.5, fill=DARK)
    s.text(X(half_out) + 10, Y(h_wing) + 24, "open width 1.68-1.90 [xh-facts]", size=10.5, fill=DARK)
    floor = t
    r = 0.36
    bot = floor + 0.41                    # bundle bottom 0.30-0.52 above the floor [bm W s2]; mid drawn
    ccy = bot + r
    el = math.radians(65)
    for side, col in ((-1, AMBER), (1, VIEW)):
        sx = -side * (ccy - floor) / math.tan(el)
        w = 2 * r / math.sin(el)
        s.rect(X(sx - w / 2), Y(floor) - 4, w * k, 4, fill=col, stroke=col, opacity=0.6)
        L = 1.8
        lx = side * L * math.cos(el); ly = ccy + L * math.sin(el)
        s.line(X(lx), Y(ly), X(sx + side * w / 2), Y(floor), stroke=col, dash="5 4")
        s.line(X(lx), Y(ly), X(sx - side * w / 2), Y(floor), stroke=col, dash="5 4")
        s.circle(X(lx), Y(ly), 8, fill="#fff8c5", stroke=col)
    s.circle(X(0), Y(ccy), r * k, fill="#d0d7de", stroke=INK)
    s.text(X(0), Y(ccy) + 4, "bundle 0.72", size=10.5, anchor="middle")
    s.text(X(-0.95), Y(ccy + 1.85), "LED at 60-75 deg, left", size=10.5, anchor="middle", fill=AMBER)
    s.text(X(0.95), Y(ccy + 1.85), "LED at 60-75 deg, right", size=10.5, anchor="middle", fill=VIEW)
    s.line(X(-0.62), Y(floor), X(-0.62), Y(bot), stroke=GOOD, sw=1.5)
    s.line(X(-0.67), Y(bot), X(-0.57), Y(bot), stroke=GOOD)
    s.text(X(-1.00), Y(floor + 0.25), "0.30-0.52", size=10.5, anchor="end", fill=GOOD)
    s.text(X(-1.00), Y(floor + 0.25) + 13, "off the floor", size=10.5, anchor="end", fill=GOOD)
    s.circle(X(0.60), Y(floor + 0.04), max(4, 0.04 * k), fill="#9aa4ae", stroke=BAD, sw=1.5)
    s.line(X(0.62), Y(floor + 0.10), X(1.25), Y(0.95), stroke=BAD)
    s.lines(X(1.27), Y(0.98), ["a strand on the floor:", "silver with no shadow", "beside it -> fail"], size=10.5, fill=BAD)
    s.camera(X(0), Y(3.35), ang=90)
    s.text(X(0) + 26, Y(3.35) - 4, "top camera, straight down", size=10.5, fill=VIEW)
    s.text(X(0) + 26, Y(3.35) + 10, "(or through v9's 45 deg mirror)", size=10.5, fill=VIEW)
    s.lines(20, Y(0) + 76, ["Lit in turn, each LED throws the raised bundle's shadow 0.08-0.30 mm further aside than a bundle lying on the floor",
                            "would (10-36 px at 122 px/mm, 7-26 px at 86 px/mm) [bm W s2]. The coloured bars are each LED's shadow."],
            size=10.5, fill=DARK, gap=14)

    ox, oy = 620, 140
    s.rect(ox, oy - 30, 360, 330, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ox + 12, oy - 10, "side view (schematic): why the bundle hovers", size=12, weight="bold")
    base = oy + 210
    s.rect(ox + 20, base, 320, 16, fill="#24292f")
    s.rect(ox + 40, base - 8, 70, 8, fill=TIN)
    s.poly([(ox + 40, base - 8), (ox + 40, base - 64), (ox + 70, base - 74), (ox + 80, base - 74),
            (ox + 110, base - 64), (ox + 110, base - 8)], fill="none", stroke=STEEL, sw=3, closed=False)
    s.text(ox + 75, base - 82, "tacked", size=10, anchor="middle", fill=FORCE)
    s.rect(ox + 20, base - 60, 90, 44, fill=JACKET)
    s.text(ox + 60, base + 36, "jacket held", size=10, anchor="middle")
    s.rect(ox + 170, base - 8, 70, 8, fill=TIN)
    s.poly([(ox + 170, base - 8), (ox + 170, base - 50)], fill="none", stroke=STEEL, sw=3, closed=False)
    s.poly([(ox + 240, base - 8), (ox + 240, base - 50)], fill="none", stroke=STEEL, sw=3, closed=False)
    s.rect(ox + 110, base - 44, 150, 13, fill="#d0d7de")
    s.text(ox + 205, base - 54, "open conductor barrel", size=10, anchor="middle")
    s.line(ox + 255, base - 8, ox + 255, base - 31, stroke=GOOD, sw=2)
    s.text(ox + 205, base + 36, "gap under the bundle", size=10, anchor="middle", fill=GOOD)
    s.rect(ox + 280, base - 40, 50, 40, fill=TIN)
    s.text(ox + 305, base - 46, "box", size=10, anchor="middle")
    s.lines(ox + 14, oy + 18, ["The jacket sits in the insulation barrel, so the bare",
                               "bundle leaves it at the jacket's height and crosses the",
                               "open conductor barrel above its floor. Focus cannot",
                               "tell 0.3-0.5 mm apart: depth of field is ~0.55-0.76 mm",
                               "at 122 px/mm [bm W s2]. A low LED can: a raised",
                               "bundle's shadow falls beside it; a strand on the",
                               "floor has none."], size=10.5, fill=DARK, gap=14)
    s.lines(20, 650, ["Cited: clone drawings for the barrel [xh-facts s1]; bundle 0.72 mm [xh-facts s7]; hover and shadow offsets from borrowed-machines'",
                      "exchange calc s2, taking the two barrel floors as one plane. Unproven on tin: one photograph with two LEDs at ~65 deg settles it."],
            size=10.5, fill=DARK, gap=14)
    s.save("w3-v8-shadow-test.svg")


# ------------------------------------------------------------------ v9 tack at the anvil
def v9():
    s = SVG(1100, 760, "v9 tack at the anvil")
    header(s, "v9  Tack at the anvil: tack, look and crimp at one datum, a contact still on its carrier in a stopped crank applicator",
           "Schematic side elevation, wire axis left to right, box at the right; crank-angle timeline below. Not to scale.")
    # applicator base and anvil
    s.rect(300, 400, 520, 40, fill="#d0d7de")
    s.text(560, 425, "applicator base (the reference for fixed)", size=11, anchor="middle")
    s.rect(470, 360, 240, 40, fill="#24292f")
    s.text(590, 385, "anvil: insulation + conductor", size=10.5, anchor="middle", fill="#ffffff")
    # contact on anvil: insulation barrel, conductor barrel, box
    s.rect(480, 350, 60, 10, fill=TIN)          # insulation barrel floor
    s.rect(560, 350, 60, 10, fill=TIN)          # conductor barrel floor
    s.rect(640, 330, 60, 30, fill=TIN)          # box
    s.text(670, 324, "box", size=10, anchor="middle")
    s.rect(462, 356, 16, 10, fill=AMBER, stroke=AMBER)
    s.line(462, 366, 440, 452, stroke=AMBER)
    s.text(440, 462, "carrier tab (strip runs into the page;", size=10, anchor="end", fill=AMBER)
    s.text(440, 475, "pre-feed: the contact waits on the anvil)", size=10, anchor="end", fill=AMBER)
    # tacked wings over jacket
    s.poly([(480, 350), (482, 322), (510, 314), (538, 322), (540, 350)], fill="none", stroke=STEEL, sw=3, closed=False)
    # wire: jacket + bundle
    s.rect(120, 326, 425, 22, fill=JACKET)
    s.rect(545, 333, 88, 8, fill="#9aa4ae")
    # open conductor wings
    s.line(562, 350, 562, 332, stroke=STEEL, sw=3)
    s.line(618, 350, 618, 332, stroke=STEEL, sw=3)
    # raised crimpers
    s.rect(470, 80, 240, 60, fill=STEEL)
    s.text(590, 105, "ram with both crimpers, raised", size=11, anchor="middle")
    s.text(590, 121, "at top dead centre", size=11, anchor="middle")
    s.line(590, 145, 590, 312, stroke=GREY, dash="3 4")
    s.text(598, 190, "~23-42 mm clear [estimate];", size=10.5, fill=DARK)
    s.text(598, 204, "the jack test measures it", size=10.5, fill=DARK)
    # T-arm former
    s.rect(500, 200, 20, 110, fill=STEEL, stroke=FORCE)
    s.line(510, 170, 510, 205, stroke=FORCE, sw=3, arrow="force")
    s.rect(430, 160, 60, 26, fill="#f6f0ff", stroke=MCU)
    s.text(460, 177, "servo", size=10, anchor="middle", fill=MCU)
    s.lines(250, 214, ["T-arm (swings in, then out):", "former = scanned insulation", "profile + 0.1-0.2 mm, to a", "stop at H_f + 0.2-0.5 mm;",
                        "20 kg cell in the link"], size=10.5, fill=FORCE, gap=14)
    # M-arm mirror + camera
    s.poly([(575, 300), (605, 270), (609, 274), (579, 304)], fill="#ddf4ff", stroke=VIEW)
    s.line(590, 312, 590, 290, stroke=VIEW, dash="3 3", arrow=None)
    s.line(592, 287, 760, 287, stroke=VIEW, dash="3 3")
    s.camera(790, 287, ang=180)
    s.lines(812, 260, ["M-arm: 10 mm mirror at 45 deg,", "IMX298 camera looking in;", "two LEDs at 60-75 deg:", "the shadow test"], size=10.5, fill=VIEW, gap=14)
    s.circle(548, 262, 6, fill="#fff8c5", stroke=AMBER)
    s.circle(634, 262, 6, fill="#fff8c5", stroke=AMBER)
    # cassette, fork, foot
    s.rect(40, 346, 150, 40, fill="#ddf4ff")
    s.text(115, 400, "b1 cassette: band folded back,", size=10.5, anchor="middle")
    s.text(115, 414, "shuttle across and along", size=10.5, anchor="middle")
    s.rect(210, 300, 14, 30, fill=GREY)
    s.text(217, 294, "fork", size=10, anchor="middle")
    s.rect(420, 312, 30, 12, fill=GREY)
    s.text(435, 306, "foot", size=10, anchor="middle")
    s.text(40, 434, "far end: pogo block; applicator grounded", size=10.5, fill=DARK)
    # neck fork and silhouette in the dwell (drawn to the right, ghosted)
    s.rect(860, 360, 180, 60, fill="#fffbe6", stroke=AMBER, dash="4 3")
    s.lines(868, 378, ["dwell position, >= 7 mm out:", "neck fork on the box's rear,", "20 N pull, silhouette + box roll"], size=10, fill=AMBER, gap=13)
    # force path
    s.text(840, 150, "crank 15 mm, rod with 4 kN disc stack", size=10.5, fill=FORCE)
    s.text(840, 164, "(switch in the enable line), 12 t frame", size=10.5, fill=FORCE)
    s.line(830, 145, 715, 110, stroke=FORCE, arrow="force")

    # timeline
    y0 = 520
    s.text(20, y0 - 18, "One conductor against crank angle (0 deg = top dead centre, 180 = bottom)", size=12.5, weight="bold")
    xa, xb = 60, 1060
    def A(deg): return xa + deg / 360 * (xb - xa)
    s.line(xa, y0 + 110, xb, y0 + 110)
    for d in (0, 90, 180, 270, 360):
        s.line(A(d), y0 + 105, A(d), y0 + 115)
        s.text(A(d), y0 + 130, f"{d}", size=10, anchor="middle")
    s.rect(A(0) - 4, y0, 84, 96, fill="#ddf4ff", stroke=VIEW)
    s.lines(A(0) + 2, y0 + 14, ["stopped at 0:", "contact alone;", "lay in; continuity;", "TACK; let go;", "TOP LOOK"], size=9.5, fill=INK, gap=13)
    s.rect(A(28), y0 + 30, A(160) - A(28), 22, fill="#f6f8fa", stroke=GREY)
    s.text(A(94), y0 + 45, "fast to a taught angle", size=10, anchor="middle")
    s.rect(A(160), y0 + 30, A(180) - A(160), 22, fill="#ffebe9", stroke=BAD)
    s.text(A(170), y0 + 22, "crawl 0.05-0.1 mm/s, 9-34 s", size=10, anchor="middle", fill=BAD)
    s.text(A(182), y0 + 70, "bottom: both barrels,", size=10, fill=FORCE)
    s.text(A(182), y0 + 83, "tab sheared", size=10, fill=FORCE)
    s.rect(A(220), y0 + 30, A(265) - A(220), 22, fill="#fffbe6", stroke=AMBER)
    s.text(A(242), y0 + 22, "dwell 220-265", size=10, anchor="middle", fill=AMBER)
    s.rect(A(266), y0 + 60, A(285) - A(266), 22, fill="#dafbe1", stroke=GOOD)
    s.text(A(276), y0 + 98, "pre-feed", size=10, anchor="middle", fill=GOOD)
    s.lines(20, y0 + 160, [
        "Fail at the top look: draw the conductor straight back, flat (the tab bends at 4-12 N along the wire but at 0.5-1.7 N sideways);",
        "the empty tacked contact is crimped empty on the next turn and blown off the anvil in the dwell; a fresh contact pre-feeds.",
        "72-142 s a conductor, 1.1-2.1 h a unit [bm W s11]. On b1c's one shaft the same stop sits at 0-40 deg, where the room is."],
        size=11, fill=DARK, gap=16)
    s.save("w3-v9-tack-at-the-anvil.svg")


# ------------------------------------------------------------------ v9b by hand
def v9b():
    s = SVG(1000, 620, "v9b tack by hand on the jack test")
    header(s, "v9b  The tack by hand on the jack-test applicator: lay in, throw a toggle, look, pump",
           "Schematic front elevation of the idle 12-ton shop press with an applicator on its bed. Not to scale.")
    # press frame
    s.rect(120, 70, 24, 470, fill="#d0d7de")
    s.rect(560, 70, 24, 470, fill="#d0d7de")
    s.rect(120, 70, 464, 30, fill="#d0d7de")
    s.rect(120, 470, 464, 26, fill="#d0d7de")
    s.text(352, 489, "press bed (VEVOR 12 t, idle)", size=11, anchor="middle")
    # jack upside down on top beam, ram down
    s.rect(300, 100, 100, 90, fill=GREY)
    s.text(350, 150, "bottle jack", size=11, anchor="middle", fill="#ffffff")
    s.rect(335, 190, 30, 60, fill=STEEL)
    s.rect(320, 250, 60, 22, fill="#ddf4ff", stroke=INK)
    s.text(392, 265, "T-slot adapter + stop collar", size=10.5)
    s.line(420, 150, 470, 150, stroke=PERSON, sw=3)
    s.text(478, 146, "hand pump", size=10.5, fill=PERSON)
    s.text(478, 160, "(or air-over-hydraulic)", size=10, fill=DARK)
    # applicator
    s.rect(250, 290, 200, 180, fill="#f6f8fa", stroke=INK)
    s.text(258, 330, "OTP applicator,", size=11)
    s.text(258, 344, "pre-feed", size=11)
    s.rect(320, 272, 60, 40, fill=STEEL)
    s.rect(300, 420, 100, 30, fill="#24292f")
    s.text(350, 440, "anvil", size=10, anchor="middle", fill="#ffffff")
    s.rect(335, 405, 30, 15, fill=TIN)
    s.text(350, 398, "contact waits", size=10, anchor="middle")
    s.rect(160, 440, 90, 8, fill=AMBER, stroke=AMBER)
    s.text(160, 462, "reel strip", size=10, fill=AMBER)
    # toggle former
    s.rect(420, 340, 60, 20, fill=GREY)
    s.line(480, 350, 598, 262, stroke=FORCE)
    s.text(600, 250, "toggle clamp", size=10.5)
    s.rect(410, 360, 10, 50, fill=STEEL, stroke=FORCE)
    s.lines(600, 264, ["-> former over the insulation", "barrel, screw stop at the", "tack height"], size=10, fill=FORCE, gap=12)
    # mirror + camera
    s.poly([(360, 382), (378, 364), (382, 368), (364, 386)], fill="#ddf4ff", stroke=VIEW)
    s.line(382, 366, 640, 366, stroke=VIEW, dash="3 3")
    s.camera(660, 366, ang=180)
    s.text(690, 350, "ELP (on hand) into a", size=10.5, fill=VIEW)
    s.text(690, 364, "swing-in mirror; two LEDs", size=10.5, fill=VIEW)
    s.text(690, 378, "at ~65 deg; live on the Mac", size=10.5, fill=VIEW)
    # hand laying in
    s.poly([(170, 380), (240, 400), (300, 405)], fill="none", stroke=JACKET, sw=6, closed=False)
    s.text(170, 370, "Derek lays the conductor in", size=10.5, fill=PERSON)
    # screen
    s.rect(770, 130, 210, 140, fill="#f6f8fa", stroke=INK, rx=6)
    s.lines(782, 152, ["on screen: the open barrel", "from straight above,", "each LED in turn:", "strands inside the wings,",
                        "brush, edge in window,", "the bundle's shadow"], size=10.5, fill=DARK, gap=14)
    s.lines(20, 560, [
        "Per conductor: lay in by hand, throw the toggle (tack), swing the mirror in and look, then pump to the collar; release, and the pre-feed brings the next.",
        "A bad look: draw the conductor straight back, flat; pump the tacked empty through as scrap. 31-93 s a crimp, 27-82 min a unit [calc w3_final s4]:",
        "slower than today by hand. It answers the tack's grip, its height and width, the order (by section), and the room under the crimpers."],
        size=11, fill=DARK, gap=16)
    s.save("w3-v9b-by-hand.svg")


# ------------------------------------------------------------------ v1b four ways
def v1b():
    s = SVG(1100, 560, "v1b four ways to give the pallet its axes")
    header(s, "v1b  Four ways to give the pallet its three axes, by what the crimp host weighs",
           "Schematic side views. Arrows: along = along the wire; across = key to key (into the page); up = height, set once.")
    panels = [
        ("A  press rides the bed", "light host: a tack station, a small die set"),
        ("B  the Ender on its back", "any bench-fixed press (12 t frame, crank, mute press)"),
        ("C  two rails in front", "the same presses, built (b1's shuttle)"),
        ("D  head on the carriage", "b3's self-contained head; ribbon on the bed"),
    ]
    w, gap = 250, 20
    for i, (t, sub) in enumerate(panels):
        x = 20 + i * (w + gap)
        s.rect(x, 70, w, 400, fill="#ffffff", stroke=GREY, rx=6)
        s.text(x + 10, 92, t, size=12.5, weight="bold")
        s.text(x + 10, 108, sub, size=9.8, fill=DARK)
        s.rect(x + 15, 420, w - 30, 14, fill="#d0d7de")       # bench
    # A
    x = 20
    s.rect(x + 30, 170, 10, 250, fill=GREY); s.rect(x + 30, 170, 190, 10, fill=GREY)   # frame
    s.rect(x + 60, 360, 150, 10, fill=STEEL)                                          # bed
    s.rect(x + 130, 300, 50, 60, fill="#f6f8fa", stroke=INK); s.text(x + 155, 334, "press", size=10, anchor="middle")
    s.rect(x + 70, 190, 50, 60, fill="#ddf4ff"); s.text(x + 95, 224, "fan", size=10, anchor="middle")
    s.text(x + 95, 262, "on carriage", size=9.5, anchor="middle", fill=DARK)
    s.line(x + 80, 390, x + 200, 390, arrow="ink"); s.text(x + 90, 405, "along: the bed", size=10)
    s.line(x + 150, 250, x + 150, 200, arrow="ink"); s.text(x + 155, 215, "up: gantry", size=10)
    # B
    x = 20 + (w + gap)
    s.rect(x + 20, 390, 150, 12, fill=GREY)               # frame lying on its back
    s.rect(x + 20, 300, 12, 90, fill=GREY)
    s.line(x + 40, 330, x + 160, 330, stroke=STEEL, sw=4); s.text(x + 40, 322, "Z lead screws, lying down", size=9.5, fill=DARK)
    s.rect(x + 100, 336, 50, 30, fill="#ddf4ff"); s.text(x + 125, 356, "fan", size=10, anchor="middle")
    s.rect(x + 180, 300, 55, 120, fill="#f6f8fa", stroke=INK); s.text(x + 207, 360, "press", size=10, anchor="middle")
    s.text(x + 207, 374, "fixed", size=9.5, anchor="middle", fill=DARK)
    s.line(x + 60, 378, x + 170, 378, arrow="ink"); s.text(x + 55, 250, "along: the Z screws", size=10)
    s.text(x + 55, 264, "(0.02-0.09 N.m for a 20 N pull)", size=9.5, fill=DARK)
    s.text(x + 55, 278, "across: the carriage belt", size=10)
    # C
    x = 20 + 2 * (w + gap)
    s.rect(x + 20, 380, 140, 10, fill=STEEL); s.text(x + 10, 342, "MGN12 rails, Tr8 steppers", size=9.5, fill=DARK)
    s.rect(x + 60, 350, 70, 30, fill="#ddf4ff"); s.text(x + 95, 370, "cassette", size=10, anchor="middle")
    s.rect(x + 175, 250, 60, 170, fill="#f6f8fa", stroke=INK); s.text(x + 205, 330, "press", size=10, anchor="middle")
    s.line(x + 40, 400, x + 160, 400, arrow="ink"); s.text(x + 40, 250, "along and across:", size=10)
    s.text(x + 40, 264, "two rails; height fixed", size=10)
    # D
    x = 20 + 3 * (w + gap)
    s.rect(x + 30, 170, 10, 250, fill=GREY); s.rect(x + 30, 170, 190, 10, fill=GREY)
    s.rect(x + 60, 380, 150, 10, fill=STEEL)
    s.rect(x + 80, 356, 90, 24, fill="#ddf4ff"); s.text(x + 125, 373, "fan, keys", size=10, anchor="middle")
    s.rect(x + 120, 200, 60, 90, fill="#f6f8fa", stroke=FORCE); s.text(x + 150, 240, "head:", size=10, anchor="middle")
    s.text(x + 150, 254, "C-frame", size=10, anchor="middle"); s.text(x + 150, 268, "closes force", size=9.5, anchor="middle")
    s.line(x + 80, 405, x + 200, 405, arrow="ink"); s.text(x + 70, 150, "along: the bed carries the ribbon", size=10)
    s.lines(x + 60, 305, ["punch <= 7.45 mm at the", "neighbours' height; throat", "past a 5P fan"], size=9.5, fill=DARK, gap=12)
    s.lines(20, 500, ["In every case the picture closes the loop, so the stage only has to be monotonic and repeatable over a few tenths, approached from one side.",
                      "The only real load on a stage axis is the ~20 N proof pull along the wire: 0.13 N.m on the bed's GT2 belt, 0.02-0.09 N.m on a Tr8 screw [bm W s7]."],
            size=11, fill=DARK, gap=16)
    s.save("w3-v1b-axes.svg")


if __name__ == "__main__":
    shadow_test(); v9(); v9b(); v1b()
