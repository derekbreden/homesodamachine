'Fixed-width page silhouettes for the installation illustrations.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def glass_lip(*args, **kwargs):
    return _compiled('contours',path=('glass_lip',),args=args,kwargs=kwargs)

def _filter_region(*args, **kwargs):
    return _compiled('contours',path=('_filter_region',),args=args,kwargs=kwargs)

class Contours:
    def __init__(self, *args, **kwargs):
        return _compiled('contours',path=('Contours.__init__',),args=(self,*args),kwargs=kwargs)

    def picture(self, *args, **kwargs):
        return _compiled('contours',path=('Contours.picture',),args=(self,*args),kwargs=kwargs)

    def render(self, *args, **kwargs):
        return _compiled('contours',path=('Contours.render',),args=(self,*args),kwargs=kwargs)

__all__ = ['Path', 'hashlib', 'json', 'math', 'subprocess', 'ET', 'Image', 'glass_lip', 'ROOT', 'ART', 'OUT', 'PAD', 'PPI', 'Contours']
_bind('contours',globals())

if __name__ == '__main__':
    _compiled('contours','main')
