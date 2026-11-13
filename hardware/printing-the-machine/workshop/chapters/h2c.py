"""The H2C: the two Bambu Lab printers, and what was learned about running them that does not
belong to one plastic. Each function returns one Page."""
import json
from datetime import datetime, timedelta

import bookkit as b
import svgkit as k
from bookkit import Page

SETTINGS = "Metadata/project_settings.config"
PP = "hardware/printed-parts"
REVIEWS = f"{PP}/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews"
IDSET = f"{PP}/enclosure/display-cover/prints"
RES = f"{PP}/cold-core/reservoir"
MOLD = f"{PP}/zone-c/funnel-mold"
FRONT = f"{PP}/enclosure/enclosure/prints/2026-11-11-front-bottom-D-mark2"
REG = f"{PP}/calibration/dual-nozzle-registration"
SLEEVE = f"{PP}/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2"
STAGGER = f"{REVIEWS}/2026-09-28-shared-circuit-stagger"
CO2 = f"{REVIEWS}/2026-10-04-bulkhead-co2-raised-mark2-v1"
WRAPPED = f"{RES}/prints/2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-right08-z000"
GUIDE = "tools/bambu-printers.md"


# ----------------------------------------------------------------------------- small pieces of this chapter
def grid(heads, rows, widths=None, style=""):
    """A table.grid with a header row. rows are lists of cell HTML; the first cell of each is its row header."""
    w = widths or [None] * len(heads)
    th = "".join(f'<th style="width:{x}px">{h}</th>' if x else f"<th>{h}</th>" for h, x in zip(heads, w))
    body = "".join("<tr>" + "".join(f"<th>{c}</th>" if i == 0 else f"<td>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
    st = f' style="{style}"' if style else ""
    return f'<table class="grid"{st}><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'


def chip(part, text):
    """A plastic's name on its part colour, as the front of the book uses."""
    return f'<span class="tag" style="background:{b.PARTS[part][2]}">{text}</span>'


def lab(text, color="var(--muted)", top=0):
    """A line of small capitals, as the captions use for date, printer and plastic."""
    return (f'<span class="mono" style="display:block; margin-top:{top}px; font-size:27px; line-height:1.35; font-weight:600; '
            f'letter-spacing:.09em; text-transform:uppercase; color:{color}">{text}</span>')


def numbered(items, gap=22, cls="small"):
    """A legend: (number, title, text) rows with the book's numbered discs. A fourth item is the disc's class."""
    out = []
    for item in items:
        n, t, d = item[:3]
        c = item[3] if len(item) > 3 else ""
        out.append(f'<div style="display:flex; gap:22px; margin-bottom:{gap}px"><span class="num {c}">{n}</span>'
                   f'<p class="{cls}" style="margin:0"><b>{t}</b> {d}</p></div>')
    return "".join(out)


def pinned(img, alt, pins, cap_lab="", cap="", keep=100):
    """A photograph at full width with numbered discs on it; keep is the percentage of its height shown, from the top.
    pins: (number, x percent, y percent of the part shown, class). The picture is taken as 4:3."""
    discs = "".join(f'<span class="num on-model {c}" style="left:{x}%; top:{y}%">{n}</span>' for n, x, y, c in pins)
    labs = f'<span class="lab">{cap_lab}</span>' if cap_lab else ""
    return (f'<figure><div style="position:relative; aspect-ratio:400 / {3 * keep}">'
            f'<img src="art/{img}" alt="{alt}" style="display:block; width:100%; height:100%; object-fit:cover; object-position:50% 0">{discs}</div>'
            f'<figcaption class="cap">{labs}{cap}</figcaption></figure>')


def local(utc, fmt="%H:%M:%S"):
    """A UTC reading as the bench clock showed it. The printers are in US Central time, on daylight time until November."""
    t = datetime.fromisoformat(utc)
    return (t - timedelta(hours=5 if (t.month, t.day) < (11, 1) else 6)).strftime(fmt)


# ----------------------------------------------------------------------------- 1 the machines
def machines():
    b.source("h2c-pieces", f"{PP}/enclosure/trial-preparation/pieces.json")
    b.source("h2c-petgf", f"{PP}/petgf.3mf", member=SETTINGS)
    b.source("h2c-reservoir", f"{RES}/prints/2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000/settings.json")
    b.source("h2c-idset", f"{IDSET}/2026-11-08-identification-set-mark1-right-z005/HSM-identification-set-Mark1-right-z005.3mf", member=SETTINGS)
    b.source("h2c-elbow", "future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1/"
             "2026-10-14-compact-single-elbow-siraya85a-overhang10-engineering-right06-z000-mark1.3mf", member=SETTINGS)
    b.source("h2c-float", f"{PP}/cold-core/magnetic-float/all-aero/mark2-print/v2/all-aero-float.3mf", member=SETTINGS)
    gf = b.setting("h2c-pieces", "/pieces/front-bottom/nozzle/diameter_mm")
    gf2 = b.setting("h2c-pieces", "/pieces/tube-collars/nozzle/diameter_mm")
    ids = b.setting("h2c-pieces", "/pieces/labels/nozzle/diameter_mm")
    tpu = b.setting("h2c-pieces", "/pieces/pump-elbows/nozzle/diameter_mm")
    res = b.setting("h2c-reservoir", "/nozzle_diameter/0")
    aero = b.setting("h2c-float", "/nozzle_diameter/1")
    photo = b.asset("h2c-inside-mark1.jpg", f"{IDSET}/2026-11-06-identification-set-mark1-z000/physical-result/photo-3.jpg")

    def row(part, name, job, side, plate, feed, dry):
        return [f'{chip(part, name)}<span class="tiny" style="display:block; margin-top:10px; font-weight:400; white-space:nowrap">{job}</span>',
                side, plate, feed, dry]

    glue = ", glued"
    rows = [
        row("petgf", "PET-GF", "Front-bottom · Mark2 · 11 November 2026",
            f"<b>Left, {gf} mm</b>, hardened. A second colour: right {gf2} mm.",
            b.setting("h2c-petgf", "/curr_bed_type"),
            "The left outside spool: 1 kg straight out of the dryer, 3 kg out of a sealed box with an axle.",
            "SUNLU E2, only if the spool has taken up moisture."),
        row("petg", "PETG clear", "Reservoirs · Mark 1 · 26 October 2026",
            f"<b>Left, {res} mm.</b>", b.setting("h2c-reservoir", "/curr_bed_type") + glue,
            "An AMS 2 Pro, which carries on to its next spool when one runs out.", "The same AMS 2 Pro, spool in place."),
        row("petg", "PETG colours", "Labels · Mark 1 · 8 November 2026",
            f"<b>{ids} mm, both sides.</b> Black left; four colours on four right hotends.",
            b.setting("h2c-idset", "/curr_bed_type") + glue,
            "Black from the AMS HT, the other four from an AMS 2 Pro.", "Those two units."),
        row("tpu", "TPU", "Pump elbows · Mark2 · 22 October 2026",
            f"<b>Right, {tpu} mm.</b>", b.setting("h2c-elbow", "/curr_bed_type") + glue,
            "The right outside spool, in a sealed box it turns freely in. No AMS feeds TPU.", "AMS HT."),
        row("aero", "ASA Aero", "Level float · Mark2 · 3 October 2026",
            f"<b>Right, {aero} mm</b>, hardened.", b.setting("h2c-float", "/curr_bed_type") + glue,
            "The right outside spool, from a sealed drybox.", "SUNLU E2."),
        row("petcf", "PET-CF", "Faucet, since retired · May and June 2026",
            "<b>Left, 0.6 mm</b> tungsten carbide, later diamond.", "Textured plate", "The SUNLU E2.", "SUNLU E2."),
    ]
    table = grid(["Plastic · its print", "Side and nozzle", "Plate", "Fed from", "Dried in"], rows, [640, 400, 290, 540, 300], "table-layout:fixed")
    legend = numbered([
        (1, "The left hotend is fixed.", "It is the hotend of Bambu&rsquo;s H2D, so nozzles sold for that printer fit it: hardened steel, tungsten carbide, diamond."),
        (2, "The right hotend swaps.", "It is heated by induction and gripped by pincers, and the printer trades it for another from a rack during a print. "
            "Only hotends made for the H2C fit. Here spares marked 0.2 wait in the rack."),
        (3, "The plate is changed for the plastic.", "This one is the smooth Engineering Plate, spread with glue. The other kind is textured PEI."),
    ])
    body = (
        b.head("The machines", "Each plastic has its side, plate and feed.",
               "Both printers are Bambu Lab H2Cs, with two hotends each. A print settled which side, plate and feed every plastic gets.", size=146, top=56)
        + b.scope("Mark 1 and Mark2 · every plastic the machine is made of · each row of the table is one dated print")
        + b.row(
            ("0 0 880px", pinned(photo, "The inside of a printer: a black plate with first layers in black and white, the toolhead at the back and spare hotends in a rack at the right",
                                 [(1, 23, 9, ""), (2, 93.5, 34, ""), (3, 85, 56, "")], "6 November 2026 · Mark 1 · PETG",
                                 "Inside Mark 1, just after a five-colour print was stopped in its first layers.", keep=77)),
            legend
            + '<p class="small" style="margin:30px 0 0"><b>Mark 1</b> was ordered on 22 March 2026. It was called H2C until 6 October and still answers to that name on the '
            'network. <b>Mark2</b> was ordered on 4 May. Neither stays loaded one way: plates, nozzles and spools are changed for the job, so every job&rsquo;s record names its own.</p>',
            gap=70, style="margin-top:34px")
        + '<h2 style="margin-top:36px">Which plastic goes where</h2>'
        + table
        + b.row(
            '<p class="small" style="margin:0"><b>Fibre goes left, mostly.</b> Glass and carbon fibre wear a nozzle away. Tungsten carbide and diamond nozzles stand up to them '
            'and are made only for the left side, so the ledger&rsquo;s rule is that abrasive plastic runs there. The record also holds PET-GF through the '
            'right side&rsquo;s hardened steel: a whole white faucet on Mark2 on 15 October 2026, and the second colour of every label.</p>'
            + b.still_open("Nothing in the record measures the wear on a right-side nozzle after PET-GF."),
            ("0 0 800px", b.quote("So far, the diamond PCD has been the toughest and most reliable, in other sizes.", "DEREK · 11 SEPTEMBER 2026", size=40)
             + '<div style="margin-top:30px">'
             + b.record(b.link("What fits which side, what dries where", "hardware/ledger/tools.md", anchor="which-hotends-fit-an-h2c"),
                        b.link("Every piece, its printer and hotend", f"{PP}/enclosure/trial-preparation/pieces.json"),
                        b.link("The white faucet on the right", f"{PP}/faucet/sculpted/prints/2026-10-15-white-right-mark2/README.md")) + "</div>"),
            gap=70, style="margin-top:32px")
    )
    return Page("each-plastic-has-its-side-plate-and-feed", "The H2C: each plastic has its side, plate and feed", "h2c", body, right="The machines")


# ----------------------------------------------------------------------------- 2 two nozzles
def _coupon(S, ex, ey, hx, hy):
    """The registration coupon as it prints when the right nozzle lands (ex, ey) mm from where the printer
    believes it is. Slate is the left nozzle's line of each pair, orange the right nozzle's. Stations hx
    (top row) and hy (bottom row) are ringed. Geometry is the coupon's own, 110 by 39 mm, at S pixels per mm."""
    W, H = 110 * S + 8, 39 * S + 8

    def X(mm):
        return 4 + (mm + 55) * S

    def Y(mm):
        return 4 + (20 - mm) * S

    def bar(x, top, w, h, fill):
        return f'<rect x="{k.n(X(x))}" y="{k.n(Y(top))}" width="{k.n(w * S)}" height="{k.n(h * S)}" fill="{fill}"/>'

    g = [f'<rect x="4" y="4" width="{k.n(110 * S)}" height="{k.n(39 * S)}" rx="6" fill="{k.WASH}" stroke="{k.FAINT}" stroke-width="3"/>']
    for i in range(15):
        x = (i - 7) * 7.0
        rx, ry = -1.05 + 0.05 * i + ex, 0.35 + 0.05 * i + ey
        g.append(bar(x - 0.45, 14.2, 0.9, 3.4, k.COLD) + bar(x + rx - 0.45, 9.8, 0.9, 3.4, k.HOT))
        g.append(bar(x - 3.0, -4.55, 2.6, 0.9, k.COLD) + bar(x + 0.4, -5 + ry + 0.45, 2.6, 0.9, k.HOT))
        for yy in (17.0, -10.0):
            g.append(k.label(X(x), Y(yy) + 9, str(i), 25, anchor="middle", fill=k.MUTED))
    g.append(k.label(X(-52.4), Y(2) + 22, "X", 46, fill=k.MUTED, weight=600) + k.label(X(-52.4), Y(-15) + 22, "Y", 46, fill=k.MUTED, weight=600))
    xs, ys = (hx - 7) * 7.0, (hy - 7) * 7.0
    ring = 'fill="none" stroke="{c}" stroke-width="5" rx="10"'
    g.append(f'<rect x="{k.n(X(xs - 1.7))}" y="{k.n(Y(15.0))}" width="{k.n(3.4 * S)}" height="{k.n(9.4 * S)}" {ring.format(c=k.INK)}/>')
    g.append(f'<rect x="{k.n(X(ys - 3.8))}" y="{k.n(Y(-3.2))}" width="{k.n(7.6 * S)}" height="{k.n(3.6 * S)}" {ring.format(c=k.INK)}/>')
    g.append(k.label(X(xs), Y(2.2), "LINES UP AT THE TWELFTH PAIR", 25, anchor="middle", fill=k.INK, weight=600) + k.line(X(xs), Y(3.9), X(xs), Y(5.6)))
    g.append(k.label(X(ys), Y(-0.4), "THE EIGHTH, PERHAPS", 25, anchor="middle", fill=k.INK, weight=600) + k.line(X(ys), Y(-1.2), X(ys), Y(-3.2)))
    return k.svg(W, H, "".join(g), "The registration coupon, drawn as it printed",
                 "A flat plate with two rows of fifteen numbered pairs of short lines. In each pair one line is laid by the left nozzle and one by "
                 "the right. In the top row the right nozzle's line is drawn a little further over in each pair, and in the printed coupon the "
                 "pairs come into line at the twelfth. In the bottom row they come into line at about the eighth.")


def _pairs(M, ex, picks):
    """Pairs of the coupon's top row enlarged M pixels per mm: the end of the left nozzle's line over the start of the right's."""
    pw = 300
    names = {1: "SECOND", 10: "ELEVENTH", 11: "TWELFTH", 12: "THIRTEENTH"}
    g = []
    for n, i in enumerate(picks):
        ox = n * pw + pw / 2
        mm = -1.05 + 0.05 * i + ex
        r = mm * M
        g.append(k.line(ox, 8, ox, 296, k.FAINT, 2, dash="6 8"))
        g.append(f'<rect x="{k.n(ox - 0.45 * M)}" y="16" width="{k.n(0.9 * M)}" height="120" fill="{k.COLD}"/>')
        g.append(f'<rect x="{k.n(ox + r - 0.45 * M)}" y="168" width="{k.n(0.9 * M)}" height="120" fill="{k.HOT}"/>')
        hit = abs(mm) < 0.001
        g.append(k.label(ox, 336, names[i], 26, anchor="middle", fill=k.INK, weight=600))
        note = "IN LINE" if hit else f"{abs(mm):.2f} MM {'LEFT' if mm < 0 else 'RIGHT'}"
        g.append(k.label(ox, 372, note, 24, anchor="middle", fill=k.HOT if hit else k.MUTED, weight=600 if hit else 400))
    return k.svg(pw * len(picks), 384, "".join(g), "Four pairs of the top row, enlarged",
                 "Each pair is the end of the left nozzle's line above the start of the right nozzle's line. In the second pair the lower line "
                 "sits half a millimetre to the left. In the eleventh and thirteenth it is a twentieth of a millimetre to either side. In the twelfth the two are in line.")


def nozzles():
    b.source("h2c-reg", f"{REG}/mark2-registration.json")
    b.source("h2c-coupon", f"{REG}/geometry-check.json")
    cx, cy = b.setting("h2c-reg", "/white_correction_mm/X"), b.setting("h2c-reg", "/white_correction_mm/Y")
    step = b.setting("h2c-coupon", "/candidate_spacing_mm")
    ex, ey = -b.value("h2c-reg", "/white_correction_mm/X"), -b.value("h2c-reg", "/white_correction_mm/Y")
    hx, hy = b.value("h2c-reg", "/selected_indices/X"), b.value("h2c-reg", "/selected_indices/Y")
    photo = b.asset("h2c-two-colour-labels.jpg", f"{CO2}/physical-result.jpg")
    body = (
        b.head("Two nozzles on one part", "Measure where the second nozzle lands.",
               "Two nozzles sharing a part must lay their lines side by side. The printer measures the gap between its own nozzles before every job. "
               "On Mark2 that still left white lettering out of its black pockets.", size=160, top=56)
        + b.scope("PET-GF · Mark2 · textured PEI · both 0.4 mm · 29 September 2026", not_tried="Mark 1, or any other nozzle pair")
        + b.row(
            ("0 0 1724px", f'<figure>{_coupon(15.6, ex, ey, hx, hy)}<figcaption class="cap"><span class="lab">The coupon, drawn as it printed</span>'
                           '<b style="color:var(--cold)">Slate</b> is the left nozzle, laid where it was drawn. <b style="color:var(--hot)">Orange</b> is the right nozzle. '
                           'No photograph of the printed coupon was kept: this is its geometry, with the right nozzle moved by the error Derek read off it.</figcaption></figure>'),
            b.stat(f'{cx} <span>mm</span>', "to move the right nozzle&rsquo;s paths along the bed, left to right.")
            + '<div style="height:34px"></div>'
            + b.stat(f'+{cy} <span>mm</span>', "to move them front to back.")
            + '<p class="tiny" style="margin-top:34px">Thirteen minutes and under six grams of plastic to find out.</p>',
            gap=56, style="margin-top:34px")
        + b.rulebar(30, 28)
        + b.row(
            ("0 0 1200px", f'<figure>{_pairs(110, ex, [1, 10, 11, 12])}</figure>'),
            '<h2>How it is read</h2>'
            f'<p class="small">Each pair is drawn end to end, with the right nozzle&rsquo;s line {step} mm further over at every pair along the row. The pair '
            'that prints as one straight line names the shift. The lines are 0.9 mm wide, so neighbours differ by an eighteenth of a line.</p>'
            '<p class="small" style="margin:0">The first coupon ran out of range: its best pairs were the last in each row. A second carried the range further. '
            'It numbers its pairs from 0 and Derek counted from 1; his &ldquo;fourth from the right&rdquo; settled which he meant.</p>',
            gap=70)
        + b.rulebar(28, 32)
        + b.row(
            ("0 0 620px", b.fig(photo, "A black nameplate with white lettering and a QR code, and red, blue, white and black label rings with contrasting letters",
                                "4 October 2026 · Mark2 · PET-GF",
                                "Two-colour pieces printed with the correction. Of the CO2 and SODA rings, printed that day, the record says the white letters sit in their recesses with no visible offset.",
                                h=450, pos="50% 6%")),
            '<h2>Where the correction goes</h2>'
            '<p class="small">Into the slice, never the drawing. The slicer is told the right nozzle sits that far from where the printer believes, and it '
            'moves every right-nozzle path to suit. The model stays as drawn. Each corrected file is compared, path by path, with an uncorrected slice of itself.</p>'
            '<h2 style="margin-top:30px">What it belongs to</h2>'
            '<p class="small" style="margin:0">One printer and one pair of hotends. Change a hotend, or how the printer calibrates, and the coupon is printed again.</p>',
            ("0 0 620px", b.quote("The X-Y alignment between the two nozzles seems really good.", "DEREK · 8 NOVEMBER 2026 · MARK 1, PETG, 0.2 MM, NO COUPON", size=40)
             + b.still_open("The front-to-back reading is tentative: slight oozing made neighbouring pairs hard to tell apart. No print has measured the error left after the correction.")
             + '<div style="margin-top:28px">'
             + b.record(b.link("The coupon and how to read it", f"{REG}/README.md"),
                        b.link("The reading", f"{REVIEWS}/2026-09-29-registration-mark2-v3/physical-result.json"),
                        b.link("The first coupon", f"{REVIEWS}/2026-09-29-registration-mark2-v2/physical-result.json"),
                        b.link("The nameplate that showed it", f"{REVIEWS}/2026-09-29-nameplate-all-ink-raised-mark2-v4/physical-result.json")) + "</div>"),
            gap=60)
    )
    return Page("measure-where-the-second-nozzle-lands", "The H2C: measure where the second nozzle lands", "h2c", body, right="Two nozzles")


# ----------------------------------------------------------------------------- 3 one breaker
def _stagger():
    """The two pairs of starts on the night of 27 September 2026, drawn from the trial's own readings."""
    folder = b.ROOT / STAGGER
    obs = json.loads((folder / "observation.json").read_text())
    restart = obs["staggered_restart"]["printers"]
    t0, t1 = restart["Mark2"]["accepted_at_utc"], restart["H2C"]["accepted_at_utc"]
    base = datetime.fromisoformat(t0)
    readings = [json.loads((folder / n).read_text()) for n in ("mark2-during-stagger.json", "mark2-before-h2c-send.json")]
    readings += json.loads((folder / "startup-reading.json").read_text())
    for group in json.loads((folder / "warmup-readings.json").read_text()):
        readings += group
    series = {"Mark2": [], "H2C": []}
    for r in readings:
        when = datetime.fromisoformat(r.get("observed_at") or r["observed_at_utc"])
        series[r["printer"]].append(((when - base).total_seconds() / 60, r["bed_temper"]))
    for s in series.values():
        s.sort()
    first = obs["original_jobs"]
    gap0 = obs["original_launch_spacing_seconds"] / 60
    gap1 = obs["staggered_restart"]["accepted_launch_spacing_seconds"] / 60

    W, H, x0, per = 2170, 800, 300, 165.0

    def X(t):
        return x0 + t * per

    g = []
    # the pair that tripped
    g.append(k.label(0, 34, f"{local(first[0]['accepted_at_utc'], '%H:%M')} ON 27 SEPTEMBER · STARTED {round(gap0 * 60)} SECONDS APART", 27, fill=k.BAD, weight=600))
    for name, t, y in (("MARK2", 0.0, 78), ("MARK 1", gap0, 150)):
        g.append(k.label(0, y + 34, name, 30, fill=k.INK, weight=600))
        g.append(k.missing(X(t), y, X(11.2), y + 50))
        g.append(f'<rect x="{k.n(X(t) - 6)}" y="{k.n(y - 8)}" width="12" height="66" fill="{k.INK}"/>')
    g.append(k.label(X(3.2), 112, "THE BREAKER TRIPPED. BOTH JOBS WERE LOST AT LAYER 0.", 27, fill=k.BAD, weight=600))
    g.append(k.label(X(3.2), 184, "NOBODY RECORDED THE MOMENT, OR THE CURRENT.", 27, fill=k.BAD))
    # the pair that ran
    top = 300
    mins, secs = int(gap1), round((gap1 - int(gap1)) * 60)
    g.append(k.label(0, top - 26, f"{local(t0, '%H:%M')} ON 28 SEPTEMBER · THE SAME TWO JOBS, STARTED {mins} MINUTES {secs} SECONDS APART", 27, fill=k.INK, weight=600))

    def lane(name, key, start, y):
        lo, hi = y + 150, y + 30          # 20 C and 80 C

        def T(c):
            return lo - (c - 20) / 60 * (lo - hi)

        g.append(k.label(0, y + 96, name, 30, fill=k.INK, weight=600))
        g.append(k.line(X(start), lo + 22, X(11.2), lo + 22, k.FAINT, 3))
        g.append(f'<rect x="{k.n(X(start) - 6)}" y="{k.n(hi - 14)}" width="12" height="{k.n(lo - hi + 36)}" fill="{k.INK}"/>')
        pts = series[key]
        for (ta, ca), (tb, cb) in zip(pts, pts[1:]):
            rising = cb > ca + 1
            seen = tb - ta < 1.0
            g.append(k.line(X(ta), T(ca), X(tb), T(cb), k.HOT if rising else k.COLD, 12 if seen else 6, "" if seen else "14 12"))
        for i, (t, c) in enumerate(pts):
            g.append(f'<circle cx="{k.n(X(t))}" cy="{k.n(T(c))}" r="11" fill="white" stroke="{k.INK}" stroke-width="5"/>')
            before = pts[i - 1][1] if i else None
            last = i == len(pts) - 1
            if c != before and not last:
                g.append(k.label(X(t), T(c) - 24, f"{round(c)} °C", 25, anchor="middle", fill=k.INK, weight=600))
            elif c != before:
                g.append(k.label(X(t) + 24, T(c) + 9, f"{round(c)} °C", 25, fill=k.INK, weight=600))
        return T

    lane("MARK2", "Mark2", 0.0, top)
    lane("MARK 1", "H2C", gap1, top + 210)
    g.append(k.label(X(0) + 14, top + 18, f"ACCEPTED {local(t0)}", 24, fill=k.MUTED))
    g.append(k.label(X(gap1) + 14, top + 228, f"ACCEPTED {local(t1)}", 24, fill=k.MUTED))
    g.append(k.label(X(4.78), top + 150, "NOT WATCHED HERE", 24, anchor="middle", fill=k.MUTED))
    axis = top + 430
    g.append(k.line(X(0), axis, X(11.2), axis, k.INK, 3))
    for m in range(0, 12):
        g.append(k.line(X(m), axis, X(m), axis + 14, k.INK, 3))
        g.append(k.label(X(m), axis + 46, str(m), 25, anchor="middle", fill=k.MUTED))
    g.append(k.label(X(11.2), axis - 16, "MINUTES AFTER MARK2 TOOK ITS JOB", 24, anchor="end", fill=k.MUTED))
    return k.svg(W, H, "".join(g), "Two pairs of printer starts on one circuit",
                 "Above, two starts 54 seconds apart, after which the breaker tripped and both jobs were lost. Below, the same two jobs started "
                 "3 minutes 56 seconds apart, with each printer's bed temperature as it was read every half minute or so. The first printer's bed "
                 "is at 80 degrees before the second printer's bed begins to heat."), gap0, gap1


def breaker():
    b.source("h2c-frontjob", f"{FRONT}/print-job.json")
    drawing, gap0, gap1 = _stagger()
    apart = b.setting("h2c-frontjob", "/launch/shared_circuit/interval_s")
    body = (
        b.head("Power", "Start the second printer three minutes after the first.",
               "Both printers plug into one household circuit. Started within a minute of each other, they tripped its breaker and both jobs were lost. "
               "Started four minutes apart, the same two jobs ran to the end.", size=150, top=56)
        + b.scope("Mark 1 and Mark2 on one circuit · both printing black PET-GF from the left 0.4 mm · the night of 27 September 2026",
                  not_tried="any gap between one minute and four")
        + f'<figure style="margin-top:40px">{drawing}<figcaption class="cap"><span class="lab">What the printers reported</span>'
          'Each dot is a bed temperature one of the printers reported. <b style="color:var(--hot)">Orange</b> is a bed heating, '
          '<b style="color:var(--cold)">slate</b> a bed holding its temperature. With the gap, Mark2&rsquo;s bed was already at 80 °C when Mark 1&rsquo;s began to climb.</figcaption></figure>'
        + b.rulebar(38, 36)
        + b.row(
            b.block("What happened", "Two display covers, one on each printer, were sent 54 seconds apart late on 27 September 2026. The breaker tripped. "
                    "When the power came back both printers reported their job failed at layer 0, and neither picked it up again. "
                    "Derek had seen the same thing when he started them by hand.")
            + b.block("A cut mid-print is different", "Two days earlier both printers had been unplugged by accident. Mark 1 was part of the way through a quarter of the "
                      "enclosure. It carried on when the power returned, and Derek could see no mark where it had stopped."),
            b.block("What we do", "After one printer accepts a job, wait at least three minutes before starting or resuming the other. A resume counts as a start. "
                    "After a power cut, read both printers first: a job that is still running needs nothing sent.")
            + b.block("Who keeps the time", "The sending tool stops two sends colliding in the app. It does not keep this interval. That is done by hand, and both "
                      f"start times go in the record. The enclosure quarter of 11 November 2026 records that Mark 1 had started {apart} seconds before it."),
            ("0 0 560px",
             b.stat(f'{round(gap0 * 60)} <span>seconds</span>', "between the two starts that tripped the breaker.", hot=True)
             + '<div style="height:30px"></div>'
             + b.stat(f'{int(gap1)}:{round((gap1 - int(gap1)) * 60):02d}', "minutes and seconds between the two that ran.")
             + b.still_open("Three minutes is Derek&rsquo;s figure, from experience. One run at just under four is all that is on record. Nothing has measured the "
                            "current, and the readings only fit the two beds heating together. They do not prove it.")),
            gap=64)
        + '<div style="margin-top:36px">'
        + b.record(b.link("The trial", f"{STAGGER}/README.md"),
                   b.link("Its bed readings", f"{STAGGER}/warmup-readings.json"),
                   b.link("The rule as written", GUIDE, anchor="shared-circuit-startup-spacing"),
                   b.link("The power cut two days before", GUIDE, anchor="power-loss-recovery"),
                   b.link("Both start times in a job record", f"{FRONT}/print-job.json")) + "</div>"
    )
    return Page("start-the-second-printer-three-minutes-after-the-first", "The H2C: start the second printer three minutes after the first", "h2c", body, right="Power")


# ----------------------------------------------------------------------------- 4 sending
def _jobcard(head, number, note, tone):
    edge = {"plain": "4px solid var(--line)", "bad": "5px dashed var(--bad)", "hot": "10px solid var(--hot)"}[tone]
    ink = {"plain": "var(--ink)", "bad": "var(--ink)", "hot": "var(--hot)"}[tone]
    top = {"plain": "var(--muted)", "bad": "var(--bad)", "hot": "var(--hot)"}[tone]
    return (f'<div style="flex:1 1 0; padding:34px 36px 32px; border:{edge}">{lab(head, top)}'
            f'<p class="mono" style="margin:16px 0 14px; font-size:92px; line-height:1; font-weight:600; letter-spacing:-.02em; color:{ink}">{number}</p>'
            f'<p class="tiny" style="margin:0">{note}</p></div>')


def sending():
    b.source("h2c-refused", f"{CO2}/rejected-send.json")
    b.source("h2c-accepted", f"{CO2}/launch.json")
    old = b.setting("h2c-refused", "/printer_state_after/job_id_unchanged")
    new = b.setting("h2c-accepted", "/reading/printer_task_id")
    arrow = '<div style="flex:none; align-self:center; font:700 80px/1 \'IBM Plex Sans\'; color:var(--faint)">&rarr;</div>'
    strip = ('<div style="display:flex; gap:26px; align-items:stretch; margin-top:40px">'
             + _jobcard("Before", old, "The printer keeps the number of its last job until a new one starts.", "plain") + arrow
             + _jobcard("01:05 · sent · refused", old, "The dialog closed. The number did not move. The printer had answered &ldquo;loading not completed&rdquo;.", "bad") + arrow
             + _jobcard("01:32 · sent again", new, "A new number, the file&rsquo;s own name, and the printer preparing. That is a send.", "hot")
             + "</div>")
    ways = [
        ("21 September 2026 · Mark2", "It vanished", "Two sends went out while the printer was loading filament, its nozzle held hot with no job. Each time the "
         "dialog closed and nothing started. The third, after the heat was off, ran. Three more vanished over the next two days, for no reason anyone found."),
        ("4 October 2026 · Mark2", "Refused: still hot", "Just after a spool was loaded, the printer&rsquo;s heater targets already read zero. Its nozzle was still at 232 °C, and it "
         "refused the job. Twenty-seven minutes later it took the same file. That is the send drawn above."),
        ("12 October 2026 · Mark2", "Refused: seen before", "A file that had been started and cancelled was refused as invalid when it was sent again. The identical file "
         "under a new name was accepted."),
        ("20 September 2026", "The other printer", "The send dialog offered Mark 1 three times after Mark2&rsquo;s page had been opened. The tool now reads the name in the "
         "dialog and changes it before it presses anything else."),
    ]
    cards = "".join(f'<div>{lab(d)}<h2 style="margin:10px 0 12px">{t}</h2><p class="small" style="margin:0">{x}</p></div>' for d, t, x in ways)
    steps = numbered([
        (1, "Read both printers.", "Finished and failed both mean idle. A heater still set above zero means wait."),
        (2, "Open the checked file in Bambu Connect", "by pressing its controls the way a screen reader would. The printer ignores a start from any program Bambu has not signed."),
        (3, "Check the dialog:", "the printer named, the spool on each nozzle by type and colour, timelapse and bed levelling on, both calibrations on auto."),
        (4, "Press Send once.", ""),
        (5, "Listen to the printer.", "A new job number, the file&rsquo;s name, preparing or running, no error. An unclear send is never simply repeated."),
    ], gap=18)
    body = (
        b.head("Sending a job", "A send is proven only by a new job number.",
               "The printer starts a job only when Bambu&rsquo;s own program asks. So an agent presses that program&rsquo;s buttons, then listens to the "
               "printer itself. Several times the press did nothing, and nothing on the screen said so.", size=150, top=56)
        + b.scope("Mark2 · PET-GF jobs · sent through Bambu Connect · autumn 2026", not_tried="the same refusals on Mark 1")
        + strip
        + '<p class="cap" style="margin-top:14px"><span class="lab">4 October 2026 · Mark2 · one label ring, sent twice</span></p>'
        + b.rulebar(30, 30)
        + '<h3>Four ways a send has gone wrong</h3>'
        + f'<div class="grid4" style="margin-top:16px; gap:44px">{cards}</div>'
        + b.rulebar(34, 32)
        + b.row(
            '<h2 style="margin-bottom:20px">How an agent sends a job</h2>' + steps,
            ("0 0 900px",
             b.quote("If I tell you to print something, you print something. I will not tell you to print something if the plate is not clear.", "DEREK · 22 SEPTEMBER 2026", size=41)
             + '<div style="margin-top:28px">' + b.quote("There is no queue. That is some agent&rsquo;s invention&hellip;", "DEREK · 23 SEPTEMBER 2026", size=41) + "</div>"
             + '<p class="small" style="margin:28px 0 0">So nobody asks whether the bed is clear, or how much is left on the spool. A request to print is the answer to both.</p>'
             + b.still_open("Why three sends vanished with nothing loading, and why a cancelled file&rsquo;s name is refused, are not known.")),
            gap=70)
        + '<div style="margin-top:30px">'
        + b.record(b.link("How sending works, and each failure", GUIDE, anchor="print-submission"),
                   b.link("The refused send", f"{CO2}/rejected-send.json"),
                   b.link("The sends that vanished", f"{PP}/fixtures/fake-countertop/print-jobs.json")) + "</div>"
    )
    return Page("a-send-is-proven-only-by-a-new-job-number", "The H2C: a send is proven only by a new job number", "h2c", body, right="Sending a job")


# ----------------------------------------------------------------------------- 5 overload
def overload():
    b.source("h2c-idresult", f"{IDSET}/2026-11-08-identification-set-mark1-right-z005/physical-result.json")
    lift = b.setting("h2c-idresult", "/print_setup/right_z_trim_mm")
    note = b.asset("h2c-overload-message.jpg", f"{IDSET}/2026-11-06-identification-set-mark1-z000/physical-result/photo-1.jpg")
    hotend = b.asset("h2c-removed-hotend.jpg", f"{IDSET}/2026-11-06-identification-set-mark1-z000/drying/physical-result/photo-4.jpg")
    causes = [
        (1, "Filament left loaded and idle", "28 September 2026 · Mark 1 · PET-GF · left 0.4 mm",
         "A print paused before its first layer. The printer had sat for a while with filament in it.",
         "Cut the filament at the spool. Unload at the touchscreen. Pull the whole cut piece out. Load the fresh end and resume. The print ran its 252 layers.",
         "Derek had done this a few times by then. He suspects the length left in the feed path takes up moisture. Nothing has tested that."),
        (2, "A hotend that would not pass plastic", "11 September 2026 · &ldquo;the H2C&rdquo;, as Mark 1 was called · PET-GF · left 0.4 mm",
         "The print paused. Derek cleaned the outside of the hotend and resumed, and it paused again. His words for the message that day were &ldquo;extruder motor overheating&rdquo;.",
         "Another hotend. He swapped in the spare, resumed, and the same job finished.",
         "The hotend that came off has not been cold-pulled, so &ldquo;clogged&rdquo; is still a suspicion."),
        (3, "A nozzle too close to the plate", "6 to 8 November 2026 · Mark 1 · white PETG · right 0.2 mm · glued Engineering Plate",
         "Four tries stopped on this message, at about the same spot in the first layer. Drying the spools twice, a spare hotend and rethreading the filament changed nothing.",
         f"Lifting the right-side nozzles {lift} mm off the plate. The fifth try finished.",
         "The PETG part tells this one in full."),
    ]
    cols = "".join(
        f'<div><div style="display:flex; align-items:center; gap:20px; margin-bottom:14px"><span class="num hot">{n}</span><h2 style="margin:0; font-size:46px">{t}</h2></div>'
        f'{lab(w)}<p class="small" style="margin:14px 0 14px">{what}</p>'
        f'<p class="small" style="margin:0 0 14px"><b>What fixed it.</b> {fix}</p><p class="tiny" style="margin:0">{rest}</p></div>'
        for n, t, w, what, fix, rest in causes)
    way_in = numbered([(1, "", "Take off the back fan."), (2, "", "Unplug the hotend&rsquo;s flat cable."), (3, "", "Unscrew its power leads."),
                       (4, "", "Only then undo its mounting screws."), (5, "", "Lift off the plate in front of the motors. The jam is there.")], gap=12)
    body = (
        b.head("&ldquo;The extrusion motor is overloaded&rdquo;", "One message. Three causes.",
               "The printer feels how hard its motor has to push the filament, and pauses when that is too hard. The message is the same whatever is in the way. "
               "We have had three different things in the way.", size=150, top=56)
        + b.scope("recorded on Mark 1, three times · PET-GF on a left 0.4 mm, twice · white PETG on a right 0.2 mm, once")
        + b.row(
            ("0 0 1240px", b.fig(note, "Two phone notifications from the printer: task paused and task cancelled, each reading that the extrusion motor is overloaded",
                                 "6 November 2026 · Mark 1 · on Derek&rsquo;s phone", "All the printer says. The same words arrived for all three causes below.", h=480, pos="50% 55%")),
            b.fig(hotend, "A hotend held in the hand, with a ball of white plastic and fine threads stuck to its tip", "7 November 2026 · Mark 1 · white PETG",
                  "The hotend Derek took off after the second stop. It looked like the cause, and a spare went on.", h=480, pos="35% 44%", zoom=150),
            gap=50, style="margin-top:36px")
        + f'<div class="grid3" style="margin-top:36px; gap:56px">{cols}</div>'
        + b.rulebar(36, 34)
        + b.row(
            '<h2 style="font-size:66px; line-height:1.05; margin-bottom:18px">Never push a clog from below.</h2>'
            '<p class="small">In May 2026, during the first PET-CF faucet attempts, filament jammed in the feed gears above the right hotend of the only printer. '
            'A probe pushed up from below to free it snapped the pincers that grip that hotend and cut the heater&rsquo;s flat cable.</p>'
            '<p class="small" style="margin:0">On the evening of 4 May a replacement extruder was ordered, and an hour later a second printer. That printer is Mark2.</p>',
            ("0 0 600px", '<h3>The way in, from the front</h3><div style="margin-top:14px">' + way_in + "</div>"),
            ("0 0 620px", b.quote("Well, it broke the same way again.", "DEREK · 7 NOVEMBER 2026 · AFTER THE SPARE HOTEND", size=44)
             + '<p class="small" style="margin:26px 0 0">A fouled hotend can be the result of the trouble. On the fourth stop he asked for one change only, and it was the one that worked.</p>'
             + '<div style="margin-top:26px">'
             + b.record(b.link("The idle-filament recovery", f"{REVIEWS}/2026-09-28-display-receiver-retention-h2c-v2/startup-recovery.json"),
                        b.link("The swapped hotend", f"{PP}/enclosure/enclosure/print-log.md"),
                        b.link("The lifted nozzle", f"{IDSET}/2026-11-08-identification-set-mark1-right-z005/README.md"),
                        b.link("The clog and the way in", f"{PP}/faucet/faucet-shell/print-log.md")) + "</div>"),
            gap=64)
    )
    return Page("one-message-three-causes", "The H2C: one overload message, three causes", "h2c", body, right="Overload")


def pages():
    return [machines(), nozzles(), breaker(), sending(), overload()]
