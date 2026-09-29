"""Schematic sketches for the procedure-is-the-machine explorer.

Run: python3 make_sketches.py   (writes the .svg files beside this script)

All drawings are schematic: shapes are placed to show order, references and what moves, not
to scale unless a caption says a dimension came from a cited number. p5-cam-timing.svg and
orders-and-the-person.svg is written by calc/person_timeline.py. p1-crimp-station, p2-turret,
p3-spool-cut-last, p5-camshaft-layout and p5-cam-timing are drawn by make_sketches_w3.py, which
holds their current form; this script draws the cassette, carousel, AMS, p4 and orders sketches.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

BLUE = "#2a5d9f"
RED = "#b03030"
GREEN = "#2f7d4f"
GREY = "#888888"
LIGHT = "#e8eef7"
AMBER = "#c77d10"
INK = "#222222"


class Svg:
    def __init__(self, w, h, title, subtitle=None):
        self.w, self.h = w, h
        self.p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
                  f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif" font-size="12">',
                  '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                  'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                  f'fill="{INK}"/></marker>'
                  '<marker id="arrb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                  'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                  f'fill="{BLUE}"/></marker>'
                  '<marker id="arrr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                  'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                  f'fill="{RED}"/></marker></defs>',
                  f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
                  f'<text x="20" y="28" font-size="16" font-weight="bold" fill="{INK}">{title}</text>']
        if subtitle:
            self.text(20, 47, subtitle, fill="#555", size=11)

    def rect(self, x, y, w, h, fill="none", stroke=INK, sw=1.2, rx=0, dash=None, op=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{op}"' if op is not None else ""
        self.p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                      f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.2, dash=None, arrow=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        a = ""
        if arrow:
            m = {"k": "arr", "b": "arrb", "r": "arrr"}[arrow[0]]
            if "end" in arrow or arrow in ("k", "b", "r"):
                a += f' marker-end="url(#{m})"'
            if "both" in arrow:
                a += f' marker-start="url(#{m})"'
        self.p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{stroke}" stroke-width="{sw}"{d}{a}/>')

    def path(self, d, stroke=INK, sw=1.2, fill="none", dash=None, arrow=None):
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        a = ""
        if arrow:
            m = {"k": "arr", "b": "arrb", "r": "arrr"}[arrow]
            a = f' marker-end="url(#{m})"'
        self.p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}{a}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=1.2):
        self.p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
                      f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="normal", italic=False):
        st = ' font-style="italic"' if italic else ""
        for i, line in enumerate(s.split("\n")):
            line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            self.p.append(f'<text x="{x:.1f}" y="{y + i*(size+3):.1f}" font-size="{size}" fill="{fill}" '
                          f'text-anchor="{anchor}" font-weight="{weight}"{st}>{line}</text>')

    def save(self, name):
        self.p.append("</svg>")
        with open(os.path.join(HERE, name), "w") as f:
            f.write("\n".join(self.p))
        print("wrote", name)


# -------------------------------------------------------------------------------------------
def p1_cassette_and_benches():
    s = Svg(980, 700, "p1 Cassette and benches (schematic)",
            "One printed cassette carries a ribbon end from the person's hands through every bench. "
            "Each bench is useful alone; the cassette's pins are the only shared reference.")
    # cassette plan view
    ox, oy = 40, 80
    s.text(ox, oy, "The cassette, plan view (J1: 5P + 4P into keys 1-9)", size=13, weight="bold")
    oy += 15
    # tail tray
    s.rect(ox, oy + 20, 120, 170, fill="#f4f4f4", stroke=GREY)
    s.text(ox + 8, oy + 40, "tail tray:\nloom coiled\nflat, 100-600 mm", size=11, fill="#555")
    # ribbons entering
    for i, (w, lab) in enumerate(((8.5 * 4, "5P"), (6.8 * 4, "4P"))):
        y0 = oy + 60 + (0 if i == 0 else 34 + 2)
        s.rect(ox + 120, y0, 120, w, fill="#333", stroke="#333")
        s.text(ox + 150, y0 + w / 2 + 4, lab, fill="#fff", size=11)
    # clamp
    s.rect(ox + 200, oy + 45, 60, 100, fill=LIGHT, stroke=BLUE, sw=1.5)
    s.text(ox + 204, oy + 40, "ribbon clamp\n(cam lever, TPU pads)", size=10, fill=BLUE)
    # datum wall
    s.line(ox + 200, oy + 146, ox + 470, oy + 146, stroke=RED, sw=3)
    s.text(ox + 290, oy + 162, "datum wall: ribbon edge + cassette pins", size=10, fill=RED)
    # fan plate with grooves
    s.rect(ox + 260, oy + 45, 110, 100, fill="#fbfbfb", stroke=GREY)
    s.text(ox + 272, oy + 40, "fan plate + lid", size=10, fill="#555")
    # conductors fanning from 1.7 to 2.5 pitch (exaggerated to 7 px -> 10 px)
    for k in range(9):
        yin = oy + 62 + k * 7.2
        yout = oy + 52 + k * 10.5
        s.path(f"M {ox+260} {yin:.1f} C {ox+310} {yin:.1f}, {ox+320} {yout:.1f}, {ox+370} {yout:.1f}",
               stroke="#333", sw=2.2)
        s.line(ox + 370, yout, ox + 470, yout, stroke="#333", sw=2.2)
        s.text(ox + 476, yout + 4, f"key {k+1}", size=9, fill="#555")
    # comb
    s.rect(ox + 370, oy + 45, 30, 100, fill=LIGHT, stroke=BLUE, sw=1.5)
    s.text(ox + 364, oy + 170 + 8, "comb at 2.5 mm\n(steel pins in print)", size=10, fill=BLUE)
    # trim line
    s.line(ox + 455, oy + 40, ox + 455, oy + 150, stroke=RED, sw=1.5, dash="5,3")
    s.text(ox + 430, oy + 30, "trim line", size=10, fill=RED)
    # pins
    for py in (oy + 30, oy + 160):
        s.circle(ox + 385, py, 6, fill="#fff", stroke=RED, sw=2)
    s.text(ox + 540, oy + 60, "Cassette pins (2 dowel bores or 3 V-grooves) are the reference\n"
                             "every bench locates to. The person's placement is loose; the\n"
                             "first machine operation is a trim against the cassette's own\n"
                             "blade guide, which turns loose lengths into one line.\n\n"
                             "J2: key 3 is blanked by a printed plug, so a conductor\n"
                             "cannot be laid there. J4, J7: the crossing is made here, by\n"
                             "the person, in a raised loft over the fan plate.\n\n"
                             "An ID (printed code or pin pattern) tells each bench which\n"
                             "loom it holds: conductor count, blank keys, strip program.",
           size=11)

    # benches row
    by = 400
    s.text(40, by - 18, "The benches: a person carries cassettes between them (or p1b's carousel does)",
           size=13, weight="bold")
    benches = [
        ("Load\n(person)", "cut ribbon square,\npeel web ~30 mm,\nlay conductors in keys,\nclose clamp", "#f7f1e6", AMBER),
        ("A  Trim + strip", "guillotine along\ncassette face;\nstrip each key\n(2.4 mm)", LIGHT, BLUE),
        ("B  Place + crimp", "index key k over anvil;\npresser drops the rest;\nlay k into waiting\ncontact; slow punch", "#fbeaea", RED),
        ("C  Insert + test", "housing nest in front;\ncontacts pushed home;\nmate onto test header;\nlabel", LIGHT, BLUE),
    ]
    bx = 40
    for i, (name, body, fill, col) in enumerate(benches):
        s.rect(bx, by, 190, 130, fill=fill, stroke=col, sw=1.8, rx=6)
        s.text(bx + 10, by + 22, name, size=13, weight="bold", fill=col)
        s.text(bx + 10, by + 48, body, size=11)
        if i < 3:
            s.line(bx + 192, by + 65, bx + 232, by + 65, arrow="k", sw=1.6)
        bx += 235
    s.text(40, by + 160, "Build order (each step useful alone):", size=12, weight="bold")
    steps = ("1  cassette + hand tools: pin order and J2's blank enforced by the cassette; SN-2549 by hand",
             "2  bench B: the priority step automated; person trims/strips with a hand jig, inserts by hand",
             "3  bench A: strip joins (or moves onto bench B's slide as a second station)",
             "4  bench C: insertion and a test header; the person's per-conductor work is gone",
             "5  joined: carousel (p1b) or an arm moves cassettes; each bench's nest takes them unchanged")
    for i, t in enumerate(steps):
        s.text(52, by + 182 + i * 18, t, size=11)
    s.save("p1-cassette-and-benches.svg")


def p1_crimp_station():
    s = Svg(1000, 640, "p1 bench B: placing the contact on conductor k and crimping it (schematic, not to scale)",
            "Side section along the wire (left) and end view from the tip (right). The bench frame and anvil "
            "are 'fixed'; the cassette is located to them by its pins.")
    # --- side section
    s.text(40, 80, "Side section", size=13, weight="bold")
    s.rect(40, 230, 150, 45, fill=LIGHT, stroke=BLUE)
    s.text(48, 257, "cassette (clamp, fan, comb)", size=10, fill=BLUE)
    s.rect(30, 290, 400, 14, fill="#ddd", stroke=GREY)
    s.text(40, 322, "lateral slide (lead screw) indexes 2.5 mm per key", size=10)
    for dx in (70, 160):
        s.circle(dx, 285, 5, fill="#fff", stroke=RED, sw=2)
    s.text(40, 340, "cassette pins (red) sit in the slide's bores", size=10, fill=RED)
    # neighbours pushed down
    s.path("M 190 256 C 250 256, 280 330, 400 345", stroke="#777", sw=5)
    s.text(150, 372, "neighbours k-1, k+1 ... pushed ~7 mm\nbelow the anvil top by the slotted\n"
                     "presser; k passes up through its slot", size=10, fill="#555")
    # presser
    s.rect(245, 190, 36, 48, fill="#f4f4f4", stroke=GREY)
    s.line(263, 150, 263, 188, arrow="k")
    s.text(215, 142, "slotted presser", size=10)
    # active conductor + strands
    s.line(190, 250, 470, 250, stroke="#111", sw=7)
    s.line(470, 250, 505, 250, stroke=AMBER, sw=3)
    # fork
    s.line(405, 200, 405, 244, stroke=GREEN, sw=3)
    s.line(418, 200, 418, 244, stroke=GREEN, sw=3)
    s.text(300, 180, "fork closes 3 mm\nbehind the strip line", size=10, fill=GREEN)
    # contact on anvil (outline)
    s.path("M 440 243 L 440 262 L 560 262 L 560 240 L 520 240 L 520 256 L 470 256 L 470 243",
           stroke=RED, sw=2)
    s.rect(432, 256, 8, 6, fill=RED, stroke=RED)
    # anvil
    s.rect(440, 262, 110, 150, fill="#ccc", stroke=INK)
    s.text(452, 430, "anvil blade 1.6 mm thick,\nfixed to the bench frame", size=10)
    # punch
    s.rect(440, 150, 110, 70, fill="#ccc", stroke=INK)
    s.line(495, 100, 495, 146, arrow="r", stroke=RED, sw=2)
    s.text(505, 110, "punch: slow ram,\nhard stop at BDC,\nforce logged", size=10, fill=RED)
    s.text(570, 250, "contact on the anvil,\nbox forward; its tab\nand carrier strip (red)\nrun across the page", size=10, fill=RED)
    # --- end view
    ex, ey = 800, 300
    s.text(700, 80, "End view from the tip", size=13, weight="bold")
    sc = 16
    s.rect(ex - 0.8 * sc, ey + 12, 1.6 * sc, 170, fill="#ccc", stroke=INK)
    s.path(f"M {ex-1.4*sc} {ey-1.9*sc} L {ex-1.0*sc} {ey+12} L {ex+1.0*sc} {ey+12} L {ex+1.4*sc} {ey-1.9*sc}",
           stroke=RED, sw=2.5)
    s.circle(ex, ey - 0.3 * sc, 0.85 * sc, fill="#111")
    s.text(ex + 28, ey, "k in the open barrels", size=10)
    s.rect(ex - 1.7 * sc, ey - 7 * sc, 3.4 * sc, 3.4 * sc, fill="#ccc", stroke=INK)
    s.text(ex + 40, ey - 5.5 * sc, "punch: wider than the\npitch is fine, nothing\nelse is up here", size=10)
    for kk in (-3, -2, -1, 1, 2, 3):
        s.circle(ex + kk * 2.5 * sc, ey + 7.5 * sc, 0.85 * sc, fill="#777")
    s.text(640, ey + 12 * sc + 40, "neighbours at 2.5 mm pitch, ~7 mm lower; the\n"
                                    "1.6 mm anvil blade passes between k-1 and k+1\n"
                                    "(3.3 mm free between them)", size=10)
    s.text(ex - 60, ey + 10 * sc, "anvil", size=10)
    s.text(40, 540, "Precision is needed at three moments: the fork closing (lateral, +/-0.05 mm), the lay-in (conductor to\n"
                    "the floor of the open barrels, against the trim line axially), and bottom dead centre (crimp height,\n"
                    "+/-0.02-0.05 mm). Between them the conductor may flop.", size=11)
    s.save("p1-crimp-station.svg")


def p1b_carousel():
    s = Svg(900, 840, "p1b Carousel joins the benches (schematic, plan view)",
            "The carousel only delivers a cassette to within a lead-in; each station lifts it onto its own pins.")
    cx, cy, R = 450, 390, 185
    s.circle(cx, cy, R + 30, fill="#f7f7f7", stroke=GREY)
    s.circle(cx, cy, 60, fill="#fff", stroke=GREY)
    s.text(cx - 50, cy - 4, "lazy-susan\nbearing, belt\nround the rim", size=10, fill="#555")
    import math
    stations = {0: ("LOAD / UNLOAD\n(person)", AMBER), 2: ("A trim + split\n+ strip", BLUE),
                4: ("B place + crimp", RED), 6: ("look (camera,\ndome light)", GREEN),
                8: ("C insert", BLUE), 10: ("test header\n+ label print", GREEN)}
    for i in range(12):
        a = math.radians(90 + i * 30)
        x = cx + R * math.cos(a)
        y = cy + R * math.sin(a)
        s.rect(x - 22, y - 16, 44, 32, fill=LIGHT, stroke=BLUE, rx=3)
        s.text(x - 6, y + 4, f"{i+1}", size=10, fill=BLUE)
        # tail pointing inward
        xi = cx + (R - 60) * math.cos(a)
        yi = cy + (R - 60) * math.sin(a)
        s.line(x - 0 * math.cos(a), y, xi, yi, stroke="#333", sw=3)
        if i in stations:
            name, col = stations[i]
            xo = cx + (R + 120) * math.cos(a)
            yo = cy + (R + 120) * math.sin(a)
            s.rect(xo - 62, yo - 24, 124, 48, fill="#fff", stroke=col, sw=1.8, rx=5)
            s.text(xo - 55, yo - 5, name, size=10, fill=col, weight="bold")
    s.text(40, 770, "Tails lie inward in each cassette's tray; the ring turns 30 deg per index. A station's own dowels rise\n"
                    "through the nest and lift the cassette 1-2 mm, so the carousel's +/-0.5-1 mm never reaches the work.\n"
                    "Each station is the p1 bench, unchanged, bolted at an angle. A linear conveyor is the same idea opened out.",
           size=11)
    s.save("p1b-carousel.svg")


def p2_turret():
    s = Svg(980, 560, "p2 Still ribbon, tools come to it (schematic, side view)",
            "The ribbon end is clamped once and never re-gripped. One carriage (y) selects conductor or contact; "
            "a drum turret (rotate + x) brings each tool.")
    # y carriage
    s.rect(40, 300, 420, 20, fill="#ddd", stroke=GREY)
    s.text(50, 335, "y carriage (into the page): conductor k, a contact post, or the housing nest to the work line", size=10)
    s.rect(60, 230, 150, 70, fill=LIGHT, stroke=BLUE)
    s.text(70, 262, "work clamp + comb\n(J1: 5P + 4P)", size=11, fill=BLUE)
    s.line(210, 250, 380, 250, stroke="#111", sw=7)
    s.line(380, 250, 410, 250, stroke=AMBER, sw=3)
    s.text(280, 238, "conductor k, lifted by selector", size=10)
    s.rect(290, 262, 12, 38, fill="#999", stroke=INK)
    s.text(240, 290, "selector", size=10)
    # contact post block
    s.rect(230, 360, 120, 34, fill="#fbeaea", stroke=RED)
    s.text(238, 381, "contact posts (on y too)", size=10, fill=RED)
    s.rect(370, 360, 80, 34, fill=LIGHT, stroke=BLUE)
    s.text(376, 381, "housing nest", size=10, fill=BLUE)
    # turret
    tx, ty = 690, 250
    s.circle(tx, ty, 150, fill="#f7f7f7", stroke=GREY)
    import math
    tools = [("strip jaws", BLUE), ("crimp head\n(C-frame, own motor)", RED), ("camera +\ndome light", GREEN),
             ("pusher /\nhousing ram", BLUE), ("trim blade", AMBER), ("web splitter", AMBER)]
    for i, (name, col) in enumerate(tools):
        a = math.radians(180 + i * 60)
        x = tx + 110 * math.cos(a)
        y = ty + 110 * math.sin(a)
        s.rect(x - 38, y - 18, 76, 36, fill="#fff", stroke=col, sw=1.6, rx=4)
        s.text(x - 34, y - 2, name, size=9, fill=col)
    s.line(575, 250, 460, 250, arrow="r", stroke=RED, sw=2)
    s.text(470, 215, "x: the tool at 9 o'clock\napproaches along the wire", size=10, fill=RED)
    s.text(600, 440, "The crimp head carries its force inside its own frame:\nthe turret and clamp only position it.", size=10)
    s.text(40, 470, "Per conductor: y to k -> selector lifts k -> trim -> strip -> y to a contact post, crimp head takes one\n"
                    "(closes one click, like a person) -> y back to k -> head slides onto k (conductor enters the open\n"
                    "barrels axially, to the wire stop) -> crimp -> camera -> selector down. After the last conductor the\n"
                    "housing nest comes to the line and slides onto every contact at once, or each is bowed and pushed.", size=11)
    s.save("p2-turret.svg")


def p3_spool():
    s = Svg(1000, 700, "p3 Terminate at the spool, cut last (schematic, side view)",
            "The spool is the carrier and the rest of the spool is the test lead. Nothing is cut until the XH end has passed.")
    # spool
    s.circle(110, 250, 80, fill="#f4f4f4", stroke=GREY)
    s.circle(110, 250, 25, fill="#fff", stroke=GREY)
    s.text(60, 355, "spool (3P, 4P or 5P)\ninner end -> slip ring ->\ncontinuity tester", size=10)
    s.rect(100, 240, 20, 20, fill=GREEN, stroke=GREEN)
    s.path("M 190 250 C 260 250, 260 200, 330 200", stroke="#333", sw=5)
    # belt feed
    s.rect(330, 170, 80, 18, fill="#bbb", stroke=INK, rx=8)
    s.rect(330, 212, 80, 18, fill="#bbb", stroke=INK, rx=8)
    s.text(330, 160, "belt feed + encoder wheel", size=10)
    s.line(330, 200, 560, 200, stroke="#333", sw=5)
    # work clamp
    s.rect(440, 180, 60, 40, fill=LIGHT, stroke=BLUE, sw=1.5)
    s.text(430, 172, "work clamp", size=10, fill=BLUE)
    # stations over the tip
    s.rect(520, 90, 170, 60, fill="#fff", stroke=RED, sw=1.5, rx=5)
    s.text(528, 110, "trim, split, strip,\nplace + crimp, look", size=11, fill=RED)
    s.line(600, 150, 600, 190, arrow="r", stroke=RED)
    # guillotine
    s.rect(505, 225, 10, 40, fill=AMBER, stroke=AMBER)
    s.text(470, 285, "guillotine at the\nclamp face (cuts last)", size=10, fill=AMBER)
    # drop tube
    s.path("M 560 200 C 640 200, 700 230, 720 300 L 720 400", stroke="#333", sw=5, dash="8,4")
    s.rect(700, 300, 40, 110, fill="none", stroke=GREY, dash="4,3")
    s.text(750, 330, "drop tube: the finished\nend leads, the loom\nfollows by gravity\n(machine at a bench edge)", size=10)
    s.rect(705, 400, 30, 18, fill=LIGHT, stroke=BLUE)
    s.text(745, 415, "XH end (housed if single-ribbon)", size=10, fill=BLUE)
    # order strip
    oy = 470
    s.text(40, oy, "Order at the machine, per ribbon end:", size=12, weight="bold")
    steps = ["feed to stop", "trim square", "split web", "strip", "place + crimp", "look / pull",
             "insert (singles)", "test through spool", "feed out L", "cut"]
    x = 40
    for i, st in enumerate(steps):
        col = RED if st in ("place + crimp",) else (GREEN if "test" in st else (AMBER if st in ("cut", "feed out L") else BLUE))
        w = 7 * len(st) + 14
        s.rect(x, oy + 12, w, 26, fill="#fff", stroke=col, sw=1.5, rx=4)
        s.text(x + 7, oy + 30, st, size=11, fill=col)
        if i < len(steps) - 1:
            s.line(x + w, oy + 25, x + w + 10, oy + 25, arrow="k")
        x += w + 12
        if x > 760 and i < len(steps) - 1:
            x = 40
            oy += 40
    s.text(40, oy + 70, "A bad crimp found at 'look' or 'test': cut ~6 mm back and go round again. It costs spool, never a loom,\n"
                        "so no loom carries a redo reserve and a pair's two ribbons stay equal. The far end (Fastons, ferrules, IDC,\n"
                        "short legs peeled back) is done by hand after the cut, so risky automated work comes before hand work.",
           size=11)
    s.save("p3-spool-cut-last.svg")


def p3b_ams():
    s = Svg(900, 520, "p3b Ribbon AMS: five spools, two lanes (schematic, plan view)",
            "Like a filament AMS: each spool has its own feed; only one ribbon occupies a lane's shared path at a time.")
    left = [("5P", 110), ("4P-L", 190), ("3P-a", 270)]
    right = [("4P-R", 370), ("3P-b", 450)]
    for name, y in left + right:
        s.circle(80, y, 30, fill="#f4f4f4", stroke=GREY)
        s.text(62, y + 4, name, size=11, weight="bold")
        s.rect(130, y - 8, 50, 16, fill="#bbb", stroke=INK, rx=6)
        s.text(135, y - 12, "feed", size=9)
    # merges
    for (lane, spools, ym, col) in (("left lane", left, 190, BLUE), ("right lane", right, 410, RED)):
        for name, y in spools:
            s.path(f"M 180 {y} C 260 {y}, 280 {ym}, 360 {ym}", stroke="#333", sw=3)
        s.rect(360, ym - 14, 60, 28, fill="#fff", stroke=col, sw=1.6, rx=5)
        s.text(365, ym + 4, "merge", size=10, fill=col)
        s.text(365, ym - 20, lane, size=10, fill=col, weight="bold")
    s.path("M 420 190 C 500 190, 520 290, 580 290", stroke=BLUE, sw=4)
    s.path("M 420 410 C 500 410, 520 306, 580 306", stroke=RED, sw=4)
    s.rect(580, 270, 110, 56, fill=LIGHT, stroke=INK, sw=1.5, rx=4)
    s.text(588, 293, "work point:\ntwo lanes edge to edge", size=10)
    s.text(610, 360, "left:  J1 5P, J2 3P-a, J4 4P, J7 5P, all singles\nright: J1 4P, J2 3P-b, J4 3P, J7 3P",
           size=10)
    s.text(40, 490, "Two lanes because every pair has a 'cavity-1 ribbon' and a second ribbon. The 4P appears on both sides "
                    "(J4 left, J1 right),\nso it is bought twice, as is the 3P. J4 and J7's crossings still need a hand, "
                    "or a changed ribbon assignment.", size=11)
    s.save("p3b-ribbon-ams.svg")


def p4_present():
    s = Svg(980, 560, "p4 The person presents, the machine takes (schematic, side view)",
            "A shoebox station: the tip is the reference; the machine grips the conductor itself, strips, places and crimps.")
    s.rect(300, 120, 520, 220, fill="#fafafa", stroke=GREY, rx=8)
    # funnel
    s.path("M 300 170 L 360 205 L 360 215 L 300 250 Z", fill=LIGHT, stroke=BLUE)
    s.text(250, 160, "funnel", size=10, fill=BLUE)
    # conductor from hand
    s.path("M 60 260 C 150 260, 200 210, 300 210", stroke="#111", sw=6)
    s.line(300, 210, 560, 210, stroke="#111", sw=6)
    s.text(60, 285, "person holds the loom,\nconductor k splayed by hand", size=10)
    # clamp
    s.rect(390, 190, 50, 40, fill=LIGHT, stroke=BLUE, sw=1.5)
    s.text(380, 182, "soft clamp\n(closes on trigger)", size=10, fill=BLUE)
    s.line(415, 250, 470, 250, arrow="b", stroke=BLUE)
    s.text(420, 268, "clamp slides: pull slug,\nthen feed into contact", size=9, fill=BLUE)
    # strip jaws
    s.rect(520, 180, 16, 26, fill=AMBER, stroke=AMBER)
    s.rect(520, 214, 16, 26, fill=AMBER, stroke=AMBER)
    s.text(505, 172, "V strip jaws", size=10, fill=AMBER)
    # tip stop / sensor
    s.rect(585, 196, 6, 28, fill=GREEN, stroke=GREEN)
    s.text(560, 250, "tip stop +\nbreak beam", size=10, fill=GREEN)
    # crimp head below/right
    s.rect(640, 240, 120, 30, fill="#ccc", stroke=INK)
    s.rect(640, 150, 120, 40, fill="#ccc", stroke=INK)
    s.text(650, 145, "punch (slow ram)", size=10)
    s.text(650, 290, "anvil + pre-fed contact", size=10, fill=RED)
    s.path("M 650 240 L 650 228 L 750 228 L 750 240", stroke=RED, sw=2)
    s.line(590, 330, 640, 245, arrow="k", dash="4,3")
    s.text(470, 360, "stop and jaws swing clear; the anvil shuttle brings the waiting contact under the tip", size=10)
    # timeline
    oy = 410
    s.text(40, oy, "The person and the machine, one conductor apart:", size=12, weight="bold")
    s.rect(40, oy + 15, 60, 22, fill="#f7f1e6", stroke=AMBER)
    s.text(46, oy + 30, "present k", size=10)
    s.rect(100, oy + 15, 90, 22, fill="#f7f1e6", stroke=AMBER)
    s.text(106, oy + 30, "insert k-1", size=10)
    s.rect(190, oy + 15, 160, 22, fill="#fff", stroke=GREY, dash="4,3")
    s.text(196, oy + 30, "waits (or far-end work)", size=10, fill="#777")
    s.rect(100, oy + 45, 250, 22, fill="#fbeaea", stroke=RED)
    s.text(106, oy + 60, "machine: grip, strip, place, crimp, look (~40 s)", size=10, fill=RED)
    s.text(380, oy + 30, "The person's hands never hold the contact. The machine's cycle, not the person, sets the\n"
                         "pace; minutes fall only when the machine can be fed an end's worth at once (p1).", size=11)
    s.save("p4-present-and-take.svg")


def p5_layout():
    s = Svg(980, 520, "p5 Camshaft: one motor, one revolution per conductor (schematic)",
            "The timing diagram is the procedure (see p5-cam-timing.svg). Printed face cams run the light motions; "
            "a steel eccentric runs the punch.")
    # shaft
    s.line(80, 360, 900, 360, stroke=INK, sw=6)
    s.rect(40, 330, 60, 60, fill="#ccc", stroke=INK)
    s.text(30, 410, "NEMA 17 +\n30:1 worm", size=10)
    cams = [("selector", 170, BLUE), ("fork", 250, GREEN), ("strip jaws", 330, AMBER), ("strip pull", 410, AMBER),
            ("lay-in finger", 490, BLUE), ("PUNCH\n(steel eccentric)", 600, RED), ("feed pawl", 710, RED),
            ("switch cams:\nindex, camera", 820, GREEN)]
    for name, x, col in cams:
        if "PUNCH" in name:
            s.circle(x, 360, 34, fill="#eee", stroke=RED, sw=2.5)
            s.line(x, 326, x, 180, stroke=RED, sw=4)
            s.rect(x - 30, 150, 60, 30, fill="#ccc", stroke=INK)
            s.rect(x - 60, 110, 120, 12, fill="#888", stroke=INK)
            s.rect(x - 60, 110, 12, 290, fill="#888", stroke=INK)
            s.text(x - 110, 100, "steel C-frame (force loop)", size=10)
            s.text(x + 40, 250, "rod", size=10)
        else:
            s.path(f"M {x-20} 360 a 20 26 0 1 0 40 0 a 20 22 0 1 0 -40 0", stroke=col, fill="#fff", sw=2)
            s.line(x, 334, x, 230, stroke=col, sw=2)
            s.circle(x, 334, 4, fill=col, stroke=col)
        s.text(x - 30, 460, name, size=10, fill=col)
    s.rect(140, 170, 380, 50, fill="#fff", stroke=GREY, dash="4,3")
    s.text(150, 190, "followers drive levers to the work point above the shaft\n(printed PETG / PET-CF cams, forces under ~50 N)", size=10)
    s.text(40, 500, "Skip (J2 cavity 3): a 12 V solenoid lifts the feed pawl and pulls the punch link pin for one turn. "
                    "Everything else is fixed by the shape of the cams.", size=11)
    s.save("p5-camshaft-layout.svg")


def orders_of_work():
    s = Svg(1000, 540, "Orders of work on J2 (3P + 3P into XHP-6, cavity 3 empty) (schematic)",
            "S strip, C place + crimp, L look, I insert, - trimmed (cavity 3). The order decides what the machine "
            "must hold, and when the person is needed.")
    cols = {"S": BLUE, "C": RED, "L": GREEN, "I": AMBER, "-": "#bbb"}

    def boxes(x, y, ops):
        for c in ops:
            s.rect(x, y + 2, 16, 20, fill="#fff", stroke=cols.get(c, INK), sw=1.5)
            s.text(x + 4, y + 16, c, size=10, fill=cols.get(c, INK))
            x += 18
        return x

    def label(x, y, t, col="#555"):
        s.text(x, y + 16, t, size=10, fill=col)
        return x + 7 * len(t) + 6

    y = 80
    s.text(20, y + 16, "per conductor, insert as you go", size=12, weight="bold")
    x = 280
    for lab, ops in (("a1", "SCLI"), ("a2", "SCLI"), ("a3", "-"), ("b1", "SCLI"), ("b2", "SCLI"), ("b3", "SCLI")):
        x = label(x, y, lab)
        x = boxes(x, y, ops) + 8
    s.text(280, y + 42, "housing present from the start; each conductor bowed ~8-10 mm to go home (calc/selector_and_bow)",
           size=10, fill="#555", italic=True)

    y += 90
    s.text(20, y + 16, "per ribbon end, then per housing", size=12, weight="bold")
    x = 280
    x = label(x, y, "a")
    x = boxes(x, y, "SS-") + 6
    x = boxes(x, y, "CC") + 6
    x = boxes(x, y, "LL") + 14
    x = label(x, y, "b")
    x = boxes(x, y, "SSS") + 6
    x = boxes(x, y, "CCC") + 6
    x = boxes(x, y, "LLL") + 14
    s.line(x, y, x, y + 24, stroke=GREY)
    x = label(x + 8, y, "housing:")
    boxes(x, y, "IIIII")
    s.text(280, y + 42, "gang insertion possible (housing slides onto all five); the pair meets only at the housing",
           size=10, fill="#555", italic=True)

    y += 90
    s.text(20, y + 16, "per unit (all 14 ends, 53 crimps)", size=12, weight="bold")
    x = 280
    for op in "SCLI":
        x = boxes(x, y, op * 4)
        x = label(x, y, "... x53") + 10
    s.text(280, y + 42, "each station runs one long job; crimped ends wait in their cassettes; the person comes back once",
           size=10, fill="#555", italic=True)

    y += 90
    s.text(20, y + 16, "per spool, cut last (p3)", size=12, weight="bold")
    x = 230
    for t, col in (("4P spool: 7 ends x 5 units", BLUE), ("5P spool: 3 ends x 11", BLUE),
                   ("3P spool: J2a, J2b, J4, J7 x 8", BLUE), ("pairs housed: J1 J2 J4 J7", AMBER)):
        w = 6 * len(t) + 14
        s.rect(x, y + 2, w, 22, fill="#fff", stroke=col, sw=1.5, rx=4)
        s.text(x + 7, y + 17, t, size=10, fill=col)
        x += w + 10
    s.text(280, y + 44, "one ribbon type for hours; J2's two 3P ends are made one after another from one spool and "
                        "meet in the housing later", size=10, fill="#555", italic=True)
    s.text(20, 490, "The empty cavity is decided where the conductor is trimmed: in the cassette (a blank key), in the machine's "
                    "program (skip), or by\nthe person at the spool. In every order it is decided before insertion and "
                    "checked at the test header after.", size=11)
    s.save("orders-of-work.svg")


if __name__ == "__main__":
    p1_cassette_and_benches()
    p1b_carousel()
    p3b_ams()
    p4_present()
    orders_of_work()
