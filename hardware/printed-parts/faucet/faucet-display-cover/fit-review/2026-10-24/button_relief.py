"""Manual lowered-tip fit correction, using the two complete vendor switches."""
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
import base64
import gzip
import hashlib
import json
import sys

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
FAUCET = ROOT / 'hardware/printed-parts/faucet'
sys.path[:0] = [str(FAUCET / 'faucet-shell'), str(ROOT / 'hardware/faucet-layout')]
import faucet_shell as shell
import faucet_assembly as assembly

SEAT_N = 8.1
FEET_N = 7.1
BUTTON_SIDE_CLEARANCE = .5
BUTTON_RECESS_DEPTH = 1.


def main():
    source = FAUCET / 'industrial/display-seat-review/2026-10-24/candidate-tip.step'
    before = cq.importers.importStep(str(source)).val()
    origin, along, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))
    native_buttons = assembly.build_display_buttons_native().val()
    bounds = [b.BoundingBox() for b in native_buttons.Solids()]
    pockets = []
    rows = []
    for button, b in zip(native_buttons.Solids(), bounds):
        x0, x1 = b.xmin - BUTTON_SIDE_CLEARANCE, b.xmax + BUTTON_SIDE_CLEARANCE
        s0 = shell._display_housing_center_s + b.ymin - BUTTON_SIDE_CLEARANCE
        s1 = shell._display_housing_center_s + b.ymax + BUTTON_SIDE_CLEARANCE
        pocket = cq.Solid.makeBox(x1 - x0, s1 - s0, 25 - FEET_N,
                                  cq.Vector(x0, s0, FEET_N))
        pockets.append(pocket)
        rows.append({'native_switch_bounds_mm': [[b.xmin, b.ymin, b.zmin],
                                                 [b.xmax, b.ymax, b.zmax]],
                     'pocket_bounds_x_s_n_mm': [[x0, s0, FEET_N], [x1, s1, SEAT_N]],
                     'pocket_width_length_mm': [x1 - x0, s1 - s0],
                     'nominal_ledge_interference_mm': SEAT_N - (FEET_N + b.zmin),
                     'nominal_floor_clearance_mm': FEET_N + b.zmin - FEET_N})
    cuts = shell._display_world(cq.Workplane(obj=cq.Compound.makeCompound(pockets))).val()
    after = before.cut(cuts, tol=1e-6)
    if not after.isValid() or len(after.Solids()) != 1:
        raise ValueError('Corrected tip must be one valid solid')
    with ExitStack() as stack:
        stack.enter_context(patch.object(shell, 'display_floor_n', FEET_N))
        stack.enter_context(patch.object(shell, 'display_feet_n', FEET_N))
        buttons = assembly._seat_on_tip(cq.Workplane(obj=native_buttons)).val()
        display = assembly.build_display_body().val()
        screen = assembly.build_display_screen().val()
    before_hits = [b.intersect(before) for b in buttons.Solids()]
    after_hits = [b.intersect(after) for b in buttons.Solids()]
    for row, b, hit0, hit1 in zip(rows, buttons.Solids(), before_hits, after_hits):
        row.update(actual_switch_before_intersection_mm3=hit0.Volume(),
                   actual_switch_after_intersection_mm3=hit1.Volume(),
                   actual_switch_after_tip_minimum_distance_mm=b.distance(after))
    # Preserve the four accepted foot-pocket bearing floors exactly.
    floors = []
    for x, s in shell.display_foot_centers:
        station = shell._cradle_prism(1.9, s - 1.9, s + 1.9, FEET_N - .1, FEET_N + .1)
        station = station.translate((x, 0, 0)).val()
        a, b = before.intersect(station), after.intersect(station)
        floors.append(a.cut(b).Volume() + b.cut(a).Volume())
    groove_region = shell._cradle_prism(25, -1, 53, 3.3, 6.78).val()
    groove_change = before.cut(after).intersect(groove_region).Volume()
    report = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
              'status': 'Corrected tip and cover candidate; no printer submission',
              'source_tip_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
              'buttons': rows,
              'button_side_clearance_mm': BUTTON_SIDE_CLEARANCE,
              'local_recess_depth_below_surrounding_seat_mm': BUTTON_RECESS_DEPTH,
              'surrounding_seat_n_mm': SEAT_N,
              'button_pocket_floor_n_mm': FEET_N,
              'retained_foot_floor_n_mm': FEET_N,
              'retained_display_drop_mm': 4.5,
              'foot_bearing_region_material_differences_mm3': floors,
              'snap_region_removed_material_mm3': groove_change,
              'tip_valid_single_solid': after.isValid() and len(after.Solids()) == 1,
              'removed_tip_stock_mm3': before.Volume() - after.Volume(),
              'scope': 'Vendor switch geometry matches the published source hash. The photo identifies a bearing conflict; its exact dimensions and elastic installation force are not measured. Button relief and cover reach are separate corrections.'}
    for name, part in [('corrected-tip', after), ('button-interference', cq.Compound.makeCompound(
        [s for hit in before_hits for s in hit.Solids()]))]:
        cq.exporters.export(part, str(HERE / (name + '.step')))
    cq.exporters.export(after, str(HERE / 'corrected-tip.stl'), tolerance=.005, angularTolerance=.1)
    (HERE / 'button-review.json').write_text(json.dumps(report, indent=2) + '\n')
    # Native meshes for the before/after review; no invented physical deformation.
    crop = shell._cradle_prism(23, -1, 53, -8, 25).val()
    shapes = {'beforeTip': before.intersect(crop), 'afterTip': after.intersect(crop),
              'display': display.cut(buttons), 'buttons': buttons, 'screen': screen,
              'removedStock': before.cut(after),
              'buttonCollision': cq.Compound.makeCompound([s for h in before_hits for s in h.Solids()]),
              'beforeCover': cq.importers.importStep(str(HERE / 'printedSculpted.step')).val(),
              'afterCover': cq.importers.importStep(str(HERE / 'correctedSculpted.step')).val(),
              'industrialCover': cq.importers.importStep(str(HERE / 'industrial.step')).val()}
    floors = [f for f in after.Faces() if f.geomType() == 'PLANE'
              and abs((f.Center() - origin).dot(normal) - FEET_N) < 1e-5
              and 7.4 < (f.Center() - origin).dot(along) < 13.1]
    shapes['pocketFloors'] = cq.Compound.makeCompound(floors)
    meshes = {}
    for name, part in shapes.items():
        local = part.moved(frame.inverse)
        if local.Faces():
            v, f = local.tessellate(.055, .18)
        else:
            v, f = [], []
        p = np.asarray([[a.x, a.z, -a.y] for a in v], dtype='<f4')
        idx = np.asarray(f, dtype='<u4')
        meshes[name] = {'p': base64.b64encode(gzip.compress(p.tobytes(), mtime=0)).decode(),
                        'i': base64.b64encode(gzip.compress(idx.tobytes(), mtime=0)).decode(), 'triangles': len(f)}
    data = {'meshes': meshes, 'buttons': report,
            'cover': json.loads((HERE / 'native-review.json').read_text())}
    (HERE / 'viewer-data.json').write_text(json.dumps(data, separators=(',', ':')))
    print(json.dumps(report, indent=2), flush=True)
    print('viewer bytes', (HERE / 'viewer-data.json').stat().st_size, flush=True)


if __name__ == '__main__':
    main()
