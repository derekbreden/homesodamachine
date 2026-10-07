"""Exact stock R14 discharge-check feed through the east service channel."""
import math
import cadquery as cq


def build(exact_arc, exact_s, routing, fore_cross=(193.9,293.5)):
    r = 14.
    x, y, z = 100.325, 304.6, 346.
    source = cq.Vector(68.4, 453.5, 342.)
    target = cq.Vector(x-r, source.y, z)
    offset = cq.Vector(0, 0, z-source.z)
    angle = math.acos(1-offset.Length/(2*r))
    axial = 2*r*math.sin(angle)
    first_lead = .5
    first_tail = target.x-source.x-axial-first_lead
    a = source+cq.Vector(first_lead, 0, 0)
    edges, b, mids, _ = exact_s(a, cq.Vector(1, 0, 0), offset, r)
    edges = [cq.Edge.makeLine(source, a)]+edges+[cq.Edge.makeLine(b, target)]
    points = [source, a, *mids, b, target]
    edge, c, mid, _ = exact_arc(target, cq.Vector(1, 0, 0), cq.Vector(0, -1, 0), r)
    edges.append(edge)
    points += [mid, c]
    a = cq.Vector(x, y+r, z)
    edges.append(cq.Edge.makeLine(c, a))
    edge, b, mid, _ = exact_arc(a, cq.Vector(0, -1, 0), cq.Vector(0, 0, -1), r)
    edges.append(edge)
    points += [a, mid, b]
    a = cq.Vector(x, y, 265.5+r)
    edges.append(cq.Edge.makeLine(b, a))
    edge, b, mid, _ = exact_arc(a, cq.Vector(0, 0, -1), cq.Vector(0, -1, 0), r)
    edges.append(edge)
    points += [a, mid, b]
    low_target = cq.Vector(x, 280, 265.5)
    low_lead = b.y-low_target.y
    edges.append(cq.Edge.makeLine(b, low_target))
    points += [low_target]
    if fore_cross!=(193.9,293.5):
        # The east-side semicircle rises exactly28mm, then the fore lane's
        # opposed circles lower the final crossing without reducing R14.
        cross_y,cross_z=fore_cross
        a=cq.Vector(x,268.,265.5)
        edges.append(cq.Edge.makeLine(low_target,a))
        edge,b,mid,_=exact_arc(a,cq.Vector(0,-1,0),cq.Vector(0,0,1),r)
        edges.append(edge);points += [a,mid,b]
        edge,b,mid,_=exact_arc(b,cq.Vector(0,0,1),cq.Vector(0,-1,0),r)
        edges.append(edge);points += [mid,b]
        if abs(cross_z-b.z)>1e-7:
            es,b,mids,_=exact_s(b,cq.Vector(0,-1,0),cq.Vector(0,0,cross_z-b.z),r)
            edges += es;points += mids+[b]
        a=cq.Vector(x,cross_y+r,cross_z)
        if a.y>b.y:raise ValueError('Fore crossing lacks R14/S space')
        edges.append(cq.Edge.makeLine(b,a))
        edge,b,mid,_=exact_arc(a,cq.Vector(0,-1,0),cq.Vector(-1,0,0),r)
        edges.append(edge);points += [a,mid,b]
        a=cq.Vector(-26+r,cross_y,cross_z)
        edges.append(cq.Edge.makeLine(b,a))
        edge,b,mid,_=exact_arc(a,cq.Vector(-1,0,0),cq.Vector(0,-1,0),r)
        edges.append(edge);points += [a,mid,b]
        loop=(-26.,174.9,cross_z)
        a=cq.Vector(*loop)
        if a.y>b.y:raise ValueError('Fore core loop lacks its straight lead')
        edges.append(cq.Edge.makeLine(b,a));points += [a]
        run=None
    else:
        routing.frame('water5-low-fore', cq.Solid.makeBox(1, 1, 1),
                  {'begin': (low_target.toTuple(), (0, 1, 0), 6.35)})
        loop = (-26., 174.9, 293.5)
        routing.frame('water5-core-loop', cq.Solid.makeBox(1, 1, 1),
                  {'begin': (loop, (0, 1, 0), 6.35)})
        run = routing.bent('water5-low-fore', 'water5-low-fore.begin',
                       (x, 254, 265.5), (x, 254, 293.5),
                       (x, 193.9, 293.5), (-26, 193.9, 293.5),
                       'water5-core-loop.begin', kind='water', bend=r,
                       lead=(0, 14), skew=(3, 0))
        edges += routing.centreline(run).Edges()
        points += [cq.Vector(*p) for p in run.pts]
    a = cq.Vector(*loop)
    b = cq.Vector(-56, 174.9, 267.4)
    delta = b-a
    u, forward = delta.normalized(), cq.Vector(0, -1, 0)
    p1 = a+forward*r+u*r
    p2 = p1+u*(delta.Length-2*r)
    m1 = a+forward*(r/math.sqrt(2))+u*(r*(1-1/math.sqrt(2)))
    m2 = p2+u*(r/math.sqrt(2))-forward*(r*(1-1/math.sqrt(2)))
    end = cq.Vector(-56, 188.9, 253.4)
    m3 = b+cq.Vector(0, r/math.sqrt(2), -r*(1-1/math.sqrt(2)))
    edges += [cq.Edge.makeThreePointArc(a, m1, p1), cq.Edge.makeLine(p1, p2),
              cq.Edge.makeThreePointArc(p2, m2, b), cq.Edge.makeThreePointArc(b, m3, end)]
    points += [m1, p1, p2, m2, b, m3, end]
    wire = cq.Wire.assembleEdges(edges)
    shape = cq.Solid.sweep(cq.Wire.makeCircle(3.175, source, cq.Vector(1, 0, 0)),
                           [], wire, makeSolid=True, isFrenet=True)
    data = {'points_mm': [p.toTuple() for p in points],
            'diameter_mm': 6.35, 'radii_mm': [r]*8+(list(run.radii.values())if run else[r]*6),
            'tightest_mm': min(r, run.tightest)if run else r, 'developed_length_mm': wire.Length(),
            'initial_s_leads_mm': [first_lead, first_tail],
            'low_fore_lead_mm': low_lead,
            'high_lane_x_mm': x, 'fore_drop_y_mm': y, 'high_fore_z_mm': z,
            'fore_cross_yz_mm':fore_cross,
            'east_wall': {'tube_max_x_mm': x+3.175,
                          'clearance_cutter_max_x_mm': x+4.175,
                          'minimum_outer_x_for_3mm_stock_mm': x+7.175,
                          'radial_air_mm': 1, 'minimum_stock_mm': 3}}
    if first_tail < 0 or low_lead < 0:
        raise ValueError('Exact water5 S arcs have insufficient straight span')
    return shape, wire, data
