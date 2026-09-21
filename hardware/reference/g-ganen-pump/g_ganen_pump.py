"""G Ganen B07F35PTFR scan-derived external reference.

The solids are clearance envelopes, not material volumes: pump internals and
unobserved purchased-part cavities are not mass or strength inputs. The frame is
X=0 at the motor/head seam, +X toward the motor rear, and Z=0 at the retained
average unloaded foot plane. Sliding rubber feet are independent bodies.

The intended +90 degree enclosure Z rotation maps local +Y to enclosure -X.
Derek identifies flow toward enclosure -X, making +Y discharge and -Y suction.
"""
from pathlib import Path
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent


def parameters():
    return json.loads((HERE/'reference-parameters.json').read_text())


def port(name):
    """A measured barb tip and outward axis in the reference frame."""
    row = parameters()['ports'][name]
    return tuple(row['tip_mm']), tuple(row['outward_axis'])


def suction():
    return port('port_yminus')


def discharge():
    return port('port_yplus')


def mount_slots():
    """Observed independent slider slots; this is not an immutable hole pattern."""
    return tuple(parameters()['mounting_feet'])


def port_profile(name):
    """Per-port exterior profile; scanned length is not a hose-retention rating."""
    return parameters()['ports'][name]


def sliding_rails():
    """Visible fixed rail observations; hidden clip and hard travel limits are open."""
    return tuple(parameters()['sliding_rails'])


def mount_seat_z():
    """The retained datum plane, not a claim that free rubber feet are coplanar."""
    return 0.


def _wire(vertices):
    return cq.Wire.makePolygon([cq.Vector(*point) for point in vertices], close=True)


def _casing(data):
    wires = [_wire(row['vertices_mm']) for row in data['casing_sections']]
    return cq.Solid.makeLoft(wires, ruled=True)


def _barb(row):
    axis = cq.Vector(*row['outward_axis'])
    tip = cq.Vector(*row['tip_mm'])
    rings = [cq.Wire.makeCircle(station['radius_mm'],
                                tip+axis*station['distance_from_tip_mm'], axis)
             for station in row['profile']]
    return cq.Solid.makeLoft(rings, ruled=True)


def _foot(row):
    # All four purchased rubber feet are identical. Observed free-foot poses
    # remain individual, but their geometry comes from one shared reference.
    sys.path.insert(0, str(HERE/'common-foot'))
    from g_ganen_foot import observed_foot
    return observed_foot(row)


def _hull(row):
    vertices = row['vertices_mm']
    faces = [cq.Face.makeFromWires(_wire([vertices[index] for index in triangle]))
             for triangle in row['triangles']]
    return cq.Solid.makeSolid(cq.Shell.makeShell(faces)).clean()


def build_parts():
    data = parameters()
    parts = {'rigid_casing_envelope': _casing(data)}
    for row in data['casing_shell_envelopes']:
        parts[row['id']+'_external_envelope'] = _hull(row['external_envelope'])
    can = data['motor_can_envelope']
    axis = cq.Vector(*can['axis_direction'])
    origin = cq.Vector(*can['axis_point_mm'])
    start_x, end_x = can['x_stations_mm']
    start = origin+axis*((start_x-origin.x)/axis.x)
    parts['motor_can_vent_filled_envelope'] = cq.Solid.makeCylinder(
        can['radius_mm'], (end_x-start_x)/axis.x, start, axis)
    for row in data['crown_round_heads']+data['crown_molded_features']:
        parts[row['id']+'_external_envelope'] = _hull(row['external_envelope'])
    for name, row in data['ports'].items():
        parts[name+'_barb_envelope'] = _barb(row)
        parts[name+'_root_envelope'] = _hull(row['root_envelope'])
    for row in data['mounting_feet']:
        parts[row['id']+'_observed_rubber_slider_envelope'] = _foot(row)
    return parts


def build():
    """Occupied external reference; see the parameter ledger's qualification limits."""
    return cq.Workplane(obj=cq.Compound.makeCompound(list(build_parts().values())))


def build_scene():
    return build().val()


def build_assembly():
    assembly = cq.Assembly(name='g-ganen-pump')
    for name, shape in build_parts().items():
        color = ((.18, .19, .20) if 'rubber_slider' in name else
                 (.64, .67, .70) if 'round_head' in name or 'motor_can' in name else
                 (.31, .34, .37))
        assembly.add(shape, name=name, color=cq.Color(*color))
    return assembly


def export(path):
    """Canonical native assembly and its viewer mesh; no shared build trace."""
    sys.path.insert(0, str(HERE.parents[1]/'scripts'))
    from _cadq_export import export_assembly
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    export_assembly(build_assembly(), path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path,
                        default=HERE/'g-ganen-pump.step')
    args = parser.parse_args()
    export(args.out)
    print(args.out)
