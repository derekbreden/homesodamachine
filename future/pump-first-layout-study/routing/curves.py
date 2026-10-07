"""Exact tangent circular paths with a fixed stock radius."""
import math,cadquery as cq
V=lambda p:p if isinstance(p,cq.Vector)else cq.Vector(*p)
X=V((1,0,0));Y=V((0,1,0));Z=V((0,0,1))
def line(a,b):
 a,b=V(a),V(b);return []if(a-b).Length<1e-6 else[cq.Edge.makeLine(a,b)]
def turn(a,h,k,theta=math.pi/2,r=14):
 a,h,k=V(a),V(h),V(k);b=a+h*(r*math.sin(theta))+k*(r*(1-math.cos(theta)));m=a+h*(r*math.sin(theta/2))+k*(r*(1-math.cos(theta/2)));return[cq.Edge.makeThreePointArc(a,m,b)],b

def s(a,h,b,r=14,lead_start=None):
 a,h,b=V(a),V(h),V(b);d=b-a;l=d.dot(h);o=d-h*l;t=o.Length
 if t<1e-8:return line(a,b),{'radii':[],'leads':[l,0]}
 if t>4*r:raise ValueError('S transverse offset exceeds4R')
 u=o.normalized();theta=math.acos(1-t/(2*r));need=2*r*math.sin(theta);remaining=l-need
 if remaining<-1e-7:raise ValueError(f'S cannot seat R{r}: long{l:.4f},need{need:.4f},off{t:.4f}')
 f=remaining/2 if lead_start is None else lead_start;last=remaining-f
 if min(f,last)<-1e-7:raise ValueError('S negative lead')
 c=a+h*f;es=line(a,c);a1,d=turn(c,h,u,theta,r);es+=a1
 # Second circular arc returns the direction to h.
 mid=d+h*(r*(math.sin(theta)-math.sin(theta/2)))+u*(r*(math.cos(theta/2)-math.cos(theta)));end=d+h*(r*math.sin(theta))+u*(r*(1-math.cos(theta)));es+=[cq.Edge.makeThreePointArc(d,mid,end)];es+=line(end,b)
 return es,{'radii':[r,r],'leads':[f,last],'theta_deg':math.degrees(theta),'error':(end+h*last-b).Length}
def wire(es):return cq.Wire.assembleEdges(es)
def validate(es):
 for i,(a,b) in enumerate(zip(es,es[1:])):
  gap=(a.endPoint()-b.startPoint()).Length
  angle=a.tangentAt(1).getAngle(b.tangentAt(0))
  if gap>1e-5 or angle>1e-5:
   raise ValueError(f'Non-tangent path at edge {i}: gap={gap:.9f}mm angle={math.degrees(angle):.6f}deg point={a.endPoint().toTuple()}')
 return True

def swept(es,normal,diam=6.35):
 validate(es);w=wire(es);start=es[0].startPoint();tangent=es[0].tangentAt(0)
 q=cq.Solid.sweep(cq.Wire.makeCircle(diam/2,start,tangent),[],w,makeSolid=True,isFrenet=True)
 expected=math.pi*(diam/2)**2*w.Length()
 if not q.isValid() or abs(q.Volume()-expected)>max(.05,expected*1e-6):
  raise ValueError(f'Circular tube sweep invalid or volume mismatch: {q.Volume():.6f}mm3 versus {expected:.6f}mm3')
 return q
def poly(points,r=14):
 import _routing as R
 pts=[tuple(V(p).toTuple())for p in points];R.BLOCKED.clear();bends=R._bends(pts,'local');caps=R._caps(bends,r,'local',6.35);rad=R.seat_radii(pts,bends,caps,'local',6.35);run=R.Run('local','water','','',pts,6.35,r,bends=bends,radii=rad,caps=caps)
 if run.tightest<r-1e-6:raise ValueError(f'polyline Rmin{run.tightest}: {pts}')
 return R.centreline(run).Edges(),run
