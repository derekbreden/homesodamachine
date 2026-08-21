"""Build the owner's manual: render every page to a vector PDF at 5.5 x 8.5 in
via tools/render/render-card.js, then write four files beside the pages.

    manual.pdf         one book page per PDF page, in reading order
    manual-print.pdf   the same pages as letter sheets, four book pages to a
                       sheet, two a side, in the order a duplex stack folded
                       down the middle reads 1, 2, 3 …
    manual.cover.png   page one, at 640 px
    manual.pdf.json    title, subtitle, page count, cover
                       (web/contracts/documents.js)

Underscore-prefixed so the dev-server watcher never runs it.

    tools/cad-venv/bin/python hardware/manual/_build.py
"""

import io
import json
import os
import subprocess
import sys
from pathlib import Path

# Browser + PDF work, below the CAD build lock (_run_lock.py).
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

MANUAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in MANUAL_DIR.parents if (p / "tools" / "render").is_dir())
HARDWARE = next(p for p in MANUAL_DIR.parents if p.name == "hardware")
OUT_DIR = MANUAL_DIR / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf, note_read, note_write  # noqa: E402

TITLE = "Owner's manual"

#: The page, in points. 5.5 x 8.5 in — a letter sheet folded once, which is what
#: makes the fold the spine and every other edge the sheet's own bled edge.
PAGE_W, PAGE_H = 5.5 * 72, 8.5 * 72
#: The sheet the pages are imposed on: letter, landscape, two pages across.
SHEET_W, SHEET_H = 11 * 72, 8.5 * 72
#: The canvas a page is authored against: 5.5 x 8.5 in at 300 dpi.
CANVAS_W, CANVAS_H = 1650, 2550
COVER_W = 640


def pages() -> list:
    """Every authored page, in reading order — the filename's leading number."""
    return sorted(MANUAL_DIR.glob("*.html"), key=lambda p: p.name)


#: WHAT THE BROWSER OPENS FROM OUTSIDE THIS DIRECTORY. A page's own `<img>` and
#: `@font-face` are read below Python, where no audit hook reaches, so the run
#: that starts the browser is the one place that names them.
#:
#: The pictures are the enclosure's line art, cut by Blender's Freestyle from the
#: built appliance. The faces are the ones the bench deck vendored — one copy in
#: this repo, in that directory.
LINE_ART = tuple(
    HARDWARE / "printed-parts" / "enclosure" / "drawings" / "line-art" / f
    for f in ("enclosure-iso-front.svg", "enclosure-iso-back.svg")
)
FONTS = tuple((HARDWARE / "assembly" / "cards" / "fonts").glob("*.woff2"))


def render_pages() -> int:
    """The renderer's exit status. A page that overflows and a page the browser
    could not draw both come back non-zero, and the book is bound from whatever
    rendered either way — `__main__` below is where the status lands."""
    renderer = REPO_ROOT / "tools" / "render" / "render-card.js"
    note_read(renderer)
    for f in LINE_ART + FONTS:
        note_read(f)
    for page in pages():
        note_write(OUT_DIR / f"{page.stem}.png")
        note_write(OUT_DIR / f"{page.stem}.pdf")
    r = subprocess.run(
        [
            "node", str(renderer), "--batch", str(MANUAL_DIR), str(OUT_DIR),
            "--size", f"{CANVAS_W}x{CANVAS_H}",
            "--dpr", "1.2",
            "--pdf", "5.5x8.5in",
        ],
        check=False,
    )
    return r.returncode


def imposition(n: int) -> list:
    """Sheet sides, front and back alternating, each `(left, right)` in
    ONE-BASED page numbers — the order a saddle-stitched booklet folds into.

    Fold a stack of sheets in half: the outermost sheet carries the first page
    and the last, the next carries the second and the second-to-last. Sheet i's
    front is `(n - 2i, 1 + 2i)` and its back is `(2 + 2i, n - 1 - 2i)`. `n` is
    rounded up to a multiple of four."""
    sheets = []
    for i in range(n // 4):
        sheets.append((n - 2 * i, 1 + 2 * i))
        sheets.append((2 + 2 * i, n - 1 - 2 * i))
    return sheets


def bind() -> int:
    """The number of authored pages with no render — leaves the book is short."""
    from pypdf import PdfWriter, PageObject
    from pypdf.generic import RectangleObject
    from pypdf import Transformation

    authored = [p.stem for p in pages()]
    rendered = {p.stem for p in OUT_DIR.glob("*.pdf")}

    for stem in sorted(rendered - set(authored)):
        print(f"orphan render (no {stem}.html): {OUT_DIR / (stem + '.pdf')}")
    missing = [s for s in authored if s not in rendered]
    for stem in missing:
        print(f"MISSING LEAF (no render for {stem}.html): {OUT_DIR / (stem + '.pdf')}")

    order = [s for s in authored if s in rendered]
    if not order:
        sys.exit("no rendered pages in out/")

    # Skia stamps its own `/CreationDate` into every `page.pdf`. The append
    # leaves each source document's `/Info` behind, so what the book carries is
    # the four keys pinned below and a rebuild over unmoved pages lands on the
    # same bytes.
    def read_order(out_path):
        w = PdfWriter()
        for stem in order:
            w.append(str(OUT_DIR / f"{stem}.pdf"))
        # One copy of the font subsets and the shared resources, not one per
        # appended page.
        w.compress_identical_objects()
        w.add_metadata({"/Title": TITLE, "/Author": "", "/Producer": "", "/Creator": ""})
        with open(out_path, "wb") as fh:
            w.write(fh)

    export_pdf(read_order, str(MANUAL_DIR / "manual.pdf"))

    # A page number past the last leaf is not drawn, and its half of the sheet
    # comes off the printer blank.
    def imposed(out_path):
        from pypdf import PdfReader

        leaves = [PdfReader(str(OUT_DIR / f"{stem}.pdf")).pages[0] for stem in order]
        padded = len(leaves) + (-len(leaves)) % 4
        w = PdfWriter()
        for left, right in imposition(padded):
            sheet = PageObject.create_blank_page(width=SHEET_W, height=SHEET_H)
            for n, x in ((left, 0), (right, PAGE_W)):
                if n <= len(leaves):
                    sheet.merge_transformed_page(
                        leaves[n - 1], Transformation().translate(x, 0)
                    )
            sheet.mediabox = RectangleObject((0, 0, SHEET_W, SHEET_H))
            w.add_page(sheet)
        w.compress_identical_objects()
        w.add_metadata({"/Title": f"{TITLE} — imposed for printing",
                        "/Author": "", "/Producer": "", "/Creator": ""})
        with open(out_path, "wb") as fh:
            w.write(fh)

    export_pdf(imposed, str(MANUAL_DIR / "manual-print.pdf"))

    write_cover(OUT_DIR / f"{order[0]}.png")
    sidecar = {
        "title": TITLE,
        "subtitle": f"{len(order)} pages · 5.5 × 8.5 in booklet, "
                    f"{len(order) // 4 + (1 if len(order) % 4 else 0)} letter sheets folded",
        "pages": len(order),
        "cover": "manual.cover.png",
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n"
    sc = MANUAL_DIR / "manual.pdf.json"
    if not sc.exists() or sc.read_text() != text:
        sc.write_text(text)
    else:
        note_write(sc)

    print(f"-> {MANUAL_DIR / 'manual.pdf'} ({len(order)} pages, "
          f"{(MANUAL_DIR / 'manual.pdf').stat().st_size // 1024} KB)")
    print(f"-> {MANUAL_DIR / 'manual-print.pdf'} "
          f"({len(imposition(len(order) + (-len(order)) % 4))} sheet sides, "
          f"letter landscape, duplex)")
    return len(missing)


def write_cover(cover_png: Path) -> None:
    """Page one at 640 px, which is what the site puts in the documents shelf.
    Pillow's PNG encoder is deterministic over the same pixels."""
    from PIL import Image

    if not cover_png.exists():
        print(f"NO COVER (no render for {cover_png.stem}.html): cover left as it stands")
        return
    with Image.open(cover_png) as im:
        thumb = im.convert("RGB").resize((COVER_W, COVER_W * CANVAS_H // CANVAS_W), Image.LANCZOS)
        buf = io.BytesIO()
        thumb.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    target = MANUAL_DIR / "manual.cover.png"
    if target.exists() and target.read_bytes() == data:
        note_write(target)
        return
    target.write_bytes(data)


if __name__ == "__main__":
    rc = render_pages()
    missing = bind()
    if rc or missing:
        sys.exit(f"manual bound with {missing} missing leaf/leaves; "
                 f"render-card exited {rc} — see the flags above")
