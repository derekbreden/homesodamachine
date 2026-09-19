"""Six dimensioned nameplate layouts, with outlined Helvetica and an encoded unit URL."""

from __future__ import annotations

import argparse
import html
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

import cairosvg
import qrcode
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTH, HEIGHT = 104.53, 66.07
FONT = TTFont("/System/Library/Fonts/Helvetica.ttc", fontNumber=1)
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
EM = FONT["head"].unitsPerEm
MARK = ET.parse(ROOT / "brand/mark.svg").getroot()
FAUCET = MARK.find(".//*[@id='faucet']").get("d")
DROP = MARK.find(".//*[@id='drop']").attrib
URL = "https://hosm.us/0001"
QR = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4)
QR.add_data(URL)
QR.make(fit=True)
MATRIX = QR.get_matrix()
BLACK, WHITE = "#1c1e21", "#dededb"
FLAME = [(500, 112), (526.5200000000001, 149.02), (550.08, 184.88), (570.68, 219.57999999999998), (588.32, 253.12), (603.0, 285.5), (614.72, 316.72), (623.48, 346.78), (629.28, 375.68000000000006), (632.12, 403.42), (632.0, 430.0), (631.86, 447.46000000000004), (633.0400000000001, 463.8400000000001), (635.54, 479.14), (639.36, 493.36), (644.5, 506.5), (650.96, 518.56), (658.74, 529.54), (667.84, 539.44), (678.2600000000001, 548.26), (690.0, 556.0), (699.8000000000001, 538.88), (708.4000000000002, 521.9200000000001), (715.8, 505.1199999999999), (722.0, 488.48), (727.0, 472.0), (730.8, 455.68), (733.4000000000001, 439.52), (734.8000000000001, 423.52), (735.0, 407.68), (734.0, 392.0), (752.2, 417.7200000000001), (768.4000000000001, 443.68000000000006), (782.6, 469.88), (794.8, 496.32000000000005), (805.0, 523.0), (813.2, 549.92), (819.4, 577.08), (823.6, 604.48), (825.8000000000001, 632.12), (826.0, 660.0), (821.7800000000001, 693.12), (811.5200000000002, 724.4800000000002), (795.2199999999999, 754.08), (772.8800000000001, 781.9200000000001), (744.5, 808.0), (710.0799999999999, 832.3199999999999), (669.62, 854.88), (623.12, 875.6800000000001), (570.5799999999999, 894.72), (512.0, 912.0), (453.4200000000001, 894.72), (400.8800000000001, 875.6800000000002), (354.37999999999994, 854.8799999999999), (313.92, 832.32), (279.5, 808.0), (251.12000000000003, 781.92), (228.78, 754.08), (212.48000000000002, 724.48), (202.22000000000003, 693.12), (198.0, 660.0), (197.98000000000002, 632.4000000000001), (199.52000000000004, 605.6000000000001), (202.62, 579.5999999999999), (207.27999999999997, 554.4), (213.5, 530.0), (221.27999999999997, 506.40000000000003), (230.62, 483.6), (241.52000000000004, 461.6), (253.98000000000002, 440.40000000000003), (268.0, 420.0), (274.64000000000004, 442.9600000000001), (281.76000000000005, 463.84000000000015), (289.36, 482.64), (297.44, 499.36), (306.0, 514.0), (315.03999999999996, 526.56), (324.56, 537.04), (334.56, 545.44), (345.04, 551.76), (356.0, 556.0), (363.72, 538.48), (370.08000000000004, 520.3200000000002), (375.08, 501.5199999999999), (378.72, 482.08), (381.0, 462.0), (381.91999999999996, 441.28), (381.48, 419.92), (379.68, 397.91999999999996), (376.52, 375.28), (372.0, 352.0), (378.32, 322.24), (386.08000000000004, 293.76000000000005), (395.28, 266.56), (405.91999999999996, 240.64), (418.0, 216.0), (431.52, 192.64), (446.48, 170.56), (462.88, 149.76), (480.71999999999997, 130.23999999999998), (500.0, 112.0)]


def lettering(value, size, tracking=0):
    pen = SVGPathPen(GLYPHS)
    bounds = BoundsPen(GLYPHS)
    advance = 0
    for char in value:
        glyph = GLYPHS[CMAP[ord(char)]]
        transform = (size / EM, 0, 0, -size / EM, advance, 0)
        glyph.draw(TransformPen(pen, transform))
        glyph.draw(TransformPen(bounds, transform))
        advance += glyph.width * size / EM + tracking
    return pen.getCommands(), bounds.bounds


class Plate:
    def __init__(self, key, title, pitch, *, code=None, payload=URL):
        self.key, self.title, self.pitch = key, title, pitch
        self.code = code if code is not None else QR
        self.matrix = self.code.get_matrix()
        self.payload = payload
        self.elements, self.bounds = [], []

    def text(self, value, x, y, size=2.8, align="left", tracking=0.08, fill=WHITE):
        path, (x0, y0, x1, y1) = lettering(value, size, tracking)
        width, height = x1 - x0, y1 - y0
        if align == "center":
            x -= width / 2
        self.elements.append(f'<g aria-label="{html.escape(value, quote=True)}" '
                             f'transform="translate({x-x0:.5f} {y-y0:.5f})" fill="{fill}">'
                             f'<path d="{path}"/></g>')
        self.bounds.append((value, x, y, width, height))
        return width, height

    def logo(self, x, y, height):
        scale = height / 688
        self.elements.append(f'<g fill="{WHITE}" transform="translate({x} {y}) '
                             f'scale({scale}) translate(-184 -160)">'
                             f'<path d="{FAUCET}"/>'
                             f'<circle cx="{DROP["cx"]}" cy="{DROP["cy"]}" '
                             f'r="{DROP["r"]}"/></g>')
        self.bounds.append(("faucet mark", x, y, 656 * scale, height))

    def hazard(self, x, y, size=2.8, align="left", fill=WHITE):
        _, bounds = lettering("FLAMMABLE REFRIGERANT", size, 0.08)
        width = bounds[2] - bounds[0]
        cap = lettering("H", size)[1][3] - lettering("H", size)[1][1]
        flame_width, gap = cap * 628 / 800, 1.2
        if align == "center":
            x -= (flame_width + gap + width) / 2
        outline = " ".join(f'{px:.3f},{py:.3f}' for px, py in FLAME)
        self.elements.append(f'<g fill="{fill}" transform="translate({x} {y}) '
                             f'scale({cap/800}) translate(-198 -112)">'
                             f'<polygon points="{outline}"/></g>')
        self.bounds.append(("flame", x, y, flame_width, cap))
        self.text("FLAMMABLE REFRIGERANT", x + flame_width + gap, y, size, fill=fill)

    def qr(self, x, y, light=False):
        count = len(self.matrix)
        side = count * self.pitch
        path = " ".join(f'M{col},{row}h1v1h-1z' for row, cells in enumerate(self.matrix)
                        for col, filled in enumerate(cells) if filled)
        self.elements.append(f'<g class="qr {"qr-light" if light else "qr-reverse"}" '
                             f'transform="translate({x} {y}) scale({self.pitch})">'
                             f'<rect class="qr-ground" width="{count}" height="{count}" '
                             f'fill="{WHITE if light else BLACK}"/>'
                             f'<path class="qr-modules" d="{path}" '
                             f'fill="{BLACK if light else WHITE}"/></g>')
        self.bounds.append(("QR including quiet zone", x, y, side, side))

    def standard_brand(self):
        cap = lettering("HOME", 10.2)[1][3] - lettering("HOME", 10.2)[1][1]
        stack_h = cap * 3 + 2.8 * 2
        self.logo(12.95, 4.5 + (stack_h - 28) / 2, 28)
        for i, value in enumerate(("HOME", "SODA", "MACHINE")):
            self.text(value, 45.15, 4.5 + i * (cap + 2.8), 10.2, tracking=0)

    def detail_block(self, x, y, align="left", step=3.4):
        for i, value in enumerate(("SERIAL  0001", "120V 60Hz 5A 600W",
                                   "120V 60Hz ONLY", "NOT FOR 240V")):
            self.text(value, x, y + i * step, align=align)
        self.hazard(x, y + 4 * step, align=align)

    def svg(self):
        screws = []
        for x in (6.9, WIDTH - 6.9):
            screws.append(f'<g transform="translate({x} {HEIGHT/2})">'
                          '<circle r="2.9" fill="#0b0c0e" stroke="#5d6064" stroke-width="0.16"/>'
                          '<circle r="2.3" fill="#25272a"/>'
                          '<path d="M-1.15,-0.664 0,-1.328 1.15,-0.664 1.15,0.664 '
                          '0,1.328 -1.15,0.664Z" fill="#08090a"/></g>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" class="nameplate" '
                f'width="{WIDTH}mm" height="{HEIGHT}mm" viewBox="0 0 {WIDTH} {HEIGHT}" '
                f'role="img" aria-label="{self.key}: {self.title}. Unit 0001 nameplate.">'
                f'<title>{self.key} · {self.title}</title>'
                f'<desc>{WIDTH} by {HEIGHT} millimetres. QR encodes {self.payload}. '
                f'{self.pitch:.2f} millimetre modules, four-module quiet zone.</desc>'
                f'<rect x="0.12" y="0.12" width="{WIDTH-.24}" height="{HEIGHT-.24}" '
                f'rx="3" fill="{BLACK}" stroke="#686a6d" stroke-width="0.24"/>'
                + "".join(screws + self.elements) + '</svg>')

    def audit(self):
        for label, x, y, width, height in self.bounds:
            assert min(x, y, WIDTH-x-width, HEIGHT-y-height) >= 2, (self.key, "edge", label)
            for screw_x in (6.9, WIDTH - 6.9):
                dx = max(x - screw_x, 0, screw_x - (x + width))
                dy = max(y - HEIGHT/2, 0, HEIGHT/2 - (y + height))
                assert math.hypot(dx, dy) >= 3.9, (self.key, "screw", label)
        for i, a in enumerate(self.bounds):
            for b in self.bounds[i+1:]:
                if (max(a[1], b[1]) < min(a[1]+a[3], b[1]+b[3]) - 0.01 and
                        max(a[2], b[2]) < min(a[2]+a[4], b[2]+b[4]) - 0.01):
                    raise ValueError((self.key, "overlap", a[0], b[0]))


def layouts():
    a = Plate("A", "Lower right", 0.60)
    a.standard_brand()
    a.text("hosm.us/0001", 14, 39.4, 5.5, tracking=0)
    a.detail_block(14, 47.0, step=3.35)
    a.qr(76, 42)

    b = Plate("B", "Upper corner", 0.56)
    b.logo(12, 5.7, 26)
    for i, word in enumerate(("HOME", "SODA", "MACHINE")):
        b.text(word, 42, 5 + i * 9.7, 9.6, tracking=0)
    b.qr(81.2, 4.2)
    b.text("hosm.us/0001", WIDTH/2, 38.8, 5.5, align="center", tracking=0)
    b.detail_block(WIDTH/2, 47, align="center", step=3.35)

    c = Plate("C", "Serial group", 0.60)
    c.standard_brand()
    c.qr(12, 41.4)
    c.text("SERIAL  0001", 37, 40.8, 5.8, tracking=0.06)
    c.text("hosm.us/0001", 37, 47.4, 4.3, tracking=0)
    c.text("120V 60Hz 5A 600W", 37, 53.2)
    c.text("120V 60Hz ONLY · NOT FOR 240V", 37, 56.6)
    c.hazard(37, 60)

    d = Plate("D", "Right column", 0.70)
    d.logo(12, 6.0, 22)
    for i, word in enumerate(("HOME", "SODA", "MACHINE")):
        d.text(word, 36.5, 5.6 + i * 8.2, 7.0, tracking=0)
    d.elements.append(f'<path d="M71,5V61" stroke="{WHITE}" stroke-width="0.3"/>')
    d.qr(76.0, 4.3)
    d.text("hosm.us/0001", 86.5, 37.6, 3.1, align="center", tracking=0)
    d.text("SERIAL", 86.5, 46.0, 2.8, align="center")
    d.text("0001", 86.5, 51.5, 9.4, align="center", tracking=0)
    for i, value in enumerate(("120V 60Hz 5A 600W", "120V 60Hz ONLY", "NOT FOR 240V")):
        d.text(value, 14, 40 + i * 4.3)
    d.hazard(14, 57)

    e = Plate("E", "White footer", 0.60)
    e.standard_brand()
    e.elements.append(f'<rect x="11" y="39" width="83" height="24" rx="0.8" fill="{WHITE}"/>')
    e.qr(11.9, 41.1, light=True)
    e.text("hosm.us/0001", 36, 41.3, 5.0, tracking=0, fill=BLACK)
    e.text("SERIAL  0001", 36, 47.0, fill=BLACK)
    e.text("120V 60Hz 5A 600W", 36, 50.5, fill=BLACK)
    e.text("120V 60Hz ONLY · NOT FOR 240V", 36, 54.0, fill=BLACK)
    e.hazard(36, 58.5, fill=BLACK)

    f = Plate("F", "Centered", 0.60)
    f.logo(20.5, 5.5, 18)
    f.text("HOME SODA", 42.5, 5.7, 7.2, tracking=0)
    f.text("MACHINE", 42.5, 15.2, 7.2, tracking=0)
    f.text("SERIAL  0001", WIDTH/2, 27.2, align="center")
    f.qr((WIDTH - 19.8)/2, 32.2)
    f.text("120V 60Hz", 14, 39)
    f.text("5A 600W", 14, 42.8)
    f.text("120V 60Hz ONLY", 71, 39)
    f.text("NOT FOR 240V", 71, 42.8)
    f.text("hosm.us/0001", WIDTH/2, 55, 4.8, align="center", tracking=0)
    f.hazard(WIDTH/2, 61, align="center")
    return [a, b, c, d, e, f]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fragment-dir", type=Path)
    parser.add_argument("--png-dir", type=Path)
    args = parser.parse_args()
    plates = layouts()
    figures = []
    manifest = []
    for plate in plates:
        plate.audit()
        name = f'{plate.key.lower()}-{plate.title.lower().replace(" ", "-")}'
        svg = plate.svg()
        (HERE / f"{name}.svg").write_text(svg + "\n")
        if args.png_dir:
            args.png_dir.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=str(args.png_dir / f"{name}.png"),
                            output_width=1254, output_height=793)
        figures.append(f'<figure data-layout="{plate.key}"><figcaption>{plate.key} · '
                       f'{plate.title}</figcaption>{svg}</figure>')
        manifest.append({"key": plate.key, "title": plate.title, "module_mm": plate.pitch,
                         "active_qr_mm": 25 * plate.pitch, "qr_with_margin_mm": 33 * plate.pitch})
    (HERE / "layouts.json").write_text(json.dumps({"url": URL, "width_mm": WIDTH,
                        "height_mm": HEIGHT, "qr_version": QR.version, "error_correction": "M",
                        "quiet_zone_modules": 4, "layouts": manifest}, indent=2) + "\n")
    fragment = (HERE / "comparison.template.html").read_text().replace("<!-- PLATES -->", "\n".join(figures))
    assert len(fragment.encode()) < 1_000_000
    (HERE / "nameplate-qr.html").write_text(fragment)
    if args.fragment_dir:
        args.fragment_dir.mkdir(parents=True, exist_ok=True)
        (args.fragment_dir / "nameplate-qr.html").write_text(fragment)
    print(f"Six layouts: fit, screw clearance and QR quiet-zone bounds checked; {len(fragment.encode()):,} bytes.")


if __name__ == "__main__":
    main()
