"Model and render ice in the owner guides' frozen first-pour scene."
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def scene(*args, **kwargs):
    return _compiled('ice_scene',path=('scene',),args=args,kwargs=kwargs)

def materials(*args, **kwargs):
    return _compiled('ice_scene',path=('materials',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('ice_scene',path=('main',),args=args,kwargs=kwargs)

__all__ = ['Path', 'argparse', 'json', 'math', 'sys', 'cq', 'np', 'ROOT', 'HARDWARE', 'OUT', 'SOURCE', 'read_payload', 'GLASS_CENTER', 'CAMERA', 'scene', 'materials', 'main']
_bind('ice_scene',globals())

if __name__ == '__main__':
    _compiled('ice_scene','main')
