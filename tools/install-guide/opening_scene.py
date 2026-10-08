#!/usr/bin/env python3
"""Render the current counter opening and its registered component silhouette."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import binary_fill_holes

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware"
OUT = HARDWARE / "install-guide/out/opening"
ASSETS = HARDWARE / "install-guide/assets"
sys.path[:0] = [str(HARDWARE / "install-guide"), str(HARDWARE / "scripts")]


def outlines(mask):
    """Closed cell-edge contours; only the exterior silhouette is illustrated."""
    mask = binary_fill_holes(mask)
    padded = np.pad(mask, 1)
    edges = {}
    neighbours = (padded[:-2, 1:-1], padded[1:-1, 2:],
                  padded[2:, 1:-1], padded[1:-1, :-2])
    for side, neighbour in enumerate(neighbours):
        ys, xs = np.nonzero(mask & ~neighbour)
        for x, y in zip(xs.tolist(), ys.tolist()):
            a, b = (((x, y), (x + 1, y)),
                    ((x + 1, y), (x + 1, y + 1)),
                    ((x + 1, y + 1), (x, y + 1)),
                    ((x, y + 1), (x, y)))[side]
            edges.setdefault(a, []).append(b)
    loops = []
    while edges:
        start = next(iter(edges))
        point = start
        loop = [point]
        while True:
            options = edges[point]
            following = options.pop()
            if not options:
                del edges[point]
            loop.append(following)
            point = following
            if point == start:
                break
        # Axis-aligned collinear steps add no information to the vector outline.
        keep = [loop[0]]
        for i in range(1, len(loop) - 1):
            before, here, after = loop[i - 1:i + 2]
            if ((here[0] - before[0]) * (after[1] - here[1])
                    != (here[1] - before[1]) * (after[0] - here[0])):
                keep.append(here)
        if len(keep) >= 3:
            loops.append(keep)
    return loops


def main():
    import cadquery as cq
    import _cad_art
    import _install_art

    OUT.mkdir(parents=True, exist_ok=True)
    scene = _install_art.s_opening()
    component = cq.Assembly(name="opening-components")
    for child in scene.children:
        if child.name != "countertop":
            component.add(child)
    paths = {"scene": OUT / "opening.step", "components": OUT / "components.step"}
    for name, shape in (("scene", scene), ("components", component)):
        _cad_art._export_colored(shape, paths[name], mesh=True)
    pose = dict(cam=(0.42, -0.80, 0.95), target=(0.0, 0.0, 24.0),
                span=120.0, size="3800x3200", up=(0, 0, 1),
                bg="#f2eee8", transparent=True, solid=True, ortho=True,
                trim=False, ground=False, fog=False)
    jobs = [{**pose, "step": str(path.relative_to(HARDWARE)),
             "out": str(OUT / f"{name}.png"), "zoom": 10.0}
            for name, path in paths.items()]
    manifest = OUT / "jobs.json"
    manifest.write_text(json.dumps(jobs, indent=2) + "\n")
    subprocess.run(["node", str(_cad_art.RENDERER), "--jobs", str(manifest)], cwd=ROOT, check=True)
    image = Image.open(OUT / "scene.png").convert("RGBA")
    crop = image.getchannel("A").point(lambda a: 255 if a >= 12 else 0).getbbox()
    assert crop is not None
    image = image.crop(crop)
    target = ASSETS / "opening.png"
    image.save(target)
    alpha = np.asarray(Image.open(OUT / "components.png").convert("RGBA").crop(crop))[:, :, 3]
    loops = outlines(alpha >= 128)
    assert loops
    width, height = image.size
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" data-source-sha256="{digest}">',
             '<title>Current faucet shank, four tubes and display cable</title>']
    for loop in loops:
        data = "M" + " L".join(f"{x} {y}" for x, y in loop) + " Z"
        lines.append(f'<path fill="none" stroke="#46515b" stroke-width="8.72" d="{data}"/>')
    lines.append("</svg>")
    (ASSETS / "opening-faucet-outline.svg").write_text("\n".join(lines) + "\n")
    (OUT / "registration.json").write_text(json.dumps({
        "render_sha256": digest, "render_size": [width, height], "native_crop": crop,
        "scene_step_sha256": hashlib.sha256(paths["scene"].read_bytes()).hexdigest(),
        "component_step_sha256": hashlib.sha256(paths["components"].read_bytes()).hexdigest(),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (Path(__file__), HARDWARE / "install-guide/_install_art.py",
                                     HARDWARE / "faucet-layout/faucet_assembly.py")},
        "silhouette_scope": "Same orthographic pose and native viewport; outer component-alpha contours.",
    }, indent=2) + "\n")
    resolution_path = ASSETS / "print-resolution.json"
    resolution = json.loads(resolution_path.read_text())
    resolution["assets"]["opening.png"] = {
        "reference_size": [width, height], "render_size": [width, height],
        "scale": [1.0, 1.0], "render_sha256": digest,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scene_step_sha256": hashlib.sha256(paths["scene"].read_bytes()).hexdigest(),
        "fixed_native_crop": crop,
        "silhouette": "opening-faucet-outline.svg",
    }
    resolution_path.write_text(json.dumps(resolution, indent=2) + "\n")
    print("Current opening artwork and component outline registered", flush=True)


if __name__ == "__main__":
    main()
