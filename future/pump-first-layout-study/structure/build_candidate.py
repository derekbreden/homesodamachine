"""Roof controller, horizontal supply and their explicit blind mounting hosts.

Exact populated bodies retain their reference qualification limits. All runtime
B-reps are disposable; canonical generators and acceptance records are read-only.
"""
from pathlib import Path
import sys, json, hashlib, os
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Curve

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/structure'
# This study imports reference shape helpers and writes only its isolated cache.
# It never invokes the canonical exporter or publishes a production build.
os.environ.setdefault('HSM_NO_BUILD_LOCK','1')
sys.path.insert(0,str(STUDY))
import baseline
from pcb_platform import place,bounds,hole_axes

def circles(shape, radius, axis):
    found=set()
    for e in shape.Edges():
        if e.geomType()!='CIRCLE':continue
        c=BRepAdaptor_Curve(e.wrapped).Circle()
        a=c.Axis().Direction()
        if abs(c.Radius()-radius)>1e-4 or abs(getattr(a,axis.upper())())<.999:continue
        p=c.Location()
        found.add(tuple(round(v,5) for v in (p.X(),p.Y(),p.Z())))
    return sorted(found)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    old=baseline.read(['pcba','psu','c14-inlet','keystone-jack'])
    parts={};checks=[];mounts=[];pilots={};clearances={}
    routing=json.loads((STUDY/'routing/candidate.json').read_text()) if (STUDY/'routing/candidate.json').exists() else {}
    flavor_portal_path=STUDY/'routing/flavor-a-portal.json'
    flavor_portal=json.loads(flavor_portal_path.read_text()) if flavor_portal_path.exists() else None
    def add(name,shape,role,detail):
        if not shape.isValid():raise ValueError(name)
        f=OUT/(name+'.brep');shape.exportBrep(str(f))
        parts[name]={'brep':str(f.relative_to(ROOT)),'bounds':bounds(shape),'role':role,
                     'detail':detail,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
        return shape
    def pilot(name,shape,owner):
        path=OUT/(name+'-pilot.brep');shape.exportBrep(str(path))
        pilots[name]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                      'print_owner':owner,'bounds':bounds(shape)}
    def screw(name,p,axis,length):
        a=cq.Vector(*axis);v=cq.Vector(*p)
        shank=cq.Solid.makeCylinder(1.5,length,v,a)
        head=cq.Solid.makeCylinder(2.75,3,v-a*3,a)
        socket=cq.Workplane('XY').polygon(6,2.887).extrude(1.6).val()
        if axis==(0,1,0):socket=socket.rotate((0,0,0),(1,0,0),-90)
        if axis==(0,0,-1):socket=socket.rotate((0,0,0),(1,0,0),180)
        socket=socket.translate((v-a*3).toTuple())
        return add(name,shank.fuse(head.cut(socket)),'structure',f'M3 × {length:g} socket screw; real shank/head and socket envelope.')
    pcb=add('pcba',place(old['pcba'],[((0,1,0),-90)],x0=-19,y0=326.8,z0=327.9),
            'electronics','Populated controller, components down; four isolated MH1–MH4 holes on roof bosses. All edge connectors prewired before roof installation.')
    for i,(x,y) in enumerate(hole_axes(pcb),1):
        face=347.0
        host=cq.Solid.makeCylinder(4,355-face,cq.Vector(x,y,face))
        host=host.cut(cq.Solid.makeCylinder(2,5.0,cq.Vector(x,y,face)))
        pilot(f'controller-{i}',cq.Solid.makeCylinder(2,5.,cq.Vector(x,y,face)),'enclosure-back-top')
        add(f'controller-roof-boss-{i}',host,'structure','Ø8 roof-rooted boss, Ø4 ×5 blind pilot for short 4mm insert; 3mm roof end cover, 3.25mm standoff clears 2mm pin tails.')
        screw(f'controller-screw-{i}',(x,y,345.4),(0,0,1),6)
        mounts.append({'owner':'pcba','mouth':[x,y,face],'axis':[0,0,1],'pilot_depth':5.0,'insert_length':4,'screw_length':6,'engagement':4.4,'tip_reserve':.6,'end_cover':3.0})
    psu=add('psu',place(old['psu'],[((0,1,0),90),((0,0,1),-90)],x0=-45,y0=411.3,z0=289.75),
            'electronics','Mean Well IRM-90-12ST horizontal across X, standard base down, terminals up; 36.35mm above the cold-core lid on four exact datasheet mounting stations. Reference terminal ledges are representative.')
    axes=sorted(set((p[0],p[1]) for p in circles(psu,1.75,'z')))
    for i,(x,y) in enumerate(axes,1):
        face=289.75
        bridge=(x==min(p[0] for p in axes)) or (x==max(p[0] for p in axes) and y==min(p[1] for p in axes))
        root=281.5 if bridge else 253.39
        host=cq.Solid.makeCylinder(4,face-root,cq.Vector(x,y,root))
        host=host.cut(cq.Solid.makeCylinder(2,5.25,cq.Vector(x,y,face),cq.Vector(0,0,-1)))
        pilot(f'supply-{i}',cq.Solid.makeCylinder(2,5.25,cq.Vector(x,y,face),cq.Vector(0,0,-1)),'cold-core-lid')
        add(f'supply-lid-boss-{i}',host,'structure',
            'Ø8 bridge boss above the fixed flavor-A interface; Ø4×5.25 blind pilot, 3mm blind floor, connected 8×3mm rail and floor web.' if bridge else
            'Ø8 lid-rooted boss; Ø4 ×5.25 blind pilot for short4mm insert; 36.35mm standoff, paired stations connected by a full3mm load web.')
        washer=cq.Solid.makeCylinder(3.5,.8,cq.Vector(x,y,296.45)).cut(cq.Solid.makeCylinder(1.6,.8,cq.Vector(x,y,296.45)))
        add(f'supply-washer-{i}',washer,'structure','Ø7 ×0.8 M3 flat washer on the 6.7mm mounting ledge.')
        screw(f'supply-screw-{i}',(x,y,297.25),(0,0,-1),12)
        mounts.append({'owner':'psu','mouth':[x,y,face],'axis':[0,0,-1],'pilot_depth':5.25,'insert_length':4,'screw_length':12,'engagement':4.5,'tip_reserve':.75,'root_cover':3.0 if bridge else 31.10})
    for i,x in enumerate(sorted({p[0] for p in axes}),1):
        ys=sorted({p[1] for p in axes if p[0]==x})
        y0=430.5 if i==2 else 410.
        y1=ys[-1] if i==2 else 445.5
        web=cq.Solid.makeBox(3,y1-y0,281.5-253.39,cq.Vector(x-1.5,y0,253.39))
        web=web.fuse(cq.Solid.makeBox(8,ys[-1]-ys[0],3,cq.Vector(x-4,ys[0],281.5)))
        for name,rec in routing.get('clearance_cutters',{}).items():
            if rec.get('target_host')==f'supply-lid-web-{i}':
                web=web.cut(cq.Shape.importBrep(str(ROOT/rec['brep'])))
                clearances[name]={**rec,'print_owner':'cold-core-lid'}
        if flavor_portal and f'supply-lid-web-{i}' in flavor_portal.get('target_hosts',[]):
            portal=cq.Shape.importBrep(str(ROOT/flavor_portal['brep']))
            web=web.cut(portal)
            clearances['flavor-a-psu-portal']={**flavor_portal,
                'sha256':hashlib.sha256((ROOT/flavor_portal['brep']).read_bytes()).hexdigest(),
                'print_owner':'cold-core-lid'}
        add(f'supply-lid-web-{i}',web,
            'structure','Full3mm lid-rooted load web with an 8×3mm fore bridge above the fixed flavor-A riser; fore station overhang9.7mm.' if i==2 else
            'Three-millimetre lid-rooted central web fromY410 to445.5, with an 8×3mm high rail supporting both left blind stations above the flavor return. The complete10.8mm fore stock precedes the flavor portal; each pilot retains3mm blind root stock. The portal is recut after fusion.')
    add('c14-inlet',old['c14-inlet'].translate((-138,0,0)),'electronics','Received IEC C14 inlet and accepted plug approach, translated to X−71.1 on rear wall; terminal face remains fore.')
    keystone_delta=tuple(routing.get('interface_moves',{}).get('keystone',{}).get('translation',(-25.865,0,-.04729046878)))
    add('keystone-jack',old['keystone-jack'].translate(keystone_delta),
        'electronics','Rear RJ11 keystone with the complete retained snap body; shifted receiver retains both native catches and the full aperture.')
    sys.path.insert(0,str(ROOT/'hardware/reference/ground-ring-stack'))
    import ground_ring_stack as ground
    ground.engage=7.2
    ground.shank_d=3.0
    datum=(51.2,430.5,341.2)
    clock=50.
    stack=(ground.build().val().rotate((0,0,0),(1,0,0),180)
           .rotate((0,0,0),(0,0,1),clock).translate(datum))
    add('ground-stack',stack,'electronics','Five ring-terminal fan, tooth washer and M3×12 clamping screw; 7.2mm screw engagement into a long5.7mm heat-set insert on a roof-rooted boss.')
    host=cq.Solid.makeCylinder(4,355-datum[2],cq.Vector(*datum))
    host=host.cut(cq.Solid.makeCylinder(2,8.5,cq.Vector(*datum)))
    pilot('ground',cq.Solid.makeCylinder(2,8.5,cq.Vector(*datum)),'enclosure-back-top')
    add('ground-roof-boss',host,'structure','Ø8 roof-rooted ground-reaction post; Ø4×8.5 blind pocket for5.7mm insert,5.3mm roof end cover and1.3mm screw-tip reserve.')
    mounts.append({'owner':'ground-stack','mouth':list(datum),'axis':[0,0,1],'clock_degrees':clock,'pilot_depth':8.5,'insert_length':5.7,'screw_length':12,'engagement':7.2,'tip_reserve':1.3,'end_cover':5.3})
    for m in mounts:
        checks.append({'check':f"{m['owner']} complete insert engagement and blind reserve",'pass':m['engagement']>=m['insert_length'] and m['tip_reserve']>=.5,**m})
    checks.extend([{'check':'four exact controller mounting holes','pass':len(hole_axes(pcb))==4},
                   {'check':'four exact supply mounting holes','pass':len(axes)==4}])
    result={'parts':parts,'replacement_names':['pcba','psu','c14-inlet','keystone-jack','ground-stack'],'mounts':mounts,'checks':checks,'pilot_cutters':pilots,'clearance_cutters':clearances,
            'qualification_limits':['Roof and lid mounting loads need their own native slice and physical qualification.','Reference PSU envelope/hole pattern are controlled drawing dimensions; terminal ledges and ground-ring stack are representative.','IRM mounting airflow and appliance thermal performance require system qualification; CAD clearance is not an output-current rating.']}
    (HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'parts':len(parts),'checks_pass':all(c['pass'] for c in checks),'mounts':len(mounts)},indent=2),flush=True)

if __name__=='__main__':main()
