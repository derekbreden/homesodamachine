'Compose the 32-interior-page, 9 x 7 inch owner install guide.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def begin_page(*args, **kwargs):
    return _compiled('landscape',path=('begin_page',),args=args,kwargs=kwargs)

def rect(*args, **kwargs):
    return _compiled('landscape',path=('rect',),args=args,kwargs=kwargs)

def ground(*args, **kwargs):
    return _compiled('landscape',path=('ground',),args=args,kwargs=kwargs)

def line(*args, **kwargs):
    return _compiled('landscape',path=('line',),args=args,kwargs=kwargs)

def text(*args, **kwargs):
    return _compiled('landscape',path=('text',),args=args,kwargs=kwargs)

def para(*args, **kwargs):
    return _compiled('landscape',path=('para',),args=args,kwargs=kwargs)

def label(*args, **kwargs):
    return _compiled('landscape',path=('label',),args=args,kwargs=kwargs)

def badge(*args, **kwargs):
    return _compiled('landscape',path=('badge',),args=args,kwargs=kwargs)

def header(*args, **kwargs):
    return _compiled('landscape',path=('header',),args=args,kwargs=kwargs)

def end(*args, **kwargs):
    return _compiled('landscape',path=('end',),args=args,kwargs=kwargs)

def image_reader(*args, **kwargs):
    return _compiled('landscape',path=('image_reader',),args=args,kwargs=kwargs)

def pic(*args, **kwargs):
    return _compiled('landscape',path=('pic',),args=args,kwargs=kwargs)

def caption(*args, **kwargs):
    return _compiled('landscape',path=('caption',),args=args,kwargs=kwargs)

def kit_picture(*args, **kwargs):
    return _compiled('landscape',path=('kit_picture',),args=args,kwargs=kwargs)

def note(*args, **kwargs):
    return _compiled('landscape',path=('note',),args=args,kwargs=kwargs)

def item(*args, **kwargs):
    return _compiled('landscape',path=('item',),args=args,kwargs=kwargs)

def arrow(*args, **kwargs):
    'An arrow through x, y pairs: two draw it straight, more follow a curve to its head.'
    return _compiled('landscape',path=('arrow',),args=args,kwargs=kwargs)

def leader(*args, **kwargs):
    return _compiled('landscape',path=('leader',),args=args,kwargs=kwargs)

def projected(*args, **kwargs):
    return _compiled('landscape',path=('projected',),args=args,kwargs=kwargs)

def mounting_slots(*args, **kwargs):
    'Show the seated steel opening and line envelopes, looking up from below.\n\nRead the production DXF and its centered mounting coordinates directly.\nThe washer/nut are omitted in this section so both slots remain visible.'
    return _compiled('landscape',path=('mounting_slots',),args=args,kwargs=kwargs)

def front_cover(*args, **kwargs):
    return _compiled('landscape',path=('front_cover',),args=args,kwargs=kwargs)

def back_cover(*args, **kwargs):
    return _compiled('landscape',path=('back_cover',),args=args,kwargs=kwargs)

__all__ = ['Path', 'ast', 'hashlib', 'io', 'json', 'math', 're', 'subprocess', 'sys', 'ET', 'Image', 'ezdxf', 'canvas', 'pdfmetrics', 'TTFont', 'HexColor', 'white', 'ParagraphStyle', 'Paragraph', 'ImageReader', 'Contours', 'PAD', 'BLEED', 'TRIM_W', 'TRIM_H', 'write_editions', 'make_order_bundle', 'ROOT', 'DIR', 'ART', 'OUT', 'PDF', 'PRESS_DIR', 'W', 'H', 'M', 'CW', 'RIGHT', 'RW', 'BLUE', 'NAVY', 'ICE', 'ORANGE', 'INK', 'MUTED', 'RULE', 'CORAL', 'contours', 'buffer', 'c', 'page_no', 'checks', 'image_checks', 'titles', 'mount_slot_checks', 'resolutions', 'FILL', 'FILL_POSE', 'begin_page', 'rect', 'ground', 'line', 'text', 'para', 'label', 'badge', 'header', 'end', 'image_reader', 'pic', 'caption', 'kit_picture', 'note', 'item', 'arrow', 'leader', 'projected', 'mounting_slots', 'front_cover', 'route', 'kit', 'supplies', 'y', 'p', 'rows', 'co2_anchors', 'power_anchors', 'pose', 'tap', 'press', 'back_cover', 'im']
_bind('landscape',globals())

if __name__ == '__main__':
    _compiled('landscape','main')
