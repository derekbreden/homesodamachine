"Draw the app's phone-at-the-faucet illustration from the faucet's source solids.\n\nThe fixed front camera looks down 15 degrees. The phone lies parallel to the\ndisplay, turned 34 degrees toward the hand. A continuous housing silhouette,\nthe cover's front bezel and aperture, the recessed glass, and the three tube\nmouths carry separate pen weights. The app supplies the template image's color.\n\nRegenerate with tools/cad-venv/bin/python tools/install-guide/hold_scene.py.\nAn optional output path writes a study without replacing the app asset."
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def projected(*args, **kwargs):
    return _compiled('hold_scene',path=('projected',),args=args,kwargs=kwargs)

def polylines(*args, **kwargs):
    return _compiled('hold_scene',path=('polylines',),args=args,kwargs=kwargs)

def visible_lines(*args, **kwargs):
    'Project visible sharp edges and silhouettes, retaining their source bodies.'
    return _compiled('hold_scene',path=('visible_lines',),args=args,kwargs=kwargs)

def wire_lines(*args, **kwargs):
    return _compiled('hold_scene',path=('wire_lines',),args=args,kwargs=kwargs)

def front_face(*args, **kwargs):
    'The broad planar face looking along normal, independent of edge ordering.'
    return _compiled('hold_scene',path=('front_face',),args=args,kwargs=kwargs)

def silhouette(*args, **kwargs):
    'Union projected solid triangles so touching pieces share one outer contour.'
    return _compiled('hold_scene',path=('silhouette',),args=args,kwargs=kwargs)

def clip(*args, **kwargs):
    'Keep the portions of a polyline for which inside(point) >= 0.'
    return _compiled('hold_scene',path=('clip',),args=args,kwargs=kwargs)

class Pen:
    def __init__(self, *args, **kwargs):
        return _compiled('hold_scene',path=('Pen.__init__',),args=(self,*args),kwargs=kwargs)

    def page(self, *args, **kwargs):
        return _compiled('hold_scene',path=('Pen.page',),args=(self,*args),kwargs=kwargs)

    def curve(self, *args, **kwargs):
        'Smooth projected curves while retaining straight runs and hard joins.'
        return _compiled('hold_scene',path=('Pen.curve',),args=(self,*args),kwargs=kwargs)

    def paths(self, *args, **kwargs):
        return _compiled('hold_scene',path=('Pen.paths',),args=(self,*args),kwargs=kwargs)

    def group(self, *args, **kwargs):
        return _compiled('hold_scene',path=('Pen.group',),args=(self,*args),kwargs=kwargs)

    def region(self, *args, **kwargs):
        return _compiled('hold_scene',path=('Pen.region',),args=(self,*args),kwargs=kwargs)

def drawing(*args, **kwargs):
    return _compiled('hold_scene',path=('drawing',),args=args,kwargs=kwargs)

__all__ = ['Path', 'math', 'os', 're', 'sys', 'ROOT', 'HARDWARE', 'cq', 'getPaths', 'BRepLib', 'gp_Ax2', 'gp_Dir', 'gp_Pnt', 'HLRAlgo_Projector', 'HLRBRep_Algo', 'HLRBRep_HLRToShape', 'line_merge', 'union_all', 'LineString', 'Polygon', 'art', 'ASSET', 'ELEVATION', 'PHONE', 'TWIST', 'GAP', 'CORNER', 'LEFT', 'WIDTH', 'HEIGHT', 'PHONE_FADE', 'projected', 'polylines', 'visible_lines', 'wire_lines', 'front_face', 'silhouette', 'clip', 'Pen', 'drawing']
_bind('hold_scene',globals())

if __name__ == '__main__':
    _compiled('hold_scene','main')
