"""RC62 magnetic float: PETG Translucent Clear envelope and fitted ASA Aero core.

Frame: guide bore on Z, finished bottom at Z=0, roof at positive Z.
The separate Aero insert seats from Z=47 to the roof underside at Z=57.

This module holds the float's numbers and the figures derived from them, and writes the numbers
the geometry takes (`numbers()`) to `magnetic-float.numbers.json`; `magnetic_float.rs`, beside
it, cuts each piece's STEP and payload, the printed pieces' STLs, and the assembly, section and
exploded views from them on the kernel (`hardware/scripts/_rust_part.py`).
"""

import argparse
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import cadquery as cq

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
sys.path.insert(0, str(ROOT / 'tools'))
import _cadq_export  # noqa: E402,F401  the CAD lock, and build-time.md's clock
from _materials import linear  # noqa: E402
from docgen import substitute_md  # noqa: E402

diameter = 36.0
height = 60.06
bore_diameter = 4.8
outer_wall = 3.0
bore_wall = 1.8
floor = 3.0
roof = 3.06
petg_layer = 0.18
petg_first_layer = 0.30
magnet_od = 19.05
magnet_id = 9.525
magnet_height = 3.175
magnet_tolerance = 0.1
magnet_mass = 5.09
magnet_pocket_od = magnet_od + 0.30
magnet_pocket_id = magnet_id - 0.30
magnet_pocket_depth = 3.40
insert_height = 10.0
core_fit_allowance = 0.05
insert_fit_allowance = 0.05
insertion_lead = 0.5
petg_density = 1.25
petg_material = 'Bambu PETG Translucent Clear 32101'
water_density = 1.0
colors = {'petg': '#D9EBF2', 'aero': '#EBC777', 'magnet': '#707985'}
insert_lift = 24.0                    # what the exploded view lifts the insert by
magnet_lift = 10.0                    # and the magnet

outer_radius = diameter / 2
bore_radius = bore_diameter / 2
core_outer_radius = outer_radius - outer_wall
core_inner_radius = bore_radius + bore_wall
roof_bottom = round(height - roof, 6)
insert_top = roof_bottom
insert_bottom = insert_top - insert_height
magnet_seat = insert_bottom - magnet_pocket_depth


def ring(outer, inner, bottom, top):
    """The volume of the ring between two radii, standing from `bottom` to `top`."""
    return math.pi * (outer ** 2 - inner ** 2) * (top - bottom)


def led_ring(outer, inner, bottom, top):
    """The ring less its two 45-degree lower lead-ins: each a right triangle of leg
    `insertion_lead` turned about the bore, so the pair takes pi * lead^2 * (outer + inner)."""
    return ring(outer, inner, bottom, top) - math.pi * insertion_lead ** 2 * (outer + inner)


def volumes():
    """Each piece's volume in mm^3: the true solid's, which the kernel's facets approach."""
    pocket = ring(magnet_pocket_od / 2, magnet_pocket_id / 2, magnet_seat, insert_bottom)
    return {'body-petg': ring(outer_radius, bore_radius, 0, height)
                         - ring(core_outer_radius, core_inner_radius, floor, roof_bottom),
            'body-aero': led_ring(core_outer_radius, core_inner_radius, floor, insert_bottom) - pocket,
            'insert-aero': led_ring(core_outer_radius, core_inner_radius, insert_bottom, insert_top),
            'magnet': ring(magnet_od / 2, magnet_id / 2, magnet_seat, magnet_seat + magnet_height)}


def measurements():
    volumes_cc = {name: volume / 1000 for name, volume in volumes().items()}
    displaced = math.pi * (outer_radius ** 2 - bore_radius ** 2) * height / 1000
    petg = volumes_cc['body-petg']
    aero = volumes_cc['body-aero'] + volumes_cc['insert-aero']
    table = []
    for density in (0.46, 0.53, 0.55, 0.60, 0.65, 0.70):
        mass = petg * petg_density + aero * density + magnet_mass
        reserve = displaced * water_density - mass
        table.append({'aero_density_g_cc': density, 'assembled_mass_g': mass,
                      'reserve_lift_g': reserve, 'upright_freeboard_mm': height * reserve / displaced})
    return {'dimensions_mm': {'diameter': diameter, 'height': height, 'bore': bore_diameter,
                'petg_outer_wall': outer_wall, 'petg_bore_wall': bore_wall,
                'petg_floor': floor, 'petg_roof': roof, 'insert_height': insert_height,
                'insert_top': insert_top, 'insert_bottom': insert_bottom,
                'magnet_seat': magnet_seat, 'roof_bottom': roof_bottom,
                'magnet_pocket_od': magnet_pocket_od, 'magnet_pocket_id': magnet_pocket_id,
                'magnet_pocket_height': magnet_pocket_depth,
                'aero_lower_lead_in': insertion_lead,
                'insert_od': 2 * core_outer_radius, 'insert_id': 2 * core_inner_radius},
            'magnet': {'model': 'K&J RC62', 'mass_g': magnet_mass,
                'od_mm': magnet_od, 'id_mm': magnet_id, 'height_mm': magnet_height,
                'maximum_dimensional_tolerance_mm': magnet_tolerance,
                'source': 'https://www.kjmagnetics.com/rc62-neodymium-ring-magnet'},
            'volume_cc': volumes_cc, 'water_displacement_g': displaced * water_density,
            'petg_material': petg_material, 'petg_density_g_cc': petg_density, 'buoyancy': table,
            'neutral_aero_density_g_cc': (displaced * water_density - petg * petg_density - magnet_mass) / aero,
            'nominal_unfilled_volume_cc': max(0.0, displaced - sum(volumes_cc.values())),
            'aero_material': 'Bambu ASA Aero White 46100',
            'core_print_fit_allowance_radial_mm': core_fit_allowance,
            'insert_print_fit_allowance_radial_mm': insert_fit_allowance,
            'minimum_seated_magnet_top_to_roof_bottom_mm': roof_bottom - magnet_seat - magnet_height - magnet_tolerance,
            'magnet_pocket_minimum_compensated_radial_clearance_mm': min(
                (magnet_pocket_od - magnet_od - magnet_tolerance) / 2 - core_fit_allowance,
                (magnet_id - magnet_tolerance - magnet_pocket_id) / 2 - core_fit_allowance),
            'magnet_pocket_minimum_depth_clearance_mm': magnet_pocket_depth - magnet_height - magnet_tolerance,
            'fit': 'The Aero pieces have 0.5 mm lower outer/bore lead-ins and 0.05 mm radial contour expansion and bore reduction on their straight lands. The RC62 seats in a clearance pocket below the insert. The insert top supports the full roof. Intentional unfilled volume comprises lower lead-ins and magnet-pocket clearance.',
            'pressure_rating': 'Unqualified prototype; no hydrostatic test recorded.'}


def numbers():
    """What `magnetic_float.rs` cuts the pieces from."""
    return {'diameter': diameter, 'height': height, 'outer_radius': outer_radius,
            'bore_radius': bore_radius, 'core_outer_radius': core_outer_radius,
            'core_inner_radius': core_inner_radius, 'floor': floor, 'roof_bottom': roof_bottom,
            'insert_bottom': insert_bottom, 'insert_top': insert_top, 'magnet_seat': magnet_seat,
            'magnet_height': magnet_height, 'magnet_outer_radius': magnet_od / 2,
            'magnet_inner_radius': magnet_id / 2, 'magnet_tolerance': magnet_tolerance,
            'pocket_outer_radius': magnet_pocket_od / 2, 'pocket_inner_radius': magnet_pocket_id / 2,
            'insertion_lead': insertion_lead, 'insert_lift': insert_lift, 'magnet_lift': magnet_lift,
            **{f'color_{material}': list(linear(cq.Color(color))) for material, color in colors.items()}}


def check(asked):
    """What `magnetic_float.rs --check` measures of the pieces it cuts: whether each is one sound
    solid, and every volume by which they miss the design. `asked` holds the lifts the separate
    pieces are slid in by and the depth of roof the insert must carry."""
    import _rust_part
    program = _rust_part.program('cold-core', 'magnetic-float')
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'magnetic-float.check.json'
        path.write_text(json.dumps({**numbers(), 'check': asked}))
        run = subprocess.run([str(program), str(path), '--check'],
                             check=True, stdout=subprocess.PIPE, text=True)
    return json.loads(run.stdout)


def write(output):
    # A run cuts the pieces; an import of this module is a reader of its numbers.
    import _rust_part
    output.mkdir(parents=True, exist_ok=True)
    _rust_part.cut('cold-core', 'magnetic-float', numbers(), output)
    info = measurements()
    (output / 'design.json').write_text(json.dumps(info, indent=2) + '\n')
    readme = output / 'README.md'
    if readme.exists():
        figures = {
            'FLOAT_DIAMETER': f'{diameter:g} mm', 'FLOAT_HEIGHT': f'{height:g} mm',
            'FLOAT_BORE': f'{bore_diameter:g} mm', 'OUTER_WALL': f'{outer_wall:g} mm',
            'BORE_WALL': f'{bore_wall:g} mm', 'FLOOR': f'{floor:g} mm', 'ROOF': f'{roof:g} mm',
            'INSERT_HEIGHT': f'{insert_height:g} mm',
            'INSERT_SIZE': f'{2 * core_outer_radius:g} × {2 * core_inner_radius:g} × {insert_height:g} mm',
            'MAGNET_SIZE': f'{magnet_od:g} × {magnet_id:g} × {magnet_height:g} mm',
            'MAGNET_SEAT': f'{magnet_seat:g} mm',
            'INSERT_STATIONS': f'{insert_bottom:g} / {insert_top:g} mm',
            'ROOF_BOTTOM': f'{roof_bottom:g} mm',
            'DISPLACEMENT': f'{info["water_displacement_g"]:.2f} g',
            'UNFILLED_VOLUME': f'{info["nominal_unfilled_volume_cc"]:.3f} cm³',
            'FIT_ALLOWANCE': f'{insert_fit_allowance:g} mm',
            'PAUSE_LAYER': f'{roof_bottom + petg_layer:g} mm',
            'ROOF_LAYERS': f'{round(roof / petg_layer)} layers',
            'MAGNET_ROOF_GAP': f'{info["minimum_seated_magnet_top_to_roof_bottom_mm"]:g} mm',
        }
        for row in info['buoyancy']:
            code = f'{round(row["aero_density_g_cc"] * 100):03d}'
            figures[f'MASS_{code}'] = f'{row["assembled_mass_g"]:.2f} g'
            figures[f'LIFT_{code}'] = f'{row["reserve_lift_g"]:.2f} g'
        substitute_md(readme, figures)
    print(json.dumps(info, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    write(args.output)


if __name__ == '__main__':
    main()
