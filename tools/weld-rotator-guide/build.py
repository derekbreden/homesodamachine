"""Bind the weld-rotator build guide into one PDF, its cover, and its `/drawings` sidecar.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/weld-rotator-guide/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
and it keeps no `note_read` / `note_write` bookkeeping. Its outputs are committed to git rather
than packed into the release asset, and reach the served disk on the deploy `render.yaml`'s
build filter already names for this directory.

    tools/cad-venv/bin/python tools/weld-rotator-guide/rotator_art.py   # the pictures, first
    tools/cad-venv/bin/python tools/weld-rotator-guide/build.py         # then the book

`pages()` is the bound order, read off the leaf filenames. The renderer prints page 1 of each
leaf and nothing else; the `.card > header|main|footer` anatomy in `style.css` is what its spill
gate measures.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / "hardware" / "weld-rotator-guide"
OUT = GUIDE / "out"
PDF = GUIDE / "weld-rotator-guide.pdf"
COVER = GUIDE / "weld-rotator-guide.cover.png"
SIDECAR = GUIDE / "weld-rotator-guide.pdf.json"
RENDERER = ROOT / "tools" / "render" / "render-card.js"

TITLE = "Weld rotator build guide"
# 8.5 x 11 in at 300 dpi. The renderer prints at 96 CSS px/in, so the PDF scale it derives is
# 8.5 * 96 / 2550 = 0.32 exactly; keep the three numbers moving together or the page resizes.
CANVAS_W, CANVAS_H = 2550, 3300
PAGE_SIZE = "8.5x11in"
COVER_W = 800

RENDER_PAGE_TIMEOUT_SECONDS = 180
RENDER_ACTION_TIMEOUT_SECONDS = 1800


def pages() -> list[Path]:
    """The bound order: every `NN-name.html` in the guide directory, by its own number."""
    found = sorted(p for p in GUIDE.glob("[0-9][0-9]-*.html"))
    if not found:
        sys.exit(f"no pages under {GUIDE}")
    numbers = [int(p.name[:2]) for p in found]
    if numbers != list(range(1, len(numbers) + 1)):
        sys.exit(f"page numbers are not 1..{len(numbers)}: {numbers}")
    return found


def render() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    authored = {page.stem for page in pages()}
    for pattern in ("*.png", "*.pdf"):
        for stale in OUT.glob(pattern):
            if stale.stem not in authored:
                stale.unlink()
    for page in pages():
        # A killed renderer must not leave an earlier leaf looking current.
        (OUT / f"{page.stem}.png").unlink(missing_ok=True)
        (OUT / f"{page.stem}.pdf").unlink(missing_ok=True)
    try:
        result = subprocess.run(
            ["node", str(RENDERER), "--batch", str(GUIDE), str(OUT),
             "--size", f"{CANVAS_W}x{CANVAS_H}", "--dpr", "1",
             "--pdf", PAGE_SIZE,
             "--page-timeout", str(RENDER_PAGE_TIMEOUT_SECONDS * 1000)],
            check=False, timeout=RENDER_ACTION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(f"renderer exceeded its {RENDER_ACTION_TIMEOUT_SECONDS} s deadline",
              file=sys.stderr)
        return 124
    return result.returncode


def bind() -> int:
    from pypdf import PdfWriter

    authored = [page.stem for page in pages()]
    rendered = {leaf.stem for leaf in OUT.glob("*.pdf")}
    missing = [stem for stem in authored if stem not in rendered]
    for stem in missing:
        print(f"MISSING LEAF: {OUT / (stem + '.pdf')}")
    order = [stem for stem in authored if stem in rendered]
    if not order:
        sys.exit("no rendered leaves")

    writer = PdfWriter()
    for stem in order:
        writer.append(str(OUT / f"{stem}.pdf"))
    # Skia stamps its own dates into every leaf and `append` leaves each source document's
    # /Info behind. Pinning all four keys is what makes the bound file a function of its pages
    # rather than of the minute it was bound.
    writer.compress_identical_objects()
    writer.add_metadata({"/Title": TITLE, "/Author": "", "/Producer": "", "/Creator": ""})
    with open(PDF, "wb") as handle:
        writer.write(handle)

    write_cover(OUT / f"{order[0]}.png")
    sidecar = {
        "title": TITLE,
        "subtitle": (f"Shop guide - build the bench rotator, {len(order)} pages, "
                     "8.5 x 11 in, single sided"),
        "pages": len(order),
        "cover": COVER.name,
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2) + "\n"
    if not SIDECAR.exists() or SIDECAR.read_text() != text:
        SIDECAR.write_text(text)
    print(f"-> {PDF.relative_to(ROOT)} ({len(order)} pages, {PDF.stat().st_size // 1024} KB)")
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


if __name__ == "__main__":
    status = render()
    absent = bind()
    if status or absent:
        sys.exit(f"built with {absent} missing leaf/leaves; renderer exited {status}")
