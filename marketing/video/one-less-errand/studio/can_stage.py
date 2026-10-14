"""Physical cans and cropped everyday handling contexts for One Less Errand.

Run with Blender's Python. Every pose is a pure function of shot-local time;
the saved scene's ``can_actions`` supplies the narration and sound clock.
Meshes are linked between identical, full-size cans. Nothing scales during
handling, removal or restocking.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
import time

import bpy
from mathutils import Vector
import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from cad import linear, material
from can_motion import SHOTS, state


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--shots", nargs="+", choices=SHOTS)
parser.add_argument("--fps", type=int, default=24)
parser.add_argument("--width", type=int, default=1920)
parser.add_argument("--samples", type=int, default=32)
parser.add_argument("--start-frame", type=int, default=0)
parser.add_argument("--end-frame", type=int)
parser.add_argument("--frames-root", type=Path)
parser.add_argument("--stills", action="store_true")
parser.add_argument("--time", type=float, help="Local time for a still")
parser.add_argument("--story", type=Path, default=HERE/"story.json")
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
scene.cycles.seed = 78
scene.cycles.use_animated_seed = False
scene.cycles.max_bounces = 7
scene.cycles.transmission_bounces = 5
scene.render.use_persistent_data = True
scene.render.resolution_x = args.width
scene.render.resolution_y = round(args.width*9/16)
scene.render.resolution_percentage = 100
scene.render.fps = args.fps
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.film_transparent = False
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"
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

camera = bpy.data.objects.new("Routine camera", bpy.data.cameras.new("Routine camera"))
scene.collection.objects.link(camera)
scene.camera = camera
camera.data.sensor_width = 36
camera.data.clip_start = .004
camera.data.clip_end = 20
camera.data.dof.use_dof = True
camera.data.dof.aperture_blades = 9


def smooth(obj):
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def mesh(name, vertices, faces, finish, parent=None, smooth_faces=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    if finish:
        data.materials.append(finish)
    obj.parent = parent
    if smooth_faces:
        smooth(obj)
    return obj


def empty(name, parent=None, at=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    scene.collection.objects.link(obj)
    obj.parent, obj.location = parent, at
    return obj


def box(name, size, at, finish, parent=None, bevel=.0015):
    x, y, z = (v/2 for v in size)
    vertices = [(a*x, b*y, c*z) for a, b, c in
                [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                 (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    obj = mesh(name, vertices, faces, finish, parent, False)
    obj.location = at
    if bevel:
        mod = obj.modifiers.new("Soft physical edges", "BEVEL")
        mod.width, mod.segments = min(bevel, min(size)*.35), 3
        obj.modifiers.new("Weighted face normals", "WEIGHTED_NORMAL")
    return obj


def pipe(name, points, radius, finish, parent=None, closed=False):
    data = bpy.data.curves.new(name, "CURVE")
    data.dimensions = "3D"
    data.resolution_u, data.bevel_resolution = 2, 3
    data.bevel_depth = radius
    spline = data.splines.new("POLY")
    spline.points.add(len(points)-1)
    for point, xyz in zip(spline.points, points):
        point.co = (*xyz, 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    data.materials.append(finish)
    obj.parent = parent
    return obj


def torus(name, radius, thickness, at, finish, parent=None, segments=96):
    vertices, faces, sides = [], [], 10
    for i in range(segments):
        a = math.tau*i/segments
        for j in range(sides):
            b = math.tau*j/sides
            radial = radius+thickness*math.cos(b)
            vertices.append((radial*math.cos(a), radial*math.sin(a), thickness*math.sin(b)))
    for i in range(segments):
        for j in range(sides):
            faces.append((i*sides+j, ((i+1)%segments)*sides+j,
                          ((i+1)%segments)*sides+(j+1)%sides, i*sides+(j+1)%sides))
    obj = mesh(name, vertices, faces, finish, parent)
    obj.location = at
    return obj


def cylinder(name, radius, height, at, finish, parent=None, segments=96):
    vertices = [(radius*math.cos(math.tau*i/segments), radius*math.sin(math.tau*i/segments), z)
                for z in (-height/2, height/2) for i in range(segments)]
    faces = [(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
    faces += [tuple(reversed(range(segments))), tuple(range(segments, 2*segments))]
    obj = mesh(name, vertices, faces, finish, parent)
    obj.location = at
    for polygon in obj.data.polygons[-2:]:
        polygon.use_smooth = False
    return obj


def textured_finish(name, color, roughness, scale, distance, metal=0):
    finish = material(name, color, roughness, metal)
    nodes, links = finish.node_tree.nodes, finish.node_tree.links
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .16
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], nodes.get("Principled BSDF").inputs["Normal"])
    return finish


aluminum = material("Soft rolled aluminum", "#D4DCE3", .27, 1)
brushed = material("Satin can lid", "#BAC5D0", .38, 1)
anisotropy = brushed.node_tree.nodes.get("Principled BSDF").inputs.get("Anisotropic IOR Level")
if anisotropy is None:
    anisotropy = brushed.node_tree.nodes.get("Principled BSDF").inputs.get("Anisotropic")
if anisotropy is not None:
    anisotropy.default_value = .45
score = material("Fine scored metal", "#84909B", .42, .82)
paint = textured_finish("Matte printed cream can", "#F3F0E8", .46, 420, .000003, .12)
carton = textured_finish("Uncoated thin carton", "#D9CEC0", .83, 1450, .00007)
fold = material("Carton folds", "#BFB19F", .87)
silver = material("Cart basket satin steel", "#C2CCD7", .32, .86)
orange = material("Warm orange cart grip", "#FF9152", .58)
rubber = textured_finish("Soft trunk rubber", "#17222D", .87, 480, .00006)
felt = textured_finish("Cargo floor felt", "#3B4656", .96, 1100, .00028)
car_paint = material("Cropped silver car exterior", "#B6C4D3", .25, .55)
tail = material("Cropped tail lamp", "#B54138", .25, .22)
white = material("Warm white kitchen cabinet", "#E7E6DF", .57)
countertop = textured_finish("Quiet pale countertop", "#F1F0E9", .45, 380, .000025)
fridge_white = material("Refrigerator interior", "#DDE8EF", .47)
shelf_glass = material("Clear refrigerator shelf", "#D8EDF6", .08, transmission=1, ior=1.46)
light_strip = material("Soft refrigerator light", "#ECF6FF", .4)
light_strip.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (*linear("#D5EAFF"), 1)
light_strip.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = 1.2


def label_texture():
    size = 2048
    u, v = np.meshgrid((np.arange(size)+.5)/size, (np.arange(size)+.5)/size)
    pixels = np.ones((size, size, 4), dtype=np.float32)
    pixels[:, :, :3] = linear("#F3F0E8")
    du = np.abs((u-.25+.25) % .5-.25)
    oval_distance = np.sqrt((du/.150)**2+((v-.465)/.145)**2)
    oval_alpha = np.clip((1-oval_distance)/(2/(size*.145))+.5,0,1)[...,None]
    pixels[:, :, :3] = (pixels[:, :, :3]*(1-oval_alpha)
                        +np.asarray(linear("#F58F45"))*oval_alpha)
    for center, height, radius in [(.19,.72,.022),(.31,.775,.033),(.365,.69,.014)]:
        dx = np.abs((u-center+.25) % .5-.25)
        distance = np.sqrt((dx/radius)**2+((v-height)/radius)**2)
        alpha = np.clip((1-distance)/(2/(size*radius))+.5,0,1)[...,None]
        pixels[:, :, :3] = pixels[:, :, :3]*(1-alpha)+np.asarray(linear("#DCE6F5"))*alpha
    image = bpy.data.images.new("Original unbranded cream and orange can artwork", width=size, height=size, float_buffer=True)
    image.colorspace_settings.name = "Non-Color"
    image.pixels.foreach_set(pixels.ravel())
    image.pack()
    nodes, links = paint.node_tree.nodes, paint.node_tree.links
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    links.new(texture.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])


label_texture()
S = .122/2.6
PROFILE = [(r*S, z*S) for r,z in [(.53,0),(.59,.02),(.62,.08),(.65,.17),(.70,.30),
            (.705,2.22),(.69,2.36),(.65,2.46),(.60,2.55),(.59,2.60)]]


def can_body(parent):
    segments = 96
    vertices = [(r*math.cos(math.tau*i/segments), r*math.sin(math.tau*i/segments), z)
                for r,z in PROFILE for i in range(segments)]
    faces = [(ring*segments+i, ring*segments+(i+1)%segments,
              (ring+1)*segments+(i+1)%segments,(ring+1)*segments+i)
             for ring in range(len(PROFILE)-1) for i in range(segments)]
    obj = mesh("Shouldered printed can body", vertices, faces, paint, parent)
    uv = obj.data.uv_layers.new(name="Wrapped can artwork")
    for face_index, polygon in enumerate(obj.data.polygons):
        ring, segment = divmod(face_index, segments)
        values = [(segment/segments, PROFILE[ring][1]/.122),
                  ((segment+1)/segments, PROFILE[ring][1]/.122),
                  ((segment+1)/segments, PROFILE[ring+1][1]/.122),
                  (segment/segments, PROFILE[ring+1][1]/.122)]
        for loop, value in zip(polygon.loop_indices, values):
            uv.data[loop].uv = value
    return obj


def pull_tab(parent):
    n, vertices = 64, []
    for z in (0.0, .00065):
        for rx,ry,cy in ((.0058,.0103,0),(.0031,.0046,.0022)):
            vertices += [(rx*math.cos(math.tau*i/n), cy+ry*math.sin(math.tau*i/n), z) for i in range(n)]
    faces = []
    for i in range(n):
        j = (i+1)%n
        faces += [(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),
                  (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
    tab = mesh("Stamped aluminum pull tab", vertices, faces, aluminum, parent)
    tab.location = (0, -.001, .1232)
    tab.rotation_euler.z = -.12
    mod = tab.modifiers.new("Tiny stamped edge", "BEVEL")
    mod.width, mod.segments = .00015, 2
    rivet = cylinder("Pull tab rivet", .00155, .00065, (0,.0064,.12405), aluminum, parent, 32)
    return tab, rivet


def make_can():
    root = empty("Full-size unbranded soda can")
    can_body(root)
    torus("Rolled top seam", .589*S, .034*S, (0,0,2.61*S), aluminum, root)
    torus("Bottom standing seam", .578*S, .030*S, (0,0,.05*S), aluminum, root)
    cylinder("Recessed brushed lid", .572*S, .034*S, (0,0,2.604*S), brushed, root)
    torus("Pressed lid groove", .477*S, .009*S, (0,0,2.626*S), score, root)
    opening = [(math.cos(math.tau*i/64)*.0075, -.011+math.sin(math.tau*i/64)*.0083, .12305) for i in range(64)]
    pipe("Scored drinking opening", opening, .00017, score, root, closed=True)
    pull_tab(root)
    return root


def clone_tree(source, parent=None):
    result = source.copy()
    scene.collection.objects.link(result)
    result.parent = parent
    for child in source.children:
        clone_tree(child, result)
    return result


def descendants(root):
    yield root
    for child in root.children:
        yield from descendants(child)


def visible(root, value):
    for obj in descendants(root):
        obj.hide_render = not value


CAN_GRID = [((column-1.5)*.0674, (row-1)*.0674, .0028)
            for row in range(3) for column in range(4)]
PACK_AT = Vector((.145, 0, 0))
template = make_can()


def make_pack(index):
    root = empty(f"Twelve-can carton {index+1}", at=PACK_AT)
    cans = []
    for number, at in enumerate(CAN_GRID):
        obj = clone_tree(template, root)
        obj.name = f"Case {index+1} can {number+1:02}"
        obj.location = at
        obj.rotation_euler.z = .11*((number%4)%2)-.08*(number//4)
        cans.append(obj)
    w,d,h,thick = .277,.211,.023,.0015
    box("Carton base", (w,d,.0028), (0,0,.0014), carton, root, .0006)
    box("Carton front fold", (w,thick,h), (0,-d/2,h/2), carton, root, .0004)
    box("Carton back fold", (w,thick,h), (0,d/2,h/2), carton, root, .0004)
    box("Carton left fold", (thick,d,h), (-w/2,0,h/2), carton, root, .0004)
    box("Carton right fold", (thick,d,h), (w/2,0,h/2), carton, root, .0004)
    for x in (-w*.5+.011,w*.5-.011):
        pipe("Carton corner crease", [(x,-d*.5-.0008,.001),(x,-d*.5-.0008,.022)], .00022, fold, root)
    pipe("Fine front carton fold", [(-w/2,-d*.5-.0009,.005),(w/2,-d*.5-.0009,.005)], .0002, fold, root)
    return root, cans


packs = [make_pack(index) for index in range(5)]
visible(template, False)


contexts = {name: empty(f"{name.title()} handling context", at=PACK_AT)
            for name in ("case", "car", "kitchen", "shelf")}
cart = contexts["case"]
for x in np.linspace(-.15,.15,11):
    pipe("Basket continuous steel wire", [(x,-.142,.147),(x*.87,-.113,-.003),(x*.87,.113,-.003),(x,.142,.147)], .00125, silver, cart)
for y in np.linspace(-.11,.11,7):
    pipe("Basket cross wire", [(-.171,y*1.24,.147),(-.139,y,-.003),(.139,y,-.003),(.171,y*1.24,.147)], .00125, silver, cart)
for z in (.028,.084,.147):
    u = (z+.003)/.15
    x,y = .139+u*.032,.113+u*.029
    pipe("Basket horizontal rail", [(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)], .0017, silver, cart, True)
for x in (-.165,.165):
    pipe("Cart handle upright", [(x,.142,.147),(x,.202,.238)], .0031, silver, cart)
pipe("Orange shopping cart handle", [(-.166,.202,.238),(.166,.202,.238)], .009, orange, cart)
for x in (-.130,.130):
    # These are the cropped cart's load-bearing frame, not loose basket wire.
    # The lower chassis and wheels remain below the camera's composition.
    pipe("Cart front structural support", [(x,-.106,-.004),(x,-.090,-.085),
         (x*1.24,.012,-.48)], .0052, silver, cart)
    pipe("Cart rear structural support", [(x,.106,-.004),(x,.130,-.095),
         (x*1.24,.205,-.48)], .0052, silver, cart)
    pipe("Cart basket lower frame", [(x,-.107,-.009),(x,.110,-.009)], .0044, silver, cart)

trunk = contexts["car"]
box("Cropped carpeted cargo floor", (.56,.40,.018), (0,.015,-.011), felt, trunk, .004)
box("Cargo bay rear lining", (.56,.018,.17), (0,.205,.067), felt, trunk, .008)
for x in (-.283,.283):
    box("Cropped cargo side lining", (.025,.27,.15), (x,.070,.060), felt, trunk, .009)
    pipe("Trunk rubber side gasket", [(x,-.10,-.01),(x,.21,.02),(x,.215,.14)], .006, rubber, trunk)
box("Trunk sill", (.61,.048,.045), (0,-.201,-.023), car_paint, trunk, .006)
box("Trunk threshold rubber", (.53,.042,.009), (0,-.197,.003), rubber, trunk, .003)
for x in np.linspace(-.23,.23,13):
    box("Threshold grip rib", (.0022,.034,.002), (x,-.198,.008), score, trunk, .0005)
box("Cropped rear body panel", (.65,.018,.11), (0,-.226,-.075), car_paint, trunk, .005)
box("Partial right rear lamp", (.039,.021,.095), (.277,-.237,-.065), tail, trunk, .006)
box("Partial left rear lamp", (.030,.021,.073), (-.277,-.237,-.042), tail, trunk, .005)

kitchen = contexts["kitchen"]
box("Full-size counter crop", (1.35,.57,.034), (-.13,.08,-.020), countertop, kitchen, .003)
box("Cabinet front crop", (1.27,.018,.45), (-.13,-.189,-.265), white, kitchen, .001)
box("Quiet cabinet seam", (.0012,.001,.37), (-.13,-.199,-.25), score, kitchen, 0)
for x in (-.35,.09):
    for dx in (-.045,.045):
        pipe("Cabinet handle standoff", [(x+dx,-.201,-.10),(x+dx,-.217,-.10)], .0021, silver, kitchen)
    pipe("Counter cabinet handle", [(x-.058,-.217,-.10),(x+.058,-.217,-.10)], .0032, silver, kitchen)

shelf = contexts["shelf"]
box("Refrigerator glass shelf", (.50,.325,.004), (0,.027,-.004), shelf_glass, shelf, .0006)
box("Refrigerator shelf front trim", (.505,.014,.012), (0,-.135,-.003), aluminum, shelf, .002)
box("Refrigerator rear interior crop", (.535,.018,.51), (0,.202,.205), fridge_white, shelf, .012)
for x in (-.259,.259):
    box("Cropped refrigerator side return", (.017,.145,.51), (x,.126,.205), fridge_white, shelf, .008)
    box("Vertical refrigerator light", (.006,.003,.29), (x*.95,.187,.20), light_strip, shelf, .001)
box("Lower refrigerator shelf lip", (.50,.015,.012), (0,-.135,-.151), aluminum, shelf, .002)
box("Lower refrigerator shelf crop", (.50,.32,.003), (0,.028,-.155), shelf_glass, shelf, .0004)


world = bpy.data.worlds.new("Neutral routine studio ambient")
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (*linear("#E7EEF6"),1)
world.node_tree.nodes["Background"].inputs["Strength"].default_value = .26
scene.world = world
floor_finish = material("Brand cobalt seamless stage", "#1749D1", .65)
floor_finish.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (*linear("#1749D1"),1)
floor_finish.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = .16
section = [(-3,-.065),(.36,-.065)]
for number in range(1,33):
    angle = math.pi*.5*number/32
    section.append((.36+.38*math.sin(angle), -.065+.38*(1-math.cos(angle))))
section.append((.74,3))
vertices = [(x,y,z) for x in (-4,4) for y,z in section]
n = len(section)
floor_sweep = mesh("Seamless cobalt handling stage", vertices, [(i,n+i,n+i+1,i+1) for i in range(n-1)], floor_finish)


def area(name, at, target, energy, width, height, color):
    data = bpy.data.lights.new(name, "AREA")
    data.energy, data.shape, data.size, data.size_y = energy, "RECTANGLE", width, height
    data.color = linear(color)
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = at
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()
    return obj


area("Long soft can key", (-.22,-.38,.55), (.145,0,.07), 8, .26,.55,"#FAFCFF")
area("Controlled aluminum edge", (.47,.14,.36), (.145,0,.09), 3.5,.10,.42,"#E7F1FF")
area("Gentle front label fill", (.36,-.55,.22), (.145,0,.07), .9,.31,.25,"#FFFFFF")
area("Broad top carton light", (.10,.03,.71), (.145,0,0), 2.5,.50,.34,"#F8FAFF")

# The lid sees a controlled neutral softbox rather than an uninterrupted
# reflection of the cobalt cyclorama. It does not light or mask the picture.
card_finish = material("Neutral lid reflection card", "#F4F7FB", .8)
card_finish.node_tree.nodes.get("Principled BSDF").inputs["Emission Color"].default_value = (*linear("#F4F7FB"),1)
card_finish.node_tree.nodes.get("Principled BSDF").inputs["Emission Strength"].default_value = .8
reflection_card = mesh("Broad neutral lid reflection", [(-.34,-.29,0),(.34,-.29,0),(.34,.29,0),(-.34,.29,0)], [(0,1,2,3)], card_finish, smooth_faces=False)
reflection_card.location = (.13,-.42,.47)
reflection_card.rotation_euler = (Vector((.145,0,.09))-reflection_card.location).to_track_quat("Z","Y").to_euler()
reflection_card.visible_camera = False
reflection_card.visible_diffuse = False
reflection_card.visible_shadow = False
reflection_card.visible_transmission = False


def blend(a,b,p):
    return tuple(x+(y-x)*p for x,y in zip(a,b))


def pose(at, target, lens, focus, aperture):
    camera.location = at
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.lens = lens
    camera.data.dof.focus_distance = (Vector(focus)-camera.location).length
    camera.data.dof.aperture_fstop = aperture


def draw(shot, t, duration, actions):
    blocking = state(shot,t,duration,actions)
    for name, context in contexts.items():
        visible(context, name == blocking["context"])
        context.location = PACK_AT+Vector(blocking["context_offset"])
    floor_sweep.location.z = (-.35*(1-blocking["context_offset"][0]/.66)
                              if shot == "case" else 0.0)
    for root, cans in packs:
        visible(root, False)
        root.location = PACK_AT
        root.rotation_euler = (0,0,0)
        for can,home in zip(cans,CAN_GRID):
            can.location = home
    for entry in blocking["packs"]:
        if entry["index"] >= len(packs):
            raise ValueError("The routine supports at most four restocks")
        root,cans = packs[entry["index"]]
        visible(root,True)
        root.location = PACK_AT+Vector(entry["offset"])
        for can,home,(culled,offset) in zip(cans,CAN_GRID,entry["cans"]):
            can.location = Vector(home)+Vector(offset)
            visible(can,not culled)
        if shot == "case":
            # The familiar first can stays put while the rest of the case
            # enters at full size during the opening camera move.
            for can in cans[1:]:
                can.location.x += .75*(1-blocking["expand"])
    wide_at,wide_target = (.485,-.785,.415),(.015,0,.042)
    if shot == "case":
        p = blocking["expand"]
        pack_z = blocking["packs"][0]["offset"][2]
        tracked_at = (wide_at[0],wide_at[1],wide_at[2]+pack_z)
        tracked_target = (wide_target[0],wide_target[1],wide_target[2]+pack_z)
        pose(blend((-.005,-.590,.088),tracked_at,p),
             blend((-.005,0,-.001),tracked_target,p),70+(45-70)*p,
             blend((.044,-.098,.000),(.145,0,.068+pack_z),p),12-p)
    else:
        # The same apparent pack placement through the handling match cuts.
        # Context objects are full-size fragments surrounding that mark.
        pose(wide_at,wide_target,45,(.145,0,.070),11)
    bpy.context.view_layer.update()


defaults = {"case":4.5,"car":1.25,"kitchen":1.25,"shelf":1.25,"repeat":5.5,"question":3}
story = json.loads(args.story.read_text()) if args.story.exists() else {"scenes":[]}
scenes = {item["id"]:item for item in story["scenes"]}
requested = args.shots or list(SHOTS)
frames_root = args.frames_root or args.out/"frames"/f"story-loop-{args.fps}-{args.fps}fps-{args.width}px-{args.samples}spp"
print(f"FILM_DEVICE {scene.cycles.device}",flush=True)
for shot in requested:
    entry = scenes.get(shot,{})
    duration = float(entry.get("end",defaults[shot]))-float(entry.get("start",0))
    actions = entry.get("can_actions",{})
    count = round(duration*args.fps)
    if args.stills:
        local = args.time if args.time is not None else duration*.55
        frames = [(round(local*args.fps),local)]
    else:
        frames = [(number,number/args.fps) for number in range(args.start_frame,min(count,args.end_frame or count))]
    directory = args.out/"can-stills" if args.stills else frames_root/shot
    directory.mkdir(parents=True,exist_ok=True)
    for number,t in frames:
        target = directory/(f"{shot}-{number:05d}.png" if args.stills else f"{number:05d}.png")
        if target.exists() and not args.stills:
            continue
        started = time.monotonic()
        scene.frame_set(number)
        draw(shot,t,duration,actions)
        scene.render.filepath = str(target)
        print(f"FILM {shot} {number}/{count}",flush=True)
        bpy.ops.render.render(write_still=True)
        print(f"FILM_FRAME {shot} {number} {time.monotonic()-started:.2f}s",flush=True)
    print(f"FILM_SHOT {shot} completed",flush=True)
