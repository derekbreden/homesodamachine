"""Manually review this tactile slice's supports, settings and chamfer beads."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union
BASE=Path(__file__).resolve().parent.parent
ROOT=next(p for p in BASE.parents if (p/'hardware').is_dir())
OUT=BASE/'guided-boot-trial'
sys.path[:0]=[str(ROOT/'hardware/printed-parts/enclosure/nameplate')]
from verify_mark2_print import segments
record=json.loads((OUT/'guided-boot-mark2-z004.print.json').read_text())
source=OUT/'guided-boot-mark2-z004.3mf';native=OUT/'guided-boot-mark2-z004.gcode.3mf'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==record['project_sha256']
assert sha(native)==record['native']['archive_sha256']
for name,digest in record['source_sha256'].items():assert sha(BASE/name)==digest,name
for part in record['parts']:assert sha(ROOT/part['source'])==part['stl_sha256'],part['name']
with zipfile.ZipFile(source) as a,zipfile.ZipFile(native) as c:
 planned=json.loads(a.read('Metadata/project_settings.config'))
 actual=json.loads(c.read('Metadata/project_settings.config'))
 diff={k:[planned.get(k),actual.get(k)] for k in set(planned)|set(actual) if planned.get(k)!=actual.get(k)}
 raw=c.read('Metadata/plate_1.gcode')
 assert hashlib.md5(raw).hexdigest()==c.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
for k,v in record['settings_changes_after_refresh'].items():assert actual[k]==v,(k,actual[k],v)
allowed={'filament_map_2':[None,['1']],'filament_prime_volume':[['30'],['45']]}
assert all(allowed.get(k)==v for k,v in diff.items()),diff
text=raw.decode();layers=sorted(set(float(z) for z in re.findall(r'^; Z_HEIGHT: ([\d.]+)',text,re.M)))
assert layers[0]==.2 and all(abs(b-a-.24)<1e-4 for a,b in zip(layers,layers[1:]))
assert record['native']['emitted_z_trim_mm']==[0.,.02]
assert record['native']['pause_commands']==0
assert record['native']['minimum_full_bead_bed_margin_mm']>=80
all_roads=list(segments(ROOT/'.cache/prints/umbilical-guided-boot/plate_1.gcode'))
boot_id=record['parts'][0]['identify_id']
roads=[r for r in all_roads if r['object']==boot_id and not r['feature'].startswith('Support') and r['feature'] not in ('Brim','Custom','Prime tower')]
by_z={}
for r in roads:by_z.setdefault(r['layer'],[]).append(r)
shape=lambda rr:unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in rr])
review=[]
needed=set([z for z in layers if z<=1.88]+[z for z in layers if 34<=z<=38.8])
for previous,z in zip(layers,layers[1:]):
 if z not in needed:continue
 rr=[r for r in by_z[z] if r['feature'] in ('Outer wall','Overhang wall')]
 under=shape(by_z[previous]);foot=shape(rr)
 points=[LineString((r['a'],r['b'])).interpolate(i/10,normalized=True) for r in rr for i in range(11)]
 review.append({'from_z_mm':previous,'to_z_mm':z,'max_sampled_outer_centerline_unsupported_mm':max(p.distance(under) for p in points),'outer_wall_area_fraction_supported':foot.intersection(under).area/foot.area})
assert max(r['max_sampled_outer_centerline_unsupported_mm'] for r in review)<.02,review
assert min(r['outer_wall_area_fraction_supported'] for r in review)>.65,review
support=json.loads((OUT/'support-audit.json').read_text())
assert support['summary']['support_bodies']==2 and support['summary']['bodies_without_interface_labels']==0
assert max(s['top_z_mm'] for s in support['trees'])<34.3
for s in support['interfaces']:
 y0=s['bbox_cad_xyz_mm'][1];y1=s['bbox_cad_xyz_mm'][4]
 if y0<-20:
  s['surface']='Tube-key window ceiling'
  s['removal_access']='Open side window on both sides; remove before fitting the key.'
  assert -29.5<y0<y1<-28
 else:
  s['surface']='Front cable-drop pocket ceiling'
  s['removal_access']='Open mating-face pogo pocket; remove before fitting the contacts.'
  assert -15.1<y0<y1<-13.5
support['physical_removal_tested']=False
(OUT/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
# Six emitted perimeter crossings through a clear +X section of the shoulder.
crossings=[]
cx=record['parts'][0]['plate_translation_mm'][0];cy=record['parts'][0]['plate_translation_mm'][1]
for z in layers:
 if not 34.3<z<38.3:continue
 hits=[]
 for r in by_z[z]:
  if r['feature'] not in ('Inner wall','Outer wall','Overhang wall'):continue
  (x0,y0),(x1,y1)=r['a'],r['b']
  if min(y0,y1)<=cy<max(y0,y1):
   x=x0+(cy-y0)*(x1-x0)/(y1-y0)
   if x>cx+10:hits.append(x)
 assert len(hits)==6,(z,hits)
 crossings.append({'z_mm':z,'wall_count':len(hits)})
proof={'native_archive_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),
 'review_source_sha256':sha(Path(__file__)),
 'gcode_sha256':hashlib.sha256(raw).hexdigest(),'source_meshes_bound_by_print_record':True,
 'project_settings_match_except_native_normalizations':diff,
 'first_layer_and_chamfer_bead_overlap':review,'shoulder_wall_counts':crossings,
 'all_supports_below_curved_guides_and_shoulder':True,'support_summary':support['summary'],
 'physical_support_removal_tested':False,'scope':'Prepared tactile job only; no physical print, tube feed, compression, grip or connector qualification.',
 'submitted':False}
(OUT/'native-review.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'settings_verified':True,'layer_count':len(layers),'shoulder_wall_count':6,'max_outer_centerline_unsupported_mm':max(r['max_sampled_outer_centerline_unsupported_mm'] for r in review),'min_outer_wall_area_supported':min(r['outer_wall_area_fraction_supported'] for r in review),'support_summary':support['summary']},indent=2))
