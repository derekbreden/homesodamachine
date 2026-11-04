"""Accepted2mm PET-GF R14 holder with3mm legs, in its printable frame."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path[:0] = [str(HW/'scripts'), str(HW/'manifold-layout')]
import soda_inlet


def numbers():
    """Live dimensions from the production inlet plan, in the printable frame."""
    from _materials import M_PETGF_BLACK, linear
    return {**soda_inlet.holder_geometry_numbers(), 'color': list(linear(M_PETGF_BLACK))}


def main(output=None):
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('tooling', 'soda-bend-holder', numbers(), out)
    print(f"soda-bend-holder: {said['bodies'][0]['volume']/1000.:.3f} cm3")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    main(args.output)
