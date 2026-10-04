"""Independent complete-casting and fit checks for the removable forming tool.

Reads the current native print and tooling files; builds only the analytical
forming envelope in memory. Does not export CAD, run a slicer or touch a printer.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys

os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[2]
MODELS = ROOT/'hardware/printed-parts/zone-c/funnel-mold'
sys.path[:0] = [str(MODELS), str(ROOT/'hardware/scripts')]
import forming_mandrel as mandrel
import funnel
from _cadq_export import import_assembly, import_step

EPS = 0.0001


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def difference(actual, reference):
    return {'actual_minus_reference_mm3': actual.cut(reference).Volume(),
            'reference_minus_actual_mm3': reference.cut(actual).Volume()}


def matched(actual, reference):
    result = difference(actual, reference)
    assert all(abs(value) < EPS for value in result.values()), result
    return result


def body_info(shape):
    assert shape.isValid() and len(shape.Solids()) == 1
    b = shape.BoundingBox()
    return {'valid': True, 'solids': 1,
            'bounds_mm': [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax],
            'volume_mm3': shape.Volume()}


def zone(shape, bottom, top):
    return shape.intersect(mandrel.slab(bottom, top))


def cylinder_row(rows, diameter, bottom, top):
    matches = [row for row in rows if abs(row['diameter_mm']-diameter) < EPS
               and abs(row['z_mm'][0]-bottom) < EPS
               and abs(row['z_mm'][1]-top) < EPS]
    assert len(matches) == 1, (diameter, bottom, top, rows)
    return matches[0]


def seat_motion(shapes, z, shift):
    """Native fit envelopes and one feasible centering route; no force model."""
    core, cavity, pin = (shapes[name] for name in ('core', 'cavity', 'rod'))
    x, y = funnel.neck_dx, funnel.neck_dy
    bottom = z['bottom']+shift
    rows, guided = [], []
    for azimuth in range(0, 360, 45):
        angle = math.radians(azimuth)
        dx, dy = math.cos(angle), math.sin(angle)
        for offset in (0.0, 0.19):
            moved = pin.translate((offset*dx, offset*dy, 0))
            assert cavity.intersect(moved).Volume() < EPS
            for lift in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9):
                overlap = core.translate((0, 0, lift)).intersect(moved).Volume()
                assert abs(overlap) < EPS, (azimuth, offset, lift, overlap)
                rows.append({'azimuth_deg': azimuth, 'upright_offset_mm': offset,
                             'core_lift_mm': lift, 'overlap_mm3': overlap})
        for lift in (0, .5, 1, 2, 3, 4, 5, 6, 7, 7.5, 8):
            # A feasible path through the lead-in, not a commanded operator angle
            # or proof that gravity/contact forces select this precise motion.
            tilt = .3*(lift/7) if lift <= 7 else .3+.7*(lift-7)
            moved = pin.rotate((x, y, bottom), (x-dy, y+dx, bottom), tilt)
            moved = moved.translate((0, 0, bottom-moved.BoundingBox().zmin))
            overlaps = {'core': core.translate((0, 0, lift)).intersect(moved).Volume(),
                        'cavity': cavity.intersect(moved).Volume()}
            assert all(abs(v) < EPS for v in overlaps.values()), (azimuth, lift, tilt, overlaps)
            guided.append({'azimuth_deg': azimuth, 'core_lift_mm': lift,
                           'pin_tilt_deg': tilt, 'overlap_mm3': overlaps})
    return {'upright_drop_in_closure': {'poses': len(rows),
            'pure_offset_mm': [0, .19], 'core_lift_mm': [0, 9], 'readings': rows},
        'feasible_lead_in_centering_route': {'poses': len(guided),
            'initial_tilt_deg': 1, 'seated_tilt_deg': 0, 'readings': guided},
        'scope': 'Ordinary closure has loose seat guidance. This checks geometry through the full lift and a feasible centering route. It requests no operator angle/offset measurement and does not establish printed insertion force or automatic contact dynamics.'}


def review(models, baseline=None):
    design = json.loads((models/'design.json').read_text())
    tool_info = json.loads((models/'forming-mandrel-design.json').read_text())
    shell_hashes = {f'{name}.{suffix}': sha(models/f'{name}.{suffix}')
                    for name in ('cavity', 'core') for suffix in ('step', 'stl', 'step.mesh')}
    assert shell_hashes == design['native_shell_sha256']
    if baseline:
        held = json.loads(baseline.read_text())['paths']
        assert all(sha(ROOT/path) == digest for path, digest in held.items())
    assert all(sha(models/name) == digest for name, digest in tool_info['sha256'].items())
    assembly = import_assembly(str(models/'assembly.step'))
    assert set(assembly) == {'cavity', 'core', 'rod', 'funnel'}
    shapes = {name: import_step(str(models/f'{name}.step')).val()
              for name in ('cavity', 'core', 'rod', 'funnel')}
    body_readings = {name: body_info(shape) for name, shape in shapes.items()}
    bindings = {name: matched(shape, assembly[name][0]) for name, shape in shapes.items()}
    raw = import_step(str(models/'forming-mandrel.step')).val()
    finished = import_step(str(models/'forming-mandrel-finished.step')).val()
    body_info(raw)
    body_info(finished)
    source_print = mandrel.raw_print_frame()
    source_reference = mandrel.finished_local().translate((0, 0, -mandrel.stations()['bottom']))
    bindings['raw_tool_source_vs_native'] = matched(raw, source_print)
    bindings['finished_tool_source_vs_native'] = matched(finished, source_reference)
    z = mandrel.stations()
    shift = design['funnel_to_mould_z_translation_mm']
    tool_translation = (funnel.neck_dx, funnel.neck_dy, z['bottom']+shift)
    tool = finished.translate(tool_translation)
    bindings['finished_tool_vs_assembled_rod'] = matched(tool, shapes['rod'])

    native_funnel_path = ROOT/'hardware/printed-parts/zone-c/funnel/funnel.step'
    native_funnel = import_step(str(native_funnel_path)).val()
    current_cast = shapes['funnel'].translate((0, 0, -shift))
    bindings['whole_casting_vs_current_native_funnel'] = matched(current_cast, native_funnel)
    print('Building independent full forming envelope in memory', flush=True)
    exterior, bore, meta = funnel.build_solids()
    # This cutter uses the complete bowl cavity above its neck and the new tool
    # below it. It independently derives every wall and the rectangular block.
    bowl_tool = bore.intersect(funnel._box(600, 600, meta['neck_z'], meta['top_z']+1, 0, 0))
    independently_cast = exterior.cut(bowl_tool, mandrel.finished_funnel_frame()).clean()
    body_info(independently_cast)
    bindings['independent_whole_casting_vs_current_native_funnel'] = matched(
        independently_cast, native_funnel)
    bindings['independent_whole_casting_vs_full_source_funnel'] = matched(
        independently_cast, exterior.cut(bore).clean())
    print('Complete casting CSG matches; checking profile, stock and socket poses', flush=True)

    native_raw_rows = mandrel.cylindrical_faces(raw)
    native_finished_rows = mandrel.cylindrical_faces(finished)
    raw_land = cylinder_row(native_raw_rows, funnel.sealing_id-2*mandrel.finishing_reserve,
        z['land_bottom']-z['bottom'], z['land_top']-z['bottom'])
    raw_relief = cylinder_row(native_raw_rows, funnel.bore_relief_id-2*mandrel.finishing_reserve,
        z['lead_top']-z['bottom'], z['land_bottom']-z['bottom']-mandrel.finishing_reserve)
    finished_land = cylinder_row(native_finished_rows, funnel.sealing_id,
        z['land_bottom']-z['bottom'], z['land_top']-z['bottom'])
    finished_relief = cylinder_row(native_finished_rows, funnel.bore_relief_id,
        z['lead_top']-z['bottom'], z['land_bottom']-z['bottom'])
    assert raw_relief['length_mm'] > 2*0.08
    raw_outside = raw.cut(finished).Volume()
    assert raw_outside < EPS
    wet_slab = mandrel.slab(z['end']-z['bottom'], z['neck']-z['bottom'])
    wet_faces = [face.intersect(wet_slab) for face in finished.Faces()
                 if face.BoundingBox().zmin < z['neck']-z['bottom']
                 and face.BoundingBox().zmax > z['end']-z['bottom']]
    wet_boundary = cq.Compound.makeCompound(wet_faces)
    wet_gap = wet_boundary.distance(raw)
    assert wet_gap >= mandrel.finishing_reserve-EPS, wet_gap
    mask_checks = {}
    for label, bottom, top in [('socket_pilot', 0, mandrel.socket_bare_length),
        ('dry_shank', z['neck']+mandrel.dry_bare_start_from_neck-z['bottom'], mandrel.length)]:
        mask_checks[label] = matched(zone(raw, bottom, top), zone(finished, bottom, top))
    mesh = trimesh.load(models/'forming-mandrel.stl', force='mesh', process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1

    nominal_fit = {name: {'overlap_mm3': tool.intersect(shapes[name]).Volume(),
                          'minimum_distance_mm': tool.distance(shapes[name])}
                   for name in ('cavity', 'core')}
    assert all(abs(reading['overlap_mm3']) < EPS for reading in nominal_fit.values())
    poses = []
    neck_mould = z['neck']+shift
    end_mould = z['end']+shift
    x, y = funnel.neck_dx, funnel.neck_dy
    bottom_mould = z['bottom']+shift
    for azimuth in range(0, 360, 45):
        angle = math.radians(azimuth)
        dx, dy = math.cos(angle), math.sin(angle)
        for tilt in (-mandrel.tilt_allowance, 0, mandrel.tilt_allowance):
            for lift in (0, mandrel.axial_allowance/2, mandrel.axial_allowance):
                misplaced = tool.rotate((x, y, bottom_mould),
                    (x-dy, y+dx, bottom_mould), tilt).translate(
                    (mandrel.lateral_allowance*dx, mandrel.lateral_allowance*dy, 0))
                floor_lift = bottom_mould-misplaced.BoundingBox().zmin
                misplaced = misplaced.translate((0, 0, floor_lift+lift))
                overlaps = {name: misplaced.intersect(shapes[name]).Volume()
                            for name in ('cavity', 'core')}
                assert all(abs(v) < EPS for v in overlaps.values()), (azimuth, tilt, lift, overlaps)
                bottom_face = min(misplaced.Faces(), key=lambda face: face.Center().z)
                poses.append({'azimuth_deg': azimuth, 'tilt_deg': tilt,
                    'floor_contact_lift_mm': floor_lift, 'additional_lift_mm': lift,
                    'cavity_overlap_mm3': overlaps['cavity'],
                    'core_overlap_mm3': overlaps['core'],
                    'cavity_gap_mm': misplaced.distance(shapes['cavity']),
                    'core_gap_mm': misplaced.distance(shapes['core']),
                    'whole_pilot_end_depth_mm': end_mould-bottom_face.BoundingBox().zmax})
    assert len(poses) == 72
    assert min(row['whole_pilot_end_depth_mm'] for row in poses) > 0
    core_withdrawal = []
    silicone_withdrawal = []
    for travel in (0, 0.5, 1, 2, 3, 5, 10, 20, design['rod_support']['engagement_mm'], mandrel.length):
        moved = tool.translate((0, 0, -travel))
        core_overlap = moved.intersect(shapes['core']).Volume()
        offset_overlap = moved.translate((mandrel.lateral_allowance, 0, 0)).intersect(shapes['core']).Volume()
        assert abs(core_overlap) < EPS and abs(offset_overlap) < EPS
        core_withdrawal.append({'travel_mm': travel, 'core_overlap_mm3': core_overlap,
                                'with_screened_lateral_offset_overlap_mm3': offset_overlap})
        silicone_withdrawal.append({'travel_mm': travel,
                                    'rigid_silicone_overlap_mm3': moved.intersect(shapes['funnel']).Volume()})
    assert max(row['rigid_silicone_overlap_mm3'] for row in silicone_withdrawal) > 1
    # The finished tool's entry is outside the casting once pulled downward;
    # the upper shank is the largest surface passing through its sealing land.
    assert funnel.bore_lead_id > mandrel.dry_shank_diameter > funnel.sealing_id

    paths = ['cavity.step', 'cavity.stl', 'core.step', 'core.stl', 'rod.step',
             'funnel.step', 'assembly.step', 'design.json', 'forming_mandrel.py', 'funnel_mold.py',
             'forming-mandrel.step', 'forming-mandrel.stl', 'forming-mandrel-finished.step',
             'forming-mandrel-design.json']
    result = {
        'checked_utc': datetime.now(timezone.utc).isoformat(),
        'method': 'Complete native BREP booleans, independent source-envelope casting, exact axial cylinder trims, whole wet-boundary normal reserve and all combined socket positioning poses.',
        'sha256': {name: sha(models/name) for name in paths},
        'review_source_sha256': sha(Path(__file__)),
        'finished_funnel_native_step_sha256': sha(native_funnel_path),
        'source_funnel_sha256': sha(ROOT/'hardware/printed-parts/zone-c/funnel/funnel.py'),
        'native_shells_bound_to_design': True, 'native_shell_sha256': shell_hashes,
        'native_bodies': body_readings, 'complete_csg_bindings': bindings,
        'finished_casting_volume_ml': shapes['funnel'].Volume()/1000,
        'funnel_to_mould_z_translation_mm': shift,
        'print_to_mould_translation_mm': list(tool_translation),
        'recommended_local_layer_phase': {
            'fine_band_print_z_mm': tool_info['recommended_fine_band_print_z_mm'],
            'fine_layer_height_mm': tool_info['recommended_fine_layer_height_mm'],
            'pilot_alignment_layer': tool_info['recommended_pilot_alignment_layer']},
        'whole_casting_scope': 'All current native funnel walls, ramp, brim, collar, rectangular block and complete staged bore; complete CSG comparison, not an axial section alone.',
        'raw_stock': {'valid_solid': True, 'raw_outside_finished_reference_mm3': raw_outside,
            'minimum_solid_land_diameter_mm': raw_land['diameter_mm'],
            'raw_relief': raw_relief, 'raw_land': raw_land,
            'minimum_wet_boundary_to_raw_mm': wet_gap,
            'bare_interface_complete_csg': mask_checks,
            'mesh': {'triangles': len(mesh.faces), 'watertight': True,
                     'winding_consistent': True, 'bodies': 1}},
        'finished_wet_reference': {'land': finished_land, 'relief': finished_relief,
            'profile': tool_info['finished_profile'],
            'scope': 'Measured finished target; the raw print and a coating thickness assumption alone do not establish this finished profile.'},
        'nominal_native_fit': nominal_fit,
        'combined_positioning_screen': {'poses': 72,
            'lateral_offset_mm': mandrel.lateral_allowance,
            'tilt_deg': mandrel.tilt_allowance, 'maximum_additional_axial_lift_mm': mandrel.axial_allowance,
            'maximum_cavity_overlap_mm3': max(abs(row['cavity_overlap_mm3']) for row in poses),
            'maximum_core_overlap_mm3': max(abs(row['core_overlap_mm3']) for row in poses),
            'minimum_core_gap_mm': min(row['core_gap_mm'] for row in poses),
            'minimum_cavity_gap_mm': min(row['cavity_gap_mm'] for row in poses),
            'minimum_whole_pilot_end_depth_mm': min(row['whole_pilot_end_depth_mm'] for row in poses),
            'readings': poses,
            'scope': 'Both loose blind seats, lower floor contact, upper roof clearance and pilot reach. Does not qualify a deliberately displaced wet forming profile or actual printed fit.'},
        'seat_and_closure_motion': seat_motion(shapes, z, shift),
        'demould': {'core_withdrawal': core_withdrawal,
            'rigid_silicone_withdrawal_readings': silicone_withdrawal,
            'required_land_diametric_expansion_percent': 100*(mandrel.dry_shank_diameter/funnel.sealing_id-1),
            'sequence': ['Lift the core in +Z off the floor-supported pin.',
                         'Peel the funnel and mandrel together from the open cavity.',
                         'Trim upper-seat flash at the bowl throat and lower-pilot flash flush with the block bottom without entering the sealing land.',
                         'Withdraw the mandrel in -Z using the silicone sealing land\'s elastic expansion.'],
            'physical_release_force_qualified': False,
            'scope': 'Core removal clears geometrically. Mandrel withdrawal intentionally uses silicone flexibility; no rigid-clearance or release-force claim.'},
        'static_head_load_screen': mandrel.load_screen(),
        'geometry_forms_complete_finished_funnel': True,
        'physical_casting_qualified': False,
        'physical_limits': ['Coating compatibility and adhesion', 'Measured finished wet profile',
                            'Measured loose seat fit and nominal alignment',
                            'Coated closure and vacuum cycle', 'Silicone-assisted withdrawal and release force',
                            'Finished casting quality and installed seal']}
    print(json.dumps({key: result[key] for key in ('native_shells_bound_to_design',
          'finished_casting_volume_ml', 'geometry_forms_complete_finished_funnel')}, indent=2), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, default=MODELS)
    parser.add_argument('--shell-baseline', type=Path)
    parser.add_argument('--output', type=Path, default=MODELS/'forming-mandrel-check.json')
    args = parser.parse_args()
    result = review(args.models, args.shell_baseline)
    args.output.write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
