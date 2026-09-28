"""Read the cover's seated clearance and catch engagement in the printed receiver."""

import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

import cover_reach_trial as trial

ROOT, HERE = trial.ROOT, trial.HERE
sys.path.insert(0, str(HERE.parent/'receiver-trial'))
import display_receiver_trial as receiver


def volume(shape):
    return abs(shape.Volume())


def difference(a, b):
    return volume(a.cut(b)) + volume(b.cut(a))


def check(name, extension):
    old = cq.importers.importStep(str(HERE.parent/'display-cover.step')).val()
    actual = cq.importers.importStep(str(HERE/(name+'.step'))).val()
    saved_receiver = HERE.parent/'receiver-trial/display-receiver-trial-v1.step'
    printed = cq.importers.importStep(str(saved_receiver)).val()
    assert difference(actual, trial.build(extension)) < 1e-5
    assert difference(printed, receiver.build()) < 1e-5
    bezel_box = receiver.box(-80, 80, -60, 60, -trial.cover.retention.ROOT, .01)
    bezel_difference = difference(old.intersect(bezel_box), actual.intersect(bezel_box))
    assert bezel_difference < 1e-5
    clearance = trial.cover.retention.BEARING_SLIP + extension
    local_receiver = receiver.receiver_surround()
    overlap_center = trial.cover.retention.OUTER_X-trial.INSET+trial.cover.retention.LIP-receiver.CATCH_EDGE
    readings = []
    for lateral in (-trial.cover.cover_slip, 0, trial.cover.cover_slip):
        seated = actual.translate((lateral, 0, 0))
        intersection = volume(printed.intersect(receiver.print_pose(seated)))
        assert intersection < 1e-5, (lateral, intersection)
        hooks = []
        for side in (-1, 1):
            skirt = trial.skirt(side, extension).translate((lateral, 0, 0))
            before = volume(local_receiver.intersect(skirt.translate((0, 0, clearance-.01))))
            caught = volume(local_receiver.intersect(skirt.translate((0, 0, clearance+.01))))
            assert before < 1e-5 and caught > 1e-4, (side, lateral, before, caught)
            overlap = overlap_center + side*lateral
            deflection = overlap + .1
            hits = [volume(local_receiver.intersect(skirt.translate((-side*deflection, 0, float(lift)))))
                    for lift in np.linspace(0, 18, 91)]
            assert max(hits) < 1e-5, (side, lateral, max(hits))
            hooks.append({'side': side, 'nominal_overlap_mm': overlap,
                          'intersection_before_bearing_mm3': before,
                          'intersection_after_bearing_mm3': caught,
                          'inward_translation_for_insertion_mm': deflection,
                          'maximum_insertion_envelope_intersection_mm3': max(hits)})
        readings.append({'lateral_position_mm': lateral, 'seated_intersection_mm3': intersection,
                         'hooks': hooks})
    mesh = trimesh.load_mesh(HERE/(name+'.stl'))
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    outside_gap = receiver.CATCH_EDGE-(trial.cover.retention.OUTER_X-trial.INSET)
    return {'name': name, 'pass': True, 'additional_hook_reach_mm': extension,
            'skirt_inset_each_mm': trial.INSET, 'bearing_clearance_mm': clearance,
            'bezel_symmetric_difference_mm3': bezel_difference,
            'outside_leaf_clearance_at_ledge_centered_mm': outside_gap,
            'outside_leaf_clearance_at_full_lateral_float_mm': outside_gap-trial.cover.cover_slip,
            'seating_and_retention': readings, 'insertion_lift_samples': 91,
            'watertight': True, 'mesh_body_count': 1, 'triangles': len(mesh.faces)}


def main():
    variants = [check(name, extension) for name, extension in trial.VARIANTS.items()]
    sources = [Path(__file__).resolve(), HERE/'cover_reach_trial.py',
               HERE.parent/'display_cover.py', HERE.parent/'display-cover.step',
               HERE.parent/'receiver-trial/display-receiver-trial-v1.step',
               HERE.parent/'receiver-trial/display_receiver_trial.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/_display_retention.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
               ROOT/'hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py']
    sources += [HERE/(name+suffix) for name in trial.VARIANTS for suffix in ('.step', '.stl')]
    report = {'pass': True, 'source_sha256': {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        'variants': variants,
        'scope': 'Nominal geometric clearance; no support-residue, force or strain prediction.',
        'physical_fit_tested': False, 'physical_retention_force_measured': False}
    (HERE/'geometry-check.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
