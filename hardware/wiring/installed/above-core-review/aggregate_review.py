"""Manual native contact review of the exported appliance's installed wiring.

Run through the workstation CAD queue after enclosure-assembly.step and its
wiring manifest/payload are materialized. Reads the actual assembly; it does not
compose wiring, generate shells or update production geometry.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout'),
             str(ROOT/'hardware/printed-parts/cold-core'),str(ROOT/'hardware/printed-parts/cadlib')]
import cadquery as cq
import fcl
import numpy as np
import above_core
import above_core_bom
import above_core_wiring
import _above_core_mounts as mounts
from _cadq_export import import_assembly
from _mesh_payload import read_source
from hardware.wiring.installed.review import load_mesh,base_name
from hardware.wiring.installed.route_search import capsule,sampled
from hardware.wiring.installed.model import STOCK
from hardware.wiring.installed.step_merge import base_document

HERE=Path(__file__).resolve().parent
CLOSURES=frozenset(('enclosure-front-top','enclosure-back-top','enclosure-front-bottom',
                    'enclosure-back-bottom','enclosure-pump-cap','enclosure-pump-cartridge',
                    'foam-cap-top','foam-cap-lid-top','funnel-frame'))
METER_WIRES=frozenset(('wire-J4-V5','wire-J4-IO25','wire-flow-GND'))
B_FILL=frozenset(('reservoir-b-fill-lower','reservoir-b-fill-upper'))
EMPTY_J4_CONTACTS=('J4.IO23','J4.IO27')
JUNCTION_FIXED=frozenset(('compressor','condenser+fan','mq6-sensor','thermal-fuse',
    'fuse-clamp','display','display-cover',
    'funnel-frame','elbow-cradle','funnel-drain-union','funnel-drain-stub'))


def junction_fixture_member(leaf):
    return (leaf in JUNCTION_FIXED or leaf.startswith(('pump-a-','pump-b-',
            'tee-y-','stem-elbow-','flavor-reducer-','coil-v-','valve-v-','tube-')))


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def box(shape):
    b=shape.BoundingBox()
    return np.array((b.xmin,b.ymin,b.zmin)),np.array((b.xmax,b.ymax,b.zmax))


def overlap(a,b):return bool(np.all(a[1]>b[0]+1e-6) and np.all(b[1]>a[0]+1e-6))


def object_for(mesh):
    vertices,faces=mesh
    model=fcl.BVHModel();model.beginModel(len(vertices),len(faces));model.addSubModel(vertices,faces);model.endModel()
    return fcl.CollisionObject(model)


def selected_equipment():
    """Selected native tenants without building any reference or shell solids."""
    data=above_core.specification()
    names=(set(data['parts'])|set(above_core.core_equipment_names())|
           set(above_core_bom.stem_elbow_names())|set(above_core_bom.union_elbow_names())|
           set(above_core_bom.core_stem_elbow_names())|set(above_core_bom.core_union_elbow_names())|
           set(above_core_wiring.placements())|
           {'ground-stack','asse-inlet-tpu','asse-outlet-tpu','asse-drain-adapter',
            'water-split','flow-regulator','gas-regulator','gas-check','keystone-jack',
            'soda-bend-holder','soda-continuous-insulation'})
    for row in data['fluid_grid']['assignment']:
        for name in row:names.update((name,name+'-nut'))
    return names


def fixed_interface(leaf):
    return (leaf.startswith(('coil-v-','valve-v-','tee-y-','stem-elbow-',
                             'flavor-reducer-','pump-a-','pump-b-')) or
            leaf in ('display','display-cover','elbow-cradle','funnel-drain-union',
                     'funnel-drain-stub','thermal-fuse','fuse-clamp'))


def preparation_lengths(manifest):
    """Project requested bench-cut comparisons from this bound manifest."""
    schedule=ROOT/'hardware/wiring/_ac_wiring_schedule_sync.py'
    lengths={}
    for node in ast.parse(schedule.read_text()).body:
        if (isinstance(node,ast.Assign) and len(node.targets)==1 and
                isinstance(node.targets[0],ast.Name) and
                node.targets[0].id.startswith('len_')):
            try:lengths[node.targets[0].id]=ast.literal_eval(node.value)
            except (ValueError,TypeError):pass
    routes={row['id']:row for row in manifest['routes']}
    groups=(
        ('AC-1 inlet pigtails','len_mid_mm',
         (('AC1-L',),('AC1-N',),('AC1-PE',))),
        ('AC-2 fixed 16 AWG','len_short_2_mm',(('AC2-L',),('AC2-N',))),
        ('AC-3 relay supply','len_short_mm',(('AC3-L',),)),
        ('DC-1 fixed 16 AWG','len_dc1_mm',(('DC1-V12',),('DC1-GND',))),
        ('DC-2 fixed 16 AWG','len_dc2_mm',(('DC2-V12',),)),
        ('DC-3 pump','len_pump_mm',(('DC3-positive',),('DC3-negative',))),
        ('DC-4 fixed 16 AWG','len_mid_mm',(('DC4-V12',),('DC4-GND',))),
        ('compressor SJOOW stock','len_compressor_mm',
         (('AC4-H','AC4-fuse'),('AC5-N',),('AC6-PE',))),
        ('J13 pump ribbon','len_pump_fixed_mm',
         tuple((name,) for name in routes if name.startswith('J13-'))),
        ('manifold A common','len_man_a_com_mm',(('J1-COM',),)),
        ('manifold A returns','len_man_a_mm',
         tuple((name,) for name in routes if name.startswith('J1-OUT'))),
        ('manifold A positive branches','len_man_a_fanout_mm',
         tuple((name,) for name in routes if name.startswith('J1-positive-'))),
        ('manifold B common','len_man_b_com_mm',(('J2-COM',),)),
        ('manifold B returns','len_man_b_mm',(('J2-OUT1',),('J2-OUT2',))),
        ('manifold B positive branches','len_man_b_fanout_mm',
         tuple((name,) for name in routes if name.startswith('J2-positive-'))),
        ('condenser fan return','len_fan_mm',(('J2-FAN',),)),
        ('V-K return','len_vk_mm',(('J2-OUT3',),)),
        ('J9 display','len_front_face_mm',
         tuple((name,) for name in routes if name.startswith('J9-'))),
        ('J3 faucet inboard','len_faucet_inboard_mm',
         tuple((name,) for name in routes if name.startswith('J3-'))),
        ('temperature bus','len_onewire_mm',
         (('J4-3V3','temp-bus-V'),('J4-IO26','temp-bus-DATA'),
          ('temp-GND','temp-bus-GND'))),
        ('sensor common pigtail','len_sensors_gnd_mm',(('J4-GND',),)),
        ('flow meter','len_flow_mm',(('J4-V5',),('J4-IO25',),('flow-GND',))),
        ('relay logic','len_relays_mm',
         (('J5-V5','relay-bus-V5'),('J5-GND','relay-bus-GND'),
          ('J5-IO19',),('J5-IO2',))),
        ('reservoir A leads','len_reeds_a_mm',
         (('J6-GND','J6-earth-1','J6-earth-2','J6-earth-3'),
          ('J6-RA1',),('J6-RA2',),('J6-RA3',),('J6-RA4',))),
        ('reservoir B leads','len_reeds_b_mm',
         (('J7-earth-4','J7-earth-1','J7-earth-2','J7-earth-3'),
          ('J7-RB1',),('J7-RB2',),('J7-RB3',),('J7-RB4',))),
        ('reed common pigtail','len_reeds_gnd_mm',(('J7-GND',),)),
        ('carbonator reed leads','len_carb_reeds_mm',
         (('J7-carb-earth-2','J7-carb-earth-1'),('J7-CLO',),('J7-CHI',))),
        ('gas sensor','len_gas_mm',
         tuple((name,) for name in routes if name.startswith('J11-'))),
    )
    rows=[]
    for name,variable,paths in groups:
        members=[]
        for path in paths:
            missing=[part for part in path if part not in routes]
            total=None if missing else sum(routes[part]['length_mm'] for part in path)
            members.append({'route_ids':path,'missing_routes':missing,
                            'developed_path_mm':None if total is None else round(total,3),
                            'remaining_preparation_mm':None if total is None else
                                round(lengths[variable]-total,3)})
        known=[row['developed_path_mm'] for row in members if row['developed_path_mm'] is not None]
        maximum=max(known) if known else None
        rows.append({'group':name,'schedule_constant':variable,
                     'prepared_length_mm':lengths[variable],
                     'maximum_developed_path_mm':maximum,
                     'minimum_remaining_preparation_mm':None if maximum is None else
                         round(lengths[variable]-maximum,3),
                     'members':members})
    covered={name for _group,_variable,paths in groups for path in paths for name in path}
    return {'source':str(schedule.relative_to(ROOT)),'source_sha256':digest(schedule),
            'scope':'Developed lengths from this actual exported manifest compared '
                    'with current preparation stock. The compressor hot allocation '
                    'includes both AC4-H and AC4-fuse pieces; the reservoir-A common '
                    'includes all three continuing earth spans. Remaining stock is '
                    'a nominal cutting allowance, not physical dressing or termination qualification.',
            'groups':rows,
            'routes_without_numeric_preparation_stock':[
                {'id':name,'developed_path_mm':routes[name]['length_mm']}
                for name in sorted(set(routes)-covered)]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--aggregate',type=Path,default=ROOT/'hardware/manifold-layout/enclosure-assembly.step')
    parser.add_argument('--manifest',type=Path,default=ROOT/'hardware/wiring/enclosure-wiring.json')
    parser.add_argument('--output',type=Path,default=HERE/'aggregate-review.json')
    parser.add_argument('--refresh-cache',action='store_true',
                        help='Refresh the explicit wiring BREP fixture and composition record from this actual export')
    args=parser.parse_args()
    meshpath=Path(str(args.aggregate)+'.mesh')
    manifest=json.loads(args.manifest.read_text())
    step_hash=digest(args.aggregate)
    record={'scope':'Actual exported appliance: every installed wiring body against selected above-core equipment, fixed front interfaces and termination bodies, all six enclosure pieces, two top core caps, funnel frame and electronics roof panel. Current source-defined nominal retaining strips are separate supplemental targets. Both B-fill fittings are tested against every wiring body. The external compressor jacket also clears the physical foam shell. No wire-to-wire packing, physical fit, electrical or energization qualification.',
            'aggregate_sha256':step_hash,'aggregate_mesh_sha256':digest(meshpath),
            'aggregate_mesh_matches_step':read_source(meshpath)==step_hash,
            'manifest_sha256':digest(args.manifest),'review_complete':False,
            'intersections':[],'errors':[],'native_boolean_count':0,
            'candidate_padding_mm':1.,
            'candidate_method':'Native bounding boxes and route capsules inflated 1 mm against the bound viewer payload, plus native containment witnesses; native Booleans for candidates.',
            'endpoint_exclusion_radius_mm':8.5,'fuse_native_stub_exclusion_radius_mm':2.5,
            'endpoint_rule':'Only named device attachments and a conductor\'s own termination IDs receive local endpoint neighborhoods, matching installed/review.py. A termination receives those same local neighborhoods at its own named mating device. The two named empty physical J4.IO23/IO27 cells use the same8.5 mm own-device neighborhoods only after exact residual containment. Native fuse-stub contact uses the existing 2.5 mm neighborhood.',
            'source_sha256':{str(path.relative_to(ROOT)):digest(path) for path in
                             (Path(__file__),Path(above_core.__file__),Path(above_core_bom.__file__),
                              Path(above_core_wiring.__file__),Path(mounts.__file__),ROOT/'hardware/manifold-layout/above-core.json')}}
    physical_hash=hashlib.sha256(base_document(args.aggregate.read_text()).encode()).hexdigest()
    record['manifest_binds_physical_scene']=manifest.get('physical_scene_sha256')==physical_hash
    record['preparation_lengths']=preparation_lengths(manifest)
    if not record['aggregate_mesh_matches_step']:
        record['errors'].append('The assembly mesh does not bind the selected STEP.')
        args.output.write_text(json.dumps(record,indent=2)+'\n');raise SystemExit(1)
    print('Read actual materialized appliance',flush=True)
    scene={n:s for n,(s,_c) in import_assembly(str(args.aggregate)).items()}
    by_leaf={n.rsplit('/',1)[-1]:n for n in scene}
    bodies={n:s for n,s in scene.items() if n.rsplit('/',1)[-1].startswith(('wire-','terminal-'))}
    routes={'wire-'+r['id']:r for r in manifest['routes']}
    terminations=manifest['terminations']
    record['empty_housing_mating_proof']=[]
    record['conductor_count']=sum(n.rsplit('/',1)[-1].startswith('wire-') for n in bodies)
    record['wiring_body_count']=len(bodies)
    record['invalid_wiring_bodies']=[n for n,s in bodies.items() if not s.isValid() or s.Volume()<=0.]
    present_bodies={n.rsplit('/',1)[-1] for n in bodies}
    record['missing_conductors']=sorted(set(routes)-present_bodies)
    expected_bodies=(set(routes)|set(terminations)|
                     {b['geometry_name'] for b in manifest['bundles'].values() if b['geometry_name']})
    record['expected_wiring_body_count']=len(expected_bodies)
    record['missing_wiring_bodies']=sorted(expected_bodies-present_bodies)
    record['physical_names']=sorted(set(scene)-set(bodies))
    record['current_core_aliases']=sorted(n for n in scene if n.startswith('cold-core/'))
    closure_names={by_leaf[n] for n in CLOSURES if n in by_leaf}
    expected_equipment=selected_equipment()
    equipment_names={n for n in scene if n.rsplit('/',1)[-1] in expected_equipment or fixed_interface(n.rsplit('/',1)[-1])}
    termination_names={n for n in bodies if not n.rsplit('/',1)[-1].startswith('wire-')}
    external_jacket_core={by_leaf['foam-shell']} if 'foam-shell' in by_leaf else set()
    strips=mounts.nominal_tie_strips()
    strip_routes={**mounts.union_tie_routes(),**mounts.meter_tie_routes(),
                  'water-check':mounts.check_tie_route()}
    nominal_names={'nominal-strip-'+name for name in strips}
    scene.update({'nominal-strip-'+name:shape for name,shape in strips.items()})
    record['nominal_retaining_strips']={name:{
        'length_mm':strip_routes[name]['length_mm'],
        'width_mm':strip_routes[name]['width_mm'],
        'thickness_mm':strip_routes[name]['thickness_mm'],
        'route_sha256':hashlib.sha256(json.dumps(strip_routes[name],sort_keys=True).encode()).hexdigest(),
        'valid':shape.isValid(),
        'scope':'Source-defined nominal flat-section segments; separate from the exported physical scene. Purchased strap/head, threading, bend/twist transitions and retention remain unqualified.'}
        for name,shape in strips.items()}
    target_names=closure_names|equipment_names|termination_names|external_jacket_core|nominal_names
    record['external_jacket_core_names']=sorted(external_jacket_core)
    record['missing_external_jacket_core']=not external_jacket_core
    record['closure_names']=sorted(closure_names)
    record['missing_closures']=sorted(CLOSURES-set(by_leaf))
    record['equipment_names']=sorted(equipment_names)
    record['missing_equipment']=sorted(expected_equipment-set(by_leaf))
    record['termination_obstacles']=sorted(termination_names)
    record['meter_wire_names']=sorted(by_leaf[n] for n in METER_WIRES if n in by_leaf)
    record['missing_meter_wires']=sorted(METER_WIRES-set(by_leaf))
    meshes=load_mesh(meshpath)
    target_meshes={n:m for n,m in meshes.items() if base_name(n) in target_names}
    for name in nominal_names:
        vertices,faces=scene[name].tessellate(.07,.1)
        target_meshes[name]=(np.array([v.toTuple() for v in vertices]),np.array(faces))
    record['missing_target_meshes']=sorted(target_names-{base_name(n) for n in target_meshes})
    objects={n:object_for(m) for n,m in target_meshes.items()}
    mesh_boxes={n:(v.min(0),v.max(0)) for n,(v,_f) in target_meshes.items()}
    native_boxes={n:box(s) for n,s in scene.items()}
    candidates=set()
    def allowed_pair(name,target):
        if name==target:return False
        if target in external_jacket_core:return name.rsplit('/',1)[-1]=='terminal-compressor-cord-jacket'
        # Two termination envelopes need one symmetric common, not two copies.
        return not(name in termination_names and target in termination_names and name>target)
    print(f'Find candidates for {len(bodies)} wiring bodies and {len(target_names)} equipment/closure/termination targets',flush=True)
    for name,solid in bodies.items():
        leaf=name.rsplit('/',1)[-1]
        potential=[m for m in objects if allowed_pair(name,base_name(m)) and
                   overlap(native_boxes[name],native_boxes[base_name(m)])]
        if not potential:continue
        if leaf in routes:
            row=routes[leaf];radius=STOCK[row['stock']]['od_mm']/2.+1.
            points=sampled(row['segments'],1.)
            for a,b in zip(points,points[1:]):
                witness=(np.minimum(a,b)-radius,np.maximum(a,b)+radius)
                for m in potential:
                    target=base_name(m)
                    if (name,target) in candidates or not overlap(witness,mesh_boxes[m]):continue
                    if fcl.collide(capsule(a,b,radius),objects[m],fcl.CollisionRequest(),fcl.CollisionResult())>0:
                        candidates.add((name,target))
        else:
            lo,hi=native_boxes[name];witness=fcl.CollisionObject(fcl.Box(*(hi-lo+2.)),fcl.Transform((lo+hi)/2.))
            for m in potential:
                if fcl.collide(witness,objects[m],fcl.CollisionRequest(),fcl.CollisionResult())>0:
                    candidates.add((name,base_name(m)))
    # Surface collisions alone do not detect a body fully embedded in stock.
    # One native witness adds contained pairs before their exact common.
    contained=[]
    target_solids={n:scene[n].Solids() for n in target_names}
    for name,solid in bodies.items():
        leaf=name.rsplit('/',1)[-1]
        witness=(routes[leaf]['segments'][0]['start_mm'] if leaf in routes else
                 solid.Vertices()[0].Center().toTuple())
        for target in target_names:
            if not allowed_pair(name,target) or (name,target) in candidates or not overlap(native_boxes[name],native_boxes[target]):continue
            if not(np.all(np.asarray(witness)>=native_boxes[target][0]-1e-6) and np.all(np.asarray(witness)<=native_boxes[target][1]+1e-6)):continue
            if any(stock.isInside(witness,1e-6) for stock in target_solids[target]):
                candidates.add((name,target));contained.append([name,target])
    record['native_containment_candidates']=contained
    def scope_for(target):
        if target in closure_names:return 'closures'
        if target in termination_names:return 'terminations'
        if target in nominal_names:return 'nominal retaining strips'
        return 'equipment'
    record['candidate_pairs']=[{'body':name,'part':target,'scope':scope_for(target)} for name,target in sorted(candidates)]
    record['candidate_counts']={kind:sum(scope_for(target)==kind for _name,target in candidates)
                                for kind in ('closures','equipment','terminations','nominal retaining strips')}
    # Persist the artifact/candidate binding before the potentially slower commons.
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print('Native candidate counts '+json.dumps(record['candidate_counts']),flush=True)
    checked=set()
    def local_neighborhoods(name,target):
        leaf=name.rsplit('/',1)[-1];other=target.rsplit('/',1)[-1]
        info=terminations.get(leaf,{})
        terminal_ids=([routes[leaf][k] for k in ('start','end')] if leaf in routes else info.get('terminal_ids',[]))
        other_ids=terminations.get(other,{}).get('terminal_ids',[])
        result=[]
        for id in terminal_ids:
            if id not in manifest['terminals']:continue  # Empty housing cavities have no installed conductor.
            terminal=manifest['terminals'][id]
            if terminal['part'].rsplit('/',1)[-1]==other or id in other_ids:
                result.append((terminal['point'],8.5))
        if other=='thermal-fuse' and 'native_stub_tip_mm' in info:
            result.append((info['native_stub_tip_mm'],2.5))
        return result
    def check(name,target,scope):
        if (name,target) in checked or not overlap(native_boxes[name],native_boxes[target]):return
        checked.add((name,target))
        try:
            hit=scene[name].intersect(scene[target])
            record['native_boolean_count']+=1
            volume=hit.Volume()
            if volume>.01:
                for point,radius in local_neighborhoods(name,target):
                    hit=hit.cut(cq.Solid.makeSphere(radius,cq.Vector(*point),angleDegrees1=-90.,angleDegrees2=90.))
                volume=hit.Volume()
                if (name.rsplit('/',1)[-1]=='terminal-J4' and
                        target.rsplit('/',1)[-1]=='pcba' and volume>.01):
                    frames=terminations['terminal-J4'].get('mating_terminals',{})
                    cells={key:frames[key] for key in EMPTY_J4_CONTACTS
                           if key in frames and key not in manifest['terminals'] and
                           frames[key]['part'].rsplit('/',1)[-1]=='pcba'}
                    proposed=hit
                    for frame in cells.values():
                        if proposed.Volume()<1e-12:break
                        proposed=proposed.cut(cq.Solid.makeSphere(
                            8.5,cq.Vector(*frame['point']),angleDegrees1=-90.,angleDegrees2=90.))
                    outside=proposed.Volume()
                    contained=len(cells)==2 and outside<.01
                    record['empty_housing_mating_proof'].append({
                        'termination':name,'device':target,'mating_terminals':cells,
                        'cell_radius_mm':8.5,'residual_after_wired_cells_mm3':volume,
                        'outside_named_empty_cells_mm3':outside,
                        'exact_native_containment':contained,
                        'scope':'Two physical empty housing cells; no electrical graph terminals or whole-device exclusion added.'})
                    if contained:hit=proposed;volume=outside
            if volume>.01:
                lo,hi=box(hit)
                row={'scope':scope,'body':name,'part':target,'volume_mm3':volume,'bounds_mm':list(lo)+list(hi)}
                record['intersections'].append(row);print(json.dumps(row),flush=True)
        except Exception as error:
            row={'scope':scope,'body':name,'part':target,'error':str(error)}
            record['errors'].append(row);print(json.dumps(row),flush=True)
    for number,(name,target) in enumerate(sorted(candidates),1):
        check(name,target,scope_for(target))
        if number%50==0:print(f'{number}/{len(candidates)} native candidate pairs checked',flush=True)
    # The B-fill question covers every housing, especially aft J6/J7 plugs.
    record['b_fill_parts']=sorted(by_leaf[n] for n in B_FILL if n in by_leaf)
    record['missing_b_fill_parts']=sorted(B_FILL-set(by_leaf))
    for target in record['b_fill_parts']:
        for name in bodies:check(name,target,'B-fill fittings')
    # The display loom passes the revised B-draw fore loop on its way to the
    # existing ridge bore. Record the requested local nominal air explicitly.
    record['display_B_draw_clearances_mm']={}
    if 'tube-fluid-26' in by_leaf:
        tube=scene[by_leaf['tube-fluid-26']]
        for leaf in ('wire-J9-A','wire-J9-B','wire-J9-GND','wire-J9-V12'):
            if leaf in by_leaf:
                record['display_B_draw_clearances_mm'][leaf]=scene[by_leaf[leaf]].distance(tube)
    record['invalid_nominal_retaining_strips']=[name for name,row in record['nominal_retaining_strips'].items() if not row['valid']]
    record['geometrically_clear']=not any(record[k] for k in
        ('intersections','errors','missing_conductors','missing_wiring_bodies','missing_closures',
         'missing_target_meshes','missing_equipment','missing_b_fill_parts','missing_meter_wires',
         'missing_external_jacket_core','invalid_wiring_bodies','invalid_nominal_retaining_strips')) and record['manifest_binds_physical_scene']
    record['review_complete']=True
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    if args.refresh_cache:
        folder=ROOT/'tmp/above-core-electrical-fixture/wiring'
        folder.mkdir(parents=True,exist_ok=True)
        files={}
        for i,(name,solid) in enumerate(sorted(bodies.items())):
            file=f'{i}.brep';solid.exportBrep(str(folder/file));files[name.rsplit('/',1)[-1]]=file
        index=folder/'index.json'
        index.write_text(json.dumps({'aggregate_sha256':step_hash,'parts':files},indent=2)+'\n')
        physical=folder.parent/'junction-fixed'
        physical.mkdir(parents=True,exist_ok=True)
        physical_files={}
        for name in sorted(set(scene)-set(bodies)-nominal_names):
            if not junction_fixture_member(name.rsplit('/',1)[-1]):continue
            file=f'{len(physical_files)}.brep'
            scene[name].exportBrep(str(physical/file))
            physical_files[name]=file
        physical_index=physical/'index.json'
        physical_index.write_text(json.dumps({'aggregate_sha256':step_hash,
            'scope':'Actual exported fixed hardware and tubes retained by the junction review.',
            'parts':physical_files},indent=2)+'\n')
        path=HERE/'native-review.json'
        composition=json.loads(path.read_text()) if path.exists() else {}
        for key in ('connection_count','reference_frames','cable_passages','interfaces',
                    'terminations','bundles','routes','terminals','source_sha256'):
            composition[key]=manifest[key]
        composition.update(physical_fixture_scope='Actual exported appliance and bound installed-wiring manifest',
                           physical_fixture_sha256=step_hash,cap_fixture_sha256={},
                           fixture_names=sorted(set(scene)-nominal_names),contact_review_run=True,
                           contact_wires=sorted(r['id'] for r in manifest['routes']),
                           route_failures=record['invalid_wiring_bodies'],termination_failures=[],
                           route_intersections=record['intersections'],
                           valid_wire_count=sum(n.rsplit('/',1)[-1].startswith('wire-') and
                                                n not in record['invalid_wiring_bodies'] for n in bodies),
                           wiring_brep_index=str(index.relative_to(ROOT)),review_complete=True,
                           junction_fixed_brep_index=str(physical_index.relative_to(ROOT)),
                           aggregate_contact_review={'record':str(args.output.relative_to(ROOT)),
                                                     'sha256':digest(args.output),'scope':record['scope'],
                                                     'geometrically_clear':record['geometrically_clear']})
        composition.pop('focused_cache_refresh',None)
        composition.pop('holder_intersections',None)
        composition.pop('junction_driver_intersections',None)
        path.write_text(json.dumps(composition,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('conductor_count','wiring_body_count','native_boolean_count','geometrically_clear')},indent=2),flush=True)

if __name__=='__main__':main()
