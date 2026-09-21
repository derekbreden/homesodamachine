#!/usr/bin/env python3
"""Read the production fluid-14 sweep against a supplied placed native G pack.

Run after the cold-core cap and pack have regenerated. This never substitutes an
old pump or removes the tube's anchor from the supplied native cap to force a pass.
The ordinary full-assembly scorecard remains responsible for all tube/tube pairs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=HERE/'fluid14-route.json')
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]
    import cadquery as cq
    import _lines as lines
    import _routing as routing
    import _clearing as clearing
    import _scorecard as card
    records_path = args.pack_cache/'frames.json'
    records = json.loads(records_path.read_text())
    if 'g-ganen-pump' not in records:
        raise ValueError('This check requires an actual placed G Ganen pack')
    inputs = {str(records_path.resolve()):sha(records_path)}
    solids = {}
    for name,row in records.items():
        path = args.pack_cache/row['brep']
        inputs[str(path.resolve())] = sha(path)
        solids[name] = cq.Shape.importBrep(str(path))
    frames = {name:routing.frame(name,solids[name],row['ports'])
              for name,row in records.items() if 'ports' in row}
    source_files = (Path(__file__),Path(lines.__file__),Path(routing.__file__),
                    Path(lines._cc.__file__))
    sources = {str(p.relative_to(ROOT)):sha(p) for p in source_files}
    run = lines._fluid_14(frames,solids)
    tube = routing.tube(run)
    bb = tube.BoundingBox()
    rows = []
    for name,shape in solids.items():
        if name in ('valve-v-f','stub-fluid-14'):
            continue
        if clearing.box_gap(bb,shape.BoundingBox()) >= 5.:
            continue
        # The G integration envelope is a compound. Skip distant native components
        # before the exact distance/boolean query without changing the tested surface.
        pieces = [s for s in shape.Solids() if clearing.box_gap(bb,s.BoundingBox()) < 5.]
        if not pieces:
            continue
        gap = min(tube.distance(s) for s in pieces)
        volume = sum(tube.intersect(s).Volume() for s in pieces if clearing.box_gap(bb,s.BoundingBox()) <= 0.)
        # The cap is the intentional bearing and endpoint body. Its actual solid must
        # still remain outside the tube; a stale unshifted anchor is a real failure.
        required_air = 0. if name == 'foam-assembly' else card.CLEARANCE_FLOOR
        passed = volume <= 1e-5 and gap >= required_air-1e-6
        row = {'name':name,'air_mm':gap,'required_air_mm':required_air,
               'overlap_mm3':volume,'pass':passed}
        rows.append(row)
        print(('PASS ' if passed else 'FAIL ')+name+f': {gap:.6f} mm air, {volume:.8g} mm3 overlap',flush=True)
    radius = min(run.radii.values(),default=run.bend)
    for path,digest in inputs.items():
        if sha(path) != digest:
            raise ValueError('Native input changed during route check: '+path)
    for path,digest in sources.items():
        if sha(ROOT/path) != digest:
            raise ValueError('Source changed during route check: '+path)
    passed = radius >= lines.TUBE_BEND-1e-6 and all(r['pass'] for r in rows)
    record = {'status':'pass' if passed else 'fail',
        'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Current production fluid-14 source against supplied placed native bodies. Tube/tube pairs require the ordinary full-assembly scorecard.',
        'assembly_current':False,'production_print_released':False,
        'input_sha256':inputs,'source_sha256':sources,
        'waypoints_mm':run.pts,'radii_mm':run.radii,'minimum_radius_mm':radius,
        'static_neighbor_readings':rows,'tube_pairs_checked':False}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    if not passed:
        raise ValueError('Fluid-14 has a native clearance or radius failure')


if __name__ == '__main__':
    main()
