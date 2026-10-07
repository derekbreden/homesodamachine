"""Native integrated occupancy audit of changed bay bodies and retained neighbors.

Broad phase uses bounding boxes; all reported distances and commons use OCC
B-reps. Fitting mouth contacts and explicit structural roots are recorded as
intended separately. This audit never substitutes for physical qualification.
"""
from pathlib import Path
from collections import OrderedDict
import sys,json,time,itertools,hashlib
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.TopTools import TopTools_ListOfShape
import baseline
from evidence_binding import content_sha256

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
_BOUND_CACHE=OrderedDict()
_BOUND_CACHE_LIMIT=4096

class ManifestHashes(dict):
    """Raw label hashes plus read-time scene-content hashes by repository path."""
    def __init__(self):
        super().__init__()
        self.content_sha256={}

def bbox(s):
    # Loaded scene geometry is immutable. Solids() returns fresh wrappers of
    # the same located native shape; trimmed-torus extrema are expensive to
    # repeat. A native identity check guards every cache hit, including hash
    # collisions. A transformed shape has a different location/identity.
    key=hash(s.wrapped)
    entries=_BOUND_CACHE.get(key,[])
    for held,box in entries:
        if s.wrapped.IsSame(held):
            _BOUND_CACHE.move_to_end(key)
            return list(box)
    b=s.BoundingBox()
    box=(b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)
    _BOUND_CACHE[key]=entries+[(s.wrapped,box)]
    _BOUND_CACHE.move_to_end(key)
    if len(_BOUND_CACHE)>_BOUND_CACHE_LIMIT:_BOUND_CACHE.popitem(last=False)
    return list(box)

def broad(a,b,pad=1.):
    return all(a[i]<=b[i+3]+pad and b[i]<=a[i+3]+pad for i in range(3))

def common(a,b,exact_root_fallback=False):
    value=0.
    for s in a.Solids():
        sb=bbox(s)
        for t in b.Solids():
            if broad(sb,bbox(t),0):
                operation=BRepAlgoAPI_Common()
                arguments=TopTools_ListOfShape();arguments.Append(s.copy(mesh=False).wrapped)
                tools=TopTools_ListOfShape();tools.Append(t.copy(mesh=False).wrapped)
                operation.SetArguments(arguments);operation.SetTools(tools)
                operation.SetFuzzyValue(.0001);operation.SetRunParallel(True);operation.Build()
                if not operation.IsDone() and exact_root_fallback:
                    # Coincident root faces can defeat fuzzy classification.
                    # Only declared print roots may use a completed exact
                    # common; their joined single-solid check is separate.
                    # A failed operation retains classification state, so
                    # the exact fallback must use a fresh operation and
                    # independent native copies of this one solid pair.
                    operation=BRepAlgoAPI_Common()
                    arguments=TopTools_ListOfShape();arguments.Append(s.copy(mesh=False).wrapped)
                    tools=TopTools_ListOfShape();tools.Append(t.copy(mesh=False).wrapped)
                    operation.SetArguments(arguments);operation.SetTools(tools)
                    operation.SetFuzzyValue(0);operation.SetRunParallel(True);operation.Build()
                if not operation.IsDone():raise RuntimeError('Native common operation did not complete')
                shape=operation.Shape()
                if not shape.IsNull():
                    solids=cq.Shape.cast(shape).Solids()
                    if any(not solid.isValid()for solid in solids):raise RuntimeError('Invalid native common material solid')
                    value+=sum(abs(solid.Volume(tol=1e-9))for solid in solids)
    return value

def collect():
    saved=baseline.prepare()
    models={};records={};changed=set();mates={};roots={};inputs=ManifestHashes();root_overrides={}
    files=[(folder,HERE/folder/'candidate.json') for folder in ['funnel','pump','routing','structure','mounts','wiring']]
    files.insert(2,('pump-fluid24',HERE/'pump/fluid24-candidate.json'))
    files.append(('fluid-mounts',HERE/'mounts/fluid-candidate.json'))
    files.append(('body-mounts',HERE/'mounts/body-candidate.json'))
    files.append(('water5-mounts',HERE/'mounts/water5-hosts.json'))
    files.append(('tube-hosts',HERE/'routing/tube-hosts.json'))
    files.append(('roof-hatch',HERE/'structure/roof-hatch.json'))
    files.append(('scene-stock',HERE/'structure/scene-stock.json'))
    for folder,path in files:
        if not path.exists():continue
        raw=path.read_bytes();m=json.loads(raw)
        if folder=='scene-stock':
            stock_content=m.get('inputs_content_sha256')
            stock_inputs=stock_content if stock_content is not None else m.get('inputs_sha256',{})
            if any(not (HERE/p).is_file() or
                   (content_sha256(json.loads((HERE/p).read_bytes())) if stock_content is not None
                    else hashlib.sha256((HERE/p).read_bytes()).hexdigest())!=digest
                   for p,digest in stock_inputs.items()):
                continue
        inputs[folder]=hashlib.sha256(raw).hexdigest()
        inputs.content_sha256[str(path.relative_to(ROOT))]=content_sha256(m)
        root_overrides.update(m.get('root_owner_overrides',{}))
        for name in m.get('replacement_names',[]):records[name]=None
        for name,p in m.get('parts',{}).items():records[name]=p;changed.add(name)
        for rid,run in m.get('routes',{}).items():
            for end in ['from','to']:
                if isinstance(run.get(end),str):
                    component=run[end].split('.')[0]
                    mates[frozenset(['tube-'+rid,component])]='declared route endpoint'
        for pair in m.get('intended_contacts',[]):mates[frozenset(pair)]='declared mounting or mating interface'
        for key,parent in [('shell_fuse_part_names','enclosure-back-top'),('lid_fuse_part_names','cold-core/foam-cap-lid-top'),
                           ('front_shell_fuse_part_names','enclosure-front-top'),('cap_fuse_part_names','cold-core/foam-cap-top'),
                           ('frame_fuse_part_names','funnel-frame')]:
            for host in m.get(key,[]):roots[host]=parent
    for i in range(1,5):
        roots['controller-roof-boss-'+str(i)]='enclosure-back-top'
        roots['supply-lid-boss-'+str(i)]='cold-core/foam-cap-lid-top'
    roots.update({'ground-roof-boss':'enclosure-back-top','discharge-chain-anchor':'enclosure-back-top',
                  'supply-lid-web-1':'cold-core/foam-cap-lid-top','supply-lid-web-2':'cold-core/foam-cap-lid-top',
                  'vk-cradle':'cold-core/foam-cap-lid-top','source-a-cradle':'cold-core/foam-cap-lid-top',
                  'source-b-cradle':'cold-core/foam-cap-lid-top','suction-chain-anchor':'cold-core/foam-cap-lid-top'})
    roots.update(root_overrides)
    for host,parent in roots.items():mates[frozenset([host,parent])]='declared joined print root'
    for a,b in itertools.combinations(roots,2):
        if roots[a]==roots[b]:mates[frozenset([a,b])]='joined stock in the same declared print'
    for name,p in saved['parts'].items():
        if name in records:continue
        b=p['bounds']
        if b[5]<248 or b[4]<181:continue
        if name.startswith('cold-core/') and name not in ['cold-core/foam-cap-top','cold-core/foam-cap-lid-top']:continue
        if name.startswith(('enclosure-front-bottom','enclosure-back-bottom','enclosure-pump-','enclosure-tee-','tee-carrier-spring','grip-')):continue
        records[name]={'brep':str((baseline.CACHE/p['file']).relative_to(ROOT)),'role':'retained'}
    for name,p in records.items():
        if p is not None:models[name]=cq.Shape.importBrep(str(ROOT/p['brep']))
    return models,records,changed,mates,inputs

def intended(a,b,records,mates):
    pair=frozenset([a,b])
    if pair in mates:return mates[pair]
    if a.startswith('enclosure-') and b.startswith('enclosure-'):return 'retained enclosure joint'
    if a in ['funnel','funnel-frame','funnel-cover'] and b in ['funnel','funnel-frame','funnel-cover']:return 'funnel mating surfaces'
    if a.startswith('hose-') or b.startswith('hose-'):
        other=b if a.startswith('hose-') else a
        if other in ['g-ganen-pump','suction-chain','discharge-chain'] or other.startswith(('hose-','tube-water-6','tube-water-7')):return 'barb engagement or clamp bearing'
    for host,other in [(a,b),(b,a)]:
        if host.startswith(('controller-','supply-')) and other in ['pcba','psu']:return 'mounting land or fastener passage'
        if host=='ground-roof-boss' and other=='ground-stack':return 'ground screw engagement'
        if host.startswith('pump-mount') and other=='g-ganen-pump':return 'pump foot clamp'
        if host.startswith('valve-') and 'seat' in host and other.startswith(('valve-v-','coil-v-')):return 'native valve seat bearing'
        if host=='VK-seat' and other=='vk-solenoid':return 'native valve seat bearing'
    return None

def main():
    source_paths=[Path(__file__),HERE/'baseline.py',HERE/'evidence_binding.py']
    source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    models,records,changed,mates,inputs=collect();boxes={n:bbox(s) for n,s in models.items()}
    native_inputs={n:{'brep':records[n]['brep'],'sha256':hashlib.sha256((ROOT/records[n]['brep']).read_bytes()).hexdigest(),
                      'valid':s.isValid(),'solids':len(s.Solids())}for n,s in models.items()}
    pairs=[(a,b) for a,b in itertools.combinations(models,2)
           if (a in changed or b in changed) and broad(boxes[a],boxes[b])]
    print('native narrow pairs',len(pairs),'parts',len(models),flush=True)
    rows=[];operation_errors=[];start=time.time()
    for i,(a,b) in enumerate(pairs):
        why=intended(a,b,records,mates)
        gap=models[a].distance(models[b])
        if gap>=1.-1e-6:continue
        try:overlap=common(models[a],models[b],why=='declared joined print root') if gap<1e-6 else 0.
        except RuntimeError as error:
            operation_errors.append({'a':a,'b':b,'error':str(error)})
            print('NATIVE OPERATION FAILURE',a,b,str(error),flush=True)
            continue
        row={'a':a,'b':b,'distance_mm':gap,'overlap_mm3':overlap,'intended':why}
        rows.append(row)
        if overlap>.01 and why is None:print('INTERFERENCE',json.dumps(row),flush=True)
        if i%100==0:print('progress',i,'of',len(pairs),round(time.time()-start,1),flush=True)
    unexpected=[r for r in rows if r['overlap_mm3']>.01 and r['intended'] is None]
    invalid=[n for n,r in native_inputs.items() if not r['valid']]
    width_overruns=[{'part':n,'xmin_mm':boxes[n][0],'xmax_mm':boxes[n][3],
                      'overrun_mm':max(-107.5-boxes[n][0],boxes[n][3]-107.5)}
                    for n in sorted(changed) if n in boxes and (boxes[n][0]<-107.5001 or boxes[n][3]>107.5001)]
    source_drift=[name for name,r in native_inputs.items()
                  if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    source_drift += [p for p,digest in source_inputs.items()
                     if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=digest]
    manifest_drift=[p for p,digest in inputs.content_sha256.items()
                    if content_sha256(json.loads((ROOT/p).read_bytes()))!=digest]
    result={'baseline_sha256':baseline.prepare()['sha256'],'manifests_sha256':inputs,'native_inputs':native_inputs,
            'manifest_content_sha256':inputs.content_sha256,'source_inputs':source_inputs,
            'source_drift':source_drift,'manifest_drift':manifest_drift,
            'invalid_parts':invalid,'parts':len(models),'tested_pairs':len(pairs),
            'interferences':unexpected,'close_pairs':rows,'appliance_width_bound_mm':215,
            'width_overruns':width_overruns,'operation_errors':operation_errors,
            'pass':len(unexpected)==0 and not invalid and not width_overruns and not operation_errors and not source_drift and not manifest_drift,
            'elapsed_seconds':time.time()-start,'scope':'Exact nominal occupancy with named connection/printed-root contacts. Clear geometry does not establish assembly tolerance, hose memory, mount loads, cooling or operational performance.'}
    (HERE/'native-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print('DONE',len(unexpected),'unexpected overlaps',len(width_overruns),'width overruns',flush=True)

if __name__=='__main__':main()
