"""Render and bind the Letter gun-positioner assembly guide.

Run by hand after author.py and art.py. These committed assets are independent
of the appliance build. Rendering keeps HTML text and rules as PDF vectors;
the raster CAD pictures are the exact assemblies named by their scene receipt.
"""
from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / "hardware/gun-positioner-guide"
OUT = GUIDE / "out"
PDF = GUIDE / "gun-positioner-guide.pdf"
COVER = GUIDE / "gun-positioner-guide.cover.png"
RENDERER = ROOT / "tools/render/render-card.js"
TITLE = "Gun positioner assembly guide"
CANVAS = (2550, 3300)


def pages() -> list[Path]:
    found = sorted(GUIDE.glob("[0-9]*-*.html"),key=lambda p:int(p.name.split('-')[0]))
    numbers = [int(p.name.split('-')[0]) for p in found]
    if not found or numbers != list(range(1, len(numbers) + 1)):
        raise ValueError(f"Guide pages are not a complete 1..N sequence: {numbers}")
    return found


def verify_inputs() -> dict:
    manifest=json.loads((GUIDE/'page-manifest.json').read_text())
    stale=[p for p,h in manifest['input_sha256'].items()
           if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    scene=json.loads((GUIDE/'art/scene-receipt.json').read_text())
    schematic=json.loads((GUIDE/'art/schematic-receipt.json').read_text())
    for leaf in manifest['leaves']:
        if not leaf['art']:continue
        path=GUIDE/'art'/leaf['art']
        if not path.exists():raise FileNotFoundError(path)
        if path.suffix=='.png':
            record=scene['scenes'].get(path.stem)
            if not record:raise RuntimeError(f'Missing actual-CAD receipt for {path.name}')
            expected=record['png_sha256']
        else:
            record=schematic
            expected=schematic['svg_sha256'][path.name]
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            stale.append(str(path.relative_to(ROOT)))
        stale.extend(p for p,h in record['input_sha256'].items()
                     if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h)
    templates=json.loads((GUIDE/'drill-template-receipt.json').read_text())
    stale.extend(p for p,h in templates['source_sha256'].items()
                 if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h)
    template_pdf=GUIDE/templates['file']
    if hashlib.sha256(template_pdf.read_bytes()).hexdigest()!=templates['pdf_sha256']:
        stale.append(str(template_pdf.relative_to(ROOT)))
    if stale:raise RuntimeError(f'Guide inputs or art changed; rebuild the affected source first: {sorted(set(stale))}')
    return manifest


def render() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stems = {p.stem for p in pages()}
    for suffix in ("png", "pdf"):
        for leaf in OUT.glob(f"*.{suffix}"):
            if leaf.stem not in stems:
                leaf.unlink()
    for page in pages():
        (OUT / f"{page.stem}.png").unlink(missing_ok=True)
        (OUT / f"{page.stem}.pdf").unlink(missing_ok=True)
    subprocess.run(
        ["node", str(RENDERER), "--batch", str(GUIDE), str(OUT),
         "--size", "2550x3300", "--dpr", "1", "--pdf", "8.5x11in",
         "--page-timeout", "180000"],
        cwd=ROOT, check=True, timeout=1800,
    )


def bind() -> None:
    from PIL import Image
    from pypdf import PdfReader, PdfWriter

    manifest=verify_inputs()
    leaves = pages()
    writer = PdfWriter()
    for page in leaves:
        leaf = OUT / f"{page.stem}.pdf"
        reader = PdfReader(leaf)
        if len(reader.pages) != 1:
            raise ValueError(f"{leaf.name}: expected exactly one Letter page")
        size = list(reader.pages[0].mediabox)[2:]
        if abs(float(size[0]) - 612) > .02 or abs(float(size[1]) - 792) > .02:
            raise ValueError(f"{leaf.name}: wrong media size {size}")
        writer.append(reader)
    parent=None
    chapter=None
    for i,leaf in enumerate(manifest['leaves']):
        name=leaf['section'].split(' / ')[0]
        if name!=chapter:
            parent=writer.add_outline_item(name,i)
            chapter=name
        writer.add_outline_item(f'{i+1:02d} · {leaf["title"]}',i,parent=parent)
    writer.compress_identical_objects()
    writer.add_metadata({"/Title": TITLE, "/Author": "Home Soda Machine",
                         "/Producer": "", "/Creator": ""})
    with PDF.open("wb") as handle:
        writer.write(handle)
    with Image.open(OUT / f"{leaves[0].stem}.png") as source:
        image = source.convert("RGB").resize((800, 1035), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format="PNG", optimize=True)
        COVER.write_bytes(buf.getvalue())
    (GUIDE / "gun-positioner-guide.pdf.json").write_text(json.dumps({
        "title": TITLE,
        "subtitle": f"Shop guide — {len(leaves)} pages, Letter 8.5 × 11 in, print single-sided at actual size",
        "pages": len(leaves), "cover": COVER.name, "cover_size": [800, 1035],
    }, indent=2) + "\n")

    sources = [
        "tools/gun-positioner-guide/author.py", "tools/gun-positioner-guide/art.py",
        "tools/gun-positioner-guide/build.py", "tools/gun-positioner-guide/templates.py",
        "tools/gun-positioner-guide/schematic_detail.py",
        "hardware/gun-positioner-guide/style.css", "hardware/gun-positioner-guide/drill-template-receipt.json",
    ]
    for receipt in [GUIDE / "art/scene-receipt.json", GUIDE / "art/schematic-receipt.json", GUIDE / "page-manifest.json"]:
        sources.append(str(receipt.relative_to(ROOT)))
    scene = json.loads((GUIDE / "art/scene-receipt.json").read_text())
    sources.extend(scene["source_files"])
    sources.extend(manifest['input_sha256'])
    sources = sorted(set(sources))
    (GUIDE / "source-receipt.json").write_text(json.dumps({
        "title": TITLE, "pages": len(leaves), "page_inches": [8.5, 11],
        "canvas_pixels": list(CANVAS), "print_scaling": "100% / actual size",
        "artwork": "CAD assemblies plus vector wiring and measurement schematics",
        "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                          for p in sources},
        "pdf_sha256": hashlib.sha256(PDF.read_bytes()).hexdigest(),
    }, indent=2) + "\n")
    print(f"Bound {len(leaves)} Letter pages: {PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    verify_inputs()
    if "--bind-only" not in sys.argv:
        render()
    bind()
