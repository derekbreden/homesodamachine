'Render the current counter opening and its registered component silhouette.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def outlines(*args, **kwargs):
    'Closed cell-edge contours; only the exterior silhouette is illustrated.'
    return _compiled('opening_scene',path=('outlines',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('opening_scene',path=('main',),args=args,kwargs=kwargs)

__all__ = ['Path', 'hashlib', 'json', 'os', 'sys', 'np', 'Image', 'binary_fill_holes', 'ROOT', 'HARDWARE', 'OUT', 'ASSETS', 'outlines', 'main']
_bind('opening_scene',globals())

if __name__ == '__main__':
    _compiled('opening_scene','main')
