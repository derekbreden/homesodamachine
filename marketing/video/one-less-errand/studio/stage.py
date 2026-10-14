"""Photograph the current appliance in a deterministic, animated Blender scene.

Run with Blender's Python; see README.md. Geometry and firmware artwork are
shared with the homepage's manual kitchen renderer. Staging, ice and fluids
are illustrations. Each shot owns its local clock, lens and camera move.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
import random
import runpy
import sys
import time

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument("--shots", nargs="+")
parser.add_argument("--stills", action="store_true")
parser.add_argument("--fps", type=int, default=24)
parser.add_argument("--width", type=int, default=1920)
parser.add_argument("--samples", type=int, default=40)
parser.add_argument("--engine", choices=["CYCLES", "BLENDER_EEVEE"], default="CYCLES")
parser.add_argument("--start-frame", type=int, default=0)
parser.add_argument("--end-frame", type=int)
parser.add_argument("--out", type=Path, default=HERE / "out")
parser.add_argument("--frames-root", type=Path)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
args.out.mkdir(parents=True, exist_ok=True)
story = json.loads((HERE / "story.json").read_text())

# The shared art tool builds a complete, accurately scaled assembly without
# producing any of its homepage stills.
saved_argv = sys.argv
sys.argv = [str(ROOT / "tools/render/render-kitchen-scene.py"), "--", "--scene-only", "--out", str(args.out)]
g = runpy.run_path(sys.argv[0])
sys.argv = saved_argv
scene, camera = g["scene"], g["camera"]
mat, box, tube, lathe = (g[k] for k in ("material", "box", "tube", "lathe"))
original_objects = list(scene.objects)
original_solids = [o for o in original_objects if o.type not in {"LIGHT", "CAMERA"}]
kitchen_lights = [o for o in original_objects if o.type == "LIGHT"]
scene.render.engine = args.engine
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = 0.025
scene.cycles.use_animated_seed = False
scene.cycles.seed = 42
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 6
scene.render.use_persistent_data = True
scene.render.film_transparent = False
scene.render.resolution_x = args.width
scene.render.resolution_y = round(args.width * 9 / 16)
scene.render.resolution_percentage = 100
scene.render.fps = args.fps
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.16
if args.engine == "BLENDER_EEVEE":
    scene.eevee.taa_render_samples = max(32, args.samples)
    scene.eevee.use_raytracing = True

camera.data.type = "PERSP"
camera.data.sensor_width = 36
camera.data.clip_start = 0.005
camera.data.clip_end = 50
camera.data.dof.use_dof = True
camera.data.dof.aperture_blades = 9

def ease(x):
    p = max(0, min(1, x))
    return p * p * (3 - 2 * p)

def lerp(a, b, p):
    return a + (b - a) * p

def blend(a, b, p):
    return tuple(lerp(x, y, p) for x, y in zip(a, b))

def pose(position, target, lens=65, aperture=7.1):
    camera.location = position
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens
    camera.data.dof.focus_distance = (Vector(target) - camera.location).length
    camera.data.dof.aperture_fstop = aperture

def show(objects):
    for obj in objects:
        if obj.hide_render:
            obj.hide_render = False

faucet = g["faucet_objects"]
screen = g["screen"]
display_node = next(n for n in g["screen_mat"].node_tree.nodes if n.type == "TEX_IMAGE")
g["screen_mat"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = .65
flavor_one, flavor_two = g["flavor_texture"](0), g["tex"]
glass_objects = [o for o in original_solids if o.name.startswith("Tiny carbonation") or o.name in {
    "Cold soda glass", "Soda in the glass", "Clear soda pour", "Separate flavor pour"}]
water = bpy.data.objects["Soda in the glass"]
streams = [bpy.data.objects[n] for n in ("Clear soda pour", "Separate flavor pour")]
base_glass_at = Vector(g["glass_at"])
glass_x, glass_y, glass_z = base_glass_at
lever = next(o for o in faucet if o.name == "lever")
lever_origin = lever.location.copy()
pivot = Vector((0, 0, 0.046))
for vertex in lever.data.vertices:
    vertex.co -= pivot
lever.location += pivot

# Clear liquid, small actual air inclusions, and a thin meniscus retain the
# optical character of soda without making it look like opaque orange juice.
soda = g["soda"]
water.data.materials.clear()
water.data.materials.append(soda)
for old_bubble in [o for o in glass_objects if o.name.startswith("Tiny carbonation")]:
    glass_objects.remove(old_bubble)
    original_solids.remove(old_bubble)
    bpy.data.objects.remove(old_bubble, do_unlink=True)

rng = random.Random(601)
extras_start = set(scene.objects)
ice_mat = mat("Clear ice with a cool edge", "#EEF9FF", 0.08, transmission=1, ior=1.31)
ice_list = []
for i, (x, y, z) in enumerate([(-.012, -.005, .018), (.010, .005, .034), (-.005, .008, .050)]):
    ice = box(f"Slow turning ice {i}", (.023, .022, .023), (glass_x + x, glass_y + y, glass_z + z), ice_mat, .0032, 5)
    ice.rotation_euler = (.18 + i * .48, -.13 + i * .24, i * .72)
    ice_list.append((ice, ice.location.copy(), ice.rotation_euler.copy()))

drop_mat = mat("Condensation water", "#FFFFFF", 0.035, transmission=1, ior=1.333)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1)
sphere = bpy.context.object
sphere.name = "Condensation master"
g["smooth"](sphere)
droplet_mesh = sphere.data
bpy.data.objects.remove(sphere, do_unlink=True)
condensation = []
for i in range(135):
    angle, z = rng.uniform(0, math.tau), rng.uniform(.009, .100)
    radius = .030 + .0045 * z / .120
    drop = bpy.data.objects.new(f"Cold glass droplet {i}", droplet_mesh)
    scene.collection.objects.link(drop)
    drop.location = (glass_x + radius * math.cos(angle), glass_y + radius * math.sin(angle), glass_z + z)
    size = rng.uniform(.00027, .00085)
    drop.scale = (size, size, size * rng.uniform(1.05, 1.45))
    if not drop.data.materials:
        drop.data.materials.append(drop_mat)
    condensation.append(drop)

bubbles = []
bubble_mesh = droplet_mesh.copy()
bubble_mesh.materials.clear()
bubble_mesh.materials.append(g["bubble_mat"])
for i in range(140):
    angle = rng.uniform(0, math.tau)
    radius = rng.uniform(.008, .027)
    bubble = bpy.data.objects.new(f"Rising carbonation {i}", bubble_mesh)
    scene.collection.objects.link(bubble)
    size = rng.uniform(.00016, .00047)
    bubble.scale = (size, size, size)
    bubbles.append((bubble, math.cos(angle) * radius, math.sin(angle) * radius, rng.random(), rng.uniform(.008, .019)))
glass_details = [o for o in scene.objects if o not in extras_start]

# The home is quiet and architectural: pale stone, warm cabinetry and one
# soft window. Its secondary sink faucet keeps the dedicated soda tap legible.
before_room = set(scene.objects)
wall_mat = mat("Warm mineral plaster", "#E3DFD6", .88)
oak_mat = g["oak"]
box("Kitchen plaster wall", (4.8, .06, 2.8), (0, .58, 1.35), wall_mat, 0)
box("Kitchen counter extension left", (1.5, .72, .032), (-1.235, .015, .814), g["stone"], .005)
box("Kitchen counter extension right", (1.5, .72, .032), (1.235, .015, .814), g["stone"], .005)
box("Left oak drawers", (1.48, .62, .76), (-1.235, .03, .426), oak_mat, .004)
box("Right oak drawers", (1.48, .62, .76), (1.235, .03, .426), oak_mat, .004)
for x in (-1.235, 1.235):
    for z in (.255, .505, .758):
        box("Precise drawer reveal", (1.475, .002, .002), (x, -.282, z), g["black_rubber"], 0)
box("Quiet oak shelf", (1.8, .20, .025), (.25, .48, 1.46), oak_mat, .003)
ceramic = mat("Warm ceramic", "#C1B39E", .69)
lathe("Kitchen ceramic carafe", [(0,0),(.039,0),(.046,.008),(.041,.12),(.026,.16),(.026,.195),(.022,.197),(.022,.16),(.036,.115),(.034,.012),(0,.012)], ceramic, (.85,.43,1.472))
lathe("Small ceramic cup", [(0,0),(.03,0),(.035,.006),(.035,.075),(.032,.077),(.031,.008),(0,.008)], ceramic, (.69,.42,1.472))
room_objects = [o for o in scene.objects if o not in before_room]

door_parents = []
doors = []
for side in (-1, 1):
    hinge = bpy.data.objects.new("Cabinet door hinge", None)
    scene.collection.objects.link(hinge)
    hinge.location = (side * .431, -.313, .426)
    door = box("Cabinet front", (.426, .019, .735), (0,0,0), oak_mat, .0025)
    door.parent = hinge
    door.location = (-side * .213, -.006, 0)
    doors.append(door)
    door_parents.append(hinge)

# The alternative design uses its own assembly, the same real finish, and
# the same mapped physical panel. No geometry is invented for the beauty cut.
white = mat("White faucet catalog finish", (.8713671192, .8713671192, .8559926082), .85)
industrial = g["payload"]("hardware/faucet-layout/faucet-industrial-assembly.step.mesh",
    lambda name: name in g["visible_faucet"],
    lambda entry: g["screen_mat"] if entry["name"] == "faucet_display_screen" else
                  g["glass_dark"] if entry["name"] == "faucet_display" else white,
    g["faucet_at"], clip_floor=-6)
industrial_screen = next(o for o in industrial if o.name.startswith("faucet_display_screen"))
uv = industrial_screen.data.uv_layers.new(name="Physical screen UV")
for polygon in industrial_screen.data.polygons:
    for index in polygon.loop_indices:
        vertex = industrial_screen.data.vertices[industrial_screen.data.loops[index].vertex_index].co
        uv.data[index].uv = ((vertex.x + .00888) / .01776, (vertex.z - .19962) / (.2251 - .19962))

spec = importlib.util.spec_from_file_location("film_errands", HERE / "errands.py")
errand_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(errand_module)
errands = errand_module.create(g)
lighting_spec = importlib.util.spec_from_file_location("film_lighting", HERE / "lighting.py")
lighting_module = importlib.util.module_from_spec(lighting_spec)
lighting_spec.loader.exec_module(lighting_module)
lighting = lighting_module.create(g)

# Each shot is rendered in its own Blender lifetime. Keep only its set in
# memory: hidden cabinet and regulator meshes have no part in can or studio
# photography, and need not occupy the shared host's render memory.
requested = set(args.shots or [s["id"] for s in story["scenes"]])
studio_shots = {"wish", "select", "lever", "pour", "fizz", "sculpted", "industrial"}
keep = None
if requested and requested <= {"can", "case", "carry", "shelf"}:
    keep = set(errands.objects + [camera])
elif requested and requested <= studio_shots:
    keep = set(faucet + industrial + glass_objects + glass_details + lighting.objects
               + door_parents + [camera, g["detail_counter"]]
               + [o for o in scene.objects if o.type == "LIGHT"])
if keep is not None:
    for obj in list(scene.objects):
        if obj not in keep:
            bpy.data.objects.remove(obj, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)

all_solids = [o for o in scene.objects if o.type not in {"CAMERA", "LIGHT"}]
all_lights = [o for o in scene.objects if o.type == "LIGHT"]
last_shot = None

def fluid(t, level, flowing=False):
    height = .006 + .104 * max(.025, level)
    water.hide_render = level <= 0
    water.scale.z = (height - .006) / .081
    water.location.z = glass_z + .006 * (1 - water.scale.z)
    for i, (ice, location, rotation) in enumerate(ice_list):
        ice.location = location
        ice.location.z += max(0, height - .048) * (.82 + i * .05)
        ice.rotation_euler = (rotation.x + .025 * math.sin(t*.75+i), rotation.y + .02*math.sin(t*.6+i), rotation.z + .025*math.sin(t*.5+i))
    for bubble, x, y, phase, speed in bubbles:
        z = .008 + ((phase*.098 + t*speed) % .098)
        bubble.location = (glass_x + x + .0005*math.sin(t*1.8+phase*12), glass_y+y, glass_z+z)
        bubble.hide_render = z > height - .002
    for i, stream in enumerate(streams):
        stream.hide_render = not flowing
        handles = stream.data.splines[0].bezier_points
        for j, h in enumerate(handles):
            fraction = j / (len(handles)-1)
            h.co.z = lerp(g["counter_top"]+.185, glass_z+height+.001, fraction)
            h.co.x = glass_x - i*.0032 + .00043*math.sin(t*10+fraction*7+i)*fraction
            h.co.y = lerp(-.100-i*.003, glass_y-i*.001, fraction) + .0006*math.sin(t*7+fraction*6)*fraction
        stream.data.bevel_depth = (.0016 if i == 0 else .0004) * (1 + .045*math.sin(t*19+i))
    lever.rotation_euler.x = .23 if flowing else 0

def draw(shot, t, duration):
    global last_shot
    p = ease(t / duration)
    if last_shot != shot:
        for obj in all_solids + all_lights:
            obj.hide_render = True
        scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (*g["linear"]("#E7EEF8"),1)
        scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .16
    last_shot = shot
    if shot in {"can", "case", "carry", "shelf"}:
        errands.draw(shot, t, duration)
        return
    if shot != "select" and display_node.image != flavor_two:
        display_node.image = flavor_two
    for hinge in door_parents:
        hinge.rotation_euler.z = 0
    if shot in {"wish", "fizz"}:
        show(glass_objects + glass_details)
        fluid(t, .95)
        if shot == "wish":
            pose(blend((.422,-.540,1.040),(.407,-.521,1.034),p), (.214,-.143,.895), 65, 7.1)
        else:
            pose(blend((.325,-.367,.976),(.313,-.353,.974),p), (.214,-.143,.922), 95, 8)
    elif shot in {"kitchen", "home", "under"}:
        show(original_solids + glass_details + room_objects + doors)
        g["detail_counter"].hide_render = True
        fluid(t, 0 if shot != "home" else .95)
        if shot == "under":
            for side, hinge in zip((-1,1),door_parents):
                hinge.rotation_euler.z = side * math.radians(104) * ease((t-.15)/1.3)
            pose(blend((1.05,-2.15,1.45),(.83,-1.73,1.08),p), blend((0,.005,.55),(.0,-.01,.37),p), 45, 11)
        elif shot == "kitchen":
            pose(blend((.84,-1.22,1.320),(.59,-.87,1.210),p),
                 blend((.060,.020,.985),(.125,-.015,.985),p), lerp(48,52,p), 8)
        else:
            pose(blend((.68,-.97,1.235),(.72,-1.02,1.245),p), (.105,.007,.972), 51, 8)
    elif shot in {"select", "lever", "pour"}:
        show(faucet)
        if shot == "select":
            selected_image = flavor_one if t < 1.65 else flavor_two
            if display_node.image != selected_image:
                display_node.image = selected_image
            pose(blend((.352,-.456,1.163),(.340,-.438,1.157),p), (.214,-.100,1.040), 90, 7.1)
            lever.rotation_euler.x = 0
        elif shot == "lever":
            pose(blend((.430,-.416,.939),(.409,-.400,.934),p), (.214,-.004,.888), 90, 7.1)
            lever.rotation_euler.x = .23 * ease((t-.55)/.28)
        else:
            show(glass_objects + glass_details)
            fluid(t, .95*ease((t-.10)/6.5), flowing=t>=.1 and t<6.8)
            sculpted_lever = .23 * (1-ease((t-6.8)/.2))
            lever.rotation_euler.x = sculpted_lever
            pose(blend((.680,-.900,1.208),(.655,-.870,1.198),p), (.213,-.067,.951), 65, 9)
    elif shot in {"sculpted", "industrial"}:
        show(faucet if shot == "sculpted" else industrial)
        lever.rotation_euler.x = 0
        pose(blend((.790,-.970,1.205),(.745,-.962,1.198),p), (.214,-.035,.969), 65, 8)
    lighting.draw(shot,t,duration)
    bpy.context.view_layer.update()

shots = [s for s in story["scenes"] if s["id"] not in {"reset", "closing"} and (not args.shots or s["id"] in args.shots)]
print(f"FILM_DEVICE {scene.cycles.device}",flush=True)
for shot in shots:
    name, duration = shot["id"], shot["end"] - shot["start"]
    frames = [(round(duration*.54*args.fps), duration*.54)] if args.stills else [(i,i/args.fps) for i in range(args.start_frame,min(round(duration*args.fps), args.end_frame if args.end_frame is not None else 10**9))]
    directory = args.out / "stills" if args.stills else (args.frames_root or args.out / "frames") / name
    directory.mkdir(parents=True,exist_ok=True)
    for number, t in frames:
        target = directory / (f"{name}.png" if args.stills else f"{number:05}.png")
        if target.exists() and not args.stills:
            continue
        started = time.monotonic()
        scene.frame_set(number)
        draw(name,t,duration)
        scene.render.filepath = str(target)
        print(f"FILM {name} {number}/{round(duration*args.fps)}",flush=True)
        bpy.ops.render.render(write_still=True)
        print(f"FILM_FRAME {name} {number} {time.monotonic()-started:.2f}s",flush=True)
    print(f"FILM_SHOT {name} completed",flush=True)
