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
SOFT_NEIGHBORS = ('vk-solenoid', 'g-ganen-pump', 'pump-inlet-tpu',
                  'pump-inlet-barb-band')
RETIRED = ('soda-inlet-stem', 'soda-rise-insulation')


def _add(a, b):
    return [x+y for x, y in zip(a, b)]


def _mul(a, scale):
    return [scale*x for x in a]


def _line(a, b):
    return {'kind': 'line', 'points_mm': [list(a), list(b)]}


def plan():
    """One accepted inlet plan, including exact circular-arc datums."""
    selected = layout.specification()['soda_inlet']
    meter = layout.pose('digiten-flow')
    mouth = list(layout.point(meter, (-30.5, 0., 0.)))
    forward = list(layout.vector(meter['rotation'], (1., 0., 0.)))
    up = [0., 0., 1.]
    radius = selected['holder']['centreline_bend_r_mm']
    leg = selected['holder']['leg_mm']
    gap = selected['holder_to_meter_mm']
    end = _add(mouth, _mul(forward, -leg-gap))
    centre = _add(end, _mul(up, -radius))
    start = _add(centre, _mul(forward, -radius))
    middle = _add(centre, _add(_mul(forward, -radius/math.sqrt(2.)),
                              _mul(up, radius/math.sqrt(2.))))
    guide = list(layout.specification()['cap_guides_world_mm']['carb-water-out'])
    xaxis = _mul(forward, -1.)
    zaxis = [xaxis[1], -xaxis[0], 0.]
    rotation = [[xaxis[i], up[i], zaxis[i]] for i in range(3)]
    zc = selected['holder']['wall_mm']+selected['holder']['channel_d_mm']/2.
    translation = _add(centre, _mul(zaxis, -zc))
    insertion = selected['meter_insertion_estimate_mm']
    inserted = _add(mouth, _mul(forward, insertion))
    foam_start = _add(guide, _mul(up, selected['foam']['start_above_guide_mm']))
    foam_end = _add(mouth, _mul(forward, -selected['foam']['end_before_meter_mm']))
    arc = {'kind': 'arc', 'points_mm': [start, middle, end],
           'radius_mm': radius, 'center_mm': centre,
           'axis': [-forward[1], forward[0], 0.],
           'angle_rad': math.pi/2.}
    tube_segments = [_line(guide, start), arc, _line(end, inserted)]
    foam_segments = [_line(foam_start, start), arc, _line(end, foam_end)]
    foam_length = math.dist(foam_start, start)+radius*math.pi/2.+math.dist(end, foam_end)
    return {
        'selection': selected['selection'], 'holder': dict(selected['holder']),
        'physical_acceptance': HOLDER_ACCEPTANCE, 'foam_fit_evidence': FOAM_EVIDENCE,
        'core_guide_mm': guide, 'guide_outward': up,
        'meter_mouth_mm': mouth, 'meter_insertion_mm': insertion,
        'meter_insertion_basis': 'Nominal DIGITEN layout estimate; actual receiving depth is unmeasured.',
        'flow_axis': forward, 'arc_start_mm': start, 'bend_center_mm': centre,
        'arc_mid_mm': middle, 'arc_end_mm': end,
        'holder_rotation': rotation, 'holder_translation_mm': translation,
        'holder_to_meter_mm': gap, 'tube_segments': tube_segments,
        'foam_segments': foam_segments, 'tube_od_mm': selected['tube_od_mm'],
        'tube_id_mm': selected['tube_id_mm'],
        'nominal_foam_id_mm': selected['foam']['stock_id_mm'],
        'nominal_foam_od_mm': selected['foam']['stock_od_mm'],
        'nominal_foam_cut_length_mm': foam_length,
        'foam_cut_mm': selected['foam']['square_cut_mm'],
        'accepted_soft_neighbors': list(SOFT_NEIGHBORS),
        'foam_model_scope': selected['foam']['occupied_model_scope'],
        'assembly': selected['assembly'],
    }


def tube_spec():
    """External CAD span of the continuous tube, with no joint at the guide."""
    p = plan()
    arc = [p['bend_center_mm'][i] for i in range(3)]
    points = [p['core_guide_mm'], p['arc_start_mm']]
    radius = p['holder']['centreline_bend_r_mm']
    for index in range(1, 33):
        angle = index*math.pi/64.
        points.append(_add(arc, _add(_mul(p['flow_axis'], -radius*math.cos(angle)),
                                    [0., 0., radius*math.sin(angle)])))
    points.append(p['tube_segments'][-1]['points_mm'][-1])
    return {'points_mm': points, 'centerline_mm': points,
            'segments': p['tube_segments'], 'od_mm': p['tube_od_mm'],
            'id_mm': p['tube_id_mm'], 'radius_mm': radius,
            'minimum_radius_mm': radius, 'spool': 'blue',
            'from': 'foam-assembly.carb-water-out',
            'frm': 'foam-assembly.carb-water-out', 'to': 'digiten-flow.inlet',
            'owners': ['foam-assembly', 'digiten-flow'],
            'status': 'selected_native_layout',
            'note': 'Continuous soda tube through the plain guide and accepted R14 holder into the meter; the guide adds no insertion, joint or cut.'}


def passage_points(lower_world_xy):
    """R14 under-lid traverse from the retained lower column to the guide."""
    guide = plan()['core_guide_mm']
    radius = plan()['holder']['centreline_bend_r_mm']
    z = guide[2]
    return [(*lower_world_xy, z-2.*radius), (*lower_world_xy, z-radius),
            (*guide[:2], z-radius), tuple(guide)]


def _holder_section():
    p = plan()['holder']
    r = p['channel_d_mm']/2.
    outer = r+p['wall_mm']
    return p, r, outer, p['wall_mm']+r, (math.sqrt(2.)-1.)*r


def _teardrop(wp, x, z, radius):
    k = radius/math.sqrt(2.)
    return (wp.moveTo(x+k, z+k).lineTo(x, z+math.sqrt(2.)*radius)
            .lineTo(x-k, z+k).threePointArc((x, z-radius), (x+k, z+k)).close())


@cache
def holder_native():
    """Accepted PET-GF holder(2,3), in its flat-back printable frame."""
    import cadquery as cq
    p, r, outer, zc, lift = _holder_section()
    bend = p['centreline_bend_r_mm']
    leg = p['leg_mm']
    def section():
        x0, x1, zd = bend-outer, bend+outer, zc+lift
        return (cq.Workplane('XZ').moveTo(x0, 0.).lineTo(x1, 0.).lineTo(x1, zd)
                .threePointArc((bend, zd+outer), (x0, zd)).close())
    axis = ((0., 0., 0.), (0., 1., 0.))
    body = section().revolve(p['turn_degrees'], *axis)
    channel = _teardrop(cq.Workplane('XZ'), bend, zc, r).revolve(p['turn_degrees'], *axis)
    half = math.radians(p['turn_degrees']/2.)
    plane, origin = cq.Vector(math.sin(half), -math.cos(half), 0.), cq.Vector(0., 0., 0.)
    def mouth_at(y, radius):
        plane = cq.Plane(origin=(0., y, 0.), xDir=(1., 0., 0.), normal=(0., -1., 0.))
        return _teardrop(cq.Workplane(plane), bend, zc, radius).wires().val()
    mouth = cq.Solid.makeLoft([mouth_at(-.3, r+.8), mouth_at(.55, r-.05)], ruled=True)
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
        points = [cq.Vector(*p) for p in segment['points_mm']]
        edges.append(cq.Edge.makeThreePointArc(*points) if segment['kind']=='arc'
                     else cq.Edge.makeLine(*points))
    path = cq.Wire.assembleEdges(edges)
    first = segments[0]['points_mm'][0]
    section = cq.Workplane(cq.Plane(origin=first, xDir=(1., 0., 0.), normal=(0., 0., 1.))).circle(outer_radius)
    if inner_radius is not None:
        section = section.circle(inner_radius)
    return section.sweep(cq.Workplane().newObject([path]), isFrenet=True).val()


@cache
def tube():
    p = plan()
    return sweep(p['tube_segments'], p['tube_od_mm']/2., p['tube_id_mm']/2.)


@cache
def foam_stock():
    """Nominal one-piece63mm stock envelope before local compression."""
    p = plan()
    return sweep(p['foam_segments'], p['nominal_foam_od_mm']/2., p['nominal_foam_id_mm']/2.)


def foam_occupied(neighbors):
    """Estimated occupied foam after local compression around named bodies.

    This display subtraction is neither a cutting pattern nor a mechanical
    strain or thermal prediction. The full stock envelope remains separately
    available for its accepted soft-contact receipt.
    """
    return foam_stock().cut(holder(), *(neighbors[name] for name in SOFT_NEIGHBORS)).clean()
