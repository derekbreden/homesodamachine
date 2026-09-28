"""Machine display covers with extra hook reach and 0.9 mm inset skirts."""

import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if p.name == 'hardware').parent
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/scripts')]
import display_cover as cover
from _cadq_export import export_assembly, note_write
from _materials import M_PETGF_BLACK, one_body
from flute_payload import cut

VARIANTS = {'display-cover-reach-05': 0.5, 'display-cover-reach-10': 1.0}
INSET = 0.9


def skirt(side, extension):
    r = cover.retention
    x = r.OUTER_X - INSET
    shoulder = -r.ROOT - r.LIP_START - extension
    tip = -r.DEPTH - extension
    profile = [(x-r.WALL, -r.ROOT), (x, -r.ROOT), (x, shoulder),
               (x+r.LIP, shoulder), (x+r.LIP, shoulder-r.LIP_LAND),
               (x, tip), (x-r.WALL, tip)]
    wire = cq.Wire.makePolygon([cq.Vector(side*px, -r.LENGTH/2, z)
                                for px, z in [*profile, profile[0]]])
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0, r.LENGTH, 0))


def build(extension):
    bezel = cover.rounded_prism(cover.cover_x, cover.cover_slope, cover.cover_corner_r,
                                -cover.dims.display_cover_thickness, 0)
    window = cover.rounded_prism(cover.window_x, cover.window_slope, cover.window_corner_r,
                                 -cover.retention.DEPTH-extension-1, 1)
    return bezel.fuse(skirt(-1, extension), skirt(1, extension)).cut(window).clean()


def main():
    for name, extension in VARIANTS.items():
        body = build(extension)
        assert body.isValid() and len(body.Solids()) == 1
        out = HERE/(name+'.step')
        export_assembly(one_body(cq.Workplane(obj=body), name, M_PETGF_BLACK), str(out))
        body.copy(mesh=False).exportStl(str(out.with_suffix('.stl')),
                                      tolerance=.005, angularTolerance=.05, relative=False)
        note_write(out.with_suffix('.stl'))
        cut(out, out.with_suffix('.stl'))
        print(f'{name}: {INSET:g} mm inset; {extension:g} mm extra reach; '
              f'{cover.retention.BEARING_SLIP+extension:g} mm nominal bearing clearance')


if __name__ == '__main__':
    main()
