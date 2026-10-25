"""Manual native counterexample and handoff query for the approved arrangement.

Run through tmp/takeover/cadq. This script reads production component poses and
selected exact tube sweeps; it never exports a production part or joins a build.
Positive native overlaps at named rail poses disprove that rigid closing path.
No negative sampled result certifies the complete path, hands or flexible leads.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT), str(HERE), str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/manifold-layout'),
               str(ROOT/'hardware/assembly/scenes'),
               str(ROOT/'hardware/printed-parts/electronics/pcba-tray')]
import cadquery as cq
import above_core as layout
import above_core_parts as parts
import above_core_routes as plumbing
import _scenes as scenes
from connector_service import recorded_witnesses


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def overlap(a, b):
    return all(a[i] < b[i+3]-1.e-7 and b[i] < a[i+3]-1.e-7 for i in range(3))


def signature(shape):
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
            'volume_mm3': volume(shape), 'bounds_mm': bounds(shape)}


def reading(a, b, finite=None):
    common = a.intersect(b)
    amount = volume(common)
    return {'common_mm3': amount,
            'outside_finite_mate_mm3': volume(common.cut(finite)) if finite is not None and amount else amount,
            'distance_mm': a.distance(b),
            'common_bounds_mm': bounds(common) if amount > 1.e-6 else None}


def cylinder(point, axis, depth, radius=3.175):
    return cq.Solid.makeCylinder(radius, depth, cq.Vector(*point), cq.Vector(*axis))


def shifted(point, axis, distance):
    return tuple(x+distance*d for x,d in zip(point,axis))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--electrical-only', action='store_true', help='Only the bounded source-wire consequence query using an existing native scene fixture')
    parser.add_argument('--scene-fixture', type=Path, default=ROOT/'tmp/above-core-electrical-fixture/index.json')
    parser.add_argument('--wiring-cache', type=Path, default=ROOT/'tmp/above-core-electrical-fixture/wiring/index.json')
    parser.add_argument('--lid', type=Path, help='Optional source-current world-frame lid BREP')
    parser.add_argument('--fixture-dir', type=Path, default=ROOT/'tmp/approved-carried-group')
    parser.add_argument('--output', type=Path, default=HERE/'approved-carried-group-review.json')
    args = parser.parse_args()
    if args.lid:
        args.lid = args.lid.resolve()
    args.fixture_dir.mkdir(parents=True, exist_ok=True)
    if args.electrical_only:
        electrical_review(args)
        return
    print('Build selected purchased components', flush=True)
    rows = parts.components()
    physical = {n: row[0] for n,row in rows.items()}
    physical['digiten-flow'] = parts.native_reference('digiten-flow').moved(layout.location('digiten-flow'))
    if args.lid:
        physical['foam-cap-lid-top'] = cq.Shape.importBrep(str(args.lid))
    specifications = parts.route_specs()
    selected_ids = ('above-core-va-under-head', 'above-core-water-in',
                    'above-core-vb-yb-cross', 'above-core-vb-yb-link')
    selected = {'tube-'+name: parts.route_shape(specifications[name]) for name in selected_ids}
    output = {'schema': 1, 'units': 'mm', 'frame': 'Production enclosure XYZ; Z up',
        'scope': 'Manual bounded native counterexample and finite-handoff query of the approved carried arrangement. No physical force, flexible-lead motion or complete-path clearance qualification.',
        'approved_carried_names': sorted(scenes.back_top_carried_names()),
        'separate_handoff_tubes': list(scenes.BACK_TOP_HANDOFF_TUBES),
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (
            Path(__file__), Path(parts.__file__), Path(layout.__file__), Path(plumbing.__file__),
            ROOT/'hardware/manifold-layout/above-core.json', Path(scenes.__file__),
            HERE/'connector_service.py', HERE/'flavor-and-connector-review.json',
            ROOT/'hardware/manifold-layout/studies/funnel-gate/assembly-ownership.json',
            ROOT/'hardware/manifold-layout/studies/funnel-gate/approved-arrangement.json')},
        'reference_sha256': {str(p.relative_to(ROOT)): sha(p) for p in set(parts.REFERENCES.values())},
        'lid_fixture': {'path': str(args.lid.relative_to(ROOT)), 'sha256': sha(args.lid)} if args.lid else None,
        'selected_native_components': {n: signature(s) for n,s in {**selected,
              'vb-outlet-return': physical['vb-outlet-return']}.items()}}
    def persist():
        args.output.write_text(json.dumps(output, indent=2)+'\n')
    persist()
    # One actual intermediate rail pose with a positive overlap is conclusive.
    # The chosen component pairs cross in Y and overlap in X/Z. This avoids a
    # costly sampled whole-machine scorecard after an obstruction is established.
    closing = []
    for moving, fixed in (('valve-v-a','psu'), ('vk-solenoid','digiten-flow'),
                          ('lower-pump-elbow','g-ganen-pump')):
        for travel in (0., 20., 50., 100., 150., 200., 237.5):
            body = physical[moving].translate((0.,travel,0.))
            if not overlap(bounds(body),bounds(physical[fixed])):
                continue
            row = {'moving': moving, 'stationary': fixed,
                   'offset_mm': [0.,travel,0.], **reading(body,physical[fixed])}
            closing.append(row)
            print('Rail pose', json.dumps(row), flush=True)
            if row['common_mm3'] > 1.e-6:
                for label, shape in ((moving+'-at-'+str(travel),body),(fixed,physical[fixed])):
                    shape.exportBrep(str(args.fixture_dir/(label+'.brep')))
                break
    output['rigid_back_top_counterexamples'] = closing
    output['rigid_back_top_path'] = {
        'offset_basis': 'Back-top starts aft of its installed pose and translates in -Y; offsets here are +Y from the installed pose.',
        'reviewed_travel_mm': [0.,237.5],
        'status': 'obstructed' if any(r['common_mm3'] > 1.e-6 for r in closing) else 'no_counterexample_in_named_pairs',
        'complete_path_tested': False,
        'scope': 'A positive native intersection is a counterexample to rigid travel of the full approved group. The limited named-pair search cannot establish a clear complete path.'}
    persist()
    import pcba_tray as pcb
    connector = json.loads((ROOT/'hardware/wiring/installed/connector-map.json').read_text())['connectors']['J10']
    witnesses = {}
    driver_datums = []
    for pin in connector['pins']:
        x,y = pin['xy_mm']
        point = layout.point(layout.pose('pcba'), (x-pcb._centre[0],y-pcb._centre[1],
                            pcb._thickness+connector['component_glb_bounds_mm'][5]))
        name = 'J10-'+pin['label']
        witnesses[name] = cylinder(point,(0.,0.,1.),355.-point[2],1.65)
        driver_datums.append({'name':name,'point_mm':point,'axis':[0.,0.,1.],
                              'diameter_mm':3.3,'roof_z_mm':355.})
    j11_stages, j11 = recorded_witnesses()['terminal-J11']
    witnesses['J11-complete-6up-6east-20up'] = j11
    for i, stage in enumerate(j11_stages):
        witnesses['J11-stage-'+str(i)] = stage
    return_group = {n:s for n,s in selected.items() if 'vb-yb' in n}
    return_group['vb-outlet-return'] = physical['vb-outlet-return']
    access = []
    for name, shape in return_group.items():
        for label, witness in witnesses.items():
            row = {'body':name,'witness':label,**reading(shape,witness)}
            access.append(row)
            if row['common_mm3'] > 1.e-6:
                print('Selected return access',json.dumps(row),flush=True)
    output['selected_return_access'] = {'drivers':driver_datums,'readings':access,
        'J11_prerequisites':'Remove funnel, removable frame and disconnected cradled drain assembly. Actual housing sweep is 6 mm up,6 mm east,20 mm up; flexible leads, latch, hand force and further extraction are unqualified.',
        'simultaneous_tool_occupancy_clear':all(r['common_mm3'] <= 1.e-6 for r in access),
        'sequence_scope':'Complete PCB power wiring before final B-return tube mating. A simultaneous driver collision alone does not reject the selected installed route.'}
    # Persist the exact current comparison geometry for an isolated reviewer.
    for name,shape in {**return_group,**witnesses,'pcba':physical['pcba']}.items():
        shape.exportBrep(str(args.fixture_dir/(name+'.brep')))
    persist()
    neighbors = []
    subjects = {**selected,'vb-outlet-return':physical['vb-outlet-return']}
    own = {n:set(specifications[n[5:]]['owners']) for n in selected}
    for name,shape in subjects.items():
        for other,body in physical.items():
            if other == name or other in own.get(name,set()):
                continue
            if not overlap(bounds(shape),bounds(body)):
                continue
            row = {'subject':name,'obstacle':other,**reading(shape,body)}
            neighbors.append(row)
            if row['common_mm3'] > 1.e-6:
                print('Selected native neighbor',json.dumps(row),flush=True)
    output['selected_native_neighbors'] = {'readings':neighbors,
        'scope':'Selected V-A under-head, ASSE supply and B return against current purchased neighbors and the optional source-current lid. Named tube endpoint owners are left to their finite receiving-interface review; this is not a blanket equipment exclusion.'}
    persist()
    # Fixed meter tube, moving rear elbow: the elbow mouth receives the free
    # tube tip over its full inferred 16.891 mm depth, exactly along column -Y.
    meter_pose = layout.pose('digiten-flow')
    mouth = layout.point(meter_pose,(30.5,0.,0.))
    meter_out = layout.vector(meter_pose['rotation'],(1.,0.,0.))
    rear_mouth,rear_axis = rows['soda-outlet-return-stem'][2](((0.,19.05,0.),(0.,1.,0.)))
    rear_depth = 16.891
    tube_spec = {'od_mm':6.35,'id_mm':4.24,'segments':[{'kind':'line','points_mm':[
        shifted(mouth,meter_out,-15.7),shifted(rear_mouth,rear_axis,-rear_depth)]}]}
    tube = parts.route_shape(tube_spec)
    receiving = []
    for advance in (rear_depth,12.,8.,4.,0.):
        host = physical['soda-outlet-return-stem'].translate((0.,advance,0.))
        host_mouth = shifted(rear_mouth,(0.,1.,0.),advance)
        mask = cylinder(host_mouth,tuple(-a for a in rear_axis),rear_depth)
        receiving.append({'remaining_y_stroke_mm':advance,**reading(tube,host,mask)})
    output['stationary_meter_tube_receiving'] = {'stationary_body':'tube-soda-meter-bulkhead',
        'moving_host':'soda-outlet-return-stem','stationary_meter_mouth_mm':mouth,
        'moving_host_installed_mouth_mm':rear_mouth,'moving_host_outward':rear_axis,
        'fixed_tube_free_tip_mm':shifted(rear_mouth,rear_axis,-rear_depth),
        'host_receiving_depth_mm':rear_depth,'meter_insertion_mm':15.7,
        'mouth_separation_mm':math.dist(mouth,rear_mouth),'readings':receiving,
        'scope':'Finite native containment of the stationary tube during named coaxial receiving poses. The tube remains inserted in the core meter; it does not travel with back-top. Receiving depth, sealing and force are inferred/unqualified.'}
    tube.exportBrep(str(args.fixture_dir/'stationary-soda-meter-bulkhead.brep'))
    # Pump-inlet mouths coincide when closed, but their common tube axis is
    # inclined; a -Y rail stroke is not the axial insertion direction.
    a,ua = rows['lower-pump-elbow'][2](((0.,19.05,0.),(0.,1.,0.)))
    b,ub = rows['pump-inlet-tpu'][2](((4.916132605004726,18.5,0.),(0.,1.,0.)))
    pump_tube = parts.route_shape(specifications['above-core-pump-inlet-link'])
    pump_rows = []
    for y in (0.,2.,4.,6.,10.,20.):
        host = physical['lower-pump-elbow'].translate((0.,y,0.))
        host_mouth = shifted(a,(0.,1.,0.),y)
        mask = cylinder(host_mouth,tuple(-c for c in ua),16.891)
        pump_rows.append({'remaining_y_stroke_mm':y,
            'transverse_axis_error_mm':abs(y)*math.sqrt(max(0.,1.-ua[1]**2)),
            **reading(pump_tube,host,mask)})
    output['pump_inlet_handoff'] = {'moving_elbow_mouth_mm':a,'fixed_tpu_mouth_mm':b,
        'moving_elbow_outward':ua,'fixed_tpu_outward':ub,
        'mouth_separation_mm':math.dist(a,b),'concealed_tube_length_mm':parts.route_wire(specifications['above-core-pump-inlet-link']).Length(),
        'elbow_receiving_depth_mm':16.891,'tpu_receiving_depth_mm':15.,
        'tube_axis_angle_to_positive_y_deg':math.degrees(math.acos(max(-1.,min(1.,ua[1])))),
        'fixed_tube_case':pump_rows,
        'automatic_rail_mating_supported':False,
        'scope':'Rigid fixed-tube diagnostic only. The closing stroke is not coaxial with either receiving socket. A specific final manual connection or released/staged member must be selected; no TPU deformation, over-insertion or blind auto-mating is claimed.'}
    # Late existing inlet cuff, with short tube already held in the back-top
    # elbow: inspect the real barb-axis stroke, rather than another -Y mate.
    tip,barb_axis = rows['pump-inlet-tpu'][2](((0.,0.,0.),(1.,0.,0.)))
    cuff = physical['pump-inlet-tpu']
    late = []
    for distance in (11.,8.,4.,2.,0.):
        offset = tuple(distance*c for c in barb_axis)
        moving_cuff = cuff.translate(offset)
        moving_mouth = tuple(b[i]+offset[i] for i in range(3))
        tube_mask = cylinder(moving_mouth,tuple(-c for c in ub),15.)
        for target,body,finite in (('preinserted-short-tube',pump_tube,tube_mask),
                                   ('lower-pump-elbow',physical['lower-pump-elbow'],None),
                                   ('g-ganen-pump',physical['g-ganen-pump'],None)):
            row = {'remaining_barb_stroke_mm':distance,'offset_mm':offset,
                   'obstacle':target,**reading(moving_cuff,body,finite)}
            late.append(row)
            if row['outside_finite_mate_mm3']>1.e-6:
                print('Late pump cuff',json.dumps(row),flush=True)
    output['late_pump_inlet_cuff'] = {'barb_tip_mm':tip,'barb_outward_axis':barb_axis,
        'barb_receiving_depth_mm':11.,'tube_receiving_depth_mm':15.,'readings':late,
        'tube_preinserted_in':'lower-pump-elbow',
        'scope':'Existing installed-envelope TPU cuff translated on the actual pump-barb axis with the short tube already seated in the back-top elbow. Bands are separate loose installation items; their screw housings, TPU stretch, hand access and flexible assembly motions are not modeled. A rigid interference does not predict TPU installation force.'}
    output['status'] = 'requires_sequence_resolution' if output['rigid_back_top_path']['status']=='obstructed' else 'bounded_review_complete'
    persist()
    print('Saved',args.output,output['status'],flush=True)


def electrical_review(args):
    """Reuse the existing native scene for source terminal frames, not wire curves.

    Prepare a fixture with above-core-review/review.py --pack-fixture
    --compose-only --export-wiring or aggregate_review.py --refresh-cache.
    The production routes are resolved anew; only native sweep candidates are
    built. Existing terminal housings come from the bound native wire cache.
    """
    from dataclasses import asdict
    from types import SimpleNamespace
    import enclosure_assembly as ea
    import above_core_wiring as junctions
    import manifold_layout as ml
    from hardware.wiring.installed.terminals import Attachments
    from hardware.wiring.installed.connections import connections
    from hardware.wiring.installed.routes import routed
    from hardware.wiring.installed.model import STOCK, shape
    from hardware.wiring.installed.bundles import circle, cross
    fixture = json.loads(args.scene_fixture.read_text())
    scene = {n:(cq.Shape.importBrep(str(args.scene_fixture.parent/f)),None)
             for n,f in fixture['parts'].items()}
    rows = parts.components()
    for n,(s,c,carry) in {**rows,**junctions.components()}.items():
        for key in [k for k in scene if k.rsplit('/',1)[-1]==n]:
            scene.pop(key)
        scene[n] = s,c
    meter = parts.native_reference('digiten-flow').moved(layout.location('digiten-flow'))
    scene['digiten-flow'] = meter,None
    at = Attachments(scene,ea)
    at.resolve()
    wires = {r.connection.id:r for r in routed(connections(),at)}
    route_rows = {n:r.record() for n,r in wires.items()}
    terminals = {n:asdict(t) for n,t in at.terminals.items()}
    # Exact arc extrema keep the broad-phase conservative without sweeping all
    # unchanged conductors merely to get their native boxes.
    def route_box(route):
        points = []
        for segment in route.segments:
            points.extend([segment['start_mm'],segment['end_mm']])
            if segment['kind']=='arc':
                centre,axis = circle(segment)
                radial = tuple(segment['start_mm'][i]-centre[i] for i in range(3))
                tangent = cross(axis,radial)
                angle = segment['angle_radians']
                for k in range(3):
                    t = math.atan2(tangent[k],radial[k])
                    for candidate in (t,t+math.pi,t+2*math.pi,t-math.pi):
                        if 0. <= candidate <= angle:
                            points.append(tuple(centre[j]+radial[j]*math.cos(candidate)+tangent[j]*math.sin(candidate) for j in range(3)))
        radius = STOCK[route.connection.stock]['od_mm']/2.+1.e-6
        return [min(p[i] for p in points)-radius for i in range(3)]+[max(p[i] for p in points)+radius for i in range(3)]
    wire_boxes = {n:route_box(r) for n,r in wires.items()}
    native = {}
    def native_wire(n):
        if n not in native:
            native[n] = shape(wires[n],STOCK[wires[n].connection.stock]['od_mm'])
        return native[n]
    # Resolve the exact current native tubes without composing an enclosure or
    # building the core/occupied-foam assembly.
    foam = parts._module('approved_wire_foam','printed-parts/cold-core/foam-assembly/foam_assembly.py')
    carries = {n:r[2] for n,r in rows.items()}
    carries['digiten-flow'] = parts._carry(layout.pose('digiten-flow'))
    for letter in 'efghij':
        carries['valve-v-'+letter] = lambda station:(ml.enclosure_point(station[0]),ml.enclosure_axis(station[1]))
    cap = layout.cap_lid_pose()
    def resolve(n,port):
        if n=='foam-assembly':
            xyz,axis = foam.cap_conduit_mouth(port)
            local = (-xyz[0],-xyz[1],xyz[2]-foam.foam_shell_outer_height-foam.top_cap_height)
            return layout.point(cap,local),layout.vector(cap['rotation'],(-axis[0],-axis[1],axis[2])),6.35
        return plumbing._station(carries,n,port)
    specifications = {**parts.route_specs(),**plumbing.route_specifications(resolve)}
    if plumbing.unresolved:
        raise ValueError(plumbing.unresolved)
    selected = {'tube-'+n:parts.route_shape(specifications[n]) for n in
        ('above-core-va-under-head','above-core-water-in','above-core-vb-yb-cross','above-core-vb-yb-link')}
    selected['vb-outlet-return'] = rows['vb-outlet-return'][0]
    record = {'schema':1,'units':'mm','scope':'Manual source-native consequence query: selected return/under-head/ASSE tubes versus all102 current source conductors and cached physical housings; restored C14 three conductors versus selected purchased equipment and all current native tube paths. No new build hook or physical wire qualification.',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (Path(__file__),
            ROOT/'hardware/manifold-layout/above-core.json',Path(parts.__file__),Path(plumbing.__file__),
            ROOT/'hardware/wiring/installed/routes.py',ROOT/'hardware/wiring/installed/route-overrides.json',
            ROOT/'hardware/wiring/installed/terminals.py',ROOT/'hardware/wiring/installed/bundle-routes.json')},
        'scene_fixture':{'path':str(args.scene_fixture.relative_to(ROOT)),'sha256':sha(args.scene_fixture)},
        'source_curve_sha256':{n:hashlib.sha256(json.dumps(r['segments'],sort_keys=True,separators=(',',':')).encode()).hexdigest() for n,r in route_rows.items()},
        'selected_plumbing_readings':[],'c14_readings':[],'source_conductor_count':len(wires),
        'selected_tube_specs':{n:specifications[n] for n in specifications if 'tube-'+n in selected},
        'simultaneous_access_scope':'Power wiring precedes final selected B-return tube mating. Tool occupancy and own attached-housing service motion have separate scopes.'}
    output = HERE/'approved-carried-wiring-review.json'
    def save():
        output.write_text(json.dumps(record,indent=2)+'\n')
    save()
    for name,body in selected.items():
        for n in wires:
            if not overlap(bounds(body),wire_boxes[n]):
                continue
            row = {'plumbing':name,'wire':n,**reading(body,native_wire(n))}
            record['selected_plumbing_readings'].append(row)
            if row['common_mm3']>1.e-6:
                print('Selected plumbing/wire',json.dumps(row),flush=True)
        save()
    wc = json.loads(args.wiring_cache.read_text())
    record['housing_cache'] = {'path':str(args.wiring_cache.relative_to(ROOT)),'sha256':sha(args.wiring_cache),
                               'aggregate_sha256':wc.get('aggregate_sha256')}
    for name,file in wc['parts'].items():
        if not name.startswith('terminal-'):
            continue
        body = cq.Shape.importBrep(str(args.wiring_cache.parent/file))
        for target,plumb in selected.items():
            if not overlap(bounds(body),bounds(plumb)):
                continue
            record['selected_plumbing_readings'].append({'plumbing':target,'housing':name,**reading(plumb,body)})
    tube_shapes = dict(selected)
    physical = {n:r[0] for n,r in rows.items()}
    physical.update({n:r[0] for n,r in junctions.components().items()})
    physical['digiten-flow'] = meter
    if args.lid:
        physical['foam-cap-lid-top'] = cq.Shape.importBrep(str(args.lid))
    for name in ('AC1-L','AC1-N','AC1-PE'):
        wire = native_wire(name)
        targets = dict(physical)
        for n,spec in specifications.items():
            radius = spec['od_mm']/2.
            pts = spec['points_mm']
            box = [min(p[i] for p in pts)-radius-1. for i in range(3)]+[max(p[i] for p in pts)+radius+1. for i in range(3)]
            if not overlap(bounds(wire),box):
                continue
            key = 'tube-'+n
            if key not in tube_shapes:
                tube_shapes[key] = parts.route_shape(spec)
            targets[key] = tube_shapes[key]
        ends = [at.terminals[k] for k in (wires[name].connection.start,wires[name].connection.end)]
        for target,body in targets.items():
            if not overlap(bounds(wire),bounds(body)):
                continue
            masks = [cq.Solid.makeSphere(8.5,cq.Vector(*t.point),angleDegrees1=-90.,angleDegrees2=90.)
                     for t in ends if t.part.rsplit('/',1)[-1]==target.rsplit('/',1)[-1]]
            finite = cq.Compound.makeCompound(masks) if masks else None
            row = {'wire':name,'obstacle':target,**reading(wire,body,finite)}
            record['c14_readings'].append(row)
            if row['outside_finite_mate_mm3']>1.e-6:
                print('C14 wire',json.dumps(row),flush=True)
        file = args.fixture_dir/('wire-'+name+'.brep')
        wire.exportBrep(str(file))
        record.setdefault('c14_native_source',{})[name] = {'path':str(file.relative_to(ROOT)),'sha256':sha(file),
            'valid':wire.isValid(),'length_mm':route_rows[name]['length_mm'],
            'start':terminals[wires[name].connection.start],'end':terminals[wires[name].connection.end]}
        save()
    record['native_conductors_built'] = {n:signature(s) for n,s in native.items()}
    record['complete'] = True
    record['contact_free'] = not any(r['outside_finite_mate_mm3']>1.e-6 for r in record['selected_plumbing_readings']+record['c14_readings'])
    save()
    print('Saved',output,'contact_free',record['contact_free'],flush=True)


if __name__ == '__main__':
    main()
