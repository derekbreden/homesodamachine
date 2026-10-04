"""Check the cover against named native bodies in the current assembly export.

This is a design integration receipt. It does not model silicone forces or
qualify the physical drip barrier.
"""

import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(HERE)]
from _cadq_export import import_assembly
import funnel_cover as lid


def main():
    assembly = ROOT / 'hardware/manifold-layout/enclosure-assembly.step'
    cover_step = HERE / 'funnel-cover.step'
    bodies = import_assembly(assembly)
    silicone = bodies['funnel'][0]
    b = silicone.BoundingBox()
    cx, cy, roof = (b.xmin + b.xmax) / 2, (b.ymin + b.ymax) / 2, b.zmax
    cover = import_assembly(cover_step)['funnel-cover'][0].translate((cx, cy, roof))
    contact = lid.contact_reading(cover, silicone, cx, cy, roof)
    assert contact['pad_contact_mm3'] > 0
    assert contact['outside_pads_mm3'] < 0.001, contact
    # The native plate contains a complete sheet over the full mouth, with
    # the thickness required for the solid cover. No thumb feature enters it.
    mouth_sheet = lid.rounded(lid.MOUTH_W, lid.MOUTH_D, lid.funnel.mouth_corner_r,
                              roof, roof + lid.PLATE_T, cx, cy)
    missing = mouth_sheet.cut(cover).Volume()
    assert missing < 0.001, missing
    # Read the actual cover/body solids. Bounding boxes only prune pairs
    # that cannot meet during the complete straight upward removal.
    neighbours = {}
    for name, (shape, _colour) in bodies.items():
        if name in ('funnel', 'funnel-cover'):
            continue
        q = shape.BoundingBox()
        c = cover.BoundingBox()
        if q.xmax < c.xmin or q.xmin > c.xmax or q.ymax < c.ymin or q.ymin > c.ymax:
            continue
        if q.zmax < c.zmin or q.zmin > c.zmax + lid.SKIRT_DEPTH + 2:
            continue
        overlaps = [cover.translate((0, 0, z)).intersect(shape).Volume()
                    for z in (0, 0.5, 1, 2, 4, 6, 8)]
        assert max(overlaps) < 0.001, (name, overlaps)
        neighbours[name] = {'gap_mm': cover.distance(shape),
                            'max_removal_overlap_mm3': max(overlaps)}
    removal = []
    for z in (0, 0.5, 1, 2, 4, 6, 8):
        shifted = cover.translate((0, 0, z))
        reading = lid.contact_reading(shifted, silicone, cx, cy, roof + z)
        assert reading['outside_pads_mm3'] < 0.001, (z, reading)
        if z >= lid.SKIRT_DEPTH:
            assert reading['pad_contact_mm3'] < 0.001, (z, reading)
        removal.append({'lift_mm': z, **reading})
    lateral = []
    for x, y in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        shifted = cover.translate((x, y, 0))
        reading = lid.contact_reading(shifted, silicone, cx + x, cy + y, roof)
        assert reading['outside_pads_mm3'] > 1, (x, y, reading)
        lateral.append({'shift_mm': [x, y], **reading})
    native_print = import_assembly(HERE / 'funnel-cover-print.step')['funnel-cover'][0]
    print_bounds = native_print.BoundingBox()
    assert abs(print_bounds.zmin) < 1e-6
    assert abs(print_bounds.zlen - lid.PLATE_T - lid.SKIRT_DEPTH) < 1e-6
    report = {
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (Path(__file__), HERE / 'funnel_cover.py',
                                    HERE.parent / 'funnel/funnel.py', cover_step,
                                    HERE / 'funnel-cover-print.step', HERE / 'funnel-cover.stl',
                                    HERE / 'funnel-cover-print.stl', assembly)},
        'seating_mm': [cx, cy, roof], 'added_height_mm': lid.PLATE_T,
        'closed_mouth_missing_mm3': missing, 'nominal_contact': contact,
        'neighbours': neighbours, 'vertical_removal': removal,
        'lateral_locating_interference': lateral,
        'print_pose': {'bed_z_mm': print_bounds.zmin, 'height_mm': print_bounds.zlen,
                       'flat_exterior_on_bed': True},
        'geometry_checks_pass': True,
        'scope': 'Native solid coverage, intended local silicone contact, neighbour clearance and sampled motion. '
                 'No physical retention, water exclusion, food-contact, cleaning or lifetime qualification.',
    }
    (HERE / 'geometry-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Cover: closed mouth, four local pad contacts; {len(neighbours)} native neighbours clear; '
          f'upward removal clear after {lid.SKIRT_DEPTH:g} mm; adds {lid.PLATE_T:g} mm.')


if __name__ == '__main__':
    main()
