"""Read the exported pieces, including both enclosure halves, at assembly poses."""
from pathlib import Path
import json, hashlib
import numpy as np
import trimesh
import manifold3d as mf

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools/cad-venv').is_dir())
ENC=ROOT/'hardware/printed-parts/enclosure/enclosure'
F=ROOT/'hardware/printed-parts/zone-c/funnel/funnel-frame.stl'

def solid(path,translation=(0,0,0)):
    m=trimesh.load_mesh(path)
    m.apply_translation(translation)
    assert m.is_watertight and m.is_winding_consistent and m.body_count==1,str(path)
    a=mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
    assert a.status()==mf.Error.NoError,str(path)
    return a,m

frame,mesh=solid(F,(0,182.5,299.9))
assert abs(mesh.bounds[0,2]-299.9)<.001,mesh.bounds
corbel_excess=[]
for sign in (-1,1):
    residual=sign*(mesh.vertices[:,1]-182.5)-np.tan(np.radians(30))*(mesh.vertices[:,2]-299.9)-27.5
    corbel_excess.append(float(residual.max()))
assert max(corbel_excess)<.001,corbel_excess
web=[]
# This ring stays inside the plug socket and outside the drain and wing slots.
web_probe_radius=17.0
for angle in np.linspace(0,2*np.pi,8,endpoint=False):
    origin=[1.85+web_probe_radius*np.cos(angle),182.5+web_probe_radius*np.sin(angle),298.9]
    points,_,_=mesh.ray.intersects_location([origin],[[0,0,1]])
    assert len(points)==2,(origin,points)
    zs=sorted(points[:,2]);assert len(zs)==2,zs
    web.append(float(zs[1]-zs[0]))
assert np.max(np.abs(np.asarray(web)-3))<.001,web
front,fmesh=solid(ENC/'enclosure-front-top.stl')
back,bmesh=solid(ENC/'enclosure-back-top.stl')
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [F,ENC/'enclosure-front-top.stl',ENC/'enclosure-back-top.stl']}
reads=[]
for col,shell in [('front',front),('back',back)]:
    travel=70 if col=='front' else 50
    sign=1 if col=='front' else -1
    poses=[]
    for off in np.unique(np.r_[np.linspace(0,travel,36),.25,.5,1,2,3,4,5,6,8,10]):
        v=(frame.translate((0,float(sign*off),0))^shell).volume()
        poses.append({'travel_mm':float(off),'overlap_mm3':v})
    reads.append({'joint':'frame / '+col+'-top','poses':poses,'max_overlap_mm3':max(p['overlap_mm3'] for p in poses)})
    print(reads[-1]['joint'],reads[-1]['max_overlap_mm3'],flush=True)
poses=[]
for off in np.unique(np.r_[np.linspace(0,50,36),.25,.5,1,2,3,4,5,6,8,10]):
    v=(front^back.translate((0,float(off),0))).volume()
    poses.append({'travel_mm':float(off),'overlap_mm3':v})
reads.append({'joint':'front-top / back-top','poses':poses,'max_overlap_mm3':max(p['overlap_mm3'] for p in poses)})
print(reads[-1]['joint'],reads[-1]['max_overlap_mm3'],flush=True)
capture=[]
for axis in range(3):
    for sign in (-1,1):
        shift=np.zeros(3);shift[axis]=sign*2
        a=frame.translate(shift)
        capture.append({'axis':'XYZ'[axis],'direction':sign,'displacement_mm':2,'bearing_intersection_mm3':(a^front).volume()+(a^back).volume()})
result={'source_sha256':hashes,'method':'Closed STL solids; sampled relative straight Y insertion. Other installed components are outside this mating-joint check.','flat_floor_z_mm':float(mesh.bounds[0,2]),'plug_web_probe_radius_mm':web_probe_radius,'plug_web_samples_mm':web,'full_width_corbel_plane_max_excess_mm':corbel_excess,'joints':reads,'captured_at_2mm':capture,'clear':all(r['max_overlap_mm3']<.1 for r in reads)}
(Path(__file__).parent/'rail-motion-check.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['clear'],[(r['joint'],r['max_overlap_mm3']) for r in reads]
assert all(r['bearing_intersection_mm3']>.1 for r in capture),capture
