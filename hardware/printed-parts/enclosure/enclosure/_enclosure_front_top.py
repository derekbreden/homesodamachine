"""Private front-top numeric records; native builders retain their existing readers."""

from contextlib import contextmanager, ExitStack
import math

import _enclosure_structure
from _enclosure_panel import _Graph, _record
from _enclosure_back_top import _leaves as _shared_leaves, _replace, _rounded, _placed, _funnel_containment


def _corner_numbers(shell, outer):
    """The retained analytic corner blend in its live enclosure frame."""
    import json
    from pathlib import Path
    asset=json.loads((Path(__file__).with_name('front-corner-controls.json')).read_text())
    swept=shell._swept_top
    current={'front_radius_mm':swept.FRONT_RADIUS,'side_radius_mm':swept.SIDE_RADIUS,
             'top_radius_mm':swept.TOP_RADIUS,'angle_deg':swept.ANGLE,
             'display_flat_mm':swept.FLAT}
    if current!=asset['domain'] or outer[1]-outer[0]<=4*swept.FRONT_RADIUS:
        raise ValueError('the front corner is outside its retained analytic parameter domain')
    foot=swept.profile(outer)['foot'][1]
    return {'surfaces':asset['surfaces'],'scale_mm':swept.SIDE_RADIUS,
            'frames':[{'origin':(outer[0]+swept.FRONT_RADIUS,outer[2]+swept.FRONT_RADIUS,foot),'x_sign':-1.},
                      {'origin':(outer[1]-swept.FRONT_RADIUS,outer[2]+swept.FRONT_RADIUS,foot),'x_sign':1.}]}


def can_cut(shell, box):
    try:
        _corner_numbers(shell,box.outer)
    except ValueError:
        return False
    return True


def _halfspace(graph, origin, normal, extent):
    """The native 4*extent square, extruded extent on the plane's positive side."""
    if abs(normal[0]) > 1e-10:
        raise ValueError('the front display plane no longer has its declared X direction')
    length=math.sqrt(sum(v*v for v in normal))
    ny,nz=normal[1]/length,normal[2]/length
    section=[(origin[1]+s*nz+d*ny,origin[2]-s*ny+d*nz)
             for s,d in ((-2*extent,0.),(2*extent,0.),(2*extent,extent),(-2*extent,extent))]
    return graph.prism(0,origin[0]-2*extent,origin[0]+2*extent,section)


def _display_frame(shell, outer):
    _,normal,origin,_,_=shell._facet_geom(outer)
    if abs(normal[0])>1e-10:
        raise ValueError('the front display plane no longer has its declared X direction')
    _,ny,nz=normal
    return {'rotation':((1.,0.,0.),(0.,nz,ny),(0.,-ny,nz)),
            'translation_mm':(shell.display_centre_x(outer),origin[1],origin[2])}


def _display_exits(graph,wing,depth,inset=0.,roof_drop=0.):
    roof=wing.BACK+wing.WING_THICK+wing.BEARING_AIR-roof_drop
    shift=-depth*math.tan(math.radians(wing.ANGLE))
    out=[]
    for side in (-1,1):
        xa,xb=sorted((side*(wing.COVER_X/2-.1),side*(wing.COVER_X/2+wing.WING_REACH+wing.TIP_AIR)))
        y0,y1=-wing.WING_SPAN/2-wing.END_AIR+inset,wing.WING_SPAN/2+wing.END_AIR-inset
        out.append(graph.prism(0,xa+inset,xb-inset,
            ((y0,roof),(y0+shift,roof-depth),(y1+shift,roof-depth),(y1,roof))))
    return out


def _display_cut(shell,graph,outer,support_floor=None,support_fore=None,extend_wing_exits=True):
    import above_core as layout
    wing=shell._display_wings
    frame=_display_frame(shell,outer)
    canonical=shell._display_cut_exit_depth()
    local=wing.cuts(shell.display_facet_thickness+shell.display_pcb_cut_through,canonical)
    radius=shell._interface.display_inset_corner_r
    below=_rounded(graph,2,(-shell.display_inset_x/2,shell.display_inset_x/2,
        -shell.display_inset_slope/2,shell.display_inset_slope/2,
        -shell.display_facet_thickness,-shell.display_inset_depth),radius)
    for exit in wing.support_exits(canonical):
        local=local.fuse(below.intersect(exit.translate((0.,-radius,0.))))
    result=_placed(graph,local,frame)
    if support_floor is not None and extend_wing_exits:
        room=graph.box(outer[0]-1,outer[1]+1,outer[2]-1,outer[3]+1,support_floor,outer[5]+1)
        if support_fore is not None:
            roof=wing.BACK+wing.WING_THICK+wing.BEARING_AIR
            aft=layout.point(frame,(0.,wing.WING_SPAN/2+wing.END_AIR
                -canonical*math.tan(math.radians(wing.ANGLE)),roof-canonical))
            run=max(0.,aft[1]-support_fore)
            room=room.intersect(graph.prism(0,outer[0]-1,outer[1]+1,
                ((outer[2]-1,support_floor),(support_fore,support_floor),
                 (support_fore,aft[2]-run),(aft[1],aft[2]),(outer[3]+1,aft[2]),
                 (outer[3]+1,outer[5]+1),(outer[2]-1,outer[5]+1))))
        for exit in wing.support_exits(250):
            result=result.fuse(_placed(graph,exit,frame).intersect(room))
    return result


def _valve_body(shell,graph):
    tray=shell._valve_tray
    valve,seat,slip=tray._valve,tray._seat,tray.PORT_SLIP
    def cylinder(radius,z0,z1,x=0.,y=0.):
        return graph.cylinder(2,radius,x,y,z0,z1)
    body=cylinder(valve.bearing_radius+slip,seat.seat_top_z,valve.bearing_z_range[1]+slip)
    body=body.fuse(cylinder(valve.body_radius+slip,valve.body_main_z_range[0]-slip,
                           valve.body_main_z_range[1]+slip))
    for sx in (-1.,1.):
        for sy in (-1.,1.):
            x,y=sx*seat.corner_inset_x,sy*seat.corner_inset_y
            body=body.fuse(cylinder(valve.corner_boss_radius+slip,seat.seat_top_z,
                                   valve.post_shoulder_z+slip,x,y))
            body=body.fuse(cylinder(valve.upper_corner_radius+slip,valve.post_shoulder_z-slip,
                                   valve.body_top_z+slip,x,y))
    cap=_rounded(graph,2,(-valve.cap_width_x/2-slip,valve.cap_width_x/2+slip,
        -valve.cap_depth_y/2-slip,valve.cap_depth_y/2+slip,
        valve.top_box_z_range[0]-slip,valve.top_box_z_range[0]+valve.top_box_height+slip),
        valve.cap_corner_radius+slip)
    return body.fuse(cap)


def _teardrop(graph,radius,x,z,y0,y1,angle):
    a=math.radians(angle)
    half=radius*math.sin(a)
    tangent,apex=z+radius*math.cos(a),z+radius/math.cos(a)
    return graph.cylinder(1,radius,x,z,y0,y1).fuse(graph.prism(1,y0,y1,
        ((x-half,tangent),(x+half,tangent),(x,apex))))


def _stacked_towers(graph,stock,inner):
    """The connected groups of the current principal placed well boxes."""
    import above_core as layout
    from itertools import product
    boxes=[]
    def visit(index):
        node=graph.nodes[index]
        if node['op']=='union':
            for child in node['inputs']:
                visit(child)
            return
        if node['op']!='placed':
            raise ValueError('the front well tower requires its declared placed rectangular stock')
        source=graph.nodes[node['inputs'][0]]
        if source['op']!='box':
            raise ValueError('the front well tower requires its declared rectangular stock')
        frame=node['frame']
        if any(sum(abs(v)>1e-8 for v in row)!=1 for row in frame['rotation']):
            raise ValueError('a front well is no longer aligned to the principal wall planes')
        points=[layout.point(frame,p) for p in product(*(source['box'][2*k:2*k+2] for k in range(3)))]
        boxes.append(tuple(v for k in range(3) for v in
            (min(p[k] for p in points),max(p[k] for p in points))))
    visit(stock.index)
    groups=[]
    while boxes:
        group=[boxes.pop()]
        changed=True
        while changed:
            changed=False
            for i in range(len(boxes)-1,-1,-1):
                b=boxes[i]
                if any(all(min(a[2*k+1],b[2*k+1])-max(a[2*k],b[2*k])>1e-8
                           for k in range(3)) for a in group):
                    group.append(boxes.pop(i));changed=True
        groups.append(group)
    towers=[]
    for group in groups:
        b=tuple(v for k in range(3) for v in
            (min(p[2*k] for p in group),max(p[2*k+1] for p in group)))
        wall=inner[1] if b[1]>0 else inner[0]
        face=b[0] if b[1]>0 else b[1]
        run=abs(wall-face)
        wedge=graph.prism(1,b[2],b[3],((face,b[4]),(wall,b[4]),(wall,b[4]-run)))
        towers.append(graph.box(*b).fuse(wedge))
    return towers[0].fuse(*towers[1:])


def _pump_inverse(shell,graph,box):
    out=[]
    for x,y0,z in box.pack.pump_trays:
        flange=z-shell._interface.pump_seated_drop
        y=y0+shell._tray.rear_axis_y_shift
        finish=shell.fits.clearance(supported=True)
        room=shell._tray.boss_room(shell.cap_boss_air)
        out.append(room.fuse(room.translate((0.,0.,finish))).translate((x,y,flange)))
        motor_end=flange+shell._tray.motor_crown
        radius=shell.cap_terminal_crown_r(box)
        start=motor_end-shell.wall
        out.append(graph.cylinder(2,shell._tray.can_half,x,y,
            flange+shell._tray.boss_depth+finish-.01,start+.01))
        def cone(r0,r1,z0,height):
            r=max(r0,r1)
            return graph.add('cone',axis=2,centre=(x,y),radii=(r0,r1),span=(z0,z0+height),
                             bounds=(x-r,x+r,y-r,y+r,z0,z0+height))
        rise=radius-shell._tray.can_half
        out.append(cone(shell._tray.can_half,radius,start,rise))
        roof=radius*math.tan(math.radians(shell.teardrop_roof_angle))
        out.append(cone(radius,0.,start+rise,roof))
    return out


def _box_points(bounds):
    from itertools import product
    return list(product(*(bounds[2*k:2*k+2] for k in range(3))))


def _diamond(x,y,z,radius):
    return [(x-radius,y,z),(x,y,z+radius),(x+radius,y,z),(x,y,z-radius)]


def _corridor(shell,graph,clouds):
    span,profile=shell._fixed_pump_mount._corridor_profile([p for cloud in clouds for p in cloud])
    points=[(x,y,z) for x in span for y,z in profile]
    return graph.prism(0,*span,profile),points


def _pump_wires(shell,graph,box):
    mount=shell._fixed_pump_mount
    plan=mount.wiring_passages(shell,box)
    rear,fore=plan['front-top-electrical']['points_mm']
    radius=plan['front-top-electrical']['diamond_half_span_mm']
    shared=graph.prism(1,fore[1],rear[1],
        ((-radius,rear[2]),(0.,rear[2]+radius),(radius,rear[2]),(0.,rear[2]-radius)))
    shared_points=_diamond(0.,fore[1],rear[2],radius)+_diamond(0.,rear[1],rear[2],radius)
    opening=(-radius,radius,shell.housing_back_y(box.outer),rear[1],rear[2],box.pump_bay[2]+.01)
    cross=plan['front-top-pump-cross'];a,_,b=cross['points_mm']
    radius=cross['roof_half_span_mm'];floor=cross['floor_z_mm']
    section=((a[1]-radius,floor),(a[1]+radius,floor),(a[1]+radius,a[2]),
             (a[1],a[2]+radius),(a[1]-radius,a[2]))
    cross_body=graph.prism(0,a[0],b[0],section)
    cross_points=[(x,y,z) for x in (a[0],b[0]) for y,z in section]
    chimney=plan['front-top-display-chimney']['bounds_mm']
    link=plan['front-top-display-link'];a,b=link['points_mm'];radius=link['diamond_half_span_mm']
    frame=_display_frame(shell,box.outer)
    local=[]
    for point in _diamond(*link['terminal_entry_mm'],radius)+_diamond(*a,radius):
        delta=tuple(v-o for v,o in zip(point,frame['translation_mm']))
        local.append(tuple(sum(frame['rotation'][j][k]*delta[j] for j in range(3)) for k in range(3)))
    bounds=tuple(v for k in range(3) for v in
        (min(p[k] for p in local)-1.,max(p[k] for p in local)+1.))
    import above_core as layout
    entry=[layout.point(frame,p) for p in _box_points(bounds)]
    corridor,corridor_points=_corridor(shell,graph,[entry,_diamond(*a,radius),
        _diamond(*b,radius),_box_points(chimney)])
    return [(shared,shared_points),(graph.box(*opening),_box_points(opening)),
            (cross_body,cross_points),(corridor,corridor_points)]


def _upper_wire_room(shell,graph,box,wire_rooms):
    mount=shell._fixed_pump_mount
    d=mount.datums(shell,box)
    radius=shell.cap_terminal_crown_r(box)
    base=d['flange_z']+shell._tray.motor_crown-shell.wall+radius-shell._tray.can_half
    peak=base+radius*math.tan(math.radians(shell.teardrop_roof_angle))
    x0=shell.display_body_offset_x-shell.display_pcb_x/2
    x1=shell.display_body_offset_x+shell.display_pcb_x/2
    motor=[(x,y,z) for x in (x0,x1) for y,z in
        ((d['motor_y']-radius,base),(d['motor_y']+radius,base),(d['motor_y'],peak))]
    bounds=(x0,x1,shell.display_body_offset_slope-shell.display_pcb_slope/2,
            shell.display_body_offset_slope+shell.display_pcb_slope/2,
            -shell.display_facet_thickness-shell.display_pcb_cut_through,shell._display_wings.GLASS_SEAT)
    import above_core as layout
    frame=_display_frame(shell,box.outer)
    pcb=[layout.point(frame,p) for p in _box_points(bounds)]
    return _corridor(shell,graph,[motor,pcb,*[points for _,points in wire_rooms[2:]]])[0]


def _display_cleanouts(shell,graph,box):
    wing=shell._display_wings
    reach=wing.COVER_X/2+wing.WING_REACH+wing.TIP_AIR
    depth=shell._display_cut_exit_depth()
    roof=wing.GLASS_SEAT-shell.wall
    floor=wing.BACK+wing.WING_THICK+wing.BEARING_AIR-depth
    y0=-wing.WING_SPAN/2-wing.END_AIR-depth*math.tan(math.radians(wing.ANGLE))
    y1=wing.WING_SPAN/2+wing.END_AIR
    pcb0=shell.display_body_offset_x-shell.display_pcb_x/2
    pcb1=shell.display_body_offset_x+shell.display_pcb_x/2
    frame=_display_frame(shell,box.outer)
    return [_placed(graph,graph.box(x0,x1,y0,y1,floor,roof),frame)
            for x0,x1 in ((-reach,pcb0+.01),(pcb1-.01,reach))]


@contextmanager
def _leaves(shell,graph,box):
    wing=shell._display_wings
    def rounded(w,d,r,z0,z1,cx=0.,cy=0.):
        return _rounded(graph,2,(cx-w/2,cx+w/2,cy-d/2,cy+d/2,z0,z1),r)
    with ExitStack() as stack:
        stack.enter_context(_shared_leaves(shell,graph,box))
        stack.enter_context(_replace(wing,{'box':graph.box,'rounded_prism':rounded,
            'support_exits':lambda depth,inset=0.,roof_drop=0.:
                _display_exits(graph,wing,depth,inset,roof_drop)}))
        stack.enter_context(_replace(shell._valve_tray,{
            'build_body_clearance':lambda:_valve_body(shell,graph),
            'build_port_channel':lambda length:graph.cylinder(1,
                shell._valve_tray._valve.port_radius+shell._valve_tray.PORT_SLIP,
                0.,shell._valve_tray._valve.port_center_z,-length/2,length/2)}))
        stack.enter_context(_replace(shell._dock,{
            'return_clearances':lambda plate:[graph.cylinder(2,shell._dock.RETURN_CHANNEL_R,
                *port['point'][:2],plate['z0']-1.,port['point'][2]+20.)
                for port in plate['return_ports'].values()],
            'box':graph.box,
            'ycyl':lambda radius,x,z,y0,y1:graph.cylinder(1,radius,x,z,y0,y1),
            'teardrop_y':lambda r,x,z,y0,y1:_teardrop(graph,r,x,z,y0,y1,shell._dock.TEARDROP_DEG)}))
        stack.enter_context(_replace(shell._above_core_shell,{
            'stacked_well_towers':lambda stock,inner:_stacked_towers(graph,stock,inner)}))
        stack.enter_context(_replace(shell._tray,{
            'boss_room':lambda air:graph.prism(2,0.,shell._tray.boss_depth,
                shell._tray._pc.offset_polygon(shell._tray._pc.bore_profile,air))}))
        wire_rooms=None
        def wires():
            nonlocal wire_rooms
            if wire_rooms is None:
                wire_rooms=_pump_wires(shell,graph,box)
            return wire_rooms
        stack.enter_context(_replace(shell._fixed_pump_mount,{
            'inverse_cuts':lambda e,box:_pump_inverse(e,graph,box),
            'wire_cuts':lambda e,box:[shape for shape,_ in wires()],
            'upper_wire_room':lambda e,box:_upper_wire_room(e,graph,box,wires()),
            'display_cleanouts':lambda e,box:_display_cleanouts(e,graph,box)}))
        stack.enter_context(_replace(shell,{
            '_halfspace':lambda origin,normal,extent:_halfspace(graph,origin,normal,extent),
            '_display_cuts':lambda outer,support_floor=None,support_fore=None,extend_wing_exits=True:
                _display_cut(shell,graph,outer,support_floor,support_fore,extend_wing_exits),
            '_valve_tray_placed':lambda shape,plane,sign,x,z:
                shape.rotate((0.,0.,0.),(1.,0.,0.),-90. if sign>0 else 90.).translate((x,plane,z)),
            '_z_rail_crossing':lambda face,inside,joint,aft,floor,peak:
                graph.prism(0,min(face,inside),max(face,inside),
                    ((joint,floor),(aft,floor+aft-joint),(aft,peak+aft-joint),(joint,peak))),
        }))
        yield


def _front_half(shell,graph,box,structure):
    inner,outer=box.inner,box.outer
    housing_back=None
    if box.pump_bay and box.pack.collet_plate and box.pack.funnel:
        housing_back=shell._funnel_frame_part.roof_datums(inner,box.pack.funnel,
            shell.funnel_seat_z(outer),box.y_joint)['front']-shell.slide_slip
    _,normal,origin,_,_=shell._facet_geom(outer)
    extent=max(outer[1]-outer[0],outer[3]-outer[2],outer[5]-outer[4])+100.
    back=tuple(p-shell.display_facet_thickness*n for p,n in zip(origin,normal))
    keepout=shell._halfspace(back,normal,extent).intersect(graph.box(
        outer[0]-extent,outer[1]+extent,outer[2]-extent,
        shell.housing_back_y(outer) if housing_back is None else housing_back,
        outer[4]-extent,outer[5]+extent))
    cavity=shell._cavity(inner).cut(keepout)
    fill=shell.housing_fill(box)
    if fill is not None:
        cavity=cavity.cut(fill)
    front=structure.cut(cavity).intersect(graph.box(
        outer[0],outer[1],outer[2],box.y_joint,outer[4],outer[5]))
    for cut in shell._front_relief_cuts(inner,shell.fridge_reliefs):
        front=front.cut(cut)
    front=front.fuse(shell._front_lip(inner,box.y_joint),shell._floor_tongue(inner,box.y_joint)[0])
    front=front.cut(shell._facet_wedge(outer))
    front=front.cut(shell._display_cuts(outer,
        box.pump_bay[2] if box.pump_bay else None,
        shell.bay_back_y(box.pack.collet_plate) if box.pack.collet_plate else None,
        extend_wing_exits=not bool(box.pump_bay and box.pack.collet_plate and box.pack.pump_trays)))
    if box.pack.funnel:
        front=front.cut(shell._funnel_cut(inner,outer,box.pack.funnel))
    for cut in shell._port_cuts(box.pack.front_ports,outer[2]-5.,inner[2]+5.):
        front=front.cut(cut)
    for cut in shell._x_port_cuts(box.pack.east_ports,inner[1]-5.,outer[1]+5.):
        front=front.cut(cut)
    return front.intersect(structure)


def numbers(shell,box,*,graph=None):
    graph=graph or _Graph()
    graph.extras={}
    if box.pack.funnel:
        _funnel_containment(shell,box)
    structure=graph.add('silhouette',bounds=box.outer)
    with _record(shell,graph,structure),_leaves(shell,graph,box):
        half=_front_half(shell,graph,box,structure)
        result=shell.build_piece(box,'front','top',halves_cache={'front':half})
    from _materials import linear
    return dict(_enclosure_structure.numbers(box.outer),
        color=linear(shell.PIECE_COLORS['front-top']),panel=graph.document(result,graph.extras),
        panel_bounds=result.bounds,front_corners=_corner_numbers(shell,box.outer))


def print_numbers(shell,box):
    """The live exterior field; the rear receiver's land is disjoint from this panel."""
    import _enclosure_skin
    identification=shell._above_core_shell.rear_identification()
    station=identification.nameplate_station()
    plan=identification.nameplate_plan()
    wing=identification.nameplate.wing_interface
    plain=(shell.disposal_field(box.outer),
           *wing.plain_lips(station,plan['face_y_mm']),
           *identification.rail_bounds(),shell._above_core_shell.keystone_land())
    if box.pack.nameplate:
        plain+=shell._nameplate_fit.plain_lips(box.pack.nameplate,box.outer[3])
    if box.pack.keystone:
        plain+=shell._data_fit.plain_lips(box.pack.keystone,box.outer[3])
    out=numbers(shell,box)
    # field_land() obtains only X/Z from its native receiver. Its Y slab is the
    # rear wall's [face-3,face+1], independent of the receiver's detailed shape.
    # Keep that whole slab beyond this panel and the field's local influence.
    import above_core as layout
    face=layout.specification()['rear_wall']['rear_wall']['ymax']
    reach=max(shell.flute_rise,_enclosure_skin.reeding.flute_width)+shell._flute_skin.face_tol
    bounds=out['panel_bounds']
    if bounds is None or bounds[3]+reach>=face-3.:
        raise ValueError('the rear receiver land reaches the front-top print boundary')
    rail=shell._flute_skin.Rail(at=lambda s:shell.plan_at(s,box.outer),
        length=shell.plan_perimeter(box.outer),plain=plain)
    out.update(_enclosure_skin.field_numbers([rail],shell.flute_pitch(box.outer),
        shell.flute_depth,shell.flute_rise))
    out['disjoint_receiver_land']={'front_panel_ymax_mm':bounds[3],
        'field_reach_mm':reach,'rear_land_ymin_mm':face-3.}
    return out


def cut(shell,box,directory):
    """Write the structural fine body and its separate fluted print surface."""
    from pathlib import Path
    import _rust_part
    from _enclosure_presentation import print_payload
    said=_rust_part.cut('enclosure-shell','enclosure-front-top',print_numbers(shell,box),directory)
    step=Path(directory)/'enclosure-front-top.step'
    print_payload(step, check_print=True)
    return said
