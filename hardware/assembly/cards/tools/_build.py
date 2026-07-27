"""Build the printable tool deck: render every station card to out/<name>.png
at 3960x3060 (11x8.5 in at 360 dpi), then assemble out/deck-tools.pdf with one
11x8.5-inch page per card in station order.

Underscore-prefixed so the dev-server watcher never runs it.

    tools/cad-venv/bin/python hardware/assembly/cards/tools/_build.py
"""

import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = next(p for p in TOOLS_DIR.parents if (p / "tools" / "render").is_dir())
# Shared machinery from the repo root, content from the nearest hardware/.
HARDWARE = next(p for p in TOOLS_DIR.parents if p.name == "hardware")
OUT_DIR = TOOLS_DIR / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import export_pdf  # noqa: E402

sys.path.insert(0, str(TOOLS_DIR))
from _index import STATIONS  # noqa: E402

PAGE_W, PAGE_H = 11 * 72, 8.5 * 72  # points
ORDER = [code.lower() for code, *_ in STATIONS]


def deck_key(png: Path):
    code = png.stem.split("-", 1)[0]
    return (ORDER.index(code) if code in ORDER else len(ORDER), png.stem)


def render_cards() -> None:
    subprocess.run(
        [
            "node", str(REPO_ROOT / "tools" / "render" / "render-card.js"),
            "--batch", str(TOOLS_DIR), str(OUT_DIR),
            "--size", "3300x2550", "--dpr", "1.2",
        ],
        check=True,
    )


def build_pdf() -> None:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as pdf_canvas

    authored = {p.stem for p in TOOLS_DIR.glob("*.html")}
    rendered = {p.stem for p in OUT_DIR.glob("*.png")}

    for stem in sorted(rendered - authored):
        print(f"orphan render (no {stem}.html): {OUT_DIR / (stem + '.png')}")
    missing = sorted(authored - rendered)
    if missing:
        sys.exit(f"card(s) authored but not rendered: {', '.join(missing)}")

    # Every station in the index either has a card or does not; naming the
    # gap here is the only place the deck's own completeness is visible.
    have = {p.stem.split("-", 1)[0] for p in TOOLS_DIR.glob("*.html")}
    gaps = [c.upper() for c in ORDER if c not in have]
    if gaps:
        print(f"stations without a card: {', '.join(gaps)}")

    pngs = sorted((OUT_DIR / f"{s}.png" for s in authored), key=deck_key)
    if not pngs:
        sys.exit("no rendered cards in out/")

    def build(out_path):
        c = pdf_canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
        for png in pngs:
            c.drawImage(ImageReader(str(png)), 0, 0, PAGE_W, PAGE_H)
            c.showPage()
        c.save()

    export_pdf(build, str(OUT_DIR / "deck-tools.pdf"))
    print(f"-> {OUT_DIR / 'deck-tools.pdf'} ({len(pngs)} of {len(ORDER)} stations)")


if __name__ == "__main__":
    render_cards()
    build_pdf()
