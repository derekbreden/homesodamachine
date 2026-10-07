"""Native cavity sweep for aft-only funnel expansion; canonical geometry stays untouched."""
from pathlib import Path
import json,sys,math
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel')]
import cadquery as cq
import funnel as f
OUT=Path(__file__).parent
base_depth=f.collar_d
base_centre=182.5-f.forward_extension/2
rows=[]
for extra in (0,60):
 d=base_depth+extra; cy=base_centre+extra/2; neck_dy=-extra/2
 w=f.collar_w-2*f.collar_wall
 bore_d=d-2*f.collar_wall
 top_z=f.brim_thickness; ramp_top_z=top_z-f.chute_h
 neck_z=ramp_top_z-f._ramp_rise
 end_z=-f.drop+f.plug_lift
 ramp=f._loft_rc(w,bore_d,0,0,ramp_top_z,f.spout_id/2,f.neck_dx,neck_dy,neck_z,f.mouth_corner_r)
 collar=f._rounded_box(w,bore_d,f.mouth_corner_r,ramp_top_z,top_z,0,0)
 outlet=f._cyl(f.spout_id/2,neck_z,end_z,f.neck_dx,neck_dy)
 cavity=ramp.fuse(collar).fuse(outlet).clean()
 ml=cavity.Volume(tol=1e-9)/1000
 # Level 10 mm below the brim leaves pouring/cover headroom.
 usable=cavity.intersect(f._box(1000,1000,end_z,top_z-10,0,0)).Volume(tol=1e-9)/1000
 run_x=w/2-f.spout_id/2+abs(f.neck_dx)
 run_y=bore_d/2-f.spout_id/2+abs(neck_dy)
 rows.append(dict(aft_extension_mm=extra,capacity_to_brim_ml=ml,capacity_10mm_below_brim_ml=usable,
 collar_width_mm=f.collar_w,collar_depth_mm=d,mouth_width_mm=w,mouth_depth_mm=bore_d,
 collar_centre_world_mm=[0,cy,349],neck_local_mm=[f.neck_dx,neck_dy,end_z],drain_world_mm=[f.neck_dx,cy+neck_dy,349+end_z],
 brim_y_world_mm=[cy-d/2-f.brim_overhang,cy+d/2+f.brim_overhang],
 frame_front_world_y_mm=95.45849207671873,frame_rear_world_y_mm=cy+(d+24.6)/2,
 full_width_corbel_foot_world_y_mm=[119.1,210+extra],
 longest_axis_floor_run_mm=max(run_x,run_y),longest_axis_ramp_grade_deg=math.degrees(math.atan2(f._ramp_rise,max(run_x,run_y))),
 method='OCCT native integration of the actual rounded mouth, lofted ramp and outlet, bounded at actual brim and drain planes. Geometric capacity only.'))
 print(extra,round(ml,3),round(usable,3),flush=True)
for r in rows:
 r['capacity_gain_ml']=r['capacity_to_brim_ml']-rows[0]['capacity_to_brim_ml']
 r['capacity_gain_percent']=100*(r['capacity_to_brim_ml']/rows[0]['capacity_to_brim_ml']-1)
(OUT/'capacity-sweep.json').write_text(json.dumps(dict(rows=rows),indent=2)+'\n')
