"""Simple integral routing clips in the host part's coordinate frame.

Tube seats use the selected C2 spring section. Cable hooks use one broad arm,
a flat retaining underside and a 45 degree entry. Callers choose the actual
host plane and cable section; these constructors add no separate mounting part.
"""
import math

import cadquery as cq


TUBE_DIAMETER_ALLOWANCE = 0.  # Selected C2 bore equals the nominal quarter-inch OD.
TUBE_WING = 2.40
TUBE_TIP_DEGREES = 125.42102606277044
TUBE_SPAN = 8.
CABLE_STOCK = 3.
CABLE_SPAN = 16.
ROOT_OVERLAP = .10


def _unit(value):
    return cq.Vector(*value).normalized()


def _prism(points, plane, length):
    return cq.Workplane(plane).polyline(points).close().extrude(length).val()


def tube_clip(centre, along, outward, root_distance, *, tube_od=6.35,
              bore_diameter=None, span=TUBE_SPAN, wing=TUBE_WING,
              tip_degrees=TUBE_TIP_DEGREES, print_up=None):
    """Filled-root C2 clip. ``outward`` points from the host toward the mouth.

    ``centre`` is the tube axis and ``root_distance`` its distance from the
    host face. The full root fills both corners beside the round seat and
    overlaps the host. ``along`` is perpendicular to ``outward``.
    """
    u,n=_unit(along),_unit(outward)
    if abs(u.dot(n))>1.e-7:
        raise ValueError('A tube clip needs perpendicular tube and host directions')
    t=u.cross(n).normalized()
    ri=(tube_od+TUBE_DIAMETER_ALLOWANCE if bore_diameter is None else bore_diameter)/2.
    ro,rm,nose=ri+wing,ri+wing/2.,wing/2.
    tip=math.radians(tip_degrees)
    origin=cq.Vector(*centre)-u*(span/2.)
    plane=cq.Plane(origin=origin,xDir=t,normal=u)
    def point(r,a):return r*math.sin(a),r*math.cos(a)
    def add(a,b):return a[0]+b[0],a[1]+b[1]
    a,b,c,d=point(ro,-tip),point(ro,tip),point(ri,tip),point(ri,-tip)
    cp,cn=point(rm,tip),point(rm,-tip)
    qp,qn=(math.cos(tip),-math.sin(tip)),(math.cos(-tip),-math.sin(-tip))
    body=(cq.Workplane(plane).moveTo(*a).threePointArc((0,ro),b)
          .threePointArc(add(cp,(nose*qp[0],nose*qp[1])),c)
          .threePointArc((0,ri),d)
          .threePointArc(add(cn,(-nose*qn[0],-nose*qn[1])),a)
          .close().extrude(span).val())
    root=_prism([(-ro,0),(ro,0),(ro,root_distance+ROOT_OVERLAP),
                 (-ro,root_distance+ROOT_OVERLAP)],plane,span)
    if print_up is not None:
        growth=_unit(print_up)
        vertical=t.dot(growth)
        if abs(abs(vertical)-1.)<1.e-7:
            # A horizontal run on a standing wall has one hanging root edge.
            # Its full-width 45 degree corbel grows from the existing wall;
            # the circular seat and both spring wings retain their profile.
            sign=1. if vertical>0 else -1.
            edge=-sign*ro
            reach=root_distance+ROOT_OVERLAP
            corbel=_prism([(edge,0),(edge,reach),(edge-sign*reach,reach)],plane,span)
            root=root.fuse(corbel)
    bore=cq.Solid.makeCylinder(ri,span+.2,origin-u*.1,u)
    return body.fuse(root).cut(bore).clean()


def cable_hook(host_origin, outward, profile_up, *, seat_depth=2.20,
               seat_height=7.75, span=CABLE_SPAN, stock=CABLE_STOCK,
               beak=.75):
    """One-arm cable hook rooted at ``host_origin`` on a wall face.

    ``profile_up`` points toward the entry and should follow the host's print
    growth direction. The cable runs perpendicular to it along the wall.
    The origin is the root's 45 degree toe, at the centre of its cable span.
    """
    n,p=_unit(outward),_unit(profile_up)
    if abs(n.dot(p))>1.e-7:
        raise ValueError('A cable hook needs perpendicular wall and entry directions')
    u=n.cross(p).normalized()
    projection=seat_depth+stock
    floor=projection+stock
    roof=floor+seat_height
    top=roof+beak+stock
    mouth=seat_depth-beak
    if mouth<=0:
        raise ValueError('The cable entry must remain open')
    # Extending the same root slope behind the wall preserves the complete
    # air-side section while making the integral attachment a native overlap.
    points=[(-ROOT_OVERLAP,-ROOT_OVERLAP),(projection,projection),(projection,top),
            (seat_depth,top),(mouth,top-beak),(mouth,roof),
            (seat_depth,roof),(seat_depth,floor),(-ROOT_OVERLAP,floor)]
    origin=cq.Vector(*host_origin)-u*(span/2.)
    # Plane y is profile_up, since u x outward = profile_up.
    plane=cq.Plane(origin=origin,xDir=n,normal=u)
    return _prism(points,plane,span).clean()


def cable_origin(centre, outward, profile_up, *, seat_depth=2.20,
                 seat_height=7.75, stock=CABLE_STOCK):
    """Root toe from the retained cable's centre, using the hook's own seat."""
    n,p=_unit(outward),_unit(profile_up)
    seat_middle=seat_depth+2*stock+seat_height/2.
    return (cq.Vector(*centre)-n*(seat_depth/2.)-p*seat_middle).toTuple()


def cable_bank(origin, *, seat_heights=(13.30, 7.75), seat_depth=2.20,
               span=CABLE_SPAN, stock=CABLE_STOCK, beak=.75):
    """Two upward-entry cable seats on one filled floor-rooted base.

    ``origin`` is the left edge of the base on its host face, at mid-span.
    The profile lies in X/Z and the cables run along Y. Each cavity retains
    cable_hook's entry chamfer and flat retaining underside. The first
    cavity has the taller wall; the middle wall belongs to both seats.
    """
    first, second = seat_heights
    a, b = stock, stock + seat_depth
    c, d = 2 * stock + seat_depth, 2 * (stock + seat_depth)
    width = 3 * stock + 2 * seat_depth
    roof_a, roof_b = stock + first, stock + second
    top_a, top_b = roof_a + stock + beak, roof_b + stock + beak
    points = [(0., -ROOT_OVERLAP), (width, -ROOT_OVERLAP),
              (width, top_b), (d, top_b), (d-beak, top_b-beak),
              (d-beak, roof_b), (d, roof_b), (d, stock), (c, stock),
              (c, top_a), (b, top_a), (b-beak, top_a-beak),
              (b-beak, roof_a), (b, roof_a), (b, stock), (a, stock),
              (a, top_a), (0., top_a)]
    plane = cq.Plane(origin=cq.Vector(*origin)+cq.Vector(0., span/2., 0.),
                     xDir=(1., 0., 0.), normal=(0., -1., 0.))
    return _prism(points, plane, span).clean()
