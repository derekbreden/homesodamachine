#!/usr/bin/env python3
"""Rebuild the symmetric scan reference and editable CAD exports.

The pinned reconstructed surfaces make the usual build deterministic. --remesh
recomputes them from the original cloud with screened Poisson reconstruction.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np
import trimesh
from mesh_tools import checked_stl, reflected_volume, stl_ready

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NAME = 'xlaserlab-sup29f-xh'
GRIP_ORIGIN = np.array([-64.86, 0., -20.])
GRIP_AXIS = np.array([-.4986, 0., -.8668])
WIRE_ORIGIN = np.array([68.3, 0., -34.8])
WIRE_AXIS = np.array([.792, 0., .6105])
WIRE_AXIS /= np.linalg.norm(WIRE_AXIS)


def aligned_cloud():
    a = np.load(HERE/'source/fused-scan.npz')['xyz_normals']
    frame = json.loads((HERE/'alignment.json').read_text())['native_to_model']
    basis, origin = np.array(frame['basis_rows']), np.array(frame['origin'])
    return (a[:, :3]-origin) @ basis.T, a[:, 3:] @ basis.T


def poisson(points, normals, mask):
    import pymeshlab as ml
    p, n = points[mask].copy(), normals[mask].copy()
    opposite, opposite_normals = p.copy(), n.copy()
    opposite[:, 1] *= -1
    opposite_normals[:, 1] *= -1
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertex_matrix=np.vstack([p, opposite]),
                        v_normals_matrix=np.vstack([n, opposite_normals])))
    ms.generate_surface_reconstruction_screened_poisson(
        depth=9, pointweight=8, samplespernode=2, threads=1, preclean=True)
    ms.meshing_remove_duplicate_vertices()
    ms.meshing_remove_duplicate_faces()
    ms.meshing_repair_non_manifold_edges(method=0)
    ms.meshing_close_holes(maxholesize=1000, newfaceselected=False,
                           selfintersection=True)
    mesh = trimesh.Trimesh(ms.current_mesh().vertex_matrix(),
                           ms.current_mesh().face_matrix(), process=True)
    mesh = max(mesh.split(only_watertight=False), key=lambda p: len(p.faces))
    mesh.fix_normals()
    if not mesh.is_volume:
        raise ValueError('Reconstructed surface is not closed')
    return mesh


def box(size, center):
    mesh = trimesh.creation.box(size)
    mesh.apply_translation(center)
    return mesh


def axial_box(size, origin, axis, across, offset):
    transform = np.eye(4)
    transform[:3, :3] = np.column_stack([across, [0., 1., 0.], -axis])
    transform[:3, 3] = origin + axis*offset
    mesh = trimesh.creation.box(size)
    mesh.apply_transform(transform)
    return mesh


def remesh_surfaces(points, normals):
    p = points
    t = (p-GRIP_ORIGIN) @ GRIP_AXIS
    mask = ((p[:, 0] < .35) & (p[:, 1] >= 0.) &
            ((p[:, 0] < -20.) | (p[:, 2] > -19.1)) & (t < 82.7))
    housing = poisson(p, normals, mask)
    housing = trimesh.boolean.intersection(
        [housing, box([300., 100., 200.], [-150., 0., -60.])], engine='manifold')
    across = np.array([-GRIP_AXIS[2], 0., GRIP_AXIS[0]])
    end_cap = axial_box([300., 100., 400.], GRIP_ORIGIN,
                        GRIP_AXIS, across, 82.6-200.)
    housing = trimesh.boolean.intersection([housing, end_cap], engine='manifold')
    # The unobserved front grip face follows the observed corner tangencies.
    front = axial_box([300., 100., 400.], GRIP_ORIGIN+across*169.,
                      GRIP_AXIS, across, 0.)
    lower = box([600., 200., 400.], [0., 0., -223.])
    front = trimesh.boolean.intersection([front, lower], engine='manifold')
    housing = trimesh.boolean.difference([housing, front], engine='manifold')
    housing = stl_ready(reflected_volume(housing))

    wire_t = (p-WIRE_ORIGIN) @ WIRE_AXIS
    wire_r = np.linalg.norm(np.cross(p-WIRE_ORIGIN, WIRE_AXIS), axis=1)
    mask = (((p[:, 0] > -8.) & (p[:, 0] < 71.) &
             (p[:, 2] < -20.) & (p[:, 2] > -42.)) |
            ((wire_t < -10.) & (wire_t > -140.) & (wire_r < 10.)))
    mask &= p[:, 1] >= 0.
    feed = poisson(p, normals, mask)
    for x, z, w, gap in [(15.8, -29.1, 19., 10.), (44.7, -28.6, 21., 8.)]:
        feed = trimesh.boolean.difference(
            [feed, box([w, gap, 30.], [x, 0., z])], engine='manifold')
    # Clip the flexible guide at the captured length.
    across = np.array([-WIRE_AXIS[2], 0., WIRE_AXIS[0]])
    transform = np.eye(4)
    transform[:3, :3] = np.column_stack([WIRE_AXIS, [0., 1., 0.], across])
    transform[:3, 3] = WIRE_ORIGIN+WIRE_AXIS*(-137.-150.)
    cut = trimesh.creation.box([300., 100., 300.])
    cut.apply_transform(transform)
    feed = trimesh.boolean.difference([feed, cut], engine='manifold')
    feed = stl_ready(reflected_volume(feed))
    return {'housing': housing, 'wire-feed-scan': feed}


def load_surfaces():
    a = np.load(HERE/'source/reconstructed-surfaces.npz')
    return {key[:-3]: trimesh.Trimesh(a[key], a[key[:-3]+'__f'])
            for key in a.files if key.endswith('__v')}


def assemble(output, surfaces):
    a = np.load(output/'cad-meshes.npz')
    # The detailed reference retains the scanned feeder, including its guide.
    # Its missing forward brass projection uses the editable clearance solids.
    include = {'wire-feed-front-nut', 'wire-feed-thread-envelope'}
    parts = {key[:-3]: trimesh.Trimesh(a[key], a[key[:-3]+'__f'])
             for key in a.files if key.endswith('__v') and
             key != 'housing__v' and
             (not key.startswith('wire-feed-') or key[:-3] in include)}
    parts = {**surfaces, **parts}
    for name, mesh in parts.items():
        if not mesh.is_volume:
            raise ValueError(f'Invalid component: {name}')
    mesh = trimesh.boolean.union(list(parts.values()), engine='manifold')
    mesh = checked_stl(reflected_volume(mesh), output/(NAME+'.stl'))

    scene = trimesh.Scene()
    for name, part in parts.items():
        color = ([184, 115, 51, 255] if 'copper' in name else
                 [38, 38, 40, 255] if 'boot' in name else
                 [181, 143, 84, 255] if name in include else [200, 203, 209, 255])
        part.visual = trimesh.visual.TextureVisuals(
            material=trimesh.visual.material.PBRMaterial(
                name=name, baseColorFactor=color,
                metallicFactor=0. if 'boot' in name else .55,
                roughnessFactor=.7 if 'boot' in name else .4))
        scene.add_geometry(part, node_name=name, geom_name=name)
    # glTF convention: metres, Y up. CAD/STL convention: millimetres, Z up.
    scene.apply_transform(np.array([[.001, 0, 0, 0], [0, 0, .001, 0],
                                    [0, -.001, 0, 0], [0, 0, 0, 1.]]))
    (output/(NAME+'.glb')).write_bytes(scene.export(file_type='glb'))
    record = {'units': 'mm', 'symmetry_plane': 'Y=0',
              'glb_units': 'metres, Y-up', 'watertight': bool(mesh.is_watertight),
              'winding_consistent': bool(mesh.is_winding_consistent),
              'connected_volumes': len(mesh.split()), 'triangles': len(mesh.faces),
              'bounds_mm': mesh.bounds.tolist(), 'extents_mm': mesh.extents.tolist(),
              'csg_cleanup_tolerance_mm': .0001,
              'files': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in output.iterdir() if p.suffix in ('.stl', '.step', '.glb')},
              'scope': 'Exterior reference. Printed fit and load capacity are unmeasured.'}
    (output/'mesh-check.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({key: record[key] for key in
                      ('watertight', 'connected_volumes', 'triangles', 'extents_mm')}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'output'/NAME)
    parser.add_argument('--remesh', action='store_true',
                        help='Reconstruct surfaces from the original scan (several minutes)')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(HERE/'xlaserlab_sup29f_xh.py'),
                    '--output', str(output)], check=True)
    surfaces = remesh_surfaces(*aligned_cloud()) if args.remesh else load_surfaces()
    if args.remesh:
        np.savez_compressed(output/'reconstructed-surfaces.npz',
                            **{name+'__v': mesh.vertices for name, mesh in surfaces.items()},
                            **{name+'__f': mesh.faces for name, mesh in surfaces.items()})
    assemble(output, surfaces)
    subprocess.run([sys.executable, str(HERE/'validate.py'),
                    '--output', str(output)], check=True)


if __name__ == '__main__':
    main()
