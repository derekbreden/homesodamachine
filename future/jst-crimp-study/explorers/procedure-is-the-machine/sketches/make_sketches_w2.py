"""Earlier drawing functions for p6, p1c, p4b, p5b and p7.

Their current forms are drawn by make_sketches_w3.py; running this script writes nothing.

All drawings are schematic: shapes show order, references and what moves, not scale, unless a
caption says a number came from calc/wave2.out.txt.
"""

import math

from make_sketches import Svg, BLUE, RED, GREEN, GREY, LIGHT, AMBER, INK


def p6_spool_bench():
    s = Svg(1000, 820, "p6 The spool-end bench that grows (schematic, plan view of stage 0)",
            "Today's hand procedure moved to the spool: the XH end is made and tested before the loom exists; "
            "the cut that frees it squares the next end.")
    # reel stand
    ox, oy = 40, 120
    for i, lab in enumerate(("5P", "4P", "3P")):
        y = oy + i * 70
        s.rect(ox, y, 110, 52, fill="#f4f4f4", stroke=GREY)
        s.circle(ox + 30, y + 26, 20, fill="#fff", stroke=INK)
        s.circle(ox + 30, y + 26, 6, fill=AMBER, stroke=AMBER)
        s.text(ox + 58, y + 22, f"{lab} reel", size=11)
        s.text(ox + 58, y + 37, "hub socket", size=9, fill=AMBER)
    s.text(ox, oy - 30, "reels: rewound once per spool onto an 80 mm hub radius,\n"
                        "inner end crimped into an XH socket in the hub", size=10, fill="#555")
    # ribbon path from 4P reel through straightener to clamp
    y4 = oy + 70 + 26
    s.line(ox + 110, y4, ox + 190, y4, stroke="#333", sw=5)
    s.rect(ox + 190, y4 - 22, 70, 44, fill=LIGHT, stroke=BLUE)
    for k in range(4):
        s.circle(ox + 200 + k * 16, y4 + (-9 if k % 2 == 0 else 9), 6, fill="#fff", stroke=BLUE)
    s.text(ox + 190, y4 + 38, "roller straightener\n(reverse bends)", size=9, fill=BLUE)
    s.line(ox + 260, y4, ox + 360, y4, stroke="#333", sw=5)
    # clamp at bench edge
    cx = ox + 360
    s.rect(cx, y4 - 30, 90, 60, fill=LIGHT, stroke=BLUE, sw=1.6)
    s.text(cx - 20, y4 - 62, "channel clamp (0.2 mm under width,\nmarked edge on the wall, cam lever)", size=9,
           fill=BLUE)
    s.line(cx + 90, y4 - 40, cx + 90, y4 + 40, stroke=RED, sw=3)
    s.text(cx + 60, y4 + 58, "cut guide at the clamp face:\nthe cut that frees a loom\nsquares the next end",
           size=9, fill=RED)
    # split, fanned end with housing
    for k in range(4):
        yy = y4 - 9 + k * 6
        yo = y4 - 15 + k * 10
        s.path(f"M {cx+90} {yy} C {cx+110} {yy}, {cx+115} {yo}, {cx+135} {yo}", stroke="#333", sw=2)
    s.rect(cx + 135, y4 - 20, 16, 40, fill="#fff", stroke=INK)
    s.text(cx + 132, y4 + 32, "XHP", size=9)
    # test board
    tx, ty = cx + 250, y4 - 55
    s.rect(tx, ty, 150, 110, fill="#f7fbf7", stroke=GREEN, sw=1.5)
    s.text(tx + 8, ty + 18, "test board (ESP32)", size=11, fill=GREEN, weight="bold")
    s.text(tx + 8, ty + 36, "real XH headers\nB4B B5B B6B B7B B9B\nLED per post\nflying lead to hub socket",
           size=10, fill=GREEN)
    s.path(f"M {tx} {ty+95} C {tx-200} {ty+200}, {ox+60} {oy+230}, {ox+30} {oy+70+46}", stroke=GREEN, sw=1.2,
           dash="5,3")
    s.text(ox + 150, oy + 262, "flying lead: plugged only while the reel stands still,\nso it never twists (no "
                               "slip ring until the draw-off is powered)", size=10, fill=GREEN)
    # length rail with pegs
    ry = oy + 300
    s.rect(cx + 90, ry, 440, 16, fill="#eee", stroke=GREY)
    s.text(cx + 90, ry - 8, "length rail: pegs at each loom's length from the clamp face (J5 100 ... J11 600 mm)",
           size=10)
    for i, (lab, d) in enumerate((("J5", 60), ("J9", 150), ("J13", 230), ("J3", 300), ("J11", 420))):
        s.rect(cx + 90 + d, ry - 4, 8, 24, fill=AMBER, stroke=AMBER)
        s.text(cx + 88 + d, ry + 34, lab, size=9, fill=AMBER)
    s.text(cx + 90, ry + 52, "draw the finished housing out to its peg, close the clamp, cut at the face: "
                             "+/-1-2 mm [estimate]", size=10, fill="#555")
    # partner nest
    s.rect(cx - 120, y4 + 60, 110, 40, fill="#fff8ee", stroke=AMBER)
    s.text(cx - 116, y4 + 76, "partner nest: a half-\nhoused pair end waits", size=9, fill=AMBER)

    # stage ladder
    ly = 520
    s.text(40, ly, "The stages. Each is useful the week it is built; each carries the interface the next motor "
                   "takes over.", size=13, weight="bold")
    stages = [
        ("0", "hand work at the spool", "recovery costs spool; pin order,\nopens, shorts before the cut;\npairs equal by the peg",
         "51"),
        ("1", "powered crimp at the clamp", "SN-2549 squeezer tip-down on a\nknob-turned slide; identity by\nhub lead at every crimp; curve", "61"),
        ("2", "motors on the same screws", "post column in loom order;\nthe machine walks the row;\none end alone", "40"),
        ("3", "strip at the clamp", "in the lifted pose (Klein\nsqueezer, spindle) or p7's\nwhole-end stroke", "33"),
        ("4", "draw-off, cut, gang insert", "belt feed + encoder, guillotine,\nslip ring, housing tube;\nsingles leave housed", "24"),
        ("5", "split at the clamp", "razor comb or zip station:\na spool of singles runs alone\n(4P: ~5 h)", "15"),
    ]
    w = 150
    for i, (n, title, body, mins) in enumerate(stages):
        x = 40 + i * (w + 8)
        s.rect(x, ly + 16, w, 170, fill=LIGHT if i % 2 == 0 else "#f6f6f6", stroke=BLUE)
        s.text(x + 8, ly + 38, f"stage {n}", size=12, weight="bold", fill=BLUE)
        s.text(x + 8, ly + 56, title, size=10, weight="bold")
        s.text(x + 8, ly + 76, body, size=9, fill="#333")
        s.text(x + 8, ly + 160, f"person ~{mins} min/unit", size=10, fill=RED)
        if i < len(stages) - 1:
            s.line(x + w, ly + 100, x + w + 8, ly + 100, arrow="k")
    s.text(40, ly + 208, "Person minutes from calc/wave2.out.txt §6, one task library [estimate]; today by the same "
                         "library ~46. Stages 0-1 cost minutes and buy recovery, test and a record;\n"
                         "the minutes fall from stage 2. Grows toward p3 / p3b, the C1 combination (p3 x "
                         "hand-tool-as-press a3), change-the-question c5 and ribbon-as-pallet a4.",
           size=10, fill="#555")
    s.save("p6-spool-end-bench.svg")


def p1c_lift_once():
    s = Svg(980, 620, "p1c Lift once: every act on conductor k in one pose (schematic, end view and sequence)",
            "Neighbours stay in the row and are never touched; k is lifted once, trimmed, stripped, measured, "
            "crimped and pulled there, then laid back and squared.")
    # end view: row of conductors
    ox, oy = 60, 360
    s.text(ox, 80, "End view along the wire axis (looking from the tool toward the cassette)", size=12,
           weight="bold")
    pitch = 28
    for i in range(7):
        x = ox + 60 + i * pitch
        if i == 3:
            continue
        s.circle(x, oy, 9, fill="#333", stroke="#333")
    kx = ox + 60 + 3 * pitch
    h = 90
    s.circle(kx, oy - h, 9, fill="#333", stroke="#333")
    # lifter
    s.path(f"M {kx-8} {oy+30} L {kx-8} {oy-h+12} L {kx+8} {oy-h+12} L {kx+8} {oy+30}", stroke=GREEN, sw=2)
    s.text(kx + 12, oy + 28, "lifter finger (from below,\nstationary at the station line)", size=9, fill=GREEN)
    # tip-down jaw: two jaw pieces either side of k, nest at k, tip t below k's axis
    jw = 70
    tpx = 30
    top = oy - h - 150
    s.rect(kx - jw, top, jw - 10, 150 + tpx, fill="#dde", stroke=INK)
    s.rect(kx + 10, top, jw - 10, 150 + tpx, fill="#dde", stroke=INK)
    s.text(kx - jw, top - 8, "SN-2549 hung tip-down: jaws close across the row", size=10)
    s.text(kx + jw + 4, oy - h - 30, "k, lifted h, in the nest\n(the lifter acts a few mm\nbehind the tool, in Y)", size=9)
    s.line(kx - jw - 10, oy - h, kx - jw - 10, oy - h + tpx, stroke=RED, arrow="r-end-both")
    s.text(kx - jw - 100, oy - h + 2, "t: nest to\njaw tip, 2-6 mm\n(unmeasured)", size=9, fill=RED)
    s.line(kx + jw + 30, oy, kx + jw + 30, oy - h, stroke=BLUE, arrow="b-end-both")
    s.text(kx + jw + 36, oy - h / 2, "h = t + 1.85 mm\n= 3.9-7.9 mm", size=10, fill=BLUE)
    s.line(ox + 40, oy - 12, ox + 60 + 6 * pitch + 20, oy - 12, stroke=GREY, dash="4,3")
    s.text(ox + 40, oy + 60, "neighbours pass under the jaw tip; nothing presses them\n(wave-1 presser left "
                             "1-5 mm of set in every waiting conductor)", size=10, fill="#555")
    # sequence
    sx, sy = 520, 90
    s.text(sx, sy, "One conductor, in one pose", size=12, weight="bold")
    steps = [
        ("index", "cassette (or spool clamp) steps key k to the station line"),
        ("lift", "finger raises k by h; k's own set from here never matters to k"),
        ("trim", "blade on the tool carriage squares k's tip in the pose"),
        ("strip", "V-jaws or a spindle on the same carriage, 2.4 mm"),
        ("measure", "ELP on a backlit tip: bare length -> Y offset"),
        ("contact", "tool picks one off the post column (or revolver)"),
        ("hold", "first ratchet tooth: contact captive, barrels open"),
        ("feed", "tool Y slides the contact onto k to the corrected depth;\nfar-end electrode reads k"),
        ("crimp", "pusher completes the ratchet; force curve logged"),
        ("pull", "blade in the neck, jaws open, 20 N through the box"),
        ("rise", "tool lifts off through the tip-down mouth"),
        ("lay back", "finger lowers k; a presser squares the crimp into the row"),
    ]
    for i, (a, b) in enumerate(steps):
        y = sy + 24 + i * 38
        s.rect(sx, y - 14, 80, 24, fill=LIGHT, stroke=BLUE)
        s.text(sx + 6, y + 2, a, size=10, weight="bold", fill=BLUE)
        s.text(sx + 90, y + 2, b, size=10)
    s.text(sx, sy + 24 + 12 * 38 + 6, "Axial chain: +/-0.07-0.09 mm RSS with the camera correction "
                                    "[calc wave2 §3]", size=10, fill=RED)
    s.save("p1c-lift-once.svg")


def p4b_two_heads():
    s = Svg(980, 360, "p4b Two heads, one person: the person's pace sets the rhythm (schematic timeline)",
            "Head cycle 26 s [estimate]; person presents 5 s and inserts 8 s. Numbers: calc/wave2.out.txt §4.")
    x0, y0 = 150, 90
    scale = 7.2  # px per second
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
        # present
        s.rect(x0 + start * scale, y0 + 8, 5 * scale, 22, fill="#f7dede", stroke=RED)
        s.text(x0 + start * scale + 2, y0 + 23, f"p{k}", size=9, fill=RED)
        row = 1 if head == "A" else 2
        s.rect(x0 + (start + 5) * scale, y0 + row * 60 + 8, 26 * scale, 22,
               fill=LIGHT if head == "A" else "#e6f3ea", stroke=BLUE if head == "A" else GREEN)
        s.text(x0 + (start + 5) * scale + 4, y0 + row * 60 + 23,
               f"conductor {k}: strip, drop contact, hold, feed, crimp, pull", size=9)
        head_free[head] = start + 5 + 26
        # insert the previous crimp from the other head, if ready
        if k >= 3:
            s.rect(x0 + (start + 5) * scale, y0 + 8, 8 * scale, 22, fill="#fbeede", stroke=AMBER)
            s.text(x0 + (start + 5) * scale + 2, y0 + 23, f"ins {k-2}", size=9, fill=AMBER)
        t = start + 13
        k += 1
    s.text(30, y0 + 200, "p = present conductor k to a head's funnel (tip to the beam); ins = insert a finished "
                         "contact into its lit cavity.\nWith one head the person waits whenever the cycle is longer "
                         "than present + insert; with two, a 26 s cycle (the head is also busy while k is presented)\nleaves ~2-3 s of waiting per conductor after the start-up.",
           size=10, fill="#555")
    s.save("p4b-two-heads.svg")


def p5b_timing():
    s = Svg(980, 540, "p5b One turn per conductor: the camshaft squeezes the SN-2549 (schematic timing)",
            "One NEMA 17 through a self-locking worm; the squeeze lobe sets the motor (2.1-3.2 N*m) "
            "[calc wave2 §5].")
    x0, y0, W = 200, 80, 720
    s.line(x0, y0, x0 + W, y0, stroke=INK)
    for d in range(0, 361, 30):
        x = x0 + W * d / 360
        s.line(x, y0 - 4, x, y0 + 4)
        s.text(x - 8, y0 - 8, f"{d}", size=9)
    rows = [
        ("index cassette", 0, 20, GREY),
        ("lift key k", 20, 50, GREEN),
        ("revolver drops a contact", 40, 70, AMBER),
        ("squeeze lobe: approach + hold click", 70, 110, BLUE),
        ("Y cam: carry k into the barrels", 110, 160, GREEN),
        ("flap blade drops into the neck", 150, 170, AMBER),
        ("squeeze lobe: crimp (last 8 mm of grip)", 170, 230, RED),
        ("ratchet releases, lobe falls", 230, 255, BLUE),
        ("Y cam back 0.5 mm against a 20 N spring", 255, 285, GREEN),
        ("flap lifts, jaws open fully", 285, 300, AMBER),
        ("lift lowers k; presser squares it", 300, 335, GREEN),
        ("camera frame, switch cam", 335, 360, GREY),
    ]
    for i, (lab, a, b, col) in enumerate(rows):
        y = y0 + 24 + i * 28
        s.text(20, y + 12, lab, size=10)
        s.rect(x0 + W * a / 360, y, W * (b - a) / 360, 16, fill=col, stroke=col, op=0.35)
    s.text(20, y0 + 24 + len(rows) * 28 + 20,
           "Strip and trim happen before the camshaft (bench A, or p7's whole-end stroke). A skip bump on the cassette "
           "rack holds the revolver\npawl and the squeeze follower off for J2's key 3; the end bump stops the shaft. "
           "The far-end electrode can stop the shaft through the switch cam\nwhen k reads as the wrong conductor.",
           size=10, fill="#555")
    s.save("p5b-cam-timing.svg")


def p7_strip_before_split():
    s = Svg(980, 560, "p7 Strip before split: one stroke takes the whole end's slug while the web still holds "
                      "the pitch (schematic)",
            "Cross-section at the strip line (left) and plan view of the order (right). Numbers: "
            "calc/wave2.out.txt §7.")
    # cross-section
    ox, oy = 60, 230
    R = 28
    for i in range(5):
        cx = ox + R + i * 2 * R
        s.circle(cx, oy, R, fill="#333", stroke="#333")
        s.circle(cx, oy, R * 0.36 / 0.85, fill="#d9a441", stroke="#b58a2a")
    zs = R * 0.56 / 0.85
    s.rect(ox - 20, oy - R - 40, 10 * R + 40, 40 + (R - zs), fill="#cfd8e6", stroke=BLUE, op=0.8)
    s.rect(ox - 20, oy + zs, 10 * R + 40, 40 + (R - zs), fill="#cfd8e6", stroke=BLUE, op=0.8)
    s.text(ox - 20, oy - R - 48, "upper blade (straight edge across the ribbon), stops at +zs", size=10, fill=BLUE)
    s.text(ox - 20, oy + R + 58, "lower blade, stops at -zs against the same steel stop", size=10, fill=BLUE)
    s.line(ox + 10 * R + 40, oy - zs, ox + 10 * R + 40, oy + zs, stroke=RED, arrow="r-end-both")
    s.text(ox + 10 * R + 46, oy + 4, "band left to tear:\n|z| < zs = strand radius\n+ 0.2-0.3 mm ligament",
           size=10, fill=RED)
    s.text(ox, oy + R + 90, "Straight edges cut every crown at one height, so conductor pitch error does not\n"
                            "move the cut toward any strands; scalloped cutters would need their notches on\n"
                            "each conductor to within the ligament.", size=10, fill="#555")
    # plan view order
    px, py = 560, 90
    s.text(px, py, "The order at the clamp", size=12, weight="bold")
    steps = [
        ("1 flush cut", "at the clamp face (the previous loom's cut, at a spool)"),
        ("2 strip, webbed", "blades close 2.4 mm from the cut; the carriage pulls\nthe whole slug (web included) "
                            "~20-75 N for 3P-5P"),
        ("3 look", "one backlit frame: every bare length and every\ninsulation edge on one line"),
        ("4 split", "wedge or razor comb enters from the open gap the slug\nleft (no nick needed); tear "
                    "stops at the clamp face"),
        ("5 fan", "comb takes the conductors to 2.5 mm by their insulation"),
        ("6 crimp", "any crimp station; the edge was measured in step 3"),
    ]
    for i, (a, b) in enumerate(steps):
        y = py + 30 + i * 62
        s.rect(px, y - 14, 120, 26, fill=LIGHT, stroke=BLUE)
        s.text(px + 6, y + 3, a, size=10, weight="bold", fill=BLUE)
        s.text(px + 130, y, b, size=10)
    s.save("p7-strip-before-split.svg")


if __name__ == "__main__":
    print("make_sketches_w3.py draws these sketches; nothing written here.")
