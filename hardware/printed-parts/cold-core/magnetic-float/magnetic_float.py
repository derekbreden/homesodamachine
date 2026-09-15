"""RC62 magnetic float: continuous PETG envelope and a fitted PLA Aero core.

Frame: guide bore on Z, finished bottom at Z=0, roof at positive Z.
The separate Aero insert seats from Z=39 to the roof underside at Z=49.
"""

import argparse
import json
import math
import sys
from pathlib import Path

import cadquery as cq
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
sys.path.insert(0, str(ROOT / 'tools'))
from _cadq_export import export_assembly
from _materials import one_body
from flute_payload import cut as write_print_payload
from docgen import substitute_md

diameter = 28.0
height = 50.0
bore_diameter = 6.0
skin = 1.0
magnet_od = 19.05
magnet_id = 9.525
magnet_height = 3.175
magnet_tolerance = 0.1
magnet_mass = 5.09
insert_height = 10.0
insert_fit_allowances = (0.05, 0.10)
petg_density = 1.25
water_density = 1.0
mesh_tolerance = 0.01
mesh_angle = 0.06

outer_radius = diameter / 2
bore_radius = bore_diameter / 2
core_outer_radius = outer_radius - skin
core_inner_radius = bore_radius + skin
roof_bottom = height - skin
insert_top = roof_bottom
insert_bottom = insert_top - insert_height
magnet_seat = insert_bottom - magnet_height


def annulus(outer, inner, bottom, top):
    return (cq.Workplane('XY').workplane(offset=bottom)
            .circle(outer).circle(inner).extrude(top - bottom).val())


def box(width, depth, bottom, top, x=0.0, y=0.0):
    return (cq.Workplane('XY').box(width, depth, top - bottom,
            centered=(True, True, False)).translate((x, y, bottom)).val())


def build():
    envelope = annulus(outer_radius, bore_radius, 0, height)
    interior = annulus(core_outer_radius, core_inner_radius, skin, roof_bottom)
    magnet = annulus(magnet_od / 2, magnet_id / 2, magnet_seat, insert_bottom)
    core = annulus(core_outer_radius, core_inner_radius, skin, insert_bottom).cut(magnet)
    insert = annulus(core_outer_radius, core_inner_radius, insert_bottom, insert_top)
    return {'body-petg': envelope.cut(interior).clean(), 'body-aero': core.clean(),
            'insert-aero': insert, 'magnet': magnet}


def measurements(parts):
    volumes = {name: shape.Volume() / 1000 for name, shape in parts.items()}
    displaced = math.pi * (outer_radius ** 2 - bore_radius ** 2) * height / 1000
    petg = volumes['body-petg']
    aero = volumes['body-aero'] + volumes['insert-aero']
    table = []
    for density in (0.42, 0.45, 0.55, 0.60, 0.65, 0.70):
        mass = petg * petg_density + aero * density + magnet_mass
        reserve = displaced * water_density - mass
        table.append({'aero_density_g_cc': density, 'assembled_mass_g': mass,
                      'reserve_lift_g': reserve, 'upright_freeboard_mm': height * reserve / displaced})
    return {'dimensions_mm': {'diameter': diameter, 'height': height, 'bore': bore_diameter,
                'petg_skin': skin, 'insert_height': insert_height,
                'insert_top': insert_top, 'insert_bottom': insert_bottom,
                'magnet_seat': magnet_seat, 'roof_bottom': roof_bottom,
                'magnet_pocket_od': magnet_od, 'magnet_pocket_id': magnet_id,
                'magnet_pocket_height': magnet_height,
                'insert_od': 2 * core_outer_radius, 'insert_id': 2 * core_inner_radius},
            'magnet': {'model': 'K&J RC62', 'mass_g': magnet_mass,
                'od_mm': magnet_od, 'id_mm': magnet_id, 'height_mm': magnet_height,
                'maximum_dimensional_tolerance_mm': magnet_tolerance,
                'source': 'https://www.kjmagnetics.com/rc62-neodymium-ring-magnet'},
            'volume_cc': volumes, 'water_displacement_g': displaced * water_density,
            'petg_density_g_cc': petg_density, 'buoyancy': table,
            'neutral_aero_density_g_cc': (displaced * water_density - petg * petg_density - magnet_mass) / aero,
            'nominal_unfilled_volume_cc': max(0.0, displaced - sum(volumes.values())),
            'insert_print_fit_allowances_radial_mm': insert_fit_allowances,
            'minimum_seated_magnet_top_to_roof_bottom_mm': insert_height - magnet_tolerance,
            'fit': 'Nominal mating faces touch. The slicer enlarges the Aero insert outer contour and reduces its bore by the radial fit allowance. Magnet tolerance is taken in the Aero pocket.',
            'pressure_rating': 'Unqualified prototype; no hydrostatic test recorded.'}


def write(parts, output):
    output.mkdir(parents=True, exist_ok=True)
    colors = {'petg': cq.Color('#3DA5C8'), 'aero': cq.Color('#EBC777'),
              'magnet': cq.Color('#707985')}
    assembly = cq.Assembly(name='magnetic-float')
    section = cq.Assembly(name='magnetic-float-section')
    exploded = cq.Assembly(name='magnetic-float-exploded')
    half = box(diameter + skin * 2, diameter, -skin, height + skin, y=-diameter / 2)
    for name, shape in parts.items():
        material = 'magnet' if name == 'magnet' else ('aero' if name.endswith('aero') else 'petg')
        color = colors[material]
        print_shape = shape.translate((0, 0, -insert_bottom)) if name == 'insert-aero' else shape
        export_assembly(one_body(cq.Workplane(obj=print_shape), name, color), str(output / f'{name}.step'))
        if name != 'magnet':
            path = output / f'{name}.stl'
            cq.exporters.export(print_shape, str(path), tolerance=mesh_tolerance, angularTolerance=mesh_angle)
            mesh = trimesh.load(path, force='mesh', process=True)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            mesh.export(path)
            write_print_payload(output / f'{name}.step', path)
        assembly.add(shape, name=name, color=color)
        section.add(shape.intersect(half), name=name, color=color)
        lift = 24 if name == 'insert-aero' else (10 if name == 'magnet' else 0)
        exploded.add(shape.translate((0, 0, lift)), name=name, color=color)
    for name, view in (('magnetic-float', assembly), ('section', section), ('exploded', exploded)):
        export_assembly(view, str(output / f'{name}.step'))
    info = measurements(parts)
    (output / 'design.json').write_text(json.dumps(info, indent=2) + '\n')
    readme = output / 'README.md'
    if readme.exists():
        figures = {
            'FLOAT_DIAMETER': f'{diameter:g} mm', 'FLOAT_HEIGHT': f'{height:g} mm',
            'FLOAT_BORE': f'{bore_diameter:g} mm', 'FLOAT_SKIN': f'{skin:g} mm',
            'INSERT_HEIGHT': f'{insert_height:g} mm',
            'INSERT_SIZE': f'{2 * core_outer_radius:g} × {2 * core_inner_radius:g} × {insert_height:g} mm',
            'MAGNET_SIZE': f'{magnet_od:g} × {magnet_id:g} × {magnet_height:g} mm',
            'MAGNET_SEAT': f'{magnet_seat:g} mm',
            'INSERT_STATIONS': f'{insert_bottom:g} / {insert_top:g} mm',
            'ROOF_BOTTOM': f'{roof_bottom:g} mm',
            'DISPLACEMENT': f'{info["water_displacement_g"]:.2f} g',
            'UNFILLED_VOLUME': f'{info["nominal_unfilled_volume_cc"]:.3f} cm³',
            'FIT_ALLOWANCES': ' / '.join(f'{v:g}' for v in insert_fit_allowances) + ' mm',
            'PAUSE_LAYER': f'{roof_bottom + 0.2:g} mm',
            'ROOF_LAYERS': f'{round(skin / 0.2)} layers',
            'MAGNET_ROOF_GAP': f'{insert_height - magnet_tolerance:g} mm',
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
    write(build(), args.output)


if __name__ == '__main__':
    main()
