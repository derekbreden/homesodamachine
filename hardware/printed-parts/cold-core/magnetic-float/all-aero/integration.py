"""Verify the shared float datums against emitted vessel CAD and sync the guide.

Upright geometry is checked over the whole translation range with bore play.
Physical sliding, expansion, immersion and directional reed switching are not
accepted by this check. Run after the float/reservoir/end-cap generators.
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/docgen').is_dir())
HW = ROOT / 'hardware'
for p in (HW/'scripts', ROOT/'tools', HERE.parents[1],
          HERE.parents[1]/'reservoir', HERE.parents[1]/'reed-bridge',
          HW/'cut-parts/carbonation/endcaps-circular', HW/'assembly'):
    sys.path.insert(0, str(p))
import _float_interface as f
import reservoir as res
import reed_bridge as bridge
import endcap_circular_dxf as cap
import _pressure_vessel_sync as pv
from _reed_channels import reed_y_center
from _cold_core_interface import bag_pocket_outermost_x, reed_x_depth
from _cadq_export import import_step
from docgen import substitute_md


def load(path):
    return import_step(str(path)).val()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    float_path = HERE/'float-aero.step'
    body = load(float_path)
    guides = {}
    inputs = [float_path, HERE/'float-aero.stl', HERE/'design.json',
              HERE.parents[1]/'_float_interface.py', HERE/'physical-observations.json',
              HW/'cut-parts/carbonation/endcaps-circular/endcap-circular-2hole.step',
              HW/'cut-parts/carbonation/endcaps-circular/endcap-circular-2hole-drawing.pdf']
    assert abs(body.BoundingBox().xlen - f.diameter) < 1e-6
    assert abs(body.BoundingBox().zlen - f.height) < 1e-6
    assert abs(cap.register_radius * 25.4 + f.rod_axis_from_inner_wall
               - cap.tube_id * 25.4 / 2) < 1e-9
    assert abs(res.rod_position_x + f.rod_axis_from_inner_wall - res.inner_far_x_abs) < 1e-9
    assert abs(reed_y_center - res.rod_position_y) < 1e-9

    # Five travel stations and nine radial offsets span the upright bounding
    # envelope. Fixed cross-section walls, sloped floor and both stops are
    # checked in the emitted body/cap B-reps, not only in duplicated dimensions.
    for side, label in ((1, 'right'), (-1, 'left')):
        vessel_path = HERE.parents[1]/'reservoir'/f'reservoir-{label}.step'
        cap_path = HERE.parents[1]/'reservoir'/f'reservoir-cap-{label}.step'
        vessel, lid = load(vessel_path), load(cap_path)
        inputs += [vessel_path, cap_path]
        max_overlap = 0.0
        min_distance = math.inf
        count = 0
        lo, hi = res.float_magnet_travel_z
        for t in (0, .25, .5, .75, 1):
            z = lo + (hi-lo)*t - f.magnet_midplane
            for angle in range(0, 360, 45):
                r = f.guide_radial_clearance
                dx, dy = r*math.cos(math.radians(angle)), r*math.sin(math.radians(angle))
                moved = body.translate((side*res.rod_position_x+dx, res.rod_position_y+dy, z))
                for solid in (vessel, lid):
                    max_overlap = max(max_overlap, moved.intersect(solid).Volume())
                    min_distance = min(min_distance, moved.distance(solid))
                count += 1
            moved = body.translate((side*res.rod_position_x, res.rod_position_y, z))
            for solid in (vessel, lid):
                max_overlap = max(max_overlap, moved.intersect(solid).Volume())
            count += 1
        assert max_overlap < 1e-6, (label, max_overlap)
        guides[label] = {'rod_axis_xy_mm': [side*res.rod_position_x, res.rod_position_y],
                         'magnet_travel_z_mm': [lo, hi], 'upright_samples': count,
                         'maximum_float_body_cap_overlap_mm3': max_overlap,
                         'minimum_body_cap_distance_mm': min_distance,
                         'end_stops': 'contact allowed at the lower/upper boss; no volume intrusion'}
    carb_reed_axis = bridge.carbonator_outer_radius + f.reed_mount_diameter/2
    reservoir_reed_axis = bag_pocket_outermost_x + reed_x_depth/2
    paths = {'carbonator': f.reed_edge_distance(cap.register_radius*25.4, carb_reed_axis),
             'reservoir': f.reed_edge_distance(res.rod_position_x, reservoir_reed_axis)}
    float_paths = {'carbonator': f.reed_float_edge_distance(cap.register_radius*25.4, carb_reed_axis),
                   'reservoir': f.reed_float_edge_distance(res.rod_position_x, reservoir_reed_axis)}
    assert all(0 < x <= f.float_edge_design_maximum for x in float_paths.values())
    assert all(abs(paths[name] - distance - f.magnet_edge_inset) < 1e-9
               for name, distance in float_paths.items())
    for z in (bridge.reed_low_z, bridge.reed_high_z):
        assert bridge.magnet_lowest_z < z < bridge.magnet_highest_z
    assert res.float_magnet_travel_z[0] < min(res.reservoir_reed_centres_z)
    assert max(res.reservoir_reed_centres_z) < res.float_magnet_travel_z[1]

    facts = {
        'FLOAT_SIZE': f'{f.diameter:g} × {f.height:g} mm',
        'FLOAT_BORE': f'{f.bore_diameter:g} mm',
        'MAGNET_CENTER': f'{f.magnet_midplane:g} mm',
        'ROD_DIAMETER': f'{f.guide_diameter:g} mm',
        'WALL_DATUM': f'{f.rod_axis_from_inner_wall:g} mm',
        'CARB_RADIUS': f'{cap.register_radius*25.4:.3f} mm',
        'CARB_RADIUS_IN': f'{cap.register_radius:.4f} in',
        'RES_X': f'{res.rod_position_x:.2f} mm', 'RES_Y': f'{res.rod_position_y:g} mm',
        'CARB_ROD_LENGTH': f'{pv.carbonator_rod_len:.2f} mm',
        'RES_ROD_LENGTH': f'{res.reservoir_rod_len:.3f} mm',
        'RES_ROD_CLEARANCE': f'{res.reservoir_rod_clearance:g} mm',
        'GUIDE_SLOP': f'{f.guide_radial_clearance:g} mm',
        'WALL_CLEARANCE': f'{f.wall_clearance:g} mm',
        'WALL_CLEARANCE_RANGE': f'{f.minimum_wall_clearance:g}–{f.maximum_wall_clearance:g} mm',
        'CARB_REED_PATH': f'{paths["carbonator"]:.3f} mm',
        'RES_REED_PATH': f'{paths["reservoir"]:.3f} mm',
        'CARB_FLOAT_REED_PATH': f'{float_paths["carbonator"]:.3f} mm',
        'RES_FLOAT_REED_PATH': f'{float_paths["reservoir"]:.3f} mm',
        'FLOAT_REED_DESIGN_MAX': f'{f.float_edge_design_maximum:g} mm',
        'FLOAT_REED_REPORTED_LIMIT': f'{f.float_edge_reported_usable_limit:g} mm',
        'CARB_WATER_LEVELS': f'{bridge.low_level_z:.3f} / {bridge.high_level_z:.3f} mm',
        'CARB_REED_CENTERS': f'{bridge.reed_low_z:.3f} / {bridge.reed_high_z:.3f} mm',
        'CARB_TRAVEL': f'{bridge.magnet_lowest_z:.3f}–{bridge.magnet_highest_z:.3f} mm',
        'RES_TRAVEL': f'{res.float_magnet_travel_z[0]:.3f}–{res.float_magnet_travel_z[1]:.3f} mm',
        'RES_REED_CENTERS': ', '.join(f'{z:.3f}' for z in res.reservoir_reed_centres_z)+' mm',
        'RES_REED_PITCH': f'{res.reservoir_reed_pitch:g} mm',
        'MAGNET_SUBMERGENCE': f'{-f.magnet_above_waterline():.3f} mm',
    }
    record = {'status': 'geometric_datums_and_upright_sweep_pass',
              'float_cad_revision': 'v2-upper-clearance', 'float_dimensions_mm': [f.diameter, f.height, f.bore_diameter],
              'rod_axis_from_inside_wall_mm': f.rod_axis_from_inner_wall,
              'carbonator_register_xy_mm': list(x*25.4 for x in cap.register_position),
              'carbonator_upright_wall_clearance_range_mm': [f.minimum_wall_clearance, f.maximum_wall_clearance],
              'reservoirs': guides, 'maximum_reed_center_to_nearest_rc62_edge_mm': paths,
              'maximum_float_edge_to_reed_center_mm': float_paths,
              'design_maximum_float_edge_to_reed_center_mm': f.float_edge_design_maximum,
              'reported_usable_float_edge_to_reed_center_mm': f.float_edge_reported_usable_limit,
              'radial_signal_evidence': f.float_edge_evidence,
              'bare_rc62_bench_reference_magnet_edge_distance_mm': f.bench_edge_distance,
              'reed_centers': 'provisional geometry; installed directional liquid calibration pending',
              'scope': 'Nominal upright CAD and horizontal bore play only; no foam expansion, tilted motion, installed switching, pressure, lifetime or wetted acceptance.',
              'files_sha256': {str(p.relative_to(ROOT)): digest(p) for p in inputs}}
    (HERE/'integration-check.json').write_text(json.dumps(record, indent=2)+'\n')
    substitute_md(HERE/'installation.md', variables=facts)
    print(json.dumps({'reservoirs': guides, 'rc62_edge_to_reed_center_mm': paths,
                      'float_edge_to_reed_center_mm': float_paths,
                      'design_maximum_float_edge_to_reed_center_mm': f.float_edge_design_maximum}, indent=2))


if __name__ == '__main__':
    main()
