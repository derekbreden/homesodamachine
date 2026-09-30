from pathlib import Path
import sys,json,hashlib
import cadquery as cq
r=Path.cwd();which=sys.argv[1]
if which=='nameplate':
 here=r/'hardware/printed-parts/enclosure/nameplate/horizontal-wing-trial'
 job=r/'.cache/prints/2026-09-30-nameplate-x015-y045-receiver-mark2-v10'
 sys.path.insert(0,str(here));import wing_interface as fit
 name='nameplate-horizontal-wings-receiver';mate='nameplate-horizontal-wings-001'
 h=fit.WIDTH/2;zh=fit.HEIGHT/2
 masks=[fit.box(-h-.35,h+.35,0,fit.THICK+1,-zh-.40,zh+.15)]
 for side in (-1,1):
  xa,xb=sorted((side*(h+fit.PROJECTION+.25),side*(h+fit.PROJECTION+.45)))
  masks.append(fit.box(xa,xb,0,fit.WING_THICK+.45,-fit.WING_SPAN/2-.40,fit.WING_SPAN/2+.15))
 mask=masks[0].fuse(*masks[1:])
 expected={'body_X_clearance_per_side_mm':{'baseline':.35,'trial':.15},
   'wing_tip_X_clearance_centered_mm':{'baseline':.45,'trial':.25},
   'unchanged_wing_Y_clearance_mm':.45,'unchanged_slot_Y_opening_mm':2.13,
   'unchanged_flat_lip_stock_mm':1.23,'wing_tip_gap_at_body_limit_mm':.10,
   'minimum_capture_mm':2.10,'minimum_flat_bearing_mm':1.00,
   'scope':'Only the latest body-X and matching wing-tip-X increments are undone. Wing Y clearance, Z gaps, seating floor, bevel planes and existing nameplate are fixed.'}
 assert fit.FACE_X_AIR==.15 and fit.TIP_AIR==.25 and fit.THICKNESS_AIR==.45
else:
 here=r/'hardware/printed-parts/enclosure/display-cover/face-up-trial'
 job=r/'.cache/prints/2026-09-30-display-x030-receiver-h2c-v5'
 sys.path.insert(0,str(here));import face_up_trial as fit
 name=fit.RECEIVER;mate=fit.NAME;h=fit.cover.cover_x/2;yh=fit.cover.cover_slope/2
 mask=fit.box(-h-.50,h+.50,-yh-fit.FACE_Y_AIR,yh+fit.FACE_Y_AIR,fit.BACK,1)
 mask=mask.rotate((0,0,0),(1,0,0),fit.ANGLE).translate((0,0,-fit.BASE_Z))
 expected={'body_X_clearance_per_side_mm':{'baseline':.50,'trial':.30},
   'unchanged_wing_tip_X_clearance_centered_mm':.55,
   'unchanged_wing_thickness_clearance_mm':fit.BEARING_AIR,
   'wing_thickness_axis':'Display local Z, corresponding to nameplate Y',
   'unchanged_retaining_lip_stock_mm':fit.LIP_THICK,'wing_tip_gap_at_body_limit_mm':.25,
   'minimum_capture_mm':3.00,
   'scope':'Only the latest main-body X increment is undone through full seating depth. Wing pockets, thickness gap, support exits, seating datums and existing cover are fixed.'}
 assert fit.FACE_X_AIR==.30 and fit.TIP_AIR==.55 and abs(fit.BEARING_AIR-.60)<1e-6
b=job/'baseline';old=cq.importers.importStep(str(b/(name+'.step'))).val();new=cq.importers.importStep(str(here/(name+'.step'))).val()
added=new.cut(old);removed=old.cut(new);outside=added.cut(mask).Volume()
assert added.Volume()>1 and removed.Volume()<1e-6 and outside<1e-6,(added.Volume(),removed.Volume(),outside)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for suffix in ('.step','.stl'):assert sha(here/(mate+suffix))==sha(b/(mate+suffix))
checks=[]
if which=='nameplate':
 part=cq.importers.importStep(str(here/(mate+'.step'))).val()
 for axis,bounds in [('X',(-.15,.15)),('Y',(0.,.45)),('Z',(-.40,.15))]:
  i='XYZ'.index(axis)
  for boundary,sign in zip(bounds,[-1,1]):
   pos=[0.,0.,0.];pos[i]=boundary
   at=abs(part.translate(pos).intersect(new).Volume());pos[i]+=sign*.05
   past=abs(part.translate(pos).intersect(new).Volume())
   assert at<1e-6 and past>.001,(axis,boundary,at,past)
   checks.append({'axis':axis,'boundary_mm':boundary,'overlap_at_boundary_mm3':at,'overlap_0.05_mm_past_boundary_mm3':past})
record={'pass':True,'added_volume_mm3':added.Volume(),'removed_volume_mm3':removed.Volume(),
 'added_outside_reverted_X_openings_mm3':outside,'existing_mate_stl_sha256':sha(here/(mate+'.stl')),
 'receiver_step_sha256':{'baseline':sha(b/(name+'.step')),'trial':sha(here/(name+'.step'))},
 'pure_axis_clash_checks':checks,**expected}
(job/'geometry-delta.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
