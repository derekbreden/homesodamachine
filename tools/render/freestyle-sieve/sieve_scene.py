"""Parameterized Freestyle stroke render for the camera/visibility sieve.

Runs inside Blender:

    blender --background --python sieve_scene.py -- <args.json>

Renders ONLY the Freestyle strokes (no disc/clip) of an imported
appliance STL for one iso view, with the camera distance and Freestyle
visibility settings taken from args. The orthographic projection is
distance-independent, so every render of a given view lands its lines
at identical pixel positions — only which edges survive the visibility
test changes. That makes the outputs directly comparable pixel-for-pixel
by sieve.py.

Args:
    appliance_stl: str
    out_svg: str
    view: "front" | "back"
    cam_mult: float — camera distance as a multiple of the bbox diagonal
    visibility: "VISIBLE" | "RANGE" (default VISIBLE)
    qi_start, qi_end: int (used when visibility == RANGE)
    clip_start_mult, clip_end_mult: float — clip planes as bbox-diag
        multiples (default: bracket the geometry around the camera)
    split_at_invisible: bool (default False)
    crease_angle: float radians (optional)
    use_culling: bool (optional)
"""
import json
import sys
from pathlib import Path

import bpy
import addon_utils
import mathutils

args = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text())

ISO = {
    "front": mathutils.Vector((1, -1, 1)).normalized(),
    "back": mathutils.Vector((1, 1, 1)).normalized(),
}

addon_utils.enable("bl_ext.blender_org.freestyle_svg_exporter")
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.wm.stl_import(filepath=args["appliance_stl"])
obj = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.01 * float(args.get("model_scale", 1.0)))
bpy.ops.object.mode_set(mode="OBJECT")

# Optional uniform scale + recenter, to test whether absolute coordinate
# magnitude (mm-scale geometry far from origin) drives the raycast
# precision loss.
_scale = float(args.get("model_scale", 1.0))
if _scale != 1.0:
    obj.scale = (_scale, _scale, _scale)
    bpy.context.view_layer.update()
    bpy.ops.object.transform_apply(scale=True)
if bool(args.get("center_origin", False)):
    import statistics
    bb = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    ctr = sum(bb, mathutils.Vector((0, 0, 0))) / len(bb)
    obj.location -= ctr
    bpy.context.view_layer.update()
    bpy.ops.object.transform_apply(location=True)

bbox = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
view = args["view"]
cam_dir = ISO[view]
world_up = mathutils.Vector((0, 0, 1))

# Framing basis (camera at the nominal direction)
fwd0 = -cam_dir
r0 = fwd0.cross(world_up).normalized()
u0 = r0.cross(fwd0).normalized()
us = [c.dot(r0) for c in bbox]
vs = [c.dot(u0) for c in bbox]
u_min, u_max, v_min, v_max = min(us), max(us), min(vs), max(vs)
# Margin scales with the model so image dimensions stay scale-invariant
# (the masks must be pixel-aligned across model_scale to compare).
margin = 20.0 * float(args.get("model_scale", 1.0))
width_world = (u_max - u_min) + 2 * margin
height_world = (v_max - v_min) + 2 * margin
ortho_scale = max(width_world, height_world)
image_height = int(args.get("image_height", 800))
image_width = int(round(width_world * image_height / height_world))

center3d = sum(bbox, mathutils.Vector((0, 0, 0))) / len(bbox)
diag = mathutils.Vector((
    max(c.x for c in bbox) - min(c.x for c in bbox),
    max(c.y for c in bbox) - min(c.y for c in bbox),
    max(c.z for c in bbox) - min(c.z for c in bbox),
)).length

dist = diag * float(args["cam_mult"])
cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = ortho_scale
cam_data.clip_start = max(0.001, diag * args["clip_start_mult"]) if "clip_start_mult" in args else max(0.001, dist - diag * 2)
cam_data.clip_end = diag * args["clip_end_mult"] if "clip_end_mult" in args else (dist + diag * 2)
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = center3d + cam_dir * dist

fwd = (center3d - cam_obj.location).normalized()
cr = fwd.cross(world_up).normalized()
cu = cr.cross(fwd).normalized()
cam_obj.rotation_mode = "QUATERNION"
cam_obj.rotation_quaternion = mathutils.Matrix((cr, cu, -fwd)).transposed().to_4x4().to_quaternion()
uc = sum(c.dot(cr) for c in bbox) / len(bbox)
vc = sum(c.dot(cu) for c in bbox) / len(bbox)
cam_obj.location += cr * ((u_min + u_max) / 2 - uc) + cu * ((v_min + v_max) / 2 - vc)

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = max(image_width, 1)
scene.render.resolution_y = image_height
scene.render.resolution_percentage = 100
scene.render.use_freestyle = True
out_svg = Path(args["out_svg"])
stem = out_svg.parent / (out_svg.stem + "_b")
scene.render.filepath = str(stem)

fss = scene.view_layers[0].freestyle_settings
if "crease_angle" in args:
    fss.crease_angle = float(args["crease_angle"])
if "use_culling" in args:
    fss.use_culling = bool(args["use_culling"])
ls = fss.linesets[0]
for a in ("select_silhouette", "select_crease", "select_material_boundary",
          "select_contour", "select_external_contour", "select_border"):
    setattr(ls, a, True)
ls.visibility = args.get("visibility", "VISIBLE")
ls.qi_start = int(args.get("qi_start", 0))
ls.qi_end = int(args.get("qi_end", 100))
ls.linestyle.thickness = 1.5
ls.linestyle.use_export_strokes = True
ls.linestyle.use_export_fills = False

scene.svg_export.use_svg_export = True
scene.svg_export.mode = "FRAME"
scene.svg_export.object_fill = False
scene.svg_export.split_at_invisible = bool(args.get("split_at_invisible", False))
scene.svg_export.line_join_type = "ROUND"

bpy.ops.render.render(write_still=False)
produced = stem.parent / (stem.name + "{:04d}.svg".format(scene.frame_current))
if not produced.exists():
    print("ERROR no svg")
    sys.exit(1)
produced.replace(out_svg)
print("WROTE", out_svg)
