"""Schematic sketches for ribbon-as-pallet: a1, a2, a3 (redrawn), a7, a8, a2e, a1c.
Run: python3 make_sketches_w2.py   (writes the .svg files beside this script)
All drawings are schematic. Where a scale is stated it is for proportion only.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

class Svg:
    def __init__(self, w, h, title, sub):
        self.w, self.h = w, h
        self.parts = []
        self.parts.append(f'<rect width="{w}" height="{h}" fill="#ffffff"/>')
        self.parts.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" '
                          'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                          '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker></defs>')
        self.text(20, 26, title, size=16, weight="bold")
        self.text(20, 44, sub, fill="#a33")

    def rect(self, x, y, w, h, fill="#eee", stroke="#555", sw=1, dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke="#333", sw=1, dash=None, arrow=False, arrow_both=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#ar)"' if arrow else ""
        if arrow_both:
            m = ' marker-start="url(#ar)" marker-end="url(#ar)"'
        self.parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}{m}/>')

    def circle(self, cx, cy, r, fill="#eee", stroke="#555", sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def poly(self, pts, fill="#ccc", stroke="#555", sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.parts.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def path(self, d, fill="none", stroke="#333", sw=1, dash=None):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd}/>')

    def text(self, x, y, s, size=12, fill="#222", weight="normal", anchor="start"):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
                          f'font-weight="{weight}" text-anchor="{anchor}">{s}</text>')

    def lines(self, x, y, rows, size=11, fill="#222", dy=14):
        for i, r in enumerate(rows):
            self.text(x, y + i * dy, r, size=size, fill=fill)

    def save(self, name):
        body = "\n  ".join(self.parts)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
               f'width="{self.w}" height="{self.h}" font-family="Helvetica, Arial, sans-serif" '
               f'font-size="12">\n  {body}\n</svg>\n')
        with open(os.path.join(HERE, name), "w") as f:
            f.write(svg)

SILICONE = "#3a3a3a"
SIL_LIGHT = "#6b6b6b"
COPPER = "#c98a3b"
BRASS = "#e6c36a"
BRASS_S = "#8a6500"
STEEL = "#b8c0c8"
BLUE = "#dbe9f6"
BLUE_S = "#2a5a8a"
TPU = "#9fd39a"

# ---------------------------------------------------------------------------
def a7():
    s = Svg(1000, 700, "a7 Zip station: tear each web along its own neck, stop it at the clamp",
            "schematic, not to scale except panel B (1 mm = 20 px); the neck thickness t_n is unmeasured")
    # Panel A plan
    s.text(20, 74, "A. Plan: the pallet drives the ribbon tip-first into the nicker, then onto the wedge comb",
           weight="bold")
    s.rect(30, 100, 190, 150, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.rect(150, 110, 70, 130, fill="#9db7d2", stroke=BLUE_S)
    s.lines(36, 120, ["pallet", "(clamp lid", "hatched)"], fill=BLUE_S)
    s.text(150, 262, "lid front face =", fill=BLUE_S, size=11)
    s.text(150, 276, "split root = tear stop", fill=BLUE_S, size=11)
    # conductors: 5 at 17 px pitch webbed until x=220, then parted and fanned by tines
    y0 = 141
    xs_root = 220
    pitch_r = 17
    for k in range(5):
        y = y0 + k * pitch_r
        s.line(100, y, xs_root, y, stroke=SILICONE, sw=15)
    # parted & fanned section
    import math
    for k in range(5):
        off = (k - 2)
        yr = y0 + k * pitch_r
        yf = 175 + off * 25  # 2.5 mm pitch at the tine roots (scaled 10 px/mm)
        s.path(f"M{xs_root},{yr} C{xs_root+60},{yr} {xs_root+80},{yf} {xs_root+180},{yf} L{xs_root+330},{yf}",
               stroke=SILICONE, sw=15)
    # tines (between conductors): noses at x=232 between rows, roots at x=400
    for k in range(4):
        yn = y0 + (k + 0.5) * pitch_r
        yr_ = 175 + (k - 1.5) * 25
        s.poly([(232, yn), (400, yr_ - 3), (400, yr_ + 3)], fill=STEEL, stroke="#556")
    s.rect(400, 100, 30, 150, fill=STEEL, stroke="#556")
    s.line(415, 252, 440, 272, stroke="#556")
    s.lines(444, 280, ["wedge comb: tines of laminated stainless, 0.2 mm blunt nose -> 0.8 mm root,",
                       "noses at 1.7 mm pitch, roots at 2.5 mm, staggered 2 mm so one web starts at a time"], size=11)
    # nicker (drawn ahead, sprung away)
    s.rect(640, 120, 26, 110, fill="#f4f4f4", stroke="#777", dash="4 3")
    for k in range(4):
        yn = y0 + (k + 0.5) * pitch_r
        s.line(640, yn, 610, yn, stroke="#556", sw=2)
    s.lines(672, 132, ["nicker: 0.10 mm razor slivers", "on flexures, V-noses find the",
                       "valleys; 2 mm nick into the tip,", "then springs aside"], size=11)
    s.line(40, 320, 150, 320, arrow=True)
    s.text(160, 324, "pallet moves +X (stage or hand rail)", size=11)
    s.text(232, 92, "tear front stays ~1 mm ahead of the noses", size=11, fill="#a33")
    s.line(236, 96, 236, 132, stroke="#a33", dash="3 2")
    s.text(560, 252, "tip region (removed later by the flush cut)", size=11, fill="#666")

    # Panel B cross-section
    s.text(20, 360, "B. Cross-section of a 5P: pitch = OD, so jackets meet at the valley planes", weight="bold")
    S = 20
    cy = 460
    x_start = 80
    for k in range(5):
        cx = x_start + 17 + k * 34
        s.circle(cx, cy, 17, fill=SILICONE, stroke="#111")
        s.circle(cx, cy, 7.2, fill=COPPER, stroke="#7a4a10")
    # neck fill (schematic)
    for k in range(4):
        vx = x_start + 34 + k * 34
        s.poly([(vx - 3, cy - 5), (vx + 3, cy - 5), (vx + 3, cy + 5), (vx - 3, cy + 5)], fill=SIL_LIGHT, stroke="none")
        s.line(vx, cy - 30, vx, cy + 30, stroke="#a33", dash="3 2")
    s.text(x_start - 40, cy + 50, "valley planes (dashed): where the tear should run", size=11, fill="#a33")
    s.lines(330, 420, ["neck t_n (lighter): fused silicone at the valley, thickness unknown",
                       "jacket wall at the equator: ~0.49 mm; strand bundle 0.72 mm",
                       "silicone between two bundles on the mid-plane: 0.98 mm",
                       "",
                       "tear path by energy [calc W2 s2]:",
                       "  t_n / wall < ~0.6  -> the tear stays in the neck (zips)",
                       "  ~0.6-1.0           -> marginal, may wander",
                       "  >= 1.0             -> wanders into a jacket: cut instead (a7b)"], size=11)

    # Panel C: detail of the tine in the split near the clamp
    s.text(20, 560, "C. Detail near the clamp: the copper hinges at the crack tip, so the tear stops where the tines stop",
           weight="bold")
    s.rect(40, 580, 120, 90, fill="#9db7d2", stroke=BLUE_S)
    s.text(46, 598, "clamp lid", fill=BLUE_S, size=11)
    s.line(40, 610, 160, 610, stroke=SILICONE, sw=15)
    s.line(40, 640, 160, 640, stroke=SILICONE, sw=15)
    s.rect(155, 617, 20, 16, fill=SIL_LIGHT, stroke="none")
    s.path("M160,610 C190,610 200,604 330,590", stroke=SILICONE, sw=15)
    s.path("M160,640 C190,640 200,646 330,660", stroke=SILICONE, sw=15)
    s.poly([(186, 625), (330, 617), (330, 633)], fill=STEEL, stroke="#556")
    s.line(175, 596, 175, 655, stroke="#a33", dash="3 2")
    s.text(340, 600, "crack tip ~1 mm ahead of the blunt nose [estimate]", size=11, fill="#a33")
    s.text(340, 616, "under the lid the conductors cannot open, so the tear stops at the face", size=11)
    s.text(340, 632, "tines steel and isolated: a tear that reaches copper reads on the far-end port", size=11)
    s.text(340, 648, "backlight under the open pallet floor: every split is a bright slit to the camera", size=11)
    s.save("a7-zip-station.svg")

# ---------------------------------------------------------------------------
def a8():
    s = Svg(1000, 720, "a8 Rolling ring scorer: the row spins in place under two fixed blades",
            "schematic; panel A at 1 mm = 20 px vertically, lengths compressed; score radius 0.58-0.63 mm")
    s.text(20, 74, "A. Section along one conductor", weight="bold")
    bed_y = 250
    s.rect(30, bed_y, 760, 16, fill=STEEL, stroke="#556")
    s.text(36, bed_y + 30, "steel bed: the radial reference (conductor axis = bed + OD/2)", size=11)
    # fan block
    s.rect(30, 150, 120, 100, fill=BLUE, stroke=BLUE_S)
    s.text(38, 170, "fan block", fill=BLUE_S, size=11)
    s.text(38, 184, "(pallet)", fill=BLUE_S, size=11)
    # conductor
    top = bed_y - 34
    s.rect(150, top, 470, 34, fill=SILICONE, stroke="#111")
    s.rect(150, top + 10, 540, 14, fill=COPPER, stroke="#7a4a10")
    # stripped stub region beyond strip line at x=620
    s.rect(620, top, 70, 34, fill="#ffffff", stroke="none")
    s.rect(620, top + 10, 70, 14, fill=COPPER, stroke="#7a4a10")
    # stop bar
    s.rect(690, 150, 22, 100, fill=STEEL, stroke="#556")
    s.lines(718, 160, ["stop bar (grounded):", "every tip touches it;", "the far-end port reads", "each conductor's touch"], size=11)
    # blades
    s.poly([(612, 120), (628, 120), (620, top + 5)], fill="#dde", stroke="#334")
    s.poly([(612, bed_y + 16), (628, bed_y + 16), (620, bed_y - 5)], fill="#dde", stroke="#334")
    s.text(560, 112, "top blade to a depth stop", size=11)
    s.text(380, bed_y + 50, "bottom blade up through a bed slot", size=11)
    # pads
    s.rect(470, top - 18, 120, 18, fill=TPU, stroke="#3a7a35")
    s.rect(470, bed_y - 2, 120, 4, fill=TPU, stroke="#3a7a35")
    s.text(470, top - 24, "TPU pads on racks, moving in opposite X", size=11, fill="#3a7a35")
    s.line(620, 300, 690, 300, arrow_both=True)
    s.text(700, 304, "strip length: one steel part (stop bar to blades), 2.4 mm", size=11)
    s.rect(630, bed_y, 58, 16, fill="#e8f4ff", stroke="#88a")
    s.text(160, 340, "clear window + LED under the stubs: one backlit frame of the row after the pull", size=11)

    s.text(20, 370, "B. End view across the row: two pads moving equal and opposite spin every conductor about its own axis",
           weight="bold")
    base = 520
    s.rect(60, base, 420, 12, fill=TPU, stroke="#3a7a35")
    s.rect(60, base - 72, 420, 12, fill=TPU, stroke="#3a7a35")
    for k in range(5):
        cx = 110 + k * 80
        s.circle(cx, base - 30, 30, fill=SILICONE, stroke="#111")
        s.circle(cx, base - 30, 12, fill=COPPER, stroke="#7a4a10")
        s.path(f"M{cx-18},{base-54} A30,30 0 0 1 {cx+18},{base-54}", stroke="#ffffff", sw=1.5)
    s.line(300, base - 90, 420, base - 90, arrow=True)
    s.line(300, base + 26, 180, base + 26, arrow=True)
    s.text(430, base - 86, "top pad +X", size=11)
    s.text(90, base + 30, "bottom pad -X", size=11)
    # rack and pinion schematic
    s.circle(560, base - 30, 22, fill="#fff", stroke="#333")
    s.line(520, base - 52, 620, base - 52, sw=3)
    s.line(520, base - 8, 620, base - 8, sw=3)
    s.lines(630, base - 60, ["one pinion between two racks:", "equal and opposite by construction",
                             "0.6 turn of each conductor",
                             "= +/-1.6 mm of pad travel,", "then back"], size=11)
    s.text(60, base + 60, "at housing pitch there is 0.8 mm between jackets, so neighbours never rub", size=11)

    s.text(20, 610, "C. The ring the blades leave", weight="bold")
    cx, cy = 110, 665
    s.circle(cx, cy, 42, fill=SILICONE, stroke="#111")
    s.circle(cx, cy, 30, fill="none", stroke="#ffcc33", sw=2, dash="4 2")
    s.circle(cx, cy, 18, fill=COPPER, stroke="#7a4a10")
    s.lines(170, 640, ["score to radius 0.58-0.63 mm (yellow): 0.22-0.27 mm deep in a 0.49 mm wall",
                       "ligament 0.22-0.27 mm left to tear: 2.6-9.2 N per conductor on the pull [calc W2 s4]",
                       "budget: bundle 0.37 + loose strand 0.04 + eccentricity 0.05-0.10 + axis height 0.05",
                       "        + setting 0.02 + 0.05 clear",
                       "blades isolated: a touch on copper stops the pinion and names the conductor"], size=11)
    s.save("a8-rolling-ring-scorer.svg")

# ---------------------------------------------------------------------------
def a2e():
    s = Svg(1000, 700, "a2e Docked strip through a feedless applicator (a2 x borrowed-machines b1b)",
            "schematic, not to scale; strip pitch ~7.1 mm (Wurth analog); parts marked dashed are removed")
    s.text(20, 74, "A. Plan: the carriage carries the carrier segment and the docked ribbon pallet along X", weight="bold")
    # rail
    s.rect(40, 330, 900, 12, fill=STEEL, stroke="#556")
    s.text(44, 358, "MGN12 rail + Tr8x2 NEMA 17: one X axis, load position upstream (right)", size=11)
    # applicator footprint
    s.rect(300, 90, 220, 160, fill="#eeeeee", stroke="#555")
    s.text(306, 106, "OTP side-feed applicator (on the VEVOR bed,", size=11)
    s.text(306, 120, "under b1b's slow crank)", size=11)
    ax = 410
    s.rect(ax - 8, 150, 16, 40, fill="#888", stroke="#333")
    s.text(ax - 22, 144, "anvil", size=11)
    # removed parts
    s.rect(440, 190, 70, 26, fill="none", stroke="#a33", dash="4 3")
    s.rect(440, 160, 70, 26, fill="none", stroke="#a33", dash="4 3")
    s.rect(ax - 10, 196, 20, 20, fill="none", stroke="#a33", dash="4 3")
    s.line(510, 165, 560, 100, stroke="#a33", dash="2 2")
    s.lines(564, 86, ["removed (dashed): pressure plate and feed finger upstream,",
                      "shear punch at the station"], size=10, fill="#a33")
    # carrier segment: contacts at pitch 50 px, from x=... row positioned with contact 1 at anvil
    pitch = 50
    x_first = ax
    n = 5
    xs = [x_first + i * pitch for i in range(-2, n + 2)]
    s.rect(xs[0] - 20, 222, xs[-1] - xs[0] + 40, 16, fill=BRASS, stroke=BRASS_S)
    for i, x in enumerate(xs):
        s.rect(x - 7, 160, 14, 62, fill=BRASS, stroke=BRASS_S)
        s.circle(x, 230, 4, fill="#fff", stroke=BRASS_S)
    # end grips on spares
    for x in (xs[0], xs[-1]):
        s.rect(x - 12, 226, 24, 10, fill="#555", stroke="#222")
    s.text(660, 268, "end grips (dark): pins in the spare contacts' holes", size=10)
    # ribbon pallet docked: conductors from contacts toward -Y (down)
    s.rect(ax - 40, 260, 280, 60, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(ax - 36, 312, "ribbon pallet, fanned to strip pitch, seated on three balls", size=10, fill=BLUE_S)
    for i in range(n):
        x = ax + i * pitch
        s.line(x, 172, x, 262, stroke=SILICONE, sw=9)
        s.line(x, 162, x, 180, stroke=COPPER, sw=4)
    # loading shelf
    s.rect(560, 150, 300, 90, fill="none", stroke="#3a7a35", dash="5 3")
    s.text(600, 146, "loading shelf, flush with the track (load position)", size=10, fill="#3a7a35")
    # downstream unknown zone
    s.rect(180, 150, 120, 90, fill="#fbeaea", stroke="#a33", dash="4 3")
    s.lines(184, 166, ["downstream: crimped", "contacts on their", "carrier pass here,", "up to 4 pitches;",
                       "room unknown", "until scanned"], size=10, fill="#a33")
    s.line(760, 300, 660, 300, arrow=True)
    s.text(680, 318, "index -X one strip pitch per crank turn", size=11)

    s.text(20, 400, "B. Section at the anvil, one crank turn per contact", weight="bold")
    # crank
    s.circle(200, 450, 26, fill="#fff", stroke="#333")
    s.circle(215, 450, 4, fill="#333")
    s.line(215, 450, 205, 540, sw=4)
    s.rect(180, 540, 50, 30, fill=STEEL, stroke="#556")
    s.text(240, 460, "NEMA 23 + 10:1, ~10 s per turn;", size=11)
    s.text(240, 474, "strain gauges on the rod: ~19 samples through compaction", size=11)
    s.rect(185, 570, 40, 40, fill="#999", stroke="#333")
    s.text(236, 596, "crimpers (conductor, insulation) and dials", size=11)
    s.rect(120, 632, 180, 10, fill=BRASS, stroke=BRASS_S)
    s.rect(180, 642, 50, 30, fill="#888", stroke="#333")
    s.text(236, 660, "anvil (fixed): the reference for the stroke", size=11)
    s.line(60, 626, 300, 626, stroke=SILICONE, sw=10)
    s.text(40, 618, "conductor already in the barrels (docked)", size=11)
    s.lines(560, 440, ["Before each stroke:", "  continuity conductor-to-carrier (far-end port)",
                       "  camera: strands in, insulation edge in the window",
                       "During: force curve, stop-before-bottom",
                       "After the row: 20 N pull per conductor at the fan block face,",
                       "  then the shear comb cuts every tab at the load position",
                       "",
                       "Person per ribbon end: snip N+4 contacts, lay them on the shelf,",
                       "  seat the ribbon pallet, press start (~2 min machine time per 5P)"], size=11)
    s.save("a2e-docked-strip-feedless-applicator.svg")

# ---------------------------------------------------------------------------
def a1c():
    s = Svg(1000, 560, "a1c Crimp from the upstream end, fold each finished conductor back (a1 x borrowed-machines b1)",
            "schematic, not to scale; crimp pitch p_c set by the applicator's downstream tooling width")
    s.text(20, 74, "Plan: the fan lies flat in the anvil plane, all of it downstream of the anvil", weight="bold")
    ax = 520
    # strip from the right
    s.rect(ax - 10, 120, 440, 14, fill=BRASS, stroke=BRASS_S)
    for i in range(0, 7):
        x = ax + i * 55
        s.rect(x - 7, 134, 14, 50, fill=BRASS, stroke=BRASS_S)
    s.text(ax + 120, 112, "reel strip from upstream (+X), feed intact; next contact waits on the anvil", size=11)
    s.rect(ax - 12, 184, 24, 16, fill="#888", stroke="#333")
    s.text(ax - 40, 214, "anvil", size=11)
    # fork
    s.rect(ax - 16, 225, 32, 18, fill=STEEL, stroke="#556")
    s.text(ax + 22, 238, "fork on the applicator axis (b1): folds the crimped conductor back", size=11)
    # pallet
    s.rect(80, 300, 600, 180, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.text(86, 470, "pallet on the XY stage; lid face = split root; fan block grooves flat", size=11, fill=BLUE_S)
    # flat fan: active conductor at anvil x=ax, uncrimped at ax-50*k
    for k in range(0, 4):
        x = ax - 60 * k
        root_x = 330 + (ax - 330) * 0.15 - 20 * k
        s.path(f"M{root_x:.0f},330 C{root_x:.0f},290 {x},280 {x},200", stroke=SILICONE, sw=9)
        s.line(x, 184, x, 204, stroke=COPPER, sw=4)
    s.text(90, 250, "uncrimped conductors, flat, downstream (-X)", size=11)
    # folded back crimped ones on pallet top to the right
    for k in range(1, 3):
        x = ax + 50 * k + 10
        s.path(f"M{x},330 L{x},420", stroke=SILICONE, sw=9)
        s.rect(x - 7, 420, 14, 22, fill=BRASS, stroke=BRASS_S)
    s.text(ax + 40, 460, "crimped, folded back over the pallet into numbered pockets", size=11)
    s.line(700, 520, 800, 520, arrow=True)
    s.text(810, 524, "index +X one p_c per conductor", size=11)
    s.lines(730, 300, ["per conductor:", "1 slide in +Y along the barrels' axis",
                       "2 sole seats it level (Repair B)", "3 crank: crimp, shear, PAUSE",
                       "4 stage backs out -Y 10 mm", "5 crank finishes: feed",
                       "6 fork folds it back", "7 index +X"], size=11)
    s.save("a1c-upstream-first-park-after.svg")


# ---------------------------------------------------------------------------
def a1():
    s = Svg(1000, 700, "a1 Pallet tour: one clamp, one stage, a fixed strip-fed crimp station",
            "schematic, not to scale; dimensions in the idea file")
    s.text(20, 74, "A. Plan: the pallet visits fixed stations and carries no motor", weight="bold")
    names = [("1 zip", "(a7)"), ("2 fan", "press"), ("3 flush", "cut"), ("4 strip", "(a8)"),
             ("5 crimp:", "applicator in"), ("6 insert", "(a6)")]
    for i, (a, b) in enumerate(names):
        x = 40 + i * 120
        s.rect(x, 90, 100, 60, fill="#eeeeee", stroke="#555")
        s.text(x + 50, 112, a, size=11, anchor="middle")
        s.text(x + 50, 126, b, size=11, anchor="middle")
    s.text(570, 140, "b1b slow crank", size=11, anchor="middle")
    s.text(760, 106, "SXH reel feeds from the side", size=11)
    s.text(760, 120, "(feed plates upstream: the", size=11)
    s.text(760, 134, "open conflict with h)", size=11)
    s.rect(200, 220, 260, 120, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.rect(200, 220, 70, 120, fill="#9db7d2", stroke=BLUE_S)
    s.text(206, 238, "lid", fill=BLUE_S, size=11)
    s.text(206, 252, "face =", fill=BLUE_S, size=11)
    s.text(206, 266, "split root", fill=BLUE_S, size=11)
    s.rect(300, 230, 90, 100, fill="#c9dcef", stroke=BLUE_S)
    s.text(304, 246, "fan block", fill=BLUE_S, size=11)
    s.text(304, 260, "1.7 -> 5.0 mm", fill=BLUE_S, size=11)
    s.text(304, 274, "held at h ~5 mm", fill=BLUE_S, size=11)
    for k in range(5):
        y = 245 + k * 18
        s.rect(390, y - 4, 40, 8, fill="#7fa6cc", stroke=BLUE_S)
        s.line(430, y, 470, y, stroke=SILICONE, sw=6)
        s.line(470, y, 480, y, stroke=COPPER, sw=3)
    s.text(436, 360, "tongues (one per groove)", size=11, fill=BLUE_S)
    s.line(160, 400, 160, 350, arrow=True)
    s.line(160, 400, 210, 400, arrow=True)
    s.text(150, 346, "+Y", size=11)
    s.text(214, 404, "+X   XY stage", size=11)
    s.text(500, 250, "order: part, fan, then flush-cut and strip at the tongue lips,", size=11)
    s.text(500, 264, "because the fan pulls a 5P's outer tips back 1.65 mm [calc W2 s3]", size=11)
    s.text(500, 290, "far end: pogo test port on the cut face (a6)", size=11)

    s.text(20, 450, "B. Side section at station 5: the tongue lays the active conductor in; the crank pauses before the feed",
           weight="bold")
    # fan block and tongue
    s.rect(40, 480, 140, 60, fill="#c9dcef", stroke=BLUE_S)
    s.text(46, 498, "fan block (pallet)", fill=BLUE_S, size=11)
    s.line(180, 510, 200, 510, stroke=SILICONE, sw=10)
    s.poly([(180, 504), (300, 556), (300, 572), (180, 520)], fill="#7fa6cc", stroke=BLUE_S)
    s.rect(300, 556, 30, 16, fill="#7fa6cc", stroke=BLUE_S)
    s.path("M180,510 L300,562 L330,562", stroke=SILICONE, sw=10)
    s.line(330, 562, 420, 562, stroke=SILICONE, sw=10)
    s.line(420, 562, 470, 562, stroke=COPPER, sw=5)
    s.text(40, 600, "tongue: hinged at the block face, covered groove, lip turns the conductor level;", size=11, fill=BLUE_S)
    s.text(40, 614, "a fixed cam at the station presses it down 5 mm and releases it on index,", size=11, fill=BLUE_S)
    s.text(40, 628, "so it lifts the crimped conductor back to h", size=11, fill=BLUE_S)
    s.poly([(250, 470), (290, 470), (280, 530)], fill="#f1d9a8", stroke="#8a6500")
    s.text(296, 486, "station cam (fixed)", size=11)
    # contact on anvil
    s.rect(380, 567, 110, 8, fill=BRASS, stroke=BRASS_S)
    s.rect(420, 575, 60, 30, fill="#888", stroke="#333")
    s.text(496, 596, "anvil = zero", size=11)
    s.rect(420, 500, 60, 50, fill="#999", stroke="#333")
    s.text(496, 520, "crimpers on the ram (b1b crank, ~10 s per turn)", size=11)
    s.text(496, 534, "crank pauses after the crimpers clear and before the", size=11)
    s.text(496, 548, "feed moves; the stage backs out -Y in that pause", size=11)
    s.text(40, 660, "Cost: any 5-6 mm drop adds 10-12 mm of parted length (tongue, moved-back block or ram sole alike) [calc W2 s7].",
           size=11)
    s.text(40, 676, "Open: how high the applicator's feed plates stand upstream, under the neighbours held at h (borrowed-machines Break a1-2).",
           size=11, fill="#a33")
    s.save("a1-pallet-tour.svg")

# ---------------------------------------------------------------------------
def a2():
    s = Svg(1000, 640, "a2 Two pallets meet: the carrier strip is the contact pallet",
            "schematic, not to scale; strip pitch ~7.1 mm (Wurth analog; JST's figure is licence-gated)")
    s.text(20, 74, "A. Plan, after docking: every conductor already lies in its contact", weight="bold")
    s.rect(120, 150, 420, 110, fill="#eee", stroke="#555")
    s.text(548, 162, "strip pallet (steel): slot pins locate the carrier;", size=11)
    s.text(548, 176, "comb clamp bar between conductor paths;", size=11)
    s.text(548, 190, "hardened rail flush with the contacts' floor (grey band)", size=11)
    s.rect(120, 110, 420, 12, fill="#aab", stroke="#556")
    s.text(560, 120, "rail for the head's lower arm (Z from the strip pallet)", size=11)
    s.rect(140, 222, 380, 16, fill=BRASS, stroke=BRASS_S)
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
    s.text(206, 396, "ribbon pallet: fan block at strip pitch, flush-cut and stripped at its face;", size=11, fill=BLUE_S)
    s.text(206, 410, "three balls seat in dowel V-grooves on the strip pallet, magnets pull it home", size=11, fill=BLUE_S)
    s.rect(262, 80, 36, 60, fill="#bbb", stroke="#333")
    s.text(560, 86, "C-frame head (borrowed-machines b3): harvested OTP crimper and anvil,", size=11)
    s.text(560, 100, "NEMA 17 + 10:1 on a 3 mm crank, ~3.8 kN, ~1 kg; arms <= 10 mm wide", size=11)
    s.line(262, 148, 212, 148, arrow=True)
    s.line(298, 148, 348, 148, arrow=True)
    s.text(20, 460, "B. Side: the head straddles one contact from the box end", weight="bold")
    s.rect(80, 500, 16, 90, fill="#999", stroke="#333")
    s.rect(80, 500, 160, 16, fill="#999", stroke="#333")
    s.rect(80, 574, 160, 16, fill="#999", stroke="#333")
    s.rect(200, 516, 30, 20, fill="#777", stroke="#333")
    s.rect(200, 556, 30, 18, fill="#777", stroke="#333")
    s.text(440, 528, "upper die (crimper) over the wings", size=11)
    s.text(250, 570, "lower die on the rail", size=11)
    s.rect(180, 538, 170, 8, fill=BRASS, stroke=BRASS_S)
    s.line(230, 532, 420, 532, stroke=SILICONE, sw=10)
    s.rect(330, 546, 60, 10, fill=BRASS, stroke=BRASS_S)
    s.text(400, 556, "carrier on slot pins", size=11)
    s.text(40, 616, "Then: 20 N pull per conductor at the fan block face; a notched shear comb cuts every tab; lift; close to 2.5 mm; insert (a6).",
           size=11)
    s.save("a2-two-pallets-meet.svg")

# ---------------------------------------------------------------------------
def a3():
    s = Svg(1000, 600, "a3 The backshell that ships: the clamp is applied once and never removed",
            "schematic, not to scale; J4 SENSORS (4P + 3P into XHP-7) shown")
    s.text(20, 74, "A. Side section of the backshell: the ribbon folds 180 deg around a bar (the IDC strain-relief fold)",
           weight="bold")
    s.rect(120, 110, 160, 90, fill=BLUE, stroke=BLUE_S, sw=1.5)
    s.circle(250, 155, 14, fill="#9db7d2", stroke=BLUE_S)
    s.path("M40,135 L250,135 A20,20 0 0 1 250,175 L120,175", stroke=SILICONE, sw=9)
    s.path("M250,141 L420,141", stroke=SILICONE, sw=9)
    s.rect(120, 100, 160, 14, fill="#9db7d2", stroke=BLUE_S)
    s.text(126, 96, "snap cover", fill=BLUE_S, size=11)
    s.line(280, 90, 280, 220, stroke="#a33", dash="3 2")
    s.text(286, 216, "front face = split root", size=11, fill="#a33")
    s.text(40, 128, "loom", size=11)
    s.text(430, 145, "to fan and housing", size=11)
    s.lines(600, 110, ["a wrap multiplies the cover's hold by e^(mu pi):",
                       "4.8x at mu 0.5, 23x at mu 1.0",
                       "3 N on the tail resists 14-69 N of loom pull",
                       "[borrowed-machines exchange calc s8]",
                       "",
                       "outer faces: the machine's datum",
                       "top: embossed name; edge: notch code = recipe"], size=11)
    s.text(20, 290, "B. Height above the board with the backshell at the split root [borrowed-machines calc s7]", weight="bold")
    s.rect(40, 520, 300, 14, fill="#5c8a3a", stroke="#333")
    s.text(46, 552, "main board, vertical XH wafer", size=11)
    s.rect(140, 480, 60, 40, fill="#eee", stroke="#555")
    s.text(206, 504, "XHP mated ~9.8 mm", size=11)
    s.line(170, 480, 170, 380, stroke=SILICONE, sw=9)
    s.rect(130, 350, 80, 30, fill=BLUE, stroke=BLUE_S)
    s.text(216, 370, "backshell ~12 mm", size=11)
    rows = [("fold-back parking (C5)", "8-15 mm", "30-37 mm"),
            ("housing fan only", "14-18 mm", "36-40 mm"),
            ("a2, 7 mm strip pitch, per ribbon", "21-30 mm", "43-52 mm"),
            ("a1, 5 mm crimp pitch", "20-35 mm", "42-57 mm")]
    s.text(420, 330, "parting", size=11, weight="bold")
    s.text(660, 330, "parted", size=11, weight="bold")
    s.text(760, 330, "top above board", size=11, weight="bold")
    for i, (a, b, c) in enumerate(rows):
        y = 352 + i * 20
        s.text(420, y, a, size=11)
        s.text(660, y, b, size=11)
        s.text(760, y, c, size=11)
    s.text(420, 460, "Arms variant: two bridge arms hook the XHP's end flanges (~0.8 mm each side);", size=11)
    s.text(420, 474, "whether they clear the wafer shroud is untested.", size=11)
    s.save("a3-backshell-that-ships.svg")

if __name__ == "__main__":
    a7(); a8(); a2e(); a1c(); a1(); a2(); a3()
    print("wrote a1, a2, a3, a7, a8, a2e, a1c sketches")
