"""Crop the production B-fill cup/lid and compare two fore clamp rows."""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
OUT = ROOT / '.cache/prints/2026-10-28-b-fill-local'
sys.path[:0] = [str(ROOT / 'hardware' / p) for p in (
    'scripts', 'manifold-layout', 'printed-parts/cold-core',
    'printed-parts/cadlib')]
import above_core
import _above_core_mounts as mounts
import _cold_core_interface as core
import _reservoir_b_fill as fill
from _show_skin import write_bed_file


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = fill.passage()
    lo, hi = data['stock_min_world_mm'], data['stock_max_world_mm']
    region = cq.Solid.makeBox(*(b-a for a, b in zip(lo, hi)), cq.Vector(*lo))
    height = core.foam_cap_height - core.head_pad_height
    frame = above_core.frame_location(above_core.cap_lid_pose())
    cap_dir = ROOT / 'hardware/printed-parts/cold-core/foam-cap'
    sources = {n: cap_dir / (n+'.step') for n in ('foam-cap-top', 'foam-cap-lid-top')}
    cup = cq.importers.importStep(str(sources['foam-cap-top'])).val()
    cup = cup.translate((0, 0, -height)).moved(frame).intersect(region).clean()
    lid = cq.importers.importStep(str(sources['foam-cap-lid-top'])).val().moved(frame)
    lid = lid.intersect(region).clean()
    aft_y = data['clamp_stations'][0]['axis_world_xy_mm'][1]
    midpoint_y = (lo[1] + aft_y) / 2.0
    top, bottom, face = (data[k] for k in (
        'cup_top_world_z_mm', 'lid_bottom_world_z_mm', 'lid_face_world_z_mm'))

    def cylinder(x, y, radius, z0, z1):
        return cq.Solid.makeCylinder(radius, z1-z0, cq.Vector(x, y, z0))

    def pilot(x, y):
        return cylinder(x, y, data['clamp_pilot_diameter_mm']/2, top-9, top)

    def lid_hole(x, y):
        return cylinder(x, y, 1.65, bottom, face).fuse(
            cylinder(x, y, 2.9, face-3.15, face)).clean()

    alternate_cup, alternate_lid = cup, lid
    for station in data['clamp_stations'][1:]:
        x, y = station['axis_world_xy_mm']
        alternate_cup = alternate_cup.fuse(pilot(x, y)).cut(pilot(x, midpoint_y)).clean()
        alternate_lid = alternate_lid.fuse(lid_hole(x, y)).cut(lid_hole(x, midpoint_y)).clean()

    report = {
        'scope': 'Local cap and lid print coupons only; production geometry is retained.',
        'production_step_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources.values()},
        'generator_sha256': sha(Path(__file__)),
        'world_crop_mm': [lo, hi],
        'aft_screw_y_mm': aft_y,
        'variants': {},
        'normal_seating_allowance_mm': bottom-top,
        'roof_allowance_mm': data['supported_roof_allowance_mm'],
        'cup_mouth_relief_mm': data['cup_mouth_relief_mm'],
        'production_print_up_retained': True,
    }
    for name, cy, shapes in (
            ('current', data['clamp_stations'][1]['axis_world_xy_mm'][1], (cup, lid)),
            ('midpoint', midpoint_y, (alternate_cup, alternate_lid))):
        directory = OUT / name
        directory.mkdir(exist_ok=True)
        row = {'fore_screw_y_mm': cy, 'fore_span_mm': cy-lo[1],
               'aft_span_mm': aft_y-cy, 'pieces': {}}
        for kind, world in zip(('cup', 'lid'), shapes):
            assert world.isValid() and len(world.Solids()) == 1
            local = mounts.world_shape_in_cap(world)
            if kind == 'cup':
                local = local.translate((0, 0, height))
            step, stl = directory/(kind+'.step'), directory/(kind+'.stl')
            cq.exporters.export(local, str(step))
            write_bed_file(local, stl)
            row['pieces'][kind] = {
                'valid': True, 'solids': 1, 'world_bounds_mm': bounds(world),
                'native_bounds_mm': bounds(local), 'volume_mm3': world.Volume(),
                'step': str(step.relative_to(ROOT)), 'step_sha256': sha(step),
                'stl': str(stl.relative_to(ROOT)), 'stl_sha256': sha(stl)}
        row['cup_lid_overlap_mm3'] = max(0., shapes[0].intersect(shapes[1]).Volume())
        report['variants'][name] = row

    # Purpose review only: these are the two native diagnostic locations.
    # The straight-Z interval belongs to the cup's roof above the descending bore.
    native = cq.importers.importStep(str(sources['foam-cap-top'])).val()
    points = ((93.184, -43.289, 13.608), (93.184, -43.289, 14.450),
              (101.503, -48.190, 13.950), (101.504, -48.188, 13.948))
    from pick_read import solid_near
    report['diagnostic_pick_faces'] = [
        {'native_point_mm': p, 'faces': [
            {'kind': k, 'parameters': params, 'nearest_mm': list(on), 'distance_mm': d}
            for k, params, on, d in solid_near(native.Faces(), p, .02)]}
        for p in points]
    (HERE/'geometry.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: {'fore_y_mm': v['fore_screw_y_mm'],
                         'fore_span_mm': v['fore_span_mm'], 'aft_span_mm': v['aft_span_mm'],
                         'pieces': {n: p['volume_mm3'] for n, p in v['pieces'].items()}}
                      for k, v in report['variants'].items()}, indent=2))


if __name__ == '__main__':
    main()
