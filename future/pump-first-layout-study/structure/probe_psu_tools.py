"""Native reservations for a2.5AF L key at all four seated PSU screws.

The circular sweep is a conservative envelope around the2.5AF hex section.
Tool procurement, actual inside bend, torque and operator handling are physical
qualifications. Purchased screw socket engagement is an explicit intended pair.
"""
from pathlib import Path
import json,sys,math,hashlib
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'pump'))
import generate as G

RADIUS=2.5/math.sqrt(3)
SHORT=32.;LONG=160.;ELBOW=2.

def key(at,h):
    tip=cq.Vector(*at);h=cq.Vector(*h).normalized();up=cq.Vector(0,0,1)
    vertex=tip+up*SHORT;a=vertex-up*ELBOW
    edge,b,_,_=G.exact_arc(a,up,h,ELBOW)
    wire=cq.Wire.assembleEdges([cq.Edge.makeLine(tip,a),edge,cq.Edge.makeLine(b,vertex+h*LONG)])
    s=cq.Solid.sweep(cq.Wire.makeCircle(RADIUS,tip,up),[],wire,makeSolid=True,isFrenet=True)
    return s,vertex,h

def main():
    recs={};removed=set();now=set()
    idx=G.baseline.prepare()
    for n,r in idx['parts'].items():recs[n]={'brep':str((G.baseline.CACHE/r['file']).relative_to(ROOT))}
    for folder in ['funnel','pump','routing','structure','mounts','controls','power']:
        p=HERE.parent/folder/'candidate.json'
        if not p.exists():continue
        m=json.loads(p.read_text());removed.update(m.get('replacement_names',[]));recs.update(m.get('parts',{}));now.update(m.get('parts',{}))
    recs={n:r for n,r in recs.items()if n not in removed or n in now}
    absent={'enclosure-front-top','funnel','funnel-frame','funnel-cover','asse-drip-pan','moisture-plate','display','display-cover','display-gasket'}
    flex={n for n,r in recs.items()if n.startswith(('wire-','loom-','harness-','power-','control-'))}
    flex|={'tube-water-2','tube-water-3','tube-water-supply-link','tube-water-5','tube-water-6','tube-co2-0','tube-co2-1','tube-fluid-1','tube-fluid-2','tube-fluid-14','tube-fluid-18','tube-fluid-28'}
    shapes={n:cq.Shape.importBrep(str(ROOT/r['brep']))for n,r in recs.items()if n not in absent}
    boxes={n:G.bounds(s)for n,s in shapes.items()};rows=[];inputs={};out=ROOT/'.cache/pump-first-layout/structure/psu-tools';out.mkdir(parents=True,exist_ok=True)
    structure=json.loads((HERE/'candidate.json').read_text());mounts=[m for m in structure['mounts']if m['owner']=='psu']
    def test(label,s,station,c14_absent=False):
        box=G.bounds(s);bad=[];trial=[];near=[]
        for n,t in shapes.items():
            if n=='supply-screw-'+str(station):continue
            if c14_absent and n=='c14-inlet':continue
            b=boxes[n]
            if not all(box[i]<=b[i+3]+1 and b[i]<=box[i+3]+1 for i in range(3)):continue
            gap=s.distance(t)
            if gap>=1-1e-6:continue
            common=G.overlap(s,t)if gap<1e-6 else 0.
            r={'other':n,'gap_mm':gap,'common_mm3':common}
            if n in flex:
                if common>.01:trial.append(r)
            elif common>.01:bad.append(r)
            else:near.append(r)
            inputs[n]={'brep':recs[n]['brep'],'sha256':hashlib.sha256((ROOT/recs[n]['brep']).read_bytes()).hexdigest()}
        p=out/(str(station)+'-'+label+'.brep');s.exportBrep(str(p))
        r={'station':station,'pose':label,'c14_absent':c14_absent,'pass':not bad,'blockers':bad,'deferred_flexible_trial':trial,'close_rigid_pairs':near,'brep':str(p.relative_to(ROOT))}
        rows.append(r);print(station,label,'rigid',bad,'flex',trial,flush=True)
    for i,m in enumerate(mounts,1):
        x,y,z=m['mouth'];screw=shapes['supply-screw-'+str(i)];headtop=G.bounds(screw)[5]
        tip=(x,y,headtop-1.7)
        if x<0:
            dy=math.sqrt(LONG*LONG-(-90-x)**2)
            h=(-90-x,-dy,0)
        else:h=(0,-1,0)
        s,v,h=key(tip,h);test('fore-seated',s,i)
        test('fore-withdraw-1p8',s.translate((0,0,1.8)),i)
        if x<0:
            s,v,h=key(tip,(-72-x,468.3-y,0));test('rear-c14-seated',s,i,True)
            lifted=s.translate((0,0,1.8));v=v+cq.Vector(0,0,1.8)
            test('rear-c14-withdraw-1p8',lifted,i,True)
            for deg in [20,40,55,68]:test('rear-c14-roll-'+str(deg),lifted.rotate(v.toTuple(),(v+h).toTuple(),deg),i,True)
            flat=lifted.rotate(v.toTuple(),(v+h).toTuple(),68).translate((0,0,327.4-v.z))
            test('rear-c14-lower',flat,i,True)
            v=cq.Vector(v.x,v.y,327.4)
            flat=flat.rotate(v.toTuple(),(v+h).toTuple(),20)
            test('rear-c14-flat88',flat,i,True)
            distance=(471.4-v.y)/h.y
            for d in [distance*k/5 for k in range(1,6)]:test('rear-c14-approach-'+str(round(d,2)),flat.translate(h*d),i,True)
        else:
            lifted=s.translate((0,0,1.8));v=v+cq.Vector(0,0,1.8)
            for deg in [-20,-40,-55,-68]:test('fore-roll-'+str(deg),lifted.rotate(v.toTuple(),(v+h).toTuple(),deg),i)
            flat=lifted.rotate(v.toTuple(),(v+h).toTuple(),-68).translate((0,0,327.4-v.z))
            test('fore-lower',flat,i)
            v=cq.Vector(v.x,v.y,327.4);flat=flat.rotate(v.toTuple(),(v+h).toTuple(),-20)
            test('fore-flat88',flat,i)
            for d in [20,40,60,80,100,120]:test('fore-extract-'+str(d),flat.translate(h*d),i)
    result={'tool_reservation':{'across_flats_mm':2.5,'conservative_radius_mm':RADIUS,'short_leg_mm':SHORT,'long_leg_mm':LONG,'centreline_elbow_radius_mm':ELBOW,'socket_engagement_mm':1.7},'poses':rows,'native_inputs':inputs,
        'limits':['Actual key availability, inside bend, socket depth, applied torque, operator grip and continuous insertion/withdrawal are physical qualifications. The supplied circular sweep conservatively contains the2.5AF section.',
            'Purchased screw socket engagement is the intentional screw/key pair; reference display heads are simple occupied cap-head envelopes.','Flexible routes listed in each trial remain free for assembly; no final installed wire/tube sweep is asserted to represent assembly deformation.']}
    (HERE/'psu-tool-probe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'poses':len(rows),'failed':sum(not r['pass']for r in rows)}),flush=True)

if __name__=='__main__':main()
