"""Two straight TPU cuffs for the native Multiplex ASSE body.

These nominal fit solids define the selected installed envelope. Socket bores
match the reference interfaces; no elastomer interference, seal, retention or
pressure qualification is represented. Each prints turned over, on its tube end.
"""

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


def numbers():
    """Live axial sections and print poses, without constructing native solids."""
    from _materials import M_TPU_BLACK, linear
    return dict(cuffs=[dict(side=side,profile=_profile(side),depth=METAL_SOCKET_DEPTH[side])
                       for side in SIDES],color=list(linear(M_TPU_BLACK)))


def main(output=None):
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut('tooling','asse-straight-cuffs',numbers(),out)
    for body in result['bodies']:
        print(f"{body['name']}: {body['volume']/1000:.3f} cm3")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    main(args.output)
