"""Join the actual printed hosts and recut every declared blind pilot.

The scene retains separately named hosts for inspection. These single solids
prove their declared load paths reach the print they belong to, and bind the
native manufacturing reviews to the complete geometry rather than coupons.
"""
from pathlib import Path
import hashlib,json,io
import cadquery as cq
import sys

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/structure/print-parts'
sys.path.insert(0,str(STUDY))
from evidence_binding import content_sha256,manifest_content_sha256

def joined(left,right,owner,name):
    # A named host may already be part of the complete carved parent. Avoid
    # refusion of coincident faces only after both native material witnesses
    # establish that every right-hand solid is fully present in the parent.
    lb=left.BoundingBox();rb=right.BoundingBox()
    contained_box=all(getattr(rb,a)>=getattr(lb,a)-1e-6 for a in ['xmin','ymin','zmin']) and all(getattr(rb,a)<=getattr(lb,a)+1e-6 for a in ['xmax','ymax','zmax'])
    if contained_box:
        contained=True
        for solid in right.Solids():
            missing=solid.copy(mesh=False).cut(left.copy(mesh=False),tol=.0001)
            present=solid.copy(mesh=False).intersect(left.copy(mesh=False),tol=.0001)
            if abs(missing.Volume(tol=1e-9))>=.001 or abs(present.Volume(tol=1e-9)-solid.Volume(tol=1e-9))>=.001:
                contained=False;break
        if contained:return left.copy(mesh=False)
    attempts=[]
    for tolerance in [.0001,0,.00001]:
        try:
            result=left.copy(mesh=False).fuse(right.copy(mesh=False),tol=tolerance)
            valid=result.isValid() and bool(result.Solids())
            volume_ok=valid and max(left.Volume(tol=1e-9),right.Volume(tol=1e-9))-.001<=result.Volume(tol=1e-9)<=left.Volume(tol=1e-9)+right.Volume(tol=1e-9)+.001
            missing=[]
            excess=None
            if volume_ok:
                for operand in [left,right]:
                    missing.append(sum(abs(solid.copy(mesh=False).cut(result.copy(mesh=False),tol=.0001).Volume(tol=1e-9)) for solid in operand.Solids()))
                if max(missing)<.001:
                    outside=result.copy(mesh=False)
                    for operand in [left,right]:
                        for solid in operand.Solids():outside=outside.cut(solid.copy(mesh=False),tol=.0001)
                    excess=abs(outside.Volume(tol=1e-9))
            if volume_ok and max(missing,default=1.)<.001 and excess is not None and excess<.001:return result
            attempts.append({'tolerance_mm':tolerance,'valid':valid,'material_volume_preserved':volume_ok,'operand_missing_mm3':missing,'outside_operands_mm3':excess})
        except ValueError as error:attempts.append({'tolerance_mm':tolerance,'error':str(error)})
    raise ValueError(f'Cannot join {name} into {owner}: {attempts}')

def main():
    files={folder:STUDY/folder/'candidate.json'
               for folder in ['funnel','pump','routing','structure','mounts','wiring']
               if (STUDY/folder/'candidate.json').exists()}
    for label,path in [('fluid-mounts',STUDY/'mounts/fluid-candidate.json'),('body-mounts',STUDY/'mounts/body-candidate.json'),('water5-mounts',STUDY/'mounts/water5-hosts.json'),('tube-hosts',STUDY/'routing/tube-hosts.json'),('roof-hatch',HERE/'roof-hatch.json')]:
        if path.exists():files[label]=path
    raw_inputs={label:path.read_bytes() for label,path in files.items()}
    manifests={label:json.loads(raw)for label,raw in raw_inputs.items()}
    manifest_sha={str(files[label].relative_to(ROOT)):hashlib.sha256(raw).hexdigest()for label,raw in raw_inputs.items()}
    content_hashes={str(files[label].relative_to(ROOT)):content_sha256(json.loads(raw))for label,raw in raw_inputs.items()}
    sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [Path(__file__),STUDY/'evidence_binding.py']}
    parts={}
    for m in manifests.values():parts.update(m.get('parts',{}))
    source_records={**parts}
    for label,m in manifests.items():
        for key in ['pilot_cutters','clearance_cutters','joined_root_coupons']:
            source_records.update({label+'/'+key+'/'+n:r for n,r in m.get(key,{}).items()})
    native_bytes={};native_inputs={}
    for name,record in source_records.items():
        path=record['brep']
        raw=native_bytes.setdefault(path,(ROOT/path).read_bytes())
        digest=hashlib.sha256(raw).hexdigest()
        declared=record.get('sha256')
        if isinstance(declared,dict):declared=declared.get(path,declared.get('brep'))
        if declared and declared!=digest:raise ValueError('Stale native input '+name)
        native_inputs[name]={'brep':path,'sha256':digest}
    loaded={}
    def load(record):
        path=record['brep']
        if path not in loaded:
            loaded[path]=cq.Shape.importBrep(io.BytesIO(native_bytes[path]))
            if not loaded[path].isValid():raise ValueError('Invalid native input '+path)
        return loaded[path]
    names={
        'enclosure-back-top':{'controller-roof-boss-'+str(i) for i in range(1,5)}|{'ground-roof-boss','discharge-chain-anchor'},
        'cold-core-lid':{'supply-lid-boss-'+str(i) for i in range(1,5)}|{'supply-lid-web-1','supply-lid-web-2',
                       'vk-cradle','source-a-cradle','source-b-cradle','suction-chain-anchor'},
        'enclosure-front-top':set(),
        'funnel-frame':set(),
        'cold-core-cap':set(),
        'discharge-chain-lower-key':set(),
        'suction-chain-upper-key':set()}
    rootkeys={'shell_fuse_part_names':'enclosure-back-top','lid_fuse_part_names':'cold-core-lid',
              'front_shell_fuse_part_names':'enclosure-front-top','cap_fuse_part_names':'cold-core-cap',
              'frame_fuse_part_names':'funnel-frame'}
    for m in manifests.values():
        for key,owner in rootkeys.items():names[owner].update(m.get(key,[]))
    base={'enclosure-back-top':'enclosure-back-top','enclosure-front-top':'enclosure-front-top',
          'cold-core-lid':'cold-core/foam-cap-lid-top','cold-core-cap':'cold-core/foam-cap-top',
          'funnel-frame':'funnel-frame',
          'discharge-chain-lower-key':'discharge-chain-lower-key',
          'suction-chain-upper-key':'suction-chain-upper-key'}
    angles={'enclosure-back-top':180,'enclosure-front-top':0,'cold-core-lid':0,'cold-core-cap':0,'funnel-frame':0,
            'discharge-chain-lower-key':0,'suction-chain-upper-key':180}
    if 'asse-drip-pan' in parts:
        base['asse-drip-pan']='asse-drip-pan';names['asse-drip-pan']=set();angles['asse-drip-pan']=0
    for m in manifests.values():
        for name,rec in m.get('standalone_print_parts',{}).items():
            base[name]=rec.get('source_part',name);names[name]=set(rec.get('fuse_part_names',[]))
            angles[name]=rec.get('rotation_x_deg',0)
    for m in manifests.values():
        for host,owner in m.get('root_owner_overrides',{}).items():
            for group in names.values():group.discard(host)
            if owner not in names:raise ValueError('Undeclared root owner '+owner)
            names[owner].add(host)
    OUT.mkdir(parents=True,exist_ok=True)
    pilot_overrides={}
    for m in manifests.values():pilot_overrides.update(m.get('pilot_owner_overrides',{}))
    records={};checks=[]
    for owner,source in base.items():
        s=load(parts[source]);base_shape=s;hosts={};roots=[]
        for name in sorted(names[owner]):
            if name not in parts:raise ValueError(f'Missing declared print root {name}')
            host=load(parts[name]);hosts[name]=host
            s=joined(s,host,owner,name)
        # A raised fore PSU station reaches the lid through its rail and aft
        # web. Resolve the native contact graph, independent of fusion order.
        reached={'parent'};remaining=set(hosts);all_shapes={'parent':base_shape,**hosts};links=[]
        while remaining:
            progress=False
            for name in sorted(remaining.copy()):
                contact=next(((other,all_shapes[other].distance(hosts[name])) for other in sorted(reached)
                              if all_shapes[other].distance(hosts[name])<1e-6),None)
                if contact:
                    reached.add(name);remaining.remove(name);links.append({'name':name,'via':contact[0],'gap_mm':contact[1]});progress=True
            if not progress:break
        for name in sorted(hosts):
            roots.append({'name':name,'native_parent_reached':name in reached,
                          'direct_parent_gap_mm':base_shape.distance(hosts[name])})
        # Explicit cutter records take precedence over their displayed host
        # voids: a long relay pilot reaches down into the retained lid stock.
        for m in manifests.values():
            for name,rec in m.get('pilot_cutters',{}).items():
                target=pilot_overrides.get(name,rec.get('print_owner','cold-core-lid' if name.startswith('relay-') else None))
                if target==owner:s=s.cut(load(rec),tol=.0001)
            for rec in m.get('clearance_cutters',{}).values():
                if rec.get('print_owner')==owner:s=s.cut(load(rec),tol=.0001)
        if not s.isValid():raise ValueError('Invalid complete recut print '+owner)
        witnesses=[]
        for label,m in manifests.items():
            for name,record in m.get('joined_root_coupons',{}).items():
                if record['print_owner']!=owner:continue
                missing=abs(load(record).cut(s,tol=.0001).Volume(tol=1e-9))
                limit=record['require_missing_volume_mm3_below']
                witnesses.append({'coupon':name,'host':record['host_part'],
                                  'missing_mm3':missing,'limit_mm3':limit,'pass':missing<limit})
        path=OUT/(owner+'.brep');s.exportBrep(str(path));b=s.BoundingBox()
        records[owner]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'rotation_x_deg':angles[owner],'valid':s.isValid(),'solids':len(s.Solids()),
                        'bounds':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],
                        'native_host_roots':roots,'root_contact_graph':links,
                        'post_cut_stock_witnesses':witnesses}
        checks.append({'part':owner,'valid_single_solid':s.isValid() and len(s.Solids())==1,
                       'all_roots_reach_parent':not remaining,
                       'all_post_cut_witnesses_preserved':all(w['pass'] for w in witnesses)})
    drift=[n for n,r in native_inputs.items()if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
    drift += [p for p,h in sources.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    manifest_drift=[p for p,h in content_hashes.items() if manifest_content_sha256(ROOT/p)!=h]
    report={'parts':records,'checks':checks,'pass':not drift and not manifest_drift and all(c['valid_single_solid'] and c['all_roots_reach_parent'] and c['all_post_cut_witnesses_preserved'] for c in checks),
            'inputs_sha256':manifest_sha,'native_inputs':native_inputs,'source_drift':drift,
            'manifest_content_sha256':content_hashes,'source_inputs':sources,'manifest_drift':manifest_drift,
            'scope':'Exact connected native print stock and declared blind-pilot recuts. Does not qualify bending loads, insert pullout, creep, vibration or support-removal effort.'}
    (HERE/'print-parts.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':checks},indent=2),flush=True)

if __name__=='__main__':main()
