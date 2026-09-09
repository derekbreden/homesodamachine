"""Bind the two funnel guides — the bench documents for making the mold and casting from it.

    funnel-mold.pdf         build the tooling: three prints, the finish, the steel
    funnel-cast.pdf         make the part: mix, pour, vacuum, cure, extract, trim
    <name>.cover.png        the cover for the drawings shelf
    <name>.pdf.json         document metadata for homesodamachine.com/drawings

Both are 8.5 x 11 in portrait, single-sided, printed at 100 % on any paper the shop has and
kept in a binder. Neither imposes; page count is free.

ONE HTML FILE IS EXACTLY ONE PAGE. The renderer prints page 1 and nothing else, so a leaf
whose content outgrows it loses its tail rather than flowing. It also fails the run on
OVERFLOW, SPILL and CLIPPED against `.card > header|main|footer`. Fix the leaf, not the check.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/funnel-mold-guide/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
so no sweep traces it into a rule and no changed-path reading widens a slice to reach it.

These bytes are in git, not in the release asset, and they reach the served disk on the deploy
`render.yaml`'s build filter names for the guide directory. The site finds the PDFs by walking
`hardware/` for a `.pdf` beside a `.pdf.json`. Run it by hand when the pages or the art move:

    tools/cad-venv/bin/python tools/funnel-mold-guide/_art.py     # the pictures
    tools/cad-venv/bin/python tools/funnel-mold-guide/_build.py   # the documents
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Set before `_cadq_export` is imported: the module takes the build lock at import time, and a
# browser-and-pypdf run is not a CAD build.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
HARDWARE = REPO_ROOT / "hardware"
GUIDE = HARDWARE / "funnel-mold-guide"
ART = GUIDE / "art"
OUT = GUIDE / "out"
FONTS = HARDWARE / "assembly" / "cards" / "fonts"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf, note_read, note_write  # noqa: E402

# 8.5 x 11 in at 300 dpi. The renderer prints at 96 CSS px/in, so the PDF scale it derives is
# 8.5 * 96 / 2550 = 0.32 exactly; keep the three numbers moving together or the page resizes.
CANVAS_W, CANVAS_H = 2550, 3300
PAGE_SIZE = "8.5x11in"
COVER_W = 800

DOCUMENTS = (
    {
        "stem": "funnel-mold",
        "title": "Funnel mold build guide",
        "subtitle": "Shop guide - build the tooling, {pages} pages, 8.5 x 11 in, single sided",
        "prefix": "mold-",
    },
    {
        "stem": "funnel-cast",
        "title": "Funnel casting guide",
        "subtitle": "Shop guide - cast one funnel, {pages} pages, 8.5 x 11 in, single sided",
        "prefix": "cast-",
    },
)

RENDER_PAGE_TIMEOUT_SECONDS = 180
RENDER_ACTION_TIMEOUT_SECONDS = 900


def leaves(prefix: str) -> list[Path]:
    return sorted(GUIDE.glob(f"{prefix}*.html"))


def all_leaves() -> list[Path]:
    return [leaf for doc in DOCUMENTS for leaf in leaves(doc["prefix"])]


def render_pages() -> int:
    renderer = REPO_ROOT / "tools" / "render" / "render-card.js"
    authored = {leaf.stem for leaf in all_leaves()}
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
    # Everything Chrome fetches. A page drawn against a picture that never arrived renders
    # clean and wrong, so the sandbox is told about each file by name.
    assets = [
        GUIDE / "style.css",
        FONTS / "IBMPlexSans-400-700-normal-latin.woff2",
        FONTS / "IBMPlexSans-400-700-italic-latin.woff2",
        FONTS / "IBMPlexMono-400-normal-latin.woff2",
        FONTS / "IBMPlexMono-600-normal-latin.woff2",
        *sorted(ART.glob("*.png")),
        # The one picture this guide does not cut: the extraction station's own section,
        # which already stands beside the geometry it describes.
        HARDWARE / "printed-parts" / "zone-c" / "funnel-mold" / "extraction.png",
    ]
    for path in (*all_leaves(), *assets):
        note_read(path)
    for leaf in all_leaves():
        note_write(OUT / f"{leaf.stem}.png")
        note_write(OUT / f"{leaf.stem}.pdf")
        (OUT / f"{leaf.stem}.png").unlink(missing_ok=True)
        (OUT / f"{leaf.stem}.pdf").unlink(missing_ok=True)
    OUT.mkdir(exist_ok=True)
    try:
        result = subprocess.run(
            [
                "node", str(renderer), "--batch", str(GUIDE), str(OUT),
                "--size", f"{CANVAS_W}x{CANVAS_H}",
                "--dpr", "1.2",
                "--pdf", PAGE_SIZE,
                "--page-timeout", str(RENDER_PAGE_TIMEOUT_SECONDS * 1000),
            ],
            check=False,
            timeout=RENDER_ACTION_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        print(f"renderer exceeded its {RENDER_ACTION_TIMEOUT_SECONDS} s deadline", file=sys.stderr)
        return 124
    return result.returncode


def bind_one(doc: dict) -> int:
    from pypdf import PdfWriter

    stem, prefix = doc["stem"], doc["prefix"]
    authored = [leaf.stem for leaf in leaves(prefix)]
    rendered = {path.stem for path in OUT.glob(f"{prefix}*.pdf")}
    missing = [name for name in authored if name not in rendered]
    for name in missing:
        print(f"MISSING LEAF: {OUT / (name + '.pdf')}")
    order = [name for name in authored if name in rendered]
    if not order:
        print(f"no rendered leaves for {stem}", file=sys.stderr)
        return 1

    def assemble(out_path: str) -> None:
        writer = PdfWriter()
        for name in order:
            writer.append(str(OUT / f"{name}.pdf"))
        # Skia stamps its own dates into every leaf. Pinning all four keys is what makes the
        # bound file a function of its pages rather than of the minute it was bound.
        writer.compress_identical_objects()
        writer.add_metadata(
            {"/Title": doc["title"], "/Author": "", "/Producer": "", "/Creator": ""}
        )
        with open(out_path, "wb") as handle:
            writer.write(handle)

    pdf = GUIDE / f"{stem}.pdf"
    cover = GUIDE / f"{stem}.cover.png"
    export_pdf(assemble, str(pdf))
    write_cover(OUT / f"{order[0]}.png", cover)
    sidecar = GUIDE / f"{stem}.pdf.json"
    text = json.dumps(
        {
            "title": doc["title"],
            "subtitle": doc["subtitle"].format(pages=len(order)),
            "pages": len(order),
            "cover": cover.name,
            "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
        },
        indent=2,
    ) + "\n"
    if not sidecar.exists() or sidecar.read_text() != text:
        sidecar.write_text(text)
    else:
        note_write(sidecar)
    print(f"-> {pdf.name} ({len(order)} pages, {pdf.stat().st_size // 1024} KB)")
    return len(missing)


def write_cover(source: Path, destination: Path) -> None:
    from PIL import Image

    with Image.open(source) as image:
        thumb = image.convert("RGB").resize(
            (COVER_W, COVER_W * CANVAS_H // CANVAS_W), Image.Resampling.LANCZOS
        )
    note_write(destination)
    thumb.save(destination, optimize=True)


def main() -> int:
    code = render_pages()
    if code:
        return code
    return sum(bind_one(doc) for doc in DOCUMENTS)


if __name__ == "__main__":
    sys.exit(main())
