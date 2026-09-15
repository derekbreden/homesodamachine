"""Check model extrusion across the cavity's chute and rim wall thicknesses."""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh
from shapely.geometry import LineString, box
from shapely.ops import unary_union

from profiles import qn
from review_layers import material_polygons


def material_section(mesh, z):
    section = mesh.section_multiplane([0, 0, 0], [0, 0, 1], [z])[0]
    assert section is not None, z
    return unary_union(material_polygons(section))


def wall_window(material, side, y, thickness):
    line = material.intersection(LineString([(0, y), (side*1000, y)]))
    segments = list(line.geoms) if hasattr(line, 'geoms') else [line]
    segments = [segment for segment in segments if segment.geom_type == 'LineString']
    assert segments, (side, y, 'no wall section')
    segment = max(segments, key=lambda s: max(abs(s.bounds[0]), abs(s.bounds[2])))
    assert segment.length > thickness*0.99, (side, y, segment.length)
    return box(segment.bounds[0], y-1, segment.bounds[2], y+1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    args = parser.parse_args()
    path = args.models/'cavity.stl'
    info = json.loads((args.models/'design.json').read_text())
    mesh = trimesh.load(path, force='mesh', process=True)
    with zipfile.ZipFile(args.project) as archive:
        raw = archive.read('Metadata/plate_1.gcode')
        root = ET.fromstring(archive.read('3D/3dmodel.model'))
        transform = list(map(float, root.find(f"{qn('build')}/{qn('item')}")
                            .get('transform').split()))
    assert transform[:9] == [1, 0, 0, 0, 1, 0, 0, 0, 1]
    offset = transform[9:12]-mesh.bounds.mean(axis=0)
    assert abs(offset[2]) < 1e-5
    data = raw.decode()
    layers = [(float(z), float(h)) for z, h in re.findall(
        r'; Z_HEIGHT: ([0-9.]+)\r?\n; LAYER_HEIGHT: ([0-9.]+)', data)]
    heights = dict(layers)
    chute_start = info['ramp_print_z_mm']['cavity'][1]
    chute_z = min(z for z, height in layers if z-height/2 >= chute_start)
    half_brim = info['dimensions_mm']['funnel'][0]/2
    rim_outer_x = half_brim+info['finish_allowance_mm']+info['shell_thickness_mm']
    rim_vertices = mesh.vertices[
        (np.abs(np.abs(mesh.vertices[:, 0])-rim_outer_x) < 1e-4)
        & (np.abs(mesh.vertices[:, 1]) <= half_brim+1e-4)]
    assert len(rim_vertices), 'outer rim transition absent from mesh'
    rim_start = float(rim_vertices[:, 2].min())
    rim_layers = sorted(z for z, height in layers if z-height/2 < rim_start)[-2:]
    assert len(rim_layers) == 2
    targets = [chute_z, *rim_layers]
    x = y = z = 0.0
    width = 0.82
    feature = ''
    paths = defaultdict(list)
    counts = defaultdict(lambda: defaultdict(int))
    body = data[data.index('; CHANGE_LAYER'):].split('; MACHINE_END_GCODE_START')[0]
    for line in body.splitlines():
        if line.startswith('; Z_HEIGHT:'):
            z = float(line.split(':')[1])
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
        'design_sha256': hashlib.sha256((args.models/'design.json').read_bytes()).hexdigest(),
        'gcode_sha256': hashlib.sha256(raw).hexdigest(),
        'method': 'Positive model G1 segments buffered by half emitted line width; '
                  'support and brim excluded. Sections use layer midplanes; XY is '
                  'the cavity assembly frame. Nominal path coverage, not physical sealing.',
        'minimum_coverage_fraction': 0.99,
        'chute_transition_z_mm': chute_start,
        'rim_transition_z_mm': rim_start,
        'layers': []}
    for z in targets:
        section_z = z-heights[z]/2
        material = material_section(mesh, section_z)
        footprint = unary_union(paths[z])
        thickness = info['shell_thickness_mm']
        negative = wall_window(material, -1, 0, thickness)
        chute_y = (-negative.bounds[2]-info['finish_allowance_mm'])/2
        positive = wall_window(material, 1, chute_y if z == chute_z else 0, thickness)
        regions = []
        for window in (negative, positive):
            expected = material.intersection(window)
            covered = expected.intersection(footprint)
            assert expected.area > 2*thickness*0.99, (z, list(window.bounds), expected.area)
            coverage = covered.area/expected.area
            assert coverage >= report['minimum_coverage_fraction'], (z, coverage)
            regions.append({'bounds_mm': list(window.bounds),
                            'model_section_area_mm2': expected.area,
                            'extrusion_footprint_area_mm2': covered.area,
                            'coverage_fraction': coverage})
        report['layers'].append({'feature': 'chute' if z == chute_z else 'rim',
                                'print_z_mm': z, 'section_z_mm': section_z,
                                'model_extrusion_segments_by_feature': dict(counts[z]),
                                'repaired_regions': regions})
        print(f'Z{z:g}: '+', '.join(format(r['coverage_fraction'], '.3%') for r in regions))
    (args.models/'repaired-wall-review.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    main()
