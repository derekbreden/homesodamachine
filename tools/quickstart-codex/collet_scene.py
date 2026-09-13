#!/usr/bin/env python3
"""Render the collet press holding the existing union's release sleeve in."""

from __future__ import annotations

import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys

from PIL import Image
import cadquery as cq


ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware"
OUT = HARDWARE / "quickstart-codex/out/collet"
ART = HARDWARE / "quickstart-codex/art/release-with-press.png"
RENDERER = ROOT / "tools/render/render-step-posed.js"
CAMERA = (1.1, -1.6, 0.9)
TARGET = (-83.0, 0.0, 36.5)
SPAN = 19.5
SIZE = (1840, 1040)

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


modern = load(
    HARDWARE / "quickstart/plumbing/modern/render_modern_tee.py",
    "quickstart_collet_modern",
)
press = load(
    HARDWARE / "printed-parts/collet-press/collet_press.py",
    "quickstart_collet_press",
)


def project(point):
    def unit(vector):
        length = math.sqrt(sum(value * value for value in vector))
        return tuple(value / length for value in vector)

    direction = unit(CAMERA)
    right = unit((-direction[1], direction[0], 0.0))
    up = (
        direction[1] * right[2] - direction[2] * right[1],
        direction[2] * right[0] - direction[0] * right[2],
        direction[0] * right[1] - direction[1] * right[0],
    )
    delta = tuple(a - b for a, b in zip(point, TARGET))
    scale = SIZE[1] / (2 * SPAN)
    return [
        SIZE[0] / 2 + sum(a * b for a, b in zip(delta, right)) * scale,
        SIZE[1] / 2 - sum(a * b for a, b in zip(delta, up)) * scale,
    ]


def build():
    scene = cq.Assembly(name="release-with-collet-press")
    body, sleeve = modern._canonical_union_parts(
        pressed_right=False, separate_right=True,
    )
    stroke = modern.union_ref.COLLET_TRAVEL
    sleeve = sleeve.translate((0.0, 0.0, -stroke))
    for name, shape, color in (
        ("existing-union", body, modern.C_WATER_WHITE),
        ("pressed-release-sleeve", sleeve, modern.C_TOUCHED_COLLET),
    ):
        shape = shape.rotate((0, 0, 0), (0, 1, 0), 90).translate(
            (modern.UNION_X, 0.0, modern.AXIS_Z),
        )
        modern._add(scene, shape, name, color)
    modern._add_source_line(scene)
    modern._add_original_line(scene, destination="union")

    face = modern.UNION_RIGHT_FACE - stroke
    tool = (
        press.build()
        .translate((0.0, 0.0, -press.HEAD_Z_SHIFT))
        .rotate((0, 0, 0), (0, 1, 0), press.HEAD_ANGLE)
        .rotate((0, 0, 0), (1, 0, 1), 180)
        .translate((face, 0.0, modern.AXIS_Z))
    )
    tube = modern._tube(
        (face - 2, 0.0, modern.AXIS_Z),
        (face + 90, 0.0, modern.AXIS_Z),
    )
    overlap = sum(solid.Volume() for solid in tool.intersect(tube).solids().vals())
    if overlap > 1e-6:
        raise ValueError(f"collet press crosses the tube by {overlap:.6f} mm³")
    scene.add(tool, name="collet-press", color=cq.Color(0.075, 0.08, 0.09))

    anchors = {
        "press_in": {
            "from": (face + 19, -8.0, modern.AXIS_Z - 7),
            "to": (face + 6.5, -8.0, modern.AXIS_Z - 7),
        },
        "pull_out": {
            "from": (face + 13, 0.0, modern.AXIS_Z + 7.5),
            "to": (face + 32, 0.0, modern.AXIS_Z + 7.5),
        },
        "sleeve": (face, 0.0, modern.AXIS_Z + 4.1),
        "tool_head": (face + 6, -8.0, modern.AXIS_Z - 5),
    }
    return scene, anchors


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ART.parent.mkdir(parents=True, exist_ok=True)
    scene, anchors = build()
    step = OUT / "release-with-press.step"
    modern._export_scene(scene, step)
    job = {
        "step": str(step.relative_to(HARDWARE)),
        "out": str(ART),
        "cam": CAMERA,
        "target": TARGET,
        "span": SPAN,
        "size": f"{SIZE[0]}x{SIZE[1]}",
        "up": (0, 0, 1),
        "bg": "#f2eee8",
        "trim": False,
        "solid": True,
        "ortho": True,
        "ground": False,
        "fog": False,
        "transparent": True,
    }
    subprocess.run(
        ["node", str(RENDERER), "--jobs", "-"],
        cwd=ROOT, input=json.dumps([job]), text=True, check=True,
    )
    metadata = {
        "camera": CAMERA,
        "target": TARGET,
        "span": SPAN,
        "up": (0, 0, 1),
        "size": SIZE,
        "world": anchors,
        "pixels": {
            name: {key: project(point) for key, point in value.items()}
            if isinstance(value, dict) else project(value)
            for name, value in anchors.items()
        },
    }
    (OUT / "anchors.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with Image.open(ART) as image:
        preview = Image.new("RGBA", image.size, "#f2eee8")
        preview.alpha_composite(image.convert("RGBA"))
        preview.resize((460, 260), Image.Resampling.LANCZOS).convert("RGB").save(
            OUT / "release-with-press-reduced.png",
        )
    print(json.dumps(metadata, indent=2))
    print(ART)


if __name__ == "__main__":
    main()
