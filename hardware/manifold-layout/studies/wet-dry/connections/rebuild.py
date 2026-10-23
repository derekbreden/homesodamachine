"""Manually rebuild nominal mesh envelopes from frozen local recipes.

This script reads only mesh-recipes.json and writes the requested output
directory. It does not import production generators, fetch sources or run CAD.
"""
from pathlib import Path
import argparse
import json
import math

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent


def tube(points, diameter, sections):
    p = np.asarray(points, float)
    tangent = np.gradient(p, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    normal = np.cross(tangent, np.array([1., 0., 0.]))
    fallback = np.linalg.norm(normal, axis=1) < .1
    normal[fallback] = np.cross(tangent[fallback], np.array([0., 1., 0.]))
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    other = np.cross(tangent, normal)
    theta = np.linspace(0, 2 * math.pi, sections, endpoint=False)
    ring = (np.cos(theta)[None, :, None] * normal[:, None, :] +
            np.sin(theta)[None, :, None] * other[:, None, :]) * diameter / 2
    vertices = (p[:, None, :] + ring).reshape(-1, 3)
    faces = []
    for j in range(len(p) - 1):
        for i in range(sections):
            a, b = j * sections + i, j * sections + (i + 1) % sections
            faces.extend([[a, b, b + sections], [a, b + sections, a + sections]])
    for j, reverse in [(0, True), (len(p) - 1, False)]:
        for i in range(1, sections - 1):
            triangle = [j * sections, j * sections + i, j * sections + i + 1]
            faces.append(triangle[::-1] if reverse else triangle)
    return vertices, np.asarray(faces, np.int32)


def geometry(recipe, sections):
    if recipe["kind"] == "box":
        mesh = trimesh.creation.box(extents=recipe["dimensions_mm"])
        return (mesh.vertices @ np.array(recipe["rotation"]).T + recipe["centre_mm"],
                mesh.faces)
    parts = [tube(points, recipe["diameter_mm"], sections) for points in recipe["paths_mm"]]
    vertices, faces, offset = [], [], 0
    for v, f in parts:
        vertices.append(v); faces.append(f + offset); offset += len(v)
    return np.vstack(vertices), np.vstack(faces)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "geometry")
    args = parser.parse_args()
    recipes = json.loads((HERE / "mesh-recipes.json").read_text())
    args.out.mkdir(parents=True, exist_ok=True)
    for name, recipe in recipes["geometry"].items():
        v, f = geometry(recipe, recipes["circle_sections"])
        np.savez_compressed(args.out / (name + ".npz"), v=v.astype(np.float32), f=f.astype(np.int32))
    print(f"Rebuilt {len(recipes['geometry'])} source-frame meshes in {args.out}")


if __name__ == "__main__":
    main()
