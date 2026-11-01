"""Private back-top construction records; Python owns the placed dimensions."""

from contextlib import contextmanager, ExitStack
import math

import _enclosure_structure
from _enclosure_panel import _Graph, _record


@contextmanager
def _replace(module, replacements):
    originals = {name: getattr(module, name) for name in replacements}
    try:
        for name, value in replacements.items():
            setattr(module, name, value)
        yield
    finally:
        for name, value in originals.items():
            setattr(module, name, value)


def _union(shapes):
    shapes = list(shapes)
    return shapes[0].fuse(*shapes[1:]) if shapes else None


def _funnel_containment(shell,box):
    """Sufficient bounds for the filled funnel to lie in the frame's body clearance.

    The ruled wet loft lies in its endpoint hull. Normal growth is bounded by
    its radius plus 0.021 mm for meshcad.grow's 0.02 mm tangential edge reach
    and the native 0.0001 mm union allowance. The remaining forming primitives
    are inside the collar plan; the brim band clips their outboard part away.
    This private path declines a layout outside these bounds.
    """
    f,frame = shell._funnel,shell._funnel_frame_part
    cx,cy = box.pack.funnel
    air = shell.funnel_collar_air
    grow = f.collar_wall+air+.021
    half_w = f.collar_w/2-f.collar_wall+grow
    half_d = f.collar_d/2-f.collar_wall+grow
    radius = f.mouth_corner_r+grow
    seat = shell.funnel_seat_z(box.outer)
    floor = frame.datums(seat)[0]-seat
    r = frame.roof_datums(box.inner,box.pack.funnel,seat)
    slip = shell.slide_slip
    narrow = box.inner[1]-shell.y_stack_high_depth-slip+slip
    margins = {
        'body_x':frame.body_width/2+slip-half_w,
        'rear_narrowing':narrow-abs(cx)-half_w,
        'front':(cy-half_d)-(r['front']-slip),
        'aft_round':(r['back']+slip-frame.corner_radius-slip)-(cy+half_d),
        'floor':(-f.drop+f.plug_lift-air)-(floor-slip),
    }
    m = frame.corbel_slope
    top = f.brim_thickness-f.chute_h
    neck = top-f._ramp_rise
    spout = f.spout_id/2+f.spout_wall
    plug_y = f.elbow_cradle.plug_half_length(f.plug_width/2)
    # The neck, outlet and plug remain in the straight middle of the collar plan.
    margins['neck_x'] = half_w-radius-abs(f.neck_dx)-spout-air
    margins['neck_y'] = half_d-radius-abs(f.neck_dy)-max(spout,plug_y)-air
    margins['plug_x'] = half_w-radius-abs(f.neck_dx)-f.plug_width/2-air
    wet = max(f.collar_d/2-f.collar_wall-m*top,
              abs(f.neck_dy)+f.spout_id/2-m*neck)+grow*math.hypot(1,m)
    outlet = abs(f.neck_dy)+spout+air-m*(-f.drop+f.plug_lift-air)
    plug = abs(f.neck_dy)+plug_y+air-m*(-f.drop+f.plug_lift-air)
    brim = half_d+m*(air+.01)
    support = frame.corbel_foot_half_depth+slip/math.cos(math.radians(30))-m*floor
    margins['corbels'] = support-max(wet,outlet,plug,brim)
    for row in frame.fastener_datums(box.inner,200.,box.pack.funnel,seat):
        inside = abs(row['x']-cx)-row['host_radius_mm']
        a = row['y']-frame.SCREW_PAD_HALF_Y-cy
        b = (r['back']+slip+1-cy if row['col']=='back' else
             row['y']+frame.SCREW_PAD_HALF_Y-cy)
        near = 0. if a<=0<=b else min(abs(a),abs(b))
        if near<=half_d:
            q = max(0.,near-(half_d-radius))
            width = half_w-radius+math.sqrt(max(0.,radius*radius-q*q))
            margins[row['name']+'-notch'] = inside-width
    if min(margins.values())<=0:
        raise ValueError('the funnel reaches beyond the private frame-containment boundary')
    return margins


def _corner_prism(graph, axis, lo, hi, section, radius, corners):
    shape = graph.prism(axis, lo, hi, section)
    graph.nodes[shape.index].update(op='corner-prism', radius=radius, corners=list(corners))
    return shape


def _rounded(graph, axis, bounds, radius, corners=(0, 1, 2, 3)):
    other = [k for k in range(3) if k != axis]
    a, b = other
    section = [(bounds[2*a], bounds[2*b]), (bounds[2*a+1], bounds[2*b]),
               (bounds[2*a+1], bounds[2*b+1]), (bounds[2*a], bounds[2*b+1])]
    return _corner_prism(graph, axis, *bounds[2*axis:2*axis+2], section, radius, corners)


def _frame_leaves(shell, graph):
    frame = shell._funnel_frame_part

    def blank(w, front, back, z0, z1, cx, radius, inner, y_joint, air):
        # The frame has square front shoulders and two rounded aft corners.
        half = w/2
        limit = inner[1]-shell.y_stack_high_depth-shell.slide_slip+air
        y0 = y_joint-shell.slide_slip+air
        if half <= limit:
            section = [(cx-half, front), (cx+half, front),
                       (cx+half, back), (cx-half, back)]
            corners = (2, 3)
        else:
            section = [(cx-half, front), (cx+half, front), (cx+half, y0),
                       (limit, y0), (limit, back), (-limit, back),
                       (-limit, y0), (cx-half, y0)]
            corners = (4, 5)
        return _corner_prism(graph, 2, z0, z1, section, radius, corners)

    def roof(inner, centre, seat, air=0., y_joint=200., full_front_opening=False):
        r = frame.roof_datums(inner, centre, seat, y_joint, full_front_opening)
        return blank(r['width']+2*air, r['front']-air, r['back']+air,
                     r['floor'], r['top']+air, centre[0], frame.corner_radius+air,
                     inner, y_joint, air)

    def body(centre, seat, air=0., inner=frame.DEFAULT_INNER, y_joint=200.):
        cx, cy = centre
        floor = frame.datums(seat)[0]
        r = frame.roof_datums(inner, centre, seat, y_joint)
        stock = blank(frame.body_width+2*air, r['front']-air, r['back']+air,
                      floor-air, seat+air, cx, frame.corner_radius+air,
                      inner, y_joint, air)
        for row in frame.fastener_datums(inner, y_joint, centre, seat):
            inside = row['x']-row['side']*(row['host_radius_mm']+shell.slide_slip-air)
            xa, xb = sorted((inside, cx+row['side']*150.))
            start = row['y']-frame.SCREW_PAD_HALF_Y-shell.slide_slip+air
            end = (r['back']+air+1 if row['col']=='back' else
                   row['y']+frame.SCREW_PAD_HALF_Y+shell.slide_slip-air)
            stock = stock.cut(graph.box(xa, xb, start, end, floor-1, r['floor']))
        for sign in (-1, 1):
            low, high = floor-2, floor+80
            foot = frame.corbel_foot_half_depth+air/math.cos(math.radians(30))
            y0 = cy+sign*(foot+frame.corbel_slope*(low-floor))
            y1 = cy+sign*(foot+frame.corbel_slope*(high-floor))
            outside = cy+sign*400
            stock = stock.cut(graph.prism(0, cx-150, cx+150,
                                          ((y0,low),(outside,low),(outside,high),(y1,high))))
        return stock.fuse(roof(inner, centre, seat, air, y_joint))

    def receivers(inner, outer, y_joint, centre, seat, col, up=None):
        blocks = []
        for row in frame.fastener_datums(inner, y_joint, centre, seat):
            if row['col'] != col:
                continue
            side = row['side']
            inside = row['x']-side*row['host_radius_mm']
            xa, xb = sorted((inside, outer[0] if side<0 else outer[1]))
            y0, bottom = row['y']-frame.SCREW_PAD_HALF_Y, row['host_bottom_z']
            block = graph.box(xa, xb, y0, y0+2*frame.SCREW_PAD_HALF_Y,
                              bottom, row['ledge_z'])
            if up is not None and up > 0:
                wall_x = inner[1] if side>0 else inner[0]
                block = block.fuse(graph.prism(1, y0, y0+2*frame.SCREW_PAD_HALF_Y,
                    ((inside,bottom),(wall_x,bottom),(wall_x,bottom-abs(wall_x-inside)))))
            blocks.append(block)
        return _union(blocks)

    def screws(inner, centre, seat, col, y_joint=200.):
        return _union(graph.cylinder(2, shell.heatset_dia/2, row['x'], row['y'],
                                    row['bore_bottom_z'], row['insert_top_z']+1)
                      for row in frame.fastener_datums(inner,y_joint,centre,seat)
                      if row['col']==col)

    return {'body_blank':body, 'roof_blank':roof, 'receivers':receivers,
            'shell_screw_cuts':screws}


def _placed(graph, shape, frame):
    from itertools import product
    import above_core as layout
    bounds = None
    if shape.bounds is not None:
        points = [layout.point(frame,p) for p in product(
            *(shape.bounds[2*k:2*k+2] for k in range(3)))]
        bounds = tuple(v for k in range(3) for v in
                       (min(p[k] for p in points),max(p[k] for p in points)))
    return graph.add('placed',[shape.index],frame=frame,bounds=bounds)


def _wing_receiver(graph, wing, solid, station, y_outer, *, supported=None, up=-1,
                   width=None,height=None,wing_span=None,wall_face=None,access=True,
                   runout_lead=0.,end_margin=2.,crown_face=None):
    """The wing interface's existing primitives, with its live physical dimensions."""
    supported = wing.SUPPORTED_END_AIR if supported is None else supported
    width = wing.WIDTH if width is None else width
    height = wing.HEIGHT if height is None else height
    wing_span = wing.WING_SPAN if wing_span is None else wing_span
    floor = y_outer-wing.THICK
    shift = (station.x,floor,station.z)
    pw,ph = width+2*wing.FACE_SLIP,height+2*wing.FACE_SLIP
    runout = max(2.,wing.FLOOR_STOCK+runout_lead)
    depth = wing.FLOOR_STOCK+wing.BACK_AIR+wing.THICK
    w,h = pw+2*(wing.PROJECTION+2),ph+end_margin+runout
    pad = _rounded(graph,2,(-w/2,w/2,-h/2,h/2,0.,depth),
                   wing.dimensions.CORNER_R+2,(0,3) if wall_face is not None else (0,1,2,3))
    pad = pad.rotate((0,0,0),(1,0,0),-90).translate(
        (0,-wing.FLOOR_STOCK-wing.BACK_AIR,-up*(runout-end_margin)/2))
    rear = -wing.FLOOR_STOCK-wing.BACK_AIR
    edge = -up*(ph/2+runout)
    def cut_yz(section):
        nonlocal pad
        pad = pad.cut(graph.prism(0,-pw,pw,section))
    cut_yz(((rear,edge),(rear,edge+up*wing.FLOOR_STOCK),(-wing.BACK_AIR,edge)))
    if wall_face is not None:
        wall_y = wall_face-floor
        run = wall_y-rear
        if run>0:
            end = up*(ph/2+end_margin)
            cut_yz(((rear,end),(wall_y,end),(rear,end-up*run)))
    if crown_face is not None and y_outer>crown_face:
        proud = y_outer-crown_face
        cut_yz(((wing.THICK-proud,edge-up*.01),(wing.THICK+.01,edge-up*.01),
                (wing.THICK+.01,edge+up*(proud+.01))))
    solid = solid.fuse(pad.translate(shift))
    mouth = _rounded(graph,2,(-width/2-wing.FACE_X_AIR,width/2+wing.FACE_X_AIR,
                              -ph/2,ph/2,0.,wing.THICK+1+wing.BACK_AIR),
                     wing.dimensions.CORNER_R+wing.FACE_SLIP)
    mouth = mouth.rotate((0,0,0),(1,0,0),-90).translate((0,-wing.BACK_AIR,0))
    solid = solid.cut(mouth.fuse(mouth.translate((0,0,up*supported))).translate(shift))
    z0 = -wing_span/2-wing.END_AIR+min(0,up*supported)
    z1 = wing_span/2+wing.END_AIR+max(0,up*supported)
    for side in (-1,1):
        xa,xb = sorted((side*(width/2-.1),side*(width/2+wing.PROJECTION+wing.TIP_AIR)))
        solid = solid.cut(graph.box(xa,xb,-wing.BACK_AIR,
                                    wing.WING_THICK+wing.THICKNESS_AIR,z0,z1).translate(shift))
        mouth_x = width/2+wing.FACE_SLIP
        roof_y = wing.WING_THICK+wing.THICKNESS_AIR
        lead = graph.prism(2,z0,z1,((side*mouth_x,roof_y),
            (side*(mouth_x+wing.ENTRY_BEVEL_WIDTH),roof_y),
            (side*mouth_x,roof_y+wing.ENTRY_BEVEL_DEPTH)))
        solid = solid.cut(lead.translate(shift))
    if access:
        diamond = graph.prism(2,0,wing.FLOOR_STOCK+wing.BACK_AIR+1,
                              ((-9,0),(0,10),(9,0),(0,-10)))
        diamond = diamond.rotate((0,0,0),(1,0,0),-90).translate(
            (0,-wing.FLOOR_STOCK-wing.BACK_AIR-.5,0))
        solid = solid.cut(diamond.translate(shift))
    return solid


def _above_leaves(shell, graph):
    import above_core_wiring as wiring
    import above_core as layout
    core = shell._above_core_shell
    identification = core.rear_identification()
    wing = identification.nameplate.wing_interface

    def wires(parent):
        additions,cuts,stations = [],[],[]
        wall = layout.specification()['enclosure']['rear_y_mm']-9.+.5
        for name,pose in wiring.placements().items():
            if pose['parent']!=parent:
                continue
            width,depth,height,*_ = wiring.SIZES[pose['size']]
            front = -.75 if name=='wago-mana' else 0.
            rear = -depth/2-wiring.FIT-wiring.WALL
            if parent=='back-top':
                rear = min(rear,pose['translation_mm'][1]-466.95)
            stock = _placed(graph,graph.box(-width/2-wiring.FIT-wiring.WALL,
                width/2+wiring.FIT+wiring.WALL,rear,front,-wiring.FIT-wiring.WALL,
                height+wiring.FIT+wiring.WALL),pose)
            pocket = _placed(graph,graph.box(-width/2-wiring.FIT,width/2+wiring.FIT,
                -depth/2-wiring.FIT,1.,-wiring.FIT,height+wiring.FIT),pose)
            if parent=='back-top':
                b = stock.BoundingBox()
                run = max(0.,wall-b.ymin)
                if run:
                    stock = stock.fuse(graph.prism(0,b.xmin,b.xmax,
                        ((b.ymin,b.zmax-3),(b.ymin,b.zmax),
                         (wall,b.zmax+run),(wall,b.zmax-3))))
            additions.append(stock)
            cuts.append(pocket)
            stations.append(dict(name=name,**pose))
        return {'add':_union(additions),'cut':_union(cuts),'stations':stations}

    def hosts():
        bosses,holes = [],[]
        datums = core.wall_mount_datums()
        def cyl(radius,root,axis,length):
            k = next(i for i,v in enumerate(axis) if abs(v)>1e-8)
            if any(abs(v)>1e-8 for i,v in enumerate(axis) if i!=k):
                raise ValueError('a wall host axis is no longer principal')
            other = [root[j] for j in range(3) if j!=k]
            return graph.cylinder(k,radius,*other,root[k],root[k]+axis[k]*length)
        for name,plan in datums.items():
            for st in plan['stations']:
                point,face,root,axis = (st[k] for k in
                    ('position_world_mm','insert_face_world_mm','stock_root_world_mm','axis_world'))
                length = sum((p-r)*u for p,r,u in zip(face,root,axis))
                bosses.append(cyl(plan['boss_radius_mm'],root,axis,length))
                tip = plan.get('bearing_tip_height_mm',0.)
                if tip:
                    bosses.append(cyl(plan['bearing_tip_radius_mm'],face,axis,tip))
                if st['threaded']:
                    inward = tuple(-u for u in axis)
                    holes.append(cyl(plan['pilot_radius_mm'],
                        tuple(p+.01*u for p,u in zip(face,axis)),inward,plan['pilot_depth_mm']+.01))
                    if tip:
                        holes.append(cyl(plan['screw_clearance_radius_mm'],
                            tuple(p+.01*u for p,u in zip(point,axis)),inward,tip+.02))
        stations = [s for n in ('relay-1','relay-2') for s in datums[n]['stations']]
        for y in sorted(set(round(s['position_world_mm'][1],6) for s in stations)):
            row = [s for s in stations if abs(s['position_world_mm'][1]-y)<1e-5]
            z0 = min(s['position_world_mm'][2] for s in row)
            z1 = max(s['position_world_mm'][2] for s in row)
            x = min(s['insert_face_world_mm'][0] for s in row)
            bosses.append(graph.box(-98.52,x,y-5,y+5,z0,z1))
        return tuple(bosses),tuple(holes)

    def receiver(piece):
        wall = layout.specification()['rear_wall']['rear_wall']
        plan = identification.nameplate_plan()
        piece = _wing_receiver(graph,wing,piece,identification.nameplate_station(),
            plan['face_y_mm'],up=-1,wall_face=wall['ymin'],runout_lead=wing.RUNOUT_LEAD,
            end_margin=3+identification.fits.supported_surface,crown_face=wall['ymax'])
        x,z = plan['center_x_mm'],plan['center_z_mm']
        outside,inside = plan['face_y_mm']+1,wall['ymin']-1
        return piece.cut(graph.prism(1,inside,outside,
            ((x-9,z),(x,z+10),(x+9,z),(x,z-10))))

    def identify(piece):
        for x in layout.specification()['fluid_grid']['columns_x_mm']:
            piece = piece.cut(graph.box(x-identification.WIDTH/2-.15,
                x+identification.WIDTH/2+.15,469.299,472.799,252.,357.))
        for b in (*identification.rail_roots(),*identification.rail_bounds()):
            piece = piece.fuse(graph.box(*b))
        return receiver(piece)

    def receiver_field():
        field = receiver(graph.add('empty'))
        graph.extras['receiver_field'] = field
        return field

    def valve_seats():
        import valve_seat as seat
        import rear_plumbing
        def sockets():
            return _union(graph.cylinder(2,seat.socket_radius,sx*seat.corner_inset_x,
                sy*seat.corner_inset_y,seat.socket_floor_z,seat.seat_top_z+1)
                for sx in (-1,1) for sy in (-1,1))
        length = 2*seat.seat_half_y+2
        channel = graph.cylinder(1,seat.valve.port_radius+seat.port_air,0.,
                                  seat.valve.port_center_z,-length/2,length/2)
        depth = rear_plumbing.plan()['joint']['PLINTH']
        native = _rounded(graph,2,(-seat.seat_half_x,seat.seat_half_x,
            -seat.seat_half_y,seat.seat_half_y,-depth,seat.seat_top_z),seat.seat_corner_radius)
        result = {'valve-v-a':_placed(graph,native.cut(sockets(),channel),layout.pose('valve-v-a'))}
        row = core.valve_seat_datums()['vk-solenoid']
        low,high = row['stock_min_world_mm'],row['stock_max_world_mm']
        stock = graph.box(*(v for pair in zip(low,high) for v in pair))
        result['vk-solenoid'] = stock.cut(_placed(graph,sockets(),layout.pose('vk-solenoid')),
                                          _placed(graph,channel,layout.pose('vk-solenoid')))
        return result

    def c14():
        inlet = shell._c14
        plan = layout.specification()['rear_wall']['dry_openings']['c14']
        x,y,z = layout.pose('c14-inlet')['translation_mm']
        clearance = plan['profile_clearance_mm']
        flange = graph.add('inlet-flange',landmarks=inlet._flange_landmarks(),
            clearance=clearance,span=(plan['flange_pocket_ymin_mm'],y+1))
        hw,hh,k = inlet.BODY_W/2,inlet.BODY_H/2,inlet.BODY_CHAMFER_LEG
        points = ((-hw,hh),(hw,hh),(hw,-(hh-k)),(hw-k,-hh),(-(hw-k),-hh),(-hw,-(hh-k)))
        body = _corner_prism(graph,1,plan['body_opening_ymin_mm'],
            plan['flange_pocket_ymin_mm']+.01,points,inlet.BODY_TOP_R,(0,1))
        graph.nodes[body.index]['offset'] = clearance
        body.bounds = tuple(v for j in range(3) for v in
                            ((body.bounds[2*j]-clearance,body.bounds[2*j+1]+clearance)
                             if j!=1 else body.bounds[2*j:2*j+2]))
        return flange.translate((x,0.,z)),body.translate((x,0.,z))

    def keystone(holds=(),keep_clear=None):
        jack = shell._keystone
        x,y,z = layout.specification()['rear_wall']['dry_openings']['keystone']['face_center_mm']
        root = layout.specification()['rear_wall']['rear_wall']['ymin']
        growth = max(0.,shell.fits.slip-jack.FIT_SLIP/2)
        half_x = shell.keystone_pocket_width()/2+jack.RECEPTACLE_WALL
        half_z = jack.POCKET_H/2+growth+jack.RECEPTACLE_WALL
        fore,centre_z = root-shell.wall,z+jack.POCKET_RISE
        x0,x1 = x-half_x,x+half_x
        for lane0,lane1,_aft,_crown in holds:
            if lane0<x1 and lane1>x0:
                x0,x1 = min(x0,lane0),max(x1,lane1)
        stock = shell._supported_cut(graph.box(x0,x1,fore,root+.01,
                                               centre_z-half_z,centre_z+half_z),shell.BACK_TOP_UP)
        top = centre_z+half_z
        stock = stock.fuse(graph.prism(0,x0,x1,((root,top),(fore,top),(root,top+root-fore))))
        if keep_clear is not None:
            stock = stock.cut(keep_clear)
        cutter,_ = shell._keystone_pocket_cut(x,z,y,back=fore)
        y_back = y-jack.DEPTH
        catches = []
        for sign,(height,proud) in ((1,jack.CATCH_UPPER),(-1,jack.CATCH_LOWER)):
            edge = z+jack.POCKET_RISE+sign*jack.POCKET_H/2
            za,zb = sorted((edge,edge-sign*height))
            za += min(0,sign*growth)
            zb += max(0,sign*growth)
            if sign*shell.BACK_TOP_UP>0:
                za += shell.BACK_TOP_UP*shell.fits.supported_surface
                zb += shell.BACK_TOP_UP*shell.fits.supported_surface
            catches.append(graph.box(x-jack.POCKET_W/2-growth,x+jack.POCKET_W/2+growth,
                                      y_back,y_back+proud,za,zb))
        return stock,shell._supported_cut(cutter,shell.BACK_TOP_UP),_union(catches)

    return [(wiring,{'shell_features':wires}),
            (core,{'box':graph.box,'rectangle':lambda b,radius=0:
                _rounded(graph,2,tuple(b[k] for k in ('xmin','xmax','ymin','ymax','zmin','zmax')),radius),
                'ycylinder':lambda r,x,z,y0,y1:graph.cylinder(1,r,x,z,y0,y1),
                'zcylinder':lambda r,x,y,z0,z1:graph.cylinder(2,r,x,y,z0,z1),
                'rear_well_tower':lambda stock,_ceiling:stock,'wall_bosses':hosts,
                'valve_seats':valve_seats,'c14_rear_cutters':c14,
                'keystone_rear_geometry':keystone,
                'fluid_supports':lambda:_fluid_supports(graph)}),
            (identification,{'apply':identify,'receiver_field':receiver_field})]


def _fluid_supports(graph):
    """Live stock and pockets around versioned reference-local radial profiles."""
    import json
    from pathlib import Path
    import above_core as layout
    import above_core_parts as parts
    import rear_plumbing as plumbing
    import rear_snaps as snaps
    import fits
    profiles = json.loads(Path(__file__).with_name('rear-seat-profiles.json').read_text())
    datums = plumbing.snap_datums()
    plan = plumbing.plan()
    bfp = plumbing.chain().bfp
    c,s = fits.running,fits.slip
    result = {}

    def runs(which,frame,axis):
        # These accepted reference frames point their axial coordinate toward -Y.
        k = 0 if which=='asse' else 2
        if tuple(row[k] for row in frame['rotation']) != (0.,-1.,0.):
            raise ValueError('the radial seat profile needs its declared axial reference orientation')
        t = frame['translation_mm'][1]
        return [(t-hi,t-lo,r+c) for lo,hi,r in reversed(profiles[which]['seat_runs'])]

    def turned(profile,axis):
        radius = max(r for _,_,r in profile)
        return graph.add('turned-runs',profile=profile,centre=axis,
            bounds=(axis[0]-radius,axis[0]+radius,profile[0][0],profile[-1][1],
                    axis[1]-radius,axis[1]+radius))

    def hex_prism(axis,apothem,clock,y0,y1,corner):
        rr = apothem/math.cos(math.pi/6)
        points = [(axis[0]+rr*math.sin(math.radians(clock+60*i)),
                   axis[1]-rr*math.cos(math.radians(clock+60*i))) for i in range(6)]
        return graph.prism(1,y0,y1,points).intersect(
            graph.cylinder(1,corner,*axis,y0,y1))

    def pockets(st):
        with _replace(snaps,{'box':graph.box}):
            return snaps.pockets(st)

    axis,frame = datums['asse_axis'],plan['chain_frame']
    profile = runs('asse',frame,axis)
    bonnet = max(x for x,r in bfp.CAP_PROFILE if r==max(r for _,r in bfp.CAP_PROFILE))
    cap_y = (layout.point(frame,(bonnet,0.,bfp.BODY_CENTER_Z))[1]-s,
             layout.point(frame,(profiles['asse']['gagira_fore_x'],0.,bfp.BODY_CENTER_Z))[1]-s)
    wrenches = []
    for p,across,clock in ((bfp.BODY_PROFILE,bfp.HEX_ACROSS_FLATS,.3),
                           (bfp.CAP_PROFILE,bfp.CAP_ACROSS_FLATS,.9)):
        y = sorted(float(layout.point(frame,(x,0.,bfp.BODY_CENTER_Z))[1])
                   for x in (p[0][0],p[-1][0]))
        wrenches.append((y,across/2,clock+datums['asse_turn'],max(r for _,r in p)))
    widest = max(*(r for y0,y1,r in profile if y1>=cap_y[0]-.25 and y0<=cap_y[1]+.25),
                 *(corner+c for *_,corner in wrenches))
    split = axis[1]+c
    st = snaps.station(axis[0],snaps.half_width(widest,split,axis[1])+snaps.WALL,
                       *cap_y,split=split)
    stock = graph.box(axis[0]-st['outer'],axis[0]+st['outer'],cap_y[0]-c-snaps.WALL,
                       datums['rear']+snaps.INTO,split,datums['ceiling']+snaps.INTO)
    room = turned(profile,axis)
    for (y0,y1),apothem,clock,corner in wrenches:
        lo = math.floor((y0-snaps.THREAD)*10)/10
        hi = math.ceil((y1+snaps.THREAD)*10)/10
        room = room.fuse(hex_prism(axis,apothem+c,clock,lo-snaps.SLIDE,hi,corner+c))
    result['asse-seat'] = stock.cut(room,*pockets(st))

    axis,frame = datums['pisco_axis'],plan['gas_frame']
    profile = runs('pisco',frame,axis)
    dims = json.loads((parts.HW/'reference/compact-inline-candidates/dimensions.json').read_text())['pisco_rvfup_quarter']
    fitting,collet = (dims['fitted_exterior']['component_ranges_mm'][k]
                       for k in ('outlet_fitting','outlet_collet'))
    cap_y = (datums['mouth_y']-collet[0]+c+.01,datums['mouth_y']-fitting[0]-2.6)
    widest = max(r for y0,y1,r in profile if y1>=cap_y[0]-.25 and y0<=cap_y[1]+.25)
    st = snaps.station(axis[0],snaps.half_width(widest,snaps.SPLIT,axis[1])+snaps.WALL,*cap_y)
    stock = graph.box(axis[0]-st['outer'],axis[0]+st['outer'],cap_y[0]-c-snaps.WALL,
                       datums['rear']+snaps.INTO,snaps.SPLIT,datums['ceiling']+snaps.INTO)
    result['pisco-seat'] = stock.cut(turned(profile,axis),*pockets(st))

    meter = parts._module('back_top_seat_meter','reference/digiten-flow-sensor/digiten_flow_sensor.py')
    frame = layout.pose('digiten-flow')
    def at(point):
        return layout.point(frame,point)
    centre = at((meter.body_center_x,0.,meter.body_center_z))
    my,mz = float(centre[1]),float(centre[2])
    port = at((0.,0.,0.))
    soda = (float(port[0]),float(port[2]))
    def wx(y):
        return float(at((meter.body_center_x,y,meter.body_center_z))[0])
    def wy(x):
        return float(at((x,0.,0.))[1])
    mx = wx(7.3)-c
    fore,aft = snaps.SLIDE+snaps.VAR,snaps.VAR
    x0,east = mx-1.,wx(meter.screw_head_y_range[1])+c
    def stadium(y,z,r):
        return graph.add('stadium-x',y=y,z=z,radius=r,fore=fore,aft=aft,span=(x0,east),
            bounds=(x0,east,y-fore-r,y+aft+r,z-r,z+r))
    cup = stadium(my,mz,17.5+c)
    for dy in (-meter.boss_x,meter.boss_x):
        for dz in (-meter.boss_z,meter.boss_z):
            cup = cup.fuse(stadium(my+dy,mz+dz,meter.boss_radius+c))
    collar = max(meter.port_collar_radii)
    for sign in (-1.,1.):
        ya,yb = sorted((wy(sign*meter.port_neck_end),wy(sign*meter.port_collar_end)))
        sleeve = graph.cylinder(1,collar+c,*soda,ya-fore-c,yb+aft+c)
        cup = cup.fuse(sleeve.intersect(graph.box(x0,soda[0]+collar+1.,
            ya-fore-2.,yb+aft+2.,soda[1]-collar-1.,soda[1]+collar+1.)))
    root = at(meter.wire_root)
    half = meter.wire_root_width/2
    cup = cup.fuse(graph.box(x0,wx(meter.wire_root[1]+meter.wire_root_depth/2)+c,
        wy(-half)-fore-c,wy(half)+aft+c,mz-60.,float(root[2])+meter.wire_boss_len+c))
    seat_y,cap_y = (386.,446.),(397.,435.)
    st = snaps.station(0.,soda[1]+collar+c-mz+snaps.WALL,*cap_y,split=0.)
    stock = graph.box(mx,datums['side']+snaps.INTO,*seat_y,mz-st['outer'],mz+st['outer'])
    cuts = [p.rotate((0,0,0),(0,1,0),90).translate((mx,0.,mz)) for p in pockets(st)]
    result['meter-seat'] = stock.cut(cup,*cuts)

    mount = plan['regulator_mount']
    st,axis = mount['station'],mount['axis']
    a,b = mount['seat_y']
    b = max(b,st['y1']+fits.running+snaps.WALL)
    stock = graph.box(axis[0]-st['outer'],axis[0]+st['outer'],a,b,snaps.SPLIT,346.5)
    seat = stock.cut(turned(mount['seat_runs'],axis),*pockets(st))
    result['regulator-seat'] = seat.rotate((0,0,0),(0,0,1),90)
    return result


def _route_features(graph,host):
    from hardware.wiring.installed.retainers import cable_sites
    from _tube_snap_sites import tube_sites
    import route_snap as snap
    def unit(v):
        length = math.sqrt(sum(k*k for k in v))
        return tuple(k/length for k in v)
    def cross(a,b):
        return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
    def place(shape,origin,x,y,z):
        return _placed(graph,shape,{'rotation':tuple(zip(x,y,z)),'translation_mm':origin})
    additions=[]
    for site in cable_sites():
        if site['host']!=host:
            continue
        n,p = unit(site['outward']),unit(site['profile_up'])
        u = unit(cross(n,p))
        d,h,span,stock,beak = (site[k] for k in ('seat_depth','seat_height','span','stock','beak'))
        projection=d+stock
        floor=projection+stock
        roof=floor+h
        top=roof+beak+stock
        mouth=d-beak
        section=((-snap.ROOT_OVERLAP,-snap.ROOT_OVERLAP),(projection,projection),
                 (projection,top),(d,top),(mouth,top-beak),(mouth,roof),
                 (d,roof),(d,floor),(-snap.ROOT_OVERLAP,floor))
        origin=tuple(a-b*span/2 for a,b in zip(site['origin'],u))
        additions.append(place(graph.prism(2,0.,span,section),origin,n,p,u))
    groups={}
    for site in tube_sites():
        if site['host']!=host:
            continue
        u,n = unit(site['along']),unit(site['outward'])
        t = unit(cross(u,n))
        ri=site['bore_diameter']/2
        wing,span = site['wing'],site['span']
        ro,rm,nose=ri+wing,ri+wing/2,wing/2
        tip=math.radians(snap.TUBE_TIP_DEGREES)
        def point(r,a):return (r*math.sin(a),r*math.cos(a))
        def add(a,b):return (a[0]+b[0],a[1]+b[1])
        a,b,c,d=point(ro,-tip),point(ro,tip),point(ri,tip),point(ri,-tip)
        cp,cn=point(rm,tip),point(rm,-tip)
        qp,qn=(math.cos(tip),-math.sin(tip)),(math.cos(-tip),-math.sin(-tip))
        body=graph.add('arc-prism',axis=2,span=(0.,span),start=a,
            segments=[{'arc':[(0.,ro),b]},
                      {'arc':[add(cp,(nose*qp[0],nose*qp[1])),c]},
                      {'arc':[(0.,ri),d]},
                      {'arc':[add(cn,(-nose*qn[0],-nose*qn[1])),a]}])
        reach=site['root_distance']+snap.ROOT_OVERLAP
        root=graph.prism(2,0.,span,((-ro,0),(ro,0),(ro,reach),(-ro,reach)))
        growth=unit(site['print_up'])
        vertical=sum(a*b for a,b in zip(t,growth))
        if abs(abs(vertical)-1)<1e-7:
            sign=1. if vertical>0 else -1.
            edge=-sign*ro
            root=root.fuse(graph.prism(2,0.,span,((edge,0),(edge,reach),(edge-sign*reach,reach))))
        body=body.fuse(root).cut(graph.cylinder(2,ri,0.,0.,-.1,span+.1))
        origin=tuple(a-b*span/2 for a,b in zip(site['centre'],u))
        body=place(body,origin,t,cross(u,t),u)
        group=site.get('group')
        if group is None:
            additions.append(body)
        else:
            entry=groups.setdefault(group['id'],[group,[]])
            entry[1].append(body)
    for group,bodies in groups.values():
        bridge=graph.box(*(v for pair in zip(group['bridge_origin'],
            (a+b for a,b in zip(group['bridge_origin'],group['bridge_size']))) for v in pair))
        additions.append(bodies[0].fuse(bridge,*bodies[1:]))
    return additions


@contextmanager
def _leaves(shell, graph, box):
    funnel = shell._funnel
    frame = shell._funnel_frame_part
    def rounded(w, d, r, z0, z1, cx=0., cy=0.):
        return _rounded(graph,2,(cx-w/2,cx+w/2,cy-d/2,cy+d/2,z0,z1),r)
    def brim(grow,z0,z1,cx=0.,cy=0.,front=0.):
        x = funnel.collar_w/2+funnel.brim_overhang+grow
        y = funnel.collar_d/2+funnel.brim_overhang+grow
        return _rounded(graph,2,(cx-x,cx+x,cy-y-front,cy+y,z0,z1),
                        funnel.brim_corner_r+grow,(2,3))
    def plumb(half,front,back,seat):
        return _rounded(graph,2,(-half,half,front,back,
            seat-shell.funnel_seat_thickness-1,seat+shell.slide_slip),
            frame.corner_radius+shell.slide_slip,(2,3))
    def keepout(outer,centre):
        # Scoped containment is checked against the current funnel/frame dimensions.
        return frame.shell_clearance(centre,shell.funnel_seat_z(outer),box.inner)
    import _route_snaps
    with ExitStack() as stack:
        stack.enter_context(_replace(frame,_frame_leaves(shell,graph)))
        stack.enter_context(_replace(funnel,{'brim_plan':brim}))
        stack.enter_context(_replace(shell._swept_top,{'rounded_prism':rounded}))
        stack.enter_context(_replace(shell,{
            '_funnel_plumb':plumb, '_funnel_keepout':keepout,
            '_rect_cut_y':lambda x,z,w,h,r,y0,y1:
                _rounded(graph,1,(x-w/2,x+w/2,y0,y1,z-h/2,z+h/2),r),
            '_rect_cut_x':lambda y,z,w,h,r,x0,x1:
                _rounded(graph,0,(x0,x1,y-w/2,y+w/2,z-h/2,z+h/2),r),
        }))
        for module,replacements in _above_leaves(shell,graph):
            stack.enter_context(_replace(module,replacements))
        stack.enter_context(_replace(_route_snaps,{'apply':lambda piece,y,z:
            piece.fuse(*_route_features(graph,f'enclosure-{y}-{z}'))}))
        yield


def numbers(shell, box):
    """Record back-top without populating any retained native geometry cache."""
    graph = _Graph()
    graph.extras = {}
    containment = _funnel_containment(shell,box) if box.pack.funnel else None
    structure = graph.add('silhouette',bounds=box.outer)
    if shell.housing_back_y(box.outer)>=box.y_joint:
        raise ValueError('the display housing reaches the private back-top boundary')
    with _record(shell,graph,structure), _leaves(shell,graph,box):
        o = box.outer
        half = structure.cut(shell._cavity(box.inner)).intersect(
            graph.box(o[0],o[1],box.y_joint,o[3],box.splits[1],o[5]))
        if box.pack.funnel:
            half = half.cut(shell._funnel_cut(box.inner,o,box.pack.funnel))
        for ports,cutter in ((box.pack.back_ports,shell._port_cuts),
                            (box.pack.west_ports,shell._x_port_cuts)):
            selected = [p for p in ports if p[2]>box.splits[1]]
            cuts = (cutter(selected,box.inner[3]-5,o[3]+5,shell.BACK_TOP_UP)
                    if cutter is shell._port_cuts else
                    cutter(selected,o[0]-5,box.inner[0]+5,shell.BACK_TOP_UP))
            for air in cuts:
                half = half.cut(air)
        result = shell.build_piece(box,'back','top',halves_cache={'back':half})
    from _materials import linear
    return dict(_enclosure_structure.numbers(box.outer),
                color=linear(shell.PIECE_COLORS['back-top']),panel=graph.document(result,graph.extras),
                funnel_containment=containment)


def print_numbers(shell,box):
    """The unchanged field phase and plain lands; Rust measures the constructed raised pad."""
    import _enclosure_skin
    identification = shell._above_core_shell.rear_identification()
    wing = identification.nameplate.wing_interface
    plain = (shell.disposal_field(box.outer),*wing.plain_lips(
        identification.nameplate_station(),identification.nameplate_plan()['face_y_mm']),
        *identification.rail_bounds(),shell._above_core_shell.keystone_land())
    if box.pack.nameplate:
        plain += shell._nameplate_fit.plain_lips(box.pack.nameplate,box.outer[3])
    if box.pack.keystone:
        plain += shell._data_fit.plain_lips(box.pack.keystone,box.outer[3])
    rail = shell._flute_skin.Rail(at=lambda s:shell.plan_at(s,box.outer),
                                  length=shell.plan_perimeter(box.outer),plain=plain)
    out = numbers(shell,box)
    out.update(_enclosure_skin.field_numbers([rail],shell.flute_pitch(box.outer),
                                             shell.flute_depth,shell.flute_rise))
    out['print'] = {'embed':shell.disposal_embed,'raised_bounds':identification.rail_bounds()}
    return out


def cut(shell,box,directory):
    """Write the structural fine model and its separate fluted print surface."""
    from pathlib import Path
    import _rust_part
    import trimesh
    from meshcad.write import print_payload
    said = _rust_part.cut('enclosure-shell','enclosure-back-top',print_numbers(shell,box),directory)
    step = Path(directory)/'enclosure-back-top.step'
    printed = trimesh.load_mesh(step.with_suffix('.stl'))
    loose = shell._flute_skin.non_manifold_edges(printed)
    if loose or not printed.is_watertight:
        raise ValueError(f'{step.with_suffix(".stl").name}: {loose} non-manifold edges, '
                          f'watertight={printed.is_watertight}')
    print_payload(step,printed)
    return said
