"""Build the printable card deck: hold every card to the machine, render every
card HTML to out/<name>.png at 2160x1440 (6x4 in at 360 dpi) and to a vector
out/<name>.pdf at the same 6x4 in, via tools/render/render-card.js, then
assemble deck.pdf with one page per card in deck order.

TWO ARTIFACTS OFF ONE LAYOUT. The PNG is a pixel grid, and it is what goes to
the printer one card at a time on 4x6 gloss. The PDF is the same page printed
rather than captured — type stays type — so the whole deck is one file a person
can read on a screen, hand to a printer, or download off the site, at a
fifteenth the bytes the same pages cost as pixels. That is what makes it a file
git carries and out/ does not: deck.pdf sits beside the cards, and the site
serves it (web/contracts/documents.js).

The deck is a thing a bench holds while it builds an appliance, so it is gated
before it is printed: `_cards_sync.py --check` builds the appliance and reads
every `data-gen` figure on every card against it. A card that disagrees stops
the build here rather than coming off the printer wrong. That costs about a
minute of CAD before any card renders.

Underscore-prefixed so the dev-server watcher never runs it.

    tools/cad-venv/bin/python hardware/assembly/cards/_build.py
"""

import io
import json
import os
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
#: The deck as one file, committed beside the cards it is made of, and the
#: picture of its first page the site shows to open it.
DECK_PDF = CARDS_DIR / "deck.pdf"
DECK_COVER = CARDS_DIR / "deck.cover.png"
DECK_SIDECAR = CARDS_DIR / "deck.pdf.json"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf, note_read, note_write  # noqa: E402

# Deck order = the build order of /hardware/README.md "Build order" — which is the
# procedure docs' own dependency chain, not their filename order. The three bench
# subsystems (ca, es, fu) feed en; ip needs the chassis en closes up; wr needs the
# lines ip lays in.
SUBSYSTEM_ORDER = ["pv", "cc", "rl", "ca", "pc", "fu", "en", "ip", "wr", "fc", "ab", "fs",
                   "sa", "gt"]

PAGE_W, PAGE_H = 6 * 72, 4 * 72  # points

#: What the deck is called wherever it is listed, and how wide its cover is drawn
#: for a grid that has to fit more than one document across.
DECK_TITLE = "Assembly card deck"
COVER_W = 900
IMAGE_QUALITY = 92
IMAGE_RECOMPRESS_ABOVE = 48 * 1024


def deck_key(render: Path):
    code = render.stem.split("-", 1)[0]
    if code == "00":  # the cover leads the deck
        return (-1, render.stem)
    try:
        subsystem = SUBSYSTEM_ORDER.index(code)
    except ValueError:
        subsystem = len(SUBSYSTEM_ORDER)
    return (subsystem, render.stem)



def render_cards() -> int:
    """The renderer's exit status, carried rather than raised. A card that
    overflows and a card the browser could not draw both come back non-zero,
    and both are things to look at on the printed deck — so the deck is still
    printed, from whatever rendered, and the status decides this build's own."""
    # A PAGE IS DRAWN BY NODE, below Python, and the deck beside it is not. Only the deck was
    # ever declared, so `sync_tree` carried `deck.pdf` and left a hundred and six pages of the
    # tree at whatever the last hand run wrote — a green build and a clean carry beside a page
    # showing a part that has since changed. The renderer is read whether or not this run
    # reaches it; the pages are what the run makes.
    renderer = REPO_ROOT / "tools" / "render" / "render-card.js"
    note_read(renderer)
    for stem in sorted(p.stem for p in CARDS_DIR.glob("*.html")):
        note_write(OUT_DIR / f"{stem}.png")
    for stem in sorted(p.stem for p in CARDS_DIR.glob("*.html")):
        note_write(OUT_DIR / f"{stem}.pdf")
    r = subprocess.run(
        [
            "node",
            str(renderer),
            "--batch",
            str(CARDS_DIR),
            str(OUT_DIR),
            "--dpr",
            "1.2",
            "--pdf",
            f"{PAGE_W // 72}x{PAGE_H // 72}in",
        ],
        check=False,
    )
    return r.returncode


def write_cover(cover_png: Path) -> None:
    """The deck's first page, small enough to be a picture on a web page.

    The site opens the deck by its cover, so the cover has to be a file the
    site can put in a grid — the 360 dpi print render is most of a megabyte and
    is drawn for a printer. Pillow's own PNG encoder is deterministic over the
    same pixels, so a rebuild that does not move the cover does not move this."""
    from PIL import Image

    with Image.open(cover_png) as im:
        thumb = im.convert("RGB").resize((COVER_W, COVER_W * PAGE_H // PAGE_W), Image.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    if DECK_COVER.exists() and DECK_COVER.read_bytes() == data:
        note_write(DECK_COVER)           # unmoved, and still this run's to name
        return
    DECK_COVER.write_bytes(data)


def build_pdf() -> int:
    """The number of authored cards with no render — pages the deck is short."""
    from pypdf import PdfWriter

    # The deck is the set of card HTML files, not whatever renders are lying in
    # out/ — a card deleted from the source keeps its render otherwise, and
    # prints as a page of a build that no longer exists.
    authored = {p.stem for p in CARDS_DIR.glob("*.html")}
    rendered = {p.stem for p in OUT_DIR.glob("*.pdf")}

    orphans = sorted(rendered - authored)
    for stem in orphans:
        print(f"orphan render (no {stem}.html): {OUT_DIR / (stem + '.pdf')}")

    # A card with no render is a page the deck cannot carry. It is named here,
    # loudly, and the rest of the deck still prints: a deck short one page is
    # something a bench can read and a missing page is something a bench can
    # see, where an unwritten PDF is neither.
    missing = sorted(authored - rendered)
    for stem in missing:
        print(f"MISSING PAGE (no render for {stem}.html): {OUT_DIR / (stem + '.pdf')}")

    pages = sorted((OUT_DIR / f"{s}.pdf" for s in authored - set(missing)), key=deck_key)
    if not pages:
        sys.exit("no rendered cards in out/")

    # THE DECK CARRIES NO FACT ABOUT THE RUN THAT ASSEMBLED IT, for the same
    # reason `_cadq_export` canonicalizes a STEP: a file git carries has to land
    # on the same bytes over a tree that has not moved, or every build is a diff.
    #
    # A PAGE OUT OF THE BROWSER DOES NOT HAVE THAT PROPERTY. Skia stamps its own
    # `/CreationDate` and `/ModDate` into every `page.pdf`, so two renders of one
    # unchanged card are two different files — and `_canonicalize_pdf`'s regex
    # cannot reach them the way it reaches ReportLab's, because Chrome compresses
    # the trailer this lives in. What settles it is the append: pypdf copies the
    # pages and leaves each source document's `/Info` behind, so the only document
    # information the deck carries is the four keys pinned here. Re-rendering a
    # card whose HTML has not moved lands on the same deck.
    def build(out_path):
        writer = PdfWriter()
        for page in pages:
            writer.append(str(page))
        # A card's render comes back out of the browser as a Flate RGB bitmap
        # about nine times the PNG it was drawn from. Re-encoded at 92 it costs
        # a third of that and moves no pixel by more than 3 of 255 — measured on
        # es-02, the largest. Type and rules are vector and untouched.
        for page in writer.pages:
            for img in page.images:
                if len(img.data) > IMAGE_RECOMPRESS_ABOVE:
                    img.replace(img.image, quality=IMAGE_QUALITY)
        # Every appended document brought its own copy of the font subsets and
        # the shared resources; one page of a hundred and three needs one of
        # each. Held to: the deck goes 21.5 MB -> 8.8 MB and no page moves.
        writer.compress_identical_objects()
        writer.add_metadata({"/Title": DECK_TITLE, "/Author": "", "/Producer": "", "/Creator": ""})
        with open(out_path, "wb") as fh:
            writer.write(fh)

    export_pdf(build, str(DECK_PDF))
    # The cover is the page the site opens the deck by. Its own PNG is the one
    # this reads, so a run that could not draw the cover leaves the last cover
    # standing rather than putting a card's face on the deck.
    lead = OUT_DIR / f"{pages[0].stem}.png"
    if lead.exists():
        write_cover(lead)
    else:
        print(f"NO COVER (no render for {pages[0].stem}.html): {DECK_COVER} left as it stands")
    # Pages, not cards: the cover is a page of the deck and not a bench
    # operation, so the two numbers differ by one and saying "cards" here is
    # what makes the cover's own count look wrong.
    sidecar = {
        "title": DECK_TITLE,
        "subtitle": f"{len(pages) - 1} cards + cover · 6 × 4 in, borderless gloss",
        "pages": len(pages),
        "cover": DECK_COVER.name,
        "cover_size": [COVER_W, COVER_W * PAGE_H // PAGE_W],
    }
    text = json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n"
    if not DECK_SIDECAR.exists() or DECK_SIDECAR.read_text() != text:
        DECK_SIDECAR.write_text(text)
    else:
        note_write(DECK_SIDECAR)
    print(f"-> {DECK_PDF} ({len(pages)} pages — {len(pages) - 1} cards + cover, "
          f"{DECK_PDF.stat().st_size // 1024} KB)")
    return len(missing)


def check_machine() -> None:
    """Every card's derived figures against the appliance it describes."""
    sys.path.insert(0, str(CARDS_DIR))
    import _cards_sync

    if _cards_sync.main(check=True):
        sys.exit("deck not printed — fix the cards, or the driver that derives them")


if __name__ == "__main__":
    check_machine()
    rc = render_cards()
    missing = build_pdf()
    # The deck is written either way, and the status is what says so out loud.
    if rc or missing:
        sys.exit(f"deck printed with {missing} missing page(s); "
                 f"render-card exited {rc} — see the flags above")
