import bpy,sys,math
from mathutils import Vector
from pathlib import Path
here=Path(__file__).resolve().parent
root=here.parents[2]
out=root/'output/xlaserlab-sup29f-xh'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(out/'xlaserlab-sup29f-xh.glb'))
for obj in bpy.context.scene.objects:
    if obj.parent is None:
        obj.scale *= 1000.
for obj in bpy.context.scene.objects:
    if obj.type=='MESH':
        for p in obj.data.polygons:p.use_smooth=not any(s in obj.name for s in ('hex','nut','coupler'))
        if obj.active_material:
            bs=obj.active_material.node_tree.nodes.get('Principled BSDF')
            if bs:
                if 'boot' in obj.name:
                    bs.inputs['Base Color'].default_value=(.012,.014,.018,1)
                elif 'copper' in obj.name:
                    bs.inputs['Base Color'].default_value=(.40,.13,.06,1)
                elif any(s in obj.name for s in ('front-nut','rear-nut','coupler','thread','shank')):
                    bs.inputs['Base Color'].default_value=(.55,.36,.11,1)
                else:
                    bs.inputs['Base Color'].default_value=(.44,.49,.57,1)
                bs.inputs['Metallic'].default_value=0.0 if 'boot' in obj.name else .45
                bs.inputs['Roughness'].default_value=.72 if 'boot' in obj.name else .38
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=1600;scene.render.resolution_y=1150;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.30,.34,.39,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
target=Vector((-22,0,-67))
def light(name,pos,power,size):
    d=bpy.data.lights.new(name,'AREA');o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;d.energy=power;d.shape='DISK';d.size=size;o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
light('Key',(-100,180,230),2100000,200);light('Fill',(160,-80,180),950000,180);light('Rim',(-160,-120,80),1200000,150)
d=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',d);scene.collection.objects.link(cam);scene.camera=cam;d.type='ORTHO';d.ortho_scale=330;d.clip_end=2000
for name,position in [('preview',(200,400,220)),('side',(0,500,-67)),('rear',(-420,175,110)),('top',(0,0,500))]:
    cam.location=position;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update()
    rotation=cam.rotation_euler.to_matrix()
    projected=[rotation.transposed()@(obj.matrix_world@Vector(p)-target)
               for obj in scene.objects if obj.type=='MESH' for p in obj.bound_box]
    xmin,xmax=min(p.x for p in projected),max(p.x for p in projected)
    ymin,ymax=min(p.y for p in projected),max(p.y for p in projected)
    delta=rotation@Vector(((xmin+xmax)/2,(ymin+ymax)/2,0))
    cam.location+=delta
    d.ortho_scale=max(xmax-xmin,(ymax-ymin)*1600/1150)*1.12
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'xlaserlab-sup29f-xh.blend'))
