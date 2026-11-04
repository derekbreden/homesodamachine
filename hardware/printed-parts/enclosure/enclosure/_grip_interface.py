"""Reference curved grip receiver and flat-wing cover geometry.

The recorded coupon and cover trials use these reliefs, slots and placement.
The production enclosure has integral exposed handholds.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_grip_interface'

class GripInterface:
    def __init__(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.__init__',), args=(self, *args), kwargs=kwargs)
    def box(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.box',), args=(self, *args), kwargs=kwargs)
    def rounded(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.rounded',), args=(self, *args), kwargs=kwargs)
    def wing(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.wing',), args=(self, *args), kwargs=kwargs)
    def cover(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.cover',), args=(self, *args), kwargs=kwargs)
    def placed(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.placed',), args=(self, *args), kwargs=kwargs)
    def receiver_reliefs(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.receiver_reliefs',), args=(self, *args), kwargs=kwargs)
    def receiver_slots(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.receiver_slots',), args=(self, *args), kwargs=kwargs)
    def apply_receiver(self, *args, **kwargs):
        return _compiled('_grip_interface', path=('GripInterface.apply_receiver',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('_grip_interface', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_grip_interface', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_grip_interface', action="main")
