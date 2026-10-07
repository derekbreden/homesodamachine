"""Occupied grouped control looms and explicit nominal connector fanouts.

The canonical net schedule retains every conductor. Shared runs are sized for
the conductor count; purchased contact locations and individual wire dressing
remain expressly identified reservations. Forward shell stock is an obstacle.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import numpy as np
import cadquery as cq
from OCP.Standard import Standard_Failure
from scipy.spatial import ConvexHull
from io import BytesIO
from weakref import ref

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/wiring/controls-looms'
sys.path[:0]=[str(HERE),str(STUDY)]
from controls import inventory,port as source_port
from controls_harness import ControlsGuide,passed_body_models,lower_lead_models,control_occupied_points
from native_harness import bounds,broad,sweep
from evidence_binding import content_sha256,manifest_content_sha256

# Explicit packing reserves, using the bought1.7mm conductor exterior.
# Four fit a1.8mm square pitch; six/seven use a1.8mm hexagon with a centre;
# the accepted eight-wire service section uses theR2.35 ring in its6.8mm bore.
DIAMETER={1:1.7,2:3.5,3:3.9,4:4.3,5:5.0,6:5.5,7:5.5,8:6.4,9:6.8}
PACKING_RADIUS={1:0.,2:.9,3:1.8/math.sqrt(3),4:1.8/math.sqrt(2),5:1.8/(2*math.sin(math.pi/5)),6:1.8,7:1.8,8:2.35,9:2.35}
BEND_RADIUS={count:math.ceil((3.4+radius)*20)/20 for count,radius in PACKING_RADIUS.items()}
BEND_RADIUS[4]=4.7

def loaded_digest(shape):
 stream=BytesIO();shape.exportBrep(stream);return hashlib.sha256(stream.getvalue()).hexdigest()

_MODEL_METADATA={}
def model_metadata(shape):
 key=id(shape);cached=_MODEL_METADATA.get(key)
 if cached is not None and cached[0]() is shape:return cached[1:]
 box=bounds(shape);solids=bool(shape.Solids())
 _MODEL_METADATA[key]=(ref(shape,lambda _: _MODEL_METADATA.pop(key,None)),box,solids)
 return box,solids

def native_hits(shape,models,owners=()):
 from audit import common as native_common
 hits=[];box=bounds(shape)
 for n,s in models.items():
  if n in owners:continue
  model_box,solid=model_metadata(s)
  if not solid or not broad(box,model_box,pad=.0001):continue
  common=native_common(shape,s)
  if common>.001:hits.append({'part':n,'common_mm3':common})
 return hits

def analytic_geometry_signature(shape):
 """Native analytic supports, trim curves and solid ownership at 1e-8 mm."""
 from OCP.BRepAdaptor import BRepAdaptor_Surface
 def vec(v):return [round(float(n),8) if abs(float(n))>=5e-9 else 0. for n in [v.X(),v.Y(),v.Z()]]
 def axis(a):return [vec(a.Location()),vec(a.Direction())]+([vec(a.XDirection()),vec(a.YDirection())] if hasattr(a,'XDirection') else [])
 def edge_signature(e):
  a=e._geomAdaptor();kind=e.geomType()
  if kind=='LINE':support=axis(a.Line().Position())
  elif kind=='CIRCLE':support=[axis(a.Circle().Position()),round(a.Circle().Radius(),8)]
  else:raise ValueError('Unsupported received fixed-region trim '+kind)
  return [kind,support,round(a.FirstParameter(),8),round(a.LastParameter(),8),str(e.wrapped.Orientation())]
 def face_signature(f):
  a=BRepAdaptor_Surface(f.wrapped);kind=f.geomType()
  if kind=='PLANE':support=axis(a.Plane().Position())
  elif kind=='CYLINDER':support=[axis(a.Cylinder().Position()),round(a.Cylinder().Radius(),8)]
  elif kind=='TORUS':support=[axis(a.Torus().Position()),round(a.Torus().MajorRadius(),8),round(a.Torus().MinorRadius(),8)]
  else:raise ValueError('Unsupported received fixed-region surface '+kind)
  wires=[sorted([edge_signature(e) for e in w.Edges()],key=lambda x:json.dumps(x,sort_keys=True)) for w in f.Wires()]
  return [kind,support,str(f.wrapped.Orientation()),sorted(wires,key=lambda x:json.dumps(x,sort_keys=True))]
 solids=[sorted([face_signature(f) for f in s.Faces()],key=lambda x:json.dumps(x,sort_keys=True)) for s in shape.Solids()]
 return hashlib.sha256(json.dumps(sorted(solids,key=lambda x:json.dumps(x,sort_keys=True)),separators=(',',':')).encode()).hexdigest()

STATIC_JOINTS=[
 ('control-service-reeds-A','control-service-fork-A'),('control-service-reeds-B','control-service-fork-B'),
 ('control-ground-lower-fanout','control-ground-descent'),('control-ground-lower-fanout','control-service-fork-A'),('control-ground-lower-fanout','control-service-fork-B'),
 ('control-ground-upper-A','control-ground-upper-merger'),('control-ground-upper-B','control-ground-upper-merger'),('control-ground-descent','control-ground-upper-merger'),
 ('control-fixed-manifold-ribbon','control-manifold-aft-fanout')]

def static_pair_checks(sections,fanouts):
 from audit import common as native_common
 models={n:s for n,(s,_) in sections.items()};models.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 allowed={frozenset(pair) for pair in STATIC_JOINTS};checks=[];boxes={n:bounds(s) for n,s in models.items()}
 names=list(models)
 for i,name in enumerate(names):
  for other in names[i+1:]:
   if not broad(boxes[name],boxes[other]):continue
   common=native_common(models[name],models[other]);mate=frozenset([name,other]) in allowed
   checks.append({'parts':[name,other],'common_mm3':common,'declared_continuity':mate,'pass':mate or common<.001})
 return {'parts_count':len(models),'checks':checks,'failures':[r for r in checks if not r['pass']],
  'input_geometry_sha256':{n:loaded_digest(s) for n,s in models.items()},'pass':all(r['pass'] for r in checks),
  'scope':'Exact fuzzy native intersections between counted static sections and nominal fanout regions. Exemptions name only physically continuous splice interfaces.'}

def protected_nameplate_records():
 routing=json.loads((STUDY/'routing/candidate.json').read_text())
 move=routing.get('interface_moves',{}).get('nameplate',{});records={}
 for field,suffix in [('new_receiver','stock'),('new_backing','backing')]:
  r=move.get(field)
  if r:records['protected-nameplate-'+suffix]=r
 if 'protected-nameplate-stock' not in records:
  r=json.loads((STUDY/'funnel/shells.json').read_text())['interfaces']['retained-nameplate-stock']
  records['protected-nameplate-stock']=r
 return records

def protected_nameplate_models():
 return {name:cq.Shape.importBrep(str(ROOT/r['brep'])) for name,r in protected_nameplate_records().items()}

def port(owner,point,axis,label):
 return source_port(owner,[float(v) for v in point],[float(v) for v in axis],label)

def circle_points(point,axis,diameter,n=32):
 p=np.asarray(point,float);a=np.asarray(axis,float);a/=np.linalg.norm(a)
 ref=np.array([0,0,1.]) if abs(a[2])<.9 else np.array([0,1.,0])
 u=np.cross(a,ref);u/=np.linalg.norm(u);v=np.cross(a,u)
 return [p+diameter/2*(u*math.cos(t)+v*math.sin(t)) for t in np.arange(n)*2*math.pi/n]

def contact_profile(ports):
 a=np.asarray(ports[0]['axis'],float);pts=np.asarray([p['point'] for p in ports],float);plane=int(np.argmax(abs(a)))
 axes=[i for i in range(3) if i!=plane];lo=pts.min(axis=0);hi=pts.max(axis=0)
 lo[axes]-=.85;hi[axes]+=.85
 out=[]
 for i in [lo[axes[0]],hi[axes[0]]]:
  for j in [lo[axes[1]],hi[axes[1]]]:
   p=pts.mean(axis=0);p[axes]=[i,j];out.append(p)
 return out

def hull(points):
 ps=np.unique(np.round(np.asarray(points),8),axis=0);h=ConvexHull(ps)
 faces=[]
 for indices in h.simplices:
  vs=[cq.Vector(*ps[i]) for i in indices];w=cq.Wire.makePolygon(vs+[vs[0]])
  faces.append(cq.Face.makeFromWires(w))
 solid=cq.Solid.makeSolid(cq.Shell.makeShell(faces)).fix().clean()
 if not solid.isValid():raise ValueError('Invalid nominal fanout hull')
 return solid

def clearance_envelope(shape,gap=1.,fused_union=False):
 """Native per-solid clearance, with bounded convex growth for dressing hulls."""
 from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
 from OCP.GeomAbs import GeomAbs_Arc
 pieces=[]
 shifts=[np.array([x,y,z]) for x in [-gap,gap] for y in [-gap,gap] for z in [-gap,gap]]
 for solid in shape.Solids():
  if all(face.geomType()=='PLANE' for face in solid.Faces()):
   # All planar source members here are convex dressing hulls or rectangular
   # bare corridors. Their Minkowski sum with the1mm cube gives at least1mm
   # Euclidean running room, and grows each roof/flank bound by at most1mm.
   grown=hull([np.asarray(v.toTuple())+delta for v in solid.Vertices() for delta in shifts])
  else:
   offset=BRepOffsetAPI_MakeOffsetShape();offset.PerformByJoin(solid.wrapped,gap,.0001,Join=GeomAbs_Arc)
   grown=cq.Shape.cast(offset.Shape())
  if not grown.isValid() or not grown.Solids():raise ValueError('Invalid native control clearance')
  missing=abs(solid.cut(grown,tol=.0001).Volume(tol=1e-9))
  if missing>.001:raise ValueError(f'Native control clearance lost{missing:g}mm³')
  pieces.append(grown)
 if fused_union:
  joined=pieces[0].copy(mesh=False).fuse(*[s.copy(mesh=False) for s in pieces[1:]],tol=.0001).clean()
  if not joined.isValid() or len(joined.Solids())!=1:raise ValueError('Dressing clearance union is not one valid solid')
  return joined
 return cq.Compound.makeCompound(pieces)

def envelope_fanout(contacts,dock,diameter):
 return hull(contact_profile(contacts)+circle_points(dock['point'],dock['axis'],diameter))

def j1_manifold_flat_departure(y,z):
 """Seven parallel bare conductors turn upward before the aft gas crossing."""
 from reed_b_flat import rectangular_sweep
 x=25.3;high=340.3
 local=[[0,0,0],[4.4,0,0],[4.4,0,high-z],[9.,0,high-z]]
 shape,record=rectangular_sweep(local,12.5,1.7,3.4)
 shape=shape.rotate((0,0,0),(0,0,1),90).translate((x,y,z))
 raw_profile=[np.array([x+u,y,z+v]) for u in [-6.25,6.25] for v in [-.85,.85]]
 end_profile=[np.array([x+u,y+9.,high+v]) for u in [-6.25,6.25] for v in [-.85,.85]]
 dock=port('control-header-J1-fanout',(x,y+13.,high),(0,1,0),'Seven-wire bare header escape followed by counted round loom')
 transition=hull(end_profile+circle_points(dock['point'],dock['axis'],5.5))
 return dock,cq.Compound.makeCompound([shape,transition]),raw_profile,{
  'conductor_count':7,'bare_section_mm':[12.5,1.7],'wire_pitch_mm':1.8,
  'wire_centres_parallel_to_world_x':True,'nominal_wire_centre_radius_mm':3.4,
  'flat_centreline_length_mm':record['length_mm'],
  'scope':'Seven bare conductors turn in the Y/Z plane with parallel X rows before entering a counted round loom. The nominal flattening and round-packing transition do not locate individual fork dressing or qualify purchased termination fit.'}

def single_junction_exit(contact,vertical=-1):
 """The complete published nominal2/4mm-normal R3.4 working approach."""
 p=np.asarray(contact['point'],float);v=np.asarray(contact['axis'],float)
 if abs(v[2])>.9:
  ps=[p,p+v*7.4,p+v*7.4+np.array([0.,-7.4,0.])];direction=[0,-1,0]
 else:
  ps=[p,p+v*5.4,p+v*5.4+np.array([0.,0.,vertical*4.2])];direction=[0,0,vertical]
 shape,record=sweep([q.tolist() for q in ps],1.7)
 return port(contact['owner'],ps[-1],direction,'Complete nominal junction approach dock'),shape

def source_b_feed_exit(contact):
 """Native blade normal2mm plusR3.4 EAST before the needle's fore face."""
 p=np.asarray(contact['point'],float);v=np.asarray(contact['axis'],float)
 corner=p+v*5.4;end=corner+np.array([7.4,0.,0.])
 shape,record=sweep([p.tolist(),corner.tolist(),end.tolist()],1.7,3.4)
 return port(contact['owner'],end,[1,0,0],'SourceB positive blade normal approach and EAST bend'),shape

def keystone_exit(contacts):
 """Four nominal normal-entry wire bends and their counted dressing region."""
 pieces=[];tops=[]
 for contact in contacts:
  p=np.asarray(contact['point'],float);q=p+np.array([0.,-7.4,0.]);end=q+np.array([0.,0.,-7.4])
  shape,_=sweep([p.tolist(),q.tolist(),end.tolist()],1.7);pieces.append(shape)
  tops+=circle_points(end,[0,0,1],1.7)
 center=np.asarray([c['point'] for c in contacts]).mean(axis=0)+np.array([0.,-7.4,-14.5])
 dock=port('keystone-jack',center,[0,0,-1],'Four-wire IDC downward bundle dock')
 pieces.append(hull(tops+circle_points(dock['point'],dock['axis'],4.3)))
 return dock,cq.Compound.makeCompound(pieces)

def manifold_transition():
 """Full retained ribbon section with an inward S and an aft upward bend."""
 radius=8.;inward=1.375;fore=2.5;start_y=326.;x0=94.625;x=x0-inward;aft_y=459.-fore
 theta=math.acos(1-inward/(2*radius));run=2*radius*math.sin(theta)
 a=cq.Vector(x0,start_y,247);half=cq.Vector(x0-inward/2,start_y+run/2,247);s_end=cq.Vector(x,start_y+run,247)
 s_mid1=cq.Vector(x0-radius*(1-math.cos(theta/2)),start_y+radius*math.sin(theta/2),247)
 s_mid2=cq.Vector(x+radius*(1-math.cos(theta/2)),start_y+run-radius*math.sin(theta/2),247)
 c=cq.Vector(x,aft_y-radius,247);d=cq.Vector(x,aft_y,255);end=cq.Vector(x,aft_y,273.6)
 mid=cq.Vector(x,aft_y-radius+radius/math.sqrt(2),255-radius/math.sqrt(2))
 edges=[cq.Edge.makeThreePointArc(a,s_mid1,half),cq.Edge.makeThreePointArc(half,s_mid2,s_end),
        cq.Edge.makeLine(s_end,c),cq.Edge.makeThreePointArc(c,mid,d),cq.Edge.makeLine(d,end)]
 vertices=[cq.Vector(xx,start_y,z) for xx,z in [(92.075,242.75),(97.175,242.75),(97.175,251.25),(92.075,251.25)]]
 profile=cq.Wire.makePolygon(vertices+[vertices[0]]);path=cq.Wire.assembleEdges(edges)
 ribbon=cq.Solid.sweep(profile,[],path,makeSolid=True,isFrenet=False)
 if abs(ribbon.Volume(tol=1e-9)-5.1*8.5*path.Length())>.001:raise ValueError('Manifold ribbon lost its complete section')
 docks={'J1':port('control-manifold-aft-fanout',(100.3,460.2,284.),(0,-1,0),'Retained7-wire manifold ribbon aft transition'),
        'J2':port('control-manifold-aft-fanout',(94.7,460.2,276.5),(0,-1,0),'Retained4-wire manifold ribbon aft transition')}
 shape=cq.Compound.makeCompound([ribbon,hull([*circle_points(docks['J1']['point'],docks['J1']['axis'],5.5),*circle_points(docks['J2']['point'],docks['J2']['axis'],4.3),
            *[np.array([xx-inward,y-fore,273.6]) for xx in [92.075,97.175] for y in [454.75,463.25]]])])
 return shape,docks,{'conductor_count':11,'ribbon_section_mm':[5.1,8.5],'nominal_rectangular_sweep_radius_mm':8,
 'clearance_fused_union':True,
 'lateral_transition_start_y_mm':start_y,'lateral_transition_x_mm':-inward,'upward_bend_axis_y_mm':aft_y,
 'outer_ribbon_length_mm':path.Length(),'scope':'Three retained bare ribbon layers keep their complete5.1x8.5mm section through anR8 inward S fromY326 and turn upward atY456.5. The first4mm overlaps the unchanged forward corridor as a named continuous dressing joint. Both counted7+4 fore-facing mouths retain their actual locations. Lower-stock clearance and individual wire dressing remain nominal and require printed-fit qualification.'}

def meter_pigtail(ports):
 """Three bare wires leave the measured6x3 root and separate beneath it."""
 contacts=[ports['meter-V5'],ports['meter-IO25'],ports['meter-GND']]
 pieces=[];tips=[]
 for p in contacts:
  start=np.asarray(p['point'],float);corner=start+np.array([0,0,-5.4]);end=corner+np.array([0,-7.4,0])
  s,_=sweep([start.tolist(),corner.tolist(),end.tolist()],1.7);pieces.append(s)
  tips+=circle_points(end,[0,-1,0],1.7)
 root=np.asarray(contacts[1]['point'],float)
 signals=port('control-meter-pigtail',(root[0]-1,root[1]-11.4,root[2]-4.5),(0,-1,0),'Meter2-wire signal/supply dressing exit')
 ground=port('control-meter-pigtail',(root[0]+2.1,root[1]-11.4,root[2]-4.5),(0,-1,0),'Meter1-wire ground dressing exit')
 pieces.append(hull(tips+circle_points(signals['point'],signals['axis'],3.5)+circle_points(ground['point'],ground['axis'],1.7)))
 return cq.Compound.makeCompound(pieces),{'signals':signals,'ground':ground},{'conductor_count':3,
  'actual_root_mm':ports['meter-IO25']['point'],'measured_root_section_mm':[6,3],
  'normal_straight_mm':2,'geometric_wire_radius_mm':3.4,'scope':'Measured DIGITEN pigtail root/outward axis, three1.7mm bare wire approaches and counted2+1 dressing fork. Flexible lead order, length, insulation and formed bends remain unqualified.'}

def relay_logic_fork(ports):
 """The four-wire J5 trunk tees shared rails at the two-relay cluster."""
 contacts=[ports[f'R{r}-{label}'] for r in [1,2] for label in ['GND','V5','IO19' if r==1 else 'IO2']]
 dock=port('control-relay-logic-fork',(36.5,442.15,283.65),(-1,0,0),'J5 four-wire device-cluster fork entry')
 branches=[];upper=[]
 for relay_contacts in [contacts[:3],contacts[3:]]:
  face=np.asarray([p['point'] for p in relay_contacts]).mean(axis=0)
  at=face+np.array([0.,0.,8.4])
  profile=circle_points(at,(0,0,1),3.9)
  branches.append(hull(contact_profile(relay_contacts)+profile));upper+=profile
 # Keep the tee above the divider's278mm crown. A single hull from both
 # terminal faces would fill the intervening isolation wall below that crown.
 branches.append(hull(upper+circle_points(dock['point'],dock['axis'],4.3)))
 shape=cq.Compound.makeCompound(branches)
 return shape,dock,{'conductor_count':4,'terminal_branch_count':6,'clamp_ports':contacts,
  'normal_terminal_approach_mm':8.4,'tee_minimum_z_mm':279.55,
  'scope':'One four-conductor J5 trunk (GND,V5,IO2,IO19); GND/V5 tee at the relay cluster into six terminal branches, as cable-assemblies.md specifies. Exact native representative working faces; clamp pitch, plugs and splice dressing remain nominal.'}

def flat_reed_a(tail_x=-52.8,tail_z=299.3,fork_x=-52.8):
 """Counted bare exit below the lower rear fittings, then anR6 round trunk."""
 flat=[np.array([-54.5,y,z]) for y in [450.85,465.15] for z in [254.95,256.65]]
 first=hull(circle_points((-31,458.3,253.4),(0,0,1),6.4)+flat)
 transition=hull(flat+circle_points((-62,458,259),(0,0,1),6.4))
 radius=6.;offset=tail_x+62;theta=math.acos(1-offset/(2*radius));height=2*radius*math.sin(theta)
 begin=cq.Vector(-62,458,279);middle=cq.Vector(-62+offset/2,458,279+height/2);end=cq.Vector(tail_x,458,279+height)
 m1=cq.Vector(-62+radius*(1-math.cos(theta/2)),458,279+radius*math.sin(theta/2))
 m2=cq.Vector(tail_x-radius+radius*math.cos(theta/2),458,279+height-radius*math.sin(theta/2))
 edges=[cq.Edge.makeLine(cq.Vector(-62,458,259),begin),cq.Edge.makeThreePointArc(begin,m1,middle),cq.Edge.makeThreePointArc(middle,m2,end)]
 wire=cq.Wire.assembleEdges(edges);profile=cq.Wire.makeCircle(3.2,cq.Vector(-62,458,259),cq.Vector(0,0,1));turn=cq.Solid.sweep(profile,[],wire,makeSolid=True,isFrenet=False)
 fore_x=tail_x-1.2
 if abs(fore_x-tail_x)>1e-6:
  tail,record=sweep([end.toTuple(),[tail_x,458,tail_z],[tail_x,425,tail_z]],6.4,6)
  side,p,length=tangent_s([tail_x,425,tail_z],[0,-1,0],[fore_x-tail_x,0,0],6,6.4)
  last,last_record=sweep([p,[fore_x,407.5,tail_z],[fore_x,407.5,319.8]],6.4,6)
  upper,q,upper_length=tangent_s([fore_x,407.5,319.8],[0,0,1],[fork_x-fore_x,0,0],6,6.4)
  final,final_record=sweep([q,[fork_x,407.5,326.4]],6.4,6)
  pieces=[tail,side,last,upper,final];record['round_trunk_length_mm']=wire.Length()+record['length_mm']+length+last_record['length_mm']+upper_length+final_record['length_mm']
  record['lateral_s']={'begin_mm':[tail_x,425,tail_z],'end_mm':p,'offset_mm':fore_x-tail_x,'radius_mm':6,'length_mm':length};record['last_segment']=last_record
  record['upper_s']={'begin_mm':[fore_x,407.5,319.8],'end_mm':q,'offset_mm':fork_x-fore_x,'radius_mm':6,'length_mm':upper_length};record['final_segment']=final_record
 else:
  tail,record=sweep([end.toTuple(),[tail_x,458,tail_z],[tail_x,407.5,tail_z],[fork_x,407.5,326.4]],6.4,6);pieces=[tail];record['round_trunk_length_mm']=wire.Length()+record['length_mm']
 shape=cq.Compound.makeCompound([first,transition,turn,*pieces])
 return shape,{**record,'conductor_count':8,'actual_bore_mm':6.8,'packing_radius_mm':2.35,'minimum_nominal_round_trunk_wire_centre_radius_mm':3.65,
  'flat_exit_cross_section_mm':[14.3,1.7],'flat_exit_z_mm':[254.95,256.65],
  'fork_axis_mm':[fork_x,407.5,326.4],
  'scope':'Actual accepted8-wire bore and immediate bare flattened exit below the rear fittings, followed by a countedR6 round trunk. Fanout hull reserves wire dressing; constituent fanout bends remain unlocated.'}

def tangent_s(begin,forward,offset,radius=6,diameter=6.4):
 p=np.asarray(begin,float);v=np.asarray(forward,float);w=np.asarray(offset,float);h=np.linalg.norm(w);w/=h
 theta=math.acos(1-h/(2*radius));run=2*radius*math.sin(theta)
 middle=p+v*run/2+w*h/2;end=p+v*run+w*h
 m1=p+v*radius*math.sin(theta/2)+w*radius*(1-math.cos(theta/2))
 m2=end-v*radius*math.sin(theta/2)-w*radius*(1-math.cos(theta/2))
 edges=[cq.Edge.makeThreePointArc(cq.Vector(*p),cq.Vector(*m1),cq.Vector(*middle)),cq.Edge.makeThreePointArc(cq.Vector(*middle),cq.Vector(*m2),cq.Vector(*end))]
 wire=cq.Wire.assembleEdges(edges);profile=cq.Wire.makeCircle(diameter/2,cq.Vector(*p),cq.Vector(*v))
 return cq.Solid.sweep(profile,[],wire,makeSolid=True,isFrenet=False),end.tolist(),wire.Length()

def east_reed_b():
 prefix,first=sweep([[-31,189.3,253.4],[-31,189.3,286],[-31,202,286],[2,202,286],[2,214,286]],6.4,6)
 lift,p,first_s=tangent_s([2,214,286],[0,1,0],[0,0,5.1])
 middle,record=sweep([p,[2,239,291.1],[94.625,239,291.1],[94.625,430,291.1],[94.625,430,327.45],[-24,430,327.45],[-24,412,327.45]],6.4,6)
 fall,last,last_s=tangent_s([-24,412,327.45],[0,-1,0],[0,0,-1.05])
 tail,final=sweep([last,[-24,404,326.4]],6.4,6)
 return cq.Compound.makeCompound([prefix,lift,middle,fall,tail]),{'conductor_count':8,'actual_bore_mm':6.8,'packing_radius_mm':2.35,'minimum_nominal_wire_centre_radius_mm':3.65,
  'diameter_mm':6.4,'centreline_radius_mm':6,'length_mm':first['length_mm']+first_s+record['length_mm']+last_s+final['length_mm'],
  'prefix_points_mm':first['points_mm'],'middle_points_mm':record['points_mm'],'final_points_mm':final['points_mm'],
  'scope':'Counted8-wire reed-B trunk through its actual accepted bore, beneath the enlarged frame above source coils, around the east side of ASSE/pump and above the supply. ExactR6 arcs and tangentS offsets.'}

def grouped(data):
 """Coalesce equal device/connector destinations without losing pin mapping."""
 groups={}
 for j in data['jobs']:
  a,b=j['from'],j['to'];pa,pb=data['ports'][a],data['ports'][b]
  source=a.split(':')[0] if a.startswith('J') else pa['owner']
  target=pb['owner']
  if source=='J5' and target.startswith('relay-'):target='relay-logic-cluster'
  if b.startswith('reed-'):target='reed-'+b.split('-')[1]
  k=(source,target)
  groups.setdefault(k,[]).append(j)
 return [{'name':'loom-'+source+'-'+target.replace('/','-'),'jobs':jobs,
          'from_keys':list(dict.fromkeys(j['from'] for j in jobs)),
          'to_keys':list(dict.fromkeys(j['to'] for j in jobs)),
          'conductor_count':len(set(j['from'] for j in jobs)) if target=='relay-logic-cluster' else len(jobs)} for (source,target),jobs in groups.items()]

def definition():
 data=inventory();groups=grouped(data);ports=data['ports'];sections={};fanouts={};forks={}
 # Complete accepted service trunks, with centrelineR6 so the innermost
 # R2.35-packed wire centre has at leastR3.65, before physical qualification.
 service={
  'A':[[-31,458.3,253.4],[-31,458.3,282.5],[-31,407.5,282.5],[-52.8,407.5,282.5],[-52.8,407.5,326.4]],
  'B':[[-31,189.3,253.4],[-31,189.3,261],[-96,189.3,261],[-96,255,261],[-96,255,273.6],[-96,330,273.6],[-96,330,321.6],[-96,404,321.6],[-96,404,305],[-24,404,305],[-24,404,326.4]]}
 for reservoir,points in service.items():
  s,record=sweep(points,6.4,6);sections['control-service-reeds-'+reservoir]=(s,{**record,'conductor_count':8,'actual_bore_mm':6.8,'packing_radius_mm':2.35,'minimum_nominal_wire_centre_radius_mm':3.65})
  if reservoir=='A':
   proved=HERE/'reed-a-service-route.json'
   ar=json.loads(proved.read_text()) if proved.exists() else{}
   if ar.get('pass'):sections['control-service-reeds-A']=(cq.Shape.importBrep(str(ROOT/ar['brep'])),ar)
   else:sections['control-service-reeds-A']=flat_reed_a()
  if reservoir=='B':
   proved=HERE/'reed-b-split-route.json'
   r=json.loads(proved.read_text()) if proved.exists() else{}
   if r.get('pass'):sections['control-service-reeds-B']=(cq.Shape.importBrep(str(ROOT/r['brep'])),r)
   else:sections['control-service-reeds-B']=east_reed_b()
  x,y,z=points[-1];face_y=y-4.3
  left=port('control-service-fork-'+reservoir,(x-5,face_y,z),(0,-1,0),reservoir+' four ground branches')
  right=port('control-service-fork-'+reservoir,(x+5,face_y,z),(0,0,-1) if reservoir=='A' else (0,-1,0),reservoir+' four reed signals')
  forks[reservoir]={'ground':left,'signals':right}
  s=hull(circle_points((x,y,z),(0,0,1),6.4)+circle_points(left['point'],left['axis'],4.3)+circle_points(right['point'],right['axis'],4.3))
  sections['control-service-fork-'+reservoir]=(s,{'conductor_count':8,'scope':'Nominal two4-wire fork from actual accepted8-wire service bore; individual wire dressing is unlocated.'})
  if reservoir=='A' and ar.get('pass'):
   sections['control-service-fork-A']=(cq.Shape.importBrep(str(ROOT/ar['aft_fork']['brep'])),{'conductor_count':8,'scope':'Counted reed-A service trunk enters the aft face of its8→4+4 dressing fork; input and both output working faces are explicit, with individual branch dressing unlocated.'})
  if reservoir=='B' and r.get('pass'):
   sections['control-service-fork-B']=(cq.Shape.importBrep(str(ROOT/r['aft_fork']['brep'])),{'conductor_count':8,'scope':'The counted bare8-wire reed-B service ribbon feeds distinct4-wire ground and signal exits in an explicit aft dressing fork; individual branch dressing remains unlocated.'})
 # Eight ground branches share a counted descent, with room outside both
 # the populated controller and the full3mm junction host.
 sections['control-ground-descent']=(cq.Solid.makeCylinder(3.2,21.4,cq.Vector(-25.5,394.05,326.4),cq.Vector(0,0,1)),{'conductor_count':8,'scope':'Eight retained reservoir ground conductors; centreX−25.5,Y394.05,Z326.4..347.8.'})
 lower_a,lower_a_record=sweep([forks['A']['ground']['point'],[-57.8,394.05,326.4],[-35,394.05,326.4]],4.3,4.7)
 lower_b,lower_b_record=sweep([forks['B']['ground']['point'],[-29,394.05,326.4]],4.3,4.7)
 lower_merge=hull(circle_points((-35,394.05,326.4),(1,0,0),4.3)+
                  circle_points((-29,394.05,326.4),(0,-1,0),4.3)+
                  circle_points((-25.5,394.05,326.4),(0,0,1),6.4))
 sections['control-ground-lower-fanout']=(cq.Compound.makeCompound([lower_a,lower_b,lower_merge]),{
  'conductor_count':8,'four_wire_branches':[lower_a_record,lower_b_record],
  'scope':'Two distinct4-wire branches continue normally from the service forks and meet the counted8-wire descent in a local unsleeved dressing region. BranchA has exactR4.7 turns; individual turns in the local merge remain unlocated.'})
 az=float(np.mean([ports['wago-reeds-a:'+str(i)]['point'][2] for i in [2,3,4,5]]))
 bx=float(np.mean([ports['wago-reeds-b:'+str(i)]['point'][0] for i in [2,3,4,5]]))
 ground_specs=[('A','wago-reeds-a',[2,3,4,5],[[-82,394.05,az],[-82,390.1,az],[-82,390.1,347.8],[-38,390.1,347.8]]),
               ('B','wago-reeds-b',[2,3,4,5],[[bx,368.1,340.9],[bx,368.1,348.3],[bx,384.95,348.3],[-25.5,384.95,348.3]])]
 for r,owner,indices,points in ground_specs:
  contacts=[ports[owner+':'+str(i)] for i in indices];s,record=sweep(points,4.3)
  begin=port(owner,points[1],(0,-1,0) if r=='A' else (0,0,1),'Four counted ground clamps')
  fan=envelope_fanout(contacts,begin,4.3)
  sections['control-ground-upper-'+r]=(cq.Compound.makeCompound([s,fan]),{**record,'conductor_count':4,'clamp_ports':contacts,'scope':'Counted outer route and nominal clamp fanout; individual formed wires are unlocated.'})
 merger_turn,_=sweep([[-38,390.1,347.8],[-25.5,390.1,347.8],[-25.5,394.05,347.8]],4.3)
 merger=cq.Compound.makeCompound([merger_turn,hull(circle_points((-25.5,394.05,347.8),(0,1,0),4.3)+circle_points((-25.5,384.95,348.3),(1,0,0),4.3)+circle_points((-25.5,394.05,347.8),(0,0,1),6.4))])
 sections['control-ground-upper-merger']=(merger,{'conductor_count':8,'scope':'Two physically distinct4-wire approaches merge into the counted8-wire descent; named unsleeved dressing region, with individual constituent turns unlocated.'})
 # Preserve the inherited13-place flat bare corridor. Eleven fixed branches
 # use this forward portion; the two changed source returns leave aft of it.
 sections['control-fixed-manifold-ribbon']=(cq.Solid.makeBox(5.1,152,8.5,cq.Vector(92.075,178,242.75)),{'conductor_count':11,'capacity_count':13,'cross_section_mm':[5.1,8.5],'scope':'Three1.7mm bare ribbon layers, retained accepted straight corridor.'})
 manifold_fan,manifold_docks,manifold_record=manifold_transition()
 sections['control-manifold-aft-fanout']=(manifold_fan,manifold_record)
 meter_shape,meter_docks,meter_record=meter_pigtail(ports)
 sections['control-meter-pigtail']=(meter_shape,meter_record)
 relay_shape,relay_dock,relay_record=relay_logic_fork(ports)
 sections['control-relay-logic-fork']=(relay_shape,relay_record)
 network=[]
 for g in groups:
  src=[ports[k] for k in g['from_keys']];dst=[ports[k] for k in g['to_keys']]
  owner=src[0]['owner'];count=g['conductor_count'];diameter=DIAMETER[count]
  if g['name'].startswith('loom-wago-reeds-') and dst[0]['label'].startswith('Reservoir'):continue
  if g['name'].startswith('loom-J'):
   p=np.asarray([s['point'] for s in src]).mean(axis=0);header=g['name'].split('-')[1]
   if header in ['J1','J2']:p[2]=329.8;a=port(owner,p,(0,1,0),header+' counted aft bundle dock')
   elif header=='J11':p[0]+=13.1;p[2]=333.25;a=port(owner,p,(0,0,-1),header+' counted downward bundle dock')
   elif header=='J13':p[2]=320.;a=port(owner,p,(-1,0,0),header+' counted below-header bundle dock')
   elif header=='J4':p[2]=325.15;a=port(owner,p,(0,-1,0),header+' counted under-board bundle dock')
   elif src[0]['point'][0]>0:p[0]+=8.4;p[2]=330.6;a=port(owner,p,(1,0,0),header+' counted bundle dock')
   else:p[2]=317.15 if count>=3 else 317.5;a=port(owner,p,(-1,0,0),header+' counted bundle dock')
   # The nominal connector free plane follows the native PCB. The independent
   # routing docks stay on their proved bay planes: lowering the aft dock
   # would consume the supply crown, and the east docks clear the pump crown.
   fanouts[g['name']+'-source']=(envelope_fanout(src,a,diameter),owner,g['name'])
  else:
   p=np.asarray([s['point'] for s in src]).mean(axis=0);v=np.asarray(src[0]['axis']);p+=v*8.4
   if abs(v[2])>.9 and owner.startswith('wago-'):
    p[2]=347.8;v=np.array([0.,-1.,0.])
   a=port(owner,p,v,'Counted junction bundle dock');fan=envelope_fanout(src,a,diameter)
   if owner.startswith('wago-') and count==1:a,fan=single_junction_exit(src[0],1 if g['name']=='loom-wago-mana-coil-v-b' else -1)
   fanouts[g['name']+'-source']=(fan,owner,g['name'])
  if g['name'].endswith('-reed-A') or g['name'].endswith('-reed-B'):
   reservoir=g['name'][-1];b=forks[reservoir]['signals']
  elif dst[0]['owner']=='retained-manifold-loom':
   header=g['name'].split('-')[1];b=manifold_docks[header]
  elif dst[0]['owner']=='digiten-flow':
   b=meter_docks['signals' if count==2 else 'ground']
  elif g['name']=='loom-J5-relay-logic-cluster':b=relay_dock
  else:
   p=np.asarray([s['point'] for s in dst]).mean(axis=0);v=np.asarray(dst[0]['axis']);p+=v*8.4
   if abs(v[2])>.9 and dst[0]['owner'].startswith('wago-'):
    p[2]=347.8;v=np.array([0.,-1.,0.])
   b=port(dst[0]['owner'],p,v,'Counted device bundle dock');fan=envelope_fanout(dst,b,diameter)
   if dst[0]['owner'].startswith('wago-') and count==1:b,fan=single_junction_exit(dst[0])
   if dst[0]['owner']=='keystone-jack':b,fan=keystone_exit(dst)
   if g['name']=='loom-wago-mana-coil-v-b':b,fan=source_b_feed_exit(dst[0])
   fanouts[g['name']+'-target']=(fan,dst[0]['owner'],g['name'])
  network.append({**g,'from_dock':a,'to_dock':b,'diameter_mm':diameter,'bend_radius_mm':BEND_RADIUS[count],
                  'nominal_packing_radius_mm':PACKING_RADIUS[count],'minimum_nominal_conductor_centre_radius_mm':BEND_RADIUS[count]-PACKING_RADIUS[count],
                  'nominal_packing':'1.7mm wires; explicit circular outer packing reserve'})
 # One authored dressing volume per physical header. Distinct outgoing net
 # groups share this volume rather than claiming intersecting independent
 # connector bodies. Shared J5 supply/ground branches need the named factory
 # fanout; this source does not imply two wires in one purchased crimp.
 for header in sorted({n['name'].split('-')[1] for n in network if n['name'].startswith('loom-J')}):
  related=[n for n in network if n['name'].startswith('loom-'+header+'-')]
  if len(related)>1:
   # Complete circular branch exits have1mm nominal separation. The header
   # dressing region preserves every canonical input pin and names any shared
   # rail fork, without placing multiple branches at an identical dock.
   axis=0 if header in ['J1','J2','J4'] else 1
   source_contacts={k:ports[k] for n in related for k in n['from_keys']}
   centre=-6.25 if header=='J4' else float(np.mean([p['point'][axis] for p in source_contacts.values()]))
   span=sum(n['diameter_mm'] for n in related)+(len(related)-1)
   at=centre-span/2
   for n in sorted(related,key=lambda n:n['from_dock']['point'][axis]):
    n['from_dock']['point'][axis]=at+n['diameter_mm']/2;at+=n['diameter_mm']+1
  shapes=[];points=[];contacts={}
  flat_escape=None;flat_profile=None
  if header=='J1':
   branch=next(n for n in related if 'retained-manifold' in n['name'])
   _,y,z=branch['from_dock']['point']
   dock,flat_escape,flat_profile,flat_record=j1_manifold_flat_departure(y,z)
   branch['from_dock']=dock;branch['header_bare_escape']=flat_record
  for n in related:
   key=n['name']+'-source';shapes.append(fanouts.pop(key)[0]);n['from_dock']['owner']='control-header-'+header+'-fanout'
   for k in n['from_keys']:contacts[k]=ports[k]
   points+=flat_profile if header=='J1' and n is branch else circle_points(n['from_dock']['point'],n['from_dock']['axis'],n['diameter_mm'])
  combined=hull(contact_profile(list(contacts.values()))+points)
  if flat_escape is not None:combined=cq.Compound.makeCompound([combined,flat_escape])
  fanouts['header-'+header+'-fanout']=(combined,'pcba',[n['name'] for n in related])
 for n in network:
  if n['name']+'-source' in fanouts:n['from_dock']['owner']='control-'+n['name']+'-source'
  if n['name']+'-target' in fanouts:n['to_dock']['owner']='control-'+n['name']+'-target'
  for endpoint in ['from_dock','to_dock']:
   p=n[endpoint];p['diameter_mm']=n['diameter_mm'];p['bend_radius_mm']=n['bend_radius_mm'];p['label']=n['name']+' '+endpoint
   # Admit an exact native-proved endpoint in a hollow that a filled ranking
   # raster closes. These normal leads remain fully checked against hardware,
   # previous wires, and every other route's future lead reservation.
   p['lead_paths']=[[p['point'],(np.asarray(p['point'])+np.asarray(p['axis'])*d).tolist()] for d in [5.4,6.8,8.4,12.6,16.8]]
   if p['owner']=='control-loom-J11-retained-mq6-loom-target' and p['axis']==[0.,1.,0.]:
    x,y,z=p['point'];p['lead_paths'].insert(0,[[x,y,z],[x,y+9.4,z],[x,y+9.4,260],[-86,y+9.4,260]])
 for prepared_path in [HERE/'controls-prepared-leads.json',HERE/'controls-core-boundaries.json',HERE/'controls-dock-repair.json',HERE/'controls-target-repair.json',HERE/'controls-selected-departures.json']:
  if not prepared_path.exists():continue
  prepared=json.loads(prepared_path.read_text())
  for n in network:
   for endpoint in ['from_dock','to_dock']:
    p=n[endpoint];r=prepared.get('prepared_leads',{}).get(p['label'])
    if r and np.linalg.norm(np.asarray(r['port_point'])-np.asarray(p['point']))<1e-6 and r['diameter_mm']==n['diameter_mm'] and r['bend_radius_mm']==n['bend_radius_mm']:
     leads=r['lead_paths']
     if prepared_path.name in ['controls-dock-repair.json','controls-target-repair.json']:
      # The future reservation uses the shortest complete curved departure.
      # Continuing a neighboring source's working prefix over this source
      # would consume an otherwise viable separate branch.
      leads=sorted(leads,key=lambda points:(len(points)!=3,len(points)==2,len(points)))
     p['lead_paths']=leads if r.get('required_path') else leads+p['lead_paths']
     if r.get('required_path'):p['required_path']=True
 return data,network,sections,fanouts

def canonical_coverage(data,network):
 """Name the occupied run and static continuations for every canonical net."""
 covered={}
 for n in network:
  for job in n['jobs']:
   continuation=[]
   target=n['to_dock']['owner']
   if target=='control-manifold-aft-fanout':continuation=['control-manifold-aft-fanout','control-fixed-manifold-ribbon']
   elif target in ['control-service-fork-A','control-service-fork-B']:
    letter=target[-1];continuation=[target,'control-service-reeds-'+letter]
   elif target in ['control-meter-pigtail','control-relay-logic-fork']:continuation=[target]
   covered[job['name']]={'grouped_route':'control-'+n['name'],'static_continuations':continuation,
    'from_key':job['from'],'to_key':job['to'],'topology':job['topology']}
 for job in data['jobs']:
  if job['name'] in covered:continue
  if job['name'].startswith(('fanout-A-GND','fanout-B-GND')):
   letter=job['name'].split('-')[1]
   covered[job['name']]={'grouped_route':None,'static_continuations':['control-ground-upper-'+letter,'control-ground-upper-merger','control-ground-descent','control-ground-lower-fanout','control-service-fork-'+letter,'control-service-reeds-'+letter],
    'from_key':job['from'],'to_key':job['to'],'topology':job['topology']}
  else:raise ValueError('Canonical net has no occupied control coverage: '+job['name'])
 return covered

def preserve_received_bounds(name,part,held):
 """Keep the held record's literals after byte identity and native bounds checks."""
 if part['brep']!=held['brep']or part['sha256']!=held['sha256']:
  raise ValueError('Received bound preservation requires the exact held native: '+name)
 delta=max(abs(a-b)for a,b in zip(part['bounds'],held['bounds']))
 if delta>1e-9:raise ValueError('Received native bounds exceed representational precision: '+name)
 record=dict(part);record['bounds']=list(held['bounds'])
 return record,{'check':'held native bound literals preserved','part':name,
  'maximum_representation_delta_mm':delta,'sha256':part['sha256'],'pass':True}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--definitions-only',action='store_true');parser.add_argument('--reserves-only',action='store_true');parser.add_argument('--fanouts-only',action='store_true');parser.add_argument('--only');parser.add_argument('--resume-failed',action='store_true');parser.add_argument('--search-states',type=int,default=600000)
 parser.add_argument('--hardware-only',action='store_true',help='Plan rigid-hardware-clear controls before the peer power reroute; final pass stays false')
 parser.add_argument('--received-statics',action='store_true',help='Validate existing fixed-region native bytes against the current recipe and preserve them during evidence refresh')
 parser.add_argument('--received-cutters',action='store_true',help='Strictly receive all75 accepted occupied bodies and cutters; validate recipes and parent fit without writing native bytes');args=parser.parse_args()
 if args.only and args.resume_failed:parser.error('--only and --resume-failed are mutually exclusive')
 if args.received_cutters and (not args.resume_failed or not args.received_statics or args.only or args.hardware_only or args.definitions_only or args.reserves_only or args.fanouts_only):
  parser.error('--received-cutters requires a complete --resume-failed --received-statics validation')
 source_inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
  for p in [Path(__file__),HERE/'controls_harness.py',HERE/'controls.py',HERE/'native_harness.py',HERE/'circular_clearance.py',HERE/'received_cutters.py',HERE/'reed_b_flat.py',STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py'] if p.exists()}
 accepted_packet=json.loads((HERE/'controls-candidate.json').read_text()) if args.received_cutters else None
 frozen_assets={}
 if accepted_packet is not None:
  if len(accepted_packet.get('parts',{}))!=75 or len(accepted_packet.get('clearance_cutters',{}))!=75 or sum('from_dock' in r for r in accepted_packet.get('control_routes',{}).values())!=26:
   raise ValueError('Strict received-cutter mode requires the complete accepted75-part/26-route packet')
  for name,part in accepted_packet['parts'].items():
   row={}
   for kind,r in [('body',part),('cutter',accepted_packet['clearance_cutters'][name])]:
    raw=(ROOT/r['brep']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('Accepted control '+kind+' hash differs before validation: '+name)
    row[kind]=raw
   frozen_assets[name]=row
 manifest_inputs={};manifest_content={}
 for relative in ['funnel/candidate.json','funnel/shells.json','pump/candidate.json','pump/fluid24-candidate.json','pump/electrical-ends.json',
  'routing/candidate.json','routing/tube-hosts.json','structure/candidate.json','structure/roof-hatch.json',
  'mounts/candidate.json','mounts/roof-candidate.json','mounts/floor-candidate.json','mounts/fluid-candidate.json',
  'mounts/body-candidate.json','mounts/wr-candidate.json','mounts/needle-candidate.json','mounts/check-tee-candidate.json','mounts/water5-hosts.json',
  'mounts/junction-port-approaches.json','wiring/lower-lead-exits.json','wiring/power-candidate.json',
  'wiring/controls-prepared-leads.json','wiring/controls-core-boundaries.json','wiring/controls-dock-repair.json',
  'wiring/controls-target-repair.json','wiring/controls-selected-departures.json','wiring/controls-selected-routes.json',
  'wiring/reed-a-service-route.json','wiring/reed-b-split-route.json']:
  p=STUDY/relative
  if p.exists():
   raw=p.read_bytes();key=str(p.relative_to(ROOT));manifest_inputs[key]=hashlib.sha256(raw).hexdigest();manifest_content[key]=content_sha256(json.loads(raw))
 OUT.mkdir(parents=True,exist_ok=True);data,network,sections,fanouts=definition()
 authored_path=HERE/'controls-selected-routes.json'
 authored_routes=json.loads(authored_path.read_text()).get('routes',{}) if authored_path.exists() else {}
 received_static_bytes={};received_native_inputs={};received_recipe_checks=[]
 def receive_static(name,recipe):
  path=OUT/(name+'.brep');raw=path.read_bytes();received=cq.Shape.importBrep(BytesIO(raw))
  missing_received=sum(abs(s.cut(recipe,tol=.0001).Volume(tol=1e-9)) for s in received.Solids())
  missing_recipe=sum(abs(s.cut(received,tol=.0001).Volume(tol=1e-9)) for s in recipe.Solids())
  received_signature=analytic_geometry_signature(received);recipe_signature=analytic_geometry_signature(recipe)
  row={'part':name,'volume_delta_mm3':abs(received.Volume(tol=1e-9)-recipe.Volume(tol=1e-9)),
   'area_delta_mm2':abs(received.Area()-recipe.Area()),'maximum_bounds_delta_mm':max(abs(a-b) for a,b in zip(bounds(received),bounds(recipe))),
   'received_missing_mm3':missing_received,'recipe_missing_mm3':missing_recipe,
   'received_analytic_geometry_sha256':received_signature,'recipe_analytic_geometry_sha256':recipe_signature,
   'scope':'Exact native plane/cylinder/torus supports, line/circle trimming ranges, face/wire orientations and solid ownership agree at1e-8mm. Equality does not depend on an ambiguous identical-shape Boolean.'}
  row['pass']=received.isValid() and row['volume_delta_mm3']<.001 and row['area_delta_mm2']<.001 and row['maximum_bounds_delta_mm']<1e-6 and received_signature==recipe_signature
  if not row['pass']:raise ValueError('Received fixed control region differs from its current geometry recipe: '+str(row))
  received_static_bytes[name]=raw;received_native_inputs[name]={'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest()};received_recipe_checks.append(row)
  return received
 if args.received_statics:
  sections={n:(receive_static(n,s),r) for n,(s,r) in sections.items()}
  fanouts={n:(receive_static('control-'+n,s),owner,loom) for n,(s,owner,loom) in fanouts.items()}
 source_inputs.update(data.get('source_sha256',{}))
 service_native_inputs={}
 for filename in ['reed-a-service-route.json','reed-b-split-route.json']:
  p=HERE/filename
  if not p.exists():continue
  service=json.loads(p.read_text())
  if not service.get('pass'):continue
  for label,r in [('trunk',service),('fork',service.get('aft_fork',{}))]:
   if not r.get('brep'):continue
   name=filename.removesuffix('.json')+'-'+label
   service_native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()}
 meta={**data,'loom_network':network,'canonical_job_coverage':canonical_coverage(data,network),'service_sections':{n:r for n,(_,r) in sections.items()},'checks':received_recipe_checks,'scope':'Canonical conductor topology; grouped occupied outer routes and named nominal fanouts. No individual formed conductor path is called measured.'}
 (HERE/'controls-loom-interfaces.json').write_text(json.dumps(meta,indent=2)+'\n')
 if args.definitions_only:print(json.dumps({'conductor_jobs':len(data['jobs']),'grouped_routes':len(network),'sections':len(sections),'fanouts':len(fanouts)},indent=2));return
 if args.reserves_only or args.fanouts_only:
  import audit,baseline
  models,records,_,_,_=audit.collect();saved=baseline.prepare()
  for name,r in saved['parts'].items():
   if name in records or not broad(r['bounds'],[-107.5,178,241,107.5,465.3,355]):continue
   records[name]={'brep':str((baseline.CACHE/r['file']).relative_to(ROOT))};models[name]=cq.Shape.importBrep(str(baseline.CACHE/r['file']))
  records.update(protected_nameplate_records());models.update(protected_nameplate_models())
  body_models,body_records=passed_body_models();models.update(body_models);records.update(body_records)
  lower_models,lower_records=lower_lead_models();models.update(lower_models);records.update(lower_records)
  mounts=json.loads((STUDY/'mounts/candidate.json').read_text())
  for name,working in mounts['working_envelopes'].items():
   if 'levers' in working:
    records[name+'-lever-working-space']=working['levers'];models[name+'-lever-working-space']=cq.Shape.importBrep(str(ROOT/working['levers']['brep']))
  target='control-fanouts-check.json'if args.fanouts_only else'control-reserves.json'
  held_static_records=json.loads((HERE/target).read_bytes())['parts']if args.received_statics else{}
  blocked={};out={'parts':{},'native_checks':[],'scope':'Native-counted transit obstacles for concurrent power planning; final viewer consumes controls-candidate only.'}
  source_native_inputs={}
  for name,shape in list(models.items()):
   if name.startswith(('control-','wire-','power-')) or name=='rear-roof-hatch':continue
   r=records.get(name)
   if r and r.get('brep'):
    raw=(ROOT/r['brep']).read_bytes();shape=cq.Shape.importBrep(BytesIO(raw));source_native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
   if name.startswith(('enclosure-back-top','enclosure-front-top')):
    shape=shape.intersect(cq.Solid.makeBox(240,147.7,130,cq.Vector(-120,178,240)))
   blocked[name]=shape
  out['native_inputs']=source_native_inputs
  out['native_inputs'].update(service_native_inputs)
  out['native_inputs'].update(received_native_inputs)
  out['checks']=received_recipe_checks
  candidates={n:(s,r,(['cold-core/foam-cap-lid-top'] if 'service-reeds-' in n else [])+(['wago-reeds-'+n[-1].lower()] if n in ['control-ground-upper-A','control-ground-upper-B'] else [])+(['digiten-flow'] if n=='control-meter-pigtail' else [])+(['relay-1','relay-2'] if n=='control-relay-logic-fork' else [])) for n,(s,r) in sections.items()}
  if args.fanouts_only:candidates={n:(s,{'conductor_count':sum(q['conductor_count'] for q in network if q['name'] in (loom if isinstance(loom,list) else [loom])),'scope':'Explicit nominal connector-to-bundle fanout working volume. Individual constituent wire dressing remains unlocated.'},[owner]) for n,(s,owner,loom) in fanouts.items()}
  for name,(shape,record,owners) in candidates.items():
   hits=native_hits(shape,blocked,owners)
   row={'part':name,'valid':shape.isValid(),'bounds':bounds(shape),'native_interferences':hits,'pass':shape.isValid() and not hits};out['native_checks'].append(row)
   if not row['pass']:continue
   native_name='control-'+name if args.fanouts_only else name
   p=OUT/(native_name+'.brep')
   if native_name in received_static_bytes:
    if p.read_bytes()!=received_static_bytes[native_name]:raise ValueError('Received static native changed during validation: '+name)
   else:shape.exportBrep(str(p))
   out['parts'][name]={'brep':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bounds':bounds(shape),'conductor_count':record['conductor_count'],'detail':record.get('scope','Counted service8-wire route')}
   if args.received_statics:
    out['parts'][name],literal_check=preserve_received_bounds(native_name,out['parts'][name],held_static_records[name])
    out['checks'].append(literal_check)
  out['input_geometry_sha256']={n:loaded_digest(s) for n,s in blocked.items() if s.Solids()}
  out['source_inputs']=source_inputs;out['source_sha256']=source_inputs;out['read_time_manifest_sha256']=manifest_inputs;out['manifest_content_sha256']=manifest_content
  out['source_drift']=[n for n,r in out['native_inputs'].items() if hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
  out['source_drift']+=[n for n,h in source_inputs.items() if hashlib.sha256((ROOT/n).read_bytes()).hexdigest()!=h]
  out['manifest_drift']=[n for n,h in manifest_content.items() if manifest_content_sha256(ROOT/n)!=h]
  out['pass']=all(r['pass'] for r in out['native_checks']) and not out['source_drift'] and not out['manifest_drift'];target='control-fanouts-check.json' if args.fanouts_only else 'control-reserves.json';(HERE/target).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True);return
 selected=[n for n in network if not args.only or args.only in n['name']]
 route_ports=[p for n in selected for p in [n['from_dock'],n['to_dock']]]
 guide=ControlsGuide(route_ports,diameter=1.7,hardware_only=args.hardware_only)
 guide.native_inputs.update(service_native_inputs)
 guide.native_inputs.update(received_native_inputs)
 guide.max_states=args.search_states
 static_checks=static_pair_checks(sections,fanouts)
 result={**meta,'parts':{},'control_routes':{},'replacement_names':[],'intended_contacts':[list(pair) for pair in STATIC_JOINTS],'clearance_cutters':{},'failures':[],
 'hardware_only':args.hardware_only,
 'static_pair_checks':static_checks,
 'native_inputs':guide.native_inputs,'source_inputs':source_inputs,'read_time_manifest_sha256':manifest_inputs,'manifest_content_sha256':manifest_content,
 'input_geometry_sha256':{n:loaded_digest(s) for n,s in guide.obstacles.items()},
 'qualification_limits':['Purchased XH/IDC/valve and representative relay clamp contacts remain the interface reservations named in controls-interfaces.json.',
 'Grouped exterior capacity follows1.7mm stock and stated packing. R3.4 loom-centre bends and convex fanout regions do not locate or qualify each constituent conductor bend, terminal insertion, retention or sleeve fit.',
 'Actual accepted reed bores and the complete retained bare forward corridor are preserved. Unlocated probe/carbonator/meter/dry-comparator lead interfaces remain named reservations.',
 'Native occupied geometry does not qualify mains insulation, thermal output, vibration or lifetime.']}
 received_group_assets={}
 old_clearance_records=json.loads((HERE/'controls-candidate.json').read_text()).get('clearance_cutters',{}) if (HERE/'controls-candidate.json').exists() else {}
 def export(name,shape,record,owners=()):
  received_bytes=received_static_bytes.get(name,received_group_assets.get(name,{}).get('bytes'))
  cached_cutter=None;cached_cut_bytes=None
  saved_cutter=old_clearance_records.get(name) if received_bytes is not None else None
  if args.received_cutters:
   if name not in frozen_assets or received_bytes!=frozen_assets[name]['body']:raise ValueError('Strict received control exterior was not preserved: '+name)
   saved_cutter=accepted_packet['clearance_cutters'][name]
   raw=(ROOT/saved_cutter['brep']).read_bytes()
   if raw!=frozen_assets[name]['cutter']:raise ValueError('Accepted control cutter changed during validation: '+name)
   cached_cutter=cq.Shape.importBrep(BytesIO(raw));cached_cut_bytes=raw
   from received_cutters import correspondence
   proof=correspondence(shape,cached_cutter,accepted_packet['control_routes'][name])
   proof.update(part=name,received_body_sha256=hashlib.sha256(received_bytes).hexdigest(),received_cutter_sha256=hashlib.sha256(raw).hexdigest())
   result['checks'].append(proof)
   if not proof['pass']:raise ValueError('Received control cutter differs from the complete clearance recipe: '+str(proof))
   guide.native_inputs[name+'-received-clearance']={'brep':saved_cutter['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
   cutter=cached_cutter
   if 'clearance_member_proof' in accepted_packet['control_routes'][name]:record['clearance_member_proof']=accepted_packet['control_routes'][name]['clearance_member_proof']
  elif saved_cutter and (ROOT/saved_cutter['brep']).exists():
   raw=(ROOT/saved_cutter['brep']).read_bytes()
   if hashlib.sha256(raw).hexdigest()==saved_cutter['sha256']:
    candidate=cq.Shape.importBrep(BytesIO(raw))
    if candidate.isValid() and all(abs(s.cut(candidate,tol=.0001).Volume(tol=1e-9))<.001 for s in shape.Solids()):
     cached_cutter=candidate;cached_cut_bytes=raw
     guide.native_inputs[name+'-received-clearance']={'brep':saved_cutter['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
  if args.received_cutters:pass
  elif 'points_mm' in record and abs(shape.Volume(tol=1e-9)-math.pi*(record['diameter_mm']/2)**2*record['length_mm'])<.001:
   # Circular looms have their complete analytic centreline. Reusing it with
   # a larger circular section avoids offsetting a many-face pipe shell.
   cutter=cached_cutter if cached_cutter is not None else sweep(record['points_mm'],record['diameter_mm']+2.,record['radius_mm'])[0]
   missing=abs(shape.cut(cutter,tol=.0001).Volume(tol=1e-9))
   member_containment=[{'member':index,'missing_mm3':abs(member.cut(cutter,tol=.0001).Volume(tol=1e-9))}
    for index,member in enumerate(shape.Solids())]
   if any(row['missing_mm3']>.001 for row in member_containment):
    cached_cut_bytes=None
    from circular_clearance import paired_members
    authored=shape if len(shape.Solids())==1 else sweep(record['points_mm'],record['diameter_mm'],record['radius_mm'])[0]
    shape,cutter,proof=paired_members(authored,record['diameter_mm'])
    proof['whole_pipe_boolean_missing_mm3']=missing
    if abs(proof['complete_length_mm']-record['length_mm'])>.0001:raise ValueError('Paired circular-member path differs from the authored centreline')
    hits=native_hits(shape,{**guide.obstacles,**guide.wires},[name,*owners])
    if hits:raise ValueError('Received circular-member exterior fails native clearance: '+str(hits))
    record['clearance_member_proof']=proof
    if name in guide.wires:guide.wires[name]=shape
   else:
    record['clearance_member_proof']={'complete_length_mm':record['length_mm'],'radial_air_mm':1.,
     'whole_pipe_boolean_missing_mm3':missing,
     'clearance_union_containment_checks':[{**row,'pass':True} for row in member_containment],
     'clearance_union_valid_one_solid':cutter.isValid() and len(cutter.Solids())==1,
     'scope':'Every actual emitted cylinder/arc member is contained by the valid concentric enlarged analytic sweep, with independently measured zero missing member volume.'}
  else:cutter=cached_cutter if cached_cutter is not None else clearance_envelope(shape,fused_union=record.get('clearance_fused_union',False))
  path=OUT/(name+'.brep')
  if received_bytes is not None:
   if path.read_bytes()!=received_bytes:raise ValueError('Accepted control native changed during rebind: '+name)
  else:shape.exportBrep(str(path))
  vs,ts=shape.tessellate(.15,.10);mesh=path.with_suffix('.json');mesh.write_text(json.dumps({'vertices':[[v.x,v.y,v.z] for v in vs],'triangles':[list(t) for t in ts]},separators=(',',':'))+'\n')
  result['parts'][name]={'brep':str(path.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':bounds(shape),'role':'wiring','color_role':'control','conductor_count':record.get('conductor_count'),'hardware_pass':not record.get('hardware_interferences',[]),'detail':record.get('scope',f"Counted{record.get('conductor_count',1)}-conductor control loom exterior.")}
  if args.received_cutters:
   result['parts'][name],literal_check=preserve_received_bounds(name,result['parts'][name],accepted_packet['parts'][name])
   result['checks'].append(literal_check)
  if 'physical_section_proof' in record:
   record['physical_section_proof']['physical_sha256']=result['parts'][name]['sha256']
   record['physical_section_proof']['generator_sha256']=source_inputs['future/pump-first-layout-study/wiring/circular_clearance.py']
  result['control_routes'][name]=record
  path.with_suffix('.route.json').write_text(json.dumps({'part':result['parts'][name],'record':record},indent=2)+'\n')
  for owner in owners:result['intended_contacts'].append([name,owner])
  cutpath=OUT/(name+'-clearance.brep')
  if cached_cut_bytes is not None:
   if cutpath.read_bytes()!=cached_cut_bytes:raise ValueError('Accepted control cutter changed during rebind: '+name)
  else:cutter.exportBrep(str(cutpath))
  result['clearance_cutters'][name]={'brep':str(cutpath.relative_to(ROOT)),'sha256':hashlib.sha256(cutpath.read_bytes()).hexdigest(),
                                    'running_room_mm':1.,'scope':'Circular looms use their analytic centreline with radius enlarged1mm, with separately contained cylinder/arc members when the whole-pipe Boolean is ambiguous; planar convex dressing members use bounded cube Minkowski growth. Apply only to the admitted aft-bay shell stock.'}
 def exact(shape,owners=()):return native_hits(shape,guide.obstacles,owners)
 if not static_checks['pass']:result['failures'].append({'route':'static-controls','reason':'Distinct occupied static regions intersect','hits':static_checks['failures']})
 for name,(shape,record) in sections.items():
  owners=['cold-core/foam-cap-lid-top'] if 'service-reeds-' in name else[]
  if name in ['control-ground-upper-A','control-ground-upper-B']:owners+=['wago-reeds-'+name[-1].lower()]
  if name=='control-meter-pigtail':owners+=['digiten-flow']
  if name=='control-relay-logic-fork':owners+=['relay-1','relay-2']
  hits=exact(shape,owners);record['native_interferences']=hits
  hardware_hits=[r for r in hits if not r['part'].startswith(('wire-','power-'))];record['hardware_interferences']=hardware_hits
  if hits:result['failures'].append({'route':name,'reason':'Fixed counted section fails current native clearance','hits':hits})
  if not hardware_hits:export(name,shape,record,owners)
 for name,(shape,owner,loom) in fanouts.items():
  hits=exact(shape,[owner]);hardware_hits=[r for r in hits if not r['part'].startswith(('wire-','power-'))];record={'scope':'Explicit nominal connector-to-bundle fanout working volume. Individual constituent wire dressing remains unlocated.','owner':owner,'loom':loom,'conductor_count':sum(q['conductor_count'] for q in network if q['name'] in (loom if isinstance(loom,list) else [loom])),'native_interferences':hits,'hardware_interferences':hardware_hits}
  if hits:result['failures'].append({'route':name,'reason':'Fanout working volume fails current native clearance','hits':hits})
  if not hardware_hits:export('control-'+name,shape,record,[owner])
 # Every counted fixed service and fanout exterior stays occupied, including
 # a provisional hardware conflict awaiting a peer's restraint correction.
 # Only the route's explicitly named end dressing solid is a mate.
 chunks=[]
 fixed_models={n:s for n,(s,_) in sections.items()}
 fixed_models.update({'control-'+n:s for n,(s,_,_) in fanouts.items()})
 for name,shape in fixed_models.items():
  r=result['parts'].get(name,{'brep':str((OUT/(name+'.brep')).relative_to(ROOT))})
  guide.obstacles[name]=shape;guide.models[name]=shape;guide.records[name]=r
  chunks.append(control_occupied_points(name,shape,r['brep']))
 if chunks:guide.voxels=np.vstack([guide.voxels,*chunks])
 if args.resume_failed:
  previous=json.loads((HERE/'controls-candidate.json').read_text())
  # Each exported seed has its own exact record, so an interrupted whole
  # check cannot discard a verified native exterior between publications.
  for n in selected:
   name='control-'+n['name'];sidecar=OUT/(name+'.route.json')
   if not sidecar.exists():continue
   saved=json.loads(sidecar.read_text());old=saved['record'];part=saved['part'];path=ROOT/part['brep']
   if any(old.get(key)!=n[key] for key in ['from_dock','to_dock','diameter_mm','bend_radius_mm']):continue
   if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=part['sha256']:continue
   previous['parts'][name]=part;previous['control_routes'][name]=old
  future_models={}
  for pending in selected:
   old=previous.get('control_routes',{}).get('control-'+pending['name'])
   if old and all(old.get(key)==pending[key] for key in ['from_dock','to_dock','diameter_mm','bend_radius_mm']):continue
   for end in ['from_dock','to_dock']:
    p=pending[end]
    points=p['lead_paths'][0]
    future_models['reserved-lead-'+p['label']]=sweep(points,p['diameter_mm'],p['bend_radius_mm'])[0]
  for n in selected:
   name='control-'+n['name'];record=previous.get('control_routes',{}).get(name)
   if not record or any(record.get(key)!=n[key] for key in ['from_dock','to_dock','diameter_mm','bend_radius_mm']):continue
   if name in authored_routes and record.get('points_mm')!=authored_routes[name]['points_mm']:continue
   part=previous['parts'][name];path=ROOT/part['brep']
   if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=part['sha256']:continue
   raw=path.read_bytes();received=cq.Shape.importBrep(BytesIO(raw));owners=[n['from_dock']['owner'],n['to_dock']['owner']]
   from circular_clearance import paired_members,CircularSelfIntersection
   section=record.get('physical_section_proof',{})
   receipt=(section.get('physical_sha256')==part['sha256'] and section.get('generator_sha256')==source_inputs['future/pump-first-layout-study/wiring/circular_clearance.py'] and section.get('members') and len(received.Solids())==len(section['members']))
   if args.received_cutters and not receipt:raise ValueError('Strict received route lacks its accepted exact physical-member receipt: '+name)
   if receipt:
    if not received.isValid() or not all(r['pass'] for r in section['physical_member_self_checks']) or not all(r['pass'] for r in section['tangent_full_section_seams']):raise ValueError('Received physical-member proof is invalid: '+name)
    shape=received
   else:
    authored=received if len(received.Solids())==1 else sweep(record['points_mm'],n['diameter_mm'],n['bend_radius_mm'])[0]
    try:shape,_,section=paired_members(authored,n['diameter_mm'],gap=0.,fuse_clearance=False)
    except CircularSelfIntersection as error:
     print('loom resume needs self-section reroute',name,error.indices,error.volume,flush=True);continue
   if abs(received.Volume(tol=1e-9)-section['member_section_volume_mm3'])>.001:
    raise ValueError('Received loom differs from its exact physical-member section volume: '+name)
   own_labels=[n[end]['label'] for end in ['from_dock','to_dock']]
   future={name:s for name,s in future_models.items() if name.removeprefix('reserved-lead-') not in own_labels}
   hits=native_hits(shape,{**guide.obstacles,**guide.wires,**future},owners)
   physical_air=[{'part':part,'air_mm':shape.distance(fluid)} for part,fluid in guide.physical_fluids.items() if broad(bounds(shape),bounds(fluid),1.) and shape.distance(fluid)<1.-1e-6]
   if physical_air:hits+=physical_air
   if hits:print('loom resume needs reroute',name,hits,flush=True);continue
   if receipt:
    received_group_assets[name]={'bytes':raw}
    guide.native_inputs[name]={'brep':part['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
   record['physical_section_proof']={key:section[key] for key in ['members','complete_length_mm','received_section_volume_mm3','member_section_volume_mm3','tangent_full_section_seams','open_end_centres_mm','physical_member_self_checks']}
   record['physical_section_proof']['scope']='Exact analytic member surfaces and full tangent section seams form one continuous exterior with zero native common between distinct physical members.'
   record['physical_member_native_interferences']=[]
   record['full_fluid_air_pass']=True
   record['minimum_unrelated_fluid_air_mm']=1.
   _,sample=sweep(record['points_mm'],n['diameter_mm'],n['bend_radius_mm'],with_centerline=True)
   guide.wires[name]=shape;guide.wire_diameters[name]=n['diameter_mm']
   guide.used_port_labels.update(own_labels)
   if not hasattr(guide,'wire_centers'):guide.wire_centers={}
   guide.wire_centers[name]=np.asarray(sample['centerline_samples_mm'])
   export(name,shape,{**record,'native_interferences':[],'hardware_interferences':[]},owners)
   if not args.received_cutters:
    result['pass']=False;(HERE/'controls-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
   print('loom resumed',name,flush=True)
 # Counted looms use the same native guide and complete exact sweeps as power.
 for n in selected:
  name='control-'+n['name']
  if name in result['control_routes']:continue
  if args.received_cutters:raise ValueError('Strict received validation cannot replace an occupied route that failed current parent fit: '+name)
  guide.diameter=n['diameter_mm'];guide.bend_radius=n['bend_radius_mm'];guide.refresh()
  try:
   if name in authored_routes:
    recipe=authored_routes[name]
    if any(recipe[key]!=n[key] for key in ['diameter_mm','bend_radius_mm','conductor_count']):raise ValueError('Authored control section differs from its canonical job count: '+name)
    if any(np.linalg.norm(np.asarray(recipe['points_mm'][i])-np.asarray(n[end]['point']))>1e-6 for i,end in [(0,'from_dock'),(-1,'to_dock')]):raise ValueError('Authored control endpoint differs from its canonical dressing mouth: '+name)
    from circular_clearance import paired_members
    authored,record=sweep(recipe['points_mm'],n['diameter_mm'],n['bend_radius_mm'])
    shape,_,section=paired_members(authored,n['diameter_mm'],gap=0.,fuse_clearance=False)
    owners=[n[end]['owner'] for end in ['from_dock','to_dock']]
    hits=native_hits(shape,{**guide.obstacles,**guide.wires},owners)
    physical_air=[{'part':part,'air_mm':shape.distance(fluid)} for part,fluid in guide.physical_fluids.items() if broad(bounds(shape),bounds(fluid),1.) and shape.distance(fluid)<1.-1e-6]
    if hits or physical_air:raise ValueError('Authored control exterior fails current native clearance: '+str(hits+physical_air))
    record['physical_section_proof']={key:section[key] for key in ['members','complete_length_mm','received_section_volume_mm3','member_section_volume_mm3','tangent_full_section_seams','open_end_centres_mm','physical_member_self_checks']}
    record.update(physical_member_native_interferences=[],full_fluid_air_pass=True,minimum_unrelated_fluid_air_mm=1.,selected_route_recipe=str(authored_path.relative_to(ROOT)),scope=recipe['scope'])
    guide.wires[name]=shape;guide.wire_diameters[name]=n['diameter_mm'];guide.used_port_labels.update(n[end]['label'] for end in ['from_dock','to_dock'])
   else:shape,record=guide.route(n['from_dock'],n['to_dock'],name)
  except (ValueError,Standard_Failure) as e:result['failures'].append({'route':name,'reason':str(e)});print('LOOM FAILURE',name,str(e),flush=True);continue
  record.update(n);export(name,shape,record,[n['from_dock']['owner'],n['to_dock']['owner']])
  if not args.received_cutters:
   result['pass']=False;(HERE/'controls-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
 complete=sum('from_dock' in r for r in result['control_routes'].values())
 result['full_fluid_air_checks']=[]
 for name,fields in result['parts'].items():
  shape=guide.wires.get(name,fixed_models.get(name))
  if shape is None:continue
  for part,fluid in guide.physical_fluids.items():
   if not broad(bounds(shape),bounds(fluid),1.):continue
   gap=shape.distance(fluid);row={'control':name,'fluid':part,'air_mm':gap,'pass':gap>=1.-1e-6}
   result['full_fluid_air_checks'].append(row)
   if not row['pass']:result['failures'].append({'route':name,'reason':'Less than required1mm unrelated fluid air','hit':row})
 result['coverage']={'canonical_conductor_jobs':len(data['jobs']),'required_grouped_routes':len(network),'selected_routes':len(selected),'completed_routes':complete,'expected_static_parts':len(sections)+len(fanouts),'completed_static_parts':sum('from_dock' not in r for r in result['control_routes'].values()),'partial_filter':args.only}
 result['hardware_pass']=not args.only and static_checks['pass'] and complete==len(network) and all(r.get('hardware_pass') for r in result['parts'].values()) and result['coverage']['completed_static_parts']==len(sections)+len(fanouts) and all(r['pass'] for r in result['full_fluid_air_checks'])
 result['bench_cut_review']=[]
 for job in data['jobs']:
  cut=job.get('baseline_bench_cut_mm')
  if cut is None:continue
  route_name=result['canonical_job_coverage'][job['name']]['grouped_route'];record=result['control_routes'].get(route_name,{})
  if 'length_mm' not in record:continue
  allowance=11.65 if job['from'].startswith('J') else 0
  result['bench_cut_review'].append({'canonical_job':job['name'],'existing_bench_cut_mm':cut,
   'shared_route_centreline_mm':record['length_mm'],'board_contact_allowance_mm':allowance,
   'remaining_before_fanouts_static_continuations_and_termination_mm':cut-record['length_mm']-allowance,
   'scope':'Comparison to the inherited bench cut only. Shared outer centreline excludes constituent packing differences, end fanouts, fixed service continuation, hidden termination insertion and manufacturing service allowance; this value is not a completed-harness cut length.'})
 result['source_drift']=[name for name,r in guide.native_inputs.items() if not(ROOT/r['brep']).exists() or hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()!=r['sha256']]
 result['source_drift']+=[name for name,h in source_inputs.items() if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h]
 result['manifest_drift']=[name for name,h in manifest_content.items() if manifest_content_sha256(ROOT/name)!=h]
 if args.received_cutters:
  unchanged_checks=[]
  for name,assets in frozen_assets.items():
   for kind,r in [('body',accepted_packet['parts'][name]),('cutter',accepted_packet['clearance_cutters'][name])]:
    unchanged=(ROOT/r['brep']).read_bytes()==assets[kind]
    unchanged_checks.append({'part':name,'kind':kind,'sha256':r['sha256'],'native_bytes_unchanged':unchanged,'pass':unchanged})
    if not unchanged:result['source_drift'].append(name+'-'+kind)
  result['checks']+=unchanged_checks
  if len(result['parts'])!=75 or len(result['clearance_cutters'])!=75:result['failures'].append({'reason':'Strict received validation did not preserve the complete75 body/cutter pairs'})
 result['pass']=not args.hardware_only and not args.only and not result['failures'] and complete==len(network) and not result['source_drift'] and not result['manifest_drift']
 result['source_sha256'].update(source_inputs);(HERE/'controls-candidate.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'parts':len(result['parts']),'routes':len(selected),'pass':result['pass'],'failures':result['failures']},indent=2),flush=True)
if __name__=='__main__':main()
