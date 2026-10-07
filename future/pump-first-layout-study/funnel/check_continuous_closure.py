"""Continuous native bounding-prism proof for the selected frame closing stroke."""
from pathlib import Path
import hashlib,json
import cadquery as cq
from frame_stock import selected_frame

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 funnel=json.loads((HERE/'candidate.json').read_text());pump=json.loads((HERE.parent/'pump/candidate.json').read_text())
 frame,frame_record=selected_frame(funnel);frame_path=ROOT/frame_record['brep'];travel=funnel['underframe_reliefs']['closure_travel_mm']
 checks=[];inputs={str(frame_path.relative_to(ROOT)):digest(frame_path)}
 for name in ['vk-solenoid','vk-cradle']:
  path=ROOT/pump['parts'][name]['brep'];part=cq.Shape.importBrep(str(path));b=part.BoundingBox()
  prism=cq.Solid.makeBox(b.xlen,b.ylen+travel,b.zlen,cq.Vector(b.xmin,b.ymin,b.zmin))
  common=abs(frame.intersect(prism,tol=.0001).Volume(tol=1e-9));gap=frame.distance(prism)
  checks.append({'part':name,'continuous_frame_fore_of_home_range_mm':[0,travel],'conservative_swept_region':'Complete native bounding box swept continuously aft relative to the seated frame',
   'common_mm3':common,'gap_mm':gap,'pass':common<.001 and gap>=.9999});inputs[str(path.relative_to(ROOT))]=digest(path)
 report={'checks':checks,'inputs_sha256':inputs,'pass':all(r['pass'] for r in checks),
  'source_sha256':{str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))},
  'scope':f'Each static body remains within its native bounding box. Its complete relative{travel:g}mm translation remains within the tested continuous prism. Thus all intermediate front-top/frame closing poses preserve at least1mm air, without relying on sample spacing. No load or tolerance qualification is inferred.'}
 (HERE/'frame-continuous-closure-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
