"""Manual native reading of the integral routing features in back-top.

Run when reviewing these routing changes. This is not a build or commit gate.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware'/'scripts').is_dir())
HERE=Path(__file__).resolve().parent
ENC=HERE.parent
sys.path[:0]=[str(ENC),str(ROOT/'hardware'/'printed-parts'/'cadlib'),str(ROOT)]

import cadquery as cq
import _route_snaps


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path=ENC/'enclosure-back-top.step'
    part=cq.importers.importStep(str(path)).val()
    rows=[]
    for site,feature in _route_snaps.features('enclosure-back-top'):
        missing=abs(feature.cut(part).Volume())
        b=feature.BoundingBox()
        row=dict(id=site['id'],kind=site['kind'],datums=site,
            native_feature_valid=feature.isValid(),native_feature_solids=len(feature.Solids()),
            volume_mm3=feature.Volume(),missing_from_part_mm3=missing,
            bounds_world_mm=[getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')])
        if site['kind']=='tube':
            direction=cq.Vector(*site['along'])
            centre=cq.Vector(*site['centre'])
            tube=cq.Solid.makeCylinder(site['tube_od']/2.,site['span'],
                                        centre-direction*(site['span']/2.),direction)
            row.update(nominal_tube_overlap_mm3=abs(feature.intersect(tube).Volume()),
                       nominal_tube_radial_clearance_mm=feature.distance(tube))
        rows.append(row)
    sources=[ROOT/'hardware/printed-parts/cadlib/route_snap.py',ENC/'enclosure.py',
        ENC/'_route_snaps.py',ENC/'_tube_snap_sites.py',
        ROOT/'hardware/wiring/installed/retainers.py']
    result=dict(scope='Manual native construction and materialization reading; physical retention and full-shell slicing are separate.',
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
        piece=str(path.relative_to(ROOT)),piece_sha256=sha(path),
        stl_sha256=sha(ENC/'enclosure-back-top.stl'),
        payload_sha256=sha(ENC/'enclosure-back-top.step.mesh'),
        part_valid=part.isValid(),part_solids=len(part.Solids()),
        tube_count=sum(r['kind']=='tube' for r in rows),
        cable_count=sum(r['kind']=='cable' for r in rows),features=rows)
    result['pass']=(result['part_valid'] and result['part_solids']==1
        and result['tube_count']==4 and result['cable_count']==3
        and all(r['native_feature_valid'] and r['native_feature_solids']==1
                and r['missing_from_part_mm3']<1.e-4 for r in rows)
        and all(r.get('nominal_tube_overlap_mm3',0.)<1.e-6 for r in rows))
    (HERE/'native-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('features','source_sha256')},indent=2))
    print(json.dumps([{k:r[k] for k in ('id','kind','missing_from_part_mm3')} for r in rows],indent=2))
    if not result['pass']:
        raise ValueError('A routing feature is not fully present in its native host')


if __name__=='__main__':
    main()
