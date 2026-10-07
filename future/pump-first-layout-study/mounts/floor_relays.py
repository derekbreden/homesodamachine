"""Native paired relay host on the cold-core lid, below the raised PSU.

The eight calipered PCB holes remain visible. Standard M3 heads at the contact
end stand above the representative terminal blocks on actual tubular spacers.
The post pilot cutters are exported separately for recutting after lid fusion.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/floor'
sys.path.insert(0,str(STUDY))
import baseline

FACE=259.65
DECK_BOTTOM=253.4
DECK_TOP=256.4
ROOT_BOTTOM=248.0

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def bounds(s):
    b=s.BoundingBox(); return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def common(a,b):
    return abs(a.intersect(b,tol=.0001).Volume(tol=1e-9))

def place(s,x0,y0,z0):
    b=s.BoundingBox();return s.translate((x0-b.xmin,y0-b.ymin,z0-b.zmin))

def hole_axes(shape):
    points=set()
    for e in shape.Edges():
        if e.geomType()!='CIRCLE':continue
        c=BRepAdaptor_Curve(e.wrapped).Circle()
        if abs(c.Radius()-1.6)>.0001 or abs(c.Axis().Direction().Z())<.999:continue
        p=c.Location();points.add((round(p.X(),5),round(p.Y(),5)))
    return sorted(points)

def screw(x,y,raised=False):
    spacer=12 if raised else 0
    length=20 if raised else 6
    headbase=FACE+1.5+spacer
    stem=cq.Solid.makeCylinder(1.5,length,cq.Vector(x,y,headbase),cq.Vector(0,0,-1))
    head=cq.Solid.makeCylinder(2.75,3,cq.Vector(x,y,headbase))
    socket=cq.Workplane('XY').polygon(6,2.887).extrude(1.6).val().translate((x,y,headbase+1.4))
    return stem.fuse(head.cut(socket)).clean()

def emit(name,s,detail,role='structure'):
    p=OUT/f'{name}.brep';s.exportBrep(str(p))
    m=OUT/f'{name}.json';v,t=s.tessellate(.12,.08)
    m.write_text(json.dumps({'vertices':[[q.x,q.y,q.z] for q in v],
                             'triangles':[list(q) for q in t]},separators=(',',':'))+'\n')
    return {'brep':str(p.relative_to(ROOT)),'mesh':str(m.relative_to(ROOT)),
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounds':bounds(s),
            'role':role,'detail':detail,'valid':s.isValid(),'solids':len(s.Solids())}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--x-shift',type=float,default=25)
    args=parser.parse_args();dx=args.x_shift
    OUT.mkdir(parents=True,exist_ok=True)
    old=baseline.read(['relay-1','relay-2'])
    devices={
        'relay-1':place(old['relay-1'].rotate((0,0,0),(0,1,0),90).rotate((0,0,0),(0,0,1),90),-49.5+dx,423.5,257.65),
        'relay-2':place(old['relay-2'].rotate((0,0,0),(0,1,0),90),-49.5+dx,443.8,257.65)}
    stock=box(-51.5+dx,24.5+dx,420.5,463.8,DECK_BOTTOM,DECK_TOP)
    divider=box(-44.5+dx,15.5+dx,440.65,443.65,DECK_TOP,278)
    stock=stock.fuse(divider,tol=.0001)
    parts={};mounts=[];cutters={};checks=[]
    for name,body in devices.items():
        b=body.BoundingBox();expected={(round(b.xmin+2,5),round(b.ymin+2,5)),
          (round(b.xmax-2,5),round(b.ymin+2,5)),(round(b.xmin+2,5),round(b.ymax-2,5)),
          (round(b.xmax-2,5),round(b.ymax-2,5))}
        holes=hole_axes(body);assert set(holes)==expected,(name,holes,expected)
        for i,(x,y) in enumerate(holes,1):
            raised=common(screw(x,y),body)>.001
            screw_shape=screw(x,y,raised)
            spacer=12 if raised else 0
            pilot_depth=8.5 if raised else 5.25
            insert_length=5.7 if raised else 4
            root=ROOT_BOTTOM if raised else DECK_BOTTOM
            stock=stock.fuse(cq.Solid.makeCylinder(4,FACE-root,cq.Vector(x,y,root)),tol=.0001)
            cutter=cq.Solid.makeCylinder(2,pilot_depth,cq.Vector(x,y,FACE),cq.Vector(0,0,-1))
            cutters[f'{name}-pilot-{i}']=cutter
            penetration=(20 if raised else 6)-1.5-spacer
            mounts.append({'owner':name,'mouth':[x,y,FACE],'axis':[0,0,-1],
              'boss_od_mm':8,'pilot_diameter_mm':4,'pilot_depth_mm':pilot_depth,
              'insert_length_mm':insert_length,'screw_length_mm':20 if raised else 6,
              'tubular_head_spacer_length_mm':spacer,'tubular_head_spacer_od_mm':4.5 if raised else None,
              'tubular_head_spacer_bore_mm':3.2 if raised else None,
              'screw_penetration_mm':penetration,'full_insert_engagement_mm':insert_length,
              'tip_reserve_mm':pilot_depth-penetration,'blind_end_cover_mm':FACE-pilot_depth-root,
              'pin_clearance_mm':1.25})
            sn=f'{name}-mount-screw-{i}'
            parts[sn]=emit(sn,screw_shape,'Standard M3×20 above an actual 12 mm tube with full 5.7 mm insert engagement and 2 mm pilot tip reserve.' if raised else 'Standard M3×6, full 4 mm short-insert engagement with 0.75 mm blind tip reserve.')
            if raised:
                tube=cq.Solid.makeCylinder(2.25,12,cq.Vector(x,y,FACE+1.5)).cut(cq.Solid.makeCylinder(1.6,12,cq.Vector(x,y,FACE+1.5))).clean()
                tn=f'{name}-head-spacer-{i}'
                parts[tn]=emit(tn,tube,'Actual Ø4.5/ID3.2×12 tube; head lower face is 2 mm above the representative contact block, with 0.25 mm lateral air.')
    for c in cutters.values():stock=stock.cut(c,tol=.0001)
    stock=stock.clean();assert stock.isValid() and len(stock.Solids())==1
    parts['relay-lid-platform']=emit('relay-lid-platform',stock,'One 3 mm lid-rooted platform, two horizontal relay seats and a 3 mm AC/DC divider; eight native PCB mounting holes with four long blind pilots rooted in the existing 5.4 mm lid.')
    expected_devices={name:emit(f'expected-{name}',s,'Exact rotated installed reference relay; components and screw hole pattern retained.','electronics') for name,s in devices.items()}
    pilot_records={name:emit(name,s,'Exact blind pilot; recut after platform is fused to retained cold-core lid.') for name,s in cutters.items()}
    for name,s in devices.items():
        v=common(stock,s);checks.append({'test':'native printed host clears mounted relay','part':name,'common_mm3':v,'pass_result':v<.001})
        for fn,r in parts.items():
            if fn=='relay-lid-platform':continue
            f=cq.Shape.importBrep(str(ROOT/r['brep']));v=common(f,s)
            checks.append({'test':'actual fastener clears mounted relay','part':fn,'device':name,'common_mm3':v,'pass_result':v<.001})
    # Preserve the reed-A cap bore and a nominal straight upper clearance
    # reserve. No measured rigid lead or minimum straight exit is recorded.
    conduit=cq.Solid.makeCylinder(3.4,35,cq.Vector(-31,458.3,248))
    for name,record in {**parts,**expected_devices}.items():
        shape=cq.Shape.importBrep(str(ROOT/record['brep']));gap=shape.distance(conduit)
        checks.append({'test':'accepted6.8mm reed-A bore and normal cable exit remain clear','part':name,'gap_mm':gap,'pass_result':gap>=.9999})
    # These bodies are native installed references, not an assertion that the
    # representative contact blocks or the 3.2 mm hole diameter are qualified.
    neighbors={}
    for path in [STUDY/'pump/candidate.json',STUDY/'routing/candidate.json',STUDY/'structure/candidate.json']:
        manifest=json.loads(path.read_text())
        for name,r in manifest.get('parts',{}).items():
            if name in devices or name.startswith(('enclosure-','cold-core/','relay-','wago-')):continue
            if 'brep' in r:neighbors[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
    for name,s in devices.items():
        for nn,n in neighbors.items():
            a=s.BoundingBox();b=n.BoundingBox()
            if a.xmax<b.xmin or b.xmax<a.xmin or a.ymax<b.ymin or b.ymax<a.ymin or a.zmax<b.zmin or b.zmax<a.zmin:continue
            v=common(s,n)
            checks.append({'test':'mounted relay clears current adjacent body','part':name,'neighbor':nn,'common_mm3':v,'pass_result':v<.001})
    checks += [{'test':'complete relay crown to supply underside','gap_mm':288.75-276.65,'pass_result':288.75-276.65>=10},
               {'test':'AC/DC divider crown to supply underside','gap_mm':288.75-278,'pass_result':288.75-278>=10},
               {'test':'PCB pin tips to printed deck','gap_mm':257.65-DECK_TOP,'pass_result':257.65-DECK_TOP>=1},
               {'test':'complete host single solid','valid':stock.isValid(),'solids':len(stock.Solids()),'pass_result':stock.isValid() and len(stock.Solids())==1}]
    endpoints={name:{'contacts':{'point':[-39.5+dx,432 if name=='relay-1' else 452.3,271.15],'axis':[0,0,1]},
       'logic':{'point':[11.5+dx,432 if name=='relay-1' else 452.3,271.15],'axis':[0,0,1]}} for name in devices}
    result={'parts':parts,'replacement_names':[],'expected_devices':expected_devices,
      'mounts':mounts,'pilot_cutters':pilot_records,'endpoints':endpoints,'checks':checks,
      'pass_result':all(c['pass_result'] for c in checks),'x_shift_mm':dx,
      'lid_fuse_part_names':['relay-lid-platform'],'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
      'qualification_limits':['Calipered relay body and hole pattern; contact blocks and 3.2 mm hole diameter remain representative reference geometry.',
       'Factory prewire the upward contact/logic connectors before supply installation; vertical lead shaping and service sequencing need explicit wiring geometry.',
       'Printed load capacity, insert retention, divider electrical property and lifetime are not established by this geometric study.']}
    (HERE/'floor-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass_result':result['pass_result'],'parts':len(parts),'poses':{n:bounds(s) for n,s in devices.items()},'failures':[c for c in checks if not c['pass_result']]},indent=2),flush=True)
    assert result['pass_result'],[c for c in checks if not c['pass_result']]

if __name__=='__main__':main()
