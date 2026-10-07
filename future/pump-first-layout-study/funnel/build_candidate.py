"""Generate aft-only funnel, frame and lid without editing the production parts.

The front edge and drain stay fixed. Dimensions import the production sources,
then only this process's collar/neck and matching removable-part parameters vary.
Exported B-reps are installed world coordinates. The source and manifest are the
reproducible artifact; the cache contains disposable exact solids and mesh files.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys,time
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel'),
             str(ROOT/'hardware/printed-parts/zone-c/funnel-cover')]
import cadquery as cq
from cadquery.occ_impl.shapes import fuse as fuse_shapes, cut as cut_shapes
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
import funnel as f
import funnel_frame as ff
import layout_funnel

def bounds(s):
 b=Bnd_Box()
 BRepBndLib.AddOptimal_s(s.wrapped,b,False,False)
 return list(b.Get())

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def mesh_data(s):
 vertices,triangles=s.tessellate(.12,.08)
 return {'vertices':[[v.x,v.y,v.z] for v in vertices], 'triangles':[list(t) for t in triangles]}

def main():
 p=argparse.ArgumentParser();p.add_argument('--aft',type=float);p.add_argument('--preview-only',action='store_true');a=p.parse_args()
 extra=a.aft if a.aft is not None else json.loads((HERE/'candidate.json').read_text())['aft_extension_mm'] if (HERE/'candidate.json').exists() else 90.0
 out=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'
 out.mkdir(parents=True,exist_ok=True)
 original_depth=f.collar_d; original_cy=ff.center_y
 cy=original_cy+extra/2
 f.collar_d=original_depth+extra;f.neck_dy=-extra/2
 ff.center_y=cy;ff.depth=f.collar_d+24.6
 ff.corbel_foot_half_depth+=extra/2
 f.build_solids=layout_funnel.build_solids
 ff.forming_clearance.cache_clear();ff.build.cache_clear()
 print('Creating native silicone and cavity',flush=True)
 outer,cavity,meta=f.build_solids()
 f.capacity_ml=cavity.intersect(f._box(1000,1000,meta['end_z'],meta['top_z'],0,0)).Volume(tol=1e-9)/1000
 silicone=cut_shapes(outer,cavity,tol=.0001).clean().translate((0,cy,349))
 filled=cavity.intersect(f._box(1000,1000,meta['end_z'],meta['top_z'],0,0)).translate((0,cy,349))
 usable=filled.intersect(f._box(1000,1000,306.05,345,0,cy))
 print('Creating native frame',f.capacity_ml,flush=True)
 inner=(-104.5,104.5,14,468.3,0,352)
 frame=ff.build(inner,200,(0,cy),349)
 print('Creating native lift-off lid',flush=True)
 import funnel_cover as cover
 lid=cover.placed(0,cy,355)
 native={'funnel':silicone,'funnel-frame':frame,'funnel-cover':lid,'funnel-liquid-capacity':filled}
 records={}
 for name,s in native.items():
  assert s.isValid() and len(s.Solids())==1,(name,s.isValid(),len(s.Solids()))
  brep=out/f'{name}.brep';s.exportBrep(str(brep))
  step=out/f'{name}.step';cq.exporters.export(s,str(step))
  mesh=out/f'{name}.json';mesh.write_text(json.dumps(mesh_data(s),separators=(',',':'))+'\n')
  records[name]=dict(valid=True,solids=1,bounds_world_mm=bounds(s),volume_mm3=s.Volume(tol=1e-9),
   brep=str(brep.relative_to(ROOT)),step=str(step.relative_to(ROOT)),mesh=str(mesh.relative_to(ROOT)),
   sha256={str(x.relative_to(ROOT)):digest(x) for x in (brep,step,mesh)})
  print('exported',name,flush=True)
 brim=f._rounded_box(f.collar_w+2*f.brim_overhang,f.collar_d+2*f.brim_overhang,
                      f.brim_corner_r,346,349,0,cy)
 collar=f._rounded_box(f.collar_w+.6,f.collar_d+.6,f.collar_corner_r+.3,345,350,0,cy)
 bearing=brim.cut(collar)
 missing=bearing.cut(frame).Volume(tol=1e-9)
 print('bearing missing mm3',missing,flush=True)
 assert abs(missing)<.0001,missing
 roof=ff.roof_datums(inner,(0,cy),349,200)
 # A constant-offset flange has the silicone brim's corner centres.
 mold_w=f.collar_w+2*f.brim_overhang+32
 mold_d=f.collar_d+2*f.brim_overhang+32
 mold_r=f.brim_corner_r+16
 mold_diam=2*(math.hypot(mold_w/2-mold_r,mold_d/2-mold_r)+mold_r)
 longest=max((f.collar_w-12)/2-3+abs(f.neck_dx),
             (f.collar_d-12)/2-3+abs(f.neck_dy))
 floor_wet,floor_dry=layout_funnel.floor_surfaces()
 floor_wall=floor_wet.distance(floor_dry)
 assert floor_wall>=6.0,floor_wall
 source=[Path(__file__),Path(layout_funnel.__file__),Path(f.__file__),Path(ff.__file__),Path(cover.__file__),
         ROOT/'hardware/printed-parts/zone-c/funnel/elbow_cradle.py']
 result=dict(aft_extension_mm=extra,capacity_to_brim_ml=filled.Volume(tol=1e-9)/1000,
  capacity_10mm_below_brim_ml=usable.Volume(tol=1e-9)/1000,
  capacity_method='OCCT native cavity Boolean bounded at actual brim and drain planes; 10 mm headroom slice also measured.',
  collar_dimensions_mm=[f.collar_w,f.collar_d],mouth_dimensions_mm=[f.collar_w-12,f.collar_d-12],
  collar_centre_world_mm=[0,cy,349],drain_world_mm=[f.neck_dx,cy+f.neck_dy,349+meta['end_z']],
  source_sha256={str(x.relative_to(ROOT)):digest(x) for x in source},parts=records,
  roof=dict(roof,complete_brim_bearing_missing_mm3=missing,complete_brim_bearing_volume_mm3=bearing.Volume(tol=1e-9)),
  retained=dict(display_face_y_mm=95.20849207671873,frame_front_y_mm=95.45849207671873,
    display_running_air_mm=.25,frame_underside_z_mm=299.9,socket_floor_z_mm=302.9,
    rail_z_mm=306.9,rail_top_z_mm=321.7,silicone_brim_seat_z_mm=349,brim_top_z_mm=355,
    socket_width_mm=36.6,silicone_plug_width_mm=36,drain_bore_mm=6,drain_stub_od_mm=6.35,
    drain_stub_engagement_mm=f.stub_engagement,frame_web_mm=3,
    complete_front_corbel_foot_y_mm=119.1,complete_rear_corbel_foot_y_mm=210+extra),
  ramp=dict(rise_mm=f._ramp_rise,longest_axis_run_mm=longest,
     longest_axis_ramp_grade_deg=math.degrees(math.atan2(f._ramp_rise,longest)),
     required_minimum_wall_mm=6,vertical_floor_stock_mm=6.6,minimum_native_ramp_wall_mm=floor_wall,
     wall_method='OCCT minimum distance between the actual wet-ramp and dry-ramp lateral faces. The side collar retains 6 mm.'),
  tooling_screen=dict(flange_plan_mm=[mold_w,mold_d],flange_corner_radius_mm=mold_r,
    enclosing_circle_mm=mold_diam,chamber_interior_diameter_mm=299.72,
    radial_clearance_mm=(299.72-mold_diam)/2,
    detail=f'Constant16mm offset flange followsR27 silicone brim withR43corners. Existing bolt stations remain on straight flank sections. The companion candidate-aft-{extra:g}-tooling.json records derived native mold closure, release, backing, passages and rod checks; chamber insertion and physical casting are unqualified.'),
  scope='Layout-study solids only. Exact seated silicone, frame, lid and cavity are generated; manufacturing fit, retained hardware clearances, motion, material strength and life are not established by this file.')
 (HERE/f'candidate-aft-{extra:g}.json').write_text(json.dumps(result,indent=2)+'\n')
 details={
  'funnel':f'Aft-only rounded mouth; drain and display edge retained. Native cavity capacity {result["capacity_to_brim_ml"]:.3f} mL; floor has measured {floor_wall:.3f} mm minimum stock.',
  'funnel-frame':'One native PET-GF solid with complete 3 mm brim bearing, production sliding rails/socket and full-width 30-degree corbels.',
  'funnel-cover':'Native lift-off 3 mm plate, locating skirt and four silicone friction pads; front lifting edge retained.'}
 result['capacity_artifact']=records['funnel-liquid-capacity']
 result['parts']={name:dict(record,role='structure' if name=='funnel-frame' else 'funnel',detail=details[name])
                  for name,record in records.items() if name!='funnel-liquid-capacity'}
 result['replacement_names']=['funnel','funnel-frame','funnel-cover']
 # Alternatives remain separately inspectable without changing the selected
 # installed manifest or its frozen native frame/motion evidence.
 if not a.preview_only:(HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
 (HERE/f'candidate-aft-{extra:g}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('aft_extension_mm','capacity_to_brim_ml','capacity_10mm_below_brim_ml','drain_world_mm','tooling_screen')},indent=2),flush=True)

if __name__=='__main__':main()
