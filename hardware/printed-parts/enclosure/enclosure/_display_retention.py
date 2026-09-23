"""The display cover's two skirts and the open-backed catches the housing holds them with.

Coordinates follow the machine display: X across, Y up the screen, Z out of the face.

EACH SKIRT IS THE NAMEPLATE'S SNAP TAB RUN BROAD. Its thickness, reach, square lip, land and
bearing slip are `_nameplate_interface`'s, and it runs `LENGTH` along the display instead of
the tab's width. The housing's side of it is the nameplate receiver's too: a slot with a flex
lane to one side, and under the catch nothing at all. The open back runs straight down in the
print (world -Z) from the catch into the pump bay, so the catch's support stands in open air
and leaves the way it came in.
"""

import math

import cadquery as cq
import _nameplate_interface as _tab
from _enclosure_interface import display_inset_x, display_cover_slip, display_cover_thickness
from _swept_top import ANGLE

WALL = _tab.TAB_THICK
LENGTH = 24.0
LIP = _tab.LIP
LIP_START = _tab.LIP_START
LIP_LAND = _tab.LIP_LAND
BEARING_SLIP = _tab.BEARING_SLIP
END_SLIP = _tab.END_SLIP
ROOT = display_cover_thickness
DEPTH = ROOT + _tab.TAB_LENGTH
OUTER_X = display_inset_x / 2.0 - display_cover_slip
# The flat the lip catches under, one bearing slip above the lip's own shoulder.
CATCH = ROOT + LIP_START - BEARING_SLIP
# The slot runs the inset's own wall down to the catch; inboard it leaves the skirt room to
# bend in by the whole lip.
NECK_X = OUTER_X + display_cover_slip
FLEX_X = OUTER_X - WALL - LIP
# The open back reaches one more lip past the lip's tip.
BACK_X = OUTER_X + 2.0 * LIP
RUN = LENGTH + 2.0 * END_SLIP
# Below the catch the skirt goes on along the display's normal while the open back drops
# plumb, so the back's base reaches this much further up the display to keep the lip inside it.
DRIFT = (DEPTH + END_SLIP - CATCH) * math.tan(math.radians(ANGLE))


def _prism(profile, length=LENGTH):
    wire = cq.Wire.makePolygon([cq.Vector(x, -length / 2.0, z)
                               for x, z in [*profile, profile[0]]])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, length, 0))


def skirt(side=1):
    """One broad skirt: the nameplate tab's square catch and tapered nose."""
    x, r = OUTER_X, ROOT
    profile = [(x - WALL, -r), (x, -r), (x, -r - LIP_START),
               (x + LIP, -r - LIP_START), (x + LIP, -r - LIP_START - LIP_LAND),
               (x, -DEPTH), (x - WALL, -DEPTH)]
    return _prism([(side * px, z) for px, z in profile])


def back_top(origin_z):
    """The highest world Z of the open back's base, for a display origin at `origin_z`."""
    a = math.radians(ANGLE)
    return origin_z + (RUN / 2.0 + DRIFT) * math.sin(a) - CATCH * math.cos(a)


def pocket(side=1, reach=DEPTH):
    """The skirt's slot down to the catch, and the open back under it, `reach` plumb."""
    slot = _prism([(side * px, z) for px, z in [
        (FLEX_X, 1.0), (NECK_X, 1.0), (NECK_X, -CATCH), (FLEX_X, -CATCH)]], RUN)
    a = math.radians(ANGLE)
    base = cq.Wire.makePolygon([cq.Vector(side * px, y, -CATCH) for px, y in [
        (FLEX_X, -RUN / 2.0), (BACK_X, -RUN / 2.0), (BACK_X, RUN / 2.0 + DRIFT),
        (FLEX_X, RUN / 2.0 + DRIFT), (FLEX_X, -RUN / 2.0)]])
    back = cq.Solid.extrudeLinear(
        base, [], cq.Vector(0.0, -math.sin(a), -math.cos(a)) * reach)
    return slot.fuse(back)
