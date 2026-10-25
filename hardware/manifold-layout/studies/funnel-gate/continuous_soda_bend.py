"""Continuous soda inlet tube, accepted R14 holder and stock foam over the turn.

This selected arrangement keeps the meter and main component poses fixed. Its foam
display is available occupied space after local compression, not a cutting
template or an elastic material prediction. Production placement is separate.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import re
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARTS=HERE/'parts'
SOURCE=ROOT/'future/tube-bend-holder-exploration'
ACCEPTANCE=SOURCE/'prints/2026-10-23-legs-123-w2-petgf-left04-z018-mark1/physical-result.json'
N=np.array([0.,1.,0.]);U=np.array([0.,0.,1.])
IDENTITY=np.eye(3).tolist()
NAMES=('soda-continuous-inlet','soda-bend-holder','soda-continuous-insulation')
REMOVED={'soda-inlet-stem','soda-core-rise','soda-rise-insulation'}


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def plan():
    soda=module('continuous_soda_route',HERE/'soda_route.py').route()
    accepted=json.loads(ACCEPTANCE.read_text())['selected_candidate']
    port=np.array(soda['meter_inlet_mm']);radius=accepted['centreline_bend_r_mm']
    leg=accepted['leg_mm'];gap=1.
    end=port-(leg+gap)*N;center=end-radius*U;start=center-radius*N
    guide=np.array([start[0],start[1],soda['upstream_handoff']['core_carb_water_out_mm'][2]])
    rotation=np.column_stack([-N,U,np.cross(-N,U)])
    zc=accepted['wall_mm']+accepted['channel_d_mm']/2
    shift=center-rotation@[0.,0.,zc]
    arc=[center-radius*math.cos(t)*N+radius*math.sin(t)*U for t in np.linspace(0,math.pi/2,81)]
    tube_points=[guide-12*U,guide,*arc,port,port+soda['metrics']['insertions_mm']['meter_estimate']*N]
    foam_points=[guide+1.1*U,*arc,port-1.*N]
    old=np.array(soda['upstream_handoff']['core_carb_water_out_mm'])
    return {'scope':'Selected insulated inlet; main components and rear outlet path fixed. The passive core guide and its internal continuation require production integration.',
            'selection':{'status':'selected','date':'2026-10-24',
                         'derek':'I am good with this insulation, this is what I want.'},
            'customer_outcome':'One continuous soda tube through an insulated supported turn; one inlet elbow and its extra push-fit connection are absent.',
            'source_holder':str((SOURCE/'tube_bend_holder.py').relative_to(ROOT)),
            'physical_acceptance':str(ACCEPTANCE.relative_to(ROOT)),
            'foam_fit_evidence':'hardware/reference/cargen-pipe-insulation/elbow-fit-2026-10-24/physical-observation.json',
            'holder':accepted,'meter_mouth_mm':port.tolist(),'meter_insertion_mm':soda['metrics']['insertions_mm']['meter_estimate'],
            'holder_to_meter_mm':gap,'bend_center_mm':center.tolist(),'arc_start_mm':start.tolist(),
            'arc_end_mm':end.tolist(),'core_guide_mm':guide.tolist(),'core_guide_shift_mm':(guide-old).tolist(),
            'holder_rotation':rotation.tolist(),'holder_translation_mm':shift.tolist(),
            'tube_points_mm':np.array(tube_points).tolist(),'foam_points_mm':np.array(foam_points).tolist(),
            'tube_od_mm':6.35,'tube_id_mm':4.24,'nominal_foam_od_mm':25.4,
            'nominal_foam_cut_length_mm':float(start[2]-guide[2]-1.1+math.pi*radius/2+leg+gap-1.),
            'foam_installation':'One approximately 63 mm square-cut length of the owned sleeve slides over the tube and holder before the meter is connected. The foam wall compresses around the holder and locally against adjacent parts. No shaped foam cut or extra mount.',
            'foam_model_scope':'The round stock envelope conforms to the holder internally. The occupied-space display excludes neighboring bodies to illustrate local compression; it does not predict exact strain or thermal performance.'}


def build():
    import cadquery as cq
    p=plan();model=module('continuous_native_bend_holder',SOURCE/'tube_bend_holder.py')
    rotation=np.array(p['holder_rotation'])
    where=cq.Location(cq.Plane(origin=p['holder_translation_mm'],xDir=rotation[:,0].tolist(),normal=rotation[:,2].tolist()))
    holder=model.holder(p['holder']['wall_mm'],p['holder']['leg_mm']).val().moved(where)
    start=np.array(p['arc_start_mm']);end=np.array(p['arc_end_mm']);center=np.array(p['bend_center_mm'])
    mid=center-p['holder']['centreline_bend_r_mm']/math.sqrt(2)*N+p['holder']['centreline_bend_r_mm']/math.sqrt(2)*U
    def swept(first,last,outer,inner):
        vec=lambda x:cq.Vector(*map(float,x))
        wire=cq.Wire.assembleEdges([cq.Edge.makeLine(vec(first),vec(start)),
             cq.Edge.makeThreePointArc(vec(start),vec(mid),vec(end)),cq.Edge.makeLine(vec(end),vec(last))])
        face=cq.Workplane(cq.Plane(origin=first.tolist(),xDir=(1,0,0),normal=(0,0,1))).circle(outer).circle(inner)
        return face.sweep(cq.Workplane().newObject([wire]),isFrenet=True).val()
    guide=np.array(p['core_guide_mm']);port=np.array(p['meter_mouth_mm'])
    tube=swept(guide-12*U,port+p['meter_insertion_mm']*N,3.175,2.12)
    foam=swept(guide+1.1*U,port-1.*N,12.7,3.175).cut(holder).clean()
    shapes={NAMES[0]:tube,NAMES[1]:holder,'soda-bend-foam-stock':foam}
    rows={};PARTS.mkdir(exist_ok=True)
    for name,shape in shapes.items():
        cq.exporters.export(shape,str(PARTS/(name+'.step')))
        v,f=shape.tessellate(.035,.1);v=np.array([q.toTuple() for q in v],np.float32);f=np.array(f,np.int32)
        np.savez_compressed(PARTS/(name+'.npz'),v=v,f=f)
        rows[name]={'valid':shape.isValid(),'solids':len(shape.Solids()),'volume_mm3':shape.Volume(),
                    'bounds_mm':[v.min(0).tolist(),v.max(0).tolist()]}
    p['native_assets']=rows
    p['source_sha256']={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest()
        for x in (SOURCE/'tube_bend_holder.py',ACCEPTANCE,ROOT/p['foam_fit_evidence'])}
    (HERE/'continuous-soda-bend.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps({'native_assets':rows,'guide_shift_mm':p['core_guide_shift_mm']}),flush=True)


def mesh(name):
    with np.load(PARTS/(name+'.npz')) as d:return d['v'],d['f']


def assess():
    import fcl
    import trimesh
    study=module('continuous_soda_fit_study',HERE/'study.py')
    g=study.library();scene=study.pose(g);world=study.base.world_meshes(scene,g)
    world={n:m for n,m in world.items() if n not in REMOVED}
    def obj(m):
        v,f=m;b=fcl.BVHModel();b.beginModel(len(v),len(f));b.addSubModel(v,f.astype(np.int32));b.endModel()
        return fcl.CollisionObject(b)
    objects={n:obj(m) for n,m in world.items()};rows={}
    for name in (NAMES[0],NAMES[1],'soda-bend-foam-stock'):
        a=obj(mesh(name));gaps={};hits=[]
        for n,b in objects.items():
            if name==NAMES[0] and n=='digiten-flow':continue
            gaps[n]=float(fcl.distance(a,b,fcl.DistanceRequest(),fcl.DistanceResult()))
            if fcl.collide(a,b,fcl.CollisionRequest(),fcl.CollisionResult()):hits.append(n)
        rows[name]={'hits':hits,'nearest_mm':sorted(gaps.items(),key=lambda v:v[1])[:10]}
    # A soft occupied-space proxy: existing stock is compressed during assembly,
    # rather than trimmed to match these neighboring reference surfaces.
    foam=trimesh.Trimesh(*mesh('soda-bend-foam-stock'),process=True)
    foam.fix_normals(multibody=True)
    tools=[];tool_solids={}
    for name in rows['soda-bend-foam-stock']['hits']:
        body=trimesh.Trimesh(*world[name],process=True);body.fix_normals(multibody=True)
        pieces=body.split(only_watertight=True,repair=False)
        if not pieces:raise ValueError('No closed occupied body for '+name)
        tools.extend(pieces);tool_solids[name]=len(pieces)
    fitted=trimesh.boolean.difference([foam,*tools],engine='manifold',check_volume=False)
    np.savez_compressed(PARTS/(NAMES[2]+'.npz'),v=np.asarray(fitted.vertices),f=np.asarray(fitted.faces,dtype=np.int32))
    p=plan();axis_points=[np.array(p['core_guide_mm'])+z*U for z in np.linspace(1.1,p['arc_start_mm'][2]-p['core_guide_mm'][2],100)]
    radial=[]
    for point in axis_points:
        probe=fcl.CollisionObject(fcl.Sphere(.001),fcl.Transform(point))
        d,n=min((float(fcl.distance(probe,objects[n],fcl.DistanceRequest(),fcl.DistanceResult()))+.001,n)
            for n in rows['soda-bend-foam-stock']['hits'])
        radial.append({'axis_point_mm':point.tolist(),'part':n,'radial_space_mm':d,'foam_between_tube_and_part_mm':d-3.175})
    narrowest=min(radial,key=lambda r:r['radial_space_mm'])
    record={'scope':p['foam_model_scope'],'rigid_parts':{n:rows[n] for n in NAMES[:2]},
            'nominal_stock_soft_contacts':rows['soda-bend-foam-stock']['hits'],
            'soft_contact_tool_solids':tool_solids,
            'nominal_foam_volume_mm3':float(foam.volume),'occupied_foam_volume_mm3':float(fitted.volume),
            'foam_occupied_proxy_watertight':bool(fitted.is_watertight),
            'narrowest_sampled_straight_riser_space':narrowest,
            'rigid_fit_passed':all(not rows[n]['hits'] for n in NAMES[:2]),
            'meter_and_main_component_poses':'Fixed; the core guide moves 11.9548 mm fore, in Y−.',
            'production_limits':'Current printed lid/supports, the internal continuation and complete installed wiring need integration review for the selected inlet.'}
    (HERE/'continuous-soda-bend-review.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2),flush=True)


def viewer(baseline,output):
    study=module('continuous_soda_mesh_packer',HERE/'study.py')
    packer=module('continuous_soda_viewer',HERE/'viewer.py')
    encoded=re.search(r'<script id="qa-data"[^>]*>(.*?)</script>',baseline.read_text(),re.S).group(1)
    data=json.loads(gzip.decompress(base64.b85decode(encoded)));old=copy.deepcopy(data['scene']['instances'])
    data['scene']['instances']=[p for p in data['scene']['instances'] if p['name'] not in REMOVED]
    for part in data['scene']['instances']:part['latest_change']=False
    labels=('Continuous soda tube · one supported R14 bend into the meter',
            'Accepted PET-GF bend holder · 2 mm wall and 3 mm legs · continuous tube inside',
            'Owned foam over the turn · local wall compression · occupied-space estimate')
    for name,label in zip(NAMES,labels):
        part={'name':name,'geometry':name,'rotation':IDENTITY,'translation':[0.,0.,0.],
              'role':'insulation' if name==NAMES[2] else 'support' if name==NAMES[1] else 'wet',
              'kind':'component' if name!=NAMES[0] else 'tube','label':label,'latest_change':True,
              'assembly':{'quadrant':'back-bottom','status':'selected','basis':'The supported continuous tube joins the core-mounted meter; the core guide and internal continuation require production integration.'}}
        if name==NAMES[2]:part['opacity']=.30
        data['scene']['instances'].append(part)
        limits={NAMES[0]:1800,NAMES[1]:2500,NAMES[2]:5000}
        raw=study.base.pack(*mesh(name),limits[name])
        data['geometries'][name]=packer.compact_meshes({'geometries':{name:raw}})['geometries'][name]
    used={p['geometry'] for p in data['scene']['instances']}
    for n in list(used):
        target=data['geometries'][n]
        while target.get('alias'):used.add(target['alias']);target=data['geometries'][target['alias']]
    data['geometries']={n:data['geometries'][n] for n in sorted(used)}
    template=(HERE/'viewer.html').read_text().replace('// INLINE_MOBILE_THEME',(ROOT/'tools/viz/inline-mobile/assets/theme.js').read_text())
    template=template.replace('quadrant-arrangement','continuous-soda-bend')
    template=template.replace('<option value="quadrant" selected>','<option value="quadrant">').replace('<option value="changes">','<option value="changes" selected>')
    template=template.replace('const n=part.name,opacity=','const n=part.name,opacity=part.opacity??(')
    template=template.replace(':1;mesh.userData.displayOpacity',':1);mesh.userData.displayOpacity')
    template=template.replace("function build(){","function build(){\n  pin('R14 holder · continuous tube',[50,346,301]);\n  pin('Foam · local compression',[50,342.4148,280]);")
    template=template.replace("pin('Core soda',[50,354.3696,253.4]);","pin('Core entry · 12 mm fore',[50,342.4148,253.4]);")
    template=re.sub(r'(<div id="qa-stage" role="img" aria-label=")[^"]*(")',
       r'\1Rotatable selected above-core arrangement with one continuous soda inlet tube supported by the accepted R14 printed holder inside the owned foam. The foam is translucent and shows an approximate locally compressed occupied envelope. The meter and every main component retain their poses. The core entry is at X50 Y342.4148. Roof hidden.\2',template)
    packed=base64.b85encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),9,mtime=0)).decode()
    template=template.replace('<!-- ARRANGEMENT_DATA -->','<script id="qa-data" type="application/octet-stream">'+packed+'</script>')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(template)
    displayed={p['name']:p for p in data['scene']['instances']}
    for before in old:
        if before['name'] in REMOVED:continue
        assert {k:v for k,v in before.items() if k!='latest_change'}=={k:v for k,v in displayed[before['name']].items() if k!='latest_change'}
    print(json.dumps({'output':str(output),'bytes':len(template.encode()),'unchanged_parts':len(old)-len(REMOVED),'removed':sorted(REMOVED),'added':NAMES}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build',action='store_true');parser.add_argument('--assess',action='store_true')
    parser.add_argument('--baseline',type=Path);parser.add_argument('--viewer',type=Path)
    args=parser.parse_args()
    if args.build:build()
    if args.assess:assess()
    if args.viewer:
        if not args.baseline:parser.error('--viewer requires the issued --baseline fragment')
        viewer(args.baseline,args.viewer)
