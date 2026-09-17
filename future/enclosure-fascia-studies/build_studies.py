"""Exterior meshes and fixed hardware for the enclosure fascia comparison."""
from pathlib import Path
import argparse
import base64
import gzip
import hashlib
import json
import struct
import sys

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PARTS = REPO / "hardware/printed-parts/enclosure/enclosure"
sys.path.insert(0, str(REPO / "hardware/scripts"))
from flute_payload import creased


def payload_meshes(path):
    raw = path.read_bytes()
    size = struct.unpack("<I", raw[:4])[0]
    header = json.loads(raw[4:4 + size])
    data = raw[4 + size:]
    for item in header["meshes"]:
        positions = np.frombuffer(data, "<f4", item["pos"][1], item["pos"][0]).reshape(-1, 3)
        faces = np.frombuffer(data, "<u4", item["idx"][1], item["idx"][0]).reshape(-1, 3)
        yield item["name"], trimesh.Trimesh(positions, faces, process=True)


def main(output):
    geometry = {}
    sources = {}
    def add(name, mesh, role):
        positions, normals, indices, _ = creased(mesh)
        geometry[name] = {"p": positions, "n": normals, "i": indices, "role": role}
        print(name, len(indices), "triangles", flush=True)

    for stem in ("front-bottom", "front-top", "back-bottom", "back-top", "pump-cartridge"):
        source = PARTS / f"enclosure-{stem}.step"
        solid = cq.importers.importStep(str(source)).val()
        positions, faces = solid.tessellate(.035, .075)
        mesh = trimesh.Trimesh([p.toTuple() for p in positions], faces, process=True)
        p = mesh.vertices
        front = np.maximum(5, p[:, 2] - 288.1281566462)
        exterior_distance = np.minimum.reduce([107.5 - np.abs(p[:, 0]), p[:, 1] - front,
                                               467 - p[:, 1], 355 - p[:, 2], p[:, 2] + 6])
        centers = mesh.triangles_center
        distances = np.array([107.5 - np.abs(centers[:, 0]),
                              centers[:, 1] - np.maximum(5, centers[:, 2] - 288.1281566462),
                              467 - centers[:, 1], 355 - centers[:, 2], centers[:, 2] + 6])
        nearest = distances.argmin(axis=0)
        outward = np.zeros_like(centers)
        outward[nearest == 0, 0] = np.sign(centers[nearest == 0, 0])
        outward[nearest == 1, 1] = -1
        outward[nearest == 2, 1] = 1
        outward[nearest == 3, 2] = 1
        outward[nearest == 4, 2] = -1
        keep = (np.any(exterior_distance[mesh.faces] < 5, axis=1)
                & (np.sum(mesh.face_normals * outward, axis=1) > -.35))
        mesh.update_faces(keep)
        mesh.remove_unreferenced_vertices()
        add(stem, mesh, "shell")
        sources[stem] = {"sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                         "vertices": len(mesh.vertices), "triangles": len(mesh.faces)}

    assembly = REPO / "hardware/manifold-layout/enclosure-assembly.step.mesh"
    sources["fixed-hardware"] = {"sha256": hashlib.sha256(assembly.read_bytes()).hexdigest()}
    for name, mesh in payload_meshes(assembly):
        if "-word" in name:
            continue
        role = None
        if name == "funnel": role = "funnel"
        elif name == "display/1": role = "device"
        elif name == "display/2": role = "glass"
        elif name in ("c14-inlet", "keystone-jack", "nameplate") or name.startswith("bulkhead-"): role = "rear"
        elif name in ("cold-core/foam-shell", "compressor/1", "compressor/2", "condenser+fan") or name.startswith(("pump-a-", "pump-b-")): role = "hardware"
        if role:
            if name == "nameplate":
                mesh = mesh.bounding_box
            if role == "hardware":
                mesh = mesh.convex_hull
            if len(mesh.faces) > 1800:
                mesh = mesh.simplify_quadric_decimation(face_count=1800, aggression=3)
            add(name, mesh, role)

    cover_path = REPO / "hardware/printed-parts/enclosure/display-cover/display-cover.step"
    cover = cq.importers.importStep(str(cover_path)).val()
    cover = cover.rotate((0, 0, 0), (1, 0, 0), 45).translate((0, 35.9359216769, 324.0640783231))
    vertices, faces = cover.tessellate(.035, .075)
    add("display-cover", trimesh.Trimesh([v.toTuple() for v in vertices], faces, process=True), "cover")

    blob = bytearray()
    for item in geometry.values():
        for field, scale in (("p", 1000), ("n", 10000), ("i", 1)):
            array = np.rint(item[field] * scale).astype(np.int32)
            if field in ("p", "n"):
                array = np.diff(array.reshape(-1, 3), axis=0, prepend=np.zeros((1, 3), dtype=np.int32))
            else:
                array = np.diff(array.reshape(-1), prepend=0)
            array = array.astype("<i4").reshape(-1)
            item[field] = [len(blob), len(array)]
            blob.extend(array.tobytes())
    header = json.dumps({"meshes": geometry, "sources": sources}, separators=(",", ":")).encode()
    raw = struct.pack("<I", len(header)) + header
    raw += b"\0" * (-len(raw) % 4) + blob
    encoded = base64.b64encode(gzip.compress(raw, 9)).decode()
    (HERE / "models.b64").write_text(encoded)
    (HERE / "sources.json").write_text(json.dumps(sources, indent=2) + "\n")
    compose(output)


def compose(output):
    fragment = (HERE / "fascia.template.html").read_text()
    fragment = fragment.replace("__MODEL_DATA__", (HERE / "models.b64").read_text())
    output.mkdir(parents=True, exist_ok=True)
    target = output / "enclosure-fascia.html"
    target.write_text(fragment)
    print(target, len(fragment.encode()), "bytes", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--compose", action="store_true")
    args = parser.parse_args()
    (compose if args.compose else main)(args.output)
