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
