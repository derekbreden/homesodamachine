"""Draw the detailed welding-head GLB's four orthographic inspection views."""
from __future__ import annotations

import argparse
from itertools import product
from pathlib import Path
import sys
import tempfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_OUT = ROOT / "output/xlaserlab-sup29f-xh"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
import _hsm_render
import _mesh_payload


TARGET = np.array((-22., 0., -67.))
VIEWS = (
    ("preview", (200., 400., 220.)),
    ("side", (0., 500., -67.)),
    ("rear", (-420., 175., 110.)),
    ("top", (0., 0., 500.)),
)
SIZE = (1600, 1150)
FRAME_MARGIN = 1.12
BACKGROUND = "#666e75"


def material(name):
    """The inspection palette in linear RGB, with its original surface finishes."""
    if "boot" in name:
        return (.012, .014, .018), .72, 0.
    if "copper" in name:
        rgb = (.40, .13, .06)
    elif any(part in name for part in ("front-nut", "rear-nut", "coupler", "thread", "shank")):
        rgb = (.55, .36, .11)
    else:
        rgb = (.44, .49, .57)
    return rgb, .38, .45


def surfaces(path):
    """The delivered GLB surfaces, in the millimetre Z-up inspection frame."""
    scene = trimesh.load(path, force="scene", process=False)
    # The exporter names metres/Y-up. This is the GLB importer's Y-up to Z-up
    # rotation and the inspection scene's 1000x root scale.
    frame = np.array(((1000., 0., 0., 0.), (0., 0., -1000., 0.),
                      (0., 1000., 0., 0.), (0., 0., 0., 1.)))
    meshes, boxes, finishes = [], [], []
    for name in scene.graph.nodes_geometry:
        transform, geometry = scene.graph[name]
        mesh = scene.geometry[geometry]
        matrix = frame @ transform
        vertices = np.asarray(mesh.vertices) @ matrix[:3, :3].T + matrix[:3, 3]
        faces = np.asarray(mesh.faces, dtype=np.uint32)
        corners = np.array(list(product(*zip(mesh.bounds[0], mesh.bounds[1]))))
        boxes.append(corners @ matrix[:3, :3].T + matrix[:3, 3])
        flat = any(part in name for part in ("hex", "nut", "coupler"))
        if flat:
            vertices = vertices[faces].reshape(-1, 3)
            normals = np.repeat(np.asarray(mesh.face_normals) @ np.linalg.inv(matrix[:3, :3]), 3, axis=0)
            faces = np.arange(len(vertices), dtype=np.uint32).reshape(-1, 3)
        else:
            normals = np.asarray(mesh.vertex_normals) @ np.linalg.inv(matrix[:3, :3])
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        rgb, roughness, metalness = material(name)
        meshes.append({"name": name, "color": rgb, "pos": vertices.ravel(),
                       "nrm": normals.ravel(), "idx": faces.ravel(),
                       "fac": [0, len(faces)-1]})
        finishes.append({"names": [name], "roughness": roughness, "metalness": metalness})
    return meshes, np.concatenate(boxes), finishes


def camera(position, corners):
    """The authored camera's orientation and projected object-box framing."""
    direction = np.asarray(position) - TARGET
    direction /= np.linalg.norm(direction)
    right = np.cross((0., 0., 1.), direction)
    right /= np.linalg.norm(right)
    up = np.cross(direction, right)
    projected = (corners - TARGET) @ np.column_stack((right, up, direction))
    lo, hi = projected.min(axis=0), projected.max(axis=0)
    target = TARGET + right * ((lo[0]+hi[0])/2) + up * ((lo[1]+hi[1])/2)
    aspect = SIZE[0] / SIZE[1]
    width = max(hi[0]-lo[0], (hi[1]-lo[1])*aspect) * FRAME_MARGIN
    return {"cam": direction.tolist(), "up": (0., 0., 1.),
            "target": target.tolist(), "span": width/(2*aspect),
            "distance": float(np.linalg.norm(np.asarray(position)-TARGET))}


def render(model, output):
    output.mkdir(parents=True, exist_ok=True)
    meshes, boxes, finishes = surfaces(model)
    with tempfile.TemporaryDirectory(prefix=".inspection-", dir=output) as temporary:
        payload = Path(temporary) / "welding-head.mesh"
        _mesh_payload.write(meshes, payload)
        jobs = [{"payload": str(payload), "out": str(output/f"{name}.png"),
                 **camera(position, boxes), "size": f"{SIZE[0]}x{SIZE[1]}",
                 "bg": BACKGROUND, "trim": False, "solid": True,
                 "ortho": True, "ground": False, "fog": False,
                 "materials": finishes}
                for name, position in VIEWS]
        return _hsm_render.render(jobs, reports=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_OUT/"xlaserlab-sup29f-xh.glb")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    render(args.model.resolve(), args.out.resolve())


if __name__ == "__main__":
    main()
