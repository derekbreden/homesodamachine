"""Integral pump inverse, roof stock and underside-installed lower retainer.

The enclosure module supplies the machine frame and the fitted pump profiles.
This module reads its declared Box without realizing another enclosure piece.
"""
import math

import cadquery as cq


WING_THICK = 2.4
WING_INWARD_ROOM = 1.9
WING_LENGTH = 21.0
HOOK_REACH = 1.25
RELAXED_SPREAD = .35
SEATED_SPREAD = .10
SHARED_HALF_SPAN = 11.0
INTERNAL_WIRE_HALF_SPAN = 6.0
DISPLAY_LINK_HALF_SPAN = 9.0
TUBE_GATE_WIDTH = 6.35 + 2.0 * 0.25


def datums(e, box):
    trays = box.pack.pump_trays
    flange = min(cz for _cx, _cy, cz in trays) - e._interface.pump_seated_drop
    grown = e.front_top_flank_t - e.wall
    return dict(
        flange_z=flange,
        bearing_z=flange + e.fits.clearance(supported=True),
        retainer_top_z=flange-e.fits.running,
        bottom_z=e.bay_floor_z(trays)[1],
        x0=box.inner[0]+grown+e.fits.running,
        x1=box.inner[1]-grown-e.fits.running,
        y0=e.front_plane_y+e.fits.running,
        y1=e.pump_cartridge_aft_y(trays, box.pack.collet_plate),
        head_y=sum(cy for _cx, cy, _cz in trays)/len(trays),
        motor_y=sum(cy for _cx, cy, _cz in trays)/len(trays)+e._tray.rear_axis_y_shift,
    )


def fasteners(e, box):
    """The integral snap retainer uses no separate fasteners."""
    return ()


def hardware(e, box):
    return ()


def snap_datums(e, box):
    """Common end planes, spring section and receiver bearing/access surfaces."""
    d = datums(e, box)
    outer = d['x1']
    floor = d['bottom_z']
    cy = (d['y0']+d['y1'])/2.
    return dict(
        carrier_inner_x=outer-WING_THICK-WING_INWARD_ROOM,
        wing_inner_x=outer-WING_THICK, wing_outer_x=outer,
        hook_outer_x=outer+HOOK_REACH, hook_step_z=floor+3.,
        hook_ramp_z=floor+5., root_z=floor+WING_LENGTH, floor_z=floor,
        receiver_floor_z=floor-e.fits.slip,
        receiver_inner_x=outer+e.fits.running,
        receiver_back_x=outer+HOOK_REACH+SEATED_SPREAD,
        receiver_outer_x=box.outer[1],
        receiver_y0=d['y0']-e.fits.running,
        receiver_y1=d['y1']+e.fits.running,
        receiver_z0=e.z_seam+e.fits.running,
        receiver_z1=e.z_seam+35., receiver_roof_z=e.z_seam+14.8,
        port_inner_x=outer+e.fits.running,
        port_outer_x=box.outer[1]-e.wall,
        port_y0=cy-2.25, port_y1=cy+2.25)


def snap_receivers(e, box, piece):
    """One plain full-span pocket per flank, with a central tool opening and 45° roof."""
    d = snap_datums(e, box)
    for side in (-1., 1.):
        x0, x1 = sorted((side*d['receiver_inner_x'],
                         side*(d['receiver_outer_x']+.5)))
        band = e._ybox(x0, x1, d['receiver_y0'], d['receiver_y1'],
                       d['receiver_z0'], d['receiver_z1'])
        stock = band.intersect(e._rounded_outer(box.outer))
        reach = d['receiver_back_x']-d['receiver_inner_x']
        pocket = e._xz_prism(d['receiver_y0'], d['receiver_y1'], [
            (side*d['receiver_inner_x'], d['receiver_floor_z']),
            (side*d['receiver_back_x'], d['receiver_floor_z']),
            (side*d['receiver_back_x'], d['receiver_roof_z']),
            (side*d['receiver_inner_x'], d['receiver_roof_z']+reach)])
        x0, x1 = sorted((side*d['port_inner_x'], side*d['port_outer_x']))
        port = e._ybox(x0, x1, d['port_y0'], d['port_y1'],
                       d['receiver_z0'], d['receiver_roof_z'])
        roof_drop = d['port_outer_x']-d['receiver_back_x']
        corbel = e._xz_prism(d['port_y0'], d['port_y1'], [
            (side*d['receiver_back_x'], d['receiver_roof_z']),
            (side*d['port_outer_x'], d['receiver_roof_z']),
            (side*d['port_outer_x'], d['receiver_roof_z']-roof_drop)])
        receiver = stock.cut(pocket).cut(port).fuse(corbel).clean()
        piece = piece.cut(band).fuse(receiver)
    return piece.clean()


def stock(e, box):
    """Broad stock continues to the existing outer roof and display housing."""
    d = datums(e, box)
    return e._ybox(box.inner[0]-1., box.inner[1]+1.,
                   e.front_plane_y-1., e.housing_back_y(box.outer),
                   d['bearing_z'], box.outer[5]+1.).intersect(e._rounded_outer(box.outer))


def loading_opening(e, box):
    d = datums(e, box)
    return e._ybox(d['x0']-e.fits.running, d['x1']+e.fits.running,
                   d['y0']-e.fits.running, e.bay_back_y(box.pack.collet_plate),
                   e.z_seam-20., d['bearing_z'])


def wiring_passages(e, box):
    """Named nominal cable passages consumed by installed wiring and CAD."""
    d = datums(e, box)
    cy = d['motor_y']
    # The exit and cross passage follow the seated motors rather than a lintel.
    motor_end = d['flange_z']+e._tray.motor_crown
    rear_z = motor_end+2.776
    cross_z = rear_z+4.
    rear_y = box.pack.collet_plate['wall_aft_y']+0.664
    plane = e.display_plane(box.outer)
    back = (plane.origin + plane.xDir*0.5 + plane.yDir*(-1.)
            - plane.zDir*(e.display_facet_thickness+e.display_pcb_cut_through-1.))
    link = back-plane.zDir*6.
    return {
        'front-top-electrical': dict(
            points_mm=[(0., rear_y, rear_z), (0., cy, rear_z)],
            diamond_half_span_mm=SHARED_HALF_SPAN),
        'front-top-pump-cross': dict(
            points_mm=[(min(x for x, _y, _z in box.pack.pump_trays), cy, cross_z),
                       (0., cy, cross_z),
                       (max(x for x, _y, _z in box.pack.pump_trays), cy, cross_z)],
            roof_half_span_mm=INTERNAL_WIRE_HALF_SPAN,
            floor_z_mm=motor_end-e.wall),
        'front-top-display-chimney': dict(
            points_mm=[(0., 79., cross_z), (0., 78., 321.)],
            bounds_mm=[-10., 10., 72., 84., rear_z, 334.]),
        'front-top-display-link': dict(
            points_mm=[link.toTuple(), (0., 78., 321.)],
            terminal_entry_mm=(back+plane.zDir*2.).toTuple(),
            diamond_half_span_mm=DISPLAY_LINK_HALF_SPAN),
    }


def _diamond_y(x, y, z, r):
    return cq.Wire.makePolygon([cq.Vector(x-r,y,z), cq.Vector(x,y,z+r),
                               cq.Vector(x+r,y,z), cq.Vector(x,y,z-r)], close=True)


def _convex_corridor(e, shapes):
    """One straight-sided display cable room containing its entry and chimney."""
    vertices=[vertex.Center() for shape in shapes for vertex in shape.Vertices()]
    points=sorted(set((p.y,p.z) for p in vertices))
    def turn(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def chain(sequence):
        result=[]
        for point in sequence:
            while len(result)>1 and turn(result[-2],result[-1],point)<=1e-9:
                result.pop()
            result.append(point)
        return result
    outline=chain(points)[:-1]+chain(reversed(points))[:-1]
    return e._yz_prism(min(p.x for p in vertices),max(p.x for p in vertices),outline)


def wire_cuts(e, box):
    p = wiring_passages(e, box)
    shared = p['front-top-electrical']
    rear, fore = shared['points_mm']
    r = shared['diamond_half_span_mm']
    out = [cq.Solid.makeLoft([_diamond_y(0.,fore[1],rear[2],r),
                              _diamond_y(0.,rear[1],rear[2],r)],True)]
    # The rear upper half opens through the bulkhead top; the forward roof
    # and the lower half retain the printable diamond section.
    out.append(e._ybox(-r,r,e.housing_back_y(box.outer),rear[1],
                       rear[2],box.pump_bay[2]+.01))
    cross = p['front-top-pump-cross']
    a, _mid, b = cross['points_mm']
    r = cross['roof_half_span_mm']
    floor = cross['floor_z_mm']
    # A single level floor joins both motor rooms and the shared outlet. It
    # cannot leave a skin between two opposed diamond/cone faces.
    out.append(e._yz_prism(a[0], b[0],
                          [(a[1]-r,floor), (a[1]+r,floor),
                           (a[1]+r,a[2]), (a[1],a[2]+r),
                           (a[1]-r,a[2])]))
    chimney=e._ybox(*p['front-top-display-chimney']['bounds_mm'])
    link = p['front-top-display-link']
    a,b = link['points_mm']
    r = link['diamond_half_span_mm']
    plane=e.display_plane(box.outer)
    first=_diamond_y(*link['terminal_entry_mm'],r)
    inner=_diamond_y(*a,r)
    # A single rectangular pocket-normal connection contains the complete
    # entry envelope and joins the diamond run to the chimney.
    points=[plane.toLocalCoords(vertex.Center()).toTuple()
            for section in (first,inner) for vertex in section.Vertices()]
    bounds=[value for axis in range(3) for value in
            (min(point[axis] for point in points)-1.,
             max(point[axis] for point in points)+1.)]
    entry=e._ybox(*bounds).moved(cq.Location(plane))
    # The entry, rising link and chimney share one convex room. Its plain
    # walls replace the thin banks between overlapping passage cuts.
    out.append(_convex_corridor(e,[entry,inner,_diamond_y(*b,r),chimney]))
    return out


def inverse_cuts(e, box):
    """The boss and motor inverse, with printable terminal-room roofs."""
    out=[]
    for cx, cy, cz in box.pack.pump_trays:
        flange=cz-e._interface.pump_seated_drop
        y=cy+e._tray.rear_axis_y_shift
        finish=e.fits.clearance(supported=True)
        room=e._tray.boss_room(e.cap_boss_air)
        # The supported boss shoulder has its own axial face allowance.
        room=room.fuse(room.translate((0.,0.,finish)))
        out.append(room.translate((cx,y,flange)))
        motor_end=flange+e._tray.motor_crown
        terminal_r=e.cap_terminal_crown_r(box)
        start=motor_end-e.wall
        out.append(e._zcyl(e._tray.can_half,cx,y,
                           flange+e._tray.boss_depth+finish-.01,start+.01))
        # The terminal room expands above the can and closes directly at the
        # saved printable roof angle, leaving full stock below the display seat.
        rise=terminal_r-e._tray.can_half
        out.append(cq.Solid.makeCone(e._tray.can_half,terminal_r,rise,
                    cq.Vector(cx,y,start),cq.Vector(0,0,1)))
        roof_rise=terminal_r*math.tan(math.radians(e.teardrop_roof_angle))
        out.append(cq.Solid.makeCone(terminal_r,0.,roof_rise,
                    cq.Vector(cx,y,start+rise),cq.Vector(0,0,1)))
    return out


def display_cleanouts(e, box):
    """Two plain wing-support access branches open into the empty PCB room."""
    wings = e._display_wings
    reach = wings.COVER_X/2. + wings.WING_REACH + wings.TIP_AIR
    depth = 12.
    roof = wings.GLASS_SEAT-e.wall
    floor = wings.BACK+wings.WING_THICK+wings.BEARING_AIR-depth
    y0 = -wings.WING_SPAN/2.-wings.END_AIR-depth*math.tan(math.radians(wings.ANGLE))
    y1 = wings.WING_SPAN/2.+wings.END_AIR
    pcb0 = e.display_body_offset_x-e.display_pcb_x/2.
    pcb1 = e.display_body_offset_x+e.display_pcb_x/2.
    place = cq.Location(e.display_plane(box.outer))
    return [e._ybox(x0,x1,y0,y1,floor,roof).moved(place)
            for x0,x1 in ((-reach,pcb0+.01),(pcb1-.01,reach))]


def fixed_cuts(e, box):
    out=[loading_opening(e,box), *inverse_cuts(e,box), *wire_cuts(e,box),
         *display_cleanouts(e,box)]
    plate=box.pack.collet_plate
    for x,z in plate['holes']:
        out.append(e._ybox(x-TUBE_GATE_WIDTH/2.,x+TUBE_GATE_WIDTH/2.,
                           plate['fore_y']-.01,plate['wall_aft_y']+.01,
                           e.z_seam-20.,z+.01))
    return out


def lower_voids(e, box):
    trays,plate=box.pack.pump_trays,box.pack.collet_plate
    d=datums(e,box)
    source=e._pump_lower_well(trays)
    wall_offset=e._tray._pc.skirt_wall-e.cap_pump_air
    upper_half=e._tray._pc.skirt_base_half_extent-wall_offset
    corner_r=e._tray._pc.corner_r-wall_offset
    support=e.pump_skirt_support_z(trays)
    out=[]
    for cx,cy,cz in trays:
        body=source.translate((cx,cy,cz))
        for sx in (-1.,1.):
            x=cx+sx*e._tray.outlet_pitch/2.
            z=cz+e._tray.outlet_axis_z
            y0=cy+e._tray.outlet_passage_start_y(e.cap_pump_air)
            body=body.fuse(e._ycyl(e.cap_fitting_half,x,z,y0,d['y1']+1.),
                e._ybox(x-e.cap_fitting_half,x+e.cap_fitting_half,
                         y0,d['y1']+1.,z,d['retainer_top_z']+1.))
        for wedge in e._outlet_under_tangent_wedges(cx,cy,cz):
            body=body.fuse(wedge)
        for wedge in e._outlet_fore_miter_wedges(cx,cy,cz):
            body=body.cut(wedge)
        # One square fore mouth per well reaches the corner tangency above
        # the fitted skirt land; the complete bearing section below stays solid.
        body=body.fuse(e._ybox(cx-upper_half,cx+upper_half,
            d['y0']-1.,cy-upper_half+corner_r+.01,
            support,d['retainer_top_z']+1.))
        out.append(body)
    return out


def _wing(e, box, side, spread):
    """A single extruded profile; cubic sides have zero slope at the upper root.

    The standalone part carries the relaxed section. Assemblies carry the seated
    section. This is a geometric pose, not a computed elastic response.
    """
    d, s = datums(e, box), snap_datums(e, box)
    points = [(s['wing_inner_x'], s['floor_z']),
              (s['hook_outer_x'], s['floor_z']),
              (s['hook_outer_x'], s['hook_step_z']),
              (s['wing_outer_x'], s['hook_ramp_z']),
              (s['wing_outer_x'], s['root_z']),
              (s['wing_inner_x'], s['root_z'])]
    length = s['root_z']-s['floor_z']
    def deflection(z):
        t = (s['root_z']-z)/length
        return spread*t*t*(3.-t)/2.
    def slope(z):
        t = (s['root_z']-z)/length
        return -spread*(3.*t-1.5*t*t)/length
    edges = []
    for a, b in zip(points, points[1:]+points[:1]):
        xa, za = a
        xb, zb = b
        pa = cq.Vector(side*(xa+deflection(za)), d['y0'], za)
        pb = cq.Vector(side*(xb+deflection(zb)), d['y0'], zb)
        if abs(zb-za)<1e-9 or not spread:
            edges.append(cq.Edge.makeLine(pa, pb))
        else:
            da = cq.Vector(side*(xb-xa+slope(za)*(zb-za)), 0., zb-za)
            db = cq.Vector(side*(xb-xa+slope(zb)*(zb-za)), 0., zb-za)
            edges.append(cq.Edge.makeBezier([pa, pa+da/3., pb-db/3., pb]))
    wire = cq.Wire.assembleEdges(edges)
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0., d['y1']-d['y0'], 0.))


def retainer(e, box, *, seated=False):
    """Full-span upper roots and lower hooks, with the fitted pump wells retained."""
    d, s = datums(e, box), snap_datums(e, box)
    body = e._xz_prism(d['y0'], d['y1'], [
        (d['x0'], d['retainer_top_z']), (d['x1'], d['retainer_top_z']),
        (d['x1'], s['root_z']), (s['carrier_inner_x'], s['root_z']),
        (s['carrier_inner_x'], d['bottom_z']),
        (-s['carrier_inner_x'], d['bottom_z']),
        (-s['carrier_inner_x'], s['root_z']), (d['x0'], s['root_z'])])
    for cutter in lower_voids(e, box):
        body = body.cut(cutter)
    spread = SEATED_SPREAD if seated else RELAXED_SPREAD
    body = body.fuse(*[_wing(e, box, side, spread) for side in (-1., 1.)])
    return e._unified(body)


def figures(e,box):
    if not (box.pump_bay and box.pack.pump_trays):
        return {}
    d=datums(e,box)
    s=snap_datums(e,box)
    return {
        'PUMP_RETAINER_W':f"{d['x1']-d['x0']:.6g} mm",
        'PUMP_RETAINER_D':f"{d['y1']-d['y0']:.6g} mm",
        'PUMP_RETAINER_H':f"{d['retainer_top_z']-d['bottom_z']:.6g} mm",
        'PUMP_RETAINER_BOTTOM_Z':f"{d['bottom_z']:.6g} mm",
        'PUMP_RETAINER_TOP_Z':f"{d['retainer_top_z']:.6g} mm",
        'PUMP_FLANGE_Z':f"{d['flange_z']:.6g} mm",
        'PUMP_FIXED_BEARING_Z':f"{d['bearing_z']:.6g} mm",
        'PUMP_SKIRT_SUPPORT_Z':f"{e.pump_skirt_support_z(box.pack.pump_trays):.6g} mm",
        'PUMP_RETAINER_SCREW_COUNT':'0',
        'PUMP_SNAP_ROOT_Z':f"{s['root_z']:.6g} mm",
        'PUMP_SNAP_WING_THICK':f"{WING_THICK:g} mm",
        'PUMP_SNAP_LENGTH':f"{WING_LENGTH:g} mm",
        'PUMP_SNAP_RECEIVER_FLOOR_Z':f"{s['receiver_floor_z']:.6g} mm",
        'PUMP_SNAP_PORT_WIDTH':f"{s['port_y1']-s['port_y0']:g} mm",
        'PUMP_TUBE_GATE_WIDTH':f"{TUBE_GATE_WIDTH:g} mm",
        'PUMP_SHARED_WIRE_SPAN':f"{2*SHARED_HALF_SPAN:g} mm",
    }
