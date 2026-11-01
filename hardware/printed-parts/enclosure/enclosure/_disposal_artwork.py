"""The accepted disposal warning's glyph curves and layout metrics, in font units."""

from functools import cache
import json
from pathlib import Path


@cache
def numbers(family, kind):
    artwork = json.loads(Path(__file__).with_name('disposal-warning-artwork.json').read_text())
    if family != artwork['family'] or kind != artwork['kind']:
        raise ValueError('the disposal warning needs artwork for its selected face')
    return artwork


def flat_bounds(lines, cap_height, depth, line_gap, family, kind):
    """The complete raked warning's XY bounds before its placement on the rear wall."""
    art = numbers(family, kind)
    scale = (cap_height/art['cap_height_at_one'])/art['units_per_em']
    rows = []
    for line in lines:
        advance = sum(art['glyphs'][char]['advance'] for char in line)
        pen, boxes = 0.0, []
        for char in line:
            glyph = art['glyphs'][char]
            if glyph['bounds'] is not None:
                x0, x1, y0, y1 = glyph['bounds']
                at = (-advance/2+pen)*scale
                base = art['baseline_units']*scale
                boxes.append((at+x0*scale, at+x1*scale,
                              base+y0*scale, base+y1*scale))
            pen += glyph['advance']
        rows.append((max(b[1] for b in boxes)-min(b[0] for b in boxes),
                     max(b[3] for b in boxes)-min(b[2] for b in boxes)))
    row_height = max(height for _width, height in rows)
    leading = row_height+line_gap
    width = max(width for width, _height in rows)
    spans = [(index*leading+(row_height-height)/2,
              index*leading+(row_height-height)/2+height+depth)
             for index, (_width, height) in enumerate(reversed(rows))]
    return -width/2, width/2, min(a for a, _b in spans), max(b for _a, b in spans)
