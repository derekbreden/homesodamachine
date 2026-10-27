"""One paired-tube snap on the fore Reservoir A station.

The fixed receiver is part of the top lid. The cap prints on one Y end, so
its spring sections lie in the bed plane. All public placements use the
appliance frame; cap() alone returns the centred standalone printable body.
"""
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'cadlib'))
import fits

CAP_NAME = 'reservoir-a-fore-snap-cap'
CENTRE = (54.25, 209.75, 259.5)
WALL = 3.0
CAP_LENGTH = 6.0
SPRING_THICK = 1.44


def specification():
    radius, pitch = 3.325, 7.5
    neck = pitch/2 + radius + WALL
    ledge = neck + .6
    inside = ledge + fits.running
    outside = inside + SPRING_THICK
    hook = ledge - .45
    return dict(
        closure='snap', cap_name=CAP_NAME, centre_world_mm=CENTRE,
        tube_centers_world_mm=[(CENTRE[0]+side*pitch/2, CENTRE[1], CENTRE[2])
                               for side in (-1., 1.)],
        wall_mm=WALL, seat_radius_mm=radius, tube_pitch_mm=pitch,
        cap_length_mm=CAP_LENGTH, axial_clearance_mm=fits.running,
        shoulder_mm=WALL, station_length_mm=CAP_LENGTH+2*fits.running+2*WALL,
        base_neck_half_x_mm=neck, base_ledge_half_x_mm=ledge,
        wing_inner_x_mm=inside, wing_outer_x_mm=outside,
        hook_inner_x_mm=hook, hook_top_z_mm=-2.5,
        hook_bottom_z_mm=-5.5, lead_rise_mm=inside-hook,
        spring_root_z_mm=4.2, spring_thickness_mm=SPRING_THICK,
        spring_length_mm=6.7, nominal_hook_overlap_mm=.45,
        side_clearance_mm=fits.running,
        hook_vertical_clearance_mm=fits.clearance(supported=True),
        base_top_z_mm=.9, base_ledge_z_mm=-2.5+fits.clearance(supported=True),
        base_floor_z_mm=-radius-WALL,
        cap_seat_bottom_z_mm=.9+fits.running,
        central_land_width_mm=WALL,
        central_land_z_mm=math.sqrt(radius**2-((pitch-WALL)/2)**2),
        outer_arch_rise_mm=4., insertion_lift_mm=.9+5.5+fits.running,
        print_up_axis=(0., 1., 0.))


def _prism(points, y0, y1):
    import cadquery as cq
    wire = cq.Wire.makePolygon([cq.Vector(x, y0, z) for x, z in points], close=True)
    return cq.Solid.extrudeLinear(wire, [], cq.Vector(0., y1-y0, 0.))


def _box(x0, x1, y0, y1, z0, z1):
    import cadquery as cq
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))


def _circle_arc(cx, y, radius, a, b):
    import cadquery as cq
    def point(angle):
        return cq.Vector(cx+radius*math.cos(angle), y, radius*math.sin(angle))
    return cq.Edge.makeThreePointArc(point(a), point((a+b)/2), point(b))


def _seat_room(y0, y1, ceiling):
    """Two round lower seats joined above a broad, three-millimetre land."""
    import cadquery as cq
    s = specification()
    c, r = s['tube_pitch_mm']/2, s['seat_radius_mm']
    a, z = WALL/2, s['central_land_z_mm']
    def v(x, zz): return cq.Vector(x, y0, zz)
    edges = [cq.Edge.makeLine(v(-c-r, ceiling), v(c+r, ceiling)),
             cq.Edge.makeLine(v(c+r, ceiling), v(c+r, 0.)),
             _circle_arc(c, y0, r, 0., -math.acos((a-c)/r)),
             cq.Edge.makeLine(v(a, -z), v(-a, -z)),
             _circle_arc(-c, y0, r, -math.acos((c-a)/r), -math.pi),
             cq.Edge.makeLine(v(-c-r, 0.), v(-c-r, ceiling))]
    return cq.Solid.extrudeLinear(cq.Wire.assembleEdges(edges), [], cq.Vector(0., y1-y0, 0.))


def base():
    """World-frame fixed receiver with full three-millimetre end shoulders."""
    s = specification()
    half = s['station_length_mm']/2
    inner = CAP_LENGTH/2+s['axial_clearance_mm']
    neck, ledge = s['base_neck_half_x_mm'], s['base_ledge_half_x_mm']
    floor, bearing, top = s['base_floor_z_mm'], s['base_ledge_z_mm'], s['base_top_z_mm']
    body = _prism([(-neck, floor), (neck, floor), (neck, bearing),
                   (ledge, bearing), (ledge, top), (-ledge, top),
                   (-ledge, bearing), (-neck, bearing)], -half, half)
    for ya, yb in ((-half, -inner), (inner, half)):
        body = body.fuse(_box(-s['wing_outer_x_mm'], s['wing_outer_x_mm'],
                              ya, yb, floor, top))
    body = body.cut(_seat_room(-half-.1, half+.1, top+1.)).clean()
    return body.translate(CENTRE)


def cap():
    """One centred cap: broad fixed seats, open spring lanes and integral hooks."""
    import cadquery as cq
    s = specification()
    c, r = s['tube_pitch_mm']/2, s['seat_radius_mm']
    wi, wo = s['wing_inner_x_mm'], s['wing_outer_x_mm']
    rigid, hook = s['base_neck_half_x_mm'], s['hook_inner_x_mm']
    root, bottom, lip = s['spring_root_z_mm'], s['hook_bottom_z_mm'], s['hook_top_z_mm']
    seat, land = s['cap_seat_bottom_z_mm'], s['central_land_z_mm']
    y = -CAP_LENGTH/2
    def v(p): return cq.Vector(p[0], y, p[1])
    def line(a, b): return cq.Edge.makeLine(v(a), v(b))
    rx, rz = wo-c, s['outer_arch_rise_mm']
    edges = [line((-wo, bottom), (-wo, root)),
             cq.Edge.makeEllipse(rx, rz, (-c, y, root), (0., -1., 0.),
                                 (1., 0., 0.), 90., 180.),
             line((-c, root+rz), (c, root+rz)),
             cq.Edge.makeEllipse(rx, rz, (c, y, root), (0., -1., 0.),
                                 (1., 0., 0.), 0., 90.),
             line((wo, root), (wo, bottom))]
    path = [(wo, bottom), (wi, bottom), (hook, bottom+s['lead_rise_mm']),
            (hook, lip), (wi, lip), (wi, root), (rigid, root), (rigid, seat)]
    edges += [line(a, b) for a, b in zip(path, path[1:])]
    angle = math.asin(seat/r)
    outer = c+math.sqrt(r*r-seat*seat)
    edges += [line((rigid, seat), (outer, seat)),
              _circle_arc(c, y, r, angle, math.acos((WALL/2-c)/r)),
              line((WALL/2, land), (-WALL/2, land)),
              _circle_arc(-c, y, r, math.acos((c-WALL/2)/r), math.pi-angle),
              line((-outer, seat), (-rigid, seat))]
    path = [(-rigid, seat), (-rigid, root), (-wi, root), (-wi, lip),
            (-hook, lip), (-hook, bottom+s['lead_rise_mm']), (-wi, bottom), (-wo, bottom)]
    edges += [line(a, b) for a, b in zip(path, path[1:])]
    return cq.Solid.extrudeLinear(cq.Wire.assembleEdges(edges), [],
                                  cq.Vector(0., CAP_LENGTH, 0.)).clean()


def installed_cap():
    return cap().translate(CENTRE)
