"""Manual printer-specific preparation using the enclosure recipe; never sends."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRIAL = ROOT / 'hardware/printed-parts/enclosure/trial-preparation'
sys.path.insert(0, str(TRIAL))
loader = importlib.util.spec_from_file_location('seam_bore_trial', TRIAL / 'prepare.py')
trial = importlib.util.module_from_spec(loader)
loader.loader.exec_module(trial)


def compact_layout(footprints, low, high, spacing, yaw):
    """Two 3x3 panels, short passages at the front and long passages behind."""
    cx, cy = (low + high) / 2
    return [(0, float(cx + (i % 3 - 1) * 30), float(cy + (i // 3 - 2.5) * 24))
            for i in range(len(footprints))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('printer', choices=('Mark1', 'Mark2'), nargs='?', default='Mark1')
    printer = parser.parse_args().printer
    geometry = json.loads((HERE / 'geometry.json').read_text())
    base = json.loads((TRIAL / 'pieces.json').read_text())
    nozzle = base['pieces']['front-top' if printer == 'Mark1' else 'back-top']['nozzle']
    spec = {key: base[key] for key in ('schema', 'profile', 'filament_mapping')}
    spec['printers'] = {printer: base['printers'][printer]}
    spec['pieces'] = {'m5-seam-bearing': dict(
        printer=printer, nozzle=nozzle, material='Polymaker Fiberon PET-GF15, black',
        plate_border_mm=80, spacing_mm=10,
        settings={'sparse_infill_density': {'value': '100%',
                  'reason': 'These small coupons represent the local dense seam-bearing hosts.'},
                  'sparse_infill_pattern': {'value': 'zig-zag',
                  'reason': 'Match the enclosure seam hosts, with the ordinary two wall loops.'}},
        parts=[dict(stl=p['stl'], name=p['name']) for p in geometry['parts']])}
    path = HERE / ('plate-spec.json' if printer == 'Mark1' else 'plate-spec-mark2.json')
    path.write_text(json.dumps(spec, indent=2) + '\n')
    trial.SPEC_PATH = path
    trial.layout = compact_layout
    folder = trial.prepare('m5-seam-bearing', output=HERE / printer.lower())
    archive = trial.slice_project(folder)
    import review
    result = review.review(folder, audit=False)
    if not result['pass']:
        raise SystemExit('Native review did not pass; see review.json.')
    from finish import finish
    finish(folder)


if __name__ == '__main__':
    main()
