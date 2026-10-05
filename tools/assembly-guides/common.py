"""Shared vector page furniture for hand-authored Letter shop guides.

Manual document tools live outside the hardware generator inventory. Typography,
print calibration and drawing primitives are shared; operations and pictures are
owned by each guide. No geometry or fabrication source is imported here.
"""
from __future__ import annotations
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
ROOT = Path(__file__).resolve().parents[2]
W, H = 612, 792
CONTENT_SCALE = .98
BLEED_OVERHANG = 18
BAND_INSET = 24
INK, BLUE, ORANGE = "#202337", "#1749D1", "#E95A2C"
PAPER, ICE, STEEL = "#FCFCFA", "#EAF0FC", "#E4E8EE"
MUTED, RULE, COPPER, GLOVE = "#606A78", "#DCE2EB", "#B8722C", "#ECD5AA"
FONT_DIR = ROOT / "hardware/install-guide/fonts"
for face_name, filename in [("Plex", "Plex-Regular.ttf"),
                            ("PlexSemi", "Plex-Semibold.ttf"),
                            ("PlexBold", "Plex-Bold.ttf")]:
    pdfmetrics.registerFont(TTFont(face_name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily("Plex", normal="Plex", bold="PlexBold",
                              italic="Plex", boldItalic="PlexBold")


def color(value):
    return HexColor(value)


def box(c, x, y, width, height, fill=PAPER, stroke=None, radius=0):
    c.setFillColor(color(fill))
    c.setStrokeColor(color(stroke or fill))
    c.setLineWidth(0.7)
    if radius:
        c.roundRect(x, H - y - height, width, height, radius,
                    fill=1, stroke=bool(stroke))
    else:
        c.rect(x, H - y - height, width, height, fill=1, stroke=bool(stroke))


def text(c, value, x, y, size=12, font="Plex", fill=INK, align="left"):
    c.setFont(font, size)
    c.setFillColor(color(fill))
    getattr(c, {"left": "drawString", "center": "drawCentredString",
                "right": "drawRightString"}[align])(x, H - y, value)


def paragraph(c, value, x, y, width, size=11.4, leading=None, fill=INK,
              max_height=None):
    style = ParagraphStyle("copy", fontName="Plex", fontSize=size,
                           leading=leading or size * 1.22, textColor=color(fill))
    p = Paragraph(value, style)
    _, height = p.wrap(width, H)
    if max_height and height > max_height:
        raise ValueError(f"Text exceeds its box: {value}")
    p.drawOn(c, x, H - y - height)
    return height


class Art:
    """Top-left coordinates for vector pictures; text remains upright."""

    def __init__(self, c, x, y, scale=1):
        self.c, self.x, self.y, self.scale = c, x, y, scale

    def __enter__(self):
        self.c.saveState()
        self.c.translate(self.x, H - self.y)
        self.c.scale(self.scale, -self.scale)
        self.c.setLineCap(1)
        self.c.setLineJoin(1)
        return self

    def __exit__(self, *exc):
        self.c.restoreState()

    def shape(self, points, fill=None, stroke=INK, width=1.5, close=True):
        c = self.c
        p = c.beginPath()
        p.moveTo(*points[0])
        for point in points[1:]:
            if len(point) == 2:
                p.lineTo(*point)
            else:
                p.curveTo(*point)
        if close:
            p.close()
        c.setStrokeColor(color(stroke or fill))
        c.setFillColor(color(fill or PAPER))
        c.setLineWidth(width)
        c.drawPath(p, fill=bool(fill), stroke=bool(stroke))

    def line(self, x1, y1, x2, y2, fill=INK, width=1.4, dash=None):
        c = self.c
        c.setStrokeColor(color(fill))
        c.setLineWidth(width)
        c.setDash(dash or [])
        c.line(x1, y1, x2, y2)
        c.setDash([])

    def rect(self, x, y, width, height, fill=STEEL, stroke=INK):
        self.shape([(x, y), (x + width, y), (x + width, y + height),
                    (x, y + height)], fill, stroke)

    def ellipse(self, x, y, width, height, fill=STEEL, stroke=INK, lw=1.5):
        c = self.c
        c.setFillColor(color(fill or PAPER))
        c.setStrokeColor(color(stroke or fill))
        c.setLineWidth(lw)
        c.ellipse(x, y, x + width, y + height, fill=bool(fill), stroke=bool(stroke))

    def label(self, value, x, y, size=10, fill=INK, font="PlexSemi", align="left"):
        c = self.c
        c.saveState()
        c.scale(1, -1)
        c.setFont(font, size)
        c.setFillColor(color(fill))
        getattr(c, {"left": "drawString", "center": "drawCentredString",
                    "right": "drawRightString"}[align])(x, -y, value)
        c.restoreState()

    def arrow(self, x1, y1, x2, y2, fill=BLUE, width=2, head=6):
        self.line(x1, y1, x2, y2, fill, width)
        angle = math.atan2(y2 - y1, x2 - x1)
        self.shape([(x2, y2),
                    (x2 - head * math.cos(angle - .5), y2 - head * math.sin(angle - .5)),
                    (x2 - head * math.cos(angle + .5), y2 - head * math.sin(angle + .5))],
                   fill, None)

    def dim(self, x1, y1, x2, y2, fill=BLUE):
        self.line(x1, y1, x2, y2, fill, .8)
        if x1 == x2:
            for y in [y1, y2]:
                self.line(x1 - 4, y, x1 + 4, y, fill, 1)
        else:
            for x in [x1, x2]:
                self.line(x, y1 - 4, x, y1 + 4, fill, 1)


def badge(c, n, x, y, label, fill=BLUE, size=14):
    box(c, x, y, 22, 22, fill, radius=5)
    text(c, str(n), x + 11, y + 15.5, 12, "PlexBold", PAPER, "center")
    text(c, label, x + 31, y + 16, size, "PlexSemi")


def page_backdrop(c):
    """Paint the bleed independently of the centered instructional layer."""
    bleed = BLEED_OVERHANG
    box(c, -bleed, -bleed, W + 2 * bleed, H + 2 * bleed, PAPER)
    box(c, -bleed, -bleed, W + 2 * bleed, BAND_INSET + bleed, BLUE)
    box(c, W - BAND_INSET, BAND_INSET, BAND_INSET + bleed,
        H - BAND_INSET + bleed, ORANGE)



def header(c, n, title, subtitle, total, category="BENCH INSTRUCTIONS"):
    text(c, f"HOME SODA MACHINE / {category}", 32, 35, 9.5, "PlexSemi", BLUE)
    text(c, f"{n:02d} / {total:02d}", 577, 35, 10, "PlexSemi", MUTED, "right")
    for i, line in enumerate(title.split("\n")):
        text(c, line, 32, 75 + i * 31, 30, "PlexBold")
    last = 75 + (len(title.split("\n")) - 1) * 31
    return paragraph(c, subtitle, 33, last + 14, 540, 13, 16, MUTED, 48)


def footer(c, n, source, link=None):
    box(c, 32, 752, 548, .8, RULE)
    paragraph(c, source, 32, 759, 425, 8.1, 9.5, MUTED, 20)
    text(c, f"LETTER / {n}", 580, 768, 8, "PlexSemi", MUTED, "right")
    if link:
        c.linkURL(link, (32, 15, 580, 38), relative=1)


def panel(c, x, y, width, height):
    box(c, x, y, width, height, "#FFFFFF", RULE, 8)


def begin_page(c):
    page_backdrop(c)
    c.saveState()
    c.translate(W * (1 - CONTENT_SCALE) / 2, H * (1 - CONTENT_SCALE) / 2)
    c.scale(CONTENT_SCALE, CONTENT_SCALE)


def end_page(c):
    c.restoreState()
    c.showPage()


def publish(pdf, guide_dir, title, subtitle, pages, sources, extra=None, write_manifest=True):
    """Commit-ready PDF/thumbnail/catalog sidecar and a source-hash receipt.

    `pdf` is the output/pdf delivery file. `guide_dir` carries the identical
    canonical document served by /drawings. Sources are explicitly selected
    local relative paths; hashing them does not evaluate the appliance build.
    """
    from PIL import Image
    pdf, guide_dir = Path(pdf), Path(guide_dir)
    guide_dir.mkdir(parents=True, exist_ok=True)
    name = pdf.stem
    canonical = guide_dir / pdf.name
    shutil.copyfile(pdf, canonical)
    cover = guide_dir / f"{name}.cover.png"
    import tempfile
    with tempfile.TemporaryDirectory(prefix="hsm-guide-cover-") as scratch:
        prefix = Path(scratch) / "cover"
        subprocess.run(["pdftoppm", "-f", "1", "-singlefile", "-scale-to-x", "800",
                        "-scale-to-y", "-1", "-png", str(pdf), str(prefix)], check=True,
                        capture_output=True)
        with Image.open(prefix.with_suffix(".png")) as im:
            im.convert("RGB").save(cover, optimize=True)
            cover_size = list(im.size)
    (guide_dir / f"{pdf.name}.json").write_text(json.dumps({
        "title": title, "subtitle": subtitle, "pages": pages,
        "cover": cover.name, "cover_size": cover_size,
    }, indent=2) + "\n")
    manifest = {
        "pdf": pdf.name, "pages": pages, "page_inches": [8.5, 11],
        "print_layout": {"content_scale": CONTENT_SCALE, "bleed_overhang_inches": .25,
                         "colored_band_inset_inches": 1/3, "bleed_layer_scale": 1,
                         "media_source": "rear", "print_scaling": "100% / none"},
        "artwork": "vector schematic; dimensions govern; not a full-size template",
        "source_sha256": {str(p): hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                          for p in sources},
        "pdf_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
    }
    if extra:
        manifest.update(extra)
    if write_manifest:
        pdf.with_suffix(".sources.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return canonical
