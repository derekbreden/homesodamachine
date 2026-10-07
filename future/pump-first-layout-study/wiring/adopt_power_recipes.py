"""Publish selected circular power recipes for the complete member gate.

Each supplied recipe retains the live terminal mouths and axes. Publication
keeps the complete power packet false until its independent nineteen-conductor
receipt, self, device, controls, peer and full fluid-air checks pass.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from native_harness import sweep,bounds
from circular_clearance import paired_members
from power_harness import terminal_approach_members

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipts',nargs='+',type=Path)
    parser.add_argument('--names',help='Comma-separated recipe names to publish')
    args=parser.parse_args();names=set(args.names.split(','))if args.names else None
    power=json.loads((HERE/'power-candidate.json').read_bytes());selected={}
    for path in args.receipts:
        received=json.loads(path.read_bytes())
        selected.update(received.get('selected',received.get('power_routes',{})))
    if names is not None:selected={n:r for n,r in selected.items()if n in names}
    if not selected:raise ValueError('No selected power recipes')
    prepared={}
    for name,recipe in selected.items():
        old=power['power_routes'][name];points=recipe.get('points_mm',recipe.get('points'))
        a=power['ports'][old['from_key']];b=power['ports'][old['to_key']]
        if math.dist(points[0],a['point'])>1e-6 or math.dist(points[-1],b['point'])>1e-6:
            raise ValueError('Recipe changes a selected terminal mouth '+name)
        if name=='PE-under-counter':
            # The installed prepared departure ends at the selected lower
            # plane. Its exact normal stem and third point also drive the
            # independent four-tail factory landing witness.
            a['lead_paths']=[points[:3]]
        authored,record=sweep(points,old['diameter_mm'],old['radius_mm'])
        physical,cutter,proof=paired_members(authored,old['diameter_mm'],gap=1.,fuse_clearance=True)
        _,witnesses=terminal_approach_members(physical,a,b,old['diameter_mm'])
        if not physical.isValid() or not cutter.isValid() or len(cutter.Solids())!=1:
            raise ValueError('Invalid selected conductor or clearance cutter '+name)
        _,enlarged,_=paired_members(authored,old['diameter_mm'],gap=1.,fuse_clearance=False)
        checks=[]
        for index,member in enumerate(enlarged.Solids()):
            missing=abs(member.cut(cutter,tol=.0001).Volume(tol=1e-9))
            checks.append({'member':index,'enlarged_missing_mm3':missing,'pass':missing<=.001})
        if not all(row['pass']for row in checks):raise ValueError('Complete radial clearance union loses a member '+name)
        proof['complete_enlarged_member_union_containment']=checks
        record={**old,**record,'from':a,'to':b,'terminal_approach_members':witnesses,
            'physical_section_proof':proof,'native_interferences':[]}
        record.pop('received_native_recovery',None)
        prepared[name]=(physical,cutter,record)
    for name,(physical,cutter,record)in prepared.items():
        key='wire-'+name;part=power['parts'][key];tool=power['clearance_cutters'][key]
        for shape,row in [(physical,part),(cutter,tool)]:
            path=ROOT/row['brep'];shape.exportBrep(str(path))
            row.update(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bounds=bounds(shape))
        record['physical_section_proof']['published_native_sha256']=part['sha256']
        power['power_routes'][name]=record
        print(name,'published',len(physical.Solids()),'members',record['length_mm'],'mm',flush=True)
    power['pass']=False
    power['failures']=[{'check':'Independent complete nineteen-conductor member gate required after recipe publication'}]
    power.pop('physical_member_gate',None)
    (HERE/'power-candidate.json').write_text(json.dumps(power,indent=2)+'\n')

if __name__=='__main__':main()
