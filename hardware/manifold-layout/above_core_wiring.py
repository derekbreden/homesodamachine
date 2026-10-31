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
from _materials import C_AC_HUB, C_GND, M_BRASS

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
WALL_BACK_FORE = ((0., 0., -1.), (0., -1., 0.), (-1., 0., 0.))
WALL_BACK_AFT = ((0., 0., -1.), (0., 1., 0.), (1., 0., 0.))
EAST_FLANK = ((0., -1., 0.), (0., 0., -1.), (1., 0., 0.))
WALL = 3.0
FIT = .15


def placements():
    """Native frames, electrical purpose and mechanical parent for every bus."""
    rows = {}

    def put(name, size, parent, rotation, xyz, purpose):
        rows[name] = dict(size=size, parent=parent, rotation=rotation,
                          translation_mm=tuple(xyz), purpose=purpose)

    # Mains branches sit below the ceiling PSU, west of the data jack.
    for name, x, z, purpose in (('wago-h', -85., 264., 'C14 live / PSU primary / relay 1 COM'),
                            ('wago-n', -54., 266., 'C14 neutral / PSU primary / compressor'),
                            ('wago-g', -85., 296.5, 'C14 PE / ring-terminal ground bus')):
        put(name, '413', 'back-top', PORTS_FORE,
            (x, 458.5, z), purpose)
    # Two rows on the board-facing back of V-B's wall. Levers open west;
    # wire mouths face away from the shared rear-half holder stock.
    for name, y, z, turn, purpose in (
            ('wago-sensors', 228.55, 286.1, WALL_BACK_FORE,
             'PCB J4 / temperature bus / flow meter common'),
            ('wago-v12', 228.55, 264., WALL_BACK_FORE,
             'PSU secondary / relay 2 COM / PCB J10 V12'),
            ('wago-gnd', 250.55, 264., WALL_BACK_AFT,
             'PSU secondary / pump negative / PCB J10 GND'),
            ('wago-reeds-b', 250.55, 286.1, WALL_BACK_AFT,
             'PCB J7 / reservoir B / carbonator reed common')):
        put(name, '413', 'cold-core', turn, (29.0, y, z), purpose)
    # These branch points travel with the complete front valve manifold.
    put('wago-mana', '420', 'front-top', EAST_FLANK, (95.20, 185.05, 277.),
        'J1 valve common and eight A-H coil branches')
    put('wago-manb', '415', 'front-top', EAST_FLANK, (95.05, 177.65, 243.),
        'J2 valve common, I/J/K coils and condenser fan')
    ground=layout.specification()['rear_plumbing']['ground-stack']
    put('ground-stack', 'ground-stack', 'back-top', ground['rotation'], ground['translation_mm'],
        'C14 earth feed and exposed-metal bond branches')
    return rows


def frame(name):
    return placements().get(name)


def owner(name):
    return placements()['ground-stack' if name=='ground-stack-insert' else name]['parent']


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
    placed=carry('ground-stack')
    insert=cq.Solid.makeCylinder(2.3,4.,cq.Vector(0,0,-4.)).cut(
        cq.Solid.makeCylinder(1.25,4.2,cq.Vector(0,0,-4.1)))
    result['ground-stack-insert']=(insert.moved(placed.where),M_BRASS,placed)
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
    """Actual three-ring clamp stack, independently of the bolt display envelope."""
    pose=placements()['ground-stack']
    landing=pose['translation_mm']
    return {'screw':'M3x8 SHCS', 'screw_length_mm':8.,
            'ring_count':3, 'tongue_thickness_mm':.8, 'washer_thickness_mm':.8,
            'clamped_thickness_mm':3.2, 'screw_projection_mm':4.8,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'parent':'back-top','landing_world_mm':landing,
            'axis_outward':layout.vector(pose['rotation'],(0.,0.,1.)),
            'pilot_diameter_mm':4., 'pilot_depth_mm':7., 'tip_air_mm':2.2,
            'blind_backing_mm':471.3-landing[1]-7.,
            'minimum_fluted_backing_mm':471.3-landing[1]-7.-.8,
            'boss_diameter_mm':10., 'radial_stock_mm':3.}


def _features(parent):
    additions, cuts, stations = [], [], []
    for name, pose in placements().items():
        if pose['parent'] != parent:
            continue
        stations.append({'name': name, **pose})
        if name == 'ground-stack':
            face=cq.Vector(*pose['translation_mm'])
            inward=cq.Vector(*layout.vector(pose['rotation'],(0.,0.,-1.)))
            additions.append(cq.Solid.makeCylinder(5.,8.,face,inward))
            cuts.append(cq.Solid.makeCylinder(2.,7.01,face-inward*.01,inward))
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
