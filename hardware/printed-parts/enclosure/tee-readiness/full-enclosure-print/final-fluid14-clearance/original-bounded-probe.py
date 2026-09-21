from pathlib import Path
import os,sys,json,math,time,hashlib
os.environ['HSM_NO_BUILD_LOCK']='1'
ROOT=Path('/Users/derekbredensteiner/Developer/homesodamachine');O=Path('/tmp/scanner-review/fluid14-current-aggregate')
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import _routing as R,_clearing,_boxes,_meshes
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=json.loads((O/'manifest.json').read_text())
p=O/'candidate-fall-advance-4.brep';tube=cq.Shape.importBrep(str(p))
b=tube.BoundingBox();tb=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
def gapbox(a,b):return math.sqrt(sum(max(0,a[k]-b[k+3],b[k]-a[k+3])**2 for k in range(3)))
inputs={str(p):sha(p),str(O/'manifest.json'):sha(O/'manifest.json')};rows=[];start=time.monotonic()
for n,r in manifest['bodies'].items():
 if n=='tube-fluid-14' or gapbox(tb,r['bounds'])>=2:continue
 q=O/r['brep'];s=cq.Shape.importBrep(str(q));inputs[str(q)]=sha(q)
 if n=='valve-v-f':
  rows.append({'name':n,'allowed_contact':'own starting collet','checked':False});continue
 print('QUERY',n,flush=True)
 g=_clearing.gap(tube,s,2)
 allowed=n in ('cold-core/foam-cap-lid-top','cold-core/foam-cap-top','cold-core/line-reservoir-a-fill','cold-core/reservoir-a-cap','cold-core/bulkhead-reservoir-a')
 v=0 if gapbox(tb,r['bounds'])>0 else abs((_meshes.meshed(tube)^_meshes.meshed(s)).volume())
 row={'name':n,'mesh_air_mm':g,'mesh_overlap_mm3':v,'required_air_mm':0 if allowed else 1,'allowed_contact':('full cap bearing or own endpoint' if allowed else None),'pass':v<1e-5 and g>=(0 if allowed else 1)-1e-6}
 if g<1.2:row['native_whole_shape_air_mm']=tube.distance(s)
 rows.append(row);print(json.dumps(row),flush=True)
 seed=json.loads((ROOT/'hardware/reference/g-ganen-pump/installation/inner-valve-route-check.json').read_text())
 run=R.Run('fluid-14','fluid','valve-v-f.outlet','foam-assembly.reservoir-a-fill',seed['waypoints_mm'],6.35,14.)
 pts=list(run.pts);pts[4]=(pts[4][0],pts[4][1]-4,pts[4][2])
 run=R.redrawn(run,pts)
 t={i:run.radii[i]*math.tan(math.radians(turn)/2) for i,turn,*_ in run.bends}
 interval=[run.pts[6][1]+t[6],run.pts[7][1]-t[7]]
 report={'status':'pass' if all(r.get('pass',True) for r in rows) else 'fail','assembly_step_sha256':manifest['assembly_step_sha256'],'input_sha256':inputs,'candidate_fall_run_mm':6.,'candidate_drop_mm':1.5,'candidate_return_mm':8.,'minimum_radius_mm':run.tightest,'waypoints':run.pts,'radii':run.radii,'bearing_required_mm':[254.4,263.2],'bearing_actual_straight_mm':interval,'bearing_pass':interval[0]<=254.4 and interval[1]>=263.2,'neighbors':rows,'full210_manifest_bounds_used':True,'elapsed_seconds':time.monotonic()-start}
 (O/'candidate-earlier-fall-check.json').write_text(json.dumps(report,indent=2)+'\n')
# Finer independent tessellation of the exact two native inputs checks sensitivity
# at the one curved patch that defeated the whole-shape OCC distance query.
valve=cq.Shape.importBrep(str(O/'valve-v-a.brep'))
report['V_A_fine_mesh_air_mm']=_meshes.meshed(tube,.005).min_gap(_meshes.meshed(valve,.005),2.)
report['all_pass']=all(r.get('pass',True) for r in rows) and report['bearing_pass'] and run.tightest>=14.-1e-6 and report['V_A_fine_mesh_air_mm']>=1
report['elapsed_seconds']=time.monotonic()-start
report['stable_inputs']=all(sha(p)==h for p,h in inputs.items())
(O/'candidate-earlier-fall-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('FINAL',report['status'],report['V_A_fine_mesh_air_mm'],report['bearing_actual_straight_mm'],report['elapsed_seconds'],flush=True)
