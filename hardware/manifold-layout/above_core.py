"""Production above-core placements and interfaces, in enclosure millimetres.

Native reference poses carry ports, holes and electrical axes with their bodies.
The data file is independent of the exploratory viewers and their build scripts.
"""

import functools
from pathlib import Path

from _layout_data import data as _data, read_json as _read_json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


@functools.cache
def specification():
    return _read_json(HERE / 'above-core.json')


def pose(name):
    return specification()['parts'][name]


def native_pose(name):
    p = pose(name)
    return p['rotation'], p['translation_mm']


def snapshot_pose(name):
    return specification()['snapshots'][name]


def logical_connections():
    """Logical circuit endpoints and their ordered physical tube/fitting members."""
    return specification()['logical_connections']


def cap_lid_pose():
    return specification()['cap_lid_pose']


def core_equipment_names():
    return frozenset(_data('equipment-names'))



def valve_names():
    return tuple(_data('valve-names'))


cap_pose = cap_lid_pose


def vector(rotation, point):
    return tuple(_data('vector', rotation=rotation, point=point))


def point(frame, xyz):
    return tuple(_data('point', frame=frame, point=xyz))


def inverse_point(frame, xyz):
    return tuple(_data('inverse-point', frame=frame, point=xyz))


def world_to_cap(xyz):
    return inverse_point(cap_lid_pose(), xyz)


def frame_location(frame):
    import cadquery as cq
    from OCP.gp import gp_Trsf
    r, t = frame['rotation'], frame['translation_mm']
    transform = gp_Trsf()
    transform.SetValues(r[0][0], r[0][1], r[0][2], t[0],
                        r[1][0], r[1][1], r[1][2], t[1],
                        r[2][0], r[2][1], r[2][2], t[2])
    return cq.Location(transform)


def location(name):
    return frame_location(pose(name))


def place(shape, name):
    return shape.moved(location(name))


def carry(name):
    frame = pose(name)

    def carried(station):
        xyz, axis = station
        return point(frame, xyz), vector(frame['rotation'], axis)

    carried.where = frame_location(frame)
    return carried
