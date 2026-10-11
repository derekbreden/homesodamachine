"""Draw the reference from the same triangles supplied to the slicer."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(ROOT / "hardware/scripts"))
import _mesh_payload
from flute_payload import cut


def write_reference_payloads(manifest):
    meshes = []
    for row in manifest["printable"]:
        surface = cut(ROOT / row["step"], ROOT / row["stl"], verbose=False,
                      preserve_print_triangles=True)
        # The generator rotates about world X, then Y, then Z before placing.
        rotation = np.eye(3)
        for axis, angle in enumerate(row["assembly"]["rotation_xyz_degrees"]):
            c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
            matrices = (
                np.array([[1, 0, 0], [0, c, -s], [0, s, c]]),
                np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
                np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]),
            )
            rotation = matrices[axis] @ rotation
        position = np.asarray(surface["pos"]).reshape(-1, 3) @ rotation.T
        position += row["assembly"]["translation_mm"]
        normals = np.asarray(surface["nrm"]).reshape(-1, 3) @ rotation.T
        meshes.append({**surface, "name": row["name"],
                       "pos": position.ravel().tolist(),
                       "nrm": normals.ravel().tolist()})
    step = HERE / manifest["assembly"]
    _mesh_payload.write(meshes, str(step) + ".mesh",
                        src=_mesh_payload.source_digest(step),
                        cut={"dev": 0, "bound": 0})
    print(f"Viewer: {len(meshes)} components, all print triangles retained")


if __name__ == "__main__":
    write_reference_payloads(json.loads((HERE / "manifest.json").read_text()))
