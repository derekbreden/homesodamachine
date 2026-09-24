"""Exclude supports on back-top's fine roof rounds, preserving the v6 mesh and settings.

Run with tools/cad-venv/bin/python. This prepares and slices offline; it never sends a job.
The source archive is identified by digest. Only triangle support annotations change.

Bambu's whole-triangle BLOCKER=2 is encoded as hexadecimal 8 (state << 2):
https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/Model.hpp
https://github.com/bambulab/BambuStudio/blob/master/src/libslic3r/TriangleSelector.cpp
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/printed-parts/petgf.3mf').is_file())
SOURCE = ROOT / '.cache/prints/2026-09-24-enclosure-back-top-h2c-v6'
OUT = ROOT / '.cache/prints/2026-09-24-enclosure-back-top-h2c-v7'
STEM = 'enclosure-back-top-black-z018-h2c-v7-unsupported-rounds'
SOURCE_SHA = 'f7f6ebf5dc5b16b0ad0577c8fbb75ef2b947d7c76eaf3792f0ee53091f4f66e1'
MEMBER = '3D/Objects/object_1.model'
CORE = '{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}'
PROD = '{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}'


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def main():
    source = SOURCE / 'enclosure-back-top-black-z018-h2c-v6-input.3mf'
    assert sha(source.read_bytes()) == SOURCE_SHA, 'source project changed'
    preparation = json.loads((SOURCE / 'preparation.json').read_text())
    for name, digest in preparation['input_sha256'].items():
        assert sha((ROOT / name).read_bytes()) == digest, f'current input changed: {name}'
    with zipfile.ZipFile(source) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
    model = ET.fromstring(members['3D/3dmodel.model'])
    items = list(model.iter(CORE + 'item'))
    components = list(model.iter(CORE + 'component'))
    assert len(items) == len(components) == 1
    assert components[0].get(PROD + 'path') == '/' + MEMBER
    assert components[0].get('transform') == '1 0 0 0 1 0 0 0 1 0 0 0'
    transform = np.array(list(map(float, items[0].get('transform').split())))
    original = members[MEMBER]
    assert b'paint_supports' not in original
    vertex_pattern = rb'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"\s*/>'
    vertices = np.fromiter((float(v) for match in re.finditer(vertex_pattern, original)
                            for v in match.groups()), dtype=float).reshape(-1, 3)
    triangle_pattern = rb'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"\s*/>'
    faces = np.fromiter((int(v) for match in re.finditer(triangle_pattern, original)
                         for v in match.groups()), dtype=np.int64).reshape(-1, 3)
    assert len(faces) == 1001638
    placed = vertices @ transform[:9].reshape(3, 3) + transform[9:]
    assert np.allclose(placed.min(axis=0), [55, 32.3500061035, 0])
    assert np.allclose(placed.max(axis=0), [270, 303.6499938965, 195])
    triangles = placed[faces]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    # CAD X remains unchanged by roof-down orientation. Both R6 roof side edges
    # lie outside |X|=101.5; the 100 mm bound includes their fluted run-outs.
    # Restrict every vertex to the fine roof band, preserving higher functional
    # faces and low internal mounts. Paint only faces looking toward the bed.
    cad_x = triangles[:, :, 0] - 162.5
    roof_band = (triangles[:, :, 2].min(axis=1) >= -1e-6) & (triangles[:, :, 2].max(axis=1) <= 9.31)
    west = (cad_x.max(axis=1) <= -100) & roof_band & (normals[:, 2] < 0)
    east = (cad_x.min(axis=1) >= 100) & roof_band & (normals[:, 2] < 0)
    selected = west | east
    assert west.any() and east.any()
    flags = iter(selected)
    def paint(match):
        return match.group(0).replace(b'/>', b'paint_supports="8" />') if next(flags) else match.group(0)
    modified = re.sub(triangle_pattern, paint, original)
    assert modified.replace(b'paint_supports="8" ', b'') == original
    members[MEMBER] = modified
    OUT.mkdir(parents=True, exist_ok=True)
    staged = OUT / (STEM + '-input.3mf')
    with zipfile.ZipFile(staged, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    report = {
        'source_project': str(source.relative_to(ROOT)), 'source_sha256': SOURCE_SHA,
        'staged_input': str(staged.relative_to(ROOT)), 'staged_sha256': sha(staged.read_bytes()),
        'source_input_sha256': preparation['input_sha256'],
        'changed_member': MEMBER, 'triangle_annotation': 'paint_supports="8"',
        'all_geometry_placement_settings_and_layer_ranges_identical': True,
        'selection': {'cad_abs_x_min_mm': 100, 'print_z_max_mm': 9.31,
                      'all_vertices_inside': True, 'normal': 'print-down'},
        'painted_triangles': {'west': int(west.sum()), 'east': int(east.sum())},
        'painted_bounds_plate_mm': {
            label: [triangles[mask].reshape(-1, 3).min(axis=0).tolist(),
                    triangles[mask].reshape(-1, 3).max(axis=0).tolist()]
            for label, mask in [('west', west), ('east', east)]},
        'printer_submission': False,
    }
    (OUT / 'preparation.json').write_text(json.dumps(report, indent=2) + '\n')
    ready = OUT / 'ready'
    ready.mkdir(exist_ok=True)
    with (ready / 'bambu-cli.log').open('w') as log:
        result = subprocess.run([
            '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '--slice', '0',
            '--arrange', '0', '--orient', '0', '--outputdir', str(ready),
            '--export-3mf', STEM + '.gcode.3mf', str(staged)],
            cwd=ready, stdout=log, stderr=subprocess.STDOUT)
    print(json.dumps(report, indent=2), flush=True)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
