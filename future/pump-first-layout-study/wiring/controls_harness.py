"""Low-voltage routing guide using retained native geometry and exact arcs.

The nominal wire exterior is1.7mm. The guide also treats individual junction
lever operation as occupied space and preserves the fixed forward cartridge.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys
import numpy as np
import cadquery as cq
from OCP.Standard import Standard_Failure
HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
from native_harness import Guide,occupied_points,bounds,broad
import audit,baseline

def control_occupied_points(name,shape,cache):
    # Small-edge fillets make OCC's relative tessellation create millions of
    # irrelevant triangles. Absolute0.3mm meshing supplies
    # only the ranking raster; all admitted looms still face the full native
    # occupied solid, including those fillets and every accepted bore.
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.BRep import BRep_Tool
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopAbs import TopAbs_REVERSED
    from native_harness import PITCH
    import trimesh
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
        mesh=trimesh.Trimesh(vertices=vertices,faces=triangles,process=True)
        chunks.append(mesh.voxelized(PITCH).fill().points)
    points=np.unique(np.vstack(chunks),axis=0) if chunks else np.zeros((0,3))
    path.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(path,points=points)
    print('wire guide absolute ranking',name,len(points),flush=True)
    return points

def passed_body_models():
    """Keep current purchased-body restraints occupied before strict composition."""
    models={};records={}
    for filename in ['needle-candidate.json','wr-candidate.json','check-tee-candidate.json']:
        path=STUDY/'mounts'/filename
        if not path.exists():continue
        module=json.loads(path.read_text())
        if not module.get('pass') and filename!='check-tee-candidate.json':continue
        for name,record in module.get('parts',{}).items():
            records[name]=record;models[name]=cq.Shape.importBrep(str(ROOT/record['brep']))
    return models,records

def lower_lead_models():
    """Independent, native-proved lower power exits remain rigid obstacles."""
    path=HERE/'lower-lead-exits.json'
    if not path.exists():return {},{}
    module=json.loads(path.read_text())
    records=module.get('parts',{})
    return {name:cq.Shape.importBrep(str(ROOT/record['brep'])) for name,record in records.items()},records

def required_power_departures():
    """Preserve the three selected DC-return normal/upward working exits."""
    from native_harness import sweep
    path=HERE/'power-candidate.json'
    if not path.exists():return {},{}
    ports=json.loads(path.read_text()).get('ports',{});models={};records={}
    folder=ROOT/'.cache/pump-first-layout/wiring/required-power-departures';folder.mkdir(parents=True,exist_ok=True)
    for index in [1,2,3]:
        p=ports.get('wago-gnd:'+str(index))
        if not p:continue
        x,y,z=p['point'];points=[p['point'],[x,y-5.4,z],[x,y-5.4,347.9]]
        shape,record=sweep(points,3.2,3.4)
        stream=BytesIO();shape.exportBrep(stream);digest=hashlib.sha256(stream.getvalue()).hexdigest()
        brep=folder/(digest+'.brep')
        if not brep.exists():shape.exportBrep(str(brep))
        name='required-return-departure-wago-gnd-'+str(index)
        models[name]=shape;records[name]={'brep':str(brep.relative_to(ROOT)),'points_mm':points,
            'diameter_mm':3.2,'radius_mm':3.4,'scope':'Selected native normal5.4mm and upward DC-return departure; parent power module owns the complete conductor.'}
    return models,records

def strict_fluid_air_models(models,records):
    """Occupied fluid exteriors enlarged by the required one-millimetre air."""
    from OCP.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
    from OCP.GeomAbs import GeomAbs_Arc
    revised={};revised_records={}
    folder=ROOT/'.cache/pump-first-layout/wiring/fluid-air-obstacles'
    folder.mkdir(parents=True,exist_ok=True)
    for name,shape in models.items():
        if not name.startswith(('tube-water-','tube-fluid-','tube-carb-','tube-co2-','carb-foam-')):continue
        if name.startswith('carb-foam-'):
            # Fill the already occupied inner tube before enlarging the sleeve;
            # an inward offset of the thin annular bore is unnecessary here.
            tube=models.get('tube-'+name.removeprefix('carb-foam-'))
            if tube is None:raise ValueError('Missing occupied inner tube for '+name)
            shape=shape.fuse(tube,tol=.0001)
        stream=BytesIO();shape.exportBrep(stream);source_hash=hashlib.sha256(stream.getvalue()).hexdigest()
        path=folder/(source_hash+'-air1.brep')
        if path.exists():grown=cq.Shape.importBrep(str(path))
        else:
            if name.startswith('carb-foam-'):
                tube_name='tube-'+name.removeprefix('carb-foam-')
                route=records.get(tube_name,{}).get('route')
                if route is None:route=json.loads((STUDY/'routing/candidate.json').read_text())['parts'][tube_name]['route']
                wire=cq.Shape.importBrep(str(ROOT/route['centreline_brep']));edges=wire.Edges()
                start,end=edges[0].startPoint(),edges[-1].endPoint()
                tangent_start,tangent_end=edges[0].tangentAt(0),edges[-1].tangentAt(1)
                source_full=cq.Solid.sweep(cq.Wire.makeCircle(12.7,start,tangent_start),[],wire,makeSolid=True,isFrenet=False)
                mismatch=abs(shape.cut(source_full,tol=.0001).Volume(tol=1e-9))+abs(source_full.cut(shape,tol=.0001).Volume(tol=1e-9))
                if mismatch>.001:raise ValueError(f'{name}: source centreline differs from complete sleeve by{mismatch:g}mm³')
                grown=cq.Solid.sweep(cq.Wire.makeCircle(13.7,start,tangent_start),[],wire,makeSolid=True,isFrenet=False)
                # Complete one-millimetre axial air at the native end faces.
                grown=grown.fuse(cq.Solid.makeCylinder(13.7,1.,start,-tangent_start),cq.Solid.makeCylinder(13.7,1.,end,tangent_end),tol=.0001)
            else:
                offset=BRepOffsetAPI_MakeOffsetShape()
                offset.PerformByJoin(shape.wrapped,1.,.0001,Join=GeomAbs_Arc)
                grown=cq.Shape.cast(offset.Shape())
                if (not grown.isValid() or not grown.Solids()) and name in ['tube-fluid-16','tube-fluid-26']:
                    # These retained STEP sweeps do not admit an OCC offset.
                    # Their production recipe supplies a guide-only enlarged
                    # sweep; final running air still uses the received solid.
                    from dataclasses import replace
                    sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),str(ROOT/'hardware/scripts')]
                    import _lines as lines,_routing as routing
                    dummy=cq.Solid.makeBox(1,1,1)
                    frames={'foam-assembly':routing.frame('foam-assembly',dummy,{
                        'reservoir-a':((43.5,188.9,253.4000001),(0,0,1),6.35),
                        'reservoir-b':((-43.5,188.9,253.4000001),(0,0,1),6.35)})}
                    for valve,x in [('valve-v-e',22.35),('valve-v-h',-22.35)]:
                        frames[valve]=routing.frame(valve,dummy,{'inlet':((x,105.29,282.175),(0,0,1),6.35)})
                    run=(lines._fluid_16 if name=='tube-fluid-16' else lines._fluid_26)(frames)
                    received_volume=shape.Volume(tol=1e-9);recipe=routing.tube(run)
                    if abs(recipe.Volume(tol=1e-9)-received_volume)>.001:raise ValueError('Retained guide recipe volume differs for '+name)
                    grown=routing.tube(replace(run,diam=8.35))
            if not grown.isValid() or not grown.Solids():raise ValueError('Invalid full-fluid air obstacle: '+name)
            missing=abs(shape.cut(grown,tol=.0001).Volume(tol=1e-9))
            if missing>.001:raise ValueError(f'{name}: fluid air obstacle lost{missing:g}mm³')
            grown.exportBrep(str(path))
        revised[name]=grown
        revised_records[name]={**records.get(name,{}),'brep':str(path.relative_to(ROOT)),
            'source_native_sha256':source_hash,'radial_air_mm':1.,
            'scope':'Guide obstacle is the full native tube, braided hose or foam exterior enlarged1mm. Complete controls are independently checked against the physical exterior.'}
    return revised,revised_records

class ControlsGuide(Guide):
    def __init__(self,ports,diameter=1.7,hardware_only=False):
        self.wire_diameters={};self.used_port_labels=set();self.ports=ports;self.diameter=diameter;self.scope=[-102.65,84.015,241.5,102.65,465.3,350.15]
        base=[np.arange(self.scope[i],self.scope[i+3]+.01,4.2) for i in range(3)]
        important=[[float(p['point'][i]) for p in ports] for i in range(3)]
        for p in ports:
            for length in [5.4,6.8,8.4,12.6,16.8]:
                q=np.asarray(p['point'])+np.asarray(p['axis'])*length
                for i in range(3):important[i].append(float(q[i]))
            for lead in p.get('lead_paths',[]):
                for q in lead:
                    for i in range(3):important[i].append(float(q[i]))
        important[2]+=[243.6,245.3,247,248.7,250.4,255.5,260,282.5,285.4,325,328,329.15,335.75,339.95,344.15,348.3,348.35,350]
        important[0]+=[-18,-24,55.5,59.5,62,92.925,94.625,96.325]
        self.axes=[np.unique(np.round(np.r_[base[i],important[i]],6)) for i in range(3)]
        self.axes=[a[(a>=self.scope[i])&(a<=self.scope[i+3])] for i,a in enumerate(self.axes)]
        self.dims=tuple(len(a) for a in self.axes);grids=np.meshgrid(*self.axes,indexing='ij');self.grid=np.stack(grids,axis=-1);self.points=self.grid.reshape(-1,3)
        self.models,self.records,_,_,_=audit.collect()
        body_models,body_records=passed_body_models()
        self.models.update(body_models);self.records.update(body_records)
        lower_models,lower_records=lower_lead_models()
        self.models.update(lower_models);self.records.update(lower_records)
        return_models,return_records=required_power_departures()
        self.models.update(return_models);self.records.update(return_records)
        routing=json.loads((STUDY/'routing/candidate.json').read_text())
        for suffix,field in [('receiver','new_receiver'),('backing','new_backing')]:
            record=routing.get('interface_moves',{}).get('nameplate',{}).get(field)
            if record:
                name='protected-nameplate-'+suffix
                self.records[name]=record
                self.models[name]=cq.Shape.importBrep(str(ROOT/record['brep']))
        # Native forward boundaries are deliberately retained and are obstacles.
        saved=baseline.prepare()
        for name,r in saved['parts'].items():
            if name in self.records or not broad(r['bounds'],self.scope,3):continue
            path=baseline.CACHE/r['file'];self.records[name]={'brep':str(path.relative_to(ROOT))};self.models[name]=cq.Shape.importBrep(str(path))
        roof=json.loads((STUDY/'mounts/candidate.json').read_text())
        for name,working in roof['working_envelopes'].items():
            if 'levers' not in working:continue
            r=working['levers'];key=name+'-lever-working-space';self.records[key]=r;self.models[key]=cq.Shape.importBrep(str(ROOT/r['brep']))
        power=STUDY/'wiring/power-candidate.json'
        if power.exists() and not hardware_only:
            for name,r in json.loads(power.read_text()).get('parts',{}).items():
                self.records[name]=r;self.models[name]=cq.Shape.importBrep(str(ROOT/r['brep']))
        # These independently published exits supersede an older partial
        # power result at the same logical part names.
        self.models.update(lower_models);self.records.update(lower_records)
        self.physical_fluids={name:shape for name,shape in self.models.items()
            if name.startswith(('tube-water-','tube-fluid-','tube-carb-','tube-co2-','carb-foam-'))}
        physical_records=dict(self.records);physical_native_inputs={}
        # Import each consumed source from the exact bytes whose digest is
        # recorded, before crop/growth or ranking meshing alters its view.
        for name,r in physical_records.items():
            if name.startswith(('control-','power-')) or name=='rear-roof-hatch' or not r or not r.get('brep'):continue
            raw=(ROOT/r['brep']).read_bytes()
            self.models[name]=cq.Shape.importBrep(BytesIO(raw))
            physical_native_inputs[name]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
        self.physical_fluids={name:shape for name,shape in self.models.items()
            if name.startswith(('tube-water-','tube-fluid-','tube-carb-','tube-co2-','carb-foam-'))}
        fluid_models,fluid_records=strict_fluid_air_models(self.models,self.records)
        self.models.update(fluid_models);self.records.update(fluid_records)
        chunks=[];self.obstacles={}
        for name,shape in self.models.items():
            if name.startswith(('control-','power-')):continue
            if name=='rear-roof-hatch':continue
            if hardware_only and name not in lower_models and (name.startswith('wire-') or name in ['compressor-jacket-reserve','lower-carbonator-earth-reserve','lower-under-counter-earth-reserve']):continue
            if name.startswith(('enclosure-back-top','enclosure-front-top')):
                # The forward shell/cartridge interfaces remain as received.
                # Only the rearranged aft bay admits emitted wiring recesses.
                shape=shape.intersect(cq.Solid.makeBox(240,241.685,130,cq.Vector(-120,84.015,240)))
                if not shape.Solids():continue
            if not broad(bounds(shape),self.scope,diameter+2):continue
            points=control_occupied_points(name,shape,self.records[name].get('brep'))
            keep=np.all((points>=np.asarray(self.scope[:3])-5)&(points<=np.asarray(self.scope[3:])+5),axis=1)
            chunks.append(points[keep]);self.obstacles[name]=shape
        self.native_inputs={name:physical_native_inputs[name] for name in self.obstacles if name in physical_native_inputs}
        self.voxels=np.vstack(chunks);self.wires={};self.refresh()

    def refresh(self):
        # Different counted looms retain their actual exterior in the ranking
        # guide, followed by the complete native collision proof.
        from scipy.spatial import cKDTree
        saved=getattr(self,'wires',{})
        key=(id(self.voxels),len(self.voxels),self.dims)
        if getattr(self,'_hardware_rank_key',None)!=key:
            self.tree=cKDTree(self.voxels)
            self._hardware_rank_distances=self.tree.query(self.points,workers=-1)[0].astype(np.float32)
            self._hardware_rank_key=key
        self.free=(self._hardware_rank_distances>=self.diameter/2+.2).reshape(self.dims)
        # Every admitted aft-wall/roof recess includes1mm running room and
        # leaves the established3mm outer skin, for this loom's actual radius.
        radius=self.diameter/2
        stock=(abs(self.points[:,0])<=103.5-radius+1e-6)&(self.points[:,2]<=351-radius+1e-6)
        self.free&=stock.reshape(self.dims)
        centres=getattr(self,'wire_centers',{})
        if not hasattr(self,'_wire_rank_distances'):self._wire_rank_distances={}
        for name,points in centres.items():
            if name not in saved:continue
            clearance=(self.diameter+self.wire_diameters.get(name,self.diameter))/2+.15
            cached=self._wire_rank_distances.get(name)
            if cached is None or cached[0]!=id(points):
                cached=(id(points),cKDTree(points).query(self.points,workers=-1)[0].astype(np.float32))
                self._wire_rank_distances[name]=cached
            distances=cached[1]
            self.free&=(distances>=clearance).reshape(self.dims)
        print('control wire grid',self.dims,'free',int(self.free.sum()),flush=True)

    def route(self,a,b,name):
        # Conductors inside one factory loom may be closer than the generic
        # independent-terminal margin. Their exact separate exteriors are still
        # tested after sweep, including the accepted8-wire bore packing.
        original=self.ports
        ends=[a,b]
        self.ports=[p for p in original if p in ends or not any(
            p.get('owner')==e.get('owner') and
            np.linalg.norm(np.asarray(p['point'])-np.asarray(e['point']))<2.06 and
            np.linalg.norm(np.asarray(p['axis'])-np.asarray(e['axis']))<1e-6
            for e in ends)]
        import native_harness as native
        original_radius,original_sweep,original_bounds=native.RADIUS,native.sweep,native.bounds
        used_before=set(self.used_port_labels);completed=False
        route_radius=getattr(self,'bend_radius',original_radius)
        self._native_dock_admission=False;self._dock_corridor_cache={}
        native.RADIUS=route_radius
        def grouped_sweep(points,diameter,radius=None,with_centerline=False):
            return original_sweep(points,diameter,route_radius if radius is None else radius,with_centerline)
        native.sweep=grouped_sweep
        from controls_looms import model_metadata
        native.bounds=lambda shape:model_metadata(shape)[0]
        try:
            result=self._control_route(a,b,name);self.wire_diameters[name]=self.diameter;completed=True;return result
        finally:
            self.ports=original;native.RADIUS=original_radius;native.sweep=original_sweep;native.bounds=original_bounds
            if not completed:self.used_port_labels=used_before

    def lead_options(self,port):
        options=super().lead_options(port)
        if not self._native_dock_admission:return options
        from native_harness import sweep
        from controls_looms import native_hits
        models={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
        admitted=0
        for ix,last,_,lead in options:
            p=self.grid[ix]
            for direction in range(6):
                if last<6 and direction==(last^1):continue
                key=(port['label'],ix,direction)
                cached=self._dock_corridor_cache.get(key)
                if cached is None:
                    axis=direction//2;sign=1 if direction%2==0 else -1
                    target=list(ix);distance=0.;indices=[]
                    need=.01 if direction==last else 2*self.bend_radius+.05
                    while distance<need:
                        target[axis]+=sign
                        if target[axis]<0 or target[axis]>=self.dims[axis]:break
                        q=tuple(target);indices.append(q)
                        distance=abs(self.axes[axis][target[axis]]-p[axis])
                    clear=False
                    if distance>=need:
                        q=self.grid[tuple(target)]
                        try:
                            shape,_=sweep(lead+[q.tolist()],self.diameter,self.bend_radius)
                            box=bounds(shape)
                            stock=box[0]>=-103.5 and box[3]<=103.5 and box[2]>=241.5 and box[5]<=351
                            clear=stock and not native_hits(shape,models,[port.get('owner')])
                        except (ValueError,Standard_Failure):pass
                    cached=(clear,indices);self._dock_corridor_cache[key]=cached
                if cached[0]:
                    for q in cached[1]:self.free[q]=True
                    admitted+=1
        print('native dock corridors',port['label'],admitted,flush=True)
        return options

    def _control_route(self,a,b,name):
        """Exclude native collision neighbourhoods before another guide search."""
        from native_harness import NativeCollision
        from circular_clearance import paired_members,CircularSelfIntersection
        from controls_looms import native_hits
        initial=self.free.copy()
        used_entry=set(self.used_port_labels)
        try:
            for attempt in range(12):
                try:
                    shape,record=self._route_once(a,b,name)
                    try:
                        physical,_,section=paired_members(shape,self.diameter,gap=0.,fuse_clearance=False)
                    except CircularSelfIntersection as error:
                        self.wires.pop(name,None);getattr(self,'wire_centers',{}).pop(name,None);self.used_port_labels=set(used_entry)
                        box=bounds(error.overlap);pad=self.diameter/2+1.5+attempt*.35
                        blocked=np.all((self.points>=np.asarray(box[:3])-pad)&(self.points<=np.asarray(box[3:])+pad),axis=1)
                        self.free&=(~blocked).reshape(self.dims)
                        print('control self-section retry',name,error.indices,error.volume,flush=True)
                        continue
                    self.wires.pop(name,None)
                    members_hits=native_hits(physical,{**self.obstacles,**self.wires,**getattr(self,'_active_future',{})},[a.get('owner'),b.get('owner')])
                    if members_hits:
                        getattr(self,'wire_centers',{}).pop(name,None)
                        raise NativeCollision(name,physical,members_hits)
                    shape=physical
                    self.wires[name]=shape
                    record['physical_section_proof']={key:section[key] for key in ['members','complete_length_mm','received_section_volume_mm3','member_section_volume_mm3','tangent_full_section_seams','open_end_centres_mm','physical_member_self_checks']}
                    record['physical_section_proof']['scope']='Exact analytic member surfaces and full tangent section seams form one continuous exterior with zero native common between distinct physical members.'
                    record['physical_member_native_interferences']=[]
                    failures=[];box=bounds(shape)
                    for part,fluid in self.physical_fluids.items():
                        if not broad(box,bounds(fluid),1.):continue
                        gap=shape.distance(fluid)
                        if gap<1.-1e-6:failures.append({'part':part,'air_mm':gap})
                    if failures:
                        self.wires.pop(name,None)
                        getattr(self,'wire_centers',{}).pop(name,None)
                        authored=__import__('native_harness').sweep(record['points_mm'],self.diameter,getattr(self,'bend_radius',3.4))[0]
                        _,grown,_=paired_members(authored,self.diameter,gap=1.,fuse_clearance=False)
                        raise NativeCollision(name,grown,failures)
                    record['full_fluid_air_pass']=True
                    record['minimum_unrelated_fluid_air_mm']=1.
                    return shape,record
                except NativeCollision as error:
                    self.used_port_labels=set(used_entry)
                    obstacles={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
                    for hit in error.hits:
                        # The exact members also supply the exclusion bounds.
                        # A whole-pipe common can be ambiguous even when every
                        # received cylinder/arc has a valid occupied section.
                        pieces=[]
                        for member in error.shape.Solids():
                            for solid in obstacles[hit['part']].Solids():
                                if not broad(bounds(member),bounds(solid),.0001):continue
                                common=member.intersect(solid,tol=.0001)
                                if abs(common.Volume(tol=1e-9))>1e-9:pieces.append(common)
                        if not pieces:raise ValueError('Native collision has no exact physical-member neighbourhood: '+str(hit))
                        overlap=cq.Compound.makeCompound(pieces)
                        box=bounds(overlap)
                        # A small collision between grid stations must remove
                        # an adjacent run or corner, rather than only an empty
                        # sub-grid box. This remains a search exclusion; each
                        # replacement candidate faces the full native solids.
                        pad=self.diameter/2+1.5+attempt*.35
                        blocked=np.all((self.points>=np.asarray(box[:3])-pad)&(self.points<=np.asarray(box[3:])+pad),axis=1)
                        self.free&=(~blocked).reshape(self.dims)
                    print('control native retry',name,attempt+1,error.hits,flush=True)
                except ValueError as error:
                    if self._native_dock_admission or 'no guide route after' not in str(error):raise
                    # A filled ranking raster may hide a genuinely clear
                    # endpoint turn. Admit only complete analytic departures
                    # checked against the current native obstacles and future
                    # endpoints; the full resulting loom is checked again.
                    self._native_dock_admission=True
                    print('control native dock repair',name,str(error),flush=True)
            raise ValueError(f'{name}: twelve guide candidates failed exact native clearance')
        finally:self.free=initial
