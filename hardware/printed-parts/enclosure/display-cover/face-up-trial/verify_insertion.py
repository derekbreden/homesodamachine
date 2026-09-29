"""Check a conservative circular-bend entry envelope, without claiming flex strength."""
import json
import math
from shapely.geometry import Polygon, box
import face_up_trial as fit


def main():
    h, p, t, w = fit.cover.cover_x/2, fit.WING_REACH, fit.THICK, fit.WING_THICK
    outline = [(-h-p, 0), (h+p, 0), (h+p, w), (h, w), (h, t), (-h, t), (-h, w), (-h-p, w)]
    points = []
    for a, b in zip(outline, outline[1:]+outline[:1]):
        count = max(2, math.ceil(math.dist(a, b)/.1))
        points.extend((a[0]+(b[0]-a[0])*k/count, a[1]+(b[1]-a[1])*k/count) for k in range(count))
    receiver = box(-fit.WIDTH/2, -fit.FRAME_THICK+t, fit.WIDTH/2, t)
    receiver = receiver.difference(box(-h-fit.FACE_AIR, 0, h+fit.FACE_AIR, t+50))
    for side in (-1, 1):
        x0, x1 = sorted((side*(h-.1), side*(h+p+fit.TIP_AIR)))
        receiver = receiver.difference(box(x0, 0, x1, w+fit.BEARING_AIR))
    readings = []
    for i in range(101):
        angle = .55*i/100
        def bend(x, z):
            if angle == 0:
                return x, z
            r, n = h/angle, t/2
            phi = min(abs(x), h)/r
            xx = (r+z-n)*math.sin(phi)
            zz = (r+z-n)*math.cos(phi)-r*math.cos(angle)+n
            if abs(x) > h:
                xx += (abs(x)-h)*math.cos(angle)
                zz -= (abs(x)-h)*math.sin(angle)
            return math.copysign(xx, x), zz
        curved = [bend(*point) for point in points]
        lift = .01-min(z for x, z in curved)
        polygon = Polygon([(x, z+lift) for x, z in curved])
        overlap = polygon.intersection(receiver).area
        assert polygon.is_valid and overlap < 1e-6, (angle, overlap)
        readings.append({'end_angle_rad':angle, 'lift_mm':lift, 'intersection_area_mm2':overlap,
                         'span_mm':polygon.bounds[2]-polygon.bounds[0]})
    assert readings[-1]['span_mm'] < 2*(h+fit.FACE_AIR)
    report = {'pass':True, 'samples':len(readings), 'checks':readings,
              'motion':'Flex the middle outward, keep both wing tips above the slot floor, then release flat into the pockets.',
              'scope':'Conservative filled X/Z outline under ideal circular bending. Rounded wing ends are treated as rectangular. Does not qualify force, strain tolerance, fatigue or three-dimensional corner motion; those need the physical trial.',
              'ideal_outer_fibre_strain_at_max_bend':fit.THICK/2*.55/h,
              'maximum_section_overlap_mm2':max(r['intersection_area_mm2'] for r in readings)}
    (fit.HERE/'insertion-envelope.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'}, indent=2))


if __name__ == '__main__':
    main()
