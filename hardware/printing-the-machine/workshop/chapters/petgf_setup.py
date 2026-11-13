"""PET-GF, setting up: the plastic, its recipe, its first layer on textured PEI, the plate's edge,
cooling, small parts, and what its surface shows. Seven pages that open the PET-GF part.
Each function returns one Page."""
import bookkit as b
import svgkit as k
from bookkit import Page

PP = "hardware/printed-parts"
ENC = f"{PP}/enclosure/enclosure"
COVER = f"{PP}/faucet/faucet-display-cover"
SHELL = f"{PP}/cold-core/foam-shell/prints"
STAND = f"{PP}/fixtures/fake-countertop"
CAPS = f"{PP}/enclosure/rear-equipment-caps/prints"
CLIP = "future/cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon"
CLIP_REV = "2f2d9c94a"       # holds the melted clip, its photographs and the cooled retry
PRINTERS = "tools/bambu-printers.md"
SETTINGS = "Metadata/project_settings.config"

# the PET-GF solids of the enclosure assembly, as the piece list names their plastic
PETGF_SOLIDS = ["enclosure-front-bottom", "enclosure-front-top", "enclosure-back-bottom", "enclosure-back-top",
                "enclosure-pump-retainer-a", "enclosure-pump-retainer-b", "display-cover", "funnel-frame", "elbow-cradle",
                "cold-core/foam-shell", "cold-core/foam-cap-bottom", "cold-core/foam-cap-lid-top", "asse-snap-cap",
                "meter-snap-cap", "pisco-snap-cap", "regulator-snap-cap", "cold-core/pump-snap-cap", "soda-bend-holder",
                "cold-core/reservoir-b-fill-guide"]


def _petgf():
    return b.source("petgf", f"{PP}/petgf.3mf", member=SETTINGS)


def _pieces():
    return b.source("petgf-setup-pieces", f"{PP}/enclosure/trial-preparation/pieces.json")


def _scalars():
    return b.source("scalars", "tools/hsm/shared-data/catalog/scalars.json")


def _tpu():
    return b.source("petgf-setup-tpu-sleeve",
                    f"{PP}/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/"
                    "2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.3mf", member=SETTINGS)


# ----------------------------------------------------------------------------- small helpers
def p(text, cls="small", style=""):
    st = f' style="{style}"' if style else ""
    return f'<p class="{cls}"{st}>{text}</p>'


def commit(text, sha):
    """A link to one commit, for evidence that lives in its message."""
    return f'<a href="{b.GITHUB}/commit/{sha}">{text}</a>'


def h3(text, style=""):
    st = f' style="{style}"' if style else ""
    return f"<h3{st}>{text}</h3>"


def tagged(src, alt, h, pos, tags, lab, cap):
    """A full-width photograph with small tags laid over it. tags: (text, left_px, top_px)."""
    marks = "".join(f'<span class="tag" style="position:absolute; left:{x}px; top:{y}px">{t}</span>' for t, x, y in tags)
    return (f'<figure><div style="position:relative"><img class="photo" src="art/{src}" alt="{alt}" '
            f'style="height:{h}px; object-position:{pos}">{marks}</div>'
            f'<figcaption class="cap"><span class="lab">{lab}</span>{cap}</figcaption></figure>')


def ghost_nozzle(x, y, s=1.0):
    """A nozzle that is not printing, drawn pale, its tip at (x, y)."""
    w, h = 74 * s, 96 * s
    return (f'<path d="M{k.n(x - 9 * s)} {k.n(y)} L{k.n(x + 9 * s)} {k.n(y)} L{k.n(x + w / 2)} {k.n(y - 44 * s)} '
            f'L{k.n(x + w / 2)} {k.n(y - h)} L{k.n(x - w / 2)} {k.n(y - h)} L{k.n(x - w / 2)} {k.n(y - 44 * s)} Z" fill="{k.FAINT}"/>')


def fan_glyph(x, y, r=40):
    """A fan seen face on."""
    blades = "".join(
        f'<path d="M{k.n(x)} {k.n(y)} q{k.n(r * 0.75 * c - r * 0.3 * s_)} {k.n(r * 0.75 * s_ + r * 0.3 * c)} {k.n(r * 0.86 * c)} {k.n(r * 0.86 * s_)}" '
        f'stroke="{k.INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
        for c, s_ in ((1.0, 0.0), (-0.5, 0.866), (-0.5, -0.866)))
    return (f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="{k.n(r)}" fill="white" stroke="{k.INK}" stroke-width="4"/>{blades}'
            f'<circle cx="{k.n(x)}" cy="{k.n(y)}" r="6" fill="{k.INK}"/>')


def air(x, y, n_=3, gap=20, length=36):
    """Short strokes of moving air, arriving at (x, y) from the upper right."""
    return "".join(k.line(x + i * gap, y - 4, x + i * gap + length * 0.5, y - 4 - length, k.INK, 4) for i in range(n_))


def texture(x0, x1, peak, depth=22, period=40, floor=46):
    """A textured plate in section: bumps whose tops are at peak, hatched underneath like the bed."""
    v = peak + depth
    d = [f"M{k.n(x0)} {k.n(v)}"]
    x = x0
    while x < x1 - 0.5:
        d.append(f"Q{k.n(x + period / 2)} {k.n(peak - depth)} {k.n(x + period)} {k.n(v)}")
        x += period
    d.append(f"L{k.n(x1)} {k.n(peak + floor)} L{k.n(x0)} {k.n(peak + floor)} Z")
    ticks = "".join(f"M{k.n(t)} {k.n(peak + floor + 4)}l-16 20" for t in k._frange(x0 + 18, x1, 18))
    return f'<path d="{"".join(d)}" fill="{k.INK}"/><path d="{ticks}" stroke="{k.INK}" stroke-width="3" fill="none"/>'


# ----------------------------------------------------------------------------- 1 the plastic
def plastic():
    _petgf()
    photo = b.asset("petgf-setup-two-plastics.jpg",
                    f"{PP}/cadlib/flute-evidence/01-flat-faces-raking-light-petgf-left-petg-right.jpeg", max_px=2000)
    machine = b.render("petgf-setup-machine.png", dict(
        step="manifold-layout/enclosure-assembly.step", cam=[1.0, -0.55, 0.38], target=[-77.0, 120.0, 172.0], span=232,
        size="1090x1010", section={"normal": [1, 0, 0], "at": [-12, 0, 0]}, context="hide", only=PETGF_SOLIDS, edges=True,
        materials=[{"names": PETGF_SOLIDS, "color": "#3a4654", "roughness": 0.9}]))
    hrc = b.setting("petgf", "/required_nozzle_HRC/0")
    traits = [
        ("Stiff", "A wall of it does not give. A clip has to be a long, broad, thin leaf before it will spring at all."),
        ("Matte", "A fine grain with no direction in it. On a flat face the layers do not show."),
        ("Weak between layers", "Bent across its layers, a thin wall splits. On 17 October 2026 two white covers cracked as a "
                                "display was pressed in."),
        ("No stretch", "A hard part pushed into a pocket a hair too small does not ease in. On 12 November 2026 the "
                       "pocket&rsquo;s edge snapped off."),
        ("Abrasive", f"Its profile asks for a nozzle of hardness HRC {hrc} or more. Ours are hardened steel, tungsten carbide "
                     "and diamond."),
    ]
    grid = "".join(f'<div><h2 style="font-size:40px">{t}</h2><p class="small" style="margin:0">{d}</p></div>' for t, d in traits)
    body = (
        b.head("The plastic", "It hides its layers and breaks along them.",
               "PET-GF is PET with short glass fibres mixed in. The glass makes a wall stiff and gives it a flat, grainy face on "
               "which the layers do not show. It also takes the stretch away: bent the wrong way, a thin wall splits between "
               "two layers.", lede_size=54)
        + b.scope("Polymaker Fiberon PET-GF15 · Mark 1 and Mark2 · textured PEI · hardened 0.4 mm nozzles",
                  not_tried="any other maker&rsquo;s glass-filled PET")
        + '<div style="margin-top:34px">'
        + tagged(photo, "Two printed enclosure fronts side by side, the left one matte and even, the right one covered in layer lines",
                 640, "50% 50%", [("PET-GF", 40, 34), ("PETG", 1290, 34)],
                 "26 August 2026 · the same enclosure front, printed in two plastics",
                 "Low sun across the inside faces. The PET-GF is one even grain. The PETG shows every layer, most of all on "
                 "the sloped ceiling. Edges and small features look the same in both. It is the large flat faces that give "
                 "the plastic away.")
        + "</div>"
        + f'<div class="grid5" style="margin-top:32px">{grid}</div>'
        + b.rulebar(36, 34)
        + b.row(
            ("0 0 500px", f'<img src="art/{machine}" alt="The enclosure cut open, showing only its PET-GF parts" style="display:block; width:500px; height:463px">'
                          + '<p class="cap" style="margin-top:4px"><span class="lab">Where it is</span>The enclosure and the shell '
                            'round the cold core, cut open. Everything drawn here is PET-GF.</p>'),
            '<h2>Most of the machine</h2>'
            + p("By weight it is most of the plastic we print: the four quadrants of the enclosure, the frame under the "
                "funnel, the cold core&rsquo;s shell, and out of this picture the faucet, the snap caps and the tube collars.")
            + '<h2 style="margin-top:30px">What it replaced</h2>'
            + p("Until August 2026 the box was printed in PETG and the faucet in carbon-filled PET, whose printed dowels had "
                "sheared off along their layers. The first enclosure piece in PET-GF went on the printer on 15 August, "
                "and the first faucet on 17 September.", style="margin:0"),
            ("0 0 600px",
             b.quote("very beautiful wall surface.", "DEREK · 15 AUGUST 2026 · SIX HOURS INTO THAT FIRST PIECE", size=52)
             + '<div style="margin-top:40px">'
             + b.record(b.link("The two fronts, and what each photograph holds", f"{PP}/cadlib/flute-evidence/README.md"),
                        b.link("The first piece", f"{ENC}/print-log.md"),
                        b.link("The maker&rsquo;s figures beside carbon-filled PET", f"{PP}/faucet/faucet-shell/print-log.md", anchor="material-and-nozzle-of-record-2026-08-24"),
                        b.link("Every printed piece and its plastic", f"{PP}/enclosure/trial-preparation/pieces.json"))
             + "</div>"),
            gap=56)
        + b.still_open("Nothing about the strength of our printed PET-GF has been measured. What this part says about it is "
                       "parts that held or broke in the hand, and the maker&rsquo;s own data sheet.")
    )
    return Page("petgf-the-plastic", "PET-GF: it hides its layers and breaks along them", "petgf", body, right="The plastic")


# ----------------------------------------------------------------------------- 2 the recipe
def _feed_drawing():
    _petgf()
    W, H, BED = 2170, 470, 420
    t_first = b.setting("petgf", "/nozzle_temperature_initial_layer/0")
    t_rest = b.setting("petgf", "/nozzle_temperature/0")
    bed_t = b.setting("petgf", "/textured_plate_temp/0")
    noz = b.setting("petgf", "/nozzle_diameter/0")
    fan = b.setting("petgf", "/fan_max_speed/0")
    tip = k.row_y(2, BED)
    s = []
    # the sealed box and its spool
    s.append(f'<rect x="40" y="96" width="380" height="356" rx="24" fill="white" stroke="{k.INK}" stroke-width="5"/>')
    s.append(f'<circle cx="230" cy="274" r="140" fill="{k.COLD}" stroke="{k.INK}" stroke-width="4"/>')
    s.append(f'<circle cx="230" cy="274" r="56" fill="white" stroke="{k.INK}" stroke-width="4"/><circle cx="230" cy="274" r="13" fill="{k.INK}"/>')
    s.append(k.label(470, 250, "A SEALED BOX", fill=k.INK, weight=600))
    s.append(k.label(470, 290, "THE SPOOL TURNS ON AN AXLE"))
    s.append(k.line(420, 242, 460, 242))
    # the tube from the box to the toolhead, with the filament inside it
    tube = "M312 160 C 330 84, 384 34, 560 28 S 1160 22, 1240 120"
    s.append(f'<path d="{tube}" stroke="{k.INK}" stroke-width="16" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="{tube}" stroke="white" stroke-width="9" fill="none" stroke-linecap="round"/>')
    s.append(f'<path d="{tube}" stroke="{k.COLD}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    s.append(k.label(640, 78, "THE FILAMENT, IN A TUBE"))
    # the toolhead with its two nozzles
    s.append(f'<rect x="1130" y="120" width="340" height="180" rx="12" fill="{k.WASH}" stroke="{k.INK}" stroke-width="4"/>')
    s.append(k.label(1154, 164, "TOOLHEAD", 25))
    s.append(fan_glyph(1404, 212, 44))
    s.append(ghost_nozzle(1390, 332))
    s.append(k.nozzle(1262, tip))
    # the part on the plate
    s.append(k.bed(1000, 2130, BED))
    s.append(k.block(1094, 1598, 0, 1, BED) + k.block(1094, 1262, 2, 2, BED, "hot"))
    # labels
    s.append(k.label(440, 352, f"LEFT HOTEND · HARDENED {noz} MM NOZZLE", fill=k.INK, weight=600))
    s.append(k.label(440, 392, f"{t_first} °C FIRST LAYER, {t_rest} °C AFTER"))
    s.append(k.line(1086, 344, 1222, 322))
    s.append(k.label(1530, 178, f"PART FAN · {fan} % ON A PLAIN WALL", fill=k.INK, weight=600))
    s.append(k.line(1522, 172, 1452, 198))
    s.append(k.label(1530, 290, "RIGHT HOTEND · WHITE AND COLOURS"))
    s.append(k.line(1522, 284, 1432, 300))
    s.append(k.label(1650, 392, f"TEXTURED PEI PLATE · {bed_t} °C", fill=k.INK, weight=600))
    return k.svg(W, H, "".join(s), "From the sealed box to the plate",
                 "A spool of PET-GF turns on an axle inside a sealed box. The filament runs through a tube to the printer's left "
                 "hotend, which carries a hardened nozzle and lays a course on a heated textured plate. The part fan is drawn at "
                 "rest. The right hotend, used for white and coloured PET-GF, is drawn pale.")


def recipe():
    _petgf()
    _pieces()
    S = lambda ptr: b.setting("petgf", ptr)
    left = [
        ("Nozzle", f'{S("/nozzle_diameter/0")} mm, HRC {S("/required_nozzle_HRC/0")} or harder'),
        ("First layer", f'{S("/initial_layer_print_height")} mm, laid at {S("/nozzle_temperature_initial_layer/0")} °C'),
        ("Every layer after", f'{S("/layer_height")} mm, laid at {S("/nozzle_temperature/0")} °C'),
        ("Plate", f'{S("/curr_bed_type")}, {S("/textured_plate_temp/0")} °C'),
        ("Chamber heater", f'{S("/chamber_temperatures/0")} °C, which is off'),
        ("Walls", f'{S("/wall_loops")} loops'),
    ]
    right = [
        ("Infill", f'{S("/sparse_infill_density")} {S("/sparse_infill_pattern")}'),
        ("Most plastic per second", f'{S("/filament_max_volumetric_speed/0")} mm³'),
        ("Flow ratio", S("/filament_flow_ratio/0")),
        ("Part fan, plain roads", f'{S("/fan_min_speed/0")} % to {S("/fan_max_speed/0")} %'),
        ("Part fan, over air", f'{S("/overhang_fan_speed/0")} % from {S("/overhang_fan_threshold/0")} unsupported'),
        ("Auxiliary fan", f'{S("/additional_cooling_fan_speed/0")} %'),
    ]
    dens_slot = S("/filament_density/0")
    dens_real = b.setting("petgf-setup-pieces", "/pieces/foam-shell/settings/filament_density/value/0")
    body = (
        b.head("The recipe", "One file holds the recipe.",
               "A printer does not know what plastic is in it. How hot, how thick, how fast and when to blow are all saved in "
               "one project file, petgf.3mf. Every PET-GF job starts from that file, and what a print teaches goes back into it.")
        + b.scope("Polymaker Fiberon PET-GF15 · Mark 1 and Mark2 · textured PEI · hardened 0.4 mm nozzles")
        + f'<div style="margin-top:30px">{_feed_drawing()}</div>'
        + b.rulebar(26, 34)
        + h3("What petgf.3mf holds today")
        + f'<div class="grid2" style="gap:70px">{b.table(left)}{b.table(right)}</div>'
        + '<div class="grid3" style="margin-top:44px; gap:56px">'
        + '<div><h2 style="font-size:44px">Where it started</h2>'
        + p("On 15 August 2026 the first enclosure piece ran on a 0.8 mm nozzle in 0.4 mm layers: 290 °C, a plate at 100 °C, "
            "the chamber held at 50 °C, no fan. Ten days later the maker&rsquo;s sheet was read beside it: nozzle 280 to 310, "
            "plate 70 to 80, room air, fan off. The nozzle had been in range. The plate and the chamber had not.",
            style="margin:0") + "</div>"
        + '<div><h2 style="font-size:44px">Fed and dried</h2>'
        + p("Black PET-GF, nearly all of it, feeds the left hotend, the only side that takes carbide and diamond. White and "
            "coloured PET-GF has fed the right, through hardened steel. Polymaker gives one drying cycle, for a spool that "
            "has taken on moisture. It is hotter than either AMS reaches, so it runs in a separate dryer. A 3 kg spool turns "
            "too stiffly in that dryer to print from, and feeds from the sealed box.", style="margin:0") + "</div>"
        + '<div><h2 style="font-size:44px">The printer calls it PET-CF</h2>'
        + p(f'The slot was copied from Bambu&rsquo;s carbon-fibre preset. Its type still reads {S("/filament_type/0")}, so the '
            f'screen and the send dialog say PET-CF. Its density still reads {dens_slot} where this plastic is {dens_real}, '
            'so the grams the slicer shows for a plate are not this spool&rsquo;s.', style="margin:0") + "</div>"
        + "</div>"
        + b.row(
            b.quote("I don&rsquo;t know why bambu defaults 0.24 layer height to a 0.20 first layer, but if I don&rsquo;t have a reason "
                    "to muck with a bambu default choice, I don&rsquo;t muck with it.", "DEREK · 25 OCTOBER 2026", size=41),
            ("0 0 940px",
             p("<b>Why these numbers are read from the file.</b> On 29 August 2026 an ordinary re-save in the slicer moved this "
               "file&rsquo;s nozzle from 290 to 265 and changed its first-layer preset. Nobody had asked for it and nothing showed "
               "it. So this page reads the file each time the book is bound, and a sliced job is read back before it is sent.",
               "tiny", "margin:0; font-size:32px; color:var(--text)")),
            gap=70, style="margin-top:40px")
        + '<div style="margin-top:30px">'
        + b.record(b.link("petgf.3mf", f"{PP}/petgf.3mf"),
                   b.link("The first piece&rsquo;s settings", f"{ENC}/enclosure-front-top-petgf.3mf", "cfcaf5dfc"),
                   commit("The maker&rsquo;s sheet read against them", "47fe7dce8"),
                   b.link("What dries where", "hardware/ledger/tools.md", anchor="what-dries-where"),
                   commit("The re-save", "72c9b062f"))
        + "</div>"
        + b.still_open(f'The file sets no pressure advance of its own (its switch reads {S("/enable_pressure_advance/0")}). Each '
                       "job leaves that to the printer&rsquo;s automatic flow calibration, and nobody has compared the result with "
                       "a value measured for this plastic.")
    )
    return Page("petgf-one-file-holds-the-recipe", "PET-GF: one file holds the recipe", "petgf", body, right="The recipe")


# ----------------------------------------------------------------------------- 3 first-layer trim
def _first_layer_panels():
    W, H, P = 2170, 330, 250
    pitch = (W - 480) / 3

    def panel(i, kind, title):
        g = [f'<g transform="translate({k.n(i * pitch)} 0)">']
        if kind == "home":
            g.append(texture(0, 480, P))
            g.append(k.line(0, P, 480, P, k.MUTED, 3, "10 9"))
            g.append(k.nozzle(260, P))
            g.append(k.label(480, P - 16, "THE PEAKS", 25, anchor="end"))
        elif kind == "close":
            g.append(f'<rect x="40" y="{P - 9}" width="352" height="34" fill="{k.HOT}"/>')
            g.append(f'<path d="M286 {P - 8} Q312 {P - 40} 350 {P - 8} Z" fill="{k.HOT}"/>')
            g.append(k.road(f"M392 {P - 6} Q424 {P - 44} 458 {P - 30}", k.HOT, 10))
            g.append(texture(0, 480, P))
            g.append(k.nozzle(372, P - 9))
        elif kind == "right":
            for j in range(6):
                g.append(f'<rect x="{40 + j * 60}" y="{P - 18}" width="62" height="22" rx="10" fill="{k.HOT if j == 5 else k.COLD}"/>')
            g.append(texture(0, 480, P))
            g.append(k.nozzle(371, P - 18))
        else:
            for j in range(5):
                g.append(f'<circle cx="{66 + j * 60}" cy="{P - 14}" r="14" fill="{k.COLD}"/>')
            g.append(texture(0, 480, P))
            g.append(k.missing(338, P - 30, 398, P - 2))
            g.append(k.nozzle(368, P - 46))
            g.append(f'<circle cx="372" cy="{P - 30}" r="17" fill="{k.HOT}"/>')
        g.append(k.label(0, 44, title, fill=k.INK, weight=600))
        g.append("</g>")
        return "".join(g)

    body = (panel(0, "home", "HOW IT FINDS THE PLATE") + panel(1, "close", "TOO CLOSE")
            + panel(2, "right", "RIGHT") + panel(3, "far", "TOO FAR"))
    return k.svg(W, H, body, "The first layer on a textured plate: how the printer finds it, then too close, right and too far",
                 "Four sections through a textured plate. First the nozzle touches the tops of the texture. Then three first "
                 "layers seen across their roads: pressed down into the texture and smeared, pressed flat and joined, and round "
                 "roads sitting on the peaks with the last one gone and a ball of plastic on the nozzle.")


def _ladder():
    _pieces()
    W, H = 1290, 306
    m2 = float(b.value("petgf-setup-pieces", "/printers/Mark2/z_trim_mm"))
    m1 = float(b.value("petgf-setup-pieces", "/printers/Mark1/z_trim_mm"))
    s2 = b.setting("petgf-setup-pieces", "/printers/Mark2/z_trim_mm")
    s1 = b.setting("petgf-setup-pieces", "/printers/Mark1/z_trim_mm")
    x = lambda v: 70 + v * 5300
    y0 = 168
    s = [k.line(x(0), y0, x(0.20) + 26, y0, k.INK, 4)]
    s.append(k.line(x(0), y0 - 44, x(0), y0 + 44, k.INK, 5))
    for i in range(1, 21):
        big = i % 5 == 0
        s.append(f'<path d="M{k.n(x(i / 100))} {y0 - (38 if big else 26)}V{y0 + (38 if big else 26)}" stroke="{k.COLD}" stroke-width="12" stroke-linecap="round"/>')
        if big or i == 1:
            s.append(k.label(x(i / 100), y0 + 80, f".{i:02d}", 26, anchor="middle"))
    s.append(k.label(x(0), y0 + 80, "0", 26, anchor="middle", fill=k.INK, weight=600))
    # the probe, off the end of the scale
    s.append(f'<path d="M{k.n(x(0.20) + 34)} {y0 + 16}l14 -32M{k.n(x(0.20) + 50)} {y0 + 16}l14 -32" stroke="{k.INK}" stroke-width="4" fill="none"/>')
    s.append(f'<path d="M{k.n(x(0.20) + 96)} {y0 - 26}V{y0 + 26}" stroke="{k.COLD}" stroke-width="12" stroke-linecap="round"/>')
    s.append(k.label(x(0.20) + 96, y0 + 80, ".30", 26, anchor="middle"))
    # where each printer settled
    for v, name, val in ((m2, "MARK2", s2), (m1, "MARK 1", s1)):
        s.append(f'<circle cx="{k.n(x(v))}" cy="{y0}" r="20" fill="{k.INK}"/>')
        s.append(k.line(x(v), y0 - 20, x(v), y0 - 78, k.INK, 4))
        s.append(k.label(x(v), y0 - 128, name, 30, anchor="middle", fill=k.INK, weight=600))
        s.append(k.label(x(v), y0 - 92, f"+{val} MM", 30, anchor="middle", fill=k.INK, weight=600))
    s.append(k.label(x(0) - 12, y0 + 124, "THE PRINTER&apos;S OWN SETTING", 24, fill=k.INK))
    s.append(k.label(x(0.20), y0 + 124, "HUNDREDTHS OF A MILLIMETRE OF EXTRA LIFT", 24, anchor="end"))
    s.append(k.label(x(0.20) + 96, y0 + 124, "PROBE", 24, anchor="middle"))
    return k.svg(W, H, "".join(s), "The ladder of trim files, and where each printer settled",
                 "A scale of twenty rungs, one hundredth of a millimetre of extra nozzle lift each, with a further probe at "
                 "thirty hundredths. Mark2 is marked low on the ladder and Mark 1 near its top.")


def trim():
    _pieces()
    plate = b.asset("petgf-setup-nameplate-first-layer.jpg", f"{PP}/enclosure/nameplate/physical-fit/front.jpg", max_px=2000)
    s2 = b.setting("petgf-setup-pieces", "/printers/Mark2/z_trim_mm")
    s1 = b.setting("petgf-setup-pieces", "/printers/Mark1/z_trim_mm")
    notes = [
        "Before each print the nozzle touches the plate. On texture it finds the peaks, so the printer then lowers it a "
        "hair. Our trim lifts it again.",
        "Forced down into the texture. One plate, 30 August 2026: &ldquo;more melty pressed in material from first layer "
        "into plate&rdquo;.",
        "Flat roads, joined to each other and keyed to the texture, which stays printed in the face of the part.",
        "Round roads resting on the peaks. They lift, and loose plastic balls up on the nozzle (20 September 2026, next "
        "page).",
    ]
    caps = '<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:83px; margin-top:12px">' + "".join(
        f'<p class="tiny" style="margin:0; font-size:32px; color:var(--text)">{t}</p>' for t in notes) + "</div>"
    body = (
        b.head("First layer · textured PEI", "A first-layer trim does not travel.",
               "The printer finds the plate by touching it with its nozzle. On a textured plate it touches the tops of the "
               "bumps, so how hard a first layer is pressed in depends on that one plate. The trim is the small correction, "
               "found by printing.", lede_size=54)
        + b.scope("PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm nozzle",
                  not_tried="smooth plates. Carried to PETG on one, this trim failed")
        + f'<div style="margin-top:32px">{_first_layer_panels()}</div>' + caps
        + b.rulebar(36, 34)
        + b.row(
            ("0 0 1250px",
             '<h2>Three days, twenty rungs, two answers</h2>'
             + p("Bambu&rsquo;s start code says why a textured plate gets a correction: &ldquo;the nozzle was touching topmost of "
                 "the texture when homing&rdquo;. Ours is found by printing. Between 28 and 30 August 2026 a ladder of empty "
                 "project files was built, z-trim-0.01.3mf to z-trim-0.20.3mf, a hundredth of a millimetre of lift apart, "
                 "and one at 0.30 to prove the setting did anything. On the first night Derek thought the answer was 0.02, "
                 "then 0.01. Two days later the ladder had been climbed to its top.", style="margin-bottom:12px")
             + _ladder()
             + p(f"Mark2 prints PET-GF at +{s2} mm and Mark 1 at +{s1} mm: the same model of printer, the same plastic, the "
                 "same size of nozzle and the same kind of plate.", style="margin:8px 0 0")),
            b.fig(plate, "A black nameplate with white lettering and a QR code, its face carrying the plate's texture",
                  "20 September 2026 · Mark2 · black and white PET-GF",
                  "A first layer that went down right. This plate was printed face down, so the letters and the code are its "
                  "first layer. &ldquo;The QR code scans clean from 2 feet away&rdquo;. (The nameplate has since moved to PETG.)",
                  h=500, pos="38% 46%", zoom=143),
            gap=70)
        + '<div class="grid3" style="margin-top:34px; gap:56px">'
        + b.quote("it seems one of the confounding variables is which textured PEI plate is used.", "DEREK · 30 AUGUST 2026", size=44)
        + p("<b>Not to another printer.</b> On 8 October 2026 a lower trim, tried once on Mark 1, had been written down as "
            "Mark 1&rsquo;s new rule. &ldquo;The +0.04 trim was a *special* case for a problem with a *specific* print - not a "
            "change to the rule for Mark1.&rdquo;", style="margin:0")
        + p("<b>Not to another plastic or plate.</b> On 6 November 2026 Mark 1&rsquo;s PET-GF trim rode along onto a PETG job "
            "on a glued smooth plate. &ldquo;lol, okay, print stopped, it lifted right off.&rdquo; Then: &ldquo;No. That should "
            "be documented as for pet-gf on textured plate.&rdquo;", style="margin:0")
        + "</div>"
        + b.row(
            ("0 0 1250px",
             b.record(b.link("How the trim works, and the ladder", f"{PP}/z-trim.md"),
                      b.link("Each printer&rsquo;s trim", PRINTERS, anchor="z-trim"),
                      b.link("The nameplate", f"{PP}/enclosure/nameplate/physical-acceptance.json"),
                      b.link("The PETG job that lifted", f"{PP}/enclosure/display-cover/prints/2026-11-06-identification-set-mark1/physical-result.json"))),
            p("<b>What we do now.</b> Each printer&rsquo;s trim is written in one place. A job&rsquo;s file name carries it, and "
              "the trim line in the sliced file is read back before the job is sent.", "tiny", "margin:0; font-size:32px; color:var(--text)"),
            gap=70, style="margin-top:30px")
        + b.still_open("Nobody wrote down what each rung looked like: the record holds the two answers and not the prints that "
                       "chose them. Mark2 also printed two whole faucets at the higher trim on 18 and 19 September 2026, and "
                       "the first &ldquo;Came out great&rdquo;, so how wide the good band is on either printer is not known. The "
                       "plates are not marked, so no trim can be tied to the plate it was found on.")
    )
    return Page("petgf-a-trim-does-not-travel", "PET-GF: a first-layer trim does not travel", "petgf", body, right="First layer")


# ----------------------------------------------------------------------------- 4 the plate's edge
def _beds():
    _petgf()
    _pieces()
    area = str(b.value("petgf", "/extruder_printable_area/0"))          # the left nozzle's reach, as corner points
    bw = max(float(c.split("x")[0]) for c in area.split(","))
    bh = max(float(c.split("x")[1]) for c in area.split(","))
    near = float(b.value("petgf-setup-pieces", "/pieces/foam-shell/plate_border_mm"))
    far = float(b.value("petgf-setup-pieces", "/pieces/pump-snap-cap/plate_border_mm"))
    near_s = b.setting("petgf-setup-pieces", "/pieces/foam-shell/plate_border_mm")
    far_s = b.setting("petgf-setup-pieces", "/pieces/pump-snap-cap/plate_border_mm")
    W, H, S, TOP = 2170, 610, 1.42, 106
    BW, BH = bw * S, bh * S
    pitch = W / 4

    def bed(i, title, sub):
        ox = i * pitch + (pitch - BW) / 2
        band = 20 * S
        return ox, (k.label(ox, 40, title, fill=k.INK, weight=600) + k.label(ox, 78, sub)
                    + f'<rect x="{k.n(ox)}" y="{TOP}" width="{k.n(BW)}" height="{k.n(BH)}" rx="14" fill="white" stroke="{k.INK}" stroke-width="5"/>'
                    + f'<rect x="{k.n(ox + band)}" y="{k.n(TOP + band)}" width="{k.n(BW - 2 * band)}" height="{k.n(BH - 2 * band)}" rx="8" '
                      f'fill="{k.WASH}" stroke="{k.FAINT}" stroke-width="3" stroke-dasharray="7 9"/>'
                    + k.label(ox + BW / 2, TOP + BH + 40, "FRONT OF THE PRINTER", 22, anchor="middle", fill=k.FAINT))

    def stand(ox):
        m = 5 * S                                                        # the stand's outline, 5 mm inside the reach
        return ox + m, TOP + m, ox + BW - m, TOP + BH - m

    def patch(x0, y0, x1, y1):
        return (f'<rect x="{k.n(x0)}" y="{k.n(y0)}" width="{k.n(x1 - x0)}" height="{k.n(y1 - y0)}" fill="white" stroke="{k.BAD}" '
                f'stroke-width="4" stroke-dasharray="10 8"/>')

    s = []
    # sends 1 to 4
    ox, plate = bed(0, "SENDS 1 TO 4", "OUR TRIM")
    x0, y0, x1, y1 = stand(ox)
    s.append(plate)
    s.append(f'<rect x="{k.n(x0)}" y="{k.n(y0)}" width="{k.n(x1 - x0)}" height="{k.n(y1 - y0)}" rx="10" fill="none" stroke="{k.BAD}" stroke-width="6" stroke-dasharray="16 12"/>')
    s.append(k.label(ox + BW / 2, TOP + 66, "THE OUTLINE DID NOT HOLD", 24, anchor="middle", fill=k.BAD, weight=600))
    s.append(k.label(ox + BW / 2, TOP + BH / 2 + 2, "PRINTED ON BEFORE", 24, anchor="middle"))
    s.append(k.label(ox + BW / 2, TOP + BH / 2 + 38, "NOBODY MAPPED WHERE", 24, anchor="middle"))
    s.append(k.label(ox + BW / 2, TOP + BH - 44, "NEVER PRINTED ON, OUT HERE", 24, anchor="middle"))
    s.append(k.line(ox + BW / 2, TOP + BH - 36, ox + BW / 2, TOP + BH - 16, k.MUTED))
    # send 5
    ox, plate = bed(1, "SEND 5", "THE PRINTER&apos;S OWN OFFSET")
    x0, y0, x1, y1 = stand(ox)
    s.append(plate + k.scaffold(x0, x1, y0, y1))
    s.append(patch(x1 - 44, y0 + 70, x1 - 6, y1 - 70))
    s.append(patch(x0 + 6, y1 - 44, x0 + 210, y1 - 6))
    s.append(f'<rect x="{k.n(ox + BW / 2 - 150)}" y="{k.n(TOP + BH / 2 - 54)}" width="300" height="100" fill="white"/>')
    s.append(k.label(ox + BW / 2, TOP + BH / 2 - 12, "TWO LAYERS,", 24, anchor="middle", fill=k.INK, weight=600))
    s.append(k.label(ox + BW / 2, TOP + BH / 2 + 24, "THEN PEELED OFF", 24, anchor="middle", fill=k.INK, weight=600))
    # send 6
    ox, plate = bed(2, "SEND 6", "OUR TRIM AGAIN")
    x0, y0, x1, y1 = stand(ox)
    s.append(plate + f'<rect x="{k.n(x0)}" y="{k.n(y0)}" width="{k.n(x1 - x0)}" height="{k.n(y1 - y0)}" rx="10" fill="{k.COLD}"/>')
    s.append(k.label(ox + BW / 2, TOP + BH / 2 + 8, "CLEAN TO THE EDGE", 24, anchor="middle", fill="white", weight=600))
    # now
    ox, plate = bed(3, "NOW", "THE MARGINS WE KEEP")
    s.append(plate)
    a, c = near * S, far * S
    s.append(f'<rect x="{k.n(ox + a)}" y="{k.n(TOP + a)}" width="{k.n(BW - 2 * a)}" height="{k.n(BH - 2 * a)}" rx="8" fill="none" stroke="{k.INK}" stroke-width="4" stroke-dasharray="14 10"/>')
    s.append(f'<rect x="{k.n(ox + c)}" y="{k.n(TOP + c)}" width="{k.n(BW - 2 * c)}" height="{k.n(BH - 2 * c)}" fill="white" stroke="{k.INK}" stroke-width="4"/>')
    for j in range(3):
        for r in range(2):
            s.append(f'<rect x="{k.n(ox + c + 30 + j * 62)}" y="{k.n(TOP + c + 46 + r * 70)}" width="44" height="40" rx="6" fill="{k.COLD}"/>')
    s.append(k.label(ox + BW / 2, TOP + a + 46, f"BIG PARTS · {near_s} MM IN", 23, anchor="middle", fill=k.INK, weight=600))
    s.append(k.label(ox + BW / 2, TOP + BH - c + 42, f"SMALL PLATES · {far_s} MM IN", 23, anchor="middle", fill=k.INK, weight=600))
    return k.svg(W, H, "".join(s), "The print bed from above, over six sends of one bed-filling part",
                 "Four views of the bed from above. The middle of the plate has been printed on before and a band at its edge "
                 "has not. First the part's outline, five millimetres from the edge, fails to hold. Then one whole first layer "
                 "is printed at the printer's own offset and peeled off, rough along the right edge and the front left. Then "
                 "the same part prints clean to the edge. Last, the margins kept now for big parts and for small plates.")


def edge():
    _pieces()
    centred = b.asset("petgf-setup-centred-plate.jpg", "hardware/print-tests/petgf-fins/photos/01-plate.jpg", max_px=2000)
    near_s = b.setting("petgf-setup-pieces", "/pieces/foam-shell/plate_border_mm")
    far_s = b.setting("petgf-setup-pieces", "/pieces/pump-snap-cap/plate_border_mm")
    notes = [
        "20 September 2026: a bench stand as big as the nozzle can reach, 5 mm from the edge. Two clumps on the nozzle, "
        "then a peel on a fresh hotend. Pulled in to 15 mm: &ldquo;It was lifting already.&rdquo;",
        "Back at the edge without our trim, so the nozzle ran lower. It pressed flat and held, rough at the right edge "
        "and the front left. Derek stopped it and peeled it off.",
        "The file of the third send, on the same hotend. The first layer went down &ldquo;clean and uniform out to the "
        "plate&rsquo;s edge&rdquo;, and the print ran all 917 layers.",
        f"The cold-core shell keeps every road {near_s} mm in from the edge. Small test plates are centred {far_s} mm in. "
        "Both are measured on the sliced paths, brim and supports included.",
    ]
    caps = '<div class="grid4" style="gap:81px; padding:0 40px; margin-top:14px">' + "".join(
        f'<p class="tiny" style="margin:0; font-size:32px; color:var(--text)">{t}</p>' for t in notes) + "</div>"
    body = (
        b.head("First layer · the plate&rsquo;s edge", "Season the edge, or stay off it.",
               "Small parts are printed in the middle of the plate, so the middle gets used and the last few centimetres at "
               "the edge do not. PET-GF held on the used part of a textured plate and let go where nothing had been printed. "
               "A part that fills the bed finds that out in its first layer.", size=150, lede_size=54)
        + b.scope("black PET-GF · Mark2&rsquo;s textured PEI · left 0.4 mm nozzle · 20 September, 4 October and 10 October 2026",
                  not_tried="Mark 1. On 6 October 2026 the rule also stopped clear PETG on Mark2&rsquo;s textured PEI "
                            "(left 0.8 mm), and no failure was named")
        + f'<div style="margin-top:30px">{_beds()}</div>' + caps
        + b.rulebar(36, 34)
        + b.row(
            ("0 0 900px",
             b.fig(centred, "A textured plate with about twenty-five small black test pieces grouped in its middle",
                   "14 October 2026 · Mark2 · black PET-GF",
                   "What staying off it looks like: twenty-five test pieces grouped in the middle, the nearest road 82 mm "
                   "from an edge.", h=440, pos="50% 46%")),
            b.quote("The seasoning worked. I mean even if it fails after this there is still a very obvious effect so far!",
                    "DEREK · 21 SEPTEMBER 2026 · THE SIXTH SEND", size=47)
            + '<div style="margin-top:34px">'
            + p("<b>What seasoned means.</b> A place on the plate where PET-GF has been printed before. The record says "
                "nothing more exact.", style="margin-bottom:20px")
            + p("<b>Two weeks later.</b> &ldquo;On mark2 you had pieces close to the edge that did not get a good first "
                "layer, so that plate is not well seasoned there yet. We could keep printing until it works, or you could "
                "avoid going that far to the edge here.&rdquo; (4 October 2026, black PET-GF, nearest road 15.5 mm in.)",
                style="margin:0")
            + "</div>",
            gap=70)
        + '<div style="margin-top:30px">'
        + p("<b>The one time it was not PET-GF.</b> On 6 October 2026 the rule stopped a plate of clear PETG on Mark2&rsquo;s "
            "textured plate, its nearest piece 17.5 mm in: &ldquo;You can&rsquo;t print that close to the edge of the bed on a "
            "plate that hasn&rsquo;t been seasoned properly first.&rdquo; The margins we keep come from that message. The record "
            "names no piece that failed that day, and PETG has since moved to a glued smooth plate.", style="margin:0")
        + "</div>"
        + '<div style="margin-top:28px">'
        + b.record(b.link("The six sends", f"{STAND}/print-jobs.json"),
                   b.link("The stand, and its seasoning layer", f"{STAND}/README.md", anchor="print"),
                   b.link("4 October", f"{ENC}/support-bottom-gap/mark2-v2/physical-result.json"),
                   b.link("6 October", f"{PP}/cold-core/reservoir/ironing-study/prints/2026-10-06-mark2/physical-result.json"),
                   b.link("The margins", PRINTERS, anchor="placement-on-unseasoned-plates"))
        + "</div>"
        + b.still_open("Nobody has looked at what a first layer leaves on the plate, so why this works is not known. The "
                       "plates are not marked and there is no map of where each has been printed on. The stand reached to "
                       "5 mm from Mark2&rsquo;s edge on 21 September, and on 4 October an edge on Mark2 would not hold: the "
                       "record cannot say whether that was another plate or whether seasoning wears off.")
    )
    return Page("petgf-season-the-edge", "PET-GF: season the edge of the plate, or stay off it", "petgf", body, right="The plate&rsquo;s edge")


# ----------------------------------------------------------------------------- 5 cooling
def _fan_drawing():
    _petgf()
    _scalars()
    W, H, BED = 2170, 430, 384
    off = b.setting("petgf", "/fan_max_speed/0")
    on = b.setting("petgf", "/overhang_fan_speed/0")
    thr = b.setting("petgf", "/overhang_fan_threshold/0")
    depth = b.setting("scalars", "/petgf_cooling/FOUNDATION/height_mm")
    y = lambda r: k.row_y(r, BED)
    G = [40, 582.5, 1125, 1667.5]                                        # the left edge of each of the four cases
    s = [k.bed(20, W - 20, BED)]
    # a plain wall
    g = G[0]
    s.append(k.block(g, g + 126, 0, 4, BED) + k.block(g, g + 126, 5, 5, BED, "hot") + k.nozzle(g + 105, y(5)))
    s.append(k.label(g, 40, "A PLAIN WALL", fill=k.INK, weight=600) + k.label(g, 80, f"FAN {off} %"))
    # a road hanging out
    g = G[1]
    s.append(k.block(g, g + 126, 0, 1, BED))
    for r in range(2, 6):
        s.append(k.course(g + (r - 1) * 21, g + 126 + (r - 1) * 21, y(r), k.HOT if r == 5 else k.COLD))
    edge_x = g + 126 + 4 * 21
    s.append(k.nozzle(edge_x - 21, y(5)) + air(edge_x + 26, y(5) + 6))
    s.append(k.line(edge_x, y(5) + 30, edge_x, y(5) + 64) + k.line(edge_x - 21, y(5) + 30, edge_x - 21, y(5) + 64))
    s.append(k.label(edge_x + 14, y(5) + 62, f"{thr} OF THE ROAD", 23) + k.label(edge_x + 14, y(5) + 92, "OVER AIR", 23))
    s.append(k.label(g, 40, "A ROAD HANGING OUT", fill=k.INK, weight=600) + k.label(g, 80, f"FAN {on} %", fill=k.HOT, weight=600))
    # a bridge
    g = G[2]
    s.append(k.block(g, g + 84, 0, 4, BED) + k.block(g + 252, g + 336, 0, 4, BED))
    s.append(k.block(g, g + 84, 5, 5, BED, "hot") + k.strand(g + 84, g + 252, y(5)) + k.block(g + 252, g + 336, 5, 5, BED, "hot"))
    s.append(k.nozzle(g + 240, y(5)))
    s.append("".join(k.line(g + 126 + i * 28, y(5) + 78, g + 138 + i * 28, y(5) + 40) for i in range(3)))
    s.append(k.label(g + 168, y(0) + 4, "AIR", 25, anchor="middle", fill=k.FAINT))
    s.append(k.label(g, 40, "A BRIDGE", fill=k.INK, weight=600) + k.label(g, 80, f"FAN {on} %", fill=k.HOT, weight=600))
    # the courses just after a bridge
    g = G[3]
    s.append(k.block(g, g + 84, 0, 4, BED) + k.block(g + 252, g + 336, 0, 4, BED))
    s.append(k.block(g, g + 84, 5, 5, BED) + k.strand(g + 84, g + 252, y(5), k.COLD) + k.block(g + 252, g + 336, 5, 5, BED))
    s.append(k.block(g, g + 336, 6, 6, BED) + k.block(g, g + 210, 7, 7, BED, "hot") + k.nozzle(g + 200, y(7)))
    s.append(k.line(g + 366, y(8), g + 366, y(5)) + k.line(g + 354, y(8), g + 378, y(8)) + k.line(g + 354, y(5), g + 378, y(5)))
    s.append(k.label(g + 388, y(6) - 2, f"{depth} MM", 25, fill=k.INK, weight=600))
    s.append(k.label(g, 40, "JUST AFTER A BRIDGE", fill=k.INK, weight=600) + k.label(g, 80, f"FAN STAYS AT {on} %", fill=k.HOT, weight=600))
    return k.svg(W, H, "".join(s), "Where the part fan comes on in PET-GF",
                 "Four sections on the bed. A plain wall is laid with the fan off. A road that hangs half its width over air is "
                 "laid with the fan on. A bridge is laid with the fan on. The courses laid just on top of a fresh bridge keep "
                 "the fan, through a band of height above it.")


def cooling():
    _petgf()
    _scalars()
    _tpu()
    cracked = b.asset("petgf-setup-cover-cracked.jpg", f"{COVER}/prints/2026-10-17-cooling-off-prepared-mark2/fracture-photo.jpg", max_px=2000)
    fitted = b.asset("petgf-setup-cover-fitted.jpg", f"{COVER}/prints/2026-10-25-front-overlap-black-mark2/physical-result/photo-4.jpg", max_px=2000)
    S = lambda ptr: b.setting("petgf", ptr)
    thr = S("/overhang_fan_threshold/0")
    depth = b.setting("scalars", "/petgf_cooling/FOUNDATION/height_mm")
    tpu = b.setting("petgf-setup-tpu-sleeve", "/fan_min_speed/0")
    notes = [
        "Walls, infill and top faces are laid with the fan at rest. On the first faucet printed this way, 17 October 2026, "
        "over 99 percent of the cover&rsquo;s outer wall was laid with it off.",
        f"The slicer asks how much of a road must hang over air before the fan comes on. Ours is {thr}. At zero, Bambu "
        "Studio cools every outer wall, overhang or not. The cracked covers&rsquo; file carried a zero.",
        "A road pulled across a gap is laid slowly, with the fan on. With no fan at all, on 24 September 2026, a rounded "
        "underside in fine layers &ldquo;turned out worse. Exploded basically.&rdquo;",
        "The slicer cools a bridge and then stops. On 5 November 2026 the course laid on a fresh bridge came off "
        f"&ldquo;stringy and loose&rdquo;: fan off, at up to 200 mm/s. Now fan and bridge speed are kept for {depth} mm above.",
    ]
    caps = '<div class="grid4" style="gap:81px; padding:0 40px; margin-top:12px">' + "".join(
        f'<p class="tiny" style="margin:0; font-size:32px; color:var(--text)">{t}</p>' for t in notes) + "</div>"
    body = (
        b.head("Cooling", "Fan only where the plastic is over air.",
               "The part fan blows room air at the plastic as it leaves the nozzle. A road laid over air needs that, to set "
               "before it sags. A plain wall of PET-GF does not. Printed with the fan on everywhere, thin covers cracked along "
               "their layers in the hand.", lede_size=54)
        + b.scope("white and black PET-GF · Mark2 · textured PEI · right and left 0.4 mm nozzles",
                  not_tried=f"PETG. Soft TPU wants the opposite: its sleeve prints with this fan at {tpu} % (the TPU part)")
        + '<div class="grid2" style="margin-top:28px">'
        + b.fig(cracked, "A white printed cover with a long strip torn away along its layers",
                "17 October 2026 · Mark2 · white PET-GF · right nozzle",
                "Printed with the fan at 70 percent on every road above the third layer. It split along its layers as the "
                "display was pressed in. The cover before it had done the same.", h=420, pos="50% 62%")
        + b.fig(fitted, "A black cover holding a display, fitted on the end of a black faucet",
                "25 October 2026 · Mark2 · black PET-GF · left nozzle",
                "A later cover, reshaped at its front corners, printed with the fan on its overhangs only. It took its display "
                "and went on. &ldquo;That worked.&rdquo;", h=420, pos="50% 64%")
        + "</div>"
        + b.row(
            ("0 0 1150px",
             b.quote("That new printed cover works great. In fact, it worked so well that the other parts of the faucet broke "
                     "while I was trying to put that cover on, which I think really indicates that we have a brittleness issue "
                     "with those cooling settings that we need to be aware of.", "DEREK · 17 OCTOBER 2026 · THE SAME COVER, FAN OFF", size=38)),
            p("<b>One change.</b> That afternoon the cracked cover&rsquo;s file was printed again with every fan setting at "
              "zero. Shape, temperatures, speeds and supports stayed as they were. It took the display and went on. By "
              "evening the fan was back, on bridges and overhangs only.", style="margin:0"),
            gap=64, style="margin-top:30px")
        + f'<div style="margin-top:36px">{_fan_drawing()}</div>' + caps
        + b.row(
            b.quote("the cooling, high cooling, is totally fine. We can use 100% cooling if we want, but only on the places "
                    "that actually need it, and everywhere else we shouldn&rsquo;t be using that cooling.", "DEREK · 17 OCTOBER 2026", size=40),
            ("0 0 800px",
             b.record(b.link("The cracked covers", f"{COVER}/prints/2026-10-17-cooling-off-prepared-mark2/reported-failure.json"),
                      b.link("The fan-off cover", f"{COVER}/prints/2026-10-17-cooling-off-prepared-mark2/physical-result.json"),
                      b.link("The cooling we keep", f"{PP}/cooling/README.md"),
                      b.link("The rail, read course by course", f"{ENC}/prints/2026-11-05-back-top-smooth-corners-mark2/rail-cooling.json"),
                      b.link("The round with no fan", f"{ENC}/print-log.md"))),
            gap=64, style="margin-top:34px")
        + b.still_open("Why the covers cracked is not established: the fan was the one thing changed between the cover that "
                       "broke and the one that held, and no strength was measured. The cooling kept above a bridge has been "
                       "read in each file&rsquo;s commands since 6 November 2026. No print has yet been judged for it.")
    )
    return Page("petgf-fan-only-over-air", "PET-GF: fan only where the plastic is over air", "petgf", body, right="Cooling")


# ----------------------------------------------------------------------------- 6 time between layers
def _timeline():
    W, H, PX, X0 = 1210, 400, 22.0, 10
    s = []
    # 26 October: one layer after another with nothing between
    s.append(k.label(X0, 40, "26 OCTOBER · ONE CLIP, ALONE", fill=k.INK, weight=600))
    seg = 2.3 * PX
    for i in range(22):
        s.append(f'<rect x="{k.n(X0 + i * (seg + 3))}" y="62" width="{k.n(seg)}" height="62" fill="{k.HOT}"/>')
    # 7 November: three seconds on the cap, then the tower
    s.append(k.label(X0, 204, "7 NOVEMBER · ONE CAP, WITH A TOWER", fill=k.INK, weight=600))
    on, away = 3.0 * PX, 23.8 * PX
    for i in range(2):
        x = X0 + i * (on + away)
        s.append(f'<rect x="{k.n(x)}" y="226" width="{k.n(on - 3)}" height="62" fill="{k.HOT}"/>')
        s.append(k.scaffold(x + on, x + on + away - 3, 226, 288))
    # seconds
    s.append(k.line(X0, 330, X0 + 54 * PX, 330, k.INK, 3))
    for t in range(0, 51, 10):
        s.append(k.line(X0 + t * PX, 322, X0 + t * PX, 340, k.INK, 3))
        s.append(k.label(X0 + t * PX, 376, f"{t} S" if t else "0", 24, anchor="middle" if t else "start"))
    return k.svg(W, H, "".join(s), "Time on the part and time away, for a small part printed alone",
                 "Two bars on one scale of seconds. On 26 October each layer of a lone clip took a second to three and a half, "
                 "with nothing between layers. On 7 November a lone cap took as little as three seconds a layer, and the nozzle "
                 "then spent at least twenty-four seconds printing a tower before it came back.")


def small_parts():
    _petgf()
    _pieces()
    clip = b.asset("petgf-setup-melted-clip.jpg", f"{CLIP}/physical-photo-2.jpg", CLIP_REV, max_px=2000)
    slow = b.setting("petgf", "/slow_down_layer_time/0")
    tower_w = b.setting("petgf-setup-pieces", "/pieces/single-regulator-cap/settings/prime_tower_width/value")
    tower_v = b.setting("petgf-setup-pieces", "/pieces/single-regulator-cap/settings/prime_tower_max_speed/value")
    ways = [
        ("A batch", "Other parts on the plate keep the nozzle busy somewhere else. On 7 November two regulator caps shared a "
                    "plate with their test receivers, and the file gave each cap 19 seconds or more between layers with no "
                    "tower. &ldquo;Like that gives us the layer time already.&rdquo;"),
        ("A tower", f"Alone on the plate, the nozzle is sent away after every layer to print a tower, {tower_w} mm wide at "
                    f"{tower_v} mm/s. The printer&rsquo;s smooth timelapse move does the sending. 7 November 2026, one cap, "
                    "Mark2: &ldquo;The print turned out fine&rdquo;."),
        ("A wait", "11 November 2026, one white display cover, Mark 1: a tower on all 86 layers, and the nozzle parked above "
                   "it for ten seconds before each. &ldquo;Just the cover. With a prime tower and wait between layers so its "
                   "not a melty blob.&rdquo;"),
    ]
    ways_html = '<div class="grid3" style="gap:56px">' + "".join(
        f'<div><div style="display:flex; align-items:center; gap:20px; margin-bottom:14px"><span class="num">{i + 1}</span>'
        f'<h2 style="margin:0">{t}</h2></div><p class="small" style="margin:0">{d}</p></div>' for i, (t, d) in enumerate(ways)) + "</div>"
    body = (
        b.head("Cooling · small parts", "A small part needs time between layers.",
               "Each layer is laid on the one before while that one is still giving up its heat. On a big part the nozzle is "
               "away for a minute or more. On a part the size of a thumb it is back in a second or two, laying hot plastic on "
               "plastic that has not set.", lede_size=54)
        + b.scope("black and white PET-GF · Mark2 and Mark 1 · textured PEI · left 0.4 mm nozzle",
                  not_tried="any other plastic. PET-GF has no fan to fall back on, so time is all it has")
        + b.row(
            ("0 0 900px",
             b.fig(clip, "A small black printed part on a textured plate, its walls slumped, wavy and glossy",
                   "26 October 2026 · Mark2 · black PET-GF",
                   "A clip for a ribbon cable, printed upright and alone: a wall 24 mm wide and 3 mm thick, ten minutes of "
                   "printing. Derek stopped it part way.", h=1010, pos="16% 75%", zoom=151)),
            b.quote("So that last one came out pretty melty there. I stopped it partway, as you&rsquo;ll see. So we definitely "
                    "can&rsquo;t do anything quite like that again without some major part fan cooling and time between layers.",
                    "DEREK · 26 OCTOBER 2026", size=42)
            + f'<div style="margin-top:40px">{_timeline()}</div>'
            + '<p class="cap" style="margin-top:10px"><span class="lab">One scale of seconds</span>Orange is the nozzle printing '
              'the part. Blue is the nozzle away, printing a tower that is thrown out.</p>'
            + '<div class="grid2" style="margin-top:30px; gap:44px">'
            + b.stat('1 to 3.5 <span>s</span>', "a whole layer, high on the clip that melted. Read from its file.")
            + b.stat('24 <span>s away</span>', "after each layer of the lone cap, whose shortest layer was 3 s of printing.", hot=True)
            + "</div>"
            + p(f"<b>The file does not wait by itself.</b> Many profiles slow down when a layer is short. This one will not "
                f"slow a layer that takes more than {slow} s.", style="margin:30px 0 0"),
            gap=70, style="margin-top:34px")
        + b.rulebar(40, 36)
        + '<h3 style="margin-bottom:22px">Three ways it gets the time</h3>' + ways_html
        + b.row(
            b.quote("But, sometimes I want to print just one.", "DEREK · 7 NOVEMBER 2026", size=47),
            ("0 0 1150px",
             b.record(b.link("The melted clip and its photographs", f"{CLIP}/physical-result.json", CLIP_REV),
                      b.link("The retry that night", "future/snap-fit-tests/2026-10-26-mark2-combined/README.md", CLIP_REV),
                      b.link("The lone cap, timed", f"{CAPS}/2026-11-07-single-regulator-mark2/job.json"),
                      b.link("The batch, timed", f"{CAPS}/2026-11-07-taller-tips-mark2/job.json"),
                      b.link("The white cover", f"{COVER}/prints/2026-11-11-white-wing-seat-mark1/slice-review.json"),
                      b.link("Small parts in the cooling rule", f"{PP}/cooling/README.md", anchor="small-individual-parts"))),
            gap=70, style="margin-top:36px")
        + b.still_open("The retry on the night of 26 October changed two things at once: three parts shared the plate with a "
                       "20-second floor on each layer, and the fan ran at 100 percent. The lone cap of 7 November printed fine "
                       "on time alone, with the fan off except over air. No small part has been printed alone and unhelped "
                       "since, so there is no control, and nobody has measured a temperature. Twenty seconds was a target "
                       "borrowed from other people&rsquo;s practice.")
    )
    return Page("petgf-time-between-layers", "PET-GF: a small part needs time between layers", "petgf", body, right="Small parts")


# ----------------------------------------------------------------------------- 7 the surface
def _seam_plans():
    W, H = 1055, 250

    def wall(ox, notch):
        top, bot = 96, 150
        if notch:
            d = f"M{ox} {top}H{ox + 210}V{top + 24}H{ox + 330}V{top}H{ox + 480}V{bot}H{ox}Z"
        else:
            d = f"M{ox} {top}H{ox + 480}V{bot}H{ox}Z"
        dot = (ox + 330, top + 24) if notch else (ox + 270, top)
        return (f'<path d="{d}" fill="{k.COLD}"/>'
                f'<circle cx="{dot[0]}" cy="{dot[1]}" r="14" fill="{k.HOT}"/>'
                + k.label(ox, 196, "THE WALL, SEEN FROM ABOVE", 22)
                + k.label(ox, 54, "SEAM IN A CORNER OF A CHANNEL" if notch else "SEAM ON THE FLAT FACE", 25, fill=k.INK, weight=600)
                + k.label(ox + 480, 84, "OUTSIDE", 22, anchor="end", fill=k.FAINT))

    return k.svg(W, H, wall(10, False) + wall(565, True), "Where the seam sits on the cold-core shell's wall",
                 "Two plan views of a wall. In the first the seam, where each layer starts and stops, sits on the flat outside "
                 "face. In the second a shallow channel runs down the wall and the seam sits in its inside corner.")


def surface():
    seam = b.asset("petgf-setup-shell-seam.jpg", f"{SHELL}/2026-10-26-mark2-round-ports-a2/physical-result/photos/04-overview.jpg", max_px=2000)
    ripples = b.asset("petgf-setup-shell-ripples.jpg", f"{SHELL}/2026-10-29-mark2-seam-channel/physical-result/photos/03-wall-overview.jpg", max_px=2000)
    body = (
        b.head("Surface", "A matte wall hides the layers and nothing else.",
               "On a flat PET-GF wall the layers vanish into the grain. That leaves a face so even that anything which breaks "
               "it stands out: the seam where every layer starts and stops, a patch of ripples, a flat in the model. Some of "
               "it shows only when the light comes from the side.", lede_size=54)
        + b.scope("black PET-GF · Mark2 · textured PEI · left 0.4 mm nozzle",
                  not_tried="white or coloured PET-GF, which nobody has set beside the black")
        + '<div class="grid2" style="margin-top:30px">'
        + b.fig(seam, "A large matte black printed shell with a straight line and a band of different sheen down one face",
                "Printed 26 October 2026 · Mark2 · black PET-GF",
                "The shell that wraps the cold core. The line down its face is the seam, and the band beside it is where the "
                "seam was feathered. &ldquo;It&rsquo;s really quite small, just very noticeable.&rdquo;", h=700, pos="50% 55%")
        + b.fig(ripples, "The same kind of shell with a clean matte face and a small patch of ripples at its top edge",
                "Printed 29 October 2026 · Mark2 · black PET-GF",
                "The next shell, with the seam moved into a channel on another flank. The face is clean. What is left is a "
                "thumbnail of ripples at the top edge. &ldquo;In some lights it&rsquo;s not visible at all, but in others, as you "
                "can see, it is quite visible there.&rdquo;", h=700, pos="50% 42%")
        + "</div>"
        + b.rulebar(40, 36)
        + b.row(
            ("0 0 1055px",
             '<h2>Give the seam a corner</h2>'
             + p("Each layer of a wall starts and stops somewhere, and on PET-GF that spot shows. Blending it along the face "
                 "made a band instead of a line. The shell of 29 October has a shallow channel down one flank, and every "
                 "layer but the first starts in the channel&rsquo;s inside corner.")
             + _seam_plans()
             + p("On the outside of the machine the standing walls are fluted. The grooves lay their own light and shadow, "
                 "finer and far stronger than a layer line, and the seam between front and back sits in one.",
                 style="margin:16px 0 0")),
            '<h2>Three things that showed</h2>'
            + p("<b>Flats.</b> 18 September 2026, the first PET-GF faucet: &ldquo;Some of those defects (low resolution polygons "
                "on what should be smooth surfaces) are showing through in the final print.&rdquo;", style="margin-bottom:20px")
            + p("<b>The seam.</b> 28 October 2026, the first shell: &ldquo;if this were an exterior surface, we&rsquo;d have to keep "
                "iterating for a while.&rdquo;", style="margin-bottom:20px")
            + p("<b>Ripples.</b> 1 November 2026, the second shell. Derek&rsquo;s guess is the tall layers near the top and the "
                "hole cut through the wall beside them: &ldquo;you can see it lines up pretty precisely with where we cut our "
                "hole there.&rdquo;", style="margin-bottom:30px")
            + b.quote("But this is a defect that we are okay shipping with.", "DEREK · 1 NOVEMBER 2026", size=47)
            + p("That patch is now the first entry in a register of accepted defects. Its photographs define what ships.",
                style="margin:26px 0 0"),
            gap=60)
        + '<div style="margin-top:30px">'
        + b.record(b.link("The first shell and its seam", f"{SHELL}/2026-10-26-mark2-round-ports-a2/physical-result/physical-result.json"),
                   b.link("The second shell and its ripples", f"{SHELL}/2026-10-29-mark2-seam-channel/physical-result/physical-result.json"),
                   b.link("Where its seam starts, layer by layer", f"{SHELL}/2026-10-29-mark2-seam-channel/README.md"),
                   b.link("Accepted defects", "hardware/defects-and-tolerances.md"),
                   b.link("Fluted and flat, in two plastics", f"{PP}/cadlib/flute-evidence/README.md"),
                   b.link("The faucet&rsquo;s flats", f"{PP}/faucet/faucet-shell/print-log.md", anchor="pet-gf-faucet-with-open-forward-lever-clearance--2026-09-18-mark2"))
        + "</div>"
        + b.still_open("The cause of the ripples is Derek&rsquo;s guess and has not been tested. On two failed prints the bad "
                       "courses came out glossy where sound PET-GF is matte: the melted clip of 26 October and the courses "
                       "above a bridge on 5 November. Nobody has tested whether gloss can be read as a sign of heat.")
    )
    return Page("petgf-a-matte-wall", "PET-GF: a matte wall hides the layers and nothing else", "petgf", body, right="Surface")


def pages():
    return [plastic(), recipe(), trim(), edge(), cooling(), small_parts(), surface()]
