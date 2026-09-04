"""Render comparative color, lockup, and step-number studies for the Quick Start.

The scene geometry comes directly from ``hardware/quickstart/quick-start.html``. This builder
changes only the field color, the paper color, the center lockup, and the step-number treatment.

    hardware/quickstart/studies/visual-variations/preview.png
    hardware/quickstart/studies/visual-variations/number-preview.png
    output/pdf/quick-start-visual-variations.pdf
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
QUICKSTART = HERE.parents[1]
REPO = HERE.parents[3]
TMP = REPO / "tmp" / "pdfs" / "quickstart-visual-variations"
VARIANT_PAGES = TMP / "variant-pages"
VARIANT_RENDERS = TMP / "variant-renders"
DECK_PAGES = TMP / "deck-pages"
DECK_RENDERS = TMP / "deck-renders"
FINAL_PDF = REPO / "output" / "pdf" / "quick-start-visual-variations.pdf"
PREVIEW = HERE / "preview.png"
NUMBER_PREVIEW = HERE / "number-preview.png"
RENDERER = REPO / "tools" / "render" / "render-card.js"
NODE = shutil.which("node") or "node"
APP_ICON = "../../ios/AppIcon.svg"


@dataclass(frozen=True)
class Variant:
    key: str
    name: str
    field: str = "#DCE7E9"
    paper: str = "#FFFFFF"
    motion: str = "#E64F5C"
    number: str = "#FFFFFF"
    ink: str = "#1A1A2E"
    lockup: str = "canonical"
    number_style: str = "current"
    note: str = ""


FIELDS = (
    Variant("F0", "Current", note="Reference field"),
    Variant("F1", "Carbonation Ice", field="#CEDFE7", note="Clear and aquatic"),
    Variant(
        "F2",
        "Harbor Mist",
        field="#C5D4DA",
        motion="#D94455",
        note="Technical and premium",
    ),
    Variant(
        "F3",
        "Porcelain Gray",
        field="#D5D9DA",
        motion="#DF4757",
        note="Architectural neutral",
    ),
    Variant(
        "F4",
        "Mineral Sage",
        field="#D3DED2",
        motion="#D94254",
        note="Calm kitchen tone",
    ),
    Variant(
        "F5",
        "Warm Stone",
        field="#DED7CD",
        motion="#D64050",
        note="Domestic and warm",
    ),
    Variant(
        "F6",
        "Lavender Fog",
        field="#DAD6E4",
        motion="#D94057",
        note="Quietly color-linked",
    ),
    Variant(
        "F7",
        "Storm Glass",
        field="#B8C7CD",
        motion="#C9344B",
        number="#F9FBFC",
        note="Boldest separation",
    ),
)


PAPERS = (
    Variant("P0", "Pure White", note="Reference paper"),
    Variant("P1", "Warm Porcelain", paper="#F7F3EC", note="Warm, clean default"),
    Variant("P2", "Soft Champagne", paper="#F5EEDC", note="Highest warm separation"),
    Variant("P3", "Coral Shell", paper="#F8ECEB", note="Echoes the motion cue"),
    Variant("P4", "Vapor Lavender", paper="#F0EDF7", note="Connects to the glass mark"),
    Variant("P5", "Chalk Sage", paper="#EEF2E8", note="Soft kitchen neutral"),
    Variant("P6", "Cool Fog", paper="#EFF3F7", note="Clean cool tint"),
    Variant("P7", "Mineral Stone", paper="#EDEAE3", note="Grounded neutral"),
    Variant(
        "P8",
        "Midnight Ink",
        paper="#1A1A2E",
        ink="#FFFFFF",
        note="High-contrast wildcard",
    ),
)


LOCKUPS = (
    Variant("L1", "Refined Horizontal", lockup="v01", note="Conservative refinement"),
    Variant("L2", "Stacked Seal", lockup="v02", note="Centered and emblematic"),
    Variant("L3", "Purpose First", lockup="v03", note="Strongest arm's-length read"),
    Variant("L4", "Editorial Split", lockup="v04", note="Most distinctive center"),
    Variant("L5", "Clock Hub", lockup="v05", note="Makes the ring explicit"),
    Variant("L6", "Technical Rule", lockup="v06", note="Equipment-label voice"),
    Variant("L7", "Dark Capsule", lockup="v07", note="Compact high contrast"),
    Variant("L8", "Asymmetric Anchor", lockup="v08", note="Open editorial center"),
)


COMPOSED = (
    Variant(
        "C1",
        "Clear",
        field="#C5D4DA",
        paper="#F7F3EC",
        motion="#D94455",
        lockup="v03",
        note="Harbor Mist / Warm Porcelain / Purpose First",
    ),
    Variant(
        "C2",
        "Familiar",
        field="#CEDFE7",
        lockup="v01",
        note="Carbonation Ice / Pure White / Refined Horizontal",
    ),
    Variant(
        "C3",
        "Calm",
        field="#D3DED2",
        paper="#F7F3EC",
        motion="#D94254",
        lockup="v04",
        note="Mineral Sage / Warm Porcelain / Editorial Split",
    ),
    Variant(
        "C4",
        "Technical",
        field="#D5D9DA",
        paper="#EDEAE3",
        motion="#DF4757",
        lockup="v06",
        note="Porcelain Gray / Mineral Stone / Technical Rule",
    ),
    Variant(
        "C5",
        "Warm Clear",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n01",
        note="Warm Stone / Pure White / Purpose First / Ink Baseline",
    ),
    Variant(
        "C6",
        "Night",
        field="#B8C7CD",
        paper="#1A1A2E",
        motion="#C9344B",
        number="#F9FBFC",
        ink="#FFFFFF",
        lockup="v03",
        note="Storm Glass / Midnight Ink / Purpose First",
    ),
)


# Every number direction uses the combination selected from the first review: the C1
# Purpose First lockup on F5 Warm Stone. Pure white is held from the F5 comparison card so
# only the number system changes between these sheets.
NUMBERS = (
    Variant(
        "N0",
        "Current White",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        note="Reference: large white Plex Sans",
    ),
    Variant(
        "N1",
        "Ink Baseline",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n01",
        note="High contrast with one restrained motion cue",
    ),
    Variant(
        "N2",
        "Porcelain Disc",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n02",
        note="Compact dark index on the paper color",
    ),
    Variant(
        "N3",
        "Indexed Ring",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n03",
        note="Open dial with a restrained coral sector",
    ),
    Variant(
        "N4",
        "Tall Condensed",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n04",
        note="Narrow silhouette leaves the scenes open",
    ),
    Variant(
        "N5",
        "Mono Register",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n05",
        note="Two-digit equipment-label notation",
    ),
    Variant(
        "N6",
        "Ink Coin",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n06",
        note="Boldest scan with a coral registration pip",
    ),
    Variant(
        "N7",
        "Underlined Tile",
        field="#DED7CD",
        motion="#D64050",
        lockup="v03",
        number_style="n07",
        note="Soft appliance-UI counter with a coral edge",
    ),
)


NUMBER_FINALISTS = ("N2", "N3", "N5", "N6")


LOCKUP_MARKUP = {
    "v01": f"""
      <div class="lockup"><img class="mark" src="{APP_ICON}" alt=""><div>
        <div class="brand">Home Soda Machine</div>
        <div class="document">Quick Start</div>
      </div></div>
    """,
    "v02": f"""
      <div class="lockup"><img class="mark" src="{APP_ICON}" alt="">
        <div class="brand">Home Soda Machine</div>
        <div class="document">Quick Start</div>
      </div>
    """,
    "v03": f"""
      <div class="lockup">
        <div class="eyebrow"><img class="mark" src="{APP_ICON}" alt="">
          <span>Home Soda Machine</span>
        </div>
        <div class="document">Quick Start</div><i class="accent"></i>
      </div>
    """,
    "v04": f"""
      <div class="lockup">
        <div class="identity"><img class="mark" src="{APP_ICON}" alt="">
          <div class="brand">Home<br>Soda<br>Machine</div>
        </div>
        <i class="rule"></i><div class="document">Quick<br>Start</div>
      </div>
    """,
    "v05": f"""
      <div class="lockup"><div class="brand">Home Soda Machine</div>
        <div class="hub"><img class="mark" src="{APP_ICON}" alt=""></div>
        <div class="document">Quick Start</div>
      </div>
    """,
    "v06": f"""
      <div class="lockup">
        <div class="identity"><img class="mark" src="{APP_ICON}" alt="">
          <div class="brand">Home Soda Machine</div>
        </div>
        <i class="rule"></i><div class="document">Quick Start</div>
      </div>
    """,
    "v07": f"""
      <div class="lockup"><img class="mark" src="{APP_ICON}" alt=""><div>
        <div class="brand">Home Soda Machine</div>
        <div class="document">Quick Start</div>
      </div></div>
    """,
    "v08": f"""
      <div class="lockup">
        <div class="identity"><img class="mark" src="{APP_ICON}" alt="">
          <div class="brand">Home Soda Machine</div>
        </div>
        <div class="document">Quick Start</div><i class="accent"></i>
      </div>
    """,
}


def reset_tmp() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    for path in (VARIANT_PAGES, VARIANT_RENDERS, DECK_PAGES, DECK_RENDERS):
        path.mkdir(parents=True, exist_ok=True)


def variant_html(
    source: str,
    variant: Variant,
    lockup_css: str,
    number_css: str,
) -> str:
    base = QUICKSTART.resolve().as_uri() + "/"
    page = source.replace(
        '<meta charset="utf-8">',
        f'<meta charset="utf-8">\n  <base href="{base}">',
        1,
    )
    if variant.paper.upper() == "#1A1A2E":
        page = page.replace("<body>", '<body class="paper-dark">', 1)
    if variant.lockup != "canonical":
        markup = (
            f'<header class="brand-lockup study-lockup {variant.lockup}">'
            f'{LOCKUP_MARKUP[variant.lockup]}</header>'
        )
        page, count = re.subn(
            r'<header class="brand-lockup">.*?</header>',
            markup,
            page,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise RuntimeError("canonical brand lockup was not found exactly once")
    if variant.number_style != "current":
        page, count = re.subn(
            r'<div class="clockwork-numbers" aria-hidden="true">',
            f'<div class="clockwork-numbers number-{variant.number_style}" '
            'aria-hidden="true">',
            page,
            count=1,
        )
        if count != 1:
            raise RuntimeError("canonical number layer was not found exactly once")
    overrides = f"""
<style id="visual-variation-theme">
:root {{
  --field: {variant.field};
  --motion: {variant.motion};
  --ink: {variant.ink};
  --paper: {variant.paper};
}}
html, body, .sheet {{ background: var(--paper) !important; }}
.clockwork-numbers {{ color: {variant.number} !important; }}
{lockup_css if variant.lockup != "canonical" else ""}
{number_css if variant.number_style != "current" else ""}
</style>
"""
    return page.replace("</head>", overrides + "</head>", 1)


def render_batch(source_dir: Path, output_dir: Path, *, dpr: float, pdf: bool) -> None:
    command = [
        NODE,
        str(RENDERER),
        "--batch",
        str(source_dir),
        str(output_dir),
        "--size",
        "5700x3900",
        "--dpr",
        str(dpr),
        "--page-timeout",
        "180000",
    ]
    if pdf:
        command.extend(("--pdf", "19x13in"))
    subprocess.run(command, check=True, cwd=REPO)


def write_variants() -> dict[str, Path]:
    source = (QUICKSTART / "quick-start.html").read_text()
    lockup_css = (HERE / "lockups.css").read_text()
    number_css = (HERE / "numbers.css").read_text()
    pages: dict[str, Path] = {}
    for variant in (*FIELDS, *PAPERS, *LOCKUPS, *COMPOSED, *NUMBERS):
        path = VARIANT_PAGES / f"{variant.key.lower()}-{slug(variant.name)}.html"
        path.write_text(variant_html(source, variant, lockup_css, number_css))
        pages[variant.key] = path
    return pages


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def variant_render(variant: Variant) -> Path:
    matches = list(VARIANT_RENDERS.glob(f"{variant.key.lower()}-*.png"))
    if len(matches) != 1:
        raise RuntimeError(f"expected one render for {variant.key}, found {len(matches)}")
    return matches[0]


def board_html(
    *,
    title: str,
    subtitle: str,
    variants: tuple[Variant, ...],
    columns: int,
    recommendation: str,
) -> str:
    font = (QUICKSTART.parent / "assembly" / "cards" / "fonts" /
            "IBMPlexSans-400-700-normal-latin.woff2").resolve().as_uri()
    cards = []
    for variant in variants:
        colors = ""
        note = variant.note
        if variant.key.startswith("F"):
            colors = swatch(variant.field) + swatch(variant.motion)
            note = f"{variant.field} / {variant.motion} - {variant.note}"
        elif variant.key.startswith("P"):
            colors = swatch(variant.paper)
            note = f"{variant.paper} - {variant.note}"
        elif variant.key.startswith("C"):
            colors = swatch(variant.field) + swatch(variant.paper) + swatch(variant.motion)
        elif variant.key.startswith("N"):
            colors = swatch(variant.field) + swatch(variant.motion)
        image_uri = variant_render(variant).resolve().as_uri()
        cards.append(
            f"""
            <article class="card">
              <div class="sheet-frame"><img src="{image_uri}" alt=""></div>
              <div class="meta">
                <div class="meta-title"><b>{escape(variant.key)}</b>
                  <strong>{escape(variant.name)}</strong>{colors}</div>
                <div class="meta-note">{escape(note)}</div>
              </div>
            </article>
            """
        )
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><style>
@font-face {{ font-family: "IBM Plex Sans"; font-style: normal; font-weight: 400 700;
  font-display: block; src: url("{font}") format("woff2"); }}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 5700px; height: 3900px; overflow: hidden; background: #121522; }}
body {{ color: #f8fafc; font-family: "IBM Plex Sans", Arial, sans-serif; }}
.board {{ width: 5700px; height: 3900px; padding: 128px 154px 138px; display: flex;
  flex-direction: column; }}
.head {{ height: 438px; display: grid; grid-template-columns: 1fr 1700px; gap: 180px;
  align-items: end; border-bottom: 4px solid rgb(255 255 255 / 12%); padding-bottom: 74px; }}
.kicker {{ color: #ef5966; font-size: 50px; font-weight: 700; letter-spacing: 13px;
  text-transform: uppercase; }}
h1 {{ margin-top: 24px; font-size: 144px; font-weight: 700; line-height: .95;
  letter-spacing: -4px; }}
.head-copy {{ color: #b9c1d1; font-size: 49px; line-height: 1.32; }}
.head-copy strong {{ color: #fff; font-weight: 650; }}
.grid {{ flex: 1; display: grid; justify-content: center; align-content: center; }}
.grid.cols-4 {{ grid-template-columns: repeat(4, 1260px); gap: 120px 72px; }}
.grid.cols-3 {{ grid-template-columns: repeat(3, 1400px); gap: 54px 76px; }}
.card {{ min-width: 0; padding: 20px; border: 2px solid rgb(255 255 255 / 11%);
  border-radius: 30px; background: #1b1f2f; box-shadow: 0 20px 48px rgb(0 0 0 / 22%); }}
.sheet-frame {{ overflow: hidden; border-radius: 12px; background: #fff; box-shadow:
  0 0 0 2px rgb(255 255 255 / 20%); }}
.sheet-frame img {{ display: block; width: 100%; height: auto; aspect-ratio: 19 / 13;
  object-fit: cover; }}
.meta {{ height: 128px; padding: 20px 8px 0; overflow: hidden; }}
.meta-title {{ display: flex; align-items: center; gap: 15px; white-space: nowrap; }}
.meta-title b {{ color: #ef5966; font-size: 37px; letter-spacing: 1px; }}
.meta-title strong {{ overflow: hidden; color: #fff; font-size: 37px; line-height: 1;
  text-overflow: ellipsis; }}
.meta-note {{ margin-top: 13px; overflow: hidden; color: #9ca6b8; font-size: 27px;
  line-height: 1; text-overflow: ellipsis; white-space: nowrap; }}
.swatch {{ width: 32px; height: 32px; flex: none; border: 2px solid rgb(255 255 255 / 32%);
  border-radius: 50%; background: var(--swatch); }}
</style></head><body><main class="board">
  <header class="head"><div><div class="kicker">Quick Start study</div><h1>{escape(title)}</h1></div>
    <div class="head-copy">{escape(subtitle)}<br><strong>{escape(recommendation)}</strong></div></header>
  <section class="grid cols-{columns}">{''.join(cards)}</section>
</main></body></html>"""


def swatch(color: str) -> str:
    return f'<i class="swatch" style="--swatch:{escape(color)}"></i>'


def write_deck_pages(variant_pages: dict[str, Path]) -> None:
    boards = (
        (
            "01-field-colors.html",
            board_html(
                title="Panel fields",
                subtitle="Only the six action fields and their matching cue color change.",
                variants=FIELDS,
                columns=4,
                recommendation="F2 Harbor Mist has the strongest overall balance.",
            ),
        ),
        (
            "02-paper-colors.html",
            board_html(
                title="Paper and center",
                subtitle="The center and every separating seam share one paper color.",
                variants=PAPERS,
                columns=3,
                recommendation="P1 Warm Porcelain is the strongest light direction.",
            ),
        ),
        (
            "03-center-lockups.html",
            board_html(
                title="Center lockups",
                subtitle="The action ring and colors stay fixed; only the identity field changes.",
                variants=LOCKUPS,
                columns=4,
                recommendation="L3 reads fastest; L4 has the clearest authored character.",
            ),
        ),
        (
            "04-composed-directions.html",
            board_html(
                title="Composed directions",
                subtitle="Six complete systems combine the strongest and most revealing choices.",
                variants=COMPOSED,
                columns=3,
                recommendation="C5 Warm Clear follows the current preferred combination.",
            ),
        ),
        (
            "05-step-numbers.html",
            board_html(
                title="Step numbers",
                subtitle="C1's Purpose First lockup and F5 Warm Stone stay fixed.",
                variants=NUMBERS,
                columns=4,
                recommendation="N1 is the clean baseline; N3 and N5 add more character.",
            ),
        ),
    )
    for name, page in boards:
        (DECK_PAGES / name).write_text(page)
    for index, variant in enumerate(COMPOSED, start=6):
        shutil.copyfile(
            variant_pages[variant.key],
            DECK_PAGES / f"{index:02d}-{variant.key.lower()}-{slug(variant.name)}.html",
        )
    number_lookup = {variant.key: variant for variant in NUMBERS}
    for index, key in enumerate(NUMBER_FINALISTS, start=6 + len(COMPOSED)):
        variant = number_lookup[key]
        shutil.copyfile(
            variant_pages[key],
            DECK_PAGES / f"{index:02d}-{key.lower()}-{slug(variant.name)}.html",
        )


def bind_pdf() -> None:
    from pypdf import PdfReader, PdfWriter

    page_pdfs = sorted(DECK_RENDERS.glob("*.pdf"))
    expected_pages = 5 + len(COMPOSED) + len(NUMBER_FINALISTS)
    if len(page_pdfs) != expected_pages:
        raise RuntimeError(f"expected {expected_pages} PDF pages, found {len(page_pdfs)}")
    FINAL_PDF.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for page in page_pdfs:
        writer.append(str(page))
    writer.compress_identical_objects()
    writer.add_metadata(
        {
            "/Title": "Home Soda Machine Quick Start visual variations",
            "/Author": "",
            "/Creator": "",
            "/Producer": "",
        }
    )
    temporary = FINAL_PDF.with_suffix(".pdf.tmp")
    with temporary.open("wb") as stream:
        writer.write(stream)
    temporary.replace(FINAL_PDF)
    check = PdfReader(str(FINAL_PDF))
    if len(check.pages) != len(page_pdfs):
        raise RuntimeError("bound PDF page count changed on reopen")


def write_preview() -> None:
    from PIL import Image

    source = DECK_RENDERS / "04-composed-directions.png"
    with Image.open(source) as image:
        preview = image.convert("RGB")
        preview.thumbnail((2850, 1950), Image.Resampling.LANCZOS)
        preview.save(PREVIEW, format="PNG", optimize=True)
    source = DECK_RENDERS / "05-step-numbers.png"
    with Image.open(source) as image:
        preview = image.convert("RGB")
        preview.thumbnail((2850, 1950), Image.Resampling.LANCZOS)
        preview.save(NUMBER_PREVIEW, format="PNG", optimize=True)


def main() -> int:
    reset_tmp()
    pages = write_variants()
    render_batch(VARIANT_PAGES, VARIANT_RENDERS, dpr=0.36, pdf=False)
    write_deck_pages(pages)
    render_batch(DECK_PAGES, DECK_RENDERS, dpr=0.5, pdf=True)
    bind_pdf()
    write_preview()
    print(f"-> {PREVIEW}")
    print(f"-> {NUMBER_PREVIEW}")
    print(f"-> {FINAL_PDF}")
    shutil.rmtree(TMP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
