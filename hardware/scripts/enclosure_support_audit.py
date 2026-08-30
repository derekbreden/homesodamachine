#!/usr/bin/env python3
"""Measure the support-removal topology in a production-profile Bambu G-code export.

The CAD assembly can prove that a ramp exists, but only the slicer knows whether it emitted a
support, where that support begins, and how many separate interfaces a hand has to remove. This
reader follows ``Support`` and ``Support interface`` extrusion paths through the layers and
reports the independent readings stated by the enclosure's support-removal policy.

Typical use after slicing a current enclosure STL with its named production 3MF profile::

    python3 hardware/scripts/enclosure_support_audit.py \
        --piece enclosure-back-top --gcode /tmp/plate_1.gcode \
        --model hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl \
        --profile hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf

Pass ``--json-out`` to retain the reading. The G-code is deliberately not committed: it is a
large derived file, while the compact JSON records its digest, model and profile inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


GRID_MM = 0.4
TREE_LINK_MM = 0.85
INTERFACE_LINK_MM = 1.25
SHORT_MM = 5.0
DECENT_MM = 10.0
SATURATED_MM = 15.0

_WORD = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
_DEFAULT_SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")


class DisjointSet:
    def __init__(self):
        self.parent: list[int] = []
        self.rank: list[int] = []

    def add(self) -> int:
        n = len(self.parent)
        self.parent.append(n)
        self.rank.append(0)
        return n

    def find(self, n: int) -> int:
        while self.parent[n] != n:
            self.parent[n] = self.parent[self.parent[n]]
            n = self.parent[n]
        return n

    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a == b:
            return
        if self.rank[a] < self.rank[b]:
            a, b = b, a
        self.parent[b] = a
        if self.rank[a] == self.rank[b]:
            self.rank[a] += 1


@dataclass
class LayerNode:
    z: float
    cells: set[tuple[int, int]]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _transform_values(value: str | None) -> list[float]:
    return [float(v) for v in
            (value or "1 0 0 0 1 0 0 0 1 0 0 0").split()]


def _matrix_multiply(a: list[float], b: list[float]) -> list[float]:
    return [sum(a[row * 3 + k] * b[k * 3 + col] for k in range(3))
            for row in range(3) for col in range(3)]


def _row_multiply(point: tuple[float, float, float] | list[float],
                  matrix: list[float]) -> tuple[float, float, float]:
    return tuple(sum(point[row] * matrix[row * 3 + col] for row in range(3))
                 for col in range(3))


def _affine_compose(first: list[float], second: list[float]) -> list[float]:
    """The 3MF row-vector transform which applies ``first`` and then ``second``."""
    matrix = _matrix_multiply(first[:9], second[:9])
    translated = _row_multiply(first[9:12], second[:9])
    return matrix + [translated[i] + second[9 + i] for i in range(3)]


def _matrix_inverse(matrix: list[float]) -> list[float]:
    a, b, c, d, e, f, g, h, i = matrix
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) <= 1e-12:
        raise RuntimeError("the profile has a singular object transform")
    return [
        (e * i - f * h) / det, (c * h - b * i) / det, (b * f - c * e) / det,
        (f * g - d * i) / det, (a * i - c * g) / det, (c * d - a * f) / det,
        (d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det,
    ]


def _affine_apply(point: tuple[float, float, float] | list[float],
                  transform: list[float]) -> tuple[float, float, float]:
    rotated = _row_multiply(point, transform[:9])
    return tuple(rotated[i] + transform[9 + i] for i in range(3))


def _affine_inverse(transform: list[float]) -> list[float]:
    matrix = _matrix_inverse(transform[:9])
    translated = _row_multiply([-v for v in transform[9:12]], matrix)
    return matrix + list(translated)


def _metadata_values(payload: bytes, keys: set[str]) -> dict[str, str]:
    root = ET.fromstring(payload)
    return {element.attrib["key"]: element.attrib["value"]
            for element in root.iter("metadata")
            if element.attrib.get("key") in keys}


def _reseat_build_item(model_payload: bytes, object_payload: bytes) -> tuple[bytes, float]:
    """Move a replacement object's lowest transformed vertex back onto plate Z zero."""
    model_root = ET.fromstring(model_payload)
    item = next(element for element in model_root.iter() if element.tag.endswith("}item"))
    component = next(element for element in model_root.iter()
                     if element.tag.endswith("}component"))
    build = _transform_values(item.attrib.get("transform"))
    component_transform = _transform_values(component.attrib.get("transform"))
    combined = _affine_compose(component_transform, build)

    object_root = ET.fromstring(object_payload)
    lowest = min(_affine_apply(tuple(float(vertex.attrib[axis]) for axis in "xyz"),
                               combined)[2]
                 for vertex in object_root.iter() if vertex.tag.endswith("}vertex"))
    shift = -lowest if abs(lowest) > 1e-6 else 0.0
    if not shift:
        return model_payload, shift
    old = item.attrib["transform"].encode()
    build[11] += shift
    new = " ".join(f"{value:.12g}" for value in build).encode()
    pattern = rb'(<item\b[^>]*\btransform=")' + re.escape(old) + rb'(")'
    model_payload, count = re.subn(pattern, rb'\g<1>' + new + rb'\2', model_payload,
                                   count=1)
    if count != 1:
        raise RuntimeError("the project has no replaceable build-item transform")
    return model_payload, shift


def _current_profile_slice(model: Path, profile: Path, slicer: Path,
                           directory: Path) -> tuple[Path, Path, float]:
    """Put ``model`` into a temporary copy of ``profile`` and slice its exact settings.

    Loading a project's JSON with ``--load-settings`` is not equivalent: Bambu rejects settings
    whose provenance is ``project``, and removing that marker asks installed presets to fill the
    gaps. The project itself is authoritative. Bambu first converts the current STL into its
    normalized object member; that member alone replaces the template's stale mesh, while every
    process, printer, filament and plate setting remains the profile's own.
    """
    mesh_project = directory / "current-mesh.3mf"
    subprocess.run([
        str(slicer), "--export-3mf", str(mesh_project), "--arrange", "0", "--orient", "0",
        str(model),
    ], check=True)

    current_project = directory / "current-profile.3mf"
    with zipfile.ZipFile(profile) as template, zipfile.ZipFile(mesh_project) as current:
        template_object = next(name for name in template.namelist()
                               if name.startswith("3D/Objects/") and name.endswith(".model"))
        current_object = next(name for name in current.namelist()
                              if name.startswith("3D/Objects/") and name.endswith(".model"))
        old_object = template.read(template_object)
        new_object = current.read(current_object)
        old_uuid = re.search(rb'<object id="1" p:UUID="([^"]+)"', old_object)
        new_uuid = re.search(rb'<object id="1" p:UUID="([^"]+)"', new_object)
        if not old_uuid or not new_uuid:
            raise RuntimeError("the template or current 3MF has no replaceable object UUID")
        new_object = new_object.replace(new_uuid.group(1), old_uuid.group(1), 1)

        new_settings = current.read("Metadata/model_settings.config")
        object_settings = re.search(
            rb'  <object\b[^>]*>.*?  </object>', new_settings, flags=re.DOTALL)
        if not object_settings:
            raise RuntimeError("the replacement project has no object settings")
        offset_keys = {"source_offset_x", "source_offset_y", "source_offset_z"}
        source_offsets = _metadata_values(new_settings, offset_keys)
        if source_offsets.keys() != offset_keys:
            missing = ", ".join(sorted(offset_keys - source_offsets.keys()))
            raise RuntimeError(f"the replacement project has no {missing} metadata")
        build_model = template.read("3D/3dmodel.model")
        build_model, bed_shift = _reseat_build_item(build_model, new_object)
        with zipfile.ZipFile(current_project, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6) as output:
            for info in template.infolist():
                if info.filename == template_object:
                    payload = new_object
                elif info.filename == "3D/3dmodel.model":
                    payload = build_model
                else:
                    payload = template.read(info.filename)
                    if info.filename == "Metadata/model_settings.config":
                        payload, count = re.subn(
                            rb'  <object\b[^>]*>.*?  </object>', object_settings.group(0),
                            payload, count=1, flags=re.DOTALL)
                        if count != 1:
                            raise RuntimeError("the profile has no replaceable object settings")
                output.writestr(info, payload)

    output_dir = directory / "slice"
    output_dir.mkdir()
    subprocess.run([
        str(slicer), "--slice", "0", "--outputdir", str(output_dir), str(current_project),
    ], check=True)
    gcodes = sorted(output_dir.glob("plate_*.gcode"))
    if len(gcodes) != 1:
        raise RuntimeError(f"expected one plate G-code, found {len(gcodes)} in {output_dir}")
    return gcodes[0], current_project, bed_shift


def _profile_cad_transform(profile: Path | None) -> list[float] | None:
    """Full row-vector transform from plate coordinates back into the CAD frame."""
    if profile is None:
        return None
    with zipfile.ZipFile(profile) as project:
        settings = ET.fromstring(project.read("Metadata/model_settings.config"))
        source = {}
        for metadata in settings.iter("metadata"):
            key = metadata.attrib.get("key")
            if key in {"source_offset_x", "source_offset_y", "source_offset_z"}:
                source[key[-1]] = float(metadata.attrib["value"])
        model = ET.fromstring(project.read("3D/3dmodel.model"))
        item = next(element for element in model.iter() if element.tag.endswith("}item"))
        build = _transform_values(item.attrib.get("transform"))
        component = next(element for element in model.iter()
                         if element.tag.endswith("}component"))
        component_transform = _transform_values(component.attrib.get("transform"))
    if len(source) != 3 or len(build) != 12 or len(component_transform) != 12:
        return None
    local_to_plate = _affine_compose(component_transform, build)
    plate_to_local = _affine_inverse(local_to_plate)
    plate_to_cad = list(plate_to_local)
    for i, axis in enumerate("xyz"):
        plate_to_cad[9 + i] += source[axis]
    return plate_to_cad


def _transform_bbox(bbox: list[float], transform: list[float]) -> list[float]:
    points = [_affine_apply((x, y, z), transform)
              for x in (bbox[0], bbox[3])
              for y in (bbox[1], bbox[4])
              for z in (bbox[2], bbox[5])]
    return [round(min(point[axis] for point in points), 3) for axis in range(3)] + [
        round(max(point[axis] for point in points), 3) for axis in range(3)]


def _q(value: float) -> int:
    return math.floor(value / GRID_MM + 0.5)


def _mark_line(cells: set[tuple[int, int]], a: tuple[float, float],
               b: tuple[float, float]) -> None:
    distance = math.hypot(b[0] - a[0], b[1] - a[1])
    count = max(1, math.ceil(distance / (GRID_MM * 0.45)))
    for i in range(count + 1):
        t = i / count
        cells.add((_q(a[0] + (b[0] - a[0]) * t),
                   _q(a[1] + (b[1] - a[1]) * t)))


def _arc_points(start: tuple[float, float], end: tuple[float, float], words: dict,
                clockwise: bool) -> list[tuple[float, float]]:
    """Endpoints along one XY arc; malformed or R-only arcs safely fall back to a chord."""
    if "I" not in words or "J" not in words:
        return [end]
    cx, cy = start[0] + words["I"], start[1] + words["J"]
    radius = math.hypot(start[0] - cx, start[1] - cy)
    if radius <= 1e-9:
        return [end]
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    a1 = math.atan2(end[1] - cy, end[0] - cx)
    if clockwise:
        while a1 >= a0:
            a1 -= 2.0 * math.pi
    else:
        while a1 <= a0:
            a1 += 2.0 * math.pi
    turns = max(1, int(round(words.get("P", 1.0))))
    sweep = (a1 - a0) + math.copysign(2.0 * math.pi * (turns - 1), a1 - a0)
    count = max(1, math.ceil(abs(sweep) * radius / (GRID_MM * 0.45)))
    return [(cx + radius * math.cos(a0 + sweep * i / count),
             cy + radius * math.sin(a0 + sweep * i / count))
            for i in range(1, count + 1)]


def _components(cells: set[tuple[int, int]], link_mm: float) -> list[set[tuple[int, int]]]:
    remaining = set(cells)
    answer = []
    reach = max(1, math.ceil(link_mm / GRID_MM))
    offsets = [(dx, dy) for dx in range(-reach, reach + 1)
               for dy in range(-reach, reach + 1)
               if dx or dy if math.hypot(dx * GRID_MM, dy * GRID_MM) <= link_mm + 1e-9]
    while remaining:
        seed = remaining.pop()
        component, stack = {seed}, [seed]
        while stack:
            x, y = stack.pop()
            for dx, dy in offsets:
                neighbour = (x + dx, y + dy)
                if neighbour in remaining:
                    remaining.remove(neighbour)
                    component.add(neighbour)
                    stack.append(neighbour)
        answer.append(component)
    return answer


def _near_nodes(cells: set[tuple[int, int]], previous: dict[tuple[int, int], int],
                link_mm: float) -> set[int]:
    reach = max(1, math.ceil(link_mm / GRID_MM))
    offsets = [(dx, dy) for dx in range(-reach, reach + 1)
               for dy in range(-reach, reach + 1)
               if math.hypot(dx * GRID_MM, dy * GRID_MM) <= link_mm + 1e-9]
    return {node for x, y in cells for dx, dy in offsets
            if (node := previous.get((x + dx, y + dy))) is not None}


def _bbox(cells: set[tuple[int, int]]) -> list[float]:
    xs, ys = zip(*cells)
    return [round(min(xs) * GRID_MM, 2), round(min(ys) * GRID_MM, 2),
            round(max(xs) * GRID_MM, 2), round(max(ys) * GRID_MM, 2)]


def _merge_bbox(a: list[float], b: list[float]) -> list[float]:
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def audit(gcode: Path, piece: str, model: Path | None = None,
          profile: Path | None = None, coordinate_profile: Path | None = None,
          bed_reseat_mm: float | None = None) -> dict:
    tree_set, island_set = DisjointSet(), DisjointSet()
    tree_nodes: list[LayerNode] = []
    island_nodes: list[LayerNode] = []
    island_tree_nodes: dict[int, set[int]] = defaultdict(set)
    previous_tree: dict[tuple[int, int], int] = {}
    previous_island: dict[tuple[int, int], int] = {}

    z = None
    layer_total: set[tuple[int, int]] = set()
    layer_interface: set[tuple[int, int]] = set()
    first_layer_z = None

    x = y = e = 0.0
    absolute_xy, relative_e = True, True
    feature = ""
    settings = {}
    slicer_version = None
    cad_transform = _profile_cad_transform(coordinate_profile or profile)

    def finish_layer() -> None:
        nonlocal previous_tree, previous_island, first_layer_z
        if z is None:
            return
        if layer_total and first_layer_z is None:
            first_layer_z = z

        tree_lookup: dict[tuple[int, int], int] = {}
        for cells in _components(layer_total, TREE_LINK_MM):
            node = tree_set.add()
            tree_nodes.append(LayerNode(z, cells))
            for old in _near_nodes(cells, previous_tree, TREE_LINK_MM):
                tree_set.union(node, old)
            for cell in cells:
                tree_lookup[cell] = node

        island_lookup: dict[tuple[int, int], int] = {}
        for cells in _components(layer_interface, INTERFACE_LINK_MM):
            node = island_set.add()
            island_nodes.append(LayerNode(z, cells))
            for old in _near_nodes(cells, previous_island, INTERFACE_LINK_MM):
                island_set.union(node, old)
            owners = {tree_lookup[cell] for cell in cells if cell in tree_lookup}
            island_tree_nodes[node].update(owners)
            for cell in cells:
                island_lookup[cell] = node

        previous_tree = tree_lookup
        previous_island = island_lookup

    with gcode.open("r", encoding="utf-8", errors="replace") as stream:
        for raw in stream:
            line = raw.strip()
            if line.startswith("; BambuStudio "):
                slicer_version = line[2:].strip()
            if line.startswith("; Z_HEIGHT:"):
                finish_layer()
                z = float(line.split(":", 1)[1])
                layer_total, layer_interface = set(), set()
                previous_tree = previous_tree if layer_total is not None else {}
                continue
            if line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
                continue
            if line.startswith("; ") and " = " in line and len(settings) < 800:
                key, value = line[2:].split(" = ", 1)
                if key in {"support_type", "support_threshold_angle", "support_on_build_plate_only",
                           "support_top_z_distance", "support_interface_top_layers",
                           "support_interface_spacing", "layer_height"}:
                    settings[key] = value.strip()
                continue
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            command = code.split(None, 1)[0]
            words = {key: float(value) for key, value in _WORD.findall(code)}
            if command == "G90":
                absolute_xy = True
                continue
            if command == "G91":
                absolute_xy = False
                continue
            if command == "M82":
                relative_e = False
                continue
            if command == "M83":
                relative_e = True
                continue
            if command == "G92":
                if "X" in words:
                    x = words["X"]
                if "Y" in words:
                    y = words["Y"]
                if "E" in words:
                    e = words["E"]
                continue
            if command not in {"G0", "G1", "G2", "G3"}:
                continue

            nx = (words.get("X", x) if absolute_xy else x + words.get("X", 0.0))
            ny = (words.get("Y", y) if absolute_xy else y + words.get("Y", 0.0))
            de = words.get("E", 0.0) if relative_e else words.get("E", e) - e
            drawing = (z is not None and feature in {"Support", "Support interface"}
                       and de > 1e-9 and (abs(nx - x) > 1e-9 or abs(ny - y) > 1e-9))
            if drawing:
                target = layer_interface if feature == "Support interface" else layer_total
                points = ([((nx, ny))] if command in {"G0", "G1"}
                          else _arc_points((x, y), (nx, ny), words, command == "G2"))
                start = (x, y)
                for point in points:
                    _mark_line(target, start, point)
                    start = point
                if feature == "Support interface":
                    # Interface material is part of the removable support body too.
                    start = (x, y)
                    for point in points:
                        _mark_line(layer_total, start, point)
                        start = point
            x, y = nx, ny
            if "E" in words:
                e = e + words["E"] if relative_e else words["E"]
    finish_layer()

    tree_groups: dict[int, dict] = {}
    for node, reading in enumerate(tree_nodes):
        root = tree_set.find(node)
        row = tree_groups.setdefault(root, {
            "base_z_mm": reading.z, "top_z_mm": reading.z,
            "bbox_xy_mm": _bbox(reading.cells), "nodes": set(),
        })
        row["base_z_mm"] = min(row["base_z_mm"], reading.z)
        row["top_z_mm"] = max(row["top_z_mm"], reading.z)
        row["bbox_xy_mm"] = _merge_bbox(row["bbox_xy_mm"], _bbox(reading.cells))
        row["nodes"].add(node)

    island_groups: dict[int, dict] = {}
    for node, reading in enumerate(island_nodes):
        root = island_set.find(node)
        row = island_groups.setdefault(root, {
            "first_z_mm": reading.z, "last_z_mm": reading.z,
            "bbox_xy_mm": _bbox(reading.cells), "tree_nodes": set(),
        })
        row["first_z_mm"] = min(row["first_z_mm"], reading.z)
        row["last_z_mm"] = max(row["last_z_mm"], reading.z)
        row["bbox_xy_mm"] = _merge_bbox(row["bbox_xy_mm"], _bbox(reading.cells))
        row["tree_nodes"].update(island_tree_nodes.get(node, ()))

    for row in island_groups.values():
        row["tree_roots"] = {tree_set.find(node) for node in row.pop("tree_nodes")}
    reaching = sorted({root for row in island_groups.values() for root in row["tree_roots"]})
    tree_number = {root: i + 1 for i, root in enumerate(
        sorted(reaching, key=lambda root: (tree_groups[root]["bbox_xy_mm"],
                                           tree_groups[root]["base_z_mm"]))) }

    interfaces = []
    for row in sorted(island_groups.values(), key=lambda item: (item["first_z_mm"],
                                                                 item["bbox_xy_mm"])):
        owners = sorted((root for root in row.pop("tree_roots") if root in tree_number),
                        key=lambda root: tree_number[root])
        if not owners:
            continue
        tree_ids = [f"tree-{tree_number[root]}" for root in owners]
        interface = {
            "id": f"interface-{len(interfaces) + 1}",
            "first_z_mm": round(row["first_z_mm"], 3),
            "last_z_mm": round(row["last_z_mm"], 3),
            "bbox_xy_mm": row["bbox_xy_mm"],
        }
        if len(owners) == 1:
            interface["tree"] = tree_ids[0]
            interface["build_up_mm"] = round(
                row["first_z_mm"] - tree_groups[owners[0]]["base_z_mm"], 3)
        else:
            # An interface island is a contact-region reading, not necessarily one connected
            # support body. Two independently removable trees can reach different passes of
            # the same surface island; keep the island singular and name every body feeding it.
            interface["trees"] = tree_ids
            interface["build_up_by_tree_mm"] = {
                tree_id: round(row["first_z_mm"] - tree_groups[root]["base_z_mm"], 3)
                for root, tree_id in zip(owners, tree_ids)
            }
        interfaces.append(interface)
        if cad_transform:
            interfaces[-1]["bbox_cad_xyz_mm"] = _transform_bbox([
                row["bbox_xy_mm"][0], row["bbox_xy_mm"][1], row["first_z_mm"],
                row["bbox_xy_mm"][2], row["bbox_xy_mm"][3], row["last_z_mm"],
            ], cad_transform)

    by_tree: dict[int, list[dict]] = defaultdict(list)
    for interface in interfaces:
        owners = ([interface["tree"]] if "tree" in interface else interface["trees"])
        for owner in owners:
            by_tree[int(owner.split("-")[1])].append(interface)
    trees = []
    for root in reaching:
        number = tree_number[root]
        row = tree_groups[root]
        contacts = by_tree[number]
        first = min(contact["first_z_mm"] for contact in contacts)
        build = first - row["base_z_mm"]
        bed = first_layer_z is not None and row["base_z_mm"] <= first_layer_z + 1e-6
        trees.append({
            "id": f"tree-{number}",
            "root": "bed" if bed else "model",
            "base_z_mm": round(row["base_z_mm"], 3),
            "first_interface_z_mm": round(first, 3),
            "shortest_build_up_mm": round(build, 3),
            "top_z_mm": round(row["top_z_mm"], 3),
            "bbox_xy_mm": row["bbox_xy_mm"],
            "interfaces": [contact["id"] for contact in contacts],
        })
        if cad_transform:
            trees[-1]["bbox_cad_xyz_mm"] = _transform_bbox([
                row["bbox_xy_mm"][0], row["bbox_xy_mm"][1], row["base_z_mm"],
                row["bbox_xy_mm"][2], row["bbox_xy_mm"][3], row["top_z_mm"],
            ], cad_transform)
    trees.sort(key=lambda row: int(row["id"].split("-")[1]))

    buckets = {"under_5_mm": 0, "5_to_10_mm": 0, "10_to_15_mm": 0, "15_mm_or_more": 0}
    for tree in trees:
        value = tree["shortest_build_up_mm"]
        key = ("under_5_mm" if value < SHORT_MM else
               "5_to_10_mm" if value < DECENT_MM else
               "10_to_15_mm" if value < SATURATED_MM else "15_mm_or_more")
        buckets[key] += 1

    coordinate_frame = None
    if cad_transform:
        coordinate_frame = {
            "plate_to_cad_transform": [round(value, 9) for value in cad_transform],
        }
        identity = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        if all(abs(cad_transform[i] - identity[i]) <= 1e-7 for i in range(9)):
            coordinate_frame["plate_to_cad_translation_mm"] = [
                round(value, 6) for value in cad_transform[9:12]]
        if bed_reseat_mm is not None:
            coordinate_frame["replacement_mesh_bed_reseat_mm"] = round(bed_reseat_mm, 6)

    result = {
        "schema": 1,
        "piece": piece,
        "inputs": {
            "gcode": gcode.name, "gcode_sha256": _sha256(gcode),
            "model": str(model) if model else None,
            "model_sha256": _sha256(model) if model else None,
            "profile": str(profile) if profile else None,
            "profile_sha256": _sha256(profile) if profile else None,
        },
        "slicer": slicer_version,
        "coordinate_frame": coordinate_frame,
        "slicer_settings": settings,
        "policy": {
            "support_count": "minimize connected bodies which reach an interface",
            "root_and_build_up_are_independent": True,
            "build_up_mm": {"defect_under": SHORT_MM, "decent_from": DECENT_MM,
                            "preference_saturates_at": SATURATED_MM},
            "preferred_root": "bed",
        },
        "summary": {
            "support_bodies": len(trees),
            "interface_islands": len(interfaces),
            "bed_rooted_bodies": sum(tree["root"] == "bed" for tree in trees),
            "model_rooted_bodies": sum(tree["root"] == "model" for tree in trees),
            "build_up_buckets": buckets,
            "shortest_build_up_mm": (min((tree["shortest_build_up_mm"] for tree in trees),
                                         default=None)),
        },
        "trees": trees,
        "interfaces": interfaces,
    }
    return result


def _selftest() -> None:
    import tempfile

    fixture = """; support_type = tree(auto)
G90
M83
; Z_HEIGHT: 0.2
; FEATURE: Support
G1 X0 Y0
G1 X1 Y0 E1
; Z_HEIGHT: 0.4
; FEATURE: Support
G1 X0 Y0
G1 X1 Y0 E1
; FEATURE: Support interface
G1 X0 Y0
G1 X1 Y0 E1
; Z_HEIGHT: 2.0
; FEATURE: Support
G1 X10 Y0
G1 X11 Y0 E1
; Z_HEIGHT: 8.0
; FEATURE: Support interface
G1 X10 Y0
G1 X11 Y0 E1
"""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "fixture.gcode"
        path.write_text(fixture)
        result = audit(path, "fixture")
    assert result["summary"]["support_bodies"] == 2, result
    assert result["summary"]["bed_rooted_bodies"] == 1, result
    assert result["summary"]["model_rooted_bodies"] == 1, result
    assert result["summary"]["build_up_buckets"]["under_5_mm"] == 1, result
    assert result["summary"]["build_up_buckets"]["5_to_10_mm"] == 1, result

    shared_fixture = """G90
M83
; Z_HEIGHT: 0.2
; FEATURE: Support
G1 X20 Y0
G1 X21 Y0 E1
G1 X22.5 Y0
G1 X23.5 Y0 E1
; Z_HEIGHT: 0.4
; FEATURE: Support
G1 X20 Y0
G1 X21 Y0 E1
G1 X22.5 Y0
G1 X23.5 Y0 E1
; FEATURE: Support interface
G1 X20 Y0
G1 X21 Y0 E1
G1 X22.5 Y0
G1 X23.5 Y0 E1
"""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "shared-interface.gcode"
        path.write_text(shared_fixture)
        shared = audit(path, "shared-interface")
    assert shared["summary"]["support_bodies"] == 2, shared
    assert shared["summary"]["interface_islands"] == 1, shared
    assert shared["interfaces"][0]["trees"] == ["tree-1", "tree-2"], shared
    assert all(tree["interfaces"] == ["interface-1"] for tree in shared["trees"]), shared

    forward = [0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0,
               10.0, 20.0, 30.0]
    point = (4.0, 5.0, 6.0)
    assert all(abs(a - b) <= 1e-9 for a, b in
               zip(_affine_apply(_affine_apply(point, forward), _affine_inverse(forward)),
                   point))
    assert _transform_bbox([0, 0, 0, 2, 3, 4], forward) == [
        7.0, 20.0, 30.0, 10.0, 22.0, 34.0]
    print("support audit selftest: pass")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--piece")
    parser.add_argument("--gcode", type=Path)
    parser.add_argument("--model", type=Path)
    parser.add_argument("--profile", type=Path)
    parser.add_argument("--slice-current", action="store_true",
                        help="slice --model through a temporary mesh-refreshed copy of --profile")
    parser.add_argument("--refreshed-profile-out", type=Path,
                        help="retain that mesh-refreshed production profile (with --slice-current)")
    parser.add_argument("--slicer", type=Path, default=_DEFAULT_SLICER)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        _selftest()
        return
    if not args.piece:
        parser.error("--piece is required unless --selftest is used")
    if args.slice_current and args.gcode:
        parser.error("use either --gcode or --slice-current, not both")
    if args.refreshed_profile_out and not args.slice_current:
        parser.error("--refreshed-profile-out requires --slice-current")
    if args.slice_current and (not args.model or not args.profile):
        parser.error("--slice-current requires --model and --profile")
    if not args.slice_current and not args.gcode:
        parser.error("--gcode is required unless --slice-current is used")
    for path in (args.gcode, args.model, args.profile,
                 args.slicer if args.slice_current else None):
        if path is not None and not path.is_file():
            parser.error(f"not a file: {path}")
    if args.slice_current:
        with tempfile.TemporaryDirectory(prefix="enclosure-support-audit-") as directory:
            gcode, coordinate_profile, bed_reseat = _current_profile_slice(
                args.model, args.profile, args.slicer, Path(directory))
            result = audit(gcode, args.piece, args.model, args.profile,
                           coordinate_profile, bed_reseat)
            if args.refreshed_profile_out:
                shutil.copyfile(coordinate_profile, args.refreshed_profile_out)
    else:
        result = audit(args.gcode, args.piece, args.model, args.profile)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_out:
        args.json_out.write_text(encoded)
    sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
