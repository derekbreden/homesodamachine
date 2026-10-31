"""Pictures of payloads through `hsm render`, the engine's resident renderer.

A job is a dict of the keys `hsm render --jobs` takes (tools/hsm/render/src/job.rs): a `step`
under hardware/ and an `out`, and the camera, frame and look of the picture. What is drawn is the
step's payload, `<step>.mesh`, so a scene exported to draw is written with one
(`_cadq_export._write_mesh_payload`). A run's jobs go in one call, which keeps the renderer's
device and model warm between its pictures.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def hsm() -> str:
    """`HSM_BIN`, else `hsm` on the PATH, else `~/.local/bin/hsm`, where tools/hsm/README.md
    installs it."""
    for found in (os.environ.get("HSM_BIN"), shutil.which("hsm"), str(Path.home() / ".local/bin/hsm")):
        if found and Path(found).is_file():
            return found
    raise SystemExit("hsm is not installed: cargo install --path tools/hsm/engine --locked --root ~/.local")


def render(jobs: list[dict], root: Path = ROOT) -> None:
    """Draw every job against the checkout at `root`. A picture that fails fails the run, after
    the others are drawn."""
    subprocess.run([hsm(), "--root", str(root), "render", "--jobs", "-"],
                   input=json.dumps(jobs), text=True, check=True)
