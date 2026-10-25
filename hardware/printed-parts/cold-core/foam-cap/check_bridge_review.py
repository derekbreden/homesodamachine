"""Manual water-check bearing, lid backing and nominal-strip review.

Run through tmp/takeover/cadq after exporting foam-cap-lid-top.step. This
updates only feature_checks.check_bridge in above-core-native-review.json.
No generator, build or hook invokes this script. Equipment/wiring contacts
belong to the separately bound actual-appliance electrical review.
"""

import argparse
import hashlib
import importlib
import json
import math
from pathlib import Path
import sys

import cadquery as cq


HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
HW = ROOT / 'hardware'
sys.path[:0] = [str(HW / path) for path in (
    'printed-parts/cold-core', 'printed-parts/cadlib', 'scripts',
    'manifold-layout', 'reference/neofit-achv44-check',
)]
import _above_core_mounts as mounts
import _cold_core_interface as core
import above_core as layout
import fits
import neofit_achv44_check as check


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lid', type=Path,
                        default=HERE / 'foam-cap-lid-top.step')
    parser.add_argument('--output', type=Path,
                        default=HERE / 'above-core-native-review.json')
    args = parser.parse_args()
    cap_location = layout.frame_location(layout.cap_lid_pose())
    support = mounts.check_support().moved(cap_location)
    lid = cq.importers.importStep(str(args.lid)).val().moved(cap_location)
    barrel = cq.importers.importStep(str(
        HW / 'reference/neofit-achv44-check/neofit-achv44-check.step'
    )).val().moved(layout.location('discharge-chain'))
    strip = mounts.nominal_tie_strips()['water-check']
    datums = mounts.check_support_datums()
    route = mounts.check_tie_route()
    x, y, z = datums['centre_world_mm']
    lower_x, upper_x = datums['stock_x_limits_world_mm']
    first, last = datums['bearing_from_inlet_mm']
    radius = datums['fixed_band_radius_mm'] + fits.slip
    outer_radius = radius + datums['wall_mm']
    bearing = cq.Solid.makeCylinder(outer_radius, last-first,
        cq.Vector(x, datums['bearing_fore_y_mm'], z), cq.Vector(0., 1., 0.))
    bearing = bearing.cut(cq.Solid.makeCylinder(radius, last-first,
        cq.Vector(x, datums['bearing_fore_y_mm'], z), cq.Vector(0., 1., 0.)))
    bearing = bearing.intersect(cq.Solid.makeBox(
        outer_radius, last-first, outer_radius,
        cq.Vector(x, datums['bearing_fore_y_mm'], z-outer_radius)))
    face = layout.specification()['cap_face_z_mm']
    backing = cq.Solid.makeBox(upper_x-lower_x,
        datums['root_aft_y_mm']-datums['root_fore_y_mm'], datums['wall_mm'],
        cq.Vector(lower_x, datums['root_fore_y_mm'], face-datums['wall_mm']))
    checks = []

    def record(name, passed, **values):
        checks.append(dict(check=name, passed=bool(passed), **values))

    record('support valid solid', support.isValid() and len(support.Solids()) == 1,
           valid=support.isValid(), solids=len(support.Solids()))
    missing = support.cut(lid).Volume()
    record('support present in exported lid', missing < .001,
           missing_volume_mm3=missing)
    missing = bearing.cut(support).Volume()
    record('complete east-lower quarter bearing', missing < .001,
           radial_stock_mm=datums['wall_mm'], length_mm=last-first,
           missing_volume_mm3=missing)
    missing = backing.cut(lid).Volume()
    record('complete lid backing under root', missing < .001,
           thickness_mm=datums['wall_mm'], missing_volume_mm3=missing)
    for name, first_shape, second_shape in (
        ('support / purchased check', support, barrel),
        ('nominal strip / purchased check', strip, barrel),
        ('nominal strip / support', strip, support),
        ('nominal strip / exported lid', strip, lid),
    ):
        volume = first_shape.intersect(second_shape).Volume()
        record(name, volume < .001, overlap_mm3=volume)

    installation = importlib.import_module('g_ganen_installation')
    tools = {}
    for index, (hx, hy) in enumerate(installation.mount_holes()):
        point = layout.point(layout.pose('g-ganen-pump'),
            (hx, hy, installation.observed_pad_upper_z()+installation.WASHER_T+3.))
        column = cq.Solid.makeCylinder(2.5/math.sqrt(3.)+fits.slip,
                                      355.-point[2], cq.Vector(*point))
        volume = support.intersect(column).Volume()
        tools[str(index)] = {
            'axis_mm': point, 'bridge_intersection_mm3': volume,
            'check_intersection_mm3': barrel.intersect(column).Volume(),
        }
        record('pump driver / support / '+str(index), volume < .001,
               bridge_intersection_mm3=volume)
    remaining = route['stock_length_mm']-route['length_mm']
    record('nominal retaining-strip stock', remaining > 0.,
           path_length_mm=route['length_mm'], remaining_stock_mm=remaining,
           physical_head_engagement_qualified=False)
    sources = [Path(__file__), Path(mounts.__file__), Path(core.__file__),
               Path(layout.__file__), Path(check.__file__), Path(fits.__file__),
               Path(installation.__file__), HW / 'manifold-layout/above-core.json',
               HW / 'reference/neofit-achv44-check/model-dimensions.json',
               HW / 'reference/neofit-achv44-check/neofit-achv44-check.step']
    result = {
        'scope': 'Source-native east quarter bearing, complete 3 mm lid backing, '
                 'four nominal pump-driver columns and complete water-check '
                 'retaining-strip path, bound to the exported cap lid. '
                 'Separate actual-appliance records cover equipment and wiring. '
                 'No physical fit, threading, retention, pressure or life qualification.',
        'source_sha256': {str(path.relative_to(ROOT)): digest(path) for path in sources},
        'exported_lid': {'path': str(args.lid.resolve().relative_to(ROOT)),
                         'sha256': digest(args.lid)},
        'reference_basis': 'neoFit ACHV44-E vendor mesh with same-family '
                           'fixed-collar scale and receiving-depth inference; '
                           'actual part dimensions unmeasured.',
        'datums': datums,
        'geometric_minimum_loop_mm': core.cap_anchor_tie_loop('discharge-chain'),
        'nominal_strip_route': route,
        'remaining_stock_mm': remaining,
        'continuous_beam_at_notch_mm': upper_x-datums['tool_notch_max_x_mm'],
        'pump_hex_driver': {
            'across_flats_mm': 2.5, 'radial_air_mm': fits.slip,
            'assembly_scope': 'Fasten the pump before seating the removable '
                              'check group; release or disconnect that group '
                              'for the occupied screw-column service.',
            'purchased_tool_fit_and_hand_access_qualified': False,
            'axes': tools,
        },
        'checks': checks,
        'passed': all(row['passed'] for row in checks),
    }
    report = json.loads(args.output.read_text())
    report['feature_checks']['check_bridge'] = result
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
