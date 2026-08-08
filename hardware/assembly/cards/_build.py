"""Build the printable card deck: hold every card to the machine, render every
card HTML to out/<name>.png at 2160x1440 (6x4 in at 360 dpi) via
tools/render/render-card.js, then assemble out/deck.pdf with one 6x4-inch page
per card in deck order.

The deck is a thing a bench holds while it builds an appliance, so it is gated
before it is printed: `_cards_sync.py --check` builds the appliance and reads
every `data-gen` figure on every card against it. A card that disagrees stops
the build here rather than coming off the printer wrong. That costs about a
minute of CAD before any card renders.

Underscore-prefixed so the dev-server watcher never runs it.

    tools/cad-venv/bin/python hardware/assembly/cards/_build.py
"""

import collections
import os
import re
import subprocess
import sys
from pathlib import Path

# Card rendering is browser + reportlab work, not a CAD build — it must neither
# supersede a running generator nor be superseded by one (_run_lock.py's opt-out
# for tooling that imports a generator's helpers without meaning to build).
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

CARDS_DIR = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in CARDS_DIR.parents if (p / "tools" / "render").is_dir())
# tools/render is shared (one copy at the repo root); hardware/ is content, so
# it resolves to the nearest copy — the tree this file stands in.
HARDWARE = next(p for p in CARDS_DIR.parents if p.name == "hardware")
OUT_DIR = CARDS_DIR / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf  # noqa: E402

# Deck order = the build order of /hardware/future.md "Build order" — which is the
# procedure docs' own dependency chain, not their filename order. The three bench
# subsystems (ca, es, fu) feed en; ip needs the chassis en closes up; wr needs the
# lines ip lays in.
SUBSYSTEM_ORDER = ["pv", "cc", "rl", "ca", "es", "fu", "en", "ip", "wr", "fc", "ab", "fs", "gt"]

PAGE_W, PAGE_H = 6 * 72, 4 * 72  # points


def deck_key(png: Path):
    code = png.stem.split("-", 1)[0]
    if code == "00":  # the cover leads the deck
        return (-1, png.stem)
    try:
        subsystem = SUBSYSTEM_ORDER.index(code)
    except ValueError:
        subsystem = len(SUBSYSTEM_ORDER)
    return (subsystem, png.stem)


COVER = "00-cover"


def check_cover(authored: set[str]) -> None:
    """The cover's contents table against the cards that exist.

    The cover is the one page that describes the whole deck, and nothing
    regenerates it — so it is the page most likely to be stale, and the least
    likely to be noticed. Its per-subsystem counts are what to check, not its
    total: two subsystems drifting in opposite directions leave the total
    correct, which is exactly how a wrong table survives being looked at.
    """
    actual = collections.Counter(
        stem.split("-", 1)[0] for stem in authored if stem != COVER
    )
    cover = (CARDS_DIR / f"{COVER}.html").read_text()
    claimed = {
        code.lower(): int(n)
        for code, n in re.findall(
            r'"tcode"[^>]*>([A-Z]{2})</span>'
            r'<span class="tname">[^<]*</span>'
            r'<span class="tn">(\d+)</span>',
            cover,
        )
    }

    drift = [
        f"{code.upper()} says {claimed.get(code)}, deck has {actual[code]}"
        for code in SUBSYSTEM_ORDER
        if claimed.get(code) != actual[code]
    ]
    missing = sorted(set(actual) - set(claimed))
    if missing:
        drift.append(f"no cover row for {', '.join(c.upper() for c in missing)}")

    total = sum(actual.values())
    stated = re.search(r"<b>(\d+) cards</b>", cover)
    if not stated:
        drift.append("cover states no card total")
    elif int(stated.group(1)) != total:
        drift.append(f"cover total says {stated.group(1)}, deck has {total}")

    if drift:
        sys.exit("cover out of step with the deck:\n  " + "\n  ".join(drift))
    print(f"cover contents ✓ {total} cards across {len(actual)} subsystems")


def render_cards() -> None:
    subprocess.run(
        [
            "node",
            str(REPO_ROOT / "tools" / "render" / "render-card.js"),
            "--batch",
            str(CARDS_DIR),
            str(OUT_DIR),
            "--dpr",
            "1.2",
        ],
        check=True,
    )


def build_pdf() -> None:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as pdf_canvas

    # The deck is the set of card HTML files, not whatever PNGs are lying in
    # out/ — a card deleted from the source keeps its render otherwise, and
    # prints as a page of a build that no longer exists.
    authored = {p.stem for p in CARDS_DIR.glob("*.html")}
    rendered = {p.stem for p in OUT_DIR.glob("*.png")}

    orphans = sorted(rendered - authored)
    for stem in orphans:
        print(f"orphan render (no {stem}.html): {OUT_DIR / (stem + '.png')}")

    missing = sorted(authored - rendered)
    if missing:
        sys.exit(f"card(s) authored but not rendered: {', '.join(missing)}")

    check_cover(authored)

    pngs = sorted((OUT_DIR / f"{s}.png" for s in authored), key=deck_key)
    if not pngs:
        sys.exit("no rendered cards in out/")

    def build(out_path):
        c = pdf_canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
        for png in pngs:
            c.drawImage(ImageReader(str(png)), 0, 0, PAGE_W, PAGE_H)
            c.showPage()
        c.save()

    export_pdf(build, str(OUT_DIR / "deck.pdf"))
    # Pages, not cards: the cover is a page of the deck and not a bench
    # operation, so the two numbers differ by one and saying "cards" here is
    # what makes the cover's own count look wrong.
    print(f"-> {OUT_DIR / 'deck.pdf'} ({len(pngs)} pages — "
          f"{len(pngs) - 1} cards + cover)")


def check_machine() -> None:
    """Every card's derived figures against the appliance it describes."""
    sys.path.insert(0, str(CARDS_DIR))
    import _cards_sync

    if _cards_sync.main(check=True):
        sys.exit("deck not printed — fix the cards, or the driver that derives them")


if __name__ == "__main__":
    check_machine()
    render_cards()
    build_pdf()
