"""Read-only native feasibility probes for generic PSU installation clearances.

None of these exploratory poses changes the selected layout or its routes.
The ten-millimetre test is an insulation-distance spatial proxy, not a cooling
or electrical-safety qualification. Mounts and flexible wiring need regeneration
for a different pose; the installed large fluid exteriors remain fixed.
"""
from pathlib import Path
from io import BytesIO
import json,hashlib,sys
import cadquery as cq
H=Path(__file__).resolve().parent;S=H.parent;R=S.parents[1];sys.path[:0]=[str(S),str(H)]
import audit,baseline,evidence_binding
sources={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in
 [Path(__file__),S/'audit.py',S/'baseline.py',S/'evidence_binding.py']}
models,records,_,_,inputs=audit.collect()
content_inputs=dict(inputs.content_sha256)
for relative in ['routing/co2-candidate.json','mounts/needle-candidate.json','mounts/wr-candidate.json','mounts/check-tee-candidate.json','mounts/fluid-candidate.json',
                 'wiring/power-candidate.json','wiring/controls-candidate.json','wiring/control-reserves.json','wiring/control-fanouts-check.json','wiring/lower-lead-exits.json']:
 path=S/relative;raw=path.read_bytes();data=json.loads(raw)
 inputs[str(path.relative_to(R))]=hashlib.sha256(raw).hexdigest()
 content_inputs[str(path.relative_to(R))]=evidence_binding.content_sha256(data)
 for n,r in data.get('parts',{}).items():records[n]=r;models[n]=cq.Shape.importBrep(str(R/r['brep']))
routing_raw=(H/'candidate.json').read_bytes();routing=json.loads(routing_raw)
inputs[str((H/'candidate.json').relative_to(R))]=hashlib.sha256(routing_raw).hexdigest()
content_inputs[str((H/'candidate.json').relative_to(R))]=evidence_binding.content_sha256(routing)
for field in ['new_receiver','new_backing']:
 r=routing['interface_moves']['nameplate'][field];records['nameplate-'+field]=r;models['nameplate-'+field]=cq.Shape.importBrep(str(R/r['brep']))
# Optimistic space: mounts/wires/small modules may be redesigned for another
# pose. The scanned pump and complete large pipes/sleeves cannot be moved here.
native_inputs={}
for n,r in records.items():
 if n not in models or not r or not r.get('brep'):continue
 raw=(R/r['brep']).read_bytes()
 models[n]=cq.Shape.importBrep(BytesIO(raw))
 native_inputs[n]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
keep={n:q for n,q in models.items()if n=='g-ganen-pump'or n=='pcba'or n=='c14-inlet'or n=='digiten-flow'or n.startswith(('tube-','carb-foam-','bulkhead-','union-','nameplate-','valve-v-','relay-','co2-'))or n in ['asse1022-assembly','wr1110','gasher-co2','flow-regulator','water-split']}
source=models['psu']
def posed(axis,x,y,z,yaw=0):
 q=source
 if axis=='backwall':q=q.rotate((0,0,0),(1,0,0),90)
 elif axis=='sidewall':q=q.rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(0,1,0),90)
 if yaw:q=q.rotate((0,0,0),(0,0,1),yaw)
 b=audit.bbox(q);return q.translate((x-b[0],y-b[1],z-b[2]))
configs=[('selected','flat',-45,411.3,289.75,0),
 ('flat-fore8-low3.05','flat',-45,403.3,286.7,0),
 ('flat-fore8-west3-low3.05','flat',-48,403.3,286.7,0),
 ('flat-fore8-low9.75','flat',-45,403.3,280,0),
 ('flat-fore8-low17','flat',-45,403.3,272.8,0),
 ('flat-fore8-east2','flat',-43,403.3,289.75,0),
 ('flat-east-column-10','flat',-53.975,403.3,289.75,0),
 ('backwall-centred-high','backwall',-54.5,421.8,289.75,0),
 ('backwall-west45-high','backwall',-45,421.8,289.75,0),
 ('backwall-clear-C14-x','backwall',-36.215,421.8,289.75,0),
 ('backwall-low','backwall',-45,421.8,275,0),
 ('backwall-fore10-low','backwall',-45,411.8,275,0),
 ('backwall-base5-centred','backwall',-54.5,426.8,263.4,0),
 ('backwall-base5-west','backwall',-75,426.8,263.4,0),
 ('backwall-base5-east','backwall',-25,426.8,263.4,0),
 ('backwall-base5-above-flavors','backwall',-54.5,426.8,290,0),
 ('backwall-yaw15','backwall',-45,397,289.75,15),
 ('backwall-yawminus15','backwall',-45,397,289.75,-15),
 ('westwall-high','sidewall',-88.5,346.3,289.75,0),
 ('eastwall-high','sidewall',55,346.3,289.75,0)]
results=[]
for name,axis,x,y,z,yaw in configs:
 q=posed(axis,x,y,z,yaw);b=audit.bbox(q);rows=[]
 for n,s in keep.items():
  if n=='pcba':continue
  if not audit.broad(b,audit.bbox(s),10):continue
  d=q.distance(s)
  if d>=10-1e-5:continue
  v=audit.common(q,s)if d<1e-6 else 0
  rows.append({'part':n,'air_mm':d,'common_mm3':v})
 rows.sort(key=lambda r:(r['air_mm'],-r['common_mm3']))
 pcb_options=[]
 for dy in [0,-6,-12,-18]:
  pcb=keep['pcba'].translate((0,dy,0));pcb_options.append({'controller_y_shift_mm':dy,'supply_air_mm':q.distance(pcb),'common_mm3':audit.common(q,pcb)if q.distance(pcb)<1e-6 else 0})
 wall={'west_air_mm':b[0]+98.5,'east_air_mm':98.5-b[3],'rear_air_mm':465.3-b[4],
       'ceiling_air_mm_optimistic_local_pocket':352-b[5],'lid_air_mm':b[2]-253.4}
 under_field='rear_air_mm'if axis=='backwall'else'west_air_mm'if axis=='sidewall'else'lid_air_mm'
 row={'name':name,'orientation':axis,'bounds_mm':b,'wall_plane_air':wall,
      'under_unit_mount_base_field':under_field,'under_unit_minimum_5mm':wall[under_field]>=5-1e-5,
      'surround_10mm_to_planes_optimistic':min(wall[k]for k in wall if k!=under_field)>=10-1e-5,
      'fixed_large_package_under10mm':rows,'controller_probes':pcb_options,
      'valid':q.isValid(),'geometry_overlap_parts':[r['part']for r in rows if r['common_mm3']>.001]}
 results.append(row);print(json.dumps(row),flush=True)
drift=['native:'+n for n,r in native_inputs.items()if hashlib.sha256((R/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
drift+=['source:'+p for p,h in sources.items()if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
drift+=['manifest-content:'+p for p,h in content_inputs.items()if evidence_binding.manifest_content_sha256(R/p)!=h]
report={'pass':False,'scope':'Limited read-only alternatives; no selected geometry is changed and no global impossibility is established. Optimistic local ceiling assumes a 3 mm roof skin at Z355. Generic 10 mm guidance is insulation distance, not sufficient ventilation proof. Actual mounting orientation, Mylar/insulation, derating, enclosure ventilation and applicable safety requirements require separate design evidence. Complete current controls, power and hosts are bound as scene provenance; the printed mounts and flexible wiring may be redesigned for an alternative pose, and only the named fixed obstacle set is used by the spatial probes.',
 'manufacturer_sources':['https://www.meanwell.com/Upload/PDF/PCB_EN.pdf','https://www.meanwell.com/Upload/PDF/IRM-90/IRM-90-spec.pdf'],
 'barrier_review':{
  'manufacturer_condition_satisfied':False,
  'primary_instruction':'The official PCB installation manual includes IRM and requires a base Mylar film in addition to5mm base spacing, plus10mm surrounding insulation distance for general supplies.',
  'supported_barrier_exception_found':False,
  'finding':'The reviewed manufacturer manual and IRM90 specification provide no exception allowing an added thin barrier to substitute for the stated surrounding distance. Encapsulation and ClassII isolation do not independently prove this proposed installation complies.',
  'selected_pose_status':'Open installation qualification; no insulating barrier or selected-pose change is authored by this limited study.',
  'source':'https://www.meanwell.com/Upload/PDF/PCB_EN.pdf'},
 'selected_native_inputs':native_inputs,'native_inputs':native_inputs,'source_inputs':sources,
 'manifests_sha256':dict(inputs),'manifest_content_sha256':content_inputs,
 'source_drift':drift,'source_binding_pass':not drift,'fixed_probe_obstacles':sorted(keep),'probes':results}
(H/'psu-surround-feasibility.json').write_text(json.dumps(report,indent=2)+'\n')
