"""Package the proposal's native shapes as compact inline-viewer meshes."""
from pathlib import Path
import argparse, base64, json, zlib, struct, hashlib
import numpy as np
from fast_simplification import simplify
import cadquery as cq


def package(source, output):
    parts={p.stem:cq.Shape.importBrep(str(p)) for p in source.glob('*.brep') if p.stem!='g-ganen-pump'}
    fit=json.loads((source/'fit-review.json').read_text())
    top=fit['dimensions_mm']['cap_top_z']
    bottom=fit['dimensions_mm']['cap_bottom_z']
    data={'meshes':[],'objects':{},'scenes':{}}
    signature=hashlib.sha256(b''.join(p.read_bytes() for p in sorted(source.glob('*.brep')))).hexdigest()[:12]
    mesh_cache=source/('mesh-cache-'+signature)
    mesh_cache.mkdir(exist_ok=True)
    def mesh(name, shape, role, opacity=1.):
        print('Mesh '+name,flush=True)
        cached=mesh_cache/(name+'.json')
        if cached.is_file(): entry=json.loads(cached.read_text())
        else:
            vertices,triangles=shape.tessellate(.12,.35)
            if not triangles:return None
            entry={'p':[round(c,3) for v in vertices for c in v.toTuple()],
                   'i':[i for t in triangles for i in t]}
            cached.write_text(json.dumps(entry,separators=(',',':')))
        data['meshes'].append(entry)
        data['objects'][name]={'m':len(data['meshes'])-1,'role':role,'opacity':opacity}
        return name
    def cropped(shape,low,high):
        region=cq.Solid.makeBox(*(high[i]-low[i] for i in range(3)),cq.Vector(*low))
        return shape.intersect(region)
    roles={}
    for n in parts:
        roles[n]=('grip' if n.startswith('grip-') else
                  'air' if n.startswith('air-') else
                  'reservoir' if n in ('reservoir-a','reservoir-b') else
                  'outer' if n.startswith('outer-') or n=='foam-shell' else
                  'liquid' if n.startswith('liquid-') or n.startswith('b-fill-') else
                  'lid' if n.startswith('cap-') else 'context')
        opacity={'outer':.12,'reservoir':.20,'context':.32,'lid':.9}.get(roles[n],1.)
        shape=parts[n]
        if n.startswith('wire-') or n.startswith('tube-above'):
            shape=cropped(shape,(-142.,-91.,200.),(142.,91.,310.))
        mesh(n,shape,roles[n],opacity)

    # The purchased pump has thousands of scan-derived planar faces. Reuse the
    # assembly's already published native tessellation instead of remeshing it.
    root=next(p for p in Path(__file__).resolve().parents if (p/'web').is_dir())
    payload=root/'hardware/manifold-layout/enclosure-assembly.step.mesh'
    raw=payload.read_bytes();head_len=struct.unpack('<I',raw[:4])[0]
    head=json.loads(raw[4:4+head_len]);blob=memoryview(raw)[4+head_len:]
    frame=json.loads((root/'hardware/manifold-layout/above-core.json').read_text())['cap_lid_pose']
    rotation=np.array(frame['rotation']);translation=np.array(frame['translation_mm'])
    positions=[];triangles=[];offset=0
    for row in head['meshes']:
        if not row['name'].startswith('cold-core/g-ganen-pump/'):continue
        a,n=row['pos'];p=np.frombuffer(blob,dtype='<f4',count=n,offset=a).reshape(-1,3).astype(float)
        p=(p-translation)@rotation;p[:,:2]*=-1;p[:,2]+=228.
        a,n=row['idx'];i=np.frombuffer(blob,dtype='<u4',count=n,offset=a).astype(int)
        positions.extend(p.round(3).ravel().tolist());triangles.extend((i+offset).tolist());offset+=len(p)
    pump_native=cq.Shape.importBrep(str(source/'g-ganen-pump.brep'))
    pump_box=pump_native.BoundingBox()
    box=np.array([pump_box.xmin,pump_box.ymin,pump_box.zmin,pump_box.xmax,pump_box.ymax,pump_box.zmax])
    p=np.array(positions).reshape(-1,3)
    bbox_error=float(np.max(np.abs(np.r_[p.min(axis=0),p.max(axis=0)]-box)))
    distances=[pump_native.distance(cq.Vertex.makeVertex(*v))
               for v in p[np.linspace(0,len(p)-1,60,dtype=int)]]
    if bbox_error>.12 or max(distances)>.12:
        raise ValueError(f'Pump display mesh does not agree with native context: {bbox_error}, {max(distances)}')
    (source/'pump-display-provenance.json').write_text(json.dumps({
        'payload':str(payload.relative_to(root)),'payload_assembly_sha256':head['src'],
        'native_clearance_assembly_sha256':fit['baseline_assembly']['sha256'],
        'maximum_bbox_error_mm':bbox_error,'sample_count':len(distances),
        'maximum_sampled_vertex_to_native_distance_mm':max(distances),
        'scope':'Purchased pump display context only; fit clearances use the frozen native B-rep, not this mesh.'},indent=2)+'\n')
    data['meshes'].append({'p':positions,'i':triangles})
    data['objects']['g-ganen-pump']={'m':len(data['meshes'])-1,'role':'context','opacity':.32}

    overview=[n for n in data['objects'] if n not in ('foam-shell','float-rod-a','float-rod-b')
              and not n.startswith('reservoir-')]
    # Lid-level liquid tubes are cropped here; the whole-core view keeps their full length.
    for n in ('liquid-a','liquid-b'):
        overview.remove(n)
        name='top-'+n
        mesh(name,cropped(parts[n],(-140.,-90.,197.),(140.,90.,240.)), 'liquid')
        overview.append(name)
    data['scenes']['assembly']={'title':'Lids and air tubes','objects':overview,
        'target':[0.,-4.,227.],'offset':[290.,-350.,310.],'span':325.,
        'labels':[
            {'p':[120.,-26.,239.4],'text':'A · 4 mm air tube'},
            {'p':[-102.,-32.5,239.4],'text':'B · 4 mm air tube'}],
        'detail':'Separate air paths · straight tubes · openings 6 mm above the outer cap'}

    # Exact native section, including the outer casing floor and its original tube guide.
    x,y=84.2,-45.
    low=(x-13.,y,205.);high=(x+13.,y+12.,219.)
    section=[]
    for n,role in [('cap-a','lid'),('grip-a-draw','grip'),('liquid-a','liquid'),('outer-cup','outer')]:
        name='section-'+n
        mesh(name,cropped(parts[n],low,high),role,.4 if role=='outer' else 1.)
        section.append(name)
    mesh('free-grip',parts['grip-a-draw'],'grip')
    data['scenes']['grip']={'title':'Flush ¼-inch tube grip','objects':section,
        'target':[x,y+3.5,211.5],'offset':[17.,-25.,17.],'span':34.,
        'labels':[
            {'p':[x+4.4,y,top],'text':'Upper face flush'},
            {'p':[x+4.4,y,bottom],'text':'Lower face flush'},
            {'p':[x+4.9,y,212.65],'text':'45° seat'}],
        'detail':'4 mm captured thickness · Ø9 waist · Ø11 flares · Ø6.2 bore candidate',
        'exploded':{'replace':'section-grip-a-draw','with':'free-grip','shift':[0.,0.,10.],
                    'hide':['section-outer-cup','section-liquid-a'],
                    'target':[x,y+3.5,216.],'span':38.}}
    for letter in ('a','b'):
        x,y=fit['dimensions_mm']['vent_axes'][letter]
        low=(x-13.,y,203.);high=(x+13.,y+12.,242.)
        items=[]
        for n,role in [(f'cap-{letter}','lid'),(f'grip-{letter}-air','grip'),
                       (f'air-{letter}','air'),('outer-cup','outer'),('outer-lid','outer')]:
            name=f'vent-{letter}-{n}'
            mesh(name,cropped(parts[n],low,high),role,.95)
            items.append(name)
        data['scenes']['vent-'+letter]={'title':f'Vent {letter.upper()} section','objects':items,
            'target':[x,y,223.],'offset':[21.,-32.,14.],'span':46.,
            'labels':[
                {'p':[x,y,239.4],'text':'Open to air above foam'},
                {'p':[x+3.6,y,222.],'text':'Integral passage wall'},
                {'p':[x+3.0,y,211.4],'text':'Flush TPU grip'},
                {'p':[x+5.5,y,207.2],'text':'Splash baffle'}],
            'detail':'Ø4 / Ø2.5 mm tube · Ø5.2 passage · 2 mm printed passage wall'}
    whole=[n for n in parts if n in data['objects']]
    whole.append('g-ganen-pump')
    data['scenes']['core']={'title':'Reservoirs in core','objects':whole,
        'target':[0.,0.,143.],'offset':[330.,-410.,275.],'span':370.,
        'labels':[
            {'p':[120.,-26.,239.4],'text':'Air A'},
            {'p':[-102.,-32.5,239.4],'text':'Air B'},
            {'p':[106.,42.,115.],'text':'Reservoir A'},
            {'p':[-106.,42.,115.],'text':'Reservoir B'}],
        'detail':'Current bodies, rim gaskets, dip-tube routes and B-fill fittings retained'}
    # Weld coincident face vertices and use bounded, per-mesh integer positions.
    # Small section views keep 0.001mm precision; large context parts keep 0.005mm.
    binary=bytearray()
    names={item['m']:name for name,item in data['objects'].items()}
    context_budgets={'g-ganen-pump':12000,'valve-v-b':4000,'b-fill-upper':3000,
                     'outer-cup':9000,'wire-PE-carbonator':1800,'wire-PE-bus':1200}
    for number,m in enumerate(data['meshes']):
        p=np.array(m.pop('p')).reshape(-1,3)
        i=np.array(m.pop('i')).reshape(-1,3)
        unique,inverse=np.unique(p,axis=0,return_inverse=True)
        i=inverse[i]
        i=i[(i[:,0]!=i[:,1])&(i[:,0]!=i[:,2])&(i[:,1]!=i[:,2])]
        budget=context_budgets.get(names.get(number,''))
        if budget and len(i)>budget:
            unique,i=simplify(unique,i,target_count=budget,agg=3.,preserve_border=True)
        # Native seat and vent section meshes are never reduced.
        origin=(unique.max(axis=0)+unique.min(axis=0))/2.
        span=float(np.max(np.ptp(unique,axis=0)))
        scale=.001 if span<65. else max(.005,span/65500.)
        packed=np.rint((unique-origin)/scale).astype('<i2')
        m['p']=[len(binary),packed.size];m['s']=scale;m['o']=origin.tolist()
        binary.extend(packed.tobytes())
        while len(binary)%4:binary.append(0)
        m['k']=16 if len(unique)<65536 else 32
        indices=i.astype('<u2' if m['k']==16 else '<u4').ravel()
        m['i']=[len(binary),indices.size]
        binary.extend(indices.tobytes())
        while len(binary)%4:binary.append(0)
    header=json.dumps(data,separators=(',',':')).encode()
    header+=b' '*((-len(header))%4)
    raw=struct.pack('<I',len(header))+header+binary
    compressed=zlib.compress(raw,9)
    packed=struct.pack('<I',len(compressed))+compressed
    packed+=b' '*((-len(packed))%4)
    # A JSON-safe Base85 alphabet avoids angle brackets in an inline script.
    encoded=base64.b85encode(packed).decode().replace('<',':').replace('>',',')
    output.write_text(encoded)
    print(json.dumps({'mesh_count':len(data['meshes']),'triangles':sum(m['i'][1]//3 for m in data['meshes']),
                      'packed_bytes':len(raw),'encoded_bytes':output.stat().st_size}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    package(args.source,args.output)
