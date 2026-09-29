"""
Generates four schematic sketches for the into-the-housing explorer:
  sketches/insulation-mouth.svg   end views: the insulation step's mouth at 2.5 mm pitch
  sketches/k7-snap-in-the-cavity.svg   side section: a pre-formed contact snapped and crimped in its cavity
  sketches/i6b-post-bed.svg        side view: posts through the housing, support comb, threading
  sketches/k8-pallets-then-sort.svg side view: half-row pallets, pallet A parked up and back, sort, push

Run: python3 sketch_wave3.py
Numbers drawn come from calc/wave3.out.txt and the sources cited there.
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "sketches")

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        'font-family="Helvetica, Arial, sans-serif" font-size="13">\n'
        '<rect width="{W}" height="{H}" fill="#ffffff"/>\n'
        '<defs>'
        '<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#c0392b"/></marker>'
        '<marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#2e7d32"/></marker>'
        '<marker id="ab" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#1f5fa8"/></marker>'
        '<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="7" stroke="#aaa" stroke-width="2"/></pattern>'
        '<pattern id="rhatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#e6a19a" stroke-width="2"/></pattern>'
        '</defs>\n')

STEEL = "#b0b8c4"
BRASS = "#d4a017"
BRASS_L = "#e6c35c"
BRONZE_E = "#6b4f00"
JACKET = "#222"
COPPER = "#b87333"
BLUE = "#1f5fa8"
GREEN = "#2e7d32"
RED = "#c0392b"


def text(P, x, y, s, fill="#222", size=None, anchor=None, weight=None):
    extra = ""
    if size:
        extra += f' font-size="{size}"'
    if anchor:
        extra += f' text-anchor="{anchor}"'
    if weight:
        extra += f' font-weight="{weight}"'
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    P.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}"{extra}>{s}</text>')


def write(name, W, H, P):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(HEAD.format(W=W, H=H))
        f.write("\n".join(P))
        f.write("\n</svg>\n")
    print("wrote", name)


# ===========================================================================
# 1. insulation-mouth.svg
# ===========================================================================
def insulation_mouth():
    W, H = 1000, 860
    P = []
    text(P, 20, 28, "The insulation step's mouth at 2.5 mm pitch (schematic end views, looking +Y)", "#111", 17, weight="bold")
    text(P, 20, 48, "~55 px per mm. Z up from the barrel floor; X across the row. Numbers: calc/wave3.out.txt sections A and J; change-the-question on_into_the_housing_w3 section 1.", "#444")
    text(P, 20, 66, "The insulation wings (2.75-3.20 mm tall open) meet the insulation step before the conductor flare centres anything, so the step's mouth must swallow them.", "#444")

    S = 55.0

    def panel(cx, floor, title, neighbour, spread, keyhole=False, note_lines=()):
        X = lambda x: cx + S * x
        Z = lambda z: floor - S * z
        text(P, cx - 230, floor - 360, title, "#111", 14, weight="bold")
        # anvil
        P.append(f'<rect x="{X(-1.6):.1f}" y="{Z(0):.1f}" width="{3.2*S:.1f}" height="{0.9*S:.1f}" fill="{STEEL}" stroke="#334"/>')
        text(P, X(0.5), Z(-0.6), "anvil", "#223", 12)
        # neighbours
        if neighbour == "jacket":
            P.append(f'<circle cx="{X(-2.5):.1f}" cy="{Z(1.05):.1f}" r="{0.85*S:.1f}" fill="{JACKET}"/>')
            P.append(f'<circle cx="{X(-2.5):.1f}" cy="{Z(1.05):.1f}" r="{0.36*S:.1f}" fill="{COPPER}"/>')
            text(P, X(-3.9), Z(-0.4), "seated neighbour's", "#222", 12)
            text(P, X(-3.9), Z(-0.4) + 15, "jacket (can give way)", "#222", 12)
            avail = 1.65
            # the other side: empty / waiting high
            text(P, X(2.0), Z(-0.4), "other side: empty", "#555", 12)
            text(P, X(2.0), Z(-0.4) + 15, "(n+1 waits high)", "#555", 12)
        else:
            for sx in (-2.5, 2.5):
                x0 = X(sx - 1.0)
                P.append(f'<rect x="{x0:.1f}" y="{Z(1.9):.1f}" width="{2.0*S:.1f}" height="{1.9*S:.1f}" rx="{0.5*S:.1f}" fill="{BRASS}" stroke="{BRONZE_E}"/>')
                P.append(f'<circle cx="{X(sx):.1f}" cy="{Z(0.95):.1f}" r="{0.7*S:.1f}" fill="{JACKET}"/>')
            text(P, X(-3.9), Z(-0.4), "crimped neighbours'", "#222", 12)
            text(P, X(-3.9), Z(-0.4) + 15, "barrels (cannot give way)", "#222", 12)
            avail = 1.50
        # available half-width lines
        for sgn in (-1, 1):
            if neighbour == "jacket" and sgn == 1:
                continue
            P.append(f'<line x1="{X(sgn*avail):.1f}" y1="{Z(-0.2):.1f}" x2="{X(sgn*avail):.1f}" y2="{Z(5.4):.1f}" stroke="{BLUE}" stroke-dasharray="5 4"/>')
        text(P, X(-avail) - 4, Z(5.5), f"{avail:.2f} mm from the axis", BLUE, 12, anchor="end")
        # the working contact: open wings (clone typical) or pre-formed keyhole
        if not keyhole:
            s = spread
            pts = f"{X(-s/2):.1f},{Z(2.95):.1f} {X(-0.8):.1f},{Z(0.25):.1f} {X(-0.8):.1f},{Z(0.1):.1f} {X(0.8):.1f},{Z(0.1):.1f} {X(0.8):.1f},{Z(0.25):.1f} {X(s/2):.1f},{Z(2.95):.1f}"
            P.append(f'<polyline points="{pts}" fill="none" stroke="{BRASS}" stroke-width="{0.2*S:.1f}" stroke-linejoin="round"/>')
            P.append(f'<circle cx="{X(0):.1f}" cy="{Z(1.05):.1f}" r="{0.85*S:.1f}" fill="{JACKET}"/>')
        else:
            # keyhole: ring of outside ~2.05 with a throat at the top
            r_out = 1.02
            r_in = 0.80
            cz = 1.0
            # arc from throat left to throat right, going around the bottom
            th = math.asin(0.70 / r_out)  # throat half-width 0.7 at the outside
            a0 = math.pi / 2 + th
            a1 = math.pi / 2 - th + 2 * math.pi
            pts = []
            n = 40
            for i in range(n + 1):
                a = a0 + (a1 - a0) * i / n
                pts.append(f"{X(r_out*math.cos(a)*0.93):.1f},{Z(cz + r_out*math.sin(a)*0.93):.1f}")
            P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{BRASS}" stroke-width="{0.2*S:.1f}" stroke-linecap="round"/>')
            P.append(f'<circle cx="{X(0):.1f}" cy="{Z(cz):.1f}" r="{r_in*S:.1f}" fill="{JACKET}"/>')
        # insulation step at first touch (solid) with its mouth
        m, l = 0.15, 0.10
        s_eff = spread
        inner = s_eff / 2 + m
        outer = inner + l
        ztop = 5.0
        zlow = 2.95 if not keyhole else 2.05
        # body
        right = outer + 0.9 if neighbour == "jacket" else outer
        path = (f"M{X(-outer):.1f},{Z(ztop):.1f} L{X(right):.1f},{Z(ztop):.1f} "
                f"L{X(right):.1f},{Z(zlow):.1f} L{X(inner):.1f},{Z(zlow):.1f} "
                f"Q{X(0):.1f},{Z(zlow+1.7):.1f} {X(-inner):.1f},{Z(zlow):.1f} "
                f"L{X(-outer)+6:.1f},{Z(zlow):.1f} L{X(-outer):.1f},{Z(zlow+0.12):.1f} L{X(-outer):.1f},{Z(ztop):.1f} z")
        P.append(f'<path d="{path}" fill="{STEEL}" stroke="#334" opacity="0.92"/>')
        # dashed: the same outer face at the bottom of the stroke
        P.append(f'<line x1="{X(-outer):.1f}" y1="{Z(zlow):.1f}" x2="{X(-outer):.1f}" y2="{Z(0.3):.1f}" stroke="#334" stroke-dasharray="4 3"/>')
        if neighbour != "jacket":
            P.append(f'<line x1="{X(outer):.1f}" y1="{Z(zlow):.1f}" x2="{X(outer):.1f}" y2="{Z(0.3):.1f}" stroke="#334" stroke-dasharray="4 3"/>')
        # interference shading
        short = outer + 0.10 - avail
        if short > 0:
            P.append(f'<rect x="{X(-outer-0.10):.1f}" y="{Z(1.9):.1f}" width="{short*S:.1f}" height="{1.7*S:.1f}" fill="url(#rhatch)" stroke="{RED}"/>')
        P.append(f'<line x1="{X(0):.1f}" y1="{Z(ztop+0.6):.1f}" x2="{X(0):.1f}" y2="{Z(ztop+0.05):.1f}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
        y = floor + 90
        for ln, col in note_lines:
            text(P, cx - 230, y, ln, col, 12)
            y += 16

    panel(260, 520, "i2 / K1, i1b: beside a seated neighbour's jacket", "jacket", 2.80, False, [
        ("Clone wings open 2.80 mm (typical): the step's outer face", "#222"),
        ("needs 1.75 mm of half-width, has 1.65 (red: the shortfall).", "#222"),
        ("Chamfered, polished outer face pushes the jacket aside:", RED),
        ("0.10-0.33 mm costs 0.05-1.9 N; every clone spread fits.", RED),
        ("Dashed: the outer face at the bottom of the stroke.", "#555"),
    ])
    panel(740, 520, "i2b pass 2, k6 at 2.5 mm, k7 pass 2: between crimped barrels", "crimped", 2.05, True, [
        ("Pre-formed keyhole (c6, 1.96-2.14 mm outside): the step", "#222"),
        ("needs 1.33-1.42 mm, has 1.50: +0.08 to +0.37 mm to spare.", GREEN),
        ("Open clone wings need 1.58-1.98 mm here and nothing can", "#222"),
        ("give way: -0.08 to -0.48 mm (generous margins).", RED),
    ])

    # table
    y0 = 720
    text(P, 20, y0, "Margin = available half-width - (s/2 + capture 0.05-0.15 + land 0.05-0.10 + clearance 0.05-0.10)", "#111", 13, weight="bold")
    rows = [
        ("wing spread s", "beside a jacket (1.65)", "beside a crimped barrel (1.50)"),
        ("pre-formed keyhole 1.96-2.14", "+0.23 to +0.52", "+0.08 to +0.37"),
        ("clone open 2.46 (drawing min)", "+0.07 to +0.27", "-0.08 to +0.12"),
        ("clone open 2.80 (typical)", "-0.10 to +0.10", "-0.25 to -0.05"),
        ("clone open 3.00 (drawing max)", "-0.20 to 0.00", "-0.35 to -0.15"),
        ("clone open 3.25 (max + tol)", "-0.33 to -0.13", "-0.48 to -0.28"),
    ]
    for i, (a, b, c) in enumerate(rows):
        yy = y0 + 22 + i * 18
        col = "#111" if i == 0 else "#333"
        text(P, 40, yy, a, col, 12, weight="bold" if i == 0 else None)
        text(P, 330, yy, b, col, 12, weight="bold" if i == 0 else None)
        text(P, 560, yy, c, col, 12, weight="bold" if i == 0 else None)
    write("insulation-mouth.svg", W, H, P)


# ===========================================================================
# 2. k7-snap-in-the-cavity.svg
# ===========================================================================
def k7_snap():
    W, H = 1000, 900
    P = []
    text(P, 20, 28, "k7 — a pre-formed contact snapped onto its conductor and crimped in its own cavity (schematic)", "#111", 17, weight="bold")
    text(P, 20, 48, "Side section through cavity n at ~25 px per mm (as i2's sketch). Box 1.4 mm in the entry; transition and lance unmeasured.", "#444")
    text(P, 20, 66, "Y left to right toward the mating face; Z up. Numbers: calc/wave3.out.txt sections A, B, J; change-the-question wave2 sections 2-5.", "#444")

    # housing (as i2 sketch)
    P.append('<rect x="560" y="224" width="194" height="15" fill="url(#hatch)" stroke="#333"/>')
    P.append('<rect x="560" y="300" width="194" height="20" fill="url(#hatch)" stroke="#333"/>')
    P.append('<rect x="739" y="239" width="15" height="61" fill="url(#hatch)" stroke="#333"/>')
    P.append('<path d="M655,300 L668,320 L700,320 L700,300 z" fill="#ffffff" stroke="#333"/>')
    text(P, 660, 345, "XHP housing in a floating nest")
    text(P, 660, 361, "(steel is the master)")
    P.append(f'<line x1="560" y1="190" x2="560" y2="420" stroke="{BLUE}" stroke-dasharray="5 4"/>')
    text(P, 566, 412, "rear face", BLUE)

    # wire with hump and web clamp
    P.append(f'<path d="M90,274 C170,274 190,200 250,200 C310,200 330,274 400,274 L485,274" fill="none" stroke="{JACKET}" stroke-width="42"/>')
    P.append(f'<line x1="485" y1="286" x2="532" y2="286" stroke="{COPPER}" stroke-width="18"/>')
    P.append('<path d="M175,300 L250,222 L325,300 z" fill="#e9d8a6" stroke="#9a7d2e"/>')
    P.append('<rect x="40" y="240" width="50" height="68" fill="#8a8a8a" stroke="#222"/>')
    text(P, 30, 330, "web clamp")
    text(P, 150, 325, "saddle", "#7a5c10")
    # hump presser, held down
    P.append(f'<rect x="232" y="160" width="36" height="18" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<line x1="250" y1="130" x2="250" y2="158" stroke="{GREEN}" stroke-width="2" marker-end="url(#ag)"/>')
    text(P, 30, 104, "hump presser sets the tip's Y from the camera's reading and", GREEN)
    text(P, 30, 120, "stays down until the crimp is done (the bore's 0.2-4 N grip", GREEN)
    text(P, 30, 136, "alone may not hold the hump's 0.4-5.7 N elastic push)", GREEN)

    # contact: box, transition, conductor barrel open, keyhole insulation barrel
    P.append(f'<rect x="545" y="240" width="50" height="60" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    text(P, 554, 275, "box", BRONZE_E)
    P.append(f'<rect x="527.5" y="295" width="17.5" height="5" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    P.append(f'<path d="M490,300 L490,261 L494,261 L494,295 L523.5,295 L523.5,261 L527.5,261 L527.5,300 z" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    P.append(f'<rect x="480" y="295" width="10" height="5" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    # keyhole barrel: top at ~2.0 mm above the floor's underside -> y = 300 - 50 = 250
    P.append(f'<path d="M447.5,300 L447.5,250 L480,250 L480,300 z" fill="none" stroke="{BRONZE_E}" stroke-width="1.5"/>')
    P.append(f'<rect x="447.5" y="250" width="32.5" height="5" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    P.append(f'<rect x="447.5" y="295" width="32.5" height="5" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    P.append(f'<line x1="534" y1="317" x2="556.5" y2="300" stroke="{BRONZE_E}" stroke-width="3"/>')
    text(P, 566, 444, "lance hangs free ahead of the anvil's front edge", BRONZE_E)

    # anvil under both barrels
    P.append(f'<rect x="440" y="300" width="91.5" height="92" fill="{STEEL}" stroke="#334"/>')
    text(P, 250, 380, "anvil under both barrels", "#223")
    text(P, 250, 396, "takes the snap's 0.5-20 N", "#223")
    P.append('<rect x="436" y="296" width="6" height="40" fill="#555"/>')
    text(P, 250, 420, "backstop on the tab stub (-Y)", "#333")

    # two-tine presser foot
    P.append(f'<rect x="446" y="150" width="84" height="16" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<rect x="456" y="166" width="16" height="84" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<rect x="501" y="166" width="14" height="110" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<line x1="488" y1="112" x2="488" y2="146" stroke="{GREEN}" stroke-width="2" marker-end="url(#ag)"/>')
    text(P, 600, 110, "two-tine presser foot:", GREEN)
    text(P, 600, 126, "rear tine pushes the jacket down through the keyhole's", GREEN)
    text(P, 600, 142, "1.3-1.5 mm throat into its 1.55-1.60 mm bore (a snap);", GREEN)
    text(P, 600, 158, "front tine lays the strands into the open conductor U.", GREEN)
    text(P, 600, 180, "Then the camera looks, the foot lifts, and the knee", "#223")
    text(P, 600, 196, "closes the stepped crimper (as i2): the conductor flare", "#223")
    text(P, 600, 212, "centres the contact; the mouth swallows the keyhole.", "#223")

    # inset: pre-former end view
    cx, cz = 190, 690
    S = 45.0
    X = lambda x: cx + S * x
    Z = lambda z: cz - S * z
    text(P, 20, 500, "Pre-former (end view, ~45 px per mm): contact box-down in a nest (a cut XHP stub works),", "#111", 13, weight="bold")
    text(P, 20, 518, "pin from behind, jaw closes the wings around it. Jaw = a second cut of the press's insulation-step profile.", "#111", 13)
    P.append(f'<rect x="{X(-1.6):.1f}" y="{Z(0):.1f}" width="{3.2*S:.1f}" height="{1.0*S:.1f}" fill="url(#hatch)" stroke="#333"/>')
    text(P, X(1.8), Z(-0.6), "nest", "#333", 12)
    r_out = 1.02
    th = math.asin(0.70 / r_out)
    a0 = math.pi / 2 + th
    a1 = math.pi / 2 - th + 2 * math.pi
    pts = []
    for i in range(41):
        a = a0 + (a1 - a0) * i / 40
        pts.append(f"{X(r_out*math.cos(a)*0.93):.1f},{Z(1.0 + r_out*math.sin(a)*0.93):.1f}")
    P.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{BRASS}" stroke-width="{0.2*S:.1f}" stroke-linecap="round"/>')
    P.append(f'<circle cx="{X(0):.1f}" cy="{Z(1.0):.1f}" r="{0.79*S:.1f}" fill="#9aa3ad" stroke="#334"/>')
    text(P, X(0), Z(1.0) + 5, "pin", "#111", 12, anchor="middle")
    # jaw (profile) above
    jaw = (f"M{X(-1.9):.1f},{Z(3.4):.1f} L{X(1.9):.1f},{Z(3.4):.1f} L{X(1.9):.1f},{Z(1.2):.1f} L{X(1.1):.1f},{Z(1.2):.1f} "
           f"Q{X(1.05):.1f},{Z(2.35):.1f} {X(0):.1f},{Z(2.35):.1f} Q{X(-1.05):.1f},{Z(2.35):.1f} {X(-1.1):.1f},{Z(1.2):.1f} "
           f"L{X(-1.9):.1f},{Z(1.2):.1f} z")
    P.append(f'<path d="{jaw}" fill="{STEEL}" stroke="#334" opacity="0.8"/>')
    text(P, X(2.1), Z(2.6), "jaw (10-80 N: servo lever or toggle clamp)", "#223", 12)
    text(P, X(2.1), Z(1.6), "keyhole: bore 1.55-1.60, throat 1.3-1.5,", BRONZE_E, 12)
    text(P, X(2.1), Z(1.6) + 15, "1.96-2.14 mm outside (open clone wings 2.46-3.25)", BRONZE_E, 12)
    text(P, X(2.1), Z(1.6) + 30, "go pin 1.50 must enter the bore from behind", BRONZE_E, 12)

    # inset: plan view of the feed
    ox, oy = 560, 600
    text(P, 540, 560, "Feed (plan view, schematic): a stick of pre-formed contacts", "#111", 13, weight="bold")
    text(P, 540, 578, "nose to tail; an escapement singles the lead one out", "#111", 13)
    P.append(f'<rect x="{ox}" y="{oy+40}" width="220" height="26" fill="#eef1f5" stroke="{BLUE}"/>')
    for i in range(5):
        x = ox + 10 + i * 42
        P.append(f'<rect x="{x}" y="{oy+44}" width="36" height="18" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    text(P, ox, oy + 84, "stick (2.1 x 2.6 mm channel, lance groove)", BLUE, 12)
    P.append(f'<rect x="{ox+232}" y="{oy+30}" width="16" height="44" fill="#9fd19f" stroke="{GREEN}"/>')
    text(P, ox + 232, oy + 22, "escapement", GREEN, 12)
    P.append(f'<rect x="{ox+262}" y="{oy+40}" width="36" height="120" fill="#eef1f5" stroke="#556"/>')
    P.append(f'<rect x="{ox+271}" y="{oy+100}" width="18" height="36" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    P.append(f'<line x1="{ox+280}" y1="{oy+140}" x2="{ox+280}" y2="{oy+190}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
    text(P, ox + 306, oy + 104, "channel plate:", "#333", 12)
    text(P, ox + 306, oy + 120, "a servo finger slides", "#333", 12)
    text(P, ox + 306, oy + 136, "it box-first into", "#333", 12)
    text(P, ox + 306, oy + 152, "cavity n", "#333", 12)
    P.append(f'<rect x="{ox+240}" y="{oy+196}" width="80" height="24" fill="url(#hatch)" stroke="#333"/>')
    text(P, ox + 330, oy + 214, "housing, cavity n", "#333", 12)
    text(P, 20, 880, "The stick never feeds the cavity directly: nose to tail, the next box would sit against the lead contact's keyhole, inside the crimper's footprint.", "#444")
    write("k7-snap-in-the-cavity.svg", W, H, P)


# ===========================================================================
# 3. i6b-post-bed.svg
# ===========================================================================
def i6b_post_bed():
    W, H = 1000, 760
    P = []
    text(P, 20, 28, "i6b — a bed of posts through the housing, with a support comb near the tips (schematic, side view)", "#111", 17, weight="bold")
    text(P, 20, 48, "~22 px per mm. Y left to right toward the mating face; Z up. Numbers: calc/wave3.out.txt sections E, F, H.", "#444")
    S = 22.0
    ox, oz = 820, 330      # Y=0 at the PCB face, Z=0 at the post line
    Y = lambda y: ox + S * y
    Z = lambda z: oz - S * z
    # PCB
    P.append(f'<rect x="{Y(0):.1f}" y="{Z(3):.1f}" width="{1.6*S:.1f}" height="{6*S:.1f}" fill="#2e6b3a" stroke="#123"/>')
    text(P, Y(2.0), Z(2.4), "post-bed PCB,", "#123", 12)
    text(P, Y(2.0), Z(2.4) + 15, "holes at 2.50 mm", "#123", 12)
    text(P, Y(2.0), Z(2.4) + 30, "(each post an", "#123", 12)
    text(P, Y(2.0), Z(2.4) + 45, "ESP32 input)", "#123", 12)
    # housing: 7.75 mm, mating face at Y=0 (touching PCB) before the push
    P.append(f'<rect x="{Y(-7.75):.1f}" y="{Z(1.6):.1f}" width="{7.75*S:.1f}" height="{3.2*S:.1f}" fill="url(#hatch)" stroke="#333"/>')
    P.append(f'<rect x="{Y(-7.15):.1f}" y="{Z(1.1):.1f}" width="{7.15*S:.1f}" height="{2.2*S:.1f}" fill="#ffffff" stroke="#333"/>')
    text(P, Y(-7.75), Z(3.4), "XHP housing (7.75 mm),", "#222", 12)
    text(P, Y(-7.75), Z(3.4) + 15, "before the push", "#222", 12)
    # posts: from PCB to 8.5 mm beyond rear face: tip at Y = -7.75 - 8.5 = -16.25
    tip = -16.25
    P.append(f'<line x1="{Y(0):.1f}" y1="{Z(0):.1f}" x2="{Y(tip):.1f}" y2="{Z(0):.1f}" stroke="#777" stroke-width="{0.64*S:.1f}"/>')
    text(P, Y(-12.5), Z(-2.6), "0.64 mm post, ~17 mm long", "#555", 12)
    # support comb 3 mm below the tip
    cy = tip + 3.0
    P.append(f'<rect x="{Y(cy)-4:.1f}" y="{Z(1.3):.1f}" width="8" height="{2.6*S:.1f}" fill="{BLUE}" opacity="0.8"/>')
    P.append(f'<line x1="{Y(cy):.1f}" y1="{Z(1.4):.1f}" x2="{Y(cy):.1f}" y2="{Z(3.4):.1f}" stroke="{BLUE}" stroke-width="2" marker-end="url(#ab)"/>')
    text(P, Y(cy) - 10, Z(7.4), "support comb (stencil steel, slots at 2.50 mm)", BLUE, 12)
    text(P, Y(cy) - 10, Z(7.4) + 15, "holds each post 3 mm below its tip while the", BLUE, 12)
    text(P, Y(cy) - 10, Z(7.4) + 30, "box threads on; withdraws in Z before the push", BLUE, 12)
    # crimped contact threaded 1.5 mm on the tip: box front at tip + 1.5
    bf = tip + 1.5
    P.append(f'<rect x="{Y(bf-2.0):.1f}" y="{Z(1.1):.1f}" width="{2.0*S:.1f}" height="{2.3*S:.1f}" fill="{BRASS_L}" stroke="{BRONZE_E}" opacity="0.9"/>')
    P.append(f'<rect x="{Y(bf-6.2):.1f}" y="{Z(0.4):.1f}" width="{4.2*S:.1f}" height="{1.5*S:.1f}" fill="{BRASS}" stroke="{BRONZE_E}"/>')
    P.append(f'<line x1="{Y(bf-6.2):.1f}" y1="{Z(0.2):.1f}" x2="{Y(bf-6.2)-230:.1f}" y2="{Z(0.2):.1f}" stroke="{JACKET}" stroke-width="{1.7*S:.1f}"/>')
    text(P, Y(bf - 6.2) - 230, Z(-1.9), "conductor from the staging plane", "#222", 12)
    # carrier fingers
    P.append(f'<rect x="{Y(bf-5.6):.1f}" y="{Z(2.8):.1f}" width="{2.6*S:.1f}" height="{1.2*S:.1f}" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<rect x="{Y(bf-5.6):.1f}" y="{Z(-0.6):.1f}" width="{2.6*S:.1f}" height="{1.0*S:.1f}" fill="#9fd19f" stroke="{GREEN}"/>')
    P.append(f'<line x1="{Y(bf-6.4):.1f}" y1="{Z(4.0):.1f}" x2="{Y(bf-3.9):.1f}" y2="{Z(4.0):.1f}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
    text(P, 150, Z(6.4), "carrier: fingers above and below the", GREEN, 12)
    text(P, 150, Z(6.4) + 15, "crimped barrels; threads the box +Y", GREEN, 12)
    text(P, 150, Z(6.4) + 30, "1-2 mm onto the post tip", GREEN, 12)
    # housing travel arrow
    P.append(f'<line x1="{Y(-1):.1f}" y1="{Z(-3.2):.1f}" x2="{Y(-15):.1f}" y2="{Z(-3.2):.1f}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
    text(P, 150, Z(-4.6), "then the housing slides -Y along the posts ~13-15 mm over every box, to the first wall;", RED, 12)
    text(P, 150, Z(-4.6) + 16, "a finishing tine brings each contact to its own wall; continuity per post is read before and after", RED, 12)

    # deflection table
    y0 = 520
    text(P, 20, y0, "Why the support comb: side-load deflection of a post tip (calc wave3 F)", "#111", 13, weight="bold")
    rows = [("support", "steel", "brass or bronze header pin"),
            ("none: free from the front wall to the tip, ~15.6 mm", "0.45 mm per N", "0.90 mm per N"),
            ("a comb at the rear face: free 8.5 mm", "0.07 mm per N", "0.15 mm per N"),
            ("a comb 3 mm below the tip: free 3 mm", "0.003 mm per N", "0.006 mm per N")]
    for i, (a, b, c) in enumerate(rows):
        yy = y0 + 22 + i * 18
        w = "bold" if i == 0 else None
        text(P, 40, yy, a, "#222", 12, weight=w)
        text(P, 420, yy, b, "#222", 12, weight=w)
        text(P, 560, yy, c, "#222", 12, weight=w)
    text(P, 20, y0 + 118, "The box mouth (0.60-0.70 mm) captures a chamfered post tip within +/-0.2 mm; threading costs 0.5-1 N of side load.", "#444", 12)
    text(P, 20, y0 + 136, "Pitch: drill at 2.50, not 2.54 (XHP-9 would be 0.32 mm off end to end). With the comb, the comb's laser-cut slots set the tips.", "#444", 12)
    text(P, 20, y0 + 154, "Open question: does a post pass cleanly along a kit cavity from the post opening to the rear face? One header pin through one housing.", "#444", 12)
    write("i6b-post-bed.svg", W, H, P)


# ===========================================================================
# 4. k8-pallets-then-sort.svg
# ===========================================================================
def k8_pallets():
    W, H = 1000, 800
    P = []
    text(P, 20, 28, "k8 — half-rows crimped in pallets (c1c), sorted into one row, housing pushed on (i6) (schematic, side view)", "#111", 16, weight="bold")
    text(P, 20, 48, "~11 px per mm. Y left to right; Z up. Numbers: calc/wave3.out.txt section I; change-the-question on_into_the_housing_w3 sections 7, 9.", "#444")
    S = 11.0
    ox, oz = 270, 420
    Y = lambda y: ox + S * y
    Z = lambda z: oz - S * z
    # web clamp and root
    P.append(f'<rect x="{Y(-8):.1f}" y="{Z(2):.1f}" width="{8*S:.1f}" height="{4*S:.1f}" fill="#8a8a8a" stroke="#222"/>')
    text(P, Y(-8), Z(-3.2), "web clamp / root", "#222", 12)
    # fixed press above the crimp station
    P.append(f'<path d="M{Y(20):.1f},{Z(22):.1f} L{Y(34):.1f},{Z(22):.1f} L{Y(34):.1f},{Z(8):.1f} L{Y(30):.1f},{Z(8):.1f} L{Y(30):.1f},{Z(18):.1f} L{Y(24):.1f},{Z(18):.1f} L{Y(24):.1f},{Z(8):.1f} L{Y(20):.1f},{Z(8):.1f} z" fill="{STEEL}" stroke="#334"/>')
    for i, ln in enumerate(["fixed press (c1c) in a small steel C:", "the X slide steps each carrier under", "its punch; proof pull on the pocket's", "rear shoulder"]):
        text(P, Y(35), Z(21) + 15 * i, ln, "#223", 12)
    # row B in pallet B in the working plane
    P.append(f'<line x1="{Y(0):.1f}" y1="{Z(0):.1f}" x2="{Y(24):.1f}" y2="{Z(0):.1f}" stroke="{JACKET}" stroke-width="{1.7*S:.1f}"/>')
    P.append(f'<rect x="{Y(22):.1f}" y="{Z(1.2):.1f}" width="{6.2*S:.1f}" height="{2.4*S:.1f}" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    P.append(f'<rect x="{Y(20):.1f}" y="{Z(-1.2):.1f}" width="{10*S:.1f}" height="{1.8*S:.1f}" fill="#cfd8e6" stroke="{BLUE}"/>')
    text(P, Y(31), Z(-0.4), "pallet B (working plane):", BLUE, 12)
    text(P, Y(31), Z(-0.4) + 15, "crimped row B, placed first", BLUE, 12)
    # pallet A parked up and back over the root
    P.append(f'<path d="M{Y(0):.1f},{Z(0.5):.1f} C{Y(6):.1f},{Z(6):.1f} {Y(0):.1f},{Z(12):.1f} {Y(-4):.1f},{Z(13):.1f}" fill="none" stroke="#666" stroke-width="{1.7*S:.1f}"/>')
    P.append(f'<rect x="{Y(-14):.1f}" y="{Z(15):.1f}" width="{10*S:.1f}" height="{1.8*S:.1f}" fill="#cfd8e6" stroke="{BLUE}"/>')
    P.append(f'<rect x="{Y(-12):.1f}" y="{Z(17.2):.1f}" width="{6.2*S:.1f}" height="{2.2*S:.1f}" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    text(P, Y(-14), Z(20.5) - 15, "pallet A (crimped row A)", BLUE, 12)
    text(P, Y(-14), Z(20.5), "parked UP and back, over the root", BLUE, 12)
    P.append(f'<path d="M{Y(-2):.1f},{Z(18):.1f} Q{Y(14):.1f},{Z(22):.1f} {Y(20):.1f},{Z(3):.1f}" fill="none" stroke="{GREEN}" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#ag)"/>')
    text(P, Y(10), Z(24), "its swing into the working", GREEN, 12)
    text(P, Y(10), Z(24) + 15, "plane stays ABOVE it", GREEN, 12)
    # target comb, housing
    h = 8.0
    P.append(f'<polyline points="{Y(4):.1f},{Z(0):.1f} {Y(30):.1f},{Z(-h):.1f} {Y(40):.1f},{Z(-h):.1f}" fill="none" stroke="#555" stroke-width="{1.7*S:.1f}" stroke-linejoin="round"/>')
    P.append(f'<rect x="{Y(39.5):.1f}" y="{Z(-h+1.2):.1f}" width="{6.2*S:.1f}" height="{2.4*S:.1f}" fill="{BRASS_L}" stroke="{BRONZE_E}"/>')
    P.append(f'<rect x="{Y(34):.1f}" y="{Z(-h-0.8):.1f}" width="{4*S:.1f}" height="{2.0*S:.1f}" fill="#cfd8e6" stroke="{BLUE}"/>')
    text(P, Y(30), Z(-h - 4.4), "target comb: 2.5 mm, housing order,", BLUE, 12)
    text(P, Y(30), Z(-h - 4.4) + 15, "h = 6-8 mm below the working plane", BLUE, 12)
    P.append(f'<rect x="{Y(48):.1f}" y="{Z(-h+2):.1f}" width="{7.75*S:.1f}" height="{4*S:.1f}" fill="url(#hatch)" stroke="#333"/>')
    P.append(f'<line x1="{Y(60):.1f}" y1="{Z(-h+4):.1f}" x2="{Y(50):.1f}" y2="{Z(-h+4):.1f}" stroke="{RED}" stroke-width="2" marker-end="url(#ar)"/>')
    text(P, Y(48), Z(-h + 7.0), "housing pushed -Y", RED, 12)
    text(P, Y(48), Z(-h + 7.0) + 15, "onto the one row", RED, 12)
    # red hatched region swept by a down-back park
    P.append(f'<path d="M{Y(0):.1f},{Z(-1):.1f} L{Y(26):.1f},{Z(-2):.1f} L{Y(26):.1f},{Z(-10):.1f} L{Y(-10):.1f},{Z(-12):.1f} z" fill="url(#rhatch)" stroke="{RED}" stroke-dasharray="4 3" opacity="0.7"/>')
    text(P, Y(-12), Z(-14.5), "red: the space a pallet parked DOWN and back (c1c as drawn) sweeps on its way into", RED, 12)
    text(P, Y(-12), Z(-14.5) + 15, "the working plane, where every sorted row-B conductor already lies", RED, 12)
    # carrier
    P.append(f'<rect x="{Y(23):.1f}" y="{Z(3.4):.1f}" width="{3*S:.1f}" height="{1.5*S:.1f}" fill="#9fd19f" stroke="{GREEN}"/>')
    text(P, Y(6), Z(6.0), "carrier: top pad on the crimp's lobes,", GREEN, 12)
    text(P, Y(6), Z(6.0) + 15, "bottom pad up through the anvil window", GREEN, 12)

    y0 = 660
    text(P, 20, y0, "Order: row B first, then row A, upper layer last. With J4 laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 and J7 laid RB1-RB4, GND | X, CLO, CHI,", "#222", 12)
    text(P, 20, y0 + 16, "every upper-layer conductor (J4's 3V3 and GND, J7's GND) is at an odd ribbon position, so in pallet A.", "#222", 12)
    text(P, 20, y0 + 36, "Once in the working plane, pallet A's carriers (1-2 mm deep) clear the sorted conductors below them when h >= ~6 mm and the pallet", "#222", 12)
    text(P, 20, y0 + 52, "sits beyond 0.36-0.53 of the span from the root (calc wave3 I). Whether the press leaves room above the root is unmeasured.", "#222", 12)
    text(P, 20, y0 + 72, "Push: to the first wall, then one finishing tine per contact (lengths differ). No crossing is made by hand.", "#222", 12)
    write("k8-pallets-then-sort.svg", W, H, P)


if __name__ == "__main__":
    insulation_mouth()
    k7_snap()
    i6b_post_bed()
    k8_pallets()
