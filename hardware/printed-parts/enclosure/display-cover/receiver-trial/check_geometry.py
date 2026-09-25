"""Read the receiver coupon against the printed cover and native front-top."""

import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

import display_receiver_trial as trial

ROOT, HERE = trial.ROOT, trial.HERE
sys.path[:0] = [str(HERE.parent), str(ROOT/'hardware/printed-parts/enclosure/enclosure')]
import display_cover as cover
import enclosure as enc


def volume(shape):
    return abs(shape.Volume())


def difference(a, b):
    return volume(a.cut(b)) + volume(b.cut(a))


def main():
    assert cover.skirt_inset == trial.COVER_INSET
    body = trial.build()
    local = trial.receiver_surround()
    actual = cq.importers.importStep(str(HERE/(trial.NAME+'.step'))).val()
    assert difference(body, actual) < 1e-5
    cover_path = HERE.parent/'display-cover.step'
    printed_cover = cq.importers.importStep(str(cover_path)).val()
    assert difference(printed_cover, cover.build_display_cover().val()) < 1e-5
    outer = json.loads((ROOT/'hardware/manifold-layout/enclosure-box.json').read_text())['box']['outer']
    placement = cq.Location(enc.display_plane(outer))
    native_path = ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step'
    native = cq.importers.importStep(str(native_path)).val().moved(placement.inverse)
    protected = trial.box(-64.5, 64.5, -43, 43, -6, .01)
    for side in (-1, 1):
        protected = protected.cut(trial.side_box(side, trial.FLEX_EDGE-.01, 65,
                                   -trial.retention.RUN/2-.01, trial.retention.RUN/2+.01, -16, 1))
    unchanged_difference = difference(native.intersect(protected), local.intersect(protected))
    assert unchanged_difference < 1e-5, unchanged_difference
    readings = []
    for lateral in (-cover.cover_slip, 0, cover.cover_slip):
        seated = trial.print_pose(printed_cover.translate((lateral, 0, 0)))
        seated_intersection = volume(body.intersect(seated))
        assert seated_intersection < 1e-5, (lateral, seated_intersection)
        each = []
        for side in (-1, 1):
            skirt = cover.build_cover_skirt(side).translate((lateral, 0, 0))
            before = volume(local.intersect(skirt.translate((0, 0, trial.retention.BEARING_SLIP-.01))))
            caught = volume(local.intersect(skirt.translate((0, 0, trial.retention.BEARING_SLIP+.01))))
            assert before < 1e-5 and caught > 1e-4, (lateral, side, before, caught)
            overlap = trial.OVERLAP + side*lateral
            deflection = overlap + .1
            envelope_hits = []
            for lift in np.linspace(0, 16, 81):
                shifted = skirt.translate((-side*deflection, 0, float(lift)))
                envelope_hits.append(volume(local.intersect(shifted)))
            assert max(envelope_hits) < 1e-5, (lateral, side, max(envelope_hits))
            each.append({'side': side, 'nominal_overlap_mm': overlap,
                         'pull_049_intersection_mm3': caught,
                         'translated_skirt_insertion_clearance_check': {
                             'inward_translation_mm': deflection,
                             'maximum_intersection_mm3': max(envelope_hits),
                             'lift_range_mm': [0, 16], 'samples': 81,
                             'scope': 'Geometric clearance envelope; no bending strain or force prediction.'}})
        readings.append({'lateral_position_mm': lateral, 'seated_intersection_mm3': seated_intersection,
                         'hooks': each})
    mesh = trimesh.load_mesh(HERE/(trial.NAME+'.stl'))
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    sources = [Path(__file__).resolve(), HERE/'display_receiver_trial.py', cover_path,
               HERE.parent/'display-cover.stl', HERE.parent/'display_cover.py', native_path,
               ROOT/'hardware/printed-parts/enclosure/enclosure/_display_retention.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py']
    report = {'pass': True, 'source_sha256': {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'native_display_seat_symmetric_difference_outside_receiver_changes_mm3': unchanged_difference,
        'same_cover_geometry': True, 'cover_skirt_inset_each_mm': cover.skirt_inset,
        'catch_edge_x_mm': trial.CATCH_EDGE, 'flex_lane_edge_x_mm': trial.FLEX_EDGE,
        'ledge_thickness_mm': trial.LEDGE_THICKNESS,
        'bearing_clearance_mm': trial.retention.BEARING_SLIP,
        'seating_and_retention': readings, 'watertight': True, 'mesh_body_count': 1,
        'print_bounds_mm': mesh.bounds.tolist(), 'triangles': len(mesh.faces),
        'physical_fit_tested': False, 'physical_retention_force_measured': False}
    (HERE/'geometry-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
