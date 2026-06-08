#!/usr/bin/env python3
"""Render the Flavor N placeholder logos to images/flavor_N.png.

Each flavor is its own soda brand named "Flavor N": its own field colour, typeface,
layout, and motif.

Full pipeline (also regenerates firmware headers + iOS bundle copies):
    tools/build_flavor_assets.sh
This step alone (project venv has PIL + numpy):
    tools/cad-venv/bin/python tools/gen_flavor_placeholders.py [--preview]
"""

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PROJECT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT / "images"

SVG = 1024          # design coordinate space
SS = 3              # supersample factor
MASTER = 512        # saved master PNG size
NAVY = (0x1a, 0x1a, 0x2e)   # == display THEME_BG / iOS Theme.background

FONTS = {
    "didot":       ("/System/Library/Fonts/Supplemental/Didot.ttc", 2),          # Bold
    "copperplate": ("/System/Library/Fonts/Supplemental/Copperplate.ttc", 2),    # Bold
    "futura":      ("/System/Library/Fonts/Supplemental/Futura.ttc", 2),         # Bold
    "futura_xb":   ("/System/Library/Fonts/Supplemental/Futura.ttc", 4),         # Condensed ExtraBold
    "rounded":     ("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf", 0),
    "phosphate":   ("/System/Library/Fonts/Supplemental/Phosphate.ttc", 1),      # Solid
    "phosphate_in":("/System/Library/Fonts/Supplemental/Phosphate.ttc", 0),      # Inline
}


def font(key, size):
    path, idx = FONTS[key]
    return ImageFont.truetype(path, int(size), index=idx)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ── Gradient fields ──────────────────────────────────────────────────────────

def linear_field(size, p0, p1, stops):
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    t = np.clip(((xs - p0[0]) * dx + (ys - p0[1]) * dy) / (dx * dx + dy * dy), 0, 1)
    locs = np.linspace(0, 1, len(stops))
    rgb = [np.interp(t, locs, [hx(c)[k] for c in stops]) for k in range(3)]
    return Image.fromarray(np.dstack(rgb).astype(np.uint8), "RGB").convert("RGBA")


def radial_field(size, center, radius, stops):
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.clip(np.sqrt((xs - center[0]) ** 2 + (ys - center[1]) ** 2) / radius, 0, 1)
    locs = np.linspace(0, 1, len(stops))
    rgb = [np.interp(d, locs, [hx(c)[k] for c in stops]) for k in range(3)]
    return Image.fromarray(np.dstack(rgb).astype(np.uint8), "RGB").convert("RGBA")


def vignette(img, strength=0.35):
    size = img.size[0]
    ys, xs = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.sqrt((xs - size / 2) ** 2 + (ys - size / 2) ** 2) / (size / 2)
    a = (np.clip((d - 0.55) / 0.45, 0, 1) ** 1.6 * strength * 255).astype(np.uint8)
    v = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    v.putalpha(Image.fromarray(a))
    img.alpha_composite(v)


# ── Text ─────────────────────────────────────────────────────────────────────

def text_strip(text, fnt, fill, tracking=0):
    """Render text with optional letter-spacing to a tight RGBA image."""
    asc, desc = fnt.getmetrics()
    boxes = [fnt.getbbox(ch) for ch in text]
    widths = [b[2] - b[0] for b in boxes]
    total = sum(widths) + tracking * (len(text) - 1)
    strip = Image.new("RGBA", (max(1, int(total) + 4), asc + desc + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    x = 2
    for ch, w, b in zip(text, widths, boxes):
        d.text((x - b[0], 2), ch, font=fnt, fill=fill)
        x += w + tracking
    return strip.crop(strip.getbbox())


def place(img, strip, center, s, rotate=0.0, shadow=None):
    """Composite a text strip centred at `center` (1024-space), optional tilt + soft shadow."""
    if shadow is not None:
        col, blur, off = shadow
        sh = Image.new("RGBA", strip.size, (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", strip.size, col), (0, 0), strip)
        if rotate:
            sh = sh.rotate(rotate, expand=True, resample=Image.BICUBIC)
        sh = _grow(sh, int(blur * s) + 1).filter(ImageFilter.GaussianBlur(blur * s))
        _paste_center(img, sh, center, s, (off[0] * s, off[1] * s))
    layer = strip.rotate(rotate, expand=True, resample=Image.BICUBIC) if rotate else strip
    _paste_center(img, layer, center, s)


def _grow(im, pad):
    out = Image.new("RGBA", (im.size[0] + 2 * pad, im.size[1] + 2 * pad), (0, 0, 0, 0))
    out.alpha_composite(im, (pad, pad))
    return out


def _paste_center(img, layer, center, s, offset=(0, 0)):
    cx, cy = center[0] * s + offset[0], center[1] * s + offset[1]
    img.alpha_composite(layer, (int(cx - layer.size[0] / 2), int(cy - layer.size[1] / 2)))


def _glyph(ch, fnt, fill):
    b = fnt.getbbox(ch)
    im = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), ch, font=fnt, fill=fill)
    return im


def arc_text(img, text, fnt, center, radius, fill, s, flip=False, gap_deg=1.5):
    """Set `text` along a circular arc — top of the circle, or `flip` for the bottom."""
    cx, cy, R = center[0] * s, center[1] * s, radius * s
    angs = [(fnt.getbbox(c)[2] - fnt.getbbox(c)[0]) / R + math.radians(gap_deg) for c in text]
    span = sum(angs)
    a = (-math.pi / 2 - span / 2) if not flip else (math.pi / 2 + span / 2)
    for ch, da in zip(text, angs):
        am = a + da / 2 if not flip else a - da / 2
        g = _glyph(ch, fnt, fill)
        rot = -(math.degrees(am) + 90) if not flip else -(math.degrees(am) - 90)
        g = g.rotate(rot, expand=True, resample=Image.BICUBIC)
        x, y = cx + R * math.cos(am), cy + R * math.sin(am)
        img.alpha_composite(g, (int(x - g.size[0] / 2), int(y - g.size[1] / 2)))
        a = a + da if not flip else a - da


# ── Shapes ───────────────────────────────────────────────────────────────────

def ring(draw, c, r, width, fill, s):
    draw.ellipse([(c[0] - r) * s, (c[1] - r) * s, (c[0] + r) * s, (c[1] + r) * s],
                 outline=fill, width=max(1, int(width * s)))


def star4(draw, c, r, fill, s, waist=0.30):
    cx, cy, r = c[0] * s, c[1] * s, r * s
    w = r * waist
    draw.polygon([(cx, cy - r), (cx + w, cy - w), (cx + r, cy), (cx + w, cy + w),
                  (cx, cy + r), (cx - w, cy + w), (cx - r, cy), (cx - w, cy - w)], fill=fill)


def sunburst(size, s, center, r, n, col_a, col_b):
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy, R = center[0] * s, center[1] * s, r * s
    for i in range(n):
        a0, a1 = (i / n) * 2 * math.pi, ((i + 1) / n) * 2 * math.pi
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))],
                  fill=col_a if i % 2 == 0 else col_b)
    return layer


# ════════════════════════════════════════════════════════════════════════════
#  Per-flavor designs
# ════════════════════════════════════════════════════════════════════════════

def design_1(size, s):
    """Cola: red radial field, Didot numeral centred in a Copperplate seal."""
    img = radial_field(size, (430, 380), 760, ["#ff7a6b", "#e0314f", "#7d1330"])
    cream = (255, 233, 201, 255)
    sh = ((60, 6, 24, 150), 7, (0, 5))
    d = ImageDraw.Draw(img)
    ring(d, (512, 512), 470, 3, (255, 233, 201, 90), s)
    ring(d, (512, 512), 452, 9, cream, s)
    ring(d, (512, 512), 434, 3, (255, 233, 201, 120), s)
    arc_text(img, "FLAVOR", font("copperplate", 74), (512, 512), 392, cream, s, gap_deg=3)
    arc_text(img, "ORIGINAL", font("copperplate", 52), (512, 512), 392, (255, 233, 201, 225), s, flip=True, gap_deg=4)
    for ang in (0, math.pi):  # seal dots at 3 and 9 o'clock
        star4(d, (512 + 392 * math.cos(ang), 512 + 392 * math.sin(ang)), 14, cream, s)
    place(img, text_strip("1", font("didot", 500), cream), (512, 512), s, shadow=sh)
    vignette(img, 0.45)
    return img


def design_2(size, s):
    """Lemon-lime: lime field, Futura on a tilt, citrus-wedge, sparkles, bubbles."""
    img = linear_field(size, (120, 120), (920, 940), ["#e6fb8a", "#74d64f", "#0d9a5f"])
    white = (255, 255, 255, 255)
    sh = ((10, 70, 30, 150), 6, (0, 5))
    d = ImageDraw.Draw(img)
    ring(d, (812, 812), 132, 6, (255, 255, 255, 55), s)          # faint citrus cross-section
    for k in range(8):
        ang = k / 8 * 2 * math.pi
        d.line([(812 * s, 812 * s), ((812 + 132 * math.cos(ang)) * s, (812 + 132 * math.sin(ang)) * s)],
               fill=(255, 255, 255, 45), width=max(1, int(3 * s)))
    for (cx, cy, r) in [(250, 250, 30), (800, 250, 18), (235, 815, 15)]:
        star4(d, (cx, cy), r, (255, 255, 255, 235), s)
    for (cx, cy, r, a) in [(360, 650, 22, 90), (700, 470, 16, 80)]:   # bubbles
        ring(d, (cx, cy), r, 5, (255, 255, 255, a), s)
    place(img, text_strip("FLAVOR", font("futura", 92), white, tracking=18), (470, 372), s, rotate=7, shadow=sh)
    place(img, text_strip("2", font("futura_xb", 580), white), (520, 600), s, rotate=7, shadow=sh)
    vignette(img, 0.26)
    return img


def design_3(size, s):
    """Orange: sunburst field, Arial Rounded numeral, FLAVOR on a pill banner."""
    img = radial_field(size, (512, 470), 720, ["#ffe07a", "#ff9e2c", "#e8531f"])
    img.alpha_composite(sunburst(size, s, (512, 545), 780, 24, (255, 255, 255, 34), (255, 255, 255, 0)))
    sh = ((150, 55, 0, 160), 7, (0, 6))
    word = text_strip("FLAVOR", font("rounded", 66), (228, 84, 26, 255), tracking=10)
    pw, ph = word.size
    bw, bh = pw + ph, ph + ph // 2
    banner = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    ImageDraw.Draw(banner).rounded_rectangle([0, 0, bw - 1, bh - 1], radius=bh // 2, fill=(255, 255, 255, 255))
    banner.alpha_composite(word, ((bw - pw) // 2, (bh - ph) // 2))
    _paste_center(img, banner, (512, 348), s)
    place(img, text_strip("3", font("rounded", 540), (255, 255, 255, 255)), (512, 605), s, shadow=sh)
    vignette(img, 0.30)
    return img


def design_4(size, s):
    """Grape: purple field, Phosphate numeral, editorial rules, stars, diamond."""
    img = radial_field(size, (512, 460), 760, ["#9a80f0", "#5d39b8", "#220a42"])
    lav = (238, 231, 255, 255)
    sh = ((10, 4, 30, 160), 8, (0, 6))
    d = ImageDraw.Draw(img)
    c, r = 512 * s, 360 * s
    diamond = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(diamond).polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)],
                                    outline=(238, 231, 255, 110), width=max(1, int(2.5 * s)))
    img.alpha_composite(diamond)
    for (cx, cy, rr) in [(512, 140, 15), (250, 512, 11), (774, 512, 11), (385, 882, 8), (642, 884, 10)]:
        star4(d, (cx, cy), rr, (255, 255, 255, 220), s)
    place(img, text_strip("FLAVOR", font("phosphate", 76), lav, tracking=18), (512, 372), s, shadow=sh)
    for x0, x1 in [(150, 286), (738, 874)]:
        d.line([(x0 * s, 372 * s), (x1 * s, 372 * s)], fill=(238, 231, 255, 150), width=max(1, int(2 * s)))
    place(img, text_strip("4", font("phosphate_in", 540), (255, 255, 255, 255)), (512, 600), s, shadow=sh)
    vignette(img, 0.40)
    return img


FLAVORS = [
    {"file": "flavor_1.png", "design": design_1},
    {"file": "flavor_2.png", "design": design_2},
    {"file": "flavor_3.png", "design": design_3},
    {"file": "flavor_4.png", "design": design_4},
]


def render(flavor, out_size):
    size = out_size * SS
    img = flavor["design"](size, size / SVG).convert("RGB")
    return img.resize((out_size, out_size), Image.LANCZOS)


# ── Preview contact sheet (one row per flavor: square / circle / RP2040) ──────

def circle_crop(img, bg=NAVY):
    out = Image.new("RGB", img.size, bg)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, img.size[0] - 1, img.size[1] - 1], fill=255)
    out.paste(img, (0, 0), mask)
    return out


def contact_sheet(masters):
    pad, cell, lab = 16, 240, 22
    cols, headers = [cell, cell, 128], ["square 240", "circle 240 (S3/iOS)", "128×115 (RP2040)"]
    row_h = cell + lab + pad
    sheet = Image.new("RGB", (pad + sum(c + pad for c in cols), pad + len(masters) * row_h), (12, 12, 20))
    d = ImageDraw.Draw(sheet)
    sf = font("futura", 15)
    xs, x = [], pad
    for c in cols:
        xs.append(x); x += c + pad
    for cx, h in zip(xs, headers):
        d.text((cx, 2), h, font=sf, fill=(150, 150, 160))
    for r, m in enumerate(masters):
        y = pad + r * row_h + lab
        sq = m.resize((cell, cell), Image.LANCZOS)
        for cx, im in zip(xs, [sq, circle_crop(sq), m.resize((128, 115), Image.LANCZOS)]):
            sheet.paste(im, (cx, y))
    return sheet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    args = ap.parse_args()

    IMAGES_DIR.mkdir(exist_ok=True)
    masters = []
    print(f"Rendering {len(FLAVORS)} flavor logos ({MASTER}×{MASTER})...")
    for fl in FLAVORS:
        m = render(fl, MASTER)
        m.save(IMAGES_DIR / fl["file"])
        masters.append(m)
        print(f"  images/{fl['file']}")
    if args.preview:
        out = PROJECT / "tools" / "flavor_preview.png"
        contact_sheet(masters).save(out)
        print(f"  preview: {out.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
