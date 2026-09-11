"""Extract a full-height corner from the current solid cavity for a print trial.

The output directory holds its STEP, STL and dimensions. Use prepare_print.py
with --models pointing there and --only cavity; the cavity's layer bands and
the same saved printer, filament and process presets apply.
"""
import argparse
import hashlib
import json
from pathlib import Path

import cadquery as cq
import trimesh


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    source = args.models/'cavity.step'
    body = cq.importers.importStep(str(source)).val()
    clip = cq.Solid.makeBox(200, 200, 100, cq.Vector(-240, -240, -1))
    corner = body.intersect(clip).clean()
    assert corner.isValid() and len(corner.Solids()) == 1
    assert abs(corner.BoundingBox().zlen-body.BoundingBox().zlen) < 1e-5
    args.output.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(corner, str(args.output/'cavity.step'))
    stl = args.output/'cavity.stl'
    cq.exporters.export(corner, str(stl), tolerance=0.02, angularTolerance=0.08)
    mesh = trimesh.load(stl, force='mesh', process=True)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    mesh.export(stl)
    info = json.loads((args.models/'design.json').read_text())
    # Imported trimmed surfaces can have loose B-rep bounds. The printed mesh
    # supplies the specimen's measured envelope.
    dimensions = mesh.extents.tolist()
    info['dimensions_mm']['cavity'] = dimensions
    info['volume_ml']['cavity'] = corner.Volume()/1000
    info['corner_trial'] = {
        'source_step_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'section': 'X <= -40 mm and Y <= -40 mm in the cavity assembly frame',
        'full_height_mm': dimensions[2],
        'scope': 'Full-height corner geometry and extrusion trial; whole-mold thermal loading is not reproduced.'}
    (args.output/'design.json').write_text(json.dumps(info, indent=2)+'\n')
    print(' x '.join(f'{d:.1f}' for d in dimensions)+f' mm; {corner.Volume()/1000:.1f} mL')


if __name__ == '__main__':
    main()
