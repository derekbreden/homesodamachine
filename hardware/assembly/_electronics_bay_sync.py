"""Figure-sync entry point and checked relay GPIO names for electronics-bay.md.

The current mounting and wiring procedure uses its linked native geometry and
wire schedule directly. It contains no generated numeric figure markers.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools' / 'docgen').is_dir())
sys.path.insert(0, str(ROOT / 'tools'))
from docgen import substitute_md

# check_pinmap.py compares these procedure assignments with the board and pinout.
relay_compressor_gpio = 19
relay_diaphragm_gpio = 2


def main():
    substitute_md(HERE / 'electronics-bay.md', variables={})
    print('-> electronics-bay.md')


if __name__ == '__main__':
    main()
