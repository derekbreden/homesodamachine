'Producer surfaces and authored illustration props for the customer pictures.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def _select(*args, **kwargs):
    return _compiled('_cad_art_mesh',path=('_select',),args=args,kwargs=kwargs)

def _color(*args, **kwargs):
    return _compiled('_cad_art_mesh',path=('_color',),args=args,kwargs=kwargs)

def _props(*args, **kwargs):
    return _compiled('_cad_art_mesh',path=('_props',),args=args,kwargs=kwargs)

def _write(*args, **kwargs):
    return _compiled('_cad_art_mesh',path=('_write',),args=args,kwargs=kwargs)

def _anchors(*args, **kwargs):
    return _compiled('_cad_art_mesh',path=('_anchors',),args=args,kwargs=kwargs)

def build_steps(*args, **kwargs):
    'The existing faucet and mount states, without rebuilding the faucet.'
    return _compiled('_cad_art_mesh',path=('build_steps',),args=args,kwargs=kwargs)

def build_connection_steps(*args, **kwargs):
    'The same rear face, six leads and SIG-6 plug in the two registered poses.'
    return _compiled('_cad_art_mesh',path=('build_connection_steps',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'json', 'math', 'Path', 'np', 'rgba', 'build_steps', 'build_connection_steps']
_bind('_cad_art_mesh',globals())

if __name__ == '__main__':
    _compiled('_cad_art_mesh','main')
