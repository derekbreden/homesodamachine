"""PET-CF: what the faucet was printed in before PET-GF, and what it left behind. Two pages: the
print log of its twenty-one tries, and which of its lessons went on to PET-GF."""
import bookkit as b
import svgkit as k
from bookkit import Page

LOG = "hardware/printed-parts/faucet/faucet-shell/print-log.md"
STEEL = "#27313b"   # a bought metal part in a drawing; svgkit has no colour for one
SETTINGS = "Metadata/project_settings.config"


def sources():
    b.source("petcf", "hardware/printed-parts/faucet/faucet-pet-cf.3mf", member=SETTINGS)   # the faucet's last PET-CF project, saved 14 June 2026
    b.source("petgf", "hardware/printed-parts/petgf.3mf", member=SETTINGS)                  # the shared PET-GF project


def cf(pointer):
    return b.setting("petcf", pointer)


def gf(pointer):
    return b.setting("petgf", pointer)


# ----------------------------------------------------------------------------- page 1: the run
# What the print log records of each try: no part, a part with a fault, a part Derek accepted, or nothing written.
TRIES = ["none", "none", "none", "none", "fault", "blank",
         "kept", "none", "kept",
         "fault", "fault", "fault", "fault", "kept", "blank",
         "fault", "blank", "kept",
         "fault", "kept", "blank"]
GROUPS = [(1, 6, "CLOGS AND AIR", "BY 2 MAY TO 4 MAY · 0.4 MM"), (7, 9, "A WIDER NOZZLE", "9 AND 10 MAY · 0.6 MM"),
          (10, 15, "THREE PIECES", "18 TO 22 MAY"), (16, 18, "A SECOND BRAND", "26 AND 27 MAY"), (19, 21, "SCREWS", "10 TO 14 JUNE")]


def disc(cx, cy, r, state, text=""):
    size = round(r * 0.86)
    num = lambda fill: (f'<text x="{k.n(cx)}" y="{k.n(cy + size * 0.36)}" text-anchor="middle" font-family="IBM Plex Mono, monospace" '
                        f'font-weight="600" font-size="{size}" fill="{fill}">{text}</text>') if text else ""
    if state == "kept":
        return f'<circle cx="{k.n(cx)}" cy="{k.n(cy)}" r="{r}" fill="{k.COLD}"/>' + num("white")
    if state == "fault":
        return f'<circle cx="{k.n(cx)}" cy="{k.n(cy)}" r="{r - 3}" fill="white" stroke="{k.COLD}" stroke-width="6"/>' + num(k.INK)
    if state == "none":
        return f'<circle cx="{k.n(cx)}" cy="{k.n(cy)}" r="{r - 2}" fill="white" stroke="{k.BAD}" stroke-width="4" stroke-dasharray="9 7"/>' + num(k.BAD)
    return f'<circle cx="{k.n(cx)}" cy="{k.n(cy)}" r="{r - 2}" fill="white" stroke="{k.FAINT}" stroke-width="4" stroke-dasharray="3 7"/>' + num(k.MUTED)


def run():
    W, H, CY, R, P, GAP = 2170, 336, 132, 36, 90, 50
    xs, x = [], 78
    for i in range(21):
        if any(i + 1 == a for a, _, _, _ in GROUPS[1:]):
            x += GAP
        xs.append(x)
        x += P
    g = []
    for a, z, name, when in GROUPS:
        x0, x1 = xs[a - 1] - R, xs[z - 1] + R
        g.append(k.line(x0, CY + 58, x1, CY + 58, k.INK, 3))
        g.append(k.label((x0 + x1) / 2, CY + 96, name, 26, anchor="middle", fill=k.INK, weight=600))
        g.append(k.label((x0 + x1) / 2, CY + 128, when, 23, anchor="middle"))
    for i, state in enumerate(TRIES):
        g.append(disc(xs[i], CY, R, state, str(i + 1)))
    for i, text in ((6, "4 MAY · A TOOLHEAD PART BROKEN, A SECOND PRINTER ORDERED"), (15, "24 MAY · PRINTED PEGS SHEAR OFF")):
        fx = (xs[i - 1] + xs[i]) / 2
        g.append(k.label(fx, 34, text, 23, anchor="middle", fill=k.INK))
        g.append(k.line(fx, 46, fx, CY + 30, k.INK, 3, dash="5 7"))
    lx = 78
    for state, text in (("none", "NO PART"), ("fault", "A PART WITH A FAULT"), ("kept", "A PART DEREK ACCEPTED"), ("blank", "RESULT NOT WRITTEN DOWN")):
        g.append(disc(lx, H - 22, 15, state) + k.label(lx + 28, H - 13, text, 23))
        lx += 60 + len(text) * 15.4
    return k.svg(W, H, "".join(g), "Twenty-one tries at the faucet in PET-CF, in order",
                 "Twenty-one numbered discs in a row, in five groups. Tries 1 to 4 and 8 are dashed red rings: no part came off. Tries "
                 "5, 10 to 13, 16 and 19 are open rings: a part with a fault. Tries 7, 9, 14, 18 and 20 are solid: a part Derek accepted. "
                 "Tries 6, 15, 17 and 21 are faint: the log does not say how they came out. Two notes mark what happened between "
                 "tries: on 4 May a toolhead part was broken and a second printer ordered, and on 24 May printed pegs sheared off.")


PHASES = [
    ("Clogs and air", "TRIES 1 TO 6<br>BY 2 MAY TO 4 MAY<br>0.4 MM NOZZLES",
     "Two clogs above the hot end. A calibration that failed &ldquo;over and over&rdquo;. A print that &ldquo;started printing air&rdquo; "
     "near layer 15 with nothing blocked. The fifth finished, full of gaps. For the sixth the spool was dried twelve more hours and "
     "everything was slowed down, and how it came out was never written. On 4 May, clearing a clog with a wire pushed up from below "
     "snapped a pincer in the right-hand heating assembly of the toolhead and cut its cable. The spare was sold out. A second printer "
     "was ordered that night, and that is why there are two."),
    ("A wider nozzle", "TRIES 7 TO 9<br>9 AND 10 MAY<br>0.6 MM TUNGSTEN CARBIDE",
     "An off-brand 0.6 mm nozzle arrived on 9 May. With it the stock profile went back on and the supports were printed in PET-CF "
     "too. &ldquo;The most recent PET-CF print worked beautifully.&rdquo; Try eight, the shell in one piece, &ldquo;failed in an "
     "interesting way, the support tower fell over&rdquo; and fused into the top of the faucet. Try nine gave the tower a wide first "
     "layer and rooted every support on the bed. &ldquo;The last print is beautiful! Actual success, and I was able to remove all the "
     "supports even those from inside of the tube.&rdquo;"),
    ("Three pieces", "TRIES 10 TO 15<br>18 TO 22 MAY<br>TWO PUSH-FIT JOINTS",
     "The gooseneck was cut into three pieces. Drawn with no clearance, the straight joint stopped &ldquo;just 2 mm short&rdquo; and "
     "the curved one jammed a third of the way in. With half a millimetre and more: &ldquo;it definitely made a difference, but far "
     "too much of one, lol.&rdquo; Three more prints closed in on five hundredths of a millimetre a side. &ldquo;Pretty good. Or good "
     "enough at least for now.&rdquo;"),
    ("A second brand", "TRIES 16 TO 18<br>26 AND 27 MAY<br>POLYMAKER FOR BAMBU",
     "The Bambu spool ran out and Polymaker&rsquo;s PET-CF went on with nothing else changed. A tall support came apart and the outer "
     "walls had small bare patches. Ten hours in the dryer changed nothing. A hotter nozzle with the fan off, then the first "
     "diamond-tipped nozzle and a flow calibration: &ldquo;They do look better. I still see some, but far less noticeable&hellip;&rdquo; "
     "The new brand also printed glossy where the old one was matte."),
    ("Screws, a slower top", "TRIES 19 TO 21<br>10 TO 14 JUNE<br>THE SHELL REDRAWN",
     "The plate under the faucet got three screws (next page) and the tip got a cradle for the display. Everything came out too "
     "tight. Try twenty opened the fits: &ldquo;things fit as well as I need them to for now.&rdquo; One fault was left, strands "
     "drooping at the top of the piece that prints standing on end. Try twenty-one slows its last few millimetres to 40 % speed and "
     "20 % acceleration, with the fan on."),
]


def tries():
    sources()
    photo = b.asset("petcf-try-nine.jpg", "public/post-images/2026-05-10-faucet-shell-thumbnail.png", "b100c064b",
                    kind="Frame from the project's video of 10 May 2026, a photograph with the video's title drawn across the top")
    rows = "".join(
        f'<div style="display:flex; gap:44px; padding:17px 0 15px; border-top:2px solid var(--line)">'
        f'<div style="flex:0 0 420px"><p style="margin:0; font:650 42px/1.15 \'IBM Plex Sans\'; color:var(--ink)">{title}</p>'
        f'<p class="mono" style="margin:8px 0 0; font-size:23px; line-height:1.45; letter-spacing:.06em; color:var(--muted)">{when}</p></div>'
        f'<p class="small" style="margin:0; font-size:33.5px">{text}</p></div>' for title, when, text in PHASES)
    body = (
        b.head("Spring 2026 · the faucet", "Twenty-one tries at one faucet.",
               "PET-CF is PET with chopped carbon fibre in it: stiff, matte and hard on nozzles. This is the print log of its first "
               "job here, try by try, in Derek&rsquo;s words.", size=150)
        + b.scope("Bambu PET-CF (tries 1 to 15), Polymaker Fiberon PET-CF17 (16 to 21) · H2C · left nozzle · textured PEI")
        + f'<div style="margin-top:30px">{run()}</div>'
        + f'<div style="margin-top:22px; border-bottom:2px solid var(--line)">{rows}</div>'
        + b.row(
            ("0 0 1000px", b.fig(photo, "A matte black printed faucet shell lying on white paper, fitted over a metal valve with its lever",
                                 "10 May 2026 · Bambu PET-CF · 0.6 mm nozzle",
                                 "Try nine on the valve it covers: the first whole faucet shell. The rough patch at the far end is "
                                 "where supports stood. The frame is from the video posted that day, with its title cropped off the top.",
                                 h=330, pos="29% 47.5%", zoom=128)),
            b.quote("the direction that things are falling are actually the direction they are being pulled, and it is the force of the "
                    "movement that is pulling things apart. So my thought is 'less velocity' => 'less force'.",
                    "DEREK · 14 JUNE 2026, ON TRY TWENTY-ONE", size=41)
            + b.still_open("Try twenty-one was sliced on 14 June and its result was never written down, so that thought is untested on "
                           "the record. Try seven changed the nozzle, the profile and the support plastic together, and which of them "
                           "ended the clogs was never separated."),
            gap=70, style="margin-top:34px")
        + '<div style="margin-top:22px">'
        + b.record(b.link("The print log", LOG),
                   b.link("Why a second printer", "hardware/purchases.md", "53aee16c1"),
                   b.link("Clearing a clog without breaking the toolhead", LOG, anchor="h2c-right-side-dual-extruder-unit--clog-access-procedure"),
                   b.link("The last PET-CF project", "hardware/printed-parts/faucet/faucet-pet-cf.3mf"),
                   b.link("The video post", "posts/2026-05-10-2244.md", "b100c064b")) + "</div>"
    )
    return Page("twenty-one-tries-at-one-faucet", "PET-CF: twenty-one tries at one faucet", "petcf", body, right="The print log")


# ----------------------------------------------------------------------------- page 2: what carried over
def peg_and_screw():
    W, H, BED = 2170, 520, 440
    g = []
    # a peg printed in one with the plate
    g.append(k.block(84, 756, 0, 3, BED))
    g.append(k.missing(378, k.row_y(11, BED), 504, BED - 4 * k.ROW_H))
    g.append('<g transform="translate(52 -4) rotate(17 504 344)">' + k.block(378, 504, 4, 11, BED) + "</g>")
    g.append(k.line(366, 344, 560, 344, k.BAD, 5))
    g.append(k.arrow(196, 214, 356, 214, k.INK, 5) + k.label(84, 190, "A SIDEWAYS PUSH", 25, fill=k.INK))
    g.append(k.label(84, 52, "A PEG PRINTED WITH THE PLATE", 30, fill=k.INK, weight=600))
    g.append(k.label(441, 500, "IT BREAKS BETWEEN TWO LAYERS", 25, anchor="middle", fill=k.BAD, weight=600) + k.line(441, 474, 441, 350, k.BAD))
    g.append(k.label(790, 420, "THE PLATE,", 25) + k.label(790, 452, "LAID FLAT", 25))
    # a screw through a wide boss
    ox = 1100
    g.append(k.block(ox + 84, ox + 399, 0, 3, BED) + k.block(ox + 441, ox + 756, 0, 3, BED))                # the plate, with a hole
    g.append(k.block(ox + 294, ox + 399, 4, 7, BED) + k.block(ox + 441, ox + 546, 4, 7, BED))                # its boss
    g.append(k.block(ox + 126, ox + 282, 4, 7, BED) + k.block(ox + 558, ox + 714, 4, 7, BED))                # the shell around the boss
    g.append(k.block(ox + 126, ox + 378, 8, 10, BED) + k.block(ox + 462, ox + 714, 8, 10, BED) + k.block(ox + 126, ox + 714, 11, 12, BED))
    g.append(f'<rect x="{ox + 380}" y="{k.n(k.row_y(10, BED) + 2)}" width="80" height="68" fill="{k.BRASS}"/>')
    g.append(f'<rect x="{ox + 370}" y="{k.n(k.row_y(1, BED))}" width="100" height="54" fill="white"/>')
    g.append(f'<rect x="{ox + 406}" y="{k.n(k.row_y(10, BED) + 12)}" width="28" height="{k.n(BED - 44 - k.row_y(10, BED) - 12)}" fill="{STEEL}"/>')
    g.append(f'<rect x="{ox + 378}" y="{BED - 44}" width="84" height="44" rx="5" fill="{STEEL}"/>')
    g.append(k.label(ox + 84, 52, "A SCREW THROUGH A WIDE BOSS", 30, fill=k.INK, weight=600))
    for (px, py), ty, lines in (((ox + 460, 210), 196, ("THREADED INSERT,", "MELTED IN")), ((ox + 546, 306), 306, ("A WIDE BOSS", "ON THE PLATE")),
                                ((ox + 462, 420), 416, ("STEEL SCREW,", "DRIVEN FROM BELOW"))):
        g.append(k.line(px, py, ox + 776, ty - 8, k.INK, 3) + f'<circle cx="{px}" cy="{py}" r="7" fill="{k.INK}"/>')
        g += [k.label(ox + 790, ty + 32 * i, text, 25, fill=k.INK) for i, text in enumerate(lines)]
    g.append(k.label(ox + 126, 124, "THE SHELL", 25))
    return k.svg(W, H, "".join(g), "A printed peg that sheared, beside the screw that replaced it",
                 "Two sections. On the left a flat plate made of four courses with a narrow peg standing on it; the peg has broken off "
                 "at its base along a layer line and tipped over, and a dashed red outline shows where it stood. On the right the same "
                 "plate with a wide boss, a steel screw driven up through the boss, and a threaded insert in the shell above that the "
                 "screw turns into.")


def carried():
    sources()
    table = ('<table class="grid" style="font-size:31px"><thead><tr><th></th><th>PET-CF<br>14 June 2026</th><th>PET-GF<br>15 August 2026</th>'
             '<th>PET-GF<br>now</th></tr></thead><tbody>'
             + "".join(f'<tr><th style="padding:11px 16px 11px 0; font-weight:400; color:var(--muted)">{a}</th>'
                       + "".join(f'<td style="padding:11px 16px 11px 0"><b>{v}</b></td>' for v in vals) + "</tr>" for a, *vals in [
                 ("Nozzle heat", cf("/nozzle_temperature/0") + " °C", "290 °C", gf("/nozzle_temperature/0") + " °C"),
                 ("Plate", cf("/textured_plate_temp/0") + " °C", "100 °C", gf("/textured_plate_temp/0") + " °C"),
                 ("Chamber heater", cf("/chamber_temperatures/0") + " °C", "50 °C", gf("/chamber_temperatures/0") + " °C"),
                 ("Part fan", cf("/fan_max_speed/0") + " %", "0 %", gf("/fan_max_speed/0") + " %, " + gf("/overhang_fan_speed/0") + " % on overhangs"),
                 ("Most plastic a second", cf("/filament_max_volumetric_speed/0") + " mm³", "5 mm³", gf("/filament_max_volumetric_speed/0") + " mm³"),
                 ("The slicer calls it", cf("/filament_type/0"), "PET-CF", gf("/filament_type/0")),
             ]) + "</tbody></table>")
    item = lambda t, d: f'<p class="small" style="font-size:33.5px; margin:0 0 18px"><b>{t}</b> {d}</p>'
    body = (
        b.head("What it left behind", "A plastic&rsquo;s lessons stay with it.",
               "From May to August 2026 the faucet was PET-CF. Then the machine moved to PET-GF, glass fibre in place of carbon. "
               "What PET-CF had taught about layers and about the printer went along. What it had taught about itself did not.", size=150)
        + b.scope("PET-CF, May and June 2026 · PET-GF from 15 August 2026 · left nozzle of an H2C · textured PEI")
        + f'<figure style="margin-top:30px">{peg_and_screw()}'
          '<div style="display:flex; gap:60px; margin-top:12px">'
          '<p class="cap" style="margin:0; flex:0 0 1040px"><span class="lab">23 to 25 May 2026 · PET-CF</span>To save two screws the plate was '
          'given two printed pegs. One snapped off as the plate went in. Thinner ones snapped too. &ldquo;they still don&rsquo;t fit, and they '
          'snap so easy because of the orientation of the layer lines. This is just not workable.&rdquo;</p>'
          '<p class="cap" style="margin:0; flex:1 1 0"><span class="lab">10 June 2026 · PET-CF, and PET-GF today</span>Three wide bosses, each '
          'with a steel screw through it. The faucet is still held to its plate this way. This lesson was about layers, and it moved '
          'to PET-GF with nothing to change.</p></div></figure>'
        + b.rulebar(30, 30)
        + b.row(
            ("0 0 1070px",
             '<h2>Stayed with PET-CF</h2>'
             + item("Its settings.", "PET-GF&rsquo;s profile began as a copy of PET-CF&rsquo;s, so the first PET-GF print ran on PET-CF&rsquo;s "
                    "plate, chamber and flow limit. Ten days later the faucet&rsquo;s copy was checked against the maker&rsquo;s sheet. The "
                    "plate and the chamber were both hotter than PET-GF is meant to have, and they came down. One thing never changed: "
                    "the name.")
             + table
             + '<div style="height:22px"></div>'
             + item("Its fits.", "The push-fit joints settled at five hundredths of a millimetre a side on 21 May. On 10 June, in the "
                    "second brand, the same joints were too tight and went to a quarter of a millimetre on the diameter. PET-GF&rsquo;s fits "
                    "were found again from nothing.")),
            '<h2>Carried on paper, and wrong</h2>'
            + item("&ldquo;No snaps.&rdquo;", "On 21 May the snap fits came off the pump case, on the reasoning that PET-CF is too stiff and "
                   "brittle to flex. No snap that broke is on the record. On 25 August the same reasoning was written down as a rule for "
                   "PET-GF: a catch goes home &ldquo;never by deflecting&rdquo;. On 16 September the rule was deleted and the faucet&rsquo;s "
                   "display cover got two sprung wings. The next day: &ldquo;They are tough though, and do spring back.&rdquo;")
            + b.quote("&hellip;those broad long thin (but not too thin!) walls provide the necessary give and spring, more so than anything "
                      "else anyone else has tried, in PET-GF so far.", "DEREK · 20 SEPTEMBER 2026", size=38)
            + '<h2 style="margin-top:30px">Went along to PET-GF</h2>'
            + item("The left nozzle, and a hard one.", "Carbon and glass both wear a nozzle away. Both print from the left hotend, the "
                   "one that takes tungsten carbide and diamond tips.")
            + item("Hands off a clog from below.", "The toolhead comes apart from the top, in order. Learning that broke one and bought the second printer.")
            + item("A second brand is a second plastic.", "On 17 May the choice was written up as PET-CF from any maker. Nine days later "
                   "the second maker&rsquo;s spool failed on the first one&rsquo;s settings.")
            + item("The dryer, and its limit.", "Both dry in the same dryer. Drying did not fix what was not damp."),
            gap=64)
        + '<p class="small" style="font-size:33.5px; margin:10px 0 0"><b>15 August 2026.</b> The first PET-GF print was the top front quarter '
          'of the enclosure, and on 24 August the faucet&rsquo;s material was changed to match. About six hours into that first print Derek '
          'wrote that it was &ldquo;working a treat so far&rdquo; and called what had printed &ldquo;very beautiful wall surface.&rdquo;</p>'
        + b.still_open("No PET-CF snap was ever printed and broken on the record, so &ldquo;too brittle to snap&rdquo; is still a "
                       "reasoning, not a result. PET-GF&rsquo;s snaps have been judged in the hand. None has a measured force or a count "
                       "of cycles.")
        + '<div style="margin-top:20px">'
        + b.record(b.link("The pegs, in the print log", LOG, anchor="pet-cf-print-attempt-16-no-joinery-features--plate--3-piece-shell-slice-renamed-faucet-pet-cfmf"),
                   f'<a href="{b.GITHUB}/commit/1f98b24a5">Snaps off the pump case</a>',
                   b.link("The rule written for PET-GF", "hardware/design-pressures.md", "9cf1c4477"),
                   f'<a href="{b.GITHUB}/commit/9af69a846">The rule deleted</a>',
                   b.link("The cover that springs", "hardware/printed-parts/faucet/faucet-display-cover/physical-acceptance.json"),
                   b.link("The first PET-GF print", "hardware/printed-parts/enclosure/enclosure/print-log.md", "cfcaf5dfc"),
                   f'<a href="{b.GITHUB}/commit/47fe7dce8">PET-CF&rsquo;s plate and chamber come down</a>',
                   b.link("Which nozzle goes where", "hardware/ledger/tools.md", anchor="which-hotends-fit-an-h2c")) + "</div>"
    )
    return Page("a-plastics-lessons-stay-with-it", "PET-CF: a plastic&rsquo;s lessons stay with it", "petcf", body, right="What carried over")


def pages():
    return [tries(), carried()]
