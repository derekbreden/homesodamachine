"""Blender scene script — runs inside Blender's bundled Python.

Invoked by `_blender_render.py` via:

    blender --background --python _blender_scene.py -- <args.json>

Imports the appliance STL, renders an iso projection with Freestyle for
strokes, then injects a red disc fill at the CO2 port (clipped by the
coupler's projected silhouette) into the resulting SVG.

Args (see _blender_render.py for the producer):
    appliance_stl: str
    disc_params: {center: [x,y,z], axis: [x,y,z], radius: float}
    coupler_params: {base, axis, hex_length, hex_circumradius,
                     body_length, body_radius}
    out_svg: str
    view: "front" | "back"
    image_height, stroke_width, margin
"""
import json
import math
import sys
from pathlib import Path

import bpy
import addon_utils
import mathutils


args_path = Path(sys.argv[sys.argv.index("--") + 1])
args = json.loads(args_path.read_text())


# ---------------------------------------------------------------------------
# Iso projection geometry
# ---------------------------------------------------------------------------
#
# The CAD model is +Z-up (height along +Z). Camera at a corner of a cube
# centered on the scene, looking at origin with world +Z as the up hint:
#
#   front: camera at (+x, -y, +z) — sees front (-Y), right (+X), top (+Z)
#   back:  camera at (+x, +y, +z) — sees back (+Y),  right (+X), top (+Z)

ISO_DIRECTIONS = {
    "front": mathutils.Vector((1, -1, 1)).normalized(),
    "back": mathutils.Vector((1, 1, 1)).normalized(),
}


def projected_bbox(corners, view):
    """2D (u_min, v_min, u_max, v_max) of `corners` projected by the
    iso camera for `view`."""
    cam_dir = ISO_DIRECTIONS[view]
    forward = -cam_dir
    world_up = mathutils.Vector((0, 0, 1))
    right = forward.cross(world_up).normalized()
    up = right.cross(forward).normalized()
    us = [c.dot(right) for c in corners]
    vs = [c.dot(up) for c in corners]
    return min(us), min(vs), max(us), max(vs)


# ---------------------------------------------------------------------------
# Build the scene
# ---------------------------------------------------------------------------

addon_utils.enable("bl_ext.blender_org.freestyle_svg_exporter")

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.wm.stl_import(filepath=args["appliance_stl"])
appliance = bpy.context.selected_objects[0]
appliance.name = "appliance"
bpy.context.view_layer.objects.active = appliance
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
# Threshold loose enough to bridge CadQuery tessellation rounding
# (coords to ~10⁻⁴ mm; 0.01 mm well below smallest real feature).
bpy.ops.mesh.remove_doubles(threshold=0.01)
bpy.ops.object.mode_set(mode="OBJECT")

white_mat = bpy.data.materials.new(name="white")
white_mat.diffuse_color = (1.0, 1.0, 1.0, 1.0)
appliance.data.materials.append(white_mat)

bbox_corners = [
    appliance.matrix_world @ mathutils.Vector(c) for c in appliance.bound_box
]

view = args["view"]
u_min, v_min, u_max, v_max = projected_bbox(bbox_corners, view)
margin = float(args.get("margin", 20.0))
width_world = (u_max - u_min) + 2 * margin
height_world = (v_max - v_min) + 2 * margin
ortho_scale = max(width_world, height_world)

image_height = int(args.get("image_height", 800))
scale_px_per_world = image_height / height_world
image_width = int(round(width_world * scale_px_per_world))


# ---------------------------------------------------------------------------
# Camera — orthographic iso
# ---------------------------------------------------------------------------

cam_dir = ISO_DIRECTIONS[view]
center3d = sum(bbox_corners, mathutils.Vector((0, 0, 0))) / len(bbox_corners)
diag = (
    mathutils.Vector(
        (
            max(c.x for c in bbox_corners) - min(c.x for c in bbox_corners),
            max(c.y for c in bbox_corners) - min(c.y for c in bbox_corners),
            max(c.z for c in bbox_corners) - min(c.z for c in bbox_corners),
        )
    )
).length

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = ortho_scale
cam_data.clip_start = diag * 0.5
cam_data.clip_end = diag * 10
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
cam_obj.location = center3d + cam_dir * (diag * 3)

forward = (center3d - cam_obj.location).normalized()
world_up = mathutils.Vector((0, 0, 1))
cam_right = forward.cross(world_up).normalized()
cam_up = cam_right.cross(forward).normalized()
rot_mat = mathutils.Matrix((cam_right, cam_up, -forward)).transposed().to_4x4()
cam_obj.rotation_mode = "QUATERNION"
cam_obj.rotation_quaternion = rot_mat.to_quaternion()

u_centroid = sum(c.dot(cam_right) for c in bbox_corners) / len(bbox_corners)
v_centroid = sum(c.dot(cam_up) for c in bbox_corners) / len(bbox_corners)
u_center = (u_min + u_max) / 2
v_center = (v_min + v_max) / 2
cam_obj.location += cam_right * (u_center - u_centroid)
cam_obj.location += cam_up * (v_center - v_centroid)


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = max(image_width, 1)
scene.render.resolution_y = max(image_height, 1)
scene.render.resolution_percentage = 100
scene.render.use_freestyle = True
scene.render.image_settings.file_format = "PNG"
out_svg = Path(args["out_svg"])
tmp_stem = out_svg.parent / (out_svg.stem + "_blender")
scene.render.filepath = str(tmp_stem)

fss = scene.view_layers[0].freestyle_settings
ls = fss.linesets[0]
ls.select_silhouette = True
ls.select_crease = True
ls.select_material_boundary = True
ls.select_contour = True
ls.select_external_contour = True
ls.select_border = True
ls.visibility = "VISIBLE"
ls.linestyle.thickness = float(args.get("stroke_width", 1.5))
ls.linestyle.use_export_strokes = True
ls.linestyle.use_export_fills = False

scene.svg_export.use_svg_export = True
scene.svg_export.mode = "FRAME"
scene.svg_export.object_fill = False
scene.svg_export.split_at_invisible = True
scene.svg_export.line_join_type = "ROUND"

bpy.ops.render.render(write_still=False)

produced = tmp_stem.parent / (tmp_stem.name + "{:04d}.svg".format(scene.frame_current))
if not produced.exists():
    print(f"ERROR: expected SVG at {produced} not found")
    sys.exit(1)
produced.replace(out_svg)


# ---------------------------------------------------------------------------
# Red disc + coupler silhouette clip
# ---------------------------------------------------------------------------

from bpy_extras.object_utils import world_to_camera_view


def _project_to_svg(world_pt):
    cam_coord = world_to_camera_view(scene, cam_obj, world_pt)
    sx = cam_coord.x * scene.render.resolution_x
    sy = (1.0 - cam_coord.y) * scene.render.resolution_y
    return sx, sy


def _circle_in_plane(center, axis, radius, n):
    axis = axis.normalized()
    u_hint = mathutils.Vector((0.0, 0.0, 1.0)) if abs(axis.z) < 0.9 else mathutils.Vector((1.0, 0.0, 0.0))
    u = axis.cross(u_hint).normalized()
    v = axis.cross(u).normalized()
    return [
        center + u * (radius * math.cos(2.0 * math.pi * i / n)) + v * (radius * math.sin(2.0 * math.pi * i / n))
        for i in range(n)
    ]


def _loop_svg_d(world_points):
    parts = []
    for i, pt in enumerate(world_points):
        sx, sy = _project_to_svg(pt)
        parts.append(f"{'M' if i == 0 else 'L'}{sx:.3f},{sy:.3f}")
    parts.append("Z")
    return "".join(parts)


def _convex_hull_2d(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


_disc_params = args["disc_params"]
_disc_center = mathutils.Vector(_disc_params["center"])
_disc_axis = mathutils.Vector(_disc_params["axis"])
_disc_pts = _circle_in_plane(_disc_center, _disc_axis, float(_disc_params["radius"]), 96)
_disc_d = _loop_svg_d(_disc_pts)

_coupler = args["coupler_params"]
_base = mathutils.Vector(_coupler["base"])
_axis = mathutils.Vector(_coupler["axis"]).normalized()
_hex_back = _base
_hex_front = _base + _axis * float(_coupler["hex_length"])
_cup_back = _hex_front
_cup_front = _hex_front + _axis * float(_coupler["body_length"])

_pts_3d = []
for center in (_hex_back, _hex_front):
    _pts_3d += _circle_in_plane(center, _axis, float(_coupler["hex_circumradius"]), 6)
for center in (_cup_back, _cup_front):
    _pts_3d += _circle_in_plane(center, _axis, float(_coupler["body_radius"]), 48)
_pts_2d = [_project_to_svg(p) for p in _pts_3d]
_coupler_hull = _convex_hull_2d(_pts_2d)
_coupler_silhouette_d = "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in _coupler_hull) + " Z"

_clip_id = f"co2-coupler-clip-{view}"
_clip_outer = "M-100000,-100000 L100000,-100000 L100000,100000 L-100000,100000 Z"
_clip_defs = (
    f'<defs>'
    f'<clipPath id="{_clip_id}" clipPathUnits="userSpaceOnUse">'
    f'<path clip-rule="evenodd" d="{_clip_outer} {_coupler_silhouette_d}"/>'
    f'</clipPath>'
    f'</defs>'
)

_disc_path = (
    f'<path fill-rule="evenodd" stroke="none" fill-opacity="1.0" '
    f'fill="rgb(255, 0, 0)" clip-path="url(#{_clip_id})" '
    f'd="{_disc_d}" />'
)

import re as _re
_svg_text = out_svg.read_text()
_svg_text = _re.sub(
    r'(<svg\b[^>]*>)',
    r'\1' + _clip_defs,
    _svg_text,
    count=1,
)
_svg_text = _svg_text.replace(
    '</g>', f'    {_disc_path}\n        </g>', 1,
)
out_svg.write_text(_svg_text)

print(f"WROTE {out_svg}")
