"""Website 3D review of the actual installed nameplate and its hidden clips.

The receiver is sectioned from the production back-top STL. The separated plate
is turned around for inspection, not animated along an installation path.
Run manually through tools/run.py using tools/cad-venv/bin/python.
"""
from pathlib import Path
import hashlib
import json
import mmap
import struct

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools').is_dir())


def payload_meshes(path, include):
    """Read selected published triangles without expanding the complete machine."""
    with path.open('rb') as stream:
        raw = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        size = struct.unpack_from('<I', raw)[0]
        header = json.loads(raw[4:4+size])
        start = 4+size
        result = []
        for row in header['meshes']:
            if not include(row['name']):
                continue
            off, count = row['pos']
            vertices = np.frombuffer(raw, dtype='<f4', count=count, offset=start+off).copy().reshape(-1, 3)
            off, count = row['idx']
            faces = np.frombuffer(raw, dtype='<u4', count=count, offset=start+off).copy().reshape(-1, 3)
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
            result.append((row['name'], mesh, row.get('color', [.15, .16, .18])))
        raw.close()
    return result


def material(mesh, color):
    rgba = np.r_[np.asarray(color[:3]), 1.]
    mesh.visual = trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(
        baseColorFactor=np.round(rgba*255).astype(np.uint8), metallicFactor=0., roughnessFactor=.75,
        doubleSided=False))
    return mesh


def main():
    enclosure = HERE.parent / 'enclosure/enclosure-back-top.stl'
    plate = HERE / 'nameplate-001.step.mesh'
    installed = ROOT / 'hardware/manifold-layout/enclosure-assembly.step.mesh'
    location = json.loads((ROOT / 'hardware/manifold-layout/above-core.json').read_text())['rear_identification']['nameplate']
    centre = np.array([location['center_x_mm'], location['face_y_mm'], location['center_z_mm']])
    thick = json.loads((HERE/'nameplate.numbers.json').read_text())['thick']
    to_world = centre-[0, thick, 0]
    printed = trimesh.load_mesh(enclosure, process=True)

    def crop(low, high):
        low, high = np.asarray(low), np.asarray(high)
        box = trimesh.creation.box(extents=high-low,
            transform=trimesh.transformations.translation_matrix((low+high)/2))
        return trimesh.boolean.intersection([printed, box], engine='manifold')

    low = [centre[0]-50, 461., centre[2]-56]
    high = [centre[0]+50, 476., centre[2]+58]
    receiver = crop(low, high)
    plate_meshes = payload_meshes(plate, lambda _: True)
    records = {}
    for view in ('seated', 'separated'):
        scene = trimesh.Scene()
        mesh = receiver.copy()
        mesh.vertices = (mesh.vertices-centre)*[-1,-1,1]
        scene.add_geometry(material(mesh, [.42,.44,.47]), node_name='Production receiver cutaway')
        for name, source, color in plate_meshes:
            mesh = source.copy()
            mesh.vertices = (mesh.vertices+to_world-centre)*[-1,-1,1]
            if view == 'separated':
                mesh.vertices = mesh.vertices*[-1,-1,1]+[112,-22,0]
                # Color only actual rear clip surfaces for the inspection view.
                # Geometry and the production part's black/white materials stay intact.
                clips = source.triangles_center[:,1] < -.05
                if clips.any():
                    highlighted = mesh.submesh([np.flatnonzero(clips)],append=True,repair=False)
                    scene.add_geometry(material(highlighted,[.9,.35,.08]),
                        node_name='Hidden spring leaves (inspection highlight)')
                    mesh = mesh.submesh([np.flatnonzero(~clips)],append=True,repair=False)
            scene.add_geometry(material(mesh, color), node_name=name)
        target = HERE / f'nameplate-attachment-{view}.glb'
        target.write_bytes(scene.export(file_type='glb'))
        records[view] = str(target.relative_to(ROOT/'hardware'))
        print(target.name, flush=True)

    # Context includes the actual curved corner and complete adjacent color-chip
    # frame. The view therefore exposes the boundary whose spacing matters.
    scene = trimesh.Scene()
    context = crop([-108, 450, 160.1], [108, 477, 352])
    context.vertices = (context.vertices-centre)*[-1,-1,1]
    scene.add_geometry(material(context,[.16,.17,.19]), node_name='Enclosure back top')
    def include(name):
        return (name.split('/')[0] in ('nameplate','nameplate-ink','data-ring','keystone-jack',
            'c14-inlet','co2-inlet','bulkhead-water','bulkhead-carb','bulkhead-drain',
            'bulkhead-flavor-a','bulkhead-flavor-b') or name.startswith('bulkhead-ring-'))
    for name, mesh, color in payload_meshes(installed, include):
        mesh.vertices = (mesh.vertices-centre)*[-1,-1,1]
        scene.add_geometry(material(mesh,color), node_name=name)
    target = HERE/'nameplate-attachment-installed.glb'
    target.write_bytes(scene.export(file_type='glb'))
    records['installed'] = str(target.relative_to(ROOT/'hardware'))
    print(target.name, flush=True)
    sources = [Path(__file__), enclosure, plate, installed, HERE/'nameplate.numbers.json',
               ROOT/'hardware/manifold-layout/above-core.json']
    report = {
        'geometry': 'Actual production back-top and complete full-scale nameplate.',
        'receiver_section_world_mm': [low,high],
        'separated_pose': 'Plate translated aside and turned 180 degrees about Z to expose its back; inspection only.',
        'inspection_color': 'Orange highlights actual hidden clip surfaces in the separated view only. The printed plate is black and white.',
        'views': records,
        'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'attachment-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
