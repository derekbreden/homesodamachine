"""Low lift-off cover located in the silicone funnel's existing mouth.

Local Z=0 is the underside of the plate on the silicone brim. The whole top
is a flat bed face in the separate print export. The shallow skirt takes
sideways displacement; four local pads lightly interfere with the silicone.
"""

import functools
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ROOT / 'tools'),
                str(HERE.parent / 'funnel')]
import funnel
from _cadq_export import export_assembly, import_assembly
from _materials import M_PETG_BLACK, one_body
from docgen import substitute_md

PLATE_T = 3.0
OVERHANG = 1.5
SKIRT_DEPTH = 6.0
SKIRT_WALL = 3.0
RUNNING_AIR = 0.25
LEAD_H = 1.4
LEAD_INSET = 0.7
PAD_INTERFERENCE = 0.15
PAD_LENGTH = 16.0
PAD_Y = 22.0
PAD_LEAD_H = 1.6
PULL_WIDTH = 28.0
PULL_REACH = 4.0
PULL_RELIEF = 1.2

MOUTH_W = funnel.collar_w - 2 * funnel.collar_wall
MOUTH_D = funnel.collar_d - 2 * funnel.collar_wall
WIDTH = funnel.collar_w + 2 * (funnel.brim_overhang + OVERHANG)
DEPTH = funnel.collar_d + 2 * (funnel.brim_overhang + OVERHANG)
RADIUS = funnel.brim_corner_r + OVERHANG


def rounded(w, d, r, z0, z1, x=0.0, y=0.0):
    return funnel._rounded_box(w, d, r, z0, z1, x, y)


def pad(side, y):
    """Broad rooted pad; the lower ramp grows 0.9 mm over 1.6 mm rise."""
    outer = MOUTH_W / 2 + PAD_INTERFERENCE
    inner = outer - SKIRT_WALL
    wires = []
    for z, inset in ((-SKIRT_DEPTH, 0.9),
                     (-SKIRT_DEPTH + PAD_LEAD_H, 0.0), (0.0, 0.0)):
        x0, x1 = sorted((side * inner, side * (outer - inset)))
        wires.append(funnel._rounded_wire(x1 - x0, PAD_LENGTH, 0.6,
                                           z, (x0 + x1) / 2, y))
    return cq.Solid.makeLoft(wires, ruled=True)


def pads():
    return cq.Compound.makeCompound([pad(s, y) for s in (-1, 1) for y in (-PAD_Y, PAD_Y)])


@functools.cache
def build():
    plate = rounded(WIDTH, DEPTH, RADIUS, 0.0, PLATE_T)
    pull = rounded(PULL_WIDTH, 8.0, 3.0, 0.0, PLATE_T,
                   y=-DEPTH / 2 - PULL_REACH + 4.0)
    plate = plate.fuse(pull).clean()
    # The underside finger relief ends outside the silicone brim and never
    # pierces the plate. Its minimum closed section is 1.8 mm.
    relief = funnel._box(PULL_WIDTH + 2, PULL_REACH + 1,
                         -1.0, PULL_RELIEF, 0.0,
                         -DEPTH / 2 - (PULL_REACH + 1) / 2 + 0.5)
    plate = plate.cut(relief).clean()
    sw, sd = MOUTH_W - 2 * RUNNING_AIR, MOUTH_D - 2 * RUNNING_AIR
    sr = funnel.mouth_corner_r - RUNNING_AIR
    wires = [funnel._rounded_wire(sw - 2 * LEAD_INSET, sd - 2 * LEAD_INSET,
                                  sr - LEAD_INSET, -SKIRT_DEPTH),
             funnel._rounded_wire(sw, sd, sr, -SKIRT_DEPTH + LEAD_H),
             funnel._rounded_wire(sw, sd, sr, 0.01)]
    skirt = cq.Solid.makeLoft(wires, ruled=True)
    inside = rounded(sw - 2 * SKIRT_WALL, sd - 2 * SKIRT_WALL,
                      sr - SKIRT_WALL, -SKIRT_DEPTH - 1, 0.02)
    skirt = skirt.cut(inside).clean()
    body = plate.fuse(skirt).fuse(pads()).clean()
    assert body.isValid() and len(body.Solids()) == 1
    assert abs(body.BoundingBox().zmax - PLATE_T) < 1e-6
    return body


def placed(cx, cy, roof):
    return build().translate((cx, cy, roof))


def contact_reading(cover, silicone, cx, cy, roof):
    """Permit silicone contact only in the four declared friction-pad solids."""
    common = cover.intersect(silicone)
    mask = pads().translate((cx, cy, roof))
    return {'pad_contact_mm3': common.Volume(),
            'outside_pads_mm3': common.cut(mask).Volume() if common.Volume() else 0.0}


def print_shape():
    # Flat exterior on the bed, skirt and pads growing up. No support is
    # required underneath a liquid-side face.
    return build().rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, PLATE_T))


def main():
    out = HERE / 'funnel-cover.step'
    export_assembly(one_body(cq.Workplane(obj=build()), 'funnel-cover', M_PETG_BLACK), str(out))
    from flute_payload import cut
    native_stl = HERE / 'funnel-cover.stl'
    import_assembly(out)['funnel-cover'][0].copy(mesh=False).exportStl(
        str(native_stl), tolerance=0.01, angularTolerance=0.06, relative=False)
    cut(out, native_stl)
    print_out = HERE / 'funnel-cover-print.step'
    shape = print_shape()
    export_assembly(one_body(cq.Workplane(obj=shape), 'funnel-cover', M_PETG_BLACK), str(print_out))
    stl = HERE / 'funnel-cover-print.stl'
    import_assembly(print_out)['funnel-cover'][0].copy(mesh=False).exportStl(
        str(stl), tolerance=0.01, angularTolerance=0.06, relative=False)
    cut(print_out, stl)
    substitute_md(HERE / 'README.md', variables={
        'PLATE': f'{PLATE_T:g} mm', 'SKIRT': f'{SKIRT_DEPTH:g} mm',
        'WALL': f'{SKIRT_WALL:g} mm', 'WIDTH': f'{WIDTH:g} mm',
        'DEPTH': f'{DEPTH:.3f} mm', 'OVERHANG': f'{OVERHANG:g} mm',
        'AIR': f'{RUNNING_AIR:g} mm', 'PAD': f'{PAD_INTERFERENCE:g} mm',
        'PULL': f'{PULL_REACH:g} mm', 'PRINT_HEIGHT': f'{PLATE_T + SKIRT_DEPTH:g} mm',
    })
    print(f'-> cover STEP, print STEP, STL and payload; {build().Volume():.1f} mm3')


if __name__ == '__main__':
    main()
