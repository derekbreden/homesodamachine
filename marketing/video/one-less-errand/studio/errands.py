"""Physical can, case and pantry photography for One Less Errand.

The film's scene builder supplies the kitchen renderer's helper namespace.
``create(namespace)`` returns an object with ``objects`` and ``draw``; time is
local to each shot, in seconds. All motion is evaluated directly from time.
"""

from __future__ import annotations

import math

from mathutils import Vector


def _ease(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3.0 - 2.0 * value)


def _mix(a, b, value):
    return a + (b - a) * value


class Errands:
    def __init__(self, g):
        self.g = g
        self.bpy = g["bpy"]
        self.scene = g["scene"]
        self.camera = g["camera"]
        before = set(self.scene.objects)
        self.groups = {}
        material = g["material"]
        self.mats = {
            "blue": material("Errand — cobalt sweep", "#1749D1", 0.52),
            "blue_edge": material("Errand — cobalt coated card", "#1749D1", 0.40),
            "ivory": material("Errand — warm ivory can lacquer", "#EEECE4", 0.27, 0.27),
            "metal": material("Errand — rolled aluminum", "#BFC9D3", 0.24, 0.97),
            "lid": material("Errand — brushed aluminum lid", "#CCD2D6", 0.35, 0.94),
            "groove": material("Errand — lid scored recess", "#66727A", 0.36, 0.80),
            "orange": material("Errand — tangerine lacquer", "#EF7B42", 0.28, 0.18),
            "card": material("Errand — uncoated ivory carton", "#E7E2D6", 0.78),
            "card_edge": material("Errand — card cut edges", "#B8AA8D", 0.92),
            "felt": material("Errand — charcoal cargo felt", "#252B32", 0.94),
            "trim": material("Errand — graphite cargo trim", "#171D25", 0.42),
            "stone": material("Errand — pale limestone", "#E5E1D6", 0.54),
            "oak": material("Errand — quiet oak", "#BFA889", 0.66),
            "pantry": material("Errand — pantry ivory", "#DFDFD4", 0.67),
        }
        # A faint manufactured finish holds a grazing highlight on the metal.
        for key, scale, strength, distance in (("lid", 1750, 0.15, 0.000012),
                                               ("card", 950, 0.20, 0.00004),
                                               ("felt", 1600, 0.48, 0.00016)):
            mat = self.mats[key]
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            noise = nodes.new("ShaderNodeTexNoise")
            noise.inputs["Scale"].default_value = scale
            noise.inputs["Detail"].default_value = 2
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = strength
            bump.inputs["Distance"].default_value = distance
            links.new(noise.outputs["Fac"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], nodes.get("Principled BSDF").inputs["Normal"])

        self._stage()
        self.hero_root = self._empty("Single can turntable")
        self.hero = self._can()
        for obj in self.hero:
            obj.parent = self.hero_root
        self.groups["hero"] = self.hero

        self.pack_root = self._empty("Twelve-can pack carrier")
        self.cans = []
        for row in range(3):
            for col in range(4):
                root = self._empty(f"Can {row * 4 + col + 1:02d}")
                root.parent = self.pack_root
                root.location = ((col - 1.5) * 0.069, (row - 1) * 0.069, 0.002)
                parts = []
                for source in self.hero:
                    obj = source.copy()
                    obj.data = source.data
                    self.scene.collection.objects.link(obj)
                    obj.name = f"Pack {row * 4 + col + 1:02d} — {source.name}"
                    obj.parent = root
                    parts.append(obj)
                root.rotation_euler.z = 0.05 * math.sin((row * 4 + col) * 2.3)
                self.cans.append((root, parts))
        self.carton = self._carton()
        for obj in self.carton:
            obj.parent = self.pack_root
        self._contexts()
        self.objects = [obj for obj in self.scene.objects if obj not in before]
        for obj in self.objects:
            obj.hide_render = True

    def _empty(self, name):
        obj = self.bpy.data.objects.new("Errand — " + name, None)
        self.scene.collection.objects.link(obj)
        return obj

    def _box(self, name, size, at, mat, bevel=0.001):
        return self.g["box"]("Errand — " + name, size, at, self.mats[mat], bevel, 4)

    def _lathe(self, name, profile, mat, at=(0, 0, 0), segments=128):
        return self.g["lathe"]("Errand — " + name, profile, self.mats[mat], at, segments)

    def _tube(self, name, points, radius, mat, kind="POLY"):
        return self.g["tube"]("Errand — " + name, points, radius, self.mats[mat], kind)

    def _patch(self, name, radius, z0, z1, angle0, angle1, mat, lean=0):
        verts = []
        rings, sides = 24, 32
        for j in range(rings + 1):
            fraction = j / rings
            z, shift = _mix(z0, z1, fraction), lean * fraction
            for i in range(33):
                angle = math.radians(_mix(angle0, angle1, i / 32) + shift)
                verts.append((radius * math.cos(angle), radius * math.sin(angle), z))
        faces = []
        for j in range(rings):
            for i in range(sides):
                base = j * (sides + 1) + i
                faces.append((base, base + 1, base + sides + 2, base + sides + 1))
        mesh = self.bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = self.bpy.data.objects.new("Errand — " + name, mesh)
        self.scene.collection.objects.link(obj)
        obj.data.materials.append(self.mats[mat])
        return self.g["smooth"](obj)

    def _can(self):
        parts = []
        parts.append(self._lathe("drawn aluminum body", [
            (0.0, 0.0017), (0.0215, 0.0017), (0.0240, 0.0003),
            (0.0272, 0.0003), (0.0294, 0.003), (0.0318, 0.0070),
            (0.0330, 0.014), (0.0330, 0.1035), (0.0325, 0.108),
            (0.0307, 0.112), (0.0273, 0.1174), (0.0266, 0.1207),
            (0.0256, 0.1207), (0.0255, 0.1187),
        ], "metal"))
        parts.append(self._lathe("ivory printed wrap", [
            (0.0321, 0.0088), (0.03285, 0.0120), (0.03306, 0.015),
            (0.03306, 0.1034), (0.03257, 0.1077),
        ], "ivory"))
        parts.append(self._patch("single tangerine slash", 0.03309, 0.020, 0.096,
                                 -108, -96, "orange", lean=34))
        parts.append(self._patch("fine cobalt rule", 0.03310, 0.023, 0.024,
                                 -160, -30, "blue_edge"))
        parts.append(self._lathe("rolled top seam", [
            (0.0262, 0.1202), (0.0276, 0.1203), (0.0283, 0.1212),
            (0.0284, 0.1223), (0.0278, 0.123), (0.0267, 0.123),
            (0.0260, 0.1224), (0.0262, 0.1202),
        ], "metal"))
        parts.append(self._lathe("recessed lid", [
            (0, 0.1208), (0.0231, 0.1208), (0.0245, 0.1211),
            (0.0254, 0.1221), (0.0265, 0.1224),
        ], "lid"))
        parts.append(self._lathe("lid fine concentric score", [
            (0.02315, 0.12083), (0.02336, 0.12083),
        ], "groove"))

        # The tab is an actual little stamped ring, including its hole and rivet.
        outer = [(0.0064 * math.cos(2 * math.pi * i / 48),
                  0.0090 * math.sin(2 * math.pi * i / 48) + 0.0009,
                  0.1218) for i in range(49)]
        tab = self._tube("pull tab stamped perimeter", outer, 0.00105, "metal")
        parts.append(tab)
        parts.append(self._box("pull tab bridge", (0.0114, 0.0040, 0.0010),
                               (0, 0.0020, 0.122), "metal", 0.0004))
        parts.append(self.g["cylinder"]("Errand — pull tab rivet", 0.00185,
                                       0.0010, (0, 0.0037, 0.1226), self.mats["lid"]))
        opening = [(0.0088 * math.cos(2 * math.pi * i / 64),
                    0.0105 * math.sin(2 * math.pi * i / 64) - 0.010,
                    0.12091) for i in range(65)]
        parts.append(self._tube("scored drinking aperture", opening, 0.00018, "groove"))
        return parts

    def _stage(self):
        # Continuous floor-to-wall radius; the camera never sees a horizon seam.
        section = [(-5, -0.001), (0.28, -0.001)]
        for i in range(1, 33):
            angle = (math.pi / 2) * i / 32
            section.append((0.28 + 0.42 * math.sin(angle),
                            -0.001 + 0.42 * (1 - math.cos(angle))))
        section.append((0.70, 3))
        verts = [(x, y, z) for x in (-5, 5) for y, z in section]
        n = len(section)
        faces = [(i, n + i, n + i + 1, i + 1) for i in range(n - 1)]
        mesh = self.bpy.data.meshes.new("Cobalt infinity sweep")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        sweep = self.bpy.data.objects.new("Errand — cobalt infinity sweep", mesh)
        self.scene.collection.objects.link(sweep)
        sweep.data.materials.append(self.mats["blue"])
        self.g["smooth"](sweep)
        self.groups["stage"] = [sweep]
        self.groups["context_floor"] = [self._box(
            "context studio ground", (20, 20, 0.002), (0, 0, -0.002), "blue", 0)]
        self.groups["lights"] = []
        for name, location, target, energy, size, size_y in (
                ("tall softbox", (-0.31, -0.35, 0.41), (0, 0, 0.07), 5.3, 0.16, 0.48),
                ("silver rim strip", (0.27, 0.17, 0.37), (0, 0, 0.07), 7.5, 0.11, 0.42),
                ("low front card", (0.36, -0.47, 0.16), (0, 0, 0.06), 1.4, 0.30, 0.30)):
            data = self.bpy.data.lights.new("Errand — " + name, "AREA")
            data.energy = energy
            data.shape = "RECTANGLE"
            data.size = size
            data.size_y = size_y
            obj = self.bpy.data.objects.new("Errand — " + name, data)
            self.scene.collection.objects.link(obj)
            obj.location = location
            obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
            self.groups["lights"].append(obj)

    def _carton(self):
        # Real-scale open twelve-pack: four by three cans in a folded card tray.
        items = [
            self._box("carton base", (0.283, 0.214, 0.0022), (0, 0, 0.0011), "card", 0.0005),
            self._box("carton front", (0.283, 0.0020, 0.075), (0, -0.107, 0.039), "card", 0.0005),
            self._box("carton back", (0.283, 0.0020, 0.075), (0, 0.107, 0.039), "card", 0.0005),
            self._box("carton left", (0.0020, 0.212, 0.075), (-0.1415, 0, 0.039), "card", 0.0005),
            self._box("carton right", (0.0020, 0.212, 0.075), (0.1415, 0, 0.039), "card", 0.0005),
            self._box("carton front cobalt field", (0.282, 0.00035, 0.023), (0, -0.10815, 0.020), "blue_edge", 0),
            self._box("carton front orange registration", (0.013, 0.0004, 0.023), (0.100, -0.10838, 0.020), "orange", 0),
            self._box("carton folded left return", (0.012, 0.212, 0.002), (-0.136, 0, 0.077), "card", 0.0005),
            self._box("carton folded right return", (0.012, 0.212, 0.002), (0.136, 0, 0.077), "card", 0.0005),
        ]
        return items

    def _contexts(self):
        cargo = [
            self._box("cargo floor", (1.25, 0.80, 0.025), (0, 0.025, -0.013), "felt", 0.009),
            self._box("cargo rear wall", (1.25, 0.05, 0.48), (0, 0.39, 0.22), "felt", 0.016),
            self._box("cargo threshold", (1.25, 0.06, 0.045), (0, -0.36, 0.014), "trim", 0.010),
            self._box("cargo left bolster", (0.13, 0.77, 0.21), (-0.57, 0.02, 0.092), "felt", 0.04),
            self._box("cargo right bolster", (0.13, 0.77, 0.21), (0.57, 0.02, 0.092), "felt", 0.04),
        ]
        for i in range(7):
            cargo.append(self._box("cargo floor shallow rib", (1.02, 0.005, 0.0015),
                                   (0, -0.28 + i * 0.080, 0.001), "trim", 0.0005))
        self.groups["cargo"] = cargo
        self.groups["counter"] = [
            self._box("kitchen stone slab", (1.45, 0.81, 0.027), (0, 0.025, -0.0135), "stone", 0.003),
            self._box("kitchen warm wall", (1.45, 0.025, 0.56), (0, 0.43, 0.265), "pantry", 0.002),
            self._box("kitchen oak face", (1.44, 0.024, 0.42), (0, -0.359, -0.235), "oak", 0.002),
            self._box("kitchen drawer line", (1.43, 0.002, 0.0025), (0, -0.373, -0.134), "trim", 0),
        ]
        # Open framing gives the pantry a real sense of depth without a literal
        # room illustration competing with the twelve cans.
        self.groups["shelf"] = [
            self._box("pantry shelf", (0.67, 0.41, 0.022), (0, 0.058, -0.011), "pantry", 0.002),
            self._box("pantry rear", (0.67, 0.021, 0.49), (0, 0.262, 0.223), "pantry", 0.001),
            self._box("pantry left upright", (0.021, 0.43, 0.49), (-0.3245, 0.058, 0.223), "pantry", 0.001),
            self._box("pantry right upright", (0.021, 0.43, 0.49), (0.3245, 0.058, 0.223), "pantry", 0.001),
            self._box("pantry upper shelf", (0.67, 0.41, 0.022), (0, 0.058, 0.236), "pantry", 0.002),
            self._box("pantry shelf cobalt front", (0.668, 0.003, 0.007), (0, -0.149, -0.007), "blue_edge", 0.0003),
        ]

    @staticmethod
    def _show(objects):
        for obj in objects:
            obj.hide_render = False

    def _pose(self, at, target, lens=62, aperture=7.1):
        camera = self.camera
        camera.data.type = "PERSP"
        camera.data.lens = lens
        camera.data.sensor_width = 36
        camera.data.clip_start = 0.005
        camera.data.clip_end = 200
        camera.location = at
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.dof.use_dof = True
        camera.data.dof.focus_object = None
        camera.data.dof.focus_distance = (Vector(target) - camera.location).length
        camera.data.dof.aperture_fstop = aperture

    def _reset_pack(self):
        self.pack_root.location = (0, 0, 0)
        self.pack_root.rotation_euler = (0, 0, 0)
        for i, (root, parts) in enumerate(self.cans):
            root.location = (((i % 4) - 1.5) * 0.069, ((i // 4) - 1) * 0.069, 0.002)
            self._show(parts)

    def draw(self, shot, t, duration):
        for obj in self.objects:
            obj.hide_render = True
        if shot not in {"can", "case", "carry", "shelf"}:
            return
        self._show(self.groups["stage"] if shot in {"can", "case"} else self.groups["context_floor"])
        self._show(self.groups["lights"])
        u = min(1.0, max(0.0, t / max(duration, 0.001)))
        e = _ease(u)

        if shot == "can":
            self._show(self.hero)
            self.hero_root.location = (0, 0, 0)
            self.hero_root.rotation_euler = (0, 0, _mix(-0.10, 0.22, e))
            angle = _mix(-1.28, -1.13, e)
            radius = _mix(0.465, 0.485, e)
            self._pose((radius * math.cos(angle), radius * math.sin(angle),
                        _mix(0.198, 0.211, e)), (0, 0, 0.063), 68, 6.3)
            return

        self._reset_pack()
        if shot == "case":
            # A calm widening move reveals the quantity in the same object.
            self._show(self.carton)
            self.pack_root.rotation_euler.z = _mix(0.04, -0.045, e)
            radius = _mix(0.665, 0.845, e)
            angle = _mix(-1.20, -1.12, e)
            self._pose((radius * math.cos(angle), radius * math.sin(angle),
                        _mix(0.328, 0.430, e)), (0, 0, 0.058), 63, 9.0)
            return

        if shot == "carry":
            phase = min(2, int(t / (duration / 3)))
            context = ("cargo", "counter", "shelf")[phase]
            self._show(self.groups[context])
            self._show(self.carton)
            # Matched camera and pack motion holds the package at a consistent
            # screen position as the three real surfaces cut beneath it.
            x = _mix(-0.12, 0.12, u)
            self.pack_root.location.x = x
            self.pack_root.rotation_euler.z = -0.045
            self._pose((0.36 + x * 0.45, -0.79, 0.365),
                       (x * 0.45, 0.01, 0.070), 58, 8.0)
            return

        self._show(self.groups["shelf"])
        # Inventory leaves in discrete edit beats, front to back. A brief
        # forward lift reads as removal, while the untouched shelf holds.
        for i, (root, parts) in enumerate(self.cans):
            remove = 0.32 + i * 0.225
            progress = (t - remove) / 0.15
            if progress >= 1:
                for obj in parts:
                    obj.hide_render = True
            elif progress > 0:
                q = _ease(progress)
                root.location.y -= 0.31 * q
                root.location.z += 0.09 * math.sin(q * math.pi * 0.65)
        self._pose((_mix(0.31, 0.27, e), _mix(-0.79, -0.74, e),
                    _mix(0.310, 0.285, e)), (0, 0.015, 0.068), 58, 8.0)


def create(g):
    return Errands(g)
