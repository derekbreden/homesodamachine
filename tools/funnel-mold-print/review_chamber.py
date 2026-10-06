"""Read the complete mold/hardware envelope and dry-side breather drill paths."""
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT/'hardware/printed-parts/zone-c/funnel-mold'
EPS = 0.0001


def cylinder(radius, bottom, top, xy):
    return cq.Solid.makeCylinder(radius, top-bottom, cq.Vector(*xy, bottom))


def main():
    info = json.loads((MODELS/'design.json').read_text())
    shapes = {n: cq.importers.importStep(str(MODELS/(n+'.step'))).val()
              for n in ('cavity', 'core', 'rod', 'funnel')}
    assert all(s.isValid() and len(s.Solids()) == 1 for s in shapes.values())
    source = ROOT/'hardware/ledger/tools.md'
    row = next(line for line in source.read_text().splitlines() if '**PB Motor Tech 5-gal' in line)
    assert 'B0D78ZM928' in row and '11.8" × 11.8" interior' in row
    diameter = height = 11.8*25.4
    flange_bottom = info['parting_z_mm']-info['flange_thickness_mm']
    core_back = shapes['core'].BoundingBox().zmax
    hardware = []
    for xy in info['clamping']['centres_xy_mm']:
        lower_washer = cylinder(4.5, flange_bottom-.8, flange_bottom, xy).cut(
            cylinder(2.15, flange_bottom-1, flange_bottom+1, xy))
        upper_washer = cylinder(4.5, core_back, core_back+.8, xy).cut(
            cylinder(2.15, core_back-1, core_back+1.8, xy))
        head = cylinder(3.5, flange_bottom-4.8, flange_bottom-.8, xy)
        shaft = cylinder(2, flange_bottom-.8, flange_bottom-.8+20, xy)
        # The bounding cylinder contains a 7 mm across-flats M4 hex nut.
        nut = cylinder(7/math.sqrt(3), core_back+.8, core_back+4, xy).cut(
            cylinder(2.15, core_back, core_back+5, xy))
        for name, part in [('head', head), ('shaft', shaft), ('lower washer', lower_washer),
                           ('upper washer', upper_washer), ('nut envelope', nut)]:
            overlaps = {n: part.intersect(shapes[n]).Volume() for n in ('cavity', 'core')}
            assert max(overlaps.values()) < EPS, (xy, name, overlaps)
            vertices, _ = part.tessellate(.005, .05)
            points = np.array([v.toTuple() for v in vertices])
            hardware.append({'part': name, 'centre_xy_mm': xy,
                'maximum_radius_mm': float(np.linalg.norm(points[:, :2], axis=1).max()),
                'top_mm': part.BoundingBox().zmax, 'mold_interference_mm3': overlaps})
    width, depth = info['flange_plan_mm']
    radius = 24.0
    exact_radius = math.hypot(width/2-radius, depth/2-radius)+radius
    mesh_radius = max(float(np.linalg.norm(trimesh.load(MODELS/(n+'.stl'),
        force='mesh').vertices[:, :2], axis=1).max()) for n in ('cavity', 'core'))
    assert abs(exact_radius-mesh_radius) < .02
    whole_radius = max(exact_radius, *(h['maximum_radius_mm'] for h in hardware))
    whole_top = max(core_back, *(h['top_mm'] for h in hardware))
    assert whole_radius < diameter/2 and whole_top < height
    drill_paths = []
    spec = info['postprint_breathers']
    for name in ('cavity', 'core'):
        record = spec[name]
        for point, axis in zip(record['entry_xyz_mm'], record['drill_axes']):
            # Move inside the entry plane, retaining a small geometric tolerance.
            start = cq.Vector(*point)+cq.Vector(*axis)*.001
            tool = cq.Solid.makeCylinder(spec['diameter_mm']/2,
                record['depth_mm']-.001, start, cq.Vector(*axis))
            outside = tool.cut(shapes[name]).Volume()
            clearance = tool.distance(shapes['funnel'])
            assert outside < EPS and clearance > 5, (name, outside, clearance)
            drill_paths.append({'part': name, 'entry_xyz_mm': point, 'axis': axis,
                'depth_mm': record['depth_mm'], 'outside_stock_mm3': outside,
                'casting_clearance_mm': clearance})
    files = [MODELS/(n+'.'+suffix) for n in ('cavity', 'core') for suffix in ('step', 'stl')]
    files += [MODELS/'design.json', Path(__file__)]
    result = {'checked_date': '2026-10-05',
        'method': 'Native STEP hardware-clearance booleans, exact rounded-flange enclosing circle, STL bound and drill-path reads.',
        'chamber': {'asin': 'B0D78ZM928', 'source': str(source.relative_to(ROOT)),
            'recorded_interior_inches': [11.8, 11.8], 'diameter_mm': diameter, 'height_mm': height,
            'source_row_sha256': hashlib.sha256(row.encode()).hexdigest()},
        'mold_and_M4x20_hardware': {'enclosing_diameter_mm': 2*whole_radius,
            'height_mm': whole_top, 'radial_clearance_mm': diameter/2-whole_radius,
            'height_clearance_mm': height-whole_top, 'stations': hardware,
            'lower_washer_thickness_mm': .8, 'upper_washer_thickness_mm': .8,
            'cap_head_diameter_mm': 7, 'cap_head_height_mm': 4, 'nut_across_flats_mm': 7,
            'nut_height_mm': 3.2},
        'catch_tray_maximum_diameter_mm': 260,
        'breather_drill_paths': drill_paths,
        'pressure': info['load_screen'],
        'scope': 'Nominal fit in the acquired chamber record, including closure hardware. No physical insertion or sparse-print stiffness measurement is claimed. Dry-side holes are drilled after printing to connect the gyroid to chamber air.',
        'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        'passed': True}
    (MODELS/'chamber-check.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: result[k] for k in ('passed', 'breather_drill_paths', 'pressure')}, indent=2))


if __name__ == '__main__':
    main()
