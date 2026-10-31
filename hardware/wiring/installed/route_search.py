"""Manual installed-route search against the actual populated viewer geometry.

This is an authoring aid, invoked explicitly. Saved hardware-relative stations
are the build inputs; expensive route search never runs during normal builds.
"""
from __future__ import annotations
from collections import Counter
import heapq
import itertools
import json
import math
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import fcl
import numpy as np
from hardware.wiring.installed.model import STOCK, Connection, rounded_segments, sampled_segments
from hardware.wiring.installed.review import load_mesh,base_name,wire_obstacle,same_part

OUT=Path(__file__).with_name('route-overrides.json')
TMP=ROOT/'tmp/wiring-foundation'


def capsule(a,b,r):
    a,b=np.asarray(a),np.asarray(b);d=b-a;length=float(np.linalg.norm(d))
    if length<1e-8:return fcl.CollisionObject(fcl.Sphere(r),fcl.Transform(a))
    z=d/length;other=np.array([1.,0,0]) if abs(z[0])<.8 else np.array([0.,1,0])
    x=np.cross(other,z);x/=np.linalg.norm(x);y=np.cross(z,x)
    return fcl.CollisionObject(fcl.Capsule(r,length),fcl.Transform(np.column_stack((x,y,z)),(a+b)/2))


def sampled(segments,step=1.):
    return np.asarray(sampled_segments(segments,step))


def tube_mesh(points,radius):
    tangent=np.gradient(points,axis=0);tangent/=np.linalg.norm(tangent,axis=1)[:,None]
    vertices=[]
    for p,z in zip(points,tangent):
        axis=np.array([1.,0,0]) if abs(z[0])<.8 else np.array([0.,1,0])
        x=np.cross(axis,z);x/=np.linalg.norm(x);y=np.cross(z,x)
        vertices.extend(p+radius*(x*math.cos(a)+y*math.sin(a)) for a in np.arange(12)*math.tau/12)
    faces=[]
    for i in range(len(points)-1):
        for j in range(12):
            a=i*12+j;b=i*12+(j+1)%12;c=a+12;d=b+12
            faces.extend(((a,b,c),(b,d,c)))
    for j in range(1,11):
        faces.append((0,j+1,j));o=(len(points)-1)*12;faces.append((o,o+j,o+j+1))
    return np.array(vertices),np.array(faces)


class Navigator:
    def __init__(self,meshes,terminals,terminations=None):
        meshes={n:m for n,m in meshes.items() if wire_obstacle(n)}
        self.names=list(meshes);self.terminals=terminals
        self.terminations=terminations or {}
        self.objects=[];self.los=[];self.his=[]
        for v,f in meshes.values():
            model=fcl.BVHModel();model.beginModel(len(v),len(f));model.addSubModel(v,f);model.endModel()
            self.objects.append(fcl.CollisionObject(model));self.los.append(v.min(0));self.his.append(v.max(0))
        self.los=np.array(self.los);self.his=np.array(self.his)
        self.wires=[];self.wire_los=np.empty((0,3));self.wire_his=np.empty((0,3))
        self.cache={};self.probes=0
        graph=__import__('hardware.wiring.installed.connections',fromlist=['connections']).connections()
        radii={}
        for c in graph:
            for id in (c.start,c.end):
                radii[id]=max(radii.get(id,0.),STOCK[c.stock]['od_mm']/2)
        self.keepout_ids=[];points=[];keepout_radii=[]
        used=set(radii)
        for id in sorted(used):
            t=terminals[id]
            for distance in (0.,):
                points.append(np.array(t['point'])+np.array(t['outward'])*distance);self.keepout_ids.append(id)
                keepout_radii.append(radii[id])
        self.keepout_points=np.array(points)
        self.keepout_radii=np.array(keepout_radii)
        self.actual_radius=None

    def clear(self,a,b,r,ends,packing=False):
        a,b=np.asarray(a),np.asarray(b)
        lo=np.minimum(a,b)-r;hi=np.maximum(a,b)+r
        # Preserve each actual mouth. Flexible dressing beyond it is supplied
        # by the routed wire, rather than an invented straight keep-out tube.
        keep=np.array([id not in (ends[0]['id'],ends[1]['id']) for id in self.keepout_ids])
        points=self.keepout_points[keep];d=b-a;length=np.dot(d,d)
        fraction=np.clip((points-a).dot(d)/length,0,1) if length>1e-12 else np.zeros(len(points))
        packing_radius=self.actual_radius if self.actual_radius is not None else r
        if packing and np.any(np.sum((points-a-fraction[:,None]*d)**2,axis=1)<(packing_radius+self.keepout_radii[keep]+.02)**2):return False
        ids=np.flatnonzero(np.all(self.his>=lo,axis=1)&np.all(self.los<=hi,axis=1))
        obj=None
        for i in ids:
            name=base_name(self.names[i])
            members=self.terminations.get(name,{}).get('terminal_ids',[])
            if any((same_part(name,t['part']) or t['id'] in members) and
                   max(np.linalg.norm(a-t['point']),np.linalg.norm(b-t['point']))<=8.3 for t in ends):continue
            key=(int(i),round(r,2),tuple(np.round(a,4)),tuple(np.round(b,4)))
            if key in self.cache:
                if not self.cache[key]:return False
                continue
            if obj is None:obj=capsule(a,b,r)
            hit=fcl.collide(obj,self.objects[i],fcl.CollisionRequest(),fcl.CollisionResult())>0
            self.cache[key]=not hit
            if hit:return False
        if packing and len(self.wires):
            ids=np.flatnonzero(np.all(self.wire_his>=lo,axis=1)&np.all(self.wire_los<=hi,axis=1))
            for i in ids:
                previous,other=self.wires[i]
                common=set(t['id'] for t in ends)&set(previous)
                if any(max(np.linalg.norm(a-self.terminals[t]['point']),np.linalg.norm(b-self.terminals[t]['point']))<=8.5 for t in common):continue
                packing_object=capsule(a,b,r+.015)
                if fcl.collide(packing_object,other,fcl.CollisionRequest(),fcl.CollisionResult())>0:return False
        self.probes+=1
        return True

    def reserve(self,row,points,r):
        segments=rounded_segments(points,2.0 if r<1.4 else 3.)
        v,f=tube_mesh(sampled(segments,1.5),r+.06)
        model=fcl.BVHModel();model.beginModel(len(v),len(f));model.addSubModel(v,f);model.endModel()
        self.wires.append(((row['start'],row['end']),fcl.CollisionObject(model)))
        self.wire_los=np.vstack((self.wire_los,v.min(0)));self.wire_his=np.vstack((self.wire_his,v.max(0)))

    def path(self,start,goal,r,ends,step=4.,limit=12000,domain=None,grid_origin=None):
        start,goal=np.asarray(start),np.asarray(goal)
        if self.clear(start,goal,r,ends):return [tuple(start),tuple(goal)]
        low=np.array([-100.,8.,2.]);high=np.array([99.,464.,349.])
        if domain is not None:low,high=map(np.asarray,domain)
        # Keep a bounded local search first; paths can still rise above a bank.
        low=np.maximum(low,np.minimum(start,goal)-np.array([65.,70.,65.]))
        high=np.minimum(high,np.maximum(start,goal)+np.array([65.,70.,65.]))
        # A packed connector or conduit can have room for a wire but no room
        # for a world-aligned grid node. Align the manual search to that mouth.
        offset=np.zeros(3) if grid_origin is None else np.asarray(grid_origin)
        def coord(k):return np.array(k,dtype=float)*step+offset
        def key(p):return tuple(np.round((p-offset)/step).astype(int))
        origin=key(start);target=key(goal)
        near=[]
        for delta in itertools.product((-1,0,1),repeat=3):
            k=tuple(origin[i]+delta[i] for i in range(3));p=coord(k)
            if np.all(p>=low)&np.all(p<=high) and self.clear(start,p,r,ends):near.append((float(np.linalg.norm(p-start)),k))
        if not near:return None
        costs={};parents={};queue=[]
        for cost,k in near:
            costs[k]=cost;parents[k]=None
            heapq.heappush(queue,(cost+1.22*float(np.linalg.norm(coord(k)-goal)),cost,k))
        offsets=[(d,math.sqrt(sum(v*v for v in d))*step) for d in itertools.product((-1,0,1),repeat=3) if any(d)]
        count=0
        while queue and count<limit:
            _score,cost,k=heapq.heappop(queue)
            if cost>costs[k]+1e-6:continue
            count+=1;p=coord(k)
            if np.linalg.norm(p-goal)<step*2 and self.clear(p,goal,r,ends):
                route=[tuple(goal),tuple(p)]
                while parents[k] is not None:
                    k=parents[k];route.append(tuple(coord(k)))
                route.append(tuple(start));route.reverse()
                # Line-of-sight simplification uses the same larger bodies as the search.
                simplified=[route[0]];i=0
                while i<len(route)-1:
                    j=len(route)-1
                    while j>i+1 and not self.clear(route[i],route[j],r,ends):j-=1
                    simplified.append(route[j]);i=j
                return simplified
            for delta,length in offsets:
                other=tuple(k[i]+delta[i] for i in range(3));q=coord(other)
                if np.any(q<low) or np.any(q>high):continue
                new=cost+length
                if new>=costs.get(other,float('inf')):continue
                if not self.clear(p,q,r,ends):continue
                costs[other]=new;parents[other]=k
                heapq.heappush(queue,(new+1.22*float(np.linalg.norm(q-goal)),new,other))
        return None


def portal_assignments(rows,terms,passages):
    groups={'a':[],'b':[],'sensor':[]}
    for r in rows:
        if not terms[r['end']]['part'].startswith('cold-core/') or terms[r['start']]['part'].startswith('cold-core/'):continue
        bank=('a' if r['end'].startswith('reed-a-') else
              'b' if r['end'].startswith('reed-b-') else 'sensor')
        groups[bank].append(r['id'])
    ports={}
    for bank,ids in groups.items():
        name='sensor-cable' if bank=='sensor' else 'reed-cable-'+bank
        axis=np.array(passages[name]['points_mm'])
        # Five reed conductors share each reservoir passage. The internal
        # loom has its 3 mm earth core centrally and six 1.7 mm sensor cores
        # around it, all inside the shared 7.5 mm bore.
        ids.sort(key=lambda id:(0 if id=='PE-carbonator' else 1,id))
        for i,id in enumerate(ids):
            if id=='PE-carbonator':offset=np.zeros(3)
            else:
                count=len(ids)-(1 if bank=='sensor' else 0)
                angle=math.tau*(i-(1 if bank=='sensor' else 0))/count
                radius=2.55 if bank=='sensor' else 1.65
                offset=np.array([radius*math.cos(angle),radius*math.sin(angle),0.])
            ports[id]=[tuple(p+offset) for p in axis]
    return ports


def main():
    sys.path.insert(0,str(ROOT/'hardware/scripts'))
    import _cadq_export  # Shares the workstation's one-heavy-CAD-job queue.
    manifest=json.loads((ROOT/'hardware/wiring/enclosure-wiring.json').read_text())
    terms=manifest['terminals'];rows=manifest['routes']
    # Refresh graph edits while retaining resolved terminal coordinates.
    from hardware.wiring.installed.connections import connections
    rows=[vars(c) for c in connections()]
    meshes={n:m for n,m in load_mesh(str(ROOT/'hardware/manifold-layout/enclosure-assembly.step.mesh')).items()
            if not n.startswith(('wire-','wiring-'))}
    nav=Navigator(meshes,terms,manifest.get('terminations'));portals=portal_assignments(rows,terms,manifest['cable_passages'])
    overrides={}
    if '--retry' in sys.argv:
        overrides=json.loads(OUT.read_text())
        routed_ids={id for id,v in overrides.items() if 'stations' in v}
        for r in manifest['routes']:
            if r['id'] in routed_ids:nav.reserve(r,r['points_mm'],STOCK[r['stock']]['od_mm']/2)
        rows=[r for r in rows if r['id'] not in routed_ids]
    # Conduit conductors go first; their passages are the most constrained.
    # Conductors and tubing do not obstruct another conductor.
    rows.sort(key=lambda r:(0 if r['id'] in portals else 1,
                            -STOCK[r['stock']]['od_mm'],r['harness'],r['id']))
    failed=[];began=time.time()
    for number,row in enumerate(rows,1):
        ends=[terms[row[k]] for k in ('start','end')];p,q=[np.array(t['point']) for t in ends]
        radius=STOCK[row['stock']]['od_mm']/2
        nav.actual_radius=radius
        # Tight attachment lands and the two cap bores use the actual wire OD.
        def escape(t):
            a=np.array(t['point']);d=np.array(t['outward'])
            for length in (6.,4.,2.,1.):
                b=a+d*length
                if nav.clear(a,b,radius+.08,ends):return b
            return None
        start,goal=map(escape,ends)
        if start is None or goal is None:
            failed.append({'id':row['id'],'reason':'attachment exit obstructed'});print('FAIL exit',row['id'],flush=True);continue
        stations=[start,*portals.get(row['id'],[]),goal]
        points=[tuple(p)];ok=True
        for a,b in zip(stations,stations[1:]):
            # Straight conduit segments retain their assigned packing lane.
            conduit=(row['id'] in portals and tuple(a)==tuple(portals[row['id']][0])
                     and tuple(b)==tuple(portals[row['id']][1]))
            if conduit:
                path=[tuple(a),tuple(b)] if nav.clear(a,b,radius+.08,ends) else None
            else:
                path=nav.path(a,b,radius+.6,ends)
                if path is None:path=nav.path(a,b,radius+.12,ends,step=2.,limit=15000,
                                            grid_origin=b)
            if path is None:
                failed.append({'id':row['id'],'reason':'no route in search domain','from':list(a),'to':list(b)})
                ok=False;break
            points.extend(path)
        if not ok:print('FAIL path',row['id'],flush=True);continue
        points.append(tuple(q))
        # The common builder adds the same relaxed end lands. Save only the
        # internal stations, relative to this wire's native source attachment.
        specs=[]
        for pt in points[2:-2]:
            anchor=min(ends,key=lambda t:np.linalg.norm(np.array(pt)-t['point']))
            if row['id'] in portals and any(np.linalg.norm(np.array(pt)-port)<.01 for port in portals[row['id']]):
                bank='b' if row['end'].startswith('reed-b-') else 'a'
                if row['end'].startswith(('reed-a-','reed-b-')):
                    anchor=terms[f'reed-{bank}-4.signal']
            specs.append({'terminal':anchor['id'],'offset':[round(float(x-y),4) for x,y in zip(pt,anchor['point'])]})
        overrides[row['id']]={'stations':specs,'bend_radius_mm':2. if radius<1.4 else 3.,
                              'end_lands_mm':[float(np.linalg.norm(start-p)),float(np.linalg.norm(goal-q))],
                              'preserve_stations':True,
                              'note':'Proposed installed route searched against current larger bodies; physical dressing remains open.'}
        # Wire-to-wire packing is outside this route search.
        print(f'{number}/{len(rows)} {row["id"]}: {len(points)} stations ({time.time()-began:.1f}s)',flush=True)
        OUT.write_text(json.dumps(overrides,indent=2)+'\n')
        (TMP/'search-failures.json').write_text(json.dumps(failed,indent=2)+'\n')
    for failure in failed:
        overrides[failure['id']]={'route_status':'unresolved',
                                 'note':'Manual route review required: '+failure['reason']+'. A bounded search failure is not proof that the physical route is impossible.'}
    OUT.write_text(json.dumps(overrides,indent=2)+'\n')
    (TMP/'search-failures.json').write_text(json.dumps(failed,indent=2)+'\n')
    print(json.dumps({'routed':len(overrides)-len(failed),'failed':failed,'seconds':time.time()-began}),flush=True)


if __name__=='__main__':main()
