"The cylinder connection and startup controls, in the regulator's world frame.\n\n+Y faces the customer, +Z is up, and the cylinder stands at -X. The red tether is\npushed into the regulator's PI010822S at the factory, so the customer's one joint here is\nthe big nut onto the cylinder valve."
from __future__ import annotations
from pathlib import Path as _Path
import sys as _sys
_sys.path.insert(0,str(_Path(__file__).resolve().parents[2]/"hardware/scripts"))
from _guides_compiled import compiled as _compiled, bind as _bind

def unit(*args, **kwargs):
    return _compiled('cylinder_actions',path=('unit',),args=args,kwargs=kwargs)

def cross(*args, **kwargs):
    return _compiled('cylinder_actions',path=('cross',),args=args,kwargs=kwargs)

def camera_axes(*args, **kwargs):
    return _compiled('cylinder_actions',path=('camera_axes',),args=args,kwargs=kwargs)

def startup_pose(*args, **kwargs):
    "The startup camera's pixel registration with extra canvas below it."
    return _compiled('cylinder_actions',path=('startup_pose',),args=args,kwargs=kwargs)

def pixel(*args, **kwargs):
    return _compiled('cylinder_actions',path=('pixel',),args=args,kwargs=kwargs)

def outlet_stations(*args, **kwargs):
    "The outlet push-fit and the tube leaving it, and the big nut's face."
    return _compiled('cylinder_actions',path=('outlet_stations',),args=args,kwargs=kwargs)

def assembly(*args, **kwargs):
    "The regulator, its factory-fitted tether and the top of the customer's cylinder."
    return _compiled('cylinder_actions',path=('assembly',),args=args,kwargs=kwargs)

def points(*args, **kwargs):
    return _compiled('cylinder_actions',path=('points',),args=args,kwargs=kwargs)

def anchor_metadata(*args, **kwargs):
    return _compiled('cylinder_actions',path=('anchor_metadata',),args=args,kwargs=kwargs)

def main(*args, **kwargs):
    return _compiled('cylinder_actions',path=('main',),args=args,kwargs=kwargs)

__all__ = ['annotations', 'argparse', 'json', 'math', 'cq', 'Image', 'scenes', 'startup', 'OUT', 'ART', 'READY_STANDOFF', 'CONNECTION_POSE', 'STARTUP_EXTRA_HEIGHT', 'reg', 'install', 'unit', 'cross', 'camera_axes', 'startup_pose', 'pixel', 'outlet_stations', 'assembly', 'points', 'anchor_metadata', 'main']
_bind('cylinder_actions',globals())

if __name__ == '__main__':
    _compiled('cylinder_actions','main')
