from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET,zipfile
import numpy as np
import trimesh

ROOT=Path.cwd(); F=ROOT/'hardware/printed-parts/faucet'; W=ROOT/'.cache/printer-control/faucet-current-review-20261011'
W.mkdir(parents=True,exist_ok=True)
acceptance=json.loads((F/'industrial/physical-acceptance.json').read_text())
project=ROOT/acceptance['prepared_project']
assert hashlib.sha256(project.read_bytes()).hexdigest()==acceptance['prepared_project_sha256']
prep=json.loads((project.parent/'preparation.json').read_text())
NS={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}

def restored(z,row):
    doc=ET.fromstring(z.read(row['member']))
    g=doc.find('m:resources/m:object/m:mesh',NS)
    vs=np.array([[float(v.get(a)) for a in 'xyz'] for v in g.find('m:vertices',NS)])+row['source_center_mm']
    fs=np.array([[int(v.get(a)) for a in ('v1','v2','v3')] for v in g.find('m:triangles',NS)])
    return trimesh.Trimesh(vertices=vs,faces=fs,process=True)

def distances(a,b,z_low=None):
    points=np.vstack([a.triangles_center,a.vertices])
    if z_low is not None:points=points[points[:,2]>=z_low]
    if len(points)>7000:points=points[np.unique(np.linspace(0,len(points)-1,7000,dtype=int))]
    readings=[]
    for i in range(0,len(points),200):
        _q,d,_face=trimesh.proximity.closest_point(b,points[i:i+200]);readings.extend(d.tolist())
    d=np.array(readings);idx=np.argsort(d)[-8:][::-1]
    return dict(samples=len(points),max_mm=float(d.max()),p99_mm=float(np.percentile(d,99)),
                above_0_025_mm=int((d>.025).sum()),witnesses=[dict(point=points[i].tolist(),distance_mm=float(d[i])) for i in idx])

rows=[]
with zipfile.ZipFile(project) as archive:
 for row in prep['parts']:
    a=restored(archive,row);b=trimesh.load(ROOT/row['source'],force='mesh',process=True)
    a.export(W/(row['name']+'-accepted.stl'))
    region=68.0 if row['name']=='industrial-shell-base' else None
    readings=dict(part=row['name'],current_stl_sha256=hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest(),
                  current_watertight=b.is_watertight,current_winding_consistent=b.is_winding_consistent,current_bodies=b.body_count,
                  accepted_bounds_mm=a.bounds.tolist(),current_bounds_mm=b.bounds.tolist(),
                  accepted_volume_mm3=float(a.volume),current_volume_mm3=float(b.volume),comparison_source_z_min_mm=region,
                  accepted_to_current=distances(a,b,region),current_to_accepted=distances(b,a,region))
    rows.append(readings)
    print(row['name'],readings['accepted_to_current']['max_mm'],readings['current_to_accepted']['max_mm'],flush=True)
    (W/'mesh-comparison.json').write_text(json.dumps(dict(accepted_project=acceptance['prepared_project'],accepted_project_sha256=acceptance['prepared_project_sha256'],
                                                       method='Deterministic vertex and face-center samples to the complete opposing triangle surface; two directions; this is a surface sample, not a global Hausdorff bound.',parts=rows),indent=2)+'\n')
