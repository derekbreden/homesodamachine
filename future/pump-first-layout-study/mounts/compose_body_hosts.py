"""Compose the four purchased fitting restraints into one scene manifest."""
from pathlib import Path
import hashlib,itertools,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY));import audit
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources

def main():
    sources=proof_sources.snapshot(__file__)
    paths=[HERE/f for f in ['needle-candidate.json','wr-candidate.json','check-tee-candidate.json']]
    manifests=[json.loads(p.read_text()) for p in paths]
    result={'parts':{},'intended_contacts':[],'checks':[],
        'inputs_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        'manifest_content_sha256':{str(p.relative_to(ROOT)):content_sha256(m)for p,m in zip(paths,manifests)},
        'source_inputs':sources,
        'retained_components':['flow-regulator','wr1110','gasher-co2','water-split'],
        'scope':'Complete nominal printed body restraints and dressed retention hardware; joined-stock, occupancy and factory motion are separate checks. Physical retention is unqualified.'}
    for m in manifests:
        if not m.get('pass'):raise ValueError('All separate fitting restraints must pass before composing')
        result['parts'].update(m['parts']);result['intended_contacts']+=m.get('intended_contacts',[])
        for key in ['shell_fuse_part_names','lid_fuse_part_names','front_shell_fuse_part_names','cap_fuse_part_names','factory_carried_part_names','factory_deferred_part_names']:
            result.setdefault(key,[]).extend(m.get(key,[]))
        for key in ['root_owner_overrides','pilot_owner_overrides','pilot_cutters','clearance_cutters','standalone_print_parts','joined_root_coupons']:
            result.setdefault(key,{}).update(m.get(key,{}))
    pairs={frozenset(p) for p in result['intended_contacts']}
    solids={n:cq.Shape.importBrep(str(ROOT/r['brep'])) for n,r in result['parts'].items()}
    for a,b in itertools.combinations(solids,2):
        if not audit.broad(audit.bbox(solids[a]),audit.bbox(solids[b]),0):continue
        volume=audit.common(solids[a],solids[b]);intended=frozenset([a,b]) in pairs
        result['checks'].append({'parts':[a,b],'common_mm3':volume,'declared_contact':intended,'pass':volume<.01 or intended})
    result['manifest_drift']=[n for n,h in result['manifest_content_sha256'].items()if manifest_content_sha256(ROOT/n)!=h]
    result['source_drift']=proof_sources.changed(sources)
    result['pass']=all(c['pass'] for c in result['checks'])and not result['manifest_drift']and not result['source_drift']
    (HERE/'body-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass'],'parts':len(solids),'checks':result['checks']},indent=2),flush=True)
    if not result['pass']:raise SystemExit(1)

if __name__=='__main__':main()
