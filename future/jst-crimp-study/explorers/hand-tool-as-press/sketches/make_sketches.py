"""Schematic sketches for the hand-tool-as-press explorer.

Run: python3 make_sketches.py   (writes the .svg files beside it)

All drawings are schematic. No geometry here comes from a measured tool.
"""
import math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "Helvetica,Arial,sans-serif"

C = dict(
    bg="#fcfcf8", ink="#1b1b1b", grey="#8a8a8a", light="#e9e6dc",
    steel="#9aa5ad", steel_d="#5e6a72", printed="#f2c14e", printed_d="#b98a12",
    bought="#7fb3d5", bought_d="#2e6f99", wire="#222", copper="#c47a2c",
    contact="#d9b64a", contact_d="#8a6d12", red="#c0392b", green="#2e8b57",
    blue="#2a6f97",
)


class S:
    def __init__(self, w, h, title, sub=""):
        self.w, self.h = w, h
        self.p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
                  '<defs><marker id="ar" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                  f'<path d="M0,0 L10,4 L0,8 z" fill="{C["ink"]}"/></marker>'
                  '<marker id="arr" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto">'
                  f'<path d="M0,0 L10,4 L0,8 z" fill="{C["red"]}"/></marker>'
                  '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                  f'<line x1="0" y1="0" x2="0" y2="6" stroke="{C["grey"]}" stroke-width="1"/></pattern></defs>',
                  f'<rect width="100%" height="100%" fill="{C["bg"]}"/>']
        self.t(16, 28, title, 18, bold=True)
        if sub:
            self.t(16, 48, sub, 12, fill=C["grey"])

    def t(self, x, y, s, size=11, fill=None, anchor="start", bold=False, italic=False):
        fill = fill or C["ink"]
        s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        w = "bold" if bold else "normal"
        st = "italic" if italic else "normal"
        self.p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
                      f'text-anchor="{anchor}" font-weight="{w}" font-style="{st}">{s}</text>')

    def lines(self, x, y, arr, size=11, dy=None, **kw):
        dy = dy or size * 1.3
        for i, s in enumerate(arr):
            self.t(x, y + i * dy, s, size, **kw)

    def r(self, x, y, w, h, fill="none", stroke=None, sw=1.2, dash=None, rx=0, op=1.0):
        stroke = stroke or C["ink"]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
                      f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def l(self, x1, y1, x2, y2, stroke=None, sw=1.2, dash=None, arrow=False, red=False):
        stroke = stroke or (C["red"] if red else C["ink"])
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ' marker-end="url(#arr)"' if (arrow and red) else (' marker-end="url(#ar)"' if arrow else "")
        self.p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
                      f'stroke-width="{sw}"{d}{m}/>')

    def poly(self, pts, fill="none", stroke=None, sw=1.2, close=True, dash=None, op=1.0):
        stroke = stroke or C["ink"]
        tag = "polygon" if close else "polyline"
        d = f' stroke-dasharray="{dash}"' if dash else ""
        ps = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.p.append(f'<{tag} points="{ps}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def c(self, x, y, r, fill="none", stroke=None, sw=1.2):
        stroke = stroke or C["ink"]
        self.p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d, fill="none", stroke=None, sw=1.2, dash=None):
        stroke = stroke or C["ink"]
        dd = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dd}/>')

    def callout(self, x, y, tx, ty, lines_, size=10.5, anchor="start"):
        self.l(x, y, tx, ty, stroke=C["grey"], sw=0.8)
        self.c(x, y, 2, fill=C["ink"], stroke=C["ink"])
        yy = ty - (len(lines_) - 1) * size * 1.25 / 2 + size * 0.35
        xx = tx + (4 if anchor == "start" else -4)
        for i, s in enumerate(lines_):
            self.t(xx, yy + i * size * 1.25, s, size, anchor=anchor)

    def legend(self, x, y):
        items = [(C["printed"], C["printed_d"], "printed"), (C["bought"], C["bought_d"], "bought / on hand"),
                 (C["steel"], C["steel_d"], "tool steel (hand tool)"), (C["contact"], C["contact_d"], "XH contact")]
        for i, (f, s, n) in enumerate(items):
            self.r(x + i * 150, y - 10, 14, 10, fill=f, stroke=s)
            self.t(x + i * 150 + 20, y - 1, n, 10.5)

    def save(self, name):
        self.p.append("</svg>")
        with open(os.path.join(HERE, name), "w") as f:
            f.write("\n".join(self.p))


def contact_side(s, x0, y0, k=10.0, flip=False, crimped=False):
    """XH contact in side view along its axis. x0,y0 = floor at box front.
    k px per mm. Box to the right (+x) unless flip. Returns key x positions."""
    sgn = -1 if flip else 1
    X = lambda mm: x0 - sgn * mm * k
    # lengths (mm) from box front, schematic from clone drawings
    box = 2.0; neck = 0.6; cb = 1.4; win = 0.8; ib = 1.2
    xs = dict(box_front=X(0), box_rear=X(box), cb_front=X(box + neck), cb_rear=X(box + neck + cb),
              ib_front=X(box + neck + cb + win), ib_rear=X(box + neck + cb + win + ib))
    # floor
    s.r(min(X(0), xs["ib_rear"]), y0, abs(X(0) - xs["ib_rear"]), 0.2 * k, fill=C["contact"], stroke=C["contact_d"], sw=0.8)
    # box
    s.r(min(X(0), X(box)), y0 - 2.4 * k, box * k, 2.4 * k, fill=C["contact"], stroke=C["contact_d"])
    # conductor barrel wings
    h_cb = 0.9 if crimped else 1.55
    h_ib = 1.9 if crimped else 3.0
    s.r(min(xs["cb_front"], xs["cb_rear"]), y0 - h_cb * k, cb * k, h_cb * k, fill=C["contact"], stroke=C["contact_d"], op=0.8)
    s.r(min(xs["ib_front"], xs["ib_rear"]), y0 - h_ib * k, ib * k, h_ib * k, fill=C["contact"], stroke=C["contact_d"], op=0.8)
    return xs


# ---------------------------------------------------------------------------
def sketch_a1():
    s = S(1320, 760, "A1  The squeezer: SN-2549 in a printed cradle, closed by a slow pusher (schematic)",
          "Left: the cradle seen from the side (tool on its side, nest axes pointing out of the page). Right: section along one nest's axis.")
    s.legend(16, 72)
    # --- left panel: cradle ---
    ox, oy = 30, 80
    s.r(ox, oy, 640, 640, stroke="#ccc")
    base_y = oy + 560
    s.r(ox + 20, base_y, 600, 20, fill="url(#hatch)", stroke=C["grey"])
    s.t(ox + 30, base_y + 36, "bench / baseplate", 10.5, fill=C["grey"])
    # printed saddle under the lower handle and a block under the head
    s.r(ox + 240, base_y - 50, 380, 50, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 430, base_y - 20, "printed cradle: saddle + strap", 10.5, anchor="middle")
    s.r(ox + 110, base_y - 40, 130, 40, fill=C["printed"], stroke=C["printed_d"])
    # strap
    s.r(ox + 400, base_y - 70, 20, 70, fill="none", stroke=C["printed_d"], sw=2)
    # lower handle lying on the saddle
    s.r(ox + 230, base_y - 64, 370, 14, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 590, base_y - 72, "lower handle (fixed)", 10, anchor="end", fill=C["steel_d"])
    # head
    hx0, hy0 = ox + 110, base_y - 140
    s.r(hx0, hy0, 130, 100, rx=10, fill=C["steel"], stroke=C["steel_d"])
    s.c(hx0 + 100, hy0 + 50, 5, fill=C["bg"], stroke=C["steel_d"])
    # jaws protruding left, mouth between them
    s.r(ox + 40, hy0 + 14, 76, 30, fill=C["steel"], stroke=C["steel_d"])
    s.r(ox + 40, hy0 + 50, 76, 30, fill=C["steel"], stroke=C["steel_d"])
    for i in range(4):
        s.c(ox + 52 + i * 18, hy0 + 47, 3.2, fill=C["bg"], stroke=C["steel_d"])
    s.t(ox + 30, hy0 - 8, "jaws: 4 nests along them", 10, fill=C["steel_d"])
    # upper handle angled up
    ux0, uy0, ux1, uy1 = ox + 230, hy0 + 30, ox + 570, oy + 300
    s.poly([(ux0, uy0 - 8), (ux1, uy1 - 8), (ux1 + 6, uy1 + 8), (ux0, uy0 + 8)], fill=C["steel"], stroke=C["steel_d"])
    s.t((ux0 + ux1) / 2 + 20, (uy0 + uy1) / 2 + 34, "upper handle (driven)", 10, anchor="middle", fill=C["steel_d"])
    # locator plate at the jaws
    s.r(ox + 34, hy0 + 82, 88, 14, fill=C["printed"], stroke=C["printed_d"])
    s.callout(ox + 78, hy0 + 90, ox + 60, base_y + 60, ["locator plate on the lower-jaw M4 screw (20 mm + thumb nut):", "front stop, insulated flap blade, flap servo, lift ramp"], anchor="start")
    # printed column and beam carrying the pusher
    s.r(ox + 604, oy + 50, 14, base_y - 50 - oy - 50, fill=C["printed"], stroke=C["printed_d"])
    s.r(ox + 470, oy + 50, 148, 14, fill=C["printed"], stroke=C["printed_d"])
    px = ox + 520
    frac = (px - ux0) / (ux1 - ux0)
    hy_at_px = uy0 + frac * (uy1 - uy0)
    s.r(px - 30, oy + 64, 60, 56, fill=C["bought"], stroke=C["bought_d"])
    s.t(px, oy + 96, "NEMA 17", 10, anchor="middle")
    s.l(px, oy + 120, px, hy_at_px - 40, stroke=C["steel_d"], sw=3)
    s.r(px - 14, hy_at_px - 80, 28, 14, fill=C["bought"], stroke=C["bought_d"])
    s.r(px - 10, hy_at_px - 62, 20, 20, fill="#fff", stroke=C["bought_d"])
    s.t(px - 16, hy_at_px - 48, "load cell", 10, anchor="end")
    s.c(px, hy_at_px - 18, 9, fill=C["printed"], stroke=C["printed_d"])
    s.t(px - 16, hy_at_px - 14, "roller foot", 10, anchor="end")
    s.l(px + 40, oy + 150, px + 40, hy_at_px - 20, arrow=True, red=True, sw=2)
    s.lines(ox + 330, oy + 172, ["Tr8x2 screw: ~280 N", "a hand gives 90-220 N", "[calc 1-2]"], 10, fill=C["red"])
    # camera
    s.r(ox + 40, oy + 40, 60, 36, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 110, oy + 62, "ELP camera", 10)
    s.l(ox + 70, oy + 76, ox + 78, hy0 + 14, dash="4,3", stroke=C["blue"])
    # far-end block and controller
    s.r(ox + 200, oy + 110, 80, 40, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 204, oy + 126, ["far-end", "terminal block"], 9.5)
    s.r(ox + 300, oy + 110, 80, 40, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 304, oy + 126, ["ESP32 runs each", "squeeze; HX711"], 9.5)
    s.path(f"M{ox+240},{oy+150} C{ox+240},{oy+230} {ox+20},{hy0} {ox+20},{hy0+47} L{ox+40},{hy0+47}", stroke=C["wire"], sw=2.5)
    s.t(ox + 300, oy + 250, "the ribbon: its far end in the block,", 10, fill=C["green"])
    s.t(ox + 300, oy + 264, "every conductor an electrode", 10, fill=C["green"])
    # --- right panel: section along nest axis ---
    ox2, oy2 = 700, 80
    s.r(ox2, oy2, 590, 640, stroke="#ccc")
    s.t(ox2 + 14, oy2 + 22, "Section along one nest's axis (contact at hold, ~one ratchet click)", 12, bold=True)
    k = 55.0  # px per mm
    y0 = oy2 + 330
    xbf = ox2 + 470  # box front
    xs = contact_side(s, xbf, y0, k=k)
    # die (anvil below, punch above) covers barrels only
    die_l = xs["ib_rear"] - 0.15 * k
    die_r = xs["cb_front"] + 0.05 * k
    s.r(die_l, y0 + 0.2 * k, die_r - die_l, 90, fill=C["steel"], stroke=C["steel_d"])
    s.r(die_l, y0 - 3.4 * k - 90, die_r - die_l, 90, fill=C["steel"], stroke=C["steel_d"])
    s.t((die_l + die_r) / 2, y0 + 0.2 * k + 50, "lower die (anvil), one stepped piece", 10.5, anchor="middle")
    s.t((die_l + die_r) / 2, y0 - 3.4 * k - 40, "upper die (punch), one stepped piece", 10.5, anchor="middle")
    s.t(die_l - 6, y0 - 3.4 * k - 100, "rear face", 10, anchor="end", fill=C["steel_d"])
    s.t(die_r + 6, y0 - 3.4 * k - 100, "front face", 10, fill=C["steel_d"])
    s.l(die_l, y0 - 3.4 * k - 96, die_l, y0 + 0.2 * k + 96, stroke=C["steel_d"], dash="3,3", sw=0.8)
    s.l(die_r, y0 - 3.4 * k - 96, die_r, y0 + 0.2 * k + 96, stroke=C["steel_d"], dash="3,3", sw=0.8)
    # wire from left: insulation + strands
    ins_edge = xs["ib_front"] - 0.4 * k
    s.r(ox2 + 20, y0 - 1.7 * k - 2, ins_edge - ox2 - 20, 1.7 * k, fill="#333", stroke="#000", op=0.85)
    strands_tip = xs["cb_front"] + 0.25 * k
    s.r(ins_edge, y0 - 1.15 * k, strands_tip - ins_edge, 0.72 * k, fill=C["copper"], stroke="#7a4a14")
    s.lines(ox2 + 20, y0 + 26, ["22 AWG silicone,", "1.7 mm OD; strip", "length set from", "the lot's contact"], 10)
    # flap blade in neck
    bx = xs["cb_front"] + 0.28 * k
    s.r(bx - 0.03 * k, y0 - 3.6 * k, 0.03 * k, 3.6 * k + 0.1 * k, fill="#6b3fa0", stroke="#6b3fa0")
    s.r(bx, y0 - 3.6 * k, 0.10 * k, 3.6 * k + 0.1 * k, fill=C["steel_d"], stroke="#222")
    s.poly([(bx, y0 - 3.6 * k), (bx + 0.10 * k, y0 - 3.6 * k), (bx + 60, y0 - 3.6 * k - 70), (bx + 45, y0 - 3.6 * k - 78)], fill=C["printed"], stroke=C["printed_d"])
    s.callout(bx + 8, y0 - 2.9 * k, ox2 + 410, oy2 + 70, ["flap blade: 0.10 mm steel;", "polyimide front face (purple),", "insulated from the box;", "slot straddles the neck strip,", "lance hangs below the tines;", "bare rear face = strand stop", "and electrode: amber = strands", "on contact/tool, green = blade"])
    # front stop
    s.r(xbf + 2, y0 - 3.0 * k, 16, 3.3 * k, fill=C["printed"], stroke=C["printed_d"])
    s.callout(xbf + 18, y0 - 1.5 * k, ox2 + 500, y0 + 150, ["front stop on the", "locator plate", "(or a pilot pin in", "a strip stub's hole)"])
    # labels on contact
    s.t((xs["box_front"] + xs["box_rear"]) / 2, y0 + 0.2 * k + 110, "box", 10.5, anchor="middle", fill=C["contact_d"])
    s.t((xs["cb_front"] + xs["cb_rear"]) / 2, y0 + 0.2 * k + 110, "conductor barrel", 10.5, anchor="middle", fill=C["contact_d"])
    s.t((xs["ib_front"] + xs["ib_rear"]) / 2, y0 + 0.2 * k + 126, "insulation barrel", 10.5, anchor="middle", fill=C["contact_d"])
    s.t((xs["cb_rear"] + xs["ib_front"]) / 2, y0 + 0.2 * k + 142, "window", 10.5, anchor="middle", fill=C["contact_d"])
    s.lines(ox2 + 20, oy2 + 560, [
        "Reference chain: lower jaw -> M4 jaw screw -> printed plate -> flap blade + front stop -> contact.",
        "Barrel rear edge 0.1-0.2 mm proud of the die for a bellmouth: ~+/-0.1 mm axial window [calc 7].",
        "Neck on a real contact unmeasured: blade 0.13-0.15 + brush 0.1-0.2 need >= ~0.3 mm (calc w2 1).",
        "Lift the crimp 1-1.7 mm before drawing it back (ramp on the plate); the pull is taken at a6's jig.",
        "Contact lengths/heights here are schematic (clone drawings, not measured)."], 10.5, fill=C["grey"])
    s.save("a1-squeezer-cradle.svg")


# ---------------------------------------------------------------------------
def sketch_a2():
    s = S(1320, 820, "A2  The ribbon comes to a fixed tool (schematic, plan view)",
          "The tool never moves. The head (X across conductors, Y along the nest axis, Z height) fetches a stub, loads it, then presents one conductor at a time.")
    s.legend(16, 72)
    ox, oy = 30, 80
    s.r(ox, oy, 840, 700, stroke="#ccc")
    # tool (plan): nest axis along Y (vertical in drawing), tool body horizontal
    ty = oy + 170
    s.r(ox + 250, ty - 30, 360, 60, rx=8, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 520, ty + 5, "SN-2549 on its side in a1's cradle", 11, anchor="middle")
    s.r(ox + 250, ty - 40, 60, 80, fill=C["steel"], stroke=C["steel_d"])
    nx = ox + 280
    s.l(nx, ty - 60, nx, ty + 330, stroke=C["blue"], dash="6,4", sw=1)
    s.t(nx + 6, ty - 64, "nest axis (Y)", 10, fill=C["blue"])
    s.r(nx - 40, ty - 60, 80, 18, fill=C["printed"], stroke=C["printed_d"])
    s.t(nx + 48, ty - 47, "locator: front stop, insulated flap blade (servo), datum pin", 10)
    s.r(ox + 620, ty - 50, 60, 100, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 626, ty - 24, ["pusher", "+ load", "cell"], 10)
    # jaw rear face line
    s.l(ox + 240, ty + 40, ox + 320, ty + 40, stroke=C["steel_d"], sw=2)
    s.t(ox + 236, ty + 44, "jaw rear face", 10, anchor="end", fill=C["steel_d"])
    # stub hanging behind rear face (after loading)
    s.r(nx - 30, ty + 44, 60, 12, fill=C["contact"], stroke=C["contact_d"])
    s.c(nx, ty + 50, 4, fill=C["bg"], stroke=C["contact_d"])
    s.t(nx + 36, ty + 58, "carrier stub (pilot hole)", 10, fill=C["contact_d"])
    # head with ribbon
    hy = oy + 420
    s.r(ox + 140, hy + 60, 300, 50, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 322, hy + 90, "head: ribbon clamp on a load cell", 10.5)
    # ribbon web
    s.r(ox + 220, hy + 110, 70, 120, fill="#333", stroke="#000", op=0.85)
    s.t(ox + 300, hy + 200, "ribbon (5P shown)", 10.5)
    # split conductors in comb
    comb_y = hy + 20
    s.r(ox + 150, comb_y - 8, 280, 16, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 436, comb_y + 4, "comb (~3 mm pitch)", 10)
    xs_ = [ox + 190 + i * 30 for i in range(5)]
    for i, x in enumerate(xs_):
        if i == 2:
            continue
        s.path(f"M{ox+230+i*8},{hy+110} C{ox+230+i*8},{hy+80} {x},{comb_y+40} {x},{comb_y}", stroke="#333", sw=4)
        s.l(x, comb_y, x, comb_y - 30, stroke="#333", sw=4)
        s.l(x, comb_y - 30, x, comb_y - 42, stroke=C["copper"], sw=2.5)
    # working conductor offset toward nest axis
    s.path(f"M{ox+246},{hy+110} C{ox+246},{hy+40} {nx},{hy-10} {nx},{ty+120}", stroke="#333", sw=4)
    s.l(nx, ty + 120, nx, ty + 96, stroke=C["copper"], sw=2.5)
    s.r(nx - 16, ty + 140, 32, 12, fill=C["printed"], stroke=C["printed_d"])
    s.t(nx + 22, ty + 150, "fork (servo) holds conductor k, 3-8 mm behind the rear face", 10)
    s.t(nx + 22, ty + 190, "neighbours stay in the comb: k stands out by a + 2.7 mm (8.7-14.7)", 10, fill=C["red"])
    s.t(nx + 22, ty + 204, "a = jaw-half depth, unmeasured; copper sets at R 9-47 mm [calc w3 2]", 10, fill=C["red"])
    # axes
    s.l(ox + 60, hy + 200, ox + 120, hy + 200, arrow=True)
    s.t(ox + 124, hy + 204, "X", 11, bold=True)
    s.l(ox + 60, hy + 200, ox + 60, hy + 140, arrow=True)
    s.t(ox + 56, hy + 134, "Y", 11, bold=True)
    s.t(ox + 60, hy + 222, "(Z out of page)", 9.5, fill=C["grey"])
    # stub magazine
    mx, my = ox + 640, oy + 420
    s.r(mx, my, 90, 120, fill=C["printed"], stroke=C["printed_d"])
    for i in range(5):
        s.r(mx + 15, my + 12 + i * 20, 60, 10, fill=C["contact"], stroke=C["contact_d"])
    s.lines(mx, my + 138, ["stub magazine", "(pin drags bottom stub", " out: drag feeder)"], 10)
    # cutter squeezer
    cx, cy = ox + 470, oy + 560
    s.r(cx, cy, 130, 70, fill=C["printed"], stroke=C["printed_d"])
    s.poly([(cx + 20, cy + 35), (cx + 70, cy + 25), (cx + 70, cy + 45)], fill=C["steel"], stroke=C["steel_d"])
    s.lines(cx, cy + 88, ["pull slot: backed plate on the", "box's rear walls, lance relieved;", "tip plate (grounded) + backlight"], 10)
    # camera
    s.r(ox + 90, oy + 110, 60, 34, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 120, oy + 158, "ELP camera", 10, anchor="middle")
    s.l(ox + 150, oy + 128, nx - 10, ty + 20, stroke=C["blue"], dash="4,3")
    # sequence panel
    sx, sy = 890, 80
    s.r(sx, sy, 400, 700, stroke="#ccc")
    s.t(sx + 14, sy + 24, "One conductor", 13, bold=True)
    seq = [
        "1  Fetch: pin up into the bottom stub's pilot hole;",
        "   drag it out of the magazine (drag feeder).",
        "2  Load: carry the contact in 1 mm above the anvil,",
        "   then set it down; the flap drops into the neck.",
        "3  Hold: pusher closes to a small force rise.",
        "4  Shear: a servo blade slides down the die's rear",
        "   face and cuts the tab before any wire arrives.",
        "5  Look: backlit picture of conductor k's tip;",
        "   splayed tips go to a twist or a question.",
        "6  Present: fork stands k out by a + 2.7 mm onto",
        "   the nest axis, corrected from the picture.",
        "7  Feed: Y creeps until green (or a set distance",
        "   from the tip plate); only conductor k may read.",
        "8  Crimp: full stroke, run whole on the ESP32.",
        "9  Open; side frame, including the window.",
        "10 Lift 1-1.7 mm, then draw back (lance clear).",
        "11 Proof pull at the pull slot: ~20 N on the",
        "   clamp's load cell, box's rear walls on steel.",
        "12 Fork lays k back in the comb; index, or skip",
        "   J2 cavity 3 / J7's trimmed conductor.",
        "",
        "~90-100 s per crimp, ~80-90 min per unit [calc 10].",
        "",
        "Force of the crimp stays inside the tool head.",
        "The carriage sees: a few N carrying the contact,",
        "a touch on the blade or tip plate, the 20 N pull.",
        "",
        "Carriage: three short rails + NEMA 17s, or a",
        "bed-slinger printer (bed = tool on Y,",
        "head = ribbon in X and Z).",
    ]
    s.lines(sx + 14, sy + 50, seq, 10.5, dy=15)
    s.save("a2-ribbon-to-fixed-tool.svg")


# ---------------------------------------------------------------------------
def sketch_a3():
    s = S(1320, 820, "A3  The tool travels to a ribbon that never moves: the fixture stands on edge (schematic)",
          "Left: looking along the conductors (Y into the page), 1 mm = 14 px, jaw sizes assumed. Right: plan of the table (Z out of the page).")
    s.legend(16, 72)
    ox, oy = 30, 80
    s.r(ox, oy, 640, 720, stroke="#ccc")
    s.t(ox + 14, oy + 22, "End view: the working conductor drawn out of the ribbon's plane", 12, bold=True)
    k = 14.0
    xf = ox + 110                 # the ribbon's plane (vertical)
    yk = oy + 470                 # working conductor's height
    a = 9.0
    xk = xf + (a + 2.7) * k
    # comb body on edge
    s.r(xf - 60, oy + 250, 26, 360, fill=C["printed"], stroke=C["printed_d"])
    s.lines(xf - 100, oy + 632, ["fixture on edge: comb slots", "stacked in Z at 2.5 mm", "(XHP cavity pitch)"], 10)
    # neighbours, crimped, barrels opening +X (away from the plane)
    for i in range(-4, 4):
        if i == 0:
            continue
        yy = yk + i * 2.5 * k
        s.r(xf - 1.25 * k, yy - 0.975 * k, 2.6 * k, 1.95 * k, fill="none", stroke=C["contact_d"], sw=1.2)
        s.l(xf - 1.05 * k, yy - 0.975 * k, xf - 1.05 * k, yy + 0.975 * k, stroke=C["contact_d"], sw=3)
        s.c(xf, yy, 0.85 * k, fill="#333", stroke="#000")
        s.c(xf, yy, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    s.callout(xf + 1.35 * k, yk - 4 * 2.5 * k, ox + 14, oy + 215, ["neighbours,", "already crimped:", "barrels open away", "from the plane"], 10)
    # empty slot where k came from
    s.c(xf, yk, 0.85 * k, fill="none", stroke=C["grey"], sw=1)
    s.l(xf + 0.85 * k, yk, xk - 0.85 * k, yk, stroke="#333", sw=4, dash="6,4")
    # working conductor and its contact (floor toward the fixture)
    s.r(xk - 1.25 * k, yk - 0.975 * k, 2.6 * k, 1.95 * k, fill="none", stroke=C["contact_d"], sw=1.6)
    s.l(xk - 1.05 * k, yk - 0.975 * k, xk - 1.05 * k, yk + 0.975 * k, stroke=C["contact_d"], sw=3)
    s.c(xk, yk, 0.85 * k, fill="#333", stroke="#000")
    s.c(xk, yk, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    # jaws: long axis along Z, tip down (4 mm below the nest)
    tip_y = yk + 4 * k
    top_y = oy + 150
    anvil_r = xk - 1.25 * k
    anvil_l = anvil_r - a * k
    s.r(anvil_l, top_y, a * k, tip_y - top_y, fill=C["steel"], stroke=C["steel_d"], op=0.75)
    s.r(xk + 1.7 * k, top_y, 8 * k, tip_y - top_y, fill=C["steel"], stroke=C["steel_d"], op=0.75)
    s.t((anvil_l + anvil_r) / 2, top_y + 60, "anvil half", 10.5, anchor="middle", bold=True)
    s.t((anvil_l + anvil_r) / 2, top_y + 74, "depth a", 10.5, anchor="middle")
    s.t((anvil_l + anvil_r) / 2, top_y + 88, "(6-12 mm?)", 10.5, anchor="middle")
    s.t(xk + 1.7 * k + 4 * k, top_y + 60, "punch half", 10.5, anchor="middle", bold=True)
    s.l(xk + 11 * k, top_y + 120, xk + 2 * k, top_y + 120, arrow=True, red=True)
    s.lines(xk + 10.2 * k, top_y + 140, ["jaws close in X,", "normal to the", "ribbon's plane"], 10, fill=C["red"])
    s.l(anvil_l - 10, tip_y, xk + 10 * k, tip_y, stroke=C["red"], dash="4,3", sw=1)
    s.t(xk + 10.2 * k, tip_y + 4, "jaw tip (down)", 10, fill=C["red"])
    # stand-out dimension
    dy = tip_y + 2.5 * k
    s.l(xf, dy, xk, dy, stroke=C["red"], sw=1.4)
    s.l(xf, dy - 6, xf, dy + 6, stroke=C["red"], sw=1.4)
    s.l(xk, dy - 6, xk, dy + 6, stroke=C["red"], sw=1.4)
    s.t(xk + 12, dy + 4, "stand-out a + 2.7 mm = 8.7-14.7 mm [calc w3 2]", 10.5, fill=C["red"])
    # side-puller finger
    s.r(xk - 0.6 * k, yk + 1.1 * k, 1.2 * k, 1.2 * k, fill=C["printed"], stroke=C["printed_d"])
    s.callout(xk, yk + 1.7 * k, xf + 30, oy + 690, ["side-puller finger (behind the jaw's rear face)"], 10)
    # module top: gantry plate and pusher
    s.r(anvil_l - 10, oy + 100, 18 * k + a * k, 18, fill=C["bought"], stroke=C["bought_d"])
    s.t(anvil_l, oy + 94, "gantry Z plate (kinematic mount + pogo pins)", 10)
    s.r(xk + 11 * k, oy + 124, 70, 44, fill=C["bought"], stroke=C["bought_d"])
    s.lines(xk + 11 * k + 4, oy + 140, ["pusher on the", "lower handle"], 9.5)
    s.lines(xk + 11 * k - 10, oy + 184, ["force loop closes", "inside the module"], 10, fill=C["green"])
    # tip camera
    s.r(ox + 470, yk + 9 * k, 70, 30, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 470, yk + 9 * k + 46, ["tip camera + backlight:", "k's tip, before the slide-on"], 10)
    s.lines(ox + 14, oy + 44, ["The jaw's long axis runs along the row (Z), so the anvil half spans the neighbours;",
                                "conductor k is drawn out in X until the anvil half's back face clears their boxes."], 10.5,
            fill=C["grey"])
    # ---------------- right: plan ----------------
    ox2, oy2 = 690, 80
    s.r(ox2, oy2, 600, 720, stroke="#ccc")
    s.t(ox2 + 14, oy2 + 22, "Plan of the table (gantry X-Y over a fixed bed)", 12, bold=True)
    fx, fy = ox2 + 150, oy2 + 360
    # web clamp and comb on edge: narrow blocks along Y
    s.r(fx - 10, fy + 110, 20, 150, fill=C["printed"], stroke=C["printed_d"])
    s.lines(fx - 140, fy + 180, ["web clamp", "(ribbon on edge:", "plane = YZ)"], 10)
    s.r(fx - 10, fy + 20, 20, 60, fill=C["printed"], stroke=C["printed_d"])
    s.t(fx - 16, fy + 50, "comb", 10, anchor="end")
    s.l(fx, fy + 110, fx, fy + 20, stroke="#333", sw=8)
    s.l(fx, fy + 20, fx, fy - 10, stroke="#333", sw=5)
    s.l(fx, fy - 10, fx, fy - 20, stroke=C["copper"], sw=3)
    s.t(fx - 16, fy - 16, "tips +Y", 10, anchor="end")
    # conductor k drawn out in X
    xk2 = fx + 70
    s.path(f"M{fx},{fy + 70} C{fx + 10},{fy + 40} {xk2},{fy + 40} {xk2},{fy + 10}", stroke="#333", sw=4)
    s.l(xk2, fy + 10, xk2, fy - 12, stroke=C["copper"], sw=2.5)
    s.t(xk2 + 8, fy + 30, "conductor k, drawn out in X", 10)
    # module approaching
    s.r(xk2 - 30, fy - 150, 60, 80, fill=C["steel"], stroke=C["steel_d"])
    s.lines(xk2 + 38, fy - 124, ["crimp module slides -Y", "onto k's corrected axis;", "rises out through the mouth"], 10)
    s.l(xk2, fy - 66, xk2, fy - 22, arrow=True, red=True, sw=1.6)
    # front plate, rear clamp, housing slide on the fixture
    s.r(fx - 40, fy - 60, 30, 14, fill=C["printed"], stroke=C["printed_d"])
    s.t(fx - 46, fy - 49, "front plate", 9.5, anchor="end")
    s.r(fx - 30, oy2 + 170, 40, 50, fill=C["bought"], stroke=C["bought_d"])
    s.lines(fx - 36, oy2 + 186, ["housing slide", "(NEMA 17 + cell)"], 9.5, anchor="end")
    # tip camera and backlight across X
    s.r(ox2 + 440, fy - 30, 60, 30, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox2 + 470, fy + 14, "tip camera", 10, anchor="middle")
    s.l(ox2 + 440, fy - 15, xk2 + 6, fy - 15, stroke=C["blue"], dash="4,3")
    s.r(fx - 60, fy - 30, 12, 30, fill="#fff", stroke=C["grey"])
    s.t(fx - 64, fy - 34, "backlight", 9.5, anchor="end", fill=C["grey"])
    # post column
    px, py = ox2 + 470, oy2 + 150
    s.r(px - 40, py, 80, 40, fill=C["printed"], stroke=C["printed_d"])
    s.r(px - 7, py + 44, 14, 44, fill=C["contact"], stroke=C["contact_d"])
    s.lines(px - 70, py + 110, ["post column: contacts on", "wired 0.64 mm header pins;", "the tool picks one moving +Y"], 10)
    # rack
    s.r(ox2 + 40, oy2 + 50, 520, 60, fill="none", stroke=C["grey"], dash="5,3")
    s.t(ox2 + 50, oy2 + 70, "module rack: crimp (SN-2549 or a4b head) | strip (Klein) | cut (flush cutters)", 10.5)
    for i in range(3):
        s.r(ox2 + 70 + i * 150, oy2 + 80, 90, 22, fill=C["steel"], stroke=C["steel_d"])
    # far end
    s.r(ox2 + 40, oy2 + 640, 120, 40, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox2 + 44, oy2 + 656, ["far-end block", "(identity, touch-off)"], 9.5)
    s.path(f"M{fx},{fy + 260} C{fx},{oy2 + 660} {ox2 + 220},{oy2 + 660} {ox2 + 160},{oy2 + 660}", stroke=C["wire"], sw=2)
    s.lines(ox2 + 250, oy2 + 560, ["After the last conductor: the front plate squares", "the noses, the rear clamp closes behind the",
                                    "insulation crimps, and the housing slide pushes", "the XHP onto the whole row. Every crimp comes out",
                                    "upright, in cavity order; no stored feed."], 10.5, fill=C["grey"])
    s.save("a3-tool-travels.svg")


# ---------------------------------------------------------------------------
def sketch_a4():
    s = S(1180, 820, "A4  SN jaws in a guided die set, slow eccentric drive (schematic front section)",
          "Force loop: eccentric shaft -> bushings -> steel side plates -> base -> disc springs -> load cell -> lower die -> upper die -> ram.")
    s.legend(16, 72)
    ox, oy = 30, 80
    cx = ox + 330
    # base
    s.r(ox + 80, oy + 620, 500, 40, fill=C["steel"], stroke=C["steel_d"])
    s.t(cx, oy + 646, "base (steel)", 10.5, anchor="middle")
    # side plates
    s.r(ox + 90, oy + 110, 30, 510, fill=C["steel"], stroke=C["steel_d"])
    s.r(ox + 540, oy + 110, 30, 510, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 60, oy + 360, "laser-cut", 10, anchor="end")
    s.t(ox + 60, oy + 374, "side plates", 10, anchor="end")
    s.t(ox + 60, oy + 388, "in tension", 10, anchor="end")
    # shaft + eccentric
    sy = oy + 170
    s.r(ox + 90, sy - 8, 480, 16, fill=C["steel_d"], stroke="#222")
    s.c(ox + 105, sy, 14, fill=C["printed"], stroke=C["printed_d"])
    s.c(ox + 555, sy, 14, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 105, sy - 22, "bronze bushing", 9.5, anchor="middle")
    s.c(cx, sy + 8, 40, fill=C["steel"], stroke=C["steel_d"])
    s.c(cx, sy, 4, fill=C["ink"])
    s.t(cx + 50, sy - 20, "eccentric e = 2-2.5 mm (stroke 4-5 mm)", 10.5)
    # gearmotor
    s.r(ox + 580, sy - 40, 110, 80, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 586, sy - 22, ["NEMA 23 + 10:1", "planetary, or a worm", "gearmotor, or a", "150-200 mm hand lever"], 9.5)
    s.r(ox + 70, sy - 20, 16, 40, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 66, sy + 40, "AS5600 on shaft end", 9.5, anchor="end")
    # ram
    ry = sy + 48
    s.r(ox + 170, ry, 320, 40, fill=C["steel"], stroke=C["steel_d"])
    s.t(cx, ry + 26, "ram plate", 10.5, anchor="middle")
    # guide rods
    for gx in (ox + 190, ox + 470):
        s.r(gx - 6, ry - 40, 12, 360, fill="#d0d6da", stroke=C["steel_d"])
    s.t(ox + 470 + 12, ry + 20, "8 mm ground rods", 10)
    s.t(ox + 470 + 12, ry + 34, "in bushings", 10)
    # upper holder + die
    s.r(cx - 70, ry + 40, 140, 60, fill=C["steel"], stroke=C["steel_d"])
    s.t(cx, ry + 76, "upper holder (laminated)", 10, anchor="middle")
    s.r(cx - 40, ry + 100, 80, 40, fill="#b7c0c6", stroke="#222")
    s.t(cx + 46, ry + 126, "SN punch die", 10)
    # work
    wy = ry + 150
    s.r(cx - 12, wy, 24, 18, fill=C["contact"], stroke=C["contact_d"])
    s.t(cx - 250, wy - 20, "contact + conductor", 10.5)
    s.l(cx - 150, wy - 16, cx - 14, wy + 9, stroke=C["grey"], sw=0.8)
    # lower die + holder
    s.r(cx - 40, wy + 20, 80, 40, fill="#b7c0c6", stroke="#222")
    s.t(cx + 46, wy + 46, "SN anvil die", 10)
    s.r(cx - 70, wy + 60, 140, 60, fill=C["steel"], stroke=C["steel_d"])
    s.t(cx, wy + 96, "lower holder (fixed reference)", 10, anchor="middle")
    # locator
    s.r(cx - 110, wy - 4, 36, 70, fill=C["printed"], stroke=C["printed_d"])
    s.t(cx - 114, wy + 70, "a1 locator", 10, anchor="end")
    # load cell + disc springs
    lcy = wy + 120
    s.r(cx - 40, lcy, 80, 26, fill=C["bought"], stroke=C["bought_d"])
    s.t(cx + 50, lcy + 18, "500 kg (4.9 kN) button cell: die force, directly", 10)
    dsy = lcy + 26
    for i in range(4):
        y = dsy + i * 16
        if i % 2 == 0:
            s.poly([(cx - 60, y + 14), (cx, y + 2), (cx + 60, y + 14)], close=False, stroke="#222", sw=3)
        else:
            s.poly([(cx - 60, y + 2), (cx, y + 14), (cx + 60, y + 2)], close=False, stroke="#222", sw=3)
    s.r(cx - 50, dsy + 64, 100, oy + 620 - (dsy + 64), fill=C["steel"], stroke=C["steel_d"])
    s.t(cx + 70, dsy + 30, "disc springs, preloaded ~3.5 kN", 10)
    s.t(cx + 70, dsy + 44, "die contact set 0.17-0.28 mm above BDC:", 10)
    s.t(cx + 70, dsy + 58, "dies meet every stroke, ~3.6 kN at BDC [calc w3 1]", 10)
    # re-touch indicator across the holders
    s.r(cx + 118, ry + 60, 12, 110, fill=C["bought"], stroke=C["bought_d"])
    s.t(cx + 152, ry + 96, "0.001 mm indicator", 9.5)
    s.t(cx + 152, ry + 109, "across the holders", 9.5)
    s.t(cx + 152, ry + 122, "(re-touch at ~10 N)", 9.5)
    # camera
    s.r(ox + 700, wy - 20, 70, 40, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 735, wy + 36, "camera: side view", 10, anchor="middle")
    s.l(ox + 700, wy, cx + 20, wy + 9, stroke=C["blue"], dash="4,3")
    s.lines(ox + 700, oy + 560, [
        "Peak shaft torque with the stack",
        "engaged: ~1.6-2.0 N*m, 2.0-3.0 with",
        "friction [calc w3 1].",
        "",
        "BDC is geometry: every turn reaches",
        "the same bottom until it stalls.",
        "Re-touch at ~10 N: a 0.001 mm indicator",
        "across the holders reads crimp height.",
    ], 10.5, fill=C["grey"])
    s.save("a4-die-set.svg")


# ---------------------------------------------------------------------------
def sketch_a5():
    s = S(1240, 720, "A5  Two squeezes on a non-ratchet precision plier (schematic)",
          "Left: the plier jaw with four die widths; the contact moves from the 1.6 die to the 1.9 die by its wire. Right: what the load cell sees.")
    s.legend(16, 72)
    ox, oy = 30, 80
    s.r(ox, oy, 560, 610, stroke="#ccc")
    # jaw with 4 dies along it
    jy = oy + 180
    s.poly([(ox + 60, jy - 60), (ox + 480, jy - 20), (ox + 480, jy - 4), (ox + 60, jy - 4)], fill=C["steel"], stroke=C["steel_d"])
    s.poly([(ox + 60, jy + 60), (ox + 480, jy + 20), (ox + 480, jy + 4), (ox + 60, jy + 4)], fill=C["steel"], stroke=C["steel_d"])
    s.c(ox + 480, jy, 10, fill=C["bg"], stroke=C["steel_d"])
    s.t(ox + 480, jy + 36, "pivot", 10, anchor="middle")
    widths = [(1.0, ox + 110), (1.4, ox + 180), (1.6, ox + 250), (1.9, ox + 330)]
    for w, x in widths:
        s.r(x - w * 8, jy - 8, w * 16, 16, fill=C["bg"], stroke=C["steel_d"])
        s.t(x, jy - 40, f"{w}", 11, anchor="middle", bold=(w in (1.6, 1.9)))
    s.t(ox + 60, jy - 76, "die widths (mm) along the jaw [mfr]", 10.5)
    s.t(ox + 250, jy + 80, "squeeze 1:", 10.5, anchor="middle", bold=True)
    s.t(ox + 250, jy + 94, "conductor barrel", 10.5, anchor="middle")
    s.t(ox + 330, jy + 80, "squeeze 2:", 10.5, anchor="middle", bold=True)
    s.t(ox + 330, jy + 94, "insulation barrel", 10.5, anchor="middle")
    s.path(f"M{ox+250},{jy+110} C{ox+270},{jy+150} {ox+310},{jy+150} {ox+330},{jy+110}", stroke=C["red"], sw=1.6)
    s.l(ox + 326, jy + 116, ox + 330, jy + 110, arrow=True, red=True)
    s.lines(ox + 60, jy + 180, [
        "Between squeezes the carriage moves the crimped contact by its wire:",
        "sideways by the die spacing, and axially ~1.5-2.5 mm so the",
        "insulation barrel sits in the 1.8 mm-thick die [calc 11].",
        "",
        "Squeeze 1 stop: the conductor barrel's rear edge 0.1-0.2 mm proud",
        "of the die for a bellmouth, set by a printed stop. The 1.6 die is",
        "1.8 mm thick: it fits a ~1.8 mm (genuine) barrel; on a clone-length",
        "barrel (1.25-1.5 mm) it reaches the box [sl w3 5].",
        "",
        "Scissor action: the dies close on an arc about one pivot.",
        "No ratchet, no hard stop: closure is the machine's decision.",
    ], 10.5)
    # right: force curves
    gx, gy, gw, gh = 640, 130, 560, 440
    s.r(gx, gy, gw, gh, stroke="#ccc")
    s.l(gx + 50, gy + gh - 40, gx + gw - 20, gy + gh - 40, arrow=True)
    s.l(gx + 50, gy + gh - 40, gx + 50, gy + 20, arrow=True)
    s.t(gx + gw - 20, gy + gh - 20, "grip position (closing)", 10.5, anchor="end")
    s.t(gx + 56, gy + 30, "grip force", 10.5)
    X0, Y0 = gx + 50, gy + gh - 40
    def curve(pts, col, sw=2, dash=None):
        s.poly([(X0 + x, Y0 - y) for x, y in pts], close=False, stroke=col, sw=sw, dash=dash)
    # squeeze 1 (conductor)
    pts = [(0, 0), (120, 4), (220, 20), (300, 45), (350, 80), (380, 130), (400, 200), (412, 280), (420, 360)]
    curve(pts, C["blue"])
    s.t(X0 + 250, Y0 - 150, "squeeze 1: wings curl, then", 10.5, fill=C["blue"])
    s.t(X0 + 250, Y0 - 136, "strands compact: the knee", 10.5, fill=C["blue"])
    s.l(X0 + 395, Y0 - 185, X0 + 395, Y0, stroke=C["red"], dash="4,3")
    s.t(X0 + 300, Y0 - 330, "stop: a set force,", 10, fill=C["red"])
    s.t(X0 + 300, Y0 - 316, "or a set position past", 10, fill=C["red"])
    s.t(X0 + 300, Y0 - 302, "the knee (taught)", 10, fill=C["red"])
    s.l(X0 + 390, Y0 - 300, X0 + 395, Y0 - 190, stroke=C["red"], sw=0.8)
    pts2 = [(0, 0), (140, 3), (240, 12), (300, 26), (340, 45), (360, 62)]
    curve(pts2, C["green"])
    s.t(X0 + 160, Y0 - 40, "squeeze 2: insulation wings on silicone,", 10.5, fill=C["green"])
    s.t(X0 + 160, Y0 - 26, "between a floor (fits the cavity) and a ceiling (cuts)", 10.5, fill=C["green"])
    pts3 = [(0, 0), (170, 3), (280, 12), (350, 26), (400, 50), (425, 90), (440, 150), (450, 230)]
    curve(pts3, C["grey"], sw=1.2, dash="5,3")
    s.t(X0 + 456, Y0 - 236, "no wire (reference):", 10, fill=C["grey"])
    s.t(X0 + 456, Y0 - 222, "knee arrives later", 10, fill=C["grey"])
    s.save("a5-two-squeeze.svg")


if __name__ == "__main__":
    sketch_a1(); sketch_a2(); sketch_a3(); sketch_a4(); sketch_a5()
    print("written:", sorted(f for f in os.listdir(HERE) if f.endswith(".svg")))
