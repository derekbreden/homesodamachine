"""Enclosure exterior studies with the installed hardware in its published coordinates."""
from pathlib import Path
import argparse, base64, gzip, hashlib, json, struct, time
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


def mesh_shape(shape,limit=2800):
    v,f=shape.tessellate(.12,.2)
    m=trimesh.Trimesh(vertices=[q.toTuple() for q in v],faces=f,process=True)
    if len(m.faces)>limit:m=m.simplify_quadric_decimation(face_count=limit,aggression=5)
    return m


def add(key,mesh,role,models,limit=None):
    if limit and len(mesh.faces)>limit:mesh=mesh.simplify_quadric_decimation(face_count=limit,aggression=5)
    MESHES[key]={'p':np.round(mesh.vertices,2).reshape(-1),'i':mesh.faces.reshape(-1)}
    for model in models:MODELS[model]['parts'].append({'mesh':key,'role':role})


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
    cuts={'A':cq.Compound.makeCompound([corner_cuts(radius=22),upper_cuts(radius=6)]),
          'B':cq.Compound.makeCompound([corner_cuts(radius=22),upper_cuts(radius=6)]),
          'C':cq.Compound.makeCompound([corner_cuts(bevel=13),upper_cuts(bevel=4)])}
    bow=front_bow()
    for stem,s in sources.items():
        role='cartridge' if stem=='pump-cartridge' else 'cap' if stem=='pump-cap' else stem
        unchanged=stem in ('back-bottom','pump-cap')
        add('current-'+stem,mesh_shape(s,2800),role,list(MODELS) if unchanged else ['current'])
        if unchanged:continue
        for k,cutter in cuts.items():
            start=time.monotonic();result=s
            for tool in cutter.Solids():
                result=result.cut(tool,tol=1e-6).clean()
            cut_volume=result.Volume()
            added=0
            if k=='B' and stem!='back-top':
                if stem=='front-bottom': z0,z1=-6,160
                elif stem=='pump-cartridge':z0,z1=165.6150001,283.2450001
                else:z0,z1=160,355
                shape=bow.intersect(block(-110,110,-10,6,z0,z1))
                if stem=='front-top':shape=shape.cut(block(-110,110,-10,6,165.3650001,283.4950001))
                result=result.fuse(shape).clean();added=result.Volume()-cut_volume
                assert added>0,(k,stem,'front union lost material',added)
            name=k+'-'+stem
            assert result.isValid() and len(result.Solids())==1,(k,stem,'invalid study solid')
            exact_box=Bnd_Box();BRepBndLib.AddOptimal_s(result.wrapped,exact_box,False,False)
            m=mesh_shape(result,2800)
            add(name,m,role,[k])
            CHECKS['studies'][name]={'valid':result.isValid(),'solids':len(result.Solids()),'removed_mm3':s.Volume()-cut_volume,'added_mm3':added,'bounds':list(exact_box.Get())}
            print(name,CHECKS['studies'][name],round(time.monotonic()-start,2),flush=True)
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
    add('fixed-machine-display-cover',mesh_shape(cover,900),'cover',list(MODELS))
    data={'meshes':MESHES,'models':MODELS,'checks':CHECKS}
    buf=bytearray()
    for m in MESHES.values():
        for key,dtype,scale in [('p','<i2',50),('i','<u2',1)]:
            values=m[key];values=np.rint(values*scale) if key=='p' else values
            assert values.min()>=np.iinfo(dtype).min and values.max()<=np.iinfo(dtype).max
            arr=values.astype(np.int32)
            delta=np.diff(arr.reshape(-1,3),axis=0,prepend=np.zeros((1,3),dtype=np.int32)).reshape(-1) if key=='p' else np.diff(arr,prepend=0)
            assert delta.min()>=-32768 and delta.max()<=32767
            arr=delta.astype('<i2');buf.extend(b'\0'*(-len(buf)%4));m[key]=[len(buf),len(arr)];buf.extend(arr.tobytes())
    h=json.dumps(data,separators=(',',':')).encode();raw=struct.pack('<I',len(h))+h
    raw+=b'\0'*(-len(raw)%4)+bytes(buf)
    payload=base64.b64encode(gzip.compress(raw,9)).decode()
    (HERE/'models.b64').write_text(payload)
    (HERE/'geometry-checks.json').write_text(json.dumps(CHECKS,indent=2)+'\n')
    if (HERE/'enclosure-forms.template.html').exists():
        content=(HERE/'enclosure-forms.template.html').read_text().replace('__MODEL_DATA__',payload)
        assert len(content.encode())<1_000_000,len(content)
        (OUT/'enclosure-forms.html').write_text(content)
    print('payload bytes',len(payload),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)
