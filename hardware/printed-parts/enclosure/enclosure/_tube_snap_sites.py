"""Selected integral tube snaps on back-top's roof and east wall.

The listed world-space line endpoints and parameters are explicit routing
datums; this registry does not infer clearance or follow an unrelated route
edit. Back-top builds in machine -Z. Each flavor station shares one filled
root bridge while its two seats remain individual routing records.

Quarter-inch tube retains the selected C2 section: diameter 6.35, wing 2.40.
The 4 mm tube uses diameter 4.10 and a 1.52 mm functional spring section scaled
from C2's proportions. That smaller section is a modeled fit estimate.
"""
import math


_SITES = (
    dict(
        id='tube-snap-flavor-a-roof-354', route_id='fluid-18',
        endpoints=((-45., 348., 343.), (-45., 395.28967877669146, 343.)),
        line_parameter=(354.-348.)/(395.28967877669146-348.),
        group='tube-snap-flavor-roof-354',
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=9,
        install_before=('drain-vent',),
        basis='Flavor-A roof straight, held on the forward common filled root; load from below with the vent clear.'),
    dict(
        id='tube-snap-flavor-b-roof-354', route_id='fluid-28',
        endpoints=((-55., 348., 343.), (-55., 403.6, 343.)),
        line_parameter=(354.-348.)/(403.6-348.),
        group='tube-snap-flavor-roof-354',
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=5,
        install_before=('drain-vent',),
        basis='Flavor-B roof straight, held on the forward common filled root; load from below with the vent clear.'),
    dict(
        id='tube-snap-flavor-a-roof-390', route_id='fluid-18',
        endpoints=((-45., 348., 343.), (-45., 395.28967877669146, 343.)),
        line_parameter=(390.-348.)/(395.28967877669146-348.),
        group='tube-snap-flavor-roof-390',
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=9,
        install_before=('drain-vent',),
        basis='Flavor-A roof straight, held on the aft common filled root; load from below with the vent clear.'),
    dict(
        id='tube-snap-flavor-b-roof-390', route_id='fluid-28',
        endpoints=((-55., 348., 343.), (-55., 403.6, 343.)),
        line_parameter=(390.-348.)/(403.6-348.),
        group='tube-snap-flavor-roof-390',
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=5,
        install_before=(),
        basis='Flavor-B roof straight, held on the aft common filled root; load from below.'),
    dict(
        id='tube-snap-vent-roof', route_id='drain-vent',
        endpoints=((-35.000000000000014, 380.3849605281867, 342.),
                   (-35., 398.1816974107724, 342.)),
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=4,
        install_before=(),
        basis='Straight vent span below the plain roof; its local approach clears seated flavor-A tubing.'),
    dict(
        id='tube-snap-reservoir-a-fill-east', route_id='fluid-14',
        endpoints=((94.31, 244., 258.5), (94.31, 286., 258.5)),
        face_axis=0, face=98.5, outward=(-1., 0., 0.),
        tube_od=6.35, bore_diameter=6.35, wing=2.40,
        source='hardware/manifold-layout/reservoir-a-routes.json',
        source_function='fluid-14.segments', source_segment=12,
        install_before=('fluid-16',),
        basis='East-wall fill straight; seat fill before draw and use the integral fore C2 seats on the cold-core lid.'),
)


_SHARED_ROOTS = {
    f'tube-snap-flavor-roof-{y}': dict(
        id=f'tube-snap-flavor-roof-{y}',
        bridge_origin=(-51.53, y-4., 343.), bridge_size=(3.06, 8., 3.1))
    for y in (354, 390)
}


def tube_sites():
    """Pure coordinates and section parameters; no CAD or assembly imports."""
    result = []
    for row in _SITES:
        first, last = row['endpoints']
        parameter = row.get('line_parameter', .5)
        centre = tuple(a+(b-a)*parameter for a, b in zip(first, last))
        length = math.dist(first, last)
        along = tuple((b-a)/length for a, b in zip(first, last))
        root_distance = abs(row['face']-centre[row['face_axis']])
        end_clearances = (length*parameter-4., length*(1.-parameter)-4.)
        result.append(dict(
            id=row['id'], route_id=row['route_id'], host='enclosure-back-top',
            centre=centre, along=along, outward=row['outward'],
            root_distance=root_distance, tube_od=row['tube_od'],
            bore_diameter=row['bore_diameter'], wing=row['wing'], span=8.,
            print_up=(0., 0., -1.), basis=row['basis'],
            install_before=row['install_before'],
            **({'group': _SHARED_ROOTS[row['group']]} if 'group' in row else {}),
            source_parameter=dict(
                file=row['source'], function=row['source_function'],
                native_segment_index=row['source_segment'],
                line_endpoints_world_mm=row['endpoints'], line_parameter=parameter,
                straight_end_clearance_mm=min(end_clearances),
                straight_end_clearances_mm=end_clearances,
                host_face_axis='XYZ'[row['face_axis']], host_face_coordinate_mm=row['face'])))
    return tuple(result)
