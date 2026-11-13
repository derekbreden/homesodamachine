"""PET-GF supports: how the project learned to hold a part up with its own plastic and get that
plastic back out. Seven pages, each built on dated prints. Each function returns one Page."""
import bookkit as b
import svgkit as k
from bookkit import Page

T = "hardware/print-tests"
P = "hardware/printed-parts"
ROOFS = f"{T}/petgf-dense-roofs"
INCL = f"{ROOFS}/inclines/prints"
ENC = f"{P}/enclosure/enclosure"
RIGHT = "Supports"
SEEN = "PET-GF, support included"


def _petgf():
    return b.source("petgf", f"{P}/petgf.3mf", member="Metadata/project_settings.config")


# --------------------------------------------------------------------------- helpers this chapter adds
def _driver(tip_x, tip_y, deg, blade=150, shaft=120, handle=150):
    """A small flat screwdriver whose tip is at (tip_x, tip_y); deg turns it clockwise from
    lying with its handle to the right (180 = handle to the left)."""
    return (
        f'<g transform="translate({k.n(tip_x)} {k.n(tip_y)}) rotate({k.n(deg)})">'
        f'<path d="M0 0 L26 -9 L{blade} -9 L{blade} 9 L26 9 Z" fill="{k.INK}"/>'
        f'<rect x="{blade}" y="-6" width="{shaft}" height="12" fill="{k.INK}"/>'
        f'<rect x="{blade + shaft}" y="-25" width="{handle}" height="50" rx="20" fill="{k.WASH}" stroke="{k.INK}" stroke-width="5"/>'
        "</g>"
    )


def _tag(x, y, text, fill=k.INK, size=27, anchor="start"):
    return k.label(x, y, text, size, anchor=anchor, fill=fill, weight=600)


def _lead(x0, y0, x1, y1, color=k.INK):
    """A leader from a label to the thing it names."""
    return k.line(x0, y0, x1, y1, color, 3) + f'<circle cx="{k.n(x1)}" cy="{k.n(y1)}" r="6" fill="{color}"/>'


def _dashes(x0, x1, y, fill=k.SCAFFOLD, gap=34.0, h=k.ROW_H):
    """One course of an open support roof: roads with air between them."""
    bh = h - 3
    return (f'<path d="M{k.n(x0 + 1.5 + bh / 2)} {k.n(y + h / 2)}H{k.n(x1 - 1.5 - bh / 2)}" fill="none" stroke="{fill}" stroke-width="{k.n(bh)}" '
            f'stroke-linecap="round" stroke-dasharray="{k.n(k.BEAD_W - 3 - bh)} {k.n(gap + 3 + bh)}"/>')


def _tree(cx, foot_y, fork_y, top_y, spread=46, trunk=17, limb=12):
    """One short tree: a trunk from foot_y up to fork_y and two limbs up to top_y."""
    return (k.road(f"M{k.n(cx)} {k.n(foot_y)} L{k.n(cx)} {k.n(fork_y)}", k.SCAFFOLD, trunk)
            + k.road(f"M{k.n(cx)} {k.n(fork_y)} L{k.n(cx - spread)} {k.n(top_y)}", k.SCAFFOLD, limb)
            + k.road(f"M{k.n(cx)} {k.n(fork_y)} L{k.n(cx + spread)} {k.n(top_y)}", k.SCAFFOLD, limb))


def _legend(items, cols=3, gap=44, size=33, row_gap=20):
    """Numbered notes under a drawing or photograph: (number, kind, text)."""
    out = []
    for num, kind, text in items:
        out.append(
            f'<div style="display:flex; gap:20px; align-items:flex-start"><span class="num {kind}">{num}</span>'
            f'<p class="tiny" style="margin:7px 0 0; font-size:{size}px; color:var(--text)">{text}</p></div>'
        )
    return f'<div style="display:grid; grid-template-columns:repeat({cols}, 1fr); gap:{row_gap}px {gap}px">{"".join(out)}</div>'


def _marked_photo(name, alt, src, box, pos=(50, 50), zoom=100, marks=(), lab="", cap=""):
    """A photograph cropped into a box (w, h) with numbered discs on it. src is the copied
    picture's size in pixels; marks are (number, u, v, kind) with u, v as fractions of the picture."""
    sw, sh = src
    w, h = box
    bw = w * zoom / 100.0
    bh = bw * sh / sw
    ox, oy = (w - bw) * pos[0] / 100.0, (h - bh) * pos[1] / 100.0
    discs = "".join(f'<span class="num on-model {kind}" style="left:{ox + u * bw:.0f}px; top:{oy + v * bh:.0f}px">{num}</span>'
                    for num, u, v, kind in marks)
    labs = f'<span class="lab">{lab}</span>' if lab else ""
    caps = f'<figcaption class="cap">{labs}{cap}</figcaption>' if (lab or cap) else ""
    return (f'<figure style="width:{w}px"><div role="img" aria-label="{alt}" style="position:relative; width:{w}px; height:{h}px; '
            f'background:url(art/{name}) {pos[0]}% {pos[1]}% / {zoom}% auto no-repeat">{discs}</div>{caps}</figure>')


def _p(text, last=False, cls="small"):
    return f'<p class="{cls}"' + (' style="margin:0"' if last else "") + f">{text}</p>"


# --------------------------------------------------------------------------- 1 blocks in a cavity
def _hook(x0, bed, body=6, cav=10, head=4, cav_w=8, wall_w=4):
    """The part every cavity drawing uses: a body, a wall behind a cavity, and a head that overhangs
    it. x0 is the cavity's mouth. Returns the drawing, the floor's y and the roof's y."""
    xb, x1 = x0 + cav_w * k.BEAD_W, x0 + (cav_w + wall_w) * k.BEAD_W
    floor, roof = k.row_y(body - 1, bed), k.row_y(body + cav - 1, bed)
    g = (k.block(x0, x1, 0, body - 1, bed) + k.block(xb, x1, body, body + cav - 1, bed)
         + k.block(x0 - k.BEAD_W, x1, body + cav, body + cav + head - 1, bed)
         + k.line(x0 - k.BEAD_W + 4, roof - 1, xb - 2, roof - 1, k.HOT, 9))
    return g, floor, roof


def _cavity_drawing():
    W, BED, G, PITCH = 2170, 496, 35, 1050
    H = BED + 64

    def x(p, c):
        return G + p * PITCH + c * k.BEAD_W

    s = [k.bed(8, W - 8, BED)]
    for p in range(2):
        g, floor, roof = _hook(x(p, 12), BED, body=5)
        s.append(g)

    # what we had: a block
    s.append(k.scaffold(x(0, 12) + 5, x(0, 20) - 5, roof + 9, floor - 1))
    s.append(f'<rect x="{k.n(x(0, 16) - 72)}" y="{k.n(roof + 92)}" width="144" height="48" fill="white"/>')
    s.append(k.label(x(0, 16), roof + 126, "BLOCK", anchor="middle", fill=k.INK, weight=600))
    s.append(_driver(x(0, 12) - 1, roof + 150, 168))
    s.append(k.callout(1, x(0, 13) + 10, roof + 46, x(0, 8), roof + 6, "bad"))
    s.append(k.callout(2, x(0, 12) - 5, roof + 152, x(0, 9), roof + 288, "bad"))
    s.append(k.label(x(0, 10) + 14, 80, "THE FACE TO BE HELD UP", 25, anchor="end", fill=k.HOT, weight=600))
    s.append(k.line(x(0, 10) + 24, 74, x(0, 12) - 8, roof - 8, k.HOT, 4))

    # what works: short trees on the cavity's own floor
    for c in (13, 15.5, 18):
        s.append(_tree(x(1, c) + 21, floor - 6, k.row_y(9, BED), roof + 40))
    s.append(k.course(x(1, 12) + 8, x(1, 20) - 14, roof + 9, k.SCAFFOLD, 22))
    s.append(_driver(x(1, 12) + 30, roof + 50, 166))
    s.append(k.arrow(x(1, 11), roof + 200, x(1, 7), roof + 200, k.INK, 5))
    s.append(k.label(x(1, 7) - 16, roof + 209, "OUT WHOLE", 25, anchor="end", fill=k.INK))
    s.append(k.callout(3, x(1, 13) + 21, floor - 40, x(1, 9), floor + 62))
    s.append(k.callout(4, x(1, 10), roof + 86, x(1, 8) + 20, roof - 26))

    for p, (t, c) in enumerate([("WHAT WE HAD", k.BAD), ("WHAT WORKS", k.INK)]):
        s.append(_tag(x(p, 0), 30, t, c))
    s.append(k.label(x(0, 0), BED + 56, "THE BED"))
    return k.svg(W, H, "".join(s), "A block of support wedged in a cavity, beside a short tree that levers out",
                 "Two sections through the same wall, which has a cavity in its side. On the left the cavity is filled by a block of "
                 "support that touches its floor, back wall and roof, and a screwdriver stops at its face. On the right short trees "
                 "stand on the cavity's own floor under a thin roof, and a screwdriver levers them out through the open side.")


def blocks():
    _petgf()
    b.source("front", f"{ENC}/prints/2026-11-11-front-bottom-D-mark2/support-audit-1901.json")
    notes = _legend([
        (1, "", "It fills the cavity and touches the floor, the back wall and the roof at once."),
        (3, "", "It stands on the floor of the same cavity, so it is short, and it meets the part only at a thin roof."),
        (2, "", "A blade cannot get behind it, and it is too big to turn."),
        (4, "", "A small flat screwdriver goes in at the open side and levers the whole tree out."),
    ], cols=2, gap=70)
    story = (
        "<h2>Two full-size prints lost in a week</h2>"
        + _p("<b>3 October 2026, Mark 1.</b> Front-top, nearly 26 hours. Tall blocks, which the slicer calls normal supports, had fused with "
             "the trees beside them into masses bigger than the cavities they had to leave through. A cover holder buried in one snapped. "
             "Rejected the next day.")
        + _p("<b>8 October 2026, Mark 1.</b> Back-top, 27 hours. Every support had been switched to blocks, to keep the print inside the "
             "margin we hold at the plate&rsquo;s edge. Thrown away the next day.")
        + _p("<b>10 October 2026, Mark 1.</b> Back-top again, on trees. For one groove they came up from far below, long and thin, and "
             "stuck in the walls on the way.", last=True)
    )
    now = (
        "<h2>What we do now</h2>"
        + _p(f'The shared recipe asks for <b>{b.setting("petgf", "/support_type")}</b>. No cavity gets a rectangular support, whether a '
             "person asked for it or the slicer chose it. On 6 November 2026 Derek made it flat: &ldquo;So we can&rsquo;t have normal "
             "supports and cavities.&rdquo;")
        + _p("A tree has to start in the cavity it serves, and allowing that does not make the slicer do it, so we read each start in the "
             f'sliced file. In the front-bottom sent to print on 11 November 2026, {b.setting("front", "/summary/model_rooted_bodies")} of '
             f'{b.setting("front", "/summary/support_bodies")} supports start inside their cavity, '
             f'{b.setting("front", "/summary/shortest_build_up_mm")} mm under the face they carry.', last=True)
    )
    body = (
        b.head("Supports · Inside a cavity", "Support blocks do not come out of a cavity.",
               "Where a part hangs over air, the slicer prints scaffold under it. In PET-GF that scaffold is the part&rsquo;s own plastic, "
               "from the same nozzle, and nothing dissolves it. It must be levered out, and a block that fills a cavity leaves a tool "
               "nowhere to go.", size=160, lede_size=52)
        + b.scope(f"{SEEN} · Mark 1 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + f'<div style="margin-top:34px">{_cavity_drawing()}</div>'
        + f'<div style="margin-top:16px">{notes}</div>'
        + b.rulebar(36, 36)
        + b.row(
            ("0 0 1050px", story),
            b.quote("lol, lmfao, it is *every* support here ... yeah, there&rsquo;s no way I&rsquo;m going to be able to do anything with this "
                    "except throw it away", "DEREK · 9 OCTOBER 2026, ON THE SECOND PRINT", size=46)
            + '<div style="margin-top:44px">'
            + b.quote("&quot;Auto&quot; is fine ... I&rsquo;ve yet to see bambu&rsquo;s auto put a normal support in an impossible to remove place ... "
                      "it&rsquo;s when you choose to put normal somewhere that it introduces problems.", "DEREK · THE SAME DAY", size=40)
            + "</div>",
            gap=70)
        + b.rulebar(36, 32)
        + b.row(
            ("0 0 1050px", now),
            b.record(b.link("Front-top, rejected 4 October", f"{P}/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json"),
                     b.link("Back-top, thrown away 9 October", f"{P}/drain-readiness/prints/2026-10-08-current-back-top-mark1/physical-result.json"),
                     b.link("Back-top, the long trees", f"{P}/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json"),
                     b.link("Where the rail trees start", f"{ENC}/front-rail-support-review.json"),
                     b.link("The rule as agents read it", f"{P}/AGENTS.md", anchor="supports"))
            + b.still_open("Nobody has measured how open a cavity must be before a block will come out of it. In the back-top printed on "
                           "5 November 2026, blocks in an open rail groove did come out, once the screwdriver found its angle. The rule "
                           "stayed."),
            gap=70)
    )
    return Page("support-blocks-do-not-come-out", "PET-GF supports: blocks do not come out of a cavity", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 2 the gap
def _disc(num, x, y, tx, ty, fill=k.INK, r=20):
    """A small numbered disc at (tx, ty) with a leader to (x, y), for drawings shown enlarged."""
    return (k.line(tx, ty, x, y, k.INK, 2) + f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="5" fill="{k.INK}"/>'
            + f'<circle cx="{k.n(tx)}" cy="{k.n(ty)}" r="{r}" fill="{fill}"/>'
            + f'<text x="{k.n(tx)}" y="{k.n(ty + 7)}" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="21" font-weight="600" fill="white">{num}</text>')


def _gap_panel(air):
    """One section through a supported roof with `air` layers of gap, drawn to be shown enlarged."""
    W, BED, X0 = 700, 414, 104
    H = BED + 4

    def x(c):
        return X0 + c * k.BEAD_W

    def y(r):
        return k.row_y(r, BED)

    top = 9 - air                                       # the upper course of the support's roof
    s = [k.block(x(0), x(3), 0, 9, BED) + k.block(x(11), x(14), 0, 9, BED),
         k.block(x(0), x(3), 10, 10, BED, "hot") + k.strand(x(3), x(11), y(10)) + k.block(x(11), x(14), 10, 10, BED, "hot"),
         k.block(x(0), x(14), 11, 13, BED),
         k.scaffold(x(4), x(10), y(top - 2), BED),
         _dashes(x(4) - 21, x(10) + 21, y(top - 1)) + _dashes(x(4) + 17, x(10) + 21, y(top))]
    marks = [(1, y(12) + 12, k.INK), (2, y(10) + 12, k.HOT), (3, (y(9) + y(top)) / 2, k.INK), (4, y(top - 1), k.SCAFFOLD), (5, y(2), k.SCAFFOLD)]
    for i, (num, ty, fill) in enumerate(marks):
        s.append(_disc(num, x(6) + 21 if num != 3 else x(8), ty, 40, 112 + i * 62, fill))
    s.append(k.label(0, 26, "ONE LAYER OF AIR" if air == 1 else "TWO LAYERS OF AIR", 21, fill=k.BAD if air == 1 else k.INK, weight=600))
    s.append(k.label(0, 56, "ASKED FOR 0.30 MM. THE FILE HAD 0.24." if air == 1 else "ASKED FOR 0.45 MM. THE FILE HAD 0.48.", 17))
    return k.svg(W, H, "".join(s), f"The gap between a support and the part, {'one layer' if air == 1 else 'two layers'} of air tall",
                 "A section through a roof that spans between two walls. Under the roof stands a support: a tree, then two open "
                 "courses that make the support's roof, then air, then the first course of the part, which crosses from wall to wall "
                 "like a bridge.")


def _plate_map():
    W, H = 1000, 890
    spec = {1: (2, 1, 1, "t"), 2: (2, 1, 0, "t"), 3: (1, 1, 0, ""), 4: (1, 0, 0, ""),
            5: (1, 1, 1, ""), 6: (1, 0, 1, ""), 7: (2, 0, 0, "t"), 8: (2, 0, 1, "3"),
            9: (2, 0, 1, "t"), 10: (2, 0, 0, "1"), 11: (1, 0, 0, ""), 12: (2, 1, 1, "t"),
            13: (1, 0, 1, ""), 14: (1, 1, 1, ""), 15: (1, 1, 0, ""), 16: (2, 1, 0, "2")}
    s = []
    for i in range(16):
        air, wall, free, mark = spec[i + 1]
        cx, cy = 150 + (i % 4) * 236, 96 + (3 - i // 4) * 200
        iw, jf = (30 if wall else 9), (26 if free else 0)
        s.append(k.scaffold(cx - 60 + iw, cx + 60 - iw, cy - 60 + iw, cy + 60 - jf))
        s.append(f'<path d="M{cx - 66} {cy + 60} V{cy - 66} H{cx + 66} V{cy + 60}" fill="none" stroke="{k.COLD}" stroke-width="12" stroke-linejoin="round"/>')
        s.append(k.label(cx, cy + 98, f"{i + 1:02d} · {'ONE' if air == 1 else 'TWO'}", 25, anchor="middle",
                         fill=k.INK if air == 2 else k.MUTED, weight=600 if air == 2 else 400))
        if mark:
            s.append(f'<circle cx="{cx + 66}" cy="{cy - 66}" r="27" fill="{k.GOOD}" stroke="white" stroke-width="5"/>')
            if mark == "t":
                s.append(f'<path d="M{cx + 54} {cy - 66} l9 10 l16 -20" fill="none" stroke="white" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
            else:
                s.append(f'<text x="{cx + 66}" y="{cy - 56}" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-size="29" font-weight="600" fill="white">{mark}</text>')
    s.append(k.label(W / 2, H - 12, "FRONT OF THE BED · EACH COUPON&rsquo;S OPEN SIDE FACES IT", 25, anchor="middle"))
    return k.svg(W, H, "".join(s), "Sixteen coupons on one plate, marked by which released cleanly",
                 "A plan of the plate with sixteen numbered coupons in four rows. Each is a square roof on three walls, open toward the "
                 "front, with the footprint of its support's roof hatched inside. On some the hatching is pulled back from the walls, on "
                 "some from the open edge, on some from both. Eight coupons carry a green mark for a clean release. All eight are ones "
                 "with two layers of air, and their edge treatments differ.")


def gap():
    b.source("fits", "tools/hsm/shared-data/catalog/scalars.json")
    edges = f"{T}/petgf-interface-edges"
    panels = (
        '<div class="grid2" style="gap:90px; margin-top:34px">'
        f"<div>{_gap_panel(1)}"
        + b.stat('0 <span>of 8</span>', "coupons with one layer of air made Derek&rsquo;s group of cleanest releases.")
        + f"</div><div>{_gap_panel(2)}"
        + b.stat('8 <span>of 8</span>', "with two layers did. The support came away and the roof&rsquo;s own strands stayed on the roof.", hot=True)
        + "</div></div>"
    )
    names = _legend([(1, "", "The part."), (2, "hot", "Its first course, pulled from wall to wall like a bridge."), (3, "", "Air."),
                     (4, "scaffold", "The support&rsquo;s roof: two courses of spaced lines."), (5, "scaffold", "A tree.")],
                    cols=5, gap=30, size=31)
    right = (
        "<h2>The edges changed nothing</h2>"
        + _p("The first reports had the support sticking at its edges. So twelve of the sixteen had the support&rsquo;s roof pulled back "
             "0.6 mm from the walls, from the open edge, or from both. The clean ones are the two-layer ones, whatever was done at their "
             "edges. Derek&rsquo;s best three used three different edge treatments. The best of all had none.")
        + "<h2>What stayed stuck was the part</h2>"
        + _p("A second plate that afternoon had four coupons: a crossed roof, straight lines, straight lines cut apart at their ends, and "
             "no roof at all, only the tips of the trees. The same strands stayed under all four. Under the one with no roof there was "
             "nothing else they could be. In the sliced file they are the part&rsquo;s own first course.")
        + "<h2>What the gap costs</h2>"
        + _p("Even where the support let go, that first course hung loose. On all eight clean coupons it looked and felt loose beside the "
             "course above it. A face printed over support is rougher and lower than it was drawn, so every fit beside one is given "
             f'{b.setting("fits", "/fits/supported_surface")} mm more room. The pages on fits show where that goes.', last=True)
    )
    body = (
        b.head("Supports · The gap", "One layer of air held on. Two let go.",
               "A support does not touch the part. The slicer leaves a little air between the support&rsquo;s roof and the first course of "
               "the part, so that the two can be pulled apart, and that first course is laid across the air like a bridge. How much air "
               "is the whole question.", size=160, lede_size=52)
        + b.scope(f"{SEEN} · Mark2 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + panels
        + f'<div style="margin-top:22px">{names}</div>'
        + b.rulebar(34, 34)
        + b.row(
            ("0 0 820px", f'<figure>{_plate_map()}<figcaption class="cap"><span class="lab">15 September 2026 · Mark2 · PET-GF</span>'
                          "Sixteen small ceilings on one plate, seen from above. Eight asked the slicer for 0.30 mm of air and eight for "
                          "0.45 mm. The trees we print with count the gap in whole layers. Hatching is the support&rsquo;s roof. Green "
                          "marks Derek&rsquo;s cleanest eight, with 1, 2 and 3 for his best.</figcaption></figure>"),
            right, gap=70)
        + '<div style="margin-top:26px">'
        + b.record(b.link("The sixteen coupons and their ranking", f"{edges}/results.json"),
                   b.link("How they were made", f"{edges}/README.md"),
                   b.link("The four coupons and the strands", f"{T}/petgf-interface-patterns/results.json"),
                   b.link("The allowance", "tools/hsm/shared-data/catalog/scalars.json"))
        + "</div>"
        + b.still_open("Nobody measured how far the loose strands hang. The allowance is Derek&rsquo;s judgement from coupons in his hand, set "
                       "before Support D closed the gap again. On 10 November 2026 a rail printed with D fitted &ldquo;a little bit loose&rdquo;.")
    )
    return Page("one-layer-of-air-held-on", "PET-GF supports: one layer of air held on, two let go", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 3 the support that fell off
def fell_off():
    coupon = f"{P}/faucet/finish-coupons/2026-10-10"
    slit = b.asset("petgf-supports-faucet-slit.jpg", f"{coupon}/physical-result/in-progress-photo-2.jpg")
    roofs = b.asset("petgf-supports-roof-strands.jpg", f"{ROOFS}/photos/02-roof-undersides.jpg")
    top = b.row(
        ("0 0 1290px", _marked_photo(
            slit, "A black faucet base section standing on tree supports, with a dark slit running along it just above the supports",
            (1280, 960), (1290, 790), pos=(50, 34),
            marks=[(1, 0.50, 0.32, ""), (2, 0.30, 0.478, "hot"), (3, 0.62, 0.63, "scaffold")],
            lab="10 October 2026 · Mark2 · PET-GF",
            cap="A section of the faucet&rsquo;s base, still on the plate. <b>1</b> The part. <b>2</b> A slit where the part should be joined "
                "to itself. <b>3</b> The trees and the roof they carry. All three copies on the plate had the slit.")),
        '<p class="small">These supports had the gap that won in September. Derek had been calling the slit lifting. Then he saw what '
        "it was.</p>"
        + b.quote("In these faucet base prints, at that &quot;lifting&quot; area, the first layer just falls off, it is not connected to the "
                  "layers above it all. So this lifting is actually &quot;perfect removal&quot; for the removal I was initially seeking, "
                  "before I realized that was removing the first layer.", "DEREK · 11 OCTOBER 2026", size=45)
        + '<p class="small" style="margin:34px 0 0">The layers in that band were fine ones, which is trouble of its own and has its own '
          "page. The lesson here is about the judging. For a month, easy removal had been the thing we were looking for.</p>",
        gap=70, style="margin-top:34px")
    second = b.row(
        ("0 0 560px", b.fig(roofs, "Three small black roofs held in a hand, their undersides rows of separate strands",
                            "9 November 2026 · Mark 1 · PET-GF", "The undersides of A, B and C.", h=620, pos="64% 8%", zoom=112)),
        "<h2>Three ceilings that let go by themselves</h2>"
        + _p("Three small ceilings, A, B and C, each on a denser support roof than the last, all with two layers of air. Nobody removed "
             "their supports.")
        + b.quote("Like as soon as the plate cooled a little bit, the prints just detached. They just slid off. There was no removal of the "
                  "supports.", "DEREK · 9 NOVEMBER 2026", size=42)
        + '<p class="small" style="margin:30px 0 26px">Removal cannot get easier than that. The roofs they left are in the photograph: '
          "separate strands, some standing proud. None was acceptable. What he asked for next was the opposite of easy.</p>"
        + b.quote("Give me three samples of some things that will perhaps be more difficult to remove, but also potentially support our "
                  "first layer a lot better.", "DEREK · THE SAME EVENING", size=42),
        gap=70)
    body = (
        b.head("Supports · Judging a result", "The support that fell off was the failure.",
               "A support has two jobs that pull against each other. It has to hold up the first course of the part while that course is "
               "soft, and afterwards it has to let go. One that lets go with no effort at all has usually skipped the first job.",
               size=160, lede_size=52)
        + b.scope(f"{SEEN} · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + top
        + b.rulebar(34, 34)
        + second
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 1150px", "<h2>What we judge now</h2>"
             + _p("The removed support is kept beside its part, and the underside it left is looked at first. Are the first roads joined to "
                  "each other and to the course above, or do they lie there as separate strands? Only then does it matter how the support "
                  "came away. One that drops off by itself is marked down.", last=True)),
            b.record(b.link("The faucet coupon", f"{coupon}/physical-result/physical-result.json"),
                     b.link("The three ceilings", f"{ROOFS}/physical-result.json"),
                     b.link("What to look at, as written for the bench", f"{ROOFS}/README.md"))
            + b.still_open("All of this is judged by eye and by hand. No coupon in this chapter has a measured sag, roof thickness or "
                           "pulling force."),
            gap=70)
    )
    return Page("the-support-that-fell-off", "PET-GF supports: the support that fell off was the failure", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 4 Support D
def _bead_trap():
    W, H, BASE = 700, 290, 216
    s = []
    for i, (x0, tall, title, left) in enumerate([(30, 24, "A PLAIN COURSE", "0.24"), (390, 30, "A BRIDGE AT THIS FLOW", "0.18")]):
        x1 = x0 + 6 * k.BEAD_W
        for r in range(3):
            s.append(k.course(x0, x1, BASE - (r + 1) * 24, k.SCAFFOLD))
        roof = BASE - 72
        first = roof - 48                                # the top of the part's first course
        s.append(k.strand(x0, x1, first, k.HOT, tall))
        s.append(k.line(x0 - 14, roof, x1 + 14, roof, k.FAINT, 2, "6 6") + k.line(x0 - 14, first + 24, x1 + 14, first + 24, k.FAINT, 2, "6 6"))
        s.append(k.label((x0 + x1) / 2, 28, title, 23, anchor="middle", fill=k.INK, weight=600))
        s.append(k.label((x0 + x1) / 2, 60, "0.24 MM TALL" if i == 0 else "0.30 MM TALL", 23, anchor="middle", fill=k.HOT, weight=600))
        s.append(k.label((x0 + x1) / 2, BASE + 44, f"LEAVES {left} MM OF AIR", 23, anchor="middle", fill=k.BAD if i else k.INK, weight=600))
    return k.svg(W, H, "".join(s), "The same gap under a plain course and under a fat bridge bead",
                 "Two small sections. In each, three solid courses make a support's roof, with the part's first course above them. On "
                 "the left that course is as tall as its layer and leaves the gap that was asked for. On the right it is a bridge laid "
                 "with extra flow, taller than its layer, and it hangs down into the gap.")


def support_d():
    _petgf()
    mats = b.asset("petgf-supports-mats-on-bed.jpg", f"{ROOFS}/photos/01-separated-supports.jpg")
    ceil = b.asset("petgf-supports-de-ceilings.jpg", f"{ROOFS}/close-contact/photos/01-D-E-undersides.jpg")
    rail_d = b.asset("petgf-supports-rail-d-one-piece.jpg", f"{ROOFS}/rail-fit-30/photos/01-whole-support-release.jpg")
    rail_e = b.asset("petgf-supports-rail-e-corner.jpg", f"{ROOFS}/rail-cavity-30-E/photos/02-pale-roughened-corner.jpg")
    cands = [("A", "0.5 mm apart", "2", "0.45 mm"), ("B", "0.15 mm apart", "2", "0.45 mm"), ("C", "touching", "2", "0.45 mm"),
             ("D", "touching", "3", "0.24 mm"), ("E", "touching", "3", "0.12 mm"), ("F", "touching", "3", "0.06 mm")]
    cells = "".join(
        f'<div><p style="margin:0; font:700 92px/1 \'IBM Plex Sans\'; color:{"var(--hot)" if letter == "D" else "var(--ink)"}">{letter}</p>'
        f'<p class="tiny" style="margin:10px 0 0; font-size:30px; line-height:1.4; color:var(--text)">roof lines <b>{space}</b><br>'
        f'<b>{layers}</b> roof layers<br><b>{asked}</b> of air asked</p></div>'
        for letter, space, layers, asked in cands)

    def shot(span, name, alt, pos, zoom):
        return (f'<div role="img" aria-label="{alt}" style="grid-column:span {span}; height:260px; '
                f'background:url(art/{name}) {pos} / {zoom}% auto no-repeat"></div>')

    def verdict(span, cls, tag, text):
        return (f'<p class="tiny" style="grid-column:span {span}; margin:0; font-size:31px; color:var(--text)">'
                f'<span class="tag {cls}" style="margin-right:14px">{tag}</span>{text}</p>')

    board = (
        '<div style="display:grid; grid-template-columns:repeat(6, 1fr); gap:18px 30px; margin-top:30px">'
        + cells
        + shot(3, mats, "Three small squares of support left standing on the print bed, the first an open mesh, the last a solid sheet", "40% 55%", 100)
        + shot(2, ceil, "Two small ceilings side by side with even, close-packed undersides", "50% 55%", 100)
        + '<div style="height:260px; background:var(--wash); display:flex; align-items:center; justify-content:center">'
          '<p class="mono" style="margin:0; font-size:25px; letter-spacing:.08em; color:var(--faint); text-align:center">NO<br>PHOTOGRAPH</p></div>'
        + verdict(3, "bad", "Fell off", "All three slid off their supports as the plate cooled and left roofs of separate strands. These "
                  "are the supports, still on the bed. Which is which was not recorded.")
        + verdict(2, "good", "Let go by hand", "&ldquo;D and E both removed without pulling the first layer with them.&rdquo; Which is "
                  "which was not recorded.")
        + verdict(1, "open", "No result", "Printed. Never reported.")
        + "</div>"
    )
    rail = b.row(
        ("0 0 540px", b.fig(rail_e, "The corner of a small black rail cavity with a pale, roughened strip along its edge",
                            "E · 9 November 2026 · Mark 1",
                            "Harder to get out than rail supports usually are. It broke up, a tree or two at a time, and one corner "
                            "had fused pale.", h=450, pos="34% 56%", zoom=160)),
        ("0 0 640px", b.fig(rail_d, "A comb of support, a flat roof with a row of short trunks, held beside the small rail piece it came out of",
                            "D · 10 November 2026 · Mark 1",
                            "The roof and its trees, out as one comb. The mating rail then slid in with room to spare.",
                            h=450, pos="50% 26%", zoom=112)),
        "<h2>Then the real cavity</h2>"
        + _p("A ceiling between three walls is kind to a support. D came clean off four less sheltered shapes the same evening. Then E and "
             "D were each printed as the front-bottom&rsquo;s own rail cavity, on its short trees.")
        + b.quote("This support, this D support on this rail cavity removed perfectly. It was great. It came off as a single piece and it "
                  "pried out just as easily as the others.", "DEREK · 10 NOVEMBER 2026", size=41)
        + '<p class="small" style="margin:26px 0 0">He had put E&rsquo;s breaking up down to its denser roof. D has the same roof.</p>',
        gap=44)
    recipe = b.table([
        ("Support", b.setting("petgf", "/support_type")),
        ("Space between roof lines", b.setting("petgf", "/support_interface_spacing") + " mm"),
        ("Roof layers", b.setting("petgf", "/support_interface_top_layers")),
        ("Air asked for", b.setting("petgf", "/support_top_z_distance") + " mm"),
        ("Bridges", b.setting("petgf", "/bridge_flow") + " of normal flow, " + b.setting("petgf", "/bridge_speed/0") + " mm/s"),
    ])
    trap = (
        "<h2>Asked for is not printed</h2>"
        f'<div style="margin:10px 0 12px">{_bead_trap()}</div>'
        + _p("A bridge at D&rsquo;s flow is a fatter bead than its layer, and it hangs lower. In D&rsquo;s file the 0.24 mm asked for left "
             "0.18. E&rsquo;s 0.12 left 0.06 on the ceiling. On the rail the trees rounded E a whole layer closer, and its bead sat inside "
             "the roof. Read the gap in the sliced file.", last=True, cls="tiny")
    )
    body = (
        b.head("Supports · Support D", "Solid roof, small gap, out in one piece.",
               "On the evening of 9 November 2026 Mark 1 printed six small ceilings, lettered A to F. Three kept the wide gap and made the "
               "support&rsquo;s roof denser. Three made the roof solid and closed the gap up. Every PET-GF part now prints with the fourth.",
               size=160, lede_size=50)
        + b.scope(f"{SEEN} · Mark 1 · textured PEI · left 0.4 mm · flat ceilings a tool can reach", not_tried="any other plastic")
        + board
        + b.rulebar(28, 28)
        + rail
        + b.rulebar(28, 26)
        + b.row(
            ("0 0 560px", '<h2>Support D today</h2>' + recipe),
            ("0 0 700px", trap),
            b.record(b.link("A, B and C", f"{ROOFS}/physical-result.json"),
                     b.link("D, E and F: the file read back", f"{ROOFS}/close-contact/verification.json"),
                     b.link("D on the rail", f"{ROOFS}/rail-fit-30/physical-result.json"),
                     b.link("E on the rail", f"{ROOFS}/rail-cavity-30-E/physical-result.json"),
                     b.link("Where D is applied", f"{P}/support-D-rollout.json"))
            + b.still_open("D is not one change. From C to D the gap, the roof&rsquo;s layers, the bridge flow, the bridge speed, the tree "
                           "style and the coupon itself all changed, and nothing has separated them. No full-size enclosure piece printed "
                           "with D has a recorded result yet."),
            gap=50)
    )
    return Page("solid-roof-small-gap", "PET-GF supports: Support D, a solid roof and a small gap", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 5 the way out
def _way_out_drawing():
    W, BED, G, PITCH = 2170, 456, 14, 714
    H = BED + 76

    def x(p, c):
        return G + p * PITCH + c * k.BEAD_W

    def y(r):
        return k.row_y(r, BED)

    s = [k.bed(6, W - 6, BED)]
    for p in range(2):                                    # the same pocket twice
        g, floor, roof = _hook(x(p, 7), BED, body=5, cav=8, head=3, cav_w=5, wall_w=3)
        s.append(g)
        s.append(_tree(x(p, 8) + 26, floor - 6, y(8), roof + 40, spread=40) + _tree(x(p, 10) + 40, floor - 6, y(8), roof + 40, spread=40))
        s.append(k.course(x(p, 7) + 8, x(p, 12) - 14, roof + 9, k.SCAFFOLD, 22))
    # on the test piece: five things the easy supports had
    tx, ty = x(0, 7) + 26, roof + 50
    s.append(_driver(tx, ty, 164, blade=120, shaft=60, handle=100))
    s.append(k.arrow(x(0, 6) + 20, floor - 30, x(0, 3) + 10, floor - 30, k.INK, 5))
    s.append(k.callout(1, tx - 200, ty + 58, tx - 226, ty - 30))
    s.append(k.callout(2, x(0, 10) + 40, y(7), x(0, 16), y(7)))
    s.append(k.callout(3, x(0, 8) + 26, floor - 50, x(0, 5), floor + 58))
    s.append(k.callout(4, x(0, 2) - 6, floor - 30))
    s.append(k.callout(5, x(0, 11), roof + 20, x(0, 16), roof + 20))
    # in the whole part: its own wall stands in front of the pocket
    s.append(k.block(x(1, 2), x(1, 5), 0, 15, BED) + k.block(x(1, 5), x(1, 7), 0, 1, BED))
    s.append(_driver(x(1, 5) + 21, floor - 50, 270, blade=110, shaft=60, handle=90))
    s.append(k.callout(6, x(1, 2) + 8, y(8), x(1, 1) - 6, y(8), "bad"))
    # what prints there now: a bar bridged between two shoulders
    q, bw = x(2, 2), k.BEAD_W
    s.append(k.block(q, q + 12 * bw, 0, 4, BED) + k.block(q, q + 3 * bw, 5, 11, BED) + k.block(q + 9 * bw, q + 12 * bw, 5, 11, BED))
    s.append(k.block(q, q + 3 * bw, 12, 12, BED, "hot") + k.strand(q + 3 * bw, q + 9 * bw, y(12)) + k.block(q + 9 * bw, q + 12 * bw, 12, 12, BED, "hot"))
    s.append(k.block(q, q + 12 * bw, 13, 15, BED))
    s.append(k.callout(7, q + 6 * bw, y(12) + 18, q + 6 * bw, y(10) + 4, "hot"))
    s.append(k.label(q + 6 * bw, y(7) + 6, "NOTHING", 25, anchor="middle", fill=k.FAINT) + k.label(q + 6 * bw, y(6) + 14, "TO REMOVE", 25, anchor="middle", fill=k.FAINT))
    for p, (t, c) in enumerate([("ON THE TEST PIECE", k.INK), ("IN THE WHOLE PART", k.BAD), ("WHAT PRINTS THERE NOW", k.INK)]):
        s.append(_tag(x(p, 2), BED + 62, t, c))
    return k.svg(W, H, "".join(s), "The same supported pocket on a test piece, inside the whole part, and redrawn to need no support",
                 "Three sections. In the first a pocket on a small test piece holds short trees under a thin roof, and a screwdriver "
                 "reaches in from the open side. In the second the same pocket sits behind a tall wall of the whole part, and the "
                 "screwdriver coming down beside that wall cannot turn into it. In the third the pocket's roof is a bar pulled across "
                 "between two full shoulders, with nothing printed under it.")


def way_out():
    snap = f"{T}/rear-snap-retention/physical-result"
    hand = b.asset("petgf-supports-coupon-in-hand.jpg", f"{snap}/asse-fit.jpg")
    needs = _legend([
        (1, "", "<b>A way in for a tool.</b> A small flat screwdriver, and room to swing it."),
        (2, "", "<b>A tree, not a block.</b> Thin where it meets the part."),
        (3, "", "<b>A root inside the cavity.</b> A tree from far below arrives long, thin and stuck to the wall."),
        (4, "", "<b>An open lane.</b> One side of the cavity stays open until the support is out."),
        (5, "", "<b>One piece.</b> A roof that ties the trees together, so the first pry brings all of them."),
        (6, "bad", "<b>The whole part&rsquo;s own walls.</b> The pocket is the same. The way to it is gone."),
        (7, "hot", "<b>A bridge instead.</b> Two full shoulders, a bar pulled across, nothing underneath."),
    ], cols=4, gap=40, size=31, row_gap=18)
    left = (
        "<h2>Easy on the test piece</h2>"
        + _p("<b>1 November 2026, both printers.</b> Ten test pieces for the rear fittings, each small enough to hold in one hand. Their "
             "tiny cavity supports came out with a small flat screwdriver: &ldquo;just an extra step&rdquo;.")
        + _p("<b>5 November 2026, Mark2.</b> The whole back-top, 27 hours, with the same receivers inside it and the same supports inside "
             "them. Its own walls stood in the way.")
        + b.quote("I can&rsquo;t reach in that far to remove those tiny little supports.", "DEREK · 6 NOVEMBER 2026", size=42)
        + '<p class="small" style="margin:26px 0 0">A test piece answers for a support only where the whole part leaves the same way in.</p>'
    )
    right = (
        "<h2>Where no tool reaches</h2>"
        + b.quote("But when there&rsquo;s not a clear path for the screwdriver, like there&rsquo;s not on the Pisco there and on the ASSE "
                  "there, then I need those to be printed without supports entirely.", "DEREK · 6 NOVEMBER 2026", size=38)
        + '<p class="small" style="margin:26px 0 26px"><b>Take the overhang away.</b> The receivers&rsquo; catches became bars bridged '
          "between two full shoulders, and bores across the rear wall grew pointed roofs. The back-top part study shows both.</p>"
        + _p("<b>Fill it.</b> Derek, 25 October 2026, of pockets beside the display: &ldquo;inner supported areas that could be filled "
             "entirely solid instead of being impossible to remove supports&rdquo;. Saving plastic is not a goal.")
        + _p("<b>Change the joint.</b> 6 November 2026: &ldquo;So I&rsquo;d like four screws for this display cover instead of these "
             "impossible-to-remove supports.&rdquo; The snap-in cover became a screwed one.", last=True)
    )
    body = (
        b.head("Supports · The way out", "Plan a support from its way out.",
               "Whether a support will come out is settled before the print starts, by the shape around it. A test piece is small and "
               "open on every side. The whole part puts the same pocket deep inside, behind its own walls.",
               size=160, lede_size=52)
        + b.scope(f"{SEEN} · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="any other plastic")
        + f'<div style="margin-top:30px">{_way_out_drawing()}</div>'
        + f'<div style="margin-top:14px">{needs}</div>'
        + b.rulebar(30, 30)
        + b.row(
            ("0 0 380px", b.fig(hand, "A small black printed receiver with a brass and steel valve seated in it, held between finger and thumb",
                                "1 November 2026 · Mark 1", "One of the ten. Open on every side.", h=500, pos="46% 60%", zoom=190)),
            ("0 0 740px", left), right, gap=50)
        + b.rulebar(30, 26)
        + b.row(
            ("0 0 1170px", '<p class="small" style="margin:0"><b>What stays supported.</b> A face that has to be flat to do its job keeps '
                           "its support, where all five needs are met. The front-bottom part study has exactly two such faces, its rail "
                           "catches. A support that comes out cleanly is not a debt, and a working face is never sloped to be rid of one.</p>"
                           + b.still_open("No full-size enclosure piece printed since these changes has a recorded cleanup. One was stopped, "
                                          "one result is pending and one has not been written down.")),
            b.record(b.link("The ten test pieces", f"{snap}/physical-result.json"),
                     b.link("The whole back-top", f"{ENC}/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json"),
                     b.link("The display cover", f"{P}/enclosure/front-service-review/physical-feedback.json"),
                     b.link("The enclosure&rsquo;s rule", f"{ENC}/README.md", anchor="support-removal-strategy")),
            gap=60)
    )
    return Page("plan-a-support-from-its-way-out", "PET-GF supports: plan a support from its way out", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 6 tilted undersides
def tilted():
    pried = b.asset("petgf-supports-faucet-pried.jpg", f"{INCL}/2026-11-10-faucet-slim-mark1/physical-result/photo-4.jpg", "1fe50e4ff")
    ring = b.asset("petgf-supports-faucet-one-ring.jpg", f"{INCL}/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/photo-2.jpg", "b388123d2")
    side = (
        "<h2>A different problem than we thought</h2>"
        + _p("The first faucet printed with Support D looked as if its roof had welded on: the stems broke and something stayed behind. "
             "Read back, the sliced file had almost no roof on the slope. The default trees met the part there with bare tips.")
        + b.quote("Still a huge problem &hellip; but a different problem than we thought, very different.", "DEREK · 10 NOVEMBER 2026", size=40)
        + '<div style="display:grid; gap:26px; margin-top:34px">'
        + b.stat('0.3 <span>m</span>', "of roof in 42.5 m of support, as that faucet was sliced. All of it lay in one low band.")
        + b.stat('9.1 <span>m</span>', "with the tree style set to Slim and nothing else changed.", hot=True)
        + "</div>"
    )
    photos = b.row(
        ("0 0 700px", _marked_photo(pried, "The underside of a black faucet base with torn strands of support, a broken stem in a round pocket and a screwdriver blade under it",
                                    (1275, 1700), (700, 800), pos=(50, 60),
                                    marks=[(1, 0.63, 0.30, "bad"), (2, 0.42, 0.50, "bad"), (3, 0.80, 0.62, "")],
                                    lab="10 November 2026 · Mark 1 · PET-GF",
                                    cap="Slim trees, so the roof was there. <b>1</b> A stem snapped off inside a pocket meant for a "
                                        "threaded insert. <b>2</b> Roof that tore instead of parting. <b>3</b> The screwdriver.")),
        ("0 0 700px", _marked_photo(ring, "A black faucet base in a hand with a clean underside and open pockets, and behind it the support that came off it as one ring",
                                    (1275, 1700), (700, 800), pos=(50, 0),
                                    marks=[(1, 0.72, 0.15, "scaffold"), (2, 0.38, 0.60, ""), (3, 0.26, 0.78, "")],
                                    lab="11 November 2026 · Mark 1 · PET-GF",
                                    cap="Four prints later. <b>1</b> The support, off as one ring. <b>2</b> A pocket, open and empty. "
                                        "<b>3</b> The underside it left.")),
        side, gap=50, style="margin-top:34px")
    steps = [
        ("10 Nov · Mark2", "Default trees, with D&rsquo;s roof and gap.", "Stems snapped. Their tops stayed on the part."),
        ("10 Nov · Mark 1", "Slim trees, so that a roof is there.", "Would not come off, even with a screwdriver."),
        ("10 Nov · Mark 1", "The gap doubled to 0.48 mm.", "Easier: &ldquo;they were all joined together&rdquo;. Underside no better."),
        ("10 Nov · Mark 1", "Gap back at 0.24 mm. Courses beside it bent to follow the slope.", "A better underside. Stems snapped inside the insert pockets."),
        ("10 Nov · Mark 1", "Pockets bridged and kept empty. Fins at the rim, under the roof.", "Stopped part way. The roof came off in one unit."),
        ("11 Nov · Mark 1", "The same recipe on the Sculpted faucet&rsquo;s base.", "&ldquo;&hellip;remove the entire bottom support in one piece&rdquo;"),
    ]
    table = ('<table class="grid" style="font-size:31px"><thead><tr><th style="width:300px">2026</th><th>What changed</th><th>What happened</th></tr></thead><tbody>'
             + "".join(f'<tr><th scope="row" class="mono" style="font-size:25px; letter-spacing:.06em; font-weight:400; color:var(--muted)">{d.upper()}</th>'
                       f"<td>{c}</td><td>{r}</td></tr>" for d, c, r in steps)
             + "</tbody></table>")
    body = (
        b.head("Supports · Tilted undersides", "Before blaming the gap, check the roof is there.",
               "The faucet&rsquo;s base prints leaning over, so its underside is a slope that curves. Under a flat ceiling a support&rsquo;s "
               "roof is one sheet. Under a slope it has to be built again, a step further out, on every layer.",
               size=150, lede_size=52)
        + b.scope(f"{SEEN} · Mark 1 and Mark2 · textured PEI · left 0.4 mm · the faucet&rsquo;s base", not_tried="any other tilted part")
        + photos
        + b.rulebar(28, 12)
        + table
        + b.row(
            ("0 0 1230px", '<p class="small" style="margin:0"><b>What we do now.</b> Read the sliced file for the roof before judging a '
                           "support. Keep supports out of blind holes, and bridge each hole&rsquo;s shoulder and roof instead. Derek on why "
                           "the fifth print let go: &ldquo;it&rsquo;s the removal of the heat sets that really made that possible&rdquo;.</p>"),
            b.record(b.link("Roof paths, two tree styles", f"{ROOFS}/inclines/contact-reading.json"),
                     b.link("The screwdriver", f"{INCL}/2026-11-10-faucet-slim-mark1/physical-result/physical-result.json", "1fe50e4ff"),
                     b.link("Stems in the pockets", f"{INCL}/2026-11-10-faucet-nonplanar-gap024-widebands-mark1/physical-result/physical-result.json", "b06ab316f"),
                     b.link("One unit", f"{INCL}/2026-11-10-faucet-nonplanar-rim-fins-mark1/physical-result/physical-result.json", "b388123d2"),
                     b.link("The Sculpted base", f"{P}/faucet/sculpted/prints/2026-11-11-support-and-fit-mark1/physical-result/physical-result.json", "7ebe4a45b")),
            gap=60, style="margin-top:24px")
        + b.still_open("The last two prints changed several things together, and the shared rules still call tilted and curved contacts "
                       "unqualified. A trees-only print on 11 November has no recorded result. Since these changes every faucet tip has "
                       "printed with a rough band near its end.")
    )
    return Page("check-the-roof-is-there", "PET-GF supports: on a tilted underside, check the roof is there", "petgf", body, right=RIGHT)


# --------------------------------------------------------------------------- 7 painted supports
def painted():
    obs = f"{ENC}/prints/2026-11-10-back-top-D-mark1/physical-observation"
    cov = f"{ENC}/prints/2026-11-10-back-top-D-coverage-mark1"
    ledge = b.asset("petgf-supports-backtop-ledge.jpg", f"{obs}/photo-3.jpg")
    wall = b.asset("petgf-supports-backtop-wall-end.jpg", f"{obs}/photo-4.jpg")
    photos = b.row(
        _marked_photo(ledge, "The first centimetres of a black print on the bed: a small ledge between two hollow support trunks with loops of plastic hanging under it",
                      (1280, 960), (1060, 600), pos=(12, 30), zoom=122,
                      marks=[(1, 0.455, 0.41, "bad"), (2, 0.25, 0.35, "scaffold"), (3, 0.085, 0.30, "bad")],
                      lab="10 November 2026 · Mark 1 · PET-GF",
                      cap="<b>1</b> A ledge nobody painted, laid over air. <b>2</b> Hollow trunks on their way up to something that was "
                          "painted. They pass the ledge and do not touch it. <b>3</b> A second spot."),
        _marked_photo(wall, "The end of a fluted wall on the print bed with a tangle of loops where its first courses had nothing under them",
                      (1280, 960), (1060, 600), pos=(62, 70), zoom=140,
                      marks=[(1, 0.56, 0.56, "bad")],
                      lab="The same print",
                      cap="<b>1</b> The third: the end of a fluted wall."),
        gap=50, style="margin-top:34px")
    owners = [
        ("Rail bearing faces", "Support", "The open rail run"),
        ("Funnel-frame ledges", "Support", "The open flank"),
        ("Raked joint ends", "Support", "The open front"),
        ("Receiver catches", "Bridge", "Nothing to remove"),
        ("Bores in the rear wall", "Lean, to a point", "Nothing to remove"),
    ]
    table = ('<table class="grid" style="font-size:31px"><thead><tr><th>Underside</th><th style="width:270px">Lands on</th><th style="width:330px">Way out</th></tr></thead><tbody>'
             + "".join(f'<tr><th scope="row">{a}</th><td>{c}</td><td>{d}</td></tr>' for a, c, d in owners) + "</tbody></table>")
    body = (
        b.head("Supports · Painted by hand", "Paint supports by hand and every underside is yours.",
               "Left alone, the slicer puts support under everything that overhangs. To keep supports out of pockets no tool reaches, "
               "back-top was switched to supports painted on by hand: none unless asked for. From then on, whatever nobody painted was "
               "printed over air.", size=150, lede_size=52)
        + b.scope("any filament: it is method · seen here in PET-GF on Mark 1, textured PEI, left 0.4 mm", label="Holds for")
        + photos
        + b.rulebar(32, 32)
        + b.row(
            ("0 0 1050px",
             b.quote("&hellip; at least three spots here that are not supported and pretty obviously should be, and it&rsquo;s printing an "
                     "error and loops are falling down. Do you see what I&rsquo;m talking about? What the hell happened here?",
                     "DEREK · 10 NOVEMBER 2026, TWELVE HOURS INTO A 37-HOUR PRINT", size=44)
             + '<h2 style="margin-top:40px">What had been checked</h2>'
             + _p("Four regions were painted: the rails and the rear outside. Before the print was sent, the sliced file was read for "
                  "supports in forbidden pockets, for room at the edge of the bed, for the right walls and fill in the right places. All "
                  "of it passed. Nobody had asked the other question: does every underside have something to land on? He stopped the "
                  "print.", last=True)),
            "<h2>Every underside gets an owner</h2>"
            + _p("The list made that afternoon has 84 downward-facing surfaces on this one piece, in 22 groups. Each group is given one of "
                 "the five landings, and each support a way out.")
            + table,
            gap=70)
        + b.rulebar(32, 26)
        + b.row(
            ("0 0 1050px", '<p class="small" style="margin:0"><b>Before you print</b> with painted supports: walk the model for every '
                           "face that points down, not for the ones you remember. For each, find its first course in the sliced file and "
                           "follow it down to what it rests on. A review that passes has answered only the questions it asked.</p>"),
            b.record(b.link("The loops", f"{obs}/physical-observation.json"),
                     b.link("The list of undersides", f"{cov}/surface-inventory.json"),
                     b.link("Why that list is not ready", f"{cov}/README.md"),
                     b.link("The rule as agents read it", f"{P}/AGENTS.md", anchor="supports"))
            + b.still_open("No back-top has been printed from the list. The one sliced on 11 November 2026 passed its review, as the "
                           "stopped one had."),
            gap=70)
    )
    return Page("every-underside-is-yours", "PET-GF supports: paint supports by hand and every underside is yours", "petgf", body, right=RIGHT)


def pages():
    return [blocks(), gap(), fell_off(), support_d(), way_out(), tilted(), painted()]
