"""Bridge the last flat shaft course between actual annular walls before native infill."""
import math
import struct

from shapely import LineString, MultiLineString, Polygon, line_merge
from shapely.ops import polygonize

import map_base as source

TIE_WIDTH = .42
TIE_SPACING = TIE_WIDTH
TIE_PHASE = 2/3
WALL_INSET = .65
BRIDGE_FEED = 15 * 60
BRIDGE_FAN = 178
BRIDGE_ACCEL = 8000
FILAMENT_FLOW = .9555
FILAMENT_AREA = math.pi * .875**2
TRIANGLE = struct.Struct('<12fH')
MINIMUM_TIE_LENGTH = .1


def section(mesh, z, pose):
    x0, y0, z0 = pose
    with mesh.open('rb') as stream:
        stream.seek(80)
        count = struct.unpack('<I', stream.read(4))[0]
        triangles = TRIANGLE.iter_unpack(stream.read())
    points = []
    for triangle in triangles:
        xyz = tuple((x0+x,y0+source.COS*y+source.SIN*n,z0-source.SIN*y+source.COS*n)
                    for x,y,n in zip(triangle[3:12:3],triangle[4:12:3],triangle[5:12:3]))
        below = [p[2] < z for p in xyz]
        if all(below) or not any(below):
            continue
        intersections = []
        for a,b in zip(xyz, xyz[1:]+xyz[:1]):
            if (a[2] < z) == (b[2] < z):
                continue
            t = (z-a[2])/(b[2]-a[2])
            intersections.append(tuple(round(a[k]+t*(b[k]-a[k]), 5) for k in (0,1)))
        if len(set(intersections)) == 2:
            points.append(LineString(intersections))
    if count == 0:
        raise ValueError('Shaft STL contains no triangles')
    annulus = max(polygonize(line_merge(MultiLineString(points))), key=lambda outline: outline.area)
    if len(annulus.interiors) != 1:
        raise ValueError('Shaft stitch requires a single unbroken through-bore')
    return annulus


def ties(mesh, z, pose, layer):
    shape = section(mesh, z, pose)
    patched = shape.buffer(-WALL_INSET)
    x1,y1,x2,y2 = patched.bounds
    first = math.ceil(y1/TIE_SPACING - TIE_PHASE)
    last = math.floor(y2/TIE_SPACING - TIE_PHASE)
    output = []
    height = source.BASE_NORMAL_LAYER
    # Short open spans use the bridge feed and fan, while the dense course keeps nominal volume.
    bead_area = height * (TIE_WIDTH - height) + math.pi * (height/2)**2
    e_per_mm = FILAMENT_FLOW * bead_area / FILAMENT_AREA
    for index in range(first, last+1):
        y = (index + TIE_PHASE) * TIE_SPACING
        clipped = LineString([(x1, y), (x2, y)]).intersection(patched)
        pieces = list(getattr(clipped, 'geoms', [clipped]))
        for path in pieces:
            if path.geom_type != 'LineString' or path.length < MINIMUM_TIE_LENGTH:
                continue
            lo, _, hi, _ = path.bounds
            first_x, last_x = (lo, hi) if index%2 == 0 else (hi, lo)
            start = first_x, y, z
            end = last_x, y, z
            output.append(source.Move(start, end, BRIDGE_FEED, path.length*e_per_mm, None,
                                      'Bridge', str(TIE_WIDTH), str(height), BRIDGE_FAN, BRIDGE_ACCEL, layer))
    return output, {
        'inside_exact_model_section_mm2': shape.area,
        'through_bore_mm2': Polygon(shape.interiors[0]).area,
        'inset_mm': WALL_INSET,
        'width_mm': TIE_WIDTH,
        'pitch_mm': TIE_SPACING,
        'feed_mm_per_s': BRIDGE_FEED/60,
        'bridge_count': len(output),
        'bridge_length_mm': sum(abs(path.start[0]-path.end[0]) for path in output),
        'filament_length_mm': sum(path.e for path in output),
        'physical_course_mm': z,
        'model_sha256': source.file_hash(mesh),
    }
