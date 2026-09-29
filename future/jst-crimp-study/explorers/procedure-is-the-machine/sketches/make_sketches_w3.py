"""Current schematic sketches for procedure-is-the-machine.

Run: python3 make_sketches_w3.py   (writes the .svg files beside this script)

Writes: p1-crimp-station, p1c-lift-once, p1d-fin-from-below, p2-turret, p3-spool-cut-last,
p4b-two-heads, p5-camshaft-layout, p5-cam-timing, p5b-cam-timing, p5c-knee-cam-timing,
p6-spool-end-bench, p6b-reel-end-docks, p7-strip-before-split.

All drawings are schematic: shapes show order, references and what moves, not scale. The end
views of p1d and p1c are drawn at a fixed px/mm from the dimensions in calc/wave3.out.txt and
xh-facts.md, and say so in their captions.
"""

import math

from make_sketches import Svg, BLUE, RED, GREEN, GREY, LIGHT, AMBER, INK

STEEL = "#c9ccd1"
PALE_RED = "#fbeaea"
PALE_GREEN = "#e6f3ea"
PALE_AMBER = "#fbf1e2"


def poly(s, pts, stroke=INK, fill="none", sw=1.2, dash=None):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    s.path(d, stroke=stroke, fill=fill, sw=sw, dash=dash)


def dcircle(s, cx, cy, r, stroke=INK, dash="3,3", sw=1.2):
    s.path(f"M {cx-r:.1f} {cy:.1f} a {r:.1f} {r:.1f} 0 1 0 {2*r:.1f} 0 a {r:.1f} {r:.1f} 0 1 0 {-2*r:.1f} 0",
           stroke=stroke, dash=dash, sw=sw)


def step_list(s, x, y, steps, w_label=110, dy=34, size=10):
    for i, (a, b) in enumerate(steps):
        yy = y + i * dy
        s.rect(x, yy - 14, w_label, 24, fill=LIGHT, stroke=BLUE)
        s.text(x + 6, yy + 2, a, size=size, weight="bold", fill=BLUE)
        s.text(x + w_label + 10, yy + 2, b, size=size)


def timing(s, x0, y0, W, rows, label_x=20, dy=28):
    s.line(x0, y0, x0 + W, y0, stroke=INK)
    for d in range(0, 361, 30):
        x = x0 + W * d / 360
        s.line(x, y0 - 4, x, y0 + 4)
        s.text(x - 8, y0 - 8, f"{d}", size=9)
    for i, (lab, a, b, col) in enumerate(rows):
        y = y0 + 24 + i * dy
        s.text(label_x, y + 12, lab, size=10)
        s.rect(x0 + W * a / 360, y, W * (b - a) / 360, 16, fill=col, stroke=col, op=0.35)
    return y0 + 24 + len(rows) * dy


# ----------------------------------------------------------------------------------------------
def p1_crimp_station():
    s = Svg(1150, 660, "p1 bench B, form B-drop: the contact waits cut free on a stepped fin (schematic)",
            "Side section along the wire (left) and end view from the tip (right). 'Fixed' is the bench frame; "
            "the cassette is located to it by its pins.")
    s.text(40, 80, "Side section", size=13, weight="bold")
    s.rect(40, 230, 150, 45, fill=LIGHT, stroke=BLUE)
    s.text(48, 250, "cassette: clamp (hard stop,\n15-30 % squeeze), fan, comb", size=9, fill=BLUE)
    s.rect(30, 290, 420, 14, fill="#ddd", stroke=GREY)
    s.text(40, 322, "slide (lead screw) indexes 2.5 mm per key", size=10)
    for dx in (70, 160):
        s.circle(dx, 285, 5, fill="#fff", stroke=RED, sw=2)
    s.path("M 190 256 C 250 256, 280 330, 400 345", stroke="#777", sw=5)
    s.text(150, 372, "neighbours pressed ~7 mm down by the\nslotted presser; k passes up its slot.\n"
                     "Each keeps a set: 1.3-4.5 mm at 20 mm free", size=10, fill="#555")
    s.rect(245, 190, 36, 48, fill="#f4f4f4", stroke=GREY)
    s.line(263, 150, 263, 188, arrow="k")
    s.text(215, 142, "slotted presser", size=10)
    s.line(190, 250, 478, 250, stroke="#111", sw=7)
    s.line(478, 250, 512, 250, stroke=AMBER, sw=3)
    # V-fork from below, 5-6 mm behind the strip line
    s.path("M 385 300 L 385 262 L 378 252 M 385 262 L 392 252", stroke=GREEN, sw=3)
    s.line(385, 330, 385, 302, arrow="k", stroke=GREEN)
    s.text(300, 410, "V-fork rises from below, 5-6 mm\nbehind the strip line; drops away\nbefore the punch arrives",
           size=10, fill=GREEN)
    # lay-in finger
    s.line(455, 170, 455, 240, stroke=BLUE, sw=3)
    s.text(395, 162, "lay-in finger", size=10, fill=BLUE)
    # contact cut free on the fin (no carrier)
    s.path("M 470 243 L 470 262 L 580 262 L 580 238 L 540 238 L 540 256 L 500 256 L 500 243",
           stroke=RED, sw=2)
    s.line(533, 232, 533, 262, stroke=INK, sw=2)
    s.text(640, 262, "contact cut free: box forward,\nheld by a 0.3 mm blade in its\nneck (or a stub on a pilot pin)",
           size=10, fill=RED)
    # stepped fin
    s.rect(470, 262, 80, 120, fill=STEEL, stroke=INK)
    s.rect(550, 262, 25, 120, fill=STEEL, stroke=INK)
    s.text(640, 318, "stepped fin, 9-10 mm tall:\n1.45 under the conductor barrel,\n1.8-1.9 under the insulation\n"
                     "barrel; relieved behind the lance", size=10)
    # punch + stops
    s.rect(470, 150, 110, 70, fill=STEEL, stroke=INK)
    s.rect(600, 170, 26, 50, fill="#aab", stroke=INK)
    s.rect(600, 222, 26, 50, fill="#aab", stroke=INK)
    s.text(632, 196, "stop blocks meet at crimp height\n(a short steel loop, shimmed)", size=10)
    s.line(525, 90, 525, 146, arrow="r", stroke=RED, sw=2)
    s.path("M 540 100 l 8 -5 l -16 -5 l 16 -5 l -16 -5 l 8 -5", stroke=RED, sw=1.5)
    s.text(560, 96, "ram through a stiff spring: overtravel past the stops\ncosts only k x m (5-10 kN/mm loop: "
                    "1.05-1.4x the crimp)", size=10, fill=RED)
    # load cell under the whole lower die
    s.rect(460, 384, 180, 14, fill=PALE_AMBER, stroke=AMBER)
    s.text(460, 414, "force sensed under the whole lower die (fin holder and\nstops together), outside the stop loop; "
                     "or foil gauges", size=10, fill=AMBER)
    # end view
    ex, ey = 1000, 300
    s.text(880, 80, "End view from the tip", size=13, weight="bold")
    sc = 16
    s.rect(ex - 0.94 * sc, ey + 12, 1.88 * sc, 170, fill="none", stroke=INK, dash="4,3")
    s.rect(ex - 0.725 * sc, ey + 12, 1.45 * sc, 170, fill=STEEL, stroke=INK)
    s.path(f"M {ex-1.4*sc} {ey-1.9*sc} L {ex-0.9*sc} {ey+12} L {ex+0.9*sc} {ey+12} L {ex+1.4*sc} {ey-1.9*sc}",
           stroke=RED, sw=2.5)
    s.circle(ex, ey - 0.3 * sc, 0.85 * sc, fill="#111")
    s.text(ex + 30, ey, "k in the open barrels", size=10)
    s.rect(ex - 1.7 * sc, ey - 7 * sc, 3.4 * sc, 3.4 * sc, fill=STEEL, stroke=INK)
    s.text(ex + 40, ey - 5.5 * sc, "punch: nothing else\nis up here", size=10)
    for kk in (-3, -2, -1, 1, 2, 3):
        s.circle(ex + kk * 2.5 * sc, ey + 7.5 * sc, 0.85 * sc, fill="#777")
    s.text(860, ey + 12 * sc + 40, "neighbours ~7 mm lower at 2.5 mm pitch; the fin\n"
                                    "(solid 1.45 mm, dashed 1.88 mm step) stands\n"
                                    "between k-1 and k+1, 3.3 mm apart", size=10)
    s.text(40, 470, "What locates what: lateral, the V-fork at the moment of use (+/-0.05 mm); axial, the trim line on the "
                    "cassette pins and the contact's own\nreference on the fin (blade on the box shoulder, +/-0.075 mm); "
                    "crimp height, the stop blocks. Axial chain +/-0.23 mm RSS against a +/-0.3 mm window\n"
                    "[calc wave2 §3]. Identity: the strands land on the barrel floor at lay-in, so the fin reads which "
                    "far-end conductor is in the contact.\nProof pull: a hook behind the box, punch up, 20 N against a "
                    "spring, reacted by the cassette clamp.\nThe other forms of bench B: p1c (lift k 8.7-14.7 mm under an "
                    "SN-2549 on its side) and p1d (lift k 3.5 mm, fin from below).", size=11)
    s.save("p1-crimp-station.svg")


# ----------------------------------------------------------------------------------------------
def p1c_lift_once():
    s = Svg(1100, 760, "p1c Lift once under a hand-tool module: the SN-2549 lies on its side (schematic)",
            "End view along the wire, 12 px/mm for the row and the lift; the tool's outline is not to scale. "
            "Numbers: calc/wave3.out.txt §1.")
    sc = 12
    ox, oy = 60, 450          # row axis
    s.text(40, 80, "End view (looking from the tool toward the cassette)", size=12, weight="bold")
    kx = ox + 230
    for i in range(-3, 4):
        if i == 0:
            continue
        s.circle(kx + i * 2.5 * sc, oy, 0.85 * sc, fill="#333", stroke="#333")
    a = 9.0
    h = a + 2.7
    ky = oy - h * sc
    s.circle(kx, ky, 0.85 * sc, fill="#333", stroke="#333")
    s.rect(kx - 3 * sc, ky + 0.2 * sc, 18 * sc, a * sc - 0.2 * sc, fill="#dde", stroke=INK)
    s.rect(kx - 3 * sc, ky - 6 * sc, 18 * sc, 5 * sc, fill="#dde", stroke=INK)
    s.text(kx + 4 * sc, ky - 3 * sc, "upper jaw", size=10)
    s.text(kx + 2 * sc, ky + 4 * sc, "anvil jaw half, depth a\nbelow the nest floor", size=10)
    s.line(kx + 15 * sc, ky - 6 * sc, kx + 24 * sc, ky - 11 * sc, stroke=GREY, sw=6)
    s.line(kx + 15 * sc, ky + a * sc, kx + 24 * sc, ky + (a + 3) * sc, stroke=GREY, sw=6)
    s.text(kx + 17 * sc, ky - 13 * sc, "handles and pusher off to +X", size=10, fill="#555")
    s.line(kx - 5 * sc, ky - 1.5 * sc, kx - 5 * sc, ky + 1.5 * sc, stroke=RED, arrow="r-end-both")
    s.text(40, ky - 70, "jaws close vertically: the closing\ndirection is the contact's floor\nnormal, so the crimp "
                        "is upright", size=10, fill=RED)
    s.text(40, ky + 30, "mouth opens to -X: the module\narrives and leaves sideways over k", size=10, fill="#555")
    s.line(kx - 11 * sc, oy, kx - 11 * sc, ky, stroke=BLUE, arrow="b-end-both")
    s.text(kx - 11 * sc - 110, (oy + ky) / 2 + 20, "h = a + 2.7\n= 8.7-14.7 mm", size=10, fill=BLUE)
    s.line(ox + 40, oy, ox + 440, oy, stroke=GREY, dash="4,3")
    s.path(f"M {kx-10} {oy+40} L {kx-10} {ky+a*sc+12} M {kx+10} {oy+40} L {kx+10} {ky+a*sc+12}",
           stroke=GREEN, sw=2, dash="5,3")
    s.text(kx + 14, oy + 36, "lift finger (10 mm behind, dashed)", size=9, fill=GREEN)
    s.text(40, oy + 70, "The jaw's back face sits ~2.1 mm above the row axis, ~1 mm over a crimped neighbour. Residual rise:\n"
                        "0-2.3 mm at 30 mm free for h 8.7; 0.4-5.7 mm at 35 mm for h 14.7 [calc wave3 §1]:\n"
                        "a 30-35 mm split and a squaring push after every crimp.", size=10)
    ix, iy = 40, oy + 130
    s.rect(ix, iy, 420, 110, fill="#fafafa", stroke=GREY, dash="4,3")
    s.text(ix + 8, iy + 18, "Not used: hung tip-down, closing along the row", size=10, weight="bold", fill=RED)
    for j in range(4):
        cx = ix + 60 + j * 70
        cy = iy + 55
        s.rect(cx - 14, cy - 12, 24, 22, fill="#fff", stroke=INK)
        s.path(f"M {cx+10} {cy+10} L {cx+18} {cy+16}", stroke=RED, sw=2)
    s.text(ix + 8, iy + 92, "every crimp rolled 90 deg: barrels open along the row, every lance\nat a neighbour; no "
                            "housing slides onto the row", size=9, fill="#555")
    sx, sy = 640, 110
    s.text(sx, sy - 16, "One conductor, in one pose", size=12, weight="bold")
    steps = [
        ("pick", "k still in the row: jaws over the contact on its\npost; close only to wing touch; blade in the neck"),
        ("lift", "finger raises k by a + 2.7 mm"),
        ("trim", "shuttle brings the grounded blade: squares the\ntip and reads identity through the far end"),
        ("strip", "V-jaws or a spindle, 2.4 mm, in the pose"),
        ("measure", "ELP on a backlight: bare length, brush"),
        ("feed", "module slides the contact onto k to the\nmeasured depth; tips stop short of the blade"),
        ("crimp", "pause at the end of the curl (identity again),\nthen complete the ratchet; curve logged"),
        ("pull", "jaws open to the blade; 20 N through the box"),
        ("release", "jaws open fully; module leaves in +X"),
        ("square", "finger lowers k; presser pushes the crimp into\nthe row within ~0.5 mm"),
    ]
    step_list(s, sx, sy + 14, steps, w_label=72, dy=52, size=10)
    s.save("p1c-lift-once.svg")


# ----------------------------------------------------------------------------------------------
def p1d_fin_from_below():
    s = Svg(1100, 900, "p1d Lift once, crimp upright: a fin rises from below into a steel C (schematic)",
            "Left: end view at 30 px/mm from calc/wave3.out.txt §2 and xh-facts §1 (the C's outline is not to "
            "scale). Right: side section, not to scale.")
    sc = 30
    ox, oy = 250, 470   # row axis, k's slot centre
    s.text(40, 80, "End view at the barrels, looking from the box toward the cassette", size=12, weight="bold")
    # neighbours, uncrimped jackets
    for i in (-3, -2, -1, 1, 2, 3):
        s.circle(ox + i * 2.5 * sc, oy, 0.85 * sc, fill="#333", stroke="#333")
        s.circle(ox + i * 2.5 * sc, oy, 0.36 * sc, fill="#d9a441", stroke="#b58a2a")
    # tip comb pins (behind, dashed)
    for i in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
        s.rect(ox + i * 2.5 * sc - 0.32 * sc, oy - 0.85 * sc, 0.64 * sc, 1.85 * sc, fill="none", stroke=GREEN,
               dash="3,3")
    s.text(ox + 3.1 * 2.5 * sc, oy - 40, "tip comb pins\n5-7 mm behind\n(dashed)", size=9, fill=GREEN)
    # k lifted 3.5 mm, stripped strands in the open conductor barrel
    ky = oy - 3.5 * sc
    dcircle(s, ox, ky, 0.85 * sc, stroke="#333")
    s.circle(ox, ky, 0.36 * sc, fill="#d9a441", stroke="#b58a2a")
    floor = ky + 0.36 * sc
    s.path(f"M {ox-0.9*sc} {ky-1.25*sc} L {ox-0.9*sc} {floor} L {ox+0.9*sc} {floor} L {ox+0.9*sc} {ky-1.25*sc}",
           stroke=RED, sw=3)
    s.path(f"M {ox-1.35*sc} {ky-1.9*sc} L {ox-1.1*sc} {floor+0.2*sc} L {ox+1.1*sc} {floor+0.2*sc} "
           f"L {ox+1.35*sc} {ky-1.9*sc}", stroke=RED, sw=1.2, dash="5,3")
    s.text(ox + 2.0 * sc, ky - 1.6 * sc, "k lifted 3.5 mm: strands in the open\nconductor barrel (solid); jacket in the\n"
                                         "open insulation wings behind (dashed)", size=9, fill=RED)
    # fin: conductor step 1.45 solid, insulation step 1.88 dashed; from floor down to the lower arm
    fin_top = floor + 0.2 * sc
    arm_y = oy + 3.0 * sc
    s.rect(ox - 0.725 * sc, fin_top, 1.45 * sc, arm_y - fin_top, fill=STEEL, stroke=INK)
    s.rect(ox - 0.94 * sc, fin_top, 1.88 * sc, arm_y - fin_top, fill="none", stroke=INK, dash="4,3")
    # clearance annotations
    y1 = oy
    s.line(ox + 0.725 * sc, y1 + 10, ox + (2.5 - 0.85) * sc, y1 + 10, stroke=BLUE, arrow="b-end-both")
    s.text(ox + 0.8 * sc, y1 + 28, "0.92", size=9, fill=BLUE)
    s.line(ox - 0.94 * sc, y1 + 22, ox - (2.5 - 0.85) * sc, y1 + 22, stroke=BLUE, arrow="b-end-both")
    s.text(ox - 1.6 * sc, y1 + 40, "0.71", size=9, fill=BLUE)
    s.text(40, oy + 205, "Fin to an uncrimped neighbour's jacket: 0.92 mm a side at the conductor step (1.45 mm),\n"
                         "0.71 mm at the insulation step (1.88 mm); against crimped, squared neighbours 1.02 and 0.56 mm.\n"
                         "Fin travel from rest (1 mm under the row) to the contact floor ~4.8 mm [calc wave3 §2].",
           size=10, fill=BLUE)
    # lower arm and upper arm of the C (not to scale)
    s.rect(ox - 5.5 * sc, arm_y, 11 * sc, 1.2 * sc, fill=STEEL, stroke=INK)
    s.text(ox - 5.5 * sc, arm_y + 1.2 * sc + 16, "lower arm of the C: entirely below the row; the fin slides in it,\n"
                                                 "a gate wedge goes under its foot (the height dial)", size=9)
    # crimper above
    cr_bot = ky - 1.9 * sc
    s.rect(ox - 1.55 * sc, cr_bot - 3.2 * sc, 3.1 * sc, 3.2 * sc, fill=STEEL, stroke=INK)
    s.path(f"M {ox-0.75*sc} {cr_bot} L {ox-0.75*sc} {cr_bot-1.0*sc} Q {ox} {cr_bot-1.6*sc} {ox+0.75*sc} "
           f"{cr_bot-1.0*sc} L {ox+0.75*sc} {cr_bot}", stroke=INK, fill="#fff")
    s.rect(ox - 5.5 * sc, cr_bot - 4.4 * sc, 11 * sc, 1.2 * sc, fill=STEEL, stroke=INK)
    s.text(ox - 5.5 * sc, cr_bot - 4.4 * sc - 8, "upper arm: knee drives a narrow stepped crimper (3.1 mm at the "
                                                 "conductor step)", size=9)
    s.line(ox + 2.0 * sc, cr_bot - 2.8 * sc, ox + 2.0 * sc, cr_bot - 0.4 * sc, arrow="k", stroke=INK)
    s.line(40, oy, ox + 8.5 * sc, oy, stroke=GREY, dash="4,3", sw=0.8)
    s.text(ox + 8.6 * sc, oy + 4, "row axis", size=9, fill=GREY)

    # side section
    bx, by = 640, 470
    s.text(620, 80, "Side section (not to scale)", size=12, weight="bold")
    s.rect(620, by - 40, 90, 80, fill=LIGHT, stroke=BLUE)
    s.text(626, by - 20, "cassette\nclamp and\nroot comb", size=9, fill=BLUE)
    s.line(710, by, 830, by, stroke="#777", sw=6)
    s.text(716, by + 70, "neighbours stay in the row", size=9, fill="#555")
    s.path(f"M 710 {by} C 760 {by}, 780 {by-38}, 830 {by-38}", stroke="#111", sw=6)
    s.line(830, by - 38, 870, by - 38, stroke="#111", sw=6)
    s.line(870, by - 38, 895, by - 38, stroke=AMBER, sw=3)
    s.rect(770, by - 30, 8, 55, fill=PALE_GREEN, stroke=GREEN)
    s.text(742, by + 40, "lift finger", size=9, fill=GREEN)
    s.rect(838, by - 12, 6, 24, fill="none", stroke=GREEN, dash="3,2")
    s.text(812, by + 26, "tip comb", size=9, fill=GREEN)
    # contact on k
    s.path(f"M 862 {by-44} L 862 {by-32} L 905 {by-32} L 905 {by-48} L 930 {by-48} L 930 {by-28} L 905 {by-28}",
           stroke=RED, sw=2)
    s.text(912, by - 58, "box", size=9, fill=RED)
    s.path(f"M 916 {by-28} l 6 7", stroke=RED, sw=2)
    s.text(924, by - 16, "lance", size=9, fill=RED)
    # post bar ahead
    s.line(930, by - 40, 975, by - 40, stroke=INK, sw=2)
    s.rect(975, by - 55, 30, 30, fill=PALE_AMBER, stroke=AMBER)
    s.rect(975, by - 55, 30, 12, fill=PALE_AMBER, stroke=AMBER)
    s.text(920, by - 120, "post bar (two tiers):\nslides the open contact\nonto k along Y", size=9, fill=AMBER)
    s.line(1010, by - 40, 1040, by - 40, arrow="k")
    # fin under the barrels, stopping behind the lance
    s.rect(866, by - 30, 44, 80, fill=STEEL, stroke=INK)
    s.text(870, by + 64, "fin", size=9)
    # C: spine ahead of the tips, arms
    s.rect(1045, by - 180, 18, 280, fill=STEEL, stroke=INK)
    s.rect(850, by - 180, 213, 22, fill=STEEL, stroke=INK)
    s.rect(850, by + 60, 213, 22, fill=STEEL, stroke=INK)
    s.text(1000, by + 110, "spine ~25-30 mm ahead\nof the tips; the post bar\nindexes in its throat", size=9)
    s.rect(866, by - 158, 44, 90, fill=STEEL, stroke=INK)
    s.text(870, by - 75, "crimper", size=9)
    s.path(f"M 890 {by-158} L 870 {by-130} L 890 {by-102}", stroke=RED, sw=2.5)
    s.text(760, by - 150, "knee: straight\nis the bottom", size=9, fill=RED)
    s.line(700, by - 130, 866, by - 130, arrow="k", stroke=RED)
    s.text(640, by - 118, "NEMA 17 Tr8x2,\n60-160 N", size=9, fill=RED)
    s.rect(866, by + 50, 44, 10, fill=PALE_AMBER, stroke=AMBER)
    s.text(790, by + 100, "gate wedge under the fin's foot", size=9, fill=AMBER)

    # steps
    s.text(40, 750, "One key: index - lift 3.5 mm - trim (grounded blade: identity) - strip in the pose or after p7 - "
                    "look (backlit silhouette) - post bar slides the open contact on -\n"
                    "fin up, gate in - knee to the end of the curl, pause (identity through the C) - knee to straight - "
                    "re-touch, indicator reads height - clear - hook pulls 20 N\n"
                    "through the box - lay back and square. 55-76 s a key; J1 8-11 min [calc wave3 §6].", size=10)
    s.text(40, 820, "'Fixed' for position: bench B's frame. 'Fixed' for crimp height: the steel C alone (knee at straight + "
                    "gate wedge; +/-1.5-6 um of scatter at 100-200 kN/mm).\nOnly the fin passes through the row "
                    "plane, so k rises 3.5 mm; at 25 mm free it keeps 0-0.05 mm of set [calc wave3 §1].", size=10)
    s.save("p1d-fin-from-below.svg")


# ----------------------------------------------------------------------------------------------
def p2_turret():
    s = Svg(1000, 580, "p2 Still ribbon, tools come to it (schematic, side view)",
            "The ribbon end is clamped once and never re-gripped. The y carriage selects conductor, post or "
            "cavity; a drum turret (rotate + x) brings each tool.")
    s.rect(40, 300, 420, 20, fill="#ddd", stroke=GREY)
    s.text(50, 335, "y carriage (into the page): conductor k, a contact post, or a housing cavity to the work line",
           size=10)
    s.rect(60, 230, 150, 70, fill=LIGHT, stroke=BLUE)
    s.text(70, 255, "work clamp + comb;\nfar end in a pogo\nblock on the carriage", size=10, fill=BLUE)
    s.line(210, 250, 380, 250, stroke="#111", sw=7)
    s.line(380, 250, 410, 250, stroke=AMBER, sw=3)
    s.text(250, 238, "conductor k, lifted once by the selector", size=10)
    s.rect(290, 262, 12, 38, fill="#999", stroke=INK)
    s.text(240, 290, "selector", size=10)
    s.rect(230, 360, 120, 34, fill=PALE_RED, stroke=RED)
    s.text(238, 381, "contact posts (on y)", size=10, fill=RED)
    s.rect(370, 360, 80, 34, fill=LIGHT, stroke=BLUE)
    s.text(376, 381, "housing nest", size=10, fill=BLUE)
    tx, ty = 690, 250
    s.circle(tx, ty, 150, fill="#f7f7f7", stroke=GREY)
    tools = [("strip jaws", BLUE), ("crimp head\nC, T or F", RED), ("camera +\nring light", GREEN),
             ("insertion\ngripper", BLUE), ("trim blade", AMBER), ("web splitter", AMBER)]
    for i, (name, col) in enumerate(tools):
        a = math.radians(180 + i * 60)
        x = tx + 110 * math.cos(a)
        y = ty + 110 * math.sin(a)
        s.rect(x - 38, y - 18, 76, 36, fill="#fff", stroke=col, sw=1.6, rx=4)
        s.text(x - 34, y - 2, name, size=9, fill=col)
    s.line(575, 250, 460, 250, arrow="r", stroke=RED, sw=2)
    s.text(470, 215, "x: the tool at 9 o'clock\napproaches along the wire", size=10, fill=RED)
    s.text(40, 450, "Crimp heads, each upright and each closing its force inside itself:\n"
                    "  C  strip-fed C-frame: conductor enters the open contact axially over the carrier; lead-in halves part "
                    "after the stroke so the crimp can leave.\n"
                    "  T  SN-2549 on its side (p1c): picks a cut-free contact, closes only to wing touch; lift 8.7-14.7 mm.\n"
                    "  F  steel C with a fin from below (p1d): the lower arm slides under the cantilevered tips; lift 3.5 mm.\n"
                    "Per conductor: y to k, lift, strip, crimp (identity at the end of the curl), look, then the gripper "
                    "bows the conductor ~10 mm and pushes the\ncontact into its cavity; or, in branch p2', the housing "
                    "slides onto every contact at once.", size=10)
    s.save("p2-turret.svg")


# ----------------------------------------------------------------------------------------------
def p3_spool():
    s = Svg(1000, 720, "p3 Terminate at the spool, cut last (schematic, side view)",
            "The spool is the carrier and the rest of the spool is the test lead. Nothing is cut until the XH end "
            "has passed.")
    cx, cy = 130, 260
    s.circle(cx, cy, 90, fill="#f4f4f4", stroke=GREY)
    s.circle(cx, cy, 28, fill="#fff", stroke=GREY)
    s.rect(cx - 12, cy - 12, 24, 24, fill=GREEN, stroke=GREEN)
    s.text(60, 380, "spool (or 80 mm-hub reel): inner end ->\nhub socket -> slip ring -> tester", size=10)
    s.path(f"M {cx+90} {cy+10} C 300 {cy+10}, 300 200, 360 200", stroke="#333", sw=5)
    s.rect(360, 170, 80, 16, fill="#bbb", stroke=INK, rx=8)
    s.rect(360, 214, 80, 16, fill="#bbb", stroke=INK, rx=8)
    s.text(350, 160, "belt feed + encoder", size=10)
    s.line(440, 200, 480, 200, stroke="#333", sw=5)
    s.rect(480, 180, 70, 40, fill=LIGHT, stroke=BLUE)
    s.text(482, 172, "work clamp on X", size=10, fill=BLUE)
    s.rect(560, 230, 10, 40, fill=AMBER, stroke=AMBER)
    s.text(520, 290, "guillotine at the\nclamp face (cuts last)", size=10, fill=AMBER)
    s.rect(580, 90, 250, 70, fill="#fff", stroke=RED, rx=6)
    s.text(588, 110, "strip (p7), split, fan; then per conductor a\nlift-once station: SN on its side (p1c) or\n"
                     "fin from below (p1d); identity through the spool", size=10, fill=RED)
    s.line(640, 160, 600, 196, arrow="r", stroke=RED)
    s.line(550, 200, 620, 200, stroke="#333", sw=5)
    s.rect(620, 186, 14, 28, fill="#fff", stroke=INK)
    s.text(612, 236, "XHP", size=9)
    # puller rail
    s.rect(560, 330, 400, 12, fill="#eee", stroke=GREY)
    s.rect(640, 318, 40, 24, fill=PALE_GREEN, stroke=GREEN)
    s.line(680, 330, 900, 330, arrow="k", stroke=GREEN)
    s.text(560, 370, "puller: a belt carriage clips the ribbon just behind the housing and draws the loom\n"
                     "length out along the rail; the housing is never the handle", size=10, fill=GREEN)
    s.path("M 634 214 C 660 260, 700 300, 700 420", stroke="#333", sw=3, dash="6,4")
    s.rect(680, 420, 40, 60, fill="none", stroke=GREY, dash="4,3")
    s.text(730, 450, "drop-tube form (alternative\nwhere bench front is short)", size=10, fill=GREY)
    s.text(40, 520, "Order at the machine, per ribbon end:", size=12, weight="bold")
    order = [("feed to stop", BLUE), ("trim", BLUE), ("strip + split", BLUE), ("place + crimp", RED),
             ("look / pull", BLUE), ("insert (singles)", BLUE), ("test through spool", GREEN),
             ("pull out L", AMBER), ("cut", AMBER)]
    x = 40
    for name, col in order:
        w = 12 + 7 * len(name)
        s.rect(x, 540, w, 28, fill="#fff", stroke=col, rx=4)
        s.text(x + 6, 559, name, size=10, fill=col)
        s.line(x + w, 554, x + w + 10, 554, arrow="k")
        x += w + 12
    s.text(40, 610, "A bad crimp found at 'look' or 'test': cut ~6 mm back and go round again. It costs spool, never a "
                    "loom, so no loom carries a redo reserve\nand a pair's two ribbons stay equal. Far ends (Fastons, "
                    "ferrules, IDC) are made by hand after the cut, so the automated risk comes first.", size=10)
    s.save("p3-spool-cut-last.svg")


# ----------------------------------------------------------------------------------------------
def p4b_two_heads():
    s = Svg(980, 380, "p4b Two heads, one person: the person's pace sets the rhythm (schematic timeline)",
            "Head cycle 26 s [estimate]; person presents 5 s and inserts 8 s. Numbers: calc/wave2.out.txt §4.")
    x0, y0 = 150, 90
    scale = 7.2
    rows = [("person", RED), ("head A", BLUE), ("head B", GREEN)]
    for i, (lab, col) in enumerate(rows):
        s.text(30, y0 + i * 60 + 18, lab, size=12, weight="bold", fill=col)
        s.line(x0, y0 + i * 60 + 30, x0 + 80 * scale, y0 + i * 60 + 30, stroke=GREY, sw=0.6)
    t = 0.0
    k = 1
    head_free = {"A": 0.0, "B": 0.0}
    for n in range(6):
        head = "A" if n % 2 == 0 else "B"
        start = max(t, head_free[head])
        s.rect(x0 + start * scale, y0 + 8, 5 * scale, 22, fill="#f7dede", stroke=RED)
        s.text(x0 + start * scale + 2, y0 + 23, f"p{k}", size=9, fill=RED)
        row = 1 if head == "A" else 2
        s.rect(x0 + (start + 5) * scale, y0 + row * 60 + 8, 26 * scale, 22,
               fill=LIGHT if head == "A" else PALE_GREEN, stroke=BLUE if head == "A" else GREEN)
        s.text(x0 + (start + 5) * scale + 4, y0 + row * 60 + 23,
               f"conductor {k}: strip, locate contact, feed, crimp, pull", size=9)
        head_free[head] = start + 5 + 26
        if k >= 3:
            s.rect(x0 + (start + 5) * scale, y0 + 8, 8 * scale, 22, fill="#fbeede", stroke=AMBER)
            s.text(x0 + (start + 5) * scale + 2, y0 + 23, f"ins {k-2}", size=9, fill=AMBER)
        t = start + 13
        k += 1
    s.text(30, y0 + 200, "p = present conductor k to a head's funnel: its copper face touches the grounded tip stop, which "
                         "reads identity before anything is cut.\nins = insert a finished contact into its lit cavity on "
                         "the sensing nest. 'locate contact' = the SN closes only to wing touch, so the wings stay open.\n"
                         "With one head the person waits whenever the cycle is longer than present + insert; with two, a "
                         "26 s cycle leaves ~2-3 s of waiting per conductor.", size=10, fill="#555")
    s.save("p4b-two-heads.svg")


# ----------------------------------------------------------------------------------------------
def p5_layout():
    s = Svg(1000, 620, "p5 Camshaft: one motor, one revolution per conductor (schematic)",
            "The shaft runs above the work. Printed face cams drive the light motions down to the work point; a "
            "steel eccentric drives the punch onto a stepped fin.")
    y = 130
    s.rect(40, y - 30, 70, 60, fill="#ccc", stroke=INK)
    s.text(40, y + 48, "gearmotor or\nNEMA 17 planetary\n(1.0-2.3 N*m peak)", size=10)
    s.line(110, y, 960, y, stroke=INK, sw=6)
    cams = [("index pawl", GREY), ("presser", BLUE), ("V-fork", GREEN), ("strip jaws", AMBER), ("strip pull", AMBER),
            ("lay-in", BLUE), ("revolver pawl:\ncut-free contact", RED), ("hook pull", GREEN)]
    for i, (name, col) in enumerate(cams):
        x = 170 + i * 62
        if x > 540:
            x += 200
        s.circle(x, y, 20, fill="#fff", stroke=col, sw=2)
        s.line(x, y + 20, x, y + 230, stroke=col, sw=2)
        s.circle(x, y + 20, 4, fill=col, stroke=col)
        s.text(x - 26, y - 30, name, size=9, fill=col)
    s.rect(150, y + 230, 400, 36, fill="none", stroke=GREY, dash="4,3")
    s.text(158, y + 252, "followers and levers reach the work point (printed PET-CF cams, forces under ~50 N)",
           size=10)
    ex = 650
    s.circle(ex, y, 36, fill="#eee", stroke=RED, sw=2)
    s.text(ex - 40, y - 48, "PUNCH: steel eccentric,\ne 2.5 mm, rod 40 mm", size=9, fill=RED)
    s.line(ex, y + 36, ex, y + 100, stroke=RED, sw=3)
    s.path(f"M {ex} {y+100} l 10 6 l -20 6 l 20 6 l -20 6 l 10 6", stroke=RED, sw=2)
    s.line(ex, y + 130, ex, y + 160, stroke=RED, sw=3)
    s.text(ex + 18, y + 108, "optional rod spring (one or two DIN 2093\ndiscs, not preloaded) if the frame is stiff",
           size=9, fill=RED)
    s.rect(ex - 40, y + 160, 80, 40, fill=STEEL, stroke=INK)
    s.text(ex - 20, y + 185, "punch", size=10)
    s.rect(ex - 18, y + 200, 22, 10, fill="none", stroke=RED)
    s.rect(ex - 30, y + 212, 38, 90, fill=STEEL, stroke=INK)
    s.rect(ex + 8, y + 212, 14, 90, fill=STEEL, stroke=INK)
    s.text(ex - 30, y + 320, "stepped fin with the\ncut-free contact on it", size=9)
    s.rect(ex + 50, y + 170, 20, 40, fill="#aab", stroke=INK)
    s.rect(ex + 50, y + 212, 20, 40, fill="#aab", stroke=INK)
    s.text(ex + 76, y + 214, "stop blocks: crimp height\n(a short steel loop)", size=9)
    s.rect(ex - 70, y + 352, 170, 12, fill=PALE_AMBER, stroke=AMBER)
    s.text(ex - 70, y + 380, "force sensed under fin holder + stops together", size=9, fill=AMBER)
    s.text(40, 540, "The outer frame may be springy (5-10 kN/mm): the eccentric is set to push a margin m past the stops, "
                    "which costs k x m, 1.05-1.4x the crimp,\nand caps a doubled contact at 3.9-5.4 kN [calc wave3 §4]. "
                    "Skip (J2's key 3): a bump on the cassette rack holds the contact pawl clear and pulls\nthe punch "
                    "link pin for one turn. p5c replaces the eccentric, stops and fin with a knee in a small steel C.",
           size=10)
    s.save("p5-camshaft-layout.svg")


def p5_cam_timing():
    s = Svg(1000, 470, "p5 camshaft: one revolution per conductor (schematic timing, ~40 s a turn)",
            "Angles illustrate the sequence. The eccentric reaches the stops at 236-240 deg.")
    rows = [
        ("index cassette (pawl in its rack)", 0, 30, GREY),
        ("presser drops neighbours; V-fork rises", 30, 70, BLUE),
        ("strip jaws close, pull 3 mm, open", 70, 130, AMBER),
        ("lay-in finger: k into the open contact", 130, 150, BLUE),
        ("identity through the fin", 140, 150, GREEN),
        ("V-fork drops; wire-hold leaf takes over", 150, 170, GREEN),
        ("punch down: curl, then compaction to the stops", 170, 240, RED),
        ("punch up", 240, 290, RED),
        ("camera; hook pulls 15-20 N, punch up", 290, 330, GREEN),
        ("presser lifts; next cut-free contact onto the fin", 330, 360, AMBER),
    ]
    end = timing(s, 330, 80, 620, rows)
    s.text(20, end + 20, "No strip reaches the fin: contacts arrive cut free (a blade in the neck, or a one-pitch stub on "
                         "a pilot pin). On a fail the switch cam stops the shaft at 330 deg.", size=10, fill="#555")
    s.save("p5-cam-timing.svg")


def p5b_timing():
    s = Svg(1000, 600, "p5b One turn per conductor: the camshaft squeezes an SN-2549 lying on its side "
                       "(schematic timing)",
            "One self-locking gearmotor; the squeeze lobe sets the motor (2.1-3.2 N*m) [calc wave2 §5]. The shaft "
            "stops twice by angle.")
    rows = [
        ("index cassette", 0, 20, GREY),
        ("lift key k by a + 2.7 mm", 20, 50, GREEN),
        ("post wheel turns one post", 40, 70, AMBER),
        ("Y cam: open jaws over the contact on its post", 60, 90, GREEN),
        ("squeeze lobe: approach to just short of wing touch", 70, 110, BLUE),
        ("flap blade drops into the neck", 100, 115, AMBER),
        ("Y cam: contact off its post, onto k", 110, 160, GREEN),
        ("lobe to the end of the curl; PAUSE, identity", 160, 175, BLUE),
        ("squeeze lobe: crimp (last 8 mm of grip)", 175, 235, RED),
        ("ratchet completes and releases; lobe falls", 235, 250, BLUE),
        ("RELEASE CHECK: pawl switch, or the shaft stops", 250, 255, RED),
        ("Y back 0.5 mm against a 20 N spring: pull", 255, 285, GREEN),
        ("flap lifts; jaws open fully", 285, 300, AMBER),
        ("lift lowers k; presser squares the crimp", 300, 335, GREEN),
        ("camera frame; switch cam", 335, 360, GREY),
    ]
    end = timing(s, 330, 80, 620, rows)
    s.text(20, end + 20, "Trim and strip happen before the camshaft (bench A in the same pose, or p7). A skip bump on the "
                         "rack holds the post-wheel pawl and the squeeze\nfollower off for J2's key 3; the end bump stops "
                         "the shaft. A 30-35 mm split: the lift leaves 0-8 mm of rise until squared [calc wave3 §1].",
           size=10, fill="#555")
    s.save("p5b-cam-timing.svg")


def p5c_knee():
    s = Svg(1000, 720, "p5c The camshaft turns a knee: one motor, one turn per conductor (schematic)",
            "Timing (top) and the station the cams drive (bottom). The knee lobe carries the joint through "
            "straight, so crimp height is the links' geometry.")
    rows = [
        ("index cassette", 0, 25, GREY),
        ("lift k 3.5 mm", 25, 50, GREEN),
        ("camera: bare length, brush", 50, 60, GREY),
        ("post bar -Y: open contact onto k", 60, 110, AMBER),
        ("fin up through k's slot; gate wedge in", 110, 130, BLUE),
        ("knee lobe: curl; STOP at 150, identity via the C", 130, 150, RED),
        ("knee lobe: through straight onto its stop", 150, 200, RED),
        ("back off, re-touch ~10 N; indicator", 200, 215, BLUE),
        ("knee open, gate out, fin down, post bar back", 215, 240, AMBER),
        ("hook: 20 N through the box; switch", 240, 275, GREEN),
        ("lift lowers k; squaring tidies", 275, 320, GREEN),
        ("switch cam: go, or stop before the index", 320, 360, GREY),
    ]
    end = timing(s, 330, 80, 620, rows)
    y = end + 60
    s.line(80, y + 120, 900, y + 120, stroke=INK, sw=6)
    s.rect(30, y + 95, 50, 50, fill="#ccc", stroke=INK)
    s.text(20, y + 165, "12 V worm gearmotor\n+ ~5:1 belt, AS5600", size=9)
    for i, (name, col) in enumerate([("index", GREY), ("lift", GREEN), ("post Y", AMBER), ("fin/gate", BLUE),
                                     ("pull", GREEN), ("square", GREEN)]):
        x = 140 + i * 80
        s.circle(x, y + 120, 18, fill="#fff", stroke=col, sw=2)
        s.text(x - 18, y + 160, name, size=9, fill=col)
    kx = 700
    s.circle(kx, y + 120, 26, fill="#fff", stroke=RED, sw=2)
    s.text(kx - 26, y + 165, "knee lobe", size=9, fill=RED)
    s.line(kx, y + 94, kx, y + 40, stroke=RED, sw=2)
    s.path(f"M {kx} {y+40} L {kx+60} {y+10} L {kx+120} {y+40}", stroke=RED, sw=3)
    s.text(kx - 40, y + 30, "pushes the knee joint (60-160 N)", size=9, fill=RED)
    s.rect(kx + 150, y - 10, 16, 150, fill=STEEL, stroke=INK)
    s.rect(kx + 80, y - 10, 86, 14, fill=STEEL, stroke=INK)
    s.rect(kx + 80, y + 126, 86, 14, fill=STEEL, stroke=INK)
    s.text(kx + 172, y + 60, "steel C:\nthe crimp's\nforce loop", size=9)
    s.text(40, y + 200, "Shaft torque 0.25-1.9 N*m peak plus 0.1-0.3 for knee friction [force-and-form calc "
                        "exchange_procedure_w3 §8]; the printed cam frame carries only the knee's input.\n"
                        "J1 6-9 minutes, a unit 35-53 minutes of shaft time [calc wave3 §6]. Tooling as p1d.", size=10)
    s.save("p5c-knee-cam-timing.svg")


# ----------------------------------------------------------------------------------------------
def p6_spool_bench():
    s = Svg(1000, 840, "p6 The spool-end bench that grows (schematic, plan view of stage 0)",
            "Today's hand procedure moved to the spool: the XH end is made and tested before the loom exists; "
            "the cut that frees it squares the next end.")
    ox, oy = 40, 120
    for i, lab in enumerate(("5P", "4P", "3P")):
        yy = oy + i * 70
        s.rect(ox, yy, 110, 52, fill="#f4f4f4", stroke=GREY)
        s.circle(ox + 30, yy + 26, 20, fill="#fff", stroke=INK)
        s.circle(ox + 30, yy + 26, 6, fill=AMBER, stroke=AMBER)
        s.text(ox + 58, yy + 22, f"{lab} reel", size=11)
        s.text(ox + 58, yy + 37, "hub socket", size=9, fill=AMBER)
    s.text(ox, oy - 30, "reels: rewound once per spool onto an 80 mm hub radius,\n"
                        "inner end crimped into an XH socket in the hub", size=10, fill="#555")
    y4 = oy + 70 + 26
    s.line(ox + 110, y4, ox + 190, y4, stroke="#333", sw=5)
    s.rect(ox + 190, y4 - 22, 70, 44, fill=LIGHT, stroke=BLUE)
    for k in range(4):
        s.circle(ox + 200 + k * 16, y4 + (-9 if k % 2 == 0 else 9), 6, fill="#fff", stroke=BLUE)
    s.text(ox + 190, y4 + 38, "roller straightener\n(reverse bends)", size=9, fill=BLUE)
    s.line(ox + 260, y4, ox + 360, y4, stroke="#333", sw=5)
    cx = ox + 360
    s.rect(cx, y4 - 30, 90, 60, fill=LIGHT, stroke=BLUE, sw=1.6)
    s.text(cx - 20, y4 - 62, "channel clamp (0.2 mm under width,\nmarked edge on the wall, cam lever)", size=9,
           fill=BLUE)
    s.line(cx + 90, y4 - 40, cx + 90, y4 + 40, stroke=RED, sw=3)
    s.text(cx + 60, y4 + 58, "cut guide at the clamp face:\nthe cut that frees a loom\nsquares the next end",
           size=9, fill=RED)
    for k in range(4):
        yy = y4 - 9 + k * 6
        yo = y4 - 15 + k * 10
        s.path(f"M {cx+90} {yy} C {cx+110} {yy}, {cx+115} {yo}, {cx+135} {yo}", stroke="#333", sw=2)
    s.rect(cx + 135, y4 - 20, 16, 40, fill="#fff", stroke=INK)
    s.text(cx + 132, y4 + 32, "XHP", size=9)
    tx, ty = cx + 250, y4 - 55
    s.rect(tx, ty, 150, 110, fill="#f7fbf7", stroke=GREEN, sw=1.5)
    s.text(tx + 8, ty + 18, "test board (ESP32)", size=11, fill=GREEN, weight="bold")
    s.text(tx + 8, ty + 36, "real XH headers\nB4B B5B B6B B7B B9B\nLED per post\nflying lead to hub socket",
           size=10, fill=GREEN)
    s.path(f"M {tx} {ty+95} C {tx-200} {ty+200}, {ox+60} {oy+230}, {ox+30} {oy+70+46}", stroke=GREEN, sw=1.2,
           dash="5,3")
    s.text(ox + 150, oy + 262, "flying lead: plugged only while the reel stands still,\nso it never twists (no "
                               "slip ring until the draw-off is powered)", size=10, fill=GREEN)
    ry = oy + 300
    s.rect(cx + 90, ry, 440, 16, fill="#eee", stroke=GREY)
    s.text(cx + 90, ry - 8, "length rail: pegs at each loom's length from the clamp face (J5 100 ... J11 600 mm)",
           size=10)
    for lab, d in (("J5", 60), ("J9", 150), ("J13", 230), ("J3", 300), ("J11", 420)):
        s.rect(cx + 90 + d, ry - 4, 8, 24, fill=AMBER, stroke=AMBER)
        s.text(cx + 88 + d, ry + 34, lab, size=9, fill=AMBER)
    s.text(cx + 90, ry + 52, "draw the finished housing out to its peg (hold the ribbon behind it), close the clamp, "
                             "cut at the face: +/-1-2 mm", size=10, fill="#555")
    s.rect(cx - 120, y4 + 60, 110, 40, fill="#fff8ee", stroke=AMBER)
    s.text(cx - 116, y4 + 76, "partner nest: a half-\nhoused pair end waits", size=9, fill=AMBER)
    ly = 520
    s.text(40, ly, "The stages. Each is useful the week it is built; each carries the interface the next motor "
                   "takes over.", size=13, weight="bold")
    stages = [
        ("0", "hand work at the spool", "recovery costs reel; pin order,\nopens, shorts before the cut;\npairs equal "
                                        "by the peg;\nthe place to qualify steel", "51"),
        ("1", "powered crimp at the clamp", "1-SN: SN-2549 on its side,\nlift 8.7-14.7 mm; or 1-fin:\np1d's C, lift "
                                            "3.5 mm;\nidentity via the hub; curve", "61"),
        ("2", "motors on the same screws", "posts in loom order\n(revolver or two-tier bar);\ncamera sets depth;\none "
                                           "end alone", "40"),
        ("3", "strip at the clamp", "in the lifted pose with a\ngrounded trim blade, or\np7's whole-end stroke", "33"),
        ("4", "draw-off, cut, gang insert", "puller + encoder, guillotine,\nslip ring, housing tube;\nsingles leave "
                                            "housed", "24"),
        ("5", "split at the clamp", "razor comb or zip station\nfrom p7's slug gap: a reel\nof singles runs alone\n"
                                    "(4P: ~5 h)", "15"),
    ]
    w = 150
    for i, (n, title, body, mins) in enumerate(stages):
        x = 40 + i * (w + 8)
        s.rect(x, ly + 16, w, 180, fill=LIGHT if i % 2 == 0 else "#f6f6f6", stroke=BLUE)
        s.text(x + 8, ly + 38, f"stage {n}", size=12, weight="bold", fill=BLUE)
        s.text(x + 8, ly + 56, title, size=10, weight="bold")
        s.text(x + 8, ly + 76, body, size=9, fill="#333")
        s.text(x + 8, ly + 176, f"person ~{mins} min/unit", size=10, fill=RED)
        if i < len(stages) - 1:
            s.line(x + w, ly + 100, x + w + 8, ly + 100, arrow="k")
    s.text(40, ly + 218, "Person minutes from calc/wave2.out.txt §6, one task library [estimate]; today by the same "
                         "library ~46. Stages 0-1 cost minutes and buy recovery, test and a record;\n"
                         "the minutes fall from stage 2. Grows toward p3 / p3b, p6b (the reel's end docks on a strip), "
                         "change-the-question c5 and ribbon-as-pallet a4.", size=10, fill="#555")
    s.save("p6-spool-end-bench.svg")


def p6b_docks():
    s = Svg(1000, 640, "p6b The reel end docks on a strip (schematic)",
            "Side view of the line (top) and the order of one end (bottom). The equal-path fan keeps the tips "
            "and strip lines on one line after fanning, so every conductor docks at once.")
    y = 190
    s.circle(90, y, 60, fill="#f4f4f4", stroke=GREY)
    s.rect(80, y - 10, 20, 20, fill=GREEN, stroke=GREEN)
    s.text(40, y + 80, "reel, hub socket", size=10)
    s.line(150, y, 230, y, stroke="#333", sw=5)
    s.rect(230, y - 22, 60, 12, fill="#bbb", stroke=INK, rx=6)
    s.rect(230, y + 10, 60, 12, fill="#bbb", stroke=INK, rx=6)
    s.text(222, y - 30, "belt feed", size=9)
    s.line(290, y, 330, y, stroke="#333", sw=5)
    s.rect(330, y - 20, 60, 40, fill=LIGHT, stroke=BLUE)
    s.text(326, y - 28, "clamp on X", size=9, fill=BLUE)
    # fan block with humps
    s.path(f"M 390 {y} C 420 {y-30}, 450 {y-30}, 480 {y}", stroke="#333", sw=3)
    s.path(f"M 390 {y+4} L 480 {y+14}", stroke="#333", sw=3)
    s.text(392, y - 38, "equal-path fan: humps on\nthe inner grooves", size=9)
    # strip + applicator
    s.rect(480, y + 18, 200, 8, fill="#d8b36a", stroke="#b58a2a")
    s.text(480, y + 44, "contact strip on a fixed track", size=9, fill="#8a6a20")
    s.rect(560, y - 90, 70, 60, fill=STEEL, stroke=INK)
    s.text(565, y - 96, "feedless OTP applicator", size=9)
    s.circle(595, y - 120, 16, fill="#fff", stroke=RED, sw=2)
    s.text(620, y - 118, "3-4 mm eccentric,\nNEMA 17 planetary", size=9, fill=RED)
    s.rect(700, y - 10, 30, 30, fill="#fff", stroke=INK)
    s.text(700, y + 36, "wafer nest\n+ load cell", size=9)
    s.rect(760, y + 60, 200, 10, fill="#eee", stroke=GREY)
    s.rect(800, y + 50, 30, 20, fill=PALE_GREEN, stroke=GREEN)
    s.text(760, y + 90, "puller on a rail", size=9, fill=GREEN)
    s.text(40, 340, "One end:", size=12, weight="bold")
    steps = [
        ("1 touch-off", "feed until every copper face touches the grounded stop; each reads through the hub"),
        ("2 strip (p7)", "two razors across the webbed end; toothed pads carry the slug; one backlit frame"),
        ("3 zip (a7)", "tines enter the slug's gaps and tear back to 1 mm short of the clamp face"),
        ("4 fan", "equal-path grooves to 7.1 mm: every tip recedes the same 2.05 mm (4P)"),
        ("5 dock", "drop onto the strip segment: all contacts at once; continuity to the carrier before force"),
        ("6 crimp", "one contact per eccentric turn; pilot in the carrier slot; force curve"),
        ("7 pull, shear", "20 N through each box against a blade comb; shear comb cuts every tab"),
        ("8 insert, test", "closing block, V staircase of fronts; pin to pin through the hub"),
        ("9 draw, cut", "puller draws the loom off; the cut squares the next end"),
    ]
    step_list(s, 40, 370, steps, w_label=110, dy=28, size=10)
    s.save("p6b-reel-end-docks.svg")


# ----------------------------------------------------------------------------------------------
def p7_strip_before_split():
    s = Svg(1000, 700, "p7 Strip before split: one stroke takes the whole end's slug while the web still holds "
                       "the pitch (schematic)",
            "Cross-section at the strip line (left), side section of the stroke (right), and the order. Numbers: "
            "calc/wave2.out.txt §7, calc/wave3.out.txt §5.")
    ox, oy = 60, 230
    R = 26
    for i in range(5):
        cx = ox + R + i * 2 * R
        s.circle(cx, oy, R, fill="#333", stroke="#333")
        s.circle(cx, oy, R * 0.36 / 0.85, fill="#d9a441", stroke="#b58a2a")
    zs = R * 0.56 / 0.85
    s.rect(ox - 20, oy - R - 40, 10 * R + 40, 40 + (R - zs), fill="#cfd8e6", stroke=BLUE, op=0.8)
    s.rect(ox - 20, oy + zs, 10 * R + 40, 40 + (R - zs), fill="#cfd8e6", stroke=BLUE, op=0.8)
    s.text(ox - 20, oy - R - 48, "upper blade across the ribbon, stops at +zs", size=10, fill=BLUE)
    s.text(ox - 20, oy + R + 58, "lower blade, rising through the floor joint, stops at -zs", size=10, fill=BLUE)
    s.line(ox + 10 * R + 30, oy - zs, ox + 10 * R + 30, oy + zs, stroke=RED, arrow="r-end-both")
    s.text(ox + 10 * R + 36, oy + 4, "band left to tear:\n|z| < zs = strand radius\n+ 0.2-0.3 mm", size=10, fill=RED)
    s.text(ox, oy + R + 90, "Straight edges cut every crown at one height, so pitch error does not move\n"
                            "the cut toward any strands.", size=10, fill="#555")
    # side section
    sx, sy = 560, 230
    s.text(sx, 90, "Side section of one conductor", size=12, weight="bold")
    s.rect(sx, sy + 30, 150, 14, fill="#ddd", stroke=GREY)
    s.text(sx, sy + 62, "fixed floor (clamp)", size=9)
    s.rect(sx + 154, sy + 30, 120, 14, fill=PALE_GREEN, stroke=GREEN)
    s.text(sx + 154, sy + 62, "carriage floor (split floor),\ncarrying the lower pad", size=9, fill=GREEN)
    s.rect(sx, sy - 20, 60, 20, fill=LIGHT, stroke=BLUE)
    s.text(sx + 4, sy - 26, "clamp", size=9, fill=BLUE)
    s.rect(sx, sy + 5, 240, 22, fill="#333", stroke="#333")
    s.rect(sx, sy + 12, 240, 8, fill="#d9a441", stroke="#b58a2a")
    s.line(sx + 152, sy - 30, sx + 152, sy + 7, stroke=BLUE, sw=3)
    s.line(sx + 152, sy + 60, sx + 152, sy + 25, stroke=BLUE, sw=3)
    s.text(sx + 110, sy - 40, "blades at the strip line,\n2.4 mm from the cut", size=9, fill=BLUE)
    s.rect(sx + 170, sy - 8, 60, 12, fill=PALE_AMBER, stroke=AMBER)
    s.rect(sx + 170, sy + 28, 60, 0.1, fill=PALE_AMBER, stroke=AMBER)
    s.text(sx + 170, sy - 14, "toothed pads bite the slug", size=9, fill=AMBER)
    s.line(sx + 240, sy + 80, sx + 300, sy + 80, arrow="k", stroke=GREEN, sw=2)
    s.text(sx + 200, sy + 100, "carriage +Y 3-4 mm: blades,\npads and floor push the slug off", size=9, fill=GREEN)
    s.line(sx + 300, sy - 60, sx + 330, sy - 60, arrow="r", stroke=RED)
    s.text(sx + 250, sy - 80, "each blade slices 2-4 mm\nalong its edge as it closes", size=9, fill=RED)
    s.text(sx, sy + 140, "Pads must grip the jacket harder than the jacket grips the strands:\n"
                         "smooth TPU 32-132 N per side on a 5P, grippy 11-44 N, toothed 6-25 N\n[calc wave3 §5]. The "
                         "blades' faces alone would crush the cut caps.", size=10)
    s.text(40, 470, "The order at the clamp", size=12, weight="bold")
    steps = [
        ("1 flush cut", "at the clamp face (at a reel, the previous loom's cut)"),
        ("2 strip, webbed", "pads close, blades slice to their stops, the carriage pushes the whole slug off"),
        ("3 look", "one backlit frame: every bare length and insulation edge on one line"),
        ("4 split", "wedge or razor comb enters the slug's gap; the tear stops at the clamp face"),
        ("5 fan", "by the insulation; fronts recede 0.05-0.31 mm by the fan's shape"),
        ("6 crimp", "any crimp station; the edge was measured in step 3"),
    ]
    step_list(s, 40, 500, steps, w_label=120, dy=30, size=10)
    s.save("p7-strip-before-split.svg")


if __name__ == "__main__":
    p1_crimp_station()
    p1c_lift_once()
    p1d_fin_from_below()
    p2_turret()
    p3_spool()
    p4b_two_heads()
    p5_layout()
    p5_cam_timing()
    p5b_timing()
    p5c_knee()
    p6_spool_bench()
    p6b_docks()
    p7_strip_before_split()
