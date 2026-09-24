"""Check every upper support road against the downward-round mesh above it."""
from pathlib import Path
from collections import defaultdict
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import Polygon,LineString
from shapely import union_all

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
BASE=ROOT/'.cache/prints/2026-09-24-pump-cartridge-cap-mark2-v7'
with zipfile.ZipFile(next(BASE.glob('*-input.3mf'))) as z:
    tree=ET.fromstring(z.read('3D/Objects/object_1.model'))
tag=lambda n:'{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'+n
v=np.array([[float(e.get(a)) for a in ['x','y','z']] for e in tree.iter(tag('vertex'))])+[162.5,210.204998493,59.489501953]
f=np.array([[int(t.get(a)) for a in ['v1','v2','v3']] for t in tree.iter(tag('triangle')) if t.get('paint_supports')=='8'])
assert len(f)==31562
tri=v[f];low=tri[:,:,2].min(axis=1);high=tri[:,:,2].max(axis=1)
segments=json.loads((JOB/'upper-support-segments.json').read_text())
by_z=defaultdict(list)
for s in segments:by_z[s['layer']].append(s)

def clip(poly,z,above):
    out=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        ia=(a[2]>=z) if above else (a[2]<=z)
        ib=(b[2]>=z) if above else (b[2]<=z)
        if ia:out.append(a)
        if ia!=ib:out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
    return np.array(out)

hits=[];counts=[]
for z,roads in sorted(by_z.items()):
    subset=tri[(high>=z-.00001)&(low<=z+.60)]
    shapes=[]
    for triangle in subset:
        p=clip(triangle,z-.00001,True)
        if len(p)<3:continue
        p=clip(p,z+.60,False)
        if len(p)>=3:
            poly=Polygon(p[:,:2])
            if poly.area>1e-12:shapes.append(poly)
    region=union_all(shapes)
    count=0
    for s in roads:
        road=LineString([s['a'][:2],s['b'][:2]]).buffer(s['width']/2+.05)
        if region.intersects(road):
            area=region.intersection(road).area
            if area>1e-8:
                count+=1;hits.append({**s,'projected_overlap_area_mm2':area})
    counts.append({'z_mm':z,'road_count':len(roads),'near_round_road_count':count})
report={'scope':'All Support, Support transition and Support interface extrusion roads at or above Z100 mm; entire bead width plus 0.05 mm XY allowance; exact clipped triangle projections through 0.60 mm above the support top.',
        'rounded_surface_triangles':len(f),'support_road_count':len(segments),'vertical_contact_check_mm':.60,
        'xy_allowance_mm':.05,'near_round_road_count':len(hits),'by_z':counts,'near_round_roads':hits,'pass':not hits}
(JOB/'round-contact-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['near_round_roads','by_z']},indent=2))
assert not hits,hits[:2]
