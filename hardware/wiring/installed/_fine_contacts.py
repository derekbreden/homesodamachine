"""Manual contact queries on explicit physical and installed-wiring fine models."""
from __future__ import annotations

from functools import cache
import hashlib
import json
from pathlib import Path

from .review import base_name, fine_review, wire_obstacle

ROOT=Path(__file__).resolve().parents[3]


def groups(rows):
    result={}
    for index,row in enumerate(rows):
        name=base_name(row['name'])
        group=result.setdefault(name,{'indices':[],'min':row['min'][:],
                                      'max':row['max'][:],'volume':0.})
        group['indices'].append(index)
        group['min']=[min(a,b)for a,b in zip(group['min'],row['min'])]
        group['max']=[max(a,b)for a,b in zip(group['max'],row['max'])]
        group['volume']+=row['volume']
    return result


def neighborhoods(manifest,name,target):
    """The existing named endpoint and fuse-stub cells, without device exclusions."""
    routes={'wire-'+row['id']:row for row in manifest['routes']}
    terminations=manifest['terminations'];leaf=name.rsplit('/',1)[-1]
    other=target.rsplit('/',1)[-1];info=terminations.get(leaf,{})
    terminal_ids=([routes[leaf][key]for key in ('start','end')]
                  if leaf in routes else info.get('terminal_ids',[]))
    other_ids=terminations.get(other,{}).get('terminal_ids',[])
    result=[]
    for id in terminal_ids:
        terminal=manifest['terminals'].get(id)
        if terminal is not None and (terminal['part'].rsplit('/',1)[-1]==other or id in other_ids):
            result.append({'center_mm':terminal['point'],'radius_mm':8.5})
    if other=='thermal-fuse' and 'native_stub_tip_mm' in info:
        result.append({'center_mm':info['native_stub_tip_mm'],'radius_mm':2.5})
    return result


def mask_stages(manifest,name,target,empty_contacts):
    stages=[{'name':'named-endpoints-and-fuse-stub',
             'spheres':neighborhoods(manifest,name,target)}]
    cells={}
    if name.rsplit('/',1)[-1]=='terminal-J4' and target.rsplit('/',1)[-1]=='pcba':
        frames=manifest['terminations']['terminal-J4'].get('mating_terminals',{})
        cells={key:frames[key]for key in empty_contacts
               if key in frames and key not in manifest['terminals'] and
               frames[key]['part'].rsplit('/',1)[-1]=='pcba'}
        stages.append({'name':'named-empty-J4-cells',
                       'spheres':[{'center_mm':frame['point'],'radius_mm':8.5}
                                  for frame in cells.values()]})
    return stages,cells


def combined(values):
    nonempty=[row for row in values if row['min']is not None]
    return {'volume_mm3':sum(row['volume_mm3']for row in values),
            'min':[min(row['min'][i]for row in nonempty)for i in range(3)]if nonempty else None,
            'max':[max(row['max'][i]for row in nonempty)for i in range(3)]if nonempty else None}


def review(aggregate,manifest_path,output,*,equipment,closures,meter_wires,
           empty_contacts,fixed_interface,preparation_lengths,refresh_cache=False,
           verify_bindings=True,selection_sources=()):
    """All fine AABB overlaps receive exact closed-entry commons and named masks."""
    import _assembly_model
    aggregate,manifest_path,output=map(Path,(aggregate,manifest_path,output))
    physical=Path(str(aggregate)+'.npz')
    wiring=Path(str(manifest_path.with_suffix('.step'))+'.npz')
    manifest=json.loads(manifest_path.read_text())
    @cache
    def digest(path):
        with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
    fine=fine_review(manifest_path,aggregate,output)
    record={'scope':'Authoritative physical and installed-wiring fine closed entries. Every exact fine AABB-overlap pair is queried; no STEP readback or displayed triangles select or measure contacts. Component commons sum their closed-entry commons. Wire-to-wire and wire-to-tube contacts are excluded. Named endpoint/fuse spheres and the two physical empty J4 cells retain their existing local scope. No physical fit, electrical or energization qualification.',
            'physical_fine_model_sha256':digest(physical),'wiring_fine_model_sha256':digest(wiring),
            'manifest_sha256':digest(manifest_path),'reader_sha256':digest(Path(__file__)),
            'source_sha256':{str(Path(path)):digest(Path(path))for path in
                            (Path(__file__),Path(fine_review.__code__.co_filename),*selection_sources)},
            'source_binding_matches':fine['all_bindings_match'],
            'candidate_method':'Every authoritative fine AABB overlap, including fully contained stock; no presentation broadphase.',
            'endpoint_exclusion_radius_mm':8.5,'fuse_stub_exclusion_radius_mm':2.5,
            'intersection_threshold_mm3':.01,'review_complete':False,
            'intersections':[],'errors':[],'empty_housing_mating_proof':[],
            'preparation_lengths':preparation_lengths(manifest)}
    def save():
        report=json.loads(output.read_text())if output.exists()else{}
        report['fine_contacts']=record;output.write_text(json.dumps(report,indent=2)+'\n')
    if verify_bindings and not fine['all_bindings_match']:
        record['errors'].append({'error':'Fine source/model/export bindings do not match.'})
        record['geometrically_clear']=False;save();return record
    physical_rows=_assembly_model.measure([_assembly_model.instance(physical)],())['bodies']
    wire_rows=_assembly_model.measure([_assembly_model.instance(wiring)],())['bodies']
    installed,stock=groups(wire_rows),groups(physical_rows)
    by_leaf={name.rsplit('/',1)[-1]:name for name in stock}
    closure_names={by_leaf[name]for name in closures if name in by_leaf}
    equipment_names={name for name in stock if wire_obstacle(name) and
                     (name.rsplit('/',1)[-1]in equipment or fixed_interface(name.rsplit('/',1)[-1]))}
    foam={by_leaf['foam-shell']}if 'foam-shell'in by_leaf else set()
    targets=closure_names|equipment_names|foam
    expected=({'wire-'+row['id']for row in manifest['routes']}|set(manifest['terminations'])|
              {row['geometry_name']for row in manifest['bundles'].values()if row['geometry_name']})
    record.update(conductor_count=sum(name.rsplit('/',1)[-1].startswith('wire-')for name in installed),
                  wiring_body_count=len(installed),expected_wiring_body_count=len(expected),
                  missing_wiring_bodies=sorted(expected-set(installed)),
                  extra_wiring_bodies=sorted(set(installed)-expected),
                  missing_closures=sorted(closures-set(by_leaf)),
                  missing_equipment=sorted(equipment-set(by_leaf)),
                  missing_meter_wires=sorted(meter_wires-{name.rsplit('/',1)[-1]for name in installed}),
                  missing_external_jacket_core=not foam,closure_names=sorted(closure_names),
                  equipment_names=sorted(equipment_names),physical_names=sorted(stock),
                  invalid_wiring_bodies=sorted(name for name,row in installed.items()if row['volume']<=0.))
    def overlaps(a,b):
        return all(a['max'][i]>b['min'][i] and b['max'][i]>a['min'][i]for i in range(3))
    pairs=[(name,target)for name,body in sorted(installed.items())for target in sorted(targets)
           if (target not in foam or name.rsplit('/',1)[-1]=='terminal-compressor-cord-jacket')and
           overlaps(body,stock[target])]
    def scope(target):return 'closures'if target in closure_names else'equipment'
    record['candidate_pairs']=[{'body':name,'part':target,'scope':scope(target)}for name,target in pairs]
    record['candidate_count']=len(pairs);record['fine_common_count']=0;save()
    for start in range(0,len(pairs),24):
        batch=pairs[start:start+24]
        wire_indices=sorted({i for name,_target in batch for i in installed[name]['indices']})
        stock_indices=sorted({i for _name,target in batch for i in stock[target]['indices']})
        wire_index={original:i for i,original in enumerate(wire_indices)}
        stock_index={original:len(wire_indices)+i for i,original in enumerate(stock_indices)}
        queries=[];owners=[];pair_info={}
        for name,target in batch:
            stages,cells=mask_stages(manifest,name,target,empty_contacts)
            pair_info[(name,target)]=(stages,cells)
            for a in installed[name]['indices']:
                for b in stock[target]['indices']:
                    queries.append({'kind':'common','a':wire_index[a],'b':stock_index[b],
                                    'mask_stages':stages})
                    owners.append((name,target))
        said=_assembly_model.measure([_assembly_model.instance(wiring,indices=wire_indices),
                                      _assembly_model.instance(physical,indices=stock_indices)],queries)
        if len(said['queries'])!=len(owners):
            record['errors'].append({'error':'Fine common query coverage differs from its requested pairs.'})
        readings={pair:[]for pair in batch}
        for owner,row in zip(owners,said['queries']):
            if 'error'in row:record['errors'].append({'body':owner[0],'part':owner[1],'error':row['error']})
            else:readings[owner].append(row['common'])
        record['fine_common_count']+=len(queries)
        for (name,target),values in readings.items():
            if not values:continue
            raw=combined([row['raw']for row in values])
            residual=raw
            if raw['volume_mm3']>.01:
                residual=combined([row['stages'][0]['residual']for row in values])
                stages,cells=pair_info[(name,target)]
                if residual['volume_mm3']>.01 and len(stages)==2:
                    outside=combined([row['stages'][1]['residual']for row in values])
                    contained=len(cells)==2 and outside['volume_mm3']<.01
                    record['empty_housing_mating_proof'].append({
                        'termination':name,'device':target,'mating_terminals':cells,'cell_radius_mm':8.5,
                        'residual_after_wired_cells_mm3':residual['volume_mm3'],
                        'outside_named_empty_cells_mm3':outside['volume_mm3'],
                        'exact_fine_containment':contained,
                        'scope':'Two named physical empty housing cells; no electrical graph terminals or whole-device exclusion.'})
                    if contained:residual=outside
            if residual['volume_mm3']>.01:
                record['intersections'].append({'scope':scope(target),'body':name,'part':target,
                    'raw_volume_mm3':raw['volume_mm3'],'volume_mm3':residual['volume_mm3'],
                    'bounds_mm':residual['min']+residual['max']})
        save()
        print(f'Fine contact pairs {min(start+24,len(pairs))}/{len(pairs)}',flush=True)
    def current_digest(path):
        with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
    record['inputs_unchanged_after_queries']=(current_digest(physical)==digest(physical)and
        current_digest(wiring)==digest(wiring)and current_digest(manifest_path)==digest(manifest_path))
    record['geometrically_clear']=(fine['all_bindings_match']and record['inputs_unchanged_after_queries']and
        not any(record[key]for key in ('intersections','errors','missing_wiring_bodies','extra_wiring_bodies',
            'missing_closures','missing_equipment','missing_meter_wires','missing_external_jacket_core','invalid_wiring_bodies')))
    record['review_complete']=True;save()
    if refresh_cache:
        folder=ROOT/'tmp/above-core-electrical-fixture/fine';folder.mkdir(parents=True,exist_ok=True)
        index={'scope':'Explicit immutable fine input references; no native BREP cache is renewed.',
               'physical_model':{'path':str(physical),'sha256':digest(physical),'bodies':stock},
               'wiring_model':{'path':str(wiring),'sha256':digest(wiring),'bodies':installed},
               'manifest_sha256':digest(manifest_path),'review':str(output)}
        (folder/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    return record


class CurrentFine:
    """One explicitly bound physical/wiring cohort for manually invoked studies.

    Bounds select candidates only. Commons use the f64 closed entries; source
    stock/cutters and tool cylinders are separate query geometry, never a
    replacement for a purchased or printed body.
    """
    def __init__(self, manifest_path, aggregate, *, source_root=None, facts=None,
                 source_proof=None, fine_index=None):
        import numpy as np
        from .review import _source_mismatches
        from .step_merge import base_document
        self.np=np
        self.manifest_path=Path(manifest_path).resolve()
        self.aggregate=Path(aggregate).resolve()
        self.root=Path(source_root or ROOT).resolve()
        self.manifest=json.loads(self.manifest_path.read_text())
        if not self.manifest.get('wiring_fine_model_sha256'):
            raise ValueError('This manual study requires the explicit current kernel wiring manifest')
        self.paths={'physical':Path(str(self.aggregate)+'.npz'),
                    'wiring':Path(str(self.manifest_path.with_suffix('.step'))+'.npz')}
        self.hashes={role:self.digest(path)for role,path in self.paths.items()}
        if self.hashes['physical']!=self.manifest['physical_fine_model_sha256'] or self.hashes['wiring']!=self.manifest['wiring_fine_model_sha256']:
            raise ValueError('Fine model does not match the explicit current manifest')
        mismatches=_source_mismatches(self.manifest,self.root)
        if mismatches:raise ValueError('Current fine source binding differs: '+', '.join(mismatches))
        if self.digest(self.manifest_path.with_suffix('.numbers.json'))!=self.manifest['wiring_numbers_sha256']:
            raise ValueError('Numeric recipe does not match the explicit current manifest')
        physical_step=hashlib.sha256(base_document(self.aggregate.read_text()).encode()).hexdigest()
        if physical_step!=self.manifest['physical_scene_sha256']:
            raise ValueError('Aggregate physical STEP does not match the explicit current manifest')
        self.payloads={}
        for role,step in [('physical',self.aggregate),('wiring',self.manifest_path.with_suffix('.step'))]:
            payload=Path(str(step)+'.mesh')
            with payload.open('rb')as stream:
                size=int.from_bytes(stream.read(4),'little');header=json.loads(stream.read(size))
            if header.get('src')!=self.digest(step):raise ValueError(f'{payload}: stale STEP source')
            self.payloads[role]={'path':str(payload),'sha256':self.digest(payload),
                                 'src':header.get('src'),'cut':header.get('cut')}
        with np.load(self.paths['wiring'],allow_pickle=False)as archive:
            document=json.loads(bytes(archive['document']))
        if document.get('presentation')!={'path':self.manifest_path.with_suffix('.step').name+'.mesh',
                                         'sha256':self.payloads['wiring']['sha256']}:
            raise ValueError('Wiring fine presentation binding differs')
        self.entries={};self.indices={};self._bounds={};self._manifolds={};self.aux={};self.aux_sources={}
        for role,path in self.paths.items():
            with np.load(path,allow_pickle=False)as archive:
                names=json.loads(bytes(archive['names']).decode())
            self.entries[role]=names
            grouped={}
            for index,name in enumerate(names):grouped.setdefault(base_name(name),[]).append(index)
            self.indices[role]=grouped
        self.proof=None
        if source_proof:
            self.proof=json.loads(Path(source_proof).read_text())
            checked=self.proof.get('fine',{})
            if not (checked.get('all_bindings_match')and
                    checked.get('physical_fine_model_sha256')==self.hashes['physical']and
                    checked.get('wiring_fine_model_sha256')==self.hashes['wiring']and
                    checked.get('manifest_sha256')==self.digest(self.manifest_path)):
                raise ValueError('Supplied fine proof belongs to another cohort')
        self.facts_path=Path(facts)if facts else self.aggregate.with_suffix('.facts.json')
        self.facts=json.loads(self.facts_path.read_text())
        handoff=self.facts.get('tube_export',{})
        if handoff.get('fine_model',{}).get('sha256')!=self.hashes['physical']:
            raise ValueError('Facts do not bind this physical fine model')
        self.bindings={'scope':'Explicit authoritative f64 entries; payload metadata describes its own presentation only.',
            'manifest':{'path':str(self.manifest_path),'sha256':self.digest(self.manifest_path)},
            'models':{role:{'path':str(path),'sha256':self.hashes[role],
                            'qualified_names':sorted(self.indices[role])}for role,path in self.paths.items()},
            'payloads':self.payloads,'facts':{'path':str(self.facts_path),'sha256':self.digest(self.facts_path)},
            'source_root':str(self.root),'source_mismatches':[],
            'source_proof':({'path':str(Path(source_proof).resolve()),'sha256':self.digest(source_proof)}if source_proof else None)}
        if fine_index:
            index=json.loads(Path(fine_index).read_text())
            if 'bindings'in index:
                matches=all(index['bindings'].get(key)==value for key,value in self.bindings.items()
                            if key not in('source_proof','source_root'))
            else:
                # aggregate_review's retained fine index binds the same models.
                matches=(index.get('manifest_sha256')==self.digest(self.manifest_path)and
                    all(index.get(role+'_model',{}).get('sha256')==self.hashes[role]and
                        Path(index[role+'_model']['path']).resolve()==self.paths[role]
                        for role in self.paths))
            if not matches:
                raise ValueError('Fine fixture index belongs to another cohort')
        self.replacements={}
        retained=[Path(__file__),Path(__file__).with_name('review.py'),
                  self.manifest_path,self.manifest_path.with_suffix('.numbers.json'),self.aggregate,
                  self.manifest_path.with_suffix('.step'),self.facts_path,
                  *(Path(row['path'])for row in self.payloads.values()),
                  *(self.root/name for name in self.manifest.get('source_sha256',{}))]
        if source_proof:retained.append(Path(source_proof))
        if fine_index:retained.append(Path(fine_index))
        self.external_inputs={str(path.resolve()):self.digest(path)for path in retained}

    @staticmethod
    def digest(path):
        with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

    def resolve(self,name,role='physical'):
        if role=='physical'and name in self.replacements:return self.replacements[name]
        if name in self.indices[role]:return role,name
        found=[key for key in self.indices[role]if key.rsplit('/',1)[-1]==name]
        if len(found)!=1:raise KeyError(f'{role}: {name!r} has {len(found)} qualified matches')
        return self.replacements.get(found[0],(role,found[0]))if role=='physical'else(role,found[0])

    def names(self,role='physical'):return tuple(self.indices[role])

    def arrays(self,ref):
        role,name=ref;np=self.np
        if role=='aux':
            mesh=self.aux[name].to_mesh64()
            return np.asarray(mesh.vert_properties,np.float64)[:,:3],np.asarray(mesh.tri_verts,np.uint32).reshape(-1,3)
        verts,tris,base=[],[],0
        with np.load(self.paths[role],allow_pickle=False)as archive:
            for index in self.indices[role][name]:
                v=np.asarray(archive[f'V{index}'],np.float64);t=np.asarray(archive[f'T{index}'],np.uint32)
                verts.append(v);tris.append(t+base);base+=len(v)
        return np.concatenate(verts),np.concatenate(tris)

    def bounds(self,ref):
        if ref not in self._bounds:
            if ref[0]=='aux':
                solid=self.aux[ref[1]]
                self._bounds[ref]=None if solid.is_empty()else list(solid.bounding_box())
            else:
                v,_=self.arrays(ref);self._bounds[ref]=v.min(0).tolist()+v.max(0).tolist()
        return self._bounds[ref]

    def manifold(self,ref):
        import manifold3d as m3d
        if ref[0]=='aux':return self.aux[ref[1]]
        if ref not in self._manifolds:
            v,t=self.arrays(ref);mesh=m3d.Mesh64(v,self.np.asarray(t,self.np.uint64))
            mesh.merge();solid=m3d.Manifold(mesh)
            if solid.status()!=m3d.Error.NoError or solid.is_empty():raise ValueError(f'{ref}: invalid closed fine entries')
            self._manifolds[ref]=solid
        return self._manifolds[ref]

    def add_aux(self,name,solid,description):
        import manifold3d as m3d
        if name in self.aux:raise ValueError('Repeated query geometry: '+name)
        if solid.status()!=m3d.Error.NoError:raise ValueError('Invalid query geometry: '+name)
        source=description.get('src',{}).get('path')
        if source:self.retain(source)
        self.retain(*description.get('numeric_sources',{}))
        self.aux[name]=solid;self.aux_sources[name]=description
        return 'aux',name

    def retain(self,*paths):
        for path in paths:
            path=Path(path).resolve();digest=self.digest(path)
            previous=self.external_inputs.setdefault(str(path),digest)
            if previous!=digest:raise ValueError('Manual query source changed: '+str(path))

    def export_index(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps({'scope':'Immutable fine references; no BREP geometry cache.',
                                   'bindings':self.bindings},indent=2)+'\n')
        return path

    def commons(self,pairs,*,masks=None,mask_above=0.):
        """Ordered pair commons. Each pair retains its exact qualified entry bindings."""
        import _assembly_model
        import tempfile
        import numpy as np
        pairs=list(pairs)
        if not pairs:return []
        used={role:sorted({index for pair in pairs for r,name in pair if r==role
                           for index in self.indices[role][name]})for role in self.paths}
        instances=[];slot={};offset=0
        for role in ('wiring','physical'):
            if not used[role]:continue
            instances.append(_assembly_model.instance(self.paths[role],indices=used[role]))
            for index in used[role]:slot[role,index]=offset;offset+=1
        aux_names=sorted({name for pair in pairs for role,name in pair if role=='aux'})
        with tempfile.TemporaryDirectory(prefix='hsm-manual-fine-')as tmp:
            if aux_names:
                items={'names':np.frombuffer(json.dumps(aux_names).encode(),np.uint8),
                       'colors':np.frombuffer(json.dumps([None]*len(aux_names)).encode(),np.uint8),
                       'records':np.frombuffer(json.dumps([[None]for _ in aux_names]).encode(),np.uint8)}
                for index,name in enumerate(aux_names):
                    v,t=self.arrays(('aux',name));items[f'V{index}']=v;items[f'T{index}']=t
                    items[f'F{index}']=np.zeros(len(t),np.uint32);slot['aux',name]=offset;offset+=1
                path=Path(tmp)/'query-geometry.npz';np.savez(path,**items)
                instances.append(_assembly_model.instance(path))
            def entries(ref):
                role,name=ref
                return [slot[role,name]]if role=='aux'else[slot[role,index]for index in self.indices[role][name]]
            queries=[];owners=[]
            for owner,pair in enumerate(pairs):
                for a in entries(pair[0]):
                    for b in entries(pair[1]):
                        row={'kind':'common','a':a,'b':b,'mask_above_mm3':mask_above}
                        if masks:row['mask_stages']=masks[owner]
                        queries.append(row);owners.append(owner)
            said=_assembly_model.measure(instances,queries)['queries']
        if len(said)!=len(queries):raise ValueError('Fine query coverage differs')
        grouped=[[]for _ in pairs]
        for owner,row in zip(owners,said):
            if 'error'in row:raise ValueError(f'{pairs[owner]}: {row["error"]}')
            grouped[owner].append(row['common'])
        return [{'raw':combined([row['raw']for row in values]),
                 'residual':combined([row['residual']for row in values]),
                 'entry_common_count':len(values),'qualified_pair':[list(ref)for ref in pair]}
                for pair,values in zip(pairs,grouped)]

    def finish(self):
        if any(self.digest(path)!=self.hashes[role]for role,path in self.paths.items())or any(self.digest(path)!=digest for path,digest in self.external_inputs.items()):
            raise ValueError('Fine inputs changed during manual queries')
        self.bindings['auxiliary_query_geometry']=self.aux_sources
        self.bindings['retained_input_sha256']=self.external_inputs
        return self.bindings


def fine_arguments(parser,root):
    """Explicit current cohort inputs shared by manual helper CLIs."""
    root=Path(root)
    parser.add_argument('--manifest',type=Path,default=root/'hardware/wiring/enclosure-wiring.json')
    parser.add_argument('--aggregate',type=Path,default=root/'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--facts',type=Path)
    parser.add_argument('--source-root',type=Path,default=root)
    parser.add_argument('--source-proof',type=Path,help='Reuse a hash-bound completed fine/source proof; never native solids')
    parser.add_argument('--fine-index',type=Path,help='Optional immutable fine fixture index; no BREP cache is read')


def current_fine(args):
    return CurrentFine(args.manifest,args.aggregate,source_root=args.source_root,facts=args.facts,
                       source_proof=args.source_proof,fine_index=args.fine_index)


def fine_overlap(first,second,tol=1e-5):
    if first is None or second is None:return False
    return all(first[i+3]>second[i]+tol and second[i+3]>first[i]+tol for i in range(3))


def numeric_values(path,names,bindings=None):
    """Read selected source constants without executing its native imports/builders."""
    import ast,math
    tree=ast.parse(Path(path).read_text())
    assignments={}
    def bind(target,value):
        if isinstance(target,ast.Name):assignments[target.id]=value
        elif isinstance(target,(ast.Tuple,ast.List)):
            for i,child in enumerate(target.elts):
                bind(child,ast.Subscript(value=value,slice=ast.Constant(i),ctx=ast.Load()))
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for target in node.targets:bind(target,node.value)
        elif isinstance(node,ast.AnnAssign)and node.value is not None:bind(node.target,node.value)
    values={'math':math,**(bindings or {})};visiting=set()
    def read(name):
        if name in values:return values[name]
        if name in visiting:raise ValueError('Cyclic numeric source: '+name)
        node=assignments[name];visiting.add(name)
        for dependency in {n.id for n in ast.walk(node)if isinstance(n,ast.Name)}&assignments.keys():
            if dependency!=name:read(dependency)
        values[name]=eval(compile(ast.fix_missing_locations(ast.Expression(node)),str(path),'eval'),values)
        visiting.remove(name);return values[name]
    return {name:read(name)for name in names}


def source_functions(path,names,bindings,*,bound_imports=()):
    """Execute only the named existing numeric/query functions in explicit bindings."""
    import ast
    tree=ast.parse(Path(path).read_text())
    nodes=[node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name in names]
    if {node.name for node in nodes}!=set(names):raise ValueError('Missing query source function')
    class BoundImports(ast.NodeTransformer):
        def visit_Import(self,node):
            remaining=[alias for alias in node.names if(alias.asname or alias.name.split('.')[0])not in bound_imports]
            if not remaining:return None
            node.names=remaining;return node
    if set(bound_imports)-set(bindings):raise ValueError('Missing explicit numeric import binding')
    nodes=[BoundImports().visit(node)for node in nodes]
    scope={'__file__':str(path),**bindings}
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),scope)
    return {name:scope[name]for name in names}


def box_solid(low,high):
    import manifold3d as m3d
    if any(b<=a for a,b in zip(low,high)):raise ValueError('Source query box has no material')
    return m3d.Manifold.cube([b-a for a,b in zip(low,high)]).translate(low)


def rounded_stock(low,high,radius):
    """The source rounded-rectangle stock at the existing fine circle rule."""
    import manifold3d as m3d
    from meshcad.rule import ring_count
    x,y,z=(b-a for a,b in zip(low,high))
    section=m3d.CrossSection.square((x-2*radius,y-2*radius)).offset(
        radius,join_type=m3d.JoinType.Round,circular_segments=ring_count(radius))
    return section.extrude(z).translate((low[0]+radius,low[1]+radius,low[2]))


def cylinder_solid(radius,length,origin,axis):
    import manifold3d as m3d
    from meshcad.rule import axis_frame,ring_count
    import numpy as np
    z,x,y=axis_frame(axis);axis=np.asarray(axis,float);axis/=np.linalg.norm(axis)
    if np.dot(z,axis)<0:y=-y;z=axis
    matrix=np.column_stack((x,y,z,np.asarray(origin,float)))
    return m3d.Manifold.cylinder(length,radius,circular_segments=ring_count(radius)).transform(matrix)


class _QueryShape:
    """The small source query-geometry vocabulary; no native CAD objects."""
    def __init__(self,solid):self.solid=solid
    def moved(self,matrix):return _QueryShape(self.solid.transform(matrix))
    def cut(self,*others):
        result=self.solid
        for other in others:result=result-other.solid
        return _QueryShape(result)
    def fuse(self,*others):
        result=self.solid
        for other in others:result=result+other.solid
        return _QueryShape(result)
    def clean(self):return self


def source_layout(context):
    import importlib.util
    path=context.root/'hardware/manifold-layout/above_core.py'
    context.retain(path,path.with_name('above-core.json'))
    spec=importlib.util.spec_from_file_location('_manual_fine_layout',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def junction_geometry(context,only=None,*,include_holders=True):
    """Existing source stock/cutters/driver definitions evaluated on fine query solids."""
    from types import SimpleNamespace
    import numpy as np
    import manifold3d as m3d
    layout=source_layout(context)
    path=context.root/'hardware/manifold-layout/above_core_wiring.py'
    constants=numeric_values(path,('SIZES','WALL','FIT','IDENTITY','PORTS_WEST','PORTS_FORE',
                                   'UPRIGHT_PORTS_FORE','WALL_BACK_FORE','WALL_BACK_AFT','EAST_FLANK'))
    def box(x0,x1,y0,y1,z0,z1):return _QueryShape(box_solid((x0,y0,z0),(x1,y1,z1)))
    def cylinder(radius,length,origin,axis):return _QueryShape(cylinder_solid(radius,length,origin,axis))
    cq=SimpleNamespace(Vector=lambda *values:values,
                       Solid=SimpleNamespace(makeCylinder=cylinder))
    scope={'layout':layout,'_box':box,'cq':cq,**constants}
    functions=source_functions(path,('placements','_well','driver_columns'),scope)
    poses=functions['placements']()
    def carry(name):
        row=poses[name]
        return SimpleNamespace(where=np.column_stack((row['rotation'],row['translation_mm'])))
    functions['_well'].__globals__['carry']=carry
    wells={};stocks={};pockets={};hosts={};parents={}
    for name,row in poses.items():
        if only is not None and name not in only:continue
        stock,pocket=functions['_well'](name)
        parent=row['parent'];host=context.resolve('foam-cap-lid-top'if parent=='cold-core'else'enclosure-'+parent)
        description={'src':{'path':str(path),'sha256':context.digest(path),'function':'_well'},
                     'pose':row,'qualified_host':list(host),
                     'cut':'Source pocket subtracted from source stock, intersected with actual bound host material'}
        stock_cut=stock.cut(pocket).solid
        installed=m3d.Manifold.batch_boolean([context.manifold(host),stock_cut],m3d.OpType.Intersect)
        wells[name]=context.add_aux(name+'-well',installed,description)
        stocks[name]=stock.solid;pockets[name]=pocket.solid;hosts[name]=host
        parents.setdefault(parent,[]).append(name)
    holders={}
    for parent,names in parents.items():
        if not include_holders:continue
        stock=m3d.Manifold.batch_boolean([stocks[name]for name in names],m3d.OpType.Add)
        pocket=m3d.Manifold.batch_boolean([pockets[name]for name in names],m3d.OpType.Add)
        host=hosts[names[0]]
        installed=m3d.Manifold.batch_boolean([context.manifold(host),stock-pocket],m3d.OpType.Intersect)
        holders[parent]=context.add_aux(parent+'-holder',installed,
            {'src':{'path':str(path),'sha256':context.digest(path),'function':'_features'},
             'qualified_host':list(host),'stock_names':names,'cut':'Union of source pockets, applied to actual host material'})
    drivers={}
    for name,shape in functions['driver_columns']().items():
        drivers[name]=context.add_aux('driver-'+name,shape.solid,
            {'src':{'path':str(path),'sha256':context.digest(path),'function':'driver_columns'},
             'psu_pose':layout.pose('psu'),'kind':'Source-defined nominal driver cylinder'})
    pocket_refs={name:context.add_aux(name+'-pocket',solid,
        {'src':{'path':str(path),'sha256':context.digest(path),'function':'_well'},'pose':poses[name],
         'kind':'Source cutter, not a physical body'})for name,solid in pockets.items()}
    return {'layout':layout,'poses':poses,'sizes':constants['SIZES'],'wells':wells,
            'holders':holders,'drivers':drivers,'pockets':pocket_refs,'hosts':hosts}


def valve_wall_geometry(context,names=('valve-v-a','vk-solenoid')):
    """Actual back-top material inside the current source valve-seat stock."""
    from types import SimpleNamespace
    import numpy as np
    import manifold3d as m3d
    layout=source_layout(context)
    source=context.root/'hardware/printed-parts/enclosure/enclosure/_above_core_shell.py'
    producer=source.with_name('_enclosure_back_top.py')
    beduan=context.root/'hardware/reference/beduan-solenoid/beduan_solenoid.py'
    valve=SimpleNamespace(**numeric_values(beduan,('corner_inset_x','corner_inset_y','corner_boss_radius',
                                                 'boss_z_range','port_center_z','port_radius')))
    fits=SimpleNamespace(**numeric_values(context.root/'hardware/printed-parts/cadlib/fits.py',('slip',)))
    seat_path=context.root/'hardware/printed-parts/valve-seat/valve_seat.py'
    seat=SimpleNamespace(**numeric_values(seat_path,('seat_half_x','seat_half_y','socket_floor_z','wall',
                                          'seat_top_z','seat_corner_radius','socket_diameter'),
                                         {'valve':valve,'fits':fits}),valve=valve,fits=fits)
    datums=source_functions(source,('valve_seat_datums',),
        {'layout':layout,'seat':seat,'HERE':source.parent,
         'sys':SimpleNamespace(path=SimpleNamespace(insert=lambda *_:None))},
        bound_imports=('seat',))['valve_seat_datums']()
    host=context.resolve('enclosure-back-top');result={};descriptions={}
    dependencies=(seat_path,beduan,context.root/'hardware/printed-parts/cadlib/fits.py',producer,
                  context.root/'hardware/manifold-layout/rear_plumbing.py')
    context.retain(*dependencies)
    for name in names:
        data=datums[name]
        if name=='valve-v-a':
            depth=layout.specification()['rear_plumbing']['joint']['PLINTH']
            low=(-seat.seat_half_x,-seat.seat_half_y,-depth)
            high=(seat.seat_half_x,seat.seat_half_y,seat.seat_top_z)
            frame=layout.pose(name)
            stock=rounded_stock(low,high,seat.seat_corner_radius).transform(
                np.column_stack((frame['rotation'],frame['translation_mm'])))
            data={**data,'stock_native_min_mm':low,'stock_native_max_mm':high,
                  'stock_corner_radius_mm':seat.seat_corner_radius,
                  'stock_definition':'Current valve_seats V-A rounded plinth; PLINTH comes from rear_plumbing.plan'}
        else:stock=box_solid(data['stock_min_world_mm'],data['stock_max_world_mm'])
        actual=m3d.Manifold.batch_boolean([context.manifold(host),stock],m3d.OpType.Intersect)
        result[name]=context.add_aux(name+'-wall',actual,
            {'src':{'path':str(source),'sha256':context.digest(source),'function':'valve_seats'},
             'qualified_host':list(host),'stock':data,
             'cut':'Current source stock intersects actual bound back-top material; source sockets/channels and all later cuts remain actual fine material',
             'numeric_sources':{str(path):context.digest(path)for path in dependencies}})
        descriptions[name]=data
    return result,descriptions


def production_tube_specs(context):
    """The exact routed specs the normal producer put in its hash-bound facts."""
    handoff=context.facts['tube_export']
    return handoff['routing']['native_route_specs']


def frame_drain_datums(context):
    """The retained numeric frame/drain question, from its current source functions."""
    from types import SimpleNamespace
    folder=context.root/'hardware/printed-parts/zone-c/funnel'
    funnel_path,elbow_path,frame_path=(folder/name for name in('funnel.py','elbow_cradle.py','funnel_frame.py'))
    context.retain(funnel_path,elbow_path,frame_path)
    funnel=SimpleNamespace(**numeric_values(funnel_path,('aft_extension','forward_extension',
                                'drop','plug_width','neck_dx','neck_dy')))
    elbow_values=numeric_values(elbow_path,('SOCKET_HALF','SLOT_AFT_Y','SLOT_FORE_Y','END_SLIP'))
    elbow=SimpleNamespace(**elbow_values,**source_functions(elbow_path,
        ('socket_half_length','plug_half_length'),elbow_values))
    values=numeric_values(frame_path,('center_y','socket_width','web','rail_below_seat'),
                          {'funnel':funnel,'elbow_cradle':elbow})
    functions=source_functions(frame_path,('datums','drain_seat_datums'),
                               {'funnel':funnel,'elbow_cradle':elbow,**values})
    return functions['drain_seat_datums']()


def selected_hardware(context,junction_names=()):
    """Selected and retained hardware identities, resolved only to actual fine entries."""
    layout=source_layout(context);data=layout.specification()
    selected=set(data['parts'])|set(layout.core_equipment_names())|set(data['snapshots'])
    selected.update(('asse-drain-adapter','gagira-coupling','jg-pi4512f6s','jg-pp061208w',
        'water-split','flow-regulator','gas-regulator','gas-check','keystone-jack',
        'soda-bend-holder','soda-continuous-insulation'))
    for row in data['fluid_grid']['assignment']:
        for name in row:
            selected.add(name)
            if name not in('bulkhead-water','co2-inlet'):selected.add(name+'-nut')
    retained=('compressor','condenser+fan','mq6-sensor','thermal-fuse','fuse-clamp','display','display-cover',
              'funnel-frame','elbow-cradle','funnel-drain-union','funnel-drain-stub','rear-nameplate-receiver')
    result={}
    for name in context.names():
        leaf=name.rsplit('/',1)[-1]
        if leaf in junction_names:continue
        if leaf in selected or leaf in retained or leaf.startswith(('pump-a-','pump-b-','tee-y-','stem-elbow-',
                'flavor-reducer-','coil-v-','valve-v-')) or leaf in(
                'tube-fluid-9','tube-fluid-10','tube-fluid-11','tube-fluid-12','tube-fluid-13','tube-fluid-17',
                'tube-fluid-19','tube-fluid-20','tube-fluid-21','tube-fluid-22','tube-fluid-23','tube-fluid-27'):
            result[name]=context.resolve(name)
    return result


def wire_source_reading(context):
    """Reuse the explicit completed proof, or answer this manual source question once."""
    if context.proof is not None:
        result=context.proof.get('fine_source',{})
        if not result.get('all_bindings_match'):raise ValueError('Fine proof contains no completed source binding')
        return result
    import tempfile
    from . import review as reader
    previous=reader.ROOT
    try:
        reader.ROOT=context.root
        with tempfile.TemporaryDirectory(prefix='hsm-manual-source-')as tmp:
            return reader.source_review(context.manifest_path,context.aggregate,Path(tmp)/'source.json')
    finally:reader.ROOT=previous


def cap_trial_replacements(context,cup,lid,frames):
    """Explicit fine cap models and rigid frames replace trial material only."""
    import numpy as np
    import manifold3d as m3d
    if not(cup and lid and frames):raise ValueError('Fine cap trials require both models and --cap-frames JSON')
    frames=Path(frames);declaration=json.loads(frames.read_text())
    context.external_inputs[str(frames)]=context.digest(frames)
    result={}
    for role,path,world_name in(('cup',Path(cup),'foam-cap-bottom'),('lid',Path(lid),'foam-cap-lid-top')):
        row=declaration[role];digest=context.digest(path)
        if digest!=row['sha256']:raise ValueError('Trial cap model differs from its frame declaration')
        with np.load(path,allow_pickle=False)as archive:
            names=json.loads(bytes(archive['names']).decode())
            indices=[i for i,name in enumerate(names)if name==row['qualified_name']]
            if not indices:raise ValueError('Trial cap has no declared qualified body')
            vv,tt,base=[],[],0
            for i in indices:
                v=np.asarray(archive[f'V{i}'],np.float64);t=np.asarray(archive[f'T{i}'],np.uint64)
                vv.append(v);tt.append(t+base);base+=len(v)
        transform=np.asarray(row['transform'],float)
        if transform.shape!=(3,4)or not np.isfinite(transform).all()or not np.allclose(transform[:,:3]@transform[:,:3].T,np.eye(3),atol=1e-10):
            raise ValueError('Trial cap needs an explicit rigid 3x4 installed frame')
        mesh=m3d.Mesh64(np.concatenate(vv),np.concatenate(tt));mesh.merge()
        solid=m3d.Manifold(mesh).transform(transform)
        if solid.status()!=m3d.Error.NoError or solid.is_empty():raise ValueError('Invalid trial fine cap')
        host=context.resolve(world_name)
        ref=context.add_aux('trial-'+world_name,solid,
            {'src':{'path':str(path),'sha256':digest,'qualified_name':row['qualified_name']},
             'installed_frame':row['transform'],'replaces_qualified_body':host[1],
             'scope':'Explicit fine cap trial; normal physical/source/fit receipts are not renewed'})
        context.replacements[host[1]]=ref;context.external_inputs[str(path)]=digest
        result[str(path)]={'sha256':digest,'frame':row,'replaces':host[1]}
    return result
