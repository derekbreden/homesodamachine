"""Generate change-the-question's settled sketches.

Run:  python3 make_w3_sketches.py
Writes c6-shapes.svg, c6b-bench.svg, c1c-crimp-in-the-row.svg, c7-straight-across.svg
next to this script. All schematic; end views in c6-shapes are drawn at 40 px per mm
from the dimensions cited in the idea files.
"""

import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
COPPER = "#b87333"
INK = "#111"
GREY = "#555"
BLUE = "#1f5fa8"
RED = "#a33"
GREEN = "#2a7a2a"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, fill=INK, size=12, bold=False, anchor="start"):
        fw = ' font-weight="bold"' if bold else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{fw} fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')

    def lines(self, x, y, rows, fill=INK, size=12, dy=15, anchor="start"):
        for i, r in enumerate(rows):
            n = len(r) - len(r.lstrip("\u00a0"))   # leading no-break spaces indent the row
            self.text(x + 3.5 * n, y + i * dy, r.lstrip("\u00a0"), fill=fill, size=size, anchor=anchor)

    def line(self, x1, y1, x2, y2, stroke="#333", w=1.5, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arr)"' if arrow else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}{m}/>')

    def rect(self, x, y, w, h, fill="none", stroke="#333", sw=1.5, dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill="none", stroke="none", sw=1.5):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def ellipse(self, cx, cy, rx, ry, fill="none", stroke="none", sw=1.5):
        self.add(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def poly(self, pts, stroke=COPPER, w=8, fill="none", dash=None, close=False):
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + (" Z" if close else "")
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{ds}/>')

    def panel(self, x, y, w, h, title):
        self.rect(x, y, w, h, stroke="#bbb", sw=1)
        self.text(x + 10, y + 19, title, bold=True)

    def save(self, name, title, subtitle):
        head = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'font-family="Helvetica, Arial, sans-serif" font-size="12">',
                '<defs><marker id="arr" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">'
                '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>',
                f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#ffffff"/>',
                f'<text x="20" y="24" font-size="16" font-weight="bold" fill="{INK}">{esc(title)}</text>',
                f'<text x="20" y="42" fill="{GREY}">{esc(subtitle)}</text>']
        with open(os.path.join(HERE, name), "w") as f:
            f.write("\n".join(head + self.parts + ["</svg>"]) + "\n")


# ---------------------------------------------------------------------------
# c6-shapes: three pre-forms and what a B-die does to each
def arc_pts(cx, cy, r, a0, a1, n=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def c6_shapes():
    S = Svg(1000, 800)
    K = 40.0  # px per mm

    def P(cx, base, x, y):
        return (cx + K * x, base - K * y)

    def mm_poly(cx, base, pts, **kw):
        S.poly([P(cx, base, x, y) for x, y in pts], **kw)

    def jacket(cx, base, x, y, rx, ry):
        X, Y = P(cx, base, x, y)
        S.ellipse(X, Y, K * rx, K * ry, fill="#333")
        S.circle(X, Y, K * 0.37, fill="#b8b8b8")

    def b_die(cx, base):
        # a B: two arches of radius 0.5 centred at x = +/-0.45, y = 1.35, meeting in a cusp at x = 0
        a = math.degrees(math.acos(0.45 / 0.5))
        pts = [(-0.95, 0.35), (-0.95, 1.35)]
        pts += arc_pts(-0.45, 1.35, 0.5, 180, a, 20)
        pts += arc_pts(0.45, 1.35, 0.5, 180 - a, 0, 20)
        pts += [(0.95, 1.35), (0.95, 0.35)]
        mm_poly(cx, base, pts, stroke=BLUE, w=1.5, dash="5,3")

    def b_crimp(cx, base):
        pts = [(-0.05, 1.1)] + arc_pts(-0.45, 1.3, 0.37, 30, 180, 12)
        pts += [(-0.82, 0.3), (-0.6, 0.1), (0.6, 0.1), (0.82, 0.3)]
        pts += arc_pts(0.45, 1.3, 0.37, 0, 150, 12) + [(0.05, 1.1)]
        mm_poly(cx, base, pts)
        jacket(cx, base, 0, 0.8, 0.62, 0.55)

    def closed_line(cx, base):
        y = base - K * 1.8
        S.line(cx - 70, y, cx + 70, y, stroke=GREY, w=1, dash="2,3")
        S.text(cx + 72, y + 4, "1.8", fill=GREY, size=11)

    cols = [(170, "Open, as bought (clone drawings)"),
            (500, "Keyhole (round mandrel), c6"),
            (830, "Tall shapes: tall keyhole (blade mandrel), or the crimper's own stroke stopped early")]
    Y1, Y2 = 300, 560
    S.panel(15, 55, 970, 300, "1. Pre-formed, with the jacket snapped in (end view at the insulation barrel)")
    S.panel(15, 365, 970, 300, "2. After the final stroke of a B-profile die closing to ~1.8 mm (blue dashed; assumed, the SN-2549's is unmeasured)")

    # column 1, open
    cx = 170
    mm_poly(cx, Y1, [(-1.3, 2.9), (-1.3, 0.35), (-1.1, 0.1), (1.1, 0.1), (1.3, 0.35), (1.3, 2.9)])
    jacket(cx, Y1, 0, 1.05, 0.85, 0.85)
    closed_line(cx, Y1)
    S.text(cx, 104, cols[0][1], anchor="middle", bold=True, size=12)
    S.lines(cx, Y1 + 20, ["2.46-3.25 wide, 2.75-3.2 tall",
                          "the jacket drops in and lifts out:",
                          "no hold before the crimp"], anchor="middle", size=11)
    b_die(cx, Y2)
    b_crimp(cx, Y2)
    S.lines(cx, Y2 + 20, ["a B: the arches carry the tips over",
                          "and drive them down into the jacket"], anchor="middle", size=11)

    # column 2, keyhole
    cx = 500
    ring = arc_pts(0, 1.0, 0.9, 29, -209, 60)
    mm_poly(cx, Y1, ring)
    jacket(cx, Y1, 0, 1.05, 0.8, 0.83)
    closed_line(cx, Y1)
    S.text(cx, 104, cols[1][1], anchor="middle", bold=True, size=12)
    S.lines(cx, Y1 + 20, ["1.96-2.14 wide; throat 1.3-1.5; metal ends at",
                          "1.28-1.66, under 1.8; the jacket stands ~1.9 [htq s1]",
                          "retention 0.15-30 N; axial grip 0.1-3.5 N [w3b s3-4]"], anchor="middle", size=11)
    b_die(cx, Y2)
    # squeezed ring: sides pinched to die width, tips moved in and slightly down
    sq = [(0.42, 1.36), (0.62, 1.42)] + [(0.78 * math.cos(math.radians(a)), 0.95 + 0.86 * math.sin(math.radians(a)))
                                          for a in range(20, -201, -8)] + [(-0.62, 1.42), (-0.42, 1.36)]
    mm_poly(cx, Y2, sq)
    jacket(cx, Y2, 0, 0.86, 0.6, 0.7)
    S.lines(cx, Y2 + 20, ["the walls pinch the ring: throat to ~0.75-1.4 with a",
                          "1.8-1.9 die, untouched at 2.0 [w3b s1]; the arches",
                          "never reach the tips: an O with a gap, not a B"], anchor="middle", size=11, fill=RED)

    # column 3, tall shapes
    cx = 830
    S.rect(cx - K * 0.77, Y1 - K * 2.7, K * 1.54, K * 2.5, stroke=GREY, sw=1, dash="3,2")
    tall = [(-0.45, 2.72)] + arc_pts(-0.62, 2.45, 0.25, 70, 180, 10) + [(-0.87, 2.3), (-0.87, 0.35), (-0.65, 0.1),
                                                                       (0.65, 0.1), (0.87, 0.35), (0.87, 2.3)] \
        + arc_pts(0.62, 2.45, 0.25, 0, 110, 10) + [(0.45, 2.72)]
    mm_poly(cx, Y1, tall)
    jacket(cx, Y1, 0, 1.03, 0.72, 0.85)
    closed_line(cx, Y1)
    S.lines(cx, 104, ["Tall shapes: blade mandrel (dashed),", "or the crimper's own stroke stopped early"],
            anchor="middle", size=12)
    S.lines(cx, Y1 + 20, ["1.82-2.05 wide, 2.3-3.0 tall; tips above 1.8",
                          "axial grip 0.02-3.5 N; retention by friction (tips",
                          "vertical) up to 0.3-27 N once curled [w3b s2]"], anchor="middle", size=11)
    b_die(cx, Y2)
    b_crimp(cx, Y2)
    S.lines(cx, Y2 + 20, ["the arches meet the tips above 1.8 and",
                          "finish the B the die was made for"], anchor="middle", size=11, fill=GREEN)

    S.lines(30, 695, [
        "Where each is made: the keyhole and the tall keyhole in c6's steel pre-former (mandrel chosen 0.08-0.12 mm under the measured jacket OD);",
        "the crimper-made U by the SN-2549 closed to click k (hand-tool-as-press a6b, a1b), if its insulation wings meet the die first (0.65-1.7 mm",
        "of die travel on the edge model, possibly none on the apex model [htq s3]).",
        "Stick channel: 2.1 x 2.6 mm for keyholes, ~2.1-2.2 x 3.1-3.2 mm for the tall shapes. None nests: a 1.85-1.95 mm box enters no throat or U.",
    ], size=12)
    S.save("c6-shapes.svg", "c6 Three pre-forms, and what the final crimp does to each",
           "schematic; end views at the insulation barrel drawn at 40 px per mm from clone drawings and the calc; heights in mm above the contact's underside")


# ---------------------------------------------------------------------------
def c6b_bench():
    S = Svg(1000, 600)
    S.panel(15, 55, 970, 190, "1. The bench, left to right on one printed baseplate (top view)")
    boxes = [
        (30, "1 Pre-former", ["toggle clamp (Prime, $18.25)", "steel nest or cut XHP stub", "mandrel from the measured jacket", "round pin or flat blade", "-> loom-order stick"]),
        (270, "2 Snap block", ["steel-floored pocket", "box stop + tip stop", "backlit window", "thumb tool: rear tine on", "jacket, front tine on strands"]),
        (510, "3 SN-2549 in a cradle", ["lower handle clamped", "flag seat on the lower", "jaw's M4 screw", "leaf stop + coin-cell lamp", "one hand squeezes"]),
        (750, "4 i5 sensing nest", ["housing on a real header", "posts are inputs", "lit cavity, lever seats", "the post that closes", "names the cavity"]),
    ]
    for x, t, rows in boxes:
        S.rect(x, 80, 210, 150, fill="#f7f4ea", stroke="#8a6d1f")
        S.text(x + 10, 100, t, bold=True)
        S.lines(x + 10, 120, rows, size=11)
    for x in (240, 480, 720):
        S.line(x, 155, x + 28, 155, w=2, arrow=True)

    S.panel(15, 255, 970, 330, "2. The flag seat in the open SN-2549 (side section along the nest axis)")
    ax, ay = 330, 470   # anvil top-left
    S.rect(ax, ay, 170, 40, fill="#9a9a9a")
    S.text(ax + 60, ay + 26, "anvil (lower jaw)", fill="#fff", size=11)
    S.rect(ax, 300, 170, 45, fill="#c8c8c8")
    S.text(ax + 12, 328, "punch (upper jaw), open", size=11)
    S.line(ax + 85, 350, ax + 85, 372, w=2, arrow=True)
    # flag at height h
    fy = 430
    S.rect(ax + 170, fy - 26, 60, 26, stroke=COPPER, sw=3)          # box
    S.text(ax + 186, fy - 32, "box", fill="#8a4b10", size=11)
    S.poly([(ax + 175, fy), (ax + 190, fy + 16)], stroke=COPPER, w=3)   # lance
    S.text(ax + 190, fy + 30, "lance", fill="#8a4b10", size=11)
    S.poly([(ax + 20, fy), (ax + 170, fy)], stroke=COPPER, w=3)       # floor
    S.poly([(ax + 95, fy), (ax + 95, fy - 18)], stroke=COPPER, w=3)
    S.poly([(ax + 150, fy), (ax + 150, fy - 18)], stroke=COPPER, w=3)
    S.poly([(ax + 20, fy), (ax + 20, fy - 30)], stroke=COPPER, w=3)
    S.poly([(ax + 70, fy), (ax + 70, fy - 30)], stroke=COPPER, w=3)
    S.rect(ax - 170, fy - 30, 230, 22, fill="#333")                    # jacket
    S.line(ax + 60, fy - 14, ax + 170, fy - 14, stroke="#999", w=4)   # strands
    S.text(ax - 160, fy - 38, "jacket, snapped into the pre-formed barrel", size=11)
    # h dimension
    S.line(ax + 130, fy + 2, ax + 130, ay - 2, stroke=BLUE, w=1)
    S.text(ax + 100, ay - 8, "h", fill=BLUE, size=12, bold=True)
    # rear guide
    S.rect(ax - 60, fy - 8, 40, 12, fill="#e8d9a8", stroke="#8a6d1f")
    S.poly([(ax - 40, fy + 4), (ax - 44, fy + 14), (ax - 36, fy + 22), (ax - 44, fy + 30), (ax - 40, ay + 20)], stroke=GREY, w=1.5)
    S.lines(40, 470, ["rear U guide on the jacket,", "at h on a 1-3 N spring"], size=11)
    # front ledge + floor strip + leaf
    S.rect(ax + 172, fy + 2, 58, 10, fill="#e8d9a8", stroke="#8a6d1f")
    S.line(ax + 172, fy + 1, ax + 230, fy + 1, stroke="#555", w=2)
    S.poly([(ax + 200, fy + 12), (ax + 196, fy + 22), (ax + 204, fy + 30), (ax + 196, fy + 38), (ax + 200, ay + 20)], stroke=GREY, w=1.5)
    S.rect(ax + 232, fy - 40, 6, 52, fill="#6b8fb3")
    S.lines(ax + 250, 300, ["front: open-topped slot keyed to box and lance,",
                            "floor strip (electrode), at h on a 1-3 N spring;",
                            "a cut kit XHP-2 on a flexure can be the slot"], size=11)
    S.lines(ax + 250, 352, ["leaf stop, insulated, preloaded 10-30 N:",
                            "the person's push (at most the flag's grip,",
                            "0.1-3.5 N) cannot move it; the barrel's growth",
                            "under coining (80-520 N) can [w3 s3]"], size=11)
    # lamp
    S.circle(ax + 420, 440, 9, fill="#ffd84a", stroke="#a88a10")
    S.rect(ax + 440, 432, 24, 16, fill="#ccc", stroke="#666")
    S.line(ax + 238, fy - 30, ax + 411, 440, stroke="#6b8fb3", w=1)
    S.line(ax + 230, fy + 1, ax + 440, 448, stroke="#6b8fb3", w=1)
    S.lines(ax + 400, 470, ["LED + coin cell: the box bridges", "strip and leaf -> lit: stop pushing"], size=11)
    S.lines(40, 540, [
        "h = 1.1-1.7 mm clears the lance on entry (lance + 0.2 = 0.8-1.1 mm) and gives the 1.0-1.7 mm lift a crimped lance needs to be drawn back.",
        "Opening needed at the nest: 3.5-4.3 mm (keyhole), 3.6-4.9 mm (tall shapes) [htq s4]; unmeasured on the SN-2549. Dragged on the anvil, the",
        "lance folds at 1-5 N, above the flag's grip, and the contact slides back along its jacket unseen. The seat is hand-tool-as-press's (a6b).",
    ], size=11)
    S.save("c6b-bench.svg", "c6b By hand this week: pre-form, snap, and a flag seat with a lamp on the SN-2549",
           "schematic, not to scale; numbers from c6b and the cited calc")


# ---------------------------------------------------------------------------
def c1c():
    S = Svg(1000, 820)
    # Panel 1: top view
    S.panel(15, 55, 480, 360, "1. Top view (front = housing side, up)")
    # rail
    S.rect(40, 370, 420, 10, fill="#bbb", stroke="#666")
    S.text(50, 398, "MGN12 rail behind the clamp; the slide body reaches forward", size=11)
    # slide body (clamp + pallets + nest)
    S.rect(80, 300, 230, 30, fill="#9ab", stroke="#345")
    S.text(95, 320, "web clamp (ribbon's reference)", fill="#123", size=11)
    for i in range(4):
        S.line(130 + 34 * i, 300, 130 + 34 * i, 215, stroke=INK, w=5)
    S.rect(110, 190, 145, 45, fill="#e8d9a8", stroke="#8a6d1f")
    for i in range(4):
        S.rect(123 + 34 * i, 195, 14, 35, stroke=COPPER, sw=2)
    S.lines(28, 205, ["pallet A", "(B parked", "below)"], fill="#6b5310", size=11, dy=13)
    S.rect(130, 140, 95, 18, fill="#fff")
    S.text(40, 153, "housing nest", size=11)
    # C at press X around carrier 2 (x=164)
    S.rect(144, 95, 40, 22, fill="none", stroke="#333", sw=2.5, dash="5,3")
    S.line(150, 117, 150, 205, stroke="#333", w=1.5, dash="5,3")
    S.line(178, 117, 178, 205, stroke="#333", w=1.5, dash="5,3")
    S.lines(235, 90, ["dashed: the fixed steel C at the press's X.",
                      "Spine in front of the housing nest's path;",
                      "arms reach back 20-26 mm over and under",
                      "the working carrier. The slide carries the",
                      "work through its throat; tail and parked",
                      "pallets stay behind, outside it."], size=11)
    # second station
    S.rect(380, 185, 100, 95, fill="none", stroke=GREEN, sw=1.5, dash="4,3")
    S.lines(385, 203, ["second station", "at another X:", "cam plate +", "pushers (A), or", "sort comb (B)"], fill=GREEN, size=11)
    S.line(262, 232, 372, 232, w=2, arrow=True)
    S.text(40, 352, "the slide steps 3.4 mm per carrier and never carries crimp force", size=11)

    # Panel 2: side section at the press
    S.panel(505, 55, 480, 360, "2. Side section at the press (front left)")
    # C: spine left, arms right
    S.rect(530, 110, 30, 250, fill="#aaa", stroke="#333")
    S.rect(530, 110, 230, 34, fill="#aaa", stroke="#333")   # upper arm
    S.rect(530, 326, 230, 34, fill="#aaa", stroke="#333")   # lower arm
    S.add('<text x="549" y="235" font-size="11" fill="#111" transform="rotate(-90 549 235)" text-anchor="middle">spine</text>')
    S.rect(700, 144, 30, 58, fill="#c8c8c8", stroke="#333")  # punch
    S.text(736, 170, "punch", size=11)
    S.rect(703, 262, 24, 64, fill="#777", stroke="#333")      # anvil
    S.text(733, 300, "anvil <= 1.90 wide,", size=11)
    S.text(733, 314, "front edge behind the lance", size=11)
    S.rect(680, 300, 18, 26, fill="#444")                      # hard stop
    S.text(600, 318, "hard stop", size=11)
    # housing nest between arms
    S.rect(575, 236, 60, 26, fill="#fff", stroke="#333")
    S.text(580, 230, "housing nest", size=11)
    # carrier + contact at anvil
    S.rect(655, 262, 90, 10, fill="#e8d9a8", stroke="#8a6d1f")
    S.rect(660, 244, 30, 18, stroke=COPPER, sw=3)
    S.poly([(695, 262), (740, 262)], stroke=COPPER, w=3)
    # retracting stop
    S.rect(645, 238, 8, 26, fill="#6b8fb3")
    S.lines(575, 91, ["retracting front stop (blue): seated before a crimp, backs off",
                      "0.3 mm at capture, out of the way while the slide steps"], size=11, dy=13)
    # ribbon going back
    S.line(740, 256, 960, 256, stroke=INK, w=5)
    S.text(800, 248, "to the web clamp, outside the C", size=11)
    S.lines(530, 386, ["12 mm arm, 15-25 mm wide: 11-41 um at 3 kN; the stop beside the anvil",
                       "makes that travel, not crimp height [htq s7]"], size=11)

    # Panel 3: end view at the press
    S.panel(15, 425, 480, 380, "3. End view at the press: crimp in the row, no lift")
    base = 690
    K = 30
    for i, cx in enumerate((145, 247, 349)):
        pts = arc_pts(0, 1.0, 0.9, 29, -209, 40)
        S.poly([(cx + K * x, base - K * y) for x, y in pts], w=6)
        S.ellipse(cx, base - K * 1.05, K * 0.8, K * 0.83, fill="#333")
    S.poly([(247 - 66, 470), (247 + 66, 470), (247 + 66, 575), (247 + 30, 600), (247 - 30, 600), (247 - 66, 575)],
           stroke="#333", w=1.5, fill="#c8c8c8", close=True)
    S.lines(322, 470, ["one-nest punch,", "half-width 1.75-2.0;", "or an SN nest cut", "to a tongue <= 4.45,",
                       "narrow to 2.1-2.3", "above the anvil", "(2.6-3.3 beside tall", "pre-forms) [htq s5]"], size=10, dy=14)
    S.rect(247 - 28, base + 4, 56, 40, fill="#888", stroke="#333")
    S.text(247 + 36, base + 30, "anvil blade <= 1.90 mm", size=11)
    S.line(145, 745, 247, 745)
    S.text(180, 760, "3.4 mm", size=11)
    S.line(247, 745, 349, 745)
    S.text(282, 760, "3.4 mm", size=11)
    S.lines(30, 778, ["beside keyhole neighbours: 0.23-0.42 mm spare (insulation), 0.33-0.65 (conductor)",
                      "[w2 s2]; the pallet floats in X on a flexure and the punch's flare centres each contact"], size=11)

    # Panel 4: sequence
    S.panel(505, 425, 480, 380, "4. One ribbon end")
    S.lines(515, 468, [
        "1 clamp; strip flat; interlaced jaws split odd (A) from even (B);",
        "    park B down and back",
        "2 pallet A up; presser comb snaps every jacket and lays every",
        "    strand bundle (or lays open contacts; tack comb, two passes);",
        "    one tine can be held back to lay a crossing in a second stroke",
        "3 camera checks every U; per carrier: the anvil electrode names",
        "    the conductor; stop seats; punch to the hard stop; stop backs off",
        "4 park A; lay and crimp row B the same way",
        "5 proof pull ~20 N per contact, row by row, into the slide",
        "6 at the second station, one of two endings:",
        "    A: cam spread 3.4 -> 5.0; housing moves 7 mm onto row A;",
        "        row B, bowed 4.6-8.6 mm when it parked, pushed 7 mm in",
        "    B: sort both rows into one 2.5 mm comb, push the housing on",
        "        (into-the-housing k8): no cam plate, nothing stored",
        "7 real XH wafer test: order, opens, shorts, J2's empty cavity",
    ], size=11, dy=15)
    S.lines(515, 706, ["split: 6-12 mm (T4), 15-26 mm (J1) for ending A [w2 s6]",
                       "person: sticks or strip, housings, one ribbon end per call;",
                       "J4/J7 crossings at the lay (A), none (B, or c7's pin map)"], size=11, fill=GREY)
    S.save("c1c-crimp-in-the-row.svg",
           "c1c Half-rows crimped where they lie: narrowed neighbours, a fixed press, both rows before either is inserted",
           "schematic, not to scale except the end view (30 px per mm at the insulation barrels); combination of c1, c6 or c1b, and other explorers' presses and rules")


# ---------------------------------------------------------------------------
def c7():
    S = Svg(1000, 745)

    def mapping(x0, y0, title, ribbon, groups, board, trimmed=(), note=None):
        S.text(x0, y0, title, bold=True)
        top, bot = y0 + 40, y0 + 150
        pos = {}
        for i, n in enumerate(ribbon):
            x = x0 + 20 + 50 * i
            pos[i] = x
            S.circle(x, top, 8, fill="#333" if n not in trimmed else "#fff", stroke="#333")
            S.text(x, top - 14, n if n != "X" else "trim", size=10, anchor="middle")
        for (a, b, lab) in groups:
            S.line(pos[a] - 8, top + 14, pos[b] + 8, top + 14, stroke=GREY, w=1)
            S.text((pos[a] + pos[b]) / 2, top + 28, lab, size=10, anchor="middle", fill=GREY)
        cav = {}
        for j, n in enumerate(board):
            x = x0 + 20 + 50 * j
            cav[n] = x
            S.rect(x - 16, bot, 32, 26, fill="#fff")
            S.text(x, bot + 16, str(j + 1), size=11, anchor="middle")
            S.text(x, bot + 42, n, size=10, anchor="middle")
        crossings = 0
        segs = []
        for i, n in enumerate(ribbon):
            if n in trimmed:
                S.text(pos[i], top + 50, "x", fill=RED, size=14, anchor="middle")
                continue
            segs.append((pos[i], cav[n]))
        for i in range(len(segs)):
            for j in range(i + 1, len(segs)):
                if (segs[i][0] - segs[j][0]) * (segs[i][1] - segs[j][1]) < 0:
                    crossings += 1
        for a, b in segs:
            straight = abs(a - b) < 1
            S.line(a, top + 36, b, bot - 2, stroke=GREEN if straight else RED, w=2)
        if note:
            S.text(x0, bot + 62, note, size=11, fill=GREY)
        return crossings

    S.panel(15, 55, 970, 265, "J4 SENSORS: 4P (1-wire and flow pairs) + 3P (GND and the moisture pair)")
    mapping(30, 100, "today: pins 1-7 = 3V3, GND, V5, IO25, IO26, IO27, IO23",
            ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"], [(0, 3, "4P"), (4, 6, "3P")],
            ["3V3", "GND", "V5", "IO25", "IO26", "IO27", "IO23"],
            note="3 layers, 5 crossings in one plane [w3b s6]")
    mapping(520, 100, "(a) swap pins 2 and 5",
            ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"], [(0, 3, "4P"), (4, 6, "3P")],
            ["3V3", "IO26", "V5", "IO25", "GND", "IO27", "IO23"],
            note="1 layer, no crossing; half-rows (0, 0)")

    S.panel(15, 330, 970, 265, "J7 REEDS B: 5P (reservoir B column and GND) + 3P (CLO, CHI, one trimmed)")
    mapping(30, 375, "today: pins 1-7 = RB1, RB2, RB3, RB4, CLO, CHI, GND",
            ["RB1", "RB2", "RB3", "RB4", "GND", "X", "CLO", "CHI"], [(0, 4, "5P"), (5, 7, "3P")],
            ["RB1", "RB2", "RB3", "RB4", "CLO", "CHI", "GND"], trimmed=("X",),
            note="2 crossings in one plane; 1 in half-rows")
    mapping(520, 375, "(a) GND to pin 5; 3P laid CLO, CHI, trim",
            ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI", "X"], [(0, 4, "5P"), (5, 7, "3P")],
            ["RB1", "RB2", "RB3", "RB4", "GND", "CLO", "CHI"], trimmed=("X",),
            note="straight in both counts")

    S.panel(15, 605, 970, 125, "Other ways to the same end")
    S.lines(30, 646, [
        "(a') no board change: J4 by pin block (4P = pins 1-4, 3P = pins 5-7); J7 with GND on the 3P. Straight; the far end peels at more places.",
        "(b) one ribbon, one housing: J1 -> XHP-5 + XHP-4, J2 -> XHP-2 + XHP-3, J4 -> XHP-4 + XHP-3, J7 -> XHP-5 + XHP-2; ~9-11 mm more board edge;",
        "      4P into XHP-4 becomes 7 of 14 ends; no pair is ever fed edge to edge.",
        "(c) one loom, one ribbon: 6P, 7P, 9P ribbon in pin order; the crossing moves to the hand-made far end (ribbon availability unchecked).",
    ], size=11)
    S.save("c7-straight-across.svg", "c7 Straight across: the pin map is the only reason two looms cross",
           "schematic: ribbon conductors (top) to housing cavities (bottom); red lines cross, green lines run straight; board pin orders from pcba.tsx")


if __name__ == "__main__":
    c6_shapes()
    c6b_bench()
    c1c()
    c7()
    print("wrote c6-shapes.svg, c6b-bench.svg, c1c-crimp-in-the-row.svg, c7-straight-across.svg")
