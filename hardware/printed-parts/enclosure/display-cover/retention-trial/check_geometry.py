"""Read the broad cover's symmetry, root stock and engagement in its receiver."""

import hashlib
import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh

import retention_trial as trial

ROOT, HERE = trial.ROOT, trial.HERE


def volume(body):
    return abs(body.Volume())


def difference(a, b):
    return volume(a.cut(b))+volume(b.cut(a))


def main():
    names = (trial.COVER_NAME, trial.RECEIVER_NAME)
    cover, receiver = [cq.importers.importStep(str(HERE/(name+'.step'))).val()
                       for name in names]
    assert difference(cover, trial.build_cover()) < 1e-5
    assert difference(receiver, trial.build_receiver()) < 1e-5
    symmetry = {plane: difference(cover, cover.mirror(plane)) for plane in ('YZ', 'XZ')}
    assert max(symmetry.values()) < 1e-5, symmetry
    original = cq.importers.importStep(str(HERE.parent/'display-cover.step')).val()
    bezel_band = trial.box(-80, 80, -60, 60, -trial.ROOT_DEPTH, .01)
    bezel_delta = difference(cover.intersect(bezel_band), original.intersect(bezel_band))
    assert bezel_delta < 1e-5, bezel_delta
    assert trial.LIP >= 3.6 and trial.SPAN > 24
    assert trial.SPAN <= trial.SPAN_LIMIT < trial.SPAN+.5
    for side in (-1, 1):
        root_stock = trial.side_box(side, trial.SKIRT_OUTER-trial.WALL,
                                   trial.SKIRT_OUTER+trial.ROOT_EDGE_STOCK,
                                   -trial.SPAN/2, trial.SPAN/2, -trial.ROOT_DEPTH, 0)
        assert volume(root_stock.cut(cover)) < 1e-5
    glass = trial.cover.rounded_prism(trial.cover.dims.display_bezel_x,
                                      trial.cover.dims.display_bezel_slope,
                                      trial.cover.dims.display_corner_r,
                                      -trial.TIP_DEPTH-1, -trial.ROOT_DEPTH-.001)
    assert volume(cover.intersect(glass)) < 1e-5
    local = trial.receiver_surround()
    positions = []
    slip = trial.cover.cover_slip
    for lateral in (-slip, 0, slip):
        for along in (-slip, 0, slip):
            if lateral and along:
                # The rounded pocket limits diagonal travel to the same radial reveal.
                lateral_position, along_position = lateral/np.sqrt(2), along/np.sqrt(2)
            else:
                lateral_position, along_position = lateral, along
            shifted = cover.translate((lateral_position, along_position, 0))
            seated_hit = volume(local.intersect(shifted))
            assert seated_hit < 1e-5, (lateral, along, seated_hit)
            hooks = []
            for side in (-1, 1):
                leaf = trial.skirt(side).translate((lateral_position, along_position, 0))
                before = volume(local.intersect(leaf.translate((0, 0, trial.BEARING_CLEARANCE-.01))))
                caught = volume(local.intersect(leaf.translate((0, 0, trial.BEARING_CLEARANCE+.01))))
                overlap = trial.OVERLAP+side*lateral_position
                assert before < 1e-5 and abs(caught/.01-overlap*trial.SPAN) < 1e-4
                deflection = overlap+trial.INSERTION_SLIP
                hits = [volume(local.intersect(leaf.translate((-side*deflection, 0, float(lift)))))
                        for lift in np.linspace(0, trial.TIP_DEPTH+1, 45)]
                assert max(hits) < 1e-5, (side, lateral, along, max(hits))
                hooks.append({'side': side, 'overlap_mm': overlap,
                              'bearing_area_mm2': caught/.01,
                              'insertion_translation_mm': deflection,
                              'insertion_envelope_intersection_mm3': max(hits)})
            positions.append({'lateral_mm': lateral_position, 'along_mm': along_position,
                              'seated_intersection_mm3': seated_hit, 'hooks': hooks})
    meshes = {}
    for name in names:
        mesh = trimesh.load_mesh(HERE/(name+'.stl'))
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
        meshes[name] = {'watertight': True, 'one_body': True,
                        'bounds_mm': mesh.bounds.tolist(), 'triangles': len(mesh.faces)}
    paths = [Path(__file__).resolve(), HERE/'retention_trial.py',
             HERE.parent/'display_cover.py', HERE.parent/'display-cover.step',
             ROOT/'hardware/printed-parts/enclosure/enclosure/_display_retention.py',
             ROOT/'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
             ROOT/'hardware/printed-parts/enclosure/enclosure/_nameplate_interface.py']
    paths += [HERE/(name+ext) for name in names for ext in ('.step', '.stl')]
    record = {'pass': True,
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in paths},
              'hook_projection_mm': trial.LIP, 'leaf_span_mm': trial.SPAN,
              'span_limit_for_root_edge_stock_mm': trial.SPAN_LIMIT,
              'minimum_bezel_stock_outside_leaf_root_mm': trial.ROOT_EDGE_STOCK,
              'root_fillet_mm': trial.ROOT_FILLET, 'skirt_inset_each_mm': trial.INSET,
              'additional_hook_reach_mm': trial.EXTRA_REACH,
              'bearing_clearance_mm': trial.BEARING_CLEARANCE,
              'nose_depth_mm': trial.NOSE_DEPTH, 'tip_depth_mm': trial.TIP_DEPTH,
              'receiver_flex_edge_x_mm': trial.FLEX_EDGE,
              'slot_end_clearance_each_mm': trial.END_SLIP,
              'nominal_overlap_mm': trial.OVERLAP,
              'minimum_overlap_at_lateral_float_mm': trial.OVERLAP-slip,
              'nominal_bearing_area_each_mm2': trial.OVERLAP*trial.SPAN,
              'cover_symmetry_difference_mm3': symmetry,
              'visible_bezel_difference_mm3': bezel_delta,
              'seating_and_retention': positions, 'meshes': meshes,
              'scope': 'Nominal geometry and rigid insertion envelopes; physical force, bending strain and printed-surface effects remain unmeasured.'}
    (HERE/'geometry-check.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items()
                      if k not in ('source_sha256','seating_and_retention')}, indent=2))


if __name__ == '__main__':
    main()
