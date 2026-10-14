"""Shot-specific photographic lighting and seamless product backgrounds.

The controller runs after the main film stage has selected objects and posed
its camera. Surface finishes stay on the shared catalog materials; the rigs
shape them with a key, a restrained fill and a grazing edge.
"""

from __future__ import annotations

import math

from mathutils import Vector


class Lighting:
    def __init__(self, g):
        self.g = g
        self.bpy = g["bpy"]
        self.scene = g["scene"]
        self.camera = g["camera"]
        self.current_shot = None
        before = set(self.scene.objects)
        self.original_lights = [o for o in self.scene.objects
                                if o.type == "LIGHT" and not o.name.startswith("Errand — ")]
        material = g["material"]
        self.ivory = material("Film — mineral studio sweep", "#E9E8E3", 0.64)
        self.cobalt = material("Film — cobalt studio sweep", "#1749D1", 0.49)
        self.negative = material("Film — black reflection flags", "#11151B", 0.98)
        self.white_sweep = self._sweep("mineral infinity", self.ivory)
        self.blue_sweep = self._sweep("cobalt infinity", self.cobalt)
        self.rigs = {}

        # Coordinates are in the kitchen's actual metre-scale product space.
        self.rigs["industrial"] = [
            self._area("white product left window", (-0.34, -0.43, 1.34),
                       (0.214, -0.025, 1.015), 16, 0.44, 0.64, "#FFF9F1"),
            self._area("white product right rim", (0.52, 0.25, 1.29),
                       (0.214, -0.015, 1.015), 23, 0.11, 0.48, "#E8F0FF"),
            self._area("white product low fill", (0.67, -0.65, 0.98),
                       (0.214, -0.03, 0.99), 0.65, 0.38, 0.40, "#FFFFFF"),
        ]
        self.rigs["product"] = [
            self._area("black product grazing key", (-0.40, -0.20, 1.25),
                       (0.214, 0.01, 1.015), 1.4, 0.12, 0.45, "#FFF9F1"),
            self._area("black product narrow rim", (0.52, 0.25, 1.29),
                       (0.214, 0.015, 1.015), 2.6, 0.065, 0.42, "#E8F0FF"),
            self._area("black product quiet fill", (0.67, -0.65, 0.98),
                       (0.214, -0.03, 0.99), 0.055, 0.38, 0.40, "#FFFFFF"),
            self._area("mineral background wash", (0.214, 0.28, 1.35),
                       (0.214, 0.94, 1.58), 7.0, 0.90, 0.60, "#FFFFFF"),
        ]
        self.rigs["glass"] = [
            self._area("glass broad backlight", (0.22, 0.13, 1.04),
                       (0.214, -0.143, 0.906), 8.5, 0.23, 0.32, "#FFFCF2"),
            self._area("glass long cold edge", (0.48, -0.10, 1.01),
                       (0.214, -0.143, 0.907), 4.5, 0.045, 0.31, "#E2EDFF"),
            self._area("glass lip softbox", (-0.12, -0.46, 1.29),
                       (0.214, -0.143, 0.91), 2.7, 0.25, 0.31, "#FFFFFF"),
        ]
        self.rigs["pour_glass"] = [
            # The faucet body is behind this emitter's plane, leaving it in
            # shadow while the forward-facing glass catches a clean edge.
            self._area("pour fluid edge", (0.240, -0.015, 0.932),
                       (0.214, -0.143, 0.906), 0.85, 0.055, 0.17, "#FFFFFF"),
        ]
        self.rigs["lever"] = [
            self._area("lever tactile edge", (0.29, -0.18, 0.965),
                       (0.214, -0.015, 0.882), 0.14, 0.035, 0.12, "#FFFFFF"),
        ]
        self.rigs["room"] = [
            self._area("architectural side window", (-1.40, -1.05, 2.25),
                       (0.10, 0.06, 0.86), 155, 1.35, 1.75, "#FFF9F1"),
            self._area("architectural quiet bounce", (1.65, -0.90, 1.65),
                       (0.20, 0.02, 0.94), 8.0, 1.8, 1.8, "#E2EDFF"),
            self._area("architectural faucet edge", (0.51, 0.38, 1.75),
                       (0.214, -0.01, 1.005), 13.5, 0.30, 0.80, "#FFFFFF"),
        ]
        self.rigs["cabinet"] = [
            self._area("cabinet broad left key", (-0.55, -0.85, 1.14),
                       (-0.02, -0.03, 0.34), 23, 0.74, 1.04, "#FFF9F1"),
            self._area("cabinet right rim", (0.56, -0.07, 0.83),
                       (0.11, -0.02, 0.33), 5.0, 0.12, 0.54, "#E2EDFF"),
            self._area("cylinder long reflection", (-0.53, -0.35, 0.64),
                       (-0.253, -0.184, 0.31), 2.2, 0.11, 0.47, "#FFFFFF"),
        ]
        self.cards = []
        for side in (-1, 1):
            card = g["box"](f"Film — glass reflection flag {side}",
                            (0.065, 0.003, 0.37), (0, 0, 0), self.negative, 0)
            # Photographic flags contribute their dark reflection without
            # becoming unexplained rectangles in a close-up or a glass.
            card.visible_camera = False
            card.visible_shadow = False
            card.visible_diffuse = False
            card.visible_glossy = True
            card.visible_transmission = True
            self.cards.append((side, card))
        self.objects = [o for o in self.scene.objects if o not in before]
        for obj in self.objects:
            obj.hide_render = True

    def _area(self, name, location, target, energy, size, size_y, color):
        data = self.bpy.data.lights.new("Film — " + name, "AREA")
        data.energy = energy
        data.shape = "RECTANGLE"
        data.size = size
        data.size_y = size_y
        data.color = self.g["linear"](color)
        obj = self.bpy.data.objects.new("Film — " + name, data)
        self.scene.collection.objects.link(obj)
        obj.location = location
        obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
        return obj

    def _sweep(self, name, material):
        z = self.g["counter_top"] - 0.0002
        section = [(-5, z), (0.45, z)]
        for i in range(1, 49):
            angle = (math.pi / 2) * i / 48
            section.append((0.45 + 0.50 * math.sin(angle),
                            z + 0.50 * (1 - math.cos(angle))))
        section.append((0.95, 5))
        verts = [(x, y, height) for x in (-6, 6) for y, height in section]
        n = len(section)
        faces = [(i, n + i, n + i + 1, i + 1) for i in range(n - 1)]
        mesh = self.bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = self.bpy.data.objects.new("Film — " + name, mesh)
        self.scene.collection.objects.link(obj)
        obj.data.materials.append(material)
        self.g["smooth"](obj)
        return obj

    @staticmethod
    def _show(objects):
        for obj in objects:
            obj.hide_render = False

    def _flags(self):
        center = Vector((0.214, -0.143, 0.925))
        facing = self.camera.location - center
        facing.z = 0
        facing.normalize()
        sideways = Vector((-facing.y, facing.x, 0))
        for side, card in self.cards:
            card.location = center + sideways * (side * 0.112) - facing * 0.045
            card.rotation_euler.z = math.atan2(facing.y, facing.x) - math.pi / 2
            card.hide_render = False

    def draw(self, shot, t, duration):
        background = self.scene.world.node_tree.nodes["Background"]
        if shot not in {"can", "case", "carry", "shelf", "reset", "closing"}:
            strength = 0.035 if shot in {"kitchen", "home", "under"} else 0.025
            if background.inputs["Strength"].default_value != strength:
                background.inputs["Strength"].default_value = strength
        if self.current_shot == shot:
            if shot in {"wish", "fizz", "pour"}:
                self._flags()
            return
        self.current_shot = shot
        for obj in self.objects:
            obj.hide_render = True
        if shot in {"can", "case", "carry", "shelf", "reset", "closing"}:
            return
        for light in self.original_lights:
            light.hide_render = True
        background.inputs["Color"].default_value = (*self.g["linear"]("#E7EEF8"), 1)

        if shot in {"kitchen", "home"}:
            background.inputs["Strength"].default_value = 0.035
            self._show(self.rigs["room"])
            return
        if shot == "under":
            background.inputs["Strength"].default_value = 0.035
            self._show(self.rigs["room"])
            self._show(self.rigs["cabinet"])
            return

        # The studio floor continues into a curved wall. Both black and white
        # faucets keep their actual finish, each against a legible surround.
        self.g["detail_counter"].hide_render = True
        sweep = self.blue_sweep if shot == "industrial" else self.white_sweep
        sweep.hide_render = False
        background.inputs["Strength"].default_value = 0.025
        if shot in {"wish", "fizz"}:
            self._show(self.rigs["glass"])
            self._flags()
        else:
            self._show(self.rigs["industrial"] if shot == "industrial" else self.rigs["product"])
            if shot == "lever":
                self._show(self.rigs["lever"])
            if shot == "pour":
                self._show(self.rigs["pour_glass"])
                self._flags()


def create(g):
    return Lighting(g)
