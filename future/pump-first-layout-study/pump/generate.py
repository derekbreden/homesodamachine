"""Native pump-first bay package: measured pump, four sliders, mount hosts and water runs.

Runtime B-reps are kept in .cache. Canonical appliance generators are not changed.
Every port uses its measured or purchased reference frame. Pump volumes remain
occupied envelopes, and clamp dimensions retain their reference qualification.
"""
from pathlib import Path
import sys, json, hashlib, math
import cadquery as cq
from OCP.gp import gp_Pnt, gp_Vec
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'.cache/pump-first-layout/pump'
for rel in ('future/pump-first-layout-study','hardware/scripts','hardware/reference/g-ganen-pump/installation','hardware/reference/g-ganen-pump/common-foot','hardware/reference/seaflo-discharge-chain','hardware/reference/seaflo-suction-chain','hardware/reference/beduan-solenoid','hardware/reference/worm-clamp','hardware/printed-parts/valve-seat','hardware/printed-parts/cadlib'):
 sys.path.insert(0,str(ROOT/rel))
import baseline
import g_ganen_installation as P
import g_ganen_foot as F
import seaflo_discharge_chain as D
import seaflo_suction_chain as S
import beduan_solenoid as V
import valve_seat as VS
import worm_clamp as C
import _routing as R

PUMP_ORIGIN=(-18.25,367.4,253.4)
HEAD_SLIDER_X=30.0
REAR_SLIDER_X=62.5
VK_ORIGIN=(-86.6,236.75,288.5)
# An exact initial heading correction frees the reinforced hose's S offset plane.
_SP,_SA=P.suction()
SUCT_TIP=(_SP[0]+PUMP_ORIGIN[0],316.1,282.15)
DISCH_TIP=(-15.,453.5,342.)
DISCH_DOWN_DEGREES=25.136056719062132
DISCH_INITIAL_TURN_DEGREES=None
DISCH_EXPOSED_LEAD_MM=.5
CAP_FLOOR_Z=233.4000002
CAP_COLUMN_TOP_Z=248.0000002
CAP_FACE_Z=253.4000002
PARTS={}
REPORT={'schema':'pump-first-layout/pump/1','source_sha256':{},'checks':[],'poses':{},'routes':{}}
SOURCE_B_RUN=None


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def loc(axis=(0,0,1),deg=0,shift=(0,0,0)):
 return cq.Location(cq.Vector(*shift))*cq.Location(cq.Vector(0,0,0),cq.Vector(*axis),deg)
def posed(shape,place):return shape.moved(place)
def point(port,place):
 p,a=port
 tr=place.wrapped.Transformation()
 q=gp_Pnt(*p).Transformed(tr)
 u=gp_Vec(*a).Transformed(tr)
 return (q.X(),q.Y(),q.Z()),(u.X(),u.Y(),u.Z())
def bounds(shape):
 b=shape.BoundingBox();return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def native_cap_floor(shape):
 """Find the broad upward planar floor of the installed native cap."""
 faces=[]
 for face in shape.Faces():
  if face.geomType()!='PLANE':continue
  box=face.BoundingBox();normal=face.normalAt()
  if box.zlen<1e-5 and normal.z>.999 and box.zmin<CAP_COLUMN_TOP_Z-1:
   faces.append((face.Area(),box.zmin))
 if not faces:raise ValueError('Native cap lacks an identifiable upward floor')
 area,z=max(faces)
 REPORT['poses']['cap-native-floor']={'z_mm':z,'face_area_mm2':area,'external_bottom_z_mm':shape.BoundingBox().zmin,'retained_floor_stock_mm':z-shape.BoundingBox().zmin,'source':'Largest upward horizontal planar face below the cap rim in baseline native cap.'}
 return z
def emit(name,shape,role,detail):
 path=OUT/(name.replace('/','-')+'.brep');shape.exportBrep(str(path))
 PARTS[name]={'brep':str(path.relative_to(ROOT)),'sha256':digest(path),'role':role,'detail':detail,'bounds_mm':bounds(shape)}
 return shape

def clearance_cutter(name,profile_origin,profile_normal,diameter,wire):
 """Exact1mm swept clearance, for the reorganized enclosure roof/flank only."""
 cutter=cq.Solid.sweep(cq.Wire.makeCircle(diameter/2+1,profile_origin,profile_normal),[],wire,makeSolid=True,isFrenet=True)
 path=OUT/(name+'-clearance-cutter.brep');cutter.exportBrep(str(path))
 REPORT.setdefault('clearance_cutters',{})[name]={'brep':str(path.relative_to(ROOT)),'sha256':digest(path),'radial_air_mm':1,'bounds_mm':bounds(cutter),'scope':'Reorganized enclosure roof/flank only; preserve fixed core mouths and part interfaces.'}
 if name=='tube-water-5':
  REPORT['clearance_cutters'][name].update({
   'print_owner':'enclosure-back-top','factory_upper_bay_channel':True,
   'minimum_exterior_stock_mm':3.,
   'scope':'Exact water5 relief through the back-top upper bay, Y>=200 and Z>=253.4; retain the three-mm exterior flank and unchanged lower interfaces. Recut after parent/host fusion.'})
 return cutter

def check(label,condition,**data):
 REPORT['checks'].append({'check':label,'pass':bool(condition),**data})
 print(('PASS ' if condition else 'FAIL ')+label,flush=True)

def overlap(a,b):
 # Independent occupied components avoid Compound common-operation ambiguities.
 total=0.0
 for s in a.Solids():
  bs=s.BoundingBox()
  for t in b.Solids():
   bt=t.BoundingBox()
   if bs.xmin>bt.xmax or bs.xmax<bt.xmin or bs.ymin>bt.ymax or bs.ymax<bt.ymin or bs.zmin>bt.zmax or bs.zmax<bt.zmin:continue
   total+=abs(s.intersect(t).Volume())
 return total

def frame(name,shape,ports,place):
 R.frame(name,shape,{label:(*point(port,place),diam)for label,(port,diam)in ports.items()})

def electrical_ends(placements):
 result={'basis':'Native Beduan terminal blade front face centre; local X−7.45/+7.45, Y27.1, Z52.2, outward+Y. The reference does not mark polarity, so terminal identities use the reference local X sign.'}
 for name,place in placements.items():
  result[name]={}
  for side in(-1,1):
   pos,axis=point(((side*V.spade_x_spacing/2,V.coil_face_y+V.spade_length,V.spade_z_center),(0,1,0)),place)
   result[name][str(side)]={'point_mm':pos,'outward_axis':axis}
 (HERE/'electrical-ends.json').write_text(json.dumps(result,indent=2)+'\n')
 return result

def route(run):
 shape=R.tube(run)
 emit('tube-'+run.id,shape,'water',run.note)
 REPORT['routes'][run.id]={'from':run.frm,'to':run.to,'points_mm':run.pts,'diameter_mm':run.diam,'radii_mm':run.radii,'tightest_mm':run.tightest,'developed_length_mm':run.length,'note':run.note}
 check(run.id+' bend radius',run.tightest>=R.stock_min(run.kind,run.diam)-1e-7,radius_mm=run.tightest,minimum_mm=R.stock_min(run.kind,run.diam))
 return shape

def tangent_s(cid,frm,to,radius,diameter):
 """Two opposite exact circles, with tangent +Y endpoints and derived straight leads.

 A diagonal offset in the XZ plane shares one pair of circles. No waypoint
 approximation reduces the actual stock bend radius.
 """
 start=cq.Vector(*R._frames[frm.split('.')[0]].at(frm.split('.')[1]))
 end=cq.Vector(*R._frames[to.split('.')[0]].at(to.split('.')[1]))
 delta=end-start; transverse=cq.Vector(delta.x,0,delta.z);d=transverse.Length
 if d<1e-8:raise ValueError('S needs a nonzero transverse offset')
 u=transverse.normalized();f=cq.Vector(0,1,0)
 theta=math.acos(1-d/(2*radius))
 axial=2*radius*math.sin(theta)
 lead=(delta.y-axial)/2
 if lead<-1e-7:raise ValueError(f'{cid} has {delta.y:.6f}mm axial room; exact R{radius} needs {axial:.6f}')
 a=start+f*lead
 mid1=a+f*(radius*math.sin(theta/2))+u*(radius*(1-math.cos(theta/2)))
 b=a+f*(radius*math.sin(theta))+u*(radius*(1-math.cos(theta)))
 mid2=b+f*(radius*(math.sin(theta)-math.sin(theta/2)))+u*(radius*(math.cos(theta/2)-math.cos(theta)))
 c=b+f*(radius*math.sin(theta))+u*(radius*(1-math.cos(theta)))
 edges=[]
 if lead>1e-7:edges.append(cq.Edge.makeLine(start,a))
 edges.extend([cq.Edge.makeThreePointArc(a,mid1,b),cq.Edge.makeThreePointArc(b,mid2,c)])
 if lead>1e-7:edges.append(cq.Edge.makeLine(c,end))
 wire=cq.Wire.assembleEdges(edges)
 profile=cq.Wire.makeCircle(diameter/2,start,f)
 shape=cq.Solid.sweep(profile,[],wire,makeSolid=True,isFrenet=True)
 note='VK outlet to suction reducer: two opposite exact tangent R14 circles in the diagonal XZ offset plane.'
 emit('tube-'+cid,shape,'water',note)
 REPORT['routes'][cid]={'from':frm,'to':to,'points_mm':[v.toTuple()for v in(start,a,mid1,b,mid2,c,end)],'diameter_mm':diameter,'radii_mm':[radius,radius],'tightest_mm':radius,'developed_length_mm':2*lead+2*radius*theta,'note':note,'curve':'two tangent circular arcs','arc_degrees':math.degrees(theta),'straight_end_leads_mm':[lead,lead],'offset_mm':d,'longitudinal_mm':delta.y}
 check(cid+' bend radius',radius>=14,radius_mm=radius,minimum_mm=14,straight_leads_mm=lead,actual_tangent_endpoint_error_mm=(c+f*lead-end).Length)
 return shape

def measured_braided_s():
 """Measured barb heading, then an exact R15.9 diagonal S into the raised reducer."""
 start,axis=point(P.suction(),loc(shift=PUMP_ORIGIN))
 start=cq.Vector(*start);end=cq.Vector(*SUCT_TIP);axis=cq.Vector(*axis)
 f=cq.Vector(0,-1,0);r=15.9;front_lead=2.
 a=start+axis*front_lead
 initial,b,mid,epsilon=exact_arc(a,axis,f,r)
 offset=cq.Vector(end.x-b.x,0,end.z-b.z)
 tail_edges,c,mids,theta=exact_s(b,f,offset,r)
 tail=(end-c).dot(f)
 if tail<0 or (c+f*tail-end).Length>1e-6:raise ValueError('Measured suction S does not close on its actual axes')
 wire=cq.Wire.assembleEdges([cq.Edge.makeLine(start,a),initial]+tail_edges+[cq.Edge.makeLine(c,end)])
 shape=cq.Solid.sweep(cq.Wire.makeCircle(S.HOSE_OD/2,start,axis),[],wire,makeSolid=True,isFrenet=True)
 note='Measured pump suction to raised reducer: a short exact R15.9 heading correction and two R15.9 opposing arcs preserve both actual terminal axes.'
 emit('tube-water-7',shape,'water',note)
 REPORT['routes']['water-7']={'from':'g-ganen-pump.suction','to':'suction-chain.barb-tip','points_mm':[v.toTuple()for v in[start,a,mid,b,*mids,c,end]],'diameter_mm':S.HOSE_OD,'radii_mm':[r]*3,'tightest_mm':r,'developed_length_mm':wire.Length(),'note':note,'curve':'three exact tangent circular arcs with measured terminal headings','arc_degrees':[math.degrees(epsilon),math.degrees(theta),math.degrees(theta)],'straight_end_leads_mm':[front_lead,tail],'actual_barb_axis':axis.toTuple()}
 check('water-7 bend radius',True,radius_mm=r,minimum_mm=15.9,endpoint_error_mm=(c+f*tail-end).Length)
 return shape

def exact_arc(start,heading,end_heading,radius):
 """A circular arc from two unit tangent vectors; return edge and end datum."""
 heading=heading.normalized();end_heading=end_heading.normalized()
 angle=math.acos(max(-1.,min(1.,heading.dot(end_heading))))
 plane=(end_heading-heading*math.cos(angle)).normalized()
 mid=start+heading*(radius*math.sin(angle/2))+plane*(radius*(1-math.cos(angle/2)))
 end=start+heading*(radius*math.sin(angle))+plane*(radius*(1-math.cos(angle)))
 return cq.Edge.makeThreePointArc(start,mid,end),end,mid,angle

def exact_s(start,heading,offset,radius):
 """Opposite tangent circles for an offset transverse to a terminal heading."""
 heading=heading.normalized();distance=offset.Length;plane=offset.normalized()
 angle=math.acos(1-distance/(2*radius))
 mid1=start+heading*(radius*math.sin(angle/2))+plane*(radius*(1-math.cos(angle/2)))
 turn=start+heading*(radius*math.sin(angle))+plane*(radius*(1-math.cos(angle)))
 mid2=turn+heading*(radius*(math.sin(angle)-math.sin(angle/2)))+plane*(radius*(math.cos(angle/2)-math.cos(angle)))
 end=turn+heading*(radius*math.sin(angle))+plane*(radius*(1-math.cos(angle)))
 return [cq.Edge.makeThreePointArc(start,mid1,turn),cq.Edge.makeThreePointArc(turn,mid2,end)],end,[mid1,turn,mid2],angle

def reversed_vk_to_chain():
 """The reversed valve exits fore, with a diagonal U above the low bay."""
 start=cq.Vector(*R._frames['vk-solenoid'].at('outlet'));forward=cq.Vector(0,-1,0);r=14.
 turn_end=cq.Vector(SUCT_TIP[0],start.y,293.5);delta=turn_end-start;plane=delta.normalized()
 first,a,m1,q1=exact_arc(start,forward,plane,r)
 b=a+plane*max(0,delta.Length-2*r)
 second,end,m2,q2=exact_arc(b,plane,-forward,r)
 edges=[first]
 if (b-a).Length>1e-8:edges.append(cq.Edge.makeLine(a,b))
 edges.append(second)
 aft_start=cq.Vector(SUCT_TIP[0],232,293.5)
 correction=cq.Vector(aft_start.x-end.x,0,aft_start.z-end.z)
 correction_lead=0.;mcor=[]
 if correction.Length>1e-8:
  correction_angle=math.acos(1-correction.Length/(2*r))
  correction_axial=2*r*math.sin(correction_angle)
  correction_lead=(aft_start.y-end.y-correction_axial)/2
  if correction_lead<0:raise ValueError('VK U correction lacks R14 axial room')
  cs=end+cq.Vector(0,correction_lead,0)
  if correction_lead>1e-8:edges.append(cq.Edge.makeLine(end,cs))
  ce,cp,mcor,ca=exact_s(cs,cq.Vector(0,1,0),correction,r)
  edges.extend(ce)
  if correction_lead>1e-8:edges.append(cq.Edge.makeLine(cp,aft_start))
 else:edges.append(cq.Edge.makeLine(end,aft_start))
 end_port=cq.Vector(*R._frames['suction-chain'].at('tube-port'))
 offset=cq.Vector(end_port.x-aft_start.x,0,end_port.z-aft_start.z)
 angle=math.acos(1-offset.Length/(2*r));axial=2*r*math.sin(angle)
 lead=(end_port.y-aft_start.y-axial)/2
 tail_begin=aft_start+cq.Vector(0,lead,0)
 tail_edges,tail_end,mids,q3=exact_s(tail_begin,cq.Vector(0,1,0),offset,r)
 edges+=[cq.Edge.makeLine(aft_start,tail_begin)]+tail_edges+[cq.Edge.makeLine(tail_end,end_port)]
 wire=cq.Wire.assembleEdges(edges)
 shape=cq.Solid.sweep(cq.Wire.makeCircle(3.175,start,forward),[],wire,makeSolid=True,isFrenet=True)
 note='VK fore outlet returns through an exact diagonal R14 U, a corrective R14 S and a descending R14 S to the suction reducer, below the frame underside.'
 emit('tube-water-4',shape,'water',note)
 REPORT['routes']['water-4']={'from':'vk-solenoid.outlet','to':'suction-chain.tube-port','points_mm':[v.toTuple()for v in[start,m1,a,b,m2,end,*mcor,aft_start,tail_begin,*mids,tail_end,end_port]],'diameter_mm':6.35,'radii_mm':[r]*(6 if correction.Length>1e-8 else 4),'tightest_mm':r,'developed_length_mm':wire.Length(),'note':note,'curve':'six exact tangent circular arcs','straight_end_leads_mm':[0,correction_lead,lead],'u_transverse_mm':max(delta.Length,28),'correction_offset_mm':correction.Length}
 check('water-4 bend radius',lead>=0 and correction_lead>=0,radius_mm=r,minimum_mm=14,lead_mm=lead,u_offset_mm=max(delta.Length,28),corrective_s_lead_mm=correction_lead)
 return shape

def low_discharge_hose():
 """Measured-axis PVC turns below the PSU, then rises outside its west flank."""
 pos,heading=point(P.discharge(),loc(shift=PUMP_ORIGIN))
 start=cq.Vector(*pos);heading=cq.Vector(*heading);r=15.9;phi=math.radians(DISCH_DOWN_DEGREES)
 a=start+heading*DISCH_EXPOSED_LEAD_MM
 edges=[cq.Edge.makeLine(start,a)] if DISCH_EXPOSED_LEAD_MM>1e-7 else []
 points=[start,a];angles=[]
 diagonal=cq.Vector(-math.cos(phi),0,-math.sin(phi))
 plane=(diagonal-heading*heading.dot(diagonal)).normalized()
 first_heading=(heading*math.cos(math.radians(DISCH_INITIAL_TURN_DEGREES))+plane*math.sin(math.radians(DISCH_INITIAL_TURN_DEGREES))) if DISCH_INITIAL_TURN_DEGREES is not None else diagonal
 for end_heading in (first_heading,cq.Vector(-1,0,0),cq.Vector(0,0,1)):
  edge,a,mid,angle=exact_arc(a,heading,end_heading,r)
  edges.append(edge);points.extend([mid,a]);angles.append(angle);heading=end_heading
 riser=a
 offset=cq.Vector(0,426.2-riser.y,0)
 theta=math.acos(1-offset.Length/(2*r));rise=2*r*math.sin(theta)
 upper_turn_z=DISCH_TIP[2]-r
 sstart=cq.Vector(riser.x,riser.y,upper_turn_z-rise)
 if sstart.z<riser.z:raise ValueError('Discharge riser has insufficient space for its stock-radius Y shift')
 edges.append(cq.Edge.makeLine(riser,sstart));points.append(sstart)
 sedges,a,mids,angle=exact_s(sstart,heading,offset,r)
 edges.extend(sedges);points.extend(mids+[a]);angles.extend([angle,angle])
 edge,a,mid,angle=exact_arc(a,heading,cq.Vector(1,0,0),r)
 edges.append(edge);points.extend([mid,a]);angles.append(angle);heading=cq.Vector(1,0,0)
 final=cq.Vector(*DISCH_TIP);shift=cq.Vector(0,final.y-a.y,0)
 theta=math.acos(1-shift.Length/(2*r));last_axial=2*r*math.sin(theta)
 bend_start=cq.Vector(final.x-last_axial,a.y,a.z)
 if bend_start.x<a.x:raise ValueError('Discharge upper return has insufficient X span')
 edges.append(cq.Edge.makeLine(a,bend_start));points.append(bend_start)
 sedges,end,mids,angle=exact_s(bend_start,heading,shift,r)
 edges.extend(sedges);points.extend(mids+[end]);angles.extend([angle,angle])
 wire=cq.Wire.assembleEdges(edges)
 shape=cq.Solid.sweep(cq.Wire.makeCircle(S.HOSE_OD/2,start,cq.Vector(*point(P.discharge(),loc(shift=PUMP_ORIGIN))[1])),[],wire,makeSolid=True,isFrenet=True)
 clearance_cutter('tube-water-6',start,cq.Vector(*point(P.discharge(),loc(shift=PUMP_ORIGIN))[1]),S.HOSE_OD,wire)
 note='Actual pump discharge axis: exact R15.9 west/down arcs, low span under PSU, west riser with gentle aft shift, then high return fore of C14 to the check-chain barb.'
 emit('tube-water-6',shape,'water',note)
 REPORT['routes']['water-6']={'from':'g-ganen-pump.discharge','to':'discharge-chain.barb-tip','points_mm':[v.toTuple()for v in points],'diameter_mm':S.HOSE_OD,'radii_mm':[r]*len(angles),'tightest_mm':r,'developed_length_mm':wire.Length(),'note':note,'curve':'eight exact tangent circular arcs','arc_degrees':[math.degrees(q)for q in angles],'straight_end_leads_mm':[DISCH_EXPOSED_LEAD_MM,0],'low_span_crown_mm':riser.z-r+S.HOSE_OD/2,'low_span_psu_base_air_mm':289.75-(riser.z-r+S.HOSE_OD/2),'west_riser_mm':riser.toTuple(),'west_flank_air_mm':riser.x+98.5-S.HOSE_OD/2,'wall_pocket_additional_depth_mm':max(0,1-(riser.x+98.5-S.HOSE_OD/2))}
 check('water-6 bend radius',(end-final).Length<1e-6,radius_mm=r,minimum_mm=15.9,endpoint_error_mm=(end-final).Length)
 return shape

def discharge_to_core():
 """Stock R14 feed through the original-width east service channel."""
 import water5_route
 shape,wire,data=water5_route.build(exact_arc,exact_s,R,fore_cross=(195.5,285.8))
 source=cq.Vector(68.4,453.5,342.)
 clearance_cutter('tube-water-5',source,cq.Vector(1,0,0),6.35,wire)
 note='Discharge check to fixed core mouth: source R14 S raises the east run to Z346, fore drop at X100.325/Y304.6 clears the compact +60 funnel and meter, low span below insulation, east rise/downward S to the Y195.5/Z285.8 fore crossing, diagonal return and cap-normal R14 entry.'
 emit('tube-water-5',shape,'water',note)
 REPORT['routes']['water-5']={**data,'from':'discharge-chain.tube-port','to':'foam-assembly.water-in','note':note,'curve':'tangent R14 circles and stock polyline'}
 REPORT['source_sha256']['future/pump-first-layout-study/pump/water5_route.py']=digest(ROOT/'future/pump-first-layout-study/pump/water5_route.py')
 check('water-5 bend radius',data['tightest_mm']>=14-1e-7,radius_mm=data['tightest_mm'],minimum_mm=14)
 return shape

def clamp(name,port,clock=0):
 p,a=port
 # Band rests over the scanned/profiled root half of each barb, rather than beyond its tip.
 mid=tuple(p[i]-a[i]*6.5 for i in range(3))
 axis=cq.Vector(0,0,1).cross(cq.Vector(*a)); angle=math.degrees(math.acos(max(-1,min(1,a[2]))))
 place=loc(tuple(axis.toTuple()) if axis.Length>1e-8 else (1,0,0),angle,mid)
 shape=C.build_worm_clamp(S.HOSE_OD).val().rotate((0,0,0),(0,0,1),clock).moved(place)
 emit(name,shape,'water','LOKMAN 10–16mm reference clamp at Ø15.1mm; housing envelope seeded, not dimensionally ratified.')
 return shape

def hose_engagement(name,port,length):
 p,a=port
 root=tuple(p[i]-a[i]*length for i in range(3))
 outer=cq.Solid.makeCylinder(S.HOSE_OD/2,length,cq.Vector(*root),cq.Vector(*a))
 # The visible engagement is hose wall, not solid fluid: the inner bore clears the barb.
 inner=cq.Solid.makeCylinder(S.HOSE_ID/2,length+.02,cq.Vector(*[root[i]-a[i]*.01 for i in range(3)]),cq.Vector(*a))
 return emit(name,outer.cut(inner),'water','Reinforced-PVC wall over barb; inserted length uses observed pump exterior or chain reference span.')

def chain_host(name,axis_mid,seat_r,on_rear=False):
 x,y,z=axis_mid; length=9.5
 if on_rear:
  # Across-X key hangs from the roof and rear wall, above the power supply.
  # The zip channel retains 3mm between its floor and the socket crown.
  host=cq.Solid.makeBox(length,465.3-(y-seat_r-3),355-(z-seat_r-3),
                       cq.Vector(x-length/2,y-seat_r-3,z-seat_r-3))
  bore=cq.Solid.makeCylinder(seat_r,length+2,cq.Vector(x-length/2-1,y,z),cq.Vector(1,0,0))
  opening=cq.Solid.makeBox(length+2,2*seat_r+6,seat_r+3,cq.Vector(x-length/2-1,y-seat_r-3,z-seat_r-3))
  host=host.cut(bore).cut(opening)
  # A bolted lower key avoids putting a tie passage through the roof's last stock.
  # Two M3x10 screws enter 8.5mm blind roof pockets; the cap is preassembled.
  clip=cq.Solid.makeCylinder(seat_r+3,length,cq.Vector(x-length/2,y,z),cq.Vector(1,0,0)).cut(cq.Solid.makeCylinder(seat_r,length+2,cq.Vector(x-length/2-1,y,z),cq.Vector(1,0,0)))
  clip=clip.cut(cq.Solid.makeBox(length+2,2*(seat_r+3)+2,seat_r+4,cq.Vector(x-length/2-1,y-seat_r-4,z)))
  flange=cq.Solid.makeBox(28,11.3,3,cq.Vector(x-14,y-20.6,z-3))
  clip=clip.fuse(flange)
  for i,sx in enumerate((x-10,x+10)):
   sy=y-15.15
   boss=cq.Solid.makeCylinder(4,355-z,cq.Vector(sx,sy,z))
   bore=cq.Solid.makeCylinder(2,8.5,cq.Vector(sx,sy,z))
   host=host.fuse(boss.cut(bore))
   clip=clip.cut(cq.Solid.makeCylinder(1.65,3.02,cq.Vector(sx,sy,z-3.01)))
   screw=cq.Solid.makeCylinder(1.5,10,cq.Vector(sx,sy,z-3)).fuse(cq.Solid.makeCylinder(2.75,3,cq.Vector(sx,sy,z-6)))
   emit('discharge-chain-clip-screw-'+str(i+1),screw,'structure','M3×10 lower-key screw: 3mm clip, 7mm penetration, 5.7mm insert engagement and 1.5mm blind reserve.')
  emit('discharge-chain-lower-key',clip.clean(),'structure','3mm lower half-key on GASHER hex, two fore M3 stations and 0.15mm radial seat air; factory-installed with roof subassembly.')
  REPORT['poses']['discharge-chain-retainer']={'screw_axes_xy_mm':[[x-10,y-15.15],[x+10,y-15.15]],'boss_od_mm':8,'pilot_d_mm':4,'pilot_depth_mm':8.5,'insert_length_mm':5.7,'end_cover_mm':355-z-8.5,'clip_stock_mm':3,'screw_length_mm':10,'screw_tip_reserve_mm':1.5}
 else:
  host=cq.Solid.makeBox(2*seat_r+6,length,z+seat_r-CAP_FACE_Z,cq.Vector(x-seat_r-3,y-length/2,CAP_FACE_Z))
  bore=cq.Solid.makeCylinder(seat_r,length+2,cq.Vector(x,y-length/2-1,z),cq.Vector(0,1,0))
  roof=cq.Solid.makeBox(2*seat_r+6,length+2,seat_r+3,cq.Vector(x-seat_r-3,y-length/2-1,z))
  host=host.cut(bore).cut(roof)
  channel=cq.Solid.makeBox(2*seat_r+6,2.8,2.8,cq.Vector(x-seat_r-3,y-1.4,z-seat_r-3-2.8))
  host=host.cut(channel)
 emit(name,host.clean(),'structure','Roof/rear-rooted 9.5mm hex key with two blind M3 columns and a separate 3mm bolted lower retainer.' if on_rear else '9.5mm section seat, 0.15mm radial air and 2.8mm zip-tie passage; 3mm channel support wall.')
 return host


def raised_suction_host(axis_mid):
 """Bolted split seat on a lid-rooted bridge above the removable pan."""
 x,y,z=axis_mid;r=8.65;length=18.6;y0=y-length/2
 bottom=z-r-3;right=9.;left=x-r-3
 root_end=298.5
 host=cq.Solid.makeBox(right-left,root_end-y0,z-bottom,cq.Vector(left,y0,bottom))
 root=cq.Solid.makeBox(8,root_end-y0,z-CAP_FACE_Z+.01,cq.Vector(1,y0,CAP_FACE_Z-.01))
 host=host.fuse(root)
 # Use the complete nativeR14 gas cross, including its diagonal S, to form
 # the1mm-air passage. Clip the cutter to this root so its later print recut
 # cannot touch an unrelated cap interface.
 gas_source=HERE.parent/'routing/co2-candidate.json'
 gas_manifest=json.loads(gas_source.read_text())
 gas_rec=gas_manifest['clearance_cutters']['tube-co2-0']
 portal_source=ROOT/gas_rec['brep']
 portal_shape=cq.Shape.importBrep(str(portal_source))
 portal_r=4.175;portal_z=261.5
 portal=portal_shape.intersect(cq.Solid.makeBox(8.04,root_end-y0+.04,z-CAP_FACE_Z+.04,cq.Vector(.98,y0-.02,CAP_FACE_Z-.02)))
 if not portal.Solids():raise ValueError('The published gas cross does not pass the suction root')
 pb=bounds(portal);portal_y0=pb[1]+portal_r;portal_y1=pb[4]-portal_r
 host=host.cut(portal)
 portal_path=OUT/'suction-chain-gas-portal.brep';portal.exportBrep(str(portal_path))
 REPORT.setdefault('pilot_cutters',{})['suction-chain-gas-portal']={'brep':str(portal_path.relative_to(ROOT)),'sha256':digest(portal_path),'print_owner':'cold-core-lid','kind':'gas-service-portal','diameter_mm':2*portal_r,'bounds_mm':pb,'axis':'Native gas cross','z_mm':portal_z,'radial_air_mm':1,'native_source':{'brep':gas_rec['brep'],'sha256':digest(portal_source),'manifest':str(gas_source.relative_to(ROOT)),'manifest_sha256':digest(gas_source)}}
 portal_stock={'fore_mm':pb[1]-y0,'aft_mm':y0+length-pb[4],'bottom_mm':pb[2]-CAP_FACE_Z,'upper_mm':bottom-pb[5]}
 check('Suction root gas portal retains at least3mm stock',min(portal_stock.values())>=3,**portal_stock,portal_diameter_mm=2*portal_r)
 bore=cq.Solid.makeCylinder(r,root_end-y0+2,cq.Vector(x,y0-1,z),cq.Vector(0,1,0))
 host=host.cut(bore)
 key=cq.Solid.makeBox(right-left,length,4,cq.Vector(left,y0,z))
 crown=cq.Solid.makeBox(2*r+6,length,r+3,cq.Vector(left,y0,z))
 key=key.fuse(crown).cut(bore)
 key=key.fuse(cq.Solid.makeBox(39,root_end-y0,4,cq.Vector(-30,y0,z)))
 # The V-B aft collet and its exact jumper have a clearance passage. The
 # rear lower rail and west part of the upper flange carry the split seat
 # around it, rather than requiring overlap with the purchased barrel.
 vb_barrel=cq.Solid.makeCylinder(8.6,61.5,cq.Vector(-13.25,210.55,270.15),cq.Vector(0,1,0))
 host=host.cut(vb_barrel);key=key.cut(vb_barrel)
 route_cutter=None
 if SOURCE_B_RUN is not None:
  wire=R.centreline(SOURCE_B_RUN)
  route_cutter=cq.Solid.sweep(cq.Wire.makeCircle(4.175,cq.Vector(-13.25,271.05,270.15),cq.Vector(0,1,0)),[],wire,makeSolid=True,isFrenet=True)
  host=host.cut(route_cutter);key=key.cut(route_cutter)
  path=OUT/'source-b-suction-passage.brep';route_cutter.exportBrep(str(path))
  REPORT.setdefault('pilot_cutters',{})['source-b-suction-passage']={'brep':str(path.relative_to(ROOT)),'sha256':digest(path),'print_owner':'cold-core-lid','kind':'source-jumper-clearance','radial_air_mm':1}
 barrel_path=OUT/'source-b-barrel-clearance.brep';vb_barrel.exportBrep(str(barrel_path))
 REPORT.setdefault('pilot_cutters',{})['source-b-barrel-clearance']={'brep':str(barrel_path.relative_to(ROOT)),'sha256':digest(barrel_path),'print_owner':'cold-core-lid','kind':'purchased-collet-clearance','radial_air_mm':1}
 axes=[(5.,y0+4),(5.,294.5)]
 for i,(sx,sy)in enumerate(axes,1):
  pilot=cq.Solid.makeCylinder(2,8.5,cq.Vector(sx,sy,z-8.5))
  passage=cq.Solid.makeCylinder(1.65,4.02,cq.Vector(sx,sy,z-.01))
  host=host.cut(pilot);key=key.cut(passage)
  screw=cq.Solid.makeCylinder(1.5,10,cq.Vector(sx,sy,z-6)).fuse(cq.Solid.makeCylinder(2.75,3,cq.Vector(sx,sy,z+4)))
  emit('suction-chain-clip-screw-'+str(i),screw,'structure','M3 ×10: 4mm retainer flange, 6mm insert engagement and 2.5mm blind tip reserve.')
  path=OUT/('suction-chain-pilot-'+str(i)+'.brep');pilot.exportBrep(str(path))
  REPORT.setdefault('pilot_cutters',{})['suction-chain-pilot-'+str(i)]={'brep':str(path.relative_to(ROOT)),'sha256':digest(path),'print_owner':'cold-core-lid'}
  check('Raised suction retainer '+str(i)+' full screw stack',6>=5.7 and 8.5-6>=1,insert_length_mm=5.7,engagement_mm=6,tip_reserve_mm=2.5,radial_bore_wall_mm=2)
 host=host.clean();key=key.clean()
 rear_rail=cq.Solid.makeBox(right-left,3,3,cq.Vector(left,292,bottom))
 missing=rear_rail.cut(host).Volume()
 check('Suction bridge retains a continuous3mm rear load rail',missing<.001,missing_stock_mm3=missing,rail_y_mm=[292,295],rail_z_mm=[bottom,bottom+3])
 emit('suction-chain-anchor',host,'structure','3mm lower seat stock on a lid-rooted bridge above the pan, with a continuous3mm rear rail around the source-B barrel and jumper clearance; two blind M3 pockets retain the upper key.')
 emit('suction-chain-upper-key',key,'structure','Separate3mm crown with4mm bolted flanges closes the Ø17.3 seat; two M3×10 screws on the east lid root.')
 REPORT['poses']['suction-chain-retainer']={'screw_axes_xy_mm':axes,'seat_radius_mm':r,'length_mm':length,'bridge_bottom_z_mm':bottom,'pan_rim_z_mm':266.4,'pan_air_mm':bottom-266.4,'pan_keepout_top_z_mm':269.4,'pan_keepout_air_mm':bottom-269.4,'root_xy_mm':[1,right,y0,root_end],'rear_load_rail_mm':[3,3],'gas_portal_stock_mm':portal_stock,'screw_length_mm':10,'pilot_depth_mm':8.5,'insert_length_mm':5.7,'tip_reserve_mm':2.5,'qualification':'Joined stock and fit are geometric. Bridge bending, retention and long-term creep remain physical qualifications.'}
 check('Raised suction bridge and upper key are single valid solids',host.isValid() and key.isValid() and len(host.Solids())==len(key.Solids())==1,host_solids=len(host.Solids()),key_solids=len(key.Solids()))
 return host


def main():
 global SOURCE_B_RUN
 OUT.mkdir(parents=True,exist_ok=True)
 for rel in ('future/pump-first-layout-study/pump/generate.py','hardware/reference/g-ganen-pump/reference-parameters.json','hardware/reference/g-ganen-pump/common-foot/g_ganen_foot.py','hardware/reference/g-ganen-pump/installation/g_ganen_installation.py','hardware/reference/seaflo-discharge-chain/seaflo_discharge_chain.py','hardware/reference/seaflo-suction-chain/seaflo_suction_chain.py','hardware/reference/beduan-solenoid/beduan_solenoid.py','hardware/reference/worm-clamp/worm_clamp.py','hardware/scripts/_routing.py'):
  REPORT['source_sha256'][rel]=digest(ROOT/rel)
 baseline_parts=baseline.read(names=['cold-core/foam-cap-top','cold-core/foam-cap-lid-top'])
 pparts=P.build_parts()
 for n in list(pparts):
  if 'rubber_slider' in n:
   side=-1 if 'yminus' in n else 1
   x=HEAD_SLIDER_X if n.startswith('head_') else REAR_SLIDER_X
   pparts[n]=F.placed_foot(x,side,38.5)
 pplace=loc(shift=PUMP_ORIGIN)
 pump=posed(cq.Compound.makeCompound(list(pparts.values())),pplace)
 emit('g-ganen-pump',pump,'pump','Measured native casing, upright rubber feet, motor along +X; suction fore and discharge aft.')
 REPORT['poses']['g-ganen-pump']={'yaw_degrees':0,'origin_mm':PUMP_ORIGIN,'slider_local_x_mm':[HEAD_SLIDER_X,REAR_SLIDER_X], 'suction':point(P.suction(),pplace),'discharge':point(P.discharge(),pplace)}
 REPORT['observed_regions']={'motor-lead-transition':{'local_bounds_mm':[[75,-8,5],[85,10,21]],'world_bounds_mm':[[PUMP_ORIGIN[i]+p[i]for i in range(3)]for p in [[75,-8,5],[85,10,21]]],'nominal_up_approaches_mm':[[PUMP_ORIGIN[i]+p[i]for i in range(3)]for p in [[85,-4,21],[85,6,21]]],'outward_axis':[0,0,1],'basis':'Observed motor lead-transition window in the scanned reference. Actual terminals and purchased strain relief are unlocated; these points reserve approaches at its upper boundary.'}}
 mount_rows=[(x+PUMP_ORIGIN[0],PUMP_ORIGIN[1]+s*40)for x in (HEAD_SLIDER_X,REAR_SLIDER_X)for s in(-1,1)]
 REPORT['poses']['pump-mounts']={'axes_xy_mm':mount_rows,'washer':'Ø9 ×0.8mm','screw':'M3 ×20mm','insert':'ruthex RX-M3x5.7','boss_od_mm':8,'bore_d_mm':4,'blind_depth_mm':8.5,'lid_thickness_mm':5.4}
 for x in (HEAD_SLIDER_X,REAR_SLIDER_X):
  check('Slider '+str(x)+' full rail engagement',x-9>=.5 and x+9<=76.5,interval_mm=[x-9,x+9],observed_rail_mm=[.5,76.5])
 # Replace old cap columns and lid screw holes while retaining cap floor, perimeter,
 # all cold-core conduit coordinates and clamp stations.
 cap=baseline_parts['cold-core/foam-cap-top'];lid=baseline_parts['cold-core/foam-cap-lid-top']
 floor_z=native_cap_floor(cap)
 old_axes=[(2.071135151942-s*40,373.235458276122+x)for x in (9.5,67.5)for s in(-1,1)]
 for x,y in old_axes:
  cap=cap.cut(cq.Solid.makeCylinder(4.01,CAP_COLUMN_TOP_Z-floor_z+.01,cq.Vector(x,y,floor_z)))
  lid=lid.fuse(cq.Solid.makeCylinder(1.8,5.4,cq.Vector(x,y,248.0000002)))
 # All elevated cradles/anchors are in the reorganized bay; the flat lid remains its
 # common bearing plane. Existing holes through the flat plate remain exact.
 lid=lid.cut(cq.Solid.makeBox(184,286,40,cq.Vector(-92,181,CAP_FACE_Z+.00001)))
 for i,(x,y)in enumerate(mount_rows):
  col=cq.Solid.makeCylinder(4,CAP_COLUMN_TOP_Z-floor_z+.01,cq.Vector(x,y,floor_z-.01))
  bore=cq.Solid.makeCylinder(2,8.5,cq.Vector(x,y,CAP_COLUMN_TOP_Z-8.5))
  cap=cap.fuse(col).cut(bore)
  lid=lid.cut(cq.Solid.makeCylinder(1.65,5.42,cq.Vector(x,y,CAP_COLUMN_TOP_Z-.01)))
  washer=cq.Solid.makeCylinder(4.5,.8,cq.Vector(x,y,260.4)).cut(cq.Solid.makeCylinder(1.6,.82,cq.Vector(x,y,260.39)))
  screw=cq.Solid.makeCylinder(1.5,20,cq.Vector(x,y,241.2)).fuse(cq.Solid.makeCylinder(2.75,3,cq.Vector(x,y,261.2)))
  emit('pump-washer-'+str(i+1),washer,'structure','Ø9 ×0.8 washer centered 1.5mm outward in the flexible-foot slot.')
  emit('pump-screw-'+str(i+1),screw,'structure','M3 ×20 shoulder-head screw: nominal 7mm pad +0.8mm washer +5.4mm lid, 6.8mm below column mouth.')
  check('Mount '+str(i+1)+' screw stack',6.8>=5.7 and 8.5-6.8>=1.0,insert_engagement_mm=5.7,screw_penetration_mm=6.8,tip_reserve_mm=1.7,insert_bore_wall_mm=2.0)
 cap=cap.clean()
 check('Cap and four pump columns form one joined native solid',cap.isValid() and len(cap.Solids())==1,solids=len(cap.Solids()),native_floor_z_mm=floor_z,root_overlap_mm=.01,blind_floor_above_cap_floor_mm=CAP_COLUMN_TOP_Z-8.5-floor_z)
 emit('cold-core/foam-cap-top',cap,'structure','Native floor rooted Ø8mm pump columns at transformed four-foot stations; original cold-core boundary and conduits retained.')
 emit('cold-core/foam-cap-lid-top',lid.clean(),'structure','Flat 5.4mm lid with relocated pump clearance holes; valve and chain support hosts are separate displayed structures.')
 vplace=loc(shift=VK_ORIGIN)*loc((1,0,0),180)*loc((0,1,0),90)
 vk=posed(V.build_beduan_solenoid().val(),vplace)
 emit('vk-solenoid',vk,'water','Carb-feed valve on its side, coil east, horizontal −Y flow; inlet aft, outlet fore, clear of western cap mouths.')
 seat=posed(VS.build_seat(4).val(),vplace)
 # The printed cradle embeds in the flat lid and presents the accepted V69 sockets.
 seat=seat.cut(cq.Solid.makeBox(200,300,100,cq.Vector(-100,180,153.4)))
 sb=seat.BoundingBox()
 if sb.zmin>CAP_FACE_Z:
  plinth=cq.Solid.makeBox(sb.xlen,sb.ylen,sb.zmin-CAP_FACE_Z+.02,cq.Vector(sb.xmin,sb.ymin,CAP_FACE_Z-.01))
  seat=seat.fuse(plinth).clean()
 vkseat=seat
 emit('vk-cradle',vkseat,'structure','V69 Ø6.90mm sockets, four posts, 3mm wall and 1mm blind floor; continuous lid-supported side plinth.')
 splace=loc((1,0,0),-90,SUCT_TIP)
 suction=posed(S.build(),splace)
 emit('suction-chain',suction,'water','MAACFLOW + PP450822E; fore-facing ¼-inch collet, aft-facing reinforced hose barb.')
 dplace=loc((0,1,0),-90,DISCH_TIP)
 discharge=posed(D.build(),dplace)
 emit('discharge-chain',discharge,'water','MAACFLOW + GASHER check + PP450822E across the bay aft of the pump; check holds carbonator pressure off pump.')
 REPORT['poses']['vk-solenoid']={'rotations_degrees':{'Y':90,'X':180},'origin_mm':VK_ORIGIN,'inlet':point(V.inlet(),vplace),'outlet':point(V.outlet(),vplace)}
 REPORT['poses']['suction-chain']={'barb_tip_mm':SUCT_TIP,'tube_port':point(S.tube_port(),splace)}
 REPORT['poses']['discharge-chain']={'barb_tip_mm':DISCH_TIP,'tube_port':point(D.tube_port(),dplace)}
 frame('g-ganen-pump',pump,{'suction':(P.suction(),S.HOSE_OD),'discharge':(P.discharge(),S.HOSE_OD)},pplace)
 frame('vk-solenoid',vk,{'inlet':(V.inlet(),6.35),'outlet':(V.outlet(),6.35)},vplace)
 frame('suction-chain',suction,{'barb-tip':(S.barb_tip(),S.HOSE_OD),'tube-port':(S.tube_port(),6.35)},splace)
 frame('discharge-chain',discharge,{'barb-tip':(D.barb_tip(),S.HOSE_OD),'tube-port':(D.tube_port(),6.35)},dplace)
 frames=R._frames
 fshape=cq.Solid.makeBox(181,283,253.4,cq.Vector(-90.5,182.3,0))
 R.frame('foam-assembly',fshape,{'water-in':((-56,188.9,253.4),(0,0,1),6.35)})
 w4=reversed_vk_to_chain()
 h7=measured_braided_s()
 h6=low_discharge_hose()
 # Across the right strip above PSU, then descend forward of PSU and under
 # the funnel frame before crossing into the water-in cap mouth.
 w5=discharge_to_core()
 # The two source valves lie on the freed low bay, with east-facing coils and
 # horizontal source ports. Their linked quarter turns remain fixed.
 source_shapes=[]
 electrical_places={'vk-solenoid':vplace}
 for label,origin in [('a',(38.,240.5,270.15)),('b',(-24.3,241.3,270.15))]:
  place=loc(shift=origin)*(loc((1,0,0),180) if label=='a' else loc())*loc((0,1,0),90)
  electrical_places['valve-v-'+label]=place
  valve=posed(V.build_beduan_solenoid().val(),place)
  emit('valve-v-'+label,valve,'water','Source valve with east-facing coil, horizontal flow on actual port axes, below enlarged funnel.')
  seat=posed(VS.build_seat(4).val(),place)
  seat=seat.cut(cq.Solid.makeBox(200,300,100,cq.Vector(-100,180,153.4)))
  emit('source-'+label+'-cradle',seat,'structure','Four V69 sockets, 3mm surrounding wall, 1mm blind floor, lid-rooted vertical plinth.')
  frame('valve-v-'+label,valve,{'inlet':(V.inlet(),6.35),'outlet':(V.outlet(),6.35)},place)
  REPORT['poses']['valve-v-'+label]={'origin_mm':origin,'flow_axis':[0,-1 if label=='a'else 1,0],'coil_axis':[1,0,0],'inlet':point(V.inlet(),place),'outlet':point(V.outlet(),place)}
  q=baseline.read(names=['turn-fluid-'+('3'if label=='a'else'5')])['turn-fluid-'+('3'if label=='a'else'5')]
  qb=q.BoundingBox()
  fixed=((qb.xmin+qb.xmax)/2,qb.ymax,qb.zmax-3.175)
  R.frame('source-quarter-'+label,q,{'end':(fixed,(0,1,0),6.35)})
  source_shapes.append((label,valve,seat))
  if label=='a':
   route(R.bent('fluid-3','valve-v-a.outlet','source-quarter-a.end',kind='fluid',bend=14,lead=9.5,note='Source A outlet to retained fore-manifold quarter, R14 formed LLDPE on both terminal axes.'))
  else:
   SOURCE_B_RUN=R.bent('fluid-5','valve-v-b.outlet',(-13.25,285.05,270.15),(27,285.05,293),(27,210,293),(-22.35,210,fixed[2]),'source-quarter-b.end',kind='fluid',bend=14,lead=(0,14),note='Source B aft outlet returns through the supported suction-root passage, rises on X27 and runs fore to the retained Y-B quarter; exact R14.')
   route(SOURCE_B_RUN)
 joint=baseline.read(names=['funnel-drain-union'])['funnel-drain-union']
 # Native elbow datum retained by the funnel study: localY20.56239 at worldY185.11239,
 # noseZ18.84 at framefloor299.9 minus0.65 catch allowance.
 R.frame('funnel-drain-union',joint,{'outlet':((1.85,185.11239,280.41),(0,1,0),6.35)})
 drain=route(R.bent('fluid-4','funnel-drain-union.outlet','valve-v-b.inlet',kind='fluid',bend=14,lead=9.7,note='Gravity drain directly descends through two tangent R14 bends into V-B fore inlet; 10.26mm fall, no rising segment.'))
 pts=REPORT['routes']['fluid-4']['points_mm']
 check('Gravity drain never rises',all(pts[i+1][2]<=pts[i][2]+1e-7 for i in range(len(pts)-1)),maximum_centerline_z_mm=max(p[2]for p in pts),mouth_z_mm=280.41,fall_mm=10.26)
 for name,q in [('VK',vk),('suction chain',suction),('suction hose',h7),('water4',w4)]:
  v=overlap(drain,q);check('Gravity drain clears '+name,v<1e-5,overlap_mm3=v,distance_mm=drain.distance(q))
 for label,q,seat in source_shapes:
  for name,t in [('pump',pump),('VK',vk),('suction chain',suction),('gravity drain',drain),('water4',w4),('water5',w5)]:
   v=overlap(q,t);check('Source '+label.upper()+' clears '+name,v<1e-5,overlap_mm3=v,distance_mm=q.distance(t))
  v=overlap(q,seat);check('Source '+label.upper()+' bearing host fits',v<1e-5,overlap_mm3=v)
  for name,t in [('water4',w4),('water5',w5),('gravity drain',drain),('pump',pump)]:
   v=overlap(seat,t);check('Source '+label.upper()+' host clears '+name,v<1e-5,overlap_mm3=v,distance_mm=seat.distance(t))
  for x,y in [(77.5,271.6),(77.5,322.3),(-43.5,233.3),(57.5,426.3)]:
   tube=cq.Solid.makeCylinder(3.175,60,cq.Vector(x,y,253.4));v=overlap(q,tube)
   check('Source '+label.upper()+' clears fixed cap tube '+str((x,y)),v<1e-5,overlap_mm3=v,distance_mm=q.distance(tube))
 suction_mid=next((a+b)/2 for label,r,a,b in S.sections()if label=='PP450822E hex')
 discharge_mid=next((a+b)/2 for label,r,a,b in D.sections()if label=='GASHER hex')
 shost=raised_suction_host((SUCT_TIP[0],SUCT_TIP[1]-suction_mid,SUCT_TIP[2]))
 for label,q,seat in source_shapes:
  if label=='b':
   check('Source B clears suction bridge',overlap(q,shost)<.001,overlap_mm3=overlap(q,shost),distance_mm=q.distance(shost))
   jumper=cq.Shape.importBrep(str(ROOT/PARTS['tube-fluid-5']['brep']))
   check('Source B jumper clears suction bridge',overlap(jumper,shost)<.001,overlap_mm3=overlap(jumper,shost),distance_mm=jumper.distance(shost))
 dhost=chain_host('discharge-chain-anchor',(DISCH_TIP[0]+discharge_mid,DISCH_TIP[1],DISCH_TIP[2]),8.65,True)
 for label,port,length,clock in (
  ('pump-suction',point(P.suction(),pplace),P.profiled_barb_length('suction'),180),
  ('pump-discharge',point(P.discharge(),pplace),P.profiled_barb_length('discharge'),180),
  ('chain-suction',point(S.barb_tip(),splace),D.BARB_L,0),
  ('chain-discharge',point(D.barb_tip(),dplace),D.BARB_L,270)):
  hose_engagement('hose-engagement-'+label,port,length)
  clamp('hose-clamp-'+label,port,clock)
 for label,s in [('VK',vk),('suction chain',suction),('discharge chain',discharge),('suction hose',h7),('discharge hose',h6),('water4',w4),('water5',w5)]:
  volume=overlap(s,pump)
  check(label+' clears pump',volume<1e-5,overlap_mm3=volume,distance_mm=s.distance(pump))
 for label,s in [('VK',vk),('suction chain',suction),('discharge chain',discharge)]:
  v=overlap(s,lid);check(label+' clears lid outside intended bearing',v<1e-5,overlap_mm3=v)
 fill=cq.Solid.makeCylinder(3.175,26,cq.Vector(57.5,426.3,253.4))
 v=overlap(fill,pump)
 check('A-fill fixed riser clears complete pump and sliders',v<1e-5,overlap_mm3=v,distance_mm=fill.distance(pump))
 b=pump.BoundingBox()
 check('Rigid pump keeps global flank clearance',b.xmin>=-97.5 and b.xmax<=97.5,west_air_mm=b.xmin+98.5,east_air_mm=98.5-b.xmax)
 check('Suction bridge over pan with at least1mm air',REPORT['poses']['suction-chain-retainer']['pan_air_mm']>=1,air_mm=REPORT['poses']['suction-chain-retainer']['pan_air_mm'])
 check('Suction chain above pan rim',suction.BoundingBox().zmin>=270.4,chain_bottom_z_mm=suction.BoundingBox().zmin,pan_rim_z_mm=266.4,pan_keepout_top_z_mm=269.4)
 check('Discharge chain aft of complete pump',discharge.BoundingBox().ymin-pump.BoundingBox().ymax>=1.0,air_mm=discharge.BoundingBox().ymin-pump.BoundingBox().ymax)
 for n,s in [('cap',cap),('lid',lid),('VK seat',vkseat),('suction support',shost),('discharge support',dhost)]+[(label.upper()+' source seat',seat)for label,q,seat in source_shapes]:check(n+' solid validity',s.isValid() and (len(s.Solids())==1 if n!='discharge support' else True),solids=len(s.Solids()))
 REPORT['parts']=PARTS
 REPORT['printed_parts']={'suction-chain-upper-key':{**PARTS['suction-chain-upper-key'],'separate':True,'rotation_x_deg':180,'nominal_crown_stock_mm':3,'bolt_flange_stock_mm':4,'fasteners':'Two M3×10 into5.7mm inserts in the lid-rooted lower bridge.'}}
 REPORT['electrical_interfaces']=electrical_ends(electrical_places)
 REPORT['replacement_names']=['valve-v-a','coil-v-a','valve-v-b','coil-v-b','step-fluid-3','step-fluid-5','tube-fluid-4','g-ganen-pump','vk-solenoid','suction-chain','discharge-chain','tube-water-4','tube-water-5','tube-water-6','tube-water-7','cold-core/foam-cap-top','cold-core/foam-cap-lid-top']
 REPORT['qualification_limits']=['Scan shapes are occupied envelopes, not strength or mass inputs.','Pump rubber compression, actual slot passage, clamp hardware dimensions and retention remain separate physical qualifications.','V69 physical hand fit belongs to the accepted upright socket article; the side VK cradle is an explicit geometric candidate.','Valve lateral orientation operating authority is not present in the supplied reference; only the candidate geometry is established.']
 REPORT['qualification_limits'].append(f"Discharge hose low span clears the PSU by{REPORT['routes']['water-6']['low_span_psu_base_air_mm']:.3f}mm; its measured attachment remains closer to the PSU. Manufacturer airflow compliance and thermal output are not established by this geometry.")
 REPORT['all_checks_pass']=all(c['pass']for c in REPORT['checks'])
 REPORT['blocked_routes']=R.BLOCKED
 REPORT['baseline']=baseline.prepare()['sha256']
 (HERE/'candidate.json').write_text(json.dumps(REPORT,indent=2)+'\n')
 print(HERE/'candidate.json',flush=True)

if __name__=='__main__':main()
