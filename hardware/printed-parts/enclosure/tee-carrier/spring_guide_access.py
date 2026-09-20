#!/usr/bin/env python3
"""Read native parts to assess a fore-inserted, recessed-head carrier spring guide.

The 3 mm guide diameter is an analysis example pending the actual spring ID.
This reads existing STEP files and retained placement facts; it builds no part.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == 'hardware')
ROOT = HARDWARE.parent
FILES = {
    'front_top': 'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step',
    'cartridge': 'hardware/printed-parts/enclosure/enclosure/enclosure-pump-cartridge.step',
    'cap': 'hardware/printed-parts/enclosure/enclosure/enclosure-pump-cap.step',
    'left': 'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-left.step',
    'right': 'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-right.step',
    'facts': 'hardware/manifold-layout/enclosure-assembly.facts.json',
}
EPS = .001
GUIDE_DIAMETER = 3.0
GUIDE_PROJECTION = 19.0
TOOL_DIAMETER = 12.0
HEAD_DIAMETER = 6.0
HEAD_HEIGHT = 2.0
HEAD_RECESS = .25


def cylinder(x, z, diameter, near, far):
    return cq.Solid.makeCylinder(diameter / 2, far - near,
                                cq.Vector(x, near, z), cq.Vector(0, 1, 0))


def measure():
    inputs = {name: {'path': path,
                     'sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
              for name, path in FILES.items()}
    facts = json.loads((ROOT / FILES['facts']).read_text())
    interface = facts['box']['tee_carrier']
    parts = {name: cq.importers.importStep(str(ROOT / path)).val()
             for name, path in FILES.items() if name != 'facts'}
    result = {
        'scope': 'Geometric feasibility of a proposed guide, using existing native parts.',
        'production_guide_released': False,
        'guide_diameter_status': '3 mm is an analysis example; actual spring ID is unmeasured.',
        'input_files': inputs,
        'candidate': {'guide_diameter_mm': GUIDE_DIAMETER,
                      'guide_projection_from_fixed_spring_floor_mm': GUIDE_PROJECTION,
                      'tool_diameter_mm': TOOL_DIAMETER,
                      'head_diameter_mm': HEAD_DIAMETER,
                      'head_height_mm': HEAD_HEIGHT,
                      'head_recess_from_bay_wall_mm': HEAD_RECESS},
        'stations': [],
    }
    for side, station in zip(('left', 'right'), interface['spring_stations']):
        x, z, floor = station['x'], station['z'], station['seat_floor_y']
        ray = cq.Edge.makeLine(cq.Vector(x, -10, z), cq.Vector(x, floor - EPS, z))
        intervals = sorted((edge.BoundingBox().ymin, edge.BoundingBox().ymax)
                           for edge in parts['front_top'].intersect(ray).Edges())
        if len(intervals) != 1 or abs(intervals[0][1] - floor + EPS) > 1e-5:
            raise ValueError(f'{side}: fixed-seat wall is not one continuous stock interval: {intervals}')
        fore = intervals[0][0]
        tip = floor + GUIDE_PROJECTION
        corridor = cylinder(x, z, TOOL_DIAMETER, -10, fore - EPS)
        head = cylinder(x, z, HEAD_DIAMETER, fore + HEAD_RECESS,
                        fore + HEAD_RECESS + HEAD_HEIGHT)
        projecting_head = cylinder(x, z, HEAD_DIAMETER, fore - HEAD_HEIGHT, fore)
        guide = cylinder(x, z, GUIDE_DIAMETER, floor + EPS, tip)
        head_stock = parts['front_top'].intersect(head).Volume()
        hardware_candidates = []
        broad = (x - TOOL_DIAMETER / 2, -10, z - TOOL_DIAMETER / 2,
                 x + TOOL_DIAMETER / 2, tip, z + TOOL_DIAMETER / 2)
        for name, bounds in facts['bodies'].items():
            if name.startswith(('enclosure-', 'tee-carrier-spring-')):
                continue
            if all(broad[i] <= bounds[i + 3] and bounds[i] <= broad[i + 3] for i in range(3)):
                hardware_candidates.append(name)
        row = {
            'side': side, 'axis_xz_mm': [x, z], 'insertion_direction': [0, 1, 0],
            'bay_wall_fore_y_mm': fore, 'spring_fixed_floor_y_mm': floor,
            'wall_thickness_mm': floor - fore, 'guide_tip_y_mm': tip,
            'bay_wall_to_tip_mm': tip - fore,
            'tool_corridor_y_mm': [-10, fore - EPS],
            'tool_enclosure_overlap_mm3': parts['front_top'].intersect(corridor).Volume(),
            'tool_pump_cap_overlap_mm3': parts['cap'].intersect(corridor).Volume(),
            'purchased_hardware_bbox_candidates': hardware_candidates,
            'projecting_head_cartridge_overlap_mm3': parts['cartridge'].intersect(projecting_head).Volume(),
            'recessed_head_y_mm': [fore + HEAD_RECESS, fore + HEAD_RECESS + HEAD_HEIGHT],
            'recessed_head_fraction_in_wall_stock': head_stock / head.Volume(),
            'recessed_head_cartridge_clearance_mm': head.distance(parts['cartridge']),
            'stock_between_head_back_and_spring_floor_mm': floor - fore - HEAD_RECESS - HEAD_HEIGHT,
            'states': [],
        }
        for state in ('release', 'connected', 'aft_limit'):
            offset = interface['states'][state]['offset_y']
            body = parts[side].translate((0, offset, 0))
            row['states'].append({
                'state': state,
                'guide_carrier_overlap_mm3': guide.intersect(body).Volume(),
                'guide_carrier_distance_mm': guide.distance(body),
                'tip_to_moving_floor_mm': station['bore_floor_y'] + offset - tip,
                'guide_overlap_into_moving_bore_mm': tip - interface['spring_bore_mouth_y'] - offset,
            })
        result['stations'].append(row)
    result['finding'] = (
        'Fore installation is clear with the cartridge absent. A projecting head collides '
        'with the seated cartridge; a flush or recessed retained head preserves its clearance.')
    result['remaining_design_inputs'] = [
        'Actual spring ID determines guide diameter and radial air.',
        'The moving loading window requires a positively retained keeper.',
        'The removable head retainer and fitting allowances are not designed by these probes.',
        'The new bore and counterbore are internal fixed-wall features; no exterior hole is required.',
        'Coordinates and clearances require another reading after the production tee is integrated.',
        'Printed assembly must demonstrate insertion, head retention and smooth unequal-grip cycling.',
    ]
    for name, recorded in inputs.items():
        if hashlib.sha256((ROOT / recorded['path']).read_bytes()).hexdigest() != recorded['sha256']:
            raise ValueError(f'{name} changed during the measurement; rerun against stable native parts')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE / 'spring-guide-access.json')
    args = parser.parse_args()
    result = measure()
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(result['finding'])
    for row in result['stations']:
        print(f"{row['side']}: wall {row['wall_thickness_mm']:.3f} mm; "
              f"recessed-head cartridge air {row['recessed_head_cartridge_clearance_mm']:.3f} mm; "
              f"projecting-head interference {row['projecting_head_cartridge_overlap_mm3']:.3f} mm³")
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
