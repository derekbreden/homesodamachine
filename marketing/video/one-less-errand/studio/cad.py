"""Read exported faucet triangles and the physical display's firmware artwork.

This module builds no environment. Payload coordinates are millimetres; the
film works in metres.
"""
from __future__ import annotations
import json
from pathlib import Path
import re
import struct
import bpy
import numpy as np

VISIBLE_FAUCET = {
    "westbrass", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x",
    "lever", "above_counter_plate", "above_counter_gasket", "shell_base",
    "shell_tip", "faucet-display-cover-seated", "faucet_display", "faucet_display_screen",
}


def linear(color):
    if not isinstance(color, str):
        return tuple(color)
    values = [int(color.lstrip("#")[i:i+2], 16)/255 for i in (0, 2, 4)]
    return tuple(v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in values)


def material(name, color, roughness=.5, metal=0, transmission=0, ior=1.45):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    bsdf = result.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*linear(color), 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value = ior
    return result


def payload(path: Path, scene, materials, location=(0, 0, 0)):
    source = path.read_bytes()
    count = struct.unpack_from("<I", source)[0]
    header = json.loads(source[4:4+count])
    binary = memoryview(source)[4+count:]
    result = {}
    for entry in header["meshes"]:
        name = entry["name"]
        if name not in VISIBLE_FAUCET:
            continue
        positions = np.frombuffer(binary, dtype="<f4", count=entry["pos"][1], offset=entry["pos"][0]).reshape((-1, 3))
        normals = np.frombuffer(binary, dtype="<f4", count=entry["nrm"][1], offset=entry["nrm"][0]).reshape((-1, 3))
        indices = np.frombuffer(binary, dtype="<u4", count=entry["idx"][1], offset=entry["idx"][0]).reshape((-1, 3))
        indices = indices[np.all(positions[indices, 2] >= -.2, axis=1)]
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(positions))
        mesh.vertices.foreach_set("co", (positions*.001).ravel())
        mesh.loops.add(indices.size)
        mesh.loops.foreach_set("vertex_index", indices.ravel())
        mesh.polygons.add(len(indices))
        mesh.polygons.foreach_set("loop_start", np.arange(len(indices), dtype=np.int32)*3)
        mesh.polygons.foreach_set("loop_total", np.full(len(indices), 3, dtype=np.int32))
        mesh.polygons.foreach_set("use_smooth", np.ones(len(indices), dtype=bool))
        mesh.update()
        mesh.normals_split_custom_set_from_vertices(normals.tolist())
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        obj.location = location
        if name in {"faucet_display", "faucet_display_screen"}:
            finish = materials["display_glass"]
        elif name == "above_counter_gasket":
            finish = materials["rubber"]
        elif name in {"westbrass", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x"}:
            finish = materials["hardware"]
        else:
            finish = materials["shell"]
        mesh.materials.append(finish)
        result[name] = obj
    return result


def selected_display(root: Path, screen):
    source = (root/"firmware/src_faucet/images/flavor1_faucet.h").read_text()
    body = source[source.index("{")+1:source.rindex("}")]
    words = np.array([int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{4})", body)], dtype=np.uint16)
    rgb = np.stack((((words >> 11) & 31)/31, ((words >> 5) & 63)/63, (words & 31)/31), axis=1)
    rgb = np.where(rgb <= .04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
    pixels = np.ones((320, 172, 4), dtype=np.float32)
    pixels[:, :, :3] = rgb.reshape((320, 172, 3))[::-1]
    image = bpy.data.images.new("Selected flavor — firmware RGB565", width=172, height=320)
    image.pixels.foreach_set(pixels.ravel())
    image.pack()
    finish = material("Selected physical faucet display", "#FFFFFF", .24)
    bsdf = finish.node_tree.nodes.get("Principled BSDF")
    texture = finish.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    finish.node_tree.links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    finish.node_tree.links.new(texture.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = .32
    screen.data.materials.clear()
    screen.data.materials.append(finish)
    uv = screen.data.uv_layers.new(name="Physical panel UV")
    for polygon in screen.data.polygons:
        for index in polygon.loop_indices:
            vertex = screen.data.vertices[screen.data.loops[index].vertex_index].co
            uv.data[index].uv = ((vertex.x+.00888)/.01776, (vertex.z-.19962)/(.22510-.19962))

