"""Schematic sketches for the terminal-supply explorer's combinations (jst-crimp-study).

Run:  python3 make_sketches_w3.py     (writes the .svg files beside this script)

x2:  crown station, then sort and push (a2d + into-the-housing i6 + a6's post head).
x3:  stage every other cavity, crimp, leave, one push (a5 + into-the-housing i2b).
a4c: bare contacts crimped on a post bed through the housing, one push.

Pitches (1.7, 2.5, 3.5 mm), wire OD and contact proportions follow ../calc/w3.py
and the clone drawings; layouts are schematic.
"""
from make_sketches import (Svg, INK, MID, LIGHT, METAL, METAL_F, WIRE, CU, STEEL, STEEL_F,
                           PRINT, PRINT_F, ACCENT, HOUS_F, contact_side, contact_plan, wire_side,
                           schematic_tag)


def post_head_small(s, x_face, y_axis, k, pin_mm=1.6, fork=True, fork_x=None):
    """Post head seen from the side; holder face at x_face, pin pointing -x into a box."""
    s.rect(x_face, y_axis - 1.0 * k, 0.6 * k, 2.0 * k, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.rect(x_face - pin_mm * k, y_axis - 0.32 * k, pin_mm * k + 2, 0.64 * k, stroke=ACCENT, fill=ACCENT, sw=0.8)
    s.rect(x_face + 0.6 * k, y_axis - 1.4 * k, 3.0 * k, 2.8 * k, stroke=PRINT, fill=PRINT_F, sw=1.2)
    if fork and fork_x is not None:
        s.rect(fork_x - 0.2 * k, y_axis - 3.4 * k, 0.4 * k, 3.4 * k + 1.3 * k, stroke=STEEL, fill=STEEL_F, sw=1)
        s.line(fork_x, y_axis - 3.4 * k, x_face + 1.5 * k, y_axis - 3.4 * k, stroke=STEEL, sw=1.2)


# ================================================================== x2
def sketch_x2():
    s = Svg(1100, 980, "x2 crown station, then sort and push")
    s.text(20, 30, "x2  Crown station, then sort and push: one web clamp from reel to latched housing", 17,
           weight="bold")
    schematic_tag(s, 20, 50, "plan of the bench not to scale; pitches and contact proportions to scale in the insets")
    # ---------------- plan
    s.text(20, 82, "PLAN, back of the bench at the top", 12, MID, weight="bold")
    s.rect(40, 95, 1020, 430, stroke=LIGHT, fill="#fbfcfd", sw=1)
    s.rect(60, 112, 980, 14, stroke=STEEL, fill=STEEL_F, sw=1)
    s.text(70, 108, "MGN12 rail: ribbon carriage (X, with a short Y slide pulling through a 5 kg bar cell)", 10, STEEL)
    k = 6.0
    for xa, ghost in ((300, False), (780, True)):
        dash = "5,3" if ghost else None
        s.rect(xa - 70, 130, 140, 34, stroke=PRINT, fill=("none" if ghost else PRINT_F), sw=1.2, dash=dash)
        s.text(xa, 151, "web clamp" if not ghost else "same carriage, docked on pins", 10, PRINT, "middle")
        # fan comb and conductors (5P at 3.5 mm)
        pitch = 3.5 * k
        s.rect(xa - 70, 190, 140, 10, stroke=PRINT, fill=("none" if ghost else PRINT_F), sw=1, dash=dash)
        for i in range(5):
            x = xa + (i - 2) * pitch
            xr = xa + (i - 2) * 1.7 * k
            s.line(xr, 164, x, 190, stroke=WIRE, sw=1.7 * k * 0.9)
            s.line(x, 200, x, 238, stroke=WIRE, sw=1.7 * k * 0.9)
            if ghost:
                contact_plan(s, x, 238, k, 1, crimped=True)
    s.text(226, 199, "fan comb, 3.5 mm", 9, PRINT, "end")
    # station A: crown in plan
    xa = 300
    s.rect(xa - 90, 236, 180, 12, stroke=METAL, fill=METAL_F, sw=1)       # carrier band over the crest
    s.rect(xa - 110, 250, 220, 90, stroke=STEEL, fill=STEEL_F, sw=1.2)    # crown block
    for j in (-1, 1):
        s.circle(xa + j * 7.1 * k, 242, 0.75 * k, stroke=ACCENT, fill=ACCENT)
    contact_plan(s, xa, 248, k, 1)
    s.rect(xa - 1.6 * k, 246, 3.2 * k, 5.0 * k, stroke=STEEL, fill="none", sw=1.6, dash="4,3")
    s.lines(xa - 105, 358, ["STATION A = a2d: reel below, strip over a steel crown",
                            "(R 25-30), every other contact removed; knife-set",
                            "punch under a 1 t arbor press, hard stop on the crown;",
                            "pins in the removed contacts' holes; fence per contact.",
                            "Added: a slotted PULL FORK drops on the crown land",
                            "behind k's insulation barrel; the carriage pulls",
                            "the web back 20 N through its cell (proof pull)."], 10, INK, 13)
    s.text(xa + 70, 325, "crown", 10, STEEL, "middle")
    s.circle(xa + 150, 250, 10, stroke=INK, fill="#e9edf2")
    s.text(xa + 164, 254, "ELP camera", 9, INK)
    # station B
    xb = 780
    s.text(xb - 150, 272, "staging plane: crimped contacts", 9, MID)
    s.text(xb - 150, 284, "cantilevered, lance down, 3.5 mm", 9, MID)
    # target comb 6-10 mm below, U-slots at 2.5
    s.rect(xb - 70, 330, 140, 16, stroke=PRINT, fill=PRINT_F, sw=1)
    for i in range(7):
        x = xb + (i - 3) * 2.5 * k
        s.rect(x - 0.78 * k, 330, 1.56 * k, 16, stroke=PRINT, fill="#ffffff", sw=0.6)
    s.lines(xb + 78, 336, ["target comb: U-slots 1.5-1.6 wide", "at 2.50 mm, 6-10 mm below staging"], 9, PRINT, 11)
    s.rect(xb - 70, 352, 140, 6, stroke=STEEL, fill=STEEL_F, sw=1, dash="3,2")
    s.text(xb + 78, 360, "backing blade, dropped for the push", 9, STEEL)
    s.rect(xb - 45, 372, 90, 26, stroke=INK, fill=HOUS_F, sw=1.2)
    s.text(xb, 389, "XHP in nest", 9, INK, "middle")
    s.rect(xb - 60, 402, 120, 12, stroke=PRINT, fill=PRINT_F, sw=1)
    s.lines(xb + 78, 400, ["nest on a Y slide: NEMA 17 + T8", "screw through a 20 kg cell"], 9, PRINT, 11)
    s.line(xb, 420, xb, 402, stroke=INK, arrow=True)
    s.text(xb + 8, 434, "push -Y onto the row", 9, INK)
    s.rect(xb + 150, 250, 70, 40, stroke=PRINT, fill=PRINT_F, sw=1.2)
    s.lines(xb + 150, 300, ["a6's post head on a", "small X-Y-Z stage"], 9, PRINT, 12)
    s.line(xb + 150, 270, xb + 30, 262, stroke=PRINT, sw=1, arrow=True)
    s.lines(xb - 150, 460, ["STATION B = into-the-housing i6 with a6's post head as the hand: lower layer first,",
                            "centre outward; upper-layer conductors (J4: 3V3, GND; J7: GND) last."], 10, INK, 13)
    s.line(430, 150, 700, 150, stroke=INK, sw=1, dash="6,4", arrow=True)
    s.text(565, 144, "carry: carriage runs A -> B", 9, INK, "middle")

    # ---------------- inset 1: the pick at B (side view)
    s.text(20, 560, "1  AT B: THE PICK. The fork drops behind k's insulation barrel; the pin spears the box from the front",
           12, INK, weight="bold")
    k2 = 18.0
    yf = 690
    xr = 250   # contact rear
    wire_side(s, xr - 180, xr + 1.6 * k2, xr + 3.2 * k2, yf - 0.85 * k2, k2)
    contact_side(s, xr, yf, k2, 1, crimped=True)
    xfront = xr + 5.8 * k2
    post_head_small(s, xfront, yf - 1.15 * k2, k2, pin_mm=1.6, fork=True, fork_x=xr - 0.4 * k2)
    s.text(xr - 0.4 * k2, yf - 3.4 * k2 - 8, "fork tines 0.4 mm straddle the wire", 9, STEEL, "middle")
    s.text(xfront + 20, yf + 2.2 * k2, "holder face on the box front", 9, STEEL)
    s.text(xfront + 20, yf + 2.2 * k2 + 12, "pin 1.5-1.8 mm in; 0.2-2 N, reacted by the fork", 9, STEEL)
    s.lines(40, 740, ["20-30 mm of free conductor buckles at 0.17-0.39 N:",
                      "without the fork the spear would bend the wire,",
                      "not enter the box (calc w3 6)."], 10, ACCENT, 13)
    # ---------------- inset 2: placing
    s.text(560, 600, "2  PLACE: down 6-10 mm and across (up to 8.5 mm on J4) into slot k", 12, INK, weight="bold")
    xr2 = 700
    yf2 = 720
    s.rect(xr2 - 3.0 * k2, yf2 + 0.3 * k2, 3.0 * k2, 2.2 * k2, stroke=PRINT, fill=PRINT_F, sw=1)
    s.text(xr2 - 1.5 * k2, yf2 + 2.0 * k2, "U-slot", 9, PRINT, "middle")
    wire_side(s, xr2 - 150, xr2 + 1.6 * k2, xr2 + 3.2 * k2, yf2 - 0.85 * k2, k2)
    contact_side(s, xr2, yf2, k2, 1, crimped=True)
    post_head_small(s, xr2 + 5.8 * k2, yf2 - 1.15 * k2, k2, pin_mm=1.6, fork=True, fork_x=xr2 - 0.4 * k2)
    s.rect(xr2 + 5.8 * k2 + 3.2 * k2 + 30, yf2 - 2.6 * k2, 50, 5.2 * k2, stroke=INK, fill=HOUS_F, sw=1)
    s.text(xr2 + 5.8 * k2 + 3.2 * k2 + 55, yf2 + 3.1 * k2, "housing", 9, INK, "middle")
    s.lines(560, 800, ["Holder face sets every box front on one placement line; lowering presses",
                       "the wire into the U-slot through the fork's crotch; the stripper frees",
                       "the box. At 2.5 mm the tines clear the placed neighbours' wires by 0.30",
                       "and the holder their boxes by 0.52 mm (calc w3 6)."], 10, INK, 13)
    s.lines(40, 890, [
        "What the person does: lays a split, stripped end (or a pair) in the web clamp and fan comb, picks the recipe, drops a housing",
        "in the nest, lifts the finished end out and labels it; mounts a reel once (0.89 of one 8,000 reel for the program); empties cups.",
        "How it knows: at A the waiting-contact picture, the level gate, stop and force, the after look, the proof-pull trace;",
        "at B the spear trace (rise, then wall), the placement photo, the push trace and a 5 N pull-back per wire.",
    ], 10, MID, 14)
    s.save("x2-crown-then-sort.svg")


# ================================================================== x3
def sketch_x3():
    s = Svg(1100, 900, "x3 stage every other cavity, crimp, leave, one push")
    s.text(20, 30, "x3  Stage every other cavity, crimp, leave, one push (a5's staging + into-the-housing i2b)", 17,
           weight="bold")
    schematic_tag(s, 20, 50, "plan and end view; 2.5 mm pitch, 1.7 mm wire and clone contact widths to scale")
    # ---------------- plan after the odd pass, during the even pass at cavity 2
    s.text(20, 82, "1  PLAN during the even pass: odds (1, 3, 5) staged 1.5 mm deep and crimped; cavity 2 now", 12,
           weight="bold")
    s.text(20, 97, "   staged beneath its lifted conductor; conductor 4 still waits lifted", 12, weight="bold")
    k = 20
    hx = 330
    y0 = 150
    ncav = 5
    s.rect(hx - 7.75 * k, y0 - 1.6 * k, 7.75 * k, (ncav - 1) * 2.5 * k + 3.2 * k, stroke=INK, fill=HOUS_F)
    s.text(hx - 7.75 * k, y0 - 1.6 * k - 8, "XHP-5, rear face on the right; nest floats +/-0.2 mm in X and Z", 10, MID)
    for c in range(ncav):
        y = y0 + c * 2.5 * k
        s.rect(hx - 6.85 * k, y - 1.0 * k, 6.85 * k, 2.0 * k, stroke=MID, fill="#ffffff", sw=0.8)
        s.text(hx - 7.75 * k - 6, y + 4, str(c + 1), 11, MID, "end")
    s.line(hx, y0 - 1.6 * k - 20, hx, y0 + 5 * 2.5 * k, stroke=MID, dash="2,3", sw=0.8)

    def staged(y, crimped):
        xf = hx - 1.5 * k
        s.rect(xf, y - 0.93 * k, 2.0 * k, 1.85 * k, stroke=METAL, fill="#f0e2b8", sw=1)
        s.rect(xf + 2.0 * k, y - 0.6 * k, 0.5 * k, 1.2 * k, stroke=METAL, fill=METAL_F, sw=1)
        cw = 1.5 if crimped else 1.8
        iw = 1.95 if crimped else 2.8
        s.rect(xf + 2.5 * k, y - cw / 2 * k, 1.4 * k, cw * k, stroke=METAL, fill=METAL_F, sw=1)
        s.rect(xf + 4.3 * k, y - iw / 2 * k, 1.4 * k, iw * k, stroke=METAL, fill=METAL_F, sw=1)
        return xf
    for c in (0, 2, 4):
        y = y0 + c * 2.5 * k
        xf = staged(y, True)
        s.rect(xf + 3.9 * k, y - 0.85 * k, 260, 1.7 * k, stroke=WIRE, fill="#555555", sw=0.8)
    y2 = y0 + 1 * 2.5 * k
    xf = staged(y2, False)
    s.rect(xf + 3.9 * k, y2 - 0.85 * k, 260, 1.7 * k, stroke=WIRE, fill="none", sw=1.2, dash="6,3")
    s.rect(xf + 2.35 * k, y2 - 1.55 * k, 1.7 * k, 3.1 * k, stroke=ACCENT, fill="none", sw=1.5, dash="4,3")
    s.rect(xf + 4.15 * k, y2 - 1.35 * k, 1.7 * k, 2.7 * k, stroke=ACCENT, fill="none", sw=1.5, dash="4,3")
    y4 = y0 + 3 * 2.5 * k
    s.rect(hx + 3.0 * k, y4 - 0.85 * k, 220, 1.7 * k, stroke=WIRE, fill="none", sw=1.2, dash="2,3")
    LX = 655
    s.text(LX, y4 + 4, "conductor 4: waits lifted ~4 mm (finger or loft)", 10, MID)
    s.text(LX, y2 - 14, "conductor 2: lowered by the finger into the barrels", 10, INK)
    s.text(LX, y2 + 2, "narrow stepped crimper (red): 3.1 mm conductor step,", 10, ACCENT)
    s.text(LX, y2 + 16, "2.5-2.7 mm insulation step, clears crimped neighbours", 10, ACCENT)
    s.text(LX, y2 + 30, "by +0.20 and +0.17-0.28 mm (calc w3 7)", 10, ACCENT)
    s.text(LX, y0 + 4, "odd crimps stay staged: held by the mouth and their wires", 10, MID)
    # ---------------- end view at the insulation step
    s.text(20, 420, "2  END VIEW at the insulation barrels, even crimp at cavity 2 (looking into the rear face)", 12,
           weight="bold")
    k2 = 36
    cx, fy = 330, 640
    for j in (-1, 1):
        x = cx + j * 2.5 * k2
        s.rect(x - 0.975 * k2, fy - 1.9 * k2, 1.95 * k2, 1.9 * k2, stroke=METAL, fill=METAL_F, sw=1.4, rx=14)
        s.circle(x, fy - 0.95 * k2, 0.85 * k2, stroke=WIRE, fill="#3a3a3a", sw=0.8)
        if j < 0:
            s.text(x - 1.1 * k2, fy - 0.9 * k2, "crimped neighbour (1.95)", 9, METAL, "end")
        else:
            s.text(x + 1.1 * k2, fy - 0.9 * k2, "crimped neighbour (1.95)", 9, METAL)
    # station open wings 2.46-3.0
    s.poly([(cx - 1.5 * k2, fy - 3.0 * k2), (cx - 0.9 * k2, fy), (cx + 0.9 * k2, fy), (cx + 1.5 * k2, fy - 3.0 * k2)],
           stroke=METAL, fill="none", sw=2, close=False)
    s.circle(cx, fy - 0.9 * k2, 0.85 * k2, stroke=WIRE, fill="#3a3a3a", sw=0.8)
    s.text(cx, fy - 3.2 * k2, "open wings 2.46-3.0", 9, METAL, "middle")
    # crimper, 2.7 wide step
    s.rect(cx - 1.35 * k2, fy - 5.5 * k2, 2.7 * k2, 2.0 * k2, stroke=ACCENT, fill="#f6dcd9", sw=1.4)
    s.text(cx, fy - 4.5 * k2, "2.7", 10, ACCENT, "middle")
    s.rect(cx - 1.35 * k2, fy + 0.1 * k2, 2.7 * k2, 1.6 * k2, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(cx, fy + 2.1 * k2, "anvil; the crimper's walls land on its shoulders", 9, STEEL, "middle")
    s.lines(620, 470, [
        "The station's open wings clear the crimped",
        "neighbours by +0.03 (3.0 wings) to +0.30 mm",
        "(2.46) while it is staged; the 2.7 mm step",
        "clears them by +0.17 mm as it closes.",
        "Waiting conductors at 2.5 mm, if left flat,",
        "meet a 3.5 mm punch by 0.10 mm: they wait",
        "lifted instead, and ordinary dies work in",
        "the odd pass.",
        "",
        "3  ONE PUSH: the nest drives the housing",
        "5.25-5.45 mm onto every staged contact at",
        "once. Nothing was stored in any conductor;",
        "the cell shows each lance event, the lit",
        "squares go dark, and each wire is pulled",
        "back 5 N.",
    ], 11, INK, 15)
    s.lines(40, 800, [
        "Supply for the staging: a nozzle into a lance-grooved shuttle nest; or a3's rail dropping box-first into a housing lying",
        "rear face up; or Derek at the lit cavity when the machine asks. Kit contacts, BXH, or strip contacts cut first.",
        "Open: the narrow stepped dies (made, not bought); whether a crimped contact stays put at 1.5 mm while its neighbours are",
        "crimped; the lance and the anvil's front edge (a flat anvil fits about half the clone range).",
    ], 10, MID, 14)
    s.save("x3-stage-crimp-one-push.svg")


# ================================================================== a4c
def sketch_a4c():
    s = Svg(1100, 820, "a4c bare contacts crimped on a post bed, one push")
    s.text(20, 30, "a4c  Every cavity's post at once: bare contacts crimped on a post bed through the housing, one push",
           17, weight="bold")
    schematic_tag(s, 20, 50, "section along one cavity; housing and contact proportions from JST/clone dims")
    k = 20
    for panel, (ytop, title, after) in enumerate(((90, "1  CRIMP: housing threaded on the bed near its root; each bare contact "
                                                  "on its post tip, 9 mm out; odd posts first", False),
                                                 (430, "2  ONE PUSH: the housing slides ~14 mm along every post at once and "
                                                  "seats every contact", True))):
        s.text(20, ytop, title, 12, weight="bold")
        hy = ytop + 150
        bx = 70
        s.rect(bx, hy - 3.0 * k, 22, 6.0 * k, stroke=PRINT, fill=PRINT_F, sw=1.2)
        s.text(bx - 2, hy + 3.0 * k + 16, "bed: pins at 2.50 mm, each wired to the controller", 10, PRINT)
        hx = bx + 22 + 10 + (14.2 * k if after else 0)
        s.rect(hx, hy - 2.05 * k, 7.75 * k, 4.1 * k, stroke=INK, fill=HOUS_F)
        s.rect(hx + 0.9 * k, hy - 1.3 * k, 6.85 * k, 2.6 * k, stroke=INK, fill="#ffffff")
        s.rect(hx, hy - 0.45 * k, 0.9 * k, 0.9 * k, stroke=INK, fill="#ffffff")
        x_tip = bx + 22 + 10 + 7.75 * k + 9.0 * k
        s.rect(bx + 22, hy - 0.32 * k, x_tip - (bx + 22), 0.64 * k, stroke=STEEL, fill=STEEL, sw=1)
        x_front = x_tip - 1.5 * k
        x_rear = x_front + 5.8 * k
        wire_side(s, x_rear + 70, x_rear - 1.6 * k, x_rear - 4.0 * k, hy + 1.15 * k - 0.85 * k, k)
        contact_side(s, x_rear, hy + 1.15 * k, k, -1, crimped=True)
        if not after:
            s.text(hx + 3.9 * k, hy - 2.05 * k - 10, "XHP housing (section through cavity k)", 10, MID, "middle")
            s.rect(x_rear - 3.4 * k, hy + 1.15 * k + 2, 3.2 * k, 44, stroke=STEEL, fill=STEEL_F)
            s.rect(x_rear - 3.4 * k, hy + 1.15 * k - 3.0 * k - 52, 3.2 * k, 36, stroke=STEEL, fill=STEEL_F)
            s.text(x_rear - 1.8 * k, hy + 1.15 * k + 36, "anvil", 10, STEEL, "middle")
            s.text(x_rear - 1.8 * k, hy + 1.15 * k - 3.0 * k - 58, "punch", 10, STEEL, "middle")
            s.line(x_tip, hy - 3.2 * k, x_tip, hy + 3.4 * k, stroke=ACCENT, sw=1, dash="3,3")
            s.lines(x_tip - 6, hy - 3.2 * k + 4, ["post tips (all posts end here);",
                                               "the dies work 1.0-4.5 mm beyond"], 9, ACCENT, 12, anchor="end")
            s.lines(700, ytop + 30, [
                "Odd pass: even posts stand bare; their tips end",
                "before the barrels, so they never meet the dies.",
                "Even conductors wait lifted, so ordinary dies fit.",
                "Even pass: a tongue nest (<= 2.75 wide, lance",
                "groove, no side walls) slides each even contact",
                "onto its post between crimped neighbours; the",
                "finger lays its conductor in; narrow stepped",
                "dies crimp it (+0.17-0.28 mm).",
                "Before each crimp, continuity from the loom's",
                "far end to post k says the right conductor is",
                "in the right contact.",
            ], 10, INK, 13)
        else:
            s.text(hx + 3.9 * k, hy - 3.2 * k, "housing after ~14 mm of travel", 10, MID, "middle")
            s.line(bx + 22 + 10 + 3.9 * k, hy - 2.6 * k, hx + 3.9 * k - 20, hy - 2.6 * k, arrow=True)
            s.lines(700, ytop + 30, [
                "Every contact is seated by the same move:",
                "13.95-14.45 mm for all of them, nothing stored",
                "in any conductor. The cell logs the lance",
                "events; the posts are now inside the boxes as",
                "the board's header posts will be, so continuity",
                "per post and adjacent shorts are read here.",
                "Then a 5 N pull-back per wire, and the housing",
                "comes off the posts straight (within 15 deg).",
            ], 10, INK, 13)
    s.lines(40, 760, [
        "From a4b: the post through the cavity. From into-the-housing i6b: the bed of posts and one housing move. From i2b: odd, then even.",
        "Open: narrow dies for the even pass; the post's path through the cavity (one flashlight photo); posts 17-19 mm free are soft (1.2-1.7 N/mm).",
    ], 10, MID, 14)
    s.save("a4c-post-bed-one-push.svg")


if __name__ == "__main__":
    sketch_x2()
    sketch_x3()
    sketch_a4c()
