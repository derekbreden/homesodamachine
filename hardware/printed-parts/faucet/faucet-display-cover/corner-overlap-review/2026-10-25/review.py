"""Manual cover-only front-corner study against the physically accepted head."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import base64
import gzip
import hashlib
import importlib.util
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
FAUCET = ROOT / 'hardware/printed-parts/faucet'
ACCEPTED = FAUCET / 'faucet-display-cover/fit-review/2026-10-24'
sys.path[:0] = [str(FAUCET / 'faucet-shell'), str(ROOT / 'hardware/faucet-layout')]
import faucet_shell as shell
import faucet_assembly as assembly

FRONT_RIM_N = 10.5


def load_cover():
    source = FAUCET / 'faucet-display-cover/faucet_display_cover.py'
    spec = importlib.util.spec_from_file_location('corner_study_cover', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def intersection_volume(a, b):
    return a.intersect(b).Volume() if a.Solids() and b.Solids() else 0.


def sightline_reading(before, after):
    origin, along, normal = shell._tip_frame()
    def point(x, s, n):
        return origin + cq.Vector(x, 0, 0) + along.multiply(s) + normal.multiply(n)
    rows = []
    for side in (-1, 1):
        for s in [2.1, 2.5, 3., 3.5, 4., 5.]:
            for n in [8.2, 8.7, 9.2, 9.7, 10.2, 10.7]:
                ray = cq.Edge.makeLine(point(side * 10, s, n), point(side * 25, s, n))
                rows.append({'side': side, 's_mm': s, 'n_mm': n,
                    'accepted_cover_stock_on_ray_mm': sum(e.Length() for e in ray.intersect(before).Edges()),
                    'proposed_cover_stock_on_ray_mm': sum(e.Length() for e in ray.intersect(after).Edges())})
    exposed = [r for r in rows if r['accepted_cover_stock_on_ray_mm'] < 1e-6]
    return {'method': 'Lateral rays between X=+/-10 and +/-25 mm at selected stations above the N8.1 ledge. Measures cover occlusion only, not every viewing angle.',
            'sampled_rays': len(rows), 'accepted_cover_unblocked_rays': len(exposed),
            'proposed_cover_unblocked_rays': sum(r['proposed_cover_stock_on_ray_mm'] < 1e-6 for r in rows),
            'minimum_cover_stock_on_newly_blocked_rays_mm': min(r['proposed_cover_stock_on_ray_mm'] for r in exposed),
            'rays': rows}


def main():
    origin, along, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))
    raw_clearance = shell.build_display_neck_clearance
    original_face, original_top = shell.display_face_n, shell.display_cover_top_n
    settings = {'display_feet_n': 7.1, 'display_floor_n': 7.1,
                'display_face_n': original_face - 4.5 + .5,
                'display_cover_top_n': original_top - 4.5 + .5}
    tip = cq.importers.importStep(str(ACCEPTED / 'corrected-tip.step')).val()
    accepted_cover = cq.importers.importStep(str(ACCEPTED / 'correctedSculpted.step')).val()
    with ExitStack() as stack:
        for key, value in settings.items():
            stack.enter_context(patch.object(shell, key, value))
        stack.enter_context(patch.object(shell, 'build_display_neck_clearance',
            lambda: raw_clearance().translate(normal.multiply(.5).toTuple())))
        cover = load_cover()
        before = cover.build_seated_display_cover().val()
        before_print = cover.build_display_cover().val()
        before_lips = cover.build_display_cover_lips().val()
        cover.front_rim_n = FRONT_RIM_N
        after = cover.build_seated_display_cover().val()
        after_print = cover.build_display_cover().val()
        after_lips = cover.build_display_cover_lips().val()
        display = assembly.build_display_body().val()
        screen = assembly.build_display_screen().val()
        buttons = assembly._seat_on_tip(assembly.build_display_buttons_native()).val()
        bezel_region = shell._cradle_prism(40, -1, 60, cover.bezel_n_bottom, 30).val()
        lip_region = shell._cradle_prism(40, shell.display_clip_s_bottom,
            shell.display_clip_s_top, shell.display_clip_bottom_n,
            shell.display_clip_top_n).val()
    added = after.cut(before)
    removed = before.cut(after)
    print_added = after_print.cut(before_print)
    report = {
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'status': 'unprinted_cover_only_proposal',
        'accepted_printer_task_id': '1372253517',
        'source_sha256': {name: hashlib.sha256((ACCEPTED / name).read_bytes()).hexdigest()
                          for name in ['corrected-tip.step', 'correctedSculpted.step',
                                       'corrected-sculpted-cover.stl']},
        'front_edge': {'equation': 'N = intercept - 1.8 * S',
                       'accepted_intercept_n_mm': 14.,
                       'proposed_intercept_n_mm': FRONT_RIM_N,
                       'normal_extension_mm': 14. - FRONT_RIM_N,
                       'pocket_front_station_s_mm': shell.dispense_face_thickness,
                       'accepted_edge_n_at_pocket_front_mm': 14. - 1.8 * shell.dispense_face_thickness,
                       'proposed_edge_n_at_pocket_front_mm': FRONT_RIM_N - 1.8 * shell.dispense_face_thickness,
                       'tip_ledge_n_mm': 8.1,
                       'nominal_projected_overlap_at_pocket_front_mm': 8.1 - (FRONT_RIM_N - 1.8 * shell.dispense_face_thickness)},
        'accepted_baseline_symmetric_difference_mm3': before.cut(accepted_cover).Volume() + accepted_cover.cut(before).Volume(),
        'added_seated_stock_mm3': added.Volume(),
        'removed_seated_stock_mm3': removed.Volume(),
        'valid_single_seated_solid': after.isValid() and len(after.Solids()) == 1,
        'valid_single_printable_solid': after_print.isValid() and len(after_print.Solids()) == 1,
        'cover_to_tip_intersection_mm3': after.intersect(tip).Volume(),
        'cover_to_display_intersection_mm3': after.intersect(display).Volume(),
        'cover_to_screen_intersection_mm3': after.intersect(screen).Volume(),
        'cover_to_vendor_switches_intersection_mm3': after.intersect(buttons).Volume(),
        'added_stock_to_switches_minimum_distance_mm': added.distance(buttons),
        'bezel_region_added_or_removed_stock_mm3': intersection_volume(added, bezel_region) + intersection_volume(removed, bezel_region),
        'retaining_lip_region_added_or_removed_stock_mm3': intersection_volume(added, lip_region) + intersection_volume(removed, lip_region),
        'lip_builder_symmetric_difference_mm3': before_lips.cut(after_lips).Volume() + after_lips.cut(before_lips).Volume(),
        'retained': {'display_foot_floor_n_mm': 7.1, 'surrounding_tip_ledge_n_mm': 8.1,
                     'display_inward_reduction_mm': 4.5, 'glass_gap_mm': .6,
                     'arch_crown_clearance_mm': .65, 'bezel_thickness_mm': 1.3,
                     'lip_bottom_top_n_mm': [3.3, 6.3], 'radial_lip_engagement_mm': 1.2,
                     'preload_at_lip_top_mm': 1.25},
        'scope': 'The front skirt extends across the corner sightline while the existing circular neck clearance and inner cavity trim it away from the accepted hardware. CAD overlap in side projection is not a liquid seal or a physical fit trial.'}
    for name, shape in [('accepted-cover', before), ('proposed-cover', after),
                        ('proposed-cover-print', after_print), ('added-stock', added)]:
        cq.exporters.export(shape, str(HERE / (name + '.step')))
    cq.exporters.export(after_print, str(HERE / 'proposed-cover.stl'), tolerance=.005, angularTolerance=.1)
    report['candidate_sha256'] = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
                                  for name in ['proposed-cover.step', 'proposed-cover-print.step', 'proposed-cover.stl']}
    report['lateral_sightline_reading'] = sightline_reading(before, after)
    crop = shell._cradle_prism(23, -1, 53, -7, 26).val()
    shapes = {'tip': tip.intersect(crop), 'beforeCover': before, 'afterCover': after,
              'addedStock': added, 'display': display, 'screen': screen,
              'printCover': after_print, 'printAddedStock': print_added}
    meshes = {}
    for name, shape in shapes.items():
        vertices, faces = shape.moved(frame.inverse).tessellate(.055, .18)
        positions = np.asarray([[v.x, v.z, -v.y] for v in vertices], dtype='<f4')
        indices = np.asarray(faces, dtype='<u4')
        meshes[name] = {'p': base64.b64encode(gzip.compress(positions.tobytes(), mtime=0)).decode(),
                        'i': base64.b64encode(gzip.compress(indices.tobytes(), mtime=0)).decode(),
                        'triangles': len(faces)}
    (HERE / 'native-review.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'viewer-data.json').write_text(json.dumps({'meshes': meshes}, separators=(',', ':')))
    print(json.dumps(report, indent=2), flush=True)
    print('Viewer bytes:', (HERE / 'viewer-data.json').stat().st_size, flush=True)


if __name__ == '__main__':
    main()
