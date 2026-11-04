"""Above-core shell datums and composition of numeric panel recipes."""

import functools
import math
import sys
from pathlib import Path

import _enclosure_datums
_enclosure_datums.install()

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "manifold-layout"))
import above_core as layout
from _enclosure_interface import flute_depth


@functools.cache
def rear_identification():
    sys.path.insert(0, str(HERE.parent / 'rear-identification'))
    import rear_identification as identification
    return identification


def psu_fastener_plan():
    """Four short inserts support the drawing's 6.7 ± 1 mm mounting ears."""
    reach = (10.-7.7, 10.-5.7)
    pilot = 5.
    return {'count':4, 'screw':'M3x10 SHCS', 'screw_length_mm':10.,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'ear_thickness_range_mm':(5.7,7.7), 'receiving_range_mm':reach,
            'pilot_depth_mm':pilot, 'minimum_tip_air_mm':pilot-reach[1],
            'minimum_blind_backing_mm':355.-layout.pose('psu')['translation_mm'][2]-pilot,
            'minimum_fluted_backing_mm':355.-layout.pose('psu')['translation_mm'][2]-pilot,
            'maximum_flute_depth_mm':flute_depth,
            'boss_radius_mm':5., 'pilot_radius_mm':2.,
            'parent':'enclosure-back-top', 'load_retention_qualified':False}


def relay_fastener_plan():
    """Two header-end screws and terminal-end edge rails hold each PCB."""
    setback=2.5
    reach=8.-1.5-setback
    pilot=reach+1.
    return {'count':2, 'active_hole_indices':(0,1),
            'screw':'M3x8 SHCS', 'screw_length_mm':8.,
            'insert':'RX-M3Sx4', 'insert_length_mm':4.,
            'pcb_thickness_mm':1.5, 'receiving_range_mm':(reach,reach),
            'pilot_depth_mm':pilot, 'minimum_tip_air_mm':1.,
            'minimum_blind_backing_mm':min(layout.pose(n)['translation_mm'][0]
                for n in ('relay-1','relay-2'))-setback-pilot+107.5,
            'minimum_fluted_backing_mm':min(layout.pose(n)['translation_mm'][0]
                for n in ('relay-1','relay-2'))-setback-pilot+107.5-flute_depth,
            'maximum_flute_depth_mm':flute_depth,
            'boss_radius_mm':5., 'pilot_radius_mm':2.,
            'insert_face_setback_mm':setback,
            'screw_clearance_radius_mm':1.7,
            'pcb_support':'Four 3 mm edge ledges support the PCB; the terminal pair captures its top edges. The insert faces stand behind the pin envelope.',
            'parent':'enclosure-back-top', 'load_retention_qualified':False}


def wall_mount_datums():
    """Native mounting holes on ceiling PSU bosses and west-wall relay bars."""
    sys.path[:0] = [str(HERE.parents[2]/'reference'/name) for name in ('meanwell-irm90','teyleten-relay')]
    import meanwell_irm90, teyleten_relay
    result = {}
    for name, source, plan in (('psu',meanwell_irm90,psu_fastener_plan()),
            ('relay-1',teyleten_relay,relay_fastener_plan()),
            ('relay-2',teyleten_relay,relay_fastener_plan())):
        stations = []
        axis = layout.vector(layout.pose(name)['rotation'], (0.,0.,1.))
        for index,(hx,hy) in enumerate(source.holes):
            point = layout.point(layout.pose(name),(hx,hy,0.))
            face = tuple(p-plan.get('insert_face_setback_mm',0.)*u for p,u in zip(point,axis))
            root = (point[0],point[1],349.25) if name=='psu' else (-98.52,point[1],point[2])
            stations.append({'native_hole_index':index,'position_world_mm':point,
                'insert_face_world_mm':face,'axis_world':axis,
                'threaded':name=='psu' or index in plan['active_hole_indices'],
                'stock_root_world_mm':root,'stock_root_world_x_mm':root[0],
                'standoff_mm':sum((p-r)*u for p,r,u in zip(point,root,axis))})
        result[name] = {**plan,'stations':tuple(stations)}
    return result


def wall_fastener_bounds():
    """Named screw/insert envelopes on the drilled PSU and relay stations.

    These are the finite mounting lanes through the flank, not clearance
    exemptions for a complete device or for hardware elsewhere in the wall.
    """
    result = {}
    for component, plan in wall_mount_datums().items():
        for number, station in enumerate(plan['stations'], 1):
            if not station['threaded']:
                continue
            axis = station['axis_world']
            point, face = station['position_world_mm'], station['insert_face_world_mm']
            head = tuple(p + u * (6.7 if component == 'psu' else 1.5)
                         for p, u in zip(point, axis))
            for kind, origin, lo, hi, radius in (
                    ('screw', head, -plan['screw_length_mm'], 3., 2.75),
                    ('insert', face, -plan['insert_length_mm'], 0., 2.3)):
                ends = [tuple(p + u * t for p, u in zip(origin, axis)) for t in (lo, hi)]
                radial = [radius * math.sqrt(max(0., 1. - u * u)) for u in axis]
                bounds = (tuple(min(p[i] for p in ends) - radial[i] for i in range(3)),
                          tuple(max(p[i] for p in ends) + radial[i] for i in range(3)))
                result[f'{component}-{kind}-{number}'] = {
                    'component': component, 'parent': plan['parent'], 'kind': kind,
                    'station': station, 'plan': plan, 'bounds_mm': bounds}
    return result


def in_wall_fastener_lane(name, bounds, tolerance=1e-5):
    """Whether this named hardware stays inside its own drilled mounting lane."""
    row = wall_fastener_bounds().get(name)
    if row is None:
        return False
    lo, hi = row['bounds_mm']
    return all(bounds[i] >= lo[i] - tolerance and
               bounds[i + 3] <= hi[i] + tolerance for i in range(3))


def c14_fastener_plan():
    """The washer bridges the inlet's native countersink under a socket head."""
    return {'screw_length_mm': 10., 'washer_od_mm': 7., 'washer_thickness_mm': .5,
            'flange_thickness_mm': 3.25, 'insert_length_mm': 4.,
            'screw_reach_mm': 6.25, 'pilot_depth_mm': 7.25,
            'boss_depth_mm': 10.25, 'tip_air_mm': 1., 'backing_mm': 3.}


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


# The panel recorder supplies these graph factories while it records the recipe.
box = rectangle = ycylinder = zcylinder = rear_well_tower = wall_bosses = valve_seats = c14_rear_cutters = keystone_rear_geometry = fluid_supports = stacked_well_towers = None


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
    # Keep the measured inlet opening clear after all integral mounts join.
    return piece.cut(*c14_rear_cutters())
