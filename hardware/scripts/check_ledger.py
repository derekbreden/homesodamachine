#!/usr/bin/env python3
"""check_ledger.py — drift guard between the assembly instructions and the ledger.

The ledger says what a build actually buys: `bom.md` is the per-unit bill of
materials, `tools.md` is the durable bench tooling. The assembly procedures and
the printed card deck are DERIVED views — they name parts in prose, and prose
does not follow a part when the ledger drops it.

`purchases.md` and `inventory.md` are HISTORY, not authority. Something bought
once and later designed out stays in purchases.md forever. So a part that an
instruction names, that lives only in purchases.md, is the exact shape of a
decision the ledger already moved past and the instruction never heard about.

Hand-run, like check_pinmap.py. Nothing in the build or the deck calls it:

    tools/cad-venv/bin/python hardware/scripts/check_ledger.py

Checks:

  A. ASIN BACKING — every Amazon ASIN cited in a procedure or card resolves to a
     line in bom.md or tools.md.
  B. PURCHASED-BRAND DRIFT — every brand the ledger knows as a real product, that
     an instruction names, is still carried by bom.md or tools.md. This is the
     self-maintaining half: a brand enters the vocabulary by being bought, so a
     part designed out of the BOM but left in the prose surfaces here.
  C. UNDRIVEN PROCEDURE — every hardware/assembly/*.md has a doc-sync driver.
     A doc with no driver has no token substitution at all, so every number and
     every part name in it is a bare literal nothing can check.

  D. GENERIC MATERIAL — a part an instruction names by what it IS rather than by
     who made it. Checks A and B are both brand-shaped: A needs an ASIN, B needs
     a capitalised name somebody once bought. "Fork terminal", "heat-shrink",
     "RTV" and "VHB 4941" are none of those — they are lowercase nouns, so the
     brand harvester never sees them and "Terminal" is in NOT_A_BRAND besides.
     A build can be missing one of these entirely and every other check passes.
     The vocabulary here is hand-kept, because that is the point: it is the list
     of things the deck asks for by description.

  E. SECTION CITATION — an instruction that cites `bom.md §N` for a named ASIN
     must cite the section that ASIN is actually in. Sections get renumbered and
     rows move between them; the prose citation does not follow.

Exit 1 on drift, 0 when clean.
"""

import html
import re
import sys
from pathlib import Path

REPO = next(p for p in Path(__file__).resolve().parents if (p / "hardware").is_dir())
LEDGER = REPO / "hardware" / "ledger"
ASSEMBLY = REPO / "hardware" / "assembly"

BOM = (LEDGER / "bom.md").read_text()
TOOLS = (LEDGER / "tools.md").read_text()
PURCHASES = (LEDGER / "purchases.md").read_text()
INVENTORY = (LEDGER / "inventory.md").read_text()

CARRIED = (BOM + TOOLS).lower()          # what a build may actually draw on
HISTORY = PURCHASES + INVENTORY          # what was bought at some point

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


# ── Corpus: the instructions a builder reads ──────────────────────────────

def detag(s: str) -> str:
    s = re.sub(r"<(style|script).*?</\1>", " ", s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


CORPUS: dict[str, str] = {}
for path in sorted(ASSEMBLY.glob("*.md")):
    CORPUS[str(path.relative_to(REPO))] = path.read_text()
for path in sorted((ASSEMBLY / "cards").glob("*.html")):
    CORPUS[str(path.relative_to(REPO))] = detag(path.read_text())


def cite(token: str, limit: int = 3) -> str:
    """Where an instruction names this token."""
    where = []
    for name, text in CORPUS.items():
        for i, line in enumerate(text.splitlines(), 1):
            if token.lower() in line.lower():
                where.append(f"{name}:{i}")
                break
    extra = f" +{len(where) - limit} more" if len(where) > limit else ""
    return ", ".join(where[:limit]) + extra


# ── A. ASIN backing ───────────────────────────────────────────────────────

ASIN = re.compile(r"\bB0[A-Z0-9]{8}\b")

# ASINs an instruction may cite without the ledger carrying them: parts the
# procedure names only to rule out, or a documented donor alternative.
ASIN_WAIVED = {
    "B0F42MT8JX": "refrigerant-loop.md donor table — the generic alternative to "
                  "the costed Frigidaire EFIC117-SS, listed as 'both verified topology'",
}

for token in sorted({m for text in CORPUS.values() for m in ASIN.findall(text)}):
    if token in ASIN_WAIVED or token.lower() in CARRIED:
        continue
    fail(f"ASIN cited by an instruction, carried by neither bom.md nor tools.md: "
         f"{token} ({cite(token)})")


# ── B. Purchased-brand drift ──────────────────────────────────────────────

# A brand token: an internal capital (KWANGIL, SunTop, BNTECHGO, CQRobot, GEARit)
# or a plain capitalised word. Harvested from the ledger's product-name cells
# only — so the vocabulary is the set of things somebody actually bought, not
# every capitalised word in English.
BRANDISH = re.compile(r"\b[A-Z][A-Za-z]*[A-Z][A-Za-z0-9]*\b|\b[A-Z][a-z]{3,}\b")

# Ledger bookkeeping words and generic nouns that ride along in a product-name
# cell. Not brands; nothing to carry.
NOT_A_BRAND = {
    "Order", "Placed", "Delivered", "Arriving", "Ordered", "Acquired", "Pack",
    "Piece", "Pieces", "Pair", "Kit", "Kits", "Spool", "Roll", "Box", "Bag",
    "Black", "White", "Green", "Blue", "Clear", "Gray", "Grey", "Maroon", "Red",
    "Transparent", "Silicone", "Stainless", "Brass", "Copper", "Steel", "Rubber",
    "Nylon", "Plastic", "Wire", "Cable", "Tube", "Tubing", "Hose", "Sleeve",
    "Valve", "Pump", "Sensor", "Module", "Board", "Relay", "Screw", "Screws",
    "Insert", "Inserts", "Washer", "Terminal", "Terminals", "Connector", "Union",
    "Adapter", "Fitting", "Elbow", "Male", "Female", "Nipple", "Gauge", "Filter",
    "Foam", "Tape", "Wipes", "Cutter", "Wrench", "Pliers", "Stripper", "Crimper",
    "Driver", "Blade", "Rod", "Plate", "Panel", "Shell", "Cord", "Inline",
    "General", "Purpose", "Hand", "Pads", "Expandable", "Braided", "Insulated",
    "Flexible", "High", "Matte", "Food", "Contact", "Compliant", "Portable",
    "Single", "Double", "Round", "Flat", "Long", "Short", "Small", "Large",
    "Water", "Cold", "Hot", "Self", "Adjusting", "Swivel", "Parallel", "Smooth",
    "Level", "Sets", "Colors", "Color", "Conductor", "Solid", "Tinned",
    "Unshielded", "Reinforced", "Assorted", "Complete", "Replacement", "Spare",
    # Names that are not a part anyone stocks: cable/thread spec designators,
    # shipping carriers, phone OSes, and ledger status words.
    "UL2464", "FNPT", "FedEx", "Android", "International", "Generic",
    "Status", "Zero",
}

brands: set[str] = set()
for line in HISTORY.splitlines():
    if not line.startswith("|"):
        continue
    cells = line.split("|")
    if len(cells) < 2:
        continue
    name = re.sub(r"\[|\]|~~", "", cells[1])
    name = re.split(r"\.\s*Order|\bOrder #", name)[0]      # drop the order suffix
    for token in BRANDISH.findall(name):
        if token not in NOT_A_BRAND and len(token) >= 4:
            brands.add(token)

# Brands an instruction may name without a bom/tools line.
BRAND_WAIVED = {
    "Frigidaire": "donor-alternative table in refrigerant-loop.md; the costed "
                  "donor is the same Frigidaire EFIC117-SS row in bom.md §5",
    "SUD8358": "refrigerant-loop.md names the Supco drier as an explicit "
               "spare/contingency — the factory drier stays in service",
    "Diet": "flavor concentrate is user-supplied, per bom.md "
            "'External / user-supplied (not shipped)'",
    "Mountain": "flavor concentrate is user-supplied, per bom.md "
                "'External / user-supplied (not shipped)'",
}

corpus_text = "\n".join(CORPUS.values())
corpus_words = set(re.findall(r"[A-Za-z][A-Za-z0-9-]*", corpus_text))

drifted = []
for brand in sorted(brands):
    if brand in BRAND_WAIVED or brand not in corpus_words:
        continue
    if brand.lower() in CARRIED:
        continue
    drifted.append(brand)

for brand in drifted:
    fail(f"instruction names a purchased brand the ledger no longer carries: "
         f"{brand} ({cite(brand)})")


# ── C. Undriven procedure ─────────────────────────────────────────────────

for doc in sorted(ASSEMBLY.glob("*.md")):
    driver = ASSEMBLY / f"_{doc.stem.replace('-', '_')}_sync.py"
    if not driver.exists():
        fail(f"procedure with no doc-sync driver — every number and part name in "
             f"it is a bare literal: {doc.relative_to(REPO)} (expected "
             f"{driver.relative_to(REPO)})")


# ── D. Generic material ───────────────────────────────────────────────────

# Materials the deck asks for by description, not by brand. Each entry is
# (what the instructions call it, what the ledger must show). A build consumes
# every one of these; none of them carries an ASIN in the prose that names it.
GENERIC = [
    (r"fork terminal|crimp fork|forks at the|ring or fork", "fork"),
    (r"heat-shrink", "heat-shrink"),
    (r"\bRTV\b", "rtv"),
    (r"VHB", "vhb"),
    (r"slip coupling", "slip coupling"),
    (r"spiral wrap", "spiral wrap"),
    (r"braided sleeve|PET braid", "braided sleeve"),
    (r"bootlace ferrule|ferrules? (?:at|into|under)", "ferrule"),
    (r"zip[- ]tie", "zip tie"),
]

# Matched against the PART-NAME cell of each ledger row, not the whole file:
# a tool's prose can mention a material it does not stock ("heat-shrink
# activation" in the heat gun's notes), and that must not read as carrying it.
CARRIED_NAMES = "\n".join(
    line.split("|")[1].lower()
    for line in (BOM + TOOLS).splitlines()
    if line.startswith("|") and len(line.split("|")) > 2
)

for pattern, needle in GENERIC:
    rx = re.compile(pattern, re.I)
    named = [f"{name}:{i}"
             for name, text in CORPUS.items()
             for i, line in enumerate(text.splitlines(), 1) if rx.search(line)]
    if named and needle not in CARRIED_NAMES:
        fail(f"instructions name a generic material no ledger row carries: "
             f"{needle!r} ({', '.join(named[:3])}"
             f"{f' +{len(named) - 3} more' if len(named) > 3 else ''})")


# ── E. Section citation ───────────────────────────────────────────────────

# bom.md's own section spans, so an ASIN can be located by section number.
BOM_SECTIONS: dict[int, str] = {}
_current = None
for line in BOM.splitlines():
    m = re.match(r"##\s+(\d+)\.", line)
    if m:
        _current = int(m.group(1))
        BOM_SECTIONS[_current] = ""
    elif _current is not None:
        BOM_SECTIONS[_current] += line + "\n"

# "…B08VS8D4WC… bom.md §5" / "bom.md §5 …B08VS8D4WC…" — an ASIN and a section
# citation close enough together in one line to be a claim about each other.
CITE = re.compile(r"bom\.md[^§\n]{0,80}§\s*(\d+)")

for name, text in CORPUS.items():
    for i, line in enumerate(text.splitlines(), 1):
        cited = {int(n) for n in CITE.findall(line)}
        if not cited:
            continue
        for asin in set(ASIN.findall(line)):
            if asin in ASIN_WAIVED:
                continue
            actual = sorted(n for n, body in BOM_SECTIONS.items() if asin in body)
            if not actual or cited & set(actual):
                continue
            fail(f"instruction cites the wrong bom.md section for {asin}: "
                 f"says §{'/§'.join(str(n) for n in sorted(cited))}, "
                 f"the row is in §{'/§'.join(str(n) for n in actual)} ({name}:{i})")


# ── Report ────────────────────────────────────────────────────────────────

_card_files = list((ASSEMBLY / "cards").glob("*.html"))
print(f"instructions: {len(CORPUS)} files "
      f"({len(list(ASSEMBLY.glob('*.md')))} procedures + "
      f"{sum(1 for p in _card_files if p.stem != '00-cover')} cards + cover) | "
      f"ledger brands: {len(brands)} | waived: "
      f"{len(ASIN_WAIVED)} ASIN + {len(BRAND_WAIVED)} brand")
for note in notes:
    print(f"  note: {note}")

if failures:
    print(f"\nDRIFT: {len(failures)} instruction(s) out of step with the ledger:")
    for f in failures:
        print(f"  ✗ {f}")
    sys.exit(1)

print("\n✓ every part the instructions name is carried by bom.md or tools.md, "
      "and every procedure has a driver.")
