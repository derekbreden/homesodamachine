'Draw the supplied kit as consistent vector hidden-line views.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def models(*args, **kwargs):
    "Current component surfaces and the kit's source-dimensioned props."
    return _compiled('kit_art',path=('models',),args=args,kwargs=kwargs)

def line_svg(*args, **kwargs):
    'Use world Z as up and bake all projection transforms into the SVG paths.'
    return _compiled('kit_art',path=('line_svg',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('kit_art',path=('main',),args=args,kwargs=kwargs)

__all__ = ['Path', 'json', 'sys', 'ROOT', 'HARDWARE', 'ART', 'model_outlines', 'CAMERA', 'VIEWS', 'models', 'line_svg', 'main']
_bind('kit_art',globals())

if __name__ == '__main__':
    _compiled('kit_art','main')
