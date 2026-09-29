"""Record sections of the exported print meshes, separately from native slice checks."""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/printed-parts/enclosure/tee-carrier/low-force-trial'))
import low_force_trial as trial


def main():
    directory = HERE.parent
    parts = {}
    for name in ('front-bottom', 'front-top', 'back-bottom', 'back-top',
                 'pump-cartridge', 'pump-cap'):
        step = directory / f'enclosure-{name}.step'
        stl = step.with_suffix('.stl')
        shape = cq.importers.importStep(str(step)).val()
        mesh = trimesh.load_mesh(stl)
        assert shape.isValid() and len(shape.Solids()) == 1, name
        assert mesh.is_watertight and mesh.is_winding_consistent, name
        zeros = np.where(np.linalg.norm(mesh.face_normals, axis=1) < .5)[0]
        assert not len(zeros) or float(mesh.area_faces[zeros].sum()) == 0, name
        parts[name] = {'step_sha256': hashlib.sha256(step.read_bytes()).hexdigest(),
                       'stl_sha256': hashlib.sha256(stl.read_bytes()).hexdigest(),
                       'valid_cad_solids': 1, 'cad_volume_mm3': shape.Volume(),
                       'minimum_cad_face_area_mm2': min(f.Area() for f in shape.Faces()),
                       'watertight_consistent_mesh': True,
                       'mesh_volume_mm3': mesh.volume, 'mesh_facets': len(mesh.faces),
                       'zero_normal_facets': {'count': len(zeros),
                           'total_area_mm2': float(mesh.area_faces[zeros].sum()),
                           'centres_mm': mesh.triangles_center[zeros].tolist(),
                           'vertex_spans_mm': np.ptp(mesh.triangles[zeros], axis=1).tolist()}}
        station = {'front-bottom': (190., 29.25), 'back-bottom': (220., 29.25),
                   'pump-cartridge': (42., 272.194), 'back-top': (280., 355.)}.get(name)
        if station:
            y, roof = station
            lines = trimesh.intersections.mesh_plane(mesh, [0,1,0], [0,y,0])
            a, b = lines[:,0,:], lines[:,1,:]
            rows = []
            for h in np.arange(.12, 6.001, .24):
                z = roof-h if name == 'back-top' else roof+h
                mask = ((a[:,2] <= z) & (b[:,2] > z)) | ((b[:,2] <= z) & (a[:,2] > z))
                aa, bb = a[mask], b[mask]
                xs = aa[:,0] + (bb[:,0]-aa[:,0]) * (z-aa[:,2]) / (bb[:,2]-aa[:,2])
                xs = xs[(xs > 90) & (xs < 108)]
                assert len(xs), (name, h)
                rows.append([round(float(h), 5), float(xs.max())])
            advances = [b[1]-a[1] for a,b in zip(rows, rows[1:])]
            assert max(advances) < .15, (name, max(advances))
            parts[name]['central_section'] = {'y_mm': y, 'root_z_mm': roof,
                'build_height_and_outer_x_mm': rows,
                'largest_advance_per_0_24_mm': max(advances)}
        print(name, 'valid; mesh checked', flush=True)
    # The fixed cutter represents the already printed front-top carrier opening.
    c = trial.carrier
    base, _ = trial.specifications()
    reference = c._box(-108.5,108.5,93.836,129.186,164.674,207.674).fuse(
        c._box(-108.5,108.5,106.632,128.186,164.674,224.796),
        c._box(-108.5,-98.5,93.836,129.186,164.674,224.796),
        c._box(98.5,108.5,93.836,129.186,164.674,224.796)).clean()
    actual = c.opening(base)
    delta = abs(reference.cut(actual).Volume()) + abs(actual.cut(reference).Volume())
    assert delta < 1e-6, delta
    sources = [Path(__file__), ROOT/'hardware/printed-parts/cadlib/overhang_round.py',
               directory/'enclosure.py', directory/'_swept_top.py', Path(c.__file__)]
    record = {'pass': True, 'parts': parts,
              'nominal_straight_profile_outward_per_0_24_mm': .12,
              'printed_carrier_opening_symmetric_difference_mm3': delta,
              'sample_scope': 'Central sections at four named stations. Corner returns and extrusion beads require a native slice audit; this is not that audit.',
              'physical_scope': 'Tee-carrier bottom surface accepted. Other surfaces and carrier sliding return remain unreported.',
              'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'geometry-check.json').write_text(json.dumps(record, indent=2)+'\n')


if __name__ == '__main__':
    main()
