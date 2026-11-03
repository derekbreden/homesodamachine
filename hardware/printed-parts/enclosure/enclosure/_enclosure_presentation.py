"""The enclosure's printed viewer surfaces, from packed mesh arrays."""
import json
from pathlib import Path
import struct

import numpy as np


def write_payload(meshes, path, *, src=None, cut=None):
    from _mesh_payload import aligned_face_sources
    entries, blob = [], bytearray()
    for mesh in meshes:
        entry = {key: mesh[key] for key in ('name', 'color')}
        for key, dtype in (('pos','<f4'), ('nrm','<f4'), ('idx','<u4'), ('fac','<u4')):
            array = np.ascontiguousarray(np.asarray(mesh[key]).reshape(-1), dtype=dtype)
            entry[key] = [len(blob), array.size]
            blob += array.tobytes()
        if 'face_sources' in mesh:
            sources = aligned_face_sources(mesh['face_sources'],
                                           len(np.asarray(mesh['fac']).reshape(-1))//2)
            if sources is not None:
                entry['face_sources'] = sources
        entries.append(entry)
    header = {'v':3, 'meshes':entries}
    if src is not None:
        header['src'] = src
    if cut is not None:
        header['cut'] = cut
    text = json.dumps(header, separators=(',', ':')).encode()
    text += b' '*(-(len(text)+4)%4)
    with open(path, 'wb') as target:
        target.write(struct.pack('<I',len(text)))
        target.write(text)
        target.write(blob)


def print_payload(step, printed):
    """Pair the printed surface with the Rust producer's immutable fine model."""
    import _mesh_payload
    import flute_payload
    from _assembly_model import identity

    step = Path(step)
    model = step.with_name(step.name+'.npz')
    (name, color), = identity(model)
    printed = printed.copy()
    printed.merge_vertices()
    lineage = flute_payload.print_lineage(step.with_suffix('.stl'), printed)
    bound = flute_payload.deflection(printed)
    reduced, deviation = flute_payload.simplify_within(printed, bound, lineage=lineage)
    pos, nrm, idx, fac = flute_payload.creased(reduced, lineage=lineage)
    mesh = dict(name=name, color=color, pos=pos, nrm=nrm, idx=idx, fac=fac)
    if lineage is not None:
        mesh['face_sources'] = lineage['face_sources']
    elif step.stem == 'enclosure-front-top':
        mesh['face_sources'] = [[None] for _ in range(len(fac)//2)]
    target = step.with_name(step.name+'.mesh')
    write_payload([mesh], target, src=_mesh_payload.source_digest(model),
                  cut={'dev':round(float(deviation),4), 'bound':round(float(bound),4)})
    print(f'-> {target.name}  {len(printed.faces)} -> {len(reduced.faces)} facets, '
          f'{deviation:.3f} mm inside a {bound:.3f} mm budget')
