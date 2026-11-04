'Check the 9 x 7 inch landscape PDFs, navigation, bleed and print artwork.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

from dataclasses import dataclass
@dataclass(frozen=True)
class Spec:
    filename: str
    pages: int
    media: tuple[float, float, float, float]
    trim: tuple[float, float, float, float]
    press: bool = False
    raster: bool = False

def dereference(*args, **kwargs):
    return _compiled('preflight',path=('dereference',),args=args,kwargs=kwargs)

def object_key(*args, **kwargs):
    return _compiled('preflight',path=('object_key',),args=args,kwargs=kwargs)

def normalized(*args, **kwargs):
    return _compiled('preflight',path=('normalized',),args=args,kwargs=kwargs)

def same_box(*args, **kwargs):
    return _compiled('preflight',path=('same_box',),args=args,kwargs=kwargs)

class Preflight:
    def __init__(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.__init__',),args=(self,*args),kwargs=kwargs)

    def fail(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.fail',),args=(self,*args),kwargs=kwargs)

    def resource_checks(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.resource_checks',),args=(self,*args),kwargs=kwargs,mutable=((4,'fonts'),(5,'visited')))

    def image_checks(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.image_checks',),args=(self,*args),kwargs=kwargs)

    def check_file(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.check_file',),args=(self,*args),kwargs=kwargs)

    def check_navigation(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.check_navigation',),args=(self,*args),kwargs=kwargs)

    def check_text_margins(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.check_text_margins',),args=(self,*args),kwargs=kwargs)

    def check_interior_text(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.check_interior_text',),args=(self,*args),kwargs=kwargs)

    def run(self, *args, **kwargs):
        return _compiled('preflight',path=('Preflight.run',),args=(self,*args),kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('preflight',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'argparse', 'hashlib', 'json', 're', 'shutil', 'subprocess', 'sys', 'unicodedata', 'dataclass', 'Path', 'pdfplumber', 'PdfReader', 'ArrayObject', 'IndirectObject', 'TRIM_W', 'TRIM_H', 'BLEED', 'COVER_SIZE', 'ROOT', 'TOC', 'Spec', 'SPECS', 'dereference', 'object_key', 'normalized', 'same_box', 'Preflight', 'main']
_bind('preflight',globals())

if __name__ == '__main__':
    _compiled('preflight','main')
