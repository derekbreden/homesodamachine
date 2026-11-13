# Writing a chapter of "Printing the Machine"

This folder builds a book. The repository around it (`/Users/derekbredensteiner/Developer/homesodamachine`) is a home
soda machine whose enclosure, faucet, reservoirs, seals and fixtures are FDM-printed on two Bambu Lab H2C printers.
Over nine months its owner, Derek, learned a great deal about printing by trial, and the record of those trials is in
the repository: trial folders, print logs, photographs, and commit messages that quote him exactly.

The book turns that record into something a person can read and share, and an agent can learn from. Derek asked for it
in these words: "a beautiful guide that would help anyone (agent or human) with FDM printing, because we'd learned so
much", "something I could share with people", "visual in a way people can actually understand and that fits into a
clean and clear cohesive whole and tells a story and like all the little details that make such a thing great instead
of just okay or passable".

You are writing one chapter. Five finished pages set the standard. Look at them before you write anything:
`preview/_check/out/small/*.png` (pictures) and `chapters/_mine.py` (how they are made).

## The shape of the book

- **One real print per page.** A page is built on something that happened: a print, its date, its printer, its plastic,
  a photograph of it. The rule is the caption of that example. Derek's own principle is that a rule is better encoded
  as an example (`calibration/Principle.md` in the repo).
- **By filament.** The book has a part for each plastic (PET-GF, PETG, TPU, ASA Aero, PET-CF), a short part of
  things that are plain geometry or method, and a part on the printers.
- **Scope is printed on every page.** See the next section.
- **What is unsettled says so.** `b.still_open(...)` marks a conclusion one print suggested and nothing has confirmed,
  a result that changed two things at once, or a test nobody has run. A guide that says what it does not know is
  worth more than one that sounds sure.

## Derek's caution. Read it twice.

When he approved the sample he wrote:

> "I would caution, I already see things in your sample such as the "plate seasoning" which are specific to PET-GF and
> that is a big part of why I was emphasizing that the book be broken up by filament, because you may not even realize
> how much is actually filament specific if you don't look deeply enough into things."

So, for every print you cite, find out **which filament, which printer, which plate and which nozzle** it used, from the
record itself: `launch.json`, `print-job.json`, the `.3mf`'s settings, the trial README, the commit, the colour of the
plastic in the photograph. Do not assume. Then:

- Put it on the page with `b.scope(...)`, e.g. `b.scope("PET-GF · Mark 1 and Mark2 · textured PEI · left 0.4 mm", not_tried="PETG, TPU")`.
- Never carry a lesson from one plastic to another. If a rule was learned in PET-GF, it is a PET-GF rule until a
  print in another plastic shows otherwise. The same question often has opposite answers in two plastics (part
  cooling is one), and those contrasts are some of the best material in the book.
- Look for what is specific to your plastic that nobody has named yet. Read deeper than the research report: the
  print logs, the physical-result files and Derek's quoted words hold more than the summaries do.

## Facts

- The research reports in `dig/` are leads. **They contain errors.** Open the file each fact comes from and read it
  before you write the sentence. If you cannot find the source, leave the fact out.
- `dig/dereks-print-quotes.json` has about 150 of Derek's remarks on printing with the commit that carries each.
  Quote him exactly, asterisks, typos and all, through `b.quote(text, "DEREK · 17 OCTOBER 2026")`. Cut with
  `&hellip;`. Never tidy, merge or invent a quote. `git log -1 --format='%(trailers:key=Derek,valueonly)' <sha>`
  shows the exact words.
- **Numbers.** A number that describes the *current* recipe or the *current* geometry goes stale, so it is never
  typed. Bind it to the file that owns it: `b.source("petgf", "hardware/printed-parts/petgf.3mf", member="Metadata/project_settings.config")`
  then `b.setting("petgf", "/layer_height")`. The book's binder fills it in each time the book is bound. If no JSON
  file owns the number, say it in words without the figure. A number that belongs to a *dated trial* (a result, a
  count, a measurement someone took that day) may be typed, with the trial's date beside it.
- Archived trials are no longer in the working tree. Docs cite them as GitHub URLs with a SHA. Read them with
  `git show <sha>:<path>`; find deleted files with `git log --diff-filter=D --name-only --format='%h %ad' --date=short -- <dir>`.
- Every page ends with `b.record(...)`: links to the files that hold its evidence, made with
  `b.link("label", "path/in/repo", "sha-if-archived")`.

## Voice

- Plain words, short sentences, present tense for what is true now and past tense for what happened. "We" is the
  project.
- The headline is a rule you could say out loud across a workbench, nine words at most, concrete:
  "A bridge needs two landings." "The nozzle goes around. The string goes straight."
- The lede says what happens physically, in two or three sentences, to someone who has never printed.
- Say what happened, in which print, on which date. Then what we do now.
- No hype, no hedging stacks, no rhetorical questions, no "crucial", "key", "robust", "leverage", "ensure".
  No em-dashes as glue; write two sentences. No signposting ("it is worth noting").
- Do not address the reader as "you" except in a short "Before you print" block.
- Dates are written "12 November 2026". Printers are "Mark 1" (its connection name is H2C) and "Mark2".

## What a good page has

1. `b.head(kicker, rule, lede)` and `b.scope(...)`.
2. One main figure that carries the page: a large real photograph, a drawing in the book's four colours, or a
   picture of the model with numbered callouts. Prefer a failure beside its fix, same framing.
3. A short explanation of why it happens. What we do now. Derek's words. Evidence links. What is still open.
4. A full page. No large empty areas, nothing tiny, nothing running into the footer. Columns that end together.

Then **look at it**. Read each rendered page as a picture and fix what is wrong: collisions, text over pictures, a
photograph cropped onto nothing, lopsided columns, a drawing whose labels overlap. A page that passes the build's
checks can still look bad.

## The kit

Read `bookkit.py` (page blocks, photographs, model pictures, bound settings), `svgkit.py` (drawings) and `proj.py`
(placing callouts on a model picture). Their docstrings are the reference. `chapters/_mine.py` shows all of it in use.

A chapter is a file `chapters/<name>.py` with one function:

```python
import bookkit as b
import svgkit as k
from bookkit import Page

def pages():
    return [first_page(), second_page(), ...]   # each returns Page(slug, title, part, body, right="...")
```

- `Page.part` is the key of your part in `bookkit.PARTS` (given in your assignment). It sets the running head, the
  colour chip and the thumb tab.
- Photographs: `name = b.asset("yourchapter-what-it-shows.jpg", "repo/path/to/photo.jpg", revision_or_None)` then
  `b.fig(name, alt, "17 OCTOBER 2026 · MARK2 · PET-GF", "What the picture shows.", h=700, pos="50% 40%", zoom=150)`.
  Open the photograph with the Read tool first and choose the crop on purpose. Start asset names with your chapter name.
- Drawings: compose `svgkit` pieces inside `k.svg(width, height, body, title, desc)`. Use only the four colours:
  slate for plastic already printed, orange for the course being laid or anything hot and soft, blue hatch for
  what is printed to be thrown away, dashed red for what was cut away. Everything must stay inside the viewBox.
  Give every drawing a real title and description; agents read those.
- Model pictures: `b.render("yourchapter-name.png", {...})` draws a part with `hsm-render` (sections, clips,
  ghosts, colours). `hsm where <name>` and `hsm features <part>` (run from the repo root) give bounds and named
  features; `proj.projector(cam, target, span, size)` turns a model point into pixels for a callout.
  `node tools/find-part.mjs "words"` finds a part's name and its link on the live 3D model.
- Do not write `{{` anywhere except through `b.setting()`.

## Build and check

From this folder:

```
python3 build.py preview <name>
```

It writes `preview/<name>/out/small/NN-<slug>.png` and reports anything that overflows the page, is clipped, or
runs into the footer. Open the PNGs with the Read tool. Repeat until the report says `no overflow or clipping`
and every page looks right. The build queues behind other runs on this Mac; a preview can take a minute or two.

## Rules

- Write only your own chapter file. Pictures arrive through `b.asset()` and `b.render()`. Do not edit
  `bookkit.py`, `svgkit.py`, `build.py`, `style.css`, `_mine.py` or anyone else's chapter. If you need something
  the kit lacks, define it in your own file and say so in your report.
- Change nothing in the repository outside this folder. No commits, no pushes, no printer commands
  (`hsm-printer` is off limits, even for status), no builds other than `build.py`.
- This Mac's shell: `grep` and `find` are wrappers, so use `git grep`, `/usr/bin/grep`, `/usr/bin/find`. zsh
  errors on an unmatched glob. There is no `timeout`. Run `git` and `hsm` from the repo root.
- Photographs are large. Open only the ones you are choosing between.

## What to send back

A short plain-text report, no preamble:

1. The pages you wrote: slug and one line each.
2. Anything in `dig/` or in Codex's earlier guide (`reference/codex-guide-README.md`) that the record contradicts.
3. Claims you wanted to make and could not verify, and so left out.
4. Where you marked something still open, and why.
5. Anything Derek should be asked.
