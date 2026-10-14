"""Render the homepage's kitchen illustrations from the current CAD mesh payloads.

Manual art tool; it is not part of the build. Run with Blender's Python:

    /Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
      --python tools/render/render-kitchen-scene.py -- --preview --out /tmp/hsm-art

Omit --preview for the three publication-size PNGs. Convert them to WebP with
the existing render tools' Sharp dependency. Cabinet, sink, glass, cylinder
and liquids are illustrative staging. Faucet, enclosure and regulator geometry
come directly from the project's current, locally available mesh payloads.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import re
import struct
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--preview", action="store_true")
parser.add_argument("--scene-only", action="store_true", help="Build the shared CAD scene without rendering stills")
parser.add_argument("--out", default="/tmp/hsm-kitchen-art")
parser.add_argument("--shots", nargs="+", default=["kitchen", "faucet", "cabinet"])
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
random.seed(12)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 32 if args.preview else 160
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = 0.025 if args.preview else 0.012
scene.cycles.max_bounces = 10
scene.cycles.transmission_bounces = 8
scene.cycles.transparent_max_bounces = 8
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.image_settings.color_depth = "8"
scene.render.film_transparent = True
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Very High Contrast"
scene.view_settings.exposure = 0

# Metal is available on the local render host; CPU remains a portable fallback.
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    accelerated = False
    for device in prefs.devices:
        device.use = device.type == "METAL"
        accelerated |= device.use
    if accelerated:
        scene.cycles.device = "GPU"
except (TypeError, RuntimeError):
    pass


def linear(hex_color):
    channels = [int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)


def material(name, color, roughness=0.5, metal=0, transmission=0, ior=1.45):
    rgb = linear(color) if isinstance(color, str) else tuple(color)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["IOR"].default_value = ior
    return mat


petgf = material("Charcoal PETGF — catalog finish", (0.0331047662, 0.0331047662, 0.0363064855), 0.85)
black_rubber = material("Matte black elastomer", "#22252A", 0.91)
glass_dark = material("Dark display glass", "#15212B", 0.14)
brushed_steel = material("Brushed stainless", "#BCC4CD", 0.27, 0.92)
aluminum = material("Satin aluminum", "#C3CCD7", 0.33, 0.88)
brass = material("Satin regulator brass", "#B5995A", 0.31, 0.77)
stone = material("Fine pale stone", "#F4F5F7", 0.49)
paint = material("Warm white cabinet exterior", "#E8EDF2", 0.57)
oak = material("Pale oak cabinet interior", "#CFC4B0", 0.63)
floor = material("Ice studio floor", "#EAF0F6", 0.78)
red_tube = material("CO2 tubing", "#66717E", 0.79)
glass = material("Clear drinking glass", "#F7FCFF", 0.035, transmission=1, ior=1.46)
soda = material("Pale golden soda", "#FFFFFF", 0.08, transmission=1, ior=1.33)
stream_water = material("Carbonated water stream", "#BDD6E8", 0.12, transmission=0.65, ior=1.33)
stream_flavor = material("Flavor stream", "#C7A169", 0.1, transmission=0.71, ior=1.33)
bubble_mat = material("Air bubbles", "#FFFFFF", 0.02, transmission=1, ior=0.752)
petgf.node_tree.nodes.get("Principled BSDF").inputs["Specular IOR Level"].default_value = 0.26
# The liquid transmits a pale yellow tint without a diffuse or opaque component.
# The thin-wall vessel supplies refraction; a small highlight defines its level.
transparent = soda.node_tree.nodes.new("ShaderNodeBsdfTransparent")
transparent.inputs["Color"].default_value = (*linear("#FFF4B4"), 1)
try:
    reflection = soda.node_tree.nodes.new("ShaderNodeBsdfGlossy")
except RuntimeError:
    reflection = soda.node_tree.nodes.new("ShaderNodeBsdfAnisotropic")
reflection.inputs["Color"].default_value = (1, 1, 1, 1)
reflection.inputs["Roughness"].default_value = 0.10
mix = soda.node_tree.nodes.new("ShaderNodeMixShader")
mix.inputs[0].default_value = 0.035
soda.node_tree.links.new(transparent.outputs["BSDF"], mix.inputs[1])
soda.node_tree.links.new(reflection.outputs["BSDF"], mix.inputs[2])
soda.node_tree.links.new(mix.outputs["Shader"], soda.node_tree.nodes.get("Material Output").inputs["Surface"])

# Subtle material grain reads as a manufactured surface, never a decorative texture.
for mat, scale, strength, distance in ((stone, 900, 0.11, 0.00009), (petgf, 2100, 0.10, 0.00005)):
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], nodes.get("Principled BSDF").inputs["Normal"])

nodes, links = oak.node_tree.nodes, oak.node_tree.links
coordinates = nodes.new("ShaderNodeTexCoord")
mapping = nodes.new("ShaderNodeVectorMath")
mapping.operation = "MULTIPLY"
mapping.inputs[1].default_value = (90, 8, 4)
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 3
noise.inputs["Detail"].default_value = 2
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.2
ramp.color_ramp.elements[0].color = (*linear("#CDC0AC"), 1)
ramp.color_ramp.elements[1].position = 0.8
ramp.color_ramp.elements[1].color = (*linear("#DDD3C2"), 1)
links.new(coordinates.outputs["Generated"], mapping.inputs[0])
links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])


def smooth(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def box(name, size, location, mat, bevel=0.002, segments=4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    if bevel:
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = segments
        modifier.limit_method = "ANGLE"
        normals = obj.modifiers.new("Planar surface normals", "WEIGHTED_NORMAL")
        normals.keep_sharp = True
    return obj


def difference(obj, cutter):
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new("Illustrative sink opening", "BOOLEAN")
    modifier.operation = "DIFFERENCE"
    modifier.object = cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def lathe(name, profile, mat, location, segments=128, profile_normals=False):
    if profile_normals:
        # Keep the vessel's long straight wall normals separate from its floor/rim.
        # Averaging a floor into the entire side would give the glass a false lens.
        verts, faces, vertex_normals = [], [], []
        for j, ((r0, z0), (r1, z1)) in enumerate(zip(profile, profile[1:])):
            length = math.hypot(r1 - r0, z1 - z0)
            radial, vertical = (z1 - z0) / length, -(r1 - r0) / length
            for r, z in ((r0, z0), (r1, z1)):
                for i in range(segments):
                    angle = 2 * math.pi * i / segments
                    verts.append((r * math.cos(angle), r * math.sin(angle), z))
                    vertex_normals.append((radial * math.cos(angle), radial * math.sin(angle), vertical))
            start = j * segments * 2
            faces.extend((start + i, start + (i + 1) % segments,
                          start + segments + (i + 1) % segments, start + segments + i) for i in range(segments))
    else:
        verts = [(r * math.cos(2 * math.pi * i / segments), r * math.sin(2 * math.pi * i / segments), z)
                 for r, z in profile for i in range(segments)]
        faces = [(j * segments + i, j * segments + (i + 1) % segments,
                  (j + 1) * segments + (i + 1) % segments, (j + 1) * segments + i)
                 for j in range(len(profile) - 1) for i in range(segments)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.data.materials.append(mat)
    smooth(obj)
    if profile_normals:
        mesh.normals_split_custom_set_from_vertices(vertex_normals)
    return obj


def tube(name, points, radius, mat, kind="BEZIER"):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 28
    curve.bevel_depth = radius
    curve.bevel_resolution = 5
    curve.use_fill_caps = True
    spline = curve.splines.new(kind)
    if kind == "BEZIER":
        spline.bezier_points.add(len(points) - 1)
        for handle, point in zip(spline.bezier_points, points):
            handle.co = point
            handle.handle_left_type = handle.handle_right_type = "AUTO"
    else:
        spline.points.add(len(points) - 1)
        for handle, point in zip(spline.points, points):
            handle.co = (*point, 1)
    obj = bpy.data.objects.new(name, curve)
    scene.collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def cylinder(name, radius, height, location, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=radius, depth=height, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    bevel = obj.modifiers.new("Machined rim", "BEVEL")
    bevel.width, bevel.segments = min(0.0012, height / 6), 3
    return smooth(obj)


def payload(path, predicate, material_for, location=(0, 0, 0), rotation=0, clip_floor=None):
    source = (ROOT / path).read_bytes()
    count = struct.unpack_from("<I", source)[0]
    header = json.loads(source[4:4 + count])
    data = memoryview(source)[4 + count:]
    objects = []
    for entry in header["meshes"]:
        name = entry["name"]
        if not predicate(name):
            continue
        positions = np.frombuffer(data, dtype="<f4", count=entry["pos"][1], offset=entry["pos"][0]).reshape((-1, 3)).copy()
        normals = np.frombuffer(data, dtype="<f4", count=entry["nrm"][1], offset=entry["nrm"][0]).reshape((-1, 3))
        indices = np.frombuffer(data, dtype="<u4", count=entry["idx"][1], offset=entry["idx"][0]).reshape((-1, 3))
        if clip_floor is not None:
            indices = indices[np.all(positions[indices, 2] >= clip_floor, axis=1)]
        mesh = bpy.data.meshes.new(name)
        mesh.vertices.add(len(positions))
        mesh.vertices.foreach_set("co", (positions * 0.001).ravel())
        mesh.loops.add(indices.size)
        mesh.loops.foreach_set("vertex_index", indices.ravel())
        mesh.polygons.add(len(indices))
        mesh.polygons.foreach_set("loop_start", np.arange(len(indices), dtype=np.int32) * 3)
        mesh.polygons.foreach_set("loop_total", np.full(len(indices), 3, dtype=np.int32))
        mesh.polygons.foreach_set("use_smooth", np.ones(len(indices), dtype=bool))
        mesh.update()
        mesh.normals_split_custom_set_from_vertices(normals.tolist())
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler.z = rotation
        obj.data.materials.append(material_for(entry))
        objects.append(obj)
    return objects


# The cabinet is deliberately open at the front and cut away at its right side.
# Its staging is a kitchen cabinet, with the product kept at its actual CAD scale.
counter_top = 0.83
box("Cabinet left side", (0.023, 0.63, 0.757), (-0.423, 0.015, 0.424), oak)
box("Cabinet pale outer left skin", (0.003, 0.63, 0.757), (-0.436, 0.015, 0.424), paint)
box("Cabinet rear panel", (0.846, 0.018, 0.757), (0, 0.321, 0.424), oak)
box("Cutaway right rear side", (0.023, 0.145, 0.757), (0.423, 0.257, 0.424), oak)
box("Cabinet base", (0.869, 0.63, 0.023), (0, 0.015, 0.055), oak)
box("Pale cabinet base edge", (0.869, 0.017, 0.025), (0, -0.308, 0.055), paint)
box("Recessed plinth", (0.811, 0.558, 0.028), (0, 0.039, 0.028), paint)
counter = box("Pale stone worktop", (0.97, 0.72, 0.032), (0, 0.015, counter_top - 0.016), stone, 0.006, 6)

# A secondary sink and normal water tap establish that the soda faucet is dedicated.
sink_x, sink_y = -0.232, 0.11
hole = box("Sink worktop cut", (0.346, 0.292, 0.26), (sink_x, sink_y, counter_top), stone, 0.028, 8)
bpy.context.view_layer.objects.active = hole
bpy.ops.object.modifier_apply(modifier="Soft manufactured edges")
difference(counter, hole)
sink = box("Undermount stainless sink", (0.362, 0.309, 0.124), (sink_x, sink_y, counter_top - 0.066), brushed_steel, 0.029, 8)
inner = box("Sink hollow", (0.35, 0.297, 0.17), (sink_x, sink_y, counter_top - 0.025), brushed_steel, 0.026, 8)
bpy.context.view_layer.objects.active = inner
bpy.ops.object.modifier_apply(modifier="Soft manufactured edges")
difference(sink, inner)
cylinder("Sink drain", 0.016, 0.0015, (sink_x, sink_y, counter_top - 0.12), aluminum)
tube("Quiet sink plumbing", [(sink_x, sink_y, 0.709), (sink_x, sink_y, 0.59), (sink_x, 0.18, 0.54),
                              (sink_x, 0.235, 0.55), (sink_x, 0.27, 0.61), (sink_x, 0.322, 0.61)], 0.014, paint)
normal_x, normal_y = -0.232, 0.296
cylinder("Standard tap base", 0.023, 0.008, (normal_x, normal_y, counter_top + 0.004), brushed_steel)
tube("Standard kitchen water tap", [(normal_x, normal_y, counter_top + 0.008),
                                    (normal_x, normal_y, counter_top + 0.10),
                                    (normal_x, normal_y - 0.045, counter_top + 0.158),
                                    (normal_x, normal_y - 0.132, counter_top + 0.153),
                                    (normal_x, normal_y - 0.165, counter_top + 0.112)], 0.0074, brushed_steel)
tube("Standard tap control", [(normal_x + 0.01, normal_y, counter_top + 0.025),
                              (normal_x + 0.039, normal_y, counter_top + 0.027),
                              (normal_x + 0.041, normal_y - 0.027, counter_top + 0.049)], 0.004, brushed_steel)

faucet_at = (0.214, 0.037, counter_top)
visible_faucet = {"westbrass", "soda_faucet_tube", "flavor_tube_pos_x", "flavor_tube_neg_x",
                  "lever", "above_counter_plate", "above_counter_gasket", "shell_base", "shell_tip",
                  "faucet-display-cover-seated", "faucet_display", "faucet_display_screen"}
faucet_objects = payload("hardware/faucet-layout/faucet-assembly.step.mesh", lambda name: name in visible_faucet,
                         lambda entry: glass_dark if entry["name"] in {"faucet_display", "faucet_display_screen"} else petgf,
                         faucet_at, clip_floor=-6)

# The selected flavor fills the current faucet UI. A touch toggles the flavor.
# Decode the very RGB565 art that the firmware compiles, then map its physical panel.
screen = next(obj for obj in faucet_objects if obj.name == "faucet_display_screen")


def flavor_texture(index):
    source = (ROOT / f"firmware/src_faucet/images/flavor{index}_faucet.h").read_text()
    words = np.array([int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{4})", source[source.index("{") + 1:source.rindex("}")])], dtype=np.uint16)
    rgb = np.stack((((words >> 11) & 31) / 31, ((words >> 5) & 63) / 63, (words & 31) / 31), axis=1)
    rgb = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    pixels = np.ones((320, 172, 4), dtype=np.float32)
    pixels[:, :, :3] = rgb.reshape((320, 172, 3))[::-1]
    image = bpy.data.images.new(f"Firmware flavor {index + 1}", width=172, height=320)
    image.pixels.foreach_set(pixels.ravel())
    image.pack()
    return image


tex = flavor_texture(1)
screen_mat = material("Faucet display — selected flavor", "#1749D1", 0.23)
nodes, links = screen_mat.node_tree.nodes, screen_mat.node_tree.links
image = nodes.new("ShaderNodeTexImage")
image.image = tex
links.new(image.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
links.new(image.outputs["Color"], nodes.get("Principled BSDF").inputs["Emission Color"])
nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 0.18
screen.data.materials.clear()
screen.data.materials.append(screen_mat)
uv = screen.data.uv_layers.new(name="Physical screen UV")
for polygon in screen.data.polygons:
    for loop_index in polygon.loop_indices:
        vertex = screen.data.vertices[screen.data.loops[loop_index].vertex_index].co
        uv.data[loop_index].uv = ((vertex.x + 0.00888) / 0.01776, (vertex.z - 0.19962) / (0.2251 - 0.19962))

unit_at = (0.144, -0.154, 0.071)
unit_objects = payload("hardware/manifold-layout/enclosure-assembly.step.mesh",
                       lambda name: name.startswith(("enclosure-", "nameplate", "display", "funnel")) or name == "pump-jack",
                       lambda entry: glass_dark if entry["name"].startswith("display/") else
                       material(entry["name"], entry["color"], 0.8) if "ink" in entry["name"] else petgf,
                       unit_at)

# The enclosure's current Home page: flavor rail, selected portrait, status pane.
# This graphic follows buildHome/buildRail in firmware/src_front/main.cpp and uses
# the same firmware flavor artwork. It is drawn on the source model's screen plane.
ui_blue = material("UI cobalt", "#1749D1", 0.31)
ui_ice = material("UI ice", "#DCE6FF", 0.31)
ui_navy = material("UI navy", "#10319C", 0.31)
ui_white = material("UI white", "#FFFFFF", 0.31)
ui_orange = material("UI orange", "#FF9152", 0.31)
for mat in (ui_blue, ui_ice, ui_navy, ui_white, ui_orange):
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Emission Color"].default_value = shader.inputs["Base Color"].default_value
    shader.inputs["Emission Strength"].default_value = 0.16
ui_center = Vector((unit_at[0], unit_at[1] + 0.0510921, unit_at[2] + 0.3266469))
ui_up, ui_normal = Vector((0, math.sqrt(3) / 2, 0.5)), Vector((0, -0.5, math.sqrt(3) / 2))


def ui_point(x, y, lift=0.00035):
    return ui_center + Vector((x, 0, 0)) + y * ui_up + lift * ui_normal


def ui_quad(name, x, y, width, height, mat, lift=0.0004, texture=None):
    corners = [ui_point(x, y, lift), ui_point(x + width, y, lift),
               ui_point(x + width, y + height, lift), ui_point(x, y + height, lift)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(corners, [], [(0, 1, 2, 3)])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    if texture:
        mat = material(name, "#FFFFFF", 0.31)
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        image = nodes.new("ShaderNodeTexImage")
        image.image = texture
        links.new(image.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
        links.new(image.outputs["Color"], nodes.get("Principled BSDF").inputs["Emission Color"])
        nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 0.16
        uv = mesh.uv_layers.new()
        for i, co in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
            uv.data[i].uv = co
    obj.data.materials.append(mat)
    return obj


ui_font = bpy.data.fonts.load(str(ROOT / "hardware/install-guide/fonts/Plex-Regular.ttf"))


def ui_text(text, x, y, size, mat=ui_white):
    curve = bpy.data.curves.new(text, "FONT")
    curve.body, curve.size, curve.font = text, size, ui_font
    obj = bpy.data.objects.new("UI " + text, curve)
    scene.collection.objects.link(obj)
    obj.location = ui_point(x, y, 0.00062)
    obj.rotation_euler.x = math.radians(30)
    obj.data.materials.append(mat)


ui_quad("Physical enclosure UI", -0.0499, -0.030, 0.0998, 0.06, ui_blue)
ui_quad("Flavor selection rail", -0.0499, -0.030, 0.013, 0.06, ui_navy, 0.00045)
ui_quad("Selected flavor panel", -0.0369, -0.030, 0.0292, 0.06, ui_ice, 0.00045)
ui_quad("Flavor 1 rail artwork", -0.0474, 0.008, 0.008, 0.01488, ui_white, 0.0005, flavor_texture(0))
ui_quad("Flavor 2 rail artwork", -0.0474, -0.018, 0.008, 0.01488, ui_white, 0.0005, tex)
ui_quad("Selected flavor artwork", -0.0331, -0.021, 0.0215, 0.040, ui_white, 0.0005, tex)
ui_text("Fill", -0.0025, 0.024, 0.0030)
ui_text("Prime", 0.0140, 0.024, 0.0030)
ui_text("Clean", 0.0310, 0.024, 0.0030)
ui_text("Pouring.", -0.0045, 0.0130, 0.0053)
ui_text("Reservoir", -0.0045, -0.015, 0.0027)
for i in range(4):
    ui_quad("Reservoir segment", 0.030 + i * 0.0046, -0.015, 0.0038, 0.0022, ui_orange, 0.00058)
ui_quad("UI divider", -0.0045, -0.020, 0.0512, 0.00012, ui_ice, 0.00054)
ui_text("Change image", -0.0045, -0.027, 0.0024)
ui_text("Ratio", 0.037, -0.027, 0.0024, ui_ice)
tube("Faucet umbilical", [(0.214, 0.037, 0.809), (0.214, 0.07, 0.66), (0.207, 0.232, 0.579),
                          (0.19, 0.297, 0.506), (0.178, 0.312, 0.387)], 0.009, black_rubber)

# The 5 lb cylinder envelope is 133 mm × 457 mm in the installation artwork.
cylinder_at = (-0.253, -0.184, 0.067)
lathe("Five-pound aluminum CO2 cylinder", [(0, 0), (0.050, 0), (0.062, 0.008), (0.0665, 0.02),
      (0.0665, 0.367), (0.065, 0.390), (0.057, 0.41), (0.046, 0.428),
      (0.022, 0.442), (0.017, 0.446), (0.017, 0.457), (0, 0.457)], aluminum, cylinder_at)
cylinder("Cylinder brass valve", 0.013, 0.033, (-0.253, -0.184, 0.539), brass)
cylinder("Cylinder valve handwheel", 0.020, 0.010, (-0.253, -0.184, 0.557), black_rubber)
reg_at = (-0.328, -0.184, 0.537)
reg_materials = {}


def regulator_material(entry):
    color = tuple(entry["color"])
    if color not in reg_materials:
        metal = 0 if "print" in entry["name"] or "dial" in entry["name"] or "band" in entry["name"] else 0.76
        reg_materials[color] = material("Regulator " + entry["name"], color, 0.35, metal)
    return reg_materials[color]


payload("hardware/reference/taprite-3741-regulator/taprite-3741-regulator.step.mesh", lambda name: True,
        regulator_material, reg_at, rotation=math.pi)
tube("CO2 supply", [(-0.328, -0.184, 0.494), (-0.324, -0.15, 0.432),
                   (-0.29, 0.235, 0.411), (-0.09, 0.285, 0.408), (0.168, 0.319, 0.40)], 0.0032, red_tube)

glass_at = (0.214, -0.143, counter_top + 0.001)
lathe("Cold soda glass", [(0, 0), (0.027, 0), (0.03, 0.004), (0.0347, 0.116),
      (0.0345, 0.119), (0.0331, 0.12), (0.0327, 0.116), (0.028, 0.006), (0, 0.006)], glass, glass_at,
      profile_normals=True)
lathe("Soda in the glass", [(0, 0.006), (0.0277, 0.006), (0.0315, 0.085), (0.0317, 0.087), (0, 0.087)], soda, glass_at,
      profile_normals=True)
tube("Clear soda pour", [(0.214, -0.100, counter_top + 0.185), (0.214, -0.12, counter_top + 0.145),
                         (0.214, -0.14, counter_top + 0.091)], 0.0016, stream_water)
tube("Separate flavor pour", [(0.2108, -0.103, counter_top + 0.185),
                              (0.2108, -0.123, counter_top + 0.145),
                              (0.211, -0.145, counter_top + 0.091)], 0.00040, stream_flavor)
for i in range(52):
    radius = random.uniform(0.00055, 0.0010)
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0.006, 0.027)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=6, radius=radius,
        location=(glass_at[0] + math.cos(angle) * distance, glass_at[1] + math.sin(angle) * distance,
                  glass_at[2] + random.uniform(0.011, 0.086)))
    bubble = bpy.context.object
    bubble.name = "Tiny carbonation bubble"
    bubble.data.materials.append(bubble_mat)
    smooth(bubble)

box("Studio floor", (200, 200, 0.01), (0, 0, -0.005), floor, 0)
detail_counter = box("Faucet close-up stone surface", (3, 3, 0.032), (0, 0, counter_top - 0.016), stone, 0.004)
detail_counter.hide_render = True
world = bpy.data.worlds.new("Cool neutral studio")
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (*linear("#E7EEF8"), 1)
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.24
scene.world = world


def area(name, location, target, energy, size, color):
    light = bpy.data.lights.new(name, "AREA")
    light.energy, light.shape, light.size = energy, "DISK", size
    light.color = linear(color)
    obj = bpy.data.objects.new(name, light)
    scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


area("Large soft window", (-1.8, -2.1, 3.0), (0, 0, 0.55), 220, 2.3, "#FFF9F1")
area("Pale front fill", (1.5, -1.9, 1.5), (0.1, 0, 0.4), 55, 1.7, "#E2EDFF")
area("Counter and faucet rim", (0.5, 1.5, 2.5), (0, 0, 0.55), 165, 1.8, "#FFFFFF")
area("Glass reflection strip", (0.70, -0.9, 1.45), (0.20, -0.10, 0.91), 15, 0.42, "#FFFFFF")

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.name = "Architectural product camera"
camera.data.type = "ORTHO"
camera.data.lens = 70
scene.camera = camera


def pose(position, target, span):
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.ortho_scale = span
    bpy.context.view_layer.update()


focals = {"faucet": (0.214, -0.093, 1.045), "faucet_base": (0.214, 0.037, 0.85),
          "glass": (0.214, -0.143, 0.90), "machine": (0.144, -0.147, 0.29),
          "machine_display": (0.144, -0.11, 0.405), "cylinder": (-0.253, -0.184, 0.31),
          "counter_front": (0, -0.345, 0.813), "counter_rear": (0, 0.375, 0.813)}
shots = {
    "kitchen": ((1.35, -2.5, 1.50), (0, 0.007, 0.508), 1.29, (1800, 1800)),
    "faucet": ((0.78, -1.30, 1.37), (0.197, -0.047, 0.96), 0.53, (1800, 1350)),
    "cabinet": ((0.89, -1.70, 0.95), (-0.045, 0.01, 0.325), 0.99, (1800, 1350)),
}
for shot in ([] if args.scene_only else args.shots):
    detail_counter.hide_render = shot != "faucet"
    for obj in scene.objects:
        if obj.name.startswith("Standard ") or obj.name in {"Pale stone worktop", "Undermount stainless sink", "Sink drain"}:
            obj.hide_render = shot == "faucet"
    position, target, span, dimensions = shots[shot]
    pose(position, target, span)
    scene.render.resolution_x, scene.render.resolution_y = dimensions
    scene.render.resolution_percentage = 50 if args.preview else 100
    scene.render.filepath = str(OUT / f"{shot}.png")
    positions = {}
    for name, point in focals.items():
        projected = world_to_camera_view(scene, camera, Vector(point))
        positions[name] = {"x": round(projected.x, 4), "y": round(1 - projected.y, 4)}
    (OUT / f"{shot}.focals.json").write_text(json.dumps({"dimensions": dimensions, "normalized": positions}, indent=2) + "\n")
    print(f"HSM_ART rendering {shot} to {scene.render.filepath}", flush=True)
    bpy.ops.render.render(write_still=True)
    print(f"HSM_ART completed {shot}", flush=True)
