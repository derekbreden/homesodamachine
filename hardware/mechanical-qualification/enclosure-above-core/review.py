"""Manual closure and populated-core motion query against the exported machine.

Run through tmp/takeover/cadq after exporting enclosure-assembly.step.
This review is not called by a generator, hook or recurring build.
"""
import hashlib
import json
from pathlib import Path
import sys

import manifold3d as mf
import numpy as np
import trimesh

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
sys.path.insert(0, str(ROOT/'hardware/scripts'))
from _cadq_export import import_assembly

SOURCE = ROOT/'hardware/manifold-layout/enclosure-assembly.step'
FACTS = SOURCE.with_suffix('.facts.json')
OUTPUT = Path(__file__).with_name('native-review.json')


def manifold(shape):
    parts=[]
    for solid in shape.Solids():
        vertices, faces=solid.tessellate(.02, .08)
        mesh=trimesh.Trimesh(np.asarray([v.toTuple() for v in vertices]),
                            np.asarray(faces), process=True)
        result=mf.Manifold(mf.Mesh(np.asarray(mesh.vertices, np.float32),
                                  np.asarray(mesh.faces, np.uint32)))
        if result.status() != mf.Error.NoError:
            raise ValueError(f'Invalid motion mesh: {result.status()}')
        parts.append(result)
    return mf.Manifold.batch_boolean(parts, mf.OpType.Add)


def bounds(shape):
    b=shape.BoundingBox()
    return np.array([b.xmin,b.ymin,b.zmin]),np.array([b.xmax,b.ymax,b.zmax])


def main():
    imported=import_assembly(SOURCE)
    placed={name:row[0] for name,row in imported.items()}
    def name_for(tail):
        matches=[name for name in placed if name.split('/')[-1] == tail]
        if len(matches)!=1:
            raise ValueError(f'{tail}: expected one component, found {matches}')
        return matches[0]
    cache={}
    def meshed(name):
        if name not in cache:
            cache[name]=manifold(placed[name])
        return cache[name]
    records=[]
    for tail in ('enclosure-front-top','enclosure-back-top',
                 'funnel-frame','electronics-access-panel'):
        shape=placed[name_for(tail)]
        valid=shape.isValid()
        solids=len(shape.Solids())
        records.append({'check':'Native printed component / '+tail,
                        'passed':valid and solids==1,
                        'valid':valid,'solids':solids})
    sleeve_name=name_for('soda-rise-insulation')
    sleeve=placed[sleeve_name]
    low,high=bounds(sleeve)
    sleeve_readings=[]
    for name,body in placed.items():
        if name==sleeve_name or name.split('/')[-1]=='tube-soda-core-rise':
            continue
        a,b=bounds(body)
        if np.any(high<a) or np.any(b<low):
            continue
        sleeve_readings.append({'body':name,
            'common_mm3':sleeve.intersect(body).Volume(),
            'distance_mm':sleeve.distance(body)})
    records.append({'check':'Square-cut soda insulation against installed stock and wiring',
        'passed':sleeve.isValid() and len(sleeve.Solids())==1
                 and all(r['common_mm3']<.001 for r in sleeve_readings),
        'valid':sleeve.isValid(),'solids':len(sleeve.Solids()),
        'nominal_stock_mm':{'length':15.,'inside_diameter':6.35,'outside_diameter':25.4},
        'nearby_tested':sleeve_readings,
        'scope':'Uncompressed nominal annulus; intended soda-tube bore contact excluded. '
                'No foam compression, slit/tape retention, installation force or thermal performance result.'})
    def query(label, moving_tail, poses, skip, moving_shapes=None, component_names=None):
        moving=name_for(moving_tail)
        offsets=np.asarray(poses,float)
        shapes={moving:placed[moving]} if moving_shapes is None else moving_shapes
        boxes={key:bounds(shape) for key,shape in shapes.items()}
        local_meshes={}
        sweep_low=np.min([low for low,high in boxes.values()],axis=0)+offsets.min(axis=0)
        sweep_high=np.max([high for low,high in boxes.values()],axis=0)+offsets.max(axis=0)
        hits=[]
        tested=[]
        for name,body in placed.items():
            tail=name.split('/')[-1]
            if name==moving or skip(tail):
                continue
            a,b=bounds(body)
            if np.any(sweep_high < a) or np.any(b < sweep_low):
                continue
            volumes=np.zeros(len(offsets))
            nearby=[]
            for key,shape in shapes.items():
                low,high=boxes[key]
                active=[i for i,offset in enumerate(offsets)
                        if np.all(high+offset>=a) and np.all(b>=low+offset)]
                if not active:
                    continue
                if key not in local_meshes:
                    print('Meshing moving component:',key,flush=True)
                    local_meshes[key]=meshed(key) if key in placed else manifold(shape)
                obstacle=meshed(name)
                moving_mesh=local_meshes[key]
                for i in active:
                    volumes[i]+=float((moving_mesh.translate(offsets[i])^obstacle).volume())
                nearby.append(key)
            if not nearby:
                continue
            maximum=max(volumes)
            tested.append(name)
            if maximum > .1:
                hits.append({'body':name,'maximum_overlap_mm3':maximum,
                             'poses':[{'offset_mm':p.tolist(),'overlap_mm3':v}
                                      for p,v in zip(offsets,volumes) if v>.1]})
        record={'check':label,'passed':not hits,'moving':moving,
                'offsets_mm':offsets.tolist(),'nearby_tested':tested,'intersections':hits,
                'method':'Sum of native-component mesh intersection volumes per obstacle and pose. '
                         'This conservatively counts any overlap between carried components twice; '
                         'the entire moving group is not unioned before the query.'}
        if component_names is not None:
            record['moving_components']=component_names
        records.append(record)
        print(json.dumps(record),flush=True)
    lifts=[0,.1,.25,.5,1,2,3,6,9,12,15,20,30,40,50,56,60]
    query('Empty funnel frame vertical removal','funnel-frame',[(0,0,z) for z in lifts],
          lambda n:n in ('funnel','funnel-cover','elbow-cradle','funnel-drain-union',
                         'funnel-drain-stub','drain-outlet-stem','tube-fluid-4',
                         'tube-above-core-drain-vb-east-link')
          or n.startswith('funnel-frame-') and n.endswith('-screw'))
    query('Empty electronics panel vertical removal','electronics-access-panel',
          [(0,0,z) for z in lifts if z<=30],
          lambda n:n.startswith('electronics-panel-') and n.endswith('-screw'))
    # The lid equipment stays with the core. Back-top's changed upper stock,
    # fixed equipment and prepared internal fluid group ride together.
    # Inter-quadrant tubing and leads are connected after the column closes.
    import cadquery as cq
    sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),
                  str(ROOT/'hardware/assembly/scenes'),
                  str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
    import _scenes
    import _realized
    facts=json.loads(FACTS.read_text())
    if facts['step'] != _realized.code_digest(SOURCE):
        raise ValueError('Motion review requires facts from this exact exported STEP')
    # Read ownership from the imported components. A name-only lookup without
    # an assembly reconstructs the manifold merely to enumerate its bodies.
    inventory=cq.Assembly(name='exported-inventory')
    inventory_names=set()
    for full_name, body in placed.items():
        tail=full_name.split('/')[-1]
        if tail in inventory_names:
            raise ValueError(f'Duplicate exported component tail: {tail}')
        inventory_names.add(tail)
        inventory.add(body,name=tail)
    inventory.wiring_body_names=frozenset(n for n in inventory_names
        if n.startswith(('wire-','terminal-','jacket-')))
    ownership=_scenes.holders(inventory)
    late_rear=frozenset(('bulkhead-carb','bulkhead-carb-nut',
                         'bulkhead-drain','bulkhead-drain-nut',
                         'soda-stem-elbow','soda-outlet-return-stem',
                         'tube-soda-meter-bulkhead','tube-drain-vent'))
    header_preassembly=frozenset(_scenes.CORE_INLET_HEADER_PREASSEMBLY)
    back_bodies=frozenset(name for name in _scenes.held_by('enclosure-back-top',ownership,
                         stop=('electronics-access-panel','funnel-frame','funnel','funnel-cover'))
                         if not name.startswith('tube-')
                         and name not in (late_rear | header_preassembly))
    back_tails=set(back_bodies)
    present_tails={name.split('/')[-1] for name in placed}
    def endpoint_body(endpoint):
        candidates=[tail for tail in present_tails if endpoint==tail
                    or endpoint.startswith(tail+'.') or endpoint.startswith(tail+' ')]
        return max(candidates,key=len,default=None)
    for run in facts['native_runs']:
        if {endpoint_body(run['frm']),endpoint_body(run['to'])} <= back_bodies:
            back_tails.add('tube-'+run['id'])
    core_tails={n.split('/')[-1] for n,s in placed.items()
                if 'cold-core/' in n and bounds(s)[1][2]>253.3}
    core_tails |= header_preassembly
    upper=cq.Solid.makeBox(400,800,200,cq.Vector(-200,0,253.3))
    back_top=placed[name_for('enclosure-back-top')].intersect(upper)
    carried=[name for name,body in placed.items()
             if name.split('/')[-1] in back_tails
             and name.split('/')[-1]!='enclosure-back-top'
             and not name.split('/')[-1].endswith('-screw')
             and bounds(body)[1][2]>253.3]
    moving={name_for('enclosure-back-top')+' above Z253.3':back_top,
            **{name:placed[name] for name in carried}}
    query('Back-top upper stock and fixed group over populated cold core','enclosure-back-top',
          [(0,y,0) for y in (0,.25,.5,1,*range(2,302,2))],
          lambda n:n not in core_tails,moving_shapes=moving,
          component_names=[name_for('enclosure-back-top')+' above Z253.3',*carried])
    # Seat the two bare valves before the removable lid equipment. The post
    # needs only the real socket depth of axial clearance during lowering.
    # Use untrimmed native bodies here: clipping the target at a coincident
    # socket face changes the kernel's treatment of that mating boundary.
    sys.path.insert(0,str(ROOT/'hardware/printed-parts/valve-seat'))
    import above_core as layout
    import valve_seat
    printed={name:body for name,body in placed.items()
             if 'cold-core/' in name and name.split('/')[-1].startswith('foam-')}
    late_bench=set(layout.core_equipment_names())|{'digiten-flow','soda-inlet-stem'}
    electrical_tokens=('wago','junction','ground','terminal','housing',
                       'termination','ferrule','spade')
    bench_fixed={name:body for name,body in placed.items()
        if 'cold-core/' in name
        and name.split('/')[-1] not in late_bench
        and not name.split('/')[-1].startswith(
            ('tube-','wire-','terminal-','jacket-','termination-'))
        and not any(token in name.split('/')[-1] for token in electrical_tokens)}
    def near(a,b):
        return np.all(a[1]>=b[0]-1e-7) and np.all(b[1]>=a[0]-1e-7)
    def native_common(a,b):
        common=a.intersect(b,tol=1e-6)
        return 0. if common.isNull() else abs(common.Volume())
    for valve in ('valve-v-a','vk-solenoid'):
        moving=name_for(valve)
        shape=placed[moving]
        low,high=bounds(shape)
        axis=np.asarray(layout.vector(layout.pose(valve)['rotation'],(0.,0.,1.)))
        depth=valve_seat.socket_depth()
        offset=axis*depth
        highest=max(bounds(body)[1][2] for body in printed.values())
        lift=highest+1.-low[2]
        sweep_low=low+offset
        sweep_high=high+offset+np.array((0.,0.,lift))
        envelope=cq.Solid.makeBox(*(sweep_high-sweep_low),cq.Vector(*sweep_low))
        vertical=[]
        for name,body in bench_fixed.items():
            if near((sweep_low,sweep_high),bounds(body)):
                vertical.append({'body':name,'common_mm3':native_common(envelope,body),
                                 'distance_mm':envelope.distance(body)})
        samples=[]
        for amount in (depth,6.,5.5,5.2,5.,4.,3.,2.,1.,.5,.25,.1,0.):
            shift=axis*amount
            moved=shape.translate(tuple(shift))
            tested=[{'body':name,'common_mm3':native_common(moved,body)}
                    for name,body in bench_fixed.items()
                    if near(bounds(moved),bounds(body))]
            samples.append({'offset_mm':shift.tolist(),'native_candidates':tested})
        passed=all(row['common_mm3']<1e-6 for row in vertical)
        passed &= all(row['common_mm3']<1e-6
                      for sample in samples for row in sample['native_candidates'])
        record={'check':'Bare valve open-bench lowering and seating / '+valve,
            'passed':passed,'moving':moving,
            'post_engagement_mm':valve_seat.seat_top_z,
            'blind_socket_depth_mm':depth,
            'socket_floor_reserve_mm':-valve_seat.socket_floor_z,
            'vertical_offset_path_mm':[(offset+np.array((0.,0.,z))).tolist()
                                       for z in (lift,0.)],
            'vertical_scope':'Continuous conservative full-valve bounding-box envelope.',
            'vertical_native_candidates':vertical,'seating_samples':samples,
            'stage_present_components':sorted(bench_fixed),
            'stage_absent_core_components':sorted(name for name in placed
                if 'cold-core/' in name and name not in bench_fixed and name!=moving),
            'full_printed_core_members_retained':sorted(printed),
            'native_boolean_tolerance_mm':1e-6}
        records.append(record)
        print(json.dumps(record),flush=True)
        bench_fixed[moving]=shape
    sys.path.insert(0,str(ROOT/'hardware/printed-parts/enclosure/enclosure'))
    import enclosure as enc
    import _box_spec
    box,_=_box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate))
    front=placed[name_for('enclosure-front-top')]
    _,seat,tip,length,_,insert_bottom,insert_top=enc.y_stack_rods(box.inner)[1]
    for x,side in ((box.inner[0],1.),(box.inner[1],-1.)):
        cx,cy=enc.y_stack_axis(x,side,box.y_joint,'upper')
        pilot=enc._y_stack_bores(x,side,box.y_joint,box.inner)[5].BoundingBox()
        radius=enc.floor_heatset_dia/2.
        outer=cq.Solid.makeCylinder(radius+3.,insert_top-pilot.zmin,
                                    cq.Vector(cx,cy,pilot.zmin))
        inner=cq.Solid.makeCylinder(radius,insert_top-pilot.zmin+.2,
                                    cq.Vector(cx,cy,pilot.zmin-.1))
        missing_stock=outer.cut(inner).cut(front).Volume()
        pilot_air=cq.Solid.makeCylinder(radius,insert_top-pilot.zmin,
                                        cq.Vector(cx,cy,pilot.zmin))
        pilot_blockage=front.intersect(pilot_air).Volume()
        floor=cq.Solid.makeCylinder(radius,3.,cq.Vector(cx,cy,pilot.zmin-3.))
        missing_floor=floor.cut(front).Volume()
        reach=insert_top-tip-enc.y_stack_screw_length_tolerance
        air=tip-pilot.zmin-enc.y_stack_screw_length_tolerance
        records.append({'check':f'Raised upper M5 host at X{cx:g}',
            'passed':missing_stock<.001 and missing_floor<.001 and pilot_blockage<.001
                     and reach>=enc.floor_heatset_depth and air>=.5,
            'screw_length_mm':length,'head_seat_z_mm':seat,
            'insert_top_z_mm':insert_top,'insert_length_mm':enc.floor_heatset_depth,
            'minimum_thread_reach_mm':reach,'minimum_blind_tip_air_mm':air,
            'missing_3mm_pilot_wall_mm3':missing_stock,
            'pilot_blocking_stock_mm3':pilot_blockage,
            'missing_3mm_blind_floor_mm3':missing_floor})
    sources=[SOURCE,FACTS,Path(__file__),Path(_scenes.__file__),
             ROOT/'hardware/manifold-layout/_scorecard.py',
             ROOT/'hardware/manifold-layout/above-core.json',
             Path(enc.__file__),Path(enc._above_core_shell.__file__),
             ROOT/'hardware/manifold-layout/above_core_wiring.py',_box_spec.ARTIFACT]
    sources.extend((ROOT/'hardware/reference/soda-rise-insulation/soda_rise_insulation.py',
                    ROOT/'hardware/reference/soda-rise-insulation/soda-rise-insulation.step',
                    Path(layout.__file__),Path(valve_seat.__file__),
                    ROOT/'hardware/reference/beduan-solenoid/beduan_solenoid.py'))
    result={'passed':all(row['passed'] for row in records),
            'scope':'Sampled nominal empty-closure removal after removing the funnel silicone, cover and cradled drain group, back-top upper stock and its named fixed equipment plus native fluid spans with both endpoints on that fixed group during the populated-core ride, and bare valve installation on the open-bench core. The inlet header and its three concealed links are preassembled with the stationary core while the open saddles capture it; permanent installed ownership is unchanged. V-A lowers at the real socket-depth axial offset and seats before V-K; PCB, PSU, pump, meter, electrical junctions, inserted valve elbows and warm tubes install after both bare valves. Full printed core stock and internal equipment remain. Valve lowering uses continuous conservative bounds; seating uses native sampled poses. Closure screws are removed. Drain disconnection or cradle release is a prerequisite; their motion and force are not queried. Soda/drain rear bulkheads, their nuts and the nested meter return elbows install after the column ride. Other inter-quadrant tubes/leads are connected after the ride. Lower seams and floors retain their separate records.',
            'late_rear_components':sorted(late_rear),
            'stationary_core_inlet_header_preassembly':sorted(header_preassembly),
            'evidence_limit':'Closure/column motions use tessellated native geometry with a 0.1 mm3 reporting threshold; valve installation uses full native shapes with 1e-6 mm Boolean tolerance and 1e-6 mm3 reporting threshold. No physical fit, installation force, hand/tool access, printed stiffness, insert strength, sealing or lifetime result.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'checks':records}
    OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
