'Lulu Small Landscape perfect-bound editions and ordering bundle.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def boxes(*args, **kwargs):
    return _compiled('press',path=('boxes',),args=args,kwargs=kwargs)

def srgb(*args, **kwargs):
    'Calibrate RGB vectors and images with the standard sRGB profile.'
    return _compiled('press',path=('srgb',),args=args,kwargs=kwargs)

def write_pdf(*args, **kwargs):
    return _compiled('press',path=('write_pdf',),args=args,kwargs=kwargs)

def write_editions(*args, **kwargs):
    return _compiled('press',path=('write_editions',),args=args,kwargs=kwargs)

def make_order_bundle(*args, **kwargs):
    return _compiled('press',path=('make_order_bundle',),args=args,kwargs=kwargs)

__all__ = ['deepcopy', 'hashlib', 'io', 'math', 'Path', 'shutil', 'subprocess', 'zipfile', 'Image', 'ImageCms', 'PdfReader', 'PdfWriter', 'Transformation', 'ArrayObject', 'DecodedStreamObject', 'DictionaryObject', 'NameObject', 'NumberObject', 'RectangleObject', 'HexColor', 'ImageReader', 'canvas', 'TRIM_W', 'TRIM_H', 'BLEED', 'INTERIOR_PAGES', 'SPINE_W', 'INTERIOR_SIZE', 'COVER_SIZE', 'boxes', 'srgb', 'write_pdf', 'write_editions', 'make_order_bundle']
_bind('press',globals())

if __name__ == '__main__':
    _compiled('press','main')
