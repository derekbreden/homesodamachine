"""Power guide admission using complete independent circular members."""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys
import numpy as np
import cadquery as cq
import audit
from native_harness import Guide,NativeCollision,bounds,broad
from circular_clearance import paired_members,CircularSelfIntersection
from recover_power import analytic_sections

def terminal_approach_members(physical,a,b,diameter):
    """Identify only received straight members normal to a terminal mouth."""
    owners={};witnesses=[]
    for label,port in [('from',a),('to',b)]:
        matches=[];point=cq.Vector(*port['point']);axis=cq.Vector(*port['axis']).normalized()
        for index,member in enumerate(physical.Solids()):
            sections=analytic_sections(member,diameter)
            if len(sections)!=1 or sections[0]['kind']!='CYLINDER':continue
            section=sections[0]
            for start,end in [(section['a'],section['b']),(section['b'],section['a'])]:
                if (start-point).Length>=1e-6:continue
                normal=(end-start).normalized();dot=normal.dot(axis)
                if dot>=1.-1e-8:
                    matches.append(index);witnesses.append({'endpoint':label,'owner':port['owner'],
                        'member':index,'mouth_mm':list(start.toTuple()),'normal_axis_dot':dot,
                        'normal_straight_length_mm':(end-start).Length,'diameter_mm':diameter,'pass':True})
        if len(matches)!=1:raise ValueError('Conductor lacks one actual normal terminal approach: '+port['label'])
        owners.setdefault(port['owner'],set()).update(matches)
    return owners,witnesses

def received_fluid_models(obstacles,records,native_inputs):
    """Received circle sections and complete chilled sleeve envelopes."""
    root=Path(__file__).resolve().parents[3];study=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(study/'routing'))
    from fluid_members import circular_parity,sealed_sleeve_parity
    source_binding={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in [Path(__file__),study/'routing/fluid_members.py',study/'wiring/circular_clearance.py']}
    cache=root/'.cache/pump-first-layout/wiring/received-fluid-members';cache.mkdir(parents=True,exist_ok=True)
    models={};proofs={}
    for name,shape in list(obstacles.items()):
        if not name.startswith(('carb-foam-','tube-fluid-','tube-water-','tube-co2-','tube-carb-')):continue
        input_binding={name:native_inputs[name]['sha256']}if name in native_inputs else None
        if name.startswith('carb-foam-'):
            route=name.removeprefix('carb-foam-');tube='tube-'+route
            path=root/records[tube]['route']['centreline_brep']
            raw=path.read_bytes();edges=cq.Shape.importBrep(BytesIO(raw)).Edges()
            native_inputs['fluid-centreline-'+route]={'brep':str(path.relative_to(root)),
                'sha256':hashlib.sha256(raw).hexdigest()}
            if input_binding is not None:
                input_binding.update({tube:native_inputs[tube]['sha256'],
                    'fluid-centreline-'+route:hashlib.sha256(raw).hexdigest()})
        key=hashlib.sha256(json.dumps({'inputs':input_binding,'sources':source_binding},sort_keys=True).encode()).hexdigest()
        saved=cache/(key+'.json');native_path=cache/(key+'.brep')
        if input_binding is not None and saved.exists() and native_path.exists():
            receipt=json.loads(saved.read_bytes());raw=native_path.read_bytes()
            if receipt['native_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('Changed cached fluid member receipt '+name)
            physical=cq.Shape.importBrep(BytesIO(raw));proof=receipt['proof']
            if receipt['inputs']!=input_binding or receipt['sources']!=source_binding or not proof['pass'] or not physical.isValid():
                raise ValueError('Cached fluid section receipt differs '+name)
        else:
            if name.startswith('carb-foam-'):physical,proof=sealed_sleeve_parity(obstacles[tube],shape,edges)
            else:physical,proof=circular_parity(shape,15.1 if name in ['tube-water-6','tube-water-7']else 6.35)
            if input_binding is not None:
                physical.exportBrep(str(native_path))
                saved.write_text(json.dumps({'inputs':input_binding,'sources':source_binding,
                    'native_sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),'proof':proof},indent=2)+'\n')
        if not proof['pass']:raise ValueError('Received fluid section parity failed '+name)
        if input_binding is not None:
            proof={**proof,'received_member_cache':{'input_sha256':input_binding,'source_sha256':source_binding,
                'brep':str(native_path.relative_to(root)),'sha256':hashlib.sha256(native_path.read_bytes()).hexdigest(),
                'scope':'Immutable received-input and reconstruction-source binding; the saved native members retain the independently checked lateral-face correspondence and complete section proof.'}}
            native_inputs['received-fluid-members-'+name]={'brep':str(native_path.relative_to(root)),
                'sha256':proof['received_member_cache']['sha256']}
        models[name]=physical;proofs[name]=proof
    return models,proofs

class PowerGuide(Guide):
    def fluid_models(self):
        if hasattr(self,'physical_fluid_models'):return self.physical_fluid_models
        models,proofs=received_fluid_models(self.obstacles,self.records,self.native_inputs)
        self.physical_fluid_models=models;self.fluid_section_proofs=proofs
        self.obstacles.update(models)
        return models

    def route(self,a,b,name):
        fluids=self.fluid_models()
        initial=self.free.copy();used_entry=set(self.used_port_labels)
        self._native_power_dock_admission=False;self._power_dock_corridors={}
        def rollback():
            self.wires.pop(name,None);getattr(self,'wire_centers',{}).pop(name,None)
            self.used_port_labels=set(used_entry)
        def exclude(shape,attempt):
            box=bounds(shape);pad=self.diameter/2+1.5+attempt*.35
            blocked=np.all((self.points>=np.asarray(box[:3])-pad)&(self.points<=np.asarray(box[3:])+pad),axis=1)
            self.free&=(~blocked).reshape(self.dims)
        try:
            for attempt in range(14):
                try:
                    shape,record=self._route_once(a,b,name)
                    try:physical,_,proof=paired_members(shape,self.diameter,gap=0.,fuse_clearance=False)
                    except CircularSelfIntersection as error:
                        rollback();exclude(error.overlap,attempt)
                        print('power self-section retry',name,error.indices,error.volume,flush=True)
                        continue
                    self.wires.pop(name,None)
                    models={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
                    owners,terminal_witnesses=terminal_approach_members(physical,a,b,self.diameter)
                    hits=[];physical_members=physical.Solids()
                    for part,obstacle in models.items():
                        if not broad(bounds(physical),bounds(obstacle)):continue
                        exempt=owners.get(part,set());tested=[s for i,s in enumerate(physical_members)if i not in exempt]
                        occupied=cq.Compound.makeCompound(tested)
                        overlap=audit.common(occupied,obstacle)
                        if overlap>.001:hits.append({'part':part,'overlap_mm3':overlap,'ignore_member_indices':sorted(exempt)})
                    if hits:
                        rollback();raise NativeCollision(name,physical,hits)
                    air_failures=[]
                    for part,fluid in fluids.items():
                        if not broad(bounds(physical),bounds(fluid),1.):continue
                        from fluid_members import closest_members
                        gap,_,_,_=closest_members(physical,fluid)
                        if gap<1.-1e-6:air_failures.append({'part':part,'air_mm':gap})
                    if air_failures:
                        rollback()
                        _,grown,_=paired_members(shape,self.diameter,gap=1.,fuse_clearance=False)
                        raise NativeCollision(name,grown,air_failures)
                    self.wires[name]=physical
                    record['physical_section_proof']={key:proof[key]for key in [
                        'members','complete_length_mm','received_section_volume_mm3','member_section_volume_mm3',
                        'tangent_full_section_seams','open_end_centres_mm','physical_member_self_checks']}
                    record['physical_member_native_interferences']=[]
                    record['terminal_approach_members']=terminal_witnesses
                    record['full_fluid_air_pass']=True
                    record['minimum_unrelated_fluid_air_mm']=1.
                    return physical,record
                except NativeCollision as error:
                    rollback();models={**self.obstacles,**self.wires,**getattr(self,'_active_future',{})}
                    for hit in error.hits:
                        pieces=[]
                        for index,member in enumerate(error.shape.Solids()):
                            if index in hit.get('ignore_member_indices',[]):continue
                            for solid in models[hit['part']].Solids():
                                if not broad(bounds(member),bounds(solid),.0001):continue
                                overlap=member.intersect(solid,tol=.0001)
                                if abs(overlap.Volume(tol=1e-9))>1e-9:pieces.append(overlap)
                        if not pieces:raise ValueError('Exact power-member collision has no native exclusion volume: '+str(hit))
                        exclude(cq.Compound.makeCompound(pieces),attempt)
                    print('power native-member retry',name,attempt+1,error.hits,flush=True)
                except ValueError as error:
                    if self._native_power_dock_admission or 'no guide route after' not in str(error):raise
                    self._native_power_dock_admission=True
                    print('power native dock repair',name,str(error),flush=True)
            rollback();raise ValueError(f'{name}: fourteen guide candidates failed independent native member admission')
        finally:self.free=initial;self._native_power_dock_admission=False
