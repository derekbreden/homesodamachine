"""TPU vent cup with an aft-facing 4 mm drain socket.

The scanned ASSE's exposed vent stem enters the vertical cup. A printed
quarter turn carries its open drain to a horizontal socket on native -X.
Both sockets retain a separate four-inch tie land. Native +Z points into
its vent mouth; the printable frame tips both bores upward at 45 degrees.
"""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference/multiplex-asse1022"))

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

from _rust_data import request as _request


def _data(**payload):
    return _request('part-data', 'part-data', {'part': 'asse-drain-adapter', **payload})


globals().update(_data()['values'])


def tube_mouth(vent_tip):
    return tuple(_data(method='tube_mouth', tip=vent_tip))


def numbers(*, installed=False):
    """The Rust scalar recipe, with the reference vent diameter when seated."""
    from _material_base import M_TPU_BLACK
    from _materials import linear
    inputs = {}
    if installed:
        import multiplex_asse1022 as bfp
        inputs['vent_diameter'] = bfp.VENT_D
    result = _data(installed=installed, color=list(linear(M_TPU_BLACK)), **inputs)['numbers']
    result['groove_centres'] = tuple(result['groove_centres'])
    result['print_shift'] = tuple(result['print_shift'])
    return result


def main(output=None):
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut('tooling','asse-drain-adapter',numbers(),out)
    from _part_output import summary
    print(f"asse-drain-adapter: {summary(result['bodies'][0])['volume']} cm3")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    main(args.output)
