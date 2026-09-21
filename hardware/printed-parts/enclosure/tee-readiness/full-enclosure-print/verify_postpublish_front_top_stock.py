"""Read-only local stock witnesses for the published front-top lint faces. Run from repository root."""
from pathlib import Path
import cadquery as cq,json,hashlib,time
root=Path.cwd(); part=root/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step'
wall=cq.importers.importStep(str(part)).val()
r={'step_sha256':hashlib.sha256(part.read_bytes()).hexdigest(),'probes':[],'faces':[]}
def box(b):
 x0,x1,y0,y1,z0,z1=b
 return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))
for side in (-1,1):
 for name,b in [
  ('outer-valve shallow side recess backing',(99.851,107.49,117.541,121.239,236.5,268.3)),
  ('outer-well land continuous wall root',(98.51,104.49,99.45,119.73,229.63,235.915)),
  ('carrier floor exposed end full backing',(83.251,93.249,93.837,94.039,160.01,166.91)),
  ('aft valve tray end full plate root',(98.6,104.4,172.10,181.28,180.81,181.25))]:
  if side<0:b=(-b[1],-b[0],*b[2:])
  q=box(b); v=q.cut(wall).Volume()
  r['probes'].append({'name':name,'side':side,'bounds_mm':b,'expected_stock_mm3':q.Volume(),'missing_stock_mm3':v,'pass':v<1e-5})
  print(r['probes'][-1],flush=True)
anchors=[(99.175,121.24,252.425),(99.175,117.54,252.425),(97.715,109.59,235.925),(97.715,119.74,232.772),(93.25,93.938,163.462)]
for a in anchors:
 vv=cq.Vertex.makeVertex(*a); rows=[]
 for f in wall.Faces():
  bb=f.BoundingBox()
  if all(lo-.01<=v<=hi+.01 for v,lo,hi in zip(a,[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax])):
   dist=f.distance(vv)
   if dist<.05:rows.append({'area_mm2':f.Area(),'bounds_mm':[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax],'distance_mm':dist})
 r['faces'].append({'anchor':a,'faces':rows})
out=root/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/postpublish-front-top-stock-check.json'
r['scope']='Read-only native full-stock probes for newly exposed narrow front-top lint faces; no shape changes or stiffness claim.'
out.write_text(json.dumps(r,indent=2)+'\n')
print('saved',out,flush=True)
