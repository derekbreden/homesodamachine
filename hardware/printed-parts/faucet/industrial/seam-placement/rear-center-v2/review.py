"""Manual native seam review against complete model outlines; never sends a job.

Usage: review.py archive.gcode.3mf project.print.json output-directory
Reads all base, tip and plate exterior-wall runs, including tilted transitions,
small contour components, arc moves, scarf starts and overlap ends. The saved
STL is sliced in the exact build pose to distinguish external from hole walls.
"""
from pathlib import Path
import argparse, csv, hashlib, json, runpy
from collections import defaultdict

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').is_file())
reader = runpy.run_path(str(HERE.parent / 'rear-center-v1/review.py'))
PART_NAMES = {'industrial-shell-base', 'faucet-shell-tip', 'industrial-above-counter-plate'}


def cover_ray_distances(points):
    """Geometric coverage of tip starts by the assembled display cover."""
    paths = runpy.run_path(str(HERE.parents[2] / 'faucet_paths.py'))
    center = np.array([paths['WATER_Y'] - paths['WATER_RADIUS'], paths['ARC_START_Z']])
    radius = paths['WATER_RADIUS'] + paths['SHELL_CENTER_N']
    mesh = trimesh.load(HERE.parents[1] / 'industrial-display-cover.stl', force='mesh', process=False)
    triangles = mesh.triangles
    edge1, edge2 = triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0]
    answer = []
    for point in points:
        yz = point[1:] - center
        angle = float(np.degrees(np.arctan2(yz[1], yz[0])))
        yz /= np.linalg.norm(yz)
        axis = np.r_[0, center + radius * yz]
        direction = point - axis
        direction /= np.linalg.norm(direction)
        h = np.cross(direction, edge2)
        a = np.einsum('ij,ij->i', edge1, h)
        valid = abs(a) > 1e-9
        f = np.zeros(len(a)); f[valid] = 1 / a[valid]
        s = point - triangles[:, 0]
        u = f * np.einsum('ij,ij->i', s, h)
        q = np.cross(s, edge1)
        v = f * (q @ direction)
        distance = f * np.einsum('ij,ij->i', edge2, q)
        hit = valid & (u >= -1e-8) & (v >= -1e-8) & (u + v <= 1 + 1e-8) & (distance > 0)
        answer.append((angle, float(distance[hit].min()) if hit.any() else None))
    return answer


def section_outlines(shape, z, low, high):
    faces = np.flatnonzero((low <= z) & (high >= z))
    segments = trimesh.intersections.mesh_plane(
        shape, [0, 0, 1], [0, 0, z], local_faces=faces,
        cached_dots=shape.vertices[:, 2] - z)
    if not len(segments):
        return []
    # Merge the numerical differences at shared STL edge intersections.
    collection = shapely.polygonize(shapely.linestrings(np.round(segments[:, :, :2], 5)))
    polygons = [Polygon(p.exterior) for p in collection.geoms if p.area > 1e-6]
    # The outside boundary of every disconnected footprint, excluding holes.
    return [p for p in polygons if not any(
        q.area > p.area and q.contains(p.representative_point()) for q in polygons)]


def rear_point(polygon, x):
    cross = polygon.exterior.intersection(LineString([(x, -10000), (x, 10000)]))
    if cross.is_empty:
        return None
    parts = list(cross.geoms) if hasattr(cross, 'geoms') else [cross]
    points = []
    for part in parts:
        if isinstance(part, Point):
            points.append([part.x, part.y])
        elif hasattr(part, 'coords'):
            points.extend(list(part.coords))
    return np.array(max(points, key=lambda p: p[1])) if points else None


def analyze(archive, report):
    parts = [p for p in report['parts'] if p['name'] in PART_NAMES]
    runs, gcode_sha = reader['read_runs'](archive, [int(p['identify_id']) for p in parts])
    by_part = defaultdict(list)
    for run in runs:
        by_part[run['object']].append(run)
    output = {}
    all_rows = []
    for part in parts:
        group = by_part[int(part['identify_id'])]
        rotation = np.array(part['build_transform'][:9]).reshape(3, 3)
        translation = np.array(part['plate_translation_mm'])
        center = np.array(part['source_center_mm'])
        to_cad = lambda pts: (pts - translation) @ rotation.T + center
        source = ROOT / part['source']
        shape = trimesh.load(source, force='mesh', process=False)
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        if source_hash != part['stl_sha256']:
            raise ValueError(f"Source mesh for {part['name']} differs from the identified print")
        shape.vertices = (shape.vertices - center) @ rotation + translation
        low = shape.triangles[:, :, 2].min(axis=1)
        high = shape.triangles[:, :, 2].max(axis=1)
        by_layer = defaultdict(list)
        for run in group:
            by_layer[run['layer']].append(run)
        rows = []
        unclassified = []
        internal = 0
        components = 0
        for z, layer_runs in sorted(by_layer.items()):
            outlines = section_outlines(shape, z, low, high)
            rear_y = max((p.bounds[3] for p in outlines), default=None)
            components += len(outlines)
            for run in layer_runs:
                pts = run['points']
                line = LineString(pts[:, :2])
                positions = np.linspace(0, line.length, max(3, int(line.length / .6) + 1))
                samples = shapely.line_interpolate_point(line, positions)
                matches = [(float(np.mean(shapely.distance(samples, p.exterior) <= .75)), p)
                           for p in outlines]
                if not matches:
                    unclassified.append({'print_z_mm': z, 'gcode_line': run['line'],
                                         'reason': 'No closed STL outside boundary reconstructed'})
                    continue
                fraction, outline = max(matches, key=lambda pair: pair[0])
                if fraction < .8:
                    internal += 1
                    continue
                reference = rear_point(outline, translation[0] - center[0])
                central = reference is not None
                rear_available = central and outline.bounds[3] - reference[1] <= .75
                main_rear = rear_available and rear_y - outline.bounds[3] <= .75
                if reference is None:
                    # A small disconnected pedestal or lip has its own center.
                    reference = rear_point(outline, (outline.bounds[0] + outline.bounds[2]) / 2)
                cad = to_cad(pts)
                reference_cad = to_cad(np.r_[reference, z]) if reference is not None else None
                lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
                full = np.flatnonzero(pts[:, 2] >= z - 1e-4)
                ramp_end = int(full[0]) if len(full) else len(pts) - 1
                scarf = run['z_range'] > .02
                # The repeat returns to the XY start after one complete lap.
                returns = np.flatnonzero((np.linalg.norm(pts[:, :2] - pts[0, :2], axis=1) < .10)
                                         & (lengths > max(5., outline.length * .65)))
                first_lap = int(returns[0]) if scarf and len(returns) else None
                turn = run['seam_angle']
                rear_in_run = reference is not None and line.distance(Point(reference)) <= .75
                terminal = (not scarf and run['length'] < 4 and run['gap'] > .95 * run['length'])
                row = {
                    'part': part['name'], 'print_z_mm': z,
                    'gcode_start_line': run['line'], 'gcode_end_line': run['end_line'],
                    'start_plate_mm': pts[0].tolist(), 'start_cad_mm': cad[0].tolist(),
                    'end_cad_mm': cad[-1].tolist(),
                    'reference_rear_cad_mm': reference_cad.tolist() if reference_cad is not None else None,
                    'component_intersects_assembly_centerline': central,
                    'rear_center_surface_available': bool(rear_available),
                    'main_rear_component': bool(main_rear),
                    'run_passes_rear_reference': bool(rear_in_run),
                    'open_terminal_trace': bool(terminal),
                    'start_lateral_offset_mm': float(cad[0, 0] - reference_cad[0]) if reference_cad is not None else None,
                    'start_distance_from_stl_rear_mm': float(np.linalg.norm(pts[0, :2] - reference)) if reference is not None else None,
                    'outside_boundary_fraction': fraction,
                    'scarf': scarf, 'scarf_height_rise_mm': run['z_range'],
                    'ramp_length_mm': float(lengths[ramp_end]) if scarf else 0.,
                    'ramp_end_cad_mm': cad[ramp_end].tolist() if scarf else None,
                    'ramp_end_line': run['point_lines'][ramp_end] if scarf else None,
                    'repeat_tail_length_mm': float(lengths[-1] - lengths[first_lap]) if first_lap is not None else None,
                    'tail_end_distance_from_ramp_end_mm': float(np.linalg.norm(pts[-1, :2] - pts[ramp_end, :2])) if scarf else None,
                    'seam_corner_angle_deg': turn,
                    'length_mm': run['length'], 'area_mm2': run['area'],
                    'numerical_connectors_joined': run['numerical_connectors'],
                    'component_width_mm': outline.bounds[2] - outline.bounds[0],
                }
                rows.append(row)
        if part['name'] == 'faucet-shell-tip':
            coverage = cover_ray_distances(np.array([r['start_cad_mm'] for r in rows]))
            paths = runpy.run_path(str(HERE.parents[2] / 'faucet_paths.py'))
            arc_center = np.array([paths['WATER_Y'] - paths['WATER_RADIUS'], paths['ARC_START_Z']])
            outer_arc_radius = paths['WATER_RADIUS'] + paths['SHELL_CENTER_N'] + paths['SHELL_RADIUS']
            for row, (angle, distance) in zip(rows, coverage):
                row['arc_angle_deg'] = angle
                row['assembled_cover_outward_ray_distance_mm'] = distance
                row['concealed_joint_plug'] = angle < 70
                ref = row['reference_rear_cad_mm']
                row['reference_on_curved_outer_arc'] = bool(ref is not None
                    and abs(np.linalg.norm(np.array(ref[1:]) - arc_center) - outer_arc_radius) <= .15)
        for row in rows:
            exposed = True
            if part['name'] == 'faucet-shell-tip':
                exposed = (not row['concealed_joint_plug']
                           and row['reference_on_curved_outer_arc']
                           and row['assembled_cover_outward_ray_distance_mm'] is None)
            elif part['name'] == 'industrial-above-counter-plate':
                exposed = row['component_width_mm'] > 55
            row['exposed_rear_seam_goal'] = bool(exposed and row['main_rear_component']
                and row['run_passes_rear_reference'] and not row['open_terminal_trace'])
        central_rows = [r for r in rows if r['exposed_rear_seam_goal']
                        and r['run_passes_rear_reference'] and not r['open_terminal_trace']]
        curved = [r for r in central_rows if r['scarf']]
        peak = max(curved, key=lambda r: abs(r['start_lateral_offset_mm'])) if curved else None
        bands = []
        if part['name'] == 'industrial-shell-base':
            for name, start, stop in [('foot', 0, 14), ('body', 14, 55), ('lower neck transition', 55, 80),
                                      ('upper neck', 80, 237.4)]:
                band = [r for r in central_rows if start <= r['start_cad_mm'][2] < stop]
                witness = max(band, key=lambda r: abs(r['start_lateral_offset_mm'])) if band else None
                bands.append({'name': name, 'cad_z_interval_mm': [start, stop], 'runs': len(band),
                              'maximum_lateral_start_offset_mm': abs(witness['start_lateral_offset_mm']) if witness else None,
                              'witness': witness})
        output[part['name']] = {
            'source': part['source'], 'source_sha256': source_hash,
            'all_wall_runs_read': len(group), 'native_model_layers_read': len(by_layer),
            'stl_external_components_read': components, 'external_runs': len(rows),
            'hole_or_interior_runs': internal, 'unclassified_runs': unclassified,
            'central_external_runs': len(central_rows), 'scarf_external_runs': len(curved),
            'exposed_rear_start_maximum_lateral_offset_mm': max((abs(r['start_lateral_offset_mm']) for r in central_rows), default=None),
            'scarf_maximum_lateral_start_offset_mm': abs(peak['start_lateral_offset_mm']) if peak else None,
            'scarf_peak_witness': peak, 'bands': bands,
        }
        all_rows.extend(rows)
        print(part['name'], json.dumps({k: output[part['name']][k] for k in
            ('all_wall_runs_read', 'external_runs', 'hole_or_interior_runs', 'scarf_maximum_lateral_start_offset_mm')}), flush=True)
    return {
        'schema': 2, 'archive': str(archive.resolve().relative_to(ROOT)),
        'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
        'gcode_sha256': gcode_sha,
        'method': 'Every emitted Outer wall/Overhang wall run is compared with every STL external footprint component in its exact build pose. Arc motions and <=0.02 mm zero-E scarf connectors are followed. No CAD height cutoff and no largest-area-only selection. Rear references follow each sliced outline as its center moves; starts, full-height ramp ends and overlap tails are converted to assembly coordinates.',
        'scope': 'Commanded paths and geometric classification; this does not establish physical seam invisibility. All external runs are retained. Rear-goal statistics cover the complete base main rear silhouette, the tip curved outer-arc rear meridian and the plate outer rim. They exclude detached front shoulder islands, off-center plate pedestals, open terminal traces, the concealed tip plug and the display-frame/dispense-terminal contours. Cover rays establish interception along the recorded normal-plane direction; a missed ray does not prove visibility.',
        'parts': output, 'runs': all_rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('report', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = analyze(args.archive, json.loads(args.report.read_text()))
    result['project_report'] = str(args.report.resolve().relative_to(ROOT))
    (args.output / 'trace.json').write_text(json.dumps(result, indent=2) + '\n')
    with (args.output / 'seams.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['part', 'print_z_mm', 'gcode_start_line', 'gcode_end_line',
                         'start_cad_x', 'start_cad_y', 'start_cad_z',
                         'end_cad_x', 'end_cad_y', 'end_cad_z', 'scarf',
                         'start_lateral_offset_mm', 'repeat_tail_length_mm'])
        for row in result['runs']:
            writer.writerow([row[k] for k in ('part', 'print_z_mm', 'gcode_start_line', 'gcode_end_line')]
                            + row['start_cad_mm'] + row['end_cad_mm']
                            + [row[k] for k in ('scarf', 'start_lateral_offset_mm', 'repeat_tail_length_mm')])


if __name__ == '__main__':
    main()
