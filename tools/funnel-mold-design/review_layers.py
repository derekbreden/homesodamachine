"""Check that every model section grows from material in the previous layer.

Run after publication. Sections use the layer heights in the delivered G-code.
This checks for floating model islands; it does not predict bed adhesion or
surface finish. It supplements the explicit V-roof angle in cut_channels.py.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile

import numpy as np
import trimesh
from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union


def material_polygons(section):
    """Polygonize the section lines, retaining the material by even/odd crossing."""
    paths = [section.vertices[e.points] for e in section.entities]
    edges = np.concatenate([np.stack([p[:-1], p[1:]], axis=1) for p in paths])
    a, b = edges[:, 0], edges[:, 1]
    result = []
    for polygon in polygonize(unary_union([LineString(p) for p in paths])):
        point = polygon.representative_point()
        crosses = (a[:, 1] > point.y) != (b[:, 1] > point.y)
        start, end = a[crosses], b[crosses]
        x = start[:, 0]+(point.y-start[:, 1])*(end[:, 0]-start[:, 0])/(end[:, 1]-start[:, 1])
        if np.count_nonzero(x > point.x) % 2 and polygon.area > 0.01:
            result.append(polygon)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--project', required=True)
    args = parser.parse_args()
    project = args.models/args.project
    report = {'project': args.project, 'project_sha256': hashlib.sha256(project.read_bytes()).hexdigest(),
              'minimum_section_area_mm2': 0.01, 'parts': {}}
    with zipfile.ZipFile(project) as archive:
        for index, name in enumerate(('cavity', 'core'), 1):
            data = archive.read(f'Metadata/plate_{index}.gcode').decode()
            layers = [(float(z), float(h)) for z, h in re.findall(
                r'; Z_HEIGHT: ([0-9.]+)\r?\n; LAYER_HEIGHT: ([0-9.]+)', data)]
            assert layers and all(h > 0 for z, h in layers)
            path = args.models/(name+'.stl')
            mesh = trimesh.load(path, force='mesh', process=True)
            if name == 'core':
                mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi, [1, 0, 0]))
            mesh.apply_translation([0, 0, -mesh.bounds[0, 2]])
            sections = mesh.section_multiplane([0, 0, 0], [0, 0, 1],
                                               [z-h/2 for z, h in layers])
            previous, roots, orphan = None, None, []
            for (z, height), section in zip(layers, sections):
                assert section is not None, (name, z, 'empty section')
                polygons = material_polygons(section)
                assert polygons and all(p.is_valid for p in polygons), (name, z)
                if previous is None:
                    roots = len(polygons)
                else:
                    for polygon in polygons:
                        if polygon.intersection(previous).area < 1e-6:
                            orphan.append({'z_mm': z, 'area_mm2': polygon.area})
                previous = unary_union(polygons)
            report['parts'][name] = {'stl_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'layers_checked': len(layers), 'bed_contact_regions': roots,
                'floating_section_components': orphan}
            print(name, len(layers), 'layers;', roots, 'bed regions;', len(orphan), 'floating components', flush=True)
            assert not orphan, (name, orphan)
    (args.models/'layer-review.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
