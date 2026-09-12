"""Bind the quick start with words into its PDF, its cover, and its `/drawings` sidecar.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/quickstart-claude/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
and it keeps no `note_read` / `note_write` bookkeeping. Its outputs are committed to git rather
than packed into the release asset, and reach the served disk on the deploy `render.yaml`'s
build filter names for the sheet's directory.

    tools/cad-venv/bin/python tools/quickstart-claude/build.py

One page. The renderer prints it at 19 x 13 in off the same laid-out 5700 x 3900 px canvas it
captures the cover from; the `.card > header|main|footer` anatomy in `style.css` is what its
spill gate measures.
"""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHEET_DIR = ROOT / "hardware" / "quickstart-claude"
PAGE = SHEET_DIR / "quick-start-claude.html"
OUT = SHEET_DIR / "out"
PDF = SHEET_DIR / "quick-start-claude.pdf"
COVER = SHEET_DIR / "quick-start-claude.cover.png"
SIDECAR = SHEET_DIR / "quick-start-claude.pdf.json"
RENDERER = ROOT / "tools" / "render" / "render-card.js"

TITLE = "Quick start · Claude"
# 19 x 13 in at 300 dpi. The renderer prints at 96 CSS px/in, so the PDF scale it derives is
# 19 * 96 / 5700 = 0.32 exactly; keep the three numbers moving together or the page resizes.
CANVAS_W, CANVAS_H = 5700, 3900
PAGE_SIZE = "19x13in"
COVER_W = 800

RENDER_PAGE_TIMEOUT_SECONDS = 180
RENDER_ACTION_TIMEOUT_SECONDS = 600


def render() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    png = OUT / f"{PAGE.stem}.png"
    # A killed renderer must not leave an earlier render looking current.
    png.unlink(missing_ok=True)
    png.with_suffix(".pdf").unlink(missing_ok=True)
    try:
        result = subprocess.run(
            ["node", str(RENDERER), str(PAGE), str(png),
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

    source = OUT / f"{PAGE.stem}.pdf"
    if not source.exists():
        print(f"MISSING SHEET: {source}")
        return 1

    writer = PdfWriter()
    writer.append(str(source))
    # Skia stamps its own dates into the page. Pinning all four keys is what makes the bound
    # file a function of its page rather than of the minute it was bound.
    writer.compress_identical_objects()
    writer.add_metadata({"/Title": TITLE, "/Author": "", "/Producer": "", "/Creator": ""})
    with open(PDF, "wb") as handle:
        writer.write(handle)

    write_cover(OUT / f"{PAGE.stem}.png")
    sidecar = {
        "title": TITLE,
        "subtitle": "Owner installation quick start, with words - one 19 x 13 in sheet",
        "pages": 1,
        "cover": COVER.name,
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2, ensure_ascii=False) + "\n"
    if not SIDECAR.exists() or SIDECAR.read_text() != text:
        SIDECAR.write_text(text)
    print(f"-> {PDF.relative_to(ROOT)} ({PDF.stat().st_size // 1024} KB)")
    return 0


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
        sys.exit(f"built with the sheet {'missing' if absent else 'present'}; renderer exited {status}")
