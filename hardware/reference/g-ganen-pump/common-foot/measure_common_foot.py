"""Bound visible common-foot dimensions without scaling or merging free poses."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import Delaunay
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from g_ganen_foot import parameters,PROFILE_YZ

HERE=Path(__file__).resolve().parent;REF=HERE.parent;ROOT=REF.parents[2]
CACHE=ROOT/'.cache/g-ganen-common-foot'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stat(a):
 a=np.asarray(a);return {'count':len(a),'median':float(np.median(a)),'abs_p95':float(np.quantile(abs(a),.95)),'min':float(a.min()),'max':float(a.max())}
data=json.loads((REF/'reference-parameters.json').read_text())
rows=[]
for f in data['mounting_feet']:
 path=CACHE/f'pass-01-feet-up-{f["id"]}.npz';a=np.load(path);p=a['points'];n=a['normals']
 m=(p[:,1]>-1)&(p[:,2]>.7)&(p[:,2]<5)&(abs(n[:,2])<.35)&(np.linalg.norm(p[:,:2],axis=1)>7)
 q=p[m,:2];fit=least_squares(lambda v:np.linalg.norm(q-v[:2],axis=1)-v[2],[0,0,9],loss='soft_l1',f_scale=.15)
 residual=np.linalg.norm(q-fit.x[:2],axis=1)-fit.x[2]
 ends=[]
 for sign in [-1,1]:
  m=(n[:,0]*sign>.94)&(p[:,0]*sign>7.5)&(p[:,1]>-10)&(p[:,1]<-5)&(p[:,2]>1)&(p[:,2]<6)
  ends.append(float(np.median(p[m,0])))
 complete=[s for s in f['pose_observations'][0]['local_slot_sections']['sections'] if s.get('status')=='complete_section_observed']
 rows.append({'foot':f['id'],'pass':'pass-01-feet-up','outer_nose_circle':{'center_xy_mm':fit.x[:2].tolist(),'radius_mm':float(fit.x[2]),'radial_residual_mm':stat(residual)},'visible_axial_end_medians_mm':ends,'visible_width_mm':ends[1]-ends[0],
 'complete_lower_slot_sections':[{'height_mm':s['depth_above_local_bearing_plane_mm'],'width_mm':s['width_mm'],'length_mm':s['total_length_mm'],'observed_sectors':s['observed_angular_sectors_of_12']} for s in complete],
 'scope':'Independent free-foot bearing frame; no scale fit and no union of bent poses. Rounded nominal geometry follows shared observations plus the direct identical/7 mm authority.'})
a=np.load(CACHE/'pass-02-on-back-rear_yplus.npz');p=a['points'];n=a['normals']
m=(abs(n[:,0])>.94)&(abs(p[:,0])>7.2)&(abs(p[:,0])<10.8)&(p[:,1]<-8)&(p[:,2]>9)&(p[:,2]<19.5)
q=p[m,1:];outline=Polygon(PROFILE_YZ);outside=np.array([outline.distance(Point(v)) for v in q])
report={'schema':1,'status':'visible_surface_dimensions_recorded','unit_scale':1.0,'owner_authority':'All four purchased feet are identical, removable rubber sliders; pads approximately 7 mm thick. Derek, 2026-09-21.',
 'parameters':parameters(),'per_foot_visible_measurements':rows,
 'exposed_clip_face':{'source':'pass-02-on-back rear_yplus','selection':'|local Nx| > .94, 7.2 < |local X| < 10.8, local Y < -8, 9 < Z < 19.5. Axial end faces distinguish rubber from the fixed axially continuous rail.','outside_nominal_profile_distance_mm':stat(outside),'scope':'Agreement of observed end-face samples with the simplified exterior clip profile; not an assertion that the unobserved inner gripping cavity is manufactured to this polygon.'},
 'rail_end_evidence':{'observed_fixed_face_extent_mm':[.4,76.9],'conservative_fully_supported_interval_mm':[.5,76.5],'common_clip_axial_interval_mm':[-9,9],'fully_engaged_slot_stations_mm':[9.5,67.5],'physical_hard_stop_observed':False,'partial_overhang_observed':True,'captured_rear_positive_slot_x_mm':74.43728463507625,'scope':'The farthest fully engaged positions do not establish the furthest mechanically possible partially overhanging positions or their retention.'},
 'input_sha256':{str(p.relative_to(REF)):sha(p) for p in [REF/'registered-measurements.json',REF/'interface-measurements.json',REF/'scan-evidence.json',HERE/'inspection-inputs.json']},
 'source_sha256':{p.name:sha(p) for p in [Path(__file__),HERE/'g_ganen_foot.py']},
 'limits':['Rounded common geometry describes visible rubber surfaces; spray and scanner absolute accuracy are unmeasured.','The 7 mm pad is nominal installed thickness, not measured loaded compression.','Simplified underside relief depths retain the observed mouths but are not a replacement-foot tooling specification.','The shared obround mouth does not certify the minimum hidden through-depth throat or grip retention.']}
(HERE/'measurement-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'nose_radii':[r['outer_nose_circle']['radius_mm'] for r in rows],'widths':[r['visible_width_mm'] for r in rows],'clip_outside':report['exposed_clip_face']['outside_nominal_profile_distance_mm']},indent=2))
