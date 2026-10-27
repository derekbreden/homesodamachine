"""Selected integral tube snaps on back-top's roof and east wall.

The listed world-space line endpoints are explicit routing datums. Their
midpoints locate the guides; this registry does not infer clearance or follow
an unrelated route edit. Back-top builds in machine -Z.

Quarter-inch tube retains the selected C2 section: diameter 6.35, wing 2.40.
The 4 mm tube uses diameter 4.10 and a 1.52 mm functional spring section scaled
from C2's proportions. That smaller section is a modeled fit estimate.
"""
import math


_SITES = (
    dict(
        id='tube-snap-flavor-a-rear-roof', route_id='fluid-18',
        endpoints=((-15., 428.6, 337.75), (12.249998871231597, 428.6, 337.75)),
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=21,
        install_before=('drain-vent',),
        basis='Rear flavor-A straight under the plain roof; seat this tube before the vent crosses its downward approach.'),
    dict(
        id='tube-snap-flavor-b-rear-roof', route_id='fluid-28',
        endpoints=((-34., 420.28967877669146, 343.),
                   (39.349999999999994, 420.28967877669146, 343.)),
        face_axis=2, face=346., outward=(0., 0., -1.),
        tube_od=4., bore_diameter=4.10, wing=1.52,
        source='hardware/manifold-layout/above_core_routes.py',
        source_function='route_specifications', source_segment=15,
        install_before=(),
        basis='Long rear flavor-B straight, three millimetres below the plain roof.'),
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
        basis='East-wall fill straight; seat fill before draw, then close the existing paired fore cap.'),
)


def tube_sites():
    """Pure coordinates and section parameters; no CAD or assembly imports."""
    result = []
    for row in _SITES:
        first, last = row['endpoints']
        centre = tuple((a+b)/2. for a, b in zip(first, last))
        length = math.dist(first, last)
        along = tuple((b-a)/length for a, b in zip(first, last))
        root_distance = abs(row['face']-centre[row['face_axis']])
        result.append(dict(
            id=row['id'], route_id=row['route_id'], host='enclosure-back-top',
            centre=centre, along=along, outward=row['outward'],
            root_distance=root_distance, tube_od=row['tube_od'],
            bore_diameter=row['bore_diameter'], wing=row['wing'], span=8.,
            print_up=(0., 0., -1.), basis=row['basis'],
            install_before=row['install_before'],
            source_parameter=dict(
                file=row['source'], function=row['source_function'],
                native_segment_index=row['source_segment'],
                line_endpoints_world_mm=row['endpoints'], line_parameter=.5,
                straight_end_clearance_mm=(length-8.)/2.,
                host_face_axis='XYZ'[row['face_axis']], host_face_coordinate_mm=row['face'])))
    return tuple(result)
