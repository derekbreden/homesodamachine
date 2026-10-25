"""Two straight TPU cuffs for the native Multiplex ASSE body.

These nominal fit solids define the selected installed envelope. Socket bores
match the reference interfaces; no elastomer interference, seal, retention or
pressure qualification is represented. Each prints turned over, on its tube end.
"""

from functools import cache
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path.insert(0, str(HW / 'scripts'))
from _cadq_export import export_assembly
from _materials import M_TPU_BLACK, one_body

SIDES = ('inlet', 'outlet')
METAL_SOCKET_DEPTH = {'inlet': 13., 'outlet': 14.}
METAL_SOCKET_RADIUS = {'inlet': 8.575, 'outlet': 7.94}
METAL_WALL = 2.8
REDUCER_LENGTH = 5.
TUBE_SOCKET_DEPTH = 15.
TUBE_SOCKET_RADIUS = 3.175
TUBE_OUTER_RADIUS = 5.916
THROAT_RADIUS = 2.2
ASSE_OUTLET_X = 65.


@cache
def _axial(side):
    """Metal tip at Z=0; metal body +Z, tube mouth at Z=-20 mm."""
    depth, bore = METAL_SOCKET_DEPTH[side], METAL_SOCKET_RADIUS[side]
    outer = bore + METAL_WALL
    tube_end = -REDUCER_LENGTH-TUBE_SOCKET_DEPTH
    profile = [(outer, depth), (outer, 0.),
               (TUBE_OUTER_RADIUS, -REDUCER_LENGTH), (TUBE_OUTER_RADIUS, tube_end),
               (TUBE_SOCKET_RADIUS, tube_end), (TUBE_SOCKET_RADIUS, -REDUCER_LENGTH),
               (THROAT_RADIUS, -REDUCER_LENGTH), (THROAT_RADIUS, 0.),
               (bore, 0.), (bore, depth)]
    return (cq.Workplane('XZ').polyline(profile).close()
            .revolve(360, (0, 0), (0, 1)).val())


def build(side):
    """One job solid, its open metal socket mouth at Z=0."""
    return (_axial(side).rotate((0, 0, 0), (1, 0, 0), 180)
            .translate((0., 0., METAL_SOCKET_DEPTH[side])))


def assembly_shape(side):
    """Selected installed geometry in the ASSE flow-axis frame.

    The frame origin is the bare inlet tip, on the flow axis. The full bare
    ASSE reference has this origin at native (0, 0, 27).
    """
    shape = _axial(side).rotate((0, 0, 0), (0, 1, 0), 90)
    if side == 'outlet':
        shape = shape.rotate((0, 0, 0), (0, 0, 1), 180).translate((ASSE_OUTLET_X, 0., 0.))
    return shape


def main():
    from flute_payload import cut
    for side in SIDES:
        name = 'asse-' + side + '-cuff'
        step, stl = HERE / (name + '.step'), HERE / (name + '.stl')
        shape = build(side)
        export_assembly(one_body(shape, name, M_TPU_BLACK), str(step))
        cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
        cut(step, stl, preserve_print_triangles=True)
        print(f'{name}: {shape.Volume()/1000:.3f} cm3')


if __name__ == '__main__':
    main()
