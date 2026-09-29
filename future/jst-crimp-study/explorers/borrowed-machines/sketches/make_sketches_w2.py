"""The w2-* sketches for the borrowed-machines explorer. Run: python3 make_sketches_w2.py
Every sketch is schematic and not to scale unless a panel says it is drawn to scale from cited
dimensions (w2-b7's cross-sections are)."""
from math import pi, sin, cos, radians, sqrt, acos
from svgkit import (Sketch, INK, MUTED, STEEL, BRONZE, COPPER, SILICONE, PRINTED, BOUGHT, ACCENT, GREEN)

OUT = __file__.rsplit("/", 1)[0] + "/"


def contact(s, x0, yf, k=1.0, crimped=False, open_h=34):
    """XH contact side view: rear (insulation barrel) at x0, box toward +x, floor at yf."""
    s.line(x0, yf, x0 + 170 * k, yf, stroke=BRONZE, sw=3)
    h1 = 22 if crimped else open_h
    h2 = 12 if crimped else 20
    op = 0.9 if crimped else 0.55
    s.rect(x0 + 5 * k, yf - h1 * k, 34 * k, h1 * k, fill=BRONZE, stroke=INK, sw=0.8, opacity=op)
    s.rect(x0 + 62 * k, yf - h2 * k, 34 * k, h2 * k, fill=BRONZE, stroke=INK, sw=0.8, opacity=op)
    s.rect(x0 + 115 * k, yf - 30 * k, 55 * k, 30 * k, fill=BRONZE, stroke=INK, sw=0.8, opacity=0.8)


# ---------------------------------------------------------------------------------------------- b1
def b1_post_feed():
    s = Sketch(1500, 860, "b1  Post-feed on the bought press: the conductor waits above, a ram finger seats it, nothing feeds on the upstroke")
    frames = [("1  before firing: anvil empty, conductor held ~4.6 mm up by the fork", 0),
              ("2  downstroke: post-feed slides the contact in; the ram finger seats the conductor", 1),
              ("3  bottom: crimpers form both barrels; shear cuts the tab", 2),
              ("4  upstroke: finger lifts with the ram; no feed; shuttle withdraws at leisure", 3)]
    for i, (title, st) in enumerate(frames):
        x0 = 10 + (i % 2) * 740
        y0 = 44 + (i // 2) * 330
        s.panel(x0, y0, 730, 320, title)
        yf = y0 + 230                     # barrel floor
        ax = x0 + 360
        # anvil
        s.rect(ax - 10, yf + 2, 150, 60, fill=STEEL)
        s.text(ax, yf + 40, "anvil", size=11)
        # ram with crimpers + finger
        ram_y = {0: y0 + 64, 1: y0 + 95, 2: y0 + 128, 3: y0 + 66}[st]
        s.rect(ax - 40, ram_y - 30, 230, 30, fill=BOUGHT)
        s.text(ax - 30, ram_y - 10, "applicator ram", size=10)
        s.rect(ax + 2, ram_y, 42, 90, fill=STEEL)
        s.rect(ax + 72, ram_y, 40, 102, fill=STEEL)
        # finger (spring loaded, protrudes below)
        fprot = {0: 22, 1: 14, 2: 4, 3: 22}[st]
        s.rect(ax - 34, ram_y, 26, 90 + fprot, fill=PRINTED)
        s.path(f"M{ax-21},{ram_y+8} l6,6 l-12,6 l12,6 l-12,6 l12,6 l-6,6", stroke=INK, sw=0.8)
        if i == 0:
            s.label(ax - 21, ram_y + 60, x0 + 30, y0 + 70, "spring V-finger on the ram (or the")
            s.text(x0 + 30, y0 + 84, "applicator's own wire hold spring)", size=11)
        # contact
        if st in (1, 2, 3):
            cx = ax if st != 1 else ax - 0
            contact(s, cx, yf, k=0.8, crimped=(st >= 2))
        # carrier
        s.rect(ax - 30, yf - 4, 10, 8, fill=BRONZE, stroke=INK, sw=0.6)
        # conductor
        if st == 0:
            s.path(f"M{x0+40},{yf-6} L{ax-60},{yf-6} L{ax+60},{yf-50}", stroke=SILICONE, sw=12)
            s.line(ax + 60, yf - 50, ax + 110, yf - 68, stroke=COPPER, sw=5)
            s.line(ax + 200, yf - 5, ax + 200, yf - 60, sw=1, arrow="both")
            s.text(ax + 206, yf - 30, "~4.6 mm to the conductor centre", size=10)
            s.text(ax + 206, yf - 17, "(wings 3.2+0.25, clearance 0.3)", size=10)
            s.text(ax - 40, yf + 80, "camera first looks at the contact waiting one pitch upstream", size=10)
            s.rect(ax - 110, yf - 30, 16, 40, fill=PRINTED)
            s.label(ax - 102, yf - 10, x0 + 30, yf + 70, "valley-tine fork: holds Y only, slot open downward")
        else:
            s.path(f"M{x0+40},{yf-6} L{ax+30},{yf-10}", stroke=SILICONE, sw=12)
            s.line(ax + 30, yf - 10, ax + 100, yf - 10, stroke=COPPER, sw=5)
            s.rect(ax - 110, yf - 30, 16, 40, fill=PRINTED)
        if st == 1:
            s.line(ax - 60, yf + 75, ax + 20, yf + 75, sw=1.2, arrow="end")
            s.text(ax - 60, yf + 92, "contact arrives on the downstroke (post-feed = 'automatic', WERI manual)", size=10)
        if st == 3:
            s.line(ax - 150, yf + 80, ax - 230, yf + 80, sw=1.4, arrow="end")
            s.text(ax - 330, yf + 97, "shuttle backs off 7-12 mm; a fork drops into the neck behind the box; 20 N pull", size=10)
    s.lines(20, 720, ["Why: on a fast press a pre-feed arrives 50-90 ms after the punch clears, while fork, foot and crimped",
                      "contact are still on the axis. The conductor sets at 24-85 mN of side push; lay-in loads are 8-330 mN",
                      "(250-2000 mN under a presser foot) [calc wave2 s1]. No sprung fork has a window between them. So the",
                      "parts that touch the conductor ride the ram, and the feed runs on the downstroke before they arrive.",
                      "Schematic, not to scale."], size=12)
    s.save(OUT + "w2-b1-post-feed.svg")


# ---------------------------------------------------------------------------------------------- b1c
def b1c_timing():
    s = Sketch(1400, 800, "b1c  One shaft: crank and cams on b1b's crankshaft (schematic timing diagram, 0 deg = top dead centre)")
    X0, X1, Y0 = 250, 1370, 110
    W = X1 - X0

    def xa(a):
        return X0 + W * a / 360.0

    def h_above_bdc(a, r=15.0, l=100.0):
        # crank above the ram: height above BDC, obliquity term added [calc wave3 s0]
        ph = radians(180.0 - a)
        return r * (1 - cos(ph)) + l - sqrt(l * l - (r * sin(ph)) ** 2)
    s.text(20, Y0 + 10, "ram height above BDC", size=12, weight="bold")
    s.text(20, Y0 + 26, "(30 mm stroke, 15 mm crank,", size=10)
    s.text(20, Y0 + 40, "100 mm rod)", size=10)
    pts = [(xa(a), Y0 + 10 + (30.0 - h_above_bdc(a)) * 5.0) for a in range(0, 361, 3)]
    s.poly(pts, closed=False, stroke=INK, sw=2)
    s.text(xa(180) - 30, Y0 + 170, "BDC 180", size=11)
    s.rect(xa(75), Y0 + 5, xa(94) - xa(75), 160, fill=ACCENT, opacity=0.10, stroke="none")
    s.lines(xa(75) + 2, Y0 + 185, ["feed finger", "retracts here", "(75-94 deg)"], size=10, fill=ACCENT)
    s.rect(xa(145), Y0 + 5, xa(185) - xa(145), 160, fill=ACCENT, opacity=0.06, stroke="none")
    s.text(xa(146), Y0 + 20, "crimp", size=11, fill=ACCENT)
    s.rect(xa(220), Y0 + 5, xa(266) - xa(220), 160, fill=GREEN, opacity=0.10, stroke="none")
    s.text(xa(222), Y0 + 20, "dwell window", size=11, fill=GREEN)
    s.rect(xa(266), Y0 + 5, xa(285) - xa(266), 160, fill=BRONZE, opacity=0.18, stroke="none")
    s.text(xa(267), Y0 + 20, "feed", size=11)
    rows = [("gate 0: the waiting contact alone", [(0, 3)], ACCENT),
            ("fork tines down", [(0, 10)], PRINTED),
            ("fork swing, lay in (cam R ~60 mm, 4:1 sector)", [(10, 50)], PRINTED),
            ("foot seats and holds", [(50, 220)], PRINTED),
            ("gate 1: picture + continuity; else back to 0", [(58, 62)], ACCENT),
            ("force logged (HX711 vs AS5600)", [(140, 185)], ACCENT),
            ("sub-slide back (withdraw to the catch)", [(222, 248)], GREEN),
            ("proof pull 20 N via spring + switch", [(248, 262)], GREEN),
            ("reject turn only: puff clears the anvil", [(225, 260)], "#f4a261"),
            ("applicator feed (its own cam)", [(266, 285)], BRONZE),
            ("fork swing back (park in band)", [(280, 340)], PRINTED),
            ("sub-slide forward", [(300, 340)], GREEN),
            ("Y index (stepper, cam switch)", [(340, 360)], BOUGHT)]
    for i, (name, spans, col) in enumerate(rows):
        y = 330 + i * 30
        s.text(20, y + 14, name, size=11)
        s.line(X0, y + 10, X1, y + 10, stroke="#ddd", sw=1)
        for a0, a1 in spans:
            s.rect(xa(a0), y, max(xa(a1) - xa(a0), 3), 20, fill=col, stroke=INK, sw=0.6)
    for a in range(0, 361, 45):
        s.line(xa(a), 310, xa(a), 725, stroke="#ccc", sw=0.6, dash="3,3")
        s.text(xa(a), 740, f"{a}", size=10, anchor="middle")
    s.lines(20, 762, ["Angles from the crank formula [calc wave3 s0-s2]; the feed band is an assumption until the jack test measures it.",
                      "Backing out from gate 1 (60 deg) to 0 crosses no feed motion; the gate sits ~15 deg before the finger's retract band."],
            size=11)
    s.save(OUT + "w2-b1c-timing.svg")


# ---------------------------------------------------------------------------------------------- b2b
def b2b_station():
    s = Sketch(1450, 820, "b2b  The pedal-less hand station (plan, schematic): the person pokes; the machine holds the contact, crimps and keeps the order")
    # plate
    s.rect(60, 120, 1050, 460, fill="#f2f2ee", stroke=MUTED)
    s.text(70, 140, "base plate ~350 x 220 mm (drawn larger)", size=11, fill=MUTED)
    # LED strip
    s.rect(300, 80, 360, 26, fill=BOUGHT)
    for i in range(5):
        s.circle(340 + i * 70, 93, 8, fill=(ACCENT if i == 2 else "#eee"))
    s.text(670, 98, "LED ribbon map: conductor k lit", size=11)
    # strip nozzle
    s.panel(90, 170, 260, 250, "A  strip nozzle (b7)")
    s.rect(130, 230, 180, 120, fill=BOUGHT)
    s.poly([(130, 290), (160, 270), (160, 310)], fill=PRINTED)
    s.rect(240, 255, 8, 70, fill=STEEL)
    s.rect(270, 255, 8, 70, fill=STEEL)
    s.text(140, 375, "die-hole blades, tip-stop electrode,", size=10)
    s.text(140, 389, "V-clamp, twist on the 3 mm pull", size=10)
    # crimp station
    s.panel(380, 170, 380, 360, "B  crimp station (b2)")
    s.rect(430, 240, 260, 60, fill=BOUGHT)
    s.text(600, 275, "SN-2549 on edge", size=10)
    s.text(600, 289, "(jaws across the wire)", size=10)
    s.rect(560, 205, 22, 130, fill=STEEL)
    s.text(590, 220, "dies", size=10)
    s.rect(430, 340, 300, 18, fill=PRINTED)
    s.text(440, 375, "contact supply in front: pawl + steel-edge shear + post head,", size=10)
    s.text(440, 389, "or a pocket plate + post head (one contact type throughout)", size=10)
    s.rect(530, 300, 60, 20, fill=PRINTED)
    s.text(470, 318, "funnel", size=10)
    s.rect(470, 395, 60, 30, fill=PRINTED)
    s.rect(535, 395, 60, 30, fill=PRINTED)
    s.text(470, 440, "soft clamp (TPU V-jaws)", size=10)
    s.rect(650, 395, 90, 60, fill=BOUGHT)
    s.text(655, 470, "actuator via spring", size=10)
    s.text(655, 484, "link (+ AS5600)", size=10)
    s.text(420, 510, "flap blade in the neck = electrode", size=10)
    # header nest
    s.panel(790, 170, 300, 300, "C  insertion nest (i5)")
    s.rect(830, 240, 220, 60, fill=GREEN, opacity=0.4)
    for i in range(4):
        s.rect(850 + i * 45, 250, 30, 40, fill=("#ffd966" if i == 2 else "#fff"), stroke=INK, sw=0.8)
    s.text(830, 320, "XH header PCB on a load cell; lit cavity;", size=10)
    s.text(830, 334, "lever seats; post continuity names cavity", size=10)
    # far end pogo
    s.rect(1150, 360, 200, 80, fill=PRINTED)
    s.text(1160, 385, "far end: pogo block on", size=11)
    s.text(1160, 400, "the raw cut face", size=11)
    for i in range(4):
        s.circle(1190 + i * 30, 420, 6, fill=STEEL)
    s.line(1150, 440, 1110, 540, stroke=MUTED, sw=1, dash="4,3")
    s.text(1115, 560, "every conductor wired to the ESP32", size=11)
    # loom
    s.path("M1150,400 C1000,640 700,640 560,560", stroke=SILICONE, sw=8)
    # person steps
    s.lines(60, 620, ["Per conductor k:  1 poke into A (tip-stop names k; wrong one = red light)  ->  strip + twist ~4 s",
                      "2 poke into B's funnel until strands touch the flap blade (k lights again = at depth)  ->  soft clamp takes it; let go",
                      "3 crimp through the spring link; jaws open; 20 N pull against the flap; continuity through the crimp",
                      "4 lift the crimp out of the open mouth; insert into the lit cavity at C while B feeds, shears and places contact k+1",
                      "~37 attended min/unit vs 46 today (procedure's task library) [calc wave2 s5]. Schematic, not to scale."], size=12)
    s.save(OUT + "w2-b2b-station.svg")


# ---------------------------------------------------------------------------------------------- b6
def b6_pierce():
    s = Sketch(1500, 900, "b6  Pierce at the root, pull toward the tip (schematic; the sewing machine's needle and needle plate, borrowed)")
    s.panel(10, 44, 900, 480, "Side section along one web (not to scale)")
    s.panel(920, 44, 570, 480, "End view at the needle (not to scale)")
    # side
    yb = 330
    s.rect(60, yb + 30, 820, 30, fill=STEEL)
    s.text(70, yb + 50, "needle plate (stencil steel strips)", size=11)
    s.rect(60, yb - 70, 820, 16, fill=STEEL, opacity=0.6)
    s.text(70, yb - 76, "top guide", size=11)
    s.rect(60, yb - 40, 180, 70, fill=PRINTED)
    s.text(70, yb - 10, "cassette clamp", size=11)
    s.rect(240, yb - 20, 600, 40, fill=SILICONE, stroke=SILICONE)
    s.line(240, yb, 840, yb, stroke="#777", sw=1, dash="5,4")
    s.text(600, yb + 5, "", size=10)
    # needle at root at stage start
    s.rect(262, yb - 140, 8, 190, fill=STEEL)
    s.poly([(262, yb + 50), (270, yb + 50), (266, yb + 62)], fill=STEEL)
    s.text(280, yb - 120, "needle (0.6 mm, floats +/-0.4 mm in Y)", size=11)
    s.text(280, yb - 104, "pierces at the root = clamp edge", size=11)
    # ghost needle at strip line
    s.rect(780, yb - 140, 8, 190, fill=STEEL, opacity=0.35)
    s.text(640, yb - 150, "stops here: the strip line, Ls from the tip (per reel)", size=11)
    s.line(270, yb - 30, 770, yb - 30, sw=1.4, arrow="end")
    s.text(430, yb - 36, "needle travels toward the tip relative to the ribbon", size=11)
    s.line(700, yb + 110, 450, yb + 110, sw=1.6, arrow="end")
    s.text(450, yb + 130, "the shuttle draws the cassette back: ribbon in TENSION", size=12, weight="bold")
    s.rect(800, yb - 20, 40, 40, fill=SILICONE, opacity=0.5, stroke=ACCENT, dash="3,2")
    s.text(795, yb + 90, "tip stays webbed", size=11, fill=ACCENT)
    s.lines(40, 480, ["The tear runs only ahead of the needle, toward the tip; it cannot run back past the pierce.",
                      "Round needle tears the neck, 3-15 N per web; an edge (scalpel point / seam-ripper crotch) cuts it, 0.2-3 N."], size=11)
    # end view
    cx, cy = 1200, 300
    for i in range(-1, 2):
        s.circle(cx + i * 110, cy, 55, fill=SILICONE)
        s.circle(cx + i * 110, cy, 23, fill=COPPER)
    s.rect(cx + 55 - 6, cy - 150, 12, 230, fill=STEEL)
    s.poly([(cx + 49, cy + 80), (cx + 61, cy + 80), (cx + 55, cy + 95)], fill=STEEL)
    s.rect(960, cy + 100, 500, 20, fill=STEEL)
    s.text(970, cy + 140, "needle plate: slot tight in X, long in Y (float)", size=11)
    s.label(cx + 55, cy - 50, 1010, 130, "the cone slides down the steep valley into the neck")
    s.text(940, 470, "copper edges sit +/-0.48 mm from each seam; seams are within +/-0.15 mm", size=11)
    s.text(940, 486, "of nominal on a 5P from a centred datum [calc wave2 s2]", size=11)
    # comparison strip
    s.panel(10, 540, 1480, 340, "Why this direction (numbers in calc wave2 s2)")
    rows = [("", "pierce at root, pull to tip (b6)", "enter at tip, push to root (a7, a7b, a harp)"),
            ("ribbon between clamp and tool", "tension", "compression: a 5P buckles at ~6-56 N over 15-5 mm free"),
            ("what sets the root", "the pierce, +/-0.05 mm", "a tear stop: a wedge drives the tear 0.6-2 mm ahead; the clamp stops it"),
            ("where the root can be", "anywhere the needle reaches", "at a clamp face"),
            ("the tip", "can stay webbed for a one-piece slug", "split first"),
            ("spool line (b8)", "the belt feed's retraction is the pull", "needs the clamp closed at the root first")]
    for i, (a, b, c) in enumerate(rows):
        y = 590 + i * 44
        s.text(30, y, a, size=12, weight="bold" if i == 0 else "normal")
        s.text(420, y, b, size=12, weight="bold" if i == 0 else "normal")
        s.text(860, y, c, size=12, weight="bold" if i == 0 else "normal")
    s.save(OUT + "w2-b6-pierce-and-pull.svg")


# ---------------------------------------------------------------------------------------------- b7
def b7_geometry():
    s = Sketch(1500, 700, "b7  Three borrowed blade geometries on one conductor, drawn to scale from cited dimensions (x120)")
    K = 120.0   # px per mm
    RO, RB, ECC = 0.85, 0.36, 0.06
    panels = [("Two 90 deg V-blades, ri = 0.45 mm", "v"), ("Two die-hole blades, hole 0.94 mm", "d"),
              ("One orbiting blade r = 0.50 mm, conductor 0.10 mm off the axis", "r")]
    for i, (t, kind) in enumerate(panels):
        x0 = 10 + i * 495
        s.panel(x0, 44, 485, 560, t)
        cx, cy = x0 + 242, 320
        # jacket and (offset) bundle
        s.circle(cx, cy, RO * K, fill=SILICONE, opacity=0.85)
        off = ECC * K
        bx = cx + (off if kind != "r" else 0)
        s.circle(bx, cy, RB * K, fill=COPPER)
        if kind == "v":
            ri = 0.45
            a = ri * sqrt(2) * K
            s.poly([(cx, cy - a), (cx + a, cy), (cx, cy + a), (cx - a, cy)], stroke=ACCENT, sw=2.5, fill="none")
            s.text(x0 + 20, 540, "cut reaches ri at 4 points (+0.02 mm to strands, worst)", size=11)
            s.text(x0 + 20, 556, "and only ri*sqrt2 at 4 others (0.35 mm of wall left)", size=11)
            s.text(x0 + 20, 572, "-> uneven ring; tear wanders; flags or nicks", size=11, fill=ACCENT)
        elif kind == "d":
            rd = 0.47
            s.circle(cx, cy, rd * K, stroke=ACCENT, sw=2.5)
            s.text(x0 + 20, 540, "even ring, 0.04-0.19 mm, set by the bundle's offset", size=11)
            s.text(x0 + 20, 556, "tear-off 1.1-2.9 N; the jacket centres itself", size=11)
            s.text(x0 + 20, 572, "-> the static geometry that suits this wire", size=11, fill=GREEN)
        else:
            rbl = 0.50
            s.circle(cx + 0.10 * K, cy, rbl * K, stroke=ACCENT, sw=2.5, dash="6,4")
            s.circle(cx + 0.10 * K, cy, 3, fill=ACCENT, stroke=ACCENT)
            s.text(x0 + 20, 540, "blade circle centred on the guide axis, not the jacket", size=11)
            s.text(x0 + 20, 556, "+/-0.05 mm centring: -0.01..+0.02 mm worst; +/-0.10: nicks", size=11)
            s.text(x0 + 20, 572, "-> needs centralizers (RotaryStrip) or closing blades (a8b)", size=11, fill=ACCENT)
        s.text(x0 + 20, 90, "jacket 1.7 mm, bundle 0.72 mm, bundle offset 0.06 mm [facts]", size=11)
    s.text(20, 640, "Scale: 120 px per mm. Rigid-jacket geometry; the soft jacket squeezes into V-blades, which makes the V case worse. [calc wave2 s3]", size=12)
    s.save(OUT + "w2-b7-strip-geometry.svg")


# ---------------------------------------------------------------------------------------------- b8
def b8_line():
    s = Sketch(1500, 860, "b8  The spool-fed borrowed line, making T4 ends (elevation, schematic, not to scale)")
    yl = 380
    # spool
    s.circle(120, yl - 40, 90, fill=BOUGHT)
    s.circle(120, yl - 40, 20, fill=STEEL)
    s.text(40, yl + 80, "4P spool; inner end on a", size=11)
    s.text(40, yl + 95, "6-circuit slip ring = test lead", size=11)
    s.path(f"M210,{yl-40} C260,{yl+60} 300,{yl+60} 340,{yl}", stroke=SILICONE, sw=6)
    s.text(250, yl + 70, "slack loop", size=10)
    # feed head on XY stage
    s.rect(330, yl + 40, 520, 30, fill=BOUGHT)
    s.text(340, yl + 60, "X/Y stage (MGN12, NEMA 17): the feed head moves; the applicator stays", size=11)
    s.rect(345, yl - 30, 80, 20, fill=BOUGHT)
    s.rect(345, yl + 10, 80, 20, fill=BOUGHT)
    s.text(345, yl - 38, "belt feed + encoder", size=10)
    s.rect(450, yl - 45, 14, 80, fill=STEEL)
    s.text(430, yl - 52, "guillotine", size=10)
    s.rect(490, yl - 30, 110, 22, fill=PRINTED)
    s.rect(490, yl + 8, 110, 22, fill=PRINTED)
    s.text(495, yl - 38, "work clamp", size=10)
    s.line(600, yl - 120, 600, yl + 120, stroke=ACCENT, dash="5,4")
    s.text(560, yl - 125, "clamp face = root", size=10, fill=ACCENT)
    # ribbon
    s.rect(340, yl - 8, 400, 16, fill=SILICONE, stroke=SILICONE)
    # needle bar
    s.rect(680, yl - 110, 10, 150, fill=STEEL)
    s.text(695, yl - 100, "needle bar, 12 mm ahead of the clamp face", size=10)
    s.rect(640, yl + 14, 90, 10, fill=STEEL)
    s.line(740, yl + 100, 640, yl + 100, sw=1.4, arrow="end")
    s.text(600, yl + 118, "belts retract 12 mm: the needles rip root -> strip line", size=11)
    # strip station
    s.rect(730, yl - 60, 8, 45, fill=STEEL)
    s.rect(730, yl + 15, 8, 45, fill=STEEL)
    s.text(700, yl - 70, "crown blades + pinch pads", size=10)
    # applicator
    s.rect(960, yl - 210, 260, 200, fill=BOUGHT, opacity=0.6)
    s.text(970, yl - 190, "OTP applicator in b1b's slow crank", size=11)
    s.text(970, yl - 175, "(shop press; pre-feed; gate; dwell)", size=11)
    s.rect(1000, yl - 10, 180, 40, fill=STEEL)
    s.text(1010, yl + 15, "anvil", size=10)
    s.rect(900, yl - 50, 16, 60, fill=PRINTED)
    s.text(860, yl - 60, "valley-tine fork", size=10)
    # insertion + drop tube
    s.rect(1240, yl - 40, 100, 60, fill=GREEN, opacity=0.35)
    s.text(1240, yl - 50, "converging comb + XHP-4 nest", size=10)
    s.rect(1360, yl + 40, 40, 300, fill="none", stroke=MUTED, dash="5,4")
    s.text(1300, yl + 360, "drop tube (~0.7 m)", size=11)
    # steps
    s.lines(40, 560, ["1 feed out 12 mm + Ls past the needles (Ls = the reel's strip length)  |  2 pierce every web  |  3 belts retract 12 mm: rip to the strip line; root lands on the clamp face",
                      "4 clamp  |  5 score crowns to 50-60 % (or a shoe), pinch the still-webbed tip, back off 3 mm: one comb-shaped slug  |  6 fold the four conductors back as one band",
                      "7 per conductor: look at the waiting contact alone; fork lays conductor k in; gate = picture + continuity through the spool; crank; dwell: withdraw, neck fork, 20 N pull",
                      "8 comb runs root to tip twice (takes out the fold's set), then converges to 2.5 mm; housing pushed onto all four  |  9 test through the spool  |  10 feed out, cut",
                      "", "Rip 9-45 N for a 4P against 32-180 N of belt traction [calc wave2 s4]; strip pull 19-52 N for four [calc wave3 s8]. ~6-7 min per T4 end; ~300 ends over the program [c5].",
                      "Sources: p3 / a4 (spool, cut last, test through spool), c5 (T4 first), b1b (applicator), b6 (pierce and pull), b1 (band, fork), i3/a6 (gang insert). Flat branch: b8b."],
            size=12)
    s.save(OUT + "w2-b8-spool-line.svg")


if __name__ == "__main__":
    b1_post_feed()
    b1c_timing()
    b2b_station()
    b6_pierce()
    b7_geometry()
    b8_line()
    print("wrote 6 wave-2 sketches")
