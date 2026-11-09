"""The display cache packs SolidCraft's exported surfaces for loading an assembly without its authoring files."""
import json
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
source, output, report = map(Path, args[:3])
models = args[3:] or tuple(path.stem for path in sorted(source.glob('*.obj'))
                          if not path.stem.endswith(('-stage', '-parent'))
                          and not (source / f'{path.stem}-reference.obj').exists())
output.mkdir(parents=True, exist_ok=True)
results = {}
for name in models:
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.obj_import(filepath=str(source / f'{name}.obj'), forward_axis='Y', up_axis='Z')
    meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    before, after = 0, 0
    volume_before, volume_after = 0., 0.
    for obj in meshes:
        mesh = bmesh.new()
        mesh.from_mesh(obj.data)
        before += sum(len(face.verts) - 2 for face in mesh.faces)
        volume_before += mesh.calc_volume(signed=True)
        bmesh.ops.remove_doubles(mesh, verts=list(mesh.verts), dist=1e-6)
        mesh.normal_update()
        bmesh.ops.dissolve_limit(mesh, angle_limit=1e-2, delimit=set(), use_dissolve_boundaries=False,
                                verts=list(mesh.verts), edges=list(mesh.edges))
        bmesh.ops.triangulate(mesh, faces=list(mesh.faces))
        after += len(mesh.faces)
        volume_after += mesh.calc_volume(signed=True)
        mesh.to_mesh(obj.data)
        mesh.free()
        for face in obj.data.polygons:
            face.use_smooth = True
        obj.data.set_sharp_from_angle(angle=0.1)
        colors = obj.data.color_attributes.new(name='Finish', type='FLOAT_COLOR', domain='CORNER')
        for face in obj.data.polygons:
            mat = obj.data.materials[face.material_index] if obj.data.materials else None
            bsdf = mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
            color = bsdf.inputs['Base Color'].default_value if bsdf else (0.46, 0.51, 0.59, 1.)
            for loop in face.loop_indices:
                colors.data[loop].color = tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in color[:3]) + (1.,)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = name + ' saved shape'
    material = bpy.data.materials.new(name='Published component finishes')
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    vertex = material.node_tree.nodes.new('ShaderNodeVertexColor')
    vertex.layer_name = 'Finish'
    material.node_tree.links.new(vertex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Metallic'].default_value = .65
    bsdf.inputs['Roughness'].default_value = .35
    obj.data.materials.clear()
    obj.data.materials.append(material)
    for polygon in obj.data.polygons:
        polygon.material_index = 0
    bpy.ops.export_scene.gltf(filepath=str(output / f'{name}.glb'), export_format='GLB',
                              export_yup=False, export_cameras=False, export_lights=False,
                              export_animations=False, use_selection=True)
    bounds = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    results[name] = {'source_triangles': before, 'display_triangles': after,
                     'source_mesh_volume_mm3': volume_before,
                     'display_mesh_volume_mm3': volume_after,
                     'bounds': [[min(v[i] for v in bounds) for i in range(3)],
                                [max(v[i] for v in bounds) for i in range(3)]],
                     'bytes': (output / f'{name}.glb').stat().st_size}
report.write_text(json.dumps(results, indent=2) + '\n')
