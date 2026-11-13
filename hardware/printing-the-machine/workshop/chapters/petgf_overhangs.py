"""PET-GF over air, without slicer supports: layer height, leaning walls, bridges and fins.
Six pages for the PET-GF part. Each function returns one Page."""
import math

import bookkit as b
import svgkit as k
from bookkit import Page

FINS = "hardware/print-tests/petgf-fins"
COUPONS = "hardware/printed-parts/faucet/finish-coupons"
NSR = "hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews"
TEE = "hardware/printed-parts/enclosure/tee-carrier"
ENC = "hardware/printed-parts/enclosure"
TEE_REV = "aab7f24fec"      # holds the tee carrier's photographs and observations
FINE = 8.0                  # a fine course in a drawing: a third of svgkit's ROW_H
MM = 100.0                  # svgkit draws a road 42 wide and 24 tall: a hundred units to the millimetre


def _petgf():
    return b.source("petgf", "hardware/printed-parts/petgf.3mf", member="Metadata/project_settings.config")


def _catalog():
    return b.source("petgf-overhangs-catalog", "tools/hsm/shared-data/catalog/scalars.json")


# ----------------------------------------------------------------------------- drawing helpers
def run(x_in, x_out, y, fill=k.COLD, h=k.ROW_H):
    """One course between two x positions given in either order, its top at y."""
    lo, hi = min(x_in, x_out), max(x_in, x_out)
    if hi - lo < h:
        return ""
    return k.course(lo, hi, y, fill, h)


def poly(points, color=k.INK, width=3, dash="", fill="none"):
    d = "M" + " L".join(f"{k.n(x)} {k.n(y)}" for x, y in points)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" stroke="{color}" stroke-width="{k.n(width)}" fill="{fill}" stroke-linejoin="round"{da}/>'


def vtext(x, y, text, size=25, fill=k.MUTED, weight=400):
    """Mono capitals running up the page."""
    return (f'<text transform="translate({k.n(x)} {k.n(y)}) rotate(-90)" font-family="IBM Plex Mono, monospace" font-size="{k.n(size)}" '
            f'letter-spacing="{k.n(0.06 * size)}" font-weight="{weight}" fill="{fill}">{text}</text>')


def tagline(tag, cls, text):
    return f'<p class="tiny" style="margin:14px 0 0; color:var(--text)"><span class="tag {cls}" style="margin-right:14px">{tag}</span>{text}</p>'


def dated(rows, first=250, size=32, gap=17):
    """A dated or labelled list: (label, what happened) pairs."""
    cells = "".join(
        f'<div class="mono" style="font-size:27px; line-height:1.3; letter-spacing:.07em; color:var(--ink); font-weight:600; padding-top:5px">{d}</div>'
        f'<div class="tiny" style="color:var(--text); font-size:{size}px">{t}</div>'
        for d, t in rows)
    return f'<div style="display:grid; grid-template-columns:{first}px 1fr; column-gap:28px; row-gap:{gap}px">{cells}</div>'


def legend(items, cols=2, size=32):
    """Numbered notes that answer the discs in a drawing: (number, kind, text)."""
    cells = "".join(
        f'<div style="display:flex; gap:20px; align-items:flex-start; break-inside:avoid; margin-bottom:14px"><span class="num {c}" style="width:50px; height:50px; font-size:27px">{n}</span>'
        f'<p class="tiny" style="margin:0; font-size:{size}px; color:var(--text)">{t}</p></div>'
        for n, c, t in items)
    return f'<div style="columns:{cols}; column-gap:44px">{cells}</div>'


def note(title, text, size=33):
    return f'<h2 style="font-size:44px; margin-bottom:10px">{title}</h2><p class="tiny" style="margin:0; font-size:{size}px; color:var(--text)">{text}</p>'


def plain_open(text):
    """still_open() without its top margin, for use inside a row."""
    return b.still_open(text).replace('class="open"', 'class="open" style="margin:0"', 1)


# ----------------------------------------------------------------------------- 1 layer height
def _fine_panel(kind):
    """Where a fine layer goes: a small schematic section, not to scale."""
    W, H, R, X0, XW = 320, 330, 150, 14, 224
    s = []
    if kind == "inward":
        base = 318
        s.append(k.block(X0, XW, 0, 3, base))
        y0 = base - 4 * k.ROW_H
        n = 18
        for i in range(n):
            z = (i + 0.5) * FINE
            xo = XW - R + math.sqrt(max(R * R - z * z, 0))
            s.append(run(X0, xo, y0 - (i + 1) * FINE, k.HOT if i == n - 1 else k.COLD, FINE))
        s.append(k.line(XW + 14, y0 - 4, XW + 14, y0 - 140, k.MUTED, 3) + k.label(XW + 26, y0 - 62, "FINE", 23))
        s.append(k.label(X0, 34, "TOP OF A PRINT", 23))
    elif kind == "support":
        bed = 300
        s.append(k.bed(4, W - 4, bed))
        s.append(k.scaffold(X0, XW, bed - 150, bed))
        s.append(k.block(X0, XW, 0, 1, bed - 150, "blue"))
        top = bed - 150 - 2 * k.ROW_H - 18
        s.append(k.road(f"M{X0 + 6} {top} C 74 {top + 6}, 104 {top - 20}, 134 {top - 2} S 184 {top + 16}, {XW - 6} {top - 4}", k.HOT, 7))
        s.append(k.road(f"M{X0 + 8} {top - 18} C 64 {top - 34}, 114 {top - 6}, 152 {top - 26} S 198 {top - 40}, {XW - 4} {top - 22}", k.HOT, 7))
        s.append(k.road(f"M{XW - 8} {top - 32} C {XW + 30} {top - 46}, {XW + 46} {top - 10}, {XW + 24} {top + 8} S {XW + 2} {top + 34}, {XW + 34} {top + 44}", k.HOT, 7))
        s.append(k.label(X0, 34, "OVER A SUPPORT", 23))
    else:
        bed = 300
        s.append(k.bed(4, W - 4, bed))
        n = 24
        for i in range(n):
            z = (i + 0.5) * FINE
            xo = 100 + math.sqrt(max(2 * R * z - z * z, 0))
            back = [16, 30, 38, 30, 14][i - 10] if 10 <= i <= 14 else 0
            s.append(run(X0, xo - back, bed - (i + 1) * FINE, k.COLD, FINE))
            if back:
                s.append(f'<rect x="{k.n(xo - back)}" y="{k.n(bed - (i + 1) * FINE)}" width="{k.n(back)}" height="{k.n(FINE)}" fill="none" stroke="{k.BAD}" stroke-width="2" stroke-dasharray="4 4"/>')
        yb = bed - 14 * FINE
        xb = 100 + math.sqrt(2 * R * 108 - 108 * 108)
        s.append(k.road(f"M{k.n(xb - 34)} {k.n(yb - 4)} C {k.n(xb + 10)} {k.n(yb - 12)}, {k.n(xb + 40)} {k.n(yb + 10)}, {k.n(xb + 26)} {k.n(yb + 34)} S {k.n(xb - 2)} {k.n(yb + 44)}, {k.n(xb + 18)} {k.n(yb + 64)}", k.HOT, 7))
        s.append(k.label(X0, 34, "ON THE BED", 23))
    title = {"inward": "Fine courses on a round that turns inward at the top of a print",
             "support": "Fine courses laid over a support",
             "outward": "Fine courses on a round that grows outward off the bed"}[kind]
    desc = {"inward": "Each thin course is a little narrower than the one below, so all of it lands on plastic.",
            "support": "The first thin courses over the gap above a support come down as loose strands.",
            "outward": "Each thin course is a little wider than the one below. Part way up, edges already laid have drawn back, shown dashed, and the next road comes down on air."}[kind]
    return k.svg(W, H, "".join(s), title, desc)


def layer_height():
    p = _petgf()
    top = b.asset("petgf-overhangs-tee-top-round.jpg", f"{TEE}/physical-observations/2026-09-24-v11/IMG_7844.jpeg", TEE_REV)
    bot = b.asset("petgf-overhangs-tee-bed-round.jpg", f"{TEE}/physical-observations/2026-09-24-v11/IMG_7842.jpeg", TEE_REV)

    strip = [
        ("1", "Straight up", "One first layer and one layer height, on every part. This page."),
        ("2", "Lean", "Drawn at 45°. A round that starts on the bed starts as a chamfer."),
        ("3", "Bridge", "Slow, with extra plastic and the fan on. Out of sight."),
        ("4", "Fin", "A thin wall under a visible edge, one layer short of touching."),
    ]
    strip_html = "".join(
        f'<div><div style="display:flex; align-items:center; gap:16px; margin-bottom:10px"><span class="num" style="width:50px; height:50px; font-size:27px">{n}</span>'
        f'<h2 style="margin:0; font-size:42px">{t}</h2></div><p class="tiny" style="margin:0">{d}</p></div>'
        for n, t, d in strip)

    panels = (
        '<div class="grid3" style="gap:30px">'
        + f'<div>{_fine_panel("inward")}{tagline("Allowed", "good", "A show round that turns inward as it rises.")}</div>'
        + f'<div>{_fine_panel("support")}{tagline("Never", "bad", "Over a support.")}</div>'
        + f'<div>{_fine_panel("outward")}{tagline("Never", "bad", "On an edge that grows outward.")}</div>'
        + '</div>'
        + '<p class="tiny" style="margin:18px 0 0; color:var(--text)">Turning inward, every thin course lands on the one below. Over its supports, the fine '
          'courses of the front-top printed on Mark 1 on 3 October 2026 came down as spaghetti. The edge that grows outward is the bed-side round above, and the next page.</p>')

    story = dated([
        ("4 OCT 2026", "The pump cartridge and both bottom pieces of the enclosure go back to ordinary layers."),
        ("11 OCT", "Faucet lip coupons, Mark2. The same support gap came out 0.60 mm under fine layers and 0.48 mm under ordinary ones, because a gap "
                   "is a whole number of layers. On the first layer over a support: &ldquo;0.24 separates every time I think, it just recovers "
                   "better as more heavy layers are added.&rdquo;"),
        ("25 OCT", "Both faucets go to one layer height: &ldquo;&hellip;that didn&rsquo;t turn out so good, so I&rsquo;d like to go back to the same layer height everywhere&hellip;&rdquo;"),
        ("9 NOV", "The handholds are reshaped so that nothing needs them: &ldquo;We don&rsquo;t need any fine layers.&rdquo;"),
        ("12 NOV", "A fit coupon is sliced in finer layers to make a tenth of a millimetre show, and stopped: &ldquo;Do not use finer layers anywhere - "
                   "that is not an option - that is a completely different variable&rdquo;. That print has its own page, <i>Height moves one layer at a time</i>."),
    ])

    body = (
        b.head("Landing 1 · Straight up", "Layer height is not a knob.",
               "A print is a stack of courses, and the layer height is how thick each one is. It sets the step on every lean, the gap over "
               "every support, and how often the nozzle passes the same edge. Change it and all three change.", size=150, lede_size=52, top=44)
        + b.scope("PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + f'<div style="margin-top:30px; padding:22px 0 22px; border-top:3px solid var(--ink); border-bottom:2px solid var(--line)">'
          f'<h3 style="margin-bottom:16px">The landings, in PET-GF <span style="font-weight:400; color:var(--faint)">&nbsp;·&nbsp; the fifth, slicer support, has the next chapter</span></h3>'
          f'<div class="grid4" style="gap:44px">{strip_html}</div></div>'
        + '<div class="grid2" style="margin-top:30px; gap:50px">'
        + b.fig(top, "A black printed block whose top edge is rounded and smooth, with coarser layer lines on the wall below",
                "24 September 2026 · Mark2 · PET-GF", "The round at the top of the print, in fine layers. It turns inward as it rises. "
                "The band shows: the texture changes where the fine layers begin.", h=390, pos="50% 62%")
        + b.fig(bot, "The same block's lower rounded edge with a rough torn band part way up",
                "The same print, the bed side", "The same radius in the same fine layers, growing outward off the bed. About twenty "
                "courses went down clean. Then the edge lifted and the nozzle dragged through it.", h=390, pos="30% 68%", zoom=128)
        + '</div>'
        + b.rulebar(30, 28)
        + b.row(
            ("0 0 1040px",
             '<div class="grid2" style="gap:40px; margin-bottom:14px">'
             + b.stat(f'{b.setting(p, "/initial_layer_print_height")} <span>mm</span>', "the first layer, on the bed")
             + b.stat(f'{b.setting(p, "/layer_height")} <span>mm</span>', "every layer after it")
             + '</div>'
             + '<p class="tiny" style="margin:0 0 26px; color:var(--text)">Both live in the shared PET-GF project and every part inherits them. '
               'The first is the slicer&rsquo;s default. Nobody has had a reason to move it.</p>'
             + '<h3 style="margin:0 0 14px">Where a finer layer was ever allowed</h3>'
             + panels
             + b.still_open("One recipe still carries fine layers: front-top, on two show rounds at the top of its print. Whether the "
                            "instruction of 12 November, given about a fit coupon, retires them has not been asked.")),
            '<h3 style="margin:0 0 16px">How the fine layers went away</h3>'
            + b.quote("&hellip;thin layers create a visible artifact that should only be used when absolutely necessary&hellip;", "DEREK · 4 OCTOBER 2026", size=44)
            + '<div style="margin-top:30px">' + story + '</div>',
            gap=64)
        + '<div style="margin-top:28px">'
        + b.record(b.link("The shared PET-GF project", "hardware/printed-parts/petgf.3mf"),
                   b.link("The tee carrier&rsquo;s two rounds", f"{TEE}/physical-observations/2026-09-24-v11/README.md", TEE_REV),
                   b.link("Front-top, 3 October", f"{NSR}/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json"),
                   b.link("The gap under two layer heights", f"{COUPONS}/coarse-start-v1/README.md"),
                   b.link("The stopped coupon", "hardware/print-tests/front-top-wago-fit/2026-11-12-mark1-dots-3-4/print-job.json", "48e5d5364"),
                   b.link("Front-top&rsquo;s fine bands", f"{ENC}/trial-preparation/pieces.json"))
        + '</div>'
    )
    return Page("layer-height-is-not-a-knob", "PET-GF: layer height is not a knob", "petgf", body, right="Over air · layer height")


# ----------------------------------------------------------------------------- 2 a round off the bed
def _round_and_chamfer():
    """The tee carrier's bed-side edge in section, to scale: as first printed, and as accepted."""
    W, H, BED, R = 2170, 822, 716, 6.0

    def prof(z):
        return math.sqrt(max(2 * R * z - z * z, 0)) if z < R else R

    s = []
    # ---- left: the round, in fine layers (Mark2, 24 September 2026)
    L0, LX = 40, 180
    s.append(k.bed(14, 900, BED))
    rows = 76

    def back(i):
        if 20 <= i <= 27:
            return 72 * (i - 20) / 7
        if 27 < i <= 47:
            return 72 * (47 - i) / 20
        return 0

    edge = []
    for i in range(rows):
        z = (i + 0.5) * 0.08
        xo = LX + MM * prof(z)
        y = BED - (i + 1) * FINE
        s.append(run(L0, xo - back(i), y, k.COLD, FINE))
        if 20 <= i <= 47:
            edge.append((xo, xo - back(i), y))
    lost = [(a, y + FINE) for a, _, y in edge] + [(c, y + FINE) for _, c, y in reversed(edge)]
    s.append(poly(lost + [lost[0]], k.BAD, 3, "9 8"))
    for (x0, y0, dx) in ((598, 494, 0), (640, 458, 18), (672, 416, 40)):
        s.append(k.road(f"M{x0} {y0} C {x0 + 60} {y0 - 14}, {x0 + 118 + dx} {y0 + 12}, {x0 + 104 + dx} {y0 + 52} S {x0 + 46} {y0 + 84}, {x0 + 86 + dx} {y0 + 112} "
                        f"S {x0 + 150 + dx} {y0 + 96}, {x0 + 128 + dx} {y0 + 140}", k.HOT, 7))
    s.append(k.label(L0, 44, "24 SEPTEMBER 2026 · MARK2 · FINE LAYERS, 0.08 mm", 27, fill=k.BAD, weight=600))
    s.append(k.callout(1, 430, BED - 9 * FINE + 4, 560, BED - 34))
    s.append(k.callout(2, 606, BED - 27 * FINE, 500, 384))
    s.append(k.callout(3, 742, 546, 866, 600, "hot"))
    s.append(k.callout(4, LX + MM * prof(4.3) - 4, BED - 54 * FINE, 880, 236))
    s.append(k.label(L0 + 4, BED + 62, "THE BED"))

    # ---- right: the chamfer, in ordinary layers (Mark 1, 29 September 2026)
    R0, RX = 1150, 1290
    s.append(k.bed(1040, 2060, BED))
    slope, tangent = 0.5, 3.3167
    foot = prof(tangent) - slope * tangent

    def cham(z):
        return foot + slope * z if z <= tangent else prof(z)

    y, z0, j = BED, 0.0, 0
    while z0 < 6.1:
        h = 0.20 if j == 0 else 0.24
        y -= h * MM
        s.append(run(R0, RX + MM * cham(z0 + h / 2), y, k.COLD, h * MM))
        z0 += h
        j += 1
    arc = [(RX + MM * prof(t / 40 * tangent), BED - MM * t / 40 * tangent) for t in range(41)]
    s.append(poly(arc, "white", 9) + poly(arc, k.INK, 4, "14 10"))
    s.append(k.label(R0, 44, "29 SEPTEMBER 2026 · MARK 1 · ORDINARY LAYERS, 0.24 mm", 27, fill=k.INK, weight=600))
    s.append(k.dim(RX, BED + 44, RX + MM * foot, BED + 44, "3.7 mm MORE ON THE BED", off=34))
    s.append(k.label(RX + MM * foot + 40, BED + 62, "DASHED: THE ROUND AS DRAWN", 25))
    s.append(k.callout(5, RX + MM * cham(1.9) + 2, BED - 190, 1960, BED - 150))
    s.append(k.callout(6, RX + MM * prof(tangent) + 2, BED - MM * tangent, 1990, BED - MM * tangent - 30))
    bx = R0 - 34
    s.append(k.line(bx, BED, bx, BED - 610, k.INK, 3) + k.line(bx - 12, BED, bx + 12, BED, k.INK, 3) + k.line(bx - 12, BED - 610, bx + 12, BED - 610, k.INK, 3))
    s.append(vtext(bx - 18, BED - 130, "SIX WALLS THROUGH THIS BAND", 25, k.INK, 600))
    s.append(k.arrow(2130, 600, 2130, 190))
    s.append(vtext(2152, 550, "BUILD DIRECTION"))
    return k.svg(W, H, "".join(s), "A rounded edge on the bed in fine layers, and the chamfer that replaced it in ordinary layers",
                 "Two sections through the same edge of the tee carrier, drawn to scale. Left: the six millimetre round in courses 0.08 mm tall. "
                 "Part way up, the edges of courses already laid have drawn back, shown dashed, and loose roads hang where the next courses came "
                 "down on air. Right: a chamfer tangent to the same round, in courses 0.24 mm tall, each stepping out half its own height, with "
                 "the corner under the drawn round filled in.")


def round_off_the_bed():
    c = _catalog()
    fan = b.asset("petgf-overhangs-tee-fan-off.jpg", f"{TEE}/physical-observations/2026-09-24-v12/IMG_7847.jpeg", TEE_REV)
    notes = legend([
        (1, "", "About twenty courses go down clean."),
        (2, "", "Edges already laid draw back."),
        (3, "hot", "The next road out has nothing under it."),
        (4, "", "Higher, where the wall is steeper, the print recovers from the inside."),
        (5, "", "The chamfer starts steep. Each course steps out half its own height."),
        (6, "", "It meets the round here, tangent. Above this the curve is as drawn."),
    ], cols=3)
    tries = dated([
        ("FINE LAYERS", "Mark2, 24 September 2026. No supports. The top round clean, the bed round torn part way up."),
        ("FAN OFF", "Same file, same day. &ldquo;That turned out worse. Exploded basically.&rdquo;"),
        ("FAN STEADY", "Stopped when the edge failed again. Derek saw where: between the places the infill reached the wall. Where it reached, the edge held."),
        ("SIX WALLS", "Through the fine band, infill laid before walls. &ldquo;We have no spaghetti explosion. It&rsquo;s not a great curve, it&rsquo;s not even a "
                      "chamfer, it actually clearly angles the wrong direction&hellip; Still, probably good enough for now.&rdquo;"),
        ("A CHAMFER", "Mark 1, 29 September. Ordinary layers from the bed, six walls through the band, walls before infill, no supports. "
                      "The record: the bottom curve turned out great."),
    ], first=230)
    body = (
        b.head("Landing 2 · Lean · from the bed", "Start a round with a chamfer.",
               "A round edge that begins on the bed grows outward as it rises: each course is wider than the last. Printed in fine layers, "
               "its edges drew back and the next course came down on air. The fan did not fix it. The shape did.", size=150, lede_size=52, top=44)
        + b.scope("PET-GF · Mark2 and Mark 1, September 2026 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + f'<figure style="margin-top:24px">{_round_and_chamfer()}</figure>'
        + f'<div style="margin-top:6px">{notes}</div>'
        + b.rulebar(14, 28)
        + b.row(
            ("0 0 700px", b.fig(fan, "The rounded end of a black printed bar with a ragged band of loose strands part way up the curve",
                                "24 September 2026 · Mark2 · PET-GF · fan off", "The second try. The edge that grew off the bed is the ragged one.",
                                h=470, pos="50% 60%")
                          + '<div style="margin-top:26px">'
                          + b.quote("The layers already laid down end up shrinking, pulled back, pulled back just at the edges, and the next layer that goes down ends up printing in air&hellip;",
                                    "DEREK · 24 SEPTEMBER 2026", size=38)
                          + '</div>'),
            '<h3 style="margin:0 0 16px">What was tried, in order</h3>' + tries
            + '<div class="grid2" style="gap:50px; margin-top:30px">'
            + f'<div>{note("What we do now", "An edge that grows outward from the bed is drawn with a chamfer under it, tangent to the round and stepping out " + b.setting(c, "/overhang_round/OUTWARD_PER_HEIGHT") + " mm for each millimetre of rise. It prints in ordinary layers with a thicker band of walls and no support. On the enclosure that is back-top, whose roof edges start on the bed.")}</div>'
            + f'<div>{note("Our reading", "Nobody measured why the edge drew back. A thin course is a thin ribbon with little stiffness of its own, and as it shrinks there is not much to hold its free edge out. Infill tying into the wall did. So did six walls. That fits what Derek saw. It is not proof.")}</div>'
            + '</div>',
            gap=64)
        + b.still_open("The accepted print changed the shape, the layer height, the order of walls and infill, and the printer, all at once. No print "
                       "separates them. The record has no photograph of it, and no result yet for the same chamfer on another part.")
        + '<div style="margin-top:22px">'
        + b.record(b.link("The print log, 24 September", f"{ENC}/enclosure/print-log.md"),
                   b.link("Fan off: the result and Derek&rsquo;s account", f"{NSR}/2026-09-24-tee-carrier-plate-mark2-v12/physical-result.json"),
                   b.link("Six walls", f"{NSR}/2026-09-24-tee-carrier-plate-mark2-v14/physical-result.json", TEE_REV),
                   b.link("The chamfer, sliced and printed", f"{NSR}/2026-09-29-tee-chamfer-h2c-v6/README.md"),
                   b.link("Its acceptance", f"{TEE}/physical-acceptance.json", "d8d50f9a5"),
                   b.link("The slope today", "tools/hsm/shared-data/catalog/scalars.json"))
        + '</div>'
    )
    return Page("start-a-round-with-a-chamfer", "PET-GF: start a round with a chamfer", "petgf", body, right="Over air · rounds")




def pages():
    return [layer_height(), round_off_the_bed()]
