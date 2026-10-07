"""Bind the final study claims to the exact currently published geometry.

Passing earlier shapes is insufficient. This check rejects stale native inputs,
missing circuit occupancy, incomplete joined parts and unmatched slice records.
It does not promote geometric evidence to physical qualification.
"""
from pathlib import Path
import hashlib,json
from evidence_binding import manifest_content_sha256

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def read(name):return json.loads((HERE/name).read_text())

def main():
    rows=[]
    def check(label,passed,**data):
        rows.append({'check':label,'pass':bool(passed),**data})
        print(('PASS ' if passed else 'FAIL ')+label,flush=True)
    gates={
        'native-audit.json':'pass',
        'pump/candidate.json':'all_checks_pass',
        'pump/fluid24-candidate.json':'pass',
        'pump/external-native-check.json':'pass',
        'funnel/motion-check.json':'pass_result',
        'funnel/frame-continuous-closure-check.json':'pass',
        'funnel/mating-final-frame.json':'pass',
        'mounts/candidate.json':'pass_result',
        'mounts/native-check.json':'pass_result',
        'mounts/floor-native-check.json':'pass_result',
        'mounts/fluid-candidate.json':'pass',
        'mounts/body-candidate.json':'pass',
        'mounts/water5-hosts.json':'pass',
        'routing/co2-candidate.json':'pass',
        'routing/tube-hosts.json':'pass',
        'routing/strict-route-audit.json':'pass',
        'routing/water-ring-finish.json':'pass',
        'routing/psu-surround-feasibility.json':'source_binding_pass',
        'routing/psu-coupled-probe.json':'source_binding_pass',
        'structure/print-parts.json':'pass',
        'structure/print-material-union-check.json':'pass',
        'structure/candidate.json':'shell_build_pass',
        'structure/pan-slot.json':'pass',
        'structure/water5-key-pocket.json':'pass',
        'structure/roof-hatch.json':'pass',
        'structure/ground-make-up-check.json':'pass',
        'structure/g2-factory-tool-probe.json':'pass',
        'structure/scene-stock.json':'pass',
        'structure/hatch-hose-check.json':'pass',
        'structure/factory-slide-check.json':'pass',
        'structure/asse-factory-check.json':'pass',
        'structure/front-closure-check.json':'pass',
        'structure/fastener-native-check.json':'pass',
        'wiring/power-candidate.json':'pass',
        'wiring/power-members-check.json':'pass',
        'wiring/join-check.json':'pass',
        'wiring/controls-candidate.json':'pass',
        'wiring/control-reserves.json':'pass',
        'wiring/control-fanouts-check.json':'pass',
        'wiring/static-controls-pair-check.json':'pass',
        'wiring/control-fluid-air-check.json':'pass',
        'wiring/control-terminal-owner-check.json':'pass',
        'wiring/front-loom-handling.json':'pass',
        'wiring/candidate.json':'pass'}
    for name,field in gates.items():
        path=HERE/name
        check(name+(' selected-scene bindings pass' if field=='source_binding_pass' else ' passes'),path.exists() and read(name).get(field) is True)
        if path.exists():
            evidence=read(name)
            reuse=evidence.get('original_check_reuse')
            if isinstance(reuse,dict):
                receipt=ROOT/reuse['receipt']
                check(name+' original root/coupon receipt remains exact',
                      reuse.get('pass') is True and receipt.is_file() and sha(receipt)==reuse['receipt_sha256'])
                stale=[p for p,digest in reuse.get('unchanged_check_sources_sha256',{}).items()
                       if not (ROOT/p).is_file() or sha(ROOT/p)!=digest]
                check(name+' reused root/coupon producers remain exact',not stale,stale=stale)
            native_inputs=evidence.get('native_inputs',evidence.get('selected_native_inputs',{}))
            changed_inputs=[n for n,r in native_inputs.items()
                            if not (ROOT/r['brep']).exists() or sha(ROOT/r['brep'])!=r['sha256']]
            if native_inputs:
                check(name+' native inputs remain exact',not changed_inputs,stale=changed_inputs)
            if 'source_drift' in evidence:
                check(name+' had stable inputs during execution',not evidence['source_drift'])
            if 'manifest_drift' in evidence:
                check(name+' had stable manifests during execution',not evidence['manifest_drift'])
            content_bindings=evidence.get('manifest_content_sha256',{})
            if content_bindings:
                stale=[]
                for p,digest in content_bindings.items():
                    actual=ROOT/p if p.startswith(('.cache/','future/','hardware/')) else HERE/p
                    if not actual.is_file() or manifest_content_sha256(actual)!=digest:stale.append(p)
                check(name+' substantive manifest inputs remain exact',not stale,stale=stale)
            for key in ['inputs_sha256','interfaces_sha256','input_manifests_sha256','manifests_sha256','manifest_sha256','module_sha256','source_inputs','source_sha256']:
                records=evidence.get(key,{})
                if not isinstance(records,dict):continue
                paths={p:digest for p,digest in records.items()
                       if p.startswith(('.cache/','future/','hardware/')) or (HERE/p).is_file()}
                if paths:
                    stale=[]
                    for p,digest in paths.items():
                        # The raw digest remains provenance. A read-time
                        # content snapshot avoids circular check-report
                        # dependencies while retaining every scene parameter.
                        actual=ROOT/p if p.startswith(('.cache/','future/','hardware/')) else HERE/p
                        canonical=str(actual.relative_to(ROOT))
                        if key not in ['source_inputs','source_sha256'] and (p in content_bindings or canonical in content_bindings):continue
                        if not actual.exists() or sha(actual)!=digest:stale.append(p)
                    check(name+' '+key+' remain exact',not stale,stale=stale)
    if not (HERE/'wiring/candidate.json').exists():
        check('complete circuit manifest present',False)
        power=read('wiring/power-candidate.json') if (HERE/'wiring/power-candidate.json').exists() else {}
    else:
        power=read('wiring/power-candidate.json')
        controls=read('wiring/controls-candidate.json')
        merged=read('wiring/candidate.json')
        check('nineteen power conductors occupied',len(power.get('power_routes',{}))==19)
        check('all canonical control nets represented',len(controls.get('jobs',[]))==71)
        expected={**power['parts'],**controls['parts']}
        missing=[n for n,r in expected.items() if merged.get('parts',{}).get(n,{}).get('sha256')!=r.get('sha256')]
        check('merged scene includes every circuit solid',not missing,missing=missing)
    audit=read('native-audit.json')
    labels={'funnel':'funnel/candidate.json','pump':'pump/candidate.json',
            'pump-fluid24':'pump/fluid24-candidate.json','routing':'routing/candidate.json',
            'structure':'structure/candidate.json','mounts':'mounts/candidate.json',
            'wiring':'wiring/candidate.json','fluid-mounts':'mounts/fluid-candidate.json',
            'body-mounts':'mounts/body-candidate.json',
            'water5-mounts':'mounts/water5-hosts.json',
            'tube-hosts':'routing/tube-hosts.json',
            'roof-hatch':'structure/roof-hatch.json','scene-stock':'structure/scene-stock.json'}
    stale=[k for k,f in labels.items() if not (HERE/f).exists() or audit.get('manifests_sha256',{}).get(k)!=sha(HERE/f)]
    check('integrated audit uses final manifests',not stale,stale=stale)
    stale_native=[n for n,r in audit.get('native_inputs',{}).items()
                  if not (ROOT/r['brep']).exists() or sha(ROOT/r['brep'])!=r['sha256']]
    check('integrated native inputs remain exact',not stale_native,stale=stale_native)
    check('original215mm width retained',audit.get('appliance_width_bound_mm')==215 and not audit.get('width_overruns',[True]))
    funnel=read('funnel/candidate.json')
    check('selected60mm funnel bound',funnel['aft_extension_mm']==60)
    mating=read('funnel/mating-final-frame.json')
    prints=read('structure/print-parts.json')
    material=read('structure/print-material-union-check.json')
    material_stale=[name for name,record in prints['parts'].items()
                    if material.get('owners',{}).get(name,{}).get('final_sha256')!=sha(ROOT/record['brep'])]
    check('every final print retains its declared native material',
          prints.get('material_union_check',{}).get('pass') is True and not material_stale
          and set(material.get('owners',{}))==set(prints['parts']),stale=material_stale)
    check('retained funnel mating proof uses final frame',mating['frame_sha256']==sha(ROOT/prints['parts']['funnel-frame']['brep']))
    exits=read('wiring/lower-lead-exits.json')
    check('complete lower lead exteriors included in power',all(power.get('parts',{}).get(n,{}).get('sha256')==r['sha256'] for n,r in exits['parts'].items()))
    routing=read('routing/candidate.json')
    routes=routing.get('routes',{})
    finished=set(routing.get('routing_status',{}).get('finished',[]))
    missing_route_parts=[n for r in routes.values() for n in r.get('parts',[]) if n not in routing.get('parts',{})]
    check('thirteen complete fluid and gas runs occupied',len(routes)==13 and finished==set(routes) and not missing_route_parts,
          unfinished=sorted(set(routes)-finished),missing_parts=missing_route_parts)
    from manufacturing.review_slices import selected_parts
    parts=selected_parts();missing=[];stale_slices=[];stale_supports=[]
    for name,(record,angle,recipe) in parts.items():
        path=HERE/'manufacturing'/(name+'-slice.json')
        support_path=HERE/'manufacturing'/(name+'-supports.json')
        if not path.exists() or not support_path.exists():missing.append(name);continue
        review=json.loads(path.read_text());support=json.loads(support_path.read_text())
        actual=sha(ROOT/record['brep'])
        if review['brep_sha256']!=actual or review['slice_return_code']!=0 or review['warnings'] or review['rotation_x_deg']!=angle or review['review_source_sha256']!=sha(HERE/'manufacturing/review_slices.py'):
            stale_slices.append(name)
        if support['inputs'].get('brep_sha256')!=actual or support['inputs'].get('archive_sha256')!=review['archive_sha256']:
            stale_supports.append(name)
    check('all joined articles and tooling have slices/supports',not missing,missing=missing)
    check('successful native slices match final articles',not stale_slices,stale=stale_slices)
    check('complete support topology matches final slices',not stale_supports,stale=stale_supports)
    report={'pass':all(r['pass'] for r in rows),'checks':rows,
            'source_sha256':sha(Path(__file__)),
            'scope':'Exact study-manifest/native-input/slice consistency. No physical load, fit, thermal, electrical, wet-flow or lifetime qualification is inferred.'}
    (HERE/'evidence-check.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['pass']:raise SystemExit(1)

if __name__=='__main__':main()
