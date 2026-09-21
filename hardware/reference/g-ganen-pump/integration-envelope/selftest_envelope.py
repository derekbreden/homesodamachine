"""Synthetic checks of outward containment and the convex-source guard."""
import cadquery as cq
import numpy as np

from derive_envelope import (convex_native_proof, outer_polytope,
                             native_polytope, surface_mesh, BOUND_MM)
import trimesh


def check_source(shape):
    points, hull, _ = convex_native_proof(shape)
    planes, outer, _ = outer_polytope(points, hull)
    reduced = native_polytope(outer, planes)
    vertices, _, _ = convex_native_proof(reduced)
    assert (points @ planes[:, :3].T+planes[:, 3]).max() < 1e-7
    _, distances, _ = trimesh.proximity.closest_point(surface_mesh(points, hull), vertices)
    assert distances.max() <= BOUND_MM


def run():
    check_source(cq.Solid.makeBox(36., 8., 2.).rotate((0, 0, 0), (1, 2, 3), 23.))
    sphere = np.array([[np.cos(a)*np.sin(b), np.sin(a)*np.sin(b), np.cos(b)]
                       for a in np.linspace(0, 2*np.pi, 24, endpoint=False)
                       for b in np.linspace(.08, np.pi-.08, 14)])*6.
    from scipy.spatial import ConvexHull
    hull = ConvexHull(sphere)
    native = native_polytope(sphere, hull.equations)
    check_source(native)
    concave = cq.Solid.makeBox(10, 10, 10).cut(cq.Solid.makeBox(6, 6, 6, cq.Vector(5, 5, 5)))
    try:
        convex_native_proof(concave)
    except ValueError:
        pass
    else:
        raise AssertionError('Concave source was accepted as convex')
    print('Containment, maximum outward distance, rotated thin prism and concavity rejection pass.')


if __name__ == '__main__':
    run()
