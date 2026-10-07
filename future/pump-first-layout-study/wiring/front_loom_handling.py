"""Constant-cut-length front contact lead handling before final wire dressing.

The display remains out during the front closing slide. Its existing ridge
passage and open display pocket carry the unplugged contact lead's temporary
tail. The contact half and its insulated joints stay on the front subassembly.
No selected installed control body or cutter is replaced.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent;STUDY=HERE.parent;ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
import audit,baseline
from native_harness import sweep,bounds,broad
from circular_clearance import paired_members
from evidence_binding import content_sha256,manifest_content_sha256
from structure.received_native import ReceivedNative

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

RAIL_ENTRY_TRAVEL_MM=102.2

def continuous_translation_air(moving,fixed,travel):
    """Prove complete interval clearance with a native distance lower bound.

    Euclidean distance to a fixed body is 1-Lipschitz under translation. A
    native midpoint distance greater than an interval's half-width therefore
    proves separation at every pose in that interval, rather than only at the
    sampled midpoint. Actual positive commons always reject the interval.
    """
    pending=[(0.,travel)];leaves=[];failures=[];samples=[]
    while pending:
        low,high=pending.pop();mid=(low+high)/2.;half=(high-low)/2.
        body=moving.translate((0,-mid,0));gap=body.distance(fixed)
        volume=audit.common(body,fixed) if gap<1e-5 else 0.
        samples.append({'travel_fore_mm':mid,'native_gap_mm':gap,'common_mm3':volume})
        if volume>.001:
            failures.append({'interval_mm':[low,high],'travel_fore_mm':mid,'common_mm3':volume});break
        bound=gap-half
        if bound>1e-5:
            leaves.append({'interval_mm':[low,high],'midpoint_native_gap_mm':gap,
                           'translation_distance_bound_mm':half,'continuous_air_lower_bound_mm':bound})
        elif half<.0001:
            failures.append({'interval_mm':[low,high],'reason':'No positive continuous air lower bound'});break
        else:pending.extend([(low,mid),(mid,high)])
    leaves.sort(key=lambda r:r['interval_mm'][0])
    covered=sum(r['interval_mm'][1]-r['interval_mm'][0] for r in leaves)
    return {'method':'Exact native midpoint distance minus the full interval translation radius; 1-Lipschitz distance bound',
            'sampled_distances':samples,'proved_intervals':leaves,'covered_travel_mm':covered,
            'failures':failures,'pass':not failures and abs(covered-travel)<1e-8}

def front_inventory(models,records,changed):
    """Load retained front bodies and return the factory occupancy classes.

    The caller's scene dictionaries are extended with retained native members.
    No motion report is read, so the closing checker can consume this helper
    and its independent parked-lead receipt without an evidence cycle.
    """
    retained=baseline.prepare()
    front_members={n for n in retained['parts'] if n.startswith((
        'tee-y-','valve-v-','coil-v-','turn-fluid-',
        'enclosure-tee-carrier-','tee-carrier-spring-',
        'enclosure-window-cover-')) and n not in changed
        and records.get(n,'retained') is not None}
    front_members.update({'wago-mana','wago-manb','display','display-cover',
                          'display-gasket','pump-contact-male'})
    front_members.update('tube-fluid-'+str(i) for i in [9,10,11,12,13,17,19,20,21,22,23,27])
    for name in front_members:
        if name in models or name not in retained['parts']:continue
        source=retained['parts'][name]
        records[name]={'brep':str((baseline.CACHE/source['file']).relative_to(ROOT)),
                       'role':'retained front-top manifold or display'}
        models[name]=cq.Shape.importBrep(str(ROOT/records[name]['brep']))
    moving={'enclosure-front-top','funnel-frame','elbow-cradle',
            'funnel-drain-union','funnel-drain-stub','tube-fluid-4',
            'j13-front-stowed','control-loom-J13-retained-cartridge-loom-target'}
    moving.update(front_members)
    deferred={'tube-fluid-24','tube-fluid-14','tube-fluid-18','tube-fluid-28',
              'control-loom-J1-control-manifold-aft-fanout',
              'control-loom-J2-control-manifold-aft-fanout'}
    paths=[STUDY/f/'candidate.json' for f in ['funnel','pump','routing','structure','mounts','wiring']]
    paths.extend([STUDY/'mounts/water5-hosts.json',STUDY/'routing/tube-hosts.json'])
    manifests={};raw_inputs={}
    for path in paths:
        if not path.exists():continue
        raw=path.read_bytes();value=json.loads(raw);key=str(path.relative_to(ROOT))
        manifests[key]=content_sha256(value);raw_inputs[key]=hashlib.sha256(raw).hexdigest()
        for field in ['front_shell_fuse_part_names','front_carried_part_names','frame_fuse_part_names']:
            moving.update(value.get(field,[]))
        deferred.update(value.get('factory_deferred_part_names',[]))
    absent={'display','display-cover','display-gasket','funnel','funnel-cover',
            'control-loom-J13-retained-cartridge-loom','control-header-J13-fanout',
            'control-loom-J13-retained-cartridge-loom-source',
            'control-loom-J9-retained-display-loom','control-header-J9-fanout',
            'control-loom-J9-retained-display-loom-source',
            'control-loom-J9-retained-display-loom-target'}
    moving-=absent
    fixed=set(models)-moving-deferred-absent
    return {'moving':moving,'fixed':fixed,'deferred':deferred,'absent':absent,
            'required_rail_entry_travel_mm':RAIL_ENTRY_TRAVEL_MM,
            'manifest_content_sha256':manifests,'read_time_manifest_sha256':raw_inputs}

def main():
    sources={str(p.relative_to(ROOT)):sha(p)for p in [Path(__file__),HERE/'native_harness.py',
        HERE/'circular_clearance.py',STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py',
        STUDY/'structure/received_native.py',STUDY/'inputs/baseline.json',ROOT/'hardware/assembly/enclosure-mechanical.md',
        ROOT/'hardware/assembly/cable-assemblies.md']}
    models,records,changed,_,collected=audit.collect()
    manifests=dict(collected.content_sha256);raw_inputs=dict(collected)
    def read(path):
        raw=path.read_bytes();key=str(path.relative_to(ROOT));value=json.loads(raw)
        manifests[key]=content_sha256(value);raw_inputs[key]=hashlib.sha256(raw).hexdigest()
        return value
    controls=read(HERE/'controls-candidate.json')
    name='control-loom-J13-retained-cartridge-loom';route=controls['control_routes'][name]
    inventory=front_inventory(models,records,changed)
    manifests.update(inventory['manifest_content_sha256'])
    raw_inputs.update(inventory['read_time_manifest_sha256'])
    moving=inventory['moving'];absent=inventory['absent']
    front={n:models[n]for n in moving if n in models}
    fixed={n:models[n]for n in inventory['fixed']}
    native_inputs={}
    for n in list(front)+list(fixed):
        r=records[n];raw=(ROOT/r['brep']).read_bytes()
        native_inputs[n]={'brep':r['brep'],'sha256':hashlib.sha256(raw).hexdigest()}
        target=front if n in front else fixed;target[n]=cq.Shape.importBrep(BytesIO(raw))
    native_inputs[name]={'brep':controls['parts'][name]['brep'],'sha256':sha(ROOT/controls['parts'][name]['brep'])}
    D=route['diameter_mm'];R=route['radius_mm'];cut_length=route['length_mm']
    points=[[0,102.236,276.4256262237512],[0,112,276.4256262237512],[0,112,301],
        [62,112,301],[62,98.5,301],[90,98.5,301],[90,122,301],[90,122,286],
        [90,143,286],[48.55,143,293.9],[48.55,100.815,293.9],[48.55,100.815,317.1],
        [61.5,100.815,317.1],[61.5,100.815,305.5045573971231],
        [61.5,110.30849207671874,305.5045573971231],[32,110.30849207671874,305.5045573971231],
        [32,92,305.5045573971231],[32,65,318],[32,-80,318]]
    authored,length=sweep(points,D,R)
    points[-1][1]-=cut_length-length['length_mm']
    authored,length=sweep(points,D,R)
    physical,_,section=paired_members(authored,D,gap=0.,fuse_clearance=False)
    path=ROOT/'.cache/pump-first-layout/wiring/front-handling/j13-front-stowed.brep'
    held_report=json.loads((HERE/'front-loom-handling.json').read_bytes())
    held_record=held_report['parts']['j13-front-stowed']
    held_bytes=path.read_bytes()
    received=ReceivedNative(ROOT,{'parts':{'j13-front-stowed':held_record}})
    physical=received.shape('j13-front-stowed',physical)
    parity=received.checks[-1]
    conservation=[]
    for direction in ['analytic_material_in_received','received_material_in_analytic']:
        accepted=next(r for r in parity[direction]['attempts']if r['pass'])
        rows=accepted['source_solids']
        expected=sum(r['source_volume_mm3']for r in rows)
        present=sum(r['independent_common_volume_mm3']for r in rows)
        error=sum(r['material_error_mm3']for r in rows)
        conservation.append({'direction':direction,'complete_source_volume_mm3':expected,
            'complete_independent_common_volume_mm3':present,
            'aggregate_absolute_material_error_mm3':error,
            'pass':abs(expected-present)<.001 and error<.001})
    parity['complete_material_conservation']=conservation
    parity['pass']=parity['pass']and all(r['pass']for r in conservation)
    if not parity['pass']:raise ValueError('Received parked article lacks complete bidirectional material parity')
    native_inputs.update(received.inputs)
    origin=cq.Vector(*points[0]);required=cq.Vector(*route['to_dock']['point'])
    normal=cq.Vector(*route['to_dock']['axis']).normalized()
    axis=(cq.Vector(*points[1])-origin).normalized()
    checks=[parity,{'test':'Complete modeled installed J13 grouped-run length is preserved by the parked article',
        'modeled_installed_run_length_mm':cut_length,'parked_run_length_mm':section['complete_length_mm'],
        'pass':abs(cut_length-section['complete_length_mm'])<1e-6},
        {'test':'Retained contact passage docking position and normal remain unchanged',
        'point_mm':points[0],'normal_axis_dot':axis.dot(normal),
        'pass':(origin-required).Length<1e-6 and axis.dot(normal)>1.-1e-8},
        {'test':'Exact physical members and tangent section continuity',
        'physical_section_proof':section,'pass':all(r['pass']for r in section['physical_member_self_checks'])
        and all(r['pass']for r in section['tangent_full_section_seams'])}]
    b=bounds(physical)
    for part,body in front.items():
        if not broad(b,bounds(body),.0001):continue
        v=audit.common(physical,body)
        checks.append({'test':'Parked contact lead clears its carried front subassembly',
            'part':part,'common_mm3':v,'air_mm':physical.distance(body),'pass':v<.001})
    travel=inventory['required_rail_entry_travel_mm']
    prism=cq.Solid.makeBox(b[3]-b[0],b[4]-b[1]+travel,b[5]-b[2],
        cq.Vector(b[0],b[1]-travel,b[2]))
    continuous=[]
    for part,body in fixed.items():
        if not broad(bounds(prism),bounds(body),.0001):continue
        v=audit.common(prism,body)
        if v<.001:
            continuous.append({'test':'Complete parked article bounding prism clears fixed hardware over the full stroke',
                'part':part,'common_mm3':v,'pass':True})
        else:
            proof=continuous_translation_air(physical,body,travel)
            continuous.append({'test':'Complete physical parked article continuously clears the fixed body',
                'part':part,'bounding_prism_common_mm3':v,'continuous_native_distance_proof':proof,'pass':proof['pass']})
    checks+=continuous
    if path.read_bytes()!=held_bytes:raise ValueError('Received parked article changed during its assembly proof')
    drift=[n for n,r in native_inputs.items()if sha(ROOT/r['brep'])!=r['sha256']]
    drift+=[n for n,h in sources.items()if sha(ROOT/n)!=h]
    manifest_drift=[n for n,h in manifests.items()if manifest_content_sha256(ROOT/n)!=h]
    report={'parts':{'j13-front-stowed':dict(held_record)},
        'points_mm':points,'diameter_mm':D,'radius_mm':R,'length_mm':section['complete_length_mm'],
        'checks':checks,'continuous_relative_travel_mm':[0,travel],'continuous_swept_containing_prism_bounds':bounds(prism),
        'front_carried_part_names':['j13-front-stowed','control-loom-J13-retained-cartridge-loom-target'],
        'absent_during_closing':sorted(absent),'display_after_closing':['display','display-gasket','display-cover'],
        'moving_names':sorted(moving),'fixed_names':sorted(fixed),'deferred_names':sorted(inventory['deferred']),
        'inventory_scope':'Every current fixed native body is retained for the parked article prism; no fore/lower crop is applied.',
        'installed_route_names_unchanged':[name,'control-loom-J9-retained-display-loom'],
        'procedure':['Prepare and insulate the contact male solder joints at the unpowered loose front-top EN-10 stage; preserve the existing contact bore, marked orientation, fasteners and retaining clip.',
            'Keep the display, its gasket and cover out. Leave the labeled J13 board end free; form and hold the shown constant-length modeled bare outer loop on the same front article, through the existing 14.7 mm ridge passage and empty display pocket.',
            'Carry the parked article with front-top/frame through the full 102.2 mm closing stroke. Every point follows the same rigid translation, preserving length, bend radius and the retained contact normal.',
            'Keep the rear roof hatch seated for the previously dressed ground hook feed. With the silicone funnel and display absent after closing, release the free J13 tail for make-up through those open apertures. Its unchanged installed route and existing four-position XH board termination are the final occupancy target. Install the display and J9 loom afterward through their retained ridge passage and screw inputs.'],
        'pass':all(r['pass']for r in checks) and not drift and not manifest_drift,
        'native_inputs':native_inputs,'source_inputs':sources,'read_time_manifest_sha256':raw_inputs,
        'manifest_content_sha256':manifests,'source_drift':drift,'manifest_drift':manifest_drift,
        'scope':'The complete counted grouped run has one constant-length native parked shape. Its retained front fanout and contact interfaces remain carried with the front. A complete containing prism proves every intermediate 102.2 mm translation against fixed native hardware; any intersected conservative prism receives an actual-body continuous native-distance bound over the whole travel. The display and its J9 loom are installed after closing.',
        'limits':['The modeled 4.3 mm outer section represents four 1.7 mm conductors. The 537.199 mm value is grouped-run geometry; it is not a finished wire cut or a claim that the inherited 350 mm DC-5 stock reaches. Stock-spool make-up includes the unchanged front fanout and individual board termination/service dressing. Constituent bends, final dressing manipulation, workholding, crimp/connector insertion and loaded retention remain physical qualifications.',
                  'The free board end is a bare dressing interface, with the existing XH housing made up after unstowing. No inline connector or altered contact solder joint is introduced.',
                  'The selected rear roof hatch stays seated during front closure and subsequent lead make-up. Final manual J9/J13 dressing, XH insertion and retention through the open funnel/display apertures have no tool-access or manipulation qualification in this receipt.',
                  'The native parked run has 0.043 mm minimum front-shell air within the retained chase and 0.802 mm frame air. Zero geometric common is established; printed tolerance and manipulation effort are not qualified.']}
    (HERE/'front-loom-handling.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'checks':len(checks),'failures':[r for r in checks if not r['pass']],
        'source_drift':drift,'manifest_drift':manifest_drift,'points_mm':points,'length_mm':report['length_mm']},indent=2),flush=True)
    if not report['pass']:raise SystemExit(1)

if __name__=='__main__':main()
