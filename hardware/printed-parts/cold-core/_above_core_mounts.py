"""Cold-core equipment mounts carried by the production above-core datums.

Coordinates returned here belong to the top cap and lid before their installed
half turn. Component mounting holes come from their native references; the
appliance placement belongs to ``manifold-layout/above_core.py``.
"""

from functools import lru_cache
import importlib
import itertools
import math
from collections import namedtuple
from pathlib import Path
import sys


HW = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
for path in (
    HW / 'manifold-layout',
    HW / 'printed-parts' / 'valve-seat',
    HW / 'printed-parts' / 'electronics' / 'pcba-tray',
    HW / 'reference' / 'meanwell-irm90',
    HW / 'reference' / 'g-ganen-pump' / 'installation',
    HW / 'reference' / 'neofit-achv44-check',
    HW / 'reference' / 'digiten-flow-sensor',
    HW / 'reference' / 'neofit-stem-elbow',
    HW / 'printed-parts' / 'cold-core' / 'reservoir',
):
    sys.path.insert(0, str(path))

import above_core


DeckMount = namedtuple('DeckMount', 'points standoff seat screw seat_min')


def _multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3))
                       for j in range(3)) for i in range(3))


def component_in_cap(name):
    """Native component frame carried into the uninstalled cap/lid frame."""
    frame = above_core.pose(name)
    cap = above_core.cap_lid_pose()
    return {
        'rotation': _multiply(tuple(zip(*cap['rotation'])), frame['rotation']),
        'translation_mm': above_core.world_to_cap(frame['translation_mm']),
    }


def lid_face_z():
    """Plain lid bearing face in the lid's native coordinate frame."""
    face = above_core.specification()['cap_face_z_mm']
    return above_core.world_to_cap((0.0, 0.0, face))[2]


def mounting_points(name, holes):
    """Native mounting-hole points at their cap XY stations."""
    frame = above_core.pose(name)
    return tuple(above_core.world_to_cap(above_core.point(frame, (x, y, 0.0)))[:2]
                 for x, y in holes)


def _standoff(name):
    # Reference meshes retain micrometre rounding; mounting seats use the
    # stated plain cap face and the native module's mounting datum.
    return round(component_in_cap(name)['translation_mm'][2] - lid_face_z(), 4) or 0.0


@lru_cache(maxsize=1)
def deck_mounts():
    """Cup-rooted columns compatible with the cap's deck-mount construction.

    The PCB's columns pass through the lid to its underside. The PSU and pump
    bear on the lid above flush columns. All use RX-M3x5.7 inserts. The PCB's
    M3x8 screws cross its 1.6 mm board; the flat PSU's M3x20 screws cross its
    6.7 ± 1 mm ledges and the lid. The minimum ear thickness sizes the blind
    pilot; the maximum still engages the complete insert. The pump retains
    its measured pad/washer stack.
    """
    pcb = importlib.import_module('pcba_tray')
    psu = importlib.import_module('meanwell_irm90')
    pump = importlib.import_module('g_ganen_installation')
    return {
        'g-ganen-pump': DeckMount(
            mounting_points('g-ganen-pump', pump.mount_holes()),
            _standoff('g-ganen-pump'),
            pump.observed_pad_upper_z() + pump.WASHER_T,
            pump.SCREW_LENGTH,
            pump.observed_pad_lower_z() + pump.WASHER_T),
        'pcba': DeckMount(
            mounting_points('pcba', pcb.board.holes), _standoff('pcba'),
            pcb._thickness, 8.0, pcb._thickness),
        'psu': DeckMount(
            mounting_points('psu', psu.holes), _standoff('psu'),
            psu.ledge_h, 20.0, psu.ledge_h - 1.0),
    }


def valve_support_datums(name, face_z=None):
    """World stock limits; full sockets above a core-footprint-clipped root."""
    seat = importlib.import_module('valve_seat')
    core = importlib.import_module('_cold_core_interface')
    frame = above_core.pose(name)
    limits = ((-seat.seat_half_x, seat.seat_half_x),
              (-seat.seat_half_y, seat.seat_half_y),
              (seat.socket_floor_z-seat.wall,seat.seat_top_z))
    corners = [above_core.point(frame,point) for point in itertools.product(*limits)]
    low = tuple(min(point[i] for point in corners) for i in range(3))
    high = tuple(max(point[i] for point in corners) for i in range(3))
    face = above_core.specification()['cap_face_z_mm'] if face_z is None else (
        above_core.point(above_core.cap_lid_pose(),(0.,0.,face_z))[2])
    half = core.outer_shell_y_length/2.
    root_high = (min(half,high[0]),high[1],low[2])
    data = {'bearing_min_world_mm':low,'bearing_max_world_mm':high,
            'root_min_world_mm':(max(-half,low[0]),low[1],face),
            'socket_backing_mm':seat.wall}
    if name in ('valve-v-a','vk-solenoid'):
        elbow = importlib.import_module('neofit_stem_elbow')
        port_y = above_core.point(frame,(0.,0.,seat.valve.port_center_z))[1]
        # One broad aft relief clears the lower valve barrel and the attached
        # elbow collar. It ends at the complete socket plate's lower face.
        aft = port_y-max(seat.valve.port_radius,elbow.COLLAR_OD/2.)-seat.fits.slip
        root_high = (root_high[0],aft,root_high[2])
        data.update(port_throat_aft_world_y_mm=aft,
                    port_throat_clearance_mm=seat.fits.slip)
    data['root_max_world_mm'] = root_high
    data['root_depth_mm'] = root_high[1]-low[1]
    return data


def valve_support(name, face_z=None):
    """One integral upright valve wall, rooted on the plain lid face.

    The shared valve seat owns the socket diameter, bearing plane and port
    channel. Three millimetres of stock backs each blind socket floor. The
    wall reaches down to the lid without a separate foot or fastening part.
    V-A and V-K have a flat aft relief below the complete socket plate for
    their lower port barrels and attached NeoFit elbows.
    """
    import cadquery as cq

    seat = importlib.import_module('valve_seat')
    data = valve_support_datums(name,face_z)
    def block(low,high):
        return cq.Solid.makeBox(*(high[i]-low[i] for i in range(3)),cq.Vector(*low))
    wall = block(data['bearing_min_world_mm'],data['bearing_max_world_mm']).fuse(
        block(data['root_min_world_mm'],data['root_max_world_mm']))
    location = above_core.location(name)
    sockets = seat.build_sockets().val().moved(location)
    channel = seat.build_port_channel(2.0 * seat.seat_half_y + 2.0).val().moved(location)
    return world_shape_in_cap(wall.cut(sockets,channel).clean())


def vb_support(face_z=None):
    return valve_support('valve-v-b',face_z)


def _check_bearing_station():
    """Midpoint of the shared ACHV44-E reference's fixed cylindrical band."""
    check = importlib.import_module('neofit_achv44_check')
    first, last, radius = check.bearing_band()
    inlet, outward = check.inlet()
    distance = (first + last) / 2.
    point = tuple(p - distance * a for p, a in zip(inlet, outward))
    return point, radius, first, last


def check_anchor():
    """Fixed-barrel tie station; both operating collets remain outside the seat."""
    native, radius, _first, _last = _check_bearing_station()
    point = above_core.point(component_in_cap('discharge-chain'), native)
    return point[:2], radius, point[2] - lid_face_z()


def check_support_datums():
    """East quarter bearing and aft root, leaving the west PSU face clear."""
    import fits
    core = importlib.import_module('_cold_core_interface')
    pump = importlib.import_module('g_ganen_installation')
    foot = importlib.import_module('g_ganen_foot')
    check = importlib.import_module('neofit_achv44_check')
    native, band_radius, first, last = _check_bearing_station()
    centre = above_core.point(above_core.pose('discharge-chain'), native)
    head_x = min(row['station_mm'][0] for row in pump.mount_stations())
    foot_aft = above_core.point(above_core.pose('g-ganen-pump'),
                                (head_x+foot.WIDTH/2.,0.,0.))[1]
    radius = max(row[1] for row in check.sections())+fits.slip
    outlet = above_core.point(above_core.pose('discharge-chain'),check.outlet()[0])
    pump_mounts = [above_core.point(above_core.pose('g-ganen-pump'),row['station_mm'])
                   for row in pump.mount_stations()]
    driver = min(pump_mounts,key=lambda p:math.dist(p[:2],centre[:2]))
    tool_radius = 2.5/math.sqrt(3.)+fits.slip
    notch_radius = tool_radius+fits.slip
    return {'centre_world_mm': centre,
            'fixed_band_from_inlet_mm': (first, last),
            'bearing_from_inlet_mm': ((first+last-core.cap_anchor_len)/2.,
                                     (first+last+core.cap_anchor_len)/2.),
            'fixed_band_radius_mm': band_radius,
            'root_fore_y_mm': foot_aft+1.,
            # The flat aft face stays in front of the outlet's stem-elbow
            # shoulder while retaining the foot's independent driver lane.
            'root_aft_y_mm': min(foot_aft+6.,outlet[1]-fits.slip),
            'bearing_fore_y_mm': centre[1]-core.cap_anchor_len/2.,
            'half_width_mm': radius+3.,
            'stock_x_limits_world_mm': (centre[0],centre[0]+radius+3.),
            'bridge_bottom_world_z_mm': centre[2]-radius-3.,
            'open_direction': 'west-and-up',
            'pump_driver_axis_world_mm': driver,
            'pump_driver_radius_mm': tool_radius,
            'tool_notch_max_x_mm': driver[0]+notch_radius,
            'tool_notch_y_mm': (driver[1]-notch_radius,driver[1]+notch_radius),
            'wall_mm': 3.}


def check_support():
    """Lid-rooted east quarter bearing with a west-open pump-tool notch."""
    import cadquery as cq
    import fits

    check = importlib.import_module('neofit_achv44_check')
    data = check_support_datums()
    x,y,z = data['centre_world_mm']
    low_x,high_x = data['stock_x_limits_world_mm']
    root = cq.Solid.makeBox(high_x-low_x,
        data['root_aft_y_mm']-data['root_fore_y_mm'],
        z-above_core.specification()['cap_face_z_mm'],
        cq.Vector(low_x,data['root_fore_y_mm'],above_core.specification()['cap_face_z_mm']))
    beam = cq.Solid.makeBox(high_x-low_x,
        data['root_aft_y_mm']-data['bearing_fore_y_mm'],
        z-data['bridge_bottom_world_z_mm'],
        cq.Vector(low_x,data['bearing_fore_y_mm'],data['bridge_bottom_world_z_mm']))
    support = root.fuse(beam)
    y0,y1 = data['tool_notch_y_mm']
    notch = cq.Solid.makeBox(data['tool_notch_max_x_mm']-low_x+1.,y1-y0,
                             z-data['bridge_bottom_world_z_mm']+2.,
                             cq.Vector(low_x-1.,y0,data['bridge_bottom_world_z_mm']-1.))
    support = support.cut(notch)
    frame = above_core.frame_location(above_core.pose('discharge-chain'))
    inlet, outward = check.inlet()
    direction = tuple(-a for a in outward)
    for _name,radius,start,end in check.sections():
        origin = tuple(p + start*a for p,a in zip(inlet,direction))
        bore = cq.Solid.makeCylinder(radius+fits.slip,end-start,
                                     cq.Vector(*origin),cq.Vector(*direction)).moved(frame)
        support = support.cut(bore)
    return world_shape_in_cap(support.clean())


def meter_support_datums():
    """Fixed-collar quarter bearings, open upward and west for drop-in assembly."""
    import fits
    meter = importlib.import_module('digiten_flow_sensor')
    frame = above_core.pose('digiten-flow')
    _start, end, r0, r1 = meter.mounting_profile(1)[-1]
    axial = (_start+end)/2.
    radius, wall = max(r0,r1)+fits.slip, 3.
    rows = []
    for side in (-1,1):
        # The aft bearing uses the fore portion of its 7.2 mm fixed collar.
        # Its full 6 mm width leaves 0.1 mm before the collar's fore edge.
        station = side*axial - (.5 if side == 1 else 0.)
        x,y,z = above_core.point(frame,(station,0.,0.))
        rows.append({'centre_world_mm': (x,y,z), 'width_mm': 6.,
                     'seat_radius_mm': radius, 'wall_mm': wall,
                     'native_bearing_band_mm': (station-3.,station+3.),
                     'root_bottom_world_z_mm': above_core.specification()['cap_face_z_mm'],
                     'stock_top_world_z_mm': z,
                     'tie_window_world_mm': (x+wall+.1,x+wall+.1+2.8,
                                              z-radius-8.,z-radius-6.)})
        if side == -1:
            # One flat step clears the fore pump foot, head approach and the
            # selected foam sleeve, whose top is Z279.5. The east root remains
            # 4.6 mm thick across the full bearing width.
            rows[-1]['lower_root_min_x_mm'] = x+7.7
            rows[-1]['lower_root_top_z_mm'] = 280.
        else:
            # A straight central wall passes between the two fixed reservoir
            # tubes. The broad lower base carries the complete closed tie slot.
            rows[-1]['central_root_min_x_mm'] = x+4.1
            rows[-1]['central_root_width_mm'] = 3.
            rows[-1]['base_top_z_mm'] = 271.
            rows[-1]['tie_window_world_mm'] = (x+3.1,x+5.9,266.,268.)
    return tuple(rows)


def meter_supports():
    """Native-lid solids for the fixed flow-meter collars and their ties."""
    import cadquery as cq
    rows = []
    for data in meter_support_datums():
        x,y,z = data['centre_world_mm']
        r,w,half = data['seat_radius_mm'],data['wall_mm'],data['width_mm']/2.
        stock = cq.Solid.makeBox(r+w,2.*half,
                                 data['stock_top_world_z_mm']-data['root_bottom_world_z_mm'],
                                 cq.Vector(x,y-half,data['root_bottom_world_z_mm']))
        if 'central_root_min_x_mm' in data:
            outer = cq.Solid.makeCylinder(
                r+w,2.*half,cq.Vector(x,y-half,z),cq.Vector(0,1,0))
            quarter = outer.intersect(stock)
            root = cq.Solid.makeBox(
                data['central_root_width_mm'],2.*half,
                z-data['root_bottom_world_z_mm'],
                cq.Vector(data['central_root_min_x_mm'],y-half,
                          data['root_bottom_world_z_mm']))
            base = cq.Solid.makeBox(
                r+w,2.*half,
                data['base_top_z_mm']-data['root_bottom_world_z_mm'],
                cq.Vector(x,y-half,data['root_bottom_world_z_mm']))
            stock = quarter.fuse(root,base)
        if 'lower_root_min_x_mm' in data:
            step = cq.Solid.makeBox(
                data['lower_root_min_x_mm']-x+.1,2.*half+.2,
                data['lower_root_top_z_mm']-data['root_bottom_world_z_mm']+.1,
                cq.Vector(x-.1,y-half-.1,data['root_bottom_world_z_mm']-.1))
            stock = stock.cut(step)
        bore = cq.Solid.makeCylinder(r,2.*half+.2,cq.Vector(x,y-half-.1,z),cq.Vector(0,1,0))
        x0,x1,z0,z1 = data['tie_window_world_mm']
        window = cq.Solid.makeBox(x1-x0,2.*half+.2,z1-z0,cq.Vector(x0,y-half-.1,z0))
        rows.append(world_shape_in_cap(stock.cut(bore,window).clean()))
    return tuple(rows)


def _jg_band_radius(leg, first, last):
    """Largest observed fixed-body radius over a named bearing band."""
    import json
    rows = json.loads((HW / 'reference' / 'jg-pp0308e-elbow' /
                       'scan-measurements.json').read_text())['profiles'][leg]['fixed_body']
    return max(radius for station,radius in rows if first <= station <= last)


def union_support_datums():
    """World-frame stock and tie windows for the core-owned union elbows.

    Fixed body bands carry the fitting; their moving collets remain outside
    the bearing. The short V-A quarter bearing sits below the pump head. V-B uses a
    short ledge rooted aft of the PCB.
    """
    import fits
    face = above_core.specification()['cap_face_z_mm']-.15
    x,y,z = above_core.snapshot_pose('va-east-turn')['translation_mm']
    radius = _jg_band_radius('z',8.5,11.5)+fits.slip
    yy = y-10.
    va = {'stock_min_world_mm':(x-radius-9.,yy-1.5,face),
          'stock_max_world_mm':(x,yy+1.5,z),
          'bore_origin_world_mm':(x,yy-1.6,z),
          'bore_axis_world':(0.,1.,0.), 'bore_length_mm':3.2,
          'seat_radius_mm':radius,'native_leg':'z','native_band_mm':(8.5,11.5),
          'tie_window_min_world_mm':(x-radius-5.8,yy-1.6,z-7.),
          'tie_window_max_world_mm':(x-radius-3.,yy+1.6,z-4.5),
          'wall_mm':3.,'parent':'foam-assembly'}
    frame = above_core.snapshot_pose('vb-outlet-return')
    centre = above_core.point(frame,(0.,14.5,0.))
    radius = _jg_band_radius('y',13.,16.)+fits.slip
    bottom = centre[2]-radius-3.
    pcb = importlib.import_module('pcba_tray')
    board_aft = max(above_core.point(above_core.pose('pcba'),
        (px-pcb._centre[0],py-pcb._centre[1],0.))[1]
        for px in pcb._outline_x for py in pcb._outline_y)
    plate_x = round(centre[0],1)-.8
    # The broad root sits aft of the PCB's eight-millimetre wire-entry lands.
    root_fore = max(round(board_aft,1)+7.5,centre[1]+4.)
    root_aft = root_fore+3.
    root_x = plate_x+1.
    window_top = round(bottom,1)-.3
    vb = {'stock_min_world_mm':(plate_x,centre[1],bottom),
          'stock_max_world_mm':(plate_x+3.,centre[1]+radius+3.,centre[2]),
          'beam_min_world_mm':(plate_x,centre[1],bottom),
          'beam_max_world_mm':(root_x+9.,root_aft,bottom+3.),
          'root_min_world_mm':(root_x,root_fore,face),
          'root_max_world_mm':(root_x+9.,root_aft,bottom+3.),
          'bore_origin_world_mm':above_core.point(frame,(0.,8.,0.)),
          'bore_axis_world':above_core.vector(frame['rotation'],(0.,1.,0.)),
          'bore_length_mm':13.,'seat_radius_mm':radius,
          'native_leg':'y','native_band_mm':(13.,16.),
          'tie_window_min_world_mm':(root_x+3.1,root_fore-.1,window_top-2.8),
          'tie_window_max_world_mm':(root_x+5.9,root_aft+.1,window_top),
          'wall_mm':3.,'parent':'foam-assembly'}
    return {'va-east-turn': va, 'vb-outlet-return': vb}


def union_supports():
    """Broad native-cap bearings; no purchased fitting or tie is fused in."""
    import cadquery as cq
    result = {}
    for name,data in union_support_datums().items():
        low,high = data['stock_min_world_mm'],data['stock_max_world_mm']
        stock = cq.Solid.makeBox(*(high[i]-low[i] for i in range(3)),cq.Vector(*low))
        for prefix in ('beam','root'):
            if prefix+'_min_world_mm' in data:
                low,high = data[prefix+'_min_world_mm'],data[prefix+'_max_world_mm']
                stock = stock.fuse(cq.Solid.makeBox(
                    *(high[i]-low[i] for i in range(3)),cq.Vector(*low)))
        bore = cq.Solid.makeCylinder(data['seat_radius_mm'],data['bore_length_mm'],
                                    cq.Vector(*data['bore_origin_world_mm']),
                                    cq.Vector(*data['bore_axis_world']))
        result[name] = world_shape_in_cap(stock.cut(bore).clean())
    return result


def union_support_cuts():
    """Closed tie passages, applied after the bearings join their lid hosts."""
    import cadquery as cq
    result = {}
    for name,data in union_support_datums().items():
        low,high = data['tie_window_min_world_mm'],data['tie_window_max_world_mm']
        result[name] = world_shape_in_cap(cq.Solid.makeBox(
            *(high[i]-low[i] for i in range(3)),cq.Vector(*low)))
    return result



def _tie_arc_point(centre, u, v, radius, angle):
    angle = math.radians(angle)
    return tuple(centre[i] + radius * (u[i] * math.cos(angle) + v[i] * math.sin(angle))
                 for i in range(3))


def _tie_line(first, last, wide_axis=(0., 0., 1.)):
    return {'kind': 'line', 'points_mm': [first, last], 'wide_axis': wide_axis}


def _tie_arc(centre, u, v, radius, first, last):
    normal = (u[1] * v[2] - u[2] * v[1],
              u[2] * v[0] - u[0] * v[2],
              u[0] * v[1] - u[1] * v[0])
    return {
        'kind': 'arc',
        'points_mm': [_tie_arc_point(centre, u, v, radius, angle)
                      for angle in (first, (first + last) / 2., last)],
        'radius_mm': radius,
        'sweep_degrees': last - first,
        'wide_axis': normal,
    }


def _tie_length(segments):
    return sum(math.dist(*row['points_mm']) if row['kind'] == 'line'
               else row['radius_mm'] * abs(math.radians(row['sweep_degrees']))
               for row in segments)


def check_tie_route():
    """Closed nominal strip around the fixed water barrel and quarter bearing.

    Its width follows the barrel axis. The strip threads beneath the bridge,
    through the open space above the lid; no printed tie window is required.
    Head engagement, bend transitions and purchased dimensions are unqualified.
    """
    data = check_support_datums()
    x,y,z = data['centre_world_mm']
    allowance = .55             # half the 0.8 mm strip plus 0.15 mm air
    radius = data['fixed_band_radius_mm']+allowance
    w = data['stock_x_limits_world_mm'][1]-x+allowance
    h = z-data['bridge_bottom_world_z_mm']+allowance
    left = (-allowance,-h)
    left_angle = math.atan2(left[1],left[0])-math.acos(radius/math.hypot(*left))
    right_angle = math.acos(radius/w)
    centre,u,v = (x,y,z),(1.,0.,0.),(0.,0.,1.)
    first = (x+left[0],y,z+left[1])
    lower_east = (x+w,y,z-h)
    upper_east = (x+w,y,z)
    right = _tie_arc_point(centre,u,v,radius,math.degrees(right_angle))
    last = _tie_arc_point(centre,u,v,radius,math.degrees(left_angle))
    segments = [
        _tie_line(first,lower_east,(0.,1.,0.)),
        _tie_line(lower_east,upper_east,(0.,1.,0.)),
        _tie_line(upper_east,right,(0.,1.,0.)),
        _tie_arc(centre,u,v,radius,math.degrees(right_angle),
                 math.degrees(left_angle)+360.),
        _tie_line(last,first,(0.,1.,0.)),
    ]
    return {
        'segments': segments,
        'length_mm': _tie_length(segments),
        'stock': '6-inch narrow nylon tie',
        'stock_length_mm': 152.4,
        'width_mm': 2.5,
        'thickness_mm': .8,
        'fixed_band_plane_world_y_mm': y,
        'threading_height_mm': (data['bridge_bottom_world_z_mm']
                                -above_core.specification()['cap_face_z_mm']),
        'strip_basis': 'Nominal layout allowance; purchased strap/head dimensions unmeasured',
    }


def _va_union_tie(data):
    x, y, z = above_core.snapshot_pose('va-east-turn')['translation_mm']
    y -= 10.
    radius = data['seat_radius_mm'] + .4
    centre, u, v = (x, y, z), (1., 0., 0.), (0., 0., 1.)
    low, high = data['stock_min_world_mm'], data['stock_max_world_mm']
    first, last = data['tie_window_min_world_mm'], data['tie_window_max_world_mm']
    wx, wz = (first[0] + last[0]) / 2., (first[2] + last[2]) / 2.
    window_fore = (wx, low[1] - .6, wz)
    window_aft = (wx, high[1] + 1.4, wz)
    upper = _tie_arc_point(centre, u, v, radius, 175.)
    lower = _tie_arc_point(centre, u, v, radius, -90.)
    west_upper = (low[0] - 1.4, y, upper[2])
    fore_upper = (low[0] - 1.4, low[1] - .6, upper[2])
    fore_lower = (low[0] - 1.4, low[1] - .6, wz)
    east_lower = (x + 1.4, y, lower[2])
    aft_lower = (x + 1.4, high[1] + 1.4, lower[2])
    return [
        _tie_line(window_aft, window_fore, (1., 0., 0.)),
        _tie_line(window_fore, fore_lower),
        _tie_line(fore_lower, fore_upper, (1., 0., 0.)),
        _tie_line(fore_upper, west_upper, (1., 0., 0.)),
        _tie_line(west_upper, upper, (0., 1., 0.)),
        _tie_arc(centre, u, v, radius, 175., -90.),
        _tie_line(lower, east_lower, (0., 1., 0.)),
        _tie_line(east_lower, aft_lower, (1., 0., 0.)),
        _tie_line(aft_lower, window_aft, (0., 1., 0.)),
    ]


def _vb_union_tie(data):
    frame = above_core.snapshot_pose('vb-outlet-return')
    centre = above_core.point(frame, (0., 14.5, 0.))
    u = (0., 1., 0.)
    v = tuple(-value for value in above_core.vector(frame['rotation'], (1., 0., 0.)))
    radius = data['seat_radius_mm'] + .55
    upper = _tie_arc_point(centre, u, v, radius, 20.)
    lower = _tie_arc_point(centre, u, v, radius, 260.)
    first, last = data['tie_window_min_world_mm'], data['tie_window_max_world_mm']
    wx, wz = (first[0]+last[0])/2., (first[2]+last[2])/2.
    fore_y, aft_y = first[1]-.5, last[1]+1.3
    west_x = data['stock_min_world_mm'][0]-1.4
    east_x = data['root_max_world_mm'][0]+1.4
    window_fore, window_aft = (wx,fore_y,wz), (wx,aft_y,wz)
    west_lower = (west_x,fore_y,wz)
    rear_y = data['stock_max_world_mm'][1]+2.2
    west_rear = (west_x,rear_y,wz)
    west_upper = (west_x,rear_y,math.ceil(data['stock_max_world_mm'][2]+2.))
    axis = above_core.vector(frame['rotation'],(0.,1.,0.))
    east_lower = (east_x,lower[1],wz-4.3)
    east_aft = (east_x,aft_y,wz)
    return [
        _tie_line(window_aft, window_fore, (1., 0., 0.)),
        _tie_line(window_fore, west_lower),
        _tie_line(west_lower, west_rear, (1., 0., 0.)),
        _tie_line(west_rear, west_upper, (1., 0., 0.)),
        _tie_line(west_upper, upper, axis),
        _tie_arc(centre, u, v, radius, 20., 260.),
        _tie_line(lower, east_lower, (0., 1., 0.)),
        _tie_line(east_lower, east_aft, (1., 0., 0.)),
        _tie_line(east_aft, window_aft),
    ]


def union_tie_routes():
    """Explicit nominal strip routes and their measured line/arc lengths.

    The 2.5 x 0.8 mm strip sections are layout allowances. Individual native
    segments are clearance probes; bend/twist transitions, purchased strap
    dimensions, threading, head engagement and retention remain unqualified.
    """
    data = union_support_datums()
    builders = {'va-east-turn': _va_union_tie,
                'vb-outlet-return': _vb_union_tie}
    result = {}
    for name, builder in builders.items():
        segments = builder(data[name])
        result[name] = {
            'segments': segments,
            'length_mm': _tie_length(segments),
            'stock': '6-inch narrow nylon tie',
            'stock_length_mm': 152.4,
            'width_mm': 2.5,
            'thickness_mm': .8,
            'strip_basis': 'Nominal layout allowance; purchased strap dimensions unmeasured',
        }
    return result


def meter_tie_routes():
    """Closed nominal retaining-strip paths through the two meter windows.

    The 2.5 × 0.8 mm section is a layout allowance. Purchased strap/head
    dimensions, bend/twist transitions, threading and retention are unqualified.
    The aft path uses the neck plane beside the offset round housing.
    """
    result = {}
    for number, data in enumerate(meter_support_datums()):
        x, y, z = data['centre_world_mm']
        x0, x1, z0, z1 = data['tie_window_world_mm']
        wx, wz = (x0+x1)/2., (z0+z1)/2.
        radius = data['seat_radius_mm']+.6
        phi = math.atan2(wz-z, wx-x)
        alpha = math.acos(radius/math.hypot(wx-x, wz-z))
        west_angle = math.degrees(phi-alpha) % 360.
        east_angle = math.degrees(phi+alpha)
        centre = (x, y+(.6 if number == 0 else 0.), z)
        u, v = (1., 0., 0.), (0., 0., 1.)
        window_fore, window_aft = (wx, y-3.8, wz), (wx, y+3.8, wz)
        west_plane = y-4.7148 if number == 0 else y-8.6
        east_plane = y+4.6
        east_centre = (x, east_plane, z)
        east_low = (wx, east_plane, wz)
        east_tangent = _tie_arc_point(east_centre, u, v, radius, east_angle)
        high_east = _tie_arc_point(east_centre, u, v, radius, 15.)
        high = _tie_arc_point(centre, u, v, radius, 15.)
        west = _tie_arc_point(centre, u, v, radius, west_angle)
        west_fore = (west[0], west_plane, west[2])
        split = tuple(west_fore[i]+.2*(window_fore[i]-west_fore[i])
                      for i in range(3))
        west_wide = (-math.sin(math.radians(west_angle)), 0.,
                     math.cos(math.radians(west_angle)))
        east_wide = (-math.sin(math.radians(15.)), 0.,
                     math.cos(math.radians(15.)))
        segments = [
            _tie_line(window_fore, window_aft, (1., 0., 0.)),
            _tie_line(window_aft, east_low, (1., 0., 0.)),
            _tie_line(east_low, east_tangent, (1., 0., 0.)),
            _tie_arc(east_centre, u, v, radius, east_angle, 15.),
            _tie_line(high_east, high, east_wide),
            _tie_arc(centre, u, v, radius, 15., west_angle),
            _tie_line(west, west_fore, west_wide),
            _tie_line(west_fore, split, (0., 1., 0.)),
            _tie_line(split, window_fore, (1., 0., 0.)),
        ]
        if number == 1:
            west_angle = 240.
            west = _tie_arc_point(centre, u, v, radius, west_angle)
            neck_y = y-3.6148
            neck_z = data['root_bottom_world_z_mm']+43.4
            neck = (west[0], neck_y, neck_z)
            corner, low = (wx, neck_y, neck_z), (wx, neck_y, wz)
            west_wide = (-math.sin(math.radians(west_angle)), 0.,
                         math.cos(math.radians(west_angle)))
            segments = segments[:5]+[
                _tie_arc(centre, u, v, radius, 15., west_angle),
                _tie_line(west, neck, west_wide),
                _tie_line(neck, corner, (0., 0., 1.)),
                _tie_line(corner, low, (1., 0., 0.)),
                _tie_line(low, window_fore, (1., 0., 0.)),
            ]
        result['meter-'+('fore' if number == 0 else 'aft')] = {
            'segments': segments,
            'length_mm': _tie_length(segments),
            'stock_length_mm': 152.4,
            'width_mm': 2.5,
            'thickness_mm': .8,
            'collar_plane_world_y_mm': centre[1],
            'strip_basis': 'Nominal layout section; purchased strap/head dimensions unmeasured',
        }
    return result


def nominal_tie_strips():
    """World-frame flat-section witnesses for the retaining-strip paths.

    These segment compounds use the nominal section in the route data. They
    are clearance witnesses, not manufactured ties; purchased dimensions,
    bend/twist transitions, threading, head engagement and retention are
    unqualified. No printable stock includes these shapes.
    """
    import cadquery as cq

    result = {}
    routes = {**union_tie_routes(), **meter_tie_routes(),
              'water-check':check_tie_route()}
    for name, data in routes.items():
        pieces = []
        for segment in data['segments']:
            if segment['kind'] == 'arc':
                edge = cq.Edge.makeThreePointArc(
                    *(cq.Vector(*point) for point in segment['points_mm']))
                wire = cq.Wire.assembleEdges([edge])
                plane = cq.Plane(origin=edge.startPoint(),
                                 normal=edge.tangentAt(0),
                                 xDir=cq.Vector(*segment['wide_axis']))
                piece = (cq.Workplane(plane)
                         .rect(data['width_mm'], data['thickness_mm'])
                         .sweep(wire, isFrenet=True, transition='round').val())
            else:
                first, last = (cq.Vector(*point) for point in segment['points_mm'])
                tangent = (last-first).normalized()
                wide = cq.Vector(*segment['wide_axis'])
                wide = (wide-tangent*wide.dot(tangent)).normalized()
                thin = tangent.cross(wide).normalized()

                def rectangle(at):
                    return cq.Wire.makePolygon([
                        at+wide*w+thin*t for w, t in (
                            (-data['width_mm']/2., -data['thickness_mm']/2.),
                            (data['width_mm']/2., -data['thickness_mm']/2.),
                            (data['width_mm']/2., data['thickness_mm']/2.),
                            (-data['width_mm']/2., data['thickness_mm']/2.))],
                        close=True)

                piece = cq.Solid.makeLoft(
                    [rectangle(first), rectangle(last)], ruled=True)
            pieces.append(piece)
        result[name] = cq.Compound.makeCompound(pieces)
    return result


def gas_guide_xy():
    """Selected gas guide in the top cap/lid's native XY frame."""
    return above_core.world_to_cap(above_core.specification()['gas_guide_world_mm'])[:2]


def cap_guide_xy(name, fallback):
    """Selected upper guide; reservoir entry bores retain their native stations."""
    point = above_core.specification()['cap_guides_world_mm'].get(name)
    return fallback if point is None else above_core.world_to_cap(point)[:2]


def world_shape_in_cap(shape):
    """Carry a world-frame solid into the native top-lid frame."""
    frame = above_core.cap_lid_pose()
    rotation = tuple(zip(*frame['rotation']))
    translation = above_core.vector(rotation, tuple(-v for v in frame['translation_mm']))
    return shape.moved(above_core.frame_location({
        'rotation': rotation, 'translation_mm': translation}))


def passive_guide_points(lower_xy, upper_xy, start_z, end_z, bend_start_z, radius=14.0):
    """Two shallow stock-radius turns between a reservoir bore and its upper guide.

    Coordinates and heights belong to the shell. The bend starts just above the
    original cup floor; both end tangents remain vertical.
    """
    distance = math.dist(lower_xy, upper_xy)
    if distance < 1e-9:
        return [(*lower_xy, start_z), (*upper_xy, end_z)]
    theta = math.acos(1.0 - distance / (2.0 * radius))
    setback = radius * math.tan(theta / 2.0)
    rise = 2.0 * radius * math.sin(theta)
    return [(*lower_xy, start_z),
            (*lower_xy, bend_start_z + setback),
            (*upper_xy, bend_start_z + rise - setback),
            (*upper_xy, end_z)]


def cable_guide_points(name):
    """Flexible loom corridor in world XYZ, retaining the original lower entry.

    The horizontal station clears the cup floor and finishes both 5.5 mm turns
    below the lid. Reed B and the sensor loom pass around the equipment insert
    columns. The radius specifies a printed passage, not cable qualification.
    """
    core = importlib.import_module('_cold_core_interface')
    spec = above_core.specification()
    lower_xy = above_core.point(above_core.cap_lid_pose(),
                               (*core.cap_conduit_floor_xy[name], 0.))[:2]
    upper_xy = above_core.point(above_core.cap_lid_pose(),
                               (*core.cap_conduits[name], 0.))[:2]
    cup_height = core.foam_cap_height - core.head_pad_height
    cup_bottom = spec['cap_lid_pose']['translation_mm'][2] - cup_height
    mid_z = spec['cap_lid_pose']['translation_mm'][2] - 6.6
    if name == 'reed-cable-b':
        plan = (lower_xy, (lower_xy[0], 205.), (upper_xy[0], 205.), upper_xy)
    elif name == 'sensor-cable':
        plan = (lower_xy, (lower_xy[0], upper_xy[1]), upper_xy)
    else:
        plan = (lower_xy, upper_xy)
    return {'points_mm': ((*lower_xy, cup_bottom-1.),
                           *((*xy, mid_z) for xy in plan),
                           (*upper_xy, spec['cap_face_z_mm']+2.)),
            'bend_radius_mm': 5.5}


def water_in_guide_points():
    """World-frame R14 inlet path from the retained metal-elbow departure.

    The first point lies on the fixed top-port clocking line. A short S
    passes east of the sensor passage, and the aft traverse clears the PSU
    insert column before rising into the plain guide beneath the check elbow.
    """
    core = importlib.import_module('_cold_core_interface')
    frame = above_core.cap_lid_pose()
    cup_height = core.foam_cap_height-core.head_pad_height
    top_z = (core.wall_and_floor_thickness+core.carbonator_support_ring_height
             +core.carbonator_height+core.hole_shift_from_edge)
    def world(point):
        return above_core.point(frame, (-point[0], -point[1],
            point[2]-core.foam_shell_outer_height-cup_height))
    origin = world((0., -core.carbonator_port_offset, top_z))
    clocking = world((-47., core.west_lane_mid_y, top_z))
    fraction = (-55.-origin[0])/(clocking[0]-origin[0])
    departure = tuple(a+fraction*(b-a) for a,b in zip(origin,clocking))
    upper = tuple(above_core.specification()['cap_guides_world_mm']['water-in'])
    traverse_z = upper[2]-14.
    return [departure, (-56.,310.,traverse_z), (-56.,330.,traverse_z),
            (0.,330.,traverse_z), (upper[0],upper[1],traverse_z), upper]


def water_in_floor_xy():
    """Actual curved inlet crossing of the existing cup floor, in cap XY."""
    from above_core_routes import _rounded
    core = importlib.import_module('_cold_core_interface')
    z = (above_core.cap_lid_pose()['translation_mm'][2]
         -(core.foam_cap_height-core.head_pad_height)+core.cap_shell_clearance)
    for segment in _rounded(water_in_guide_points(),14.):
        a,b = segment['points_mm'][0],segment['points_mm'][-1]
        if not min(a[2],b[2]) <= z <= max(a[2],b[2]):
            continue
        if segment['kind']=='line':
            t=(z-a[2])/(b[2]-a[2])
            point=tuple(x+t*(y-x) for x,y in zip(a,b))
        else:
            center,axis=segment['center_mm'],segment['axis']
            radial=tuple(x-y for x,y in zip(a,center))
            cross=(axis[1]*radial[2]-axis[2]*radial[1],
                   axis[2]*radial[0]-axis[0]*radial[2],
                   axis[0]*radial[1]-axis[1]*radial[0])
            def at(angle):
                return tuple(c+r*math.cos(angle)+n*math.sin(angle)
                             for c,r,n in zip(center,radial,cross))
            low,high=0.,segment['angle_rad']
            for _ in range(48):
                mid=(low+high)/2.
                if at(mid)[2] < z:
                    low=mid
                else:
                    high=mid
            point=at((low+high)/2.)
        return above_core.world_to_cap(point)[:2]
    raise ValueError('Water inlet does not cross the cup floor')


@lru_cache(maxsize=1)
def water_in_features():
    """D7.5 inlet passage with floor-rooted 3 mm side and roof stock.

    The existing 2 mm cup floor is retained; the horizontal air passage has
    2.10 mm backing to its outer face. The curved entry cuts that floor only
    on the actual tube corridor. No stock projects below the cup. Individual
    native line/arc sleeves are clipped before union for stable band Booleans.
    """
    import cadquery as cq
    from _internal_routes import route_wire

    core = importlib.import_module('_cold_core_interface')
    points = water_in_guide_points()
    points[-1] = (*points[-1][:2], points[-1][2]+1.)
    wire = route_wire(points,14.)
    def pieces(radius):
        return [cq.Workplane(cq.Plane(origin=edge.startPoint(),normal=edge.tangentAt(0.)))
                .circle(radius).sweep(cq.Wire.assembleEdges([edge]),isFrenet=False).val()
                for edge in wire.Edges()]
    air_parts = pieces(core.cap_conduit_bore_radius)
    air = air_parts[0].fuse(*air_parts[1:]).clean()
    sleeve_parts = pieces(core.cap_conduit_bore_radius+3.)
    lid_bottom = above_core.cap_lid_pose()['translation_mm'][2]
    cup_bottom = lid_bottom-(core.foam_cap_height-core.head_pad_height)
    def stock(z0,z1):
        band=cq.Solid.makeBox(220.,330.,z1-z0,cq.Vector(-110.,170.,z0))
        clipped=[part.intersect(band) for part in sleeve_parts]
        clipped=[part for part in clipped if part.Solids()]
        return clipped[0].fuse(*clipped[1:]).clean()
    return {
        'cup_add': stock(cup_bottom+core.cap_shell_clearance,
                         lid_bottom-core.cap_lid_clearance),
        'lid_add': stock(lid_bottom,above_core.specification()['cap_face_z_mm']),
        'cut': air,
        'wall_mm': 3.,
        'horizontal_floor_backing_mm': points[1][2]-core.cap_conduit_bore_radius
                                       -cup_bottom-core.cap_shell_clearance,
    }


def soda_out_guide_points():
    """R14 roof traverse from the fixed soda riser to its upper plain guide.

    The horizontal reach stands above the complete cup floor. Both quarter
    turns retain vertical end tangents; the guide is an ownership boundary
    in one continuous tube.
    """
    import soda_inlet
    core = importlib.import_module('_cold_core_interface')
    frame = above_core.cap_lid_pose()
    lower = above_core.point(frame, (*core.cap_conduit_floor_xy['carb-water-out'], 0.))[:2]
    return soda_inlet.passage_points(lower)


@lru_cache(maxsize=1)
def soda_out_features():
    """Curved D7.5 soda passage with 3 mm side and roof stock.

    Individual native line/arc sleeves join the established cup floor;
    its horizontal backing is2.10mm. The sleeve is clipped at the existing
    floor and lid bands, with no added projection below the cup.
    """
    import cadquery as cq
    from _internal_routes import route_wire

    core = importlib.import_module('_cold_core_interface')
    points = soda_out_guide_points()
    points[0] = (*points[0][:2], points[0][2]-1.)
    points[-1] = (*points[-1][:2], points[-1][2]+1.)
    wire = route_wire(points,14.)
    def pieces(radius):
        return [cq.Workplane(cq.Plane(origin=edge.startPoint(),normal=edge.tangentAt(0.)))
                .circle(radius).sweep(cq.Wire.assembleEdges([edge]),isFrenet=False).val()
                for edge in wire.Edges()]
    air_parts = pieces(core.cap_conduit_bore_radius)
    air = air_parts[0].fuse(*air_parts[1:]).clean()
    sleeve_parts = pieces(core.cap_conduit_bore_radius+3.)
    lid_bottom = above_core.cap_lid_pose()['translation_mm'][2]
    cup_bottom = lid_bottom-(core.foam_cap_height-core.head_pad_height)
    def stock(z0,z1):
        band=cq.Solid.makeBox(220.,330.,z1-z0,cq.Vector(-110.,170.,z0))
        clipped=[part.intersect(band) for part in sleeve_parts]
        clipped=[part for part in clipped if part.Solids()]
        return clipped[0].fuse(*clipped[1:]).clean()
    return {'cup_add': stock(cup_bottom+core.cap_shell_clearance,
                             lid_bottom-core.cap_lid_clearance),
            'lid_add': stock(lid_bottom,above_core.specification()['cap_face_z_mm']),
            'cut': air,'wall_mm':3.,
            'horizontal_floor_backing_mm': points[1][2]-core.cap_conduit_bore_radius
                                           -cup_bottom-core.cap_shell_clearance}


@lru_cache(maxsize=1)
def reservoir_b_fill_link():
    """Two native fittings joining the unchanged reservoir bore to its upper guide.

    The link route ends on the two observed socket faces. The JG scan has no
    measured insertion depth; these points specify exposed tube, not cut length.
    """
    spec = above_core.specification()
    link = spec['reservoir_b_fill_link']
    core = importlib.import_module('_cold_core_interface')
    reservoir = importlib.import_module('reservoir')
    native_xy = core.reservoir_fill_conduit_xy(-1)
    xy = above_core.point(above_core.cap_lid_pose(), (*native_xy, 0.))[:2]
    lower = (*xy, link['lower_corner_z_mm'])
    upper_xy = spec['cap_guides_world_mm']['B-fill'][:2]
    upper = (*upper_xy, link['upper_corner_z_mm'])
    dx, dy = upper[0] - lower[0], upper[1] - lower[1]
    length = math.hypot(dx, dy)
    x, y = dx / length, dy / length
    lower_frame = {'rotation': ((0., x, -y), (0., y, x), (1., 0., 0.)),
                   'translation_mm': lower}
    upper_frame = {'rotation': ((-y, -x, 0.), (x, -y, 0.), (0., 0., 1.)),
                   'translation_mm': upper}
    lower_mouth = (lower[0] + 19.05*x, lower[1] + 19.05*y, lower[2])
    upper_mouth = (upper[0] - 20.56239*x, upper[1] - 20.56239*y, upper[2])
    exposed = length - 19.05 - 20.56239
    route = (lower_mouth,
             (lower_mouth[0] + exposed*x/3., lower_mouth[1] + exposed*y/3., lower[2]),
             (upper_mouth[0] - exposed*x/3., upper_mouth[1] - exposed*y/3., upper[2]),
             upper_mouth)
    cup_height = core.foam_cap_height - core.head_pad_height
    core_world_z = spec['cap_lid_pose']['translation_mm'][2] - cup_height - core.foam_shell_outer_height
    stem_tip = core_world_z + reservoir.cap_assembly_lift - reservoir.fill_boss_drop - 1.0
    return {
        'parts': {
            'reservoir-b-fill-lower': {
                'reference': 'neofit-stem-elbow', 'frame': lower_frame,
                'stem_length_mm': lower[2] - 6.0452 - stem_tip},
            'reservoir-b-fill-upper': {
                'reference': 'jg-turn-elbow', 'frame': upper_frame},
        },
        'exposed_route_world_mm': route,
        'upper_mouth_world_mm': above_core.point(upper_frame, (0., 0., 20.56239)),
        'exposed_span_mm': exposed,
        'roof_top_z_mm': link['roof_top_z_mm'],
        'clearance_mm': link['fitting_clearance_mm'],
    }


@lru_cache(maxsize=1)
def reservoir_b_fill_parts():
    """Purchased B-fill solids in world XYZ, owned by the native cold core."""
    import above_core_parts

    result = {}
    for name,row in reservoir_b_fill_link()['parts'].items():
        native = (above_core_parts.stem_elbow(row['stem_length_mm'])
                  if row['reference'] == 'neofit-stem-elbow'
                  else above_core_parts.native_reference(row['reference']))
        result[name] = native.moved(above_core.frame_location(row['frame']))
    return result


@lru_cache(maxsize=2)
def reservoir_b_fill_features(cup_height):
    """Simple carrier, rectangular roof and fitting air pockets in world XYZ.

    The original cup floor remains intact around the male stem. A single flat
    roof over the lower elbow retains at least 3 mm above its clearance pocket.
    """
    import cadquery as cq

    data = reservoir_b_fill_link()
    first = data['parts']['reservoir-b-fill-lower']['frame']
    second = data['parts']['reservoir-b-fill-upper']['frame']
    # A rectangular pocket clears the molded corner as well as the female
    # barrel. Its flat floor/ceiling retain the cup and roof sections. The
    # reservoir cap owns the unchanged lower stem entry.
    lower = cq.Solid.makeBox(15.8, 25.4, 15.8, cq.Vector(-7.9, -6.2, -7.9))
    lower = lower.moved(above_core.frame_location(first))
    radius, reach = 8.35, 20.75
    upper = cq.Solid.makeSphere(radius, angleDegrees1=-90., angleDegrees2=90.).fuse(
        cq.Solid.makeCylinder(radius, reach, cq.Vector(), cq.Vector(0., 1., 0.)),
        cq.Solid.makeCylinder(radius, reach, cq.Vector(), cq.Vector(0., 0., 1.)))
    upper = upper.moved(above_core.frame_location(second))
    # The exposed link is almost level; a rectangular corridor adds generous
    # access without a contoured pocket or a thin web between the fittings.
    a, b = data['exposed_route_world_mm'][0], data['exposed_route_world_mm'][-1]
    axis = cq.Vector(b[0]-a[0], b[1]-a[1], b[2]-a[2])
    tube = cq.Solid.makeCylinder(3.75, axis.Length, cq.Vector(*a), axis.normalized())
    air = lower.fuse(upper, tube)
    lower_box, air_box = lower.BoundingBox(), air.BoundingBox()
    margin = 3.0
    lid_bottom = above_core.cap_lid_pose()['translation_mm'][2]
    carrier = cq.Solid.makeBox(air_box.xlen + 2.*margin, air_box.ylen + 2.*margin,
        cup_height, cq.Vector(air_box.xmin-margin, air_box.ymin-margin, lid_bottom-cup_height))
    roof = cq.Solid.makeBox(lower_box.xlen + 2.*margin, lower_box.ylen + 2.*margin,
        data['roof_top_z_mm']-lid_bottom,
        cq.Vector(lower_box.xmin-margin, lower_box.ymin-margin, lid_bottom))
    return {'cup_add': carrier, 'lid_add': roof, 'cut': air}


def schedule():
    """Mounting stations and clamp stacks, without constructing native solids."""
    core = importlib.import_module('_cold_core_interface')
    modules = {}
    for name,row in deck_mounts().items():
        lid_stack = (core.foam_cap_lid_height+core.cap_lid_clearance
                     if row.standoff == 0. else 0.)
        maximum_reach = row.screw-row.seat_min-lid_stack
        modules[name] = {
            **row._asdict(),
            'quantity': len(row.points),
            'nominal_threaded_reach_mm': core.deck_mount_reach(name),
            'maximum_threaded_reach_mm': maximum_reach,
            'minimum_tip_clearance_mm': core.deck_mount_bore_depth-maximum_reach,
        }
    return {
        'frame': 'Top cap/lid native coordinates before installed half turn',
        'insert': 'ruthex RX-M3x5.7',
        'lid_face_z_mm': lid_face_z(),
        'column_diameter_mm': 2.*core.deck_mount_boss_radius,
        'pilot_diameter_mm': 2.*core.deck_mount_bore_radius,
        'pilot_depth_mm': core.deck_mount_bore_depth,
        'insert_length_mm': core.deck_mount_insert_length,
        'modules': modules,
        'valve_supports': {
            name: {'attachment': 'Integral upright socket wall on the top lid',
                   'native_to_cap': component_in_cap(name),
                   'socket_fit': 'Shared valve_seat V69'}
            for name in ('valve-v-a', 'valve-v-b', 'vk-solenoid')
        },
        'union_supports': union_support_datums(),
        'union_tie_allocation': {
            name: {key: row[key] for key in ('length_mm', 'stock', 'stock_length_mm')}
            for name, row in union_tie_routes().items()
        },
    }
