"""Website review of the four-screw nameplate on the complete enclosure.

The detail receiver is sectioned from the production back-top STL. The separate
view exposes the plate, four screws and four short inserts.
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
VIEWER = ROOT / 'hardware/assembly/scenes/glb'
READ_SHA = {}


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
            result.append((row['name'], mesh, row.get('color') or [.15, .16, .18]))
        READ_SHA[path] = hashlib.sha256(raw).hexdigest()
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
    aggregate = HERE.parent / 'enclosure/enclosure.step.mesh'
    plate = HERE / 'nameplate-001.step.mesh'
    hardware = HERE / 'nameplate-fasteners.step.mesh'
    installed = ROOT / 'hardware/manifold-layout/enclosure-assembly.step.mesh'
    plan_path = ROOT / 'hardware/manifold-layout/above-core.json'
    location = json.loads(plan_path.read_text())['rear_identification']['nameplate']
    centre = np.array([location['center_x_mm'], location['face_y_mm'], location['center_z_mm']])
    numbers = json.loads((HERE/'nameplate.numbers.json').read_text())
    to_world = centre-[0, numbers['thick'], 0]
    printed = trimesh.load_mesh(enclosure, process=True)
    mount = numbers['snap']

    def crop(low, high):
        low, high = np.asarray(low), np.asarray(high)
        box = trimesh.creation.box(extents=high-low,
            transform=trimesh.transformations.translation_matrix((low+high)/2))
        return trimesh.boolean.intersection([printed, box], engine='manifold')

    low = [centre[0]-50, 461., centre[2]+mount['frame_bottom']-2]
    high = [centre[0]+50, centre[1]+3, centre[2]+mount['frame_top']+2]
    receiver = crop(low, high)
    plate_meshes = payload_meshes(plate, lambda _: True)
    fasteners = payload_meshes(hardware, lambda _: True)
    VIEWER.mkdir(parents=True, exist_ok=True)
    records = {}

    def put(scene, name, mesh, color, shift=None):
        mesh=mesh.copy()
        if shift is not None:
            mesh.vertices += shift
        mesh.apply_transform(np.diag([-1.,-1.,1.,1.]))
        scene.add_geometry(material(mesh,color), node_name=name)

    for view in ('seated', 'separated'):
        scene = trimesh.Scene()
        put(scene, 'Production receiver section', receiver, [.32,.34,.37])
        for name, mesh, color in plate_meshes:
            put(scene,name,mesh,color,to_world+([0,18,0] if view=='separated' else [0,0,0]))
        for name, mesh, color in fasteners:
            shift = [0,35,0] if view=='separated' and 'screw' in name else [0,0,0]
            put(scene,name,mesh,color,to_world+shift)
        target = VIEWER / f'nameplate-attachment-{view}.glb'
        target.write_bytes(scene.export(file_type='glb'))
        records[view] = str(target.relative_to(ROOT/'hardware'))
        print(target.name, flush=True)

    # Full-size exterior of the complete enclosure, with its actual rear fittings.
    # Every complete panel uses its production print payload.
    # No panel is cropped away in this view.
    scene = trimesh.Scene()
    for name, mesh, color in payload_meshes(aggregate,
            lambda n:n.startswith('enclosure_') and n!='enclosure_back_top'):
        put(scene,name,mesh,color)
    back_payload=enclosure.with_name('enclosure-back-top.step.mesh')
    for name,mesh,color in payload_meshes(back_payload,lambda _:True):
        put(scene,name,mesh,color)
    def include(name):
        return (name.split('/')[0] in ('data-ring','keystone-jack',
            'c14-inlet','co2-inlet','bulkhead-water','bulkhead-carb','bulkhead-drain',
            'bulkhead-flavor-a','bulkhead-flavor-b','funnel-cover','funnel-frame')
            or name.startswith('bulkhead-ring-'))
    for name, mesh, color in payload_meshes(installed, include):
        put(scene,name,mesh,color)
    for name, mesh, color in plate_meshes+fasteners:
        put(scene,name,mesh,color,to_world)
    for view in ('installed','full-context'):
        target=VIEWER/(f'nameplate-four-screws-{view}.glb' if view=='full-context' else f'nameplate-attachment-{view}.glb')
        target.write_bytes(scene.export(file_type='glb'))
        records[view]=str(target.relative_to(ROOT/'hardware'))
        print(target.name,flush=True)
    sources=[Path(__file__),enclosure,back_payload,aggregate,plate,hardware,installed,
             HERE/'nameplate.numbers.json',plan_path]
    report={
        'geometry':'Complete production enclosure with the installed four-screw nameplate and rear connections.',
        'receiver_section_world_mm':[low,high],
        'review_rotation_about_z_degrees':180,
        'review_pose':'Presentation models turn 180 degrees about Z so the default website camera opens on the rear; production parts retain their original machine coordinates.',
        'separated_pose':'Plate moves 18 mm outwards in Y; screws move 35 mm. Inserts remain flush in their seats.',
        'views':records,
        'source_sha256':{str(p.relative_to(ROOT)):READ_SHA.get(p) or hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'attachment-review.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
