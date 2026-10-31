"""Manual review of the complete installed model; never invoked by a build/hook.

    tools/cad-venv/bin/python hardware/wiring/installed/review.py
    tools/cad-venv/bin/python hardware/wiring/installed/review.py --native

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
            'native':json.loads(OUTPUT.read_text()).get('native') if OUTPUT.exists() else None}
    OUTPUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'wires':len(wires),'physical_pairs':len(collisions),
                      'packing_pairs':len(packing),'bundle_pairs':len(bundle_collisions),
                      'termination_pairs':len(termination_collisions),
                      'missing':report['coverage_missing']}),flush=True)


def native_review():
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


if __name__=='__main__':
    native_review() if '--native' in sys.argv else mesh_review()
