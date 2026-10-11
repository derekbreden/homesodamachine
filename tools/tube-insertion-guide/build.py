"""Bind the tube insertion jig guide into a Letter PDF, cover and `/drawings` sidecar.

Run by hand. The authored pages, pictures and bound PDF are committed artifacts.
This module has no build-system target.

    tools/cad-venv/bin/python tools/tube-insertion-guide/insertion_art.py   # the pictures, first
    tools/cad-venv/bin/python tools/tube-insertion-guide/build.py         # then the book

`pages()` reads the order from the numbered leaf filenames. The renderer checks the
authored page bounds during this manual pass and prints page 1 of each leaf.
"""

from __future__ import annotations

import io
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / "hardware" / "tube-insertion-guide"
OUT = GUIDE / "out"
PDF = GUIDE / "tube-insertion-guide.pdf"
COVER = GUIDE / "tube-insertion-guide.cover.png"
SIDECAR = GUIDE / "tube-insertion-guide.pdf.json"
DELIVERY = ROOT / "output" / "pdf" / PDF.name
FIXTURE = ROOT / "hardware" / "printed-parts" / "fixtures" / "tube-insertion"
RENDERER = ROOT / "tools" / "render" / "render-card.js"

TITLE = "Tube insertion jig build guide"
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
        "subtitle": (f"Shop guide - build and use the tube insertion jig, {len(order)} pages, "
                     "8.5 x 11 in, single sided"),
        "pages": len(order),
        "cover": COVER.name,
        "cover_size": [COVER_W, COVER_W * CANVAS_H // CANVAS_W],
    }
    text = json.dumps(sidecar, indent=2) + "\n"
    if not SIDECAR.exists() or SIDECAR.read_text() != text:
        SIDECAR.write_text(text)
    write_delivery(len(order))
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


def write_delivery(count: int) -> None:
    """Save an identical delivery copy and a manual snapshot of its authored inputs."""
    DELIVERY.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PDF, DELIVERY)
    source_paths = set(pages()) | set((GUIDE / "art").glob("*.png")) | {
        GUIDE / "style.css",
        GUIDE / "README.md",
        HERE / "build.py",
        HERE / "insertion_art.py",
        FIXTURE / "tube_insertion.py",
        FIXTURE / "parts.json",
        FIXTURE / "geometry-review.json",
        FIXTURE / "print-layout.json",
        FIXTURE / "prepare_print.py",
        ROOT / "hardware/printed-parts/faucet/lever-replica/lever_replica.py",
        ROOT / "hardware/printed-parts/faucet/lever-replica/physical-acceptance.json",
        ROOT / "hardware/printed-parts/faucet/lever-replica/assembly-observations.json",
        ROOT / "hardware/printed-parts/faucet/tpu-o-ring/tpu_o_ring.py",
        ROOT / "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass_reference.py",
        ROOT / "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step",
        ROOT / "hardware/assembly/faucet-and-umbilical.md",
    }
    plan = json.loads((FIXTURE / "print-layout.json").read_text())
    for plate in plan["plates"]:
        source_paths.add(ROOT / plate["settings_source"])
        for part in plate["parts"]:
            source_paths.add(FIXTURE / part["source"])
        project = FIXTURE / "ready" / plate["project"]
        source_paths.update((project, project.with_suffix(".gcode.3mf"),
                             project.with_suffix(".print.json"),
                             project.with_suffix(".readiness.json")))
    receipt = {
        "pdf": PDF.name,
        "pages": count,
        "page_inches": [8.5, 11],
        "print_layout": {"canvas_px": [CANVAS_W, CANVAS_H], "dpi": 300,
                         "print_scaling": "100% / none", "sides": "single sided"},
        "artwork": "Real fixture CAD, accepted faucet lever and thimble; fasteners are size proxies. The installed faucet lever is omitted from nominal jig views because its accepted pose has no measured CAD transform.",
        "physical_scope": "Unprinted prototype. Observations establish the faucet assembly sequence; geometry and offline slices do not establish insertion force, grip or endurance.",
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(source_paths)},
        "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
    }
    DELIVERY.with_suffix(".sources.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    status = render()
    absent = bind()
    if status or absent:
        sys.exit(f"built with {absent} missing leaf/leaves; renderer exited {status}")
