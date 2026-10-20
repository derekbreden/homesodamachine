from pathlib import Path
import sys,json,zipfile,shutil,hashlib
import trimesh,numpy as np
root=Path.cwd();out=root/'tmp/funnel-runoff/corner-slice';models=out/'models';models.mkdir(parents=True,exist_ok=True)
source=root/'hardware/printed-parts/zone-c/funnel-mold/cavity.stl'
mesh=trimesh.load(source,force='mesh',process=True)
rotation=np.array([[0.,-1.,0.,0.],[1.,0.,0.,0.],[0.,0.,1.,0.],[0.,0.,0.,1.]])
mesh.apply_transform(rotation);mesh.export(models/'cavity.stl')
shutil.copy2(root/'hardware/printed-parts/zone-c/funnel-mold/design.json',models/'design.json')
sys.path.insert(0,str(root/'tools/funnel-mold-print'))
import prepare_print
project=out/'cavity-inspection.3mf'
sys.argv=['prepare_print.py','--models',str(models),'--output',str(project),'--nozzle','0.4','--z-trim','0.04','--only','cavity']
prepare_print.main()
recipe=root/'hardware/printed-parts/zone-c/funnel-mold/native-slice-reviews/2026-10-06-mark1-retry-z004-v2/funnel-mold-mark1-retry-z004.3mf'
with zipfile.ZipFile(recipe) as z:settings=z.read('Metadata/project_settings.config')
with zipfile.ZipFile(project) as z:payload={n:z.read(n) for n in z.namelist()}
payload['Metadata/project_settings.config']=settings
with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in payload.items():z.writestr(name,data)
record={'purpose':'Inspect model filament paths at the remaining small forming corner; no printer submission or full production readiness claim.','cavity_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_to_slice_rotation':rotation.tolist(),'settings_source':str(recipe.relative_to(root)),'settings_source_sha256':hashlib.sha256(recipe.read_bytes()).hexdigest(),'project_settings_sha256':hashlib.sha256(settings).hexdigest(),'project_sha256':hashlib.sha256(project.read_bytes()).hexdigest()}
(out/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
print(project)
