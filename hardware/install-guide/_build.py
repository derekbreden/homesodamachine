"""Build the Home Soda Machine install guide — the bound booklet that ships in the install kit.

The quick start draws the six actions; this guide carries everything they stand on. Its
pictures are the same solids, in views `hardware/quickstart/` has already cut, so a change to
the machine reaches both documents through one set of renders and neither can drift from the
other. Nothing here draws CAD of its own.

    install-guide.pdf         the bound booklet, in reading order
    install-guide.cover.png   the cover for the drawings shelf
    install-guide.pdf.json    document metadata for homesodamachine.com/drawings

One page per HTML file: the renderer prints page 1 of each and nothing else, so a leaf that
paginates is a leaf that loses its tail. `PAGES` below is the bound order; the batch render's
own filename sort only decides which one is drawn first.

Underscore-prefixed so the development server does not run it as a generator.

    tools/cad-venv/bin/python hardware/install-guide/_build.py
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path


# Set before `_cadq_export` is imported: the module takes the build lock at import time, and a
# browser-and-pypdf run is not a CAD build — it must neither supersede a running generator nor
# be superseded by one.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in HERE.parents if (p / "tools" / "render").is_dir())
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
QUICKSTART = HARDWARE / "quickstart"
OUT = HERE / "out"
PDF = HERE / "install-guide.pdf"
COVER = HERE / "install-guide.cover.png"
SIDECAR = HERE / "install-guide.pdf.json"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf, note_read, note_write  # noqa: E402

TITLE = "Home Soda Machine install guide"
# 5.5 x 8.5 in at 300 dpi. The renderer prints at 96 CSS px/in, so the PDF scale it derives is
# 5.5 * 96 / 1650 = 0.32 exactly; keep the three numbers moving together or the page resizes.
CANVAS_W, CANVAS_H = 1650, 2550
PAGE_SIZE = "5.5x8.5in"
COVER_W = 800

# Bound order. A saddle-stapled booklet folds in fours, so this stays a multiple of four.
PAGES = (
    HERE / "01-cover.html",
    HERE / "02-two-documents.html",
    HERE / "03-in-the-box.html",
    HERE / "04-what-you-bring.html",
    HERE / "05-the-whole-path.html",
    HERE / "06-the-opening.html",
    HERE / "07-the-cabinet.html",
    HERE / "08-the-faucet.html",
    HERE / "09-which-kitchen.html",
    HERE / "10-older-kitchen-1.html",
    HERE / "11-older-kitchen-2.html",
    HERE / "12-the-filter.html",
    HERE / "13-the-cylinder.html",
    HERE / "14-the-back.html",
    HERE / "15-power.html",
    HERE / "16-first-hour.html",
    HERE / "17-keeping-it.html",
    HERE / "18-ratings.html",
    HERE / "19-if-unsure.html",
    HERE / "20-back.html",
)
RENDER_PAGE_TIMEOUT_SECONDS = 180
# The cold-browser probe and each kept page have their own deadlines inside the renderer. This
# outer cap is the final guard around browser launch and cleanup.
RENDER_ACTION_TIMEOUT_SECONDS = 600

FONTS = HARDWARE / "assembly" / "cards" / "fonts"
ART = QUICKSTART / "art"
PLUMBING_ART = QUICKSTART / "plumbing" / "art"

# Everything Chrome fetches. A file absent here is a file the sandbox does not have, and a page
# drawn against a picture that never arrived renders clean and wrong.
PAGE_ASSETS = (
    HERE / "style.css",
    FONTS / "IBMPlexSans-400-700-normal-latin.woff2",
    FONTS / "IBMPlexSans-400-700-italic-latin.woff2",
    REPO_ROOT / "ios" / "AppIcon.svg",
    QUICKSTART / "quick-start.cover.png",
    ART / "machine-front.png",
    ART / "machine-back-iso.png",
    ART / "machine-back-close.png",
    ART / "machine-funnel-close.png",
    ART / "machine-ports-action.png",
    ART / "faucet-front.png",
    ART / "faucet-side-pressed.png",
    ART / "mount-tighten-close.png",
    PLUMBING_ART / "plumbing-valve-on.png",
    PLUMBING_ART / "plumbing-valve-off.png",
    PLUMBING_ART / "plumbing-pre-tee.png",
    PLUMBING_ART / "plumbing-tee-installed.png",
)


def pages() -> list[Path]:
    return list(PAGES)


def render_pages() -> int:
    renderer = REPO_ROOT / "tools" / "render" / "render-card.js"
    authored = {page.stem for page in pages()}
    for suffix in ("*.png", "*.pdf"):
        for stale in OUT.glob(suffix):
            if stale.stem not in authored:
                stale.unlink()
    for runtime in (
        renderer.parent / "browser.js",
        renderer.parent / "package-lock.json",
        renderer.parent / "package.json",
        renderer,
    ):
        note_read(runtime)
    for path in (*PAGES, *PAGE_ASSETS):
        note_read(path)
    for page in pages():
        note_write(OUT / f"{page.stem}.png")
        note_write(OUT / f"{page.stem}.pdf")
        # A killed renderer cannot leave an earlier hand-build leaf looking current.
        (OUT / f"{page.stem}.png").unlink(missing_ok=True)
        (OUT / f"{page.stem}.pdf").unlink(missing_ok=True)
    try:
        result = subprocess.run(
            [
                "node",
                str(renderer),
                "--batch",
                str(HERE),
                str(OUT),
                "--size",
                f"{CANVAS_W}x{CANVAS_H}",
                "--dpr",
                "1.2",
                "--pdf",
                PAGE_SIZE,
                "--page-timeout",
                str(RENDER_PAGE_TIMEOUT_SECONDS * 1000),
            ],
            check=False,
            timeout=RENDER_ACTION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(
            "install guide renderer exceeded its "
            f"{RENDER_ACTION_TIMEOUT_SECONDS} s action deadline",
            file=sys.stderr,
        )
        return 124
    return result.returncode


def bind() -> int:
    from pypdf import PdfWriter

    authored = [page.stem for page in pages()]
    rendered = {page.stem for page in OUT.glob("*.pdf")}
    missing = [stem for stem in authored if stem not in rendered]
    for stem in missing:
        print(f"MISSING LEAF: {OUT / (stem + '.pdf')}")
    for stem in sorted(rendered - set(authored)):
        print(f"orphan render: {OUT / (stem + '.pdf')}")
    order = [stem for stem in authored if stem in rendered]
    if not order:
        sys.exit("no rendered leaves")
    if len(order) % 4:
        print(f"NOT A FOLDED MULTIPLE: {len(order)} leaves do not saddle-staple in fours")

    def assemble(out_path: str) -> None:
        writer = PdfWriter()
        for stem in order:
            writer.append(str(OUT / f"{stem}.pdf"))
        # Skia stamps its own dates into every leaf, and append leaves each source document's
        # /Info behind. Pinning all four keys is what makes the bound file a function of its
        # pages rather than of the minute it was bound.
        writer.compress_identical_objects()
        writer.add_metadata(
            {"/Title": TITLE, "/Author": "", "/Producer": "", "/Creator": ""}
        )
        with open(out_path, "wb") as handle:
            writer.write(handle)

    export_pdf(assemble, str(PDF))
    write_cover(OUT / f"{order[0]}.png")
    sidecar = {
        "title": TITLE,
        "subtitle": f"Owner install guide - {len(order)} pages, 5.5 x 8.5 in, saddle-stapled",
        "pages": len(order),
        "cover": COVER.name,
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2) + "\n"
    if not SIDECAR.exists() or SIDECAR.read_text() != text:
        SIDECAR.write_text(text)
    else:
        note_write(SIDECAR)
    print(f"-> {PDF} ({len(order)} pages, {PDF.stat().st_size // 1024} KB)")
    return len(missing)


def write_cover(source: Path) -> None:
    from PIL import Image

    with Image.open(source) as image:
        thumb = image.convert("RGB").resize(
            (COVER_W, COVER_W * CANVAS_H // CANVAS_W), Image.Resampling.LANCZOS
        )
        buffer = io.BytesIO()
        thumb.save(buffer, format="PNG", optimize=True)
    data = buffer.getvalue()
    if not COVER.exists() or COVER.read_bytes() != data:
        COVER.write_bytes(data)
    else:
        note_write(COVER)


if __name__ == "__main__":
    status = render_pages()
    missing = bind()
    if status or missing:
        sys.exit(
            f"install guide built with {missing} missing leaf/leaves; renderer exited {status}"
        )
