"""Prepare only the frozen front-top's one exterior and enclosed RC62 void.

The generic writer's default single-component gate remains unchanged. This
scoped writer accepts the independently validated inward-wound sealed cavity;
every other geometry and archive check remains in the original writer.
"""
from pathlib import Path
import hashlib
import inspect
import json
import shutil

import manifold3d as md
import numpy as np
import trimesh

import prepare_prints as preparation

SOURCE = preparation.ENC / 'enclosure-front-top.stl'
FROZEN_STL_SHA = 'cc2cfd8a490b52439d957aa082b0e4369c5602076740494298b3a954f0ba36ba'
VALIDATION = None


def one_front_top_material(mesh, source):
    global VALIDATION
    assert Path(source) == SOURCE and preparation.sha(source) == FROZEN_STL_SHA
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.is_volume
    components = mesh.split(only_watertight=False)
    assert len(components) == 2 and all(c.is_watertight and c.is_winding_consistent for c in components)
    positive = [c for c in components if c.volume > 0]
    negative = [c for c in components if c.volume < 0]
    assert len(positive) == 1 and len(negative) == 1
    outer, cavity = positive[0], negative[0]
    pocket = json.loads((preparation.ENC / 'magnet-retention/geometry-check.json').read_text())['pieces']['front-top']
    px, _ = pocket['axis_xz_mm']; radius = pocket['pocket_radius_mm']
    y0, y1 = pocket['pocket_y_mm']
    expected = np.array([[px-radius, y0, pocket['seat_floor_z_mm']],
                         [px+radius, y1, pocket['roof_z_mm']]])
    assert np.allclose(cavity.bounds, expected, atol=1e-5, rtol=0), (cavity.bounds, expected)
    def manifold(part):
        result = md.Manifold(md.Mesh(vert_properties=np.asarray(part.vertices, dtype=np.float32),
                                     tri_verts=np.asarray(part.faces, dtype=np.uint32)))
        assert result.status() == md.Error.NoError
        return result
    void = cavity.copy(); void.invert()
    outer_volume, void_volume = manifold(outer), manifold(void)
    outside = (void_volume-outer_volume).volume()
    assert abs(outside) < 1e-5, outside
    entire = manifold(mesh)
    assert entire.volume() > 0 and np.isclose(entire.volume(), outer_volume.volume()-void_volume.volume(), atol=.001, rtol=0)
    VALIDATION = dict(source_stl_sha256=FROZEN_STL_SHA, watertight=True, winding_consistent=True,
                      connected_closed_shell_components=2, positive_material_body_count=1,
                      enclosed_inward_cavity_count=1, cavity_bounds_mm=cavity.bounds.tolist(),
                      total_material_volume_mm3=mesh.volume, outer_volume_mm3=outer.volume,
                      cavity_signed_volume_mm3=cavity.volume, cavity_outside_positive_mm3=outside,
                      manifold_status=str(entire.status()),
                      scope='Exactly this frozen front-top: one closed exterior and the fully contained sealed RC62 pocket. No automatic mesh repair or disconnected positive material is accepted.')
    return True


def main():
    # Derive a process-local writer with one explicit validation predicate.
    # The shared source file and all frozen source/native geometry stay intact.
    original = inspect.getsource(preparation.writer.refresh)
    expression = 'mesh.body_count != 1'
    assert original.count(expression) == 1
    scoped = original.replace(expression, 'not one_front_top_material(mesh, source_path)')
    namespace = dict(preparation.writer.refresh.__globals__)
    namespace['one_front_top_material'] = one_front_top_material
    exec(compile(scoped, str(Path(__file__)), 'exec'), namespace)
    preparation.writer.refresh = namespace['refresh']
    directory, project, report = preparation.prepare('front-top', .3, .5)
    assert VALIDATION is not None
    report['closed_cavity_validation'] = VALIDATION
    report['parts'][0].update(positive_material_body_count=1, connected_closed_shell_components=2)
    report['source_sha256'][str(Path(__file__).relative_to(preparation.ROOT))] = preparation.sha(__file__)
    shutil.copyfile(__file__, directory / 'inputs/scoped-front-top-preparer.py')
    report['writer_validation_scope'] = dict(original_refresh_source_sha256=hashlib.sha256(original.encode()).hexdigest(),
                                             scoped_refresh_source_sha256=hashlib.sha256(scoped.encode()).hexdigest(),
                                             replaced_predicate=expression,
                                             replacement='not one_front_top_material(mesh, source_path)')
    (directory / 'preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    preparation.slice_prepared(directory, project, report)


if __name__ == '__main__':
    main()
