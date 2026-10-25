"""Accepted2mm PET-GF R14 holder with3mm legs, in its printable frame."""
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path[:0] = [str(HW/'scripts'), str(HW/'manifold-layout')]
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
import soda_inlet


def build():
    return soda_inlet.holder_native()


def main():
    from flute_payload import cut
    step = HERE/'soda-bend-holder.step'
    stl = HERE/'soda-bend-holder.stl'
    shape = build()
    export_assembly(one_body(shape, 'soda-bend-holder', M_PETGF_BLACK), str(step))
    cq.exporters.export(shape, str(stl), tolerance=.01, angularTolerance=.1)
    cut(step, stl, preserve_print_triangles=True)
    print(f'soda-bend-holder: {shape.Volume()/1000.:.3f} cm3')


if __name__ == '__main__':
    main()
