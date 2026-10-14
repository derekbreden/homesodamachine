"""Manual six-swatch follow-up to the N100/N125 physical result; does not send."""
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parent
source = HERE.parent / 'bonding-and-fins-v4/prepare.py'
loader = importlib.util.spec_from_file_location('v4_geometry', source)
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)


def main():
    groups = []
    for prefix, fan, y in (('A', 70, 140), ('B', 100, 166)):
        items = []
        for flow in (100, 115, 125):
            name = f'{prefix}{flow}'
            shape, detail = v4.control(name, v4.FIRST + 22*v4.LAYER)
            detail.update(thick_bridges=False, bridge_extrusion_multiplier=flow/100,
                          fan_percent=fan, reference='v4 N100/N125 geometry and normal mode')
            items.append((name, shape, detail))
        groups.append((y, items))
    v4.write_plate('Mark1', groups, destination=HERE,
                  stem='2026-10-14-v5-normal-flow-cooling-petgf-left04-z018-mark1')


if __name__ == '__main__':
    main()
