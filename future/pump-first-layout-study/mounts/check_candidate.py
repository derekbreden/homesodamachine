"""Check the selected electronics hosts against the complete current scene."""
from pathlib import Path
import argparse,hashlib,json,sys

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY))
import audit
from evidence_binding import content_sha256

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--floor-only',action='store_true',help='Bind the floor relay module and purchased relays to the complete installed scene')
    args=parser.parse_args()
    source_inputs={str(p.relative_to(ROOT)):sha(p)for p in [Path(__file__),STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    module_path=HERE/('floor-candidate.json' if args.floor_only else 'candidate.json')
    module=json.loads(module_path.read_bytes())
    models,records,_,mates,inputs=audit.collect()
    content_bindings=dict(inputs.content_sha256)
    content_bindings[str(module_path.relative_to(ROOT))]=content_sha256(module)
    own=(set(module['parts'])|set(module.get('expected_devices',{})))&models.keys();rows=[];errors=[]
    boxes={n:audit.bbox(s)for n,s in models.items()}
    native={n:{'brep':records[n]['brep'],'sha256':sha(ROOT/records[n]['brep'])}for n in models}
    for name in sorted(own):
        shape=models[name]
        for other,obstacle in models.items():
            if name==other or (other in own and other<name):continue
            if not audit.broad(boxes[name],boxes[other]):continue
            why=audit.intended(name,other,records,mates)
            try:common=audit.common(shape,obstacle,why=='declared joined print root')
            except RuntimeError as error:
                errors.append({'parts':[name,other],'error':str(error)});continue
            rows.append({'parts':[name,other],'common_mm3':common,'intended':why,
                'pass_result':common<.01 or why is not None})
    gap=models['west-junction-platform'].distance(models['psu'])
    thermal=[{'part':'west-junction-platform','native_distance_to_psu_mm':gap,
        'minimum_geometric_air_mm':10.,'pass_result':gap>=10.-1e-6}]
    drift=[n for n,r in native.items()if sha(ROOT/r['brep'])!=r['sha256']]
    drift += [p for p,h in source_inputs.items()if sha(ROOT/p)!=h]
    manifest_drift=[p for p,h in content_bindings.items()if content_sha256(json.loads((ROOT/p).read_bytes()))!=h]
    result={'checks':rows,'operation_errors':errors,'thermal_clearances':thermal,
        'native_inputs':native,'manifest_sha256':inputs,'source_drift':drift,
        'source_inputs':source_inputs,'manifest_content_sha256':content_bindings,'manifest_drift':manifest_drift,
        'pass_result':not errors and not drift and not manifest_drift and all(r['pass_result']for r in rows+thermal),
        'qualification_scope':'Current selected host occupancy with named bearings, pilot passages and joined roots, plus the10mm platform/supply air gap. Natural ventilation, current derating, electrical insulation, mounting loads and wire dressing need their own physical qualification.'}
    (HERE/('floor-native-check.json' if args.floor_only else 'native-check.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['pass_result'],'pair_checks':len(rows),
        'unexpected':[r for r in rows if not r['pass_result']],
        'platform_psu_air_mm':gap,'operation_errors':errors,'source_drift':drift}),flush=True)
    if not result['pass_result']:raise SystemExit(1)

if __name__=='__main__':main()
