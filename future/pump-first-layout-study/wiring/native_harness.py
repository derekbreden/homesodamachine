"""Conservative routing guide followed by exact native wire sweeps.

The guide rasterizes the occupied native solids. A search result is only a
candidate: the emitted R3.4 analytic arcs and complete wire exterior are checked
against the B-reps afterwards. Wire diameter and bend radius are fit reserves,
not a physical wire or termination qualification.
"""
from pathlib import Path
from io import BytesIO
import hashlib, heapq, itertools, json, math, sys
import numpy as np
from scipy.spatial import cKDTree
import trimesh
import cadquery as cq

STUDY=Path(__file__).resolve().parents[1]
ROOT=STUDY.parents[1]
sys.path.insert(0,str(STUDY))
import audit

RADIUS=3.4
PITCH=1.0

class NativeCollision(ValueError):
    def __init__(self,name,shape,hits):
        super().__init__(f'{name}: guide candidate fails exact native clearance {hits}')
        self.shape=shape;self.hits=hits

def bounds(s):
    cached=getattr(s,'_pump_layout_bounds',None)
    if cached is None:
        b=s.BoundingBox();cached=(b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax)
        s._pump_layout_bounds=cached
    return list(cached)

def broad(a,b,pad=0):
    return all(a[i]<=b[i+3]+pad and b[i]<=a[i+3]+pad for i in range(3))

def simplified(points):
    out=[]
    for p in points:
        p=np.asarray(p,dtype=float)
        if out and np.linalg.norm(p-out[-1])<1e-7:continue
        while len(out)>=2:
            u=out[-1]-out[-2];v=p-out[-1]
            if np.linalg.norm(np.cross(u,v))<1e-6 and np.dot(u,v)>0:out.pop()
            else:break
        out.append(p)
    return out

def sweep(points,diameter,radius=RADIUS,with_centerline=False):
    ps=simplified(points);cuts=[0.]*len(ps);corners={}
    for i in range(1,len(ps)-1):
        u=(ps[i]-ps[i-1]);u=u/np.linalg.norm(u)
        v=(ps[i+1]-ps[i]);v=v/np.linalg.norm(v)
        angle=math.acos(float(np.clip(np.dot(u,v),-1,1)))
        if angle<1e-6:continue
        if angle>math.pi-1e-5:raise ValueError('Wire path reverses')
        take=radius*math.tan(angle/2);cuts[i]=take
        a=ps[i]-u*take;b=ps[i]+v*take
        center=ps[i]+(v-u)/np.linalg.norm(v-u)*(radius/math.cos(angle/2))
        radial=(a-center)/radius+(b-center)/radius
        mid=center+radial/np.linalg.norm(radial)*radius
        corners[i]=(a,mid,b)
    edges=[];previous=ps[0]
    for i in range(1,len(ps)):
        length=np.linalg.norm(ps[i]-ps[i-1])
        if cuts[i-1]+cuts[i]>length+1e-6:
            raise ValueError(f'Wire R{radius} needs {cuts[i-1]+cuts[i]:.4f}, leg {length:.4f}')
        end=corners[i][0] if i in corners else ps[i]
        if np.linalg.norm(end-previous)>1e-7:edges.append(cq.Edge.makeLine(cq.Vector(*previous),cq.Vector(*end)))
        if i in corners:
            a,m,b=corners[i];edges.append(cq.Edge.makeThreePointArc(cq.Vector(*a),cq.Vector(*m),cq.Vector(*b)));previous=b
        else:previous=end
    path=cq.Wire.assembleEdges(edges)
    tangent=ps[1]-ps[0]
    profile=cq.Wire.makeCircle(diameter/2,cq.Vector(*ps[0]),cq.Vector(*tangent))
    shape=cq.Solid.sweep(profile,[],path,makeSolid=True,isFrenet=False)
    if not shape.isValid():raise ValueError('Invalid wire sweep')
    expected=math.pi*(diameter/2)**2*path.Length()
    if abs(shape.Volume(tol=1e-9)-expected)>max(.001,expected*1e-6):
        raise ValueError('Wire sweep does not preserve circular section along its complete path')
    rec={'points_mm':[p.tolist() for p in ps],'radius_mm':radius,'diameter_mm':diameter,'length_mm':path.Length()}
    if with_centerline:
        rec['centerline_samples_mm']=[v.toTuple() for edge in edges for v in edge.sample(max(2,int(math.ceil(edge.Length()/.3))+1))[0]]
    return shape,rec

def occupied_points(name,shape,cache):
    # Absolute meshing avoids excessive fillet tessellation in the cap. This
    # raster ranks candidates; complete exact native solids decide admission.
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopAbs import TopAbs_REVERSED
    stream=BytesIO();shape.exportBrep(stream);digest=hashlib.sha256(stream.getvalue()).hexdigest()
    path=ROOT/'.cache/pump-first-layout/wiring/voxels'/f'{digest}-control-absolute0.3-p{PITCH:g}.npz'
    if path.exists():return np.load(path)['points']
    chunks=[]
    for source in shape.Solids():
        solid=source.copy(mesh=False);BRepMesh_IncrementalMesh(solid.wrapped,.3,False,.2,True)
        vertices=[];triangles=[]
        for face in solid.Faces():
            location=TopLoc_Location();poly=BRep_Tool.Triangulation_s(face.wrapped,location)
            if poly is None:continue
            transform=location.Transformation();offset=len(vertices);reverse=face.wrapped.Orientation()==TopAbs_REVERSED
            vertices.extend([[p.X(),p.Y(),p.Z()] for p in [poly.Node(i).Transformed(transform) for i in range(1,poly.NbNodes()+1)]])
            for triangle in poly.Triangles():
                order=[1,3,2] if reverse else [1,2,3]
                triangles.append([triangle.Value(i)+offset-1 for i in order])
        if not triangles:continue
        mesh=trimesh.Trimesh(vertices=vertices,faces=triangles,process=True)
        chunks.append(mesh.voxelized(PITCH).fill().points)
    points=np.unique(np.vstack(chunks),axis=0) if chunks else np.zeros((0,3))
    path.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(path,points=points)
    print('wire guide absolute ranking',name,len(points),flush=True)
    return points

class Guide:
    def __init__(self,ports,diameter=3.2):
        self.diameter=diameter
        # Local recesses may extend into the established thick bay skin, while
        # leaving at least 3 mm exterior stock. Fixed forward geometry remains
        # an obstacle and every recess is emitted as an exact swept cutter.
        self.scope=[-101.9,295.7,255.5,101.9,463.2,349.4]
        base=[np.arange(self.scope[i],self.scope[i+3]+.01,4.2) for i in range(3)]
        important=[[float(p['point'][i]) for p in ports] for i in range(3)]
        for p in ports:
            v=np.asarray(p['axis'],float)
            for length in [5.4,6.8,8.4,12.6,16.8]:
                q=np.asarray(p['point'])+v*length
                for i in range(3):important[i].append(float(q[i]))
            for lead in p.get('lead_paths',[]):
                for q in lead:
                    for i in range(3):important[i].append(float(q[i]))
        important[2]+=[282.5,285.4,325.,329.15,333.15,333.25,335.75,339.95,344.15,344.75,348.35,350.0]
        self.axes=[np.unique(np.round(np.r_[base[i],important[i]],6)) for i in range(3)]
        self.axes=[a[(a>=self.scope[i])&(a<=self.scope[i+3])] for i,a in enumerate(self.axes)]
        self.dims=tuple(len(a) for a in self.axes)
        grids=np.meshgrid(*self.axes,indexing='ij');self.grid=np.stack(grids,axis=-1)
        self.points=self.grid.reshape(-1,3)
        self.models,self.records,_,_,_=audit.collect()
        lower_path=STUDY/'wiring/lower-lead-exits.json'
        if lower_path.exists():
            for name,r in json.loads(lower_path.read_text())['parts'].items():
                self.records[name]=r;self.models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
        control_path=STUDY/'wiring/controls-candidate.json'
        if control_path.exists():
            controls=json.loads(control_path.read_text())
            for name,r in controls.get('parts',{}).items():
                self.records[name]=r;self.models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
        roof=json.loads((STUDY/'mounts/roof-candidate.json').read_text())
        for name,fields in roof.get('working_envelopes',{}).items():
            r=fields['levers'];key='lever-space-'+name
            self.records[key]=r;self.models[key]=cq.Shape.importBrep(str(ROOT/r['brep']))
        shell=json.loads((STUDY/'funnel/shells.json').read_text())
        routing=json.loads((STUDY/'routing/candidate.json').read_text())
        r=routing.get('interface_moves',{}).get('nameplate',{}).get('new_receiver',shell['interfaces']['retained-nameplate-stock'])
        self.records['protected-nameplate-stock']=r
        self.models['protected-nameplate-stock']=cq.Shape.importBrep(str(ROOT/r['brep']))
        backing=routing.get('interface_moves',{}).get('nameplate',{}).get('new_backing')
        if backing:
            self.records['protected-nameplate-backing']=backing
            self.models['protected-nameplate-backing']=cq.Shape.importBrep(str(ROOT/backing['brep']))
        control_reserves=STUDY/'wiring/control-reserves.json'
        if control_reserves.exists():
            reserves=json.loads(control_reserves.read_text())
            accepted={c['part'] for c in reserves.get('native_checks',[]) if c.get('pass')}
            for name,r in reserves.get('parts',{}).items():
                if not reserves.get('pass') and name not in accepted:continue
                self.records[name]=r;self.models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
        fanouts_path=STUDY/'wiring/control-fanouts-check.json'
        if fanouts_path.exists():
            fanouts=json.loads(fanouts_path.read_text())
            accepted={c['part'] for c in fanouts.get('native_checks',[]) if c.get('pass')}
            for name,r in fanouts.get('parts',{}).items():
                if not fanouts.get('pass') and name not in accepted:continue
                self.records[name]=r;self.models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
        self.native_inputs={n:{'brep':r['brep'],'sha256':hashlib.sha256((ROOT/r['brep']).read_bytes()).hexdigest()}
                            for n,r in self.records.items()if n in self.models and r is not None
                            and not n.startswith(('wire-AC','wire-DC','wire-PE','power-'))
                            and broad(bounds(self.models[n]),self.scope,diameter+2)}
        chunks=[];self.obstacles={}
        for name,shape in self.models.items():
            if name.startswith(('enclosure-back-top','enclosure-front-top')):continue
            if name.startswith(('wire-AC','wire-DC','wire-PE','power-')):continue
            if not broad(bounds(shape),self.scope,diameter+2):continue
            points=occupied_points(name,shape,self.records[name].get('brep'))
            keep=np.all((points>=np.asarray(self.scope[:3])-5)&(points<=np.asarray(self.scope[3:])+5),axis=1)
            chunks.append(points[keep]);self.obstacles[name]=shape
        self.voxels=np.vstack(chunks)
        self.wires={};self.ports=ports;self.refresh()

    def refresh(self):
        tree=cKDTree(self.voxels);self.tree=tree
        # Raster clearance ranks candidates; it cannot prove interference or
        # fit. Every complete analytic wire is tested against native solids.
        clearance=self.diameter/2+.2
        d=tree.query(self.points,workers=-1)[0]
        self.free=(d>=clearance).reshape(self.dims)
        if self.wires:
            centers=getattr(self,'wire_centers',{})
            samples=[centers[n] for n in self.wires if n in centers]
            if samples:
                distances=cKDTree(np.vstack(samples)).query(self.points,workers=-1)[0]
                self.free &= (distances>=self.diameter+.15).reshape(self.dims)
        print('wire grid',self.dims,'free',int(self.free.sum()),flush=True)

    def idx(self,p):
        return tuple(int(np.argmin(abs(a-p[i]))) for i,a in enumerate(self.axes))

    def lead_options(self,port):
        p=np.asarray(port['point'],float);v=np.asarray(port['axis'],float)
        axis=int(np.argmax(abs(v)));sign=1 if v[axis]>0 else -1
        options=[]
        if port.get('lead_paths'):
            for lead in port['lead_paths']:
                q=np.asarray(lead[-1]);ix=self.idx(q)
                if np.linalg.norm(self.grid[ix]-q)>1e-4:continue
                shape,rec=sweep(lead,self.diameter)
                native={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
                if any(n!=port.get('owner') and broad(bounds(shape),bounds(s)) and shape.distance(s)<1e-6 and abs(shape.intersect(s,tol=.0001).Volume(tol=1e-9))>.001 for n,s in native.items()):continue
                # A native-checked prepared exit can lie in a hollow that the
                # filled routing raster conservatively closes. Admit that one
                # dock; the complete resulting route still needs native proof.
                self.free[ix]=True
                vector=np.asarray(lead[-1])-np.asarray(lead[-2]);axis=int(np.argmax(abs(vector)))
                if np.count_nonzero(abs(vector)>1e-6)>1:direction=6
                else:direction=axis*2+(0 if vector[axis]>0 else 1)
                options.append((ix,direction,rec['length_mm'],lead))
            return self.admit_power_dock_corridors(port,options)
        diagonal=np.count_nonzero(abs(v)>1e-5)>1
        # Exact straight normal approach, with enough reach for a 3.4mm corner.
        values=[8.4,12.6,16.8] if diagonal else [(value-p[axis])*sign for value in self.axes[axis]]
        for length in values:
            if length<5.4-1e-6 or length>20+1e-6:continue
            q=p+v*length;ix=self.idx(q)
            if np.linalg.norm(self.grid[ix]-q)>1e-4 or not self.free[ix]:continue
            straight=cq.Solid.makeCylinder(self.diameter/2,length,cq.Vector(*p),cq.Vector(*v))
            hit=[]
            for n,s in {**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}.items():
                if n==port.get('owner'):continue
                if broad(bounds(straight),bounds(s)) and straight.distance(s)<1e-6 and abs(straight.intersect(s,tol=.0001).Volume(tol=1e-9))>.001:hit.append(n)
            if hit:continue
            options.append((ix,6 if diagonal else axis*2+(0 if sign>0 else 1),length,[port['point'],q.tolist()]))
        return self.admit_power_dock_corridors(port,options)

    def admit_power_dock_corridors(self,port,options):
        """Recover only native-clear first turns hidden by the filled raster.

        Ranking occupancy conservatively fills some hollow purchased parts.
        A complete analytic endpoint prefix can admit the affected stations;
        the complete resulting conductor still receives the native check.
        """
        if not getattr(self,'_native_power_dock_admission',False):return options
        native={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
        admitted=0
        for ix,last,_,lead in options:
            p=self.grid[ix]
            for direction in range(6):
                if last<6 and direction==(last^1):continue
                key=(port['label'],ix,direction)
                cached=self._power_dock_corridors.get(key)
                if cached is None:
                    axis=direction//2;sign=1 if direction%2==0 else -1
                    target=list(ix);distance=0.;indices=[]
                    need=.01 if direction==last else (10.5 if last==6 else 2*RADIUS+.05)
                    while distance<need:
                        target[axis]+=sign
                        if target[axis]<0 or target[axis]>=self.dims[axis]:break
                        q=tuple(target);indices.append(q)
                        distance=abs(self.axes[axis][target[axis]]-p[axis])
                    clear=False
                    if distance>=need:
                        q=self.grid[tuple(target)]
                        try:
                            shape,_=sweep(lead+[q.tolist()],self.diameter)
                            box=bounds(shape)
                            stock=(box[0]>=-103.5 and box[3]<=103.5 and
                                   box[1]>=295.691508 and box[2]>=253.4 and box[5]<=351)
                            clear=stock and not any(n!=port.get('owner') and broad(box,bounds(s)) and
                                shape.distance(s)<1e-6 and abs(shape.intersect(s,tol=.0001).Volume(tol=1e-9))>.001
                                for n,s in native.items())
                        except ValueError:pass
                    cached=(clear,indices);self._power_dock_corridors[key]=cached
                if cached[0]:
                    for q in cached[1]:self.free[q]=True
                    admitted+=1
        print('wire native dock corridors',port['label'],admitted,flush=True)
        return options

    def route(self,a,b,name):
        initial=self.free.copy()
        self._native_power_dock_admission=False
        self._power_dock_corridors={}
        try:
            for attempt in range(10):
                try:return self._route_once(a,b,name)
                except NativeCollision as e:
                    for hit in e.hits:
                        obstacle={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}[hit['part']]
                        overlap=e.shape.intersect(obstacle,tol=.0001);box=bounds(overlap)
                        # Ban the corner's complete fillet neighborhood. A
                        # small tangent intersection can sit between guide
                        # vertices; banning only the wire radius repeats the
                        # same rounded corner without changing its grid path.
                        pad=self.diameter/2+RADIUS+.35
                        blocked=np.all((self.points>=np.asarray(box[:3])-pad)&(self.points<=np.asarray(box[3:])+pad),axis=1)
                        self.free &= (~blocked).reshape(self.dims)
                    print('wire native retry',name,attempt+1,e.hits,flush=True)
                except ValueError as e:
                    if self._native_power_dock_admission or 'no guide route after' not in str(e):raise
                    self._native_power_dock_admission=True
                    print('wire native dock repair',name,str(e),flush=True)
            raise ValueError(f'{name}: ten guide candidates failed exact native clearance')
        finally:
            self.free=initial
            self._native_power_dock_admission=False

    def _route_once(self,a,b,name):
        saved_free=self.free.copy()
        # A later conductor still needs its normal make-up reach. Reserve
        # every other endpoint now, so an early wire cannot consume that exit.
        samples={};future={}
        for p in self.ports:
            if p==a or p==b:continue
            if p['label']in getattr(self,'used_port_labels',set()):continue
            reach=12.6 if p.get('owner')=='c14-inlet' else 8.4
            leads=p.get('lead_paths') or [[p['point'],(np.asarray(p['point'])+np.asarray(p['axis'])*reach).tolist()]]
            for lead in leads[:1]:
                diameter=p.get('diameter_mm',self.diameter)
                reserve,rec=sweep(lead,diameter,radius=p.get('bend_radius_mm',RADIUS),with_centerline=True)
                samples.setdefault(diameter,[]).extend(rec['centerline_samples_mm'])
                future['reserved-lead-'+p['label']]=reserve
        self._active_future=future
        for diameter,centres in samples.items():
            dist=cKDTree(centres).query(self.points,workers=-1)[0]
            self.free &= (dist>=(self.diameter+diameter)/2+.16).reshape(self.dims)
        starts=self.lead_options(a);ends=self.lead_options(b)
        if not starts or not ends:
            self.free=saved_free
            raise ValueError(f'{name}: no normal dock; starts {len(starts)} ends {len(ends)}')
        goals={e[0]:e for e in ends};goal_points=np.asarray([self.grid[e[0]] for e in ends])
        heuristic=lambda p:float(np.min(np.sum(abs(goal_points-p),axis=1)))
        serial=itertools.count();heap=[];costs={};prev={};origins={}
        start_leads={}
        for ix,d,l,lead in starts:
            state=(ix,d);costs[state]=l;origins[state]=state
            start_leads[state]=lead
            heapq.heappush(heap,(l+heuristic(self.grid[ix]),next(serial),l,state))
        winner=None;expanded=0
        while heap:
            _,_,cost,state=heapq.heappop(heap)
            if cost>costs.get(state,float('inf'))+1e-6:continue
            ix,last=state;p=self.grid[ix]
            if ix in goals and last!=(goals[ix][1]):winner=state;break
            expanded+=1
            if expanded>getattr(self,'max_states',600000):break
            for direction in range(6):
                if last<6 and direction==last^1:continue
                axis=direction//2;sgn=1 if direction%2==0 else -1
                target=list(ix);distance=0.;ok=True
                # Each new run spans at least 2R, so adjacent analytic fillets
                # cannot consume the same short leg. Straight continuation is
                # allowed between neighboring nonuniform grid stations.
                need=.01 if direction==last else (10.5 if last==6 else 2*RADIUS+.05)
                while distance<need:
                    target[axis]+=sgn
                    if target[axis]<0 or target[axis]>=self.dims[axis]:ok=False;break
                    ti=tuple(target)
                    if not self.free[ti]:ok=False;break
                    distance=abs(self.axes[axis][target[axis]]-p[axis])
                if not ok:continue
                ti=tuple(target);new=(ti,direction)
                newcost=cost+distance+(1.0 if direction!=last else 0.)
                if newcost>=costs.get(new,float('inf'))-1e-6:continue
                costs[new]=newcost;prev[new]=state;origins[new]=origins[state]
                heapq.heappush(heap,(newcost+heuristic(self.grid[ti]),next(serial),newcost,new))
        self.free=saved_free
        if winner is None:raise ValueError(f'{name}: no guide route after {expanded} states')
        states=[winner]
        while states[-1] in prev:states.append(prev[states[-1]])
        states.reverse();lead=start_leads[origins[winner]];end_lead=goals[winner[0]][3]
        points=lead[:-1]+[self.grid[s[0]].tolist() for s in states]+list(reversed(end_lead))[1:]
        shape,rec=sweep(points,self.diameter,with_centerline=True)
        hits=[]
        for n,s in {**self.obstacles,**self.wires,**future}.items():
            if n in [a.get('owner'),b.get('owner')]:continue
            if broad(bounds(shape),bounds(s)) and shape.distance(s)<1e-6:
                volume=abs(shape.intersect(s,tol=.0001).Volume(tol=1e-9))
                if volume>.001:hits.append({'part':n,'overlap_mm3':volume})
        if hits:raise NativeCollision(name,shape,hits)
        rec.update({'from':a,'to':b,'search_states':expanded,'native_interferences':hits})
        self.wires[name]=shape
        if hasattr(self,'used_port_labels'):self.used_port_labels.update([a['label'],b['label']])
        if not hasattr(self,'wire_centers'):self.wire_centers={}
        self.wire_centers[name]=np.asarray(rec.pop('centerline_samples_mm'))
        print('WIRE',name,'length',round(rec['length_mm'],2),'states',expanded,flush=True)
        return shape,rec
