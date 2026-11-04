'Draw the cylinder handwheel and the factory-set regulator with both gauges pressurised.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def dial_print(*args, **kwargs):
    "The dial's scale and a needle at the illustrated pressure."
    return _compiled('startup',path=('dial_print',),args=args,kwargs=kwargs)

def assembly(*args, **kwargs):
    "The fitted regulator and top of the customer's cylinder."
    return _compiled('startup',path=('assembly',),args=args,kwargs=kwargs)

def points(*args, **kwargs):
    return _compiled('startup',path=('points',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('startup',path=('main',),args=args,kwargs=kwargs)

__all__ = ['json', 'math', 'cq', 'scenes', 'OUT', 'ART', 'CAM', 'TARGET', 'SPAN', 'SIZE', 'reg', 'OUTLET_PSI', 'CYLINDER_PSI', 'dial_print', 'assembly', 'points', 'main']
_bind('startup',globals())

if __name__ == '__main__':
    _compiled('startup','main')
