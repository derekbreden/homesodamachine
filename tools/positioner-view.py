#!/usr/bin/env python3
"""Build /positioner's display mesh from the fixture CAD and pinned references.

Run tools/cad-venv/bin/python tools/positioner-view.py after the PGFUN build
and check have produced assembly-meshes.npz and reference-meshes.npz.
Display tessellation is reduced; the linked STEP files retain precise geometry.
"""
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "hardware/printed-parts/fixtures/pgfun-positioner"
OUTPUT = ROOT / "web/public/assemblies/pgfun-positioner.json.gz"


def build():
    info = {x["name"]: x for x in json.loads((CAD / "display-meshes.json").read_text())}
    binding = json.loads((CAD / "motion-geometry.json").read_text())
    references = json.loads((CAD / "reference-source.json").read_text())
    for relative, expected in binding["motion"]["mechanical_sources"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    assert hashlib.sha256((CAD / "reference-meshes.npz").read_bytes()).hexdigest() == references["mesh_sha256"]
    spec = importlib.util.spec_from_file_location("pgfun_view_check", CAD / "check.py")
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    assert all(binding["motion"][key] == value for key, value in check.D.items()), "Rebuild CAD after changing design.json"
    pivot = np.array([*check.D["yaw_xy"], check.D["pivot_z"]])
    parts = []
    for filename in ["assembly-meshes.npz", "reference-meshes.npz"]:
        with np.load(CAD / filename) as source:
            for key in source.files:
                if not key.endswith("__v"):
                    continue
                name = key[:-3]
                vertices, faces = source[key], source[name + "__f"]
                item = info.get(name, dict(group="pitch" if name.startswith("gun:") else "fixed", category="reference"))
                if name.startswith("gun:"):
                    transform = check.gun_transform()
                    vertices = vertices @ transform[:3, :3].T + transform[:3, 3]
                if item["group"] in ("pitch", "yaw"):
                    vertices = vertices - pivot
                mesh = trimesh.Trimesh(vertices, faces, process=True)
                mesh.vertices = np.round(mesh.vertices / 0.4) * 0.4
                mesh.merge_vertices(digits_vertex=2)
                mesh.update_faces(mesh.nondegenerate_faces())
                target = 900 if name in ("fork", "left-cheek", "lower-cradle", "camera-riser-base", "camera-riser-top") or name.startswith(("gun:housing", "rotator:")) else 250
                if len(mesh.faces) > target:
                    center, scale = mesh.vertices.mean(axis=0), max(mesh.extents)
                    mesh.vertices = (mesh.vertices - center) / scale
                    mesh = mesh.simplify_quadric_decimation(face_count=target, aggression=7)
                    mesh.vertices = mesh.vertices * scale + center
                quantized = np.rint(mesh.vertices / 0.02)
                assert np.max(np.abs(quantized)) < 32768 and len(mesh.vertices) <= 65536, name
                parts.append(dict(
                    name=name, group=item["group"], category=item["category"],
                    v=base64.b64encode(quantized.astype("<i2").tobytes()).decode(),
                    f=base64.b64encode(mesh.faces.astype("<u2").tobytes()).decode(),
                ))
    payload = dict(
        revision=check.D["revision"], geometrySha256=binding["sha256"],
        coordinateScale=0.02, pivot=pivot.tolist(), softLimitDeg=check.D["soft_limit_deg"], parts=parts,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(gzip.compress(json.dumps(payload, separators=(",", ":")).encode(), mtime=0))
    print(json.dumps(dict(path=str(OUTPUT.relative_to(ROOT)), bytes=OUTPUT.stat().st_size, parts=len(parts))))


if __name__ == "__main__":
    build()
