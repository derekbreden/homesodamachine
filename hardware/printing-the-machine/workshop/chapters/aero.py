"""ASA Aero: the foaming plastic the level floats are printed in. Three pages: the plastic and what
it needed, printing around a magnet, and why the float is all walls."""
import math

import bookkit as b
import svgkit as k
from bookkit import Page
from proj import projector

F = "hardware/printed-parts/cold-core/magnetic-float"
A = f"{F}/all-aero"
NIGHT = f"{F}/mark2-aero-print"      # the first night's trials, 2 to 3 October 2026
THREE = f"{A}/mark2-print/three-close-v1"
STEEL = "#27313b"                    # a bought metal part in a drawing; svgkit has no colour for one
SCOPE = "Bambu ASA Aero · Mark2 · glued Engineering plate · right 0.4 mm hardened nozzle"


def sources():
    """The files this chapter reads values from."""
    b.source("aero", f"{A}/all-aero-float.3mf", member="Metadata/project_settings.config")   # the float's recipe project
    b.source("aeroflight", f"{A}/mark2-print/v2/float-preflight.json")                       # the float as it is sliced now
    b.source("aerodesign", f"{A}/design.json")
    b.source("aerodry", "tools/magnetic-float-guide/build-recipe-sources.json")
    b.source("aerostrip", f"{NIGHT}/v6/pair-preflight.json")
    # the float that printed on 3 October 2026, as it was reviewed that morning
    b.source("aeroprint", f"{A}/mark2-print/v1/float-preflight.json", revision="7abb9dfd6")
    b.source("aeroprintdesign", f"{A}/design.json", revision="7abb9dfd6")


def s(name, pointer):
    return b.setting(name, pointer)


# ----------------------------------------------------------------------------- foam beads
def fblock(x0, x1, row0, row1, bed_y, hot=False):
    """svgkit's courses with bubbles in them, because this chapter's plastic is a foam. The bubbles
    are two dotted strokes per course, so the drawing stays as light as any other."""
    rows = range(row0, row1 + 1)
    a = "".join(f"M{k.n(x0 + 9)} {k.n(k.row_y(r, bed_y) + 8.5)}H{k.n(x1 - 4)}" for r in rows)
    c = "".join(f"M{k.n(x0 + 16)} {k.n(k.row_y(r, bed_y) + 15.5)}H{k.n(x1 - 4)}" for r in rows)
    return (k.block(x0, x1, row0, row1, bed_y, "hot" if hot else "cold")
            + f'<path d="{a}" fill="none" stroke="white" stroke-width="5" stroke-linecap="round" stroke-dasharray="0.1 13.9"/>'
            + f'<path d="{c}" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-dasharray="0.1 13.9 0.1 27.9"/>')


def bx(i):
    return i * k.BEAD_W


def recipe_table(rows, size=33, pad=11, th=44):
    """bookkit's recipe table, set a little tighter so a long recipe fits beside a drawing."""
    cell = f"padding:{pad}px 0"
    return (f'<table class="recipe" style="font-size:{size}px">'
            + "".join(f'<tr><th scope="row" style="{cell}; width:{th}%">{a}</th><td style="{cell}">{v}</td></tr>' for a, v in rows)
            + "</table>")


def bullets(items, size=34, gap=18):
    return "".join(
        f'<div style="display:flex; gap:22px; margin-bottom:{gap}px"><span class="num">{i + 1}</span>'
        f'<p class="small" style="margin:0; font-size:{size}px"><b>{t}</b> {d}</p></div>' for i, (t, d) in enumerate(items))


# ----------------------------------------------------------------------------- page 1: the plastic
def foam_drawing():
    W, H, BED = bx(28), 620, 22 * k.ROW_H
    flow = float(b.value("aero", "/filament_flow_ratio/0"))
    g = []
    for ox, foam, title in ((0, False, "AN ORDINARY FILAMENT"), (bx(15), True, "ASA AERO")):
        x0, x1 = ox + bx(1), ox + bx(12)
        nx = x0 + bx(7)
        top = k.row_y(4, BED)
        g.append(k.label(x0, 44, title, 32, fill=k.INK, weight=600))
        g.append(k.label(x0, 108, "PLASTIC FED FOR ONE LINE", 25))
        if foam:
            fed = (x1 - x0) * flow
            g.append(f'<rect x="{k.n(x0)}" y="124" width="{k.n(fed)}" height="44" fill="{k.COLD}"/>')
            g.append(f'<rect x="{k.n(x0 + fed + 2)}" y="126" width="{k.n(x1 - x0 - fed - 4)}" height="40" fill="none" stroke="{k.MUTED}" stroke-width="3" stroke-dasharray="9 8"/>')
            g.append(k.label(x0 + fed + (x1 - x0 - fed) / 2, 156, "FOAM", 25, anchor="middle"))
            g.append(k.label(x0, 214, "FLOW RATIO " + s("aero", "/filament_flow_ratio/0"), 30, fill=k.HOT, weight=600))
        else:
            g.append(f'<rect x="{k.n(x0)}" y="124" width="{k.n(x1 - x0)}" height="44" fill="{k.COLD}"/>')
            g.append(k.label(x0, 214, "FLOW RATIO CLOSE TO 1", 30, fill=k.INK, weight=600))
        g.append(k.bed(ox + 12, ox + bx(13) - 12, BED))
        g.append(fblock(x0, x1, 0, 3, BED) if foam else k.block(x0, x1, 0, 3, BED))
        g.append(fblock(x0, nx, 4, 4, BED, hot=True) if foam else k.block(x0, nx, 4, 4, BED, "hot"))
        g.append(k.nozzle(nx - 2, top))
        g.append(k.label(x0, BED + 72, "SAME LINE, HALF THE PLASTIC" if foam else "A SOLID LINE", 25, fill=k.INK))
    return k.svg(W, H, "".join(g), "Half the plastic, the same line",
                 "Two nozzles laying the same size of line on a stack of earlier courses. On the left an ordinary filament: the bar "
                 "of plastic fed for one line is full and the line is solid. On the right ASA Aero: the bar is about half as long, "
                 "the rest is foam made in the nozzle, and the line is the same size with bubbles through it.")


def night_strip():
    """The first night's starts, drawn as discs: stopped, not written down, ran."""
    W, H, P = 1180, 196, 170
    times = ["22:20", "23:06", "23:30", "00:09", "00:30", "01:01", "BY 01:53"]
    g = []
    for i, t in enumerate(times):
        cx = 52 + i * P
        if i:
            g.append(k.line(cx - P + 40, 60, cx - 40, 60, k.FAINT, 3))
        if i == 6:
            g.append(f'<circle cx="{cx}" cy="60" r="34" fill="{k.COLD}"/>')
            g.append(f'<text x="{cx}" y="71" text-anchor="middle" class="d-num">{i + 1}</text>')
        else:
            col, dash = (k.BAD, "9 7") if i < 5 else (k.MUTED, "3 7")
            g.append(f'<circle cx="{cx}" cy="60" r="32" fill="white" stroke="{col}" stroke-width="4" stroke-dasharray="{dash}"/>')
            g.append(f'<text x="{cx}" y="71" text-anchor="middle" font-family="IBM Plex Mono, monospace" font-weight="600" font-size="32" fill="{col}">{i + 1}</text>')
        g.append(k.label(cx, 130, t, 25, anchor="middle", fill=k.INK if i == 6 else k.MUTED, weight=600 if i == 6 else 400))
    g.append(k.line(16, 152, 52 + 4 * P + 36, 152, k.BAD, 3))
    g.append(k.label(16, 186, "TEXTURED PEI · EACH ONE STOPPED", 23, fill=k.BAD))
    g.append(k.line(52 + 5 * P - 44, 152, 52 + 5 * P + 44, 152, k.MUTED, 3))
    g.append(k.label(52 + 5 * P, 186, "GLUE", 23, anchor="middle"))
    g.append(k.line(52 + 6 * P - 44, 152, 52 + 6 * P + 44, 152, k.COLD, 3))
    g.append(k.label(52 + 6 * P, 186, "DRY BOX · RAN", 23, anchor="middle", fill=k.INK, weight=600))
    return k.svg(W, H, "".join(g), "Seven starts on the first night",
                 "Seven numbered discs with the time each print was started, from 22:20 on 2 October 2026 into the small hours of "
                 "3 October. The first five, all on textured PEI, are dashed red rings because each was stopped. The sixth, the first "
                 "on a glued Engineering plate, is a faint ring because how it ended was not written down. The seventh, feeding "
                 "from a dry box, is solid because it ran to the end.")


def plastic():
    sources()
    step = "printed-parts/cold-core/magnetic-float/all-aero/assembly.step"
    cam, target, span, size = [0.55, -1.0, 0.62], [0.0, 0.0, 13.6], 20.5, (1040, 880)
    cut = b.render("aero-float-cutaway.png", dict(
        step=step, cam=cam, target=target, span=span, size="1040x880", edges=True,
        section={"normal": [0, -1, 0], "at": [0, 0, 0]},
        materials=[{"names": ["float-aero"], "color": "#5f7180", "roughness": 0.95},
                   {"names": ["RC62"], "color": STEEL, "roughness": 0.4, "metalness": 0.5}]))
    pm = projector(cam, target, span, size)
    marks = [("1", [0.0, 0.0, 22.0]), ("2", [7.2, 0.0, 14.0]), ("3", [-13.0, 0.0, 7.0])]
    PW, PH = 430, 364   # the picture on the page, well under half its drawn size
    discs = "".join(f'<span class="num on-model" style="left:{pm(pt)[0] * PW / size[0]:.0f}px; top:{pm(pt)[1] * PH / size[1]:.0f}px">{n}</span>' for n, pt in marks)
    legend = "".join(
        f'<div style="display:flex; gap:18px; margin-bottom:14px"><span class="num">{n}</span><p class="tiny" style="margin:0; color:var(--text)">{t}</p></div>'
        for n, t in (("1", "<b>The bore.</b> It slides on a rod."),
                     ("2", "<b>A ring magnet,</b> read through the tank wall."),
                     ("3", "<b>Foam</b> above and below, in one piece.")))
    recipe = recipe_table([
        ("Nozzle, right side", "hardened, " + s("aero", "/nozzle_diameter/1") + " mm, " + s("aero", "/nozzle_temperature/0") + " °C"),
        ("Plate", s("aeroflight", "/bed") + ", " + s("aero", "/eng_plate_temp/0") + " °C"),
        ("Chamber", s("aero", "/chamber_temperatures/0") + " °C, door shut"),
        ("Flow ratio", s("aero", "/filament_flow_ratio/0")),
        ("Layer, line", s("aero", "/layer_height") + " mm high, " + s("aero", "/line_width") + " mm wide"),
        ("Wall loops", s("aero", "/wall_loops")),
        ("Fill, top skin, bottom skin", s("aero", "/sparse_infill_density") + ", " + s("aero", "/top_shell_layers") + ", " + s("aero", "/bottom_shell_layers")),
        ("Part fan", s("aero", "/fan_min_speed/0") + " to " + s("aero", "/fan_max_speed/0") + " %"),
        ("Most plastic a second", s("aero", "/filament_max_volumetric_speed/0") + " mm³"),
        ("First-layer trim on Mark2", "+" + s("aeroflight", "/requested_z_trim_mm") + " mm"),
    ])
    needs = bullets([
        ("A smooth plate with glue.",
         "Five starts on textured PEI, the plate PET-GF prints on. Of the first: &ldquo;It did, eventually, adhere to the bed, after "
         "more layers were added, but then it peeled off *very* easily.&rdquo; Before the sixth: &ldquo;Engineering plate is glued and "
         "loaded now. Textured plate is a no go.&rdquo;"),
        ("A head start.",
         "The printer&rsquo;s own short start line &ldquo;does not adhere to the bed at all. It just raises right up,&rdquo; and was "
         f"dragged into the part. From the fourth start on, a strip of {s('aerostrip', '/priming_strip_review/rows')} passes in the front "
         "corner prints first."),
        ("A dry box.",
         f"Dried at {s('aerodry', '/sources/0/official_parameters/forced_air_drying_temperature_c')} °C for "
         f"{s('aerodry', '/sources/0/official_parameters/forced_air_drying_duration_h')} hours and kept under "
         f"{s('aerodry', '/sources/0/official_parameters/printing_and_storage_rh_percent_max_exclusive')} % humidity, the maker&rsquo;s "
         "figures. The first six starts fed from the AMS HT. Of the seventh: &ldquo;&hellip;we are now using the polymaker drybox and "
         "that is working better.&rdquo;"),
    ])
    body = (
        b.head("The plastic", "It prints lighter than it feeds.",
               "ASA Aero foams when it is heated. It swells in the nozzle, so the printer feeds about half the plastic of an "
               "ordinary line and the foam makes up the rest.", size=168)
        + b.scope(SCOPE, not_tried="Mark 1")
        + b.row(
            ("0 0 1060px", f'<figure>{foam_drawing()}<figcaption class="cap"><span class="lab">Half the plastic, the same line</span>'
                           'The slicer works out the plastic for a line and multiplies it by the flow ratio. The spool weighs '
                           f'{s("aero", "/filament_density/0")} grams per cubic centimetre, about the same as water. What comes out of the '
                           'nozzle weighs less. How much less depends on heat, speed and flow, and we have not measured it.'
                           '</figcaption></figure>'),
            '<h2>The recipe</h2><p class="tiny" style="margin-bottom:14px">Read from the float&rsquo;s project file as this book is bound. '
            'The filament settings are the maker&rsquo;s stock profile for this printer. The walls are ours (see the third page).</p>' + recipe,
            gap=70, style="margin-top:34px")
        + b.rulebar(32, 32)
        + b.row(
            ("0 0 900px",
             '<h2>Why the floats are foam</h2>'
             '<p class="small" style="font-size:35px">A level float rides in the carbonator and in each flavor reservoir, and it has to float '
             'while carrying a magnet. Solid PETG and PET-GF both sink. The float was first drawn as a foam core sealed inside a clear PETG '
             'shell, and the first night&rsquo;s prints were that core. The next day it became foam and nothing else.</p>'
             + b.quote("&hellip;starting simpler seems better to me, generally speaking.", "DEREK · 3 OCTOBER 2026", size=38)
             + f'<div style="display:flex; gap:26px; align-items:center; margin-top:22px">'
               f'<div style="position:relative; flex:0 0 {PW}px; height:{PH}px"><img src="art/{cut}" alt="The float cut in half, with a ring magnet in a pocket at mid height" '
               f'style="position:absolute; left:0; top:0; width:{PW}px; height:{PH}px">{discs}</div><div>{legend}</div></div>'),
            '<h2>What it needed, found in one night</h2>'
            '<p class="tiny" style="margin-bottom:8px">Mark2, from 22:20 on 2 October 2026. Seven starts in about three hours; the seventh, '
            'which Derek started at the printer, ran to the end.</p>'
            f'<div style="max-width:1180px">{night_strip()}</div><div style="margin-top:20px">{needs}</div>',
            gap=70)
        + b.still_open(
            "The strip, the plate and the dry box arrived on three starts in a row, and only the last of them ran to the end, so the record "
            "cannot say what each one did. "
            f"Nothing about the finished foam has been measured. The float is sized on an assumed {s('aerodesign', '/sizing/design_foam_density_g_cc')} "
            f"g/cm³, for {s('aerodesign', '/sizing/minimum_reserve_lift_g')} g of spare lift with its {s('aerodesign', '/magnet/mass_g')} g magnet "
            "aboard. None has been weighed, floated or soaked on the record.")
        + '<div style="margin-top:20px">'
        + b.record(b.link("The float&rsquo;s sums", f"{A}/README.md"),
                   b.link("The maker&rsquo;s figures", f"{F}/asa-aero-research.md"),
                   b.link("The first start", f"{NIGHT}/v1/physical-observations.json"),
                   b.link("The start line", f"{NIGHT}/v3/physical-observations.json"),
                   b.link("The plate", f"{NIGHT}/v5/physical-observations.json"),
                   b.link("The print that finished", f"{NIGHT}/v6/operator-print.json"),
                   b.link("Drying", "hardware/ledger/tools.md", anchor="what-dries-where")) + "</div>"
    )
    return Page("it-prints-lighter-than-it-feeds", "ASA Aero: it prints lighter than it feeds", "aero", body, right="The plastic")


# ----------------------------------------------------------------------------- page 2: around a magnet
def _words(n):
    return {1: "ONE LAYER", 2: "TWO LAYERS", 3: "THREE LAYERS"}.get(n, f"{n} LAYERS")


def pocket_panel(x0, bed, src):
    """One side of the float in section, from the bore outwards, drawn course by course around the
    magnet pocket. Every height comes from the slice review named by src."""
    layer = float(b.value("aerodesign", "/print_intent/layer_height_mm"))
    thick = float(b.value("aerodesign", "/magnet/thickness_mm"))
    seat = float(b.value(src, "/magnet_pause_review/printed_seat_top_z_mm"))
    last_open = float(b.value(src, "/magnet_pause_review/last_open_pocket_layer_z_mm"))
    below = 3
    open_rows = round((last_open - seat) / layer)
    cover = below + open_rows
    spare = round((last_open - seat - thick) / layer)
    xb, xp0 = x0 + bx(1), x0 + bx(5)
    xp1, xe = xp0 + bx(11), xp0 + bx(13)
    g = [fblock(xb, xe, 0, below - 1, bed),
         fblock(xb, xp0, below, cover - 1, bed), fblock(xp1, xe, below, cover - 1, bed),
         fblock(xb, xe, cover, cover, bed, hot=True)]
    y_seat, y_pause = k.row_y(below - 1, bed), k.row_y(cover - 1, bed)
    mh = thick / layer * k.ROW_H
    ym = y_seat - mh
    g.append(f'<rect x="{k.n(xp0 + 18)}" y="{k.n(ym)}" width="{k.n(xp1 - xp0 - 36)}" height="{k.n(mh)}" rx="5" fill="{STEEL}"/>')
    g.append(k.label((xp0 + xp1) / 2, y_seat - mh / 2 + 10, "RING MAGNET", 30, anchor="middle", fill="white", weight=600))
    g.append(k.line(x0, y_pause - 50, x0, bed + 14, k.FAINT, 3, dash="26 8 5 8"))      # the bore's centre line
    # the pause, and the space left over the magnet
    g.append(k.line(xb - 6, y_pause, xe + 268, y_pause, k.INK, 3, dash="12 9"))
    g.append(k.label(xe + 20, y_pause - 46, "THE PAUSE", 27, fill=k.INK, weight=600))
    g.append(k.label(xe + 20, y_pause - 13, "AFTER LAYER " + s(src, "/magnet_pause_review/completed_layers_before_pause"), 27))
    g.append(k.line(xp1 - 9, ym, xp1 - 9, y_pause, k.INK, 3))
    g.append(k.line(xp1 - 9, (ym + y_pause) / 2, xe + 14, y_pause + 66, k.INK, 3))
    g.append(k.label(xe + 20, y_pause + 76, "SPACE OVER IT:", 27))
    g.append(k.label(xe + 20, y_pause + 110, "ABOUT " + _words(spare), 27, fill=k.INK, weight=600))
    # names along the bottom and over the top
    g.append(k.label((xb + xp0) / 2, bed + 46, "COLLAR", 27, anchor="middle"))
    g.append(k.label((xp0 + xp1) / 2 - 40, bed + 46, "THE SEAT", 27, anchor="middle", fill=k.INK, weight=600))
    g.append(k.arrow((xp0 + xp1) / 2 + 60, bed + 34, (xp0 + xp1) / 2 + 60, y_seat + 6, k.INK, 3))
    g.append(k.label(xe, bed + 46, "OUTER BAND", 27, anchor="end"))
    g.append(k.label(x0 + 8, y_pause - 62, "BORE", 25, fill=k.FAINT))
    g.append(k.label((xb + xe) / 2, k.row_y(cover, bed) - 20, "FIRST COURSE OVER THE MAGNET", 27, anchor="middle", fill=k.HOT, weight=600))
    return "".join(g)


def key(x, y):
    """Where the slice is in the whole float."""
    d, h = float(b.value("aerodesign", "/dimensions_mm/diameter")), float(b.value("aerodesign", "/dimensions_mm/height"))
    bore, mid = float(b.value("aerodesign", "/dimensions_mm/guide_bore")), float(b.value("aerodesign", "/dimensions_mm/magnet_midplane"))
    od, idm, th = (float(b.value("aerodesign", "/magnet/" + f)) for f in ("od_mm", "id_mm", "thickness_mm"))
    u = 6.0
    cxm, ymid = x + d / 2 * u, y + (h - mid) * u
    g = [f'<rect x="{k.n(x)}" y="{k.n(y)}" width="{k.n(d * u)}" height="{k.n(h * u)}" fill="{k.COLD}"/>',
         f'<rect x="{k.n(cxm - bore / 2 * u)}" y="{k.n(y - 2)}" width="{k.n(bore * u)}" height="{k.n(h * u + 4)}" fill="white"/>']
    for side in (-1, 1):
        x_in = cxm + side * idm / 2 * u
        x_out = cxm + side * od / 2 * u
        g.append(f'<rect x="{k.n(min(x_in, x_out))}" y="{k.n(ymid - th / 2 * u)}" width="{k.n(abs(x_out - x_in))}" height="{k.n(th * u)}" fill="{STEEL}"/>')
    g.append(f'<rect x="{k.n(cxm)}" y="{k.n(ymid - 22)}" width="{k.n(13.5 * u)}" height="42" fill="none" stroke="{k.HOT}" stroke-width="4"/>')
    g.append(k.label(x, y - 50, "THE WHOLE FLOAT", 23) + k.label(x, y - 20, "SLICE BOXED", 23, fill=k.HOT))
    return "".join(g)


def pocket_drawing():
    W, H, BED = 2340, 750, 28 * k.ROW_H
    g = [pocket_panel(24, BED, "aeroprint"), pocket_panel(24 + 1050, BED, "aeroflight"), key(2340 - 224, 440)]
    return k.svg(W, H, "".join(g), "The magnet pocket as it printed on 3 October 2026, and as it is drawn now",
                 "Two sections through one side of the float, from the bore outwards, with every course drawn. In each, foam courses rise "
                 "either side of an open pocket, a dark ring magnet sits on the pocket floor, a dashed line marks where the print pauses, and "
                 "one orange course is laid across collar, magnet and outer band. On the left, the float of 3 October: the pause comes after "
                 "layer 79 and about one layer of space is left over the magnet. On the right, the float as drawn now: the pocket is one "
                 "layer deeper and about two layers of space are left. A small key shows where the slice sits in the whole float.")


def magnet():
    sources()
    photo = b.asset("aero-magnet-overprint.jpg", f"{A}/mark2-print/v1/evidence/magnet-insertion-overprint-2026-10-03.jpg")
    caps = ('<div style="display:flex; gap:56px; margin-top:14px">'
            '<p class="cap" style="margin:0; flex:0 0 930px"><span class="lab">3 October 2026 · as it printed</span>The pocket walls stopped '
            'about one layer above the top of the magnet, so the first course across had almost no room under it.</p>'
            '<p class="cap" style="margin:0; flex:1 1 0"><span class="lab">The float as it is drawn now</span>The pocket is one layer deeper, '
            f'{s("aeroprintdesign", "/dimensions_mm/pocket_depth")} mm then and {s("aerodesign", "/dimensions_mm/pocket_depth")} mm now, and the '
            'pause comes one layer later.</p></div>')
    body = (
        b.head("Print around a magnet", "Pause. Seat the magnet. Print on.",
               "The level float has a ring magnet closed inside it, with no lid and no seam. The printer builds the float up to the top "
               "of an open pocket and stops. The magnet is pushed in by hand. The printer starts again and lays the rest of the float "
               "over it.", size=140)
        + b.scope(SCOPE, not_tried="Mark 1")
        + f'<figure style="margin-top:30px">{pocket_drawing()}{caps}</figure>'
        + b.rulebar(32, 32)
        + b.row(
            ("0 0 720px", b.fig(photo, "A cream-white foam float on the print bed with the toolhead over it, a grey ring showing on its top face",
                                "3 October 2026 · Mark2 · ASA Aero",
                                "The float under the toolhead while foam goes on over the magnet. The grey ring is the magnet, part "
                                "covered.", h=560, pos="50% 12%", zoom=100)
             + '<h3 style="margin-top:26px">What the printer says at the pause</h3>'
               f'<p class="small" style="font-size:33px; margin:0; padding:18px 22px; background:var(--wash)">{s("aeroflight", "/magnet_pause_review/pause_message")}</p>'),
            b.quote("It worked. Maybe one more layer of space needed above the magnet for next time, as the first layer on the magnet "
                    "was a bit too tight, but the second layer went down beautifully.", "DEREK · 3 OCTOBER 2026", size=45)
            + '<div class="grid2" style="margin-top:34px; gap:50px">'
            + '<div><h2>What happened</h2>'
              f'<p class="small" style="font-size:35px; margin:0">The float went to Mark2 at about three in the afternoon. After layer '
              f'{s("aeroprint", "/magnet_pause_review/completed_layers_before_pause")} of {s("aeroprint", "/layers")} the printer parked and '
              'waited. Derek pushed one ring into the pocket and pressed resume. The pocket was drawn one layer deeper the same day.</p></div>'
            + '<div><h2>Push in, not drop in</h2>'
              '<p class="small" style="font-size:35px; margin:0">The nozzle is steel and passes close over the magnet. Before the print: '
              '&ldquo;&hellip;I think it might just work, especially because the magnet actually sits and grips quite well in the ASA '
              'Aero.&rdquo; It did. The next day the same pause in PET-GF, in a pump cartridge, left a magnet that &ldquo;rattles&rdquo;: it '
              'had been &ldquo;too easy to "drop the magnet in" instead of "push the magnet in" as had happened with the aero that worked '
              'even better.&rdquo;</p></div>'
            + '</div>'
            + b.still_open(
                "The deeper pocket went onto a plate of three floats on 8 October 2026, and nobody wrote down how it came out. No finished "
                f"float has been cut open or held under water. The magnet&rsquo;s maker rates it for {s('aerodesign', '/magnet/continuous_operating_limit_c')} "
                f"°C in steady use, and foam at {s('aero', '/nozzle_temperature/0')} °C is laid straight onto it. What that costs the magnet has "
                "not been measured. What is on record: that evening the float worked a reed switch from 20 mm away."),
            gap=70)
        + '<div style="margin-top:24px">'
        + b.record(b.link("Derek&rsquo;s report and the photograph", f"{A}/physical-observations.json"),
                   b.link("The slice that printed", f"{A}/mark2-print/v1/float-preflight.json"),
                   b.link("The slice as it is now", f"{A}/mark2-print/v2/float-preflight.json"),
                   b.link("The three-float plate", f"{THREE}/README.md"),
                   f'<a href="{b.GITHUB}/commit/c9fe945fd">The PET-GF magnet that rattled</a>',
                   b.link("Reed reach", f"{F}/README.md", anchor="reed-reach")) + "</div>"
    )
    return Page("pause-seat-the-magnet-print-on", "ASA Aero: pause, seat the magnet, print on", "aero", body, right="Around a magnet")


# ----------------------------------------------------------------------------- page 3: all walls
def _pt(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy - r * math.sin(a)


def rings(cx, cy, radii, color=k.COLD, width=17):
    return "".join(f'<circle cx="{k.n(cx)}" cy="{k.n(cy)}" r="{k.n(r)}" fill="none" stroke="{color}" stroke-width="{width}"/>' for r in radii)


def walls_and_fill():
    W, H, CY = 1000, 640, 292
    g = []
    for cx, name in ((222, "CORE"), (778, "INSERT")):
        g.append(f'<circle cx="{cx}" cy="{CY}" r="204" fill="{k.WASH}"/>')
        g.append(rings(cx, CY, (190, 169, 148)) + rings(cx, CY, (82, 61, 40)))
        g.append(f'<circle cx="{cx}" cy="{CY}" r="115" fill="none" stroke="{k.COLD}" stroke-width="44" stroke-dasharray="7 8"/>')
        g.append(f'<circle cx="{cx}" cy="{CY}" r="29" fill="white"/>')
        g.append(k.label(cx, CY + 252, name, 25, anchor="middle"))
    ax, bxx = 222 + 190, 778 - 190
    g.append(f'<path d="M{ax} {CY} L{bxx} {CY}" fill="none" stroke="{k.INK}" stroke-width="6" stroke-dasharray="4 15" stroke-linecap="round"/>')
    for x, y, r in ((ax + 44, CY - 5, 7), (ax + 96, CY + 6, 5), (bxx - 30, CY - 4, 6)):
        g.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{k.HOT}"/>')
    g.append(k.road(f"M{bxx + 4} {CY - 4} c 10 -22, 26 -18, 20 6", k.HOT, 9))
    g.append(f'<circle cx="{ax}" cy="{CY}" r="15" fill="white" stroke="{k.INK}" stroke-width="6"/>' + k.nozzle_top(bxx - 2, CY, 34))
    g.append(k.label(500, 46, "A JUMP EVERY LAYER", 25, anchor="middle", fill=k.INK, weight=600) + k.line(500, 60, 500, CY - 16))
    g.append(k.label(500, 600, "BITS, CARRIED AND LEFT", 25, anchor="middle", fill=k.HOT, weight=600) + k.line(500, 574, bxx + 12, CY + 22, k.HOT))
    g.append(k.label(24, 46, "THREE WALLS") + k.line(96, 58, 92, CY - 176))
    g.append(k.label(976, 46, "ZIGZAG FILL", anchor="end") + k.line(894, 58, 848, CY - 96))
    return k.svg(W, H, "".join(g), "Seen from above: two parts on one plate, each three walls around zigzag fill, with a jump between them",
                 "Two round parts side by side. Each has three wall loops at its outside and three around its bore, with hatched fill "
                 "between. A dotted line shows the nozzle travelling from one part to the other without printing. Small orange bits "
                 "lie along the dotted line and are stuck to the wall where the nozzle lands.")


def all_walls():
    W, H, CX, CY = 1000, 640, 500, 300
    radii = [225 - 21 * i for i in range(9)]
    g = [f'<circle cx="{CX}" cy="{CY}" r="240" fill="{k.WASH}"/>', rings(CX, CY, radii), f'<circle cx="{CX}" cy="{CY}" r="46" fill="white"/>']
    # the loop being laid, and the nozzle on it
    r = radii[4]
    (sx, sy), (ex, ey) = _pt(CX, CY, r, 82), _pt(CX, CY, r, 318)
    g.append(f'<path d="M{k.n(sx)} {k.n(sy)} A{r} {r} 0 1 1 {k.n(ex)} {k.n(ey)}" fill="none" stroke="{k.HOT}" stroke-width="17" stroke-linecap="round"/>')
    g.append(k.nozzle_top(ex, ey, 34))
    # the short steps from loop to loop, at the seam
    steps = []
    for i in range(len(radii) - 1):
        (x0, y0), (x1, y1) = _pt(CX, CY, radii[i], 90 + (4 if i % 2 else -4)), _pt(CX, CY, radii[i + 1], 90 + (-4 if i % 2 else 4))
        steps.append(f"M{k.n(x0)} {k.n(y0)}L{k.n(x1)} {k.n(y1)}")
    g.append(f'<path d="{"".join(steps)}" fill="none" stroke="{k.INK}" stroke-width="6" stroke-dasharray="3 9" stroke-linecap="round"/>')
    g.append(k.label(24, 46, "A SHORT STEP FROM EACH LOOP TO THE NEXT", 25, fill=k.INK) + k.line(430, 58, CX - 14, CY - 198))
    g.append(k.label(CX, 600, "LOOP INSIDE LOOP, OUTSIDE WALL TO BORE", 25, anchor="middle", fill=k.HOT, weight=600) + k.line(CX, 574, CX, CY + 152, k.HOT))
    g.append(k.label(CX, CY + 10, "BORE", 23, anchor="middle", fill=k.FAINT))
    return k.svg(W, H, "".join(g), "Seen from above: one part printed as loops inside loops",
                 "One round part made of nine nested loops from its outside wall to its bore. One loop is orange with the nozzle on "
                 "it. At the top a short dotted zigzag crosses from each loop to the next. Nothing crosses open ground.")


def close_together():
    W, H = 560, 500
    R, gap = 118, 14
    pitch = 2 * R + gap
    cx, cy = W / 2, 262
    cs = [(cx - pitch / 2, cy + pitch * 0.2887), (cx + pitch / 2, cy + pitch * 0.2887), (cx, cy - pitch * 0.5774)]
    g, seams = [], []
    for x, y in cs:
        g.append(f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="{R + 4}" fill="{k.WASH}"/>' + rings(x, y, [R - 9 - 19 * i for i in range(5)], width=15)
                 + f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="22" fill="white"/>')
        a = math.atan2(cy - y, cx - x)
        seams.append((x + (R - 9) * math.cos(a), y + (R - 9) * math.sin(a)))
    d = "M" + " L".join(f"{k.n(x)} {k.n(y)}" for x, y in seams) + " Z"
    g.append(f'<path d="{d}" fill="none" stroke="{k.INK}" stroke-width="5" stroke-dasharray="3 8" stroke-linecap="round"/>')
    g += [f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="11" fill="{k.HOT}"/>' for x, y in seams]
    return k.svg(W, H, "".join(g), "Three floats close together with their seams turned inwards",
                 "Three round floats in a triangle with a narrow gap between them. An orange dot on each marks where every layer of "
                 "that float starts and stops, and all three dots face the middle, so the hops between floats are short.")


def walls():
    sources()
    tiles = ('<div class="grid2" style="margin-top:34px">'
             f'<figure>{walls_and_fill()}<figcaption class="cap"><span class="lab">The first night · 2 and 3 October 2026</span>The plates that were '
             'sent: two parts side by side, each three walls around solid zigzag fill, with a jump between them on every layer. The one '
             'print that ran to the end came off with flaking.</figcaption></figure>'
             f'<figure>{all_walls()}<figcaption class="cap"><span class="lab">What Derek asked for</span>One part on the plate, and nothing in it but '
             'walls. The walls are set to a number too big to reach, so the slicer keeps nesting loops until the part is full.</figcaption></figure></div>')
    body = (
        b.head("Travel", "Every jump carries a bit along.",
               "When the nozzle moves without printing, ASA Aero keeps coming out of it. A bit goes along on every move and is left "
               "wherever the nozzle lands. So the float is printed with as few of those moves as its shape allows.", size=150)
        + b.scope(SCOPE, not_tried="Mark 1")
        + tiles
        + b.rulebar(34, 34)
        + b.row(
            b.quote("The one more issue is that every time the nozzle moves and is *not* printing the filament continues to extrude just "
                    "because of its expansion when heating, and so we end up with bits carried around on each \"jump\".",
                    "DEREK · 3 OCTOBER 2026, WATCHING THE FIRST PRINT THAT RAN", size=40)
            + '<div style="margin-top:34px">'
            + b.quote("So I&rsquo;m thinking we want to try one piece at a time, and with that piece, just do like 300 walls so that it is all "
                      "walls and we get concentric the whole way, and no jumps.", "DEREK · THE SAME NIGHT", size=40) + "</div>"
            + '<div class="grid2" style="margin-top:38px; gap:44px">'
            + b.stat(s("aeroprint", "/travel_review/object_retraction_count"),
                     f"stops and restarts were still in the all-walls float that printed on 3 October, across {s('aeroprint', '/layers')} layers.")
            + b.stat('10 <span>mm</span>', "was the longest of those moves inside any one layer. All walls is fewer and shorter jumps. It is not none.", hot=True)
            + "</div>",
            ("0 0 800px",
             f'<div style="display:flex; gap:30px; align-items:center"><div style="flex:0 0 400px">{close_together()}</div>'
             '<div><h2>Close together</h2><p class="small" style="font-size:34px; margin:0">On 8 October 2026 three floats went on one plate, '
             '2 mm apart. The orange dot is where each layer of a float starts and stops. All three face the middle.</p></div></div>'
             '<p class="small" style="font-size:34px; margin-top:22px">Derek asked for it that way: &ldquo;I&rsquo;d like the floats to be close '
             'together, so that the distance between objects is small.&rdquo; Four days later, printing soft TPU:</p>'
             + b.quote("With both ASA Aero and TPU I am finding that the distance between objects increases risk of problems on these "
                       "\"unclean start/stop\" filaments.", "DEREK · 12 OCTOBER 2026", size=38)),
            gap=70)
        + b.still_open(
            "Whether the all-walls float came off clean of bits was not written down; what Derek reported of it was the magnet. The plate of "
            "three has no written result. His reading that the foam keeps swelling in the heat has not been tested. Nor has his other idea "
            f"from that night, &ldquo;maybe we just need to reduce the volume a bit&rdquo;: the flow ratio is still the maker&rsquo;s {s('aero', '/filament_flow_ratio/0')}.")
        + '<div style="margin-top:22px">'
        + b.record(b.link("What Derek saw on the first print that ran", f"{NIGHT}/v6/operator-print.json"),
                   b.link("The all-walls trial and what travel was left", f"{NIGHT}/v7/README.md"),
                   b.link("The float&rsquo;s slice, move by move", f"{A}/mark2-print/v1/float-preflight.json"),
                   b.link("Three floats close together", f"{THREE}/README.md"),
                   b.link("Keeping parts close", "tools/bambu-printers.md", anchor="placement-on-unseasoned-plates")) + "</div>"
    )
    return Page("every-jump-carries-a-bit-along", "ASA Aero: every jump carries a bit along", "aero", body, right="All walls")


def pages():
    return [plastic(), magnet(), walls()]
