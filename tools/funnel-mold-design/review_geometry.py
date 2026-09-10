"""Review the published mold meshes in their actual print orientations.

Run after publication with the project's CadQuery Python. Picks remain in the
assembly frame. The core prints inverted on its plate back.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'hardware/scripts'))
import geometry_lint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    args = parser.parse_args()
    geometry_lint.PRINT_UP['core'] = -1.0
    return geometry_lint.main([str(args.models/(name+'.stl'))
                               for name in ('cavity', 'core')])


if __name__ == '__main__':
    sys.exit(main())
