"""Manual Mark1 flow bracket with isolated and completed roofs; does not send."""
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'bonding-and-fins-v4/prepare.py'
loader = importlib.util.spec_from_file_location('v4_geometry', source)
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)
base_settings_for = v4.settings_for


def settings_for(printer):
    settings, data, edits = base_settings_for(printer)
    for key, value in {'sparse_infill_density': '100%',
                       'sparse_infill_pattern': 'zig-zag',
                       'bottom_shell_layers': '23'}.items():
        edits[key] = {'profile': settings.get(key), 'plate': value}
        settings[key] = value
    data['Metadata/project_settings.config'] = json.dumps(settings, indent=2).encode()
    return settings, data, edits


v4.settings_for = settings_for


def main():
    groups = []
    for prefix, courses, y in (('L', 1, 140), ('R', 5, 166)):
        items = []
        for flow in (125, 130, 135, 140):
            name = f'{prefix}{flow}'
            shape, detail = v4.control(name, v4.FIRST + 22*v4.LAYER,
                                       thickness=courses*v4.LAYER)
            detail.update(thick_bridges=False,
                          bridge_extrusion_multiplier=flow/100,
                          fan_percent=70, roof_courses=courses,
                          reference='v5 A125 first-roof settings and model-post geometry')
            items.append((name, shape, detail))
        groups.append((y, items))
    v4.write_plate('Mark1', groups, destination=HERE,
                  stem='2026-10-14-v7-flow-bracket-petgf-left04-z018-mark1')


if __name__ == '__main__':
    main()
