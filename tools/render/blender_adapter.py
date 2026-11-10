"""Apply native scene descriptors to Blender and render their explicit frame poses."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def socket(sockets, key):
    return sockets[int(key)] if key.isdigit() else sockets[key]


def apply(path):
    spec = json.loads(Path(path).read_text())
    binary = Path(spec["buffer"]).read_bytes()

    def values(span, code="f"):
        return memoryview(binary)[span["offset"]:span["offset"] + span["count"] * 4].cast(code)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    settings = spec["settings"]
    scene.render.engine = "CYCLES"
    for key in ("samples", "max_bounces", "transmission_bounces", "transparent_max_bounces", "seed"):
        source = "transparent_bounces" if key == "transparent_max_bounces" else key
        setattr(scene.cycles, key, settings[source])
    scene.cycles.use_denoising = True
    scene.cycles.adaptive_threshold = settings["threshold"]
    scene.cycles.use_animated_seed = False
    scene.render.use_persistent_data = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if settings["transparent"] else "RGB"
    scene.render.film_transparent = settings["transparent"]
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = settings["look"]
    scene.view_settings.exposure = 0
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == "METAL"
        if any(device.use for device in prefs.devices):
            scene.cycles.device = "GPU"
    except (TypeError, RuntimeError):
        pass
    world = bpy.data.worlds.new("Native studio environment")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*settings["world"], 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = settings["world_strength"]
    scene.world = world

    materials = {}
    for row in spec["materials"]:
        material = bpy.data.materials.new(row["name"])
        material.use_nodes = True
        nodes, links = material.node_tree.nodes, material.node_tree.links
        shader = nodes["Principled BSDF"]
        for key, value in (("Base Color", (*row["base"], 1)), ("Roughness", row["roughness"]),
                           ("Metallic", row["metal"]), ("Transmission Weight", row["transmission"]),
                           ("IOR", row["ior"]), ("Emission Color", (*row["base"], 1)),
                           ("Emission Strength", row["emission"])):
            shader.inputs[key].default_value = value
        if row["specular"] is not None:
            shader.inputs["Specular IOR Level"].default_value = row["specular"]
        if row["anisotropy"] is not None:
            key = "Anisotropic IOR Level" if "Anisotropic IOR Level" in shader.inputs else "Anisotropic"
            shader.inputs[key].default_value = row["anisotropy"]
        if row["texture"]:
            texture = nodes.new("ShaderNodeTexImage")
            texture.image = bpy.data.images.load(row["texture"], check_existing=True)
            links.new(texture.outputs["Color"], shader.inputs["Base Color"])
            links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
        aliases = {node.name: node for node in nodes}
        for descriptor in row["nodes"]:
            node = nodes.new(descriptor["kind"])
            aliases[descriptor["id"]] = node
            for key, value in descriptor["properties"].items():
                parts = key.split(".")
                target = node
                for name in parts[:-1]:
                    target = getattr(target, name)
                setattr(target, parts[-1], value)
            for key, value in descriptor["inputs"].items():
                socket(node.inputs, key).default_value = value
            if descriptor["ramp"]:
                while len(node.color_ramp.elements) < len(descriptor["ramp"]):
                    node.color_ramp.elements.new(0.5)
                for element, (position, color) in zip(node.color_ramp.elements, descriptor["ramp"]):
                    element.position, element.color = position, color
        for link in row["links"]:
            links.new(socket(aliases[link["from"]].outputs, link["output"]),
                      socket(aliases[link["to"]].inputs, link["input"]))
        materials[row["name"]] = material
        material["native_aliases"] = json.dumps({key: node.name for key, node in aliases.items()})

    objects = {}
    for row in spec["objects"]:
        shape = row["geometry"]
        kind = shape["kind"]
        name = row["name"]
        if kind == "mesh":
            mesh = bpy.data.meshes.new(name)
            indices = values(shape["triangles"], "I")
            mesh.vertices.add(shape["vertices"]["count"] // 3)
            mesh.vertices.foreach_set("co", values(shape["vertices"]))
            mesh.loops.add(len(indices))
            mesh.loops.foreach_set("vertex_index", indices)
            mesh.polygons.add(len(indices) // 3)
            mesh.polygons.foreach_set("loop_start", range(0, len(indices), 3))
            mesh.polygons.foreach_set("loop_total", [3] * (len(indices) // 3))
            mesh.polygons.foreach_set("use_smooth", [shape["smooth"]] * (len(indices) // 3))
            mesh.update()
            if shape.get("normals"):
                normal = values(shape["normals"])
                mesh.normals_split_custom_set_from_vertices(list(zip(normal[::3], normal[1::3], normal[2::3])))
            if shape.get("uv"):
                points = values(shape["uv"])
                uv = mesh.uv_layers.new()
                for loop in mesh.loops:
                    uv.data[loop.index].uv = points[loop.vertex_index * 2:loop.vertex_index * 2 + 2]
            obj = bpy.data.objects.new(name, mesh)
        elif kind == "instance":
            obj = bpy.data.objects.new(name, objects[shape["source"]].data)
        elif kind == "curve":
            curve = bpy.data.curves.new(name, "CURVE")
            curve.dimensions, curve.resolution_u = "3D", 28
            curve.bevel_depth, curve.bevel_resolution = shape["radius"], 5
            curve.use_fill_caps = True
            spline = curve.splines.new("BEZIER" if shape["bezier"] else "POLY")
            points = spline.bezier_points if shape["bezier"] else spline.points
            points.add(len(shape["points"]) - 1)
            for point, co in zip(points, shape["points"]):
                point.co = co if shape["bezier"] else (*co, 1)
                if shape["bezier"]:
                    point.handle_left_type = point.handle_right_type = "AUTO"
            spline.use_cyclic_u = shape["closed"]
            obj = bpy.data.objects.new(name, curve)
        elif kind == "text":
            curve = bpy.data.curves.new(name, "FONT")
            curve.body, curve.size = shape["body"], shape["size"]
            curve.font = bpy.data.fonts.load(shape["font"], check_existing=True)
            curve.align_x = shape["align"]
            obj = bpy.data.objects.new(name, curve)
        elif kind == "area":
            light = bpy.data.lights.new(name, "AREA")
            light.energy, light.size, light.color = shape["energy"], shape["size"], shape["color"]
            light.shape = "RECTANGLE" if shape["size_y"] else "DISK"
            if shape["size_y"]:
                light.size_y = shape["size_y"]
            obj = bpy.data.objects.new(name, light)
        else:
            obj = bpy.data.objects.new(name, None)
        scene.collection.objects.link(obj)
        obj.location, obj.rotation_euler, obj.scale = row["location"], row["rotation"], row["scale"]
        obj.hide_render = row["hidden"]
        obj.visible_transmission, obj.visible_glossy = row["transmission"], row["glossy"]
        obj.visible_camera, obj.visible_diffuse, obj.visible_shadow = row["camera"], row["diffuse"], row["shadow"]
        if row["parent"]:
            obj.parent = objects[row["parent"]]
        if row["material"]:
            obj.data.materials.append(materials[row["material"]])
        if row["bevel"]:
            modifier = obj.modifiers.new("Native specified edge finish", "BEVEL")
            modifier.width, modifier.segments = row["bevel"], row["bevel_segments"]
        if row["normals"]:
            obj.modifiers.new("Native specified planar normals", "WEIGHTED_NORMAL")
        objects[name] = obj

    for row in spec["objects"]:
        obj = objects[row["name"]]
        if row["receivers"]:
            receivers = bpy.data.collections.new(row["name"] + " receivers")
            for name in row["receivers"]:
                receivers.objects.link(objects[name])
            obj.light_linking.receiver_collection = receivers
        for name in row["difference"]:
            cutter = objects[name]
            bpy.context.view_layer.objects.active = cutter
            for modifier in list(cutter.modifiers):
                bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.context.view_layer.objects.active = obj
            modifier = obj.modifiers.new("Native specified subtraction", "BOOLEAN")
            modifier.operation, modifier.object = "DIFFERENCE", cutter
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(cutter, do_unlink=True)

    camera = bpy.data.objects.new("Native camera", bpy.data.cameras.new("Native camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera.data.clip_start, camera.data.clip_end = .003, 1000
    camera.data.dof.aperture_blades = 9
    for frame in spec["frames"]:
        scene.frame_set(frame["number"])
        pose = frame["camera"]
        camera.location = pose["position"]
        camera.rotation_euler = (Vector(pose["target"]) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.type = "ORTHO" if pose["ortho"] else "PERSP"
        if pose["ortho"]:
            camera.data.ortho_scale = pose["ortho"]
        camera.data.lens = pose["lens"]
        camera.data.dof.use_dof = bool(pose["focus"])
        if pose["focus"]:
            camera.data.dof.focus_distance = (Vector(pose["focus"]) - camera.location).length
        camera.data.dof.aperture_fstop = pose["aperture"]
        for row in frame["updates"]:
            obj = objects[row["name"]]
            for key in ("location", "scale"):
                if key in row:
                    setattr(obj, key, row[key])
            if "rotation" in row:
                obj.rotation_euler = row["rotation"]
            if "hidden" in row:
                obj.hide_render = row["hidden"]
            if "vertices" in row:
                obj.data.vertices.foreach_set("co", values(row["vertices"]))
                obj.data.update()
            if "energy" in row:
                obj.data.energy = row["energy"]
        for material, alias, key, value in frame["node_inputs"]:
            aliases = json.loads(materials[material]["native_aliases"])
            node = materials[material].node_tree.nodes[aliases[alias]]
            socket(node.inputs, key).default_value = value
        scene.render.resolution_x, scene.render.resolution_y = frame["width"], frame["height"]
        scene.render.resolution_percentage = 100
        scene.render.filepath = frame["file"]
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
    if spec["save"]:
        bpy.ops.wm.save_as_mainfile(filepath=spec["save"])


apply(sys.argv[sys.argv.index("--") + 1])
