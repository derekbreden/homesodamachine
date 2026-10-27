"""Plain roof piers for the meter's two fixed collars.

Each pier has an open west-facing bearing and a straight strap passage.
Three millimetres of stock back the seats and passages. One broad fore
column carries both the meter and ASSE; their strap openings remain open.
"""

import importlib
import functools
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[2]
sys.path[:0] = [str(HW / 'manifold-layout'), str(HW / 'scripts'),
                str(HW / 'reference/digiten-flow-sensor'),
                str(HW / 'printed-parts/cadlib')]
import above_core as layout


def meter_support_datums():
    import fits
    meter = importlib.import_module('digiten_flow_sensor')
    first, last, r0, r1 = meter.mounting_profile(1)[-1]
    radius, wall = max(r0, r1) + fits.slip, 3.
    result = []
    for side in (-1, 1):
        station = -(first + last) / 2. if side == -1 else 21.5
        x, y, z = layout.point(layout.pose('digiten-flow'), (station, 0., 0.))
        low = (44.5,361.,z-radius-wall) if side == -1 else (x+2.5,y-4.5,z-radius-wall)
        high = (63.,y+4.5,355.)
        result.append({
            'parent': 'enclosure-back-top',
            'centre_world_mm': (x, y, z),
            'width_mm': high[1]-low[1], 'seat_radius_mm': radius, 'wall_mm': wall,
            'native_bearing_band_mm': ((station-3., station+3.) if side == -1
                                       else (station-1.5, station+4.5)),
            'stock_min_world_mm': low, 'stock_max_world_mm': high,
            'seat_bottom_world_z_mm': low[2],
            'roof_root_world_z_mm': 346.,
            'tie_plane_world_y_mm': y,
            'tie_slot_min_world_mm': (low[0]-.1, y-1.5, z+radius+wall),
            'tie_slot_max_world_mm': (high[0]+.1, y+1.5, z+radius+2.*wall),
            'tie_backing_x_mm':52.5,
            'asse_bore': ({'centre_xz_mm': (37.25, layout.pose(
                'asse1022-assembly')['translation_mm'][2]), 'radius_mm':16.75}
                if side == -1 else None),
            'body_setback': ({'fore_face_y_mm':y-1.5, 'top_z_mm':315.}
                             if side == 1 else None),
        })
    return tuple(result)


@functools.cache
def meter_supports():
    """Two roof-rooted rectangular piers, with west-open circular seats."""
    import cadquery as cq
    result = []
    for data in meter_support_datums():
        low, high = data['stock_min_world_mm'], data['stock_max_world_mm']
        x, y, z = data['centre_world_mm']
        stock = cq.Solid.makeBox(*(high[i]-low[i] for i in range(3)), cq.Vector(*low))
        bore = cq.Solid.makeCylinder(data['seat_radius_mm'],data['width_mm']+.2,
            cq.Vector(x,low[1]-.1,z),cq.Vector(0,1,0))
        a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
        slot = cq.Solid.makeBox(*(b[i]-a[i] for i in range(3)),cq.Vector(*a))
        stock = stock.cut(bore, slot)
        if data['body_setback']:
            fit = data['body_setback']
            stock = stock.cut(cq.Solid.makeBox(high[0]-low[0]+.2,
                fit['fore_face_y_mm']-low[1]+.1,fit['top_z_mm']-low[2]+.1,
                cq.Vector(low[0]-.1,low[1]-.1,low[2]-.1)))
        if data['asse_bore']:
            import _above_core_shell as shell
            fit = data['asse_bore']
            cx, cz = fit['centre_xz_mm']
            stock = stock.cut(cq.Solid.makeCylinder(fit['radius_mm'],data['width_mm']+.2,
                cq.Vector(cx,low[1]-.1,cz),cq.Vector(0,1,0)))
            stock = stock.cut(shell.tie_window('y',low[1]-.1,high[1]+.1,
                cx+fit['radius_mm']+3.,cx+fit['radius_mm']+5.5,cz))
            # A straight west mouth admits the whole rigid collar. The open
            # approach above it joins the ASSE bore, leaving no tapered web.
            stock = stock.cut(shell.box(low[0]-.1,x,low[1]-.1,high[1]+.1,
                z-data['seat_radius_mm'],z+data['seat_radius_mm']),
                shell.box(low[0]-.1,data['tie_backing_x_mm'],y-1.5,y+1.5,
                    a[2],cz))
        result.append(stock.clean())
    return tuple(result)


def meter_tie_routes():
    """Nominal 2.5 by 0.8 mm straps through the piers' straight passages.

    The straps surround each collar and its seat. The head is accessible on
    the west face. Purchased head dimensions, threading and holding force
    require the physical assembly.
    """
    result = {}
    for number, data in enumerate(meter_support_datums()):
        x, y, z = data['centre_world_mm']
        low, high = data['stock_min_world_mm'], data['stock_max_world_mm']
        radius = data['seat_radius_mm']+.6
        a, b = data['tie_slot_min_world_mm'], data['tie_slot_max_world_mm']
        upper_z = (a[2]+b[2])/2.
        lower_z = low[2]-.6
        upper_west, lower_west = (low[0]-.6,y,upper_z),(low[0]-.6,y,lower_z)
        upper_east, lower_east = (high[0]+.6,y,upper_z),(high[0]+.6,y,lower_z)
        def tangent(point, sign):
            dx,dz=point[0]-x,point[2]-z
            return math.degrees(math.atan2(dz,dx)+sign*math.acos(radius/math.hypot(dx,dz)))%360.
        lower_angle,upper_angle=tangent(lower_west,-1),tangent(upper_west,1)
        def point(angle):
            theta=math.radians(angle)
            return (x+radius*math.cos(theta),y,z+radius*math.sin(theta))
        def line(a,b):
            return {'kind':'line','points_mm':[a,b],'wide_axis':(0.,1.,0.)}
        lower,upper=point(lower_angle),point(upper_angle)
        segments=[line(upper_west,upper_east),line(upper_east,lower_east),
            line(lower_east,lower_west),line(lower_west,lower),
            {'kind':'arc','points_mm':[lower,point((lower_angle+upper_angle)/2.),upper],
             'radius_mm':radius,'sweep_degrees':upper_angle-lower_angle,'wide_axis':(0.,1.,0.)},
            line(upper,upper_west)]
        length=sum(math.dist(*row['points_mm']) if row['kind']=='line'
            else radius*abs(math.radians(row['sweep_degrees'])) for row in segments)
        result['meter-'+('fore' if number==0 else 'aft')]={
            'parent':'enclosure-back-top','segments':segments,'length_mm':length,
            'stock':'6-inch narrow nylon tie','stock_length_mm':152.4,
            'width_mm':2.5,'thickness_mm':.8,'collar_plane_world_y_mm':y,
            'strip_basis':'Nominal layout section; purchased strap/head dimensions unmeasured',
        }
    return result
