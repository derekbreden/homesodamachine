"""Standalone studio portrait of the Sculpted faucet and a cold citrus soda.

Run with Blender's Python. ``draw(shot, t, duration)`` evaluates an absolute
shot-local time, without a simulation cache or dependence on an earlier frame.
The drink and studio are illustrative. Faucet geometry and selected display
come directly from the project's CAD payload and firmware artwork.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import random
import sys
import time
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from cad import linear, material, payload, selected_display
from lighting import StudioLighting

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--shots", nargs="+")
parser.add_argument("--stills", action="store_true")
parser.add_argument("--fps", type=int, default=24)
parser.add_argument("--width", type=int, default=1920)
parser.add_argument("--samples", type=int, default=24)
parser.add_argument("--start-frame", type=int, default=0)
parser.add_argument("--end-frame", type=int)
parser.add_argument("--frames-root", type=Path)
parser.add_argument("--out", type=Path, default=HERE/"out")
args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
args.out.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.adaptive_threshold = .035
scene.cycles.use_animated_seed = False
scene.cycles.seed = 78
scene.cycles.max_bounces = 10
scene.cycles.transmission_bounces = 8
scene.cycles.transparent_max_bounces = 8
scene.render.use_persistent_data = True
scene.render.resolution_x = args.width
scene.render.resolution_y = round(args.width*9/16)
scene.render.resolution_percentage = 100
scene.render.fps = args.fps
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.render.threads_mode = "AUTO"
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
scene.view_settings.exposure = 0
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"
    prefs.get_devices()
    for device in prefs.devices:
        device.use = device.type == "METAL"
    if any(d.use for d in prefs.devices):
        scene.cycles.device = "GPU"
except (TypeError, RuntimeError):
    pass

camera = bpy.data.objects.new("Studio camera", bpy.data.cameras.new("Studio camera"))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.sensor_width = 36
camera.data.clip_start = .003
camera.data.clip_end = 30
camera.data.dof.use_dof = True
camera.data.dof.aperture_blades = 9


def smooth(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def mesh_object(name, vertices, faces, finish, location=(0, 0, 0)):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    obj.location = location
    mesh.materials.append(finish)
    return smooth(obj)


def lathe(name, profile, finish, at, segments=160):
    vertices, normals, faces = [], [], []
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
        length = math.hypot(r1-r0, z1-z0)
        radial, vertical = (z1-z0)/length, -(r1-r0)/length
        start = len(vertices)
        for r, z in ((r0, z0), (r1, z1)):
            for i in range(segments):
                angle = math.tau*i/segments
                vertices.append((r*math.cos(angle), r*math.sin(angle), z))
                normals.append((radial*math.cos(angle), radial*math.sin(angle), vertical))
        faces.extend((start+i, start+(i+1) % segments,
                      start+segments+(i+1) % segments, start+segments+i) for i in range(segments))
    obj = mesh_object(name, vertices, faces, finish, at)
    obj.data.normals_split_custom_set_from_vertices(normals)
    return obj


def ease(value):
    value = min(1., max(0., value))
    return value*value*(3-2*value)


def blend(a, b, amount):
    return tuple(x+(y-x)*amount for x, y in zip(a, b))


def pose(location, target, lens, focus, aperture):
    camera.location = location
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = lens
    camera.data.dof.focus_distance = (Vector(focus)-camera.location).length
    camera.data.dof.aperture_fstop = aperture


shell = material("Black PET-GF shell", "#0E1216", .66)
nodes, links = shell.node_tree.nodes, shell.node_tree.links
grain = nodes.new("ShaderNodeTexNoise")
grain.inputs["Scale"].default_value = 1450
grain.inputs["Detail"].default_value = 2
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = .10
bump.inputs["Distance"].default_value = .000008
links.new(grain.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], nodes.get("Principled BSDF").inputs["Normal"])
materials = {
    "shell": shell,
    "rubber": material("Black mounting elastomer", "#15191D", .88),
    "hardware": material("Retained black faucet hardware", "#202428", .56),
    "display_glass": material("Dark physical display cover", "#101A20", .17),
}
FAUCET_AT = Vector((.145, .045, 0))
faucet = payload(ROOT/"hardware/faucet-layout/faucet-assembly.step.mesh", scene, materials, FAUCET_AT)
selected_display(ROOT, faucet["faucet_display_screen"])
for obj in faucet.values():
    # Keep the appliance's silhouette out of the drink's optical path. Its
    # refracted housing would otherwise read as a dark solid in the soda.
    obj.visible_transmission = False
    obj.visible_glossy = False
lever = faucet["lever"]
lever_pivot = Vector((0, 0, .046))
for vertex in lever.data.vertices:
    vertex.co -= lever_pivot
lever.location += lever_pivot

GLASS_AT = Vector((.145, -.151, .0004))
glass_finish = material("Clear thin-walled tumbler", (1, 1, 1), .040, transmission=1, ior=1.46)
glass = lathe("Short everyday soda tumbler", [
    (0, 0), (.0285, 0), (.0334, .0007), (.0342, .0027),
    (.0350, .0090), (.0382, .0834), (.03835, .0851),
    (.03815, .0860), (.03765, .08645), (.03710, .08620),
    (.03685, .0855), (.03675, .0834), (.0335, .0090),
    (.0326, .0054), (.0285, .0048), (0, .0048),
], glass_finish, GLASS_AT)
def clean_liquid_surface(finish, tint, roughness, reflection=.72):
    """Photographic liquid optics: a clean transmitted image and soft glints.

    The glass supplies refraction. The drink's closed volume supplies colour;
    its surface carries the meniscus and animated disturbance without making
    another magnifying lens inside the tumbler.
    """
    nodes, links = finish.node_tree.nodes, finish.node_tree.links
    clear = nodes.new("ShaderNodeBsdfTransparent")
    clear.inputs["Color"].default_value = (*tint, 1)
    gloss = nodes.new("ShaderNodeBsdfAnisotropic")
    gloss.inputs["Color"].default_value = (1, 1, 1, 1)
    gloss.inputs["Roughness"].default_value = roughness
    fresnel = nodes.new("ShaderNodeFresnel")
    fresnel.inputs["IOR"].default_value = 1.333
    amount = nodes.new("ShaderNodeMath")
    amount.operation = "MULTIPLY"
    amount.inputs[1].default_value = reflection
    links.new(fresnel.outputs["Fac"], amount.inputs[0])
    mix = nodes.new("ShaderNodeMixShader")
    links.new(amount.outputs[0], mix.inputs[0])
    links.new(clear.outputs["BSDF"], mix.inputs[1])
    links.new(gloss.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], nodes.get("Material Output").inputs["Surface"])
    return gloss


soda = material("Transparent yellow-green citrus soda", (1, 1, 1))
clean_liquid_surface(soda, (.98, 1, .70), .050, .85)
absorption = soda.node_tree.nodes.new("ShaderNodeVolumeAbsorption")
absorption.inputs["Color"].default_value = (.92, .98, .06, 1)
absorption.inputs["Density"].default_value = 38
soda.node_tree.links.new(absorption.outputs["Volume"], soda.node_tree.nodes.get("Material Output").inputs["Volume"])
stream_water = material("Moving clear carbonated-water jet", (1, 1, 1))
jet_gloss = clean_liquid_surface(stream_water, (.985, .995, 1), .12, .92)
jet_nodes, jet_links = stream_water.node_tree.nodes, stream_water.node_tree.links
position = jet_nodes.new("ShaderNodeNewGeometry")
jet_noise = jet_nodes.new("ShaderNodeTexNoise")
jet_noise.noise_dimensions = "4D"
jet_noise.inputs["Scale"].default_value = 650
jet_noise.inputs["Detail"].default_value = 2
jet_links.new(position.outputs["Position"], jet_noise.inputs["Vector"])
jet_bump = jet_nodes.new("ShaderNodeBump")
jet_bump.inputs["Strength"].default_value = .28
jet_bump.inputs["Distance"].default_value = .000075
jet_links.new(jet_noise.outputs["Fac"], jet_bump.inputs["Height"])
jet_links.new(jet_bump.outputs["Normal"], jet_gloss.inputs["Normal"])
jet_output = jet_nodes.get("Material Output").inputs["Surface"]
jet_surface = jet_output.links[0].from_socket
jet_aeration = jet_nodes.new("ShaderNodeBsdfDiffuse")
jet_aeration.inputs["Color"].default_value = (.92, .97, 1, 1)
jet_aeration.inputs["Roughness"].default_value = .25
jet_mix = jet_nodes.new("ShaderNodeMixShader")
jet_mix.inputs[0].default_value = .085
jet_links.new(jet_surface, jet_mix.inputs[1])
jet_links.new(jet_aeration.outputs["BSDF"], jet_mix.inputs[2])
jet_links.new(jet_mix.outputs["Shader"], jet_output)
stream_flavor = material("Moving fine citrus-concentrate jet", (1, 1, 1))
clean_liquid_surface(stream_flavor, (.87, .98, .47), .12, .75)
condensation_finish = material("Clear cold-glass condensation", (1, 1, 1), .035, transmission=1, ior=1.333)
air = material("Fine bright carbonation rims", (1, 1, 1))
clean_liquid_surface(air, (1, 1, 1), .045, .9)
air_nodes, air_links = air.node_tree.nodes, air.node_tree.links
air_surface = air_nodes.get("Material Output").inputs["Surface"].links[0].from_socket
air_fresnel = air_nodes.new("ShaderNodeFresnel")
air_fresnel.inputs["IOR"].default_value = 1.333
air_strength = air_nodes.new("ShaderNodeMath")
air_strength.operation = "MULTIPLY"
air_strength.inputs[1].default_value = .85
air_links.new(air_fresnel.outputs["Fac"], air_strength.inputs[0])
air_glint = air_nodes.new("ShaderNodeEmission")
air_glint.inputs["Color"].default_value = (.80, .94, 1, 1)
air_links.new(air_strength.outputs[0], air_glint.inputs["Strength"])
air_add = air_nodes.new("ShaderNodeAddShader")
air_links.new(air_surface, air_add.inputs[0])
air_links.new(air_glint.outputs["Emission"], air_add.inputs[1])
air_links.new(air_add.outputs["Shader"], air_nodes.get("Material Output").inputs["Surface"])


def inner_radius(z):
    return .0335+(.03675-.0335)*min(1., max(0., (z-.009)/(.0834-.009)))


# The top is part of one closed dielectric volume, including its meniscus.
SURFACE_RINGS, SURFACE_SIDES = 40, 112
water_vertices = [(0, 0, .0049)]
water_vertices += [(.0327*math.cos(i*math.tau/SURFACE_SIDES),
                    .0327*math.sin(i*math.tau/SURFACE_SIDES), .0049) for i in range(SURFACE_SIDES)]
surface_start = len(water_vertices)
water_vertices.append((0, 0, .0715))
surface_data = [(0, 0, 0)]
for ring in range(1, SURFACE_RINGS+1):
    fraction = ring/SURFACE_RINGS
    for side in range(SURFACE_SIDES):
        angle = side*math.tau/SURFACE_SIDES
        water_vertices.append((fraction*.0362*math.cos(angle), fraction*.0362*math.sin(angle), .0715))
        surface_data.append((fraction, math.cos(angle), math.sin(angle)))
water_faces = [(0, 1+(i+1) % SURFACE_SIDES, 1+i) for i in range(SURFACE_SIDES)]
first_ring = surface_start+1
water_faces += [(surface_start, first_ring+i, first_ring+(i+1) % SURFACE_SIDES) for i in range(SURFACE_SIDES)]
for ring in range(SURFACE_RINGS-1):
    lower, upper = first_ring+ring*SURFACE_SIDES, first_ring+(ring+1)*SURFACE_SIDES
    water_faces += [(lower+i, upper+i, upper+(i+1) % SURFACE_SIDES, lower+(i+1) % SURFACE_SIDES)
                    for i in range(SURFACE_SIDES)]
outer_ring = first_ring+(SURFACE_RINGS-1)*SURFACE_SIDES
# Separate coincident wall and surface rings keep vertical wall normals out of
# the meniscus. A smoothed top-to-wall normal would make the drink a false lens.
side_start = len(water_vertices)
water_vertices += [(.0327*math.cos(i*math.tau/SURFACE_SIDES),
                    .0327*math.sin(i*math.tau/SURFACE_SIDES), .0049) for i in range(SURFACE_SIDES)]
side_top_start = len(water_vertices)
water_vertices += [water_vertices[outer_ring+i] for i in range(SURFACE_SIDES)]
water_faces += [(side_start+i, side_start+(i+1) % SURFACE_SIDES,
                 side_top_start+(i+1) % SURFACE_SIDES, side_top_start+i)
                for i in range(SURFACE_SIDES)]
liquid = mesh_object("Soda volume with continuous meniscus", water_vertices, water_faces, soda, GLASS_AT)

rng = random.Random(718)
bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=1)
master = bpy.context.object
drop_mesh = master.data
bpy.data.objects.remove(master, do_unlink=True)
for polygon in drop_mesh.polygons:
    polygon.use_smooth = True
drop_mesh.materials.append(condensation_finish)
for i in range(300):
    angle, z = rng.uniform(0, math.tau), rng.uniform(.010, .080)
    size = rng.uniform(.00015, .00048) if i % 3 else rng.uniform(.00048, .00090)
    radius = .035+.0032*(z-.009)/.0744
    drop = bpy.data.objects.new(f"Condensation bead {i:03}", drop_mesh)
    scene.collection.objects.link(drop)
    drop.location = GLASS_AT+Vector(((radius+size*.13)*math.cos(angle), (radius+size*.13)*math.sin(angle), z))
    drop.scale = (size*.44, size, size*rng.uniform(1.1, 1.75))
    drop.rotation_euler.z = angle
bubble_mesh = drop_mesh.copy()
bubble_mesh.materials.clear()
bubble_mesh.materials.append(air)
bubbles = []
for lane in range(30):
    angle = rng.uniform(-2.6, -.2) if lane < 18 else rng.uniform(0, math.tau)
    radius = rng.uniform(.024, .032) if lane < 18 else rng.uniform(.009, .030)
    speed = rng.uniform(.012, .023)
    for bead in range(25):
        obj = bpy.data.objects.new(f"Fine carbonation lane {lane:02} bead {bead:02}", bubble_mesh)
        scene.collection.objects.link(obj)
        bubbles.append((obj, radius*math.cos(angle), radius*math.sin(angle),
                        (bead/25+rng.uniform(0, .012)) % 1, speed, rng.uniform(.00012, .00030)))
wall_bubbles = []
for i in range(220):
    z, angle = rng.uniform(.009, .068), rng.uniform(0, math.tau)
    radius = inner_radius(z)-.0002
    obj = bpy.data.objects.new(f"Tiny wall nucleation bead {i:03}", bubble_mesh)
    scene.collection.objects.link(obj)
    obj.location = GLASS_AT+Vector((radius*math.cos(angle), radius*math.sin(angle), z))
    size = rng.uniform(.00008, .00019)
    obj.scale = (size, size, size)
    wall_bubbles.append((obj, z))
impact_bubbles = []
for i in range(28):
    obj = bpy.data.objects.new(f"Small impact air inclusion {i:02}", bubble_mesh)
    scene.collection.objects.link(obj)
    impact_bubbles.append((obj, rng.uniform(0, math.tau), rng.uniform(.0013, .0055),
                           rng.uniform(.0001, .00028), rng.random()))
impact_drops = []
for i in range(7):
    obj = bpy.data.objects.new(f"Tiny moving impact droplet {i:02}", drop_mesh)
    scene.collection.objects.link(obj)
    impact_drops.append((obj, rng.uniform(0, math.tau), rng.random(), rng.uniform(.00018, .00038)))

# CAD final path station, with its 140-degree exit tangent, in metres.
WATER_OUTLET = FAUCET_AT+Vector((0, -.1339967220, .1803887434))
FLAVOR_OUTLET = WATER_OUTLET+Vector((-.003175, -.004641, .003897))
EXIT_DIRECTION = Vector((0, -math.sin(math.radians(140)), math.cos(math.radians(140))))
STREAM_RINGS, STREAM_SIDES = 52, 12


def new_stream(name, finish):
    vertices = [(0, 0, 0)]*(STREAM_RINGS*STREAM_SIDES)
    faces = [(ring*STREAM_SIDES+side, ring*STREAM_SIDES+(side+1) % STREAM_SIDES,
              (ring+1)*STREAM_SIDES+(side+1) % STREAM_SIDES, (ring+1)*STREAM_SIDES+side)
             for ring in range(STREAM_RINGS-1) for side in range(STREAM_SIDES)]
    faces += [tuple(reversed(range(STREAM_SIDES))), tuple((STREAM_RINGS-1)*STREAM_SIDES+i for i in range(STREAM_SIDES))]
    return mesh_object(name, vertices, faces, finish)


streams = [(new_stream("Curving clear water stream", stream_water), WATER_OUTLET, .90, .0018, 0),
           (new_stream("Separate fine citrus stream", stream_flavor), FLAVOR_OUTLET, .75, .00044, 1.3)]


def trajectory(outlet, speed, level, fraction):
    velocity = EXIT_DIRECTION*speed
    drop = outlet.z-(GLASS_AT.z+level)
    flight = (velocity.z+math.sqrt(velocity.z*velocity.z+2*9.81*drop))/9.81
    dt = flight*fraction
    return outlet+velocity*dt+Vector((0, 0, -.5*9.81*dt*dt)), velocity+Vector((0, 0, -9.81*dt))


def surface_height(x, y, radius, level, t, flowing, impact):
    edge = max(0., radius-math.hypot(x, y))
    height = level+.00055*math.exp(-edge/.0015)
    if flowing:
        dx, dy = x-impact.x, y-impact.y
        distance = math.hypot(dx*1.06, dy*.94)
        angle = math.atan2(dy, dx)
        wave_distance = distance+.00075*math.sin(angle*3+t*4.1)
        depression = -.00060*math.exp(-(distance/.0028)**2)
        rings = .00028*math.exp(-distance*80)*math.cos(wave_distance*670-t*13)
        cross = .00010*math.sin(x*320+y*450+t*8)
        height += min(1., edge/.003)*(depression+rings+cross)
    else:
        height += .000022*math.sin(x*170+y*120+t*1.6)
    return height


def beverage(t, level, flowing):
    jet_noise.inputs["W"].default_value = t*1.7
    radius = inner_radius(level)+.00006
    hit, _ = trajectory(WATER_OUTLET, .90, level, 1)
    local_hit = hit-GLASS_AT
    for index, (fraction, c, s) in enumerate(surface_data):
        x, y = fraction*radius*c, fraction*radius*s
        z = surface_height(x, y, radius, level, t, flowing, local_hit)
        liquid.data.vertices[surface_start+index].co = (x, y, z)
    for i in range(SURFACE_SIDES):
        liquid.data.vertices[side_top_start+i].co = liquid.data.vertices[outer_ring+i].co
    liquid.data.update()
    for obj, x, y, phase, speed, size in bubbles:
        z = .007+(phase*(level-.008)+t*speed) % (level-.008)
        obj.location = GLASS_AT+Vector((x+.00025*math.sin(t*2+phase*math.tau), y, z))
        actual_size = size*(.65+.45*z/level)
        obj.scale = (actual_size, actual_size, actual_size*1.06)
    for obj, z in wall_bubbles:
        obj.hide_render = z > level-.001
    for obj, angle, distance, size, phase in impact_bubbles:
        obj.hide_render = not flowing
        obj.location = hit+Vector((math.cos(angle+t*.6)*distance, math.sin(angle+t*.6)*distance,
                                   -.00025-.0025*((phase+t*.8) % 1)))
        obj.scale = (size, size, size)
    for obj, angle, phase, size in impact_drops:
        obj.hide_render = not flowing
        age = ((t+phase)*1.8) % .075
        radius = .0015+age*.035
        obj.location = hit+Vector((math.cos(angle+t*.7)*radius, math.sin(angle+t*.7)*radius,
                                   .34*age-.5*9.81*age*age))
        obj.scale = (size, size, size*1.25)
    for obj, outlet, initial_speed, initial_radius, phase in streams:
        obj.hide_render = not flowing
        if not flowing:
            continue
        for ring in range(STREAM_RINGS):
            fraction = ring/(STREAM_RINGS-1)
            point, velocity = trajectory(outlet, initial_speed, level, fraction)
            point.x += .00065*math.sin(t*28-fraction*22+phase)*fraction**1.4
            point.y += .00045*math.sin(t*21-fraction*29+phase)*fraction
            point.z -= .00035*fraction**12
            tangent = velocity.normalized()
            side_x = Vector((1, 0, 0))
            side_y = tangent.cross(side_x).normalized()
            taper = math.sqrt(initial_speed/velocity.length)
            travelling = .17*math.sin(t*31-fraction*32+phase)+.075*math.sin(t*54-fraction*75)
            radius_here = initial_radius*taper*(1+travelling*fraction**.7)
            for side in range(STREAM_SIDES):
                angle = math.tau*side/STREAM_SIDES
                organic = 1+.035*math.sin(angle*3+t*18-fraction*15)
                offset = (side_x*math.cos(angle)+side_y*math.sin(angle))*radius_here*organic
                obj.data.vertices[ring*STREAM_SIDES+side].co = point+offset
        obj.data.update()


beverage_objects = [obj for obj in scene.objects if obj.type == "MESH" and obj not in faucet.values()]
lighting = StudioLighting(scene, material, linear, GLASS_AT, beverage_objects)


def draw(shot, t, duration):
    """Set the complete picture state from one absolute local time."""
    motion_duration = motion_durations.get(shot,duration)
    p = ease(t/max(motion_duration, .001))
    pouring = shot == "pour"
    for obj in faucet.values():
        obj.hide_render = shot == "drink"
    lever.rotation_euler.x = .23 if pouring else 0
    full_level = .0715
    flow_volume = sum(math.pi*radius*radius*speed for _, _, speed, radius, _ in streams)
    surface_area = math.pi*inner_radius(full_level)**2
    level = full_level-flow_volume*max(0., duration-t)/surface_area if pouring else full_level
    beverage(t, level, pouring)
    if shot == "drink":
        pose(blend((.225, -.385, .145), (.221, -.377, .142), p),
             (.145, -.151, .060), 85, (.155, -.181, .060), 32)
    elif pouring:
        pose(blend((.520, -.480, .340), (.514, -.474, .337), p),
             (.143, -.118, .115), 62, (.144, -.139, .119), 13)
    elif shot == "serve":
        pose(blend((.435, -.790, .263), (.432, -.784, .261), p),
             (-.025, -.035, .084), 52, (.145, -.085, .112), 12)
    else:
        pose(blend((.470, -.820, .270), (.461, -.805, .267), p),
             (-.018, -.045, .092), 53, (.145, -.085, .119), 9)
    lighting.draw(camera, shot, t, motion_duration)
    bpy.context.view_layer.update()


defaults = {"drink": 2.125, "hero": 4.125, "pour": 4.375, "serve": 127/24}
story_path = HERE/"story.json"
story = json.loads(story_path.read_text()) if story_path.exists() else {"scenes": []}
timings = {item["id"]: item["end"]-item["start"] for item in story["scenes"] if item["id"] in defaults}
motion_durations = {item["id"]: item.get("motion_duration",item["end"]-item["start"]) for item in story["scenes"] if item["id"] in defaults}
requested = args.shots or ["hero", "pour", "serve"]
unknown = set(requested)-set(defaults)
if unknown:
    raise SystemExit(f"Unknown studio shot(s): {', '.join(sorted(unknown))}")
print(f"FILM_DEVICE {scene.cycles.device}", flush=True)
for shot in requested:
    duration = timings.get(shot, defaults[shot])
    frames = [(round(duration*.55*args.fps), duration*.55)] if args.stills else [
        (number, number/args.fps) for number in range(args.start_frame,
            min(round(duration*args.fps), args.end_frame if args.end_frame is not None else 10**9))]
    directory = args.out/"stills" if args.stills else (args.frames_root or args.out/"frames")/shot
    directory.mkdir(parents=True, exist_ok=True)
    for number, t in frames:
        target = directory/(f"{shot}.png" if args.stills else f"{number:05}.png")
        if target.exists() and not args.stills:
            continue
        started = time.monotonic()
        scene.frame_set(number)
        draw(shot, t, duration)
        scene.render.filepath = str(target)
        print(f"FILM {shot} {number}/{round(duration*args.fps)}", flush=True)
        bpy.ops.render.render(write_still=True)
        print(f"FILM_FRAME {shot} {number} {time.monotonic()-started:.2f}s", flush=True)
    print(f"FILM_SHOT {shot} completed", flush=True)
