"""Read-only, seated native C14 fit against the already exported printed station."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,time
os.environ['HSM_NO_BUILD_LOCK']='1'
root=Path('/Users/derekbredensteiner/Developer/homesodamachine')
sys.path.insert(0,str(root/'hardware/manifold-layout'))
import cadquery as cq
import enclosure_assembly as ea
enc=ea._enc
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
back=root/'hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step'
paths=[back,ea.C14_STEP,Path(ea.__file__),Path(enc.__file__),Path(enc._c14.__file__)]
inputs={str(p):sha(p) for p in paths}
wall=cq.importers.importStep(str(back)).val();part,carry=ea.build_c14()
common=part.intersect(wall)
origin=carry(((0,0,0),(0,1,0)))[0]
preservation=Path('/tmp/scanner-review/current-hard-contacts/c14-pocket-preservation.json')
preserved=json.loads(preservation.read_text())
report={'scope':'Seated current C14 reference against exact current exported back-top. The physically accepted printed station is preserved; no station redesign or complete insertion-motion claim.',
 'reference_commit':'6d89e8ae5','input_sha256':inputs,
 'station':{'origin_mm':origin,'pocket_floor_y_mm':ea.c14_seat_y(),'rim_face_y_mm':origin[1]+enc._c14.RIM_PROUD,'pocket_depth_mm':enc.c14_pocket_depth,'bore_mm':[enc.c14_bore_w,enc.c14_bore_h,enc.c14_bore_r],'screw_pitch_mm':enc.c14_screw_pitch,'rear_plane_y_mm':enc.rear_plane_y,'rear_boundary_translation_mm':4.3},
 'native':{'inlet_valid':part.isValid(),'wall_valid':wall.isValid(),'overlap_mm3':common.Volume(),'intersection_solids':len(common.Solids())},
 'printed_profile_preservation':{'report_sha256':sha(preservation),'all_pass':preserved['all_pass'],'details':preserved},
 'physical_authority':'Derek reports actual inlet and mating C13 connector fit the prior printed station; that accepted station controls. The full enclosure assembly remains the physical test for new coupled placement.',
 'reproducer_sha256':sha(__file__)}
report['native']['pass']=report['native']['inlet_valid'] and report['native']['wall_valid'] and abs(report['native']['overlap_mm3'])<1e-6
report['stable_inputs']=all(sha(p)==h for p,h in inputs.items())
report['all_pass']=report['native']['pass'] and report['stable_inputs'] and preserved['all_pass']
out=Path('/tmp/scanner-review/current-hard-contacts/c14-frozen-reference-check.json');out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
