"""Draw the reference from the same triangles supplied to the slicer."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(ROOT / "hardware/scripts"))
import _mesh_payload
from flute_payload import creased


def print_surface(stl, name, rgb):
    surface = trimesh.load_mesh(ROOT / stl, process=True)
    pos, nrm, idx, fac = creased(surface)
    return {"name": name, "color": rgb,
            "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist(),
            "idx": idx.ravel().tolist(), "fac": fac.tolist()}


def write_part_payloads(manifest):
    """Keep every individual part's viewer on its actual manufacturing mesh."""
    for row in manifest["parts"]:
        surfaces = []
        for volume in row.get("material_volumes", [row]):
            name = volume["id"]
            rgb = volume.get("color_rgb", row["color_rgb"])
            if row["id"] == "TC":
                rgb = [105/255, 180/255, 247/255] if name.endswith("body") else [235/255, 236/255, 234/255]
            surface = print_surface(volume["stl"], name, rgb)
            surfaces.append(surface)
            if volume.get("step") and volume["step"] != row["step"]:
                step = ROOT / volume["step"]
                _mesh_payload.write([surface], str(step) + ".mesh",
                                    src=_mesh_payload.source_digest(step), cut={"dev": 0, "bound": 0})
        step = ROOT / row["step"]
        _mesh_payload.write(surfaces, str(step) + ".mesh",
                            src=_mesh_payload.source_digest(step), cut={"dev": 0, "bound": 0})
        if row.get("seated_display"):
            seated = row["seated_display"]
            step = ROOT / seated["step"]
            surface = print_surface(seated["stl"], row["id"], row["color_rgb"])
            _mesh_payload.write([surface], str(step) + ".mesh",
                                src=_mesh_payload.source_digest(step), cut={"dev": 0, "bound": 0})
    print(f"Individual viewers: {len(manifest['parts'])} physical parts, supplied triangles retained")


def write_reference_payloads(manifest):
    meshes = []
    for row in manifest["printable"]:
        surface = trimesh.load_mesh(ROOT / row["stl"], process=True)
        surface.apply_transform(np.asarray(row["assembly"]["matrix_mm"]))
        pos, nrm, idx, fac = creased(surface)
        rgb = row.get("color_rgb", [.2, .2, .21])
        if row.get("material_volumes"):
            volume = next(v for v in row["material_volumes"] if v["id"] == row["name"])
            rgb = volume.get("color_rgb", rgb)
        if row["id"] == "TC":
            rgb = [105/255, 180/255, 247/255] if row["name"].endswith("body") else [235/255, 236/255, 234/255]
        meshes.append({"name": row["name"], "color": rgb,
                       "pos": pos.ravel().tolist(), "nrm": nrm.ravel().tolist(),
                       "idx": idx.ravel().tolist(), "fac": fac.tolist()})
    step = HERE / manifest["assembly"]
    _mesh_payload.write(meshes, str(step) + ".mesh",
                        src=_mesh_payload.source_digest(step),
                        cut={"dev": 0, "bound": 0})
    print(f"Viewer: {len(meshes)} components, all print triangles retained")


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    write_part_payloads(manifest)
    write_reference_payloads(manifest)
