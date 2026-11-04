'Render the cord and bottle insertion poses from the frozen installation meshes.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def unit(*args, **kwargs):
    return _compiled('insertion_actions',path=('unit',),args=args,kwargs=kwargs)

def pixel(*args, **kwargs):
    return _compiled('insertion_actions',path=('pixel',),args=args,kwargs=kwargs)

def mesh_bounds(*args, **kwargs):
    return _compiled('insertion_actions',path=('mesh_bounds',),args=args,kwargs=kwargs)

def anchor(*args, **kwargs):
    return _compiled('insertion_actions',path=('anchor',),args=args,kwargs=kwargs)

def metadata(*args, **kwargs):
    return _compiled('insertion_actions',path=('metadata',),args=args,kwargs=kwargs)

def moved_payload(*args, **kwargs):
    'Translate the moving meshes in a render-only copy of the frozen payload.'
    return _compiled('insertion_actions',path=('moved_payload',),args=args,kwargs=kwargs,mutable=((1,'entry'),))

def registration(*args, **kwargs):
    'Read the anchor pixels from the matrix the GPU picture was drawn with.'
    return _compiled('insertion_actions',path=('registration',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('insertion_actions',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'argparse', 'hashlib', 'json', 'math', 'Path', 'struct', 'sys', 'np', 'Image', 'ROOT', 'HARDWARE', 'SNAPSHOTS', 'OUT', 'ART', 'POWER_RETREAT', 'BOTTLE_LIFT', 'POSES', 'unit', 'pixel', 'mesh_bounds', 'anchor', 'metadata', 'moved_payload', 'registration', 'main']
_bind('insertion_actions',globals())

if __name__ == '__main__':
    _compiled('insertion_actions','main')
