"""Check exported solids, mesh fidelity, millimetre datums, and artifact hashes."""
import gzip,io,json,hashlib
import numpy as np,trimesh,cadquery as cq
from scipy.spatial import cKDTree
from scan_tools import HERE, observations, material_mask

p=HERE
points,_,height=observations();cloud=points[material_mask(points,height)]
mesh=trimesh.load(io.BytesIO(gzip.decompress((p/'observed-surface.ply.gz').read_bytes())),file_type='ply',process=False)
dist=cKDTree(cloud).query(mesh.vertices[::8])[0]
assert np.quantile(dist,.99)<.02 and max(dist)<.06
shape=cq.importers.importStep(str(p/'jg-pp0308e-elbow.step')).val();solids=shape.Solids();bb=shape.BoundingBox()
assert len(solids)==3 and all(s.isValid() for s in solids)
assert abs(bb.ymax-20.56239)<1e-6 and abs(bb.zmax-20.56239)<1e-6
for i in range(3):
    for j in range(i):
        assert solids[i].intersect(solids[j]).Volume()<1e-6
bounds=np.array([[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]])
stl=trimesh.load(p/'jg-pp0308e-elbow.stl')
# A tessellated circle need not have a vertex at the exact analytic extremum.
assert np.max(abs(stl.bounds-bounds))<.025
result={'units':'mm','valid_step_solids':3,'component_overlap_volume_mm3':0,
        'bounding_box_mm':bounds.tolist(),'stl_max_bound_difference_mm':float(np.max(abs(stl.bounds-bounds))),
        'observed_mesh_vertices':len(mesh.vertices),'observed_mesh_triangles':len(mesh.faces),
        'observed_mesh_watertight':bool(mesh.is_watertight),
        'sampled_mesh_vertex_to_source_cloud_p95_p99_max_mm':np.quantile(dist,[.95,.99,1]).tolist(),
        'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.iterdir()) if f.suffix in ('.step','.stl','.gz')}}
(p/'artifact-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
