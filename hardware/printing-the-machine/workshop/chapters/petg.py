"""PETG: the plastic for the parts that hold liquid, plus small parts and molds. Each function
returns one Page; pages() gives them in reading order."""
import math

import bookkit as b
import svgkit as k
from bookkit import Page
from proj import projector
from chapters import _mine

R = "hardware/printed-parts/cold-core/reservoir"
P = R + "/prints"
ID = "hardware/printed-parts/enclosure/display-cover/prints"
MOLD = "hardware/printed-parts/zone-c/funnel-mold"
TEAL = "#1f8aa5"

MAY_WATER = P + "/2026-10-21-mark1-may-water-right08-z000"
WALLS_ONLY = P + "/2026-10-21-mark1-walls-only-right08-z000-a4"
T59 = P + "/2026-10-22-mark1-walls-t59-right08-z000"
FIVE_WALLS = P + "/2026-10-22-mark1-flow105-overlap30-right08-z000"
TEMP260 = P + "/2026-10-24-mark1-flow105-overlap30-temp260-right08-z000"
LIFTED = P + "/2026-10-25-mark1-right-flow105-overlap30-temp260-right08-z000"
ENG_RIGHT = P + "/2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-right08-z000"
ENG_LEFT = P + "/2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-left08-z000"
LEFT50 = P + "/2026-10-26-mark1-left-engineering-flow105-overlap50-temp260-left08-z000"
RIGHT50 = P + "/2026-10-26-mark1-right-engineering-flow105-overlap50-temp260-left08-z000"
LIDS = P + "/2026-10-26-mark1-lids-flush-grips-no-supports"
MAY_PROJECT = "f25975cd045cc835eccf1a207cb12fe48dc63ada"
SEPT_PROJECTS = "67994c7efaed7589ff26db350b90eea089fbd3e8"


def sources():
    """The files that own the numbers this chapter prints."""
    b.source("petg_res", R + "/reservoir.3mf", member="Metadata/project_settings.config")
    b.source("petg_plan", R + "/reservoir.print.json")
    b.source("petg_slice", R + "/slice-review.json")
    b.source("petg_gf", "hardware/printed-parts/petgf.3mf", member="Metadata/project_settings.config")
    b.source("petg_mold", "tools/funnel-mold-print/recipes.json")


def res(pointer):
    return b.setting("petg_res", pointer)


def gf(pointer):
    return b.setting("petg_gf", pointer)


def mold(pointer):
    return b.setting("petg_mold", "/0.4" + pointer)


# ----------------------------------------------------------------------------- page pieces
def mono(text, size=25, color="var(--muted)"):
    return f'<span class="mono" style="font-size:{size}px; letter-spacing:.08em; color:{color}">{text}</span>'


def grid(head, rows, widths, size=33, pad=12):
    """A comparison table: head is the column titles, rows are lists whose first cell names the row."""
    cols = "".join(f'<col style="width:{w}px">' for w in widths)
    th = "".join(f'<th scope="col" style="padding:0 22px {pad}px 0">{h}</th>' for h in head)
    body = ""
    for r in rows:
        cells = f'<th scope="row" style="padding:{pad}px 22px {pad}px 0; font-weight:400; color:var(--muted)">{r[0]}</th>'
        cells += "".join(f'<td style="padding:{pad}px 22px {pad}px 0; color:var(--ink); font-weight:600">{c}</td>' for c in r[1:])
        body += f"<tr>{cells}</tr>"
    return (f'<table class="grid" style="font-size:{size}px; table-layout:fixed"><colgroup>{cols}</colgroup>'
            f'<thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>')


def legend(items, size=31):
    """Numbered notes beside a picture: (number, colour class, title, mono tag, text)."""
    out = ""
    for n, c, title, tag, text in items:
        out += (f'<div style="display:flex; gap:22px; align-items:flex-start"><span class="num {c}">{n}</span>'
                f'<div><p style="margin:0 0 2px; font:650 40px/1.2 \'IBM Plex Sans\'; color:var(--ink)">{title}</p>'
                f'<p style="margin:0 0 6px; font-size:25px; line-height:1.3">{mono(tag)}</p>'
                f'<p class="tiny" style="margin:0; font-size:{size}px; color:var(--text)">{text}</p></div></div>')
    return out


def drop(x, y, r=11):
    """A bead of water in a drawing: white with an ink edge, so it adds no fifth colour."""
    return f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="{k.n(r)}" fill="white" stroke="{k.INK}" stroke-width="4"/>'


def beads(x0, x1, y, w, colour=k.COLD, shift=0.0):
    """One course of beads w wide, its top at y. Fill laid at an angle is cut on the slant, so its beads are drawn wider than a loop's."""
    bh = k.ROW_H - 3
    return (f'<path d="M{k.n(x0 + 1.5 + bh / 2 + shift)} {k.n(y + k.ROW_H / 2)}H{k.n(x1 - 1.5 - bh / 2)}" fill="none" stroke="{colour}" '
            f'stroke-width="{k.n(bh)}" stroke-linecap="round" stroke-dasharray="{k.n(w - 3 - bh)} {k.n(3 + bh)}"/>')


def clip_poly(pts, x0, x1, y0, y1):
    """A convex polygon cut to a box, so no part of a drawing has to rely on a clip path."""
    def cut(points, inside, cross):
        out = []
        for i, cur in enumerate(points):
            prev = points[i - 1]
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
        return out

    def at_x(xv):
        return lambda p, q: (xv, p[1] + (q[1] - p[1]) * (xv - p[0]) / (q[0] - p[0]))

    def at_y(yv):
        return lambda p, q: (p[0] + (q[0] - p[0]) * (yv - p[1]) / (q[1] - p[1]), yv)

    for inside, cross in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                          (lambda p: p[1] >= y0, at_y(y0)), (lambda p: p[1] <= y1, at_y(y1))):
        pts = cut(pts, inside, cross)
        if not pts:
            return []
    return pts


def slanted_roads(x0, x1, y0, y1, pitch, width, colour, start=0.0):
    """Roads at 45 degrees filling a box, each cut square to the box: fill seen from above."""
    h, d, t = y1 - y0, "", x0 - (y1 - y0) - width + start
    while t < x1:
        pts = clip_poly([(t, y1), (t + width, y1), (t + width + h, y0), (t + h, y0)], x0, x1, y0, y1)
        if len(pts) > 2:
            d += "M" + "L".join(f"{k.n(px)} {k.n(py)}" for px, py in pts) + "Z"
        t += pitch
    return f'<path d="{d}" fill="{colour}"/>'


def cap(lab, text):
    return f'<figcaption class="cap"><span class="lab">{lab}</span>{text}</figcaption>'


# ----------------------------------------------------------------------------- 1 the plastic
def plastic():
    sources()
    W, H = 800, 760
    cam, target, span = [1.0, 0.9, 0.55], [0.0, 238.0, 177.5], 270
    base = dict(step="manifold-layout/enclosure-assembly.step", cam=cam, target=target, span=span, size=f"{W}x{H}")
    clear = ["cold-core/reservoir-a", "cold-core/reservoir-a-cap", "cold-core/reservoir-b", "cold-core/reservoir-b-cap", "status-plate-diffuser"]
    black = ["funnel-cover", "status-plate", "nameplate", "cold-core/prv-shroud", "cold-core/reed-bridge", "fuse-clamp",
             "bulkhead-ring-flavor-a", "bulkhead-ring-flavor-b", "bulkhead-ring-*-word"]
    white = ["bulkhead-ring-water", "bulkhead-ring-drain", "nameplate-ink", "bulkhead-ring-flavor-*-word"]
    shell = b.render("petg-machine-shell.png", {**base, "only": ["enclosure-front-*", "enclosure-back-*"], "context": "hide",
                                                "materials": [{"names": ["enclosure-*"], "color": "#9aa7b2", "opacity": 0.22}]})
    parts = b.render("petg-machine-parts.png", {**base, "only": clear + black + ["bulkhead-ring-*", "nameplate-ink"], "context": "hide", "edges": True,
                                                "materials": [{"names": clear, "color": TEAL, "roughness": 0.55},
                                                              {"names": black, "color": "#1b242d", "roughness": 0.8},
                                                              {"names": white, "color": "#f4f5f6", "roughness": 0.8},
                                                              {"names": ["bulkhead-ring-carb"], "color": "#0086d6", "roughness": 0.8},
                                                              {"names": ["bulkhead-ring-co2"], "color": "#d6001c", "roughness": 0.8}]})
    pm = projector(cam, target, span, (W, H))
    marks = [  # number, the point on the model, how far from it the disc sits
        (1, [70.25, 415.0, 110.0], (0, 0)), (1, [70.25, 232.0, 150.0], (0, 0)),
        (2, [20.0, 150.0, 361.0], (0, 0)),
        (3, [76.0, 471.0, 340.0], (70, -110)), (3, [-41.0, 473.5, 200.0], (40, 120)),
        (4, [-62.0, 324.0, 231.0], (-30, -150)), (4, [62.7, 324.0, 112.0], (-150, 150)), (4, [-6.0, 25.0, 40.0], (-110, 70)),
    ]
    over = ""
    for num, pt, (dx, dy) in marks:
        x, y = pm(pt)
        over += k.callout(num, x, y, x + dx, y + dy)
    over = k.svg(W, H, over, "Where the PETG is in one machine",
                 "The machine seen from the rear with its enclosure faded. Two tall reservoirs with lids stand inside, a flat cover sits on the roof, "
                 "and six small chips and a nameplate are on the rear wall.", style=f"position:absolute; left:0; top:0; width:{W}px; height:{H}px")
    hero = (f'<figure style="margin:0"><div style="position:relative; width:{W}px; height:{H}px">'
            f'<img src="art/{shell}" alt="" style="position:absolute; left:0; top:0; width:{W}px; height:{H}px">'
            f'<img src="art/{parts}" alt="The PETG parts of the machine, coloured, inside a faded enclosure" style="position:absolute; left:0; top:0; width:{W}px; height:{H}px">{over}</div>'
            '<figcaption class="cap" style="margin-top:6px"><span class="lab">One machine from the rear, enclosure faded</span>'
            'Teal is clear PETG. The rest is PETG Basic, drawn in the colour it prints in.</figcaption></figure>')
    notes = legend([
        (1, "", "Reservoirs and their lids", "CLEAR",
         "<b>Printed, and holding water.</b> They hold the flavoring, and the level shows through the wall. The glass-filled PET-GF stays in the shells around them."),
        (2, "", "Funnel cover", "BASIC, BLACK",
         "<b>Sliced, never sent.</b> A solid plate that closes the fill funnel between fills."),
        (3, "", "Chips and nameplate", "BASIC, FOUR COLOURS",
         "<b>Printed 8 November 2026.</b> Black, white, blue and red through 0.2 mm nozzles. The status plate on the front shared their bed, with a clear window for its light."),
        (4, "", "Small parts inside", "BASIC, BLACK",
         "<b>No print on record.</b> The relief-valve shroud, the reed bridge and the fuse clamp."),
    ])
    which = ('<div style="margin-top:34px; padding-top:26px; border-top:2px solid var(--line)"><h3>Which PETG, which print</h3>'
             '<p class="small" style="margin:0; font-size:33px"><b>SunTop clear</b>, an off-brand spool: the first two reservoirs, 22 and 25 May 2026. The first leaked. Not used since. '
             '<b>Bambu PETG Translucent Clear:</b> every reservoir and lid from 30 May 2026, both halves of the funnel mold, and the status light&rsquo;s window. '
             '<b>Bambu PETG Basic:</b> the chips, the nameplate and the status plate.</p></div>')
    table = grid(
        ["", "Clear PETG · reservoir body", "Clear PETG · mold half", "PET-GF · enclosure"],
        [
            ["Nozzle", f'Mark 1, left {res("/nozzle_diameter/0")} mm', f'Mark 1, {mold("/side")} {mold("/nozzle_mm")} mm', f'left {gf("/nozzle_diameter/0")} mm'],
            ["Plate", f'{res("/curr_bed_type")}, glued, {res("/eng_plate_temp/0")} °C', "Textured PEI", f'{gf("/curr_bed_type")}, {gf("/textured_plate_temp/0")} °C'],
            ["Lift added to the first layer", f'none: <span class="mono" style="font-size:28px">{b.setting("petg_slice", "/plates/0/z_trim_commands/1")}</span>',
             f'{mold("/z_trim/default_mm")} mm', "its own for each printer and plate"],
            ["Brim", f'{res("/brim_width")} mm', f'{mold("/process_settings/brim_width/value")} mm', gf("/brim_type")],
            ["Layers, first / rest", f'{res("/initial_layer_print_height")} / {res("/layer_height")} mm', "the preset&rsquo;s", f'{gf("/initial_layer_print_height")} / {gf("/layer_height")} mm'],
            ["Nozzle heat, first / rest", f'{res("/nozzle_temperature_initial_layer/0")} / {res("/nozzle_temperature/0")} °C', "the preset&rsquo;s",
             f'{gf("/nozzle_temperature_initial_layer/0")} / {gf("/nozzle_temperature/0")} °C'],
            ["Flow", res("/filament_flow_ratio/0"), mold("/filament_settings/filament_flow_ratio/value/0"), gf("/filament_flow_ratio/0")],
            ["Wall loops", f'{res("/wall_loops")}, {res("/wall_generator")}, {res("/line_width")} mm each', mold("/process_settings/wall_loops/value"), f'{gf("/wall_loops")}, {gf("/wall_generator")}'],
            ["Inside the loops", f'{res("/sparse_infill_density")} {res("/sparse_infill_pattern")}',
             f'{mold("/process_settings/sparse_infill_density/value")} {mold("/process_settings/sparse_infill_pattern/value")}',
             f'{gf("/sparse_infill_density")} {gf("/sparse_infill_pattern")}'],
            ["Fill pushed into the loops", f'{b.setting("petg_plan", "/plates/0/infill_wall_overlap")} left body · {b.setting("petg_plan", "/plates/1/infill_wall_overlap")} right body',
             "the preset&rsquo;s", gf("/infill_wall_overlap")],
            ["Part fan on plain walls", f'{res("/fan_min_speed/0")} to {res("/fan_max_speed/0")}%, off for {res("/close_fan_the_first_x_layers/0")} layers', "the preset&rsquo;s", f'{gf("/fan_max_speed/0")}%'],
        ],
        [470, 600, 520, 580], pad=10)
    body = (
        b.head("PETG · the plastic", "Plain PETG holds the flavoring.",
               "The enclosure is stiffened with glass fibre. The two reservoirs are not. They and their lids are plain clear PETG, "
               "laid a little fat so that every road is pressed into its neighbours.", size=160, lede_size=52, top=60)
        + b.scope("Bambu PETG Translucent Clear · Mark 1 · glued Engineering Plate · left 0.8 mm", not_tried="Mark2")
        + b.row(("0 0 800px", hero),
                f'<div style="display:grid; grid-template-columns:1fr 1fr; column-gap:44px; row-gap:30px">{notes}</div>' + which,
                gap=50, style="margin-top:26px")
        + b.rulebar(26, 22)
        + '<h2 style="margin-bottom:6px">One family, two recipes, and neither is PET-GF&rsquo;s.</h2>'
        + table
        + b.row(
            b.quote("I have found in other testing that over extrusion (flow ratio) helps with air tightness / water tightness.",
                    "DEREK · 22 MAY 2026, BEFORE THE FIRST RESERVOIR", size=40),
            ("0 0 900px",
             b.record(b.link("The project that holds this recipe", R + "/reservoir.3mf"),
                      b.link("Which print each plate is bound to", R + "/print-settings.json"),
                      b.link("Mold recipe", "tools/funnel-mold-print/recipes.json"),
                      b.link("Why no glass touches the drink", "hardware/concerns.md"))),
            gap=70, style="margin-top:28px")
        + b.still_open("The project file holds the reservoir column. Two notes beside it still describe the file as it stood during October&rsquo;s trials: 30% and "
                       "265/270 °C through the right nozzle. The right body is still bound to 30%, the last value with a water test written against that side, "
                       "though its 50% print finished on 26 October 2026 and Derek&rsquo;s word of 12 November covers it. No printed PETG surface has been through "
                       "the food-contact screen the project wrote for it.")
    )
    return Page("plain-petg-holds-the-flavoring", "PETG: plain PETG holds the flavoring", "petg", body, right="The plastic")


# ----------------------------------------------------------------------------- 2 the floor seam
def floor_plan():
    """The reservoir floor from above: five loops round the outline, straight fill inside, and the one line where they meet."""
    W, H = 1100, 470
    cx, y0, y1 = 520.0, 12.0, 458.0
    x0, x1 = cx - 422, cx + 422
    c, sag, r = 768.0, 150.0, 24.0
    rad = (c * c / 4 + sag * sag) / (2 * sag)
    cy = y0 - (rad - sag)
    pitch, loops = 22.0, 5

    def loop(d):
        """The outline moved inward by d, as a closed path."""
        rr = max(r - d, 0.0)
        lft, rgt, top, bot, big = x0 + d, x1 - d, y0 + d, y1 - d, rad + d
        half = math.sqrt(max(big * big - (top - cy) ** 2, 0.0))
        low = (f"L{k.n(rgt)} {k.n(bot - rr)}Q{k.n(rgt)} {k.n(bot)} {k.n(rgt - rr)} {k.n(bot)}L{k.n(lft + rr)} {k.n(bot)}Q{k.n(lft)} {k.n(bot)} {k.n(lft)} {k.n(bot - rr)}")
        if cx - half > lft + rr + 1:  # the two ears beside the scoop still have a flat top
            return (f"M{k.n(lft + rr)} {k.n(top)}L{k.n(cx - half)} {k.n(top)}A{k.n(big)} {k.n(big)} 0 0 0 {k.n(cx + half)} {k.n(top)}L{k.n(rgt - rr)} {k.n(top)}"
                    f"Q{k.n(rgt)} {k.n(top)} {k.n(rgt)} {k.n(top + rr)}{low}L{k.n(lft)} {k.n(top + rr)}Q{k.n(lft)} {k.n(top)} {k.n(lft + rr)} {k.n(top)}Z")
        ya = cy + math.sqrt(big * big - (lft - cx) ** 2)  # the scoop runs into the side edges
        return f"M{k.n(lft)} {k.n(ya)}A{k.n(big)} {k.n(big)} 0 0 0 {k.n(rgt)} {k.n(ya)}{low}Z"

    g = []
    # fill: roads at 45 degrees, each cut where it meets the innermost loop
    inset = loops * pitch + 6
    lft, rgt, top, bot, big = x0 + inset, x1 - inset, y0 + inset, y1 - inset, rad + inset
    d, t = "", lft - (bot - top) - 40
    while t < rgt:
        lo = max(0.0, lft - t)
        hi = min(rgt - t, bot - top)
        qb = (t - cx) - (bot - cy)
        disc = qb * qb - 2 * ((t - cx) ** 2 + (bot - cy) ** 2 - big * big)
        if disc > 0:
            hi = min(hi, (-qb - math.sqrt(disc)) / 2)
        if hi - lo > 6:
            d += f"M{k.n(t + lo)} {k.n(bot - lo)}L{k.n(t + hi)} {k.n(bot - hi)}"
        t += 31.0
    g.append(f'<path d="{d}" fill="none" stroke="{k.COLD}" stroke-width="18"/>')
    for i in range(loops):
        g.append(f'<path d="{loop((i + 0.5) * pitch)}" fill="none" stroke="{k.COLD}" stroke-width="18" stroke-linejoin="round"/>')
    g.append(f'<path d="{loop(loops * pitch + 1)}" fill="none" stroke="{k.BAD}" stroke-width="6" stroke-dasharray="15 11" stroke-linejoin="round"/>')
    seam = rad + loops * pitch + 14
    for deg, size in ((66, 9), (73, 12), (81, 10), (90, 13), (98, 9), (106, 12), (114, 8)):
        ang = math.radians(deg)
        g.append(drop(cx + seam * math.cos(ang), cy + seam * math.sin(ang), size))
    g.append(k.callout(1, x1 - loops * pitch / 2, 300, x1 + 72, 300))
    g.append(k.callout(2, cx + 200, 392))
    g.append(k.callout(3, cx - 56, cy + seam - 20, cx - 56, y0 + 50, "bad"))
    return k.svg(W, H, "".join(g), "The reservoir floor seen from above",
                 "Five loops follow the outline of the floor, which has one side scooped out in an arc. Straight fill runs at an angle inside them. "
                 "A dashed red line marks where the fill meets the innermost loop, and beads of water sit along it beside the scoop.")


def floor_section():
    """The same joint cut through: the wall, the loops under it, the fill, and the seam running through every floor course."""
    W, H, G, BED = 1100, 400, 62.0, 344.0

    def x(i):
        return G + i * k.BEAD_W

    def y(row):
        return k.row_y(row, BED)

    g = [f'<rect x="{k.n(x(5))}" y="{k.n(y(13))}" width="{k.n(x(22) - x(5))}" height="{k.n(y(11) - y(13))}" fill="{k.WASH}"/>',
         k.block(x(0), x(5), 0, 13, BED)]
    for row in range(12):
        g.append(beads(x(5), x(22), y(row), 61.0, shift=(row % 2) * 30.0))
    g.append(k.line(x(5), y(11) - 4, x(5), BED + 4, k.BAD, 6, "13 9"))
    g.append(drop(x(5), BED + 22, 13) + drop(x(5) + 5, BED + 46, 7))
    g.append(k.label(x(22) - 14, y(12) + 8, "WATER", anchor="end"))
    g.append(f'<text transform="translate({k.n(G - 18)} {k.n(y(6))}) rotate(-90)" font-family="IBM Plex Mono, monospace" font-size="27" font-weight="600" '
             f'letter-spacing="1.6" fill="{k.INK}">WALL</text>')
    g.append(k.label(x(22) + 14, y(5) + 6, "FLOOR", fill=k.INK, weight=600))
    g.append(k.callout(1, x(2.5), y(5) + 12))
    g.append(k.callout(2, x(14), y(5) + 12))
    g.append(k.callout(3, x(5), y(8), x(5) + 120, y(12) + 2, "bad"))
    return k.svg(W, H, "".join(g), "The floor and wall of the reservoir in section",
                 "The wall stands on five loops that run down through all twelve floor courses. Fill makes the rest of the floor. "
                 "A dashed red line between the last loop and the fill runs from the water side to the underside, where beads of water hang.")


def lap_strip():
    """Three close views from above: how far the fill is pushed into the innermost loop at 15, 30 and 50 percent."""
    W, H, line_w, top = 2170, 226, 110.0, 30.0
    edge = top + line_w
    g = []
    for i, pct in enumerate((15, 30, 50)):
        ox, lap = i * 741.0, pct / 100.0 * line_w
        g.append(f'<g transform="translate({k.n(ox)} 0)">'
                 f'<rect x="0" y="0" width="540" height="{k.n(top - 7)}" fill="{k.COLD}"/>'
                 f'<rect x="0" y="{k.n(top)}" width="540" height="{k.n(line_w - 7)}" fill="{k.COLD}"/>'
                 + slanted_roads(0, 540, edge - lap, H, 124.0, 104.0, k.HOT, start=20.0)
                 + k.line(566, edge - lap, 566, edge - 3, k.INK, 5)
                 + k.line(554, edge - lap, 578, edge - lap, k.INK, 5) + k.line(554, edge - 3, 578, edge - 3, k.INK, 5)
                 + k.label(592, edge - lap / 2 + 12, f"{pct}%", 40, fill=k.INK, weight=600)
                 + k.label(556, top + 26, "LOOP", 25) + k.label(556, H - 16, "FILL", 25, fill=k.HOT, weight=600) + "</g>")
    return k.svg(W, H, "".join(g), "How far the fill is pushed into the innermost loop",
                 "Three views from above of fill roads, in orange, being laid against the innermost loop, in slate. "
                 "At 15 percent the fill barely laps onto the loop. At 30 percent it laps further. At 50 percent it covers half the loop's width.")


def floor_seam():
    sources()
    drops = b.asset("petg-floor-seam-drops.jpg", MAY_WATER + "/physical-result/photo-3.jpg")
    left = b.fig(drops, "The underside of a clear printed floor with beads of water in a row where diagonal fill meets a band of loops",
                 "21 October 2026 · Mark 1 · Bambu clear PETG",
                 "The underside of a reservoir, filled and held up to the light. Loops follow the scooped side and fill runs at an angle. "
                 "The beads of water sit in a row on the line between them.", h=836, pos="50% 62%")
    right = (f'<figure>{floor_plan()}<div style="height:18px"></div>{floor_section()}'
             + cap("That floor from above, and cut through at the wall",
                   "<b>1</b> five loops, laid first. <b>2</b> fill, laid inside them afterwards. <b>3</b> the line where they meet, "
                   "which runs through every course of the floor.") + "</figure>")
    steps = ('<div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:44px; margin-top:10px">'
             '<p class="small" style="margin:0"><span class="tag bad" style="margin-right:14px">Leaked</span><b>15%, 21 October 2026.</b> The slicer&rsquo;s own number. '
             'Beads in a row: &ldquo;Leaks between infill and wall.&rdquo;</p>'
             '<p class="small" style="margin:0"><span class="tag" style="margin-right:14px">One wept</span><b>30%, 22 to 25 October.</b> Changed with flow, '
             'loop count and heat. Bodies held for days. Then the newest wept specks in two hours.</p>'
             '<p class="small" style="margin:0"><span class="tag good" style="margin-right:14px">Holds</span><b>50%, 26 October.</b> The only setting changed. '
             'That body: &ldquo;It&rsquo;s holding water so far.&rdquo;</p></div>')
    body = (
        b.head("Watertight · the floor", "It weeps where the floor meets the wall.",
               "A floor is printed in two parts: loops that follow its outline, then straight fill inside them. Unless the fill is pushed into "
               "the loops, the line where the two meet lets water through.", size=150, lede_size=52, top=60)
        + b.scope("Bambu PETG Translucent Clear · Mark 1 · 0.8 mm nozzle · flat 3 mm floor", not_tried="PETG Basic")
        + b.row(("0 0 960px", left), right, gap=60, style="margin-top:30px")
        + b.rulebar(22, 18)
        + '<h2 style="margin-bottom:16px">One setting moved, in three steps: how far the fill is pushed into the loops.</h2>'
        + lap_strip() + steps
        + b.rulebar(22, 20)
        + b.row(
            b.quote("It does appear to be precisely in the line between wall and infill. I know we increased that overlap some already, can we increase it more?",
                    "DEREK · 26 OCTOBER 2026, OF THE SPECKS", size=41)
            + '<p class="small" style="margin:18px 0 0">An agent prepared 40%. &ldquo;Please make that 50% instead, thanks.&rdquo;</p>',
            ("0 0 600px",
             '<h2>What we do now</h2>'
             f'<p class="small" style="margin:0">{res("/wall_loops")} loops, solid fill between them, and the fill pushed {b.setting("petg_plan", "/plates/0/infill_wall_overlap")} '
             f'of a road into the loops on the left body. The PET-GF enclosure stays at {gf("/infill_wall_overlap")}. Nothing asks it to hold water.</p>'),
            ("0 0 500px",
             b.record(b.link("The beads in a row", MAY_WATER + "/physical-result/physical-result.json"),
                      b.link("The specks at two hours", R + "/water-hold-evidence/2026-10-26-two-hour-leak/physical-result.json"),
                      b.link("30% to 50%, nothing else", R + "/recipe-reviews/2026-10-26-overlap50/verification.json"),
                      b.link("Derek, 12 November", "hardware/ledger/fitted.json"))),
            gap=56)
        + b.still_open("The photographs show where water came out, not the path it took. Nobody has cut a floor open. The first step, 15% to 30%, changed with three other "
                       "settings. Every result is a fill-and-watch test with no fill height written down. On 12 November 2026 Derek wrote that every reservoir printed "
                       "since the change was still holding.")
    )
    return Page("it-weeps-where-the-floor-meets-the-wall", "PETG: it weeps where the floor meets the wall", "petg", body, right="Watertight · the floor")


# ----------------------------------------------------------------------------- 3 a floor of loops
def loops_pair():
    """Two floors from above: loops round fill, and loops all the way in."""
    W, H, pitch, bead = 1380, 310, 26.0, 22.0
    x0, x1, y0, y1 = 0.0, 600.0, 4.0, 304.0

    def ring(d, colour=k.COLD, width=bead, dash=""):
        rx = max(40.0 - d, 3.0)
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<rect x="{k.n(x0 + d)}" y="{k.n(y0 + d)}" width="{k.n(x1 - x0 - 2 * d)}" height="{k.n(y1 - y0 - 2 * d)}" rx="{k.n(rx)}" '
                f'fill="none" stroke="{colour}" stroke-width="{k.n(width)}"{extra}/>')

    a = [ring((i + 0.5) * pitch) for i in range(3)]
    inner = 3 * pitch + 5
    a.append(slanted_roads(x0 + inner, x1 - inner, y0 + inner, y1 - inner, 34.0, 26.0, k.COLD, start=6.0))
    a.append(ring(3 * pitch + 1, k.BAD, 6, "15 11"))
    bb = [ring((i + 0.5) * pitch) for i in range(5)]
    mid = (y0 + y1) / 2
    bb.append(f'<path d="M{k.n(x0 + 5 * pitch + 30)} {k.n(mid)}H{k.n(x1 - 5 * pitch - 30)}" stroke="{k.COLD}" stroke-width="{k.n(bead)}" stroke-linecap="round" fill="none"/>')
    bb.append(k.line(x0 + 5 * pitch + 6, mid - 16, x1 - 5 * pitch - 6, mid - 16, k.BAD, 6, "15 11"))
    bb.append(k.line(x0 + 5 * pitch + 6, mid + 16, x1 - 5 * pitch - 6, mid + 16, k.BAD, 6, "15 11"))
    for i in range(1, 5):
        d = i * pitch
        for px, py in ((x0 + d, y0 + d), (x1 - d, y0 + d), (x0 + d, y1 - d), (x1 - d, y1 - d)):
            bb.append(f'<circle cx="{k.n(px)}" cy="{k.n(py)}" r="6.5" fill="{k.BAD}"/>')
    return k.svg(W, H, f'<g>{"".join(a)}</g><g transform="translate(760 0)">{"".join(bb)}</g>',
                 "Two ways to print a flat floor, seen from above",
                 "Left: three loops round the outline with straight fill inside, and one dashed red seam where fill meets loop. "
                 "Right: loops nested all the way to the middle, with red marks at every corner the loops turn and a dashed red line where they meet in the middle.")


def loops_floor():
    sources()
    photo = b.asset("petg-loops-only-drops.jpg", WALLS_ONLY + "/physical-result/photo-1.jpg")
    paths = b.asset("petg-loops-only-paths.png", WALLS_ONLY + "/floor-wall-paths.png", kind="Figure from the record")
    left = b.fig(photo, "The underside of a clear printed floor made of nested loops, with beads of water along a branching line and at two corners",
                 "22 October 2026 · Mark 1 · Bambu clear PETG",
                 "A reservoir whose floor is loops and nothing else, full of water, seen from below. The beads sit along a branching line across the floor and at its corners.",
                 h=700, pos="50% 45%")
    plot = (f'<figure><img src="art/{paths}" alt="Plots of the first and twelfth floor layers: nested blue loops with small red marks along two diagonals and a middle line" '
            'style="display:block; width:100%; height:700px; object-fit:contain; background:white; box-shadow:inset 0 0 0 2px var(--line)">'
            + cap("From the record · first and twelfth floor layer",
                  "Blue is a loop. Red is floor no loop covers, counted from the file sent to the printer. Nobody has laid the photograph over this plot.") + "</figure>")
    stats = ('<div style="display:grid; gap:26px">'
             + b.stat("45", "loops in each floor layer of that print.")
             + b.stat('10 <span>mm²</span>', "of floor left uncovered in each of its twelve layers. About a thousandth of the floor.")
             + b.stat('72% <span>less</span>', "uncovered in the slice once a setting added centre roads where loops meet. Printed on 22 October, it leaked in the same place.", hot=True)
             + "</div>")
    body = (
        b.head("Watertight · a floor of loops", "A floor made of loops leaks along its seams.",
               "Loops laid side by side run out of room where they turn a corner and where they meet in the middle. Each of those places is a small "
               "gap, and it comes back on every layer.", size=150, lede_size=52, top=60)
        + b.scope("Bambu PETG Translucent Clear · Mark 1 · right 0.8 mm · textured PEI", not_tried="a flow above 1.02")
        + b.row(("0 0 1180px", left), plot, gap=50, style="margin-top:30px")
        + b.rulebar(22, 22)
        + b.row(
            ("0 0 1380px",
             f'<figure>{loops_pair()}</figure>'
             '<div class="grid2" style="gap:160px; margin-top:12px">'
             '<p class="small" style="margin:0"><b>Loops round fill.</b> One seam, a closed line, and one setting pushes the fill across it. The floor on the page before.</p>'
             '<p class="small" style="margin:0"><b>Loops all the way in.</b> No fill to push. A gap wherever a loop cannot follow its neighbour: at each turn, and along the middle.</p></div>'),
            stats, gap=70)
        + b.rulebar(22, 20)
        + b.row(
            b.quote("I think I&rsquo;d rather continue the walls forever, as we did in the sphere pressure vessel test. Another agent suggested at some point infill works better, but I haven&rsquo;t seen that.",
                    "DEREK · 21 OCTOBER 2026, ASKING FOR THIS PRINT", size=38),
            b.quote("Leaks along the seam", "DEREK · 22 OCTOBER 2026", size=58)
            + '<p class="small" style="margin:22px 0 0">Of the second try: &ldquo;Not sure that made any difference at all.&rdquo;</p>',
            ("0 0 560px",
             '<h2>What we do now</h2><p class="small" style="margin-bottom:16px">The floor is solid fill inside five loops. The loops-only floor has not been printed again.</p>'
             + b.record(b.link("Result and photograph", WALLS_ONLY + "/physical-result/physical-result.json"),
                        b.link("Gaps, layer by layer", WALLS_ONLY + "/floor-wall-coverage.json"),
                        b.link("The second try", T59 + "/physical-result/physical-result.json"))),
            gap=56)
        + b.still_open("Both loops-only floors were printed at flow 1.02, before the flow went up to the value that held. A floor of loops has not been tried at that flow, "
                       "so this page shows that these two floors leaked, not that no floor of loops can hold. The sphere Derek remembered was printed in April 2026, and its "
                       "settings were never found.")
    )
    return Page("a-floor-made-of-loops-leaks-along-its-seams", "PETG: a floor made of loops leaks along its seams", "petg", body, right="Watertight · a floor of loops")


# ----------------------------------------------------------------------------- 4 what mattered
def trials_table():
    """Every reservoir that met water, in order. Each cell is (text, changed from the print above)."""
    ch = lambda t: (t, True)
    same = lambda t: (t, False)
    m1 = "Mark 1 · right 0.8 mm · textured"
    eng = "Mark 1 · left 0.8 mm · glued plate"
    rows = [
        ("row", [same("30 May 2026"), same("Mark 1 · 0.6 mm · textured"), same("thin, sloped, on supports"), same("none kept"), same("1.02"), same("6"), same("15%"), same("255 / 260")],
         ("good", "Held"), "for hours"),
        ("row", [same("5 and 8 September"), ch("Mark2 · 0.8 mm · textured"), ch("solid, sloped inside"), ch("20 h and 26 h"), ch("0.97"), same("6"), same("15%"), ch("255")],
         ("good", "Held"), "both"),
        ("note", "19 October 2026 · the floor becomes one flat slab 3 mm thick, with nothing through it"),
        ("row", [same("21 October"), ch(m1), ch("flat, 3 mm"), same("19 h"), same("0.97"), same("6"), same("15%"), same("255")],
         ("bad", "Leaked"), "&ldquo;many places&rdquo;"),
        ("row", [same("21 October"), same(m1), same("flat"), ch("5 h 42 min"), ch("1.02"), same("6"), same("15%"), ch("255 / 260")],
         ("bad", "Leaked"), "along the fill line"),
        ("row", [same("21 and 22 October"), same(m1), ch("flat, loops only"), same("5 h 46 min"), same("1.02"), ch("all"), ch("no fill"), same("255 / 260")],
         ("bad", "Leaked"), "at loop seams, twice"),
        ("row", [same("22 October"), same(m1), ch("flat, fill again"), same("5 h 42 min"), ch("1.05"), ch("5"), ch("30%"), ch("265 / 270")],
         ("good", "Held"), "and two days on"),
        ("row", [same("24 October"), same(m1), same("flat"), same("5 h 42 min"), same("1.05"), same("5"), same("30%"), ch("255 / 260")],
         ("good", "Held"), ""),
        ("row", [same("25 October"), ch(eng), same("flat"), same("5 h 42 min"), same("1.05"), same("5"), same("30%"), same("255 / 260")],
         ("good", "Held"), "at first report"),
        ("note", "26 October · the newest 30% body lets a few specks through in two hours. The record does not say which print it was."),
        ("row", [same("26 October"), same(eng), same("flat"), same("5 h 42 min"), same("1.05"), same("5"), ch("50%"), same("255 / 260")],
         ("good", "Holds"), "and so does the next"),
    ]
    widths = [300, 470, 270, 205, 90, 110, 120, 150, 455]
    head = ["Print", "Printer · nozzle · plate", "Floor", "Time", "Flow", "Loops", "Lap", "°C", "Water"]
    cols = "".join(f'<col style="width:{w}px">' for w in widths)
    th = "".join(f'<th scope="col" style="padding:0 16px 12px 0">{h}</th>' for h in head)
    body = ""
    for r in rows:
        if r[0] == "note":
            body += (f'<tr><td colspan="9" style="padding:11px 0; background:var(--wash); font:400 27px/1.3 \'IBM Plex Mono\', monospace; letter-spacing:.05em; '
                     f'color:var(--ink); text-indent:18px">{r[1]}</td></tr>')
            continue
        _, cells, (tag, word), after = r
        tds = ""
        for i, (text, changed) in enumerate(cells):
            style = "color:var(--hot); font-weight:650" if changed else ("color:var(--ink); font-weight:600" if i == 0 else "color:var(--text)")
            tds += f'<td style="padding:13px 16px 13px 0; {style}">{text}</td>'
        tds += f'<td style="padding:13px 0; color:var(--text)"><span class="tag {tag}" style="margin-right:12px">{word}</span>{after}</td>'
        body += f"<tr>{tds}</tr>"
    return (f'<table class="grid" style="font-size:30px; table-layout:fixed"><colgroup>{cols}</colgroup><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'
            '<p class="tiny" style="margin:14px 0 0"><span style="color:var(--hot); font-weight:650">Orange</span> is what changed from the print above it. '
            'Lap is how far the fill is pushed into the loops, °C is the nozzle on the first layer and after, and time is the slicer&rsquo;s estimate for a body and its lid.</p>')


def what_mattered():
    sources()
    body = (
        b.head("Watertight · what we know", "Slow and hot were not what sealed it.",
               "Between the reservoir that leaked everywhere and the one that holds, the print got three times quicker and, for one body, ten degrees hotter. "
               "The heat came back out and it still held. Flow, loop count and the first lap step moved together.",
               size=150, lede_size=52, top=60)
        + b.scope("Bambu PETG Translucent Clear · one reservoir · printer, nozzle and plate named in each row")
        + f'<div style="margin-top:30px">{trials_table()}</div>'
        + b.rulebar(28, 26)
        + b.row(
            '<h2>What did not matter</h2>'
            '<p class="small"><b>Going slow.</b> September&rsquo;s recipe asked for 30 mm/s everywhere and took 20 hours. It held on September&rsquo;s solid floor '
            'and leaked in many places on the flat one. The recipe that holds asks for the slicer&rsquo;s ordinary speeds and is done in under six.</p>'
            '<p class="small" style="margin:0"><b>Ten more degrees.</b> Heat went up with three other things on 22 October. It came back down on the 24th, alone, and the body held. '
            'Derek had asked for that: the hotter print held, and he did not like the look of it.</p>',
            '<h2>What was never isolated</h2>'
            '<p class="small"><b>Flow.</b> 0.97, then 1.02, then 1.05, each time with something else. No body has been printed at two flows with the rest left alone.</p>'
            '<p class="small"><b>Loop count.</b> Six became five by reading slices at two, three, four and five loops. Five was never water-tested against six.</p>'
            '<p class="small" style="margin:0"><b>Plate and nozzle.</b> The glued plate and the left nozzle came in to stop lifting and fouling. 50% has only ever run on them.</p>',
            ("0 0 600px",
             b.quote("What I&rsquo;d like is:<br>- 1.05 flow rate<br>- enough walls for our actual walls to be entirely walls, no more<br>"
                     "- double the XY overlap (does bambu slicer call this wall/infill overlap? Its at 15% now?)<br>- higher temp",
                     "DEREK · 22 OCTOBER 2026 · FOUR AT ONCE, AND IT HELD", size=35)),
            gap=60)
        + b.rulebar(28, 0)
        + b.row(
            b.still_open("The test is water, a look, and Derek&rsquo;s report. No fill height, temperature, pressure or dye is written down, and the longest duration on record "
                         "is &ldquo;holding water for an hour&rdquo; followed by &ldquo;still holding&rdquo; two days later. One body at 30% wept and nobody knows why that one."),
            ("0 0 760px",
             b.record(b.link("Every attempt, in order", R + "/print-log.md"),
                      b.link("Each hold and leak", R + "/water-hold-acceptance.json"),
                      b.link("Heat alone: twelve commands differ", TEMP260 + "/adaptation.json"),
                      b.link("Five loops, by reading slices", R + "/recipe-reviews/2026-10-22-flow105-overlap30/README.md"),
                      b.link("September&rsquo;s slow recipe", R + "/history/seal-trial.md"))),
            gap=70, align="flex-end")
    )
    return Page("slow-and-hot-were-not-what-sealed-it", "PETG: slow and hot were not what sealed it", "petg", body, right="Watertight · what we know")


def pages():
    return [plastic(), floor_seam(), loops_floor(), what_mattered(), _mine.five_hundredths()]
