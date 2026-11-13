"""Finished pages that several chapters place: the cover, the one idea, the bridge rule, the
front-bottom part study and the TPU strings page. Each function returns one Page."""
import math

import bookkit as b
import svgkit as k
from bookkit import Page

WAGO = "hardware/print-tests/front-top-wago-fit"


# --------------------------------------------------------------------------- cover
def cover():
    step = "printed-parts/enclosure/enclosure/enclosure-front-bottom.step"
    base = dict(step=step, target=[0.0, 110.0, 86.0], span=152, size="2430x2025", cam=[0.63, 0.9, 0.7])
    cut = 96.0
    printed = b.render("cover-printed.png", {**base, "clip": [{"axis": "z", "lo": -10.0, "hi": cut}], "edges": True,
                                             "materials": [{"names": ["enclosure-front-bottom"], "color": "#4a5a6b", "roughness": 0.8}]})
    layer = b.render("cover-layer.png", {**base, "clip": [{"axis": "z", "lo": cut - 1.3, "hi": cut}],
                                         "materials": [{"names": ["enclosure-front-bottom"], "color": "#f26a21", "unlit": True}]})
    ghost = b.render("cover-ghost.png", {**base, "clip": [{"axis": "z", "lo": cut, "hi": 200.0}], "ghost": ["enclosure-front-bottom"]})
    body = f"""
<div class="top">
  <div class="brand">HOME SODA MACHINE</div>
  <h1>Printing<br>the Machine</h1>
  <p class="sub">What nine months of printing a kitchen appliance taught us about FDM, one plastic at a time.</p>
</div>
<div class="hero">
  <img src="art/{ghost}" alt="" style="filter:brightness(3.4)">
  <img src="art/{printed}" alt="An enclosure quadrant printed part of the way up">
  <img src="art/{layer}" alt="">
</div>
<div class="note hot" style="left:1775px; top:1716px">THE COURSE BEING LAID</div>
<div class="leader" style="left:1775px; top:1778px; width:431px"></div>
<div class="leader" style="left:2203px; top:1778px; width:3px; height:372px"></div>
<div class="note dim" style="left:300px; top:1296px">NOT PRINTED YET</div>
<div class="leader dim" style="left:300px; top:1358px; width:343px"></div>
<div class="leader dim" style="left:640px; top:1358px; width:3px; height:262px"></div>
<div class="foot">homesodamachine.com</div>
"""
    return Page("cover", "Printing the Machine", "front", body, cls="cover")


# --------------------------------------------------------------------------- the one idea
def landings():
    W, H, BED, G = 2170, 790, 710, 60

    def x(i):
        return G + i * k.BEAD_W

    def y(r):
        return k.row_y(r, BED)

    s = [k.defs(G, BED), k.bed(30, W - 30, BED)]
    s.append(k.block(x(0), x(49), 0, 3, BED))
    # 1 straight wall, 2 a lean off it
    s.append(k.block(x(0), x(3), 4, 17, BED))
    for r in range(18, 27):
        s.append(k.course(x(0), x(3) + (r - 17) * 15, y(r), k.HOT if r == 22 else k.COLD))
    s.append(k.block(x(0), x(3), 11, 11, BED, "hot"))
    # 3 bridge
    s.append(k.block(x(15), x(18), 4, 15, BED) + k.block(x(24), x(27), 4, 15, BED) + k.block(x(15), x(27), 17, 19, BED))
    s.append(k.block(x(15), x(18), 16, 16, BED, "hot") + k.strand(x(18), x(24), y(16)) + k.block(x(24), x(27), 16, 16, BED, "hot"))
    # 4 fin
    s.append(k.block(x(34), x(37), 4, 14, BED) + k.block(x(30), x(37), 16, 18, BED) + k.block(x(30), x(37), 15, 15, BED, "hot"))
    s.append(f'<rect x="{k.n(x(30) + 2)}" y="{k.n(y(13))}" width="20" height="{k.n(y(3) - y(13))}" fill="{k.SCAFFOLD}"/>')
    s.append(f'<rect x="{k.n(x(30) + 7)}" y="{k.n(y(14))}" width="10" height="{k.n(k.ROW_H)}" fill="{k.SCAFFOLD}"/>')
    # 5 support
    s.append(k.block(x(46), x(49), 4, 26, BED) + k.block(x(39), x(46), 23, 25, BED) + k.block(x(39), x(46), 22, 22, BED, "hot"))
    s.append(k.scaffold(x(39), x(45), y(18), y(3)) + k.block(x(39), x(45), 19, 20, BED, "blue"))
    # labels
    s.append(k.arrow(2146, 610, 2146, 200))
    s.append(f'<text transform="translate(2166 560) rotate(-90)" font-family="IBM Plex Mono, monospace" font-size="25" letter-spacing="2" fill="{k.MUTED}">BUILD DIRECTION</text>')
    s.append(k.label(60, BED + 62, "THE BED"))
    s.append(k.label(x(30) - 20, y(8), "FIN", anchor="end"))
    sx = (x(39) + x(45)) / 2
    s.append(f'<rect x="{k.n(sx - 90)}" y="{k.n(y(11) - 8)}" width="180" height="48" fill="white"/>')
    s.append(k.label(sx, y(11) + 26, "SUPPORT", anchor="middle", fill=k.INK, weight=600))
    s.append(k.line(x(39) - 10, y(21), x(39) - 10, y(21) + k.ROW_H) + k.label(x(39) - 24, y(21) + 20, "GAP", anchor="end"))
    s.append(k.label((x(18) + x(24)) / 2, y(9), "AIR", anchor="middle", fill=k.FAINT))
    # callouts
    s.append(k.callout(1, x(3), y(11) + 12, x(3) + 144, y(11) + 12))
    s.append(k.callout(2, x(3) + 75, y(22) + 12, x(3) + 234, y(22) + 12))
    s.append(k.callout(3, (x(18) + x(24)) / 2, y(16) + 2, (x(18) + x(24)) / 2, y(23)))
    s.append(k.callout(4, x(33), y(15) + 2, x(33), y(22)))
    s.append(k.callout(5, x(39), y(22) + 12, x(39) - 130, y(22) + 12))
    hero = k.svg(W, H, "".join(s), "Five things a course of plastic can land on",
                 "Section through an imaginary part on the print bed. Left to right: a straight wall; a corbel that leans out a "
                 "little each course; a bridge pulled between two piers over air; a roof whose free edge rests on a thin fin; "
                 "and a roof resting on slicer support, with a gap under it.")
    cols = [
        ("1", "Straight up", "The course below, directly underneath. A plain wall. Everything else here is a way of getting back to this.", "Every wall of the enclosure."),
        ("2", "Lean out", "Step each course out a little, so most of every road still sits on the one below.", "The lifting handholds, the chamfer under a bed-facing round, the pointed roof of a teardrop hole."),
        ("3", "Bridge", "Pull the road tight between two landings. Both have to be there before the road arrives.", "The connector pockets, the receiver catches, the roofs of the insert pilots."),
        ("4", "Fin", "A thin wall we draw into the part under an edge, to be snapped off at the bench.", "The visible lower edge of the faucet base."),
        ("5", "Support", "Scaffold from the slicer, with a gap so it lets go. Only where a tool can get in to lever it out.", "The two rail catches of front-bottom. Nothing else on that part."),
    ]
    col_html = "".join(
        f'<div><div style="display:flex;align-items:center;gap:20px;margin-bottom:18px"><span class="num">{n}</span><h2 style="margin:0">{t}</h2></div>'
        f'<p class="small">{d}</p><h3 style="margin-top:22px">In PET-GF</h3><p class="small" style="color:var(--muted)">{m}</p></div>'
        for n, t, d, m in cols
    )
    a = [k.defs(40, 262), k.bed(10, 510, 262), k.block(40, 166, 0, 5, 262), k.block(40, 166, 6, 6, 262, "hot")]
    ay = k.row_y(6, 262) + 12
    a.append(k.road(f"M166 {ay} C 250 {ay}, 300 {ay + 18}, 340 {ay + 70} S 400 228, 366 232 S 330 190, 372 176 S 430 214, 452 236"))
    a.append(k.label(300, 56, "NO LANDING", fill=k.BAD, weight=600))
    air = k.svg(520, 300, "".join(a), "A road laid over air droops and curls")
    photo = b.asset("wago-roof-fell.jpg", f"{WAGO}/2026-11-12-mark2/physical-result/IMG_8622.jpeg", "a8f24b2b5")
    body = (
        b.head("The one idea", "Every course lands on something.",
               "A printer builds a part one course at a time, from the bed up. Each road of plastic comes out soft and stays put "
               "only if something is already underneath. There are five things it can land on.")
        + b.scope("any filament: it is geometry · each plastic&rsquo;s own limits are in its part", label="Holds for")
        + f'<div style="margin-top:36px">{hero}</div>'
        + f'<div class="grid5" style="margin-top:32px">{col_html}</div>'
        + b.rulebar(28, 28)
        + b.row(
            ("0 0 1010px",
             '<h2>The first three leave nothing to remove.</h2>'
             '<p class="small">A wall, a lean and a bridge are all part. A fin has to be snapped off and a support levered out, so each '
             'needs a way in. In PET-GF a bridge leaves the roughest underside of the five, so it goes where nobody looks or no tool '
             'can reach. Before any of them: can the part be turned so the roof becomes a floor?</p>'
             '<p class="small" style="margin:0"><b>Air is not on the list.</b> A road laid over nothing does not hang there waiting '
             'for the next one. It droops, and everything printed onto it afterwards goes with it.</p>'),
            ("0 0 380px", f'<div style="padding-top:40px">{air}</div>'),
            b.fig(photo, "Loops of black plastic hanging from a pocket roof", "12 November 2026 · PET-GF",
                  "A pocket roof laid across a cutout that had taken its landing away.", h=340, pos="62% 52%", zoom=150),
            gap=64)
    )
    return Page("every-course-lands-on-something", "Every course lands on something", "any", body, right="The one idea")


# --------------------------------------------------------------------------- bridge
def bridge():
    BED, G = 230, 20

    def y(r):
        return k.row_y(r, BED)

    def frame(ox, kind, step):
        g = [f'<g transform="translate({ox} 100)">', k.bed(4, 372, BED), k.block(20, 104, 0, 3, BED)]
        if kind == "two":
            g.append(k.block(272, 356, 0, 3, BED))
        else:
            g.append(k.block(272, 356, 0, 1, BED) + k.missing(273, y(3), 355, y(1)))
        top = y(4)
        sag = f"M104 {top + 12} C 180 {top + 12}, 230 {top + 30}, 268 {top + 66} S 322 {top + 86}, 344 {top + 60}"
        if step == 1:
            g.append(k.block(20, 104, 4, 4, BED, "hot") + k.strand(104, 186, top) + k.nozzle(184, top))
        elif kind == "two" and step == 2:
            g.append(k.block(20, 104, 4, 4, BED, "hot") + k.strand(104, 272, top) + k.block(272, 356, 4, 4, BED, "hot") + k.nozzle(342, top))
        elif kind == "two":
            g.append(k.block(20, 104, 4, 4, BED) + k.strand(104, 272, top, k.COLD) + k.block(272, 356, 4, 4, BED))
            g.append(k.block(20, 272, 5, 5, BED, "hot") + k.nozzle(270, y(5)))
        elif step == 2:
            g.append(k.block(20, 104, 4, 4, BED, "hot") + k.road(sag) + k.nozzle(342, top))
        else:
            t5 = y(5)
            g.append(k.block(20, 104, 4, 4, BED) + k.road(sag, k.COLD) + k.block(20, 104, 5, 5, BED, "hot"))
            g.append(k.road(f"M104 {t5 + 12} C 164 {t5 + 12}, 198 {t5 + 34}, 224 {t5 + 62} S 276 {t5 + 44}, 252 {t5 + 20} S 206 {t5 + 40}, 244 {t5 + 70}"))
            g.append(k.nozzle(270, t5))
        g.append("</g>")
        return "".join(g)

    def strip(kind, title, color, desc):
        body = k.defs(G, BED) + "".join(frame(i * 394, kind, i + 1) for i in range(3)) + k.label(8, 30, title.upper(), fill=color, weight=600)
        return k.svg(1170, 360, body, title, desc)

    two = strip("two", "Two landings", k.INK,
                "The nozzle leaves one pier, pulls a road across the gap and presses it onto the second pier. The next course then has a floor.")
    one = strip("one", "One landing cut away", k.BAD,
                "The second pier has been cut down. The road has nothing to press onto and sags, and the next course is laid on the sag.")
    caps = lambda items: '<div class="grid3" style="gap:20px">' + "".join(f'<p class="tiny" style="margin:0">{t}</p>' for t in items) + "</div>"
    photo = b.asset("wago-roof-fell.jpg", f"{WAGO}/2026-11-12-mark2/physical-result/IMG_8622.jpeg", "a8f24b2b5")
    left = (
        '<p style="font-size:50px; line-height:1.36; margin-bottom:44px">A bridge is the one time the printer lays plastic over air on '
        'purpose. It works because the road is fixed at one end, pulled across, and pressed down at the other while it is still soft. '
        'It hangs like a line pulled tight. Take away either end and it is just a road laid over nothing.</p>'
        + two + '<div style="margin:14px 0 46px">' + caps(["Leaves the first landing.", "Pulled across, pressed onto the second.", "The next course has a floor."]) + "</div>"
        + one + '<div style="margin-top:14px">' + caps(["Leaves the first landing.", "Nothing to press onto. It sags.", "The next course is laid on the sag."]) + "</div>"
    )
    right = (
        b.fig(photo, "Loops of black plastic hanging where a pocket roof should be", "12 November 2026 · Mark2 · PET-GF",
              "A fit coupon for the connector pockets in front-top. A cutout added to clear the connector&rsquo;s levers went through "
              "the wall the pocket roofs rested on. The slice still showed those roofs as bridges, and that was taken as proof they "
              "would print.", h=1010, pos="60% 50%", zoom=128)
        + '<div style="margin-top:52px">' + b.quote("The only reason a bridge works is because it *is* a bridge that actually has a column supporting both ends.", "DEREK · ON SEEING THAT COUPON") + "</div>"
    )
    body = (
        b.head("Landing 3 · Bridge", "A bridge needs two landings.")
        + b.scope("any filament: it is geometry · shown here in PET-GF", label="Holds for")
        + b.row(("0 0 1130px", left), right, gap=80, style="margin-top:44px")
        + b.rulebar(60, 40)
        + b.row(
            b.block("How it gets in", "Nobody draws a bridge to nowhere on purpose. It arrives as a side effect, when a relief, a chamfer "
                    "or a cutout made for some other reason passes through the wall a bridge was resting on. On the rear receiver it was "
                    "a service opening. Five days later, on these pockets, it was clearance for a lever."),
            b.block("Before you print", "In the slice, find the first road across every opening and follow each of its ends straight down. "
                    "If either end is over air it is not a bridge, whatever the slicer calls it. After any cut near an opening, look at "
                    "the roofs beside it again."),
            ("0 0 560px", b.record(b.link("The coupon and its photographs", f"{WAGO}/2026-11-12-mark2/physical-result/physical-result.json", "a8f24b2b5"),
                                   b.link("The receiver, five days earlier", "changes/2026-11-07-1859-pisco-bridge-anchor/entry.md"))),
            gap=70)
    )
    return Page("a-bridge-needs-two-landings", "A bridge needs two landings", "any", body, right="Landing 3 of 5")


# --------------------------------------------------------------------------- front-bottom
def anatomy():
    from proj import projector
    step = "printed-parts/enclosure/enclosure/enclosure-front-bottom.step"
    mat = [{"names": ["enclosure-front-bottom"], "color": "#3a4654", "roughness": 0.85}]
    cam, target, span, size = [0.72, 0.86, 0.62], [0.0, 112.0, 82.0], 147, (2170, 1110)
    main = b.render("front-bottom-on-the-bed.png", dict(step=step, cam=cam, target=target, span=span, size="2170x1110", edges=True, materials=mat))
    pm = projector(cam, target, span, size)
    # the rail in section: 16 mm wide, 19 mm tall, so the picture needs no cropping on the page
    rcam, rtarget, rspan, rsize = [0.0, 1.0, 0.0], [100.6, 110.0, 167.0], 9.5, (860, 1000)
    rail_img = b.render("front-bottom-rail-section.png", dict(step=step, section={"normal": [0, 1, 0], "at": [0, 110, 0]}, cam=rcam, target=rtarget,
                                                              span=rspan, size="860x1000", edges=True, materials=mat))
    pr = projector(rcam, rtarget, rspan, rsize)
    b.source("front", "hardware/printed-parts/enclosure/enclosure/prints/2026-11-11-front-bottom-D-mark2/support-audit-1901.json")
    b.source("frontslice", "hardware/printed-parts/enclosure/enclosure/prints/2026-11-11-front-bottom-D-mark2/review.json")
    marks = [("1", [98.6, 110, 174.8], "hot"), ("1", [-98.6, 110, 174.8], "hot"), ("2", [108, 192, 14], ""), ("2", [-108, 192, 14], ""),
             ("3", [110.5, 90, 86], ""), ("4", [110.5, 30, 142], ""), ("5", [12.4, 156.5, 14.6], ""), ("6", [-104, 208, 100], "")]
    discs = "".join(f'<span class="num on-model {c}" style="left:{pm(pt)[0]:.0f}px; top:{pm(pt)[1]:.0f}px">{n}</span>' for n, pt, c in marks)
    x0, yroof = pr([103.45, 110, 169.2])
    x1, _ = pr([98.92, 110, 169.2])
    tx0, ty0 = pr([103.5, 110, 168.92])
    tx1, ty1 = pr([99.1, 110, 160.52])
    _, yled = pr([100, 110, 160.0])
    mid = (ty0 + ty1) / 2
    over = k.svg(860, 1000,
                 k.defs()
                 + k.scaffold(tx0, tx1, ty0, ty1)
                 + k.line(x0, yroof, x1, yroof, k.HOT, 16)
                 + k.label(24, yroof - 70, "SUPPORTED", 40, fill=k.HOT, weight=600) + k.label(24, yroof - 22, "FACE", 40, fill=k.HOT, weight=600)
                 + k.line(132, yroof - 34, x0 - 12, yroof - 2, k.HOT, 5)
                 + k.label(24, mid - 30, "SHORT", 40, fill=k.SCAFFOLD, weight=600) + k.label(24, mid + 18, "TREE", 40, fill=k.SCAFFOLD, weight=600)
                 + k.label(24, yled - 66, "WAY OUT", 40, fill=k.INK, weight=600) + k.arrow(250, yled - 30, 36, yled - 30, k.INK, 6),
                 "Section through a sliding rail",
                 "The rail is a hook. The flat underside of its head is the supported face. A short tree stands on the ledge under it, "
                 "in a lane that is open along its length.", style="position:absolute; left:0; top:0")
    items = [
        ("1", "hot", "Rail catches", "Support", "The only two supported faces. They are flat on purpose: they hold the top half down, and a sloped catch would cam open. Each gets a short tree that stands on the ledge just below it."),
        ("2", "", "Handhold roofs", "Lean", "A 45° corbel, printed in ordinary layers. It replaced a flat ceiling that had needed tree supports, a band of six walls and snap-off fins along its edge."),
        ("3", "", "Vents", "Lean", "The vent is the flutes, pierced. Each slot runs up the floor of a groove and ends in a 45° point, so nothing has to bridge."),
        ("4", "", "Flutes", "Straight up", "Grooves that run straight up the build cost nothing. They stop short of the bed so the first layer is a plain outline, and they hide the seam between front and back in a shadow."),
        ("5", "", "Bosses", "Straight up", "Stand on the floor slab and are bored along the build direction, which keeps the holes round."),
        ("6", "", "Seam knuckles", "Lean", "Every hidden underside rises at the same 45°. Where a screw hole crosses one it runs on as a slot, because a round hole through a slope leaves a skin a third of a millimetre thick."),
    ]
    legend = "".join(
        f'<div style="display:flex; gap:24px; align-items:flex-start; margin-bottom:26px; break-inside:avoid"><span class="num {c}">{n}</span>'
        f'<div><p style="margin:0 0 4px; font:650 40px/1.2 \'IBM Plex Sans\'; color:var(--ink)">{t} <span class="mono" style="font-size:25px; font-weight:400; letter-spacing:.08em; color:var(--muted); margin-left:10px">{land.upper()}</span></p>'
        f'<p class="tiny" style="margin:0; font-size:32px; color:var(--text)">{d}</p></div></div>'
        for n, c, t, land, d in items
    )
    body = (
        b.head("Part study · Enclosure front-bottom", "One pair of supported faces.",
               "It takes about a day to print and it overhangs all over: handholds, vents, rails, seam knuckles. All but two of those "
               "places land on plastic. The two are flat because their job needs them flat.", size=150, lede_size=52, top=60)
        + b.scope("PET-GF · the print sent to Mark2 on 11 November 2026 · textured PEI · left 0.4 mm")
        + f'<figure style="position:relative; margin-top:6px; height:1110px"><img src="art/{main}" alt="Enclosure front-bottom as it sits on the bed" '
          f'style="position:absolute; left:0; top:0; width:2170px; height:1110px">{discs}'
          f'<div style="position:absolute; right:0; top:20px; width:330px; display:grid; gap:36px">'
          + b.stat(b.setting("frontslice", "/layers"), "layers in that print")
          + b.stat(b.setting("front", "/summary/support_bodies"), "supports, both standing on the part")
          + '</div><p class="mono" style="position:absolute; left:0; bottom:26px; margin:0; font-size:27px; line-height:1.5; letter-spacing:.08em; color:var(--muted)">AS IT SITS ON THE BED<br>BUILD DIRECTION ↑</p></figure>'
        + b.rulebar(10, 30)
        + b.row(
            ("0 0 480px", f'<div style="position:relative; width:480px; height:558px; background:var(--wash)"><img src="art/{rail_img}" alt="" style="position:absolute; left:0; top:0; width:480px; height:558px">{over}</div>'
                          '<p class="cap"><span class="lab">Section through a rail</span>The lane is open along its whole length, so a screwdriver levers the tree out sideways in one piece.</p>'),
            f'<div style="columns:2; column-gap:50px">{legend}</div>', gap=56)
        + b.row(
            b.quote("&hellip;precisely one pair of supported faces, that are quite intentional and the absolute easiest to remove (with tool) support removal situation we&rsquo;ve found so far.", "DEREK · 12 NOVEMBER 2026", size=39),
            ("0 0 800px", '<p class="tiny" style="margin:0; font-size:32px"><b>A support is not a defect.</b> In September a tool counted supports and scored fewer as better. To lose one, a catch on the rear rail became a ridge, which can cam open. The flat went back, with its support. A count of supports falls whenever the thing being supported is deleted.</p>'),
            gap=56, style="margin-top:-6px")
        + b.still_open("The record holds this piece&rsquo;s reviewed slice and a rail coupon whose support came out whole on 10 November. The full-size print&rsquo;s own result is not written down yet.")
    )
    return Page("one-pair-of-supported-faces", "Front-bottom: one pair of supported faces", "petgf", body, right="Part study")


# --------------------------------------------------------------------------- strings
def strings():
    CX, CY = 500, 330
    loops = [(196, 132), (232, 162), (268, 192), (304, 222)]

    def pt(rx, ry, deg):
        a = math.radians(deg)
        return CX + rx * math.cos(a), CY - ry * math.sin(a)

    ax, ay = pt(196, 132, 212)
    bx, by = pt(196, 132, 22)
    arc = f"M{k.n(ax)} {k.n(ay)} A196 132 0 0 0 {k.n(bx)} {k.n(by)}"

    def ring(kind):
        g = [f'<ellipse cx="{CX}" cy="{CY}" rx="324" ry="242" fill="{k.WASH}"/>']
        g += [f'<ellipse cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{k.COLD}" stroke-width="27"/>' for rx, ry in loops]
        g.append(f'<ellipse cx="{CX}" cy="{CY}" rx="178" ry="114" fill="white"/>' + k.label(CX, CY + 96, "THE BORE", 25, anchor="middle", fill=k.FAINT))
        if kind == "travel":
            g.append(f'<path d="{arc}" fill="none" stroke="{k.INK}" stroke-width="6" stroke-dasharray="4 15" stroke-linecap="round"/>')
            g.append(k.line(ax, ay, bx, by, k.HOT, 8) + k.label(CX - 6, CY - 22, "THE THREAD", 26, anchor="middle", fill=k.HOT, weight=600))
            g.append(k.label(CX, 612, "THE ROUTE THE NOZZLE TOOK, OVER THE WALL", 25, anchor="middle", fill=k.INK) + k.line(CX, 588, CX, 476))
        else:
            g.append(f'<path d="{arc}" fill="none" stroke="{k.HOT}" stroke-width="27" stroke-linecap="round"/>')
            g.append(k.label(CX, 612, "STILL PRINTING, ALL THE WAY ROUND", 25, anchor="middle", fill=k.HOT, weight=600) + k.line(CX, 588, CX, 476, k.HOT))
        g.append(f'<circle cx="{k.n(ax)}" cy="{k.n(ay)}" r="15" fill="white" stroke="{k.INK}" stroke-width="6"/>' + k.nozzle_top(bx, by))
        g.append(k.label(24, ay + 150, "STOPS PRINTING HERE" if kind == "travel" else "NEVER STOPS", 25, fill=k.INK) + k.line(170, ay + 122, ax - 14, ay + 12))
        g.append(k.label(bx + 96, by - 96, "THE NOZZLE", 25, fill=k.INK) + k.line(bx + 92, by - 90, bx + 30, by - 30))
        return k.svg(1000, 660, "".join(g),
                     "Seen from above: a ring of wall around a bore" + (", with a thread across it" if kind == "travel" else ", printed all the way round"),
                     "The nozzle stopped printing at one point on the wall and travelled round over the wall to another. The thread it left runs straight between the two points, across the bore."
                     if kind == "travel" else "The nozzle keeps printing along the wall between the same two points, so nothing crosses the bore.")

    E = "future/pump-elbow-exploration/prints"
    photo = b.asset("tpu-elbow-threads.jpg", f"{E}/2026-10-16-vertical-center-web-tpu85a-mark1/result-photo.jpg", max_px=2200)
    body = (
        b.head("Strings", "The nozzle goes around. The string goes straight.",
               "Soft TPU never quite stops coming out. When the nozzle stops printing and moves, a thread stays attached where it left off "
               "and follows. Sending the nozzle the long way round, over the walls, does nothing. The thread is not on that route. It is "
               "pulled tight between its two ends.", size=158)
        + b.scope("TPU 85A, both brands · Mark 1 and Mark2 · right 0.6 mm nozzle", not_tried="PET-GF or PETG, which do not string like this here")
        + '<div class="grid2" style="margin-top:40px">'
        + f'<figure>{ring("travel")}<figcaption class="cap"><span class="lab">What we had</span>Every move between walls was routed to stay over plastic. In the file the nozzle never crosses the bore. The thread does.</figcaption></figure>'
        + f'<figure>{ring("print")}<figcaption class="cap"><span class="lab">What works</span>Print through every turn. Any hop that is left is short, straight and over plastic, so a thread has nowhere to cross.</figcaption></figure></div>'
        + b.rulebar(46, 40)
        + b.row(
            ("0 0 900px", b.fig(photo, "Two pairs of black TPU sockets with their bores full of fine threads", "16 October 2026 · Mark 1 · Bambu TPU 85A",
                                "A pair of pump elbows joined by a web. Seam routing, wall-following travel, wiping laps and fins had each been tried by then. The bores still came out like this.",
                                h=690, pos="50% 46%")),
            b.quote("&hellip;if you stop printing and you travel south and then you travel east, you end up drawing a diagonal thread in the southeast direction.", "DEREK · LOOKING AT THAT PRINT", size=49)
            + '<div class="grid2" style="margin-top:48px; gap:44px">'
            + b.stat('78 <span>of 118</span>', "rerouted moves in that file could still pull a thread across a bore, though the nozzle stayed over plastic on every one.")
            + b.stat('0 <span>of 6,118</span>', "in the reworked file. No retraction and no Z-hop anywhere in the part.", hot=True)
            + "</div>"
            + '<p class="small" style="margin-top:32px"><b>22 October 2026, Mark2, Siraya TPU 85A:</b> &ldquo;That worked very well. I see no strings, and seal seems as good as before.&rdquo;</p>'
            + b.still_open("The clean print also changed the brand of TPU. The reworked path has not yet been run on the first brand."),
            gap=80)
        + '<div style="margin-top:34px">' + b.record(b.link("The print with the threads", f"{E}/2026-10-16-vertical-center-web-tpu85a-mark1/physical-result.json"),
                                                     b.link("Which moves could leave a thread", f"{E}/2026-10-16-vertical-center-web-tpu85a-mark1/free-strand-review.json"),
                                                     b.link("The reworked file", f"{E}/2026-10-16-deposited-links-siraya85a-mark1/emitted-command-review.json"),
                                                     b.link("The clean print", f"{E}/2026-10-22-deposited-links-siraya85a-mark2/physical-result.json")) + "</div>"
    )
    return Page("the-string-goes-straight", "TPU: the nozzle goes around, the string goes straight", "tpu", body, right="Strings")


# --------------------------------------------------------------------------- first layer, PETG
def five_hundredths():
    D = "hardware/printed-parts/enclosure/display-cover/prints"
    before = b.asset("petg-first-layer-torn.jpg", f"{D}/2026-11-08-identification-set-mark1-dried-rethreaded/physical-result/photo-1.jpg", max_px=2000)
    after = b.asset("petg-first-layer-lifted.jpg", f"{D}/2026-11-08-identification-set-mark1-right-z005/physical-progress/white-first-layer.jpg", max_px=2000)

    def panel(ox, kind, title, note):
        BED = 190
        g = [f'<g transform="translate({ox} 0)">', k.bed(0, 560, BED)]
        tip = {"close": BED - 9, "right": BED - 20, "far": BED - 38}[kind]
        if kind == "close":
            g.append(f'<path d="M40 {BED} L40 {BED - 8} Q70 {BED - 30} 96 {BED - 10} L300 {BED - 10} Q318 {BED - 34} 352 {BED - 12} Q372 {BED - 40} 398 {BED - 9} L398 {BED} Z" fill="{k.HOT}"/>')
            g.append(k.road(f"M398 {BED - 9} Q430 {BED - 46} 470 {BED - 30}", k.HOT, 10))
        elif kind == "right":
            g += [f'<rect x="{40 + i * 60}" y="{BED - 20}" width="62" height="20" rx="10" fill="{k.HOT if i == 5 else k.COLD}"/>' for i in range(6)]
        else:
            g += [f'<circle cx="{66 + i * 60}" cy="{BED - 15}" r="15" fill="{k.HOT if i == 5 else k.COLD}"/>' for i in range(6)]
        g.append(k.nozzle(372 if kind != "far" else 366, tip, 1.15))
        g.append(k.label(0, 262, title.upper(), 27, fill=k.INK, weight=600) + k.label(0, 304, note, 30, mono=False))
        g.append("</g>")
        return "".join(g)

    drawing = k.svg(2170, 330,
                    panel(0, "close", "Too close", "Nowhere to go. It tears and backs up.")
                    + panel(805, "right", "Right", "Pressed flat, joined to its neighbour.")
                    + panel(1610, "far", "Too far", "Round lines that sit on top."),
                    "The first layer with the nozzle too close, right, and too far",
                    "Three sections of a first layer on the bed. Too close: the plastic has nowhere to go, piles up and tears. Right: each "
                    "line is pressed flat and joins the one beside it. Too far: round lines sit on the plate without being pressed in.")
    body = (
        b.head("First layer", "Five hundredths of a millimetre.",
               "The first layer is pressed into the plate through a gap the printer sets for itself. A little too small and the plastic has "
               "nowhere to go. It tears and smears, and the printer stops to say its extruder is overloaded, which sounds like a different problem.")
        + b.scope("Bambu PETG Basic, white · Mark 1 · glued Engineering Plate · right 0.2 mm nozzle · 8 November 2026", not_tried="any other plastic, plate or nozzle")
        + '<div class="grid2" style="margin-top:44px; gap:44px">'
        + b.fig(before, "A white first layer torn and smeared on a dark plate", "8 November 2026 · Mark 1 · white PETG",
                "The fourth try. By then the spools had been dried twice, the hotend swapped for a spare and the filament rethreaded. It stopped at the same place.",
                h=640, pos="48% 60%")
        + b.fig(after, "The same white square laid down in even lines, with the toolhead above it", "The same day · the same file · the same spot",
                "The right-side nozzles lifted by 0.05 mm, and nothing else changed. &ldquo;It&rsquo;s looking a lot better at the same spot, so far at least.&rdquo;",
                h=640, pos="52% 52%")
        + "</div>"
        + f'<div style="margin-top:40px">{drawing}</div>'
        + b.rulebar(36, 36)
        + b.row(
            ("0 0 800px", b.quote("Let&rsquo;s see if we can change just that one variable of the Z offset and try again.", "DEREK · 8 NOVEMBER 2026", size=47)
                          + '<p class="small" style="margin:34px 0 0">That print ran to the end. The next day: &ldquo;So the multicolor print turned out beautifully that time.&rdquo;</p>'),
            b.block("It belongs to one setup", "The lift is set only while a right-side filament is printing, and taken off again before each tool change. The black "
                    "from the left nozzle prints with none. It is the number for this plastic on this plate through these nozzles, and for nothing else.")
            + b.still_open("One print. The record calls the cause unconfirmed: the lift was the only change and the print finished, which does not rule out something else helping."),
            b.block("PET-GF&rsquo;s number is not PETG&rsquo;s", "Two days earlier this same job had been sent with the lift Mark 1 uses for PET-GF on textured plate, 0.18 mm. "
                    "On the glued plate, Derek: &ldquo;lol, okay, print stopped, it lifted right off.&rdquo; Asked whether that lift was the printer&rsquo;s own: "
                    "&ldquo;No. That should be documented as for pet-gf on textured plate.&rdquo;"),
            gap=64)
        + '<div style="margin-top:34px">'
        + b.record(b.link("Sent with PET-GF&rsquo;s lift, 6 November", f"{D}/2026-11-06-identification-set-mark1/physical-result.json"),
                   b.link("The fourth stop", f"{D}/2026-11-08-identification-set-mark1-dried-rethreaded/physical-result.json"),
                   b.link("How the lift is applied", f"{D}/2026-11-08-identification-set-mark1-right-z005/review.json"),
                   b.link("The same spot, lifted", f"{D}/2026-11-08-identification-set-mark1-right-z005/physical-progress.json"),
                   b.link("The finished print", f"{D}/2026-11-08-identification-set-mark1-right-z005/physical-result.json"),
                   b.link("Trims, and what each belongs to", "hardware/printed-parts/z-trim.md")) + "</div>"
    )
    return Page("five-hundredths-of-a-millimetre", "PETG: five hundredths of a millimetre", "petg", body, right="First layer")
