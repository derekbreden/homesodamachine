"""Derive R43 tooling for the larger funnel, retaining the original 16 mm flange margin."""
from pathlib import Path
import hashlib,json,math,sys
ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts/_cadq_export.py').exists())
HERE=Path(__file__).parent
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/zone-c/funnel'),
             str(ROOT/'hardware/printed-parts/zone-c/funnel-mold')]
import cadquery as cq
import funnel as f
from study_configuration import configuration
extra,preview,candidate=configuration()
f.collar_d+=extra;f.neck_dy=-extra/2
import layout_funnel
f.build_solids=layout_funnel.build_solids
import funnel_mold as m
m.flange_radius=f.brim_corner_r+m.flange_margin
original_expanded=m.expanded
def studied_backing(shape,distance):
 if len(shape.Faces())==11 and distance>6:
  return layout_funnel.backing_envelope(shape,distance)
 if distance>5 and shape.BoundingBox().zmin>=-.0001:
  return f._rounded_box(f.collar_w+2*(f.brim_overhang+distance),
   f.collar_d+2*(f.brim_overhang+distance),f.brim_corner_r+distance,
   -distance,f.brim_thickness+distance)
 if distance>5 and shape.BoundingBox().zmax<.1:
  return original_expanded(shape,distance+.5)
 return original_expanded(shape,distance)
m.expanded=studied_backing
m.contracted=layout_funnel.core_finishing_stock
def rectangular_containment(cavity,core,rod,cast,floor,top,back,width,
                           neck,pour,vents,x,y,guide_top):
 # The production complement assumes the mold is wider than it is deep.
 # Aft growth makes depth the larger axis; caps and witnesses must cover the
 # actual rectangle to evaluate a leak through the mold rather than the screen.
 depth=f.collar_d+2*f.brim_overhang+2*m.flange_margin
 overlap=.02
 surrounding=m.box(width+26,depth+26,floor-2,back+8)
 outside=cq.Vector(-(width+26)/2+1,0,floor)
 witness=cq.Vector(x+m.rod_diameter,y,rod.BoundingBox().zmin+m.rod_socket_depth)
 mouth_cap=m.box(width+2,depth+2,top-overlap,back+2)
 caps=[m.cylinder(diameter/2+overlap,back-overlap,back+1,*xy)
       for xy,diameter in [(pour,m.pour_diameter),*[(xy,m.vent_diameter) for xy in vents]]]
 caps.append(m.cylinder((m.rod_diameter+m.rod_clearance)/2+overlap,
                        guide_top-overlap,guide_top+1,x,y))
 reads={}
 for label,closed in [('cavity',[cavity,mouth_cap]),('assembled',[cavity,core,rod,*caps])]:
  remainder=m.cleaned_shape(surrounding.cut(*closed))
  assert remainder.isValid(),f'{label}: invalid liquid complement'
  retained=[s for s in remainder.Solids()
            if s.isInside(witness,1e-6) and not s.isInside(outside,1e-6)]
  assert len(retained)==1,f'{label}: liquid space leaks to outside'
  target=cast.cut(*closed)
  missing=target.cut(retained[0]).Volume()
  assert missing<m.tolerance,f'{label}: {missing:g} mm3 casting outside retained liquid'
  reads[label]={'retained_volume_ml':retained[0].Volume()/1000,
                'casting_outside_retained_mm3':missing}
 return reads
m.liquid_containment=rectangular_containment
OUT=ROOT/'.cache/pump-first-layout/funnel'/f'aft-{extra:g}'/'tooling';OUT.mkdir(parents=True,exist_ok=True)
parts,info=m.build()
for name,s in parts.items():
 assert s.isValid() and len(s.Solids())==1,name
 s.exportBrep(str(OUT/f'{name}.brep'))
 cq.exporters.export(s,str(OUT/f'{name}.step'))
 v,t=s.tessellate(.12,.08)
 (OUT/f'{name}.json').write_text(json.dumps({'vertices':[[x.x,x.y,x.z] for x in v],
  'triangles':[list(x) for x in t]},separators=(',',':'))+'\n')
 print('exported',name,flush=True)
w,d=info['flange_plan_mm'];r=m.flange_radius
circ=2*(math.hypot(w/2-r,d/2-r)+r)
info.pop('finished_funnel_step_sha256',None)
info['aft_extension_mm']=extra
info['flange_corner_radius_mm']=r
info['enclosing_diameter_mm']=circ
info['chamber_radial_clearance_mm']=(m.chamber_diameter-circ)/2
info['closure_hardware_radial_screen_mm']=max(math.hypot(*xy)+4.5 for xy in info['clamping']['centres_xy_mm'])
info['clamping_bolt_stations_on_straight_flanks']=all(
  abs(py)<=d/2-r if abs(px)>w/2-r else abs(px)<=w/2-r
  for px,py in info['clamping']['centres_xy_mm'])
assert info['clamping_bolt_stations_on_straight_flanks']
assert 2*info['closure_hardware_radial_screen_mm']<circ
assert info['chamber_radial_clearance_mm']>0
# The enlarged footprint makes depth the longer load span. Keep this an applied
# load screen, without deriving stiffness or life from the print's infill.
info['load_screen'].update(span_mm=max(f.collar_w,f.collar_d),
 footprint_dimensions_mm=[f.collar_w,f.collar_d],
 pressure_force_n=info['load_screen']['pressure_kpa']*f.collar_w*f.collar_d/1000)
info['raw_fill_allocation']={'assembled_retained_liquid_space_ml':
 info['liquid_containment']['assembled']['retained_volume_ml'],
 'mixing_reserve_fraction':.1,'allocation_ml':
 info['liquid_containment']['assembled']['retained_volume_ml']*1.1,
 'scope':'Nominal raw mold liquid space, including the finishing reserve and connected passages, plus10 percent mixing allowance. Finishing and release stack remain physically unqualified.'}
info['artifact_parts']={n:{'brep':str((OUT/f'{n}.brep').relative_to(ROOT)),
 'step':str((OUT/f'{n}.step').relative_to(ROOT)),'mesh':str((OUT/f'{n}.json').relative_to(ROOT))}
 for n in parts}
info['source_sha256']={str(Path(x).relative_to(ROOT)):hashlib.sha256(Path(x).read_bytes()).hexdigest()
 for x in (str(Path(__file__)),layout_funnel.__file__,f.__file__,m.__file__)}
info['scope']='Native two-shell mold derivation with existing rod, clamp stations, 16 mm margin, backing and release checks. Nominal chamber fit is a geometric result; no print, finished casting or chamber insertion is qualified.'
(HERE/f'candidate-aft-{extra:g}-tooling.json').write_text(json.dumps(info,indent=2)+'\n')
print(json.dumps({k:info[k] for k in ('flange_plan_mm','flange_corner_radius_mm','enclosing_diameter_mm','chamber_radial_clearance_mm','clamping_bolt_stations_on_straight_flanks')},indent=2),flush=True)
