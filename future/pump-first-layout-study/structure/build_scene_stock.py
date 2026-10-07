"""Expose the exact parent stock with all declared pilot cavities recut.

Printed hosts stay separately named for inspection. The parent solids must
still contain their complete screw-tip cavities, including those extending
below a raised relay platform. Joined articles are audited separately.
"""
from pathlib import Path
import hashlib,json
import cadquery as cq
import sys
from io import BytesIO

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/structure/scene-stock'
sys.path.insert(0,str(STUDY))
from evidence_binding import content_sha256,manifest_content_sha256

def main():
    paths=[STUDY/f/'candidate.json' for f in ['funnel','pump','routing','structure','mounts','wiring']]
    paths += [STUDY/'mounts/fluid-candidate.json',STUDY/'mounts/body-candidate.json',STUDY/'mounts/water5-hosts.json',STUDY/'routing/tube-hosts.json',HERE/'roof-hatch.json']
    raw_inputs={p:p.read_bytes() for p in paths if p.exists()}
    manifests=[json.loads(raw) for raw in raw_inputs.values()]
    manifest_hashes={str(p.relative_to(STUDY)):hashlib.sha256(raw).hexdigest() for p,raw in raw_inputs.items()}
    content_hashes={str(p.relative_to(STUDY)):content_sha256(json.loads(raw)) for p,raw in raw_inputs.items()}
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [Path(__file__),STUDY/'evidence_binding.py']}
    native_inputs={}
    def load(key,record):
        path=ROOT/record['brep'];raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        declared=record.get('sha256')
        if isinstance(declared,dict):declared=declared.get(record['brep'])
        if declared and declared!=digest:raise ValueError('Changed scene-stock input '+key)
        native_inputs[key]={'brep':record['brep'],'sha256':digest}
        return cq.Shape.importBrep(BytesIO(raw))
    parts={};overrides={}
    for m in manifests:
        parts.update(m.get('parts',{}));overrides.update(m.get('pilot_owner_overrides',{}))
    owners={'cold-core-lid':'cold-core/foam-cap-lid-top',
            'cold-core-cap':'cold-core/foam-cap-top',
            'enclosure-back-top':'enclosure-back-top',
            'enclosure-front-top':'enclosure-front-top',
            'rear-roof-hatch':'rear-roof-hatch','funnel-frame':'funnel-frame'}
    records={};checks=[];OUT.mkdir(parents=True,exist_ok=True)
    for owner,name in owners.items():
        if name not in parts:continue
        original=parts[name];shape=load('parent:'+name,original);cutters=[]
        for m in manifests:
            for key,rec in m.get('pilot_cutters',{}).items():
                target=overrides.get(key,rec.get('print_owner','cold-core-lid' if key.startswith('relay-') else None))
                if target==owner:
                    shape=shape.cut(load('pilot:'+key,rec))
                    cutters.append(key)
            for key,rec in m.get('clearance_cutters',{}).items():
                if rec.get('print_owner')==owner:
                    shape=shape.cut(load('clearance:'+key,rec))
                    cutters.append(key)
        path=OUT/(owner+'.brep');shape.exportBrep(str(path));b=shape.BoundingBox()
        record={**original,'brep':str(path.relative_to(ROOT)),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]}
        record.pop('mesh',None)
        records[name]=record
        checks.append({'part':name,'valid':shape.isValid(),'solids':len(shape.Solids()),
                       'recut_pilots':cutters,'pass':shape.isValid() and len(shape.Solids())==1})
    report={'parts':records,'replacement_names':sorted(records),
            'checks':checks,'pass':all(c['pass'] for c in checks),
            'inputs_sha256':manifest_hashes,'inputs_content_sha256':content_hashes,
            'manifest_content_sha256':{str((STUDY/p).relative_to(ROOT)):h for p,h in content_hashes.items()},
            'source_inputs':sources,
            'native_inputs':native_inputs,
            'source_drift':[p for p,h in sources.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h],
            'manifest_drift':[p for p,h in content_hashes.items() if manifest_content_sha256(STUDY/p)!=h],
            'scope':'Unfused parent scene stock with the same complete blind-pilot recuts as the joined articles. No load or lifetime qualification.'}
    report['source_drift'] += [n for n,r in native_inputs.items() if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    report['pass']=report['pass'] and not report['source_drift'] and not report['manifest_drift']
    (HERE/'scene-stock.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':checks},indent=2),flush=True)
    if not report['pass']:raise SystemExit(1)

if __name__=='__main__':main()
