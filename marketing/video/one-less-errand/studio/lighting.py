"""Neutral daylight studio shared by the faucet and beverage portraits."""
from __future__ import annotations
import math
import bpy
from mathutils import Vector


class StudioLighting:
    def __init__(self, scene, material, linear, glass_at, beverage_objects):
        self.scene, self.linear, self.glass_at = scene, linear, Vector(glass_at)
        scene.world = bpy.data.worlds.new("Cool studio ambient")
        scene.world.use_nodes = True
        scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (*linear("#E9F1F5"), 1)
        scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = .18
        floor = material("Ice and cobalt studio", "#EAF6FF", .50)
        nodes, links = floor.node_tree.nodes, floor.node_tree.links
        coordinates = nodes.new("ShaderNodeTexCoord")
        separate = nodes.new("ShaderNodeSeparateXYZ")
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "EASE"
        ramp.color_ramp.elements[0].position = .46
        ramp.color_ramp.elements[0].color = (*linear("#EAF6FF"), 1)
        ramp.color_ramp.elements[1].position = .98
        ramp.color_ramp.elements[1].color = (*linear("#1D51D3"), 1)
        middle = ramp.color_ramp.elements.new(.65)
        middle.color = (*linear("#A7D5FB"), 1)
        links.new(coordinates.outputs["Window"], separate.inputs["Vector"])
        links.new(separate.outputs["X"], ramp.inputs["Fac"])
        bsdf = nodes.get("Principled BSDF")
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = .12
        section = [(-4, 0), (.32, 0)]
        for i in range(1, 41):
            angle = math.pi*.5*i/40
            section.append((.32+.38*math.sin(angle), .38*(1-math.cos(angle))))
        section.append((.70, 3))
        vertices = [(x, y, z) for x in (-4, 4) for y, z in section]
        n = len(section)
        mesh = bpy.data.meshes.new("Seamless studio sweep")
        mesh.from_pydata(vertices, [], [(i, n+i, n+i+1, i+1) for i in range(n-1)])
        mesh.update()
        sweep = bpy.data.objects.new("Seamless pale studio", mesh)
        scene.collection.objects.link(sweep)
        mesh.materials.append(floor)
        for polygon in mesh.polygons:
            polygon.use_smooth = True
        self.area("Broad neutral key", (-.30, -.32, .56), (.13, -.04, .11), 5, .42, .58, "#F7FBFF")
        self.area("Long product edge", (.40, .21, .39), (.145, .02, .13), 1.2, .10, .40, "#E5F0FF")
        receivers = bpy.data.collections.new("Beverage lighting receivers")
        for obj in beverage_objects:
            receivers.objects.link(obj)
        backlight = self.area("Glass broad backlight", (.12, .15, .29), (.145, -.15, .052), 5, .22, .30, "#FFFFFF")
        edge = self.area("Glass bright side", (.36, -.10, .22), (.145, -.151, .045), 1.6, .035, .20, "#FFFFFF")
        sparkle = self.area("Cold bead highlight", (-.04, -.29, .19), (.145, -.17, .05), 1.8, .035, .19, "#FFFFFF")
        for lamp in (backlight, edge, sparkle):
            lamp.light_linking.receiver_collection = receivers
        self.area("Quiet front fill", (.35, -.53, .28), (.145, -.04, .13), .15, .32, .36, "#F5FAFF")
        self.area("Background gradient", (-.55, -.12, .85), (.12, .60, .48), 5, .85, .85, "#E8F2FF")

    def area(self, name, at, target, energy, width, height, color):
        light = bpy.data.lights.new(name, "AREA")
        light.energy = energy
        light.shape = "RECTANGLE"
        light.size, light.size_y = width, height
        light.color = self.linear(color)
        obj = bpy.data.objects.new(name, light)
        self.scene.collection.objects.link(obj)
        obj.location = at
        obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj

    def draw(self, camera, shot, t, duration):
        pass
