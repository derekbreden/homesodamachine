"""Shared purchased checks and selected local fittings in the clean study.

Check geometry comes from the single canonical STEP. Ports and insertion come
from its stdlib API. Selected production poses and curves are frozen with the
native export so later implementation edits cannot rearrange this study.
The water outlet retains the approved downward direction. Native display assets
and their selected placement are refreshed explicitly through the CAD queue.
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
HW=ROOT/'hardware'
REF=HW/'reference/neofit-achv44-check'
NAME='neofit-achv44-check'
GAS_NAMES=('gas-regulator','gas-check','gas-inlet-elbow','gas-lower-a',
           'gas-lower-b','gas-upper-a','gas-upper-b')
PISCO_STEMS=('gas-inlet-elbow','gas-lower-a')
DOWN_ROTATION=np.array([[0.,0.,-1.],[1.,0.,0.],[0.,-1.,0.]])
IDENTITY=np.eye(3).tolist()


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result
    spec.loader.exec_module(result)
    return result


def reference():
    return module('funnel_gate_shared_check',REF/'neofit_achv44_check.py')


def selected():
    record=json.loads((HERE/'purchased-checks-native.json').read_text())
    return {'parts':{'discharge-chain':record['water_frame']},
            'snapshots':{**record['gas_frames'],'carbonator-fold':
                         {'exposed_stem_mm':record['water']['exposed_stem_mm']}},
            'gas_datums':record['gas_datums'],'cap_face_z_mm':record['cap_face_z_mm']}


def elbow_interfaces():
    return json.loads((HW/'reference/neofit-stem-elbow/model-check.json').read_text())


def world(frame,point):
    return np.array(frame['rotation'])@np.array(point)+np.array(frame['translation_mm'])


def water_datums(spec=None):
    ref=reference();spec=selected() if spec is None else spec;frame=spec['parts']['discharge-chain']
    inlet=world(frame,ref.inlet()[0]);outlet=world(frame,ref.outlet()[0])
    outward=np.array(frame['rotation'])@np.array(ref.outlet()[1])
    exposed=spec['snapshots']['carbonator-fold'].get('exposed_stem_mm',0.)
    shoulder=np.array(elbow_interfaces()['stem_shoulder'][0])
    turn=outlet+exposed*outward-DOWN_ROTATION@shoulder
    socket=turn+DOWN_ROTATION@np.array(elbow_interfaces()['socket'][0])
    guide=np.array([socket[0],socket[1],spec['cap_face_z_mm']])
    return {'inlet':inlet.tolist(),'outlet':outlet.tolist(),'turn':turn.tolist(),
            'socket':socket.tolist(),'guide':guide.tolist(),
            'rotation':DOWN_ROTATION.tolist(),'exposed_stem_mm':exposed,
            'insertion_mm':ref.socket_depth('outlet'),
            'guide_scope':'Down-facing outlet directly above an aft passive core guide; the internal continuation to the fixed carbonator port is production integration work.'}


def stem_depth(name,spec=None):
    spec=selected() if spec is None else spec;exposed=spec['snapshots'][name].get('exposed_stem_mm',0.)
    if name in PISCO_STEMS:
        dims=json.loads((HW/'reference/compact-inline-candidates/dimensions.json').read_text())
        port='inlet' if name=='gas-inlet-elbow' else 'outlet'
        return dims['pisco_rvfup_quarter']['ports'][port]['insertion_mm']+exposed
    return reference().socket_depth()+exposed


def geometry_for(name):
    return 'purchased-check-stem-pisco' if name in PISCO_STEMS else 'purchased-check-stem-neofit'


def freeze():
    import cadquery as cq
    placement=HW/'manifold-layout/above-core.json'
    spec=json.loads(placement.read_text()) if placement.exists() else selected()
    stem=cq.importers.importStep(str(HW/'reference/neofit-stem-elbow/neofit-stem-elbow.step')).val()
    def trimmed(depth):
        tip=float(elbow_interfaces()['stem_shoulder'][0][0])-depth
        cut=cq.Solid.makeBox(100.+tip,100.,100.,cq.Vector(-100.,-50.,-50.))
        return stem.cut(cut)
    shapes={NAME:cq.importers.importStep(str(REF/(NAME+'.step'))).val(),
            'purchased-check-stem-pisco':trimmed(stem_depth('gas-lower-a',spec)),
            'purchased-check-stem-neofit':trimmed(stem_depth('gas-upper-a',spec))}
    # One plain upper-U pocket in the ideal 9 mm study ceiling.
    upper=[]
    for name in ('gas-upper-a','gas-upper-b'):
        frame=spec['snapshots'][name];rotation=np.array(frame['rotation'])
        where=cq.Location(cq.Plane(origin=frame['translation_mm'],
                                  xDir=rotation[:,0].tolist(),normal=rotation[:,2].tolist()))
        placed=shapes[geometry_for(name)].moved(where)
        upper.append(placed.BoundingBox())
    x0=min(b.xmin for b in upper)-1.;x1=max(b.xmax for b in upper)+1.
    y0=min(b.ymin for b in upper)-1.;y1=max(b.ymax for b in upper)+1.
    top=max(b.zmax for b in upper)
    ceiling=cq.importers.importStep(str(PARTS/'expanded-funnel-ceiling.step')).val()
    bounds=ceiling.BoundingBox();roof=math.ceil((top+1.)*10.)/10.
    pocket=cq.Solid.makeBox(x1-x0,y1-y0,roof-bounds.zmin+1.,cq.Vector(x0,y0,bounds.zmin-1.))
    shapes['purchased-checks-ceiling']=ceiling.cut(pocket).clean()
    cq.exporters.export(shapes['purchased-checks-ceiling'],str(PARTS/'purchased-checks-ceiling.step'))
    rows={}
    for name,shape in shapes.items():
        v,f=shape.tessellate(.04,.12)
        v=np.array([p.toTuple() for p in v],np.float32);f=np.array(f,np.int32)
        np.savez_compressed(PARTS/(name+'.npz'),v=v,f=f)
        rows[name]={'valid':shape.isValid(),'solid_count':len(shape.Solids()),
                    'bounds_mm':[v.min(0).tolist(),v.max(0).tolist()]}
    sources=[REF/(NAME+'.step'),REF/'neofit_achv44_check.py',
             HW/'reference/neofit-stem-elbow/neofit-stem-elbow.step']
    record={'reference':str((REF/(NAME+'.step')).relative_to(ROOT)),
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'check_ports':reference().ports(),'water':water_datums(spec),
            'water_frame':spec['parts']['discharge-chain'],'cap_face_z_mm':spec['cap_face_z_mm'],
            'gas_datums':spec['gas_datums'],
            'gas_frames':{n:spec['snapshots'][n] for n in GAS_NAMES},
            'stem_cut_lengths_mm':{n:stem_depth(n,spec) for n in (*PISCO_STEMS,'gas-lower-b','gas-upper-a','gas-upper-b','carbonator-fold')},
            'ceiling_pocket':{'bounds_xy_mm':[x0,x1,y0,y1],'roof_z_mm':roof,
                              'air_above_upper_fold_mm':roof-top,
                              'retained_roof_mm':bounds.zmax-roof},
            'display_assets':rows,
            'scope':'Canonical reference STEP and selected native trimmed elbows, with one plain ceiling pocket. Check external dimensions and socket depths retain the family-based layout estimate scope.'}
    (HERE/'purchased-checks-native.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ('gas_datums','source_sha256')},indent=2),flush=True)


def add_library(library,tube):
    for name in (NAME,'purchased-check-stem-pisco','purchased-check-stem-neofit','purchased-checks-ceiling','soda-rise-insulation'):
        with np.load(PARTS/(name+'.npz')) as data:library[name]=data['v'],data['f']
    spec=selected();datums=spec['gas_datums'];water=water_datums()
    library['purchased-gas-inlet-tube']=tube(datums['inlet_route']['points_mm'])
    library['purchased-gas-core-drop']=tube(datums['core_drop_route']['points_mm'])
    depth=reference().socket_depth('inlet');station=np.array(datums['check_in'])
    library['purchased-gas-check-link']=tube([station-depth*np.array([0.,0.,1.]),station+depth*np.array([0.,0.,1.])])
    socket=np.array(water['socket']);guide=np.array(water['guide'])
    library['purchased-check-core-drop']=tube([guide-[0.,0.,12.],guide,socket,socket+[0.,0.,water['insertion_mm']]])
    inlet=np.array(water['inlet'])
    # The printed pump elbow has a 15 mm tube socket (TUBE_DEPTH in its native source).
    library['pump-check-link']=tube([inlet-[0.,15.,0.],inlet+[0.,depth,0.]])


def apply(scene):
    scene=copy.deepcopy(scene);spec=selected();water=water_datums()
    for part in scene['instances']:
        name=part['name']
        if name in GAS_NAMES:
            frame=spec['snapshots'][name]
            part.update(rotation=frame['rotation'],translation=frame['translation_mm'])
            if name=='gas-check':
                part.update(geometry=NAME,label='Purchased neoFit ACHV44-E · CO2 check · flow up')
            elif name!='gas-regulator':part['geometry']=geometry_for(name)
        elif name=='check':
            frame=spec['parts']['discharge-chain']
            part.update(geometry=NAME,rotation=frame['rotation'],translation=frame['translation_mm'],
                        label='Purchased neoFit ACHV44-E · pump discharge check · flow aft')
        elif name=='carbonator-fold':
            part.update(geometry=geometry_for(name),rotation=water['rotation'],translation=water['turn'],
                        label='Pump discharge · stem elbow turns DOWN directly toward the cold core')
        elif name=='check-carbonator':
            part.update(geometry='purchased-check-core-drop',rotation=IDENTITY,translation=[0.,0.,0.],
                        label='Pump discharge · short vertical tube to proposed aft core guide')
        elif name in ('gas-inlet-tube','gas-core-drop','gas-check-link'):
            part.update(geometry='purchased-'+name,rotation=IDENTITY,translation=[0.,0.,0.])
        elif name=='ceiling':part['geometry']='purchased-checks-ceiling'
    scene['instances'].extend([
        {'name':'pump-check-link','geometry':'pump-check-link','rotation':IDENTITY,'translation':[0.,0.,0.],
         'role':'wet','kind':'tube','label':'Concealed tube between the pump TPU outlet and purchased check inlet'},
        {'name':'soda-rise-insulation','geometry':'soda-rise-insulation','rotation':IDENTITY,'translation':[0.,0.,0.],
         'role':'insulation','kind':'component','label':'Soda riser · 15 mm square-cut owned foam sleeve'}])
    scene['mates'].extend({'a':a,'b':b,'connection':'Intended seated tube or foam bore contact'} for a,b in
        [('pump-check-link','pump-outlet-tpu'),('pump-check-link','check'),
         ('carbonator-fold','check-carbonator'),('soda-rise-insulation','soda-core-rise')])
    for mate in scene['mates']:
        if {mate['a'],mate['b']}=={'pump-outlet-tpu','check'}:mate['point']=water['inlet']
        elif {mate['a'],mate['b']}=={'check','carbonator-fold'}:
            mate.update(point=water['outlet'],insertion_mm=water['insertion_mm'],shoulder_gap_mm=water['exposed_stem_mm'])
    scene['layout'].update(purchased_checks={'reference':str((REF/(NAME+'.step')).relative_to(ROOT)),
        'ports':reference().ports(),'water':water,'gas_datums':spec['gas_datums'],
        'geometry_scope':reference().specification()['geometry_status']})
    return scene


def viewer(baseline,output):
    """Overlay only the selected checks and their local fittings on an issued view."""
    packer=module('purchased_check_viewer',HERE/'viewer.py')
    encoded=re.search(r'<script id="qa-data"[^>]*>(.*?)</script>',baseline.read_text(),re.S).group(1)
    data=json.loads(gzip.decompress(base64.b85decode(encoded)))
    current=packer.payload()
    selected_names={*GAS_NAMES,'check','carbonator-fold','check-carbonator',
                    'gas-inlet-tube','gas-core-drop','gas-check-link','ceiling','pump-check-link'}
    replacements={p['name']:p for p in current['scene']['instances'] if p['name'] in selected_names}
    originals=copy.deepcopy(data['scene']['instances'])
    for i,part in enumerate(data['scene']['instances']):
        if part['name'] in replacements:
            data['scene']['instances'][i]=copy.deepcopy(replacements.pop(part['name']))
            data['scene']['instances'][i]['latest_change']=True
        else:part['latest_change']=False
    for part in replacements.values():
        part=copy.deepcopy(part);part['latest_change']=True
        data['scene']['instances'].append(part)
    needed={p['geometry'] for p in data['scene']['instances'] if p['name'] in selected_names}
    for name in list(needed):
        target=current['geometries'][name]
        while target.get('alias'):
            needed.add(target['alias']);target=current['geometries'][target['alias']]
    fresh=packer.compact_meshes({'geometries':{n:copy.deepcopy(current['geometries'][n]) for n in needed}})
    data['geometries'].update(fresh['geometries'])
    used={p['geometry'] for p in data['scene']['instances']}
    for name in list(used):
        target=data['geometries'][name]
        while target.get('alias'):
            used.add(target['alias']);target=data['geometries'][target['alias']]
    data['geometries']={n:data['geometries'][n] for n in sorted(used)}
    template=(HERE/'viewer.html').read_text().replace('// INLINE_MOBILE_THEME',
        (ROOT/'tools/viz/inline-mobile/assets/theme.js').read_text())
    template=template.replace('quadrant-arrangement','purchased-checks-arrangement')
    template=template.replace('<option value="quadrant" selected>','<option value="quadrant">')
    template=template.replace('<option value="changes">','<option value="changes" selected>')
    water=water_datums();gas=selected()['snapshots']['gas-check']['translation_mm']
    template=template.replace('function build(){',
        "function build(){\n  pin('Purchased water check',"+json.dumps(water['outlet'])+");\n  pin('Purchased CO2 check',"+json.dumps(gas)+");")
    template=re.sub(r'(<div id="qa-stage" role="img" aria-label=")[^"]*(")',
        r'\1Rotatable clean above-core arrangement with both purchased neoFit ACHV44-E checks. The water check outlet turns directly down toward the cold core. Main components, forward plumbing and the stock foam sleeve retain their displayed positions. Latest changes highlights the checks and their local fittings and tubes. All printed walls are included; the roof is hidden.\2',template)
    packed=base64.b85encode(gzip.compress(json.dumps(data,separators=(',',':')).encode(),9,mtime=0)).decode()
    template=template.replace('<!-- ARRANGEMENT_DATA -->',
        '<script id="qa-data" type="application/octet-stream">'+packed+'</script>')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(template)
    unchanged=[p for p in originals if p['name'] not in selected_names]
    displayed={p['name']:p for p in data['scene']['instances']}
    for old in unchanged:
        assert {k:v for k,v in old.items() if k!='latest_change'}=={k:v for k,v in displayed[old['name']].items() if k!='latest_change'}
    print(json.dumps({'output':str(output),'bytes':len(template.encode()),
        'unchanged_parts':len(unchanged),'displayed_parts':len(displayed),
        'highlighted_parts':[p['name'] for p in displayed.values() if p['latest_change']]}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze',action='store_true')
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--viewer',type=Path)
    args=parser.parse_args()
    if args.freeze:freeze()
    if args.viewer:
        if not args.baseline:parser.error('--viewer requires the issued --baseline fragment')
        viewer(args.baseline,args.viewer)
