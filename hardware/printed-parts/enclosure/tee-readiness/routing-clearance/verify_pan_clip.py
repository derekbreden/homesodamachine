#!/usr/bin/env python3
"""Read-only native clip, nearby pack and conservative pan-withdrawal check."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pack-cache', type=Path, required=True)
    parser.add_argument('--neighbor-cache', type=Path, required=True)
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT/'hardware/manifold-layout'), str(ROOT/'hardware/scripts'),
                    str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
    import cadquery as cq
    import _box_spec
    import enclosure as enc
    import enclosure_assembly as assembly
    box_path = ROOT/'hardware/manifold-layout/enclosure-box.json'
    box, _ = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate), path=box_path)
    bounds = enc.pan_cable_clip_bounds(box)
    x0, y0, z0, x1, y1, z1 = bounds
    face = enc.back_top_flank_face()[0]
    base = enc._ybox(box.outer[0], face, y0-3, box.outer[3], z0-3, z1+3).fuse(
        enc._ybox(face, face+12, enc.back_top_wall_face(), box.outer[3], z0-3, z1+3))
    wall = enc._pan_cable_clip(base, box, up=enc.print_up('back','top'))
    room = enc._ybox(x0,x1,y0,y1,z0,z1)
    slab = enc._ybox(box.outer[0]+.001, x0-.001, y0,y1,z0,z1)
    _kind, sy, sz, width, height, _radius = box.pack.west_ports[0]
    withdrawal = enc._ybox(
        box.outer[0]-120, box.outer[0]+60,
        sy-width/2, sy+width/2,
        sz-height/2-enc.fits.supported_surface, sz+height/2)
    checks = []

    def check(name, value, limit, minimum=False):
        passed = value >= limit-1e-6 if minimum else value <= limit+1e-6
        checks.append(dict(check=name, value=value, limit=limit, minimum=minimum, passed=passed))
        print(('PASS ' if passed else 'FAIL ')+name+f': {value:.9g}', flush=True)

    check('bounded flank and rear wall: one valid solid', int(not wall.isValid())+abs(len(wall.Solids())-1),0)
    check('complete nominal 3 mm outside backing retained mm3',slab.cut(wall).Volume(),1e-5)
    check('declaration matches actual clip bounds',int(assembly.pan_cable_clip_room(box)[0][1]!=bounds),0)
    check('rear dry end clearance mm',enc.back_top_wall_face()-y1,enc.pan_cable_clip_rear_land,True)
    check('complete pan withdrawal room overlap mm3',room.intersect(withdrawal).Volume(),1e-5)
    check('complete pan withdrawal room air mm',room.distance(withdrawal),enc.pan_cable_clip_slot_gap,True)
    input_hashes = {str(box_path):sha(box_path)}
    native, disjoint = [], []
    for cache,index,key in ((args.pack_cache,'frames.json',None),(args.neighbor_cache,'neighbors.json','placed')):
        path = cache/index
        input_hashes[str(path.resolve())] = sha(path)
        records = json.loads(path.read_text())
        if key: records = records[key]
        for name, row in records.items():
            p = cache/row['brep']; input_hashes[str(p.resolve())] = sha(p)
            bb = row['bbox']
            gap = math.sqrt(sum(max(0.,bb[k+'min']-hi,lo-bb[k+'max'])**2
                               for k,lo,hi in zip('xyz',(x0,y0,z0),(x1,y1,z1))))
            if gap > 12.:
                disjoint.append(dict(name=name,bounding_box_air_lower_bound_mm=gap))
                continue
            shape = cq.Shape.importBrep(str(p))
            volume, distance = room.intersect(shape).Volume(), room.distance(shape)
            check(name+' / full clip room overlap mm3',volume,1e-5)
            check(name+' / full clip room air mm',distance,enc.fits.running,True)
            native.append(dict(name=name,overlap_mm3=volume,air_mm=distance))
    record = dict(status='pass' if all(c['passed'] for c in checks) else 'fail',
                  created_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Actual clip on bounded flank/rear-wall stock; conservative full clip room versus retained native pack, electronics and full pan withdrawal envelope. Final shell remains responsible for other printed features.',
                  box_dependency='Clip placement and final assembly kept-room declaration consume the serialized Box; neither participates in pack() or Box derivation.',
                  profile='Unchanged cable_clip.py: 18 mm run, 39 mm height, 6 mm embed, 3 mm projection/backing; print-up remains world -Z.',
                  support_access='Profile and print orientation unchanged; both end ramps and the inboard channel remain exposed before hardware installation. Final slice retains responsibility for actual generated supports.',
                  bounds_mm=bounds, checks=checks,native_neighbors=native,bbox_separated_neighbors=disjoint,
                  input_sha256=input_hashes,
                  source_sha256={str(Path(m.__file__).relative_to(ROOT)):sha(m.__file__) for m in (enc,assembly,enc._cable_clip)},
                  checker_sha256=sha(__file__),assembly_current=False,production_print_released=False)
    (HERE/'pan-clip-clearance.json').write_text(json.dumps(record,indent=2)+'\n')
    if record['status'] != 'pass': raise SystemExit(1)


if __name__ == '__main__':
    main()
