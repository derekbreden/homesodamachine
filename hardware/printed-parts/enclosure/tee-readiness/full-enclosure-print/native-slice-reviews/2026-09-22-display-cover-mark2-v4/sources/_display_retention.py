"""Broad flexible cover skirts and their rigid retaining pockets.

Coordinates follow the machine display: X across, Y up the screen, Z out of the face.
The cover prints with its visible face upward.
"""

import cadquery as cq
from _enclosure_interface import display_inset_x, display_cover_slip

WALL = 2.0
LENGTH = 24.0
DEPTH = 34.0
LIP_HEIGHT = 3.0
ENGAGEMENT = 1.8
PRELOAD = 0.35
ROOF_AIR = 0.48
END_AIR = 0.4
OUTER_X = display_inset_x / 2.0 - display_cover_slip


def _prism(profile, length=LENGTH):
    wire = cq.Wire.makePolygon([cq.Vector(x, -length / 2.0, z)
                               for x, z in [*profile, profile[0]]])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, length, 0))


def skirt(side=1, seated=False):
    """One continuous side skirt with a lead-in and a flat retaining shoulder."""
    x = OUTER_X
    profile = [(x - WALL, -2), (x, -2), (x, -DEPTH + LIP_HEIGHT),
               (x + ENGAGEMENT, -DEPTH + LIP_HEIGHT),
               (x + ENGAGEMENT, -DEPTH + 1.8), (x, -DEPTH),
               (x - WALL, -DEPTH)]
    if seated:
        profile = [(px - PRELOAD * (-z - 2.0) / (DEPTH - LIP_HEIGHT - 2.0 - ROOF_AIR), z)
                   for px, z in profile]
    return _prism([(side * px, z) for px, z in profile])


def pocket(side=1):
    """The skirt's approach and the deeper groove under its retaining shoulder."""
    x = OUTER_X
    roof = -DEPTH + LIP_HEIGHT + ROOF_AIR
    profile = [(x - WALL - PRELOAD - END_AIR, 1.0),
               (x + END_AIR, 1.0), (x + END_AIR, -3.0),
               (x - PRELOAD, roof),
               (x + ENGAGEMENT + END_AIR, roof),
               (x + ENGAGEMENT + END_AIR, -DEPTH - END_AIR),
               (x - WALL - PRELOAD - END_AIR, -DEPTH - END_AIR)]
    return _prism([(side * px, z) for px, z in profile], LENGTH + 2.0 * END_AIR)


def stock(side=1):
    """The pocket's solid surround, continuing into the display housing."""
    x = OUTER_X
    return _prism([(side * px, z) for px, z in [
        (x - WALL - PRELOAD - END_AIR - WALL, -1.0),
        (x + ENGAGEMENT + END_AIR + WALL, -1.0),
        (x + ENGAGEMENT + END_AIR + WALL, -DEPTH - END_AIR - WALL),
        (x - WALL - PRELOAD - END_AIR - WALL, -DEPTH - END_AIR - WALL)]],
        LENGTH + 2.0 * (END_AIR + WALL))
