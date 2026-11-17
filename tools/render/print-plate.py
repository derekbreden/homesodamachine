#!/usr/bin/env python3
"""Turn the printable objects and their poses in a Bambu project into a plate thumbnail."""

import argparse
from collections import Counter
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
MODEL = "3D/3dmodel.model"
PATH = "{http://schemas.microsoft.com/3dmanufacturing/production/2015/06}path"
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
OUTPUT = ROOT / "web/public/parts/plates"


def metadata(node):
    return {row.get("key"): row.get("value") for row in node.findall("metadata")}


def transform(node):
    pose = np.eye(4)
    pose[:, :3] = np.fromstring(node.get("transform", IDENTITY), sep=" ").reshape(4, 3)
    return pose


def mesh_objects(project, plate):
    """Read printable volumes in the selected plate's physical bed frame."""
    config = ET.fromstring(project.read("Metadata/model_settings.config"))
    plates = config.findall("plate")
    selected = plates[plate - 1]
    instances = {
        (m["object_id"], int(m.get("instance_id", 0)))
        for m in map(metadata, selected.findall("model_instance"))
    }
    objects = {row.get("id"): row for row in config.findall("object")}
    settings = json.loads(project.read("Metadata/project_settings.config"))
    limits = np.array([list(map(float, point.split("x"))) for point in settings["printable_area"]])
    low, high = limits.min(axis=0), limits.max(axis=0)
    colors = settings["filament_colour"]
    model = ET.fromstring(project.read(MODEL))
    seen = Counter()
    solids = []

    def walk(node, pose, parts, filament):
        mesh = node.find("{*}mesh")
        if mesh is not None:
            vertices = np.array([
                [float(row.get(axis)) for axis in "xyz"]
                for row in mesh.find("{*}vertices")
            ])
            triangles = np.array([
                [int(row.get(key)) for key in ("v1", "v2", "v3")]
                for row in mesh.find("{*}triangles")
            ], dtype=np.uint32)
            points = vertices @ pose[:3, :3] + pose[3, :3]
            if np.linalg.det(pose[:3, :3]) < 0:
                triangles = triangles[:, ::-1]
            solids.append((points, triangles, filament))
            return
        for component in node.findall("{*}components/{*}component"):
            volume = component.get("objectid")
            part = parts.get(volume)
            if part is not None and part.get("subtype") != "normal_part":
                continue
            external = component.get(PATH)
            source = ET.fromstring(project.read(external.lstrip("/"))) if external else model
            child = source.find(f"{{*}}resources/{{*}}object[@id='{volume}']")
            extruder = metadata(part).get("extruder", filament) if part is not None else filament
            walk(child, transform(component) @ pose, parts, extruder)

    for item in model.findall("{*}build/{*}item"):
        object_id = item.get("objectid")
        serial = seen[object_id]
        seen[object_id] += 1
        if (object_id, serial) not in instances or item.get("printable", "1") == "0":
            continue
        config_object = objects[object_id]
        parts = {part.get("id"): part for part in config_object.findall("part")}
        node = model.find(f"{{*}}resources/{{*}}object[@id='{object_id}']")
        walk(node, transform(item), parts, metadata(config_object).get("extruder", "1"))
    if not solids:
        raise ValueError(f"no printable geometry on plate {plate}")

    # Other plates occupy full beds plus the gutter in Bambu's logical layout. Read the
    # physical frame from where this plate's objects fit, independent of the grid's columns.
    if len(plates) > 1:
        bounds = np.array([
            np.min([p[:, :2].min(axis=0) for p, _, _ in solids], axis=0),
            np.max([p[:, :2].max(axis=0) for p, _, _ in solids], axis=0),
        ])
        pitch = (high - low) * 1.2
        origin = np.round((bounds.mean(axis=0) - (high + low) / 2) / pitch) * pitch
        for points, _, _ in solids:
            points[:, :2] -= origin
    return low, high, colors, solids


def box(low, high):
    x, y, z = low
    w, d, h = high
    vertices = np.array([(x, y, z), (w, y, z), (w, d, z), (x, d, z),
                         (x, y, h), (w, y, h), (w, d, h), (x, d, h)])
    edges = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4),
             (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)]
    return vertices, np.array(edges, dtype=np.uint32)


def linear(color):
    rgb = np.array([int(color[i:i+2], 16) for i in (1, 3, 5)]) / 255
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4).tolist()


def surface(color):
    if color.endswith("00") and len(color) == 9:
        return "#a9c3cf"
    if color[:7] in {"#000000", "#161616", "#111111"}:
        return "#344051"
    return color[:7]


def payload(project, plate, output):
    with ZipFile(project) as archive:
        (x, y), (w, d), colors, solids = mesh_objects(archive, plate)
    rows, blob = [], bytearray()

    def put(values, dtype):
        values = np.ascontiguousarray(values, dtype=dtype)
        location = [len(blob), values.size]
        blob.extend(values.tobytes())
        return location

    def add(name, vertices, triangles, color, flat=False):
        p, q, r = vertices[triangles].transpose(1, 0, 2)
        faces = np.cross(q - p, r - p)
        if flat:
            vertices = vertices[triangles].reshape(-1, 3)
            triangles = np.arange(len(vertices), dtype=np.uint32)
            normals = np.repeat(faces, 3, axis=0)
        else:
            normals = np.zeros_like(vertices)
            for indices in triangles.T:
                np.add.at(normals, indices, faces)
        lengths = np.linalg.norm(normals, axis=1)
        normals /= np.where(lengths > 0, lengths, 1)[:, None]
        rows.append({"name": name, "color": linear(color), "pos": put(vertices, "<f4"),
                     "nrm": put(normals, "<f4"), "idx": put(triangles, "<u4"), "fac": [0, 0]})

    add("bed", *box((x, y, -5), (w, d, 0)), "#8195ac", flat=True)
    for axis, start, end in (("x", x, w), ("y", y, d)):
        for i, coordinate in enumerate(np.arange(start + 20, end, 20)):
            corners = ((coordinate - .22, y, 0), (coordinate + .22, d, .05)) if axis == "x" else (
                (x, coordinate - .22, 0), (w, coordinate + .22, .05)
            )
            add(f"bed-grid-{axis}-{i}", *box(*corners), "#9eaec0", flat=True)
    for i, (points, triangles, filament) in enumerate(solids):
        add(f"part-{i}", points, triangles, surface(colors[int(filament) - 1]))
    header = json.dumps({"v": 3, "meshes": rows}, separators=(",", ":")).encode()
    header += b" " * (-len(header) % 4)
    output.write_bytes(struct.pack("<I", len(header)) + header + blob)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plates", nargs="+", metavar="ID=PROJECT.3mf[:PLATE]")
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="parts-plate-render-", dir=ROOT / ".cache/runs") as scratch:
        scratch = Path(scratch)
        jobs = []
        for entry in args.plates:
            name, source = entry.split("=", 1)
            project, sep, plate = source.partition(":")
            if Path(name).name != name or not name:
                parser.error("an ID must be a filename stem")
            mesh = scratch / f"{name}.mesh"
            picture = scratch / f"{name}.png"
            payload(Path(project), int(plate) if sep else 1, mesh)
            jobs.append({
                "payload": str(mesh), "out": str(picture), "size": "640x560",
                "cam": [0.65, -1, 1.25], "transparent": True, "ortho": True,
                "margin": 1.54, "ground": False, "fog": False,
                "materials": [
                    {"names": ["bed", "bed-grid-*"], "roughness": .87, "metalness": .10},
                    {"names": ["part-*"], "roughness": .55, "metalness": .02},
                ],
            })
        renderer = ROOT / "tools/hsm/target/release/hsm-render"
        subprocess.run([renderer, "--jobs", "-"], input=json.dumps(jobs), text=True, check=True, cwd=ROOT)
        subprocess.run([
            "node", "--input-type=module", "-e",
            """import path from 'node:path';
import sharp from './tools/render/node_modules/sharp/dist/index.mjs';
const [source, destination, ...files] = process.argv.slice(1);
for (const file of files) {
  await sharp(path.join(source, file + '.png')).webp({ quality: 84 })
    .toFile(path.join(destination, file + '.webp'));
}""",
            scratch, OUTPUT, *(Path(job["out"]).stem for job in jobs),
        ], check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
