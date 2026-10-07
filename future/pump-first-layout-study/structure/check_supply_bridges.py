"""Native supply load-path stock, joined lid and external occupancy."""
from pathlib import Path
import hashlib, json, sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path[:0]=[str(STUDY),str(STUDY/'pump')]
import audit
import generate as G


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def box(x0,y0,z0,x1,y1,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))


def main():
    models,records,_,mates,inputs=audit.collect()
    for rel in ['routing/co2-candidate.json','mounts/check-tee-candidate.json',
                'mounts/needle-candidate.json','mounts/wr-candidate.json',
                'wiring/control-reserves.json','wiring/control-fanouts-check.json']:
        p=STUDY/rel
        if p.exists():
            d=json.loads(p.read_text());inputs[rel]=sha(p)
            for n,r in d.get('parts',{}).items():
                records[n]=r;models[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
    m=json.loads((HERE/'candidate.json').read_text())
    own={n for n in m['parts']if n=='psu'or n.startswith('supply-')}
    # The source module takes precedence over stale parent overlays during
    # this local proof; final fasteners bind the recut joined print separately.
    for n in own:
        records[n]=m['parts'][n];models[n]=cq.Shape.importBrep(str(ROOT/records[n]['brep']))
    native={n:{'brep':r['brep'],'sha256':sha(ROOT/r['brep'])}
            for n,r in records.items()if r and n in models}
    rows=[]
    for n in sorted(own):
        q=models[n];near=[];bad=[]
        for other,t in models.items():
            if other in own:continue
            if not audit.broad(G.bounds(q),G.bounds(t),1):continue
            why=audit.intended(n,other,records,mates)
            gap=q.distance(t)
            if gap>=1-1e-6:continue
            common=audit.common(q,t,why=='declared joined print root') if gap<1e-6 else 0.
            row={'other':other,'gap_mm':gap,'common_mm3':common,'intended':why};near.append(row)
            if common>.01 and why is None:bad.append(row)
        rows.append({'part':n,'pass':not bad and q.isValid()and len(q.Solids())==1,
                     'blockers':bad,'close_pairs':near,'valid':q.isValid(),'solids':len(q.Solids())})
        print(n,rows[-1],flush=True)
    lid=models['cold-core/foam-cap-lid-top']
    for n in sorted(own):
        if n.startswith(('supply-lid-boss-','supply-lid-web-')):lid=lid.fuse(models[n])
    for r in m.get('pilot_cutters',{}).values():
        if r.get('print_owner')=='cold-core-lid':lid=lid.cut(cq.Shape.importBrep(str(ROOT/r['brep'])))
    for r in m.get('clearance_cutters',{}).values():
        if r.get('print_owner')=='cold-core-lid':lid=lid.cut(cq.Shape.importBrep(str(ROOT/r['brep'])))
    structural=[{'check':'native lid and all supply hosts remain one solid',
                 'pass':lid.isValid()and len(lid.Solids())==1,
                 'valid':lid.isValid(),'solids':len(lid.Solids())}]
    web=models['supply-lid-web-1']
    fore=box(-41.,410.,253.39,-38.,413.,281.5)
    missing=fore.cut(web).Volume()
    structural.append({'check':'full3mm fore load section before the flavor portal',
                       'pass':missing<.01,'coupon_mm':[3.,3.,28.11],'missing_mm3':missing})
    portal=json.loads((STUDY/'routing/flavor-a-portal.json').read_text())
    cutter=cq.Shape.importBrep(str(ROOT/portal['brep']))
    uncut=box(-41.,410.,253.39,-38.,445.5,281.5)
    cut=uncut.intersect(cutter);b=G.bounds(cut)
    structural.append({'check':'full3mm remaining load stock above and below actual pipe portal',
                       'pass':b[2]-253.39>=3 and 281.5-b[5]>=3,
                       'removed_bounds_mm':b,'lower_stock_mm':b[2]-253.39,
                       'upper_stock_mm':281.5-b[5]})
    for i,station in enumerate([x for x in m['mounts']if x['owner']=='psu'],1):
        x,y,z=station['mouth'];host=models['supply-lid-boss-'+str(i)]
        if G.bounds(host)[2]>280:
            floor=cq.Solid.makeCylinder(4,3,cq.Vector(x,y,z-5.25-3))
            missing=floor.cut(host).Volume()
            structural.append({'check':'bridge'+str(i)+' actual3mm full blind floor',
                               'pass':missing<.01,'missing_mm3':missing})
    drift=[n for n,r in native.items()if sha(ROOT/r['brep'])!=r['sha256']]
    report={'pass':all(r['pass']for r in rows+structural)and not drift, 'native_checks':rows,
            'stock_and_join_checks':structural,'native_inputs':native,'manifest_sha256':inputs,
            'source_drift':drift,
            'scope':'Exact supply body/fasteners, supported blind bridges and full3mm load sections around the flavor portal. Final pilot passage and covers are also bound to the recut joined print in fastener-native-check.json.',
            'qualification_limits':['Rail bending, insert pullout, vibration, creep and thermal behavior require physical qualification; native stock is a geometric witness.']}
    (HERE/'supply-bridge-native-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'failed':[r for r in rows+structural if not r['pass']]}),flush=True)


if __name__=='__main__':main()
