"""Rear inlet header, pump joints and integral snap seats in appliance coordinates.

Purchased profiles retain their own reference frames. The shared production
specification places every fitting and defines the short flexible pump joints;
no exploratory assembly or exported study is a build input.
"""
from functools import cache
import math
import json

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
    free, angle, lean = (j[k] for k in ('free', 'th', 'psi'))
    n = np.array([0., -math.sin(lean), -math.cos(lean)])
    def arc(t):
        a, r = angle*t, free/angle
        return r*math.sin(a)*np.array([1.,0.,0.])+r*(1.-math.cos(a))*n
    end, middle = arc(1.), arc(.5)
    bend = cq.Location(cq.Vector(*end)) * cq.Location(
        cq.Vector(), cq.Vector(*np.cross([1.,0.,0.], n)), math.degrees(angle))
    rows = pj.bore('suction')
    path = cq.Wire.assembleEdges([cq.Edge.makeThreePointArc(
        cq.Vector(), cq.Vector(*middle), cq.Vector(*end))])
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
    for name, (shape, color) in pj.build('discharge', (j['discharge_keys'],)*2, j['DISCHARGE_BEND']).items():
        if name in ('barb-clamp','barb-key'):
            shape=shape.moved(cq.Location(cq.Vector(),cq.Vector(1,0,0),j['discharge_barb_roll']))
        result['discharge-'+name] = _placed(shape, data['discharge-joint'], color)
    turn = pj.turn('discharge', j['DISCHARGE_BEND'])
    reducer = result['discharge-reducer']
    result['discharge-reducer'] = (*reducer[:2], parts._carry(parts._compose(data['discharge-joint'], _datum(turn))))
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
    result,_ = snaps.build(rows,(37.25,328.),layout.frame_location(plan()['chain_frame']),90.,
                           (77.5,328.),480.8,346.,465.3,98.5,meter,layout.location('digiten-flow'))
    mount = plan()['regulator_mount']
    st, axis = mount['station'], mount['axis']
    a,b = mount['seat_y']; width = st['outer']
    seat = snaps.box(axis[0]-width,axis[0]+width,a,b,snaps.SPLIT,346.5).cut(snaps.turned(mount['seat_runs'],axis))
    for pocket in snaps.pockets(st): seat = seat.cut(pocket)
    cap = snaps.cap(st,axis[1],mount['cap_bottom'],axis[1]).cut(snaps.turned(mount['cap_runs'],axis))
    result['regulator-seat'] = seat.clean().rotate((0,0,0),(0,0,1),90.)
    result['regulator-snap-cap'] = cap.clean().rotate((0,0,0),(0,0,1),90.)
    # Clear the installed vent sleeve and its two tie lands through the cap.
    sleeve = selected['asse-drain-adapter'][0]
    b = sleeve.BoundingBox()
    vent_room = snaps.box(b.xmin-fits.running,b.xmax+fits.running,
                          b.ymin-fits.running,b.ymax+fits.running,b.zmin-1.,328.)
    result['asse-snap-cap'] = result['asse-snap-cap'].cut(vent_room).clean()
    # The flavor-A tube crosses beneath the meter's housing. Its curved
    # passage opens only the lower snap wing, retaining the west spine.
    import above_core_routes as routes
    bulkhead = selected['bulkhead-flavor-a']
    source = parts._grid_module(next(r for r in parts._grid() if r['name']=='bulkhead-flavor-a'))
    destination,_ = bulkhead[2](source.port(-1.))
    segments = _flavor_rear('a', destination)
    path = parts.route_wire({'segments':segments})
    corridor = (cq.Workplane(cq.Plane(origin=segments[0]['points_mm'][0],normal=(0.,1.,0.)))
                .circle(2.5).sweep(path,isFrenet=False,clean=False).val())
    # Open the fore end of the lower wing beneath the descending tube. The
    # aft bearing and both spring catches retain their complete sections.
    corner = snaps.box(71.25,80.,396.,403.75,260.,267.)
    result['meter-snap-cap'] = result['meter-snap-cap'].cut(corridor,corner).clean()
    return result


def caps():
    from _materials import M_PETGF_BLACK
    return {name:_world(shape,M_PETGF_BLACK) for name,shape in seats().items() if name.endswith('snap-cap')}


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
    a,m,b = data['points_mm']
    guide = station('foam-assembly','water-in')[0]
    inserted = r._sub(a,r._mul(data['flow'],check().INSERTION))
    segments = [r._line(inserted,a),_arc_three([a,m,b])]
    if math.dist(b,guide)>1e-7: segments.append(r._line(b,guide))
    add('water-5',segments,('discharge-chain','outlet'),('foam-assembly','water-in'),14.)
    a,ua,_ = station('digiten-flow','outlet');b,ub,_ = station('bulkhead-carb','tube-in')
    add('soda-meter-bulkhead',[r._line(r._sub(a,r._mul(ua,15.7)),r._sub(b,r._mul(ub,12.7)))],
        ('digiten-flow','outlet'),('bulkhead-carb','tube-in'),None,spool='blue')

    gas = plan()['co2_tube']
    a = list(station('gas-check','outlet')[0]); top = gas['bend_foot']; floor = list(layout.specification()['gas_guide_world_mm'])
    da,db = gas['bend_tangents_mm']; pa,pb = gas['s_tangents_mm']
    c1 = [a,[a[0],a[1]-da,a[2]],[top[0],top[1],top[2]+db],top]
    c2 = [top,[top[0],top[1],top[2]-pb],[floor[0],floor[1],floor[2]+pa],floor]
    add('above-core-gas-core-drop',[r._line((a[0],a[1]+check().INSERTION,a[2]),a),r._bezier(c1),r._bezier(c2)],
        ('gas-check','outlet'),('foam-assembly','co2-in'),25.,spool='red')

    # V-A's feed turns around the inlet header in the open space above the
    # pump. The fore drop reuses the accepted low Y-A handoff and its lid snap.
    a,ua,_ = station('va-south-elbow','socket');b,ub,_ = station('ya-stem-elbow','socket')
    z = a[2]
    points = [r._sub(a,r._mul(ua,16.891)),a,
        (a[0],340.,z),(11.,340.,z),(11.,326.,z)]
    prefix = r._rounded(points,14.)
    angle = math.pi/3.
    first,end = r._arc((11.,326.,z),(0.,-1.,0.),(1.,0.,0.),angle,14.)
    second,end = r._arc(end,(0.,-math.cos(angle),-math.sin(angle)),(-1.,0.,0.),angle,14.)
    drop = r._rounded([end,(11.,285.,z-14.),(11.,285.,261.6),
                       (11.,261.19496077274215,261.6)],14.)
    retained = layout.specification()['fore_routes']['native_segments']['va-fore-feed'][2:]
    add('above-core-va-fore-feed',[*prefix,first,second,*drop,*retained],
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
    peak, low_z = (282., 257.) if flavor=='a' else (303.5, destination[2])
    aisle = 62. if flavor=='a' else 35.
    start = (aisle, 368. if flavor=='a' else 348., peak)
    offset = (15.5 if flavor=='a' else 0., 0., low_z-peak)
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
            ('a','valve-v-g',-33.,270.,55.5,296.,295.),
            ('b','valve-v-j',-40.,260.,35.,290.,295.)):
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
        crossing = r._rounded([approach,(lane,cross_y,cross_z),(aisle,cross_y,cross_z),
                                (aisle,lift_y,cross_z)],radius)
        peak,low_z = (282.,257.) if flavor=='a' else (303.5,destination[2])
        rise,end = _flavor_s_bend((aisle,lift_y,cross_z),(0.,1.,0.),(0.,0.,peak-cross_z),
                          (1. if peak>cross_z else -1.,0.,0.))
        transfer = []
        if flavor=='a':
            transfer_start = (aisle,330.,peak)
            shifted,shift_end = _flavor_s_bend(transfer_start,(0.,1.,0.),(6.5,0.,0.),(0.,0.,-1.))
            transfer = [r._line(end,transfer_start),*shifted]
            end = shift_end
            aisle = 62.
        rear = _flavor_rear(flavor,destination)
        stop = rear[-1]['points_mm'][-1]
        segments = [*lead,r._ease_lane(lead_end,approach),*crossing,*rise,*transfer,
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
