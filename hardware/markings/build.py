"""Household R-600a warning proofs with outlined, measured Helvetica Bold lettering."""

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
SYMBOL_HEIGHT = 18.0
SYMBOL_SOURCE_HEIGHT = 523.6
SYMBOL = ET.parse(HERE / 'w021.svg').getroot()


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
            self.text.append(('R-600a', 137.0, 12.9, 6.5))
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
            boxes.append(('ISO 7010 W021', 108, 6, 600 * SYMBOL_HEIGHT / SYMBOL_SOURCE_HEIGHT, SYMBOL_HEIGHT))
            assert SYMBOL_HEIGHT >= 15
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
            content.append(symbol_svg(108, 6))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}mm" '
                f'height="{self.height}mm" viewBox="0 0 {WIDTH} {self.height}">'
                f'<title>{self.title}</title><desc>Household R-600a warning artwork. '
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
            draw_symbol(canvas, 108, 6)
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
    content = ''.join(ET.tostring(child, encoding='unicode') for child in SYMBOL
                      if child.tag.rsplit('}', 1)[-1] in ('path', 'polygon'))
    return (f'<g transform="translate({x} {y}) scale({SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT})">'
            f'{content}</g>')


def draw_symbol(canvas, x, y):
    from reportlab.graphics import renderPDF
    from reportlab.graphics.shapes import Drawing
    canvas.saveState()
    canvas.translate(x, y)
    canvas.scale(SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT, SYMBOL_HEIGHT/SYMBOL_SOURCE_HEIGHT)
    for element in SYMBOL:
        kind = element.tag.rsplit('}', 1)[-1]
        if kind not in ('path', 'polygon'):
            continue
        pen = ReportLabPen(None)
        target = pen
        if 'transform' in element.attrib:
            matrix = element.attrib['transform'].removeprefix('matrix(').removesuffix(')')
            target = TransformPen(pen, tuple(float(n) for n in matrix.split(',')))
        if kind == 'path':
            parse_path(element.attrib['d'], target)
        else:
            points = [tuple(float(n) for n in p.split(','))
                      for p in element.attrib['points'].split()]
            target.moveTo(points[0])
            for point in points[1:]:
                target.lineTo(point)
            target.closePath()
        style = dict(pair.split(':', 1) for pair in element.get('style', '').split(';') if ':' in pair)
        fill = element.get('fill', '#000000')
        fill = style.get('fill', fill)
        pen.path.fillColor = HexColor(fill)
        pen.path.strokeColor = None
        drawing = Drawing()
        drawing.add(pen.path)
        renderPDF.draw(drawing, canvas, 0, 0)
    canvas.restoreState()


def labels():
    return [
        Label('household-exterior-disposal', 'Exterior / disposal', 'CAUTION', [
            'Risk of Fire Or Explosion.',
            'Dispose of Properly In Accordance With The Applicable Federal Or Local Regulations.',
            'Flammable Refrigerant Used.'
        ]),
        Label('household-service', 'Compressor compartment / service and tubing', 'DANGER', [
            'Risk Of Fire Or Explosion Due To Puncture Of Refrigerant Tubing.',
            'Flammable Refrigerant Used.',
            'To Be Repaired Only By\nTrained Service Personnel.',
            'Do Not Puncture\nRefrigerant Tubing.',
            "Consult Repair Manual/Owner's Guide Before Attempting To Service This Product.",
            'All Safety Precautions\nMust Be Followed.',
            'Follow Handling Instructions Carefully.'
        ], symbol=True),
    ]


def page_heading(canvas, page, title):
    canvas.setFillColor(HexColor('#161616'))
    canvas.setFont('Helvetica-Bold', 14)
    canvas.drawString(13 * mm, letter[1] - 16 * mm, title)
    canvas.setFont('Helvetica', 9)
    canvas.drawString(13 * mm, letter[1] - 23 * mm, 'FULL-SIZE FIT PROOF  /  US LETTER  /  PRINT AT 100%, ACTUAL SIZE')
    canvas.setFont('Helvetica', 8)
    canvas.drawString(13 * mm, 17 * mm, 'Household design specification. Paper is a fit template; use permanent production markings.')
    canvas.drawString(13 * mm, 12 * mm, 'EPA Rule 22 / UL 60335-2-24 (April 28, 2017). Sources: hardware/markings/README.md.')
    canvas.drawRightString(203 * mm, 7 * mm, f'{page} / 2')


def proof_label(canvas, label, top):
    canvas.setFillColor(HexColor('#555555'))
    canvas.setFont('Helvetica', 9)
    canvas.drawString(13 * mm, letter[1] - top * mm,
                      f'{label.title}  /  {WIDTH:g} x {label.height:g} mm  /  6.5 mm body capitals')
    label.pdf(canvas, 13, top + 4)
    return top + 4 + label.height


def notes(canvas, top, lines):
    canvas.setFillColor(HexColor('#333333'))
    canvas.setFont('Helvetica', 9)
    for line in lines:
        canvas.drawString(13 * mm, letter[1] - top * mm, line)
        top += 5
    return top


def scale_bar(canvas, y):
    canvas.setStrokeColor(HexColor('#161616'))
    canvas.setLineWidth(.5)
    canvas.line(13 * mm, letter[1] - y * mm, 63 * mm, letter[1] - y * mm)
    for x in (13, 63):
        canvas.line(x * mm, letter[1] - (y-2) * mm, x * mm, letter[1] - (y+2) * mm)
    canvas.drawString(13 * mm, letter[1] - (y+7) * mm, '50 mm at actual size. Do not use Fit or Shrink to page.')


def main():
    drawings = HERE / 'artwork'
    drawings.mkdir(exist_ok=True)
    items = labels()
    for item in items:
        (drawings / f'{item.key}.svg').write_text(item.svg())
    output = ROOT / 'output/pdf'
    output.mkdir(parents=True, exist_ok=True)
    pdf_path = output / 'refrigerant-warning-proof.pdf'
    canvas = Canvas(str(pdf_path), pagesize=letter, invariant=1)
    canvas.setTitle('Home Soda Machine - household R-600a warning fit proof')
    canvas.setAuthor('Derek Bredensteiner')
    exterior, service = items
    page_heading(canvas, 1, 'Household R-600a / exterior disposal warning')
    bottom = proof_label(canvas, exterior, 34)
    notes(canvas, bottom + 12, [
        'Placement: on the outside of the enclosure; a rear or side face can carry this label.',
        'This warning does not need to occupy the brand / serial / QR nameplate.',
        'Wording: UL 60335-2-24 (2017), 7.1DV.4.1(d). Body capitals: at least 6.4 mm.',
        '',
        'Separate appliance information: manufacturer / model, voltage, AC frequency, rated current,',
        'manufacturing date or date code, R-600a, actual charge in grams, and foam blowing-agent ID.',
        'Use established unit values. The study text 5A / 600W is not a measured appliance rating.',
        '',
        'The disposal warning plus the service panel on page 2 cover the four applicable messages.',
        'The enclosed, foam-embedded evaporator has no user-contact defrost-warning location.',
        'No commercial storage paragraph, packaging paragraph, or A3 diamond is specified here.'
    ])
    scale_bar(canvas, 230)
    canvas.showPage()
    page_heading(canvas, 2, 'Household R-600a / compressor compartment')
    bottom = proof_label(canvas, service, 34)
    y = notes(canvas, bottom + 10, [
        'Place near the compressor compartment and its exposed tubing, visible on gaining access.',
        'Combined equivalent wording for 7.1DV.4.1(b), (c), (e); all instructions retained.',
        'ISO 7010 W021 triangle: 18 mm high. R-600a identification visible at compressor access.',
        'Service-opening locations: PMS 185 red; process tube red at least 25 mm from compressor.'
    ])
    assert y < 249
    scale_bar(canvas, 243)
    canvas.save()
    audit = {
        'status': 'household design specification; dimensioned fit proof; physical attachment not implemented',
        'standard': 'UL 60335-2-24, second edition, April 28, 2017; EPA SNAP Rule 22',
        'warning_clauses': {'household-exterior-disposal': ['7.1DV.4.1(d)'],
                            'household-service': ['7.1DV.4.1(b)', '7.1DV.4.1(c)', '7.1DV.4.1(e)']},
        'service_wording': 'Combined equivalent warning; DANGER heading and all substantive instructions retained',
        'body_cap_height_mm': CAP,
        'minimum_body_letter_ink_height_mm': round(min(
            minimum_letter_height(item.lines) for item in items), 6),
        'minimum_target_mm': 6.4,
        'font': 'Helvetica Bold, macOS Helvetica.ttc face 1; outlined',
        'font_em_mm': round(CAP * FONT['head'].unitsPerEm / CAP_UNITS, 6),
        'symbol': 'ISO 7010 W021',
        'symbol_triangle_height_mm': SYMBOL_HEIGHT,
        'labels': [{'file': f'artwork/{item.key}.svg', 'width_mm': WIDTH,
                    'height_mm': item.height, 'body_lines': item.lines,
                    'glyph_bounds': item.audit()} for item in items]
    }
    (HERE / 'artwork-dimensions.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps({item.key: [WIDTH, item.height] for item in items}, indent=2))
    print(pdf_path)


if __name__ == '__main__':
    main()
