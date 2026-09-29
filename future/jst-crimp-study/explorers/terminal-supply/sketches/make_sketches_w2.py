"""Wave-2 schematic sketches for the terminal-supply explorer (jst-crimp-study).

Run:  python3 make_sketches_w2.py     (writes the .svg files beside this script)

a2d: the skip-pitch strip over a crowned anvil, seen along the contacts' axis.
a6:  the post head: picking from a pocket plate, at an open die, and at the
     SN-2549's XH nest (x1).

Crown radius, pitch and contact heights follow ../calc/wave2.py; everything
else is schematic.
"""
from math import sin, cos, radians, pi
from make_sketches import (Svg, INK, MID, LIGHT, METAL, METAL_F, WIRE, CU, STEEL, STEEL_F,
                           PRINT, PRINT_F, ACCENT, HOUS_F, contact_side, wire_side,
                           schematic_tag)


# ================================================================== a2d
def sketch_crown():
    s = Svg(1100, 900, "a2d skip-pitch strip over a crowned anvil")
    s.text(20, 30, "a2d  Skip-pitch strip over a crowned anvil: the fresh contacts fall out of the ribbon's plane",
           17, weight="bold")
    schematic_tag(s, 20, 50, "seen along the contacts' axis; R 25 mm, pitch 7.1 mm (Wurth analog), "
                  "open wing height 3.2 mm (clone max); to scale within the view")
    k = 9.0           # px per mm
    R = 25.0
    P = 7.1
    ox, oy = 500, 300   # crest (floor plane at the station)

    def pt(x, y):
        return ox + x * k, oy - y * k

    # crown body
    arc = []
    for i in range(0, 181):
        th = radians(-100 + i * 200 / 180)
        arc.append(pt(R * sin(th), -R + R * cos(th)))
    body = arc + [pt(R * sin(radians(100)), -R - 6), pt(-R * sin(radians(100)), -R - 6)]
    s.poly(body, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(ox, oy + 190, "crown block, steel, R ~25 mm", 11, STEEL, "middle")
    s.text(ox, oy + 206, "the tension-wrapped carrier is its own hold-down", 10, MID, "middle")
    s.text(ox, oy + 120, "radial pins in the holes of removed", 10, ACCENT, "middle")
    s.text(ox, oy + 134, "contacts, tips flush with the carrier", 10, ACCENT, "middle")
    # strip over the crown and down both sides
    s.path("M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in
                             [pt((R + 0.25) * sin(radians(t)), -R + (R + 0.25) * cos(radians(t)))
                              for t in range(-90, 91, 3)]), stroke=METAL, sw=2.6)
    xL, yL = pt(-R - 0.25, -R)
    xR, yR = pt(R + 0.25, -R)
    s.line(xL, yL, xL, yL + 150, stroke=METAL, sw=2.6)
    s.line(xR, yR, xR, yR + 150, stroke=METAL, sw=2.6)
    s.line(xL - 50, yL + 140, xL - 4, yL + 140, arrow=True)
    s.text(xL - 54, yL + 144, "strip rises from the reel", 10, MID, "end")
    s.line(xR + 6, yR + 110, xR + 6, yR + 148, arrow=True)
    s.text(xR + 14, yR + 132, "to sprocket and take-up", 10, MID)
    # thinning punch on the rising run
    tx, ty = xL, yL + 80
    s.rect(tx - 64, ty - 12, 44, 24, stroke=ACCENT, fill="#f6dcd9", sw=1.2)
    s.text(tx - 42, ty + 4, "punch", 9, ACCENT, "middle")
    s.line(tx - 20, ty, tx - 3, ty, stroke=ACCENT, sw=1.4, arrow=True)
    s.text(tx - 42, ty - 34, "thinning: every other", 10, ACCENT, "middle")
    s.text(tx - 42, ty - 20, "contact cut off, kept loose", 10, ACCENT, "middle")

    def contact_u(sarc):
        th = sarc / R
        n = (sin(th), cos(th))
        t = (cos(th), -sin(th))
        base = (R * sin(th), -R + R * cos(th))
        loc = [(-1.45, 3.2), (-1.0, 0.0), (1.0, 0.0), (1.45, 3.2)]
        pts = [pt(base[0] + u * t[0] + v * n[0], base[1] + u * t[1] + v * n[1]) for u, v in loc]
        s.poly(pts, stroke=METAL, fill=METAL_F, sw=1.6, close=False)
        s.poly(pts, stroke=METAL, fill="none", sw=2.0, close=False)
        tip = pts[0]
        return tip

    # wing-tip band and plane
    bx0, by0 = pt(-40, 3.6)
    bx1, by1 = pt(33, 2.7)
    s.rect(bx0, by0, bx1 - bx0, by1 - by0, stroke="none", fill="#fff1bf", sw=0)
    x0, y0 = pt(-40, 0)
    x1, y1 = pt(35, 0)
    s.line(x0, y0, x1, y1, stroke=MID, sw=1, dash="6,4")
    s.text(x0, y0 + 16, "station floor plane", 10, MID)
    s.text(bx0, by0 - 8, "yellow band: where a strand above a wing tip would show", 10, MID)
    # kept contacts upstream; stubs downstream
    tips = {}
    for m in (-2, -1, 0):
        tips[m] = contact_u(m * 2 * P)
    for m in (1, 2):
        th = m * 2 * P / R
        bx, by = pt(R * sin(th), -R + R * cos(th))
        s.circle(bx, by, 3, stroke=METAL, fill=METAL, sw=1)
    s.text(pt(24, -8)[0], pt(0, -8)[1], "downstream:", 10, MID)
    s.text(pt(24, -8)[0], pt(0, -8)[1] + 14, "tab stubs only", 10, MID)
    # radial pins at +/-7.1
    for m in (-1, 1):
        th = m * P / R
        a = pt((R - 5) * sin(th), -R + (R - 5) * cos(th))
        b = pt(R * sin(th), -R + R * cos(th))
        s.line(a[0], a[1], b[0], b[1], stroke=ACCENT, sw=3)
    # label for next kept contact
    tx1, ty1 = tips[-1]
    s.line(tx1 - 4, ty1 + 4, 230, 390, stroke=INK, sw=0.8)
    s.text(40, 404, "next kept contact, 14.2 mm of arc upstream:", 10, INK)
    s.text(40, 418, "rotated 32 deg; wing tips 1.2 mm below the plane", 10, ACCENT)
    # conductors, end-on, fan pitch 3.5
    for x in (-10.5, -7.0, -3.5, 0.0, 3.5, 7.0):
        cxp, cyp = pt(x, 0.85)
        s.circle(cxp, cyp, 0.85 * k, stroke=WIRE, fill="#3a3a3a", sw=1)
        s.circle(cxp, cyp, 0.36 * k, stroke=CU, fill=CU, sw=0.5)
        if x < 0:
            s.rect(cxp - 1.0 * k, cyp - 1.0 * k, 2.0 * k, 1.9 * k, stroke=METAL, fill="none", sw=1)
    s.text(pt(-7, 0)[0], pt(0, 5.6)[1], "done, crimped", 10, INK, "middle")
    s.text(pt(5.25, 0)[0], pt(0, 5.6)[1], "waiting", 10, INK, "middle")
    s.text(pt(0, 0)[0], pt(0, 7.2)[1], "k", 11, INK, "middle", weight="bold")
    # punch
    px, py = pt(-1.3, 18)
    s.rect(px, py, 2.6 * k, 13.5 * k, stroke=STEEL, fill=STEEL_F, sw=1.2)
    hx, hy = pt(-6, 25)
    s.rect(hx, hy, 12 * k, 7 * k, stroke=STEEL, fill="url(#hatch)", sw=1.2)
    s.text(hx - 8, hy + 20, "knife-set punch; its holder must clear the", 10, STEEL, "end")
    s.text(hx - 8, hy + 34, "crimped neighbours' boxes (1.95 wide, 2.4 tall)", 10, STEEL, "end")
    s.text(hx - 8, hy + 48, "at the bottom of the stroke: fan pitch p >= 2.5-2.8", 10, STEEL, "end")
    # camera and backlight
    camx, camy = pt(-40, 3.1)
    s.rect(camx - 36, camy - 13, 32, 26, stroke=INK, fill="#e9edf2", sw=1.2)
    s.text(camx - 20, camy + 4, "cam", 9, INK, "middle")
    s.line(camx - 4, camy, pt(30.5, 3.1)[0], camy, stroke=ACCENT, sw=1, dash="3,3", arrow=True)
    blx, bly = pt(31, 4.6)
    s.rect(blx, bly, 1.6 * k, 3.2 * k, stroke=INK, fill="#fffbe6", sw=1.2)
    s.text(blx + 22, bly + 12, "backlight tile, beyond the ribbon;", 10, INK)
    s.text(blx + 22, bly + 26, "the crown is 7-8 mm below here", 10, INK)
    s.lines(760, 100, [
        "Next kept contact's wing tips vs the plane",
        "(pitch 7.1 mm, every other contact removed):",
        "  R 20 mm, carrier at yield    -2.4 mm",
        "  R 25 mm, elastic             -1.2 mm",
        "  R 30 mm, elastic             -0.5 mm",
        "With every contact kept, the 7.1 mm",
        "neighbour clears only at R ~8 mm, which",
        "bends the carrier plastically at every",
        "contact that passes.",
        "(calc wave2 sections 1-3)",
    ], 11, INK, 15)
    s.lines(770, 545, [
        "Proof pull: a slotted pull fork drops on the",
        "crown land behind k's insulation barrel; the",
        "carriage pulls the web back 20 N through its",
        "load cell while the camera watches the",
        "insulation edge (calc w3 section 6).",
    ], 10, ACCENT, 13)
    # plan inset of the thinned strip
    iy = 780
    s.text(20, iy - 40, "PLAN of the thinned strip, looking down on the open barrels", 12, MID, weight="bold")
    kk = 7
    x_s = 60
    s.rect(x_s, iy - 20, 980, 3 * kk, stroke=METAL, fill=METAL_F, sw=1)
    for i in range(0, 20):
        x = x_s + 20 + i * 7.1 * kk
        if x > x_s + 970:
            break
        s.circle(x, iy - 20 + 1.5 * kk, 0.75 * kk, stroke=METAL, fill="#ffffff", sw=1)
        if i % 2 == 0:
            s.rect(x - 0.4 * kk, iy - 20 + 3 * kk, 0.8 * kk, 0.9 * kk, stroke=METAL, fill=METAL_F, sw=0.8)
            s.rect(x - 1.4 * kk, iy - 20 + 3.9 * kk, 2.8 * kk, 5.8 * kk, stroke=METAL, fill=METAL_F, sw=0.8)
        else:
            s.rect(x - 0.4 * kk, iy - 20 + 3 * kk, 0.8 * kk, 0.25 * kk, stroke=METAL, fill=METAL_F, sw=0.8)
    s.text(x_s, iy + 72, "a contact every 14.2 mm, a pilot hole every 7.1 mm; the holes of removed contacts "
           "take the pins. One 8,000 reel covers the whole program (0.89 of it).", 11, INK)
    s.save("a2d-skip-pitch-crown.svg")


# ================================================================== a6
def post_head(s, x_face, y_axis, k, dirn=-1, pin_mm=1.7, label=True):
    """Holder face at x_face; the pin points toward -x*dirn... pin extends from the face in direction dirn."""
    # pin
    x_tip = x_face + pin_mm * k * dirn
    s.rect(min(x_face, x_tip), y_axis - 0.32 * k, abs(x_tip - x_face), 0.64 * k, stroke=ACCENT, fill=ACCENT, sw=0.6)
    # holder (steel face) and body
    w = 1.0 * k
    xh = x_face if dirn < 0 else x_face - w
    s.rect(xh, y_axis - 1.0 * k, w, 2.0 * k, stroke=STEEL, fill=STEEL_F, sw=1.2)
    xb = xh + w if dirn < 0 else xh - 60
    s.rect(xb, y_axis - 18, 60, 36, stroke=PRINT, fill=PRINT_F, sw=1.2)
    # flexure squiggle
    xf = xb + 60 if dirn < 0 else xb
    s.path(f"M {xf:.1f},{y_axis:.1f} l 8,-8 l 8,16 l 8,-16 l 8,16 l 8,-8", stroke=PRINT, sw=1.2)
    xl = xf + 40 if dirn < 0 else xf - 40
    s.rect(xl if dirn < 0 else xl - 44, y_axis - 10, 44, 20, stroke=INK, fill="#eef0f3", sw=1)
    s.text((xl + 22) if dirn < 0 else (xl - 22), y_axis + 4, "load cell", 8, INK, "middle")
    if label:
        s.text(xb + 30, y_axis + 32, "post head", 10, PRINT, "middle")
        s.text(xb + 30, y_axis + 45, "(pin retracts: stripper)", 9, MID, "middle")


def sketch_post_gripper():
    s = Svg(1100, 980, "a6 the post is the gripper")
    s.text(20, 30, "a6  The post is the gripper: one 0.64 mm pin carries every contact from its supply to the die",
           17, weight="bold")
    schematic_tag(s, 20, 50, "side views; contact proportions from clone drawings, box front at right")
    k = 20.0
    # ---- panel 1: pick from pocket plate
    s.text(20, 90, "1  PICK from the pocket plate (or from a strip on pins)", 13, INK, weight="bold")
    y_floor = 250
    x0 = 180
    s.rect(60, y_floor, 520, 30, stroke=PRINT, fill=PRINT_F, sw=1.2)
    s.line(60, y_floor + 1.0 * k, 580, y_floor + 1.0 * k, stroke=PRINT, sw=1, dash="5,3")
    s.text(80, y_floor + 56, "pocket plate channel, 2.05 mm at the floor, open at both ends; a lance groove", 10, PRINT)
    s.text(80, y_floor + 69, "1.0 wide x >= 1.0 deep (dashed) runs its whole length, so the contact lies flat", 10, PRINT)
    s.rect(60, y_floor + 30, 520, 10, stroke="#e8c85a", fill="#fff4c9", sw=0.8)
    s.text(590, y_floor + 39, "light pad", 9, MID)
    contact_side(s, x0, y_floor, k, 1)
    # backstop blade behind insulation barrel
    s.rect(x0 - 0.5 * k, y_floor - 5.5 * k, 0.3 * k, 5.5 * k, stroke=STEEL, fill=STEEL_F, sw=1)
    s.text(x0 - 0.9 * k, y_floor - 5.8 * k, "backstop blade drops in", 10, STEEL, "end")
    xb_front = x0 + 5.8 * k
    post_head(s, xb_front, y_floor - 1.15 * k, k, dirn=-1, label=False)
    s.text(xb_front + 2, y_floor - 3.2 * k, "holder face = box-front datum", 10, STEEL)
    s.text(xb_front + 2, y_floor - 3.2 * k - 14, "post head (the pin retracts through the holder: stripper)", 10, PRINT)
    s.lines(760, 120, [
        "The camera over the light pad finds a",
        "barrels-up contact and which end its box is.",
        "The pin enters the box (0.2-2 N), then the",
        "force climbs when the box front meets the",
        "holder face: stop, lift. The box's 0.60-0.70",
        "entry captures a pointed pin +/-0.2-0.3 mm;",
        "the groove puts the entry at floor + 1.1 mm.",
        "Strip version: the carrier on pins reacts",
        "the push, then a flush punch cuts the tab",
        "from above - no wire exists yet.",
    ], 11, INK, 15)
    # ---- panel 2: at the open die
    s.text(20, 360, "2  AT THE DIE: silhouette on the post first, then onto the anvil", 13, INK, weight="bold")
    y2 = 540
    x2 = 240
    s.rect(x2 - 0.2 * k, y2 + 2, 4.0 * k, 60, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(x2 + 1.8 * k, y2 + 50, "anvil (knife set)", 10, STEEL, "middle")
    s.rect(x2 - 0.2 * k, y2 - 3.4 * k - 70, 4.0 * k, 60, stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(x2 + 1.8 * k, y2 - 3.4 * k - 76, "punch", 10, STEEL, "middle")
    wire_side(s, x2 - 160, x2 + 1.2 * k, x2 + 3.2 * k, y2 - 0.85 * k, k)
    contact_side(s, x2, y2, k, 1)
    post_head(s, x2 + 5.8 * k, y2 - 1.15 * k, k, dirn=-1)
    s.text(x2 - 160, y2 + 16, "conductor k from behind, steered", 10, INK)
    s.text(x2 - 160, y2 + 30, "by its insulation edge as seen", 10, INK)
    # camera across the die
    s.circle(x2 + 2.6 * k, y2 - 2.9 * k, 7, stroke=ACCENT, fill="#ffffff", sw=1.4)
    s.text(x2 + 3.4 * k, y2 - 2.9 * k + 4, "camera line across the die, at wing height (into the page)", 9, ACCENT)
    s.lines(760, 400, [
        "Float: the holder rides a flexure,",
        "+/-0.2 mm sideways and +/-0.2 mm in Z,",
        "preloaded from above: it holds the floor",
        "on the anvil and follows a nest that sits",
        "lower than taught. The float also",
        "lets the punch's lead-in centre the",
        "barrels. Axial stop = die fiducial +",
        "offset measured on the post. No strip",
        "beside the die: nothing one pitch away.",
        "Release: the pin draws back through the",
        "holder face; the crimp stays with its wire.",
    ], 11, INK, 15)
    # ---- panel 3: the SN-2549 nest (x1)
    s.text(20, 680, "3  x1: THE SAME HEAD PLACES THE CONTACT IN THE SN-2549's XH NEST", 13, INK, weight="bold")
    y3 = 860
    x3 = 240
    # jaws
    jf = x3 + 3.45 * k
    s.poly([(x3 - 0.4 * k, y3 + 2), (jf, y3 + 2), (jf, y3 + 70), (x3 - 60, y3 + 90)],
           stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.poly([(x3 - 0.4 * k, y3 - 3.3 * k), (jf, y3 - 3.3 * k), (jf, y3 - 3.3 * k - 60),
            (x3 - 60, y3 - 3.3 * k - 80)], stroke=STEEL, fill=STEEL_F, sw=1.2)
    s.text(x3 - 50, y3 + 110, "SN-2549 jaws on their side in hand-tool-as-press a1's cradle", 10, STEEL)
    s.line(jf, y3 - 3.3 * k - 60, jf, y3 + 70, stroke=MID, sw=1, dash="4,3")
    s.text(jf + 4, y3 + 60, "jaw front face, at the neck", 9, MID)
    contact_side(s, x3, y3, k, 1)
    post_head(s, x3 + 5.8 * k, y3 - 1.15 * k, k, dirn=-1)
    s.lines(760, 710, [
        "Head slides the contact in along its axis",
        "through the open jaws; the box and holder",
        "stay in front of the jaw face. One ratchet",
        "click captures it; the pin stays in the box",
        "while the conductor enters from behind and",
        "the tool crimps. Post pen: the same pin in",
        "a printed pen, its face against a printed",
        "fence on the jaw - a locator for loose",
        "kit contacts, no motors (spear block with",
        "the same lance groove).",
    ], 11, INK, 15)
    s.save("a6-post-is-the-gripper.svg")


if __name__ == "__main__":
    sketch_crown()
    sketch_post_gripper()
