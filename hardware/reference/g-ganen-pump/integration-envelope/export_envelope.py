"""Export proven cached native solids and verify their STEP round trip.

Unverified exports stay in the repository's .cache directory. A successful
round-trip check copies the exact STEP and bound viewer payload here.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import sys
import time

import cadquery as cq
import numpy as np

from derive_envelope import (HERE, REFERENCE, ROOT, CACHE, digest, bounds, points,
                             convex_native_proof, GEOMETRY_TOLERANCE_MM)


def run():
    containment_path = HERE/'containment.json'
    report = json.loads(containment_path.read_text())
    description = json.loads((HERE/'envelope-parameters.json').read_text())
    if description['containment_sha256'] != digest(containment_path):
        raise ValueError('Envelope parameter ledger is stale')
    for name, expected in report['tool_sha256'].items():
        if digest(HERE/name) != expected:
            raise ValueError('Envelope derivation source changed')
    if digest(REFERENCE/'g-ganen-pump.step') != report['detailed_native_sha256']:
        raise ValueError('Measured native input changed')
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in
              (containment_path, HERE/'envelope-parameters.json', Path(__file__),
               REFERENCE/'g-ganen-pump.step', REFERENCE/'artifact-manifest.json')}
    assembly = cq.Assembly(name='g-ganen-integration-envelope')
    cached = {}
    for row in report['components']:
        name = row['name']
        item = report['derived_native_cache'][name]
        path = ROOT/item['path']
        if digest(path) != item['sha256']:
            raise ValueError('Native derivation cache changed: '+name)
        shape = cq.Shape.importBrep(str(path))
        if not shape.isValid() or len(shape.Solids()) != 1:
            raise ValueError('Invalid cached native shape: '+name)
        cached[name] = shape
        color = (.18, .19, .20) if 'rubber_slider' in name else (.45, .58, .63)
        assembly.add(shape, name=name, color=cq.Color(*color))
    sys.path.insert(0, str(ROOT/'hardware/scripts'))
    from _cadq_export import export_assembly
    temporary = CACHE/'g-ganen-integration-envelope.step'
    export_assembly(assembly, temporary)
    print('candidate exported', temporary, flush=True)
    started = time.perf_counter()
    imported = cq.importers.importStep(str(temporary)).val()
    remaining = list(imported.Solids())
    readings = []
    for row, data in zip(report['components'], description['components']):
        name = row['name']
        if name != data['name']:
            raise ValueError('Envelope component order changed')
        matches = [s for s in remaining if np.allclose(bounds(s), row['envelope_bounds_mm'], atol=1e-5, rtol=0)]
        if len(matches) != 1:
            raise ValueError('Exported native component cannot be identified: '+name)
        shape = matches[0]
        remaining.remove(shape)
        if not shape.isValid() or len(shape.Faces()) != row['envelope_faces']:
            raise ValueError('Exported native validity/faces changed: '+name)
        volume_delta = abs(shape.Volume()-row['envelope_volume_mm3'])
        if volume_delta > max(1e-5, row['envelope_volume_mm3']*1e-8):
            raise ValueError('Exported native volume changed: '+name)
        vertex_delta = None
        if row['method'] == 'convex_native_outer_supporting_planes':
            vertices, hull, proof = convex_native_proof(shape)
            planes = np.asarray(data['support_planes'])
            violation = float((vertices @ planes[:, :3].T+planes[:, 3]).max())
            if violation > GEOMETRY_TOLERANCE_MM:
                raise ValueError('Exported native vertex exceeds proven halfspaces')
            from scipy.spatial import cKDTree
            vertex_delta = float(cKDTree(np.asarray(data['vertices_mm'])).query(vertices)[0].max())
            if vertex_delta > GEOMETRY_TOLERANCE_MM:
                raise ValueError('Exported native vertex moved beyond proof tolerance')
        readings.append({'name': name, 'valid': True, 'faces': len(shape.Faces()),
                         'bounds_mm': bounds(shape).tolist(),
                         'volume_roundtrip_delta_mm3': volume_delta,
                         'vertex_roundtrip_max_distance_mm': vertex_delta,
                         'method': row['method']})
    if remaining:
        raise ValueError('Unmapped native envelope solids')
    mesh = temporary.with_suffix('.step.mesh')
    with mesh.open('rb') as stream:
        header = json.loads(stream.read(struct.unpack('<I', stream.read(4))[0]))
    if header.get('v') != 3 or header.get('src') != digest(temporary):
        raise ValueError('Viewer payload does not match exported STEP')
    for name, expected in inputs.items():
        if digest(ROOT/name) != expected:
            raise ValueError('Export input changed while running: '+name)
    destination = HERE/temporary.name
    shutil.copyfile(temporary, destination)
    shutil.copyfile(mesh, HERE/mesh.name)
    result = {'schema': 1, 'status': 'native_envelope_roundtrip_pass',
              'input_sha256': inputs, 'native_sha256': digest(destination),
              'native_bytes': destination.stat().st_size,
              'viewer_payload_sha256': digest(HERE/mesh.name),
              'viewer_payload_matches_step': True,
              'native_reimport_and_checks_seconds': time.perf_counter()-started,
              'native_containment_proof': 'containment.json',
              'native_containment_sha256': digest(containment_path),
              'all_native_solids_valid': True, 'solids': len(readings),
              'faces': sum(row['faces'] for row in readings), 'components': readings}
    (HERE/'native-validation.json').write_text(json.dumps(result, indent=2)+'\n')
    print(destination, flush=True)


if __name__ == '__main__':
    run()
