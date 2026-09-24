"""Inset grip-ceiling supports using native subdivided facet painting."""
from pathlib import Path
import hashlib,json,subprocess,zipfile
import xml.etree.ElementTree as ET
import numpy as np

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
BASE=ROOT/'.cache/prints/2026-09-24-pump-cartridge-cap-mark2-v7'
STEM='pump-cartridge-cap-black-z004-mark2-v8-six-wall-grip-rounds'
source=next(BASE.glob('*-input.3mf'));target=JOB/(STEM+'-input.3mf')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(source)=='cce29d0aa5b949f0b95f8764cee0e0cda1f06024d913c8e32fb4ee3784f7253d'
assert not target.exists()
with zipfile.ZipFile(source) as z:members={n:z.read(n) for n in z.namelist()}
NS='http://schemas.microsoft.com/3dmanufacturing/core/2015/02';ET.register_namespace('',NS)
tag=lambda n:'{'+NS+'}'+n
member='3D/Objects/object_1.model';tree=ET.fromstring(members[member])
vertices=np.array([[float(v.get(a)) for a in ['x','y','z']] for v in tree.iter(tag('vertex'))])
cad=vertices+np.array([0,42.134498596191406,224.68450927734375])
flat=[];leaves=[]

def encode(p,depth=0):
    # Only this inset rectangle may receive support. Painting follows Bambu's
    # TriangleSelector::perform_split/serialize and Model::get_triangle_as_string.
    xy=p[:,:2].copy();xy[:,0]=np.abs(xy[:,0])
    lo=np.array([92.55,34.9325]);hi=np.array([100.7,49.3325])
    if ((xy>=lo)&(xy<=hi)).all():
        leaves.append((p,0));return '0'
    if (xy.max(axis=0)<lo).any() or (xy.min(axis=0)>hi).any() or depth==7:
        leaves.append((p,8));return '8'
    a,b,c=p;ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2
    children=[np.array([a,ab,ca]),np.array([ab,b,bc]),np.array([bc,c,ca]),np.array([ab,bc,ca])]
    # get_triangle_as_string reverses serialized nibbles. Serialization itself
    # visits children 3,2,1,0, so the saved string visits 0,1,2,3 then the parent.
    return ''.join(encode(q,depth+1) for q in children)+'3'

for i,t in enumerate(tree.iter(tag('triangle'))):
    p=cad[[int(t.get(a)) for a in ['v1','v2','v3']]]
    cross=np.cross(p[1]-p[0],p[2]-p[0])
    if cross[2]<0 and (np.abs(p[:,2]-272.1940001)<.0001).all() and (np.abs(p[:,0])>=91.7499).all():
        assert not t.get('paint_supports')
        code=encode(p)
        t.set('paint_supports',code)
        flat.append({'triangle':i,'paint_nibbles':len(code)})
assert len(flat)>=4
members[member]=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for n,p in members.items():z.writestr(n,p)
with zipfile.ZipFile(source) as z:
    assert [n for n,p in members.items() if z.read(n)!=p]==[member]
config=json.loads((BASE/'job-config.json').read_text());config['archive_stem']=STEM
config['support_ceiling_inset_mm']=.8
(JOB/'job-config.json').write_text(json.dumps(config,indent=2)+'\n')
prep=json.loads((BASE/'preparation.json').read_text())
prep.update(reference_input=str(source.relative_to(ROOT)),reference_input_sha256=sha(source),
            staged_input=str(target.relative_to(ROOT)),staged_input_sha256=sha(target),
            changed_archive_members=[member],support_ceiling_inset_mm=.8,
            ceiling_painted_source_facets=flat,
            facet_painting_sources=['https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/TriangleSelector.cpp','https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Model.cpp'],
            base_preparation=str((BASE/'preparation.json').relative_to(ROOT)))
prep['ceiling_leaf_area_mm2']={str(state):float(sum(np.linalg.norm(np.cross(p[1]-p[0],p[2]-p[0]))/2 for p,s in leaves if s==state)) for state in [0,8]}
(JOB/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
print(json.dumps({'facets':len(flat),'area':prep['ceiling_leaf_area_mm2'],'input_sha':sha(target)}),flush=True)
with (JOB/'ready/bambu-cli.log').open('w') as log:
    rc=subprocess.run(['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0','--arrange','0','--orient','0','--outputdir',str(JOB/'ready'),'--export-3mf',STEM+'.gcode.3mf',str(target)],cwd=JOB/'ready',stdout=log,stderr=subprocess.STDOUT).returncode
print('SLICE_EXIT',rc,flush=True)
raise SystemExit(rc)
