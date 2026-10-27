"""Integral above-core shell mounts beneath the continuous ceiling."""

import functools
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'manifold-layout'))
import above_core as layout
from _enclosure_interface import flute_depth


@functools.cache
def rear_identification():
    sys.path.insert(0, str(HERE.parent / 'rear-identification'))
    import rear_identification as identification
    return identification


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def rectangle(bounds, radius=0):
    shape = box(*(bounds[k] for k in ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax')))
    return cq.Workplane(obj=shape).edges('|Z').fillet(radius).val() if radius else shape


def zcylinder(radius, x, y, z0, z1):
    return cq.Solid.makeCylinder(radius, z1-z0, cq.Vector(x, y, z0))


def ycylinder(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius, y1-y0, cq.Vector(x, y0, z), cq.Vector(0, 1, 0))


def psu_fastener_plan():
    """Four short inserts support the drawing's 6.7 ± 1 mm mounting ears."""
    reach = (12.-7.7, 12.-5.7)
    pilot = reach[1]+1.
    return {'count':4, 'screw':'M3x12 SHCS', 'screw_length_mm':12.,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'ear_thickness_range_mm':(5.7,7.7), 'receiving_range_mm':reach,
            'pilot_depth_mm':pilot, 'minimum_tip_air_mm':1.,
            'minimum_blind_backing_mm':layout.pose('psu')['translation_mm'][0]-pilot+107.5,
            'minimum_fluted_backing_mm':layout.pose('psu')['translation_mm'][0]-pilot+107.5-flute_depth,
            'maximum_flute_depth_mm':flute_depth,
            'boss_radius_mm':5., 'pilot_radius_mm':2.,
            'parent':'enclosure-back-top', 'load_retention_qualified':False}


def relay_fastener_plan():
    """Two diagonal screws and four bearing pads support each relay PCB."""
    tip=2.15
    reach=8.-1.5-tip
    pilot=reach+1.
    return {'count':2, 'active_hole_indices':(0,3),
            'screw':'M3x8 SHCS', 'screw_length_mm':8.,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'pcb_thickness_mm':1.5, 'receiving_range_mm':(reach,reach),
            'pilot_depth_mm':pilot, 'minimum_tip_air_mm':1.,
            'minimum_blind_backing_mm':min(layout.pose(n)['translation_mm'][0]
                for n in ('relay-1','relay-2'))-tip-pilot+107.5,
            'minimum_fluted_backing_mm':min(layout.pose(n)['translation_mm'][0]
                for n in ('relay-1','relay-2'))-tip-pilot+107.5-flute_depth,
            'maximum_flute_depth_mm':flute_depth,
            'boss_radius_mm':5., 'pilot_radius_mm':2.,
            'bearing_tip_height_mm':tip, 'bearing_tip_radius_mm':2.85,
            'screw_clearance_radius_mm':1.7,
            'bearing_tip_basis':'The short bearing tip clears the reference pin envelope and the PSU. Its passage is unthreaded; the full 3 mm insert wall begins behind the pins. Actual pin fit, load and retention are unqualified.',
            'parent':'enclosure-back-top', 'load_retention_qualified':False}


def wall_mount_datums():
    """Native-reference mounting planes and the selected west-wall hosts.

    All four corners bear on pads. Relay screws occupy opposite diagonal
    corners, keeping a complete 3 mm pilot wall between the stacked boards.
    These are nominal mechanical interfaces, without load or retention data.
    """
    sys.path[:0] = [str(HERE.parents[2] / 'reference' / name)
                   for name in ('meanwell-irm90','teyleten-relay')]
    import meanwell_irm90, teyleten_relay
    result={}
    for name,source,plan in (('psu',meanwell_irm90,psu_fastener_plan()),
            ('relay-1',teyleten_relay,relay_fastener_plan()),
            ('relay-2',teyleten_relay,relay_fastener_plan())):
        stations=[]
        for index,(hx,hy) in enumerate(source.holes):
            point=layout.point(layout.pose(name),(hx,hy,0.))
            face=(point[0]-plan.get('bearing_tip_height_mm',0.),point[1],point[2])
            stations.append({'native_hole_index':index,'position_world_mm':point,
                'insert_face_world_mm':face,
                'axis_world':layout.vector(layout.pose(name)['rotation'],(0.,0.,1.)),
                'threaded':name=='psu' or index in plan['active_hole_indices'],
                'stock_root_world_x_mm':-98.52,
                'standoff_mm':point[0]+98.5})
        result[name]={**plan,'stations':tuple(stations)}
    return result


def _wall_hosts(names):
    bosses,holes=[],[]
    for name,plan in wall_mount_datums().items():
        if name not in names:
            continue
        for station in plan['stations']:
            x,y,z=station['position_world_mm'];root=station['stock_root_world_x_mm']
            insert_x=station['insert_face_world_mm'][0]
            boss=cq.Solid.makeCylinder(plan['boss_radius_mm'],insert_x-root,
                cq.Vector(root,y,z),cq.Vector(1.,0.,0.))
            if plan.get('bearing_tip_height_mm',0.):
                tip=cq.Solid.makeCylinder(plan['bearing_tip_radius_mm'],x-insert_x,
                    cq.Vector(insert_x,y,z),cq.Vector(1.,0.,0.))
                boss=boss.fuse(tip).clean()
            bosses.append(boss)
            if station['threaded']:
                holes.append(cq.Solid.makeCylinder(plan['pilot_radius_mm'],
                    plan['pilot_depth_mm']+.01,cq.Vector(insert_x+.01,y,z),cq.Vector(-1.,0.,0.)))
                if plan.get('bearing_tip_height_mm',0.):
                    holes.append(cq.Solid.makeCylinder(plan['screw_clearance_radius_mm'],
                        x-insert_x+.02,cq.Vector(x+.01,y,z),cq.Vector(-1.,0.,0.)))
    return tuple(bosses),tuple(holes)


@functools.cache
def relay_bosses():
    return _wall_hosts(('relay-1','relay-2'))


@functools.cache
def psu_bosses():
    return _wall_hosts(('psu',))


def wall_bosses():
    first,second=relay_bosses(),psu_bosses()
    return first[0]+second[0],first[1]+second[1]


def c14_fastener_plan():
    """The washer bridges the inlet's native countersink under a socket head."""
    return {'screw_length_mm': 10., 'washer_od_mm': 7., 'washer_thickness_mm': .5,
            'flange_thickness_mm': 3.25, 'insert_length_mm': 4.,
            'screw_reach_mm': 6.25, 'pilot_depth_mm': 7.25,
            'boss_depth_mm': 10.25, 'tip_air_mm': 1., 'backing_mm': 3.}


def c14_rear_cutters():
    """Separate the measured inboard body fit from the outboard flange recess.

    The reference's measured 26.10 by 18.00 mm wiring body, including its
    chamfers and upper rounds, sets the inboard aperture. The larger generic
    panel-cutout recommendation would cut the neighboring WAGO wall and the
    insert hosts. Actual body seating remains a physical fit question.
    """
    sys.path.insert(0, str(HERE.parents[2] / 'reference/iec-c14-inlet'))
    import iec_c14_inlet as inlet

    plan = layout.specification()['rear_wall']['dry_openings']['c14']
    x, y, z = layout.pose('c14-inlet')['translation_mm']
    clearance = plan['profile_clearance_mm']
    flange = inlet.flange_prism(
        clearance, plan['flange_pocket_ymin_mm'], y + 1.).val()
    profile = inlet._body_profile()._faces.Faces()[0].outerWire()
    outline = profile.offset2D(clearance)[0]
    body = (cq.Workplane(inlet.xz_plane_y_up)
            .workplane(offset=plan['body_opening_ymin_mm'])
            .placeSketch(cq.Sketch().face(outline).reset())
            .extrude(plan['flange_pocket_ymin_mm']
                     - plan['body_opening_ymin_mm'] + .01).val())
    return flange.translate((x, 0., z)), body.translate((x, 0., z))


def keystone_rear_geometry(holds=(), keep_clear=None):
    """The enclosure's fitted shoulder, catches and broad corbel at the jack.

    THE BOSS STANDS ONE WALL PROUD OF THE REAR WALL'S FACE. The jack reaches 0.7 mm past the
    wall to its catches; the boss carries the pocket on through its own depth behind them, so
    its faces stand a full wall wide rather than 0.7 mm. Where a core hold's lane meets the
    boss (`holds`, the pack's `(x0, x1, aft, crown)` stations), the boss runs across the whole
    lane and its side lands on the bracket's own. `keep_clear` is the wiring's room, which the
    boss and its corbel give back."""
    import enclosure

    jack = enclosure._keystone
    x, y, z = layout.specification()['rear_wall']['dry_openings']['keystone'][
        'face_center_mm']
    root = layout.specification()['rear_wall']['rear_wall']['ymin']
    growth = max(0., enclosure.fits.slip - jack.FIT_SLIP / 2.)
    half_x = enclosure.keystone_pocket_width() / 2. + jack.RECEPTACLE_WALL
    half_z = jack.POCKET_H / 2. + growth + jack.RECEPTACLE_WALL
    fore = root - enclosure.wall
    centre_z = z + jack.POCKET_RISE
    x0, x1 = x - half_x, x + half_x
    for lane0, lane1, _aft, _crown in holds:
        if lane0 < x1 and lane1 > x0:
            x0, x1 = min(x0, lane0), max(x1, lane1)
    block = box(x0, x1, fore, root+.01, centre_z-half_z, centre_z+half_z)
    stock = enclosure._supported_cut(block, enclosure.BACK_TOP_UP)
    top = centre_z + half_z
    stock = stock.fuse(enclosure._yz_prism(
        x0, x1, ((root, top), (fore, top), (root, top+root-fore))))
    if keep_clear is not None:
        stock = stock.cut(keep_clear)
    cutter, _ = enclosure._keystone_pocket_cut(x, z, y, back=fore)
    _, catches = jack.receptacle_boss(x, z, y, root)
    return (stock.clean(),
            enclosure._supported_cut(cutter, enclosure.BACK_TOP_UP),
            enclosure._keystone_catches(catches, enclosure.BACK_TOP_UP))


def keystone_land():
    """The flat land round the jack's aperture on the rear face: the flutes stay off its
    three-millimetre lip and the ease over the aperture, one wall past each edge."""
    import enclosure

    jack = enclosure._keystone
    x, y, z = layout.specification()['rear_wall']['dry_openings']['keystone'][
        'face_center_mm']
    half_w = jack.FACE_W / 2. + enclosure.fits.slip + enclosure.wall
    half_h = jack.FACE_H / 2. + enclosure.fits.slip + enclosure.wall
    return (x - half_w, x + half_w, y - 3., y + 1.,
            z - half_h, z + half_h + enclosure.keystone_ease_shoulder)


def rear_geometry(piece, holds=(), keep_clear=None):
    plan = layout.specification()['rear_wall']
    relief = plan['interior_panel_relief']
    piece = piece.cut(rectangle(relief))
    for port in plan['wet_ports']:
        piece = piece.cut(ycylinder(port['bore_diameter_mm']/2,
                                    port['center_x_mm'], port['center_z_mm'],
                                    458., 472.3))
    c14 = plan['dry_openings']['c14']
    x, y, z = layout.pose('c14-inlet')['translation_mm']
    piece = piece.cut(*c14_rear_cutters())
    # Two washer-backed M3 x 10 screws carry the flange on short inserts.
    # Their blind pilots retain 3 mm stock behind the screw-tip relief.
    seat_y = y-3.25
    fasteners = c14_fastener_plan()
    for dx in (-c14['mount_pitch_mm']/2, c14['mount_pitch_mm']/2):
        piece = piece.fuse(ycylinder(5., x+dx, z,
                                    seat_y-fasteners['boss_depth_mm'], seat_y))
        piece = piece.cut(ycylinder(2., x+dx, z,
                                    seat_y-fasteners['pilot_depth_mm'], seat_y+.01))
    stock, cutter, catches = keystone_rear_geometry(holds, keep_clear)
    piece = piece.fuse(stock).cut(cutter).fuse(catches)
    return piece


def gas_check_support_datums():
    """The purchased check's fixed barrel band, carried into the east bay.

    The body scale and socket depths retain the vendor-reference estimates.
    The eight-millimetre bearing stays inside its fixed cylindrical band.
    Both gas seats share Z293..301 and join as one plain rectangular carrier.
    """
    sys.path.insert(0, str(HERE.parents[2] / 'reference/neofit-achv44-check'))
    import neofit_achv44_check as check

    first, last, body_radius = check.bearing_band()
    inlet, _ = check.inlet()
    native_centre = (0., inlet[1] + (first + last) / 2., 0.)
    frame = layout.snapshot_pose('gas-check')
    x, y, _z = layout.point(frame, native_centre)
    return {
        'centre_world_mm': (x, y, 297.),
        'axis_world': layout.vector(frame['rotation'], (0., 1., 0.)),
        'fixed_band_from_inlet_mm': (first, last),
        'body_radius_mm': body_radius,
        'seat_radius_mm': body_radius + .25,
        'bearing_width_mm': 8.,
        'outer_half_y_mm': max(11., body_radius + .25 + 3.),
        'wall_root_x_mm': 98.51,
        'nominal_radial_air_mm': .25,
        'ordinary_wall_mm': 3.,
    }


def gas_check_support():
    """One broad east-wall saddle; the nominal release collets remain free."""
    data = gas_check_support_datums()
    x, y, z = data['centre_world_mm']
    radius = data['seat_radius_mm']
    half = data['bearing_width_mm'] / 2.
    side = data['outer_half_y_mm']
    saddle = box(x, data['wall_root_x_mm'], y-side, y+side, z-half, z+half)
    return saddle.cut(
        zcylinder(radius, x, y, z-half-.1, z+half+.1),
        box(x+radius+3., x+radius+5.5, y-2., y+2., z-half-.1, z+half+.1),
    ).clean()


def valve_seat_datums():
    """Approved full socket plates rooted directly in the two sidewalls."""
    import itertools
    sys.path.insert(0, str(HERE.parents[2] / 'printed-parts/valve-seat'))
    import valve_seat as seat

    result = {}
    for name in ('valve-v-a', 'vk-solenoid'):
        frame = layout.pose(name)
        corners = [layout.point(frame, point) for point in itertools.product(
            (-seat.seat_half_x, seat.seat_half_x),
            (-seat.seat_half_y, seat.seat_half_y),
            (seat.socket_floor_z-seat.wall, seat.seat_top_z))]
        low = [min(point[i] for point in corners) for i in range(3)]
        high = [max(point[i] for point in corners) for i in range(3)]
        if frame['translation_mm'][0] < 0.:
            low[0] = -98.51
        else:
            high[0] = 98.51
        result[name] = {'parent': 'enclosure-back-top',
                        'stock_min_world_mm': low, 'stock_max_world_mm': high,
                        'socket_diameter_mm': seat.socket_diameter,
                        'socket_floor_backing_mm': seat.wall,
                        'frame': frame,
                        'interface': 'Shared valve_seat V69 four blind sockets and open port channel'}
    return result


@functools.cache
def valve_seats():
    """Native full-width valve plates fused to their nearest shell sidewall."""
    datums = valve_seat_datums()
    import valve_seat as seat

    result = {}
    for name, row in datums.items():
        low, high = row['stock_min_world_mm'], row['stock_max_world_mm']
        stock = box(low[0], high[0], low[1], high[1], low[2], high[2])
        location = layout.location(name)
        sockets = seat.build_sockets().val().moved(location)
        channel = seat.build_port_channel(2.*seat.seat_half_y+2.).val().moved(location)
        result[name] = stock.cut(sockets, channel).clean()
    return result


def tie_window(axis, lo, hi, a0, a1, z_mid):
    """Straight tie passage with its existing 45-degree print-down closure."""
    import enclosure
    mid, half = (a0+a1)/2., (a1-a0)/2.
    section = [(a0,z_mid+2.),(a1,z_mid+2.),(a1,z_mid-2.),
               (mid,z_mid-2.-half),(a0,z_mid-2.)]
    return (enclosure._xz_prism(lo,hi,section) if axis == 'y'
            else enclosure._yz_prism(lo,hi,section))


@functools.cache
def fluid_supports():
    """Broad, open saddles on fixed roof/wall stock, with separate tie paths.

    The horizontal bodies enter from the open half of each saddle. Gas bodies
    enter from the west. The 0.25 mm radial fit is nominal layout clearance;
    the restraints do not establish pressure capacity or service life.
    """
    result = {}
    z = layout.pose('asse1022-assembly')['translation_mm'][2]
    # The aft ASSE bearing shares the meter's broad fore roof column.
    x = 37.25
    for index, y in enumerate((340., 364.), 1):
        if index == 2:
            import _back_top_meter
            result['asse-2'] = _back_top_meter.meter_supports()[0]
            continue
        radius = 16.75
        saddle = box(x+7.25, x+radius+9., y-3., y+3., 315.92604788, 355.)
        saddle = saddle.cut(ycylinder(radius, x, z, y-3.1, y+3.1))
        saddle = saddle.cut(tie_window('y', y-3.1, y+3.1, x+radius+3., x+radius+5.5, z))
        result[f'asse-{index}'] = saddle.clean()
    # The regulator's two diameters retain their own bearings. Its narrow
    # socket ends and the transverse outlet tube stay free of the supports.
    y = layout.snapshot_pose('reg')['translation_mm'][1]
    for index, x, radius in ((1, -5.3541011287684, 13.75),
                              (2, -29.3541011287684, 12.25)):
        saddle = box(x-3., x+3., y, y+radius+9., z-radius-3., 355.)
        bore = cq.Solid.makeCylinder(radius, 6.2, cq.Vector(x-3.1, y, z), cq.Vector(1, 0, 0))
        saddle = saddle.cut(bore, tie_window('x', x-3.1, x+3.1, y+radius+3., y+radius+5.5, z))
        result[f'water-regulator-{index}'] = saddle.clean()
    # Both seats join on common Z293/301 planes as one broad, flat carrier.
    # Only the two circular bearings and their straight tie slots cut it.
    for name, y, z, radius in (('gas-regulator', 418.9526, 297., 11.),):
        x = layout.snapshot_pose(name)['translation_mm'][0]
        saddle = box(x, 98.51, y-radius-3., y+radius+3., z-4., z+4.)
        saddle = saddle.cut(zcylinder(radius, x, y, z-4.1, z+4.1),
                              box(x+radius+3., x+radius+5.5, y-2., y+2., z-4.1, z+4.1))
        result[name] = saddle.clean()
    result['gas-check'] = gas_check_support()
    return result



def closure_hardware(x, y, head_seat, insert_top, length=12.):
    """Nominal socket-head envelope and annular full-length M3 insert."""
    screw = zcylinder(1.5, x, y, head_seat-length, head_seat)
    screw = screw.fuse(zcylinder(2.75, x, y, head_seat, head_seat+3.))
    socket = (cq.Workplane('XY').workplane(offset=head_seat+1.5)
              .center(x, y).polygon(6, 2.5/0.8660254037844386).extrude(1.6).val())
    screw = screw.cut(socket).clean()
    insert = zcylinder(2.3, x, y, insert_top-5.7, insert_top).cut(
        zcylinder(1.25, x, y, insert_top-5.8, insert_top+.1))
    return screw, insert


def stacked_well_towers(stock, inner):
    """Front-top's manifold wells, each connected cluster as one tower on its flank.

    Each well's rear-half stock is drawn at its own inboard reach and span. Stacked, two wells
    overlap in height and leave a step and a strip where their inboard faces differ, and a
    print-down soffit under each. One tower takes the envelope of a cluster: one inboard face,
    one span along the wall, and a 45 degree wedge carrying its print-down face to the wall.
    The pockets are still cut at their own stations."""
    towers = []
    for solid in stock.Solids():
        bb = solid.BoundingBox()
        east = bb.xmax > 0.
        wall_x = inner[1] if east else inner[0]
        face_x = bb.xmin if east else bb.xmax
        run = abs(wall_x - face_x)
        wedge = (cq.Workplane('XZ')
                 .polyline([(face_x, bb.zmin), (wall_x, bb.zmin), (wall_x, bb.zmin - run)])
                 .close().extrude(-(bb.ymax - bb.ymin)).val().translate((0., bb.ymin, 0.)))
        towers.append(box(bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax).fuse(wedge))
    result = towers[0]
    for tower in towers[1:]:
        result = result.fuse(tower)
    return result.clean()


def rear_well_tower(stock, ceiling):
    """Back-top's stacked rear-wall wells as one tower over the depth they all share, from the
    lowest well's foot to the ceiling, so no well's top hangs a few millimetres under the next
    well or under the ceiling of a piece that prints ceiling-down. The pockets are cut after."""
    boxes = [solid.BoundingBox() for solid in stock.Solids()]
    x0, x1 = max(b.xmin for b in boxes), min(b.xmax for b in boxes)
    y0, y1 = max(b.ymin for b in boxes), min(b.ymax for b in boxes)
    if x1 <= x0 or y1 <= y0:
        return stock
    return stock.fuse(box(x0, x1, y0, y1, min(b.zmin for b in boxes), ceiling+.01)).clean()


def apply(piece, box_spec, y_side, z_side):
    if z_side != 'top':
        return piece
    import above_core_wiring
    wiring = above_core_wiring.shell_features(y_side+'-top')
    stock = wiring['add']
    if stock is not None and y_side == 'front':
        stock = stacked_well_towers(stock, box_spec.inner)
    if stock is not None and y_side == 'back':
        import enclosure
        stock = rear_well_tower(stock, enclosure.back_top_ceiling_face())
    if stock is not None:
        piece = piece.fuse(stock)
    if wiring['cut'] is not None:
        piece = piece.cut(wiring['cut'])
    if y_side != 'back':
        return piece
    piece = rear_geometry(piece, box_spec.pack.core_holds or (), wiring['cut'])
    piece = rear_identification().apply(piece)
    bosses, holes = wall_bosses()
    for feature in bosses:
        piece = piece.fuse(feature)
    for hole in holes:
        piece = piece.cut(hole)
    for feature in valve_seats().values():
        piece = piece.fuse(feature)
    for feature in fluid_supports().values():
        piece = piece.fuse(feature)
    import _back_top_meter
    # The fore meter/ASSE column has already joined as fluid_supports' asse-2.
    for support in _back_top_meter.meter_supports()[1:]:
        piece = piece.fuse(support)
    # Keep the measured inlet opening clear after all integral mounts join.
    return piece.cut(*c14_rear_cutters())
