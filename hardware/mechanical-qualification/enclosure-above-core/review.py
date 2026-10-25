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
    sys.path.insert(0,str(ROOT/'hardware/manifold-layout'))
    import soda_inlet
    inlet_path=Path(__file__).with_name('soda-inlet-review.json')
    inlet_receipt=json.loads(inlet_path.read_text())
    inlet_plan=soda_inlet.plan()
    inlet_components=[]
    for tail in ('tube-soda-core-rise','soda-bend-holder','soda-continuous-insulation'):
        shape=placed[name_for(tail)]
        low,high=bounds(shape)
        actual={'valid':shape.isValid(),'solids':len(shape.Solids()),
                'faces':len(shape.Faces()),'volume_mm3':shape.Volume(),
                'center_mm':list(shape.Center().toTuple()),
                'bounds_mm':[*low.tolist(),*high.tolist()]}
        expected=inlet_receipt['component_signatures'][tail]
        volume_tolerance=max(.001,abs(expected['volume_mm3'])*1e-7)
        differences={'volume_mm3':abs(actual['volume_mm3']-expected['volume_mm3']),
            'center_mm':max(abs(a-b) for a,b in zip(actual['center_mm'],expected['center_mm'])),
            'bounds_mm':max(abs(a-b) for a,b in zip(actual['bounds_mm'],expected['bounds_mm']))}
        passed=actual['valid'] and actual['solids']==expected['solids']
        passed &= actual['faces']==expected['faces']
        passed &= differences['volume_mm3']<=volume_tolerance
        passed &= differences['center_mm']<=1e-5 and differences['bounds_mm']<=1e-5
        if tail!='soda-continuous-insulation':
            passed &= actual['solids']==1
        inlet_components.append({'component':name_for(tail),'passed':bool(passed),
            'actual':actual,'fixture':expected,'absolute_differences':differences,
            'comparison_tolerances':{'volume_mm3':volume_tolerance,
                                     'center_mm':1e-5,'bounds_mm':1e-5}})
    records.append({'check':'Selected continuous soda inlet matches the native fit receipt',
        'passed':bool(inlet_receipt['passed'] and all(r['passed'] for r in inlet_components)),
        'receipt':str(inlet_path.relative_to(ROOT)),
        'receipt_sha256':hashlib.sha256(inlet_path.read_bytes()).hexdigest(),
        'components':inlet_components,
        'nominal_stock_mm':{'physical_piece_count':1,
            'cut_length':inlet_plan['foam_cut_mm'],
            'centerline_length':inlet_plan['nominal_foam_cut_length_mm'],
            'inside_diameter':inlet_plan['nominal_foam_id_mm'],
            'outside_diameter':inlet_plan['nominal_foam_od_mm']},
        'scope':'Artifact comparison to the linked native tube/holder/contact receipt. '
                'The occupied foam is an estimated compression display proxy; its native '
                'regions do not specify cuts or separate physical foam pieces. The full '
                'stock contacts and accepted qualitative physical evidence retain the '
                'receipt scope. No compression, force or thermal prediction.'})
    def query(label, moving_tail, poses, skip, moving_shapes=None, component_names=None,
              finite_mates=None):
        moving=name_for(moving_tail)
        offsets=np.asarray(poses,float)
        shapes={moving:placed[moving]} if moving_shapes is None else moving_shapes
        boxes={key:bounds(shape) for key,shape in shapes.items()}
        local_meshes={}
        sweep_low=np.min([low for low,high in boxes.values()],axis=0)+offsets.min(axis=0)
        sweep_high=np.max([high for low,high in boxes.values()],axis=0)+offsets.max(axis=0)
        hits=[]
        tested=[]
        mating_readings=[]
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
                    common=moving_mesh.translate(offsets[i])^obstacle
                    mate=(finite_mates or {}).get((key.split('/')[-1],tail))
                    if mate is not None:
                        raw=float(common.volume())
                        mate_mesh=mate['mesh']
                        if mate.get('moves_with_group'):
                            mate_mesh=mate_mesh.translate(offsets[i])
                        common=common-mate_mesh
                        mating_readings.append({'moving':key,'stationary':name,
                            'offset_mm':offsets[i].tolist(),'raw_common_mm3':raw,
                            'outside_finite_mate_mm3':float(common.volume())})
                    volumes[i]+=float(common.volume())
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
        if finite_mates:
            record['finite_mate_regions']=[
                {'moving_tail':pair[0],'stationary_tail':pair[1],
                 **{key:value for key,value in mate.items() if key!='mesh'}}
                for pair,mate in finite_mates.items()]
            record['finite_mate_readings']=mating_readings
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
    # The approved back-top equipment and its prepared plumbing ride together.
    # The core retains V-B, pump, PCB, PSU and the selected soda inlet.
    # Cross-owner handoffs need their own final-connection evidence.
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
    late_handoffs=frozenset(('tube-drain-vent', *_scenes.BACK_TOP_HANDOFF_TUBES))
    back_bodies=frozenset(name for name in _scenes.held_by('enclosure-back-top',ownership,
                         stop=('electronics-access-panel','funnel-frame','funnel','funnel-cover'))
                         if not name.startswith('tube-') and name not in late_handoffs)
    back_tails=set(back_bodies) | set(_scenes.back_top_carried_names())
    present_tails={name.split('/')[-1] for name in placed}
    missing_selected=set(_scenes.back_top_carried_names())-present_tails
    if missing_selected:
        raise ValueError(f'Approved back-top group is missing: {sorted(missing_selected)}')
    def endpoint_body(endpoint):
        candidates=[tail for tail in present_tails if endpoint==tail
                    or endpoint.startswith(tail+'.') or endpoint.startswith(tail+' ')]
        return max(candidates,key=len,default=None)
    for run in facts['native_runs']:
        if {endpoint_body(run['frm']),endpoint_body(run['to'])} <= back_bodies:
            back_tails.add('tube-'+run['id'])
    back_tails -= late_handoffs
    core_tails={n.split('/')[-1] for n,s in placed.items()
                if 'cold-core/' in n and bounds(s)[1][2]>253.3}
    core_tails.add('tube-soda-meter-bulkhead')
    upper=cq.Solid.makeBox(400,800,200,cq.Vector(-200,0,253.3))
    back_top=placed[name_for('enclosure-back-top')].intersect(upper)
    carried=[name for name,body in placed.items()
             if name.split('/')[-1] in back_tails
             and name.split('/')[-1]!='enclosure-back-top'
             and not name.split('/')[-1].endswith('-screw')
             and bounds(body)[1][2]>253.3]
    moving={name_for('enclosure-back-top')+' above Z253.3':back_top,
            **{name:placed[name] for name in carried}}
    import above_core as layout
    return_frame=layout.snapshot_pose('soda-outlet-return-stem')
    return_mouth=layout.point(return_frame,(0.,19.05,0.))
    return_axis=layout.vector(return_frame['rotation'],(0.,1.,0.))
    if return_axis != (0.,-1.,0.):
        raise ValueError('Finite rear capture requires the selected fore-facing socket')
    return_depth=16.891
    return_mask=mf.Manifold.cylinder(return_depth,3.175,circular_segments=512).rotate(
        (-90.,0.,0.)).translate(return_mouth)
    rear_mates={('soda-outlet-return-stem','tube-soda-meter-bulkhead'):{
        'mesh':return_mask,'moves_with_group':True,'mouth_world_mm':list(return_mouth),
        'inward_world':[0.,1.,0.],'depth_mm':return_depth,'radius_mm':3.175,
        'circular_segments':512,
        'scope':'Finite receiving cylinder travels with the back-top elbow. The concealed '
                'tube stays in the fixed meter. Nominal same-family receiving depth; '
                'no radial or axial enlargement.'}}
    query('Approved back-top upper stock and carried group over populated cold core',
          'enclosure-back-top',[(0,y,0) for y in (0,.25,.5,1,*range(2,302,2))],
          lambda n:n not in core_tails,moving_shapes=moving,
          component_names=[name_for('enclosure-back-top')+' above Z253.3',*carried],
          finite_mates=rear_mates)
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
    sources.extend((Path(soda_inlet.__file__),inlet_path,
                    ROOT/soda_inlet.HOLDER_ACCEPTANCE,ROOT/soda_inlet.FOAM_EVIDENCE,
                    ROOT/'hardware/manifold-layout/above_core.py',
                    ROOT/'hardware/reference/beduan-solenoid/beduan_solenoid.py'))
    result={'passed':all(row['passed'] for row in records),
            'scope':'Sampled nominal empty-closure removal after removing the funnel silicone, cover and cradled drain group; the approved back-top upper stock and named carried equipment/plumbing passing over the populated cold core; and raised upper M5 stock. V-A, V-K, their fitted elbows, low V-A feed and the complete inlet header travel with back-top. V-B, pump, PCB, PSU, meter and the continuous insulated soda inlet remain with the core. The concealed meter-outlet tube remains on the core. The explicitly listed cross-owner spans are omitted from the rigid-group motion and require separate final-connection evidence. This report does not establish those handoffs or bare-valve bench installation. Closure screws are removed. Lower seams and floors retain their separate records.',
            'late_handoff_components':sorted(late_handoffs),
            'approved_back_top_carried_components':sorted(back_tails),
            'evidence_limit':'Closure/column motions use tessellated native geometry with a0.1mm3 reporting threshold. No physical fit, installation force, hand/tool access, printed stiffness, insert strength, sealing or lifetime result. A clear rigid-group motion does not establish the final handoffs.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'checks':records}
    OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
