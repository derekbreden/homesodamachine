"""The enclosure print field's numeric handoff to its Rust producer.

The smooth structural solid remains the enclosure builder's. One print mesh is handed to
the field at a time, with the same sampled rails and plain lands as ``flute_skin``.
"""

import json
import struct
import tempfile
from pathlib import Path

import numpy as np
import trimesh

import _rust_part
import flute_skin
import reeding


def _write_mesh(path, mesh):
    """Write the existing arrays directly; joining their bytes would duplicate a full mesh."""
    with path.open("wb") as stream:
        stream.write(struct.pack("<QQ", len(mesh.vertices), len(mesh.faces)))
        np.asarray(mesh.vertices, dtype="<f8").tofile(stream)
        np.asarray(mesh.faces, dtype="<i8").view("<u8").tofile(stream)


def _read_mesh(path):
    with path.open("rb") as stream:
        vertices, triangles = struct.unpack("<QQ", stream.read(16))
        points = np.fromfile(stream, dtype="<f8", count=3 * vertices).reshape((-1, 3))
        faces = np.fromfile(stream, dtype="<i8", count=3 * triangles).reshape((-1, 3))
        if len(points) != vertices or len(faces) != triangles or stream.read(1):
            raise ValueError("enclosure-skin did not write the mesh arrays it named")
    return trimesh.Trimesh(vertices=points, faces=faces, process=False)


def numbers(mesh_path, rails, pitch, depth, rise):
    """The existing field's sampling, shape and exact rail frames; no native geometry."""
    frames = []
    for rail in rails:
        if rail.berthed:
            raise ValueError("the enclosure's exterior print rail has no berthed bodies")
        s, point, normal = flute_skin._rail_frames(rail)
        frames.append({"s": s.tolist(), "point": point.tolist(), "normal": normal.tolist(),
                       "closed": rail.closed, "band": rail.band, "plain": rail.plain})
    return {
        "mesh": str(mesh_path),
        "field": {
            "across": flute_skin.grid_across, "along": flute_skin.grid_along,
            "margin": flute_skin.cut_margin, "overrun": flute_skin.cut_overrun,
            "plan_tol": flute_skin.plan_tol, "face_tol": flute_skin.face_tol,
            "pitch": pitch, "width": reeding.flute_width, "depth": depth, "rise": rise,
        },
        "rails": frames,
    }


def flute(mesh, rails, pitch, depth, rise):
    """The enclosure's print mesh through the Rust flute field, one mesh per handoff."""
    if not rails:
        return mesh
    with tempfile.TemporaryDirectory(prefix="hsm-enclosure-skin-") as directory:
        directory = Path(directory)
        mesh_path = directory / "smooth.bin"
        _write_mesh(mesh_path, mesh)
        description = directory / "enclosure-skin.numbers.json"
        description.write_text(json.dumps(numbers(mesh_path, rails, pitch, depth, rise),
                                          separators=(",", ":")) + "\n")
        _rust_part.run("enclosure-shell", "enclosure-skin", description, directory)
        return _read_mesh(directory / "enclosure-skin.bin")
