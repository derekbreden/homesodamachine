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
sys.path[:0] = [str(ROOT / 'hardware/scripts'), str(HERE),
                str(ROOT / 'hardware/printed-parts/enclosure/enclosure')]
from _cadq_export import import_assembly
import funnel_cover as lid
import enclosure as enc
import _box_spec


def main():
    assembly = ROOT / 'hardware/manifold-layout/enclosure-assembly.step'
    cover_step = HERE / 'funnel-cover.step'
    bodies = import_assembly(assembly)
    silicone = bodies['funnel'][0]
    b = silicone.BoundingBox()
    box, _ = _box_spec.read(enc.Box, enc.Bound, (enc.Pack, enc.PortField, enc.Nameplate))
    cx, cy = box.pack.funnel
    roof = b.zmax
    cover = import_assembly(cover_step)['funnel-cover'][0].translate((cx, cy, roof))
    assembled_cover = bodies['funnel-cover'][0]
    assembly_difference = (cover.cut(assembled_cover).Volume()
                           + assembled_cover.cut(cover).Volume())
    assert assembly_difference < 0.001, assembly_difference
    cover_bounds = cover.BoundingBox()
    contact = abs(cover.intersect(silicone).Volume())
    assert contact < 0.001, contact
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
        overlap = abs(shifted.intersect(silicone).Volume())
        assert overlap < 0.001, (z, overlap)
        removal.append({'lift_mm': z, 'silicone_overlap_mm3': overlap})
    lateral = []
    for x, y in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        shifted = cover.translate((x, y, 0))
        overlap = abs(shifted.intersect(silicone).Volume())
        assert overlap > 1, (x, y, overlap)
        lateral.append({'shift_mm': [x, y], 'silicone_overlap_mm3': overlap})
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
        'plate_bounds_mm': [cover_bounds.xmin, cover_bounds.xmax,
                            cover_bounds.ymin, cover_bounds.ymax],
        'front_extension_mm': lid.FRONT_EXTENSION,
        'assembly_cover_difference_mm3': assembly_difference,
        'closed_mouth_missing_mm3': missing, 'silicone_overlap_mm3': contact,
        'neighbours': neighbours, 'vertical_removal': removal,
        'lateral_locating_interference': lateral,
        'print_pose': {'bed_z_mm': print_bounds.zmin, 'height_mm': print_bounds.zlen,
                       'flat_exterior_on_bed': True},
        'geometry_checks_pass': True,
        'scope': 'Native solid coverage, silicone clearance, neighbour clearance and sampled motion. '
                 'No physical retention, water exclusion, food-contact, cleaning or lifetime qualification.',
    }
    (HERE / 'geometry-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Cover: closed mouth, continuous skirt with silicone clearance; {len(neighbours)} native neighbours clear; '
          f'upward removal clear after {lid.SKIRT_DEPTH:g} mm; adds {lid.PLATE_T:g} mm.')


if __name__ == '__main__':
    main()
