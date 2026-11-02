"""Rear inlet header, pump joints and integral snap seats in appliance coordinates.

Purchased profiles retain their own reference frames. The shared production
specification places every fitting and defines the short flexible pump joints;
no exploratory assembly or exported study is a build input.
"""
from functools import cache
import math
import json
from pathlib import Path

import cadquery as cq
import numpy as np

import above_core as layout


def plan():
    return layout.specification()['rear_plumbing']


def reference(name, path):
    import above_core_parts as parts
    return parts._module('rear_' + name, path)


def chain():
    return reference('threaded_chain', 'reference/asse1022-threaded-chain/asse1022_threaded_chain.py')


def union_tee():
    return reference('union_tee', 'reference/jg-pp0208e-tee/jg_pp0208e_tee.py')


def check():
    return reference('acvus', 'reference/neofit-acvus44-check/neofit_acvus44_check.py')


def joint():
    return reference('pump_joint', 'reference/pump-barb-joint/pump_barb_joint.py')


def _placed(shape, frame, color):
    import above_core_parts as parts
    carry = parts._carry(frame)
    return shape.moved(carry.where), color, carry


def _world(shape, color):
    import above_core_parts as parts
    return shape, color, parts._carry(parts._frame())


def _discharge_pvc(end_frame):
    """The two seated cuff ends meet on their shared bend's bisecting plane."""
    pj = joint()
    direction = np.array(end_frame['rotation'],float)[:,0]
    angle = math.acos(float(np.clip(direction[0],-1.,1.)))
    axis = np.cross((1.,0.,0.),direction)
    axis /= np.linalg.norm(axis)
    radial = direction.copy()
    radial[0] = 0.
    radial /= np.linalg.norm(radial)
    pivot = cq.Vector(*(-pj.pivot('discharge')[2]*radial))
    half = (cq.Location(pivot)
            * cq.Location(cq.Vector(),cq.Vector(*axis),math.degrees(angle)/2.)
            * cq.Location(-pivot))
    crease = cq.Solid.makeBox(100.,200.,200.,cq.Vector(-100.,-100.,-100.)).moved(half)
    rows = pj.bore('discharge')
    past = pj.TUBE_OD*math.tan(angle/2.)+1.
    on_barb = pj.turned(rows[:-2]+[(past,rows[-3][1])]).intersect(crease)
    on_stem = pj.turned([(-past,rows[-1][1]),rows[-1]]).moved(
        layout.frame_location(end_frame)).cut(crease)
    return on_barb.fuse(on_stem).clean()


@cache
def components():
    import above_core_parts as parts
    from _materials import M_BRASS, M_JG_BLACK_PP, M_NEOFIT_WHITE_ACETAL
    data, tc, pj = plan(), chain(), joint()
    result = {}
    names = {'pp010822e': 'bulkhead-water', 'gagira': 'gagira-coupling',
             'pi4512f6s': 'jg-pi4512f6s', 'pp061208w': 'jg-pp061208w'}
    for native_name, shape in tc.parts().items():
        if native_name in names:
            result[names[native_name]] = _placed(shape, data['chain_frame'], tc.COLORS[native_name])
    result['water-split'] = _placed(union_tee().build_jg_pp0208e_tee().val(),
                                    layout.snapshot_pose('water-split'), M_JG_BLACK_PP)
    result['flow-regulator'] = _placed(parts.native_reference('flow-regulator'),
                                       layout.snapshot_pose('reg'), M_NEOFIT_WHITE_ACETAL)
    # The inlet release collet is the external CO2 station. Both pieces use
    # the regulator's native frame and together represent one purchased body.
    ranges = __import__('json').loads((parts.HW / 'reference/compact-inline-candidates/dimensions.json').read_text())['pisco_rvfup_quarter']['fitted_exterior']['component_ranges_mm']
    inlet, rest = [], []
    for solid in parts.native_reference('gas-regulator').Solids():
        target = inlet if ranges['inlet_collet'][0] <= solid.Center().z <= ranges['inlet_collet'][1] else rest
        target.append(solid)
    result['co2-inlet'] = _placed(parts._compound(inlet), data['gas_frame'], M_JG_BLACK_PP)
    result['gas-regulator'] = _placed(parts._compound(rest), data['gas_frame'], M_JG_BLACK_PP)
    result['gas-check'] = _placed(check().build(), data['gas_check_frame'], M_NEOFIT_WHITE_ACETAL)
    result['discharge-chain'] = _placed(check().build(), layout.pose('discharge-chain'), M_NEOFIT_WHITE_ACETAL)

    # Suction: one swept PVC bend joins the unchanged barb seating length to
    # the reducer stem. The reducer and its clamp share the end tangent.
    j = data['joint']
    # Two tangent arcs accommodate the exposed shoulder land while the
    # measured barb and the receiving connector retain their own axes.
    suction = j['suction_bend']
    bend = layout.frame_location(suction['end_frame'])
    rows = pj.bore('suction')
    path = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(
        *(cq.Vector(*p) for p in segment['points_mm']))
        for segment in suction['segments']])
    span = cq.Workplane('YZ').circle(pj.TUBE_OD/2.).circle(pj.TUBE_ID/2.).sweep(path).val()
    tube = pj.turned(rows[:-2]).fuse(span, pj.turned([(0.,rows[-1][1]),(pj.TRIM,rows[-1][1])]).moved(bend)).clean()
    result['suction-tube'] = _placed(tube, data['suction-joint'], pj.M_PVC_CLEAR)
    result['suction-reducer'] = _placed(pj.build_reducer().moved(bend), data['suction-joint'], pj.M_JG_WHITE_PP)
    # A reducer's port frame follows its stem; its construction frame starts
    # at the trimmed stem tip, not the purchased reducer's original tip.
    result['suction-reducer'] = (result['suction-reducer'][0], result['suction-reducer'][1],
        parts._carry(parts._compose(data['suction-joint'], _datum(bend))))
    for name, (xc, diameter) in pj.bands('suction').items():
        steel, key = pj.build_clamp(diameter, xc, j.get('suction_stem_keys',j['suction_keys']) if name=='stem' else j['suction_keys'])
        if name=='barb':
            roll=cq.Location(cq.Vector(),cq.Vector(1,0,0),j['suction_barb_roll'])
            steel,key=steel.moved(roll),key.moved(roll)
        if name == 'stem':
            steel, key = steel.moved(bend), key.moved(bend)
        result['suction-'+name+'-clamp'] = _placed(steel, data['suction-joint'], pj.M_STAINLESS)
        result['suction-'+name+'-key'] = _placed(key, data['suction-joint'], pj.M_POM_ORANGE)
    discharge = j['discharge_bend']
    turn = layout.frame_location(discharge['end_frame'])
    result['discharge-tube'] = _placed(_discharge_pvc(discharge['end_frame']),
                                      data['discharge-joint'],pj.M_PVC_CLEAR)
    result['discharge-reducer'] = _placed(pj.build_reducer(),
        parts._compose(data['discharge-joint'],discharge['end_frame']),pj.M_JG_WHITE_PP)
    xc, diameter = pj.bands('discharge')['barb']
    steel, key = pj.build_clamp(diameter,xc,j['discharge_keys'])
    roll = cq.Location(cq.Vector(),cq.Vector(1.,0.,0.),j['discharge_barb_roll'])
    for name, shape, color in (('clamp',steel,pj.M_STAINLESS),('key',key,pj.M_POM_ORANGE)):
        result['discharge-barb-'+name] = _placed(shape.moved(roll),data['discharge-joint'],color)
    xc, diameter = pj.bands('discharge')['stem']
    steel, key = pj.build_clamp(diameter, xc, j['discharge_keys'])
    roll = cq.Location(cq.Vector(), cq.Vector(1.,0.,0.), j['STEM_ROLL'])
    for name, shape, color in (('clamp',steel,pj.M_STAINLESS),('key',key,pj.M_POM_ORANGE)):
        result['discharge-stem-'+name] = _placed(shape.moved(roll).moved(turn), data['discharge-joint'], color)
    return result


def _datum(location):
    trsf = location.wrapped.Transformation()
    return {'rotation': [[trsf.Value(i,j) for j in (1,2,3)] for i in (1,2,3)],
            'translation_mm': [trsf.Value(i,4) for i in (1,2,3)]}


def _arc_three(points):
    a,m,b = (np.array(p,float) for p in points)
    u,v = m-a,b-a
    normal = np.cross(u,v)
    centre = a+(float(u@u)*np.cross(v,normal)+float(v@v)*np.cross(normal,u))/(2.*float(normal@normal))
    normal /= np.linalg.norm(normal)
    start,end = a-centre,b-centre
    angle = math.atan2(float(np.cross(start,end)@normal),float(start@end))
    if angle<0.: angle+=2.*math.pi
    return {'kind':'arc','points_mm':[list(p) for p in points],
            'center_mm':centre.tolist(),'axis':normal.tolist(),
            'angle_rad':angle,'radius_mm':float(np.linalg.norm(start))}


def ports(name):
    data = plan()
    if name == 'bulkhead-water':
        p, u = chain().ports()['inlet']
        return {'outboard': (p,u,6.35), 'inboard':(p,tuple(-c for c in u),6.35)}
    if name in ('gas-regulator','co2-inlet'):
        return {'inlet':((0.,0.,0.),(0.,0.,-1.),6.35),
                'outlet':((0.,0.,62.814),(0.,0.,1.),6.35),
                'outboard':((0.,0.,0.),(0.,0.,-1.),6.35),
                'inboard':((0.,0.,62.814),(0.,0.,1.),6.35)}
    if name in ('gas-check','discharge-chain'):
        return {'inlet':(*check().stem_tip(),6.35), 'outlet':(*check().tube_port(),6.35),
                'tube-port':(*check().tube_port(),6.35)}
    if name == 'water-split':
        return {'supply':(*union_tee().branch(),6.35),
                'to-vk':(*union_tee().run(1),6.35),'to-flavor':(*union_tee().run(-1),6.35)}
    if name in ('suction-reducer','discharge-reducer'):
        mouth = joint().reducer.LENGTH-joint().CUT_X
        return {'tube':((mouth,0.,0.),(1.,0.,0.),6.35)}
    if name == 'jg-pp061208w':
        red = chain().parameters()['pp061208w']
        x = red['visible_axial_range_mm'][1]
        p = chain().placed(cq.Vertex.makeVertex(x,0.,0.),red).Center().toTuple()
        r = red['rotation']
        return {'tube':(p,tuple(row[0] for row in r),6.35)}
    return None


def snap_datums():
    """The integral rear seats' axes and supporting wall planes."""
    data=plan()
    c=layout.point(data['chain_frame'],(0.,0.,chain().bfp.BODY_CENTER_Z))
    p=layout.point(data['gas_frame'],(0.,0.,0.))
    return {'asse_axis':(c[0],c[2]), 'asse_turn':90., 'pisco_axis':(p[0],p[2]),
            'mouth_y':p[1], 'ceiling':346., 'rear':465.3, 'side':98.5}


def regulator_datums():
    """The measured water-regulator profile in the snap's local +Y frame."""
    import rear_snaps as snaps
    mount=plan()['regulator_mount']
    profile=json.loads((Path(__file__).resolve().parent.parent/
        'reference/yzmsz-water-regulator/reference-parameters.json').read_text())['profile_x_radius_mm']
    fit=mount['cavity_fit']
    pose=layout.snapshot_pose('reg')
    turn=np.array(((0.,1.,0.),(-1.,0.,0.),(0.,0.,1.)))
    frame={'rotation':(turn@np.array(pose['rotation'])).tolist(),
           'translation_mm':(turn@np.array(pose['translation_mm'])).tolist()}
    st=mount['station']
    half=st['inner']-snaps.ROOT_RADIUS-.5
    return dict(mount,profile_frame=frame,
        seat_profile=snaps.clearance_profile(profile,fit['receiver_radial_mm'],fit['axial_mm']),
        cap_profile=snaps.clearance_profile(profile,fit['cap_radial_mm'],fit['axial_mm']),
        cap_stock=[(st['axis_x']-half,st['axis_x']+half,st['y0'],st['y1'],
                    mount['cap_bottom'],mount['axis'][1])])


@cache
def seats():
    """Integral back-top stock and four removable snap caps."""
    import above_core_parts as parts
    import rear_snaps as snaps
    import fits
    selected = parts.components()
    aliases = {'jg-pp010822e':'bulkhead-water','multiplex-asse1022':'asse1022-assembly',
               'co2-check':'gas-check'}
    rows = {n: selected[aliases.get(n,n)][:2] for n in (*snaps.CHAIN,'co2-check','digiten-flow')}
    gas = selected['gas-regulator'][0]
    ranges = __import__('json').loads((parts.HW/'reference/compact-inline-candidates/dimensions.json').read_text())['pisco_rvfup_quarter']['fitted_exterior']['component_ranges_mm']
    native = parts.native_reference('gas-regulator')
    for n,(lo,hi) in ranges.items():
        group = [s for s in native.Solids() if lo <= s.Center().z <= hi]
        rows['pisco-'+n.replace('_','-')] = (parts._compound(group).moved(layout.frame_location(plan()['gas_frame'])), selected['gas-regulator'][1])
    meter = parts._module('rear_digiten','reference/digiten-flow-sensor/digiten_flow_sensor.py')
    d=snap_datums()
    result,numbers = snaps.build(rows,d['asse_axis'],layout.frame_location(plan()['chain_frame']),d['asse_turn'],
                           d['pisco_axis'],d['mouth_y'],d['ceiling'],d['rear'],d['side'],meter,layout.location('digiten-flow'))
    mount = regulator_datums()
    st, axis = mount['station'], mount['axis']
    a,b = mount['seat_y']; width = st['outer']
    b = max(b,st['y1']+fits.running+snaps.WALL)
    def room(name):
        return snaps.radial_profile(mount[name]).moved(layout.frame_location(mount['profile_frame']))
    seat = snaps.box(axis[0]-width,axis[0]+width,a,b,snaps.SPLIT,346.5).cut(room('seat_profile'))
    for pocket in snaps.pockets(st): seat = seat.cut(pocket)
    cap = snaps.cap(st,st['root'],mount['cap_bottom']).fuse(
        *(snaps.box(*bounds) for bounds in mount['cap_stock'])).cut(room('cap_profile'))
    result['regulator-seat'] = seat.clean().rotate((0,0,0),(0,0,1),90.)
    result['regulator-snap-cap'] = cap.clean().rotate((0,0,0),(0,0,1),90.)
    # Clear the installed vent sleeve and its two tie lands through the cap.
    sleeve = selected['asse-drain-adapter'][0]
    b = sleeve.BoundingBox()
    lo,hi = numbers['asse']['vent']
    vent_room = snaps.box(min(b.xmin,lo[0])-fits.running,max(b.xmax,hi[0])+fits.running,
                          min(b.ymin,lo[1]-snaps.THREAD)-fits.running,
                          max(b.ymax,hi[1]+snaps.THREAD)+fits.running,b.zmin-1.,328.)
    result['asse-snap-cap'] = result['asse-snap-cap'].cut(vent_room).clean()
    return result


def caps():
    from _materials import M_PETGF_BLACK
    if getattr(cq,'MESH',False):
        from _cadq_export import import_assembly
        path = Path(__file__).resolve().parent.parent/'printed-parts/enclosure/rear-equipment-caps/rear-equipment-caps-installed.step'
        return {name:_world(shape,M_PETGF_BLACK)
                for name,(shape,_color) in import_assembly(path).items()}
    return {name:_world(shape,M_PETGF_BLACK) for name,shape in seats().items() if name.endswith('snap-cap')}


def printable_cap(name, shape=None):
    """Stand the axial end down so each spring bends within the printed layers."""
    if shape is None:shape=seats()[name]
    axis=(0.,1.,0.) if name=='regulator-snap-cap' else (1.,0.,0.)
    shape=shape.rotate((0.,0.,0.),axis,90.)
    b=shape.BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2.,-(b.ymin+b.ymax)/2.,-b.zmin))


def route_specs():
    """Short quarter-inch tubes, ending at their actual receiving stops."""
    import above_core_parts as parts
    import above_core_routes as routes
    selected, result = parts.components(), {}

    def station(name, port):
        p,u,d = parts.port_stations(name)[port]
        return selected[name][2]((p,u))

    def add(name, segments, owners, radius=None):
        points = routes._points(segments)
        result[name] = {'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':6.35,'id_mm':4.32,'spool':'white','owners':list(owners),
            'from':owners[0],'to':owners[-1],'minimum_radius_mm':radius,
            'status':'complete_between_named_interfaces','basis':'Named receiving socket depths'}

    d = plan()['water_split_stub']
    a,m,b = d['points_mm']
    before = routes._sub(a,routes._mul(d['flow_in'],joint().reducer.TUBE_INSERTION_DEPTH))
    after = routes._add(b,routes._mul(d['flow_out'],union_tee().INSERTION))
    add('above-core-water-split-stub', [routes._line(before,a),_arc_three([a,m,b]),
        routes._line(b,after)], ('jg-pp061208w','water-split'),d['radius_mm'])
    for name, first, port_a, depth_a, second, port_b, depth_b in (
            ('tee-vk-link','water-split','to-vk',15.7,'tee-fold','socket',16.891),
            ('reg-va-link','flow-regulator','outlet',15.,'reg-va-elbow','socket',16.891),
            ('tee-regulator','water-split','to-flavor',15.7,'flow-regulator','inlet',15.),
            ('pump-inlet-link','suction-reducer','tube',joint().reducer.TUBE_INSERTION_DEPTH,
             'lower-pump-elbow','socket',parts.stem_elbow_reference().SOCKET_INSERTION)):
        flex = plan().get('flex_links', {}).get(name)
        if flex:
            if flex['kind'] == 'tangent_cubic':
                a,ua = station(first,port_a)
                b,ub = station(second,port_b)
                a = routes._sub(a,routes._mul(ua,depth_a))
                b = routes._sub(b,routes._mul(ub,depth_b))
                length = math.dist(a,b)
                control = [a,routes._add(a,routes._mul(ua,length/3.)),
                           routes._add(b,routes._mul(ub,length/3.)),b]
                # Derivative controls bound speed along the chord from below;
                # the two acceleration controls bound its norm from above.
                # Consequently curvature <= max_acceleration / min_speed².
                chord = [(b[i]-a[i])/length for i in range(3)]
                velocity = [[3.*(q[i]-p[i]) for i in range(3)]
                            for p,q in zip(control,control[1:])]
                speed = min(sum(v[i]*chord[i] for i in range(3)) for v in velocity)
                acceleration = max(math.sqrt(sum((6.*(r[i]-2.*q[i]+p[i]))**2
                                                  for i in range(3)))
                                   for p,q,r in zip(control,control[1:],control[2:]))
                radius = (speed*speed/acceleration if acceleration else None) if speed>0. else 0.
                add('above-core-'+name,[routes._bezier(control)],(first,second),radius)
                result['above-core-'+name]['radius_basis'] = 'Conservative derivative bound on the tangent cubic'
                continue
            segment = (_arc_three(flex['points_mm']) if flex['kind'] == 'arc'
                       else routes._bezier(flex['points_mm']))
            add('above-core-'+name, [segment], (first, second),
                flex['minimum_radius_mm'])
            continue
        a,ua = station(first,port_a); b,ub = station(second,port_b)
        points = parts._link(a,ua,depth_a,b,ub,depth_b)
        add('above-core-'+name,[routes._line(points[0],points[-1])],(first,second))
    return result


def continuations(station):
    """Water, gas, vent and flavor handoffs to the production core and manifold."""
    import above_core_routes as r
    result = {}

    def add(name, segments, source, destination, radius, *, spool='white', od=6.35, inside=4.32):
        points = r._points(segments)
        result[name] = {'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':od,'id_mm':inside,'spool':spool,'owners':[source[0],destination[0]],
            'from':'.'.join(source),'frm':'.'.join(source),'to':'.'.join(destination),
            'minimum_radius_mm':radius,'radius_mm':radius,'status':'selected_native_layout'}

    data = plan()['water5_bend']
    arcs = data['segments']
    a = arcs[0]['points_mm'][0]
    b = arcs[-1]['points_mm'][-1]
    inserted = r._sub(a,r._mul(data['flow'],check().INSERTION))
    segments = [r._line(inserted,a),*arcs]
    add('water-5',segments,('discharge-chain','outlet'),('foam-assembly','water-in'),
        data['radius_mm'])
    a,ua,_ = station('digiten-flow','outlet');b,ub,_ = station('bulkhead-carb','tube-in')
    add('soda-meter-bulkhead',[r._line(r._sub(a,r._mul(ua,15.7)),r._sub(b,r._mul(ub,12.7)))],
        ('digiten-flow','outlet'),('bulkhead-carb','tube-in'),None,spool='blue')

    gas = plan()['co2_tube']
    a = list(station('gas-check','outlet')[0]); top = gas['bend_foot']; floor = list(layout.specification()['gas_guide_world_mm'])
    da,db = gas['bend_tangents_mm']; pa,pb = gas['s_tangents_mm']
    c1 = [a,[a[0],a[1]-da,a[2]],[top[0],top[1],top[2]+db],top]
    c2 = [top,[top[0],top[1],top[2]-pb],[floor[0],floor[1],floor[2]+pa],floor]
    add('above-core-gas-core-drop',[r._line((a[0],a[1]+check().INSERTION,a[2]),a),r._bezier(c1),r._bezier(c2)],
        ('gas-check','outlet'),('foam-assembly','co2-in'),gas['minimum_radius_mm'],spool='red')

    # Full receiving straights and tangent bends through the occupied layout.
    add('above-core-va-fore-feed',layout.specification()['fore_routes']['native_segments']['va-fore-feed'],
        ('va-south-elbow','socket'),('ya-stem-elbow','socket'),14.)

    # The integral aft-facing socket keeps the LLDPE straight between the
    # downward vent and OVER. Its small lateral correction is a gentle cubic.
    a,ua,_ = station('asse-drain-adapter','tube');b,ub,_ = station('bulkhead-drain','inboard')
    span = b[1]-a[1]
    control = [a,r._add(a,r._mul(ua,span/3.)),r._add(b,r._mul(ub,span/3.)),b]
    add('drain-vent',[r._line(r._sub(a,r._mul(ua,14.)),a),r._bezier(control),
        r._line(b,r._sub(b,r._mul(ub,10.)))],('asse-drain-adapter','tube'),('bulkhead-drain','inboard'),25.,
        spool='drain-white',od=4.,inside=2.5)
    return result


def _flavor_s_bend(start, heading, offset, axis):
    import above_core_routes as r
    radius = 25.
    # Two equal opposite arcs restore the original tangent.
    distance = math.sqrt(sum(c*c for c in offset))
    angle = math.acos(1.-distance/(2.*radius))
    first,end = r._arc(start,heading,axis,angle,radius)
    u = np.array(heading,float); n = np.array(axis,float)
    tangent = math.cos(angle)*u+math.sin(angle)*np.cross(n,u)
    second,end = r._arc(end,tangent,tuple(-c for c in axis),angle,radius)
    return [first,second],end


def _flavor_rear(flavor, destination):
    """Shared descending bend, lower straight and rear socket approach."""
    import above_core_routes as r
    radius = 25.
    if flavor=='a':
        # Finish the descent ahead of the meter's complete lower spring.
        # The rear straight passes above that leaf, beneath the housing.
        start = (61.,369.5,276.5)
        low_z = 262.
        offset = (destination[0]-start[0],0.,low_z-start[2])
        normal = r._unit(r._cross((0.,1.,0.),offset))
        fall,low = _flavor_s_bend(start,(0.,1.,0.),offset,normal)
        rise = (0.,0.,destination[2]-low_z)
        angle = math.acos(1.-r._norm(rise)/(2.*radius))
        shift_start = (low[0],destination[1]-2.*radius*math.sin(angle),low_z)
        shift,stop = _flavor_s_bend(shift_start,(0.,1.,0.),rise,(1.,0.,0.))
        return [*fall,r._line(low,shift_start),*shift]
    peak, low_z = 303.5, destination[2]
    start = (35.,348.,peak)
    offset = (0.,0.,low_z-peak)
    normal = r._unit(r._cross((0.,1.,0.),offset))
    fall, low = _flavor_s_bend(start,(0.,1.,0.),offset,normal)
    offset = (destination[0]-low[0],0.,destination[2]-low_z)
    angle = math.acos(1.-r._norm(offset)/(2.*radius))
    shift_start = (low[0],destination[1]-2.*radius*math.sin(angle),low_z)
    normal = r._unit(r._cross((0.,1.,0.),offset))
    shift, stop = _flavor_s_bend(shift_start,(0.,1.,0.),offset,normal)
    return [*fall,r._line(low,shift_start),*shift]


def flavor_routes(station):
    """Two 4 mm dispense lines through the pump's east aisle, below the meter."""
    import above_core_routes as r
    result = {}
    radius = 25.

    for flavor, valve, lane, cross_y, aisle, cross_z, lift_y in (
            ('a','valve-v-g',-33.,266.,55.5,296.,291.),
            ('b','valve-v-j',-40.,274.,35.,293.,299.)):
        source,axis,_ = station(valve,'outlet')
        destination,outward,_ = station('bulkhead-flavor-'+flavor,'tube-in')
        if flavor=='a':
            lead = r._rounded([r._sub(source,r._mul(axis,10.)),source,
                (source[0],source[1],292.5),(35.,156.,288.5),(-45.,156.,288.5),(-45.,181.,288.5)],radius)
            lead_end = (-45.,181.,288.5)
        else:
            lead = r._rounded([r._sub(source,r._mul(axis,10.)),source,
                (source[0],source[1],288.5),(source[0],source[1]+radius,288.5)],radius)
            lead_end = (source[0],source[1]+radius,288.5)
        approach = (lane,cross_y-radius-10.,cross_z)
        lane_segments = [r._ease_lane(lead_end,approach)]
        if flavor=='b':
            offset = (lane-lead_end[0],0.,cross_z-lead_end[2])
            normal = r._unit(r._cross((0.,1.,0.),offset))
            lane_segments,approach = _flavor_s_bend(lead_end,(0.,1.,0.),offset,normal)
        crossing = r._rounded([approach,(lane,cross_y,cross_z),(aisle,cross_y,cross_z),
                                (aisle,lift_y,cross_z)],radius)
        peak,low_z = (276.5,262.) if flavor=='a' else (303.5,destination[2])
        offset = (5.5 if flavor=='a' else 0.,0.,peak-cross_z)
        normal = r._unit(r._cross((0.,1.,0.),offset))
        rise,end = _flavor_s_bend((aisle,lift_y,cross_z),(0.,1.,0.),offset,normal)
        rear = _flavor_rear(flavor,destination)
        stop = rear[-1]['points_mm'][-1]
        segments = [*lead,*lane_segments,*crossing,*rise,
                    r._line(end,rear[0]['points_mm'][0]),*rear,
                    r._line(stop,r._sub(destination,r._mul(outward,10.)))]
        points = r._points(segments)
        result['fluid-'+('18' if flavor=='a' else '28')] = {
            'segments':segments,'points_mm':points,'centerline_mm':points,
            'od_mm':4.,'id_mm':2.5,'spool':'flavor-black-4mm',
            'owners':[valve,'bulkhead-flavor-'+flavor],
            'from':valve+'.outlet','frm':valve+'.outlet','to':'bulkhead-flavor-'+flavor+'.tube-in',
            'minimum_radius_mm':radius,'radius_mm':radius,'status':'selected_native_layout'}
    return result
