"""Build the two-sheet, 11 x 17 in Home Soda Machine installation quick start.

Product-derived artwork is a separate build step in ``quickstart_art.py``. Keeping it separate means a
layout or copy edit rerenders only these sheets; CAD and firmware changes rebuild the artwork
first through the Bazel dependency graph.

    quick-start.pdf         two print-ready 11 x 17 in pages
    quick-start.cover.png   the installation sheet for the drawings shelf
    quick-start.pdf.json    document metadata for homesodamachine.com/drawings

Underscore-prefixed so the development server does not run it as a generator.

    tools/cad-venv/bin/python hardware/quickstart/_build.py
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
from pathlib import Path


os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in HERE.parents if (p / "tools" / "render").is_dir())
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
OUT = HERE / "out"
PDF = HERE / "quick-start.pdf"
COVER = HERE / "quick-start.cover.png"
SIDECAR = HERE / "quick-start.pdf.json"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf, note_read, note_write  # noqa: E402

TITLE = "Faucet + umbilical installation quick start"
CANVAS_W, CANVAS_H = 2550, 1650
COVER_W = 800

FONTS = tuple((HARDWARE / "assembly" / "cards" / "fonts").glob("*.woff2"))
PAGES = (HERE / "00-mount.html", HERE / "01-connect.html")
PAGE_ASSETS = (
    HERE / "style.css",
    HERE / "art" / "colors.css",
    HERE / "art" / "faucet-side.png",
    HERE / "art" / "machine-back-iso.png",
    HERE / "art" / "machine-ports-iso.png",
    HERE / "art" / "mount-drop.png",
    HERE / "art" / "mount-final-clean.png",
    HERE / "art" / "mount-lowered-clean.png",
    HERE / "art" / "mount-slide-clean.png",
)


def pages() -> list[Path]:
    return list(PAGES)


def render_pages() -> int:
    renderer = REPO_ROOT / "tools" / "render" / "render-card.js"
    note_read(renderer)
    for path in FONTS:
        note_read(path)
    for path in (*PAGES, *PAGE_ASSETS):
        note_read(path)
    status = 0
    for page in pages():
        note_write(OUT / f"{page.stem}.png")
        note_write(OUT / f"{page.stem}.pdf")
        result = subprocess.run(
            [
                "node",
                str(renderer),
                str(page),
                str(OUT / f"{page.stem}.png"),
                "--size",
                f"{CANVAS_W}x{CANVAS_H}",
                "--dpr",
                "1",
                "--pdf",
                "17x11in",
            ],
            check=False,
        )
        status = status or result.returncode
    return status


def bind() -> int:
    from pypdf import PdfWriter

    authored = [page.stem for page in pages()]
    rendered = {page.stem for page in OUT.glob("*.pdf")}
    missing = [stem for stem in authored if stem not in rendered]
    for stem in missing:
        print(f"MISSING SHEET: {OUT / (stem + '.pdf')}")
    for stem in sorted(rendered - set(authored)):
        print(f"orphan render: {OUT / (stem + '.pdf')}")
    order = [stem for stem in authored if stem in rendered]
    if not order:
        raise SystemExit("no rendered sheets")

    def assemble(out_path: str) -> None:
        writer = PdfWriter()
        for stem in order:
            writer.append(str(OUT / f"{stem}.pdf"))
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
        "subtitle": "Owner installation quick start - two 11 x 17 in sheets",
        "pages": len(order),
        "cover": COVER.name,
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2) + "\n"
    if not SIDECAR.exists() or SIDECAR.read_text() != text:
        SIDECAR.write_text(text)
    else:
        note_write(SIDECAR)
    print(f"-> {PDF} ({len(order)} sheets, {PDF.stat().st_size // 1024} KB)")
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
        raise SystemExit(
            f"quick start built with {missing} missing sheet(s); renderer exited {status}"
        )
