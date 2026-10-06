#!/usr/bin/env python3
"""Build /positioner's display mesh from the fixture CAD and pinned references.

Run tools/cad-venv/bin/python tools/positioner-view.py after the PGFUN build
and check have produced assembly-meshes.npz and reference-meshes.npz.
Retains every source triangle and coordinate, with normals split at CAD creases.
Float32 positions match the renderer's precision; normals use normalized Int16.
"""
import base64
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "hardware/printed-parts/fixtures/pgfun-positioner"
OUTPUT = ROOT / "web/public/assemblies/pgfun-positioner.json.gz"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from flute_payload import creased


def canonical_faces(faces):
    """Triangle identities independent of ordering, preserving winding."""
    first = np.argmin(faces, axis=1)
    rows = np.arange(len(faces))[:, None]
    ordered = faces[rows, (first[:, None] + np.arange(3)) % 3]
    return ordered[np.lexsort(ordered.T[::-1])]


def display_mesh(mesh):
    positions, normals, faces, _ = creased(mesh)
    assert len(faces) == len(mesh.faces), "Display export lost triangles"
    # Splitting normal regions duplicates vertices without changing a triangle.
    source_ids = {tuple(point): i for i, point in enumerate(mesh.vertices)}
    mapped = np.fromiter((source_ids[tuple(point)] for point in positions), dtype=np.int64)
    assert np.array_equal(canonical_faces(mapped[faces]), canonical_faces(mesh.faces)), "Display export changed a source triangle or its winding"
    packed_positions = positions.astype("<f4")
    assert np.abs(packed_positions - positions).max() < 0.0001, "Float32 position error exceeds 0.1 micron"
    packed_normals = np.rint(normals * 32767).astype("<i2")
    index_type = "uint32" if len(positions) > 65536 else "uint16"
    packed_faces = faces.astype("<u4" if index_type == "uint32" else "<u2")
    return dict(
        v=base64.b64encode(packed_positions.tobytes()).decode(),
        n=base64.b64encode(packed_normals.tobytes()).decode(),
        f=base64.b64encode(packed_faces.tobytes()).decode(),
        indexType=index_type, sourceFaceCount=len(mesh.faces),
        sourceVolumeMm3=float(mesh.volume), sourceClosed=bool(mesh.is_watertight),
    )


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
                mesh = trimesh.Trimesh(vertices, faces, process=False)
                if item["category"] in ("print", "liner"):
                    assert mesh.is_volume, f"{name}: source print is not a closed positive volume"
                parts.append(dict(name=name, group=item["group"], category=item["category"], **display_mesh(mesh)))
    payload = dict(
        revision=check.D["revision"], geometrySha256=binding["sha256"],
        meshFormat="creased-f32-v1", pivot=pivot.tolist(), softLimitDeg=check.D["soft_limit_deg"], parts=parts,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(gzip.compress(json.dumps(payload, separators=(",", ":")).encode(), mtime=0))
    print(json.dumps(dict(path=str(OUTPUT.relative_to(ROOT)), bytes=OUTPUT.stat().st_size, parts=len(parts))))


if __name__ == "__main__":
    build()
