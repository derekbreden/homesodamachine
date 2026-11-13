"""Before any filament: what is geometry or method and holds whatever is in the nozzle."""
import bookkit as b
import svgkit as k
from bookkit import Page
from chapters import _mine

WAGO = "hardware/print-tests/front-top-wago-fit"
STD = f"{WAGO}/2026-11-12-mark1-dots-3-4-standard-layers"


# --------------------------------------------------------------------------- height
def height():
    b.source("petgf", "hardware/printed-parts/petgf.3mf", member="Metadata/project_settings.config")
    layer = b.setting("petgf", "/layer_height")
    # A ladder of layer boundaries near a pocket roof, with four drawn heights and where each lands.
    W, H, step, y30 = 1040, 760, 240, 400
    g = [k.defs()]
    for i in (-1, 0):
        g.append(f'<rect x="250" y="{y30 + i * step}" width="500" height="{step}" fill="{k.WASH}"/>')
        g.append(k.label(500, y30 + i * step + step / 2 + 12, "ONE LAYER", 30, anchor="middle", fill=k.FAINT))
    for i, name in ((-1, "30.24"), (0, "30.00"), (1, "29.76")):
        yy = y30 + i * step
        g.append(k.line(250, yy, 750, yy, k.INK, 7))
        g.append(k.label(790, yy + 20, name, 62, fill=k.INK, weight=600))
    g.append(k.label(790, y30 - step - 60, "PRINTS AT", 30, fill=k.MUTED))
    g.append(k.label(20, y30 - step - 60, "DRAWN", 30, fill=k.HOT, weight=600))
    for name, mm, lands in (("30.2", 0.2, -1), ("30.1", 0.1, 0), ("30.0", 0.0, 0), ("29.9", -0.1, 0)):
        yy = y30 - mm / 0.24 * step
        g.append(k.line(250, yy, 750, yy, k.HOT, 5, dash="18 12"))
        g.append(k.label(20, yy + 20, name, 62, fill=k.HOT, weight=600))
        target = y30 + lands * step
        if abs(target - yy) > 8:
            g.append(k.arrow(205, yy, 205, target + (14 if target < yy else -14), k.HOT, 7))
    ladder = k.svg(W, H, "".join(g), "Four drawn pocket heights and the two heights that print",
                   "A ladder of layer boundaries one layer apart. Drawn heights of 29.9, 30.0 and 30.1 millimetres all land on the boundary "
                   "that prints at 30.00. A drawn height of 30.2 lands a whole layer higher, at 30.24.")
    rows = [("Wide pocket, three dots", "30.0", "30.00"), ("Wide pocket, four dots", "29.9", "30.00"),
            ("Narrow pocket, three dots", "30.2", "30.24"), ("Narrow pocket, four dots", "30.1", "30.00")]
    tab = ('<table class="grid"><thead><tr><th>Pocket</th><th>Drawn</th><th>Printed</th></tr></thead><tbody>'
           + "".join(f"<tr><th>{a}</th><td>{d} mm</td><td><b>{p} mm</b></td></tr>" for a, d, p in rows) + "</tbody></table>")
    body = (
        b.head("Height", "Height moves one layer at a time.",
               "The printer cannot lay half a layer. A height in the drawing is rounded to a whole number of layers, so a change smaller "
               "than a layer either vanishes or arrives as a whole layer.")
        + b.scope("any filament: it is arithmetic · the example is a PET-GF pocket, 12 November 2026", label="Holds for")
        + b.row(
            ("0 0 1040px", f'<div style="margin-top:10px">{ladder}</div>'
                           '<p class="cap"><span class="lab">One pocket roof, four drawings</span>Three of the four drawn heights print as the same pocket. The fourth prints a whole layer taller.</p>'),
            '<h2>What was asked</h2>'
            '<p class="small">Two test pockets for a connector, one a tenth of a millimetre shorter than the other, to feel which grips better.</p>'
            '<h2>What the slice did</h2>'
            f'<p class="small">A tenth is less than half of a {layer} mm layer. Both wide pockets came out the same height. The narrow pair came out a whole layer apart.</p>'
            + tab
            + '<h2 style="margin-top:40px">What went wrong next</h2>'
            '<p class="small" style="margin:0">To make the tenth show, the plate was re-sliced with thinner layers around the pockets, and sent. Derek stopped it.</p>',
            gap=70, style="margin-top:40px")
        + b.rulebar(44, 40)
        + b.row(
            b.quote("Do not use finer layers anywhere - that is not an option - that is a completely different variable", "DEREK · 12 NOVEMBER 2026", size=45)
            + '<div style="margin-top:36px">' + b.quote("if the slices come out the same with what I requested then just tell me that.", "DEREK · THE SAME MINUTE", size=45) + "</div>",
            b.block("A different variable", "Layer height is part of the process, like temperature. Change it and an overhang prints differently, a support sits a "
                    "different distance under its roof, and each course has a different time to cool. A fit trial that changes it is testing two things.")
            + b.block("What we do", "Keep the plastic&rsquo;s own layers. Read the opening from the sliced file, from the top of the last floor course to the "
                      "underside of the first roof course. When two drawings print the same, say so. To compare heights, draw them a whole layer apart."),
            gap=80)
        + '<div style="margin-top:36px">'
        + b.record(b.link("Drawn and sliced openings", f"{STD}/print-job.json", "ae3a1e7b7"),
                   b.link("The cancelled plate with thinner layers", f"{WAGO}/2026-11-12-mark1-dots-3-4/print-job.json", "48e5d5364"),
                   b.link("How the fit came out", f"{STD}/physical-result/physical-result.json", "eb3ec0fcf")) + "</div>"
    )
    return Page("height-moves-one-layer-at-a-time", "Height moves one layer at a time", "any", body, right="Height")


# --------------------------------------------------------------------------- coupons
def coupon():
    photo = b.asset("any-five-coupons.jpg", "hardware/print-tests/rear-snap-retention/v4/physical-result/10-all-five.jpg", max_px=2400)
    keep = [
        ("The pose", "The same way up as the full part, so its layers run the same way and its overhangs face the same way."),
        ("The layers", "The plastic&rsquo;s own first layer and layer height, the same nozzle and that printer&rsquo;s own trim."),
        ("The wall it sits in", "A pocket cut free of its wall is a different pocket. Keep the wall and its full thickness."),
        ("Both landings", "Every bridge in the coupon needs both of the landings it has in the part."),
        ("Every stop", "Whatever the mating part touches in the machine, it should touch in the coupon."),
    ]
    keep_html = "".join(f'<div style="display:flex; gap:22px; margin-bottom:20px"><span class="num">{i + 1}</span><p class="small" style="margin:0"><b>{t}.</b> {d}</p></div>'
                        for i, (t, d) in enumerate(keep))
    body = (
        b.head("Test pieces", "A coupon has to print like the part.",
               "A coupon is a small piece cut out of a big part, so a fit can be tried in an hour instead of a day. It tells the truth only if it "
               "keeps everything that decides how the feature prints.")
        + b.scope("any filament: it is method · every example on this page is PET-GF", label="Holds for")
        + b.row(
            ("0 0 1180px", b.fig(photo, "Five black printed coupons on a counter, each holding a pump, a regulator, a meter or a fitting",
                                 "2 November 2026 · PET-GF",
                                 "Five coupons, each a crop of the real part with its own wall, holding the hardware it was cut to hold. Two were kept as they were. Three went back to be changed.",
                                 h=1000, pos="74% 92%", zoom=142)),
            "<h2>What a coupon keeps</h2>" + keep_html, gap=70, style="margin-top:44px")
        + b.rulebar(44, 40)
        + '<h2>What a coupon cannot tell you</h2>'
        + '<div class="grid3" style="margin-top:22px">'
        + '<div><h3>Whether a tool can reach</h3><p class="small">Tiny supports came out of the coupons with a screwdriver. In the full rear quadrant the walls were in the way.</p>'
          + b.quote("I can&rsquo;t reach in that far to remove those tiny little supports.", "DEREK · 5 NOVEMBER 2026", size=38) + "</div>"
        + '<div><h3>How it feels at full length</h3><p class="small">A screw hole that passed a screw freely in a short sample dragged in a longer one. Drag grows with the length of plastic the screw passes through.</p>'
          + b.quote("On the 12 mm sample it pushed through fine, on the 40 mm sample I got some resistance in some cases and had to screw to get past it.", "DEREK · 26 OCTOBER 2026", size=38) + "</div>"
        + '<div><h3>How long a layer takes</h3><p class="small" style="margin:0">A small coupon printed alone finishes a layer in a few seconds, and the next goes down on plastic that is still soft. On 26 October 2026 a cable-clip coupon printed that way deformed and was cancelled. The full part gives every layer minutes.</p></div>'
        + "</div>"
        + '<div style="margin-top:34px">'
        + b.record(b.link("The five coupons", "hardware/print-tests/rear-snap-retention/v4/physical-result/physical-result.json"),
                   b.link("The full quadrant, where the tool did not reach", "hardware/printed-parts/enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json"),
                   b.link("The screw-hole ladder", "hardware/print-tests/m5-seam-bearing/physical-result.json", "b57b985c6"),
                   b.link("The coupon that printed too fast", "future/snap-fit-tests/2026-10-26-mark2-combined/README.md", "2f2d9c94a")) + "</div>"
    )
    return Page("a-coupon-has-to-print-like-the-part", "A coupon has to print like the part", "any", body, right="Test pieces")


# --------------------------------------------------------------------------- one thing
def one_thing():
    # a ladder plate from above: a control in the middle and steps either side, marked with dots
    W, H = 2170, 430
    g = [k.defs(), f'<rect x="20" y="40" width="{W - 40}" height="330" fill="{k.WASH}"/>']
    xs = [200 + i * 295 for i in range(7)]
    names = ["-3", "-2", "-1", "CONTROL", "+1", "+2", "+3"]
    for i, x in enumerate(xs):
        fill = k.HOT if i == 3 else k.COLD
        g.append(f'<rect x="{x - 105}" y="110" width="210" height="190" rx="14" fill="{fill}"/>')
        for d in range(i + 1):
            g.append(f'<circle cx="{x - 78 + d * 26}" cy="140" r="8" fill="white"/>')
        g.append(k.label(x, 345, names[i], 27, anchor="middle", fill=k.INK if i == 3 else k.MUTED, weight=600 if i == 3 else 400))
    g.append(k.label(40, 28, "ONE PLATE · ONE SETTING STEPPED · DOTS PRINTED INTO EACH PIECE", 25, fill=k.MUTED))
    plate = k.svg(W, H, "".join(g), "A plate of seven test pieces seen from above",
                  "Seven pieces in a row. The middle one is the control, printed at the current setting. Three on each side step one setting down and up. Each piece carries a number of raised dots so it can be told apart after it leaves the bed.")
    body = (
        b.head("Trials", "Change one thing.",
               "A print has dozens of settings and every one of them moves the result. A trial that changes two cannot say which one did it.")
        + b.scope("any filament: it is method · the quotes are from PET-GF, PETG and TPU trials", label="Holds for")
        + f'<div style="margin-top:44px">{plate}</div>'
        + b.row(
            b.quote("&hellip;have one control, and have variations in both directions, with whatever you can fit in about a 30 minute to 120 minute print&hellip;", "DEREK · 11 OCTOBER 2026 · PET&#8209;GF", size=43),
            b.quote("Please don&rsquo;t keep doubling down on changes already tried, I would prefer you get back to our normal settings, and pick one specific thing to change&hellip;", "DEREK · 9 OCTOBER 2026 · PET&#8209;GF", size=43),
            b.quote("And I don&rsquo;t want you to keep wasting my time printing the same control over and over again.", "DEREK · 15 OCTOBER 2026 · PET&#8209;GF", size=43),
            gap=60, style="margin-top:44px")
        + b.rulebar(50, 40)
        + '<div class="grid3">'
        + '<div>' + b.block("One control, once", "The control is the current recipe, printed on the same plate as its variations. Once it has been printed and judged it is not printed again.") + "</div>"
        + '<div>' + b.block("About an hour", "A coupon plate that takes an hour gets tried the same evening. A trial that takes a day gets tried once.")
        + b.quote("This amount of TPU costs less than your tokens, so please just start a print once you are ready.", "DEREK · 13 OCTOBER 2026 · TPU", size=38) + "</div>"
        + '<div>' + b.block("Both printers", "When two printers are loaded and clear, the plate is split across them. One sitting loaded and idle is a wasted evening.")
        + b.quote("Both printers are available and its my bed time. Print as you see fit.", "DEREK · 15 OCTOBER 2026", size=38) + "</div>"
        + "</div>"
        + b.rulebar(44, 40)
        + b.row(
            ("0 0 1040px", "<h2>Then write down what happened</h2>"
             '<p class="small">Every print keeps its photographs, the file that was sent, and what Derek said when he held it, word for word. When he says a part is good enough, that goes on record against the part, with the flaw he named.</p>'
             '<p class="small" style="margin:0"><b>Where this book says Still open,</b> it is usually because a trial changed two things at once and worked. The result is real. Which change did it is not known.</p>'),
            b.quote("That worked. There&rsquo;s still a gap, so make a note of it, but I don&rsquo;t want to iterate any further on this right now. It&rsquo;s fine. It&rsquo;s good enough.", "DEREK · 25 OCTOBER 2026", size=43)
            + '<div style="margin-top:30px">' + b.quote("Fixtures we may print again. Trials will never be reprinted, we&rsquo;ll just make new trials instead.", "DEREK · 2 NOVEMBER 2026", size=43) + "</div>",
            gap=80)
        + '<div style="margin-top:30px">' + b.record(b.link("What Derek has tried in hand and said", "hardware/ledger/fitted.json"),
                                                     f'<a href="{b.GITHUB}/commit/5d20beae4">A plate with one control</a>') + "</div>"
    )
    return Page("change-one-thing", "Change one thing", "any", body, right="Trials")


# --------------------------------------------------------------------------- the same question
def same_question():
    M = "Metadata/project_settings.config"
    b.source("petgf", "hardware/printed-parts/petgf.3mf", member=M)
    b.source("reservoir", "hardware/printed-parts/cold-core/reservoir/reservoir.3mf", member=M)
    b.source("tpusleeve", "hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.3mf", member=M)
    b.source("aerofloat", "hardware/printed-parts/cold-core/magnetic-float/all-aero/all-aero-float.3mf", member=M)
    srcs = ["petgf", "reservoir", "tpusleeve", "aerofloat"]

    def each(pointer, unit="", only=None):
        return [(b.setting(s_, pointer) + unit) if (only is None or s_ in only) else "" for s_ in srcs]

    def pair(p1, p2, unit=""):
        return [f"{b.setting(s_, p1)} / {b.setting(s_, p2)}{unit}" for s_ in srcs]

    rows = [
        ("Plate", each("/curr_bed_type")),
        ("Bed", [b.setting("petgf", "/textured_plate_temp/0") + " °C"] + each("/eng_plate_temp/0", " °C")[1:]),
        ("Nozzle width", each("/nozzle_diameter/0", " mm")),
        ("Nozzle heat", each("/nozzle_temperature/0", " °C")),
        ("First layer / the rest", pair("/initial_layer_print_height", "/layer_height", " mm")),
        ("Part fan, least / most", pair("/fan_min_speed/0", "/fan_max_speed/0", " %")),
        ("Fan over an overhang", each("/overhang_fan_speed/0", " %")),
        ("Flow", each("/filament_flow_ratio/0")),
        ("Most plastic per second", each("/filament_max_volumetric_speed/0", " mm³")),
        ("Walls / fill", pair("/wall_loops", "/sparse_infill_density")),
    ]
    heads = [("petgf", "PET-GF", "the enclosure"), ("petg", "Clear PETG", "a reservoir"), ("tpu", "TPU 85A", "a sleeve"), ("aero", "ASA Aero", "a float")]
    thead = "<tr><th></th>" + "".join(
        f'<th style="padding-bottom:16px"><span class="tag" style="background:{b.PARTS[key][2]}">{name}</span>'
        f'<span style="display:block; margin-top:10px; font:400 27px/1.2 \'IBM Plex Mono\', monospace; letter-spacing:.06em; color:var(--faint); text-transform:none">{what}</span></th>'
        for key, name, what in heads) + "</tr>"
    tbody = "".join(
        f'<tr><th style="font-weight:400; color:var(--muted); width:520px">{q}</th>'
        + "".join(f'<td style="font:650 44px/1.2 \'IBM Plex Sans\'; color:var(--ink)">{v}</td>' for v in vals) + "</tr>"
        for q, vals in rows)
    opp = [
        ("Fan", "PET-GF prints with its fan off except over air, and went brittle when the fan was left on. Soft TPU prints with the fan full on, and its overhanging lips curled the moment it was turned down."),
        ("Flow", "The reservoir&rsquo;s recipe feeds a little more plastic than the lines call for. The float&rsquo;s feeds about half, because that plastic foams as it leaves the nozzle."),
        ("Plate", "PET-GF goes on bare textured plate. The other three print on a smooth plate with glue, and clear PETG got there by lifting off the textured one."),
        ("Pace", "Each plastic has a limit on how much can be pushed through the nozzle each second, and the limit sets the speed. Soft TPU&rsquo;s is a small fraction of PET-GF&rsquo;s."),
    ]
    opp_html = "".join(f'<div><h3>{t}</h3><p class="small" style="margin:0">{d}</p></div>' for t, d in opp)
    body = (
        b.head("Before the plastics", "The same question, a different answer.",
               "Four recipes side by side, each read from the project file that owns it. Hardly a row agrees. Settings that are right "
               "for one plastic have failed prints in another, which is why the rest of this book is sorted by plastic.", size=160)
        + b.scope("one part&rsquo;s project file in each plastic · filled in each time the book is bound", label="Read from")
        + f'<table class="grid" style="margin-top:50px"><thead>{thead}</thead><tbody>{tbody}</tbody></table>'
        + b.rulebar(50, 40)
        + f'<div class="grid4">{opp_html}</div>'
        + '<div style="margin-top:50px">'
        + b.quote("There&rsquo;s just so many variables, and you really have to look at the slice and how the lines actually print and what they are connected to and how all the lines of filament are actually laid down and connected and it is just a lot.", "DEREK · 20 OCTOBER 2026", size=50)
        + '</div><div style="margin-top:44px">'
        + b.record(b.link("PET-GF project", "hardware/printed-parts/petgf.3mf"), b.link("Reservoir project", "hardware/printed-parts/cold-core/reservoir/reservoir.3mf"),
                   b.link("TPU sleeve project", "hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.3mf"),
                   b.link("Float project", "hardware/printed-parts/cold-core/magnetic-float/all-aero/all-aero-float.3mf")) + "</div>"
    )
    return Page("the-same-question-a-different-answer", "The same question, a different answer", "any", body, right="Before the plastics")


def pages():
    return [_mine.landings(), _mine.bridge(), height(), coupon(), one_thing(), same_question()]
