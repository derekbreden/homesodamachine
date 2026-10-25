"""Integral above-core shell mounts and the empty electronics roof closure."""

import functools
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'manifold-layout'))
import above_core as layout


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


def access_plan():
    return layout.specification()['electronics_access']


def access_opening():
    p = access_plan()['panel']
    gap = p['edge_clearance_mm']
    bounds = {key: p[key] + (gap if key.endswith('max') else -gap)
              for key in ('xmin', 'xmax', 'ymin', 'ymax')}
    bounds.update(zmin=p['zmin']-.01, zmax=p['zmax']+1)
    return rectangle(bounds, p['corner_radius_mm']+gap)


@functools.cache
def access_panel():
    p, f = access_plan()['panel'], access_plan()['fasteners']
    panel = rectangle(p, p['corner_radius_mm'])
    for x, y in f['centres_xy_mm']:
        panel = panel.cut(zcylinder(f['clearance_hole_diameter_mm']/2, x, y,
                                    p['zmin']-.1, p['zmax']+.1),
                          zcylinder(f['counterbore_diameter_mm']/2, x, y,
                                    f['counterbore_floor_z_mm'], p['zmax']+.1))
    notch = access_plan()['pry_notch']
    cx, half = notch['centre_x_mm'], notch['width_mm']/2
    return panel.cut(box(cx-half, cx+half, p['ymin']-.1,
                         p['ymin']+notch['depth_mm'], p['zmin']-.1,
                         p['zmax']+.1)).clean()


@functools.cache
def access_bosses():
    p, f = access_plan()['panel'], access_plan()['fasteners']
    gap = p['edge_clearance_mm']
    ox, oy0, oy1 = p['xmax']+gap, p['ymin']-gap, p['ymax']+gap
    void = access_opening().intersect(box(-200, 200, 0, 600,
                                         f['bearing_z_mm'], p['zmax']+1))
    result = []
    for x, y in f['centres_xy_mm']:
        front = y < (p['ymin']+p['ymax'])/2
        east = x > (p['xmin']+p['xmax'])/2
        half, reach, root = f['boss_width_mm']/2, f['boss_inner_reach_mm'], f['roof_root_depth_mm']
        inner = f['east_boss_inner_reach_mm'] if east else reach
        x0, x1 = x-half, ox+root if east else x+half
        y0 = oy0-root if front else y-inner
        y1 = y+inner if front else oy1+root
        boss = box(x0, x1, y0, y1, f['boss_bottom_z_mm'], p['zmax']).cut(void)
        boss = boss.cut(zcylinder(f['pilot_diameter_mm']/2, x, y,
                                  f['bearing_z_mm']-f['pilot_depth_mm'],
                                  f['bearing_z_mm']+.1)).clean()
        result.append(boss)
    return tuple(result)


@functools.cache
def relay_bosses():
    sys.path.insert(0, str(HERE.parents[2] / 'reference/teyleten-relay'))
    import teyleten_relay
    bosses, holes = [], []
    for name in ('relay-1', 'relay-2'):
        for hx, hy in teyleten_relay.holes:
            x, y, z = layout.point(layout.pose(name), (hx, hy, 0))
            bosses.append(cq.Solid.makeCylinder(4., 4.02, cq.Vector(-98.52, y, z), cq.Vector(1, 0, 0)))
            holes.append(cq.Solid.makeCylinder(2., 7.51, cq.Vector(-94.49, y, z), cq.Vector(-1, 0, 0)))
    return tuple(bosses), tuple(holes)


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


def keystone_rear_geometry():
    """The enclosure's fitted shoulder, catches and broad corbel at the jack."""
    import enclosure

    jack = enclosure._keystone
    x, y, z = layout.specification()['rear_wall']['dry_openings']['keystone'][
        'face_center_mm']
    root = layout.specification()['rear_wall']['rear_wall']['ymin']
    growth = max(0., enclosure.fits.slip - jack.FIT_SLIP / 2.)
    half_x = jack.POCKET_W / 2. + growth + jack.RECEPTACLE_WALL
    half_z = jack.POCKET_H / 2. + growth + jack.RECEPTACLE_WALL
    fore = y - jack.DEPTH
    centre_z = z + jack.POCKET_RISE
    block = box(x-half_x, x+half_x, fore, root+.01,
                centre_z-half_z, centre_z+half_z)
    stock = enclosure._supported_cut(block, enclosure.BACK_TOP_UP)
    top = centre_z + half_z
    stock = stock.fuse(enclosure._yz_prism(
        x-half_x, x+half_x,
        ((root, top), (fore, top), (root, top+root-fore))))
    cutter, _ = enclosure._keystone_pocket_cut(x, z, y)
    _, catches = jack.receptacle_boss(x, z, y, root)
    return (stock.clean(),
            enclosure._supported_cut(cutter, enclosure.BACK_TOP_UP),
            enclosure._keystone_catches(catches, enclosure.BACK_TOP_UP))


def rear_geometry(piece):
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
    stock, cutter, catches = keystone_rear_geometry()
    piece = piece.fuse(stock).cut(cutter).fuse(catches)
    return piece


def gas_check_support_datums():
    """The purchased check's fixed barrel band, carried into the east bay.

    The body scale and socket depths retain the vendor-reference estimates.
    The eight-millimetre bearing stays inside its fixed cylindrical band. The
    broad sidewall root retains at least three millimetres around its seat.
    """
    sys.path.insert(0, str(HERE.parents[2] / 'reference/neofit-achv44-check'))
    import neofit_achv44_check as check

    first, last, body_radius = check.bearing_band()
    inlet, _ = check.inlet()
    native_centre = (0., inlet[1] + (first + last) / 2., 0.)
    frame = layout.snapshot_pose('gas-check')
    return {
        'centre_world_mm': layout.point(frame, native_centre),
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


@functools.cache
def fluid_supports():
    """Broad, open saddles on fixed roof/wall stock, with separate tie paths.

    The horizontal bodies enter from the open half of each saddle. Gas bodies
    enter from the west. The 0.25 mm radial fit is nominal layout clearance;
    the restraints do not establish pressure capacity or service life.
    """
    result = {}
    z = layout.pose('asse1022-assembly')['translation_mm'][2]
    # Two six-millimetre bearings beside the ASSE's west-facing vent. Their
    # lower planes pass above the populated core during the back-column ride.
    # The east-sector seats retain at least 3.34 mm beneath the circular bore.
    x = 37.25
    for index, y in enumerate((340., 364.), 1):
        radius = 16.75
        saddle = box(x+7.25, x+radius+9., y-3., y+3., 315.92604788, 355.)
        saddle = saddle.cut(ycylinder(radius, x, z, y-3.1, y+3.1))
        saddle = saddle.cut(box(x+radius+3., x+radius+5.5,
                                  y-3.1, y+3.1, z-2., z+2.))
        result[f'asse-{index}'] = saddle.clean()
    # The regulator's two diameters retain their own bearings. Its narrow
    # socket ends and the transverse outlet tube stay free of the supports.
    y = layout.snapshot_pose('reg')['translation_mm'][1]
    for index, x, radius in ((1, -5.3541011287684, 13.75),
                              (2, -29.3541011287684, 12.25)):
        saddle = box(x-3., x+3., y, y+radius+9., z-radius-3., 355.)
        bore = cq.Solid.makeCylinder(radius, 6.2, cq.Vector(x-3.1, y, z), cq.Vector(1, 0, 0))
        saddle = saddle.cut(bore, box(x-3.1, x+3.1, y+radius+3., y+radius+5.5, z-2., z+2.))
        result[f'water-regulator-{index}'] = saddle.clean()
    # Sidewall roots hold the folded, vertical gas pair without loading their
    # interconnecting stem elbows. A closed tie window retains each body.
    for name, y, z, radius in (('gas-regulator', 418.9526, 301., 11.),):
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


def apply(piece, box_spec, y_side, z_side):
    if z_side != 'top':
        return piece
    import above_core_wiring
    wiring = above_core_wiring.shell_features(y_side+'-top')
    if wiring['add'] is not None:
        piece = piece.fuse(wiring['add'])
    if wiring['cut'] is not None:
        piece = piece.cut(wiring['cut'])
    if y_side != 'back':
        return piece
    piece = rear_geometry(piece)
    piece = rear_identification().apply(piece)
    bosses, holes = relay_bosses()
    for feature in bosses:
        piece = piece.fuse(feature)
    for hole in holes:
        piece = piece.cut(hole)
    for feature in valve_seats().values():
        piece = piece.fuse(feature)
    for feature in fluid_supports().values():
        piece = piece.fuse(feature)
    piece = piece.cut(access_opening())
    for boss in access_bosses():
        piece = piece.fuse(boss)
    return piece
