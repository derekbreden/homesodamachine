"""Schematic sketches for the terminal-supply explorer (jst-crimp-study, wave 1).

Run:  python3 make_sketches.py     (writes the .svg files beside this script)

Contact, strip and housing proportions follow the clone drawings and the Wurth
analog cited in ../calc/terminal_supply.py; everything else is schematic.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1d2430"
MID = "#5b6675"
LIGHT = "#c9d0da"
METAL = "#8a6d2f"      # bronze contact
METAL_F = "#e8d7a8"
WIRE = "#222222"
CU = "#c26a2e"
STEEL = "#6f7c8c"
STEEL_F = "#d7dde5"
PRINT = "#2f7d6d"     # printed parts
PRINT_F = "#cfe8e1"
ACCENT = "#b3342b"
HOUS_F = "#f4f1e8"


class Svg:
    def __init__(self, w, h, title):
        self.w, self.h = w, h
        self.el = []
        self.title = title

    def add(self, s):
        self.el.append(s)

    def rect(self, x, y, w, h, stroke=INK, fill="none", sw=1.2, dash=None, rx=0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        r = f' rx="{rx}"' if rx else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{r} '
                 f'stroke="{stroke}" fill="{fill}" stroke-width="{sw}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=1.2, dash=None, arrow=False):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arr)"' if arrow else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                 f'stroke-width="{sw}"{d}{m}/>')

    def poly(self, pts, stroke=INK, fill="none", sw=1.2, close=True, dash=None):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        tag = "polygon" if close else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<{tag} points="{p}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, stroke=INK, fill="none", sw=1.2):
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" stroke="{stroke}" fill="{fill}" '
                 f'stroke-width="{sw}"/>')

    def path(self, d, stroke=INK, fill="none", sw=1.2, dash=None, arrow=False):
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arr)"' if arrow else ""
        self.add(f'<path d="{d}" stroke="{stroke}" fill="{fill}" stroke-width="{sw}"{dd}{m}/>')

    def text(self, x, y, s, size=12, color=INK, anchor="start", weight="normal", italic=False):
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        st = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
                 f'text-anchor="{anchor}" font-weight="{weight}"{st}>{s}</text>')

    def lines(self, x, y, rows, size=12, color=INK, lh=None, anchor="start"):
        lh = lh or size * 1.3
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size, color, anchor)

    def save(self, name):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" font-family="Helvetica, Arial, sans-serif">\n'
                f'<title>{self.title}</title>\n'
                '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/>'
                '</marker>'
                '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
                'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#8b96a5" '
                'stroke-width="1"/></pattern></defs>\n'
                f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="#ffffff"/>\n')
        with open(os.path.join(HERE, name), "w") as f:
            f.write(head + "\n".join(self.el) + "\n</svg>\n")
        print("wrote", name)


# ------------------------------------------------------------------ shapes
def contact_plan(s, x0, y0, k, dirn=1, crimped=False, wire=False, label=None):
    """Top view of an open contact, rear (tab end) at y0, pointing +y*dirn. k = px/mm."""
    segs = [  # (length, width, kind)
        (1.4, 2.8, "ib"), (0.4, 1.0, "win"), (1.4, 1.85, "cb"), (0.6, 1.2, "tr"), (2.0, 1.85, "box")]
    y = y0
    for L, W, kind in segs:
        if crimped and kind == "ib":
            W = 1.95
        if crimped and kind == "cb":
            W = 1.5
        h = L * k * dirn
        top = min(y, y + h)
        fill = METAL_F if kind != "box" else "#f0e2b8"
        s.rect(x0 - W * k / 2, top, W * k, abs(h), stroke=METAL, fill=fill, sw=1)
        if kind in ("ib", "cb") and not crimped:
            s.line(x0 - W * k / 2 + 2, top + 1, x0 - W * k / 2 + 2, top + abs(h) - 1, stroke=METAL, sw=0.6)
            s.line(x0 + W * k / 2 - 2, top + 1, x0 + W * k / 2 - 2, top + abs(h) - 1, stroke=METAL, sw=0.6)
        y += h
    if wire:
        # insulated wire comes from the rear, conductor into the conductor barrel
        ins_end = y0 + 1.6 * k * dirn
        s.rect(x0 - 0.85 * k, min(y0 - 30 * dirn, ins_end), 1.7 * k, abs(ins_end - (y0 - 30 * dirn)),
               stroke=WIRE, fill="#3a3a3a", sw=0.8)
        cu_end = y0 + 3.4 * k * dirn
        s.rect(x0 - 0.36 * k, min(ins_end, cu_end), 0.72 * k, abs(cu_end - ins_end), stroke=CU, fill=CU, sw=0.6)
    if label:
        s.text(x0, y + 14 * dirn + (4 if dirn > 0 else 0), label, 10, MID, "middle")
    return y


def contact_side(s, x0, y_floor, k, dirn=1, crimped=False, lance=True, carrier_mm=0.0, outline=True):
    """Side view, rear at x0, front toward +x*dirn; floor plane at y_floor (y up is -).
    Barrels drawn as outlines so a wire inside them stays visible."""
    L = 5.8
    x_end = x0 + L * k * dirn
    s.line(x0 - carrier_mm * k * dirn, y_floor, x_end, y_floor, stroke=METAL, sw=2.4)
    ih = 1.9 if crimped else 3.0
    ch = 0.95 if crimped else 1.5
    bf = "none" if outline else METAL_F
    s.rect(min(x0, x0 + 1.4 * k * dirn), y_floor - ih * k, 1.4 * k, ih * k, stroke=METAL, fill=bf, sw=1.6)
    xc = x0 + 1.8 * k * dirn
    s.rect(min(xc, xc + 1.4 * k * dirn), y_floor - ch * k, 1.4 * k, ch * k, stroke=METAL, fill=bf, sw=1.6)
    xb = x0 + 3.8 * k * dirn
    s.rect(min(xb, xb + 2.0 * k * dirn), y_floor - 2.3 * k, 2.0 * k, 2.3 * k, stroke=METAL, fill="#f0e2b8", sw=1.2)
    if lance:
        xl0 = x0 + 4.2 * k * dirn
        xl1 = x0 + 3.3 * k * dirn
        s.line(xl0, y_floor, xl1, y_floor + 0.8 * k, stroke=METAL, sw=1.4)
    return x_end


def wire_side(s, x_from, x_ins_end, x_cu_end, y_axis, k, sw=1):
    s.rect(min(x_from, x_ins_end), y_axis - 0.85 * k, abs(x_ins_end - x_from), 1.7 * k,
           stroke=WIRE, fill="#3a3a3a", sw=sw)
    s.rect(min(x_ins_end, x_cu_end), y_axis - 0.36 * k, abs(x_cu_end - x_ins_end), 0.72 * k,
           stroke=CU, fill=CU, sw=0.6)


def schematic_tag(s, x, y, extra=""):
    s.text(x, y, "schematic" + (" - " + extra if extra else ""), 11, MID, italic=True)


# ================================================================== a1b
def sketch_strip_indexer():
    s = Svg(1000, 860, "a2 strip indexer: the carrier as feeder, locator and handle")
    k = 12  # px per mm in plan
    s.text(20, 30, "a2  Strip indexer: the carrier strip is the feeder, the locator and the handle", 17,
           weight="bold")
    schematic_tag(s, 20, 50, "contact and strip proportions from clone drawings; pitch 7.1 mm (Wurth analog)")
    s.text(20, 82, "PLAN, looking down on the open barrels; the strip moves left to right", 12, MID, weight="bold")
    y_car_top = 160
    car_h = 3.0 * k
    x_st = 520
    P = 7.1 * k
    xs = [x_st + i * P for i in range(-6, 6)]
    xs = [x for x in xs if 150 < x < 960]
    s.rect(40, y_car_top, 920, car_h, stroke=METAL, fill=METAL_F, sw=1.2)
    for x in xs:
        s.circle(x, y_car_top + car_h / 2, 0.75 * k, stroke=METAL, fill="#ffffff", sw=1)
        s.rect(x + P / 2 - 1.25 * k, y_car_top + car_h / 2 - 0.6 * k, 2.5 * k, 1.2 * k, stroke=METAL,
               fill="#ffffff", sw=0.8)
    y_rear = y_car_top + car_h + 1.0 * k
    for x in xs:
        if x > x_st + 5:      # downstream: contact already cut away, tab stub left
            s.rect(x - 0.4 * k, y_car_top + car_h, 0.8 * k, 0.35 * k, stroke=METAL, fill=METAL_F, sw=0.8)
            continue
        s.rect(x - 0.4 * k, y_car_top + car_h, 0.8 * k, 1.0 * k, stroke=METAL, fill=METAL_F, sw=0.8)
        contact_plan(s, x, y_rear, k, 1)
    s.text(x_st + 2.0 * P, y_car_top + car_h + 30, "empty carrier, tab stubs only", 10, MID, "middle")
    # anvil/punch footprint at the station
    s.rect(x_st - 1.6 * k, y_rear - 0.2 * k, 3.2 * k, 3.4 * k, stroke=STEEL, fill="none", sw=1.6, dash="5,3")
    s.text(x_st + 1.9 * k, y_rear + 2.2 * k, "anvil + punch", 10, STEEL)
    # conductor k from behind, over the carrier
    s.rect(x_st - 0.85 * k, 88, 1.7 * k, y_rear + 1.6 * k - 88, stroke=WIRE, fill="#555555", sw=0.8)
    s.rect(x_st - 0.36 * k, y_rear + 1.6 * k, 0.72 * k, 1.8 * k, stroke=CU, fill=CU, sw=0.6)
    s.text(x_st + 16, 98, "conductor k slides in from behind, over the carrier, into the open U", 11)
    s.text(x_st + 16, 112, "(the other conductors ride ~5 mm up on a notched lifter bar; only k lies at carrier height)", 10, MID)
    # pilot pins in neighbour holes
    for x in (x_st - P, x_st + P):
        s.circle(x, y_car_top + car_h / 2, 0.72 * k, stroke=ACCENT, fill=ACCENT, sw=1)
        s.text(x, y_car_top - 8, "pilot pin", 10, ACCENT, "middle")
    # hold-down plates
    for xa, xb in ((175, x_st - P - 12), (x_st - P + 12, x_st - 16), (x_st + 16, x_st + P - 12)):
        s.rect(xa, y_car_top - 3, xb - xa, car_h + 6, stroke=PRINT, fill="url(#hatch)", sw=1)
    s.text(200, y_car_top - 8, "sprung hold-down", 10, PRINT)
    # feed wheel
    s.circle(100, y_car_top + car_h / 2, 32, stroke=PRINT, fill=PRINT_F, sw=1.2)
    s.text(100, y_car_top + car_h / 2 + 50, "pin wheel or pawl,", 10, PRINT, "middle")
    s.text(100, y_car_top + car_h / 2 + 63, "small stepper", 10, PRINT, "middle")
    s.line(40, y_car_top - 30, 120, y_car_top - 30, arrow=True)
    s.text(40, y_car_top - 36, "strip in", 10)
    s.line(900, y_car_top + car_h + 22, 975, y_car_top + car_h + 22, arrow=True)
    s.text(880, y_car_top + car_h + 42, "to take-up or", 10)
    s.text(880, y_car_top + car_h + 55, "a snip bin", 10)
    # drop shear note
    s.line(x_st + 0.6 * k, y_car_top + car_h + 0.5 * k, x_st + 90, 380, stroke=ACCENT, sw=0.8)
    s.lines(x_st + 94, 378, ["drop-shear: after the crimp the carrier downstream of the tab",
                             "is pushed down, away from the wire above; the upstream carrier",
                             "is clamped to an edge 2-3 mm upstream, so the kink goes to scrap"], 10, ACCENT, 13)
    s.lines(190, 380, ["waiting contacts: open, same pose,", "one pitch apart"], 10, MID, 13)

    # side section at the station
    s.text(20, 470, "SECTION through the station, along the contact axis (larger scale)", 12, MID,
           weight="bold")
    ys = 650
    k2 = 22
    x_rear = 360
    # track and drop plate under the carrier
    s.rect(x_rear - 4.0 * k2 - 60, ys + 2, 3.0 * k2 + 60, 30, stroke=PRINT, fill=PRINT_F, sw=1)
    s.text(x_rear - 4.0 * k2 - 55, ys + 22, "printed track", 10, PRINT)
    s.rect(x_rear - 1.05 * k2, ys + 2, 0.9 * k2, 30, stroke=ACCENT, fill="#f6d9d6", sw=1)
    s.text(x_rear - 1.05 * k2 - 4, ys + 48, "drop plate (spring)", 10, ACCENT, "end")
    # anvil
    s.rect(x_rear - 0.1 * k2, ys + 2, 3.4 * k2, 60, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(x_rear + 1.6 * k2, ys + 48, "anvil", 11, STEEL, "middle")
    # hold-down over the carrier's rear strip
    s.rect(x_rear - 4.0 * k2 - 60, ys - 11, 1.6 * k2 + 60, 9, stroke=PRINT, fill="url(#hatch)", sw=1)
    s.text(x_rear - 4.0 * k2 - 60, ys - 18, "hold-down at the carrier's far edge", 10, PRINT)
    # wire first, then the contact outline over it
    wire_side(s, x_rear - 4.0 * k2 - 170, x_rear + 1.6 * k2, x_rear + 4.0 * k2, ys - 0.85 * k2, k2)
    xe = contact_side(s, x_rear, ys, k2, 1, carrier_mm=4.0)
    s.text(x_rear - 4.0 * k2 - 170, ys - 1.9 * k2 - 6, "ribbon carriage slides conductor k in axially", 10)
    # punch
    s.rect(x_rear - 0.1 * k2, ys - 3.0 * k2 - 60, 3.4 * k2, 44, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(x_rear + 1.6 * k2, ys - 3.0 * k2 - 68, "punch, stepped for both barrels", 11, STEEL, "middle")
    s.line(x_rear + 1.6 * k2, ys - 3.0 * k2 - 14, x_rear + 1.6 * k2, ys - 3.0 * k2 - 2, arrow=True)
    s.text(xe + 8, ys - 20, "box: never touched", 10, MID)
    s.text(x_rear - 3.0 * k2, ys + 80, "carrier 3.0 + tab 0.8-1.15 mm, in the floor plane", 10, METAL)
    s.lines(620, 490, [
        "What locates what:",
        "- pilot pins in the neighbours' holes: along the strip",
        "- carrier edge on a stepper fence: along the contact,",
        "  corrected per contact from the waiting contact's picture",
        "- anvil top: height; carrier held flat: roll",
        "What drives the crimp: an arbor-press ram pulled",
        "  by a stepper lead screw, hard stop at the bottom",
        "How it knows: pins home, the waiting contact's picture,",
        "  a gate across the station (lit vane in the gap),",
        "  ram at the stop, force trace, the after-crimp look",
        "What Derek does: splay and strip the ribbon end,",
        "  thread a 100-piece strip every ~2 units (or a",
        "  reel once), empty the scrap, insert the contacts",
    ], 11, INK, 15)
    s.save("a2-strip-indexer.svg")


# ================================================================== a1
def sketch_applicator():
    s = Svg(900, 620, "a1 stock side-feed applicator on a slow screw ram")
    s.text(20, 30, "a1  A stock side-feed XH applicator, driven by a slow screw ram", 17, weight="bold")
    schematic_tag(s, 20, 50, "not to scale")
    # frame
    s.rect(300, 80, 30, 470, stroke=STEEL, fill=STEEL_F)
    s.rect(300, 80, 330, 30, stroke=STEEL, fill=STEEL_F)
    s.rect(250, 530, 450, 30, stroke=STEEL, fill=STEEL_F)
    s.text(705, 550, "base: load cell under the applicator plate", 11, STEEL)
    # motor + screw
    s.rect(430, 40, 60, 40, stroke=INK, fill="#e6e6e6")
    s.text(500, 62, "NEMA 23 + ~5:1 belt or gearbox", 11)
    s.line(460, 110, 460, 250, stroke=INK, sw=3)
    s.text(470, 180, "ball screw (SFU1605 class)", 11)
    s.rect(430, 250, 60, 30, stroke=INK, fill="#dddddd")
    s.text(500, 270, "guided nut + coupler to the T-shank", 11)
    # applicator
    s.rect(380, 290, 160, 230, stroke=PRINT, fill="#eef6f3", sw=1.4)
    s.text(460, 310, "applicator", 12, PRINT, "middle", weight="bold")
    s.lines(390, 332, ["- feed finger in the", "  pilot holes (cam fed", "  by the ram stroke)",
                       "- guide plates, pressure", "  plate (drag brake)", "- anvils + floating shear",
                       "- crimp-height dials", "- stripper plate"], 10, PRINT, 13)
    # reel
    s.circle(150, 200, 70, stroke=METAL, fill=METAL_F)
    s.circle(150, 200, 30, stroke=METAL, fill="#ffffff")
    s.text(150, 290, "reel on an arm", 11, METAL, "middle")
    s.text(150, 304, "(8,000 = the whole program)", 10, MID, "middle")
    s.path("M 150 130 C 250 140 330 420 380 470", stroke=METAL, sw=2)
    s.text(215, 400, "strip enters the side", 10, METAL)
    # scrap
    s.path("M 540 470 C 600 480 640 500 660 525", stroke=METAL, sw=2, dash="4,3")
    s.text(560, 460, "cut-off carrier pieces", 10, METAL)
    s.text(560, 473, "to a bin (scrap cover)", 10, METAL)
    # ribbon carriage
    s.rect(560, 380, 160, 40, stroke=INK, fill="#f3f3f3")
    s.text(640, 404, "ribbon carriage + fork", 11, INK, "middle")
    s.line(560, 400, 520, 400, arrow=True)
    s.text(730, 395, "presents conductor k", 10)
    s.text(730, 408, "into the waiting contact", 10)
    s.lines(40, 470, ["Pre-feed: at rest, the next contact", "already sits on the anvil.",
                      "One slow stroke: crimp both barrels,", "shear the tab, feed the next."], 11, INK, 15)
    s.lines(40, 580, ["Mini-applicator interface: 30-40 mm stroke; shut height 135.8 mm (standard) or 160 mm (JST MKS-L",
                      "for AP-K2N). A screw ram must reach the shut height to +/-0.02 mm: stop on a hard stop or teach it."],
            10, MID, 13)
    s.save("a1-applicator-slow-ram.svg")


# ================================================================== a1c
def sketch_carrier_handle():
    s = Svg(1000, 520, "a2b carrier kept as the handle through insertion")
    s.text(20, 30, "a2b  The carrier kept as the handle: crimp, inspect and insert by the tab", 17, weight="bold")
    schematic_tag(s, 20, 50, "contact from clone drawings; housing cavity schematic")
    k = 16
    # panel 1: trimmed handle top view
    s.text(20, 85, "1  After the crimp, the carrier is cut to a", 12, weight="bold")
    s.text(20, 100, "   2.3 mm handle around its pilot hole", 12, weight="bold")
    x0, y0 = 150, 150
    s.rect(x0 - 1.15 * k, y0, 2.3 * k, 3.0 * k, stroke=METAL, fill=METAL_F)
    s.circle(x0, y0 + 1.5 * k, 0.75 * k, stroke=METAL, fill="#fff")
    s.rect(x0 - 0.4 * k, y0 + 3.0 * k, 0.8 * k, 1.0 * k, stroke=METAL, fill=METAL_F, sw=0.8)
    contact_plan(s, x0, y0 + 4.0 * k, k, 1, crimped=True)
    # wire lifted: shown as dashed going up-left
    s.path(f"M {x0} {y0+4.0*k+10} C {x0-10} {y0+2*k} {x0-60} {y0-10} {x0-90} {y0-30}", stroke=WIRE, sw=6)
    s.text(x0 - 130, y0 - 36, "wire rises off the handle", 10)
    s.text(x0 + 30, y0 + 1.6 * k, "pin in the hole, plus", 10, ACCENT)
    s.text(x0 + 30, y0 + 1.6 * k + 13, "fingers on the crimp", 10, ACCENT)
    s.text(x0 + 30, y0 + 6 * k, "at 2.5 mm pitch the", 10, MID)
    s.text(x0 + 30, y0 + 6 * k + 13, "handles clear by 0.2", 10, MID)

    # panel 2: insertion section
    s.text(360, 85, "2  Two-point grip: pin in the tag's hole + fingers on the", 12, weight="bold")
    s.text(360, 100, "   crimped insulation barrel; the cavity guides the box", 12, weight="bold")
    k2 = 20
    hx, hy = 470, 250   # housing front face at hx (left), rear face at hx + 7.75k
    s.rect(hx, hy - 60, 7.75 * k2, 120, stroke=INK, fill=HOUS_F)
    s.rect(hx + 0.9 * k2, hy - 1.4 * k2, 6.85 * k2, 2.8 * k2, stroke=INK, fill="#ffffff")
    s.rect(hx, hy - 0.45 * k2, 0.9 * k2, 0.9 * k2, stroke=INK, fill="#ffffff")
    s.text(hx + 3.9 * k2, hy - 68, "XHP housing, one cavity (section)", 10, MID, "middle")
    # contact inside partly, pointing left (front toward -x)
    xr = hx + 7.75 * k2 + 1.6 * k2  # contact rear still 1.6 mm outside
    contact_side(s, xr, hy + 1.1 * k2, k2, -1, crimped=True, lance=True, carrier_mm=0)
    # tab + handle to the right, in floor plane
    s.line(xr, hy + 1.1 * k2, xr + 4.0 * k2, hy + 1.1 * k2, stroke=METAL, sw=3)
    s.rect(xr + 1.0 * k2, hy + 1.1 * k2 - 6, 3.0 * k2, 12, stroke=ACCENT, fill="none", sw=1.2, dash="3,2")
    s.text(xr + 1.0 * k2, hy + 1.1 * k2 + 26, "pin in the hole; fingers on the crimp", 10, ACCENT)
    s.line(xr + 4.5 * k2, hy + 1.1 * k2, xr + 2.6 * k2 + 50, hy + 1.1 * k2, arrow=False)
    s.line(xr + 5.5 * k2, hy + 60, xr + 3.0 * k2, hy + 60, arrow=True)
    s.text(xr + 3.0 * k2, hy + 76, "push", 10)
    wire_side(s, xr + 3.6 * k2, xr - 1.4 * k2, xr - 1.4 * k2, hy + 1.1 * k2 - 0.85 * k2, k2)
    s.text(hx + 7.75 * k2 + 4, hy + 100, "rear face", 10, MID)

    # panel 3: near seat, snip and fork
    s.text(20, 380, "3  Near home the carrier edge meets the rear face (margin -0.05 to +0.9 mm, calc 4):", 12,
           weight="bold")
    s.text(20, 396, "   snip the tab at the face, then a fork behind the insulation barrel finishes the seat and "
           "feels the lance click", 12, weight="bold")
    s.lines(20, 430, [
        "What the tag buys: a stamped datum on the contact's centreline, carried from the crimp through inspection",
        "and most of insertion. The proof pull goes to the box's rear face through a slotted plate, not through the tag.",
        "What it costs: a second cut or bend-off beside the housing, and a tag 2.3 mm wide that no 1.5-1.6 mm",
        "wire comb takes: in a gang push the tags are bent off after a partial push, or cut before it.",
    ], 11, INK, 15)
    s.save("a2b-carrier-as-handle.svg")


# ================================================================== a2
def sketch_hanging_rail():
    s = Svg(1000, 760, "a3 hanging rail for loose kit contacts")
    s.text(20, 30, "a3  Loose contacts hang by their insulation wings on a slotted rail, like screws in a presenter",
           17, weight="bold")
    schematic_tag(s, 20, 50, "rail cross-section from clone dimensions; machine not to scale")
    # hopper & scoop wheel
    s.poly([(40, 120), (220, 120), (200, 300), (60, 300)], stroke=INK, fill="#fafafa")
    s.text(60, 112, "hopper: loose kit contacts", 11)
    s.circle(130, 230, 55, stroke=PRINT, fill=PRINT_F)
    s.text(130, 232, "slow scoop", 10, PRINT, "middle")
    s.text(130, 245, "wheel ~4 rpm", 10, PRINT, "middle")
    # rail
    s.line(200, 180, 720, 250, stroke=STEEL, sw=5)
    s.text(420, 185, "rail, tilted and gently vibrated", 11, STEEL)
    # hanging contacts under rail
    import math
    for i, t in enumerate([0.12, 0.25, 0.38, 0.51, 0.64, 0.77]):
        x = 200 + t * 520
        y = 180 + t * 70
        s.rect(x - 5, y - 3, 10, 6, stroke=METAL, fill=METAL_F, sw=0.8)
        s.rect(x - 3, y + 3, 6, 16, stroke=METAL, fill=METAL_F, sw=0.8)
        s.rect(x - 3.5, y + 19, 7, 12, stroke=METAL, fill="#f0e2b8", sw=0.8)
    # brush and height wiper
    s.circle(330, 168, 14, stroke=MID, fill="none", sw=1)
    s.text(350, 128, "brush sweeps off anything not hanging", 10, MID)
    s.line(470, 200, 470, 238, stroke=ACCENT, sw=2)
    s.text(480, 290, "height wiper: knocks off", 10, ACCENT)
    s.text(480, 303, "anything riding high", 10, ACCENT)
    s.line(478, 282, 471, 240, stroke=ACCENT, sw=0.8)
    # escapement + camera
    s.rect(700, 235, 50, 50, stroke=INK, fill="#f0f0f0")
    s.text(760, 250, "escapement: two gates", 10)
    s.text(760, 263, "release one at a time", 10)
    s.rect(705, 130, 40, 26, stroke=INK, fill="#dde3ea")
    s.text(750, 140, "ELP camera looks down", 10)
    s.text(750, 153, "into the insulation U", 10)
    s.line(725, 156, 725, 230, stroke=MID, dash="3,3")
    s.circle(725, 320, 22, stroke=PRINT, fill=PRINT_F)
    s.text(755, 318, "turn pocket: servo turns", 10, PRINT)
    s.text(755, 331, "the contact 180 deg if the", 10, PRINT)
    s.text(755, 344, "U opens the wrong way", 10, PRINT)
    # handoffs
    s.text(560, 400, "Handoff, pick one:", 12, weight="bold")
    s.lines(560, 420, [
        "(a3)  a hinged pocket tips the contact 90 deg onto a horizontal",
        "      anvil; a spring flap (WC-110 style) holds it to a stop",
        "(a3b) crimp it where it hangs: the pocket is the anvil, the",
        "      punch moves sideways, the conductor comes down from above",
        "(to a4) a 0.64 mm post rises into the hanging box from below",
        "      and carries the contact away",
    ], 11, INK, 15)
    # rail section inset
    k = 30
    ox, oy = 170, 480
    s.text(40, 395, "RAIL CROSS-SECTION, contact hanging (looking along the rail)", 12, MID, weight="bold")
    # rail blocks with stepped slot
    top_gap = 2.4 * k
    low_gap = 2.05 * k
    s.rect(ox - 110, oy, 110 - top_gap / 2, 30, stroke=STEEL, fill=STEEL_F)
    s.rect(ox + top_gap / 2, oy, 110 - top_gap / 2, 30, stroke=STEEL, fill=STEEL_F)
    s.rect(ox - 110, oy + 30 + 3.0 * k, 110 - low_gap / 2, 40, stroke=STEEL, fill=STEEL_F)
    s.rect(ox + low_gap / 2, oy + 30 + 3.0 * k, 110 - low_gap / 2, 40, stroke=STEEL, fill=STEEL_F)
    s.line(ox - 110 + (110 - top_gap / 2), oy + 30, ox - 110 + (110 - top_gap / 2), oy + 30 + 3.0 * k,
           stroke=STEEL, sw=1, dash="3,3")
    s.line(ox + top_gap / 2, oy + 30, ox + top_gap / 2, oy + 30 + 3.0 * k, stroke=STEEL, sw=1, dash="3,3")
    # contact: wings resting on rail top, barrels below, box in low gap
    s.rect(ox - 1.4 * k, oy - 1.2 * k, 2.8 * k, 1.2 * k, stroke=METAL, fill=METAL_F)
    s.text(ox, oy - 1.2 * k - 6, "insulation wings 2.7-3.0 wide rest on the rail", 10, METAL, "middle")
    s.rect(ox - 0.93 * k, oy, 1.85 * k, 3.1 * k, stroke=METAL, fill=METAL_F)
    s.text(ox + 1.4 * k + 10, oy + 1.5 * k, "conductor barrel in the 2.4 slot", 10, METAL)
    s.rect(ox - 0.93 * k, oy + 3.1 * k, 1.85 * k, 2.0 * k, stroke=METAL, fill="#f0e2b8")
    s.text(ox + 1.4 * k + 10, oy + 3.9 * k, "box 1.85 wide passes 2.05;", 10, METAL)
    s.text(ox + 1.4 * k + 10, oy + 3.9 * k + 13, "box 2.2-2.35 tall does not", 10, METAL)
    s.text(40, oy + 6.2 * k, "A genuine JST contact drawn inside 1.95 x 2.4 has no wider 'head' and would", 10, ACCENT)
    s.text(40, oy + 6.2 * k + 13, "fall through: this feeder is for the kit (clone) contacts as drawn. Measure one.",
           10, ACCENT)
    s.save("a3-hanging-rail.svg")


# ================================================================== a2b
def sketch_hanging_crimp():
    s = Svg(780, 580, "a3b vertical crimp where the contact hangs")
    s.text(20, 30, "a3b  Crimp it where it hangs: the turning pocket faces the U to a sideways punch", 17,
           weight="bold")
    schematic_tag(s, 20, 50, "side view looking along the rail, after the pocket's turn; contact from clone drawings")
    k = 26
    cx, top = 330, 250
    # anvil pocket behind the floor
    s.rect(cx - 70, top - 30, 70 - 0.1 * k, 5.8 * k + 60, stroke=STEEL, fill=STEEL_F)
    s.lines(40, top + 20, ["fixed steel wall", "beside the rail's", "line: carries the", "crimp force"], 10, STEEL, 13)
    # wire from above (drawn first)
    s.rect(cx + 0.1 * k, 70, 1.7 * k, top + 1.6 * k - 70, stroke=WIRE, fill="#555555", sw=0.8)
    s.rect(cx + 0.1 * k + 0.49 * k, top + 1.6 * k, 0.72 * k, 1.8 * k, stroke=CU, fill=CU, sw=0.6)
    # contact vertical: floor on the left, wings open to the right, box down
    s.rect(cx - 0.1 * k, top, 0.2 * k, 5.8 * k, stroke=METAL, fill=METAL)
    s.rect(cx, top, 3.0 * k, 1.4 * k, stroke=METAL, fill="none", sw=1.6)
    s.rect(cx, top + 1.8 * k, 1.5 * k, 1.4 * k, stroke=METAL, fill="none", sw=1.6)
    s.rect(cx, top + 3.8 * k, 2.3 * k, 2.0 * k, stroke=METAL, fill="#f0e2b8")
    s.text(cx + 3.2 * k, top + 0.8 * k, "insulation U, open to the right", 10, METAL)
    s.text(cx + 2.6 * k, top + 5 * k, "box, hanging down", 10, METAL)
    # punch from right
    s.rect(cx + 3.6 * k, top + 1.6 * k, 120, 1.8 * k, stroke=STEEL, fill=STEEL_F)
    s.line(cx + 3.6 * k + 60, top + 2.5 * k, cx + 3.2 * k, top + 2.5 * k, arrow=True)
    s.text(cx + 3.6 * k + 5, top + 1.6 * k - 8, "punch moves sideways", 10, STEEL)
    # finger pressing the insulation toward the floor
    s.poly([(cx + 3.4 * k, top - 0.9 * k), (cx + 1.9 * k, top - 0.3 * k), (cx + 1.9 * k, top - 0.05 * k),
            (cx + 3.4 * k, top - 0.5 * k)], stroke=PRINT, fill=PRINT_F, sw=1.2)
    s.text(cx + 3.5 * k, top - 0.7 * k, "finger presses the insulation toward the floor", 10, PRINT)
    s.lines(cx + 2.4 * k, 90, ["conductor k lowered from above;", "the open insulation U is its funnel;",
                               "the ribbon hangs above, clamped"], 11, INK, 14)
    s.lines(20, 490, [
        "Z reference: the pocket top the insulation barrel rests on. The conductor's depth is steered by the",
        "insulation edge as seen. The pocket turned 90 or 270 deg so the U faces the punch; its cut-away side lets",
        "the floor meet the fixed wall. The punch pushes the contact onto the wall, outside the rail's line.",
    ], 11, INK, 15)
    s.save("a3b-hanging-crimp.svg")


# ================================================================== a3
def sketch_post_turret():
    import math
    s = Svg(1000, 720, "a4 post-held contacts on a turret")
    s.text(20, 30, "a4  Hold the contact by mating it: 0.64 mm square posts on a slow turret", 17, weight="bold")
    schematic_tag(s, 20, 50, "turret layout not to scale; inset from clone dimensions")
    cx, cy, R = 250, 360, 105
    s.circle(cx, cy, R, stroke=PRINT, fill=PRINT_F, sw=1.4)
    s.circle(cx, cy, 16, stroke=PRINT, fill="#fff")
    s.text(cx, cy + 34, "printed turret", 11, PRINT, "middle")
    s.text(cx, cy + 48, "(stepper, 16 posts)", 10, PRINT, "middle")
    n = 16
    for i in range(n):
        a = 2 * math.pi * i / n
        x1, y1 = cx + R * math.cos(a), cy + R * math.sin(a)
        x2, y2 = cx + (R + 10) * math.cos(a), cy + (R + 10) * math.sin(a)
        s.line(x1, y1, x2, y2, stroke=STEEL, sw=2)
        if i in (3, 11):
            continue
        x3, y3 = cx + (R + 60) * math.cos(a), cy + (R + 60) * math.sin(a)
        s.line(x2, y2, x3, y3, stroke=METAL, sw=7)
    s.rect(cx + R + 5, cy - 18, 70, 36, stroke=STEEL, fill="none", sw=1.4, dash="5,3")
    s.text(cx + R + 5, cy - 26, "crimp station", 10, STEEL)
    s.rect(cx + R + 62, cy - 4, 170, 8, stroke=WIRE, fill="#555555")
    s.text(cx + R + 90, cy + 26, "conductor k comes in radially", 10)
    s.lines(20, cy - 10, ["loading station:", "a nozzle fills a", "lance-grooved nest;", "the post spears it.",
                          "Or Derek pushes", "contacts on, U up"],
            10, INK, 13)
    s.rect(cx - 20, cy - R - 105, 40, 24, stroke=INK, fill="#dde3ea")
    s.text(cx + 28, cy - R - 88, "camera: contact present? U up?", 10)
    s.text(40, cy + R + 95, "an empty post, loaded in loom order, stands for J2's empty cavity 3", 10, MID)
    # inset
    k = 24
    ox, oy = 650, 470
    s.text(560, 150, "INSET: side view at the crimp station", 12, MID, weight="bold")
    s.rect(ox - 60, oy - 100, 60, 160, stroke=PRINT, fill=PRINT_F)
    s.lines(ox - 60, oy + 78, ["post holder: face = axial stop;", "floats in Z on a leaf spring"], 10, PRINT, 13)
    s.rect(ox, oy - 1.15 * k - 0.32 * k, 1.65 * k, 0.64 * k, stroke=STEEL, fill=STEEL, sw=1)
    s.text(ox + 2, oy - 3.0 * k - 50, "0.64 mm post, 1.5-1.8 mm into the box", 10, STEEL)
    s.line(ox + 1.3 * k, oy - 3.0 * k - 46, ox + 1.3 * k, oy - 1.5 * k, stroke=STEEL, sw=0.8)
    xr = ox + 5.8 * k
    wire_side(s, xr + 90, xr - 1.6 * k, xr - 4.0 * k, oy - 0.85 * k, k)
    contact_side(s, xr, oy, k, -1, crimped=False)
    s.rect(xr - 3.4 * k, oy + 2, 3.5 * k, 50, stroke=STEEL, fill=STEEL_F)
    s.text(xr - 1.7 * k, oy + 40, "anvil sets Z", 10, STEEL, "middle")
    s.rect(xr - 3.4 * k, oy - 3.0 * k - 30, 3.5 * k, 22, stroke=STEEL, fill=STEEL_F)
    s.text(xr - 1.7 * k + 50, oy - 3.0 * k - 14, "punch", 10, STEEL)
    s.lines(560, 620, ["The post locates the box in plane, as the header post it was made for;",
                       "the anvil sets height; the holder floats so the die centres the barrels.",
                       "After the crimp a pull on the wire slides it off (0.2-2 N): joined or not."],
            10, INK, 13)
    s.save("a4-post-turret.svg")


# ================================================================== a3b
def sketch_through_cavity_post():
    s = Svg(1000, 640, "a4b post through the housing cavity guides the insertion")
    s.text(20, 30, "a4b  The post goes through the housing first: crimp on its tip, then slide the contact home",
           17, weight="bold")
    schematic_tag(s, 20, 50, "section along one cavity; housing and contact proportions from JST/clone dims")
    k = 22
    hx, hy = 220, 250
    # housing section
    s.rect(hx, hy - 2.05 * k, 7.75 * k, 4.1 * k, stroke=INK, fill=HOUS_F)
    s.rect(hx + 0.9 * k, hy - 1.3 * k, 6.85 * k, 2.6 * k, stroke=INK, fill="#ffffff")
    s.rect(hx, hy - 0.45 * k, 0.9 * k, 0.9 * k, stroke=INK, fill="#ffffff")
    s.text(hx + 3.9 * k, hy - 2.05 * k - 10, "XHP housing (section through cavity k)", 10, MID, "middle")
    s.text(hx - 5, hy + 2.05 * k + 16, "mating face", 10, MID, "end")
    s.text(hx + 7.75 * k + 4, hy + 2.05 * k + 16, "rear face", 10, MID)
    # post from the left, through the post opening and cavity, out the rear
    x_tip = hx + 7.75 * k + 9.0 * k
    s.rect(hx - 120, hy - 0.32 * k, x_tip - (hx - 120), 0.64 * k, stroke=STEEL, fill=STEEL, sw=1)
    s.rect(hx - 180, hy - 40, 60, 80, stroke=PRINT, fill=PRINT_F)
    s.text(hx - 180, hy + 58, "post slide (Y)", 10, PRINT)
    # contact on tip, front at x_tip - 2.5 mm engagement
    x_front = x_tip - 1.5 * k
    x_rear = x_front + 5.8 * k
    wire_side(s, x_rear + 120, x_rear - 1.6 * k, x_rear - 4.0 * k, hy + 1.15 * k - 0.85 * k, k)
    contact_side(s, x_rear, hy + 1.15 * k, k, -1, crimped=False)
    # anvil + punch
    s.rect(x_rear - 3.4 * k, hy + 1.15 * k + 2, 3.5 * k, 50, stroke=STEEL, fill=STEEL_F)
    s.rect(x_rear - 3.4 * k, hy + 1.15 * k - 3.0 * k - 60, 3.5 * k, 40, stroke=STEEL, fill=STEEL_F)
    s.text(x_rear - 1.7 * k, hy + 1.15 * k + 40, "anvil", 10, STEEL, "middle")
    s.text(x_rear - 1.7 * k, hy + 1.15 * k - 3.0 * k - 66, "punch", 10, STEEL, "middle")
    s.text(x_front - 4 * k, hy + 3.4 * k, "~9 mm clear of the rear face:", 10, INK)
    s.text(x_front - 4 * k, hy + 3.4 * k + 13, "room for the dies beside seated neighbours", 10, INK)
    # sequence notes
    s.lines(40, 420, [
        "1  The stage (housing nest and web clamp together) puts cavity k on the post line; the post runs through it.",
        "2  A lance-grooved shuttle nest pushes a bare contact onto the post tip, box first, 1.5-1.8 mm deep.",
        "3  The ribbon carriage lays conductor k into the open barrels; the anvil rises to the floor; crimp.",
        "4  A fork behind the insulation barrel pushes the contact ~14 mm along the post into cavity k while the post",
        "   withdraws in step, its tip staying 1.5 mm inside the box, clear of the crimped strands.",
        "5  Force against distance: rise at the lance, a drop at the click, a wall at the seat. Then a 5 N pull.",
        "6  The post withdraws out the front; the stage goes to the next cavity in layer order (J4, J7 upper layer last).",
    ], 11, INK, 16)
    s.lines(40, 545, [
        "Nothing has to find the cavity: the contact is threaded on a line that already runs through it.",
        "Open: with one web clamp, conductor k must carry that ~14 mm at its crimp as an 11-15 mm hump (calc w3 3);",
        "   every post at once and one housing move stores nothing: branch a4c. The post's path past the cavity's",
        "   inner features is unmeasured (one flashlight photo); a 17 mm post is soft (1.2-1.7 N/mm).",
    ], 11, ACCENT, 16)
    s.save("a4b-through-cavity-post.svg")


# ================================================================== a4
def sketch_housing_fixture():
    import math
    s = Svg(1000, 760, "a5 housing as the fixture: stage the bare contact, crimp at the mouth, push home")
    s.text(20, 30, "a5  The housing is the fixture: stage a bare contact in its cavity, crimp at the mouth, push home",
           17, weight="bold")
    schematic_tag(s, 20, 50, "plan from above; 2.5 mm pitch and 1.7 mm wire true to scale, dies schematic")
    k = 22
    hx = 300                 # housing rear face x (housing to the left)
    y0 = 150                 # cavity 1 centre
    ncav = 5
    s.rect(hx - 7.75 * k, y0 - 1.6 * k, 7.75 * k, (ncav - 1) * 2.5 * k + 3.2 * k, stroke=INK, fill=HOUS_F)
    s.text(hx - 7.75 * k, y0 - 1.6 * k - 8, "XHP-5 from above, rear face on the right", 10, MID)
    for c in range(ncav):
        y = y0 + c * 2.5 * k
        s.rect(hx - 6.85 * k, y - 1.0 * k, 6.85 * k, 2.0 * k, stroke=MID, fill="#ffffff", sw=0.8)
        s.text(hx - 7.75 * k - 6, y + 4, str(c + 1), 11, MID, "end")
    s.line(hx, y0 - 1.6 * k - 20, hx, y0 + 5 * 2.5 * k, stroke=MID, dash="2,3", sw=0.8)
    s.text(hx + 3, y0 - 1.6 * k - 22, "rear face", 10, MID)
    # seated contacts 1 and 2, wires swept toward the done side at 35 and 20 deg
    for c, deg in ((0, 35), (1, 20)):
        y = y0 + c * 2.5 * k
        s.rect(hx - 6.5 * k, y - 0.93 * k, 6.1 * k, 1.85 * k, stroke=METAL, fill=METAL_F, sw=0.8)
        a = math.radians(deg)
        L = 150
        xe, ye = hx + L * math.cos(a), y - L * math.sin(a)
        nx, ny = math.sin(a) * 0.85 * k, math.cos(a) * 0.85 * k
        s.poly([(hx, y - 0.85 * k), (xe - nx, ye - ny), (xe + nx, ye + ny), (hx, y + 0.85 * k)],
               stroke=WIRE, fill="#555555", sw=0.8)
    s.circle(hx + 55, y0 + 2.5 * k + 0.85 * k - 55 * math.tan(math.radians(20)) + 9, 8, stroke=PRINT, fill=PRINT_F)
    s.lines(hx + 200, y0 - 40, ["a finger sweeps the seated wires", "toward the done side, 20-35 deg,",
                                "right at the face"], 10, PRINT, 13)
    # staged contact 3: box 1.5 mm into cavity 3
    y = y0 + 2 * 2.5 * k
    xf = hx - 1.5 * k
    s.rect(xf, y - 0.93 * k, 2.0 * k, 1.85 * k, stroke=METAL, fill="#f0e2b8", sw=1)
    s.rect(xf + 2.0 * k, y - 0.6 * k, 0.6 * k, 1.2 * k, stroke=METAL, fill=METAL_F, sw=1)
    s.rect(xf + 2.6 * k, y - 0.93 * k, 1.4 * k, 1.85 * k, stroke=METAL, fill=METAL_F, sw=1)
    s.rect(xf + 4.0 * k, y - 0.5 * k, 0.5 * k, 1.0 * k, stroke=METAL, fill=METAL_F, sw=1)
    s.rect(xf + 4.5 * k, y - 1.4 * k, 1.4 * k, 2.8 * k, stroke=METAL, fill=METAL_F, sw=1)
    s.rect(xf + 2.45 * k, y - 1.75 * k, 1.7 * k, 3.5 * k, stroke=ACCENT, fill="none", sw=1.5, dash="5,3")
    s.rect(xf + 4.35 * k, y - 2.0 * k, 1.7 * k, 4.0 * k, stroke=ACCENT, fill="none", sw=1.5, dash="5,3")
    s.lines(xf + 6.4 * k, y + 1.2 * k, ["punch footprints, 3.5 and 4.0 mm wide:",
                                        "they reach into lane 2, which the swept",
                                        "wire has left"], 10, ACCENT, 13)
    s.rect(xf + 4.3 * k, y - 0.85 * k, 300, 1.7 * k, stroke=WIRE, fill="none", sw=1, dash="6,3")
    s.text(xf + 6.4 * k, y - 1.1 * k, "conductor 3, laid in from above", 10)
    s.text(hx + 8, y0 + 3.5 * 2.5 * k + 20, "cavities 4, 5 empty; their conductors wait lifted above the dies", 10, MID)
    s.text(hx + 8, y0 + 3.5 * 2.5 * k + 34, "(fanned flat at 2.5 mm they would meet 3.5-4.0 mm punches: calc w3 7)", 10, MID)
    # side view
    s.text(20, 470, "SIDE VIEW at cavity 3", 12, MID, weight="bold")
    k2 = 22
    sx, sy = 360, 590
    s.rect(sx - 7.75 * k2, sy - 2.05 * k2, 7.75 * k2, 4.1 * k2, stroke=INK, fill=HOUS_F)
    s.rect(sx - 6.85 * k2, sy - 1.3 * k2, 6.85 * k2, 2.6 * k2, stroke=INK, fill="#fff")
    s.rect(sx - 7.75 * k2, sy - 0.45 * k2, 0.9 * k2, 0.9 * k2, stroke=INK, fill="#fff")
    xr = sx - 1.5 * k2 + 5.8 * k2
    s.rect(sx - 7.75 * k2 - 80, sy - 0.32 * k2, 80 + 6.2 * k2, 0.64 * k2, stroke=STEEL, fill=STEEL, sw=0.6)
    wire_side(s, xr + 140, xr - 1.6 * k2, xr - 4.0 * k2, sy + 1.15 * k2 - 0.85 * k2, k2)
    contact_side(s, xr, sy + 1.15 * k2, k2, -1)
    s.rect(xr - 3.4 * k2, sy + 1.15 * k2 + 2, 3.5 * k2, 45, stroke=STEEL, fill=STEEL_F)
    s.rect(xr - 3.4 * k2, sy + 1.15 * k2 - 3.0 * k2 - 55, 3.5 * k2, 38, stroke=STEEL, fill=STEEL_F)
    s.text(xr - 1.7 * k2, sy + 1.15 * k2 + 36, "anvil", 10, STEEL, "middle")
    s.text(xr - 1.7 * k2, sy + 1.15 * k2 - 3.0 * k2 - 62, "punch", 10, STEEL, "middle")
    s.text(sx - 7.75 * k2 - 80, sy - 14, "staging post", 10, STEEL)
    s.text(sx - 7.75 * k2 - 80, sy + 26, "through the front", 10, STEEL)
    s.lines(620, 510, [
        "Staged 1.5 mm deep: the lance is still",
        "0.9 mm outside, the conductor barrel sits",
        "1.1-2.5 mm behind the face, the insulation",
        "barrel 3.0-4.5 mm. A flat anvil's front edge",
        "has ~0.06 mm between lance and barrel:",
        "a lance slot in the anvil, or measure first.",
        "After the crimp a fork pushes it the last",
        "5.25-5.45 mm; conductor k carries that as a",
        "6-8 mm hump at its crimp (or: x3, one push).",
    ], 11, INK, 15)
    s.save("a5-housing-as-fixture.svg")


if __name__ == "__main__":
    sketch_strip_indexer()
    sketch_applicator()
    sketch_carrier_handle()
    sketch_hanging_rail()
    sketch_hanging_crimp()
    sketch_post_turret()
    sketch_through_cavity_post()
    sketch_housing_fixture()
