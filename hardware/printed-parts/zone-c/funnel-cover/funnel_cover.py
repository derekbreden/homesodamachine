"""Low lift-off cover located in the silicone funnel's existing mouth.

Local Z=0 is the underside of the plate on the silicone brim. The whole top
is a flat bed face in the separate print export. The continuous shallow skirt
locates the cover sideways; the plate rests on the silicone brim under gravity.

The Rust kernel cuts both file sets from `numbers()`.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts/_rust_part.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(ROOT / 'tools'),
                str(HERE.parent / 'funnel')]
if __name__ == '__main__':
    import _rust_part
    _rust_part.start()

import funnel
from _materials import M_PETG_BLACK, linear
from docgen import substitute_md

PLATE_T = 3.0
OVERHANG = 1.5
SKIRT_DEPTH = 6.0
SKIRT_WALL = 3.0
RUNNING_AIR = 0.25
LEAD_H = 1.4
LEAD_INSET = 0.7
FRONT_EXTENSION = 4.0
FRONT_RELIEF = 1.2
CUT_OVERRUN = 1.0
SKIRT_PLATE_OVERLAP = 0.01
INNER_CUT_OVERLAP = 0.02

MOUTH_W = funnel.collar_w - 2 * funnel.collar_wall
MOUTH_D = funnel.collar_d - 2 * funnel.collar_wall
WIDTH = funnel.collar_w + 2 * (funnel.brim_overhang + OVERHANG)
SEATED_DEPTH = funnel.collar_d + 2 * (funnel.brim_overhang + OVERHANG)
DEPTH = SEATED_DEPTH + FRONT_EXTENSION


def _skirt_dimensions():
    return (MOUTH_W - 2 * RUNNING_AIR, MOUTH_D - 2 * RUNNING_AIR,
            funnel.mouth_corner_r - RUNNING_AIR)


def numbers():
    """The plate, lifting relief and locating skirt in the cover's seating frame."""
    sw, sd, sr = _skirt_dimensions()
    return {
        'name': 'funnel-cover', 'print_name': 'funnel-cover-print',
        'color': [float(v) for v in linear(M_PETG_BLACK)],
        'plate_half_size': [WIDTH / 2, SEATED_DEPTH / 2],
        'plate_corner_radius': funnel.brim_corner_r + OVERHANG,
        'plate_thickness': PLATE_T,
        'front_extension': FRONT_EXTENSION,
        'relief_size': [WIDTH + 2 * CUT_OVERRUN, FRONT_EXTENSION + CUT_OVERRUN],
        'relief_z': [-CUT_OVERRUN, FRONT_RELIEF],
        'relief_center_y': -SEATED_DEPTH / 2 - (FRONT_EXTENSION + CUT_OVERRUN) / 2 + 0.5,
        'skirt_sections': [
            [sw - 2 * LEAD_INSET, sd - 2 * LEAD_INSET, sr - LEAD_INSET, -SKIRT_DEPTH],
            [sw, sd, sr, -SKIRT_DEPTH + LEAD_H],
            [sw, sd, sr, SKIRT_PLATE_OVERLAP],
        ],
        'skirt_inside': [sw - 2 * SKIRT_WALL, sd - 2 * SKIRT_WALL, sr - SKIRT_WALL,
                          -SKIRT_DEPTH - CUT_OVERRUN, INNER_CUT_OVERLAP],
    }


def main():
    import _rust_part
    said = _rust_part.cut('funnel', 'funnel-cover', numbers(), HERE)
    substitute_md(HERE / 'README.md', variables={
        'PLATE': f'{PLATE_T:g} mm', 'SKIRT': f'{SKIRT_DEPTH:g} mm',
        'WALL': f'{SKIRT_WALL:g} mm', 'WIDTH': f'{WIDTH:g} mm',
        'DEPTH': f'{DEPTH:.3f} mm', 'OVERHANG': f'{OVERHANG:g} mm',
        'AIR': f'{RUNNING_AIR:g} mm',
        'FRONT_EXTENSION': f'{FRONT_EXTENSION:g} mm',
        'FRONT_RELIEF': f'{FRONT_RELIEF:g} mm',
        'PRINT_HEIGHT': f'{PLATE_T + SKIRT_DEPTH:g} mm',
    })
    print(f'-> cover STEP, print STEP, STL and payload; {said["bodies"][0]["volume"]:.1f} mm3')


if __name__ == '__main__':
    main()
