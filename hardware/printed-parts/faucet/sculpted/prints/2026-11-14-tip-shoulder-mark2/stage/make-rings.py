"""Write removable PET-GF interface rings for the three 1904 screw seats."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from math import cos, dist, pi, radians, sin
from pathlib import Path


CENTERS = ((183., 106.), (205.5, 85.7), (228., 106.))
FIRST_Z = .20
PITCH = .24
COURSES = 13
OPENING_ANGLE_DEGREES = 40
ARC_SEGMENTS = 32
TURN_SEGMENTS = 6
TRAVEL_Z = 5.
FILAMENT_DIAMETER = 1.75
FLOW_RATIO = .9555
RETRACT = .8


def move(origin, radial, tangent, r, t=0.):
    return tuple(round(x + r * u + t * v, 5) for x, u, v in zip(origin, radial, tangent))


def unit(angle):
    return cos(angle), sin(angle)


def ring_path(center, inner, outer):
    """Give the two joined arcs a single opening reachable from the bed face."""
    opening_angle = radians(OPENING_ANGLE_DEGREES)
    start = -pi / 2 + opening_angle / 2
    span = 2 * pi - opening_angle
    angles = [start + span * i / ARC_SEGMENTS for i in range(ARC_SEGMENTS + 1)]
    points = [move(center, unit(angle), (0., 0.), inner) for angle in angles]
    radial = unit(angles[-1])
    tangent = -radial[1], radial[0]
    radius = (outer - inner) / 2
    middle = (outer + inner) / 2
    for number in range(1, TURN_SEGMENTS + 1):
        angle = pi * number / TURN_SEGMENTS
        points.append(move(center, radial, tangent, middle - radius * cos(angle), radius * sin(angle)))
    points.extend(move(center, unit(angle), (0., 0.), outer) for angle in reversed(angles[:-1]))
    return points


def point(xy):
    return f'X{xy[0]:.5f} Y{xy[1]:.5f}'


def write(output):
    rows = []
    total = 0.
    with output.open('w') as stream:
        def line(command):
            stream.write(command + '\n')

        for course in range(COURSES):
            z = round(FIRST_Z + course * PITCH, 2)
            height, width = (PITCH, .48) if course else (FIRST_Z, .55)
            inner, outer = (2.06, 2.49) if course else (2.03, 2.53)
            # The area matches the rounded-road convention of the donor.
            e_per_mm = height * (width - height * (1 - pi / 4)) * FLOW_RATIO / (pi * (FILAMENT_DIAMETER / 2) ** 2)
            rings = [ring_path(center, inner, outer) for center in CENTERS]
            travel_feed, deposition_feed = 9000, 1800 if course else 1500
            first = rings[0][0]
            line(f'; HSM_PLATE_RING_Z: {z:.2f}')
            line(f'; HSM_ENTRY_XYZ: {first[0]:.5f} {first[1]:.5f} {z:.5f}')
            line(f'; HSM_ENTRY_RETRACT_MM: {RETRACT:g}')
            line('M106 S0')
            line('M204 S500')
            line('; FEATURE: Support interface' if course >= COURSES - 3 else '; FEATURE: Support')
            line(f'; LINE_WIDTH: {width:g}')
            line(f'; LAYER_HEIGHT: {height:g}')
            for index, path in enumerate(rings):
                if index:
                    line(f'G1 Z{TRAVEL_Z:.3f} F900')
                    line(f'G1 {point(path[0])} F{travel_feed}')
                    line(f'G1 Z{z:.5f} F900')
                line(f'G1 E{RETRACT:g} F1800')
                line(f'G1 F{deposition_feed}')
                for start, end in zip(path, path[1:]):
                    amount = round(dist(start, end) * e_per_mm, 6)
                    line(f'G1 {point(end)} E{amount:.6f}')
                    total += amount
                line(f'G1 E-{RETRACT:g} F1800')
            flat = [xy for path in rings for xy in path]
            rows.append({
                'z_mm': z, 'bead_height_mm': height, 'bead_width_mm': width,
                'centerline_radii_mm': [inner, outer], 'outer_material_radius_mm': outer + width / 2,
                'centerline_bounds_xy_mm': [[min(p[a] for p in flat) for a in range(2)],
                                            [max(p[a] for p in flat) for a in range(2)]],
                'road_count': sum(len(p) - 1 for p in rings), 'lift_z_mm': TRAVEL_Z,
            })

    return {
        'purpose': __doc__, 'object': 1904, 'seat_centers_xy_mm': CENTERS, 'courses': rows,
        'gap_opening_angle_deg': OPENING_ANGLE_DEGREES, 'deposition_mm_filament': round(total, 6),
        'gcode_sha256': sha256(output.read_bytes()).hexdigest(),
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('report', type=Path)
    args = parser.parse_args()
    args.report.write_text(json.dumps(write(args.output), indent=2) + '\n')


if __name__ == '__main__':
    main()
