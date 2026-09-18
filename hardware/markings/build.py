"""Dimensioned refrigerant warning proofs with outlined Helvetica Bold lettering."""

from __future__ import annotations

import html
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.reportLabPen import ReportLabPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONT = TTFont('/System/Library/Fonts/Helvetica.ttc', fontNumber=1)
GLYPHS = FONT.getGlyphSet()
CMAP = FONT.getBestCmap()
CAP_PEN = BoundsPen(GLYPHS)
GLYPHS[CMAP[ord('H')]].draw(CAP_PEN)
CAP_UNITS = CAP_PEN.bounds[3] - CAP_PEN.bounds[1]
CAP = 6.5
WIDTH = 190.0
MARGIN = 6.0
LEADING = 9.0
SYMBOL_HEIGHT = 21.0
SAFETY_CLASS_CAP = 7.2
SYMBOL = ET.parse(HERE / 'ghs02.svg').getroot()


def text_paths(value, cap, x=0.0, y=0.0):
    scale = cap / CAP_UNITS
    bounds, svg = BoundsPen(GLYPHS), SVGPathPen(GLYPHS)
    pdf = ReportLabPen(GLYPHS)
    advance = 0.0
    for char in value:
        glyph = GLYPHS[CMAP[ord(char)]]
        transform = (scale, 0, 0, -scale, advance, 0)
        for pen in (bounds, svg, pdf):
            glyph.draw(TransformPen(pen, transform))
        advance += glyph.width * scale
    x0, y0, x1, y1 = bounds.bounds
    return svg.getCommands(), pdf.path, (x - x0, y - y0), (x1 - x0, y1 - y0)


def width(value, cap=CAP):
    return text_paths(value, cap)[3][0]


def minimum_letter_height(lines):
    heights = []
    for char in set(''.join(lines)):
        if char.isalpha():
            pen = BoundsPen(GLYPHS)
            GLYPHS[CMAP[ord(char)]].draw(pen)
            heights.append((pen.bounds[3] - pen.bounds[1]) * CAP / CAP_UNITS)
    return min(heights)


def wrap(sentence):
    if '\n' in sentence:
        lines = sentence.upper().splitlines()
        assert all(width(line) <= WIDTH - 2 * MARGIN for line in lines)
        return lines
    lines, current = [], ''
    for word in sentence.upper().split():
        candidate = f'{current} {word}'.strip()
        if width(candidate) > WIDTH - 2 * MARGIN:
            assert current, f'Word too wide: {word}'
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


class Label:
    def __init__(self, key, title, signal, sentences, *, symbol=False):
        self.key, self.title, self.signal = key, title, signal
        self.symbol = symbol
        self.lines = [line for sentence in sentences for line in wrap(sentence)]
        self.body_top = 33.0 if symbol else 22.0
        self.height = math.ceil(self.body_top + (len(self.lines) - 1) * LEADING + CAP + MARGIN)
        self.text = [(signal, MARGIN, 9.0, 9.0)]
        if symbol:
            self.text.append(('A3', 165.0, 12.9, SAFETY_CLASS_CAP))
        self.text += [(line, MARGIN, self.body_top + i * LEADING, CAP)
                      for i, line in enumerate(self.lines)]
        self.audit()

    def audit(self):
        assert minimum_letter_height(self.lines) >= 6.4
        boxes = []
        for value, x, y, cap in self.text:
            _, _, _, (w, h) = text_paths(value, cap)
            assert x >= MARGIN and x + w <= WIDTH - MARGIN
            assert y >= MARGIN and y + h <= self.height - MARGIN + 0.2
            assert cap >= 6.4
            boxes.append((value, x, y, w, h))
        if self.symbol:
            boxes.append(('GHS02', 138, 6, SYMBOL_HEIGHT, SYMBOL_HEIGHT))
            assert SAFETY_CLASS_CAP >= SYMBOL_HEIGHT / 3
        for i, a in enumerate(boxes):
            for b in boxes[i + 1:]:
                assert (a[1] + a[3] <= b[1] or b[1] + b[3] <= a[1]
                        or a[2] + a[4] <= b[2] or b[2] + b[4] <= a[2]), (self.key, a[0], b[0])
        return boxes

    def svg(self):
        content = [f'<rect x="0.25" y="0.25" width="{WIDTH-.5}" height="{self.height-.5}" '
                   'rx="2" fill="white" stroke="#161616" stroke-width="0.5"/>']
        for value, x, y, cap in self.text:
            path, _, offset, _ = text_paths(value, cap, x, y)
            content.append(f'<path aria-label="{html.escape(value, quote=True)}" '
                           f'transform="translate({offset[0]} {offset[1]})" d="{path}"/>')
        if self.symbol:
            content.append(symbol_svg(138, 6))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}mm" '
                f'height="{self.height}mm" viewBox="0 0 {WIDTH} {self.height}">'
                f'<title>{self.title}</title><desc>Provisional warning artwork. '
                f'Uppercase body letters have a {CAP} mm H cap height. '
                'See README.md for applicability and installation status.</desc>'
                + ''.join(content) + '</svg>')

    def pdf(self, canvas, x, top):
        canvas.saveState()
        canvas.translate(x * mm, letter[1] - top * mm)
        canvas.scale(mm, -mm)
        canvas.setFillColor(HexColor('#ffffff'))
        canvas.setStrokeColor(HexColor('#161616'))
        canvas.setLineWidth(.5)
        canvas.roundRect(.25, .25, WIDTH-.5, self.height-.5, 2, stroke=1, fill=1)
        for value, tx, ty, cap in self.text:
            draw_text(canvas, value, tx, ty, cap)
        if self.symbol:
            draw_symbol(canvas, 138, 6)
        canvas.restoreState()


def draw_text(canvas, value, x, y, cap):
    _, path, offset, _ = text_paths(value, cap, x, y)
    canvas.saveState()
    canvas.translate(*offset)
    canvas.setFillColor(HexColor('#000000'))
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing
    drawing = Drawing()
    path.fillColor, path.strokeColor = HexColor('#000000'), None
    drawing.add(path)
    renderPDF.draw(drawing, canvas, 0, 0)
    canvas.restoreState()


def symbol_svg(x, y):
    # The source diamond spans 6..573 in its 579-unit viewBox.
    content = ''.join(ET.tostring(child, encoding='unicode') for child in SYMBOL)
    return (f'<g transform="translate({x} {y}) scale({SYMBOL_HEIGHT/567}) '
            f'translate(-6 -6)">{content}</g>')


def draw_symbol(canvas, x, y):
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing
    canvas.saveState()
    canvas.translate(x, y)
    canvas.scale(SYMBOL_HEIGHT/567, SYMBOL_HEIGHT/567)
    canvas.translate(-6, -6)
    for element in SYMBOL:
        pen = ReportLabPen(None)
        parse_path(element.attrib['d'], pen)
        fill = element.get('fill', '#000000')
        fill = {'red': '#ff0000', '#fff': '#ffffff'}.get(fill, fill)
        pen.path.fillColor = HexColor(fill)
        pen.path.strokeColor = None
        drawing = Drawing()
        drawing.add(pen.path)
        renderPDF.draw(drawing, canvas, 0, 0)
    canvas.restoreState()


def labels():
    return [
        Label('a-exterior-service', 'A / Exterior - service and puncture', 'DANGER', [
            'Risk of Fire Or Explosion.',
            'Flammable Refrigerant Used.',
            'To Be Repaired Only By\nTrained Service Personnel.',
            'Do Not Puncture\nRefrigerant Tubing.'
        ], symbol=True),
        Label('b-exterior-disposal', 'B / Exterior - disposal', 'WARNING', [
            'Risk of Fire Or Explosion.',
            'Dispose of Properly In Accordance With Federal Or Local Regulations.',
            'Flammable Refrigerant Used.'
        ]),
        Label('c-compressor-service', 'C / Inside - near compressor', 'DANGER', [
            'Risk Of Fire Or Explosion.',
            'Flammable Refrigerant Used.',
            "Consult Repair Manual/Owner's Guide Before Attempting To Service This Product.",
            'All Safety Precautions\nMust Be Followed.'
        ]),
        Label('d-package-handling', 'D / Packaging - factory-charged unit', 'DANGER', [
            'Risk of Fire or Explosion Due To Flammable Refrigerant Used.',
            'Follow Handling Instructions Carefully In Compliance With National Regulations.'
        ], symbol=True),
        Label('f-exterior-storage', 'F / Exterior - non-fixed unit storage', 'WARNING', [
            'Risk of Fire or Explosion.',
            'Store In A Well-Ventilated Room\nWithout Continuously Operating\nFlames Or Other\nPotential Ignition.'
        ]),
    ]


def page_heading(canvas, page, title):
    canvas.setFillColor(HexColor('#161616'))
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(13 * mm, letter[1] - 16 * mm, title)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(13 * mm, letter[1] - 23 * mm, 'FULL-SIZE FIT PROOF  /  US LETTER  /  PRINT AT 100%, ACTUAL SIZE')
    canvas.setFont('Helvetica', 8)
    canvas.drawString(13 * mm, 17 * mm, 'Provisional marking set. End-use / R-600a acceptance and physical installation remain open.')
    canvas.drawString(13 * mm, 12 * mm, 'Source: EPA SNAP Rule 26, 89 FR 50482-50484. See hardware/markings/README.md.')
    canvas.drawRightString(203 * mm, 7 * mm, f'{page} / 3')


def proof_label(canvas, label, top):
    canvas.setFillColor(HexColor('#555555'))
    canvas.setFont('Helvetica', 9)
    canvas.drawString(13 * mm, letter[1] - top * mm,
                      f'{label.title}  /  {WIDTH:g} x {label.height:g} mm  /  6.5 mm body capitals')
    label.pdf(canvas, 13, top + 4)
    return top + 4 + label.height


def service_tag_svg():
    texts = []
    for value, x, y, cap in [('A3', 33, 6, 7.2), ('R-600a', 33, 19, 6.5)]:
        path, _, offset, _ = text_paths(value, cap, x, y)
        texts.append(f'<path aria-label="{value}" transform="translate({offset[0]} {offset[1]})" d="{path}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="82mm" height="33mm" viewBox="0 0 82 33">'
            '<title>Service port refrigerant identification</title>'
            '<rect x=".25" y=".25" width="81.5" height="32.5" rx="2" fill="white" stroke="black" stroke-width=".5"/>'
            + symbol_svg(6, 6) + ''.join(texts) + '</svg>')


def main():
    drawings = HERE / 'artwork'
    drawings.mkdir(exist_ok=True)
    items = labels()
    for item in items:
        (drawings / f'{item.key}.svg').write_text(item.svg())
    (drawings / 'service-port-id.svg').write_text(service_tag_svg())
    output = ROOT / 'output/pdf'
    output.mkdir(parents=True, exist_ok=True)
    pdf_path = output / 'refrigerant-warning-proof.pdf'
    canvas = Canvas(str(pdf_path), pagesize=letter, invariant=1)
    canvas.setTitle('Home Soda Machine - refrigerant warning fit proof')
    canvas.setAuthor('Derek Bredensteiner')
    a, b, c, d, f = items
    page_heading(canvas, 1, 'Refrigerant warnings / exterior')
    bottom = proof_label(canvas, a, 34)
    bottom = proof_label(canvas, b, bottom + 15)
    assert bottom < 249
    canvas.showPage()
    page_heading(canvas, 2, 'Refrigerant warnings / storage and service')
    bottom = proof_label(canvas, f, 34)
    bottom = proof_label(canvas, c, bottom + 15)
    assert bottom < 249
    canvas.showPage()
    page_heading(canvas, 3, 'Refrigerant warnings / packaging and service port')
    bottom = proof_label(canvas, d, 34)
    top = bottom + 20
    canvas.setFont('Helvetica', 9)
    canvas.drawString(13 * mm, letter[1] - top * mm, 'SERVICE PORT ID  /  82 x 33 mm  /  21 mm diamond + 7.2 mm A3 capitals')
    canvas.saveState()
    canvas.translate(13 * mm, letter[1] - (top + 4) * mm)
    canvas.scale(mm, -mm)
    canvas.setStrokeColor(HexColor('#161616'))
    canvas.setFillColor(HexColor('#ffffff'))
    canvas.setLineWidth(.5)
    canvas.roundRect(.25, .25, 81.5, 32.5, 2, fill=1, stroke=1)
    draw_symbol(canvas, 6, 6)
    draw_text(canvas, 'A3', 33, 6, 7.2)
    draw_text(canvas, 'R-600a', 33, 19, 6.5)
    canvas.restoreState()
    y = top + 49
    canvas.setFont('Helvetica', 9)
    for line in [
        'Service ports / process tube: PMS 185 or RAL 3020; at least 25 mm each direction.',
        'Actual charge mass needs its own completed, permanent unit marking.',
        'Minimum room area / installation height: determine from the applicable standard.',
        'Ordinary paper is for fit checking. Permanent label material and attachment are unverified.'
    ]:
        canvas.drawString(13 * mm, letter[1] - y * mm, line)
        y += 5
    y += 13
    canvas.setLineWidth(.5)
    canvas.line(13 * mm, letter[1] - y * mm, 63 * mm, letter[1] - y * mm)
    for x in (13, 63):
        canvas.line(x * mm, letter[1] - (y-2) * mm, x * mm, letter[1] - (y+2) * mm)
    canvas.drawString(13 * mm, letter[1] - (y+7) * mm, 'This line must measure 50 mm. Do not use Fit or Shrink to page.')
    assert y + 7 < 249
    canvas.save()
    audit = {
        'status': 'provisional artwork; physical print and placement unverified',
        'body_cap_height_mm': CAP,
        'minimum_body_letter_ink_height_mm': round(min(
            minimum_letter_height(item.lines) for item in items), 6),
        'minimum_target_mm': 6.4,
        'font': 'Helvetica Bold, macOS Helvetica.ttc face 1; outlined',
        'font_em_mm': round(CAP * FONT['head'].unitsPerEm / CAP_UNITS, 6),
        'symbol_diamond_height_mm': SYMBOL_HEIGHT,
        'safety_class_cap_height_mm': SAFETY_CLASS_CAP,
        'labels': [{'file': f'artwork/{item.key}.svg', 'width_mm': WIDTH,
                    'height_mm': item.height, 'body_lines': item.lines,
                    'glyph_bounds': item.audit()} for item in items]
    }
    (HERE / 'artwork-dimensions.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({item.key: [WIDTH, item.height] for item in items}, indent=2))
    print(pdf_path)


if __name__ == '__main__':
    main()
