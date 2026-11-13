"""Front matter: the cover, what the book is, its contents and the machine by plastic."""
import subprocess

import bookkit as b
import svgkit as k
from bookkit import Page
from chapters import _mine
from proj import projector


def swatch(kind):
    g = [k.defs()]
    if kind == "cold":
        g.append(k.block(0, 126, 0, 1, 56))
    elif kind == "hot":
        g.append(k.block(0, 126, 0, 0, 56) + k.strand(0, 126, 8))
    elif kind == "scaffold":
        g.append(k.scaffold(0, 126, 8, 56))
    else:
        g.append(k.missing(3, 10, 123, 54))
    return k.svg(126, 64, "".join(g), kind, style="width:150px; flex:none")


# --------------------------------------------------------------------------- about
def about():
    src = b.RUN / "preview" / "anyfil" / "out" / "02-a-bridge-needs-two-landings.png"
    mini = b.ART / "about-a-page.jpg"
    if src.exists():
        b.ART.mkdir(parents=True, exist_ok=True)
        subprocess.run(["magick", str(src), "-resize", "1400x1400>", "-quality", "84", "-strip", str(mini)], capture_output=True)
    legend = [("cold", "Plastic already printed."), ("hot", "The course being laid, still soft."),
              ("scaffold", "Printed to be thrown away: a fin or a support."), ("gone", "Something that was cut away.")]
    leg = "".join(f'<div style="display:flex; gap:28px; align-items:center; margin-bottom:20px">{swatch(kd)}<p class="small" style="margin:0">{t}</p></div>' for kd, t in legend)
    marks = [(1, 1, 14.3, "The rule", "One line you could say across a workbench."),
             (2, 1, 22.0, "Where it holds", "Which plastic, printer, plate and nozzle the evidence comes from."),
             (3, 51, 40, "The print that taught it", "Photographed, with its date and printer."),
             (4, 51, 66.5, "Derek&rsquo;s words", "Exactly as he typed them, beside an orange bar."),
             (5, 70, 76.5, "In the record", "Links to the files that hold the evidence.")]
    discs = "".join(f'<span class="num on-model hot" style="left:{x}%; top:{t}%">{n}</span>' for n, x, t, _, _ in marks)
    notes = "".join(f'<div style="display:flex; gap:22px; margin-bottom:18px"><span class="num hot">{n}</span><p class="small" style="margin:0"><b>{a}.</b> {d}</p></div>' for n, _, _, a, d in marks)
    leg = "".join(f'<div style="display:flex; gap:24px; align-items:center">{swatch(kd)}<p class="small" style="margin:0">{t}</p></div>' for kd, t in legend)
    body = (
        b.head("What this book is", "Every page is one of our prints.",
               "Nearly everything you can see or touch on the Home Soda Machine comes off two desktop printers. Getting there took nine months "
               "of prints that failed for reasons. This book is the reasons, each shown on the print that taught it.", size=170)
        + b.row(
            '<p class="small">On 5 April 2026, a month into the project, a section of general advice about 3D printing was deleted from the '
            'repository. An AI had written it, and it was not about anything we had printed.</p>'
            '<p class="small">Everything here is the opposite. Each page starts from a print that exists: its date, its printer, its plastic and a '
            'photograph. The rule at the top is what that print taught, and the page says how far the lesson has been tested.</p>'
            '<h2 style="margin-top:40px">It is sorted by plastic</h2>'
            '<p class="small">Most of what a print teaches belongs to the plastic it was made of. PET-GF wants its fan off; soft TPU curls without '
            'it. A first layer that is right for one is wrong for the next. So after a short part on what is plain geometry, the book has '
            'a part for each plastic, and every page says which one it is about.</p>'
            '<h2 style="margin-top:40px">It says what it does not know</h2>'
            '<p class="small"><span class="tag open" style="margin-right:14px">Still open</span>marks what one print suggested and nothing has '
            'confirmed, or a result that changed two things at once.</p>'
            '<h2 style="margin-top:40px">Its numbers do not go stale</h2>'
            '<p class="small">A setting in the current recipe is read from its project file each time the book is put together. A number from a '
            'trial stays as it was measured, with its date.</p>'
            '<h2 style="margin-top:40px">It is written for agents too</h2>'
            '<p class="small" style="margin:0">The machine is designed and printed with AI agents, who start each day knowing none of this. Every page is a '
            'plain file in the repository, so what a person reads here and what an agent reads there are the same words.</p>',
            ("0 0 940px",
             f'<div style="position:relative; margin-left:44px; box-shadow:0 0 0 3px var(--line)"><img src="art/about-a-page.jpg" alt="A page of this book" style="display:block; width:100%">{discs}</div>'
             f'<div style="margin:34px 0 0 0">{notes}</div>'),
            gap=90, style="margin-top:44px")
        + b.rulebar(30, 28)
        + '<h3>How to read a drawing</h3>' + f'<div class="grid4" style="margin-top:20px; gap:30px">{leg}</div>'
    )
    return Page("every-page-is-one-of-our-prints", "What this book is", "front", body, right="What this book is")


# --------------------------------------------------------------------------- contents
def contents():
    groups = []
    for key, (title, _, color, _) in b.PARTS.items():
        rows = [(t, n) for part, t, n in b.TOC if part == key and n > 4] if key != "front" else []
        if not rows:
            continue
        lines = "".join(f'<div style="display:flex; justify-content:space-between; gap:20px; padding:5px 0"><span>{(lambda x: x[0].upper() + x[1:])(t.split(": ", 1)[-1])}</span>'
                        f'<span class="mono" style="color:var(--faint)">{n:02d}</span></div>' for t, n in rows)
        groups.append(
            f'<div style="break-inside:avoid; margin-bottom:46px">'
            f'<div style="display:flex; align-items:baseline; gap:18px; padding-bottom:10px; border-bottom:3px solid {color}">'
            f'<span style="display:inline-block; width:26px; height:26px; background:{color}"></span>'
            f'<span style="font:650 46px/1.1 \'IBM Plex Sans\'; color:var(--ink)">{title}</span></div>'
            f'<div style="font-size:35px; line-height:1.3; color:var(--text); margin-top:12px">{lines}</div></div>')
    body = (
        b.head("Contents", "One plastic at a time.", size=150, top=56)
        + f'<div style="columns:3; column-gap:56px; margin-top:50px">{"".join(groups)}</div>'
    )
    return Page("contents", "Contents", "front", body, right="Contents")


# --------------------------------------------------------------------------- the machine by plastic
PETGF = ["enclosure-front-bottom", "enclosure-front-top", "enclosure-back-bottom", "enclosure-back-top", "enclosure-pump-retainer-a",
         "enclosure-pump-retainer-b", "display-cover", "funnel-frame", "elbow-cradle", "cold-core/foam-shell", "cold-core/foam-cap-bottom",
         "cold-core/foam-cap-lid-top", "nameplate", "bulkhead-ring-carb", "bulkhead-ring-co2", "bulkhead-ring-drain", "bulkhead-ring-flavor-a",
         "bulkhead-ring-flavor-b", "bulkhead-ring-water", "asse-snap-cap", "meter-snap-cap", "pisco-snap-cap", "regulator-snap-cap",
         "cold-core/pump-snap-cap", "soda-bend-holder", "cold-core/reservoir-b-fill-guide"]
PETG = ["cold-core/reservoir-a", "cold-core/reservoir-b", "cold-core/reservoir-a-cap", "cold-core/reservoir-b-cap", "funnel-cover",
        "cold-core/prv-shroud", "cold-core/reed-bridge", "fuse-clamp", "status-plate"]
TPU = ["cold-core/reservoir-a-gasket", "cold-core/reservoir-b-gasket", "cold-core/reservoir-grip-a-air", "cold-core/reservoir-grip-a-draw",
       "cold-core/reservoir-grip-a-fill", "cold-core/reservoir-grip-b-air", "cold-core/reservoir-grip-b-draw", "cold-core/reservoir-grip-b-fill",
       "display-gasket", "asse-drain-adapter"]
AERO = ["cold-core/float-a/1", "cold-core/float-b/1", "cold-core/float-carb/1", "cold-core/float-a", "cold-core/float-b", "cold-core/float-carb",
        "float-a", "float-b", "float-carb"]


def by_plastic():
    col = {k_: b.PARTS[k_][2] for k_ in ("petgf", "petg", "tpu", "aero")}
    mats = [{"names": PETGF, "color": "#4b5864", "roughness": 0.9}, {"names": PETG, "color": "#3bb6d1", "roughness": 0.5},
            {"names": TPU, "color": "#d04fa8", "roughness": 0.7}, {"names": AERO, "color": "#edbd3f", "roughness": 0.8}]
    cam, target, span, size = [1.0, -0.55, 0.38], [-12.0, 238.0, 172.0], 232, (2170, 1560)
    img = b.render("front-machine-by-plastic.png", dict(step="manifold-layout/enclosure-assembly.step", size="2170x1560", cam=cam, target=target, span=span,
                                                      only=PETGF + PETG + TPU + AERO, context="hide", materials=mats,
                                                      section={"normal": [1, 0, 0], "at": [-12, 0, 0]}))
    pm = projector(cam, target, span, size)
    tags = [("PET-GF · enclosure", col["petgf"], [-12, 60, 120]), ("PET-GF · cold core shell", col["petgf"], [-12, 320, 12]),
            ("PETG · reservoirs", col["petg"], [-12, 235, 100]), ("PETG · funnel cover", col["petg"], [-12, 180, 358]),
            ("ASA Aero · floats", col["aero"], [-32, 430, 127]), ("TPU · cap gaskets and tube grips", col["tpu"], [-12, 414, 228])]
    pins = "".join(
        f'<span style="position:absolute; left:{pm(pt)[0]:.0f}px; top:{pm(pt)[1]:.0f}px; transform:translate(-50%,-50%); padding:8px 18px 9px; '
        f'background:{c}; color:white; font:600 27px/1 \'IBM Plex Mono\', monospace; letter-spacing:.06em; white-space:nowrap; box-shadow:0 0 0 5px white">{t.upper()}</span>'
        for t, c, pt in tags)
    rows = [
        ("petgf", "PET-GF", "Everything stiff and everything you see.", "The four enclosure quadrants, the cold core&rsquo;s shell and caps, the faucet, the funnel frame, the snap caps, rings and labels."),
        ("petg", "PETG", "Whatever holds liquid, and a few small parts.", "Both flavor reservoirs and their caps, the funnel cover, the status plate, a shroud, a bridge and a clamp. The mold for the silicone funnel."),
        ("tpu", "TPU", "Whatever has to stretch or seal.", "Reservoir cap gaskets, tube grips, the display gasket, the drain adapter, and the pump elbows in development."),
        ("aero", "ASA Aero", "The one part that has to float.", "Three level floats, each printed around a magnet."),
        ("petcf", "PET-CF", "Nothing now.", "The faucet&rsquo;s first attempts, in the spring."),
    ]
    tab = "".join(
        f'<tr><th style="width:300px"><span class="tag" style="background:{b.PARTS[key][2]}">{name}</span></th>'
        f'<td style="width:640px"><b>{what}</b></td><td>{parts}</td></tr>' for key, name, what, parts in rows)
    body = (
        b.head("The machine", "Four plastics, each doing one job.",
               "The machine cut in half, with every printed part coloured by the plastic it is made of. Which plastic a part gets was decided "
               "by what the part has to do.", size=160, top=56)
        + f'<figure style="position:relative; height:1560px; margin-top:6px"><img src="art/{img}" alt="The machine cut in half from front to back" '
          f'style="position:absolute; left:0; top:0; width:2170px; height:1560px">{pins}'
          '<p class="mono" style="position:absolute; left:0; bottom:10px; margin:0; font-size:27px; line-height:1.5; letter-spacing:.08em; color:var(--muted)">'
          'BOUGHT PARTS, TUBES AND WIRING ARE HIDDEN<br>THE FAUCET, ALSO PET-GF, STANDS ON THE COUNTER ABOVE</p></figure>'
        + f'<table class="grid" style="margin-top:10px"><tbody>{tab}</tbody></table>'
        + '<div style="margin-top:26px">' + b.record(b.link("Every printed part and its plastic", "hardware/ledger/bom.md", anchor="7-printed-mechanical-parts"),
                                                     b.model_link("The machine in 3D", "solid: enclosure-front-bottom")) + "</div>"
    )
    return Page("four-plastics-each-doing-one-job", "The machine, by plastic", "front", body, right="The machine")


def pages():
    return [_mine.cover(), about(), contents(), by_plastic()]
