"""One square-cut length of owned CARGEN foam around the vertical soda riser."""
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path.insert(0, str(HW / 'scripts'))
from _cadq_export import export_assembly
from _materials import M_NITRILE_BLACK, one_body

NAME = 'soda-rise-insulation'
CENTER_XY = (50., 354.3696)
BOTTOM_Z = 264.5
LENGTH = 15.
INSIDE_DIAMETER = 6.35
OUTSIDE_DIAMETER = 25.4


def build():
    """Nominal uncompressed stock in the installed enclosure-world frame."""
    return (cq.Workplane('XY').workplane(offset=BOTTOM_Z)
            .center(*CENTER_XY).circle(OUTSIDE_DIAMETER / 2.)
            .circle(INSIDE_DIAMETER / 2.).extrude(LENGTH).val())


def main():
    export_assembly(one_body(build(), NAME, M_NITRILE_BLACK),
                    str(HERE / (NAME + '.step')))


if __name__ == '__main__':
    main()
