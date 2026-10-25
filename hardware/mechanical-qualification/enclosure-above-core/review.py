"""Manual funnel closure, inlet binding and upper-joint query against the exported machine.

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
                 'funnel-frame'):
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
    import cadquery as cq
    sys.path.insert(0,str(ROOT/'hardware/manifold-layout'))
    import _realized
    facts=json.loads(FACTS.read_text())
    if facts['step'] != _realized.code_digest(SOURCE):
        raise ValueError('Closure review requires facts from this exact exported STEP')
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
    sources=[SOURCE,FACTS,Path(__file__),
             ROOT/'hardware/manifold-layout/_scorecard.py',
             ROOT/'hardware/manifold-layout/above-core.json',
             Path(enc.__file__),Path(enc._above_core_shell.__file__),
             ROOT/'hardware/manifold-layout/above_core_wiring.py',_box_spec.ARTIFACT]
    sources.extend((Path(soda_inlet.__file__),inlet_path,
                    ROOT/soda_inlet.HOLDER_ACCEPTANCE,ROOT/soda_inlet.FOAM_EVIDENCE,
                    ROOT/'hardware/manifold-layout/above_core.py',
                    ROOT/'hardware/reference/beduan-solenoid/beduan_solenoid.py'))
    result={'passed':all(row['passed'] for row in records),
            'scope':'Sampled nominal empty-frame removal after removing the funnel silicone, '
                    'cover and cradled drain group; the selected continuous-inlet artifact '
                    'binding; and raised upper M5 stock. Closure screws are removed. '
                    'The wall-carried back-top motion is read separately by wall_closing.py. '
                    'Lower seams and floors retain their separate records.',
            'evidence_limit':'Tessellated native closure geometry with a 0.1 mm3 reporting '
                    'threshold. No physical fit, installation force, hand/tool access, '
                    'printed stiffness, insert strength, sealing or lifetime result.',
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'checks':records}
    OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
    if not result['passed']:raise SystemExit(1)


if __name__=='__main__':main()
