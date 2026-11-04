"""Selected continuous soda inlet, accepted bend holder and compressed foam.

``plan`` and ``tube_spec`` use only the standard library. Native builders import
CadQuery when called. All placed shapes use appliance-world millimetres; the
holder's printable shape retains the accepted flat-back native frame.
"""

from functools import cache
import math

import above_core as layout

HOLDER_ACCEPTANCE = ('future/tube-bend-holder-exploration/prints/'
                     '2026-10-23-legs-123-w2-petgf-left04-z018-mark1/physical-result.json')
FOAM_EVIDENCE = ('hardware/reference/cargen-pipe-insulation/'
                 'elbow-fit-2026-10-24/physical-observation.json')
SOFT_NEIGHBORS = ('vk-solenoid', 'g-ganen-pump', 'suction-tube',
                  'suction-barb-clamp')
RETIRED = ('soda-inlet-stem', 'soda-rise-insulation')


from _layout_data import data as _data

def _add(a, b):
    return _data('add', a=a, b=b)


def _mul(a, scale):
    return _data('mul', a=a, scale=scale)


def _line(a, b):
    return _data('line', a=a, b=b)


def _vertical_transition(a, b):
    return _data('vertical-transition', a=a, b=b)


def _tail(control, t):
    return _data('soda-tail', control=control, t=t)


def _bezier_point(control, t):
    return _tail(control, t)[0]


def _bezier_length(control):
    return _data('soda-bezier-length', control=control)


def plan():
    return _data('soda-plan', spec=layout.specification())


def tube_spec():
    return _data('soda-tube', spec=layout.specification())


def passage_points(lower_world_xy):
    return [tuple(row) for row in _data('soda-passage', spec=layout.specification(), lower_world_xy=lower_world_xy)]


def _holder_section():
    return tuple(_data('soda-holder-section', spec=layout.specification()))


def holder_geometry_numbers():
    return _data('soda-holder', spec=layout.specification())


def _teardrop(wp, x, z, radius):
    k = radius/math.sqrt(2.)
    return (wp.moveTo(x+k, z+k).lineTo(x, z+math.sqrt(2.)*radius)
            .lineTo(x-k, z+k).threePointArc((x, z-radius), (x+k, z+k)).close())


@cache
def holder_native():
    """Accepted PET-GF holder(2,3), in its flat-back printable frame."""
    import cadquery as cq
    n = holder_geometry_numbers()
    r, outer, zc = n['channel_radius'], n['outer_radius'], n['channel_z']
    bend, leg = n['bend_radius'], n['leg']
    def section():
        x0, x1, zd = bend-outer, bend+outer, n['stock_arc_z']
        return (cq.Workplane('XZ').moveTo(x0, 0.).lineTo(x1, 0.).lineTo(x1, zd)
                .threePointArc((bend, zd+outer), (x0, zd)).close())
    axis = ((0., 0., 0.), (0., 1., 0.))
    body = section().revolve(n['turn_degrees'], *axis)
    channel = _teardrop(cq.Workplane('XZ'), bend, zc, r).revolve(n['turn_degrees'], *axis)
    plane, origin = cq.Vector(*n['mirror_normal']), cq.Vector(0., 0., 0.)
    def mouth_at(y, radius):
        plane = cq.Plane(origin=(0., y, 0.), xDir=(1., 0., 0.), normal=(0., -1., 0.))
        return _teardrop(cq.Workplane(plane), bend, zc, radius).wires().val()
    mouth = cq.Solid.makeLoft([mouth_at(y, radius)
                              for y, radius in zip(n['mouth_y'], n['mouth_radii'])], ruled=True)
    if leg > 0.:
        body_leg = section().extrude(leg)
        channel_leg = _teardrop(cq.Workplane('XZ'), bend, zc, r).extrude(leg)
        body = body.union(body_leg).union(body_leg.mirror(plane, origin))
        channel = channel.union(channel_leg).union(channel_leg.mirror(plane, origin))
        mouth = mouth.translate(cq.Vector(0., -leg, 0.))
    end = mouth.mirror(plane, origin)
    return body.cut(channel).cut(cq.Workplane().add(mouth)).cut(cq.Workplane().add(end)).clean().val()


@cache
def holder():
    """Placed holder, carried with the continuous core-to-meter tube."""
    p = plan()
    return holder_native().moved(layout.frame_location({
        'rotation': p['holder_rotation'], 'translation_mm': p['holder_translation_mm']}))


def sweep(segments, outer_radius, inner_radius=None):
    """Native exact line/arc sweep for the tube or square-ended foam."""
    import cadquery as cq
    edges = []
    for segment in segments:
        if segment['kind'] == 'bezier':
            edges.append(cq.Edge.makeBezier([cq.Vector(*p) for p in segment['control_points_mm']]))
        else:
            points = [cq.Vector(*p) for p in segment['points_mm']]
            edges.append(cq.Edge.makeThreePointArc(*points) if segment['kind']=='arc'
                         else cq.Edge.makeLine(*points))
    path = cq.Wire.assembleEdges(edges)
    section = cq.Workplane(cq.Plane(origin=edges[0].startPoint(), xDir=(1., 0., 0.),
                                   normal=edges[0].tangentAt(0.))).circle(outer_radius)
    if inner_radius is not None:
        section = section.circle(inner_radius)
    # The corrected frame stays continuous through the S transition's
    # inflection; a Frenet frame flips there and pinches the circular sweep.
    return section.sweep(cq.Workplane().newObject([path]), isFrenet=False).val()


@cache
def tube():
    p = plan()
    return sweep(p['tube_segments'], p['tube_od_mm']/2., p['tube_id_mm']/2.)


@cache
def foam_stock():
    """Nominal one-piece stock envelope before local compression."""
    p = plan()
    return sweep(p['foam_segments'], p['nominal_foam_od_mm']/2., p['nominal_foam_id_mm']/2.)


def foam_occupied(neighbors):
    """Estimated occupied foam after local compression around named bodies.

    This display subtraction is neither a cutting pattern nor a mechanical
    strain or thermal prediction. The full stock envelope remains separately
    available for its accepted soft-contact receipt.
    """
    import cadquery as cq
    from above_core_routes import _rounded

    # The two downward coil tabs need their lead exits through the compressed
    # side of the sleeve. These are occupied-space estimates, like the valve
    # and pump contacts, rather than cuts in the square-ended stock piece.
    valve = layout.pose('vk-solenoid')
    lead_exits = []
    for x in (-7.45, 7.45):
        tip = layout.point(valve, (x, 27.1, 52.2))
        points = [_add(tip, [0., 0., 2.]), _add(tip, [0., 0., -6.]),
                  _add(tip, [0., -12., -6.])]
        segments = _rounded(points, 3.)
        edges = []
        for segment in segments:
            p = [cq.Vector(*v) for v in segment['points_mm']]
            edges.append(cq.Edge.makeThreePointArc(*p) if segment['kind']=='arc'
                         else cq.Edge.makeLine(*p))
        path = cq.Wire.assembleEdges(edges)
        lead_exits.append(cq.Workplane(cq.Plane(origin=points[0], normal=(0.,0.,-1.)))
                          .circle(2.).sweep(path, isFrenet=False).val())
    # One solid at a time: the neighbours are compounds of overlapping solids, and one
    # cut against all of them leaves the holder uncut and the sleeve in fragments.
    foam = foam_stock()
    for tool in (holder(), tube(), *lead_exits, *(neighbors[name] for name in SOFT_NEIGHBORS)):
        for solid in tool.Solids():
            foam = foam.cut(solid)
    # It also leaves specks along the tangent contacts; none is a cubic millimetre.
    kept = [s for s in foam.clean().Solids() if s.Volume() > 1.]
    return kept[0] if len(kept) == 1 else cq.Compound.makeCompound(kept)
