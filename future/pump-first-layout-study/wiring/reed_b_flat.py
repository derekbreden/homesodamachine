"""Counted eight-wire bare ribbon through the controller/supply air band."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from controls_looms import definition,hull,circle_points,protected_nameplate_models
from native_harness import bounds,broad
import audit
from math import acos,cos,tan,pi

def rectangular_sweep(points,width=14.3,height=1.7,radius=12.):
 ps=[cq.Vector(*p) for p in points];takes=[0.]*len(ps);corners={}
 for i in range(1,len(ps)-1):
  u=(ps[i]-ps[i-1]).normalized();v=(ps[i+1]-ps[i]).normalized();angle=acos(max(-1.,min(1.,u.dot(v))));take=radius*tan(angle/2);takes[i]=take
  a=ps[i]-u*take;b=ps[i]+v*take;center=ps[i]+(v-u).normalized()*(radius/cos(angle/2));middle=center+((a-center)+(b-center)).normalized()*radius;corners[i]=(a,middle,b)
 edges=[];last=ps[0]
 for i in range(1,len(ps)):
  assert takes[i-1]+takes[i] <= (ps[i]-ps[i-1]).Length+1e-6
  end=corners[i][0] if i in corners else ps[i]
  if (end-last).Length>1e-7:edges.append(cq.Edge.makeLine(last,end))
  if i in corners:
   a,m,b=corners[i];edges.append(cq.Edge.makeThreePointArc(a,m,b));last=b
  else:last=end
 path=cq.Wire.assembleEdges(edges);p=ps[0]
 profile=cq.Wire.makePolygon([cq.Vector(p.x,p.y+y,p.z+z) for y,z in [(-width/2,-height/2),(width/2,-height/2),(width/2,height/2),(-width/2,height/2),(-width/2,-height/2)]])
 solid=cq.Solid.sweep(profile,[],path,makeSolid=True,isFrenet=False)
 expected=width*height*path.Length();actual=solid.Volume(tol=1e-9)
 assert solid.isValid() and abs(actual-expected)<=max(.001,expected*1e-6),(actual,expected)
 return solid,{'points_mm':points,'width_mm':width,'height_mm':height,'radius_mm':radius,'length_mm':path.Length(),'volume_mm3':actual,'expected_volume_mm3':expected}

def main():
 models,records,_,_,_=audit.collect()
 models.update(protected_nameplate_models())
 for n,r in json.loads((HERE/'power-candidate.json').read_text()).get('parts',{}).items():models[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
 for n,s in list(models.items()):
  if n.startswith(('control-','power-')):del models[n];continue
  if n.startswith(('enclosure-front-top','enclosure-back-top')):models[n]=s.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
 _,_,sections,fanouts=definition()
 for n,(s,r) in sections.items():
  if n not in ['control-service-reeds-B','control-service-fork-B','control-ground-lower-fanout']:models[n]=s
 for n,(s,owner,looms) in fanouts.items():models['control-'+n]=s
 stem=cq.Solid.makeCylinder(3.2,35,cq.Vector(-31,189.3,248),cq.Vector(0,0,1))
 tests=[]
 for startx,x in [(-28.,30.5),(-30.,30.5),(-32.,30.5),(-34.,30.5)]:
  start=(startx,205.,298.05);profile=[(start[0],start[1]+y,start[2]+z) for y in [-7.15,7.15] for z in [-.85,.85]]
  bare=hull(circle_points((-31,189.3,283),(0,0,1),6.4)+profile)
  ps=[list(start),[x,205.,298.05],[x,284.6,298.05],[x,284.6,325.2],[x,429.6,325.2],[-24,429.6,325.2],[-24,404,325.2]]
  ribbon,rec=rectangular_sweep(ps);shape=cq.Compound.makeCompound([stem,bare,ribbon])
  fork_profile=[[-24+xx,404,325.2+zz] for xx in [-7.15,7.15] for zz in [-.85,.85]]
  fork=hull(fork_profile+circle_points((-29,399.7,326.4),(0,-1,0),4.3)+circle_points((-19,399.7,326.4),(0,-1,0),4.3))
  hits=[];power_hits=[]
  for label,candidate in [('trunk',shape),('aft-fork',fork)]:
   for n,t in models.items():
    if n=='cold-core/foam-cap-lid-top' or not t.Solids() or not broad(bounds(candidate),bounds(t)):continue
    c=candidate.intersect(t,tol=.0001);v=abs(c.Volume(tol=1e-9))
    if v>.001:
     row={'section':label,'part':n,'common_mm3':v,'bounds':bounds(c)}
     (power_hits if n.startswith(('wire-','power-')) else hits).append(row)
  fluid_air=[]
  for label,candidate in [('trunk',shape),('aft-fork',fork)]:
   for n,t in models.items():
    if not n.startswith(('tube-','carb-foam-')) or not broad(bounds(candidate),bounds(t),1.):continue
    gap=candidate.distance(t)
    if gap<.999999:fluid_air.append({'section':label,'part':n,'air_mm':gap})
  row={'fanout_ribbon_start_x_mm':startx,'ribbon_x_mm':x,'hardware_hits':hits,'current_power_hits':power_hits,'fluid_air_failures':fluid_air,'hardware_pass':shape.isValid() and fork.isValid() and not hits and not fluid_air};tests.append(row);print(json.dumps(row),flush=True)
  if not row['hardware_pass']:continue
  out=ROOT/'.cache/pump-first-layout/wiring/controls-looms';out.mkdir(parents=True,exist_ok=True)
  path=out/'control-service-reeds-B-split-proved.brep';shape.exportBrep(str(path));fp=out/'control-service-fork-B-split.brep';fork.exportBrep(str(fp))
  report={'pass':True,'hardware_pass':True,'all_current_native_pass':not power_hits,'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
   'aft_fork':{'brep':str(fp.relative_to(ROOT)),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest()},'branches':[rec],'method':'counted bare eight-wire ribbon',
   'conductor_count':8,'actual_bore_mm':6.8,'normal_exit_from_lid_base_mm':35,'flat_section_mm':[14.3,1.7],'bare_wire_diameter_mm':1.7,'wire_pitch_mm':1.8,
   'minimum_nominal_horizontal_wire_centre_radius_mm':12-6.3,'minimum_nominal_vertical_wire_centre_radius_mm':12-.85,
   'native_checks':tests,'scope':'Hardware-only native reservation: the accepted eight-wire bore and35mm normal exit feed a bare one-layer counted ribbon. The1.7mm section traverses the real controller/supply band with exactR12 bends; purchased service lead length and individual bare fork dressing remain unqualified. Current power intersections are explicit and require its reroute before complete wiring qualification.'}
  (HERE/'reed-b-split-route.json').write_text(json.dumps(report,indent=2)+'\n');break
 else:(HERE/'reed-b-flat-check.json').write_text(json.dumps({'pass':False,'tests':tests},indent=2)+'\n')
if __name__=='__main__':main()
