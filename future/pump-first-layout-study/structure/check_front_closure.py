"""Close the front-top and its funnel frame against the installed upper bay.

Retained fore-column internals keep their accepted subassembly interfaces.
This proof covers the changed upper bay, including the moving frame pockets;
flexible links to fore-column devices have free ends during factory closing.
"""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY))
import audit
import baseline
from evidence_binding import manifest_content_sha256
from structure import proof_sources
from wiring import front_loom_handling

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    sources=proof_sources.snapshot(__file__,baseline.__file__,front_loom_handling.__file__)
    models,records,changed,mates,inputs=audit.collect()
    handling_path=STUDY/'wiring/front-loom-handling.json'
    handling_raw=handling_path.read_bytes();handling=json.loads(handling_raw)
    if not handling.get('pass'):raise ValueError('Reviewed complete parked contact lead is required')
    key=str(handling_path.relative_to(ROOT))
    inputs[key]=hashlib.sha256(handling_raw).hexdigest()
    inputs.content_sha256[key]=manifest_content_sha256(handling_path)
    for name,record in handling['parts'].items():
        if sha(ROOT/record['brep'])!=record['sha256']:raise ValueError('Stale parked native lead '+name)
        records[name]=record;models[name]=cq.Shape.importBrep(str(ROOT/record['brep']))
    inventory=front_loom_handling.front_inventory(models,records,changed)
    inputs.update(inventory['read_time_manifest_sha256'])
    inputs.content_sha256.update(inventory['manifest_content_sha256'])
    moving=inventory['moving']&models.keys()
    deferred=inventory['deferred'];absent=inventory['absent']
    fixed={}
    for name,shape in models.items():
        if name in moving|deferred|absent:continue
        b=audit.bbox(shape)
        if b[4]<218.8 or b[5]<253.4:continue
        # The full native body is retained when it reaches the changed bay.
        fixed[name]=shape
    fixed_boxes={n:audit.bbox(s)for n,s in fixed.items()}
    native={n:{'brep':records[n]['brep'],'sha256':sha(ROOT/records[n]['brep'])} for n in moving|fixed.keys()}
    poses=[];blockers=[];near=[]
    for travel in [inventory['required_rail_entry_travel_mm'],90,70,40,20,10,5,2,1,.5,.25,0]:
        hits=[]
        for name in sorted(moving):
            body=models[name].translate((0,-travel,0));b=audit.bbox(body)
            for other,shape in fixed.items():
                if not audit.broad(b,fixed_boxes[other],1):continue
                gap=body.distance(shape)
                if gap>=1-1e-6:continue
                why=audit.intended(name,other,records,mates) if travel==0 else None
                volume=audit.common(body,shape,why=='declared joined print root') if gap<1e-6 else 0.
                row={'travel_fore_mm':travel,'moving':name,'fixed':other,
                     'gap_mm':gap,'common_mm3':volume,'intended_at_seated':why}
                if volume>.01 and why is None:hits.append(row);blockers.append(row)
                else:near.append(row)
        poses.append({'travel_fore_mm':travel,'blockers':hits,'pass':not hits})
        print('front closing',travel,'blockers',len(hits),flush=True)
    drift=[n for n,r in native.items()if sha(ROOT/r['brep'])!=r['sha256']]+proof_sources.changed(sources)
    manifest_drift=[p for p,h in inputs.content_sha256.items() if manifest_content_sha256(ROOT/p)!=h]
    report={'pass':not blockers and not drift and not manifest_drift,'poses':poses,'blockers':blockers,'close_pairs':near,
            'moving_names':sorted(moving),'fixed_names':sorted(fixed),
            'deferred_fore_link_names':sorted(deferred&models.keys()),
            'absent_during_closing':sorted(absent&models.keys()),
            'parked_contact_lead_evidence':'wiring/front-loom-handling.json',
            'manifests_sha256':dict(inputs),'native_inputs':native,'source_drift':drift,
            'manifest_content_sha256':dict(inputs.content_sha256),
            'source_inputs':sources,'manifest_drift':manifest_drift,
            'required_rail_entry_travel_mm':inventory['required_rail_entry_travel_mm'],
            'retained_assembly_source':'hardware/assembly/enclosure-mechanical.md section4',
            'scope':'Twelve sampled fore-to-aft front-top/frame closure poses from the full102.2mm retained rail entry, with complete preassembled valve rows, local manifold tubes, tee carrier and constant-length parked contact lead. The independent parked-lead receipt proves continuous clearance against every fixed body using a swept containing prism and bounded native-distance intervals; the display and J9 loom are installed afterward. Other cabinet-spanning links remain free until final make-up; global audit owns installed routing.',
            'limits':['Sampled native rigid clearance is not continuous flexible-wire/tube compliance, factory workholding, insertion effort or physical fit qualification.']}
    (HERE/'front-closure-check.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['pass']:raise SystemExit(1)

if __name__=='__main__':main()
