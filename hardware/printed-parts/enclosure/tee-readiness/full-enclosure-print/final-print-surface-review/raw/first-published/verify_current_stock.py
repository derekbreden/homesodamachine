"""Bounded read-only native stock checks for the current lint locations."""
from pathlib import Path
import hashlib
import json
import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/cad-artifacts.json').exists())
paths = {
    'front': ROOT / 'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step',
    'left': ROOT / 'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-left.step',
}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
digests = {key: sha(path) for key, path in paths.items()}
shapes = {key: cq.importers.importStep(str(path)).val() for key, path in paths.items()}
rows = []


def probe(name, body, low, high):
    block = cq.Solid.makeBox(*(high[i] - low[i] for i in range(3)), cq.Vector(*low))
    missing = abs(block.cut(shapes[body]).Volume())
    rows.append({'name': name, 'body': body, 'bounds_mm': [low, high],
                 'expected_mm3': block.Volume(), 'missing_mm3': missing, 'pass': missing < 1e-5})


for side in (-1, 1):
    xlo, xhi = sorted([side * 99.851, side * 107.49])
    end = 151.15245914989052 if side < 0 else 150.88240677056572
    probe('expanded yoke pocket complete flank backing', 'front',
          [xlo, 119.241, 235.821], [xhi, end - .001, 269.028])
    xlo, xhi = sorted([side * 98.51, side * 104.49])
    probe('outer well guide land root', 'front', [xlo, 99.45, 229.63], [xhi, 119.23, 235.915])
    xlo, xhi = sorted([side * 83.251, side * 93.249])
    probe('carrier floor exposed end backing', 'front', [xlo, 93.837, 160.01], [xhi, 94.039, 166.91])
    xlo, xhi = sorted([side * 98.6, side * 104.4])
    probe('aft tray root', 'front', [xlo, 172.1, 180.81], [xhi, 181.28, 181.25])

probe('left Wago full 3 mm floor inside boundary margins', 'front',
      [-104.49, 111.66, 272.851], [-95.21, 126.34, 275.849])
probe('left Wago inward root above clipped corbel edge', 'front',
      [-97.49, 119.25, 271.40], [-95.21, 126.34, 275.849])
probe('left carrier full upper web backing', 'left',
      [-74, 108.787, 211.1], [-73, 114.289, 219.0])
probe('left carrier full 3 x 3 x 9 stop with boundary margin', 'left',
      [-28.999, 133.001, 211.001], [-26.001, 135.999, 219.999])
drift = [str(paths[key]) for key, digest in digests.items() if sha(paths[key]) != digest]
record = {
    'status': 'native_stock_probes_pass' if all(row['pass'] for row in rows) and not drift
              else 'native_stock_probe_failure',
    'input_sha256': {str(paths[key].relative_to(ROOT)): digest for key, digest in digests.items()},
    'probes': rows, 'input_drift': drift,
    'scope': 'Read-only native containment. No geometry change, support-path approval or physical force claim.',
    'wago_note': 'The 0.838643 mm face is the yoke relief meeting the underside corbel below the complete Wago floor.',
    'script_sha256': sha(Path(__file__)),
}
(HERE / 'current-stock-probes.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
