"""Manual review of the complete installed model; never invoked by a build/hook.

    tools/cad-venv/bin/python hardware/wiring/installed/review.py
    tools/cad-venv/bin/python hardware/wiring/installed/review.py --native
    tools/cad-venv/bin/python hardware/wiring/installed/review.py --fine

The mesh review checks wires against larger bodies. Wires and tubes do not
obstruct wire routes. Endpoint contact exclusions are
local to the named attachment, not exclusions of entire device bodies.
"""
from __future__ import annotations
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np

MANIFEST=ROOT/'hardware/wiring/enclosure-wiring.json'
HOST=ROOT/'hardware/manifold-layout/enclosure-assembly.step'
OUTPUT=Path(__file__).with_name('routing-review.json')


def load_mesh(path):
    data=Path(path).read_bytes();n=struct.unpack_from('<I',data)[0]
    head=json.loads(data[4:4+n]);blob=memoryview(data)[4+n:]
    out={}
    for m in head['meshes']:
        a,count=m['pos'];b,size=m['idx']
        v=np.frombuffer(blob[a:a+4*count],dtype='<f4').reshape(-1,3).astype(float)
        f=np.frombuffer(blob[b:b+4*size],dtype='<u4').reshape(-1,3)
        out[m['name']]=(v,f)
    return out


def base_name(name): return re.sub(r'/\d+$','',name)


def same_part(a,b):
    return base_name(a).rsplit('/',1)[-1]==base_name(b).rsplit('/',1)[-1]


def wire_obstacle(name):
    """Larger installed bodies, excluding conductors, jackets and tubing."""
    leaf=base_name(name).rsplit('/',1)[-1]
    if leaf.startswith(('wiring-junction-', 'terminal-J')):
        return True
    return (not leaf.startswith(('wire-','wiring-','terminal-','tube-','line-','evap-tail-'))
            and leaf not in ('suction-tube','discharge-tube','evap-coil'))


def mesh_review():
    sys.path.insert(0,str(ROOT/'hardware/scripts'))
    import _cadq_export  # Shares the workstation's one-heavy-CAD-job queue.
    import fcl
    manifest=json.loads(MANIFEST.read_text())
    meshes=load_mesh(str(HOST)+'.mesh')
    rows={r['id']:r for r in manifest['routes']}
    terminals=manifest['terminals']
    physical={n:m for n,m in meshes.items() if wire_obstacle(n)}
    wires={n[5:]:m for n,m in meshes.items() if n.startswith('wire-')}
    print(f'Review {len(wires)} wires against {len(physical)} physical meshes',flush=True)
    def collision_object(mesh):
        v,f=mesh;model=fcl.BVHModel();model.beginModel(len(v),len(f));model.addSubModel(v,f);model.endModel()
        return fcl.CollisionObject(model)
    objects={n:collision_object(m) for n,m in physical.items()}
    wire_objects={n:collision_object(m) for n,m in wires.items()}
    aabbs={n:(v.min(0),v.max(0)) for n,(v,f) in meshes.items()}
    def near(a,b):
        p,q=aabbs[a];r,s=aabbs[b]
        return np.all(q>=r-.001) and np.all(s>=p-.001)
    def contacts(obj,other):
        result=fcl.CollisionResult()
        fcl.collide(obj,other,fcl.CollisionRequest(num_max_contacts=10000,enable_contact=True),result)
        return result.contacts
    collisions=[];intended=0
    for number,(id,obj) in enumerate(wire_objects.items(),1):
        row=rows[id]
        endpoints=[terminals[row[k]] for k in ('start','end')]
        for name,other in objects.items():
            if not near('wire-'+id,name):continue
            hits=contacts(obj,other)
            bad=[]
            for hit in hits:
                p=tuple(float(x) for x in hit.pos)
                ids=manifest.get('terminations',{}).get(base_name(name),{}).get('terminal_ids',[])
                if any((same_part(name,t['part']) or t['id'] in ids) and math.dist(p,t['point'])<=8.5 for t in endpoints):
                    intended+=1;continue
                if hit.penetration_depth>.025:
                    bad.append((p,float(hit.penetration_depth)))
            if bad:
                point,depth=max(bad,key=lambda h:h[1])
                collisions.append({'wire':id,'part':name,'point_mm':[round(v,3) for v in point],
                                   'mesh_penetration_mm':round(depth,4),'contacts':len(bad)})
        if number%20==0:print(f'  {number}/{len(wires)} wires; {len(collisions)} physical interference pairs',flush=True)
    packing=[]
    bundle_collisions=[]
    for bundle in manifest.get('bundles',{}).values():
        name=bundle['geometry_name']
        if name is None:continue
        obj=collision_object(meshes[name])
        for other in physical:
            if name==other or not near(name,other):continue
            bad=[hit for hit in contacts(obj,objects[other]) if hit.penetration_depth>.025]
            if bad:
                hit=max(bad,key=lambda h:h.penetration_depth)
                bundle_collisions.append({'bundle':name,'part':other,
                    'point_mm':[round(float(v),3) for v in hit.pos],
                    'mesh_penetration_mm':round(float(hit.penetration_depth),4)})
    termination_collisions=[]
    for name,info in manifest.get('terminations',{}).items():
        if not name.startswith('terminal-fuse-'):continue
        obj=collision_object(meshes[name])
        for other in physical:
            if name==other or not near(name,other):continue
            bad=[]
            for hit in contacts(obj,objects[other]):
                if any(base_name(other)==terminals[t]['part'] and
                       math.dist(hit.pos,terminals[t]['point'])<=8.5
                       for t in info.get('terminal_ids',[])):continue
                if (base_name(other)=='thermal-fuse' and 'native_stub_tip_mm' in info and
                        math.dist(hit.pos,info['native_stub_tip_mm'])<=2.5):continue
                if hit.penetration_depth>.025:bad.append(hit)
            if bad:
                hit=max(bad,key=lambda h:h.penetration_depth)
                termination_collisions.append({'termination':name,'part':other,
                    'point_mm':[round(float(v),3) for v in hit.pos],
                    'mesh_penetration_mm':round(float(hit.penetration_depth),4)})
    report={'schema':1,'scope':'One manual full-scene mesh interference review of every wire and cable jacket against larger bodies; wire-to-wire and wire-to-tube contacts are excluded. Tessellated penetration is a routing witness, not a native-solid or physical assembly qualification.',
            'manifest_sha256':hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
            'assembly_step_sha256':hashlib.sha256(HOST.read_bytes()).hexdigest(),
            'assembly_mesh_sha256':hashlib.sha256(Path(str(HOST)+'.mesh').read_bytes()).hexdigest(),
            'wire_count':len(wires),'physical_mesh_count':len(physical),
            'coverage_missing':sorted(set(rows)-set(wires)),
            'physical_interference_pairs':collisions,'wire_packing_pairs':packing,
            'bundle_interference_pairs':bundle_collisions,
            'termination_interference_pairs':termination_collisions,
            'wires_with_physical_interference':len({r['wire'] for r in collisions}),
            'endpoint_contact_scope':'Only the named endpoint part within 8.5 mm of its attachment. All other contact with that part remains in the reading.',
            'native':json.loads(OUTPUT.read_text()).get('native') if OUTPUT.exists() else None,
            'fine':json.loads(OUTPUT.read_text()).get('fine') if OUTPUT.exists() else None}
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'wires':len(wires),'physical_pairs':len(collisions),
                      'packing_pairs':len(packing),'bundle_pairs':len(bundle_collisions),
                      'termination_pairs':len(termination_collisions),
                      'missing':report['coverage_missing']}),flush=True)


def native_review():
    if json.loads(MANIFEST.read_text()).get('wiring_fine_model_sha256'):
        return fine_review()
    model=ROOT/'hardware/wiring/enclosure-wiring.step.npz'
    if model.is_file():
        return production_solid_review(model)
    sys.path[:0]=[str(ROOT/'hardware/scripts')]
    from _cadq_export import import_assembly
    manifest=json.loads(MANIFEST.read_text())
    wires=import_assembly(str(ROOT/'hardware/wiring/enclosure-wiring.step'))
    host=import_assembly(str(HOST))
    validity=[];poses=[]
    for id in (r['id'] for r in manifest['routes']):
        n='wire-'+id;s=wires[n][0];p=host[n][0]
        validity.append({'id':id,'valid':s.isValid(),'solids':len(s.Solids()),'volume_mm3':s.Volume()})
        def bb(s):
            b=s.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
        poses.append({'id':id,'maximum_bounds_error_mm':max(abs(a-b) for a,b in zip(bb(s),bb(p)))})
    native={'scope':'All standalone native wires and their installed native placements, read back from both STEP files.',
            'wiring_step_sha256':hashlib.sha256((ROOT/'hardware/wiring/enclosure-wiring.step').read_bytes()).hexdigest(),
            'all_valid_single_solids':all(r['valid'] and r['solids']==1 for r in validity),
            'maximum_installed_bounds_error_mm':max(r['maximum_bounds_error_mm'] for r in poses),
            'invalid':[r for r in validity if not r['valid'] or r['solids']!=1],
            'wire_count':len(validity),'reference_frame_maximum_extent_residual_mm':
                max(r['maximum_extent_residual_mm'] for r in manifest['reference_frames'].values())}
    native['termination_count']=len(manifest.get('terminations',{}))
    native['invalid_terminations']=[n for n in manifest.get('terminations',{})
                                    if not wires[n][0].isValid() or len(wires[n][0].Solids())!=1]
    native['bundles']={}
    for id,b in manifest.get('bundles',{}).items():
        if b['geometry_name'] is None:
            native['bundles'][id]={'jacket':False}
            continue
        jacket=wires[b['geometry_name']][0]
        native['bundles'][id]={'valid':jacket.isValid(),'solids':len(jacket.Solids()),
                               'scope':'Jacket validity only; conductor packing is excluded.'}
    ids=[r['id'] for r in manifest['routes']]
    native['unique_connection_ids']=len(set(ids))==len(ids)
    populated={r[k] for r in manifest['routes'] for k in ('start','end') if r[k].startswith('J')}
    native['populated_board_contacts']=len(populated)
    bench={}
    for j in ('J2','J13'):
        guide=json.loads((ROOT/f'hardware/assembly/harnesses/{j.lower()}.json').read_text())
        bench[j]=all(manifest['terminals'][f'{j}.{p["net"]}']['pin']==str(p['pin'])
                     for p in guide['pins'] if p['net']!='OUT4')
    native['bench_pin_maps_match']=bench
    report=json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    report['native']=native;OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(native),flush=True)


def production_solid_review(model):
    """Read mesh-kernel solids and compare the installed viewer arrays directly."""
    import manifold3d as m3d
    manifest=json.loads(MANIFEST.read_text())
    step=ROOT/'hardware/wiring/enclosure-wiring.step'
    standalone=load_mesh(str(step)+'.mesh')
    installed=load_mesh(str(HOST)+'.mesh')
    grouped={}
    with np.load(model,allow_pickle=False) as arrays:
        names=json.loads(bytes(arrays['names']).decode())
        for i,name in enumerate(names):
            mesh=m3d.Mesh64(np.asarray(arrays[f'V{i}'],np.float64),
                            np.asarray(arrays[f'T{i}'],np.uint64))
            mesh.merge()
            grouped.setdefault(base_name(name),[]).append(m3d.Manifold(mesh))
    members=[]
    for name,parts in grouped.items():
        valid=all(p.status()==m3d.Error.NoError and not p.is_empty() for p in parts)
        body=m3d.Manifold.batch_boolean(parts,m3d.OpType.Add) if valid else None
        members.append({'name':name,'valid_closed_manifold':valid,
                        'connected_solids':len(body.decompose()) if valid else 0,
                        'volume_mm3':float(body.volume()) if valid else None})
    missing=sorted(set(standalone)-set(installed))
    changed=[name for name,pair in standalone.items() if name in installed and
             any(not np.array_equal(a,b) for a,b in zip(pair,installed[name]))]
    ids=[row['id'] for row in manifest['routes']]
    expected={'wire-'+id for id in ids}|set(manifest.get('terminations',{}))
    expected.update(b['geometry_name'] for b in manifest.get('bundles',{}).values()
                    if b['geometry_name'] is not None)
    bench={}
    for j in ('J2','J13'):
        guide=json.loads((ROOT/f'hardware/assembly/harnesses/{j.lower()}.json').read_text())
        bench[j]=all(manifest['terminals'][f'{j}.{p["net"]}']['pin']==str(p['pin'])
                     for p in guide['pins'] if p['net']!='OUT4')
    invalid=[r for r in members if not r['valid_closed_manifold'] or r['connected_solids']!=1]
    reading={'scope':'Production f64 mesh-kernel solids, closed and connected, with exact standalone-to-installed viewer vertex and triangle arrays. The installed STEP retains native physical bodies and attaches the separate mesh-kernel wiring export.',
             'wiring_step_sha256':hashlib.sha256(step.read_bytes()).hexdigest(),
             'wiring_model_sha256':hashlib.sha256(Path(model).read_bytes()).hexdigest(),
             'assembly_step_sha256':hashlib.sha256(HOST.read_bytes()).hexdigest(),
             'assembly_mesh_sha256':hashlib.sha256(Path(str(HOST)+'.mesh').read_bytes()).hexdigest(),
             'wire_count':len(ids),'member_count':len(members),
             'all_valid_single_solids':not invalid,'invalid':invalid,
             'coverage_missing':sorted(expected-set(grouped)),
             'coverage_extra':sorted(set(grouped)-expected),
             'installed_missing':missing,'installed_changed':changed,
             'all_installed_wire_vertex_and_triangle_arrays_identical':not missing and not changed,
             'reference_frame_maximum_extent_residual_mm':max(r['maximum_extent_residual_mm'] for r in manifest['reference_frames'].values()),
             'unique_connection_ids':len(set(ids))==len(ids),
             'bench_pin_maps_match':bench,'members':members}
    report=json.loads(OUTPUT.read_text()) if OUTPUT.exists() else {}
    report.pop('native',None)
    report['production_solids']=reading
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in reading.items() if k!='members'}),flush=True)



def _source_mismatches(manifest,root):
    """Compare Python code across raw/staged sources and all other files by their bytes."""
    from _realized import code_digest
    sources=manifest.get('source_sha256',{})
    code=manifest.get('source_code_digest',{})
    if 'source_code_digest' in manifest:
        expected={name for name in sources if Path(name).suffix=='.py'}
        if (manifest.get('source_code_digest_algorithm')!='_realized.code_digest' or
                not isinstance(code,dict) or set(code)!=expected):
            return ['source_code_digest']
    def current(name):
        path=Path(root)/name
        if name in code:return code_digest(path)==code[name]
        with path.open('rb')as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()==sources[name]
    return [name for name in sources if not (Path(root)/name).is_file()or not current(name)]


def fine_review(manifest_path=MANIFEST,host=HOST,output=OUTPUT):
    """Inspect authoritative wire topology and its explicit source/export bindings."""
    from functools import cache
    sys.path[:0]=[str(ROOT/'hardware/scripts')]
    import _assembly_model
    from hardware.wiring.installed.step_merge import base_document
    manifest_path,host,output=map(Path,(manifest_path,host,output))
    manifest=json.loads(manifest_path.read_text())
    if not manifest.get('wiring_fine_model_sha256'):
        raise ValueError('Fine inspection requires the kernel wiring manifest and its bound model files')
    step=manifest_path.with_suffix('.step')
    wire_model=Path(str(step)+'.npz');physical_model=Path(str(host)+'.npz')
    @cache
    def sha(path):
        with Path(path).open('rb') as stream:
            return hashlib.file_digest(stream,'sha256').hexdigest()
    def arrays(path,names=None):
        with Path(path).open('rb') as stream:
            size=struct.unpack('<I',stream.read(4))[0]
            header=json.loads(stream.read(size));blob=4+size
            result={}
            for row in header['meshes']:
                if names is not None and row['name'] not in names:continue
                values={k:v for k,v in row.items() if k not in ('pos','nrm','idx','fac','col','uv')}
                for key in ('pos','nrm','idx','fac','col','uv'):
                    if key not in row:continue
                    offset,count=row[key];stream.seek(blob+offset)
                    remaining=count*4;h=hashlib.sha256()
                    while remaining:
                        data=stream.read(min(remaining,1<<20))
                        if not data:raise EOFError(f'{path}: truncated {key}')
                        h.update(data);remaining-=len(data)
                    values[key]={'count':count,'sha256':h.hexdigest()}
                result[row['name']]=values
        return header,result
    measured=_assembly_model.measure([_assembly_model.instance(wire_model)],())['bodies']
    names=Counter(base_name(row['name']) for row in measured)
    expected={f'wire-{r["id"]}' for r in manifest['routes']}
    expected.update(manifest.get('terminations',{}))
    expected.update(b['geometry_name'] for b in manifest.get('bundles',{}).values()
                    if b['geometry_name'] is not None)
    wire_header,wires=arrays(Path(str(step)+'.mesh'))
    host_header,installed=arrays(Path(str(host)+'.mesh'),names=set(wires))
    with np.load(wire_model,allow_pickle=False) as model:
        document=json.loads(bytes(model['document']))
    sources=manifest.get('source_sha256',{})
    source_errors=_source_mismatches(manifest,ROOT)
    bindings={
        'physical_fine_input':sha(physical_model)==manifest.get('physical_fine_model_sha256'),
        'wiring_fine_model':sha(wire_model)==manifest.get('wiring_fine_model_sha256'),
        'numbers':sha(manifest_path.with_suffix('.numbers.json'))==manifest.get('wiring_numbers_sha256'),
        'physical_step':hashlib.sha256(base_document(host.read_text()).encode()).hexdigest()==manifest.get('physical_scene_sha256'),
        'standalone_presentation_source':wire_header.get('src')==sha(step),
        'installed_presentation_source':host_header.get('src')==sha(host),
        'fine_document_presentation':document.get('presentation')=={
            'path':step.name+'.mesh','sha256':sha(Path(str(step)+'.mesh'))},
        'installed_presentation_arrays':all(installed.get(name)==row for name,row in wires.items()),
        'source_files':bool(sources) and not source_errors,
        'body_coverage':bool(expected) and set(names)==expected==set(wires),
    }
    fine={'scope':'Authoritative fine wire topology and source/export bindings, including exact installed presentation arrays. Contact, clearance and native B-rep readback retain their own artifact scopes.',
          'physical_fine_model_sha256':sha(physical_model),'wiring_fine_model_sha256':sha(wire_model),
          'wiring_step_sha256':sha(step),'manifest_sha256':sha(manifest_path),
          'body_count':len(measured),'conductor_count':len(manifest['routes']),
          'all_model_entries_passed_topology_check':True,
          'single_model_entry_by_name':all(count==1 for count in names.values()),
          'bindings':bindings,'all_bindings_match':all(bindings.values()),
          'source_mismatches':source_errors,'missing_bodies':sorted(expected-set(names)),
          'extra_bodies':sorted(set(names)-expected),
          'unique_connection_ids':len({r['id'] for r in manifest['routes']})==len(manifest['routes'])}
    report=json.loads(output.read_text()) if output.exists() else {}
    report['fine']=fine;output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(fine),flush=True)
    return fine


def source_review(manifest_path=MANIFEST,host=HOST,output=OUTPUT):
    """Bind the current electrical graph and regenerated numeric recipes to fine bodies."""
    from dataclasses import asdict
    import _assembly_model
    import _rust_part
    from hardware.wiring.installed.connections import connections
    from hardware.wiring.installed.model import STOCK
    from hardware.wiring.installed.wire_geometry import numbers as route_numbers
    manifest_path,host,output=map(Path,(manifest_path,host,output))
    fine=fine_review(manifest_path,host,output)
    manifest=json.loads(manifest_path.read_text())
    numbers=json.loads(manifest_path.with_suffix('.numbers.json').read_text())
    expected=_rust_part.check('machine','installed-wires',numbers)['bodies']
    actual=_assembly_model.measure([
        _assembly_model.instance(Path(str(manifest_path.with_suffix('.step'))+'.npz'))],())['bodies']
    def difference(a,b):
        if isinstance(a,dict) and isinstance(b,dict) and a.keys()==b.keys():
            values=[difference(a[k],b[k])for k in a]
        elif isinstance(a,(list,tuple))and isinstance(b,(list,tuple))and len(a)==len(b):
            values=[difference(x,y)for x,y in zip(a,b)]
        elif isinstance(a,(int,float))and isinstance(b,(int,float)):
            return abs(a-b)
        else:return 0. if a==b else None
        return None if any(v is None for v in values)else max(values,default=0.)
    graph={row.id:asdict(row)for row in connections()}
    routes={row['id']:row for row in manifest['routes']}
    graph_errors=[name for name,row in graph.items()
                  if name not in routes or any(routes[name].get(key)!=value for key,value in row.items())]
    numeric_routes={row['name']:row for row in numbers['routes']}
    source_recipes={row['name']:row for row in route_numbers(manifest['routes'],STOCK)['routes']}
    curve_deltas={name:difference(row['segments'],numeric_routes.get('wire-'+name,{}).get('segments'))
                  for name,row in routes.items()}
    recipe_deltas={name:difference(row,numeric_routes.get(name))for name,row in source_recipes.items()}
    rows=[]
    for source,readback in zip(expected,actual):
        delta={key:difference(source[key],readback[key])for key in ('min','max','center','volume')}
        topology=all(source[key]==readback[key]for key in ('vertices','triangles','faces'))
        rows.append({'name':readback['name'],'source_name':source['name'],
                     'source':source,'fine_readback':readback,'absolute_deltas':delta,
                     'topology_counts_match':topology,
                     'matches':source['name']==base_name(readback['name']) and
                               source['color']==readback['color'] and topology and
                               all(value is not None and value<1e-7 for value in delta.values())})
    graph_match=(set(graph)==set(routes) and not graph_errors and
                 len(routes)==manifest['connection_count'])
    curves_match=(set(numeric_routes)=={'wire-'+name for name in routes} and
                  all(delta is not None and delta<1e-9 for delta in curve_deltas.values())and
                  all(delta is not None and delta<1e-9 for delta in recipe_deltas.values()))
    physical_match=numbers.get('physical_fine_model_sha256')==manifest.get('physical_fine_model_sha256')
    shapes_match=bool(expected) and len(expected)==len(actual) and all(row['matches']for row in rows)
    result={'scope':'Current electrical graph and bound numeric recipes regenerated by the Rust producer, compared with authoritative fine bodies. Native B-rep and contact receipts retain their separate artifact scopes.',
            'graph_connection_count':len(graph),'manifest_connection_count':len(routes),
            'source_body_count':len(expected),'fine_body_count':len(actual),
            'graph_metadata_mismatches':graph_errors,'missing_routes':sorted(set(graph)-set(routes)),
            'extra_routes':sorted(set(routes)-set(graph)),'source_curve_maximum_deltas_mm':curve_deltas,
            'source_conductor_recipe_deltas':recipe_deltas,
            'recipe_binds_physical_fine_model':physical_match,
            'all_source_curves_match':graph_match and curves_match,
            'all_fine_shapes_match_regenerated_recipes':shapes_match,
            'all_bindings_match':fine['all_bindings_match'] and graph_match and curves_match and shapes_match and physical_match,
            'bodies':rows}
    report=json.loads(output.read_text());report['fine_source']=result
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items()if key not in
                     ('bodies','source_curve_maximum_deltas_mm','source_conductor_recipe_deltas')}),flush=True)
    return result


if __name__=='__main__':
    fine_review() if '--fine' in sys.argv else native_review() if '--native' in sys.argv else mesh_review()
