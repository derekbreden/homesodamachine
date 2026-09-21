"""Read-only exact native equality of accepted pre-scan and current printed C14 pocket."""
from pathlib import Path
import ast, hashlib, json, math, os, subprocess, sys
os.environ['HSM_NO_BUILD_LOCK']='1'
ROOT=Path('/Users/derekbredensteiner/Developer/homesodamachine')
sys.path.insert(0,str(ROOT/'hardware/printed-parts/cadlib'))
import cadquery as cq
from world_workplane import xz_plane_y_up
old_commit=subprocess.check_output(['git','rev-parse','fbdb1f06e^'],cwd=ROOT,text=True).strip()
ref_rel='hardware/reference/iec-c14-inlet/iec_c14_inlet.py'
enc_rel='hardware/printed-parts/enclosure/enclosure/enclosure.py'
old_ref=subprocess.check_output(['git','show',old_commit+':'+ref_rel],cwd=ROOT,text=True)
old_enc=subprocess.check_output(['git','show',old_commit+':'+enc_rel],cwd=ROOT,text=True)
new_enc=(ROOT/enc_rel).read_text()
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def subset(src,variables,functions):
 tree=ast.parse(src)
 nodes=[]
 for n in tree.body:
  names=set()
  if isinstance(n,(ast.Assign,ast.AnnAssign)):
   targets=n.targets if isinstance(n,ast.Assign) else [n.target]
   names={x.id for t in targets for x in ast.walk(t) if isinstance(x,ast.Name)}
  if names & set(variables) or isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name in functions:nodes.append(n)
 env={'cq':cq,'math':math,'xz_plane_y_up':xz_plane_y_up}
 exec(compile(ast.Module(body=nodes,type_ignores=[]),'<frozen-profile>','exec'),env)
 return env
old=subset(old_ref,('FLANGE_W','FLANGE_H','FLANGE_END_CHORD','SCREW_PITCH','EAR_R','FLANGE_SHOULDER_X','FLANGE_KNUCKLE_R','FLANGE_T'),('_flange_landmarks','flange_profile','flange_prism'))
new=subset(new_enc,('c14_pocket_w','c14_pocket_h','c14_pocket_end_chord','c14_pocket_knuckle_r','c14_screw_pitch','c14_pocket_depth'),('_c14_pocket_landmarks','c14_pocket_profile','c14_pocket_prism'))
report={'scope':'Exact native printed-pocket profile equality; live C14 reference is neither imported nor tested.',
 'baseline_git_commit':old_commit,'baseline_reference_sha256':digest(old_ref),'baseline_enclosure_sha256':digest(old_enc),
 'current_enclosure_sha256':digest(new_enc),'clearances':[],
 'physical_authority':'Derek reports the printed C14 station fits the actual inlet and mating C13 connector. This check does not reconsider that physical acceptance.'}
for clearance in (0,.15,3.15):
 a=old['flange_prism'](clearance,0,5).val();b=new['c14_pocket_prism'](clearance,0,5).val()
 added=b.cut(a).Volume();missing=a.cut(b).Volume()
 row={'offset_mm':clearance,'depth_mm':5,'old_volume_mm3':a.Volume(),'current_volume_mm3':b.Volume(),'added_mm3':added,'missing_mm3':missing,'pass':abs(added)<1e-8 and abs(missing)<1e-8}
 report['clearances'].append(row);print(json.dumps(row),flush=True)
old_lip=subset(old_enc,('c14_pocket_lip',),())['c14_pocket_lip']
report['depth']={'old_flange_plus_lip_mm':old['FLANGE_T']+old_lip,'current_mm':new['c14_pocket_depth'],'pass':old['FLANGE_T']+old_lip==new['c14_pocket_depth']}
report['landmarks_equal']=old['_flange_landmarks']()==new['_c14_pocket_landmarks']()
report['all_pass']=all(x['pass'] for x in report['clearances']) and report['depth']['pass'] and report['landmarks_equal']
report['stable_current_source']=digest((ROOT/enc_rel).read_text())==report['current_enclosure_sha256']
report['reproducer_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
out=Path('/tmp/scanner-review/current-hard-contacts/c14-pocket-preservation.json');out.write_text(json.dumps(report,indent=2)+'\n')
print('PASS' if report['all_pass'] and report['stable_current_source'] else 'FAIL',str(out),flush=True)
