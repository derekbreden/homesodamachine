"""Enclosure exterior studies with the installed hardware in its published coordinates."""
from pathlib import Path
import argparse, base64, gzip, hashlib, json, struct, time, math, sys
from concurrent.futures import ProcessPoolExecutor
import cadquery as cq
import numpy as np
import trimesh
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
P=REPO/'hardware/printed-parts/enclosure/enclosure'
MODELS={k:{'parts':[]} for k in ('current','A','B','C')}
MESHES={}
CHECKS={'source':{},'studies':{}}
sys.path.insert(0,str(REPO/'hardware/printed-parts/cadlib'))
import flute_skin
import reeding
sys.path.insert(0,str(REPO/'hardware/scripts'))


def mesh_shape(shape):
    v,f=shape.tessellate(.02,.08)
    m=trimesh.Trimesh(vertices=[q.toTuple() for q in v],faces=f,process=True)
    return m


def add(key,mesh,role,models,limit=None):
    from flute_payload import creased
    if limit and len(mesh.faces)>limit:mesh=mesh.simplify_quadric_decimation(face_count=limit,aggression=5)
    positions,normals,indices,_=creased(mesh)
    MESHES[key]={'p':positions.reshape(-1),'n':normals.reshape(-1),'i':indices.reshape(-1)}
    for model in models:MODELS[model]['parts'].append({'mesh':key,'role':role})


def read_payload(path):
    raw=path.read_bytes();n=struct.unpack('<I',raw[:4])[0];header=json.loads(raw[4:4+n]);blob=raw[4+n:]
    for m in header['meshes']:
        vertices=np.frombuffer(blob,dtype='<f4',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3).copy()
        faces=np.frombuffer(blob,dtype='<u4',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3).copy()
        yield m['name'],trimesh.Trimesh(vertices=vertices,faces=faces,process=True)


def outline_half(key):
    """The right half of the plan, from the front centre to the rear centre."""
    line=lambda a,b: ('line',math.dist(a,b),(a,tuple((np.array(b)-a)/math.dist(a,b)),
                                          tuple((np.array(b)-a)[[1,0]]*np.array([1,-1])/math.dist(a,b))))
    arc=lambda c,a,r,sweep: ('arc',r*sweep,(c,a,r))
    segments=[]
    if key=='B':
        a,h=79.5,6.;r=(a*a+h*h)/(2*h);theta=math.asin(a/r)
        segments += [arc((0,r-1),-math.pi/2,r,theta),line((a,5),(85.5,5))]
    else:segments.append(line((0,5),(85.5 if key=='A' else 94.5 if key=='C' else 95.5,5)))
    if key=='C':
        segments=[line((0,5),(94.6,5)),line((94.6,5),(107.5,17.9))]
        y=17.9
    else:
        r=22 if key in ('A','B') else 12
        segments.append(arc((107.5-r,5+r),-math.pi/2,r,math.pi/2));y=5+r
    segments += [line((107.5,y),(107.5,455)),arc((95.5,455),0,12,math.pi/2),line((95.5,467),(0,467))]
    return segments


def study_rail(key):
    """Retain the installed vent/flute phase aft of Y80; distribute its front phase
    across the revised forebody. The front remains symmetric about the centreline."""
    original=outline_half('current');revised=outline_half(key)
    half=sum(s[1] for s in original);length=sum(s[1] for s in revised)
    front=half-(467-80+12*(math.pi/2-1)+95.5)
    new_front=front+length-half
    def at(s):
        s=(s+half)%(2*half)-half;side=-1 if s<0 else 1;t=abs(s)
        t=t*new_front/front if t<front else t+length-half
        p,n=reeding.walk(revised,t)
        return (side*p[0],p[1]),(side*n[0],n[1])
    return flute_skin.Rail(at=at,length=2*half),2*half/260


def study_mesh(job):
    key,stem,cache=job;cache=Path(cache);name=key+'-'+stem
    saved=cache/(name+'.npz');reading=cache/(name+'.json')
    dependencies=(Path(__file__),Path(flute_skin.__file__),Path(reeding.__file__),P/f'enclosure-{stem}.step')
    if saved.exists() and reading.exists() and reading.stat().st_mtime>max(p.stat().st_mtime for p in dependencies):
        return name,str(saved),json.loads(reading.read_text())
    start=time.monotonic();s=cq.importers.importStep(str(P/f'enclosure-{stem}.step')).val()
    cutter=cq.Compound.makeCompound([corner_cuts(bevel=13),upper_cuts(bevel=4)]) if key=='C' else cq.Compound.makeCompound([corner_cuts(radius=22),upper_cuts(radius=6)])
    result=s
    for tool in cutter.Solids():result=result.cut(tool,tol=1e-6).clean()
    cut_volume=result.Volume();added=0
    if key=='B' and stem!='back-top':
        z0,z1=(-6,160) if stem=='front-bottom' else (165.6150001,283.2450001) if stem=='pump-cartridge' else (160,355)
        shape=front_bow().intersect(block(-110,110,-10,6,z0,z1))
        if stem=='front-top':shape=shape.cut(block(-110,110,-10,6,165.3650001,283.4950001))
        result=result.fuse(shape).clean();added=result.Volume()-cut_volume
        assert added>0,(name,'front union lost material',added)
    assert result.isValid() and len(result.Solids())==1,(name,'invalid study solid')
    exact_box=Bnd_Box();BRepBndLib.AddOptimal_s(result.wrapped,exact_box,False,False)
    mesh=mesh_shape(result)
    rail,pitch=study_rail(key)
    mesh=flute_skin.flute(mesh,[rail],pitch,1.2,5)
    assert mesh.is_watertight,(name,'open fluted mesh')
    # Keep the actual flute triangles and the fine CAD tessellation. No face-count target.
    np.savez_compressed(saved,p=mesh.vertices,f=mesh.faces)
    row={'valid':True,'solids':1,'removed_mm3':s.Volume()-cut_volume,'added_mm3':added,
         'bounds':list(exact_box.Get()),'triangles':len(mesh.faces),'watertight':bool(mesh.is_watertight),
         'preview_reduction':False,'cad_linear_tolerance_mm':.02,'cad_angle_tolerance_rad':.08}
    reading.write_text(json.dumps(row,indent=2)+'\n')
    print(name,len(mesh.faces),'triangles',round(time.monotonic()-start,1),'seconds',flush=True)
    return name,str(saved),row


def block(x0,x1,y0,y1,z0,z1):
    return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()


def corner_cuts(radius=None,bevel=None):
    cutters=[]
    if radius:
        for side in (-1,1):
            x=side*(107.5-radius)
            box=block(-107.6,-107.5+radius,4.9,5+radius,-7,356) if side<0 else block(107.5-radius,107.6,4.9,5+radius,-7,356)
            cylinder=cq.Solid.makeCylinder(radius,365,cq.Vector(x,5+radius,-8))
            cutters.append(box.cut(cylinder))
    else:
        for side in (-1,1):
            poly=[(side*107.6,4.9),(side*(107.5-bevel),4.9),(side*107.6,5+bevel)]
            cutters.append(cq.Workplane('XY').polyline(poly).close().extrude(365).translate((0,0,-8)).val())
    return cq.Compound.makeCompound(cutters)


def upper_cuts(radius=None, bevel=None):
    cutters=[]
    width=radius or bevel
    for side in (-1,1):
        for tilt,origin,length in [(0,(0,0,355),480),(45,(0,35.9359216769,324.0640783231),87.5)]:
            if radius:
                x=side*(107.5-radius)
                stock=block(-107.6,-107.5+radius,-length/2,length/2,-radius,.1) if side<0 else block(107.5-radius,107.6,-length/2,length/2,-radius,.1)
                cyl=cq.Solid.makeCylinder(radius,length+2,cq.Vector(x,-length/2-1,-radius),cq.Vector(0,1,0))
                tool=stock.cut(cyl)
            else:
                tool=cq.Workplane('XZ').polyline([(side*107.6,.1),(side*(107.5-width),.1),(side*107.6,-width)]).close().extrude(length/2,both=True).val()
            if tilt==0:origin=(0,240,355)
            cutters.append(tool.rotate((0,0,0),(1,0,0),tilt).translate(origin))
    return cq.Compound.makeCompound(cutters)


def front_bow():
    a=79.5
    wire=cq.Workplane('XY').moveTo(-a,5).threePointArc((0,-1),(a,5)).lineTo(a,8).lineTo(-a,8).close()
    bow=wire.extrude(300).translate((0,0,-6)).val()
    # The added face closes into the fixed 45-degree display plane at its lower arris.
    # Explicit sloped upper bound: z <= y + 288.1281566.
    keep=cq.Workplane('YZ').polyline([(-10,-7),(10,-7),(10,298.1281566),(-10,278.1281566)]).close().extrude(120,both=True).val()
    return bow.intersect(keep)


def source_payload():
    p=REPO/'hardware/manifold-layout/enclosure-assembly.step.mesh'
    raw=p.read_bytes();n=struct.unpack('<I',raw[:4])[0];header=json.loads(raw[4:4+n]);blob=raw[4+n:]
    CHECKS['source']['assembly_sha256']=hashlib.sha256(raw).hexdigest()
    for m in header['meshes']:
        vertices=np.frombuffer(blob,dtype='<f4',count=m['pos'][1],offset=m['pos'][0]).reshape(-1,3).copy()
        faces=np.frombuffer(blob,dtype='<u4',count=m['idx'][1],offset=m['idx'][0]).reshape(-1,3).copy()
        yield m['name'],trimesh.Trimesh(vertices=vertices,faces=faces,process=True)


def main(output):
    OUT=output
    OUT.mkdir(parents=True, exist_ok=True)
    sources={}
    for stem in ('front-bottom','front-top','back-bottom','back-top','pump-cartridge','pump-cap'):
        f=P/f'enclosure-{stem}.step';sources[stem]=cq.importers.importStep(str(f)).val()
        CHECKS['source'][stem]=hashlib.sha256(f.read_bytes()).hexdigest()
        print('read',stem,flush=True)
    cache=OUT/'mesh-cache';cache.mkdir(exist_ok=True)
    jobs=[]
    for stem,s in sources.items():
        role='cartridge' if stem=='pump-cartridge' else 'cap' if stem=='pump-cap' else stem
        unchanged=stem in ('back-bottom','pump-cap')
        payload=P/f'enclosure-{stem}.step.mesh'
        CHECKS['source'][stem+'_fluted_payload_sha256']=hashlib.sha256(payload.read_bytes()).hexdigest()
        _,mesh=next(read_payload(payload))
        add('current-'+stem,mesh,role,list(MODELS) if unchanged else ['current'])
        if unchanged:continue
        for k in ('A','B','C'):
            if k=='B' and stem=='back-top':continue
            jobs.append((k,stem,str(cache)))
    with ProcessPoolExecutor(max_workers=3) as pool:
        for name,path,row in pool.map(study_mesh,jobs):
            k,stem=name.split('-',1);role='cartridge' if stem=='pump-cartridge' else stem
            saved=np.load(path);mesh=trimesh.Trimesh(saved['p'],saved['f'],process=False)
            add(name,mesh,role,[k,'B'] if name=='A-back-top' else [k])
            CHECKS['studies'][name]=row
    for name,mesh in source_payload():
        if name in ('display-cover','display-gasket'):continue
        if name.startswith('enclosure-') and name not in ('enclosure-tee-carrier-left','enclosure-tee-carrier-right'):continue
        if any(x in name for x in ('-word','nameplate-ink','tube-collar-')):continue
        if name.startswith('cold-core/') and name not in ('cold-core/foam-shell','cold-core/foam-cap-top','cold-core/foam-cap-lid-top'):continue
        if name.startswith(('coil-','tee-carrier-spring')):continue
        role='hardware'
        if name=='funnel':role='funnel'
        elif name=='display/1':role='device'
        elif name=='display/2':role='glass'
        elif name=='display-cover':role='cover'
        elif name=='display-gasket':role='gasket'
        elif name=='asse-drip-pan':role='pan'
        elif name.startswith('bulkhead-ring-'):role='port'
        elif name in ('c14-inlet','keystone-jack','nameplate') or name.startswith('bulkhead-'):role='rear'
        elif name.startswith('cold-core/'):role='core'
        elif name.startswith('pump-') and name!='pump-jack':role='pump'
        elif name.startswith(('tube-','turn-','step-')):role='tube'
        elif name.startswith('enclosure-tee'):role='carrier'
        elif name.startswith('compressor'):role='compressor'
        elif name=='condenser+fan':role='condenser'
        if role=='core':mesh=mesh.convex_hull
        limit=700 if role in ('core','funnel','pan','cover','condenser') else 180
        add('fixed-'+name,mesh,role,list(MODELS),limit)
    cover_path=REPO/'hardware/printed-parts/enclosure/display-cover/display-cover.step'
    cover=cq.importers.importStep(str(cover_path)).val().rotate((0,0,0),(1,0,0),45).translate((0,35.9359216769,324.0640783231))
    CHECKS['source']['display_cover_sha256']=hashlib.sha256(cover_path.read_bytes()).hexdigest()
    add('fixed-machine-display-cover',mesh_shape(cover),'cover',list(MODELS))
    data={'meshes':MESHES,'models':MODELS,'checks':CHECKS}
    buf=bytearray()
    for m in MESHES.values():
        for key,dtype,scale in [('p','<i4',1000),('n','<i4',10000),('i','<u4',1)]:
            values=m[key];values=np.rint(values*scale) if key in ('p','n') else values
            assert values.min()>=np.iinfo(dtype).min and values.max()<=np.iinfo(dtype).max
            arr=values.astype(np.int32)
            delta=np.diff(arr.reshape(-1,3),axis=0,prepend=np.zeros((1,3),dtype=np.int32)).reshape(-1) if key in ('p','n') else np.diff(arr,prepend=0)
            arr=delta.astype('<i4');buf.extend(b'\0'*(-len(buf)%4));m[key]=[len(buf),len(arr)];buf.extend(arr.tobytes())
    h=json.dumps(data,separators=(',',':')).encode();raw=struct.pack('<I',len(h))+h
    raw+=b'\0'*(-len(raw)%4)+bytes(buf)
    payload=base64.b64encode(gzip.compress(raw,9)).decode()
    (HERE/'models.b64').write_text(payload)
    (HERE/'geometry-checks.json').write_text(json.dumps(CHECKS,indent=2)+'\n')
    from compose import compose
    compose(OUT)
    print('payload bytes',len(payload),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
