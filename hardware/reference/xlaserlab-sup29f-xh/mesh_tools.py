"""Closed mesh operations with a checked binary-STL round trip."""
import numpy as np
import trimesh
import manifold3d as md


def stl_ready(mesh, tolerance=.0001):
    """Remove sub-resolution CSG slivers before the STL vertex merge."""
    solid = md.Manifold(md.Mesh(np.asarray(mesh.vertices, dtype=np.float32),
                               np.asarray(mesh.faces, dtype=np.uint32)))
    if solid.status() != md.Error.NoError:
        raise ValueError(f'Manifold rejected input: {solid.status()}')
    cleaned = solid.simplify(tolerance).to_mesh()
    result = trimesh.Trimesh(cleaned.vert_properties, cleaned.tri_verts,
                             process=True)
    if not result.is_volume:
        raise ValueError('Mesh is not a closed, consistently oriented volume')
    return result


def reflected_volume(mesh):
    """Retain Y >= 0 and weld its reflection into a single exterior."""
    box = trimesh.creation.box([500., 150., 500.])
    box.apply_translation([0., 75., 0.])
    half = trimesh.boolean.intersection([mesh, box], engine='manifold')
    other = half.copy()
    other.apply_transform(np.diag([1., -1., 1., 1.]))
    return trimesh.boolean.union([half, other], engine='manifold')


def checked_stl(mesh, path):
    mesh = stl_ready(mesh)
    mesh.export(path)
    loaded = trimesh.load_mesh(path)
    if not loaded.is_volume or len(loaded.split()) != 1:
        raise ValueError(f'STL round trip failed: {path}')
    return loaded
