"""Four removable snap caps for the rear inlet equipment."""
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name=='hardware')
sys.path[:0] = [str(HW/'manifold-layout'),str(HW/'scripts'),str(HW/'printed-parts/cadlib')]
import rear_plumbing
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body

NAMES = ('asse-snap-cap','pisco-snap-cap','meter-snap-cap','regulator-snap-cap')


def printable(name):
    shape = rear_plumbing.seats()[name]
    if name=='meter-snap-cap':
        shape = shape.rotate((0,0,0),(0,1,0),-90.)
    bounds = shape.BoundingBox()
    return shape.translate((-(bounds.xmin+bounds.xmax)/2.,
                            -(bounds.ymin+bounds.ymax)/2.,-bounds.zmin))


def main():
    import flute_payload
    for name in NAMES:
        shape = printable(name)
        step,stl = HERE/(name+'.step'),HERE/(name+'.stl')
        export_assembly(one_body(shape,name,M_PETGF_BLACK),str(step))
        cq.exporters.export(shape,str(stl),tolerance=.02,angularTolerance=.08)
        flute_payload.cut(step,stl,preserve_print_triangles=True)
        print(f'{name}: {shape.Volume()/1000.:.2f} cm³',flush=True)


if __name__=='__main__':
    main()
