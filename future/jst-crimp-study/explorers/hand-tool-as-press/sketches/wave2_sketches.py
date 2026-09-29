"""Wave-2 schematic sketches for the hand-tool-as-press explorer.

Run: python3 wave2_sketches.py   (writes a6-jig-bench.svg and jaw-law-and-c-frame.svg)

All drawings are schematic. Contact proportions follow the clone drawings in
../../../context/xh-facts.md; nothing comes from a measured tool.
"""
import os
from make_sketches import S, C, HERE


# ---------------------------------------------------------------------------
def sketch_a6():
    s = S(1340, 900, "A6  The foot-closed jig bench: a stop for every placement, no motor (schematic)",
          "Left: the bench seen from the front, treadle under it. Right: the neck at hold, section along the contact. "
          "Bottom: what each jig grows into.")
    s.legend(16, 74)

    # ---------------- left: bench ----------------
    ox, oy = 20, 90
    s.r(ox, oy, 760, 560, stroke="#ccc")
    bench_y = oy + 250
    s.r(ox + 10, bench_y, 740, 18, fill="url(#hatch)", stroke=C["grey"])
    s.t(ox + 16, bench_y + 32, "bench top and baseplate", 10.5, fill=C["grey"])

    jigs = [
        ("1 end jig", ["channel 0.2 under width,", "cut slot = datum,", "split line, Klein stop", "set from the lot's contact"]),
        ("2 crimp jig", ["SN-2549 on its side,", "locator plate + blade,", "opening limiter,", "cord to the treadle"]),
        ("3 pull + look", ["plate on the box's rear,", "blade + roll flat + ELP,", "capstan, leaf at 20 N"]),
        ("4 keyhole", ["cavity section,", "lance notch,", "side slot for the wire"]),
        ("5 i5 nest", ["XHP on a wired header,", "lit cavity,", "lever + slotted blade"]),
    ]
    xs = [ox + 20, ox + 175, ox + 330, ox + 465, ox + 590]
    ws = [140, 145, 125, 115, 150]
    for (name, lines_), x, w in zip(jigs, xs, ws):
        h = 70 if name.startswith("2") else 50
        s.r(x, bench_y - h, w, h, fill=C["printed"], stroke=C["printed_d"])
        ty_ = bench_y - 118 if name.startswith("2") else bench_y - h - 8
        s.t(x + w / 2, ty_, name, 11.5, anchor="middle", bold=True)
        s.lines(x + (24 if name.startswith("2") else 4), bench_y + 50, lines_, 10)
    # crimp tool drawn on jig 2
    cx = xs[1]
    s.r(cx + 10, bench_y - 60, 120, 9, fill=C["steel"], stroke=C["steel_d"])     # lower handle
    s.poly([(cx + 10, bench_y - 64), (cx + 130, bench_y - 88), (cx + 132, bench_y - 80), (cx + 12, bench_y - 56)],
           fill=C["steel"], stroke=C["steel_d"])                                   # upper handle
    s.r(cx + 110, bench_y - 100, 30, 44, fill=C["steel"], stroke=C["steel_d"])    # head
    s.t(cx + 125, bench_y - 104, "head", 9, anchor="middle", fill=C["steel_d"])
    s.r(cx + 60, bench_y - 70, 14, 10, fill=C["printed"], stroke=C["printed_d"])  # limiter
    s.callout(cx + 67, bench_y - 66, cx + 30, bench_y - 150, ["opening limiter"], 10)
    # cord from upper handle down through bench to pulley and treadle
    hx = cx + 16
    s.c(hx, bench_y - 69, 3, fill=C["bought"], stroke=C["bought_d"])
    s.l(hx, bench_y - 69, hx, bench_y + 150, stroke=C["bought_d"], sw=1.6)
    s.c(hx, bench_y + 158, 9, fill=C["bought"], stroke=C["bought_d"])
    s.t(hx + 14, bench_y + 150, "608 pulley + AS5600", 10)
    s.r(hx - 6, bench_y + 110, 12, 22, fill=C["bought"], stroke=C["bought_d"])
    s.t(hx + 14, bench_y + 124, "S-type cell in the cord (optional)", 10)
    # treadle
    ty = oy + 520
    s.r(ox + 10, ty + 20, 740, 10, fill="url(#hatch)", stroke=C["grey"])
    s.t(ox + 16, ty + 44, "floor", 10.5, fill=C["grey"])
    heel = (hx - 120, ty + 12)
    toe = (hx + 150, ty - 40)
    s.c(*heel, 6, fill=C["grey"], stroke=C["ink"])
    s.l(heel[0], heel[1], toe[0], toe[1], stroke=C["printed_d"], sw=7)
    s.t(heel[0] - 10, heel[1] + 4, "hinge", 10, anchor="end")
    cord_pt = (heel[0] + (toe[0] - heel[0]) * 0.5, heel[1] + (toe[1] - heel[1]) * 0.5)
    s.l(hx, bench_y + 167, hx, cord_pt[1], stroke=C["bought_d"], sw=1.6)
    s.l(hx, cord_pt[1], cord_pt[0], cord_pt[1], stroke=C["bought_d"], sw=1.6)
    s.c(cord_pt[0], cord_pt[1], 3, fill=C["ink"])
    s.t(toe[0] + 14, toe[1] + 30, "toe: <= ~120 N over ~60 mm at 2:1 (calc w2 §5)", 10.5)
    s.l(toe[0] - 10, toe[1] - 40, toe[0] - 10, toe[1] - 6, arrow=True, red=True, sw=1.6)
    s.t(toe[0] - 16, toe[1] - 44, "foot", 10.5, anchor="end", fill=C["red"])
    # two-stage step
    st = (heel[0] + 190, ty + 10)
    s.r(st[0] - 5, st[1] - 22, 10, 30, fill=C["bought"], stroke=C["bought_d"])
    s.callout(st[0], st[1] - 22, ox + 25, ty - 110,
              ["two-stage step: half-press stops", "at the first ratchet tooth (hold);", "full press goes through (crimp)"], 10)
    # electronics box and far-end
    ex, ey = ox + 520, oy + 360
    s.r(ex, ey, 220, 90, fill=C["bought"], stroke=C["bought_d"])
    s.lines(ex + 8, ey + 18, ["ESP32 + LEDs + buzzer", "amber: strands on contact/tool", "green: strands on the blade",
                              "far-end block (Wago 221 / push-in)", "HX711, AS5600 (optional)"], 10)
    # ribbon from far end to jig 2
    s.path(f"M {ex} {ey + 60} C {ex - 150} {ey + 80}, {cx + 200} {bench_y - 20}, {cx + 150} {bench_y - 80}",
           stroke=C["wire"], sw=2.2)
    s.t(ex, ey + 108, "loom: far end already in the block", 10.5)

    # ---------------- right: the neck at hold ----------------
    rx, ry = 800, 90
    s.r(rx, ry, 520, 560, stroke="#ccc")
    s.t(rx + 10, ry + 20, "The neck at hold (section along the contact; 1 mm = 60 px; box to the left)", 11, bold=True)
    k = 60.0
    y0 = ry + 330  # floor top
    x_nose = rx + 30

    def X(mm):
        return x_nose + mm * k
    # anvil (lower die) under the barrels, front face at 2.45 mm from nose
    anvil_front = 2.75
    s.r(X(anvil_front), y0 + 12, 260, 120, fill=C["steel"], stroke=C["steel_d"])
    s.t(X(anvil_front) + 130, y0 + 110, "anvil (lower die)", 10.5, anchor="middle", fill=C["steel_d"])
    # punch above conductor barrel at hold height
    s.r(X(anvil_front), y0 - 1.55 * k - 80, 260, 80, fill=C["steel"], stroke=C["steel_d"])
    s.t(X(anvil_front) + 130, y0 - 1.55 * k - 40, "punch at hold (first tooth)", 10.5, anchor="middle", fill=C["steel_d"])
    # floor of contact
    s.r(X(0), y0, 7.0 * k - 60, 0.2 * k, fill=C["contact"], stroke=C["contact_d"])
    # box
    s.r(X(0), y0 - 2.2 * k, 2.0 * k, 2.2 * k, fill=C["contact"], stroke=C["contact_d"])
    s.t(X(1.0), y0 - 1.1 * k, "box", 11, anchor="middle")
    # conductor barrel wings (open, partly curled)
    cb0 = 2.35
    s.r(X(cb0), y0 - 1.5 * k, 1.4 * k, 1.5 * k, fill=C["contact"], stroke=C["contact_d"], op=0.6)
    s.t(X(cb0 + 0.7), y0 - 0.2 * k - 4, "cond. barrel", 9.5, anchor="middle")
    # lance hanging below the floor, tip 2.44 from nose, 0.75 below
    s.poly([(X(1.2), y0 + 0.2 * k), (X(2.44), y0 + 0.2 * k + 0.75 * k), (X(2.44), y0 + 0.2 * k + 0.6 * k),
            (X(1.4), y0 + 0.2 * k)], fill=C["contact"], stroke=C["contact_d"])
    s.callout(X(2.3), y0 + 0.2 * k + 0.7 * k, X(0.05), y0 + 100,
              ["lance: tip 2.44 +/-0.2 from the nose,", "0.6-0.9 below the floor,", "in front of the anvil face (or a relief)"], 10)
    # blade: steel + polyimide in the neck (2.0 - 2.15)
    s.r(X(2.0), y0 - 2.6 * k, 0.025 * k + 1, 2.6 * k, fill="#6b3fa0", stroke="#6b3fa0")
    s.r(X(2.025), y0 - 2.6 * k, 0.10 * k, 2.6 * k, fill=C["steel_d"], stroke=C["ink"], sw=0.6)
    s.callout(X(2.08), y0 - 2.4 * k, X(2.8), y0 - 3.4 * k - 10,
              ["blade 0.10 steel, bare rear face = strand stop + electrode (green)",
               "polyimide on its front face and slot edges: insulated from the box",
               "slot straddles the floor strip; tines stop at its lower face"], 10)
    # strands (brush) reaching blade
    for i in range(6):
        yy = y0 - 0.25 * k - i * 0.13 * k
        s.l(X(2.13), yy, X(4.8), yy, stroke=C["copper"], sw=1.4)
    s.r(X(4.8), y0 - 1.25 * k, 2.0 * k - 40, 1.2 * k, fill="#333", stroke="#000")
    s.t(X(5.5), y0 - 0.55 * k, "insulation", 10, anchor="middle", fill="#fff")
    # dimension of neck
    s.l(X(2.0), y0 - 3.0 * k, X(cb0), y0 - 3.0 * k, stroke=C["red"], sw=1.2)
    s.l(X(2.0), y0 - 3.1 * k, X(2.0), y0 - 2.6 * k, stroke=C["red"], sw=0.8, dash="3,2")
    s.l(X(cb0), y0 - 3.1 * k, X(cb0), y0 - 1.5 * k, stroke=C["red"], sw=0.8, dash="3,2")
    s.t(X(1.95), y0 - 3.0 * k + 4, "transition 0.2-0.5", 10, anchor="end", fill=C["red"])
    s.lines(rx + 12, ry + 500, ["Room for a brush = transition - blade (0.13-0.15): +0.05 to +0.38 mm (calc w2 §1).",
                                "Below ~0.3 mm transition: no blade; locate by the stub's pilot pin, depth by the",
                                "camera line. Lift the crimp 1-1.7 mm before drawing it back: the lance meets the",
                                "anvil face otherwise. The blade never carries the proof pull (calc w2 §2)."], 10.5)

    # ---------------- bottom: growth table ----------------
    gy = oy + 580
    s.t(20, gy, "Each jig this week, and what drives it later", 12.5, bold=True)
    rows = [("end jig", "Klein in a squeezer (a2c), laser score (b4)"),
            ("crimp jig + treadle cord", "a worm winch on the same cord, or the NEMA 17 pusher (a1, a1b, a2)"),
            ("far-end block + ESP32", "the same block and ESP32 run the motors"),
            ("cord cell + AS5600", "the same sensors under a motor: force against travel on every crimp"),
            ("pull + look jig", "servo or stepper on the lever, leaf kept as the limit; v5's readings logged (a2's pull slot)"),
            ("flags (a6b, a6c)", "a sprung seat takes a contact already on its wire: no blade, single-stage treadle"),
            ("keyhole", "on the machine's unload path (a1b)"),
            ("i5 nest", "servo on the lever, or i3's housing press (a2d)")]
    for i, (a, b) in enumerate(rows):
        yy = gy + 22 + i * 20
        s.t(40, yy, a, 11, bold=True)
        s.l(250, yy - 4, 290, yy - 4, arrow=True)
        s.t(300, yy, b, 11)
    s.save("a6-jig-bench.svg")


# ---------------------------------------------------------------------------
def sketch_jaw_law():
    s = S(1340, 900, "The side-entry jaw law, and the C-frame arm that gets round it (schematic)",
          "End views looking along the conductors (1 mm = 14 px). Row at 2.5 mm pitch. Jaw sizes assumed: the SN jaw half depth a is unmeasured.")
    s.legend(16, 74)
    k = 14.0

    def row(x0, y0, n=7, skip=None, lift=None):
        for i in range(n):
            if skip is not None and i == skip:
                continue
            s.c(x0 + i * 2.5 * k, y0, 0.85 * k, fill="#333", stroke="#000")
            s.c(x0 + i * 2.5 * k, y0, 0.36 * k, fill=C["copper"], stroke=C["copper"])

    def contact_end(xc, yc, rot=0):
        # upright contact end view: floor below, wings up; rot=90 turns it
        w, h = 2.0 * k, 2.4 * k
        if rot == 0:
            s.r(xc - w / 2, yc - 0.85 * k - 0.2 * k, w, h, fill="none", stroke=C["contact_d"], sw=1.6)
            s.l(xc - w / 2, yc + 0.85 * k + 0.2 * k, xc + w / 2, yc + 0.85 * k + 0.2 * k, stroke=C["contact_d"], sw=3)
        else:
            s.r(xc - 0.85 * k - 0.2 * k, yc - w / 2, h, w, fill="none", stroke=C["contact_d"], sw=1.6)
            s.l(xc - 0.85 * k - 0.2 * k, yc - w / 2, xc - 0.85 * k - 0.2 * k, yc + w / 2, stroke=C["contact_d"], sw=3)

    # ---- panel A: jaws close along the row -> rolled
    ax, ay = 30, 110
    s.r(ax, ay, 420, 470, stroke="#ccc")
    s.t(ax + 10, ay + 20, "A  Jaws close ALONG the row (set aside)", 12, bold=True)
    base = ay + 380
    row(ax + 60, base, skip=3)
    xk = ax + 60 + 3 * 2.5 * k
    yk = base - 5 * k
    s.c(xk, yk, 0.85 * k, fill="#333", stroke="#000")
    s.c(xk, yk, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    contact_end(xk, yk, rot=90)
    # jaws: left anvil, right punch, tall in Z, tip at bottom just above row
    s.r(xk - 1.05 * k - 8 * k, yk - 16 * k, 8 * k, 16 * k + 1.5 * k, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.r(xk + 1.4 * k, yk - 16 * k, 7 * k, 16 * k + 1.5 * k, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.t(xk - 5 * k, yk - 8 * k, "anvil", 10, anchor="middle")
    s.t(xk + 5 * k, yk - 8 * k, "punch", 10, anchor="middle")
    s.l(xk + 9 * k, yk - 4 * k, xk + 2 * k, yk - 4 * k, arrow=True, red=True)
    s.lines(ax + 12, ay + 428, ["lift = nest-to-tip + margin (4-8 mm)",
                                "barrels open ALONG the row: every crimp",
                                "rolled 90 deg, no housing fits the row"], 10.5)
    s.t(xk, base + 22, "neighbours pass under the jaw tip", 10, anchor="middle", fill=C["grey"])

    # ---- panel B: jaws close normal to the row -> upright but stand-out a+2
    bx, by = 460, 110
    s.r(bx, by, 420, 470, stroke="#ccc")
    s.t(bx + 10, by + 20, "B  Jaws close NORMAL to the row (a2, a3 on edge)", 12, bold=True)
    base = by + 400
    for i in range(7):
        if i == 3:
            continue
        xi = bx + 60 + i * 2.5 * k
        s.c(xi, base, 0.85 * k, fill="#333", stroke="#000")
        s.c(xi, base, 0.36 * k, fill=C["copper"], stroke=C["copper"])
        contact_end(xi, base, rot=0)
    xk = bx + 60 + 3 * 2.5 * k
    a = 9.0
    yk = base - (a + 2.7) * k
    s.c(xk, yk, 0.85 * k, fill="#333", stroke="#000")
    s.c(xk, yk, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    contact_end(xk, yk, rot=0)
    # jaw lying along the row: anvil half below the contact, punch half above
    s.r(bx + 20, yk + 1.05 * k, 380, a * k, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.r(bx + 20, yk - 1.6 * k - 7 * k, 380, 7 * k, fill=C["steel"], stroke=C["steel_d"], op=0.8)
    s.t(bx + 60, yk + 1.05 * k + a * k / 2 + 4, "anvil half, depth a (6-12 mm?)", 10)
    s.t(bx + 60, yk - 1.6 * k - 3.5 * k, "punch half", 10)
    s.l(bx + 395, yk + 1.05 * k + a * k, bx + 395, base - 1.35 * k, stroke=C["red"], sw=1)
    s.t(bx + 390, yk + 1.05 * k + a * k - 6, "0.3 mm over the crimped boxes", 9.5, anchor="end", fill=C["red"])
    s.lines(bx + 12, by + 448, ["barrels upright (insertion orientation)",
                                "stand-out = a + 2.7 = 8.7-14.7 mm: copper sets (R 9-47 mm)"], 10.5)
    s.t(bx + 12, base + 29, "the jaw's long axis lies along the row", 10, fill=C["grey"])

    # ---- panel C: C-frame arm from the front
    cx0, cy = 890, 110
    s.r(cx0, cy, 430, 470, stroke="#ccc")
    s.t(cx0 + 10, cy + 20, "C  a4b: one nest on an arm reaching in from the front", 12, bold=True)
    base = cy + 400
    # neighbours crimped (boxes)
    for i in range(7):
        if i == 3:
            continue
        xi = cx0 + 60 + i * 2.5 * k
        s.c(xi, base, 0.85 * k, fill="#333", stroke="#000")
        contact_end(xi, base, rot=0)
    xk = cx0 + 60 + 3 * 2.5 * k
    t_arm = 4.2
    arm_bot = base - (1.35 + 0.3) * k
    s.r(xk - 4 * k, arm_bot - t_arm * k, 8 * k, t_arm * k, fill=C["steel"], stroke=C["steel_d"])
    s.t(xk, arm_bot - t_arm * k / 2 + 4, "arm 8 x 4.2", 9.5, anchor="middle")
    s.r(xk - 1.6 * k, arm_bot - t_arm * k - 1.0 * k, 3.2 * k, 1.0 * k, fill=C["steel_d"], stroke=C["ink"])
    yk = arm_bot - t_arm * k - 1.0 * k - 1.05 * k
    s.c(xk, yk, 0.85 * k, fill="#333", stroke="#000")
    s.c(xk, yk, 0.36 * k, fill=C["copper"], stroke=C["copper"])
    contact_end(xk, yk, rot=0)
    s.r(xk - 2.2 * k, yk - 1.6 * k - 6 * k, 4.4 * k, 6 * k, fill=C["steel"], stroke=C["steel_d"], op=0.9)
    s.t(xk, yk - 1.6 * k - 3 * k, "punch", 9.5, anchor="middle")
    s.l(xk + 5 * k, yk, xk + 5 * k, base, stroke=C["red"], sw=1)
    s.t(xk + 5.5 * k, (yk + base) / 2, "lift 6.3-9.2 mm", 10.5, fill=C["red"])
    s.lines(cx0 + 12, cy + 430, ["arm passes over the neighbours' crimped boxes;",
                                 "lift independent of the SN jaw's shape (calc w2 §4)"], 10.5)

    # ---- side view of the C-frame below
    sx, sy = 30, 600
    s.r(sx, sy, 1290, 285, stroke="#ccc")
    s.t(sx + 10, sy + 20, "a4b side view (Y to the right = toward the tips): the C opens toward the web; force closes inside the C",
        11.5, bold=True)
    gy = sy + 240
    s.r(sx + 40, gy - 6, 520, 12, fill="#333", stroke="#000")
    s.t(sx + 44, gy + 26, "neighbour conductors in the fixture comb (web to the left)", 10, fill=C["grey"])
    s.r(sx + 520, gy - 26, 40, 20, fill="none", stroke=C["contact_d"], sw=1.5)
    s.t(sx + 540, gy - 30, "neighbour noses", 9.5, anchor="middle", fill=C["contact_d"])
    # working conductor lifted
    s.path(f"M {sx + 200} {gy} C {sx + 330} {gy}, {sx + 380} {gy - 60}, {sx + 470} {gy - 62} L {sx + 560} {gy - 62}",
           stroke="#333", sw=10)
    # arm
    s.r(sx + 470, gy - 50, 180, 22, fill=C["steel"], stroke=C["steel_d"])
    s.r(sx + 640, gy - 130, 40, 102, fill=C["steel"], stroke=C["steel_d"])
    s.t(sx + 660, gy - 136, "spine", 10, anchor="middle")
    s.r(sx + 470, gy - 150, 210, 22, fill=C["steel"], stroke=C["steel_d"])
    s.r(sx + 500, gy - 128, 30, 50, fill=C["steel_d"], stroke=C["ink"])
    s.t(sx + 515, gy - 102, "ram", 9, anchor="middle", fill="#fff")
    s.c(sx + 515, gy - 165, 12, fill=C["bought"], stroke=C["bought_d"])
    s.t(sx + 535, gy - 168, "eccentric + disc-spring cartridge (die contact 0.17-0.28 mm above BDC) + button cell", 10)
    s.r(sx + 500, gy - 74, 60, 22, fill="none", stroke=C["contact_d"], sw=1.5)
    s.t(sx + 494, gy - 60, "crimp on the anvil", 9.5, anchor="end", fill=C["contact_d"])
    s.t(sx + 700, gy - 60, "lower arm 6-10 mm long, 3-5.5 mm thick, over the neighbours;", 10.5)
    s.t(sx + 700, gy - 44, "the head moves -Y onto the lifted conductor, crimps, drops 1.5 mm, withdraws +Y", 10.5)
    s.save("jaw-law-and-c-frame.svg")


if __name__ == "__main__":
    sketch_a6()
    sketch_jaw_law()
    print("written:", sorted(f for f in os.listdir(HERE) if f.endswith(".svg")))
