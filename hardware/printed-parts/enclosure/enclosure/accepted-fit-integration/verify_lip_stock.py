"""Sample the printed nameplate retaining lips, including the fluted surface."""
from pathlib import Path
import hashlib,json,numpy as np,trimesh
here=Path(__file__).resolve().parent
m=trimesh.load_mesh(here.parent/'enclosure-back-top.stl')
xs=[38.16+s*(104.53/2+t) for s in (-1,1) for t in (1.30,1.60,2.0,2.25)]
zs=[269.1785001+t for t in (-13,-6,0,6,13)]
origins=np.array([[x,461,z] for x in xs for z in zs]);directions=np.tile([0,1,0],(len(origins),1))
loc,ray,tri=m.ray.intersects_location(origins,directions,multiple_hits=True)
rows=[]
for i,o in enumerate(origins):
 ys=sorted(set(round(float(y),5) for y in loc[ray==i,1]));roof=471.3-3.36+1.68+.45
 outer=[y for y in ys if y>roof+.01]
 assert outer,(o,ys)
 rows.append({'x':o[0],'z':o[2],'ray_y_hits':ys,'lip_mm':max(outer)-roof})
minimum=min(r['lip_mm'] for r in rows)
assert minimum>1.19,minimum
(here/'fluted-receiver-stock.json').write_text(json.dumps({'pass':True,'source_stl_sha256':hashlib.sha256((here.parent/'enclosure-back-top.stl').read_bytes()).hexdigest(),'minimum_sampled_nameplate_lip_mm':minimum,'sample_count':len(rows),'samples':rows},indent=2)+'\n')
print('Nameplate lip in fluted STL',minimum,'mm; samples',len(rows))
