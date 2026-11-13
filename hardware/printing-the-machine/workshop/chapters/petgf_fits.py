"""PET-GF fits: how PET-GF parts fit each other and the bought parts they hold. Five pages:
allowances, connector pockets, snaps, pegs, and screws."""
import bookkit as b
import svgkit as k
from bookkit import Page

PART = "petgf"
ENC = "hardware/printed-parts/enclosure"
TESTS = "hardware/print-tests"
WAGO = f"{TESTS}/front-top-wago-fit"
SNAP = f"{TESTS}/rear-snap-retention"

# Files that own current values. Each is read again when the book is bound.
FITS = b.source("petgf-fits-catalog", "tools/hsm/shared-data/catalog/scalars.json")
RECIPE = b.source("petgf", "hardware/printed-parts/petgf.3mf", member="Metadata/project_settings.config")


# ----------------------------------------------------------------------------- drawing helpers
def beads(x0, y, count, w, h, fill=k.COLD, inset=2.0):
    """One course of `count` roads seen end-on, each w by h, starting at x0. The kit's own course()
    keeps the kit's bead width; the close-up drawings here need larger roads."""
    return "".join(
        f'<rect x="{k.n(x0 + i * w + inset)}" y="{k.n(y + inset)}" width="{k.n(w - 2 * inset)}" height="{k.n(h - 2 * inset)}" '
        f'rx="{k.n((h - 2 * inset) / 2)}" fill="{fill}"/>'
        for i in range(count)
    )


def road(x0, x1, y, h, fill=k.COLD, inset=2.0):
    """One road seen from the side between x0 and x1: a bead of any length."""
    return (f'<rect x="{k.n(x0 + inset)}" y="{k.n(y + inset)}" width="{k.n(x1 - x0 - 2 * inset)}" height="{k.n(h - 2 * inset)}" '
            f'rx="{k.n((h - 2 * inset) / 2)}" fill="{fill}"/>')


def dash(x0, y0, x1, y1, color=k.INK, width=4, pattern="14 10"):
    return k.line(x0, y0, x1, y1, color, width, pattern)


def rect(x, y, w, h, fill="none", stroke="none", sw=0, extra=""):
    return f'<rect x="{k.n(x)}" y="{k.n(y)}" width="{k.n(w)}" height="{k.n(h)}" fill="{fill}" stroke="{stroke}" stroke-width="{k.n(sw)}" {extra}/>'


def caps(text):
    return f'<span class="lab">{text}</span>'


# ----------------------------------------------------------------------------- 1 allowances
def _faces_hero():
    """Two parts one static allowance apart, as drawn and as printed, at 330 px to the millimetre."""
    S = 330.0
    slip = float(b.value(FITS, "/fits/slip"))
    bw, bh = 0.42 * S, 0.24 * S
    gap = slip * S
    PW = 690                                         # one panel
    W, H = 2 * PW, 590
    top, rows = 132, 5
    part_w = 2 * bw
    bottom = top + rows * bh

    def panel(ox, title, printed):
        xa0 = ox + (PW - (2 * part_w + gap)) / 2
        xa1 = xa0 + part_w                       # part A's drawn face
        xb0, xb1 = xa1 + gap, xa1 + gap + part_w  # part B's drawn face is xb0
        g = [k.label(ox + 30, 44, title, 30, fill=k.INK, weight=600)]
        yd = 92                                       # the allowance, dimensioned the same way over both
        g.append(k.line(xa1, yd - 22, xa1, yd + 22, k.INK, 3) + k.line(xb0, yd - 22, xb0, yd + 22, k.INK, 3))
        g.append(k.arrow(xa1 - 90, yd, xa1 - 4, yd) + k.arrow(xb0 + 90, yd, xb0 + 4, yd))
        g.append(k.label(xb0 + 106, yd + 10, b.setting(FITS, "/fits/slip") + " mm", 30, fill=k.INK, weight=600))
        if not printed:
            g.append(rect(xa0, top, part_w, rows * bh, k.WASH, k.INK, 4) + rect(xb0, top, part_w, rows * bh, k.WASH, k.INK, 4))
            g.append(k.label((xa0 + xa1) / 2, top + rows * bh / 2 + 10, "PART", 28, anchor="middle"))
            g.append(k.label((xb0 + xb1) / 2, top + rows * bh / 2 + 10, "PART", 28, anchor="middle"))
        else:
            proud_a = [0.035, 0.085, 0.020, 0.060, 0.050]   # how far each course stands past its drawn face, mm
            proud_b = [0.070, 0.030, 0.090, 0.045, 0.040]
            for r in range(rows):
                y = top + r * bh
                ea, eb = xa1 + proud_a[r] * S, xb0 - proud_b[r] * S
                g.append(road(xa0, xa0 + bw, y, bh) + road(xa0 + bw, ea, y, bh))
                g.append(road(eb, xb1 - bw, y, bh) + road(xb1 - bw, xb1, y, bh))
            sx, sy = xb0 - 0.040 * S + 14, top + 4 * bh + bh / 2 + 9   # a seam on part B's last course
            g.append(f'<circle cx="{k.n(sx)}" cy="{k.n(sy)}" r="{k.n(bh * 0.47)}" fill="{k.COLD}"/>')
            g.append(dash(xa1, top - 16, xa1, bottom + 18) + dash(xb0, top - 16, xb0, bottom + 18))
            g.append(k.line(sx + 6, sy + 16, sx + 52, bottom + 30, k.INK, 3) + f'<circle cx="{k.n(sx + 6)}" cy="{k.n(sy + 16)}" r="7" fill="{k.INK}"/>')
            g.append(k.label(sx + 62, bottom + 50, "A SEAM", 26, fill=k.INK))
            g.append(k.label(xa1 - 14, bottom + 50, "THE DRAWN FACES", 26, anchor="end", fill=k.INK))
        return "".join(g)

    body = panel(0, "AS DRAWN", False) + panel(PW, "AS PRINTED", True) + k.line(PW, 16, PW, H - 10, k.FAINT, 2)
    return k.svg(W, H, body, "Two parts one allowance apart, as drawn and as printed",
                 "Left: two parts drawn with flat faces and an empty gap between them. Right: the same two parts made of printed roads, "
                 "seen end-on. The ends of the roads and one seam stand past both drawn faces and meet in the gap. The drawn faces are "
                 "in the same place in both pictures.")


def _card_svg(kind):
    """A small section at the kit's own scale, 100 px to the millimetre, for one allowance."""
    S = 100.0
    slip = float(b.value(FITS, "/fits/slip"))
    slide = slip + float(b.value(FITS, "/fits/sliding_extra"))
    sup = float(b.value(FITS, "/fits/supported_surface"))
    floor = float(b.value(FITS, "/fits/layer_transition"))
    W, H = 500, 236
    G, BED = 40, 208                                   # bead grid origin
    g = []

    def x(i):
        return G + i * k.BEAD_W

    def y(r):
        return k.row_y(r, BED)

    if kind == "seat":
        gp = slip * S
        g.append(k.block(x(0), x(5), 0, 5, BED))
        g.append(f'<g transform="translate({k.n(gp)} 0)">' + k.block(x(5), x(10), 0, 5, BED) + "</g>")
        ya = y(5) - 30
        g.append(k.arrow(x(1), ya, x(4) + 10, ya) + k.arrow(x(9) + gp, ya, x(6) + gp - 10, ya))
    elif kind == "slide":
        gp = slide * S
        g.append(k.block(x(0), x(10), 0, 1, BED))
        g.append(f'<g transform="translate(0 {k.n(-gp)})">' + k.block(x(1), x(7), 2, 4, BED) + "</g>")
        ya = y(4) - gp - 30
        g.append(k.arrow(x(2), ya, x(9), ya))
    elif kind == "supported":
        gp = (slide + sup) * S
        g.append(k.block(x(0), x(10), 0, 1, BED))
        top = y(1) - gp                                 # the roof's drawn underside
        g.append(f'<g transform="translate(0 {k.n(-gp)})">' + k.block(x(1), x(9), 3, 5, BED) + "</g>")
        # the course that was laid on support: each road sagged a different amount
        for i, d in enumerate([5, 13, 2, 17, 8, 15, 3, 11]):
            g.append(f'<rect x="{k.n(x(1 + i) + 1.5)}" y="{k.n(top - k.ROW_H + 1.5)}" width="39" height="{k.n(21 + d)}" rx="10.5" fill="{k.COLD}"/>')
        g.append(k.road(f"M{k.n(x(5) + 8)} {k.n(top + 4)} C {k.n(x(5) + 50)} {k.n(top + 34)}, {k.n(x(7) + 10)} {k.n(top + 34)}, {k.n(x(8) - 8)} {k.n(top + 4)}", k.COLD, 5))
        g.append(dash(x(0), top, x(10), top, k.INK, 3, "10 8"))
    else:
        gp = slide * S
        fl = floor * S
        g.append(k.block(x(0), x(10), 0, 1, BED))
        g.append(k.block(x(0), x(2), 2, 6, BED) + k.block(x(8), x(10), 2, 6, BED))
        # the first courses of each wall round the corner where it leaves the floor
        for r, d in ((2, 14), (3, 6)):
            g.append(f'<rect x="{k.n(x(2) - 12)}" y="{k.n(y(r) + 1.5)}" width="{k.n(d + 14)}" height="21" rx="10.5" fill="{k.COLD}"/>')
            g.append(f'<rect x="{k.n(x(8) - d - 2)}" y="{k.n(y(r) + 1.5)}" width="{k.n(d + 14)}" height="21" rx="10.5" fill="{k.COLD}"/>')
        px0, px1 = x(2) + gp, x(8) - gp                # the part coming home, drawn square
        py1 = y(1) - gp - fl
        g.append(rect(px0, y(7) - 6, px1 - px0, py1 - y(7) + 6, "white", k.INK, 4))
        g.append(k.label((px0 + px1) / 2, y(4) + 2, "PART", 23, anchor="middle"))
    titles = {"seat": "Two faces that close head-on", "slide": "One face sliding past another",
              "supported": "A face printed over support, above its mate", "floor": "A part coming home to the floor of a pocket"}
    return k.svg(W, H, "".join(g), titles[kind])


def allowances():
    slip, extra = b.setting(FITS, "/fits/slip"), b.setting(FITS, "/fits/sliding_extra")
    sup, floor = b.setting(FITS, "/fits/supported_surface"), b.setting(FITS, "/fits/layer_transition")
    cards = [
        ("seat", "A seat", f"{slip} mm",
         "Two faces that only have to close. It is a friction fit and hard to slide.",
         "The faces that meet head-on when front and back come together. The back of a nameplate."),
        ("slide", "A slide", f"{slip} + {extra} mm",
         "One face has to travel past the other. It is still a tight slide.",
         "Rails, tongues and pin passages. The pump cradle going into its bay."),
        ("supported", "Under a supported face", f"+ {sup} mm",
         "An underside printed over support sags into bumps and keeps loose strands. Each such face in a gap adds this once.",
         "The front rail catch has one. The rear catch has two."),
        ("floor", "At the floor of a pocket", f"+ {floor} mm",
         "The first courses of a wall round the corner where it leaves the floor, so a pocket is narrowest at the bottom.",
         "The floor under the pump cradle. The floor under the cold core."),
    ]
    card_html = "".join(
        f'<div><figure style="background:var(--wash)">{_card_svg(kind)}</figure>'
        f'<p style="margin:18px 0 2px; font:650 42px/1.15 \'IBM Plex Sans\'; color:var(--ink)">{title}</p>'
        f'<p class="mono" style="margin:0 0 12px; font-size:33px; font-weight:600; color:var(--hot)">{val}</p>'
        f'<p class="small" style="margin:0 0 10px; font-size:33px">{what}</p>'
        f'<p class="tiny" style="margin:0">{where}</p></div>'
        for kind, title, val, what, where in cards
    )
    rail = b.asset("petgf-fits-rail-pair.jpg", f"{TESTS}/petgf-dense-roofs/rail-fit-30/photos/03-mating-rail-fit.jpg")
    left = (
        f'<figure>{_faces_hero()}</figure>'
        '<div class="grid2" style="margin-top:6px; gap:40px">'
        f'<p class="cap" style="margin:0; font-size:32px">{caps("How it gets read")}Two flat faces and nothing between them. Read that way, '
        'the gap looks like room to spend somewhere else in a stack.</p>'
        f'<p class="cap" style="margin:0; font-size:32px">{caps("What it is")}Both faces stand a little past where they were drawn. Seated under a screw '
        'or its own weight, a part still rests about where it was drawn.</p></div>'
    )
    right = (
        b.quote("You do realize our clearances are not filled with free space but are actually filled with rough edges of materials? "
                "&hellip; if you put a 1mm object next to a 1mm object pressed with several lbs of fource you still don&rsquo;t get a "
                "2 mm object, you get a 2.15 mm one.", "DEREK · 22 OCTOBER 2026", size=42)
        + '<div style="margin-top:44px">'
        + b.quote("Our clearance rules are not &quot;we need more free space&quot;, they are &quot;this is the reality of what these "
                  "surfaces are&quot;", "DEREK · THE SAME DAY", size=42) + "</div>"
    )
    body = (
        b.head("Fits · Printed face against printed face", "A clearance is surface, not air.",
               "A printed face is not the flat plane that was drawn. It is the sides of roads, the ridges between courses and a seam "
               "on every loop. Press two together and those touch first. The gap we draw between parts is the room they take.", size=146, lede_size=54)
        + b.scope("PET-GF against PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="other pairs")
        + b.row(("0 0 1380px", left), right, gap=66, style="margin-top:28px")
        + f'<div class="grid4" style="margin-top:30px">{card_html}</div>'
        + b.rulebar(24, 24)
        + b.row(
            ("0 0 650px", b.fig(rail, "A short length of printed rail engaged in the printed channel it slides in",
                                "10 November 2026 · Mark 1 · PET-GF",
                                "A slice of the sliding rail in a slice of the wall it slides into, cut from the real parts "
                                "with their own allowances.", h=380, pos="0% 5%", zoom=182)),
            '<h2 style="font-size:44px">What we do now</h2>'
            '<p class="small" style="font-size:34px">Every allowance stays on the face it describes. A face that seats, bears or stops a '
            'stroke gets one too. Derek, 16 October: &ldquo;SEATING FACES ARE NOT EXEMPT FROM THE RULES!&rdquo;</p>'
            '<p class="small" style="font-size:34px">The slicer&rsquo;s hole and contour corrections stay at '
            f'{b.setting(RECIPE, "/xy_hole_compensation")}, so every fit is in the drawing, where it can be read.</p>'
            '<p class="small" style="font-size:34px; margin:0"><b>7 October 2026.</b> Three quarters of the enclosure, the foam shell, the pump '
            'cradle and cap, a tee carrier and a funnel frame were on the bench: &ldquo;And all those prints fit together right now&rdquo;.</p>',
            ("0 0 640px",
             '<p class="small" style="font-size:34px"><b>The pocket floor came first.</b> On 23 September Derek said the bottom of a printed cavity '
             '&ldquo;is almost guaranteed to narrow at the tip because of the layer transitions resulting in very slight rounding&rdquo;.</p>'
             + b.still_open("The rail slice went together with &ldquo;plenty of clearance&rdquo; and &ldquo;might be a little bit loose&rdquo;. "
                            "Derek left it alone until a full-length rail is tried. That result is not in the record.")),
            gap=56)
        + '<div style="margin-top:14px">' + b.record(
            b.link("The allowances and where each is used", f"{ENC}/clearance-audit.md"),
            b.link("The file that owns them", "tools/hsm/shared-data/catalog/scalars.json"),
            b.link("The rail slice", f"{TESTS}/petgf-dense-roofs/rail-fit-30/physical-result.json"),
            b.link("The pocket floor, 23 September", "hardware/printed-parts/cadlib/fits.py", "87b6b440f"),
            b.link("What fitted on 7 October", "hardware/ledger/fitted.json")) + "</div>"
    )
    return Page("a-clearance-is-surface-not-air", "PET-GF fits: a clearance is surface, not air", PART, body, right="Fits · 1 of 4")


# ----------------------------------------------------------------------------- 2 pockets
JUNCTIONS = b.source("petgf-fits-junctions", "hardware/manifold-layout/junctions.json")


def _dots(n, color="var(--ink)"):
    return '<span style="display:inline-flex; gap:9px; vertical-align:middle">' + "".join(
        f'<span style="width:22px; height:22px; border-radius:50%; background:{color}; display:inline-block"></span>' for _ in range(n)) + "</span>"


def _pocket_svg():
    """The pocket that fitted, seen through its mouth: walls at the connector's size, a bridged roof just clear of it."""
    W, H, BED = 620, 540, 514
    xl, xr = 58, 562                                   # outside of the left and right walls
    TOPW = 16                                          # the last course of wall under the roof

    def y(r):
        return k.row_y(r, BED)

    wl, wr = xl + 3 * k.BEAD_W, xr - 3 * k.BEAD_W      # the pocket's two wall faces
    g = [k.block(xl, xr, 0, 2, BED)]                   # floor
    g.append(k.block(xl, wl, 3, TOPW, BED) + k.block(wr, xr, 3, TOPW, BED))
    g.append(k.block(xl, wl, TOPW + 1, TOPW + 1, BED) + k.strand(wl, wr, y(TOPW + 1), k.COLD) + k.block(wr, xr, TOPW + 1, TOPW + 1, BED))   # the first roof course bridges
    g.append(k.block(xl, xr, TOPW + 2, TOPW + 3, BED))
    top = y(TOPW) + 20                                 # the connector stops a fifth of a millimetre under the roof, drawn to scale
    g.append(rect(wl, top, wr - wl, y(2) - top, "white", k.INK, 4))
    xm = (wl + wr) / 2
    g.append(k.label(xm, y(6), "CONNECTOR", 25, anchor="middle"))
    g.append(k.arrow(26, y(1), 26, y(TOPW + 2), k.INK, 4))
    g.append(k.callout(1, wr, y(10), wr + 62, y(10)))
    g.append(k.callout(2, xm, top - 10, xm, top + 76))
    g.append(k.callout(3, xm - 80, y(TOPW + 1) + 12, xm - 80, y(TOPW + 3) - 4))
    return k.svg(W, H, "".join(g), "The pocket that fitted, seen through its mouth",
                 "A connector between two printed walls with no gap drawn at either side. The roof over it is a bridge from wall to wall, "
                 "and the connector stops a fifth of a millimetre short of it. An arrow at the left shows the build direction, upward.")


def pockets():
    R1 = "cbd8efc66"      # the full-depth coupons and their photographs
    crack = b.asset("petgf-fits-wago-crack.jpg", f"{WAGO}/2026-11-12-mark1/physical-result/IMG_8623.jpeg", R1, max_px=2000)
    rest = b.asset("petgf-fits-wago-rest.jpg", f"{WAGO}/2026-11-12-mark1/physical-result/IMG_8624.jpeg", R1)
    spread = b.asset("petgf-fits-wago-spread.jpg", f"{WAGO}/2026-11-12-mark1/physical-result/IMG_8625.jpeg", R1)
    now = b.setting(JUNCTIONS, "/well_fit_mm")

    def cell(mark, value, words, hot=False):
        edge = "var(--hot)" if hot else "var(--ink)"
        return (f'<div style="border-top:8px solid {edge}; padding-top:14px">'
                f'<p style="margin:0 0 10px; height:30px; line-height:30px">{mark}</p>'
                f'<p class="mono" style="margin:0 0 8px; font-size:34px; font-weight:600; color:{edge}">{value}</p>'
                f'<p class="tiny" style="margin:0; font-size:30px; color:var(--text)">{words}</p></div>')

    ladder = (
        '<p class="lab" style="margin:0 0 14px">The pocket&rsquo;s walls against the connector&rsquo;s catalog size, each side · 12 and 13 November 2026 · tightest first</p>'
        '<div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:30px">'
        + cell(_dots(2), "0.60 under", "Derek&rsquo;s first guess, times one and a half.")
        + cell(_dots(1), "0.35 under", "His first guess. Neither coupon took a connector straight.")
        + cell(_dots(4), "0.10 under", "&ldquo;it&rsquo;s possible to get in there, but it&rsquo;s too tight.&rdquo; Its height differed too.")
        + cell(_dots(5), "0.05 under", "The next morning: &ldquo;Size wise I think we&rsquo;re getting very good&rdquo;.")
        + cell(_dots(3, "var(--hot)"), "0.00", "&ldquo;the WAGO fits in very easily, but is still held pretty well. It&rsquo;s awesome.&rdquo;", hot=True)
        + cell('<span class="mono" style="font-size:24px; letter-spacing:.06em; color:var(--muted)">FRONT-TOP AS PRINTED</span>', f"{now} over",
               "The seat allowance of the page before. &ldquo;in Y they are a bit loose.&rdquo;")
        + "</div>"
    )
    right = (
        '<div class="grid2" style="gap:40px">'
        + b.fig(rest, "A caliper across the solid end of a black coupon reads 21.83", "At rest",
                "<b>21.83 mm</b> across the coupon where nothing pushes on it.", h=430, pos="50% 82%")
        + b.fig(spread, "The same caliper across the pocket walls, with the connector in, reads 22.53", "Spread",
                "<b>22.53 mm</b> across a pocket with a connector shoved in. Walls three and a half millimetres thick had moved 0.7 mm.",
                h=430, pos="50% 82%")
        + "</div>"
        + '<div style="margin-top:40px">'
        + b.quote("Prints turned out well. My guesses on adjustments were way off. It looks likethe PET-GF does flex enough at some points "
                  "there to allow me to corner shove in a wago, but when I pressed the wago to the edge, you can see it snapped the edge "
                  "of the receiver.", "DEREK · 12 NOVEMBER 2026", size=42) + "</div>"
    )
    legend = "".join(
        f'<div style="display:flex; gap:16px; align-items:flex-start; margin-bottom:18px"><span class="num" style="width:50px; height:50px; font-size:27px">{n}</span>'
        f'<p class="tiny" style="margin:0; font-size:31px; color:var(--text)">{t}</p></div>'
        for n, t in (
            ("1", "<b>Wall to wall: the catalog size.</b> No gap is drawn."),
            ("2", "<b>Under the roof: a fifth of a millimetre,</b> as sliced. Up the build a pocket moves a whole course at a time. "
                  "See &ldquo;Height moves one layer at a time&rdquo;."),
            ("3", "<b>The roof is a bridge</b> from wall to wall."),
        ))
    body = (
        b.head("Fits · A bought part in a printed pocket", "PET-GF does not stretch.",
               "Glass-filled PET is stiff. A pocket wall gives a few tenths of a millimetre and then an edge lets go. A hard part "
               "held by friction gets a pocket drawn at the part&rsquo;s own size, give or take a tenth of a millimetre.", lede_size=54)
        + b.scope("PET-GF, black Fiberon PET-GF15 · Mark 1 · textured PEI · left 0.4 mm", not_tried="PETG, PET-CF")
        + b.row(
            ("0 0 800px", b.fig(crack, "The corner of a black printed pocket split open beside an orange lever connector",
                                "12 November 2026 · Mark 1 · PET-GF",
                                "A fit coupon for the two lever connectors in front-top, its pockets drawn narrower than the connectors. "
                                "Pressed against the edge, a connector split it.", h=750, pos="60% 44%", zoom=118)),
            right, gap=70, style="margin-top:32px")
        + f'<div style="margin-top:34px">{ladder}</div>'
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 860px",
             '<p class="lab" style="margin:0 0 12px">What fitted · seen through the pocket&rsquo;s mouth · not to scale</p>'
             + b.row(("0 0 440px", f'<figure style="background:var(--wash)">{_pocket_svg()}</figure>'), legend, gap=30)),
            '<h2 style="font-size:44px">Twice before</h2>'
            '<p class="small" style="font-size:34px">On 5 October 2026, on Mark 1, Derek tried ladders of pockets for a ring magnet and for '
            'the four posts of a valve. He chose the pocket at the part&rsquo;s nominal size both times.</p>'
            '<h2 style="font-size:44px">What we do now</h2>'
            '<p class="small" style="font-size:34px; margin:0">A ladder for a hard part starts at its catalog size and steps a twentieth or a tenth '
            'of a millimetre either way. Each coupon is cut from the real part at the real depth, with dots in the plastic.</p>',
            ("0 0 560px",
             '<h2 style="font-size:44px">Where it stands</h2>'
             '<p class="small" style="font-size:34px">Three dots is accepted on a coupon and five is close behind. A sixth went onto Mark 1 '
             'on 13 November: the slim connector&rsquo;s walls a tenth under again, at three dots&rsquo; height. The front-top on the machine '
             'still has the looser pockets.</p>'
             + b.still_open("Nobody put a caliper on a connector: the catalog size is the maker&rsquo;s figure. The record does not say "
                            "which coupon cracked or which pocket was too tight.")),
            gap=50)
        + '<div style="margin-top:20px">' + b.record(
            b.link("The cracked coupon and the caliper", f"{WAGO}/2026-11-12-mark1/physical-result/physical-result.json", R1),
            b.link("The coupon that fitted", f"{WAGO}/2026-11-12-mark1-dots-3-4-standard-layers/physical-result/physical-result.json", "eb3ec0fcf"),
            b.link("Five dots", f"{WAGO}/2026-11-12-mark1-five-dot/physical-result/physical-result.json", "474000169"),
            b.link("Six dots, printing", f"{WAGO}/2026-11-13-mark1-six-dot-rail-trees/print-job.json", "9af81b4f3"),
            b.link("The connectors&rsquo; catalog sizes", "hardware/reference/wago-221/replica-evidence.json"),
            b.link("Magnet and valve ladders", f"{ENC}/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json")) + "</div>"
    )
    return Page("pet-gf-does-not-stretch", "PET-GF fits: PET-GF does not stretch", PART, body, right="Fits · 2 of 4")

# ----------------------------------------------------------------------------- 3 snaps
ABOVE = b.source("petgf-fits-above-core", "hardware/manifold-layout/above-core.json")
CAPS = f"{ENC}/rear-equipment-caps"


def _leaf_svg(kind):
    """One leaf pushed down at its tip, built two ways: courses stacked along its length, or roads running its length."""
    W, H = 640, 300
    bw, bh = 42.0, 24.0                                # a road is 42 wide and one course is 24 thick, as elsewhere in the book
    xb, x0, ytop = 40, 160, 82                         # the body's left side, where the leaf leaves it, and the leaf's upper face
    thick, crack, tail = 3 * bw, 160 + 2 * bh, 14
    g = []
    if kind == "across":
        # the build runs left to right: every course is a column, and the leaf is a stack of columns
        def column(x, n_, y):
            return "".join(f'<rect x="{k.n(x + 1.5)}" y="{k.n(y + i * bw + 1.5)}" width="{k.n(bh - 3)}" height="{k.n(bw - 3)}" rx="{k.n((bh - 3) / 2)}" fill="{k.COLD}"/>'
                           for i in range(n_))
        g += [column(xb + i * bh, 5, ytop - bw) for i in range(5)]
        g += [column(x0 + i * bh, 3, ytop) for i in range(2)]
        g.append(f'<g transform="rotate(7 {k.n(crack)} {k.n(ytop + thick)})">' + "".join(column(crack + i * bh, 3, ytop) for i in range(tail)) + "</g>")
        g.append(k.line(crack + 5, ytop - 26, crack + 1, ytop + thick + 8, k.BAD, 4, "9 8"))
        g.append(k.label(crack + 20, ytop - 30, "A WELD LETS GO", 23, fill=k.BAD, weight=600))
        g.append(k.arrow(xb, H - 24, xb + 130, H - 24, k.INK, 4) + k.label(xb + 146, H - 15, "BUILD DIRECTION", 23))
    else:
        # seen from above the bed: every road of a layer runs from inside the body to the tip
        for i in range(5):
            yy = ytop - bw + i * bw + bw / 2
            d = f"M{k.n(xb + 20)} {k.n(yy)} H{k.n(x0 - 20)}"
            if 1 <= i <= 3:
                d = (f"M{k.n(xb + 20)} {k.n(yy)} H{k.n(crack)} "
                     f"C {k.n(crack + 130)} {k.n(yy)}, {k.n(crack + 240)} {k.n(yy + 14)}, {k.n(crack + tail * bh - 26)} {k.n(yy + 40)}")
            g.append(k.road(d, k.COLD, bw - 3))
        g.append(k.label(crack + 20, ytop - 30, "ROADS RUN ITS LENGTH", 23, fill=k.INK, weight=600))
        g.append(f'<circle cx="{k.n(xb + 14)}" cy="{k.n(H - 24)}" r="13" fill="none" stroke="{k.INK}" stroke-width="4"/><circle cx="{k.n(xb + 14)}" cy="{k.n(H - 24)}" r="4" fill="{k.INK}"/>')
        g.append(k.label(xb + 40, H - 15, "BUILD DIRECTION, TOWARD YOU", 23))
    g.append(k.arrow(572, 14, 572, 96, k.INK, 5))    # the same push in both
    title = {"across": "A leaf built in courses across its length cracks at the root",
             "along": "A leaf whose roads run its length bends as one"}[kind]
    desc = {"across": "A leaf sticks out from a body and is pushed down at its tip. It is built of courses stacked along its length, like a roll "
                      "of coins. Near the root one course has let go of the next and a crack has opened on the stretched side.",
            "along": "The same leaf, seen from above the bed. Three long roads run from inside the body to the tip and bend together under the same push."}[kind]
    return k.svg(W, H, "".join(g), title, desc)


def snaps():
    from proj import projector
    step = "printed-parts/enclosure/rear-equipment-caps/regulator-snap-cap.step"
    cam, up, target, span, show = [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 0.0, 18.0], 26.0, 720
    profile = b.render("petgf-fits-snap-profile.png", dict(step=step, cam=cam, up=up, target=target, span=span, size="1080x1080", edges=True,
                                                           materials=[{"names": ["regulator-snap-cap"], "color": "#3a4654", "roughness": 0.85}]))
    pm = projector(cam, target, span, (show, show), up=tuple(up))
    # each disc stands beside its feature, on open ground, so the feature itself stays in view
    marks = [("1", [-8.0, -9.5, 36.0], ""), ("2", [-1.5, 24.0, 36.0], "hot"), ("3", [-16.6, 23.4, 36.0], ""),
             ("4", [4.6, 14.6, 36.0], ""), ("5", [15.4, 15.6, 36.0], "")]
    discs = "".join(f'<span class="num on-model {c}" style="left:{pm(pt)[0]:.0f}px; top:{pm(pt)[1]:.0f}px">{n}</span>' for n, pt, c in marks)
    rise = b.setting(ABOVE, "/rear_plumbing/snap_tip_rise_mm")
    items = [
        ("1", "", "Body", "A thick block shaped to the part it holds. It does not flex."),
        ("2", "hot", "Leaf", "The spring. Two millimetres thick and about twenty-two long since 2 November. Thinner tore. Thicker bent only at its root."),
        ("3", "", "Root", "A rounded inside corner, so the bend spreads along the leaf."),
        ("4", "", "Catch", "A flat face square to the pull. It will not cam open. To let go, the leaf is spread by hand."),
        ("5", "", "Lead-in", f"One solid slope to a point, {rise} mm long, that wedges the leaf aside on the way in."),
    ]
    legend = "".join(
        f'<div style="display:flex; gap:20px; align-items:flex-start; margin-bottom:20px"><span class="num {c}">{n}</span>'
        f'<div><p style="margin:0 0 2px; font:650 38px/1.2 \'IBM Plex Sans\'; color:var(--ink)">{t}</p>'
        f'<p class="tiny" style="margin:0; font-size:31px; color:var(--text)">{d}</p></div></div>'
        for n, c, t, d in items)
    torn = b.asset("petgf-fits-snap-torn-wing.jpg", f"{SNAP}/physical-result/meter-fracture.jpg")

    def cell(when, title, words, hot=False):
        edge = "var(--hot)" if hot else "var(--ink)"
        return (f'<div style="border-top:8px solid {edge}; padding-top:14px">'
                f'<p class="mono" style="margin:0 0 6px; font-size:25px; letter-spacing:.08em; color:var(--muted)">{when}</p>'
                f'<p style="margin:0 0 8px; font:650 35px/1.15 \'IBM Plex Sans\'; color:{edge}">{title}</p>'
                f'<p class="tiny" style="margin:0; font-size:29px; color:var(--text)">{words}</p></div>')

    week = (
        '<p class="lab" style="margin:0 0 14px">One week of caps · 1 to 8 November 2026 · Mark 1 and Mark2 · PET-GF</p>'
        '<div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:30px">'
        + cell("1 NOV", "One thin arch", "The pump&rsquo;s first cap was all spring. &ldquo;&hellip;this has basically 0 hold.&rdquo; It became a thick box with two separate leaves.")
        + cell("1 NOV", "Thin leaves, across", "Flat catches on leaves 1.3 mm thick, the caps printed as they sit. Two of five tore while fitting.")
        + cell("2 NOV", "Thick leaves, on end", "2.6 mm, nearly twice as long, every cap on its end. They held, and bent only at the root.")
        + cell("2 NOV", "In the middle", "2.0 mm with a rounded root. That night three fits were &ldquo;perfect, or close enough to perfect&rdquo;.")
        + cell("3 NOV", "No tunnels", "A screwdriver tunnel under each catch bent the leaf only where the blade touched. &ldquo;Please just remove those.&rdquo;")
        + cell("8 NOV", "A long point", "The lead-in doubled. &ldquo;The longer pointed tips on the snaps there worked beautifully.&rdquo;", hot=True)
        + "</div>"
    )
    body = (
        b.head("Fits · Snaps", "A snap bends within its layers.",
               "A snap is a leaf that bends out of the way and springs back. Printed so that every road runs the length of the leaf, "
               "the plastic itself takes the bend. Printed in courses across the leaf, the bend pulls one course off the next.",
               size=150, lede_size=54)
        + b.scope("PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm · caps printed solid", not_tried="PETG, TPU")
        + b.row(
            ("0 0 700px", b.fig(torn, "A black printed cap over a white flow meter, its top torn open along the layers",
                                "1 November 2026 · Mark2 · PET-GF",
                                "A first-round cap, printed as it sits. Its layers run across both leaves. Fitting it over the flow meter "
                                "tore it.", h=600, pos="10% 28%", zoom=115)),
            ("0 0 720px", f'<figure style="position:relative; width:{show}px; height:{show}px; background:var(--wash)">'
                          f'<img src="art/{profile}" alt="The water regulator&rsquo;s cap seen down its build direction" '
                          f'style="position:absolute; left:0; top:0; width:{show}px; height:{show}px">{discs}</figure>'
                          '<p class="cap"><span class="lab">The cap now · looking down at the bed</span>It stands on its end, so every layer is this shape.</p>'),
            legend, gap=50, style="margin-top:30px")
        + b.rulebar(30, 30)
        + b.row(
            ("0 0 640px", f'<figure style="background:var(--wash)">{_leaf_svg("across")}</figure>'
                          '<p class="cap"><span class="lab">Across</span>The bend is carried by the welds between courses.</p>'),
            ("0 0 640px", f'<figure style="background:var(--wash)">{_leaf_svg("along")}</figure>'
                          '<p class="cap"><span class="lab">Along</span>The bend is carried by the roads themselves.</p>'),
            b.quote("Those snaps need to be, the wings need to be at least twice as thick.", "DEREK · 1 NOVEMBER 2026", size=40)
            + '<div style="margin-top:30px">'
            + b.quote("Can they all be designed to be printed on their end like the pump cap?", "DEREK · THE SAME DAY", size=40) + "</div>",
            gap=50)
        + f'<div style="margin-top:34px">{week}</div>'
        + b.rulebar(30, 26)
        + b.row(
            b.block("What we do now",
                    "Stand a snap part on the bed so its leaves lie in the layers. Give it a stiff body and separate leaves. Leave the leaves "
                    "where fingers can spread them. Keep the catch flat and put the ease in a long lead-in."),
            ("0 0 900px", b.still_open("Every verdict here is Derek&rsquo;s hand. No snap has been measured for force, cycled or shaken on a running "
                                       "pump. The long point was approved on the water regulator&rsquo;s cap. The other caps now carry it and "
                                       "have not been tried.")),
            gap=60)
        + '<div style="margin-top:18px">' + b.record(
            b.link("&ldquo;basically 0 hold&rdquo;", f"{TESTS}/pump-mount-fit/physical-result.json"),
            b.link("The round that tore", f"{SNAP}/physical-result/physical-result.json"),
            b.link("Thick leaves", f"{SNAP}/v2/physical-result/physical-result.json"),
            b.link("In the middle", f"{SNAP}/v4/physical-result/physical-result.json"),
            b.link("No tunnels", f"{TESTS}/receiver-tool-access/physical-result/physical-result.json"),
            b.link("The long point", f"{CAPS}/prints/2026-11-07-ceiling-down-mark2/physical-result.json"),
            b.link("The caps today", f"{CAPS}/README.md")) + "</div>"
    )
    return Page("a-snap-bends-within-its-layers", "PET-GF fits: a snap bends within its layers", PART, body, right="Fits · 3 of 4")


# ----------------------------------------------------------------------------- 4 pegs
FAUCET = "hardware/printed-parts/faucet"


def _peg_svg(kind):
    """A plate on the bed in section. Left: a peg standing on it, sheared at its foot. Right: a broad pedestal with a screw through it."""
    W, H, BED = 640, 440, 396
    X0 = 41

    def x(i):
        return X0 + i * k.BEAD_W

    def y(r):
        return k.row_y(r, BED)

    g = [k.bed(16, W - 16, BED)]
    if kind == "peg":
        g.append(k.block(x(0), x(13), 0, 3, BED))
        g.append(k.block(x(5), x(8), 4, 4, BED))                                   # the stub left on the plate
        g.append(f'<g transform="translate(20 -3) rotate(6 {k.n(x(8))} {k.n(y(4))})">' + k.block(x(5), x(8), 5, 12, BED) + "</g>")
        g.append(k.line(x(5) - 26, y(4), x(8) + 44, y(4), k.BAD, 4, "9 8"))
        g.append(k.label(x(8) + 58, y(4) + 9, "ONE WELD", 24, fill=k.BAD, weight=600))
        g.append(k.arrow(x(1), y(10), x(5) - 4, y(10), k.INK, 5))
        g.append(k.label(x(1), y(10) - 22, "A SIDEWAYS PUSH", 24, fill=k.INK))
        g.append(k.label(x(9) + 10, y(1) + 4, "THE PLATE", 24, fill="white"))
    else:
        sh = k.FAINT                                                               # the shell this plate fastens to, drawn pale
        g.append(k.block(x(0), x(5), 0, 1, BED) + k.block(x(8), x(13), 0, 1, BED))  # plate, with a recess for the screw's head
        g.append(k.block(x(0), x(6), 2, 3, BED) + k.block(x(7), x(13), 2, 3, BED))
        g.append(k.block(x(4), x(6), 4, 7, BED) + k.block(x(7), x(9), 4, 7, BED))   # the pedestal, bored through
        g.append(k.block(x(0), x(4), 4, 12, BED, sh) + k.block(x(9), x(13), 4, 12, BED, sh))
        g.append(k.block(x(4), x(6), 8, 12, BED, sh) + k.block(x(7), x(9), 8, 12, BED, sh))
        xc = x(6) + k.BEAD_W / 2
        g.append(rect(xc - 30, y(11), 60, y(7) - y(11), k.BRASS))                   # the insert
        g.append(rect(xc - 13, y(11) + 10, 26, BED - 40 - y(11) - 10, k.INK))       # the screw
        g.append(rect(xc - 46, BED - 42, 92, 34, k.INK, extra='rx="6"'))
        g.append(k.callout(1, x(4) + 8, y(5), x(1) + 10, y(5)))
        g.append(k.callout(2, xc, y(2) + 4, x(11) + 20, y(2) + 4))
        g.append(k.callout(3, xc + 30, y(9) - 4, x(11) + 20, y(9) - 4))
    title = {"peg": "A peg standing on a plate, sheared off where it joins the plate",
             "screw": "A broad pedestal on the same plate, with a screw through it into an insert"}[kind]
    desc = {"peg": "A plate lies on the bed with a slender peg standing up from it. Every course of the peg lies across its length. A sideways push "
                   "near its top has sheared it off along the one weld where it joins the plate.",
            "screw": "The same plate with a short, broad pedestal in place of the peg. A steel screw passes up from a recess under the plate, "
                     "through the pedestal, into a brass insert in the part above. The pedestal locates and the screw holds."}[kind]
    return k.svg(W, H, "".join(g), title, desc)


def pegs():
    base = b.asset("petgf-fits-split-base.jpg", f"{SNAP}/v2/physical-result/pump-base-fracture.jpg")
    plate = b.render("petgf-fits-plate-pedestals.png",
                     dict(step="printed-parts/faucet/above-counter-plate/above-counter-plate.step", cam=[0.45, -0.8, 0.62], target=[0.0, 0.0, -1.0],
                          span=27.0, size="1100x800", edges=True,
                          materials=[{"names": ["above-counter-plate"], "color": "#4a5a6b", "roughness": 0.85}]))
    legend = "".join(
        f'<span style="display:inline-flex; align-items:center; gap:12px; margin-right:26px"><span class="num" style="width:44px; height:44px; font-size:25px">{n}</span>{t}</span>'
        for n, t in (("1", "a broad pedestal, which only locates"), ("2", "a steel screw, which holds"), ("3", "a brass insert melted into the other part")))
    body = (
        b.head("Fits · Pegs and bosses", "Never load a peg<br>across its layers.",
               "Each layer is welded to the one below, and that weld is the weakest thing in a print. A peg standing up off a plate "
               "joins it along one such weld. Push the peg sideways and that weld takes the whole load.", lede_size=54)
        + b.scope("PET-CF first: a faucet plate, May 2026, 0.6 mm nozzle · then PET-GF: a pump base, 2 November 2026, Mark 1",
                  not_tried="a PET-GF peg, broken on purpose")
        + b.row(
            ("0 0 640px", f'<figure style="background:var(--wash)">{_peg_svg("peg")}</figure>'
                          '<p class="cap"><span class="lab">May 2026 · a peg</span>Two pegs four millimetres across stood on the faucet&rsquo;s plate to press '
                          'into its shell. One snapped off on the first try.</p>'),
            ("0 0 640px", f'<figure style="background:var(--wash)">{_peg_svg("screw")}</figure>'
                          '<p class="cap"><span class="lab">June 2026 and since · a pedestal and a screw</span>The pedestal is short and wide, and '
                          'nothing pulls on it.</p>'),
            b.quote("they still don&rsquo;t fit, and they snap so easy because of the orientation of the layer lines. This is just not workable.",
                    "DEREK · MAY 2026 · AFTER THE SECOND TRY", size=44)
            + '<p class="small" style="margin:40px 0 0; font-size:34px"><b>The second try</b> made the pegs a tenth of a millimetre slimmer, as loose '
              'locating pins with nothing to hold. They snapped again. The fault was the direction of the layers, not the fit.</p>',
            gap=50, style="margin-top:30px")
        + f'<p class="tiny" style="margin:14px 0 0; font-size:30px; color:var(--text)">{legend}</p>'
        + b.rulebar(30, 30)
        + b.row(
            ("0 0 700px", b.fig(base, "A flat black printed base held in a hand, split open along a layer from one end",
                                "2 November 2026 · Mark 1 · PET-GF",
                                "The pump&rsquo;s test base, printed flat. Prying its cap off, the base let go before the snaps did. It opened "
                                "along a layer.", h=520, pos="50% 38%", zoom=125)),
            b.block("Which plastic", "The pegs were not PET-GF. The faucet was PET-CF that spring and its print log files them with its PET-CF "
                    "prints. The plate&rsquo;s own notes that week say &ldquo;PETG or PET-CF&rdquo;, and nothing names the spool.")
            + b.block("In PET-GF", "The photograph is the nearest we have. Derek asked for no change on account of it. The first round of snap "
                      "caps, printed with their leaves across the layers, is the other case, on the page before."),
            ("0 0 560px",
             '<div class="grid2" style="gap:30px">'
             + b.stat('27.9 <span>of 65.9</span>', "MPa. PET-CF across its layers, against along them.")
             + b.stat('48.2 <span>of 59.9</span>', "MPa. PET-GF, the same two figures.", hot=True)
             + "</div>"
             '<p class="tiny" style="margin:16px 0 0">The maker&rsquo;s own printed test bars, as noted in the faucet&rsquo;s print log on 24 August 2026, '
             'the day the faucet moved to PET-GF.</p>'),
            gap=50)
        + b.rulebar(30, 30)
        + b.row(
            ("0 0 520px", f'<figure style="background:var(--wash)"><img src="art/{plate}" alt="The faucet&rsquo;s mounting plate with three short pedestals, each bored for a screw" style="display:block; width:100%"></figure>'
                          '<p class="cap"><span class="lab">The plate today · PET-GF</span>Three pedestals, three screws.</p>'),
            b.block("What we do now", "A feature that will be pushed sideways or pulled is laid so that its roads run through the load, as a "
                    "snap&rsquo;s leaves are. Anything that has to stand up off a plate is kept short and broad and is only asked to locate. "
                    "A screw in a heat-set insert carries the joint."),
            ("0 0 640px", b.still_open("Nobody has broken a PET-GF peg on purpose. By the maker&rsquo;s figures PET-GF keeps four fifths of its "
                                       "strength across its layers and PET-CF less than half, so the rule may bind less hard here. Nothing in "
                                       "the record tests that.")),
            gap=50)
        + '<div style="margin-top:18px">' + b.record(
            b.link("The pegs, in the faucet&rsquo;s print log", f"{FAUCET}/faucet-shell/print-log.md"),
            b.link("The commit that removed them", "hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md", "d166c99b"),
            b.link("The base that split", f"{SNAP}/v2/physical-result/physical-result.json"),
            b.link("The plate today", f"{FAUCET}/above-counter-plate/README.md")) + "</div>"
    )
    return Page("never-load-a-peg-across-its-layers", "PET-GF fits: never load a peg across its layers", PART, body, right="Fits · 4 of 4")


def pages():
    return [allowances(), pockets(), snaps(), pegs()]
