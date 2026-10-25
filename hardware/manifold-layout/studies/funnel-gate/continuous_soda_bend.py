"""Continuous soda inlet tube, accepted R14 holder and stock foam over the turn.

This selected arrangement keeps the meter and main component poses fixed. Its foam
display is available occupied space after local compression, not a cutting
template or an elastic material prediction. Production stock and wiring reviews
are separate.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import hashlib
import importlib.util
import json
import re
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PARTS=HERE/'parts'
API=ROOT/'hardware/manifold-layout/soda_inlet.py'
U=np.array([0.,0.,1.])
IDENTITY=np.eye(3).tolist()
NAMES=('soda-continuous-inlet','soda-bend-holder','soda-continuous-insulation')
REMOVED={'soda-inlet-stem','soda-core-rise','soda-rise-insulation'}


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def production():
    path=str(API.parent)
    if path not in sys.path:sys.path.insert(0,path)
    name='funnel_gate_production_soda_inlet'
    return sys.modules.get(name) or module(name,API)


def plan():
    """Read the shared production plan; retain no independent inlet dimensions."""
    model=production()
    return {**model.plan(),
            'scope':'Selected production inlet shown in the isolated above-core study. Printed supports, internal continuation and installed wiring have separate production reviews.',
            'source_model':str(API.relative_to(ROOT)),
            'tube_points_mm':model.tube_spec()['points_mm']}


def build():
    import cadquery as cq
    p=plan();model=production()
    import above_core_parts
    native=above_core_parts.components()
    neighbors={name:native[name][0] for name in model.SOFT_NEIGHBORS}
    shapes={NAMES[0]:model.tube(),NAMES[1]:model.holder(),
            'soda-bend-foam-stock':model.foam_stock(),
            NAMES[2]:model.foam_occupied(neighbors)}
    rows={};PARTS.mkdir(exist_ok=True)
    for name,shape in shapes.items():
        cq.exporters.export(shape,str(PARTS/(name+'.step')))
        v,f=shape.tessellate(.035,.1);v=np.array([q.toTuple() for q in v],np.float32);f=np.array(f,np.int32)
        np.savez_compressed(PARTS/(name+'.npz'),v=v,f=f)
        rows[name]={'valid':shape.isValid(),'solids':len(shape.Solids()),'volume_mm3':shape.Volume(),
                    'bounds_mm':[v.min(0).tolist(),v.max(0).tolist()]}
    p['native_assets']=rows
    sources=(API,API.with_name('above-core.json'),API.with_name('above_core_parts.py'),
             ROOT/p['physical_acceptance'],ROOT/p['foam_fit_evidence'])
    p['source_sha256']={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
    (HERE/'continuous-soda-bend.json').write_text(json.dumps(p,indent=2)+'\n')
    print(json.dumps({'native_assets':rows,'core_guide_mm':p['core_guide_mm']}),flush=True)


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
    # The production native API supplies both stock and occupied foam. This
    # query measures those exports; it does not construct another foam model.
    foam=trimesh.Trimesh(*mesh('soda-bend-foam-stock'),process=True)
    foam.fix_normals(multibody=True)
    fitted=trimesh.Trimesh(*mesh(NAMES[2]),process=True)
    fitted.fix_normals(multibody=True)
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
            'occupied_foam_source':str(API.relative_to(ROOT))+':foam_occupied',
            'accepted_soft_neighbors':p['accepted_soft_neighbors'],
            'nominal_foam_volume_mm3':float(foam.volume),'occupied_foam_volume_mm3':float(fitted.volume),
            'foam_occupied_proxy_watertight':bool(fitted.is_watertight),
            'narrowest_sampled_straight_riser_space':narrowest,
            'rigid_fit_passed':all(not rows[n]['hits'] for n in NAMES[:2]),
            'meter_and_main_component_poses':'Fixed; shared production guide is at X50/Y342.4148/Z253.4.',
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
