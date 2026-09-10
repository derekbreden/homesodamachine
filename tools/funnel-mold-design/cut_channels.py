"""Two open V channels through the print back of each solid mold body.

Run by hand with the project's CadQuery Python. Each channel has a pointed
roof and open side mouths. The forming geometry and mating features are the
solid design's. Outputs are a separate optional design under --output.
"""
import argparse
import math
from pathlib import Path

import cadquery as cq

import solid_mold as base
from _cadq_export import export_assembly

centres = (-28.0, 28.0)
roof_rise_per_run = 5.0/3.0
cavity_depth = 28.0
core_depth = 32.0
core_mouth_depth = 3.0
core_deep_half_length = 35.0
core_taper_end = 65.0
minimum_backing = 6.0


def channel(stations, y):
    """A ruled V roof, with height varying along X and a constant side slope."""
    profiles = []
    for x, height in stations:
        half_width = (height+1)/roof_rise_per_run
        profiles.append(cq.Wire.makePolygon([
            cq.Vector(x, y-half_width, -1), cq.Vector(x, y+half_width, -1),
            cq.Vector(x, y, height)], close=True))
    return cq.Solid.makeLoft(profiles, ruled=True)


def build():
    parts, info = base.build()
    reference = dict(parts)
    back_z = parts['core'].BoundingBox().zmax
    profiles = {
        'cavity': [(-120, cavity_depth), (120, cavity_depth)],
        'core': [(-110, core_mouth_depth), (-core_taper_end, core_mouth_depth),
                 (-core_deep_half_length, core_depth), (core_deep_half_length, core_depth),
                 (core_taper_end, core_mouth_depth), (110, core_mouth_depth)]}
    reports = {}
    for name in ('cavity', 'core'):
        tools = []
        for y in centres:
            tool = channel(profiles[name], y)
            if name == 'core':
                tool = tool.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, back_z))
            tools.append(tool)
        removed = [base.one(reference[name].intersect(tool), f'{name} channel')
                   for tool in tools]
        clearance = min(p.distance(parts['funnel']) for p in removed)-base.finish_allowance
        assert clearance >= minimum_backing, (name, 'forming backing', clearance)
        assert all(p.distance(parts['rod']) >= minimum_backing for p in removed)
        parts[name] = base.one(reference[name].cut(*tools), name)
        assert reference[name].intersect(parts[name]).Volume() > parts[name].Volume()-0.001
        assert parts[name].intersect(parts['funnel']).Volume() < 0.001
        # The cutter must open through both sides above a flat shelf. At these
        # stations its section is entirely outside the original body's bounds.
        assert all(t.BoundingBox().xmin < reference[name].BoundingBox().xmin and
                   t.BoundingBox().xmax > reference[name].BoundingBox().xmax for t in tools)
        for y in centres:
            passage = cq.Solid.makeCylinder(0.5, 240, cq.Vector(-120, y, 1.1), cq.Vector(1, 0, 0))
            if name == 'core':
                passage = passage.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, back_z))
            assert parts[name].intersect(passage).Volume() < 0.001, 'side passage obstructed'
        bed_z = reference[name].BoundingBox().zmin if name == 'cavity' else back_z
        bed_area = lambda s: sum(f.Area() for f in s.Faces()
            if f.geomType() == 'PLANE' and abs(f.Center().z-bed_z) < 1e-6
            and abs(f.normalAt().z) > .999)
        reports[name] = {
            'baseline_volume_ml': reference[name].Volume()/1000,
            'volume_ml': parts[name].Volume()/1000,
            'removed_ml': sum(p.Volume() for p in removed)/1000,
            'minimum_added_channel_to_forming_face_mm': clearance,
            'bed_contact_mm2': bed_area(parts[name]),
            'baseline_bed_contact_mm2': bed_area(reference[name])}
        info['volume_ml'][name] = parts[name].Volume()/1000
    assert parts['cavity'].intersect(parts['core']).Volume() < 0.001
    info['channels'] = {
        'count_per_body': 2, 'centres_y_mm': centres,
        'roof_angle_from_bed_degrees': math.degrees(math.atan(roof_rise_per_run)),
        'max_horizontal_growth_per_0_40_mm_layer': 0.4/roof_rise_per_run,
        'cavity_depth_mm': cavity_depth, 'core_depth_mm': core_depth,
        'core_side_mouth_height_mm': core_mouth_depth,
        'core_side_mouth_width_mm': 2*core_mouth_depth/roof_rise_per_run,
        'clear_through_passage_diameter_mm': 1.0,
        'parts': reports}
    return parts, info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parts, info = build()
    base.write_parts(parts, info, args.output)
    # A transverse section cuts across both V channels and shows their roof angle.
    section = cq.Assembly()
    slab = base.box(2, 240, -1, 120)
    colors = {'cavity': cq.Color('#3D9998'), 'core': cq.Color('#D8A751'),
              'funnel': cq.Color('#555C68'), 'rod': cq.Color('#AAB9C8')}
    for name, part in parts.items():
        section.add(part.intersect(slab), name=name, color=colors[name])
    export_assembly(section, str(args.output/'channel-section.step'))
    backs = cq.Assembly()
    for name, dx in (('cavity', -120), ('core', 120)):
        part = parts[name]
        if name == 'cavity':
            part = part.rotate((0, 0, 0), (1, 0, 0), 180)
        part = part.translate((dx, 0, -part.BoundingBox().zmin))
        backs.add(part, name=name, color=colors[name])
    export_assembly(backs, str(args.output/'backs.step'))


if __name__ == '__main__':
    main()
