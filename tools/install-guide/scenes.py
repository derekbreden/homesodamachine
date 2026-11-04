'Compose the cylinder, power, fill and pour pictures for the install guide.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def load(*args, **kwargs):
    return _compiled('scenes',path=('load',),args=args,kwargs=kwargs)

def stage(*args, **kwargs):
    return _compiled('scenes',path=('stage',),args=args,kwargs=kwargs)

def cylinder(*args, **kwargs):
    "The regulator on the customer's cylinder, its red tether in the outlet from the factory.\n`stand_off` holds the regulator out along its inlet axis, its big nut short of the valve."
    return _compiled('scenes',path=('cylinder',),args=args,kwargs=kwargs)

def fill(*args, **kwargs):
    return _compiled('scenes',path=('fill',),args=args,kwargs=kwargs)

def pour(*args, **kwargs):
    return _compiled('scenes',path=('pour',),args=args,kwargs=kwargs)

def materials(*args, **kwargs):
    "The glass and cola's authored presentation, addressed by solid name."
    return _compiled('scenes',path=('materials',),args=args,kwargs=kwargs)

def render(*args, **kwargs):
    'Draw the staged payloads with the clear glass and cola materials.'
    return _compiled('scenes',path=('render',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('scenes',path=('main',),args=args,kwargs=kwargs)

__all__ = ['Path', 'importlib', 'json', 'math', 'sys', 'ROOT', 'HARDWARE', 'OUT', 'ART', 'cq', 'install', 'original', 'load', 'reg', 'SILVER', 'BLACK', 'GLASS', 'DRINK', 'jobs', 'stage', 'cylinder', 'fill', 'pour', 'materials', 'render', 'main']
_bind('scenes',globals())

if __name__ == '__main__':
    _compiled('scenes','main')
