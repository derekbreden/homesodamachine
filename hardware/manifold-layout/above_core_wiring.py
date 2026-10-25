"""Electrical junctions placed at their actual branches in the above-core layout.

All component and feature shapes use enclosure-world millimetres. Junctions
follow their named back-top, front-top or cold-core mounting parent.
``cap_features`` supplies stock and cutters for the core lid;
``shell_features`` supplies the features for a named enclosure quadrant.
"""
from functools import cache
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parent
sys.path.insert(0, str(HW / 'scripts'))
import above_core as layout
from _cadq_export import import_step
from _materials import C_AC_HUB, C_GND

REFERENCES = {
    '413': HW / 'reference/wago-221/wago-221-413.step',
    '415': HW / 'reference/wago-221/wago-221-415.step',
    '420': HW / 'reference/wago-221/wago-221-420.step',
    'ground-stack': HW / 'reference/ground-ring-stack/ground-ring-stack.step',
}
SIZES = {'413': (18.8, 18.6, 8.4, 3, 1),
         '415': (30.0, 18.6, 8.4, 5, 1),
         '420': (29.8, 18.3, 15.8, 10, 2)}
IDENTITY = ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))
PORTS_WEST = ((0., -1., 0.), (1., 0., 0.), (0., 0., 1.))
PORTS_FORE = ((-1., 0., 0.), (0., -1., 0.), (0., 0., 1.))
EAST_FLANK = ((0., -1., 0.), (0., 0., -1.), (1., 0., 0.))
WALL = 3.0
FIT = .15


def placements():
    """Native frames, electrical purpose and mechanical parent for every bus."""
    rows = {}

    def put(name, size, parent, rotation, xyz, purpose):
        rows[name] = dict(size=size, parent=parent, rotation=rotation,
                          translation_mm=tuple(xyz), purpose=purpose)

    # Rear-wall mains branches stay beside C14 and relay 1.
    # The 19.5 mm pitch clears each lower lever
    # beneath the next holder's floor.
    for name, z, purpose in (('wago-h', 292.5, 'C14 live / PSU primary / relay 1 COM'),
                            ('wago-n', 312.0, 'C14 neutral / PSU primary / compressor'),
                            ('wago-g', 331.5, 'C14 PE / ring-terminal ground bus')):
        put(name, '413', 'back-top', PORTS_FORE,
            (-34., 440. if name=='wago-n' else 454.5, z), purpose)
    # The core junctions face the PCB and stagger their wire mouths around the
    # B-draw passage. Their blank-backed wells sit wholly on the core lid.
    for name, y, purpose in (('wago-sensors', 195., 'PCB J4 / temperature bus / flow meter common'),
                            ('wago-v12', 218., 'PSU secondary / relay 2 COM / PCB J10 V12'),
                            ('wago-gnd', 242., 'PSU secondary / pump negative / PCB J10 GND'),
                            ('wago-reeds-b', 265., 'PCB J7 / reservoir B / carbonator reed common')):
        put(name, '413', 'cold-core', PORTS_WEST, (7.5, y, 256.4), purpose)
    # These branch points travel with the complete front valve manifold.
    put('wago-mana', '420', 'front-top', EAST_FLANK, (95.20, 176.9, 277.),
        'J1 valve common and eight A-H coil branches')
    put('wago-manb', '415', 'front-top', EAST_FLANK, (95.05, 173.2, 243.),
        'J2 valve common, I/J/K coils and condenser fan')
    put('ground-stack', 'ground-stack', 'cold-core', IDENTITY, (45., 195., 259.4),
        'C14 earth feed and exposed-metal bond branches')
    return rows


def frame(name):
    return placements().get(name)


def owner(name):
    return placements()[name]['parent']


def carry(name):
    pose = placements()[name]

    def carried(station):
        xyz, axis = station
        return layout.point(pose, xyz), layout.vector(pose['rotation'], axis)
    carried.where = layout.frame_location(pose)
    return carried


@cache
def components():
    result = {}
    for name, pose in placements().items():
        native = import_step(REFERENCES[pose['size']]).val()
        placed = carry(name)
        result[name] = (native.moved(placed.where),
                        C_GND if name == 'ground-stack' else C_AC_HUB, placed)
    return result


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def _well(name):
    """Closed-section rear-half well; both lever faces remain free at the front.

    The connector inserts butt-first along its own -Y axis. Uniform 3 mm stock
    surrounds the blank rear half, with the shared 0.15 mm fit allowance.
    """
    pose = placements()[name]
    width, depth, height, _poles, _rows = SIZES[pose['size']]
    # The front manifold's A-fill tube passes the upper edge of this well.
    # Keep its open mouth behind that path while retaining the blank rear half.
    front = -.75 if name == 'wago-mana' else 0.
    rear = -depth/2-FIT-WALL
    if pose['parent']=='back-top':
        rear=min(rear,pose['translation_mm'][1]-466.95)
    stock = _box(-width/2-FIT-WALL, width/2+FIT+WALL,
                 rear, front, -FIT-WALL, height+FIT+WALL)
    pocket = _box(-width/2-FIT, width/2+FIT,
                  -depth/2-FIT, 1., -FIT, height+FIT)
    location = carry(name).where
    return stock.moved(location), pocket.moved(location)


def _union(shapes):
    shapes = list(shapes)
    if not shapes:
        return None
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.fuse(shape)
    return result.clean()


def ground_fastener_datums():
    """Actual five-ring clamp stack, independently of the bolt display envelope."""
    landing=placements()['ground-stack']['translation_mm'][2]
    # cap_lid_pose maps native lid Z0, its underside; cap_face_z_mm is the top.
    return {'screw':'M3x10 SHCS', 'screw_length_mm':10.,
            'ring_count':5, 'tongue_thickness_mm':.8, 'washer_thickness_mm':.8,
            'clamped_thickness_mm':4.8, 'screw_projection_mm':5.2,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'landing_z_mm':landing, 'pilot_diameter_mm':4., 'pilot_depth_mm':7.,
            'pilot_bottom_z_mm':landing-7., 'tip_air_mm':1.8,
            'blind_backing_mm':landing-7.-layout.cap_lid_pose()['translation_mm'][2],
            'boss_diameter_mm':10., 'radial_stock_mm':3.}


def _features(parent):
    additions, cuts, stations = [], [], []
    for name, pose in placements().items():
        if pose['parent'] != parent:
            continue
        stations.append({'name': name, **pose})
        if name == 'ground-stack':
            x, y, z = pose['translation_mm']
            additions.append(cq.Solid.makeCylinder(5., z-253.4, cq.Vector(x, y, 253.4)))
            cuts.append(cq.Solid.makeCylinder(2., 8., cq.Vector(x, y, z-7.)))
        else:
            stock, pocket = _well(name)
            additions.append(stock)
            cuts.append(pocket)
    return {'add': _union(additions), 'cut': _union(cuts), 'stations': stations,
            'frame': 'enclosure world XYZ; invert cap_lid_pose for core-lid construction'}


def cap_features():
    """World-frame additions/cutters; fuse after fluid cuts, then cut pockets."""
    return _features('cold-core')


def shell_features(parent):
    """World-frame additions/cutters for ``front-top`` or ``back-top``.

    Cut pockets after stock is joined. The front-top wells use the same native
    manifold stations as their purchased components; omit duplicate side wells.
    """
    return _features(parent)


def driver_columns():
    """PSU terminal driver approaches along its carried native +Z screw axes."""
    pose = layout.pose('psu')
    axis = layout.vector(pose['rotation'], (0., 0., 1.))
    result = {}
    for side in (-1, 1):
        for x in (-4., 4.):
            xyz = layout.point(pose, (x, side*48.5, 13.7))
            limits = (-107.5, 107.5, 0., 473.5, 0., 355.)
            reach = min((limits[2*i+(1 if value>0 else 0)]-xyz[i])/value
                        for i,value in enumerate(axis) if abs(value)>1e-9)
            result[f'psu-{side:+}-{x:+g}'] = cq.Solid.makeCylinder(
                3., reach, cq.Vector(*xyz), cq.Vector(*axis))
    return result
