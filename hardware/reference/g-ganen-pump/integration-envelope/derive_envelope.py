"""Conservative planar reduction of the frozen G Ganen native reference.

Convex native components use an outer supporting-plane polytope. Source faces
must be planar with straight edges and form a convex solid. The maximum distance
of the outer polytope to that convex source occurs at an outer vertex, so its
native vertices give a bound for the whole solid. The casing, motor cylinder and
per-port barb profiles remain exact native copies.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

import cadquery as cq
import numpy as np
from scipy.spatial import ConvexHull, HalfspaceIntersection
import trimesh

HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent
ROOT = REFERENCE.parents[2]
CACHE = ROOT/'.cache/g-ganen-integration-envelope'
sys.path.insert(0, str(REFERENCE))
from freeze_reference import check as check_frozen_reference

BOUND_MM = .15
GUARD_MM = .00001
GEOMETRY_TOLERANCE_MM = .000002
EXACT = {'rigid_casing_envelope', 'motor_can_vent_filled_envelope',
         'port_yminus_barb_envelope', 'port_yplus_barb_envelope',
         *(name+'_observed_rubber_slider_envelope' for name in
           ('head_yminus', 'head_yplus', 'rear_yminus', 'rear_yplus'))}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(shape):
    box = shape.BoundingBox()
    return np.array([[box.xmin, box.ymin, box.zmin],
                     [box.xmax, box.ymax, box.zmax]])


def points(shape):
    return np.unique(np.round([[v.X, v.Y, v.Z] for v in shape.Vertices()], 10), axis=0)


def source_parts():
    """Identify frozen native solids by their independently recorded bounds."""
    check_frozen_reference()
    began = time.perf_counter()
    cache_path = CACHE/'source-native-cache.json'
    source_digest = digest(REFERENCE/'g-ganen-pump.step')
    if cache_path.exists():
        cache = json.loads(cache_path.read_text())
        if cache['source_sha256'] == source_digest and all(
                digest(CACHE/row['file']) == row['sha256'] for row in cache['components'].values()):
            result = {name: cq.Shape.importBrep(str(CACHE/row['file']))
                      for name, row in cache['components'].items()}
            print('identical native source cache imported', round(time.perf_counter()-began, 3), flush=True)
            return result
    imported = cq.importers.importStep(str(REFERENCE/'g-ganen-pump.step')).val()
    remaining = list(imported.Solids())
    rows = json.loads((REFERENCE/'native-validation.json').read_text())['native_solids']
    result = {}
    for row in rows:
        matches = [s for s in remaining if np.allclose(bounds(s), row['bounds_mm'], atol=1e-5, rtol=0)]
        if len(matches) != 1:
            raise ValueError('Native source component mapping is not unique: '+row['name'])
        shape = matches[0]
        if not shape.isValid() or len(shape.Faces()) != row['faces']:
            raise ValueError('Native source validity/faces differ: '+row['name'])
        result[row['name']] = shape
        remaining.remove(shape)
    if remaining:
        raise ValueError('Unmapped native source solids')
    (CACHE/'source').mkdir(parents=True, exist_ok=True)
    stored = {}
    for name, shape in result.items():
        path = CACHE/'source'/(name+'.brep')
        shape.exportBrep(str(path))
        stored[name] = {'file': str(path.relative_to(CACHE)), 'sha256': digest(path)}
    cache_path.write_text(json.dumps({'source_sha256': source_digest, 'components': stored}, indent=2)+'\n')
    print('native source imported', round(time.perf_counter()-began, 3), flush=True)
    return result


def convex_native_proof(shape):
    """A closed planar/linear B-rep whose face planes contain all its vertices."""
    vertices = points(shape)
    if any(face.geomType() != 'PLANE' for face in shape.Faces()):
        raise ValueError('Convex reduction requires planar native faces')
    if any(edge.geomType() != 'LINE' for edge in shape.Edges()):
        raise ValueError('Convex reduction requires straight native edges')
    center = vertices.mean(0)
    worst = -np.inf
    for face in shape.Faces():
        n = np.array(face.normalAt().toTuple())
        p = np.array(face.Center().toTuple())
        if np.dot(center-p, n) > 0:
            n = -n
        worst = max(worst, float(((vertices-p) @ n).max()))
    hull = ConvexHull(vertices)
    native_volume = shape.Volume()
    discrepancy = abs(hull.volume-native_volume)
    if worst > GEOMETRY_TOLERANCE_MM or discrepancy > max(1e-5, native_volume*1e-8):
        raise ValueError(f'Native source is not the asserted convex polytope: {worst}, {discrepancy}')
    return vertices, hull, {'planar_faces': len(shape.Faces()),
                            'linear_edges': len(shape.Edges()),
                            'max_native_face_halfspace_violation_mm': max(worst, 0.),
                            'native_volume_mm3': native_volume,
                            'hull_volume_discrepancy_mm3': discrepancy}


def surface_mesh(vertices, hull):
    """Exact planar source boundary triangles, with outward winding."""
    triangles = hull.simplices.copy()
    p = vertices[triangles]
    normal = np.cross(p[:, 1]-p[:, 0], p[:, 2]-p[:, 0])
    reverse = (normal*hull.equations[:, :3]).sum(1) < 0
    triangles[reverse] = triangles[reverse, ::-1]
    return trimesh.Trimesh(vertices=vertices, faces=triangles, process=False)


def initial_directions():
    directions = np.array([(x, y, z) for x in (-1, 0, 1)
                           for y in (-1, 0, 1) for z in (-1, 0, 1)
                           if (x, y, z) != (0, 0, 0)], float)
    return directions/np.linalg.norm(directions, axis=1)[:, None]


def outer_polytope(vertices, hull):
    mesh = surface_mesh(vertices, hull)
    directions = initial_directions()
    interior = vertices.mean(0)
    history = []
    for iteration in range(100):
        support = np.max(vertices @ directions.T, axis=0)
        planes = np.c_[directions, -support]
        raw = HalfspaceIntersection(planes, interior).intersections
        _, unique = np.unique(np.round(raw, 9), axis=0, return_index=True)
        outer = raw[unique]
        closest, distances, _ = trimesh.proximity.closest_point(mesh, outer)
        worst = float(distances.max())
        history.append({'planes': len(planes), 'vertices': len(outer),
                        'maximum_vertex_distance_mm': worst})
        if worst <= BOUND_MM-.001:
            expansion = GUARD_MM/np.min(support-directions @ interior)
            outer = interior+(outer-interior)*(1+expansion)
            support = directions @ interior+(support-directions @ interior)*(1+expansion)
            return np.c_[directions, -support], outer, history
        candidates = np.argsort(distances)[::-1]
        added = []
        for index in candidates:
            if distances[index] <= BOUND_MM-.001:
                break
            normal = (outer[index]-closest[index])/distances[index]
            existing = np.vstack([directions, added]) if added else directions
            if (existing @ normal).max() < 1-1e-9:
                added.append(normal)
            if len(added) == 12:
                break
        if not added:
            raise ValueError('Supporting-plane refinement stalled')
        directions = np.vstack([directions, added])
    raise ValueError('Supporting-plane refinement exceeded its bound')


def native_polytope(vertices, planes):
    """One exact native polygon per active supporting plane."""
    faces = []
    seen = []
    for equation in planes:
        if any(np.linalg.norm(equation-old) < 1e-8 for old in seen):
            continue
        seen.append(equation)
        selected = vertices[np.abs(vertices @ equation[:3]+equation[3]) < 1e-8]
        if len(selected) < 3:
            continue
        normal = equation[:3]
        selected = selected-(selected @ normal+equation[3])[:, None]*normal
        center = selected.mean(0)
        e1 = selected[np.argmax(np.linalg.norm(selected-center, axis=1))]-center
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(normal, e1)
        local = np.c_[(selected-center) @ e1, (selected-center) @ e2]
        polygon = ConvexHull(local)
        if polygon.volume < 1e-12:
            continue
        selected = selected[polygon.vertices]
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in selected], close=True)
        if len(wire.Vertices()) < 3:
            continue
        face = cq.Face.makeFromWires(wire)
        if len(face.Vertices()) >= 3 and face.Area() > 1e-9:
            faces.append(face)
    shape = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
    if not shape.isValid() or len(shape.Solids()) != 1:
        raise ValueError('Reduced native solid is invalid')
    return shape


def reduce_component(name, source):
    began = time.perf_counter()
    native_vertices, original_hull, proof = convex_native_proof(source)
    planes, outer_vertices, history = outer_polytope(native_vertices, original_hull)
    reduced = native_polytope(outer_vertices, planes)
    reduced_vertices, reduced_hull, reduced_proof = convex_native_proof(reduced)
    source_violation = float((native_vertices @ planes[:, :3].T+planes[:, 3]).max())
    reduced_violation = float((reduced_vertices @ planes[:, :3].T+planes[:, 3]).max())
    if source_violation > GEOMETRY_TOLERANCE_MM or reduced_violation > GEOMETRY_TOLERANCE_MM:
        raise ValueError('Native containment half-space check failed')
    if abs(reduced_hull.volume-ConvexHull(outer_vertices).volume) > 1e-5:
        raise ValueError('Native reduction is not the complete supporting-plane intersection')
    _, distances, _ = trimesh.proximity.closest_point(
        surface_mesh(native_vertices, original_hull), reduced_vertices)
    maximum = float(distances.max())
    if maximum > BOUND_MM+GEOMETRY_TOLERANCE_MM:
        raise ValueError('Reduced native vertices exceed the surface-distance bound')
    original_bounds, reduced_bounds = bounds(source), bounds(reduced)
    outward_extent = np.vstack([original_bounds[0]-reduced_bounds[0],
                               reduced_bounds[1]-original_bounds[1]])
    report = {'name': name, 'method': 'convex_native_outer_supporting_planes',
              'source_faces': len(source.Faces()), 'envelope_faces': len(reduced.Faces()),
              'source_native_convexity': proof, 'envelope_native_convexity': reduced_proof,
              'source_vertices_within_envelope_planes': True,
              'max_source_halfspace_violation_mm': source_violation,
              'max_envelope_halfspace_violation_mm': reduced_violation,
              'max_outward_surface_distance_mm': maximum,
              'distance_bound_method': 'Distance to a convex set is convex, so its maximum on a polytope is attained at a vertex. Every reduced native vertex was compared with the exact triangulated planar source boundary.',
              'source_bounds_mm': original_bounds.tolist(),
              'envelope_bounds_mm': reduced_bounds.tolist(),
              'added_axis_extents_mm': outward_extent.tolist(),
              'source_volume_mm3': source.Volume(), 'envelope_volume_mm3': reduced.Volume(),
              'refinement': history, 'derivation_seconds': time.perf_counter()-began}
    description = {'name': name, 'method': report['method'],
                   'vertices_mm': reduced_vertices.tolist(),
                   'support_planes': planes.tolist()}
    print(name, report['source_faces'], '->', report['envelope_faces'],
          'excess', round(maximum, 6), flush=True)
    return reduced, report, description


def run():
    frozen = digest(REFERENCE/'artifact-manifest.json')
    native_hash = digest(REFERENCE/'g-ganen-pump.step')
    tool_hash = digest(Path(__file__))
    source = source_parts()
    native = {}
    reports, descriptions = [], []
    for name, shape in source.items():
        if name in EXACT:
            native[name] = shape
            box = bounds(shape).tolist()
            reports.append({'name': name, 'method': 'exact_frozen_native_copy',
                            'source_faces': len(shape.Faces()), 'envelope_faces': len(shape.Faces()),
                            'source_bounds_mm': box, 'envelope_bounds_mm': box,
                            'max_outward_surface_distance_mm': 0.,
                            'added_axis_extents_mm': [[0., 0., 0.], [0., 0., 0.]],
                            'source_volume_mm3': shape.Volume(), 'envelope_volume_mm3': shape.Volume()})
            descriptions.append({'name': name, 'method': 'exact_frozen_native_copy'})
        else:
            native[name], report, description = reduce_component(name, shape)
            reports.append(report)
            descriptions.append(description)
    if digest(REFERENCE/'artifact-manifest.json') != frozen or digest(REFERENCE/'g-ganen-pump.step') != native_hash or digest(Path(__file__)) != tool_hash:
        raise ValueError('Frozen source changed during envelope derivation')
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = {}
    for name, shape in native.items():
        path = CACHE/(name+'.brep')
        shape.exportBrep(str(path))
        cached[name] = {'path': str(path.relative_to(ROOT)), 'sha256': digest(path)}
    data = {'schema': 1, 'part': 'G Ganen conservative integration envelope',
            'frozen_reference_manifest_sha256': frozen, 'detailed_native_sha256': native_hash,
            'tool_sha256': {'derive_envelope.py': tool_hash},
            'surface_distance_bound_mm': BOUND_MM, 'support_plane_guard_mm': GUARD_MM,
            'geometry_tolerance_mm': GEOMETRY_TOLERANCE_MM,
            'source_solids': len(source), 'source_faces': sum(len(s.Faces()) for s in source.values()),
            'envelope_solids': len(native), 'envelope_faces': sum(len(s.Faces()) for s in native.values()),
            'all_native_solids_valid': all(s.isValid() for s in native.values()),
            'native_containment_verified': True, 'source_scale_factor': 1.0,
            'measured_reference_changed': False, 'production_consumers_changed': False,
            'qualification': 'Clearance-only occupied envelope. External hulls fill hidden feet slots and clip cavities; no material mass, loaded rubber state, screw passage or hose retention is inferred.',
            'components': reports, 'derived_native_cache': cached}
    (HERE/'containment.json').write_text(json.dumps(data, indent=2)+'\n')
    (HERE/'envelope-parameters.json').write_text(json.dumps({
        'schema': 1, 'detailed_native_sha256': native_hash,
        'containment_sha256': digest(HERE/'containment.json'),
        'components': descriptions}, indent=2)+'\n')
    print('envelope complete', data['envelope_faces'], 'faces', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    run()
