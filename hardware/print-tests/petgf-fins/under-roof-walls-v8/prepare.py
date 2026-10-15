"""Prepare a small wall-under-roof gap comparison. Manual use; does not send."""
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
loader = importlib.util.spec_from_file_location('v4_geometry', HERE.parent/'bonding-and-fins-v4/prepare.py')
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)
base_settings = v4.settings_for
STEM = '2026-10-14-v8-under-roof-walls-petgf-left04-z018-mark1'
ROOF_BOTTOM = v4.FIRST + 22*v4.LAYER


def settings_for(printer):
    settings, data, edits = base_settings(printer)
    # One roof perimeter leaves the native bridge raster reaching the 1 mm wall.
    # All three conditions share this setting. No XY toolpath editing is used.
    for key, value in {'wall_loops': '1', 'sparse_infill_density': '100%',
                       'sparse_infill_pattern': 'zig-zag',
                       'bottom_shell_layers': '23'}.items():
        edits[key] = {'profile': settings.get(key), 'plate': value}
        settings[key] = value
    data['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
    return settings, data, edits


def specimen(name, empty_layers, rotate):
    gap = empty_layers*v4.LAYER
    post = v4.model_post(0, ROOF_BOTTOM, name)
    roof = v4.block(16, 12, 5*v4.LAYER, (0, 0, ROOF_BOTTOM))
    wall = v4.block(1, 12, ROOF_BOTTOM-gap, (15, 0, 0))
    wall = wall.union(v4.block(3.2, 14, v4.FIRST+2*v4.LAYER, (13.9, -1, 0)))
    shape = post.union(roof).union(wall).clean()
    if rotate:
        shape = shape.rotate((0, 0, 0), (0, 0, 1), 90)
    detail = {'kind': 'under_roof_wall', 'empty_layers': empty_layers,
              'vertical_gap_mm': gap, 'clear_span_mm': 12,
              'roof_bottom_z_mm': ROOF_BOTTOM,
              'first_roof_z_mm': ROOF_BOTTOM+v4.LAYER,
              'wall_top_z_mm': ROOF_BOTTOM-gap,
              'wall_bounds_local_mm': [[15, 0, 0], [16, 12, ROOF_BOTTOM-gap]],
              'roof_bounds_mm': [[0, 0, ROOF_BOTTOM], [16, 12, ROOF_BOTTOM+5*v4.LAYER]],
              'bridge_axis': 'Y' if rotate else 'X',
              'rotation_degrees': 90 if rotate else 0,
              'roof_courses': 5, 'roof_thickness_mm': 5*v4.LAYER,
              'fan_percent': 70, 'bridge_extrusion_multiplier': 1.25,
              'first_bridge_speed_mm_s': 25, 'thick_bridges': False,
              'expected_mesh_bodies': 2 if empty_layers else 1,
              'bearing': '1 mm vertical wall wholly underneath roof; no teeth or horizontal bearing fingers'}
    return shape, detail


def main():
    v4.settings_for = settings_for
    groups = []
    for axis, rotate, cy in (('X', False, 141), ('Y', True, 170)):
        items = []
        for layers, prefix in ((0, 'C0'), (1, 'G1'), (2, 'G2')):
            name = prefix+axis
            shape, detail = specimen(name, layers, rotate)
            items.append((name, shape, detail))
        groups.append((cy, items))
    v4.write_plate('Mark1', groups, destination=HERE, stem=STEM, spacing_mm=4)
    manifest = HERE/'mark1'/f'{STEM}.print.json'
    spec = json.loads(manifest.read_text())
    bad = [p['id'] for p in spec['parts'] if not p['cad_valid'] or not p['mesh_watertight']
           or p['mesh_bodies'] != p['expected_mesh_bodies']]
    if bad:
        raise ValueError(f'Unexpected geometry: {bad}')
    print('Six valid specimens; gap specimens intentionally include a detached wall body.')


if __name__ == '__main__':
    main()
