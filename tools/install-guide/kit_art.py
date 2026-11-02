#!/usr/bin/env python3
"""Draw the supplied kit as consistent vector hidden-line views."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / 'hardware'
ART = HARDWARE / 'install-guide/assets/kit'
sys.path[:0] = [str(HARDWARE/'scripts'), str(HARDWARE/'install-guide'),
               str(HARDWARE/'printed-parts/enclosure/enclosure')]

import _rust_part
if __name__ == '__main__':
    _rust_part.start()

from _mesh_projection import model_outlines

CAMERA = (.8, -1, .7)
VIEWS = (
    ('machine', CAMERA),
    ('faucet-and-plate', (.95, -1, .55)),
    ('filtered-line', CAMERA),
    ('water-tees', (.6, -1, .65)),
    ('regulator-and-tether', (.15, 1, .3)),
    ('collet-press', (-.5, -.9, .85)),
    ('power-cord', CAMERA),
    ('install-guide', CAMERA),
    ('cold-kit', CAMERA),
)


def models(work):
    """Current component surfaces and the kit's source-dimensioned props."""
    import _install_art as shared
    import _swept_top

    facts = json.loads(shared.MACHINE_FACTS.read_text())
    faucet = shared._cad_art._load_faucet_module()
    regulator = shared._load_regulator()
    inputs = {
        'faucet': HARDWARE/'faucet-layout/faucet-assembly.step.npz',
        'collet': HARDWARE/'printed-parts/collet-press/collet-press.step.npz',
        'black_tee': HARDWARE/'reference/jg-pp0208e-tee/jg-pp0208e-tee.step.mesh',
        'regulator': shared.REGULATOR_DIR/'taprite-3741-regulator.step.mesh',
        'white_tee': shared.PLUMBING_DIR/'out/plumbing-pre-tee.step.npz',
    }
    for path in [shared.MACHINE_FACTS, *inputs.values()]:
        _rust_part._READ_TARGETS.add(path.relative_to(ROOT).as_posix())
    numbers = {
        'kit_art': {
            'inputs': {name: path.relative_to(ROOT).as_posix()
                       for name, path in inputs.items()},
            'machine': {'outer': facts['box']['outer'],
                        'profile': _swept_top.profile(facts['box']['outer']),
                        'cover': facts['bodies']['funnel-cover']},
            'lever': [faucet.plateau_z, faucet.port_center_depth,
                      faucet.soda_faucet_tube_r, faucet.lever_pivot_y,
                      faucet.lever_pivot_z, faucet.lever_press_angle_deg],
            'regulator': {'mouth': regulator.outlet()[0],
                          'insert': shared.TETHER_IN_MOUTH},
        },
        'filter': [shared.FILTER_D, shared.FILTER_L],
        'tube_d': shared.TUBE_D,
        'colors': {name: [0., 0., 0.] for name in
                   ('FILTER_BODY', 'FILTER_CAP', 'WHITE_TUBE', 'RED_TUBE')},
    }
    work.mkdir(parents=True, exist_ok=True)
    path = work/'kit-art.numbers.json'
    path.write_text(json.dumps(numbers, sort_keys=True)+'\n')
    _rust_part.run('tooling', 'install-art-props', path, work)
    return {name: work/f'{name}.kit.npz' for name, _ in VIEWS}


def line_svg(model, camera):
    """Use world Z as up and bake all projection transforms into the SVG paths."""
    right = (-camera[1], camera[0], 0.)
    points = model_outlines(model, camera, right)
    flat = [p for edge in points for p in edge]
    left, right = min(p[0] for p in flat), max(p[0] for p in flat)
    bottom, top = min(p[1] for p in flat), max(p[1] for p in flat)
    scale = min(564/(right-left), 414/(top-bottom))
    ox, oy = (600-(right-left)*scale)/2, (450-(top-bottom)*scale)/2
    body = []
    for edge in points:
        path = ' '.join(f'{"M" if i == 0 else "L"}{ox+(x-left)*scale:.4f},'
                        f'{oy+(top-y)*scale:.4f}' for i, (x, y) in enumerate(edge))
        if path:
            body.append(f'<path d="{path}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="450" '
            'viewBox="0 0 600 450">\n'
            '<g fill="none" stroke="#46515b" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round">\n'
            + '\n'.join(body) + '\n</g>\n</svg>\n')


def main():
    ART.mkdir(parents=True, exist_ok=True)
    shown = models(ROOT/'.cache/install-guide-kit')
    for name, camera in VIEWS:
        print('Drawing', name, flush=True)
        (ART/f'{name}.svg').write_text(line_svg(shown[name], camera))
    print(f'{len(VIEWS)} kit drawings written to {ART.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
