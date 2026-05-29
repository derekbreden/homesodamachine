"""Blender scene script — runs inside Blender's bundled Python.

Invoked by `_blender_render.py` via:

    blender --background --python _blender_scene.py -- <args.json>

Imports the appliance STL, renders an iso projection with Freestyle for
strokes, then injects each marking's colored disc fill (clipped by the
projected silhouette of its occluding part) into the resulting SVG.

Args (see _blender_render.py for the producer):
    appliance_stl: str
    markings: list of {id: str, disc: {center, axis, radius},
        color: [r, g, b], clip_stl: str}
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

# Freestyle's visibility raycast loses precision on geometry that's
# hundreds of units across (the model is in mm), dropping silhouette
# edges unpredictably with camera distance. Rendering at ~unit scale
# (mm → m) keeps the raycast stable, so every edge survives regardless
# of camera distance. All geometry entering the scene — appliance,
# coupler, disc — is scaled by this same factor.
MODEL_SCALE = 0.001

bpy.ops.wm.stl_import(filepath=args["appliance_stl"])
appliance = bpy.context.selected_objects[0]
appliance.name = "appliance"
appliance.scale = (MODEL_SCALE, MODEL_SCALE, MODEL_SCALE)
bpy.context.view_layer.objects.active = appliance
bpy.ops.object.transform_apply(scale=True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.01 * MODEL_SCALE)
bpy.ops.object.mode_set(mode="OBJECT")

bbox_corners = [
    appliance.matrix_world @ mathutils.Vector(c) for c in appliance.bound_box
]

view = args["view"]
u_min, v_min, u_max, v_max = projected_bbox(bbox_corners, view)
margin = float(args.get("margin", 20.0)) * MODEL_SCALE
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
cam_obj.location = center3d + cam_dir * (diag * 3.0)

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

# Mirror the view horizontally so the right-side face (carrying the CO2
# port) reads on the viewer's left. A negative X scale on the camera is a
# reflection — it can't come from the rotation, which is why it lives
# here. Freestyle strokes and the disc (projected through this same
# camera by world_to_camera_view) both land in the mirrored frame, so
# nothing downstream has to flip anything.
cam_obj.scale.x = -1.0
bpy.context.view_layer.update()


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

_thickness = float(args.get("stroke_width", 1.5))
fss = scene.view_layers[0].freestyle_settings
ls = fss.linesets[0]
ls.select_silhouette = True
ls.select_crease = True
ls.select_material_boundary = True
ls.select_contour = True
ls.select_external_contour = True
ls.select_border = True
ls.visibility = "VISIBLE"
ls.linestyle.thickness = _thickness
ls.linestyle.use_export_strokes = True
ls.linestyle.use_export_fills = False

scene.svg_export.use_svg_export = True
scene.svg_export.mode = "FRAME"
scene.svg_export.object_fill = False
scene.svg_export.split_at_invisible = False
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


def _ring_to_d(coords):
    pts = list(coords)
    return "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"


def _polygon_to_d(poly):
    rings = [poly.exterior] + list(poly.interiors)
    return " ".join(_ring_to_d(r.coords) for r in rings)


# Markings arrive in mm; scale them by the same MODEL_SCALE as the
# appliance so they project through the same camera consistently.
try:
    from shapely.geometry import Polygon as _Polygon
    from shapely.ops import unary_union as _unary_union
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "shapely"], check=True)
    from shapely.geometry import Polygon as _Polygon
    from shapely.ops import unary_union as _unary_union


def _clip_silhouette_d(clip_stl):
    """Exact silhouette of the clip part: project every mesh triangle to
    2D and union them. The union follows concavities, so the clip
    removes only the disc area the part actually covers."""
    bpy.ops.wm.stl_import(filepath=clip_stl)
    obj = bpy.context.selected_objects[0]
    obj.scale = (MODEL_SCALE, MODEL_SCALE, MODEL_SCALE)
    bpy.context.view_layer.update()
    mw = obj.matrix_world
    verts2d = [_project_to_svg(mw @ v.co) for v in obj.data.vertices]
    tris = []
    for face in obj.data.polygons:
        ring = [verts2d[i] for i in face.vertices]
        if len(ring) >= 3:
            p = _Polygon(ring)
            if p.is_valid and p.area > 1e-6:
                tris.append(p)
    footprint = _unary_union(tris).buffer(0.25).buffer(-0.25)
    if footprint.geom_type == "Polygon":
        return _polygon_to_d(footprint)
    return " ".join(_polygon_to_d(p) for p in footprint.geoms)


_clip_outer = "M-100000,-100000 L100000,-100000 L100000,100000 L-100000,100000 Z"
_all_defs = []
_all_paths = []
for _mk in args["markings"]:
    _disc = _mk["disc"]
    _disc_center = mathutils.Vector(_disc["center"]) * MODEL_SCALE
    _disc_axis = mathutils.Vector(_disc["axis"])
    _disc_pts = _circle_in_plane(
        _disc_center, _disc_axis, float(_disc["radius"]) * MODEL_SCALE, 96
    )
    _disc_d = _loop_svg_d(_disc_pts)

    _sil_d = _clip_silhouette_d(_mk["clip_stl"])
    _clip_id = f"{_mk['id']}-clip-{view}"
    _all_defs.append(
        f'<clipPath id="{_clip_id}" clipPathUnits="userSpaceOnUse">'
        f'<path clip-rule="evenodd" d="{_clip_outer} {_sil_d}"/>'
        f'</clipPath>'
    )
    # Project the port-hole target (the coupling/tube hole out at the
    # proud end) so a consumer can aim at the hole rather than the wall
    # disc; stamp it on the path as data-target in SVG coordinates.
    _data_target = ""
    _target = _disc.get("target")
    if _target is not None:
        _tpx, _tpy = _project_to_svg(mathutils.Vector(_target) * MODEL_SCALE)
        _data_target = f' data-target="{_tpx:.3f},{_tpy:.3f}"'
    # Fill AND outline come from this one path: the colored fill plus a
    # black stroke for the disc's outer edge. The clip part's own
    # Freestyle strokes draw the inner boundary where it bites into the
    # disc.
    _r, _g, _b = _mk["color"]
    _all_paths.append(
        f'<path fill-rule="evenodd" fill-opacity="1.0" fill="rgb({_r}, {_g}, {_b})" '
        f'stroke="rgb(0, 0, 0)" stroke-width="{_thickness}"{_data_target} '
        f'clip-path="url(#{_clip_id})" d="{_disc_d}" />'
    )

_clip_defs = "<defs>" + "".join(_all_defs) + "</defs>"
_discs_svg = "\n        ".join(_all_paths)

import re as _re
_svg_text = out_svg.read_text()
_svg_text = _re.sub(
    r'(<svg\b[^>]*>)',
    r'\1' + _clip_defs,
    _svg_text,
    count=1,
)
_svg_text = _svg_text.replace(
    '</g>', f'    {_discs_svg}\n        </g>', 1,
)

out_svg.write_text(_svg_text)

print(f"WROTE {out_svg}")
