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

from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'asse-straight-cuffs', **payload})


globals().update(_data()['values'])
SIDES = tuple(SIDES)


def _profile(side):
    return [tuple(point) for point in _data()['profiles'][side]]


def numbers():
    from _materials import M_TPU_BLACK, linear
    result = _data(color=list(linear(M_TPU_BLACK)))['numbers']
    for cuff in result['cuffs']:
        cuff['profile'] = [tuple(point) for point in cuff['profile']]
    return result


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
