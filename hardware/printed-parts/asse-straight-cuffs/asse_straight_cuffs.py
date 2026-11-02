"""Two straight TPU cuffs for the native Multiplex ASSE body.

These nominal fit solids define the selected installed envelope. Socket bores
match the reference interfaces; no elastomer interference, seal, retention or
pressure qualification is represented. Each prints turned over, on its tube end.
"""

from functools import cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path.insert(0, str(HW / 'scripts'))

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

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


def _profile(side):
    depth, bore = METAL_SOCKET_DEPTH[side], METAL_SOCKET_RADIUS[side]
    outer = bore + METAL_WALL
    tube_end = -REDUCER_LENGTH-TUBE_SOCKET_DEPTH
    return [(outer, depth), (outer, 0.),
               (TUBE_OUTER_RADIUS, -REDUCER_LENGTH), (TUBE_OUTER_RADIUS, tube_end),
               (TUBE_SOCKET_RADIUS, tube_end), (TUBE_SOCKET_RADIUS, -REDUCER_LENGTH),
               (THROAT_RADIUS, -REDUCER_LENGTH), (THROAT_RADIUS, 0.),
               (bore, 0.), (bore, depth)]


@cache
def _axial(side):
    """Metal tip at Z=0; metal body +Z, tube mouth at Z=-20 mm."""
    import cadquery as cq
    return (cq.Workplane('XZ').polyline(_profile(side)).close()
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


def numbers():
    """Live axial sections and print poses, without constructing native solids."""
    from _materials import M_TPU_BLACK, linear
    return dict(cuffs=[dict(side=side,profile=_profile(side),depth=METAL_SOCKET_DEPTH[side])
                       for side in SIDES],color=list(linear(M_TPU_BLACK)))


def _native_main(output=None):
    import cadquery as cq
    from _cadq_export import export_assembly
    from _materials import M_TPU_BLACK, one_body
    from flute_payload import cut
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    for side in SIDES:
        name = 'asse-' + side + '-cuff'
        step, stl = out / (name + '.step'), out / (name + '.stl')
        shape = build(side)
        export_assembly(one_body(shape, name, M_TPU_BLACK), str(step))
        cq.exporters.export(shape, str(stl), tolerance=.025, angularTolerance=.08)
        cut(step, stl, preserve_print_triangles=True)
        print(f'{name}: {shape.Volume()/1000:.3f} cm3')


def main(output=None, *, native=False):
    if native:
        return _native_main(output)
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut('tooling','asse-straight-cuffs',numbers(),out)
    for body in result['bodies']:
        print(f"{body['name']}: {body['volume']/1000:.3f} cm3")


def __getattr__(name):
    if name == 'cq':
        import cadquery
        return cadquery
    if name == 'export_assembly':
        from _cadq_export import export_assembly
        return export_assembly
    if name in ('M_TPU_BLACK','one_body'):
        import _materials
        return getattr(_materials,name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--native',action='store_true')
    args = parser.parse_args()
    main(args.output,native=args.native)
