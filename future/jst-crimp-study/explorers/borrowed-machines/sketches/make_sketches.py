"""Schematic sketches for the borrowed-machines explorer. Run: python3 make_sketches.py
Writes b1-press-shuttle, b1b-crank-press, b2-hand-crimper-frame, b3-gantry-head, b4-laser-score,
b4b-diode-station, b5-arm-stations and b8b-flat-spool-line. The w2-* sketches come from
make_sketches_w2.py. Every sketch is schematic and not to scale unless a panel says otherwise."""
from math import pi, sin, cos, radians, sqrt, atan2, degrees
from svgkit import (Sketch, INK, MUTED, STEEL, BRONZE, COPPER, SILICONE, PRINTED, BOUGHT, ACCENT, GREEN)

OUT = __file__.rsplit("/", 1)[0] + "/"


def contact_side(s, x0, y_floor, k=1.0, crimped=False, ghost=False):
    """XH contact in side view: rear (insulation barrel) at x0, box toward +x, floor at y_floor."""
    op = 0.35 if ghost else (0.9 if crimped else 0.55)
    s.line(x0, y_floor, x0 + 170 * k, y_floor, stroke=BRONZE, sw=3)
    h1, h2 = (22, 12) if crimped else (34, 20)
    s.rect(x0 + 5 * k, y_floor - h1 * k, 34 * k, h1 * k, fill=BRONZE, stroke=INK, sw=0.8, opacity=op)
    s.rect(x0 + 62 * k, y_floor - h2 * k, 34 * k, h2 * k, fill=BRONZE, stroke=INK, sw=0.8, opacity=op)
    s.rect(x0 + 115 * k, y_floor - 30 * k, 55 * k, 30 * k, fill=BRONZE, stroke=INK, sw=0.8,
           opacity=0.35 if ghost else 0.8)


# --------------------------------------------------------------------------------------------- b1
def b1():
    s = Sketch(1500, 920, "b1  Bought press + OTP applicator in post-feed; a printer-axis shuttle presents one conductor at a time")
    s.panel(10, 44, 800, 820, "Side elevation, looking along the carrier strip (schematic, not to scale)")
    s.panel(820, 44, 670, 820, "Plan, looking down (schematic, not to scale)")
    yf = 470
    # ram, crimpers, ram finger
    s.rect(500, 110, 230, 120, fill=BOUGHT)
    s.lines(512, 140, ["press ram + applicator ram", "(bought; 1.5-2 t, 30 mm stroke)",
                       "fires on a relay; one fast stroke"], size=12)
    s.rect(548, 230, 44, 160, fill=STEEL)
    s.rect(618, 230, 42, 176, fill=STEEL)
    s.label(592, 300, 745, 300, "insulation crimper")
    s.label(660, 340, 745, 340, "conductor crimper")
    s.rect(510, 230, 28, 190, fill=PRINTED)
    s.path("M524,240 l6,6 l-12,6 l12,6 l-12,6 l12,6 l-6,6", stroke=INK, sw=0.8)
    s.poly([(510, 420), (538, 420), (524, 434)], fill=STEEL)
    s.label(524, 380, 360, 250, "ram finger: spring V on the ram (or the", anchor="end")
    s.text(360, 264, "applicator's wire hold spring); lifts with the ram", size=11, anchor="end")
    # anvil (empty at rest: post-feed)
    s.rect(540, yf + 2, 130, 90, fill=STEEL)
    s.text(552, yf + 50, "anvil: empty at rest", size=12)
    s.text(552, yf + 66, "(post-feed)", size=11)
    contact_side(s, 545, yf, k=0.72, ghost=True)
    s.text(540, yf + 110, "next contact waits one pitch upstream (into the page);", size=11)
    s.text(540, yf + 126, "it slides in on the downstroke", size=11)
    # tooling face
    s.line(500, 90, 500, 650, stroke=ACCENT, sw=1.2, dash="6,4")
    s.text(494, 84, "tooling front face", size=11, fill=ACCENT, anchor="end")
    # cassette + band
    s.rect(120, 420, 200, 30, fill=PRINTED)
    s.rect(120, 470, 200, 36, fill=PRINTED)
    s.rect(20, 452, 300, 14, fill=SILICONE, stroke=SILICONE)
    s.text(128, 440, "cassette top plate", size=11)
    s.text(128, 492, "cassette bottom plate", size=11)
    s.text(26, 446, "webbed ribbon", size=11)
    for i, yb in enumerate((406, 394, 382)):
        s.path(f"M320,{459 - i} C352,{459 - i} 352,{yb} 320,{yb} L150,{yb}", stroke=SILICONE, sw=9)
    s.rect(110, 382 - 7, 40, 14, fill=BRONZE, stroke=INK, sw=0.8)
    s.label(230, 394, 30, 330, "the other split conductors: folded back 180 deg as ONE flat band")
    s.label(125, 380, 30, 350, "crimped ones return to their place, box in a pocket")
    # target conductor held up at ~4.6 mm
    s.path(f"M320,459 L420,459 L560,{yf-42}", stroke=SILICONE, sw=12)
    s.line(560, yf - 42, 610, yf - 55, stroke=COPPER, sw=5)
    s.line(700, yf - 2, 700, yf - 46, sw=1, arrow="both")
    s.lines(706, yf - 30, ["~4.6 mm to the", "conductor centre"], size=10)
    # valley-tine fork
    s.circle(324, 452, 5, fill=INK)
    s.rect(410, 440, 14, 36, fill=PRINTED)
    s.path("M 400,445 C 390,370 300,360 300,398", stroke=INK, sw=1.2, dash="4,3", arrow="start")
    s.text(365, 370, "180 deg", size=11)
    s.label(417, 470, 30, 690, "valley-tine fork: pivot at the clamp edge, two 0.25 mm tines, holds Y only (slot open downward)")
    # neck fork for the proof pull
    s.rect(686, yf - 70, 6, 50, fill=STEEL)
    s.label(689, yf - 22, 690, 505, "neck fork: proof pull 20 N after the stroke")
    # camera
    s.rect(230, 150, 60, 40, fill=BOUGHT)
    s.circle(290, 170, 12, fill="#555")
    s.poly([(298, 175), (640, 450), (590, 478)], fill="#f4d35e", opacity=0.25, stroke="none")
    s.lines(160, 120, ["ELP camera: the waiting contact upstream at rest,",
                       "the tip over the anvil, the finished crimp"], size=11)
    # shuttle
    s.rect(110, 540, 240, 14, fill=BOUGHT)
    s.text(110, 572, "shuttle: MGN12 rails, NEMA 17 + Tr8x2 (Prime rows)", size=11)
    s.line(120, 592, 280, 592, sw=1.4, arrow="both")
    s.text(290, 596, "X: approach, withdraw, proof pull", size=11)
    s.text(110, 616, "Y (into the page): index to the next conductor", size=11)
    s.line(324, 720, 670, 720, sw=1, arrow="both")
    s.text(330, 738, "split 8-15 mm: tooling depth 6-12 mm [estimate] + bend and fork [calc geometry s1]", size=11)
    s.lines(20, 772, ["Reference for 'fixed': the applicator locates the contact; the ram finger's V, bolted to the ram,",
                      "puts the conductor on the crimp axis at first die touch; axial depth comes from the cassette datum.",
                      "Lateral capture in the open insulation wings: clone +/-0.21-0.83 mm, JST envelope +/-0.08-0.18 mm [TS s4]."],
            size=11)
    # plan
    ax = 400
    s.rect(1180, 110, 290, 600, fill=BOUGHT, opacity=0.35, stroke=MUTED)
    s.text(1262, 128, "applicator footprint (bought)", size=11)
    s.rect(1230, ax - 45, 110, 90, fill=ACCENT, opacity=0.12, stroke=ACCENT, dash="4,3")
    s.lines(1350, ax - 60, ["punch zone,", "half-width", "3-6 mm", "[estimate]"], size=11, fill=ACCENT)
    s.rect(1236, 120, 12, 580, fill=BRONZE, stroke=INK, sw=0.8, opacity=0.8)
    for yy in range(160, 700, 60):
        if yy == ax:
            s.rect(1248, yy - 9, 80, 18, fill="none", stroke=INK, sw=0.8, dash="3,2")
            continue
        s.rect(1248, yy - 9, 80, 18, fill=BRONZE, stroke=INK, sw=0.6, opacity=0.6)
        s.circle(1242, yy, 3.5, fill="#fff", stroke=INK, sw=0.6)
    s.text(1335, ax + 4, "station: empty", size=10)
    s.line(1225, 150, 1225, 250, arrow="end")
    s.text(1220, 146, "strip feed (applicator cam, post-feed)", size=11, anchor="end")
    s.text(1300, 725, "contact pitch on strip ~7.1 mm [facts, Wurth analog]", size=11, anchor="middle")
    # cassette + flat band
    s.rect(900, 300, 190, 200, fill=PRINTED, opacity=0.8)
    s.text(905, 318, "cassette (printed)", size=11)
    s.rect(830, 360, 70, 80, fill=SILICONE, opacity=0.9, stroke=SILICONE)
    s.text(835, 352, "ribbon", size=10)
    for i, yy in enumerate((368, 384, 400, 416, 432)):
        if yy == ax:
            s.line(1090, yy, 1280, yy, stroke=SILICONE, sw=12)
            s.line(1280, yy, 1305, yy, stroke=COPPER, sw=5)
        else:
            s.rect(930, yy - 7, 160, 14, fill="#666", stroke="#fff", sw=1)
    s.text(935, 352, "flat band (4 of 5 conductors)", size=10)
    s.text(905, 470, "the band lies back over the top plate, in ribbon order", size=11)
    s.rect(1120, 388, 6, 24, fill=STEEL)
    s.rect(1128, 388, 6, 24, fill=STEEL)
    s.text(1100, 380, "tines", size=11)
    s.line(860, 530, 860, 610, sw=1.4, arrow="both")
    s.text(870, 575, "Y index 1.7 mm per conductor", size=11)
    s.line(900, 640, 1060, 640, sw=1.4, arrow="both")
    s.text(905, 660, "X toward the die", size=11)
    s.line(1090, 300, 1090, 520, stroke=ACCENT, sw=1, dash="3,3")
    s.text(1086, 540, "clamp edge = split root = datum", size=11, anchor="end", fill=ACCENT)
    s.lines(830, 760, ["A neighbour left flat in the anvil plane at 1.7 or 2.5 mm spacing sits inside the punch zone",
                       "[calc geometry s1]; with the strip attached the only open side is behind the tooling,",
                       "so every conductor except the target lies back in the band."], size=11)
    s.legend(20, 900)
    s.save(OUT + "b1-press-shuttle.svg")


# --------------------------------------------------------------------------------------------- b1b
def b1b():
    s = Sketch(1450, 900, "b1b  The OTP applicator in a slow crank built into the idle 12-ton shop press")
    s.panel(10, 44, 930, 820, "Front elevation (schematic, not to scale)")
    # shop press H-frame
    for x in (150, 800):
        s.rect(x - 15, 110, 30, 700, fill=STEEL)
    s.rect(120, 110, 710, 40, fill=STEEL)
    s.text(130, 135, "shop press top beam (VEVOR 12 t, on hand)", size=11)
    s.rect(120, 640, 710, 34, fill=STEEL)
    s.text(130, 662, "press bed (two channels on pins)", size=11)
    # crank unit
    for x in (330, 560):
        s.rect(x, 150, 60, 40, fill=BOUGHT)
    s.text(565, 205, "UCP204 pillow blocks", size=11)
    s.line(260, 172, 880, 172, stroke=INK, sw=5)
    s.text(620, 168, "20 mm crankshaft", size=11)
    s.circle(455, 205, 46, fill=STEEL, opacity=0.6)
    s.circle(455, 245, 7, fill=INK)
    s.text(505, 250, "crank disc: throw = half the applicator's stroke", size=11)
    s.text(505, 264, "(15 mm for 30 mm, 20 mm for 40 mm); shown at BDC", size=11)
    # rod with stack and gauges
    s.rect(446, 245, 18, 60, fill=STEEL)
    for i in range(2):
        s.poly([(436, 305 + i * 14), (474, 305 + i * 14), (464, 317 + i * 14), (446, 317 + i * 14)],
               fill=GREEN, opacity=0.6)
    s.rect(446, 333, 18, 40, fill=STEEL)
    s.label(474, 318, 520, 312, "disc-spring stack: 2 x DIN 2093 A35.5, ~4 kN preload,")
    s.text(520, 326, "~0.3 mm to ~5.2 kN; microswitch = 'stopped at force' [TS s7]", size=11)
    s.rect(466, 345, 12, 22, fill=ACCENT, opacity=0.7, stroke=ACCENT)
    s.label(478, 356, 520, 360, "BF350 gauges -> HX711: ~19 samples in the last 0.2 mm at 10 s")
    s.rect(430, 373, 50, 36, fill=BRONZE)
    s.label(480, 391, 520, 400, "ram in a bronze bushing")
    s.rect(443, 409, 24, 60, fill=STEEL)
    s.rect(415, 469, 80, 14, fill=STEEL)
    s.text(300, 481, "T-slot block", size=11)
    # applicator on the bed, wedge
    s.rect(360, 483, 190, 140, fill=BOUGHT)
    s.lines(370, 512, ["OTP side-feed XH", "applicator (bought)", "pre-feed: a contact", "waits on the anvil"], size=12)
    s.poly([(350, 640), (560, 640), (560, 623), (350, 632)], fill=STEEL, opacity=0.7, dash="4,3")
    s.label(540, 630, 575, 612, "optional stepper wedge: crimp-height sweep [TS wave2 s8]")
    s.line(360, 610, 170, 610, stroke=BRONZE, sw=3)
    s.text(175, 604, "carrier strip in", size=11)
    # air nozzle + reject cup
    s.line(600, 527, 555, 560, stroke=INK, sw=2, arrow="end")
    s.text(575, 500, "puff (24 V 5/2 valve) clears a crushed", size=11)
    s.text(575, 514, "contact on a reject turn, 220-266 deg", size=11)
    s.rect(640, 540, 44, 30, fill="none", stroke=INK)
    s.text(692, 560, "reject cup", size=10)
    # motor
    s.rect(880, 150, 45, 44, fill=BOUGHT)
    s.text(470, 96, "NEMA 23 + DM542T (on hand) + 10:1 planetary (Prime, 10 N*m permissible)", size=11)
    # jack note
    s.lines(170, 720, ["Stage 0, the jack test: the bottle jack strokes the applicator by hand",
                       "against a hard-stop collar; measures feed timing, envelope and geometry."], size=11)
    s.path("M 505,490 L 505,652 L 165,652 L 165,160 L 350,160 L 440,200 L 452,300", stroke=ACCENT, sw=2, dash="7,4",
           arrow="end")
    s.text(170, 790, "force loop: crank -> rod -> stack -> ram -> applicator -> bed -> columns -> top beam -> bearings",
           size=12, fill=ACCENT)
    s.text(170, 810, "bottom dead centre comes from crank geometry; rod length set once to the applicator's shut height",
           size=12)
    # numbers panel
    s.panel(950, 44, 490, 820, "Sequence and numbers")
    rows = [
        "One conductor (0 deg = top dead centre):",
        "  1  look at the contact ALONE on the anvil",
        "  2  fork lays conductor in; foot seats it",
        "  3  gate: picture + far-end continuity",
        "  4  crank through BDC, force logged",
        "  5  dwell 220 -> 266-285 deg: foot and fork off,",
        "     withdraw, neck fork, 20 N pull, picture",
        "  6  finish the turn: feed on an empty anvil",
        "  reject turn: band aside, crimp empty, puff",
        "",
        "Torque at the crank [calc presses s1]:",
        "  3.8 N*m through a 3 kN design crimp",
        "  5.4 N*m mid-stroke at 300 N of springs",
        "Drive held to the gearbox's 10 N*m:",
        "  4.6 kN at 0.1 mm above BDC [calc wave3 s4]",
        "Dwell: 1.3-1.8 s at a 10 s turn, or stopped",
        "  [calc wave3 s1, s5]",
        "HX711 at 80 Hz, last 0.2 mm: 19 samples at",
        "  10 s, 39 at 20 s, 78 at 40 s [calc wave3 s3]",
        "",
        "Frame: the 12 t press barely notices 3 kN.",
        "Laser-cut O-frame alternative: 13-39 kN/mm,",
        "  +/-0.024-0.008 mm scatter [calc presses s2].",
        "3 t arbor press (310 mm opening) is the",
        "  Prime frame that fits an applicator.",
    ]
    s.lines(965, 80, rows, size=12, gap=19)
    s.legend(20, 890)
    s.save(OUT + "b1b-crank-press.svg")


# --------------------------------------------------------------------------------------------- b2
def b2():
    s = Sketch(1450, 880, "b2  A ratchet hand crimper in a frame, closed through a spring link; a post in the box places each contact")
    s.panel(10, 44, 600, 780, "View along the wire axis (schematic)")
    s.panel(620, 44, 820, 780, "Side view, wire axis left to right (schematic)")
    # left: tool
    s.rect(50, 720, 540, 24, fill="#bbb")
    s.text(60, 738, "aluminium base plate", size=11)
    s.poly([(290, 170), (460, 190), (460, 245), (290, 245)], fill=STEEL)
    s.poly([(290, 255), (460, 255), (460, 310), (290, 330)], fill=STEEL)
    s.circle(300, 250, 9, fill=INK)
    for x in (330, 370, 410, 445):
        s.rect(x, 243, 12 if x != 410 else 16, 14, fill="#fff", stroke=INK, sw=0.8)
    s.label(418, 250, 470, 150, "XH nest", size=11)
    s.text(310, 160, "SN-2549 jaws ($22.29, Prime)", size=11)
    s.poly([(290, 245), (280, 250), (110, 640), (140, 650)], fill=BOUGHT)
    s.poly([(300, 262), (312, 258), (290, 660), (258, 655)], fill=BOUGHT, opacity=0.9)
    s.text(40, 440, "fixed handle", size=11)
    s.text(320, 520, "moving handle", size=11)
    s.rect(85, 600, 90, 120, fill=PRINTED)
    s.text(50, 590, "printed saddle", size=11)
    # spring link + actuator
    s.rect(330, 626, 70, 22, fill=PRINTED)
    s.path("M335,637 l6,-7 l6,14 l6,-14 l6,14 l6,-14 l6,14 l6,-14 l6,14 l6,-7", stroke=INK, sw=0.9)
    s.line(296, 634, 330, 637, sw=3)
    s.line(400, 637, 470, 650, sw=4, stroke="#777")
    s.rect(470, 630, 100, 40, fill=BOUGHT)
    s.lines(420, 580, ["12 V actuator (Justech 1,500 N,", "7 mm/s, Prime) through a spring link"], size=11)
    s.label(365, 648, 330, 700, "spring link: preload ~1.25 x handle need; switch = 'closed by force'")
    s.circle(300, 250, 16, fill="none", stroke=GREEN, sw=2)
    s.label(314, 262, 360, 470, "AS5600 on the pivot: finds the captive click")
    s.lines(30, 770, ["Handle force 40-325 N for a 0.8-2.6 kN crimp at a ratio of 8-20 [calc presses s4].",
                      "The link caps die force near 3.2 kN; if the dies bottom face to face the tool sets BDC."], size=11)
    # right: side view
    yf = 470
    s.rect(900, 290, 60, 170, fill=STEEL)
    s.rect(900, yf + 4, 60, 150, fill=STEEL)
    s.text(905, 282, "jaw plates", size=11)
    s.line(961, 270, 961, 640, stroke=MUTED, sw=1, dash="4,3")
    s.text(966, 266, "jaw front face", size=10, fill=MUTED)
    # placed contact (state B)
    contact_side(s, 893, yf, k=0.55)
    s.rect(958, yf - 60, 5, 55, fill=ACCENT)
    s.label(960, yf - 60, 1000, 300, "flap blade (feeler leaf) drops into the neck after capture")
    # post in the box of the placed contact
    s.rect(986, yf - 12, 60, 5, fill=STEEL)
    s.rect(1000, yf - 22, 40, 26, fill=PRINTED, opacity=0.8)
    s.label(1020, yf - 22, 1080, 380, "post head: 0.64 mm pin in the box, floating holder, stripper sleeve")
    # funnel + conductor
    s.poly([(760, 440), (860, 460), (860, 480), (760, 500)], fill=PRINTED, opacity=0.8)
    s.text(700, 430, "printed funnel", size=11)
    s.rect(650, yf - 16, 250, 10, fill=SILICONE, stroke=SILICONE)
    s.rect(900, yf - 13, 24, 4, fill=COPPER, stroke=COPPER)
    s.line(680, 520, 780, 520, arrow="end")
    s.lines(650, 545, ["conductor arrives along the axis, strands to the", "blade: by hand (b2b) or by b1's shuttle"], size=11)
    # track station (state A), drawn to the right, lower
    ya = 640
    s.rect(1090, ya, 150, 18, fill=STEEL)
    s.text(1095, ya + 36, "steel land; its left edge is the tab root", size=11)
    s.rect(1040, ya + 4, 48, 10, fill=BRONZE, stroke=INK, sw=0.6)
    s.rect(1000, ya + 14, 90, 14, fill=PRINTED)
    s.path(f"M1000,{ya+28} l-10,10", stroke=INK)
    s.text(900, ya + 60, "drop section, hinged 2-3 mm upstream of the station tab:", size=11)
    s.text(900, ya + 74, "pushes the carrier down; the tab shears on the steel edge", size=11)
    contact_side(s, 1090, ya, k=0.55, ghost=True)
    s.rect(1183, ya - 12, 60, 5, fill=STEEL, opacity=0.5)
    s.path(f"M1100,{ya-30} C1060,{ya-120} 1000,{yf+60} 960,{yf+20}", stroke=INK, sw=1.2, dash="5,3", arrow="end")
    s.lines(1110, ya - 120, ["A: at the track, the post enters the box,", "the tab is cut, the silhouette is measured",
                              "B: carried barrels first into the open dies,", "stop = jaw-face fiducial + measured offset"], size=11)
    s.rect(1250, ya - 6, 150, 12, fill=STEEL, opacity=0.6)
    s.lines(1250, ya - 40, ["pawl on a flat run + tapered", "pin in a neighbouring hole"], size=11)
    # camera
    s.rect(820, 700, 60, 36, fill=BOUGHT)
    s.circle(850, 700, 10, fill="#555")
    s.poly([(850, 690), (910, yf + 20), (945, yf + 10)], fill="#f4d35e", opacity=0.25, stroke="none")
    s.text(700, 760, "camera: silhouette on the post, brush at the blade, insulation edge", size=11)
    s.lines(640, 790, ["Reference for 'fixed': the tool body. The shear force (48-158 N) is reacted by the steel land,",
                       "not by the post; the post only holds the contact and sets the box-front datum."], size=11)
    s.legend(20, 870)
    s.save(OUT + "b2-hand-crimper-frame.svg")


# --------------------------------------------------------------------------------------------- b3
def b3():
    s = Sketch(1450, 900, "b3  A cheap printer gantry carries a narrow crimp head to a fanned ribbon (the head goes to the wire)")
    s.panel(10, 44, 820, 810, "Plan on the printer bed (schematic)")
    s.panel(840, 44, 600, 810, "Elevation through the head (schematic)")
    s.rect(100, 220, 360, 380, fill=PRINTED, opacity=0.8)
    s.text(110, 240, "fan fixture (printed): grooves + clamp bar, no trim steps", size=11)
    s.rect(20, 380, 230, 70, fill=SILICONE, stroke=SILICONE)
    ys_r = [386, 400, 414, 428, 442]
    ys_f = [415 - 76, 415 - 38, 415, 415 + 38, 415 + 76]
    for yr, yfan in zip(ys_r, ys_f):
        # equal along-conductor length: the outer tips end further back
        extra = abs(yfan - 415) * 0.25
        xend = 525 - extra
        s.path(f"M250,{yr} C330,{yr} 360,{yfan} 440,{yfan} L {xend:.0f},{yfan}", stroke=SILICONE, sw=11)
        s.line(xend, yfan, xend + 26, yfan, stroke=COPPER, sw=5)
    s.path("M 506,339 Q 540,415 506,491", stroke=ACCENT, sw=1.2, dash="4,3")
    s.lines(520, 520, ["tips at equal along-conductor distance", "from the root: strip line cut while flat",
                       "(b6 rip + slug, b4 scores, or p7)"], size=11, fill=ACCENT)
    s.line(460, 230, 460, 600, stroke=MUTED, dash="4,3")
    s.text(300, 660, "fan pitch 3.6-6.4 mm for die sets 4.5-10 mm wide [calc geometry s2]", size=11)
    s.rect(540, 415 - 24, 42, 48, fill=STEEL, opacity=0.85)
    s.rect(582, 415 - 60, 130, 120, fill=BOUGHT, opacity=0.7)
    s.lines(590, 395, ["head body:", "motor + crank", "inside"], size=11)
    s.label(561, 395, 560, 330, "narrow dies + V-fork", anchor="middle")
    s.rect(560, 110, 240, 26, fill=PRINTED)
    for x in range(575, 800, 40):
        s.rect(x, 136, 14, 42, fill=BRONZE, stroke=INK, sw=0.6, opacity=0.6)
    s.text(560, 104, "strip feeder at the frame side: pawl on a flat run + tapered pin", size=11)
    s.rect(640, 700, 150, 40, fill=PRINTED)
    s.rect(660, 708, 110, 24, fill="#eee", stroke=INK)
    s.text(640, 760, "housing nest + converging comb", size=11)
    s.line(820 - 20, 600, 820 - 20, 680, arrow="both")
    s.text(700, 630, "carriage: across", size=11)
    s.line(300, 740, 440, 740, arrow="both")
    s.text(300, 760, "bed: along the wire (slides the conductor into the contact)", size=11)
    s.lines(20, 800, ["Fronts in the housing land short only by the housing fan: 4P 0.04, 5P 0.06, J4 0.14, J1 0.25 mm",
                      "at 20 mm free length [calc wave3 s7]. The printer carries positions only; crimp force stays in the head."],
            size=11)
    # elevation
    ycl = 455
    s.rect(870, ycl - 26, 180, 20, fill=PRINTED)
    s.rect(870, ycl + 8, 180, 60, fill=PRINTED)
    s.text(875, ycl + 45, "fixture + clamp bar", size=11)
    s.rect(870, ycl - 6, 250, 12, fill=SILICONE, stroke=SILICONE)
    s.rect(1120, ycl - 3, 40, 6, fill=COPPER, stroke=COPPER)
    s.rect(1300, 220, 40, 330, fill=STEEL, opacity=0.8)
    s.rect(1100, 500, 240, 30, fill=STEEL, opacity=0.8)
    s.text(1170, 522, "fixed lower arm", size=11)
    s.rect(1120, ycl + 8, 100, 37, fill=STEEL)
    s.text(1130, ycl + 32, "anvil", size=11)
    s.rect(1108, ycl + 20, 10, 40, fill=ACCENT, opacity=0.7)
    s.label(1112, ycl + 55, 900, 610, "drop blade at the anvil's rear edge: cuts the tab at its root, beside the pinch")
    s.rect(1110, 360, 190, 30, fill=STEEL, opacity=0.8)
    s.text(1150, 380, "sliding punch holder", size=11)
    s.rect(1130, 390, 90, 50, fill=STEEL)
    s.text(1140, 420, "punches", size=11)
    s.rect(1225, 395, 5, 55, fill=ACCENT)
    s.label(1227, 420, 1346, 430, "neck blade")
    s.poly([(1075, ycl - 24), (1100, ycl - 8), (1100, ycl + 8), (1075, ycl + 24)], fill=PRINTED)
    s.label(1080, ycl - 20, 900, 300, "V-fork on the head's rear face")
    s.line(1255, 320, 1255, 358, arrow="end")
    s.circle(1255, 290, 26, fill=STEEL, opacity=0.6)
    s.rect(1180, 240, 60, 50, fill=BOUGHT)
    s.lines(1060, 200, ["NEMA 17 + planetary + 3 mm crank:", "the crimp force closes inside the C"], size=11)
    s.rect(1150, 110, 200, 40, fill=BOUGHT)
    s.text(1160, 135, "printer X carriage", size=11)
    s.line(1320, 150, 1320, 220, sw=3)
    s.lines(860, 690, ["The head picks the lead contact, closes to captive and cuts the tab on the anvil's rear edge;",
                       "the neck blade drops in; the bed slides the conductor into the open barrels until the strands",
                       "touch the blade; then the crank crimps."], size=11)
    s.legend(20, 890)
    s.save(OUT + "b3-gantry-head.svg")


# --------------------------------------------------------------------------------------------- b4
def b4():
    s = Sketch(1400, 820, "b4  A laser engraver slits the webs and scores the strip line; silicone's weak tear finishes the job")
    s.panel(10, 44, 640, 720, "Section through two webbed conductors (to scale, 60 px per mm)")
    s.panel(660, 44, 730, 720, "Plan of a 5P end in the cassette on the laser bed (schematic)")
    k = 60.0
    R, Ri = 0.85 * k, 0.36 * k
    d0 = 0.65 * 0.49
    for cx in (250.0, 250.0 + 1.7 * k):
        cy = 380.0
        s.circle(cx, cy, R, fill=SILICONE, stroke=INK, sw=1, opacity=0.9)
        s.circle(cx, cy, Ri, fill=COPPER, stroke=INK, sw=0.8)
        for sign in (1, -1):
            pts_out, pts_in = [], []
            for i in range(0, 181):
                phi = radians(-89 + i * 178 / 180)
                depth = d0 * cos(phi) ** 2 * k
                pts_out.append((cx + R * sin(phi), cy - sign * R * cos(phi)))
                pts_in.append((cx + (R - depth) * sin(phi), cy - sign * (R - depth) * cos(phi)))
            s.poly(pts_out + pts_in[::-1], fill="#f4a261", stroke="none", opacity=0.9)
    s.line(250 + 0.85 * k, 250, 250 + 0.85 * k, 380, stroke=ACCENT, sw=2)
    s.line(250 + 0.85 * k, 380, 250 + 0.85 * k, 510, stroke=ACCENT, sw=2, dash="4,3")
    s.lines(410, 245, ["web slit from each side to about", "the mid-plane (kerf ~0.1-0.2 mm)"], size=11, fill=ACCENT)
    for x in (230, 270, 330, 370):
        s.line(x, 180, x, 300, arrow="end", stroke="#d97706")
        s.line(x, 590, x, 470, arrow="end", stroke="#d97706")
    s.text(130, 170, "beam from above", size=11)
    s.text(130, 612, "beam from below, after a flip on the pins", size=11)
    s.lines(30, 660, ["Orange: score ~60-70 % of the 0.49 mm wall at the crown, falling as cos^2 toward the flanks",
                      "[estimate]. 80 % would leave as little as 0.04 mm over the strands where the wall is thinnest.",
                      "Tear-off at 60 %: 4.7-13 N per conductor (4-11 MPa) [calc geometry s3, calc wave3 s8]."], size=11)
    s.rect(700, 250, 300, 260, fill=PRINTED, opacity=0.8)
    s.text(705, 268, "cassette (the one the crimper uses)", size=11)
    s.circle(720, 290, 7, fill="#fff")
    s.circle(720, 470, 7, fill="#fff")
    s.text(735, 475, "datum pins: flip about the ribbon axis", size=11)
    s.rect(680, 330, 560, 100, fill=SILICONE, opacity=0.95, stroke=SILICONE)
    for i in range(1, 5):
        y = 330 + i * 20
        s.line(1000, y, 1195, y, stroke=ACCENT, sw=2)
    s.text(1005, 320, "web slits: clamp edge -> score line only", size=11, fill=ACCENT)
    s.line(1200, 322, 1200, 440, stroke="#d97706", sw=4)
    s.lines(1110, 470, ["score line Ls from the tip (2.4 mm JST,", "1.85-2.1 mm clone contacts)"], size=11, fill="#d97706")
    s.rect(1208, 312, 40, 18, fill=PRINTED)
    s.rect(1208, 430, 40, 18, fill=PRINTED)
    s.lines(1060, 560, ["TPU pads pinch the still-webbed tip; the cassette", "backs off 3 mm; the whole tip leaves as ONE",
                        "comb-shaped slug (~24-65 N for a 5P)"], size=11)
    s.line(1000, 250, 1000, 520, stroke=ACCENT, dash="3,3")
    s.text(1000, 540, "split root = clamp edge = datum", size=11, anchor="middle", fill=ACCENT)
    s.lines(680, 650, ["Lasers: the H2C's 455 nm module (10 W / 40 W kit, 3D Universe) or a CO2 engraver ($759.90, Prime).",
                       "CO2 stops at copper (copper reflects 10.6 um); 455 nm does not (copper absorbs ~65 %),",
                       "so the blue laser only scores. Ash is brushed off before crimping."], size=11)
    s.legend(20, 810)
    s.save(OUT + "b4-laser-score.svg")


# --------------------------------------------------------------------------------------------- b4b
def b4b():
    s = Sketch(1300, 720, "b4b  Two diode heads at the station: both faces scored and slit in the pose the crimp uses")
    s.panel(10, 44, 1280, 620, "Side section along the wire (schematic, not to scale)")
    # enclosure
    s.rect(420, 110, 560, 480, fill="none", stroke=INK, sw=2)
    s.text(430, 130, "light-tight box, interlocked lid, fan ducted outdoors", size=11)
    s.rect(410, 330, 20, 50, fill="#444")
    s.text(380, 440, "brush slot in the box wall", size=11)
    # bed plate with slot
    s.rect(440, 380, 520, 16, fill=STEEL)
    s.rect(700, 380, 60, 16, fill="#fff", stroke=INK, sw=0.8)
    s.text(600, 420, "steel bed plate; slot under the ribbon", size=11)
    # cassette on shuttle
    s.rect(80, 330, 260, 30, fill=PRINTED)
    s.rect(80, 372, 260, 30, fill=PRINTED)
    s.text(90, 320, "cassette on b1's shuttle (or b8/b8b's work clamp)", size=11)
    s.rect(60, 360, 760, 12, fill=SILICONE, stroke=SILICONE)
    s.line(120, 450, 300, 450, sw=1.4, arrow="both")
    s.text(120, 470, "shuttle X sweeps the slits; Y sweeps the scores", size=11)
    # heads
    s.rect(700, 150, 60, 90, fill=BOUGHT)
    s.text(770, 180, "top head: 450 nm module, 10 W optical", size=11)
    s.text(770, 196, "(LASER TREE, $137.17, Prime), air assist", size=11)
    s.poly([(720, 240), (740, 240), (731, 358)], fill="#60a5fa", opacity=0.5, stroke="none")
    s.rect(700, 480, 60, 90, fill=BOUGHT)
    s.text(770, 520, "bottom head looking up through the slot", size=11)
    s.text(770, 536, "(its window faces falling ash)", size=11)
    s.poly([(720, 480), (740, 480), (731, 374)], fill="#60a5fa", opacity=0.5, stroke="none")
    # pads and cup
    s.rect(800, 336, 30, 20, fill=PRINTED)
    s.rect(800, 376, 30, 20, fill=PRINTED)
    s.label(815, 336, 860, 290, "TPU pads pinch the webbed tip; shuttle backs off 3 mm")
    s.rect(840, 440, 60, 40, fill="none", stroke=INK)
    s.text(840, 500, "slug cup", size=11)
    s.lines(30, 620, ["Order as b4: score both faces at the strip line (~60-70 % of the wall), then slit each web from the clamp edge",
                      "to the score line from both sides, then pinch and pull the whole tip. No dock, no flip, no module swap on the H2C;",
                      "a redo is re-scored in place, in the crimp's own coordinates."], size=12)
    s.save(OUT + "b4b-diode-station.svg")


# --------------------------------------------------------------------------------------------- b5
def b5():
    s = Sketch(1250, 820, "b5  A desktop arm operates one-step stations; the stations hold the precision")
    s.panel(10, 44, 760, 740, "Plan of the cell (schematic)")
    cx, cy = 390, 420
    s.circle(cx, cy, 250, fill="none", stroke=MUTED, dash="5,4")
    s.text(cx + 120, cy - 240, "reach ~440 mm (MG400) / ~400 mm (SO-101)", size=11, fill=MUTED)
    s.circle(cx, cy, 45, fill=BOUGHT)
    s.text(cx, cy + 5, "arm", size=13, anchor="middle")
    stations = [("cassette rack", 0), ("rip board (b6) / laser", 55), ("pinch pull + brush", 110),
                ("crimp cell (b1b / b2)", 165), ("insertion jig", 220), ("continuity test", 275)]
    for name, ang in stations:
        a = radians(ang - 90)
        x = cx + 210 * cos(a)
        y = cy + 210 * sin(a)
        s.rect(x - 62, y - 28, 124, 56, fill=PRINTED, opacity=0.85)
        s.text(x, y - 5, name, size=11, anchor="middle")
        s.poly([(x - 18, y + 20), (x, y + 6), (x + 18, y + 20)], fill="#fff", stroke=INK, sw=0.8)
        s.line(cx + 50 * cos(a), cy + 50 * sin(a), x - 40 * cos(a), y - 40 * sin(a), stroke=MUTED, dash="3,3")
    s.lines(30, 720, ["Each dock is a kinematic seat (cones + vee) with >= 5 mm lead-in and a magnet;",
                      "a hall sensor says 'seated'. Every dock is approached from above, the same way."], size=11)
    s.panel(780, 44, 460, 740, "Two tiers of borrowed arm")
    rows = ["Cheap tier: SO-101 (LeRobot)", "  follower kit $184.99; Pro servo kit $360;",
            "  assembled kit $269.99-459.99 (Prime rows)", "  STS3215: 0.87 deg backlash, 0.17 deg repeat",
            "  same-direction docking: ~1.2 mm RSS, 2.2 worst", "  -> carries cassettes between docks; flips", "",
            "Precise tier: Dobot MG400, $2,890-3,495", "  +/-0.05 mm, 500-750 g payload, 440 mm",
            "  + terminal-supply's post head:", "  picks a loose contact, measures it on the post,",
            "  sets it in an open die, then presents each", "  conductor (Kurabo's pattern)", "",
            "Carrying costs the person least; every", "cheap-tier reason has another route (b4b,",
            "a slide magazine, the spool). Where an arm", "could earn its place: loading ribbon ends,",
            "taught by imitation (>= 50 demos per task).", "", "[calc cycle_and_arm.out.txt]"]
    s.lines(795, 80, rows, size=12, gap=19)
    s.legend(20, 810)
    s.save(OUT + "b5-arm-stations.svg")


# --------------------------------------------------------------------------------------------- b8b
def b8b():
    s = Sketch(1500, 1000, "b8b  The flat spool line over a crown (b8 x terminal-supply a2d): nothing folds")
    s.panel(10, 44, 980, 560, "Plan (schematic, not to scale)")
    s.panel(1000, 44, 490, 560, "Section across the crown, looking along the wire (schematic)")
    # spool + head
    s.circle(80, 320, 55, fill=BOUGHT)
    s.circle(80, 320, 14, fill=STEEL)
    s.lines(30, 400, ["4P spool; inner end", "on a slip ring"], size=10)
    s.path("M135,320 C170,380 190,380 215,330", stroke=SILICONE, sw=5)
    s.rect(210, 250, 290, 150, fill=BOUGHT, opacity=0.35, stroke=MUTED)
    s.text(215, 245, "feed head on an X/Y stage", size=11)
    s.rect(220, 270, 40, 26, fill=BOUGHT)
    s.rect(220, 340, 40, 26, fill=BOUGHT)
    s.text(215, 420, "belts + encoder", size=10)
    s.rect(280, 290, 10, 70, fill=STEEL)
    s.text(270, 436, "guillotine", size=10)
    s.rect(330, 285, 90, 22, fill=PRINTED)
    s.rect(330, 343, 90, 22, fill=PRINTED)
    s.text(330, 280, "work clamp", size=10)
    s.rect(210, 309, 210, 32, fill=SILICONE, stroke=SILICONE)
    s.line(420, 230, 420, 470, stroke=ACCENT, dash="5,4")
    s.text(420, 486, "clamp face = root", size=10, fill=ACCENT, anchor="middle")
    # split conductors through the comb, 1.7 -> p  (plan drawn at ~7 px per mm)
    PX = 7.0
    yc = 325.0
    ys0 = [yc + (i - 1.5) * 1.7 * PX for i in range(4)]
    p_px = 2.5 * PX
    ys1 = [yc + (i - 1.5) * p_px for i in range(4)]
    k_idx = 1
    shift = yc - ys1[k_idx]        # the stage has moved Y so conductor k sits on the station
    x_tip = 712
    for i, (a, b) in enumerate(zip(ys0, ys1)):
        a2, b2 = a + shift, b + shift
        s.path(f"M420,{a2:.1f} L445,{a2:.1f} L475,{b2:.1f} L{x_tip - 17},{b2:.1f}", stroke=SILICONE, sw=11)
        s.line(x_tip - 17, b2, x_tip, b2, stroke=COPPER, sw=4)
    s.rect(440, 270 + shift, 60, 110, fill=PRINTED, opacity=0.35, stroke=INK, dash="3,2")
    s.lines(430, 205, ["spreading comb, entered from the tip side", "after the strip: 1.7 mm -> p (fan), then parallel"],
            size=10)
    s.line(x_tip - 17, 240, x_tip - 17, 420, stroke="#d97706", sw=1.5, dash="4,3")
    s.text(x_tip - 17, 234, "strip line", size=10, fill="#d97706", anchor="middle")
    # crown station: strip along Y (drawn at the same ~7 px per mm)
    xc = 672                        # carrier centre line
    s.rect(xc - 30, 90, 175, 480, fill=STEEL, opacity=0.18, stroke=MUTED)
    s.text(xc - 25, 105, "crown block (steel)", size=10)
    s.rect(xc - 7, 100, 14, 460, fill=BRONZE, stroke=INK, sw=0.6, opacity=0.8)
    s.text(xc + 60, 588, "carrier along Y, wrapping over the crown", size=10, anchor="middle")
    pitch = 7.1 * PX
    for j in range(-4, 5):
        yy = yc + j * pitch
        if yy < 105 or yy > 555:
            continue
        s.circle(xc, yy, 0.75 * PX, fill="#fff", stroke=INK, sw=0.6)
        if j % 2 == 0:
            op = 0.95 if j == 0 else 0.35
            s.rect(xc + 7, yy - 0.95 * PX, 6.0 * PX, 1.9 * PX, fill=BRONZE, stroke=INK, sw=0.6, opacity=op)
    for yy in (yc - pitch, yc + pitch):
        s.circle(xc, yy, 0.75 * PX, fill=ACCENT, stroke=ACCENT)
    s.label(xc, yc + pitch, 800, 470, "tapered pins in the removed contacts' holes (+/-7.1 mm)")
    s.lines(800, 130, ["every other contact punched out upstream;", "the next kept one is 14.2 mm away,",
                       "below the crest plane"], size=10)
    s.lines(800, 290, ["station contact at the crest: conductor k", "slid forward over the carrier into the U;",
                       "neighbours at +/-p lie flat over the flanks"], size=10)
    s.rect(xc + 58, 230, 22, 190, fill=BOUGHT, opacity=0.5)
    s.text(xc + 58, 224, "fence", size=10)
    s.line(xc + 22, 95, xc + 22, 560, stroke="#f4d35e", sw=3)
    s.lines(800, 520, ["level gate view along Y at wing height,", "to a fixed backlight"], size=10)
    # housing nest
    s.rect(870, 390, 80, 44, fill=GREEN, opacity=0.35)
    s.text(870, 384, "housing nest (XHP-4 tube)", size=10)
    # section across the crown
    cx, cy, R = 1245, 520, 250
    s.path(f"M {cx - 200},{cy - sqrt(R*R - 200*200):.1f} A {R} {R} 0 0 1 {cx + 200},{cy - sqrt(R*R - 200*200):.1f}",
           stroke=INK, sw=2, fill="none")
    s.path(f"M {cx - 200},{cy - sqrt(R*R - 200*200):.1f} A {R} {R} 0 0 1 {cx + 200},{cy - sqrt(R*R - 200*200):.1f}",
           stroke=BRONZE, sw=4, fill="none", opacity=0.6)
    top = cy - R
    s.rect(cx - 22, top - 34, 6, 34, fill=BRONZE, opacity=0.8)
    s.rect(cx + 16, top - 34, 6, 34, fill=BRONZE, opacity=0.8)
    s.line(cx - 22, top, cx + 22, top, stroke=BRONZE, sw=4)
    s.circle(cx, top - 17, 17, fill=SILICONE)
    s.circle(cx, top - 17, 7, fill=COPPER)
    for sgn in (-1, 1):
        x = cx + sgn * 62
        s.circle(x, top - 16, 17, fill=SILICONE, opacity=0.8)
    s.lines(cx + 40, top - 52, ["neighbours at +/-p lie flat,", "0.09-0.16 mm below the crest"], size=10)
    ang = radians(32)
    px, py = cx + R * sin(ang), cy - R * cos(ang)
    s.poly([(px - 20 * cos(ang), py - 20 * sin(ang)), (px + 20 * cos(ang), py + 20 * sin(ang)),
            (px + 20 * cos(ang) + 34 * sin(ang), py + 20 * sin(ang) - 34 * cos(ang)),
            (px - 20 * cos(ang) + 34 * sin(ang), py - 20 * sin(ang) - 34 * cos(ang))],
           fill=BRONZE, opacity=0.4)
    s.lines(1150, py + 60, ["next kept contact, 14.2 mm of arc away:", "rotated 32 deg, wing tips 1.2 mm",
                             "below the plane [TS wave2 s2]"], size=10)
    s.rect(cx - 30, top - 140, 60, 80, fill=STEEL, opacity=0.8)
    s.text(cx - 30, top - 148, "knife-set punch (arbor press, hard stop)", size=10)
    s.line(1010, top - 25, 1480, top - 25, stroke="#f4d35e", sw=3)
    s.text(1015, top - 32, "camera line at wing height", size=10)
    s.text(cx, cy - 40, "crown R 25-30 mm", size=11, anchor="middle")
    # steps
    s.panel(10, 614, 1480, 370, "One T4 end")
    rows = ["1 feed out S + Ls past the needles (S = 16 mm here);  2 pierce each web;  3 belts retract S: the needles rip to the strip line; the root lands on the clamp face; clamp",
            "4 flat blades score the crowns to 50-60 % (or ride a shoe); pads pinch the webbed tip; back off 3 mm: one slug (19-52 N for a 4P) [calc wave3 s8]",
            "5 the comb comes in from the tip side and slides back to the clamp face: conductors leave it parallel at the crimp pitch p (2.35-2.80 mm if the punch holder clears)",
            "6 present conductor k over the carrier into the waiting contact; steer X by the insulation edge   7 gate: level picture + continuity spool -> k -> crown block",
            "8 stroke to the hard stop; the drop plate shears the tab   9 punch lifts; neck fork; 20 N pull   10 draw the ribbon back; pins out; advance two pitches;",
            "   look at the new contact alone; fence; step p in Y   11 after four: at p = 2.5 the row is at housing pitch; push an XHP-4 on; 5 N pull-backs",
            "12 test through the spool; feed out the loom; the guillotine squares the next end",
            "",
            "The carrier and crown take 5.3-9.2 mm behind the strip line, so the comb sits behind that and the split is >= 9.3-15.2 mm [calc wave3 s7].",
            "Fronts in the housing at 16 mm free length: 4P ~0.05, 5P ~0.09 mm short; J1 needs ~20 mm (0.25 mm). Supply at skip-2: 0.30 of a reel for all T4 [TS s5].",
            "Reference for 'fixed': the crown block for the contact, anvil, stop and camera fiducials; the work clamp for the ribbon."]
    s.lines(25, 648, rows, size=12, gap=24)
    s.save(OUT + "b8b-flat-spool-line.svg")


if __name__ == "__main__":
    b1(); b1b(); b2(); b3(); b4(); b4b(); b5(); b8b()
    print("written")
