from pathlib import Path
import sys,json,hashlib
import cadquery as cq
r=Path.cwd();here=r/'hardware/printed-parts/enclosure/nameplate/horizontal-wing-trial'
job=r/'.cache/prints/2026-09-30-nameplate-y045-receiver-mark2-v9';b=job/'baseline'
sys.path.insert(0,str(here));import wing_interface as fit
name='nameplate-horizontal-wings-receiver.step'
old=cq.importers.importStep(str(b/name)).val();new=cq.importers.importStep(str(here/name)).val()
removed=old.cut(new);added=new.cut(old);h=fit.WIDTH/2
masks=[]
for side in (-1,1):
 xa,xb=sorted((side*(h+fit.FACE_X_AIR),side*(h+fit.PROJECTION+fit.TIP_AIR)))
 masks.append(fit.box(xa,xb,fit.WING_THICK+.30,fit.WING_THICK+fit.THICKNESS_AIR+fit.ENTRY_BEVEL_DEPTH,-fit.WING_SPAN/2-.40,fit.WING_SPAN/2+.15))
outside=removed.cut(masks[0].fuse(masks[1])).Volume()
assert removed.Volume()>1 and added.Volume()<1e-6 and outside<1e-6,(removed.Volume(),added.Volume(),outside)
part=cq.importers.importStep(str(here/'nameplate-horizontal-wings-001.step')).val()
assert part.intersect(new).Volume()<1e-6
checks=[]
for axis,bounds in [('X',(-.35,.35)),('Y',(0.,.45)),('Z',(-.40,.15))]:
 i='XYZ'.index(axis)
 for boundary,sign in zip(bounds,[-1,1]):
  pos=[0.,0.,0.];pos[i]=boundary
  at=abs(part.translate(pos).intersect(new).Volume());pos[i]+=sign*.05
  past=abs(part.translate(pos).intersect(new).Volume())
  assert at<1e-6 and past>.001,(axis,boundary,at,past)
  checks.append({'axis':axis,'boundary_mm':boundary,'overlap_at_boundary_mm3':at,'overlap_0.05_mm_past_boundary_mm3':past})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n in ['nameplate-horizontal-wings-001.step','nameplate-horizontal-wings-001.stl']:assert sha(here/n)==sha(b/n),n
assert fit.THICK-fit.WING_THICK-fit.THICKNESS_AIR>=1.2
record={'pass':True,'comparison':'v8 receiver to v9 wing-Y receiver',
 'removed_volume_mm3':removed.Volume(),'added_volume_mm3':added.Volume(),
 'changes_outside_wing_slot_roofs_and_entry_bevels_mm3':outside,
 'body_X_clearance_per_side_mm':.35,'wing_tip_X_clearance_centered_mm':.45,
 'minimum_tip_gap_at_full_body_X_float_mm':.10,
 'Y_slot_thickness_mm':{'baseline':1.98,'trial':2.13},
 'Y_clearance_total_mm':{'baseline':.30,'trial':.45},'same_seating_floor_Y_mm':0.,
 'Z_end_clearances_mm':[.40,.15],'flat_retaining_lip_thickness_mm':1.23,
 'minimum_retention_overlap_at_full_body_X_float_mm':1.70,
 'minimum_flat_bearing_width_at_full_body_X_float_mm':.80,
 'entry_bevel_Y_shift_mm':.15,'unchanged_entry_bevel_width_and_slope':True,
 'unchanged_nameplate_stl_sha256':sha(here/'nameplate-horizontal-wings-001.stl'),
 'pure_axis_clash_checks':checks,
 'receiver_step_sha256':{'baseline':sha(b/name),'trial':sha(here/name)},
 'scope':'Only the wing-slot Y retaining faces and their entry bevels are relieved. X and Z gaps, seating datum, external stock and existing nameplate are fixed. Printed bow and retention require the physical comparison.'}
(job/'geometry-delta.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
