"""Build the printable card deck: render every card HTML to out/<name>.png
at 2160x1440 (6x4 in at 360 dpi) via tools/render/render-card.js, then
assemble out/deck.pdf with one 6x4-inch page per card in deck order.

Underscore-prefixed so the dev-server watcher never runs it.

    tools/cad-venv/bin/python hardware/assembly/cards/_build.py
"""

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
OUT_DIR = CARDS_DIR / "out"

sys.path.insert(0, str(REPO_ROOT / "hardware" / "scripts"))
from _cadq_export import export_pdf  # noqa: E402

# Deck order = the build order of /hardware/future.md "Build order".
SUBSYSTEM_ORDER = ["pv", "cc", "rl", "ip", "ca", "es", "wr", "en", "fu", "fc", "ab", "fs"]

PAGE_W, PAGE_H = 6 * 72, 4 * 72  # points


def deck_key(png: Path):
    code = png.stem.split("-", 1)[0]
    if code == "00":  # the cover leads the deck
        return (-1, png.stem)
    try:
        subsystem = SUBSYSTEM_ORDER.index(code)
    except ValueError:
        subsystem = len(SUBSYSTEM_ORDER)
    return (subsystem, png.stem)


def render_cards() -> None:
    subprocess.run(
        [
            "node",
            str(REPO_ROOT / "tools" / "render" / "render-card.js"),
            "--batch",
            str(CARDS_DIR),
            str(OUT_DIR),
            "--dpr",
            "1.2",
        ],
        check=True,
    )


def build_pdf() -> None:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas as pdf_canvas

    pngs = sorted(OUT_DIR.glob("*.png"), key=deck_key)
    if not pngs:
        sys.exit("no rendered cards in out/")

    def build(out_path):
        c = pdf_canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
        for png in pngs:
            c.drawImage(ImageReader(str(png)), 0, 0, PAGE_W, PAGE_H)
            c.showPage()
        c.save()

    export_pdf(build, str(OUT_DIR / "deck.pdf"))
    print(f"-> {OUT_DIR / 'deck.pdf'} ({len(pngs)} cards)")


if __name__ == "__main__":
    render_cards()
    build_pdf()
