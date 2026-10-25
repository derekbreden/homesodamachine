"""Manual native counterexamples to a near-final-Y vertical back-top entry.

The actual exported top and bottom retain their existing hooked Z-seam rails.
A positive common at one intermediate pose disproves a straight vertical entry
at that Y offset. A negative point reading establishes no complete path.
This reader exports no production geometry and joins no recurring check.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'hardware/scripts'))
from _cadq_export import import_step


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def main():
    enclosure = ROOT / 'hardware/printed-parts/enclosure/enclosure'
    sources = {name: enclosure / f'enclosure-{name}.step'
               for name in ('back-top', 'back-bottom')}
    top, bottom = (import_step(sources[name]).val()
                   for name in ('back-top', 'back-bottom'))
    rows = []
    fixture = ROOT / 'tmp/near-final-back-top'
    fixture.mkdir(exist_ok=True)
    for y in (0., .5, 1., 2., 5., 10., 15.):
        offset = (0., y, 3.)
        moved = top.translate(offset)
        common = moved.intersect(bottom, tol=1e-6)
        amount = 0. if common.isNull() else abs(common.Volume())
        row = {'offset_mm': list(offset), 'common_mm3': amount,
               'common_bounds_mm': bounds(common) if amount > 1e-6 else None,
               'straight_vertical_entry_disproved': amount > 1e-6}
        rows.append(row)
        print(json.dumps(row), flush=True)
        if y == 2.:
            moved.exportBrep(str(fixture / 'back-top-at-y2-z3.brep'))
            bottom.exportBrep(str(fixture / 'back-bottom.brep'))
            if amount > 1e-6:
                common.exportBrep(str(fixture / 'common-at-y2-z3.brep'))
    report = {'schema': 1, 'units': 'mm', 'frame': 'Enclosure world XYZ; Z up',
        'scope': 'Native point counterexamples against the actual exported hooked shell '
                 'rails. Only the two named shell pieces are tested. No body, '
                 'attachment or routing change; no complete-path or force claim.',
        'moving': 'enclosure-back-top', 'stationary': 'enclosure-back-bottom',
        'proposed_handling': 'Lower back-top at a near-final Y offset, then seat fore.',
        'readings': rows,
        'all_named_vertical_entries_disproved': all(
            row['straight_vertical_entry_disproved'] for row in rows),
        'source_sha256': {str(p.relative_to(ROOT)): sha(p)
                         for p in (Path(__file__), *sources.values())}}
    output = HERE / 'back-top-approach-review.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    print('REPORT', output, flush=True)


if __name__ == '__main__':
    main()
