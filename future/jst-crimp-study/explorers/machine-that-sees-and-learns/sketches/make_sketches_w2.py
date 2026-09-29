"""Wave-2 sketches for machine-that-sees-and-learns.

Run: python3 make_sketches_w2.py   (writes the w2-*.svg files beside this script)

Drawings are schematic unless a caption says the geometry comes from cited dimensions.
"""
import math
from make_sketches import SVG, header, INK, GREY, LIGHT, DARK, VIEW, FORCE, GOOD, BAD

AMBER = "#9a6700"
MCU = "#8250df"
PERSON = "#bf3989"


# ------------------------------------------------------------------ v1 lifted neighbours
def v1_lifted():
    s = SVG(980, 665, "v1 neighbours lifted, piano keys")
    header(s, "v1  Neighbours wait 5 mm up; only the active conductor goes down, pressed by its key",
           "End view along the wire at the nest (1 mm = 36 px, positions from cited dimensions); side view of one key at right, schematic.")
    k = 36.0
    cx, fy = 350, 520                        # nest centre, barrel floor
    def Y(mm): return fy - mm * k
    # nest block and black shroud
    s.rect(cx - 150, fy, 300, 70, fill="#24292f")
    s.text(cx, fy + 40, "nest on the anvil (blackened)", size=11, anchor="middle", fill="#ffffff")
    # insulation barrel open U, 2.8 wide x 3.0 tall, 0.2 stock
    w, h, t = 2.8, 3.0, 0.2
    s.rect(cx - w / 2 * k, fy - t * k, w * k, t * k, fill="#c9d1d9")
    s.rect(cx - w / 2 * k, Y(h), t * k, h * k, fill="#c9d1d9")
    s.rect(cx + w / 2 * k - t * k, Y(h), t * k, h * k, fill="#c9d1d9")
    s.text(cx + w / 2 * k + 8, Y(h) + 10, "insulation wings, 2.75-3.2 mm tall", size=10.5, fill=DARK)
    # active conductor laid in
    s.circle(cx, Y(0.85 + t), 0.85 * k, fill="#24292f")
    s.circle(cx, Y(0.85 + t), 0.36 * k, fill="#9aa4ae", stroke="#9aa4ae")
    s.text(cx, Y(0.85 + t) + 4, "", size=9)
    # neighbours at h = 5 mm, pitch 5 mm, in their keys
    for dx in (-5.0, 5.0):
        x = cx + dx * k
        s.rect(x - 1.25 * k, Y(5.0) - 2.2 * k, 2.5 * k, 2.2 * k, fill="none", stroke=INK, dash="5 4")
        s.circle(x, Y(5.0), 0.85 * k, fill="#24292f")
        s.circle(x, Y(5.0), 0.36 * k, fill="#9aa4ae", stroke="#9aa4ae")
    s.text(cx - 5 * k, Y(5.0) - 2.2 * k - 8, "key (up)", size=11, anchor="middle")
    s.text(cx + 5 * k, Y(5.0) - 2.2 * k - 8, "key (up)", size=11, anchor="middle")
    s.text(20, 608, "Dashed: behind this plane. Every key ends 1-2 mm behind the contact; at the nest only the conductors themselves are in the section.", size=10.5, fill=DARK)
    s.text(cx + 5 * k + 1.4 * k, Y(5.0) + 4, "neighbour axis 5 mm up", size=10.5)
    s.text(cx + 5 * k + 1.4 * k, Y(5.0) + 18, "(needs >= 4.1-4.55 mm)", size=10.5, fill=DARK)
    # active key, pressed down, behind the contact (dashed)
    s.rect(cx - 1.25 * k, Y(0.85 + t) - 3.6 * k, 2.5 * k, 3.0 * k, fill="none", stroke=INK, dash="5 4")
    s.text(cx, Y(0.85 + t) - 3.6 * k - 8, "active key, down (1-2 mm behind the contact)", size=10.5, anchor="middle")
    # punch body limit
    s.rect(cx - 4 * k, 105, 8 * k, 40, fill="#afb8c1", stroke=INK)
    s.text(cx, 122, "raised punch or tack former", size=10.5, anchor="middle")
    s.text(cx, 137, "<= 7.45 mm wide up to ~5.9 mm (crimped nbrs)", size=10.5, anchor="middle")
    # camera 2 band under neighbours
    y2 = Y(2.2)
    s.camera(40, y2, ang=0)
    s.text(30, y2 - 20, "cam 2", size=11, fill=VIEW)
    s.line(60, y2, 640, y2, stroke=VIEW, dash="5 4")
    s.rect(650, Y(4.0), 16, 3.0 * k, fill="#fff8c5", stroke=AMBER)
    s.text(642, Y(4.0) - 8, "backlight", size=10.5, anchor="end", fill=AMBER)
    s.text(20, y2 + 22, "side silhouette at wing height", size=10.5, fill=VIEW)
    s.text(20, y2 + 36, "passes under both neighbours", size=10.5, fill=VIEW)
    # camera 1 oblique at 35 deg from vertical
    a = math.radians(35)
    x0, y0 = cx, Y(0.9)
    L = 390
    x1, y1 = x0 - L * math.sin(a), y0 - L * math.cos(a)
    s.line(x1 + 10, y1 + 14, x0, y0, stroke=VIEW, dash="5 4", arrow="view")
    s.camera(x1, y1, ang=55)
    s.text(20, y1 + 40, "cam 1, 30-40 deg", size=11, fill=VIEW)
    s.text(20, y1 + 54, "from vertical (at 45 deg", size=10, fill=DARK)
    s.text(20, y1 + 68, "the near neighbour hides", size=10, fill=DARK)
    s.text(20, y1 + 82, "the U's floor)", size=10, fill=DARK)
    # dimension: pitch
    s.line(cx - 5 * k, Y(6.2) - 70, cx, Y(6.2) - 70, stroke=GREY, arrow="ink")
    s.text(cx - 2.5 * k, Y(6.2) - 76, "5 mm fan pitch", size=10.5, anchor="middle", fill=DARK)
    # side view of a key
    ix, iy = 700, 330
    s.rect(ix, iy - 20, 265, 260, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ix + 132, iy, "one key, side view (schematic)", size=11, anchor="middle", weight="bold")
    s.rect(ix + 15, iy + 40, 60, 60, fill="#d0d7de")
    s.text(ix + 45, iy + 115, "fan block", size=10.5, anchor="middle")
    s.circle(ix + 75, iy + 55, 4, fill="#ffffff")
    s.poly([(ix + 75, iy + 50), (ix + 215, iy + 88), (ix + 215, iy + 104), (ix + 75, iy + 62)], fill="#ddf4ff")
    s.line(ix + 20, iy + 57, ix + 75, iy + 57, stroke="#24292f", sw=5)
    s.line(ix + 75, iy + 57, ix + 215, iy + 97, stroke="#24292f", sw=5)
    s.line(ix + 215, iy + 97, ix + 245, iy + 97, stroke="#9aa4ae", sw=2.5)
    s.rect(ix + 200, iy + 100, 40, 16, fill="#24292f")
    s.line(ix + 190, iy + 20, ix + 190, iy + 78, stroke=FORCE, sw=2.5, arrow="force")
    s.text(ix + 186, iy + 30, "plunger", size=10, anchor="end", fill=FORCE)
    s.rect(ix + 120, iy + 118, 40, 8, fill=DARK)
    s.text(ix + 140, iy + 140, "hard stop on the pallet body", size=10, anchor="middle")
    s.lines(ix + 12, iy + 165, ["hinge where the fan is ~2.5 mm pitch;",
                                "key 20-30 mm: 5 mm drop is 10-15 deg,",
                                "bend at the key root R 24-60 mm,",
                                "20-30 mm behind the contact",
                                "[ribbon-as-pallet calc P s9]"], size=10, fill=DARK)
    s.lines(20, 628, ["Lateral capture with no picture: +/-0.48-0.59 mm for a gathered bundle, +/-0.24-0.35 mm for a splayed one [calc wave2 s2].",
                      "The picture sets Y per conductor from tip and insulation edge, and finds the bad tips."],
            size=11, fill=DARK)
    s.save("w2-v1-lifted-neighbours.svg")


# ------------------------------------------------------------------ v5 box as roll gauge
def v5_roll():
    s = SVG(980, 420, "v5 box as roll gauge")
    header(s, "v5 / v1  The box is its own roll gauge: one silhouette carries both",
           "Silhouette seen across the wire; box 1.9 x 2.35 mm and crimp 1.6 x 0.8 mm rolled 3 deg (exaggerated x3 in the drawing). Schematic.")
    k = 55
    def rect_rot(cx, cy, W, H, deg, fill):
        r = math.radians(deg)
        pts = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x, y = sx * W / 2, sy * H / 2
            xr = x * math.cos(r) - y * math.sin(r)
            yr = x * math.sin(r) + y * math.cos(r)
            pts.append((cx + xr * k, cy + yr * k))
        s.poly(pts, fill=fill)
        ys = [p[1] for p in pts]
        return min(ys), max(ys)
    base = 330
    for (cx, W, H, lab) in ((250, 1.9, 2.35, "box (front 1 mm, ahead of the lance)"), (520, 1.6, 0.8, "conductor crimp")):
        t, b = rect_rot(cx, base - H / 2 * k, W, H, 9, "#c9d1d9")
        s.line(cx - 110, t, cx + 110, t, stroke=VIEW, dash="4 3")
        s.line(cx - 110, b, cx + 110, b, stroke=VIEW, dash="4 3")
        s.text(cx, b + 22, lab, size=11, anchor="middle")
    s.lines(660, 110, ["extent = H cos r + W sin r",
                       "",
                       "box grows 32-34 um per degree:",
                       "0.05-0.3 deg of roll read from it",
                       "(45-122 px/mm) [calc wave2 s1].",
                       "",
                       "crimp corrected by W_c sin r;",
                       "rolled > 2 deg: re-seat, not correct.",
                       "",
                       "box's true height: the lot's minimum",
                       "in a +/-4 deg sweep of five contacts."], size=11.5, fill=DARK)
    s.save("w2-v5-box-roll-gauge.svg")


# ------------------------------------------------------------------ v7 stack
def v7_stack():
    s = SVG(1000, 860, "v7 the run: control stack")
    header(s, "v7  The run: what drives what, where each loop closes, and where Claude sits",
           "Schematic. Arrows are the wires and messages; the time bars below are estimates [calc wave2 s3].")
    def box(x, y, w, h, title, rows, fill, stroke=INK):
        s.rect(x, y, w, h, fill=fill, stroke=stroke, rx=7)
        s.text(x + 10, y + 19, title, size=12.5, weight="bold")
        s.lines(x + 10, y + 37, rows, size=10.3, fill=DARK, gap=13.5)
    s.text(20, 80, "On the bench", size=13, weight="bold", fill=MCU)
    s.text(355, 80, "On the Mac", size=13, weight="bold", fill=VIEW)
    s.text(700, 80, "Claude and Derek", size=13, weight="bold", fill=PERSON)
    box(20, 92, 300, 96, "Stage controller", ["Ender board as bought (Marlin G-code),",
        "or FluidNC on an ESP32, or Klipper MCU.", "Moves only; M400 = moves finished;",
        "never releases the steppers (M84 S0)."], "#f6f0ff", MCU)
    box(20, 200, 300, 176, "Station MCU (ESP32, PlatformIO)", ["press axis: stepper + driver, taught crawl height,",
        "  force envelope checked every sample (HX711/717),", "  stops on a fault (cranks: profiled crawl), completes",
        "  a stroke in compaction if the Mac goes silent;", "servos: keys, tack former, drop-shear;",
        "lights: LED ring one at a time + sync LED;", "far-end port: continuity per conductor;",
        "e-stop, lid, force-ceiling switch cut enable;", "heartbeat, JSON lines over USB serial."], "#f6f0ff", MCU)
    box(20, 388, 300, 80, "Cameras", ["ELP 16MP (oblique / top), MJPG only;",
        "close camera for the side silhouette;", "named by device, never by index."], "#f6f0ff", MCU)
    box(355, 92, 310, 80, "capture app", ["holds the macOS camera grant; opens each", "stream once per run; walks focus upward once;",
        "hands out frames tagged with the light state."], "#ddf4ff", VIEW)
    box(355, 184, 310, 136, "runner (Python, launchd)", ["recipe per loom: pins, skips, crossings;",
        "per conductor: waiting > laid > gated > crimped", "  > inspected > pulled > parked | asked | backed out;",
        "station = look, act, look, decide;", "write-ahead journal: intent before each act,",
        "  result after; a restart re-looks, never re-acts."], "#ddf4ff", VIEW)
    box(355, 332, 310, 96, "judge", ["numbers from OpenCV only;", "pass band / borderline band / hard fail;",
        "borderline -> claude -p --json-schema;", "Claude never passes a hard fail."], "#ddf4ff", VIEW)
    box(355, 440, 310, 80, "log and queue", ["one folder per crimp: crops, trace, record;",
        "SQLite index; thresholds file versioned;", "asks: photo, numbers, proposal, 4 answers."], "#ddf4ff", VIEW)
    box(700, 92, 280, 176, "supervisor session (Claude Code)", ["wakes on an ask, an alarm, or the end;",
        "drafts each ask's proposal from the", "  labelled examples; groups like asks;",
        "watches trends: force peaks, heights,", "  retries by pallet slot, lot changes;",
        "may pause the runner; cannot resume it", "  or move a motor in production;",
        "writes the unit report; proposes new", "  thresholds with their evidence."], "#fff0f6", PERSON)
    box(700, 280, 280, 96, "Derek's phone", ["push with the photo and three buttons;",
        "the answer goes back on a second topic", "  the runner listens to (no port opened",
        "  on the Mac); or the session, followed remotely."], "#fff0f6", PERSON)
    box(700, 388, 280, 80, "Derek at the bench", ["loads pallets, contacts, housings;",
        "answers; e-stop; approves thresholds;", "commissioning and campaigns with Claude."], "#fff0f6", PERSON)
    # arrows
    s.line(320, 140, 355, 215, stroke=MCU, arrow="ink"); s.text(326, 196, "G-code", size=9.5, fill=MCU)
    s.line(320, 280, 355, 270, stroke=MCU, arrow="ink"); s.text(326, 290, "JSON", size=9.5, fill=MCU)
    s.line(320, 420, 355, 140, stroke=MCU, dash="4 3", arrow="ink"); s.text(326, 400, "UVC", size=9.5, fill=MCU)
    s.line(510, 172, 510, 184, arrow="ink")
    s.line(510, 320, 510, 332, arrow="ink")
    s.line(510, 428, 510, 440, arrow="ink")
    s.line(665, 465, 700, 170, stroke=PERSON, arrow="ink"); s.text(672, 132, "reads", size=9.5, fill=PERSON)
    s.line(700, 330, 665, 490, stroke=PERSON, arrow="ink"); s.text(668, 506, "answers", size=9.5, fill=PERSON)
    s.line(665, 360, 700, 240, stroke=PERSON, dash="4 3", arrow="ink"); s.text(630, 300, "claude -p", size=9.5, fill=PERSON)
    # loop time scale
    y0 = 560
    s.text(20, y0 - 10, "Where each loop closes (log time axis)", size=13, weight="bold")
    xa, xb = 250, 980
    lo, hi = math.log10(0.001), math.log10(30 * 86400)
    def X(t): return xa + (math.log10(t) - lo) / (hi - lo) * (xb - xa)
    for t, lab in ((0.001, "1 ms"), (0.1, "0.1 s"), (1, "1 s"), (60, "1 min"), (3600, "1 h"), (86400, "1 d"), (30 * 86400, "30 d")):
        s.line(X(t), y0, X(t), y0 + 250, stroke="#eaeef2")
        s.text(X(t), y0 + 266, lab, size=10, anchor="middle", fill=DARK)
    loops = [("force limit, stroke envelope", MCU, 0.003, 0.0125),
             ("drop to crawl at taught height", MCU, 0.0125, 0.05),
             ("heartbeat hold", MCU, 1, 2),
             ("visual servo round", VIEW, 1, 3),
             ("gate by thresholds", VIEW, 0.2, 1),
             ("borderline judged by Claude", PERSON, 5, 30),
             ("ask answered by Derek", PERSON, 60, 8 * 3600),
             ("trend across an end / unit", PERSON, 600, 6 * 3600),
             ("destructive re-check (v3)", PERSON, 5 * 86400, 30 * 86400)]
    for i, (lab, col, a, b) in enumerate(loops):
        y = y0 + 8 + i * 27
        s.text(20, y + 13, lab, size=11)
        s.rect(X(a), y, max(4, X(b) - X(a)), 16, fill=col, stroke=col, opacity=0.8)
    s.text(20, y0 + 290, "purple: MCU   blue: runner on the Mac   pink: Claude or Derek. At a 0.05 mm/s crawl a USB hiccup of 0.5 s is 25 um "
           "and 375-750 N into a steel stop, so the MCU owns the stroke.", size=10.5, fill=DARK)
    s.save("w2-v7-stack.svg")


# ------------------------------------------------------------------ v7 first day
def v7_day():
    s = SVG(1000, 420, "v7 the first day")
    header(s, "v7  The first day of running: the machine asks about everything, and every answer is a label",
           "Estimated hours [calc wave2 s8]. About 25 crimps, 5 of them cut open and pulled.")
    blocks = [("doctor", 0.5, "#eaeef2"), ("calibrate", 0.75, "#eaeef2"), ("reference strokes", 0.5, "#f6f0ff"),
              ("dry lay-ins", 0.75, "#ddf4ff"), ("5 scrap crimps, ask all", 1.0, "#fff0f6"),
              ("cut, measure, pull", 0.75, "#fff8c5"), ("lunch; thresholds 2", 0.75, "#eaeef2"),
              ("five 4P ends, 20 crimps", 1.5, "#dafbe1"), ("insert, test", 0.75, "#eaeef2"), ("report", 0.25, "#fff0f6")]
    x0, y0, W = 20, 110, 960
    total = sum(b[1] for b in blocks)
    x = x0
    for i, (lab, h, col) in enumerate(blocks):
        w = W * h / total
        s.rect(x, y0, w, 50, fill=col, rx=3)
        yy = y0 + 72 + (i % 2) * 18
        s.line(x + w / 2, y0 + 50, x + w / 2, yy - 12, stroke=GREY)
        s.text(x + w / 2, yy, lab, size=10.5, anchor="middle")
        x += w
    for hh in range(0, 8):
        xx = x0 + W * hh / total
        if hh <= total:
            s.text(xx, y0 - 8, f"{hh} h", size=10, anchor="middle", fill=DARK)
    s.lines(20, 250, ["What is checked before anything crimps: every device found by name; the MCU's heartbeat and e-stop loop;",
                      "the load cell's zero and noise; focus walked upward once; fiducials and the gauge pin give px/mm.",
                      "Reference strokes with an empty nest and with a contact but no wire set the floor of the force envelope.",
                      "The first crimps are scrap: each gate and after-picture is shown to Derek, then the crimp is cut open, micrometered",
                      "and pulled. Those five are the first labels. Thresholds 2 come from them; the day's real crimps are the simplest end",
                      "type (4P into XHP-4: J3, J5, J9, J11, J13). Insertion stays by hand until the crimp side is trusted."],
            size=11.2, fill=DARK, gap=17)
    s.save("w2-v7-first-day.svg")


# ------------------------------------------------------------------ v8 tack, look, crimp
def v8():
    s = SVG(1000, 700, "v8 tack, look, then crimp")
    header(s, "v8  Tack, look, then crimp: a light watched station pins the contact; the heavy crimp comes after",
           "Schematic side elevations, wire axis left to right, box at the right. Not to scale.")
    # station T
    s.rect(20, 70, 470, 370, fill="#ffffff", stroke=GREY, rx=8)
    s.text(35, 92, "Station T: tack (light, printed frame, steel former and anvil insert)", size=12, weight="bold")
    s.rect(60, 330, 400, 30, fill="#24292f")
    s.text(260, 350, "nest: box slot + lance relief; steel insert under the insulation barrel", size=10.5, anchor="middle", fill="#ffffff")
    # contact
    s.rect(330, 300, 70, 30, fill="#c9d1d9")            # box
    s.text(365, 294, "box", size=10.5, anchor="middle")
    s.rect(265, 318, 55, 12, fill="#c9d1d9")            # conductor barrel floor
    s.poly([(265, 318), (268, 296), (274, 318)], fill="#c9d1d9")
    s.poly([(314, 318), (317, 296), (320, 318)], fill="#c9d1d9")
    s.rect(205, 318, 45, 12, fill="#c9d1d9")            # insulation barrel
    # wire
    s.line(60, 300, 205, 300, stroke="#24292f", sw=12)
    s.line(205, 306, 248, 306, stroke="#24292f", sw=12)
    s.line(248, 311, 300, 311, stroke="#9aa4ae", sw=4)
    # key
    s.poly([(60, 280), (190, 283), (190, 294), (60, 292)], fill="#ddf4ff")
    s.text(90, 274, "key: hold-down", size=10.5)
    # former
    s.rect(210, 150, 20, 150, fill="#afb8c1")
    s.line(220, 120, 220, 170, stroke=FORCE, sw=3, arrow="force")
    s.text(240, 106, "former: 1.2-1.5 mm steel, C's insulation", size=10.5, fill=FORCE)
    s.text(240, 120, "profile 0.1-0.2 mm wider; stop at C's", size=10.5, fill=FORCE)
    s.text(240, 134, "final insulation height + 0.2-0.5 mm;", size=10.5, fill=FORCE)
    s.text(240, 148, "33-132 N, 35 kg.cm servo on a 1:1 lever", size=10.5, fill=FORCE)
    # top camera over conductor barrel
    s.camera(292, 200, ang=90)
    s.line(292, 222, 292, 292, stroke=VIEW, dash="4 3", arrow="view")
    s.text(310, 210, "top camera, straight down:", size=10.5, fill=VIEW)
    s.text(310, 224, "open U, strands, edge in window,", size=10.5, fill=VIEW)
    s.text(310, 238, "LEDs at 60-75 deg: the shadow test", size=10.5, fill=VIEW)
    s.text(60, 400, "cam 2 across at wing height (as v1), backlight far side", size=10.5, fill=VIEW)
    s.text(60, 418, "20 kg load cell under the nest insert: forming curve only", size=10.5, fill=DARK)
    # station C
    s.rect(510, 70, 470, 370, fill="#ffffff", stroke=GREY, rx=8)
    s.text(525, 92, "Station C: a host that takes a tacked contact", size=12, weight="bold")
    s.rect(560, 330, 380, 30, fill="#24292f")
    s.text(750, 350, "seat: floor ledge and front stop; set down from above", size=10.5, anchor="middle", fill="#ffffff")
    s.rect(820, 300, 70, 30, fill="#c9d1d9")
    s.rect(755, 318, 55, 12, fill="#c9d1d9")
    s.rect(695, 318, 45, 12, fill="#c9d1d9")
    s.line(560, 300, 695, 300, stroke="#24292f", sw=12)
    s.line(695, 306, 740, 306, stroke="#24292f", sw=12)
    s.line(740, 311, 790, 311, stroke="#9aa4ae", sw=4)
    s.rect(690, 150, 130, 100, fill="#afb8c1")
    s.line(755, 118, 755, 150, stroke=FORCE, sw=3, arrow="force")
    s.text(700, 200, "punch: both barrels", size=10.5)
    s.text(700, 214, "insulation re-formed", size=10.5)
    s.lines(530, 384, ["fed from the pallet: a narrow punch (<= 7.45 mm): a4c's one-nest",
                       "SN die set, or f3's knee with f9's keyed nest. SN-2549 as sold:",
                       "the ribbon leaves the pallet (a6c, foot or hand). Strip on an",
                       "applicator: the tack moves to its anvil (v9)."], size=10.5, fill=DARK)
    s.line(490, 250, 510, 250, arrow="ink")
    s.text(500, 240, "carry", size=10, anchor="middle")
    # stroke diagram
    y0 = 500
    s.text(20, y0 - 10, "The stroke at C after a tack, remaining ram travel (mm) [calc w3_final s1, clone dimensions]", size=12, weight="bold")
    xa, xb = 120, 900
    def X(mm): return xa + (1.5 - mm) / 1.5 * (xb - xa)
    s.line(xa, y0 + 110, xb, y0 + 110, stroke=INK)
    for mm in (1.5, 1.2, 0.9, 0.6, 0.3, 0.0):
        s.line(X(mm), y0 + 106, X(mm), y0 + 114)
        s.text(X(mm), y0 + 130, f"{mm:.1f}", size=10, anchor="middle")
    s.rect(X(0.50), y0 + 10, X(0.20) - X(0.50), 22, fill="#ddf4ff", stroke=VIEW)
    s.text(X(0.50) - 6, y0 + 26, "insulation crimper meets the tacked barrel", size=10.5, anchor="end")
    s.rect(X(0.87), y0 + 42, X(0.62) - X(0.87), 22, fill="#fff8c5", stroke=AMBER)
    s.text(X(0.87) - 6, y0 + 58, "conductor wings first touched", size=10.5, anchor="end")
    s.rect(X(0.2), y0 + 74, X(0.0) - X(0.2), 22, fill="#ffebe9", stroke=BAD)
    s.text(X(0.2) - 6, y0 + 90, "compaction: the force", size=10.5, anchor="end")
    s.lines(20, y0 + 160, ["After a tack the conductor wings are met first and curl for 0.12-0.67 mm before the insulation crimper retouches;",
                           "the tack holds the jacket through compaction. The pause after the tack is where the camera looks straight down",
                           "into the open barrel. A failed look slides the loose tack off the tip: it costs a contact, not a ribbon end."],
            size=11, fill=DARK, gap=16)
    s.save("w2-v8-tack-look-crimp.svg")


if __name__ == "__main__":
    v1_lifted(); v5_roll(); v7_stack(); v7_day(); v8()
