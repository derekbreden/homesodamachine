"""The card deck's docgen: a marker a card can carry, and the gate that holds it
to the machine.

`tools/docgen` writes `[value](NAME)` into markdown, where the brackets hold what
renders and the parens hold the name of the script variable that owns it. A card
is HTML printed full-bleed on gloss, so that marker would print literally — the
bench would read "[15](EAST_BOSSES)" off the page. The name moves into an
attribute instead, and the element's own text is the value:

    <span class="dim" data-gen="EAST_BOSSES">15</span>
    <td class="v" data-gen="BOX_SIZE">223 &#215; 481 &#215; 358 mm</td>

The attribute never draws; the value does. The name is literally in the source
for any reader to see, and — exactly as in docgen — the value in the file is
never authoritative. `_cards_sync.py`'s variable is.

A MARKED ELEMENT HOLDS TEXT AND NOTHING ELSE. `<span data-gen="X">a <b>b</b></span>`
has no single value to rewrite, so it is not substituted — it is a build failure,
caught by counting `data-gen` attributes against substitutable elements. HTML
entities are text and pass through: a value is compared and written as the card's
own source spells it, `&#215;` and all.

What the gate holds
-------------------

`sync()` takes the derived facts and a registry of which card carries which, and
checks all of it at once, reporting every disagreement rather than the first:

- a marker naming a fact nobody derives          → the card invents a number
- a marked card with no registry entry           → markers added without registering
- a registered card missing a name it registered → the figure was deleted from the page
- a card carrying a name it did not register     → the registry no longer describes the card
- a derived fact no registered card carries      → THE GATE OVERSTATING ITS OWN READING.
  A checker that passes because it only looked at half the deck is worse than no
  checker, so a fact that reaches no card fails the run instead of sitting there
  looking like coverage.
- a registered card whose `.src` footer does not name this driver → the bench
  cannot see what keeps the card honest. docgen's `## Sources` block, in the one
  slot a card has for it.

Then, per marker, the card's text against the machine's value. `--check` reports
and exits 2; the default rewrites the card.

Last, `sync_titles` holds `README.md`'s deck table to the titles those same cards
print — a row is written from its card, never typed beside it — and reports a card
with no row and a row with no card.
"""

import re
import sys
from pathlib import Path

# ── the deck's own order ───────────────────────────────────────────────────
#: Deck order = the build order of /hardware/README.md "Build order" — the procedure docs'
#: own dependency chain, not their filename order. The three bench subsystems (ca, eb, fu)
#: feed en; ip needs the chassis en closes up; wr needs the lines ip lays in.
#:
#: IT LIVES HERE BECAUSE THREE THINGS READ IT AND THEY MUST AGREE. `_build.py` sorts the
#: bound pages by it, the cover's contents table is printed in it, and `README.md`'s deck
#: tables are written in it. A bench finds a deck by reading the cover, so a table in any
#: other order sends a hand to the wrong place — with the counts beside it still right,
#: which is exactly what makes a wrong table convincing.
SUBSYSTEM_ORDER = ["pv", "cc", "rl", "ca", "eb", "fu", "en", "ip", "wr", "fc", "ab", "fs",
                   "sa", "gt"]

#: The page the deck opens on, which is not one of the operations it tables.
COVER = "00-cover"

# One marked element. `attrs` and `value` admit no angle bracket, so an element
# with a child cannot match — which is how the text-only rule is enforced rather
# than assumed. The closing tag is a backreference, so nesting cannot be
# mistaken for a match.
#: Every card a run was handed, whether or not its text moved. A card is READ AND WRITTEN
#: BACK — its prose is authored and only the marked values are this driver's — so it belongs
#: on both sides of its own action, the way a doc does. `docgen._WRITE_TARGETS` is the same
#: record for the same reason; `tools/bazel/trace_inputs.py` takes both.
_WRITE_TARGETS = set()


def _note_target(path) -> None:
    """Keep `path` as one this run rewrites in place, named from the repo root."""
    p = Path(path).resolve()
    for up in (p, *p.parents):
        if (up / ".git").exists():
            _WRITE_TARGETS.add(p.relative_to(up).as_posix())
            return


MARKER = re.compile(
    r"<(?P<tag>[a-z][a-z0-9]*)(?P<attrs>[^<>]*?\sdata-gen=\"(?P<name>[A-Z_][A-Z0-9_]*)\"[^<>]*)>"
    r"(?P<value>[^<>]*)</(?P=tag)>"
)
# Every declaration, matched or not — the count that catches the unmatchable ones.
DECL = re.compile(r"data-gen=\"([A-Z_][A-Z0-9_]*)\"")

# The generator credit a registered card owes its reader, in the footer STYLE.md
# gives to "source doc §, generator files, rev date".
DRIVER = "_cards_sync.py"


def markers(text: str) -> list:
    """Every substitutable marker in a card: `(name, value, start, end)` of the value."""
    return [(m.group("name"), m.group("value"), m.start("value"), m.end("value"))
            for m in MARKER.finditer(text)]


def _unmatchable(text: str) -> list:
    """Names declared by an attribute that no substitutable element carries.

    A declaration outnumbering its element means the element holds more than text.
    Names are compared as multisets so a card can carry one name twice."""
    declared, matched = DECL.findall(text), [n for n, _v, _s, _e in markers(text)]
    for name in matched:
        declared.remove(name)
    return declared


def _rewritten(text: str, variables: dict) -> str:
    """The card with every marker's value replaced by the derived one."""
    out, end = [], 0
    for name, _value, start, stop in markers(text):
        out.append(text[end:start])
        out.append(str(variables[name]))
        end = stop
    out.append(text[end:])
    return "".join(out)


#: One row of the deck table in `README.md`: `| PV-03 | Drill the rod register — both plates |`.
TABLE_ROW = re.compile(r"^\|\s*(?P<code>[A-Z]{2}-\d{2})\s*\|\s*(?P<title>.*?)\s*\|\s*$", re.M)

#: The entities a card spells its title with, and the character each prints as. The README is
#: read by a person in a text editor, so it carries the character; the card is read by a
#: browser at 300 dpi, so it carries the entity. One title, two spellings, and this is the
#: whole of the difference between them.
_ENTITIES = {
    "&#8212;": "—", "&mdash;": "—", "&#8211;": "–", "&ndash;": "–",
    "&#8217;": "’", "&rsquo;": "’", "&#8722;": "−",
    "&Prime;": "″", "&#8243;": "″", "&#215;": "×", "&times;": "×",
    "&#8960;": "⌀", "&amp;": "&", "&nbsp;": " ", "&#160;": " ",
}


def title_of(text: str, variables: dict) -> str:
    """A card's `h1` as it prints: markers resolved, `<br>` a space, entities characters.

    This is the reading the README's deck table is written from, so the row a reader scans
    and the title a bench reads off the printed card are one string and cannot part."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.S)
    if not h1:
        return ""
    body = _rewritten(h1.group(1), variables) if variables else h1.group(1)
    body = re.sub(r"<br\s*/?>", " ", body)
    body = re.sub(r"<[^>]+>", "", body)
    for entity, char in _ENTITIES.items():
        body = body.replace(entity, char)
    return re.sub(r"\s+", " ", body).strip()


def sync_titles(cards_dir: Path, readme: Path, variables: dict, check: bool = False) -> list:
    """Hold `README.md`'s deck table to the titles the cards print; return the faults.

    A ROW IS WRITTEN FROM ITS CARD, for the same reason a figure is written from the
    machine: the reading a reader trusts has to be the one the thing itself gives. Typed
    beside the card instead, a row is free to drift from it, and a title carrying a derived
    count drifts the moment the machine moves — the table would go on naming a figure the
    card no longer prints, with nothing to say so."""
    faults = []
    text = readme.read_text()
    titles = {}
    for path in sorted(cards_dir.glob("*.html")):
        if path.stem == COVER:
            continue
        code = f"{path.stem[:2].upper()}-{path.stem[3:5]}"
        titles[code] = title_of(path.read_text(), variables)

    tabled = {m.group("code"): m.group("title") for m in TABLE_ROW.finditer(text)}
    for code in sorted(set(titles) - set(tabled)):
        faults.append(f"README.md: {code} is a card and has no row in the deck table — "
                      f"add it to that subsystem's section, title and all")
    for code in sorted(set(tabled) - set(titles)):
        faults.append(f"README.md: the deck table rows {code} and no such card is authored")

    drift = {c: t for c, t in titles.items() if c in tabled and tabled[c] != t}
    if check:
        faults += [f"README.md: {c} — table says {tabled[c]!r}, card prints {t!r}"
                   for c, t in sorted(drift.items())]
    elif drift:
        def row(m):
            code = m.group("code")
            return f"| {code} | {titles[code]} |" if code in drift else m.group(0)
        readme.write_text(TABLE_ROW.sub(row, text))
        _note_target(readme)
        print(f"   README.md deck table: {', '.join(sorted(drift))}")
    elif titles:
        _note_target(readme)
    return faults


def sync(cards_dir: Path, variables: dict, registry: dict, check: bool = False) -> int:
    """Hold every card in `cards_dir` to `variables`; return a process exit code.

    `registry` is {card stem: {NAME, ...}} — the facts that card is declared to
    carry. A card with no marker needs no entry; a card with one needs an exact
    one. `check` reports drift instead of writing it away."""
    faults, written = [], []

    cards = {p.stem: p for p in sorted(cards_dir.glob("*.html"))}
    for stem in sorted(set(registry) - set(cards)):
        faults.append(f"{stem}: registered, but no such card")

    used = set()
    for stem, path in cards.items():
        text = path.read_text()
        found = markers(text)
        for name in _unmatchable(text):
            faults.append(
                f"{stem}: data-gen=\"{name}\" is on an element that holds more than text — "
                f"a marked element's whole content is its value, so wrap the value alone")
        if not found and stem not in registry:
            continue
        carried = {n for n, _v, _s, _e in found}
        used |= carried

        unknown = sorted(carried - set(variables))
        if unknown:
            faults.append(f"{stem}: no derived fact named {', '.join(unknown)}")
        if stem not in registry:
            faults.append(
                f"{stem}: carries {', '.join(sorted(carried))} but is not in `CARDS` — "
                f"register it so a figure cannot go missing unnoticed")
            continue

        declared = registry[stem]
        for name in sorted(declared - carried):
            faults.append(f"{stem}: registered for {name} and does not carry it")
        for name in sorted(carried - declared - set(unknown)):
            faults.append(f"{stem}: carries {name} and is not registered for it")
        if DRIVER not in text:
            faults.append(f"{stem}: its .src footer does not name `{DRIVER}`")

        # A CARD THIS RUN MAINTAINS, whether or not this run moved it. Recording it where the
        # write happens records the cards that drifted on one particular run — one of the
        # registered ones, on the run that traced this — and a card left out is a card the
        # action may rewrite and never hand back.
        _note_target(path)

        drift = [(n, v) for n, v, _s, _e in found
                 if n in variables and v != str(variables[n])]
        if check:
            faults += [f"{stem}: {n} — card says {v!r}, machine says {str(variables[n])!r}"
                       for n, v in drift]
        elif drift:
            path.write_text(_rewritten(text, variables))
            written.append((stem, [n for n, _v in drift]))

    for name in sorted(set(variables) - used):
        faults.append(
            f"{name}: derived and on no card — either a card states it or this driver "
            f"stops deriving it. A fact nobody carries is coverage the gate does not have")

    # The deck table, held to the same cards by the same run. It is last because it reads the
    # resolved titles, and a card whose markers are wrong has a title that is wrong with them.
    faults += sync_titles(cards_dir, cards_dir / "README.md", variables, check=check)

    if faults:
        print(f"cards out of step with the machine ({len(faults)}):", file=sys.stderr)
        for f in faults:
            print(f"  {f}", file=sys.stderr)
        return 2

    for stem, names in written:
        print(f"   {stem}: {', '.join(sorted(names))}")
    verb = "checked" if check else "in step"
    print(f"cards ✓ {len(registry)} {verb} against {len(variables)} derived facts"
          + (f" — {len(written)} rewritten" if written else ""))
    return 0
