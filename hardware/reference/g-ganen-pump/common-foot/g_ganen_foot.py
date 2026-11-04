"""Shared purchased G Ganen rubber slider reference, in its nominal installed frame.

Local X follows the rail, +Y points outward, and Z=0 is the bearing plane. Four
identical feet are a direct owner observation; the pad is nominally 7 mm thick.
Visible outlines, relief mouths and slot are rounded scan measurements. This is
not a replacement-foot design or a qualification of the hidden rail interface.
"""
from functools import lru_cache
from pathlib import Path
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('g_ganen_foot')
globals().update({name: _reference_values[name] for name in ('PAD_THICKNESS', 'SLOT_Y', 'WIDTH', 'SLOT_WIDTH', 'SLOT_LENGTH', 'CLIP_AXIAL_INTERVAL', 'PROFILE_YZ')})

# This is the axial extent of the visible extruded rubber clip. It defines a
# conservative fully-engaged position, not a hard stop or partial-overhang limit.

# Exposed axial end-face outline. The upper open C-mouth is observed directly
# on the rear +Y foot in pass 02; fixed continuous rail points are excluded by
# their normal and axial station. Straight segments are a simplified reference.


def parameters():
    return _reference_data('g_ganen_foot', 'parameters', (), {})


def rail_engagement_interval():
    return _reference_data('g_ganen_foot', 'rail_engagement_interval', (), {})


def _profile_prism(vertices, x0, width):
    plane = cq.Plane(origin=(x0, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    return cq.Workplane(plane).polyline(vertices).close().extrude(width).val()


@lru_cache(maxsize=1)
def build_foot():
    """One nominal identical foot with exposed slot, C-mouth and lower reliefs."""
    body = _profile_prism(PROFILE_YZ, -WIDTH/2, WIDTH)
    # D-shaped outer pad: an analytic semicircular nose joins parallel sides.
    back = cq.Solid.makeBox(WIDTH, 20, 25, cq.Vector(-WIDTH/2, -20, 0))
    nose = cq.Solid.makeCylinder(9.0, 25, cq.Vector(0, 0, 0))
    body = body.intersect(back.fuse(nose))
    # The visible underside recesses retain side cheeks and a central web.
    pocket = ((-11.0, -1.0), (-4.0, -1.0), (-4.0, 1.0),
              (-6.7, 5.0), (-9.1, 3.4), (-11.0, 2.0))
    for x0 in (-7.0, 1.2):
        body = body.cut(_profile_prism(pocket, x0, 5.8))
    # Rounded visible screw opening. Its complete lower scan sections are
    # 4.07..4.67 wide and 6.38..6.92 long; only the lower mouth is well observed.
    slot = (cq.Workplane('XY').workplane(offset=-1)
            .slot2D(SLOT_LENGTH, SLOT_WIDTH, 90).extrude(12).val())
    body = body.cut(slot).clean()
    if not body.isValid() or len(body.Solids()) != 1:
        raise ValueError('Common G Ganen foot must be one valid native solid')
    return body


def placed_foot(station_x, side, slot_y=SLOT_Y):
    """One identical nominal foot, rigidly installed on either side of the pump."""
    if side not in (-1, 1):
        raise ValueError('side must be -1 or +1')
    shape = build_foot()
    if side < 0:
        shape = shape.rotate((0, 0, 0), (0, 0, 1), 180)
    return shape.translate((float(station_x), side*abs(float(slot_y)), 0))


def observed_placement(row):
    pose = _reference_data('g_ganen_foot', 'observed_pose', (row,), {})
    return cq.Location(cq.Plane(origin=cq.Vector(*pose['origin']),
                                xDir=cq.Vector(*pose['x']), normal=cq.Vector(*pose['z'])))


def observed_foot(row):
    return build_foot().moved(observed_placement(row))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(build_foot(), str(args.out))
    print(args.out)
