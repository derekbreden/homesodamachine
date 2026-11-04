"""The anchor cap and the tube anchor it closes, in the anchor's own frame.

`u` runs along the tube, `n` from the tube toward the face the rib roots on, and `t = n x u`; a
section point (a, b) stands at mid + a*t + b*n, with b = 0 on the tube's axis plane. That is the
frame `enclosure._tube_anchors` strikes every rib in, so one station places the rib, its catch
windows, the ceiling's wing room and the cap.

THE RIB IS THE TIE RIB'S HALF PIPE WITHOUT THE TIE. A solid post, the seat bored into it and its
lips flat one `WALL` past the axis plane, with a catch window in each flank. Each window is a
closed pocket between the rib's two end webs, so on a piece printed root-down its bearing face
prints as a bridge web to web, the way the tie channel's crown did. On a rib rooted on a wall the
flank that looks print-down and its window's roof bridge web to web instead, and the two end
webs stand on the tied rib's own 45-degree corbels (`enclosure._capped_anchor`).

THE CAP IS THE OTHER HALF OF THE PIPE, one section extruded `CAP_LEN` along the tube. Below the
axis plane it is solid from the bore out to its round back; two `WING`-thick wings rise up the
rib's flanks and each carries a lip that drops into its window. A `CAVITY` gap separates the
half pipe from each wing for `CAVITY_DEG` round the pipe, so a wing bends from the gap's round
end rather than from the axis plane. That length is what sets its strain going on
(`wing_strain`), and the cap's README holds it beside the accepted faucet display cover's.

THE CAP IS CUT FOR THE 1/4" TUBE'S SEAT AND PRINTS STANDING ON ITS END. Every layer is the
whole section, so the wings bend along their extrusion lines, and no face overhangs.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_anchor_cap_interface'

class Frame:
    def __init__(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.__init__',), args=(self, *args), kwargs=kwargs)
    def point(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.point',), args=(self, *args), kwargs=kwargs)
    def plane(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.plane',), args=(self, *args), kwargs=kwargs)
    def prism(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.prism',), args=(self, *args), kwargs=kwargs)
    def section(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.section',), args=(self, *args), kwargs=kwargs)
    def bore(self, *args, **kwargs):
        return _compiled('_anchor_cap_interface', path=('Frame.bore',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('_anchor_cap_interface', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_anchor_cap_interface', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_anchor_cap_interface', action="main")
