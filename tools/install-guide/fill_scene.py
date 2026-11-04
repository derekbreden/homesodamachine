'Render concentrate bottles, the closed funnel and a framed Fill screen from the current appliance.'
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def visible(*args, **kwargs):
    return _compiled('fill_scene',path=('visible',),args=args,kwargs=kwargs)

def bottle(*args, **kwargs):
    'The bottle as it pours, and the centre of its mouth.\n\nBuilt mouth down at the origin, then tipped about the mouth toward the cabinet door. The\nconcentrate keeps its volume and settles level.'
    return _compiled('fill_scene',path=('bottle',),args=args,kwargs=kwargs)

def scene(*args, **kwargs):
    return _compiled('fill_scene',path=('scene',),args=args,kwargs=kwargs)

def label(*args, **kwargs):
    return _compiled('fill_scene',path=('label',),args=args,kwargs=kwargs)

def materials(*args, **kwargs):
    return _compiled('fill_scene',path=('materials',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('fill_scene',path=('main',),args=args,kwargs=kwargs)

def publish(*args, **kwargs):
    return _compiled('fill_scene',path=('publish',),args=args,kwargs=kwargs)

__all__ = ['Path', 'argparse', 'hashlib', 'json', 'math', 'shutil', 'sys', 'cq', 'cairosvg', 'np', 'Image', 'TTFont', 'SVGPathPen', 'ROOT', 'HARDWARE', 'DIR', 'OUT', 'SOURCE', 'FACTS', 'read_payload', 'ASSEMBLY_FACTS', 'FUNNEL_BOUNDS', 'TIP', 'CLEARANCE', 'AXIS', 'CAMERA', 'TARGET', 'SPAN', 'SWING_R', 'SWING_FROM', 'DISPLAY_PROFILE', 'SCREEN', 'EXTERIOR', 'visible', 'bottle', 'scene', 'label', 'materials', 'main', 'publish']
_bind('fill_scene',globals())

if __name__ == '__main__':
    _compiled('fill_scene','main')
