#!/usr/bin/env python3
"""Check the current pump-cap/floor construction against independent scan observations.

This bounded mechanical regression uses an explicitly retained holder station and
its archived native cradle. It builds the cap and floor only, and does not claim
a fresh whole-enclosure assembly or physical clamp-load qualification.
"""
from pathlib import Path
from types import SimpleNamespace
import argparse
import hashlib
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next((p for p in HERE.parents if (p / 'tools/docgen').is_dir()), Path.cwd())
if not (ROOT / 'tools/docgen').is_dir():
    raise RuntimeError('Run the archived checker from the Home Soda Machine repository root')
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/enclosure'))
import enclosure as enc  # noqa: E402


def check(native_dir):
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    measured = json.loads((HERE / 'scan-measurements.json').read_text())
    fixture = evidence['native_contact_fixture']
    trays = fixture['pump_trays']
    box = SimpleNamespace(
        pack=SimpleNamespace(pump_trays=trays, collet_plate=fixture['collet_plate']),
        inner=fixture['inner'], pump_bay=fixture['pump_bay'])
    native_path = native_dir / 'enclosure-pump-cartridge.step'
    native_hash = hashlib.sha256(native_path.read_bytes()).hexdigest()
    expected = evidence['native_baseline']['sha256'][native_path.name]
    if native_hash != expected:
        raise ValueError('Use the archived native cradle matching the retained station fixture')
    cradle = cq.importers.importStep(str(native_path)).val()
    cap = enc.build_pump_cap(box).val()
    assert cap.isValid() and len(cap.Solids()) == 1, 'Cap must be one valid solid'
    path = []
    for dz in (-enc.cap_contact_travel, 0., .25, 5., 35., 70.):
        foul = cap.translate((0, 0, dz)).intersect(cradle).Volume()
        assert foul < 1e-5, f'Cap/cradle interference at lift {dz}: {foul} mm3'
        path.append({'lift_mm': dz, 'interference_mm3': foul})

    land = enc.pump_skirt_support_z(trays)
    contact = enc.cap_pressing_z(trays)
    base = enc.cap_base_z(trays)
    floor_bottom, floor_top = enc.bay_floor_z(trays)
    # Physical observations are independent of the case-derived nominal pump solid.
    front_height = measured['baseline_front_rim']['head_front_height_above_skirt_land_mm']['min']
    front_air = land + front_height - floor_top
    assert front_air >= enc.fits.running, f'Observed rigid front rim has only {front_air} mm floor air'
    assert floor_top - floor_bottom >= 4., 'Continuous insertion floor needs at least 4 mm stock'
    conservative_air = land - enc._tray.head_front_below_skirt - floor_top
    assert conservative_air >= enc.fits.running, 'Declared scan envelope does not clear floor'
    baseline_land = measured['native_placement']['native_cradle_bearing_z_mm']
    assert abs(land - baseline_land) < .001, 'Fitted skirt land moved in the retained station'

    rows = measured['corrected_cap_rail_observations']
    minimum_height = min(r['observed_height_above_land_mm']['min'] for r in rows)
    maximum_height = max(r['observed_height_above_land_mm']['max'] for r in rows)
    nominal_height = contact - land
    assert nominal_height - enc.cap_contact_travel < minimum_height
    assert maximum_height - nominal_height < enc.cap_contact_travel
    bridge_air = base - enc.cap_split_z(trays) - enc.cap_contact_travel
    assert bridge_air > 0., 'Bridge hard stop precedes rim contact'
    _clear, pilots = enc._cap_screws(box)
    screw_tip = enc.cap_head_seat_z(box) - enc.cap_screw_len - enc.cap_contact_travel
    tip_air = min(screw_tip - pilot.BoundingBox().zmin for pilot in pilots)
    assert tip_air >= .25 - 1e-6, 'Screw bottoms before available contact adjustment'
    raised_tip = enc.cap_head_seat_z(box) + enc.cap_contact_travel - enc.cap_screw_len
    insert_bottom = enc.cap_split_z(trays) - enc.cap_heatset_len
    assert raised_tip <= insert_bottom + 1e-6, 'Upward contact adjustment loses full insert engagement'

    rails = enc._cap_pressing_rails(trays)
    assert len(rails) == 4
    rail_footprints = []
    for rail, (cx, cy, _cz) in zip(rails, [trays[0], trays[0], trays[1], trays[1]]):
        bounds = rail.BoundingBox()
        assert abs(bounds.zmin - contact) < 1e-6
        faces = [f for f in rail.Faces()
                 if f.normalAt().z < -.99999 and abs(f.Center().z - contact) < 1e-6]
        assert len(faces) == 1 and faces[0].Area() > 90., 'Each rail needs an exposed flat bearing face'
        assert enc.PIECE_PRINT_UP['pump-cap'] * faces[0].normalAt().z > .99
        x_range = [bounds.xmin - cx, bounds.xmax - cx]
        y_range = [bounds.ymin - cy - enc.clamp_pump_y_shift,
                   bounds.ymax - cy - enc.clamp_pump_y_shift]
        side = 'xminus' if sum(x_range) < 0 else 'xplus'
        observation = next(row for row in rows if row['side'] == side)
        assert all(abs(a - b) < 1e-6 for a, b in zip(x_range, observation['bearing_frame_x_range_mm']))
        assert all(abs(a - b) < 1e-6 for a, b in zip(y_range, observation['bearing_frame_y_range_mm']))
        rail_footprints.append({'x_mm': x_range, 'y_mm': y_range, 'flat_area_mm2': faces[0].Area()})

    # The floor is one horizontal sliding lane, not a local recess that catches the head.
    floor = enc._bay_floor(fixture['inner'], fixture['y_joint'], fixture['collet_plate'], trays)
    assert floor.isValid()
    lane_checks = []
    for cx, cy, _cz in trays:
        x0, x1 = cx - 32., cx + 32.
        y0, y1 = enc.front_plane_y, cy + 33.
        above = enc._ybox(x0, x1, y0, y1, floor_top + .001, floor_top + 2.)
        below = enc._ybox(x0, x1, y0, y1, floor_top - .1, floor_top - .001)
        assert floor.intersect(above).Volume() < 1e-5, 'Head sliding corridor has a floor lip'
        filled = floor.intersect(below).Volume()
        assert abs(filled - below.Volume()) < 1e-5, 'Head corridor loses continuous floor stock'
        lane_checks.append({'x_mm': [x0, x1], 'y_mm': [y0, y1], 'flat_top_z_mm': floor_top})

    return {
        'status': 'passed_bounded_native_contact_regression',
        'scope': 'Current source cap/floor at archived holder station; full current assembly and physical fit are separate checks.',
        'native_cradle_step_sha256': native_hash,
        'measurement_record_sha256': hashlib.sha256((HERE / 'scan-measurements.json').read_bytes()).hexdigest(),
        'cap_valid': cap.isValid(), 'cap_solids': len(cap.Solids()),
        'cap_cradle_sampled_vertical_path': path,
        'land_z_mm': land, 'nominal_cap_rail_z_mm': contact,
        'observed_rim_height_above_land_min_max_mm': [minimum_height, maximum_height],
        'downward_contact_adjustment_mm': enc.cap_contact_travel,
        'bridge_clearance_at_max_closure_mm': bridge_air,
        'screw_tip_clearance_at_max_closure_mm': tip_air,
        'insert_engagement_at_max_upward_adjustment_mm': enc.cap_heatset_len,
        'floor_z_mm': [floor_bottom, floor_top],
        'minimum_floor_stock_mm': floor_top - floor_bottom,
        'minimum_air_above_floor_observed_mm': front_air,
        'minimum_air_above_floor_declared_envelope_mm': conservative_air,
        'rail_footprints': rail_footprints, 'continuous_floor_lanes': lane_checks,
        'support_access': 'Front-top floor is bed-grown. Cap prints crown-down; terminal rail bearing faces are print-up, with exposed sides and no new support-removal pocket.',
        'physical_acceptance': 'Unmeasured. Dry assembly must verify both pumps seat on skirt lands, cap removes play without bottoming, tubes capture/release, and primed operation is leak-free.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-dir', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('command', nargs='?', choices=['selftest'])
    args = parser.parse_args()
    evidence = json.loads((HERE / 'scan-evidence.json').read_text())
    native_dir = args.native_dir or Path(evidence['capture_archive']) / evidence['native_baseline']['directory']
    result = check(native_dir)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(f'PASS pump contacts: floor stock {result["minimum_floor_stock_mm"]:.3f} mm; '
          f'observed front air {result["minimum_air_above_floor_observed_mm"]:.3f} mm; '
          f'cap contact travel {result["downward_contact_adjustment_mm"]:.2f} mm; '
          'valid cap, clear native lift samples, open flat floor lanes.')


if __name__ == '__main__':
    main()
