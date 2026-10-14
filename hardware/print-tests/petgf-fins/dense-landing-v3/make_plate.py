"""Prepare a dense-tooth candidate using the same short-span comparison; no send."""
from pathlib import Path
import importlib.util
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'short-spans-v2'
sys.path.insert(0, str(BASE))
spec = importlib.util.spec_from_file_location('short_span_plate', BASE / 'make_plate.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

# Retain the corner contacts. Seventeen intermediate teeth leave a nominal
# 0.1125 mm gap at the regular pitch, instead of the sparse pattern's 1.5 mm.
DENSE_TEETH = [(0.4, 0.8)] + [(1.1 + i * .6125, .5) for i in range(17)] + [(11.6, .8)]


def tag(fan):
    part = base.block(18, 8, base.FOOT_HEIGHT)
    part = part.union(base.label(f'DENSE {fan}', 2.25, (9, 4, base.FOOT_HEIGHT), rotation=0))
    return part.clean(), {'kind': 'plate_identifier', 'part_fan_percent': fan,
                          'contact_pattern': 'dense 19 lower teeth'}


def main():
    base.HERE = HERE
    base.stem = lambda fan: f'2026-10-14-fin-v3-dense-fan{fan}-petgf-left04-z004-mark2'
    base.tag = tag
    base.make(0, lower_teeth=DENSE_TEETH, fin_prefix='D')


if __name__ == '__main__':
    main()
