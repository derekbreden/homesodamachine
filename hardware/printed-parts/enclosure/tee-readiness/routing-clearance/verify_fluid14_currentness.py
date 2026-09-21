#!/usr/bin/env python3
"""Prove a retained fluid-14 native report still describes the current sweep.

The route source module also contains independent runs. A change elsewhere in it
does not change this sweep when its native inputs, tube constructor and complete
wire/diameter parameters remain equal. Any mismatch requires a new native report.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    report_path = HERE / 'fluid14-current-pack.json'
    report = json.loads(report_path.read_text())
    if report['status'] != 'pass':
        raise ValueError('The original native report did not pass')
    for path, digest in report['input_sha256'].items():
        if sha(path) != digest:
            raise ValueError('A native input changed: ' + path)
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT / 'hardware/manifold-layout'), str(ROOT / 'hardware/scripts')]
    import cadquery as cq
    import _lines as lines
    import _routing as routing
    for module in (routing, lines._cc):
        path = Path(module.__file__)
        key = str(path.relative_to(ROOT))
        if sha(path) != report['source_sha256'][key]:
            raise ValueError('A constructor/interface changed: ' + key)
    frames_path = next(Path(p) for p in report['input_sha256'] if p.endswith('/frames.json'))
    records = json.loads(frames_path.read_text())
    solids = {n: cq.Shape.importBrep(str(frames_path.parent / r['brep']))
              for n, r in records.items()}
    frames = {n: routing.frame(n, solids[n], r['ports'])
              for n, r in records.items() if 'ports' in r}
    run = lines._fluid_14(frames, solids)
    # _routing.tube uses diameter plus centreline. The centreline uses the waypoints,
    # radii and the angle table derived by the unchanged constructor from those points.
    if [list(p) for p in run.pts] != report['waypoints_mm']:
        raise ValueError('Fluid-14 waypoints changed')
    if {str(i): v for i, v in run.radii.items()} != report['radii_mm']:
        raise ValueError('Fluid-14 radii changed')
    original_diameter = records['valve-v-f']['ports']['outlet'][2]
    if run.diam != original_diameter:
        raise ValueError('Fluid-14 stock diameter changed')
    record = dict(status='pass', created_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Exact current native sweep identity; no new neighborhood claim.',
                  native_report_sha256=sha(report_path),
                  prior_lines_sha256=report['source_sha256'][str(Path(lines.__file__).relative_to(ROOT))],
                  current_lines_sha256=sha(lines.__file__),
                  checker_sha256=sha(__file__), diameter_mm=run.diam,
                  waypoints_equal=True, radii_equal=True,
                  unchanged_native_inputs=len(report['input_sha256']),
                  unchanged_constructor_sha256=sha(routing.__file__),
                  unchanged_cap_interface_sha256=sha(lines._cc.__file__),
                  assembly_current=False, production_print_released=False)
    (HERE / 'fluid14-source-currentness.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS: same native inputs, constructor, diameter, waypoints and radii')


if __name__ == '__main__':
    main()
