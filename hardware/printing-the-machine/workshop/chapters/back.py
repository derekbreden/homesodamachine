"""At the back: the rules that had to be repeated, the nine months on one page, and how the book is kept."""
import bookkit as b
import svgkit as k
from bookkit import Page

SAID = [
    ("Fewer edges, more material.",
     "&hellip;an attempt to use less material when less material is basically the opposite of our goal.", "19 Oct", "any", "Any plastic",
     [("5 Oct", "b20e7d208"), ("8 Oct", "23db8c58e"), ("10 Oct", "498369996"), ("19 Oct", "444346f44"), ("19 Oct", "e681cc367"),
      ("25 Oct", "7c311ff22"), ("27 Oct", "c82784774"), ("1 Nov", "9a96de823"), ("12 Nov", "a8f24b2b5")]),
    ("Blocks of support do not come out of a cavity. Short trees rooted inside it do.",
     "lol, lmfao, it is *every* support here &hellip; there&rsquo;s no way I&rsquo;m going to be able to do anything with this except throw it away", "9 Oct", "petgf", "PET-GF",
     [("4 Oct", "922c8d6f4"), ("9 Oct", "f8f4e7f01"), ("9 Oct", "684dc2f2b"), ("11 Oct", "78eb4b6f8"), ("25 Oct", "d57670e38"),
      ("6 Nov", "65066d840"), ("8 Nov", "d5bf35612")]),
    ("What one print proved has to reach the next print.",
     "Please start me a complete faucet with ***EVERYTHING*** we&rsquo;ve learned.", "15 Oct", "any", "Any plastic",
     [("5 Oct", "67994c7ef"), ("14 Oct", "ba17c3430"), ("15 Oct", "cb5632d2c"), ("26 Oct", "948e0bff4"), ("7 Nov", "3ccd9d1e9"), ("11 Nov", "ec257a4db")]),
    ("Change one thing. Do not print the control again.",
     "&hellip;get back to our normal settings, and pick one specific thing to change to address the problem we are seeing.", "9 Oct", "any", "Any plastic",
     [("9 Oct", "9f5865af2"), ("15 Oct", "7fde4f2a4"), ("8 Nov", "d85cd06c1"), ("9 Nov", "908851a7a"), ("12 Nov", "2f17ad737")]),
    ("Fan on every bridge and overhang, and nowhere else.",
     "We can use 100% cooling if we want, but only on the places that actually need it&hellip;", "17 Oct", "petgf", "PET-GF",
     [("15 Oct", "7fde4f2a4"), ("17 Oct", "9ae148e1d"), ("6 Nov", "f62c528c4"), ("12 Nov", "4494e83e3")]),
    ("A first-layer trim belongs to one printer, one plate and one plastic.",
     "The +0.04 trim was a *special* case for a problem with a *specific* print - not a change to the rule for Mark1.", "8 Oct", "any", "Each plastic",
     [("8 Oct", "8d7be0e3c"), ("13 Oct", "a86ede62e"), ("25 Oct", "7248987e1"), ("6 Nov", "926988d8a")]),
    ("Stay off the edges of a textured plate that has not been printed on.",
     "You can&rsquo;t print that close to the edge of the bed on a plate that hasn&rsquo;t been seasoned properly first.", "6 Oct", "petgf", "Textured plate",
     [("4 Oct", "5d2b1b080"), ("6 Oct", "464f0465c"), ("10 Oct", "723faaef7")]),
]


def said():
    def tally(n):
        g, x = [], 6
        for i in range(n):
            if i % 5 == 4:
                g.append(k.line(x - 64, 62, x + 4, 10, k.HOT, 9))
                x += 30
            else:
                g.append(k.line(x, 8, x, 64, k.HOT, 9))
                x += 17
        return k.svg(190, 72, "".join(g), f"{n} marks", style="width:190px")

    def dates(marks):
        return " · ".join(f'<a href="{b.GITHUB}/commit/{sha}">{d.upper()}</a>' for d, sha in marks)

    rows = "".join(
        f'<div style="display:grid; grid-template-columns:230px 1fr 280px; gap:30px; align-items:start; padding:24px 0 22px; border-top:2px solid var(--line)">'
        f'<div>{tally(len(marks))}<p class="mono" style="margin:10px 0 0; font-size:27px; letter-spacing:.08em; color:var(--muted)">{len(marks)} TIMES</p></div>'
        f'<div><p style="margin:0 0 10px; font:650 56px/1.12 \'IBM Plex Sans\'; letter-spacing:-0.01em; color:var(--ink)">{rule}</p>'
        f'<p style="margin:0 0 10px; font:italic 400 37px/1.34 \'IBM Plex Sans\'; color:var(--text)">&ldquo;{q}&rdquo; <span class="mono" style="font-style:normal; font-size:26px; letter-spacing:.06em; color:var(--faint); margin-left:8px">{d.upper()}</span></p>'
        f'<p class="mono" style="margin:0; font-size:24px; line-height:1.5; letter-spacing:.06em; color:var(--faint)">{dates(marks)}</p></div>'
        f'<p style="margin:12px 0 0; text-align:right"><span class="tag" style="background:{b.PARTS[part][2]}">{label}</span></p></div>'
        for rule, q, d, part, label, marks in SAID
    )
    body = (
        b.head("The rules, ranked by the record", "Seven things that had to be said again.",
               "Since late September 2026, every change to the machine is saved with the words that asked for it. Read back in order, they are a "
               "ledger of what the written record kept failing to pass on. Each mark is one commit that carries Derek saying it, and each date opens that commit.",
               size=160, lede_size=52)
        + f'<div style="margin-top:40px">{rows}<div style="border-top:2px solid var(--line)"></div></div>'
        + b.row(
            ("0 0 520px", '<h3>And from the night this book was asked for</h3><p class="tiny" style="margin-top:14px">12 November 2026.</p>'),
            b.quote("The only reason a bridge works is because it *is* a bridge that actually has a column supporting both ends.", "DEREK", size=41),
            b.quote("Do not use finer layers anywhere - that is not an option - that is a completely different variable", "DEREK", size=41),
            gap=70, style="margin-top:36px")
    )
    return Page("seven-things-that-had-to-be-said-again", "Seven things that had to be said again", "back", body, right="The rules")


EVENTS = [
    ("March", [("22", "h2c", "The first printer is ordered.")]),
    ("April", [("2", "any", "The first test prints: three snap-fit struts."),
               ("5", "any", "A section of general printing advice is deleted from the repository."),
               ("23", "any", "A printed pressure vessel is abandoned.")]),
    ("May", [("2", "petcf", "The faucet&rsquo;s print log opens, in PET-CF."),
             ("4", "h2c", "A hotend is wrecked clearing a clog. The second printer is ordered."),
             ("10", "petcf", "Faucet attempt nine is logged as a success."),
             ("22", "petg", "The first reservoir attempt in PETG."),
             ("30", "petg", "The first reservoir that holds water."),
             ("30", "tpu", "An 85A TPU seal seats.")]),
    ("June", [("14", "any", "A float is printed around a magnet for the first time."),
              ("18", "any", "The first test coupon cut from the enclosure.")]),
    ("August", [("15", "petgf", "The first enclosure piece in PET-GF."),
                ("20", "petgf", "The enclosure&rsquo;s exterior moves to a 0.4 mm nozzle."),
                ("28", "petgf", "A ladder of first-layer trims.")]),
    ("September", [("13", "h2c", "Agents are given the printer controls."),
                   ("14", "petgf", "Sixteen specimens start the support trials."),
                   ("23", "petgf", "Enclosure quadrants come off both printers.")]),
    ("October", [("3", "aero", "The float printed wholly in ASA Aero is accepted."),
                 ("4", "petgf", "A front-top is rejected for its supports."),
                 ("9", "petgf", "A back-top is thrown away for the same reason."),
                 ("13", "tpu", "The first 85A pump elbow fits."),
                 ("17", "petgf", "White covers crack. The fan is limited to bridges and overhangs."),
                 ("22", "tpu", "The elbows print without strings."),
                 ("26", "petg", "A reservoir holds water at the last overlap setting.")]),
    ("November", [("9", "petgf", "The handhold roofs become corbels."),
                  ("10", "petgf", "Support D is adopted across PET-GF."),
                  ("12", "petgf", "A pocket roof is printed over air. This book is asked for.")]),
]


def timeline():
    blocks = []
    for month, events in EVENTS:
        rows = "".join(
            f'<div style="display:grid; grid-template-columns:70px 44px 1fr; align-items:baseline; padding:9px 0">'
            f'<span class="mono" style="font-size:30px; color:var(--muted); text-align:right">{d}</span>'
            f'<span style="justify-self:center; width:22px; height:22px; border-radius:50%; background:{b.PARTS[part][2]}; align-self:center"></span>'
            f'<span style="font-size:36px; line-height:1.3">{t}</span></div>' for d, part, t in events)
        blocks.append(f'<div style="display:grid; grid-template-columns:360px 1fr; padding:22px 0; border-top:2px solid var(--line)">'
                      f'<div style="font:650 60px/1.1 \'IBM Plex Sans\'; color:var(--ink)">{month}</div><div>{rows}</div></div>')
    key = "".join(f'<span style="display:inline-flex; align-items:center; gap:12px; margin-right:36px"><span style="width:22px; height:22px; border-radius:50%; background:{b.PARTS[kk][2]}"></span>{"The project" if kk == "any" else b.PARTS[kk][0]}</span>'
                  for kk in ("any", "petgf", "petg", "tpu", "aero", "petcf", "h2c"))
    body = (
        b.head("2026", "Nine months.",
               "Dates are those of the commit or purchase that records each event.", size=170, top=56)
        + f'<p class="mono" style="margin:34px 0 22px; font-size:27px; letter-spacing:.05em; color:var(--muted)">{key}</p>'
        + "".join(blocks) + '<div style="border-top:2px solid var(--line)"></div>'
    )
    return Page("nine-months", "Nine months", "back", body, right="Timeline")


def colophon():
    body = (
        b.head("How this book is kept", "The page you read is the file an agent reads.",
               "The book lives in the machine&rsquo;s repository, beside the parts it describes. Each page is one plain file.", size=150)
        + b.row(
            b.block("Where it is", cls="", text="The pages are <span class='mono' style='font-size:36px'>hardware/printing-the-machine/NN-title.html</span>, numbered in "
                    "reading order. <span class='mono' style='font-size:36px'>README.md</span> in the same folder is the index: every page&rsquo;s rule, by plastic, "
                    "and where to start for the job in hand.")
            + b.block("Where its pictures come from", cls="", text="Every photograph was taken at the bench and saved with the print it shows. "
                      "<span class='mono' style='font-size:36px'>art/manifest.json</span> lists each one with the file and revision it was copied from. "
                      "Pictures of the model are drawn from the same geometry the printers get.")
            + b.block("Where its numbers come from", cls="", text="Settings in the current recipes are read from their project files each time the book is bound; "
                      "<span class='mono' style='font-size:36px'>guide-inputs.json</span> names those files. Numbers from trials are as they were measured, with a date."),
            b.block("To add a page", cls="", text="Start from a print: its date, printer, plastic, plate and nozzle, and a photograph. Say what happened, then the rule it "
                    "taught, then how far that has been tested. Put it in the part for its plastic. Link the record.")
            + b.block("To bind it", cls="", text="<span class='mono' style='font-size:36px'>tools/run hsm-manual-guides bind printing-the-machine</span> draws every page, "
                      "stops on any whose content overflows, and writes the PDF this was read from.")
            + b.block("What is not in it yet", cls="", text="How far PET-GF leans, and its bridges and fins. Screws and heat-set inserts. Why clear PETG "
                      "moved to a glued plate, and PETG&rsquo;s molds. Reading back the file the printer receives. Each has prints on record and no page.")
            + b.block("Who made it", cls="", text="The prints, the photographs and the judgements are Derek&rsquo;s, made with AI agents over nine months of 2026. "
                      "The pages were written and drawn from that record by Claude (Fable 5.2) in November 2026."),
            gap=90, style="margin-top:60px")
        + b.rulebar(50, 40)
        + b.quote("I&rsquo;d like the repo to be a clear memory to all agents, a written memory that builds FDM print expertise progressively as and when needed. And a PDF that gives a visual high level of it all, so I can see too.",
                  "DEREK · 12 NOVEMBER 2026", size=54)
    )
    return Page("how-this-book-is-kept", "How this book is kept", "back", body, right="Colophon")


def pages():
    return [said(), timeline(), colophon()]
