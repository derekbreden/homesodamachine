"""Schematic sketches for the machine-that-sees-and-learns explorer.

Run: python3 make_sketches.py   (writes the .svg files beside this script)

Every drawing here is schematic: proportions are chosen to be read, not measured.
"""
from pathlib import Path

HERE = Path(__file__).parent
INK = "#1f2328"
GREY = "#8c959f"
LIGHT = "#eaeef2"
DARK = "#57606a"
VIEW = "#0969da"      # camera views and light
FORCE = "#bc4c00"     # force path
GOOD = "#1a7f37"
BAD = "#cf222e"


class SVG:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'font-family="Helvetica, Arial, sans-serif">',
            f'<title>{title}</title>',
            '<defs>'
            f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
            f'<marker id="arrv" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{VIEW}"/></marker>'
            f'<marker id="arrf" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{FORCE}"/></marker>'
            '</defs>',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
        ]

    def rect(self, x, y, w, h, fill=LIGHT, stroke=INK, sw=1.5, rx=0, dash=None, opacity=1):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{sw}"{d} opacity="{opacity}"/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.5, dash=None, arrow=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow:
            mk = {"ink": "arr", "view": "arrv", "force": "arrf"}[arrow]
            m = f' marker-end="url(#{mk})"'
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" '
                          f'stroke-width="{sw}"{d}{m}/>')

    def poly(self, pts, fill=LIGHT, stroke=INK, sw=1.5, closed=True, dash=None):
        p = " ".join(f"{x},{y}" for x, y in pts)
        tag = "polygon" if closed else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        f = fill if closed else "none"
        self.parts.append(f'<{tag} points="{p}" fill="{f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill=LIGHT, stroke=INK, sw=1.5):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="normal", italic=False):
        st = ' font-style="italic"' if italic else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
                          f'font-weight="{weight}"{st}>{s}</text>')

    def lines(self, x, y, rows, size=12, fill=INK, anchor="start", gap=None, weight="normal"):
        gap = gap or size + 3
        for i, r in enumerate(rows):
            self.text(x, y + i * gap, r, size=size, fill=fill, anchor=anchor, weight=weight)

    def camera(self, x, y, ang=0, label=None):
        # a small camera body with lens, rotated by ang degrees about (x, y)
        self.parts.append(f'<g transform="rotate({ang} {x} {y})">'
                          f'<rect x="{x-16}" y="{y-11}" width="26" height="22" rx="3" fill="{DARK}" stroke="{INK}"/>'
                          f'<rect x="{x+10}" y="{y-6}" width="9" height="12" fill="{GREY}" stroke="{INK}"/>'
                          '</g>')
        if label:
            self.text(x, y - 16, label, size=11, anchor="middle", fill=VIEW)

    def save(self, name):
        self.parts.append("</svg>")
        (HERE / name).write_text("\n".join(self.parts))
        print("wrote", name)


def header(s, title, sub):
    s.text(20, 28, title, size=17, weight="bold")
    s.text(20, 47, sub, size=12, fill=DARK, italic=True)


# ---------------------------------------------------------------- v1 watched nest
def v1():
    s = SVG(980, 640, "v1 the watched nest")
    header(s, "v1  The watched nest: a fixed press that is photographed at every step",
           "Schematic side elevation, wire axis left to right. Not to scale.")
    # press C-frame
    s.poly([(560, 80), (760, 80), (760, 470), (560, 470), (560, 420), (720, 420), (720, 130), (560, 130)],
           fill="#d0d7de")
    s.text(740, 100, "press frame", size=11, anchor="end")
    # ram + punch
    s.rect(610, 130, 40, 150, fill="#afb8c1")
    s.rect(622, 280, 16, 40, fill=DARK)
    s.text(655, 200, "ram, slow", size=11)
    s.text(655, 214, "(any drive the", size=11)
    s.text(655, 228, "force explorers", size=11)
    s.text(655, 242, "develop)", size=11)
    s.text(645, 300, "punch", size=11)
    s.line(630, 140, 630, 175, stroke=FORCE, sw=2.5, arrow="force")
    # anvil + load cell
    s.rect(600, 375, 60, 45, fill="#24292f")
    s.text(596, 395, "anvil, blackened", size=11, anchor="end")
    s.text(596, 409, "(stray strand = bright line)", size=10, anchor="end", fill=DARK)
    s.rect(605, 420, 50, 12, fill="#f6c177")
    s.text(662, 432, "load cell", size=11, fill=FORCE)
    # contact in nest
    s.rect(615, 360, 32, 15, fill="#c9d1d9")
    s.poly([(615, 360), (619, 348), (623, 360)], fill="#c9d1d9")
    s.poly([(628, 360), (632, 350), (636, 360)], fill="#c9d1d9")
    s.text(650, 356, "contact, barrels up", size=11)
    # conductor + pallet + stage
    s.line(300, 352, 560, 352, stroke="#24292f", sw=7)
    s.line(560, 352, 612, 355, stroke="#24292f", sw=7)
    s.line(612, 355, 640, 356, stroke="#9aa4ae", sw=3)
    s.text(380, 330, "active conductor, pressed down by its key", size=11)
    s.rect(300, 335, 70, 36, fill="#ddf4ff")
    s.text(335, 390, "fan block: keys, neighbours 5 mm up", size=11, anchor="middle")
    s.rect(270, 395, 140, 30, fill=LIGHT)
    s.text(340, 415, "X Y Z stage", size=12, anchor="middle", weight="bold")
    s.line(410, 410, 450, 410, arrow="ink"); s.text(455, 414, "Y", size=11)
    s.line(340, 425, 340, 455, arrow="ink"); s.text(346, 452, "Z", size=11)
    s.circle(258, 410, 6, fill="#fff"); s.text(248, 414, "X (into page)", size=11, anchor="end")
    # hold-down finger
    s.line(560, 300, 600, 346, stroke=DARK, sw=3)
    s.text(470, 296, "piano key tip = hold-down and pull grip", size=11)
    # cameras
    s.camera(470, 205, ang=35, label="cam 1: oblique, under the raised punch")
    s.line(485, 220, 610, 350, stroke=VIEW, dash="5 4", arrow="view")
    # backlight behind the nest, in the far plane
    s.rect(590, 330, 80, 40, fill="none", stroke="#9a6700", dash="4 3")
    # lighting ring note, kept clear of the ram
    s.text(250, 110, "LEDs round the nest, lit one at a time; two at 60-75 deg:", size=11, fill=VIEW)
    s.text(250, 124, "a strand lying on the barrel floor casts no displaced shadow", size=10, fill=DARK)
    # end-view inset: camera 2 and its backlight on opposite sides of the nest
    ix, iy = 790, 110
    s.rect(ix, iy, 175, 200, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ix + 87, iy + 18, "end view, along the wire", size=11, anchor="middle", weight="bold")
    s.rect(ix + 60, iy + 120, 55, 40, fill="#24292f")
    s.poly([(ix + 70, iy + 120), (ix + 66, iy + 95), (ix + 76, iy + 120)], fill="#c9d1d9")
    s.poly([(ix + 105, iy + 120), (ix + 109, iy + 95), (ix + 99, iy + 120)], fill="#c9d1d9")
    s.circle(ix + 87, iy + 108, 9, fill="#24292f")
    s.camera(ix + 22, iy + 105, ang=0)
    s.text(ix + 12, iy + 80, "cam 2", size=11, fill=VIEW)
    s.rect(ix + 150, iy + 70, 12, 70, fill="#fff8c5", stroke="#9a6700")
    s.line(ix + 42, iy + 105, ix + 145, iy + 105, stroke=VIEW, dash="4 3")
    s.text(ix + 87, iy + 178, "backlight on the far side:", size=10, anchor="middle", fill="#9a6700")
    s.text(ix + 87, iy + 191, "strands vs wing tips in silhouette", size=10, anchor="middle", fill="#9a6700")
    # silhouette window + proof pull
    s.rect(430, 470, 120, 40, fill="#fff8c5", stroke="#9a6700")
    s.text(490, 494, "silhouette window", size=11, anchor="middle")
    s.text(490, 525, "gauge pin in the same frame", size=10, anchor="middle", fill=DARK)
    s.line(260, 490, 190, 490, stroke=FORCE, sw=2.5, arrow="force")
    s.text(195, 480, "proof pull ~20 N by the stage's Y", size=11, fill=FORCE)
    s.text(195, 508, "reaction: carrier tab + box hold-down (strip), or a lance-notched plate (loose)", size=10, fill=DARK)
    # sequence strip
    y0 = 555
    s.text(20, y0 - 8, "What the log keeps for every crimp (one picture or trace per box):", size=12, weight="bold")
    boxes = ["contact seated", "tip on backlight", "servo converged", "laid in: top + side",
             "force-stroke curve", "after: side silhouette", "after: top view", "during proof pull"]
    for i, b in enumerate(boxes):
        x = 20 + i * 120
        s.rect(x, y0, 110, 40, fill="#f6f8fa", rx=4)
        s.text(x + 55, y0 + 25, b, size=10.5, anchor="middle")
        if i < len(boxes) - 1:
            s.line(x + 110, y0 + 20, x + 120, y0 + 20, arrow="ink")
    s.text(20, 625, "Reference for fixed: the image. Contact, conductor and anvil fiducials are measured in one frame; "
           "the stage is steered by the picture, not by its own step count.", size=11, fill=DARK)
    s.save("v1-watched-nest.svg")


# ---------------------------------------------------------------- v2 arm and docks
def v2():
    s = SVG(980, 600, "v2 arm taught by demonstration")
    header(s, "v2  An arm taught by Derek's hands carries the work; docks and stations do the precision",
           "Schematic plan view of the bench. Not to scale.")
    cx, cy = 470, 340
    s.circle(cx, cy, 34, fill="#d0d7de")
    s.text(cx, cy + 5, "SO-101", size=12, anchor="middle", weight="bold")
    s.parts.append(f'<path d="M {cx-230} {cy} A 230 230 0 0 1 {cx+230} {cy}" fill="none" stroke="{GREY}" '
                   f'stroke-dasharray="4 5"/>')
    s.text(cx, cy - 238, "reach ~ the arm's working circle", size=10, anchor="middle", fill=DARK)
    stations = [
        (-160, "split + strip", "dock + blade stations"),
        (-115, "watched nest (v1)", "dock on a 2-axis micro stage"),
        (-65, "inspection (v5)", "dock in the booth"),
        (-20, "housing nest", "comb guide at 2.5 mm"),
    ]
    import math
    for ang, name, sub in stations:
        a = math.radians(ang)
        x = cx + 230 * math.cos(a)
        y = cy + 230 * math.sin(a)
        s.rect(x - 70, y - 26, 140, 52, fill="#ddf4ff", rx=6)
        s.text(x, y - 5, name, size=12, anchor="middle", weight="bold")
        s.text(x, y + 12, sub, size=10.5, anchor="middle", fill=DARK)
        s.line(cx + 36 * math.cos(a), cy + 36 * math.sin(a), x - 60 * math.cos(a), y - 24 * math.sin(a),
               stroke=GREY, dash="3 4")
    # tail tray
    s.rect(cx - 330, cy + 60, 200, 60, fill="#fff8c5", stroke="#9a6700", rx=6)
    s.text(cx - 230, cy + 85, "finished-loom tray", size=12, anchor="middle")
    s.text(cx - 230, cy + 102, "XH end first: tails coil on the pallet", size=10.5, anchor="middle", fill=DARK)
    # leader arm and Derek
    s.rect(cx + 250, cy + 60, 190, 70, fill="#f6f8fa", rx=6)
    s.text(cx + 345, cy + 85, "leader arm", size=12, anchor="middle", weight="bold")
    s.text(cx + 345, cy + 102, "Derek demonstrates; takes over", size=10.5, anchor="middle", fill=DARK)
    s.text(cx + 345, cy + 117, "when a check fails (DAgger)", size=10.5, anchor="middle", fill=DARK)
    # tip clip inset
    ix, iy = 40, 470
    s.rect(ix, iy, 360, 115, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ix + 10, iy + 18, "pallet (what the arm actually holds)", size=12, weight="bold")
    s.rect(ix + 20, iy + 40, 150, 40, fill="#ddf4ff")
    s.line(ix + 170, iy + 60, ix + 250, iy + 60, stroke="#24292f", sw=7)
    s.line(ix + 250, iy + 60, ix + 275, iy + 60, stroke="#9aa4ae", sw=3)
    s.circle(ix + 45, iy + 90, 7, fill=DARK); s.text(ix + 58, iy + 94, "ball", size=10)
    s.circle(ix + 103, iy + 90, 7, fill=DARK); s.text(ix + 115, iy + 94, "ball", size=10)
    s.circle(ix + 148, iy + 90, 7, fill=DARK); s.text(ix + 160, iy + 94, "ball", size=10)
    s.text(ix + 285, iy + 50, "conductor ~6 mm", size=10, fill=DARK)
    s.text(ix + 285, iy + 63, "proud of the clip", size=10, fill=DARK)
    s.text(ix + 190, iy + 95, "steel balls on dowel-pin pairs; magnet", size=10, fill=DARK)
    s.lines(430, 520, ["Tip wander ~1.2 mm RSS approached one way, ~6 mm if not;",
                       "funnels >= 5 mm lead-in; the station's stage and camera do the last 0.2 mm.",
                       "Cameras: one on the wrist and one overhead feed the policy;",
                       "the station cameras judge whether each step worked."], size=11, fill=DARK)
    s.save("v2-arm-docks.svg")


# ---------------------------------------------------------------- v3 experiment loop
def v3():
    s = SVG(980, 560, "v3 the press that runs its own experiments")
    header(s, "v3  The press that runs its own experiments",
           "Schematic loop. The chart is axes only: every point on it is still to be measured.")
    steps = [
        ("choose a set point", "crimp height (bottom stop),", "insertion depth, contact lot"),
        ("crimp", "force vs ram position", "recorded every 10 ms"),
        ("photograph", "side silhouette: CH, bellmouth,", "brush; top: width, seam, strays"),
        ("pull to failure", "peak N and the mode:", "pull-out or wire break"),
        ("fit and decide", "pull force vs CH, image vs", "pull: where is the window?"),
    ]
    x0, y0, w, h, gap = 30, 90, 170, 80, 22
    for i, (a, b, c) in enumerate(steps):
        x = x0 + i * (w + gap)
        s.rect(x, y0, w, h, fill="#ddf4ff" if i != 4 else "#dafbe1", rx=8)
        s.text(x + w / 2, y0 + 24, a, size=13, anchor="middle", weight="bold")
        s.text(x + w / 2, y0 + 45, b, size=10.5, anchor="middle", fill=DARK)
        s.text(x + w / 2, y0 + 60, c, size=10.5, anchor="middle", fill=DARK)
        if i < len(steps) - 1:
            s.line(x + w, y0 + h / 2, x + w + gap, y0 + h / 2, arrow="ink")
    # return arrow
    s.poly([(x0 + 4 * (w + gap) + w / 2, y0 + h), (x0 + 4 * (w + gap) + w / 2, y0 + h + 40),
            (x0 + w / 2, y0 + h + 40), (x0 + w / 2, y0 + h + 4)], fill="none", closed=False)
    s.line(x0 + w / 2, y0 + h + 12, x0 + w / 2, y0 + h + 2, arrow="ink")
    s.text(470, y0 + h + 34, "next set point: a fixed grid, or the supervisor zooms in where the pull force changes fastest",
           size=11, anchor="middle", fill=DARK)
    # labels feeding the judge
    s.rect(30, 260, 420, 110, fill="#fff8c5", stroke="#9a6700", rx=8)
    s.lines(45, 285, ["Every destroyed test crimp labels its own pictures:",
                      "the pull result says whether the image of that crimp",
                      "showed a good crimp. The non-destructive checks in",
                      "production (v1, v5) are tuned on these labels, and",
                      "Claude's few-shot examples are drawn from them."], size=11.5)
    # chart axes
    ox, oy, cw, ch = 540, 500, 390, 210
    s.line(ox, oy, ox + cw, oy, arrow="ink")
    s.line(ox, oy, ox, oy - ch, arrow="ink")
    s.text(ox + cw, oy + 36, "conductor crimp height, mm", size=11, anchor="end")
    s.text(ox - 8, oy - ch + 5, "pull N", size=11, anchor="end")
    for i, v in enumerate([0.70, 0.80, 0.90, 1.00]):
        x = ox + 20 + i * 115
        s.line(x, oy, x, oy + 5); s.text(x, oy + 18, f"{v:.2f}", size=10, anchor="middle")
    ythr = oy - 90
    s.line(ox, ythr, ox + cw - 10, ythr, stroke=BAD, dash="6 4")
    s.text(ox + cw - 10, ythr - 6, "39.2 N, JST minimum at 22 AWG [mfr]", size=10.5, anchor="end", fill=BAD)
    ywb = oy - 175
    s.line(ox, ywb, ox + cw - 10, ywb, stroke=GREY, dash="2 4")
    s.text(ox + cw - 10, ywb - 6, "~85-100 N, the wire itself breaks [source]", size=10.5, anchor="end", fill=DARK)
    for i in range(16):
        x = ox + 20 + i * 23
        s.circle(x, oy - 130, 3, fill="#ffffff", stroke=GREY)
    s.text(ox + 200, oy - 140, "16 set points x 5 crimps, results unknown", size=10.5, anchor="middle", fill=DARK)
    s.text(ox + 200, oy - 60, "the window is where the lower tail clears 39.2 N", size=10.5, anchor="middle", fill=DARK)
    s.text(ox + 200, oy - 46, "and the pictures also pass", size=10.5, anchor="middle", fill=DARK)
    s.text(30, 410, "Instruments: height by a stop, shim stack, hit-and-re-touch or crank angle; die gap by a 0.001 mm indicator; force by a load cell",
           size=11, fill=DARK)
    s.text(30, 426, "in the force path (rod gauges on an applicator); pull on a soldered lug or bare-copper wrap; camera at the silhouette window.", size=11, fill=DARK)
    s.text(30, 452, "~153 test crimps, ~8 h unattended, ~$2 of contacts; coupons are production-made 5P ends [calc/campaign.out.txt].",
           size=11, fill=DARK)
    s.save("v3-experiment-loop.svg")


# ---------------------------------------------------------------- v4 tap look pick
def v4():
    s = SVG(980, 560, "v4 tap look pick")
    header(s, "v4  Tap, look, pick: loose contacts from a lit tray into the nest",
           "Schematic side elevation with a plan-view inset of what the camera sees. Not to scale.")
    # tray + LED
    s.rect(120, 330, 300, 12, fill="#f6f8fa")
    s.text(112, 340, "frosted tray (diffuser)", size=11, anchor="end")
    s.rect(120, 350, 300, 14, fill="#fff8c5", stroke="#9a6700")
    s.text(270, 380, "LED panel: contacts read as black shapes", size=11, anchor="middle", fill="#9a6700")
    for i in range(3):
        s.line(150 + i * 120, 364, 150 + i * 120, 410, stroke=DARK, sw=2)
    s.text(140, 425, "flexure legs", size=10.5, fill=DARK)
    s.rect(420, 395, 50, 26, fill="#d0d7de")
    s.text(445, 440, "tapper", size=11, anchor="middle")
    s.text(445, 454, "(solenoid / voice coil)", size=10, anchor="middle", fill=DARK)
    s.line(420, 400, 420, 350, stroke=FORCE, sw=2, arrow="force")
    # contacts on tray
    for (x, w, h) in ((160, 22, 8), (215, 8, 22), (250, 22, 10), (330, 20, 8), (375, 10, 20)):
        s.rect(x, 330 - h, w, h, fill="#c9d1d9")
    # camera
    s.camera(270, 120, ang=90, label="ELP, looking down")
    s.line(270, 145, 200, 318, stroke=VIEW, dash="5 4")
    s.line(270, 145, 340, 318, stroke=VIEW, dash="5 4")
    s.text(60, 210, "two exposures per tap:", size=10.5, fill=VIEW)
    s.text(60, 224, "backlight only -> outline;", size=10.5, fill=VIEW)
    s.text(60, 238, "top light only -> the open U", size=10.5, fill=VIEW)
    # nozzle and nest
    s.rect(560, 150, 18, 120, fill="#d0d7de")
    s.poly([(563, 270), (575, 270), (571, 290), (567, 290)], fill=DARK)
    s.rect(560, 290, 22, 10, fill="#c9d1d9")
    s.text(590, 200, "pick head on the stage Z", size=11)
    s.text(590, 214, "(bellows cup or tilt-cut face: the box top", size=10.5, fill=DARK)
    s.text(590, 228, "sits 11-17 deg on its lance; sensor confirms)", size=10.5, fill=DARK)
    s.line(569, 140, 569, 110, arrow="ink"); s.line(560, 120, 480, 120, arrow="ink")
    s.rect(640, 330, 120, 40, fill="#24292f")
    s.rect(682, 318, 36, 12, fill="#c9d1d9")
    s.text(700, 390, "nest on the anvil (v1)", size=11, anchor="middle")
    s.text(700, 404, "camera checks: seated, level", size=10.5, anchor="middle", fill=DARK)
    # inset
    ix, iy = 40, 470
    s.rect(ix, iy - 10, 900, 80, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ix + 10, iy + 8, "what the software sorts after each tap (plan view, backlit):", size=12, weight="bold")
    shapes = [(("barrels up, box", "forward: pick"), GOOD), (("barrels up, wrong", "heading: rotate or wait"), "#9a6700"),
              (("on its side:", "tap again"), DARK), (("barrels down:", "tap again"), DARK),
              (("two touching or", "tangled: tap harder"), BAD)]
    for i, (lab, col) in enumerate(shapes):
        x = ix + 20 + i * 178
        s.rect(x, iy + 22, 40, 12, fill="#24292f")
        s.rect(x + 40, iy + 19, 16, 18, fill="#24292f")
        s.text(x + 66, iy + 26, lab[0], size=10.5, fill=col)
        s.text(x + 66, iy + 40, lab[1], size=10.5, fill=col)
    s.save("v4-tap-look-pick.svg")


# ---------------------------------------------------------------- v5 booth
def v5():
    s = SVG(980, 540, "v5 inspection booth")
    header(s, "v5  The inspection booth: look and pull after any crimp, hand-made or machine-made",
           "Schematic side elevation (wire left to right) with an end-view inset. Not to scale.")
    s.rect(60, 380, 640, 20, fill="#d0d7de")
    # backlight panel in the far plane, behind the V-block
    s.rect(400, 250, 170, 110, fill="#fffbe6", stroke="#9a6700", dash="5 4")
    s.text(485, 244, "backlight panel, far side", size=10.5, anchor="middle", fill="#9a6700")
    # mirror above, seen face on
    s.rect(430, 150, 120, 30, fill="#ddf4ff", stroke=VIEW)
    s.text(490, 140, "45 deg mirror above the crimp", size=10.5, anchor="middle", fill=VIEW)
    # blackened block with blade support and stop
    s.rect(420, 330, 120, 50, fill="#24292f")
    s.rect(540, 318, 10, 62, fill=DARK)
    s.text(556, 330, "lance-notched stop behind the box", size=11)
    s.text(420, 420, "blackened block, blade support, roll flat; gauge pin beside; box read as roll gauge", size=11)
    # crimped conductor
    s.line(180, 336, 470, 336, stroke="#24292f", sw=7)
    s.rect(470, 330, 68, 12, fill="#c9d1d9")
    # clamp + pull
    s.rect(250, 316, 40, 40, fill="#ddf4ff")
    s.text(270, 370, "clamp", size=11, anchor="middle")
    s.line(245, 336, 170, 336, stroke=FORCE, sw=2.5, arrow="force")
    s.rect(100, 316, 60, 40, fill="#f6c177")
    s.text(130, 305, "motor + load cell", size=11, anchor="middle", fill=FORCE)
    s.text(130, 290, "proof pull ~20 N", size=11, anchor="middle", fill=FORCE)
    s.text(300, 460, "camera: in front of the page, looking in (see inset)", size=11, fill=VIEW)
    # end-view inset
    ix, iy = 720, 200
    s.rect(ix, iy, 240, 230, fill="#ffffff", stroke=GREY, rx=6)
    s.text(ix + 120, iy + 18, "end view, along the wire", size=11, anchor="middle", weight="bold")
    s.rect(ix + 95, iy + 150, 50, 40, fill="#24292f")
    s.circle(ix + 120, iy + 142, 9, fill="#c9d1d9")
    s.camera(ix + 30, iy + 142, ang=0)
    s.text(ix + 15, iy + 118, "camera", size=10.5, fill=VIEW)
    s.rect(ix + 210, iy + 105, 12, 70, fill="#fff8c5", stroke="#9a6700")
    s.line(ix + 50, iy + 142, ix + 205, iy + 142, stroke=VIEW, dash="4 3")
    s.line(ix + 95, iy + 60, ix + 145, iy + 100, stroke=VIEW, sw=3)
    s.line(ix + 50, iy + 136, ix + 118, iy + 80, stroke=VIEW, dash="2 3")
    s.line(ix + 120, iy + 80, ix + 120, iy + 130, stroke=VIEW, dash="2 3")
    s.text(ix + 150, iy + 70, "mirror", size=10.5, fill=VIEW)
    s.text(ix + 120, iy + 208, "side silhouette + top view,", size=10, anchor="middle", fill=DARK)
    s.text(ix + 120, iy + 221, "one frame, two focus settings", size=10, anchor="middle", fill=DARK)
    # readout
    s.rect(720, 60, 240, 100, fill="#f6f8fa", rx=6)
    s.lines(732, 82, ["J4 pin 3  crimp 212", "CH 0.87 mm   width 1.52", "bellmouth yes  brush 0.3",
                      "window: insulation 50/50", "proof 20 N: no slip   PASS"], size=11)
    s.text(840, 175, "(illustrative readout, not data)", size=10, anchor="middle", fill=DARK, italic=True)
    s.lines(60, 490, ["Modes: a crimp dropped in by the person after the hand tool; the verify station of any machine;",
                      "the finished housing on a board wafer, continuity pin by pin and a picture of the mating face."],
            size=11.5, fill=DARK)
    s.save("v5-inspection-booth.svg")


# ---------------------------------------------------------------- v6 look act look
def v6():
    s = SVG(980, 600, "v6 the patient cell")
    header(s, "v6  The patient cell: every act is bracketed by a look, and a doubt goes to a queue",
           "Schematic flow for one conductor. Each station is a function with a picture before and after.")
    stations = [("load", "person: ribbon in pallet,", "flush cut; tail coiled"),
                ("split", "blade plunged at the root,", "drawn out to the tip"),
                ("twist + strip", "die-hole blades at the", "contact's length; twist-pull"),
                ("place + crimp", "v1, v8 tack + crimp,", "or v9 at an applicator"),
                ("inspect + pull", "v5 in line", "log the crimp"),
                ("insert", "housing on the wire axis;", "push, latch seen in window")]
    x0, y0, w, h, gap = 20, 95, 145, 70, 12
    for i, (a, b, c) in enumerate(stations):
        x = x0 + i * (w + gap)
        s.rect(x, y0, w, h, fill="#ddf4ff" if i else "#fff8c5", rx=8)
        s.text(x + w / 2, y0 + 22, a, size=13, anchor="middle", weight="bold")
        s.text(x + w / 2, y0 + 42, b, size=10.5, anchor="middle", fill=DARK)
        s.text(x + w / 2, y0 + 56, c, size=10.5, anchor="middle", fill=DARK)
        if i < len(stations) - 1:
            s.line(x + w, y0 + h / 2, x + w + gap, y0 + h / 2, arrow="ink")
    # detail of one station loop
    bx, by = 150, 250
    s.text(bx - 130, by - 12, "Inside every station:", size=13, weight="bold")
    loop = [("look", "is the precondition true?"), ("act", "one motion or one stroke"),
            ("look", "did it do what it should?"), ("decide", "accept / retry / back out / ask")]
    for i, (a, b) in enumerate(loop):
        x = bx + i * 190
        s.rect(x, by, 160, 56, fill="#f6f8fa", rx=6)
        s.text(x + 80, by + 22, a, size=13, anchor="middle", weight="bold")
        s.text(x + 80, by + 40, b, size=10.5, anchor="middle", fill=DARK)
        if i < 3:
            s.line(x + 160, by + 28, x + 190, by + 28, arrow="ink")
    # outcomes
    outs = [("accept", GOOD, "next station"), ("retry", "#9a6700", "same act, new attempt (max 2-3)"),
            ("back out", DARK, "undo: lift, re-strip, re-seat"), ("ask", BAD, "park it, photo to the queue, next conductor")]
    s.line(bx + 3 * 190 + 80, by + 56, bx + 3 * 190 + 80, by + 78, stroke=GREY, dash="3 3")
    s.line(560, by + 78, bx + 3 * 190 + 80, by + 78, stroke=GREY, dash="3 3")
    for i, (a, col, b) in enumerate(outs):
        y = by + 100 + i * 32
        s.text(560, y, a, size=12, weight="bold", fill=col)
        s.text(640, y, b, size=11, fill=DARK)
    s.rect(20, 360, 470, 120, fill="#ffffff", stroke=GREY, rx=6)
    s.lines(34, 384, ["Per conductor ~3-7.5 min; per unit ~3-6.6 h unattended [calc].",
                      "Person: cut and load 14 ribbon ends (~15-30 min), load contacts",
                      "and housings, answer the queue.",
                      "The queue holds a photo, the station, what was measured and",
                      "what the machine proposes; Derek answers from the phone or",
                      "the bench, and the answer becomes a labelled example."], size=11.5)
    s.text(20, 560, "Irreversible acts (the crimp, the lance catching in the housing) get the strictest look before them;",
           size=11, fill=DARK)
    s.text(20, 576, "everything before the crimp can be undone; a bad crimp costs a ~6-10 mm cut-back of the whole ribbon end.",
           size=11, fill=DARK)
    s.save("v6-look-act-look.svg")


if __name__ == "__main__":
    v1(); v2(); v3(); v4(); v5(); v6()
