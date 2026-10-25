"""Empty, screw-fastened roof closure above the electronics bay."""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == 'hardware')
sys.path[:0] = [str(HW / 'scripts'), str(HW / 'printed-parts/cadlib'),
               str(HERE.parent / 'enclosure')]

import cadquery as cq
import _above_core_shell as interface
from _cadq_export import export_assembly, import_assembly
from _materials import M_PETGF_BLACK, one_body
from flute_payload import cut
from print_mesh import write_print_stl


def build():
    p = interface.access_plan()['panel']
    return interface.access_panel().translate((-(p['xmin']+p['xmax'])/2,
                                               -(p['ymin']+p['ymax'])/2, -p['zmin']))


def main():
    step, stl = HERE / 'electronics-access-panel.step', HERE / 'electronics-access-panel.stl'
    export_assembly(one_body(cq.Workplane(obj=build()), 'electronics-access-panel',
                             M_PETGF_BLACK), str(step))
    write_print_stl(import_assembly(step)['electronics-access-panel'][0], stl,
                    tol=.02, angle=.08)
    cut(step, stl)


if __name__ == '__main__':
    main()
