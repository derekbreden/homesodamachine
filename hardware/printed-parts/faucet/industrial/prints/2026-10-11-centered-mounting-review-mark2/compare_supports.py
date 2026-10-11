from pathlib import Path
import hashlib,json,sys,xml.etree.ElementTree as ET,zipfile
import numpy as np
import trimesh

ROOT=Path.cwd(); F=ROOT/'hardware/printed-parts/faucet'; W=ROOT/'.cache/printer-control/faucet-current-review-20261011'
W.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(F),str(ROOT/'hardware/scripts')]
import refresh_print_project as writer
from enclosure_support_audit import audit

physical=json.loads((F/'industrial/physical-acceptance.json').read_text())
project=ROOT/physical['prepared_project']; report=json.loads((project.parent/'preparation.json').read_text())
assert hashlib.sha256(project.read_bytes()).hexdigest()==physical['prepared_project_sha256']
with zipfile.ZipFile(ROOT/physical['native_archive']) as z:
 payload=z.read('Metadata/plate_1.gcode')
 assert hashlib.sha256(payload).hexdigest()==physical['gcode_sha256']
 (W/'accepted.gcode').write_bytes(payload)
with zipfile.ZipFile(project) as z: members={n:z.read(n) for n in z.namelist()}
results=[]
for row in report['parts'][:3]:
 # Restore the accepted embedded mesh in its CAD frame without requiring another reader.
 doc=ET.fromstring(members[row['member']]);geo=doc.find(f"{writer.qn('resources')}/{writer.qn('object')}/{writer.qn('mesh')}")
 vs=np.array([[float(v.get(a)) for a in 'xyz'] for v in geo.find(writer.qn('vertices'))])+row['source_center_mm']
 fs=np.array([[int(v.get(a)) for a in ('v1','v2','v3')] for v in geo.find(writer.qn('triangles'))])
 trimesh.Trimesh(vertices=vs,faces=fs,process=True).export(W/(row['name']+'-accepted.stl'))
 one=dict(members);model=ET.fromstring(one['3D/3dmodel.model'])
 for res in list(model.find(writer.qn('resources'))):
  if res.get('id')!=row['object_id']: model.find(writer.qn('resources')).remove(res)
 for item in list(model.find(writer.qn('build'))):
  if item.get('objectid')!=row['object_id']:model.find(writer.qn('build')).remove(item)
 cfg=ET.fromstring(one['Metadata/model_settings.config'])
 for item in list(cfg):
  if item.tag!='object' or item.get('id')!=row['object_id']:cfg.remove(item)
 one['3D/3dmodel.model']=writer.xml(model);one['Metadata/model_settings.config']=writer.xml(cfg)
 coord=W/('accepted-coordinates-'+row['name']+'.3mf');writer.archive_write(coord,one)
 filtered=W/('accepted-support-labels-'+row['name']+'.gcode')
 writer.object_toolpaths(W/'accepted.gcode',filtered,row['identify_id'])
 result=audit(filtered,row['name'],W/(row['name']+'-accepted.stl'),project,coord,profile_label=physical['prepared_project'],include_unlabelled_support=True)
 results.append(result);print(row['name'],result['summary'],flush=True)
 (W/'accepted-support-audit.json').write_text(json.dumps(dict(accepted_project=physical['prepared_project'],accepted_project_sha256=physical['prepared_project_sha256'],native_archive=physical['native_archive'],gcode_sha256=physical['gcode_sha256'],parts=results),indent=2)+'\n')
