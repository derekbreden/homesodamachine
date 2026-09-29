"""Wave-3 sketch for machine-that-sees-and-learns (exchange with hand-tool-as-press).

Run: python3 make_sketches_w3.py   (writes w3-*.svg beside this script)

The end view uses cited dimensions (calc/w3_on_hand_tool_as_press.out.txt section 7);
the side elevation is schematic.
"""
from make_sketches import SVG, header, INK, GREY, LIGHT, DARK, VIEW, FORCE, GOOD, BAD

STEEL = "#afb8c1"
TIN = "#c9d1d9"
JACKET = "#24292f"
AMBER = "#9a6700"


def w1_station_c():
    s = SVG(1340, 780, "W1 station C: tacked contact under a one-nest SN die between lifted neighbours")
    header(s, "W1  Station C: a tacked contact, a one-nest SN die set, and neighbours waiting 5 mm up",
           "Left: end view looking back along the wire, 1 mm = 22 px, positions from cited dimensions (calc w3 s7). "
           "Right: side elevation, schematic.")
    k = 22.0
    cx, fy = 440, 520            # working conductor axis x, working floor y

    def X(mm): return cx + mm * k

    def Z(mm): return fy - mm * k

    # lower die piece (one nest) and lower holder
    s.rect(X(-3.25), Z(0), 6.5 * k, 3.5 * k, fill=STEEL)
    s.text(X(0), Z(-1.9), "anvil piece, one nest,", size=10.5, anchor="middle")
    s.text(X(0), Z(-1.9) + 13, "6-7 mm wide", size=10.5, anchor="middle")
    s.rect(X(-9), Z(-3.5), 18 * k, 2.2 * k, fill=LIGHT)
    s.text(X(0), Z(-4.4), "lower holder, button cell, disc springs below", size=10.5, anchor="middle", fill=DARK)

    # working tacked contact: box in front (end view), lance below floor, conductor behind
    s.rect(X(-0.95), Z(2.3), 1.9 * k, 2.3 * k, fill=TIN, stroke=INK)
    s.poly([(X(-0.3), Z(0)), (X(0.3), Z(0)), (X(0.15), Z(-0.75)), (X(-0.15), Z(-0.75))], fill=TIN)
    s.circle(X(0), Z(1.05 + 0.2), 0.85 * k, fill="none", stroke=GREY)
    s.text(X(1.3), Z(1.6), "tacked contact on the anvil", size=10.5)
    s.text(X(1.3), Z(1.6) + 13, "(box 1.9 x 2.3, lance in a relief)", size=10.5, fill=DARK)

    # punch piece open (e 2.5) and at BDC (dashed)
    s.rect(X(-3.25), Z(5.73 + 5.9), 6.5 * k, 5.9 * k, fill=STEEL)
    s.text(X(0), Z(5.73 + 3.2), "punch piece", size=10.5, anchor="middle")
    s.text(X(0), Z(5.73 + 3.2) + 13, "open, e 2.5", size=10.5, anchor="middle")
    s.line(X(-3.25), Z(0.73), X(3.25), Z(0.73), stroke=FORCE, dash="5 4")
    s.text(X(3.5), Z(0.73) + 4, "punch at BDC", size=10, fill=FORCE)
    # holder widening above the narrow section
    s.rect(X(-9), Z(5.73 + 5.9 + 1.6), 18 * k, 1.6 * k, fill=LIGHT)
    s.text(X(0), Z(5.73 + 5.9 + 1.6) - 6, "upper holder widens only above ~5.9 mm from the crimping edge", size=10.5,
           anchor="middle", fill=DARK)

    # neighbours: crimped at +/-5, bare at +/-10, axis 5 mm up
    for dx in (-5.0, 5.0):
        s.rect(X(dx - 0.975), Z(6.35), 1.95 * k, 2.4 * k, fill=TIN, stroke=INK)
        s.poly([(X(dx - 0.3), Z(3.95)), (X(dx + 0.3), Z(3.95)), (X(dx + 0.15), Z(3.05)),
                (X(dx - 0.15), Z(3.05))], fill=TIN)
    for dx in (-10.0, 10.0):
        s.circle(X(dx), Z(5.0), 0.85 * k, fill=JACKET)
        s.circle(X(dx), Z(5.0), 0.36 * k, fill="#9aa4ae", stroke="#9aa4ae")
    s.text(X(5.0), Z(6.35) - 6, "crimped neighbour", size=10.5, anchor="middle")
    s.text(X(10.0), Z(5.0) - 30, "bare neighbour", size=10.5, anchor="middle")
    # free width arrow
    yw = Z(4.6)
    s.line(X(-4.025), yw, X(4.025), yw, stroke=GOOD, arrow="ink")
    s.line(X(4.025), yw, X(-4.025), yw, stroke=GOOD, arrow="ink")
    s.text(X(0), yw - 6, "8.05 free, 7.45 with 0.3 clearance", size=10.5, anchor="middle", fill=GOOD)
    # Z marks
    for z, lab in ((3.05, "3.05 lowest neighbour (lance)"), (6.35, "6.35 neighbour box top"),
                   (5.73, "5.73 open punch")):
        s.line(X(11.2), Z(z), X(11.8), Z(z), stroke=DARK)
        s.text(X(12.0), Z(z) + 4, lab, size=10, anchor="start", fill=DARK)

    # cam 2 band under the neighbours
    yc = Z(1.5)
    s.camera(X(-15.5), yc, ang=0)
    s.line(X(-14.8), yc, X(10.4), yc, stroke=VIEW, dash="5 4")
    s.rect(X(10.5), Z(2.85), 0.6 * k, 2.85 * k, fill="#fff8c5", stroke=AMBER)
    s.text(X(-16.2), yc + 26, "cam 2: Z 0-2.85 runs under", size=10.5, fill=VIEW)
    s.text(X(-16.2), yc + 39, "every neighbour", size=10.5, fill=VIEW)

    # ------------- right: side elevation, schematic
    ox, oy = 1010, 520
    kk = 22.0

    def SX(mm): return ox + mm * kk

    def SZ(mm): return oy - mm * kk

    s.text(820, 105, "Side elevation at C (schematic, +Y toward the box nose):", size=12, weight="bold")
    s.text(820, 121, "carry in high, set down, crimp, lift, draw back", size=12, weight="bold")
    # die (anvil below, punch above open) over both barrels
    s.rect(SX(0.2), SZ(0), 3.5 * kk, 3 * kk, fill=STEEL)
    s.text(SX(1.95), SZ(-1.6), "anvil", size=10.5, anchor="middle")
    s.rect(SX(0.2), SZ(5.73 + 4), 3.5 * kk, 4 * kk, fill=STEEL)
    s.text(SX(1.95), SZ(5.73 + 2), "punch", size=10.5, anchor="middle")
    # seat ahead of the die: floor ledge and front stop
    s.rect(SX(3.9), SZ(0), 2.6 * kk, 0.35 * kk, fill=LIGHT)
    s.rect(SX(6.05), SZ(1.0), 0.4 * kk, 1.0 * kk, fill=LIGHT)
    s.text(SX(5.2), SZ(-0.9), "seat: floor ledge,", size=10, anchor="middle")
    s.text(SX(5.2), SZ(-0.9) + 12, "front stop set per lot", size=10, anchor="middle")
    # contact: insulation barrel (rear), conductor barrel, box (front); raised dashed, seated solid
    for lift, dash, col in ((1.7, "5 4", DARK), (0.0, None, INK)):
        b = lift
        s.rect(SX(0.4), SZ(b + 2.5), 1.2 * kk, 2.5 * kk, fill="none", stroke=col, dash=dash)   # tacked ins.
        s.rect(SX(2.2), SZ(b + 1.6), 1.5 * kk, 1.6 * kk, fill="none", stroke=col, dash=dash)   # cond. barrel
        s.rect(SX(4.0), SZ(b + 2.3), 2.0 * kk, 2.3 * kk, fill="none", stroke=col, dash=dash)   # box
        s.line(SX(-7), SZ(b + 1.25), SX(1.0), SZ(b + 1.25), stroke=col, sw=3, dash=dash)       # wire
    s.line(SX(6.9), SZ(3.3), SX(6.9), SZ(1.1), stroke=INK, arrow="ink")
    s.text(SX(7.1), SZ(2.2), "set down", size=10.5)
    s.text(SX(-7), SZ(1.7 + 1.25) - 8, "carried in with the floor 1.0-1.7 up", size=10.5, fill=DARK)
    s.line(SX(-7), SZ(-1.4), SX(-2), SZ(-1.4), stroke=INK, arrow="ink")
    s.text(SX(-7), SZ(-1.4) + 16, "+Y: key k and the stage carry it", size=10.5)
    s.lines(820, 175, ["Nothing stands over the barrel at T; at C the", "punch only has to open 4-5 mm (e 2.0-2.5)",
                        "to pass a tacked contact with 0.5-1.7 mm to spare."], size=10.5, fill=DARK)

    # footer: sequence
    s.lines(30, 680, [
        "Sequence per conductor: T (nest, key k down, tack to a loose stop, top-down look) -> key up, contact rides on its wire -> C: carry in high, set down on the seat,",
        "seat look under the neighbours -> MCU turns the eccentric, dies bottom on the disc stack, button cell trace -> re-touch at 10 N, indicator reads crimp height ->",
        "ram up, lift 1.0-1.7, draw back -> silhouette on a blade beside C, box as roll gauge (second crimp height) -> proof pull on a backed plate -> key back up, next conductor.",
    ], size=11, fill=INK, gap=17)
    s.save("w3-t-then-c.svg")


if __name__ == "__main__":
    w1_station_c()
