"""Check model extrusion across the cavity's chute and rim wall thicknesses."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import trimesh
from shapely.geometry import LineString, box
from shapely.ops import unary_union

from profiles import qn
from review_layers import material_polygons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    path = args.models/'cavity.stl'
    mesh = trimesh.load(path, force='mesh', process=True)
    with zipfile.ZipFile(args.project) as archive:
        raw = archive.read('Metadata/plate_1.gcode')
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
        transform = list(map(float, root.find(f"{qn('build')}/{qn('item')}")
                            .get('transform').split()))
    assert transform[:9] == [1, 0, 0, 0, 1, 0, 0, 0, 1]
    offset = transform[9:12]-mesh.bounds.mean(axis=0)
    assert abs(offset[2]) < 1e-5
    targets = (55.6, 70.4, 70.8)
    x = y = z = 0.0
    width = 0.82
    feature = ''
    paths = defaultdict(list)
    counts = defaultdict(lambda: defaultdict(int))
    heights = {}
    data = raw.decode()
    body = data[data.index('; CHANGE_LAYER'):].split('; MACHINE_END_GCODE_START')[0]
    for line in body.splitlines():
        if line.startswith('; Z_HEIGHT:'):
            z = float(line.split(':')[1])
        elif line.startswith('; LAYER_HEIGHT:'):
            heights[z] = float(line.split(':')[1])
        elif line.startswith('; LINE_WIDTH:'):
            width = float(line.split(':')[1])
        elif line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
        tokens = line.partition(';')[0].split()
        if not tokens or tokens[0] not in ('G0', 'G1', 'G2', 'G3'):
            continue
        values = {t[0]: float(t[1:]) for t in tokens[1:]
                  if re.fullmatch(r'[XYE][-+]?\d*\.?\d+', t)}
        nx, ny = values.get('X', x), values.get('Y', y)
        if (z in targets and values.get('E', 0) > 0 and (nx, ny) != (x, y)
                and feature not in ('Support', 'Support interface', 'Brim', 'Skirt',
                                    'Custom', 'Flush', 'Prime tower')):
            assert tokens[0] == 'G1', 'Curved extrusion needs a curved-path reader'
            segment = [(x-offset[0], y-offset[1]), (nx-offset[0], ny-offset[1])]
            paths[z].append(LineString(segment).buffer(width/2, quad_segs=4))
            counts[z][feature] += 1
        x, y = nx, ny
    report = {
        'project': args.project.name,
        'project_sha256': hashlib.sha256(args.project.read_bytes()).hexdigest(),
        'cavity_stl_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'gcode_sha256': hashlib.sha256(raw).hexdigest(),
        'method': 'Positive model G1 segments buffered by half emitted line width; '
                  'support and brim excluded. Sections use layer midplanes; XY is '
                  'the cavity assembly frame. Nominal path coverage, not physical sealing.',
        'minimum_coverage_fraction': 0.99,
        'layers': []}
    for z in targets:
        section_z = z-heights[z]/2
        section = mesh.section_multiplane([0, 0, 0], [0, 0, 1], [section_z])[0]
        material = unary_union(material_polygons(section))
        footprint = unary_union(paths[z])
        witnesses = ([(-84.8, -79.8, 0), (79.8, 84.8, 39.75)] if z == 55.6
                     else [(-91.8, -86.8, 0), (86.8, 91.8, 0)])
        regions = []
        for x0, x1, y in witnesses:
            window = box(x0, y-1, x1, y+1)
            expected = material.intersection(window)
            covered = expected.intersection(footprint)
            assert expected.area > 9.9, (z, list(window.bounds), expected.area)
            coverage = covered.area/expected.area
            assert coverage >= report['minimum_coverage_fraction'], (z, coverage)
            regions.append({'bounds_mm': list(window.bounds),
                            'model_section_area_mm2': expected.area,
                            'extrusion_footprint_area_mm2': covered.area,
                            'coverage_fraction': coverage})
        report['layers'].append({'print_z_mm': z, 'section_z_mm': section_z,
                                'model_extrusion_segments_by_feature': dict(counts[z]),
                                'repaired_regions': regions})
        print(f'Z{z:g}: '+', '.join(format(r['coverage_fraction'], '.3%') for r in regions))
    (args.models/'repaired-wall-review.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
