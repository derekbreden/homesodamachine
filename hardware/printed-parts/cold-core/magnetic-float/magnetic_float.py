"""RC62 magnetic float: PETG envelope, PLA Aero core and bayonet insert.

Frame: guide bore on Z, finished bottom at Z=0, roof at positive Z.
The insert enters at zero rotation and locks through 90 degrees about +Z.
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
magnet_radial_clearance = 0.2
magnet_pocket_height = 3.6
insert_height = 10.0
insert_radial_clearance = 0.2
insert_roof_clearance = 0.2
loose_extra_clearance = 0.15
collar_inner_radius = 10.4
collar_lip_inner_radius = 9.9
collar_lip_height = 0.8
groove_radius = 11.8
groove_bottom_from_top = 1.6
groove_height = 1.4
lug_radial_depth = 0.95
lug_width = 4.0
lug_height = 1.0
lug_axial_clearance = 0.2
entry_width = 4.8
groove_start_angle = -100.0
groove_end_angle = 12.0
lock_angle = 90.0
key_socket_radius = 11.6
key_socket_diameter = 1.4
key_socket_depth = 1.4
key_pin_diameter = 1.0
key_pin_height = 1.2
key_bar_length = 29.0
key_bar_width = 5.0
key_bar_height = 3.0
petg_density = 1.25
water_density = 1.0
mesh_tolerance = 0.01
mesh_angle = 0.06

outer_radius = diameter / 2
bore_radius = bore_diameter / 2
core_outer_radius = outer_radius - skin
core_inner_radius = bore_radius + skin
roof_bottom = height - skin
insert_top = roof_bottom - insert_roof_clearance
insert_bottom = insert_top - insert_height
magnet_seat = insert_bottom - magnet_pocket_height
magnet_pocket_outer_radius = (magnet_od + magnet_tolerance) / 2 + magnet_radial_clearance
magnet_pocket_inner_radius = (magnet_id - magnet_tolerance) / 2 - magnet_radial_clearance
groove_bottom = insert_top - groove_bottom_from_top
groove_top = groove_bottom + groove_height
lug_bottom = groove_bottom + lug_axial_clearance
lug_top = lug_bottom + lug_height
lug_inner_radius = core_outer_radius - lug_radial_depth


def annulus(outer, inner, bottom, top):
    return (cq.Workplane('XY').workplane(offset=bottom)
            .circle(outer).circle(inner).extrude(top - bottom).val())


def box(width, depth, bottom, top, x=0.0, y=0.0):
    return (cq.Workplane('XY').box(width, depth, top - bottom,
            centered=(True, True, False)).translate((x, y, bottom)).val())


def polar(radius, angle):
    angle = math.radians(angle)
    return radius * math.cos(angle), radius * math.sin(angle)


def sector(outer, inner, bottom, top, start, end):
    middle = (start + end) / 2
    profile = (cq.Workplane('XY').workplane(offset=bottom)
               .moveTo(*polar(inner, start)).lineTo(*polar(outer, start))
               .threePointArc(polar(outer, middle), polar(outer, end))
               .lineTo(*polar(inner, end))
               .threePointArc(polar(inner, middle), polar(inner, start)).wire())
    return profile.extrude(top - bottom).val()


def clean(shape):
    return shape.clean()


def body_parts():
    envelope = annulus(outer_radius, bore_radius, 0, height)
    interior = annulus(core_outer_radius, core_inner_radius, skin, roof_bottom)
    shell = envelope.cut(interior)
    lug_band = annulus(core_outer_radius + skin / 2, lug_inner_radius, lug_bottom, lug_top)
    for angle in (0, 180):
        lug = lug_band.intersect(box(diameter, lug_width, lug_bottom, lug_top,
                                    x=outer_radius))
        shell = shell.fuse(lug.rotate((0, 0, 0), (0, 0, 1), angle))
    core = annulus(core_outer_radius, core_inner_radius, skin, insert_bottom)
    pocket = annulus(magnet_pocket_outer_radius, magnet_pocket_inner_radius,
                     magnet_seat, insert_bottom)
    return clean(shell), clean(core.cut(pocket))


def insert_parts(extra=0.0):
    outer = core_outer_radius - insert_radial_clearance - extra
    inner = core_inner_radius + insert_radial_clearance + extra
    envelope = annulus(outer, inner, insert_bottom, insert_top)
    collar = annulus(outer, collar_inner_radius, insert_bottom, insert_top)
    for bottom, top in ((insert_bottom, insert_bottom + collar_lip_height),
                        (insert_top - collar_lip_height, insert_top)):
        collar = collar.fuse(annulus(outer, collar_lip_inner_radius, bottom, top))
    for angle in (0, 180):
        groove = sector(outer + skin, groove_radius - extra, groove_bottom,
                        groove_top, groove_start_angle + angle, groove_end_angle + angle)
        entry = box(diameter, entry_width + 2 * extra, insert_bottom, insert_top,
                    x=groove_radius + diameter / 2 - extra)
        entry = entry.rotate((0, 0, 0), (0, 0, 1), angle)
        collar = collar.cut(groove).cut(entry)
        envelope = envelope.cut(groove).cut(entry)
    for angle in (45, 225):
        x, y = polar(key_socket_radius, angle)
        hole = cq.Solid.makeCylinder(key_socket_diameter / 2, key_socket_depth,
                    cq.Vector(x, y, insert_top - key_socket_depth))
        collar = collar.cut(hole)
        envelope = envelope.cut(hole)
    return clean(collar), clean(envelope.cut(collar))


def turning_key():
    key = box(key_bar_length, key_bar_width, 0, key_bar_height)
    for x in (-key_socket_radius, key_socket_radius):
        pin = cq.Solid.makeCylinder(key_pin_diameter / 2, key_pin_height,
                                   cq.Vector(x, 0, key_bar_height))
        key = key.fuse(pin)
    return clean(key)


def build():
    shell, core = body_parts()
    collar, insert = insert_parts()
    loose_collar, loose_insert = insert_parts(loose_extra_clearance)
    magnet = annulus(magnet_od / 2, magnet_id / 2, magnet_seat, magnet_seat + magnet_height)
    return {'body-petg': shell, 'body-aero': core,
            'insert-petg': collar, 'insert-aero': insert,
            'insert-loose-petg': loose_collar, 'insert-loose-aero': loose_insert,
            'turning-key': turning_key(), 'magnet': magnet}


def measurements(parts):
    volumes = {name: shape.Volume() / 1000 for name, shape in parts.items()}
    displaced = math.pi * (outer_radius ** 2 - bore_radius ** 2) * height / 1000
    petg = volumes['body-petg'] + volumes['insert-petg']
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
                'magnet_pocket_od': 2 * magnet_pocket_outer_radius,
                'magnet_pocket_id': 2 * magnet_pocket_inner_radius,
                'magnet_pocket_height': magnet_pocket_height},
            'magnet': {'model': 'K&J RC62', 'mass_g': magnet_mass,
                'od_mm': magnet_od, 'id_mm': magnet_id, 'height_mm': magnet_height,
                'maximum_dimensional_tolerance_mm': magnet_tolerance,
                'source': 'https://www.kjmagnetics.com/rc62-neodymium-ring-magnet'},
            'volume_cc': volumes, 'water_displacement_g': displaced * water_density,
            'petg_density_g_cc': petg_density, 'buoyancy': table,
            'neutral_aero_density_g_cc': (displaced * water_density - petg * petg_density - magnet_mass) / aero,
            'assembly_clearance_volume_cc': displaced - petg - aero - volumes['magnet'],
            'lock_rotation_degrees': lock_angle,
            'minimum_magnet_top_to_roof_bottom_mm': roof_bottom - insert_bottom - lug_axial_clearance,
            'pressure_rating': 'Unqualified prototype; no hydrostatic test recorded.'}


def write(parts, output):
    output.mkdir(parents=True, exist_ok=True)
    colors = {'petg': cq.Color('#3DA5C8'), 'aero': cq.Color('#EBC777'),
              'magnet': cq.Color('#707985')}
    assembly = cq.Assembly(name='magnetic-float')
    section = cq.Assembly(name='magnetic-float-section')
    exploded = cq.Assembly(name='magnetic-float-exploded')
    half = box(diameter + skin * 2, diameter, -skin, height + skin,
               y=-diameter / 2)
    for name, shape in parts.items():
        material = 'magnet' if name == 'magnet' else ('aero' if name.endswith('aero') else 'petg')
        color = colors[material]
        print_shape = shape.translate((0, 0, -insert_bottom)) if name.startswith('insert') else shape
        export_assembly(one_body(cq.Workplane(obj=print_shape), name, color), str(output / f'{name}.step'))
        if name != 'magnet':
            path = output / f'{name}.stl'
            cq.exporters.export(print_shape, str(path), tolerance=mesh_tolerance, angularTolerance=mesh_angle)
            mesh = trimesh.load(path, force='mesh', process=True)
            mesh.update_faces(mesh.nondegenerate_faces())
            mesh.remove_unreferenced_vertices()
            mesh.export(path)
            write_print_payload(output / f'{name}.step', path)
        if name == 'turning-key' or name.startswith('insert-loose'):
            continue
        placed = shape.rotate((0, 0, 0), (0, 0, 1), lock_angle) if name.startswith('insert') else shape
        assembly.add(placed, name=name, color=color)
        section.add(placed.intersect(half), name=name, color=color)
        lift = 24 if name.startswith('insert') else (10 if name == 'magnet' else 0)
        exploded.add(placed.translate((0, 0, lift)), name=name, color=color)
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
            'MAGNET_SIZE': f'{magnet_od:g} × {magnet_id:g} × {magnet_height:g} mm',
            'MAGNET_POCKET': f'{2 * magnet_pocket_outer_radius:g} × {2 * magnet_pocket_inner_radius:g} × {magnet_pocket_height:g} mm',
            'MAGNET_SEAT': f'{magnet_seat:g} mm',
            'INSERT_STATIONS': f'{insert_bottom:g} / {insert_top:g} mm',
            'ROOF_BOTTOM': f'{roof_bottom:g} mm',
            'DISPLACEMENT': f'{info["water_displacement_g"]:.2f} g',
            'INSERT_RADIAL_CLEARANCE': f'{insert_radial_clearance:g} mm',
            'LOOSE_RADIAL_CLEARANCE': f'{insert_radial_clearance + loose_extra_clearance:g} mm',
            'INSERT_ROOF_CLEARANCE': f'{insert_roof_clearance:g} mm',
            'ASSEMBLY_CLEARANCE': f'{info["assembly_clearance_volume_cc"]:.3f} cm³',
            'PAUSE_LAYER': f'{roof_bottom + 0.2:g} mm',
            'LOCK_ANGLE': f'{lock_angle:g}°', 'ROOF_LAYERS': f'{round(skin / 0.2)} layers',
            'MAGNET_ROOF_GAP': f'{info["minimum_magnet_top_to_roof_bottom_mm"]:g} mm',
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
