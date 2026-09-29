"""Wave-3 sketches for the hand-tool-as-press explorer.

Run: python3 wave3_sketches.py   (writes a4c-t-then-c.svg and flag-seat.svg)

Side views are schematic. The end view at C in a4c-t-then-c.svg is drawn to
scale from cited dimensions (xh-facts §1 clone drawings; machine-that-sees-and-learns
calc w3 §7; this explorer's calc w3 §4). Nothing comes from a measured tool.
"""
import os
from make_sketches import S, C, HERE


def zig(s, x0, x1, y0, y1, n=4, sw=2):
    """A spring drawn as a zigzag from (x0, y0) down to (x1, y1)."""
    pts = []
    for i in range(2 * n + 1):
        t = i / (2 * n)
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        dx = 0 if i in (0, 2 * n) else (8 if i % 2 else -8)
        pts.append((x + dx, y))
    s.poly(pts, close=False, stroke="#444", sw=sw)


# ---------------------------------------------------------------------------
def sketch_a4c():
    s = S(1340, 960, "A4c  Tack at T, crimp in a one-nest SN die set at C (schematic side views; end view at C to scale)",
          "Left: the two stations the printer's stage carries each conductor to. Right: looking along the conductor at C, "
          "1 mm = 20 px, from cited dimensions.")
    s.legend(16, 74)

    # ---------------- left top: station T ----------------
    ox, oy = 20, 90
    s.r(ox, oy, 700, 370, stroke="#ccc")
    s.t(ox + 12, oy + 20, "At T: lay-in, tack, then the straight-down look (nothing over the conductor barrel)", 11.5, bold=True)
    fy = oy + 300
    s.r(ox + 40, fy + 30, 620, 26, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 50, fy + 48, "T's printed frame", 10)
    s.r(ox + 290, fy + 12, 140, 18, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 440, fy + 26, "20 kg bar cell under the nest", 10)
    s.r(ox + 290, fy - 20, 140, 32, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 360, fy + 2, "steel insert", 9.5, anchor="middle", fill="#fff")
    # contact on the nest: insulation barrel left, conductor barrel, box right
    fl = fy - 20
    s.r(ox + 300, fl - 50, 34, 50, fill=C["contact"], stroke=C["contact_d"], op=0.9)   # tacked insulation barrel
    s.r(ox + 356, fl - 36, 52, 36, fill=C["contact"], stroke=C["contact_d"], op=0.6)   # open conductor barrel
    s.r(ox + 430, fl - 56, 50, 56, fill=C["contact"], stroke=C["contact_d"])           # box
    s.r(ox + 430, fl - 6, 60, 6, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 455, fl - 26, "box", 10, anchor="middle")
    s.poly([(ox + 470, fl), (ox + 488, fl + 14), (ox + 490, fl + 10), (ox + 478, fl)], fill=C["contact"], stroke=C["contact_d"])
    s.t(ox + 494, fl + 22, "lance in a relief", 9.5)
    # wire from the key
    s.r(ox + 60, fl - 44, 240, 36, fill="#333", stroke="#000")
    for i in range(5):
        s.l(ox + 300, fl - 34 + i * 6, ox + 416, fl - 34 + i * 6, stroke=C["copper"], sw=1.4)
    s.r(ox + 60, fl - 60, 170, 16, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 64, fl + 12, "key k pressed down (pallet on the stage)", 10)
    # former over the insulation barrel only
    s.r(ox + 298, fl - 130, 38, 76, fill=C["steel_d"], stroke=C["ink"])
    s.r(ox + 288, fl - 160, 58, 26, fill=C["printed"], stroke=C["printed_d"])
    s.l(ox + 288, fl - 147, ox + 170, fl - 147, stroke=C["printed_d"], sw=5)
    s.r(ox + 120, fl - 170, 50, 40, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 60, fl - 196, ["35 kg*cm servo, lever,", "loose screw stop"], 10)
    s.callout(ox + 318, fl - 100, ox + 170, fl - 100, ["former cut from a spare", "SN jaw's insulation", "section: the tack is the", "SN's own stroke, paused"], 10, anchor="end")
    # top camera straight down
    s.r(ox + 360, oy + 40, 60, 30, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 426, oy + 60, "top camera, straight down, 4-8 lighting states", 10)
    s.l(ox + 390, oy + 70, ox + 385, fl - 40, stroke=C["blue"], dash="4,3")
    s.l(ox + 390, oy + 70, ox + 400, fl - 40, stroke=C["blue"], dash="4,3")
    # side camera
    s.r(ox + 600, fl - 50, 60, 28, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 630, fl - 58, "side camera", 10, anchor="middle")
    s.l(ox + 600, fl - 36, ox + 490, fl - 36, stroke=C["blue"], dash="4,3")
    s.lines(ox + 470, oy + 84, ["pass: go on to C", "fail: the conductor backs out;", "it costs a contact, not an end"], 10, fill=C["red"])

    # ---------------- left bottom: station C ----------------
    oy2 = oy + 390
    s.r(ox, oy2, 700, 450, stroke="#ccc")
    s.t(ox + 12, oy2 + 20, "At C: carried in 1.0-1.7 mm high, set down on the seat, crimped by the eccentric", 11.5, bold=True)
    ay = oy2 + 300   # anvil top
    s.r(ox + 290, ay, 150, 40, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 365, ay + 25, "anvil (one nest)", 9.5, anchor="middle", fill="#fff")
    s.r(ox + 290, ay + 40, 150, 16, fill=C["bought"], stroke=C["bought_d"])
    s.t(ox + 450, ay + 52, "500 kg button cell", 10)
    for i in range(3):
        y = ay + 56 + i * 12
        pts = [(ox + 300, y + (10 if i % 2 == 0 else 2)), (ox + 365, y + (2 if i % 2 == 0 else 10)),
               (ox + 430, y + (10 if i % 2 == 0 else 2))]
        s.poly(pts, close=False, stroke="#222", sw=3)
    s.t(ox + 450, ay + 80, "disc stack ~3.5 kN; die contact 0.17-0.28 above BDC", 10)
    s.r(ox + 270, ay + 92, 190, 16, fill=C["steel"], stroke=C["steel_d"])
    # seat ledge and stop in front of the anvil
    s.r(ox + 440, ay, 56, 10, fill=C["steel_d"], stroke=C["ink"])
    s.r(ox + 504, ay - 50, 8, 60, fill=C["printed"], stroke=C["printed_d"])
    s.callout(ox + 470, ay + 5, ox + 560, ay + 30, ["seat: floor ledge for the box's", "front mm, no side walls;", "retractable front stop"], 10)
    # contact set down (solid)
    s.r(ox + 300, ay - 50, 34, 50, fill=C["contact"], stroke=C["contact_d"], op=0.9)
    s.r(ox + 356, ay - 36, 52, 36, fill=C["contact"], stroke=C["contact_d"], op=0.6)
    s.r(ox + 440, ay - 56, 50, 56, fill=C["contact"], stroke=C["contact_d"])
    # contact carried high (dashed)
    lift = 28
    for (x, w, h) in ((300, 34, 50), (356, 52, 36), (440, 50, 56)):
        s.r(ox + x - 40, ay - h - lift, w, h, fill="none", stroke=C["contact_d"], dash="4,3")
    s.l(ox + 520, ay - 90, ox + 560, ay - 90, stroke=C["red"])
    s.lines(ox + 564, ay - 100, ["carry in high (+Y),", "then set down 1.0-1.7:", "the lance never meets", "the anvil face"], 10, fill=C["red"])
    # wire and key
    s.r(ox + 60, ay - 44, 240, 36, fill="#333", stroke="#000")
    s.r(ox + 60, ay - 60, 170, 16, fill=C["printed"], stroke=C["printed_d"])
    s.t(ox + 64, ay - 66, "key k (neighbours ride 5 mm up)", 10)
    # punch, T-section holder, eccentric
    s.r(ox + 300, ay - 150, 110, 70, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 355, ay - 110, "one-nest punch", 9.5, anchor="middle", fill="#fff")
    s.r(ox + 270, ay - 200, 170, 50, fill=C["steel"], stroke=C["steel_d"])
    s.t(ox + 355, ay - 170, "holder (widens above the neighbours)", 9.5, anchor="middle", fill="#fff")
    s.c(ox + 355, ay - 235, 26, fill=C["steel"], stroke=C["steel_d"])
    s.c(ox + 355, ay - 241, 4, fill=C["ink"])
    s.lines(ox + 60, ay - 250, ["eccentric e 2.0-2.5 mm,", "NEMA 23 + 10:1 planetary;", "ESP32 runs the stroke"], 10)
    # indicator
    s.r(ox + 250, ay - 150, 10, 190, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ox + 60, ay + 60, ["0.001 mm indicator across", "the holders: re-touch at ~10 N", "= crimp height #1"], 10)
    s.l(ox + 250, ay + 40, ox + 210, ay + 56, stroke=C["grey"], sw=0.8)
    s.lines(ox + 560, ay + 110, ["beside C: silhouette window", "(crimp height #2) and a", "backed pull plate"], 10, fill=C["grey"])

    # ---------------- right: end view at C, to scale ----------------
    rx, ry = 740, 90
    s.r(rx, ry, 580, 840, stroke="#ccc")
    s.t(rx + 12, ry + 20, "End view at C, punch at BDC (1 mm = 20 px; clone dimensions)", 11.5, bold=True)
    k = 20.0
    x0 = rx + 290
    y0 = ry + 520       # working contact's floor (anvil top)

    def box(xc, floor_y, w=1.95, h=2.4, lance=0.75, dash=None):
        s.r(xc - w / 2 * k, floor_y - h * k, w * k, h * k, fill="none", stroke=C["contact_d"], sw=1.6, dash=dash)
        s.poly([(xc - 0.25 * k, floor_y), (xc, floor_y + lance * k), (xc + 0.25 * k, floor_y)], fill=C["contact"],
               stroke=C["contact_d"])
    # anvil (one nest, 6.5 mm)
    s.r(x0 - 3.25 * k, y0, 6.5 * k, 3.0 * k, fill=C["steel"], stroke=C["steel_d"])
    s.t(x0, y0 + 1.8 * k, "anvil, one nest", 10, anchor="middle", fill="#fff")
    # working contact (tacked) and conductor
    box(x0, y0, lance=0.0)
    s.t(x0 + 1.1 * k, y0 - 2.6 * k, "", 9)
    s.c(x0, y0 - 1.05 * k, 0.85 * k, fill="#333", stroke="#000")
    s.c(x0, y0 - 1.05 * k, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    # neighbours at +/-5 mm, axis 5 mm up
    for sgn in (-1, 1):
        xc = x0 + sgn * 5 * k
        yc = y0 - 5 * k
        box(xc, yc + 1.05 * k)
        s.c(xc, yc, 0.85 * k, fill="#333", stroke="#000")
        s.c(xc, yc, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    # punch at BDC: narrow section 7.0 wide from 0.8 up to 6.65, holder wider above
    edge = y0 - 0.8 * k
    top_n = y0 - 6.65 * k
    s.r(x0 - 3.5 * k, top_n, 7.0 * k, edge - top_n, fill=C["steel"], stroke=C["steel_d"], op=0.55)
    s.r(x0 - 7.5 * k, top_n - 2.5 * k, 15.0 * k, 2.5 * k, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.t(x0, top_n - 1.0 * k, "holder widens above the neighbours (T-section)", 10, anchor="middle", fill="#fff")
    s.t(x0, top_n + 1.2 * k, "punch + holder neck", 10, anchor="middle")
    s.t(x0, top_n + 1.9 * k, "<= 7.45 mm wide", 10, anchor="middle")
    # dimension: free width between the crimped boxes at the neighbours' height
    yd = y0 - 5.2 * k
    xl = x0 - 5 * k + 0.975 * k
    xr = x0 + 5 * k - 0.975 * k
    s.l(xl, yd, xr, yd, stroke=C["red"], sw=1.2)
    s.l(xl, yd - 6, xl, yd + 6, stroke=C["red"])
    s.l(xr, yd - 6, xr, yd + 6, stroke=C["red"])
    s.lines(rx + 14, ry + 60, ["8.05 mm between the neighbours' crimped boxes; with 0.3 mm",
                               "clearance each side the punch and its holder neck stay",
                               "<= 7.45 mm wide up to ~5.9 mm above the crimping edge,",
                               "then widen [sl w3 §7; calc w3 §4]."], 10.5, fill=C["red"])
    # height of the narrow section
    xh = x0 + 11 * k
    s.l(xh, edge, xh, top_n, stroke=C["red"], sw=1.2)
    s.l(xh - 6, edge, xh + 6, edge, stroke=C["red"])
    s.l(xh - 6, top_n, xh + 6, top_n, stroke=C["red"])
    s.lines(xh + 8, (edge + top_n) / 2, ["~5.9 mm", "narrow"], 10, fill=C["red"])
    # neighbours' vertical extent
    xz = x0 - 7.8 * k
    s.l(xz, y0 - 3.05 * k, xz, y0 - 6.35 * k, stroke=C["contact_d"], sw=1.2)
    s.lines(rx + 14, y0 - 5.6 * k, ["neighbours k-1, k+1:", "crimped, axes 5 mm up;", "occupy Z 3.05-6.35"], 10, fill=C["contact_d"])
    # side camera band under the neighbours
    s.r(rx + 20, y0 - 2.85 * k, x0 - 3.6 * k - rx - 20, 2.85 * k, fill=C["bought"], stroke="none", op=0.25)
    s.lines(rx + 24, y0 - 1.9 * k, ["side camera sees", "Z 0-2.85 under", "the neighbours"], 10, fill=C["bought_d"])
    s.l(rx + 20, y0, rx + 560, y0, stroke=C["grey"], dash="3,3", sw=0.8)
    s.t(rx + 556, y0 - 4, "working floor = anvil top", 9.5, anchor="end", fill=C["grey"])
    s.lines(rx + 14, y0 + 90, ["The working contact is tacked (insulation barrel ~2.3-2.5 mm tall, drawn as its box).",
                               "Neighbour boxes 1.95 x 2.4 with the lance 0.6-0.9 mm below the floor [xh-facts §1].",
                               "A tacked contact carried in level passes an e = 2.0-2.5 mm eccentric's open punch",
                               "with 0.5-1.7 mm to spare [calc w3 §4]."], 10, fill=C["grey"])
    s.save("a4c-t-then-c.svg")


# ---------------------------------------------------------------------------
def sketch_flag_seat():
    s = S(1340, 950, "The flag seat: a contact already on its wire, carried clear of the anvil into the SN-2549 (schematic)",
          "Left: at C, section along the nest axis. Right: station P (a click pre-forms the insulation barrel) and station S "
          "(the snap), for a6b. In a6c the flag comes from a tack station instead.")
    s.legend(16, 74)
    # ---------------- left: the seat ----------------
    ox, oy = 20, 90
    s.r(ox, oy, 760, 840, stroke="#ccc")
    s.t(ox + 12, oy + 20, "At C: the SN-2549 open, the flag slid in at h, green at the stop", 11.5, bold=True)
    k = 26.0
    ay = oy + 480          # anvil top
    xr = ox + 330          # die rear face
    xf = xr + 3.8 * k      # die front face
    top = ay - 4.2 * k     # punch face, open
    # wire first, so the barrels draw over it
    h = 1.4
    fl = ay - h * k
    xib0 = xr + 0.1 * k
    xib1 = xib0 + 1.2 * k
    xcb0 = xib1 + 0.7 * k
    xcb1 = xcb0 + 1.5 * k
    xb0 = xf + 0.25 * k
    xb1 = xb0 + 2.0 * k
    s.r(ox + 40, fl - 1.9 * k, xib1 + 0.3 * k - ox - 40, 1.7 * k, fill="#333", stroke="#000")
    for i in range(5):
        yy = fl - 1.55 * k + i * 0.2 * k
        s.l(xib1 + 0.3 * k, yy, xcb1 + 0.15 * k, yy, stroke=C["copper"], sw=1.4)
    # dies
    s.r(xr, ay, xf - xr, 110, fill=C["steel"], stroke=C["steel_d"])
    s.t((xr + xf) / 2, ay + 60, "anvil", 10.5, anchor="middle", fill="#fff")
    s.r(xr, top - 110, xf - xr, 110, fill=C["steel"], stroke=C["steel_d"])
    s.t((xr + xf) / 2, top - 50, "punch (open)", 10.5, anchor="middle", fill="#fff")
    s.l(xr, top - 120, xr, ay + 125, stroke=C["steel_d"], dash="3,3", sw=0.8)
    s.l(xf, top - 120, xf, ay + 125, stroke=C["steel_d"], dash="3,3", sw=0.8)
    s.t(xr - 4, ay + 140, "rear face", 10, anchor="end", fill=C["steel_d"])
    s.t(xf + 4, ay + 140, "front face", 10, fill=C["steel_d"])
    # the flag at h
    s.r(xib0, fl - 2.6 * k, xib1 - xib0, 2.6 * k, fill=C["contact"], stroke=C["contact_d"], op=0.85)
    s.r(xcb0, fl - 1.55 * k, xcb1 - xcb0, 1.55 * k, fill=C["contact"], stroke=C["contact_d"], op=0.55)
    s.r(xb0, fl - 2.4 * k, xb1 - xb0, 2.4 * k, fill=C["contact"], stroke=C["contact_d"])
    s.r(xib0, fl, xb1 - xib0, 0.2 * k, fill=C["contact"], stroke=C["contact_d"])
    s.t((xb0 + xb1) / 2, fl - 1.1 * k, "box", 10.5, anchor="middle")
    lt = xb1 - 2.44 * k    # lance tip 2.44 mm behind the nose
    s.poly([(xb0 + 0.9 * k, fl + 0.2 * k), (lt, fl + 0.2 * k + 0.75 * k), (lt + 0.05 * k, fl + 0.2 * k + 0.6 * k),
            (xb0 + 1.1 * k, fl + 0.2 * k)], fill=C["contact"], stroke=C["contact_d"])
    s.callout(lt, fl + 0.9 * k, ox + 40, ay + 90, ["lance clear of the anvil:", "h >= lance + 0.2 = 0.8-1.1 mm"], 10)
    # rear U guide on a spring, behind the rear face
    gx0, gx1 = xr - 2.6 * k, xr - 0.6 * k
    s.r(gx0, fl - 0.3 * k, gx1 - gx0, 0.3 * k, fill=C["printed"], stroke=C["printed_d"])
    s.r(gx0, fl - 2.1 * k, 7, 1.8 * k, fill=C["printed"], stroke=C["printed_d"], op=0.7)
    zig(s, (gx0 + gx1) / 2, (gx0 + gx1) / 2, fl, ay + 70)
    s.r(gx0 - 10, ay + 70, gx1 - gx0 + 20, 12, fill=C["printed"], stroke=C["printed_d"])
    s.callout(gx0 + 4, fl - 1.2 * k, ox + 40, fl - 4.4 * k, ["rear U guide on the jacket,", "at h on a 1-3 N spring"], 10)
    # h dimension behind the guide
    xh = gx0 - 22
    s.l(xh, fl, xh, ay, stroke=C["red"], sw=1.2)
    s.l(xh - 6, fl, xh + 6, fl, stroke=C["red"])
    s.l(xh - 6, ay, xh + 6, ay, stroke=C["red"])
    s.t(xh - 8, ay - 8, "h = 1.1-1.7 mm", 10, anchor="end", fill=C["red"])
    s.l(xh - 30, ay, xr, ay, stroke=C["grey"], dash="3,3", sw=0.8)
    # opening dimension inside the rear of the die
    xo = xr - 8
    s.l(xo, top, xo, ay, stroke=C["red"], sw=1.2)
    s.l(xo - 6, top, xo + 6, top, stroke=C["red"])
    s.t(xo - 8, top + 14, "opening needed 3.6-4.9 mm", 10, anchor="end", fill=C["red"])
    # front ledge with keyed slot on a spring, under the box
    lx0, lx1 = xf + 0.1 * k, xb1 - 0.2 * k
    s.r(lx0, fl + 0.2 * k, lx1 - lx0, 0.3 * k, fill=C["printed"], stroke=C["printed_d"])
    zig(s, (lx0 + lx1) / 2 + 12, (lx0 + lx1) / 2 + 12, fl + 0.5 * k, ay + 70)
    s.r(lx0 - 4, ay + 70, lx1 - lx0 + 30, 12, fill=C["printed"], stroke=C["printed_d"])
    # wired front stop leaf
    sx = xb1 + 3
    s.r(sx, fl - 2.9 * k, 5, 3.1 * k, fill=C["steel_d"], stroke=C["ink"])
    s.c(sx + 34, fl - 3.5 * k, 9, fill="#35a853", stroke="#1d6b33")
    s.l(sx + 5, fl - 2.9 * k, sx + 27, fl - 3.3 * k, stroke=C["green"])
    s.callout(sx + 3, fl - 1.6 * k, ox + 580, fl - 2.6 * k, ["front stop: spring-steel leaf,", "preload 10-30 N, insulated,",
                                                        "wired: GREEN = box at the stop;", "stop pushing"], 10)
    s.callout(lx1 - 6, fl + 0.35 * k, ox + 580, ay + 30, ["front ledge: open-topped slot", "keyed to box and lance, at h", "on a 1-3 N spring"], 10)
    # amber on the jaws
    s.c(xr + 12, top - 130, 9, fill="#f2a900", stroke="#a06f00")
    s.t(xr + 26, top - 126, "AMBER: jaws wired; the punch meets the wings", 10)
    # push arrow, below the wire
    s.l(ox + 60, fl - 2.6 * k, ox + 180, fl - 2.6 * k, arrow=True, red=True, sw=1.8)
    s.t(ox + 60, fl - 2.6 * k - 8, "slide it box first until green", 10, fill=C["red"])
    s.lines(ox + 14, oy + 690, [
        "Treadle (single stage): amber, then the punch pushes the flag down onto the anvil against the",
        "1-3 N springs, curls and coins; the ratchet completes. The springs lift the crimp back to h: draw it out.",
        "Why a seat: the flag's grip on its wire (0.08-3.8 N pre-formed, 0.2-1.5 N tacked) is below the",
        "1-5 N that folds a lance dragged over the jaw's edge. Dragged on the anvil, the contact stops and",
        "the jacket keeps moving: the strip position is lost without a sign [htq §4; calc w3 §5].",
        "Opening at the nest: 3.6-4.9 mm (pre-formed), 3.6-4.4 mm (tacked); unmeasured on the SN-2549.",
        "Proportions schematic; contact dimensions from clone drawings [xh-facts §1]."], 10.5,
        fill=C["grey"])

    # ---------------- right top: station P ----------------
    px, py = 800, 90
    s.r(px, py, 520, 390, stroke="#ccc")
    s.t(px + 12, py + 20, "Station P (a6b): one click in a second SN-2549, no wire", 11.5, bold=True)
    kk = 34.0
    base = py + 300

    def endview(xc, wtop, htop, tips_in=0.0, label=""):
        # floor
        s.l(xc - 0.95 * kk, base, xc + 0.95 * kk, base, stroke=C["contact_d"], sw=3)
        # wings: from floor corners up to htop, spreading to wtop at the top
        s.l(xc - 0.95 * kk, base, xc - wtop / 2 * kk, base - htop * kk, stroke=C["contact_d"], sw=3)
        s.l(xc + 0.95 * kk, base, xc + wtop / 2 * kk, base - htop * kk, stroke=C["contact_d"], sw=3)
        if tips_in:
            s.l(xc - wtop / 2 * kk, base - htop * kk, xc - wtop / 2 * kk + tips_in * kk, base - htop * kk + 0.25 * kk,
                stroke=C["contact_d"], sw=3)
            s.l(xc + wtop / 2 * kk, base - htop * kk, xc + wtop / 2 * kk - tips_in * kk, base - htop * kk + 0.25 * kk,
                stroke=C["contact_d"], sw=3)
        s.lines(xc - 0.95 * kk - 10, base + 26, label, 10)
    endview(px + 90, 2.8, 3.0, label=["open kit contact:", "insulation wings", "2.46-3.0 wide"])
    endview(px + 260, 1.9, 2.6, tips_in=0.3, label=["after click k:", "narrowed to the die", "width 1.8-2.05, tips", "curled in, 2.3-3.0 tall"])
    # flag after snap: jacket inside
    endview(px + 430, 1.9, 2.6, tips_in=0.3, label=["after the snap (S):", "jacket pressed", "into the narrowed U"])
    s.c(px + 430, base - 1.2 * kk, 0.82 * kk, fill="#333", stroke="#000")
    s.c(px + 430, base - 1.2 * kk, 0.36 * kk, fill=C["copper"], stroke=C["copper"])
    s.lines(px + 12, py + 50, ["The insulation wings meet a single-stroke die before the conductor wings: on an",
                               "edge model, over 0.65-1.7 mm of die stroke (one or more clicks) [htq §3].",
                               "Stopped there, the tool makes the shape its own final stroke passes through."],
            10, fill=C["grey"])
    s.lines(px + 12, py + 104, ["Contacts this narrow stack nose to tail in a loom-order stick:",
                                "a 1.85-1.95 mm box cannot enter a 1.4-1.6 mm U."], 10, fill=C["grey"])

    # ---------------- right bottom: station S ----------------
    sy = py + 410
    s.r(px, sy, 520, 430, stroke="#ccc")
    s.t(px + 12, sy + 20, "Station S (a6b): the snap block", 11.5, bold=True)
    by = sy + 250
    s.r(px + 60, by, 400, 60, fill=C["printed"], stroke=C["printed_d"])
    s.r(px + 180, by - 6, 220, 12, fill=C["steel"], stroke=C["steel_d"])
    s.t(px + 290, by + 36, "steel-lined box pocket, lance groove, front stop", 10, anchor="middle")
    # contact in pocket
    s.r(px + 190, by - 50, 30, 44, fill=C["contact"], stroke=C["contact_d"], op=0.9)
    s.r(px + 238, by - 30, 44, 24, fill=C["contact"], stroke=C["contact_d"], op=0.6)
    s.r(px + 300, by - 46, 50, 40, fill=C["contact"], stroke=C["contact_d"])
    s.r(px + 352, by - 50, 8, 50, fill=C["steel_d"], stroke=C["ink"])
    s.t(px + 364, by - 54, "box stop", 9.5)
    # tip plate electrode
    s.r(px + 292, by - 90, 6, 44, fill=C["steel_d"], stroke=C["ink"])
    s.c(px + 295, by - 104, 8, fill="#f2a900", stroke="#a06f00")
    s.lines(px + 306, by - 110, ["tip plate, wired: names the", "conductor, buzzes if wrong"], 10)
    # conductor laid over
    s.r(px + 20, by - 80, 190, 30, fill="#333", stroke="#000")
    for i in range(4):
        s.l(px + 210, by - 74 + i * 6, px + 292, by - 74 + i * 6, stroke=C["copper"], sw=1.4)
    # thumb tool fork
    s.r(px + 186, by - 150, 36, 70, fill=C["printed"], stroke=C["printed_d"])
    s.r(px + 238, by - 150, 44, 64, fill=C["printed"], stroke=C["printed_d"])
    s.r(px + 186, by - 176, 96, 26, fill=C["printed"], stroke=C["printed_d"])
    s.l(px + 234, by - 200, px + 234, by - 180, arrow=True, red=True, sw=1.6)
    s.lines(px + 20, by - 170, ["thumb tool:", "rear tine on the jacket,", "front tine on the strands"], 10)
    # backlit window
    s.r(px + 230, by + 60, 60, 14, fill="#fff", stroke=C["grey"])
    s.t(px + 296, by + 72, "backlit window: strays show first", 10, fill=C["grey"])
    s.lines(px + 12, by + 110, ["He lifts a flag: the contact held on its wire at the right axial position and roll.",
                                "Axial grip 0.08-3.8 N [htq §2]: the push at C must stop at green."], 10, fill=C["grey"])
    s.save("flag-seat.svg")



# ---------------------------------------------------------------------------
def sketch_a4d():
    s = S(1200, 700, "A4d  One SN nest cut to a tongue, crimping in the row at 3.4 mm (end view at the press, to scale)",
          "1 mm = 24 px. Contact envelopes from clone drawings and change-the-question's pre-form widths; punch and anvil "
          "widths from calc w3 §6 / htq §5.")
    s.legend(16, 74)
    k = 24.0
    x0, y0 = 600, 470          # working contact's floor = anvil top
    # carriers (printed) at 3.4 mm, pocket floor 0.15 below the anvil top
    for i in range(-2, 3):
        xc = x0 + i * 3.4 * k
        s.r(xc - 1.5 * k, y0 + 0.15 * k, 3.0 * k, 2.2 * k, fill=C["printed"], stroke=C["printed_d"], op=0.8)
        s.r(xc - 1.0 * k, y0 + 0.15 * k, 2.0 * k, 1.2 * k, fill="#fff", stroke=C["printed_d"])
    s.t(x0 + 2 * 3.4 * k + 1.8 * k, y0 + 1.6 * k, "printed carriers at 3.4 mm, 2.0 mm box slot,", 10)
    s.t(x0 + 2 * 3.4 * k + 1.8 * k, y0 + 1.6 * k + 13, "window under the working one", 10)
    # HSS anvil blade rising through the window
    s.r(x0 - 0.95 * k, y0, 1.9 * k, 4.0 * k, fill=C["steel_d"], stroke=C["ink"])
    s.callout(x0, y0 + 3.2 * k, x0 - 7.5 * k, y0 + 4.0 * k, ["anvil: 3 x 3 mm HSS blank ground to <= 1.90 mm,",
                                                            "over a button cell and a disc stack"], 10, anchor="end")
    # contacts: pre-formed insulation envelope 2.05 wide, 2.3-3.0 tall; conductor
    for i in range(-2, 3):
        xc = x0 + i * 3.4 * k
        hgt = 2.6
        s.r(xc - 1.025 * k, y0 - hgt * k, 2.05 * k, hgt * k, fill="none", stroke=C["contact_d"], sw=1.6)
        s.l(xc - 1.025 * k, y0, xc + 1.025 * k, y0, stroke=C["contact_d"], sw=3)
        s.c(xc, y0 - 1.05 * k, 0.85 * k, fill="#333", stroke="#000")
        s.c(xc, y0 - 1.05 * k, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    # tongue: 4.45 wide up to 3.3 mm above the anvil, wider above
    tw = 4.45
    s.r(x0 - tw / 2 * k, y0 - 3.3 * k - 0.1 * k, tw * k, 2.5 * k, fill=C["steel"], stroke=C["steel_d"], op=0.6)
    s.r(x0 - 7 * k, y0 - 3.4 * k - 4.0 * k, 14 * k, 4.0 * k, fill=C["steel"], stroke=C["steel_d"], op=0.85)
    s.t(x0, y0 - 5.2 * k, "punch holder, wide above the neighbours", 10, anchor="middle", fill="#fff")
    s.t(x0, y0 - 2.4 * k, "tongue <= 4.45", 10, anchor="middle")
    # dims
    yd = y0 - 3.6 * k
    s.l(x0 - tw / 2 * k, yd, x0 + tw / 2 * k, yd, stroke=C["red"])
    s.lines(x0 + 7.4 * k, y0 - 6.8 * k, ["tongue <= 4.45 mm wide: 0.1 mm a side beside", "pre-formed neighbours 1.8-2.14 mm wide;",
                                         "narrow to 2.1-2.3 mm above the anvil beside c6 keyholes,",
                                         "2.6-3.3 mm beside tool-made pre-forms"], 10, fill=C["red"])
    s.lines(40, y0 - 6.8 * k, ["neighbours pre-formed (a6b's click or c6):", "the jaw law's stand-out is gone;",
                               "no conductor is lifted or kinked"], 10, fill=C["contact_d"])
    s.l(40, y0, 1160, y0, stroke=C["grey"], dash="3,3", sw=0.8)
    s.t(1160, y0 - 4, "anvil top = the contact's plane", 9.5, anchor="end", fill=C["grey"])
    s.lines(40, 640, ["Crimp height comes from a hard stop between the ram holder and the anvil block, beside the anvil; the SN's lower",
                      "cradle is replaced by the flat blade, so the crimp's underside differs from the hand tool's [assumption]."],
            10.5, fill=C["grey"])
    s.save("a4d-tongue.svg")


# ---------------------------------------------------------------------------
def sketch_a2b():
    s = S(1200, 760, "A2b  The tool lies flat: contacts drop into the nest, the ribbon hangs into them (schematic side view)",
          "The nest axis is vertical: the jaw's rear face is on top, the front face (box side) underneath.")
    s.legend(16, 74)
    # tool, flat: jaw slab
    jy = 400
    s.r(420, jy, 220, 60, fill=C["steel"], stroke=C["steel_d"])
    s.t(530, jy + 36, "SN-2549 jaws, lying flat", 10.5, anchor="middle", fill="#fff")
    s.r(640, jy + 10, 420, 40, fill=C["steel"], stroke=C["steel_d"], op=0.7)
    s.t(850, jy + 36, "handles to a1's pusher (on the stand)", 10.5, anchor="middle")
    s.l(420, jy, 640, jy, stroke=C["ink"], sw=2)
    s.t(410, jy + 4, "rear face (top)", 10, anchor="end")
    s.t(410, jy + 64, "front face (below)", 10, anchor="end")
    # nest axis
    nx = 470
    s.l(nx, 150, nx, 620, stroke=C["blue"], dash="6,4")
    s.t(nx + 6, 620, "nest axis (vertical)", 10, fill=C["blue"])
    # stop plate below
    s.r(nx - 40, jy + 90, 80, 16, fill=C["printed"], stroke=C["printed_d"])
    s.r(nx - 10, jy + 60, 20, 30, fill=C["contact"], stroke=C["contact_d"])
    s.t(nx + 50, jy + 102, "stop plate: pocket for the box's front end", 10)
    # chute from revolver
    s.c(760, 190, 70, fill=C["printed"], stroke=C["printed_d"])
    for i in range(8):
        import math
        a = i * math.pi / 4
        s.r(760 + 50 * math.cos(a) - 6, 190 + 50 * math.sin(a) - 6, 12, 12, fill=C["contact"], stroke=C["contact_d"])
    s.t(840, 150, "revolver disc: one contact per pocket,", 10)
    s.t(840, 163, "box down, filled by hand away from any wire", 10)
    s.poly([(700, 230), (nx + 18, jy - 4), (nx + 4, jy - 4), (688, 222)], fill=C["printed"], stroke=C["printed_d"], op=0.8)
    s.t(610, 300, "chute: the contact's end view,", 10)
    s.t(610, 313, "with a lance slot; its tongue", 10)
    s.t(610, 326, "reaches between the open jaws", 10)
    # hanging ribbon from X-Z carriage
    s.r(150, 110, 200, 30, fill=C["bought"], stroke=C["bought_d"])
    s.t(160, 104, "X-Z carriage: ribbon clamp", 10)
    s.r(200, 140, 60, 90, fill="#333", stroke="#000")
    s.r(180, 230, 110, 14, fill=C["printed"], stroke=C["printed_d"])
    s.t(176, 241, "comb", 10, anchor="end")
    for i, x in enumerate((200, 225, 250, 275)):
        s.l(x, 244, x, 330, stroke="#333", sw=4)
        s.l(x, 330, x, 342, stroke=C["copper"], sw=2.5)
    s.path("M 237 244 C 237 300, 470 300, 470 360", stroke="#333", sw=4)
    s.l(nx, 360, nx, 386, stroke=C["copper"], sw=2.5)
    s.r(nx - 22, 330, 44, 12, fill=C["printed"], stroke=C["printed_d"])
    s.t(nx - 26, 322, "fork + close U-guide set the line;", 10, anchor="end")
    s.t(nx - 26, 335, "the conductor's weight does not", 10, anchor="end")
    s.t(nx - 26, 348, "straighten set copper", 10, anchor="end")
    s.lines(40, 520, ["Z lowers conductor k to amber (strands on the contact), then green (at the blade in the neck).",
                      "The crimp moves 1-1.7 mm sideways off the anvil before Z draws it up and out.",
                      "Stand-out once neighbours carry crimps: a + 2.7 mm = 8.7-14.7 mm [calc w3 2].",
                      "Pre-formed contacts (a6b) stack nose to tail: a loom-order stick can replace the revolver."],
            10.5, fill=C["grey"])
    s.save("a2b-gravity.svg")


# ---------------------------------------------------------------------------
def sketch_a2d():
    s = S(1200, 700, "A2d  Lay the crimped row into a squaring comb, square it, push the housing onto it (schematic plan)",
          "Z out of the page. The head lays each crimped conductor into its pocket in pin-map order; crossings last, over the top.")
    s.legend(16, 74)
    cy = 330
    # squaring comb with pockets
    s.r(360, cy - 70, 60, 180, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.t(390, cy - 80, "squaring comb", 10, anchor="middle")
    s.t(390, cy - 67, "(2.5 mm pockets)", 9.5, anchor="middle", fill="#fff")
    ys = [cy - 45 + i * 22.5 for i in range(5)]
    for i, y in enumerate(ys):
        s.r(362, y - 8, 56, 16, fill=C["contact"], stroke=C["contact_d"])
        if i > 0:
            s.l(120, y, 362, y, stroke="#333", sw=5)
    # crossing conductor over the top
    s.path(f"M 120 {ys[4] + 30} C 250 {ys[4] + 30}, 250 {ys[0]}, 362 {ys[0]}", stroke="#555", sw=5, dash="8,3")
    s.lines(40, ys[4] + 60, ["crossing (J4's or J7's GND)", "laid last, over the top"], 10)
    # rear clamp
    s.r(300, cy - 70, 40, 180, fill=C["printed"], stroke=C["printed_d"], op=0.9)
    s.t(320, cy + 128, "rear clamp", 10, anchor="middle")
    s.t(320, cy + 141, "1-2 mm behind", 9.5, anchor="middle")
    s.t(320, cy + 154, "the insulation crimps", 9.5, anchor="middle")
    # front plate sliding across the noses
    s.r(424, cy - 90, 14, 220, fill=C["printed"], stroke=C["printed_d"])
    s.l(431, cy - 110, 431, cy - 92, arrow=True, red=True)
    s.t(446, cy - 100, "front plate slides across: every nose to one line, ~2 mm back; then withdraws", 10)
    # guide comb and housing on slide
    s.r(520, cy - 70, 20, 180, fill=C["printed"], stroke=C["printed_d"], op=0.6)
    s.t(530, cy + 128, "sprung guide comb", 10, anchor="middle")
    s.r(600, cy - 60, 70, 150, fill="#fff", stroke=C["ink"])
    s.t(635, cy + 20, "XHP", 11, anchor="middle", bold=True)
    s.r(670, cy - 40, 120, 110, fill=C["printed"], stroke=C["printed_d"])
    s.t(730, cy + 20, "keyed holder", 10, anchor="middle")
    s.r(790, cy - 10, 30, 50, fill=C["bought"], stroke=C["bought_d"])
    s.t(805, cy + 58, "20 kg cell", 10, anchor="middle")
    s.r(820, cy - 25, 200, 80, fill=C["bought"], stroke=C["bought_d"])
    s.t(920, cy + 20, "NEMA 17, Tr8x2 slide (~280 N)", 10, anchor="middle")
    s.l(760, cy + 100, 620, cy + 100, arrow=True, red=True, sw=1.8)
    s.t(640, cy + 118, "the housing moves; the contacts stay: no stored feed", 10, fill=C["red"])
    s.lines(40, 560, ["Force loop: baseplate -> slide -> housing -> contacts -> comb and rear clamp -> baseplate. J1's nine contacts",
                      "take 27-225 N [ith ex §12]. Latch check routes: a camera on the mating face, a wired header, or a staggered row."],
            10.5, fill=C["grey"])
    s.save("a2d-squaring.svg")


if __name__ == "__main__":
    sketch_a4c()
    sketch_flag_seat()
    sketch_a4d()
    sketch_a2b()
    sketch_a2d()
    print("written:", sorted(f for f in os.listdir(HERE) if f.endswith(".svg")))
