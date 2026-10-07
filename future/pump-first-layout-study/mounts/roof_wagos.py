"""All eight roof junctions with explicit port and lever working space.

Horizontal-entry junctions stand on a 3 mm high floor above the diagonal gas
regulator. The upward-entry 420 occupies the eastern void beside the controller.
Each installed lever is checked with every other junction closed and its entry
wires present. Native occupied geometry is separate from bend and retention
qualification.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts/roof'
sys.path.insert(0,str(STUDY));import baseline
WALL=3.;SLIP=.15

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
def bounds(s):
    b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def place(s,x0,y0,z0):
    b=s.BoundingBox();return s.translate((x0-b.xmin,y0-b.ymin,z0-b.zmin))
def common(a,b):return abs(a.intersect(b,tol=.0001).Volume(tol=1e-9))
def touch(s,t):
    a=s.BoundingBox();b=t.BoundingBox()
    return all(min(x1,y1)-max(x0,y0)>=-.001 for x0,x1,y0,y1 in [(a.xmin,a.xmax,b.xmin,b.xmax),(a.ymin,a.ymax,b.ymin,b.ymax),(a.zmin,a.zmax,b.zmin,b.zmax)])
def emit(name,s,detail,role='structure'):
    p=OUT/f'{name}.brep';s.exportBrep(str(p));v,t=s.tessellate(.12,.08);mesh=OUT/f'{name}.json'
    mesh.write_text(json.dumps({'vertices':[[q.x,q.y,q.z] for q in v],'triangles':[list(q) for q in t]},separators=(',',':'))+'\n')
    return {'brep':str(p.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),
      'bounds':bounds(s),'role':role,'detail':detail,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
      'valid':s.isValid(),'solids':len(s.Solids())}

def working_wire(body,mode,x,y,diameter):
    """Nominal 1.7 mm wire approach with an exact geometric quarter arc.

    WAGO strip length is inside its body. The external approach is an authored
    fit envelope; neither this R3.4 nor the chosen normal reach is qualified.
    """
    b=body.BoundingBox();r=3.4
    if mode=='up':
        a=cq.Vector(x,y,b.zmax);c=a+cq.Vector(0,0,4)
        mid=c+cq.Vector(0,-r+r/(2**.5),r/(2**.5));d=c+cq.Vector(0,-r,r)
        e=d+cq.Vector(0,-4,0);edges=[cq.Edge.makeLine(a,c),cq.Edge.makeThreePointArc(c,mid,d),cq.Edge.makeLine(d,e)]
        profile=cq.Wire.makeCircle(diameter/2,a,cq.Vector(0,0,1))
    elif mode in ['fore','aft']:
        sign=-1 if mode=='fore' else 1
        a=cq.Vector(x,b.ymin if sign<0 else b.ymax,(b.zmin+b.zmax)/2);c=a+cq.Vector(0,sign*2,0)
        mid=c+cq.Vector(0,sign*r/(2**.5),-r+r/(2**.5));d=c+cq.Vector(0,sign*r,-r)
        e=d+cq.Vector(0,0,-.8);edges=[cq.Edge.makeLine(a,c),cq.Edge.makeThreePointArc(c,mid,d),cq.Edge.makeLine(d,e)]
        profile=cq.Wire.makeCircle(diameter/2,a,cq.Vector(0,sign,0))
    else:
        sign=-1 if mode=='west' else 1
        a=cq.Vector(b.xmin if sign<0 else b.xmax,y,(b.zmin+b.zmax)/2);c=a+cq.Vector(sign*2,0,0)
        mid=c+cq.Vector(sign*r/(2**.5),0,-r+r/(2**.5));d=c+cq.Vector(sign*r,0,-r)
        e=d+cq.Vector(0,0,-.8);edges=[cq.Edge.makeLine(a,c),cq.Edge.makeThreePointArc(c,mid,d),cq.Edge.makeLine(d,e)]
        profile=cq.Wire.makeCircle(diameter/2,a,cq.Vector(sign,0,0))
    return cq.Solid.sweep(profile,[],cq.Wire.assembleEdges(edges),makeSolid=True,isFrenet=False)

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--b-x-shift',type=float,default=3.4);parser.add_argument('--high-z-shift',type=float,default=.5);parser.add_argument('--probe-only',action='store_true');args=parser.parse_args()
    if args.probe_only:OUT=OUT.parent/f'probe-reeds-b-x-shift-{args.b_x_shift:g}'
    OUT.mkdir(parents=True,exist_ok=True)
    names=['wago-h','wago-n','wago-g','wago-v12','wago-gnd','wago-reeds-b','wago-reeds-a','wago-sensors']
    old=baseline.read(names);devices={};upward={};modes={}
    poses={'wago-h':(-96.35,334.55,335.75), 'wago-n':(-74.25,334.55,335.75),
      'wago-g':(-52.15,334.55,335.75), 'wago-v12':(-96.35,356.45,335.75),
      'wago-gnd':(-74.25,364.3,335.75), 'wago-reeds-b':(-51.3,364.15,322.6),
      'wago-reeds-a':(-96.35,394.05,335.75), 'wago-sensors':(-63.05,394.05,335.75)}
    bx,by,bz=poses['wago-reeds-b'];poses['wago-reeds-b']=(bx+args.b_x_shift,by,bz)
    for name,(x,y,z) in list(poses.items()):
        if name!='wago-reeds-b':poses[name]=(x,y,z+args.high_z_shift)
    for name,(x,y,z) in poses.items():
        mode='up' if name=='wago-reeds-b' else ('aft' if name=='wago-v12' else 'fore')
        modes[name]=mode;upward[name]=mode=='up'
        if mode=='up':s=old[name].rotate((0,0,0),(0,1,0),-90)
        elif name.startswith('wago-reeds') or name=='wago-sensors':
            s=old[name].rotate((0,0,0),(0,0,1),-90).rotate((0,0,0),(0,1,0),90)
            if mode in ['east','west']:s=s.rotate((0,0,0),(0,0,1),90 if mode=='east' else -90)
        else:s=old[name].rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(0,1,0),-90)
        if mode=='aft':s=s.rotate((0,0,0),(0,0,1),180)
        devices[name]=place(s,x,y,z)
    # Full3mm upper stock roots into the west wall. The low420 has a separate
    # roof-rooted pier outside its body, lever and individual wire envelopes.
    high_floor=332.75+args.high_z_shift;high_top=335.75+args.high_z_shift
    stock=box(-99.5,-29.9,331.4,414.6,high_floor,high_top)
    stock=stock.fuse(box(-54.45+args.b_x_shift,-18.35+args.b_x_shift,361,386.9,319.6,322.6),tol=.0001)
    # This full3mm roof-rooted pier stands outside the420's body and wire field.
    stock=stock.fuse(box(-54.45+args.b_x_shift,-51.45+args.b_x_shift,383.9,386.9,319.6,355),tol=.0001)
    mounts=[];pockets=[];lever_shapes={};wire_shapes={};roof_pockets={}
    for name,s in devices.items():
        b=s.BoundingBox();mode=modes[name];up=upward[name];grip=(b.zlen if up else (b.xlen if mode in ['east','west'] else b.ylen))/2
        if mode=='east':tower=box(b.xmin-WALL-SLIP,b.xmin+grip+SLIP,b.ymin-WALL-SLIP,b.ymax+WALL+SLIP,b.zmin-WALL,b.zmax)
        elif mode=='west':tower=box(b.xmin+grip-SLIP,b.xmax+WALL+SLIP,b.ymin-WALL-SLIP,b.ymax+WALL+SLIP,b.zmin-WALL,b.zmax)
        elif mode=='aft':tower=box(b.xmin-WALL-SLIP,b.xmax+WALL+SLIP,b.ymin-WALL-SLIP,b.ymax-grip+SLIP,b.zmin-WALL,b.zmax)
        else:tower=box(b.xmin-WALL-SLIP,b.xmax+WALL+SLIP,b.ymin-WALL-SLIP if up else b.ymin+grip-SLIP,b.ymax+WALL+SLIP,b.zmin-WALL,b.zmin+grip if up else b.zmax)
        stock=stock.fuse(tower,tol=.0001)
        pockets.append(box(b.xmin-SLIP,b.xmax+SLIP,b.ymin-SLIP,b.ymax+SLIP,b.zmin,
          b.zmax+1))
        # Open the full wire/lever half below every horizontal entry so actual
        # descending quarter bends remain clear of the supporting floor.
        if mode=='fore':pockets.append(box(b.xmin,b.xmax,b.ymin-8,b.ymin+grip-SLIP,b.zmin-WALL-.01,b.zmin+.01))
        elif mode=='aft':pockets.append(box(b.xmin,b.xmax,b.ymax-grip+SLIP,b.ymax+8,b.zmin-WALL-.01,b.zmin+.01))
        elif mode=='east':pockets.append(box(b.xmin+grip+SLIP,b.xmax+8,b.ymin,b.ymax,b.zmin-WALL-.01,b.zmin+.01))
        elif mode=='west':pockets.append(box(b.xmin-8,b.xmax-grip-SLIP,b.ymin,b.ymax,b.zmin-WALL-.01,b.zmin+.01))
        if up:pockets.append(box(b.xmin-SLIP,b.xmax+SLIP,b.ymin-7.85,b.ymax+7.85,high_floor,high_top+.01))
        # Levers occupy only the working wire-entry half of each body; their
        # reach is the production measured413 dimension applied as an envelope.
        if up:
            f=box(b.xmin,b.xmax,b.ymin-6.85,b.ymin,b.zmin+grip,b.zmax)
            levers=[f]
            if name=='wago-reeds-b':levers.append(box(b.xmin,b.xmax,b.ymax,b.ymax+6.85,b.zmin+grip,b.zmax))
        elif mode=='east':levers=[box(b.xmin+grip,b.xmax,b.ymin,b.ymax,b.zmax,b.zmax+6.85)]
        elif mode=='west':levers=[box(b.xmin,b.xmin+grip,b.ymin,b.ymax,b.zmax,b.zmax+6.85)]
        elif mode=='aft':levers=[box(b.xmin,b.xmax,b.ymax-grip,b.ymax,b.zmax,b.zmax+6.85)]
        else:levers=[box(b.xmin,b.xmax,b.ymin,b.ymin+grip,b.zmax,b.zmax+6.85)]
        lever_shapes[name]=cq.Compound.makeCompound(levers)
        poles=5 if name.startswith(('wago-reeds','wago-sensors')) else 3
        diameter=1.7 if poles==5 else 3.2
        xs=[b.xmin+b.xlen/poles*(i+.5) for i in range(poles)] if mode not in ['east','west'] else [b.xmax if mode=='east' else b.xmin]
        ys=([b.ymin+b.ylen*.25,b.ymin+b.ylen*.75] if up else ([b.ymin+b.ylen/poles*(i+.5) for i in range(poles)] if mode in ['east','west'] else [(b.ymin+b.ymax)/2]))
        wire_shapes[name]=cq.Compound.makeCompound([working_wire(s,mode,x,y,diameter) for y in ys for x in xs])
        roof_pockets[name]=box(b.xmin if up else b.xmin-1,b.xmax if up else b.xmax+1,b.ymin-5.8 if up else b.ymin-7,
          b.ymax+1,343,350.15 if up else 352)
        axis={'up':[0,0,1],'fore':[0,-1,0],'aft':[0,1,0],'east':[1,0,0],'west':[-1,0,0]}[mode]
        port_points=[[x,y,b.zmax] if up else ([b.xmax if mode=='east' else b.xmin,y,(b.zmin+b.zmax)/2] if mode in ['east','west'] else [x,b.ymax if mode=='aft' else b.ymin,(b.zmin+b.zmax)/2]) for y in ys for x in xs]
        entry={'point':[sum(p[i] for p in port_points)/len(port_points) for i in range(3)],'axis':axis}
        mounts.append({'owner':name,'wire_entry':entry,'lever_axes':[[0,-1,0],[0,1,0]] if name=='wago-reeds-b' else ([[0,-1,0]] if up else [[0,0,1]]),
          'well_wall_mm':3,'well_floor_mm':3,'per_side_slip_mm':.15,'rear_blank_half_grip_mm':grip,
          'external_straight_wire_approach_mm':4 if up else 2,'geometric_wire_bend_radius_mm':3.4,
          'occupied_wire_diameter_mm':diameter,'reserved_port_points':port_points,
          'port_point_scope':'Uniform source groove pitch; nominal terminal-face reservation, not measured metal-clamp locations.',
          'retention':'Full 3 mm well around the blank rear half; the complete working wire-entry half is open.'})
    pockets.append(box(-99.51,-29.9,331.4,343.7,high_floor-.01,high_top+.01))
    for p in pockets:stock=stock.cut(p,tol=.0001)
    stock=stock.clean()
    parts={'west-junction-platform':emit('west-junction-platform',stock,'One3mm west/roof-rooted host: four FORE-entry and one AFT-entry mains above the complete diagonal gas regulator, one UP-entry420 in the east native void, and FORE-entry reedsA/sensors. Entry-floor windows preserve actual wire quarter turns.')}
    expected={name:emit(f'expected-{name}',s,'Exact rotated retained WAGO envelope including closed-lever grooves; working face is fully open.','electronics') for name,s in devices.items()}
    working={name:{'levers':emit(f'lever-envelope-{name}',lever_shapes[name],'Measured6.85 mm lever reach; full working half is explicit.','motion'),
       'entry_wire':emit(f'entry-wire-{name}',wire_shapes[name],'All ports explicitly reserved:1.7 mm signal wires or conservative3.2 mm main-wire drafting envelopes; normal approach4/2 mm and R3.4 quarter arcs remain unqualified.','wiring'),
       'roof_cutter':emit(f'roof-pocket-{name}',roof_pockets[name],'Localized ceiling relief preserves at least3 mm exterior stock.')} for name in devices}
    checks=[]
    for name,s in devices.items():
        v=common(stock,s);checks.append({'test':'native host clears closed connector','part':name,'common_mm3':v,'pass_result':v<.001})
    neighbors={}
    for folder in ['funnel','pump','routing','structure']:
        manifest=json.loads((STUDY/folder/'candidate.json').read_text())
        for name,r in manifest.get('parts',{}).items():
            if name in devices or name.startswith(('relay-','enclosure-','cold-core/')):continue
            if 'brep' in r:neighbors[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
    neighbors.update(devices)
    # Exact native body/host/hose collisions, plus every individual lever with
    # all other bodies closed. Simultaneous opened levers are not assumed.
    for name,s in {'west-junction-platform':stock,**devices}.items():
        for nn,n in neighbors.items():
            if nn==name or (name=='west-junction-platform' and nn in devices):continue
            if touch(s,n):
                v=common(s,n);checks.append({'test':'native occupied geometry clears adjacent body','part':name,'neighbor':nn,'common_mm3':v,'pass_result':v<.001})
    for name,lever in lever_shapes.items():
        for nn,n in {'west-junction-platform':stock,**neighbors,**{f'{nn}-entry-wire':w for nn,w in wire_shapes.items() if nn!=name}}.items():
            if name==nn:continue
            if touch(lever,n):
                v=common(lever,n);checks.append({'test':'individual opened lever clears closed installed body','part':name,'neighbor':nn,'common_mm3':v,'pass_result':v<.001})
    for name,wire in wire_shapes.items():
        for nn,n in {'west-junction-platform':stock,**neighbors}.items():
            if name==nn:continue
            if touch(wire,n):
                v=common(wire,n);checks.append({'test':'explicit candidate entry wire clears native body','part':name,'neighbor':nn,'common_mm3':v,'pass_result':v<.001})
    checks.append({'test':'native joined west-rooted host','valid':stock.isValid(),'solids':len(stock.Solids()),'pass_result':stock.isValid() and len(stock.Solids())==1})
    # The low420 floor lies entirely forward of the PSU; high aft stock keeps
    # the manual10mm component-air target wherever its footprint overlaps.
    for name,s in {'west-junction-platform':stock,**devices}.items():
        gap=s.distance(neighbors['psu']);checks.append({'test':'shortest supply component air','part':name,'gap_mm':gap,'pass_result':gap>=9.999})
    result={'parts':parts,'replacement_names':[],'expected_devices':expected,'working_envelopes':working,
      'isolated_reeds_b_x_shift_mm':args.b_x_shift,
      'high_junction_lift_mm':args.high_z_shift,
      'controller_clearances_mm':{name:shape.distance(neighbors['pcba']) for name,shape in {
        'reeds_b_closed_body':devices['wago-reeds-b'],
        'reeds_b_opened_levers':lever_shapes['wago-reeds-b'],
        'reeds_b_entry_wires':wire_shapes['wago-reeds-b'],
        'junction_platform':stock}.items()},
      'mounts':mounts,'checks':checks,'pass_result':all(c['pass_result'] for c in checks),
      'shell_fuse_part_names':['west-junction-platform'],'source_sha256':{str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
      'qualification_limits':['Lever reach envelope is measured on221-413; individual lever operation is screened with other junctions closed.',
      'Normal lead reaches4/2 mm and R3.4 wire turns are explicit geometric candidates, not qualified terminal strain relief or bend radii.',
      'All ten/three/five port reservations use source groove pitch; actual metal clamps and main-wire jacket diameter require their real purchased geometry. Main-wire OD3.2 mm is conservative drafting stock, not a measured wire specification.',
      'Printed capacity, creep, heat, retention and native manufacturing slice remain distinct physical properties.']}
    for name,lever in lever_shapes.items():
        ceiling=350.15 if name=='wago-reeds-b' else 352.
        air=ceiling-lever.BoundingBox().zmax
        checks.append({'test':'opened lever stays below localized roof with full3mm outer skin','part':name,'roof_pocket_end_z_mm':ceiling,'lever_air_mm':air,'pass_result':ceiling<=352.00001 and air>=.4999})
    result['pass_result']=all(c['pass_result'] for c in checks)
    target=HERE/('reeds-b-x-shift-probe.json' if args.probe_only else 'roof-candidate.json')
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass_result':result['pass_result'],'checks':len(checks),'failures':[c for c in checks if not c['pass_result']]},indent=2),flush=True)

if __name__=='__main__':main()
