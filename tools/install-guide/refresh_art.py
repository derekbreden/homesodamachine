"""Refresh the install guide's appliance views from the current meshes, on request."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'hardware/scripts'))
import _run_slots
import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project(point,matrix,size):
    p=np.asarray(matrix).reshape(4,4).T@np.array([*point,1.])
    return [(p[0]/p[3]+1)*size[0]/2,(1-p[1]/p[3])*size[1]/2]


def screen_overlay(image,screen,matrix,size):
    """Project the guide's Fill artwork onto the current glass inside its real bezel."""
    center=np.array(screen['centre'])+np.array(screen['normal'])*.15
    x=np.array([screen['width']/2,0,0]);y=np.array(screen['up'])*screen['height']/2
    corners=[project(center-x+y,matrix,size),project(center+x+y,matrix,size),
             project(center+x-y,matrix,size),project(center-x-y,matrix,size)]
    art=Image.open(ROOT/'hardware/install-guide/assets/fill-screen.png').convert('RGBA')
    uv=[(0,0),(art.width,0),(art.width,art.height),(0,art.height)]
    a=[];b=[]
    for (px,py),(u,v) in zip(corners,uv):
        a.extend([[px,py,1,0,0,0,-u*px,-u*py],[0,0,0,px,py,1,-v*px,-v*py]])
        b.extend([u,v])
    coefficients=np.linalg.solve(np.array(a),np.array(b))
    layer=art.transform(tuple(size),Image.Transform.PERSPECTIVE,coefficients,Image.Resampling.BICUBIC)
    return Image.alpha_composite(image.convert('RGBA'),layer)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'.cache/runs'/time.strftime('install-guide-%Y%m%dT%H%M%S'))
    parser.add_argument('--views',nargs='*')
    args=parser.parse_args();run=args.out.resolve();run.mkdir(parents=True,exist_ok=True)
    _run_slots.acquire('install-guide illustrations')
    def command(argv):
        result=subprocess.run([str(x) for x in argv],cwd=ROOT,text=True,capture_output=True,
                              **_run_slots.subprocess_kwargs())
        if result.returncode:
            raise RuntimeError(result.stderr or result.stdout)
        return result.stdout
    command([ROOT/'tools/hsm/target/release/install-illustrations',run])
    scenes=json.loads((run/'scenes.json').read_text())
    assets=ROOT/'hardware/install-guide/assets'
    registrations=json.loads((assets/'print-resolution.json').read_text())
    receipts=[]
    for view in scenes['views']:
        name=view['name']
        if args.views and name not in args.views:continue
        raw_ref_size=view['reference_size'];ref_size=raw_ref_size
        size=[int(x*view['scale']) for x in raw_ref_size]
        path=run/(name+'.png')
        result=json.loads(command(['hsm','render','manifold-layout/enclosure-assembly.step',path,
            '--payload',view['path'],'--cam',','.join(map(str,view['cam'])),
            '--target',','.join(map(str,view['target'])),'--up',','.join(map(str,view.get('up',[0,0,1]))),
            '--span',view['span'],'--size',f'{size[0]}x{size[1]}',
            '--transparent','--no-ground','--no-fog','--json']))
        report=result[0] if isinstance(result,list) else result
        matrix=report['camera']['view_proj']
        image=Image.open(path).convert('RGBA')
        if name.startswith('fill-'):
            image=screen_overlay(image,scenes['screen'],matrix,size)
        target=assets/('fill-screen-framed.png' if name=='fill-screen-framed' else f'steps/{name}.png')
        image.save(target)
        if name!='fill-screen-framed':
            reference_name=f'{name}.png' if name.startswith('fill-') else f'rear-layout-{name}.png'
            ref=assets/'reference'/reference_name
            image.resize(tuple(ref_size),Image.Resampling.LANCZOS).save(ref)
            old=registrations['assets'].get(f'steps/{name}.png',{})
            old.update({'reference_size':ref_size,'render_size':size,'scale':[view['scale']]*2,
                'coordinate_reference_path':str(ref.relative_to(assets)),
                'coordinate_reference_sha256':digest(ref),'render_sha256':digest(target),
                'source_sha256':scenes['source_sha256'],
                'scene_mesh_sha256':digest(Path(view['path'])),
                'registered_camera':{k:view[k] for k in ['cam','target','span']},
                'anchor_source_mm':view['anchors'],
                'anchors_reference_pixels':{k:project(p,matrix,raw_ref_size)
                                            for k,p in view['anchors'].items()}})
            old.pop('fixed_native_crop',None)
            registrations['assets'][f'steps/{name}.png']=old
        else:
            ref=assets/'reference/fill-screen-framed.png'
            image.save(ref)
            registrations['assets']['fill-screen-framed.png']={
                'reference_size':ref_size,'render_size':size,'scale':[1,1],
                'coordinate_reference_path':str(ref.relative_to(assets)),
                'coordinate_reference_sha256':digest(ref),'render_sha256':digest(target),
                'source_sha256':scenes['source_sha256']}
        receipts.append({'name':name,'sha256':digest(target),'path':str(target.relative_to(ROOT))})
        print(f'{name}: {size[0]}x{size[1]}',flush=True)
    (assets/'print-resolution.json').write_text(json.dumps(registrations,indent=2)+'\n')
    fills=[r for r in receipts if r['name'].startswith('fill-')]
    if fills:
        fill=json.loads((assets/'fill-scene-inputs.json').read_text())
        fill['purpose']='The Fill pictures and their motion cue follow the current appliance geometry.'
        fill['sources']={scenes['source']:scenes['source_sha256'],
            'tools/install-guide/art.rs':digest(ROOT/'tools/install-guide/art.rs'),
            'tools/install-guide/refresh_art.py':digest(Path(__file__)),
            'hardware/install-guide/assets/fill-screen.png':digest(assets/'fill-screen.png')}
        fill['screen']=scenes['screen']
        if any(r['name']=='fill-ready' for r in fills):
            fill['bottle_mouth']=scenes['bottle_mouth']
            mouth=np.array(scenes['bottle_mouth'])
            fill['arrow']=[(mouth+np.array([0,-190*np.cos(a),190*np.sin(a)])).tolist() for a in np.linspace(0,np.radians(20),11)]
            pose=next(x for x in scenes['views'] if x['name']=='fill-ready')
            fill['pose']={key:pose[key] for key in ['cam','target','span']};fill['pose']['size']=pose['reference_size']
        fill.setdefault('outputs_sha256',{}).update({r['path']:r['sha256'] for r in fills})
        for receipt in fills:
            fill.setdefault('views',{})[receipt['name']]={
                'source_payload_sha256':scenes['source_sha256'],'render_sha256':receipt['sha256']}
        (assets/'fill-scene-inputs.json').write_text(json.dumps(fill,indent=2)+'\n')
    (run/'result.json').write_text(json.dumps({'purpose':__doc__,'source_sha256':scenes['source_sha256'],'images':receipts},indent=2)+'\n')


if __name__=='__main__':main()
