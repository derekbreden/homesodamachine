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
PAD_THICKNESS = 7.0
SLOT_Y = 38.5
WIDTH = 18.0
SLOT_WIDTH = 4.5
SLOT_LENGTH = 6.8
# This is the axial extent of the visible extruded rubber clip. It defines a
# conservative fully-engaged position, not a hard stop or partial-overhang limit.
CLIP_AXIAL_INTERVAL = (-9.0, 9.0)

# Exposed axial end-face outline. The upper open C-mouth is observed directly
# on the rear +Y foot in pass 02; fixed continuous rail points are excluded by
# their normal and axial station. Straight segments are a simplified reference.
PROFILE_YZ = (
    (-10.5, 0.0), (9.0, 0.0), (9.0, PAD_THICKNESS),
    (-3.5, PAD_THICKNESS), (-5.5, 9.4), (-10.0, 9.4),
    (-10.5, 10.0), (-10.5, 12.0), (-10.0, 15.4),
    (-10.9, 15.8), (-11.2, 16.2), (-13.5, 15.1),
    (-14.4, 15.6), (-14.5, 16.3), (-12.8, 17.8),
    (-13.5, 18.4), (-14.2, 18.4), (-14.9, 18.0),
    (-15.7, 17.9), (-16.0, 9.7), (-12.2, 8.4),
    (-12.2, 7.5), (-13.5, 4.2), (-12.2, 2.1),
)


def parameters():
    return {
        'frame': 'slot centre; X rail, +Y outward, Z0 bearing',
        'identical_feet': True,
        'pad_thickness_mm': PAD_THICKNESS,
        'axial_width_mm': WIDTH,
        'outward_nose_radius_mm': 9.0,
        'slot_width_mm': SLOT_WIDTH,
        'slot_length_mm': SLOT_LENGTH,
        'slot_long_axis': '+Y',
        'installed_slot_y_abs_mm': SLOT_Y,
        'clip_axial_interval_mm': list(CLIP_AXIAL_INTERVAL),
        'visible_profile_yz_mm': [list(p) for p in PROFILE_YZ],
        'undercuts': 'two visible underside reliefs, separated by a central rib',
        'qualification': 'Purchased-part visible geometry reference. The hidden rail cavity and elastomer compliance are not qualified for manufacture.',
        'travel_scope': 'Full axial engagement is a chosen mounting datum; scan observations include partially overhanging feet and do not establish hard stops.',
    }


def rail_engagement_interval():
    return CLIP_AXIAL_INTERVAL


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
    """Rigid pose of the same common shape at the first retained observed foot."""
    import numpy as np
    section = row['pose_observations'][0]['local_slot_sections']
    origin = np.asarray(section['local_origin_reference_mm'], dtype=float)
    z = np.asarray(section['reference_to_local_rotation'], dtype=float)[2]
    side = -1 if 'yminus' in row['id'] else 1
    y = np.asarray((0., float(side), 0.)) - z*z[1]*side
    y /= np.linalg.norm(y)
    x = np.cross(y, z)
    rotation = np.column_stack((x, y, z))
    matrix = np.eye(4); matrix[:3, :3] = rotation; matrix[:3, 3] = origin
    return cq.Location(cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(*x), normal=cq.Vector(*z)))


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
