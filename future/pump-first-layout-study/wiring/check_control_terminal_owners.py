"""Received control members against their exact terminal owners.

Purchased bodies admit only the actual normal endpoint cylinder as a mate.
An explicitly named counted fanout can meet that cylinder's adjacent arc.
Every later return remains occupied against both owner types.
"""
from pathlib import Path
from io import BytesIO
import hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent; STUDY=HERE.parent; ROOT=STUDY.parents[1]
sys.path[:0]=[str(HERE),str(STUDY)]
import audit
from native_harness import bounds,broad
from power_harness import terminal_approach_members
from recover_power import analytic_sections
from evidence_binding import content_sha256,manifest_content_sha256

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def received_normal_approaches(physical,a,b,diameter):
    try:return terminal_approach_members(physical,a,b,diameter)
    except ValueError:
        # A selected tangent arc can begin at the dressing face. With no
        # straight member there is no owner waiver: its complete arc is tested.
        owners={};witnesses=[]
        for label,port in [('from',a),('to',b)]:
            point=cq.Vector(*port['point']);axis=cq.Vector(*port['axis']).normalized();matches=[]
            for index,member in enumerate(physical.Solids()):
                sections=analytic_sections(member,diameter)
                if len(sections)!=1 or sections[0]['kind']!='CYLINDER':continue
                section=sections[0]
                for start,end in [(section['a'],section['b']),(section['b'],section['a'])]:
                    if (start-point).Length>=1e-6:continue
                    dot=(end-start).normalized().dot(axis)
                    if dot>=1.-1e-8:
                        matches.append(index);witnesses.append({'endpoint':label,'owner':port['owner'],
                            'member':index,'mouth_mm':list(start.toTuple()),'normal_axis_dot':dot,
                            'normal_straight_length_mm':(end-start).Length,'diameter_mm':diameter,'pass':True})
            if len(matches)>1:raise ValueError('Ambiguous received terminal approach '+port['label'])
            if not matches:witnesses.append({'endpoint':label,'owner':port['owner'],'member':None,
                'mouth_mm':port['point'],'normal_axis':port['axis'],'no_straight_member_exemption':True,'pass':True})
            owners.setdefault(port['owner'],set()).update(matches)
        return owners,witnesses

def local_dressing_members(solids,port,diameter,normal_indices):
    """Only the arc sharing the actual normal stem, or tangent at its mouth."""
    point=cq.Vector(*port['point']);axis=cq.Vector(*port['axis']).normalized()
    sections=[analytic_sections(s,diameter)[0] for s in solids]
    anchors=[]
    for index in normal_indices:
        section=sections[index]
        anchors.append(section['b'] if (section['a']-point).Length<1e-6 else section['a'])
    candidates={}
    for index,section in enumerate(sections):
        if section['kind']!='TORUS':continue
        for start,end in [(section['a'],section['b']),(section['b'],section['a'])]:
            joined=any((start-anchor).Length<1e-6 for anchor in anchors)
            mouth=(start-point).Length<1e-6
            if not joined and not (not normal_indices and mouth):continue
            if mouth:
                c=section['centre'];mid=c+((start-c)+(end-c)).normalized()*section['radius']
                edge=cq.Edge.makeThreePointArc(start,mid,end)
                if edge.tangentAt(0).normalized().dot(axis)<1.-1e-8:continue
            candidates[index]={'member':index,'kind':'TORUS','shared_section_centre_mm':list(start.toTuple()),
                'shares_normal_stem_section':joined,'begins_tangent_at_actual_dressing_mouth':mouth}
    return candidates

def main():
    sources={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),HERE/'controls_looms.py',HERE/'controls.py',
        HERE/'power_harness.py',HERE/'recover_power.py',HERE/'native_harness.py',HERE/'circular_clearance.py',
        STUDY/'audit.py',STUDY/'baseline.py',STUDY/'evidence_binding.py']}
    models,records,_,_,collected=audit.collect()
    manifests=dict(collected.content_sha256);raw_inputs=dict(collected)
    def read(path):
        raw=path.read_bytes();key=str(path.relative_to(ROOT));value=json.loads(raw)
        manifests[key]=content_sha256(value);raw_inputs[key]=hashlib.sha256(raw).hexdigest()
        return value
    controls=read(HERE/'controls-candidate.json')
    records.update(controls['parts'])
    declared={frozenset(pair) for pair in controls.get('intended_contacts',[])}
    native_inputs={};loaded={}
    def receive(name):
        if name in loaded:return loaded[name]
        record=records[name];raw=(ROOT/record['brep']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if record.get('sha256') and record['sha256']!=digest:raise ValueError('Stale received terminal native '+name)
        native_inputs[name]={'brep':record['brep'],'sha256':digest}
        loaded[name]=cq.Shape.importBrep(BytesIO(raw))
        if not loaded[name].isValid():raise ValueError('Invalid received terminal native '+name)
        return loaded[name]
    # The current purchased valve packet contains casting and coil together.
    # The canonical blade net still names its coil subcomponent.
    installed_owners={'coil-v-a':'valve-v-a','coil-v-b':'valve-v-b'}
    checks=[];routes=[];failures=[]
    for name,route in controls['control_routes'].items():
        if 'from_dock' not in route:continue
        shape=receive(name);solids=shape.Solids();diameter=route['diameter_mm']
        receipt=route['physical_section_proof']
        if receipt['physical_sha256']!=native_inputs[name]['sha256'] or len(solids)!=len(receipt['members']):
            raise ValueError('Received physical-member receipt differs '+name)
        ownership,witnesses=received_normal_approaches(shape,route['from_dock'],route['to_dock'],diameter)
        endpoint_rows=[]
        for endpoint,keyfield in [('from_dock','from_keys'),('to_dock','to_keys')]:
            port=route[endpoint];nominal=port['owner']
            if nominal not in records:raise ValueError('Missing occupied nominal terminal owner '+nominal)
            actual={controls['ports'][key]['owner'] for key in route.get(keyfield,[]) if key in controls['ports']}
            installed={installed_owners.get(owner,owner) for owner in actual}
            owners=[(nominal,'nominal counted dressing region')]+[(owner,'canonical purchased or retained hardware')for owner in sorted(installed) if records.get(owner) is not None and owner!=nominal]
            unresolved=[owner for owner in sorted(installed) if records.get(owner) is None]
            indices=ownership[nominal]
            local=local_dressing_members(solids,port,diameter,indices)
            endpoint_rows.append({'endpoint':endpoint,'nominal_owner':nominal,'canonical_hardware_owners':sorted(actual),
                'installed_hardware_owners':sorted(installed),'unlocated_boundary_owners':unresolved,'normal_approach_member_indices':sorted(indices)})
            for owner,scope in owners:
                body=receive(owner)
                tested=[solid for index,solid in enumerate(solids)if index not in indices]
                remaining=cq.Compound.makeCompound(tested)
                overlap=audit.common(remaining,body) if broad(bounds(remaining),bounds(body),.0001) else 0.
                terminal=cq.Compound.makeCompound([solids[index]for index in sorted(indices)]) if indices else None
                mate_overlap=audit.common(terminal,body) if terminal is not None and broad(bounds(terminal),bounds(body),.0001) else 0.
                row={'control':name,'endpoint':endpoint,'owner':owner,'owner_scope':scope,
                    'exempt_normal_approach_member_indices':sorted(indices),'tested_member_count':len(tested),
                    'remaining_members_common_mm3':overlap,'normal_terminal_member_common_mm3':mate_overlap,
                    'strict_remaining_members_clear':overlap<=.001,'pass':overlap<=.001}
                if overlap>.001 and scope=='nominal counted dressing region':
                    contacts=[]
                    for index,member in enumerate(solids):
                        if index in indices or not broad(bounds(member),bounds(body),.0001):continue
                        common=audit.common(member,body)
                        if common<=.001:continue
                        region=member.intersect(body,tol=.0001)
                        contacts.append({'member':index,'common_mm3':common,'overlap_bounds_mm':bounds(region),
                            'local_arc_connection':local.get(index),'pass':index in local})
                    named=frozenset([name,owner]) in declared
                    row['nominal_endpoint_continuity']={'named_route_end_contact_declared':named,
                        'actual_dressing_mouth_mm':port['point'],'normal_axis':port['axis'],
                        'local_arc_connections':list(local.values()),'contacts':contacts,
                        'pass':named and bool(contacts) and all(c['pass'] for c in contacts),
                        'scope':'Only the immediate native arc sharing the terminal-normal stem section, or beginning tangent at the actual dressing mouth, can meet this named bare dressing region. Later members remain tested.'}
                    row['pass']=row['nominal_endpoint_continuity']['pass']
                checks.append(row)
                if not row['pass']:failures.append(row)
        routes.append({'control':name,'native_sha256':native_inputs[name]['sha256'],
            'received_physical_member_count':len(solids),'localized_terminal_approach_witnesses':witnesses,'endpoints':endpoint_rows})
        print('control terminal owners checked',name,flush=True)
    drift=[name for name,r in native_inputs.items()if sha(ROOT/r['brep'])!=r['sha256']]
    drift+=[name for name,digest in sources.items()if sha(ROOT/name)!=digest]
    manifest_drift=[name for name,digest in manifests.items()if manifest_content_sha256(ROOT/name)!=digest]
    report={'pass':len(routes)==26 and not failures and not drift and not manifest_drift,
        'required_grouped_routes':26,'completed_grouped_routes':len(routes),'checks':checks,'failures':failures,
        'routes':routes,'canonical_to_installed_owner_map':installed_owners,'native_inputs':native_inputs,'source_inputs':sources,'inputs_sha256':raw_inputs,
        'manifest_content_sha256':manifests,'source_drift':drift,'manifest_drift':manifest_drift,
        'strict_purchased_owner_pass':all(c['strict_remaining_members_clear'] for c in checks if c['owner_scope']=='canonical purchased or retained hardware'),
        'declared_local_nominal_continuity_count':sum('nominal_endpoint_continuity' in c for c in checks),
        'scope':'Every actual received control cylinder/arc is tested against its own counted source/target dressing region and canonical purchased or retained hardware. Purchased hardware exempts only the unique straight endpoint cylinder aligned with the terminal normal; all arcs and later returns remain tested. Named nominal bare dressing joins separately admit only their immediate shared-stem arc or tangent mouth arc, with exact common volumes, overlap bounds and native section adjacency. They never waive a purchased body or a later return. Unlocated lower interfaces retain named scope. Native byte, source and scene-content bindings establish the receipt; no native part is written.'}
    (HERE/'control-terminal-owner-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'pass':report['pass'],'routes':len(routes),'checks':len(checks),'failures':failures,
        'source_drift':drift,'manifest_drift':manifest_drift}),flush=True)

if __name__=='__main__':main()
